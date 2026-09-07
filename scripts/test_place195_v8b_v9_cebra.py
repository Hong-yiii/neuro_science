# pyright: reportMissingImports=false
import csv
import tempfile
import unittest
from collections import defaultdict
from pathlib import Path

import numpy as np
import torch
from cebra.data.single_session import DiscreteDataLoader

from scripts.place195_v8b_v9_cebra import (
    SameTrialTimeLoader,
    TrialCueDataset,
    flatten_rows,
    make_solver,
    run_cebra_fit,
)


class V8bV9CebraTest(unittest.TestCase):
    def test_flatten_rows_preserves_trial_bins_and_labels(self):
        X = np.arange(2 * 3 * 4, dtype="float32").reshape(2, 3, 4)
        y = np.array([0, 1])
        Xflat, trial, bins, labels = flatten_rows(X, y)
        self.assertEqual(Xflat.shape, (8, 3))
        np.testing.assert_array_equal(trial, [0, 0, 0, 0, 1, 1, 1, 1])
        np.testing.assert_array_equal(bins, [0, 1, 2, 3, 0, 1, 2, 3])
        np.testing.assert_array_equal(labels, [0, 0, 0, 0, 1, 1, 1, 1])
        np.testing.assert_array_equal(Xflat[1], X[0, :, 1])

    def test_time_loader_samples_only_within_trial_offset_one(self):
        device = "cuda" if torch.cuda.is_available() else "cpu"
        X = np.zeros((2, 2, 4), dtype="float32")
        y = np.array([0, 1])
        Xflat, trial, bins, labels = flatten_rows(X, y)
        ds = TrialCueDataset(Xflat, trial, bins, labels, device=device)
        loader = SameTrialTimeLoader(dataset=ds, time_offset=1, num_steps=1, batch_size=64)
        idx = loader.get_indices(64)
        self.assertTrue(torch.all(ds.trial_ids[idx.reference] == ds.trial_ids[idx.positive]).item())
        self.assertTrue(torch.all(ds.bin_ids[idx.positive] == ds.bin_ids[idx.reference] + 1).item())
        self.assertFalse(torch.any(ds.bin_ids[idx.reference] == 3).item())

    def test_offset1_fast_path_matches_cebra_trial_expansion(self):
        device = "cuda" if torch.cuda.is_available() else "cpu"
        solver = make_solver(3, 2, 4, 1e-3, device)
        self.assertEqual(str(solver.model.get_offset()), "Offset(left = 0, right = 1, length = 1)")
        X = np.arange(8 * 3, dtype="float32").reshape(8, 3)
        trial_ids = np.repeat([0, 1], 4)
        ds = TrialCueDataset(X, trial_ids, np.tile(np.arange(4), 2), device=device)
        ds.configure_for(solver.model)
        idx = torch.tensor([0, 3, 4, 7], device=device)
        fast = ds[idx]
        slow_expanded = ds.expand_index_in_trial(idx, ds.trial_ids, ds.trial_borders)
        slow = ds.neural[slow_expanded].transpose(2, 1)
        self.assertEqual(tuple(fast.shape), (4, 3, 1))
        self.assertEqual(float(torch.max(torch.abs(fast - slow)).item()), 0.0)

    def test_behavior_loader_samples_matching_labels(self):
        device = "cuda" if torch.cuda.is_available() else "cpu"
        X = np.zeros((4, 2, 3), dtype="float32")
        y = np.array([0, 0, 1, 1])
        Xflat, trial, bins, labels = flatten_rows(X, y)
        ds = TrialCueDataset(Xflat, trial, bins, labels, device=device)
        loader = DiscreteDataLoader(dataset=ds, num_steps=1, batch_size=64, prior="empirical")
        idx = loader.get_indices(64)
        self.assertIsNotNone(ds.discrete_index)
        labels = ds.discrete_index
        if labels is None:
            self.fail("discrete labels missing")
        self.assertTrue(torch.all(labels[idx.reference] == labels[idx.positive]).item())

    def test_saved_manifest_has_seven_session_components_per_pseudorow(self):
        path = Path(
            "outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/"
            "v7-v8-neural-experiments/primary29_min3train_min1val/bin100ms/pseudo_manifest_seed0.csv"
        )
        self.assertTrue(path.exists())
        seen = defaultdict(set)
        with path.open(newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                seen[(r["split"], r["label"], r["pseudo_row"])].add(r["session_id"])
        self.assertEqual({len(v) for v in seen.values()}, {7})

    def test_tiny_cebra_fit_writes_save_load_parity(self):
        device = "cuda" if torch.cuda.is_available() else "cpu"
        X = np.random.default_rng(0).normal(size=(8, 3, 4)).astype("float32")
        y = np.array([0, 1] * 4)
        arrays = {"train": (X, y), "validation": (X.copy(), y.copy())}
        with tempfile.TemporaryDirectory() as td:
            rows, _preds, info = run_cebra_fit(
                arrays,
                variant="cebra_time",
                dim=2,
                seed=0,
                outdir=Path(td),
                iterations=2,
                batch_size=8,
                lr=1e-3,
                hidden=4,
                device=device,
            )
            self.assertTrue((Path(td) / "checkpoint_final.pth").exists())
            self.assertEqual(info["save_load_max_abs_embedding_diff"], 0.0)
            self.assertEqual(len(rows), 2)


if __name__ == "__main__":
    unittest.main()
