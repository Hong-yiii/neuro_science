"""Invented saved-metric tests; never fit models."""

import tempfile
import unittest
from pathlib import Path

import numpy as np

from scripts.render_cebra_endpoint_report import (
    Report,
    index_metrics,
    matrix,
    read_metric_rows,
    tail_fraction,
    values,
)


class ReportRegression(unittest.TestCase):
    def test_inclusive_plus_one_tail_keeps_ties(self):
        self.assertEqual(tail_fraction(1.0, [0.0, 1.0, 2.0]), 0.75)
        self.assertEqual(tail_fraction(3.0, [0.0] * 20), 1 / 21)

    def test_seed_axis_is_not_pooled(self):
        index = {
            ("observed", seed, "goal6", "raw", "wholecue", "development"): {
                "balanced_accuracy": seed / 10
            }
            for seed in range(3)
        }
        np.testing.assert_array_equal(
            values(index, "goal6", "raw", "balanced_accuracy", ["wholecue"]),
            np.array([[0], [0.1], [0.2]]),
        )

    def test_confusion_counts_and_row_normalization(self):
        rows = [
            {
                "true": i,
                "pred": j,
                "count": 40 if i == j else 0,
                "row_normalized_recall": 1.0 if i == j else 0.0,
                "target": "start6",
                "representation": "raw",
                "window": "wholecue",
                "split": "development",
            }
            for i in range(1, 7)
            for j in range(1, 7)
        ]
        counts, normalized, classes = matrix(rows, "start6", "raw")
        np.testing.assert_array_equal(counts, np.eye(6) * 40)
        np.testing.assert_array_equal(normalized, np.eye(6))
        self.assertEqual(classes, list(range(1, 7)))
        rows[0]["row_normalized_recall"] = 0.5
        with self.assertRaises(AssertionError):
            matrix(rows, "start6", "raw")

    def test_rejects_duplicate_or_incomplete_metrics(self):
        row = {
            "world": "observed",
            "seed": 0,
            "target": "start6",
            "representation": "raw",
            "window": "wholecue",
            "split": "development",
        }
        with self.assertRaisesRegex(ValueError, "duplicate"):
            index_metrics([row, row])
        with self.assertRaisesRegex(ValueError, "incomplete"):
            index_metrics([row])

    def test_rejects_bad_json_and_unverified_report(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            bad = root / "metrics.jsonl"
            bad.write_text("{not json}\n")
            with self.assertRaisesRegex(RuntimeError, "Invalid metric JSON"):
                read_metric_rows(bad)
            receipt = root / "receipt.json"
            receipt.write_text('{"status":"failed"}')
            with self.assertRaisesRegex(ValueError, "before successful"):
                Report(root, receipt, root / "report")
            self.assertFalse((root / "report").exists())


if __name__ == "__main__":
    unittest.main()
