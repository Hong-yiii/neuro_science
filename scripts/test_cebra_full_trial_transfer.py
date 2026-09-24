# pyright: reportMissingImports=false
import argparse
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

import numpy as np
import torch

from scripts import cebra_full_trial_transfer as ft


class CebraFullTrialTransferTest(unittest.TestCase):
    def _small_bundle(self):
        cohort, nav = ft.synthetic_cohort(seed=1)
        plans = ft.make_training_plans(
            cohort.metas, cohort.cell_ids, rows_per_class=3, seed=0
        )
        bundle = ft.materialize_cue_rows(cohort, plans)
        scaler = ft.fit_cue_scaler(bundle.X_cue)
        bank = ft.build_pair_bank(bundle, nav, scaler, cohort.cell_ids)
        X_scaled = ft.transform_cue_samples(bundle.X_cue, scaler)
        return cohort, nav, bundle, bank, X_scaled

    def test_pair_bank_covers_every_native_adjacent_pair(self):
        _cohort, _nav, _bundle, bank, _X_scaled = self._small_bundle()
        self.assertTrue(bank.coverage_rows)
        for row in bank.coverage_rows:
            self.assertEqual(row["native_adjacent_pairs"], row["represented_pairs"])
        self.assertTrue(
            any(len(g) != len(bank.nav_pairs_by_row[0]) for g in bank.nav_pairs_by_row)
        )

    def test_time_sampler_is_row_uniform_not_flat_pair_weighted(self):
        _cohort, _nav, bundle, bank, X_scaled = self._small_bundle()
        ds, payload, _info = ft.cebra_dataset_for_arm(
            "full_time", X_scaled, bundle.y, bank, device="cpu"
        )
        loader = ft.PhaseTimeLoader(
            dataset=ds,
            pair_groups_by_phase=payload["pair_groups_by_phase"],
            sample_groups_by_phase=payload["sample_groups_by_phase"],
            num_steps=1,
            batch_size=1,
            seed=123,
            phase_probs=payload["phase_probs"],
        )
        idx = loader.get_indices(12000)
        self.assertTrue(
            torch.all(ds.labels[idx.reference] == ds.labels[idx.positive]).item()
        )
        nav_counts = loader.reference_row_counts[1].cpu().numpy()
        nonzero = nav_counts[nav_counts > 0]
        self.assertLess(nonzero.max() / nonzero.min(), 1.8)

    def test_behavior_sampler_keeps_positive_label_and_balances_rows(self):
        _cohort, _nav, bundle, bank, X_scaled = self._small_bundle()
        ds, payload, _info = ft.cebra_dataset_for_arm(
            "full_behavior", X_scaled, bundle.y, bank, device="cpu"
        )
        loader = ft.PhaseBehaviorLoader(
            dataset=ds,
            sample_groups_by_phase=payload["sample_groups_by_phase"],
            row_labels=payload["row_labels"],
            num_steps=1,
            batch_size=1,
            seed=456,
            phase_probs=payload["phase_probs"],
        )
        idx = loader.get_indices(12000)
        self.assertTrue(
            torch.all(ds.labels[idx.reference] == ds.labels[idx.positive]).item()
        )
        counts = loader.reference_row_counts.sum(dim=0).cpu().numpy()
        self.assertLess(counts.max() / counts.min(), 1.8)

    def test_validation_manifest_ids_are_class_qualified(self):
        cohort, _nav = ft.synthetic_cohort(seed=2)
        plans, _support = ft.make_validation_plans(cohort.metas, cohort.cell_ids)
        keys = [p["manifest_key"] for p in plans]
        self.assertTrue(all("|" in key for key in keys))
        self.assertEqual(len(keys), len(set(keys)))

    def test_shuffle_reports_actual_changed_fraction(self):
        cohort, _nav = ft.synthetic_cohort(seed=3)
        labels, info = ft.shuffled_source_labels(cohort.metas, seed=50000)
        changed = sum(labels[m.source_trial_id] != m.label for m in cohort.metas)
        self.assertEqual(info["actual_changed_count"], changed)
        self.assertIn("movable_by_stratum_fraction", info)

    def test_prefit_approval_tamper_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            audit = Path(td) / "audit_manifest.json"
            ft.write_json(audit, {"ok": True})
            approval = Path(td) / "approval.json"
            facts = {"code_sha256": "approved-code", "navigation_sha256": "approved-nav"}
            ft.write_json(approval, {"approved": True, **facts, "code_sha256": "tampered"})
            with patch.object(ft, "approval_facts", return_value=facts):
                with self.assertRaises(RuntimeError):
                    ft.require_prefit_approval(approval, audit)

    def test_nav_loader_rejects_validation_split(self):
        cohort, nav = ft.synthetic_cohort(seed=4)
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "bad_nav.npz"
            np.savez_compressed(
                path,
                nav_counts_flat=nav.counts_flat,
                nav_exposure_flat=nav.exposure_flat,
                nav_observed_mask_flat=nav.observed_mask_flat,
                nav_offsets=nav.offsets,
                nav_n_bins=nav.n_bins,
                source_trial_ids=np.asarray(nav.source_trial_ids),
                source_session_ids=np.asarray(nav.source_session_ids),
                source_labels=np.asarray(nav.source_labels),
                source_splits=np.asarray(["validation"] * len(nav.source_trial_ids)),
                source_trial_indices=nav.source_trial_indices,
                cell_ids=np.asarray(nav.cell_ids),
                bin_width_s=np.asarray([ft.BIN_WIDTH_S], dtype=np.float32),
            )
            with self.assertRaises(RuntimeError):
                ft.load_nav_data(path, cohort)

    def test_tiny_synthetic_end_to_end_smoke(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "smoke"
            summary = ft.run_synthetic_smoke(
                out, iterations=1, batch_size=8, device="cpu"
            )
            self.assertEqual(summary["status"], "synthetic_smoke_passed")
            self.assertTrue((out / "metrics.csv").exists())
            self.assertTrue((out / "worlds/00_observed/seed0/encoders/cue_time/checkpoint_final.pth").exists())
            cohort, _nav = ft.synthetic_cohort()
            def no_fit(*args, **kwargs):
                raise AssertionError("fit invoked during replay")
            with patch.object(ft.StandardScaler, "fit", no_fit), patch.object(ft.PCA, "fit", no_fit), patch.object(ft.LogisticRegression, "fit", no_fit), patch.object(ft.SVC, "fit", no_fit), patch.object(torch.optim.Adam, "step", no_fit):
                metrics, predictions, checked = ft.replay_seed_dir(out / "worlds/00_observed/seed0", cohort, device="cpu")
            saved_m = ft.read_csv_rows(out / "metrics.csv")
            saved_p = ft.read_csv_rows(out / "predictions.csv.gz")
            ft.compare_replay(saved_m, saved_p, metrics, predictions)
            self.assertEqual(len(checked), 17)
            with self.assertRaises(RuntimeError):
                ft.compare_replay(saved_m + [saved_m[0]], saved_p, metrics, predictions)
            saved_p[0]["sources"] = "tampered=lineage"
            with self.assertRaises(RuntimeError):
                ft.compare_replay(saved_m, saved_p, metrics, predictions)
            ft.write_hash_manifest(out)
            ft.verify_hash_manifest(out)
            (out / "metrics.csv").write_text("tampered")
            with self.assertRaises(RuntimeError):
                ft.verify_hash_manifest(out)

    def test_locked_config_deadline_and_summary_integrity(self):
        args = argparse.Namespace(**{k: ft.locked_config()["encoder"][k] for k in ("iterations", "batch_size", "lr", "hidden", "dim")})
        ft.validate_run_config(args)
        args.dim = 3
        with self.assertRaises(RuntimeError):
            ft.validate_run_config(args)
        with self.assertRaises(RuntimeError):
            ft.check_deadline(0)
        with self.assertRaises(RuntimeError):
            ft.assert_equivalent({"tail": .05}, {"tail": .10})

    def test_source_sensitivity_averages_seeds_not_last_seed(self):
        predictions = []
        for seed in (0, 1, 2):
            for rep in ft.REPRESENTATIONS:
                for readout in ft.DECODERS:
                    correctness_probability = (.9, .5, .1)[seed] if rep.startswith("cue_") else (.1, .5, .9)[seed]
                    for y, label in enumerate(ft.LABELS):
                        score = correctness_probability if y else 1 - correctness_probability
                        predictions.append({"world": "observed", "split": "validation", "seed": seed,
                                            "representation": rep, "readout": readout, "row_id": label,
                                            "label": label, "pred_label": ft.INT_TO_LABEL[int(score >= .5)],
                                            "score": score, "sources": f"session=source-{label}"})
        with tempfile.TemporaryDirectory() as td:
            summary = ft.source_sensitivity(predictions, Path(td))
            self.assertEqual(summary["inestimable_deletions"], 2)
            np.testing.assert_allclose(summary["time_mean_gain_quantiles_025_50_975"], 0, atol=1e-12)
            self.assertEqual(summary["seeds"], [0, 1, 2])

    def test_positive_and_no_signal_readout_controls(self):
        y = np.tile([0, 1], 20)
        with tempfile.TemporaryDirectory() as td:
            for name, X, expected in (("positive", (2 * y - 1)[:, None].astype(float), 1.), ("constant", np.zeros((40, 1)), .5)):
                ptr, scores, pva, sva, _model, _scaler = ft.fit_decoder("logistic", X, y, X, outdir=Path(td) / name)
                assert sva is not None
                replay_pred, replay_score = ft.predict_decoder_state(Path(td) / name / "logistic_decoder_state.npz", X)
                np.testing.assert_array_equal(replay_pred, pva)
                np.testing.assert_allclose(replay_score, sva)
                metrics = ft.metric_row(y, pva, sva, weights=ft.exact_class_weights(y), readout="logistic", prefix={})
                self.assertEqual(metrics["balanced_accuracy"], expected)



if __name__ == "__main__":
    unittest.main()
