from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np

from scripts import cebra_decoder_autoresearch as cda
from scripts.cebra_decoder_autoresearch import (
    CEBRA_OBJECTIVES,
    FIT_GATE_FLAG,
    LABELS,
    NONLINEAR_RECIPE_IDS,
    RECIPES,
    RECIPE_BY_ID,
    FeatureSet,
    binary_metrics,
    compute_null_tails,
    delete_source_weights,
    exact_class_weights,
    fit_recipe,
    load_model,
    metric_rows_for_bundle,
    predict_from_saved_state,
    reconstruct_rows_from_manifest,
    run_readouts,
    save_model_and_predictions,
    sha256_file,
    source_bootstrap_worlds,
    stable_hash,
    verify_run,
)


class CebraDecoderAutoresearchSyntheticTest(unittest.TestCase):
    def test_class_local_product_rows_survive_lineage_roundtrip(self) -> None:
        # Real manifests restart product_row at zero for each class.
        manifest = [
            {
                "label": label,
                "product_row": str(i),
                "session_id": "s0",
                "source_trial_id": f"{label}-{i}",
                "split": "validation",
            }
            for label, count in (("absent", 24), ("present", 6))
            for i in range(count)
        ]
        y = np.array([0] * 24 + [1] * 6)
        feature = FeatureSet(
            "local-rows",
            "synthetic",
            "tiny",
            np.zeros((30, 2)),
            y,
            np.zeros((30, 2)),
            y,
            exact_class_weights(y),
            manifest,
            {"is_null": False},
        )
        matrix = cda.validation_source_matrix(manifest)
        self.assertEqual(matrix["source_ids"].shape, (30, 1))
        self.assertEqual(matrix["source_ids"][0, 0], "absent-0")
        self.assertEqual(matrix["source_ids"][24, 0], "present-0")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)
            meta = cda.save_feature(path, feature)
            restored = cda.load_feature(path, meta)
            worlds = source_bootstrap_worlds(restored, worlds=2)
            self.assertEqual(len(worlds[0]["row_weights"]), 30)
            weights, info = delete_source_weights(restored, "present-0")
            self.assertEqual(info["rows_removed"], 1)
            self.assertEqual(info["removed_absent_rows"], 0)
            assert weights is not None
            self.assertAlmostEqual(weights[24], 0)

    def test_pca_saved_transform_replays_without_fitting(self) -> None:
        rng = np.random.default_rng(92)
        train = rng.poisson(0.3, size=(32, 29, 10)).astype(np.float32)
        validation = rng.poisson(0.3, size=(12, 29, 10)).astype(np.float32)
        expected_train, expected_validation, state = cda.pca8_fit_transform(
            train, validation
        )
        with (
            patch(
                "sklearn.decomposition.PCA.fit",
                side_effect=AssertionError("fit forbidden"),
            ),
            patch(
                "sklearn.preprocessing.StandardScaler.fit",
                side_effect=AssertionError("fit forbidden"),
            ),
        ):
            for data, expected in (
                (train, expected_train),
                (validation, expected_validation),
            ):
                np.testing.assert_allclose(
                    cda.pca8_transform_from_state(data, state),
                    expected,
                    atol=1e-6,
                    rtol=0,
                )

    def test_weighted_ba_and_nonlinear_xor_signal(self) -> None:
        y = np.asarray([0] * 24 + [1] * 6, dtype=np.int64)
        weights = exact_class_weights(y)
        all_absent = np.zeros_like(y)
        metrics = binary_metrics(
            y,
            pred=all_absent,
            score=1 - all_absent,
            weights=weights,
            prob=1 - all_absent,
        )
        self.assertAlmostEqual(metrics["weighted_accuracy"], 0.5)
        self.assertAlmostEqual(metrics["balanced_accuracy"], 0.5)

        X, y2 = _xor_rows(repeats=12)
        feature = FeatureSet(
            feature_id="xor",
            kind="synthetic",
            representation="xor",
            X_train=X,
            y_train=y2,
            X_validation=X.copy(),
            y_validation=y2.copy(),
            validation_weights=exact_class_weights(y2),
            validation_manifest=[],
            metadata={"is_null": False},
        )
        linear = metric_rows_for_bundle(
            feature,
            "logistic_scaled_c1",
            fit_recipe(feature, RECIPE_BY_ID["logistic_scaled_c1"]),
        )[1]
        nonlinear_best = max(
            metric_rows_for_bundle(
                feature, rid, fit_recipe(feature, RECIPE_BY_ID[rid])
            )[1]["balanced_accuracy"]
            for rid in NONLINEAR_RECIPE_IDS
        )
        self.assertLessEqual(linear["balanced_accuracy"], 0.75)
        self.assertGreaterEqual(nonlinear_best, 0.95)

    def test_reconstruct_masks_disjoint_labels_and_train_only_scaler(self) -> None:
        Xsrc, Msrc, source_index, cells, train_manifest, val_manifest = (
            _source_fixture()
        )
        Xtr, ytr, _ = reconstruct_rows_from_manifest(
            Xsrc=Xsrc,
            Msrc=Msrc,
            source_index=source_index,
            cell_ids=cells,
            manifest=train_manifest,
            row_field="pseudo_row",
        )
        Xva, yva, _ = reconstruct_rows_from_manifest(
            Xsrc=Xsrc,
            Msrc=Msrc,
            source_index=source_index,
            cell_ids=cells,
            manifest=val_manifest,
            row_field="product_row",
        )
        self.assertEqual(ytr.tolist(), [0, 1])
        self.assertEqual(yva.tolist(), [0, 1])
        self.assertTrue(
            {r["source_trial_id"] for r in train_manifest}.isdisjoint(
                {r["source_trial_id"] for r in val_manifest}
            )
        )

        bad_mask = Msrc.copy()
        bad_mask[source_index["s0_train_absent"], 0] = False
        with self.assertRaises(ValueError):
            reconstruct_rows_from_manifest(
                Xsrc=Xsrc,
                Msrc=bad_mask,
                source_index=source_index,
                cell_ids=cells,
                manifest=train_manifest,
                row_field="pseudo_row",
            )

        feature = FeatureSet(
            feature_id="scaler",
            kind="synthetic",
            representation="raw",
            X_train=Xtr.reshape(2, -1),
            y_train=ytr,
            X_validation=(Xva.reshape(2, -1) + 1000.0),
            y_validation=yva,
            validation_weights=exact_class_weights(yva),
            validation_manifest=val_manifest,
            metadata={"is_null": False},
        )
        bundle = fit_recipe(feature, RECIPE_BY_ID["logistic_scaled_c1"])
        np.testing.assert_allclose(
            bundle.state["scaler_mean"], feature.X_train.mean(axis=0), atol=1e-12
        )
        self.assertFalse(
            np.allclose(bundle.state["scaler_mean"], feature.X_validation.mean(axis=0))
        )

    def test_source_bootstrap_lineage_delete_source_and_null_ties(self) -> None:
        _Xsrc, _Msrc, _source_index, cells, _train_manifest, val_manifest = (
            _source_fixture()
        )
        y = np.asarray([0, 1], dtype=np.int64)
        feature = FeatureSet(
            feature_id="boot",
            kind="synthetic",
            representation="tiny",
            X_train=np.zeros((2, 2), dtype=np.float32),
            y_train=y,
            X_validation=np.zeros((2, 2), dtype=np.float32),
            y_validation=y,
            validation_weights=exact_class_weights(y),
            validation_manifest=val_manifest,
            metadata={"is_null": False, "assembly_seed": 0},
        )
        worlds_a = source_bootstrap_worlds(feature, worlds=5, seed=123)
        worlds_b = source_bootstrap_worlds(feature, worlds=5, seed=123)
        self.assertEqual(stable_hash(worlds_a), stable_hash(worlds_b))
        for world in worlds_a:
            self.assertAlmostEqual(sum(world["row_weights"]), 1.0)
        weights_after_delete, summary = delete_source_weights(
            feature, val_manifest[0]["source_trial_id"]
        )
        self.assertIsNone(weights_after_delete)
        self.assertTrue(summary["inestimable"])
        self.assertEqual(summary["rows_removed"], 1)

        metric_rows = _null_tie_metric_rows()
        tails = compute_null_tails(metric_rows)
        self.assertEqual(tails["family_exceedances_inclusive"], 20)
        self.assertAlmostEqual(tails["family_p_plus_one"], 1.0)

    def test_save_replay_hash_tamper_and_no_fit_on_replay(self) -> None:
        X, y = _xor_rows(repeats=4)
        manifest = []
        for i, label in enumerate(y):
            manifest.append(
                {
                    "split": "validation",
                    "label": "present" if label else "absent",
                    "product_row": str(i),
                    "session_id": "s0_session01",
                    "source_trial_id": f"src{i}",
                }
            )
        feature = FeatureSet(
            feature_id="replay",
            kind="synthetic",
            representation="xor",
            X_train=X,
            y_train=y,
            X_validation=X.copy(),
            y_validation=y.copy(),
            validation_weights=exact_class_weights(y),
            validation_manifest=manifest,
            metadata={"is_null": False},
        )
        bundle = fit_recipe(feature, RECIPE_BY_ID["svm_rbf_scaled"])
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp)
            model_meta, rows, _preds = save_model_and_predictions(
                run_dir, feature, "svm_rbf_scaled", bundle
            )
            state = load_model(run_dir, model_meta)
            with patch(
                "sklearn.svm.SVC.fit", side_effect=AssertionError("fit forbidden")
            ):
                replay = predict_from_saved_state(
                    feature, "svm_rbf_scaled", state, model_meta["state_meta"]
                )
            replay_rows = metric_rows_for_bundle(feature, "svm_rbf_scaled", replay)
            self.assertEqual(
                rows[1]["balanced_accuracy"], replay_rows[1]["balanced_accuracy"]
            )
            model_path = next((run_dir / "models").glob("*.npz"))
            model_path.write_bytes(model_path.read_bytes() + b"tamper")
            with self.assertRaises(ValueError):
                load_model(run_dir, model_meta)

    def test_synthetic_run_verify_integration_and_tamper_rejections(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            audit_path, audit = _synthetic_audit(root)
            out = root / "run"
            with (
                patch.object(cda, "BOOTSTRAP_WORLDS", 2),
                patch.object(
                    cda, "synthetic_runtime_estimate", return_value={"synthetic": True}
                ),
                patch.object(
                    cda, "make_cebra_feature", side_effect=_fake_cebra_feature
                ),
                patch.object(
                    cda,
                    "raw_pca_features_from_audit",
                    side_effect=_fake_raw_pca_features,
                ),
            ):
                summary = run_readouts(
                    audit_path,
                    out,
                    protocol_sha256=audit["protocol_sha256"],
                    gate=FIT_GATE_FLAG,
                    runtime_cap_seconds=120,
                    allow_tmp=True,
                )
            self.assertEqual(
                summary["fit_counts"]["observed_cebra_new_readout_fits"], 14
            )
            self.assertEqual(summary["fit_counts"]["null_cebra_new_readout_fits"], 280)
            self.assertEqual(summary["fit_counts"]["matched_raw_pca_readout_fits"], 0)
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
                    "sklearn.neighbors.KNeighborsClassifier.fit",
                    side_effect=AssertionError("fit forbidden"),
                ),
                patch(
                    "sklearn.preprocessing.StandardScaler.fit",
                    side_effect=AssertionError("fit forbidden"),
                ),
            ):
                receipt = verify_run(out)
            self.assertEqual(receipt["status"], "verified")
            self.assertEqual(receipt["rowset_replay"]["source_bootstrap"]["rows"], 32)

            _tamper_csv_numeric(
                out / "source_bootstrap_metrics.csv", "balanced_accuracy"
            )
            with self.assertRaises(ValueError):
                verify_run(out)
            _restore_from_bak(out / "source_bootstrap_metrics.csv")

            _tamper_csv_numeric(out / "delete_source_influence.csv", "rows_removed")
            with self.assertRaises(ValueError):
                verify_run(out)
            _restore_from_bak(out / "delete_source_influence.csv")

            summary_json = out / "summary.json"
            original = summary_json.read_bytes()
            data = cda.read_json(summary_json)
            data["null_family_tails"]["family_p_plus_one"] = 0.123
            cda.write_json(summary_json, data)
            with self.assertRaises(ValueError):
                verify_run(out)
            summary_json.write_bytes(original)

            bad_audit = dict(audit)
            bad_audit["code_sha256"] = "0" * 64
            bad_path = root / "bad_audit.json"
            cda.write_json(bad_path, bad_audit)
            with self.assertRaises(ValueError):
                run_readouts(
                    bad_path,
                    root / "bad_run",
                    protocol_sha256=audit["protocol_sha256"],
                    gate=FIT_GATE_FLAG,
                    allow_tmp=True,
                )

    def test_audit_does_not_fit_pca_or_scaler(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            track = root / "track_b"
            source_tensor = root / "stage" / "source_level_cue_tensors.npz"
            source_tensor.parent.mkdir(parents=True)
            source_tensor.write_bytes(b"source")
            entries = []
            for spec in _synthetic_specs():
                fit_dir = track / "fits" / cda.stable_hash(spec)[:16]
                fit_dir.mkdir(parents=True)
                cda.write_json(fit_dir / "fit_info.json", {"fit_spec": spec})
                cda.write_csv(
                    fit_dir / "generated_assembly_manifest.csv",
                    [
                        {
                            "split": "train",
                            "label": "absent",
                            "pseudo_row": "0",
                            "session_id": "s0_session01",
                            "source_trial_id": "src",
                        }
                    ],
                )
                cda.write_csv(
                    fit_dir / "exact_evaluation_manifest.csv",
                    [
                        {
                            "split": "validation",
                            "label": "absent",
                            "product_row": "0",
                            "session_id": "s0_session01",
                            "source_trial_id": "src",
                        }
                    ],
                )
                if spec["family_role"] == cda.OBSERVED_FAMILY_ROLE:
                    entries.append(
                        {
                            "fit_id": fit_dir.name,
                            "fit_dir": str(fit_dir),
                            "fit_info_path": str(fit_dir / "fit_info.json"),
                            "fit_info_sha256": sha256_file(fit_dir / "fit_info.json"),
                            "npz_sha256": "n",
                            "generated_manifest_sha256": sha256_file(
                                fit_dir / "generated_assembly_manifest.csv"
                            ),
                            "exact_manifest_sha256": sha256_file(
                                fit_dir / "exact_evaluation_manifest.csv"
                            ),
                            "fit_identity_hash": "h",
                            "fit_spec": spec,
                            "is_null": False,
                            "baseline_validation_ba": 0.5,
                            "baseline_max_probability_replay_diff": 0.0,
                        }
                    )
            for seed in range(5):
                np.savez_compressed(
                    source_tensor.parent / f"train_only_pca_seed{seed}.npz",
                    pca_cellspace_8_components=np.zeros((8, 2), dtype=np.float32),
                )

            class FakeNpz:
                files = ["a"]

                def __getitem__(self, key):
                    return np.zeros(1)

            fake_source = {
                "path": source_tensor,
                "sha256": "source",
                "npz": FakeNpz(),
                "Xsrc": np.zeros((1, 2, 1), dtype=np.float32),
                "Msrc": np.ones((1, 2), dtype=bool),
                "source_ids": ["src"],
                "labels": ["absent"],
                "splits": ["train"],
                "cell_ids": ["s0/session01/a/c"],
                "source_index": {"src": 0},
                "metas": [],
            }

            def fake_audit_one(path, source):
                spec = cda.read_json(path)["fit_spec"]
                fit_dir = path.parent
                return {
                    "fit_id": fit_dir.name,
                    "fit_dir": str(fit_dir),
                    "fit_info_path": str(path),
                    "fit_info_sha256": sha256_file(path),
                    "npz_sha256": "n",
                    "generated_manifest_sha256": sha256_file(
                        fit_dir / "generated_assembly_manifest.csv"
                    ),
                    "exact_manifest_sha256": sha256_file(
                        fit_dir / "exact_evaluation_manifest.csv"
                    ),
                    "fit_identity_hash": "h",
                    "fit_spec": spec,
                    "is_null": spec.get("permutation_index") is not None,
                    "baseline_validation_ba": 0.5,
                    "baseline_max_probability_replay_diff": 0.0,
                }

            with (
                patch.object(cda, "load_source_tensor", return_value=fake_source),
                patch.object(cda, "audit_one_fit", side_effect=fake_audit_one),
                patch.object(
                    cda,
                    "reconstruct_rows_from_manifest",
                    return_value=(
                        np.zeros((1, 2, 1), dtype=np.float32),
                        np.zeros(1, dtype=np.int64),
                        [],
                    ),
                ),
                patch(
                    "sklearn.decomposition.PCA.fit",
                    side_effect=AssertionError("PCA.fit forbidden"),
                ),
                patch(
                    "sklearn.preprocessing.StandardScaler.fit",
                    side_effect=AssertionError("StandardScaler.fit forbidden"),
                ),
            ):
                manifest = cda.audit_artifacts(
                    root / "audit",
                    track_b_root=track,
                    source_tensor=source_tensor,
                    allow_tmp=True,
                )
            self.assertEqual(manifest["eligibility"]["observed_cebra_anchors"], 50)


def _xor_rows(repeats: int) -> tuple[np.ndarray, np.ndarray]:
    base = np.asarray(
        [[0.0, 0.0], [0.0, 1.0], [1.0, 0.0], [1.0, 1.0]], dtype=np.float32
    )
    labels = np.asarray([0, 1, 1, 0], dtype=np.int64)
    return np.tile(base, (repeats, 1)), np.tile(labels, repeats)


def _source_fixture():
    cells = [
        "s0/session01/array00/channel000/cell00",
        "s1/session01/array00/channel000/cell00",
    ]
    source_ids = []
    rows = []
    for split in ("train", "validation"):
        for label in LABELS:
            for sess in ("s0_session01", "s1_session01"):
                sid = f"{sess[:2]}_{split}_{label}"
                source_ids.append(sid)
                rows.append((sid, sess, split, label))
    Xsrc = np.zeros((len(rows), 2, 1), dtype=np.float32)
    Msrc = np.zeros((len(rows), 2), dtype=bool)
    for i, (_sid, sess, _split, label) in enumerate(rows):
        cell_i = 0 if sess == "s0_session01" else 1
        Msrc[i, cell_i] = True
        Xsrc[i, cell_i, 0] = 1.0 if label == "present" else -1.0
    source_index = {sid: i for i, sid in enumerate(source_ids)}

    def manifest(split: str, row_field: str):
        out = []
        for row_i, label in enumerate(LABELS):
            for sess in ("s0_session01", "s1_session01"):
                sid = f"{sess[:2]}_{split}_{label}"
                out.append(
                    {
                        "split": split,
                        "label": label,
                        row_field: str(row_i),
                        "session_id": sess,
                        "source_trial_id": sid,
                    }
                )
        return out

    return (
        Xsrc,
        Msrc,
        source_index,
        cells,
        manifest("train", "pseudo_row"),
        manifest("validation", "product_row"),
    )


def _null_tie_metric_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    recipe_ids = [r["id"] for r in RECIPES]
    for objective in CEBRA_OBJECTIVES:
        for recipe_id in recipe_ids:
            rows.append(
                {
                    "split": "validation_exact_q",
                    "feature_kind": "cebra",
                    "is_null": False,
                    "objective": objective,
                    "assembly_seed": 0,
                    "optimizer_seed": 0,
                    "permutation_index": "",
                    "recipe_id": recipe_id,
                    "balanced_accuracy": 0.6,
                }
            )
            for perm in range(20):
                rows.append(
                    {
                        "split": "validation_exact_q",
                        "feature_kind": "cebra",
                        "is_null": True,
                        "objective": objective,
                        "assembly_seed": 0,
                        "optimizer_seed": 0,
                        "permutation_index": perm,
                        "recipe_id": recipe_id,
                        "balanced_accuracy": 0.6,
                    }
                )
    return rows


def _synthetic_specs():
    specs = []
    for objective in CEBRA_OBJECTIVES:
        for assembly_seed in range(5):
            for optimizer_seed in range(5):
                specs.append(
                    {
                        "objective": objective,
                        "dim": 8,
                        "rows_per_class": 64,
                        "updates": 1000,
                        "assembly_seed": assembly_seed,
                        "optimizer_seed": optimizer_seed,
                        "family_role": cda.OBSERVED_FAMILY_ROLE,
                        "permutation_index": None,
                    }
                )
        for permutation_index in range(20):
            specs.append(
                {
                    "objective": objective,
                    "dim": 8,
                    "rows_per_class": 64,
                    "updates": 1000,
                    "assembly_seed": 0,
                    "optimizer_seed": 0,
                    "family_role": cda.NULL_FAMILY_ROLE,
                    "permutation_index": permutation_index,
                }
            )
    return specs


def _integration_specs():
    specs = []
    for objective in CEBRA_OBJECTIVES:
        specs.append(
            {
                "objective": objective,
                "dim": 8,
                "rows_per_class": 64,
                "updates": 1000,
                "assembly_seed": 0,
                "optimizer_seed": 0,
                "family_role": cda.OBSERVED_FAMILY_ROLE,
                "permutation_index": None,
            }
        )
        for permutation_index in range(20):
            specs.append(
                {
                    "objective": objective,
                    "dim": 8,
                    "rows_per_class": 64,
                    "updates": 1000,
                    "assembly_seed": 0,
                    "optimizer_seed": 0,
                    "family_role": cda.NULL_FAMILY_ROLE,
                    "permutation_index": permutation_index,
                }
            )
    return specs


def _synthetic_audit(root: Path):
    audit_dir = root / "audit"
    snapshot_dir = audit_dir / "source_snapshots"
    snapshot_dir.mkdir(parents=True)
    evaluator = Path(cda.__file__)
    (snapshot_dir / evaluator.name).write_bytes(evaluator.read_bytes())
    source = root / "source.npz"
    source.write_bytes(b"synthetic-source")
    observed = []
    nulls = []
    track = root / "track"
    for spec in _integration_specs():
        fit_dir = track / cda.stable_hash(spec)[:16]
        fit_dir.mkdir(parents=True)
        fit_info = fit_dir / "fit_info.json"
        cda.write_json(fit_info, {"fit_spec": spec})
        for name in (
            "embeddings_predictions_decoder.npz",
            "generated_assembly_manifest.csv",
            "exact_evaluation_manifest.csv",
        ):
            (fit_dir / name).write_text(name)
        entry = {
            "fit_id": fit_dir.name,
            "fit_dir": str(fit_dir),
            "fit_info_path": str(fit_info),
            "fit_info_sha256": sha256_file(fit_info),
            "npz_sha256": sha256_file(fit_dir / "embeddings_predictions_decoder.npz"),
            "generated_manifest_sha256": sha256_file(
                fit_dir / "generated_assembly_manifest.csv"
            ),
            "exact_manifest_sha256": sha256_file(
                fit_dir / "exact_evaluation_manifest.csv"
            ),
            "fit_identity_hash": cda.stable_hash(spec),
            "fit_spec": spec,
            "is_null": spec.get("permutation_index") is not None,
        }
        (nulls if entry["is_null"] else observed).append(entry)
    audit = {
        "status": "audited",
        "protocol_sha256": sha256_file(cda.PROTOCOL_PATH),
        "code_sha256": sha256_file(evaluator),
        "source_tensor": {"path": str(source), "sha256": sha256_file(source)},
        "observed_fits": observed,
        "null_fits": nulls,
        "readout_budget": {
            "observed_cebra_new_readout_fits": 14,
            "null_cebra_new_readout_fits": 280,
            "matched_raw_pca_readout_fits": 0,
            "new_train_only_pca_fits": 0,
            "saved_baseline_forwards": 42,
            "total_new_readout_fits_ceiling": 294,
            "new_cebra_fits": 0,
        },
    }
    path = audit_dir / "audit_manifest.json"
    cda.write_json(path, audit)
    return path, audit


def _base_feature(feature_id: str, kind: str, metadata: dict) -> FeatureSet:
    x0, y0 = _xor_rows(5)
    manifest = []
    x_val = []
    y_val = []
    row_i = 0
    for label, points in ((0, [(0, 0), (1, 1)]), (1, [(0, 1), (1, 0)])):
        for a, point_a in enumerate(points):
            for b, point_b in enumerate(points):
                x_val.append(point_a if (a + b) % 2 == 0 else point_b)
                y_val.append(label)
                manifest.append(
                    {
                        "split": "validation",
                        "label": "present" if label else "absent",
                        "product_row": str(row_i),
                        "session_id": "s0_session01",
                        "source_trial_id": f"s0_{label}_{a}",
                    }
                )
                manifest.append(
                    {
                        "split": "validation",
                        "label": "present" if label else "absent",
                        "product_row": str(row_i),
                        "session_id": "s1_session01",
                        "source_trial_id": f"s1_{label}_{b}",
                    }
                )
                row_i += 1
    yv = np.asarray(y_val, dtype=np.int64)
    return FeatureSet(
        feature_id=feature_id,
        kind=kind,
        representation="tiny",
        X_train=x0.astype(np.float32),
        y_train=y0.astype(np.int64),
        X_validation=np.asarray(x_val, dtype=np.float32),
        y_validation=yv,
        validation_weights=exact_class_weights(yv),
        validation_manifest=manifest,
        metadata=metadata,
    )


def _fake_cebra_feature(entry):
    spec = entry["fit_spec"]
    metadata = {
        "legacy_fit_id": entry["fit_id"],
        "objective": spec["objective"],
        "assembly_seed": spec["assembly_seed"],
        "optimizer_seed": spec["optimizer_seed"],
        "permutation_index": spec.get("permutation_index"),
        "family_role": spec["family_role"],
        "is_null": entry["is_null"],
    }
    feature = _base_feature(
        cda.stable_hash({"cebra": metadata})[:20], "cebra", metadata
    )
    baseline = {
        "scaler_mean": np.zeros(feature.X_train.shape[1]),
        "scaler_scale": np.ones(feature.X_train.shape[1]),
        "coef": np.zeros((1, feature.X_train.shape[1])),
        "intercept": np.zeros(1),
    }
    return feature, baseline


def _fake_raw_pca_features(audit, run_dir):
    features = []
    pca_rows = []
    return features, pca_rows


def _tamper_csv_numeric(path: Path, field: str) -> None:
    backup = path.with_suffix(path.suffix + ".bak")
    backup.write_bytes(path.read_bytes())
    rows = cda.csv_rows(path)
    rows[0][field] = str(float(rows[0].get(field) or 0) + 0.25)
    cda.write_csv(path, rows)


def _restore_from_bak(path: Path) -> None:
    backup = path.with_suffix(path.suffix + ".bak")
    path.write_bytes(backup.read_bytes())
    backup.unlink()


if __name__ == "__main__":
    unittest.main()
