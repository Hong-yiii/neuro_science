import collections
import unittest

import numpy as np

from scripts.place195_v7_v8_neural_experiments import (
    LABELS,
    SourceMeta,
    assemble_pseudo,
    bin_events,
    source_level_shuffle,
)


class V7V8NeuralExperimentsTest(unittest.TestCase):
    def test_half_open_bin_events_and_conservation(self):
        counts, exposure, omitted = bin_events([0.0, 0.0999, 0.1, 0.9999, 1.0, 1.01], 1.02, 0.1)
        self.assertEqual(counts.sum(), 4)
        self.assertEqual(omitted, 2)
        self.assertAlmostEqual(float(exposure.sum()), 1.0, places=6)
        self.assertEqual(counts[0], 2)
        self.assertEqual(counts[1], 1)
        self.assertEqual(counts[9], 1)

    def test_source_shuffle_preserves_session_split_counts(self):
        meta = [
            SourceMeta(f"s{i}", "sessA", "train", "present" if i < 3 else "absent")
            for i in range(5)
        ] + [
            SourceMeta(f"v{i}", "sessA", "validation", "present" if i < 2 else "absent")
            for i in range(4)
        ]
        shuffled = source_level_shuffle(meta, 0)
        before = collections.Counter((m.session_id, m.split, m.label) for m in meta)
        after = collections.Counter((m.session_id, m.split, shuffled[m.source_trial_id]) for m in meta)
        self.assertEqual(before, after)

    def test_assemble_pseudo_uses_one_source_per_session_for_all_cells_bins(self):
        cells = ["d1/session01/array/cell1", "d1/session01/array/cell2", "d2/session01/array/cell1"]
        source_meta = []
        source_index = {}
        rows = []
        for split in ("train", "validation"):
            for label in LABELS:
                for sess in ("d1_session01", "d2_session01"):
                    sid = f"{split}_{label}_{sess}"
                    source_index[sid] = len(rows)
                    source_meta.append(SourceMeta(sid, sess, split, label))
                    rows.append(sid)
        X = np.arange(len(rows) * len(cells) * 2, dtype=np.float32).reshape(len(rows), len(cells), 2)
        M = np.ones((len(rows), len(cells)), dtype=bool)
        pseudo, manifest = assemble_pseudo(X, M, source_index, source_meta, cells, "train", "present", 2, 0)
        self.assertEqual(pseudo.shape, (2, 3, 2))
        by_row = collections.defaultdict(list)
        for row in manifest:
            by_row[row["pseudo_row"]].append(row)
        for entries in by_row.values():
            self.assertEqual({e["session_id"] for e in entries}, {"d1_session01", "d2_session01"})
            for entry in entries:
                self.assertTrue(entry["source_trial_id"].startswith("train_present_"))


if __name__ == "__main__":
    unittest.main()
