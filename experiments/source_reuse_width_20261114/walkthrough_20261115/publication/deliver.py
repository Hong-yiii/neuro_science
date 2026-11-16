"""Preserve executed code/outputs, correct one teaching sentence, export offline copies.

Post-execution packaging only; requires the completed run and independent numeric
verification. No model loading or fitting; feature/value archives are hashed, never decoded.
"""

from __future__ import annotations
import argparse
import base64
import copy
import json
import re
import shutil
from pathlib import Path

import nbformat
from nbconvert import HTMLExporter
from neuro.studies.population_models import frozen_models
from ... import study


def first_case_figure(run, out, part, receipt):
    """Render already fitted/saved aggregate evidence; never read neural arrays."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    arm, width, sessions = ("B2", 17, 3) if part == "reuse" else ("Wmid", 49, 11)
    case_id = "observed_seed0_" + arm
    source_files = [
        "cases/" + case_id + "/" + name for name in ("learning.json", "confusions.json")
    ]
    assert all(
        study.sha(run / name) == receipt["files_sha256"][name] for name in source_files
    )
    learning = json.loads((run / source_files[0]).read_text())
    confusion = json.loads((run / source_files[1]).read_text())
    row = next(
        r
        for r in confusion
        if (r["encoder"], r["decoder"], r["head"]) == ("raw", "logistic", "pair")
    )
    counts = np.asarray(row["counts"])
    assert counts.shape == (9, 9) and counts.sum() == 72
    recall = counts / counts.sum(1, keepdims=True)
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    for ax, encoder, title in zip(
        axes[:2],
        ("cebra", "native"),
        ("CEBRA-Time", "Native multisession"),
        strict=True,
    ):
        record = next(r for r in learning if r["encoder"] == encoder)
        values = record["loss"]["total"]
        assert len(values) == record["iterations"] == 1000
        ax.plot(np.arange(1, 1001), values, color="#245c9c")
        ax.set(
            xlabel="Optimizer update", ylabel="Own-objective total loss", title=title
        )
        ax.grid(alpha=0.2)
    image = axes[2].imshow(recall, vmin=0, vmax=1, cmap="Blues")
    axes[2].set(
        xticks=range(9),
        yticks=range(9),
        xticklabels=row["labels"],
        yticklabels=row["labels"],
        xlabel="Predicted pair",
        ylabel="True pair",
        title="Raw/logistic development confusion",
    )
    axes[2].tick_params(axis="x", rotation=90)
    for y in range(9):
        for x in range(9):
            axes[2].text(
                x,
                y,
                str(counts[y, x]),
                ha="center",
                va="center",
                fontsize=7,
                color="white" if recall[y, x] > 0.5 else "black",
            )
    fig.colorbar(image, ax=axes[2], label="Fraction within true class")
    fig.suptitle(case_id + ": saved first-case evidence")
    fig.tight_layout()
    filename = "first_case_" + part + ".png"
    path = out / "figures" / filename
    fig.savefig(path, dpi=140, bbox_inches="tight")
    plt.close(fig)
    caption = (
        f"Post-execution rendering of the same first case: {arm}, observed seed0, {width}columns/{sessions}sessions; "
        f"144constructed training rows from {54 if part == 'reuse' else 297} distinct training source identities; "
        "72constructed exposed-development rows, nine ordered endpoint classes, cue[0,1)s in100msbins. "
        f"Training curves have1,000updates each and different sampling objectives; compare within each curve. "
        f"Raw/logistic pair balanced accuracy={np.diag(recall).mean() * 100:.2f}%, uniform reference11.11%. "
        "Matrix text=counts; color=row-normalized fraction; diagonal=recall. No biological uncertainty interval. "
        "Sources: authenticated case learning.json and confusions.json; no refitting or neural-array reads."
    )
    encoded = base64.b64encode(path.read_bytes()).decode()
    content = (
        "### Saved first-case figure — rendering supplement\n\n"
        "The original diagnostic cell ran under the non-interactive Agg backend and displayed only the figure object's text. "
        "This figure renders the same authenticated saved loss/confusion records after execution. "
        "The original code and output above are preserved.\n\n"
        '<figure><img style="max-width:100%" src="data:image/png;base64,'
        + encoded
        + '"><figcaption>'
        + caption
        + "</figcaption></figure>"
    )
    return content, dict(
        file="figures/" + filename,
        sha256=study.sha(path),
        caption=caption,
        source_sha256={name: receipt["files_sha256"][name] for name in source_files},
    )


def deliver(run, audit, out):
    run, audit, out = Path(run), Path(audit), Path(out)
    receipt = json.loads((run / "receipt.json").read_text())
    verification = json.loads(audit.read_text())
    assert receipt["status"] == "completed" and verification["status"] == "passed"
    assert verification["receipt_sha256"] == study.sha(run / "receipt.json")
    assert verification["reproduction_comparison"]["cases"] == 48
    for path, digest in receipt["files_sha256"].items():
        target = (run / path).resolve()
        assert target.is_relative_to(run.resolve()) and study.sha(target) == digest
    out.mkdir(parents=True, exist_ok=False)
    (out / "figures").mkdir()
    notebooks, supplements = [], []
    for name in ("source_reuse_20261115", "population_width_20261115"):
        source = run / (name + ".executed.ipynb")
        notebook = nbformat.read(source, as_version=4)
        cells = [c for c in notebook.cells if c.cell_type == "code"]
        assert [c.execution_count for c in cells] == list(range(1, len(cells) + 1))
        assert not any(o.output_type == "error" for c in cells for o in c.outputs)
        target = out / source.name
        before = [copy.deepcopy(dict(cell)) for cell in notebook.cells]
        old = "A **session block** supplies several simultaneously recorded columns from one source trial."
        new = (
            "A **session block** supplies columns assigned to the same session/source trial. "
            "Same-session grouping does not itself verify simultaneous recording; this study "
            "does not establish biological simultaneity within or across blocks."
        )
        changed = [
            i
            for i, cell in enumerate(notebook.cells)
            if cell.cell_type == "markdown" and old in cell.source
        ]
        assert changed == [2]
        notebook.cells[2].source = notebook.cells[2].source.replace(old, new, 1)
        for index, cell in enumerate(notebook.cells):
            original = before[index]
            if index == 2:
                assert cell.cell_type == "markdown"
                assert cell.source == original["source"].replace(old, new, 1)
            else:
                assert dict(cell) == original
        part = "reuse" if name.startswith("source") else "width"
        figure_markdown, figure_manifest = first_case_figure(run, out, part, receipt)
        supplements.append(figure_manifest)
        diagnostic = [
            i
            for i, cell in enumerate(notebook.cells)
            if cell.cell_type == "code"
            and "execution.stage('first-case diagnostics')" in cell.source
        ]
        assert len(diagnostic) == 1
        notebook.cells.insert(
            diagnostic[0] + 1, nbformat.v4.new_markdown_cell(figure_markdown)
        )
        notebook.cells.append(
            nbformat.v4.new_markdown_cell(
                "## Editorial correction after execution\n\n"
                "The methods paragraph was corrected to describe same-session/source-trial grouping "
                "without asserting verified simultaneous recording. Every executed code cell and "
                "output is unchanged. The frozen training-source notebooks and run snapshot retain "
                "the original wording as execution provenance; this reviewed copy supersedes that "
                "sentence. A labelled first-case figure renders authenticated saved aggregate records after "
                "the original Agg cell displayed only text. No model was refitted for either change. "
                "Generic absolute output/runtime paths in preserved stdout describe the execution host; "
                "they are historical local paths, not public links. All figures and the confusion explorer "
                "needed to read this notebook are embedded."
            )
        )
        nbformat.write(notebook, target)
        rendered, _ = HTMLExporter().from_notebook_node(notebook)
        # All scientific figures/tables are embedded. The only interactive output
        # is the inline iframe's escaped srcdoc; removing nbconvert's top-level
        # CDN/MathJax scripts leaves that isolated local explorer intact.
        rendered = re.sub(
            r"<script\b[^>]*>.*?</script\s*>", "", rendered, flags=re.I | re.S
        )
        assert not re.search(
            r'<(?:script|link|img|iframe)\b[^>]*(?:src|href)=["\']https?://',
            rendered,
            re.I,
        )
        assert rendered.count('title="Complete confusion explorer"') == 1
        target.with_suffix(".html").write_text(rendered)
        notebooks.append(
            dict(
                file=target.name,
                code_cells=len(cells),
                sha256=study.sha(target),
                outputs_unchanged=True,
                executed_code_unchanged=True,
                executed_source_sha256=study.sha(source),
                editorial_markdown_cells=[2],
                added_editorial_note=True,
                added_saved_figure_after_original_cell=diagnostic[0],
            )
        )
    figures = out / "figures"
    for relative, filename in (
        ("report_width/figures/design.png", "width_design.png"),
        ("walkthrough_reuse/paired_svm_changes.png", "reuse_paired_svm_changes.png"),
        (
            "walkthrough_width/all_model_paired_changes.png",
            "width_all_model_changes.png",
        ),
        (
            "report_width/figures/best_worst_class_changes.png",
            "width_class_changes.png",
        ),
    ):
        source = run / relative
        assert study.sha(source) == receipt["files_sha256"][relative]
        shutil.copyfile(source, figures / filename)
        assert study.sha(source) == study.sha(figures / filename)
    manifest = dict(
        classification="post-execution publication; one explicit Markdown correction; no fits or altered code/outputs",
        run_receipt_sha256=study.sha(run / "receipt.json"),
        numeric_verification_sha256=study.sha(audit),
        publication_code_sha256=study.sha(Path(__file__)),
        notebooks=notebooks,
        post_execution_figures=supplements,
        files_sha256={
            str(p.relative_to(out)): study.sha(p)
            for p in sorted(out.rglob("*"))
            if p.is_file()
        },
    )
    study.write_json(out / "manifest.json", manifest)
    return manifest


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--run", type=Path, required=True)
    p.add_argument("--audit", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    with frozen_models():
        print(json.dumps(deliver(a.run, a.audit, a.output), indent=2))
