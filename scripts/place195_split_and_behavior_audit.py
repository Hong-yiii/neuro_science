#!/usr/bin/env python3
"""Freeze source-trial splits and run a train/validation behavior QC audit.

No graph, route family, PCA, CEBRA, decoder, or H1 claim is created here.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
from collections import Counter, defaultdict
from collections.abc import Iterable, Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path
from statistics import median
from typing import Any

from docs.cebra_pilot.implementation.splits import freeze_splits
from scripts.import_place195_sessions import (
    ROOT,
    _jsonable,
    _to_float,
    _to_int,
    git_state,
    package_versions,
    sha256_file,
    validate_output_dir,
)

DEFAULT_IMPORT_DIR = (
    ROOT / "outputs/prospective_path_first_run/place195-all-sessions-20260830-v4"
)
DEFAULT_OUTPUT_PARENT = ROOT / "outputs/prospective_path_first_run"
SPLIT_VERSION = "place195_source_trial_blocked_split_v1"
SPLIT_STATUS = "source_trial_split_for_exploratory_behavior_audit_not_h1_evidence"
AUDIT_STATUS = "train_validation_behavior_qc_audit_graph_path_blocked"
SIMULTANEITY_STATUS = "candidate_same_session_unverified"
TASK_LABEL_STATUS = "inferred_from_marker_minor_digit_unverified"


def read_csv(path: Path) -> list[dict[str, str]]:
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(
    path: Path, rows: Iterable[Mapping[str, Any]], fieldnames: Sequence[str]
) -> Path:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {field: _csv_value(row.get(field, "")) for field in fieldnames}
            )
    return path


def write_json(path: Path, payload: Mapping[str, Any]) -> Path:
    path.write_text(
        json.dumps(_jsonable(payload), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return path


def read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"could not read JSON from {path}") from exc


def parse_json_text(text: str, label: str) -> dict[str, Any]:
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"could not parse JSON payload: {label}") from exc
    if not isinstance(parsed, dict):
        raise ValueError(f"expected JSON object: {label}")
    return parsed


def freeze_place195_splits(
    import_dir: Path,
    output_dir: Path,
    block_size: int = 20,
    train_ratio: float = 0.70,
    validation_ratio: float = 0.15,
    test_ratio: float = 0.15,
) -> dict[str, Any]:
    if block_size < 2:
        raise ValueError("block_size must be at least 2")
    if abs((train_ratio + validation_ratio + test_ratio) - 1.0) > 1e-9:
        raise ValueError("split ratios must sum to 1")
    validate_output_dir(output_dir, import_dir)
    output_dir.mkdir(parents=True, exist_ok=False)

    summary = read_json(import_dir / "summary.json")
    trials = read_csv(import_dir / "trials.csv")
    assignments = assign_splits_to_trials(
        trials,
        block_size=block_size,
        train_ratio=train_ratio,
        validation_ratio=validation_ratio,
        test_ratio=test_ratio,
    )
    frozen = freeze_splits(
        (
            {
                "sample_id": row["source_trial_id"],
                "source_trial_id": row["source_trial_id"],
                "session_id": row["session_id"],
                "simultaneous_recording_group": row["candidate_recording_group"],
                "split": row["split"],
            }
            for row in assignments
        ),
        expected_source_trial_ids=[row["source_trial_id"] for row in trials],
    )

    assignment_path = write_csv(
        output_dir / "source_trial_splits.csv",
        assignments,
        (
            "split_version",
            "source_trial_id",
            "session_id",
            "candidate_recording_group",
            "simultaneity_status",
            "trial_index",
            "previous_source_trial_id",
            "ripple_codes",
            "unity_codes",
            "eyelink_codes",
            "marker_minor_digit",
            "task_label_status",
            "outcome",
            "qc_flags",
            "split_block_id",
            "split",
            "trial_row_sha256",
        ),
    )
    frozen_path = write_json(
        output_dir / "frozen_splits.json",
        {
            "sha256": frozen.sha256,
            "payload": parse_json_text(
                frozen.canonical_json, "frozen split canonical json"
            ),
        },
    )
    counts_path = write_csv(
        output_dir / "split_counts_by_session.csv",
        split_counts_by_session(assignments),
        ("session_id", "split", "trials", "success", "timeout", "qc_flagged"),
    )
    marker_counts_path = write_csv(
        output_dir / "split_counts_by_marker_outcome.csv",
        split_counts_by_marker(assignments),
        ("split", "marker_minor_digit", "outcome", "trials", "qc_flagged"),
    )

    run_summary: dict[str, Any] = {
        "created_utc": datetime.now(UTC).isoformat(),
        "status": "passed",
        "scientific_status": SPLIT_STATUS,
        "import_dir": str(import_dir),
        "output_dir": str(output_dir),
        "split_hash": frozen.sha256,
        "split_version": SPLIT_VERSION,
        "split_policy": {
            "algorithm": "deterministic per-session contiguous trial blocks assigned by sha256-ranked block id",
            "block_size_source_trials": block_size,
            "ratios_by_block": {
                "train": train_ratio,
                "validation": validation_ratio,
                "test": test_ratio,
            },
            "uses_neural_activity": False,
            "uses_path_samples_or_path_metrics": False,
            "uses_graph_or_route_labels": False,
            "uses_unverified_start_goal_labels": False,
        },
        "input_artifact_hashes": summary.get("artifact_hashes", {}),
        "selection_list": summary.get("selection_list", {}),
        "counts": split_counts(assignments),
        "recording_group_split_counts": frozen.recording_group_split_counts,
        "artifact_hashes": {
            assignment_path.name: sha256_file(assignment_path),
            frozen_path.name: sha256_file(frozen_path),
            counts_path.name: sha256_file(counts_path),
            marker_counts_path.name: sha256_file(marker_counts_path),
        },
        "code_hashes": {
            "scripts/place195_split_and_behavior_audit.py": sha256_file(Path(__file__))
        },
        "git": git_state(),
        "package_versions": package_versions(),
        "stop_conditions": stop_conditions(),
    }
    write_json(output_dir / "split_summary.json", run_summary)
    write_decisions(output_dir / "decisions.md", run_summary)
    return run_summary


def assign_splits_to_trials(
    trials: Sequence[Mapping[str, str]],
    block_size: int,
    train_ratio: float,
    validation_ratio: float,
    test_ratio: float,
) -> list[dict[str, Any]]:
    by_session: dict[str, list[Mapping[str, str]]] = defaultdict(list)
    for row in trials:
        by_session[row["session_id"]].append(row)

    assignments: list[dict[str, Any]] = []
    for session_id in sorted(by_session):
        session_rows = sorted(
            by_session[session_id], key=lambda row: _to_int(row["trial_index"])
        )
        blocks = [
            session_rows[index : index + block_size]
            for index in range(0, len(session_rows), block_size)
        ]
        split_by_block = assign_blocks(
            session_id, len(blocks), train_ratio, validation_ratio, test_ratio
        )
        for block_index, block_rows in enumerate(blocks):
            block_id = f"{session_id}_block{block_index + 1:03d}"
            split = split_by_block[block_index]
            for row in block_rows:
                assignments.append(
                    {
                        "split_version": SPLIT_VERSION,
                        "source_trial_id": row["source_trial_id"],
                        "session_id": session_id,
                        "candidate_recording_group": f"{session_id}_candidate_same_session_unverified",
                        "simultaneity_status": SIMULTANEITY_STATUS,
                        "trial_index": row["trial_index"],
                        "previous_source_trial_id": row.get(
                            "previous_source_trial_id", ""
                        ),
                        "ripple_codes": row.get("ripple_codes", ""),
                        "unity_codes": row.get("unity_codes", ""),
                        "eyelink_codes": row.get("eyelink_codes", ""),
                        "marker_minor_digit": row.get("marker_minor_digit", ""),
                        "task_label_status": TASK_LABEL_STATUS,
                        "outcome": row.get("outcome", ""),
                        "qc_flags": row.get("qc_flags", ""),
                        "split_block_id": block_id,
                        "split": split,
                        "trial_row_sha256": row_sha256(row),
                    }
                )
    return sorted(
        assignments, key=lambda row: (row["session_id"], _to_int(row["trial_index"]))
    )


def assign_blocks(
    session_id: str,
    n_blocks: int,
    train_ratio: float,
    validation_ratio: float,
    _test_ratio: float,
) -> dict[int, str]:
    if n_blocks < 3:
        raise ValueError("need at least three blocks per session")
    n_train = max(1, round(n_blocks * train_ratio))
    n_validation = max(1, round(n_blocks * validation_ratio))
    if n_train + n_validation >= n_blocks:
        n_validation = 1
        n_train = n_blocks - 2
    ranked = sorted(range(n_blocks), key=lambda index: block_hash(session_id, index))
    split_by_block: dict[int, str] = {}
    for rank, block_index in enumerate(ranked):
        if rank < n_train:
            split_by_block[block_index] = "train"
        elif rank < n_train + n_validation:
            split_by_block[block_index] = "validation"
        else:
            split_by_block[block_index] = "test"
    return split_by_block


def block_hash(session_id: str, block_index: int) -> str:
    split_key = f"{SPLIT_VERSION}|{session_id}|block{block_index + 1:03d}"
    return hashlib.sha256(split_key.encode("utf-8")).hexdigest()


def row_sha256(row: Mapping[str, str]) -> str:
    return hashlib.sha256(
        json.dumps(
            dict(sorted(row.items())), sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
    ).hexdigest()


def split_counts(assignments: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    by_split = Counter(row["split"] for row in assignments)
    by_split_outcome = Counter((row["split"], row["outcome"]) for row in assignments)
    split_by_source = {row["source_trial_id"]: row["split"] for row in assignments}
    previous_transitions = Counter(
        (split_by_source[row["previous_source_trial_id"]], row["split"])
        for row in assignments
        if row["previous_source_trial_id"] in split_by_source
    )
    return {
        "total_source_trials": len(assignments),
        "by_split": dict(sorted(by_split.items())),
        "by_split_outcome": {
            "|".join(key): value for key, value in sorted(by_split_outcome.items())
        },
        "previous_trial_split_transitions": {
            "->".join(key): value for key, value in sorted(previous_transitions.items())
        },
    }


def split_counts_by_session(
    assignments: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    counts: dict[tuple[str, str], Counter[str]] = defaultdict(Counter)
    for row in assignments:
        key = (row["session_id"], row["split"])
        counts[key]["trials"] += 1
        counts[key][row["outcome"]] += 1
        counts[key]["qc_flagged"] += 1 if row["qc_flags"] else 0
    return [
        {
            "session_id": session,
            "split": split,
            "trials": counter["trials"],
            "success": counter["success"],
            "timeout": counter["timeout"],
            "qc_flagged": counter["qc_flagged"],
        }
        for (session, split), counter in sorted(counts.items())
    ]


def split_counts_by_marker(
    assignments: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    counts: dict[tuple[str, str, str], Counter[str]] = defaultdict(Counter)
    for row in assignments:
        key = (row["split"], row["marker_minor_digit"], row["outcome"])
        counts[key]["trials"] += 1
        counts[key]["qc_flagged"] += 1 if row["qc_flags"] else 0
    return [
        {
            "split": split,
            "marker_minor_digit": marker,
            "outcome": outcome,
            "trials": counter["trials"],
            "qc_flagged": counter["qc_flagged"],
        }
        for (split, marker, outcome), counter in sorted(counts.items())
    ]


def behavior_audit(
    import_dir: Path, split_dir: Path, output_dir: Path
) -> dict[str, Any]:
    validate_output_dir(output_dir, import_dir)
    output_dir.mkdir(parents=True, exist_ok=False)
    import_summary = read_json(import_dir / "summary.json")
    split_summary = read_json(split_dir / "split_summary.json")
    split_rows = read_csv(split_dir / "source_trial_splits.csv")
    split_by_source = {row["source_trial_id"]: row for row in split_rows}
    design_sources = {
        row["source_trial_id"]
        for row in split_rows
        if row["split"] in {"train", "validation"}
    }
    trials = [
        merge_trial_split(row, split_by_source[row["source_trial_id"]], split_by_source)
        for row in read_csv(import_dir / "trials.csv")
        if row["source_trial_id"] in design_sources
    ]

    trial_path = output_dir / "trial_behavior_qc_train_validation.csv"
    trial_rows = [trial_behavior_row(row) for row in trials]
    write_csv(
        trial_path,
        trial_rows,
        (
            "session_id",
            "source_trial_id",
            "split",
            "trial_index",
            "previous_source_trial_id",
            "previous_source_split",
            "previous_source_in_design_split",
            "marker_minor_digit",
            "inferred_start_marker",
            "task_label_status",
            "outcome",
            "qc_flags",
            "unity_nav_duration_s",
            "unity_path_rows_inclusive",
            "unity_path_distance_axis_units",
            "unity_start_axis1",
            "unity_start_axis2",
            "unity_end_axis1",
            "unity_end_axis2",
        ),
    )
    support_session_path = write_csv(
        output_dir / "support_by_session_split_train_validation.csv",
        behavior_support_by_session(trial_rows),
        (
            "session_id",
            "split",
            "trials",
            "success",
            "timeout",
            "qc_flagged",
            "median_unity_nav_duration_s",
            "median_unity_path_distance_axis_units",
        ),
    )
    support_condition_path = write_csv(
        output_dir / "support_by_inferred_marker_pair_train_validation.csv",
        behavior_support_by_marker_pair(trial_rows),
        (
            "split",
            "inferred_start_marker",
            "marker_minor_digit",
            "outcome",
            "trials",
            "sessions",
            "qc_flagged",
            "median_unity_nav_duration_s",
            "median_unity_path_distance_axis_units",
            "iqr_unity_path_distance_axis_units",
            "median_unity_path_rows_inclusive",
        ),
    )
    qc_path = write_csv(
        output_dir / "qc_flags_train_validation.csv",
        qc_flag_rows(trial_rows),
        ("qc_flag", "trials"),
    )

    run_summary: dict[str, Any] = {
        "created_utc": datetime.now(UTC).isoformat(),
        "status": "passed_with_graph_path_blocked",
        "scientific_status": AUDIT_STATUS,
        "import_dir": str(import_dir),
        "split_dir": str(split_dir),
        "output_dir": str(output_dir),
        "split_hash": split_summary["split_hash"],
        "input_artifact_hashes": import_summary.get("artifact_hashes", {}),
        "selection_list": import_summary.get("selection_list", {}),
        "counts": {
            "train_validation_trials": len(trial_rows),
            "locked_test_trials_not_used_for_path_audit": sum(
                1 for row in split_rows if row["split"] == "test"
            ),
            "train_validation_qc_flagged_trials": sum(
                1 for row in trial_rows if row["qc_flags"]
            ),
            "previous_start_marker_blanked_due_to_locked_test": sum(
                1 for row in trial_rows if row["previous_source_split"] == "test"
            ),
        },
        "guardrails": {
            "test_path_metrics_in_outputs": False,
            "test_derived_previous_labels_in_outputs": False,
            "graph_or_route_family_created": False,
            "uses_unverified_labels_as_verified_start_goal": False,
        },
        "blocked_next_steps": [
            "authoritative maze geometry/adjacency or position-to-node mapping is required before route signatures or edge metrics",
            "marker-to-cue/start/goal semantics require lab confirmation before H1 baselines",
            "recording groups and unit completeness require lab confirmation before neural population claims",
        ],
        "artifact_hashes": {
            trial_path.name: sha256_file(trial_path),
            support_session_path.name: sha256_file(support_session_path),
            support_condition_path.name: sha256_file(support_condition_path),
            qc_path.name: sha256_file(qc_path),
        },
        "code_hashes": {
            "scripts/place195_split_and_behavior_audit.py": sha256_file(Path(__file__))
        },
        "git": git_state(),
        "package_versions": package_versions(),
        "stop_conditions": stop_conditions(),
    }
    write_json(output_dir / "behavior_audit_summary.json", run_summary)
    write_behavior_note(output_dir / "decisions.md", run_summary)
    return run_summary


def merge_trial_split(
    trial: Mapping[str, str],
    split: Mapping[str, str],
    split_by_source: Mapping[str, Mapping[str, str]],
) -> dict[str, str]:
    merged = dict(trial)
    merged["split"] = split["split"]
    previous_id = trial.get("previous_source_trial_id", "")
    previous_split = split_by_source.get(previous_id, {}).get("split", "")
    merged["previous_source_split"] = previous_split
    merged["previous_source_in_design_split"] = str(
        previous_split in {"train", "validation"}
    ).lower()
    return merged


def trial_behavior_row(row: Mapping[str, str]) -> dict[str, Any]:
    return {
        "session_id": row["session_id"],
        "source_trial_id": row["source_trial_id"],
        "split": row["split"],
        "trial_index": row["trial_index"],
        "previous_source_trial_id": row.get("previous_source_trial_id", ""),
        "previous_source_split": row.get("previous_source_split", ""),
        "previous_source_in_design_split": row.get(
            "previous_source_in_design_split", "false"
        ),
        "marker_minor_digit": row.get("marker_minor_digit", ""),
        "inferred_start_marker": (
            row.get("inferred_start_id_from_previous_marker", "")
            if row.get("previous_source_in_design_split") == "true"
            else ""
        ),
        "task_label_status": TASK_LABEL_STATUS,
        "outcome": row.get("outcome", ""),
        "qc_flags": row.get("qc_flags", ""),
        "unity_nav_duration_s": row.get("unity_nav_duration_s", ""),
        "unity_path_rows_inclusive": row.get("unity_path_rows_inclusive", ""),
        "unity_path_distance_axis_units": row.get("unity_path_distance_axis_units", ""),
        "unity_start_axis1": row.get("unity_start_axis1", ""),
        "unity_start_axis2": row.get("unity_start_axis2", ""),
        "unity_end_axis1": row.get("unity_end_axis1", ""),
        "unity_end_axis2": row.get("unity_end_axis2", ""),
    }


def behavior_support_by_session(
    rows: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], list[Mapping[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[(row["session_id"], row["split"])].append(row)
    return [
        {
            "session_id": session,
            "split": split,
            "trials": len(items),
            "success": sum(1 for row in items if row["outcome"] == "success"),
            "timeout": sum(1 for row in items if row["outcome"] == "timeout"),
            "qc_flagged": sum(1 for row in items if row["qc_flags"]),
            "median_unity_nav_duration_s": safe_median(
                row["unity_nav_duration_s"] for row in items
            ),
            "median_unity_path_distance_axis_units": safe_median(
                row["unity_path_distance_axis_units"] for row in items
            ),
        }
        for (session, split), items in sorted(grouped.items())
    ]


def behavior_support_by_marker_pair(
    rows: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, str, str], list[Mapping[str, Any]]] = defaultdict(
        list
    )
    for row in rows:
        grouped[
            (
                row["split"],
                row["inferred_start_marker"],
                row["marker_minor_digit"],
                row["outcome"],
            )
        ].append(row)
    output = []
    for (split, start, marker, outcome), items in sorted(grouped.items()):
        distances = numeric_values(
            row["unity_path_distance_axis_units"] for row in items
        )
        output.append(
            {
                "split": split,
                "inferred_start_marker": start,
                "marker_minor_digit": marker,
                "outcome": outcome,
                "trials": len(items),
                "sessions": len({row["session_id"] for row in items}),
                "qc_flagged": sum(1 for row in items if row["qc_flags"]),
                "median_unity_nav_duration_s": safe_median(
                    row["unity_nav_duration_s"] for row in items
                ),
                "median_unity_path_distance_axis_units": safe_median(distances),
                "iqr_unity_path_distance_axis_units": iqr(distances),
                "median_unity_path_rows_inclusive": safe_median(
                    row["unity_path_rows_inclusive"] for row in items
                ),
            }
        )
    return output


def qc_flag_rows(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    counts: Counter[str] = Counter()
    for row in rows:
        flags = str(row["qc_flags"]).split(";") if row["qc_flags"] else []
        for flag in flags:
            counts[flag] += 1
    return [
        {"qc_flag": flag, "trials": count} for flag, count in sorted(counts.items())
    ]


def numeric_values(values: Iterable[Any]) -> list[float]:
    output = []
    for value in values:
        if value in {None, ""}:
            continue
        output.append(_to_float(value))
    return output


def safe_median(values: Iterable[Any]) -> str | float:
    numbers = numeric_values(values)
    return "" if not numbers else median(numbers)


def iqr(values: Iterable[Any]) -> str | float:
    numbers = sorted(numeric_values(values))
    if len(numbers) < 4:
        return ""
    q1 = numbers[len(numbers) // 4]
    q3 = numbers[(3 * len(numbers)) // 4]
    return q3 - q1


def stop_conditions() -> list[str]:
    return [
        "no H1 modeling until marker-to-cue/start/goal semantics are lab-confirmed",
        "no neural population claim until recording groups and unit completeness are lab-confirmed",
        "no graph/path labels until authoritative geometry or a reviewed position-to-node mapping exists",
        "no route-family construction, PCA, CEBRA, decoder, or target selection before respecting the frozen split hash",
        "do not use locked test behavior to redesign graph granularity, cleaning, exclusions, targets, metrics, or contrasts",
    ]


def write_decisions(path: Path, summary: Mapping[str, Any]) -> None:
    lines = [
        "# Place195 Source-Trial Split Decisions",
        "",
        f"Date: {summary['created_utc']}",
        f"Status: **{summary['scientific_status']}**",
        "",
        "## Split policy",
        "",
        "- Unit: complete `source_trial_id`.",
        "- Scope: within session, using candidate same-session recording group labels only.",
        "- Block: contiguous 20-trial blocks to reduce adjacent-trial leakage.",
        "- Assignment: deterministic SHA-256 ranking of block IDs into 70/15/15 train/validation/test by block.",
        "- Inputs deliberately not used: neural activity, path samples, path metrics, graph labels, route labels, or verified start/goal labels.",
        "",
        f"Split hash: `{summary['split_hash']}`",
        "",
        "## Stop boundary",
        "",
    ]
    lines.extend(f"- {condition}" for condition in stop_conditions())
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_behavior_note(path: Path, summary: Mapping[str, Any]) -> None:
    lines = [
        "# Place195 Train/Validation Behavior QC Audit Decisions",
        "",
        f"Date: {summary['created_utc']}",
        f"Status: **{summary['scientific_status']}**",
        "",
        f"Split hash: `{summary['split_hash']}`",
        "",
        "## Guardrails",
        "",
        "- Only train and validation trials are summarized for path/behavior QC.",
        "- Locked test trials are counted from the split file but not used for behavior/path metrics.",
        "- Previous-trial-derived marker labels are blanked when the previous source trial is locked test.",
        "- Inferred marker fields are not verified start/goal/cue labels.",
        "- No graph, edge metric, route family, model, PCA, CEBRA, or decoder is produced.",
        "",
        "## Blocked next steps",
        "",
    ]
    lines.extend(f"- {item}" for item in summary["blocked_next_steps"])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _csv_value(value: Any) -> str | int | float | bool:
    if value is None:
        return ""
    return value  # type: ignore[return-value]


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    freeze = sub.add_parser("freeze-splits")
    freeze.add_argument("--import-dir", type=Path, default=DEFAULT_IMPORT_DIR)
    freeze.add_argument("--output-dir", type=Path, required=True)
    freeze.add_argument("--block-size", type=int, default=20)

    audit = sub.add_parser("behavior-audit")
    audit.add_argument("--import-dir", type=Path, default=DEFAULT_IMPORT_DIR)
    audit.add_argument("--split-dir", type=Path, required=True)
    audit.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    if args.command == "freeze-splits":
        summary = freeze_place195_splits(
            args.import_dir.resolve(),
            args.output_dir.resolve(),
            block_size=args.block_size,
        )
    elif args.command == "behavior-audit":
        summary = behavior_audit(
            args.import_dir.resolve(),
            args.split_dir.resolve(),
            args.output_dir.resolve(),
        )
    else:  # pragma: no cover
        raise ValueError(f"unknown command: {args.command}")
    print(json.dumps(_jsonable(summary), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
