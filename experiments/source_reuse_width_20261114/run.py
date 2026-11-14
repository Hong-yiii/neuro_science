"""Bounded invented benchmark, biological preflight or two-notebook execution."""

from __future__ import annotations
import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

os.environ["CUDA_VISIBLE_DEVICES"] = ""
from . import study
from scripts.run_population_grid_study import cgroup

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent


def numerical_hashes():
    files = sorted((ROOT / "src/neuro").rglob("*.py")) + [
        HERE / "study.py",
        HERE / "test_study.py",
        Path(__file__),
        ROOT / "scripts/run_population_grid_study.py",
    ]
    return {str(p.relative_to(ROOT)): study.sha(p) for p in files}


def code_hashes():
    files = sorted(HERE.glob("*.py")) + [
        ROOT / study.DESIGN_PATH,
        ROOT / "docs/experiments/source-reuse-width-20261114/protocol.md",
        ROOT / "scripts/source_support_report.py",
    ]
    return {
        **numerical_hashes(),
        **{str(p.relative_to(ROOT)): study.sha(p) for p in files},
    }


def assert_pins(pins):
    for path, digest in pins.items():
        if study.sha(ROOT / path) != digest:
            raise ValueError("pinned source changed: " + path)


def gate_contract(out):
    from neuro.notebook_artifacts import runtime_identity, stable_kernel_identity

    return dict(
        numerical_code_sha256=numerical_hashes(),
        configuration_sha256=study.sha(out / "configuration.json"),
        design_sha256=study.sha(ROOT / study.DESIGN_PATH),
        runtime_stable_identity=stable_kernel_identity(runtime_identity()),
    )


def check_contract(out, contract):
    if gate_contract(out) != contract:
        raise ValueError("execution source/configuration/runtime changed during gate")


def benchmark(out, config):
    from .test_study import fixture

    contract = gate_contract(out)
    study.write_json(out / "execution-contract.json", contract)
    data, meta, design = fixture(units=83, blocks=20)
    plans = study.paired_plans(data, meta, design, seed=0)
    study.verify_plans(plans, numerical_rank=True)
    accounting = study.GridFitAccounting(cebra=True).start()
    started = time.monotonic()
    try:
        study.train_case(
            {
                "id": "invented_full_width",
                "arm": "benchmark",
                "world": "invented",
                "seed": 0,
            },
            *plans["Wfull"],
            meta=meta,
            config=config,
            run_root=out,
        )
    finally:
        counts = accounting.stop()
        study.write_json(out / "actual-fit-counts.json", counts)
    expected = {k: v // 48 for k, v in config["expected_fit_counts"].items()}
    if counts != expected:
        raise ValueError("benchmark actual fit count mismatch")
    duration = time.monotonic() - started
    budget = 48 * duration * 1.25 + 900
    if budget >= config["limits"]["run_seconds"]:
        raise ValueError("benchmark exceeds conservative run headroom")
    check_contract(out, contract)
    receipt = dict(
        status="passed",
        classification="invented software benchmark",
        case_seconds=duration,
        conservative_budget_seconds=budget,
        training_shape=[144, 83, 10],
        development_shape=[72, 83, 10],
        fit_counts=counts,
        **contract,
    )
    study.write_json(out / "benchmark.json", receipt)
    print(
        json.dumps({k: v for k, v in receipt.items() if k not in contract}), flush=True
    )


def preflight(out, config):
    from neuro.studies.population_models import frozen_models

    contract = gate_contract(out)
    study.write_json(out / "execution-contract.json", contract)
    with frozen_models():
        meta = study.metadata(ROOT / "data/cue-source-v1")
        data, audit = study.reconstruct(
            ROOT / "data/cue-source-v1", meta, config["design"]
        )
        records = []
        for world, seeds in [("observed", (0, 1, 2))] + [
            (f"permuted{p}", (0,)) for p in study.PERMUTATIONS
        ]:
            permutation = None if world == "observed" else int(world[8:])
            for seed in seeds:
                plans = study.paired_plans(
                    data, meta, config["design"], seed=seed, permutation=permutation
                )
                records.extend(
                    dict(world=world, seed=seed, **r)
                    for r in study.verify_plans(plans, numerical_rank=True)
                )
        if len(records) != 48:
            raise ValueError("incomplete preflight schedule")
    study.write_json(out / "reconstruction-audit.json", audit)
    study.write_json(out / "rank-and-plan-checks.json", records)
    check_contract(out, contract)
    study.write_json(
        out / "preflight.json",
        dict(
            status="passed",
            cases=48,
            new_fits=0,
            minimum_rank=min(r["training_rank"] for r in records),
            rank_checks_sha256=study.sha(out / "rank-and-plan-checks.json"),
            **contract,
        ),
    )
    print(
        "All48scheduled plans passed source/array/rank checks; zero fits.", flush=True
    )


def validate_gate(path, digest, kind, out):
    if study.sha(path) != digest:
        raise ValueError(kind + " receipt identity changed")
    gate = json.loads(path.read_text())
    if gate["status"] != "passed":
        raise ValueError(kind + " gate did not pass")
    assert_pins(gate["numerical_code_sha256"])
    if any(gate.get(k) != v for k, v in gate_contract(out).items()):
        raise ValueError(
            kind + " differs from start-of-run source/configuration/runtime"
        )
    return gate


def execute(out, config, args):
    import nbformat
    from nbclient import NotebookClient
    from nbconvert import HTMLExporter
    from .build_notebooks import make_notebook

    gate = validate_gate(
        args.benchmark_receipt, args.benchmark_sha256, "benchmark", out
    )
    if gate["conservative_budget_seconds"] >= config["limits"]["run_seconds"]:
        raise ValueError("benchmark budget exceeds run ceiling")
    gate = validate_gate(
        args.preflight_receipt, args.preflight_sha256, "preflight", out
    )
    if (
        gate["cases"] != 48
        or gate["minimum_rank"] < 7
        or gate["design_sha256"] != study.sha(ROOT / study.DESIGN_PATH)
    ):
        raise ValueError("preflight does not cover frozen design")
    if gate["rank_checks_sha256"] != study.sha(
        args.preflight_receipt.parent / "rank-and-plan-checks.json"
    ):
        raise ValueError("preflight rank/plan table identity changed")
    pins = code_hashes()
    study.write_json(out / "code-pins.json", pins)
    evidence = out / "prefit-evidence"
    evidence.mkdir()
    for path in (
        args.benchmark_receipt,
        args.preflight_receipt,
        args.preflight_receipt.parent / "rank-and-plan-checks.json",
    ):
        shutil.copyfile(path, evidence / path.name)
    study.write_json(
        evidence / "gate-pins.json",
        dict(
            benchmark_sha256=args.benchmark_sha256,
            preflight_sha256=args.preflight_sha256,
        ),
    )
    for relative in pins:
        destination = out / "source-snapshot" / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / relative, destination)
    env = {
        **os.environ,
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
        "CUDA_VISIBLE_DEVICES": "",
        "MPLCONFIGDIR": str(out / "mpl"),
        "IPYTHONDIR": str(out / "ipython"),
        "NEURO_PROJECT_ROOT": str(ROOT),
        "NEURO_REUSE_RUN": str(out),
        "NEURO_REUSE_ALLOW_BIOLOGICAL": "1",
    }
    kernel = out / "jupyter/kernels/source-reuse-width"
    kernel.mkdir(parents=True)
    study.write_json(
        kernel / "kernel.json",
        dict(
            argv=[
                sys.executable,
                "-m",
                "ipykernel_launcher",
                "-f",
                "{connection_file}",
            ],
            display_name="Bounded source reuse / width",
            language="python",
            env=env,
        ),
    )
    os.environ["JUPYTER_PATH"] = os.pathsep.join(
        (
            str(out / "jupyter"),
            str(ROOT / "scratch/endpoint-notebook-runtime/share/jupyter"),
        )
    )
    os.environ["JUPYTER_DATA_DIR"] = str(out / "jupyter")
    counts = {k: 0 for k in config["expected_fit_counts"]}
    for part in ("reuse", "width"):
        if part == "width":
            env["NEURO_BRIDGE_SHA256"] = study.sha(out / "bridge-receipt.json")
            spec = json.loads((kernel / "kernel.json").read_text())
            spec["env"] = env
            study.write_json(kernel / "kernel.json", spec)
        notebook = make_notebook(part)
        destination = out / (
            {"reuse": "source_reuse_20261114", "width": "population_width_20261114"}[
                part
            ]
            + ".executed.ipynb"
        )
        try:
            NotebookClient(
                notebook,
                timeout=config["limits"]["run_seconds"],
                kernel_name="source-reuse-width",
                resources={"metadata": {"path": str(ROOT)}},
            ).execute()
        finally:
            nbformat.write(notebook, destination)
        cells = [c for c in notebook.cells if c.cell_type == "code"]
        if [c.execution_count for c in cells] != list(range(1, len(cells) + 1)):
            raise ValueError("notebook cell execution incomplete")
        html, _ = HTMLExporter().from_notebook_node(notebook)
        destination.with_suffix(".html").write_text(html)
        actual = json.loads((out / ("actual-fit-counts-" + part + ".json")).read_text())
        for key, value in actual.items():
            counts[key] += value
        if part == "reuse":
            bridge_files = sorted(
                p
                for p in (out / "cases").rglob("*")
                if p.is_file() and p.parent.name.endswith("_B3")
            )
            bridge_files += sorted((out / "aggregates_reuse").glob("*"))
            study.write_json(
                out / "bridge-receipt.json",
                dict(
                    classification="authenticated shared B3 evidence; no refit",
                    files_sha256={
                        str(p.relative_to(out)): study.sha(p) for p in bridge_files
                    },
                ),
            )
        assert_pins(pins)
    if counts != config["expected_fit_counts"]:
        raise ValueError("actual total fit accounting mismatch")
    study.write_json(out / "actual-fit-counts.json", counts)
    print(
        "Completed both experiment notebooks,48unique cases,2448fits,96000updates.",
        flush=True,
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode", choices=("benchmark", "preflight", "train"), required=True
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--benchmark-receipt", type=Path)
    parser.add_argument("--benchmark-sha256")
    parser.add_argument("--preflight-receipt", type=Path)
    parser.add_argument("--preflight-sha256")
    args = parser.parse_args()
    os.umask(0o077)
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    cg, limits = cgroup()
    started = time.monotonic()
    from neuro.notebook_artifacts import runtime_identity

    design = json.loads((ROOT / study.DESIGN_PATH).read_text())
    cfg = study.configuration(design)
    study.write_json(out / "configuration.json", cfg)
    study.write_json(out / "runtime.json", runtime_identity())
    study.write_json(
        out / "source-state.json",
        dict(
            code_sha256=code_hashes(),
            git_head=subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
            ).strip(),
            git_status=subprocess.check_output(
                ["git", "status", "--short"], cwd=ROOT, text=True
            ),
        ),
    )
    status = "failed"
    try:
        if args.mode == "benchmark":
            benchmark(out, cfg)
        elif args.mode == "preflight":
            preflight(out, cfg)
        else:
            if not all(
                (
                    args.benchmark_receipt,
                    args.benchmark_sha256,
                    args.preflight_receipt,
                    args.preflight_sha256,
                )
            ):
                raise ValueError("pinned benchmark and preflight receipts required")
            execute(out, cfg, args)
        status = "completed"
    finally:
        resources = dict(
            status=status,
            seconds=time.monotonic() - started,
            limits=limits,
            memory_peak_bytes=int((cg / "memory.peak").read_text()),
            memory_events=(cg / "memory.events").read_text(),
            cpu_stat=(cg / "cpu.stat").read_text(),
        )
        study.write_json(out / "resources.json", resources)
        files = {
            str(p.relative_to(out)): study.sha(p)
            for p in sorted(out.rglob("*"))
            if p.is_file()
            and not any(
                x in p.parts for x in ("mpl", "ipython", "jupyter", "__pycache__")
            )
        }
        study.write_json(
            out / "receipt.json",
            dict(
                status=status, mode=args.mode, files_sha256=files, resources=resources
            ),
        )
        print(
            "Run",
            status,
            "peakMiB",
            round(resources["memory_peak_bytes"] / 1024**2, 1),
            flush=True,
        )


if __name__ == "__main__":
    main()
