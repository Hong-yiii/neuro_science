"""Small immutable contracts for the first CEBRA pilot framework.

These objects are intentionally plain dataclasses. They validate only the fields
needed by the approved software framework and do not infer missing scientific
metadata from current one-cell navigation exports.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Hashable, Sequence
from dataclasses import dataclass, field
from numbers import Integral
from typing import Any

import numpy as np

Node = Hashable


def _require_text(value: str, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return value


def _readonly_array(array: np.ndarray) -> np.ndarray:
    out = np.array(array, copy=True)
    out.setflags(write=False)
    return out


def _node_token(node: Node) -> dict[str, Any]:
    if node is None or node == 0:
        raise ValueError("None and 0 are invalid path nodes, not graph nodes")
    if isinstance(node, bool):
        raise TypeError("boolean node IDs are too ambiguous for canonical hashing")
    if isinstance(node, str):
        if not node:
            raise ValueError("string node IDs must be non-empty")
        return {"type": "str", "value": node}
    if isinstance(node, Integral):
        try:
            value = int(node)
        except (TypeError, ValueError, OverflowError) as exc:
            raise TypeError(f"invalid integer node ID: {node!r}") from exc
        return {"type": "int", "value": value}
    raise TypeError(f"unsupported node ID type for canonical hashing: {type(node)!r}")


def _canonical_json(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


@dataclass(frozen=True)
class CueNavigationTrial:
    """One source trial that can support the pilot's scientific data gate.

    The count array shape is fixed as ``(cue_bin, unit)``. There is no transpose
    fallback. At least two simultaneous units are required so the present
    one-cell navigation-period export cannot be treated as this population
    contract by reshaping a vector.
    """

    source_trial_id: str
    session_id: str
    simultaneous_recording_group: str
    previous_trial_id: str | None
    trial_index: int
    previous_goal_id: str | None
    previous_success: bool | None
    previous_metadata_missing_reason: str | None
    current_success: bool
    timeout: bool
    inclusion_reason: str
    cue_id: str
    start_id: str
    goal_id: str
    cue_onset: float
    cue_offset: float
    navigation_onset: float
    navigation_end: float
    unit_ids: Sequence[str]
    cue_counts_by_bin_unit: np.ndarray
    cue_valid_mask: np.ndarray
    cue_exposure_seconds: np.ndarray
    observed_path_nodes: Sequence[Node]

    def __post_init__(self) -> None:
        for name in (
            "source_trial_id",
            "session_id",
            "simultaneous_recording_group",
            "inclusion_reason",
            "cue_id",
            "start_id",
            "goal_id",
        ):
            object.__setattr__(self, name, _require_text(getattr(self, name), name))

        if isinstance(self.trial_index, bool) or not isinstance(
            self.trial_index, Integral
        ):
            raise ValueError("trial_index must be a nonnegative integer")
        try:
            trial_index = int(self.trial_index)
        except (TypeError, ValueError, OverflowError) as exc:
            raise ValueError("trial_index must be a nonnegative integer") from exc
        if trial_index < 0:
            raise ValueError("trial_index must be a nonnegative integer")

        previous_fields = (
            self.previous_trial_id,
            self.previous_goal_id,
            self.previous_success,
        )
        if any(value is None for value in previous_fields) and not all(
            value is None for value in previous_fields
        ):
            raise ValueError(
                "previous_trial_id, previous_goal_id, and previous_success must be all present or all absent"
            )
        previous_metadata_absent = all(value is None for value in previous_fields)
        if previous_metadata_absent:
            if self.previous_metadata_missing_reason is None:
                raise ValueError(
                    "previous_metadata_missing_reason is required when previous-trial metadata is absent"
                )
            object.__setattr__(
                self,
                "previous_metadata_missing_reason",
                _require_text(
                    self.previous_metadata_missing_reason,
                    "previous_metadata_missing_reason",
                ),
            )
        elif self.previous_metadata_missing_reason is not None:
            raise ValueError(
                "previous_metadata_missing_reason must be absent when previous-trial metadata is present"
            )

        if self.previous_trial_id is not None:
            if self.previous_goal_id is None:
                raise ValueError("previous_goal_id is required with previous_trial_id")
            object.__setattr__(
                self,
                "previous_trial_id",
                _require_text(self.previous_trial_id, "previous_trial_id"),
            )
            object.__setattr__(
                self,
                "previous_goal_id",
                _require_text(self.previous_goal_id, "previous_goal_id"),
            )
        if self.previous_success is not None and not isinstance(
            self.previous_success, (bool, np.bool_)
        ):
            raise ValueError(
                "previous_success must be boolean when previous-trial metadata exists"
            )
        if not isinstance(self.current_success, (bool, np.bool_)) or not isinstance(
            self.timeout, (bool, np.bool_)
        ):
            raise ValueError("current_success and timeout must be boolean")
        if bool(self.current_success) == bool(self.timeout):
            raise ValueError("exactly one of current_success and timeout must be true")

        object.__setattr__(self, "trial_index", trial_index)
        object.__setattr__(
            self,
            "previous_success",
            None if self.previous_success is None else bool(self.previous_success),
        )
        object.__setattr__(self, "current_success", bool(self.current_success))
        object.__setattr__(self, "timeout", bool(self.timeout))

        times = np.array(
            [
                self.cue_onset,
                self.cue_offset,
                self.navigation_onset,
                self.navigation_end,
            ],
            dtype=float,
        )
        if not np.all(np.isfinite(times)):
            raise ValueError("cue/navigation timing must be finite")
        if not (
            self.cue_onset
            < self.cue_offset
            <= self.navigation_onset
            < self.navigation_end
        ):
            raise ValueError(
                "expected cue_onset < cue_offset <= navigation_onset < navigation_end"
            )

        units = tuple(_require_text(unit, "unit_id") for unit in self.unit_ids)
        if len(units) < 2:
            raise ValueError(
                "scientific pilot contract requires at least two simultaneous units"
            )
        if len(set(units)) != len(units):
            raise ValueError("unit_ids must be unique and preserve column order")

        counts = _readonly_array(np.asarray(self.cue_counts_by_bin_unit))
        if counts.ndim != 2:
            raise ValueError("cue_counts_by_bin_unit must have shape (cue_bin, unit)")
        if counts.shape[1] != len(units):
            raise ValueError(
                "unit_ids length must match the unit axis of cue_counts_by_bin_unit"
            )
        if not np.issubdtype(counts.dtype, np.integer):
            raise ValueError("cue spike counts must use an integer dtype")
        if np.any(counts < 0):
            raise ValueError("cue spike counts must be nonnegative")

        mask = _readonly_array(np.asarray(self.cue_valid_mask))
        if mask.dtype != np.bool_ or mask.ndim != 1 or mask.shape[0] != counts.shape[0]:
            raise ValueError("cue_valid_mask must be a bool vector aligned to cue bins")

        exposure = _readonly_array(np.asarray(self.cue_exposure_seconds, dtype=float))
        if exposure.ndim != 1 or exposure.shape[0] != counts.shape[0]:
            raise ValueError(
                "cue_exposure_seconds must be a vector aligned to cue bins"
            )
        valid_exposure = exposure[mask]
        try:
            total_exposure = float(np.sum(valid_exposure))
        except (TypeError, ValueError, OverflowError) as exc:
            raise ValueError("cue exposure could not be summarized") from exc
        if valid_exposure.size == 0 or total_exposure <= 0.0:
            raise ValueError(
                "at least one valid cue bin with nonzero exposure is required"
            )
        if not np.all(np.isfinite(valid_exposure)) or np.any(valid_exposure <= 0.0):
            raise ValueError("valid cue bins require positive finite exposure")

        path = tuple(self.observed_path_nodes)
        if not path:
            raise ValueError(
                "observed_path_nodes must be present; clean invalid nodes separately"
            )

        object.__setattr__(self, "unit_ids", units)
        object.__setattr__(self, "cue_counts_by_bin_unit", counts)
        object.__setattr__(self, "cue_valid_mask", mask)
        object.__setattr__(self, "cue_exposure_seconds", exposure)
        object.__setattr__(self, "observed_path_nodes", path)


@dataclass(frozen=True)
class MazeGraph:
    """Explicit directed maze graph with a stable content hash."""

    directed_edges: Sequence[tuple[Node, Node]]
    nodes: tuple[Node, ...] = field(init=False)
    _edge_set: frozenset[tuple[Node, Node]] = field(
        init=False, repr=False, compare=False
    )

    def __post_init__(self) -> None:
        edges_list: list[tuple[Node, Node]] = []
        seen: set[tuple[Node, Node]] = set()
        for raw_edge in self.directed_edges:
            if len(raw_edge) != 2:
                raise ValueError("each directed edge must be a pair")
            edge = (raw_edge[0], raw_edge[1])
            _node_token(edge[0])
            _node_token(edge[1])
            if edge in seen:
                raise ValueError(f"duplicate directed edge: {edge!r}")
            seen.add(edge)
            edges_list.append(edge)

        def sort_key(edge: tuple[Node, Node]) -> str:
            return _canonical_json([_node_token(edge[0]), _node_token(edge[1])])

        canonical = tuple(sorted(edges_list, key=sort_key))
        object.__setattr__(self, "directed_edges", canonical)
        object.__setattr__(self, "_edge_set", frozenset(canonical))

        nodes = sorted(
            {node for edge in canonical for node in edge},
            key=lambda n: _canonical_json(_node_token(n)),
        )
        object.__setattr__(self, "nodes", tuple(nodes))

    @property
    def canonical_json(self) -> str:
        payload = {
            "directed_edges": [
                [_node_token(start), _node_token(end)]
                for start, end in self.directed_edges
            ]
        }
        return _canonical_json(payload)

    @property
    def sha256(self) -> str:
        return hashlib.sha256(self.canonical_json.encode("utf-8")).hexdigest()

    def has_edge(self, start: Node, end: Node) -> bool:
        return (start, end) in self._edge_set


@dataclass(frozen=True)
class PathAudit:
    """Counts produced by primary path cleaning."""

    raw_sample_count: int
    invalid_sample_count: int
    valid_sample_count: int
    invalid_gap_count: int
    nonadjacent_transition_count: int
    raw_valid_segment_count: int
    route_shape_segment_count: int
    repeated_sample_count: int
    leading_invalid_sample_count: int
    trailing_invalid_sample_count: int


@dataclass(frozen=True)
class CleanedPath:
    """A cleaned observed path without stitched gaps.

    ``raw_valid_segments`` keeps valid samples and dwell repeats. ``route_shape_segments``
    collapses only consecutive repeats for edge and shape metrics.
    """

    raw_valid_segments: tuple[tuple[Node, ...], ...]
    route_shape_segments: tuple[tuple[Node, ...], ...]
    audit: PathAudit
