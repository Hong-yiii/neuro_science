from __future__ import annotations

import csv
import gzip
import json
import tempfile
import unittest
from pathlib import Path

from scripts.place195_split_filtered_access import SplitAccessError, SplitFilteredAccess


class SplitFilteredAccessTest(unittest.TestCase):
    def test_sentinel_test_values_do_not_reach_downstream_aggregates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            import_dir, split_dir = _fixture(root)
            access = SplitFilteredAccess(import_dir, split_dir)

            trial_goals = [row["marker_minor_digit"] for row in access.iter_trials()]
            path_sum = sum(
                float(row["position_axis1"]) for row in access.iter_path_samples()
            )
            cue_sum = sum(
                float(row["cue_spike_count"]) for row in access.iter_cue_counts()
            )
            event_sum = sum(
                float(row["cue_relative_time_s"])
                for row in access.iter_cue_spike_events()
            )

            self.assertEqual(trial_goals, ["1", "2"])
            self.assertEqual(path_sum, 3.0)
            self.assertEqual(cue_sum, 7.0)
            self.assertAlmostEqual(event_sum, 0.3)
            audit = access.audit.as_dict()
            self.assertEqual(audit["forbidden_rows_yielded"], 0)
            self.assertEqual(audit["rows_skipped_by_split"]["cue_counts"]["test"], 1)

    def test_missing_split_mapping_fails_before_yield(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            import_dir, split_dir = _fixture(root, include_unmapped_trial=True)
            access = SplitFilteredAccess(import_dir, split_dir)
            with self.assertRaisesRegex(SplitAccessError, "no split mapping"):
                list(access.iter_trials())

    def test_test_split_cannot_be_allowed_for_development_access(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            import_dir, split_dir = _fixture(root)
            with self.assertRaisesRegex(SplitAccessError, "forbids"):
                SplitFilteredAccess(import_dir, split_dir, allowed_splits={"test"})


def _fixture(root: Path, include_unmapped_trial: bool = False) -> tuple[Path, Path]:
    import_dir = root / "import"
    split_dir = root / "splits"
    import_dir.mkdir()
    split_dir.mkdir()
    _write_csv(
        split_dir / "source_trial_splits.csv",
        [
            {"source_trial_id": "train_trial", "split": "train"},
            {"source_trial_id": "validation_trial", "split": "validation"},
            {"source_trial_id": "test_trial", "split": "test"},
        ],
        ("source_trial_id", "split"),
    )
    (split_dir / "split_summary.json").write_text(
        json.dumps({"split_hash": "fixture"}), encoding="utf-8"
    )
    trial_rows = [
        {
            "session_id": "s1",
            "source_trial_id": "train_trial",
            "trial_index": "1",
            "marker_minor_digit": "1",
        },
        {
            "session_id": "s1",
            "source_trial_id": "validation_trial",
            "trial_index": "2",
            "marker_minor_digit": "2",
        },
        {
            "session_id": "s1",
            "source_trial_id": "test_trial",
            "trial_index": "3",
            "marker_minor_digit": "TEST_SENTINEL",
        },
    ]
    if include_unmapped_trial:
        trial_rows.append(
            {
                "session_id": "s1",
                "source_trial_id": "missing_trial",
                "trial_index": "4",
                "marker_minor_digit": "999",
            }
        )
    _write_csv(
        import_dir / "trials.csv",
        trial_rows,
        ("session_id", "source_trial_id", "trial_index", "marker_minor_digit"),
    )
    _write_gzip_csv(
        import_dir / "path_samples.csv.gz",
        [
            {"source_trial_id": "train_trial", "position_axis1": "1"},
            {"source_trial_id": "validation_trial", "position_axis1": "2"},
            {"source_trial_id": "test_trial", "position_axis1": "999999"},
        ],
        ("source_trial_id", "position_axis1"),
    )
    _write_gzip_csv(
        import_dir / "cue_counts.csv.gz",
        [
            {"source_trial_id": "train_trial", "cell_id": "c1", "cue_spike_count": "3"},
            {
                "source_trial_id": "validation_trial",
                "cell_id": "c1",
                "cue_spike_count": "4",
            },
            {
                "source_trial_id": "test_trial",
                "cell_id": "c1",
                "cue_spike_count": "777",
            },
        ],
        ("source_trial_id", "cell_id", "cue_spike_count"),
    )
    _write_gzip_csv(
        import_dir / "cue_spike_events.csv.gz",
        [
            {"source_trial_id": "train_trial", "cue_relative_time_s": "0.1"},
            {"source_trial_id": "validation_trial", "cue_relative_time_s": "0.2"},
            {"source_trial_id": "test_trial", "cue_relative_time_s": "999"},
        ],
        ("source_trial_id", "cue_relative_time_s"),
    )
    return import_dir, split_dir


def _write_csv(
    path: Path, rows: list[dict[str, str]], fieldnames: tuple[str, ...]
) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _write_gzip_csv(
    path: Path, rows: list[dict[str, str]], fieldnames: tuple[str, ...]
) -> None:
    with gzip.open(path, "wt", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    unittest.main()
