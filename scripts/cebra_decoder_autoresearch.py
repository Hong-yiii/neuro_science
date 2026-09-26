#!/usr/bin/env python3
"""Bounded frozen-CEBRA decoder readout experiment (2026-09-24).

This runner never fits CEBRA.  It audits saved Track-B embeddings, optionally
fits the predeclared downstream readouts behind an explicit gate, verifies saved
readout artifacts forward-only, and renders compact offline summaries.
"""

from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import html
import json
import math
import os
import platform
import random
import shutil
import subprocess
import sys
import time
import warnings
from collections import Counter, defaultdict
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib
import numpy as np
from scipy.special import expit
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss, roc_auc_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

try:  # Keep old helper imports narrow and main-guard-safe.
    from scripts.place195_v7_v8_neural_experiments import SourceMeta, session_from_cell
except Exception:  # pragma: no cover - source checkout issue, surfaced at runtime.
    SourceMeta = None  # type: ignore[assignment]

    def session_from_cell(cell_id: str) -> str:
        parts = cell_id.split("/")
        return f"{parts[0]}_{parts[1]}"


REPO_ROOT = Path(__file__).resolve().parents[1]
PROTOCOL_PATH = REPO_ROOT / "docs/reports/cebra-decoder-prefit-20260924.md"
TRACK_B_ROOT = (
    REPO_ROOT / "outputs/path-generalization-20260907/results-20260907T081200Z/track_b"
)
SOURCE_TENSOR_PATH = (
    REPO_ROOT
    / "outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/"
    "v7-v8-neural-experiments/primary29_min3train_min1val/bin100ms/source_level_cue_tensors.npz"
)
OWNED_OUTPUT_ROOT = REPO_ROOT / "outputs/cebra-decoder-autoresearch-20260924"
EXPECTED_SOURCE_TENSOR_SHA256 = (
    "688e3b52f69a872c7aec420da99ebb6f0b80464351ded3813b077cd7ed3cf567"
)
TARGET_COMPONENT = "D_N_R_T__N_R_M"
TARGET_ENDPOINT = "4->3"
LABELS = ("absent", "present")
LABEL_TO_INT = {"absent": 0, "present": 1}
INT_TO_LABEL = {0: "absent", 1: "present"}
CEBRA_OBJECTIVES = ("cebra_time", "cebra_behavior")
OBSERVED_FAMILY_ROLE = "crossed_seed_primary"
NULL_FAMILY_ROLE = "family_null"
READOUT_RANDOM_STATE = 0
BOOTSTRAP_SEED = 20260924
BOOTSTRAP_WORLDS = 200
PROB_CLIP = 1e-9
REPLAY_TOLERANCE = 1e-6
NULL_TIE_TOLERANCE = 1e-12
FIT_GATE_FLAG = "I_UNDERSTAND_THIS_RUNS_710_BOUNDED_READOUT_FITS_ZERO_CEBRA_FITS"


RECIPES: tuple[dict[str, Any], ...] = (
    {
        "id": "logistic_scaled_c1",
        "kind": "logistic",
        "C": 1.0,
        "scaled": True,
        "role": "archived_cebra_baseline_or_matched_raw_pca",
    },
    {"id": "logistic_scaled_c01", "kind": "logistic", "C": 0.1, "scaled": True},
    {"id": "logistic_scaled_c001", "kind": "logistic", "C": 0.01, "scaled": True},
    {"id": "logistic_unscaled_c1", "kind": "logistic", "C": 1.0, "scaled": False},
    {"id": "knn_cosine_5", "kind": "knn", "k": 5},
    {"id": "knn_cosine_15", "kind": "knn", "k": 15},
    {"id": "svm_rbf_scaled", "kind": "svm", "scaled": True},
    {"id": "svm_rbf_unscaled", "kind": "svm", "scaled": False},
)
RECIPE_BY_ID = {r["id"]: r for r in RECIPES}
LINEAR_RECIPE_IDS = (
    "logistic_scaled_c1",
    "logistic_scaled_c01",
    "logistic_scaled_c001",
    "logistic_unscaled_c1",
)
NONLINEAR_RECIPE_IDS = (
    "knn_cosine_5",
    "knn_cosine_15",
    "svm_rbf_scaled",
    "svm_rbf_unscaled",
)


@dataclass(frozen=True)
class FeatureSet:
    feature_id: str
    kind: str
    representation: str
    X_train: np.ndarray
    y_train: np.ndarray
    X_validation: np.ndarray
    y_validation: np.ndarray
    validation_weights: np.ndarray
    validation_manifest: list[dict[str, str]]
    metadata: dict[str, Any]


@dataclass(frozen=True)
class PredictionBundle:
    train_score: np.ndarray
    train_prob: np.ndarray | None
    train_pred: np.ndarray
    validation_score: np.ndarray
    validation_prob: np.ndarray | None
    validation_pred: np.ndarray
    state: dict[str, np.ndarray]
    state_meta: dict[str, Any]
    warnings: list[str]
    estimator: Any | None = None


# ---------------------------------------------------------------------------
# Small file/hash helpers


def jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [jsonable(v) for v in value]
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, Path):
        return str(value)
    return value


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(jsonable(payload), indent=2, sort_keys=True) + "\n")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text())


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
                    keys.append(key)
        fieldnames = keys
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fieldnames))
        writer.writeheader()
        for row in rows:
            writer.writerow({k: jsonable(row.get(k, "")) for k in fieldnames})


def csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def append_jsonl(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(jsonable(payload), sort_keys=True) + "\n")


def coerce_scalar(value: Any) -> Any:
    if value in (None, ""):
        return ""
    if isinstance(value, bool):
        return str(value)
    if isinstance(value, (int, np.integer)):
        return int(value)
    if isinstance(value, (float, np.floating)):
        if math.isnan(float(value)):
            return "nan"
        return float(value)
    text = str(value)
    try:
        number = float(text)
    except ValueError:
        return text
    if math.isnan(number):
        return "nan"
    return number


def compare_row_sets(
    label: str,
    expected_rows: Sequence[Mapping[str, Any]],
    saved_rows: Sequence[Mapping[str, Any]],
    *,
    key_fields: Sequence[str],
    tolerance: float = REPLAY_TOLERANCE,
) -> dict[str, Any]:
    def key(row: Mapping[str, Any]) -> tuple[str, ...]:
        return tuple(str(row.get(field, "")) for field in key_fields)

    expected_keys = [key(row) for row in expected_rows]
    saved_keys = [key(row) for row in saved_rows]
    if len(expected_keys) != len(set(expected_keys)):
        dup = [k for k, n in Counter(expected_keys).items() if n > 1][:5]
        raise ValueError(f"{label}: duplicate expected identities {dup}")
    if len(saved_keys) != len(set(saved_keys)):
        dup = [k for k, n in Counter(saved_keys).items() if n > 1][:5]
        raise ValueError(f"{label}: duplicate saved identities {dup}")
    if set(expected_keys) != set(saved_keys):
        missing = sorted(set(expected_keys) - set(saved_keys))[:5]
        extra = sorted(set(saved_keys) - set(expected_keys))[:5]
        raise ValueError(
            f"{label}: row identity mismatch missing={missing} extra={extra}"
        )
    saved_by_key = {key(row): row for row in saved_rows}
    max_diff = 0.0
    for expected in expected_rows:
        saved = saved_by_key[key(expected)]
        for field, expected_value in expected.items():
            if field not in saved:
                if expected_value in (None, ""):
                    continue
                raise ValueError(f"{label}: saved row lacks field {field}")
            ev = coerce_scalar(expected_value)
            sv = coerce_scalar(saved.get(field, ""))
            if isinstance(ev, float) or isinstance(sv, float):
                if ev == "" and sv == "":
                    continue
                diff = abs(float(ev) - float(sv))
                max_diff = max(max_diff, diff)
                if diff > tolerance:
                    raise ValueError(
                        f"{label}: numeric mismatch field={field} key={key(expected)} diff={diff}"
                    )
            else:
                if str(ev) != str(sv):
                    raise ValueError(
                        f"{label}: value mismatch field={field} key={key(expected)} expected={ev!r} saved={sv!r}"
                    )
    return {"rows": len(expected_rows), "max_abs_diff": max_diff}


def apply_baseline_deltas(metric_rows: list[dict[str, Any]]) -> None:
    baseline_by_feature = {
        row["feature_id"]: row
        for row in metric_rows
        if row["split"] == "validation_exact_q"
        and row["recipe_id"] == "logistic_scaled_c1"
    }
    for row in metric_rows:
        if row["split"] != "validation_exact_q":
            continue
        base = baseline_by_feature.get(row["feature_id"])
        if (
            base
            and row.get("balanced_accuracy") is not None
            and base.get("balanced_accuracy") is not None
        ):
            row["delta_ba_vs_logistic_scaled_c1"] = float(
                row["balanced_accuracy"] - base["balanced_accuracy"]
            )
            if row.get("auroc") is not None and base.get("auroc") is not None:
                row["delta_auroc_vs_logistic_scaled_c1"] = float(
                    row["auroc"] - base["auroc"]
                )


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def stable_hash(payload: Any) -> str:
    blob = json.dumps(jsonable(payload), sort_keys=True, separators=(",", ":")).encode(
        "utf-8"
    )
    return hashlib.sha256(blob).hexdigest()


def ndarray_sha256(array: np.ndarray) -> str:
    arr = np.ascontiguousarray(array)
    h = hashlib.sha256()
    h.update(str(arr.shape).encode("utf-8"))
    h.update(str(arr.dtype).encode("utf-8"))
    h.update(arr.view(np.uint8))
    return h.hexdigest()


def require_fresh_path(path: Path) -> None:
    if path.exists():
        raise FileExistsError(f"refusing to overwrite existing path: {path}")


def resolve_owned_output(path: Path, *, allow_tmp: bool = False) -> Path:
    resolved = path.resolve()
    if allow_tmp:
        return resolved
    root = OWNED_OUTPUT_ROOT.resolve()
    if resolved != root and root not in resolved.parents:
        raise ValueError(f"out-of-scope output path {resolved}; expected under {root}")
    return resolved


def git_state() -> dict[str, Any]:
    def run(args: list[str]) -> str:
        try:
            return subprocess.check_output(
                args, cwd=REPO_ROOT, text=True, stderr=subprocess.DEVNULL
            ).strip()
        except Exception as exc:  # pragma: no cover - depends on checkout.
            return f"unavailable: {exc}"

    return {
        "head": run(["git", "rev-parse", "HEAD"]),
        "branch": run(["git", "branch", "--show-current"]),
        "status_short": run(["git", "status", "--short"]),
    }


def runtime_info() -> dict[str, Any]:
    import scipy
    import sklearn

    return {
        "python": sys.version,
        "platform": platform.platform(),
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "sklearn": sklearn.__version__,
        "env_threads": {
            name: os.environ.get(name)
            for name in (
                "OMP_NUM_THREADS",
                "OPENBLAS_NUM_THREADS",
                "MKL_NUM_THREADS",
                "NUMEXPR_NUM_THREADS",
            )
        },
    }


# ---------------------------------------------------------------------------
# Source tensor and manifest reconstruction


def make_source_meta(
    source_ids: Sequence[str],
    sessions: Sequence[str],
    splits: Sequence[str],
    labels: Sequence[str],
) -> list[Any]:
    rows = []
    for sid, sess, split, label in zip(
        source_ids, sessions, splits, labels, strict=True
    ):
        if SourceMeta is None:
            rows.append(
                {
                    "source_trial_id": str(sid),
                    "session_id": str(sess),
                    "split": str(split),
                    "label": str(label),
                }
            )
        else:
            rows.append(SourceMeta(str(sid), str(sess), str(split), str(label)))
    return rows


def meta_get(meta: Any, field: str) -> str:
    if isinstance(meta, dict):
        return str(meta[field])
    return str(getattr(meta, field))


def load_source_tensor(path: Path = SOURCE_TENSOR_PATH) -> dict[str, Any]:
    if sha256_file(path) != EXPECTED_SOURCE_TENSOR_SHA256:
        raise ValueError(f"source tensor hash mismatch: {path}")
    z = np.load(path, allow_pickle=False)
    required = {
        "X_source_cell_bin": ((104, 29, 10), np.float32),
        "exposure_source_bin": ((104, 10), np.float32),
        "observed_source_cell_mask": ((104, 29), np.bool_),
        "source_trial_ids": ((104,), None),
        "source_session_ids": ((104,), None),
        "source_splits": ((104,), None),
        "source_labels": ((104,), None),
        "cell_ids": ((29,), None),
        "bin_width_s": ((1,), np.float32),
    }
    for name, (shape, dtype) in required.items():
        if name not in z.files or z[name].shape != shape:
            raise ValueError(
                f"source tensor schema mismatch for {name}: {z[name].shape if name in z.files else 'missing'}"
            )
        if dtype is not None and z[name].dtype != dtype:
            raise ValueError(
                f"source tensor dtype mismatch for {name}: {z[name].dtype}"
            )
    Xsrc = z["X_source_cell_bin"]
    Msrc = z["observed_source_cell_mask"]
    if not np.all(np.isfinite(Xsrc[Msrc])):
        raise ValueError("source tensor has nonfinite observed values")
    source_ids = [str(x) for x in z["source_trial_ids"]]
    sessions = [str(x) for x in z["source_session_ids"]]
    splits = [str(x) for x in z["source_splits"]]
    labels = [str(x) for x in z["source_labels"]]
    cells = [str(x) for x in z["cell_ids"]]
    metas = make_source_meta(source_ids, sessions, splits, labels)
    return {
        "path": path,
        "sha256": sha256_file(path),
        "npz": z,
        "Xsrc": Xsrc,
        "Msrc": Msrc,
        "source_ids": source_ids,
        "source_index": {sid: i for i, sid in enumerate(source_ids)},
        "sessions": sessions,
        "splits": splits,
        "labels": labels,
        "cell_ids": cells,
        "metas": metas,
    }


def session_cell_index(cell_ids: Sequence[str]) -> dict[str, np.ndarray]:
    grouped: dict[str, list[int]] = defaultdict(list)
    for i, cell in enumerate(cell_ids):
        grouped[session_from_cell(cell)].append(i)
    return {k: np.asarray(v, dtype=int) for k, v in grouped.items()}


def exact_class_weights(y: np.ndarray) -> np.ndarray:
    y = np.asarray(y, dtype=np.int64)
    weights = np.zeros(len(y), dtype=np.float64)
    for label in (0, 1):
        idx = y == label
        if np.any(idx):
            weights[idx] = 0.5 / float(np.sum(idx))
    return weights


def reconstruct_rows_from_manifest(
    *,
    Xsrc: np.ndarray,
    Msrc: np.ndarray,
    source_index: Mapping[str, int],
    cell_ids: Sequence[str],
    manifest: Sequence[Mapping[str, str]],
    row_field: str,
) -> tuple[np.ndarray, np.ndarray, list[dict[str, str]]]:
    sess_cells = session_cell_index(cell_ids)
    groups: dict[tuple[str, int], list[Mapping[str, str]]] = defaultdict(list)
    for row in manifest:
        label = row["label"]
        if label not in LABEL_TO_INT:
            raise ValueError(f"unknown label in manifest: {label}")
        groups[(label, int(row[row_field]))].append(row)
    ordered_keys = []
    for label in LABELS:
        rows = sorted(k[1] for k in groups if k[0] == label)
        ordered_keys.extend((label, row_i) for row_i in rows)
    X = np.empty((len(ordered_keys), len(cell_ids), Xsrc.shape[2]), dtype=np.float32)
    y = np.empty(len(ordered_keys), dtype=np.int64)
    ordered_manifest: list[dict[str, str]] = []
    for out_i, key in enumerate(ordered_keys):
        label, _ = key
        X[out_i, :, :] = np.nan
        y[out_i] = LABEL_TO_INT[label]
        rows = sorted(groups[key], key=lambda r: r["session_id"])
        seen_sessions = set()
        for source_row in rows:
            sess = source_row["session_id"]
            sid = source_row["source_trial_id"]
            if sess in seen_sessions:
                raise ValueError(f"duplicate session {sess} in product row {key}")
            seen_sessions.add(sess)
            if sess not in sess_cells:
                raise ValueError(f"manifest session {sess} has no cells")
            source_i = source_index[sid]
            cidx = sess_cells[sess]
            if not np.all(Msrc[source_i, cidx]):
                raise ValueError(f"source {sid} lacks observed cells for {sess}")
            X[out_i, cidx, :] = Xsrc[source_i, cidx, :]
            ordered_manifest.append(dict(source_row))
        if set(sess_cells) != seen_sessions:
            raise ValueError(
                f"product row {key} missing sessions: {set(sess_cells) - seen_sessions}"
            )
        if np.isnan(X[out_i]).any():
            raise ValueError(f"product row {key} has unavailable cells")
    return X, y, ordered_manifest


def flatten_raw_binned(X3: np.ndarray) -> np.ndarray:
    return np.asarray(
        X3.reshape(X3.shape[0], X3.shape[1] * X3.shape[2]), dtype=np.float32
    )


def standard_scaler_mean_scale(values: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    vals = np.asarray(values, dtype=np.float64)
    mean = vals.mean(axis=0)
    var = vals.var(axis=0)
    scale = np.sqrt(var)
    scale[scale == 0.0] = 1.0
    return mean, scale


def pca8_fit_transform(
    X_train3: np.ndarray, X_validation3: np.ndarray
) -> tuple[np.ndarray, np.ndarray, dict[str, np.ndarray]]:
    obs_train = np.transpose(X_train3, (0, 2, 1)).reshape(
        X_train3.shape[0] * X_train3.shape[2], X_train3.shape[1]
    )
    scaler = StandardScaler().fit(obs_train)
    z_train = scaler.transform(obs_train)
    pca = PCA(n_components=8, svd_solver="full", whiten=False, random_state=0).fit(
        z_train
    )

    def tx(X3: np.ndarray) -> np.ndarray:
        obs = np.transpose(X3, (0, 2, 1)).reshape(
            X3.shape[0] * X3.shape[2], X3.shape[1]
        )
        z = pca.transform(scaler.transform(obs)).reshape(X3.shape[0], X3.shape[2], 8)
        return np.asarray(z.reshape(X3.shape[0], X3.shape[2] * 8), dtype=np.float32)

    state = {
        "mean": np.asarray(scaler.mean_, dtype=np.float64),
        "scale": np.asarray(scaler.scale_, dtype=np.float64),
        "components": np.asarray(pca.components_, dtype=np.float64),
        "pca_mean": np.asarray(pca.mean_, dtype=np.float64),
        "explained_variance_ratio": np.asarray(
            pca.explained_variance_ratio_, dtype=np.float64
        ),
    }
    return tx(X_train3), tx(X_validation3), state


def pca8_transform_from_state(
    X3: np.ndarray, state: Mapping[str, np.ndarray]
) -> np.ndarray:
    obs = np.transpose(X3, (0, 2, 1)).reshape(X3.shape[0] * X3.shape[2], X3.shape[1])
    # Preserve sklearn's float32 transform rounding, without fitting either object.
    scaled = np.asarray(obs, dtype=np.float32).copy()
    scaled -= state["mean"]
    scaled /= state["scale"]
    components = np.asarray(state["components"], dtype=np.float32)
    center = np.asarray(state["pca_mean"], dtype=np.float32)
    z = scaled @ components.T - center @ components.T
    z3 = z.reshape(X3.shape[0], X3.shape[2], 8)
    return np.asarray(z3.reshape(X3.shape[0], X3.shape[2] * 8), dtype=np.float32)


def source_label_shuffle_from_metas(
    metas: Sequence[Any], *, seed: int
) -> tuple[dict[str, str], dict[str, Any]]:
    rng = random.Random(seed)
    grouped: dict[tuple[str, str], list[Any]] = defaultdict(list)
    for meta in metas:
        grouped[(meta_get(meta, "session_id"), meta_get(meta, "split"))].append(meta)
    out: dict[str, str] = {}
    movable = 0
    immovable = 0
    for rows in grouped.values():
        labels = [meta_get(m, "label") for m in rows]
        shuffled = labels[:]
        rng.shuffle(shuffled)
        if len(set(labels)) < 2 or len(rows) < 2 or labels == shuffled:
            immovable += len(rows)
        else:
            movable += len(rows)
        for meta, label in zip(rows, shuffled, strict=True):
            out[meta_get(meta, "source_trial_id")] = label
    total = movable + immovable
    return out, {
        "seed": seed,
        "group_fields": ["session_id", "split"],
        "source_count": total,
        "movable_fraction": movable / total if total else 0.0,
        "immovable_fraction": immovable / total if total else 0.0,
        "shuffled_label_hash": stable_hash(out),
    }


# ---------------------------------------------------------------------------
# Metrics and prediction helpers


def safe_weighted_auc(
    y: np.ndarray, score: np.ndarray, weights: np.ndarray
) -> float | None:
    if len(set(np.asarray(y, dtype=int))) < 2:
        return None
    try:
        return float(roc_auc_score(y, score, sample_weight=weights))
    except ValueError:
        return None


def binary_metrics(
    y_true: np.ndarray,
    *,
    pred: np.ndarray,
    score: np.ndarray,
    weights: np.ndarray | None = None,
    prob: np.ndarray | None = None,
) -> dict[str, Any]:
    y = np.asarray(y_true, dtype=np.int64)
    pred = np.asarray(pred, dtype=np.int64)
    score = np.asarray(score, dtype=np.float64)
    if y.shape != pred.shape or y.shape != score.shape or not len(y):
        raise ValueError("metric vectors must be matching and nonempty")
    if weights is None:
        w = np.full(len(y), 1.0 / len(y), dtype=np.float64)
    else:
        w = np.asarray(weights, dtype=np.float64)
        if (
            w.shape != y.shape
            or np.any(w < 0)
            or not np.isfinite(w).all()
            or w.sum() <= 0
        ):
            raise ValueError("invalid weights")
        w = w / w.sum()
    out: dict[str, Any] = {
        "n": int(len(y)),
        "weight_sum": float(w.sum()),
        "weighted_accuracy": float(np.sum(w * (pred == y))),
        "positive_rate_true_weighted": float(np.sum(w * y)),
        "positive_rate_pred_weighted": float(np.sum(w * pred)),
    }
    recalls: list[float | None] = []
    for label in (0, 1):
        idx = y == label
        denom = float(np.sum(w[idx]))
        recall = (
            float(np.sum(w[idx] * (pred[idx] == y[idx])) / denom) if denom else None
        )
        out[f"recall_{INT_TO_LABEL[label]}"] = recall
        out[f"support_weight_{INT_TO_LABEL[label]}"] = denom
        out[f"support_n_{INT_TO_LABEL[label]}"] = int(np.sum(idx))
        recalls.append(recall)
    if recalls[0] is None or recalls[1] is None:
        out["balanced_accuracy"] = None
        out["ba_minus_chance"] = None
    else:
        ba = 0.5 * (recalls[0] + recalls[1])
        out["balanced_accuracy"] = float(ba)
        out["ba_minus_chance"] = float(ba - 0.5)
    out["auroc"] = safe_weighted_auc(y, score, w)
    if prob is None:
        out["log_loss"] = None
        out["brier"] = None
        out["probability_clipping"] = (
            "not_applicable_svm_margin" if np.any(np.isfinite(score)) else "absent"
        )
    else:
        p = np.asarray(prob, dtype=np.float64)
        if p.shape != y.shape or not np.isfinite(p).all() or np.any((p < 0) | (p > 1)):
            raise ValueError("invalid probabilities")
        pc = np.clip(p, PROB_CLIP, 1 - PROB_CLIP)
        out["log_loss"] = float(
            log_loss(y, np.c_[1 - pc, pc], labels=[0, 1], sample_weight=w)
        )
        out["brier"] = float(np.sum(w * (p - y) ** 2))
        out["probability_clipping"] = (
            f"logloss clipped to [{PROB_CLIP}, {1 - PROB_CLIP}]; brier unclipped"
        )
    return out


def metric_rows_for_bundle(
    feature: FeatureSet, recipe_id: str, bundle: PredictionBundle
) -> list[dict[str, Any]]:
    train_w = exact_class_weights(feature.y_train)
    rows = []
    for split, y, weights, pred, score, prob in (
        (
            "train_sampled",
            feature.y_train,
            train_w,
            bundle.train_pred,
            bundle.train_score,
            bundle.train_prob,
        ),
        (
            "validation_exact_q",
            feature.y_validation,
            feature.validation_weights,
            bundle.validation_pred,
            bundle.validation_score,
            bundle.validation_prob,
        ),
    ):
        row = {
            "feature_id": feature.feature_id,
            "feature_kind": feature.kind,
            "representation": feature.representation,
            "recipe_id": recipe_id,
            "split": split,
            **feature.metadata,
            **binary_metrics(y, pred=pred, score=score, weights=weights, prob=prob),
        }
        rows.append(row)
    if (
        rows[0]["balanced_accuracy"] is not None
        and rows[1]["balanced_accuracy"] is not None
    ):
        rows[1]["train_minus_validation_ba"] = float(
            rows[0]["balanced_accuracy"] - rows[1]["balanced_accuracy"]
        )
    return rows


def logistic_predict_from_state(
    X: np.ndarray, state: Mapping[str, np.ndarray]
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    Z = X
    if "scaler_mean" in state and state["scaler_mean"].size:
        Z = (X - state["scaler_mean"]) / state["scaler_scale"]
    margin = Z @ state["coef"].reshape(-1) + float(state["intercept"].reshape(-1)[0])
    prob = expit(margin)
    pred = (prob >= 0.5).astype(np.int64)
    return margin.astype(np.float64), prob.astype(np.float64), pred


def knn_predict_from_state(
    X: np.ndarray, state: Mapping[str, np.ndarray], k: int
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    train = np.asarray(state["X_train"], dtype=np.float64)
    ytr = np.asarray(state["y_train"], dtype=np.int64)
    query = np.asarray(X, dtype=np.float64)
    train_norm = np.linalg.norm(train, axis=1)
    query_norm = np.linalg.norm(query, axis=1)
    denom = np.outer(query_norm, train_norm)
    sim = np.divide(
        query @ train.T,
        denom,
        out=np.zeros((len(query), len(train)), dtype=np.float64),
        where=denom > 0,
    )
    dist = 1.0 - sim
    idx = np.argsort(dist, axis=1, kind="mergesort")[:, :k]
    votes = ytr[idx]
    prob = votes.mean(axis=1)
    pred = (prob >= 0.5).astype(np.int64)
    return prob.astype(np.float64), prob.astype(np.float64), pred


def svm_predict_from_state(
    X: np.ndarray, state: Mapping[str, np.ndarray]
) -> tuple[np.ndarray, None, np.ndarray]:
    Z = X
    if "scaler_mean" in state and state["scaler_mean"].size:
        Z = (X - state["scaler_mean"]) / state["scaler_scale"]
    sv = np.asarray(state["support_vectors"], dtype=np.float64)
    gamma = float(state["gamma"].reshape(-1)[0])
    z_norm = np.sum(Z * Z, axis=1)[:, None]
    sv_norm = np.sum(sv * sv, axis=1)[None, :]
    sq = np.maximum(z_norm + sv_norm - 2 * (Z @ sv.T), 0.0)
    kernel = np.exp(-gamma * sq)
    margin = kernel @ state["dual_coef"].reshape(-1) + float(
        state["intercept"].reshape(-1)[0]
    )
    pred = (margin >= 0.0).astype(np.int64)
    return margin.astype(np.float64), None, pred


# ---------------------------------------------------------------------------
# Recipe fitting and model persistence


def fit_recipe(
    feature: FeatureSet,
    recipe: Mapping[str, Any],
    *,
    baseline_state: Mapping[str, np.ndarray] | None = None,
) -> PredictionBundle:
    recipe_id = str(recipe["id"])
    warn_rows: list[str] = []
    if baseline_state is not None:
        train_score, train_prob, train_pred = logistic_predict_from_state(
            feature.X_train, baseline_state
        )
        val_score, val_prob, val_pred = logistic_predict_from_state(
            feature.X_validation, baseline_state
        )
        return PredictionBundle(
            train_score=train_score,
            train_prob=train_prob,
            train_pred=train_pred,
            validation_score=val_score,
            validation_prob=val_prob,
            validation_pred=val_pred,
            state={k: np.asarray(v) for k, v in baseline_state.items()},
            state_meta={
                "model_kind": "archived_logistic_forward",
                "fit_counted": False,
                "recipe_id": recipe_id,
            },
            warnings=[],
        )

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        if recipe["kind"] == "logistic":
            Xtr = feature.X_train
            Xva = feature.X_validation
            state: dict[str, np.ndarray] = {}
            if recipe.get("scaled", False):
                scaler = StandardScaler().fit(Xtr)
                Xtr = scaler.transform(Xtr)
                Xva = scaler.transform(Xva)
                state["scaler_mean"] = np.asarray(scaler.mean_, dtype=np.float64)
                state["scaler_scale"] = np.asarray(scaler.scale_, dtype=np.float64)
            clf = LogisticRegression(
                C=float(recipe["C"]),
                solver="liblinear",
                class_weight="balanced",
                max_iter=1000,
                random_state=READOUT_RANDOM_STATE,
            ).fit(Xtr, feature.y_train)
            state["coef"] = np.asarray(clf.coef_, dtype=np.float64)
            state["intercept"] = np.asarray(clf.intercept_, dtype=np.float64)
            train_score, train_prob, train_pred = logistic_predict_from_state(
                feature.X_train, state
            )
            val_score, val_prob, val_pred = logistic_predict_from_state(
                feature.X_validation, state
            )
            meta = {
                "model_kind": "logistic_regression",
                "fit_counted": True,
                "C": float(recipe["C"]),
                "solver": "liblinear",
                "class_weight": "balanced",
                "max_iter": 1000,
                "random_state": READOUT_RANDOM_STATE,
                "scaled": bool(recipe.get("scaled", False)),
                "estimator_params": clf.get_params(deep=True),
            }
        elif recipe["kind"] == "knn":
            k = int(recipe["k"])
            clf = KNeighborsClassifier(
                n_neighbors=k,
                metric="cosine",
                weights="uniform",
                algorithm="brute",
                n_jobs=1,
            ).fit(feature.X_train, feature.y_train)
            train_prob = clf.predict_proba(feature.X_train)[:, 1]
            val_prob = clf.predict_proba(feature.X_validation)[:, 1]
            train_score = train_prob
            val_score = val_prob
            train_pred = clf.predict(feature.X_train)
            val_pred = clf.predict(feature.X_validation)
            state = {
                "X_train_sha256": np.asarray([ndarray_sha256(feature.X_train)]),
                "y_train_sha256": np.asarray(
                    [ndarray_sha256(feature.y_train.astype(np.int64))]
                ),
            }
            meta = {
                "model_kind": "knn_cosine",
                "fit_counted": True,
                "estimator_params": clf.get_params(deep=True),
                "n_neighbors": k,
                "metric": "cosine",
                "weights": "uniform",
                "algorithm": "brute",
                "n_jobs": 1,
                "persistence": "trusted_local_joblib_estimator_hash_checked",
            }
        elif recipe["kind"] == "svm":
            Xtr = feature.X_train
            Xva = feature.X_validation
            state = {}
            if recipe.get("scaled", False):
                scaler = StandardScaler().fit(Xtr)
                Xtr = scaler.transform(Xtr)
                Xva = scaler.transform(Xva)
                state["scaler_mean"] = np.asarray(scaler.mean_, dtype=np.float64)
                state["scaler_scale"] = np.asarray(scaler.scale_, dtype=np.float64)
            clf = SVC(
                C=1.0,
                kernel="rbf",
                gamma="scale",
                probability=False,
                class_weight="balanced",
                tol=0.001,
                max_iter=100000,
                cache_size=200,
            ).fit(Xtr, feature.y_train)
            state.update(
                {
                    "support_vectors": np.asarray(
                        clf.support_vectors_, dtype=np.float64
                    ),
                    "dual_coef": np.asarray(clf.dual_coef_, dtype=np.float64),
                    "intercept": np.asarray(clf.intercept_, dtype=np.float64),
                    "gamma": np.asarray([clf._gamma], dtype=np.float64),
                    "classes": np.asarray(clf.classes_, dtype=np.int64),
                    "n_support": np.asarray(clf.n_support_, dtype=np.int64),
                }
            )
            train_score, _, train_pred = svm_predict_from_state(feature.X_train, state)
            val_score, _, val_pred = svm_predict_from_state(feature.X_validation, state)
            if (
                np.max(np.abs(train_score - clf.decision_function(Xtr)))
                > REPLAY_TOLERANCE
            ):
                raise AssertionError(
                    "manual SVM replay disagrees with sklearn train margins"
                )
            if (
                np.max(np.abs(val_score - clf.decision_function(Xva)))
                > REPLAY_TOLERANCE
            ):
                raise AssertionError(
                    "manual SVM replay disagrees with sklearn validation margins"
                )
            train_prob = None
            val_prob = None
            meta = {
                "model_kind": "svc_rbf",
                "fit_counted": True,
                "C": 1.0,
                "kernel": "rbf",
                "gamma": "scale",
                "probability": False,
                "class_weight": "balanced",
                "tol": 0.001,
                "max_iter": 100000,
                "cache_size": 200,
                "scaled": bool(recipe.get("scaled", False)),
                "estimator_params": clf.get_params(deep=True),
            }
        else:
            raise ValueError(f"unknown recipe kind: {recipe}")
        warn_rows = [f"{w.category.__name__}: {w.message}" for w in caught]
        meta["recipe_id"] = recipe_id
        meta["warnings"] = warn_rows
        return PredictionBundle(
            train_score=np.asarray(train_score, dtype=np.float64),
            train_prob=None
            if train_prob is None
            else np.asarray(train_prob, dtype=np.float64),
            train_pred=np.asarray(train_pred, dtype=np.int64),
            validation_score=np.asarray(val_score, dtype=np.float64),
            validation_prob=None
            if val_prob is None
            else np.asarray(val_prob, dtype=np.float64),
            validation_pred=np.asarray(val_pred, dtype=np.int64),
            state=state,
            state_meta=meta,
            warnings=warn_rows,
            estimator=clf if recipe["kind"] == "knn" else None,
        )


def predict_from_saved_state(
    feature: FeatureSet,
    recipe_id: str,
    state: Mapping[str, np.ndarray],
    meta: Mapping[str, Any],
    estimator: Any | None = None,
) -> PredictionBundle:
    kind = meta["model_kind"]
    if kind in {"archived_logistic_forward", "logistic_regression"}:
        tr_s, tr_p, tr_pred = logistic_predict_from_state(feature.X_train, state)
        va_s, va_p, va_pred = logistic_predict_from_state(feature.X_validation, state)
    elif kind == "knn_cosine":
        if estimator is None:
            raise ValueError(
                "kNN replay requires trusted hash-checked joblib estimator"
            )
        tr_p = estimator.predict_proba(feature.X_train)[:, 1]
        va_p = estimator.predict_proba(feature.X_validation)[:, 1]
        tr_s = tr_p
        va_s = va_p
        tr_pred = estimator.predict(feature.X_train)
        va_pred = estimator.predict(feature.X_validation)
    elif kind == "svc_rbf":
        tr_s, tr_p, tr_pred = svm_predict_from_state(feature.X_train, state)
        va_s, va_p, va_pred = svm_predict_from_state(feature.X_validation, state)
    else:
        raise ValueError(f"unknown saved model kind: {kind}")
    return PredictionBundle(
        train_score=tr_s,
        train_prob=tr_p,
        train_pred=tr_pred,
        validation_score=va_s,
        validation_prob=va_p,
        validation_pred=va_pred,
        state={k: np.asarray(v) for k, v in state.items()},
        state_meta={**dict(meta), "recipe_id": recipe_id},
        warnings=list(meta.get("warnings", [])),
    )


def save_npz_exact(path: Path, **arrays: np.ndarray) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    if "allow_pickle" in arrays:
        raise ValueError("allow_pickle is reserved by numpy.savez_compressed")
    np.savez_compressed(path, **arrays)  # type: ignore[call-arg]
    return sha256_file(path)


# ---------------------------------------------------------------------------
# Audit


def fit_spec_is_observed(spec: Mapping[str, Any]) -> bool:
    return (
        spec.get("family_role") == OBSERVED_FAMILY_ROLE
        and spec.get("objective") in CEBRA_OBJECTIVES
        and spec.get("dim") == 8
        and spec.get("rows_per_class") == 64
        and spec.get("updates") == 1000
        and spec.get("assembly_seed") in range(5)
        and spec.get("optimizer_seed") in range(5)
        and spec.get("permutation_index") is None
    )


def fit_spec_is_null(spec: Mapping[str, Any]) -> bool:
    return (
        spec.get("family_role") == NULL_FAMILY_ROLE
        and spec.get("objective") in CEBRA_OBJECTIVES
        and spec.get("dim") == 8
        and spec.get("rows_per_class") == 64
        and spec.get("updates") == 1000
        and spec.get("assembly_seed") == 0
        and spec.get("optimizer_seed") == 0
        and spec.get("permutation_index") in range(20)
    )


def saved_baseline_state(npz: np.lib.npyio.NpzFile) -> dict[str, np.ndarray]:
    return {
        "scaler_mean": np.asarray(npz["decoder_scaler_mean"], dtype=np.float64),
        "scaler_scale": np.asarray(npz["decoder_scaler_scale"], dtype=np.float64),
        "coef": np.asarray(npz["decoder_coef"], dtype=np.float64),
        "intercept": np.asarray(npz["decoder_intercept"], dtype=np.float64),
    }


def audit_one_fit(fit_info_path: Path, source: Mapping[str, Any]) -> dict[str, Any]:
    info = read_json(fit_info_path)
    spec = info["fit_spec"]
    fit_dir = fit_info_path.parent
    npz_path = fit_dir / "embeddings_predictions_decoder.npz"
    if not npz_path.exists():
        raise FileNotFoundError(npz_path)
    for name, digest in info.get("artifact_sha256", {}).items():
        p = fit_dir / name
        if p.is_file() and sha256_file(p) != digest:
            raise ValueError(f"artifact hash mismatch: {p}")
    z = np.load(npz_path, allow_pickle=False)
    expected_schema = {
        "Z_train": ((128, 80), np.float32),
        "Z_validation": ((30, 80), np.float32),
        "y_train": ((128,), np.int64),
        "y_validation": ((30,), np.int64),
        "validation_weights": ((30,), np.float64),
        "decoder_coef": ((1, 80), np.float64),
        "decoder_intercept": ((1,), np.float64),
        "neural_scaler_mean": ((29,), np.float64),
        "neural_scaler_scale": ((29,), np.float64),
        "decoder_scaler_mean": ((80,), np.float64),
        "decoder_scaler_scale": ((80,), np.float64),
    }
    for name, (shape, dtype) in expected_schema.items():
        if name not in z.files or z[name].shape != shape or z[name].dtype != dtype:
            raise ValueError(
                f"NPZ schema mismatch {fit_dir.name}/{name}: {z[name].shape if name in z.files else 'missing'} {z[name].dtype if name in z.files else ''}"
            )
    if Counter(z["y_train"].tolist()) != {0: 64, 1: 64}:
        raise ValueError(f"train labels mismatch in {fit_dir}")
    if Counter(z["y_validation"].tolist()) != {0: 24, 1: 6}:
        raise ValueError(f"validation labels mismatch in {fit_dir}")
    if not np.allclose(
        z["validation_weights"], exact_class_weights(z["y_validation"]), atol=1e-14
    ):
        raise ValueError(f"validation weights mismatch in {fit_dir}")

    shuffled = None
    shuffle_info = None
    identity = info["fit_identity"]
    if spec.get("permutation_index") is not None:
        seed = int(identity["shuffle"]["seed"])
        shuffled, shuffle_info = source_label_shuffle_from_metas(
            source["metas"], seed=seed
        )
        for key in ("seed", "group_fields", "source_count", "shuffled_label_hash"):
            if shuffle_info[key] != identity["shuffle"][key]:
                raise ValueError(f"null shuffle identity mismatch {fit_dir.name}/{key}")
    gen_manifest = csv_rows(fit_dir / "generated_assembly_manifest.csv")
    train_gen_manifest = [r for r in gen_manifest if r["split"] == "train"]
    eval_manifest = csv_rows(fit_dir / "exact_evaluation_manifest.csv")
    if shuffled:
        for row in gen_manifest + eval_manifest:
            if shuffled[row["source_trial_id"]] != row["label"]:
                raise ValueError(
                    f"shuffled source-label map mismatch in {fit_dir.name}"
                )
    else:
        label_by_source = dict(zip(source["source_ids"], source["labels"], strict=True))
        for row in gen_manifest + eval_manifest:
            if label_by_source[row["source_trial_id"]] != row["label"]:
                raise ValueError(f"source-label map mismatch in {fit_dir.name}")
    Xtr, ytr, ordered_gen = reconstruct_rows_from_manifest(
        Xsrc=source["Xsrc"],
        Msrc=source["Msrc"],
        source_index=source["source_index"],
        cell_ids=source["cell_ids"],
        manifest=train_gen_manifest,
        row_field="pseudo_row",
    )
    Xev, yev, ordered_eval = reconstruct_rows_from_manifest(
        Xsrc=source["Xsrc"],
        Msrc=source["Msrc"],
        source_index=source["source_index"],
        cell_ids=source["cell_ids"],
        manifest=eval_manifest,
        row_field="product_row",
    )
    wev = exact_class_weights(yev)
    checks = {
        "train_array_sha256": ndarray_sha256(Xtr),
        "train_label_sha256": ndarray_sha256(ytr.astype(np.int64)),
        "train_manifest_hash": stable_hash(list(gen_manifest)),
        "eval_array_sha256": ndarray_sha256(Xev),
        "eval_label_weight_hash": stable_hash({"y": yev.tolist(), "w": wev.tolist()}),
        "eval_manifest_hash": stable_hash(list(eval_manifest)),
    }
    for key, value in checks.items():
        if identity.get(key) != value:
            raise ValueError(f"fit identity mismatch {fit_dir.name}/{key}")
    train_ids = {r["source_trial_id"] for r in gen_manifest if r["split"] == "train"}
    val_ids = {r["source_trial_id"] for r in eval_manifest}
    if not train_ids.isdisjoint(val_ids):
        raise ValueError(f"train/exact validation source overlap in {fit_dir}")

    obs_train = np.transpose(Xtr, (0, 2, 1)).reshape(
        Xtr.shape[0] * Xtr.shape[2], Xtr.shape[1]
    )
    mean, scale = standard_scaler_mean_scale(obs_train)
    if np.max(np.abs(mean - z["neural_scaler_mean"])) > REPLAY_TOLERANCE:
        raise ValueError(f"neural scaler mean parity failed in {fit_dir.name}")
    if np.max(np.abs(scale - z["neural_scaler_scale"])) > REPLAY_TOLERANCE:
        raise ValueError(f"neural scaler scale parity failed in {fit_dir.name}")

    state = saved_baseline_state(z)
    tr_s, tr_p, tr_pred = logistic_predict_from_state(z["Z_train"], state)
    va_s, va_p, va_pred = logistic_predict_from_state(z["Z_validation"], state)
    pred_rows = csv_rows(fit_dir / "predictions.csv")
    csv_probs = []
    calc_probs = []
    for row in pred_rows:
        if row["split"] == "train_sampled":
            i = int(row["row"])
            csv_probs.append(float(row["prob_present"]))
            calc_probs.append(float(tr_p[i]))
            if ("present" if tr_pred[i] else "absent") != row["pred_label"]:
                raise ValueError(
                    f"baseline train prediction mismatch in {fit_dir.name}"
                )
        elif row["split"] == "validation_exact_q":
            i = int(row["row"])
            csv_probs.append(float(row["prob_present"]))
            calc_probs.append(float(va_p[i]))
            if ("present" if va_pred[i] else "absent") != row["pred_label"]:
                raise ValueError(
                    f"baseline validation prediction mismatch in {fit_dir.name}"
                )
    max_prob_diff = (
        float(np.max(np.abs(np.asarray(csv_probs) - np.asarray(calc_probs))))
        if csv_probs
        else math.nan
    )
    if max_prob_diff > REPLAY_TOLERANCE:
        raise ValueError(
            f"saved baseline probability replay diff {max_prob_diff} in {fit_dir.name}"
        )

    metric_val = binary_metrics(yev, pred=va_pred, score=va_p, weights=wev, prob=va_p)
    stored_val = next(r for r in info["metrics"] if r["split"] == "validation_exact_q")
    max_metric_diff = max(
        abs(float(stored_val[k]) - float(metric_val[k]))
        for k in ("balanced_accuracy", "log_loss", "brier", "auroc")
        if metric_val[k] is not None
    )
    if max_metric_diff > REPLAY_TOLERANCE:
        raise ValueError(
            f"saved baseline metric replay diff {max_metric_diff} in {fit_dir.name}"
        )

    return {
        "fit_id": fit_dir.name,
        "fit_dir": str(fit_dir),
        "fit_info_path": str(fit_info_path),
        "fit_info_sha256": sha256_file(fit_info_path),
        "npz_sha256": sha256_file(npz_path),
        "generated_manifest_sha256": sha256_file(
            fit_dir / "generated_assembly_manifest.csv"
        ),
        "exact_manifest_sha256": sha256_file(fit_dir / "exact_evaluation_manifest.csv"),
        "fit_identity_hash": info["fit_identity_hash"],
        "fit_spec": spec,
        "is_null": spec.get("permutation_index") is not None,
        "baseline_validation_ba": metric_val["balanced_accuracy"],
        "baseline_validation_auroc": metric_val["auroc"],
        "baseline_max_probability_replay_diff": max_prob_diff,
        "baseline_max_metric_replay_diff": max_metric_diff,
        "train_array_sha256": checks["train_array_sha256"],
        "eval_array_sha256": checks["eval_array_sha256"],
        "train_label_sha256": checks["train_label_sha256"],
        "eval_label_weight_hash": checks["eval_label_weight_hash"],
        "train_manifest_hash": checks["train_manifest_hash"],
        "eval_manifest_hash": checks["eval_manifest_hash"],
        "shuffle": shuffle_info,
        "train_unique_sources": len(train_ids),
        "validation_unique_sources": len(val_ids),
    }


def audit_artifacts(
    output_dir: Path,
    *,
    track_b_root: Path = TRACK_B_ROOT,
    source_tensor: Path = SOURCE_TENSOR_PATH,
    allow_tmp: bool = False,
) -> dict[str, Any]:
    output_dir = resolve_owned_output(output_dir, allow_tmp=allow_tmp)
    require_fresh_path(output_dir)
    output_dir.mkdir(parents=True)
    started = time.time()
    source = load_source_tensor(source_tensor)
    protocol_sha = sha256_file(PROTOCOL_PATH) if PROTOCOL_PATH.exists() else None
    fit_files = sorted((track_b_root / "fits").glob("*/fit_info.json"))
    observed_files = []
    null_files = []
    for f in fit_files:
        spec = read_json(f)["fit_spec"]
        if fit_spec_is_observed(spec):
            observed_files.append(f)
        elif fit_spec_is_null(spec):
            null_files.append(f)
    if len(observed_files) != 50 or len(null_files) != 40:
        raise ValueError(
            f"eligible fit count mismatch: observed={len(observed_files)} null={len(null_files)}"
        )
    entries = [audit_one_fit(f, source) for f in observed_files + null_files]
    observed_entries = [e for e in entries if not e["is_null"]]
    null_entries = [e for e in entries if e["is_null"]]

    # Assembly seed raw parity and saved PCA parity where old artifacts exist.
    raw_pca_audits: list[dict[str, Any]] = []
    by_seed: dict[int, dict[str, Any]] = {}
    for entry in observed_entries:
        seed = int(entry["fit_spec"]["assembly_seed"])
        by_seed.setdefault(seed, entry)
    source_stage = source_tensor.parent
    for seed in range(5):
        entry = by_seed[seed]
        gen_manifest = [
            r
            for r in csv_rows(
                Path(entry["fit_dir"]) / "generated_assembly_manifest.csv"
            )
            if r["split"] == "train"
        ]
        exact_manifest = csv_rows(
            Path(entry["fit_dir"]) / "exact_evaluation_manifest.csv"
        )
        Xtr, ytr, _ = reconstruct_rows_from_manifest(
            Xsrc=source["Xsrc"],
            Msrc=source["Msrc"],
            source_index=source["source_index"],
            cell_ids=source["cell_ids"],
            manifest=gen_manifest,
            row_field="pseudo_row",
        )
        Xev, yev, _ = reconstruct_rows_from_manifest(
            Xsrc=source["Xsrc"],
            Msrc=source["Msrc"],
            source_index=source["source_index"],
            cell_ids=source["cell_ids"],
            manifest=exact_manifest,
            row_field="product_row",
        )
        row = {
            "assembly_seed": seed,
            "train_array_sha256": ndarray_sha256(Xtr),
            "exact_validation_array_sha256": ndarray_sha256(Xev),
            "train_label_sha256": ndarray_sha256(ytr.astype(np.int64)),
            "exact_validation_label_weight_hash": stable_hash(
                {"y": yev.tolist(), "w": exact_class_weights(yev).tolist()}
            ),
            "saved_pseudo_parity": "not_available_for_seed",
            "saved_pca8_parity": "not_available_for_seed",
        }
        pseudo_path = source_stage / f"pseudo_arrays_seed{seed}.npz"
        if pseudo_path.exists():
            pseudo = np.load(pseudo_path, allow_pickle=False)
            row["saved_pseudo_parity"] = bool(
                pseudo["X_train"].dtype == np.float32
                and np.array_equal(pseudo["X_train"], Xtr)
                and np.array_equal(pseudo["y_train"], ytr)
            )
        pca_path = source_stage / f"train_only_pca_seed{seed}.npz"
        if pca_path.exists():
            saved = np.load(pca_path, allow_pickle=False)
            row["saved_pca8_parity"] = "deferred_to_run_gate_no_audit_fit"
            row["saved_pca8_npz_sha256"] = sha256_file(pca_path)
            row["saved_pca8_schema"] = {
                name: {
                    "shape": list(saved[name].shape),
                    "dtype": str(saved[name].dtype),
                }
                for name in saved.files
            }
        raw_pca_audits.append(row)

    manifest = {
        "schema_version": 1,
        "status": "audited",
        "generated_unix_seconds": time.time(),
        "wall_seconds": time.time() - started,
        "protocol_path": str(PROTOCOL_PATH),
        "protocol_sha256": protocol_sha,
        "target_component": TARGET_COMPONENT,
        "target_endpoint": TARGET_ENDPOINT,
        "track_b_root": str(track_b_root),
        "source_tensor": {
            "path": str(source_tensor),
            "sha256": source["sha256"],
            "schema": {
                k: {
                    "shape": list(source["npz"][k].shape),
                    "dtype": str(source["npz"][k].dtype),
                }
                for k in source["npz"].files
            },
            "counts": {
                "sources": len(source["source_ids"]),
                "cells": len(source["cell_ids"]),
                "bins": int(source["Xsrc"].shape[2]),
                "split_label": dict(
                    Counter(
                        f"{split_name}/{label_name}"
                        for split_name, label_name in zip(
                            source["splits"], source["labels"], strict=True
                        )
                    )
                ),
                "mask_observed_cells_per_source": dict(
                    Counter(np.sum(source["Msrc"], axis=1).astype(int).tolist())
                ),
            },
        },
        "eligibility": {
            "observed_cebra_anchors": len(observed_entries),
            "null_cebra_anchors": len(null_entries),
            "objectives": list(CEBRA_OBJECTIVES),
            "assembly_seeds": [0, 1, 2, 3, 4],
            "optimizer_seeds": [0, 1, 2, 3, 4],
            "null_permutations": list(range(20)),
        },
        "readout_budget": {
            "observed_cebra_new_readout_fits": 50 * 7,
            "null_cebra_new_readout_fits": 40 * 7,
            "matched_raw_pca_readout_fits": 10 * 8,
            "new_train_only_pca_fits": 5,
            "saved_baseline_forwards": 90,
            "total_new_readout_fits_ceiling": 710,
            "new_cebra_fits": 0,
        },
        "observed_fits": observed_entries,
        "null_fits": null_entries,
        "raw_pca_audit": raw_pca_audits,
        "runtime": runtime_info(),
        "git": git_state(),
        "code_sha256": sha256_file(Path(__file__)),
    }
    write_json(output_dir / "audit_manifest.json", manifest)
    flat_rows = []
    for e in entries:
        spec = e["fit_spec"]
        flat_rows.append(
            {
                "fit_id": e["fit_id"],
                "fit_dir": e["fit_dir"],
                "is_null": e["is_null"],
                **{f"spec_{k}": v for k, v in spec.items()},
                "npz_sha256": e["npz_sha256"],
                "fit_identity_hash": e["fit_identity_hash"],
                "baseline_validation_ba": e["baseline_validation_ba"],
                "baseline_max_probability_replay_diff": e[
                    "baseline_max_probability_replay_diff"
                ],
            }
        )
    write_csv(output_dir / "fit_manifest.csv", flat_rows)
    write_csv(output_dir / "raw_pca_audit.csv", raw_pca_audits)
    snapshot_dir = output_dir / "source_snapshots"
    snapshot_dir.mkdir()
    shutil.copy2(Path(__file__), snapshot_dir / Path(__file__).name)
    if PROTOCOL_PATH.exists():
        shutil.copy2(PROTOCOL_PATH, snapshot_dir / PROTOCOL_PATH.name)
    return manifest


# ---------------------------------------------------------------------------
# Feature persistence and run


def feature_metadata_base(entry: Mapping[str, Any]) -> dict[str, Any]:
    spec = entry["fit_spec"]
    return {
        "legacy_fit_id": entry["fit_id"],
        "objective": spec["objective"],
        "assembly_seed": spec["assembly_seed"],
        "optimizer_seed": spec["optimizer_seed"],
        "permutation_index": spec.get("permutation_index"),
        "family_role": spec["family_role"],
        "is_null": entry["is_null"],
    }


def save_feature(run_dir: Path, feature: FeatureSet) -> dict[str, Any]:
    path = run_dir / "features" / f"{feature.feature_id}.npz"
    val_sources = validation_source_matrix(feature.validation_manifest)
    if not np.array_equal(
        val_sources["row_labels"], [INT_TO_LABEL[int(y)] for y in feature.y_validation]
    ):
        raise ValueError("validation lineage rows do not align with feature labels")
    digest = save_npz_exact(
        path,
        X_train=np.asarray(feature.X_train),
        y_train=np.asarray(feature.y_train, dtype=np.int64),
        X_validation=np.asarray(feature.X_validation),
        y_validation=np.asarray(feature.y_validation, dtype=np.int64),
        validation_weights=np.asarray(feature.validation_weights, dtype=np.float64),
        validation_source_ids=val_sources["source_ids"],
        validation_session_ids=val_sources["session_ids"],
        validation_row_labels=np.asarray(
            [INT_TO_LABEL[int(v)] for v in feature.y_validation]
        ),
    )
    meta = {
        "feature_id": feature.feature_id,
        "kind": feature.kind,
        "representation": feature.representation,
        "path": str(path.relative_to(run_dir)),
        "sha256": digest,
        "array_hashes": {
            "X_train": ndarray_sha256(feature.X_train),
            "y_train": ndarray_sha256(feature.y_train.astype(np.int64)),
            "X_validation": ndarray_sha256(feature.X_validation),
            "y_validation": ndarray_sha256(feature.y_validation.astype(np.int64)),
            "validation_weights": ndarray_sha256(
                feature.validation_weights.astype(np.float64)
            ),
        },
        **feature.metadata,
    }
    write_json(run_dir / "features" / f"{feature.feature_id}.json", meta)
    return meta


def load_feature(run_dir: Path, feature_meta: Mapping[str, Any]) -> FeatureSet:
    path = run_dir / str(feature_meta["path"])
    if sha256_file(path) != feature_meta["sha256"]:
        raise ValueError(f"feature hash mismatch: {path}")
    z = np.load(path, allow_pickle=False)
    if len(z["validation_source_ids"]) != len(z["y_validation"]):
        raise ValueError(
            "saved validation lineage row count does not match feature rows"
        )
    manifest = manifest_from_validation_source_matrix(
        z["validation_source_ids"],
        z["validation_session_ids"],
        z["validation_row_labels"],
    )
    feature = FeatureSet(
        feature_id=str(feature_meta["feature_id"]),
        kind=str(feature_meta["kind"]),
        representation=str(feature_meta["representation"]),
        X_train=np.asarray(z["X_train"]),
        y_train=np.asarray(z["y_train"], dtype=np.int64),
        X_validation=np.asarray(z["X_validation"]),
        y_validation=np.asarray(z["y_validation"], dtype=np.int64),
        validation_weights=np.asarray(z["validation_weights"], dtype=np.float64),
        validation_manifest=manifest,
        metadata={
            k: v
            for k, v in feature_meta.items()
            if k
            not in {
                "feature_id",
                "kind",
                "representation",
                "path",
                "sha256",
                "array_hashes",
            }
        },
    )
    for name, expected in feature_meta.get("array_hashes", {}).items():
        arr = getattr(feature, name) if hasattr(feature, name) else z[name]
        if ndarray_sha256(np.asarray(arr)) != expected:
            raise ValueError(f"feature array hash mismatch {feature.feature_id}/{name}")
    return feature


def make_cebra_feature(
    entry: Mapping[str, Any],
) -> tuple[FeatureSet, dict[str, np.ndarray]]:
    npz_path = Path(entry["fit_dir"]) / "embeddings_predictions_decoder.npz"
    if sha256_file(npz_path) != entry["npz_sha256"]:
        raise ValueError(f"legacy NPZ hash mismatch: {npz_path}")
    z = np.load(npz_path, allow_pickle=False)
    eval_manifest = csv_rows(Path(entry["fit_dir"]) / "exact_evaluation_manifest.csv")
    meta = feature_metadata_base(entry)
    meta.update({"legacy_npz_sha256": entry["npz_sha256"]})
    feature_id = stable_hash({"kind": "cebra", **meta})[:20]
    baseline_state = saved_baseline_state(z)
    return (
        FeatureSet(
            feature_id=feature_id,
            kind="cebra",
            representation="cebra_dim8_10bins_flat80",
            X_train=np.asarray(z["Z_train"], dtype=np.float32),
            y_train=np.asarray(z["y_train"], dtype=np.int64),
            X_validation=np.asarray(z["Z_validation"], dtype=np.float32),
            y_validation=np.asarray(z["y_validation"], dtype=np.int64),
            validation_weights=np.asarray(z["validation_weights"], dtype=np.float64),
            validation_manifest=eval_manifest,
            metadata=meta,
        ),
        baseline_state,
    )


def raw_pca_features_from_audit(
    audit: Mapping[str, Any], run_dir: Path
) -> tuple[list[FeatureSet], list[dict[str, Any]]]:
    source = load_source_tensor(Path(audit["source_tensor"]["path"]))
    features: list[FeatureSet] = []
    pca_rows: list[dict[str, Any]] = []
    observed_by_seed: dict[int, Mapping[str, Any]] = {}
    for entry in audit["observed_fits"]:
        seed = int(entry["fit_spec"]["assembly_seed"])
        observed_by_seed.setdefault(seed, entry)
    for seed in range(5):
        entry = observed_by_seed[seed]
        gen_manifest = [
            r
            for r in csv_rows(
                Path(entry["fit_dir"]) / "generated_assembly_manifest.csv"
            )
            if r["split"] == "train"
        ]
        eval_manifest = csv_rows(
            Path(entry["fit_dir"]) / "exact_evaluation_manifest.csv"
        )
        Xtr3, ytr, _ = reconstruct_rows_from_manifest(
            Xsrc=source["Xsrc"],
            Msrc=source["Msrc"],
            source_index=source["source_index"],
            cell_ids=source["cell_ids"],
            manifest=gen_manifest,
            row_field="pseudo_row",
        )
        Xev3, yev, ordered_eval = reconstruct_rows_from_manifest(
            Xsrc=source["Xsrc"],
            Msrc=source["Msrc"],
            source_index=source["source_index"],
            cell_ids=source["cell_ids"],
            manifest=eval_manifest,
            row_field="product_row",
        )
        raw_meta = {
            "assembly_seed": seed,
            "is_null": False,
            "source_tensor_sha256": audit["source_tensor"]["sha256"],
            "source_train_array_sha256": ndarray_sha256(Xtr3),
            "source_validation_array_sha256": ndarray_sha256(Xev3),
        }
        raw_id = stable_hash({"kind": "raw", **raw_meta})[:20]
        features.append(
            FeatureSet(
                feature_id=raw_id,
                kind="raw",
                representation="raw_binned_29cells_x_10bins_flat290",
                X_train=flatten_raw_binned(Xtr3),
                y_train=ytr,
                X_validation=flatten_raw_binned(Xev3),
                y_validation=yev,
                validation_weights=exact_class_weights(yev),
                validation_manifest=ordered_eval,
                metadata=raw_meta,
            )
        )
        started = time.time()
        Xp_tr, Xp_ev, pca_state = pca8_fit_transform(Xtr3, Xev3)
        pca_id = stable_hash({"kind": "pca8", **raw_meta})[:20]
        pca_npz = run_dir / "pca_transforms" / f"pca_seed{seed}.npz"
        pca_digest = save_npz_exact(pca_npz, **pca_state)
        pca_rows.append(
            {
                "assembly_seed": seed,
                "pca_transform_id": pca_id,
                "pca_npz": str(pca_npz.relative_to(run_dir)),
                "pca_npz_sha256": pca_digest,
                "fit_counted": True,
                "svd_solver": "full",
                "n_components": 8,
                "whiten": False,
                "wall_seconds": time.time() - started,
                "train_feature_sha256": ndarray_sha256(Xp_tr),
                "validation_feature_sha256": ndarray_sha256(Xp_ev),
            }
        )
        pca_meta = {
            **raw_meta,
            "pca_transform_id": pca_id,
            "pca_npz_sha256": pca_digest,
        }
        features.append(
            FeatureSet(
                feature_id=pca_id,
                kind="pca",
                representation="train_only_cellspace_pca8_per_bin_flat80",
                X_train=Xp_tr,
                y_train=ytr,
                X_validation=Xp_ev,
                y_validation=yev,
                validation_weights=exact_class_weights(yev),
                validation_manifest=ordered_eval,
                metadata=pca_meta,
            )
        )
    return features, pca_rows


def validation_source_matrix(
    manifest: Sequence[Mapping[str, str]],
) -> dict[str, np.ndarray]:
    # product_row is class-local in the archived exact-product manifests.
    by_row: dict[tuple[str, int], list[Mapping[str, str]]] = defaultdict(list)
    for row in manifest:
        if row["label"] not in LABEL_TO_INT:
            raise ValueError(f"unknown validation label: {row['label']}")
        by_row[(row["label"], int(row["product_row"]))].append(row)
    row_ids = sorted(by_row, key=lambda key: (LABEL_TO_INT[key[0]], key[1]))
    sessions = sorted({r["session_id"] for rows in by_row.values() for r in rows})
    source_matrix = np.empty((len(row_ids), len(sessions)), dtype="U64")
    session_matrix = np.empty((len(row_ids), len(sessions)), dtype="U32")
    for i, row_id in enumerate(row_ids):
        rows = {r["session_id"]: r for r in by_row[row_id]}
        if len(rows) != len(by_row[row_id]) or set(rows) != set(sessions):
            raise ValueError(f"duplicate or missing session in validation row {row_id}")
        for j, sess in enumerate(sessions):
            source_matrix[i, j] = rows[sess]["source_trial_id"]
            session_matrix[i, j] = sess
    return {
        "source_ids": source_matrix,
        "session_ids": session_matrix,
        "row_labels": np.asarray([key[0] for key in row_ids]),
    }


def manifest_from_validation_source_matrix(
    source_ids: np.ndarray, session_ids: np.ndarray, labels: np.ndarray
) -> list[dict[str, str]]:
    rows = []
    for i in range(source_ids.shape[0]):
        label = str(labels[i])
        for j in range(source_ids.shape[1]):
            rows.append(
                {
                    "split": "validation",
                    "label": label,
                    "product_row": str(i),
                    "session_id": str(session_ids[i, j]),
                    "source_trial_id": str(source_ids[i, j]),
                }
            )
    return rows


def source_bootstrap_worlds(
    feature: FeatureSet, *, worlds: int = BOOTSTRAP_WORLDS, seed: int = BOOTSTRAP_SEED
) -> list[dict[str, Any]]:
    val_sources = validation_source_matrix(feature.validation_manifest)
    source_ids = val_sources["source_ids"]
    session_ids = val_sources["session_ids"]
    y = feature.y_validation
    pools: dict[tuple[str, int], list[str]] = defaultdict(list)
    for i in range(source_ids.shape[0]):
        for j in range(source_ids.shape[1]):
            pools[(str(session_ids[i, j]), int(y[i]))].append(str(source_ids[i, j]))
    pools = {k: sorted(set(v)) for k, v in pools.items()}
    rng = np.random.default_rng(seed)
    out = []
    for world in range(worlds):
        multiplicities: dict[str, int] = {}
        draws_record: dict[str, list[str]] = {}
        for (sess, label), pool in sorted(pools.items()):
            draws = rng.choice(pool, size=len(pool), replace=True).tolist()
            draws_record[f"{sess}|{INT_TO_LABEL[label]}"] = [str(x) for x in draws]
            counts = Counter(draws)
            for sid in pool:
                multiplicities[sid] = int(counts.get(sid, 0))
        raw_weights = np.zeros(len(y), dtype=np.float64)
        for i in range(len(y)):
            mult = 1
            for sid in source_ids[i]:
                mult *= multiplicities[str(sid)]
            raw_weights[i] = mult
        weights = np.zeros_like(raw_weights)
        for label in (0, 1):
            idx = y == label
            denom = raw_weights[idx].sum()
            if denom > 0:
                weights[idx] = 0.5 * raw_weights[idx] / denom
        out.append(
            {
                "world": world,
                "draws": draws_record,
                "row_weights": weights.tolist(),
                "row_weights_sha256": ndarray_sha256(weights),
                "nonzero_rows": int(np.sum(weights > 0)),
            }
        )
    return out


def metric_rows_with_alternate_weights(
    feature: FeatureSet,
    bundle: PredictionBundle,
    recipe_id: str,
    weights: np.ndarray,
    prefix: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        **prefix,
        "feature_id": feature.feature_id,
        "feature_kind": feature.kind,
        "representation": feature.representation,
        "recipe_id": recipe_id,
        **feature.metadata,
        **binary_metrics(
            feature.y_validation,
            pred=bundle.validation_pred,
            score=bundle.validation_score,
            weights=weights,
            prob=bundle.validation_prob,
        ),
    }


def delete_source_weights(
    feature: FeatureSet, source_id: str
) -> tuple[np.ndarray | None, dict[str, Any]]:
    val_sources = validation_source_matrix(feature.validation_manifest)["source_ids"]
    y = feature.y_validation
    contains = np.any(val_sources == source_id, axis=1)
    retained = ~contains
    weights = np.zeros(len(y), dtype=np.float64)
    summary = {
        "deleted_source_trial_id": source_id,
        "rows_removed": int(np.sum(contains)),
        "rows_retained": int(np.sum(retained)),
        "original_weight_removed": float(np.sum(feature.validation_weights[contains])),
        "removed_absent_rows": int(np.sum(contains & (y == 0))),
        "removed_present_rows": int(np.sum(contains & (y == 1))),
        "inestimable": False,
    }
    for label in (0, 1):
        idx = retained & (y == label)
        if not np.any(idx):
            summary["inestimable"] = True
            return None, summary
        weights[idx] = 0.5 / float(np.sum(idx))
    return weights, summary


def save_model_and_predictions(
    run_dir: Path,
    feature: FeatureSet,
    recipe_id: str,
    bundle: PredictionBundle,
) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    readout_id = stable_hash(
        {"feature_id": feature.feature_id, "recipe_id": recipe_id}
    )[:20]
    model_npz = run_dir / "models" / f"{readout_id}.npz"
    model_digest = save_npz_exact(model_npz, **bundle.state)
    meta = {
        "readout_id": readout_id,
        "feature_id": feature.feature_id,
        "recipe_id": recipe_id,
        "model_npz": str(model_npz.relative_to(run_dir)),
        "model_npz_sha256": model_digest,
        "state_meta": bundle.state_meta,
        "warnings": bundle.warnings,
    }
    if bundle.estimator is not None:
        estimator_path = run_dir / "models" / f"{readout_id}.joblib"
        joblib.dump(bundle.estimator, estimator_path)
        meta["estimator_joblib"] = str(estimator_path.relative_to(run_dir))
        meta["estimator_joblib_sha256"] = sha256_file(estimator_path)
    write_json(run_dir / "models" / f"{readout_id}.json", meta)
    rows = metric_rows_for_bundle(feature, recipe_id, bundle)
    pred_rows: list[dict[str, Any]] = []
    for split, y, weights, pred, score, prob in (
        (
            "train_sampled",
            feature.y_train,
            exact_class_weights(feature.y_train),
            bundle.train_pred,
            bundle.train_score,
            bundle.train_prob,
        ),
        (
            "validation_exact_q",
            feature.y_validation,
            feature.validation_weights,
            bundle.validation_pred,
            bundle.validation_score,
            bundle.validation_prob,
        ),
    ):
        for i in range(len(y)):
            pred_rows.append(
                {
                    "readout_id": readout_id,
                    "feature_id": feature.feature_id,
                    "recipe_id": recipe_id,
                    "split": split,
                    "row": i,
                    "true_label": INT_TO_LABEL[int(y[i])],
                    "pred_label": INT_TO_LABEL[int(pred[i])],
                    "score": float(score[i]),
                    "prob_present": "" if prob is None else float(prob[i]),
                    "evaluation_weight": float(weights[i]),
                }
            )
    return meta, rows, pred_rows


def synthetic_runtime_estimate() -> dict[str, Any]:
    rng = np.random.default_rng(0)
    X = rng.normal(size=(32, 8)).astype(np.float32)
    y = np.asarray([0] * 16 + [1] * 16, dtype=np.int64)
    X[16:, :2] += 1.0
    feature = FeatureSet(
        feature_id="synthetic_estimate",
        kind="synthetic",
        representation="estimate",
        X_train=X,
        y_train=y,
        X_validation=X.copy(),
        y_validation=y.copy(),
        validation_weights=exact_class_weights(y),
        validation_manifest=[],
        metadata={},
    )
    rows = []
    started = time.time()
    for recipe in RECIPES:
        t0 = time.time()
        fit_recipe(feature, recipe)
        rows.append({"recipe_id": recipe["id"], "wall_seconds": time.time() - t0})
    return {"total_wall_seconds": time.time() - started, "recipe_rows": rows}


def validate_audit_for_run(audit_manifest_path: Path, audit: Mapping[str, Any]) -> None:
    current_code_sha = sha256_file(Path(__file__))
    if audit.get("code_sha256") != current_code_sha:
        raise ValueError(
            "audit code_sha256 does not match current evaluator; run a fresh audit"
        )
    audit_dir = audit_manifest_path.parent
    snapshot = audit_dir / "source_snapshots" / Path(__file__).name
    if not snapshot.exists() or sha256_file(snapshot) != current_code_sha:
        raise ValueError(
            "audit source snapshot is missing or does not match current evaluator"
        )
    if (
        sha256_file(audit_manifest_path) == ""
    ):  # impossible, keeps path read explicit for provenance.
        raise AssertionError("unreachable")
    validate_audited_inputs(audit)


def validate_audited_inputs(audit: Mapping[str, Any]) -> None:
    """Check frozen biological inputs independently of the caller's code revision."""
    source_info = audit.get("source_tensor", {})
    if source_info:
        source_path = Path(str(source_info["path"]))
        if sha256_file(source_path) != source_info["sha256"]:
            raise ValueError("audited source tensor hash no longer matches")
    for section in ("observed_fits", "null_fits"):
        for entry in audit.get(section, []):
            checks = (
                ("fit_info_path", "fit_info_sha256"),
                ("fit_dir", "npz_sha256", "embeddings_predictions_decoder.npz"),
                (
                    "fit_dir",
                    "generated_manifest_sha256",
                    "generated_assembly_manifest.csv",
                ),
                ("fit_dir", "exact_manifest_sha256", "exact_evaluation_manifest.csv"),
            )
            for check in checks:
                if len(check) == 2:
                    path = Path(str(entry[check[0]]))
                    expected = entry[check[1]]
                else:
                    path = Path(str(entry[check[0]])) / check[2]
                    expected = entry[check[1]]
                if sha256_file(path) != expected:
                    raise ValueError(f"audited input hash changed: {path}")


def write_incomplete(
    output_dir: Path,
    reason: str,
    started: float,
    ledger_rows: Sequence[Mapping[str, Any]],
    model_metas: Sequence[Mapping[str, Any]],
    metric_rows: Sequence[Mapping[str, Any]],
    prediction_rows: Sequence[Mapping[str, Any]],
) -> None:
    counted = count_fit_ledger(ledger_rows)
    write_json(
        output_dir / "INCOMPLETE.json",
        {
            "status": "incomplete",
            "reason": reason,
            "elapsed": time.time() - started,
            "fit_counts_so_far": counted,
            "models_flushed": len(model_metas),
            "metric_rows_flushed": len(metric_rows),
            "prediction_rows_flushed": len(prediction_rows),
        },
    )


def count_fit_ledger(ledger_rows: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    counted: Counter[str] = Counter(
        {
            "observed_cebra_new_readout_fits": 0,
            "null_cebra_new_readout_fits": 0,
            "matched_raw_pca_readout_fits": 0,
        }
    )
    for row in ledger_rows:
        if int(row["readout_fit_counted"]):
            if row["feature_kind"] == "cebra" and truthy(row.get("is_null")):
                counted["null_cebra_new_readout_fits"] += 1
            elif row["feature_kind"] == "cebra":
                counted["observed_cebra_new_readout_fits"] += 1
            else:
                counted["matched_raw_pca_readout_fits"] += 1
    counted["new_cebra_fits"] = 0
    return dict(counted)


def flush_run_tables(
    output_dir: Path,
    feature_metas: Sequence[Mapping[str, Any]],
    model_metas: Sequence[Mapping[str, Any]],
    metric_rows: Sequence[Mapping[str, Any]],
    prediction_rows: Sequence[Mapping[str, Any]],
    ledger_rows: Sequence[Mapping[str, Any]],
) -> None:
    write_json(output_dir / "feature_manifest.json", {"features": list(feature_metas)})
    write_json(output_dir / "model_manifest.json", {"models": list(model_metas)})
    write_csv(output_dir / "readout_metrics.csv", metric_rows)
    write_csv(output_dir / "readout_predictions.csv", prediction_rows)
    write_csv(output_dir / "fit_ledger.csv", ledger_rows)


def run_readouts(
    audit_manifest_path: Path,
    output_dir: Path,
    *,
    protocol_sha256: str,
    gate: str,
    runtime_cap_seconds: int = 1800,
    allow_tmp: bool = False,
) -> dict[str, Any]:
    if gate != FIT_GATE_FLAG:
        raise PermissionError(f"explicit gate flag mismatch; expected {FIT_GATE_FLAG}")
    output_dir = resolve_owned_output(output_dir, allow_tmp=allow_tmp)
    require_fresh_path(output_dir)
    audit = read_json(audit_manifest_path)
    if audit.get("status") != "audited":
        raise ValueError("audit manifest is not audited")
    current_protocol_sha = (
        sha256_file(PROTOCOL_PATH) if PROTOCOL_PATH.exists() else None
    )
    if (
        protocol_sha256 != audit.get("protocol_sha256")
        or protocol_sha256 != current_protocol_sha
    ):
        raise ValueError(
            "protocol SHA does not match audited and current frozen protocol"
        )
    validate_audit_for_run(audit_manifest_path, audit)
    output_dir.mkdir(parents=True)
    started = time.time()
    write_json(
        output_dir / "run_config.json",
        {
            "status": "running",
            "started_unix_seconds": started,
            "audit_manifest": str(audit_manifest_path),
            "audit_manifest_sha256": sha256_file(audit_manifest_path),
            "protocol_sha256": protocol_sha256,
            "gate_flag": gate,
            "runtime_cap_seconds": runtime_cap_seconds,
            "recipes": RECIPES,
            "bootstrap_worlds": BOOTSTRAP_WORLDS,
            "bootstrap_seed": BOOTSTRAP_SEED,
            "runtime": runtime_info(),
            "git": git_state(),
            "code_sha256": sha256_file(Path(__file__)),
        },
    )
    shutil.copy2(audit_manifest_path, output_dir / "audit_manifest.json")
    snapshot_dir = output_dir / "source_snapshots"
    snapshot_dir.mkdir()
    shutil.copy2(Path(__file__), snapshot_dir / Path(__file__).name)
    if PROTOCOL_PATH.exists():
        shutil.copy2(PROTOCOL_PATH, snapshot_dir / PROTOCOL_PATH.name)

    estimate = synthetic_runtime_estimate()
    write_json(output_dir / "synthetic_runtime_estimate.json", estimate)

    feature_metas: list[dict[str, Any]] = []
    model_metas: list[dict[str, Any]] = []
    metric_rows: list[dict[str, Any]] = []
    prediction_rows: list[dict[str, Any]] = []
    ledger_rows: list[dict[str, Any]] = []
    bundles: dict[tuple[str, str], PredictionBundle] = {}
    features_by_id: dict[str, FeatureSet] = {}

    # CEBRA observed + null features.
    baseline_states: dict[str, dict[str, np.ndarray]] = {}
    for entry in audit["observed_fits"] + audit["null_fits"]:
        feature, baseline = make_cebra_feature(entry)
        features_by_id[feature.feature_id] = feature
        baseline_states[feature.feature_id] = baseline
        feature_metas.append(save_feature(output_dir, feature))
        write_json(output_dir / "feature_manifest.json", {"features": feature_metas})

    # Matched raw/PCA observed features (5 raw + 5 PCA, with 5 PCA fits).
    raw_pca_features, pca_rows = raw_pca_features_from_audit(audit, output_dir)
    for feature in raw_pca_features:
        features_by_id[feature.feature_id] = feature
        feature_metas.append(save_feature(output_dir, feature))
        write_json(output_dir / "feature_manifest.json", {"features": feature_metas})
    write_csv(output_dir / "pca_fit_ledger.csv", pca_rows)

    journal = output_dir / "event_journal.jsonl"
    try:
        for feature in features_by_id.values():
            for recipe in RECIPES:
                recipe_id = str(recipe["id"])
                if time.time() - started > runtime_cap_seconds:
                    write_incomplete(
                        output_dir,
                        "runtime cap exceeded before readout fit",
                        started,
                        ledger_rows,
                        model_metas,
                        metric_rows,
                        prediction_rows,
                    )
                    append_jsonl(
                        journal,
                        {
                            "event": "failed",
                            "reason": "runtime_cap",
                            "feature_id": feature.feature_id,
                            "recipe_id": recipe_id,
                            "unix_seconds": time.time(),
                        },
                    )
                    raise TimeoutError("runtime cap exceeded")
                append_jsonl(
                    journal,
                    {
                        "event": "started",
                        "feature_id": feature.feature_id,
                        "recipe_id": recipe_id,
                        "unix_seconds": time.time(),
                    },
                )
                t0 = time.time()
                try:
                    baseline = (
                        baseline_states.get(feature.feature_id)
                        if feature.kind == "cebra" and recipe_id == "logistic_scaled_c1"
                        else None
                    )
                    bundle = fit_recipe(feature, recipe, baseline_state=baseline)
                    bundles[(feature.feature_id, recipe_id)] = bundle
                    model_meta, rows, preds = save_model_and_predictions(
                        output_dir, feature, recipe_id, bundle
                    )
                    model_metas.append(model_meta)
                    metric_rows.extend(rows)
                    prediction_rows.extend(preds)
                    fit_counted = bool(bundle.state_meta.get("fit_counted", True))
                    ledger_rows.append(
                        {
                            "readout_id": model_meta["readout_id"],
                            "feature_id": feature.feature_id,
                            "feature_kind": feature.kind,
                            "representation": feature.representation,
                            "recipe_id": recipe_id,
                            "readout_fit_counted": int(fit_counted),
                            "cebra_fit_counted": 0,
                            "wall_seconds": time.time() - t0,
                            "warnings": "; ".join(bundle.warnings),
                            **feature.metadata,
                        }
                    )
                    flush_run_tables(
                        output_dir,
                        feature_metas,
                        model_metas,
                        metric_rows,
                        prediction_rows,
                        ledger_rows,
                    )
                    append_jsonl(
                        journal,
                        {
                            "event": "completed",
                            "feature_id": feature.feature_id,
                            "recipe_id": recipe_id,
                            "readout_id": model_meta["readout_id"],
                            "fit_counted": int(fit_counted),
                            "unix_seconds": time.time(),
                        },
                    )
                except Exception as exc:
                    write_incomplete(
                        output_dir,
                        f"readout failed: {exc}",
                        started,
                        ledger_rows,
                        model_metas,
                        metric_rows,
                        prediction_rows,
                    )
                    append_jsonl(
                        journal,
                        {
                            "event": "failed",
                            "feature_id": feature.feature_id,
                            "recipe_id": recipe_id,
                            "error": repr(exc),
                            "unix_seconds": time.time(),
                        },
                    )
                    raise
    except Exception:
        raise

    try:
        return finalize_readouts(
            output_dir,
            audit,
            feature_metas,
            model_metas,
            metric_rows,
            prediction_rows,
            ledger_rows,
            bundles,
            features_by_id,
            pca_rows,
            started,
            runtime_cap_seconds,
        )
    except Exception as exc:
        write_incomplete(
            output_dir,
            f"postprocessing failed: {exc}",
            started,
            ledger_rows,
            model_metas,
            metric_rows,
            prediction_rows,
        )
        append_jsonl(
            journal,
            {
                "event": "postprocessing_failed",
                "error": repr(exc),
                "unix_seconds": time.time(),
            },
        )
        raise


def finalize_readouts(
    output_dir: Path,
    audit: Mapping[str, Any],
    feature_metas: list[dict[str, Any]],
    model_metas: list[dict[str, Any]],
    metric_rows: list[dict[str, Any]],
    prediction_rows: list[dict[str, Any]],
    ledger_rows: list[dict[str, Any]],
    bundles: dict[tuple[str, str], PredictionBundle],
    features_by_id: dict[str, FeatureSet],
    pca_rows: list[dict[str, Any]],
    started: float,
    runtime_cap_seconds: int,
) -> dict[str, Any]:
    """Shared evaluation-only finalization; no model fitting or recipe selection."""
    # Baseline-relative deltas.
    baseline_by_feature = {
        row["feature_id"]: row
        for row in metric_rows
        if row["split"] == "validation_exact_q"
        and row["recipe_id"] == "logistic_scaled_c1"
    }
    for row in metric_rows:
        if row["split"] == "validation_exact_q":
            base = baseline_by_feature.get(row["feature_id"])
            if (
                base
                and row["balanced_accuracy"] is not None
                and base["balanced_accuracy"] is not None
            ):
                row["delta_ba_vs_logistic_scaled_c1"] = float(
                    row["balanced_accuracy"] - base["balanced_accuracy"]
                )
                if row.get("auroc") is not None and base.get("auroc") is not None:
                    row["delta_auroc_vs_logistic_scaled_c1"] = float(
                        row["auroc"] - base["auroc"]
                    )

    # Shared source bootstrap and delete-source sensitivity for observed features only.
    observed_features = [
        f for f in features_by_id.values() if not f.metadata.get("is_null")
    ]
    reference = observed_features[0]
    reference_lineage = validation_source_matrix(reference.validation_manifest)
    for feature in observed_features:
        lineage = validation_source_matrix(feature.validation_manifest)
        if any(
            not np.array_equal(lineage[key], reference_lineage[key])
            for key in reference_lineage
        ):
            raise ValueError(
                "observed representations do not share validation source rows"
            )
    worlds = source_bootstrap_worlds(reference, worlds=BOOTSTRAP_WORLDS)
    write_json(
        output_dir / "source_bootstrap_worlds.json",
        {"seed": BOOTSTRAP_SEED, "worlds": worlds},
    )
    bootstrap_rows: list[dict[str, Any]] = []
    influence_rows: list[dict[str, Any]] = []
    unique_sources = sorted(
        {r["source_trial_id"] for r in reference.validation_manifest}
    )
    for feature in observed_features:
        for recipe in RECIPES:
            recipe_id = str(recipe["id"])
            if time.time() - started > runtime_cap_seconds:
                write_incomplete(
                    output_dir,
                    "runtime cap exceeded before sensitivity",
                    started,
                    ledger_rows,
                    model_metas,
                    metric_rows,
                    prediction_rows,
                )
                raise TimeoutError("runtime cap exceeded during sensitivity")
            bundle = bundles[(feature.feature_id, recipe_id)]
            for world in worlds:
                bootstrap_rows.append(
                    metric_rows_with_alternate_weights(
                        feature,
                        bundle,
                        recipe_id,
                        np.asarray(world["row_weights"], dtype=np.float64),
                        {"world": world["world"], "sensitivity": "source_bootstrap"},
                    )
                )
            for sid in unique_sources:
                if time.time() - started > runtime_cap_seconds:
                    write_incomplete(
                        output_dir,
                        "runtime cap exceeded during delete-source sensitivity",
                        started,
                        ledger_rows,
                        model_metas,
                        metric_rows,
                        prediction_rows,
                    )
                    raise TimeoutError(
                        "runtime cap exceeded during delete-source sensitivity"
                    )
                weights, summary = delete_source_weights(feature, sid)
                prefix = {"sensitivity": "delete_source", **summary}
                if weights is None:
                    influence_rows.append(
                        {
                            **prefix,
                            "feature_id": feature.feature_id,
                            "recipe_id": recipe_id,
                            **feature.metadata,
                        }
                    )
                else:
                    influence_rows.append(
                        metric_rows_with_alternate_weights(
                            feature, bundle, recipe_id, weights, prefix
                        )
                    )
    write_csv(output_dir / "source_bootstrap_metrics.csv", bootstrap_rows)
    write_csv(output_dir / "delete_source_influence.csv", influence_rows)

    null_tail = compute_null_tails(metric_rows)
    decisions = compute_decisions(metric_rows)
    write_json(output_dir / "null_family_tails.json", null_tail)
    write_json(output_dir / "decision_summary.json", decisions)
    write_csv(output_dir / "readout_metrics.csv", metric_rows)
    write_csv(output_dir / "readout_predictions.csv", prediction_rows)
    write_csv(output_dir / "fit_ledger.csv", ledger_rows)
    write_json(output_dir / "feature_manifest.json", {"features": feature_metas})
    write_json(output_dir / "model_manifest.json", {"models": model_metas})

    counted = Counter(count_fit_ledger(ledger_rows))
    counted["new_train_only_pca_fits"] = len(pca_rows)
    counted["new_cebra_fits"] = 0
    summary = {
        "status": "complete",
        "wall_seconds": time.time() - started,
        "feature_count": len(feature_metas),
        "readout_rows": len(ledger_rows),
        "metrics_rows": len(metric_rows),
        "prediction_rows": len(prediction_rows),
        "fit_counts": dict(counted),
        "expected_fit_counts": audit["readout_budget"],
        "null_family_tails": null_tail,
        "decision_summary": decisions,
        "verification_tolerance": REPLAY_TOLERANCE,
    }
    expected_budget = audit["readout_budget"]
    for key in (
        "observed_cebra_new_readout_fits",
        "null_cebra_new_readout_fits",
        "matched_raw_pca_readout_fits",
    ):
        if counted[key] != expected_budget[key]:
            raise RuntimeError(
                f"readout fit count mismatch for {key}: {dict(counted)} expected {expected_budget}"
            )
    write_json(output_dir / "summary.json", summary)
    config = read_json(output_dir / "run_config.json")
    config["status"] = "complete"
    config["completed_unix_seconds"] = time.time()
    write_json(output_dir / "run_config.json", config)
    return summary


def validation_rows(
    metric_rows: Sequence[Mapping[str, Any]],
) -> list[Mapping[str, Any]]:
    return [r for r in metric_rows if r.get("split") == "validation_exact_q"]


def compute_null_tails(metric_rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    rows = validation_rows(metric_rows)
    # A0/O0 observed rows only: assembly0 optimizer0, two objectives, eight recipes.
    observed = [
        r
        for r in rows
        if r.get("feature_kind") == "cebra"
        and not truthy(r.get("is_null"))
        and int(r.get("assembly_seed", -1)) == 0
        and int(r.get("optimizer_seed", -1)) == 0
    ]
    nulls = [
        r for r in rows if r.get("feature_kind") == "cebra" and truthy(r.get("is_null"))
    ]
    per_score = []
    for obs in observed:
        score = float(obs["balanced_accuracy"])
        matches = [
            n
            for n in nulls
            if n.get("objective") == obs.get("objective")
            and n.get("recipe_id") == obs.get("recipe_id")
        ]
        if len(matches) != 20:
            raise ValueError(
                f"null tail requires 20 worlds for {obs.get('objective')} {obs.get('recipe_id')}"
            )
        exceed = sum(
            float(n["balanced_accuracy"]) >= score - NULL_TIE_TOLERANCE for n in matches
        )
        per_score.append(
            {
                "objective": obs.get("objective"),
                "recipe_id": obs.get("recipe_id"),
                "observed_ba": score,
                "exceedances_inclusive": exceed,
                "p_plus_one": (exceed + 1) / 21.0,
            }
        )
    if len(per_score) != 16:
        raise ValueError(
            f"expected 16 observed A0/O0 recipe scores, got {len(per_score)}"
        )
    observed_max = max(float(r["balanced_accuracy"]) - 0.5 for r in observed)
    null_maxima = []
    for perm in range(20):
        world = [n for n in nulls if int(n.get("permutation_index", -1)) == perm]
        if len(world) != 16:
            raise ValueError(
                f"null world {perm} does not have 16 objective×recipe scores"
            )
        null_maxima.append(max(float(n["balanced_accuracy"]) - 0.5 for n in world))
    family_exceed = sum(v >= observed_max - NULL_TIE_TOLERANCE for v in null_maxima)
    return {
        "policy": "one_sided_max_BA_minus_0p5_over_A0O0_two_objectives_eight_readouts_inclusive_plus_one",
        "not_tests": [
            "not_50_seed_mean_p",
            "not_decoder_superiority_p",
            "not_raw_pca_family",
        ],
        "per_fixed_observed_score": per_score,
        "observed_family_max_ba_minus_chance": observed_max,
        "null_family_maxima_ba_minus_chance": null_maxima,
        "family_exceedances_inclusive": family_exceed,
        "family_p_plus_one": (family_exceed + 1) / 21.0,
        "tie_tolerance": NULL_TIE_TOLERANCE,
    }


def compute_decisions(metric_rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    rows = validation_rows(metric_rows)
    decisions = []
    for objective in CEBRA_OBJECTIVES:
        obs = [
            r
            for r in rows
            if r.get("feature_kind") == "cebra"
            and not truthy(r.get("is_null"))
            and r.get("objective") == objective
        ]
        by_recipe: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
        for r in obs:
            by_recipe[str(r["recipe_id"])].append(r)
        linear_means = {
            rid: mean_float([r["balanced_accuracy"] for r in by_recipe[rid]])
            for rid in LINEAR_RECIPE_IDS
            if by_recipe.get(rid)
        }
        linear_envelope = max(linear_means.values()) if linear_means else math.nan
        for rid in NONLINEAR_RECIPE_IDS:
            vals = by_recipe.get(rid, [])
            if not vals:
                continue
            mean_ba = mean_float([r["balanced_accuracy"] for r in vals])
            mean_auc = mean_float([r["auroc"] for r in vals])
            candidate = (
                mean_ba > 0.5 and mean_auc > 0.5 and mean_ba >= linear_envelope + 0.05
            )
            decisions.append(
                {
                    "objective": objective,
                    "recipe_id": rid,
                    "mean_ba": mean_ba,
                    "mean_auroc": mean_auc,
                    "largest_linear_mean_ba": linear_envelope,
                    "descriptive_nonlinear_followup_candidate": bool(candidate),
                    "decision_rule": "mean BA>0.5, mean AUROC>0.5, BA >= largest fixed linear mean BA + 0.05 within objective",
                }
            )
    return {"nonlinear_followup_candidates": decisions}


def mean_float(values: Iterable[Any]) -> float:
    vals = [float(v) for v in values if v not in (None, "")]
    return float(np.mean(vals)) if vals else math.nan


def truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    return str(value).lower() in {"1", "true", "yes"}


# ---------------------------------------------------------------------------
# Verification and report


def load_model(run_dir: Path, model_meta: Mapping[str, Any]) -> dict[str, np.ndarray]:
    path = run_dir / str(model_meta["model_npz"])
    if sha256_file(path) != model_meta["model_npz_sha256"]:
        raise ValueError(f"model hash mismatch: {path}")
    z = np.load(path, allow_pickle=False)
    return {k: np.asarray(z[k]) for k in z.files}


def load_estimator(run_dir: Path, model_meta: Mapping[str, Any]) -> Any | None:
    if "estimator_joblib" not in model_meta:
        return None
    path = run_dir / str(model_meta["estimator_joblib"])
    if sha256_file(path) != model_meta["estimator_joblib_sha256"]:
        raise ValueError(f"estimator hash mismatch: {path}")
    return joblib.load(path)


def verify_run(run_dir: Path, output: Path | None = None) -> dict[str, Any]:
    summary = read_json(run_dir / "summary.json")
    if summary.get("status") != "complete":
        raise ValueError("run is incomplete")
    run_config = read_json(run_dir / "run_config.json")
    run_snapshot = run_dir / "source_snapshots" / Path(__file__).name
    if not run_snapshot.exists() or sha256_file(run_snapshot) != run_config.get(
        "code_sha256"
    ):
        raise ValueError("run source snapshot does not match run_config code hash")
    feature_manifest = read_json(run_dir / "feature_manifest.json")["features"]
    model_manifest = read_json(run_dir / "model_manifest.json")["models"]
    features = {m["feature_id"]: load_feature(run_dir, m) for m in feature_manifest}
    pca_ledger = csv_rows(run_dir / "pca_fit_ledger.csv")
    for row in pca_ledger:
        path = run_dir / row["pca_npz"]
        if sha256_file(path) != row["pca_npz_sha256"]:
            raise ValueError("PCA state hash mismatch")
        seed = int(row["assembly_seed"])
        raw = next(
            f
            for f in features.values()
            if f.kind == "raw" and int(f.metadata["assembly_seed"]) == seed
        )
        projected = next(
            f
            for f in features.values()
            if f.kind == "pca" and int(f.metadata["assembly_seed"]) == seed
        )
        with np.load(path, allow_pickle=False) as state:
            for split in ("train", "validation"):
                X = getattr(raw, f"X_{split}")
                X3 = X.reshape(len(X), 29, 10)
                replay = pca8_transform_from_state(X3, state)
                expected = getattr(projected, f"X_{split}")
                if not np.allclose(replay, expected, atol=REPLAY_TOLERANCE, rtol=0):
                    raise ValueError(f"PCA forward replay mismatch seed{seed}/{split}")
    metric_rows = csv_rows(run_dir / "readout_metrics.csv")
    prediction_rows = csv_rows(run_dir / "readout_predictions.csv")
    recomputed_metrics: list[dict[str, Any]] = []
    recomputed_predictions: list[dict[str, Any]] = []
    max_metric_diff = 0.0
    max_probability_diff = 0.0
    max_score_diff = 0.0
    original_metric_key = {
        (r["feature_id"], r["recipe_id"], r["split"]): r for r in metric_rows
    }
    original_pred_key = {
        (r["readout_id"], r["split"], int(r["row"])): r for r in prediction_rows
    }
    replayed_bundles: dict[tuple[str, str], PredictionBundle] = {}
    for model_meta in model_manifest:
        feature = features[model_meta["feature_id"]]
        state = load_model(run_dir, model_meta)
        estimator = load_estimator(run_dir, model_meta)
        recipe_id = str(model_meta["recipe_id"])
        bundle = predict_from_saved_state(
            feature, recipe_id, state, model_meta["state_meta"], estimator
        )
        replayed_bundles[(feature.feature_id, recipe_id)] = bundle
        rows = metric_rows_for_bundle(feature, recipe_id, bundle)
        readout_id = model_meta["readout_id"]
        for row in rows:
            key = (row["feature_id"], row["recipe_id"], row["split"])
            old = original_metric_key[key]
            for name in (
                "balanced_accuracy",
                "auroc",
                "log_loss",
                "brier",
                "positive_rate_pred_weighted",
                "weighted_accuracy",
            ):
                if row.get(name) in (None, "") and old.get(name) in (None, ""):
                    continue
                if row.get(name) in (None, "") or old.get(name) in (None, ""):
                    raise ValueError(f"metric null mismatch {key}/{name}")
                diff = abs(float(row[name]) - float(old[name]))
                max_metric_diff = max(max_metric_diff, diff)
                if diff > REPLAY_TOLERANCE:
                    raise ValueError(f"metric mismatch {key}/{name}: {diff}")
            recomputed_metrics.append(row)
        for split, y, _weights, pred, score, prob in (
            (
                "train_sampled",
                feature.y_train,
                exact_class_weights(feature.y_train),
                bundle.train_pred,
                bundle.train_score,
                bundle.train_prob,
            ),
            (
                "validation_exact_q",
                feature.y_validation,
                feature.validation_weights,
                bundle.validation_pred,
                bundle.validation_score,
                bundle.validation_prob,
            ),
        ):
            for i in range(len(y)):
                old = original_pred_key[(readout_id, split, i)]
                if (
                    old["pred_label"] != INT_TO_LABEL[int(pred[i])]
                    or old["true_label"] != INT_TO_LABEL[int(y[i])]
                ):
                    raise ValueError(
                        f"prediction label mismatch {readout_id}/{split}/{i}"
                    )
                score_diff = abs(float(old["score"]) - float(score[i]))
                max_score_diff = max(max_score_diff, score_diff)
                if score_diff > REPLAY_TOLERANCE:
                    raise ValueError(
                        f"prediction score mismatch {readout_id}/{split}/{i}: {score_diff}"
                    )
                if prob is not None:
                    prob_diff = abs(float(old["prob_present"]) - float(prob[i]))
                    max_probability_diff = max(max_probability_diff, prob_diff)
                    if prob_diff > REPLAY_TOLERANCE:
                        raise ValueError(
                            f"prediction probability mismatch {readout_id}/{split}/{i}: {prob_diff}"
                        )
                elif old["prob_present"] != "":
                    raise ValueError(
                        f"SVM probability should be absent {readout_id}/{split}/{i}"
                    )
                recomputed_predictions.append(
                    {
                        "readout_id": readout_id,
                        "feature_id": feature.feature_id,
                        "recipe_id": recipe_id,
                        "split": split,
                        "row": i,
                        "true_label": INT_TO_LABEL[int(y[i])],
                        "pred_label": INT_TO_LABEL[int(pred[i])],
                        "score": float(score[i]),
                        "prob_present": "" if prob is None else float(prob[i]),
                        "evaluation_weight": float(_weights[i]),
                    }
                )

    apply_baseline_deltas(recomputed_metrics)
    metric_compare = compare_row_sets(
        "readout_metrics",
        recomputed_metrics,
        metric_rows,
        key_fields=("feature_id", "recipe_id", "split"),
    )
    prediction_compare = compare_row_sets(
        "readout_predictions",
        recomputed_predictions,
        prediction_rows,
        key_fields=("readout_id", "split", "row"),
    )

    recomputed_null = compute_null_tails(recomputed_metrics)
    saved_null = read_json(run_dir / "null_family_tails.json")
    if stable_hash(recomputed_null) != stable_hash(saved_null):
        raise ValueError("null family tails do not replay")
    recomputed_decisions = compute_decisions(recomputed_metrics)
    saved_decisions = read_json(run_dir / "decision_summary.json")
    if stable_hash(recomputed_decisions) != stable_hash(saved_decisions):
        raise ValueError("decision summary does not replay")
    if stable_hash(summary.get("null_family_tails")) != stable_hash(recomputed_null):
        raise ValueError("summary embedded null family tails do not replay")
    if stable_hash(summary.get("decision_summary")) != stable_hash(
        recomputed_decisions
    ):
        raise ValueError("summary embedded decision summary does not replay")

    worlds = read_json(run_dir / "source_bootstrap_worlds.json")["worlds"]
    ref_feature = next(f for f in features.values() if not f.metadata.get("is_null"))
    regenerated = source_bootstrap_worlds(ref_feature, worlds=len(worlds))
    if stable_hash(worlds) != stable_hash(regenerated):
        raise ValueError("source bootstrap worlds do not replay from lineage")
    observed_features = [
        f for f in features.values() if not truthy(f.metadata.get("is_null"))
    ]
    unique_sources = sorted(
        {r["source_trial_id"] for r in ref_feature.validation_manifest}
    )
    expected_bootstrap_rows: list[dict[str, Any]] = []
    expected_influence_rows: list[dict[str, Any]] = []
    for feature in observed_features:
        for recipe in RECIPES:
            recipe_id = str(recipe["id"])
            bundle = replayed_bundles[(feature.feature_id, recipe_id)]
            for world in worlds:
                weights = np.asarray(world["row_weights"], dtype=np.float64)
                if ndarray_sha256(weights) != world["row_weights_sha256"]:
                    raise ValueError("bootstrap world row weight hash mismatch")
                expected_bootstrap_rows.append(
                    metric_rows_with_alternate_weights(
                        feature,
                        bundle,
                        recipe_id,
                        weights,
                        {"world": world["world"], "sensitivity": "source_bootstrap"},
                    )
                )
            for sid in unique_sources:
                weights, delete_summary = delete_source_weights(feature, sid)
                prefix = {"sensitivity": "delete_source", **delete_summary}
                if weights is None:
                    expected_influence_rows.append(
                        {
                            **prefix,
                            "feature_id": feature.feature_id,
                            "recipe_id": recipe_id,
                            **feature.metadata,
                        }
                    )
                else:
                    expected_influence_rows.append(
                        metric_rows_with_alternate_weights(
                            feature, bundle, recipe_id, weights, prefix
                        )
                    )
    bootstrap_compare = compare_row_sets(
        "source_bootstrap_metrics",
        expected_bootstrap_rows,
        csv_rows(run_dir / "source_bootstrap_metrics.csv"),
        key_fields=("sensitivity", "world", "feature_id", "recipe_id"),
    )
    influence_compare = compare_row_sets(
        "delete_source_influence",
        expected_influence_rows,
        csv_rows(run_dir / "delete_source_influence.csv"),
        key_fields=(
            "sensitivity",
            "deleted_source_trial_id",
            "feature_id",
            "recipe_id",
        ),
    )

    ledger = csv_rows(run_dir / "fit_ledger.csv")
    counts = Counter(count_fit_ledger(ledger))
    counts["new_train_only_pca_fits"] = len(csv_rows(run_dir / "pca_fit_ledger.csv"))
    counts["new_cebra_fits"] = 0
    if dict(counts) != summary["fit_counts"]:
        raise ValueError("fit ledger counts do not match summary")
    receipt = {
        "status": "verified",
        "run_dir": str(run_dir),
        "verified_unix_seconds": time.time(),
        "features": len(features),
        "models": len(model_manifest),
        "metric_rows_recomputed": len(recomputed_metrics),
        "prediction_rows_recomputed": len(recomputed_predictions),
        "max_metric_abs_diff": max_metric_diff,
        "max_probability_abs_diff": max_probability_diff,
        "max_score_abs_diff": max_score_diff,
        "rowset_replay": {
            "metrics": metric_compare,
            "predictions": prediction_compare,
            "source_bootstrap": bootstrap_compare,
            "delete_source": influence_compare,
        },
        "fit_counts": dict(counts),
        "null_family_tails": recomputed_null,
        "decision_summary": recomputed_decisions,
        "new_fits_during_verify": 0,
        "pca_transforms_replayed": len(pca_ledger),
        "report_input_hashes": {
            name: sha256_file(run_dir / name)
            for name in (
                "summary.json",
                "readout_metrics.csv",
                "null_family_tails.json",
                "decision_summary.json",
                "source_bootstrap_metrics.csv",
                "delete_source_influence.csv",
                "fit_ledger.csv",
            )
        },
        "tolerance": REPLAY_TOLERANCE,
    }
    if output is not None:
        require_fresh_path(output)
        write_json(output, receipt)
    return receipt


def render_report(
    run_dir: Path,
    output_dir: Path,
    *,
    verify_receipt: Path | None = None,
    allow_tmp: bool = False,
) -> dict[str, Any]:
    output_dir = resolve_owned_output(output_dir, allow_tmp=allow_tmp)
    require_fresh_path(output_dir)
    output_dir.mkdir(parents=True)
    if verify_receipt is None:
        receipt = verify_run(run_dir)
    else:
        receipt = read_json(verify_receipt)
        if (
            receipt.get("status") != "verified"
            or Path(receipt["run_dir"]).resolve() != run_dir.resolve()
        ):
            raise ValueError("verify receipt is not for this verified run")
        if not receipt.get("report_input_hashes"):
            raise ValueError("verification receipt lacks report input hashes")
        for name, digest in receipt["report_input_hashes"].items():
            if sha256_file(run_dir / name) != digest:
                raise ValueError(f"report input changed after verification: {name}")
    metrics = csv_rows(run_dir / "readout_metrics.csv")
    val = [
        r
        for r in metrics
        if r["split"] == "validation_exact_q"
        and r["feature_kind"] == "cebra"
        and r.get("is_null") in {"False", "false", "", False}
    ]
    summary = read_json(run_dir / "summary.json")
    nulls = read_json(run_dir / "null_family_tails.json")
    decisions = read_json(run_dir / "decision_summary.json")

    # Compact figure: observed CEBRA validation BA means by recipe/objective.
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        recipes = [r["id"] for r in RECIPES]
        x = np.arange(len(recipes))
        width = 0.38
        fig, ax = plt.subplots(figsize=(11, 4))
        for offset, objective in [
            (-width / 2, "cebra_time"),
            (width / 2, "cebra_behavior"),
        ]:
            means = [
                mean_float(
                    [
                        r["balanced_accuracy"]
                        for r in val
                        if r["objective"] == objective and r["recipe_id"] == rid
                    ]
                )
                for rid in recipes
            ]
            ax.bar(x + offset, means, width=width, label=objective)
        ax.axhline(0.5, color="black", linewidth=1, linestyle="--")
        ax.set_ylabel("Validation balanced accuracy")
        ax.set_xticks(x)
        ax.set_xticklabels(recipes, rotation=35, ha="right")
        ax.legend()
        fig.tight_layout()
        fig.savefig(output_dir / "observed_cebra_ba_by_recipe.png", dpi=140)
        plt.close(fig)
    except Exception as exc:  # pragma: no cover - plotting optional in minimal env.
        (output_dir / "figure_warning.txt").write_text(str(exc))

    # Summarize every observed recipe; shuffled controls are never leaderboard rows.
    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in metrics:
        if row["split"] == "validation_exact_q" and not truthy(row.get("is_null")):
            representation = (
                row["objective"]
                if row["feature_kind"] == "cebra"
                else row["feature_kind"]
            )
            groups[(representation, row["recipe_id"])].append(row)
    aggregate_rows = []
    for (representation, recipe), rows in sorted(groups.items()):
        result: dict[str, Any] = {
            "representation": representation,
            "recipe_id": recipe,
            "n_frozen_runs": len(rows),
        }
        for key in (
            "balanced_accuracy",
            "auroc",
            "delta_ba_vs_logistic_scaled_c1",
            "log_loss",
            "brier",
        ):
            values = [float(row[key]) for row in rows if row.get(key) not in (None, "")]
            result[key] = float(np.mean(values)) if values else None
        result["ba_min"] = min(float(row["balanced_accuracy"]) for row in rows)
        result["ba_max"] = max(float(row["balanced_accuracy"]) for row in rows)
        aggregate_rows.append(result)
    write_csv(output_dir / "all_observed_recipe_means.csv", aggregate_rows)
    figure_path = output_dir / "observed_cebra_ba_by_recipe.png"
    figure_html = (
        (
            "<img alt='All observed CEBRA decoder means; chance 50 percent' style='max-width:100%' src='data:image/png;base64,"
            + base64.b64encode(figure_path.read_bytes()).decode("ascii")
            + "'>"
        )
        if figure_path.exists()
        else "<p>Figure unavailable; see tables.</p>"
    )
    machine = {
        "status": "reported",
        "run_summary": summary,
        "verify_receipt": receipt,
        "null_family_tails": nulls,
        "decision_summary": decisions,
        "all_observed_recipe_means": aggregate_rows,
        "all_observed_recipe_means_csv": "all_observed_recipe_means.csv",
        "figure": "observed_cebra_ba_by_recipe.png",
    }
    write_json(output_dir / "machine_summary.json", machine)
    html_rows = "\n".join(
        "<tr>"
        + "".join(
            f"<td>{html.escape(str(row.get(col, '')))}</td>"
            for col in (
                "representation",
                "recipe_id",
                "n_frozen_runs",
                "balanced_accuracy",
                "auroc",
                "delta_ba_vs_logistic_scaled_c1",
                "log_loss",
                "brier",
            )
        )
        + "</tr>"
        for row in aggregate_rows
    )
    page = f"""<!doctype html>
<html><head><meta charset='utf-8'><title>CEBRA decoder readout summary</title>
<style>body{{font-family:system-ui,sans-serif;max-width:1100px;margin:2rem auto;line-height:1.35}}table{{border-collapse:collapse;font-size:12px}}td,th{{border:1px solid #ccc;padding:4px 6px}}code{{background:#eee;padding:1px 3px}}</style></head>
<body>
<h1>Frozen CEBRA decoder readout summary</h1>
<p>Status: <b>{html.escape(summary["status"])}</b>; verification: <b>{html.escape(receipt["status"])}</b>; new CEBRA fits: <b>0</b>.</p>
<p>Fit counts: <code>{html.escape(json.dumps(summary["fit_counts"], sort_keys=True))}</code></p>
<p>Null family p+1: <b>{nulls["family_p_plus_one"]:.6g}</b> ({nulls["family_exceedances_inclusive"]} inclusive exceedances / 20 null worlds).</p>
<p><b>Exploratory, exposed development data.</b> Fixed endpoint 4→3, interior component D_N_R_T__N_R_M; 82 training and22 validation source trials. The30 exact combinations are not30 independent trials. CEBRA seed counts and raw/PCA assembly counts are not biological replication.</p>
<p>The null reference concerns only observed A0/O0 versus20 matched null worlds; it is neither a decoder-superiority test nor a p-value for the25-seed means below. SVM margins are not probabilities; its loss/Brier are absent. All eight recipes are reported, not only the highest-scoring seed.</p>
{figure_html}
<h2>All observed recipes: means over fixed runs</h2>
<table><thead><tr><th>Representation</th><th>Recipe</th><th>Runs</th><th>BA</th><th>AUROC</th><th>ΔBA</th><th>Log loss</th><th>Brier</th></tr></thead><tbody>{html_rows}</tbody></table>
<p>Machine-readable summary: <code>machine_summary.json</code>. Parent supplies the main human scientific report.</p>
</body></html>"""
    (output_dir / "summary.html").write_text(page, encoding="utf-8")
    return machine


# ---------------------------------------------------------------------------
# CLI


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_audit = sub.add_parser(
        "audit", help="read-only audit of frozen Track-B artifacts"
    )
    p_audit.add_argument("--output-dir", type=Path, required=True)
    p_audit.add_argument("--track-b-root", type=Path, default=TRACK_B_ROOT)
    p_audit.add_argument("--source-tensor", type=Path, default=SOURCE_TENSOR_PATH)

    p_run = sub.add_parser(
        "run", help="fit bounded downstream readouts; no CEBRA fitting"
    )
    p_run.add_argument("--audit-manifest", type=Path, required=True)
    p_run.add_argument("--output-dir", type=Path, required=True)
    p_run.add_argument("--protocol-sha256", required=True)
    p_run.add_argument("--gate", required=True, help=f"must equal {FIT_GATE_FLAG}")
    p_run.add_argument("--runtime-cap-seconds", type=int, default=1800)

    p_verify = sub.add_parser("verify", help="forward-only replay verification")
    p_verify.add_argument("--run-dir", type=Path, required=True)
    p_verify.add_argument("--output", type=Path, required=True)

    p_report = sub.add_parser(
        "report", help="render compact offline HTML/tables from verified results"
    )
    p_report.add_argument("--run-dir", type=Path, required=True)
    p_report.add_argument("--output-dir", type=Path, required=True)
    p_report.add_argument("--verify-receipt", type=Path)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> None:
    args = parse_args(argv)
    if args.cmd == "audit":
        out = audit_artifacts(
            args.output_dir,
            track_b_root=args.track_b_root,
            source_tensor=args.source_tensor,
        )
        print(
            json.dumps(
                {
                    "status": out["status"],
                    "output": str(args.output_dir),
                    "observed": out["eligibility"]["observed_cebra_anchors"],
                    "null": out["eligibility"]["null_cebra_anchors"],
                    "protocol_sha256": out["protocol_sha256"],
                },
                indent=2,
            )
        )
    elif args.cmd == "run":
        out = run_readouts(
            args.audit_manifest,
            args.output_dir,
            protocol_sha256=args.protocol_sha256,
            gate=args.gate,
            runtime_cap_seconds=args.runtime_cap_seconds,
        )
        print(json.dumps(out, indent=2, sort_keys=True))
    elif args.cmd == "verify":
        out = verify_run(args.run_dir, args.output)
        print(json.dumps(out, indent=2, sort_keys=True))
    elif args.cmd == "report":
        out = render_report(
            args.run_dir, args.output_dir, verify_receipt=args.verify_receipt
        )
        print(
            json.dumps(
                {"status": out["status"], "output": str(args.output_dir)}, indent=2
            )
        )
    else:  # pragma: no cover
        raise AssertionError(args.cmd)


if __name__ == "__main__":
    main()
