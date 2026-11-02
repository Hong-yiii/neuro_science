"""Invented-source software checks only: no biological input, result or fit access."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

from neuro.evaluation import classification_metrics
from neuro.pca_lda import fit_lda, fit_pca, fit_standardizer, raw_features
from neuro.pseudopopulation import (
    ablate_training_sources,
    materialize,
    sample_plan,
    source_usage,
    support,
)
from neuro.source_data import Source, SourceData, Split, Target, TargetDefinition, Unit


def invented_sources(seed=0):
    """Two independent invented blocks, three classes, four nonhistorical bins."""
    rng = np.random.default_rng(seed)
    units = tuple(
        Unit(f"invented/{block}/unit{u}", block, "invented fixture")
        for block in ("b0", "b1")
        for u in range(3)
    )
    sources, targets = [], []
    for block in ("b0", "b1"):
        trial = 0
        for split, n in (("fit", 4), ("dev", 2)):
            for cls in range(3):
                for _ in range(n):
                    sid = f"invented/{block}/trial{trial}"
                    sources.append(
                        Source(sid, block, split, trial, sid, "invented fixture")
                    )
                    targets.append(Target(sid, f"condition{cls}", f"class{cls}"))
                    trial += 1
    values = np.full((len(sources), len(units), 4), np.nan, dtype=np.float32)
    mask = np.array([[s.block_id == u.block_id for u in units] for s in sources])
    for i, target in enumerate(targets):
        cls = int(target.value[-1])
        values[i, mask[i]] = rng.poisson(1, (3, 4))
        values[i, cls + (0 if sources[i].block_id == "b0" else 3)] += 20
    return SourceData(
        values,
        mask,
        np.full((len(sources), 4), 0.1),
        tuple(sources),
        units,
        tuple(targets),
        (
            Split("fit", "train", "invented training"),
            Split("dev", "evaluation", "invented development"),
        ),
        TargetDefinition(
            "invented target",
            "v1",
            "invented class",
            ("fixture_class",),
            "derived",
            tuple((f"condition{i}", f"class{i}") for i in range(3)),
        ),
        np.linspace(0, 0.4, 5),
        "s",
        "count",
        "invented event",
        "invented clock",
        "contributors-disjoint",
        "Invented independent trial/group/contributor IDs",
    )


class SourceContractTests(unittest.TestCase):
    def setUp(self):
        self.data = invented_sources()

    def test_contract_owns_immutable_array_copies(self):
        original = self.data.values.copy()
        copied = replace(self.data, values=original)
        original[:] = 999
        np.testing.assert_array_equal(copied.values, self.data.values)
        with self.assertRaises(ValueError):
            copied.values[0, 0, 0] = 1

    def test_duplicate_ids_and_target_join_rejected(self):
        data = self.data
        changes = [
            {"sources": (data.sources[0],) + data.sources[:-1]},
            {"units": (data.units[0],) + data.units[:-1]},
            {"targets": (data.targets[0],) + data.targets[:-1]},
            {"splits": data.splits + (data.splits[0],)},
            {"targets": data.targets[::-1]},
            {
                "target_definition": replace(
                    data.target_definition, condition_to_target=(("x", "a"), ("x", "b"))
                )
            },
        ]
        for change in changes:
            with self.subTest(change=list(change)), self.assertRaises(ValueError):
                replace(data, **change)

    def test_bad_values_masks_exposure_and_time_rejected(self):
        data = self.data
        for value in (-1, np.nan, np.inf, 0.5):
            x = data.values.copy()
            x[0, 0, 0] = value
            with self.subTest(value=value), self.assertRaises(ValueError):
                replace(data, values=x)
        x = data.values.copy()
        x[~data.observed] = 0
        with self.assertRaisesRegex(ValueError, "unavailable"):
            replace(data, values=x)
        m = data.observed.copy()
        m[0, 0] = False
        with self.assertRaisesRegex(ValueError, "incomplete"):
            replace(data, observed=m)
        for value in (0, -1, np.nan, np.inf, 0.2):
            e = data.exposure.copy()
            e[0, 0] = value
            with self.subTest(exposure=value), self.assertRaises(ValueError):
                replace(data, exposure=e)
        with self.assertRaises(ValueError):
            replace(data, observed=np.ones(data.values.shape, bool))
        with self.assertRaises(ValueError):
            replace(data, bin_edges=np.array([0, 0.1, 0.1, 0.3, 0.4]))
        with self.assertRaises(ValueError):
            replace(data, value_unit="spikes")
        rates = data.values / 0.1
        self.assertEqual(
            replace(data, values=rates, value_unit="rate").value_unit, "rate"
        )

    def test_dependency_contributors_external_and_shared(self):
        data = self.data
        train = data.sources[0]
        external = replace(
            train,
            dependency_ids=("invented/external-previous",),
            dependency_provenance="invented label ledger",
        )
        clean = replace(data, sources=(external,) + data.sources[1:])
        self.assertEqual(len(clean.dependency_audit()["external_dependencies"]), 1)
        dev_index = next(i for i, s in enumerate(data.sources) if s.split_id == "dev")
        sources = list(clean.sources)
        sources[dev_index] = replace(
            sources[dev_index],
            dependency_ids=external.dependency_ids,
            dependency_provenance="invented ledger",
        )
        with self.assertRaisesRegex(ValueError, "contributors overlap"):
            replace(clean, sources=tuple(sources))
        exposed = replace(
            clean, sources=tuple(sources), dependency_policy="declared-dependent"
        )
        self.assertEqual(
            exposed.dependency_audit()["overlapping_contributor_ids"],
            ["invented/external-previous"],
        )
        with self.assertRaisesRegex(ValueError, "provenance"):
            replace(
                data,
                sources=(replace(train, dependency_ids=("external",)),)
                + data.sources[1:],
            )


class AssemblyTests(unittest.TestCase):
    def setUp(self):
        self.data = invented_sources()
        self.plan = sample_plan(
            self.data, split_id="fit", rows_per_condition=5, seed=42
        )

    def test_seed_reconstruction_source_usage_and_feature_order(self):
        data, plan = self.data, self.plan
        self.assertEqual(
            plan, sample_plan(data, split_id="fit", rows_per_condition=5, seed=42)
        )
        assembly = materialize(data, plan)
        np.testing.assert_array_equal(
            materialize(data, assembly.plan).values, assembly.values
        )
        index = {s.source_id: i for i, s in enumerate(data.sources)}
        for ri, row in enumerate(plan.rows):
            for block, sid in zip(data.block_ids, row.source_ids, strict=True):
                ui = [i for i, u in enumerate(data.units) if u.block_id == block]
                np.testing.assert_array_equal(
                    assembly.values[ri, ui], data.values[index[sid], ui]
                )
        self.assertEqual(
            sum(r["uses"] for r in source_usage(data, assembly)),
            len(plan.rows) * len(data.block_ids),
        )
        self.assertTrue(all(r["source_count"] > 0 for r in support(data)))
        np.testing.assert_array_equal(
            raw_features(assembly.values)[0], assembly.values[0].reshape(-1)
        )

    def test_invalid_hand_built_plans_rejected(self):
        data, plan = self.data, self.plan
        row = plan.rows[0]
        bad_row = [
            replace(row, target="wrong"),
            replace(row, condition="missing"),
            replace(row, source_ids=row.source_ids[::-1]),
            replace(row, source_ids=row.source_ids[:1]),
            replace(row, source_ids=("missing", row.source_ids[1])),
            replace(row, source_ids=(data.sources[12].source_id, row.source_ids[1])),
        ]
        for bad in bad_row:
            with self.subTest(row=bad), self.assertRaises(ValueError):
                materialize(data, replace(plan, rows=(bad,) + plan.rows[1:]))
        for bad in (
            replace(plan, rows=(row, row)),
            replace(plan, rows=()),
            replace(plan, policy="cartesian"),
            replace(plan, split_identity="wrong"),
            replace(plan, effective_conditions=plan.effective_conditions[:-1]),
            replace(
                plan,
                effective_conditions=((row.source_ids[0], "missing"),)
                + plan.effective_conditions[1:],
            ),
        ):
            with self.subTest(plan=bad), self.assertRaises(ValueError):
                materialize(data, bad)
        with self.assertRaises(ValueError):
            sample_plan(
                data, split_id="fit", rows_per_condition=100, seed=0, max_rows=5
            )

    def test_effective_world_does_not_rewrite_observed_targets(self):
        data = self.data
        mapping = {
            t.source_id: f"condition{(int(t.condition[-1]) + 1) % 3}"
            for t in data.targets
        }
        plan = sample_plan(
            data,
            split_id="fit",
            rows_per_condition=3,
            seed=0,
            effective_conditions=mapping,
        )
        assembly = materialize(data, plan)
        first_source = plan.rows[0].source_ids[0]
        observed = next(t for t in data.targets if t.source_id == first_source)
        self.assertNotEqual(observed.condition, plan.rows[0].condition)
        self.assertEqual(assembly.targets[0], "class0")
        self.assertNotEqual(
            plan.effective_condition_identity, self.plan.effective_condition_identity
        )
        for bad in (
            {},
            {**mapping, "unknown": "condition0"},
            {**mapping, first_source: "bad"},
        ):
            with self.assertRaises(ValueError):
                sample_plan(
                    data,
                    split_id="fit",
                    rows_per_condition=1,
                    seed=0,
                    effective_conditions=bad,
                )

    def test_missing_support_and_nested_training_ablation_fixed_eval(self):
        data = self.data
        dev_plan = sample_plan(data, split_id="dev", rows_per_condition=3, seed=9)
        dev = materialize(data, dev_plan)
        mapping = {
            t.source_id: f"condition{(int(t.condition[-1]) + 1) % 3}"
            for t in data.targets
        }
        small = ablate_training_sources(
            data, fraction=0.5, seed=0, effective_conditions=mapping
        )
        same = ablate_training_sources(
            data, fraction=0.5, seed=0, effective_conditions=mapping
        )
        self.assertEqual(small.sources, same.sources)
        np.testing.assert_array_equal(materialize(small, dev_plan).values, dev.values)
        self.assertEqual(materialize(small, dev_plan).plan, dev.plan)
        with self.assertRaisesRegex(ValueError, "identity mismatch"):
            materialize(
                small, sample_plan(data, split_id="fit", rows_per_condition=3, seed=9)
            )
        self.assertEqual(
            len(small.sources), 24
        )  # 12 train + unchanged 12 evaluation sources.
        self.assertEqual({r["source_count"] for r in support(small)}, {2})
        with self.assertRaises(ValueError):
            ablate_training_sources(data, sources_per_condition_block=5, seed=0)
        with self.assertRaisesRegex(ValueError, "incomplete"):
            effective = {t.source_id: "condition0" for t in data.targets}
            sample_plan(
                data,
                split_id="fit",
                rows_per_condition=1,
                seed=0,
                effective_conditions=effective,
            )


class BaselineTests(unittest.TestCase):
    def setUp(self):
        data = invented_sources()
        self.train = materialize(
            data, sample_plan(data, split_id="fit", rows_per_condition=8, seed=0)
        )
        self.dev = materialize(
            data, sample_plan(data, split_id="dev", rows_per_condition=4, seed=1)
        )

    def test_train_only_normalization_pca_layout_and_sklearn_parity(self):
        train, dev = self.train.values, self.dev.values
        state = fit_pca(train, n_components=3)
        pooled = train.transpose(0, 2, 1).reshape(-1, train.shape[1])
        scaler = StandardScaler().fit(pooled)
        np.testing.assert_allclose(
            np.asarray(state.standardizer.scaler.mean_), np.asarray(scaler.mean_)
        )
        scaled = np.asarray(scaler.transform(pooled)).astype(np.float32)
        direct = PCA(n_components=3, svd_solver="full", whiten=False).fit(scaled)
        np.testing.assert_allclose(
            np.asarray(state.pca.components_), np.asarray(direct.components_)
        )
        before = np.asarray(state.standardizer.scaler.mean_).copy()
        with (
            patch.object(
                StandardScaler, "fit", side_effect=AssertionError("evaluation refit")
            ),
            patch.object(PCA, "fit", side_effect=AssertionError("evaluation refit")),
        ):
            z = state.transform(dev + 100)
        np.testing.assert_array_equal(state.standardizer.scaler.mean_, before)
        self.assertEqual(z.shape, (len(dev), dev.shape[2] * 3))
        padded = (
            fit_pca(train, n_components=2, pad_to=4)
            .transform(dev)
            .reshape(len(dev), 4, 4)
        )
        np.testing.assert_array_equal(padded[:, :, 2:], 0)
        with self.assertRaises(ValueError):
            fit_pca(train, n_components=100)
        with self.assertRaisesRegex(ValueError, "numerical training rank"):
            fit_pca(np.ones_like(train), n_components=1)
        with self.assertRaises(ValueError):
            fit_standardizer(train).transform(dev[:, :-1])

    def test_signal_and_constant_control_metrics(self):
        model = fit_lda(raw_features(self.train.values), self.train.targets)
        features = raw_features(self.dev.values)
        metrics = classification_metrics(
            self.dev.targets,
            model.predict(features),
            classes=model.classes_,
            probabilities=model.predict_proba(features),
        )
        self.assertEqual(metrics["balanced_accuracy"], 1.0)
        classes = np.unique(self.dev.targets)
        constant = classification_metrics(
            self.dev.targets, np.repeat(classes[0], len(features)), classes=classes
        )
        self.assertAlmostEqual(constant["balanced_accuracy"], 1 / 3)
        self.assertNotIn("confidence_interval", metrics)
        with self.assertRaises(ValueError):
            classification_metrics(
                self.dev.targets, model.predict(features), classes=classes[:2]
            )
        with self.assertRaises(ValueError):
            classification_metrics(
                self.dev.targets,
                model.predict(features),
                classes=classes,
                probabilities=np.zeros((len(features), 3)),
            )

    def test_lightweight_public_modules_import_without_torch_or_cebra(self):
        code = """import importlib.abc, sys
class Deny(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, *args):
        if fullname.split('.')[0] in {'torch', 'cebra'}:
            raise AssertionError('optional dependency imported: ' + fullname)
sys.meta_path.insert(0, Deny())
import neuro.pseudopopulation, neuro.pca_lda, neuro.evaluation
assert not any(n.startswith('neuro.studies') for n in sys.modules)
"""
        with tempfile.TemporaryDirectory() as td:
            subprocess.run(
                [sys.executable, "-B", "-c", code],
                cwd=td,
                env={
                    **os.environ,
                    "PYTHONPATH": str(Path(__file__).resolve().parents[1] / "src"),
                },
                check=True,
            )


class CEBRATests(unittest.TestCase):
    def test_tiny_cpu_fit_real_sampler_exposure_transform_and_save(self):
        import torch

        from neuro.cebra import fit

        data = invented_sources()
        train = materialize(
            data, sample_plan(data, split_id="fit", rows_per_condition=3, seed=0)
        )
        dev = materialize(
            data, sample_plan(data, split_id="dev", rows_per_condition=2, seed=1)
        )
        kwargs = {
            "iterations": 3,
            "batch_size": 8,
            "output_dimension": 2,
            "hidden": 8,
            "learning_rate": 0.0003,
            "seed": 0,
            "max_seconds": 30,
            "device": "cpu",
        }
        state = fit(train.values, train.targets, **kwargs)
        counts = state.diagnostics["sample_exposure_counts"]
        np.testing.assert_array_equal(counts.sum(axis=1), [24, 24, 24])
        self.assertEqual(state.diagnostics["pairs_by_row"][0], [[0, 1], [1, 2], [2, 3]])
        self.assertEqual(
            state.diagnostics["exposure_summary"]["reference_phase_counts"],
            {"cue": 24, "nav": 0},
        )
        with (
            patch.object(
                torch.optim.Adam, "step", side_effect=AssertionError("transform fit")
            ),
            patch.object(
                StandardScaler, "fit", side_effect=AssertionError("transform fit")
            ),
        ):
            z = state.transform(dev.values, batch_vectors=3)
        self.assertEqual(z.shape, (6, 8))
        self.assertTrue(np.isfinite(z).all())
        same = fit(train.values, train.targets, **kwargs)
        np.testing.assert_allclose(same.transform(dev.values), z, atol=1e-6)
        np.testing.assert_array_equal(
            same.diagnostics["sample_exposure_counts"], counts
        )
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "fresh.pth"
            state.save(path)
            self.assertGreater(path.stat().st_size, 0)
            with self.assertRaises(FileExistsError):
                state.save(path)
        with self.assertRaises(ValueError):
            fit(train.values, train.targets, **{**kwargs, "iterations": 0})
        with self.assertRaises(TimeoutError):
            fit(train.values, train.targets, **{**kwargs, "max_seconds": 1e-12})
        from neuro.cebra_solver import make_solver

        broken = make_solver(train.values.shape[1], 2, 8, 0.0003, "cpu")
        original_step = broken.step

        def corrupt_loss(batch):
            result = original_step(batch)
            broken.log["total"][-1] = float("nan")
            return result

        with (
            patch("neuro.cebra.make_solver", return_value=broken),
            patch.object(broken, "step", side_effect=corrupt_loss),
            self.assertRaisesRegex(RuntimeError, "nonfinite CEBRA loss"),
        ):
            fit(train.values, train.targets, **kwargs)


if __name__ == "__main__":
    unittest.main()
