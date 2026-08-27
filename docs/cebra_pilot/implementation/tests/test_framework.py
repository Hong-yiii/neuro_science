from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from typing import TypedDict
from unittest.mock import patch

import numpy as np

from docs.cebra_pilot.implementation.contracts import CueNavigationTrial, MazeGraph
from docs.cebra_pilot.implementation.manifest import (
    build_manifest,
    require_pilot_output_path,
    write_run_manifest,
)
from docs.cebra_pilot.implementation.neural import summarize_cue_activity
from docs.cebra_pilot.implementation.paths import (
    clean_path,
    directed_edge_set,
    edge_jaccard,
    longest_shared_contiguous_directed_segment,
)
from docs.cebra_pilot.implementation.preflight import (
    SOFTWARE_SMOKE_ONLY,
    select_one_cell_smoke_trial,
    summarize_one_cell_jld2_files,
)
from docs.cebra_pilot.implementation.splits import freeze_splits


class ScientificTrialFields(TypedDict):
    source_trial_id: str
    session_id: str
    simultaneous_recording_group: str
    previous_trial_id: str | None
    trial_index: int
    previous_goal_id: str | None
    previous_success: bool | None
    previous_metadata_missing_reason: str | None
    current_success: bool
    timeout: bool
    inclusion_reason: str
    cue_id: str
    start_id: str
    goal_id: str
    cue_onset: float
    cue_offset: float
    navigation_onset: float
    navigation_end: float
    unit_ids: tuple[str, ...]
    cue_counts_by_bin_unit: np.ndarray
    cue_valid_mask: np.ndarray
    cue_exposure_seconds: np.ndarray
    observed_path_nodes: tuple[str, ...]


def valid_scientific_trial_fields() -> ScientificTrialFields:
    return {
        "source_trial_id": "trial-1",
        "session_id": "session-1",
        "simultaneous_recording_group": "group-1",
        "previous_trial_id": "trial-0",
        "trial_index": 1,
        "previous_goal_id": "start-A",
        "previous_success": True,
        "previous_metadata_missing_reason": None,
        "current_success": True,
        "timeout": False,
        "inclusion_reason": "synthetic contract-boundary test",
        "cue_id": "cue-A",
        "start_id": "start-A",
        "goal_id": "goal-B",
        "cue_onset": 0.0,
        "cue_offset": 1.0,
        "navigation_onset": 1.0,
        "navigation_end": 3.0,
        "unit_ids": ("unit-1", "unit-2"),
        "cue_counts_by_bin_unit": np.array([[1, 0], [0, 1]], dtype=np.int64),
        "cue_valid_mask": np.array([True, True]),
        "cue_exposure_seconds": np.array([0.02, 0.02]),
        "observed_path_nodes": ("A", "B"),
    }


class NeuralSummaryTests(unittest.TestCase):
    def test_axis_mask_exposure_and_unit_order_are_fixed(self) -> None:
        summary = summarize_cue_activity(
            np.array([[1, 2], [10, 20], [3, 4]], dtype=np.int64),
            np.array([True, False, True]),
            np.array([0.02, 0.50, 0.03]),
            ("u-left", "u-right"),
        )

        self.assertEqual(summary.unit_ids, ("u-left", "u-right"))
        np.testing.assert_array_equal(summary.counts_by_unit, np.array([4, 6]))
        np.testing.assert_allclose(summary.rates_hz_by_unit, np.array([80.0, 120.0]))
        self.assertEqual(summary.valid_bin_count, 2)

        with self.assertRaisesRegex(ValueError, "second axis"):
            summarize_cue_activity(
                np.array([[1, 2, 3], [4, 5, 6]], dtype=np.int64),
                np.array([True, True]),
                np.array([0.02, 0.02]),
                ("u-left", "u-right"),
            )
        with self.assertRaisesRegex(ValueError, "positive finite exposure"):
            summarize_cue_activity(
                np.array([[1, 2], [3, 4]], dtype=np.int64),
                np.array([True, False]),
                np.array([0.0, 0.02]),
                ("u-left", "u-right"),
            )
        with self.assertRaisesRegex(ValueError, "at least one valid cue bin"):
            summarize_cue_activity(
                np.array([[1, 2]], dtype=np.int64),
                np.array([False]),
                np.array([0.02]),
                ("u-left", "u-right"),
            )


class PathRuleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.graph = MazeGraph(
            (("A", "B"), ("B", "C"), ("C", "D"), ("B", "E"), ("E", "D"))
        )

    def test_invalid_and_nonadjacent_gaps_split_without_bridge_edges(self) -> None:
        path = clean_path(("A", "A", "B", 0, "C", "D", "A", "B"), self.graph)

        self.assertEqual(
            path.raw_valid_segments, (("A", "A", "B"), ("C", "D"), ("A", "B"))
        )
        self.assertEqual(
            path.route_shape_segments, (("A", "B"), ("C", "D"), ("A", "B"))
        )
        self.assertEqual(path.audit.repeated_sample_count, 1)
        self.assertEqual(path.audit.invalid_gap_count, 1)
        self.assertEqual(path.audit.nonadjacent_transition_count, 1)
        self.assertNotIn(("B", "C"), directed_edge_set(path))
        self.assertIn(("C", "D"), directed_edge_set(path))

    def test_empty_edge_jaccard_and_shared_segment_rules(self) -> None:
        one_node_left = clean_path(("A",), self.graph)
        one_node_right = clean_path(("B",), self.graph)
        self.assertIsNone(edge_jaccard(one_node_left, one_node_right))

        left = clean_path(("A", "B", None, "C", "D"), self.graph)
        right = clean_path(("A", "B", "C", "D"), self.graph)
        shared = longest_shared_contiguous_directed_segment(left, right)
        self.assertEqual(shared.length, 1)
        self.assertEqual(shared.edges, (("A", "B"),))
        self.assertEqual(shared.classification, "initial")

        complete = longest_shared_contiguous_directed_segment(right, right)
        self.assertEqual(complete.classification, "complete")

        obscured = clean_path((0, "A", "B", "C"), self.graph)
        shared_obscured = longest_shared_contiguous_directed_segment(obscured, right)
        self.assertEqual(shared_obscured.classification, "unavailable")
        self.assertIn(
            "initial endpoint obscured", shared_obscured.unavailable_reason or ""
        )


class SplitTests(unittest.TestCase):
    def test_derivatives_share_split_and_hash_is_stable(self) -> None:
        common = {
            "session_id": "session-1",
            "simultaneous_recording_group": "group-1",
        }
        assignments = [
            {
                "sample_id": "trial-2",
                "source_trial_id": "trial-2",
                "split": "validation",
                **common,
            },
            {
                "sample_id": "trial-1-a",
                "source_trial_id": "trial-1",
                "split": "train",
                **common,
            },
            {
                "sample_id": "trial-1-b",
                "source_trial_id": "trial-1",
                "split": "train",
                **common,
            },
            {
                "sample_id": "trial-3",
                "source_trial_id": "trial-3",
                "split": "test",
                **common,
            },
        ]
        expected = ("trial-1", "trial-2", "trial-3")
        frozen = freeze_splits(assignments, expected)
        frozen_again = freeze_splits(reversed(assignments), expected)

        self.assertEqual(frozen.sha256, frozen_again.sha256)
        self.assertEqual(frozen.source_trial_splits["trial-1"], "train")
        self.assertEqual(
            frozen.recording_group_split_counts,
            {"group-1": {"test": 1, "train": 1, "validation": 1}},
        )

        with self.assertRaisesRegex(ValueError, "derivatives"):
            freeze_splits(
                [
                    {
                        "sample_id": "a",
                        "source_trial_id": "trial-1",
                        "split": "train",
                        **common,
                    },
                    {
                        "sample_id": "b",
                        "source_trial_id": "trial-1",
                        "split": "test",
                        **common,
                    },
                ],
                ("trial-1",),
            )
        with self.assertRaisesRegex(ValueError, "coverage mismatch"):
            freeze_splits(assignments[:-1], expected)


class ManifestTests(unittest.TestCase):
    def test_run_manifest_refuses_existing_output_directory(self) -> None:
        manifest = build_manifest(
            stage="unit_test",
            status="passed",
            scientific_status=SOFTWARE_SMOKE_ONLY,
            stop_conditions=("test only",),
            package_names=(),
        )
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "run"
            with patch(
                "docs.cebra_pilot.implementation.manifest.require_pilot_output_path",
                return_value=out,
            ):
                write_run_manifest(out, manifest)
                with self.assertRaises(FileExistsError):
                    write_run_manifest(out, manifest)

    def test_preflight_outputs_are_restricted_to_pilot_runs(self) -> None:
        accepted = require_pilot_output_path("outputs/cebra_pilot/test-boundary-only")
        self.assertTrue(
            str(accepted).endswith("outputs/cebra_pilot/test-boundary-only")
        )
        with self.assertRaisesRegex(ValueError, "must be below"):
            require_pilot_output_path("data/preflight-would-be-wrong")


class CurrentExportBoundaryTests(unittest.TestCase):
    def test_local_training_selector_enforces_alignment_and_variation(self) -> None:
        def fake_reader(_path: Path):
            yield 10, np.zeros((64, 1)), np.zeros((64, 1))
            yield 11, np.full(64, "not-a-count", dtype=object), np.arange(64)
            yield 12, np.r_[np.zeros(63), np.nan], np.arange(64)
            yield 13, np.r_[np.zeros(63), -1.0], np.arange(64)
            yield 14, np.zeros(65), np.zeros(64)
            yield 15, np.zeros(63), np.arange(63)
            yield 16, np.zeros(64), np.arange(64)
            yield 17, np.r_[np.zeros(63), 1.0], np.arange(64)

        selected = select_one_cell_smoke_trial(
            Path("fake.jld2"),
            reader=fake_reader,
        )
        self.assertEqual(selected.loader_trial_index, 17)
        self.assertEqual(selected.file_order_index, 7)
        self.assertEqual(selected.input_data.shape, (64, 1))
        self.assertEqual(selected.total_spikes, 1.0)
        self.assertEqual(
            selected.rejection_counts,
            {
                "not_one_dimensional": 1,
                "shape_mismatch": 1,
                "non_numeric_counts": 1,
                "non_finite_counts": 1,
                "negative_counts": 1,
                "too_short": 1,
                "constant_counts": 1,
            },
        )
        with self.assertRaisesRegex(ValueError, "min_samples must be at least 2"):
            select_one_cell_smoke_trial(
                Path("fake.jld2"), min_samples=1, reader=fake_reader
            )

        def no_eligible_reader(_path: Path):
            yield 20, np.zeros(64), np.arange(64)

        with self.assertRaisesRegex(ValueError, "no intact trial"):
            select_one_cell_smoke_trial(
                Path("fake.jld2"),
                reader=no_eligible_reader,
            )

    def test_one_cell_smoke_never_becomes_scientific_contract(self) -> None:
        def fake_reader(_path: Path):
            yield (
                10,
                np.array([1, 0, 2], dtype=np.int64),
                np.array([5, 0, 6], dtype=np.int64),
            )
            yield 11, np.array([], dtype=np.int64), np.array([], dtype=np.int64)

        summary = summarize_one_cell_jld2_files(
            (Path("fake.jld2"),), reader=fake_reader
        )
        self.assertEqual(summary["scientific_status"], SOFTWARE_SMOKE_ONLY)
        self.assertIn("H1 stop", summary["stop_conditions"][0])
        self.assertIn("single-cell navigation samples", summary["contract_boundary"])

        one_cell_fields = valid_scientific_trial_fields()
        one_cell_fields["unit_ids"] = ("one-cell-export",)
        one_cell_fields["cue_counts_by_bin_unit"] = np.array([[1], [0]], dtype=np.int64)
        with self.assertRaisesRegex(ValueError, "at least two simultaneous units"):
            CueNavigationTrial(**one_cell_fields)

    def test_scientific_contract_requires_selection_history(self) -> None:
        valid = valid_scientific_trial_fields()
        trial = CueNavigationTrial(**valid)
        self.assertEqual(trial.trial_index, 1)
        self.assertTrue(trial.current_success)

        incomplete = valid_scientific_trial_fields()
        incomplete["previous_goal_id"] = None
        with self.assertRaisesRegex(ValueError, "all present or all absent"):
            CueNavigationTrial(**incomplete)

        unexplained_absence = valid_scientific_trial_fields()
        unexplained_absence["previous_trial_id"] = None
        unexplained_absence["previous_goal_id"] = None
        unexplained_absence["previous_success"] = None
        with self.assertRaisesRegex(ValueError, "missing_reason is required"):
            CueNavigationTrial(**unexplained_absence)

        audited_absence = unexplained_absence.copy()
        audited_absence["previous_metadata_missing_reason"] = (
            "predecessor unavailable in export"
        )
        self.assertIsNone(CueNavigationTrial(**audited_absence).previous_trial_id)


if __name__ == "__main__":
    unittest.main()
