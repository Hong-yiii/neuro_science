"""Invented scientific invariants for the fresh class × roster grid; no models fit."""

import itertools
import unittest
from collections import Counter

import numpy as np

from neuro.notebook_artifacts import no_fitting
from neuro.notebook_inputs import demo_configuration, inspect_inputs, load_inputs
from neuro.studies import population_grid as study


class DesignTests(unittest.TestCase):
    def test_milp_optimum_and_ties_against_enumerated_derangements(self):
        pairs = [f"{a}->{b}" for a in range(1, 7) for b in range(1, 7) if a != b]
        rng = np.random.default_rng(6)
        train = rng.integers(1, 8, (5, 30))
        train[0] = 4
        meta = dict(
            pairs=pairs,
            train=train,
            development=np.ones_like(train),
            widths=np.array([2, 5, 3, 7, 4]),
        )
        candidates = []
        for perm in itertools.permutations(range(1, 7)):
            if any(a == b for a, b in enumerate(perm, 1)):
                continue
            labels = [f"{a}->{b}" for a, b in enumerate(perm, 1)]
            ci = [pairs.index(p) for p in labels]
            selected = np.all(train[:, ci] >= 2, axis=1)
            candidates.append(
                (
                    -int(meta["widths"][selected].sum()),
                    -int(train[selected][:, ci].sum()),
                    labels,
                )
            )
        expected = min(candidates)
        actual = study.optimize_classes(meta, 6, complete_ties=True)
        self.assertEqual(
            (
                actual["maximum_columns"],
                actual["optimal_training_sources_at_maximum_width"],
                actual["conditions"],
            ),
            (-expected[0], -expected[1], expected[2]),
        )

    def test_exact_harmonic_tie_uses_width_tiebreaker(self):
        pairs = [f"{a}->{a % 6 + 1}" for a in range(1, 7)]
        row = [2, 3, 4, 5, 6, 7]
        meta = dict(
            pairs=pairs,
            sessions=["A", "B", "C"],
            train=np.array([row, row[::-1], [2] * 6]),
            development=np.ones((3, 6), int),
            widths=np.array([8, 9, 10]),
            aliases={s: s for s in "ABC"},
        )
        prefixes, grid = study.selection_tables(meta, {"conditions": pairs})
        self.assertEqual(prefixes[0]["session_aliases"], ["B"])
        self.assertEqual(grid[-1]["session_aliases"], ["B", "A", "C"])
        self.assertEqual(prefixes[-1]["balanced_no_reuse_rows"], 12)


class PlanTests(unittest.TestCase):
    def test_paired_policies_nested_rosters_and_null_before_subset(self):
        cfg = demo_configuration()
        cfg.update(demo_units=24, demo_blocks=6, demo_bins=10)
        with no_fitting():
            data, _ = load_inputs(inspect_inputs(cfg))
            aliases = {b: str(i) for i, b in enumerate(data.block_ids)}
            design = {
                "grid": [
                    {
                        "class_count": 6,
                        "roster": tag,
                        "session_aliases": list(aliases.values())[:n],
                    }
                    for tag, n in zip(study.ROSTERS, (2, 4, 6))
                ]
            }
            for permutation in (None, 60000):
                plans = study.paired_plans(
                    data, {"aliases": aliases}, design, seed=0, permutation=permutation
                )
                ranks = study.verify_plans(plans, numerical_rank=True)
                self.assertEqual(len(ranks), 9)
                for tag in study.ROSTERS:
                    a, b = [
                        Counter(
                            sid for r in plans[tag, p][1].rows for sid in r.source_ids
                        )
                        for p in ("U2", "R16")
                    ]
                    self.assertEqual(set(a), set(b))
                    self.assertEqual(set(a.values()), {1})
                    self.assertEqual(set(b.values()), {8})
                if permutation is not None:
                    source, plan, _ = plans["S100", "U2"]
                    effective = dict(plan.effective_conditions)
                    self.assertTrue(
                        any(
                            effective[t.source_id] != t.condition
                            for t in source.targets
                        )
                    )


if __name__ == "__main__":
    unittest.main()
