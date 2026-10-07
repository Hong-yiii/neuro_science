#!/usr/bin/env python3
"""Replay the immutable endpoint run with fit-free numerical parity corrections.

The adapter reconstructs sklearn's float64 scaler accumulation and the original
PCA.transform arithmetic/dtype from saved state. It does not change the frozen
runner, fitted artifacts, global NumPy behavior, fit guards, or tolerances.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import importlib.util
import inspect
import json
import sys
import textwrap
import types
from collections.abc import Callable
from pathlib import Path
from typing import Any

APPROVED_RUNNER_SHA256 = (
    "12a0f27c11fbf3d075331cfc235d17eaf0c36ac874a3c706f4e7ee21058a812b"
)


def sha256_file(path: Path) -> str:
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


class _Float64ReductionNamespace:
    """Private NumPy proxy used only by a cloned replay function's globals."""

    __slots__ = ("_numpy",)

    def __init__(self, numpy_module: Any) -> None:
        self._numpy = numpy_module

    def __getattr__(self, name: str) -> Any:
        return getattr(self._numpy, name)

    def mean(self, *args: Any, **kwargs: Any) -> Any:
        if "dtype" in kwargs:
            raise ValueError("unexpected dtype in frozen scaler mean call")
        return self._numpy.mean(*args, **kwargs, dtype=self._numpy.float64)

    def var(self, *args: Any, **kwargs: Any) -> Any:
        if "dtype" in kwargs:
            raise ValueError("unexpected dtype in frozen scaler variance call")
        return self._numpy.var(*args, **kwargs, dtype=self._numpy.float64)


def float64_scaler_replay(replay: types.FunctionType) -> Callable[..., Any]:
    """Clone replay with float64 only for its two audited scaler reductions."""
    tree = ast.parse(textwrap.dedent(inspect.getsource(replay)))
    reductions = [
        (node.func.attr, node)
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id == "np"
        and node.func.attr in {"mean", "var"}
    ]
    if sorted(name for name, _ in reductions) != ["mean", "var"]:
        raise ValueError("expected exactly one scaler mean and variance reduction")
    for _, node in reductions:
        if (
            len(node.args) != 1
            or not isinstance(node.args[0], ast.Name)
            or node.args[0].id != "pooled_train"
            or len(node.keywords) != 1
            or node.keywords[0].arg != "axis"
            or not isinstance(node.keywords[0].value, ast.Constant)
            or node.keywords[0].value.value != 0
        ):
            raise ValueError("unexpected scaler reduction; refuse a broader amendment")

    private_globals = replay.__globals__.copy()
    numpy_module = private_globals.get("np")
    if numpy_module is None:
        raise ValueError("frozen replay has no NumPy namespace")
    private_globals["np"] = _Float64ReductionNamespace(numpy_module)
    amended = types.FunctionType(
        replay.__code__,
        private_globals,
        name=replay.__name__,
        argdefs=replay.__defaults__,
        closure=replay.__closure__,
    )
    amended.__kwdefaults__ = replay.__kwdefaults__
    amended.__annotations__ = dict(replay.__annotations__)
    amended.__dict__.update(replay.__dict__)
    amended.__doc__ = replay.__doc__
    amended.__qualname__ = replay.__qualname__
    return amended


def _sklearn_pca_replay_features(
    cue: Any,
    components: Any,
    mean: Any,
    *,
    pca_class: Any,
    numpy_module: Any,
    output_dim: int,
) -> Any:
    """Recreate fit-time sklearn PCA.transform from saved float32 state only."""
    if cue.dtype != numpy_module.float32:
        raise ValueError("unexpected cue dtype for saved PCA transform")
    if components.dtype != numpy_module.float64 or mean.dtype != numpy_module.float64:
        raise ValueError("replay did not expose the audited float64 PCA casts")
    components32 = numpy_module.asarray(components, dtype=numpy_module.float32)
    mean32 = numpy_module.asarray(mean, dtype=numpy_module.float32)
    if not numpy_module.array_equal(
        components32.astype(numpy_module.float64), components
    ):
        raise ValueError("saved PCA components are not exactly float32-representable")
    if not numpy_module.array_equal(mean32.astype(numpy_module.float64), mean):
        raise ValueError("saved PCA mean is not exactly float32-representable")
    components = components32
    mean = mean32
    rows, cells, bins = cue.shape
    if components.shape[1] != cells or mean.shape != (cells,):
        raise ValueError("saved PCA state does not match cue feature dimensions")
    flat = cue.transpose(0, 2, 1).reshape(rows * bins, cells)
    pca = pca_class(
        n_components=components.shape[0],
        svd_solver="full",
        whiten=False,
        random_state=0,
    )
    pca.components_ = components
    pca.mean_ = mean
    pca.n_components_ = components.shape[0]
    pca.n_features_in_ = cells
    # PCA.transform only uses this for array-namespace selection when whiten=False.
    pca.explained_variance_ = numpy_module.zeros(
        components.shape[0], dtype=components.dtype
    )
    transformed = pca.transform(flat).astype(numpy_module.float32)
    transformed = transformed.reshape(rows, bins, components.shape[0])
    if components.shape[0] < output_dim:
        padding = numpy_module.zeros(
            (rows, bins, output_dim - components.shape[0]),
            dtype=numpy_module.float32,
        )
        transformed = numpy_module.concatenate([transformed, padding], axis=2)
    return transformed.reshape(rows, bins * output_dim)


def precision_corrected_replay(replay: types.FunctionType) -> Callable[..., Any]:
    """Clone replay with audited scaler and fit-time PCA reconstruction semantics."""
    scaler_replay = float64_scaler_replay(replay)
    tree = ast.parse(textwrap.dedent(inspect.getsource(replay)))
    pca_casts: list[tuple[str, ast.Call]] = []
    for node in ast.walk(tree):
        if not (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "np"
            and node.func.attr == "asarray"
            and len(node.args) == 1
            and isinstance(node.args[0], ast.Subscript)
            and isinstance(node.args[0].value, ast.Name)
            and node.args[0].value.id == "pca_file"
            and isinstance(node.args[0].slice, ast.Constant)
            and isinstance(node.args[0].slice.value, str)
        ):
            continue
        field = node.args[0].slice.value
        if (
            field not in {"components", "mean"}
            or len(node.keywords) != 1
            or node.keywords[0].arg != "dtype"
            or not isinstance(node.keywords[0].value, ast.Attribute)
            or not isinstance(node.keywords[0].value.value, ast.Name)
            or node.keywords[0].value.value.id != "np"
            or node.keywords[0].value.attr != "float64"
        ):
            raise ValueError("unexpected persisted PCA state cast")
        pca_casts.append((field, node))
    if sorted(field for field, _ in pca_casts) != ["components", "mean"]:
        raise ValueError("expected exactly two persisted PCA state casts")
    private_globals = scaler_replay.__globals__
    numpy_module = replay.__globals__.get("np")
    pca_class = replay.__globals__.get("PCA")
    output_dim = replay.__globals__.get("CEBRA_DIM")
    if numpy_module is None or pca_class is None or not isinstance(output_dim, int):
        raise ValueError("frozen replay lacks required sklearn PCA bindings")

    def pca_replay(cue: Any, components: Any, mean: Any) -> Any:
        return _sklearn_pca_replay_features(
            cue,
            components,
            mean,
            pca_class=pca_class,
            numpy_module=numpy_module,
            output_dim=output_dim,
        )

    private_globals["_pca_replay_features"] = pca_replay
    return scaler_replay


def training_backend_replay(
    replay: types.FunctionType, *, device: str
) -> types.FunctionType:
    """Route only frozen encoder restoration/forward calls to the fitted backend."""
    if device != "cuda":
        raise ValueError("this approved run was fitted on CUDA")
    tree = ast.parse(textwrap.dedent(inspect.getsource(replay)))
    calls = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id in {"load_encoder_checkpoint", "_embed_cue"}
    ]
    names = [node.func.id for node in calls if isinstance(node.func, ast.Name)]
    if sorted(names) != ["_embed_cue", "_embed_cue", "load_encoder_checkpoint"]:
        raise ValueError("unexpected encoder restoration/forward call coverage")
    for call in calls:
        keywords = [item for item in call.keywords if item.arg == "device"]
        if (
            len(keywords) != 1
            or not isinstance(keywords[0].value, ast.Constant)
            or keywords[0].value.value != "cpu"
        ):
            raise ValueError("unexpected original replay backend")

    def route(helper: Callable[..., Any]) -> Callable[..., Any]:
        def call(*args: Any, **kwargs: Any) -> Any:
            if kwargs.get("device") != "cpu":
                raise ValueError("unexpected original replay backend at execution")
            return helper(*args, **dict(kwargs, device=device))

        return call

    namespace = replay.__globals__.copy()
    for name in ("load_encoder_checkpoint", "_embed_cue"):
        helper = namespace.get(name)
        if not callable(helper):
            raise ValueError(f"missing frozen replay helper: {name}")
        namespace[name] = route(helper)
    amended = types.FunctionType(
        replay.__code__,
        namespace,
        replay.__name__,
        replay.__defaults__,
        replay.__closure__,
    )
    amended.__kwdefaults__ = replay.__kwdefaults__
    return amended


def load_frozen_runner(path: Path) -> types.ModuleType:
    if sha256_file(path) != APPROVED_RUNNER_SHA256:
        raise ValueError("frozen runner differs from the independently approved bytes")
    spec = importlib.util.spec_from_file_location("endpoint_frozen_verification", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load approved frozen runner")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frozen-runner", type=Path, required=True)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=False)
    receipt: dict[str, Any] = {
        "classification": "postfit verification; zero model fits",
        "amendment": [
            "float64 accumulation for replay scaler mean and variance",
            "fit-free sklearn PCA.transform replay using persisted float32 state",
            "encoder restoration/forward replay on the hash-bound fitted CUDA backend",
        ],
        "frozen_runner_sha256": APPROVED_RUNNER_SHA256,
        "verifier_sha256": sha256_file(Path(__file__)),
        "run_dir": str(args.run_dir.resolve()),
        "tolerances_unchanged": True,
    }
    try:
        frozen = load_frozen_runner(args.frozen_runner)
        frozen.set_thread_limits()
        frozen.verify_hash_manifest(args.run_dir)
        receipt["run_hash_manifest_sha256"] = sha256_file(
            args.run_dir / "hash_manifest.json"
        )
        receipt["run_inputs_sha256"] = sha256_file(args.run_dir / "run_inputs.json")
        config = frozen.read_json(args.run_dir / "run_config.json")
        inputs = frozen.read_json(args.run_dir / "run_inputs.json")
        approval_path = Path(inputs["prefit_approval"])
        if sha256_file(approval_path) != inputs["prefit_approval_sha256"]:
            raise ValueError("prefit approval changed")
        approval = frozen.read_json(approval_path)
        receipt["prefit_approval_sha256"] = inputs["prefit_approval_sha256"]
        if frozen.stable_hash(config) != approval["config_hash"]:
            raise ValueError("replay configuration differs from prefit approval")
        device = frozen.select_device(config["device"])
        receipt["encoder_replay_device"] = device
        receipt["run_config_sha256"] = sha256_file(args.run_dir / "run_config.json")
        replay = training_backend_replay(
            precision_corrected_replay(frozen.replay_run), device=device
        )
        receipt["verification"] = replay(args.run_dir)
        receipt["status"] = "passed"
    except Exception as exc:
        receipt.update(status="failed", error=f"{type(exc).__name__}: {exc}")
        (args.output_dir / "receipt.json").write_text(
            json.dumps(receipt, indent=2) + "\n"
        )
        raise
    (args.output_dir / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2), flush=True)


if __name__ == "__main__":
    main()
