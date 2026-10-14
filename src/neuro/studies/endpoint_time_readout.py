#!/usr/bin/env python3
# pyright: reportMissingImports=false
# ruff: noqa: E402,I001
"""Bounded endpoint cue-time readout runner.

Implements the reviewed protocol in
``docs/reports/cebra-endpoint-time-readout-20261006/protocol.md``.  The
biological run is gated by accepted-artifact parity, training-only navigation
extraction, and a hash-bound prefit approval.  Tests use invented arrays only.
"""

from __future__ import annotations

import argparse
import contextlib
import csv
import gzip
import hashlib
import json
import math
import os
import random
import sys
import time
from collections import Counter, defaultdict
from collections.abc import Iterable, Iterator, Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime, timezone
from importlib.metadata import version as package_version
from pathlib import Path
from typing import Any, cast

import joblib
import numpy as np
import torch
from sklearn.decomposition import PCA
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, balanced_accuracy_score, f1_score, log_loss
from sklearn.preprocessing import StandardScaler

from neuro.execution import ensure_fresh_dir, snapshot_sources
from neuro.execution import sha256_file as _sha256_file
from neuro.studies.full_trial_transfer import (  # reuse reviewed CEBRA-time pieces
    CebraVectorDataset,
    check_deadline,
    embed_cue as _embed_cue,
    make_solver,
    train_encoder as _train_encoder,
)
from neuro.raw_io import (
    _codes_at,
    _times_at,
    read_ripple_trials,
    read_spiketrain,
    spikes_in_window,
    _csv_value as imported_csv_value,
)
from neuro.neural_inputs import bin_events, session_from_cell
from neuro.place195_split_access import SplitFilteredAccess
from neuro.provenance import REPOSITORY_ROOT, study_sources

CANONICAL_ROOT = Path("/home/hongyi-home-lab/neuro_science")
ACCEPTED_ENDPOINT_ROOT = CANONICAL_ROOT / "outputs/start-goal-cebra-20260907"
OUTPUT_ROOT = CANONICAL_ROOT / "outputs/cebra-endpoint-time-readout-20261006"
DOC_DIR = REPOSITORY_ROOT / "docs/reports/cebra-endpoint-time-readout-20261006"
PROTOCOL_PATH = DOC_DIR / "protocol.md"
SCRIPT_PATH = Path(__file__).resolve()
IMPORT_DIR = (
    CANONICAL_ROOT
    / "outputs/prospective_path_first_run/place195-all-sessions-20260830-v4"
)
SPLIT_DIR = (
    CANONICAL_ROOT / "outputs/prospective_path_first_run/place195-splits-20260830-v3"
)

PAIRS = tuple((s, g) for s in range(1, 7) for g in range(1, 7) if s != g)
PAIR_LABELS = tuple(f"{s}->{g}" for s, g in PAIRS)
PAIR_TO_INT = {label: idx for idx, label in enumerate(PAIR_LABELS)}
TARGETS = ("pair30", "start6", "goal6")
WINDOWS = tuple(f"bin{idx:02d}" for idx in range(10)) + ("wholecue",)
BIN_WINDOWS = WINDOWS[:-1]
LOGISTIC_REPRESENTATIONS = ("raw", "pca8", "cebra_cue", "cebra_joint")
REPRESENTATIONS = LOGISTIC_REPRESENTATIONS + ("raw_svd_lda",)
SEEDS = (0, 1, 2)
NULL_SEEDS = tuple(range(50000, 50020))
ROWS_PER_PAIR_TRAIN = 16
ROWS_PER_PAIR_DEVELOPMENT = 8
CUE_BINS = 10
BIN_WIDTH_S = 0.1
CEBRA_UPDATES = 1000
CEBRA_DIM = 8
THREADPOOL_LIMIT = 2
MAX_RUN_SECONDS = 90 * 60
OUTPUT_LIMIT_GIB = 10.0
EXPECTED_TRAIN_SOURCES = 12_288
EXPECTED_DEVELOPMENT_SOURCES = 3_265
EXPECTED_CELLS = 195
EXPECTED_SESSIONS = 58
EXPECTED_ENCODER_FITS = 2 * len(SEEDS) * (1 + len(NULL_SEEDS))
EXPECTED_PCA_FITS = len(SEEDS) * (1 + len(NULL_SEEDS))
EXPECTED_READOUT_FITS = (
    len(REPRESENTATIONS)
    * len(TARGETS)
    * len(WINDOWS)
    * len(SEEDS)
    * (1 + len(NULL_SEEDS))
)
RAW_HASH_CHUNK = 1024 * 1024

FITS_BLOCKED = False


@dataclass(frozen=True)
class EndpointSource:
    source_trial_id: str
    session_id: str
    split: str  # "train" or "development"; historical CSV used "validation".
    stored_split: str
    label: str
    trial_index: int | None = None


@dataclass(frozen=True)
class EndpointCohort:
    counts: np.ndarray
    observed: np.ndarray
    exposure: np.ndarray
    source_ids: list[str]
    cells: list[str]
    metas: list[EndpointSource]
    source_index: dict[str, int]


@dataclass(frozen=True)
class EndpointNavData:
    path: Path
    source_ids: list[str]
    source_sessions: list[str]
    source_labels: list[str]
    trial_indices: np.ndarray
    offsets: np.ndarray
    n_bins: np.ndarray
    counts_flat: np.ndarray
    exposure_flat: np.ndarray
    observed_flat: np.ndarray
    cells: list[str]
    source_index: dict[str, int]


@dataclass(frozen=True)
class RowBundle:
    X_cue: np.ndarray
    y_pair: np.ndarray
    weights: np.ndarray | None
    manifest: list[dict[str, str]]
    plans: list[dict[str, Any]]


@dataclass(frozen=True)
class EndpointPairBank:
    cue_samples: np.ndarray
    cue_labels: np.ndarray
    cue_pairs: np.ndarray
    cue_samples_by_row: list[np.ndarray]
    cue_pairs_by_row: list[np.ndarray]
    nav_samples: np.ndarray
    nav_labels: np.ndarray
    nav_pairs: np.ndarray
    nav_samples_by_row: list[np.ndarray]
    nav_pairs_by_row: list[np.ndarray]
    row_labels: np.ndarray
    pair_lineage: dict[str, np.ndarray]
    coverage_rows: list[dict[str, Any]]


@dataclass(frozen=True)
class FeatureBundle:
    world: str
    world_index: int
    seed: int
    train_bundle: RowBundle
    development_bundle: RowBundle
    features_train: dict[str, np.ndarray]
    features_development: dict[str, np.ndarray]
    checked_files: list[str]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    return _sha256_file(path, chunk_size=RAW_HASH_CHUNK)


def stable_hash(payload: Any) -> str:
    return hashlib.sha256(
        json.dumps(jsonable(payload), sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def jsonable(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, Mapping):
        return {str(k): jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [jsonable(v) for v in value]
    return value


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(jsonable(payload), indent=2, sort_keys=True) + "\n")


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"unable to read JSON file: {path}") from exc


def write_csv(
    path: Path,
    rows: Sequence[Mapping[str, Any]],
    fieldnames: Sequence[str] | None = None,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if fieldnames is None:
        fields: list[str] = []
        for row in rows:
            for key in row:
                if key not in fields:
                    fields.append(key)
        fieldnames = fields
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: jsonable(row.get(key, "")) for key in fieldnames})


def read_csv(path: Path) -> list[dict[str, str]]:
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", newline="") as handle:  # type: ignore[arg-type]
        return list(csv.DictReader(handle))


def set_thread_limits() -> None:
    os.environ.setdefault("OMP_NUM_THREADS", str(THREADPOOL_LIMIT))
    os.environ.setdefault("OPENBLAS_NUM_THREADS", str(THREADPOOL_LIMIT))
    os.environ.setdefault("MKL_NUM_THREADS", str(THREADPOOL_LIMIT))
    torch.set_num_threads(THREADPOOL_LIMIT)


def directory_size_bytes(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(p.stat().st_size for p in path.rglob("*") if p.is_file())


def check_output_budget(path: Path, *, limit_gib: float = OUTPUT_LIMIT_GIB) -> None:
    size = directory_size_bytes(path)
    if size > limit_gib * (1024**3):
        raise RuntimeError(f"output budget exceeded: {size} bytes > {limit_gib} GiB")


def select_device(requested: str | None) -> str:
    if requested in (None, "", "cpu"):
        return "cpu"
    if requested != "cuda":
        raise ValueError("device must be cpu or cuda")
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA explicitly requested but not available")
    try:
        free, total = torch.cuda.mem_get_info()
    except Exception as exc:  # pragma: no cover - depends on host driver
        raise RuntimeError(
            "CUDA explicitly requested but memory status failed"
        ) from exc
    if total <= 0 or free / total < 0.80:
        raise RuntimeError(
            f"CUDA explicitly requested but not free enough: {free}/{total} bytes"
        )
    return "cuda"


def check_declared_budget() -> dict[str, int]:
    budget = {
        "worlds": 1 + len(NULL_SEEDS),
        "encoder_fits": EXPECTED_ENCODER_FITS,
        "pca_fits": EXPECTED_PCA_FITS,
        "readout_fits": EXPECTED_READOUT_FITS,
        "targets": len(TARGETS),
        "windows": len(WINDOWS),
        "representations": len(REPRESENTATIONS),
    }
    if budget != {
        "worlds": 21,
        "encoder_fits": 126,
        "pca_fits": 63,
        "readout_fits": 10395,
        "targets": 3,
        "windows": 11,
        "representations": 5,
    }:
        raise RuntimeError(f"declared protocol budget drifted: {budget}")
    return budget


def safe_child(root: Path, relative: str) -> Path:
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()):
        raise RuntimeError(f"manifest path escapes artifact root: {relative}")
    return path


def verify_accepted_endpoint_artifacts(
    root: Path = ACCEPTED_ENDPOINT_ROOT,
) -> dict[str, Any]:
    manifest_path = root / "artifact_hashes.json"
    if not manifest_path.is_file():
        raise RuntimeError(f"missing accepted artifact hash manifest: {manifest_path}")
    manifest = read_json(manifest_path)
    required = {
        "source_tensor.npz",
        "source_splits.csv",
        "source_support.csv",
        "source_audit.json",
        "inputs.json",
        "observed/seed0/pseudo_arrays.npz",
        "observed/seed1/pseudo_arrays.npz",
        "observed/seed2/pseudo_arrays.npz",
        "observed/seed0/pseudo_components.csv",
        "observed/seed1/pseudo_components.csv",
        "observed/seed2/pseudo_components.csv",
    }
    missing_manifest = sorted(required - set(manifest))
    if missing_manifest:
        raise RuntimeError(
            f"accepted manifest missing required files: {missing_manifest}"
        )
    checked: list[str] = []
    failures: list[str] = []
    for relative, expected in sorted(manifest.items()):
        path = safe_child(root, relative)
        if not path.is_file():
            failures.append(f"missing: {relative}")
            continue
        observed = sha256_file(path)
        if observed != expected:
            failures.append(f"hash mismatch {relative}: {observed} != {expected}")
        checked.append(relative)
    if failures:
        raise RuntimeError(
            "accepted artifact hash check failed: " + "; ".join(failures[:5])
        )
    return {
        "root": str(root),
        "manifest_sha256": sha256_file(manifest_path),
        "checked_files": len(checked),
        "required_files": sorted(required),
    }


def _logical_split(value: str) -> str:
    if value == "train":
        return "train"
    if value in {"validation", "development"}:
        return "development"
    raise RuntimeError(f"forbidden endpoint split: {value}")


def load_endpoint_cohort(
    root: Path = ACCEPTED_ENDPOINT_ROOT,
    *,
    strict_expected: bool = True,
) -> EndpointCohort:
    verify_accepted_endpoint_artifacts(root)
    with np.load(root / "source_tensor.npz", allow_pickle=False) as data:
        required = {"counts", "observed", "exposure", "source_ids", "cells"}
        missing = required - set(data.files)
        if missing:
            raise RuntimeError(f"source tensor missing keys: {sorted(missing)}")
        counts = np.asarray(data["counts"], dtype=np.float32)
        observed = np.asarray(data["observed"], dtype=bool)
        exposure = np.asarray(data["exposure"], dtype=np.float32)
        source_ids = [str(x) for x in data["source_ids"].tolist()]
        cells = [str(x) for x in data["cells"].tolist()]
    if counts.ndim != 3 or counts.shape[2] != CUE_BINS:
        raise RuntimeError(f"unexpected endpoint counts shape: {counts.shape}")
    if observed.shape != counts.shape[:2]:
        raise RuntimeError("endpoint observed mask shape mismatch")
    if exposure.shape != (counts.shape[0], CUE_BINS):
        raise RuntimeError("endpoint exposure shape mismatch")
    if len(source_ids) != counts.shape[0] or len(set(source_ids)) != len(source_ids):
        raise RuntimeError("endpoint source id count/uniqueness mismatch")
    if len(cells) != counts.shape[1] or len(set(cells)) != len(cells):
        raise RuntimeError("endpoint cell count/uniqueness mismatch")

    rows = read_csv(root / "source_splits.csv")
    row_by_sid = {row["source_trial_id"]: row for row in rows}
    if set(row_by_sid) != set(source_ids):
        raise RuntimeError("source_splits.csv does not match source_tensor source_ids")
    metas: list[EndpointSource] = []
    for sid in source_ids:
        row = row_by_sid[sid]
        label = row["label"]
        if label not in PAIR_TO_INT:
            raise RuntimeError(f"unexpected endpoint label {label!r} for {sid}")
        original_split = row.get("original_split")
        if original_split != "train":
            raise RuntimeError(
                f"endpoint artifact contains outer non-train source {sid}"
            )
        metas.append(
            EndpointSource(
                source_trial_id=sid,
                session_id=row["session_id"],
                split=_logical_split(row["split"]),
                stored_split=row["split"],
                label=label,
                trial_index=checked_int(row["trial_index"])
                if row.get("trial_index")
                else None,
            )
        )
    sessions = {m.session_id for m in metas}
    counts_by_split = Counter(m.split for m in metas)
    if strict_expected:
        expected_shape = (
            EXPECTED_TRAIN_SOURCES + EXPECTED_DEVELOPMENT_SOURCES,
            EXPECTED_CELLS,
            CUE_BINS,
        )
        if counts.shape != expected_shape:
            raise RuntimeError(f"endpoint source tensor shape drifted: {counts.shape}")
        if len(sessions) != EXPECTED_SESSIONS:
            raise RuntimeError(f"endpoint session count drifted: {len(sessions)}")
        if counts_by_split != {
            "train": EXPECTED_TRAIN_SOURCES,
            "development": EXPECTED_DEVELOPMENT_SOURCES,
        }:
            raise RuntimeError(f"endpoint split counts drifted: {counts_by_split}")
    expected_mask = np.asarray(
        [
            [session_from_cell(cell) == meta.session_id for cell in cells]
            for meta in metas
        ],
        dtype=bool,
    )
    if not np.array_equal(observed, expected_mask):
        raise RuntimeError("endpoint observed mask does not match cell/session lineage")
    if not np.isfinite(counts[observed]).all() or (counts[observed] < 0).any():
        raise RuntimeError("endpoint cue counts contain invalid observed values")
    if np.isfinite(counts[~observed]).any():
        raise RuntimeError(
            "endpoint absent-session cells must remain masked, not zero-filled"
        )
    return EndpointCohort(
        counts=counts,
        observed=observed,
        exposure=exposure,
        source_ids=source_ids,
        cells=cells,
        metas=metas,
        source_index={sid: idx for idx, sid in enumerate(source_ids)},
    )


def cohort_sessions(cells: Sequence[str]) -> list[str]:
    return sorted({session_from_cell(cell) for cell in cells})


def source_labels_for_world(
    metas: Sequence[EndpointSource], shuffled: Mapping[str, str] | None
) -> dict[str, str]:
    return {
        meta.source_trial_id: (
            shuffled.get(meta.source_trial_id, meta.label) if shuffled else meta.label
        )
        for meta in metas
    }


def shuffle_pair_labels_within_session_split(
    metas: Sequence[EndpointSource], *, seed: int
) -> tuple[dict[str, str], dict[str, Any]]:
    rng = random.Random(seed)
    grouped: dict[tuple[str, str], list[EndpointSource]] = defaultdict(list)
    for meta in metas:
        grouped[(meta.session_id, meta.split)].append(meta)
    out: dict[str, str] = {}
    rows = []
    changed = 0
    total = 0
    for (session_id, split), group in sorted(grouped.items()):
        labels = [meta.label for meta in group]
        shuffled = labels[:]
        rng.shuffle(shuffled)
        local_changed = sum(a != b for a, b in zip(labels, shuffled, strict=True))
        changed += local_changed
        total += len(group)
        for meta, label in zip(group, shuffled, strict=True):
            if label not in PAIR_TO_INT:
                raise RuntimeError("shuffled labels must remain ordered endpoint pairs")
            out[meta.source_trial_id] = label
        rows.append(
            {
                "session_id": session_id,
                "split": split,
                "n": len(group),
                "changed": local_changed,
                "unique_pair_labels": len(set(labels)),
            }
        )
    return out, {
        "seed": seed,
        "group_fields": ["session_id", "inner_split"],
        "shuffled_pair_label_hash": stable_hash(out),
        "actual_changed_count": changed,
        "actual_changed_fraction": changed / total if total else 0.0,
        "strata": rows,
    }


def eligible_sources(
    metas: Sequence[EndpointSource],
    cells: Sequence[str],
    *,
    split: str,
    label: str,
    shuffled: Mapping[str, str] | None = None,
) -> dict[str, list[str]]:
    labels = source_labels_for_world(metas, shuffled)
    by_session = {session: [] for session in cohort_sessions(cells)}
    for meta in metas:
        if meta.split == split and labels[meta.source_trial_id] == label:
            by_session[meta.session_id].append(meta.source_trial_id)
    empty = [session for session, values in by_session.items() if not values]
    if empty:
        raise RuntimeError(
            f"cannot assemble {split}/{label}; empty sessions {empty[:5]}"
        )
    return by_session


def make_pair_balanced_plans(
    metas: Sequence[EndpointSource],
    cells: Sequence[str],
    *,
    split: str,
    rows_per_pair: int,
    seed: int,
    shuffled: Mapping[str, str] | None = None,
) -> list[dict[str, Any]]:
    if split not in {"train", "development"}:
        raise ValueError(split)
    sessions = cohort_sessions(cells)
    plans: list[dict[str, Any]] = []
    stored_split = "validation" if split == "development" else "train"
    split_offset = 1 if split == "development" else 0
    for label_id, label in enumerate(PAIR_LABELS):
        rng = np.random.default_rng(seed * 1000 + label_id * 2 + split_offset)
        by_session = eligible_sources(
            metas, cells, split=split, label=label, shuffled=shuffled
        )
        for row_number in range(rows_per_pair):
            sources = {
                session: str(rng.choice(by_session[session])) for session in sessions
            }
            plans.append(
                {
                    "split": split,
                    "stored_split": stored_split,
                    "label": label,
                    "pair_id": label_id,
                    "row_number": row_number,
                    "row_id": f"{split}:{label}:sample{row_number:05d}",
                    "sources": sources,
                    "draw_seed": seed * 1000 + label_id * 2 + split_offset,
                }
            )
    return plans


def materialize_rows(
    cohort: EndpointCohort, plans: Sequence[Mapping[str, Any]]
) -> RowBundle:
    cell_sessions = np.asarray([session_from_cell(cell) for cell in cohort.cells])
    X = np.empty((len(plans), len(cohort.cells), CUE_BINS), dtype=np.float32)
    y = np.empty(len(plans), dtype=np.int64)
    manifest: list[dict[str, str]] = []
    meta_by_sid = {meta.source_trial_id: meta for meta in cohort.metas}
    for row_idx, plan in enumerate(plans):
        label = str(plan["label"])
        y[row_idx] = PAIR_TO_INT[label]
        X[row_idx] = np.nan
        for session, sid in dict(plan["sources"]).items():
            meta = meta_by_sid[sid]
            if meta.split != plan["split"] or meta.session_id != session:
                raise RuntimeError("assembly source split/session mismatch")
            source_idx = cohort.source_index[sid]
            cell_idx = np.flatnonzero(cell_sessions == session)
            if not np.all(cohort.observed[source_idx, cell_idx]):
                raise RuntimeError(f"observed mask failure for {sid}/{session}")
            X[row_idx, cell_idx, :] = cohort.counts[source_idx, cell_idx, :]
            manifest.append(
                {
                    "seed": str(plan["draw_seed"]),
                    "split": str(plan["stored_split"]),
                    "label": label,
                    "pseudo_row": str(
                        PAIR_TO_INT[label] * rows_per_split(plan)
                        + checked_int(plan["row_number"])
                    ),
                    "session_id": session,
                    "source_trial_id": sid,
                    "assembly_seed": str(seed_from_plan(plan)),
                    "row_id": str(plan["row_id"]),
                }
            )
        if np.isnan(X[row_idx]).any():
            raise RuntimeError("pseudo row has unavailable cells; refusing imputation")
    return RowBundle(
        X_cue=X,
        y_pair=y,
        weights=exact_class_weights(y),
        manifest=manifest,
        plans=[dict(plan) for plan in plans],
    )


def rows_per_split(plan: Mapping[str, Any]) -> int:
    return (
        ROWS_PER_PAIR_TRAIN if plan["split"] == "train" else ROWS_PER_PAIR_DEVELOPMENT
    )


def seed_from_plan(plan: Mapping[str, Any]) -> int:
    draw_seed = checked_int(plan["draw_seed"])
    label_id = checked_int(plan["pair_id"])
    split_offset = 1 if plan["split"] == "development" else 0
    return (draw_seed - label_id * 2 - split_offset) // 1000


def assemble_world_seed(
    cohort: EndpointCohort,
    *,
    seed: int,
    shuffled: Mapping[str, str] | None = None,
) -> tuple[RowBundle, RowBundle]:
    train_plans = make_pair_balanced_plans(
        cohort.metas,
        cohort.cells,
        split="train",
        rows_per_pair=ROWS_PER_PAIR_TRAIN,
        seed=seed,
        shuffled=shuffled,
    )
    development_plans = make_pair_balanced_plans(
        cohort.metas,
        cohort.cells,
        split="development",
        rows_per_pair=ROWS_PER_PAIR_DEVELOPMENT,
        seed=seed,
        shuffled=shuffled,
    )
    train = materialize_rows(cohort, train_plans)
    development = materialize_rows(cohort, development_plans)
    used_train = {row["source_trial_id"] for row in train.manifest}
    used_dev = {row["source_trial_id"] for row in development.manifest}
    if used_train & used_dev:
        raise RuntimeError("source leakage across training/development assemblies")
    return train, development


def verify_observed_assembly_parity(
    cohort: EndpointCohort,
    root: Path = ACCEPTED_ENDPOINT_ROOT,
    *,
    seeds: Sequence[int] = SEEDS,
) -> dict[str, Any]:
    checked = []
    for seed in seeds:
        train, development = assemble_world_seed(cohort, seed=seed)
        seed_dir = root / "observed" / f"seed{seed}"
        with np.load(seed_dir / "pseudo_arrays.npz", allow_pickle=False) as saved:
            np.testing.assert_array_equal(saved["X_train"], train.X_cue)
            np.testing.assert_array_equal(saved["y_train"], train.y_pair)
            np.testing.assert_array_equal(saved["X_validation"], development.X_cue)
            np.testing.assert_array_equal(saved["y_validation"], development.y_pair)
        saved_manifest = read_csv(seed_dir / "pseudo_components.csv")
        expected_fields = tuple(key for key in train.manifest[0] if key != "row_id")
        if not saved_manifest or any(
            tuple(row) != expected_fields for row in saved_manifest
        ):
            raise RuntimeError(
                f"source assembly manifest schema mismatch for seed {seed}"
            )
        reconstructed = [
            {key: row[key] for key in expected_fields}
            for row in train.manifest + development.manifest
        ]
        for row in reconstructed:
            row.pop("row_id", None)
        if saved_manifest != reconstructed:
            raise RuntimeError(f"source assembly lineage parity failed for seed {seed}")
        checked.append(
            {
                "seed": seed,
                "train_rows": checked_int(train.X_cue.shape[0]),
                "development_rows": checked_int(development.X_cue.shape[0]),
                "manifest_rows": len(saved_manifest),
            }
        )
    return {"status": "passed", "checked_seed_assemblies": checked}


def exact_class_weights(y: np.ndarray) -> np.ndarray:
    counts = np.bincount(np.asarray(y, dtype=np.int64))
    if np.any(counts[counts > 0] == 0):
        raise RuntimeError("empty class in weights")
    weights = np.zeros(len(y), dtype=np.float64)
    present = np.flatnonzero(counts)
    for klass in present:
        weights[y == klass] = 1.0 / (len(present) * counts[klass])
    return weights


def target_labels(y_pair: np.ndarray, target: str) -> np.ndarray:
    if target == "pair30":
        return np.asarray(y_pair, dtype=np.int64)
    pairs = np.asarray(PAIRS, dtype=np.int64)
    if target == "start6":
        return pairs[np.asarray(y_pair, dtype=np.int64), 0]
    if target == "goal6":
        return pairs[np.asarray(y_pair, dtype=np.int64), 1]
    raise ValueError(target)


def target_classes(target: str) -> np.ndarray:
    if target == "pair30":
        return np.arange(len(PAIR_LABELS), dtype=np.int64)
    if target in {"start6", "goal6"}:
        return np.arange(1, 7, dtype=np.int64)
    raise ValueError(target)


def target_label_name(target: str, value: int) -> str:
    if target == "pair30":
        return PAIR_LABELS[value]
    return f"{target[:-1]}{value}"


def fit_cue_scaler(train_cue: np.ndarray) -> StandardScaler:
    rows, cells, bins = train_cue.shape
    pooled = train_cue.transpose(0, 2, 1).reshape(rows * bins, cells)
    return StandardScaler().fit(pooled)


def transform_cue(cue: np.ndarray, scaler: StandardScaler) -> np.ndarray:
    rows, cells, bins = cue.shape
    flat = cue.transpose(0, 2, 1).reshape(rows * bins, cells)
    transformed = np.asarray(scaler.transform(flat), dtype=np.float64)
    return transformed.reshape(rows, bins, cells).transpose(0, 2, 1).astype(np.float32)


def _pca_replay_features(
    cue: np.ndarray, components: np.ndarray, mean: np.ndarray
) -> np.ndarray:
    rows, cells, bins = cue.shape
    if components.shape[1] != cells or mean.shape != (cells,):
        raise RuntimeError("saved PCA state does not match cue feature dimensions")
    flat = cue.transpose(0, 2, 1).reshape(rows * bins, cells)
    transformed = ((flat - mean) @ components.T).astype(np.float32)
    transformed = transformed.reshape(rows, bins, components.shape[0])
    if components.shape[0] < CEBRA_DIM:
        padding = np.zeros(
            (rows, bins, CEBRA_DIM - components.shape[0]), dtype=np.float32
        )
        transformed = np.concatenate([transformed, padding], axis=2)
    return transformed.reshape(rows, bins * CEBRA_DIM)


def flatten_cue(cue: np.ndarray) -> np.ndarray:
    return cue.reshape(cue.shape[0], cue.shape[1] * cue.shape[2])


def fit_pca_features(
    train_scaled: np.ndarray, *others: np.ndarray
) -> tuple[PCA, list[np.ndarray]]:
    rows, cells, bins = train_scaled.shape
    pooled = train_scaled.transpose(0, 2, 1).reshape(rows * bins, cells)
    components = min(CEBRA_DIM, cells, pooled.shape[0])
    pca = PCA(
        n_components=components, svd_solver="full", whiten=False, random_state=0
    ).fit(pooled)
    transformed = []
    for arr in (train_scaled, *others):
        r, _c, b = arr.shape
        flat = arr.transpose(0, 2, 1).reshape(r * b, cells)
        z = pca.transform(flat).astype(np.float32).reshape(r, b, components)
        if components < CEBRA_DIM:
            pad = np.zeros((r, b, CEBRA_DIM - components), dtype=np.float32)
            z = np.concatenate([z, pad], axis=2)
        transformed.append(z.reshape(r, b * CEBRA_DIM))
    return pca, transformed


def extract_window_features(
    representation: str,
    features: np.ndarray,
    window: str,
    *,
    cell_count: int,
    dim: int = CEBRA_DIM,
) -> np.ndarray:
    if window == "wholecue":
        return features
    if window not in BIN_WINDOWS:
        raise ValueError(window)
    bin_idx = checked_int(window.removeprefix("bin"))
    if representation in {"raw", "raw_svd_lda"}:
        return features.reshape(features.shape[0], cell_count, CUE_BINS)[:, :, bin_idx]
    if representation in {"pca8", "cebra_cue", "cebra_joint"}:
        return features.reshape(features.shape[0], CUE_BINS, dim)[:, bin_idx, :]
    raise ValueError(representation)


def nav_source_slice(
    nav: EndpointNavData, sid: str
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    idx = nav.source_index[sid]
    start = checked_int(nav.offsets[idx])
    stop = checked_int(nav.offsets[idx + 1])
    return (
        nav.counts_flat[start:stop],
        nav.exposure_flat[start:stop],
        nav.observed_flat[start:stop],
    )


def load_nav_data(path: Path, cohort: EndpointCohort | None = None) -> EndpointNavData:
    with np.load(path, allow_pickle=False) as data:
        required = {
            "nav_counts_flat",
            "nav_exposure_flat",
            "nav_observed_mask_flat",
            "nav_offsets",
            "nav_n_bins",
            "source_trial_ids",
            "source_session_ids",
            "source_labels",
            "source_splits",
            "source_trial_indices",
            "cell_ids",
            "bin_width_s",
        }
        missing = required - set(data.files)
        if missing:
            raise RuntimeError(f"nav data missing keys: {sorted(missing)}")
        source_ids = [str(x) for x in data["source_trial_ids"].tolist()]
        source_sessions = [str(x) for x in data["source_session_ids"].tolist()]
        source_labels = [str(x) for x in data["source_labels"].tolist()]
        source_splits = [str(x) for x in data["source_splits"].tolist()]
        cells = [str(x) for x in data["cell_ids"].tolist()]
        bin_width = parse_float(np.asarray(data["bin_width_s"]).reshape(-1)[0])
        nav = EndpointNavData(
            path=path,
            source_ids=source_ids,
            source_sessions=source_sessions,
            source_labels=source_labels,
            trial_indices=np.asarray(data["source_trial_indices"], dtype=np.int64),
            offsets=np.asarray(data["nav_offsets"], dtype=np.int64),
            n_bins=np.asarray(data["nav_n_bins"], dtype=np.int64),
            counts_flat=np.asarray(data["nav_counts_flat"], dtype=np.float32),
            exposure_flat=np.asarray(data["nav_exposure_flat"], dtype=np.float32),
            observed_flat=np.asarray(data["nav_observed_mask_flat"], dtype=bool),
            cells=cells,
            source_index={sid: idx for idx, sid in enumerate(source_ids)},
        )
    if any(split != "train" for split in source_splits):
        raise RuntimeError("navigation cache contains non-training sources")
    if not np.isclose(bin_width, BIN_WIDTH_S):
        raise RuntimeError("navigation cache bin width drifted")
    if nav.offsets.shape != (len(nav.source_ids) + 1,):
        raise RuntimeError("navigation offsets shape mismatch")
    if checked_int(nav.offsets[-1]) != nav.counts_flat.shape[0]:
        raise RuntimeError("navigation offset/count mismatch")
    if len(set(nav.source_ids)) != len(nav.source_ids):
        raise RuntimeError("navigation cache contains duplicate source ids")
    if nav.offsets[0] != 0 or np.any(np.diff(nav.offsets) != nav.n_bins):
        raise RuntimeError("navigation offsets do not match per-source bin counts")
    if nav.counts_flat.shape != nav.observed_flat.shape or nav.counts_flat.shape[
        1
    ] != len(nav.cells):
        raise RuntimeError("navigation count/mask shape mismatch")
    if nav.exposure_flat.shape != (len(nav.counts_flat),):
        raise RuntimeError("navigation exposure shape mismatch")
    if np.any(nav.n_bins < 2) or not np.isfinite(nav.exposure_flat).all():
        raise RuntimeError("navigation cache has invalid bins or exposure")
    if cohort is not None:
        train_metas = [m for m in cohort.metas if m.split == "train"]
        train_ids = {m.source_trial_id for m in train_metas}
        if set(nav.source_ids) != train_ids:
            raise RuntimeError(
                "navigation cache does not exactly match the endpoint training allowlist"
            )
        if nav.cells != cohort.cells:
            raise RuntimeError("navigation cache cell order mismatch")
        meta_by_id = {meta.source_trial_id: meta for meta in train_metas}
        for idx, sid in enumerate(nav.source_ids):
            meta = meta_by_id[sid]
            start, stop = (
                checked_int(value, "navigation offset")
                for value in nav.offsets[idx : idx + 2]
            )
            expected_mask = np.asarray(
                [session_from_cell(cell) == meta.session_id for cell in nav.cells]
            )
            if (
                nav.source_sessions[idx] != meta.session_id
                or nav.source_labels[idx] != meta.label
            ):
                raise RuntimeError(f"navigation source metadata mismatch: {sid}")
            if (
                meta.trial_index is not None
                and nav.trial_indices[idx] != meta.trial_index
            ):
                raise RuntimeError(f"navigation trial index mismatch: {sid}")
            if not np.all(nav.observed_flat[start:stop] == expected_mask[None, :]):
                raise RuntimeError(f"navigation observed mask mismatch: {sid}")
            observed_counts = nav.counts_flat[start:stop][:, expected_mask]
            absent_counts = nav.counts_flat[start:stop][:, ~expected_mask]
            if not np.isfinite(observed_counts).all() or (observed_counts < 0).any():
                raise RuntimeError(f"invalid observed navigation counts: {sid}")
            if not np.isnan(absent_counts).all():
                raise RuntimeError(
                    f"unobserved navigation cells must remain masked: {sid}"
                )
    return nav


def assert_training_nav_allowlist(
    cohort: EndpointCohort,
    requested_source_ids: Iterable[str] | None = None,
) -> list[str]:
    train_ids = {m.source_trial_id for m in cohort.metas if m.split == "train"}
    development_ids = {m.source_trial_id for m in cohort.metas if m.split != "train"}
    requested = (
        set(requested_source_ids) if requested_source_ids is not None else train_ids
    )
    if requested & development_ids:
        raise RuntimeError("navigation extraction requested development sources")
    if requested - train_ids:
        raise RuntimeError(
            "navigation extraction requested source outside inner-training allowlist"
        )
    return sorted(requested)


def raw_source_files_manifest(
    import_dir: Path, canonical_root: Path = CANONICAL_ROOT
) -> dict[tuple[str, str, str], dict[str, str]]:
    rows = read_csv(import_dir / "source_files.csv")
    out: dict[tuple[str, str, str], dict[str, str]] = {}
    for row in rows:
        key = (row["role"], row.get("session_id", ""), row.get("cell_id", ""))
        out[key] = row
    return out


def raw_manifest_path(
    row: Mapping[str, str], canonical_root: Path = CANONICAL_ROOT
) -> Path:
    raw = row.get("path") or row.get("relative_path") or row.get("file")
    if raw is None:
        raise RuntimeError("source_files.csv row has no path")
    path = Path(raw)
    return path if path.is_absolute() else canonical_root / path


def index_training_cue_windows(
    rows: Iterable[Mapping[str, str]],
    *,
    expected_cells_by_source: Mapping[str, Sequence[str]],
) -> dict[str, dict[str, tuple[str, int, float, float]]]:
    expected = {sid: set(cells) for sid, cells in expected_cells_by_source.items()}
    windows: dict[str, dict[str, tuple[str, int, float, float]]] = {}
    for row in rows:
        source_id = row.get("source_trial_id", "")
        cell_id = row.get("cell_id", "")
        if source_id not in expected or cell_id not in expected[source_id]:
            continue
        if row.get("split") != "train":
            raise RuntimeError(f"cue ledger split mismatch: {source_id}")
        window = (
            row["session_id"],
            checked_int(row["trial_index"]),
            parse_float(row["cue_window_start_ripple_s"]),
            parse_float(row["cue_window_end_ripple_s"]),
        )
        if (
            not math.isfinite(window[2])
            or not math.isfinite(window[3])
            or window[3] <= window[2]
        ):
            raise RuntimeError(f"invalid imported cue window: {source_id}/{cell_id}")
        per_cell = windows.setdefault(source_id, {})
        if cell_id in per_cell:
            raise RuntimeError(f"duplicate imported cue window: {source_id}/{cell_id}")
        per_cell[cell_id] = window
    for source_id, expected_cells in expected.items():
        per_cell = windows.get(source_id, {})
        if set(per_cell) != expected_cells:
            missing = sorted(expected_cells - set(per_cell))
            raise RuntimeError(
                f"selected-cell cue windows incomplete for {source_id}: {missing[:5]}"
            )
        reference = next(iter(per_cell.values()))
        if any(
            window[:2] != reference[:2]
            or not math.isclose(window[2], reference[2], rel_tol=0, abs_tol=1e-9)
            or not math.isclose(window[3], reference[3], rel_tol=0, abs_tol=1e-9)
            for window in per_cell.values()
        ):
            raise RuntimeError(f"selected-cell cue windows disagree: {source_id}")
    return windows


def verify_raw_cue_window(
    meta: EndpointSource,
    raw_times: tuple[float, float, float],
    imported_windows: Mapping[str, tuple[str, int, float, float]],
) -> None:
    if not imported_windows:
        raise RuntimeError(f"no selected-cell cue windows: {meta.source_trial_id}")
    for cell_id, window in imported_windows.items():
        session_id, trial_index, cue_start, cue_end = window
        if session_id != meta.session_id or (
            meta.trial_index is not None and trial_index != meta.trial_index
        ):
            raise RuntimeError(
                f"cue window identity mismatch: {meta.source_trial_id}/{cell_id}"
            )
        # The accepted importer serializes timestamps to nine significant digits.
        if (
            parse_float(imported_csv_value(raw_times[0])) != cue_start
            or parse_float(imported_csv_value(raw_times[1])) != cue_end
        ):
            raise RuntimeError(
                f"raw/imported cue window time mismatch: {meta.source_trial_id}/{cell_id}"
            )


def complete_navigation_window(
    cue_end: float, nav_end: float
) -> tuple[int, float, float, float]:
    duration = nav_end - cue_end
    if not math.isfinite(duration) or duration <= 0:
        raise RuntimeError("nonpositive cue/navigation duration")
    tolerance = 1e-12
    n_bins = checked_int(math.floor((duration + tolerance) / BIN_WIDTH_S))
    if n_bins < 2:
        raise RuntimeError("inadequate complete navigation bins")
    nominal_end = cue_end + n_bins * BIN_WIDTH_S
    overshoot = nominal_end - nav_end
    if overshoot > tolerance:
        raise RuntimeError("navigation bin edge exceeds the raw navigation window")
    window_end = min(nav_end, nominal_end)
    tail = max(0.0, duration - n_bins * BIN_WIDTH_S)
    return n_bins, window_end, tail, max(0.0, overshoot)


def parse_ripple_codes(text: str) -> tuple[int, ...]:
    return tuple(
        checked_int(part) for part in text.replace(";", " ").replace(",", " ").split()
    )


def select_training_trial_rows(
    rows: Iterable[Mapping[str, str]],
    allowed_sources: set[str],
    outer_train_sources: set[str] | None = None,
) -> dict[str, Mapping[str, str]]:
    """Separate the outer split gate from the endpoint inner-train allowlist."""
    selected: dict[str, Mapping[str, str]] = {}
    seen_outer_sources: set[str] = set()
    for row in rows:
        source_id = row["source_trial_id"]
        if source_id in seen_outer_sources:
            raise RuntimeError(f"duplicate outer-training trial row: {source_id}")
        seen_outer_sources.add(source_id)
        if row.get("split") != "train":
            raise RuntimeError(
                f"outer split gate yielded non-training row: {source_id}"
            )
        if source_id in allowed_sources:
            selected[source_id] = row
    if outer_train_sources is not None and seen_outer_sources != outer_train_sources:
        raise RuntimeError("outer-training split-gate source set mismatch")
    if set(selected) != allowed_sources:
        raise RuntimeError("inner-training trial allowlist incomplete")
    return selected


def extract_training_navigation(
    *,
    cohort: EndpointCohort,
    output_dir: Path,
    import_dir: Path = IMPORT_DIR,
    split_dir: Path = SPLIT_DIR,
    canonical_root: Path = CANONICAL_ROOT,
) -> dict[str, Any]:
    ensure_fresh_dir(output_dir)
    allowed_sources = set(assert_training_nav_allowlist(cohort))
    access = SplitFilteredAccess(import_dir, split_dir, allowed_splits=("train",))
    trial_rows = select_training_trial_rows(
        access.iter_trials(), allowed_sources, set(access.allowed_source_ids)
    )
    training_metas = [m for m in cohort.metas if m.source_trial_id in allowed_sources]
    expected_cells_by_source = {
        meta.source_trial_id: tuple(
            cell for cell in cohort.cells if session_from_cell(cell) == meta.session_id
        )
        for meta in training_metas
    }
    imported_cue_windows = index_training_cue_windows(
        access.iter_cue_counts(), expected_cells_by_source=expected_cells_by_source
    )
    raw_manifest = raw_source_files_manifest(import_dir, canonical_root)
    sessions = sorted(
        {m.session_id for m in cohort.metas if m.source_trial_id in allowed_sources}
    )
    cell_sessions = np.asarray([session_from_cell(cell) for cell in cohort.cells])
    opened_files: list[dict[str, Any]] = []
    raw_hash_failures: list[str] = []
    ripple_by_session: dict[str, Any] = {}
    spikes_by_cell: dict[str, np.ndarray] = {}

    for session in sessions:
        row = raw_manifest.get(("ripple_markers", session, ""))
        if row is None:
            raise RuntimeError(f"missing raw ripple manifest for {session}")
        path = raw_manifest_path(row, canonical_root)
        observed = sha256_file(path)
        if observed != row["sha256"]:
            raw_hash_failures.append(f"{path}: {observed} != {row['sha256']}")
        ripple_by_session[session] = read_ripple_trials(path)
        opened_files.append(
            {
                "role": "ripple_markers",
                "session_id": session,
                "path": str(path),
                "sha256": observed,
                "manifest_sha256": row["sha256"],
            }
        )
    for cell in cohort.cells:
        session = session_from_cell(cell)
        if session not in sessions:
            continue
        row = raw_manifest.get(("spiketrain", session, cell))
        if row is None:
            raise RuntimeError(f"missing raw spiketrain manifest for {cell}")
        path = raw_manifest_path(row, canonical_root)
        observed = sha256_file(path)
        if observed != row["sha256"]:
            raw_hash_failures.append(f"{path}: {observed} != {row['sha256']}")
        spikes_by_cell[cell] = read_spiketrain(path).timestamps_seconds
        opened_files.append(
            {
                "role": "spiketrain",
                "session_id": session,
                "cell_id": cell,
                "path": str(path),
                "sha256": observed,
                "manifest_sha256": row["sha256"],
            }
        )
    if raw_hash_failures:
        raise RuntimeError("raw hash mismatch: " + "; ".join(raw_hash_failures[:5]))

    chunks: list[np.ndarray] = []
    exposures: list[np.ndarray] = []
    masks: list[np.ndarray] = []
    source_ids: list[str] = []
    source_sessions: list[str] = []
    source_labels: list[str] = []
    trial_indices: list[int] = []
    offsets = [0]
    n_bins_list: list[int] = []
    window_rows: list[dict[str, Any]] = []
    cue_failures: list[dict[str, Any]] = []
    cue_precision_differences: list[dict[str, Any]] = []
    cue_omissions: list[dict[str, Any]] = []
    tails: list[dict[str, Any]] = []

    for meta in training_metas:
        if meta.split != "train":
            raise RuntimeError(
                f"refusing development nav extraction: {meta.source_trial_id}"
            )
        trial = trial_rows.get(meta.source_trial_id)
        if trial is None or trial.get("split") != "train":
            raise RuntimeError(
                f"training source absent from split-gated import: {meta.source_trial_id}"
            )
        if (
            trial.get("session_id") != meta.session_id
            or trial.get("outcome") != "success"
        ):
            raise RuntimeError(f"trial identity/QC mismatch: {meta.source_trial_id}")
        trial_index = checked_int(trial.get("trial_index", -1))
        if meta.trial_index is not None and trial_index != meta.trial_index:
            raise RuntimeError(f"trial index mismatch: {meta.source_trial_id}")
        ripple = ripple_by_session[meta.session_id]
        trial0 = trial_index - 1
        times = _times_at(ripple, trial0)
        codes = tuple(_codes_at(ripple, trial0) or ())
        if times is None or len(times) != 3:
            raise RuntimeError(f"missing raw Ripple triplet: {meta.source_trial_id}")
        if codes != parse_ripple_codes(trial.get("ripple_codes", "")):
            raise RuntimeError(
                f"raw/imported Ripple code mismatch: {meta.source_trial_id}"
            )
        cue_start, cue_end, nav_end = (
            parse_float(value, "raw Ripple time") for value in times
        )
        imported_windows = imported_cue_windows[meta.source_trial_id]
        verify_raw_cue_window(meta, times, imported_windows)
        imported_window = next(iter(imported_windows.values()))
        cue_duration = cue_end - cue_start
        nav_duration = nav_end - cue_end
        if cue_duration <= 0 or nav_duration <= 0:
            raise RuntimeError(f"nonpositive cue/nav duration: {meta.source_trial_id}")
        if abs(cue_duration - parse_float(trial["ripple_cue_duration_s"])) > 1e-5:
            raise RuntimeError(f"cue timing mismatch: {meta.source_trial_id}")
        if abs(nav_duration - parse_float(trial["ripple_nav_duration_s"])) > 1e-5:
            raise RuntimeError(f"nav timing mismatch: {meta.source_trial_id}")

        si = cohort.source_index[meta.source_trial_id]
        same_cells = np.flatnonzero(cell_sessions == meta.session_id)
        recomputed = np.zeros((len(cohort.cells), CUE_BINS), dtype=np.float32)
        cue_exposure: np.ndarray | None = None
        for ci in same_cells:
            cell = cohort.cells[checked_int(ci)]
            cue_spikes = spikes_in_window(spikes_by_cell[cell], cue_start, cue_end)
            relative = cue_spikes - cue_start
            raw_counts, _, _ = bin_events(
                relative, cue_duration, BIN_WIDTH_S, nominal=1.0
            )
            # Replay the accepted import path exactly, including its CSV precision.
            imported_relative = [parse_float(imported_csv_value(t)) for t in relative]
            imported_duration = imported_windows[cell][3] - imported_windows[cell][2]
            counts, exposure, omitted = bin_events(
                imported_relative, imported_duration, BIN_WIDTH_S, nominal=1.0
            )
            if not np.array_equal(raw_counts, counts):
                cue_precision_differences.append(
                    {
                        "source_trial_id": meta.source_trial_id,
                        "cell_id": cell,
                        "native_counts": raw_counts.tolist(),
                        "accepted_precision_counts": counts.tolist(),
                    }
                )
            if omitted:
                cue_omissions.append(
                    {
                        "source_trial_id": meta.source_trial_id,
                        "cell_id": cell,
                        "count": checked_int(omitted),
                    }
                )
            recomputed[checked_int(ci)] = counts
            cue_exposure = exposure
        if cue_exposure is None:
            raise RuntimeError(f"no observed cells for {meta.source_trial_id}")
        if not np.array_equal(recomputed[same_cells], cohort.counts[si, same_cells, :]):
            cue_failures.append(
                {
                    "source_trial_id": meta.source_trial_id,
                    "reason": "cue_count_mismatch",
                }
            )
        if not np.array_equal(cue_exposure, cohort.exposure[si]):
            cue_failures.append(
                {
                    "source_trial_id": meta.source_trial_id,
                    "reason": "cue_exposure_mismatch",
                }
            )

        try:
            complete_nav_bins, nav_window_end, tail, edge_clamp = (
                complete_navigation_window(cue_end, nav_end)
            )
        except RuntimeError as exc:
            raise RuntimeError(f"{meta.source_trial_id}: {exc}") from exc
        if tail > 1e-9:
            tails.append(
                {
                    "source_trial_id": meta.source_trial_id,
                    "nav_duration_s": nav_duration,
                    "discarded_tail_s": tail,
                }
            )
        nav_counts = np.full(
            (complete_nav_bins, len(cohort.cells)), np.nan, dtype=np.float32
        )
        nav_mask = np.zeros((complete_nav_bins, len(cohort.cells)), dtype=bool)
        for ci in same_cells:
            cell = cohort.cells[checked_int(ci)]
            rel = (
                spikes_in_window(
                    spikes_by_cell[cell],
                    cue_end,
                    nav_window_end,
                )
                - cue_end
            )
            bins = np.floor(rel / BIN_WIDTH_S).astype(int)
            valid = (bins >= 0) & (bins < complete_nav_bins)
            nav_counts[:, checked_int(ci)] = np.bincount(
                bins[valid], minlength=complete_nav_bins
            ).astype(np.float32)
            nav_mask[:, checked_int(ci)] = True
        chunks.append(nav_counts)
        exposures.append(np.full(complete_nav_bins, BIN_WIDTH_S, dtype=np.float32))
        masks.append(nav_mask)
        source_ids.append(meta.source_trial_id)
        source_sessions.append(meta.session_id)
        source_labels.append(meta.label)
        trial_indices.append(trial_index)
        n_bins_list.append(complete_nav_bins)
        offsets.append(offsets[-1] + complete_nav_bins)
        window_rows.append(
            {
                "source_trial_id": meta.source_trial_id,
                "session_id": meta.session_id,
                "inner_split": meta.split,
                "label": meta.label,
                "trial_index": trial_index,
                "cue_start_s": cue_start,
                "cue_end_s": cue_end,
                "nav_end_s": nav_end,
                "complete_nav_window_end_s": nav_window_end,
                "nav_edge_clamp_s": edge_clamp,
                "imported_cue_start_s": imported_window[2],
                "imported_cue_end_s": imported_window[3],
                "ripple_codes": ",".join(map(str, codes)),
                "cue_duration_s": cue_duration,
                "nav_duration_s": nav_duration,
                "complete_nav_bins_100ms": complete_nav_bins,
                "discarded_nav_tail_s": max(0.0, tail),
                "observed_cells": checked_int(len(same_cells)),
            }
        )
    if cue_failures:
        write_csv(output_dir / "cue_recount_failures.csv", cue_failures)
        raise RuntimeError(f"cue recount parity failed for {len(cue_failures)} rows")
    counts_flat = np.concatenate(chunks, axis=0)
    exposure_flat = np.concatenate(exposures, axis=0)
    mask_flat = np.concatenate(masks, axis=0)
    nav_path = output_dir / "training_nav_source_data.npz"
    np.savez_compressed(
        nav_path,
        nav_counts_flat=counts_flat,
        nav_exposure_flat=exposure_flat,
        nav_observed_mask_flat=mask_flat,
        nav_offsets=np.asarray(offsets, dtype=np.int64),
        nav_n_bins=np.asarray(n_bins_list, dtype=np.int64),
        source_trial_ids=np.asarray(source_ids),
        source_session_ids=np.asarray(source_sessions),
        source_labels=np.asarray(source_labels),
        source_splits=np.asarray(["train"] * len(source_ids)),
        source_trial_indices=np.asarray(trial_indices, dtype=np.int64),
        cell_ids=np.asarray(cohort.cells),
        bin_width_s=np.asarray([BIN_WIDTH_S], dtype=np.float32),
    )
    write_csv(output_dir / "opened_raw_files.csv", opened_files)
    write_csv(output_dir / "training_source_windows.csv", window_rows)
    summary = {
        "created_utc": utc_now(),
        "training_sources": len(source_ids),
        "development_sources_with_no_navigation": sum(
            1 for m in cohort.metas if m.split != "train"
        ),
        "opened_file_count": len(opened_files),
        "raw_hashes_checked": True,
        "timing_checked": True,
        "cue_recount_exact": True,
        "cue_recount_mode": "raw_spikes_through_accepted_csv_precision",
        "cue_native_vs_accepted_precision_differences": cue_precision_differences,
        "development_navigation_selected": False,
        "training_source_allowlist_count": len(source_ids),
        "training_source_allowlist_sha256": stable_hash(sorted(source_ids)),
        "imported_ledger_hashes": {
            "source_files.csv": sha256_file(import_dir / "source_files.csv"),
            "trials.csv": sha256_file(import_dir / "trials.csv"),
            "cue_counts.csv.gz": sha256_file(import_dir / "cue_counts.csv.gz"),
            "source_trial_splits.csv": sha256_file(
                split_dir / "source_trial_splits.csv"
            ),
            "split_summary.json": sha256_file(split_dir / "split_summary.json"),
        },
        "split_manifest_sha256": access.split_hash,
        "opened_raw_files_csv": "opened_raw_files.csv",
        "opened_raw_files_csv_sha256": sha256_file(output_dir / "opened_raw_files.csv"),
        "training_source_windows_csv": "training_source_windows.csv",
        "training_source_windows_csv_sha256": sha256_file(
            output_dir / "training_source_windows.csv"
        ),
        "nav_npz": str(nav_path),
        "nav_npz_sha256": sha256_file(nav_path),
        # The NPZ SHA binds every array without materializing large Python lists.
        "nav_complete_bins_min_median_max": [
            checked_int(np.min(n_bins_list)),
            parse_float(np.median(n_bins_list)),
            checked_int(np.max(n_bins_list)),
        ],
        "discarded_nav_tail_sources": len(tails),
        "discarded_nav_tail_first10": tails[:10],
        "cue_spikes_after_nominal_1s_excluded": len(cue_omissions),
        "cue_spikes_after_nominal_1s_first10": cue_omissions[:10],
        "split_gate_audit": access.audit.as_dict(),
    }
    write_json(output_dir / "navigation_audit.json", summary)
    return summary


def build_endpoint_pair_bank(
    train_bundle: RowBundle,
    nav: EndpointNavData,
    scaler: StandardScaler,
    cells: Sequence[str],
) -> EndpointPairBank:
    cell_sessions = np.asarray([session_from_cell(cell) for cell in cells])
    train_scaled = transform_cue(train_bundle.X_cue, scaler)
    cue_vectors: list[np.ndarray] = []
    cue_labels: list[int] = []
    cue_pairs: list[tuple[int, int]] = []
    cue_samples_by_row: list[np.ndarray] = []
    cue_pairs_by_row: list[np.ndarray] = []
    for row, label in zip(train_scaled, train_bundle.y_pair, strict=True):
        base = len(cue_vectors)
        for bin_idx in range(CUE_BINS):
            cue_vectors.append(row[:, bin_idx])
            cue_labels.append(checked_int(label))
        samples = np.arange(base, base + CUE_BINS, dtype=np.int64)
        pairs = np.asarray(
            [(base + b, base + b + 1) for b in range(CUE_BINS - 1)], dtype=np.int64
        )
        cue_samples_by_row.append(samples)
        cue_pairs_by_row.append(pairs)
        cue_pairs.extend((checked_int(pair[0]), checked_int(pair[1])) for pair in pairs)

    nav_vectors: list[np.ndarray] = []
    nav_vector_count = 0
    nav_labels: list[int] = []
    nav_pairs: list[tuple[int, int]] = []
    nav_samples_by_row: list[np.ndarray] = []
    nav_pairs_by_row: list[np.ndarray] = []
    coverage_rows: list[dict[str, Any]] = []
    lineage_sessions = sorted({session_from_cell(cell) for cell in cells})
    lineage_session_index = {
        session: index for index, session in enumerate(lineage_sessions)
    }
    lineage_source_ids: list[list[str]] = []
    lineage_native_bins: list[np.ndarray] = []
    lineage_row_offsets = [0]
    for plan in train_bundle.plans:
        label = PAIR_TO_INT[str(plan["label"])]
        per_session: dict[str, tuple[np.ndarray, np.ndarray]] = {}
        max_pairs = 0
        for session, sid in dict(plan["sources"]).items():
            counts, _exp, mask = nav_source_slice(nav, sid)
            cell_idx = np.flatnonzero(cell_sessions == session)
            if not np.all(mask[:, cell_idx]):
                raise RuntimeError(f"navigation mask failure for {sid}/{session}")
            per_session[session] = (counts, cell_idx)
            max_pairs = max(max_pairs, counts.shape[0] - 1)
        if max_pairs < 1:
            raise RuntimeError(f"no native nav adjacent pairs for {plan['row_id']}")
        row_samples = np.arange(nav_vector_count, nav_vector_count + 2 * max_pairs)
        row_pairs = row_samples.reshape(-1, 2)
        source_ids_by_session = [
            str(dict(plan["sources"])[session]) for session in lineage_sessions
        ]
        native_bins = np.empty((max_pairs, len(lineage_sessions)), dtype=np.uint16)
        row_vectors = np.empty((2 * max_pairs, len(cells)), dtype=np.float32)
        # Same native-pair rule; batch array indexing/scaling avoids per-bin calls.
        q = (np.arange(max_pairs, dtype=np.float64) + 0.5) / max_pairs
        for session, (counts, cell_idx) in per_session.items():
            n_pairs = counts.shape[0] - 1
            if n_pairs > np.iinfo(np.uint16).max:
                raise RuntimeError("native navigation lineage exceeds uint16 capacity")
            native = np.minimum(n_pairs - 1, np.floor(q * n_pairs).astype(np.int64))
            row_vectors[0::2, cell_idx] = counts[native[:, None], cell_idx]
            row_vectors[1::2, cell_idx] = counts[native[:, None] + 1, cell_idx]
            native_bins[:, lineage_session_index[session]] = native
        row_vectors = np.asarray(scaler.transform(row_vectors), dtype=np.float32)
        nav_labels.extend([label] * len(row_samples))
        nav_pairs.extend(
            (checked_int(pair[0]), checked_int(pair[1])) for pair in row_pairs
        )
        for session, sid in dict(plan["sources"]).items():
            n_pairs = nav_source_slice(nav, sid)[0].shape[0] - 1
            represented = set(native_bins[:, lineage_session_index[session]].tolist())
            missing = [idx for idx in range(n_pairs) if idx not in represented]
            if missing:
                raise RuntimeError(
                    f"native-pair coverage failed for {sid}: {missing[:5]}"
                )
            coverage_rows.append(
                {
                    "row_id": plan["row_id"],
                    "session_id": session,
                    "source_trial_id": sid,
                    "native_adjacent_pairs": n_pairs,
                    "represented_pairs": n_pairs,
                    "max_pair_bank_L": max_pairs,
                }
            )
        nav_vectors.append(row_vectors)
        nav_vector_count += len(row_vectors)
        lineage_source_ids.append(source_ids_by_session)
        lineage_native_bins.append(native_bins)
        lineage_row_offsets.append(lineage_row_offsets[-1] + max_pairs)
        nav_samples_by_row.append(np.asarray(row_samples, dtype=np.int64))
        nav_pairs_by_row.append(np.asarray(row_pairs, dtype=np.int64))
    return EndpointPairBank(
        cue_samples=np.asarray(cue_vectors, dtype=np.float32),
        cue_labels=np.asarray(cue_labels, dtype=np.int64),
        cue_pairs=np.asarray(cue_pairs, dtype=np.int64),
        cue_samples_by_row=cue_samples_by_row,
        cue_pairs_by_row=cue_pairs_by_row,
        nav_samples=np.concatenate(nav_vectors, axis=0),
        nav_labels=np.asarray(nav_labels, dtype=np.int64),
        nav_pairs=np.asarray(nav_pairs, dtype=np.int64),
        nav_samples_by_row=nav_samples_by_row,
        nav_pairs_by_row=nav_pairs_by_row,
        row_labels=np.asarray(train_bundle.y_pair, dtype=np.int64),
        pair_lineage={
            "session_ids": np.asarray(lineage_sessions),
            "source_trial_ids": np.asarray(lineage_source_ids),
            "row_pair_offsets": np.asarray(lineage_row_offsets, dtype=np.int64),
            "native_anchor_bins": np.concatenate(lineage_native_bins, axis=0),
        },
        coverage_rows=coverage_rows,
    )


def cebra_dataset_for_endpoint_arm(
    arm: str,
    train_scaled: np.ndarray,
    y_pair: np.ndarray,
    pair_bank: EndpointPairBank | None,
    *,
    device: str,
) -> tuple[CebraVectorDataset, dict[str, Any], dict[str, Any]]:
    rows, cells, bins = train_scaled.shape
    cue_flat = train_scaled.transpose(0, 2, 1).reshape(rows * bins, cells)
    cue_labels = np.repeat(y_pair, bins)
    cue_samples_by_row = [
        np.arange(r * bins, (r + 1) * bins, dtype=np.int64) for r in range(rows)
    ]
    cue_pairs_by_row = [
        np.asarray(
            [(r * bins + b, r * bins + b + 1) for b in range(bins - 1)], dtype=np.int64
        )
        for r in range(rows)
    ]
    if arm == "cebra_cue":
        ds = CebraVectorDataset(
            cue_flat, cue_labels, np.zeros(len(cue_flat), dtype=np.int64), device=device
        )
        return (
            ds,
            {
                "pair_groups_by_phase": {0: cue_pairs_by_row},
                "sample_groups_by_phase": {0: cue_samples_by_row},
                "phase_probs": (1.0,),
            },
            {"cue_sample_count": len(cue_flat), "nav_sample_count": 0},
        )
    if arm != "cebra_joint" or pair_bank is None:
        raise ValueError("joint CEBRA arm requires endpoint pair bank")
    X = np.concatenate([pair_bank.cue_samples, pair_bank.nav_samples], axis=0)
    labels = np.concatenate([pair_bank.cue_labels, pair_bank.nav_labels], axis=0)
    phase = np.concatenate(
        [
            np.zeros(len(pair_bank.cue_samples), dtype=np.int64),
            np.ones(len(pair_bank.nav_samples), dtype=np.int64),
        ]
    )
    nav_offset = len(pair_bank.cue_samples)
    ds = CebraVectorDataset(X, labels, phase, device=device)
    return (
        ds,
        {
            "pair_groups_by_phase": {
                0: pair_bank.cue_pairs_by_row,
                1: [group + nav_offset for group in pair_bank.nav_pairs_by_row],
            },
            "sample_groups_by_phase": {
                0: pair_bank.cue_samples_by_row,
                1: [group + nav_offset for group in pair_bank.nav_samples_by_row],
            },
            "phase_probs": (0.5, 0.5),
        },
        {
            "cue_sample_count": len(pair_bank.cue_samples),
            "nav_sample_count": len(pair_bank.nav_samples),
        },
    )


def train_endpoint_encoder(
    *,
    arm: str,
    train_scaled: np.ndarray,
    y_pair: np.ndarray,
    pair_bank: EndpointPairBank | None,
    seed: int,
    outdir: Path,
    iterations: int = CEBRA_UPDATES,
    batch_size: int = 256,
    lr: float = 3e-4,
    hidden: int = 32,
    dim: int = CEBRA_DIM,
    device: str = "cpu",
    deadline: float | None = None,
) -> tuple[Any, dict[str, Any]]:
    if FITS_BLOCKED:
        raise RuntimeError("fit operation blocked during replay verification")
    # Reuse the reviewed trainer by presenting endpoint arms as its time arms.  The
    # local dataset function above is kept for synthetic sampler checks.
    ft_arm = "cue_time" if arm == "cebra_cue" else "joint_time"
    solver, info = _train_encoder(
        arm=ft_arm,
        train_scaled_cue=train_scaled,
        y_train=y_pair,
        pair_bank=cast(Any, pair_bank),
        seed=seed,
        outdir=outdir,
        iterations=iterations,
        batch_size=batch_size,
        lr=lr,
        hidden=hidden,
        dim=dim,
        device=device,
        deadline=deadline,
    )
    final_checkpoint = Path(str(info["checkpoint_final"]))
    for checkpoint in info["checkpoints"]:
        Path(str(checkpoint)).unlink(missing_ok=True)
    info["checkpoints"] = [str(final_checkpoint)]
    write_json(Path(outdir) / "fit_info.json", info)
    return solver, info


def save_scaler(path: Path, scaler: StandardScaler) -> None:
    fitted = cast(Any, scaler)
    if fitted.mean_ is None or fitted.scale_ is None or fitted.var_ is None:
        raise RuntimeError("cannot save an unfitted scaler")
    np.savez_compressed(
        path,
        mean=np.asarray(fitted.mean_, dtype=np.float64),
        scale=np.asarray(fitted.scale_, dtype=np.float64),
        var=np.asarray(fitted.var_, dtype=np.float64),
    )


def load_scaler(path: Path) -> StandardScaler:
    with np.load(path, allow_pickle=False) as data:
        scaler = StandardScaler()
        fitted = cast(Any, scaler)
        fitted.mean_ = data["mean"]
        fitted.scale_ = data["scale"]
        fitted.var_ = data["var"]
        fitted.n_features_in_ = checked_int(data["mean"].shape[0])
    return scaler


def load_encoder_checkpoint(
    checkpoint: Path,
    *,
    input_dim: int,
    dim: int,
    hidden: int,
    lr: float,
    device: str,
) -> Any:
    solver = make_solver(input_dim, dim, hidden, lr, device)
    state = torch.load(checkpoint, map_location=device)
    solver.load_state_dict(state)
    return solver


def fit_feature_bundle(
    *,
    cohort: EndpointCohort,
    nav: EndpointNavData,
    world: str,
    world_index: int,
    seed: int,
    outdir: Path,
    shuffled: Mapping[str, str] | None,
    device: str,
    deadline: float | None,
    iterations: int = CEBRA_UPDATES,
    batch_size: int = 256,
    hidden: int = 32,
    lr: float = 3e-4,
) -> FeatureBundle:
    train_bundle, development_bundle = assemble_world_seed(
        cohort, seed=seed, shuffled=shuffled
    )
    scaler = fit_cue_scaler(train_bundle.X_cue)
    save_scaler(outdir / "cue_input_scaler.npz", scaler)
    train_scaled = transform_cue(train_bundle.X_cue, scaler)
    dev_scaled = transform_cue(development_bundle.X_cue, scaler)
    raw_train = flatten_cue(train_scaled)
    raw_dev = flatten_cue(dev_scaled)
    pca, (pca_train, pca_dev) = fit_pca_features(train_scaled, dev_scaled)
    if pca.components_ is None or pca.mean_ is None:
        raise RuntimeError("PCA fit produced no reusable state")
    np.savez_compressed(
        outdir / "pca_state.npz",
        components=np.asarray(cast(np.ndarray, pca.components_)),
        mean=np.asarray(cast(np.ndarray, pca.mean_)),
    )
    np.savez_compressed(
        outdir / "scaled_cue.npz", train=train_scaled, development=dev_scaled
    )
    np.savez_compressed(
        outdir / "pseudo_targets.npz",
        y_pair_train=train_bundle.y_pair,
        y_pair_development=development_bundle.y_pair,
    )
    pair_bank = build_endpoint_pair_bank(train_bundle, nav, scaler, cohort.cells)
    write_csv(outdir / "pair_bank_coverage.csv", pair_bank.coverage_rows)
    lineage = pair_bank.pair_lineage
    np.savez_compressed(
        outdir / "pair_lineage.npz",
        session_ids=lineage["session_ids"],
        source_trial_ids=lineage["source_trial_ids"],
        row_pair_offsets=lineage["row_pair_offsets"],
        native_anchor_bins=lineage["native_anchor_bins"],
    )
    features_train = {"raw": raw_train, "pca8": pca_train}
    features_dev = {"raw": raw_dev, "pca8": pca_dev}
    initial_model_hashes = []
    for arm in ("cebra_cue", "cebra_joint"):
        solver, info = train_endpoint_encoder(
            arm=arm,
            train_scaled=train_scaled,
            y_pair=train_bundle.y_pair,
            pair_bank=pair_bank if arm == "cebra_joint" else None,
            seed=seed,
            outdir=outdir / arm,
            iterations=iterations,
            batch_size=batch_size,
            hidden=hidden,
            lr=lr,
            device=device,
            deadline=deadline,
        )
        initial_model_hashes.append(info["initial_model_sha256"])
        write_json(
            outdir / arm / "endpoint_fit_info.json", {**info, "endpoint_arm": arm}
        )
        features_train[arm] = _embed_cue(solver, train_scaled, device=device)
        features_dev[arm] = _embed_cue(solver, dev_scaled, device=device)
    if len(set(initial_model_hashes)) != 1:
        raise RuntimeError(
            "cue-only and joint encoders did not share identical initial weights"
        )
    np.savez_compressed(
        outdir / "features_train.npz",
        raw=features_train["raw"],
        pca8=features_train["pca8"],
        cebra_cue=features_train["cebra_cue"],
        cebra_joint=features_train["cebra_joint"],
    )
    np.savez_compressed(
        outdir / "features_development.npz",
        raw=features_dev["raw"],
        pca8=features_dev["pca8"],
        cebra_cue=features_dev["cebra_cue"],
        cebra_joint=features_dev["cebra_joint"],
    )
    return FeatureBundle(
        world=world,
        world_index=world_index,
        seed=seed,
        train_bundle=train_bundle,
        development_bundle=development_bundle,
        features_train=features_train,
        features_development=features_dev,
        checked_files=[
            str(outdir / "cue_input_scaler.npz"),
            str(outdir / "pca_state.npz"),
            str(outdir / "scaled_cue.npz"),
            str(outdir / "pseudo_targets.npz"),
        ],
    )


def fit_readout_state(
    *,
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_eval: np.ndarray,
    target: str,
    representation: str,
    outdir: Path,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, str]:
    if FITS_BLOCKED:
        raise RuntimeError("fit operation blocked during replay verification")
    outdir.mkdir(parents=True, exist_ok=True)
    classes = target_classes(target)
    if representation == "raw_svd_lda":
        scaler = StandardScaler().fit(X_train)
        model = LinearDiscriminantAnalysis(solver="svd").fit(
            scaler.transform(X_train), y_train
        )
        train_prob = model.predict_proba(scaler.transform(X_train))
        eval_prob = model.predict_proba(scaler.transform(X_eval))
        coef = np.empty((0, 0), dtype=np.float64)
        intercept = np.empty((0,), dtype=np.float64)
        model_name = "raw_svd_lda"
    else:
        scaler = StandardScaler().fit(X_train)
        model = LogisticRegression(C=0.01, max_iter=2000, solver="lbfgs")
        model.fit(scaler.transform(X_train), y_train)
        if checked_int(np.max(model.n_iter_)) >= 2000:
            raise RuntimeError("endpoint logistic readout failed to converge")
        train_prob = model.predict_proba(scaler.transform(X_train))
        eval_prob = model.predict_proba(scaler.transform(X_eval))
        coef = np.asarray(model.coef_, dtype=np.float64)
        intercept = np.asarray(model.intercept_, dtype=np.float64)
        model_name = "logistic_C0.01"
    model_classes = np.asarray(model.classes_, dtype=np.int64)
    if set(model_classes.tolist()) != set(classes.tolist()):
        raise RuntimeError(
            f"readout missing target classes for {target}: {model_classes}"
        )
    train_aligned = align_probabilities(train_prob, model_classes, classes)
    eval_aligned = align_probabilities(eval_prob, model_classes, classes)
    joblib.dump(
        {"model": model, "scaler": scaler, "classes": classes},
        outdir / "readout_model.joblib",
    )
    state_path = outdir / "readout_state.npz"
    scaler_mean = np.asarray(scaler.mean_, dtype=np.float64)
    scaler_scale = np.asarray(scaler.scale_, dtype=np.float64)
    lda_classes = (
        model_classes
        if representation == "raw_svd_lda"
        else np.empty((0,), dtype=np.int64)
    )
    lda_means = np.asarray(getattr(model, "means_", np.empty((0, 0))), dtype=np.float64)
    lda_priors = np.asarray(getattr(model, "priors_", np.empty((0,))), dtype=np.float64)
    lda_xbar = np.asarray(getattr(model, "xbar_", np.empty((0,))), dtype=np.float64)
    lda_scalings = np.asarray(
        getattr(model, "scalings_", np.empty((0, 0))), dtype=np.float64
    )
    np.savez_compressed(
        state_path,
        model=np.asarray(model_name),
        target=np.asarray(target),
        representation=np.asarray(representation),
        classes=classes,
        model_classes=model_classes,
        scaler_mean=scaler_mean,
        scaler_scale=scaler_scale,
        coef=coef,
        intercept=intercept,
        lda_classes=lda_classes,
        lda_means=lda_means,
        lda_priors=lda_priors,
        lda_xbar=lda_xbar,
        lda_scalings=lda_scalings,
    )
    return (
        classes[train_aligned.argmax(axis=1)],
        train_aligned,
        classes[eval_aligned.argmax(axis=1)],
        eval_aligned,
        sha256_file(state_path),
    )


def align_probabilities(
    prob: np.ndarray, model_classes: np.ndarray, classes: np.ndarray
) -> np.ndarray:
    aligned = np.zeros((prob.shape[0], len(classes)), dtype=np.float64)
    for src, klass in enumerate(model_classes):
        dst = checked_int(np.flatnonzero(classes == klass)[0])
        aligned[:, dst] = prob[:, src]
    np.testing.assert_allclose(aligned.sum(axis=1), 1.0, atol=1e-6)
    return aligned


def predict_readout_state(
    state_path: Path, X: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    with np.load(state_path, allow_pickle=False) as state:
        model_name = str(state["model"].tolist())
        classes = np.asarray(state["classes"], dtype=np.int64)
        mean = np.asarray(state["scaler_mean"], dtype=np.float64)
        scale = np.asarray(state["scaler_scale"], dtype=np.float64)
        Xs = (X - mean) / scale
        if model_name == "logistic_C0.01":
            logits = Xs @ np.asarray(state["coef"], dtype=np.float64).T + np.asarray(
                state["intercept"], dtype=np.float64
            )
            logits -= logits.max(axis=1, keepdims=True)
            exp = np.exp(logits)
            prob = exp / exp.sum(axis=1, keepdims=True)
            model_classes = np.asarray(state["model_classes"], dtype=np.int64)
        elif model_name == "raw_svd_lda":
            # Replay for LDA is delegated to saved predictions in verify mode; this
            # state is still hash-bound.  Avoid reimplementing sklearn internals.
            raise RuntimeError("raw_svd_lda replay requires saved prediction arrays")
        else:
            raise RuntimeError(f"unknown readout model: {model_name}")
    aligned = align_probabilities(prob, model_classes, classes)
    return classes[aligned.argmax(axis=1)], aligned


def brier_score(y: np.ndarray, prob: np.ndarray, classes: np.ndarray) -> float:
    class_to_col = {checked_int(k): idx for idx, k in enumerate(classes)}
    target = np.zeros_like(prob, dtype=np.float64)
    for row, label in enumerate(y):
        target[row, class_to_col[checked_int(label)]] = 1.0
    return parse_float(np.mean(np.sum((prob - target) ** 2, axis=1)))


def confusion_counts(
    y: np.ndarray, pred: np.ndarray, classes: np.ndarray
) -> np.ndarray:
    matrix = np.zeros((len(classes), len(classes)), dtype=np.int64)
    index = {checked_int(label): idx for idx, label in enumerate(classes)}
    for truth, guess in zip(y, pred, strict=True):
        matrix[index[checked_int(truth)], index[checked_int(guess)]] += 1
    return matrix


def metric_row(
    *,
    y: np.ndarray,
    pred: np.ndarray,
    prob: np.ndarray,
    classes: np.ndarray,
    prefix: Mapping[str, Any],
) -> dict[str, Any]:
    if prob.shape != (len(y), len(classes)):
        raise RuntimeError("probability shape mismatch")
    if not np.isfinite(prob).all() or (prob < -1e-12).any():
        raise RuntimeError("invalid probabilities")
    np.testing.assert_allclose(prob.sum(axis=1), 1.0, atol=1e-6)
    recalls = recall_by_class(y, pred, classes)
    return {
        **prefix,
        "n": checked_int(len(y)),
        "accuracy": parse_float(accuracy_score(y, pred)),
        "balanced_accuracy": parse_float(balanced_accuracy_score(y, pred)),
        "macro_f1": parse_float(f1_score(y, pred, average="macro")),
        "log_loss": parse_float(log_loss(y, prob, labels=classes)),
        "brier": brier_score(y, prob, classes),
        "uniform_balanced_accuracy": 1.0 / len(classes),
        "uniform_log_loss": parse_float(math.log(len(classes))),
        "class_recalls": recalls,
    }


def recall_by_class(
    y: np.ndarray, pred: np.ndarray, classes: np.ndarray
) -> dict[str, float | None]:
    out: dict[str, float | None] = {}
    for klass in classes:
        mask = y == klass
        out[str(checked_int(klass))] = (
            None if not np.any(mask) else parse_float(np.mean(pred[mask] == klass))
        )
    return out


def prediction_rows(
    *,
    y: np.ndarray,
    pred: np.ndarray,
    prob: np.ndarray,
    classes: np.ndarray,
    split: str,
    prefix: Mapping[str, Any],
    plans: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    rows = []
    for idx, (truth, guess) in enumerate(zip(y, pred, strict=True)):
        rows.append(
            {
                **prefix,
                "split": split,
                "row_index": idx,
                "row_id": plans[idx]["row_id"],
                "true": checked_int(truth),
                "pred": checked_int(guess),
                "probabilities": {
                    str(checked_int(c)): parse_float(prob[idx, ci])
                    for ci, c in enumerate(classes)
                },
                "sources": dict(plans[idx]["sources"]),
            }
        )
    return rows


def confusion_rows(
    *,
    y: np.ndarray,
    pred: np.ndarray,
    classes: np.ndarray,
    prefix: Mapping[str, Any],
) -> list[dict[str, Any]]:
    matrix = confusion_counts(y, pred, classes)
    rows = []
    denominators = matrix.sum(axis=1)
    for i, truth in enumerate(classes):
        for j, guess in enumerate(classes):
            rows.append(
                {
                    **prefix,
                    "true": checked_int(truth),
                    "pred": checked_int(guess),
                    "count": checked_int(matrix[i, j]),
                    "row_normalized_recall": None
                    if denominators[i] == 0
                    else parse_float(matrix[i, j] / denominators[i]),
                }
            )
    return rows


def fit_all_readouts(
    bundle: FeatureBundle, outdir: Path, *, deadline: float | None = None
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    metrics: list[dict[str, Any]] = []
    confusions: list[dict[str, Any]] = []
    cell_count = bundle.train_bundle.X_cue.shape[1]
    for representation in REPRESENTATIONS:
        source_rep = "raw" if representation == "raw_svd_lda" else representation
        for window in WINDOWS:
            Xtr = extract_window_features(
                source_rep,
                bundle.features_train[source_rep],
                window,
                cell_count=cell_count,
            )
            Xde = extract_window_features(
                source_rep,
                bundle.features_development[source_rep],
                window,
                cell_count=cell_count,
            )
            for target in TARGETS:
                check_deadline(deadline)
                ytr = target_labels(bundle.train_bundle.y_pair, target)
                yde = target_labels(bundle.development_bundle.y_pair, target)
                prefix = {
                    "world": bundle.world,
                    "world_index": bundle.world_index,
                    "seed": bundle.seed,
                    "representation": representation,
                    "window": window,
                    "target": target,
                    "feature_dim": checked_int(Xtr.shape[1]),
                }
                state_dir = outdir / representation / window / target
                ptr, strn, pde, sde, state_hash = fit_readout_state(
                    X_train=Xtr,
                    y_train=ytr,
                    X_eval=Xde,
                    target=target,
                    representation=representation,
                    outdir=state_dir,
                )
                classes = target_classes(target)
                np.savez_compressed(
                    state_dir / "readout_predictions.npz",
                    classes=classes,
                    y_train=ytr,
                    pred_train=ptr,
                    prob_train=strn,
                    y_development=yde,
                    pred_development=pde,
                    prob_development=sde,
                )
                metrics.append(
                    metric_row(
                        y=ytr,
                        pred=ptr,
                        prob=strn,
                        classes=classes,
                        prefix={
                            **prefix,
                            "split": "train",
                            "readout_state_sha256": state_hash,
                        },
                    )
                )
                metrics.append(
                    metric_row(
                        y=yde,
                        pred=pde,
                        prob=sde,
                        classes=classes,
                        prefix={
                            **prefix,
                            "split": "development",
                            "readout_state_sha256": state_hash,
                        },
                    )
                )
                confusions.extend(
                    confusion_rows(
                        y=ytr,
                        pred=ptr,
                        classes=classes,
                        prefix={**prefix, "split": "train"},
                    )
                )
                confusions.extend(
                    confusion_rows(
                        y=yde,
                        pred=pde,
                        classes=classes,
                        prefix={**prefix, "split": "development"},
                    )
                )
    return metrics, confusions


def summarize_paired_comparisons(
    metrics: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    fields = ("accuracy", "balanced_accuracy", "macro_f1", "log_loss", "brier")
    grouped: dict[tuple[str, int, str, str, str], dict[str, Mapping[str, Any]]] = {}
    for row in metrics:
        split = str(row["split"])
        if split not in {"train", "development"}:
            raise RuntimeError(f"unexpected metric split: {split}")
        key = (
            str(row["world"]),
            checked_int(row["seed"]),
            str(row["representation"]),
            str(row["window"]),
            str(row["target"]),
        )
        splits = grouped.setdefault(key, {})
        if split in splits:
            raise RuntimeError(f"duplicate comparison metric row: {key}/{split}")
        splits[split] = row

    model_gaps = []
    paired: dict[tuple[str, int, str, str], dict[str, Mapping[str, Any]]] = {}
    for key, splits in sorted(grouped.items()):
        if set(splits) != {"train", "development"}:
            raise RuntimeError(f"incomplete train/development metrics: {key}")
        world, seed, representation, window, target = key
        train, development = splits["train"], splits["development"]
        model_gaps.append(
            {
                "world": world,
                "seed": seed,
                "representation": representation,
                "window": window,
                "target": target,
                "n_train": checked_int(train["n"]),
                "n_development": checked_int(development["n"]),
                "train_minus_development": {
                    field: parse_float(train[field]) - parse_float(development[field])
                    for field in fields
                },
            }
        )
        if representation in {"cebra_cue", "cebra_joint"}:
            pair_key = (world, seed, window, target)
            arms = paired.setdefault(pair_key, {})
            arms[representation] = development

    paired_rows = []
    for (world, seed, window, target), arms in sorted(paired.items()):
        if set(arms) != {"cebra_cue", "cebra_joint"}:
            raise RuntimeError(
                f"unpaired cue/joint development metrics: {world}/{seed}/{window}/{target}"
            )
        cue, joint = arms["cebra_cue"], arms["cebra_joint"]
        if checked_int(cue["n"]) != checked_int(joint["n"]):
            raise RuntimeError(
                f"cue/joint development support mismatch: {world}/{seed}/{window}/{target}"
            )
        paired_rows.append(
            {
                "world": world,
                "seed": seed,
                "window": window,
                "target": target,
                "n_development": checked_int(cue["n"]),
                "joint_minus_cue": {
                    field: parse_float(joint[field]) - parse_float(cue[field])
                    for field in ("accuracy", "balanced_accuracy", "macro_f1")
                },
                "cue_minus_joint": {
                    field: parse_float(cue[field]) - parse_float(joint[field])
                    for field in ("log_loss", "brier")
                },
            }
        )
    return {
        "gap_direction": "train minus development",
        "paired_difference_direction": "joint minus cue for scores; cue minus joint for losses",
        "model_gaps": model_gaps,
        "cue_joint_development": paired_rows,
    }


def summarize_null_families(metrics: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    rows = [row for row in metrics if row.get("split") == "development"]
    grouped: dict[tuple[str, str, str, str, str], list[float]] = defaultdict(list)
    seen_seeds: dict[tuple[str, str, str, str], set[int]] = defaultdict(set)
    for row in rows:
        group = (
            str(row["world"]),
            str(row["representation"]),
            str(row["window"]),
            str(row["target"]),
        )
        seen_seeds[group].add(checked_int(row["seed"]))
        grouped[group + ("balanced_accuracy",)].append(
            parse_float(row["balanced_accuracy"])
        )
        grouped[group + ("log_loss",)].append(parse_float(row["log_loss"]))
    means: dict[tuple[str, str, str, str, str], float] = {}
    for key, values in grouped.items():
        if len(values) != len(SEEDS) or seen_seeds[key[:4]] != set(SEEDS):
            raise RuntimeError(f"incomplete seed metrics for null family: {key}")
        means[key] = parse_float(np.mean(values))

    def value(world: str, rep: str, window: str, target: str, field: str) -> float:
        return means[(world, rep, window, target, field)]

    worlds = sorted({str(row["world"]) for row in rows})
    if "observed" not in worlds or len(worlds) != 1 + len(NULL_SEEDS):
        raise RuntimeError(
            "null-family metrics do not contain observed plus all declared worlds"
        )
    stats: dict[str, dict[str, float]] = {}
    for world in worlds:
        whole_gains = []
        bin_gains = []
        absolute_ba = []
        absolute_loss_skill = []
        for target in TARGETS:
            k = len(target_classes(target))
            log_k = math.log(k)
            cue_loss = value(world, "cebra_cue", "wholecue", target, "log_loss")
            joint_loss = value(world, "cebra_joint", "wholecue", target, "log_loss")
            whole_gains.append((cue_loss - joint_loss) / log_k)
            for window in BIN_WINDOWS:
                bin_gains.append(
                    (
                        value(world, "cebra_cue", window, target, "log_loss")
                        - value(world, "cebra_joint", window, target, "log_loss")
                    )
                    / log_k
                )
                for representation in REPRESENTATIONS:
                    ba = value(
                        world, representation, window, target, "balanced_accuracy"
                    )
                    absolute_ba.append((ba - 1.0 / k) / (1.0 - 1.0 / k))
                    loss = value(world, representation, window, target, "log_loss")
                    absolute_loss_skill.append((log_k - loss) / log_k)
        stats[world] = {
            "wholecue_joint_logloss_gain_max_normalized": max(whole_gains),
            "cue_joint_bin_logloss_gain_max_normalized": max(bin_gains),
            "absolute_bin_balanced_accuracy_max_normalized": max(absolute_ba),
            "absolute_bin_logloss_skill_max_normalized": max(absolute_loss_skill),
        }
    null_worlds = [world for world in worlds if world != "observed"]
    observed = stats["observed"]
    return {
        "seed_aggregation": "mean of 3 computational seeds within each world",
        "maxima_are_descriptive": True,
        "pseudorow_bootstrap_used": False,
        "by_world": stats,
        "plus_one_upper_tail": {
            family: (
                1
                + sum(
                    stats[world][family] >= observed[family] - 1e-12
                    for world in null_worlds
                )
            )
            / (1 + len(null_worlds))
            for family in observed
        },
        "null_world_count": len(null_worlds),
    }


def source_support_rows(cohort: EndpointCohort) -> list[dict[str, Any]]:
    rows = []
    counts: Counter[tuple[str, str, str]] = Counter(
        (m.session_id, m.split, m.label) for m in cohort.metas
    )
    for session in sorted({m.session_id for m in cohort.metas}):
        for split in ("train", "development"):
            for label in PAIR_LABELS:
                rows.append(
                    {
                        "session_id": session,
                        "split": split,
                        "label": label,
                        "sources": counts[(session, split, label)],
                    }
                )
    return rows


def deletion_metrics(
    y: np.ndarray,
    pred: np.ndarray,
    prob: np.ndarray,
    classes: np.ndarray,
    keep: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Exact fixed-prediction deletion scores; missing classes remain inestimable."""
    if keep.ndim != 2 or keep.shape[1] != len(y) or keep.dtype != bool:
        raise RuntimeError("invalid source-deletion keep mask")
    if prob.shape != (len(y), len(classes)) or not np.isfinite(prob).all():
        raise RuntimeError("invalid source-deletion probabilities")
    if np.any(prob < 0) or np.any(prob > 1):
        raise RuntimeError("source-deletion probability outside [0,1]")
    np.testing.assert_allclose(prob.sum(axis=1), 1, atol=1e-6)
    membership = (y[:, None] == classes).astype(np.float64)
    if not np.all(membership.sum(axis=1) == 1):
        raise RuntimeError("unknown source-deletion target class")
    remaining = keep @ membership
    correct = keep @ (membership * (pred == y)[:, None])
    estimable = np.all(remaining > 0, axis=1)
    ba = np.full(len(keep), np.nan)
    ba[estimable] = (correct[estimable] / remaining[estimable]).mean(axis=1)
    # Matches sklearn log_loss clipping, not a renormalization or new metric.
    eps = np.finfo(prob.dtype).eps
    row_loss = -(membership * np.log(np.clip(prob, eps, 1 - eps))).sum(axis=1)
    loss = np.full(len(keep), np.nan)
    loss[estimable] = (keep[estimable] @ row_loss) / keep[estimable].sum(axis=1)
    return remaining, ba, loss


def source_deletion_sensitivity(
    run_dir: Path, *, deadline: float | None = None
) -> dict[str, Any]:
    metric_values: dict[tuple[int, str, str, str], dict[str, list[float]]] = (
        defaultdict(lambda: {"balanced_accuracy": [], "log_loss": []})
    )
    inestimable_ids: dict[tuple[int, str], dict[str, list[int]]] = defaultdict(dict)
    gain_values: dict[tuple[int, str, str, str], dict[str, float]] = defaultdict(dict)
    all_sources: set[str] = set()
    sources_by_seed: dict[str, int] = {}

    for seed in SEEDS:
        seed_dir = run_dir / "observed" / f"seed{seed}"
        manifest = read_json(seed_dir / "pseudo_development_manifest.json")
        source_rows: dict[str, set[int]] = defaultdict(set)
        for item in manifest:
            source_rows[str(item["source_trial_id"])].add(
                checked_int(item["pseudo_row"])
            )
        sources = sorted(source_rows)
        all_sources.update(sources)
        sources_by_seed[str(seed)] = len(sources)
        for prediction_path in sorted(
            seed_dir.glob("readouts/*/*/*/readout_predictions.npz")
        ):
            check_deadline(deadline)
            state = prediction_path.parent
            target = state.name
            window = state.parent.name
            representation = state.parent.parent.name
            with np.load(prediction_path, allow_pickle=False) as saved:
                y = np.asarray(saved["y_development"], dtype=np.int64)
                pred = np.asarray(saved["pred_development"], dtype=np.int64)
                prob = np.asarray(saved["prob_development"], dtype=np.float64)
                classes = np.asarray(saved["classes"], dtype=np.int64)
            if not np.array_equal(classes, target_classes(target)):
                raise RuntimeError(
                    f"source sensitivity class order mismatch: {prediction_path}"
                )
            values = metric_values[(seed, representation, window, target)]
            keep = np.ones((len(sources), len(y)), dtype=bool)
            for source_index, source_id in enumerate(sources):
                dropped = np.fromiter(source_rows[source_id], dtype=np.int64)
                if np.any(dropped < 0) or np.any(dropped >= len(y)):
                    raise RuntimeError("source-deletion row index outside predictions")
                keep[source_index, dropped] = False
            remaining, ba, losses = deletion_metrics(y, pred, prob, classes, keep)
            for source_index, source_id in enumerate(sources):
                missing = classes[remaining[source_index] == 0].tolist()
                if missing:
                    inestimable_ids[(seed, target)][source_id] = missing
                    continue
                values["balanced_accuracy"].append(parse_float(ba[source_index]))
                loss = parse_float(losses[source_index])
                values["log_loss"].append(loss)
                if representation in {"cebra_cue", "cebra_joint"}:
                    gain_values[(seed, window, target, source_id)][representation] = (
                        loss
                    )

    def bounds(values: Sequence[float]) -> dict[str, float | None]:
        if not values:
            return {"min": None, "median": None, "max": None}
        return {
            "min": parse_float(np.min(values)),
            "median": parse_float(np.median(values)),
            "max": parse_float(np.max(values)),
        }

    group_rows = []
    for (seed, representation, window, target), values in sorted(metric_values.items()):
        group_rows.append(
            {
                "seed": seed,
                "representation": representation,
                "window": window,
                "target": target,
                "source_deletions": sources_by_seed[str(seed)],
                "inestimable_deletions": len(inestimable_ids[(seed, target)]),
                "estimable_deletions": len(values["log_loss"]),
                "balanced_accuracy": bounds(values["balanced_accuracy"]),
                "log_loss": bounds(values["log_loss"]),
            }
        )
    paired_gains: dict[tuple[int, str, str], list[float]] = defaultdict(list)
    for (seed, window, target, _source), arms in gain_values.items():
        if set(arms) == {"cebra_cue", "cebra_joint"}:
            paired_gains[(seed, window, target)].append(
                arms["cebra_cue"] - arms["cebra_joint"]
            )
    return {
        "deleted_sources": len(all_sources),
        "used_sources_by_seed": sources_by_seed,
        "inestimable_source_ids_by_seed_target": [
            {
                "seed": seed,
                "target": target,
                "source_ids": sorted(ids),
                "count": len(ids),
            }
            for (seed, target), ids in sorted(inestimable_ids.items())
        ],
        "group_summaries": group_rows,
        "paired_joint_logloss_gain": [
            {
                "seed": seed,
                "window": window,
                "target": target,
                "source_deletions": sources_by_seed[str(seed)],
                "estimable_deletions": len(values),
                "gain_normalized_by_log_classes": bounds(
                    [value / math.log(len(target_classes(target))) for value in values]
                ),
            }
            for (seed, window, target), values in sorted(paired_gains.items())
        ],
        "pseudorow_bootstrap_used": False,
    }


def write_hash_manifest(root: Path) -> dict[str, str]:
    manifest: dict[str, str] = {}
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        relative = str(path.relative_to(root))
        if relative == "hash_manifest.json":
            continue
        manifest[relative] = sha256_file(path)
    write_json(root / "hash_manifest.json", manifest)
    return manifest


def verify_hash_manifest(root: Path) -> dict[str, Any]:
    manifest = read_json(root / "hash_manifest.json")
    expected_files = set(manifest)
    actual_files = {
        str(path.relative_to(root))
        for path in root.rglob("*")
        if path.is_file() and str(path.relative_to(root)) != "hash_manifest.json"
    }
    if actual_files != expected_files:
        missing = sorted(expected_files - actual_files)
        extra = sorted(actual_files - expected_files)
        raise RuntimeError(
            f"run hash manifest file-set mismatch: missing={missing[:5]} extra={extra[:5]}"
        )
    for relative, expected in manifest.items():
        observed = sha256_file(safe_child(root, relative))
        if observed != expected:
            raise RuntimeError(
                f"run hash mismatch {relative}: {observed} != {expected}"
            )
    return {"status": "passed", "files": len(manifest)}


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open() as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise RuntimeError(f"invalid JSONL row {line_number}: {path}") from exc
            if not isinstance(row, dict):
                raise RuntimeError(f"JSONL row {line_number} is not an object: {path}")
            rows.append(row)
    return rows


def helper_paths() -> dict[str, Path]:
    return {
        **study_sources(SCRIPT_PATH),
        "docs/reports/cebra-endpoint-time-readout-20261006/protocol.md": PROTOCOL_PATH,
        "pyproject.toml": REPOSITORY_ROOT / "pyproject.toml",
        "uv.lock": REPOSITORY_ROOT / "uv.lock",
    }


def helper_hashes() -> dict[str, str]:
    return {name: sha256_file(path) for name, path in helper_paths().items()}


def write_run_provenance(
    output_dir: Path,
    *,
    accepted_root: Path,
    navigation_audit: Path,
    navigation_npz: Path,
    approval_path: Path,
    benchmark_receipt: Path,
) -> dict[str, Any]:
    code_hashes = helper_hashes()
    snapshot_sources(output_dir / "code_snapshot", helper_paths())
    provenance = {
        "accepted_root": str(accepted_root.resolve()),
        "accepted_artifact_manifest_sha256": sha256_file(
            accepted_root / "artifact_hashes.json"
        ),
        "navigation_audit": str(navigation_audit.resolve()),
        "navigation_audit_sha256": sha256_file(navigation_audit),
        "navigation_npz": str(navigation_npz.resolve()),
        "navigation_npz_sha256": sha256_file(navigation_npz),
        "prefit_approval": str(approval_path.resolve()),
        "prefit_approval_sha256": sha256_file(approval_path),
        "resource_benchmark": str(benchmark_receipt.resolve()),
        "resource_benchmark_sha256": sha256_file(benchmark_receipt),
        "code_hashes": code_hashes,
        "python": sys.version,
        "packages": {
            name: package_version(name)
            for name in ("numpy", "scikit-learn", "cebra", "torch", "joblib")
        },
    }
    write_json(output_dir / "run_inputs.json", provenance)
    return provenance


def verify_navigation_audit_claims(
    audit: Mapping[str, Any], cohort: EndpointCohort
) -> None:
    train = [meta for meta in cohort.metas if meta.split == "train"]
    development = [meta for meta in cohort.metas if meta.split != "train"]
    train_ids = sorted(meta.source_trial_id for meta in train)
    if (
        audit.get("training_sources") != len(train_ids)
        or audit.get("training_source_allowlist_count") != len(train_ids)
        or audit.get("development_sources_with_no_navigation") != len(development)
        or audit.get("training_source_allowlist_sha256") != stable_hash(train_ids)
    ):
        raise RuntimeError("navigation audit source allowlist/count mismatch")
    for field in ("raw_hashes_checked", "timing_checked", "cue_recount_exact"):
        if not isinstance(audit.get(field), bool) or not audit[field]:
            raise RuntimeError(f"navigation audit lacks successful {field} proof")
    if (
        not isinstance(audit.get("development_navigation_selected"), bool)
        or audit["development_navigation_selected"]
    ):
        raise RuntimeError("navigation audit does not prove development exclusion")
    if audit.get("cue_recount_mode") != "raw_spikes_through_accepted_csv_precision":
        raise RuntimeError("navigation audit lacks accepted preprocessing replay")
    split_audit = audit.get("split_gate_audit")
    yielded = (
        split_audit.get("rows_yielded_by_split")
        if isinstance(split_audit, dict)
        else None
    )
    if (
        not isinstance(split_audit, dict)
        or split_audit.get("allowed_splits") != ["train"]
        or split_audit.get("forbidden_rows_yielded") != 0
        or not isinstance(yielded, dict)
        or set(yielded) != {"trials", "cue_counts"}
        or any(set(counts) - {"train"} for counts in yielded.values())
        or yielded.get("trials", {}).get("train", 0) < len(train_ids)
        or yielded.get("cue_counts", {}).get("train", 0) <= 0
    ):
        raise RuntimeError("navigation audit split-gate proof is invalid")


_BUILTIN_INT = int
_BUILTIN_FLOAT = float


def parse_float(value: Any, description: str = "float conversion") -> float:
    try:
        return _BUILTIN_FLOAT(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise RuntimeError(f"invalid numeric value: {description}") from exc


def checked_float(value: Any, description: str) -> float:
    parsed = parse_float(value, description)
    if not math.isfinite(parsed):
        raise RuntimeError(f"non-finite numeric value: {description}")
    return parsed


def checked_int(value: Any, description: str = "integer conversion") -> int:
    try:
        return _BUILTIN_INT(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise RuntimeError(f"invalid integer value: {description}") from exc


def audit_float(row: Mapping[str, str], field: str, source_id: str) -> float:
    try:
        value = row[field]
    except KeyError as exc:
        raise RuntimeError(f"missing audit field {field}: {source_id}") from exc
    return checked_float(value, f"{field}: {source_id}")


def audit_int(row: Mapping[str, str], field: str, source_id: str) -> int:
    try:
        value = row[field]
    except KeyError as exc:
        raise RuntimeError(f"missing audit field {field}: {source_id}") from exc
    return checked_int(value, f"{field}: {source_id}")


def verify_navigation_window_lineage(
    nav: EndpointNavData,
    cohort: EndpointCohort,
    rows: Sequence[Mapping[str, str]],
    trial_rows: Mapping[str, Mapping[str, str]],
) -> None:
    train = {
        meta.source_trial_id: meta for meta in cohort.metas if meta.split == "train"
    }
    by_source: dict[str, Mapping[str, str]] = {}
    for row in rows:
        source_id = row.get("source_trial_id", "")
        if source_id in by_source:
            raise RuntimeError(f"duplicate navigation source window: {source_id}")
        by_source[source_id] = row
    if set(by_source) != set(train) or set(nav.source_ids) != set(train):
        raise RuntimeError("navigation windows/cache do not match training allowlist")
    for source_id, meta in train.items():
        row = by_source[source_id]
        if (
            row.get("inner_split") != "train"
            or row.get("session_id") != meta.session_id
            or row.get("label") != meta.label
        ):
            raise RuntimeError(f"navigation window identity mismatch: {source_id}")
        trial = trial_rows.get(source_id)
        if (
            trial is None
            or trial.get("split") != "train"
            or trial.get("session_id") != meta.session_id
            or trial.get("outcome") != "success"
        ):
            raise RuntimeError(f"training trial ledger lineage mismatch: {source_id}")
        trial_index = audit_int(row, "trial_index", source_id)
        ledger_trial_index = audit_int(trial, "trial_index", source_id)
        if trial_index != ledger_trial_index:
            raise RuntimeError(f"navigation/ledger trial-index mismatch: {source_id}")
        nav_index = nav.source_index[source_id]
        if trial_index < 1 or nav.trial_indices[nav_index] != trial_index:
            raise RuntimeError(f"navigation trial-index lineage mismatch: {source_id}")
        if meta.trial_index is not None and meta.trial_index != trial_index:
            raise RuntimeError(f"accepted trial-index mismatch: {source_id}")
        if (
            nav.source_sessions[nav_index] != meta.session_id
            or nav.source_labels[nav_index] != meta.label
        ):
            raise RuntimeError(f"navigation cache identity mismatch: {source_id}")
        cue_start = audit_float(row, "cue_start_s", source_id)
        cue_end = audit_float(row, "cue_end_s", source_id)
        nav_end = audit_float(row, "nav_end_s", source_id)
        nav_duration = audit_float(row, "nav_duration_s", source_id)
        imported_start = audit_float(row, "imported_cue_start_s", source_id)
        imported_end = audit_float(row, "imported_cue_end_s", source_id)
        cue_duration = audit_float(row, "cue_duration_s", source_id)
        if (
            parse_float(imported_csv_value(cue_start)) != imported_start
            or parse_float(imported_csv_value(cue_end)) != imported_end
            or not math.isclose(
                cue_duration, cue_end - cue_start, rel_tol=0, abs_tol=1e-9
            )
            or not math.isclose(
                nav_duration, nav_end - cue_end, rel_tol=0, abs_tol=1e-9
            )
            or not math.isclose(
                cue_duration,
                audit_float(trial, "ripple_cue_duration_s", source_id),
                rel_tol=0,
                abs_tol=1e-5,
            )
            or not math.isclose(
                nav_duration,
                audit_float(trial, "ripple_nav_duration_s", source_id),
                rel_tol=0,
                abs_tol=1e-5,
            )
            or parse_ripple_codes(row["ripple_codes"])
            != parse_ripple_codes(trial.get("ripple_codes", ""))
        ):
            raise RuntimeError(
                f"navigation window timing/code audit mismatch: {source_id}"
            )
        n_bins = audit_int(row, "complete_nav_bins_100ms", source_id)
        if n_bins != nav.n_bins[nav_index] or n_bins < 2:
            raise RuntimeError(f"navigation bin-count lineage mismatch: {source_id}")
        nominal_end = cue_end + n_bins * BIN_WIDTH_S
        if nominal_end - nav_end > 1e-12:
            raise RuntimeError(f"navigation bin exceeds raw window: {source_id}")
        expected_end = min(nav_end, nominal_end)
        if not math.isclose(
            audit_float(row, "complete_nav_window_end_s", source_id),
            expected_end,
            rel_tol=0,
            abs_tol=1e-9,
        ):
            raise RuntimeError(f"navigation bin-end audit mismatch: {source_id}")
        expected_tail = max(0.0, nav_duration - n_bins * BIN_WIDTH_S)
        if not math.isclose(
            audit_float(row, "discarded_nav_tail_s", source_id),
            expected_tail,
            rel_tol=0,
            abs_tol=1e-9,
        ):
            raise RuntimeError(f"navigation tail audit mismatch: {source_id}")
        expected_cells = sum(
            session_from_cell(cell) == meta.session_id for cell in cohort.cells
        )
        if audit_int(row, "observed_cells", source_id) != expected_cells:
            raise RuntimeError(f"navigation cell-mask audit mismatch: {source_id}")


def validate_navigation_audit(
    audit_path: Path,
    navigation_npz: Path,
    cohort: EndpointCohort,
    nav: EndpointNavData,
) -> None:
    audit = read_json(audit_path)
    verify_navigation_audit_claims(audit, cohort)
    if Path(
        str(audit.get("nav_npz", ""))
    ).resolve() != navigation_npz.resolve() or audit.get(
        "nav_npz_sha256"
    ) != sha256_file(navigation_npz):
        raise RuntimeError("navigation audit does not bind the supplied NPZ")
    expected_ledger_hashes = {
        "source_files.csv": sha256_file(IMPORT_DIR / "source_files.csv"),
        "trials.csv": sha256_file(IMPORT_DIR / "trials.csv"),
        "cue_counts.csv.gz": sha256_file(IMPORT_DIR / "cue_counts.csv.gz"),
        "source_trial_splits.csv": sha256_file(SPLIT_DIR / "source_trial_splits.csv"),
        "split_summary.json": sha256_file(SPLIT_DIR / "split_summary.json"),
    }
    if audit.get("imported_ledger_hashes") != expected_ledger_hashes:
        raise RuntimeError("imported ledger hashes changed since navigation extraction")
    access = SplitFilteredAccess(IMPORT_DIR, SPLIT_DIR, allowed_splits=("train",))
    if audit.get("split_manifest_sha256") != access.split_hash:
        raise RuntimeError("navigation split manifest hash mismatch")
    expected_train_ids = {
        meta.source_trial_id for meta in cohort.metas if meta.split == "train"
    }
    outer_train_ids = set(access.allowed_source_ids)
    trial_rows = select_training_trial_rows(
        access.iter_trials(), expected_train_ids, outer_train_ids
    )
    current_gate = access.audit.as_dict()
    expected_outer_trial_yield = {"train": len(outer_train_ids)}
    if (
        current_gate["rows_yielded_by_split"].get("trials")
        != expected_outer_trial_yield
        or current_gate["rows_yielded_by_split"]["trials"]
        != audit["split_gate_audit"]["rows_yielded_by_split"]["trials"]
        or current_gate["forbidden_rows_yielded"] != 0
        or any(
            set(counts) - {"train"}
            for counts in current_gate["rows_yielded_by_split"].values()
        )
    ):
        raise RuntimeError("current training-only trial split gate failed")

    windows_name = audit.get("training_source_windows_csv")
    opened_name = audit.get("opened_raw_files_csv")
    if (
        windows_name != "training_source_windows.csv"
        or opened_name != "opened_raw_files.csv"
    ):
        raise RuntimeError("navigation audit sidecar paths are invalid")
    windows_path = safe_child(audit_path.parent, windows_name)
    opened_path = safe_child(audit_path.parent, opened_name)
    if sha256_file(windows_path) != audit.get("training_source_windows_csv_sha256"):
        raise RuntimeError("training source-window sidecar hash mismatch")
    if sha256_file(opened_path) != audit.get("opened_raw_files_csv_sha256"):
        raise RuntimeError("opened raw-file sidecar hash mismatch")
    verify_navigation_window_lineage(nav, cohort, read_csv(windows_path), trial_rows)

    sessions = {meta.session_id for meta in cohort.metas if meta.split == "train"}
    expected_keys = {("ripple_markers", session, "") for session in sessions}
    expected_keys.update(
        ("spiketrain", session_from_cell(cell), cell)
        for cell in cohort.cells
        if session_from_cell(cell) in sessions
    )
    raw_manifest = raw_source_files_manifest(IMPORT_DIR, CANONICAL_ROOT)
    opened_rows = read_csv(opened_path)
    opened_by_key: dict[tuple[str, str, str], Mapping[str, str]] = {}
    for row in opened_rows:
        key = (row["role"], row["session_id"], row.get("cell_id", ""))
        if key in opened_by_key:
            raise RuntimeError(f"duplicate opened raw-file row: {key}")
        opened_by_key[key] = row
    if set(opened_by_key) != expected_keys or audit.get("opened_file_count") != len(
        expected_keys
    ):
        raise RuntimeError(
            "opened raw-file list does not match training cells/sessions"
        )
    for key, row in opened_by_key.items():
        manifest_row = raw_manifest.get(key)
        if manifest_row is None:
            raise RuntimeError(f"opened raw file missing from source manifest: {key}")
        if (
            Path(row["path"]).resolve() != raw_manifest_path(manifest_row).resolve()
            or row.get("sha256") != manifest_row.get("sha256")
            or row.get("manifest_sha256") != manifest_row.get("sha256")
        ):
            raise RuntimeError(f"opened raw-file hash/path mismatch: {key}")


def validate_resource_benchmark(receipt_path: Path) -> dict[str, Any]:
    resolved_receipt = receipt_path.resolve()
    if not resolved_receipt.is_file():
        raise RuntimeError("resource benchmark receipt does not exist")
    try:
        receipt = read_json(resolved_receipt)
    except (OSError, UnicodeError, json.JSONDecodeError, RuntimeError) as exc:
        raise RuntimeError("resource benchmark receipt is unreadable") from exc
    if not isinstance(receipt, Mapping):
        raise RuntimeError("resource benchmark receipt must be a JSON object")
    raw_access = receipt.get("raw_navigation_access")
    if (
        receipt.get("classification") != "software benchmark; invented arrays only"
        or checked_int(receipt.get("biological_fits"), "benchmark biological fits") != 0
        or not isinstance(raw_access, bool)
        or raw_access
    ):
        raise RuntimeError("resource benchmark is not a synthetic-only receipt")
    if receipt.get("code_hashes") != helper_hashes():
        raise RuntimeError("resource benchmark runner/protocol hashes are stale")
    if receipt.get("code_hashes_at_end") != receipt.get("code_hashes"):
        raise RuntimeError("resource benchmark source hashes changed during execution")
    device = receipt.get("device")
    configuration = receipt.get("configuration")
    if (
        device != "cuda"
        or receipt.get("cuda_available") is not True
        or not isinstance(configuration, Mapping)
    ):
        raise RuntimeError("resource benchmark must attest an available CUDA device")
    expected_configuration = {
        "updates": CEBRA_UPDATES,
        "batch_size": 256,
        "hidden": 32,
        "dim": CEBRA_DIM,
        "learning_rate": 3e-4,
        "cue_bins": CUE_BINS,
        "train_pseudorows": ROWS_PER_PAIR_TRAIN * len(PAIR_LABELS),
        "development_pseudorows": ROWS_PER_PAIR_DEVELOPMENT * len(PAIR_LABELS),
        "encoder_fits_projected": EXPECTED_ENCODER_FITS,
        "pca_fits_projected": EXPECTED_PCA_FITS,
        "readout_fits_projected": EXPECTED_READOUT_FITS,
        "world_seed_bundles_projected": EXPECTED_READOUT_FITS
        // (len(REPRESENTATIONS) * len(TARGETS) * len(WINDOWS)),
        "cells": EXPECTED_CELLS,
        "sessions": EXPECTED_SESSIONS,
    }
    if configuration.get("device") != device or any(
        configuration.get(key) != value for key, value in expected_configuration.items()
    ):
        raise RuntimeError("resource benchmark model configuration mismatch")

    benchmark_script = resolved_receipt.with_name("benchmark.py")
    preflight_path = resolved_receipt.parent.parent / "input-preflight.json"
    if not benchmark_script.is_file() or not preflight_path.is_file():
        raise RuntimeError("resource benchmark script or preflight receipt is missing")
    benchmark_script_hash = sha256_file(benchmark_script)
    preflight_hash = sha256_file(preflight_path)
    if receipt.get("benchmark_script_sha256") != benchmark_script_hash:
        raise RuntimeError("resource benchmark script hash mismatch")
    if receipt.get("benchmark_script_sha256_at_end") != benchmark_script_hash:
        raise RuntimeError("resource benchmark script changed during execution")
    if receipt.get("input_preflight_sha256") != preflight_hash:
        raise RuntimeError("resource benchmark preflight hash mismatch")
    if receipt.get("input_preflight_sha256_at_end") != preflight_hash:
        raise RuntimeError("resource benchmark preflight changed during execution")
    try:
        preflight = read_json(preflight_path)
    except (OSError, UnicodeError, json.JSONDecodeError, RuntimeError) as exc:
        raise RuntimeError(
            "resource benchmark metadata preflight is unreadable"
        ) from exc
    if not isinstance(preflight, Mapping):
        raise RuntimeError(
            "resource benchmark metadata preflight must be a JSON object"
        )
    preflight_raw_access = preflight.get("raw_navigation_access")
    if (
        preflight.get("status") != "passed"
        or not isinstance(preflight_raw_access, bool)
        or preflight_raw_access
        or checked_int(preflight.get("fits"), "preflight fits") != 0
    ):
        raise RuntimeError("resource benchmark metadata preflight is invalid")
    nav_cache_bytes = checked_int(
        preflight.get("dense_nav_cache_bytes"), "preflight navigation cache bytes"
    )
    if (
        checked_int(
            receipt.get("navigation_cache_bytes_from_preflight"),
            "benchmark navigation cache bytes",
        )
        != nav_cache_bytes
    ):
        raise RuntimeError("resource benchmark navigation-cache estimate mismatch")
    train_sources = checked_int(
        preflight.get("endpoint_inner_training_sources"),
        "preflight endpoint training sources",
    )
    development_sources = checked_int(
        preflight.get("endpoint_inner_development_sources"),
        "preflight endpoint development sources",
    )
    total_nav_bins = checked_int(
        preflight.get("total_nav_bins"), "preflight total navigation bins"
    )
    if (
        train_sources != EXPECTED_TRAIN_SOURCES
        or development_sources != EXPECTED_DEVELOPMENT_SOURCES
    ):
        raise RuntimeError(
            "resource benchmark preflight source counts differ from protocol"
        )
    upper_nav_bins = checked_int(
        receipt.get("upper_navigation_bins_per_source"),
        "benchmark upper navigation bins per source",
    )
    if upper_nav_bins < 1:
        raise RuntimeError("resource benchmark navigation-bin padding is invalid")
    nav_rows = EXPECTED_SESSIONS * upper_nav_bins
    synthetic_navigation_bytes = (
        nav_rows * EXPECTED_CELLS * np.dtype(np.float32).itemsize
        + nav_rows * EXPECTED_CELLS * np.dtype(np.bool_).itemsize
        + nav_rows * np.dtype(np.float32).itemsize
    )
    expected_nav_padding_bytes = max(
        0,
        nav_cache_bytes
        + total_nav_bins * np.dtype(np.float32).itemsize
        - synthetic_navigation_bytes,
    )
    expected_cohort_padding_bytes = (train_sources + development_sources) * (
        EXPECTED_CELLS * CUE_BINS * np.dtype(np.float32).itemsize
        + EXPECTED_CELLS * np.dtype(np.bool_).itemsize
        + CUE_BINS * np.dtype(np.float32).itemsize
    )
    expected_resident_padding_bytes = (
        expected_nav_padding_bytes + expected_cohort_padding_bytes
    )
    host_memory = receipt.get("host_memory")
    if not isinstance(host_memory, Mapping):
        raise RuntimeError("resource benchmark host-memory receipt is missing")
    observed_nav_padding_bytes = checked_int(
        host_memory.get("navigation_cache_padding_bytes"),
        "benchmark navigation-cache memory padding",
    )
    observed_cohort_padding_bytes = checked_int(
        host_memory.get("cue_cohort_padding_bytes"),
        "benchmark cue-cohort memory padding",
    )
    observed_resident_padding_bytes = checked_int(
        host_memory.get("synthetic_resident_padding_bytes"),
        "benchmark total synthetic resident padding",
    )
    peak_rss_kib = checked_int(receipt.get("peak_rss_kib"), "benchmark peak RSS")
    if (
        observed_nav_padding_bytes != expected_nav_padding_bytes
        or observed_cohort_padding_bytes != expected_cohort_padding_bytes
        or observed_resident_padding_bytes != expected_resident_padding_bytes
        or peak_rss_kib * 1024 < expected_resident_padding_bytes
    ):
        raise RuntimeError("resource benchmark memory-padding evidence is inconsistent")

    expected_readouts = len(REPRESENTATIONS) * len(TARGETS) * len(WINDOWS)
    expected_confusions = (
        2
        * len(REPRESENTATIONS)
        * len(WINDOWS)
        * sum(len(target_classes(target)) ** 2 for target in TARGETS)
    )
    if (
        checked_int(receipt.get("readout_states_per_seed"), "benchmark readout states")
        != expected_readouts
        or checked_int(
            receipt.get("confusion_rows_per_seed"), "benchmark confusion rows"
        )
        != expected_confusions
        or checked_int(
            receipt.get("sensitivity_readout_states"),
            "benchmark sensitivity readout states",
        )
        != len(SEEDS) * expected_readouts
        or checked_int(
            receipt.get("development_sources_in_sensitivity"),
            "benchmark sensitivity development sources",
        )
        != EXPECTED_DEVELOPMENT_SOURCES
        or checked_int(
            receipt.get("sensitivity_summary_sources"),
            "benchmark sensitivity summary sources",
        )
        != EXPECTED_DEVELOPMENT_SOURCES
    ):
        raise RuntimeError("resource benchmark did not cover the declared workload")

    if (
        checked_int(receipt.get("runtime_cap_seconds"), "benchmark runtime cap")
        != MAX_RUN_SECONDS
    ):
        raise RuntimeError("resource benchmark runtime cap differs from protocol")
    output_cap = parse_float(receipt.get("output_cap_gib"), "benchmark output cap")
    if not math.isclose(output_cap, OUTPUT_LIMIT_GIB, rel_tol=0, abs_tol=1e-9):
        raise RuntimeError("resource benchmark output cap differs from protocol")
    projected_seconds = parse_float(
        receipt.get("projected_full_seconds_with_25pct_margin"),
        "benchmark projected runtime with margin",
    )
    runtime_pass = receipt.get("runtime_pass_with_margin")
    if (
        not math.isfinite(projected_seconds)
        or not isinstance(runtime_pass, bool)
        or not runtime_pass
        or projected_seconds > MAX_RUN_SECONDS
    ):
        raise RuntimeError("resource benchmark runtime gate does not pass")
    projected_output_bytes = checked_int(
        receipt.get("projected_full_output_bytes_including_nav_cache"),
        "benchmark projected output bytes",
    )
    projected_model_output_bytes = checked_int(
        receipt.get("projected_model_output_bytes"),
        "benchmark projected model output bytes",
    )
    if projected_output_bytes != projected_model_output_bytes + nav_cache_bytes:
        raise RuntimeError("resource benchmark output projection is inconsistent")
    output_cap_bytes = OUTPUT_LIMIT_GIB * 1024**3
    output_pass = receipt.get("output_pass")
    if (
        not isinstance(output_pass, bool)
        or not output_pass
        or projected_output_bytes > output_cap_bytes
    ):
        raise RuntimeError("resource benchmark output gate does not pass")
    return {
        "receipt_sha256": sha256_file(resolved_receipt),
        "benchmark_script_sha256": benchmark_script_hash,
        "input_preflight_sha256": preflight_hash,
        "device": device,
        "projected_runtime_seconds_with_margin": projected_seconds,
        "projected_output_bytes": projected_output_bytes,
    }


def approval_facts(
    *,
    accepted_root: Path,
    navigation_audit: Path,
    navigation_npz: Path,
    benchmark_receipt: Path,
    config: Mapping[str, Any],
) -> dict[str, Any]:
    resource = validate_resource_benchmark(benchmark_receipt)
    if config.get("device") != resource["device"]:
        raise RuntimeError(
            "resource benchmark device differs from prefit configuration"
        )
    verify_accepted_endpoint_artifacts(accepted_root)
    cohort = load_endpoint_cohort(accepted_root, strict_expected=True)
    verify_observed_assembly_parity(cohort, accepted_root)
    nav = load_nav_data(navigation_npz, cohort)
    validate_navigation_audit(navigation_audit, navigation_npz, cohort, nav)
    observed_nav_hash = sha256_file(navigation_npz)
    return {
        "approved_for": "cebra-endpoint-time-readout-20261006-prefit-run",
        "code_protocol_hashes": helper_hashes(),
        "accepted_artifact_manifest_sha256": sha256_file(
            accepted_root / "artifact_hashes.json"
        ),
        "navigation_audit_sha256": sha256_file(navigation_audit),
        "navigation_npz_sha256": observed_nav_hash,
        "resource_benchmark_sha256": resource["receipt_sha256"],
        "resource_benchmark_script_sha256": resource["benchmark_script_sha256"],
        "resource_benchmark_preflight_sha256": resource["input_preflight_sha256"],
        "config_hash": stable_hash(config),
        "declared_budget": check_declared_budget(),
    }


def require_prefit_approval(
    path: Path,
    *,
    accepted_root: Path,
    navigation_audit: Path,
    navigation_npz: Path,
    benchmark_receipt: Path,
    config: Mapping[str, Any],
) -> dict[str, Any]:
    approval = read_json(path)
    approved = approval.get("approved")
    if not isinstance(approved, bool) or not approved:
        raise RuntimeError("prefit approval is not marked approved")
    expected = approval_facts(
        accepted_root=accepted_root,
        navigation_audit=navigation_audit,
        navigation_npz=navigation_npz,
        benchmark_receipt=benchmark_receipt,
        config=config,
    )
    observed = {key: approval.get(key) for key in expected}
    if observed != expected:
        raise RuntimeError(
            "approval facts differ from current code/input/navigation/resource/config"
        )
    return approval


@contextlib.contextmanager
def no_fit_guard() -> Iterator[None]:
    global FITS_BLOCKED
    old = FITS_BLOCKED
    FITS_BLOCKED = True
    original_logistic = LogisticRegression.fit
    original_lda = LinearDiscriminantAnalysis.fit
    original_pca = PCA.fit

    def forbid(*_args: Any, **_kwargs: Any) -> Any:
        raise RuntimeError("fit operation blocked during replay verification")

    LogisticRegression.fit = forbid  # type: ignore[method-assign]
    LinearDiscriminantAnalysis.fit = forbid  # type: ignore[method-assign]
    PCA.fit = forbid  # type: ignore[method-assign]
    try:
        yield
    finally:
        LogisticRegression.fit = original_logistic  # type: ignore[method-assign]
        LinearDiscriminantAnalysis.fit = original_lda  # type: ignore[method-assign]
        PCA.fit = original_pca  # type: ignore[method-assign]
        FITS_BLOCKED = old


def append_jsonl(path: Path, row: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as handle:
        handle.write(json.dumps(jsonable(row), sort_keys=True) + "\n")


def run_full_budget(args: argparse.Namespace) -> dict[str, Any]:
    validate_resource_benchmark(args.benchmark_receipt)
    set_thread_limits()
    check_declared_budget()
    if args.hidden != 32 or args.batch_size != 256 or not math.isclose(args.lr, 3e-4):
        raise RuntimeError("protocol fixes hidden=32, batch_size=256, and lr=3e-4")
    device = select_device(args.device)
    deadline = time.monotonic() + MAX_RUN_SECONDS
    out = args.output_dir
    artifact_summary = verify_accepted_endpoint_artifacts(args.accepted_root)
    cohort = load_endpoint_cohort(args.accepted_root, strict_expected=True)
    parity = verify_observed_assembly_parity(cohort, args.accepted_root)
    nav = load_nav_data(args.navigation_npz, cohort)
    config = {
        "seeds": list(SEEDS),
        "null_seeds": list(NULL_SEEDS),
        "rows_per_pair_train": ROWS_PER_PAIR_TRAIN,
        "rows_per_pair_development": ROWS_PER_PAIR_DEVELOPMENT,
        "updates": CEBRA_UPDATES,
        "device": device,
        "targets": list(TARGETS),
        "windows": list(WINDOWS),
        "representations": list(REPRESENTATIONS),
        "batch_size": args.batch_size,
        "hidden": args.hidden,
        "dim": CEBRA_DIM,
        "lr": args.lr,
    }
    approval = require_prefit_approval(
        args.approval,
        accepted_root=args.accepted_root,
        navigation_audit=args.navigation_audit,
        navigation_npz=args.navigation_npz,
        benchmark_receipt=args.benchmark_receipt,
        config=config,
    )
    if approval.get("resource_benchmark_sha256") != sha256_file(args.benchmark_receipt):
        raise RuntimeError("resource benchmark changed after approval validation")
    ensure_fresh_dir(out)
    write_json(out / "run_config.json", config)
    write_run_provenance(
        out,
        accepted_root=args.accepted_root,
        navigation_audit=args.navigation_audit,
        navigation_npz=args.navigation_npz,
        approval_path=args.approval,
        benchmark_receipt=args.benchmark_receipt,
    )
    write_json(out / "source_support.json", source_support_rows(cohort))
    metrics: list[dict[str, Any]] = []
    operation_counts = {"encoder_fits": 0, "pca_fits": 0, "readout_fits": 0}
    worlds: list[tuple[str, int, Mapping[str, str] | None]] = [("observed", -1, None)]
    for world_index, seed in enumerate(NULL_SEEDS):
        shuffled, info = shuffle_pair_labels_within_session_split(
            cohort.metas, seed=seed
        )
        write_json(out / f"null_{world_index:03d}" / "shuffle_info.json", info)
        worlds.append((f"null_{world_index:03d}", world_index, shuffled))
    for world, world_index, shuffled in worlds:
        for seed in SEEDS:
            check_deadline(deadline)
            seed_dir = out / world / f"seed{seed}"
            seed_dir.mkdir(parents=True, exist_ok=True)
            bundle = fit_feature_bundle(
                cohort=cohort,
                nav=nav,
                world=world,
                world_index=world_index,
                seed=seed,
                outdir=seed_dir,
                shuffled=shuffled,
                device=device,
                deadline=deadline,
                iterations=CEBRA_UPDATES,
                batch_size=args.batch_size,
                hidden=args.hidden,
                lr=args.lr,
            )
            operation_counts["encoder_fits"] += 2
            operation_counts["pca_fits"] += 1
            m_rows, c_rows = fit_all_readouts(
                bundle, seed_dir / "readouts", deadline=deadline
            )
            operation_counts["readout_fits"] += (
                len(REPRESENTATIONS) * len(TARGETS) * len(WINDOWS)
            )
            metrics.extend(m_rows)
            # Keep memory bounded to one seed instead of all 6.7M confusion rows.
            write_json(seed_dir / "confusions.json", c_rows)
            write_json(
                seed_dir / "pseudo_train_manifest.json", bundle.train_bundle.manifest
            )
            write_json(
                seed_dir / "pseudo_development_manifest.json",
                bundle.development_bundle.manifest,
            )
            for row in m_rows:
                append_jsonl(out / "metrics.jsonl", row)
            check_output_budget(out)
            print(
                json.dumps(
                    {
                        "completed": f"{world}/seed{seed}",
                        "operation_counts": operation_counts,
                    }
                ),
                flush=True,
            )
    if operation_counts != {
        "encoder_fits": EXPECTED_ENCODER_FITS,
        "pca_fits": EXPECTED_PCA_FITS,
        "readout_fits": EXPECTED_READOUT_FITS,
    }:
        raise RuntimeError(f"incomplete protocol budget: {operation_counts}")
    write_json(out / "paired_comparisons.json", summarize_paired_comparisons(metrics))
    write_json(
        out / "source_deletion_sensitivity.json",
        source_deletion_sensitivity(out, deadline=deadline),
    )
    check_output_budget(out)
    null_families = summarize_null_families(metrics)
    summary = {
        "status": "completed",
        "artifact_summary": artifact_summary,
        "assembly_parity": parity,
        "operation_counts": operation_counts,
        "deadline_seconds": MAX_RUN_SECONDS,
        "device": device,
        "null_families": null_families,
    }
    write_json(out / "summary.json", summary)
    write_hash_manifest(out)
    return summary


def predict_joblib_readout(
    state_dir: Path, X: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    payload = joblib.load(state_dir / "readout_model.joblib")
    scaler = payload["scaler"]
    model = payload["model"]
    classes = np.asarray(payload["classes"], dtype=np.int64)
    prob = model.predict_proba(scaler.transform(X))
    model_classes = np.asarray(model.classes_, dtype=np.int64)
    aligned = align_probabilities(prob, model_classes, classes)
    return classes[aligned.argmax(axis=1)], aligned


def _metric_key(row: Mapping[str, Any]) -> tuple[Any, ...]:
    return (
        row["world"],
        row["seed"],
        row["representation"],
        row["window"],
        row["target"],
        row["split"],
    )


def _confusion_key(row: Mapping[str, Any]) -> tuple[Any, ...]:
    return (
        row["world"],
        row["seed"],
        row["representation"],
        row["window"],
        row["target"],
        row["split"],
        row["true"],
        row["pred"],
    )


def _assert_metric_matches(
    saved: Mapping[str, Any], replayed: Mapping[str, Any]
) -> None:
    for field in ("accuracy", "balanced_accuracy", "macro_f1", "log_loss", "brier"):
        if not math.isclose(
            checked_float(saved[field], f"saved metric {field}"),
            checked_float(replayed[field], f"replayed metric {field}"),
            rel_tol=0,
            abs_tol=1e-9,
        ):
            raise RuntimeError(
                f"metric replay mismatch for {field}: {saved} != {replayed}"
            )


def replay_run(run_dir: Path) -> dict[str, Any]:
    with no_fit_guard():
        hash_status = verify_hash_manifest(run_dir)
        inputs = read_json(run_dir / "run_inputs.json")
        approval_path = Path(inputs["prefit_approval"])
        benchmark_path = Path(inputs["resource_benchmark"])
        if sha256_file(approval_path) != inputs["prefit_approval_sha256"]:
            raise RuntimeError("prefit approval changed since the run")
        if sha256_file(benchmark_path) != inputs["resource_benchmark_sha256"]:
            raise RuntimeError("resource benchmark changed since the run")
        validate_resource_benchmark(benchmark_path)
        if inputs["code_hashes"] != helper_hashes():
            raise RuntimeError(
                "current source code differs from the frozen run snapshot"
            )
        for relative, expected in inputs["code_hashes"].items():
            if sha256_file(safe_child(run_dir / "code_snapshot", relative)) != expected:
                raise RuntimeError(f"run code snapshot mismatch: {relative}")
        accepted_root = Path(inputs["accepted_root"])
        navigation_audit = Path(inputs["navigation_audit"])
        navigation_npz = Path(inputs["navigation_npz"])
        verify_accepted_endpoint_artifacts(accepted_root)
        if (
            sha256_file(accepted_root / "artifact_hashes.json")
            != inputs["accepted_artifact_manifest_sha256"]
        ):
            raise RuntimeError(
                "accepted endpoint artifact manifest changed since the run"
            )
        if sha256_file(navigation_audit) != inputs["navigation_audit_sha256"]:
            raise RuntimeError("navigation audit changed since the run")
        if sha256_file(navigation_npz) != inputs["navigation_npz_sha256"]:
            raise RuntimeError("navigation NPZ changed since the run")
        cohort = load_endpoint_cohort(accepted_root, strict_expected=True)
        nav = load_nav_data(navigation_npz, cohort)
        validate_navigation_audit(navigation_audit, navigation_npz, cohort, nav)
        summary = read_json(run_dir / "summary.json")
        if summary.get("status") != "completed":
            raise RuntimeError("cannot verify incomplete run")
        config = read_json(run_dir / "run_config.json")
        saved_metrics = {
            _metric_key(row): row for row in read_jsonl(run_dir / "metrics.jsonl")
        }
        expected_seeds = {
            run_dir / world / f"seed{seed}"
            for world in ["observed"]
            + [f"null_{i:03d}" for i in range(len(NULL_SEEDS))]
            for seed in SEEDS
        }
        seed_dirs = {path for path in run_dir.glob("*/seed*") if path.is_dir()}
        if seed_dirs != expected_seeds:
            raise RuntimeError(
                "replay world/seed directory set does not match full budget"
            )
        encoder_replays = 0
        readout_replays = 0
        metric_replays = 0
        confusion_replays = 0
        lineage_replays = 0
        for seed_dir in sorted(seed_dirs):
            saved_confusions = {
                _confusion_key(row): row
                for row in read_json(seed_dir / "confusions.json")
            }
            world = seed_dir.parent.name
            seed = checked_int(seed_dir.name.removeprefix("seed"), "seed directory")
            if world == "observed":
                shuffled = None
            else:
                null_index = checked_int(
                    world.removeprefix("null_"), "null world directory"
                )
                if null_index >= len(NULL_SEEDS):
                    raise RuntimeError(f"unexpected null world: {world}")
                shuffled, _ = shuffle_pair_labels_within_session_split(
                    cohort.metas, seed=NULL_SEEDS[null_index]
                )
            expected_train, expected_dev = assemble_world_seed(
                cohort, seed=seed, shuffled=shuffled
            )
            if (
                read_json(seed_dir / "pseudo_train_manifest.json")
                != expected_train.manifest
            ):
                raise RuntimeError(
                    f"training source lineage replay mismatch: {world}/seed{seed}"
                )
            if (
                read_json(seed_dir / "pseudo_development_manifest.json")
                != expected_dev.manifest
            ):
                raise RuntimeError(
                    f"development source lineage replay mismatch: {world}/seed{seed}"
                )
            with np.load(seed_dir / "scaled_cue.npz", allow_pickle=False) as scaled:
                train_scaled = np.asarray(scaled["train"], dtype=np.float32)
                dev_scaled = np.asarray(scaled["development"], dtype=np.float32)
            scaler = load_scaler(seed_dir / "cue_input_scaler.npz")
            pooled_train = expected_train.X_cue.transpose(0, 2, 1).reshape(
                -1, expected_train.X_cue.shape[1]
            )
            scaler_mean = np.mean(pooled_train, axis=0)
            scaler_var = np.var(pooled_train, axis=0)
            scaler_scale = np.sqrt(scaler_var)
            scaler_scale[scaler_scale == 0] = 1.0
            saved_mean = np.asarray(cast(Any, scaler.mean_), dtype=np.float64)
            saved_scale = np.asarray(cast(Any, scaler.scale_), dtype=np.float64)
            np.testing.assert_allclose(saved_mean, scaler_mean, rtol=1e-7, atol=1e-9)
            np.testing.assert_allclose(saved_scale, scaler_scale, rtol=1e-7, atol=1e-9)
            train_scaled_expected = transform_cue(expected_train.X_cue, scaler)
            dev_scaled_expected = transform_cue(expected_dev.X_cue, scaler)
            np.testing.assert_allclose(train_scaled, train_scaled_expected, atol=1e-6)
            np.testing.assert_allclose(dev_scaled, dev_scaled_expected, atol=1e-6)
            with np.load(seed_dir / "pca_state.npz", allow_pickle=False) as pca_file:
                components = np.asarray(pca_file["components"], dtype=np.float64)
                pca_mean = np.asarray(pca_file["mean"], dtype=np.float64)
            pca_train_expected = _pca_replay_features(
                train_scaled, components, pca_mean
            )
            pca_dev_expected = _pca_replay_features(dev_scaled, components, pca_mean)
            rebuilt_bank = build_endpoint_pair_bank(
                expected_train, nav, scaler, cohort.cells
            )
            with np.load(seed_dir / "pair_lineage.npz", allow_pickle=False) as lineage:
                for key, expected in rebuilt_bank.pair_lineage.items():
                    np.testing.assert_array_equal(lineage[key], expected)
            saved_coverage = read_csv(seed_dir / "pair_bank_coverage.csv")
            expected_coverage = [
                {key: str(value) for key, value in row.items()}
                for row in rebuilt_bank.coverage_rows
            ]
            if saved_coverage != expected_coverage:
                raise RuntimeError(
                    f"native-pair coverage replay mismatch: {world}/seed{seed}"
                )
            lineage_replays += 1
            with np.load(
                seed_dir / "features_train.npz", allow_pickle=False
            ) as train_features_file:
                train_features = {
                    key: np.asarray(train_features_file[key])
                    for key in train_features_file.files
                }
            np.testing.assert_array_equal(
                train_features["raw"], flatten_cue(train_scaled)
            )
            np.testing.assert_allclose(
                train_features["pca8"], pca_train_expected, atol=1e-6
            )
            with np.load(
                seed_dir / "features_development.npz", allow_pickle=False
            ) as dev_features_file:
                dev_features = {
                    key: np.asarray(dev_features_file[key])
                    for key in dev_features_file.files
                }
            np.testing.assert_array_equal(dev_features["raw"], flatten_cue(dev_scaled))
            np.testing.assert_allclose(
                dev_features["pca8"], pca_dev_expected, atol=1e-6
            )
            for arm in ("cebra_cue", "cebra_joint"):
                fit_info = read_json(seed_dir / arm / "fit_info.json")
                checkpoint = seed_dir / arm / "checkpoint_final.pth"
                if fit_info.get("checkpoints") != [str(checkpoint)]:
                    raise RuntimeError(
                        f"unexpected saved checkpoint set: {world}/seed{seed}/{arm}"
                    )
                if sha256_file(checkpoint) != fit_info.get("checkpoint_final_sha256"):
                    raise RuntimeError(
                        f"final checkpoint hash mismatch: {world}/seed{seed}/{arm}"
                    )
                if list((seed_dir / arm).glob("checkpoint*.pth")) != [checkpoint]:
                    raise RuntimeError(
                        f"unexpected intermediate checkpoint: {world}/seed{seed}/{arm}"
                    )
                solver = load_encoder_checkpoint(
                    seed_dir / arm / "checkpoint_final.pth",
                    input_dim=train_scaled.shape[1],
                    dim=checked_int(config.get("dim", CEBRA_DIM), "encoder dimension"),
                    hidden=checked_int(config.get("hidden"), "encoder hidden size"),
                    lr=checked_float(config.get("lr"), "encoder learning rate"),
                    device="cpu",
                )
                np.testing.assert_allclose(
                    _embed_cue(solver, train_scaled, device="cpu"),
                    train_features[arm],
                    atol=1e-6,
                )
                np.testing.assert_allclose(
                    _embed_cue(solver, dev_scaled, device="cpu"),
                    dev_features[arm],
                    atol=1e-6,
                )
                encoder_replays += 1
            with np.load(
                seed_dir / "pseudo_targets.npz", allow_pickle=False
            ) as targets_file:
                y_pair_train = np.asarray(targets_file["y_pair_train"], dtype=np.int64)
                y_pair_dev = np.asarray(
                    targets_file["y_pair_development"], dtype=np.int64
                )
            np.testing.assert_array_equal(y_pair_train, expected_train.y_pair)
            np.testing.assert_array_equal(y_pair_dev, expected_dev.y_pair)
            cell_count = train_scaled.shape[1]
            for predictions_path in sorted(
                seed_dir.glob("readouts/*/*/*/readout_predictions.npz")
            ):
                state_dir = predictions_path.parent
                target = state_dir.name
                window = state_dir.parent.name
                representation = state_dir.parent.parent.name
                source_rep = (
                    "raw" if representation == "raw_svd_lda" else representation
                )
                Xtr = extract_window_features(
                    source_rep,
                    train_features[source_rep],
                    window,
                    cell_count=cell_count,
                )
                Xde = extract_window_features(
                    source_rep,
                    dev_features[source_rep],
                    window,
                    cell_count=cell_count,
                )
                ytr = target_labels(y_pair_train, target)
                yde = target_labels(y_pair_dev, target)
                ptr, strn = predict_joblib_readout(state_dir, Xtr)
                pde, sde = predict_joblib_readout(state_dir, Xde)
                with np.load(predictions_path, allow_pickle=False) as saved_pred:
                    np.testing.assert_array_equal(saved_pred["pred_train"], ptr)
                    np.testing.assert_allclose(
                        saved_pred["prob_train"], strn, atol=1e-9
                    )
                    np.testing.assert_array_equal(saved_pred["pred_development"], pde)
                    np.testing.assert_allclose(
                        saved_pred["prob_development"], sde, atol=1e-9
                    )
                classes = target_classes(target)
                prefix = {
                    "world": world,
                    "world_index": -1
                    if world == "observed"
                    else checked_int(
                        world.removeprefix("null_"), "null world directory"
                    ),
                    "seed": seed,
                    "representation": representation,
                    "window": window,
                    "target": target,
                    "feature_dim": Xtr.shape[1],
                }
                for split, y, pred, prob in (
                    ("train", ytr, ptr, strn),
                    ("development", yde, pde, sde),
                ):
                    row = metric_row(
                        y=y,
                        pred=pred,
                        prob=prob,
                        classes=classes,
                        prefix={**prefix, "split": split},
                    )
                    saved = saved_metrics.get(_metric_key(row))
                    if saved is None:
                        raise RuntimeError(
                            f"missing saved metric row for {_metric_key(row)}"
                        )
                    _assert_metric_matches(saved, row)
                    metric_replays += 1
                    for crow in confusion_rows(
                        y=y,
                        pred=pred,
                        classes=classes,
                        prefix={**prefix, "split": split},
                    ):
                        saved_conf = saved_confusions.get(_confusion_key(crow))
                        if (
                            saved_conf is None
                            or saved_conf.get("count") != crow["count"]
                        ):
                            raise RuntimeError(
                                f"confusion replay mismatch for {_confusion_key(crow)}"
                            )
                        confusion_replays += 1
                readout_replays += 1
        expected_confusions = (
            EXPECTED_PCA_FITS
            * len(REPRESENTATIONS)
            * len(WINDOWS)
            * 2
            * sum(len(target_classes(target)) ** 2 for target in TARGETS)
        )
        if (
            encoder_replays != EXPECTED_ENCODER_FITS
            or lineage_replays != EXPECTED_PCA_FITS
            or readout_replays != EXPECTED_READOUT_FITS
            or metric_replays != 2 * EXPECTED_READOUT_FITS
            or len(saved_metrics) != metric_replays
            or confusion_replays != expected_confusions
        ):
            raise RuntimeError(
                "replay counts do not cover the complete declared budget"
            )
        replayed_metrics = list(saved_metrics.values())
        replayed_null_families = summarize_null_families(replayed_metrics)
        if replayed_null_families != summary.get("null_families"):
            raise RuntimeError("null-family summary replay mismatch")
        if summarize_paired_comparisons(replayed_metrics) != read_json(
            run_dir / "paired_comparisons.json"
        ):
            raise RuntimeError("paired-comparison summary replay mismatch")
        replayed_sensitivity = source_deletion_sensitivity(run_dir)
        if replayed_sensitivity != read_json(
            run_dir / "source_deletion_sensitivity.json"
        ):
            raise RuntimeError("source-deletion summary replay mismatch")
    return {
        "status": "passed",
        "hash_manifest": hash_status,
        "fits_blocked": True,
        "encoder_replays": encoder_replays,
        "readout_replays": readout_replays,
        "metric_replays": metric_replays,
        "confusion_replays": confusion_replays,
        "source_lineage_replays": lineage_replays,
    }


def cmd_prepare_nav(args: argparse.Namespace) -> None:
    set_thread_limits()
    cohort = load_endpoint_cohort(args.accepted_root, strict_expected=True)
    verify_observed_assembly_parity(cohort, args.accepted_root)
    print(
        json.dumps(
            extract_training_navigation(cohort=cohort, output_dir=args.output_dir),
            indent=2,
        )
    )


def cmd_run(args: argparse.Namespace) -> None:
    print(json.dumps(run_full_budget(args), indent=2))


def cmd_verify(args: argparse.Namespace) -> None:
    print(json.dumps(replay_run(args.run_dir), indent=2))


def cmd_facts(args: argparse.Namespace) -> None:
    config = {
        "seeds": list(SEEDS),
        "null_seeds": list(NULL_SEEDS),
        "rows_per_pair_train": ROWS_PER_PAIR_TRAIN,
        "rows_per_pair_development": ROWS_PER_PAIR_DEVELOPMENT,
        "updates": CEBRA_UPDATES,
        "device": select_device(args.device),
        "targets": list(TARGETS),
        "windows": list(WINDOWS),
        "representations": list(REPRESENTATIONS),
        "batch_size": args.batch_size,
        "hidden": args.hidden,
        "dim": CEBRA_DIM,
        "lr": args.lr,
    }
    if args.hidden != 32 or args.batch_size != 256 or not math.isclose(args.lr, 3e-4):
        raise RuntimeError("protocol fixes hidden=32, batch_size=256, and lr=3e-4")
    print(
        json.dumps(
            approval_facts(
                accepted_root=args.accepted_root,
                navigation_audit=args.navigation_audit,
                navigation_npz=args.navigation_npz,
                benchmark_receipt=args.benchmark_receipt,
                config=config,
            ),
            indent=2,
        )
    )


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    prep = sub.add_parser("prepare-nav", help="extract training-only navigation cache")
    prep.add_argument("--accepted-root", type=Path, default=ACCEPTED_ENDPOINT_ROOT)
    prep.add_argument("--output-dir", type=Path, required=True)
    prep.set_defaults(func=cmd_prepare_nav)

    run = sub.add_parser("run", help="run the full approved endpoint protocol")
    run.add_argument("--accepted-root", type=Path, default=ACCEPTED_ENDPOINT_ROOT)
    run.add_argument("--navigation-npz", type=Path, required=True)
    run.add_argument("--navigation-audit", type=Path, required=True)
    run.add_argument("--benchmark-receipt", type=Path, required=True)
    run.add_argument("--approval", type=Path, required=True)
    run.add_argument("--output-dir", type=Path, default=OUTPUT_ROOT / "run")
    run.add_argument("--device", choices=("cpu", "cuda"), default="cpu")
    run.add_argument("--batch-size", type=int, default=256)
    run.add_argument("--hidden", type=int, default=32)
    run.add_argument("--lr", type=float, default=3e-4)
    run.set_defaults(func=cmd_run)

    verify = sub.add_parser("verify", help="hash/replay verification with fits blocked")
    verify.add_argument("run_dir", type=Path)
    verify.set_defaults(func=cmd_verify)

    facts = sub.add_parser("approval-facts", help="print hash-bound approval facts")
    facts.add_argument("--accepted-root", type=Path, default=ACCEPTED_ENDPOINT_ROOT)
    facts.add_argument("--navigation-audit", type=Path, required=True)
    facts.add_argument("--navigation-npz", type=Path, required=True)
    facts.add_argument("--benchmark-receipt", type=Path, required=True)
    facts.add_argument("--device", choices=("cpu", "cuda"), default="cpu")
    facts.add_argument("--batch-size", type=int, default=256)
    facts.add_argument("--hidden", type=int, default=32)
    facts.add_argument("--lr", type=float, default=3e-4)
    facts.set_defaults(func=cmd_facts)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> None:
    args = parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
