from __future__ import annotations

import unittest

import numpy as np

from docs.cebra_pilot.implementation.paths import clean_path
from scripts.place195_graph_path_baseline import (  # type: ignore[reportMissingImports]
    DEFAULT_GEOMETRY,
    ROUTE_OTHER,
    SCRIPT_PRIMARY_GRAPH_HASH,
    apply_route_family,
    build_condition_pseudopopulation,
    build_graph,
    coarse5_signature,
    map_position_to_node,
    masked_nearest_centroid_predictions,
    supportable_signatures,
    train_fit_masked_zscore,
)


class Place195GraphPathBaselineTest(unittest.TestCase):
    def test_builds_pinned_fine_graph(self) -> None:
        graph = build_graph(DEFAULT_GEOMETRY)
        self.assertEqual(len(graph.centroids), 1344)
        self.assertEqual(graph.undirected_edge_count, 2544)
        self.assertEqual(len(graph.directed_edges), 5088)
        self.assertEqual(graph.connected_components, 1)
        self.assertEqual(graph.primary_graph_hash, SCRIPT_PRIMARY_GRAPH_HASH)

    def test_maps_exact_centroid_and_rejects_far_coordinate(self) -> None:
        graph = build_graph(DEFAULT_GEOMETRY)
        self.assertEqual(map_position_to_node(-11.5625, -9.6875, graph), 1)
        self.assertEqual(map_position_to_node(100.0, 100.0, graph), 0)

    def test_coarse_signature_keeps_gap_separator(self) -> None:
        graph = build_graph(DEFAULT_GEOMETRY)
        path = clean_path((1, 1, 2, 0, 3), graph.graph)
        self.assertEqual(coarse5_signature(path, graph), "c11|c11")

    def test_supportable_signatures_collapse_unsupported_to_other(self) -> None:
        rows = [
            {
                "session_id": "s1",
                "start": "1",
                "goal": "2",
                "split": "train",
                "coarse5_signature": "a",
            },
            {
                "session_id": "s2",
                "start": "1",
                "goal": "2",
                "split": "train",
                "coarse5_signature": "a",
            },
            {
                "session_id": "s1",
                "start": "1",
                "goal": "2",
                "split": "validation",
                "coarse5_signature": "a",
            },
            {
                "session_id": "s1",
                "start": "1",
                "goal": "2",
                "split": "train",
                "coarse5_signature": "b",
            },
            {
                "session_id": "s1",
                "start": "1",
                "goal": "2",
                "split": "validation",
                "coarse5_signature": "b",
            },
        ]
        supported = supportable_signatures(rows, min_train=2, min_validation=1)
        labelled = apply_route_family(rows, supported)
        self.assertEqual(labelled[0]["route_family"], "a")
        self.assertEqual(labelled[-1]["route_family"], ROUTE_OTHER)

    def test_condition_pseudopopulation_keeps_missing_cells_masked(self) -> None:
        rows = [
            {
                "session_id": "s1",
                "source_trial_id": "s1_t1",
                "split": "train",
                "trial_index": "1",
                "start": "1",
                "goal": "2",
                "route_family": "a",
                "target_label": "1->2|a",
            },
            {
                "session_id": "s2",
                "source_trial_id": "s2_t1",
                "split": "train",
                "trial_index": "1",
                "start": "1",
                "goal": "2",
                "route_family": "a",
                "target_label": "1->2|a",
            },
        ]
        units = ["u1", "u2", "u3"]
        units_by_session = {"s1": {"u1", "u2"}, "s2": {"u3"}, "s3": set()}
        counts = {("s1_t1", "u1"): 1.0, ("s1_t1", "u2"): 2.0, ("s2_t1", "u3"): 3.0}
        pseudo = build_condition_pseudopopulation(rows, units, units_by_session, counts)
        self.assertEqual(len(pseudo.rows), 1)
        self.assertEqual(pseudo.rows[0]["observed_cells"], 3)
        self.assertEqual(pseudo.rows[0]["component_sessions"], 2)
        self.assertEqual(pseudo.rows[0]["missing_sessions"], 1)
        np.testing.assert_array_equal(pseudo.observed[0], np.array([True, True, True]))

    def test_train_fit_masked_zscore_does_not_impute_missing(self) -> None:
        x = np.array([[1.0, np.nan], [3.0, 10.0], [np.nan, 20.0]])
        observed = np.isfinite(x)
        z, coverage = train_fit_masked_zscore(
            x, observed, ["train", "train", "validation"]
        )
        self.assertTrue(np.isnan(z[0, 1]))
        self.assertTrue(np.isnan(z[2, 0]))
        self.assertEqual(coverage["observed_entries"], 4)
        self.assertEqual(coverage["missing_entries"], 2)
        self.assertEqual(
            coverage["imputation_policy"],
            "none; missing cells stay masked and distances use overlap only",
        )

    def test_masked_nearest_centroid_predicts_only_within_start_goal(self) -> None:
        rows = [
            {"split": "train", "start": "1", "goal": "2", "target_label": "1->2|left"},
            {"split": "train", "start": "1", "goal": "2", "target_label": "1->2|right"},
            {"split": "train", "start": "3", "goal": "4", "target_label": "3->4|left"},
            {
                "split": "validation",
                "start": "1",
                "goal": "2",
                "target_label": "1->2|right",
            },
        ]
        z = np.array([[0.0, 0.0], [10.0, 0.0], [10.0, 0.0], [9.0, 0.0]])
        observed = np.ones_like(z, dtype=bool)
        predictions, overlaps, supported = masked_nearest_centroid_predictions(
            z, observed, rows, min_overlap=1
        )
        self.assertEqual(predictions[-1], "1->2|right")
        self.assertEqual(overlaps[-1], 2)
        self.assertTrue(supported[-1])


if __name__ == "__main__":
    unittest.main()
