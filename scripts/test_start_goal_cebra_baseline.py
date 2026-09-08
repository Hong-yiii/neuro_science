"""Small synthetic checks; no lab data or original holdout access."""

import argparse
import tempfile
import unittest
from collections import Counter
from pathlib import Path
from typing import Any, cast

import numpy as np
import torch
from cebra.data.single_session import DiscreteDataLoader

from scripts.place195_v8b_v9_cebra import (
    SameTrialTimeLoader,
    TrialCueDataset,
    flatten_rows,
)
from scripts.start_goal_cebra_baseline import (
    LABELS,
    SourceMeta,
    assemble_dataset,
    decode,
    eligible_trials,
    inner_split,
    representations,
    source_level_shuffle,
)


def synthetic_sources():
    cells = [
        f"{s}/session01/array01/channel{i:03d}/cell01"
        for s in ("dayA", "dayB")
        for i in range(5)
    ]
    metadata = [
        SourceMeta(f"{s}_{label}_{i}", f"{s}_session01", "train", label)
        for s in ("dayA", "dayB")
        for label in LABELS
        for i in range(4)
    ]
    metadata, support = inner_split(metadata, {m.session_id for m in metadata}, 23)
    index = {m.source_trial_id: i for i, m in enumerate(metadata)}
    x = np.full((len(metadata), len(cells), 10), np.nan, dtype=np.float32)
    mask = np.zeros(x.shape[:2], dtype=bool)
    for i, m in enumerate(metadata):
        ci = slice(0, 5) if m.session_id == "dayA_session01" else slice(5, 10)
        x[i, ci, :] = i
        mask[i, ci] = True
    return (x, mask, index, metadata, cells), support


class StartGoalTest(unittest.TestCase):
    def test_split_and_session_blocks_are_source_disjoint(self):
        data, support = synthetic_sources()
        self.assertEqual({r["train"] for r in support}, {3})
        self.assertEqual({r["validation"] for r in support}, {1})
        arrays, manifest = assemble_dataset(*data, 3, 2, 0)
        self.assertEqual(arrays["train"][0].shape, (90, 10, 10))
        self.assertEqual(set(arrays["validation"][1]), set(range(30)))
        used = {split: set() for split in arrays}
        by_id = {m.source_trial_id: m for m in data[3]}
        for r in manifest:
            source = r["source_trial_id"]
            used[r["split"]].add(source)
            self.assertEqual(by_id[source].label, r["label"])
            self.assertEqual(by_id[source].split, r["split"])
            ci = slice(0, 5) if r["session_id"] == "dayA_session01" else slice(5, 10)
            np.testing.assert_array_equal(
                arrays[r["split"]][0][int(r["pseudo_row"]), ci, :],
                data[0][data[2][source], ci, :],
            )
        self.assertFalse(used["train"] & used["validation"])
        replay, _ = assemble_dataset(*data, 3, 2, 0)
        np.testing.assert_array_equal(replay["train"][0], arrays["train"][0])

    def test_missing_condition_or_cell_fails_closed(self):
        data, _ = synthetic_sources()
        without_class = [m for m in data[3] if m.label != LABELS[0]]
        with self.assertRaisesRegex(ValueError, "cannot split fixed panel"):
            inner_split(without_class, {m.session_id for m in data[3]}, 23)
        data[1][:, 0] = False
        with self.assertRaisesRegex(RuntimeError, "observed mask failure"):
            assemble_dataset(*data, 3, 2, 0)

    def test_null_preserves_source_pool_sizes_and_moves_whole_labels(self):
        data, _ = synthetic_sources()
        shuffled = source_level_shuffle(data[3], 42)
        before = Counter((m.session_id, m.split, m.label) for m in data[3])
        after = Counter(
            (m.session_id, m.split, shuffled[m.source_trial_id]) for m in data[3]
        )
        self.assertEqual(before, after)
        self.assertTrue(any(shuffled[m.source_trial_id] != m.label for m in data[3]))
        _, manifest = assemble_dataset(*data, 2, 1, 0, shuffled)
        self.assertTrue(
            all(shuffled[r["source_trial_id"]] == r["label"] for r in manifest)
        )

    def test_eligibility_qc_and_original_split_gate(self):
        def row(i, goal, prev, start):
            codes = f"{10 + goal} {20 + goal} {30 + goal}"
            return {
                "source_trial_id": str(i),
                "previous_source_trial_id": prev,
                "session_id": "A",
                "trial_index": str(i),
                "split": "train",
                "outcome": "success",
                "qc_flags": "",
                "ripple_cue_duration_s": "1.02",
                "marker_minor_digit": str(goal),
                "inferred_start_id_from_previous_marker": f"marker_{start}",
                "inferred_goal_id": f"marker_{goal}",
                "ripple_codes": codes,
                "unity_codes": codes,
                "eyelink_codes": codes,
            }

        rows = [row(1, 1, "", 0), row(2, 2, "1", 1)]
        kept, excluded = eligible_trials(rows)
        self.assertEqual([m.label for m in kept], ["1->2"])
        self.assertEqual(len(excluded), 1)
        rows[0]["ripple_cue_duration_s"] = "0.99"
        self.assertEqual([m.label for m in eligible_trials(rows)[0]], ["1->2"])
        rows[1]["ripple_cue_duration_s"] = "0.99"
        self.assertFalse(eligible_trials(rows)[0])
        rows[1]["ripple_cue_duration_s"] = "1.02"
        rows[0]["qc_flags"] = "bad_clock"
        self.assertFalse(eligible_trials(rows)[0])
        rows[0]["split"] = "test"
        with self.assertRaisesRegex(ValueError, "non-training"):
            eligible_trials(rows)

    def test_multiclass_representation_fit_decode_reload(self):
        rng = np.random.default_rng(4)
        arrays = {
            split: (
                rng.normal(size=(60, 10, 10)).astype("float32"),
                np.tile(np.arange(30), 2),
            )
            for split in ("train", "validation")
        }
        args = argparse.Namespace(iterations=2, batch_size=32, device="cpu")
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            outputs = dict(representations(arrays, out, args, 0))
            self.assertEqual(
                set(outputs),
                {"raw_total", "raw_binned", "pca8", "cebra_time", "cebra_behavior"},
            )
            self.assertEqual(outputs["cebra_behavior"]["validation"].shape, (60, 80))
            labels = {k: v[1] for k, v in arrays.items()}
            metrics = decode(
                outputs["cebra_behavior"],
                labels,
                out / "decoder",
                "cebra_behavior",
                0,
                -1,
            )
            self.assertEqual(len(metrics), 2)
            saved = np.load(out / "decoder/decoder.npz")
            np.testing.assert_allclose(saved["prob_validation"].sum(axis=1), 1)
            # Validation values cannot change a fitted training transform.
            arrays["validation"] = (
                arrays["validation"][0] + 1000,
                arrays["validation"][1],
            )
            again = dict(representations(arrays, out, args, 0))
            np.testing.assert_allclose(
                outputs["cebra_behavior"]["train"], again["cebra_behavior"]["train"]
            )

    def test_time_and_discrete_samplers_respect_boundaries(self):
        x = np.zeros((60, 10, 10), dtype="float32")
        flat, trial, bins, y = flatten_rows(x, np.tile(np.arange(30), 2))
        ds = TrialCueDataset(flat, trial, bins, y, device="cpu")
        # CEBRA generates dataclass initializers not represented in its stubs.
        indices = cast(Any, SameTrialTimeLoader)(
            dataset=ds, time_offset=1, num_steps=1, batch_size=128
        ).get_indices(128)
        self.assertTrue(
            torch.all(
                ds.trial_ids[indices.reference] == ds.trial_ids[indices.positive]
            ).item()
        )
        self.assertTrue(
            torch.all(
                ds.bin_ids[indices.positive] == ds.bin_ids[indices.reference] + 1
            ).item()
        )
        indices = cast(Any, DiscreteDataLoader)(
            dataset=ds, num_steps=1, batch_size=128, prior="empirical"
        ).get_indices(128)
        labels = ds.discrete_index
        assert labels is not None
        self.assertTrue(
            torch.all(labels[indices.reference] == labels[indices.positive]).item()
        )


if __name__ == "__main__":
    unittest.main()
