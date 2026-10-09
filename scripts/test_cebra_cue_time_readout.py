# pyright: reportMissingImports=false
"""Invented-data checks for the frozen cue-time readout preparation runner."""

from __future__ import annotations

import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

import numpy as np

from scripts import cebra_cue_time_readout as ct
from scripts import cebra_full_trial_transfer as ft


class CueTimeReadoutPreparationTests(unittest.TestCase):
    def test_bin_slice_preserves_raw_cell_major_and_latent_bin_major_order(self):
        raw_cells = np.arange(2 * 29 * 10).reshape(2, 29, 10)
        raw_whole = raw_cells.reshape(2, 290)
        np.testing.assert_array_equal(
            ct.extract_window_features("raw290", raw_whole, "bin03"), raw_cells[:, :, 3]
        )
        np.testing.assert_array_equal(
            ct.extract_window_features("raw290", raw_whole, "wholecue"), raw_whole
        )

        latent_bins = np.arange(2 * 10 * 8).reshape(2, 10, 8)
        latent_whole = latent_bins.reshape(2, 80)
        np.testing.assert_array_equal(
            ct.extract_window_features("pca8", latent_whole, "bin03"),
            latent_bins[:, 3, :],
        )
        np.testing.assert_array_equal(
            ct.extract_window_features("cue_time", latent_whole, "wholecue"),
            latent_whole,
        )
        self.assertEqual(ct.feature_dim("raw290", "bin00"), 29)
        self.assertEqual(ct.feature_dim("full_time", "wholecue"), 80)

    def test_exact_class_weights_for_24_absent_6_present_validation_rows(self):
        y = np.array([0] * 24 + [1] * 6)
        weights = ft.exact_class_weights(y)
        self.assertAlmostEqual(float(weights[y == 0].sum()), 0.5)
        self.assertAlmostEqual(float(weights[y == 1].sum()), 0.5)
        self.assertAlmostEqual(float(weights.sum()), 1.0)
        self.assertAlmostEqual(float(weights[y == 1][0] / weights[y == 0][0]), 4.0)

    def test_count_exposure_gate_rejects_negative_or_nonfinite_observed_counts(self):
        cohort, _nav = ft.synthetic_cohort(seed=7)
        ok = ct.validate_counts_exposure(cohort)
        self.assertTrue(ok["mask_matches_session"])
        bad_x = cohort.X.copy()
        first = np.argwhere(cohort.mask)[0]
        bad_x[first[0], first[1], 0] = -1
        with self.assertRaises(RuntimeError):
            ct.validate_counts_exposure(replace(cohort, X=bad_x))
        bad_exposure = cohort.exposure.copy()
        bad_exposure[0, 0] = np.nan
        with self.assertRaises(RuntimeError):
            ct.validate_counts_exposure(replace(cohort, exposure=bad_exposure))

    def test_train_only_decoder_state_ignores_validation_values(self):
        rng = np.random.default_rng(0)
        y = np.tile([0, 1], 16)
        Xtr = np.column_stack([y, 1 - y]).astype(float) + rng.normal(
            scale=0.01, size=(32, 2)
        )
        Xva_a = rng.normal(size=(5, 2))
        Xva_b = rng.normal(size=(7, 2)) + 100
        with tempfile.TemporaryDirectory() as td:
            ft.fit_decoder("logistic", Xtr, y, Xva_a, outdir=Path(td) / "a")
            ft.fit_decoder("logistic", Xtr, y, Xva_b, outdir=Path(td) / "b")
            a = np.load(Path(td) / "a/logistic_decoder_state.npz", allow_pickle=False)
            b = np.load(Path(td) / "b/logistic_decoder_state.npz", allow_pickle=False)
            for key in ("scaler_mean", "scaler_scale", "coef", "intercept", "classes"):
                np.testing.assert_allclose(a[key], b[key])

    def test_null_family_uses_three_seed_mean_before_max_over_bins(self):
        rows = []
        worlds = ["observed"] + [f"null{i:02d}" for i in range(20)]
        for world in worlds:
            for seed in ft.SEEDS:
                for rep in ct.REPRESENTATIONS:
                    for readout in ct.DECODERS:
                        for window in ct.WINDOWS:
                            for split in ("validation",):
                                loss = 1.0
                                if (
                                    rep == "cue_time"
                                    and readout == "logistic"
                                    and window == "bin00"
                                ):
                                    loss = (
                                        100.0
                                        if (world == "observed" and seed == 0)
                                        else 2.0
                                    )
                                if (
                                    rep == "full_time"
                                    and readout == "logistic"
                                    and window == "bin00"
                                ):
                                    loss = 0.0 if world == "observed" else 1.0
                                if (
                                    rep == "cue_time"
                                    and readout == "logistic"
                                    and window == "bin01"
                                ):
                                    loss = 3.0 if world == "observed" else 1.0
                                if (
                                    rep == "full_time"
                                    and readout == "logistic"
                                    and window == "bin01"
                                ):
                                    loss = 1.0
                                rows.append(
                                    {
                                        "world": world,
                                        "world_index": 0,
                                        "seed": seed,
                                        "representation": rep,
                                        "window": window,
                                        "readout": readout,
                                        "split": split,
                                        "balanced_log_loss": loss
                                        if readout == "logistic"
                                        else "",
                                        "balanced_brier": 0.25
                                        if readout == "logistic"
                                        else "",
                                        "balanced_accuracy": 0.5,
                                        "auroc": 0.5,
                                        "recall_absent": 0.5,
                                        "recall_present": 0.5,
                                        "n": 2,
                                        "positive_fraction": 0.5,
                                        "fit_origin": "fake",
                                        "feature_dim": ct.feature_dim(rep, window),
                                    }
                                )
        with tempfile.TemporaryDirectory() as td:
            summary = ct.summarize_metrics(rows, Path(td))
        self.assertAlmostEqual(summary["primary_null_family"]["observed"], 104 / 3)
        # If the family incorrectly maximized a single seed, this would be 100.
        self.assertLess(summary["primary_null_family"]["observed"], 35)

    def test_source_sensitivity_marks_singleton_source_deletions_inestimable(self):
        predictions = []
        for seed in ft.SEEDS:
            for rep in ct.REPRESENTATIONS:
                for window in ct.WINDOWS:
                    for readout in ct.DECODERS:
                        for label, score in (("absent", 0.1), ("present", 0.9)):
                            predictions.append(
                                {
                                    "world": "observed",
                                    "world_index": 0,
                                    "seed": seed,
                                    "representation": rep,
                                    "window": window,
                                    "readout": readout,
                                    "split": "validation",
                                    "row_id": label,
                                    "label": label,
                                    "pred_label": label,
                                    "score": score,
                                    "fit_origin": "fake",
                                    "sources": f"session={label}-source",
                                }
                            )
        with tempfile.TemporaryDirectory() as td:
            summary = ct.observed_source_sensitivity(predictions, Path(td))
        self.assertEqual(summary["deletions"], 2)
        self.assertEqual(summary["inestimable_deletions"], 2)
        self.assertFalse(summary["pseudorow_bootstrap_used"])

    def test_no_fit_guard_and_approval_tamper_rejection(self):
        y = np.tile([0, 1], 4)
        X = y[:, None].astype(float)
        with tempfile.TemporaryDirectory() as td:
            with ct.no_fit_guard(), self.assertRaises(RuntimeError):
                ft.fit_decoder("logistic", X, y, X, outdir=Path(td) / "blocked")
            approval = Path(td) / "approval.json"
            audit = Path(td) / "audit.json"
            audit.write_text("{}")
            approval.write_text(
                __import__("json").dumps(
                    {
                        "approved": True,
                        "script_sha256": "tampered",
                        "source_audit_path": str(audit),
                        "source_audit_sha256": ct.sha256_file(audit),
                    }
                )
            )
            with (
                patch.object(
                    ct, "approval_facts", return_value={"script_sha256": "original"}
                ),
                self.assertRaisesRegex(RuntimeError, "approval facts differ"),
            ):
                ct.require_prefit_approval(approval)

    def test_all_windows_replay_with_corruption_rejected(self):
        y = np.array([0, 1])
        score = np.array([0.1, 0.9])
        plans = [
            {"row_id": label, "sources": {"session": label}} for label in ft.LABELS
        ]
        metrics, predictions = [], []
        for window in ct.WINDOWS:
            prefix = {
                "world": "observed",
                "world_index": 0,
                "seed": 0,
                "representation": "cue_time",
                "window": window,
                "readout": "logistic",
                "fit_origin": "accepted_wholecue_replay"
                if window == "wholecue"
                else "new_single_bin_readout",
            }
            metrics.append(
                ct.metric_row(
                    y,
                    y,
                    score,
                    weights=ft.exact_class_weights(y),
                    readout="logistic",
                    prefix={**prefix, "split": "validation"},
                )
            )
            predictions.extend(
                ct.prediction_rows(
                    y,
                    y,
                    score,
                    split="validation",
                    readout="logistic",
                    prefix=prefix,
                    plans=plans,
                )
            )
        self.assertEqual(
            len(ct.compare_window_replay(metrics, predictions, metrics, predictions)),
            11,
        )
        corrupted = [dict(p) for p in predictions]
        corrupted[0]["score"] = 0.8
        with self.assertRaises(RuntimeError):
            ct.compare_window_replay(metrics, predictions, metrics, corrupted)
        with self.assertRaises(RuntimeError):
            ct.compare_window_replay(metrics, predictions, metrics, predictions[2:])

    def test_numeric_state_replay_without_fits_and_hash_tamper(self):
        y = np.tile([0, 1], 12)
        X = np.column_stack([2 * y - 1, y]).astype(float)
        with tempfile.TemporaryDirectory() as td:
            for readout in ct.DECODERS:
                out = Path(td) / readout
                _, _, pred, score, _, _ = ft.fit_decoder(readout, X, y, X, outdir=out)
                with ct.no_fit_guard():
                    replay_pred, replay_score = ft.predict_decoder_state(
                        out / f"{readout}_decoder_state.npz", X
                    )
                np.testing.assert_array_equal(replay_pred, pred)
                np.testing.assert_allclose(replay_score, score, atol=1e-10)
                ft.write_hash_manifest(out)
                ft.verify_hash_manifest(out)
                (out / f"{readout}_decoder_state.json").write_text("tampered")
                with self.assertRaises(RuntimeError):
                    ft.verify_hash_manifest(out)


if __name__ == "__main__":
    unittest.main()
