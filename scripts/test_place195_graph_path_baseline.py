from __future__ import annotations

import unittest

import numpy as np

from docs.cebra_pilot.implementation.paths import clean_path
from scripts.place195_graph_path_baseline import (  # type: ignore[reportMissingImports]
    DEFAULT_GEOMETRY,
    ROUTE_OTHER,
    SCRIPT_PRIMARY_GRAPH_HASH,
    apply_route_family,
    build_graph,
    coarse5_signature,
    map_position_to_node,
    nearest_centroid_predictions,
    supportable_signatures,
    train_fit_impute_zscore,
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
            {"session_id": "s1", "start": "1", "goal": "2", "split": "train", "coarse5_signature": "a"},
            {"session_id": "s2", "start": "1", "goal": "2", "split": "train", "coarse5_signature": "a"},
            {"session_id": "s1", "start": "1", "goal": "2", "split": "validation", "coarse5_signature": "a"},
            {"session_id": "s1", "start": "1", "goal": "2", "split": "train", "coarse5_signature": "b"},
            {"session_id": "s1", "start": "1", "goal": "2", "split": "validation", "coarse5_signature": "b"},
        ]
        supported = supportable_signatures(rows, min_train=2, min_validation=1)
        labelled = apply_route_family(rows, supported)
        self.assertEqual(labelled[0]["route_family"], "a")
        self.assertEqual(labelled[-1]["route_family"], ROUTE_OTHER)

    def test_train_fit_zero_imputes_missing_after_zscore(self) -> None:
        x = np.array([[1.0, np.nan], [3.0, 10.0], [np.nan, 20.0]])
        observed = np.isfinite(x)
        z, burden = train_fit_impute_zscore(x, observed, ["train", "train", "validation"])
        self.assertEqual(z[0, 1], 0.0)
        self.assertEqual(z[2, 0], 0.0)
        self.assertEqual(burden["observed_entries"], 4)
        self.assertEqual(burden["imputed_entries"], 2)

    def test_nearest_centroid_predicts_only_within_start_goal(self) -> None:
        rows = [
            {"split": "train", "start": "1", "goal": "2", "target_label": "1->2|left"},
            {"split": "train", "start": "1", "goal": "2", "target_label": "1->2|right"},
            {"split": "train", "start": "3", "goal": "4", "target_label": "3->4|left"},
            {"split": "validation", "start": "1", "goal": "2", "target_label": "1->2|right"},
        ]
        x = np.array([[0.0, 0.0], [10.0, 0.0], [10.0, 0.0], [9.0, 0.0]])
        predictions = nearest_centroid_predictions(x, rows)
        self.assertEqual(predictions[-1], "1->2|right")


if __name__ == "__main__":
    unittest.main()
