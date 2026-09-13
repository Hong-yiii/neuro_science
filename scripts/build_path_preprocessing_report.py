#!/usr/bin/env python3
"""Render the verified study's teaching Markdown with embedded, offline figures."""
from __future__ import annotations

import argparse
import csv
import gzip
import html
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np
from markdown_it import MarkdownIt
# ponytail: reuse the existing offline SVG renderer, not a new browser chart stack.
from scripts.build_path_generalization_report import Figure, figure_html, save_fig, plt


def load(path: Path):
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt") as stream:
        return json.load(stream)


def csv_rows(path: Path):
    with gzip.open(path, "rt") as stream:
        return list(csv.DictReader(stream))


def label(row):
    transform = {"raw_rate": "raw", "sqrt_rate": "sqrt", "log1p_rate": "log1p"}[row["transform"]]
    scale = "floor" if row["scaler"] == "variance_floor" else "z-score"
    return f"{row['temporal_bins']} bin · {transform} · {scale} · λ={row['lambda_l2']:g}"


def make_figures(run: Path, final: Path, assets: Path):
    summary = load(final / "final_summary.json")
    family = load(run / "round2/round2_summary.json")["family20_summary_rows"]
    observed = {r["candidate_key"]: r for r in load(final / "final_observed_candidate_summary.json")}
    assert len(family) == len(observed) == 20
    assert {r["candidate_key"] for r in family} == set(observed)
    chosen = summary["selected_candidate"]["candidate_key"]
    figures = []

    def save(fig, name, title, caption):
        assets.mkdir(parents=True, exist_ok=True)
        fig.savefig(assets / f"{name}.png", dpi=120, bbox_inches="tight")
        figures.append(Figure(save_fig(fig, assets, f"{name}.svg"), title, caption))

    ordered = sorted(family, key=lambda r: -r["primary_cv_delta_log_loss"])
    y = np.arange(len(ordered))
    fig, ax = plt.subplots(figsize=(11, 8))
    ax.barh(y - .17, [r["primary_cv_delta_log_loss"] for r in ordered], .32, label="Source-held-out inner CV", color="#2563a6")
    ax.barh(y + .17, [observed[r["candidate_key"]]["diagnostic_validation_delta_log_loss"] for r in ordered], .32,
            label="Exposed historical validation", color="#d27920")
    ax.set_yticks(y, [label(r) + ("  ← CV-selected" if r["candidate_key"] == chosen else "") for r in ordered], fontsize=8)
    ax.invert_yaxis()
    ax.axvline(0, color="black", lw=.8)
    ax.set_xlabel("Balanced conditional-Q Δlogloss (nats); positive beats constant probability 0.5")
    ax.legend(loc="upper left", bbox_to_anchor=(0, 1.08), ncol=2, fontsize=8)
    ax.grid(axis="x", alpha=.18)
    save(fig, "family", "All 20 declared candidates, not just a winner",
         "Order follows inner CV. Historical validation did not select the recipe. Bars are point estimates, not independent-trial confidence intervals.")

    metrics = csv_rows(run / "round1/round1_cv_metrics.csv.gz") + csv_rows(run / "round2/round2_cv_metrics.csv.gz")
    regularization = sorted([r for r in family if r["representation_key"] == "t1_raw_rate_variance_floor"], key=lambda r: r["lambda_l2"])
    assert [r["lambda_l2"] for r in regularization] == [.01, .1, 1.0]
    train = [np.mean([json.loads(m["train_metrics"])["log_loss"] for m in metrics if m["candidate_key"] == r["candidate_key"]]) for r in regularization]
    fig, ax = plt.subplots(figsize=(8, 4.7))
    xs = [r["lambda_l2"] for r in regularization]
    ax.plot(xs, train, "o-", label="Training", color="#53656f")
    ax.plot(xs, [r["mean_cv_log_loss"] for r in regularization], "o-", label="Inner CV", color="#2563a6")
    ax.plot(xs, [np.log(2) - observed[r["candidate_key"]]["diagnostic_validation_delta_log_loss"] for r in regularization], "o-", label="Historical validation", color="#d27920")
    ax.axhline(np.log(2), ls="--", color="black", lw=.8, label="Constant 0.5 baseline")
    ax.set_xscale("log")
    ax.set_xticks(xs, ["0.01", "0.1", "1"])
    ax.set_xlabel("Average-loss L2 λ (right = stronger regularization)")
    ax.set_ylabel("Balanced conditional-Q logloss (lower is better)")
    ax.legend(fontsize=8)
    ax.grid(alpha=.18)
    save(fig, "regularization", "Why the more accurate model was not selected",
         "λ=0.01 had the highest CV balanced accuracy but much worse logloss. This is a regularization-response curve, not an optimizer learning curve or proof of biological calibration.")

    selected_cv = next(r for r in family if r["candidate_key"] == chosen)
    endpoints = sorted(selected_cv["endpoint_mean_delta_log_loss"])
    val = summary["observed_selected_diagnostic"]["endpoint_delta_log_loss"]
    fig, ax = plt.subplots(figsize=(8, 4.6))
    x = np.arange(len(endpoints))
    ax.bar(x - .18, [selected_cv["endpoint_mean_delta_log_loss"][e] for e in endpoints], .34, label="Inner CV", color="#2563a6")
    ax.bar(x + .18, [val[e] for e in endpoints], .34, label="Historical validation", color="#d27920")
    ax.set_xticks(x, [e.replace("->", "→") + ("*" if e in ("2->1", "4->1") else "") for e in endpoints])
    ax.axhline(0, color="black", lw=.8)
    ax.set_ylabel("Selected-recipe Δlogloss (nats)")
    ax.legend(fontsize=8)
    ax.grid(axis="y", alpha=.18)
    save(fig, "endpoints", "The small aggregate gain is not broad consistency",
         "Only 2/5 historical-validation endpoint deltas are positive. Removing 6→1 makes the remaining aggregate negative. Asterisks mark point/influence-only panels; none of these bars are biological confidence intervals.")

    nulls = load(final / "null_world_summaries.json.gz")
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2), sharey=True)
    obs = summary["observed_selected_diagnostic"]["diagnostic_validation_delta_log_loss"]
    for ax, kind, title in zip(axes, ("ordinary", "temporal_half"), ("Within-stratum null", "Additional temporal-half conditioning"), strict=True):
        rows = [r for r in nulls if r["null_type"] == kind]
        assert len(rows) == 100
        chosen_null = [r["null_selected_diagnostic_delta_log_loss"] for r in rows]
        max_null = [r["null_max_family_diagnostic_delta_log_loss"] for r in rows]
        edges = np.histogram_bin_edges(chosen_null + max_null + [obs], bins=14)
        ax.hist(chosen_null, bins=edges, alpha=.55, color="#657687", label="Null's CV-selected recipe")
        ax.hist(max_null, bins=edges, histtype="step", lw=1.8, color="#d27920", label="Null's best validation score in family")
        ax.axvline(obs, color="#193e72", lw=2, label="Observed CV-selected recipe")
        ax.set_title(title, fontsize=10)
        ax.set_xlabel("Historical-validation Δlogloss (nats)")
    axes[0].set_ylabel("Permutation worlds (not biological trials)")
    fig.legend(*axes[1].get_legend_handles_labels(), loc="upper center", bbox_to_anchor=(.5, 1.08), ncol=3, fontsize=7)
    save(fig, "nulls", "The same adaptive search is repeated under each null",
         "100 worlds per null type. Both null references are compared with the fixed observed CV-selected statistic. Temporal-half conditioning is a limited serial-structure sensitivity, not proof of exchangeability.")
    return figures


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--final-dir", type=Path, required=True)
    parser.add_argument("--verification", type=Path, required=True)
    parser.add_argument("--markdown", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--assets-dir", type=Path, required=True)
    args = parser.parse_args()
    verification = load(args.verification)
    assert verification["status"] == "verified" and verification["new_model_fits"] == 0
    plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False})
    figures = make_figures(args.run_dir, args.final_dir, args.assets_dir)
    document = MarkdownIt("commonmark", {"html": True}).enable("table").render(args.markdown.read_text())
    for number, name in enumerate(("family", "regularization", "endpoints", "nulls"), 1):
        marker = f"<!-- figure:{name} -->"
        assert marker in document, marker
        document = document.replace(marker, figure_html(figures, number))
    style = """body{font:17px/1.65 system-ui,sans-serif;color:#172536;background:#f8fafc;margin:0}
main{max-width:1050px;margin:auto;padding:2rem}h1,h2,h3{line-height:1.25;color:#102e52}
a{color:#175d98}code{font-size:.88em;overflow-wrap:anywhere}pre{padding:1rem;background:#edf2f7;overflow:auto}
table{border-collapse:collapse;font-size:.9rem;display:block;overflow:auto}th,td{border:1px solid #bbc6d2;padding:.5rem;text-align:left}
th{background:#e7edf4}blockquote{border-left:4px solid #d27920;margin-left:0;padding:.7rem 1rem;background:#fff7e8}
figure{margin:2rem 0;padding:1rem;background:white;border:1px solid #d6dfe8}svg{max-width:100%;height:auto}
figcaption{font-size:.9rem;color:#37485b}.svg-wrap{overflow-x:auto}footer{font-size:.85rem;border-top:1px solid #bdc9d5;padding:1rem 0}
@media print{body{background:white}main{padding:0}figure,table{break-inside:avoid}}"""
    page = f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Path preprocessing autoresearch — 2026-09-08</title><style>{style}</style></head><body><main>{document}<footer>Self-contained figures and styling; no network resources or model fitting required to read this report. Verification: {html.escape(args.verification.name)}.</footer></main></body></html>'
    assert page.count('<svg role="img"') == 4
    assert '<script' not in page and '<img' not in page
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(page)
    print(f"Wrote {args.output}; 4 embedded figures; zero new fits")


if __name__ == "__main__":
    main()
