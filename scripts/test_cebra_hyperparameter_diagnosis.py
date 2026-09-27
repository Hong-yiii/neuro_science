from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np

from scripts import cebra_decoder_autoresearch as base
from scripts import cebra_hyperparameter_diagnosis as chd
from scripts.cebra_decoder_autoresearch import FeatureSet


class CebraHyperparameterDiagnosisSyntheticTest(unittest.TestCase):
    def test_audit_is_no_fit_and_freezes_full_budget(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            accepted = _fake_accepted_for_audit(root / "accepted")
            with (
                patch(
                    "sklearn.decomposition.PCA.fit",
                    side_effect=AssertionError("PCA.fit forbidden"),
                ),
                patch(
                    "sklearn.preprocessing.StandardScaler.fit",
                    side_effect=AssertionError("scaler fit forbidden"),
                ),
                patch.object(chd, "validate_accepted_inputs"),
            ):
                manifest = chd.audit_accepted(
                    root / "audit", accepted_run=accepted, allow_tmp=True
                )
        self.assertEqual(manifest["planned_counts"]["total_features_after_run"], 140)
        self.assertEqual(manifest["planned_counts"]["total_new_readout_fits"], 1700)
        self.assertEqual(manifest["matched_null_worlds"], 20)
        self.assertEqual(manifest["planned_counts"]["new_observed_pca_fits"], 0)

    def test_classlocal30_temperature_invariance_and_svm_replay(self) -> None:
        feature = _feature(
            "classlocal",
            "cebra",
            {
                "is_null": False,
                "assembly_seed": 0,
                "optimizer_seed": 0,
                "objective": "cebra_time",
            },
        )
        matrix = base.validation_source_matrix(feature.validation_manifest)
        self.assertEqual(matrix["source_ids"].shape, (30, 1))
        self.assertEqual(matrix["source_ids"][0, 0], "absent-0")
        self.assertEqual(matrix["source_ids"][24, 0], "present-0")

        logistic = base.fit_recipe(feature, chd.RECIPE_BY_ID["logistic_scaled_c1"])
        temps = chd.temperature_rows(
            {feature.feature_id: feature},
            {(feature.feature_id, "logistic_scaled_c1"): logistic},
        )
        validation = [r for r in temps if r["split"] == "validation_exact_q"]
        self.assertEqual(len(validation), 4)
        bas = {r["balanced_accuracy"] for r in validation}
        aucs = {r["auroc"] for r in validation}
        self.assertEqual(len(bas), 1)
        self.assertEqual(len(aucs), 1)

        rid = chd.svm_recipe_id(10.0, 10.0)
        svm = chd.fit_svm_grid(feature, chd.RECIPE_BY_ID[rid])
        replay = base.predict_from_saved_state(feature, rid, svm.state, svm.state_meta)
        np.testing.assert_allclose(
            replay.validation_score, svm.validation_score, atol=1e-10, rtol=0
        )
        self.assertIn("gamma_base_scale", svm.state_meta)

    def test_budget_pair_completeness_and_incomplete_accounting(self) -> None:
        metas = [
            {"feature_id": "f0", "kind": "cebra", "is_null": False},
            {"feature_id": "n0", "kind": "cebra", "is_null": True},
        ]
        models = [
            {"feature_id": m["feature_id"], "recipe_id": rid}
            for m in metas
            for rid in chd.PRIOR_RECIPE_IDS
        ]
        chd._validate_prior_model_grid(metas, models, full=False)
        with self.assertRaises(ValueError):
            chd._validate_prior_model_grid(metas, models[:-1], full=False)

        features = {
            "f0": _feature("f0", "cebra", {"is_null": False}),
            "rp": _feature("rp", "raw", {"is_null": True}),
        }
        complete = [
            {"feature_id": fid, "recipe_id": rid}
            for fid, f in features.items()
            for rid in chd.expected_recipe_ids(f)
        ]
        chd.validate_model_completeness(features, complete)
        with self.assertRaises(ValueError):
            chd.validate_model_completeness(features, complete[:-1])

        old_audit = {
            "null_fits": [
                _null_entry(0, "cebra_time", "same"),
                _null_entry(0, "cebra_behavior", "different"),
            ]
        }
        with self.assertRaises(ValueError):
            chd.audit_matched_null_worlds(old_audit)

    def test_failed_fit_is_journaled_and_changed_inputs_block_run(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            accepted = _accepted_run(root / "accepted")
            audit_path, token = _synthetic_audit(root / "audit.json", accepted)
            out = root / "failed"
            with (
                patch.object(
                    chd,
                    "make_null_raw_pca_features",
                    side_effect=_fake_null_raw_pca_features,
                ),
                patch.object(
                    chd, "fit_new_recipe", side_effect=RuntimeError("injected failure")
                ),
                self.assertRaisesRegex(RuntimeError, "injected failure"),
            ):
                chd.run_diagnosis(
                    audit_path, out, gate=chd.FIT_GATE_FLAG, token=token, allow_tmp=True
                )
            failure = chd.read_json(out / "INCOMPLETE.json")
            self.assertEqual(failure["new_readouts_started"], 1)
            self.assertEqual(failure["new_readouts_completed"], 0)
            self.assertEqual(
                chd.read_json(out / "run_config.json")["status"], "incomplete"
            )
            with self.assertRaises(ValueError):
                chd.verify_run(out)
            path = accepted / "model_manifest.json"
            path.write_bytes(path.read_bytes() + b" ")
            with self.assertRaisesRegex(ValueError, "changed since audit"):
                chd.validate_gate(chd.read_json(audit_path), chd.FIT_GATE_FLAG, token)

    def test_sensitivity_matches_independent_class_recalls(self) -> None:
        feature = _feature("weights", "cebra", {"is_null": False})
        bundle = base.fit_recipe(feature, chd.RECIPE_BY_ID["logistic_scaled_c1"])
        for world in base.source_bootstrap_worlds(feature, worlds=4):
            weights = np.asarray(world["row_weights"])
            actual = chd._metric_for_weights(
                feature, bundle, "logistic_scaled_c1", weights
            )["balanced_accuracy"]
            expected = base.binary_metrics(
                feature.y_validation,
                pred=bundle.validation_pred,
                score=bundle.validation_score,
                weights=weights,
                prob=bundle.validation_prob,
            )["balanced_accuracy"]
            self.assertAlmostEqual(actual, expected)

    def test_synthetic_run_verify_forbids_fit_and_rejects_tamper(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            accepted = _accepted_run(root / "accepted")
            audit_path, token = _synthetic_audit(root / "audit.json", accepted)
            out = root / "run"
            with (
                patch.object(
                    chd,
                    "make_null_raw_pca_features",
                    side_effect=_fake_null_raw_pca_features,
                ),
                patch.object(chd.base, "BOOTSTRAP_WORLDS", 2),
            ):
                summary = chd.run_diagnosis(
                    audit_path,
                    out,
                    gate=chd.FIT_GATE_FLAG,
                    token=token,
                    allow_tmp=True,
                    runtime_cap_seconds=120,
                )
            self.assertEqual(summary["counts"]["new_cebra_fits"], 0)
            self.assertEqual(summary["counts"]["new_observed_pca_fits"], 0)
            self.assertGreater(summary["counts"]["total_new_readout_fits"], 0)
            self.assertTrue((out / "event_journal.jsonl").exists())

            with (
                patch(
                    "sklearn.linear_model.LogisticRegression.fit",
                    side_effect=AssertionError("fit forbidden"),
                ),
                patch(
                    "sklearn.svm.SVC.fit", side_effect=AssertionError("fit forbidden")
                ),
                patch(
                    "sklearn.preprocessing.StandardScaler.fit",
                    side_effect=AssertionError("fit forbidden"),
                ),
                patch(
                    "sklearn.decomposition.PCA.fit",
                    side_effect=AssertionError("PCA.fit forbidden"),
                ),
            ):
                receipt = chd.verify_run(out)
            self.assertEqual(receipt["status"], "verified")
            self.assertEqual(receipt["pca_transforms_replayed"], 1)
            for name in ("source_bootstrap_worlds.json", "run_config.json"):
                path = out / name
                saved = path.read_bytes()
                value = chd.read_json(path)
                if name.startswith("source"):
                    value["worlds"][0]["row_weights"][0] += 0.01
                else:
                    value["code_sha256"] = "0" * 64
                chd.write_json(path, value)
                with self.assertRaises(ValueError):
                    chd.verify_run(out)
                path.write_bytes(saved)
            pca_path = next((out / "pca_transforms").glob("*.npz"))
            saved = pca_path.read_bytes()
            pca_path.write_bytes(saved + b"tamper")
            with self.assertRaises(ValueError):
                chd.verify_run(out)
            pca_path.write_bytes(saved)

            metrics = out / "readout_metrics.csv"
            original = metrics.read_bytes()
            rows = base.csv_rows(metrics)
            rows[0]["balanced_accuracy"] = str(
                float(rows[0]["balanced_accuracy"]) + 0.25
            )
            base.write_csv(metrics, rows)
            with self.assertRaises(ValueError):
                chd.verify_run(out)
            metrics.write_bytes(original)

            pred_npz = next((out / "predictions").glob("*.npz"))
            pred_npz.write_bytes(pred_npz.read_bytes() + b"tamper")
            with self.assertRaises(ValueError):
                chd.verify_run(out)


def _feature(feature_id: str, kind: str, metadata: dict, seed: int = 1) -> FeatureSet:
    rng = np.random.default_rng(seed + sum(map(ord, feature_id)))
    y_train = np.asarray([0] * 16 + [1] * 16, dtype=np.int64)
    x_train = rng.normal(0, 0.25, size=(32, 10)).astype(np.float32)
    x_train[y_train == 0, 0] -= 1.0
    x_train[y_train == 1, 0] += 1.0
    y_val = np.asarray([0] * 24 + [1] * 6, dtype=np.int64)
    x_val = rng.normal(0, 0.25, size=(30, 10)).astype(np.float32)
    x_val[y_val == 0, 0] -= 0.8
    x_val[y_val == 1, 0] += 0.8
    manifest = []
    for label, count in (("absent", 24), ("present", 6)):
        for i in range(count):
            manifest.append(
                {
                    "split": "validation",
                    "label": label,
                    "product_row": str(i),
                    "session_id": "s0_session01",
                    "source_trial_id": f"{label}-{i}",
                }
            )
    return FeatureSet(
        feature_id,
        kind,
        "synthetic4",
        x_train,
        y_train,
        x_val,
        y_val,
        base.exact_class_weights(y_val),
        manifest,
        metadata,
    )


def _accepted_run(path: Path) -> Path:
    path.mkdir(parents=True)
    features = [
        _feature(
            "cebra_obs",
            "cebra",
            {
                "is_null": False,
                "family_role": "crossed_seed_primary",
                "objective": "cebra_time",
                "assembly_seed": 0,
                "optimizer_seed": 0,
            },
        ),
        _feature("raw_obs", "raw", {"is_null": False, "assembly_seed": 0}),
        _feature(
            "cebra_null",
            "cebra",
            {
                "is_null": True,
                "family_role": "family_null",
                "objective": "cebra_time",
                "assembly_seed": 0,
                "optimizer_seed": 0,
                "permutation_index": 0,
            },
        ),
    ]
    feature_metas = [base.save_feature(path, f) for f in features]
    model_metas = []
    for feature in features:
        for rid in chd.PRIOR_RECIPE_IDS:
            bundle = base.fit_recipe(feature, chd.RECIPE_BY_ID[rid])
            meta, _rows, _preds = base.save_model_and_predictions(
                path, feature, rid, bundle
            )
            model_metas.append(meta)
    base.write_json(path / "feature_manifest.json", {"features": feature_metas})
    base.write_json(path / "model_manifest.json", {"models": model_metas})
    base.write_json(
        path / "audit_manifest.json",
        {
            "source_tensor": {"path": "synthetic", "sha256": "synthetic"},
            "null_fits": [],
        },
    )
    return path


def _fake_null_raw_pca_features(_old_audit, _run_dir):
    raw = _feature(
        "raw_null",
        "raw",
        {
            "is_null": True,
            "family_role": "matched_raw_pca_null",
            "assembly_seed": 0,
            "optimizer_seed": 0,
            "permutation_index": 0,
        },
    )
    chd.append_event(_run_dir, {"event": "pca_started", "permutation_index": 0})
    train, validation, state = base.pca8_fit_transform(
        raw.X_train[:, :, None], raw.X_validation[:, :, None]
    )
    path = _run_dir / "pca_transforms" / "synthetic.npz"
    digest = base.save_npz_exact(path, **state)
    pca = FeatureSet(
        "pca_null",
        "pca",
        "synthetic_pca8",
        train,
        raw.y_train,
        validation,
        raw.y_validation,
        raw.validation_weights,
        raw.validation_manifest,
        {**raw.metadata, "pca_transform_id": "pca-null", "pca_npz_sha256": digest},
    )
    ledger = {
        "permutation_index": 0,
        "pca_transform_id": "pca-null",
        "fit_counted": True,
        "observed_pca_fit": False,
        "pca_npz": str(path.relative_to(_run_dir)),
        "pca_npz_sha256": digest,
        "train_feature_sha256": base.ndarray_sha256(train),
        "validation_feature_sha256": base.ndarray_sha256(validation),
    }
    chd.append_event(
        _run_dir, {"event": "pca_complete", "permutation_index": 0, "ledger": ledger}
    )
    return [raw, pca], [ledger]


def _synthetic_audit(path: Path, accepted: Path) -> tuple[Path, str]:
    artifact_hashes = {
        "feature_manifest.json": chd.sha256_file(accepted / "feature_manifest.json"),
        "model_manifest.json": chd.sha256_file(accepted / "model_manifest.json"),
    }
    payload = chd.gate_payload(accepted, artifact_hashes)
    token = chd.gate_token(payload)
    audit = {
        "status": "audited",
        "synthetic": True,
        "accepted_run": str(accepted),
        "protocol_sha256": payload["protocol_sha256"],
        "code_sha256": payload["code_sha256"],
        "dependency_hash": payload["dependency_hash"],
        "artifact_hashes": artifact_hashes,
        "gate_payload": payload,
        "gate_token": token,
        "source_tensor": {"path": "synthetic", "sha256": "synthetic"},
    }
    chd.write_json(path, audit)
    return path, token


def _fake_accepted_for_audit(path: Path) -> Path:
    path.mkdir(parents=True)
    features = []
    for i in range(50):
        features.append(
            {
                "feature_id": f"cobs{i}",
                "kind": "cebra",
                "is_null": False,
                "objective": base.CEBRA_OBJECTIVES[i // 25],
                "assembly_seed": (i % 25) // 5,
                "optimizer_seed": i % 5,
            }
        )
    for i in range(40):
        features.append(
            {
                "feature_id": f"cnull{i}",
                "kind": "cebra",
                "is_null": True,
                "objective": base.CEBRA_OBJECTIVES[i // 20],
                "permutation_index": i % 20,
                "assembly_seed": 0,
                "optimizer_seed": 0,
            }
        )
    for i in range(5):
        features.append(
            {
                "feature_id": f"raw{i}",
                "kind": "raw",
                "is_null": False,
                "assembly_seed": i,
            }
        )
        features.append(
            {
                "feature_id": f"pca{i}",
                "kind": "pca",
                "is_null": False,
                "assembly_seed": i,
            }
        )
    models = [
        {"feature_id": f["feature_id"], "recipe_id": rid}
        for f in features
        for rid in chd.PRIOR_RECIPE_IDS
    ]
    base.write_json(path / "feature_manifest.json", {"features": features})
    base.write_json(path / "model_manifest.json", {"models": models})
    nulls = []
    for perm in range(20):
        nulls.append(_null_entry(perm, "cebra_time", f"h{perm}"))
        nulls.append(_null_entry(perm, "cebra_behavior", f"h{perm}"))
    base.write_json(
        path / "audit_manifest.json",
        {"source_tensor": {"path": "source", "sha256": "source"}, "null_fits": nulls},
    )
    for name in (
        "readout_metrics.csv",
        "verify_receipt.json",
        "summary.json",
        "source_bootstrap_worlds.json",
        "run_config.json",
    ):
        (path / name).write_text("{}\n" if name.endswith(".json") else "")
    return path


def _null_entry(perm: int, objective: str, digest: str) -> dict:
    return {
        "fit_id": f"{objective}-{perm}",
        "fit_spec": {"permutation_index": perm, "objective": objective},
        "generated_manifest_sha256": digest,
        "exact_manifest_sha256": digest,
        "train_manifest_hash": digest,
        "eval_manifest_hash": digest,
        "train_array_sha256": digest,
        "eval_array_sha256": digest,
        "train_unique_sources": 82,
        "validation_unique_sources": 22,
    }


if __name__ == "__main__":
    unittest.main()
