# pyright: reportMissingImports=false, reportUnknownMemberType=false, reportUnknownVariableType=false
"""V8b saved-array diagnostics and V9 native CEBRA runs.

Uses only audited V7/V8 saved arrays; no raw tables and no test split access.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import platform
import random
import shlex
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import cebra
import cebra.data
import cebra.models
import cebra.solver
import numpy as np
import torch
from cebra.data import BatchIndex, Offset
from cebra.data.single_session import DiscreteDataLoader, SingleSessionDataset
from cebra.models import FixedCosineInfoNCE
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    brier_score_loss,
    log_loss,
    roc_auc_score,
)
from sklearn.preprocessing import StandardScaler

from scripts.place195_v7_v8_neural_experiments import (
    INT_TO_LABEL,
    LABELS,
    SourceMeta,
    build_dataset,
    session_from_cell,
    source_level_shuffle,
)

PANEL = "primary29_min3train_min1val"
BIN_DIR = "bin100ms"
VARIANTS = ("cebra_time", "cebra_behavior")
DIMS = (3, 8)
SEEDS = (0, 1, 2)
CS = (1.0, 0.1, 0.01)
REPRS = ("raw_total", "raw_binned", "raw_bin", "pca_cellspace")


def jsonable(x: Any) -> Any:
    if isinstance(x, dict):
        return {str(k): jsonable(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [jsonable(v) for v in x]
    if isinstance(x, np.ndarray):
        return x.tolist()
    if isinstance(x, (np.integer,)):
        return int(x)
    if isinstance(x, (np.floating,)):
        return float(x)
    if isinstance(x, Path):
        return str(x)
    return x


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(jsonable(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    keys: list[str] = []
    for row in rows:
        for k in row:
            if k not in keys:
                keys.append(k)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def git(cmd: list[str]) -> str:
    try:
        return subprocess.check_output(["git", *cmd], text=True, stderr=subprocess.STDOUT).strip()
    except Exception as exc:  # pragma: no cover - provenance best effort
        return f"ERROR: {exc}"


def load_source_npz(stage_dir: Path) -> tuple[np.lib.npyio.NpzFile, list[SourceMeta], dict[str, int], list[str]]:
    z = np.load(stage_dir / "source_level_cue_tensors.npz")
    metas = [
        SourceMeta(str(sid), str(sess), str(split), str(label))
        for sid, sess, split, label in zip(
            z["source_trial_ids"], z["source_session_ids"], z["source_splits"], z["source_labels"], strict=True
        )
    ]
    source_index = {m.source_trial_id: i for i, m in enumerate(metas)}
    return z, metas, source_index, [str(c) for c in z["cell_ids"]]


def feature(X: np.ndarray, representation: str, *, bin_index: int | None = None, pca_dim: int | None = None, scaler=None, pca=None):
    if representation == "raw_total":
        return X.sum(axis=2)
    if representation == "raw_binned":
        return X.reshape(X.shape[0], -1)
    if representation == "raw_bin":
        if bin_index is None:
            raise ValueError("bin_index is required for raw_bin")
        return X[:, :, bin_index]
    if representation == "pca_cellspace":
        if pca_dim is None:
            raise ValueError("pca_dim is required for pca_cellspace")
        flat = X.transpose(0, 2, 1).reshape(-1, X.shape[1])
        if scaler is None:
            scaler = StandardScaler().fit(flat)
            pca = PCA(n_components=pca_dim, random_state=0).fit(scaler.transform(flat))
        Z = pca.transform(scaler.transform(flat)).reshape(X.shape[0], X.shape[2], pca_dim)
        return Z.reshape(X.shape[0], -1), scaler, pca
    raise ValueError(representation)


def metrics(y: np.ndarray, pred: np.ndarray, prob: np.ndarray, prefix: dict[str, Any]) -> dict[str, Any]:
    out = dict(prefix)
    out.update(
        n=len(y),
        accuracy=float(accuracy_score(y, pred)),
        balanced_accuracy=float(balanced_accuracy_score(y, pred)),
        log_loss=float(log_loss(y, np.c_[1 - prob, prob], labels=[0, 1])),
        brier=float(brier_score_loss(y, prob)),
        positive_rate_true=float(np.mean(y)),
        positive_rate_pred=float(np.mean(pred)),
    )
    out["auroc"] = float(roc_auc_score(y, prob)) if len(set(map(int, y))) == 2 else None
    return out


def fit_logreg(Xtr, ytr, Xva, *, C: float):
    scaler = StandardScaler().fit(Xtr)
    clf = LogisticRegression(C=C, class_weight="balanced", solver="liblinear", random_state=0, max_iter=1000).fit(scaler.transform(Xtr), ytr)
    Ptr = clf.predict_proba(scaler.transform(Xtr))[:, 1]
    Pva = clf.predict_proba(scaler.transform(Xva))[:, 1]
    return clf.predict(scaler.transform(Xtr)), Ptr, clf.predict(scaler.transform(Xva)), Pva, clf, scaler


def source_prior_from_npz(stage_dir: Path) -> float:
    _z, metas, _source_index, _cells = load_source_npz(stage_dir)
    train = [m.label for m in metas if m.split == "train"]
    return sum(x == "present" for x in train) / len(train)


def baseline_metric_rows(stage_dir: Path, outdir: Path, c1_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    wanted = {"raw_total", "raw_binned", "pca_cellspace_3", "pca_cellspace_8"}
    for r in c1_rows:
        if r.get("C") == 1.0 and r.get("representation") in wanted:
            rr = dict(r)
            rr["table"] = "same_array_comparator"
            rows.append(rr)
    prior = source_prior_from_npz(stage_dir)
    for seed in SEEDS:
        z = np.load(stage_dir / f"pseudo_arrays_seed{seed}.npz")
        for split, y in (("train", z["y_train"]), ("validation", z["y_validation"])):
            for name, prob in (("constant_p0_5", 0.5), ("selected_panel_train_source_prior", prior)):
                p = np.full(len(y), prob, dtype=float)
                pred = (p >= 0.5).astype(int)
                rows.append(metrics(y, pred, p, {"table": "same_array_baseline", "stage": "v8b_v9_comparator", "seed": seed, "representation": name, "C": None, "split": split}))
    write_csv(outdir / "v8b_v9_same_array_comparator_baselines.csv", rows)
    return rows


def v8b_regularization(stage_dir: Path, outdir: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    rows: list[dict[str, Any]] = []
    pred_rows: list[dict[str, Any]] = []
    coef_dir = outdir / "coefs"
    coef_dir.mkdir(parents=True, exist_ok=True)
    for seed in SEEDS:
        z = np.load(stage_dir / f"pseudo_arrays_seed{seed}.npz")
        Xtr, ytr, Xva, yva = z["X_train"], z["y_train"], z["X_validation"], z["y_validation"]
        built: list[tuple[str, Any, Any, dict[str, Any]]] = [
            ("raw_total", feature(Xtr, "raw_total"), feature(Xva, "raw_total"), {}),
            ("raw_binned", feature(Xtr, "raw_binned"), feature(Xva, "raw_binned"), {}),
        ]
        for b in range(Xtr.shape[2]):
            built.append((f"raw_bin_{b}", feature(Xtr, "raw_bin", bin_index=b), feature(Xva, "raw_bin", bin_index=b), {"bin_index": b}))
        for dim in (3, 8):
            Ftr, sc, pca = feature(Xtr, "pca_cellspace", pca_dim=dim)
            Fva, _, _ = feature(Xva, "pca_cellspace", pca_dim=dim, scaler=sc, pca=pca)
            built.append((f"pca_cellspace_{dim}", Ftr, Fva, {"pca_dim": dim, "pca_explained_variance_sum": float(np.sum(pca.explained_variance_ratio_))}))
        for rep, Ftr, Fva, extra in built:
            for C in CS:
                ptr, pptr, pva, ppva, clf, scaler = fit_logreg(Ftr, ytr, Fva, C=C)
                prefix = {"stage": "v8b_C_sensitivity", "seed": seed, "representation": rep, "C": C, **extra}
                rows.append(metrics(ytr, ptr, pptr, {**prefix, "split": "train", "n_iter": int(clf.n_iter_[0])}))
                rows.append(metrics(yva, pva, ppva, {**prefix, "split": "validation", "n_iter": int(clf.n_iter_[0])}))
                np.savez_compressed(coef_dir / f"seed{seed}_{rep}_C{C:g}.npz", coef=clf.coef_, intercept=clf.intercept_, scaler_mean=scaler.mean_, scaler_scale=scaler.scale_)
                for split, y, pred, prob in (("train", ytr, ptr, pptr), ("validation", yva, pva, ppva)):
                    for i, (yy, pp, pr) in enumerate(zip(y, pred, prob, strict=True)):
                        pred_rows.append({"seed": seed, "representation": rep, "C": C, "split": split, "row": i, "true_label": INT_TO_LABEL[int(yy)], "pred_label": INT_TO_LABEL[int(pp)], "prob_present": float(pr)})
    write_csv(outdir / "v8b_regularization_metrics.csv", rows)
    write_csv(outdir / "v8b_regularization_predictions.csv", pred_rows)
    return rows, pred_rows


def manifest_source_components(stage_dir: Path, seed: int, split: str) -> dict[int, str]:
    out: dict[int, list[str]] = {}
    with (stage_dir / f"pseudo_manifest_seed{seed}.csv").open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["split"] != split:
                continue
            offset = 0 if row["label"] == LABELS[0] else 64
            array_row = offset + int(row["pseudo_row"])
            out.setdefault(array_row, []).append(f"{row['session_id']}:{row['source_trial_id']}")
    return {k: "|".join(v) for k, v in sorted(out.items())}


def v8b_bin2_margins_and_ablation(stage_dir: Path, outdir: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    _z, _metas, _source_index, cells = load_source_npz(stage_dir)
    cell_sessions = np.array([session_from_cell(c) for c in cells])
    margin_rows: list[dict[str, Any]] = []
    ablation_rows: list[dict[str, Any]] = []
    for seed in SEEDS:
        z = np.load(stage_dir / f"pseudo_arrays_seed{seed}.npz")
        Xtr, ytr, Xva, yva = z["X_train"], z["y_train"], z["X_validation"], z["y_validation"]
        scaler = StandardScaler().fit(Xtr[:, :, 2])
        clf = LogisticRegression(C=1.0, class_weight="balanced", solver="liblinear", random_state=0, max_iter=1000).fit(scaler.transform(Xtr[:, :, 2]), ytr)
        for split, X, y in (("train", Xtr, ytr), ("validation", Xva, yva)):
            comps = manifest_source_components(stage_dir, seed, split)
            F = scaler.transform(X[:, :, 2])
            prob = clf.predict_proba(F)[:, 1]
            pred = clf.predict(F)
            margin = clf.decision_function(F)
            for i, (yy, pp, pr, mg) in enumerate(zip(y, pred, prob, margin, strict=True)):
                margin_rows.append({"seed": seed, "split": split, "row": i, "true_label": INT_TO_LABEL[int(yy)], "pred_label": INT_TO_LABEL[int(pp)], "prob_present": float(pr), "decision_margin_present": float(mg), "correct": bool(int(yy) == int(pp)), "source_components": comps.get(i, "")})
        for sess in sorted(set(cell_sessions)):
            keep = cell_sessions != sess
            for split, X, y in (("train", Xtr, ytr), ("validation", Xva, yva)):
                Ftr = Xtr[:, keep, 2]
                F = X[:, keep, 2]
                ptr, pptr, pred, prob, _clf, _sc = fit_logreg(Ftr, ytr, F, C=1.0)
                if split == "train":
                    pred, prob = ptr, pptr
                ablation_rows.append(metrics(y, pred, prob, {"stage": "v8b_bin2_leave_one_session_cell_block_out", "seed": seed, "split": split, "left_out_session": sess, "dropped_cells": int(np.sum(~keep)), "kept_cells": int(np.sum(keep)), "representation": "raw_bin_2"}))
    write_csv(outdir / "v8b_bin2_margin_rows.csv", margin_rows)
    write_csv(outdir / "v8b_bin2_leave_one_session_cell_block_ablation.csv", ablation_rows)
    return margin_rows, ablation_rows


def v8b_source_diagnostics(stage_dir: Path, outdir: Path, rows_per_class: int, nulls: int):
    z, metas, source_index, cells = load_source_npz(stage_dir)
    Xsrc, Msrc = z["X_source_cell_bin"], z["observed_source_cell_mask"]
    rows = []
    for sess in sorted({m.session_id for m in metas}):
        sess_cells = [c for c in cells if sess.replace("_", "/") in c or sess.split("_")[0] in c]
        for split in ("train", "validation"):
            for lab in LABELS:
                idx = [i for i, m in enumerate(metas) if m.session_id == sess and m.split == split and m.label == lab]
                if not idx:
                    continue
                b2 = Xsrc[idx, :, 2]
                rows.append({
                    "session_id": sess,
                    "split": split,
                    "label": lab,
                    "source_count": len(idx),
                    "panel_cell_count": len(sess_cells),
                    "bin2_sum_mean_all_panel_cells": float(np.nanmean(np.nansum(b2, axis=1))),
                    "bin2_sum_min": float(np.nanmin(np.nansum(b2, axis=1))),
                    "bin2_sum_max": float(np.nanmax(np.nansum(b2, axis=1))),
                    "bin2_nonzero_source_fraction": float(np.mean(np.nansum(b2, axis=1) > 0)),
                })
    write_csv(outdir / "v8b_session_label_bin2_source_counts.csv", rows)

    # Observed and matched source-label nulls on same arrays/seeds. Statistic is mean BA over seeds.
    def rawbin_stats(shuffled=None):
        by_bin = []
        full = {"raw_binned": [], "pca_cellspace_8": []}
        for seed in SEEDS:
            arrays, _ = build_dataset(Xsrc=Xsrc, Msrc=Msrc, source_index=source_index, source_meta=metas, cell_ids=cells, rows_per_class=rows_per_class, seed=seed, shuffled_labels=shuffled)
            Xtr, ytr = arrays["train"]
            Xva, yva = arrays["validation"]
            bins = []
            for b in range(Xtr.shape[2]):
                _ptr, _pptr, pva, ppva, _clf, _sc = fit_logreg(feature(Xtr, "raw_bin", bin_index=b), ytr, feature(Xva, "raw_bin", bin_index=b), C=1.0)
                bins.append(float(balanced_accuracy_score(yva, pva)))
            by_bin.append(bins)
            for rep in full:
                if rep == "raw_binned":
                    Ftr, Fva = feature(Xtr, "raw_binned"), feature(Xva, "raw_binned")
                else:
                    Ftr, sc, pca = feature(Xtr, "pca_cellspace", pca_dim=8)
                    Fva, _, _ = feature(Xva, "pca_cellspace", pca_dim=8, scaler=sc, pca=pca)
                _ptr, _pptr, pva, ppva, _clf, _sc = fit_logreg(Ftr, ytr, Fva, C=1.0)
                full[rep].append(float(balanced_accuracy_score(yva, pva)))
        mean_by_bin = np.mean(np.asarray(by_bin), axis=0)
        return {"raw_bin2_mean_ba": float(mean_by_bin[2]), "raw_bin_max_over10_mean_ba": float(np.max(mean_by_bin)), "raw_bin_mean_ba_by_bin": mean_by_bin.tolist(), "raw_binned_mean_ba": float(np.mean(full["raw_binned"])), "pca8_mean_ba": float(np.mean(full["pca_cellspace_8"]))}

    observed = rawbin_stats()
    null_rows = []
    null_stats = []
    for n in range(nulls):
        shuffled = source_level_shuffle(metas, 30000 + n)
        st = rawbin_stats(shuffled)
        st["null_index"] = n
        null_stats.append(st)
        null_rows.append(st)
    pvals = {"observed": observed, "nulls": nulls, "resolution": 1 / (nulls + 1)}
    for key in ("raw_bin2_mean_ba", "raw_bin_max_over10_mean_ba", "raw_binned_mean_ba", "pca8_mean_ba"):
        exc = sum(float(ns[key]) >= float(observed[key]) for ns in null_stats)
        pvals[key] = {"observed": observed[key], "exceedances": exc, "p_value": (1 + exc) / (nulls + 1)}
    write_csv(outdir / "v8b_source_label_null_stats.csv", null_rows)
    write_json(outdir / "v8b_source_label_null_pvalues.json", pvals)
    return {"session_rows": rows, "observed_null_pvalues": pvals}


class TrialCueDataset(SingleSessionDataset):
    def __init__(self, X: np.ndarray, trial_id: np.ndarray, bin_id: np.ndarray, discrete: np.ndarray | None = None, *, device: str):
        super().__init__(device=device)
        self.neural = torch.as_tensor(X, dtype=torch.float32, device=device)
        self.trial_ids = torch.as_tensor(trial_id, dtype=torch.long, device=device)
        self.bin_ids = torch.as_tensor(bin_id, dtype=torch.long, device=device)
        self.offset = Offset(0, 1)
        self._discrete = None if discrete is None else torch.as_tensor(discrete, dtype=torch.long, device=device)
        self.trial_borders = torch.as_tensor(np.r_[0, np.flatnonzero(np.diff(trial_id)) + 1, len(trial_id)], dtype=torch.long, device=device)

    @property
    def input_dimension(self):
        return int(self.neural.shape[1])

    @property
    def discrete_index(self):
        return self._discrete

    def __len__(self):
        return int(self.neural.shape[0])

    def __getitem__(self, index):
        index = index.to(self.device).long()
        if str(self.offset) != str(Offset(0, 1)):
            raise NotImplementedError(f"TrialCueDataset fast path is audited only for offset1-model, got {self.offset}")
        if torch.any(index < 0) or torch.any(index >= len(self)):
            raise IndexError("CEBRA dataset index out of bounds")
        return self.neural[index].unsqueeze(-1)


class SameTrialTimeLoader(cebra.data.Loader):
    def __post_init__(self):
        super().__post_init__()
        tid = self.dataset.trial_ids
        bid = self.dataset.bin_ids
        idx = torch.arange(len(tid), device=self.device)
        ok = idx + self.time_offset < len(tid)
        nxt = torch.clamp(idx + self.time_offset, max=len(tid) - 1)
        ok &= tid == tid[nxt]
        ok &= bid + self.time_offset == bid[nxt]
        self.refs = torch.nonzero(ok, as_tuple=False).flatten()
        if int(self.refs.numel()) == 0:
            raise ValueError("no same-trial temporal positives")

    def get_indices(self, num_samples: int):
        r = self.refs[torch.randint(int(self.refs.numel()), (num_samples,), device=self.device)]
        p = r + self.time_offset
        n = torch.randint(len(self.dataset), (num_samples,), device=self.device)
        if not torch.all(self.dataset.trial_ids[r] == self.dataset.trial_ids[p]):
            raise AssertionError("temporal positive crossed trial boundary")
        if not torch.all(self.dataset.bin_ids[p] == self.dataset.bin_ids[r] + self.time_offset):
            raise AssertionError("temporal positive is not offset +1 bin")
        return BatchIndex(reference=r, positive=p, negative=n)


def flatten_rows(X: np.ndarray, y: np.ndarray):
    # row-major: each pseudo row is a trial with ten cue bins.
    n, c, b = X.shape
    Xflat = X.transpose(0, 2, 1).reshape(n * b, c)
    trial = np.repeat(np.arange(n), b)
    bins = np.tile(np.arange(b), n)
    labels = np.repeat(y, b)
    return Xflat, trial, bins, labels


def make_solver(input_dim: int, output_dim: int, hidden: int, lr: float, device: str):
    model = cebra.models.init("offset1-model", num_neurons=input_dim, num_units=hidden, num_output=output_dim).to(device)
    criterion = FixedCosineInfoNCE(temperature=1.0).to(device)
    opt = torch.optim.Adam(list(model.parameters()) + list(criterion.parameters()), lr=lr)
    return cebra.solver.init("single-session", model=model, criterion=criterion, optimizer=opt, tqdm_on=False).to(device)


def train_cebra(Xtr_rows: np.ndarray, ytr: np.ndarray, *, variant: str, dim: int, seed: int, outdir: Path, iterations: int, batch_size: int, lr: float, hidden: int, device: str):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    Xflat, trial, bins, labels = flatten_rows(Xtr_rows, ytr)
    scaler = StandardScaler().fit(Xflat)
    Xflat = scaler.transform(Xflat).astype("float32")
    discrete = labels if variant == "cebra_behavior" else None
    ds = TrialCueDataset(Xflat, trial, bins, discrete, device=device)
    solver = make_solver(ds.input_dimension, dim, hidden, lr, device)
    ds.configure_for(solver.model)
    if str(solver.model.get_offset()) != str(Offset(0, 1)):
        raise AssertionError(f"expected offset1-model, got {solver.model.get_offset()}")
    loader = SameTrialTimeLoader(dataset=ds, time_offset=1, num_steps=iterations, batch_size=batch_size) if variant == "cebra_time" else DiscreteDataLoader(dataset=ds, num_steps=iterations, batch_size=batch_size, prior="empirical")
    solver._set_fitted_params(loader)
    solver.model.train()
    outdir.mkdir(parents=True, exist_ok=True)
    if torch.cuda.is_available():
        torch.cuda.reset_peak_memory_stats()
    t0 = time.time()
    checkpoints = []
    for step, batch in enumerate(loader, start=1):
        solver.step(batch)
        if step in {1, 250, 500, 750, iterations}:
            ckpt = outdir / f"checkpoint_step{step:04d}.pth"
            torch.save(solver.state_dict(), ckpt)
            checkpoints.append(str(ckpt))
    wall = time.time() - t0
    loss = [{"step": i + 1, "total": float(t), "pos": float(p), "neg": float(n), "temperature": float(temp)} for i, (t, p, n, temp) in enumerate(zip(solver.log["total"], solver.log["pos"], solver.log["neg"], solver.log["temperature"], strict=True))]
    write_csv(outdir / "loss_trace.csv", loss)
    torch.save(solver.state_dict(), outdir / "checkpoint_final.pth")
    peak_alloc = int(torch.cuda.max_memory_allocated()) if torch.cuda.is_available() else 0
    peak_reserved = int(torch.cuda.max_memory_reserved()) if torch.cuda.is_available() else 0
    info = {"loss_first": loss[0]["total"], "loss_last": loss[-1]["total"], "loss_last100_mean": float(np.mean([x["total"] for x in loss[-100:]])), "loss_prev100_mean": float(np.mean([x["total"] for x in loss[-200:-100]])) if len(loss) >= 200 else None, "wall_seconds": wall, "peak_allocated_bytes": peak_alloc, "peak_reserved_bytes": peak_reserved, "checkpoints": checkpoints, "extension": "not_run; predeclared no validation-based extension in this pass"}
    return solver, scaler, info


def embed_rows(solver: Any, scaler: StandardScaler, X_rows: np.ndarray, *, device: str, dim: int):
    Xflat, _trial, _bins, _labels = flatten_rows(X_rows, np.zeros(X_rows.shape[0], dtype=int))
    Xflat = scaler.transform(Xflat).astype("float32")
    with torch.no_grad():
        Z = solver.transform(torch.as_tensor(Xflat, dtype=torch.float32, device=device), batch_size=1024).detach().cpu().numpy()
    return Z.reshape(X_rows.shape[0], X_rows.shape[2] * dim)


def run_cebra_fit(arrays: dict[str, tuple[np.ndarray, np.ndarray]], *, variant: str, dim: int, seed: int, outdir: Path, iterations: int, batch_size: int, lr: float, hidden: int, device: str):
    Xtr, ytr = arrays["train"]
    Xva, yva = arrays["validation"]
    solver, scaler, info = train_cebra(Xtr, ytr, variant=variant, dim=dim, seed=seed, outdir=outdir, iterations=iterations, batch_size=batch_size, lr=lr, hidden=hidden, device=device)
    Ztr = embed_rows(solver, scaler, Xtr, device=device, dim=dim)
    Zva = embed_rows(solver, scaler, Xva, device=device, dim=dim)
    ptr, pptr, pva, ppva, clf, zscaler = fit_logreg(Ztr, ytr, Zva, C=1.0)
    rows = [metrics(ytr, ptr, pptr, {"split": "train", "representation": variant, "dim": dim, "seed": seed, "C": 1.0, "decoder_n_iter": int(clf.n_iter_[0])}), metrics(yva, pva, ppva, {"split": "validation", "representation": variant, "dim": dim, "seed": seed, "C": 1.0, "decoder_n_iter": int(clf.n_iter_[0])})]
    pred_rows = []
    for split, y, pred, prob in (("train", ytr, ptr, pptr), ("validation", yva, pva, ppva)):
        for i, (yy, pp, pr) in enumerate(zip(y, pred, prob, strict=True)):
            pred_rows.append({"representation": variant, "dim": dim, "seed": seed, "split": split, "row": i, "true_label": INT_TO_LABEL[int(yy)], "pred_label": INT_TO_LABEL[int(pp)], "prob_present": float(pr)})
    # save-load parity on embeddings from final checkpoint
    reloaded = make_solver(Xtr.shape[1], dim, hidden, lr, device)
    reloaded.load_state_dict(torch.load(outdir / "checkpoint_final.pth", map_location=device), strict=True)
    reloaded.n_features = Xtr.shape[1]
    Zva2 = embed_rows(reloaded, scaler, Xva, device=device, dim=dim)
    info["save_load_max_abs_embedding_diff"] = float(np.max(np.abs(Zva - Zva2)))
    np.savez_compressed(outdir / "embeddings_and_decoder.npz", Z_train=Ztr, Z_validation=Zva, y_train=ytr, y_validation=yva, decoder_coef=clf.coef_, decoder_intercept=clf.intercept_, embedding_scaler_mean=scaler.mean_, embedding_scaler_scale=scaler.scale_, decoder_scaler_mean=zscaler.mean_, decoder_scaler_scale=zscaler.scale_)
    write_json(outdir / "fit_info.json", info)
    return rows, pred_rows, info


def run_v9(stage_dir: Path, outdir: Path, rows_per_class: int, nulls: int, iterations: int, batch_size: int, lr: float, hidden: int):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    if device != "cuda":
        raise RuntimeError("V9 requires actual CUDA GPU")
    z, metas, source_index, cells = load_source_npz(stage_dir)
    Xsrc, Msrc = z["X_source_cell_bin"], z["observed_source_cell_mask"]
    all_metrics, all_preds, all_info, null_metric_rows = [], [], [], []
    for seed in SEEDS:
        pz = np.load(stage_dir / f"pseudo_arrays_seed{seed}.npz")
        arrays = {"train": (pz["X_train"], pz["y_train"]), "validation": (pz["X_validation"], pz["y_validation"])}
        for variant in VARIANTS:
            for dim in DIMS:
                fit_dir = outdir / "observed" / variant / f"dim{dim}" / f"seed{seed}"
                rows, preds, info = run_cebra_fit(arrays, variant=variant, dim=dim, seed=seed, outdir=fit_dir, iterations=iterations, batch_size=batch_size, lr=lr, hidden=hidden, device=device)
                all_metrics.extend(rows)
                all_preds.extend(preds)
                all_info.append({"variant": variant, "dim": dim, "seed": seed, **info})
    observed_dim8_seed0 = {r["representation"]: r["balanced_accuracy"] for r in all_metrics if r["split"] == "validation" and r["dim"] == 8 and r["seed"] == 0}
    for variant in VARIANTS:
        for n in range(nulls):
            shuffled = source_level_shuffle(metas, 40000 + n)
            arrays, _ = build_dataset(Xsrc=Xsrc, Msrc=Msrc, source_index=source_index, source_meta=metas, cell_ids=cells, rows_per_class=rows_per_class, seed=0, shuffled_labels=shuffled)
            fit_dir = outdir / "nulls" / variant / f"null{n:03d}"
            rows, _preds, info = run_cebra_fit(arrays, variant=variant, dim=8, seed=0, outdir=fit_dir, iterations=iterations, batch_size=batch_size, lr=lr, hidden=hidden, device=device)
            for r in rows:
                if r["split"] == "validation":
                    rr = dict(r)
                    rr["null_index"] = n
                    rr["null_type"] = "source_label_shuffle_reassemble_refit_encoder_decoder"
                    rr["loss_last"] = info["loss_last"]
                    null_metric_rows.append(rr)
    pvals = {"nulls_per_variant": nulls, "resolution": 1 / (nulls + 1), "observed_dim8_seed0_validation_ba": observed_dim8_seed0}
    for variant in VARIANTS:
        vals = [r["balanced_accuracy"] for r in null_metric_rows if r["representation"] == variant]
        obs = observed_dim8_seed0[variant]
        exc = sum(v >= obs for v in vals)
        pvals[variant] = {"observed": obs, "exceedances": exc, "p_value": (1 + exc) / (nulls + 1), "null_min": float(np.min(vals)), "null_median": float(np.median(vals)), "null_max": float(np.max(vals))}
    write_csv(outdir / "v9_cebra_metrics.csv", all_metrics)
    write_csv(outdir / "v9_cebra_predictions.csv", all_preds)
    write_csv(outdir / "v9_dim8_seed0_source_label_null_metrics.csv", null_metric_rows)
    write_json(outdir / "v9_null_pvalues.json", pvals)
    write_json(outdir / "v9_fit_infos.json", all_info)
    return {"metrics": all_metrics, "null_pvalues": pvals, "fit_infos": all_info}


def read_loss_totals(path: Path) -> list[float]:
    with path.open(newline="", encoding="utf-8") as f:
        return [float(r["total"]) for r in csv.DictReader(f)]


def old_new_speedfix_comparison(old_dir: Path | None, new_dir: Path) -> dict[str, Any]:
    if old_dir is None:
        return {"status": "not_requested"}
    rel = Path("v9/observed/cebra_time/dim3/seed0")
    old_fit = old_dir / rel
    new_fit = new_dir / rel
    if not (old_fit / "loss_trace.csv").exists() or not (new_fit / "loss_trace.csv").exists():
        return {"status": "missing_reference", "old_fit": str(old_fit), "new_fit": str(new_fit)}
    old_loss = read_loss_totals(old_fit / "loss_trace.csv")
    new_loss = read_loss_totals(new_fit / "loss_trace.csv")
    n = min(len(old_loss), len(new_loss))
    out = {
        "status": "compared",
        "fit": str(rel),
        "compared_steps": n,
        "old_steps": len(old_loss),
        "new_steps": len(new_loss),
        "loss_max_abs_diff_first_common_steps": float(np.max(np.abs(np.asarray(old_loss[:n]) - np.asarray(new_loss[:n])))) if n else None,
        "old_wall_seconds": json.load((old_fit / "fit_info.json").open())["wall_seconds"] if (old_fit / "fit_info.json").exists() else None,
        "new_wall_seconds": json.load((new_fit / "fit_info.json").open())["wall_seconds"] if (new_fit / "fit_info.json").exists() else None,
    }
    old_emb = old_fit / "embeddings_and_decoder.npz"
    new_emb = new_fit / "embeddings_and_decoder.npz"
    if old_emb.exists() and new_emb.exists():
        oe, ne = np.load(old_emb), np.load(new_emb)
        out["embedding_Z_validation_max_abs_diff"] = float(np.max(np.abs(oe["Z_validation"] - ne["Z_validation"])))
    write_json(new_dir / "speedfix_old_new_comparison.json", out)
    return out


def write_audit_and_handoff(outdir: Path, summary: dict[str, Any]) -> None:
    lines = [
        "# V8b/V9 audit and handoff",
        "",
        "Status: complete; exploratory development validation only. No raw tables/test split used.",
        "",
        "## V8b",
        "The raw_bin_2 perfect validation result was treated as a diagnostic, not a selected endpoint. Source/session tables and matched source-label nulls are saved under `v8b/`.",
        f"V8b null p-values: `{summary['v8b']['observed_null_pvalues']}`",
        f"Bin-2 margin rows: `{summary['v8b']['bin2_margin_rows']}`; leave-one-session-cell-block ablation rows: `{summary['v8b']['bin2_ablation_rows']}`.",
        "Interpretation ceiling: 29 cells from 7 sessions, source N 82 train/22 validation; 64 pseudo rows/class are repeated synthetic draws, not independent N.",
        "",
        "## V9",
        "Native CEBRA 0.6.1 PyTorch solver, `offset1-model`, CUDA device, train-only normalization, trial-safe temporal positives for Time variant, categorical positives for Behavior variant.",
        f"V9 null p-values: `{summary['v9']['null_pvalues']}`",
        f"Old/new speedfix comparison: `{summary['speedfix_comparison']}`",
        "Behavior CEBRA is label-shaped; CEBRA-Time has no path-label input but assembly itself is label-conditioned. No biology/significance claim before independent review.",
        "",
        "## First V7 tee failure history",
        "Recovered from `.pi/tasks/session-283783-283783/b5ef41ea0.json`: command started 2026-09-05T21:30:43.331Z / local 2026-09-06T05:30:43.331, exited 1 at 21:31:28.265Z because `tee` target log dir was missing. Artifacts were overwritten by final rerun; exact first-run artifact hashes are unavailable.",
    ]
    (outdir / "v8b_v9_teaching_audit.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (outdir / "V8B-V9-HANDOFF.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(args: argparse.Namespace) -> dict[str, Any]:
    started = time.time()
    if (args.output_dir / "summary.json").exists():
        raise FileExistsError(f"refusing to clobber completed run: {args.output_dir}")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    stage_dir = args.v7v8_dir / PANEL / BIN_DIR
    prefit = {
        "created_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "stage": "V8b diagnostics plus V9 native GPU CEBRA from saved V7/V8 arrays",
        "raw_test_data_policy": "no raw/test access; source_level_cue_tensors.npz and pseudo_arrays_seed*.npz only",
        "primary": {"panel": PANEL, "bin_width": "100ms", "whole_cue_bins": 10, "seeds": list(SEEDS), "rows_per_class": args.rows_per_class},
        "v8b": {"C_grid": list(CS), "source_label_nulls": args.v8b_nulls, "max_over_bins_family_stat": "max over 10 raw_bin mean validation BA across seeds 0/1/2"},
        "v9": {"cebra_version": cebra.__version__, "variants": list(VARIANTS), "dims": list(DIMS), "iterations": args.iterations, "nulls_dim8_seed0_per_variant": args.v9_nulls, "model": "offset1-model", "hidden": args.hidden, "batch_size": args.batch_size, "lr": args.lr, "temperature": 1.0},
    }
    write_json(args.output_dir / "prefit_config_manifest.json", prefit)
    v8b_dir = args.output_dir / "v8b"
    v8b_metrics, _ = v8b_regularization(stage_dir, v8b_dir)
    comparator_rows = baseline_metric_rows(stage_dir, v8b_dir, v8b_metrics)
    bin2_margin_rows, bin2_ablation_rows = v8b_bin2_margins_and_ablation(stage_dir, v8b_dir)
    v8b_diag = v8b_source_diagnostics(stage_dir, v8b_dir, args.rows_per_class, args.v8b_nulls)
    v9_dir = args.output_dir / "v9"
    v9 = run_v9(stage_dir, v9_dir, args.rows_per_class, args.v9_nulls, args.iterations, args.batch_size, args.lr, args.hidden)
    speedfix = old_new_speedfix_comparison(args.old_partial_dir, args.output_dir)
    summary = {
        "status": "complete",
        "runtime_seconds": time.time() - started,
        "command": " ".join(shlex.quote(x) for x in sys.argv),
        "hashes": {"script_sha256": sha256_file(Path(__file__)), "git_head": git(["rev-parse", "HEAD"]), "git_status_short": git(["status", "--short"]), "source_npz_sha256": sha256_file(stage_dir / "source_level_cue_tensors.npz")},
        "environment": {"python": sys.version, "platform": platform.platform(), "numpy": np.__version__, "torch": torch.__version__, "cebra": cebra.__version__, "cuda_available": torch.cuda.is_available(), "cuda_device": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None},
        "artifacts": {"v8b_metrics": str(v8b_dir / "v8b_regularization_metrics.csv"), "v8b_comparators": str(v8b_dir / "v8b_v9_same_array_comparator_baselines.csv"), "v8b_bin2_margins": str(v8b_dir / "v8b_bin2_margin_rows.csv"), "v8b_bin2_ablation": str(v8b_dir / "v8b_bin2_leave_one_session_cell_block_ablation.csv"), "v8b_null_pvalues": str(v8b_dir / "v8b_source_label_null_pvalues.json"), "v9_metrics": str(v9_dir / "v9_cebra_metrics.csv"), "v9_null_pvalues": str(v9_dir / "v9_null_pvalues.json"), "speedfix_comparison": str(args.output_dir / "speedfix_old_new_comparison.json"), "handoff": str(args.output_dir / "V8B-V9-HANDOFF.md")},
        "v8b": {"regularization_rows": len(v8b_metrics), "comparator_rows": len(comparator_rows), "bin2_margin_rows": len(bin2_margin_rows), "bin2_ablation_rows": len(bin2_ablation_rows), **v8b_diag},
        "v9": {"metric_rows": len(v9["metrics"]), "null_pvalues": v9["null_pvalues"]},
        "speedfix_comparison": speedfix,
    }
    write_json(args.output_dir / "summary.json", summary)
    write_audit_and_handoff(args.output_dir, summary)
    return summary


def parse_args(argv=None):
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--v7v8-dir", type=Path, required=True)
    r.add_argument("--output-dir", type=Path, required=True)
    r.add_argument("--rows-per-class", type=int, default=64)
    r.add_argument("--v8b-nulls", type=int, default=100)
    r.add_argument("--v9-nulls", type=int, default=20)
    r.add_argument("--iterations", type=int, default=1000)
    r.add_argument("--batch-size", type=int, default=256)
    r.add_argument("--lr", type=float, default=3e-4)
    r.add_argument("--hidden", type=int, default=32)
    r.add_argument("--old-partial-dir", type=Path)
    return p.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    if args.cmd == "run":
        print(json.dumps({"summary": str(run(args)["artifacts"]["handoff"])}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
