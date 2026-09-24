"""Frozen saved-run atlas; numeric artifacts only, no encoder/decoder fitting.

Run as a module from the repository root in the recorded research runtime.
See docs/reports/cebra-latent-atlas-protocol-20260924.md for interpretation.
"""

from __future__ import annotations

import argparse
import base64
from collections import Counter
import csv
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
from pathlib import Path
import shutil
import subprocess
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
from scipy.spatial.distance import cdist, pdist
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "outputs/start-goal-cebra-20260907"
STUDY = ROOT / "outputs/start-goal-autoresearch-20260907"
VROOT = ROOT / "outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906"
STAGE = VROOT / "v7-v8-neural-experiments/primary29_min3train_min1val/bin100ms"
FINAL = VROOT / "v8b-v9-cebra-final-20260905T224554Z"
SPLITS = ("train", "development")
PAIRS = [(s, g) for s in range(1, 7) for g in range(1, 7) if s != g]
ENDPOINT_CASES = (
    ("positive_bin_t03", 250),
    ("positive_bin_t03", 3000),
    ("time_t1", 250),
    ("time_t1", 1000),
    ("behavior_t03", 250),
)
READS: dict[str, dict] = {}
EXPECTED: dict[Path, str] = {}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    with Path(path).open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def record(path):
    path = Path(path).resolve()
    require(
        any(path.is_relative_to(p) for p in (BASE, STUDY, VROOT)),
        "outside artifact roots",
    )
    digest = sha(path)
    if path in EXPECTED:
        require(digest == EXPECTED[path], f"historical hash mismatch: {path}")
    READS[str(path.relative_to(ROOT))] = {
        "sha256": digest,
        "historical_hash_checked": path in EXPECTED,
    }
    return path


def json_read(path):
    return json.loads(record(path).read_text())


def csv_read(path):
    with record(path).open(newline="") as handle:
        return list(csv.DictReader(handle))


def npz_read(path):
    with np.load(record(path), allow_pickle=False) as data:
        return {key: data[key] for key in data.files}


def prepare_hashes():
    for parent in (BASE, STUDY / "02-cebra"):
        receipt = json_read(parent / "artifact_hashes.json")
        for relative, digest in receipt.items():
            path = (parent / relative).resolve()
            require(path.is_relative_to(parent), "hash receipt path escapes root")
            EXPECTED[path] = digest
    manifest = json_read(STUDY / "02-cebra/manifest.json")
    for relative, digest in manifest["input_hashes"].items():
        path = (BASE / relative).resolve()
        require(path.is_relative_to(BASE), "input receipt path escapes root")
        EXPECTED[path] = digest
    EXPECTED[STAGE / "source_level_cue_tensors.npz"] = (
        "688e3b52f69a872c7aec420da99ebb6f0b80464351ded3813b077cd7ed3cf567"
    )
    config = json_read(FINAL / "prefit_config_manifest.json")
    require(
        config["primary"]["panel"] == "primary29_min3train_min1val"
        and config["primary"]["whole_cue_bins"] == 10,
        "wrong V9 source panel",
    )


def row_bins(flat, nrows, dim):
    require(flat.shape == (nrows, 10 * dim), "embedding shape/bin-order mismatch")
    require(np.isfinite(flat).all(), "nonfinite embedding")
    return flat.reshape(nrows, 10, dim).astype(float)


def source_audit(manifest, ys, lane, source_table):
    """Join explicit manifest row IDs; never assume CSV ordering or independence."""
    names = (
        [f"{s}->{g}" for s, g in PAIRS] if lane == "endpoint" else ["absent", "present"]
    )
    authority = {r["source_trial_id"]: r for r in source_table}
    require(len(authority) == len(source_table), "duplicate source authority")
    result, used, reuse = {}, {}, {}
    for split, old in zip(SPLITS, ("train", "validation"), strict=True):
        labels = ys[split]
        require(
            np.array_equal(np.unique(labels), np.arange(len(names))),
            "missing/unknown labels",
        )
        counts = Counter(labels.tolist())
        offsets = np.cumsum([0] + [counts[i] for i in range(len(names))])
        require(
            np.array_equal(
                labels,
                np.repeat(
                    np.arange(len(names)), [counts[i] for i in range(len(names))]
                ),
            ),
            "source manifests require verified class-block ordering",
        )
        rows = [{} for _ in labels]
        for r in manifest:
            if r["split"] != old:
                continue
            label = names.index(r["label"])
            index = int(r["pseudo_row"]) + (
                int(offsets[label]) if lane == "path" else 0
            )
            require(
                0 <= index < len(labels) and labels[index] == label,
                "manifest label/row mismatch",
            )
            sid, session = r["source_trial_id"], r["session_id"]
            require(session not in rows[index], "duplicate session block")
            require(sid in authority, "unregistered source")
            a = authority[sid]
            require(
                a["session_id"] == session
                and a["split"] == old
                and a["label"] == r["label"],
                "source metadata disagrees with assembly",
            )
            rows[index][session] = sid
        expected_sessions = 58 if lane == "endpoint" else 7
        require(
            all(len(r) == expected_sessions for r in rows), "incomplete session blocks"
        )
        require(all(set(r) == set(rows[0]) for r in rows), "inconsistent session panel")
        usage = Counter(sid for row in rows for sid in row.values())
        used[split] = set(usage)
        reuse[split] = np.array(
            [np.mean([usage[sid] for sid in row.values()]) for row in rows]
        )
        result[split] = {
            "pseudorows": len(rows),
            "session_blocks_per_row": expected_sessions,
            "unique_sources_used": len(usage),
            "max_source_reuse": max(usage.values()),
            "unique_source_combinations": len(
                {tuple(sorted(row.items())) for row in rows}
            ),
            "mean_source_reuse_per_row_range": [
                float(reuse[split].min()),
                float(reuse[split].max()),
            ],
        }
    require(not (used["train"] & used["development"]), "source leakage between splits")
    return result, reuse


def add_run(runs, lane, seed, name, dim, z, ys, metrics, support, reuse, note):
    for split in SPLITS:
        require(z[split].shape == (len(ys[split]), 10, dim), f"bad tensor: {name}")
        require(np.isfinite(z[split]).all(), f"nonfinite tensor: {name}")
    runs.append(
        {
            "id": f"{lane}-{name}-seed{seed}",
            "lane": lane,
            "seed": seed,
            "name": name,
            "dim": dim,
            "z": z,
            "ys": ys,
            "metrics": metrics,
            "support": support,
            "reuse": reuse,
            "note": note,
        }
    )


def endpoint_runs(runs):
    source_table = csv_read(BASE / "source_splits.csv")
    require(
        all(r["original_split"] == "train" for r in source_table),
        "original holdout in endpoint sources",
    )
    for seed in range(3):
        parent = BASE / "observed" / f"seed{seed}"
        a = npz_read(parent / "pseudo_arrays.npz")
        ys = dict(zip(SPLITS, (a["y_train"], a["y_validation"]), strict=True))
        x = dict(zip(SPLITS, (a["X_train"], a["X_validation"]), strict=True))
        require(
            x["train"].shape == (480, 195, 10)
            and x["development"].shape == (240, 195, 10),
            "unexpected endpoint cohort",
        )
        support, reuse = source_audit(
            csv_read(parent / "pseudo_components.csv"), ys, "endpoint", source_table
        )
        add_references(runs, "endpoint", seed, x, ys, support, reuse, parent)
        for case, step in ENDPOINT_CASES:
            folder = STUDY / "02-cebra" / f"{case}_seed{seed}"
            cfg = json_read(folder / "config.json")
            require(
                cfg["seed"] == seed and cfg["dim"] == 8 and not cfg["whole"],
                "wrong endpoint config",
            )
            readout = folder / f"readout{step:05d}"
            features = npz_read(readout / "embeddings.npz")
            z, metrics = {}, {}
            for split in SPLITS:
                z[split] = row_bins(features[split], len(ys[split]), 8)
                predictions = npz_read(readout / f"joint/{split}_predictions.npz")
                require(
                    np.array_equal(predictions["y"], ys[split]),
                    "readout label join failed",
                )
                metrics[split] = json_read(readout / f"joint/{split}_metrics.json")[
                    "accuracy"
                ]
            add_run(
                runs,
                "endpoint",
                seed,
                f"{case}-step{step}",
                8,
                z,
                ys,
                metrics,
                support,
                reuse,
                f"CEBRA {cfg['mode']}; tau={cfg['temperature']}; original whole-cue logistic C=.01 accuracy.",
            )


def add_references(runs, lane, seed, x, ys, support, reuse, parent):
    bins = {s: a.transpose(0, 2, 1).astype(float) for s, a in x.items()}
    training = bins["train"].reshape(-1, bins["train"].shape[-1])
    mean, scale = training.mean(axis=0), training.std(axis=0)
    scale[scale == 0] = 1
    raw = {s: (a - mean) / scale for s, a in bins.items()}
    if lane == "endpoint":
        metrics, pca = {}, {}
        for rep in ("raw_binned", "pca8"):
            d = npz_read(parent / rep / "decoder.npz")
            scores = {}
            for split, old in zip(SPLITS, ("train", "validation"), strict=True):
                require(
                    np.array_equal(d[f"y_{old}"], ys[split]), "baseline label mismatch"
                )
                scores[split] = float(
                    np.mean(d["classes"][d[f"prob_{old}"].argmax(axis=1)] == ys[split])
                )
                if rep == "pca8":
                    pca[split] = row_bins(d[f"features_{old}"], len(ys[split]), 8)
                else:
                    require(
                        np.array_equal(
                            d[f"features_{old}"], x[split].reshape(len(x[split]), -1)
                        ),
                        "raw feature correspondence failed",
                    )
            metrics[rep] = scores
        note = "Original baseline whole-cue logistic C=1 accuracy (not the later C=.01 readout)."
    else:
        saved = npz_read(STAGE / f"train_only_pca_seed{seed}.npz")
        prefix = "pca_cellspace_8_"
        pca = {
            s: ((a - saved[prefix + "mean"]) / saved[prefix + "scale"])
            @ saved[prefix + "components"].T
            for s, a in bins.items()
        }
        center = pca["train"].reshape(-1, 8).mean(axis=0)
        pca = {s: a - center for s, a in pca.items()}
        rows = csv_read(FINAL / "v8b/v8b_v9_same_array_comparator_baselines.csv")
        metrics = {}
        for rep, key in (("raw_binned", "raw_binned"), ("pca8", "pca_cellspace_8")):
            metrics[rep] = {}
            for split, old in zip(SPLITS, ("train", "validation"), strict=True):
                match = [
                    r
                    for r in rows
                    if int(r["seed"]) == seed
                    and r["representation"] == key
                    and r["split"] == old
                ]
                require(len(match) == 1, "ambiguous baseline score")
                metrics[rep][split] = float(match[0]["balanced_accuracy"])
        note = "Original C=1 whole-cue balanced accuracy. PCA uses saved float32 directions, training-recentered; not bitwise replay."
    add_run(
        runs,
        lane,
        seed,
        "raw",
        training.shape[1],
        raw,
        ys,
        metrics["raw_binned"],
        support,
        reuse,
        "Raw counts, training-standardized per cell for display; decoder uses its own feature scaling. "
        + note,
    )
    add_run(
        runs,
        lane,
        seed,
        "pca8",
        8,
        pca,
        ys,
        metrics["pca8"],
        support,
        reuse,
        "One saved pooled-training-bin PCA basis (not a different basis per bin). "
        + note,
    )


def path_runs(runs):
    source = npz_read(STAGE / "source_level_cue_tensors.npz")
    source_table = [
        {
            "source_trial_id": str(i),
            "session_id": str(s),
            "split": str(t),
            "label": str(y),
        }
        for i, s, t, y in zip(
            source["source_trial_ids"],
            source["source_session_ids"],
            source["source_splits"],
            source["source_labels"],
            strict=True,
        )
    ]
    rows = csv_read(FINAL / "v9/v9_cebra_metrics.csv")
    for seed in range(3):
        a = npz_read(STAGE / f"pseudo_arrays_seed{seed}.npz")
        ys = dict(zip(SPLITS, (a["y_train"], a["y_validation"]), strict=True))
        x = dict(zip(SPLITS, (a["X_train"], a["X_validation"]), strict=True))
        require(all(v.shape == (128, 29, 10) for v in x.values()), "wrong path cohort")
        support, reuse = source_audit(
            csv_read(STAGE / f"pseudo_manifest_seed{seed}.csv"),
            ys,
            "path",
            source_table,
        )
        add_references(runs, "path", seed, x, ys, support, reuse, STAGE)
        for variant in ("cebra_time", "cebra_behavior"):
            for dim in (3, 8):
                folder = FINAL / f"v9/observed/{variant}/dim{dim}/seed{seed}"
                d = npz_read(folder / "embeddings_and_decoder.npz")
                z, metrics = {}, {}
                for split, old in zip(SPLITS, ("train", "validation"), strict=True):
                    require(
                        np.array_equal(d[f"y_{old}"], ys[split]),
                        "V9 labels disagree with source rows",
                    )
                    z[split] = row_bins(d[f"Z_{old}"], len(ys[split]), dim)
                    match = [
                        r
                        for r in rows
                        if r["representation"] == variant
                        and int(r["dim"]) == dim
                        and int(r["seed"]) == seed
                        and r["split"] == old
                    ]
                    require(len(match) == 1, "ambiguous V9 metric")
                    metrics[split] = float(match[0]["balanced_accuracy"])
                add_run(
                    runs,
                    "path",
                    seed,
                    f"{variant}-dim{dim}",
                    dim,
                    z,
                    ys,
                    metrics,
                    support,
                    reuse,
                    "V9 final 1000 steps; tau=1; original C=1 whole-cue balanced accuracy. Endpoint fixed at 4->3.",
                )


def spectrum(x):
    power = np.linalg.svd(x - x.mean(axis=0), compute_uv=False) ** 2
    total = power.sum()
    if total <= np.finfo(float).eps:
        return {
            "fractions": [],
            "participation_ratio": None,
            "norm_mean": float(np.linalg.norm(x, axis=1).mean()),
        }
    fractions = power / total
    return {
        "fractions": fractions.tolist(),
        "participation_ratio": float(1 / (fractions @ fractions)),
        "norm_mean": float(np.linalg.norm(x, axis=1).mean()),
    }


def display_projection(training, development, native=False):
    require(
        training.ndim == development.ndim == 2
        and training.shape[1] == development.shape[1],
        "projection shape",
    )
    require(
        training.shape[1] >= 3
        and np.isfinite(training).all()
        and np.isfinite(development).all(),
        "projection values",
    )
    mean = training.mean(axis=0)
    if native:
        require(training.shape[1] == 3, "native display requires three dimensions")
        basis = np.eye(3)
        # Keep native CEBRA axes/origin; center only for retention measurement.
        shown = (training.copy(), development.copy())
    else:
        _, _, vt = np.linalg.svd(training - mean, full_matrices=False)
        basis = vt[:3].T
        shown = ((training - mean) @ basis, (development - mean) @ basis)
    retention = []
    for x in (training, development):
        centered = x - mean
        total = float(np.sum(centered**2))
        retention.append(
            float(np.sum((centered @ basis) ** 2) / total) if total > 1e-15 else None
        )
    return mean, basis, shown, retention


def rank_correlation(a, b):
    if len(a) < 3 or np.ptp(a) == 0 or np.ptp(b) == 0:
        return None
    return np.asarray(spearmanr(a, b)[0], dtype=float).item()


def sample_rows(y):
    rng = np.random.default_rng(20260924)
    groups = np.unique(y)
    take = max(1, 64 // len(groups))
    return np.sort(
        np.concatenate(
            [
                rng.choice(
                    np.flatnonzero(y == c), min(take, np.sum(y == c)), replace=False
                )
                for c in groups
            ]
        )
    )


def fidelity(full, view, row_ids, k=10):
    d, p = cdist(full, full), cdist(view, view)
    allowed = row_ids[:, None] != row_ids[None, :]
    upper = np.triu(allowed, 1)
    require(allowed.sum(axis=1).min() > k, "too few cross-row neighbors")
    dv, pv = d[upper], p[upper]
    d[~allowed] = p[~allowed] = np.inf
    near_d, near_p = (
        np.argsort(d, axis=1, kind="stable")[:, :k],
        np.argsort(p, axis=1, kind="stable")[:, :k],
    )
    overlap = np.mean(
        [len(set(a) & set(b)) / k for a, b in zip(near_d, near_p, strict=True)]
    )
    # ponytail: fixed-size diagnostic sample bounds pairwise memory; not source-independent inference.
    return {
        "distance_spearman": rank_correlation(dv, pv),
        "knn10_overlap": float(overlap) if np.ptp(dv) > 0 and np.ptp(pv) > 0 else None,
        "sample_points": len(full),
        "sample_rows": len(np.unique(row_ids)),
        "zero_distance_pair_fraction": float(np.mean(dv < 1e-12)),
        "k_boundary_tie_fraction": float(
            np.mean(np.sort(d, axis=1)[:, k - 1] == np.sort(d, axis=1)[:, k])
        ),
    }


def condition_rdm(x, y, space):
    classes = np.unique(y)
    if len(classes) < 3:
        return None
    means = np.stack([x[y == c].mean(axis=0) for c in classes])
    if space == "bin":
        return np.concatenate([pdist(means[:, b, :]) for b in range(10)])
    return pdist(means.reshape(len(classes), -1))


def analyze_run(run, out):
    output = {
        k: run[k]
        for k in ("id", "lane", "seed", "name", "dim", "metrics", "support", "note")
    }
    output["spaces"] = {}
    transforms = {}
    for space in ("bin", "whole"):
        arrays = {
            s: z.reshape(-1, run["dim"]) if space == "bin" else z.reshape(len(z), -1)
            for s, z in run["z"].items()
        }
        native = space == "bin" and run["dim"] == 3 and run["name"].startswith("cebra_")
        mean, basis, views, energy = display_projection(
            arrays["train"], arrays["development"], native
        )
        info = {
            "projection": "native latent 1–3"
            if native
            else "training-fitted display PC1–3",
            "ambient_dimension": arrays["train"].shape[1],
            "splits": {},
        }
        transforms[f"{space}_mean"] = mean
        transforms[f"{space}_basis"] = basis
        for idx, split in enumerate(SPLITS):
            labels, full, view = run["ys"][split], arrays[split], views[idx]
            chosen = sample_rows(labels)
            flat_indices = (
                (chosen[:, None] * 10 + np.arange(10)).ravel()
                if space == "bin"
                else chosen
            )
            all_rows = (
                np.repeat(np.arange(len(labels)), 10)
                if space == "bin"
                else np.arange(len(labels))
            )
            stat = spectrum(full)
            if (
                run["name"].startswith(("cebra_", "positive_", "time_", "behavior_"))
                and space == "bin"
            ):
                require(
                    np.allclose(np.linalg.norm(full, axis=1), 1, atol=1e-5),
                    "CEBRA normalization mismatch",
                )
            stat.update(
                fidelity(full[flat_indices], view[flat_indices], all_rows[flat_indices])
            )
            stat["retained_energy_training_center"] = energy[idx]
            info["splits"][split] = stat
            transforms[f"{space}_{split}"] = view
        rdm = {s: condition_rdm(run["z"][s], run["ys"][s], space) for s in SPLITS}
        info["train_development_condition_rdm_spearman"] = (
            None
            if rdm["train"] is None
            else rank_correlation(rdm["train"], rdm["development"])
        )
        info["rdm_note"] = (
            "Descriptive within-bin condition distances; no pairwise independence."
            if space == "bin"
            else "Descriptive whole-cue condition distances."
        )
        if rdm["train"] is None:
            info["rdm_note"] = (
                "Not estimated: binary target provides fewer than three condition centroids."
            )
        output["spaces"][space] = info
    np.savez_compressed(out / "projections" / f"{run['id']}.npz", **transforms)
    run["views"] = transforms
    run["summary"] = output
    return output


def seed_consistency(runs):
    results = []
    for name in sorted({r["name"] for r in runs if r["lane"] == "endpoint"}):
        group = sorted(
            [r for r in runs if r["lane"] == "endpoint" and r["name"] == name],
            key=lambda r: r["seed"],
        )
        for space in ("bin", "whole"):
            for split in SPLITS:
                for i in range(3):
                    for j in range(i + 1, 3):
                        a, b = group[i], group[j]
                        results.append(
                            {
                                "name": name,
                                "space": space,
                                "split": split,
                                "seeds": [i, j],
                                "spearman": rank_correlation(
                                    condition_rdm(a["z"][split], a["ys"][split], space),
                                    condition_rdm(b["z"][split], b["ys"][split], space),
                                ),
                            }
                        )
    return results


def spectrum_figure(runs, out):
    fig, axes = plt.subplots(3, 2, figsize=(15, 12), constrained_layout=True)
    for col, lane in enumerate(("endpoint", "path")):
        for seed in range(3):
            ax = axes[seed, col]
            for run in (r for r in runs if r["lane"] == lane and r["seed"] == seed):
                fractions = run["summary"]["spaces"]["bin"]["splits"]["development"][
                    "fractions"
                ]
                cumulative = np.cumsum(fractions[:16])
                ax.plot(
                    np.arange(1, len(cumulative) + 1),
                    cumulative,
                    marker=".",
                    label=run["name"],
                )
            ax.set_title(f"{lane}, seed {seed}: development bin-space spectrum")
            ax.set_xlabel("Linear component (at most first 16 shown)")
            ax.set_ylabel("Cumulative variance fraction")
            ax.set_ylim(0, 1.02)
            ax.grid(alpha=0.2)
            if seed == 0:
                ax.legend(fontsize=7)
    fig.suptitle(
        "Separate descriptive development spectra — not training-fitted projection retention or intrinsic dimension"
    )
    file = out / "spectra.png"
    fig.savefig(file, dpi=140)
    plt.close(fig)
    return file


def static_figures(runs, out):
    files = []
    families = {
        "endpoint": [
            "raw",
            "pca8",
            "time_t1-step250",
            "behavior_t03-step250",
            "positive_bin_t03-step250",
        ],
        "path": [
            "raw",
            "pca8",
            "cebra_time-dim3",
            "cebra_time-dim8",
            "cebra_behavior-dim8",
        ],
    }
    for lane, names in families.items():
        for native in (False, True):
            fig, axes = plt.subplots(
                3, len(names), figsize=(16, 9), squeeze=False, constrained_layout=True
            )
            for row in range(3):
                for col, name in enumerate(names):
                    run = next(
                        r
                        for r in runs
                        if r["lane"] == lane and r["name"] == name and r["seed"] == row
                    )
                    xy = (
                        run["z"]["development"].reshape(-1, run["dim"])[:, :2]
                        if native
                        else run["views"]["bin_development"][:, :2]
                    )
                    y = run["ys"]["development"]
                    colors = np.repeat(
                        np.array(PAIRS)[y, 1] if lane == "endpoint" else y, 10
                    )
                    ax = axes[row, col]
                    ax.scatter(
                        xy[:, 0],
                        xy[:, 1],
                        c=colors,
                        cmap="tab10",
                        vmin=0,
                        vmax=9,
                        s=2,
                        alpha=0.35,
                        rasterized=True,
                    )
                    ax.set_title(f"{name}\nseed {row}", fontsize=9)
                    ax.set_aspect("equal", adjustable="datalim")
                    ax.set_xlabel("coordinate 1" if native else "display axis 1")
                    ax.set_ylabel("coordinate 2" if native else "display axis 2")
            mode = (
                "fixed first two feature coordinates"
                if native
                else "first two axes of training-fitted/native 3D view"
            )
            fig.suptitle(
                f"{lane}: development cue-bin clouds — {mode}\nSynthetic rows; axes not aligned across fits. Color legend below."
            )
            categories = (
                [(i, f"goal {i}") for i in range(1, 7)]
                if lane == "endpoint"
                else [(0, "absent"), (1, "present")]
            )
            handles = [
                Line2D(
                    [],
                    [],
                    marker="o",
                    linestyle="none",
                    color=plt.get_cmap("tab10")(i / 9),
                    label=label,
                )
                for i, label in categories
            ]
            fig.legend(
                handles=handles, loc="outside lower center", ncol=len(categories)
            )
            file = out / f"{lane}-{'native-pairs' if native else 'projection'}.png"
            fig.savefig(file, dpi=140)
            plt.close(fig)
            files.append(file)
    fig, axes = plt.subplots(1, 2, figsize=(15, 12), constrained_layout=True)
    for ax, lane in zip(axes, ("endpoint", "path"), strict=True):
        subset = [r for r in runs if r["lane"] == lane]
        for split, marker in (("train", "o"), ("development", "x")):
            vals = [
                r["summary"]["spaces"]["bin"]["splits"][split][
                    "retained_energy_training_center"
                ]
                for r in subset
            ]
            ax.scatter(vals, range(len(vals)), label=split, marker=marker)
        ax.set_yticks(
            range(len(subset)),
            [r["id"].removeprefix(lane + "-") for r in subset],
            fontsize=8,
        )
        ax.invert_yaxis()
        ax.set_xlim(0, 1.02)
        ax.set_xlabel("3D retained energy, relative to training center")
        ax.set_title(lane)
        ax.legend()
        ax.grid(alpha=0.2)
    file = out / "projection-retention.png"
    fig.savefig(file, dpi=140)
    plt.close(fig)
    files.append(file)
    files.append(spectrum_figure(runs, out))
    return files


def write_html(runs, summary, figures, out):
    payload = []
    for r in runs:
        views = {}
        for split in SPLITS:
            views[split] = {
                "labels": r["ys"][split].tolist(),
                "reuse": r["reuse"][split].round(2).tolist(),
                "bin": r["views"][f"bin_{split}"].round(5).tolist(),
                "whole": r["views"][f"whole_{split}"].round(5).tolist(),
                "coordinates": r["z"][split]
                .reshape(-1, r["dim"])[:, :3]
                .round(5)
                .tolist(),
            }
        payload.append({**r["summary"], "views": views})
    template = (ROOT / "scripts/cebra_latent_atlas.html").read_text()
    data = json.dumps(
        {"runs": payload, "seeds": summary["seed_consistency"], "pairs": PAIRS},
        separators=(",", ":"),
        allow_nan=False,
    )
    data = (
        data.replace("<", "\\u003c")
        .replace("\u2028", "\\u2028")
        .replace("\u2029", "\\u2029")
    )
    images = "".join(
        f'<figure><img alt="{p.stem} — descriptive geometry, not a biological manifold test" src="data:image/png;base64,{base64.b64encode(p.read_bytes()).decode()}"/><figcaption>{p.stem}</figcaption></figure>'
        for p in figures
    )
    (out / "atlas.html").write_text(
        template.replace("@@DATA@@", data).replace("@@FIGURES@@", images)
    )


def verify_output(out):
    manifest = json.loads((out / "manifest.json").read_text())
    for relative, digest in manifest["outputs"].items():
        path = (out / relative).resolve()
        require(
            path.is_relative_to(out) and sha(path) == digest,
            f"output hash mismatch: {relative}",
        )
    for relative, info in manifest["inputs"].items():
        path = (ROOT / relative).resolve()
        require(
            path.is_relative_to(ROOT) and sha(path) == info["sha256"],
            f"input hash mismatch: {relative}",
        )
    prepare_hashes()
    runs: list[dict] = []
    endpoint_runs(runs)
    path_runs(runs)
    summary = json.loads((out / "summary.json").read_text())
    require(summary["run_count"] == len(runs) == 39, "verification run count")
    comparisons = 0
    for run, result in zip(runs, summary["runs"], strict=True):
        require(run["id"] == result["id"], "verification run identity")
        with np.load(out / "projections" / f"{run['id']}.npz", allow_pickle=False) as z:
            for space in ("bin", "whole"):
                mean, basis = z[f"{space}_mean"], z[f"{space}_basis"]
                require(
                    np.allclose(basis.T @ basis, np.eye(3), atol=1e-10),
                    "nonorthogonal display basis",
                )
                for split in SPLITS:
                    x = run["z"][split]
                    x = (
                        x.reshape(-1, run["dim"])
                        if space == "bin"
                        else x.reshape(len(x), -1)
                    )
                    native = result["spaces"][space]["projection"].startswith("native")
                    predicted = x if native else (x - mean) @ basis
                    require(
                        np.allclose(
                            predicted, z[f"{space}_{split}"], atol=1e-10, rtol=1e-10
                        ),
                        "projection replay differs",
                    )
                    energy = np.sum(((x - mean) @ basis) ** 2) / np.sum((x - mean) ** 2)
                    require(
                        np.isclose(
                            energy,
                            result["spaces"][space]["splits"][split][
                                "retained_energy_training_center"
                            ],
                            atol=1e-10,
                        ),
                        "retention replay differs",
                    )
                    comparisons += 1
    receipt = {
        "status": "passed",
        "input_hashes": len(manifest["inputs"]),
        "output_hashes": len(manifest["outputs"]),
        "forward_projection_checks": comparisons,
        "encoder_fits": 0,
        "decoder_fits": 0,
        "display_pca_refits": 0,
        "scope": "Hashes and forward projection/retention; not an independent replay of every geometry statistic.",
    }
    (out / "verification.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Forward replay stored projections without PCA refitting",
    )
    args = parser.parse_args()
    out = args.output.resolve()
    require(out.is_relative_to(ROOT / "outputs"), "output must be under outputs/")
    if args.verify:
        verify_output(out)
        return
    require(not out.exists(), "output must be a fresh directory")
    out.mkdir(parents=True)
    (out / "projections").mkdir()
    prepare_hashes()
    runs: list[dict] = []
    endpoint_runs(runs)
    path_runs(runs)
    require(len(runs) == 39, "frozen run count changed")
    summary = {
        "status": "exploratory",
        "encoder_fits": 0,
        "decoder_fits": 0,
        "checkpoint_loads": 0,
        "display_projections_training_only": True,
        "run_count": len(runs),
        "runs": [],
    }
    for r in runs:
        print(r["id"], flush=True)
        summary["runs"].append(analyze_run(r, out))
    summary["seed_consistency"] = seed_consistency(runs)
    figures = static_figures(runs, out)
    write_html(runs, summary, figures, out)
    (out / "summary.json").write_text(
        json.dumps(summary, indent=2, allow_nan=False) + "\n"
    )
    code = [
        ROOT / "scripts" / f
        for f in (
            "cebra_latent_atlas.py",
            "cebra_latent_atlas.html",
            "test_cebra_latent_atlas.py",
        )
    ]
    code.append(ROOT / "docs/reports/cebra-latent-atlas-protocol-20260924.md")
    (out / "code").mkdir()
    for path in code:
        shutil.copyfile(path, out / "code" / path.name)
    manifest = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "command": sys.argv,
        "git": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "dirty": subprocess.check_output(
            ["git", "status", "--short"], cwd=ROOT, text=True
        ),
        "python": sys.version,
        "executable": sys.executable,
        "device": "CPU",
        "random_seed": 20260924,
        "packages": {
            p: importlib.metadata.version(p) for p in ("numpy", "scipy", "matplotlib")
        },
        "inputs": READS,
        "code": {str(p.relative_to(ROOT)): sha(p) for p in code},
        "outputs": {
            str(p.relative_to(out)): sha(p)
            for p in sorted(out.rglob("*"))
            if p.is_file()
        },
        "limitations": "No new source split, topology/null test, biological independence, or checkpoint replay.",
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"Wrote {out / 'atlas.html'}", flush=True)


if __name__ == "__main__":
    main()
