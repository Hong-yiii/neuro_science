from __future__ import annotations

import unittest

from scripts.place195_split_and_behavior_audit import (  # type: ignore[reportMissingImports]
    SPLIT_VERSION,
    assign_blocks,
    assign_splits_to_trials,
    behavior_support_by_marker_pair,
    merge_trial_split,
    trial_behavior_row,
)


def trial(index: int, session: str = "s1") -> dict[str, str]:
    return {
        "session_id": session,
        "source_trial_id": f"{session}_trial{index:03d}",
        "trial_index": str(index),
        "previous_source_trial_id": ""
        if index == 1
        else f"{session}_trial{index - 1:03d}",
        "ripple_codes": "11 21 31",
        "unity_codes": "11 21 31",
        "eyelink_codes": "11 21 31",
        "marker_minor_digit": "1",
        "outcome": "success",
        "qc_flags": "",
    }


class Place195SplitAuditTest(unittest.TestCase):
    def test_block_assignment_contains_every_split(self) -> None:
        split_by_block = assign_blocks("s1", 20, 0.70, 0.15, 0.15)
        self.assertEqual(set(split_by_block), set(range(20)))
        self.assertEqual(list(split_by_block.values()).count("train"), 14)
        self.assertEqual(list(split_by_block.values()).count("validation"), 3)
        self.assertEqual(list(split_by_block.values()).count("test"), 3)

    def test_source_trials_in_one_contiguous_block_share_split(self) -> None:
        rows = [trial(index) for index in range(1, 61)]
        assignments = assign_splits_to_trials(rows, 20, 0.70, 0.15, 0.15)
        first_block_splits = {
            row["split"]
            for row in assignments
            if row["split_block_id"] == "s1_block001"
        }
        second_block_splits = {
            row["split"]
            for row in assignments
            if row["split_block_id"] == "s1_block002"
        }
        self.assertEqual(len(first_block_splits), 1)
        self.assertEqual(len(second_block_splits), 1)
        self.assertTrue(
            all(row["split_version"] == SPLIT_VERSION for row in assignments)
        )

    def test_behavior_row_blanks_previous_marker_from_locked_test(self) -> None:
        row = trial(2)
        row["inferred_start_id_from_previous_marker"] = "marker_6"
        split_by_source = {
            "s1_trial001": {"source_trial_id": "s1_trial001", "split": "test"},
            "s1_trial002": {"source_trial_id": "s1_trial002", "split": "validation"},
        }
        merged = merge_trial_split(row, split_by_source["s1_trial002"], split_by_source)
        behavior_row = trial_behavior_row(merged)
        self.assertEqual(behavior_row["previous_source_split"], "test")
        self.assertEqual(behavior_row["previous_source_in_design_split"], "false")
        self.assertEqual(behavior_row["inferred_start_marker"], "")

    def test_behavior_row_keeps_previous_marker_from_design_split(self) -> None:
        row = trial(2)
        row["inferred_start_id_from_previous_marker"] = "marker_6"
        split_by_source = {
            "s1_trial001": {"source_trial_id": "s1_trial001", "split": "train"},
            "s1_trial002": {"source_trial_id": "s1_trial002", "split": "validation"},
        }
        merged = merge_trial_split(row, split_by_source["s1_trial002"], split_by_source)
        behavior_row = trial_behavior_row(merged)
        self.assertEqual(behavior_row["previous_source_split"], "train")
        self.assertEqual(behavior_row["previous_source_in_design_split"], "true")
        self.assertEqual(behavior_row["inferred_start_marker"], "marker_6")

    def test_behavior_support_labels_inferred_marker_pair(self) -> None:
        rows = [
            {
                "split": "train",
                "inferred_start_marker": "marker_1",
                "marker_minor_digit": "2",
                "outcome": "success",
                "session_id": "s1",
                "qc_flags": "",
                "unity_nav_duration_s": "2.0",
                "unity_path_distance_axis_units": "4.0",
                "unity_path_rows_inclusive": "10",
            },
            {
                "split": "train",
                "inferred_start_marker": "marker_1",
                "marker_minor_digit": "2",
                "outcome": "success",
                "session_id": "s2",
                "qc_flags": "clock_flag",
                "unity_nav_duration_s": "4.0",
                "unity_path_distance_axis_units": "8.0",
                "unity_path_rows_inclusive": "20",
            },
        ]
        [support] = behavior_support_by_marker_pair(rows)
        self.assertEqual(support["trials"], 2)
        self.assertEqual(support["sessions"], 2)
        self.assertEqual(support["qc_flagged"], 1)
        self.assertEqual(support["median_unity_path_distance_axis_units"], 6.0)


if __name__ == "__main__":
    unittest.main()
