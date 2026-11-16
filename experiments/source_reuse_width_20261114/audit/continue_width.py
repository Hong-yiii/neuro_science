"""Reviewed continuation of only unattempted width cases after a kernel handoff error.

This is not an automatic resume mode. It accepts only the exact authenticated
32-case boundary, preserves it, and runs the existing width notebook once.
"""

from __future__ import annotations
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import nbformat
from nbclient import NotebookClient
from nbconvert import HTMLExporter

from .. import study
from ..build_notebooks import make_notebook
from ..run import ROOT, assert_pins, cgroup, validate_gate


def write_kernel(out, name, env):
    kernel = out / "jupyter/kernels" / name
    kernel.mkdir(parents=True, exist_ok=False)
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
            display_name=name,
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
    return kernel / "kernel.json"


def smoke():
    """Real fresh-kernel handoff with invented strings only; no data or fits."""
    with tempfile.TemporaryDirectory(prefix="neuro-two-kernel-smoke-") as directory:
        out = Path(directory)
        digests = []
        for index in (0, 1):
            name = "invented-handoff-" + str(index)
            path = write_kernel(
                out, name, dict(NEURO_BRIDGE_SHA256=str(index), PYTHONNOUSERSITE="1")
            )
            digests.append((path, study.sha(path)))
            notebook = nbformat.v4.new_notebook(
                cells=[
                    nbformat.v4.new_code_cell(
                        'import os\nassert os.environ["NEURO_BRIDGE_SHA256"] == '
                        + repr(str(index))
                        + '\nprint("invented handoff '
                        + str(index)
                        + ' passed")'
                    )
                ]
            )
            NotebookClient(notebook, kernel_name=name, timeout=60).execute()
            assert notebook.cells[0].execution_count == 1
        assert all(study.sha(path) == digest for path, digest in digests)
    print(
        "Two fresh kernels, separate immutable specs, authenticated handoff environment: passed; no biological reads or fits."
    )


def authenticate_parent(parent, digest):
    assert study.sha(parent / "receipt.json") == digest
    receipt = json.loads((parent / "receipt.json").read_text())
    assert receipt["status"] == "failed" and receipt["mode"] == "train"
    for name, value in receipt["files_sha256"].items():
        path = (parent / name).resolve()
        assert path.is_relative_to(parent) and study.sha(path) == value, name
    cfg = json.loads((parent / "configuration.json").read_text())
    assert cfg == study.configuration(cfg["design"])
    pins = json.loads((parent / "code-pins.json").read_text())
    assert_pins(pins)
    expected = [c for c in study.schedule() if c["arm"] in study.PART_ARMS["reuse"]]
    assert {p.name for p in (parent / "cases").iterdir()} == {c["id"] for c in expected}
    events = [
        json.loads(line)
        for line in (parent / "attempt-log.jsonl").read_text().splitlines()
    ]
    assert len(events) == 64
    for case in expected:
        assert [r["status"] for r in events if r["id"] == case["id"]] == [
            "started",
            "completed",
        ]
        done = json.loads(
            (parent / "cases" / case["id"] / "completion.json").read_text()
        )
        assert all(done[k] == v for k, v in case.items())
    assert not any(
        (parent / name).exists()
        for name in (
            "aggregates_width",
            "attempts_width.json",
            "actual-fit-counts-width.json",
            "population_width_20261114.executed.ipynb",
        )
    )
    counts = json.loads((parent / "actual-fit-counts-reuse.json").read_text())
    assert counts == {k: v * 32 // 48 for k, v in cfg["expected_fit_counts"].items()}
    notebook = nbformat.read(
        parent / "source_reuse_20261114.executed.ipynb", as_version=4
    )
    assert [(c.cell_type, c.source) for c in notebook.cells] == [
        (c.cell_type, c.source) for c in make_notebook("reuse").cells
    ]
    cells = [c for c in notebook.cells if c.cell_type == "code"]
    assert [c.execution_count for c in cells] == list(range(1, len(cells) + 1))
    assert not any(o.output_type == "error" for c in cells for o in c.outputs)
    bridge = json.loads((parent / "bridge-receipt.json").read_text())
    assert all(
        study.sha(parent / name) == value
        for name, value in bridge["files_sha256"].items()
    )
    gates = json.loads((parent / "prefit-evidence/gate-pins.json").read_text())
    for kind in ("benchmark", "preflight"):
        validate_gate(
            parent / "prefit-evidence" / (kind + ".json"),
            gates[kind + "_sha256"],
            kind,
            parent,
        )
    assert receipt["resources"]["seconds"] + 7200 < cfg["limits"]["run_seconds"]
    return receipt, cfg, pins


def continuation(parent, out, parent_hash):
    parent = parent.resolve()
    out = out.resolve()
    if out.is_relative_to(parent) or parent.is_relative_to(out):
        raise ValueError("continuation must use a separate sibling output directory")
    original, cfg, pins = authenticate_parent(parent, parent_hash)
    cg, limits = cgroup()
    out.mkdir(parents=True, exist_ok=False, mode=0o700)
    started = time.monotonic()
    status = "failed"
    try:
        preserved = {}
        for name, digest in original["files_sha256"].items():
            target_name = (
                "parent-evidence/" + name
                if name in ("resources.json", "source-state.json", "attempt-log.jsonl")
                else name
            )
            destination = out / target_name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(parent / name, destination)
            assert study.sha(destination) == digest
            preserved[name] = target_name
        shutil.copyfile(parent / "receipt.json", out / "parent-evidence/receipt.json")
        shutil.copyfile(parent / "attempt-log.jsonl", out / "attempt-log.jsonl")
        amendment = (
            ROOT
            / "docs/experiments/source-reuse-width-20261114/continuation-20261115.md"
        )
        study.write_json(
            out / "continuation.json",
            dict(
                parent_receipt_sha256=parent_hash,
                inherited_cases=32,
                new_cases=16,
                total_unique_cases=48,
                hard_continuation_seconds=7200,
                reason="exclusive-create kernel specification handoff failure after complete first notebook; no width case attempted",
                inherited_path_mapping=preserved,
                amendment_sha256=study.sha(amendment),
            ),
        )
        shutil.copyfile(amendment, out / "parent-evidence/continuation-amendment.md")
        own_pins = {
            str(Path(__file__).relative_to(ROOT)): study.sha(Path(__file__)),
            str(amendment.relative_to(ROOT)): study.sha(amendment),
        }
        study.write_json(out / "continuation-source-pins.json", own_pins)
        for relative in own_pins:
            target = out / "continuation-source-snapshot" / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, target)
        study.write_json(
            out / "source-state.json",
            dict(
                execution="bounded width-only continuation",
                parent_receipt_sha256=parent_hash,
                code_sha256=pins,
                continuation_code_sha256=own_pins,
                git_head=subprocess.check_output(
                    ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
                ).strip(),
                git_status=subprocess.check_output(
                    ["git", "status", "--short"], cwd=ROOT, text=True
                ),
            ),
        )
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
            "NEURO_BRIDGE_SHA256": study.sha(out / "bridge-receipt.json"),
        }
        write_kernel(out, "source-reuse-width-continuation", env)
        notebook = make_notebook("width")
        destination = out / "population_width_20261114.executed.ipynb"
        try:
            NotebookClient(
                notebook,
                kernel_name="source-reuse-width-continuation",
                timeout=7200,
                resources={"metadata": {"path": str(ROOT)}},
            ).execute()
        finally:
            nbformat.write(notebook, destination)
        cells = [c for c in notebook.cells if c.cell_type == "code"]
        assert [c.execution_count for c in cells] == list(range(1, len(cells) + 1))
        html, _ = HTMLExporter().from_notebook_node(notebook)
        destination.with_suffix(".html").write_text(html)
        counts = {k: 0 for k in cfg["expected_fit_counts"]}
        for part in ("reuse", "width"):
            for k, v in json.loads(
                (out / f"actual-fit-counts-{part}.json").read_text()
            ).items():
                counts[k] += v
        assert counts == cfg["expected_fit_counts"]
        study.write_json(out / "actual-fit-counts.json", counts)
        assert_pins(pins)
        assert_pins(own_pins)
        assert (
            study.sha(out / "parent-evidence/continuation-amendment.md")
            == own_pins[str(amendment.relative_to(ROOT))]
        )
        expected_ids = {case["id"] for case in study.schedule()}
        assert {p.name for p in (out / "cases").iterdir()} == expected_ids
        events = [
            json.loads(line)
            for line in (out / "attempt-log.jsonl").read_text().splitlines()
        ]
        assert len(events) == 96
        assert all(
            [r["status"] for r in events if r["id"] == cid] == ["started", "completed"]
            for cid in expected_ids
        )
        for name, target in preserved.items():
            assert study.sha(out / target) == original["files_sha256"][name]
        assert study.sha(parent / "receipt.json") == parent_hash
        for name, digest in original["files_sha256"].items():
            assert study.sha(parent / name) == digest
        status = "completed"
        print(
            "Completed16new width cases;32inherited cases remain byte-identical;48unique cases total.",
            flush=True,
        )
    finally:
        own = dict(
            status=status,
            seconds=time.monotonic() - started,
            limits=limits,
            memory_peak_bytes=int((cg / "memory.peak").read_text()),
            memory_events=(cg / "memory.events").read_text(),
            cpu_stat=(cg / "cpu.stat").read_text(),
        )
        study.write_json(out / "continuation-resources.json", own)
        resources = {
            **own,
            "seconds": original["resources"]["seconds"] + own["seconds"],
            "memory_peak_bytes": max(
                own["memory_peak_bytes"], original["resources"]["memory_peak_bytes"]
            ),
            "resource_scope": "sum of original execution and continuation seconds; maximum phase peak; original counters preserved separately",
        }
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
                status=status,
                mode="train",
                execution="reviewed composite:32inherited fresh cases +16unattempted fresh cases",
                parent_receipt_sha256=parent_hash,
                files_sha256=files,
                resources=resources,
            ),
        )
        print(
            "Continuation",
            status,
            "total execution seconds",
            resources["seconds"],
            flush=True,
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--parent", type=Path)
    parser.add_argument("--parent-sha256")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    os.umask(0o077)
    if args.smoke:
        smoke()
    elif all((args.parent, args.parent_sha256, args.output)):
        continuation(args.parent, args.output, args.parent_sha256)
    else:
        parser.error("parent, pinned receipt hash and fresh output are required")
