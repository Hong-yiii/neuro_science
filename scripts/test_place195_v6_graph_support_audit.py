from __future__ import annotations

import unittest

from scripts.place195_v6_graph_support_audit import (
    DEFAULT_GEOMETRY,
    ComponentTrial,
    SelectedCohort,
    build_regions,
    component_support,
    fine_graph_facts,
    infer_direction,
    map_sample,
    required_panel_summary,
    selected_direction_sensitivity,
)


class Place195V6GraphSupportAuditTest(unittest.TestCase):
    def test_hash_reconciliation_keeps_legacy_and_current_contracts_distinct(self) -> None:
        facts = fine_graph_facts(DEFAULT_GEOMETRY)
        self.assertTrue(facts["legacy_bare_int_numeric_sorted_edge_hash_matches_expected"])
        self.assertTrue(facts["current_typed_mazegraph_edge_only_hash_matches_expected"])
        self.assertNotEqual(
            facts["legacy_bare_int_numeric_sorted_edge_hash_computed"],
            facts["current_typed_mazegraph_edge_only_hash_computed"],
        )

    def test_static_four_pillar_regions_and_mapping(self) -> None:
        regions, _corridors, components = build_regions()
        self.assertEqual(len(regions), 21)
        self.assertEqual(len(components), 24)
        self.assertEqual(
            map_sample(
                {"navigation_sample": "0", "position_axis1": "-10", "position_axis2": "-10"},
                regions,
            ).region_id,
            "N_L_B",
        )
        corridor = map_sample(
            {"navigation_sample": "1", "position_axis1": "-5", "position_axis2": "-10"},
            regions,
        )
        self.assertEqual(corridor.region_id, "E_H_B_L_C")
        self.assertEqual(corridor.progress, 0.5)
        self.assertEqual(
            map_sample(
                {"navigation_sample": "2", "position_axis1": "-5", "position_axis2": "-5"},
                regions,
            ).unknown_reason,
            "pillar_macro_cell",
        )

    def test_unknown_component_trial_is_not_absent(self) -> None:
        _regions, _corridors, components = build_regions()
        support_rows, _candidate_rows, _route_rows, _selected = component_support(
            [
                ComponentTrial(
                    source_trial_id="s_t1",
                    session_id="s",
                    split="train",
                    endpoint_pair="1->2",
                    complete=False,
                    middle_components=frozenset(),
                    motifs=frozenset(),
                    route_signature="__incomplete_or_unknown__",
                )
            ],
            components[:1],
        )
        self.assertEqual({row["component_status"] for row in support_rows}, {"unknown"})
        self.assertEqual(support_rows[0]["unknown_not_absent_policy"], "true")

    def test_direction_inference_reports_evidence_source(self) -> None:
        regions, _corridors, _components = build_regions()
        region = regions["E_H_B_L_C"]
        directed, direction, source = infer_direction(
            region, "N_L_B", "N_C_B", [0.1, 0.9]
        )
        self.assertEqual((directed, direction, source), ("D_N_L_B__N_C_B", "forward", "adjacent_nodes"))
        directed, direction, source = infer_direction(region, "", "", [0.1, 0.9])
        self.assertEqual((directed, direction, source), ("D_N_L_B__N_C_B", "forward", "progress"))
        directed, direction, source = infer_direction(region, "N_L_B", "", [0.5])
        self.assertEqual((directed, direction, source), ("D_N_L_B__N_C_B", "forward", "one_adjacent_node"))

    def test_selects_behavior_supported_directed_middle_component(self) -> None:
        _regions, _corridors, components = build_regions()
        component = components[0]["component_id"]
        trials = _supported_trials(component, direction_source="adjacent_nodes")
        _support_rows, _candidate_rows, _route_rows, selected = component_support(trials, components[:1])
        self.assertEqual(selected.component_id, component)
        self.assertEqual(selected.status, "strict_viable_behavior_support")

    def test_strict_direction_sensitivity_flags_one_adjacent_dependence(self) -> None:
        selected = SelectedCohort(
            "D_N_L_B__N_C_B",
            "directed_middle_corridor",
            "1->2",
            "strict_viable_behavior_support",
            "fixture",
        )
        trials = _supported_trials(selected.component_id, direction_source="one_adjacent_node")
        summary = selected_direction_sensitivity(trials, selected)
        self.assertEqual(summary["one_adjacent_node_only_source_trial_count"], 11)
        self.assertEqual(summary["strict_direction_sensitivity_gate_status"], "failed")

    def test_required_panel_summary_fails_missing_validation_absent(self) -> None:
        selected = SelectedCohort(
            "D_N_L_B__N_C_B",
            "directed_middle_corridor",
            "1->2",
            "strict_viable_behavior_support",
            "fixture",
        )
        condition_sources = {
            ("train", "present"): {"tp"},
            ("train", "absent"): {"ta"},
            ("validation", "present"): {"vp"},
        }
        condition_sessions = {key: {"s"} for key in condition_sources}
        panel_sets = {
            "train|present": {"c1"},
            "train|absent": {"c1"},
            "validation|present": {"c1"},
        }
        summary = required_panel_summary(condition_sources, condition_sessions, panel_sets, selected)
        self.assertEqual(summary["condition_panel_gate_status"], "failed")
        self.assertEqual(summary["missing_required_conditions"], ["validation|absent"])


def _supported_trials(component: str, direction_source: str) -> list[ComponentTrial]:
    trials: list[ComponentTrial] = []
    for split, n_present, n_absent in (("train", 8, 8), ("validation", 3, 3)):
        for idx in range(n_present):
            trials.append(
                ComponentTrial(
                    f"{split}_p{idx}",
                    "s",
                    split,
                    "1->2",
                    True,
                    frozenset({component}),
                    frozenset(),
                    component,
                    ((component, direction_source),),
                )
            )
        for idx in range(n_absent):
            trials.append(
                ComponentTrial(
                    f"{split}_a{idx}",
                    "s",
                    split,
                    "1->2",
                    True,
                    frozenset(),
                    frozenset(),
                    "other",
                )
            )
    return trials


if __name__ == "__main__":
    unittest.main()
