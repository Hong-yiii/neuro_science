"""One bounded task-owned benchmark or fresh-kernel study, no retry/resume."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

from neuro.studies import source_support_ablation as study

ROOT = Path(__file__).resolve().parents[1]


def cgroup():
    entry = next(
        line.split("::", 1)[1]
        for line in Path("/proc/self/cgroup").read_text().splitlines()
        if "::" in line
    )
    root = Path("/sys/fs/cgroup") / entry.lstrip("/")
    limits = {
        name: (root / name).read_text().strip()
        for name in ("memory.max", "memory.swap.max", "cpu.max")
    }
    quota, period = limits["cpu.max"].split()
    if limits["memory.max"] == "max" or int(limits["memory.max"]) > 4 * 1024**3:
        raise RuntimeError("hard <=4GiB cgroup memory limit required")
    if (
        limits["memory.swap.max"] != "0"
        or quota == "max"
        or int(quota) / int(period) > 2
    ):
        raise RuntimeError("zero swap and <=two-core CPU quota required")
    return root, limits


def code_hashes():
    files = list((ROOT / "src/neuro").rglob("*.py"))
    files += [
        Path(__file__),
        ROOT / "scripts/source_support_report.py",
        ROOT / "scripts/build_source_support_notebook.py",
        ROOT / "docs/source-support-protocol-20261110.md",
    ]
    return {str(p.relative_to(ROOT)): study.sha(p) for p in sorted(files) if p.exists()}


def benchmark(out):
    from neuro.notebook_artifacts import FitAccounting
    from neuro.notebook_inputs import demo_configuration, inspect_inputs, load_inputs
    from neuro.pseudopopulation import sample_plan

    cfg = demo_configuration()
    cfg.update(
        demo_units=144, demo_blocks=43, demo_bins=10, landmarks=[1, 2, 3, 4, 5, 6]
    )
    data, _ = load_inputs(inspect_inputs(cfg))
    meta = {
        "aliases": {b: f"B{i}" for i, b in enumerate(data.block_ids)},
        "source_aliases": {s.source_id: f"T{i}" for i, s in enumerate(data.sources)},
    }
    train = sample_plan(data, split_id="train", rows_per_condition=16, seed=0)
    dev = sample_plan(data, split_id="development", rows_per_condition=8, seed=0)
    accounting = FitAccounting(cebra=True).start()
    started = time.monotonic()
    try:
        study.train_case(
            {
                "id": "invented_full_size",
                "arm": "benchmark",
                "world": "invented",
                "seed": 0,
            },
            data,
            train,
            dev,
            meta=meta,
            config=study.frozen_configuration(),
            run_root=out,
        )
    finally:
        counts = accounting.stop()
        study.write_json(out / "actual-fit-counts.json", counts)
    expected = {
        "cebra": 1,
        "pca": 1,
        "logistic": 9,
        "lda": 3,
        "optimizer_updates": 1000,
    }
    if counts != expected:
        raise RuntimeError("benchmark fit accounting mismatch")
    duration = time.monotonic() - started
    budget = 39 * duration * 1.25 + 900
    if budget >= 5400:
        raise RuntimeError("benchmark lacks declared runtime headroom")
    receipt = {
        "status": "passed",
        "classification": "invented software benchmark",
        "training_shape": [480, 144, 10],
        "development_shape": [240, 144, 10],
        "fit_counts": counts,
        "case_seconds": duration,
        "conservative_budget_seconds": budget,
    }
    study.write_json(out / "benchmark.json", receipt)
    print(json.dumps(receipt), flush=True)


def execute(out, benchmark_path, benchmark_hash):
    import nbformat
    from nbclient import NotebookClient
    from nbconvert import HTMLExporter
    from scripts.build_source_support_notebook import make_notebook

    if study.sha(benchmark_path) != benchmark_hash:
        raise ValueError("benchmark receipt pin changed")
    if json.loads(benchmark_path.read_text())["status"] != "passed":
        raise ValueError("successful benchmark required")
    pins = code_hashes()
    study.write_json(out / "code-pins.json", pins)
    study.write_json(out / "configuration.json", study.frozen_configuration())
    env = {
        "PYTHONPATH": os.pathsep.join(
            (
                str(ROOT / "src"),
                str(ROOT),
                str(ROOT / "scratch/v6-v9-runtime/lib/python3.13/site-packages"),
            )
        ),
        "PYTHONNOUSERSITE": "1",
        "PYTHONDONTWRITEBYTECODE": "1",
        "OMP_NUM_THREADS": "2",
        "OPENBLAS_NUM_THREADS": "2",
        "MKL_NUM_THREADS": "2",
        "MPLBACKEND": "Agg",
        "MPLCONFIGDIR": str(out / "mpl"),
        "IPYTHONDIR": str(out / "ipython"),
        "NEURO_PROJECT_ROOT": str(ROOT),
        "NEURO_SUPPORT_RUN": str(out),
        "NEURO_SUPPORT_ALLOW_BIOLOGICAL": "1",
    }
    kernel = out / "jupyter/kernels/source-support"
    kernel.mkdir(parents=True, mode=0o700)
    study.write_json(
        kernel / "kernel.json",
        {
            "argv": [
                sys.executable,
                "-m",
                "ipykernel_launcher",
                "-f",
                "{connection_file}",
            ],
            "display_name": "Bounded source-support study",
            "language": "python",
            "env": env,
        },
    )
    os.environ["JUPYTER_PATH"] = os.pathsep.join(
        (
            str(out / "jupyter"),
            str(ROOT / "scratch/endpoint-notebook-runtime/share/jupyter"),
        )
    )
    notebook = make_notebook()
    nbformat.write(notebook, out / "source_support.source.ipynb")
    client = NotebookClient(
        notebook,
        timeout=5100,
        kernel_name="source-support",
        allow_errors=False,
        resources={"metadata": {"path": str(ROOT)}},
    )
    try:
        client.execute()
    finally:
        nbformat.write(notebook, out / "source_support.executed.ipynb")
        (out / "source_support.executed.ipynb").chmod(0o600)
    if pins != code_hashes():
        raise ValueError("source code changed during execution")
    cells = [c for c in notebook.cells if c.cell_type == "code"]
    if [c.execution_count for c in cells] != list(range(1, len(cells) + 1)):
        raise ValueError("notebook execution order mismatch")
    html, _ = HTMLExporter().from_notebook_node(notebook)
    (out / "source_support.notebook.html").write_text(html)
    (out / "source_support.notebook.html").chmod(0o600)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--benchmark", action="store_true")
    parser.add_argument("--benchmark-receipt", type=Path)
    parser.add_argument("--benchmark-sha256")
    args = parser.parse_args()
    os.umask(0o077)
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False, mode=0o700)
    started = time.monotonic()
    cg, limits = cgroup()
    from neuro.notebook_artifacts import runtime_identity

    study.write_json(out / "runtime.json", runtime_identity())
    study.write_json(
        out / "source-state.json",
        {
            "code_sha256": code_hashes(),
            "git_head": subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
            ).strip(),
            "git_status": subprocess.check_output(
                ["git", "status", "--short"], cwd=ROOT, text=True
            ),
        },
    )
    status = "failed"
    try:
        if args.benchmark:
            benchmark(out)
        else:
            if not args.benchmark_receipt or not args.benchmark_sha256:
                raise ValueError("pinned benchmark receipt required")
            execute(out, args.benchmark_receipt.resolve(), args.benchmark_sha256)
        status = "completed"
    finally:
        resources = {
            "status": status,
            "seconds": time.monotonic() - started,
            "limits": limits,
            "memory_peak_bytes": int((cg / "memory.peak").read_text()),
            "memory_events": (cg / "memory.events").read_text(),
            "cpu_stat": (cg / "cpu.stat").read_text(),
        }
        study.write_json(out / "resources.json", resources)
        files = {
            str(p.relative_to(out)): study.sha(p)
            for p in sorted(out.rglob("*"))
            if p.is_file()
            and not any(x in p.parts for x in ("mpl", "ipython", "jupyter"))
        }
        study.write_json(
            out / "receipt.json",
            {
                "status": status,
                "files_sha256": files,
                "resources": resources,
                "classification": "invented benchmark"
                if args.benchmark
                else "exploratory biological study",
            },
        )
        print(
            "Run",
            status,
            "peak MiB",
            round(resources["memory_peak_bytes"] / 1024**2, 1),
            flush=True,
        )


if __name__ == "__main__":
    main()
