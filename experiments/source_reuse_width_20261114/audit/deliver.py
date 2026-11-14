"""Post-execution interpretation and two dated delivery copies; never fits models."""

from __future__ import annotations
import argparse
import base64
import html
import json
import re
import shutil
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import nbformat
from nbconvert import HTMLExporter
import numpy as np
from neuro.studies.population_models import frozen_models
from scripts.source_support_report import table
from .. import study
from .tables import read_rows

ENCODERS = ("raw", "pca", "cebra", "native")
DECODERS = ("logistic", "svm", "knn", "lda")
NAMES = {
    "raw": "Raw",
    "pca": "PCA7",
    "cebra": "CEBRA-Time7",
    "native": "Native multisession7",
}
COLORS = ("#245c9c", "#d27d21", "#2d897b", "#9a4b92")


def control_summaries(run, part):
    groups = defaultdict(list)
    for row in read_rows(run / f"report_{part}/metrics.csv"):
        groups[row["arm"], row["encoder"], row["decoder"], row["head"]].append(row)
    scores = []
    for (arm, encoder, decoder, head), rows in groups.items():
        observed = [
            float(r["balanced_accuracy"]) for r in rows if r["world"] == "observed"
        ]
        null = [float(r["balanced_accuracy"]) for r in rows if r["world"] != "observed"]
        assert len(observed) == 3 and len(null) == 5
        scores.append(
            dict(
                arm=arm,
                encoder=encoder,
                decoder=decoder,
                head=head,
                observed_mean=float(np.mean(observed)),
                observed_min=min(observed),
                observed_max=max(observed),
                diagnostic_mean=float(np.mean(null)),
                diagnostic_min=min(null),
                diagnostic_max=max(null),
                all_observed_above_five_diagnostics=min(observed) > max(null),
                mean_accuracy=float(
                    np.mean(
                        [float(r["accuracy"]) for r in rows if r["world"] == "observed"]
                    )
                ),
                mean_macro_f1=float(
                    np.mean(
                        [float(r["macro_f1"]) for r in rows if r["world"] == "observed"]
                    )
                ),
            )
        )
    groups = defaultdict(list)
    for row in read_rows(run / f"report_{part}/paired_contrasts.csv"):
        groups[
            row["before"], row["after"], row["encoder"], row["decoder"], row["head"]
        ].append(row)
    contrasts = []
    for (before, after, encoder, decoder, head), rows in groups.items():
        observed = [float(r["delta_BA"]) for r in rows if r["world"] == "observed"]
        null = [float(r["delta_BA"]) for r in rows if r["world"] != "observed"]
        assert len(observed) == 3 and len(null) == 5
        contrasts.append(
            dict(
                before=before,
                after=after,
                encoder=encoder,
                decoder=decoder,
                head=head,
                observed_mean=float(np.mean(observed)),
                observed_min=min(observed),
                observed_max=max(observed),
                positive_repeats=sum(v > 0 for v in observed),
                zero_repeats=sum(abs(v) < 1e-12 for v in observed),
                diagnostic_mean=float(np.mean(null)),
                diagnostic_min=min(null),
                diagnostic_max=max(null),
                all_observed_above_diagnostic_contrasts=min(observed) > max(null),
            )
        )
    return scores, contrasts


def supplemental_figures(folder, contrasts, part):
    pairs = list(dict.fromkeys((r["before"], r["after"]) for r in contrasts))
    labels = [b + " − " + a for a, b in pairs]
    figures = []
    fig, ax = plt.subplots(figsize=(12, 4.5))
    for index, (encoder, color) in enumerate(zip(ENCODERS, COLORS, strict=True)):
        rows = [
            next(
                r
                for r in contrasts
                if (r["before"], r["after"], r["encoder"], r["decoder"], r["head"])
                == (a, b, encoder, "svm", "pair")
            )
            for a, b in pairs
        ]
        x = np.arange(len(pairs)) + (index - 1.5) * 0.15
        means = np.array([r["observed_mean"] for r in rows]) * 100
        ax.errorbar(
            x,
            means,
            yerr=[
                means - np.array([r["observed_min"] for r in rows]) * 100,
                np.array([r["observed_max"] for r in rows]) * 100 - means,
            ],
            fmt="o",
            color=color,
            capsize=4,
            label=NAMES[encoder] + " observed",
        )
        for xi, r in zip(x, rows, strict=True):
            ax.plot(
                [xi, xi],
                [r["diagnostic_min"] * 100, r["diagnostic_max"] * 100],
                color=color,
                lw=5,
                alpha=0.2,
            )
            ax.scatter(
                [xi], [r["diagnostic_mean"] * 100], marker="x", s=30, color=color
            )
    ax.axhline(0, color="black", lw=0.8)
    ax.set_xticks(range(len(pairs)), labels)
    ax.set_ylabel("Paired pair-BA change (percentage points)")
    ax.set_title("RBF-SVM: observed repeat changes and five diagnostic-world changes")
    ax.legend(fontsize=8, ncol=2)
    ax.grid(axis="y", alpha=0.2)
    path = folder / "paired_svm_changes.png"
    fig.savefig(path, dpi=140, bbox_inches="tight")
    plt.close(fig)
    caption = "Post-execution collation of prespecified contrasts. Circles/thin ranges: mean/min/max across3paired computational repeats. Crosses/thick translucent ranges: mean/min/max across5source-label worlds at modelseed0. Same nine endpoint classes,72constructed exposed-development rows; whole-cue RBF-SVM. These ranges are not biological confidence intervals or p-values."
    figures.append(dict(file=path.name, sha256=study.sha(path), caption=caption))
    families = [(e, d) for e in ENCODERS for d in DECODERS]
    values = np.array(
        [
            [
                next(
                    r["observed_mean"] * 100
                    for r in contrasts
                    if (r["before"], r["after"], r["encoder"], r["decoder"], r["head"])
                    == (a, b, e, d, "pair")
                )
                for a, b in pairs
            ]
            for e, d in families
        ]
    )
    maximum = max(1, float(np.abs(values).max()))
    fig, ax = plt.subplots(figsize=(10, 6.7))
    im = ax.imshow(values, cmap="RdBu", vmin=-maximum, vmax=maximum, aspect="auto")
    ax.set_xticks(range(len(pairs)), labels)
    ax.set_yticks(range(16), [NAMES[e] + " / " + d for e, d in families], fontsize=8)
    for y in range(16):
        for x in range(len(pairs)):
            ax.text(
                x,
                y,
                f"{values[y, x]:+.2f}",
                ha="center",
                va="center",
                fontsize=8,
                color="white" if abs(values[y, x]) > 0.6 * maximum else "black",
            )
    ax.set_title("Every fixed model: mean paired change in pair balanced accuracy")
    fig.colorbar(im, ax=ax, label="Percentage-point change")
    path = folder / "all_model_paired_changes.png"
    fig.savefig(path, dpi=140, bbox_inches="tight")
    plt.close(fig)
    figures.append(
        dict(
            file=path.name,
            sha256=study.sha(path),
            caption="All16fixed encoder/readout comparisons; mean of3paired computational-repeat changes. Positive cells favor AFTER, the left-hand arm in each AFTER − BEFORE label. See contrast_summary.csv for every repeat range and five diagnostic-world contrast range. Same fixed task and exposed-development construction; no biological uncertainty interval.",
        )
    )
    return figures


def narrative(part):
    if part == "reuse":
        return (
            "<p><b>More distinct source trials helped Raw/SVM and CEBRA-Time/SVM; repeating the same trials had model-dependent effects.</b> "
            "At17columns, moving from2to5distinct training sources per pool raises mean pair balanced accuracy from36.57%to59.72%for Raw/SVM "
            "and16.67%to46.30%for Time/SVM. PCA/SVM changes32.41%→34.26%; native/SVM25.00%→28.70%.</p>"
            "<p>The once-only U3 control reaches40.74%Raw/SVM and40.28%PCA/SVM. Repeated B3 assembly of the same source IDs reaches37.96%and33.33%, "
            "respectively; Time/SVM rises24.54%→34.72%, native/SVM26.39%→29.63%. Thus repeated assembly is neither necessary for every successful "
            "decoder nor uniformly beneficial. The diagnostic ranges below determine how strong each comparison is under the sampled controls.</p>"
            "<p>At fixed16rows/class, broader source support also changes repetition, weighting and joint combinations. B3/U3 retains source identities "
            "but B3 has5/6uses per source whereas U3 is uniform once-only; row count, combination coverage and optimizer exposure differ. "
            "This supports a condition-level sampling-policy conclusion, not a pure causal repetition coefficient.</p>"
            "<p>Raw/SVM and PCA/SVM pair balanced accuracy with U3 exceed all five sampled label-world scores in every observed repeat. For gains rather than absolute scores, only Raw/SVM B5−B3 "
            "(+21.76points; observed16.67…31.94, diagnostics−5.56…8.33) and Time/SVM B5−B2 "
            "(+29.63points;22.22…36.11 versus−9.72…15.28) separate all three observed changes from all five diagnostic changes. "
            "None of the four SVM B3−U3 contrasts has that separation. These are descriptive range comparisons.</p>"
        )
    return (
        "<p><b>Wider populations helped PCA/SVM strongly and CEBRA-Time/SVM at83columns, while Raw/SVM and native/SVM peaked at49columns.</b> "
        "At17/49/83columns, mean pair balanced accuracy is37.96/52.31/46.30%for Raw,33.33/68.06/72.22%for PCA, "
        "34.72/35.65/48.61%for Time and29.63/38.89/27.78%for native multisession, all with RBF-SVM. The largest population is not uniformly best.</p>"
        "<p>Every roster uses exactly3training sources/session×class and144constructed training rows. Expansion adds sessions and measured sources "
        "(81→297→540distinct current-source IDs), not just feature columns. All shared recorded blocks and development rows are matched. "
        "Raw whole-cue dimensionality increases170→490→830; each latent readout stays70-dimensional.</p>"
        "<p>Native expansion changes3→11→20encoders and mean pooling, with total references/update255/253/240 under the fixed per-session batch rule. "
        "Its supervision and pooling differ from Time. These are complete-pipeline, roster-expansion results; they do not identify individually harmful "
        "sessions/cells or isolate biological population width.</p>"
        "<p>PCA mean pairBA rises across17→49→83columns for all four readouts. Raw is decoder-dependent: logistic rises42.13→63.43→66.20%, "
        "whereas SVM peaks at49columns. The native/SVM49→83mean drop is dominated by one computational repeat; the other two show small gains.</p>"
        "<p>Among SVM width contrasts, PCA Wmid−B3 (+34.72points; observed22.22…44.44 versus diagnostics−20.83…12.50) "
        "and Time Wfull−Wmid (+12.96points;11.11…15.28 versus−18.06…6.94) separate every observed change from every sampled diagnostic change. "
        "Other positive mean gains overlap diagnostic contrast ranges. This is descriptive evidence, not a significance test.</p>"
    )


def deliver(run, out, receipt_hash, audit_path):
    assert study.sha(run / "receipt.json") == receipt_hash
    receipt = json.loads((run / "receipt.json").read_text())
    assert receipt["status"] == "completed"
    audit = json.loads(audit_path.read_text())
    assert audit["status"] == "passed" and audit["receipt_sha256"] == receipt_hash
    for path, digest in receipt["files_sha256"].items():
        assert study.sha(run / path) == digest
    out.mkdir(parents=True, exist_ok=False, mode=0o700)
    result = {}
    for part, base, foldername in (
        ("reuse", "source_reuse", "source_reuse"),
        ("width", "population_width", "population_width"),
    ):
        folder = out / foldername
        shutil.copytree(run / f"report_{part}", folder)
        scores, contrasts = control_summaries(run, part)
        study.write_csv(folder / "score_control_summary.csv", scores)
        study.write_csv(folder / "contrast_summary.csv", contrasts)
        figures = supplemental_figures(folder, contrasts, part)
        arms = study.PART_ARMS[part]
        headline = []
        for encoder in ENCODERS:
            record = {"Representation": "RBF-SVM · " + NAMES[encoder]}
            for arm in arms:
                row = next(
                    r
                    for r in scores
                    if (r["arm"], r["encoder"], r["decoder"], r["head"])
                    == (arm, encoder, "svm", "pair")
                )
                record[arm] = (
                    f"{row['observed_mean'] * 100:.2f}% [{row['observed_min'] * 100:.2f}, {row['observed_max'] * 100:.2f}]"
                )
            headline.append(record)
        controls = [
            dict(
                arm=r["arm"],
                representation=NAMES[r["encoder"]],
                observed=f"{r['observed_min'] * 100:.2f}–{r['observed_max'] * 100:.2f}%",
                five_diagnostics=f"{r['diagnostic_min'] * 100:.2f}–{r['diagnostic_max'] * 100:.2f}%",
                all_observed_above_five=r["all_observed_above_five_diagnostics"],
            )
            for r in scores
            if r["decoder"] == "svm" and r["head"] == "pair"
        ]
        section = (
            '<section id="post-execution-interpretation"><h2>Interpreted results — November15,2026</h2><p>Added after execution using authenticated saved results; no new fits or changed predictions. Study definedNovember14; biological execution completedNovember15(Singapore). Mean [min,max] below describes3computational repeats.</p>'
            + narrative(part)
            + table(headline)
            + table(controls)
        )
        section += "<p>Five source-label worlds are a bounded diagnostic reference, not a calibrated null distribution or biological significance test. Inspect all model/readout/head results in the full tables. Pair uniform reference11.11%; the hypothetical perfect-single-endpoint reference66.67% reflects the sparse nine-pair task. All claims remain conditional on known-label pseudopopulation assembly and historically exposed development.</p>"
        for figure in figures:
            encoded = base64.b64encode((folder / figure["file"]).read_bytes()).decode()
            section += (
                '<figure><img style="max-width:100%" src="data:image/png;base64,'
                + encoded
                + '"><figcaption>'
                + html.escape(figure["caption"])
                + "</figcaption></figure>"
            )
        section += "<p><b>Issue29 handoff:</b> best/worst ranking, per-class recall changes, right→wrong/wrong→right switches and retained/removed column aliases are included. No class is deleted between arms. Spatial-field maps/occupancy/coordinate provenance are unavailable in these compact inputs, so the lost-place-field explanation remains untested. Map absence is unknown, not zero selectivity. Across width, adding columns can still lower performance; a count-only missing-cell explanation is insufficient.</p>"
        section += "<p>Source-usage CSV eligible_sources denotes sources admitted by the arm’s budget; full pre-budget availability is recorded in the design. Exact_duplicate_rows counts repeated source-ID tuples, not every coincidentally equal neural vector. U3 kNN5 pair probabilities have a structural3/5ceiling. Best/worst ties were audited using exact pair-correct totals.</p>"
        section += "<p>Execution evidence:32cases completed before a kernel-file handoff error; an independently reviewed continuation trained only16unattempted width cases. Parentfailedreceipt and all inherited bytes are preserved. Total48unique cases,2,448fits excluding scalers,96,000updates;18executed code cells; no biological case was refitted.</p></section>"
        original = (folder / "report.html").read_text()
        (folder / "report.html").write_text(
            original.replace("<body>", "<body>" + section, 1)
        )
        source = run / (base + "_20261114.executed.ipynb")
        notebook = nbformat.read(source, as_version=4)
        previous = [dict(c) for c in notebook.cells]
        notebook.cells.append(
            nbformat.v4.new_markdown_cell(
                "## Post-execution interpretation and paired contrasts\n\n" + section
            )
        )
        assert [dict(c) for c in notebook.cells[:-1]] == previous
        notebook.metadata["delivery"] = {
            "date": "2026-11-15",
            "original_notebook_sha256": study.sha(source),
            "run_receipt_sha256": receipt_hash,
            "added_cells": "one labelled post-execution Markdown cell; all original cells/outputs preserved",
        }
        target = out / (base + "_20261115.executed.ipynb")
        nbformat.write(notebook, target)
        for cell in notebook.cells:
            for output in cell.get("outputs", []):
                data = output.get("data", {})
                assert not any(
                    "javascript" in mime or "widget" in mime for mime in data
                )
                assert "<script" not in data.get("text/html", "").lower()
        rendered, _ = HTMLExporter().from_notebook_node(notebook)
        # These notebooks contain static tables, text and embedded PNGs only.
        # Drop nbconvert's unused CDN loaders; the separate report retains its
        # own entirely local confusion-explorer script.
        rendered = re.sub(
            r"<script\b[^>]*>.*?</script\s*>", "", rendered, flags=re.I | re.S
        )
        target.with_suffix(".html").write_text(rendered)
        study.write_json(
            folder / "supplement_manifest.json",
            dict(
                classification="post-execution saved-result collation; no fits",
                figures=figures,
                source_notebook_sha256=study.sha(source),
                delivered_notebook_sha256=study.sha(target),
                original_cells=len(previous),
                original_code_cells=sum(c["cell_type"] == "code" for c in previous),
            ),
        )
        result[part] = dict(
            notebook=target.name,
            report=foldername + "/report.html",
            supplemental_figures=len(figures),
        )
    (out / "README.md").write_text(
        "# Two experiment notebooks — delivered November15,2026\n\n"
        "Study defined November14; fresh biological training completed November15 using existing recordings.\n\n"
        "- [Source reuse notebook](source_reuse_20261115.executed.ipynb) and [complete report](source_reuse/report.html).\n"
        "- [Population width notebook](population_width_20261115.executed.ipynb) and [complete report](population_width/report.html).\n\n"
        "Each preserves its original9executed code cells and adds one labelled interpretation cell. "
        "Reports embed every confusion matrix in an offline explorer and retain full numeric tables. "
        "Underlying models, predictions, source lineage, original notebooks and receipts are in the sibling complete-01 directory. "
        "The original real-01 handoff failure remains preserved; its32completed cases were not refitted.\n\n"
        "48unique cases;2448fits excluding scalers;96000updates;4608unique train/development confusion matrices "
        "(5376report views because B3 is shared);61original figures plus4paired-contrast figures. "
        "Existing-data exploratory condition-level evidence; spatial-field attribution awaits authenticated maps.\n"
    )
    files = {
        str(p.relative_to(out)): study.sha(p)
        for p in sorted(out.rglob("*"))
        if p.is_file()
    }
    study.write_json(
        out / "delivery_manifest.json",
        dict(
            status="completed",
            source_receipt_sha256=receipt_hash,
            numeric_audit_sha256=study.sha(audit_path),
            experiments=result,
            files_sha256=files,
        ),
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--receipt-sha256", required=True)
    parser.add_argument("--numeric-audit", type=Path, required=True)
    args = parser.parse_args()
    with frozen_models():
        deliver(
            args.run.resolve(),
            args.output.resolve(),
            args.receipt_sha256,
            args.numeric_audit.resolve(),
        )
