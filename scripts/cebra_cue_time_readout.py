#!/usr/bin/env python3
# pyright: reportMissingImports=false
"""Frozen CEBRA cue-time readout preparation runner.

This script intentionally does not train encoders. Real single-bin decoder fitting is
blocked unless a hash-bound approval file matches the current protocol/code/input
facts. It reuses the accepted 2026-09-24 full-trial-transfer source lineage,
scalers, PCA states, CEBRA checkpoints and whole-cue decoder states.
"""

from __future__ import annotations

import argparse
import base64
import csv
import gzip
import hashlib
import json
import math
import shutil
import sys
import time
from collections import Counter, defaultdict
from collections.abc import Iterator, Mapping, Sequence
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import torch

from scripts import cebra_full_trial_transfer as ft
from scripts.cebra_latent_atlas import fidelity, spectrum
from scripts.place195_v7_v8_neural_experiments import session_from_cell
from scripts.place195_v8b_v9_cebra import make_solver

CANONICAL_ROOT = ft.CANONICAL_ROOT
ACCEPTED_RUN = ft.OUTPUT_ROOT / "biological-run-20260924T162913Z"
OUTPUT_ROOT = CANONICAL_ROOT / "outputs/cebra-cue-time-readout-20261005"
PREPARATION_ROOT = OUTPUT_ROOT / "preparation"
DOC_DIR = CANONICAL_ROOT / "docs/reports/cebra-cue-time-readout-20261005"
PROTOCOL_PATH = DOC_DIR / "protocol.md"
SOURCE_SUPPORT_PATH = DOC_DIR / "source-support.md"
SCRIPT_PATH = Path(__file__).resolve()

ACCEPTED_EXECUTED_FT_SHA256 = (
    "ad1dc989d65b43bf0bcdd55638f66d1918a6c61654f69eec3e98edabe2e1a4b4"
)
CURRENT_TYPE_ONLY_FT_SHA256 = (
    "5e8065af5cb7f61683a3cc05a4d022f05c79f214afaea093682cafb94695ff5e"
)
PARENT_REVIEW_NOTE = "scientific-preflight-review-run5773a0b1"

WINDOW_BINS = tuple(range(ft.CUE_BINS))
WINDOWS = tuple(f"bin{b:02d}" for b in WINDOW_BINS) + ("wholecue",)
BIN_WINDOWS = tuple(f"bin{b:02d}" for b in WINDOW_BINS)
REPRESENTATIONS = ("raw290", "pca8", "cue_time", "full_time")
CEBRA_REPRESENTATIONS = ("cue_time", "full_time")
DECODERS = ft.DECODERS
CHECKPOINT_STEPS = (250, 500, 750, 1000)
EXPECTED_WORLDS = 21
EXPECTED_NULL_WORLDS = 20
EXPECTED_SEEDS = ft.SEEDS
EXPECTED_NEW_BIN_READOUTS = 4 * 2 * 10 * 3 * 21
EXPECTED_WHOLE_REPLAYS = 4 * 2 * 3 * 21
EXPECTED_TOTAL_METRIC_GROUPS = (EXPECTED_NEW_BIN_READOUTS + EXPECTED_WHOLE_REPLAYS) * 2
RUN_OUTPUT_LIMIT_GIB = 10.0
MAX_RUN_SECONDS = 90 * 60


@dataclass(frozen=True)
class SeedFeatures:
    world: str
    world_index: int
    seed: int
    seed_dir: Path
    train_bundle: ft.RowBundle
    validation_bundle: ft.RowBundle
    features_train: dict[str, np.ndarray]
    features_validation: dict[str, np.ndarray]
    checked_files: list[str]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stable_hash(payload: Any) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text())


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(ft.jsonable(payload), indent=2, sort_keys=True) + "\n")


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
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fieldnames})


def read_csv(path: Path) -> list[dict[str, str]]:
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", newline="") as f:
        return list(csv.DictReader(f))


def append_jsonl(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as f:
        f.write(json.dumps(ft.jsonable(payload), sort_keys=True) + "\n")


def ensure_fresh_dir(path: Path) -> None:
    if path.exists():
        raise RuntimeError(f"refusing to overwrite existing directory: {path}")
    path.mkdir(parents=True)


def run_world_dirs(run_dir: Path = ACCEPTED_RUN) -> list[Path]:
    worlds = sorted((run_dir / "worlds").iterdir(), key=lambda p: p.name)
    if len(worlds) != EXPECTED_WORLDS:
        raise RuntimeError(f"expected {EXPECTED_WORLDS} worlds, found {len(worlds)}")
    if not worlds[0].name.startswith("00_observed"):
        raise RuntimeError("observed world is not index 00")
    return worlds


def seed_dirs(world_dir: Path) -> list[Path]:
    dirs = [world_dir / f"seed{s}" for s in EXPECTED_SEEDS]
    missing = [str(p) for p in dirs if not p.is_dir()]
    if missing:
        raise RuntimeError(f"missing seed dirs: {missing}")
    return dirs


def world_parts(seed_dir: Path) -> tuple[int, str, int]:
    world_index_text, world = seed_dir.parent.name.split("_", 1)
    return int(world_index_text), world, int(seed_dir.name.removeprefix("seed"))


def accepted_manifest_hash(path: Path) -> str:
    rel = str(path.resolve().relative_to(ACCEPTED_RUN.resolve()))
    manifest = read_json(ACCEPTED_RUN / "hash_manifest.json")
    for row in manifest["files"]:
        if row["relative_path"] == rel:
            return str(row["sha256"])
    raise RuntimeError(f"accepted hash manifest does not list {rel}")


def validate_counts_exposure(cohort: ft.CueCohort) -> dict[str, Any]:
    expected_mask = np.asarray(
        [
            [session_from_cell(cell) == session for cell in cohort.cell_ids]
            for session in cohort.source_session_ids
        ],
        dtype=bool,
    )
    if not np.array_equal(cohort.mask, expected_mask):
        raise RuntimeError("saved source mask does not match session/cell membership")
    observed = np.broadcast_to(cohort.mask[:, :, None], cohort.X.shape)
    values = cohort.X[observed]
    if not np.isfinite(values).all() or np.any(values < 0):
        raise RuntimeError(
            "observed source counts contain nonfinite or negative values"
        )
    if not np.isfinite(cohort.exposure).all() or np.any(cohort.exposure <= 0):
        raise RuntimeError(
            "source bin exposure contains nonfinite or nonpositive values"
        )
    # The shortest valid cue bin is the known clipped final cue bin; it remains valid measured exposure.
    shortest = np.unravel_index(int(np.argmin(cohort.exposure)), cohort.exposure.shape)
    return {
        "source_count": len(cohort.source_trial_ids),
        "cell_count": len(cohort.cell_ids),
        "bin_count": int(cohort.X.shape[2]),
        "observed_count_values": int(values.size),
        "count_min": float(values.min()),
        "count_max": float(values.max()),
        "exposure_min_s": float(cohort.exposure[shortest]),
        "exposure_min_source_trial_id": cohort.source_trial_ids[shortest[0]],
        "exposure_min_bin": int(shortest[1]),
        "known_short_cue_bin_retained": bool(
            cohort.exposure[shortest] < ft.BIN_WIDTH_S
        ),
        "mask_matches_session": True,
        "missing_to_zero_conversion": False,
    }


def bin_label(window: str) -> int | None:
    if window == "wholecue":
        return None
    if not window.startswith("bin"):
        raise ValueError(window)
    b = int(window.removeprefix("bin"))
    if b not in WINDOW_BINS:
        raise ValueError(window)
    return b


def extract_window_features(
    rep: str, features: np.ndarray, window: str, *, cell_count: int = 29, dim: int = 8
) -> np.ndarray:
    """Return exact feature view for a cue window.

    raw290 whole-cue order is cell-major `(row, cell, bin) -> row x 290` from
    `ft.raw_features`. PCA/CEBRA whole-cue order is bin-major
    `(row, bin, coord) -> row x 80` from `ft.apply_pca_state`/`ft.embed_cue`.
    """
    b = bin_label(window)
    if b is None:
        return np.asarray(features)
    if rep == "raw290":
        if features.shape[1] != cell_count * ft.CUE_BINS:
            raise RuntimeError(
                f"raw feature shape {features.shape} is not row x {cell_count * ft.CUE_BINS}"
            )
        return np.asarray(features).reshape(features.shape[0], cell_count, ft.CUE_BINS)[
            :, :, b
        ]
    if features.shape[1] != ft.CUE_BINS * dim:
        raise RuntimeError(
            f"{rep} feature shape {features.shape} is not row x {ft.CUE_BINS * dim}"
        )
    return np.asarray(features).reshape(features.shape[0], ft.CUE_BINS, dim)[:, b, :]


def feature_dim(rep: str, window: str) -> int:
    if rep == "raw290":
        return 290 if window == "wholecue" else 29
    return 80 if window == "wholecue" else 8


def safe_load_cebra_embeddings(
    seed_dir: Path,
    arm: str,
    Xtr_scaled: np.ndarray,
    Xva_scaled: np.ndarray,
    *,
    device: str,
    checkpoint_step: int | None = None,
) -> tuple[np.ndarray, np.ndarray, list[str]]:
    fit_dir = seed_dir / "encoders" / arm
    info = read_json(fit_dir / "fit_info.json")
    if checkpoint_step is None:
        ckpt = Path(info["checkpoint_final"])
        expected_hash = info["checkpoint_final_sha256"]
    else:
        ckpt = fit_dir / f"checkpoint_step{checkpoint_step:04d}.pth"
        expected_hash = accepted_manifest_hash(ckpt)
    if sha256_file(ckpt) != expected_hash:
        raise RuntimeError(f"checkpoint hash mismatch: {ckpt}")
    solver = make_solver(
        Xtr_scaled.shape[1],
        int(info["dim"]),
        int(info["hidden"]),
        float(info["lr"]),
        device,
    )
    solver.load_state_dict(ft.load_torch_state(ckpt, device=device), strict=True)
    solver.n_features = Xtr_scaled.shape[1]
    return (
        ft.embed_cue(solver, Xtr_scaled, device=device),
        ft.embed_cue(solver, Xva_scaled, device=device),
        [str(ckpt)],
    )


def load_seed_features(
    seed_dir: Path,
    cohort: ft.CueCohort,
    *,
    device: str = "cpu",
    recompute_cebra: bool = True,
) -> SeedFeatures:
    world_index, world, seed = world_parts(seed_dir)
    shuffled = (
        None
        if world_index == 0
        else ft.shuffled_source_labels(
            cohort.metas, seed=ft.NULL_SEEDS[world_index - 1]
        )[0]
    )
    train_plans = ft.make_training_plans(
        cohort.metas,
        cohort.cell_ids,
        rows_per_class=ft.ROWS_PER_CLASS,
        seed=seed,
        shuffled_labels=shuffled,
    )
    validation_plans, _support = ft.make_validation_plans(
        cohort.metas, cohort.cell_ids, shuffled_labels=shuffled
    )
    train_bundle = ft.materialize_cue_rows(cohort, train_plans)
    validation_bundle = ft.materialize_cue_rows(cohort, validation_plans)
    ft.assert_equivalent(
        ft.read_csv_rows(seed_dir / "train_manifest.csv"),
        train_bundle.manifest,
        tolerance=0,
    )
    ft.assert_equivalent(
        ft.read_csv_rows(seed_dir / "validation_manifest.csv"),
        validation_bundle.manifest,
        tolerance=0,
    )
    scaler = ft.scaler_from_npz(seed_dir / "cue_scaler.npz")
    Xtr_scaled = ft.transform_cue_samples(train_bundle.X_cue, scaler)
    Xva_scaled = ft.transform_cue_samples(validation_bundle.X_cue, scaler)
    features_train: dict[str, np.ndarray] = {"raw290": ft.raw_features(Xtr_scaled)}
    features_validation: dict[str, np.ndarray] = {"raw290": ft.raw_features(Xva_scaled)}
    checked = [str(seed_dir / "cue_scaler.npz")]

    pca_meta = read_json(seed_dir / "pca8_state.json")
    pca_path = Path(pca_meta["path"])
    if sha256_file(pca_path) != pca_meta["sha256"]:
        raise RuntimeError(f"PCA state hash mismatch: {pca_path}")
    features_train["pca8"] = ft.apply_pca_state(pca_path, Xtr_scaled)
    features_validation["pca8"] = ft.apply_pca_state(pca_path, Xva_scaled)
    checked.append(str(pca_path))

    for arm in CEBRA_REPRESENTATIONS:
        fit_dir = seed_dir / "encoders" / arm
        info = read_json(fit_dir / "fit_info.json")
        if recompute_cebra:
            ztr, zva, files = safe_load_cebra_embeddings(
                seed_dir, arm, Xtr_scaled, Xva_scaled, device=device
            )
            saved = np.load(fit_dir / "cue_embeddings.npz", allow_pickle=False)
            if (
                float(np.max(np.abs(ztr - saved["Z_train"]))) > 1e-5
                or float(np.max(np.abs(zva - saved["Z_validation"]))) > 1e-5
            ):
                raise RuntimeError(f"saved/recomputed embedding mismatch for {fit_dir}")
            checked.extend(files)
        else:
            ckpt = Path(info["checkpoint_final"])
            if sha256_file(ckpt) != info["checkpoint_final_sha256"]:
                raise RuntimeError(f"checkpoint hash mismatch: {ckpt}")
            saved = np.load(fit_dir / "cue_embeddings.npz", allow_pickle=False)
            ztr, zva = (
                saved["Z_train"].astype(np.float32),
                saved["Z_validation"].astype(np.float32),
            )
            checked.extend([str(ckpt), str(fit_dir / "cue_embeddings.npz")])
        if not np.array_equal(saved["y_train"], train_bundle.y) or not np.array_equal(
            saved["y_validation"], validation_bundle.y
        ):
            raise RuntimeError(
                f"saved labels differ from materialized lineage for {fit_dir}"
            )
        features_train[arm] = ztr
        features_validation[arm] = zva
    return SeedFeatures(
        world,
        world_index,
        seed,
        seed_dir,
        train_bundle,
        validation_bundle,
        features_train,
        features_validation,
        checked,
    )


def prediction_rows(
    y: np.ndarray,
    pred: np.ndarray,
    score: np.ndarray,
    *,
    split: str,
    readout: str,
    prefix: Mapping[str, Any],
    plans: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    rows = ft.prediction_rows(
        y, pred, score, split=split, readout=readout, prefix=prefix, plans=plans
    )
    for row in rows:
        row["feature_dim"] = feature_dim(
            str(prefix["representation"]), str(prefix["window"])
        )
    return rows


def metric_row(
    y: np.ndarray,
    pred: np.ndarray,
    score: np.ndarray,
    *,
    weights: np.ndarray | None,
    readout: str,
    prefix: Mapping[str, Any],
) -> dict[str, Any]:
    row = ft.metric_row(y, pred, score, weights=weights, readout=readout, prefix=prefix)
    row["feature_dim"] = feature_dim(
        str(prefix["representation"]), str(prefix["window"])
    )
    return row


def fit_one_readout(
    seed_features: SeedFeatures,
    rep: str,
    window: str,
    readout: str,
    outdir: Path,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], str]:
    cell_count = int(seed_features.train_bundle.X_cue.shape[1])
    Xtr = extract_window_features(
        rep, seed_features.features_train[rep], window, cell_count=cell_count
    )
    Xva = extract_window_features(
        rep, seed_features.features_validation[rep], window, cell_count=cell_count
    )
    ptr, strn, pva, sva, _model, _scaler = ft.fit_decoder(
        readout, Xtr, seed_features.train_bundle.y, Xva, outdir=outdir
    )
    prefix = {
        "world": seed_features.world,
        "world_index": seed_features.world_index,
        "seed": seed_features.seed,
        "representation": rep,
        "window": window,
        "readout": readout,
        "fit_origin": "new_single_bin_readout"
        if window != "wholecue"
        else "accepted_wholecue_replay",
    }
    metrics = [
        metric_row(
            seed_features.train_bundle.y,
            ptr,
            strn,
            weights=ft.exact_class_weights(seed_features.train_bundle.y),
            readout=readout,
            prefix={**prefix, "split": "train"},
        ),
        metric_row(
            seed_features.validation_bundle.y,
            pva,
            sva,
            weights=seed_features.validation_bundle.weights,
            readout=readout,
            prefix={**prefix, "split": "validation"},
        ),
    ]
    predictions = []
    predictions.extend(
        prediction_rows(
            seed_features.train_bundle.y,
            ptr,
            strn,
            split="train",
            readout=readout,
            prefix=prefix,
            plans=seed_features.train_bundle.plans,
        )
    )
    predictions.extend(
        prediction_rows(
            seed_features.validation_bundle.y,
            pva,
            sva,
            split="validation",
            readout=readout,
            prefix=prefix,
            plans=seed_features.validation_bundle.plans,
        )
    )
    return metrics, predictions, sha256_file(outdir / f"{readout}_decoder_state.npz")


def replay_wholecue_readout(
    seed_features: SeedFeatures,
    rep: str,
    readout: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], str]:
    meta = read_json(
        seed_features.seed_dir
        / "readouts"
        / rep
        / readout
        / f"{readout}_decoder_state.json"
    )
    state_path = Path(meta["path"])
    if sha256_file(state_path) != meta["sha256"]:
        raise RuntimeError(f"accepted decoder state hash mismatch: {state_path}")
    cell_count = int(seed_features.train_bundle.X_cue.shape[1])
    Xtr = extract_window_features(
        rep, seed_features.features_train[rep], "wholecue", cell_count=cell_count
    )
    Xva = extract_window_features(
        rep, seed_features.features_validation[rep], "wholecue", cell_count=cell_count
    )
    ptr, strn = ft.predict_decoder_state(state_path, Xtr)
    pva, sva = ft.predict_decoder_state(state_path, Xva)
    prefix = {
        "world": seed_features.world,
        "world_index": seed_features.world_index,
        "seed": seed_features.seed,
        "representation": rep,
        "window": "wholecue",
        "readout": readout,
        "fit_origin": "accepted_wholecue_replay",
    }
    metrics = [
        metric_row(
            seed_features.train_bundle.y,
            ptr,
            strn,
            weights=ft.exact_class_weights(seed_features.train_bundle.y),
            readout=readout,
            prefix={**prefix, "split": "train"},
        ),
        metric_row(
            seed_features.validation_bundle.y,
            pva,
            sva,
            weights=seed_features.validation_bundle.weights,
            readout=readout,
            prefix={**prefix, "split": "validation"},
        ),
    ]
    predictions = []
    predictions.extend(
        prediction_rows(
            seed_features.train_bundle.y,
            ptr,
            strn,
            split="train",
            readout=readout,
            prefix=prefix,
            plans=seed_features.train_bundle.plans,
        )
    )
    predictions.extend(
        prediction_rows(
            seed_features.validation_bundle.y,
            pva,
            sva,
            split="validation",
            readout=readout,
            prefix=prefix,
            plans=seed_features.validation_bundle.plans,
        )
    )
    # Check the historical results, not merely the ability to load their state.
    accepted_metrics = [
        r
        for r in ft.read_csv_rows(seed_features.seed_dir / "metrics.csv")
        if r["representation"] == rep and r["readout"] == readout
    ]
    accepted_predictions = [
        r
        for r in ft.read_csv_rows(seed_features.seed_dir / "predictions.csv.gz")
        if r["representation"] == rep and r["readout"] == readout
    ]
    strip = lambda r: {
        k: v for k, v in r.items() if k not in ("window", "fit_origin", "feature_dim")
    }
    ft.compare_replay(
        accepted_metrics,
        accepted_predictions,
        list(map(strip, metrics)),
        list(map(strip, predictions)),
    )
    return metrics, predictions, str(state_path)


def metric_index(
    metrics: Sequence[Mapping[str, Any]],
) -> dict[tuple[str, int, str, str, str, str], Mapping[str, Any]]:
    out = {}
    for row in metrics:
        key = (
            str(row["world"]),
            int(row["seed"]),
            str(row["representation"]),
            str(row["window"]),
            str(row["readout"]),
            str(row["split"]),
        )
        if key in out:
            raise RuntimeError(f"duplicate metric row: {key}")
        out[key] = row
    return out


def mean_metric(
    metrics: Mapping[tuple[str, int, str, str, str, str], Mapping[str, Any]],
    world: str,
    rep: str,
    window: str,
    readout: str,
    split: str,
    field: str,
) -> float:
    vals = []
    for seed in EXPECTED_SEEDS:
        value = metrics[(world, seed, rep, window, readout, split)][field]
        if value == "":
            raise RuntimeError(
                f"metric {field} unavailable for {world}/{rep}/{window}/{readout}"
            )
        vals.append(float(value))
    return float(np.mean(vals))


def summarize_metrics(
    metrics_rows: Sequence[Mapping[str, Any]], outdir: Path
) -> dict[str, Any]:
    idx = metric_index(metrics_rows)
    worlds = sorted({str(r["world"]) for r in metrics_rows})
    null_worlds = [w for w in worlds if w != "observed"]
    if len(null_worlds) != EXPECTED_NULL_WORLDS:
        raise RuntimeError(
            f"expected {EXPECTED_NULL_WORLDS} null worlds, got {len(null_worlds)}"
        )

    bin_rows = []
    for world in worlds:
        for window in BIN_WINDOWS:
            seed_gains = []
            for seed in EXPECTED_SEEDS:
                cue = float(
                    idx[(world, seed, "cue_time", window, "logistic", "validation")][
                        "balanced_log_loss"
                    ]
                )
                full = float(
                    idx[(world, seed, "full_time", window, "logistic", "validation")][
                        "balanced_log_loss"
                    ]
                )
                seed_gains.append(cue - full)
            bin_rows.append(
                {
                    "world": world,
                    "window": window,
                    "mean_loss_gain_cue_minus_full": float(np.mean(seed_gains)),
                    "seed_gains": seed_gains,
                }
            )
    write_csv(
        outdir / "bin_primary_family.csv",
        [
            {k: (json.dumps(v) if isinstance(v, list) else v) for k, v in row.items()}
            for row in bin_rows
        ],
    )

    def primary_stat(world: str) -> float:
        return max(
            float(r["mean_loss_gain_cue_minus_full"])
            for r in bin_rows
            if r["world"] == world
        )

    observed_primary = primary_stat("observed")
    null_primary = [primary_stat(w) for w in null_worlds]
    primary_tail = (1 + sum(v >= observed_primary - 1e-12 for v in null_primary)) / (
        1 + len(null_primary)
    )

    def absolute_ba_stat(world: str) -> tuple[float, dict[str, Any]]:
        best = (-math.inf, {})
        for rep in REPRESENTATIONS:
            for window in BIN_WINDOWS:
                for readout in DECODERS:
                    ba = mean_metric(
                        idx,
                        world,
                        rep,
                        window,
                        readout,
                        "validation",
                        "balanced_accuracy",
                    )
                    if ba > best[0]:
                        best = (
                            ba,
                            {
                                "representation": rep,
                                "window": window,
                                "readout": readout,
                            },
                        )
        return best

    observed_ba, observed_ba_arg = absolute_ba_stat("observed")
    null_ba = [absolute_ba_stat(w)[0] for w in null_worlds]
    ba_tail = (1 + sum(v >= observed_ba - 1e-12 for v in null_ba)) / (1 + len(null_ba))

    def absolute_loss_stat(world: str) -> tuple[float, dict[str, Any]]:
        best = (-math.inf, {})
        for rep in REPRESENTATIONS:
            for window in BIN_WINDOWS:
                loss = mean_metric(
                    idx,
                    world,
                    rep,
                    window,
                    "logistic",
                    "validation",
                    "balanced_log_loss",
                )
                stat = ft.LOG2 - loss
                if stat > best[0]:
                    best = (
                        stat,
                        {
                            "representation": rep,
                            "window": window,
                            "readout": "logistic",
                        },
                    )
        return best

    observed_loss_abs, observed_loss_arg = absolute_loss_stat("observed")
    null_loss_abs = [absolute_loss_stat(w)[0] for w in null_worlds]
    loss_tail = (1 + sum(v >= observed_loss_abs - 1e-12 for v in null_loss_abs)) / (
        1 + len(null_loss_abs)
    )

    wholecue_rows = []
    for rep in REPRESENTATIONS:
        for readout in DECODERS:
            wholecue_rows.append(
                {
                    "representation": rep,
                    "readout": readout,
                    "balanced_accuracy_mean": mean_metric(
                        idx,
                        "observed",
                        rep,
                        "wholecue",
                        readout,
                        "validation",
                        "balanced_accuracy",
                    ),
                    "auroc_mean": mean_metric(
                        idx, "observed", rep, "wholecue", readout, "validation", "auroc"
                    )
                    if readout == "logistic"
                    or all(
                        idx[("observed", seed, rep, "wholecue", readout, "validation")][
                            "auroc"
                        ]
                        != ""
                        for seed in EXPECTED_SEEDS
                    )
                    else "",
                    "balanced_log_loss_mean": mean_metric(
                        idx,
                        "observed",
                        rep,
                        "wholecue",
                        readout,
                        "validation",
                        "balanced_log_loss",
                    )
                    if readout == "logistic"
                    else "",
                }
            )
    write_csv(outdir / "wholecue_fixed_reference.csv", wholecue_rows)

    summary = {
        "created_utc": utc_now(),
        "counts": {
            "new_single_bin_readouts": EXPECTED_NEW_BIN_READOUTS,
            "wholecue_saved_replays": EXPECTED_WHOLE_REPLAYS,
            "metric_groups_train_plus_validation": EXPECTED_TOTAL_METRIC_GROUPS,
            "worlds": EXPECTED_WORLDS,
            "null_worlds": EXPECTED_NULL_WORLDS,
            "seeds": list(EXPECTED_SEEDS),
            "bin_windows": list(BIN_WINDOWS),
            "representations": list(REPRESENTATIONS),
            "readouts": list(DECODERS),
        },
        "primary_null_family": {
            "statistic": "max over 10 bins of three-seed mean paired logistic balanced-loss gain cue_time-minus-full_time",
            "observed": observed_primary,
            "null": null_primary,
            "inclusive_plus_one_tail": primary_tail,
            "wholecue_is_fixed_comparator_not_11th_bin": True,
        },
        "secondary_absolute_ba_family": {
            "statistic": "max over 10 bins x 4 representations x 2 readouts of three-seed mean validation balanced accuracy",
            "observed": observed_ba,
            "observed_argmax_descriptor_not_selection_rule": observed_ba_arg,
            "null": null_ba,
            "inclusive_plus_one_tail": ba_tail,
        },
        "secondary_absolute_logistic_loss_family": {
            "statistic": "max over 10 bins x 4 representations of log(2)-three-seed-mean balanced log loss",
            "observed": observed_loss_abs,
            "observed_argmax_descriptor_not_selection_rule": observed_loss_arg,
            "null": null_loss_abs,
            "inclusive_plus_one_tail": loss_tail,
        },
        "wholecue_fixed_reference": wholecue_rows,
    }
    write_json(outdir / "summary.json", summary)
    return summary


def confusion_rows(
    predictions: Sequence[Mapping[str, Any]], *, validation_only: bool = True
) -> list[dict[str, Any]]:
    groups: dict[tuple[str, int, str, str, str, str], Counter[tuple[str, str]]] = (
        defaultdict(Counter)
    )
    supports: dict[tuple[str, int, str, str, str, str], Counter[str]] = defaultdict(
        Counter
    )
    for p in predictions:
        if validation_only and p["split"] != "validation":
            continue
        key = (
            str(p["world"]),
            int(p["seed"]),
            str(p["representation"]),
            str(p["window"]),
            str(p["readout"]),
            str(p["fit_origin"]),
        )
        truth = str(p["label"])
        pred = str(p["pred_label"])
        groups[key][(truth, pred)] += 1
        supports[key][truth] += 1
    rows = []
    for key, counts in sorted(groups.items()):
        world, seed, rep, window, readout, origin = key
        for truth in ft.LABELS:
            denom = supports[key][truth]
            for pred in ft.LABELS:
                count = counts[(truth, pred)]
                rows.append(
                    {
                        "world": world,
                        "seed": seed,
                        "representation": rep,
                        "window": window,
                        "readout": readout,
                        "fit_origin": origin,
                        "true_label": truth,
                        "predicted_label": pred,
                        "count": count,
                        "true_class_support": denom,
                        "true_class_normalized": (count / denom) if denom else "",
                    }
                )
    return rows


def observed_source_sensitivity(
    predictions: Sequence[Mapping[str, Any]], outdir: Path
) -> dict[str, Any]:
    obs = [
        p
        for p in predictions
        if p["world"] == "observed" and p["split"] == "validation"
    ]
    if not obs:
        raise RuntimeError("missing observed validation predictions")
    index = {}
    for p in obs:
        key = (
            int(p["seed"]),
            str(p["representation"]),
            str(p["window"]),
            str(p["readout"]),
            str(p["row_id"]),
        )
        if key in index:
            raise RuntimeError(f"duplicate prediction row for sensitivity: {key}")
        index[key] = p
    row_info: dict[str, tuple[str, dict[str, str]]] = {}
    source_info: dict[str, tuple[str, str]] = {}
    for p in obs:
        blocks = dict(item.split("=", 1) for item in str(p["sources"]).split(";"))
        value = (str(p["label"]), blocks)
        if p["row_id"] in row_info and row_info[p["row_id"]] != value:
            raise RuntimeError("source lineage/label changes across methods")
        row_info[str(p["row_id"])] = value
        for session, source in blocks.items():
            meta = (session, str(p["label"]))
            if source in source_info and source_info[source] != meta:
                raise RuntimeError("inconsistent source session/class")
            source_info[source] = meta
    rows = sorted(row_info)
    y = np.array([ft.LABEL_TO_INT[row_info[r][0]] for r in rows])
    row_sources = [tuple(row_info[r][1].values()) for r in rows]
    strata: dict[tuple[str, str], list[str]] = defaultdict(list)
    for source, meta in sorted(source_info.items()):
        strata[meta].append(source)

    errors = {}
    for seed in EXPECTED_SEEDS:
        for window in WINDOWS:
            for readout in DECODERS:
                for rep in REPRESENTATIONS:
                    ps = [index[(seed, rep, window, readout, row)] for row in rows]
                    pred = np.array([ft.LABEL_TO_INT[p["pred_label"]] for p in ps])
                    score = np.asarray([float(p["score"]) for p in ps], dtype=float)
                    correct = pred == y
                    if readout == "logistic":
                        prob = np.clip(score, 1e-9, 1 - 1e-9)
                        loss = -(y * np.log(prob) + (1 - y) * np.log1p(-prob))
                    else:
                        loss = np.full_like(score, np.nan, dtype=float)
                    errors[(seed, rep, window, readout)] = (correct, loss)

    def evaluate(
        weights: Any, identity: Mapping[str, Any]
    ) -> tuple[list[dict[str, Any]], bool]:
        weights = np.asarray(weights, dtype=float)
        class_mass = [float(weights[y == c].sum()) for c in (0, 1)]
        valid = min(class_mass) > 0
        balanced = np.zeros(len(y), dtype=float)
        if valid:
            for c in (0, 1):
                balanced[y == c] = 0.5 * weights[y == c] / class_mass[c]
        details = []
        for window in WINDOWS:
            for readout in DECODERS:
                seed_values = []
                for seed in EXPECTED_SEEDS:
                    ca, cl = errors[(seed, "cue_time", window, readout)]
                    fa, fl = errors[(seed, "full_time", window, readout)]
                    vals = {
                        "cue_ba": float(balanced @ ca) if valid else None,
                        "full_ba": float(balanced @ fa) if valid else None,
                        "ba_gain_full_minus_cue": float(
                            balanced @ (fa.astype(float) - ca.astype(float))
                        )
                        if valid
                        else None,
                        "loss_gain_cue_minus_full": float(balanced @ (cl - fl))
                        if valid and readout == "logistic"
                        else None,
                    }
                    # Fixed-model source sensitivity of window-vs-whole, not window selection.
                    for rep in REPRESENTATIONS:
                        correct, loss = errors[(seed, rep, window, readout)]
                        whole_correct, whole_loss = errors[
                            (seed, rep, "wholecue", readout)
                        ]
                        vals[f"{rep}_ba"] = float(balanced @ correct) if valid else None
                        vals[f"{rep}_ba_bin_minus_whole"] = (
                            float(balanced @ (correct.astype(float) - whole_correct))
                            if valid
                            else None
                        )
                        vals[f"{rep}_loss"] = (
                            float(balanced @ loss)
                            if valid and readout == "logistic"
                            else None
                        )
                        vals[f"{rep}_loss_whole_minus_bin"] = (
                            float(balanced @ (whole_loss - loss))
                            if valid and readout == "logistic"
                            else None
                        )
                    seed_values.append(vals)
                    details.append(
                        {
                            **identity,
                            "window": window,
                            "readout": readout,
                            "seed": seed,
                            "estimable": valid,
                            "absent_weight": class_mass[0],
                            "present_weight": class_mass[1],
                            **vals,
                        }
                    )
                means = {
                    k: (
                        float(np.mean([v[k] for v in seed_values]))
                        if seed_values[0][k] is not None
                        else None
                    )
                    for k in seed_values[0]
                }
                details.append(
                    {
                        **identity,
                        "window": window,
                        "readout": readout,
                        "seed": "mean",
                        "estimable": valid,
                        "absent_weight": class_mass[0],
                        "present_weight": class_mass[1],
                        **means,
                    }
                )
        return details, valid

    deletions, resamples, draw_rows = [], [], []
    invalid_deletions = 0
    for source in sorted(source_info):
        weights = [float(source not in members) for members in row_sources]
        details, valid = evaluate(
            weights,
            {
                "deleted_source_trial_id": source,
                "sensitivity_kind": "delete_one_source",
            },
        )
        deletions.extend(details)
        invalid_deletions += int(not valid)
    rng = np.random.default_rng(ft.RESAMPLE_SEED)
    for b in range(ft.RESAMPLES):
        multiplicities = Counter()
        for members in strata.values():
            multiplicities.update(
                map(str, rng.choice(members, len(members), replace=True))
            )
        weights = [
            float(math.prod(multiplicities[source] for source in members))
            for members in row_sources
        ]
        details, _valid = evaluate(
            weights, {"resample": b, "sensitivity_kind": "stratified_source_reweight"}
        )
        resamples.extend(details)
        draw_rows.extend(
            {"resample": b, "source_trial_id": s, "multiplicity": multiplicities[s]}
            for s in sorted(source_info)
        )
    write_csv(outdir / "validation_source_deletion.csv", deletions)
    write_csv(outdir / "validation_source_resamples.csv", resamples)
    write_csv(outdir / "validation_source_draws.csv", draw_rows)
    summary: dict[str, Any] = {
        "deletions": len(source_info),
        "resamples": ft.RESAMPLES,
        "seeds": list(EXPECTED_SEEDS),
        "windows": list(WINDOWS),
        "inestimable_deletions": int(invalid_deletions),
        "sensitivity_not_biological_confidence_intervals": True,
        "pseudorow_bootstrap_used": False,
    }
    for window in WINDOWS:
        vals = [
            r["loss_gain_cue_minus_full"]
            for r in resamples
            if r.get("window") == window
            and r.get("readout") == "logistic"
            and r.get("seed") == "mean"
            and r.get("estimable")
        ]
        summary[f"{window}_logistic_loss_gain_quantiles_025_50_975"] = (
            np.quantile(vals, [0.025, 0.5, 0.975]).tolist() if vals else None
        )
    write_json(outdir / "source_sensitivity_summary.json", summary)
    return summary


def helper_hashes() -> dict[str, str]:
    return {
        "cebra_full_trial_transfer.py": sha256_file(
            CANONICAL_ROOT / "scripts/cebra_full_trial_transfer.py"
        ),
        "import_place195_sessions.py": sha256_file(
            CANONICAL_ROOT / "scripts/import_place195_sessions.py"
        ),
        "place195_split_filtered_access.py": sha256_file(
            CANONICAL_ROOT / "scripts/place195_split_filtered_access.py"
        ),
        "place195_v7_v8_neural_experiments.py": sha256_file(
            CANONICAL_ROOT / "scripts/place195_v7_v8_neural_experiments.py"
        ),
        "place195_v8b_v9_cebra.py": sha256_file(
            CANONICAL_ROOT / "scripts/place195_v8b_v9_cebra.py"
        ),
        "cebra_latent_atlas.py": sha256_file(
            CANONICAL_ROOT / "scripts/cebra_latent_atlas.py"
        ),
    }


def approval_facts() -> dict[str, Any]:
    docs = {}
    for path in (PROTOCOL_PATH, SOURCE_SUPPORT_PATH):
        docs[str(path.relative_to(CANONICAL_ROOT))] = (
            sha256_file(path) if path.exists() else None
        )
    return {
        "approved_for": "cebra-cue-time-readout-20261005-single-bin-readout-fitting",
        "script_sha256": sha256_file(SCRIPT_PATH),
        "docs_sha256": docs,
        "helper_hashes": helper_hashes(),
        "accepted_run_hash_manifest_sha256": sha256_file(
            ACCEPTED_RUN / "hash_manifest.json"
        ),
        "accepted_run_metrics_sha256": sha256_file(ACCEPTED_RUN / "metrics.csv"),
        "source_npz_sha256": ft.SOURCE_NPZ_SHA256,
        "expected_counts": {
            "new_single_bin_readouts": EXPECTED_NEW_BIN_READOUTS,
            "wholecue_saved_replays": EXPECTED_WHOLE_REPLAYS,
            "worlds": EXPECTED_WORLDS,
            "null_worlds": EXPECTED_NULL_WORLDS,
            "seeds": list(EXPECTED_SEEDS),
        },
        "accepted_executed_ft_sha256": ACCEPTED_EXECUTED_FT_SHA256,
        "current_ft_sha256": helper_hashes()["cebra_full_trial_transfer.py"],
        "ft_snapshot_difference": "current ft differs from accepted executed runner only by typing.cast/Pyright-only annotations inspected by parent; scientific functions unchanged",
        "scientific_preflight_review": PARENT_REVIEW_NOTE,
        "null_family": "primary=max over 10 bins of three-seed mean paired logistic loss gain; wholecue fixed comparator",
    }


def require_prefit_approval(path: Path) -> None:
    approval = read_json(path)
    if not approval.get("approved"):
        raise RuntimeError("approval JSON does not contain approved=true")
    audit_path = Path(approval.get("source_audit_path", "missing-source-audit"))
    if not audit_path.is_file() or sha256_file(audit_path) != approval.get(
        "source_audit_sha256"
    ):
        raise RuntimeError("missing or changed prefit source audit")
    facts = approval_facts()
    mismatches = []
    for key, value in facts.items():
        if approval.get(key) != value:
            mismatches.append(key)
    if mismatches:
        raise RuntimeError(
            f"approval facts differ; protocol/code/input changed or approval stale: {mismatches}"
        )


@contextmanager
def no_fit_guard() -> Iterator[None]:
    originals = {
        "StandardScaler.fit": ft.StandardScaler.fit,
        "PCA.fit": ft.PCA.fit,
        "PCA.fit_transform": ft.PCA.fit_transform,
        "LogisticRegression.fit": ft.LogisticRegression.fit,
        "SVC.fit": ft.SVC.fit,
        "Adam.step": torch.optim.Adam.step,
    }

    def forbid(*_args: Any, **_kwargs: Any) -> None:
        raise RuntimeError("fitting/training is blocked in verify mode")

    ft.StandardScaler.fit = forbid  # type: ignore[method-assign]
    ft.PCA.fit = forbid  # type: ignore[method-assign]
    ft.PCA.fit_transform = forbid  # type: ignore[method-assign]
    ft.LogisticRegression.fit = forbid  # type: ignore[method-assign]
    ft.SVC.fit = forbid  # type: ignore[method-assign]
    torch.optim.Adam.step = forbid  # type: ignore[method-assign]
    try:
        yield
    finally:
        ft.StandardScaler.fit = originals["StandardScaler.fit"]  # type: ignore[method-assign]
        ft.PCA.fit = originals["PCA.fit"]  # type: ignore[method-assign]
        ft.PCA.fit_transform = originals["PCA.fit_transform"]  # type: ignore[method-assign]
        ft.LogisticRegression.fit = originals["LogisticRegression.fit"]  # type: ignore[method-assign]
        ft.SVC.fit = originals["SVC.fit"]  # type: ignore[method-assign]
        torch.optim.Adam.step = originals["Adam.step"]  # type: ignore[method-assign]


def audit_source_support(outdir: Path) -> dict[str, Any]:
    ensure_fresh_dir(outdir)
    ft.verify_hash_manifest(ACCEPTED_RUN)
    expected_inputs = read_json(ACCEPTED_RUN / "input_manifest_hashes.json")
    for name, digest in expected_inputs.items():
        if sha256_file(CANONICAL_ROOT / name) != digest:
            raise RuntimeError(f"accepted source ledger changed: {name}")
    cohort = ft.load_cue_cohort()
    count_summary = validate_counts_exposure(cohort)
    worlds = run_world_dirs()
    support_rows = []
    worked_rows = []
    validation_combo_counts = []
    overlap_failures = []
    for world_dir in worlds:
        world_index_text, world_name = world_dir.name.split("_", 1)
        for sdir in seed_dirs(world_dir):
            seed = int(sdir.name.removeprefix("seed"))
            # Reconstruct every observed/null assembly from source labels, rather than trusting a manifest roundtrip.
            with no_fit_guard():
                load_seed_features(sdir, cohort, device="cpu", recompute_cebra=False)
            train_manifest = ft.read_csv_rows(sdir / "train_manifest.csv")
            val_manifest = ft.read_csv_rows(sdir / "validation_manifest.csv")
            train_sources = {r["source_trial_id"] for r in train_manifest}
            val_sources = {r["source_trial_id"] for r in val_manifest}
            if train_sources & val_sources:
                overlap_failures.append(
                    {
                        "world": world_name,
                        "seed": seed,
                        "overlap": sorted(train_sources & val_sources),
                    }
                )
            for split, rows in (
                ("train", train_manifest),
                ("validation", val_manifest),
            ):
                row_ids = defaultdict(list)
                for row in rows:
                    row_ids[row["row_id"]].append(row)
                labels = Counter(rs[0]["label"] for rs in row_ids.values())
                support_rows.append(
                    {
                        "world_index": int(world_index_text),
                        "world": world_name,
                        "seed": seed,
                        "split": split,
                        "pseudo_rows": len(row_ids),
                        "manifest_rows": len(rows),
                        "absent_rows": labels["absent"],
                        "present_rows": labels["present"],
                        "unique_sources_used": len(
                            {r["source_trial_id"] for r in rows}
                        ),
                        "max_source_reuse": max(
                            Counter(r["source_trial_id"] for r in rows).values()
                        ),
                    }
                )
            if world_name == "observed" and seed == 0:
                for manifest_path, split in (
                    (sdir / "train_manifest.csv", "train"),
                    (sdir / "validation_manifest.csv", "validation"),
                ):
                    rows = ft.read_csv_rows(manifest_path)
                    first_id = rows[0]["row_id"]
                    worked_rows.extend(
                        {"split": split, **r} for r in rows if r["row_id"] == first_id
                    )
                    if split == "validation":
                        row_counts = Counter(r["row_id"] for r in rows)
                        label_counts = Counter(
                            next(r["label"] for r in rows if r["row_id"] == rid)
                            for rid in row_counts
                        )
                        validation_combo_counts.append(
                            {
                                "validation_product_rows": len(row_counts),
                                "absent": label_counts["absent"],
                                "present": label_counts["present"],
                            }
                        )
    if overlap_failures:
        raise RuntimeError(
            f"train/validation source overlap detected: {overlap_failures[:3]}"
        )
    if validation_combo_counts and validation_combo_counts[0] != {
        "validation_product_rows": 30,
        "absent": 24,
        "present": 6,
    }:
        raise RuntimeError(
            f"unexpected observed validation combo counts: {validation_combo_counts[0]}"
        )
    write_csv(outdir / "source_support_by_world_seed.csv", support_rows)
    write_csv(outdir / "worked_observed_seed0_rows.csv", worked_rows)
    summary = {
        "created_utc": utc_now(),
        "accepted_run": str(ACCEPTED_RUN),
        "protected_preexisting_hashes_from_parent": {
            "docs/professor_updates/research_review_20260928/evidence.py": "15dd91f31afe58e1a969cd54389fd8698b6e7d8aaf43c3c1660b9e0e3a5e8a54",
            "docs/reports/README.md": "7880a6c8483934d49f14b77b909fcd0236d74d1e20ddc5132ec605f35d5f71dd",
            "scripts/test_cebra_latent_atlas.py": "d38a866edc1bb37a416ad4b290ff8056d0efa50c73cb8a05b40292bc3ef45fc3",
        },
        "ft_snapshot_note": approval_facts()["ft_snapshot_difference"],
        "helper_hashes": helper_hashes(),
        "count_exposure_summary": count_summary,
        "source_split_counts": dict(Counter(cohort.source_splits)),
        "source_label_counts": dict(Counter(cohort.source_labels)),
        "source_split_label_counts": {
            f"{split}:{label}": n
            for (split, label), n in Counter(
                zip(cohort.source_splits, cohort.source_labels, strict=True)
            ).items()
        },
        "world_count": len(worlds),
        "null_world_count": len(worlds) - 1,
        "seed_count_per_world": len(EXPECTED_SEEDS),
        "readout_count_confirmation": {
            "new_single_bin_readouts": EXPECTED_NEW_BIN_READOUTS,
            "wholecue_saved_replays": EXPECTED_WHOLE_REPLAYS,
        },
        "observed_seed0_validation_combinations": validation_combo_counts[0]
        if validation_combo_counts
        else None,
        "train_validation_source_overlap": False,
        "raw_feature_order_contract": "raw whole cue is cell-major row x cell x bin; single bins are [:, :, b] -> 29 features",
        "latent_feature_order_contract": "PCA/CEBRA whole cue is bin-major row x bin x coord; single bins are [:, b, :] -> 8 features",
        "scientific_preflight_review": PARENT_REVIEW_NOTE,
    }
    summary["accepted_hash_manifest_verified"] = True
    summary["source_ledger_hashes_verified"] = expected_inputs
    summary["all_63_assemblies_reconstructed"] = True
    write_json(outdir / "source_support_audit.json", summary)
    write_json(
        outdir / "prefit_approval_request.json", {"approved": False, **approval_facts()}
    )
    return summary


def geometry_diagnostics(outdir: Path, *, device: str = "cpu") -> dict[str, Any]:
    ensure_fresh_dir(outdir)
    cohort = ft.load_cue_cohort()
    rows = []
    spectra_rows = []
    stability_rows = []
    for sdir in seed_dirs(ACCEPTED_RUN / "worlds/00_observed"):
        seed_features = load_seed_features(
            sdir, cohort, device=device, recompute_cebra=False
        )
        scaler = ft.scaler_from_npz(sdir / "cue_scaler.npz")
        Xtr_scaled = ft.transform_cue_samples(seed_features.train_bundle.X_cue, scaler)
        Xva_scaled = ft.transform_cue_samples(
            seed_features.validation_bundle.X_cue, scaler
        )
        train_row_ids = np.arange(len(seed_features.train_bundle.y))
        val_row_ids = np.arange(len(seed_features.validation_bundle.y))
        embedded: dict[tuple[str, int], tuple[np.ndarray, np.ndarray]] = {}
        for arm in CEBRA_REPRESENTATIONS:
            for step in CHECKPOINT_STEPS:
                ztr, zva, files = safe_load_cebra_embeddings(
                    sdir,
                    arm,
                    Xtr_scaled,
                    Xva_scaled,
                    device=device,
                    checkpoint_step=step,
                )
                embedded[(arm, step)] = (ztr, zva)
                for split, z in (("train", ztr), ("validation", zva)):
                    spec = spectrum(z)
                    spectra_rows.append(
                        {
                            "seed": seed_features.seed,
                            "arm": arm,
                            "checkpoint_step": step,
                            "split": split,
                            "space": "wholecue80",
                            "participation_ratio": spec["participation_ratio"],
                            "norm_mean": spec["norm_mean"],
                            "variance_fraction_1": spec["fractions"][0]
                            if spec["fractions"]
                            else "",
                            "variance_fractions": json.dumps(spec["fractions"]),
                        }
                    )
                    zb = z.reshape(z.shape[0], ft.CUE_BINS, 8)
                    for b in WINDOW_BINS:
                        bs = spectrum(zb[:, b, :])
                        spectra_rows.append(
                            {
                                "seed": seed_features.seed,
                                "arm": arm,
                                "checkpoint_step": step,
                                "split": split,
                                "space": f"bin{b:02d}_8d",
                                "participation_ratio": bs["participation_ratio"],
                                "norm_mean": bs["norm_mean"],
                                "variance_fraction_1": bs["fractions"][0]
                                if bs["fractions"]
                                else "",
                                "variance_fractions": json.dumps(bs["fractions"]),
                            }
                        )
                rows.append(
                    {
                        "seed": seed_features.seed,
                        "arm": arm,
                        "checkpoint_step": step,
                        "loaded_checkpoint": ";".join(files),
                    }
                )
            final_tr, final_va = embedded[(arm, 1000)]
            for step in CHECKPOINT_STEPS:
                ztr, zva = embedded[(arm, step)]
                for split, z, final, row_ids in (
                    ("train", ztr, final_tr, train_row_ids),
                    ("validation", zva, final_va, val_row_ids),
                ):
                    stability_rows.append(
                        {
                            "seed": seed_features.seed,
                            "arm": arm,
                            "checkpoint_step": step,
                            "split": split,
                            "space": "wholecue80",
                            **fidelity(final, z, row_ids, k=10),
                        }
                    )
                    for b in WINDOW_BINS:
                        stability_rows.append(
                            {
                                "seed": seed_features.seed,
                                "arm": arm,
                                "checkpoint_step": step,
                                "split": split,
                                "space": f"bin{b:02d}_8d",
                                **fidelity(
                                    final.reshape(len(final), 10, 8)[:, b],
                                    z.reshape(len(z), 10, 8)[:, b],
                                    row_ids,
                                    k=10,
                                ),
                            }
                        )
    write_csv(outdir / "geometry_checkpoints_loaded.csv", rows)
    write_csv(outdir / "geometry_spectra.csv", spectra_rows)
    write_csv(outdir / "geometry_stability_vs_final.csv", stability_rows)
    summary = {
        "created_utc": utc_now(),
        "world": "observed only",
        "arms": list(CEBRA_REPRESENTATIONS),
        "seeds": list(EXPECTED_SEEDS),
        "checkpoint_steps": list(CHECKPOINT_STEPS),
        "readout_selection_on_checkpoints": False,
        "two_centroid_rdm_correlation_used": False,
        "source_reuse_caveat": "descriptive geometry over condition-level pseudorows; rows are synthetic and source-reusing, not biological independent trials",
        "spectra_rows": len(spectra_rows),
        "stability_rows": len(stability_rows),
    }
    write_json(outdir / "geometry_summary.json", summary)
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(7, 4))
        for arm in CEBRA_REPRESENTATIONS:
            xs, ys = [], []
            for step in CHECKPOINT_STEPS:
                vals = [
                    float(r["participation_ratio"])
                    for r in spectra_rows
                    if r["arm"] == arm
                    and r["checkpoint_step"] == step
                    and r["split"] == "validation"
                    and r["space"] == "wholecue80"
                    and r["participation_ratio"] != ""
                ]
                xs.append(step)
                ys.append(float(np.mean(vals)))
            ax.plot(xs, ys, marker="o", label=arm)
        ax.set_title("Observed validation whole-cue80 participation ratio")
        ax.set_xlabel("saved checkpoint update")
        ax.set_ylabel("participation ratio (mean over seeds)")
        ax.legend()
        fig.tight_layout()
        fig.savefig(outdir / "geometry_participation_ratio.png", dpi=160)
        plt.close(fig)
    except (
        Exception
    ) as exc:  # pragma: no cover - plotting availability is environment-level.
        summary["plot_warning"] = str(exc)
        write_json(outdir / "geometry_summary.json", summary)
    return summary


def cmd_audit(args: argparse.Namespace) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = Path(args.output_dir) if args.output_dir else PREPARATION_ROOT / f"audit-{ts}"
    summary = audit_source_support(out)
    print(
        json.dumps(
            {"audit_dir": str(out), "summary": summary}, indent=2, sort_keys=True
        )
    )


def cmd_geometry(args: argparse.Namespace) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = (
        Path(args.output_dir)
        if args.output_dir
        else PREPARATION_ROOT / f"geometry-{ts}"
    )
    ft.verify_hash_manifest(ACCEPTED_RUN)
    with no_fit_guard():
        summary = geometry_diagnostics(out, device=args.device)
    ft.write_hash_manifest(out)
    print(
        json.dumps(
            {"geometry_dir": str(out), "summary": summary}, indent=2, sort_keys=True
        )
    )


def cmd_run(args: argparse.Namespace) -> None:
    require_prefit_approval(Path(args.approval))
    if not (
        0 < args.max_seconds <= MAX_RUN_SECONDS
        and 0 < args.output_limit_gib <= RUN_OUTPUT_LIMIT_GIB
    ):
        raise RuntimeError("runtime/output limits exceed the frozen budget")
    ft.verify_hash_manifest(ACCEPTED_RUN)
    out = Path(args.output_dir)
    ft.ensure_under(out, OUTPUT_ROOT)
    ensure_fresh_dir(out)
    deadline = time.time() + args.max_seconds
    cohort = ft.load_cue_cohort()
    validate_counts_exposure(cohort)
    shutil.copy2(SCRIPT_PATH, out / "code_snapshot_cebra_cue_time_readout.py")
    for path in (PROTOCOL_PATH, SOURCE_SUPPORT_PATH):
        if path.exists():
            shutil.copy2(path, out / path.name)
    write_json(out / "approval_checked.json", read_json(Path(args.approval)))
    write_json(out / "locked_config.json", approval_facts())
    write_json(
        out / "runtime_manifest.json",
        {
            "created_utc": utc_now(),
            "command": sys.argv,
            "python": sys.executable,
            "versions": ft.package_versions(),
            "git": ft.git_state(),
            "device": args.device,
            "max_seconds": args.max_seconds,
            "output_limit_gib": args.output_limit_gib,
            "use_saved_embeddings": args.use_saved_embeddings,
        },
    )
    for name in helper_hashes():
        (out / "helper_snapshots").mkdir(exist_ok=True)
        shutil.copy2(CANONICAL_ROOT / "scripts" / name, out / "helper_snapshots" / name)
    journal_path = out / "journal.jsonl"
    metrics_rows: list[dict[str, Any]] = []
    prediction_rows_all: list[dict[str, Any]] = []
    completed_new, completed_replayed = 0, 0
    for world_dir in run_world_dirs():
        for sdir in seed_dirs(world_dir):
            if time.time() > deadline:
                raise RuntimeError("run deadline exceeded")
            sf = load_seed_features(
                sdir,
                cohort,
                device=args.device,
                recompute_cebra=not args.use_saved_embeddings,
            )
            for rep in REPRESENTATIONS:
                for readout in DECODERS:
                    m, p, origin = replay_wholecue_readout(sf, rep, readout)
                    metrics_rows.extend(m)
                    prediction_rows_all.extend(p)
                    completed_replayed += 1
                    append_jsonl(
                        journal_path,
                        {
                            "event": "wholecue_replayed",
                            "world": sf.world,
                            "seed": sf.seed,
                            "representation": rep,
                            "readout": readout,
                            "state": origin,
                            "utc": utc_now(),
                        },
                    )
                    for window in BIN_WINDOWS:
                        readout_dir = (
                            out
                            / "worlds"
                            / f"{sf.world_index:02d}_{sf.world}"
                            / f"seed{sf.seed}"
                            / "readouts"
                            / rep
                            / window
                            / readout
                        )
                        append_jsonl(
                            journal_path,
                            {
                                "event": "readout_fit_started",
                                "world": sf.world,
                                "seed": sf.seed,
                                "representation": rep,
                                "window": window,
                                "readout": readout,
                                "utc": utc_now(),
                            },
                        )
                        if time.time() > deadline:
                            raise RuntimeError("run deadline exceeded")
                        try:
                            m, p, state_hash = fit_one_readout(
                                sf, rep, window, readout, readout_dir
                            )
                        except Exception as exc:
                            append_jsonl(
                                journal_path,
                                {
                                    "event": "readout_fit_failed",
                                    "world": sf.world,
                                    "seed": sf.seed,
                                    "representation": rep,
                                    "window": window,
                                    "readout": readout,
                                    "error": repr(exc),
                                    "utc": utc_now(),
                                },
                            )
                            raise
                        metrics_rows.extend(m)
                        prediction_rows_all.extend(p)
                        completed_new += 1
                        append_jsonl(
                            journal_path,
                            {
                                "event": "readout_fit_completed",
                                "world": sf.world,
                                "seed": sf.seed,
                                "representation": rep,
                                "window": window,
                                "readout": readout,
                                "state_sha256": state_hash,
                                "utc": utc_now(),
                            },
                        )
            print(
                f"{sf.world}/seed{sf.seed}: completed {completed_new} new / {completed_replayed} replayed",
                flush=True,
            )
            if ft.directory_size_bytes(out) > args.output_limit_gib * (1024**3):
                raise RuntimeError("output limit exceeded")
    if (
        completed_new != EXPECTED_NEW_BIN_READOUTS
        or completed_replayed != EXPECTED_WHOLE_REPLAYS
    ):
        raise RuntimeError(
            f"unexpected readout counts: new={completed_new} replayed={completed_replayed}"
        )
    ft.write_csv(out / "metrics.csv", metrics_rows)
    ft.write_csv_gz(
        out / "predictions.csv.gz",
        prediction_rows_all,
        fieldnames=list(prediction_rows_all[0]),
    )
    write_csv(out / "confusions_validation.csv", confusion_rows(prediction_rows_all))
    summarize_metrics(metrics_rows, out)
    observed_source_sensitivity(prediction_rows_all, out)
    ft.write_hash_manifest(out)
    print(
        json.dumps(
            {
                "run_dir": str(out),
                "new_readouts": completed_new,
                "wholecue_replays": completed_replayed,
            },
            indent=2,
            sort_keys=True,
        )
    )


def replay_run(
    run_dir: Path, *, device: str = "cpu"
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], int, int]:
    cohort = ft.load_cue_cohort()
    metrics_rows: list[dict[str, Any]] = []
    prediction_rows_all: list[dict[str, Any]] = []
    checked_new, checked_replayed = 0, 0
    for world_dir in run_world_dirs():
        for sdir in seed_dirs(world_dir):
            sf = load_seed_features(sdir, cohort, device=device, recompute_cebra=True)
            for rep in REPRESENTATIONS:
                for readout in DECODERS:
                    m, p, _origin = replay_wholecue_readout(sf, rep, readout)
                    metrics_rows.extend(m)
                    prediction_rows_all.extend(p)
                    checked_replayed += 1
                    for window in BIN_WINDOWS:
                        state_path = (
                            run_dir
                            / "worlds"
                            / f"{sf.world_index:02d}_{sf.world}"
                            / f"seed{sf.seed}"
                            / "readouts"
                            / rep
                            / window
                            / readout
                            / f"{readout}_decoder_state.npz"
                        )
                        meta_path = state_path.parent / f"{readout}_decoder_state.json"
                        meta = read_json(meta_path)
                        if sha256_file(state_path) != meta["sha256"]:
                            raise RuntimeError(
                                f"decoder state hash mismatch: {state_path}"
                            )
                        Xtr = extract_window_features(
                            rep,
                            sf.features_train[rep],
                            window,
                            cell_count=len(cohort.cell_ids),
                        )
                        Xva = extract_window_features(
                            rep,
                            sf.features_validation[rep],
                            window,
                            cell_count=len(cohort.cell_ids),
                        )
                        ptr, strn = ft.predict_decoder_state(state_path, Xtr)
                        pva, sva = ft.predict_decoder_state(state_path, Xva)
                        prefix = {
                            "world": sf.world,
                            "world_index": sf.world_index,
                            "seed": sf.seed,
                            "representation": rep,
                            "window": window,
                            "readout": readout,
                            "fit_origin": "new_single_bin_readout",
                        }
                        metrics_rows.extend(
                            [
                                metric_row(
                                    sf.train_bundle.y,
                                    ptr,
                                    strn,
                                    weights=ft.exact_class_weights(sf.train_bundle.y),
                                    readout=readout,
                                    prefix={**prefix, "split": "train"},
                                ),
                                metric_row(
                                    sf.validation_bundle.y,
                                    pva,
                                    sva,
                                    weights=sf.validation_bundle.weights,
                                    readout=readout,
                                    prefix={**prefix, "split": "validation"},
                                ),
                            ]
                        )
                        prediction_rows_all.extend(
                            prediction_rows(
                                sf.train_bundle.y,
                                ptr,
                                strn,
                                split="train",
                                readout=readout,
                                prefix=prefix,
                                plans=sf.train_bundle.plans,
                            )
                        )
                        prediction_rows_all.extend(
                            prediction_rows(
                                sf.validation_bundle.y,
                                pva,
                                sva,
                                split="validation",
                                readout=readout,
                                prefix=prefix,
                                plans=sf.validation_bundle.plans,
                            )
                        )
                        checked_new += 1
    return metrics_rows, prediction_rows_all, checked_new, checked_replayed


def cmd_verify(args: argparse.Namespace) -> None:
    run_dir = Path(args.run_dir)
    out = Path(args.output_dir)
    ensure_fresh_dir(out)
    ft.verify_hash_manifest(run_dir)
    ft.verify_hash_manifest(ACCEPTED_RUN)
    with no_fit_guard():
        metrics_rows, predictions, new_count, replay_count = replay_run(
            run_dir, device=args.device
        )
    if (new_count, replay_count, len(metrics_rows)) != (
        EXPECTED_NEW_BIN_READOUTS,
        EXPECTED_WHOLE_REPLAYS,
        EXPECTED_TOTAL_METRIC_GROUPS,
    ):
        raise RuntimeError("replay count mismatch")
    saved_metrics = ft.read_csv_rows(run_dir / "metrics.csv")
    saved_predictions = ft.read_csv_rows(run_dir / "predictions.csv.gz")
    replay_diffs = compare_window_replay(
        saved_metrics, saved_predictions, metrics_rows, predictions
    )
    summary = summarize_metrics(metrics_rows, out)
    sensitivity = observed_source_sensitivity(predictions, out)
    saved_summary = read_json(run_dir / "summary.json")
    ft.assert_equivalent(
        {k: v for k, v in saved_summary.items() if k != "created_utc"},
        {k: v for k, v in summary.items() if k != "created_utc"},
    )
    ft.assert_equivalent(
        read_json(run_dir / "source_sensitivity_summary.json"), sensitivity
    )
    write_csv(out / "confusions_validation.csv", confusion_rows(predictions))
    for filename in (
        "validation_source_deletion.csv",
        "validation_source_resamples.csv",
        "validation_source_draws.csv",
        "confusions_validation.csv",
        "wholecue_fixed_reference.csv",
        "bin_primary_family.csv",
    ):
        ft.assert_equivalent(read_csv(run_dir / filename), read_csv(out / filename))
    receipt = {
        "status": "verified",
        "replay_diffs_by_window": replay_diffs,
        "run_dir": str(run_dir),
        "new_single_bin_readouts_checked": new_count,
        "wholecue_replays_checked": replay_count,
        "source_sensitivity_summary": sensitivity,
        "created_utc": utc_now(),
    }
    write_json(out / "verification.json", receipt)
    print(json.dumps(receipt, indent=2, sort_keys=True))


def compare_window_replay(saved_metrics, saved_predictions, metrics, predictions):
    # The historical comparator keys have no window field: compare one window at a time.
    for rows in (saved_metrics, saved_predictions, metrics, predictions):
        if {r["window"] for r in rows} != set(WINDOWS):
            raise RuntimeError("saved/replayed window coverage changed")
    return {
        w: ft.compare_replay(
            *[
                [r for r in rows if r["window"] == w]
                for rows in (saved_metrics, saved_predictions, metrics, predictions)
            ]
        )
        for w in WINDOWS
    }


def fig_to_base64(path: Path) -> str:
    return base64.b64encode(path.read_bytes()).decode("ascii")


def cmd_report(args: argparse.Namespace) -> None:
    run_dir = Path(args.run_dir)
    out = Path(args.output_dir) if args.output_dir else DOC_DIR
    out.mkdir(parents=True, exist_ok=True)
    summary = read_json(run_dir / "summary.json")
    metrics = ft.read_csv_rows(run_dir / "metrics.csv")
    observed = [
        r for r in metrics if r["world"] == "observed" and r["split"] == "validation"
    ]
    fig_paths: list[Path] = []
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig_dir = out / "figures"
        fig_dir.mkdir(exist_ok=True)
        fig, ax = plt.subplots(figsize=(8, 4))
        for rep in ("cue_time", "full_time"):
            ys = []
            for window in BIN_WINDOWS:
                vals = [
                    float(r["balanced_log_loss"])
                    for r in observed
                    if r["representation"] == rep
                    and r["readout"] == "logistic"
                    and r["window"] == window
                ]
                ys.append(float(np.mean(vals)))
            ax.plot(range(10), ys, marker="o", label=rep)
        ax.axhline(ft.LOG2, color="0.5", linestyle="--", label="constant .5")
        ax.set_xlabel("cue bin (100 ms)")
        ax.set_ylabel("balanced log loss")
        ax.set_title("Observed single-bin logistic readouts")
        ax.legend()
        fig.tight_layout()
        p = fig_dir / "observed_bin_logistic_loss.png"
        fig.savefig(p, dpi=160)
        plt.close(fig)
        fig_paths.append(p)
    except Exception as exc:  # pragma: no cover
        summary["report_plot_warning"] = str(exc)
    machine_summary = {"run_dir": str(run_dir), "summary": summary}
    write_json(out / "summary.json", machine_summary)
    md = [
        "# CEBRA cue-time frozen-readout study",
        "",
        "Exploratory, historically exposed source-coherent study. Single-bin readouts are fitted only from a hash-approved run; whole-cue is a fixed saved comparator, not an eleventh selected bin.",
        "",
        f"- New single-bin readouts: {summary['counts']['new_single_bin_readouts']}",
        f"- Whole-cue saved replays: {summary['counts']['wholecue_saved_replays']}",
        f"- Primary null tail: {summary['primary_null_family']['inclusive_plus_one_tail']}",
        f"- Secondary absolute BA tail: {summary['secondary_absolute_ba_family']['inclusive_plus_one_tail']}",
        "",
    ]
    for p in fig_paths:
        md.append(f"![{p.stem}](figures/{p.name})")
    (out / "README.md").write_text("\n".join(md) + "\n")
    html_figs = "\n".join(
        f'<figure><img alt="{p.stem}" src="data:image/png;base64,{fig_to_base64(p)}"><figcaption>{p.stem}</figcaption></figure>'
        for p in fig_paths
    )
    (out / "report.html").write_text(
        f"<!doctype html><meta charset='utf-8'><title>CEBRA cue-time readout</title><h1>CEBRA cue-time frozen-readout study</h1><p>Exploratory. Whole-cue is fixed comparator; bin curves are descriptive.</p>{html_figs}<pre>{json.dumps(summary, indent=2)}</pre>\n"
    )
    print(json.dumps({"report_dir": str(out)}, indent=2, sort_keys=True))


def cmd_counts(args: argparse.Namespace) -> None:
    print(json.dumps(approval_facts()["expected_counts"], indent=2, sort_keys=True))


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    audit = sub.add_parser(
        "audit", help="no-fit source/provenance audit; does not read raw lab files"
    )
    audit.add_argument("--output-dir")
    audit.set_defaults(func=cmd_audit)
    geom = sub.add_parser(
        "geometry", help="observed-only checkpoint geometry diagnostics; no readouts"
    )
    geom.add_argument("--output-dir")
    geom.add_argument("--device", default="cpu")
    geom.set_defaults(func=cmd_geometry)
    counts = sub.add_parser("counts", help="print expected fit/replay counts")
    counts.set_defaults(func=cmd_counts)
    run = sub.add_parser(
        "run",
        help="fit approved single-bin decoders and replay saved whole-cue decoders",
    )
    run.add_argument("--approval", required=True)
    run.add_argument("--output-dir", required=True)
    run.add_argument("--device", default="cuda")
    run.add_argument("--max-seconds", type=int, default=MAX_RUN_SECONDS)
    run.add_argument("--output-limit-gib", type=float, default=RUN_OUTPUT_LIMIT_GIB)
    run.add_argument(
        "--use-saved-embeddings",
        action="store_true",
        help="use accepted cue_embeddings.npz instead of recomputing from final checkpoints",
    )
    run.set_defaults(func=cmd_run)
    verify = sub.add_parser(
        "verify", help="no-fit replay of a completed cue-time readout run"
    )
    verify.add_argument("--run-dir", required=True)
    verify.add_argument("--output-dir", required=True)
    verify.add_argument("--device", default="cpu")
    verify.set_defaults(func=cmd_verify)
    report = sub.add_parser(
        "report", help="render Markdown/HTML report from a verified run"
    )
    report.add_argument("--run-dir", required=True)
    report.add_argument("--output-dir")
    report.set_defaults(func=cmd_report)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> None:
    args = parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
