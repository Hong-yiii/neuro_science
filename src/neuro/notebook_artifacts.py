"""Protected fresh-run artifacts and authenticated fit-blocked model replay.

Only this new run's explicitly indexed files are read. Joblib is pickle-based:
never verify/load an untrusted run without its separately retained manifest hash.
"""

from __future__ import annotations

import importlib.metadata
import importlib.util
import json
import re
import sys
from collections import Counter
from contextlib import ExitStack, contextmanager
from pathlib import Path
from unittest.mock import patch

import joblib
import numpy as np
from sklearn.decomposition import PCA
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

from neuro.evaluation import classification_metrics
from neuro.pca_lda import raw_features
from neuro.place195 import file_hash


def runtime_identity():
    versions = {}
    for name in (
        "numpy",
        "scikit-learn",
        "torch",
        "cebra",
        "joblib",
        "nbclient",
        "ipykernel",
    ):
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            versions[name] = "not installed"
    origins = {}
    for name in ("numpy", "sklearn", "torch", "cebra", "joblib"):
        spec = importlib.util.find_spec(name)
        origin = spec.origin if spec else None
        origins[name] = {
            "path": origin,
            "sha256": file_hash(Path(origin))
            if origin and Path(origin).is_file()
            else None,
        }
    return {
        "executable": sys.executable,
        "prefix": sys.prefix,
        "python": sys.version,
        "packages": versions,
        "dependency_origins": origins,
        "neuro_origin": str(Path(__file__).parent),
        "neuro_module_sha256": {
            p.name: file_hash(p) for p in Path(__file__).parent.glob("*.py")
        },
        "imported_versions": {
            name: str(getattr(sys.modules[name], "__version__", "unknown"))
            for name in origins
            if name in sys.modules
        },
        "loaded_optional_modules": sorted(
            name for name in ("torch", "cebra") if name in sys.modules
        ),
    }


def stable_kernel_identity(identity):
    return {
        key: value
        for key, value in identity.items()
        if key not in {"loaded_optional_modules", "imported_versions"}
    }


def validate_kernel_identity(configuration):
    actual = runtime_identity()
    expected = configuration.get("expected_kernel_identity")
    if expected is None and configuration["mode"] in {"place195", "compact"}:
        raise ValueError(
            "supplied biological execution requires a pinned kernel identity"
        )
    if expected is not None and stable_kernel_identity(actual) != expected:
        raise ValueError(
            "actual kernel interpreter/dependencies/package code differ from expected identity"
        )
    return actual


def target_heads(assembly):
    pair = np.array([r.condition for r in assembly.plan.rows])
    components = [value.split("->") for value in pair]
    if any(len(c) != 2 or c[0] == c[1] for c in components):
        raise ValueError("explicit unequal ordered-pair conditions required")
    return {
        "pair": pair,
        "start": np.array([c[0] for c in components]),
        "goal": np.array([c[1] for c in components]),
    }


def _json(value):
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    raise TypeError("unsupported artifact JSON value")


def write_private_json(path: Path, payload):
    with path.open("x") as handle:
        json.dump(
            payload, handle, default=_json, sort_keys=True, indent=2, allow_nan=False
        )
    path.chmod(0o600)


class FitAccounting:
    """Count actual sklearn fits, solver constructions and optimizer updates."""

    def __init__(self, *, cebra=False):
        self.cebra = cebra
        self.counts = Counter(
            dict.fromkeys(("pca", "logistic", "lda", "cebra", "optimizer_updates"), 0)
        )
        self.stack = ExitStack()

    def start(self):
        def counted(kind, original):
            def call(*args, **kwargs):
                self.counts[kind] += 1
                return original(*args, **kwargs)

            return call

        for cls, kind in (
            (PCA, "pca"),
            (LogisticRegression, "logistic"),
            (LinearDiscriminantAnalysis, "lda"),
        ):
            self.stack.enter_context(patch.object(cls, "fit", counted(kind, cls.fit)))
        if self.cebra:
            import torch

            import neuro.cebra as module

            self.stack.enter_context(
                patch.object(
                    module, "make_solver", counted("cebra", module.make_solver)
                )
            )
            self.stack.enter_context(
                patch.object(
                    torch.optim.Adam,
                    "step",
                    counted("optimizer_updates", torch.optim.Adam.step),
                )
            )
        return self

    def stop(self):
        self.stack.close()
        return dict(self.counts)


@contextmanager
def no_fitting(*, cebra=False):
    def forbidden(*args, **kwargs):
        raise RuntimeError("fresh-artifact verification forbids fitting/updates")

    with ExitStack() as stack:
        for cls in (
            PCA,
            StandardScaler,
            LogisticRegression,
            LinearDiscriminantAnalysis,
        ):
            stack.enter_context(patch.object(cls, "fit", forbidden))
            if hasattr(cls, "fit_transform"):
                stack.enter_context(patch.object(cls, "fit_transform", forbidden))
        if cebra:
            import torch

            import neuro.cebra as module

            stack.enter_context(patch.object(module, "fit", forbidden))
            stack.enter_context(patch.object(torch.optim.Adam, "step", forbidden))
        yield


class ArtifactStore:
    def __init__(self, root: Path):
        self.root = Path(root)
        self.root.mkdir(mode=0o700, parents=True, exist_ok=False)
        self.files = {}
        self.encoders = {}
        self.bundles = {}
        self.readouts = []

    def save(self, name, obj):
        if not re.fullmatch(r"[A-Za-z0-9_-]+", name):
            raise ValueError("invalid artifact name")
        filename = name + ".joblib"
        if filename in self.files:
            raise ValueError("duplicate artifact name")
        path = self.root / filename
        with path.open("xb") as handle:
            joblib.dump(obj, handle, compress=3)
        path.chmod(0o600)
        self.files[filename] = file_hash(path)
        return filename

    def save_bundle(self, name, train, development):
        self.save(name, {"train": train, "development": development})
        self.bundles[name] = (train, development)

    def save_encoder(self, name, encoder, *, kind):
        if kind not in {"raw", "pca", "cebra"}:
            raise ValueError("unknown encoder kind")
        self.save(name, encoder)
        self.encoders[name] = kind

    def readout(
        self,
        name,
        model,
        *,
        encoder,
        bundle,
        head,
        train_features,
        development_features,
    ):
        train, development = self.bundles[bundle]
        targets = (target_heads(train)[head], target_heads(development)[head])
        records = {}
        for split, features, y in zip(
            ("train", "development"),
            (train_features, development_features),
            targets,
            strict=True,
        ):
            pred, probability = model.predict(features), model.predict_proba(features)
            if not np.isfinite(probability).all():
                raise RuntimeError("nonfinite readout probability")
            records[split] = {
                "features": features,
                "targets": y,
                "predictions": pred,
                "probabilities": probability,
                "metrics": classification_metrics(
                    y, pred, classes=model.classes_, probabilities=probability
                ),
            }
        self.save(name + "_model", model)
        self.save(name + "_predictions", records)
        self.readouts.append(
            {"name": name, "encoder": encoder, "bundle": bundle, "head": head}
        )
        return {
            "name": name,
            "head": head,
            "train": records["train"]["metrics"],
            "development": records["development"]["metrics"],
            "balanced_accuracy_gap": records["train"]["metrics"]["balanced_accuracy"]
            - records["development"]["metrics"]["balanced_accuracy"],
        }

    def finish(self, *, fit_counts, expected_counts):
        if fit_counts != expected_counts:
            raise RuntimeError("unexpected model/update fit accounting")
        manifest = {
            "files": self.files,
            "encoders": self.encoders,
            "readouts": self.readouts,
            "fit_counts": fit_counts,
            "expected_counts": expected_counts,
        }
        write_private_json(self.root / "manifest.json", manifest)
        return file_hash(self.root / "manifest.json")


def verify_artifacts(root: Path, *, expected_manifest_hash: str) -> dict:
    root = Path(root)
    manifest_path = root / "manifest.json"
    if manifest_path.is_symlink() or file_hash(manifest_path) != expected_manifest_hash:
        raise ValueError("fresh-artifact manifest authentication failed")
    manifest = json.loads(manifest_path.read_text())
    if manifest["fit_counts"] != manifest["expected_counts"]:
        raise ValueError("stored fit accounting mismatch")
    for filename, expected in manifest["files"].items():
        if not re.fullmatch(r"[A-Za-z0-9_-]+\.joblib", filename):
            raise ValueError("unsafe artifact path")
        path = root / filename
        if path.is_symlink() or file_hash(path) != expected:
            raise ValueError("fresh artifact hash mismatch")
    cache = {}

    def load(name):
        filename = name + ".joblib"
        if filename not in manifest["files"]:
            raise ValueError("unindexed artifact")
        if name not in cache:
            cache[name] = joblib.load(root / filename)
        return cache[name]

    def compare(actual, expected):
        if isinstance(expected, dict):
            if actual.keys() != expected.keys():
                raise AssertionError("replayed metric keys differ")
            for k in expected:
                compare(actual[k], expected[k])
        elif isinstance(expected, (int, float)):
            np.testing.assert_allclose(actual, expected, rtol=1e-6, atol=1e-6)
        else:
            if actual != expected:
                raise AssertionError("replayed metric differs")

    checked = 0
    with no_fitting(cebra="cebra" in manifest["encoders"].values()):
        for readout in manifest["readouts"]:
            name, encoder_name = readout["name"], readout["encoder"]
            encoder, bundle = load(encoder_name), load(readout["bundle"])
            model, saved = load(name + "_model"), load(name + "_predictions")
            for split in ("train", "development"):
                assembly = bundle[split]
                features = encoder.transform(assembly.values)
                if manifest["encoders"][encoder_name] == "raw":
                    features = raw_features(features)
                np.testing.assert_allclose(
                    features, saved[split]["features"], rtol=1e-5, atol=1e-5
                )
                y = target_heads(assembly)[readout["head"]]
                np.testing.assert_array_equal(y, saved[split]["targets"])
                pred, prob = model.predict(features), model.predict_proba(features)
                np.testing.assert_array_equal(pred, saved[split]["predictions"])
                np.testing.assert_allclose(
                    prob, saved[split]["probabilities"], rtol=1e-6, atol=1e-6
                )
                metrics = classification_metrics(
                    y, pred, classes=model.classes_, probabilities=prob
                )
                compare(metrics, saved[split]["metrics"])
                checked += 1
    return {
        "status": "fit-blocked-loaded-model-replay-passed",
        "readout_splits_checked": checked,
        "fit_counts": manifest["fit_counts"],
        "manifest_sha256": expected_manifest_hash,
    }
