#!/usr/bin/env python3
"""Render verified matched-PCA summaries as Markdown and offline HTML; no fits."""

import argparse
from collections import defaultdict
import html
import json
import math
from pathlib import Path
import sys

import numpy as np
from markdown_it import MarkdownIt

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from scripts import place195_path_preprocessing_autoresearch as pp  # noqa: E402
from scripts import place195_matched_pca as study  # noqa: E402
from scripts import verify_path_preprocessing_results as vr  # noqa: E402
from scripts.verify_matched_pca import forbid_fits  # noqa: E402


def table(headers, rows):
    return (
        "\n".join(
            ["| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)]
            + ["| " + " | ".join(str(v) for v in row) + " |" for row in rows]
        )
        + "\n"
    )


def f(value):
    return f"{value:.6f}"


def endpoint_figure(differences):
    bound = max(abs(v) for v in differences.values()) or 1
    pieces = [
        '<figure><svg role="img" aria-labelledby="endpoint-title endpoint-desc" viewBox="0 0 720 300" xmlns="http://www.w3.org/2000/svg">',
        '<title id="endpoint-title">Matched loss differences by endpoint</title>',
        '<desc id="endpoint-desc">Bars right of zero favor PCA; left favor raw. Values are descriptive historical-validation loss differences, not confidence intervals.</desc>',
        '<line x1="370" y1="35" x2="370" y2="235" stroke="#64748b"/>',
        '<text x="120" y="25">Favors raw ←</text><text x="405" y="25">→ Favors PCA</text>',
    ]
    for i, (ep, value) in enumerate(differences.items()):
        y, width = 45 + 38 * i, abs(value) / bound * 190
        x, color = (370, "#087f5b") if value >= 0 else (370 - width, "#a61e4d")
        pieces.append(
            f'<text x="15" y="{y + 17}">{html.escape(ep.replace("->", "→"))}</text>'
            f'<rect x="{x:.2f}" y="{y}" width="{width:.2f}" height="23" fill="{color}"/>'
            f'<text x="580" y="{y + 17}">{value:+.6f}</text>'
        )
    pieces.append(
        '<text x="160" y="275">Raw-selected loss − PCA-selected loss (nats)</text></svg><figcaption>Figure 2. Equal-endpoint comparisons on an exposed, known-label pseudopopulation benchmark.</figcaption></figure>'
    )
    return "".join(pieces)


def pipeline_figure():
    return """<figure><svg role="img" aria-labelledby="pipeline-title pipeline-desc" viewBox="0 0 800 150" style="font-size:14px" xmlns="http://www.w3.org/2000/svg">
<title id="pipeline-title">What differs between the two methods</title><desc id="pipeline-desc">Both arms use identical source-safe rows and training-only scaling. Only the PCA arm adds a training-fitted projection. Each arm selects from the same three penalties using training CV.</desc>
<rect x="5" y="20" width="280" height="90" rx="8" fill="#e7edf4"/><text x="20" y="48">Same source-safe training rows</text><text x="20" y="73">One first-second rate per unit</text><text x="20" y="98">Training-only variance-floor scale</text>
<text x="315" y="48">→ Raw → logistic λ selection</text><text x="315" y="98">→ PCA (90%, no whitening) → logistic λ selection</text>
<text x="20" y="140">Each arm: λ .01 / .1 / 1; same held-out rows and weights. No endpoint decoder substituted.</text></svg><figcaption>Figure 1. PCA makes new weighted combinations of the same unit rates; it does not add recordings.</figcaption></figure>"""


def build(run, receipt_path, output):
    summary, receipt = pp.read_json(run / "summary.json"), pp.read_json(receipt_path)
    assert receipt["status"] == "verified" and receipt["new_fits"] == 0
    assert receipt["summary_sha256"] == pp.sha256_file(run / "summary.json")
    assert receipt["models_forward_replayed"] == summary["fit_count"]
    hashes = pp.read_json(run / "artifact-hashes.json")
    for relative in (
        "summary.json",
        "input-audit.json",
        "anchor.json",
        "nulls.json",
        "observed/validation_metrics.csv.gz",
        "observed/cv_summary.json",
        "observed/validation_models.json.gz",
        "observed/cv_models.json.gz",
        "observed/validation_predictions.csv.gz",
        "observed/validation_summary.json",
    ):
        assert pp.sha256_file(run / relative) == hashes[relative], relative
    audit = pp.read_json(run / "input-audit.json")
    selected, pair = summary["selected"], summary["observed"]
    assert math.isclose(
        pair["raw_loss_minus_pca_loss"],
        receipt["primary_raw_loss_minus_pca_loss"],
        abs_tol=1e-12,
    )
    metrics = vr.csv_rows(run / "observed/validation_metrics.csv.gz")
    cv = pp.read_json(run / "observed/cv_summary.json")
    models = pp.read_json(run / "observed/validation_models.json.gz")
    cv_models = pp.read_json(run / "observed/cv_models.json.gz")
    groups = vr.prediction_groups(run / "observed/validation_predictions.csv.gz")
    cv_by_key = {r["candidate_key"]: r for r in cv}
    by_key = defaultdict(list)
    for row in metrics:
        vr.close_fields(
            row,
            vr.group_metrics(groups[row["candidate_key"], row["endpoint_pair"], ""]),
        )
        by_key[row["candidate_key"]].append(row)
    all_six = []
    for candidate in study.candidates():
        rows = by_key[candidate.key]
        averages = {
            k: float(np.mean([float(r[k]) for r in rows]))
            for k in ("log_loss", "balanced_accuracy", "brier", "auroc")
        }
        train_loss = float(
            np.mean([json.loads(r["train_metrics"])["log_loss"] for r in rows])
        )
        if candidate.key in selected.values():
            assert math.isclose(
                math.log(2) - averages["log_loss"],
                pair["baseline_deltas"][study.arm(candidate.as_dict())],
                abs_tol=1e-12,
            )
        all_six.append(
            [
                "PCA" if candidate.projection == "pca90" else "Raw",
                candidate.lambda_l2,
                "yes" if candidate.key in selected.values() else "no",
                f(cv_by_key[candidate.key]["mean_cv_log_loss"]),
                f(averages["log_loss"]),
                f(math.log(2) - averages["log_loss"]),
                f(averages["balanced_accuracy"]),
                f(averages["brier"]),
                f(averages["auroc"]),
                f(train_loss),
            ]
        )
    endpoint_rows, dimension_rows, recall_rows = [], [], []
    for ep, difference in pair["endpoint_difference"].items():
        rows = {
            name: next(r for r in by_key[selected[name]] if r["endpoint_pair"] == ep)
            for name in study.ARMS
        }
        model = next(
            m
            for m in models
            if m["candidate_key"] == selected["pca"] and m["endpoint_pair"] == ep
        )
        state = model["projection_state"]
        endpoint_rows.append(
            [
                ep.replace("->", "→"),
                f(float(rows["raw"]["log_loss"])),
                f(float(rows["pca"]["log_loss"])),
                f(difference),
                f(float(rows["raw"]["balanced_accuracy"])),
                f(float(rows["pca"]["balanced_accuracy"])),
            ]
        )
        folds = sorted(
            (
                m
                for m in cv_models
                if m["candidate_key"] == selected["pca"] and m["endpoint_pair"] == ep
            ),
            key=lambda m: m["fold"],
        )
        dimension_rows.append(
            [
                ep.replace("->", "→"),
                state["input_features"],
                "/".join(str(m["projection_state"]["n_components"]) for m in folds),
                state["n_components"],
                f(state["retained_variance"]),
                rows["raw"]["train_distinct_source_count"],
                rows["raw"]["validation_rows"],
            ]
        )
        for name in study.ARMS:
            predictions = groups[selected[name], ep, ""]
            recalls = []
            for label in ("absent", "present"):
                subset = [r for r in predictions if r["true_label"] == label]
                recalls.append(
                    sum(
                        float(r["weight"])
                        for r in subset
                        if (float(r["prob_present"]) >= 0.5) == (label == "present")
                    )
                    / sum(float(r["weight"]) for r in subset)
                )
            assert math.isclose(
                float(np.mean(recalls)),
                float(rows[name]["balanced_accuracy"]),
                abs_tol=1e-12,
            )
            recall_rows.append(
                [ep.replace("->", "→"), name, f(recalls[0]), f(recalls[1])]
            )
    fixed_rows = []
    summaries = pp.read_json(run / "observed/validation_summary.json")
    for lam in study.LAMBDAS:
        keys = {
            study.arm(c.as_dict()): c.key
            for c in study.candidates()
            if c.lambda_l2 == lam
        }
        p = study.paired(summaries, keys)
        fixed_rows.append(
            [lam, f(p["raw_loss_minus_pca_loss"])]
            + [f(v) for v in p["endpoint_difference"].values()]
        )
    null_rows = [
        [kind, name, f(ref["selected"]), f(ref["max_six"])]
        for kind, arms in summary["null_references"].items()
        for name, ref in arms.items()
    ]
    nulls = pp.read_json(run / "nulls.json")
    movement_rows = [
        [
            kind,
            len(worlds),
            f(
                float(
                    np.median([w["changed_labels"] / w["source_count"] for w in worlds])
                )
            ),
            worlds[0]["pure_strata"],
            worlds[0]["pure_sources"],
        ]
        for kind, worlds in nulls.items()
    ]
    sensitivity_rows = [
        [name] + [f(q[k]) for k in ("q025", "q50", "q975")]
        for name, q in summary["bootstrap_fixed_selection_sensitivity"].items()
    ]
    influence_rows = [
        [
            r["omitted_session"],
            f(r["pair"]["baseline_deltas"]["raw"]),
            f(r["pair"]["baseline_deltas"]["pca"]),
            f(r["pair"]["raw_loss_minus_pca_loss"]),
            f(r["original_common_difference"]),
            ", ".join(r["dropped_endpoints"]) or "none",
        ]
        for r in summary["leave_session_out"]
    ]
    delta = pair["raw_loss_minus_pca_loss"]
    favored = "PCA" if delta > 0 else "raw" if delta < 0 else "neither arm"
    prose = f"""# Matched PCA versus raw: verified exploratory results

**Primary paired effect: {delta:+.6f} nats (raw-selected loss − PCA-selected loss).** The historical point comparison favors **{favored}**. This is not a confirmatory superiority result.

Training-source CV selected λ={next(c.lambda_l2 for c in study.candidates() if c.key == selected["raw"]):g} (raw) and λ={next(c.lambda_l2 for c in study.candidates() if c.key == selected["pca"]):g} (PCA), before new historical evaluation. Absolute selected losses are **{math.log(2) - pair["baseline_deltas"]["raw"]:.6f} raw** and **{math.log(2) - pair["baseline_deltas"]["pca"]:.6f} PCA**. Balanced constant-.5 loss is **{math.log(2):.6f}**.

## Explain it simply

We gave two methods the same recordings and the same question: did a particular middle corridor component appear in the later path, while start and goal stayed fixed? One method kept each unit's first-second rate. The other first mixed those rates into fewer summary numbers using PCA. Both then used the same type of simple probability predictor and the same three penalty choices.

Probability loss punishes confident mistakes; smaller is better. The difference above is the missing like-for-like comparison. It does not mean PCA predicts whole paths, reads intentions, or that synthetic rows are new animals/trials. We already knew the evaluation recordings from earlier work.

<!-- pipeline -->

## Selected-arm results by endpoint

{table(["Endpoint", "Raw loss", "PCA loss", "Raw−PCA", "Raw BA", "PCA BA"], endpoint_rows)}
<!-- endpoints -->

A positive paired difference can occur even when both methods are worse than the .5 baseline. Inspect absolute losses as well as the difference. Endpoints 2→1 and 4→1 are point/influence-only because source support is exceptionally small.

## All six recipes (nothing hidden)

{table(["Arm", "λ", "Selected", "CV loss", "Historical loss", "Baseline Δ", "BA", "Brier", "AUROC", "Training loss"], all_six)}
CV means weight each endpoint and fold equally. Historical means weight endpoints equally and each endpoint's two classes equally. Training loss is on assembled fitting rows, not new sources. BA is balanced accuracy, not accuracy under natural class prevalence.

### Same-penalty paired diagnostics

{table(["λ", "Mean raw−PCA"] + list(pair["endpoint_difference"]), fixed_rows)}
The λ=1 raw anchor reproduces accepted historical probabilities exactly (maximum difference {pp.read_json(run / "anchor.json")["maximum_probability_difference"]:.3g}); this verifies compatibility, not independent replication. The old ~83% PCA endpoint accuracy and earlier 52.1%/45.3% path-segment means involved different targets/panels/assembly and are not matched benchmarks here.

## What PCA actually compressed

{table(["Endpoint", "Unit inputs", "CV components folds0/1/2", "Final components", "Final variance fraction", "Distinct training sources drawn", "Historical product rows"], dimension_rows)}
One input per unit; the whole first second is pooled, not ten separate temporal features. PCA is full-SVD, training-only, no whitening, with the smallest positive-rank dimension reaching 90% variance. Retained variance is not percent path information or brain dimensionality. Product rows reuse original sources; they are not independent observations. Every fit's full state, singular spectrum, feature order and convergence are saved locally.

### Class recalls

{table(["Endpoint", "Arm", "Absent recall", "Present recall"], recall_rows)}

## Declared shuffled-label references

{table(["Null", "Arm", "Selected-policy tail", "Maximum-six tail"], null_rows)}
Inclusive plus-one references, with 1e−12 near-tie handling; 100 worlds of each kind, repeating all six CV recipes and both selections. These test no-path-association reference assumptions for each arm versus baseline. **They are not p-values for PCA/raw equal predictive risk or PCA superiority.**

{table(["Null", "Worlds", "Median actually changed fraction", "Pure strata", "Sources in pure strata"], movement_rows)}
Temporal halves use training-defined trial-index boundaries. Pure strata cannot change labels. Neither conditioning nor label movement verifies serial exchangeability.

## Source-resampling sensitivity, not confidence intervals

{table(["Quantity", "2.5th percentile", "Median", "97.5th percentile"], sensitivity_rows)}
Raw/PCA rows above are baseline-relative Δloss; paired_difference is raw loss minus PCA loss. 200 paired source-stratified refits use the two frozen selections, without reselection. These are **fixed-selection sensitivity percentiles**, not selection-adjusted confidence intervals, animal replication, or a superiority test. {audit["validation_singletons"]}/{audit["validation_pools"]} validation session×endpoint×label pools are singletons; copying one source cannot estimate missing variability. Aggregate summaries inherit that limitation.

### Assembly randomness (no reselection)

{table(["Seed", "Raw baseline Δ", "PCA baseline Δ", "Raw−PCA"], [[seed, f(p["baseline_deltas"]["raw"]), f(p["baseline_deltas"]["pca"]), f(p["raw_loss_minus_pca_loss"])] for seed, p in summary["assembly_seeds"].items()])}
These change mixtures of existing recordings, not biological samples.

### Leave one endpoint out (point effects)

{table(["Omitted endpoint", "Remaining mean raw−PCA"], [[ep, f(v)] for ep, v in summary["leave_endpoint_out_difference"].items()])}

### Leave one session out (paired fixed-recipe refits)

{table(["Omitted session", "Raw baseline Δ", "PCA baseline Δ", "Remaining raw−PCA", "Original common-endpoint difference", "Dropped endpoints"], influence_rows)}
Session removal drops its sources and unit columns. Comparisons use only common remaining endpoints; overlapping refits are not independent replications or unit-identity transfer.

## Data, limits, and verification

147 original-training + 41 historical-validation sources; 49 distinct selected-unit IDs, 13 sessions, 756 observed unit–source pairs. Different endpoints have separate panels. Each artificial row uses known path labels to join session blocks, preserving each source's cells/bins. This is **condition-level response-distribution separability**, not a simultaneous natural trial with an unknown label. Missing recordings stay masked, not zero-filled.

The window is exactly [0,1) s of the accepted operational cue, excluding variable tails. Eligibility previously used historical-validation support. The target is directed component `D_N_C_M__N_C_B` among all interior corridor runs after removing first/last runs, not a single midpoint or full-path reconstruction. Start/goal conditioning is not control for all varying history, gaze, heading, cue, or state. No new nuisance family was fitted; the older nuisance-only failure does not exclude confounds. Simultaneity, cue/task/animal/anatomical metadata and serial independence remain unresolved.

No minimum biologically worthwhile effect is agreed. No absence/equivalence, universal superiority, confirmatory H1, H1b low-dimensional organization, H2, causal planning or mechanism claim follows from this benchmark.

Completed **{summary["fit_count"]:,}** fit instances in **{summary["elapsed_seconds"] / 60:.2f} min**; all converged. Forward-only verifier replayed **{receipt["models_forward_replayed"]:,}** with **zero new fits**, checking saved predictions, source lineage, preprocessing, selections, nulls, bootstrap and sensitivity summaries. It independently calculates probability metrics/selection/reference summaries but shares assembly, label/resampling and forward helpers; it is not wholly independent software. AI review is not human peer review or lab metadata verification.

Full raw data/models/lineage/logs remain local and ignored. Git contains only code, methods, reports, lightweight summary and verification/review receipts. Use the execution ledger for paths and exact commands. This offline report needs no network, JavaScript, server, or model fitting.
"""
    figures = {
        "<!-- endpoints -->": endpoint_figure(pair["endpoint_difference"]),
        "<!-- pipeline -->": pipeline_figure(),
    }
    markdown = prose
    for marker, figure in figures.items():
        markdown = markdown.replace(marker, figure)
    body = MarkdownIt("commonmark", {"html": True}).enable("table").render(markdown)
    style = "body{font:17px/1.65 system-ui,sans-serif;background:#f8fafc;color:#172536;margin:0}main{max-width:1120px;margin:auto;padding:2rem}h1,h2,h3{line-height:1.25}table{border-collapse:collapse;display:block;overflow:auto;font-size:.87rem}td,th{border:1px solid #b8c4d0;padding:.45rem;text-align:left}th{background:#e7edf4}figure{background:white;padding:1rem;margin:1.5rem 0}svg{max-width:100%;height:auto}figcaption{font-size:.9rem}code{overflow-wrap:anywhere}@media print{body{background:white}main{padding:0}figure{break-inside:avoid}}"
    page = f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Matched PCA versus raw — exploratory results</title><style>{style}</style></head><body><main>{body}</main></body></html>'
    assert page.count('<svg role="img"') == 2
    assert "<script" not in page and "<img" not in page and "<link" not in page
    assert "<table>" in page and "<!-- endpoints -->" not in page
    output.mkdir(parents=True, exist_ok=True)
    (output / "report.md").write_text(markdown)
    (output / "report.html").write_text(page)
    pp.write_json(output / "summary.json", summary)
    pp.write_json(
        output / "report-evidence.json",
        {
            "summary_sha256": receipt["summary_sha256"],
            "verification_sha256": pp.sha256_file(receipt_path),
            "report_sha256": pp.sha256_file(output / "report.html"),
            "generator_sha256": pp.sha256_file(Path(__file__)),
            "new_fits": 0,
        },
    )
    return page


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path)
    parser.add_argument("--verification", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    with forbid_fits():
        build(args.run, args.verification, args.output)
    print(
        f"Wrote {args.output}/report.html and report.md; two inline figures; zero fits"
    )


if __name__ == "__main__":
    main()
