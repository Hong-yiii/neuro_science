#!/usr/bin/env python3
"""Frozen CEBRA hyperparameter diagnosis runner.

Thin wrapper around scripts.cebra_decoder_autoresearch: no CEBRA fitting, no
observed PCA fitting, forward-only verification.
"""

from __future__ import annotations

import argparse
import json
import math
import shutil
import sys
import time
import warnings
from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from contextlib import ExitStack
from pathlib import Path
from unittest.mock import patch
from typing import Any

import numpy as np
from scipy.special import expit
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts import cebra_decoder_autoresearch as base
from scripts.cebra_decoder_autoresearch import FeatureSet, PredictionBundle

REPO_ROOT = base.REPO_ROOT
PROTOCOL_PATH = REPO_ROOT / "docs/reports/cebra-hyperparameter-prefit-20260924.md"
ACCEPTED_RUN = (
    REPO_ROOT / "outputs/cebra-decoder-autoresearch-20260924/recovery-20260924T042259Z"
)
OWNED_OUTPUT_ROOT = REPO_ROOT / "outputs/cebra-hyperparameter-diagnosis-20260924"
FIT_GATE_FLAG = "I_UNDERSTAND_THIS_RUNS_1700_READOUT_FITS_20_NULL_PCA_ZERO_CEBRA_OR_OBSERVED_PCA_FITS"
TEMPERATURES = (1.0, 2.0, 5.0, 10.0)
LOGISTIC_CS = (0.001, 0.01, 0.1, 1.0, 10.0, 100.0)
SVM_CS = (0.1, 1.0, 10.0)
SVM_GAMMA_MULTIPLIERS = (0.1, 1.0, 10.0)
TOL = base.REPLAY_TOLERANCE
NULL_TOL = 1e-12


def logistic_recipe_id(C: float) -> str:
    return {
        0.001: "logistic_scaled_c0001",
        0.01: "logistic_scaled_c001",
        0.1: "logistic_scaled_c01",
        1.0: "logistic_scaled_c1",
        10.0: "logistic_scaled_c10",
        100.0: "logistic_scaled_c100",
    }[float(C)]


def svm_recipe_id(C: float, gamma_multiplier: float) -> str:
    if float(C) == 1.0 and float(gamma_multiplier) == 1.0:
        return "svm_rbf_scaled"
    c = str(C).replace(".", "_")
    g = str(gamma_multiplier).replace(".", "_")
    return f"svm_rbf_scaled_c{c}_g{g}"


LOGISTIC_RECIPES = tuple(
    {"id": logistic_recipe_id(C), "kind": "logistic", "C": C, "scaled": True}
    for C in LOGISTIC_CS
)
SVM_GRID_RECIPES = tuple(
    {
        "id": svm_recipe_id(C, g),
        "kind": "svm_grid",
        "C": C,
        "gamma_multiplier": g,
        "scaled": True,
    }
    for C in SVM_CS
    for g in SVM_GAMMA_MULTIPLIERS
)
GRID_RECIPE_IDS = tuple(r["id"] for r in LOGISTIC_RECIPES + SVM_GRID_RECIPES)
LEGACY_CONTEXT_IDS = (
    "logistic_unscaled_c1",
    "knn_cosine_5",
    "knn_cosine_15",
    "svm_rbf_unscaled",
)
ALL_RECIPE_IDS = GRID_RECIPE_IDS + LEGACY_CONTEXT_IDS
PRIOR_RECIPE_IDS = (
    (
        "logistic_scaled_c1",
        "logistic_scaled_c01",
        "logistic_scaled_c001",
    )
    + LEGACY_CONTEXT_IDS[:3]
    + ("svm_rbf_scaled", "svm_rbf_unscaled")
)
NEW_EXISTING_RECIPE_IDS = tuple(
    rid
    for rid in GRID_RECIPE_IDS
    if rid
    not in {
        "logistic_scaled_c1",
        "logistic_scaled_c01",
        "logistic_scaled_c001",
        "svm_rbf_scaled",
    }
)
RECIPE_BY_ID: dict[str, dict[str, Any]] = {
    r["id"]: dict(r) for r in LOGISTIC_RECIPES + SVM_GRID_RECIPES
}
RECIPE_BY_ID.update({r["id"]: dict(r) for r in base.RECIPES})


# ---------------------------------------------------------------------------
# Small helpers


def resolve_output(path: Path, *, allow_tmp: bool = False) -> Path:
    path = path.resolve()
    if allow_tmp:
        return path
    root = OWNED_OUTPUT_ROOT.resolve()
    if path != root and root not in path.parents:
        raise ValueError(f"output must be under {root}")
    return path


def require_fresh(path: Path) -> None:
    if path.exists():
        raise FileExistsError(f"refusing to overwrite existing path: {path}")


def write_json(path: Path, payload: Any) -> None:
    base.write_json(path, payload)


def read_json(path: Path) -> Any:
    return base.read_json(path)


def write_csv(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    base.write_csv(path, rows)


def csv_rows(path: Path) -> list[dict[str, str]]:
    return base.csv_rows(path)


def stable_hash(payload: Any) -> str:
    return base.stable_hash(payload)


def sha256_file(path: Path) -> str:
    return base.sha256_file(path)


def dependency_hash() -> str:
    info = base.runtime_info()
    return stable_hash(
        {
            **{
                k: info.get(k)
                for k in ("python", "numpy", "scipy", "sklearn", "env_threads")
            },
            "base_code_sha256": sha256_file(Path(base.__file__)),
        }
    )


def gate_payload(
    accepted_run: Path, artifact_hashes: Mapping[str, str]
) -> dict[str, Any]:
    return {
        "code_sha256": sha256_file(Path(__file__)),
        "base_code_sha256": sha256_file(Path(base.__file__)),
        "protocol_sha256": sha256_file(PROTOCOL_PATH),
        "dependency_hash": dependency_hash(),
        "accepted_run": str(accepted_run),
        "artifact_hashes": dict(sorted(artifact_hashes.items())),
    }


def gate_token(payload: Mapping[str, Any]) -> str:
    return stable_hash(payload)


def as_bool(value: Any) -> bool:
    return base.truthy(value)


def as_int_or_none(value: Any) -> int | None:
    if value in (None, "", "None"):
        return None
    return int(value)


def row_float(value: Any) -> float | None:
    if value in (None, "", "None"):
        return None
    return float(value)


# ---------------------------------------------------------------------------
# Audit


def audit_accepted(
    output_dir: Path,
    *,
    accepted_run: Path = ACCEPTED_RUN,
    allow_tmp: bool = False,
) -> dict[str, Any]:
    """No-fit audit.  Does not call PCA.fit or any readout fit API."""
    output_dir = resolve_output(output_dir, allow_tmp=allow_tmp)
    require_fresh(output_dir)
    output_dir.mkdir(parents=True)
    accepted_run = accepted_run.resolve()
    started = time.time()
    required = [
        "audit_manifest.json",
        "feature_manifest.json",
        "model_manifest.json",
        "readout_metrics.csv",
        "verify_receipt.json",
        "summary.json",
        "source_bootstrap_worlds.json",
        "run_config.json",
    ]
    artifact_hashes = {name: sha256_file(accepted_run / name) for name in required}
    old_audit = read_json(accepted_run / "audit_manifest.json")
    features = read_json(accepted_run / "feature_manifest.json")["features"]
    models = read_json(accepted_run / "model_manifest.json")["models"]
    if len(features) != 100 or len(models) != 800:
        raise ValueError(
            f"accepted package count mismatch: features={len(features)} models={len(models)}"
        )
    _validate_prior_model_grid(features, models, full=True)
    validate_accepted_inputs(accepted_run)
    null_worlds = audit_matched_null_worlds(old_audit)
    payload = gate_payload(accepted_run, artifact_hashes)
    manifest = {
        "schema_version": 1,
        "status": "audited",
        "synthetic": False,
        "generated_unix_seconds": time.time(),
        "wall_seconds": time.time() - started,
        "accepted_run": str(accepted_run),
        "protocol_path": str(PROTOCOL_PATH),
        "protocol_sha256": payload["protocol_sha256"],
        "code_sha256": payload["code_sha256"],
        "dependency_hash": payload["dependency_hash"],
        "gate_payload": payload,
        "gate_token": gate_token(payload),
        "artifact_hashes": artifact_hashes,
        "source_tensor": old_audit["source_tensor"],
        "prior_counts": {"features": len(features), "models": len(models)},
        "planned_counts": expected_full_counts(),
        "null_worlds": null_worlds,
        "matched_null_worlds": len(null_worlds),
        "notes": [
            "audit is forward/reconstruction only",
            "PCA null transforms are fitted only by gated run, never by audit",
            "observed raw/PCA features are reused from the accepted recovery package",
        ],
        "runtime": base.runtime_info(),
        "git": base.git_state(),
    }
    write_json(output_dir / "audit_manifest.json", manifest)
    write_csv(output_dir / "matched_null_worlds.csv", null_worlds)
    snapshots = output_dir / "source_snapshots"
    snapshots.mkdir()
    shutil.copy2(Path(__file__), snapshots / Path(__file__).name)
    shutil.copy2(PROTOCOL_PATH, snapshots / PROTOCOL_PATH.name)
    shutil.copy2(base.__file__, snapshots / Path(base.__file__).name)
    return manifest


def validate_accepted_inputs(accepted_run: Path) -> None:
    receipt = read_json(accepted_run / "verify_receipt.json")
    if (
        receipt.get("status") != "verified"
        or read_json(accepted_run / "run_config.json").get("status") != "complete"
    ):
        raise ValueError("accepted input is not complete and verified")
    for name, digest in receipt["report_input_hashes"].items():
        if sha256_file(accepted_run / name) != digest:
            raise ValueError(f"accepted verified input changed: {name}")
    old_audit = read_json(accepted_run / "audit_manifest.json")
    if (
        sha256_file(accepted_run / "audit_manifest.json")
        != read_json(accepted_run / "run_config.json")["audit_manifest_sha256"]
    ):
        raise ValueError("original accepted audit binding mismatch")
    base.validate_audited_inputs(old_audit)
    for entry in old_audit["observed_fits"] + old_audit["null_fits"]:
        train_ids = {
            r["source_trial_id"]
            for r in csv_rows(
                Path(entry["fit_dir"]) / "generated_assembly_manifest.csv"
            )
            if r["split"] == "train"
        }
        val_ids = {
            r["source_trial_id"]
            for r in csv_rows(Path(entry["fit_dir"]) / "exact_evaluation_manifest.csv")
        }
        if train_ids & val_ids or len(val_ids) != 22:
            raise ValueError("source disjointness/evaluation support gate failed")
    metas, features = load_features(accepted_run)
    if len(features) != len(metas):
        raise ValueError("duplicate feature IDs")
    reference_lineage = None
    for feature in features.values():
        if len(feature.y_train) != 128 or len(feature.y_validation) != 30:
            raise ValueError("accepted feature row count mismatch")
        if not np.array_equal(
            np.bincount(feature.y_train), [64, 64]
        ) or not np.array_equal(np.bincount(feature.y_validation), [24, 6]):
            raise ValueError("accepted feature class counts mismatch")
        for X in (feature.X_train, feature.X_validation):
            if not np.isfinite(X).all() or X.shape[1] != (
                290 if feature.kind == "raw" else 80
            ):
                raise ValueError("accepted feature shape/nonfinite mismatch")
        np.testing.assert_allclose(
            feature.validation_weights,
            base.exact_class_weights(feature.y_validation),
            atol=1e-12,
            rtol=0,
        )
        lineage = base.validation_source_matrix(feature.validation_manifest)
        if (
            lineage["source_ids"].shape != (30, 7)
            or len(set(lineage["source_ids"].ravel())) != 22
        ):
            raise ValueError("accepted class-local source lineage mismatch")
        if not as_bool(feature.metadata.get("is_null")):
            digest = stable_hash({k: v.tolist() for k, v in lineage.items()})
            reference_lineage = reference_lineage or digest
            if digest != reference_lineage:
                raise ValueError(
                    "observed source lineage differs across representations"
                )
    for meta in load_model_metas(accepted_run):
        base.load_model(accepted_run, meta)
        if (
            meta.get("estimator_joblib")
            and sha256_file(accepted_run / meta["estimator_joblib"])
            != meta["estimator_joblib_sha256"]
        ):
            raise ValueError("accepted fitted kNN hash mismatch")


def audit_matched_null_worlds(old_audit: Mapping[str, Any]) -> list[dict[str, Any]]:
    by_perm: dict[int, dict[str, Mapping[str, Any]]] = defaultdict(dict)
    for entry in old_audit["null_fits"]:
        spec = entry["fit_spec"]
        by_perm[int(spec["permutation_index"])][str(spec["objective"])] = entry
    rows = []
    for perm in range(20):
        pair = by_perm.get(perm, {})
        if set(pair) != set(base.CEBRA_OBJECTIVES):
            raise ValueError(f"missing null objective pair for permutation {perm}")
        t = pair["cebra_time"]
        b = pair["cebra_behavior"]
        for field in (
            "generated_manifest_sha256",
            "exact_manifest_sha256",
            "train_manifest_hash",
            "eval_manifest_hash",
            "train_array_sha256",
            "eval_array_sha256",
        ):
            if t[field] != b[field]:
                raise ValueError(f"null permutation {perm} mismatch in {field}")
        rows.append(
            {
                "permutation_index": perm,
                "time_fit_id": t["fit_id"],
                "behavior_fit_id": b["fit_id"],
                "generated_manifest_sha256": t["generated_manifest_sha256"],
                "exact_manifest_sha256": t["exact_manifest_sha256"],
                "train_array_sha256": t["train_array_sha256"],
                "eval_array_sha256": t["eval_array_sha256"],
                "train_unique_sources": t.get("train_unique_sources"),
                "validation_unique_sources": t.get("validation_unique_sources"),
            }
        )
    return rows


def expected_full_counts() -> dict[str, int]:
    return {
        "prior_features": 100,
        "total_features_after_run": 140,
        "observed_feature_sets": 60,
        "cebra_null_feature_sets": 40,
        "raw_pca_null_feature_sets": 40,
        "reused_prior_readouts": 800,
        "observed_new_readout_fits": 660,
        "cebra_null_new_readout_fits": 440,
        "raw_pca_null_readout_fits": 600,
        "total_new_readout_fits": 1700,
        "total_readout_records": 2500,
        "new_train_only_pca_fits": 20,
        "new_cebra_fits": 0,
        "new_observed_pca_fits": 0,
        "source_bootstrap_rows": 228000,
        "delete_source_rows": 25080,
    }


# ---------------------------------------------------------------------------
# Feature/model loading and fitting


def load_features(run_dir: Path) -> tuple[list[dict[str, Any]], dict[str, FeatureSet]]:
    metas = read_json(run_dir / "feature_manifest.json")["features"]
    features = {m["feature_id"]: base.load_feature(run_dir, m) for m in metas}
    return metas, features


def load_model_metas(run_dir: Path) -> list[dict[str, Any]]:
    return read_json(run_dir / "model_manifest.json")["models"]


def _validate_prior_model_grid(
    feature_metas: Sequence[Mapping[str, Any]],
    model_metas: Sequence[Mapping[str, Any]],
    *,
    full: bool,
) -> None:
    keys = [(m["feature_id"], m["recipe_id"]) for m in model_metas]
    dup = [k for k, n in Counter(keys).items() if n > 1]
    if dup:
        raise ValueError(f"duplicate prior model rows: {dup[:5]}")
    have = set(keys)
    missing = []
    for fm in feature_metas:
        for rid in PRIOR_RECIPE_IDS:
            if (fm["feature_id"], rid) not in have:
                missing.append((fm["feature_id"], rid))
    if missing:
        raise ValueError(f"incomplete prior model grid: {missing[:5]}")
    if full:
        kinds = Counter((m["kind"], as_bool(m.get("is_null"))) for m in feature_metas)
        if kinds[("cebra", False)] != 50 or kinds[("cebra", True)] != 40:
            raise ValueError(f"accepted feature kind/null counts mismatch: {kinds}")
        if kinds[("raw", False)] != 5 or kinds[("pca", False)] != 5:
            raise ValueError(f"accepted raw/PCA observed counts mismatch: {kinds}")
        obs = {
            (m.get("objective"), m.get("assembly_seed"), m.get("optimizer_seed"))
            for m in feature_metas
            if m["kind"] == "cebra" and not as_bool(m.get("is_null"))
        }
        null = {
            (
                m.get("objective"),
                m.get("permutation_index"),
                m.get("assembly_seed"),
                m.get("optimizer_seed"),
            )
            for m in feature_metas
            if m["kind"] == "cebra" and as_bool(m.get("is_null"))
        }
        controls = {
            (m["kind"], m.get("assembly_seed"))
            for m in feature_metas
            if m["kind"] in {"raw", "pca"}
        }
        if obs != {
            (o, a, s) for o in base.CEBRA_OBJECTIVES for a in range(5) for s in range(5)
        }:
            raise ValueError("observed encoder factorial is incomplete")
        if null != {(o, p, 0, 0) for o in base.CEBRA_OBJECTIVES for p in range(20)}:
            raise ValueError("null encoder factorial is incomplete")
        if controls != {(k, s) for k in ("raw", "pca") for s in range(5)}:
            raise ValueError("raw/PCA assembly factorial is incomplete")


def fit_svm_grid(feature: FeatureSet, recipe: Mapping[str, Any]) -> PredictionBundle:
    warn_rows: list[str] = []
    Xtr = feature.X_train
    Xva = feature.X_validation
    state: dict[str, np.ndarray] = {}
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        scaler = StandardScaler().fit(Xtr)
        Xtr_s = np.asarray(scaler.transform(Xtr), dtype=np.float64)
        Xva_s = np.asarray(scaler.transform(Xva), dtype=np.float64)
        state["scaler_mean"] = np.asarray(scaler.mean_, dtype=np.float64)
        state["scaler_scale"] = np.asarray(scaler.scale_, dtype=np.float64)
        var = float(np.var(np.asarray(Xtr_s, dtype=np.float64)))
        gamma0 = 1.0 / (Xtr_s.shape[1] * var) if var > 0.0 else 1.0
        gamma = gamma0 * float(recipe["gamma_multiplier"])
        gamma_arg: Any = float(gamma)
        clf = SVC(
            C=float(recipe["C"]),
            kernel="rbf",
            gamma=gamma_arg,
            probability=False,
            class_weight="balanced",
            tol=0.001,
            max_iter=100000,
            cache_size=200,
        ).fit(Xtr_s, feature.y_train)
        state.update(
            {
                "support_vectors": np.asarray(clf.support_vectors_, dtype=np.float64),
                "dual_coef": np.asarray(clf.dual_coef_, dtype=np.float64),
                "intercept": np.asarray(clf.intercept_, dtype=np.float64),
                "gamma": np.asarray([gamma], dtype=np.float64),
                "classes": np.asarray(clf.classes_, dtype=np.int64),
                "n_support": np.asarray(clf.n_support_, dtype=np.int64),
            }
        )
        tr_s, tr_p, tr_pred = base.svm_predict_from_state(feature.X_train, state)
        va_s, va_p, va_pred = base.svm_predict_from_state(feature.X_validation, state)
        if np.max(np.abs(tr_s - clf.decision_function(Xtr_s))) > TOL:
            raise AssertionError(
                "manual SVM replay disagrees with sklearn train margins"
            )
        if np.max(np.abs(va_s - clf.decision_function(Xva_s))) > TOL:
            raise AssertionError(
                "manual SVM replay disagrees with sklearn validation margins"
            )
        warn_rows = [f"{w.category.__name__}: {w.message}" for w in caught]
    meta = {
        "model_kind": "svc_rbf",
        "fit_counted": True,
        "C": float(recipe["C"]),
        "kernel": "rbf",
        "gamma": float(gamma),
        "gamma_base_scale": float(gamma0),
        "gamma_multiplier": float(recipe["gamma_multiplier"]),
        "gamma_scale_variance_float64": float(var),
        "probability": False,
        "class_weight": "balanced",
        "tol": 0.001,
        "max_iter": 100000,
        "cache_size": 200,
        "scaled": True,
        "recipe_id": recipe["id"],
        "warnings": warn_rows,
    }
    if any("ConvergenceWarning" in w for w in warn_rows):
        meta["convergence_warning"] = True
    return PredictionBundle(
        train_score=tr_s,
        train_prob=tr_p,
        train_pred=tr_pred,
        validation_score=va_s,
        validation_prob=va_p,
        validation_pred=va_pred,
        state=state,
        state_meta=meta,
        warnings=warn_rows,
    )


def fit_new_recipe(feature: FeatureSet, recipe_id: str) -> PredictionBundle:
    recipe = RECIPE_BY_ID[recipe_id]
    if recipe["kind"] == "svm_grid":
        return fit_svm_grid(feature, recipe)
    if recipe["kind"] == "logistic":
        return base.fit_recipe(feature, recipe)
    return base.fit_recipe(feature, recipe)


def make_null_raw_pca_features(
    old_audit: Mapping[str, Any], run_dir: Path
) -> tuple[list[FeatureSet], list[dict[str, Any]]]:
    source = base.load_source_tensor(Path(old_audit["source_tensor"]["path"]))
    by_perm: dict[int, dict[str, Mapping[str, Any]]] = defaultdict(dict)
    for entry in old_audit["null_fits"]:
        spec = entry["fit_spec"]
        by_perm[int(spec["permutation_index"])][str(spec["objective"])] = entry
    features: list[FeatureSet] = []
    pca_rows: list[dict[str, Any]] = []
    for perm in range(20):
        pair = by_perm[perm]
        if set(pair) != set(base.CEBRA_OBJECTIVES):
            raise ValueError(f"missing CEBRA null pair for permutation {perm}")
        entry = pair["cebra_time"]
        other = pair["cebra_behavior"]
        for field in (
            "generated_manifest_sha256",
            "exact_manifest_sha256",
            "train_array_sha256",
            "eval_array_sha256",
        ):
            if entry[field] != other[field]:
                raise ValueError(f"null world {perm} objective mismatch in {field}")
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
        Xtr3, ytr, _ = base.reconstruct_rows_from_manifest(
            Xsrc=source["Xsrc"],
            Msrc=source["Msrc"],
            source_index=source["source_index"],
            cell_ids=source["cell_ids"],
            manifest=gen_manifest,
            row_field="pseudo_row",
        )
        Xev3, yev, ordered_eval = base.reconstruct_rows_from_manifest(
            Xsrc=source["Xsrc"],
            Msrc=source["Msrc"],
            source_index=source["source_index"],
            cell_ids=source["cell_ids"],
            manifest=eval_manifest,
            row_field="product_row",
        )
        if base.ndarray_sha256(Xtr3) != entry["train_array_sha256"]:
            raise ValueError(f"raw null train hash mismatch world {perm}")
        if base.ndarray_sha256(Xev3) != entry["eval_array_sha256"]:
            raise ValueError(f"raw null validation hash mismatch world {perm}")
        meta = {
            "is_null": True,
            "family_role": "matched_raw_pca_null",
            "permutation_index": perm,
            "assembly_seed": 0,
            "optimizer_seed": 0,
            "source_tensor_sha256": old_audit["source_tensor"]["sha256"],
            "source_train_array_sha256": base.ndarray_sha256(Xtr3),
            "source_validation_array_sha256": base.ndarray_sha256(Xev3),
            "cebra_time_fit_id": entry["fit_id"],
            "cebra_behavior_fit_id": other["fit_id"],
        }
        raw_id = stable_hash({"null_raw": meta})[:20]
        features.append(
            FeatureSet(
                raw_id,
                "raw",
                "raw_binned_29cells_x_10bins_flat290",
                base.flatten_raw_binned(Xtr3),
                ytr,
                base.flatten_raw_binned(Xev3),
                yev,
                base.exact_class_weights(yev),
                ordered_eval,
                meta,
            )
        )
        started = time.time()
        append_event(
            run_dir,
            {"event": "pca_started", "permutation_index": perm, "time": started},
        )
        Xp_tr, Xp_ev, state = base.pca8_fit_transform(Xtr3, Xev3)
        pca_id = stable_hash({"null_pca8": meta})[:20]
        pca_npz = run_dir / "pca_transforms" / f"null_pca_perm{perm:02d}.npz"
        pca_digest = base.save_npz_exact(pca_npz, **state)
        pca_rows.append(
            {
                "permutation_index": perm,
                "pca_transform_id": pca_id,
                "pca_npz": str(pca_npz.relative_to(run_dir)),
                "pca_npz_sha256": pca_digest,
                "fit_counted": True,
                "svd_solver": "full",
                "n_components": 8,
                "whiten": False,
                "observed_pca_fit": False,
                "wall_seconds": time.time() - started,
                "train_feature_sha256": base.ndarray_sha256(Xp_tr),
                "validation_feature_sha256": base.ndarray_sha256(Xp_ev),
            }
        )
        write_json(
            run_dir / "pca_transforms" / f"null_pca_perm{perm:02d}.json", pca_rows[-1]
        )
        append_event(
            run_dir,
            {
                "event": "pca_complete",
                "permutation_index": perm,
                "time": time.time(),
                "ledger": pca_rows[-1],
            },
        )
        features.append(
            FeatureSet(
                pca_id,
                "pca",
                "train_only_cellspace_pca8_per_bin_flat80",
                Xp_tr,
                ytr,
                Xp_ev,
                yev,
                base.exact_class_weights(yev),
                ordered_eval,
                {**meta, "pca_transform_id": pca_id, "pca_npz_sha256": pca_digest},
            )
        )
    return features, pca_rows


# ---------------------------------------------------------------------------
# Metrics, diagnostics, persistence


def persist_readout(
    run_dir: Path,
    feature: FeatureSet,
    recipe_id: str,
    bundle: PredictionBundle,
    *,
    run_fit_counted: bool,
    reused_from: str | None = None,
) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    model_meta, rows, pred_rows = base.save_model_and_predictions(
        run_dir, feature, recipe_id, bundle
    )
    pred_npz = run_dir / "predictions" / f"{model_meta['readout_id']}.npz"
    pred_digest = base.save_npz_exact(
        pred_npz,
        train_score=bundle.train_score,
        train_pred=bundle.train_pred.astype(np.int64),
        train_prob=np.asarray(
            [] if bundle.train_prob is None else bundle.train_prob, dtype=np.float64
        ),
        validation_score=bundle.validation_score,
        validation_pred=bundle.validation_pred.astype(np.int64),
        validation_prob=np.asarray(
            [] if bundle.validation_prob is None else bundle.validation_prob,
            dtype=np.float64,
        ),
    )
    model_meta.update(
        {
            "prediction_npz": str(pred_npz.relative_to(run_dir)),
            "prediction_npz_sha256": pred_digest,
            "run_fit_counted": bool(run_fit_counted),
            "reused_from": reused_from or "",
        }
    )
    write_json(run_dir / "models" / f"{model_meta['readout_id']}.json", model_meta)
    augment_metric_rows(rows, feature, bundle)
    ledger = {
        "readout_id": model_meta["readout_id"],
        "feature_id": feature.feature_id,
        "feature_kind": feature.kind,
        "representation": feature.representation,
        "recipe_id": recipe_id,
        "run_fit_counted": int(run_fit_counted),
        "reused_prior_readout": int(bool(reused_from)),
        "cebra_fit_counted": 0,
        "observed_pca_fit_counted": 0,
        "warnings": "; ".join(bundle.warnings),
        **feature.metadata,
        "model_npz": model_meta["model_npz"],
        "prediction_npz": model_meta["prediction_npz"],
    }
    return model_meta, rows, pred_rows, ledger


def augment_metric_rows(
    rows: list[dict[str, Any]], feature: FeatureSet, bundle: PredictionBundle
) -> None:
    by_split = {
        "train_sampled": (
            feature.y_train,
            base.exact_class_weights(feature.y_train),
            bundle.train_score,
            bundle.train_prob,
        ),
        "validation_exact_q": (
            feature.y_validation,
            feature.validation_weights,
            bundle.validation_score,
            bundle.validation_prob,
        ),
    }
    coef = bundle.state.get("coef")
    coef_l2 = float(np.linalg.norm(coef)) if coef is not None else None
    coef_l1 = float(np.sum(np.abs(coef))) if coef is not None else None
    gamma = (
        float(bundle.state["gamma"].reshape(-1)[0]) if "gamma" in bundle.state else None
    )
    for row in rows:
        y, weights, score, prob = by_split[row["split"]]
        w = np.asarray(weights, dtype=np.float64)
        w = w / w.sum()
        smean = float(np.sum(w * score))
        row["weighted_margin_spread"] = float(np.sqrt(np.sum(w * (score - smean) ** 2)))
        if prob is None:
            row["weighted_probability_spread"] = None
            row["probability_near_half_fraction"] = None
        else:
            pmean = float(np.sum(w * prob))
            row["weighted_probability_spread"] = float(
                np.sqrt(np.sum(w * (prob - pmean) ** 2))
            )
            row["probability_near_half_fraction"] = float(
                np.sum(w * (np.abs(prob - 0.5) <= 0.05))
            )
        row["coef_l2_norm"] = coef_l2
        row["coef_l1_norm"] = coef_l1
        row["svm_effective_gamma"] = gamma
        row["svm_support_vectors"] = (
            int(np.asarray(bundle.state["support_vectors"]).shape[0])
            if "support_vectors" in bundle.state
            else None
        )


def temperature_rows(
    features: Mapping[str, FeatureSet],
    bundles: Mapping[tuple[str, str], PredictionBundle],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for fid, feature in sorted(features.items()):
        if as_bool(feature.metadata.get("is_null")):
            continue
        key = (fid, "logistic_scaled_c1")
        if key not in bundles:
            continue
        base_bundle = bundles[key]
        for T in TEMPERATURES:
            bundle = PredictionBundle(
                train_score=base_bundle.train_score / T,
                train_prob=expit(base_bundle.train_score / T),
                train_pred=base_bundle.train_pred,
                validation_score=base_bundle.validation_score / T,
                validation_prob=expit(base_bundle.validation_score / T),
                validation_pred=base_bundle.validation_pred,
                state={},
                state_meta={"temperature": T},
                warnings=[],
            )
            mrows = base.metric_rows_for_bundle(feature, f"temperature_T{T:g}", bundle)
            augment_metric_rows(mrows, feature, bundle)
            baseline_rows = base.metric_rows_for_bundle(
                feature, "logistic_scaled_c1", base_bundle
            )
            for transformed, original in zip(mrows, baseline_rows, strict=True):
                if any(
                    abs(transformed[k] - original[k]) > 1e-12
                    for k in ("balanced_accuracy", "auroc")
                ):
                    raise ValueError("positive temperature changed discrimination")
            for row in mrows:
                row["temperature"] = T
                row["source_recipe_id"] = "logistic_scaled_c1"
            rows.extend(mrows)
    return rows


def class_alignment_rows(
    features: Mapping[str, FeatureSet],
    bundles: Mapping[tuple[str, str], PredictionBundle],
) -> list[dict[str, Any]]:
    rows = []
    for fid, feature in sorted(features.items()):
        state = bundles[(fid, "logistic_scaled_c1")].state
        mean, scale = state["scaler_mean"], state["scaler_scale"]
        ztr = (feature.X_train - mean) / scale
        zva = (feature.X_validation - mean) / scale
        dt = ztr[feature.y_train == 1].mean(axis=0) - ztr[feature.y_train == 0].mean(
            axis=0
        )
        dv = zva[feature.y_validation == 1].mean(axis=0) - zva[
            feature.y_validation == 0
        ].mean(axis=0)
        nt = float(np.linalg.norm(dt))
        nv = float(np.linalg.norm(dv))
        rows.append(
            {
                "feature_id": fid,
                "feature_kind": feature.kind,
                "representation": feature.representation,
                **feature.metadata,
                "train_contrast_norm": nt,
                "validation_contrast_norm": nv,
                "contrast_cosine": None
                if nt == 0.0 or nv == 0.0
                else float(np.dot(dt, dv) / (nt * nv)),
            }
        )
    return rows


def source_sensitivity_rows(
    features: Mapping[str, FeatureSet],
    bundles: Mapping[tuple[str, str], PredictionBundle],
    *,
    worlds: int | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    if worlds is None:
        worlds = base.BOOTSTRAP_WORLDS
    boot_rows: list[dict[str, Any]] = []
    delete_rows: list[dict[str, Any]] = []
    world_rows: list[dict[str, Any]] = []
    observed = [f for f in features.values() if not as_bool(f.metadata.get("is_null"))]
    reference = observed[0]
    reference_lineage = base.validation_source_matrix(reference.validation_manifest)
    world_rows = base.source_bootstrap_worlds(reference, worlds=worlds)
    for feature in sorted(observed, key=lambda f: f.feature_id):
        lineage = base.validation_source_matrix(feature.validation_manifest)
        if any(not np.array_equal(lineage[k], reference_lineage[k]) for k in lineage):
            raise ValueError("source sensitivity requires identical observed lineage")
        recipes = [
            rid for rid in ALL_RECIPE_IDS if (feature.feature_id, rid) in bundles
        ]
        worlds_data = world_rows
        for wrow in worlds_data:
            weights = np.asarray(wrow["row_weights"], dtype=np.float64)
            base_ba = _metric_for_weights(
                feature,
                bundles[(feature.feature_id, "logistic_scaled_c1")],
                "logistic_scaled_c1",
                weights,
            )["balanced_accuracy"]
            for rid in recipes:
                row = _metric_for_weights(
                    feature, bundles[(feature.feature_id, rid)], rid, weights
                )
                row.update({"sensitivity": "source_bootstrap", "world": wrow["world"]})
                _add_delta(row, base_ba)
                boot_rows.append(row)
        source_ids = sorted(
            set(
                base.validation_source_matrix(feature.validation_manifest)["source_ids"]
                .reshape(-1)
                .tolist()
            )
        )
        for source_id in source_ids:
            weights, summary = base.delete_source_weights(feature, source_id)
            base_ba = None
            if weights is not None:
                base_ba = _metric_for_weights(
                    feature,
                    bundles[(feature.feature_id, "logistic_scaled_c1")],
                    "logistic_scaled_c1",
                    weights,
                )["balanced_accuracy"]
            for rid in recipes:
                prefix = {"sensitivity": "delete_source", **summary}
                if weights is None:
                    row = {
                        **prefix,
                        "feature_id": feature.feature_id,
                        "recipe_id": rid,
                        **feature.metadata,
                        "feature_kind": feature.kind,
                        "representation": feature.representation,
                    }
                else:
                    row = {
                        **prefix,
                        **_metric_for_weights(
                            feature, bundles[(feature.feature_id, rid)], rid, weights
                        ),
                    }
                    _add_delta(row, base_ba)
                delete_rows.append(row)
    return boot_rows, delete_rows, world_rows


def _metric_for_weights(
    feature: FeatureSet, bundle: PredictionBundle, recipe_id: str, weights: np.ndarray
) -> dict[str, Any]:
    # ponytail: only the prespecified BA sensitivity; avoid 228k unnecessary sklearn loss/AUC calls.
    y = feature.y_validation
    w = np.asarray(weights, dtype=np.float64)
    if w.shape != y.shape or np.any(w < 0) or not np.isfinite(w).all():
        raise ValueError("invalid source weights")
    recalls = [
        float(
            np.sum(w[y == label] * (bundle.validation_pred[y == label] == label))
            / np.sum(w[y == label])
        )
        for label in (0, 1)
    ]
    return {
        "feature_id": feature.feature_id,
        "feature_kind": feature.kind,
        "recipe_id": recipe_id,
        "representation": feature.representation,
        **{
            k: feature.metadata[k]
            for k in ("is_null", "objective", "assembly_seed", "optimizer_seed")
            if k in feature.metadata
        },
        "balanced_accuracy": 0.5 * sum(recalls),
    }


def _add_delta(row: dict[str, Any], base_ba: Any) -> None:
    ba = row.get("balanced_accuracy")
    row["delta_ba_vs_logistic_scaled_c1"] = (
        None if ba is None or base_ba is None else float(ba - base_ba)
    )


def compute_null_tails(metric_rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    rows = [r for r in metric_rows if r.get("split") == "validation_exact_q"]

    def sel(
        kind: str, null: bool, recipe_ids: Sequence[str], perm: int | None = None
    ) -> list[Mapping[str, Any]]:
        out = []
        for r in rows:
            if (
                as_bool(r.get("is_null")) != null
                or r.get("recipe_id") not in recipe_ids
            ):
                continue
            if kind == "cebra":
                if (
                    r.get("feature_kind") != "cebra"
                    or as_int_or_none(r.get("assembly_seed")) != 0
                    or as_int_or_none(r.get("optimizer_seed")) != 0
                ):
                    continue
                if r.get("objective") not in base.CEBRA_OBJECTIVES:
                    continue
            elif kind == "raw_pca":
                if (
                    r.get("feature_kind") not in {"raw", "pca"}
                    or as_int_or_none(r.get("assembly_seed")) != 0
                ):
                    continue
            if perm is not None and as_int_or_none(r.get("permutation_index")) != perm:
                continue
            out.append(r)
        return out

    def fam(name: str, kind: str, recipe_ids: Sequence[str]) -> dict[str, Any]:
        obs = sel(kind, False, recipe_ids)
        obs_max = max(
            (float(r["balanced_accuracy"]) - 0.5 for r in obs), default=math.nan
        )
        null_maxima = []
        for perm in range(20):
            vals = [
                float(r["balanced_accuracy"]) - 0.5
                for r in sel(kind, True, recipe_ids, perm)
            ]
            if vals:
                null_maxima.append(max(vals))
        exc = (
            sum(v >= obs_max - NULL_TOL for v in null_maxima)
            if not math.isnan(obs_max)
            else 0
        )
        return {
            "family": name,
            "observed_max_ba_minus_chance": obs_max,
            "null_family_maxima_ba_minus_chance": null_maxima,
            "null_worlds": len(null_maxima),
            "family_exceedances_inclusive": exc,
            "family_p_plus_one": (exc + 1) / (len(null_maxima) + 1)
            if null_maxima
            else None,
            "recipe_count": len(recipe_ids),
            "not_tests": [
                "not_seed_mean_p",
                "not_decoder_superiority_p",
                "not_full_adaptive_history_correction",
            ],
        }

    cebra = fam("cebra_family_2x19", "cebra", ALL_RECIPE_IDS)
    raw_pca = fam("raw_pca_family_2x15", "raw_pca", GRID_RECIPE_IDS)
    joint_obs = cebra["observed_max_ba_minus_chance"]
    if raw_pca["observed_max_ba_minus_chance"] is not None and not math.isnan(
        raw_pca["observed_max_ba_minus_chance"]
    ):
        joint_obs = max(joint_obs, raw_pca["observed_max_ba_minus_chance"])
    joint_null = [
        max(a, b)
        for a, b in zip(
            cebra["null_family_maxima_ba_minus_chance"],
            raw_pca["null_family_maxima_ba_minus_chance"],
            strict=False,
        )
    ]
    joint_exc = (
        sum(v >= joint_obs - NULL_TOL for v in joint_null)
        if not math.isnan(joint_obs)
        else 0
    )
    return {
        "schema_version": 1,
        "families": [
            cebra,
            raw_pca,
            {
                "family": "joint_family_68",
                "observed_max_ba_minus_chance": joint_obs,
                "null_family_maxima_ba_minus_chance": joint_null,
                "null_worlds": len(joint_null),
                "family_exceedances_inclusive": joint_exc,
                "family_p_plus_one": (joint_exc + 1) / (len(joint_null) + 1)
                if joint_null
                else None,
                "recipe_count": len(ALL_RECIPE_IDS) * 2 + len(GRID_RECIPE_IDS) * 2,
                "not_tests": [
                    "not_seed_mean_p",
                    "not_decoder_superiority_p",
                    "not_full_adaptive_history_correction",
                ],
            },
        ],
        "fixed_recipe_tails": fixed_recipe_tails(rows),
    }


def fixed_recipe_tails(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    out = []
    groups: dict[tuple[str, str, str], dict[str, list[float]]] = defaultdict(
        lambda: {"obs": [], "null": []}
    )
    for r in rows:
        if (
            r.get("split") != "validation_exact_q"
            or r.get("recipe_id") not in ALL_RECIPE_IDS
        ):
            continue
        kind = str(r.get("feature_kind"))
        if kind == "cebra":
            if (
                as_int_or_none(r.get("assembly_seed")) != 0
                or as_int_or_none(r.get("optimizer_seed")) != 0
            ):
                continue
            fam = f"cebra/{r.get('objective')}"
        elif (
            kind in {"raw", "pca"}
            and r.get("recipe_id") in GRID_RECIPE_IDS
            and as_int_or_none(r.get("assembly_seed")) == 0
        ):
            fam = kind
        else:
            continue
        bucket = "null" if as_bool(r.get("is_null")) else "obs"
        groups[(fam, kind, str(r["recipe_id"]))][bucket].append(
            float(r["balanced_accuracy"]) - 0.5
        )
    for (fam, kind, rid), vals in sorted(groups.items()):
        if not vals["obs"] or not vals["null"]:
            continue
        obs = max(vals["obs"])
        exc = sum(v >= obs - NULL_TOL for v in vals["null"])
        out.append(
            {
                "family_slice": fam,
                "feature_kind": kind,
                "recipe_id": rid,
                "observed_ba_minus_chance": obs,
                "null_worlds": len(vals["null"]),
                "exceedances_inclusive": exc,
                "p_plus_one_descriptive": (exc + 1) / (len(vals["null"]) + 1),
            }
        )
    return out


def mean_validation_rows(
    metric_rows: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    vals: dict[tuple[str, str, str, str], list[Mapping[str, Any]]] = defaultdict(list)
    for r in metric_rows:
        if r.get("split") == "validation_exact_q":
            key = (
                str(r.get("feature_kind")),
                str(r.get("objective", "")),
                str(r.get("is_null")),
                str(r.get("recipe_id")),
            )
            vals[key].append(r)
    out = []
    for (kind, objective, is_null, recipe), group in sorted(vals.items()):
        out.append(
            {
                "feature_kind": kind,
                "objective": objective,
                "is_null": is_null,
                "recipe_id": recipe,
                "n_feature_sets": len(group),
                "mean_balanced_accuracy": _mean(
                    row_float(r.get("balanced_accuracy")) for r in group
                ),
                "mean_auroc": _mean(row_float(r.get("auroc")) for r in group),
                "mean_log_loss": _mean(row_float(r.get("log_loss")) for r in group),
                "mean_delta_ba_vs_logistic_scaled_c1": _mean(
                    row_float(r.get("delta_ba_vs_logistic_scaled_c1")) for r in group
                ),
            }
        )
    return out


def _mean(values: Any) -> float | None:
    xs = [float(v) for v in values if v is not None]
    return None if not xs else float(sum(xs) / len(xs))


def expected_recipe_ids(feature: FeatureSet) -> tuple[str, ...]:
    if as_bool(feature.metadata.get("is_null")) and feature.kind in {"raw", "pca"}:
        return GRID_RECIPE_IDS
    return ALL_RECIPE_IDS


# ---------------------------------------------------------------------------
# Run and verify


def run_diagnosis(
    audit_manifest: Path,
    output_dir: Path,
    *,
    gate: str,
    token: str,
    runtime_cap_seconds: int = 1800,
    allow_tmp: bool = False,
) -> dict[str, Any]:
    output_dir = resolve_output(output_dir, allow_tmp=allow_tmp)
    require_fresh(output_dir)
    try:
        return _run_diagnosis(
            audit_manifest,
            output_dir,
            gate=gate,
            token=token,
            runtime_cap_seconds=runtime_cap_seconds,
            allow_tmp=allow_tmp,
        )
    except Exception as exc:
        if output_dir.exists():
            events_path = output_dir / "event_journal.jsonl"
            events = (
                [json.loads(line) for line in events_path.read_text().splitlines()]
                if events_path.exists()
                else []
            )
            failure = {
                "status": "incomplete",
                "error": repr(exc),
                "new_readouts_completed": sum(
                    e["event"] == "readout_complete" for e in events
                ),
                "new_readouts_started": sum(
                    e["event"] == "readout_started" for e in events
                ),
                "null_pca_completed": sum(e["event"] == "pca_complete" for e in events),
                "null_pca_started": sum(e["event"] == "pca_started" for e in events),
            }
            write_json(output_dir / "INCOMPLETE.json", failure)
            write_json(output_dir / "summary.json", failure)
            config = (
                read_json(output_dir / "run_config.json")
                if (output_dir / "run_config.json").exists()
                else {}
            )
            write_json(
                output_dir / "run_config.json", {**config, "status": "incomplete"}
            )
            append_event(
                output_dir, {"event": "failed", "time": time.time(), "error": repr(exc)}
            )
        raise


def _run_diagnosis(
    audit_manifest: Path,
    output_dir: Path,
    *,
    gate: str,
    token: str,
    runtime_cap_seconds: int = 1800,
    allow_tmp: bool = False,
) -> dict[str, Any]:
    output_dir = resolve_output(output_dir, allow_tmp=allow_tmp)
    require_fresh(output_dir)
    output_dir.mkdir(parents=True)
    started = time.time()
    audit = read_json(audit_manifest)
    audit["audit_manifest_path"] = str(audit_manifest)
    validate_gate(audit, gate, token)
    accepted_run = Path(audit["accepted_run"])
    prior_metas, prior_features = load_features(accepted_run)
    prior_model_metas = load_model_metas(accepted_run)
    _validate_prior_model_grid(
        prior_metas, prior_model_metas, full=not audit.get("synthetic", False)
    )
    old_audit = (
        read_json(accepted_run / "audit_manifest.json")
        if (accepted_run / "audit_manifest.json").exists()
        else {"source_tensor": audit.get("source_tensor", {}), "null_fits": []}
    )

    append_event(
        output_dir,
        {"event": "start", "time": time.time(), "audit_manifest": str(audit_manifest)},
    )
    write_json(output_dir / "audit_manifest.json", audit)
    write_json(
        output_dir / "run_config.json",
        {
            "status": "running",
            "started_unix_seconds": started,
            "code_sha256": audit["code_sha256"],
            "protocol_sha256": audit["protocol_sha256"],
            "dependency_hash": audit["dependency_hash"],
            "synthetic": bool(audit.get("synthetic")),
            "accepted_run": str(accepted_run),
            "bootstrap_worlds": base.BOOTSTRAP_WORLDS,
        },
    )
    snapshots = output_dir / "source_snapshots"
    snapshots.mkdir()
    for source_path in (Path(__file__), Path(base.__file__), PROTOCOL_PATH):
        shutil.copy2(source_path, snapshots / source_path.name)
    feature_metas: list[dict[str, Any]] = []
    for feature in prior_features.values():
        feature_metas.append(base.save_feature(output_dir, feature))
    null_features, pca_rows = make_null_raw_pca_features(old_audit, output_dir)
    for feature in null_features:
        feature_metas.append(base.save_feature(output_dir, feature))
    features = {**prior_features, **{f.feature_id: f for f in null_features}}
    write_json(output_dir / "feature_manifest.json", {"features": feature_metas})
    write_csv(output_dir / "pca_fit_ledger.csv", pca_rows)

    bundles: dict[tuple[str, str], PredictionBundle] = {}
    model_metas: list[dict[str, Any]] = []
    metric_rows: list[dict[str, Any]] = []
    pred_rows: list[dict[str, Any]] = []
    ledger_rows: list[dict[str, Any]] = []
    prior_by_key = {(m["feature_id"], m["recipe_id"]): m for m in prior_model_metas}

    for key, old_meta in sorted(prior_by_key.items()):
        feature = prior_features[key[0]]
        state = base.load_model(accepted_run, old_meta)
        estimator = base.load_estimator(accepted_run, old_meta)
        bundle = base.predict_from_saved_state(
            feature, key[1], state, old_meta["state_meta"], estimator
        )
        if estimator is not None:
            bundle = PredictionBundle(
                train_score=bundle.train_score,
                train_prob=bundle.train_prob,
                train_pred=bundle.train_pred,
                validation_score=bundle.validation_score,
                validation_prob=bundle.validation_prob,
                validation_pred=bundle.validation_pred,
                state=bundle.state,
                state_meta=bundle.state_meta,
                warnings=bundle.warnings,
                estimator=estimator,
            )
        bundles[key] = bundle
        mm, mr, pr, lr = persist_readout(
            output_dir,
            feature,
            key[1],
            bundle,
            run_fit_counted=False,
            reused_from=str(accepted_run),
        )
        model_metas.append(mm)
        metric_rows.extend(mr)
        pred_rows.extend(pr)
        ledger_rows.append(lr)
        append_event(
            output_dir, {"event": "readout_reused", "time": time.time(), "ledger": lr}
        )

    old_feature_ids = set(prior_features)
    for feature in sorted(features.values(), key=lambda f: f.feature_id):
        rids = (
            GRID_RECIPE_IDS
            if feature.feature_id not in old_feature_ids
            else NEW_EXISTING_RECIPE_IDS
        )
        for rid in rids:
            if time.time() - started > runtime_cap_seconds:
                raise TimeoutError("runtime cap before fitting")
            t0 = time.time()
            append_event(
                output_dir,
                {
                    "event": "readout_started",
                    "time": t0,
                    "feature_id": feature.feature_id,
                    "recipe_id": rid,
                },
            )
            bundle = fit_new_recipe(feature, rid)
            bundles[(feature.feature_id, rid)] = bundle
            mm, mr, pr, lr = persist_readout(
                output_dir, feature, rid, bundle, run_fit_counted=True
            )
            lr["wall_seconds"] = time.time() - t0
            model_metas.append(mm)
            metric_rows.extend(mr)
            pred_rows.extend(pr)
            ledger_rows.append(lr)
            append_event(
                output_dir,
                {
                    "event": "readout_complete",
                    "time": time.time(),
                    "feature_id": feature.feature_id,
                    "recipe_id": rid,
                    "run_fit_counted": True,
                    "ledger": lr,
                },
            )
            if time.time() - started > runtime_cap_seconds:
                write_incomplete(
                    output_dir,
                    "runtime_cap_seconds",
                    feature_metas,
                    model_metas,
                    metric_rows,
                    pred_rows,
                    ledger_rows,
                    pca_rows,
                )
                raise TimeoutError("runtime cap reached; incomplete attempt preserved")

    validate_model_completeness(features, model_metas)
    base.apply_baseline_deltas(metric_rows)
    temp_rows = temperature_rows(features, bundles)
    align_rows = class_alignment_rows(features, bundles)
    boot_rows, delete_rows, world_rows = source_sensitivity_rows(features, bundles)
    if not audit.get("synthetic") and stable_hash(world_rows) != stable_hash(
        read_json(accepted_run / "source_bootstrap_worlds.json")["worlds"]
    ):
        raise ValueError("source worlds differ from accepted fixed worlds")
    if time.time() - started > runtime_cap_seconds:
        raise TimeoutError("runtime cap during diagnostics")
    tails = compute_null_tails(metric_rows)
    mean_rows = mean_validation_rows(metric_rows)
    summary = make_summary(
        features,
        model_metas,
        ledger_rows,
        pca_rows,
        metric_rows,
        temp_rows,
        boot_rows,
        delete_rows,
        tails,
        started,
    )
    if not audit.get("synthetic", False):
        validate_full_summary(summary)
    write_outputs(
        output_dir,
        feature_metas,
        model_metas,
        metric_rows,
        pred_rows,
        ledger_rows,
        pca_rows,
        temp_rows,
        align_rows,
        boot_rows,
        delete_rows,
        world_rows,
        tails,
        mean_rows,
        summary,
        audit,
        gate,
        token,
        started,
        runtime_cap_seconds,
    )
    append_event(
        output_dir,
        {"event": "complete", "time": time.time(), "summary": summary["counts"]},
    )
    return summary


def validate_gate(audit: Mapping[str, Any], gate: str, token: str) -> None:
    if gate != FIT_GATE_FLAG:
        raise ValueError("refusing run without exact fit gate flag")
    if token != audit.get("gate_token"):
        raise ValueError("gate token mismatch")
    if audit.get("code_sha256") != sha256_file(Path(__file__)):
        raise ValueError("code hash changed since audit")
    if audit.get("protocol_sha256") != sha256_file(PROTOCOL_PATH):
        raise ValueError("protocol hash changed since audit")
    if (
        gate_token(gate_payload(Path(audit["accepted_run"]), audit["artifact_hashes"]))
        != token
    ):
        raise ValueError("audit payload fields or code/helper/runtime identity changed")
    if audit.get("status") != "audited" or token != gate_token(audit["gate_payload"]):
        raise ValueError("audit status or gate payload mismatch")
    if audit.get("dependency_hash") != dependency_hash():
        raise ValueError("dependency/runtime hash changed since audit")
    accepted = Path(audit["accepted_run"])
    for name, digest in audit["artifact_hashes"].items():
        if sha256_file(accepted / name) != digest:
            raise ValueError(f"accepted artifact changed since audit: {name}")
    if not audit.get("synthetic"):
        validate_accepted_inputs(accepted)


def validate_model_completeness(
    features: Mapping[str, FeatureSet], model_metas: Sequence[Mapping[str, Any]]
) -> None:
    have = {(m["feature_id"], m["recipe_id"]) for m in model_metas}
    if len(have) != len(model_metas):
        raise ValueError("duplicate model feature/recipe pairs")
    expected = {
        (f.feature_id, rid) for f in features.values() for rid in expected_recipe_ids(f)
    }
    if have != expected:
        missing = sorted(expected - have)[:8]
        extra = sorted(have - expected)[:8]
        raise ValueError(f"readout grid incomplete missing={missing} extra={extra}")


def make_summary(
    features: Mapping[str, FeatureSet],
    model_metas: Sequence[Mapping[str, Any]],
    ledger_rows: Sequence[Mapping[str, Any]],
    pca_rows: Sequence[Mapping[str, Any]],
    metric_rows: Sequence[Mapping[str, Any]],
    temp_rows: Sequence[Mapping[str, Any]],
    boot_rows: Sequence[Mapping[str, Any]],
    delete_rows: Sequence[Mapping[str, Any]],
    tails: Mapping[str, Any],
    started: float,
) -> dict[str, Any]:
    old_features = [
        f
        for f in features.values()
        if not (as_bool(f.metadata.get("is_null")) and f.kind in {"raw", "pca"})
    ]
    counts = {
        "features": len(features),
        "prior_or_observed_features": len(old_features),
        "observed_features": sum(
            not as_bool(f.metadata.get("is_null")) for f in features.values()
        ),
        "cebra_null_features": sum(
            f.kind == "cebra" and as_bool(f.metadata.get("is_null"))
            for f in features.values()
        ),
        "raw_pca_null_features": sum(
            f.kind in {"raw", "pca"} and as_bool(f.metadata.get("is_null"))
            for f in features.values()
        ),
        "models": len(model_metas),
        "metric_rows": len(metric_rows),
        "reused_prior_readouts": sum(
            int(r.get("reused_prior_readout", 0)) for r in ledger_rows
        ),
        "total_new_readout_fits": sum(
            int(r.get("run_fit_counted", 0)) for r in ledger_rows
        ),
        "new_train_only_pca_fits": sum(
            1 for r in pca_rows if as_bool(r.get("fit_counted"))
        ),
        "new_cebra_fits": 0,
        "new_observed_pca_fits": 0,
        "temperature_rows": len(temp_rows),
        "source_bootstrap_rows": len(boot_rows),
        "delete_source_rows": len(delete_rows),
    }
    return {
        "schema_version": 1,
        "status": "complete",
        "counts": counts,
        "null_family_tails": tails,
        "wall_seconds": time.time() - started,
    }


def validate_full_summary(summary: Mapping[str, Any]) -> None:
    exp = expected_full_counts()
    c = summary["counts"]
    checks = {
        "total_features_after_run": c["features"],
        "observed_feature_sets": c["observed_features"],
        "cebra_null_feature_sets": c["cebra_null_features"],
        "raw_pca_null_feature_sets": c["raw_pca_null_features"],
        "reused_prior_readouts": c["reused_prior_readouts"],
        "total_new_readout_fits": c["total_new_readout_fits"],
        "total_readout_records": c["models"],
        "new_train_only_pca_fits": c["new_train_only_pca_fits"],
        "new_cebra_fits": c["new_cebra_fits"],
        "new_observed_pca_fits": c["new_observed_pca_fits"],
        "source_bootstrap_rows": c["source_bootstrap_rows"],
        "delete_source_rows": c["delete_source_rows"],
    }
    bad = {k: (v, exp[k]) for k, v in checks.items() if v != exp[k]}
    if bad:
        raise ValueError(f"full protocol accounting mismatch: {bad}")


def write_outputs(
    run_dir: Path,
    feature_metas: Sequence[Mapping[str, Any]],
    model_metas: Sequence[Mapping[str, Any]],
    metric_rows: Sequence[Mapping[str, Any]],
    pred_rows: Sequence[Mapping[str, Any]],
    ledger_rows: Sequence[Mapping[str, Any]],
    pca_rows: Sequence[Mapping[str, Any]],
    temp_rows: Sequence[Mapping[str, Any]],
    align_rows: Sequence[Mapping[str, Any]],
    boot_rows: Sequence[Mapping[str, Any]],
    delete_rows: Sequence[Mapping[str, Any]],
    world_rows: Sequence[Mapping[str, Any]],
    tails: Mapping[str, Any],
    mean_rows: Sequence[Mapping[str, Any]],
    summary: Mapping[str, Any],
    audit: Mapping[str, Any],
    gate: str,
    token: str,
    started: float,
    runtime_cap_seconds: int,
) -> None:
    write_json(run_dir / "feature_manifest.json", {"features": list(feature_metas)})
    write_json(run_dir / "model_manifest.json", {"models": list(model_metas)})
    write_csv(run_dir / "fit_ledger.csv", ledger_rows)
    write_csv(run_dir / "readout_metrics.csv", metric_rows)
    write_csv(run_dir / "readout_predictions.csv", pred_rows)
    write_csv(run_dir / "pca_fit_ledger.csv", pca_rows)
    write_csv(run_dir / "confidence_temperature_metrics.csv", temp_rows)
    write_csv(run_dir / "class_contrast_alignment.csv", align_rows)
    write_csv(run_dir / "source_bootstrap_metrics.csv", boot_rows)
    write_csv(run_dir / "delete_source_influence.csv", delete_rows)
    write_json(run_dir / "source_bootstrap_worlds.json", {"worlds": list(world_rows)})
    write_json(run_dir / "null_family_tails.json", tails)
    write_csv(run_dir / "mean_validation_metrics.csv", mean_rows)
    write_json(run_dir / "summary.json", summary)
    write_json(
        run_dir / "run_config.json",
        {
            **read_json(run_dir / "run_config.json"),
            "status": summary["status"],
            "audit_manifest_sha256": sha256_file(
                Path(audit.get("audit_manifest_path", ""))
            )
            if audit.get("audit_manifest_path")
            else None,
            "audit_copy_sha256": sha256_file(run_dir / "audit_manifest.json"),
            "base_code_sha256": audit.get("gate_payload", {}).get("base_code_sha256"),
            "gate_flag": gate,
            "gate_token": token,
            "protocol_sha256": sha256_file(PROTOCOL_PATH),
            "code_sha256": sha256_file(Path(__file__)),
            "dependency_hash": dependency_hash(),
            "recipes": [RECIPE_BY_ID[rid] for rid in ALL_RECIPE_IDS],
            "temperature_values": list(TEMPERATURES),
            "runtime_cap_seconds": runtime_cap_seconds,
            "started_unix_seconds": started,
            "completed_unix_seconds": time.time(),
            "runtime": base.runtime_info(),
            "git": base.git_state(),
        },
    )
    snapshots = run_dir / "source_snapshots"
    snapshots.mkdir(exist_ok=True)
    # Execution snapshots were captured before any fitting; do not replace them here.


def append_event(run_dir: Path, payload: Mapping[str, Any]) -> None:
    base.append_jsonl(run_dir / "event_journal.jsonl", payload)


def write_incomplete(
    run_dir: Path,
    reason: str,
    feature_metas: Sequence[Mapping[str, Any]],
    model_metas: Sequence[Mapping[str, Any]],
    metric_rows: Sequence[Mapping[str, Any]],
    pred_rows: Sequence[Mapping[str, Any]],
    ledger_rows: Sequence[Mapping[str, Any]],
    pca_rows: Sequence[Mapping[str, Any]],
) -> None:
    write_json(
        run_dir / "INCOMPLETE.json",
        {
            "status": "incomplete",
            "reason": reason,
            "models": len(model_metas),
            "new_fits": sum(int(r.get("run_fit_counted", 0)) for r in ledger_rows),
        },
    )
    write_outputs(
        run_dir,
        feature_metas,
        model_metas,
        metric_rows,
        pred_rows,
        ledger_rows,
        pca_rows,
        [],
        [],
        [],
        [],
        [],
        {"families": []},
        [],
        read_json(run_dir / "INCOMPLETE.json"),
        {},
        "",
        "",
        time.time(),
        0,
    )


def verify_run(run_dir: Path, output: Path | None = None) -> dict[str, Any]:
    with ExitStack() as stack:
        for entry in (
            "sklearn.linear_model.LogisticRegression.fit",
            "sklearn.svm.SVC.fit",
            "sklearn.neighbors.KNeighborsClassifier.fit",
            "sklearn.preprocessing.StandardScaler.fit",
            "sklearn.decomposition.PCA.fit",
            "sklearn.decomposition.PCA.fit_transform",
        ):
            stack.enter_context(
                patch(
                    entry,
                    side_effect=AssertionError("fitting forbidden during verification"),
                )
            )
        return _verify_run(run_dir, output)


def verify_provenance(run_dir: Path) -> dict[str, Any]:
    config = read_json(run_dir / "run_config.json")
    audit = read_json(run_dir / "audit_manifest.json")
    if config.get("status") != "complete" or (run_dir / "INCOMPLETE.json").exists():
        raise ValueError("run is incomplete")
    if sha256_file(run_dir / "audit_manifest.json") != config["audit_copy_sha256"]:
        raise ValueError("saved audit hash mismatch")
    if (
        config["gate_token"] != gate_token(audit["gate_payload"])
        or config["gate_flag"] != FIT_GATE_FLAG
    ):
        raise ValueError("saved gate mismatch")
    if config["accepted_run"] != audit["accepted_run"] or config["synthetic"] != bool(
        audit.get("synthetic")
    ):
        raise ValueError("saved input authority mismatch")
    for key, name in (
        ("code_sha256", Path(__file__).name),
        ("base_code_sha256", Path(base.__file__).name),
        ("protocol_sha256", PROTOCOL_PATH.name),
    ):
        if (
            config[key] != audit["gate_payload"][key]
            or sha256_file(run_dir / "source_snapshots" / name) != config[key]
        ):
            raise ValueError(f"source snapshot provenance mismatch: {name}")
    if config["recipes"] != [RECIPE_BY_ID[rid] for rid in ALL_RECIPE_IDS] or config[
        "temperature_values"
    ] != list(TEMPERATURES):
        raise ValueError("saved recipe configuration mismatch")
    for name, digest in audit["artifact_hashes"].items():
        if sha256_file(Path(audit["accepted_run"]) / name) != digest:
            raise ValueError(f"accepted source artifact changed: {name}")
    return config


def verify_pca_states(
    run_dir: Path, features: Mapping[str, FeatureSet], rows: Sequence[Mapping[str, Any]]
) -> None:
    if len({r["permutation_index"] for r in rows}) != len(rows):
        raise ValueError("duplicate null PCA worlds")
    for row in rows:
        path = run_dir / str(row["pca_npz"])
        if sha256_file(path) != row["pca_npz_sha256"] or as_bool(
            row["observed_pca_fit"]
        ):
            raise ValueError("PCA state hash/role mismatch")
        perm = int(row["permutation_index"])
        raw = next(
            f
            for f in features.values()
            if f.kind == "raw"
            and as_bool(f.metadata.get("is_null"))
            and f.metadata["permutation_index"] == perm
        )
        projected = next(
            f
            for f in features.values()
            if f.kind == "pca"
            and f.metadata.get("pca_transform_id") == row["pca_transform_id"]
        )
        with np.load(path, allow_pickle=False) as state:
            cells = len(state["mean"])
            for split in ("train", "validation"):
                X = getattr(raw, f"X_{split}")
                target = getattr(projected, f"X_{split}")
                if base.ndarray_sha256(target) != row[f"{split}_feature_sha256"]:
                    raise ValueError("PCA feature ledger hash mismatch")
                replay = base.pca8_transform_from_state(
                    X.reshape(len(X), cells, X.shape[1] // cells), state
                )
                np.testing.assert_allclose(replay, target, atol=TOL, rtol=0)


def verify_fit_accounting(
    run_dir: Path,
    features: Mapping[str, FeatureSet],
    models: Sequence[Mapping[str, Any]],
) -> None:
    ledger = csv_rows(run_dir / "fit_ledger.csv")
    by_id = {row["readout_id"]: row for row in ledger}
    if len(by_id) != len(ledger) or set(by_id) != {m["readout_id"] for m in models}:
        raise ValueError("fit ledger row identities mismatch")
    for model in models:
        row = by_id[model["readout_id"]]
        feature = features[model["feature_id"]]
        new = (
            feature.kind in {"raw", "pca"} and as_bool(feature.metadata.get("is_null"))
        ) or model["recipe_id"] in NEW_EXISTING_RECIPE_IDS
        if (
            as_bool(row["run_fit_counted"]) != new
            or as_bool(model["run_fit_counted"]) != new
            or as_bool(row["reused_prior_readout"]) == new
        ):
            raise ValueError("fit/reuse accounting flags mismatch")
        for key in ("feature_id", "recipe_id", "model_npz", "prediction_npz"):
            if row[key] != str(model[key]):
                raise ValueError(f"fit ledger identity mismatch: {key}")
    events = [
        json.loads(line)
        for line in (run_dir / "event_journal.jsonl").read_text().splitlines()
    ]
    if (
        not events
        or events[-1]["event"] != "complete"
        or any(e["event"] == "failed" for e in events)
    ):
        raise ValueError("event lifecycle is incomplete")
    started = [
        (e["feature_id"], e["recipe_id"])
        for e in events
        if e["event"] == "readout_started"
    ]
    completed = [
        (e["feature_id"], e["recipe_id"])
        for e in events
        if e["event"] == "readout_complete"
    ]
    expected = [
        (m["feature_id"], m["recipe_id"]) for m in models if m["run_fit_counted"]
    ]
    if Counter(started) != Counter(expected) or Counter(completed) != Counter(expected):
        raise ValueError("started/completed readout event mismatch")
    event_ledger = [
        e["ledger"]
        for e in events
        if e["event"] in {"readout_reused", "readout_complete"}
    ]
    base.compare_row_sets(
        "event ledger", event_ledger, ledger, key_fields=("readout_id",)
    )
    pcas = csv_rows(run_dir / "pca_fit_ledger.csv")
    if Counter(
        int(e["permutation_index"]) for e in events if e["event"] == "pca_started"
    ) != Counter(int(r["permutation_index"]) for r in pcas):
        raise ValueError("PCA attempt count mismatch")
    base.compare_row_sets(
        "PCA event ledger",
        [e["ledger"] for e in events if e["event"] == "pca_complete"],
        pcas,
        key_fields=("permutation_index",),
    )


def _verify_run(run_dir: Path, output: Path | None = None) -> dict[str, Any]:
    config = verify_provenance(run_dir)
    features_meta, features = load_features(run_dir)
    if len(features_meta) != len(features):
        raise ValueError("duplicate feature IDs")
    model_metas = load_model_metas(run_dir)
    validate_model_completeness(features, model_metas)
    verify_fit_accounting(run_dir, features, model_metas)
    bundles: dict[tuple[str, str], PredictionBundle] = {}
    metric_rows: list[dict[str, Any]] = []
    pred_rows: list[dict[str, Any]] = []
    for meta in model_metas:
        feature = features[meta["feature_id"]]
        state = base.load_model(run_dir, meta)
        estimator = base.load_estimator(run_dir, meta)
        bundle = base.predict_from_saved_state(
            feature, meta["recipe_id"], state, meta["state_meta"], estimator
        )
        _verify_prediction_npz(run_dir, meta, bundle)
        bundles[(feature.feature_id, meta["recipe_id"])] = bundle
        rows = base.metric_rows_for_bundle(feature, meta["recipe_id"], bundle)
        augment_metric_rows(rows, feature, bundle)
        metric_rows.extend(rows)
        pred_rows.extend(
            _prediction_rows(meta["readout_id"], feature, meta["recipe_id"], bundle)
        )
    base.apply_baseline_deltas(metric_rows)
    temp_rows = temperature_rows(features, bundles)
    align_rows = class_alignment_rows(features, bundles)
    pca_rows = (
        csv_rows(run_dir / "pca_fit_ledger.csv")
        if (run_dir / "pca_fit_ledger.csv").exists()
        else []
    )
    verify_pca_states(run_dir, features, pca_rows)
    world_count = int(config["bootstrap_worlds"])
    if not config["synthetic"] and world_count != base.BOOTSTRAP_WORLDS:
        raise ValueError("wrong source bootstrap world count")
    boot_rows, delete_rows, world_rows = source_sensitivity_rows(
        features, bundles, worlds=world_count
    )
    if stable_hash(world_rows) != stable_hash(
        read_json(run_dir / "source_bootstrap_worlds.json")["worlds"]
    ):
        raise ValueError("source bootstrap draws/weights do not replay")
    if not config["synthetic"] and stable_hash(world_rows) != stable_hash(
        read_json(Path(config["accepted_run"]) / "source_bootstrap_worlds.json")[
            "worlds"
        ]
    ):
        raise ValueError("source worlds do not match accepted worlds")
    tails = compute_null_tails(metric_rows)
    mean_rows = mean_validation_rows(metric_rows)
    comparisons = {
        "metrics": base.compare_row_sets(
            "metrics",
            metric_rows,
            csv_rows(run_dir / "readout_metrics.csv"),
            key_fields=("feature_id", "recipe_id", "split"),
        ),
        "predictions": base.compare_row_sets(
            "predictions",
            pred_rows,
            csv_rows(run_dir / "readout_predictions.csv"),
            key_fields=("readout_id", "split", "row"),
        ),
        "temperature": base.compare_row_sets(
            "temperature",
            temp_rows,
            csv_rows(run_dir / "confidence_temperature_metrics.csv"),
            key_fields=("feature_id", "recipe_id", "split", "temperature"),
        ),
        "alignment": base.compare_row_sets(
            "alignment",
            align_rows,
            csv_rows(run_dir / "class_contrast_alignment.csv"),
            key_fields=("feature_id",),
        ),
        "source_bootstrap": base.compare_row_sets(
            "source_bootstrap",
            boot_rows,
            csv_rows(run_dir / "source_bootstrap_metrics.csv"),
            key_fields=("feature_id", "recipe_id", "world"),
        ),
        "delete_source": base.compare_row_sets(
            "delete_source",
            delete_rows,
            csv_rows(run_dir / "delete_source_influence.csv"),
            key_fields=("feature_id", "recipe_id", "deleted_source_trial_id"),
        ),
        "means": base.compare_row_sets(
            "means",
            mean_rows,
            csv_rows(run_dir / "mean_validation_metrics.csv"),
            key_fields=("feature_kind", "objective", "is_null", "recipe_id"),
        ),
    }
    saved_summary = read_json(run_dir / "summary.json")
    if saved_summary.get("status") != "complete":
        raise ValueError("summary incomplete")
    if not config["synthetic"]:
        validate_full_summary(saved_summary)
        if len(pca_rows) != 20 or len(world_rows) != 200:
            raise ValueError("PCA/bootstrap full budget mismatch")
    summary = make_summary(
        features,
        model_metas,
        csv_rows(run_dir / "fit_ledger.csv"),
        pca_rows,
        metric_rows,
        temp_rows,
        boot_rows,
        delete_rows,
        tails,
        time.time(),
    )
    if saved_summary["counts"] != summary["counts"]:
        raise ValueError("summary count mismatch")
    if stable_hash(saved_summary["null_family_tails"]) != stable_hash(tails):
        raise ValueError("null-family tail summary mismatch")
    saved_tails = read_json(run_dir / "null_family_tails.json")
    if stable_hash(saved_tails) != stable_hash(tails):
        raise ValueError("null_family_tails.json mismatch")
    receipt = {
        "status": "verified",
        "run_dir": str(run_dir.resolve()),
        "features": len(features),
        "models": len(model_metas),
        "new_fits_during_verify": 0,
        "fit_methods_blocked": True,
        "pca_transforms_replayed": len(pca_rows),
        "comparisons": comparisons,
        "summary_counts": summary["counts"],
        "input_hashes": {
            p.name: sha256_file(p)
            for p in run_dir.iterdir()
            if p.is_file()
            and p.suffix in {".json", ".csv", ".jsonl"}
            and p.name != "verify_receipt.json"
        },
        "verifier_sha256": sha256_file(Path(__file__)),
    }
    if output is None:
        output = run_dir / "verify_receipt.json"
    write_json(output, receipt)
    return receipt


def _saved_bootstrap_world_count(run_dir: Path) -> int | None:
    path = run_dir / "source_bootstrap_worlds.json"
    if not path.exists():
        return None
    worlds = read_json(path).get("worlds", [])
    ids = {int(w["world"]) for w in worlds}
    return (max(ids) + 1) if ids else None


def _verify_prediction_npz(
    run_dir: Path, meta: Mapping[str, Any], bundle: PredictionBundle
) -> None:
    path = run_dir / str(meta["prediction_npz"])
    if sha256_file(path) != meta["prediction_npz_sha256"]:
        raise ValueError(f"prediction hash mismatch: {path}")
    z = np.load(path, allow_pickle=False)
    checks = {
        "train_score": bundle.train_score,
        "train_pred": bundle.train_pred,
        "validation_score": bundle.validation_score,
        "validation_pred": bundle.validation_pred,
        "train_prob": np.asarray(
            [] if bundle.train_prob is None else bundle.train_prob, dtype=np.float64
        ),
        "validation_prob": np.asarray(
            [] if bundle.validation_prob is None else bundle.validation_prob,
            dtype=np.float64,
        ),
    }
    for name, expected in checks.items():
        if name not in z.files or not np.array_equal(
            np.asarray(z[name]), np.asarray(expected)
        ):
            raise ValueError(f"prediction replay mismatch {meta['readout_id']}/{name}")


def _prediction_rows(
    readout_id: str, feature: FeatureSet, recipe_id: str, bundle: PredictionBundle
) -> list[dict[str, Any]]:
    rows = []
    for split, y, weights, pred, score, prob in (
        (
            "train_sampled",
            feature.y_train,
            base.exact_class_weights(feature.y_train),
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
            rows.append(
                {
                    "readout_id": readout_id,
                    "feature_id": feature.feature_id,
                    "recipe_id": recipe_id,
                    "split": split,
                    "row": i,
                    "true_label": base.INT_TO_LABEL[int(y[i])],
                    "pred_label": base.INT_TO_LABEL[int(pred[i])],
                    "score": float(score[i]),
                    "prob_present": "" if prob is None else float(prob[i]),
                    "evaluation_weight": float(weights[i]),
                }
            )
    return rows


def render_machine_report(
    run_dir: Path, output_dir: Path, *, allow_tmp: bool = False
) -> dict[str, Any]:
    output_dir = resolve_output(output_dir, allow_tmp=allow_tmp)
    require_fresh(output_dir)
    receipt = read_json(run_dir / "verify_receipt.json")
    if receipt.get("status") != "verified" or receipt.get("run_dir") != str(
        run_dir.resolve()
    ):
        raise ValueError("report requires a verified receipt for this run")
    for name, digest in receipt["input_hashes"].items():
        if sha256_file(run_dir / name) != digest:
            raise ValueError(f"report input changed after verification: {name}")
    output_dir.mkdir(parents=True)
    summary = read_json(run_dir / "summary.json")
    report = {
        "schema_version": 1,
        "run_dir": str(run_dir),
        "summary": summary,
        "files": {p.name: sha256_file(p) for p in run_dir.iterdir() if p.is_file()},
        "no_human_claim_authoring": True,
    }
    write_json(output_dir / "machine_report.json", report)
    shutil.copy2(
        run_dir / "mean_validation_metrics.csv",
        output_dir / "mean_validation_metrics.csv",
    )
    shutil.copy2(
        run_dir / "null_family_tails.json", output_dir / "null_family_tails.json"
    )
    return report


# ---------------------------------------------------------------------------
# CLI


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="command", required=True)
    a = sub.add_parser("audit")
    a.add_argument("--output", required=True, type=Path)
    a.add_argument("--accepted-run", default=ACCEPTED_RUN, type=Path)
    a.add_argument("--allow-tmp", action="store_true")
    r = sub.add_parser("run")
    r.add_argument("--audit-manifest", required=True, type=Path)
    r.add_argument("--output", required=True, type=Path)
    r.add_argument("--gate", required=True)
    r.add_argument("--gate-token", required=True)
    r.add_argument("--runtime-cap-seconds", default=1800, type=int)
    r.add_argument("--allow-tmp", action="store_true")
    v = sub.add_parser("verify")
    v.add_argument("--run-dir", required=True, type=Path)
    v.add_argument("--output", type=Path)
    m = sub.add_parser("report-machine")
    m.add_argument("--run-dir", required=True, type=Path)
    m.add_argument("--output-dir", required=True, type=Path)
    m.add_argument("--allow-tmp", action="store_true")
    return p.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    if args.command == "audit":
        out = audit_accepted(
            args.output, accepted_run=args.accepted_run, allow_tmp=args.allow_tmp
        )
        print(
            json.dumps(
                {
                    "audit_manifest": str(args.output / "audit_manifest.json"),
                    "gate_token": out["gate_token"],
                },
                indent=2,
            )
        )
    elif args.command == "run":
        out = run_diagnosis(
            args.audit_manifest,
            args.output,
            gate=args.gate,
            token=args.gate_token,
            runtime_cap_seconds=args.runtime_cap_seconds,
            allow_tmp=args.allow_tmp,
        )
        print(json.dumps(out["counts"], indent=2))
    elif args.command == "verify":
        out = verify_run(args.run_dir, args.output)
        print(json.dumps(out["summary_counts"], indent=2))
    elif args.command == "report-machine":
        out = render_machine_report(
            args.run_dir, args.output_dir, allow_tmp=args.allow_tmp
        )
        print(
            json.dumps(
                {
                    "machine_report": str(args.output_dir / "machine_report.json"),
                    "files": len(out["files"]),
                },
                indent=2,
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
