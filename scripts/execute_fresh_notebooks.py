"""Bounded sequential fresh-kernel execution; explicit inputs, no retries or server.

Run with notebook extras installed. --runtime-python selects a task-owned kernel
runtime; --dependency-path adds explicit read-only dependency/code locations.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
import signal
import subprocess
import sys
import tempfile
import time
from contextlib import suppress
from pathlib import Path

NOTEBOOKS = ("01_pseudopopulation", "02_pca_lda", "03_cebra")


def expected_fit_counts(names, iterations):
    grid = {
        NOTEBOOKS[0]: (0, 0, 0, 0),
        NOTEBOOKS[1]: (4, 24, 12, 0),
        NOTEBOOKS[2]: (6, 54, 0, 6),
    }
    if len(set(names)) != len(names) or not set(names) <= grid.keys() or not names:
        raise ValueError("invalid notebook selection")
    result = {
        kind: sum(grid[name][i] for name in names)
        for i, kind in enumerate(("pca", "logistic", "lda", "cebra"))
    }
    result["optimizer_updates"] = result["cebra"] * iterations
    return result


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def write(path, value):
    with Path(path).open("x") as handle:
        json.dump(value, handle, indent=2, sort_keys=True, allow_nan=False)
    Path(path).chmod(0o600)


def descendants(pid):
    """Owned-process ancestry and RSS from Linux /proc; no command lines/environments."""
    states = {}
    for directory in Path("/proc").iterdir():
        if not directory.name.isdigit():
            continue
        try:
            fields = (directory / "stat").read_text().rsplit(")", 1)[1].split()
            states[int(directory.name)] = (
                int(fields[1]),
                int(fields[21]) * os.sysconf("SC_PAGE_SIZE"),
            )
        except (FileNotFoundError, ProcessLookupError, PermissionError, IndexError):
            continue
    owned = {pid}
    while True:
        children = {p for p, (parent, _) in states.items() if parent in owned}
        if children <= owned:
            break
        owned |= children
    return owned, sum(states.get(p, (0, 0))[1] for p in owned)


def terminate(process):
    owned, _ = descendants(process.pid)
    for pid in owned - {process.pid}:
        with suppress(ProcessLookupError):
            os.kill(pid, signal.SIGTERM)
    with suppress(ProcessLookupError):
        os.killpg(process.pid, signal.SIGTERM)
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        for pid in owned:
            with suppress(ProcessLookupError):
                os.kill(pid, signal.SIGKILL)
        process.wait()


def worker(args):
    import nbformat  # pyright: ignore[reportMissingImports]
    from nbclient import NotebookClient  # pyright: ignore[reportMissingImports]
    from nbconvert import HTMLExporter  # pyright: ignore[reportMissingImports]

    from neuro.notebook_artifacts import (
        stable_kernel_identity,
        verify_artifacts,
        write_private_json,
    )
    from neuro.place195 import file_hash

    root = args.output.resolve()
    config = json.loads((root / "configuration.json").read_text())
    deadline = float(os.environ["NEURO_DEADLINE_MONOTONIC"])
    environment = {
        "PYTHONPATH": os.pathsep.join(args.dependency_path),
        "PYTHONNOUSERSITE": "1",
        "PYTHONDONTWRITEBYTECODE": "1",
        "OMP_NUM_THREADS": "2",
        "OPENBLAS_NUM_THREADS": "2",
        "MKL_NUM_THREADS": "2",
        "MPLBACKEND": "Agg",
        "MPLCONFIGDIR": str(root / "mpl"),
        "NEURO_NOTEBOOK_CONFIG": str(root / "configuration.json"),
        "NEURO_DEADLINE_MONOTONIC": str(deadline),
        "NEURO_ALLOW_BIOLOGICAL": "1" if args.allow_biological else "0",
    }
    stages = []
    started = time.monotonic()
    with tempfile.TemporaryDirectory(prefix="neuro-fresh-kernel-") as temporary:
        spec = Path(temporary) / "kernels/neuro-fresh"
        spec.mkdir(parents=True)
        (spec / "kernel.json").write_text(
            json.dumps(
                {
                    "argv": [
                        str(args.runtime_python),
                        "-m",
                        "ipykernel_launcher",
                        "-f",
                        "{connection_file}",
                    ],
                    "display_name": "Fresh supplied-input analysis",
                    "language": "python",
                    "env": environment,
                }
            )
        )
        # Keep explicitly supplied read-only template assets when tooling is an
        # overlay, while our temporary kernelspec remains first in discovery.
        os.environ["JUPYTER_PATH"] = os.pathsep.join(
            filter(None, (temporary, os.environ.get("JUPYTER_PATH", "")))
        )
        for name in args.notebooks:
            stage_start = time.monotonic()
            if stage_start >= deadline:
                raise TimeoutError("overall notebook deadline exceeded")
            source = args.notebook_directory / (name + ".ipynb")
            notebook = nbformat.read(source, as_version=4)
            notebook.metadata.pop(
                "fresh_demo_execution", None
            )  # Never carry demo execution evidence into a new supplied-data run.
            for cell in notebook.cells:
                if cell.cell_type == "code":
                    cell.outputs, cell.execution_count = [], None
            stage_dir = root / name
            environment["NEURO_NOTEBOOK_OUTPUT"] = str(stage_dir)
            spec_data = json.loads((spec / "kernel.json").read_text())
            spec_data["env"] = environment
            (spec / "kernel.json").write_text(json.dumps(spec_data))
            client = NotebookClient(
                notebook,
                timeout=max(1, int(deadline - time.monotonic())),
                kernel_name="neuro-fresh",
                allow_errors=False,
                resources={"metadata": {"path": str(root)}},
            )
            executed = stage_dir / (name + ".executed.ipynb")
            try:
                client.execute()
            finally:
                # Preserve failed cells/output privately too; never retry/resume this run.
                stage_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
                nbformat.write(notebook, executed)
                executed.chmod(0o600)
            cells = [c for c in notebook.cells if c.cell_type == "code"]
            if [c.execution_count for c in cells] != list(range(1, len(cells) + 1)):
                raise RuntimeError("fresh notebook execution order invalid")
            output_text = json.dumps([c.outputs for c in cells])
            if (
                any(o.output_type == "error" for c in cells for o in c.outputs)
                or "/home/" in output_text
                or "/Users/" in output_text
            ):
                raise RuntimeError("notebook output error/privacy failure")
            completion = json.loads((stage_dir / "completion.json").read_text())
            replay = verify_artifacts(
                stage_dir / "artifacts",
                expected_manifest_hash=completion["manifest_sha256"],
            )
            # Already authenticated before loading ID-bearing data for output privacy checks.
            import joblib

            data = joblib.load(stage_dir / "artifacts/source_data.joblib")
            kernel_runtime = joblib.load(
                stage_dir / "artifacts/kernel_runtime_final.joblib"
            )
            if (
                stable_kernel_identity(kernel_runtime)
                != config["expected_kernel_identity"]
            ):
                raise RuntimeError("actual final kernel code/runtime identity drifted")
            if name != NOTEBOOKS[2] and kernel_runtime["loaded_optional_modules"]:
                raise RuntimeError(
                    "construction/baseline notebook imported optional torch/CEBRA"
                )
            forbidden = (
                {s.source_id for s in data.sources}
                | {u.unit_id for u in data.units}
                | set(data.block_ids)
            )
            if any(identifier in output_text for identifier in forbidden):
                raise RuntimeError("raw identifier in rendered output")
            images = sum(
                "image/png" in o.get("data", {}) for c in cells for o in c.outputs
            )
            if images < 1:
                raise RuntimeError("no rendered figures")
            html = stage_dir / (name + ".html")
            html.write_text(HTMLExporter().from_notebook_node(notebook)[0])
            html.chmod(0o600)
            stages.append(
                {
                    "name": name,
                    "source_sha256": sha(source),
                    "executed_sha256": sha(executed),
                    "html_sha256": sha(html),
                    "code_cells": len(cells),
                    "rendered_figures": images,
                    "seconds": time.monotonic() - stage_start,
                    "replay": replay,
                    "kernel_runtime": kernel_runtime,
                    "development_identity": data.split_identity("development"),
                }
            )
            print(
                name
                + ": fresh execution, privacy check and loaded-model replay passed",
                flush=True,
            )
    if len({s["development_identity"] for s in stages}) != 1:
        raise RuntimeError("independently reconstructed development inputs differ")
    if set(NOTEBOOKS[1:]) <= set(args.notebooks):
        import joblib
        import numpy as np

        b = joblib.load(root / NOTEBOOKS[1] / "artifacts/fixed_development.joblib")
        c = joblib.load(
            root / NOTEBOOKS[2] / "artifacts/observed_fixed_development.joblib"
        )
        for attr in ("values", "targets", "exposure"):
            np.testing.assert_array_equal(getattr(b, attr), getattr(c, attr))
        if b.plan != c.plan:
            raise RuntimeError("cross-notebook observed development lineage differs")
    counts = {
        kind: sum(s["replay"]["fit_counts"][kind] for s in stages)
        for kind in ("pca", "logistic", "lda", "cebra", "optimizer_updates")
    }
    expected = expected_fit_counts(args.notebooks, config["execution"]["iterations"])
    if counts != expected:
        raise RuntimeError("aggregate fit grid differs from declared contract")
    import neuro

    package = Path(neuro.__file__).parent
    versions = {}
    for name in (
        "numpy",
        "scipy",
        "scikit-learn",
        "cebra",
        "torch",
        "joblib",
        "nbclient",
        "nbformat",
        "nbconvert",
    ):
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            versions[name] = "not installed"
    runtime = {
        "python": sys.version,
        "kernel_python": str(args.runtime_python.absolute()),
        "package_origin": str(package),
        "packages": versions,
    }
    receipt = {
        "status": "fresh-notebooks-and-fit-blocked-replay-passed",
        "mode": config["mode"],
        "configuration_sha256": file_hash(root / "configuration.json"),
        "runtime": runtime,
        "package_source_sha256": {p.name: sha(p) for p in package.glob("*.py")},
        "input_sha256": {k: v["sha256"] for k, v in config.get("inputs", {}).items()},
        "stages": stages,
        "selected_notebooks": args.notebooks,
        "fit_counts": counts,
        "seconds": time.monotonic() - started,
        "claim": "software smoke"
        if config["mode"] == "invented"
        else "exploratory historically exposed conditional assay",
    }
    write_private_json(root / "receipt.json", receipt)


def output_bytes(root):
    return sum(p.stat().st_size for p in root.rglob("*") if p.is_file())


def final_budget_check(root, *, deadline, limit):
    size = output_bytes(root)
    if size > limit or time.monotonic() >= deadline:
        raise RuntimeError("final output/deadline budget exceeded after worker exit")
    return size


def probe_kernel_identity(args, deadline):
    environment = {
        **os.environ,
        "PYTHONPATH": os.pathsep.join(args.dependency_path),
        "PYTHONNOUSERSITE": "1",
        "PYTHONDONTWRITEBYTECODE": "1",
        "OMP_NUM_THREADS": "2",
        "OPENBLAS_NUM_THREADS": "2",
        "MKL_NUM_THREADS": "2",
    }
    code = "import json; from neuro.notebook_artifacts import runtime_identity,stable_kernel_identity; print(json.dumps(stable_kernel_identity(runtime_identity()),sort_keys=True))"
    result = subprocess.run(
        [str(args.runtime_python.absolute()), "-c", code],
        env=environment,
        capture_output=True,
        text=True,
        check=True,
        timeout=max(0.001, deadline - time.monotonic()),
    )
    return json.loads(result.stdout)


def execute(args):
    from neuro.notebook_inputs import demo_configuration

    if not 0 < args.timeout_seconds <= 5400 or not 0 < args.memory_gib <= 6:
        raise ValueError("deadline<=90min and aggregate memory<=6GiB required")
    os.umask(0o077)
    args.output = args.output.resolve()
    args.output.mkdir(mode=0o700, parents=True, exist_ok=False)
    config = (
        demo_configuration()
        if args.manifest is None
        else json.loads(args.manifest.read_text())
    )
    if args.manifest is not None:
        if not args.manifest_sha256 or sha(args.manifest) != args.manifest_sha256:
            raise ValueError("supplied configuration requires exact manifest SHA256")
        config["manifest_directory"] = str(args.manifest.resolve().parent)
    if config["mode"] == "place195":
        if not args.allow_biological or not config.get("biological_execution"):
            raise PermissionError("biological execution is not authorized")
        expected = {
            "iterations": 1000,
            "train_rows_per_condition": 16,
            "development_rows_per_condition": 8,
            "seeds": [0, 1],
            "subset_seed": 20261023,
            "permutation_seed": 50000,
            "pca_components": 8,
            "hidden": 32,
            "output_dimension": 8,
            "batch_size": 256,
            "learning_rate": 0.0003,
            "logistic_C": 0.01,
            "logistic_max_iter": 2000,
        }
        if config["execution"] != expected or config["landmarks"] != list(range(1, 7)):
            raise ValueError("biological configuration differs from frozen protocol")
    if not 0 < args.output_limit_bytes <= 2 * 1024**3:
        raise ValueError("output limit must be positive and <=2GiB")
    deadline = time.monotonic() + args.timeout_seconds
    actual_kernel = probe_kernel_identity(args, deadline)
    expected_kernel = config.get("expected_kernel_identity")
    if config["mode"] == "place195" and expected_kernel is None:
        raise ValueError(
            "real execution requires reviewed pinned expected_kernel_identity"
        )
    if expected_kernel is not None and actual_kernel != expected_kernel:
        raise ValueError("probed kernel differs from reviewed expected identity")
    config["expected_kernel_identity"] = actual_kernel
    write(args.output / "configuration.json", config)
    env = {
        **os.environ,
        "NEURO_DEADLINE_MONOTONIC": str(deadline),
        "OMP_NUM_THREADS": "2",
        "OPENBLAS_NUM_THREADS": "2",
        "MKL_NUM_THREADS": "2",
        "PYTHONDONTWRITEBYTECODE": "1",
    }
    command = [
        sys.executable,
        str(Path(__file__).resolve()),
        "--worker",
        "--output",
        str(args.output),
        "--runtime-python",
        str(args.runtime_python.absolute()),
        "--notebook-directory",
        str(args.notebook_directory.resolve()),
    ]
    command.extend(["--notebooks", *args.notebooks])
    if args.allow_biological:
        command.append("--allow-biological")
    for path in args.dependency_path:
        command.extend(["--dependency-path", path])
    peak, size_peak = 0, 0
    with (args.output / "execution.log").open("x") as log:
        process = subprocess.Popen(
            command,
            env=env,
            stdout=log,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
        try:
            while process.poll() is None:
                _, rss = descendants(os.getpid())
                peak = max(peak, rss)
                size_peak = max(size_peak, output_bytes(args.output))
                if (
                    time.monotonic() >= deadline
                    or rss > args.memory_gib * 1024**3
                    or size_peak > args.output_limit_bytes
                ):
                    raise RuntimeError(
                        "owned execution deadline/memory/output budget exceeded"
                    )
                time.sleep(0.5)
            if process.returncode:
                raise RuntimeError(
                    "fresh notebook worker failed; inspect protected execution.log"
                )
            size_peak = max(
                size_peak,
                final_budget_check(
                    args.output, deadline=deadline, limit=args.output_limit_bytes
                ),
            )
            write(
                args.output / "resources.json",
                {
                    "peak_owned_rss_bytes": peak,
                    "peak_output_bytes": size_peak,
                    "deadline_seconds": args.timeout_seconds,
                    "memory_limit_gib": args.memory_gib,
                    "output_limit_bytes": args.output_limit_bytes,
                    "threads": 2,
                    "sequential_kernels": True,
                    "observation": "RSS/disk sampled every0.5s; final disk/deadline checked after exit and receipt write; not a hard memory cap",
                },
            )
            final_budget_check(
                args.output, deadline=deadline, limit=args.output_limit_bytes
            )
        except BaseException as error:
            if process.poll() is None:
                terminate(process)
            write(
                args.output / "failure.json",
                {
                    "error_type": type(error).__name__,
                    "message": str(error),
                    "peak_owned_rss_bytes": peak,
                    "peak_output_bytes": size_peak,
                },
            )
            raise
    print("Fresh notebook execution/replay passed; protected receipts written.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--manifest-sha256")
    parser.add_argument("--allow-biological", action="store_true")
    parser.add_argument("--timeout-seconds", type=float, default=5400)
    parser.add_argument("--memory-gib", type=float, default=6)
    parser.add_argument(
        "--output-limit-bytes",
        type=int,
        default=2 * 1024**3,
        help="Can lower, never exceed2GiB; also used by budget regression tests",
    )
    parser.add_argument("--runtime-python", type=Path, default=Path(sys.executable))
    parser.add_argument("--dependency-path", action="append", default=[])
    parser.add_argument(
        "--notebook-directory",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "notebooks",
    )
    parser.add_argument(
        "--notebooks", nargs="+", choices=NOTEBOOKS, default=list(NOTEBOOKS)
    )
    parser.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    args.dependency_path = [str(Path(p).resolve()) for p in args.dependency_path]
    if args.worker:
        worker(args)
    else:
        execute(args)


if __name__ == "__main__":
    main()
