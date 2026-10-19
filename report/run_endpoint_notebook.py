"""Execute the saved-artifact notebook in a fresh native kernel, then export HTML.

Run with the compatible notebook environment; no server/global kernelspec is used.
Private artifacts are required. Does not install packages or modify saved runs.
"""

import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory

# Notebook tooling is isolated from the project's scientific/LSP environment.
import nbformat  # pyright: ignore[reportMissingImports]
from nbclient import NotebookClient  # pyright: ignore[reportMissingImports]
from nbconvert import HTMLExporter  # pyright: ignore[reportMissingImports]

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = ROOT / "report/endpoint_walkthrough.ipynb"
OUTPUT = ROOT / "outputs/endpoint-notebook/endpoint_walkthrough.html"


def execute():
    notebook = nbformat.read(NOTEBOOK, as_version=4)
    for cell in notebook.cells:
        if cell.cell_type == "code":
            cell.outputs = []
            cell.execution_count = None
    nbformat.validate(notebook)
    paths = [str(ROOT / "src"), str(ROOT / "report")]
    retained = ROOT / "scratch/v6-v9-runtime/lib/python3.13/site-packages"
    if retained.is_dir():
        paths.append(str(retained))
    environment = {
        "PYTHONPATH": os.pathsep.join(paths),
        "PYTHONNOUSERSITE": "1",
        "PYTHONDONTWRITEBYTECODE": "1",
        "OMP_NUM_THREADS": "2",
        "OPENBLAS_NUM_THREADS": "2",
        "MKL_NUM_THREADS": "2",
    }
    with TemporaryDirectory(prefix="neuro-notebook-kernel-") as temporary:
        directory = Path(temporary) / "kernels/neuro-review"
        directory.mkdir(parents=True)
        (directory / "kernel.json").write_text(
            json.dumps(
                {
                    "argv": [
                        sys.executable,
                        "-m",
                        "ipykernel_launcher",
                        "-f",
                        "{connection_file}",
                    ],
                    "display_name": "Endpoint review (temporary)",
                    "language": "python",
                    "env": environment,
                }
            )
        )
        old_path = os.environ.get("JUPYTER_PATH")
        os.environ["JUPYTER_PATH"] = temporary
        try:
            client = NotebookClient(
                notebook,
                timeout=240,
                kernel_name="neuro-review",
                resources={"metadata": {"path": str(ROOT)}},
                allow_errors=False,
            )
            client.execute()
        finally:
            if old_path is None:
                os.environ.pop("JUPYTER_PATH", None)
            else:
                os.environ["JUPYTER_PATH"] = old_path
    codes = [cell for cell in notebook.cells if cell.cell_type == "code"]
    if [cell.execution_count for cell in codes] != list(range(1, len(codes) + 1)):
        raise RuntimeError("Notebook did not execute every cell once in order")
    if any(o.output_type == "error" for cell in codes for o in cell.outputs):
        raise RuntimeError("Notebook contains execution errors")
    # Outputs must be reviewed aggregates: never dump private arrays or identifiers.
    text = json.dumps([cell.outputs for cell in codes])
    for forbidden in (
        "source_trial_id",
        "session_id",
        str(ROOT),
        "checkpoint_final.pth",
        "array([",
    ):
        if forbidden in text:
            raise RuntimeError(
                "Notebook output requires privacy review before publication"
            )
    notebook.metadata["saved_artifact_execution"] = {
        "executed_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "observed saved-input replay; 6 encoders, 495 readouts, zero fits",
        "helper_sha256": hashlib.sha256(
            (ROOT / "report/endpoint_replay.py").read_bytes()
        ).hexdigest(),
        "code_sha256": hashlib.sha256(
            "\n".join(c.source for c in codes).encode()
        ).hexdigest(),
    }
    # The temporary kernel is gone; normal Python kernel metadata is portable.
    notebook.metadata.kernelspec = {
        "display_name": "Python 3",
        "language": "python",
        "name": "python3",
    }
    nbformat.validate(notebook)
    nbformat.write(notebook, NOTEBOOK)
    body, _ = HTMLExporter(template_name="basic").from_notebook_node(notebook)
    head = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; img-src data:; style-src 'unsafe-inline'; base-uri 'none'; form-action 'none'">
<title>Saved endpoint model — executed review notebook</title>
<style>body{font:17px/1.65 system-ui,sans-serif;max-width:1100px;margin:30px auto;padding:24px;color:#222}
img{max-width:100%;height:auto}pre{font-size:13px;white-space:pre-wrap;overflow-wrap:anywhere;background:#f4f6f8;padding:12px}
table{border-collapse:collapse;display:block;overflow-x:auto}th,td{padding:8px;border:1px solid #ddd;text-align:left}
.cell{margin-bottom:28px}h1,h2,h3{line-height:1.3}a{color:#245370}.output_png{text-align:center}</style></head><body>"""
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(head + body + "</body></html>")
    print(f"PASS: fresh native kernel, {len(codes)} code cells, no execution errors")
    print(f"Notebook: {NOTEBOOK.relative_to(ROOT)}")
    print(
        f"HTML: {OUTPUT.relative_to(ROOT)} (inline PNG equations/figures; no MathJax dependency)"
    )


if __name__ == "__main__":
    execute()
