"""Primary path cleaning and simple directed-edge metrics.

Rule used here:

* ``None`` and integer ``0`` are invalid samples. They end the current segment;
  the next valid node starts a new segment.
* Consecutive repeats stay in ``raw_valid_segments`` and are collapsed only in
  ``route_shape_segments``.
* A transition without an explicit directed graph edge ends the current segment;
  no shortest-path interpolation and no bridge edge are added.
* Longest shared directed segments are searched only within pairs of cleaned
  route-shape segments. Endpoint labels are relative to the complete cleaned
  trial: ``initial`` means the run starts at the first available edge in both
  trials; ``terminal`` means it ends at the last available edge in both trials;
  ``middle`` means it touches no trial endpoint; everything else is ``mixed``.
  If a leading/trailing invalid gap or earlier/later split prevents knowing the
  relevant trial endpoint, the result is ``unavailable`` with a reason.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass

from .contracts import (
    CleanedPath,
    MazeGraph,
    Node,
    PathAudit,
    _canonical_json,
    _node_token,
)

Edge = tuple[Node, Node]


@dataclass(frozen=True)
class EdgeRunLocation:
    segment_index: int
    start_edge_index: int
    length: int

    @property
    def end_edge_index(self) -> int:
        return self.start_edge_index + self.length - 1


@dataclass(frozen=True)
class SharedDirectedSegment:
    length: int
    edges: tuple[Edge, ...]
    classification: str
    left: EdgeRunLocation | None = None
    right: EdgeRunLocation | None = None
    unavailable_reason: str | None = None


def is_invalid_node(node: Node) -> bool:
    """Return true for the pilot's invalid path sentinels."""

    return node is None or node == 0


def clean_path(nodes: Sequence[Node], graph: MazeGraph) -> CleanedPath:
    """Clean raw observed nodes into non-bridged valid segments."""

    raw_nodes = tuple(nodes)
    raw_segments: list[tuple[Node, ...]] = []
    current: list[Node] = []
    invalid_sample_count = 0
    valid_sample_count = 0
    invalid_gap_count = 0
    nonadjacent_transition_count = 0
    in_invalid_gap = False

    def flush() -> None:
        nonlocal current
        if current:
            raw_segments.append(tuple(current))
            current = []

    for node in raw_nodes:
        if is_invalid_node(node):
            invalid_sample_count += 1
            flush()
            if not in_invalid_gap:
                invalid_gap_count += 1
                in_invalid_gap = True
            continue

        valid_sample_count += 1
        in_invalid_gap = False
        if not current:
            current.append(node)
            continue

        previous = current[-1]
        if node == previous or graph.has_edge(previous, node):
            current.append(node)
            continue

        nonadjacent_transition_count += 1
        flush()
        current.append(node)

    flush()

    shape_segments = tuple(_collapse_repeats(segment) for segment in raw_segments)
    repeated_sample_count = sum(
        len(raw_segment) - len(shape_segment)
        for raw_segment, shape_segment in zip(raw_segments, shape_segments, strict=True)
    )

    audit = PathAudit(
        raw_sample_count=len(raw_nodes),
        invalid_sample_count=invalid_sample_count,
        valid_sample_count=valid_sample_count,
        invalid_gap_count=invalid_gap_count,
        nonadjacent_transition_count=nonadjacent_transition_count,
        raw_valid_segment_count=len(raw_segments),
        route_shape_segment_count=len(shape_segments),
        repeated_sample_count=repeated_sample_count,
        leading_invalid_sample_count=_leading_invalid_count(raw_nodes),
        trailing_invalid_sample_count=_trailing_invalid_count(raw_nodes),
    )
    return CleanedPath(
        raw_valid_segments=tuple(raw_segments),
        route_shape_segments=shape_segments,
        audit=audit,
    )


def _collapse_repeats(segment: Sequence[Node]) -> tuple[Node, ...]:
    collapsed: list[Node] = []
    for node in segment:
        if not collapsed or node != collapsed[-1]:
            collapsed.append(node)
    return tuple(collapsed)


def _leading_invalid_count(nodes: Sequence[Node]) -> int:
    count = 0
    for node in nodes:
        if not is_invalid_node(node):
            break
        count += 1
    return count


def _trailing_invalid_count(nodes: Sequence[Node]) -> int:
    count = 0
    for node in reversed(nodes):
        if not is_invalid_node(node):
            break
        count += 1
    return count


def directed_edge_sequences(path: CleanedPath) -> tuple[tuple[Edge, ...], ...]:
    """Return directed edges per cleaned route-shape segment, with no bridges."""

    return tuple(
        tuple(zip(segment, segment[1:], strict=False))
        for segment in path.route_shape_segments
    )


def directed_edge_set(path: CleanedPath) -> frozenset[Edge]:
    """Return the union of directed edges across segments, without gap bridges."""

    return frozenset(
        edge for sequence in directed_edge_sequences(path) for edge in sequence
    )


def edge_jaccard(left: CleanedPath, right: CleanedPath) -> float | None:
    """Return directed-edge Jaccard distance, or ``None`` for two empty sets."""

    left_edges = directed_edge_set(left)
    right_edges = directed_edge_set(right)
    union = left_edges | right_edges
    if not union:
        return None
    return 1.0 - (len(left_edges & right_edges) / len(union))


def longest_shared_contiguous_directed_segment(
    left: CleanedPath,
    right: CleanedPath,
) -> SharedDirectedSegment:
    """Find the longest shared contiguous directed-edge run.

    Runs never cross cleaned segment boundaries. Ties use canonical edge content,
    then segment/start indices, so results are deterministic.
    """

    left_sequences = directed_edge_sequences(left)
    right_sequences = directed_edge_sequences(right)
    best_edges: tuple[Edge, ...] = ()
    best_left: EdgeRunLocation | None = None
    best_right: EdgeRunLocation | None = None
    best_tie_key: tuple[str, int, int, int, int] | None = None

    for left_segment_index, left_sequence in enumerate(left_sequences):
        for right_segment_index, right_sequence in enumerate(right_sequences):
            for left_start in range(len(left_sequence)):
                for right_start in range(len(right_sequence)):
                    length = _common_prefix_length(
                        left_sequence[left_start:],
                        right_sequence[right_start:],
                    )
                    if length == 0:
                        continue
                    edges = left_sequence[left_start : left_start + length]
                    tie_key = (
                        _edge_sequence_key(edges),
                        left_segment_index,
                        left_start,
                        right_segment_index,
                        right_start,
                    )
                    if len(edges) > len(best_edges) or (
                        len(edges) == len(best_edges)
                        and (best_tie_key is None or tie_key < best_tie_key)
                    ):
                        best_edges = edges
                        best_left = EdgeRunLocation(
                            left_segment_index, left_start, length
                        )
                        best_right = EdgeRunLocation(
                            right_segment_index, right_start, length
                        )
                        best_tie_key = tie_key

    if not best_edges or best_left is None or best_right is None:
        return SharedDirectedSegment(length=0, edges=(), classification="none")

    classification, reason = _classify_shared_segment(
        left, right, best_left, best_right
    )
    return SharedDirectedSegment(
        length=len(best_edges),
        edges=best_edges,
        classification=classification,
        left=best_left,
        right=best_right,
        unavailable_reason=reason,
    )


def _common_prefix_length(left: Sequence[Edge], right: Sequence[Edge]) -> int:
    length = 0
    for left_edge, right_edge in zip(left, right, strict=False):
        if left_edge != right_edge:
            break
        length += 1
    return length


def _edge_sequence_key(edges: Iterable[Edge]) -> str:
    return _canonical_json(
        [[_node_token(start), _node_token(end)] for start, end in edges]
    )


def _first_last_edge_locations(
    path: CleanedPath,
) -> tuple[tuple[int, int] | None, tuple[int, int] | None]:
    sequences = directed_edge_sequences(path)
    first: tuple[int, int] | None = None
    last: tuple[int, int] | None = None
    for segment_index, sequence in enumerate(sequences):
        if sequence and first is None:
            first = (segment_index, 0)
        if sequence:
            last = (segment_index, len(sequence) - 1)
    return first, last


def _endpoint_availability(path: CleanedPath) -> tuple[bool, bool]:
    first, last = _first_last_edge_locations(path)
    first_available = (
        first is not None
        and first[0] == 0
        and path.audit.leading_invalid_sample_count == 0
    )
    last_available = (
        last is not None
        and last[0] == len(path.route_shape_segments) - 1
        and path.audit.trailing_invalid_sample_count == 0
    )
    return first_available, last_available


def _classify_shared_segment(
    left: CleanedPath,
    right: CleanedPath,
    left_location: EdgeRunLocation,
    right_location: EdgeRunLocation,
) -> tuple[str, str | None]:
    left_first, left_last = _first_last_edge_locations(left)
    right_first, right_last = _first_last_edge_locations(right)
    left_first_available, left_last_available = _endpoint_availability(left)
    right_first_available, right_last_available = _endpoint_availability(right)

    left_starts = (
        left_location.segment_index,
        left_location.start_edge_index,
    ) == left_first
    right_starts = (
        right_location.segment_index,
        right_location.start_edge_index,
    ) == right_first
    left_ends = (left_location.segment_index, left_location.end_edge_index) == left_last
    right_ends = (
        right_location.segment_index,
        right_location.end_edge_index,
    ) == right_last

    unavailable_reasons: list[str] = []
    if left_starts and not left_first_available:
        unavailable_reasons.append("left initial endpoint obscured")
    if right_starts and not right_first_available:
        unavailable_reasons.append("right initial endpoint obscured")
    if left_ends and not left_last_available:
        unavailable_reasons.append("left terminal endpoint obscured")
    if right_ends and not right_last_available:
        unavailable_reasons.append("right terminal endpoint obscured")
    if unavailable_reasons:
        return "unavailable", "; ".join(unavailable_reasons)

    touches_start = left_starts or right_starts
    touches_end = left_ends or right_ends
    if left_starts and right_starts and left_ends and right_ends:
        return "complete", None
    if not touches_start and not touches_end:
        return "middle", None
    if left_starts and right_starts and not touches_end:
        return "initial", None
    if left_ends and right_ends and not touches_start:
        return "terminal", None
    return "mixed", None
