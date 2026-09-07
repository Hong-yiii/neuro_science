#!/usr/bin/env python3
"""V6 split-safe geometry/path/support audit for place195.

This is behavior/support construction only. It freezes a small static
four-pillar region/corridor map before reading train/validation behavior, maps
observed Unity paths without interpolating gaps, then audits component support
and source/cell membership without fitting neural values.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import math
import shlex
import sys
from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, TextIO

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle

from docs.cebra_pilot.implementation.contracts import MazeGraph
from scripts.import_place195_sessions import (
    DEFAULT_OUTPUT_PARENT,
    ROOT,
    git_state,
    package_versions,
    sha256_file,
    validate_output_dir,
)
from scripts.place195_split_and_behavior_audit import write_csv, write_json
from scripts.place195_split_filtered_access import SplitFilteredAccess

DEFAULT_IMPORT_DIR = DEFAULT_OUTPUT_PARENT / "place195-all-sessions-20260830-v4"
DEFAULT_SPLIT_DIR = DEFAULT_OUTPUT_PARENT / "place195-splits-20260830-v3"
DEFAULT_GEOMETRY = ROOT / "docs/geometry/maze_mesh_centroids_1344.txt"
DEFAULT_OUTPUT_DIR = (
    DEFAULT_OUTPUT_PARENT
    / "place195-v6-v9-autoresearch-20260906"
    / "v6-reset-graph-support-audit"
)

SCIENTIFIC_STATUS = "exploratory_v6_behavior_support_audit_not_h1_evidence"
GRAPH_SCHEMA = "v6_static_four_pillar_9node_12corridor_v1"
GEOMETRY_SHA256 = "479f0df501e92e167206248eff2d0a44ba5f26cd62cfcc879dcaad979d7a7e66"
DOCUMENTED_FINE_PRIMARY_HASH = (
    "1e7804c5d2167dcd8709a9760d8917034cb60e36e936229fad9056b1dae0f9ad"
)
V5_SCRIPT_FINE_PRIMARY_HASH = (
    "f83908e027012e49f1be2396bb0f7aeb514b807c43b6e703625a40647a3738a0"
)
DOCUMENTED_EDGE_ONLY_HASH = (
    "ab31ee91f615bd4165282e8dd9ab2c4298a4f5285cb76fd3c4aeea38096a4ebb"
)
GRID_STEP = 0.625
OUTER_MIN = -12.5
OUTER_MAX = 12.5
MACRO_STEP = 5.0
UNKNOWN = "unknown"
MIN_TRAIN_PER_COMPONENT_CLASS = 8
MIN_VALIDATION_PER_COMPONENT_CLASS = 3
REQUIRED_PANEL_CONDITIONS = (
    "train|present",
    "train|absent",
    "validation|present",
    "validation|absent",
)

X_BANDS = (
    ("L", OUTER_MIN, -7.5, "node"),
    ("LC", -7.5, -2.5, "connector"),
    ("C", -2.5, 2.5, "node"),
    ("CR", 2.5, 7.5, "connector"),
    ("R", 7.5, OUTER_MAX, "node"),
)
Y_BANDS = (
    ("B", OUTER_MIN, -7.5, "node"),
    ("BM", -7.5, -2.5, "connector"),
    ("M", -2.5, 2.5, "node"),
    ("MT", 2.5, 7.5, "connector"),
    ("T", 7.5, OUTER_MAX, "node"),
)
NODE_X_ORDER = ("L", "C", "R")
NODE_Y_ORDER = ("B", "M", "T")


@dataclass(frozen=True)
class TrialLabel:
    session_id: str
    source_trial_id: str
    split: str
    trial_index: int
    start: str
    goal: str
    endpoint_pair: str
    qc_flags: str


@dataclass(frozen=True)
class Region:
    region_id: str
    region_type: str
    x_band: str
    y_band: str
    x_min: float
    x_max: float
    y_min: float
    y_max: float
    center_x: float
    center_y: float
    corridor_id: str = ""
    from_node: str = ""
    to_node: str = ""
    axis: str = ""
    length: float = 0.0


@dataclass(frozen=True)
class SampleMap:
    navigation_sample: int
    unity_time_since_nav_onset_s: str
    x: float
    y: float
    heading: str
    region_id: str
    region_type: str
    corridor_id: str
    progress: float | None
    lateral_offset: float | None
    map_error: float | None
    unknown_reason: str
    directed_component_id: str = ""
    corridor_direction: str = ""
    run_index: int = -1


@dataclass(frozen=True)
class Run:
    run_index: int
    region_id: str
    region_type: str
    corridor_id: str
    samples: tuple[SampleMap, ...]
    progress_start: float | None
    progress_end: float | None
    reversal_count: int
    directed_component_id: str = ""
    corridor_direction: str = ""
    direction_source: str = ""
    is_middle: bool = False


@dataclass
class PathProducts:
    sample_rows: list[dict[str, Any]] = field(default_factory=list)
    trial_rows: list[dict[str, Any]] = field(default_factory=list)
    dwell_rows: list[dict[str, Any]] = field(default_factory=list)
    traversal_rows: list[dict[str, Any]] = field(default_factory=list)
    motif_rows: list[dict[str, Any]] = field(default_factory=list)
    grid_diagnostics: Counter[tuple[str, int, int, str]] = field(default_factory=Counter)
    raw_plot_sources: set[str] = field(default_factory=set)
    raw_paths_for_plot: dict[str, list[tuple[float, float]]] = field(default_factory=dict)


@dataclass(frozen=True)
class ComponentTrial:
    source_trial_id: str
    session_id: str
    split: str
    endpoint_pair: str
    complete: bool
    middle_components: frozenset[str]
    motifs: frozenset[str]
    route_signature: str
    middle_component_direction_sources: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class SelectedCohort:
    component_id: str
    component_type: str
    endpoint_pair: str
    status: str
    reason: str


class JsonlLog:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def write(self, event: str, **payload: Any) -> None:
        row = {"time_utc": datetime.now(UTC).isoformat(), "event": event} | payload
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(_jsonable(row), sort_keys=True) + "\n")


def canonical_hash(payload: Mapping[str, Any]) -> str:
    return hashlib.sha256(
        json.dumps(_jsonable(payload), sort_keys=True, separators=(",", ":")).encode(
            "utf-8"
        )
    ).hexdigest()


def _jsonable(value: Any) -> Any:
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, Mapping):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set, frozenset)):
        return [_jsonable(v) for v in value]
    return value


def ensure_output_dir(output_dir: Path, input_dir: Path) -> None:
    validate_output_dir(output_dir, input_dir)
    if output_dir.exists():
        unexpected = [path.name for path in output_dir.iterdir() if path.name != "logs"]
        if unexpected:
            raise ValueError(
                f"output_dir already contains V6 artifacts: {output_dir} {unexpected}"
            )
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "logs").mkdir(exist_ok=True)


def parse_centroids(path: Path) -> dict[int, tuple[float, float]]:
    geometry_sha = sha256_file(path)
    if geometry_sha != GEOMETRY_SHA256:
        raise ValueError(f"geometry hash mismatch: {geometry_sha}")
    centroids: dict[int, tuple[float, float]] = {}
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        text = line.strip()
        if not text:
            continue
        x_text, y_text = text.strip("()").split(",")
        centroids[line_number] = (round(float(x_text), 4), round(float(y_text), 4))
    if len(centroids) != 1344:
        raise ValueError(f"expected 1344 centroids, got {len(centroids)}")
    return centroids


def fine_graph_facts(geometry: Path) -> dict[str, Any]:
    centroids = parse_centroids(geometry)
    coord_to_node = {coord: node for node, coord in centroids.items()}
    directed_edges: list[tuple[int, int]] = []
    for node, (x, y) in centroids.items():
        for dx, dy in ((GRID_STEP, 0.0), (-GRID_STEP, 0.0), (0.0, GRID_STEP), (0.0, -GRID_STEP)):
            neighbor = coord_to_node.get((round(x + dx, 4), round(y + dy, 4)))
            if neighbor is not None:
                directed_edges.append((node, neighbor))
    undirected = {(min(a, b), max(a, b)) for a, b in directed_edges}
    degree = Counter()
    for a, b in undirected:
        degree[a] += 1
        degree[b] += 1
    script_payload = {
        "schema": "maze_graph_1344_4neighbor_v1",
        "geometry_file": "docs/geometry/maze_mesh_centroids_1344.txt",
        "geometry_sha256": GEOMETRY_SHA256,
        "node_id": "1-based line number in centroid file",
        "coordinate_units": "Unity axis units",
        "adjacency_rule": "directed cardinal 4-neighbor edge when centroids differ by exactly 0.625 on one axis and 0 on the other",
        "grid_step": "0.625",
        "nodes": [
            {"id": node, "axis1": f"{x:g}", "axis2": f"{y:g}"}
            for node, (x, y) in sorted(centroids.items())
        ],
        "directed_edges": [[a, b] for a, b in sorted(directed_edges)],
    }
    current_typed_edge_only = MazeGraph(tuple(directed_edges)).sha256
    legacy_bare_int_edge_payload = {
        "directed_edges": [[a, b] for a, b in sorted(directed_edges)]
    }
    legacy_bare_int_edge_hash = canonical_hash(legacy_bare_int_edge_payload)
    script_hash = canonical_hash(script_payload)
    return {
        "geometry_sha256": GEOMETRY_SHA256,
        "nodes": len(centroids),
        "undirected_edges": len(undirected),
        "directed_edges": len(directed_edges),
        "degree_counts": dict(sorted(Counter(degree.values()).items())),
        "documented_primary_hash": DOCUMENTED_FINE_PRIMARY_HASH,
        "v5_script_style_primary_hash_computed": script_hash,
        "v5_script_style_primary_hash_expected": V5_SCRIPT_FINE_PRIMARY_HASH,
        "v5_script_style_primary_hash_matches_expected": script_hash == V5_SCRIPT_FINE_PRIMARY_HASH,
        "legacy_bare_int_numeric_sorted_edge_hash_computed": legacy_bare_int_edge_hash,
        "legacy_bare_int_numeric_sorted_edge_hash_expected": DOCUMENTED_EDGE_ONLY_HASH,
        "legacy_bare_int_numeric_sorted_edge_hash_matches_expected": legacy_bare_int_edge_hash
        == DOCUMENTED_EDGE_ONLY_HASH,
        "current_typed_mazegraph_edge_only_hash_computed": current_typed_edge_only,
        "current_typed_mazegraph_edge_only_hash_expected": "46f113070ca5f3b94c06c0b2943ef9d011b8dd432d8d6956481f8b6de36ccda3",
        "current_typed_mazegraph_edge_only_hash_matches_expected": current_typed_edge_only
        == "46f113070ca5f3b94c06c0b2943ef9d011b8dd432d8d6956481f8b6de36ccda3",
        "hash_reconciliation": "documented ab31... is the legacy bare-int numeric-sorted compact JSON edge-list hash; current MazeGraph.sha256 is the typed-node-token contract and gives 46f...; both are serialized from the same generated directed edge list, recorded here explicitly instead of treating counts alone as topology proof",
    }


def build_regions() -> tuple[dict[str, Region], list[Region], list[dict[str, str]]]:
    regions: dict[str, Region] = {}
    corridor_regions: list[Region] = []
    directed_components: list[dict[str, str]] = []
    for x_band, x0, x1, x_kind in X_BANDS:
        for y_band, y0, y1, y_kind in Y_BANDS:
            if x_kind == "connector" and y_kind == "connector":
                continue
            cx = (x0 + x1) / 2.0
            cy = (y0 + y1) / 2.0
            if x_kind == "node" and y_kind == "node":
                region_id = node_id(x_band, y_band)
                regions[region_id] = Region(
                    region_id, "node", x_band, y_band, x0, x1, y0, y1, cx, cy
                )
                continue
            if x_kind == "connector":
                left_node, right_node = adjacent_x_nodes(x_band)
                from_node = node_id(left_node, y_band)
                to_node = node_id(right_node, y_band)
                corridor_id = f"E_H_{y_band}_{left_node}_{right_node}"
                region_id = corridor_id
                axis = "x"
            else:
                low_node, high_node = adjacent_y_nodes(y_band)
                from_node = node_id(x_band, low_node)
                to_node = node_id(x_band, high_node)
                corridor_id = f"E_V_{x_band}_{low_node}_{high_node}"
                region_id = corridor_id
                axis = "y"
            region = Region(
                region_id,
                "corridor",
                x_band,
                y_band,
                x0,
                x1,
                y0,
                y1,
                cx,
                cy,
                corridor_id=corridor_id,
                from_node=from_node,
                to_node=to_node,
                axis=axis,
                length=MACRO_STEP,
            )
            regions[region_id] = region
            corridor_regions.append(region)
            directed_components.append(
                {
                    "component_id": directed_id(from_node, to_node),
                    "component_type": "directed_middle_corridor",
                    "corridor_id": corridor_id,
                    "from_node": from_node,
                    "to_node": to_node,
                }
            )
            directed_components.append(
                {
                    "component_id": directed_id(to_node, from_node),
                    "component_type": "directed_middle_corridor",
                    "corridor_id": corridor_id,
                    "from_node": to_node,
                    "to_node": from_node,
                }
            )
    return regions, corridor_regions, directed_components


def node_id(x_band: str, y_band: str) -> str:
    return f"N_{x_band}_{y_band}"


def directed_id(from_node: str, to_node: str) -> str:
    return f"D_{from_node}__{to_node}"


def motif_id(incoming: str, node: str, outgoing: str) -> str:
    return f"M_{incoming}__{node}__{outgoing}"


def adjacent_x_nodes(connector: str) -> tuple[str, str]:
    if connector == "LC":
        return "L", "C"
    if connector == "CR":
        return "C", "R"
    raise ValueError(connector)


def adjacent_y_nodes(connector: str) -> tuple[str, str]:
    if connector == "BM":
        return "B", "M"
    if connector == "MT":
        return "M", "T"
    raise ValueError(connector)


def region_payload(regions: Mapping[str, Region], components: Sequence[Mapping[str, str]]) -> dict[str, Any]:
    return {
        "schema": GRAPH_SCHEMA,
        "derivation": "static four-pillar macro partition from authoritative centroids and upstream wall/pillar constants; no behavior-derived thresholds",
        "outer_bounds": [OUTER_MIN, OUTER_MAX, OUTER_MIN, OUTER_MAX],
        "pillar_bounds": [
            [-7.5, -2.5, -7.5, -2.5],
            [2.5, 7.5, -7.5, -2.5],
            [2.5, 7.5, 2.5, 7.5],
            [-7.5, -2.5, 2.5, 7.5],
        ],
        "regions": [region_to_row(region) for region in sorted(regions.values(), key=lambda r: r.region_id)],
        "directed_components": list(components),
    }


def region_to_row(region: Region) -> dict[str, Any]:
    return {
        "region_id": region.region_id,
        "region_type": region.region_type,
        "x_band": region.x_band,
        "y_band": region.y_band,
        "x_min": region.x_min,
        "x_max": region.x_max,
        "y_min": region.y_min,
        "y_max": region.y_max,
        "center_x": region.center_x,
        "center_y": region.center_y,
        "corridor_id": region.corridor_id,
        "from_node": region.from_node,
        "to_node": region.to_node,
        "axis": region.axis,
        "centerline_length": region.length,
    }


def write_frozen_config(
    output_dir: Path,
    import_dir: Path,
    split_dir: Path,
    geometry: Path,
    access: SplitFilteredAccess,
    regions: Mapping[str, Region],
    components: Sequence[Mapping[str, str]],
    min_train_per_class: int,
    min_validation_per_class: int,
) -> dict[str, Any]:
    v6a = output_dir / "v6a_geometry_mapping"
    v6a.mkdir(exist_ok=True)
    fine_facts = fine_graph_facts(geometry)
    payload = region_payload(regions, components)
    static_hash = canonical_hash(payload)
    headers = {table: list(access.table_header(table)) for table in ("trials", "path_samples", "cue_counts", "cue_spike_events")}
    config = {
        "created_utc_before_behavior_inspection": datetime.now(UTC).isoformat(),
        "scientific_status": SCIENTIFIC_STATUS,
        "claim_ceiling": "exploratory behavior/support audit after holdout exposure reset; original test is not pristine and is not evaluated",
        "import_dir": str(import_dir),
        "split_dir": str(split_dir),
        "split_hash": access.split_hash,
        "allowed_splits": list(access.allowed_splits),
        "locked_test_policy": "test rows may be counted as skipped by the guard but never yielded or evaluated",
        "geometry_file": str(geometry),
        "input_hashes": {
            "geometry": sha256_file(geometry),
            "source_trial_splits.csv": sha256_file(split_dir / "source_trial_splits.csv"),
            "trials.csv": sha256_file(import_dir / "trials.csv"),
            "path_samples.csv.gz": sha256_file(import_dir / "path_samples.csv.gz"),
            "cue_counts.csv.gz": sha256_file(import_dir / "cue_counts.csv.gz"),
            "cue_spike_events.csv.gz": sha256_file(import_dir / "cue_spike_events.csv.gz"),
        },
        "table_headers_only_preread": headers,
        "fine_graph_reconciliation": fine_facts,
        "static_region_corridor_graph_hash": static_hash,
        "static_region_corridor_graph": payload,
        "mapping_rule": {
            "coordinate_source": "Unity position_axis1/position_axis2 from path_samples after split guard",
            "macro_partition": "5x5 cells defined by outer wall and four 5x5 pillar bounds",
            "node_regions": "9 lane-intersection/plaza cells at L/C/R x B/M/T",
            "corridor_regions": "12 rectangular connector cells between neighboring node regions",
            "unknown_policy": "outside outer bounds or inside pillar macro cells is unknown; unknowns break route coverage",
            "direction_policy": "directed corridor labels require adjacent node evidence or monotonic progress in the observed corridor run",
            "gap_policy": "no shortest-path interpolation or bridge edges; incomplete/unknown paths are not labelled absent",
        },
        "behavior_selection_rule_declared_before_neural_access": {
            "candidate_type": "directed_middle_corridor",
            "endpoint_scope": "within one inferred start->goal endpoint pair",
            "strict_thresholds": {
                "min_train_trials_per_class": min_train_per_class,
                "min_validation_trials_per_class": min_validation_per_class,
            },
            "rank_order": [
                "strictly thresholded present and absent classes in train and validation",
                "larger minimum class count across train/validation",
                "larger validation minimum class count",
                "more within-session both-class support across splits",
                "larger total behavior support",
                "lexicographic endpoint_pair then component_id",
            ],
            "neural_value_use": "none; cue tables may be used later only for source/cell membership after this behavior-only selection",
        },
        "rejected_alternatives_preserved": [
            "degree-contracting the 1344-node floor grid: rejected because broad floor grid degrees are spatial mesh facts, not decision points",
            "V5 coarse5 signatures as V6 graph: retained only as historical comparison, not a reviewed region/corridor map",
            "shortest-path filling across unmapped or skipped samples: rejected because invented bridges must not masquerade as observed behavior",
            "all195 blind imputation: rejected for V6 support gate; missing cells remain missing membership",
        ],
        "git": git_state(),
        "package_versions": package_versions(),
    }
    write_json(v6a / "preread_frozen_graph_config.json", config)
    write_markdown_config(v6a / "preread_frozen_graph_config.md", config)
    return config


def write_hash_reconciliation_report(output_dir: Path, config: Mapping[str, Any]) -> Path:
    path = output_dir / "v6a_geometry_mapping" / "static_hash_reconciliation.md"
    facts = config["fine_graph_reconciliation"]
    lines = [
        "# V6 static/fine graph hash reconciliation",
        "",
        "This report resolves the fine-graph edge-only hash mismatch without rerunning mapping.",
        "",
        "## Fine 1,344-node graph hashes",
        "",
        f"- Documented primary hash: `{facts['documented_primary_hash']}`",
        f"- V5 script-style primary hash: `{facts['v5_script_style_primary_hash_computed']}` (matches expected: `{facts['v5_script_style_primary_hash_matches_expected']}`)",
        f"- Legacy bare-int numeric-sorted edge hash: `{facts['legacy_bare_int_numeric_sorted_edge_hash_computed']}` (matches documented ab31: `{facts['legacy_bare_int_numeric_sorted_edge_hash_matches_expected']}`)",
        f"- Current typed `MazeGraph.sha256`: `{facts['current_typed_mazegraph_edge_only_hash_computed']}` (matches expected 46f: `{facts['current_typed_mazegraph_edge_only_hash_matches_expected']}`)",
        "",
        "The `ab31...` hash is compact JSON over `{'directed_edges': [[1, 2], ...]}` with bare integer edges sorted numerically. The current `MazeGraph` contract serializes typed node-token dictionaries and sorts by that canonical JSON, producing `46f...`. Both are emitted from the same generated directed edge list; counts alone are not used as proof of identical topology.",
        "",
        "## V6 static region/corridor graph",
        "",
        f"- V6 static graph hash: `{config['static_region_corridor_graph_hash']}`",
        "- Schema: 9 node/plaza regions + 12 corridor regions from the four-pillar geometry.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def write_markdown_config(path: Path, config: Mapping[str, Any]) -> None:
    lines = [
        "# V6 preread frozen graph config",
        "",
        f"Created before behavior inspection: `{config['created_utc_before_behavior_inspection']}`",
        "",
        "This stage is exploratory and behavior/support-only. It discloses the holdout exposure reset and does not evaluate test.",
        "",
        "## Static graph",
        "",
        f"- Schema: `{GRAPH_SCHEMA}`",
        f"- Static graph hash: `{config['static_region_corridor_graph_hash']}`",
        "- Regions: 9 node/plaza rectangles + 12 corridor rectangles from the four-pillar geometry.",
        "- No degree contraction of the 1344-node floor grid.",
        "- No shortest-path gap invention.",
        "",
        "## Selection rule declared before cue membership access",
        "",
        "Choose one directed middle corridor within one endpoint pair using behavior counts only: both present and absent classes in train and validation, then max-min class support, validation support, within-session support, total support, lexicographic tie-break.",
        "",
        "## Hash reconciliation",
        "",
        "```json",
        json.dumps(config["fine_graph_reconciliation"], indent=2, sort_keys=True),
        "```",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def band_for(value: float, bands: Sequence[tuple[str, float, float, str]]) -> tuple[str, float, float, str] | None:
    eps = 1e-9
    if value < OUTER_MIN - eps or value > OUTER_MAX + eps:
        return None
    for index, band in enumerate(bands):
        _name, lo, hi, _kind = band
        if lo - eps <= value < hi - eps or (index == len(bands) - 1 and value <= hi + eps):
            return band
    return None


def map_sample(row: Mapping[str, str], regions: Mapping[str, Region]) -> SampleMap:
    x = float(row["position_axis1"])
    y = float(row["position_axis2"])
    nav_sample = int(row["navigation_sample"])
    heading = row.get("heading", "")
    time = row.get("unity_time_since_nav_onset_s", "")
    x_band = band_for(x, X_BANDS)
    y_band = band_for(y, Y_BANDS)
    if x_band is None or y_band is None:
        return SampleMap(nav_sample, time, x, y, heading, UNKNOWN, UNKNOWN, "", None, None, None, "outside_outer_bounds")
    xb, _x0, _x1, x_kind = x_band
    yb, _y0, _y1, y_kind = y_band
    if x_kind == "connector" and y_kind == "connector":
        return SampleMap(nav_sample, time, x, y, heading, UNKNOWN, UNKNOWN, "", None, None, None, "pillar_macro_cell")
    if x_kind == "node" and y_kind == "node":
        region = regions[node_id(xb, yb)]
        map_error = math.hypot(x - region.center_x, y - region.center_y)
        return SampleMap(nav_sample, time, x, y, heading, region.region_id, "node", "", None, None, map_error, "")
    if x_kind == "connector":
        left, right = adjacent_x_nodes(xb)
        region = regions[f"E_H_{yb}_{left}_{right}"]
        progress = (x - region.x_min) / (region.x_max - region.x_min)
        lateral = abs(y - region.center_y)
    else:
        low, high = adjacent_y_nodes(yb)
        region = regions[f"E_V_{xb}_{low}_{high}"]
        progress = (y - region.y_min) / (region.y_max - region.y_min)
        lateral = abs(x - region.center_x)
    return SampleMap(nav_sample, time, x, y, heading, region.region_id, "corridor", region.corridor_id, progress, lateral, lateral, "")


def labels_from_trials(access: SplitFilteredAccess) -> dict[str, TrialLabel]:
    trial_by_source = {row["source_trial_id"]: row for row in access.iter_trials()}
    labels: dict[str, TrialLabel] = {}
    for source, row in trial_by_source.items():
        if row.get("outcome") != "success":
            continue
        previous = row.get("previous_source_trial_id", "")
        previous_row = trial_by_source.get(previous)
        if not previous_row or previous_row.get("outcome") != "success":
            continue
        start = row.get("inferred_start_id_from_previous_marker", "").replace("marker_", "")
        goal = row.get("marker_minor_digit", "")
        if not start or not goal:
            continue
        labels[source] = TrialLabel(
            session_id=row["session_id"],
            source_trial_id=source,
            split=row["split"],
            trial_index=int(row["trial_index"]),
            start=start,
            goal=goal,
            endpoint_pair=f"{start}->{goal}",
            qc_flags=row.get("qc_flags", ""),
        )
    return labels


def build_path_products(
    access: SplitFilteredAccess,
    labels: Mapping[str, TrialLabel],
    regions: Mapping[str, Region],
    output_dir: Path,
) -> tuple[PathProducts, list[ComponentTrial]]:
    products = PathProducts()
    plot_source_order = sorted(
        labels.values(), key=lambda label: (label.split != "validation", label.endpoint_pair, label.source_trial_id)
    )[:12]
    products.raw_plot_sources = {label.source_trial_id for label in plot_source_order}

    v6a = output_dir / "v6a_geometry_mapping"
    sample_path = v6a / "mapped_path_samples_train_validation_success_after_success.csv.gz"
    sample_fields = (
        "session_id",
        "source_trial_id",
        "split",
        "endpoint_pair",
        "navigation_sample",
        "unity_time_since_nav_onset_s",
        "position_axis1",
        "position_axis2",
        "heading",
        "region_id",
        "region_type",
        "corridor_id",
        "directed_component_id",
        "corridor_direction",
        "progress",
        "lateral_offset",
        "map_error",
        "unknown_reason",
        "run_index",
    )
    component_trials: list[ComponentTrial] = []
    current_source = ""
    current_samples: list[SampleMap] = []

    def flush(handle: TextIO) -> None:
        nonlocal current_source, current_samples
        if not current_source:
            return
        label = labels[current_source]
        trial_component = finalize_trial(label, current_samples, regions, products, handle, sample_fields)
        component_trials.append(trial_component)
        if current_source in products.raw_plot_sources:
            products.raw_paths_for_plot[current_source] = [(sample.x, sample.y) for sample in current_samples]
        current_source = ""
        current_samples = []

    with gzip.open(sample_path, "wt", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=sample_fields)
        writer.writeheader()
        for row in access.iter_path_samples():
            source = row["source_trial_id"]
            if source not in labels:
                continue
            if current_source and source != current_source:
                flush(handle)
            if not current_source:
                current_source = source
            current_samples.append(map_sample(row, regions))
        flush(handle)
    return products, component_trials


def finalize_trial(
    label: TrialLabel,
    samples: Sequence[SampleMap],
    regions: Mapping[str, Region],
    products: PathProducts,
    sample_handle: TextIO,
    sample_fields: Sequence[str],
) -> ComponentTrial:
    runs = assign_runs(samples, regions)
    known_runs = [run for run in runs if run.region_type != UNKNOWN]
    corridor_runs = [run for run in known_runs if run.region_type == "corridor"]
    directed_sequence = [run.directed_component_id for run in corridor_runs if run.directed_component_id]
    unknown_direction_count = sum(1 for run in corridor_runs if not run.directed_component_id)
    unknown_sample_count = sum(1 for sample in samples if sample.region_type == UNKNOWN)
    unknown_gap_count = count_unknown_gaps(samples)
    complete = bool(samples) and unknown_sample_count == 0 and unknown_direction_count == 0
    middle_runs = corridor_runs[1:-1] if complete and len(corridor_runs) >= 3 else []
    middle_components = frozenset(
        run.directed_component_id for run in middle_runs if run.directed_component_id
    )
    middle_direction_sources = tuple(
        (run.directed_component_id, run.direction_source)
        for run in middle_runs
        if run.directed_component_id
    )
    motifs = frozenset(extract_motifs(runs)) if complete else frozenset()
    route_signature = ">".join(directed_sequence) if complete else "__incomplete_or_unknown__"

    row_by_run = {run.run_index: run for run in runs}
    writer = csv.DictWriter(sample_handle, fieldnames=sample_fields)
    for run in runs:
        for sample in run.samples:
            out = sample_row(label, sample, row_by_run.get(sample.run_index))
            writer.writerow({field: csv_value(out.get(field, "")) for field in sample_fields})

    for run in known_runs:
        products.dwell_rows.append(dwell_row(label, run))
    for run in corridor_runs:
        products.traversal_rows.append(traversal_row(label, run, route_signature, complete))
    for motif in motifs:
        products.motif_rows.append(
            {
                "session_id": label.session_id,
                "source_trial_id": label.source_trial_id,
                "split": label.split,
                "endpoint_pair": label.endpoint_pair,
                "motif_id": motif,
                "route_signature": route_signature,
            }
        )
    update_grid_fragmentation(samples, products.grid_diagnostics)
    products.trial_rows.append(
        {
            "session_id": label.session_id,
            "source_trial_id": label.source_trial_id,
            "split": label.split,
            "trial_index": label.trial_index,
            "start": label.start,
            "goal": label.goal,
            "endpoint_pair": label.endpoint_pair,
            "qc_flags": label.qc_flags,
            "raw_sample_count": len(samples),
            "known_sample_count": len(samples) - unknown_sample_count,
            "unknown_sample_count": unknown_sample_count,
            "unknown_sample_fraction": unknown_sample_count / len(samples) if samples else 1.0,
            "unknown_gap_count": unknown_gap_count,
            "region_run_count": len(runs),
            "node_run_count": sum(1 for run in runs if run.region_type == "node"),
            "corridor_run_count": len(corridor_runs),
            "known_directed_corridor_count": len(directed_sequence),
            "unknown_direction_corridor_count": unknown_direction_count,
            "middle_directed_component_count": len(middle_components),
            "junction_motif_count": len(motifs),
            "corridor_reversal_count": sum(run.reversal_count for run in corridor_runs),
            "node_dwell_samples": sum(len(run.samples) for run in runs if run.region_type == "node"),
            "corridor_samples": sum(len(run.samples) for run in corridor_runs),
            "complete_directed_path_coverage": str(complete).lower(),
            "route_signature": route_signature,
            "middle_directed_components": ";".join(sorted(middle_components)),
            "junction_motifs": ";".join(sorted(motifs)),
            "absence_labels_allowed": str(complete).lower(),
        }
    )
    return ComponentTrial(
        source_trial_id=label.source_trial_id,
        session_id=label.session_id,
        split=label.split,
        endpoint_pair=label.endpoint_pair,
        complete=complete,
        middle_components=middle_components,
        motifs=motifs,
        route_signature=route_signature,
        middle_component_direction_sources=middle_direction_sources,
    )


def assign_runs(samples: Sequence[SampleMap], regions: Mapping[str, Region]) -> list[Run]:
    raw_runs: list[list[SampleMap]] = []
    for sample in samples:
        if not raw_runs or raw_runs[-1][-1].region_id != sample.region_id:
            raw_runs.append([sample])
        else:
            raw_runs[-1].append(sample)
    runs: list[Run] = []
    for idx, group in enumerate(raw_runs):
        progress_values = [sample.progress for sample in group if sample.progress is not None]
        reversal_count = count_reversals(progress_values)
        first = group[0]
        directed_component = ""
        direction = ""
        direction_source = ""
        if first.region_type == "corridor":
            region = regions[first.corridor_id]
            prev_node = nearest_node(raw_runs, idx, -1)
            next_node = nearest_node(raw_runs, idx, 1)
            directed_component, direction, direction_source = infer_direction(
                region, prev_node, next_node, progress_values
            )
        runs.append(
            Run(
                run_index=idx,
                region_id=first.region_id,
                region_type=first.region_type,
                corridor_id=first.corridor_id,
                samples=tuple(
                    SampleMap(
                        sample.navigation_sample,
                        sample.unity_time_since_nav_onset_s,
                        sample.x,
                        sample.y,
                        sample.heading,
                        sample.region_id,
                        sample.region_type,
                        sample.corridor_id,
                        sample.progress,
                        sample.lateral_offset,
                        sample.map_error,
                        sample.unknown_reason,
                        directed_component,
                        direction,
                        idx,
                    )
                    for sample in group
                ),
                progress_start=progress_values[0] if progress_values else None,
                progress_end=progress_values[-1] if progress_values else None,
                reversal_count=reversal_count,
                directed_component_id=directed_component,
                corridor_direction=direction,
                direction_source=direction_source,
            )
        )
    corridor_indices = [i for i, run in enumerate(runs) if run.region_type == "corridor"]
    middle_indices = set(corridor_indices[1:-1]) if len(corridor_indices) >= 3 else set()
    return [replace_middle(run, run_index in middle_indices) for run_index, run in enumerate(runs)]


def replace_middle(run: Run, is_middle: bool) -> Run:
    return Run(
        run.run_index,
        run.region_id,
        run.region_type,
        run.corridor_id,
        run.samples,
        run.progress_start,
        run.progress_end,
        run.reversal_count,
        run.directed_component_id,
        run.corridor_direction,
        run.direction_source,
        is_middle,
    )


def nearest_node(raw_runs: Sequence[Sequence[SampleMap]], index: int, step: int) -> str:
    i = index + step
    while 0 <= i < len(raw_runs):
        sample = raw_runs[i][0]
        if sample.region_type == UNKNOWN:
            return ""
        if sample.region_type == "node":
            return sample.region_id
        i += step
    return ""


def infer_direction(
    region: Region,
    prev_node: str,
    next_node: str,
    progress_values: Sequence[float | None],
) -> tuple[str, str, str]:
    if prev_node == region.from_node and next_node == region.to_node:
        return directed_id(region.from_node, region.to_node), "forward", "adjacent_nodes"
    if prev_node == region.to_node and next_node == region.from_node:
        return directed_id(region.to_node, region.from_node), "reverse", "adjacent_nodes"
    valid_progress = [p for p in progress_values if p is not None]
    if len(valid_progress) >= 2:
        delta = valid_progress[-1] - valid_progress[0]
        if delta > 0.05:
            return directed_id(region.from_node, region.to_node), "forward", "progress"
        if delta < -0.05:
            return directed_id(region.to_node, region.from_node), "reverse", "progress"
    if prev_node == region.from_node or next_node == region.to_node:
        return directed_id(region.from_node, region.to_node), "forward", "one_adjacent_node"
    if prev_node == region.to_node or next_node == region.from_node:
        return directed_id(region.to_node, region.from_node), "reverse", "one_adjacent_node"
    return "", "unknown", "insufficient_observed_context"


def count_reversals(values: Sequence[float | None]) -> int:
    numeric = [value for value in values if value is not None]
    if len(numeric) < 3:
        return 0
    signs = []
    for left, right in zip(numeric, numeric[1:], strict=False):
        delta = right - left
        if abs(delta) > 0.02:
            signs.append(1 if delta > 0 else -1)
    return sum(1 for left, right in zip(signs, signs[1:], strict=False) if left != right)


def count_unknown_gaps(samples: Sequence[SampleMap]) -> int:
    gaps = 0
    in_gap = False
    for sample in samples:
        if sample.region_type == UNKNOWN:
            if not in_gap:
                gaps += 1
                in_gap = True
        else:
            in_gap = False
    return gaps


def extract_motifs(runs: Sequence[Run]) -> list[str]:
    motifs: list[str] = []
    for left, node, right in zip(runs, runs[1:], runs[2:], strict=False):
        if node.region_type != "node":
            continue
        if left.region_type != "corridor" or right.region_type != "corridor":
            continue
        if not left.directed_component_id or not right.directed_component_id:
            continue
        motifs.append(motif_id(left.directed_component_id, node.region_id, right.directed_component_id))
    return motifs


def sample_row(label: TrialLabel, sample: SampleMap, run: Run | None) -> dict[str, Any]:
    return {
        "session_id": label.session_id,
        "source_trial_id": label.source_trial_id,
        "split": label.split,
        "endpoint_pair": label.endpoint_pair,
        "navigation_sample": sample.navigation_sample,
        "unity_time_since_nav_onset_s": sample.unity_time_since_nav_onset_s,
        "position_axis1": sample.x,
        "position_axis2": sample.y,
        "heading": sample.heading,
        "region_id": sample.region_id,
        "region_type": sample.region_type,
        "corridor_id": sample.corridor_id,
        "directed_component_id": run.directed_component_id if run else "",
        "corridor_direction": run.corridor_direction if run else "",
        "progress": sample.progress,
        "lateral_offset": sample.lateral_offset,
        "map_error": sample.map_error,
        "unknown_reason": sample.unknown_reason,
        "run_index": sample.run_index,
    }


def dwell_row(label: TrialLabel, run: Run) -> dict[str, Any]:
    return {
        "session_id": label.session_id,
        "source_trial_id": label.source_trial_id,
        "split": label.split,
        "endpoint_pair": label.endpoint_pair,
        "region_id": run.region_id,
        "region_type": run.region_type,
        "corridor_id": run.corridor_id,
        "run_index": run.run_index,
        "first_navigation_sample": run.samples[0].navigation_sample,
        "last_navigation_sample": run.samples[-1].navigation_sample,
        "dwell_samples": len(run.samples),
    }


def traversal_row(label: TrialLabel, run: Run, route_signature: str, complete: bool) -> dict[str, Any]:
    return {
        "session_id": label.session_id,
        "source_trial_id": label.source_trial_id,
        "split": label.split,
        "endpoint_pair": label.endpoint_pair,
        "corridor_id": run.corridor_id,
        "directed_component_id": run.directed_component_id,
        "corridor_direction": run.corridor_direction,
        "direction_source": run.direction_source,
        "run_index": run.run_index,
        "first_navigation_sample": run.samples[0].navigation_sample,
        "last_navigation_sample": run.samples[-1].navigation_sample,
        "dwell_samples": len(run.samples),
        "progress_start": run.progress_start,
        "progress_end": run.progress_end,
        "progress_delta": (run.progress_end - run.progress_start) if run.progress_start is not None and run.progress_end is not None else "",
        "reversal_count_within_corridor": run.reversal_count,
        "is_middle_corridor": str(run.is_middle).lower(),
        "complete_directed_path_coverage": str(complete).lower(),
        "route_signature": route_signature,
    }


def update_grid_fragmentation(samples: Sequence[SampleMap], counter: Counter[tuple[str, int, int, str]]) -> None:
    prev: tuple[int, int] | None = None
    for sample in samples:
        if sample.region_type == UNKNOWN:
            prev = None
            continue
        gx = int(round((sample.x - OUTER_MIN) / GRID_STEP))
        gy = int(round((sample.y - OUTER_MIN) / GRID_STEP))
        if prev is None:
            prev = (gx, gy)
            continue
        dx = abs(gx - prev[0])
        dy = abs(gy - prev[1])
        if dx == 0 and dy == 0:
            category = "repeat_or_subcell"
        elif dx + dy == 1:
            category = "cardinal_adjacent"
        elif dx == 1 and dy == 1:
            category = "diagonal_one_cell"
        elif dx + dy > 1 and (dx == 0 or dy == 0):
            category = "axis_skip"
        else:
            category = "multi_axis_skip"
        crosses = "line_crosses_pillar" if line_crosses_pillar(prev, (gx, gy)) else "line_clear_or_unchecked"
        counter[(category, dx, dy, crosses)] += 1
        prev = (gx, gy)


def line_crosses_pillar(prev: tuple[int, int], current: tuple[int, int]) -> bool:
    x0 = OUTER_MIN + prev[0] * GRID_STEP
    y0 = OUTER_MIN + prev[1] * GRID_STEP
    x1 = OUTER_MIN + current[0] * GRID_STEP
    y1 = OUTER_MIN + current[1] * GRID_STEP
    for xmin, xmax, ymin, ymax in ((-7.5, -2.5, -7.5, -2.5), (2.5, 7.5, -7.5, -2.5), (2.5, 7.5, 2.5, 7.5), (-7.5, -2.5, 2.5, 7.5)):
        if segment_intersects_rect((x0, y0), (x1, y1), (xmin, xmax, ymin, ymax)):
            return True
    return False


def segment_intersects_rect(p0: tuple[float, float], p1: tuple[float, float], rect: tuple[float, float, float, float]) -> bool:
    xmin, xmax, ymin, ymax = rect
    if point_inside_rect(p0, rect) or point_inside_rect(p1, rect):
        return True
    edges = [((xmin, ymin), (xmax, ymin)), ((xmax, ymin), (xmax, ymax)), ((xmax, ymax), (xmin, ymax)), ((xmin, ymax), (xmin, ymin))]
    return any(segments_intersect(p0, p1, a, b) for a, b in edges)


def point_inside_rect(point: tuple[float, float], rect: tuple[float, float, float, float]) -> bool:
    x, y = point
    xmin, xmax, ymin, ymax = rect
    return xmin < x < xmax and ymin < y < ymax


def segments_intersect(a: tuple[float, float], b: tuple[float, float], c: tuple[float, float], d: tuple[float, float]) -> bool:
    def orient(p: tuple[float, float], q: tuple[float, float], r: tuple[float, float]) -> float:
        return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])

    o1 = orient(a, b, c)
    o2 = orient(a, b, d)
    o3 = orient(c, d, a)
    o4 = orient(c, d, b)
    return o1 * o2 < 0 and o3 * o4 < 0


def write_mapping_artifacts(output_dir: Path, products: PathProducts) -> dict[str, Path]:
    v6a = output_dir / "v6a_geometry_mapping"
    paths = {
        "trial_mapping_metrics": write_csv(
            v6a / "trial_mapping_metrics.csv",
            products.trial_rows,
            (
                "session_id",
                "source_trial_id",
                "split",
                "trial_index",
                "start",
                "goal",
                "endpoint_pair",
                "qc_flags",
                "raw_sample_count",
                "known_sample_count",
                "unknown_sample_count",
                "unknown_sample_fraction",
                "unknown_gap_count",
                "region_run_count",
                "node_run_count",
                "corridor_run_count",
                "known_directed_corridor_count",
                "unknown_direction_corridor_count",
                "middle_directed_component_count",
                "junction_motif_count",
                "corridor_reversal_count",
                "node_dwell_samples",
                "corridor_samples",
                "complete_directed_path_coverage",
                "route_signature",
                "middle_directed_components",
                "junction_motifs",
                "absence_labels_allowed",
            ),
        ),
        "trial_region_dwell": write_csv(
            v6a / "trial_region_dwell.csv",
            products.dwell_rows,
            (
                "session_id",
                "source_trial_id",
                "split",
                "endpoint_pair",
                "region_id",
                "region_type",
                "corridor_id",
                "run_index",
                "first_navigation_sample",
                "last_navigation_sample",
                "dwell_samples",
            ),
        ),
        "trial_corridor_traversals": write_csv(
            v6a / "trial_corridor_traversals.csv",
            products.traversal_rows,
            (
                "session_id",
                "source_trial_id",
                "split",
                "endpoint_pair",
                "corridor_id",
                "directed_component_id",
                "corridor_direction",
                "direction_source",
                "run_index",
                "first_navigation_sample",
                "last_navigation_sample",
                "dwell_samples",
                "progress_start",
                "progress_end",
                "progress_delta",
                "reversal_count_within_corridor",
                "is_middle_corridor",
                "complete_directed_path_coverage",
                "route_signature",
            ),
        ),
        "trial_junction_motifs": write_csv(
            v6a / "trial_junction_motifs.csv",
            products.motif_rows,
            ("session_id", "source_trial_id", "split", "endpoint_pair", "motif_id", "route_signature"),
        ),
        "grid_fragmentation_diagnosis": write_csv(
            v6a / "old_grid_fragmentation_diagnosis.csv",
            grid_diagnostic_rows(products.grid_diagnostics),
            ("transition_category", "dx_grid_steps", "dy_grid_steps", "pillar_line_check", "transitions"),
        ),
    }
    return paths


def grid_diagnostic_rows(counter: Counter[tuple[str, int, int, str]]) -> list[dict[str, Any]]:
    rows = [
        {
            "transition_category": category,
            "dx_grid_steps": dx,
            "dy_grid_steps": dy,
            "pillar_line_check": crosses,
            "transitions": count,
        }
        for (category, dx, dy, crosses), count in counter.items()
    ]
    return sorted(rows, key=lambda row: (-row["transitions"], row["transition_category"], row["dx_grid_steps"], row["dy_grid_steps"]))


def component_support(
    component_trials: Sequence[ComponentTrial],
    directed_components: Sequence[Mapping[str, str]],
) -> tuple[
    list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], SelectedCohort
]:
    component_catalog = {row["component_id"]: row["component_type"] for row in directed_components}
    motif_ids = sorted({motif for trial in component_trials for motif in trial.motifs})
    for motif in motif_ids:
        component_catalog[motif] = "junction_choice_motif"

    support: Counter[tuple[str, str, str, str, str, str]] = Counter()
    route_support: Counter[tuple[str, str, str, str]] = Counter()
    route_sessions: dict[tuple[str, str, str, str], set[str]] = defaultdict(set)
    for trial in component_trials:
        route_support[(trial.endpoint_pair, trial.route_signature, trial.split, trial.complete and "complete" or "incomplete")] += 1
        route_sessions[(trial.endpoint_pair, trial.route_signature, trial.split, trial.complete and "complete" or "incomplete")].add(trial.session_id)
        present = trial.middle_components | trial.motifs
        for component_id, component_type in component_catalog.items():
            if not trial.complete:
                status = "unknown"
            else:
                status = "present" if component_id in present else "absent"
            support[(component_type, component_id, trial.endpoint_pair, trial.session_id, trial.split, status)] += 1

    support_rows = [
        {
            "component_type": ctype,
            "component_id": cid,
            "endpoint_pair": endpoint,
            "session_id": session,
            "split": split,
            "component_status": status,
            "trials": count,
            "unknown_not_absent_policy": str(status == "unknown").lower(),
        }
        for (ctype, cid, endpoint, session, split, status), count in support.items()
    ]
    support_rows.sort(key=lambda row: (row["component_type"], row["component_id"], row["endpoint_pair"], row["session_id"], row["split"], row["component_status"]))

    candidate_rows = candidate_summary(support_rows)
    selected = select_cohort(
        candidate_rows,
        min_train=MIN_TRAIN_PER_COMPONENT_CLASS,
        min_validation=MIN_VALIDATION_PER_COMPONENT_CLASS,
    )
    route_rows = [
        {
            "endpoint_pair": endpoint,
            "route_signature": route,
            "split": split,
            "coverage_status": coverage,
            "trials": count,
            "sessions": len(route_sessions[(endpoint, route, split, coverage)]),
        }
        for (endpoint, route, split, coverage), count in route_support.items()
    ]
    route_rows.sort(
        key=lambda row: (
            -row["trials"],
            row["endpoint_pair"],
            row["route_signature"],
            row["split"],
        )
    )
    return support_rows, candidate_rows, route_rows, selected


def candidate_summary(support_rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    totals: dict[tuple[str, str, str], Counter[tuple[str, str]]] = defaultdict(Counter)
    sessions: dict[tuple[str, str, str, str, str], set[str]] = defaultdict(set)
    session_status: dict[tuple[str, str, str, str, str], Counter[str]] = defaultdict(Counter)
    for row in support_rows:
        key = (str(row["component_type"]), str(row["component_id"]), str(row["endpoint_pair"]))
        split = str(row["split"])
        status = str(row["component_status"])
        if status in {"present", "absent"}:
            totals[key][(split, status)] += int(row["trials"])
            sessions[(*key, split, status)].add(str(row["session_id"]))
            session_status[(*key, split, str(row["session_id"]))][status] += int(row["trials"])
    both_sessions: Counter[tuple[str, str, str, str]] = Counter()
    for session_key, status_counts in session_status.items():
        ctype, cid, endpoint, split, _session = session_key
        if status_counts["present"] and status_counts["absent"]:
            both_sessions[(ctype, cid, endpoint, split)] += 1

    rows: list[dict[str, Any]] = []
    for key, counter in totals.items():
        ctype, cid, endpoint = key
        train_present = counter[("train", "present")]
        train_absent = counter[("train", "absent")]
        val_present = counter[("validation", "present")]
        val_absent = counter[("validation", "absent")]
        train_both_sessions = both_sessions[(*key, "train")]
        val_both_sessions = both_sessions[(*key, "validation")]
        rows.append(
            {
                "component_type": ctype,
                "component_id": cid,
                "endpoint_pair": endpoint,
                "train_present_trials": train_present,
                "train_absent_trials": train_absent,
                "validation_present_trials": val_present,
                "validation_absent_trials": val_absent,
                "train_present_sessions": len(sessions[(*key, "train", "present")]),
                "train_absent_sessions": len(sessions[(*key, "train", "absent")]),
                "validation_present_sessions": len(sessions[(*key, "validation", "present")]),
                "validation_absent_sessions": len(sessions[(*key, "validation", "absent")]),
                "train_sessions_with_both_classes": train_both_sessions,
                "validation_sessions_with_both_classes": val_both_sessions,
                "both_classes_in_endpoint_pair_train": str(bool(train_present and train_absent)).lower(),
                "both_classes_in_endpoint_pair_validation": str(bool(val_present and val_absent)).lower(),
                "min_class_trials_all_splits": min(train_present, train_absent, val_present, val_absent),
                "min_validation_class_trials": min(val_present, val_absent),
                "total_known_trials": train_present + train_absent + val_present + val_absent,
            }
        )
    rows.sort(
        key=lambda row: (
            row["component_type"] != "directed_middle_corridor",
            -int(row["min_class_trials_all_splits"]),
            -int(row["min_validation_class_trials"]),
            -(int(row["train_sessions_with_both_classes"]) + int(row["validation_sessions_with_both_classes"])),
            -int(row["total_known_trials"]),
            row["endpoint_pair"],
            row["component_id"],
        )
    )
    return rows


def select_cohort(rows: Sequence[Mapping[str, Any]], min_train: int, min_validation: int) -> SelectedCohort:
    for row in rows:
        if row["component_type"] != "directed_middle_corridor":
            continue
        if (
            int(row["train_present_trials"]) >= min_train
            and int(row["train_absent_trials"]) >= min_train
            and int(row["validation_present_trials"]) >= min_validation
            and int(row["validation_absent_trials"]) >= min_validation
        ):
            return SelectedCohort(
                str(row["component_id"]),
                str(row["component_type"]),
                str(row["endpoint_pair"]),
                "strict_viable_behavior_support",
                f"met min_train={min_train}, min_validation={min_validation} per present/absent class",
            )
    for row in rows:
        if row["component_type"] == "directed_middle_corridor" and int(row["min_class_trials_all_splits"]):
            return SelectedCohort(
                str(row["component_id"]),
                str(row["component_type"]),
                str(row["endpoint_pair"]),
                "fallback_behavior_support_below_threshold",
                "no strict candidate met thresholds; selected best behavior-only support for feasibility documentation",
            )
    return SelectedCohort("", "", "", "no_viable_component", "no component had both classes in train and validation")


def selected_direction_sensitivity(
    component_trials: Sequence[ComponentTrial], selected: SelectedCohort
) -> dict[str, Any]:
    strict_sources = {"adjacent_nodes", "progress"}
    primary_counts: Counter[str] = Counter()
    strict_counts: Counter[str] = Counter()
    direction_sources: Counter[str] = Counter()
    weak_sources: list[str] = []
    for trial in component_trials:
        if trial.endpoint_pair != selected.endpoint_pair:
            continue
        primary_status = (
            "unknown"
            if not trial.complete
            else "present"
            if selected.component_id in trial.middle_components
            else "absent"
        )
        primary_counts[f"{trial.split}|{primary_status}"] += 1
        selected_sources = [
            direction_source
            for component_id, direction_source in trial.middle_component_direction_sources
            if component_id == selected.component_id
        ]
        for direction_source in selected_sources:
            direction_sources[direction_source] += 1
        if not trial.complete:
            strict_status = "unknown"
        elif any(source in strict_sources for source in selected_sources):
            strict_status = "present"
        elif selected_sources:
            strict_status = "unknown_direction_dependency"
            weak_sources.append(trial.source_trial_id)
        else:
            strict_status = "absent"
        strict_counts[f"{trial.split}|{strict_status}"] += 1
    threshold_failures = []
    requirements = {
        "train|present": MIN_TRAIN_PER_COMPONENT_CLASS,
        "train|absent": MIN_TRAIN_PER_COMPONENT_CLASS,
        "validation|present": MIN_VALIDATION_PER_COMPONENT_CLASS,
        "validation|absent": MIN_VALIDATION_PER_COMPONENT_CLASS,
    }
    for condition, required in requirements.items():
        if strict_counts[condition] < required:
            threshold_failures.append(
                {
                    "condition": condition,
                    "strict_direction_trials": strict_counts[condition],
                    "required_trials": required,
                }
            )
    weak_count = sum(
        count
        for key, count in strict_counts.items()
        if key.endswith("|unknown_direction_dependency")
    )
    gate_failures = []
    if threshold_failures:
        gate_failures.append("strict direction source present/absent support below threshold")
    if weak_count:
        gate_failures.append("selected component has one-adjacent-node-only trial dependence")
    return {
        "selected_component_id": selected.component_id,
        "selected_endpoint_pair": selected.endpoint_pair,
        "allowed_strict_direction_sources": sorted(strict_sources),
        "selected_middle_traversal_direction_source_counts": dict(
            sorted(direction_sources.items())
        ),
        "primary_trial_status_counts_by_split": dict(sorted(primary_counts.items())),
        "strict_direction_trial_status_counts_by_split": dict(
            sorted(strict_counts.items())
        ),
        "strict_direction_threshold_failures": threshold_failures,
        "one_adjacent_node_only_source_trial_count": weak_count,
        "one_adjacent_node_only_source_trial_examples": weak_sources[:20],
        "strict_direction_sensitivity_gate_status": "passed" if not gate_failures else "failed",
        "strict_direction_sensitivity_gate_failures": gate_failures,
    }


def write_direction_source_counts(
    output_dir: Path,
    traversal_rows: Sequence[Mapping[str, Any]],
    selected_sensitivity: Mapping[str, Any],
) -> Path:
    counts = Counter(str(row["direction_source"]) for row in traversal_rows)
    rows = [
        {"scope": "all_corridor_traversals", "direction_source": source, "count": count}
        for source, count in sorted(counts.items())
    ]
    rows.extend(
        {
            "scope": "selected_middle_component_traversals",
            "direction_source": source,
            "count": count,
        }
        for source, count in selected_sensitivity[
            "selected_middle_traversal_direction_source_counts"
        ].items()
    )
    return write_csv(
        output_dir / "v6a_geometry_mapping" / "direction_source_counts.csv",
        rows,
        ("scope", "direction_source", "count"),
    )


def write_support_artifacts(
    output_dir: Path,
    support_rows: Sequence[Mapping[str, Any]],
    candidate_rows: Sequence[Mapping[str, Any]],
    route_rows: Sequence[Mapping[str, Any]],
) -> dict[str, Path]:
    v6b = output_dir / "v6b_component_support"
    v6b.mkdir(exist_ok=True)
    return {
        "component_support": write_csv(
            v6b / "component_endpoint_session_split_support.csv",
            support_rows,
            (
                "component_type",
                "component_id",
                "endpoint_pair",
                "session_id",
                "split",
                "component_status",
                "trials",
                "unknown_not_absent_policy",
            ),
        ),
        "candidate_summary": write_csv(
            v6b / "component_candidate_behavior_support_summary.csv",
            candidate_rows,
            (
                "component_type",
                "component_id",
                "endpoint_pair",
                "train_present_trials",
                "train_absent_trials",
                "validation_present_trials",
                "validation_absent_trials",
                "train_present_sessions",
                "train_absent_sessions",
                "validation_present_sessions",
                "validation_absent_sessions",
                "train_sessions_with_both_classes",
                "validation_sessions_with_both_classes",
                "both_classes_in_endpoint_pair_train",
                "both_classes_in_endpoint_pair_validation",
                "min_class_trials_all_splits",
                "min_validation_class_trials",
                "total_known_trials",
            ),
        ),
        "whole_route_support": write_csv(
            v6b / "whole_route_behavior_support_summary.csv",
            route_rows,
            (
                "endpoint_pair",
                "route_signature",
                "split",
                "coverage_status",
                "trials",
                "sessions",
            ),
        ),
    }


def required_panel_summary(
    condition_sources: Mapping[tuple[str, str], set[str]],
    condition_sessions: Mapping[tuple[str, str], set[str]],
    panel_sets: Mapping[str, set[str]],
    selected: SelectedCohort,
) -> dict[str, Any]:
    required_counts = {
        "train|present": MIN_TRAIN_PER_COMPONENT_CLASS,
        "train|absent": MIN_TRAIN_PER_COMPONENT_CLASS,
        "validation|present": MIN_VALIDATION_PER_COMPONENT_CLASS,
        "validation|absent": MIN_VALIDATION_PER_COMPONENT_CLASS,
    }
    source_counts = {
        f"{split}|{status}": len(sources)
        for (split, status), sources in sorted(condition_sources.items())
    }
    session_counts = {
        f"{split}|{status}": len(sessions)
        for (split, status), sessions in sorted(condition_sessions.items())
    }
    missing_required = [
        label for label in REQUIRED_PANEL_CONDITIONS if source_counts.get(label, 0) == 0
    ]
    below_threshold = [
        {
            "condition": label,
            "source_trials": source_counts.get(label, 0),
            "required_source_trials": required,
        }
        for label, required in required_counts.items()
        if source_counts.get(label, 0) < required
    ]
    required_panel_sets = [panel_sets.get(label, set()) for label in REQUIRED_PANEL_CONDITIONS]
    shared_required_panel = (
        set.intersection(*required_panel_sets)
        if required_panel_sets and not missing_required
        else set()
    )
    gate_failures = []
    if selected.status != "strict_viable_behavior_support":
        gate_failures.append("selected component did not meet strict behavior support")
    if missing_required:
        gate_failures.append("missing required train/validation present/absent condition")
    if below_threshold:
        gate_failures.append("required condition below source-trial threshold")
    if not shared_required_panel:
        gate_failures.append("no shared observed cell panel across required conditions")
    return {
        "required_conditions": list(REQUIRED_PANEL_CONDITIONS),
        "required_source_trial_thresholds": required_counts,
        "source_trials_by_split_status": source_counts,
        "sessions_by_split_status": session_counts,
        "cells_by_split_status": {
            label: len(cells) for label, cells in sorted(panel_sets.items())
        },
        "missing_required_conditions": missing_required,
        "below_threshold_required_conditions": below_threshold,
        "unknown_source_trials_by_split": {
            label: count
            for label, count in source_counts.items()
            if label.endswith("|unknown")
        },
        "unknown_sessions_by_split": {
            label: count
            for label, count in session_counts.items()
            if label.endswith("|unknown")
        },
        "shared_observed_cell_panel_required_present_absent_conditions": len(
            shared_required_panel
        ),
        "shared_observed_cell_panel_all_selected_conditions": len(
            shared_required_panel
        ),
        "shared_observed_cell_ids": sorted(shared_required_panel),
        "condition_panel_gate_status": "passed" if not gate_failures else "failed",
        "condition_panel_gate_failures": gate_failures,
    }


def cue_membership(
    access: SplitFilteredAccess,
    component_trials: Sequence[ComponentTrial],
    selected: SelectedCohort,
    output_dir: Path,
) -> tuple[dict[str, Path], dict[str, Any]]:
    selected_sources = {
        trial.source_trial_id
        for trial in component_trials
        if selected.endpoint_pair and trial.endpoint_pair == selected.endpoint_pair
    }
    source_status = {}
    for trial in component_trials:
        if trial.source_trial_id not in selected_sources:
            continue
        if not trial.complete:
            status = "unknown"
        elif selected.component_id in trial.middle_components or selected.component_id in trial.motifs:
            status = "present"
        else:
            status = "absent"
        source_status[trial.source_trial_id] = (trial, status)

    cells_by_source: dict[str, set[str]] = defaultdict(set)
    cells_by_session: dict[str, set[str]] = defaultdict(set)
    for row in access.iter_cue_counts():
        source = row["source_trial_id"]
        if source not in source_status:
            continue
        cell = row["cell_id"]
        trial, _status = source_status[source]
        cells_by_source[source].add(cell)
        cells_by_session[trial.session_id].add(cell)

    v6c = output_dir / "v6c_population_membership"
    v6c.mkdir(exist_ok=True)
    source_rows = []
    condition_cells: dict[tuple[str, str], dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))
    condition_sources: dict[tuple[str, str], set[str]] = defaultdict(set)
    condition_sessions: dict[tuple[str, str], set[str]] = defaultdict(set)
    for source, (trial, status) in sorted(source_status.items()):
        cells = cells_by_source.get(source, set())
        source_rows.append(
            {
                "source_trial_id": source,
                "session_id": trial.session_id,
                "split": trial.split,
                "endpoint_pair": trial.endpoint_pair,
                "selected_component_id": selected.component_id,
                "component_status": status,
                "complete_directed_path_coverage": str(trial.complete).lower(),
                "route_signature": trial.route_signature,
                "observed_cells_for_source_trial": len(cells),
                "cell_ids": ";".join(sorted(cells)),
            }
        )
        key = (trial.split, status)
        condition_sources[key].add(source)
        condition_sessions[key].add(trial.session_id)
        for cell in cells:
            condition_cells[key][cell].add(source)

    condition_rows = []
    panel_sets: dict[str, set[str]] = {}
    for key, cell_sources in sorted(condition_cells.items()):
        split, status = key
        label = f"{split}|{status}"
        panel_sets[label] = set(cell_sources)
        for cell, sources in sorted(cell_sources.items()):
            sessions = {source_status[source][0].session_id for source in sources}
            condition_rows.append(
                {
                    "split": split,
                    "component_status": status,
                    "selected_component_id": selected.component_id,
                    "endpoint_pair": selected.endpoint_pair,
                    "cell_id": cell,
                    "source_trial_count": len(sources),
                    "sessions": len(sessions),
                    "source_trial_ids": ";".join(sorted(sources)),
                }
            )
    paths = {
        "selected_source_manifest": write_csv(
            v6c / "selected_component_source_membership.csv",
            source_rows,
            (
                "source_trial_id",
                "session_id",
                "split",
                "endpoint_pair",
                "selected_component_id",
                "component_status",
                "complete_directed_path_coverage",
                "route_signature",
                "observed_cells_for_source_trial",
                "cell_ids",
            ),
        ),
        "condition_mean_membership": write_csv(
            v6c / "selected_component_condition_mean_source_membership.csv",
            condition_rows,
            (
                "split",
                "component_status",
                "selected_component_id",
                "endpoint_pair",
                "cell_id",
                "source_trial_count",
                "sessions",
                "source_trial_ids",
            ),
        ),
    }
    panel_summary = {
        "selected_component_id": selected.component_id,
        "selected_endpoint_pair": selected.endpoint_pair,
        "selection_status": selected.status,
        **required_panel_summary(
            condition_sources, condition_sessions, panel_sets, selected
        ),
        "neural_values_read_or_fit": False,
        "cue_table_use": "source_trial_id/cell_id membership only after behavior-only component selection; cue_spike_count values are not aggregated or emitted",
    }
    write_json(v6c / "selected_component_panel_summary.json", panel_summary)
    paths["panel_summary"] = v6c / "selected_component_panel_summary.json"
    return paths, panel_summary


def plot_static_graph(regions: Mapping[str, Region], output_dir: Path) -> Path:
    fig_dir = output_dir / "v6a_geometry_mapping" / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)
    path = fig_dir / "static_region_corridor_graph.png"
    fig, ax = plt.subplots(figsize=(7, 7))
    for region in regions.values():
        color = "#dcecff" if region.region_type == "node" else "#fff3cd"
        rect = Rectangle((region.x_min, region.y_min), region.x_max - region.x_min, region.y_max - region.y_min, facecolor=color, edgecolor="black", alpha=0.75)
        ax.add_patch(rect)
        ax.text(region.center_x, region.center_y, region.region_id, ha="center", va="center", fontsize=6)
    for xmin, xmax, ymin, ymax in ((-7.5, -2.5, -7.5, -2.5), (2.5, 7.5, -7.5, -2.5), (2.5, 7.5, 2.5, 7.5), (-7.5, -2.5, 2.5, 7.5)):
        ax.add_patch(Rectangle((xmin, ymin), xmax - xmin, ymax - ymin, facecolor="#666666", edgecolor="black"))
    ax.set_aspect("equal")
    ax.set_xlim(OUTER_MIN, OUTER_MAX)
    ax.set_ylim(OUTER_MIN, OUTER_MAX)
    ax.set_title("V6 static 9-node / 12-corridor geometry")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def plot_raw_overlays(regions: Mapping[str, Region], products: PathProducts, output_dir: Path) -> Path:
    fig_dir = output_dir / "v6a_geometry_mapping" / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)
    path = fig_dir / "raw_path_overlays_train_validation_examples.png"
    sources = sorted(products.raw_paths_for_plot)[:12]
    cols = 3
    rows_n = max(1, math.ceil(len(sources) / cols))
    fig, axes = plt.subplots(rows_n, cols, figsize=(12, 3.5 * rows_n), squeeze=False)
    for ax in axes.flat:
        for region in regions.values():
            color = "#dcecff" if region.region_type == "node" else "#fff3cd"
            ax.add_patch(Rectangle((region.x_min, region.y_min), region.x_max - region.x_min, region.y_max - region.y_min, facecolor=color, edgecolor="lightgray", alpha=0.5))
        for xmin, xmax, ymin, ymax in ((-7.5, -2.5, -7.5, -2.5), (2.5, 7.5, -7.5, -2.5), (2.5, 7.5, 2.5, 7.5), (-7.5, -2.5, 2.5, 7.5)):
            ax.add_patch(Rectangle((xmin, ymin), xmax - xmin, ymax - ymin, facecolor="#777777", edgecolor="black", alpha=0.8))
        ax.set_aspect("equal")
        ax.set_xticks([])
        ax.set_yticks([])
    for ax, source in zip(axes.flat, sources, strict=False):
        coords = products.raw_paths_for_plot[source]
        if coords:
            ax.plot([x for x, _ in coords], [y for _, y in coords], linewidth=1.0, marker=".", markersize=1.5)
        ax.set_title(source, fontsize=8)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def summarize(
    output_dir: Path,
    config: Mapping[str, Any],
    access: SplitFilteredAccess,
    labels: Mapping[str, TrialLabel],
    products: PathProducts,
    component_trials: Sequence[ComponentTrial],
    candidate_rows: Sequence[Mapping[str, Any]],
    selected: SelectedCohort,
    panel_summary: Mapping[str, Any],
    direction_sensitivity: Mapping[str, Any],
    artifact_paths: Sequence[Path],
    command: str,
) -> dict[str, Any]:
    complete_trials = [trial for trial in component_trials if trial.complete]
    by_split = Counter(label.split for label in labels.values())
    complete_by_split = Counter(trial.split for trial in complete_trials)
    top_candidates = list(candidate_rows[:10])
    split_guard = access.audit.as_dict()
    gate_failures = []
    if split_guard["forbidden_rows_yielded"]:
        gate_failures.append("split guard yielded forbidden rows")
    if selected.status != "strict_viable_behavior_support":
        gate_failures.append("selected component did not meet strict behavior support")
    if panel_summary["condition_panel_gate_status"] != "passed":
        gate_failures.append("required train/validation present/absent panel gate failed")
    if direction_sensitivity["strict_direction_sensitivity_gate_status"] != "passed":
        gate_failures.append("strict direction-source sensitivity gate failed")
    summary = {
        "created_utc": datetime.now(UTC).isoformat(),
        "status": "completed_v6_behavior_support_audit",
        "scientific_status": SCIENTIFIC_STATUS,
        "claim_ceiling": config["claim_ceiling"],
        "output_dir": str(output_dir),
        "command": command,
        "split_guard_audit": split_guard,
        "input_hashes": config["input_hashes"],
        "split_hash": config["split_hash"],
        "graph_hashes": {
            "v6_static_region_corridor_graph_hash": config["static_region_corridor_graph_hash"],
            "fine_documented_primary_hash": config["fine_graph_reconciliation"]["documented_primary_hash"],
            "fine_v5_script_style_primary_hash_computed": config["fine_graph_reconciliation"]["v5_script_style_primary_hash_computed"],
            "fine_legacy_bare_int_edge_hash_computed": config["fine_graph_reconciliation"]["legacy_bare_int_numeric_sorted_edge_hash_computed"],
            "fine_current_typed_mazegraph_edge_hash_computed": config["fine_graph_reconciliation"]["current_typed_mazegraph_edge_only_hash_computed"],
            "schema_note": config["fine_graph_reconciliation"]["hash_reconciliation"],
        },
        "counts": {
            "success_after_success_train_validation_trials": len(labels),
            "success_after_success_by_split": dict(sorted(by_split.items())),
            "mapped_trials_with_path_rows": len(component_trials),
            "complete_directed_path_coverage_trials": len(complete_trials),
            "complete_directed_path_coverage_by_split": dict(sorted(complete_by_split.items())),
            "complete_path_fraction": len(complete_trials) / len(component_trials) if component_trials else None,
            "unique_complete_route_signatures": len({trial.route_signature for trial in complete_trials}),
            "unique_middle_directed_components_observed": len({component for trial in component_trials for component in trial.middle_components}),
            "unique_junction_motifs_observed": len({motif for trial in component_trials for motif in trial.motifs}),
        },
        "old_grid_fragmentation_top_categories": grid_diagnostic_rows(products.grid_diagnostics)[:12],
        "selected_component_cohort": {
            "component_id": selected.component_id,
            "component_type": selected.component_type,
            "endpoint_pair": selected.endpoint_pair,
            "status": selected.status,
            "reason": selected.reason,
        },
        "top_behavior_support_candidates": top_candidates,
        "population_membership_panel_summary": panel_summary,
        "selected_component_direction_sensitivity": direction_sensitivity,
        "v6_stage_gate": {
            "status": "ready_for_parent_review" if not gate_failures else "blocked_before_neural_fits",
            "failures": gate_failures,
            "next_gate": "parent independent review before any V7/V8/V9 neural fitting",
        },
        "guardrails": {
            "locked_test_evaluated": False,
            "raw_test_rows_yielded_by_loader": split_guard["forbidden_rows_yielded"],
            "neural_values_read_or_fit": False,
            "shortest_path_gap_invention": False,
            "all195_blind_imputation": False,
            "unknown_segments_labelled_absent": False,
        },
        "artifact_hashes": {
            str(path.relative_to(output_dir)): sha256_file(path)
            for path in artifact_paths
            if path.exists() and path.is_file()
        },
        "git": git_state(),
        "package_versions": package_versions(),
    }
    write_json(output_dir / "summary.json", summary)
    return summary


def write_teaching_audit_markdown(path: Path, summary: Mapping[str, Any]) -> None:
    counts = summary["counts"]
    selected = summary["selected_component_cohort"]
    lines = [
        "# V6 reset graph/support audit",
        "",
        f"Status: **{summary['scientific_status']}**",
        "",
        "## What this stage answers",
        "",
        "V6 asks whether the behavior can be represented by a reviewed static geometry and whether any route component has enough train/validation support for a later neural analysis. It does not fit neural models and it does not evaluate test.",
        "",
        "Measured data are Unity 2D navigation positions and cue-table source/cell membership. Derived data are static regions/corridors, directed corridor traversals, complete/unknown coverage flags, and support counts. Inferred start/goal labels remain exploratory marker labels.",
        "",
        "## Holdout reset",
        "",
        "A prior stopped writer exposed unfiltered all-session endpoint summaries. This run uses only the split-gated loader; the original test is not pristine and is not evaluated. Claims remain exploratory development claims only.",
        "",
        "## Static geometry",
        "",
        f"- V6 static graph hash: `{summary['graph_hashes']['v6_static_region_corridor_graph_hash']}`",
        "- 9 node/plaza regions and 12 corridor regions from the four-pillar floor geometry.",
        "- The 1,344-node fine floor grid is retained as a reference; it is not degree-contracted into a skeleton.",
        "- Unknown samples and unknown directions break complete coverage; no shortest path is inserted.",
        "",
        "## Mapping/support metrics",
        "",
        f"- success-after-success train/validation trials labelled: `{counts['success_after_success_train_validation_trials']}`",
        f"- mapped trials with path rows: `{counts['mapped_trials_with_path_rows']}`",
        f"- complete directed path coverage trials: `{counts['complete_directed_path_coverage_trials']}` ({counts['complete_path_fraction']:.3f} fraction)",
        f"- unique complete route signatures: `{counts['unique_complete_route_signatures']}`",
        f"- observed middle directed components: `{counts['unique_middle_directed_components_observed']}`",
        f"- observed junction motifs: `{counts['unique_junction_motifs_observed']}`",
        "",
        "## Selected behavior-only cohort",
        "",
        f"- component: `{selected['component_id']}`",
        f"- endpoint pair: `{selected['endpoint_pair']}`",
        f"- status: `{selected['status']}` — {selected['reason']}",
        "",
        "This selection used behavior support only. Cue tables were consulted afterward only to list source/cell memberships; spike-count values were not aggregated or fit.",
        "",
        "## Scientific gate",
        "",
        "V6 passes the software/support gate if independent review accepts the static regions, overlay plots, split guard, and selected component support. It does not pass the H1 neural evidence gate; V7/V8/V9 fitting needs parent review first.",
        "",
        "## Key artifact files",
        "",
    ]
    for name in sorted(summary["artifact_hashes"]):
        lines.append(f"- `{name}`")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def csv_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        if not math.isfinite(value):
            return ""
        return f"{value:.8g}"
    return str(value)


def run_audit(
    import_dir: Path,
    split_dir: Path,
    geometry: Path,
    output_dir: Path,
    command: str,
) -> dict[str, Any]:
    ensure_output_dir(output_dir, import_dir)
    log = JsonlLog(output_dir / "logs" / "stage_events.jsonl")
    log.write("start", output_dir=str(output_dir))
    access = SplitFilteredAccess(import_dir, split_dir)
    regions, corridor_regions, directed_components = build_regions()
    config = write_frozen_config(
        output_dir,
        import_dir,
        split_dir,
        geometry,
        access,
        regions,
        directed_components,
        min_train_per_class=MIN_TRAIN_PER_COMPONENT_CLASS,
        min_validation_per_class=MIN_VALIDATION_PER_COMPONENT_CLASS,
    )
    v6a = output_dir / "v6a_geometry_mapping"
    v6b = output_dir / "v6b_component_support"
    v6c = output_dir / "v6c_population_membership"
    for path in (v6b, v6c):
        path.mkdir(exist_ok=True)
    hash_reconciliation_path = write_hash_reconciliation_report(output_dir, config)

    write_csv(
        v6a / "static_region_catalog.csv",
        (region_to_row(region) for region in sorted(regions.values(), key=lambda item: item.region_id)),
        (
            "region_id",
            "region_type",
            "x_band",
            "y_band",
            "x_min",
            "x_max",
            "y_min",
            "y_max",
            "center_x",
            "center_y",
            "corridor_id",
            "from_node",
            "to_node",
            "axis",
            "centerline_length",
        ),
    )
    write_csv(
        v6a / "static_corridor_directed_components.csv",
        directed_components,
        ("component_id", "component_type", "corridor_id", "from_node", "to_node"),
    )
    plot1 = plot_static_graph(regions, output_dir)
    log.write("frozen_config_written", static_hash=config["static_region_corridor_graph_hash"])

    labels = labels_from_trials(access)
    log.write("labels_loaded", labels=len(labels))
    products, component_trials = build_path_products(access, labels, regions, output_dir)
    artifact_paths = list(write_mapping_artifacts(output_dir, products).values())
    plot2 = plot_raw_overlays(regions, products, output_dir)
    artifact_paths.extend([plot1, plot2])
    log.write("paths_mapped", trials=len(component_trials))

    support_rows, candidate_rows, route_rows, selected = component_support(component_trials, directed_components)
    direction_sensitivity = selected_direction_sensitivity(component_trials, selected)
    artifact_paths.append(
        write_direction_source_counts(output_dir, products.traversal_rows, direction_sensitivity)
    )
    artifact_paths.extend(
        write_support_artifacts(output_dir, support_rows, candidate_rows, route_rows).values()
    )
    log.write("support_counted", candidates=len(candidate_rows), selected=selected.component_id)

    membership_paths, panel_summary = cue_membership(access, component_trials, selected, output_dir)
    artifact_paths.extend(membership_paths.values())
    log.write("cue_membership_listed", selected=selected.component_id)

    artifact_paths.extend(
        [
            v6a / "preread_frozen_graph_config.json",
            v6a / "preread_frozen_graph_config.md",
            hash_reconciliation_path,
            v6a / "static_region_catalog.csv",
            v6a / "static_corridor_directed_components.csv",
            v6a / "mapped_path_samples_train_validation_success_after_success.csv.gz",
            output_dir / "logs" / "stage_events.jsonl",
        ]
    )
    summary = summarize(
        output_dir,
        config,
        access,
        labels,
        products,
        component_trials,
        candidate_rows,
        selected,
        panel_summary,
        direction_sensitivity,
        artifact_paths,
        command,
    )
    write_teaching_audit_markdown(output_dir / "v6_teaching_audit.md", summary)
    summary["artifact_hashes"]["v6_teaching_audit.md"] = sha256_file(output_dir / "v6_teaching_audit.md")
    write_json(output_dir / "summary.json", summary)
    log.write("complete", summary=str(output_dir / "summary.json"))
    return summary


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run")
    run.add_argument("--import-dir", type=Path, default=DEFAULT_IMPORT_DIR)
    run.add_argument("--split-dir", type=Path, default=DEFAULT_SPLIT_DIR)
    run.add_argument("--geometry", type=Path, default=DEFAULT_GEOMETRY)
    run.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    if args.command == "run":
        command = " ".join(
            shlex.quote(arg)
            for arg in [
                sys.executable,
                "-m",
                "scripts.place195_v6_graph_support_audit",
                *sys.argv[1:],
            ]
        )
        summary = run_audit(args.import_dir, args.split_dir, args.geometry, args.output_dir, command)
        print(
            json.dumps(
                {
                    "status": summary["status"],
                    "output_dir": summary["output_dir"],
                    "counts": summary["counts"],
                    "selected_component_cohort": summary["selected_component_cohort"],
                    "guardrails": summary["guardrails"],
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 0
    raise ValueError(args.command)


if __name__ == "__main__":
    raise SystemExit(main())
