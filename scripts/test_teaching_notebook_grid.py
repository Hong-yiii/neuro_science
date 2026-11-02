"""Exercise staged notebook orchestration with invented sources and mock estimators.

No notebook kernel, biological input, estimator fit or optimizer is executed.
Real source assembly, contributor checks, artifact/readout bookkeeping and metrics
are retained; deterministic mock objects replace every fitting operation.
"""

from __future__ import annotations

import ast
from collections import Counter
import contextlib
import hashlib
import io
import json
from pathlib import Path
from types import SimpleNamespace
import unittest

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from neuro.notebook_artifacts import ArtifactStore, no_fitting, target_heads
from neuro.notebook_diagnostics import embedding_summary, learning_summary
from neuro.notebook_inputs import demo_configuration, effective_pair_map, inspect_inputs, load_inputs
from neuro.notebook_support import checked_assemblies, compact_metrics, source_budget, usage_summary
from neuro.pca_lda import raw_features
from neuro.pseudopopulation import materialize, sample_plan

from scripts.notebook_model_guide import (
    _revise_baseline_loop,
    _revise_cebra_loop,
    _staged_baseline,
    _staged_cebra,
    enrich_model_notebooks,
)


def original_notebook_cells():
    """Read the generator's original cells without writing generated files."""
    path = Path(__file__).with_name("build_fresh_notebooks.py")
    tree = ast.parse(path.read_text())
    build = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "build")
    last = next(
        i for i, node in enumerate(build.body)
        if isinstance(node, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == "c" for target in node.targets)
    )
    build.body = [
        node for node in build.body[:last + 1]
        if not isinstance(node, (ast.Import, ast.ImportFrom, ast.If))
    ] + [ast.Return(ast.Tuple([ast.Name("b", ast.Load()), ast.Name("c", ast.Load())], ast.Load()))]
    tree.body = [node for node in tree.body if not isinstance(node, ast.If)]
    ast.fix_missing_locations(tree)
    namespace = {"__file__": str(path.resolve()), "__name__": "unexecuted_notebook_source"}
    exec(compile(tree, str(path), "exec"), namespace)
    b, c = namespace["build"]()
    return b, c, namespace["md"], namespace["code"]


class MemoryStore(ArtifactStore):
    """Use real readout bookkeeping, replacing file output with unique memory keys."""

    def __init__(self):
        self.saved = {}
        self.bundles = {}
        self.encoders = {}
        self.readouts = []
        self.current_key = None

    def save(self, name, payload):
        if name in self.saved:
            raise AssertionError(f"duplicate artifact key: {name}")
        self.saved[name] = payload

    def save_bundle(self, name, train, development):
        self.current_key = name
        super().save_bundle(name, train, development)


class MockScaler:
    """Return transparent fixture statistics; never instantiate an estimator."""

    def __init__(self, values):
        pooled = values.transpose(0, 2, 1).reshape(-1, values.shape[1]).astype(float)
        mean, variance = pooled.mean(axis=0), pooled.var(axis=0)
        self.scaler = SimpleNamespace(mean_=mean, var_=variance, scale_=np.where(variance > 0, np.sqrt(variance), 1))

    def transform(self, values):
        return (values - self.scaler.mean_[None, :, None]) / self.scaler.scale_[None, :, None]


class MockPCA:
    """A fixed coordinate selector, deliberately not a learned PCA."""

    def __init__(self, values, dimensions):
        self.standardizer = MockScaler(values)
        self.pca = SimpleNamespace(
            mean_=np.zeros(values.shape[1]),
            components_=np.eye(values.shape[1])[:dimensions],
            explained_variance_ratio_=np.full(dimensions, 1 / dimensions),
        )

    def transform(self, values):
        standardized = self.standardizer.transform(values)
        pooled = standardized.transpose(0, 2, 1).reshape(-1, values.shape[1])
        return ((pooled - self.pca.mean_) @ self.pca.components_.T).reshape(len(values), -1)


class MockNetwork:
    def parameters(self):
        return []


class MockCEBRA:
    """A fixed normalized selector with fabricated loss/exposure instrumentation."""

    def __init__(self, values, *, iterations, output_dimension):
        self.selector = MockPCA(values, output_dimension)
        self.dimension = output_dimension
        self.solver = SimpleNamespace(model=MockNetwork())
        self.diagnostics = {
            "loss": {name: np.linspace(2, 1, iterations).tolist() for name in ("total", "pos", "neg", "temperature")},
            "sample_exposure_counts": np.ones((3, values.shape[0] * values.shape[2]), dtype=int),
            "exposure_summary": {"reference_phase_counts": {"cue": iterations, "nav": 0}},
        }

    def transform(self, values):
        vectors = self.selector.transform(values).reshape(-1, self.dimension)
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        vectors = vectors / np.where(norms > 0, norms, 1)
        return vectors.reshape(len(values), -1)


class MockReadout:
    """A fixed softmax whose parameters depend only on declared shapes/classes."""

    def __init__(self, features, labels, C):
        self.classes_ = np.unique(labels)
        columns = features.shape[1]
        self.named_steps = {
            "standardscaler": SimpleNamespace(
                mean_=np.zeros(columns), scale_=np.ones(columns),
                transform=lambda x: np.asarray(x, dtype=float),
            ),
            "logisticregression": SimpleNamespace(
                coef_=(np.arange(len(self.classes_) * columns).reshape(len(self.classes_), columns) % 17) * .001,
                intercept_=np.zeros(len(self.classes_)),
                classes_=self.classes_, C=C, n_iter_=np.array([1]),
            ),
        }

    def predict_proba(self, features):
        head = self.named_steps["logisticregression"]
        logits = np.asarray(features, dtype=float) @ head.coef_.T + head.intercept_
        positive = np.exp(logits - logits.max(axis=1, keepdims=True))
        return positive / positive.sum(axis=1, keepdims=True)

    def predict(self, features):
        return self.classes_[self.predict_proba(features).argmax(axis=1)]


def digest(values):
    array = np.asarray(values)
    return (array.shape, str(array.dtype), hashlib.sha256(array.tobytes()).hexdigest())


def execute_orchestration(cells, *, family, data, configuration):
    """Execute only extracted orchestration cells, with every fit replaced."""
    store, trace = MemoryStore(), []
    settings = configuration["execution"]

    def record(kind, features, labels=None, **kwargs):
        trace.append((kind, store.current_key, digest(features), None if labels is None else tuple(labels), kwargs))

    def standardizer(values):
        record("scaler", values)
        return MockScaler(values)

    def pca(values, *, n_components):
        record("pca", values, n_components=n_components)
        return MockPCA(values, n_components)

    def cebra(values, labels, **kwargs):
        record("cebra", values, labels, **kwargs)
        return MockCEBRA(values, iterations=kwargs["iterations"], output_dimension=kwargs["output_dimension"])

    def logistic(features, labels, **kwargs):
        record("logistic", features, labels, **kwargs)
        return MockReadout(features, labels, kwargs["C"])

    def lda(features, labels):
        record("lda", features, labels)
        return MockReadout(features, labels, None)

    namespace = {
        "data": data, "settings": settings, "configuration": configuration, "store": store,
        "np": np, "json": json, "plt": plt, "display": lambda figure: None,
        "os": SimpleNamespace(environ={}), "time": SimpleNamespace(monotonic=lambda: 1000.0),
        "effective_pair_map": effective_pair_map, "sample_plan": sample_plan, "materialize": materialize,
        "source_budget": source_budget, "checked_assemblies": checked_assemblies,
        "usage_summary": usage_summary, "target_heads": target_heads,
        "fit_standardizer": standardizer, "raw_features": raw_features, "fit_pca": pca,
        "cebra": SimpleNamespace(fit=cebra), "fit_logistic": logistic, "fit_lda": lda,
        "embedding_summary": embedding_summary, "learning_summary": learning_summary,
        "plot_confusions": lambda *args, **kwargs: plt.figure(),
        "plot_learning": lambda *args, **kwargs: plt.figure(), "compact_metrics": compact_metrics,
        "case_diagnostics": {}, "reference_view": None, "results": [],
    }
    if family == "B":
        observed = effective_pair_map(data, permutation_seed=None)
        plan = sample_plan(data, split_id="development", rows_per_condition=settings["development_rows_per_condition"], seed=0, effective_conditions=observed)
        development = materialize(data, plan)
        namespace.update(observed=observed, dev_plan=plan, reference_development=development)
        store.save("fixed_development", development)
    with no_fitting(), contextlib.redirect_stdout(io.StringIO()):
        for cell in cells:
            if cell["cell_type"] == "code":
                exec(compile("".join(cell["source"]), "mocked_notebook_orchestration", "exec"), namespace)
    return namespace, trace, store


class TeachingGridTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.b, cls.c, cls.md, cls.code = original_notebook_cells()
        cls.configuration = demo_configuration()
        cls.data, _ = load_inputs(inspect_inputs(cls.configuration))

    def tearDown(self):
        plt.close("all")

    def check_family(self, family):
        cells = self.b if family == "B" else self.c
        prefix = "for seed in settings['seeds']" if family == "B" else "for world in ('observed', 'permuted')"
        original = next("".join(cell["source"]) for cell in cells if "".join(cell["source"]).startswith(prefix))
        revise = _revise_baseline_loop if family == "B" else _revise_cebra_loop
        stage = _staged_baseline if family == "B" else _staged_cebra
        code, md = type(self).code, type(self).md
        old, old_trace, old_store = execute_orchestration([code(revise(original))], family=family, data=self.data, configuration=self.configuration)
        new, new_trace, new_store = execute_orchestration(stage(original, md, code), family=family, data=self.data, configuration=self.configuration)
        self.assertEqual(new_trace, old_trace, "Every mock fit must receive the same case, values, targets and settings in order")
        expected = {f"observed_seed{seed}_{budget}" for seed in (0, 1) for budget in ("full", "reduced")}
        if family == "C":
            expected |= {f"permuted_seed0_{budget}" for budget in ("full", "reduced")}
        self.assertEqual(set(new_store.bundles), expected)
        self.assertEqual(set(new_store.saved), set(old_store.saved), "No artifact key may be duplicated, dropped or invented by staging")
        self.assertEqual(new["results"], old["results"])
        counts = Counter(entry[0] for entry in new_trace)
        self.assertEqual(counts["pca"], 4 if family == "B" else 6)
        self.assertEqual(counts["logistic"], 24 if family == "B" else 54)
        self.assertEqual(counts["lda"], 12 if family == "B" else 0)
        self.assertEqual(counts["cebra"], 0 if family == "B" else 6)
        self.assertEqual(Counter(entry[1] for entry in new_trace if entry[0] == "pca"), Counter({case: 1 for case in expected}))
        if family == "C":
            self.assertEqual(sum(entry[4]["iterations"] for entry in new_trace if entry[0] == "cebra"), 6 * self.configuration["execution"]["iterations"])
        for case, (train, development) in new_store.bundles.items():
            old_train, old_dev = old_store.bundles[case]
            self.assertEqual(train.plan, old_train.plan)
            self.assertEqual(development.plan, old_dev.plan)
            np.testing.assert_array_equal(train.values, old_train.values)
            np.testing.assert_array_equal(development.values, old_dev.values)
            world = case.split("_", 1)[0]
            reference = new_store.saved["fixed_development" if family == "B" else world + "_fixed_development"]
            self.assertEqual(development.plan, reference.plan)
            np.testing.assert_array_equal(development.values, reference.values)
            np.testing.assert_array_equal(development.targets, reference.targets)
            np.testing.assert_array_equal(development.exposure, reference.exposure)
        self.assertEqual(new["reference_view"]["key"], "observed_seed0_full")
        if family == "B":
            for split in ("train", "development"):
                np.testing.assert_array_equal(new["reference_view"][split], old["reference_view"][split])
        else:
            for model in ("pca", "cebra"):
                for actual, wanted in zip(new["reference_view"]["features"][model], old["reference_view"]["features"][model], strict=True):
                    np.testing.assert_array_equal(actual, wanted)

    def test_pca_lda_staging_preserves_every_case_and_readout(self):
        self.check_family("B")

    def test_cebra_staging_preserves_worlds_and_fit_budget(self):
        self.check_family("C")

    def test_generated_cells_parse_and_keep_execution_boundaries(self):
        b, c = enrich_model_notebooks(self.b, self.c, type(self).md, type(self).code)
        for original, enriched in ((self.b, b), (self.c, c)):
            old_code = [cell for cell in original if cell["cell_type"] == "code"]
            new_code = [cell for cell in enriched if cell["cell_type"] == "code"]
            self.assertEqual(old_code[0], new_code[0])
            self.assertEqual(original[-1], enriched[-1])
            for cell in new_code:
                ast.parse("".join(cell["source"]))


if __name__ == "__main__":
    unittest.main()
