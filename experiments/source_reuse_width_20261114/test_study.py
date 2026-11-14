"""Invented and metadata-only checks; no biological fitting."""

import itertools
import unittest
from dataclasses import replace

import numpy as np

from neuro.notebook_inputs import demo_configuration, inspect_inputs, load_inputs
from neuro.studies.population_models import frozen_models
from . import study


def fixture(units=24, blocks=6):
    cfg = demo_configuration()
    cfg.update(
        demo_units=units, demo_blocks=blocks, demo_bins=10, landmarks=list(range(1, 7))
    )
    data, _ = load_inputs(inspect_inputs(cfg))
    conditions = (
        "1->2",
        "1->4",
        "2->5",
        "2->6",
        "3->1",
        "4->6",
        "5->3",
        "5->4",
        "6->2",
    )
    rows = [i for i, t in enumerate(data.targets) if t.condition in conditions]
    data = replace(
        data,
        values=data.values[rows],
        observed=data.observed[rows],
        exposure=data.exposure[rows],
        sources=tuple(data.sources[i] for i in rows),
        targets=tuple(data.targets[i] for i in rows),
        target_definition=replace(
            data.target_definition,
            condition_to_target=tuple((c, c) for c in conditions),
        ),
    )
    aliases = {b: f"S{i:02d}" for i, b in enumerate(data.block_ids)}
    design = {
        "rosters": {
            r: {"session_aliases": list(aliases.values())[:n]}
            for r, n in (
                ("core", max(2, blocks // 3)),
                ("middle", max(3, 2 * blocks // 3)),
                ("full", blocks),
            )
        }
    }
    meta = {
        "aliases": aliases,
        "source_aliases": {s.source_id: f"T{i}" for i, s in enumerate(data.sources)},
    }
    return data, meta, design


class DesignTests(unittest.TestCase):
    def test_optimizer_both_support_objectives_and_lex_against_enumeration(self):
        pairs = [f"{a}->{b}" for a in range(1, 7) for b in range(1, 7) if a != b]
        rng = np.random.default_rng(6)
        train = rng.integers(1, 8, (5, 30))
        train[0] = 5
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
            indices = [pairs.index(p) for p in labels]
            widths = [
                -int(meta["widths"][(train[:, indices] >= minimum).all(1)].sum())
                for minimum in (5, 3)
            ]
            candidates.append((*widths, labels))
        expected = min(candidates)
        actual = study.select_panel(meta, 6)
        self.assertEqual(
            (
                actual["maximum_columns_min5"],
                actual["maximum_columns_min3_at_min5_optimum"],
                actual["conditions"],
            ),
            (-expected[0], -expected[1], expected[2]),
        )

    def test_schedule_fits_and_shared_bridge(self):
        cases = study.schedule()
        self.assertEqual(len({c["id"] for c in cases}), 48)
        self.assertEqual(sum(c["world"] == "observed" for c in cases), 18)
        self.assertEqual(sum(c["arm"] == "B3" for c in cases), 8)
        cfg = study.configuration({})
        self.assertEqual(cfg["expected_fit_counts"]["optimizer_updates"], 96000)
        self.assertEqual(
            sum(
                v
                for k, v in cfg["expected_fit_counts"].items()
                if k != "optimizer_updates"
            ),
            2448,
        )


class PlanTests(unittest.TestCase):
    def test_nested_sources_exact_width_projection_common_dev_and_nulls(self):
        with frozen_models():
            data, meta, design = fixture()
            for permutation in (None, 61000):
                plans = study.paired_plans(
                    data, meta, design, seed=0, permutation=permutation
                )
                ranks = study.verify_plans(plans, numerical_rank=True)
                self.assertEqual(len(ranks), 6)
                byarm = {r["arm"]: r for r in ranks}
                self.assertEqual(byarm["U3"]["training_source_extra_draw_fraction"], 0)
                self.assertEqual(
                    byarm["B5"]["training_source_extra_draw_fraction"], 0.6875
                )
                if permutation:
                    source, plan, _ = plans["Wfull"]
                    effective = dict(plan.effective_conditions)
                    self.assertTrue(
                        any(
                            effective[t.source_id] != t.condition
                            for t in source.targets
                            if t.source_id in effective
                        )
                    )
                again = study.paired_plans(
                    data, meta, design, seed=1, permutation=permutation
                )
                for arm in study.ARMS:
                    self.assertEqual(plans[arm][2], again[arm][2])

    def test_source_order_unaffected_by_input_iteration_order(self):
        pool = ["a", "b", "c", "d", "e"]
        self.assertEqual(
            study.source_order(pool, block="s", condition="1->2", seed=0),
            study.source_order(pool[::-1], block="s", condition="1->2", seed=0),
        )

    def test_prefit_rejects_corrupt_source_budget(self):
        with frozen_models():
            data, meta, design = fixture()
            plans = study.paired_plans(data, meta, design, seed=0)
            plans["B5"] = plans["B2"]
            with self.assertRaises(ValueError):
                study.verify_plans(plans)


if __name__ == "__main__":
    unittest.main()
