"""Add reviewed interpretation to authenticated new results; never fit or replay.

Preserves the immutable run and every original notebook cell. The new sibling
directory contains a standalone HTML report, the executed notebook with a new
markdown cell, and copies of all aggregate tables/figures.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import html
import json
import os
from pathlib import Path
import re
import shutil

import mistune
import nbformat


def sha(path: Path) -> str:
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def relative_links(markdown: str, source: Path, destination: Path) -> str:
    """Keep repository-relative document links valid in the sibling deliverable."""

    def replace(match):
        target = match.group(2)
        if re.match(r"[a-zA-Z]+:|#", target):
            return match.group(0)
        location, separator, fragment = target.partition("#")
        resolved = (source.parent / location).resolve()
        link = Path(os.path.relpath(resolved, destination)).as_posix()
        if separator:
            link += "#" + fragment
        return f"{match.group(1)}({link})"

    return re.sub(r"(!?\[[^\]]+\])\(([^\s)]+)\)", replace, markdown)


def narrative_images(markdown: str, destination: Path, run: Path, receipt: dict):
    """Embed only receipt-authenticated PNGs in the added narrative cell/report."""
    attachments, images = {}, {}

    def attach(match):
        target = match.group(2)
        path = (destination / target).resolve()
        if not path.is_relative_to(run) or path.suffix != ".png":
            raise ValueError("narrative images must be PNGs from the completed run")
        relative = path.relative_to(run).as_posix()
        digest = sha(path)
        if digest != receipt["files_sha256"].get(relative):
            raise ValueError("narrative image authentication failed")
        name = f"interpretation-{len(attachments) + 1}.png"
        data = base64.b64encode(path.read_bytes()).decode()
        attachments[name] = {"image/png": data}
        images[target] = {"data": data, "file": relative, "sha256": digest}
        return f"![{match.group(1)}](attachment:{name})"

    notebook_markdown = re.sub(r"!\[([^\]]*)\]\(([^\s)]+)\)", attach, markdown)
    return notebook_markdown, attachments, images


def collate(run: Path, note: Path, out: Path, receipt_sha256: str) -> dict:
    if out.exists():
        raise FileExistsError("fresh deliverable directory required")
    if out.is_relative_to(run):
        raise ValueError("deliverables must not modify the immutable run tree")
    receipt_path = run / "receipt.json"
    if sha(receipt_path) != receipt_sha256:
        raise ValueError("unexpected run receipt")
    receipt = json.loads(receipt_path.read_text())
    if receipt["status"] != "completed":
        raise ValueError("only a completed run can be collated")
    for name, digest in receipt["files_sha256"].items():
        path = (run / name).resolve()
        if not path.is_relative_to(run) or sha(path) != digest:
            raise ValueError(f"run file authentication failed: {name}")

    original = json.loads((run / "population_grid.executed.ipynb").read_text())
    code = [cell for cell in original["cells"] if cell["cell_type"] == "code"]
    if [cell["execution_count"] for cell in code] != list(range(1, 13)):
        raise ValueError("expected twelve sequential executed cells")
    if any(
        output["output_type"] == "error" for cell in code for output in cell["outputs"]
    ):
        raise ValueError("notebook contains execution errors")

    interpretation = relative_links(note.read_text(), note, out)
    notebook_interpretation, attachments, images = narrative_images(
        interpretation, out, run, receipt
    )
    provenance = {
        "original_run_receipt_sha256": receipt_sha256,
        "interpretation_sha256": sha(note),
        "original_notebook_sha256": sha(run / "population_grid.executed.ipynb"),
        "original_cells_and_outputs_preserved": True,
        "new_fits_or_model_replays_during_collation": 0,
    }
    addition = nbformat.v4.new_markdown_cell(
        "This interpretation was added after execution and independent results "
        "review. All original code cells and saved outputs below are unchanged.\n\n"
        + notebook_interpretation,
        id="interpretation-20261111",
    )
    if attachments:
        addition["attachments"] = attachments
    notebook = json.loads(json.dumps(original))
    notebook["cells"].insert(1, addition)
    notebook["metadata"]["population_grid_collation"] = provenance
    nbformat.validate(nbformat.from_dict(notebook))
    assert notebook["cells"][:1] + notebook["cells"][2:] == original["cells"]

    render_markdown = mistune.create_markdown(plugins=["table"])
    rendered = render_markdown(interpretation)
    for target, record in images.items():
        rendered = rendered.replace(
            'src="' + html.escape(target, quote=True) + '"',
            'src="data:image/png;base64,' + record["data"] + '"',
        )
    full_report = (run / "report/report.html").read_text()
    body_start = full_report.index("<body>") + len("<body>")
    first_h1_end = full_report.index("</h1>", body_start) + len("</h1>")
    full_report = (
        full_report[:body_start]
        + '<article id="interpretation">'
        + rendered
        + "</article><hr>"
        + '<h1 id="complete-evidence">Complete numerical and visual evidence</h1>'
        + full_report[first_h1_end:]
    )
    headings = []

    def add_anchor(match):
        index = len(headings) + 1
        content = match.group(1)
        label = re.sub("<[^>]+>", "", content)
        headings.append((f"section-{index}", label))
        return f'<h2 id="section-{index}">{content}</h2>'

    full_report = re.sub(r"<h2>(.*?)</h2>", add_anchor, full_report)
    navigation = (
        '<nav aria-label="Report contents"><details><summary>Report contents</summary><ul>'
        + "".join(
            f'<li><a href="#{anchor}">{html.escape(html.unescape(label))}</a></li>'
            for anchor, label in headings
        )
        + "</ul></details></nav>"
    )
    full_report = full_report.replace("<body>", "<body>" + navigation, 1)
    full_report = full_report.replace(
        "</style>",
        "nav{background:#eef3f2;padding:4px 16px}"
        "article table{font-size:14px}a{color:#245a81}"
        "article{max-width:1100px}hr{margin:64px 0}</style>",
        1,
    )
    if full_report.count('src="data:image/png;base64,') != 246 + len(attachments):
        raise ValueError("expected every original embedded figure")
    if re.search(r'<img[^>]+src="(?!data:image/png;base64,)', full_report):
        raise ValueError("report image is not embedded")
    if re.search(r'<(?:script|link)[^>]+(?:src|href)="https?://', full_report):
        raise ValueError("report requires an external resource")

    out.mkdir(parents=True, mode=0o700)
    shutil.copytree(run / "report/tables", out / "tables")
    shutil.copytree(run / "report/images", out / "images")
    for name in (
        "figure_provenance.json",
        "configuration.json",
        "reconstruction_accounting.json",
    ):
        shutil.copy2(run / "report" / name, out / name)
    (out / "report.html").write_text(full_report)
    (out / "population_grid.executed.ipynb").write_text(
        json.dumps(notebook, ensure_ascii=False, indent=1) + "\n"
    )
    (out / "interpretation.md").write_text(interpretation)
    saved = json.loads((out / "population_grid.executed.ipynb").read_text())
    assert saved["cells"][:1] + saved["cells"][2:] == original["cells"]
    manifest = {
        "classification": "reviewed presentation of completed exploratory study",
        **provenance,
        "collator_sha256": sha(Path(__file__)),
        "authenticated_original_files": len(receipt["files_sha256"]),
        "preserved_original_code_cells": len(code),
        "original_figures": 246,
        "interpretation_figure_occurrences": len(attachments),
        "embedded_figures": 246 + len(attachments),
        "interpretation_images": [
            {key: value for key, value in record.items() if key != "data"}
            for record in images.values()
        ],
        "files_sha256": {
            p.relative_to(out).as_posix(): sha(p)
            for p in sorted(out.rglob("*"))
            if p.is_file()
        },
    }
    (out / "collation.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return {key: value for key, value in manifest.items() if key != "files_sha256"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", required=True, type=Path)
    parser.add_argument("--interpretation", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--receipt-sha256", required=True)
    args = parser.parse_args()
    print(
        json.dumps(
            collate(
                args.run.resolve(),
                args.interpretation.resolve(),
                args.output.resolve(),
                args.receipt_sha256,
            ),
            indent=2,
        )
    )
