from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import numpy as np

from scripts.import_place195_sessions import (
    ROOT,
    _event_matrix,
    _eyelink_times_seconds,
    _is_trial_triplet,
    read_selection_keys,
    read_unity_trials,
    spikes_in_window,
    validate_output_dir,
)


class Place195ImporterTest(unittest.TestCase):
    def test_trial_triplets_keep_timeout_rows(self) -> None:
        self.assertTrue(_is_trial_triplet((16, 26, 36)))
        self.assertTrue(_is_trial_triplet((14, 24, 44)))
        self.assertFalse(_is_trial_triplet((16, 26, 35)))

    def test_half_open_cue_spike_window(self) -> None:
        spikes = np.array([0.9, 1.0, 1.5, 2.0, 2.1])
        np.testing.assert_array_equal(
            spikes_in_window(spikes, 1.0, 2.0), np.array([1.0, 1.5])
        )

    def test_event_matrix_orients_three_events_to_columns(self) -> None:
        events_by_trials = np.array([[11, 12], [21, 22], [31, 32]])
        oriented = _event_matrix(events_by_trials, Path("dummy.mat"), "events")
        np.testing.assert_array_equal(oriented, np.array([[11, 21, 31], [12, 22, 32]]))

    def test_eyelink_millisecond_like_trial_times_become_seconds(self) -> None:
        raw_times = np.array([[1000.0, 2025.0, 9000.0]])
        np.testing.assert_allclose(
            _eyelink_times_seconds(raw_times), np.array([[1.0, 2.025, 9.0]])
        )

    def test_selection_list_keys_use_session_cell_suffix(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "cells.txt"
            path.write_text(
                "/Volumes/Hippocampus/Data/picasso-misc/20181105/session01/array02/channel045/cell01\n",
                encoding="utf-8",
            )
            self.assertEqual(
                read_selection_keys(path),
                {"20181105/session01/array02/channel045/cell01"},
            )

    def test_output_dir_rejects_raw_data_location(self) -> None:
        with self.assertRaises(ValueError):
            validate_output_dir(
                ROOT / "data/raw/generated-import",
                ROOT / "data/raw/lab_server/cortex_picasso_misc_place195_20260830",
            )

    def test_unity_parser_retains_startup_marker_but_parses_trials(self) -> None:
        text = "\n".join(
            [
                "Version: test",
                "Trigger: v4",
                " 84 0.01 0 0 0",
                " 11 0.01 0 0 0",
                " 21 1.00 0 0 0",
                " 31 2.00 1 0 0",
                " 12 0.50 1 0 0",
                " 22 1.00 1 0 0",
                " 42 4.00 2 0 0",
            ]
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "session_1_test.txt"
            path.write_text(text, encoding="utf-8")
            events, raw, header = read_unity_trials(path)
        np.testing.assert_array_equal(
            events.codes, np.array([[11, 21, 31], [12, 22, 42]])
        )
        self.assertEqual(events.first_numeric_line, 2)
        self.assertEqual(events.bad_event_count, 0)
        self.assertEqual(raw.shape, (7, 5))
        self.assertEqual(header["Trigger"], "v4")


if __name__ == "__main__":
    unittest.main()
