#!/usr/bin/env python3
"""Behavior-only graph-path audit plus condition-matched pseudopop baseline.

This is not H1 evidence. Route labels are behavior-derived from behavior, and
V5 assembles cross-session pseudopopulation rows matched by
(start, goal, route_family) instead of imputing one real trial across all 195
selected cells.
"""

from __future__ import annotations

import argparse
import ast
import csv
import gzip
import hashlib
import json
import math
from collections import Counter, defaultdict
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, TextIO, cast

import matplotlib.pyplot as plt
import numpy as np

from docs.cebra_pilot.implementation.contracts import CleanedPath, MazeGraph
from docs.cebra_pilot.implementation.paths import (
    clean_path,
    directed_edge_sequences,
    longest_shared_contiguous_directed_segment,
)
from scripts.import_place195_sessions import (
    DEFAULT_OUTPUT_PARENT,
    ROOT,
    git_state,
    package_versions,
    sha256_file,
    validate_output_dir,
)
from scripts.place195_split_and_behavior_audit import (
    read_csv,
    read_json,
    write_csv,
    write_json,
)

DEFAULT_IMPORT_DIR = DEFAULT_OUTPUT_PARENT / "place195-all-sessions-20260830-v4"
DEFAULT_SPLIT_DIR = DEFAULT_OUTPUT_PARENT / "place195-splits-20260830-v3"
DEFAULT_GEOMETRY = ROOT / "docs/geometry/maze_mesh_centroids_1344.txt"
DEFAULT_OUTPUT_DIR = DEFAULT_OUTPUT_PARENT / "place195-graph-path-baseline-20260901-v5"
DEFAULT_RECEIPT = (
    ROOT / "notes/data_inspection/place195_graph_path_baseline_v5_20260901.md"
)

GEOMETRY_SHA256 = "479f0df501e92e167206248eff2d0a44ba5f26cd62cfcc879dcaad979d7a7e66"
PINNED_PRIMARY_GRAPH_HASH = (
    "1e7804c5d2167dcd8709a9760d8917034cb60e36e936229fad9056b1dae0f9ad"
)
SCRIPT_PRIMARY_GRAPH_HASH = (
    "f83908e027012e49f1be2396bb0f7aeb514b807c43b6e703625a40647a3738a0"
)
GRAPH_SCHEMA = "maze_graph_1344_4neighbor_v1"
GRID_STEP = 0.625
MAPPING_TOLERANCE = math.sqrt(2) * GRID_STEP / 2
ROUTE_OTHER = "__other_within_start_goal__"
SCIENTIFIC_STATUS = (
    "exploratory_graph_path_condition_matched_pseudopop_baseline_not_h1_evidence"
)


@dataclass(frozen=True)
class GraphSpec:
    centroids: dict[int, tuple[float, float]]
    coord_to_node: dict[tuple[float, float], int]
    graph: MazeGraph
    directed_edges: tuple[tuple[int, int], ...]
    undirected_edge_count: int
    connected_components: int
    geometry_sha256: str
    primary_graph_hash: str


@dataclass(frozen=True)
class TrialLabel:
    session_id: str
    source_trial_id: str
    split: str
    trial_index: str
    start: str
    goal: str


@dataclass(frozen=True)
class Pseudopopulation:
    rows: list[dict[str, Any]]
    components: list[dict[str, Any]]
    x: np.ndarray
    observed: np.ndarray


def open_text(path: Path, mode: str = "rt") -> TextIO:
    try:
        if path.suffix == ".gz":
            return cast(TextIO, gzip.open(path, mode, encoding="utf-8", newline=""))
        return cast(TextIO, open(path, mode, encoding="utf-8", newline=""))
    except OSError as exc:
        raise OSError(f"failed to open {path}") from exc


def csv_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (list, tuple, dict)):
        return json.dumps(value, sort_keys=True, separators=(",", ":"))
    return str(value)


def signature_sha256(signature: str) -> str:
    return hashlib.sha256(signature.encode("utf-8")).hexdigest()


def parse_float(value: Any, label: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(f"invalid float for {label}: {value!r}") from exc


def parse_int(value: Any, label: str) -> int:
    try:
        return int(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(f"invalid integer for {label}: {value!r}") from exc


def mean_or_none(values: Sequence[float]) -> float | None:
    return sum(values) / len(values) if values else None


def format_coord(value: float) -> str:
    text = f"{value:.4f}".rstrip("0").rstrip(".")
    return "0" if text == "-0" else text


def parse_centroids(
    path: Path,
) -> tuple[dict[int, tuple[float, float]], dict[tuple[float, float], int]]:
    centroids: dict[int, tuple[float, float]] = {}
    coord_to_node: dict[tuple[float, float], int] = {}
    with open_text(path) as handle:
        for line_number, line in enumerate(handle, 1):
            text = line.strip()
            if not text:
                continue
            try:
                x, y = ast.literal_eval(text)
            except (SyntaxError, ValueError, TypeError) as exc:
                raise ValueError(
                    f"invalid centroid line {line_number}: {text!r}"
                ) from exc
            coord = (
                round(parse_float(x, f"centroid {line_number} axis1"), 4),
                round(parse_float(y, f"centroid {line_number} axis2"), 4),
            )
            centroids[line_number] = coord
            if coord in coord_to_node:
                raise ValueError(f"duplicate centroid coordinate: {coord}")
            coord_to_node[coord] = line_number
    return centroids, coord_to_node


def primary_graph_hash(
    geometry: Path,
    geometry_sha: str,
    centroids: Mapping[int, tuple[float, float]],
    directed_edges: Sequence[tuple[int, int]],
) -> str:
    try:
        geometry_file = str(geometry.resolve().relative_to(ROOT))
    except ValueError:
        geometry_file = str(geometry)
    payload = {
        "schema": GRAPH_SCHEMA,
        "geometry_file": geometry_file,
        "geometry_sha256": geometry_sha,
        "node_id": "1-based line number in centroid file",
        "coordinate_units": "Unity axis units",
        "adjacency_rule": "directed cardinal 4-neighbor edge when centroids differ by exactly 0.625 on one axis and 0 on the other",
        "grid_step": format_coord(GRID_STEP),
        "nodes": [
            {"id": node_id, "axis1": format_coord(x), "axis2": format_coord(y)}
            for node_id, (x, y) in sorted(centroids.items())
        ],
        "directed_edges": [[left, right] for left, right in sorted(directed_edges)],
    }
    return signature_sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")))


def build_graph(geometry: Path) -> GraphSpec:
    geometry_sha = sha256_file(geometry)
    if geometry_sha != GEOMETRY_SHA256:
        raise ValueError(f"geometry hash mismatch: {geometry_sha}")
    centroids, coord_to_node = parse_centroids(geometry)
    directed_edges: list[tuple[int, int]] = []
    for node_id, (x, y) in centroids.items():
        for dx, dy in (
            (GRID_STEP, 0.0),
            (-GRID_STEP, 0.0),
            (0.0, GRID_STEP),
            (0.0, -GRID_STEP),
        ):
            neighbor = coord_to_node.get((round(x + dx, 4), round(y + dy, 4)))
            if neighbor is not None:
                directed_edges.append((node_id, neighbor))
    graph = MazeGraph(tuple(directed_edges))
    undirected: set[tuple[int, int]] = {
        (min(left, right), max(left, right)) for left, right in directed_edges
    }
    components = connected_component_count(set(centroids), undirected)
    computed_primary_hash = primary_graph_hash(
        geometry, geometry_sha, centroids, directed_edges
    )
    if computed_primary_hash != SCRIPT_PRIMARY_GRAPH_HASH:
        raise ValueError(f"script primary graph hash mismatch: {computed_primary_hash}")
    if (len(centroids), len(undirected), len(directed_edges), components) != (
        1344,
        2544,
        5088,
        1,
    ):
        raise ValueError(
            "graph facts mismatch: "
            f"nodes={len(centroids)} undirected={len(undirected)} "
            f"directed={len(directed_edges)} components={components}"
        )
    return GraphSpec(
        centroids=centroids,
        coord_to_node=coord_to_node,
        graph=graph,
        directed_edges=tuple(directed_edges),
        undirected_edge_count=len(undirected),
        connected_components=components,
        geometry_sha256=geometry_sha,
        primary_graph_hash=computed_primary_hash,
    )


def connected_component_count(
    nodes: set[int], undirected_edges: set[tuple[int, int]]
) -> int:
    neighbors: dict[int, list[int]] = {node: [] for node in nodes}
    for left, right in undirected_edges:
        neighbors[left].append(right)
        neighbors[right].append(left)
    seen: set[int] = set()
    components = 0
    for node in nodes:
        if node in seen:
            continue
        components += 1
        stack = [node]
        seen.add(node)
        while stack:
            current = stack.pop()
            for neighbor in neighbors[current]:
                if neighbor not in seen:
                    seen.add(neighbor)
                    stack.append(neighbor)
    return components


def map_position_to_node(x: float, y: float, graph_spec: GraphSpec) -> int:
    grid_x = round(round((x + 12.1875) / GRID_STEP) * GRID_STEP - 12.1875, 4)
    grid_y = round(round((y + 12.1875) / GRID_STEP) * GRID_STEP - 12.1875, 4)
    node = graph_spec.coord_to_node.get((grid_x, grid_y))
    if node is None:
        return 0
    distance = math.hypot(x - grid_x, y - grid_y)
    return node if distance <= MAPPING_TOLERANCE + 1e-9 else 0


def load_trial_labels(import_dir: Path, split_dir: Path) -> dict[str, TrialLabel]:
    split_rows = read_csv(split_dir / "source_trial_splits.csv")
    split_by_source = {row["source_trial_id"]: row for row in split_rows}
    trial_rows = read_csv(import_dir / "trials.csv")
    trial_by_source = {row["source_trial_id"]: row for row in trial_rows}
    labels: dict[str, TrialLabel] = {}
    for row in trial_rows:
        source = row["source_trial_id"]
        split = split_by_source[source]["split"]
        if split not in {"train", "validation"} or row["outcome"] != "success":
            continue
        previous = row.get("previous_source_trial_id", "")
        previous_row = trial_by_source.get(previous)
        previous_split = split_by_source.get(previous, {}).get("split", "")
        if previous_split not in {"train", "validation"}:
            continue
        if not previous_row or previous_row.get("outcome") != "success":
            continue
        start = row.get("inferred_start_id_from_previous_marker", "").replace(
            "marker_", ""
        )
        goal = row.get("marker_minor_digit", "")
        if not start or not goal:
            continue
        labels[source] = TrialLabel(
            session_id=row["session_id"],
            source_trial_id=source,
            split=split,
            trial_index=row["trial_index"],
            start=start,
            goal=goal,
        )
    return labels


def signature_from_segments(segments: Sequence[Sequence[Any]]) -> str:
    return "|".join("-".join(str(node) for node in segment) for segment in segments)


def coarse5_index(value: float) -> int:
    return min(4, max(0, parse_int((value + 12.5) // 5.0, "coarse5 index"))) + 1


def coarse5_for_node(node: int, graph_spec: GraphSpec) -> str:
    x, y = graph_spec.centroids[node]
    return f"c{coarse5_index(x)}{coarse5_index(y)}"


def coarse5_signature(path: CleanedPath, graph_spec: GraphSpec) -> str:
    coarse_segments: list[list[str]] = []
    for segment in path.route_shape_segments:
        coarse_segment: list[str] = []
        for node in segment:
            coarse = coarse5_for_node(
                parse_int(cast(Any, node), "route node"), graph_spec
            )
            if not coarse_segment or coarse_segment[-1] != coarse:
                coarse_segment.append(coarse)
        if coarse_segment:
            coarse_segments.append(coarse_segment)
    return "|".join("-".join(segment) for segment in coarse_segments)


def route_support(
    rows: Sequence[Mapping[str, Any]], signature_field: str
) -> list[dict[str, Any]]:
    counts: dict[tuple[str, str, str], Counter[str]] = defaultdict(Counter)
    sessions: dict[tuple[str, str, str, str], set[str]] = defaultdict(set)
    for row in rows:
        key = (str(row["start"]), str(row["goal"]), str(row[signature_field]))
        split = str(row["split"])
        counts[key][split] += 1
        sessions[(*key, split)].add(str(row["session_id"]))
    out: list[dict[str, Any]] = []
    for (start, goal, signature), by_split in sorted(counts.items()):
        out.append(
            {
                "start": start,
                "goal": goal,
                signature_field: signature,
                "train_trials": by_split["train"],
                "validation_trials": by_split["validation"],
                "train_sessions": len(sessions[(start, goal, signature, "train")]),
                "validation_sessions": len(
                    sessions[(start, goal, signature, "validation")]
                ),
                "has_train_validation_support": str(
                    bool(by_split["train"] and by_split["validation"])
                ).lower(),
            }
        )
    out.sort(
        key=lambda r: (
            -(r["train_trials"] + r["validation_trials"]),
            r["start"],
            r["goal"],
            r[signature_field],
        )
    )
    return out


def supportable_signatures(
    rows: Sequence[Mapping[str, Any]], min_train: int, min_validation: int
) -> set[tuple[str, str, str]]:
    supported: set[tuple[str, str, str]] = set()
    for row in route_support(rows, "coarse5_signature"):
        if (
            row["train_trials"] >= min_train
            and row["validation_trials"] >= min_validation
        ):
            supported.add(
                (str(row["start"]), str(row["goal"]), str(row["coarse5_signature"]))
            )
    return supported


def apply_route_family(
    rows: Sequence[dict[str, Any]], supported: set[tuple[str, str, str]]
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in rows:
        copied = dict(row)
        key = (str(row["start"]), str(row["goal"]), str(row["coarse5_signature"]))
        route_family = (
            str(row["coarse5_signature"]) if key in supported else ROUTE_OTHER
        )
        copied["route_family"] = route_family
        copied["target_label"] = f"{row['start']}->{row['goal']}|{route_family}"
        out.append(copied)
    return out


def iter_mapped_trials(
    import_dir: Path,
    labels: Mapping[str, TrialLabel],
    graph_spec: GraphSpec,
    mapped_sample_path: Path,
) -> Iterable[tuple[TrialLabel, list[int], CleanedPath]]:
    fieldnames = (
        "session_id",
        "source_trial_id",
        "split",
        "navigation_sample",
        "position_axis1",
        "position_axis2",
        "mapped_node",
    )
    path = import_dir / "path_samples.csv.gz"
    current_source = ""
    current_label: TrialLabel | None = None
    current_nodes: list[int] = []
    with gzip.open(
        mapped_sample_path, "wt", encoding="utf-8", newline=""
    ) as sample_handle:
        writer = csv.DictWriter(sample_handle, fieldnames=fieldnames)
        writer.writeheader()
        with open_text(path) as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                source = row["source_trial_id"]
                label = labels.get(source)
                if label is None:
                    continue
                if current_label is None:
                    current_source = source
                    current_label = label
                if source != current_source:
                    if current_label is None:
                        raise RuntimeError(
                            "missing current trial label while flushing mapped path"
                        )
                    yield (
                        current_label,
                        current_nodes,
                        clean_path(current_nodes, graph_spec.graph),
                    )
                    current_source = source
                    current_label = label
                    current_nodes = []
                x = parse_float(row["position_axis1"], "position_axis1")
                y = parse_float(row["position_axis2"], "position_axis2")
                node = map_position_to_node(x, y, graph_spec)
                current_nodes.append(node)
                writer.writerow(
                    {
                        "session_id": label.session_id,
                        "source_trial_id": source,
                        "split": label.split,
                        "navigation_sample": row["navigation_sample"],
                        "position_axis1": row["position_axis1"],
                        "position_axis2": row["position_axis2"],
                        "mapped_node": node,
                    }
                )
    if current_label is not None:
        yield current_label, current_nodes, clean_path(current_nodes, graph_spec.graph)


def build_trial_rows(
    import_dir: Path,
    labels: Mapping[str, TrialLabel],
    graph_spec: GraphSpec,
    output_dir: Path,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    mapped_path = (
        output_dir / "mapped_path_samples_train_validation_success_after_success.csv.gz"
    )
    for label, _nodes, path in iter_mapped_trials(
        import_dir, labels, graph_spec, mapped_path
    ):
        fine_signature = signature_from_segments(path.route_shape_segments)
        edge_count = sum(len(edges) for edges in directed_edge_sequences(path))
        coarse_signature = coarse5_signature(path, graph_spec)
        rows.append(
            {
                "session_id": label.session_id,
                "source_trial_id": label.source_trial_id,
                "split": label.split,
                "trial_index": label.trial_index,
                "start": label.start,
                "goal": label.goal,
                "raw_sample_count": path.audit.raw_sample_count,
                "valid_sample_count": path.audit.valid_sample_count,
                "invalid_sample_count": path.audit.invalid_sample_count,
                "invalid_gap_count": path.audit.invalid_gap_count,
                "nonadjacent_transition_count": path.audit.nonadjacent_transition_count,
                "raw_valid_segment_count": path.audit.raw_valid_segment_count,
                "route_shape_segment_count": path.audit.route_shape_segment_count,
                "repeated_sample_count": path.audit.repeated_sample_count,
                "route_shape_node_count": sum(
                    len(segment) for segment in path.route_shape_segments
                ),
                "directed_edge_count": edge_count,
                "fine_signature_sha256": signature_sha256(fine_signature),
                "fine_signature": fine_signature,
                "coarse5_signature": coarse_signature,
                "coarse5_signature_sha256": signature_sha256(coarse_signature),
            }
        )
    return rows


def start_goal_support(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    counts: dict[tuple[str, str], Counter[str]] = defaultdict(Counter)
    sessions: dict[tuple[str, str, str], set[str]] = defaultdict(set)
    for row in rows:
        key = (str(row["start"]), str(row["goal"]))
        split = str(row["split"])
        counts[key][split] += 1
        sessions[(*key, split)].add(str(row["session_id"]))
    out: list[dict[str, Any]] = []
    for (start, goal), by_split in sorted(counts.items()):
        out.append(
            {
                "start": start,
                "goal": goal,
                "train_trials": by_split["train"],
                "validation_trials": by_split["validation"],
                "train_sessions": len(sessions[(start, goal, "train")]),
                "validation_sessions": len(sessions[(start, goal, "validation")]),
            }
        )
    return out


def load_units_by_session(import_dir: Path) -> tuple[list[str], dict[str, set[str]]]:
    unit_rows = read_csv(import_dir / "units.csv")
    units = [row["cell_id"] for row in unit_rows]
    by_session: dict[str, set[str]] = defaultdict(set)
    for row in unit_rows:
        by_session[row["session_id"]].add(row["cell_id"])
    return units, by_session


def pseudopop_cell_support(
    rows: Sequence[Mapping[str, Any]],
    units: Sequence[str],
    units_by_session: Mapping[str, set[str]],
) -> list[dict[str, Any]]:
    sessions_by_key: dict[tuple[str, str, str, str], set[str]] = defaultdict(set)
    trials_by_key: Counter[tuple[str, str, str, str]] = Counter()
    all_units = set(units)
    for row in rows:
        key = (
            str(row["start"]),
            str(row["goal"]),
            str(row["route_family"]),
            str(row["split"]),
        )
        sessions_by_key[key].add(str(row["session_id"]))
        trials_by_key[key] += 1
    out: list[dict[str, Any]] = []
    for key in sorted(sessions_by_key):
        start, goal, route_family, split = key
        sessions = sessions_by_key[key]
        observed_units = (
            set().union(*(units_by_session[session] for session in sessions))
            if sessions
            else set()
        )
        missing_units = sorted(all_units - observed_units)
        out.append(
            {
                "start": start,
                "goal": goal,
                "route_family": route_family,
                "split": split,
                "trial_count": trials_by_key[key],
                "sessions_observed": len(sessions),
                "cells_observed": len(observed_units),
                "missing_cells_for_full195": len(missing_units),
                "missing_cell_fraction_for_full195": round(
                    len(missing_units) / len(all_units), 6
                ),
                "missing_cell_ids": ";".join(missing_units),
                "missing_session_ids": ";".join(
                    sorted(set(units_by_session) - sessions)
                ),
            }
        )
    out.sort(
        key=lambda r: (
            -r["trial_count"],
            r["start"],
            r["goal"],
            r["route_family"],
            r["split"],
        )
    )
    return out


def load_cue_counts_by_source_cell(import_dir: Path) -> dict[tuple[str, str], float]:
    counts: dict[tuple[str, str], float] = {}
    with open_text(import_dir / "cue_counts.csv.gz") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            counts[(row["source_trial_id"], row["cell_id"])] = parse_float(
                row["cue_spike_count"], "cue_spike_count"
            )
    return counts


def pseudopop_target_count(session_trial_counts: Sequence[int], max_rows: int) -> int:
    if not session_trial_counts:
        return 0
    ordered = sorted(session_trial_counts)
    q1 = ordered[len(ordered) // 4]
    return max(1, min(max_rows, q1))


def build_condition_pseudopopulation(
    rows: Sequence[Mapping[str, Any]],
    units: Sequence[str],
    units_by_session: Mapping[str, set[str]],
    cue_counts: Mapping[tuple[str, str], float],
    max_rows_per_condition: int = 10,
) -> Pseudopopulation:
    unit_index = {unit: index for index, unit in enumerate(units)}
    grouped: dict[tuple[str, str], dict[str, list[Mapping[str, Any]]]] = defaultdict(
        lambda: defaultdict(list)
    )
    row_by_label: dict[tuple[str, str], Mapping[str, Any]] = {}
    for row in rows:
        key = (str(row["split"]), str(row["target_label"]))
        grouped[key][str(row["session_id"])].append(row)
        row_by_label.setdefault(key, row)
    for by_session in grouped.values():
        for trial_rows in by_session.values():
            trial_rows.sort(
                key=lambda row: (
                    parse_int(row["trial_index"], "trial_index"),
                    str(row["source_trial_id"]),
                )
            )

    pseudo_rows: list[dict[str, Any]] = []
    components: list[dict[str, Any]] = []
    x_rows: list[np.ndarray] = []
    observed_rows: list[np.ndarray] = []
    all_sessions = set(units_by_session)
    pseudo_index = 0
    for split_label in sorted(grouped):
        split, target_label = split_label
        template = row_by_label[split_label]
        by_session = grouped[split_label]
        target_n = pseudopop_target_count(
            [len(items) for items in by_session.values()], max_rows_per_condition
        )
        for k in range(target_n):
            row_id = f"pp_{pseudo_index:06d}"
            pseudo_index += 1
            x = np.full(len(units), np.nan, dtype=np.float64)
            observed = np.zeros(len(units), dtype=bool)
            component_sessions: list[str] = []
            bootstrapped_sessions: list[str] = []
            source_trials: list[str] = []
            for session_id, trial_rows in sorted(by_session.items()):
                trial = trial_rows[k % len(trial_rows)]
                bootstrapped = k >= len(trial_rows)
                if bootstrapped:
                    bootstrapped_sessions.append(session_id)
                component_sessions.append(session_id)
                source_id = str(trial["source_trial_id"])
                source_trials.append(source_id)
                session_cells = sorted(
                    units_by_session[session_id], key=lambda cell: unit_index[cell]
                )
                cell_count = 0
                for cell in session_cells:
                    value = cue_counts.get((source_id, cell))
                    if value is None:
                        continue
                    x[unit_index[cell]] = value
                    observed[unit_index[cell]] = True
                    cell_count += 1
                components.append(
                    {
                        "pseudopop_row_id": row_id,
                        "split": split,
                        "target_label": target_label,
                        "session_id": session_id,
                        "source_trial_id": source_id,
                        "cell_count": cell_count,
                        "bootstrapped_component": str(bootstrapped).lower(),
                    }
                )
            observed_count = parse_int(observed.sum().item(), "observed cells")
            missing_sessions = sorted(all_sessions - set(component_sessions))
            pseudo_rows.append(
                {
                    "pseudopop_row_id": row_id,
                    "split": split,
                    "start": template["start"],
                    "goal": template["goal"],
                    "route_family": template["route_family"],
                    "target_label": target_label,
                    "pseudopop_index_within_condition": k,
                    "observed_cells": observed_count,
                    "missing_cells": len(units) - observed_count,
                    "observed_cell_fraction": observed_count / len(units),
                    "component_sessions": len(component_sessions),
                    "missing_sessions": len(missing_sessions),
                    "bootstrapped_component_sessions": len(bootstrapped_sessions),
                    "component_session_ids": ";".join(component_sessions),
                    "missing_session_ids": ";".join(missing_sessions),
                    "component_source_trial_ids": ";".join(source_trials),
                    "row_unit": "condition_matched_pseudopopulation",
                }
            )
            x_rows.append(x)
            observed_rows.append(observed)
    return Pseudopopulation(
        rows=pseudo_rows,
        components=components,
        x=np.vstack(x_rows) if x_rows else np.empty((0, len(units))),
        observed=np.vstack(observed_rows) if observed_rows else np.empty((0, len(units)), dtype=bool),
    )


def train_fit_masked_zscore(
    x: np.ndarray, observed: np.ndarray, split: Sequence[str]
) -> tuple[np.ndarray, dict[str, Any]]:
    train_mask = np.array([item == "train" for item in split], dtype=bool)
    train_observed = observed & train_mask[:, None]
    means = np.zeros(x.shape[1], dtype=np.float64)
    stds = np.ones(x.shape[1], dtype=np.float64)
    for col in range(x.shape[1]):
        values = x[train_observed[:, col], col]
        if values.size:
            means[col] = np.mean(values).item()
            std = np.std(values).item()
            stds[col] = std if std > 1e-12 else 1.0
    z = np.full_like(x, np.nan, dtype=np.float64)
    z[observed] = ((x - means[None, :]) / stds[None, :])[observed]
    observed_entries = parse_int(observed.sum().item(), "observed entries")
    total_entries = observed.size
    return z, {
        "rows": x.shape[0],
        "features": x.shape[1],
        "observed_entries": observed_entries,
        "missing_entries": total_entries - observed_entries,
        "observed_fraction": observed_entries / total_entries if total_entries else None,
        "missing_fraction": 1 - (observed_entries / total_entries) if total_entries else None,
        "normalization_policy": "per-cell mean/std fit on observed train pseudopop values only",
        "imputation_policy": "none; missing cells stay masked and distances use overlap only",
    }


def masked_nearest_centroid_predictions(
    z: np.ndarray,
    observed: np.ndarray,
    rows: Sequence[Mapping[str, Any]],
    min_overlap: int = 5,
) -> tuple[list[str], list[int], list[bool]]:
    labels = np.array([str(row["target_label"]) for row in rows], dtype=object)
    starts_goals = np.array(
        [f"{row['start']}->{row['goal']}" for row in rows], dtype=object
    )
    split = np.array([str(row["split"]) for row in rows], dtype=object)
    train_mask = split == "train"
    centroids: dict[str, np.ndarray] = {}
    centroid_observed: dict[str, np.ndarray] = {}
    centroid_start_goal: dict[str, str] = {}
    for label in sorted(set(labels[train_mask])):
        mask = train_mask & (labels == label)
        obs_counts = observed[mask].sum(axis=0)
        sums = np.nansum(np.where(observed[mask], z[mask], 0.0), axis=0)
        centroid = np.full(z.shape[1], np.nan, dtype=np.float64)
        valid = obs_counts > 0
        centroid[valid] = sums[valid] / obs_counts[valid]
        centroids[label] = centroid
        centroid_observed[label] = valid
        centroid_start_goal[label] = str(starts_goals[mask][0])

    predictions: list[str] = []
    overlaps: list[int] = []
    supported: list[bool] = []
    global_labels = sorted(centroids)
    for i, _row in enumerate(rows):
        candidates = [
            label
            for label in global_labels
            if centroid_start_goal[label] == starts_goals[i]
        ]
        best_label = ""
        best_distance = math.inf
        best_overlap = 0
        for label in candidates:
            overlap = observed[i] & centroid_observed[label]
            overlap_n = parse_int(overlap.sum().item(), "overlap cells")
            if overlap_n < min_overlap:
                continue
            distance = np.mean((z[i, overlap] - centroids[label][overlap]) ** 2).item()
            if distance < best_distance:
                best_distance = distance
                best_label = label
                best_overlap = overlap_n
        predictions.append(best_label)
        overlaps.append(best_overlap)
        supported.append(bool(best_label))
    return predictions, overlaps, supported


def pseudopop_prediction_rows(
    rows: Sequence[Mapping[str, Any]],
    baseline: Sequence[str],
    neural: Sequence[str],
    overlaps: Sequence[int],
    supported: Sequence[bool],
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row, base_pred, neural_pred, overlap, is_supported in zip(
        rows, baseline, neural, overlaps, supported, strict=True
    ):
        if row["split"] != "validation":
            continue
        out.append(
            {
                "pseudopop_row_id": row["pseudopop_row_id"],
                "start": row["start"],
                "goal": row["goal"],
                "route_family": row["route_family"],
                "target_label": row["target_label"],
                "observed_cells": row["observed_cells"],
                "missing_cells": row["missing_cells"],
                "start_goal_majority_prediction": base_pred,
                "condition_matched_pseudopop_neural_prediction": neural_pred,
                "neural_overlap_cells": overlap,
                "neural_prediction_supported": str(is_supported).lower(),
                "baseline_correct": str(base_pred == row["target_label"]).lower(),
                "neural_correct": str(neural_pred == row["target_label"]).lower(),
            }
        )
    return out


def neural_support_summary(
    rows: Sequence[Mapping[str, Any]], overlaps: Sequence[int], supported: Sequence[bool]
) -> dict[str, Any]:
    validation = [
        (row, overlap, ok)
        for row, overlap, ok in zip(rows, overlaps, supported, strict=True)
        if row["split"] == "validation"
    ]
    validation_overlaps = [overlap for _row, overlap, ok in validation if ok]
    return {
        "validation_supported_rows": sum(1 for _row, _overlap, ok in validation if ok),
        "validation_unsupported_rows": sum(1 for _row, _overlap, ok in validation if not ok),
        "validation_mean_overlap_cells_when_supported": (
            sum(validation_overlaps) / len(validation_overlaps)
            if validation_overlaps
            else None
        ),
        "validation_min_overlap_cells_when_supported": min(validation_overlaps) if validation_overlaps else None,
    }


def majority_predictions(rows: Sequence[Mapping[str, Any]]) -> list[str]:
    by_start_goal: dict[tuple[str, str], Counter[str]] = defaultdict(Counter)
    global_counts: Counter[str] = Counter()
    for row in rows:
        if row["split"] != "train":
            continue
        label = str(row["target_label"])
        by_start_goal[(str(row["start"]), str(row["goal"]))][label] += 1
        global_counts[label] += 1
    global_label = global_counts.most_common(1)[0][0]
    predictions: list[str] = []
    for row in rows:
        counts = by_start_goal[(str(row["start"]), str(row["goal"]))]
        predictions.append(counts.most_common(1)[0][0] if counts else global_label)
    return predictions


def metrics(
    rows: Sequence[Mapping[str, Any]], predictions: Sequence[str], model_name: str
) -> dict[str, Any]:
    validation_indices = [
        i for i, row in enumerate(rows) if row["split"] == "validation"
    ]
    correct = 0
    by_class: dict[str, list[bool]] = defaultdict(list)
    by_start_goal: dict[str, list[bool]] = defaultdict(list)
    for i in validation_indices:
        truth = str(rows[i]["target_label"])
        ok = predictions[i] == truth
        correct += 1 if ok else 0
        by_class[truth].append(ok)
        by_start_goal[f"{rows[i]['start']}->{rows[i]['goal']}"].append(ok)
    return {
        "model": model_name,
        "validation_rows": len(validation_indices),
        "validation_accuracy": correct / len(validation_indices)
        if validation_indices
        else None,
        "validation_macro_class_accuracy": mean_or_none(
            [
                mean_or_none([1.0 if ok else 0.0 for ok in v]) or 0.0
                for v in by_class.values()
            ]
        ),
        "validation_macro_start_goal_accuracy": mean_or_none(
            [
                mean_or_none([1.0 if ok else 0.0 for ok in v]) or 0.0
                for v in by_start_goal.values()
            ]
        ),
        "validation_classes": len(by_class),
        "validation_start_goal_pairs": len(by_start_goal),
    }


def confusion_rows(
    rows: Sequence[Mapping[str, Any]], predictions: Sequence[str], model_name: str
) -> list[dict[str, Any]]:
    counts: Counter[tuple[str, str]] = Counter()
    for row, pred in zip(rows, predictions, strict=True):
        if row["split"] != "validation":
            continue
        counts[(str(row["target_label"]), pred)] += 1
    return [
        {"model": model_name, "truth": truth, "prediction": pred, "count": count}
        for (truth, pred), count in sorted(
            counts.items(), key=lambda item: (-item[1], item[0][0], item[0][1])
        )
    ]


def shared_edge_candidates(
    rows: Sequence[Mapping[str, Any]], graph_spec: GraphSpec, limit: int = 120
) -> list[dict[str, Any]]:
    top_by_condition: dict[tuple[str, str, str], Mapping[str, Any]] = {}
    counts: Counter[tuple[str, str, str]] = Counter()
    for row in rows:
        key = (str(row["start"]), str(row["goal"]), str(row["route_family"]))
        counts[key] += 1
        top_by_condition.setdefault(key, row)
    selected = [key for key, _ in counts.most_common(limit) if key[2] != ROUTE_OTHER]
    cleaned: dict[tuple[str, str, str], CleanedPath] = {}
    for key in selected:
        row = top_by_condition[key]
        segments = []
        for segment in str(row["fine_signature"]).split("|"):
            if segment:
                segments.extend(
                    parse_int(node, "fine signature node")
                    for node in segment.split("-")
                    if node
                )
            segments.append(0)
        cleaned[key] = clean_path(segments, graph_spec.graph)
    out: list[dict[str, Any]] = []
    for i, left_key in enumerate(selected):
        for right_key in selected[i + 1 :]:
            if left_key[:2] == right_key[:2]:
                continue
            shared = longest_shared_contiguous_directed_segment(
                cleaned[left_key], cleaned[right_key]
            )
            if shared.length <= 0:
                continue
            out.append(
                {
                    "left_start": left_key[0],
                    "left_goal": left_key[1],
                    "left_route_family": left_key[2],
                    "right_start": right_key[0],
                    "right_goal": right_key[1],
                    "right_route_family": right_key[2],
                    "same_start": str(left_key[0] == right_key[0]).lower(),
                    "same_goal": str(left_key[1] == right_key[1]).lower(),
                    "shared_directed_edges": shared.length,
                    "shared_segment_classification": shared.classification,
                    "shared_edges": json.dumps(shared.edges),
                }
            )
    out.sort(
        key=lambda r: (-r["shared_directed_edges"], r["shared_segment_classification"])
    )
    return out[:limit]


def plot_sample_paths(
    rows: Sequence[Mapping[str, Any]], graph_spec: GraphSpec, output_dir: Path
) -> list[Path]:
    figure_dir = output_dir / "figures"
    figure_dir.mkdir(exist_ok=True)
    paths: list[Path] = []
    samples = sorted(
        rows,
        key=lambda row: (
            row["split"] != "validation",
            row["start"],
            row["goal"],
            row["source_trial_id"],
        ),
    )[:12]
    paths.append(
        plot_rows(
            samples, graph_spec, figure_dir / "sample_mapped_paths_by_source_trial.png"
        )
    )
    top_pairs = Counter((row["start"], row["goal"]) for row in rows).most_common(6)
    pair_rows = []
    for pair, _count in top_pairs:
        pair_rows.extend(
            [row for row in rows if (row["start"], row["goal"]) == pair][:2]
        )
    paths.append(
        plot_rows(
            pair_rows[:12],
            graph_spec,
            figure_dir / "sample_mapped_paths_by_start_goal.png",
        )
    )
    return paths


def plot_rows(
    rows: Sequence[Mapping[str, Any]], graph_spec: GraphSpec, path: Path
) -> Path:
    cols = 3
    rows_n = max(1, math.ceil(len(rows) / cols))
    fig, axes = plt.subplots(rows_n, cols, figsize=(12, rows_n * 3.5), squeeze=False)
    xs = [coord[0] for coord in graph_spec.centroids.values()]
    ys = [coord[1] for coord in graph_spec.centroids.values()]
    for ax in axes.flat:
        ax.scatter(xs, ys, s=1, color="lightgray")
        ax.set_aspect("equal", adjustable="box")
        ax.set_xticks([])
        ax.set_yticks([])
    for ax, row in zip(axes.flat, rows, strict=False):
        for segment in str(row["fine_signature"]).split("|"):
            nodes = [
                parse_int(node, "plot node") for node in segment.split("-") if node
            ]
            if not nodes:
                continue
            coords = [graph_spec.centroids[node] for node in nodes]
            ax.plot(
                [x for x, _ in coords], [y for _, y in coords], marker=".", linewidth=1
            )
        ax.set_title(
            f"{row['source_trial_id']}\n{row['split']} {row['start']}→{row['goal']}",
            fontsize=8,
        )
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def run_audit(
    import_dir: Path,
    split_dir: Path,
    geometry: Path,
    output_dir: Path,
    receipt_path: Path,
    min_train: int,
    min_validation: int,
) -> dict[str, Any]:
    validate_output_dir(output_dir, import_dir)
    output_dir.mkdir(parents=True, exist_ok=False)
    graph_spec = build_graph(geometry)
    labels = load_trial_labels(import_dir, split_dir)
    trial_rows = build_trial_rows(import_dir, labels, graph_spec, output_dir)
    train_supported = supportable_signatures(trial_rows, min_train, 0)
    train_validation_supported = supportable_signatures(
        trial_rows, min_train, min_validation
    )
    training_rows = apply_route_family(trial_rows, train_supported)
    units, units_by_session = load_units_by_session(import_dir)

    trial_path = write_csv(
        output_dir / "trial_graph_path_audit.csv",
        trial_rows,
        (
            "session_id",
            "source_trial_id",
            "split",
            "trial_index",
            "start",
            "goal",
            "raw_sample_count",
            "valid_sample_count",
            "invalid_sample_count",
            "invalid_gap_count",
            "nonadjacent_transition_count",
            "raw_valid_segment_count",
            "route_shape_segment_count",
            "repeated_sample_count",
            "route_shape_node_count",
            "directed_edge_count",
            "fine_signature_sha256",
            "fine_signature",
            "coarse5_signature",
            "coarse5_signature_sha256",
        ),
    )
    start_goal_path = write_csv(
        output_dir / "support_start_goal.csv",
        start_goal_support(training_rows),
        (
            "start",
            "goal",
            "train_trials",
            "validation_trials",
            "train_sessions",
            "validation_sessions",
        ),
    )
    fine_support_path = write_csv(
        output_dir / "fine_signature_support.csv",
        route_support(training_rows, "fine_signature_sha256"),
        (
            "start",
            "goal",
            "fine_signature_sha256",
            "train_trials",
            "validation_trials",
            "train_sessions",
            "validation_sessions",
            "has_train_validation_support",
        ),
    )
    coarse_support_path = write_csv(
        output_dir / "coarse5_signature_support.csv",
        route_support(training_rows, "coarse5_signature"),
        (
            "start",
            "goal",
            "coarse5_signature",
            "train_trials",
            "validation_trials",
            "train_sessions",
            "validation_sessions",
            "has_train_validation_support",
        ),
    )
    training_table_path = write_csv(
        output_dir / "supportable_training_table.csv",
        training_rows,
        (
            "session_id",
            "source_trial_id",
            "split",
            "start",
            "goal",
            "coarse5_signature",
            "route_family",
            "target_label",
            "fine_signature_sha256",
            "coarse5_signature_sha256",
            "raw_sample_count",
            "nonadjacent_transition_count",
            "route_shape_segment_count",
            "directed_edge_count",
        ),
    )
    cell_support_path = write_csv(
        output_dir / "pseudopop_cell_support.csv",
        pseudopop_cell_support(training_rows, units, units_by_session),
        (
            "start",
            "goal",
            "route_family",
            "split",
            "trial_count",
            "sessions_observed",
            "cells_observed",
            "missing_cells_for_full195",
            "missing_cell_fraction_for_full195",
            "missing_cell_ids",
            "missing_session_ids",
        ),
    )
    shared_path = write_csv(
        output_dir / "shared_edge_contrast_candidates.csv",
        shared_edge_candidates(training_rows, graph_spec),
        (
            "left_start",
            "left_goal",
            "left_route_family",
            "right_start",
            "right_goal",
            "right_route_family",
            "same_start",
            "same_goal",
            "shared_directed_edges",
            "shared_segment_classification",
            "shared_edges",
        ),
    )

    cue_counts = load_cue_counts_by_source_cell(import_dir)
    pseudopop = build_condition_pseudopopulation(
        training_rows, units, units_by_session, cue_counts
    )
    pseudopop_rows_path = write_csv(
        output_dir / "condition_pseudopopulation_rows.csv",
        pseudopop.rows,
        (
            "pseudopop_row_id",
            "split",
            "start",
            "goal",
            "route_family",
            "target_label",
            "pseudopop_index_within_condition",
            "observed_cells",
            "missing_cells",
            "observed_cell_fraction",
            "component_sessions",
            "missing_sessions",
            "bootstrapped_component_sessions",
            "component_session_ids",
            "missing_session_ids",
            "component_source_trial_ids",
            "row_unit",
        ),
    )
    pseudopop_components_path = write_csv(
        output_dir / "condition_pseudopopulation_components.csv",
        pseudopop.components,
        (
            "pseudopop_row_id",
            "split",
            "target_label",
            "session_id",
            "source_trial_id",
            "cell_count",
            "bootstrapped_component",
        ),
    )
    feature_matrix_path = output_dir / "condition_pseudopopulation_features.npz"
    np.savez_compressed(
        feature_matrix_path,
        x=pseudopop.x,
        observed=pseudopop.observed,
        unit_ids=np.array(units, dtype=object),
        split=np.array([row["split"] for row in pseudopop.rows], dtype=object),
        target_label=np.array(
            [row["target_label"] for row in pseudopop.rows], dtype=object
        ),
        pseudopop_row_id=np.array(
            [row["pseudopop_row_id"] for row in pseudopop.rows], dtype=object
        ),
    )

    baseline_pred = majority_predictions(pseudopop.rows)
    z, pseudopop_coverage = train_fit_masked_zscore(
        pseudopop.x,
        pseudopop.observed,
        [str(row["split"]) for row in pseudopop.rows],
    )
    neural_pred, neural_overlaps, neural_supported = masked_nearest_centroid_predictions(
        z, pseudopop.observed, pseudopop.rows
    )
    baseline_metrics = metrics(
        pseudopop.rows, baseline_pred, "pseudopop_start_goal_majority"
    )
    neural_metrics = metrics(
        pseudopop.rows,
        neural_pred,
        "condition_matched_pseudopop_nearest_centroid_within_start_goal",
    ) | neural_support_summary(pseudopop.rows, neural_overlaps, neural_supported)
    predictions_path = write_csv(
        output_dir / "validation_predictions.csv",
        pseudopop_prediction_rows(
            pseudopop.rows,
            baseline_pred,
            neural_pred,
            neural_overlaps,
            neural_supported,
        ),
        (
            "pseudopop_row_id",
            "start",
            "goal",
            "route_family",
            "target_label",
            "observed_cells",
            "missing_cells",
            "start_goal_majority_prediction",
            "condition_matched_pseudopop_neural_prediction",
            "neural_overlap_cells",
            "neural_prediction_supported",
            "baseline_correct",
            "neural_correct",
        ),
    )
    confusion_path = write_csv(
        output_dir / "validation_confusion.csv",
        confusion_rows(pseudopop.rows, baseline_pred, "pseudopop_start_goal_majority")
        + confusion_rows(
            pseudopop.rows,
            neural_pred,
            "condition_matched_pseudopop_nearest_centroid_within_start_goal",
        ),
        ("model", "truth", "prediction", "count"),
    )
    metrics_path = output_dir / "validation_metrics.json"
    write_json(
        metrics_path,
        {
            "baseline": baseline_metrics,
            "condition_matched_pseudopop_nearest_centroid": neural_metrics,
            "pseudopop_coverage": pseudopop_coverage,
        },
    )
    figure_paths = plot_sample_paths(training_rows, graph_spec, output_dir)

    split_summary = read_json(split_dir / "split_summary.json")
    import_summary = read_json(import_dir / "summary.json")
    class_counts = Counter(row["target_label"] for row in training_rows)
    validation_labels = {
        row["target_label"] for row in training_rows if row["split"] == "validation"
    }
    artifact_paths = [
        output_dir
        / "mapped_path_samples_train_validation_success_after_success.csv.gz",
        trial_path,
        start_goal_path,
        fine_support_path,
        coarse_support_path,
        training_table_path,
        cell_support_path,
        shared_path,
        pseudopop_rows_path,
        pseudopop_components_path,
        feature_matrix_path,
        predictions_path,
        confusion_path,
        metrics_path,
        *figure_paths,
    ]
    def artifact_key(path: Path) -> str:
        if path.is_relative_to(output_dir):
            return path.relative_to(output_dir).as_posix()
        return path.as_posix()

    summary: dict[str, Any] = {
        "created_utc": datetime.now(UTC).isoformat(),
        "status": "completed_exploratory_training_run",
        "scientific_status": SCIENTIFIC_STATUS,
        "import_dir": str(import_dir),
        "split_dir": str(split_dir),
        "geometry": str(geometry),
        "output_dir": str(output_dir),
        "receipt_path": str(receipt_path),
        "input_artifact_hashes": {
            "trials.csv": import_summary.get("artifact_hashes", {}).get("trials.csv"),
            "path_samples.csv.gz": import_summary.get("artifact_hashes", {}).get(
                "path_samples.csv.gz"
            ),
            "cue_counts.csv.gz": import_summary.get("artifact_hashes", {}).get(
                "cue_counts.csv.gz"
            ),
            "units.csv": import_summary.get("artifact_hashes", {}).get("units.csv"),
            "source_trial_splits.csv": split_summary.get("artifact_hashes", {}).get(
                "source_trial_splits.csv"
            ),
            "geometry": graph_spec.geometry_sha256,
        },
        "split_hash": split_summary.get("split_hash"),
        "graph": {
            "schema": GRAPH_SCHEMA,
            "script_primary_graph_hash": graph_spec.primary_graph_hash,
            "pinned_primary_graph_hash_from_receipt": PINNED_PRIMARY_GRAPH_HASH,
            "script_hash_matches_pinned_receipt_hash": graph_spec.primary_graph_hash
            == PINNED_PRIMARY_GRAPH_HASH,
            "node_count": len(graph_spec.centroids),
            "undirected_edge_count": graph_spec.undirected_edge_count,
            "directed_edge_count": len(graph_spec.directed_edges),
            "connected_components": graph_spec.connected_components,
            "grid_step": GRID_STEP,
            "mapping_tolerance": MAPPING_TOLERANCE,
        },
        "filters": {
            "splits_used": ["train", "validation"],
            "locked_test_used": False,
            "current_timeout_trials": "dropped",
            "endpoint_subset": "success_after_success",
            "route_design_uses_neural_activity": False,
        },
        "route_family": {
            "status": "exploratory_coarse5_graph_node_signature_train_frozen_for_model",
            "coarse_rule": "map fine graph nodes to fixed 5x5 Unity-space bins, collapse consecutive repeats, keep segment separators",
            "model_vocabulary_min_train_trials": min_train,
            "descriptive_support_min_validation_trials": min_validation,
            "unsupported_policy": ROUTE_OTHER,
            "train_supported_route_families_for_model": len(train_supported),
            "train_validation_supported_route_families_descriptive": len(
                train_validation_supported
            ),
            "target_classes": len(class_counts),
            "validation_target_classes": len(validation_labels),
        },
        "counts": {
            "endpoint_labelled_train_validation_trials": len(training_rows),
            "train_trials": sum(1 for row in training_rows if row["split"] == "train"),
            "validation_trials": sum(
                1 for row in training_rows if row["split"] == "validation"
            ),
            "fine_signatures": len(
                {row["fine_signature_sha256"] for row in training_rows}
            ),
            "coarse5_signatures": len(
                {row["coarse5_signature"] for row in training_rows}
            ),
            "trials_collapsed_to_other": sum(
                1 for row in training_rows if row["route_family"] == ROUTE_OTHER
            ),
            "pseudopopulation_rows": len(pseudopop.rows),
            "pseudopopulation_train_rows": sum(
                1 for row in pseudopop.rows if row["split"] == "train"
            ),
            "pseudopopulation_validation_rows": sum(
                1 for row in pseudopop.rows if row["split"] == "validation"
            ),
        },
        "pseudopopulation": {
            "row_unit": "condition_matched_pseudopopulation",
            "assembly": "one or more deterministic pseudopop rows per split and target_label; each session contributes one same-condition source trial per row, and that session's cells use that trial's cue count",
            "target_count_rule": "25th-percentile session trial count per condition, capped at 10, with deterministic within-session cycling when needed",
            "cell_imputation": "none in V5; missing cells remain masked",
            "neural_distance_min_overlap_cells": 5,
            "target_classes": len({row["target_label"] for row in pseudopop.rows}),
            "validation_target_classes": len(
                {row["target_label"] for row in pseudopop.rows if row["split"] == "validation"}
            ),
        },
        "validation": {
            "baseline": baseline_metrics,
            "condition_matched_pseudopop_nearest_centroid": neural_metrics,
            "pseudopop_coverage": pseudopop_coverage,
        },
        "commands": {
            "test": "uv run python -m unittest scripts.test_import_place195_sessions scripts.test_place195_split_and_behavior_audit scripts.test_place195_graph_path_baseline docs.cebra_pilot.implementation.tests.test_framework",
            "run": "uv run python -m scripts.place195_graph_path_baseline run "
            f"--import-dir {import_dir} --split-dir {split_dir} --geometry {geometry} "
            f"--output-dir {output_dir} --receipt {receipt_path} "
            f"--min-train {min_train} --min-validation {min_validation}",
            "post_run_validation": "artifact hashes recomputed; supportable_training_table.csv, condition_pseudopopulation_rows.csv, and validation_predictions.csv checked for zero test rows",
        },
        "guardrails": {
            "test_rows_in_outputs": False,
            "cell_imputation_used_in_v5_neural_model": False,
            "imputation_is_primary_evidence": False,
            "claims_h1_evidence": False,
            "claims_simultaneous_population": False,
            "marker_labels_verified": False,
        },
        "stop_conditions": [
            "stop if geometry hash/counts/connectivity mismatch",
            "stop if no train/validation route-family support remains",
            "stop before H1 claims until marker semantics and simultaneity are independently verified",
        ],
        "artifact_hashes": {artifact_key(path): sha256_file(path) for path in artifact_paths},
        "code_hashes": {
            "scripts/place195_graph_path_baseline.py": sha256_file(Path(__file__))
        },
        "git": git_state(),
        "package_versions": package_versions(),
    }
    decisions_path = output_dir / "decisions.md"
    write_decisions(decisions_path, summary)
    write_receipt(receipt_path, summary)
    summary["artifact_hashes"][artifact_key(decisions_path)] = sha256_file(decisions_path)
    summary["artifact_hashes"][artifact_key(receipt_path)] = sha256_file(receipt_path)
    write_json(output_dir / "graph_path_baseline_summary.json", summary)
    return summary


def write_decisions(path: Path, summary: Mapping[str, Any]) -> None:
    lines = [
        "# Graph-path baseline decisions",
        "",
        f"Created UTC: {summary['created_utc']}",
        "",
        "Status: exploratory support audit plus condition-matched pseudopop baseline; not H1 evidence.",
        "",
        "## Decisions",
        "",
        "- Locked test split was not used.",
        "- Current timeout trials were dropped.",
        "- Endpoint-labelled rows use success_after_success.",
        "- Fine graph uses the pinned 1,344-node 4-neighbor centroid geometry.",
        "- Route family is exploratory fixed 5x5 graph-node signature; unsupported signatures collapse to __other_within_start_goal__.",
        "- V5 assembles condition-matched pseudopopulation rows instead of a source_trial x 195 matrix.",
        "- Missing cells remain masked; no cell-value imputation is used in the V5 neural distance.",
        "- Nearest-centroid classifier is constrained within start-goal at prediction time and uses overlapping observed cells only.",
        "",
        "## Commands",
        "",
        "```sh",
        summary["commands"]["test"],
        summary["commands"]["run"],
        "# post-run: " + summary["commands"]["post_run_validation"],
        "```",
        "",
        "## Validation metrics",
        "",
        "```json",
        json.dumps(summary["validation"], indent=2, sort_keys=True),
        "```",
        "",
        "## Claim ceiling",
        "",
        "This run can support only exploratory feasibility statements. It does not verify marker semantics, simultaneity, route-family biology, or H1.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_receipt(path: Path, summary: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# place195 graph-path baseline receipt",
        "",
        f"Date: {datetime.now(UTC).date().isoformat()}",
        f"Status: {summary['scientific_status']}",
        "",
        "## Inputs",
        "",
        f"- import dir: `{summary['import_dir']}`",
        f"- split dir: `{summary['split_dir']}`",
        f"- geometry: `{summary['geometry']}`",
        f"- output dir: `{summary['output_dir']}`",
        "",
        "## Graph/path rule",
        "",
        f"- graph schema: `{summary['graph']['schema']}`",
        f"- script graph hash: `{summary['graph']['script_primary_graph_hash']}`",
        f"- pinned receipt graph hash: `{summary['graph']['pinned_primary_graph_hash_from_receipt']}`",
        f"- mapping tolerance: `{summary['graph']['mapping_tolerance']}`",
        "- no interpolation; split at invalid/unmapped and nonadjacent transitions; collapse repeats.",
        "- exploratory route family: fixed 5x5 graph-node signature.",
        "",
        "## Main counts",
        "",
        "```json",
        json.dumps(summary["counts"], indent=2, sort_keys=True),
        "```",
        "",
        "## Commands",
        "",
        "```sh",
        summary["commands"]["test"],
        summary["commands"]["run"],
        "# post-run: " + summary["commands"]["post_run_validation"],
        "```",
        "",
        "## Validation",
        "",
        "```json",
        json.dumps(summary["validation"], indent=2, sort_keys=True),
        "```",
        "",
        "## Decision log",
        "",
        "- V5 replaces the trial-wise imputed baseline with condition-matched pseudopopulation rows.",
        "- Missing cells stay masked; the neural distance uses overlapping observed cells only.",
        "- This remains a cross-session pseudopopulation, not a simultaneous 195-cell population.",
        "- Marker semantics and simultaneous-population metadata remain unverified.",
        "- Locked test is still untouched for final evaluation.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    run_parser = subparsers.add_parser("run")
    run_parser.add_argument("--import-dir", type=Path, default=DEFAULT_IMPORT_DIR)
    run_parser.add_argument("--split-dir", type=Path, default=DEFAULT_SPLIT_DIR)
    run_parser.add_argument("--geometry", type=Path, default=DEFAULT_GEOMETRY)
    run_parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    run_parser.add_argument("--receipt", type=Path, default=DEFAULT_RECEIPT)
    run_parser.add_argument("--min-train", type=int, default=5)
    run_parser.add_argument("--min-validation", type=int, default=2)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    if args.command == "run":
        summary = run_audit(
            args.import_dir,
            args.split_dir,
            args.geometry,
            args.output_dir,
            args.receipt,
            args.min_train,
            args.min_validation,
        )
        print(
            json.dumps(
                {
                    "status": summary["status"],
                    "output_dir": summary["output_dir"],
                    "validation": summary["validation"],
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 0
    raise ValueError(args.command)


if __name__ == "__main__":
    raise SystemExit(main())
