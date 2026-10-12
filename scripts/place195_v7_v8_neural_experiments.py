"""V7/V8 exploratory neural cue experiments for place195 selected component.

Runs only split-guarded train/validation rows. Test split is excluded by
SplitFilteredAccess; outputs are exploratory development artifacts.
"""

from __future__ import annotations

import argparse
import collections
import csv
import datetime as dt
import gzip
import hashlib
import json
import platform
import random
import shlex
import subprocess
import sys
import time
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    brier_score_loss,
    log_loss,
    roc_auc_score,
)
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

import scripts  # noqa: F401 — bootstrap src for legacy direct/PYTHONPATH callers
from neuro.place195_split_access import SplitFilteredAccess

LABELS = ("absent", "present")
LABEL_TO_INT = {"absent": 0, "present": 1}
INT_TO_LABEL = {0: "absent", 1: "present"}
PRIMARY_COMPONENT = "D_N_R_T__N_R_M"
PRIMARY_ENDPOINT = "4->3"
DEFAULT_SEEDS = (0, 1, 2)


@dataclass(frozen=True)
class PanelSpec:
    name: str
    min_train: int
    min_validation: int


@dataclass(frozen=True)
class SourceMeta:
    source_trial_id: str
    session_id: str
    split: str
    label: str


def open_text(path: Path):
    return (
        gzip.open(path, "rt", newline="")
        if path.suffix == ".gz"
        else path.open(newline="")
    )


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(jsonable(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [jsonable(v) for v in value]
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, Path):
        return str(value)
    return value


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git(cmd: list[str]) -> str:
    try:
        return subprocess.check_output(
            ["git", *cmd], text=True, stderr=subprocess.STDOUT
        ).strip()
    except Exception as exc:  # pragma: no cover - provenance should not kill run
        return f"unavailable: {exc}"


def load_condition_membership(path: Path) -> dict[tuple[str, str, str], list[str]]:
    out: dict[tuple[str, str, str], list[str]] = {}
    with path.open(newline="") as f:
        for row in csv.DictReader(f):
            if (
                row["selected_component_id"] != PRIMARY_COMPONENT
                or row["endpoint_pair"] != PRIMARY_ENDPOINT
            ):
                continue
            key = (row["cell_id"], row["split"], row["component_status"])
            sources = [s for s in row["source_trial_ids"].split(";") if s]
            out[key] = sources
    return out


def panel_cells(
    membership: dict[tuple[str, str, str], list[str]], min_train: int, min_val: int
) -> list[str]:
    cells = sorted({k[0] for k in membership})
    keep = []
    for cell in cells:
        ok = True
        for split, threshold in (("train", min_train), ("validation", min_val)):
            for label in LABELS:
                if len(membership.get((cell, split, label), ())) < threshold:
                    ok = False
        if ok:
            keep.append(cell)
    return keep


def session_from_cell(cell_id: str) -> str:
    parts = cell_id.split("/")
    return f"{parts[0]}_{parts[1]}"


def load_source_membership(path: Path) -> dict[str, SourceMeta]:
    out = {}
    with path.open(newline="") as f:
        for row in csv.DictReader(f):
            if (
                row["selected_component_id"] == PRIMARY_COMPONENT
                and row["endpoint_pair"] == PRIMARY_ENDPOINT
            ):
                out[row["source_trial_id"]] = SourceMeta(
                    row["source_trial_id"],
                    row["session_id"],
                    row["split"],
                    row["component_status"],
                )
    return out


def bin_events(
    events: Iterable[float], duration: float, bin_width: float, nominal: float = 1.0
) -> tuple[np.ndarray, np.ndarray, int]:
    n_bins = int(round(nominal / bin_width))
    counts = np.zeros(n_bins, dtype=np.float32)
    exposure = np.zeros(n_bins, dtype=np.float32)
    included_end = min(duration, nominal)
    for i in range(n_bins):
        start = i * bin_width
        end = start + bin_width
        exposure[i] = max(0.0, min(end, included_end) - start)
    omitted = 0
    for t in events:
        if not (0.0 <= t < duration):
            continue
        if 0.0 <= t < included_end:
            idx = int(t / bin_width)
            if 0 <= idx < n_bins:
                counts[idx] += 1.0
        elif nominal <= t < duration:
            omitted += 1
    return counts, exposure, omitted


def load_trials(
    access: SplitFilteredAccess, source_ids: set[str]
) -> dict[str, dict[str, str]]:
    return {
        r["source_trial_id"]: r
        for r in access.iter_trials()
        if r["source_trial_id"] in source_ids
    }


def load_cue_data(
    access: SplitFilteredAccess,
    source_meta: dict[str, SourceMeta],
    cell_ids: list[str],
    bin_width: float,
) -> tuple[
    np.ndarray, np.ndarray, np.ndarray, dict[str, int], list[SourceMeta], dict[str, Any]
]:
    source_ids = sorted(source_meta)
    cells = {c: i for i, c in enumerate(cell_ids)}
    sources = {s: i for i, s in enumerate(source_ids)}
    n_bins = int(round(1.0 / bin_width))
    events: dict[tuple[str, str], list[float]] = collections.defaultdict(list)
    for row in access.iter_cue_spike_events():
        sid = row["source_trial_id"]
        cid = row["cell_id"]
        if sid in sources and cid in cells:
            events[(sid, cid)].append(float(row["cue_relative_time_s"]))
    X = np.full((len(source_ids), len(cell_ids), n_bins), np.nan, dtype=np.float32)
    E = np.full((len(source_ids), n_bins), np.nan, dtype=np.float32)
    M = np.zeros((len(source_ids), len(cell_ids)), dtype=bool)
    full_count_mismatches = []
    durations = []
    omitted_after_nominal = 0
    rows_loaded = 0
    for row in access.iter_cue_counts():
        sid = row["source_trial_id"]
        cid = row["cell_id"]
        if sid not in sources or cid not in cells:
            continue
        duration = float(row["cue_window_end_ripple_s"]) - float(
            row["cue_window_start_ripple_s"]
        )
        ev = events.get((sid, cid), [])
        full_events = sum(1 for t in ev if 0.0 <= t < duration)
        cue_count = int(row["cue_spike_count"])
        if full_events != cue_count:
            full_count_mismatches.append(
                {
                    "source_trial_id": sid,
                    "cell_id": cid,
                    "events": full_events,
                    "cue_count": cue_count,
                }
            )
        counts, exposure, omitted = bin_events(ev, duration, bin_width)
        si, ci = sources[sid], cells[cid]
        X[si, ci, :] = counts
        E[si, :] = exposure
        M[si, ci] = True
        durations.append(duration)
        omitted_after_nominal += omitted
        rows_loaded += 1
    # All cells in the source's session must be observed; off-session cells remain unavailable, not zero.
    missing_same_session = []
    for sid, meta in source_meta.items():
        si = sources[sid]
        for cid, ci in cells.items():
            if session_from_cell(cid) == meta.session_id and not M[si, ci]:
                missing_same_session.append((sid, cid))
    if missing_same_session:
        raise RuntimeError(
            f"missing same-session cue counts, first={missing_same_session[:3]}"
        )
    audit = {
        "bin_width_s": bin_width,
        "n_bins": n_bins,
        "cue_count_rows_loaded": rows_loaded,
        "event_pairs_loaded": len(events),
        "full_window_event_count_mismatches": full_count_mismatches[:20],
        "full_window_event_count_mismatch_count": len(full_count_mismatches),
        "omitted_spikes_after_nominal_1s": omitted_after_nominal,
        "duration_s_summary": summary_stats(durations),
        "duration_values": durations,
        "half_open_convention": "counts include 0 <= cue_relative_time_s < min(actual_duration, nominal_1s); full conservation compared against 0 <= t < actual_duration",
    }
    return X, E, M, sources, [source_meta[s] for s in source_ids], audit


def summary_stats(values: Iterable[float]) -> dict[str, float | int | None]:
    arr = np.asarray(list(values), dtype=float)
    if arr.size == 0:
        return {"n": 0, "min": None, "median": None, "mean": None, "max": None}
    return {
        "n": int(arr.size),
        "min": float(np.min(arr)),
        "median": float(np.median(arr)),
        "mean": float(np.mean(arr)),
        "max": float(np.max(arr)),
    }


def assemble_pseudo(
    Xsrc: np.ndarray,
    Msrc: np.ndarray,
    source_index: dict[str, int],
    source_meta: list[SourceMeta],
    cell_ids: list[str],
    split: str,
    label: str,
    rows_per_class: int,
    seed: int,
    shuffled_labels: dict[str, str] | None = None,
) -> tuple[np.ndarray, list[dict[str, str]]]:
    rng = np.random.default_rng(seed)
    cell_sessions = np.array([session_from_cell(c) for c in cell_ids])
    sessions = sorted(set(cell_sessions))
    by_session: dict[str, list[str]] = {s: [] for s in sessions}
    for meta in source_meta:
        lab = (
            shuffled_labels.get(meta.source_trial_id, meta.label)
            if shuffled_labels
            else meta.label
        )
        if meta.split == split and lab == label and meta.session_id in by_session:
            by_session[meta.session_id].append(meta.source_trial_id)
    empty = [s for s, ids in by_session.items() if not ids]
    if empty:
        raise RuntimeError(f"cannot assemble {split}/{label}; empty sessions {empty}")
    n_bins = Xsrc.shape[2]
    X = np.empty((rows_per_class, len(cell_ids), n_bins), dtype=np.float32)
    manifest = []
    for r in range(rows_per_class):
        X[r, :, :] = np.nan
        for sess in sessions:
            sid = rng.choice(by_session[sess])
            si = source_index[sid]
            cidx = np.where(cell_sessions == sess)[0]
            if not np.all(Msrc[si, cidx]):
                raise RuntimeError(f"observed mask failure for {sid} {sess}")
            X[r, cidx, :] = Xsrc[si, cidx, :]
            manifest.append(
                {
                    "seed": str(seed),
                    "split": split,
                    "label": label,
                    "pseudo_row": str(r),
                    "session_id": sess,
                    "source_trial_id": sid,
                }
            )
        if np.isnan(X[r]).any():
            raise RuntimeError("pseudo row has unavailable cells; refusing imputation")
    return X, manifest


def build_dataset(
    *,
    Xsrc,
    Msrc,
    source_index,
    source_meta,
    cell_ids,
    rows_per_class,
    seed,
    shuffled_labels=None,
):
    arrays = {}
    manifests = []
    for split in ("train", "validation"):
        xs, ys = [], []
        for label in LABELS:
            X, man = assemble_pseudo(
                Xsrc,
                Msrc,
                source_index,
                source_meta,
                cell_ids,
                split,
                label,
                rows_per_class,
                seed,
                shuffled_labels,
            )
            xs.append(X)
            ys.extend([LABEL_TO_INT[label]] * rows_per_class)
            manifests.extend(man)
        arrays[split] = (np.concatenate(xs, axis=0), np.asarray(ys, dtype=np.int64))
    return arrays, manifests


def feature_matrix(
    X: np.ndarray, representation: str, bin_index: int | None = None
) -> np.ndarray:
    if representation == "raw_total":
        return X.sum(axis=2)
    if representation == "raw_binned":
        return X.reshape(X.shape[0], X.shape[1] * X.shape[2])
    if representation == "raw_bin":
        if bin_index is None:
            raise ValueError("raw_bin requires bin_index")
        return X[:, :, bin_index]
    raise ValueError(representation)


def fit_predict(
    Xtr: np.ndarray, ytr: np.ndarray, Xva: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    clf = make_pipeline(
        StandardScaler(),
        LogisticRegression(
            C=1.0,
            class_weight="balanced",
            max_iter=1000,
            solver="liblinear",
            random_state=0,
        ),
    )
    clf.fit(Xtr, ytr)
    prob = clf.predict_proba(Xva)[:, 1]
    pred = (prob >= 0.5).astype(int)
    return pred, prob


def metric_row(
    y: np.ndarray, pred: np.ndarray, prob: np.ndarray, prefix: dict[str, Any]
) -> dict[str, Any]:
    eps_prob = np.clip(prob, 1e-6, 1 - 1e-6)
    row = dict(prefix)
    row.update(
        {
            "n_validation_rows": int(len(y)),
            "accuracy": float(accuracy_score(y, pred)),
            "balanced_accuracy": float(balanced_accuracy_score(y, pred)),
            "log_loss": float(
                log_loss(y, np.c_[1 - eps_prob, eps_prob], labels=[0, 1])
            ),
            "brier": float(brier_score_loss(y, eps_prob)),
            "auroc": float(roc_auc_score(y, eps_prob))
            if len(set(y.tolist())) == 2
            else None,
        }
    )
    return row


def baseline_metrics(
    ytr: np.ndarray, yva: np.ndarray, prefix: dict[str, Any], source_train_prior: float
) -> list[dict[str, Any]]:
    synthetic_p = float(np.mean(ytr))
    rows = []
    rows.append(
        metric_row(
            yva,
            np.full_like(yva, int(synthetic_p >= 0.5)),
            np.full(len(yva), synthetic_p),
            {**prefix, "representation": "synthetic_train_prior"},
        )
    )
    rows.append(
        metric_row(
            yva,
            np.full_like(yva, int(source_train_prior >= 0.5)),
            np.full(len(yva), source_train_prior),
            {**prefix, "representation": "selected_panel_train_source_prior"},
        )
    )
    rows.append(
        metric_row(
            yva,
            np.zeros_like(yva),
            np.full(len(yva), 0.5),
            {**prefix, "representation": "constant_0p5_class_balanced_validation"},
        )
    )
    return rows


def run_decoders(
    arrays: dict[str, tuple[np.ndarray, np.ndarray]],
    panel: str,
    bin_width: float,
    seed: int,
    source_train_prior: float,
) -> tuple[
    list[dict[str, Any]], dict[str, Any], dict[str, tuple[np.ndarray, np.ndarray]]
]:
    Xtr3, ytr = arrays["train"]
    Xva3, yva = arrays["validation"]
    rows = baseline_metrics(
        ytr,
        yva,
        {"panel": panel, "bin_width_s": bin_width, "seed": seed},
        source_train_prior,
    )
    predictions = {}
    for rep in ("raw_total", "raw_binned"):
        Xtr = feature_matrix(Xtr3, rep)
        Xva = feature_matrix(Xva3, rep)
        pred, prob = fit_predict(Xtr, ytr, Xva)
        rows.append(
            metric_row(
                yva,
                pred,
                prob,
                {
                    "panel": panel,
                    "bin_width_s": bin_width,
                    "seed": seed,
                    "representation": rep,
                },
            )
        )
        predictions[rep] = (pred, prob)
    for b in range(Xtr3.shape[2]):
        pred, prob = fit_predict(
            feature_matrix(Xtr3, "raw_bin", b), ytr, feature_matrix(Xva3, "raw_bin", b)
        )
        rows.append(
            metric_row(
                yva,
                pred,
                prob,
                {
                    "panel": panel,
                    "bin_width_s": bin_width,
                    "seed": seed,
                    "representation": f"raw_bin_{b}",
                },
            )
        )
    pca_info = {}
    obs_train = np.transpose(Xtr3, (0, 2, 1)).reshape(
        Xtr3.shape[0] * Xtr3.shape[2], Xtr3.shape[1]
    )
    rank_limit = min(obs_train.shape[0] - 1, obs_train.shape[1])
    for dim in (3, 8):
        if rank_limit < dim:
            pca_info[f"pca_cellspace_{dim}"] = {
                "skipped": True,
                "rank_limit": int(rank_limit),
            }
            continue
        scaler = StandardScaler().fit(obs_train)
        pca = PCA(n_components=dim, random_state=0).fit(scaler.transform(obs_train))

        def tx(X3, *, scaler=scaler, pca=pca, dim=dim):
            obs = np.transpose(X3, (0, 2, 1)).reshape(
                X3.shape[0] * X3.shape[2], X3.shape[1]
            )
            z = pca.transform(scaler.transform(obs)).reshape(
                X3.shape[0], X3.shape[2], dim
            )
            return z.reshape(X3.shape[0], X3.shape[2] * dim)

        pred, prob = fit_predict(tx(Xtr3), ytr, tx(Xva3))
        rep = f"pca_cellspace_{dim}"
        rows.append(
            metric_row(
                yva,
                pred,
                prob,
                {
                    "panel": panel,
                    "bin_width_s": bin_width,
                    "seed": seed,
                    "representation": rep,
                },
            )
        )
        predictions[rep] = (pred, prob)
        pca_info[rep] = {
            "skipped": False,
            "explained_variance_ratio": pca.explained_variance_ratio_.tolist(),
            "components": pca.components_.astype(np.float32),
            "mean": scaler.mean_.astype(np.float32),
            "scale": scaler.scale_.astype(np.float32),
        }
    return rows, pca_info, predictions


def condition_means(
    Xsrc, source_index, source_meta, membership, cell_ids, panel_name, outdir, nulls=100
):
    cell_index = {c: i for i, c in enumerate(cell_ids)}
    means = {}
    counts = {}
    for split in ("train", "validation"):
        for label in LABELS:
            arr = np.zeros((len(cell_ids), Xsrc.shape[2]), dtype=np.float32)
            cnt = np.zeros(len(cell_ids), dtype=np.int32)
            for c in cell_ids:
                ci = cell_index[c]
                vals = []
                for sid in membership.get((c, split, label), []):
                    if sid in source_index:
                        vals.append(Xsrc[source_index[sid], ci, :])
                if vals:
                    arr[ci, :] = np.mean(vals, axis=0)
                    cnt[ci] = len(vals)
                else:
                    raise RuntimeError(
                        f"panel {panel_name} missing condition mean support {c} {split} {label}"
                    )
            means[(split, label)] = arr
            counts[(split, label)] = cnt
    train_diff = (means[("train", "present")] - means[("train", "absent")]).reshape(-1)
    val_diff = (
        means[("validation", "present")] - means[("validation", "absent")]
    ).reshape(-1)
    denom = np.linalg.norm(train_diff) * np.linalg.norm(val_diff)
    align = float(np.dot(train_diff, val_diff) / denom) if denom else None
    margin_present = float(
        np.dot(means[("validation", "present")].reshape(-1), train_diff)
    )
    margin_absent = float(
        np.dot(means[("validation", "absent")].reshape(-1), train_diff)
    )
    observed = {
        "panel": panel_name,
        "train_validation_difference_cosine": align,
        "validation_present_minus_absent_margin_on_train_diff": margin_present
        - margin_absent,
        "mean_source_counts_by_condition": {
            f"{k[0]}|{k[1]}": summary_stats(v.tolist()) for k, v in counts.items()
        },
    }
    np.savez_compressed(
        outdir / f"{panel_name}_condition_means.npz",
        **{f"{k[0]}_{k[1]}": v for k, v in means.items()},
    )
    return observed


def source_level_shuffle(source_meta: list[SourceMeta], seed: int) -> dict[str, str]:
    rng = random.Random(seed)
    grouped: dict[tuple[str, str], list[SourceMeta]] = collections.defaultdict(list)
    for m in source_meta:
        grouped[(m.split, m.session_id)].append(m)
    out = {}
    for _key, rows in grouped.items():
        labs = [m.label for m in rows]
        rng.shuffle(labs)
        for m, lab in zip(rows, labs, strict=True):
            out[m.source_trial_id] = lab
    return out


def no_replacement_ceiling(
    source_meta: list[SourceMeta], cell_ids: list[str]
) -> dict[str, Any]:
    sessions = sorted({session_from_cell(c) for c in cell_ids})
    out = {"panel_sessions": sessions, "ceilings": {}}
    for split in ("train", "validation"):
        for label in LABELS:
            vals = []
            by_s = collections.Counter(
                m.session_id
                for m in source_meta
                if m.split == split and m.label == label and m.session_id in sessions
            )
            vals = [by_s[s] for s in sessions]
            out["ceilings"][f"{split}|{label}"] = int(min(vals)) if vals else 0
    return out


def source_reuse(manifest: list[dict[str, str]]) -> dict[str, Any]:
    counts = collections.Counter(
        (m["split"], m["label"], m["source_trial_id"]) for m in manifest
    )
    by_cond: dict[str, list[int]] = collections.defaultdict(list)
    for (split, label, _sid), n in counts.items():
        by_cond[f"{split}|{label}"].append(n)
    return {
        k: {"unique_sources": len(v), "reuse_count_summary": summary_stats(v)}
        for k, v in by_cond.items()
    }


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("\n", encoding="utf-8")
        return
    fields = list(rows[0])
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow(
                {
                    k: json.dumps(v) if isinstance(v, (list, dict)) else v
                    for k, v in r.items()
                }
            )


def plot_outputs(
    outdir: Path, metrics: list[dict[str, Any]], exposure_summary: dict[str, Any]
) -> None:
    figdir = outdir / "figures"
    figdir.mkdir(exist_ok=True)
    primary = [
        r
        for r in metrics
        if r.get("panel") == "primary29_min3train_min1val"
        and r.get("bin_width_s") == 0.1
        and r.get("representation")
        in {
            "raw_total",
            "raw_binned",
            "pca_cellspace_3",
            "pca_cellspace_8",
            "synthetic_train_prior",
            "selected_panel_train_source_prior",
            "constant_0p5_class_balanced_validation",
        }
    ]
    if primary:
        labels = [f"{r['representation']}\nseed{r['seed']}" for r in primary]
        vals = [r["balanced_accuracy"] for r in primary]
        plt.figure(figsize=(max(8, len(vals) * 0.5), 4))
        plt.bar(range(len(vals)), vals)
        plt.axhline(0.5, color="k", linestyle="--", linewidth=1)
        plt.xticks(range(len(vals)), labels, rotation=75, ha="right", fontsize=7)
        plt.ylabel("validation balanced accuracy")
        plt.tight_layout()
        plt.savefig(figdir / "primary100_balanced_accuracy.png", dpi=150)
        plt.close()
    d = exposure_summary.get("primary29_min3train_min1val|0.1", {}).get(
        "duration_values", []
    )
    if d:
        plt.figure(figsize=(6, 4))
        plt.hist(d, bins=30)
        plt.axvline(1.0, color="k", linestyle="--")
        plt.xlabel("actual cue duration (s)")
        plt.ylabel("source-cell rows")
        plt.tight_layout()
        plt.savefig(figdir / "primary100_cue_duration_hist.png", dpi=150)
        plt.close()


def run(args: argparse.Namespace) -> dict[str, Any]:
    started = time.time()
    output = args.output_dir
    output.mkdir(parents=True, exist_ok=True)
    (output / "logs").mkdir(exist_ok=True)
    command = " ".join(shlex.quote(x) for x in sys.argv)
    membership_csv = (
        args.v6_dir
        / "v6c_population_membership"
        / "selected_component_condition_mean_source_membership.csv"
    )
    source_csv = (
        args.v6_dir
        / "v6c_population_membership"
        / "selected_component_source_membership.csv"
    )
    membership = load_condition_membership(membership_csv)
    source_membership_all = load_source_membership(source_csv)
    access = SplitFilteredAccess(
        args.import_dir, args.split_dir, allowed_splits=("train", "validation")
    )
    panel_specs = [
        PanelSpec("primary29_min3train_min1val", 3, 1),
        PanelSpec("relaxed40_min2train_min1val", 2, 1),
        PanelSpec("strict6_min3train_min2val", 3, 2),
    ]
    prefit = {
        "created_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "stage": "V7-V8 actual neural experiments; exploratory development validation only",
        "neural_value_access_after_this_file": True,
        "test_split_policy": "excluded via SplitFilteredAccess allowed_splits train/validation only; prior exposure incident disclosed",
        "component": PRIMARY_COMPONENT,
        "endpoint_pair": PRIMARY_ENDPOINT,
        "panels": [p.__dict__ for p in panel_specs],
        "bin_widths_s": args.bin_widths,
        "primary_bin_width_s": 0.1,
        "rows_per_class_per_split": args.rows_per_class,
        "seeds": args.seeds,
        "decoder": "StandardScaler(train only) + LogisticRegression(C=1,class_weight=balanced,solver=liblinear,random_state=0)",
        "baselines": "report constant p=0.5 for class-balanced synthetic validation separately from empirical selected-panel train-source class prior; never use all-58-session prior",
        "pca": "train-only StandardScaler and PCA over train pseudo rows x cue bins in shared cell space; dims 3 and 8 when rank permits",
        "null": f"{args.nulls} source-level within (session, split, fixed endpoint_pair={PRIMARY_ENDPOINT}) label shuffles preserving class counts; one shuffled source label applies to every cell/bin, then pseudo rows are reassembled and scaler/PCA/decoder refit",
        "attempted_rejected_settings": [
            "CEBRA fitting rejected for V7/V8 by directive; saved arrays for V9 only",
            "128 pseudo rows/class rejected; 64/class used as declared synthetic empirical benchmark, not independent N",
            "cross-endpoint pooling rejected as primary due V6 0-1 common validation sessions",
            "blind imputation rejected; unavailable source/cell entries remain NaN and pseudo assembly asserts complete same-session cells",
        ],
    }
    write_json(output / "prefit_config_before_neural_access.json", prefit)

    all_metrics: list[dict[str, Any]] = []
    all_predictions: list[dict[str, Any]] = []
    panels_summary = []
    exposure_summary: dict[str, Any] = {}
    null_rows: list[dict[str, Any]] = []
    condition_rows = []
    no_stitch_rows = []
    saved_npz = []
    for ps in panel_specs:
        cells = panel_cells(membership, ps.min_train, ps.min_validation)
        if not cells:
            panels_summary.append(
                {"panel": ps.name, "cell_count": 0, "status": "infeasible"}
            )
            continue
        allowed_sources = set()
        for c in cells:
            for split in ("train", "validation"):
                for lab in LABELS:
                    allowed_sources.update(membership[(c, split, lab)])
        source_meta = {
            sid: source_membership_all[sid]
            for sid in allowed_sources
            if sid in source_membership_all
        }
        train_labels = [m.label for m in source_meta.values() if m.split == "train"]
        source_train_prior = sum(label == "present" for label in train_labels) / len(
            train_labels
        )
        sessions = sorted({session_from_cell(c) for c in cells})
        panels_summary.append(
            {
                "panel": ps.name,
                "cell_count": len(cells),
                "session_count": len(sessions),
                "selected_panel_train_source_prior_present": source_train_prior,
                **no_replacement_ceiling(list(source_meta.values()), cells),
            }
        )
        for bw in args.bin_widths:
            stage_dir = output / ps.name / f"bin{int(round(bw * 1000))}ms"
            stage_dir.mkdir(parents=True, exist_ok=True)
            Xsrc, Esrc, Msrc, source_idx, meta_list, cue_audit = load_cue_data(
                access, source_meta, cells, bw
            )
            # Retain exact source arrays/masks for V9 and audit reuse.
            npz_path = stage_dir / "source_level_cue_tensors.npz"
            np.savez_compressed(
                npz_path,
                X_source_cell_bin=Xsrc,
                exposure_source_bin=Esrc,
                observed_source_cell_mask=Msrc,
                source_trial_ids=np.array([m.source_trial_id for m in meta_list]),
                source_session_ids=np.array([m.session_id for m in meta_list]),
                source_splits=np.array([m.split for m in meta_list]),
                source_labels=np.array([m.label for m in meta_list]),
                cell_ids=np.array(cells),
                bin_width_s=np.array([bw], dtype=np.float32),
            )
            saved_npz.append(str(npz_path))
            exposure_summary[f"{ps.name}|{bw}"] = cue_audit
            write_json(stage_dir / "cue_exposure_conservation_audit.json", cue_audit)
            cm = condition_means(
                Xsrc,
                source_idx,
                meta_list,
                membership,
                cells,
                ps.name,
                stage_dir,
                nulls=args.nulls,
            )
            cm["bin_width_s"] = bw
            condition_rows.append(cm)
            for seed in args.seeds:
                arrays, manifest = build_dataset(
                    Xsrc=Xsrc,
                    Msrc=Msrc,
                    source_index=source_idx,
                    source_meta=meta_list,
                    cell_ids=cells,
                    rows_per_class=args.rows_per_class,
                    seed=seed,
                )
                np.savez_compressed(
                    stage_dir / f"pseudo_arrays_seed{seed}.npz",
                    X_train=arrays["train"][0],
                    y_train=arrays["train"][1],
                    X_validation=arrays["validation"][0],
                    y_validation=arrays["validation"][1],
                    cell_ids=np.array(cells),
                    bin_width_s=np.array([bw], dtype=np.float32),
                )
                write_csv(stage_dir / f"pseudo_manifest_seed{seed}.csv", manifest)
                write_json(
                    stage_dir / f"source_reuse_seed{seed}.json", source_reuse(manifest)
                )
                rows, pca_info, preds = run_decoders(
                    arrays, ps.name, bw, seed, source_train_prior
                )
                all_metrics.extend(rows)
                pca_arrays = {}
                for name, info in pca_info.items():
                    if not info.get("skipped"):
                        pca_arrays[f"{name}_components"] = info["components"]
                        pca_arrays[f"{name}_mean"] = info["mean"]
                        pca_arrays[f"{name}_scale"] = info["scale"]
                        pca_arrays[f"{name}_explained_variance_ratio"] = np.asarray(
                            info["explained_variance_ratio"], dtype=np.float32
                        )
                np.savez_compressed(
                    stage_dir / f"train_only_pca_seed{seed}.npz", **pca_arrays
                )
                for rep, (pred, prob) in preds.items():
                    y = arrays["validation"][1]
                    for i, (yy, pp, pr) in enumerate(zip(y, pred, prob, strict=True)):
                        all_predictions.append(
                            {
                                "panel": ps.name,
                                "bin_width_s": bw,
                                "seed": seed,
                                "representation": rep,
                                "validation_row": i,
                                "true_label": INT_TO_LABEL[int(yy)],
                                "pred_label": INT_TO_LABEL[int(pp)],
                                "prob_present": float(pr),
                            }
                        )
            if ps.name == "primary29_min3train_min1val" and abs(bw - 0.1) < 1e-9:
                # Full-pipeline source-level nulls for primary 100 ms. Refit all downstream steps.
                for n in range(args.nulls):
                    shuffled = source_level_shuffle(meta_list, 10000 + n)
                    arrays, _manifest = build_dataset(
                        Xsrc=Xsrc,
                        Msrc=Msrc,
                        source_index=source_idx,
                        source_meta=meta_list,
                        cell_ids=cells,
                        rows_per_class=args.rows_per_class,
                        seed=0,
                        shuffled_labels=shuffled,
                    )
                    rows, _pca, _preds = run_decoders(
                        arrays,
                        ps.name,
                        bw,
                        seed=0,
                        source_train_prior=source_train_prior,
                    )
                    for r in rows:
                        if r["representation"] in {"raw_binned", "pca_cellspace_8"}:
                            rr = dict(r)
                            rr["null_index"] = n
                            rr["null_type"] = (
                                "source_label_shuffle_within_split_session"
                            )
                            null_rows.append(rr)
            # no-stitch source-level baselines: real source predictions within each panel session.
            if abs(bw - 0.1) < 1e-9:
                for sess in sessions:
                    cidx = [
                        i for i, c in enumerate(cells) if session_from_cell(c) == sess
                    ]
                    tr_sources = [
                        m
                        for m in meta_list
                        if m.session_id == sess and m.split == "train"
                    ]
                    va_sources = [
                        m
                        for m in meta_list
                        if m.session_id == sess and m.split == "validation"
                    ]
                    if {m.label for m in tr_sources} == set(LABELS) and {
                        m.label for m in va_sources
                    } == set(LABELS):
                        Xtr = np.stack(
                            [
                                Xsrc[source_idx[m.source_trial_id], cidx, :].reshape(-1)
                                for m in tr_sources
                            ]
                        )
                        ytr = np.array([LABEL_TO_INT[m.label] for m in tr_sources])
                        Xva = np.stack(
                            [
                                Xsrc[source_idx[m.source_trial_id], cidx, :].reshape(-1)
                                for m in va_sources
                            ]
                        )
                        yva = np.array([LABEL_TO_INT[m.label] for m in va_sources])
                        pred, prob = fit_predict(Xtr, ytr, Xva)
                        no_stitch_rows.append(
                            metric_row(
                                yva,
                                pred,
                                prob,
                                {
                                    "panel": ps.name,
                                    "session_id": sess,
                                    "representation": "no_stitch_session_raw_binned",
                                    "n_train_sources": len(ytr),
                                },
                            )
                        )
    write_csv(output / "metrics.csv", all_metrics)
    write_csv(output / "predictions.csv", all_predictions)
    write_json(output / "panels_and_no_replacement_ceilings.json", panels_summary)
    write_json(output / "condition_mean_metrics.json", condition_rows)
    write_csv(output / "source_level_null_metrics.csv", null_rows)
    write_csv(output / "no_stitch_session_metrics.csv", no_stitch_rows)
    write_json(output / "cue_exposure_summary.json", exposure_summary)
    plot_outputs(output, all_metrics, exposure_summary)
    summary = {
        "stage_status": "complete",
        "claim_ceiling": "exploratory development validation on sparse same-session pseudopopulation panels; synthetic rows are empirical product samples, not independent trials; no test split evaluated",
        "runtime_seconds": time.time() - started,
        "command": command,
        "input_paths": {
            "import_dir": args.import_dir,
            "split_dir": args.split_dir,
            "v6_dir": args.v6_dir,
        },
        "hashes": {
            "split_hash": access.split_hash,
            "script_sha256": sha256_file(Path(__file__)),
            "membership_sha256": sha256_file(membership_csv),
            "source_membership_sha256": sha256_file(source_csv),
            "git_head": git(["rev-parse", "HEAD"]),
            "git_status_short": git(["status", "--short"]),
        },
        "environment": {
            "python": sys.version,
            "platform": platform.platform(),
            "numpy": np.__version__,
        },
        "panels": panels_summary,
        "metrics_rows": len(all_metrics),
        "prediction_rows": len(all_predictions),
        "null_rows": len(null_rows),
        "source_tensor_npz": saved_npz,
        "split_access_audit": access.audit.as_dict(),
        "artifacts": {
            "metrics_csv": str(output / "metrics.csv"),
            "predictions_csv": str(output / "predictions.csv"),
            "condition_mean_json": str(output / "condition_mean_metrics.json"),
            "null_metrics_csv": str(output / "source_level_null_metrics.csv"),
            "handoff_md": str(output / "V7-V8-HANDOFF.md"),
        },
    }
    write_json(output / "summary.json", summary)
    write_handoff(
        output, summary, all_metrics, condition_rows, null_rows, no_stitch_rows
    )
    return summary


def best_rows(
    metrics: list[dict[str, Any]], panel="primary29_min3train_min1val", bw=0.1
) -> list[dict[str, Any]]:
    reps = {
        "synthetic_train_prior",
        "selected_panel_train_source_prior",
        "constant_0p5_class_balanced_validation",
        "raw_total",
        "raw_binned",
        "pca_cellspace_3",
        "pca_cellspace_8",
    }
    return [
        r
        for r in metrics
        if r.get("panel") == panel
        and abs(float(r.get("bin_width_s", -1)) - bw) < 1e-9
        and r.get("representation") in reps
    ]


def write_handoff(
    output_dir: Path,
    summary: dict[str, Any],
    metrics: list[dict[str, Any]],
    cm: list[dict[str, Any]],
    null_rows,
    no_stitch_rows,
) -> None:
    primary = best_rows(metrics)
    lines = [
        "# V7–V8 handoff — actual cue neural exploratory experiments",
        "",
        f"Status: **{summary['stage_status']}**. Test split excluded; prior test exposure remains disclosed.",
        "",
        "## Exact V9 reuse inputs",
    ]
    for p in summary["source_tensor_npz"]:
        lines.append(f"- `{p}`")
    lines += [
        "- pseudo arrays/manifests: `<runroot>/<panel>/bin{50,100,200}ms/pseudo_arrays_seed{0,1,2}.npz` and matching `pseudo_manifest_seed*.csv`",
        "- train-only PCA transformer arrays: `<runroot>/<panel>/bin*/train_only_pca_seed*.npz`",
        "",
        "## Primary 29-cell/7-session 100 ms metrics",
    ]
    for r in primary:
        lines.append(
            f"- seed {r['seed']} {r['representation']}: bal_acc={r['balanced_accuracy']:.3f}, acc={r['accuracy']:.3f}, logloss={r['log_loss']:.3f}, brier={r['brier']:.3f}"
        )
    lines += [
        "",
        "## Condition mean readout",
    ]
    for r in cm:
        if (
            r["panel"] == "primary29_min3train_min1val"
            and abs(float(r["bin_width_s"]) - 0.1) < 1e-9
        ):
            lines.append(
                f"- primary 100 ms train/validation difference cosine={r['train_validation_difference_cosine']}; val margin={r['validation_present_minus_absent_margin_on_train_diff']}"
            )
    lines += [
        "",
        "## Null/support limits",
        f"- source-level full-pipeline null rows: {len(null_rows)} (raw_binned and pca8 over finite permutations; resolution 1/(N+1)).",
        f"- no-stitch session heldout rows: {len(no_stitch_rows)}; low-N support control only.",
        "- Cross-endpoint pooling was not treated as tested neural evidence because V6 found only 0–1 common validation sessions for alternatives.",
        "- Do not infer independent N from synthetic pseudo rows; independent units are source trials/sessions, with same-session cells/bins sampled together.",
        "",
        "## Next command for V9 (after audit)",
        "Use the NPZ arrays above as native sampler input; fit no CEBRA from this stage output until review accepts split/mask/source manifests.",
        "",
    ]
    (output_dir / "V7-V8-HANDOFF.md").write_text("\n".join(lines), encoding="utf-8")


def parse_args(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("run", nargs="?")
    p.add_argument("--import-dir", type=Path, required=True)
    p.add_argument("--split-dir", type=Path, required=True)
    p.add_argument("--v6-dir", type=Path, required=True)
    p.add_argument("--output-dir", type=Path, required=True)
    p.add_argument("--rows-per-class", type=int, default=64)
    p.add_argument("--seeds", type=int, nargs="+", default=list(DEFAULT_SEEDS))
    p.add_argument("--bin-widths", type=float, nargs="+", default=[0.1, 0.05, 0.2])
    p.add_argument("--nulls", type=int, default=100)
    return p.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    if args.run != "run":
        raise SystemExit("usage: ... run --import-dir ...")
    summary = run(args)
    print(
        json.dumps(
            {
                "stage_status": summary["stage_status"],
                "summary": str(args.output_dir / "summary.json"),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
