"""Invented-array checks of presentation semantics; no fitted or biological inputs."""

from __future__ import annotations

import io
import unittest
from types import SimpleNamespace

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from neuro.notebook_artifacts import no_fitting
from neuro.notebook_diagnostics import (
    embedding_summary,
    learning_summary,
    metrics_table,
    plot_decoder_summary,
    plot_embedding_views,
    plot_learning,
)


def readout(name="observed_seed0_full_pca_pair", *, train=0.9, dev=0.65):
    return {
        "name": name,
        "head": name.rsplit("_", 1)[1],
        "train": {"balanced_accuracy": train},
        "development": {
            "balanced_accuracy": dev,
            "accuracy": 0.7,
            "macro_f1": 0.64,
            "log_loss": 0.6,
            "confusion_counts": [[8, 2], [3, 3]],
        },
        "balanced_accuracy_gap": train - dev,
    }


def instrumented_encoder():
    return SimpleNamespace(
        diagnostics={
            "loss": {
                "total": np.arange(10, 0, -1).tolist(),
                "pos": [-0.1] * 10,
                "neg": np.arange(10, 0, -1).tolist(),
                "temperature": [1.0] * 10,
            },
            "sample_exposure_counts": np.array(
                [[2, 4, 0, 0], [0, 2, 4, 0], [1, 2, 1, 2]]
            ),
            "exposure_summary": {"reference_phase_counts": {"cue": 6, "nav": 0}},
        }
    )


class NotebookDiagnosticTests(unittest.TestCase):
    def tearDown(self):
        plt.close("all")

    def test_metric_units_and_worlds_are_explicit(self):
        rows = [
            readout(),
            readout("permuted_seed1_reduced_cebra_goal", train=0.8, dev=0.4),
        ]
        table = metrics_table(rows)
        self.assertEqual(table[0]["development_BA_percent"], 65)
        self.assertAlmostEqual(table[0]["gap_percentage_points"], 25)
        self.assertEqual(table[0]["uniform_BA_percent"], 50)
        self.assertAlmostEqual(table[0]["uniform_log_loss_nats"], np.log(2))
        self.assertEqual(table[0]["constructed_development_rows"], 16)
        self.assertEqual(
            (table[1]["world"], table[1]["seed"], table[1]["budget"]),
            ("permuted", 1, "reduced"),
        )
        with self.assertRaisesRegex(ValueError, "declare world"):
            metrics_table([readout("unnamed_pair")])
        rows[0]["development"]["confusion_counts"][0] = [0, 0]
        with self.assertRaisesRegex(ValueError, "complete"):
            metrics_table(rows)

    def test_distribution_diagnostic_distinguishes_constant_rank1_and_full_rank(self):
        # Eight vectors with exactly equal coordinate variance; no model is fitted.
        vectors = np.concatenate((np.eye(4), -np.eye(4)))
        features = vectors.reshape(4, 8)
        with no_fitting():
            summary = embedding_summary(features, features.copy(), n_bins=2)
        self.assertEqual(summary["coordinate_count"], 4)
        self.assertEqual(summary["development"]["dependent_bin_vectors"], 8)
        self.assertAlmostEqual(
            summary["train"]["first_three_coordinate_variance_fraction"], 0.75
        )
        self.assertAlmostEqual(
            summary["train"]["effective_rank_participation_ratio"], 4
        )
        rank1 = np.repeat(np.arange(8.0)[:, None], 4, axis=1).reshape(4, 8)
        summary = embedding_summary(rank1, np.ones_like(rank1), n_bins=2)
        self.assertAlmostEqual(
            summary["train"]["effective_rank_participation_ratio"], 1
        )
        self.assertTrue(summary["development"]["zero_centered_variance"])
        self.assertEqual(
            summary["development"]["effective_rank_participation_ratio"], 0
        )
        self.assertIsNone(
            summary["development"]["first_three_coordinate_variance_fraction"]
        )

    def test_embedding_plot_preserves_bin_order_and_is_not_last_bin_projection(self):
        # Row0 bin0=(0,1,2), bin1=(3,4,5); row1 bin0=(6,7,8).
        features = np.arange(12.0).reshape(2, 6)
        original = features.copy()
        with no_fitting():
            fig = plot_embedding_views(
                features,
                features,
                {"start": np.array(["a", "b"]), "goal": np.array(["b", "a"])},
                n_bins=2,
                title="Invented observed/full/seed0",
            )
            # First collection is training bin0; class-a development follows it.
            train_points = np.array(fig.axes[0].collections[0]._offsets3d).T
            class_a_points = np.array(fig.axes[0].collections[1]._offsets3d).T
            np.testing.assert_array_equal(train_points, [[0, 1, 2], [6, 7, 8]])
            np.testing.assert_array_equal(class_a_points, [[0, 1, 2]])
            pooled = np.array(fig.axes[2].collections[0]._offsets3d).T
            np.testing.assert_array_equal(pooled, features.reshape(4, 3))
            np.testing.assert_array_equal(
                fig.axes[2].collections[0].get_array(), [0, 1, 0, 1]
            )
            image = io.BytesIO()
            fig.savefig(image, format="png")
            self.assertGreater(image.tell(), 1000)
        np.testing.assert_array_equal(features, original)

    def test_geometry_rejects_ambiguous_layout_and_target_shape(self):
        features = np.zeros((3, 8))
        for n_bins in (0, True, 3):
            with self.subTest(n_bins=n_bins), self.assertRaises(ValueError):
                embedding_summary(features, features, n_bins=n_bins)
        with self.assertRaisesRegex(ValueError, "dimensions differ"):
            embedding_summary(features, np.zeros((4, 6)), n_bins=2)
        bad = features.copy()
        bad[0, 0] = np.nan
        with self.assertRaisesRegex(ValueError, "finite"):
            embedding_summary(bad, features, n_bins=2)
        with self.assertRaisesRegex(ValueError, "one start/goal target"):
            plot_embedding_views(features, features, ["a->b"], n_bins=2, title="Bad")
        with self.assertRaisesRegex(ValueError, "at least three"):
            plot_embedding_views(
                np.ones((3, 4)), np.ones((3, 4)), ["a->b"] * 3, n_bins=2, title="Bad"
            )

    def test_learning_summary_exposes_role_specific_coverage_and_loss_windows(self):
        encoder = instrumented_encoder()
        with no_fitting():
            result = learning_summary(encoder)
            fig = plot_learning(encoder, title="Invented observed/full/seed0")
            fig.savefig(io.BytesIO(), format="png")
        self.assertEqual(result["updates_recorded"], 10)
        self.assertEqual(result["summary_window_updates"], 2)
        self.assertEqual(result["loss_components"]["total"]["first_window_mean"], 9.5)
        self.assertEqual(result["loss_components"]["total"]["last_window_mean"], 1.5)
        self.assertEqual(result["loss_components"]["total"]["last_minus_first"], -8)
        self.assertEqual(result["sampler"]["reference"]["coverage_fraction"], 0.5)
        self.assertEqual(result["sampler"]["negative"]["coverage_fraction"], 1)
        self.assertEqual(result["reference_phase_counts"], {"cue": 6, "nav": 0})
        encoder.diagnostics["loss"]["total"][3] = float("nan")
        self.assertFalse(learning_summary(encoder)["finite_loss_components"]["total"])

    def test_decoder_plot_keeps_world_head_seed_and_budget_visible_without_fitting(
        self,
    ):
        rows = [
            readout(f"{world}_seed{seed}_{budget}_{model}_{head}")
            for world in ("observed", "permuted")
            for seed in (0, 1)
            for budget in ("full", "reduced")
            for model in ("raw", "pca")
            for head in ("pair", "goal")
        ]
        with no_fitting():
            fig = plot_decoder_summary(rows)
            fig.savefig(io.BytesIO(), format="png")
        self.assertEqual(len(fig.axes), 8)
        self.assertIn("observed · pair", fig.axes[0].get_title())
        self.assertIn("permuted · goal", fig.axes[6].get_title())
        self.assertEqual(len(fig.axes[0].collections), 2)
        self.assertEqual(sum(len(c.get_offsets()) for c in fig.axes[0].collections), 8)


if __name__ == "__main__":
    unittest.main()
