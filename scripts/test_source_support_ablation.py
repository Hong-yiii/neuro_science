"""Invented-only regression checks for the bounded source-support experiment."""

import copy
import tempfile
import unittest
from collections import Counter
from dataclasses import replace
from pathlib import Path

import numpy as np

from neuro.notebook_artifacts import no_fitting
from neuro.notebook_inputs import (
    demo_configuration,
    effective_pair_map,
    inspect_inputs,
    load_inputs,
)
from neuro.place195 import panel_policy, reconstruct_neural, select_metadata
from neuro.pseudopopulation import materialize, sample_plan
from neuro.studies.source_support_ablation import (
    allocation_plan,
    project_plan,
    restrict_data,
    three_sources,
)
from scripts.test_fresh_notebooks import invented_ledgers


class PanelTests(unittest.TestCase):
    def test_restriction_keeps_original_split_and_global_embargo(self):
        with tempfile.TemporaryDirectory() as td, no_fitting():
            manifest, _, _ = invented_ledgers(Path(td))
            original = select_metadata(manifest)
            panel = copy.deepcopy(manifest)
            panel["analysis_panel"] = {
                "conditions": ["1->2", "1->3"],
                "minimum_train_sources": 3,
                "minimum_development_sources": 1,
            }
            selected = select_metadata(panel)
            self.assertEqual(original.eligible, selected.eligible)
            self.assertEqual(
                original.audit["development_contributor_union"],
                selected.audit["development_contributor_union"],
            )
            expected = tuple(
                s for s in original.selected if s["condition"] in {"1->2", "1->3"}
            )
            self.assertEqual(selected.selected, expected)
            data, _ = reconstruct_neural(selected, interpret_neural=True)
            self.assertEqual(
                dict(data.target_definition.condition_to_target),
                {"1->2": "1->2", "1->3": "1->3"},
            )
            self.assertEqual(data.dependency_audit()["overlapping_contributor_ids"], [])

    def test_bad_conditions_and_implicit_singletons_rejected(self):
        base = {"landmarks": [1, 2, 3]}
        for conditions in (["1->1"], ["1->2", "1->2"], [], ["1->7"]):
            with self.assertRaises(ValueError):
                panel_policy(
                    {
                        **base,
                        "analysis_panel": {
                            "conditions": conditions,
                            "minimum_train_sources": 2,
                            "minimum_development_sources": 1,
                        },
                    }
                )
        with self.assertRaises(ValueError):
            panel_policy(
                {
                    **base,
                    "analysis_panel": {
                        "conditions": ["1->2"],
                        "minimum_train_sources": 1,
                        "minimum_development_sources": 1,
                    },
                }
            )


class SamplingTests(unittest.TestCase):
    def setUp(self):
        self.data, _ = load_inputs(inspect_inputs(demo_configuration()))
        self.mapping = effective_pair_map(self.data, permutation_seed=None)

    def test_projection_preserves_blocks_values_and_rebinds_identity(self):
        wide = self.data
        small = restrict_data(wide, unit_ids=[u.unit_id for u in wide.units[::3]])
        plan = sample_plan(wide, split_id="train", rows_per_condition=8, seed=7)
        projected = project_plan(plan, wide, small, self.mapping)
        self.assertNotEqual(plan.split_identity, projected.split_identity)
        a, b = materialize(wide, plan), materialize(small, projected)
        np.testing.assert_array_equal(a.values[:, ::3], b.values)
        np.testing.assert_array_equal(a.targets, b.targets)
        # Removing a complete block requires filtering that source position too.
        block = wide.block_ids[0]
        single = restrict_data(
            wide, unit_ids=[u.unit_id for u in wide.units if u.block_id == block]
        )
        p = project_plan(plan, wide, single, self.mapping)
        self.assertTrue(all(len(r.source_ids) == 1 for r in p.rows))
        np.testing.assert_array_equal(materialize(single, p).values, a.values[:, :3])

    def test_unique_and_recombined_use_exactly_same_three_sources(self):
        with no_fitting():
            data = three_sources(self.data, self.mapping, 0)
            unique = allocation_plan(
                data,
                self.mapping,
                rows_per_class=3,
                seed=0,
                policy="sample-without-replacement",
            )
            repeated = allocation_plan(
                data,
                self.mapping,
                rows_per_class=15,
                seed=700000,
                policy="balanced-cycle",
            )
            materialize(data, unique)
            materialize(data, repeated)
            a = Counter(s for r in unique.rows for s in r.source_ids)
            b = Counter(s for r in repeated.rows for s in r.source_ids)
            self.assertEqual(set(a), set(b))
            self.assertEqual(set(a.values()), {1})
            self.assertEqual(set(b.values()), {5})
            self.assertAlmostEqual(3 * 0.01 * 16 / 3, 15 * 0.01 * 16 / 15)

    def test_false_unique_or_balanced_claim_is_rejected(self):
        data = three_sources(self.data, self.mapping, 0)
        p = allocation_plan(
            data,
            self.mapping,
            rows_per_class=3,
            seed=0,
            policy="sample-without-replacement",
        )
        bad_rows = (
            p.rows[0],
            replace(p.rows[1], source_ids=p.rows[0].source_ids),
            *p.rows[2:],
        )
        with self.assertRaisesRegex(ValueError, "repeats a source"):
            materialize(data, replace(p, rows=bad_rows))
        with self.assertRaisesRegex(ValueError, "unequal per-pool"):
            materialize(data, replace(p, rows=bad_rows, policy="balanced-cycle"))

    def test_null_precedes_subset_and_retains_class_counts_and_development(self):
        mapping = effective_pair_map(self.data, permutation_seed=50000)
        small = three_sources(self.data, mapping, 0)
        counts = Counter(
            (s.block_id, mapping[s.source_id])
            for s in small.sources
            if s.split_id == "train"
        )
        self.assertEqual(set(counts.values()), {3})
        self.assertEqual(
            small.split_identity("development"), self.data.split_identity("development")
        )
        p = allocation_plan(
            small,
            mapping,
            rows_per_class=3,
            seed=0,
            policy="sample-without-replacement",
        )
        materialize(small, p)
        self.assertTrue(any(mapping[t.source_id] != t.condition for t in small.targets))


if __name__ == "__main__":
    unittest.main()
