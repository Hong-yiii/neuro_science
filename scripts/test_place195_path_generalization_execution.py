"""Regression checks for scientific execution paths, using synthetic data only."""

import csv
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np

from scripts import place195_path_generalization_phase1 as study
from scripts.place195_v7_v8_neural_experiments import SourceMeta


def fixture():
    X, M, metas, cells, _, _ = study.gaussian_source_fixture(
        session_cell_counts=(2, 1),
        n_bins=2,
        train_per_class_session=4,
        validation_per_class_session=2,
        mean_difference=0.7,
        seed=11,
    )
    metas = [
        SourceMeta(f"{m.session_id}_trial{i:03d}", m.session_id, m.split, m.label)
        for i, m in enumerate(metas)
    ]
    return X, M, metas, cells


class ExecutionRegressionTests(unittest.TestCase):
    def test_source_identity_vocabulary_never_contains_validation(self):
        manifest = [
            {
                "split": split,
                "label": label,
                "pseudo_row": "0",
                "product_row": "0",
                "session_id": "s0_session01",
                "source_trial_id": f"{split}_{label}",
            }
            for split in ("train", "validation")
            for label in study.LABELS
        ]
        X, y, levels = study.source_index_feature_rows(manifest, rows_per_class=1)
        self.assertEqual(X.shape, (2, 2))
        self.assertEqual(y.tolist(), [0, 1])
        self.assertTrue(all("validation" not in key for key in levels))
        val = study.exact_source_index_features(
            [r for r in manifest if r["split"] == "validation"], levels
        )
        self.assertFalse(np.any(val))

    def test_row_grid_executes_exact_pca_and_nonleaky_identity_control(self):
        X, M, metas, cells = fixture()
        Xv, yv, wv, vm, _ = study.exact_validation_product(X, M, metas, cells)
        rows, predictions = study.run_track_a_row_grid(
            Xsrc=X,
            Msrc=M,
            metas=metas,
            source_index={m.source_trial_id: i for i, m in enumerate(metas)},
            cells=cells,
            Xval=Xv,
            yval=yv,
            wval=wv,
            val_manifest=vm,
            rows_per_class_grid=(4,),
            seeds=(0,),
            pca_dims=(1, 2),
        )
        representations = {r.get("representation") for r in rows}
        self.assertTrue(
            {"moment_pca_cellspace_1", "moment_pca_cellspace_2"} <= representations
        )
        identity = [
            r for r in rows if r.get("representation") == "source_index_control"
        ]
        self.assertEqual(len(identity), 2)
        self.assertTrue(all(r["balanced_accuracy"] == 0.5 for r in identity))
        self.assertGreater(len(predictions), 0)

    def test_real_session_controls_cannot_call_pseudopopulation_builder(self):
        X, M, metas, cells = fixture()
        z = {"X_source_cell_bin": X, "observed_source_cell_mask": M}
        index = {m.source_trial_id: i for i, m in enumerate(metas)}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with (
                patch.object(study, "validate_under_accepted", side_effect=lambda p: p),
                patch.object(
                    study, "_load_v7_stage", return_value=(z, metas, index, cells)
                ),
                patch.object(
                    study,
                    "build_dataset",
                    side_effect=AssertionError("stitching forbidden"),
                ),
            ):
                result = study.run_relaxed40_source_controls(
                    stage_dir=root, output_dir=root, seeds=(0, 1), fractions=(0.5, 1.0)
                )
            self.assertEqual(result["metric_rows"], 24)
            self.assertEqual(
                result["input_kind"], "real_source_trials_not_pseudopopulations"
            )
            with (root / "track_a_relaxed40_source_controls.csv").open() as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(
                {r["representation"] for r in rows},
                {"raw_total", "raw_binned", "trial_index_only"},
            )
            self.assertTrue(all(int(r["n_validation_sources"]) == 4 for r in rows))
            for row in rows:
                self.assertTrue(
                    set(row["train_source_ids"].split(";")).isdisjoint(
                        row["validation_source_ids"].split(";")
                    )
                )

    def test_source_budget_uses_exact_moments_not_assembly_draws(self):
        X, M, metas, cells = fixture()
        Xv, yv, wv, _, _ = study.exact_validation_product(X, M, metas, cells)
        with patch.object(
            study, "build_dataset", side_effect=AssertionError("assembly forbidden")
        ):
            rows = study.run_track_a_source_budget(
                Xsrc=X,
                Msrc=M,
                metas=metas,
                source_index={},
                cells=cells,
                Xval=Xv,
                yval=yv,
                wval=wv,
                fractions=(0.5, 1.0),
                seeds=(0,),
                rows_per_class=16,
            )
        self.assertEqual(len(rows), 2)
        small, full = (set(r["train_source_ids"].split(";")) for r in rows)
        self.assertTrue(small < full)
        self.assertEqual([r["n_train_sources_used"] for r in rows], [8, 16])

    def test_named_target_cannot_fall_back_to_old_middle_label(self):
        row = {
            "source_trial_id": "s0_session01_trial001",
            "cell_id": "s0/session01/unit1",
            "cue_spike_count": "1",
            "cue_duration_s": "1",
            "trial_index": "1",
            "session_id": "s0_session01",
            "split": "train",
            "endpoint_pair": "4->3",
            "component_label": "present",
        }
        for target in ("anywhere", "supported_middle"):
            with self.assertRaises(ValueError):
                study.per_unit_rows_from_export([row], target_mode=target)

    def test_behavior_ranking_denominator_is_gate_qualified(self):
        rows = [
            {
                "source_trial_id": f"{session}_{label}_{i}",
                "session_id": session,
                "split": "train",
                "endpoint_pair": "4->3",
                "component_label": label,
            }
            for session, n in (("small", 3), ("qualified", 10))
            for label in study.LABELS
            for i in range(n)
        ]
        result = study.behavior_support_funnel_from_allowlist(rows)
        self.assertEqual(result["eligible_train_source_count_total"], 26)
        self.assertEqual(result["qualified_train_source_count_total"], 20)
        self.assertEqual(result["sessions_meeting_unit_source_gate"], 1)

    def test_weighted_scores_are_class_balanced_and_rank_is_not_clipped(self):
        y = np.array([0, 0, 0, 1])
        probability = np.array([0.2, 0.2, 0.2, 0.6])
        measured = study.weighted_binary_metrics(
            y, probability, study.exact_class_weights(y)
        )
        self.assertAlmostEqual(measured["log_loss"], -(np.log(0.8) + np.log(0.6)) / 2)
        self.assertAlmostEqual(measured["brier"], 0.1)
        clipped = study.ridge_score_to_probability(np.array([2.0, 3.0]))
        ranked = study.weighted_binary_metrics(
            np.array([0, 1]), clipped, ranking_score=np.array([2.0, 3.0])
        )
        self.assertEqual(ranked["auroc"], 1.0)

    def test_completed_fit_reuse_rejects_missing_or_changed_artifacts(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            names = {
                "checkpoint_final.pth",
                "embeddings_predictions_decoder.npz",
                "metrics.csv",
                "predictions.csv",
                "generated_assembly_manifest.csv",
                "exact_evaluation_manifest.csv",
            }
            for name in names:
                (root / name).write_bytes(b"synthetic artifact")
            (root / "loss_trace.csv").write_text("step,total\n1,1\n2,0.9\n")
            hashes = {p.name: study.sha256_file(p) for p in root.iterdir()}
            info = {
                "fit_identity_hash": "fixture",
                "fit_spec": {"updates": 2},
                "artifact_sha256": hashes,
                "save_load_max_abs_embedding_diff": 0.0,
            }
            (root / "fit_info.json").write_text(json.dumps(info))
            self.assertEqual(
                study.validate_completed_cebra_fit(root, "fixture")["fit_spec"][
                    "updates"
                ],
                2,
            )
            (root / "predictions.csv").write_text("changed")
            with self.assertRaises(ValueError):
                study.validate_completed_cebra_fit(root, "fixture")

    def test_legacy_cebra_prediction_schema_has_no_C_column(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "v9_predictions.csv"
            path.write_text(
                "representation,dim,seed,split,row,prob_present\n"
                "cebra_time,8,0,validation,0,0.25\n"
            )
            values = study._prediction_probs_from_csv(
                path, seed=0, representation="cebra_time", split="validation", dim=8
            )
            np.testing.assert_array_equal(values, [0.25])

    def test_inclusive_permutation_comparison_keeps_floating_ties(self):
        observed = 7 / 12
        numerically_lower_tie = np.nextafter(observed, -np.inf)
        result = study._p_value_greater_equal(observed, [numerically_lower_tie, 0.5])
        self.assertEqual(result["exceedances"], 1)
        self.assertEqual(result["p_value"], 2 / 3)
        self.assertGreater(result["tie_tolerance"], observed - numerically_lower_tie)


if __name__ == "__main__":
    unittest.main()
