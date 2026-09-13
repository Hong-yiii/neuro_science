#!/usr/bin/env python3
"""Frozen path-preprocessing protocol implementation.

Implementation-only until code review passes: this module provides reusable CLI
stages and synthetic checks, but biological export/fits require an explicit gate.
The assay is condition-level pseudopopulation decoding for the fixed supported
middle component D_N_C_M__N_C_B within fixed endpoint panels.
"""

# ruff: noqa: E402,I001

from __future__ import annotations

import argparse
import csv
import datetime as dt
import gzip
import hashlib
import importlib.metadata
import itertools
import json
import math
import os
import platform
import random
import shlex
import shutil
import subprocess
import sys
import time
import traceback
from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import numpy as np
from sklearn.linear_model import LogisticRegression

from scripts.place195_split_filtered_access import SplitFilteredAccess
from scripts.place195_v7_v8_neural_experiments import bin_events, session_from_cell

LABELS = ("absent", "present")
LABEL_TO_INT = {"absent": 0, "present": 1}
INT_TO_LABEL = {0: "absent", 1: "present"}
SUPPORTED_MIDDLE_COMPONENT = "D_N_C_M__N_C_B"
EXPECTED_ENDPOINTS = ("2->1", "3->1", "4->1", "5->1", "6->1")
EXPECTED_SUPPORT = {
    "2->1": {
        "train_absent": 6,
        "train_present": 6,
        "validation_absent": 2,
        "validation_present": 1,
        "cells": 2,
        "sessions": 1,
    },
    "3->1": {
        "train_absent": 20,
        "train_present": 11,
        "validation_absent": 7,
        "validation_present": 4,
        "cells": 14,
        "sessions": 3,
    },
    "4->1": {
        "train_absent": 3,
        "train_present": 6,
        "validation_absent": 1,
        "validation_present": 1,
        "cells": 3,
        "sessions": 1,
    },
    "5->1": {
        "train_absent": 14,
        "train_present": 19,
        "validation_absent": 4,
        "validation_present": 4,
        "cells": 12,
        "sessions": 3,
    },
    "6->1": {
        "train_absent": 43,
        "train_present": 19,
        "validation_absent": 9,
        "validation_present": 8,
        "cells": 23,
        "sessions": 6,
    },
}
POINT_INFLUENCE_ENDPOINTS = {"2->1", "4->1"}
ROUND1_TEMPORAL_BINS = (1, 2, 5)
TRANSFORMS = ("raw_rate", "sqrt_rate", "log1p_rate")
SCALERS = ("standard", "variance_floor")
ROUND1_LAMBDA = 0.1
ROUND2_EXTRA_LAMBDAS = (0.01, 1.0)
PRIMARY_SEED = 0
SENSITIVITY_SEEDS = (1, 2)
ROWS_PER_CLASS = 128
MAX_EVAL_COMBINATIONS_PER_CLASS = 10_000
SAMPLED_EVAL_ROWS_PER_CLASS = 2_048
REVIEW_GATE_TOKEN = "reviewed-code-data-gate"
FINAL_REVIEW_GATE_TOKEN = "reviewed-final-inference-gate"
OWNED_OUTPUT_ROOT = Path("outputs/path-preprocessing-autoresearch-20260908")
MANAGER_ROOT = REPO_ROOT / "outputs/path-autoresearch-management-20260908"
FROZEN_SELECTED_SOURCES_SHA256 = (
    "36c72e8f1f9c55ca3af9458963cf1e1062c8803cb57b33af29df4502e46c2b2f"
)
# ponytail: one CLI stage per process; use a passed logger if stages become concurrent.
ACTIVE_PROGRESS_PATH: Path | None = None
FIT_COUNT = 0
THREAD_ENV_KEYS = (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
)


@dataclass(frozen=True)
class SourceRecord:
    source_trial_id: str
    session_id: str
    split: str
    endpoint_pair: str
    label: str
    inner_fold: int
    trial_index: int
    cue_duration_s: float
    cell_ids: tuple[str, ...]
    qc_flags: str = ""
    supported_middle_component_id: str = SUPPORTED_MIDDLE_COMPONENT
    candidate_recording_group: str = ""
    simultaneity_status: str = ""


@dataclass(frozen=True)
class Candidate:
    temporal_bins: int
    transform: str
    scaler: str
    lambda_l2: float = ROUND1_LAMBDA
    projection: str = "none"

    def __post_init__(self) -> None:
        if self.projection not in {"none", "pca90"}:
            raise ValueError(f"unknown projection {self.projection}")

    @property
    def representation_key(self) -> str:
        base = f"t{self.temporal_bins}_{self.transform}_{self.scaler}"
        return base if self.projection == "none" else f"{base}_{self.projection}"

    @property
    def key(self) -> str:
        lam = f"{self.lambda_l2:g}".replace(".", "p")
        return f"{self.representation_key}_l2_{lam}"

    def as_dict(self) -> dict[str, Any]:
        return {
            "temporal_bins": self.temporal_bins,
            "transform": self.transform,
            "scaler": self.scaler,
            "lambda_l2": self.lambda_l2,
            "representation_key": self.representation_key,
            "candidate_key": self.key,
            **({"projection": self.projection} if self.projection != "none" else {}),
        }


@dataclass(frozen=True)
class FeatureScaler:
    kind: str
    mean: np.ndarray
    scale: np.ndarray
    floor: float
    floored_fraction: float


@dataclass(frozen=True)
class FittedCandidate:
    candidate: Candidate
    scaler: FeatureScaler
    model: LogisticRegression
    projection: dict[str, Any] | None = None


@dataclass(frozen=True)
class SourceTensor:
    X: np.ndarray
    E: np.ndarray
    M: np.ndarray
    records: tuple[SourceRecord, ...]
    cell_ids: tuple[str, ...]
    audit: dict[str, Any]


@dataclass(frozen=True)
class RowBundle:
    X_counts: np.ndarray
    E: np.ndarray
    y: np.ndarray
    weights: np.ndarray
    manifest: list[dict[str, Any]]
    support: dict[str, Any]


# ---------- small IO/provenance helpers ----------


def jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [jsonable(v) for v in value]
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, (np.bool_,)):
        return bool(value)
    return value


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(jsonable(payload), indent=2, sort_keys=True) + "\n"
    if path.suffix == ".gz":
        with gzip.open(path, "wt", encoding="utf-8") as handle:
            handle.write(text)
    else:
        path.write_text(text, encoding="utf-8")


def read_json(path: Path) -> Any:
    if path.suffix == ".gz":
        with gzip.open(path, "rt", encoding="utf-8") as handle:
            return json.load(handle)
    return json.loads(path.read_text(encoding="utf-8"))


def open_text(path: Path, mode: str = "rt"):
    if path.suffix == ".gz":
        return gzip.open(path, mode, encoding="utf-8", newline="")
    return (
        path.open(mode.replace("t", ""), encoding="utf-8", newline="")
        if "b" not in mode
        else path.open(mode)
    )


def write_csv(
    path: Path,
    rows: Sequence[Mapping[str, Any]],
    fieldnames: Sequence[str] | None = None,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if fieldnames is None:
        keys: list[str] = []
        for row in rows:
            for key in row:
                if key not in keys:
                    keys.append(str(key))
        fieldnames = keys
    with (
        gzip.open(path, "wt", encoding="utf-8", newline="")
        if path.suffix == ".gz"
        else path.open("w", encoding="utf-8", newline="")
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fieldnames))
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    k: json.dumps(jsonable(v), sort_keys=True)
                    if isinstance(v, (dict, list, tuple))
                    else v
                    for k, v in row.items()
                }
            )


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_path(path: Path) -> str:
    path = path.resolve()
    if path.is_file():
        return sha256_file(path)
    h = hashlib.sha256()
    for child in sorted(p for p in path.rglob("*") if p.is_file()):
        rel = child.relative_to(path).as_posix()
        h.update(rel.encode("utf-8"))
        h.update(b"\0")
        h.update(sha256_file(child).encode("ascii"))
        h.update(b"\n")
    return h.hexdigest()


def append_jsonl(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(jsonable(payload), sort_keys=True) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def append_jsonl_gz(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, "at", encoding="utf-8") as handle:
        handle.write(json.dumps(jsonable(payload), sort_keys=True) + "\n")


def stable_hash(payload: Any) -> str:
    encoded = json.dumps(
        jsonable(payload), sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def ndarray_sha256(array: np.ndarray) -> str:
    arr = np.ascontiguousarray(array)
    h = hashlib.sha256()
    h.update(str(arr.dtype).encode("utf-8"))
    h.update(str(arr.shape).encode("utf-8"))
    h.update(arr.tobytes())
    return h.hexdigest()


def git(cmd: Sequence[str]) -> str:
    try:
        return subprocess.check_output(
            ["git", *cmd], text=True, stderr=subprocess.STDOUT
        ).strip()
    except Exception as exc:  # pragma: no cover - provenance must not kill analysis
        return f"unavailable: {exc}"


def _package_version(name: str) -> str:
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return "unavailable"


def _owned_output_root() -> Path:
    return (REPO_ROOT / OWNED_OUTPUT_ROOT).resolve()


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def prepare_cli_output_dir(path: Path) -> Path:
    resolved = path.resolve()
    root = _owned_output_root()
    if not _is_relative_to(resolved, root):
        raise ValueError(f"output_dir must resolve under {root}: {resolved}")
    if resolved.exists():
        raise FileExistsError(
            f"output_dir already exists; use a unique run dir: {resolved}"
        )
    resolved.mkdir(parents=True, exist_ok=False)
    return resolved


def ensure_empty_output_dir(path: Path) -> None:
    # main exclusively creates a fresh directory and writes this receipt first.
    if path.exists() and any(p.name != "command_start.json" for p in path.iterdir()):
        raise FileExistsError(f"output_dir is non-empty; refusing to clobber: {path}")
    path.mkdir(parents=True, exist_ok=True)


def record_progress(event: str, **payload: Any) -> None:
    if ACTIVE_PROGRESS_PATH is not None:
        row = {
            "event": event,
            "utc": dt.datetime.now(dt.timezone.utc).isoformat(),
            **payload,
        }
        append_jsonl(ACTIVE_PROGRESS_PATH, row)
        print(json.dumps(jsonable(row), sort_keys=True), flush=True)


def input_paths_for_args(args: argparse.Namespace) -> dict[str, Path]:
    paths: dict[str, Path] = {}
    for name in (
        "source_tensor",
        "selected_sources",
        "round1_summary",
        "round2_summary",
        "support_audit",
        "import_dir",
        "split_dir",
    ):
        value = getattr(args, name, None)
        if isinstance(value, Path):
            if name == "import_dir":
                for filename in ("cue_counts.csv.gz", "cue_spike_events.csv.gz"):
                    paths[f"import_{filename}"] = value / filename
            elif name == "split_dir":
                for filename in ("source_trial_splits.csv", "split_summary.json"):
                    paths[f"split_{filename}"] = value / filename
            else:
                paths[name] = value
    protocol = MANAGER_ROOT / "PROTOCOL-FROZEN-V1.md"
    if protocol.exists():
        paths["protocol_frozen_v1"] = protocol
    selection = MANAGER_ROOT / "SELECTION-FROZEN.json"
    if selection.exists():
        paths["selection_frozen"] = selection
    return paths


def _module_path(obj: Any) -> Path | None:
    filename = getattr(sys.modules[obj.__module__], "__file__", None)
    return Path(filename) if filename else None


def runtime_manifest(
    command: Sequence[str], input_paths: Mapping[str, Path] | None = None
) -> dict[str, Any]:
    paths = input_paths or {}
    code_paths = {
        "driver": Path(__file__),
        "split_filtered_access": _module_path(SplitFilteredAccess),
        "v7_v8_neural_helpers": _module_path(bin_events),
    }
    return {
        "created_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "command": " ".join(shlex.quote(str(x)) for x in command),
        "argv": [str(x) for x in command],
        "python": sys.version,
        "platform": platform.platform(),
        "device": "CPU",
        "thread_env": {k: os.environ.get(k, "") for k in THREAD_ENV_KEYS},
        "package_versions": {
            "numpy": np.__version__,
            "scipy": _package_version("scipy"),
            "scikit-learn": _package_version("scikit-learn"),
        },
        "sklearn_logistic_regression": str(LogisticRegression),
        "git_head": git(["rev-parse", "HEAD"]),
        "git_dirty": bool(git(["status", "--short"])),
        "git_status_short": git(["status", "--short"]),
        "code_hashes": {
            name: sha256_file(path.resolve())
            for name, path in code_paths.items()
            if path is not None and path.exists()
        },
        "input_hashes": {
            name: sha256_path(path) for name, path in paths.items() if path.exists()
        },
    }


def require_authorization(token: str | None, operation: str) -> None:
    if token != REVIEW_GATE_TOKEN:
        raise PermissionError(
            f"{operation} requires code-review gate token; implementation/synthetic checks only before approval"
        )


def _validate_repo_imports() -> None:
    repo = Path(__file__).resolve().parents[1]
    for obj in (SplitFilteredAccess, bin_events):
        module = sys.modules[obj.__module__]
        module_path = Path(getattr(module, "__file__", "")).resolve()
        if repo not in module_path.parents:
            raise RuntimeError(f"unexpected module path for {obj}: {module_path}")


# ---------- protocol metadata/support ----------


def _parse_record(row: Mapping[str, Any]) -> SourceRecord:
    cells = row.get("cell_ids", ())
    if not isinstance(cells, (list, tuple)):
        raise ValueError(f"cell_ids must be a list for {row.get('source_trial_id')}")
    return SourceRecord(
        source_trial_id=str(row["source_trial_id"]),
        session_id=str(row["session_id"]),
        split=str(row["split"]),
        endpoint_pair=str(row["endpoint_pair"]),
        label=str(row["supported_middle_component_label"]),
        inner_fold=int(row["inner_fold"]),
        trial_index=int(row["trial_index"]),
        cue_duration_s=float(row["cue_duration_s"]),
        cell_ids=tuple(str(c) for c in cells),
        qc_flags=str(row.get("qc_flags", "")),
        supported_middle_component_id=str(
            row.get("supported_middle_component_id", SUPPORTED_MIDDLE_COMPONENT)
        ),
        candidate_recording_group=str(row.get("candidate_recording_group", "")),
        simultaneity_status=str(row.get("simultaneity_status", "")),
    )


def require_frozen_selected_sources_hash(path: Path) -> None:
    got = sha256_file(path)
    if got != FROZEN_SELECTED_SOURCES_SHA256:
        raise ValueError(
            "selected sources SHA256 mismatch: "
            f"{got} != {FROZEN_SELECTED_SOURCES_SHA256}"
        )


def load_selected_source_records(
    path: Path, *, strict_expected: bool = False
) -> tuple[SourceRecord, ...]:
    if strict_expected:
        require_frozen_selected_sources_hash(path)
    rows = read_json(path)
    if not isinstance(rows, list):
        raise ValueError("selected sources manifest must be a JSON list")
    records = tuple(_parse_record(row) for row in rows)
    validate_source_records(records, strict_expected=strict_expected)
    return records


def validate_source_records(
    records: Sequence[SourceRecord], *, strict_expected: bool = True
) -> None:
    if not records:
        raise ValueError("no source records")
    seen: set[str] = set()
    for rec in records:
        if rec.source_trial_id in seen:
            raise ValueError(f"duplicate source_trial_id {rec.source_trial_id!r}")
        seen.add(rec.source_trial_id)
        if rec.split not in {"train", "validation"}:
            raise ValueError(
                f"forbidden split retained for {rec.source_trial_id}: {rec.split}"
            )
        if rec.label not in LABELS:
            raise ValueError(f"bad label for {rec.source_trial_id}: {rec.label}")
        if rec.supported_middle_component_id != SUPPORTED_MIDDLE_COMPONENT:
            raise ValueError(
                f"wrong component for {rec.source_trial_id}: {rec.supported_middle_component_id}"
            )
        if rec.qc_flags:
            raise ValueError(
                f"non-empty qc_flags for selected source {rec.source_trial_id}"
            )
        if not (1.0 <= rec.cue_duration_s <= 1.5):
            raise ValueError(
                f"cue duration outside [1,1.5] for {rec.source_trial_id}: {rec.cue_duration_s}"
            )
        expected_fold = -1 if rec.split == "validation" else rec.inner_fold
        if rec.split == "validation" and rec.inner_fold != -1:
            raise ValueError(
                f"validation source has inner_fold != -1: {rec.source_trial_id}"
            )
        if rec.split == "train" and rec.inner_fold not in {0, 1, 2}:
            raise ValueError(
                f"train source has bad inner fold: {rec.source_trial_id} {expected_fold}"
            )
        if not rec.cell_ids:
            raise ValueError(f"selected source has no cell_ids: {rec.source_trial_id}")
        bad_session = [
            c for c in rec.cell_ids if session_from_cell(c) != rec.session_id
        ]
        if bad_session:
            raise ValueError(
                f"cell/session join mismatch for {rec.source_trial_id}: {bad_session[:3]}"
            )
    if strict_expected:
        summary = support_summary(records)
        if summary["train_sources"] != 147 or summary["validation_sources"] != 41:
            raise ValueError(
                f"selected-source count mismatch: {summary['train_sources']} train / {summary['validation_sources']} validation"
            )
        if summary["unique_cells"] != 49 or summary["unique_sessions"] != 13:
            raise ValueError(
                f"scope mismatch: {summary['unique_cells']} cells / {summary['unique_sessions']} sessions"
            )
        got_eps = tuple(row["endpoint_pair"] for row in summary["panels"])
        if got_eps != EXPECTED_ENDPOINTS:
            raise ValueError(f"endpoint set mismatch: {got_eps}")
        for panel in summary["panels"]:
            expected = EXPECTED_SUPPORT[panel["endpoint_pair"]]
            for key, value in expected.items():
                if panel[key] != value:
                    raise ValueError(
                        f"support mismatch {panel['endpoint_pair']} {key}: {panel[key]} != {value}"
                    )
        _validate_inner_fold_coverage(records)


def _validate_inner_fold_coverage(records: Sequence[SourceRecord]) -> None:
    grouped: dict[tuple[str, str, str], set[int]] = defaultdict(set)
    for rec in records:
        if rec.split == "train":
            grouped[(rec.session_id, rec.endpoint_pair, rec.label)].add(rec.inner_fold)
    missing = {
        key: sorted({0, 1, 2} - folds)
        for key, folds in grouped.items()
        if folds != {0, 1, 2}
    }
    if missing:
        raise ValueError(
            f"inner folds do not cover 0/1/2 for every train session×endpoint×label pool: {missing}"
        )


def support_summary(records: Sequence[SourceRecord]) -> dict[str, Any]:
    panels = []
    for endpoint in sorted({r.endpoint_pair for r in records}):
        ers = [r for r in records if r.endpoint_pair == endpoint]
        counts = Counter((r.split, r.label) for r in ers)
        panels.append(
            {
                "endpoint_pair": endpoint,
                "train_absent": counts[("train", "absent")],
                "train_present": counts[("train", "present")],
                "validation_absent": counts[("validation", "absent")],
                "validation_present": counts[("validation", "present")],
                "sources": len(ers),
                "cells": len({c for r in ers for c in r.cell_ids}),
                "sessions": len({r.session_id for r in ers}),
                "interval_grade": "point_influence_only"
                if endpoint in POINT_INFLUENCE_ENDPOINTS
                else "source_resampling_sensitivity_only",
            }
        )
    return {
        "component": SUPPORTED_MIDDLE_COMPONENT,
        "source_count": len(records),
        "train_sources": sum(r.split == "train" for r in records),
        "validation_sources": sum(r.split == "validation" for r in records),
        "unique_cells": len({c for r in records for c in r.cell_ids}),
        "unique_sessions": len({r.session_id for r in records}),
        "panels": panels,
        "inner_fold_policy": "frozen prefit-selected-sources.json; train folds 0/1/2, validation -1",
    }


def verify_prefit_support(
    selected_sources_path: Path, support_audit_path: Path | None = None
) -> dict[str, Any]:
    records = load_selected_source_records(selected_sources_path)
    validate_source_records(records, strict_expected=True)
    summary = support_summary(records)
    if support_audit_path is not None:
        audit = read_json(support_audit_path)
        selected = audit.get("selected_sources", {}) if isinstance(audit, dict) else {}
        if selected.get("train") != 147 or selected.get("validation") != 41:
            raise ValueError(f"support audit selected counts mismatch: {selected}")
        summary["support_audit_sha256"] = sha256_file(support_audit_path)
        summary["two_duration_exclusions"] = [
            r.get("source_trial_id")
            for r in audit.get("removed_from_fixed_contexts", [])
        ]
    summary["selected_sources_sha256"] = sha256_file(selected_sources_path)
    summary["selected_sources_stable_hash"] = stable_hash(
        [record_to_json(r) for r in records]
    )
    return summary


def record_to_json(record: SourceRecord) -> dict[str, Any]:
    return {
        "source_trial_id": record.source_trial_id,
        "session_id": record.session_id,
        "split": record.split,
        "endpoint_pair": record.endpoint_pair,
        "supported_middle_component_label": record.label,
        "inner_fold": record.inner_fold,
        "trial_index": record.trial_index,
        "cue_duration_s": record.cue_duration_s,
        "cell_ids": list(record.cell_ids),
        "qc_flags": record.qc_flags,
        "supported_middle_component_id": record.supported_middle_component_id,
        "candidate_recording_group": record.candidate_recording_group,
        "simultaneity_status": record.simultaneity_status,
    }


# ---------- guarded binned export ----------


def _field(row: Mapping[str, str], *names: str, default: str = "") -> str:
    for name in names:
        if name in row and row[name] != "":
            return row[name]
    return default


def _event_time(row: Mapping[str, str]) -> float:
    return float(
        _field(row, "cue_relative_time_s", "relative_time_s", "spike_time_relative_s")
    )


def _count_duration(row: Mapping[str, str]) -> float:
    if "cue_duration_s" in row and row["cue_duration_s"]:
        return float(row["cue_duration_s"])
    return float(row["cue_window_end_ripple_s"]) - float(
        row["cue_window_start_ripple_s"]
    )


def _integer_count(value: str, *, field: str) -> int:
    number = float(value)
    if not math.isfinite(number) or number < 0 or abs(number - round(number)) > 1e-9:
        raise ValueError(f"{field} must be a nonnegative integer, got {value!r}")
    return int(round(number))


def _row_metadata_mismatches(
    row: Mapping[str, str],
    rec: SourceRecord,
    *,
    access: SplitFilteredAccess,
    cell_id: str,
    duration: float | None = None,
) -> list[dict[str, Any]]:
    mismatches: list[dict[str, Any]] = []

    def check(field: str, got: Any, expected: Any) -> None:
        if str(got) != str(expected):
            mismatches.append(
                {
                    "source_trial_id": rec.source_trial_id,
                    "cell_id": cell_id,
                    "field": field,
                    "got": got,
                    "expected": expected,
                }
            )

    check("split", row.get("split", ""), rec.split)
    if "session_id" in row and row.get("session_id"):
        check("session_id", row.get("session_id", ""), rec.session_id)
    else:
        check("session_id_from_cell", session_from_cell(cell_id), rec.session_id)
    if "trial_index" in row and row.get("trial_index"):
        check("trial_index", int(row["trial_index"]), rec.trial_index)
    if duration is not None and not math.isclose(
        duration, rec.cue_duration_s, rel_tol=0.0, abs_tol=1e-6
    ):
        check("cue_duration_s", duration, rec.cue_duration_s)

    split_meta = access.split_metadata_by_source.get(rec.source_trial_id, {})
    for source, prefix in ((row, "row"), (split_meta, "split_manifest")):
        if "qc_flags" in source:
            check(f"{prefix}.qc_flags", source.get("qc_flags", ""), rec.qc_flags)
        if "candidate_recording_group" in source:
            check(
                f"{prefix}.candidate_recording_group",
                source.get("candidate_recording_group", ""),
                rec.candidate_recording_group,
            )
        if "simultaneity_status" in source:
            check(
                f"{prefix}.simultaneity_status",
                source.get("simultaneity_status", ""),
                rec.simultaneity_status,
            )
    if "session_id" in split_meta:
        check(
            "split_manifest.session_id",
            split_meta.get("session_id", ""),
            rec.session_id,
        )
    if "trial_index" in split_meta and split_meta.get("trial_index"):
        check(
            "split_manifest.trial_index",
            int(split_meta["trial_index"]),
            rec.trial_index,
        )
    return mismatches


def _raise_metadata_mismatch(
    output_dir: Path, mismatches: Sequence[Mapping[str, Any]]
) -> None:
    write_json(output_dir / "accessor_metadata_mismatch_audit.json", list(mismatches))
    raise ValueError(
        f"accessor metadata mismatch for selected source/cell rows: {list(mismatches)[:3]}"
    )


def export_binned_cue_counts(
    *,
    import_dir: Path,
    split_dir: Path,
    selected_sources_path: Path,
    output_dir: Path,
    authorized_phase: str | None,
    strict_expected: bool = True,
) -> dict[str, Any]:
    require_authorization(authorized_phase, "guarded binned cue export")
    _validate_repo_imports()
    ensure_empty_output_dir(output_dir)
    started = time.time()
    records = load_selected_source_records(
        selected_sources_path, strict_expected=strict_expected
    )
    by_source = {r.source_trial_id: r for r in records}
    allowed_cells_by_source = {r.source_trial_id: set(r.cell_ids) for r in records}
    all_cells = tuple(sorted({c for r in records for c in r.cell_ids}))
    cell_index = {c: i for i, c in enumerate(all_cells)}
    source_index = {r.source_trial_id: i for i, r in enumerate(records)}
    access = SplitFilteredAccess(
        import_dir, split_dir, allowed_splits=("train", "validation")
    )

    events: dict[tuple[str, str], list[float]] = defaultdict(list)
    skipped_event_unselected_source = 0
    skipped_event_unselected_cell = 0
    for row in access.iter_cue_spike_events():
        sid = row["source_trial_id"]
        if sid not in by_source:
            skipped_event_unselected_source += 1
            continue
        cid = row.get("cell_id", "")
        if cid not in allowed_cells_by_source[sid]:
            skipped_event_unselected_cell += 1
            continue
        rec = by_source[sid]
        mismatches = _row_metadata_mismatches(row, rec, access=access, cell_id=cid)
        if mismatches:
            _raise_metadata_mismatch(output_dir, mismatches)
        events[(sid, cid)].append(_event_time(row))

    X = np.full((len(records), len(all_cells), 10), np.nan, dtype=np.float32)
    E = np.full((len(records), len(all_cells), 10), np.nan, dtype=np.float32)
    M = np.zeros((len(records), len(all_cells)), dtype=bool)
    long_rows: list[dict[str, Any]] = []
    tail_rows: list[dict[str, Any]] = []
    conservation_failures: list[dict[str, Any]] = []
    durations: list[float] = []
    seen_pairs: set[tuple[str, str]] = set()
    skipped_unselected_source_rows = 0
    skipped_unselected_cell_rows = 0
    for row in access.iter_cue_counts():
        sid = row["source_trial_id"]
        if sid not in by_source:
            skipped_unselected_source_rows += 1
            continue
        cid = row.get("cell_id", "")
        if cid not in allowed_cells_by_source[sid]:
            skipped_unselected_cell_rows += 1
            continue
        key = (sid, cid)
        if key in seen_pairs:
            raise ValueError(f"duplicate cue count row for selected source/cell {key}")
        seen_pairs.add(key)
        rec = by_source[sid]
        duration = _count_duration(row)
        mismatches = _row_metadata_mismatches(
            row, rec, access=access, cell_id=cid, duration=duration
        )
        if mismatches:
            _raise_metadata_mismatch(output_dir, mismatches)
        if not (1.0 <= duration <= 1.5):
            raise ValueError(
                f"selected source/cell duration outside [1,1.5] for {key}: {duration}"
            )
        count_full = _integer_count(
            _field(row, "cue_spike_count", "spike_count"), field="cue_spike_count"
        )
        ev = events.get(key, [])
        full_events = sum(1 for t in ev if 0.0 <= t < duration)
        counts, exposure, omitted = bin_events(ev, duration, 0.1, nominal=1.0)
        if full_events != count_full or int(counts.sum() + omitted) != count_full:
            conservation_failures.append(
                {
                    "source_trial_id": sid,
                    "cell_id": cid,
                    "full_events": full_events,
                    "cue_spike_count": count_full,
                    "canonical_0_1_count": int(counts.sum()),
                    "tail_1_to_duration_count": int(omitted),
                }
            )
        si = source_index[sid]
        ci = cell_index[cid]
        X[si, ci, :] = counts
        E[si, ci, :] = exposure
        M[si, ci] = True
        durations.append(duration)
        for b in range(10):
            long_rows.append(
                {
                    "source_trial_id": sid,
                    "session_id": rec.session_id,
                    "split": rec.split,
                    "trial_index": rec.trial_index,
                    "endpoint_pair": rec.endpoint_pair,
                    "start_id": rec.endpoint_pair.split("->")[0],
                    "goal_id": rec.endpoint_pair.split("->")[1],
                    "component_id": SUPPORTED_MIDDLE_COMPONENT,
                    "supported_middle_component_id": SUPPORTED_MIDDLE_COMPONENT,
                    "supported_middle_component_label": rec.label,
                    "inner_fold": rec.inner_fold,
                    "cell_id": cid,
                    "cue_bin_100ms": b,
                    "bin_start_s": b / 10,
                    "bin_end_s": (b + 1) / 10,
                    "spike_count": int(counts[b]),
                    "exposure_s": float(exposure[b]),
                    "tail_spike_count_1s_to_cue_end": int(omitted),
                    "full_cue_spike_count": count_full,
                    "candidate_recording_group": rec.candidate_recording_group,
                    "simultaneity_status": rec.simultaneity_status,
                    "qc_flags": rec.qc_flags,
                }
            )
        tail_rows.append(
            {
                "source_trial_id": sid,
                "session_id": rec.session_id,
                "endpoint_pair": rec.endpoint_pair,
                "cell_id": cid,
                "cue_duration_s": duration,
                "canonical_0_1_count": int(counts.sum()),
                "tail_spike_count_1s_to_cue_end": int(omitted),
                "full_cue_spike_count": count_full,
            }
        )
    if conservation_failures:
        raise ValueError(
            f"cue event/count conservation failed: {conservation_failures[:3]}"
        )
    missing = []
    for rec in records:
        si = source_index[rec.source_trial_id]
        for cid in rec.cell_ids:
            if not M[si, cell_index[cid]]:
                missing.append((rec.source_trial_id, cid))
    if missing:
        raise RuntimeError(
            f"missing selected same-source cell count rows: {missing[:3]}"
        )

    binned_path = output_dir / "development_binned_cue_counts.csv.gz"
    tail_path = output_dir / "cue_tail_count_conservation.csv.gz"
    tensor_path = output_dir / "source_tensors.npz"
    write_csv(binned_path, long_rows)
    write_csv(tail_path, tail_rows)
    np.savez_compressed(
        tensor_path,
        X_source_cell_bin=X,
        exposure_source_cell_bin=E,
        observed_source_cell_mask=M,
        source_records_json=np.array(
            [json.dumps(record_to_json(r), sort_keys=True) for r in records]
        ),
        cell_ids=np.array(all_cells),
        bin_edges_s=np.linspace(0.0, 1.0, 11, dtype=np.float32),
        frozen_selected_sources_sha256=np.array(sha256_file(selected_sources_path)),
        source_record_hash=np.array(stable_hash([record_to_json(r) for r in records])),
    )
    manifest = {
        "stage": "guarded_binned_cue_export",
        "status": "complete",
        "claim_ceiling": "condition-level pseudopopulation preprocessing input; physical stream may contain skipped test rows but SplitFilteredAccess yields only train/validation",
        "elapsed_seconds": time.time() - started,
        "selected_sources": len(records),
        "unique_cells": len(all_cells),
        "binned_rows": len(long_rows),
        "tail_rows": len(tail_rows),
        "skipped_unselected_source_rows": skipped_unselected_source_rows,
        "skipped_unselected_cell_rows": skipped_unselected_cell_rows,
        "skipped_event_unselected_source_rows": skipped_event_unselected_source,
        "skipped_event_unselected_cell_rows": skipped_event_unselected_cell,
        "forbidden_rows_yielded": access.audit.as_dict()["forbidden_rows_yielded"],
        "split_access_audit": access.audit.as_dict(),
        "duration_s_min": min(durations) if durations else None,
        "duration_s_max": max(durations) if durations else None,
        "half_open_bins": "canonical ten 100 ms bins include 0 <= t < 1.0; t==1.0 belongs to saved tail if cue duration extends past 1s",
        "outputs": {
            "binned_counts": binned_path,
            "tail_counts": tail_path,
            "source_tensor_npz": tensor_path,
        },
        "hashes": {
            "selected_sources_sha256": sha256_file(selected_sources_path),
            "expected_selected_sources_sha256": FROZEN_SELECTED_SOURCES_SHA256,
            "source_record_hash": stable_hash([record_to_json(r) for r in records]),
            "binned_counts_sha256": sha256_file(binned_path),
            "tail_counts_sha256": sha256_file(tail_path),
            "source_tensor_sha256": sha256_file(tensor_path),
            "input_file_hashes": {
                str(p): sha256_file(p)
                for p in (
                    import_dir / "cue_counts.csv.gz",
                    import_dir / "cue_spike_events.csv.gz",
                    split_dir / "source_trial_splits.csv",
                    split_dir / "split_summary.json",
                )
            },
        },
    }
    write_json(output_dir / "export_manifest.json", manifest)
    return manifest


# ---------- source tensor loading/saving ----------


def load_source_tensor(
    path: Path, *, strict_expected: bool = False, selected_sources_path: Path | None = None
) -> SourceTensor:
    with np.load(path, allow_pickle=False) as npz:
        X = np.asarray(npz["X_source_cell_bin"], dtype=np.float32)
        M = np.asarray(npz["observed_source_cell_mask"], dtype=bool)
        if "exposure_source_cell_bin" in npz:
            E = np.asarray(npz["exposure_source_cell_bin"], dtype=np.float32)
        else:
            Ebin = np.asarray(npz["exposure_source_bin"], dtype=np.float32)
            E = np.broadcast_to(Ebin[:, None, :], X.shape).copy()
        records = tuple(
            _parse_record(json.loads(str(s))) for s in npz["source_records_json"]
        )
        cell_ids = tuple(str(c) for c in npz["cell_ids"])
    if X.shape != E.shape or X.shape[:2] != M.shape or X.shape[2] != 10:
        raise ValueError(
            f"bad source tensor shapes X={X.shape} E={E.shape} M={M.shape}"
        )
    if X.shape[0] != len(records) or X.shape[1] != len(cell_ids):
        raise ValueError("source tensor metadata length mismatch")
    _validate_masks_no_zero_fill(X, E, M)
    validate_source_records(records, strict_expected=strict_expected)
    if strict_expected:
        expected = load_selected_source_records(
            selected_sources_path or MANAGER_ROOT / "prefit-selected-sources.json",
            strict_expected=True,
        )
        if records != expected or cell_ids != tuple(
            sorted({c for r in expected for c in r.cell_ids})
        ):
            raise ValueError(
                "source tensor metadata does not match the pinned source/fold/cell manifest"
            )
        expected_mask = np.array(
            [[c in rec.cell_ids for c in cell_ids] for rec in records]
        )
        if not np.array_equal(M, expected_mask):
            raise ValueError(
                "source tensor availability mask differs from the pinned observations"
            )
        if not np.allclose(E[M], 0.1, rtol=0, atol=1e-7):
            raise ValueError(
                "source tensor exposure must be ten fully observed 100ms bins"
            )
        if (
            not np.isfinite(X[M]).all()
            or (X[M] < 0).any()
            or not np.equal(X[M], np.floor(X[M])).all()
        ):
            raise ValueError(
                "source tensor observed counts must be finite nonnegative integers"
            )
        receipt = read_json(path.parent / "export_manifest.json")
        if receipt["hashes"]["source_tensor_sha256"] != sha256_file(path):
            raise ValueError(
                "source tensor hash differs from its guarded export receipt"
            )
        if (
            receipt["hashes"]["selected_sources_sha256"]
            != FROZEN_SELECTED_SOURCES_SHA256
        ):
            raise ValueError("export receipt used an unapproved source allowlist")
    return SourceTensor(
        X=X,
        E=E,
        M=M,
        records=records,
        cell_ids=cell_ids,
        audit={"source_tensor_sha256": sha256_file(path)},
    )


def save_source_tensor(path: Path, tensor: SourceTensor) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        path,
        X_source_cell_bin=tensor.X.astype(np.float32),
        exposure_source_cell_bin=tensor.E.astype(np.float32),
        observed_source_cell_mask=tensor.M,
        source_records_json=np.array(
            [json.dumps(record_to_json(r), sort_keys=True) for r in tensor.records]
        ),
        cell_ids=np.array(tensor.cell_ids),
        bin_edges_s=np.linspace(0.0, 1.0, 11, dtype=np.float32),
    )


def _validate_masks_no_zero_fill(X: np.ndarray, E: np.ndarray, M: np.ndarray) -> None:
    if np.isnan(X[M]).any() or np.isnan(E[M]).any():
        raise ValueError("observed source/cell entries contain NaN")
    if not np.isnan(X[~M]).all() or not np.isnan(E[~M]).all():
        raise ValueError(
            "unobserved source/cell entries must remain NaN, not zero-filled"
        )


def subset_tensor(
    tensor: SourceTensor, endpoint: str, records: Sequence[SourceRecord] | None = None
) -> SourceTensor:
    base_records = tuple(
        r
        for r in (records if records is not None else tensor.records)
        if r.endpoint_pair == endpoint
    )
    if not base_records:
        raise ValueError(f"no records for endpoint {endpoint}")
    source_pos = {r.source_trial_id: i for i, r in enumerate(tensor.records)}
    rows = [source_pos[r.source_trial_id] for r in base_records]
    endpoint_cells = tuple(sorted({c for r in base_records for c in r.cell_ids}))
    global_cell_pos = {c: i for i, c in enumerate(tensor.cell_ids)}
    cols = [global_cell_pos[c] for c in endpoint_cells]
    return SourceTensor(
        X=tensor.X[np.ix_(rows, cols, range(tensor.X.shape[2]))],
        E=tensor.E[np.ix_(rows, cols, range(tensor.E.shape[2]))],
        M=tensor.M[np.ix_(rows, cols)],
        records=base_records,
        cell_ids=endpoint_cells,
        audit=tensor.audit,
    )


# ---------- pseudo rows / exact products ----------


def _records_by_session_label(
    records: Sequence[SourceRecord],
    *,
    split: str,
    label: str,
    fold_mode: str,
    fold: int | None,
    shuffled_labels: Mapping[str, str] | None = None,
) -> dict[str, list[int]]:
    sessions = sorted({r.session_id for r in records})
    out: dict[str, list[int]] = {s: [] for s in sessions}
    for i, rec in enumerate(records):
        lab = (
            shuffled_labels.get(rec.source_trial_id, rec.label)
            if shuffled_labels
            else rec.label
        )
        if rec.split != split or lab != label:
            continue
        if split == "train" and fold is not None:
            if fold_mode == "train" and rec.inner_fold == fold:
                continue
            if fold_mode == "validation" and rec.inner_fold != fold:
                continue
        out[rec.session_id].append(i)
    return out


def _require_nonempty_session_support(
    by_session: Mapping[str, Sequence[int]], *, label: str, context: str
) -> None:
    empty = [s for s, idx in by_session.items() if not idx]
    if empty:
        raise RuntimeError(f"cannot assemble {context}/{label}; empty sessions {empty}")


def make_draw_plan(
    records: Sequence[SourceRecord],
    *,
    split: str,
    rows_per_class: int,
    seed: int,
    fold_mode: str = "all",
    fold: int | None = None,
    shuffled_labels: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    rng = np.random.default_rng(seed)
    labels: dict[str, Any] = {}
    for label in LABELS:
        by_session = _records_by_session_label(
            records,
            split=split,
            label=label,
            fold_mode=fold_mode,
            fold=fold,
            shuffled_labels=shuffled_labels,
        )
        _require_nonempty_session_support(
            by_session, label=label, context=f"{split}/fold={fold}/{fold_mode}"
        )
        draws = []
        for _row in range(rows_per_class):
            draws.append(
                {sess: int(rng.choice(indices)) for sess, indices in by_session.items()}
            )
        labels[label] = {
            "support_by_session": {s: len(v) for s, v in by_session.items()},
            "draws": draws,
        }
    return {
        "split": split,
        "rows_per_class": rows_per_class,
        "seed": seed,
        "fold_mode": fold_mode,
        "fold": fold,
        "labels": labels,
    }


def materialize_plan(tensor: SourceTensor, plan: Mapping[str, Any]) -> RowBundle:
    sessions = sorted({r.session_id for r in tensor.records})
    cell_sessions = np.array([session_from_cell(c) for c in tensor.cell_ids])
    xs: list[np.ndarray] = []
    es: list[np.ndarray] = []
    ys: list[int] = []
    manifest: list[dict[str, Any]] = []
    for label in LABELS:
        for pseudo_row, draw in enumerate(plan["labels"][label]["draws"]):
            row_x = np.full((len(tensor.cell_ids), 10), np.nan, dtype=np.float32)
            row_e = np.full((len(tensor.cell_ids), 10), np.nan, dtype=np.float32)
            for sess in sessions:
                ri = int(draw[sess])
                rec = tensor.records[ri]
                cidx = np.where(cell_sessions == sess)[0]
                if not len(cidx):
                    continue
                if not np.all(tensor.M[ri, cidx]):
                    raise RuntimeError(
                        f"observed mask failure for {rec.source_trial_id} {sess}"
                    )
                row_x[cidx, :] = tensor.X[ri, cidx, :]
                row_e[cidx, :] = tensor.E[ri, cidx, :]
                manifest.append(
                    {
                        "seed": plan["seed"],
                        "split": plan["split"],
                        "fold_mode": plan["fold_mode"],
                        "fold": plan["fold"],
                        "label": label,
                        "pseudo_row": len(xs),
                        "within_label_row": pseudo_row,
                        "session_id": sess,
                        "source_trial_id": rec.source_trial_id,
                        "cell_ids": [tensor.cell_ids[i] for i in cidx],
                    }
                )
            if np.isnan(row_x).any() or np.isnan(row_e).any():
                raise RuntimeError(
                    "pseudo row has unavailable cells; refusing imputation"
                )
            xs.append(row_x)
            es.append(row_e)
            ys.append(LABEL_TO_INT[label])
    y = np.asarray(ys, dtype=int)
    weights = exact_class_weights(y)
    return RowBundle(
        np.stack(xs),
        np.stack(es),
        y,
        weights,
        manifest,
        {"plan_hash": stable_hash(plan)},
    )


def _class_product_indices(
    records: Sequence[SourceRecord],
    *,
    split: str,
    label: str,
    fold_mode: str = "all",
    fold: int | None = None,
    shuffled_labels: Mapping[str, str] | None = None,
) -> dict[str, list[int]]:
    by_session = _records_by_session_label(
        records,
        split=split,
        label=label,
        fold_mode=fold_mode,
        fold=fold,
        shuffled_labels=shuffled_labels,
    )
    _require_nonempty_session_support(
        by_session, label=label, context=f"product {split}/fold={fold}/{fold_mode}"
    )
    return by_session


def exact_class_weights(y: np.ndarray) -> np.ndarray:
    y = np.asarray(y, dtype=int)
    if y.ndim != 1 or not len(y):
        raise ValueError("weights require nonempty one-dimensional labels")
    weights = np.zeros(len(y), dtype=float)
    for lab in (0, 1):
        idx = y == lab
        n = int(idx.sum())
        if n == 0:
            raise ValueError("both classes are required for exact class weights")
        weights[idx] = 0.5 / n
    return weights


def build_product_rows(
    tensor: SourceTensor,
    *,
    split: str,
    fold_mode: str = "all",
    fold: int | None = None,
    max_combinations_per_class: int | None = MAX_EVAL_COMBINATIONS_PER_CLASS,
    sampled_rows_per_class: int = SAMPLED_EVAL_ROWS_PER_CLASS,
    seed: int = 0,
    shuffled_labels: Mapping[str, str] | None = None,
) -> RowBundle:
    rng = np.random.default_rng(seed)
    sessions = sorted({r.session_id for r in tensor.records})
    cell_sessions = np.array([session_from_cell(c) for c in tensor.cell_ids])
    xs: list[np.ndarray] = []
    es: list[np.ndarray] = []
    ys: list[int] = []
    manifest: list[dict[str, Any]] = []
    support: dict[str, Any] = {}
    for label in LABELS:
        by_session = _class_product_indices(
            tensor.records,
            split=split,
            label=label,
            fold_mode=fold_mode,
            fold=fold,
            shuffled_labels=shuffled_labels,
        )
        counts = {s: len(v) for s, v in by_session.items()}
        combinations = math.prod(counts.values())
        exact = (
            max_combinations_per_class is None
            or combinations <= max_combinations_per_class
        )
        if exact:
            combos = itertools.product(*(by_session[s] for s in sessions))
        else:
            combos = (
                [int(rng.choice(by_session[s])) for s in sessions]
                for _ in range(sampled_rows_per_class)
            )
        rows_before = len(xs)
        for combo_index, combo in enumerate(combos):
            row_x = np.full((len(tensor.cell_ids), 10), np.nan, dtype=np.float32)
            row_e = np.full((len(tensor.cell_ids), 10), np.nan, dtype=np.float32)
            combo_list = list(combo)
            for sess, ri in zip(sessions, combo_list, strict=True):
                rec = tensor.records[int(ri)]
                cidx = np.where(cell_sessions == sess)[0]
                if not np.all(tensor.M[int(ri), cidx]):
                    raise RuntimeError(
                        f"observed mask failure for {rec.source_trial_id} {sess}"
                    )
                row_x[cidx, :] = tensor.X[int(ri), cidx, :]
                row_e[cidx, :] = tensor.E[int(ri), cidx, :]
                manifest.append(
                    {
                        "split": split,
                        "fold_mode": fold_mode,
                        "fold": fold,
                        "label": label,
                        "product_row": len(xs),
                        "within_label_row": combo_index,
                        "session_id": sess,
                        "source_trial_id": rec.source_trial_id,
                        "cell_ids": [tensor.cell_ids[i] for i in cidx],
                    }
                )
            if np.isnan(row_x).any() or np.isnan(row_e).any():
                raise RuntimeError(
                    "product row has unavailable cells; refusing imputation"
                )
            xs.append(row_x)
            es.append(row_e)
            ys.append(LABEL_TO_INT[label])
        support[label] = {
            "support_by_session": counts,
            "product_combinations": combinations,
            "rows_materialized": len(xs) - rows_before,
            "exact": exact,
        }
    y = np.asarray(ys, dtype=int)
    weights = exact_class_weights(y)
    return RowBundle(np.stack(xs), np.stack(es), y, weights, manifest, support)


# ---------- features/models/metrics ----------


def aggregate_temporal(
    counts: np.ndarray, exposures: np.ndarray, temporal_bins: int
) -> tuple[np.ndarray, np.ndarray]:
    counts = np.asarray(counts, dtype=np.float32)
    exposures = np.asarray(exposures, dtype=np.float32)
    if counts.shape != exposures.shape or counts.shape[-1] != 10:
        raise ValueError(
            f"expected matching ten-bin arrays, got {counts.shape} and {exposures.shape}"
        )
    if temporal_bins not in {1, 2, 5, 10}:
        raise ValueError(f"unsupported temporal bin count {temporal_bins}")
    group = 10 // temporal_bins
    shape = counts.shape[:-1] + (temporal_bins, group)
    agg_counts = counts.reshape(shape).sum(axis=-1)
    agg_exp = exposures.reshape(shape).sum(axis=-1)
    if not np.allclose(agg_counts.sum(axis=-1), counts.sum(axis=-1)):
        raise ValueError("count conservation failed during temporal aggregation")
    return agg_counts, agg_exp


def feature_matrix(
    counts: np.ndarray, exposures: np.ndarray, candidate: Candidate
) -> np.ndarray:
    agg_counts, agg_exp = aggregate_temporal(counts, exposures, candidate.temporal_bins)
    if (
        np.any(~np.isfinite(agg_counts))
        or np.any(~np.isfinite(agg_exp))
        or np.any(agg_exp <= 0)
    ):
        raise ValueError("features require finite counts and positive exposures")
    rate = agg_counts / agg_exp
    if candidate.transform == "raw_rate":
        values = rate
    elif candidate.transform == "sqrt_rate":
        values = np.sqrt(agg_counts + 0.375) / np.sqrt(agg_exp)
    elif candidate.transform == "log1p_rate":
        values = np.log1p(rate)
    else:
        raise ValueError(f"unknown transform {candidate.transform}")
    return values.reshape(values.shape[0], -1).astype(np.float64)


def fit_scaler(X: np.ndarray, kind: str) -> FeatureScaler:
    if kind not in SCALERS:
        raise ValueError(f"unknown scaler {kind}")
    mean = X.mean(axis=0)
    sd = X.std(axis=0)
    positive = sd[sd > 0]
    if kind == "standard":
        scale = np.where(sd > 0, sd, 1.0)
        floor = 0.0
        floored_fraction = float(np.mean(sd == 0))
    else:
        floor = float(np.median(positive)) if len(positive) else 1.0
        scale = np.maximum(sd, floor)
        floored_fraction = float(np.mean(sd < floor))
    return FeatureScaler(
        kind=kind,
        mean=mean,
        scale=scale,
        floor=floor,
        floored_fraction=floored_fraction,
    )


def apply_scaler(X: np.ndarray, scaler: FeatureScaler) -> np.ndarray:
    return (X - scaler.mean) / scaler.scale


def average_loss_logistic_c(lambda_l2: float, n_training_rows: int) -> float:
    if lambda_l2 <= 0 or n_training_rows <= 0:
        raise ValueError("lambda_l2 and n_training_rows must be positive")
    return 1.0 / (lambda_l2 * n_training_rows)


def fit_pca_projection(X: np.ndarray, *, variance_target: float = 0.9) -> dict[str, Any]:
    """Full SVD, no whitening. Target=1 is a synthetic rotation check only."""
    X = np.asarray(X, dtype=float)
    if X.ndim != 2 or min(X.shape) < 1 or not np.isfinite(X).all():
        raise ValueError("PCA requires a finite nonempty matrix")
    if not 0 < variance_target <= 1:
        raise ValueError("variance target must be in (0,1]")
    mean = X[0].copy() if np.all(X == X[0]) else X.mean(axis=0)
    centered = X - mean
    _, singular, components = np.linalg.svd(centered, full_matrices=False)
    tolerance = np.finfo(float).eps * max(X.shape) * singular[0]
    rank = int(np.count_nonzero(singular > tolerance))
    variance = singular ** 2
    ratios = variance / variance.sum() if rank else np.zeros_like(variance)
    cumulative = np.cumsum(ratios)
    k = min(rank, int(np.searchsorted(cumulative, variance_target - 1e-12)) + 1) if rank else 0
    components = components[:k].copy()
    if k:
        signs = np.sign(components[np.arange(k), np.abs(components).argmax(axis=1)])
        components *= signs[:, None]
    return {
        "mean": mean.tolist(), "components": components.tolist(),
        "input_features": X.shape[1], "n_components": k, "numerical_rank": rank,
        "singular_tolerance": float(tolerance), "variance_target": variance_target,
        "singular_values": singular.tolist(), "explained_variance_ratio": ratios.tolist(),
        "retained_variance": float(cumulative[k - 1]) if k else 0.0,
        "intercept_only": k == 0, "whiten": False, "schema_version": 1,
    }


def apply_projection(X: np.ndarray, projection: Mapping[str, Any] | None) -> np.ndarray:
    if projection is None:
        return X
    if X.shape[1] != projection["input_features"]:
        raise ValueError("PCA feature count mismatch")
    if projection["intercept_only"]:
        # ponytail: one zero column lets the existing solver fit only its intercept.
        return np.zeros((len(X), 1))
    return (X - np.asarray(projection["mean"])) @ np.asarray(projection["components"]).T


def fit_candidate_model(train: RowBundle, candidate: Candidate) -> FittedCandidate:
    X = feature_matrix(train.X_counts, train.E, candidate)
    scaler = fit_scaler(X, candidate.scaler)
    Xs = apply_scaler(X, scaler)
    projection = fit_pca_projection(Xs) if candidate.projection == "pca90" else None
    model = LogisticRegression(
        C=average_loss_logistic_c(candidate.lambda_l2, len(train.y)),
        penalty="l2",
        solver="lbfgs",
        fit_intercept=True,
        max_iter=1000,
        random_state=0,
    )
    model.fit(apply_projection(Xs, projection), train.y)
    return FittedCandidate(candidate=candidate, scaler=scaler, model=model, projection=projection)


def predict_candidate(fit: FittedCandidate, rows: RowBundle) -> np.ndarray:
    X = feature_matrix(rows.X_counts, rows.E, fit.candidate)
    Xs = apply_scaler(X, fit.scaler)
    return fit.model.predict_proba(apply_projection(Xs, fit.projection))[:, 1]


def weighted_metrics(
    y: np.ndarray, prob: np.ndarray, weights: np.ndarray
) -> dict[str, Any]:
    y = np.asarray(y, dtype=int)
    p0 = np.asarray(prob, dtype=float)
    w = np.asarray(weights, dtype=float)
    if y.shape != p0.shape or y.shape != w.shape or not len(y):
        raise ValueError("metric arrays must be matching and nonempty")
    if (
        not np.all(np.isin(y, (0, 1)))
        or not np.all(np.isfinite(p0))
        or np.any((p0 < 0) | (p0 > 1))
    ):
        raise ValueError("invalid labels/probabilities")
    if not np.all(np.isfinite(w)) or np.any(w < 0) or w.sum() <= 0:
        raise ValueError("invalid weights")
    w = w / w.sum()
    p = np.clip(p0, 1e-9, 1 - 1e-9)
    pred = (p >= 0.5).astype(int)
    log_loss = -float(np.sum(w * (y * np.log(p) + (1 - y) * np.log1p(-p))))
    brier = float(np.sum(w * (p - y) ** 2))
    acc = float(np.sum(w * (pred == y)))
    recalls = []
    for lab in (0, 1):
        idx = y == lab
        denom = float(w[idx].sum())
        recalls.append(
            float(np.sum(w[idx] * (pred[idx] == lab)) / denom) if denom else None
        )
    return {
        "n_rows": int(len(y)),
        "log_loss": log_loss,
        "delta_log_loss_baseline_minus_model": math.log(2.0) - log_loss,
        "weighted_accuracy": acc,
        "balanced_accuracy": None
        if any(r is None for r in recalls)
        else float(sum(recalls) / 2),
        "brier": brier,
        "positive_rate_true_weighted": float(np.sum(w * y)),
        "positive_rate_pred_weighted": float(np.sum(w * pred)),
        "auroc": weighted_auc(y, p0, w),
    }


def weighted_auc(y: np.ndarray, score: np.ndarray, weights: np.ndarray) -> float | None:
    y = np.asarray(y, dtype=int)
    score = np.asarray(score, dtype=float)
    weights = np.asarray(weights, dtype=float)
    pos = y == 1
    neg = y == 0
    if not pos.any() or not neg.any():
        return None
    total = float(weights[pos].sum() * weights[neg].sum())
    if total <= 0:
        return None
    auc = 0.0
    for ps, pw in zip(score[pos], weights[pos], strict=True):
        auc += float(
            pw * np.sum(weights[neg] * ((ps > score[neg]) + 0.5 * (ps == score[neg])))
        )
    return float(auc / total)


def model_replay_payload(fit: FittedCandidate) -> dict[str, Any]:
    return {
        **fit.candidate.as_dict(),
        **({"projection_state": fit.projection, "replay_schema_version": 2} if fit.projection is not None else {}),
        "intercept": np.asarray(fit.model.intercept_).tolist(),
        "coef": np.asarray(fit.model.coef_).tolist(),
        "classes": np.asarray(fit.model.classes_).tolist(),
        "input_features": len(fit.scaler.mean),
        "intercept_only": fit.scaler.floored_fraction == 1.0,
        "scaler": {
            "kind": fit.scaler.kind,
            "mean": fit.scaler.mean.tolist(),
            "scale": fit.scaler.scale.tolist(),
            "floor": fit.scaler.floor,
            "floored_fraction": fit.scaler.floored_fraction,
        },
    }


def predict_from_replay(
    payload: Mapping[str, Any], counts: np.ndarray, exposures: np.ndarray
) -> np.ndarray:
    candidate = candidate_from_dict(payload)
    X = feature_matrix(counts, exposures, candidate)
    scaler_info = payload["scaler"]
    scaler = FeatureScaler(
        kind=str(scaler_info["kind"]),
        mean=np.asarray(scaler_info["mean"], dtype=float),
        scale=np.asarray(scaler_info["scale"], dtype=float),
        floor=float(scaler_info["floor"]),
        floored_fraction=float(scaler_info["floored_fraction"]),
    )
    Xs = apply_scaler(X, scaler)
    if candidate.projection == "pca90":
        if payload.get("replay_schema_version") != 2:
            raise ValueError("PCA replay requires schema version 2")
        Xs = apply_projection(Xs, payload["projection_state"])
    coef = np.asarray(payload["coef"], dtype=float).reshape(1, -1)
    intercept = float(np.asarray(payload["intercept"], dtype=float).reshape(-1)[0])
    logits = Xs @ coef.T + intercept
    return (1.0 / (1.0 + np.exp(-logits.reshape(-1)))).astype(float)


# ---------- candidate-family evaluation ----------


def round1_candidates() -> list[Candidate]:
    return [
        Candidate(t, tr, sc, ROUND1_LAMBDA)
        for t in ROUND1_TEMPORAL_BINS
        for tr in TRANSFORMS
        for sc in SCALERS
    ]


def candidate_from_dict(payload: Mapping[str, Any]) -> Candidate:
    # Saved models carry scaler state; candidate/metric rows carry its name.
    scaler = payload["scaler"]
    scaler_kind = scaler["kind"] if isinstance(scaler, Mapping) else scaler
    return Candidate(
        int(payload["temporal_bins"]),
        str(payload["transform"]),
        str(scaler_kind),
        float(payload["lambda_l2"]),
        str(payload.get("projection", "none")),
    )


def candidate_sort_index(candidate: Candidate) -> tuple[int, int, int, int]:
    return (
        ROUND1_TEMPORAL_BINS.index(candidate.temporal_bins),
        TRANSFORMS.index(candidate.transform),
        SCALERS.index(candidate.scaler),
        [0.01, 0.1, 1.0].index(float(candidate.lambda_l2))
        if float(candidate.lambda_l2) in {0.01, 0.1, 1.0}
        else 99,
    )


def select_best_candidate(
    rows: Sequence[Mapping[str, Any]], *, metric: str = "primary_cv_delta_log_loss"
) -> dict[str, Any]:
    best: dict[str, Any] | None = None
    for row in sorted(rows, key=lambda r: candidate_sort_index(candidate_from_dict(r))):
        score = float(row[metric])
        if best is None or score > float(best[metric]):
            best = dict(row)
    if best is None:
        raise ValueError("no candidate rows to select from")
    return best


def evaluate_candidate_cv(
    tensor: SourceTensor,
    candidate: Candidate,
    *,
    rows_per_class: int = ROWS_PER_CLASS,
    seed: int = PRIMARY_SEED,
    shuffled_labels: Mapping[str, str] | None = None,
    save_details: bool = True,
) -> tuple[
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
]:
    global FIT_COUNT
    metric_rows: list[dict[str, Any]] = []
    prediction_rows: list[dict[str, Any]] = []
    model_rows: list[dict[str, Any]] = []
    lineage_rows: list[dict[str, Any]] = []
    for endpoint in EXPECTED_ENDPOINTS:
        if not any(r.endpoint_pair == endpoint for r in tensor.records):
            continue
        et = subset_tensor(tensor, endpoint)
        for fold in (0, 1, 2):
            plan = make_draw_plan(
                et.records,
                split="train",
                rows_per_class=rows_per_class,
                seed=seed,
                fold_mode="train",
                fold=fold,
                shuffled_labels=shuffled_labels,
            )
            train = materialize_plan(et, plan)
            eval_rows = build_product_rows(
                et,
                split="train",
                fold_mode="validation",
                fold=fold,
                seed=seed + 10_000 + fold,
                shuffled_labels=shuffled_labels,
            )
            fit_started = time.monotonic()
            fit = fit_candidate_model(train, candidate)
            FIT_COUNT += 1
            train_metrics = weighted_metrics(
                train.y, predict_candidate(fit, train), train.weights
            )
            prob = predict_candidate(fit, eval_rows)
            metrics = weighted_metrics(eval_rows.y, prob, eval_rows.weights)
            row = {
                **candidate.as_dict(),
                "endpoint_pair": endpoint,
                "fold": fold,
                "seed": seed,
                "split_evaluated": "inner_cv_train_fold_only",
                **metrics,
                "train_rows": int(len(train.y)),
                "eval_rows": int(len(eval_rows.y)),
                "eval_support": eval_rows.support,
                "train_plan_hash": stable_hash(plan),
                "train_metrics": train_metrics,
                "train_cv_log_loss_gap": metrics["log_loss"]
                - train_metrics["log_loss"],
                "train_distinct_source_count": len(
                    {r["source_trial_id"] for r in train.manifest}
                ),
                "train_available_source_count": len(
                    {
                        r.source_trial_id
                        for r in et.records
                        if r.split == "train" and r.inner_fold != fold
                    }
                ),
                "n_iter": int(fit.model.n_iter_.max()),
                "converged": bool(fit.model.n_iter_.max() < fit.model.max_iter),
                "elapsed_seconds": time.monotonic() - fit_started,
            }
            record_progress("cv_fit_complete", fit_count=FIT_COUNT, **row)
            metric_rows.append(row)
            if save_details:
                replay = model_replay_payload(fit)
                replay.update(
                    {
                        "endpoint_pair": endpoint,
                        "fold": fold,
                        "seed": seed,
                        "train_plan_hash": stable_hash(plan),
                    }
                )
                model_rows.append(replay)
                for i, p in enumerate(prob):
                    prediction_rows.append(
                        {
                            **candidate.as_dict(),
                            "endpoint_pair": endpoint,
                            "fold": fold,
                            "seed": seed,
                            "eval_row": i,
                            "true_label": INT_TO_LABEL[int(eval_rows.y[i])],
                            "prob_present": float(p),
                            "weight": float(eval_rows.weights[i]),
                        }
                    )
                lineage_rows.extend(train.manifest)
                lineage_rows.extend(eval_rows.manifest)
    return metric_rows, prediction_rows, model_rows, lineage_rows


def summarize_cv_metrics(
    metric_rows: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    grouped: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for row in metric_rows:
        grouped[str(row["candidate_key"])].append(row)
    summaries: list[dict[str, Any]] = []
    for _candidate_key, rows in grouped.items():
        endpoint_means = []
        endpoints = sorted({str(r["endpoint_pair"]) for r in rows})
        for endpoint in endpoints:
            endpoint_rows = [r for r in rows if r["endpoint_pair"] == endpoint]
            endpoint_means.append(
                float(
                    np.mean(
                        [
                            float(r["delta_log_loss_baseline_minus_model"])
                            for r in endpoint_rows
                        ]
                    )
                )
            )
        first = rows[0]
        summaries.append(
            {
                **candidate_from_dict(first).as_dict(),
                "primary_cv_delta_log_loss": float(np.mean(endpoint_means)),
                "endpoint_count": len(endpoints),
                "fold_count": len(rows),
                "endpoint_mean_delta_log_loss": dict(
                    zip(endpoints, endpoint_means, strict=True)
                ),
                "mean_cv_log_loss": float(
                    np.mean([float(r["log_loss"]) for r in rows])
                ),
                "mean_cv_balanced_accuracy": float(
                    np.mean(
                        [
                            float(r["balanced_accuracy"])
                            for r in rows
                            if r["balanced_accuracy"] is not None
                        ]
                    )
                ),
            }
        )
    return sorted(summaries, key=lambda r: candidate_sort_index(candidate_from_dict(r)))


def run_round1_cv(
    tensor: SourceTensor,
    *,
    rows_per_class: int = ROWS_PER_CLASS,
    seed: int = PRIMARY_SEED,
    output_dir: Path | None = None,
) -> dict[str, Any]:
    started = time.time()
    all_metrics: list[dict[str, Any]] = []
    all_predictions: list[dict[str, Any]] = []
    all_models: list[dict[str, Any]] = []
    all_lineage: list[dict[str, Any]] = []
    for candidate in round1_candidates():
        metrics, preds, models, lineage = evaluate_candidate_cv(
            tensor, candidate, rows_per_class=rows_per_class, seed=seed
        )
        all_metrics.extend(metrics)
        all_predictions.extend(preds)
        all_models.extend(models)
        all_lineage.extend(lineage)
    summaries = summarize_cv_metrics(all_metrics)
    best = select_best_candidate(summaries)
    result = {
        "stage": "round1_cv_only_18_arm_screen",
        "status": "complete",
        "original_validation_metrics_policy": "not computed in round1; only original-training inner folds are evaluated",
        "elapsed_seconds": time.time() - started,
        "rows_per_class": rows_per_class,
        "seed": seed,
        "candidate_count": len(summaries),
        "best_round1": best,
        "summary_rows": summaries,
        "metric_row_count": len(all_metrics),
        "prediction_row_count": len(all_predictions),
        "model_row_count": len(all_models),
    }
    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)
        write_csv(output_dir / "round1_cv_metrics.csv.gz", all_metrics)
        write_csv(output_dir / "round1_cv_predictions.csv.gz", all_predictions)
        write_json(output_dir / "round1_summary.json", result)
        write_json(output_dir / "round1_model_replays.json.gz", all_models)
        write_json(output_dir / "round1_source_lineage.json.gz", all_lineage)
    return result


def round2_extra_candidates(round1_best: Mapping[str, Any]) -> list[Candidate]:
    base = candidate_from_dict(round1_best)
    return [replace(base, lambda_l2=lam) for lam in ROUND2_EXTRA_LAMBDAS]


def family20_from_round2(
    round1_rows: Sequence[Mapping[str, Any]], round2_rows: Sequence[Mapping[str, Any]]
) -> list[dict[str, Any]]:
    rows = [dict(r) for r in round1_rows] + [dict(r) for r in round2_rows]
    if len(rows) != 20:
        raise ValueError(f"expected 20 candidate rows, got {len(rows)}")
    return sorted(rows, key=lambda r: candidate_sort_index(candidate_from_dict(r)))


def run_round2_adapt(
    tensor: SourceTensor,
    round1_summary: Mapping[str, Any],
    *,
    rows_per_class: int = ROWS_PER_CLASS,
    seed: int = PRIMARY_SEED,
    output_dir: Path | None = None,
    plan_only: bool = False,
) -> dict[str, Any]:
    started = time.time()
    round1_rows = list(round1_summary["summary_rows"])
    round1_best = select_best_candidate(round1_rows)
    plan = {
        "stage": "round2_l2_refinement_plan",
        "status": "planned" if plan_only else "complete",
        "basis": "best representation by round1 primary inner-CV delta; no original validation metrics inspected",
        "round1_best_representation": round1_best,
        "extra_lambdas": list(ROUND2_EXTRA_LAMBDAS),
        "extra_candidates": [c.as_dict() for c in round2_extra_candidates(round1_best)],
    }
    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)
        write_json(output_dir / "round2_refinement_plan.json", plan)
    if plan_only:
        return plan
    extra_metrics: list[dict[str, Any]] = []
    extra_predictions: list[dict[str, Any]] = []
    extra_models: list[dict[str, Any]] = []
    extra_lineage: list[dict[str, Any]] = []
    for candidate in round2_extra_candidates(round1_best):
        metrics, preds, models, lineage = evaluate_candidate_cv(
            tensor, candidate, rows_per_class=rows_per_class, seed=seed
        )
        extra_metrics.extend(metrics)
        extra_predictions.extend(preds)
        extra_models.extend(models)
        extra_lineage.extend(lineage)
    extra_rows = summarize_cv_metrics(extra_metrics)
    family_rows = family20_from_round2(round1_rows, extra_rows)
    final_best = select_best_candidate(family_rows)
    result = {
        **plan,
        "status": "complete",
        "elapsed_seconds": time.time() - started,
        "round2_summary_rows": extra_rows,
        "family20_summary_rows": family_rows,
        "selected_family20_candidate": final_best,
        "original_validation_metrics_policy": "not computed in round2; only original-training inner folds are evaluated",
    }
    if output_dir is not None:
        write_csv(output_dir / "round2_cv_metrics.csv.gz", extra_metrics)
        write_csv(output_dir / "round2_cv_predictions.csv.gz", extra_predictions)
        write_json(output_dir / "round2_summary.json", result)
        write_json(output_dir / "round2_model_replays.json.gz", extra_models)
        write_json(output_dir / "round2_source_lineage.json.gz", extra_lineage)
    return result


def train_evaluate_validation(
    tensor: SourceTensor,
    candidates: Sequence[Candidate],
    *,
    rows_per_class: int = ROWS_PER_CLASS,
    seed: int = PRIMARY_SEED,
    shuffled_labels: Mapping[str, str] | None = None,
    save_details: bool = False,
    artifact_dir: Path | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    global FIT_COUNT
    save_details = save_details or artifact_dir is not None
    metric_rows: list[dict[str, Any]] = []
    pred_rows: list[dict[str, Any]] = []
    model_rows: list[dict[str, Any]] = []
    lineage: list[dict[str, Any]] = []
    for endpoint in EXPECTED_ENDPOINTS:
        if not any(r.endpoint_pair == endpoint for r in tensor.records):
            continue
        et = subset_tensor(tensor, endpoint)
        plan = make_draw_plan(
            et.records,
            split="train",
            rows_per_class=rows_per_class,
            seed=seed,
            shuffled_labels=shuffled_labels,
        )
        train = materialize_plan(et, plan)
        validation = build_product_rows(
            et,
            split="validation",
            max_combinations_per_class=None,
            seed=seed + 20_000,
            shuffled_labels=shuffled_labels,
        )
        if save_details:
            lineage.extend({"endpoint_pair": endpoint, **r} for r in train.manifest)
            lineage.extend(
                {"endpoint_pair": endpoint, **r} for r in validation.manifest
            )
        for candidate in candidates:
            fit = fit_candidate_model(train, candidate)
            FIT_COUNT += 1
            prob = predict_candidate(fit, validation)
            metrics = weighted_metrics(validation.y, prob, validation.weights)
            train_metrics = weighted_metrics(
                train.y, predict_candidate(fit, train), train.weights
            )
            metric_rows.append(
                {
                    **candidate.as_dict(),
                    "endpoint_pair": endpoint,
                    "seed": seed,
                    "split_evaluated": "original_validation_diagnostic",
                    **metrics,
                    "train_rows": int(len(train.y)),
                    "validation_rows": int(len(validation.y)),
                    "validation_support": validation.support,
                    "train_plan_hash": stable_hash(plan),
                    "train_metrics": train_metrics,
                    "train_distinct_source_count": len(
                        {r["source_trial_id"] for r in train.manifest}
                    ),
                    "n_iter": int(fit.model.n_iter_.max()),
                    "converged": bool(fit.model.n_iter_.max() < fit.model.max_iter),
                    "interval_grade": "point_influence_only"
                    if endpoint in POINT_INFLUENCE_ENDPOINTS
                    else "source_resampling_sensitivity_only",
                }
            )
            record_progress(
                "diagnostic_fit_complete", fit_count=FIT_COUNT, **metric_rows[-1]
            )
            if save_details:
                replay = model_replay_payload(fit)
                replay.update(
                    {
                        "endpoint_pair": endpoint,
                        "seed": seed,
                        "cell_ids": list(et.cell_ids),
                        "train_plan_hash": stable_hash(plan),
                    }
                )
                model_rows.append(replay)
                for i, p in enumerate(prob):
                    pred_rows.append(
                        {
                            **candidate.as_dict(),
                            "endpoint_pair": endpoint,
                            "seed": seed,
                            "validation_row": i,
                            "true_label": INT_TO_LABEL[int(validation.y[i])],
                            "prob_present": float(p),
                            "weight": float(validation.weights[i]),
                        }
                    )
    if artifact_dir is not None:
        write_csv(artifact_dir / "validation_metrics.csv.gz", metric_rows)
        write_csv(artifact_dir / "validation_predictions.csv.gz", pred_rows)
        write_json(artifact_dir / "validation_models.json.gz", model_rows)
        write_json(artifact_dir / "validation_source_lineage.json.gz", lineage)
    return metric_rows, pred_rows, model_rows


def aggregate_validation_rows(
    metric_rows: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    grouped: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for row in metric_rows:
        grouped[str(row["candidate_key"])].append(row)
    out = []
    for _candidate_key, rows in grouped.items():
        endpoints = sorted({str(r["endpoint_pair"]) for r in rows})
        endpoint_delta = {
            ep: float(
                np.mean(
                    [
                        float(r["delta_log_loss_baseline_minus_model"])
                        for r in rows
                        if r["endpoint_pair"] == ep
                    ]
                )
            )
            for ep in endpoints
        }
        first = rows[0]
        out.append(
            {
                **candidate_from_dict(first).as_dict(),
                "diagnostic_validation_delta_log_loss": float(
                    np.mean(list(endpoint_delta.values()))
                ),
                "endpoint_count": len(endpoints),
                "endpoint_delta_log_loss": endpoint_delta,
                "point_influence_only_endpoints": sorted(
                    POINT_INFLUENCE_ENDPOINTS & set(endpoints)
                ),
            }
        )
    return sorted(out, key=lambda r: candidate_sort_index(candidate_from_dict(r)))


def make_label_permutation(
    records: Sequence[SourceRecord],
    *,
    seed: int,
    temporal_half: bool = False,
) -> tuple[dict[str, str], dict[str, Any]]:
    rng = random.Random(seed)
    half_by_source, boundaries = (
        temporal_half_assignments(records) if temporal_half else ({}, {})
    )
    grouped: dict[tuple[Any, ...], list[SourceRecord]] = defaultdict(list)
    for rec in records:
        fold_key = rec.inner_fold if rec.split == "train" else -1
        key = (rec.session_id, rec.endpoint_pair, rec.split, fold_key)
        if temporal_half:
            key = (*key, half_by_source[rec.source_trial_id])
        grouped[key].append(rec)
    out: dict[str, str] = {}
    movable = 0
    immovable = 0
    stratum_rows = []
    for key, rows in sorted(grouped.items()):
        labels = [r.label for r in rows]
        shuffled = labels[:]
        rng.shuffle(shuffled)
        moved = labels != shuffled and len(set(labels)) > 1
        if moved:
            movable += len(rows)
        else:
            immovable += len(rows)
        before = Counter(labels)
        after = Counter(shuffled)
        if before != after:
            raise RuntimeError(f"permutation changed label counts for {key}")
        for rec, lab in zip(rows, shuffled, strict=True):
            out[rec.source_trial_id] = lab
        stratum_rows.append(
            {"key": list(key), "n": len(rows), "counts": dict(before), "moved": moved}
        )
    return out, {
        "seed": seed,
        "temporal_half": temporal_half,
        "group_fields": [
            "session_id",
            "endpoint_pair",
            "split",
            "inner_fold_train_else_minus1",
        ]
        + (["train_trial_index_half"] if temporal_half else []),
        "source_count": len(records),
        "movable_fraction": movable / len(records) if records else 0.0,
        "immovable_fraction": immovable / len(records) if records else 0.0,
        "shuffled_label_hash": stable_hash(out),
        "temporal_half_boundaries": boundaries,
        "strata": stratum_rows,
    }


def temporal_half_assignments(
    records: Sequence[SourceRecord],
) -> tuple[dict[str, str], dict[str, float]]:
    by_context: dict[tuple[str, str], list[int]] = defaultdict(list)
    for rec in records:
        if rec.split == "train":
            by_context[(rec.session_id, rec.endpoint_pair)].append(rec.trial_index)
    boundaries = {
        f"{sess}|{ep}": float(np.median(vals))
        for (sess, ep), vals in by_context.items()
    }
    assignments: dict[str, str] = {}
    for rec in records:
        key = f"{rec.session_id}|{rec.endpoint_pair}"
        boundary = boundaries[key]
        assignments[rec.source_trial_id] = (
            "early" if rec.trial_index <= boundary else "late"
        )
    return assignments, boundaries


def select_family_for_world(
    tensor: SourceTensor,
    *,
    rows_per_class: int,
    seed: int,
    shuffled_labels: Mapping[str, str] | None,
    save_details: bool = False,
    artifact_dir: Path | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any], list[Candidate]]:
    cv_rows: list[dict[str, Any]] = []
    predictions: list[dict[str, Any]] = []
    models: list[dict[str, Any]] = []
    lineage: list[dict[str, Any]] = []
    candidates = list(round1_candidates())
    for index in range(20):
        if index == 18:
            # Repeat the adaptive branch in THIS world, not the observed branch.
            best1 = select_best_candidate(summarize_cv_metrics(cv_rows))
            candidates.extend(round2_extra_candidates(best1))
        rows, preds, replays, sources = evaluate_candidate_cv(
            tensor,
            candidates[index],
            rows_per_class=rows_per_class,
            seed=seed,
            shuffled_labels=shuffled_labels,
            save_details=save_details or artifact_dir is not None,
        )
        cv_rows.extend(rows)
        predictions.extend(preds)
        models.extend(replays)
        if index == 0:
            # Assemblies are matched across all representations and lambdas.
            lineage = sources
    family_rows = summarize_cv_metrics(cv_rows)
    best20 = select_best_candidate(family_rows)
    if artifact_dir is not None:
        write_json(artifact_dir / "cv_family20.json", family_rows)
        write_csv(artifact_dir / "cv_metrics.csv.gz", cv_rows)
        write_csv(artifact_dir / "cv_predictions.csv.gz", predictions)
        write_json(artifact_dir / "cv_models.json.gz", models)
        write_json(artifact_dir / "cv_source_lineage.json.gz", lineage)
    return family_rows, best20, candidates


def run_null_worlds(
    tensor: SourceTensor,
    *,
    count: int,
    temporal_half: bool,
    rows_per_class: int,
    seed0: int,
    artifact_dir: Path | None = None,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for i in range(count):
        world_dir = (
            artifact_dir / f"world-{i:03d}" if artifact_dir is not None else None
        )
        labels, audit = make_label_permutation(
            tensor.records, seed=seed0 + i, temporal_half=temporal_half
        )
        if world_dir is not None:
            write_json(
                world_dir / "permutation.json", {"labels": labels, "audit": audit}
            )
        family_rows, best20, candidates20 = select_family_for_world(
            tensor,
            rows_per_class=rows_per_class,
            seed=PRIMARY_SEED,
            shuffled_labels=labels,
            artifact_dir=world_dir,
        )
        max_metrics, _p, _m = train_evaluate_validation(
            tensor,
            candidates20,
            rows_per_class=rows_per_class,
            seed=PRIMARY_SEED,
            shuffled_labels=labels,
            artifact_dir=world_dir,
        )
        validation_summaries = aggregate_validation_rows(max_metrics)
        selected_summary = next(
            r
            for r in validation_summaries
            if r["candidate_key"] == best20["candidate_key"]
        )
        max_summary = select_best_candidate(
            validation_summaries, metric="diagnostic_validation_delta_log_loss"
        )
        rows.append(
            {
                "null_index": i,
                "null_type": "temporal_half" if temporal_half else "ordinary",
                "selection_policy": "world_own_round1_plus_own_l2_refinement",
                "seed": seed0 + i,
                "movable_fraction": audit["movable_fraction"],
                "immovable_fraction": audit["immovable_fraction"],
                "shuffled_label_hash": audit["shuffled_label_hash"],
                "selected_candidate_key": best20["candidate_key"],
                "selected_cv_delta_log_loss": best20["primary_cv_delta_log_loss"],
                "null_selected_diagnostic_delta_log_loss": selected_summary[
                    "diagnostic_validation_delta_log_loss"
                ],
                "null_max_family_diagnostic_delta_log_loss": max_summary[
                    "diagnostic_validation_delta_log_loss"
                ],
                "max_family_candidate_key": max_summary["candidate_key"],
                "family20_hash": stable_hash(family_rows),
                "artifact_dir": world_dir,
                "audit": audit,
            }
        )
        if world_dir is not None:
            write_json(
                world_dir / "validation_candidate_summaries.json", validation_summaries
            )
            write_json(world_dir / "world_summary.json", rows[-1])
        record_progress(
            "null_world_complete",
            world=i,
            total=count,
            temporal_half=temporal_half,
            fit_count=FIT_COUNT,
        )
    return rows


def _bootstrap_records(
    records: Sequence[SourceRecord], *, seed: int
) -> tuple[list[SourceRecord], dict[str, Any]]:
    rng = random.Random(seed)
    grouped: dict[tuple[str, str, str, str], list[SourceRecord]] = defaultdict(list)
    for rec in records:
        grouped[(rec.session_id, rec.endpoint_pair, rec.split, rec.label)].append(rec)
    boot: list[SourceRecord] = []
    lineage = []
    for key, rows in sorted(grouped.items()):
        picks = [rng.choice(rows) for _ in rows]
        for j, rec in enumerate(picks):
            dup_id = f"{rec.source_trial_id}__boot{seed}_{j}"
            boot.append(replace(rec, source_trial_id=dup_id))
            lineage.append(
                {
                    "bootstrap_source_trial_id": dup_id,
                    "original_source_trial_id": rec.source_trial_id,
                    "stratum": list(key),
                }
            )
    return boot, {
        "seed": seed,
        "lineage": lineage,
        "strata": {"|".join(k): len(v) for k, v in grouped.items()},
    }


def bootstrap_tensor(
    tensor: SourceTensor, records: Sequence[SourceRecord]
) -> SourceTensor:
    original_index = {r.source_trial_id: i for i, r in enumerate(tensor.records)}
    rows = [original_index[r.source_trial_id.split("__boot", 1)[0]] for r in records]
    return SourceTensor(
        X=tensor.X[rows].copy(),
        E=tensor.E[rows].copy(),
        M=tensor.M[rows].copy(),
        records=tuple(records),
        cell_ids=tensor.cell_ids,
        audit=tensor.audit,
    )


def run_bootstraps(
    tensor: SourceTensor,
    *,
    selected_candidate: Candidate,
    count: int,
    rows_per_class: int,
    seed0: int,
    artifact_dir: Path | None = None,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for i in range(count):
        world_dir = (
            artifact_dir / f"resample-{i:03d}" if artifact_dir is not None else None
        )
        records, audit = _bootstrap_records(tensor.records, seed=seed0 + i)
        bt = bootstrap_tensor(tensor, records)
        if world_dir is not None:
            write_json(world_dir / "resampling.json", audit)
        metrics, _preds, _models = train_evaluate_validation(
            bt,
            [selected_candidate],
            rows_per_class=rows_per_class,
            seed=PRIMARY_SEED,
            artifact_dir=world_dir,
        )
        summary = aggregate_validation_rows(metrics)[0]
        rows.append(
            {
                "bootstrap_index": i,
                "seed": seed0 + i,
                "selected_candidate_key": selected_candidate.key,
                "diagnostic_validation_delta_log_loss": summary[
                    "diagnostic_validation_delta_log_loss"
                ],
                "endpoint_delta_log_loss": summary["endpoint_delta_log_loss"],
                "interval_label": "source-resampling sensitivity only; point/influence endpoints do not support interval-backed repeatability claims",
                "lineage_hash": stable_hash(audit["lineage"]),
                "audit": audit,
            }
        )
        if world_dir is not None:
            write_json(world_dir / "bootstrap_summary.json", rows[-1])
        record_progress(
            "bootstrap_complete", resample=i, total=count, fit_count=FIT_COUNT
        )
    return rows


def nuisance_features(rows: RowBundle, records: Sequence[SourceRecord]) -> np.ndarray:
    """Same source draws as neural rows; no path label or future path feature input."""
    by_source = {r.source_trial_id: r for r in records}
    sessions = sorted({r.session_id for r in records})
    columns = {s: 2 * i for i, s in enumerate(sessions)}
    X = np.full((len(rows.y), 2 * len(sessions)), np.nan)
    for entry in rows.manifest:
        index = entry.get("pseudo_row", entry.get("product_row"))
        rec = by_source[entry["source_trial_id"]]
        col = columns[rec.session_id]
        X[index, col : col + 2] = (rec.trial_index, rec.cue_duration_s)
    if not np.isfinite(X).all():
        raise ValueError("nuisance rows lack observed source metadata")
    return X


def run_nuisance_control(
    tensor: SourceTensor, rows_per_class: int, artifact_dir: Path | None
) -> dict[str, Any]:
    global FIT_COUNT
    metrics, predictions, models = [], [], []
    for endpoint in EXPECTED_ENDPOINTS:
        if not any(r.endpoint_pair == endpoint for r in tensor.records):
            continue
        et = subset_tensor(tensor, endpoint)
        for fold in (0, 1, 2, None):
            plan = make_draw_plan(
                et.records,
                split="train",
                rows_per_class=rows_per_class,
                seed=PRIMARY_SEED,
                fold_mode="all" if fold is None else "train",
                fold=fold,
            )
            train = materialize_plan(et, plan)
            validation = build_product_rows(
                et,
                split="validation" if fold is None else "train",
                fold_mode="all" if fold is None else "validation",
                fold=fold,
                seed=20_000 if fold is None else 10_000 + fold,
            )
            Xtrain = nuisance_features(train, et.records)
            Xval = nuisance_features(validation, et.records)
            scaler = fit_scaler(Xtrain, "standard")
            model = LogisticRegression(
                C=average_loss_logistic_c(0.1, len(train.y)),
                max_iter=1000,
                solver="lbfgs",
                random_state=0,
            )
            model.fit(apply_scaler(Xtrain, scaler), train.y)
            FIT_COUNT += 1
            prob = model.predict_proba(apply_scaler(Xval, scaler))[:, 1]
            key = {
                "endpoint_pair": endpoint,
                "fold": fold,
                "seed": PRIMARY_SEED,
                "evaluation": "historical_validation" if fold is None else "inner_cv",
            }
            row = {
                **key,
                **weighted_metrics(validation.y, prob, validation.weights),
                "train_plan_hash": stable_hash(plan),
                "n_iter": int(model.n_iter_.max()),
            }
            metrics.append(row)
            predictions.extend(
                {
                    **key,
                    "eval_row": i,
                    "true_label": INT_TO_LABEL[int(validation.y[i])],
                    "prob_present": float(p),
                    "weight": float(validation.weights[i]),
                }
                for i, p in enumerate(prob)
            )
            models.append(
                {
                    **key,
                    "mean": scaler.mean,
                    "scale": scaler.scale,
                    "coef": model.coef_[0],
                    "intercept": float(np.asarray(model.intercept_).reshape(-1)[0]),
                    "evaluation_features": Xval,
                    "sessions": sorted({r.session_id for r in et.records}),
                    "evaluation_lineage": validation.manifest,
                }
            )
            record_progress("nuisance_fit_complete", fit_count=FIT_COUNT, **row)
    result = {
        "policy": "descriptive fixed-L2 nuisance-only baseline; not a nested neural-plus-nuisance conditional test",
        "features": ["source_trial_index", "full_cue_duration_s"],
        "lambda_l2": 0.1,
        "cv_delta_log_loss": float(
            np.mean(
                [
                    r["delta_log_loss_baseline_minus_model"]
                    for r in metrics
                    if r["fold"] is not None
                ]
            )
        ),
        "validation_delta_log_loss": float(
            np.mean(
                [
                    r["delta_log_loss_baseline_minus_model"]
                    for r in metrics
                    if r["fold"] is None
                ]
            )
        ),
        "endpoint_metrics": metrics,
    }
    if artifact_dir is not None:
        write_json(artifact_dir / "summary.json", result)
        write_csv(artifact_dir / "predictions.csv.gz", predictions)
        write_json(artifact_dir / "models.json.gz", models)
    return result


def run_influence(
    tensor: SourceTensor,
    selected: Candidate,
    baseline: Mapping[str, Any],
    rows_per_class: int,
    artifact_dir: Path | None,
) -> dict[str, Any]:
    base = baseline["endpoint_delta_log_loss"]
    endpoint_rows = [
        {
            "omitted_endpoint": ep,
            "remaining_equal_endpoint_delta": float(
                np.mean([v for k, v in base.items() if k != ep])
            ),
        }
        for ep in base
        if len(base) > 1
    ]
    session_rows = []
    for session in sorted({r.session_id for r in tensor.records}):
        indices = [i for i, r in enumerate(tensor.records) if r.session_id != session]
        if not indices:
            session_rows.append(
                {"omitted_session": session, "status": "no_remaining_sources"}
            )
            continue
        reduced = replace(
            tensor,
            X=tensor.X[indices],
            E=tensor.E[indices],
            M=tensor.M[indices],
            records=tuple(tensor.records[i] for i in indices),
        )
        world_dir = artifact_dir / session if artifact_dir is not None else None
        metrics, _, _ = train_evaluate_validation(
            reduced,
            [selected],
            rows_per_class=rows_per_class,
            seed=PRIMARY_SEED,
            artifact_dir=world_dir,
        )
        summary = aggregate_validation_rows(metrics)[0]
        common = summary["endpoint_delta_log_loss"]
        original_common = float(np.mean([base[k] for k in common]))
        session_rows.append(
            {
                "omitted_session": session,
                "remaining_endpoint_deltas": common,
                "dropped_endpoints": sorted(set(base) - set(common)),
                "remaining_equal_endpoint_delta": summary[
                    "diagnostic_validation_delta_log_loss"
                ],
                "original_common_endpoint_delta": original_common,
                "change_on_common_endpoints": summary[
                    "diagnostic_validation_delta_log_loss"
                ]
                - original_common,
            }
        )
    result = {
        "policy": "frozen recipe refit after dropping source/session and its cell columns; not neuron-identity transfer or independent-session CI",
        "leave_endpoint_out": endpoint_rows,
        "leave_session_out": session_rows,
    }
    if artifact_dir is not None:
        write_json(artifact_dir / "summary.json", result)
    return result


def run_assembly_sensitivity(
    tensor: SourceTensor,
    candidates: Sequence[Candidate],
    selected: Candidate,
    rows_per_class: int,
    artifact_dir: Path | None,
) -> list[dict[str, Any]]:
    results = []
    for seed in SENSITIVITY_SEEDS:
        world_dir = artifact_dir / f"seed-{seed}" if artifact_dir is not None else None
        cv_rows, predictions, models, lineage = [], [], [], []
        for index, candidate in enumerate(candidates):
            metrics, preds, replays, sources = evaluate_candidate_cv(
                tensor,
                candidate,
                seed=seed,
                rows_per_class=rows_per_class,
                save_details=world_dir is not None,
            )
            cv_rows.extend(metrics)
            predictions.extend(preds)
            models.extend(replays)
            if index == 0:
                lineage = sources
        val_metrics, _, _ = train_evaluate_validation(
            tensor,
            candidates,
            seed=seed,
            rows_per_class=rows_per_class,
            artifact_dir=world_dir,
        )
        cv_summary = summarize_cv_metrics(cv_rows)
        val_summary = aggregate_validation_rows(val_metrics)
        results.append(
            {
                "seed": seed,
                "selection_allowed": False,
                "fixed_selected_candidate": selected.key,
                "selected_cv": next(
                    r for r in cv_summary if r["candidate_key"] == selected.key
                ),
                "selected_validation": next(
                    r for r in val_summary if r["candidate_key"] == selected.key
                ),
            }
        )
        if world_dir is not None:
            write_csv(world_dir / "cv_metrics.csv.gz", cv_rows)
            write_csv(world_dir / "cv_predictions.csv.gz", predictions)
            write_json(world_dir / "cv_models.json.gz", models)
            write_json(world_dir / "cv_source_lineage.json.gz", lineage)
            write_json(
                world_dir / "candidate_summaries.json",
                {"cv": cv_summary, "validation": val_summary},
            )
            write_json(world_dir / "sensitivity_summary.json", results[-1])
    return results


def p_value_greater_equal(
    observed: float, null_values: Sequence[float]
) -> float | None:
    if not null_values:
        return None
    return (1 + sum(float(v) >= observed for v in null_values)) / (len(null_values) + 1)


def run_final_diagnostic(
    tensor: SourceTensor,
    family20_rows: Sequence[Mapping[str, Any]],
    selected_row: Mapping[str, Any],
    *,
    rows_per_class: int = ROWS_PER_CLASS,
    ordinary_nulls: int = 100,
    temporal_nulls: int = 100,
    bootstraps: int = 200,
    output_dir: Path | None = None,
    observed_cv_package: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    started = time.time()
    family_candidates = [candidate_from_dict(r) for r in family20_rows]
    selected_candidate = candidate_from_dict(selected_row)
    if selected_candidate.key != select_best_candidate(family20_rows)["candidate_key"]:
        raise ValueError("final recipe must equal the already frozen CV selection")
    if len(family_candidates) != 20:
        raise ValueError(
            "final diagnostic requires the frozen 20-candidate adaptive family"
        )
    observed_metrics, observed_predictions, observed_models = train_evaluate_validation(
        tensor,
        family_candidates,
        rows_per_class=rows_per_class,
        seed=PRIMARY_SEED,
        save_details=True,
        artifact_dir=output_dir / "observed" if output_dir is not None else None,
    )
    observed_summary = aggregate_validation_rows(observed_metrics)
    observed_selected = next(
        r for r in observed_summary if r["candidate_key"] == selected_candidate.key
    )
    observed_max = select_best_candidate(
        observed_summary, metric="diagnostic_validation_delta_log_loss"
    )
    nuisance = run_nuisance_control(
        tensor,
        rows_per_class,
        output_dir / "nuisance" if output_dir is not None else None,
    )
    sensitivity = run_assembly_sensitivity(
        tensor,
        family_candidates,
        selected_candidate,
        rows_per_class,
        output_dir / "assembly_sensitivity" if output_dir is not None else None,
    )
    influence = run_influence(
        tensor,
        selected_candidate,
        observed_selected,
        rows_per_class,
        output_dir / "influence" if output_dir is not None else None,
    )
    ordinary_rows = run_null_worlds(
        tensor,
        count=ordinary_nulls,
        temporal_half=False,
        rows_per_class=rows_per_class,
        seed0=50_000,
        artifact_dir=output_dir / "null_ordinary" if output_dir is not None else None,
    )
    temporal_rows = run_null_worlds(
        tensor,
        count=temporal_nulls,
        temporal_half=True,
        rows_per_class=rows_per_class,
        seed0=70_000,
        artifact_dir=output_dir / "null_temporal_half"
        if output_dir is not None
        else None,
    )
    bootstrap_rows = run_bootstraps(
        tensor,
        selected_candidate=selected_candidate,
        count=bootstraps,
        rows_per_class=rows_per_class,
        seed0=90_000,
        artifact_dir=output_dir / "source_bootstrap"
        if output_dir is not None
        else None,
    )
    observed_delta = float(observed_selected["diagnostic_validation_delta_log_loss"])
    ordinary_selected = [
        float(r["null_selected_diagnostic_delta_log_loss"]) for r in ordinary_rows
    ]
    ordinary_max = [
        float(r["null_max_family_diagnostic_delta_log_loss"]) for r in ordinary_rows
    ]
    temporal_selected = [
        float(r["null_selected_diagnostic_delta_log_loss"]) for r in temporal_rows
    ]
    temporal_max = [
        float(r["null_max_family_diagnostic_delta_log_loss"]) for r in temporal_rows
    ]
    result = {
        "stage": "final_diagnostic_null_bootstrap",
        "status": "complete",
        "validation_policy": "historically exposed development validation diagnostic; not pristine confirmation; round1/round2 selection was CV-only",
        "elapsed_seconds": time.time() - started,
        "rows_per_class": rows_per_class,
        "candidate_family_count": len(family_candidates),
        "selected_candidate": selected_candidate.as_dict(),
        "label_map": {"absent": 0, "present": 1, "positive_probability": "present"},
        "observed_cv_package": observed_cv_package,
        "observed_selected_diagnostic": observed_selected,
        "observed_max_family_diagnostic": observed_max,
        "ordinary_null_count": ordinary_nulls,
        "temporal_half_null_count": temporal_nulls,
        "bootstrap_count": bootstraps,
        "nuisance_control": nuisance,
        "assembly_sensitivity": sensitivity,
        "influence": influence,
        "bootstrap_policy": "fixed selected recipe refit; no model reselection; sensitivity quantiles, not selection-adjusted confidence intervals",
        "validation_source_pool_sizes": {
            "|".join(k): v
            for k, v in Counter(
                (r.endpoint_pair, r.session_id, r.label)
                for r in tensor.records
                if r.split == "validation"
            ).items()
        },
        "p_value_policy": "inclusive >= with plus-one correction; max-family null is compared to CV-selected observed statistic, not observed validation-best statistic",
        "p_values": {
            "ordinary_null_selected_policy_ge_observed_selected": p_value_greater_equal(
                observed_delta, ordinary_selected
            ),
            "ordinary_null_max_family_policy_ge_observed_selected": p_value_greater_equal(
                observed_delta, ordinary_max
            ),
            "temporal_half_null_selected_policy_ge_observed_selected": p_value_greater_equal(
                observed_delta, temporal_selected
            ),
            "temporal_half_null_max_family_policy_ge_observed_selected": p_value_greater_equal(
                observed_delta, temporal_max
            ),
        },
        "bootstrap_delta_quantiles": quantiles(
            [r["diagnostic_validation_delta_log_loss"] for r in bootstrap_rows]
        ),
        "tiny_panel_interval_downgrade": "2->1 and 4->1 are point/influence diagnostics only; aggregate intervals inherit this ceiling",
    }
    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)
        write_csv(
            output_dir / "final_observed_endpoint_metrics.csv.gz", observed_metrics
        )
        write_csv(
            output_dir / "final_observed_predictions.csv.gz", observed_predictions
        )
        write_json(output_dir / "final_observed_model_replays.json.gz", observed_models)
        write_json(
            output_dir / "final_observed_candidate_summary.json", observed_summary
        )
        write_json(
            output_dir / "null_world_summaries.json.gz", ordinary_rows + temporal_rows
        )
        write_json(output_dir / "bootstrap_summaries.json.gz", bootstrap_rows)
        write_json(output_dir / "label_map.json", result["label_map"])
        write_json(output_dir / "final_summary.json", result)
    return result


def quantiles(values: Sequence[float]) -> dict[str, float | None]:
    if not values:
        return {"q025": None, "q50": None, "q975": None}
    arr = np.asarray(values, dtype=float)
    return {
        "q025": float(np.quantile(arr, 0.025)),
        "q50": float(np.quantile(arr, 0.5)),
        "q975": float(np.quantile(arr, 0.975)),
    }


# ---------- synthetic fixture/smoke ----------


def synthetic_tensor(
    *,
    mean_difference: float,
    seed: int = 0,
    endpoints: Sequence[str] = ("2->1", "3->1"),
) -> SourceTensor:
    rng = np.random.default_rng(seed)
    records: list[SourceRecord] = []
    cells: list[str] = []
    X_rows: list[np.ndarray] = []
    E_rows: list[np.ndarray] = []
    M_rows: list[np.ndarray] = []
    # Two sessions per endpoint keep the product assembly nontrivial but fast.
    for ep_i, endpoint in enumerate(endpoints):
        for sess_i in range(2):
            session = f"syn{ep_i}{sess_i}_session01"
            sess_cells = [
                f"syn{ep_i}{sess_i}/session01/array/channel00{j}/cell01"
                for j in range(2)
            ]
            for c in sess_cells:
                if c not in cells:
                    cells.append(c)
            for split, n_per_label in (("train", 6), ("validation", 2)):
                for label in LABELS:
                    for j in range(n_per_label):
                        fold = -1 if split == "validation" else j % 3
                        sid = f"{session}_{endpoint.replace('->', 'to')}_{split}_{label}_{j}"
                        records.append(
                            SourceRecord(
                                source_trial_id=sid,
                                session_id=session,
                                split=split,
                                endpoint_pair=endpoint,
                                label=label,
                                inner_fold=fold,
                                trial_index=100 * ep_i
                                + 10 * sess_i
                                + j
                                + (1000 if split == "validation" else 0),
                                cue_duration_s=1.0,
                                cell_ids=tuple(sess_cells),
                                candidate_recording_group=f"{session}_synthetic",
                                simultaneity_status="synthetic_same_session_block",
                            )
                        )
    cell_index = {c: i for i, c in enumerate(cells)}
    for rec in records:
        x = np.full((len(cells), 10), np.nan, dtype=np.float32)
        e = np.full((len(cells), 10), np.nan, dtype=np.float32)
        m = np.zeros(len(cells), dtype=bool)
        for cid in rec.cell_ids:
            ci = cell_index[cid]
            base = 1.5 + 0.2 * (ci % 3)
            signal = (
                mean_difference if (rec.label == "present" and ci % 2 == 0) else 0.0
            )
            rates = np.full(10, base + signal, dtype=float)
            # Distributed weak signal: each cell alone is small, assembled panel is visible.
            counts = rng.poisson(rates * 0.1).astype(np.float32)
            x[ci, :] = counts
            e[ci, :] = 0.1
            m[ci] = True
        X_rows.append(x)
        E_rows.append(e)
        M_rows.append(m)
    return SourceTensor(
        np.stack(X_rows),
        np.stack(E_rows),
        np.stack(M_rows),
        tuple(records),
        tuple(cells),
        {"synthetic_mean_difference": mean_difference},
    )


def run_synthetic_smoke(
    output_dir: Path,
    *,
    ordinary_nulls: int = 2,
    temporal_nulls: int = 2,
    bootstraps: int = 2,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    started = time.time()
    positive = synthetic_tensor(mean_difference=3.0, seed=1)
    no_signal = synthetic_tensor(mean_difference=0.0, seed=2)
    save_source_tensor(output_dir / "synthetic_positive_source_tensors.npz", positive)
    save_source_tensor(output_dir / "synthetic_no_signal_source_tensors.npz", no_signal)
    pos_round1 = run_round1_cv(
        positive, rows_per_class=16, output_dir=output_dir / "positive" / "round1"
    )
    pos_round2 = run_round2_adapt(
        positive,
        pos_round1,
        rows_per_class=16,
        output_dir=output_dir / "positive" / "round2",
    )
    pos_final = run_final_diagnostic(
        positive,
        pos_round2["family20_summary_rows"],
        pos_round2["selected_family20_candidate"],
        rows_per_class=16,
        ordinary_nulls=ordinary_nulls,
        temporal_nulls=temporal_nulls,
        bootstraps=bootstraps,
        output_dir=output_dir / "positive" / "final",
    )
    null_round1 = run_round1_cv(
        no_signal, rows_per_class=16, output_dir=output_dir / "no_signal" / "round1"
    )
    null_round2 = run_round2_adapt(
        no_signal,
        null_round1,
        rows_per_class=16,
        output_dir=output_dir / "no_signal" / "round2",
    )
    null_final = run_final_diagnostic(
        no_signal,
        null_round2["family20_summary_rows"],
        null_round2["selected_family20_candidate"],
        rows_per_class=16,
        ordinary_nulls=ordinary_nulls,
        temporal_nulls=temporal_nulls,
        bootstraps=bootstraps,
        output_dir=output_dir / "no_signal" / "final",
    )
    elapsed = time.time() - started
    world_count = ordinary_nulls + temporal_nulls
    full_worlds = 200
    full_boots = 200
    tiny_units = max(1, world_count + bootstraps)
    estimated = elapsed * (full_worlds + full_boots) / tiny_units
    result = {
        "stage": "synthetic_smoke",
        "status": "complete",
        "elapsed_seconds": elapsed,
        "positive_selected_delta": pos_final["observed_selected_diagnostic"][
            "diagnostic_validation_delta_log_loss"
        ],
        "no_signal_selected_delta": null_final["observed_selected_diagnostic"][
            "diagnostic_validation_delta_log_loss"
        ],
        "ordinary_nulls": ordinary_nulls,
        "temporal_nulls": temporal_nulls,
        "bootstraps": bootstraps,
        "rough_full_protocol_runtime_seconds_estimate": estimated,
        "estimate_caveat": "linear extrapolation from tiny synthetic fixture; real endpoint products are still small, but logistic convergence can vary",
    }
    write_json(output_dir / "synthetic_smoke_summary.json", result)
    return result


# ---------- CLI ----------


def _load_round1(path: Path) -> dict[str, Any]:
    payload = read_json(path)
    if payload.get("stage") != "round1_cv_only_18_arm_screen":
        raise ValueError(f"not a round1 summary: {path}")
    return payload


def _load_round2(path: Path) -> dict[str, Any]:
    payload = read_json(path)
    if (
        "family20_summary_rows" not in payload
        or "selected_family20_candidate" not in payload
    ):
        raise ValueError(f"not a round2/family20 summary: {path}")
    return payload


def cmd_verify_support(args: argparse.Namespace) -> dict[str, Any]:
    started = time.time()
    summary = verify_prefit_support(args.selected_sources, args.support_audit)
    output = args.output_dir
    output.mkdir(parents=True, exist_ok=True)
    write_json(
        output / "support_verification.json",
        {
            **summary,
            "runtime": runtime_manifest(
                sys.argv,
                {
                    "selected_sources": args.selected_sources,
                    "support_audit": args.support_audit,
                },
            ),
            "elapsed_seconds": time.time() - started,
        },
    )
    return summary


def cmd_export_bins(args: argparse.Namespace) -> dict[str, Any]:
    return export_binned_cue_counts(
        import_dir=args.import_dir,
        split_dir=args.split_dir,
        selected_sources_path=args.selected_sources,
        output_dir=args.output_dir,
        authorized_phase=args.authorized_phase,
    )


def cmd_round1(args: argparse.Namespace) -> dict[str, Any]:
    require_authorization(args.authorized_phase, "round1 biological CV fitting")
    if args.rows_per_class != ROWS_PER_CLASS:
        raise ValueError("biological protocol requires 128 rows per class")
    tensor = load_source_tensor(args.source_tensor, strict_expected=True)
    return run_round1_cv(
        tensor,
        rows_per_class=args.rows_per_class,
        seed=PRIMARY_SEED,
        output_dir=args.output_dir,
    )


def cmd_round2(args: argparse.Namespace) -> dict[str, Any]:
    require_authorization(args.authorized_phase, "round2 biological CV fitting")
    if args.rows_per_class != ROWS_PER_CLASS:
        raise ValueError("biological protocol requires 128 rows per class")
    tensor = load_source_tensor(args.source_tensor, strict_expected=True)
    return run_round2_adapt(
        tensor,
        _load_round1(args.round1_summary),
        rows_per_class=args.rows_per_class,
        seed=PRIMARY_SEED,
        output_dir=args.output_dir,
        plan_only=args.plan_only,
    )


def package_observed_cv(
    freeze: Mapping[str, Any], round2_path: Path, tensor_path: Path, output_dir: Path
) -> dict[str, Any]:
    """Copy the already fitted CV evidence without fitting or changing selection."""
    first_paths = [
        Path(p) for p in freeze["input_hashes"] if Path(p).name == "round1_summary.json"
    ]
    if len(first_paths) != 1:
        raise ValueError("selection freeze must name exactly one Round1 summary")
    # ponytail: fixed run layout; keep historical paths in receipts, not dependencies.
    first = round2_path.parent.parent / "round1/round1_summary.json"
    if sha256_file(first) != freeze["input_hashes"][str(first_paths[0])]:
        raise ValueError("Round1 summary differs from selection freeze")
    destination = output_dir / "observed_cv"
    destination.mkdir(parents=True, exist_ok=False)
    copied = {}
    for phase, summary_path in (("round1", first), ("round2", round2_path)):
        phase_dir = destination / phase
        phase_dir.mkdir()
        names = [
            f"{phase}_summary.json",
            f"{phase}_cv_metrics.csv.gz",
            f"{phase}_cv_predictions.csv.gz",
            f"{phase}_model_replays.json.gz",
            f"{phase}_source_lineage.json.gz",
            "command_start.json",
            "command_result.json",
        ]
        for name in names:
            source = summary_path.parent / name
            target = phase_dir / name
            shutil.copyfile(source, target)
            copied[str(target.relative_to(output_dir))] = {
                "source": str(source),
                "sha256": sha256_file(target),
            }
    snapshot = (
        REPO_ROOT
        / "docs/reports/archive/path-preprocessing-20260908/code/gated-export-round1"
    )
    originals = read_json(first.parent / "command_start.json")["runtime"]["code_hashes"]
    for key, name in (
        ("driver", Path(__file__).name),
        ("split_filtered_access", "place195_split_filtered_access.py"),
        ("v7_v8_neural_helpers", "place195_v7_v8_neural_experiments.py"),
    ):
        source = snapshot / f"{name}.txt"
        if sha256_file(source) != originals[key]:
            raise ValueError(f"original CV code snapshot mismatch: {name}")
        target = destination / name
        shutil.copyfile(source, target)
        copied[str(target.relative_to(output_dir))] = {
            "source": str(source),
            "sha256": sha256_file(target),
        }
    inputs = destination / "inputs"
    inputs.mkdir()
    for source in (
        tensor_path,
        tensor_path.parent / "export_manifest.json",
        MANAGER_ROOT / "prefit-selected-sources.json",
        MANAGER_ROOT / "PROTOCOL-FROZEN-V1.md",
        MANAGER_ROOT / "SELECTION-FROZEN.json",
    ):
        target = inputs / source.name
        shutil.copyfile(source, target)
        copied[str(target.relative_to(output_dir))] = {
            "source": str(source),
            "sha256": sha256_file(target),
        }
    result = {
        "policy": "frozen Round1+Round2 replay package copied without refitting; 300 original CV models",
        "new_fits": 0,
        "files": copied,
    }
    write_json(destination / "manifest.json", result)
    return result


def cmd_final(args: argparse.Namespace) -> dict[str, Any]:
    if args.authorized_phase != FINAL_REVIEW_GATE_TOKEN:
        raise PermissionError(
            "final biological inference requires separate independent final-stage review"
        )
    if (
        args.rows_per_class,
        args.ordinary_nulls,
        args.temporal_nulls,
        args.bootstraps,
    ) != (128, 100, 100, 200):
        raise ValueError(
            "frozen biological policy: 128 rows/class, 100 ordinary+100 temporal nulls, 200 bootstraps"
        )
    freeze = read_json(MANAGER_ROOT / "SELECTION-FROZEN.json")
    for path, frozen_name in (
        (args.source_tensor, "source_tensors.npz"),
        (args.round2_summary, "round2_summary.json"),
    ):
        expected = [
            value
            for name, value in freeze["input_hashes"].items()
            if Path(name).name == frozen_name
        ]
        if len(expected) != 1 or expected[0] != sha256_file(path):
            raise ValueError(
                f"input differs from pre-diagnostic selection freeze: {path}"
            )
    tensor = load_source_tensor(args.source_tensor, strict_expected=True)
    round2 = _load_round2(args.round2_summary)
    if round2["selected_family20_candidate"] != freeze["selected_candidate"]:
        raise ValueError(
            "final recipe differs from the pre-diagnostic selection freeze"
        )
    package = package_observed_cv(
        freeze, args.round2_summary, args.source_tensor, args.output_dir
    )
    return run_final_diagnostic(
        tensor,
        round2["family20_summary_rows"],
        round2["selected_family20_candidate"],
        rows_per_class=args.rows_per_class,
        ordinary_nulls=args.ordinary_nulls,
        temporal_nulls=args.temporal_nulls,
        bootstraps=args.bootstraps,
        output_dir=args.output_dir,
        observed_cv_package=package,
    )


def cmd_synthetic_smoke(args: argparse.Namespace) -> dict[str, Any]:
    return run_synthetic_smoke(
        args.output_dir,
        ordinary_nulls=args.ordinary_nulls,
        temporal_nulls=args.temporal_nulls,
        bootstraps=args.bootstraps,
    )


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("verify-support")
    p.add_argument(
        "--selected-sources",
        type=Path,
        default=MANAGER_ROOT / "prefit-selected-sources.json",
    )
    p.add_argument(
        "--support-audit", type=Path, default=MANAGER_ROOT / "prefit-support-audit.json"
    )
    p.add_argument("--output-dir", type=Path, required=True)
    p.set_defaults(func=cmd_verify_support)

    p = sub.add_parser("export-bins")
    p.add_argument("--import-dir", type=Path, required=True)
    p.add_argument("--split-dir", type=Path, required=True)
    p.add_argument(
        "--selected-sources",
        type=Path,
        default=MANAGER_ROOT / "prefit-selected-sources.json",
    )
    p.add_argument("--output-dir", type=Path, required=True)
    p.add_argument("--authorized-phase", required=False)
    p.set_defaults(func=cmd_export_bins)

    p = sub.add_parser("round1-cv")
    p.add_argument("--source-tensor", type=Path, required=True)
    p.add_argument("--output-dir", type=Path, required=True)
    p.add_argument("--rows-per-class", type=int, default=ROWS_PER_CLASS)
    p.add_argument("--authorized-phase", required=False)
    p.set_defaults(func=cmd_round1)

    p = sub.add_parser("round2-adapt")
    p.add_argument("--source-tensor", type=Path, required=True)
    p.add_argument("--round1-summary", type=Path, required=True)
    p.add_argument("--output-dir", type=Path, required=True)
    p.add_argument("--rows-per-class", type=int, default=ROWS_PER_CLASS)
    p.add_argument("--plan-only", action="store_true")
    p.add_argument("--authorized-phase", required=False)
    p.set_defaults(func=cmd_round2)

    p = sub.add_parser("final-diagnostic")
    p.add_argument("--source-tensor", type=Path, required=True)
    p.add_argument("--round2-summary", type=Path, required=True)
    p.add_argument("--output-dir", type=Path, required=True)
    p.add_argument("--rows-per-class", type=int, default=ROWS_PER_CLASS)
    p.add_argument("--ordinary-nulls", type=int, default=100)
    p.add_argument("--temporal-nulls", type=int, default=100)
    p.add_argument("--bootstraps", type=int, default=200)
    p.add_argument("--authorized-phase", required=False)
    p.set_defaults(func=cmd_final)

    p = sub.add_parser("synthetic-smoke")
    p.add_argument("--output-dir", type=Path, required=True)
    p.add_argument("--ordinary-nulls", type=int, default=2)
    p.add_argument("--temporal-nulls", type=int, default=2)
    p.add_argument("--bootstraps", type=int, default=2)
    p.set_defaults(func=cmd_synthetic_smoke)

    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    global ACTIVE_PROGRESS_PATH, FIT_COUNT
    args = parse_args(argv)
    started = time.time()
    # Outside the failure handler: rejected output paths must never receive writes.
    args.output_dir = prepare_cli_output_dir(args.output_dir)
    command = sys.argv if argv is None else [str(Path(__file__)), *argv]
    inputs = input_paths_for_args(args)
    try:
        runtime = runtime_manifest(command, inputs)
        write_json(
            args.output_dir / "command_start.json",
            {
                "status": "started",
                "runtime": runtime,
                "configuration": {k: v for k, v in vars(args).items() if k != "func"},
            },
        )
        ACTIVE_PROGRESS_PATH = args.output_dir / "progress.jsonl"
        FIT_COUNT = 0
        result = args.func(args)
    except Exception as exc:
        failure = {
            "status": "failed",
            "command": sys.argv,
            "elapsed_seconds": time.time() - started,
            "error_type": type(exc).__name__,
            "error": str(exc),
            "traceback": traceback.format_exc(),
        }
        output_dir = getattr(args, "output_dir", None)
        if isinstance(output_dir, Path):
            output_dir.mkdir(parents=True, exist_ok=True)
            write_json(output_dir / "failure.json", failure)
        raise
    finally:
        ACTIVE_PROGRESS_PATH = None
    output_dir = getattr(args, "output_dir", None)
    if isinstance(output_dir, Path):
        write_json(
            output_dir / "command_result.json",
            {
                "result": result,
                "runtime": runtime,
                "fit_count": FIT_COUNT,
                "elapsed_seconds": time.time() - started,
            },
        )
    print(json.dumps(jsonable(result), sort_keys=True))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
