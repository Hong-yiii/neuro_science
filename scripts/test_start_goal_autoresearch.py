"""Run with the audited runtime: python -m unittest scripts.test_start_goal_autoresearch."""

import tempfile
import unittest
from pathlib import Path

import numpy as np
import torch
from sklearn.preprocessing import StandardScaler

from scripts.place195_v8b_v9_cebra import TrialCueDataset, embed_rows, flatten_rows
from scripts.start_goal_autoresearch import (
    BASE,
    PAIRS,
    BinLabelLoader,
    Cfg,
    SourceMeta,
    arrays,
    encoder_rows,
    geometry,
    hidden_features,
    pca_features,
    readout,
    solver_for,
    subset_sources,
    target_labels,
    verify_inputs,
)


class StudyChecks(unittest.TestCase):
    def test_label_mapping(self):
        y = np.arange(30)
        np.testing.assert_array_equal(target_labels(y, "start"), np.array(PAIRS)[:, 0])
        np.testing.assert_array_equal(target_labels(y, "goal"), np.array(PAIRS)[:, 1])
        with self.assertRaises(ValueError):
            target_labels(y, "path")

    def test_sampler_denominator_and_groups(self):
        # Unequal class sizes check padded group pools as well as all-to-all negatives.
        y = np.array([0, 0, 0, 1, 2, 2])
        x = np.zeros((len(y), 9, 10), dtype="float32")
        flat, tid, bid, labels = flatten_rows(x, y)
        ds = TrialCueDataset(flat, tid, bid, labels, device="cpu")
        loader = BinLabelLoader(dataset=ds, num_steps=1, batch_size=256)  # type: ignore[reportCallIssue]  # inherited CEBRA dataclass signature
        for _ in range(10):
            ix = loader.get_indices(256)
            r, p, n = (v.numpy() for v in (ix.reference, ix.positive, ix.negative))
            np.testing.assert_array_equal(labels[r], labels[p])
            np.testing.assert_array_equal(bid[r], bid[p])
            self.assertTrue(np.all(bid[r, None] == bid[n][None, :]))
        loader.match_negative = False
        loader.group_references = False
        ix = loader.get_indices(256)
        self.assertGreater(len(np.unique(bid[ix.reference])), 1)
        np.testing.assert_array_equal(labels[ix.reference], labels[ix.positive])
        np.testing.assert_array_equal(bid[ix.reference], bid[ix.positive])
        loader.match_negative = True
        with self.assertRaises(ValueError):
            loader.get_indices(256)

    def test_shape_and_hidden_normalization(self):
        torch.manual_seed(41)
        rng = np.random.default_rng(41)
        x = rng.normal(size=(12, 9, 10)).astype("float32")
        self.assertEqual(encoder_rows(x, True).shape, (12, 90, 1))
        flat, _, _, _ = flatten_rows(x, np.zeros(12))
        scaler = StandardScaler().fit(flat)
        solver = solver_for(9, Cfg(), "cpu")
        solver.n_features = 9
        z = embed_rows(solver, scaler, x, device="cpu", dim=8)
        post = hidden_features(solver.model, scaler, x, "cpu", 8)
        pre = hidden_features(solver.model, scaler, x, "cpu", 7).reshape(-1, 8)
        np.testing.assert_allclose(z, post, atol=1e-7)
        np.testing.assert_allclose(
            pre / np.linalg.norm(pre, axis=1, keepdims=True),
            post.reshape(-1, 8),
            atol=1e-6,
        )

    def test_nested_sources_and_temporal_order(self):
        rows = [
            SourceMeta(
                f"s_trial{i:03}", "s", "train" if i % 4 else "validation", str(i % 2)
            )
            for i in range(40)
        ]
        small = subset_sources(rows, 0.25, 0)
        medium = subset_sources(rows, 0.5, 0)
        self.assertLessEqual(
            {m.source_trial_id for m in small}, {m.source_trial_id for m in medium}
        )
        self.assertEqual(
            {m.source_trial_id for m in rows if m.split == "validation"},
            {m.source_trial_id for m in small if m.split == "validation"},
        )
        chronological = subset_sources(rows, 1, 0, True)
        for label in ("0", "1"):
            train = [
                m.source_trial_id
                for m in chronological
                if m.label == label and m.split == "train"
            ]
            dev = [
                m.source_trial_id
                for m in chronological
                if m.label == label and m.split == "validation"
            ]
            if dev:
                self.assertLess(max(train), min(dev))

    def test_constant_chance_and_train_only_pca(self):
        y = np.repeat(np.arange(30), 2)
        with tempfile.TemporaryDirectory() as d:
            features = {s: np.zeros((60, 8)) for s in ("train", "development")}
            rows, _ = readout(
                Path(d) / "chance",
                features,
                dict.fromkeys(features, y),
                {"case": "test", "seed": 0},
            )
            self.assertAlmostEqual(rows[-1]["balanced_accuracy"], 1 / 30)
            self.assertEqual(geometry(features, 8)["train"]["participation_ratio"], 0)
        rng = np.random.default_rng(1)
        a = rng.normal(size=(60, 12, 10)).astype("float32")
        data = {"train": (a, y), "development": (a + 1e4, y)}
        _, model = pca_features(data)
        scaler = model.steps[0][1]
        self.assertIsInstance(scaler, StandardScaler)
        np.testing.assert_allclose(
            np.asarray(scaler.mean_), a.mean(axis=(0, 2)), atol=1e-7
        )

    @unittest.skipUnless(BASE.exists(), "local audited source artifacts unavailable")
    def test_actual_input_gate(self):
        self.assertGreater(len(verify_inputs()), 40)
        for seed in (0, 1, 2):
            self.assertEqual(arrays(seed)["train"][0].shape, (480, 195, 10))


if __name__ == "__main__":
    unittest.main()
