#!/usr/bin/env python3
"""Render the October23 report from authenticated notebook outputs, never execution.

Run from any directory. --self-test uses invented scalar rows only. No neuro,
joblib, pickle, torch, input reconstruction, model loading or fitting is used.
"""

from __future__ import annotations

import base64
import csv
import hashlib
import json
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "outputs/fresh-notebooks-20261023/real"
OUT = ROOT / "docs/reports/cebra-27unit-notebooks-20261023"
RECEIPT_SHA = "bbc59a6899cb2c42b20a985baaaf7b55cec4f7d37c3e92f076d73c8325dafebe"
STAGES = ("01_pseudopopulation", "02_pca_lda", "03_cebra")
CASES = [f"observed_seed{s}_{b}" for s in (0, 1) for b in ("full", "reduced")]
CASES += [f"permuted_seed0_{b}" for b in ("full", "reduced")]
HEADS = {"pair": "Pair30", "start": "Start6", "goal": "Goal6"}
REPS = {
    "raw": "Raw + LR",
    "pca": "PCA-8 + LR",
    "cebra": "CEBRA-8 + LR",
    "lda": "Raw SVD-LDA",
}
METRICS = (
    "accuracy",
    "development_BA",
    "macro_F1",
    "log_loss",
    "train_BA",
    "train_development_gap",
)
NAME = re.compile(
    r"(observed|permuted)_seed([01])_(full|reduced)_(raw|pca|cebra|lda)_(pair|start|goal)"
)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def text(value):
    return "".join(value) if isinstance(value, list) else value


def checked_json(path, expected):
    require(sha256(path) == expected, f"Changed authenticated input: {path.name}")
    return json.loads(path.read_text())


def validate_row(row):
    require(set(row) == {"name", "head", *METRICS}, "Unexpected metric schema")
    match = NAME.fullmatch(row["name"])
    if match is None:
        raise ValueError("Unexpected readout identity")
    world, seed, budget, rep, head = match.groups()
    require(head == row["head"], "Mismatched target")
    require(
        world == "observed" or (seed == "0" and rep != "lda"),
        "Unexpected diagnostic case",
    )
    for key in METRICS:
        require(
            type(row[key]) in (int, float) and math.isfinite(row[key]),
            f"Nonfinite/non-numeric {key}",
        )
    for key in ("accuracy", "development_BA", "macro_F1", "train_BA"):
        require(0 <= row[key] <= 1, f"Out-of-range {key}")
    require(row["log_loss"] >= 0, "Negative loss")
    require(
        math.isclose(row["accuracy"], row["development_BA"], abs_tol=1e-12),
        "Unbalanced evaluation",
    )
    require(
        math.isclose(
            row["train_BA"] - row["development_BA"],
            row["train_development_gap"],
            abs_tol=1e-12,
        ),
        "Wrong gap",
    )
    return {
        "world": world,
        "seed": int(seed),
        "budget": budget,
        "representation": rep,
        **row,
    }


def metric_rows(notebook):
    rows = []
    for cell in notebook["cells"]:
        for output in cell.get("outputs", []):
            require(
                output.get("output_type") != "error", "Saved notebook contains an error"
            )
            for line in text(output.get("text", "")).splitlines():
                if line.startswith('[{"accuracy":'):
                    batch = json.loads(line)
                    require(len(batch) == 9, "Incomplete readout batch")
                    rows.extend(validate_row(row) for row in batch)
    return rows


def combine_rows(b_rows, c_rows):
    require(len(b_rows) == 36 and len(c_rows) == 54, "Wrong notebook row counts")
    combined = {}
    for stage, rows in ((STAGES[1], b_rows), (STAGES[2], c_rows)):
        require(
            len({r["name"] for r in rows}) == len(rows), "Duplicate within notebook"
        )
        for row in rows:
            name = row["name"]
            if name in combined:
                require(
                    combined[name][0] == row, "Repeated raw/PCA references disagree"
                )
                combined[name][1].append(stage)
            else:
                combined[name] = (row, [stage])
    expected = {
        f"{case}_{rep}_{head}"
        for case in CASES
        for rep in REPS
        for head in HEADS
        if not (case.startswith("permuted") and rep == "lda")
    }
    require(set(combined) == expected, "Incomplete/unexpected grid")
    return [
        {
            **row,
            "source_notebooks": ";".join(stages),
            "window": "0-1s_wholecue",
            "n_development_pseudorows": 240,
        }
        for row, stages in combined.values()
    ]


def source_accounting(notebooks):
    a = notebooks[STAGES[0]]
    audit = json.loads(text(a["cells"][3]["outputs"][0]["text"]))
    neural = json.loads(text(a["cells"][7]["outputs"][0]["text"]).splitlines()[0])
    # ponytail: fixed authenticated snapshot; no generic notebook-schema adapter.
    usage = {}
    for stage in STAGES[1:]:
        for output in notebooks[stage]["cells"][8]["outputs"]:
            for line in text(output.get("text", "")).splitlines():
                if " source accounting: " not in line:
                    continue
                case, payload = line.split(" source accounting: ", 1)
                require(case in CASES, "Unexpected source-accounting case")
                value = json.loads(payload)
                require(
                    set(value)
                    == {
                        "eligible_sources",
                        "used_sources",
                        "unused_sources",
                        "repeated_sources",
                        "reuse_histogram",
                    },
                    "Unexpected usage fields",
                )
                require(
                    value["used_sources"] + value["unused_sources"]
                    == value["eligible_sources"],
                    "Usage conservation",
                )
                require(
                    sum(int(k) * v for k, v in value["reuse_histogram"].items())
                    == 4800,
                    "Wrong block draws",
                )
                require(
                    case not in usage or usage[case] == value, "Notebook usage mismatch"
                )
                usage[case] = value
    require(set(usage) == set(CASES), "Missing source accounting")
    require(
        (
            audit["selected_units"],
            audit["selected_sessions"],
            audit["selected_train"],
            audit["selected_development"],
            audit["contributor_overlap"],
        )
        == (27, 10, 1415, 551, 0),
        "Wrong cohort",
    )
    return {
        "selection": {k: v for k, v in audit.items() if k != "access"},
        "neural_event_accounting": {k: v for k, v in neural.items() if k != "access"},
        "training_usage": usage,
    }


def extract_images(notebooks):
    entries = [
        (STAGES[0], 8, 0, "source_audit"),
        (STAGES[0], 10, 1, "construction"),
        (STAGES[0], 12, 1, "source_reuse"),
    ]
    entries += [
        (STAGES[1], 8, 2 + 3 * i, f"b_{case}_confusions")
        for i, case in enumerate(CASES[:4])
    ]
    entries.append((STAGES[1], 10, 1, "pca_observed_seed1_reduced_projection"))
    for i, case in enumerate(CASES):
        entries += [
            (STAGES[2], 8, 2 + 4 * i, f"c_{case}_learning"),
            (STAGES[2], 8, 3 + 4 * i, f"c_{case}_confusions"),
        ]
    entries.append((STAGES[2], 10, 0, "cebra_permuted_seed0_reduced_projection"))
    require(
        sum(
            "image/png" in o.get("data", {})
            for n in notebooks.values()
            for c in n["cells"]
            for o in c.get("outputs", [])
        )
        == len(entries)
        == 21,
        "Unexpected image inventory",
    )
    records = []
    for stage, cell, output, name in entries:
        encoded = text(
            notebooks[stage]["cells"][cell]["outputs"][output]["data"]["image/png"]
        )
        data = base64.b64decode("".join(encoded.split()), validate=True)
        require(data.startswith(b"\x89PNG\r\n\x1a\n"), "Invalid saved PNG")
        path = OUT / "images" / f"{name}.png"
        path.write_bytes(data)
        records.append(
            {
                "file": str(path.relative_to(OUT)),
                "source_notebook": stage,
                "cell_index": cell,
                "output_index": output,
                "sha256": sha256(path),
            }
        )
    return records


def summary_plots(rows):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    index = {r["name"]: r for r in rows}
    for metric, filename, ylabel in (
        (
            "development_BA",
            "wholecue_balanced_accuracy",
            "Development balanced accuracy (%)",
        ),
        ("log_loss", "wholecue_log_loss", "Development log loss (log axis)"),
        (
            "train_development_gap",
            "training_development_gap",
            "Train − development BA (percentage points)",
        ),
    ):
        fig, axes = plt.subplots(1, 3, figsize=(13, 4.4), constrained_layout=True)
        for ax, (head, label) in zip(axes, HEADS.items(), strict=True):
            for budget, offset, color in (
                ("full", -0.16, "#326ba8"),
                ("reduced", 0.16, "#d97928"),
            ):
                vals = np.array(
                    [
                        [
                            index[f"observed_seed{s}_{budget}_{rep}_{head}"][metric]
                            for s in (0, 1)
                        ]
                        for rep in REPS
                    ]
                )
                if metric != "log_loss":
                    vals *= 100
                x = np.arange(4) + offset
                if metric == "log_loss":
                    ax.scatter(
                        x,
                        vals.mean(axis=1),
                        marker="_",
                        s=220,
                        color=color,
                        label=budget,
                    )
                else:
                    ax.bar(
                        x,
                        vals.mean(axis=1),
                        width=0.3,
                        color=color,
                        alpha=0.8,
                        label=budget,
                    )
                for s, marker in ((0, "o"), (1, "x")):
                    ax.scatter(
                        x + (s - 0.5) * 0.06,
                        vals[:, s],
                        color="black",
                        s=18,
                        marker=marker,
                    )
            reference = 1 / (30 if head == "pair" else 6)
            if metric == "development_BA":
                ax.axhline(100 * reference, color="gray", linestyle=":")
                ax.set_ylim(0, 100)
            elif metric == "log_loss":
                ax.set_yscale("log")
                ax.axhline(-math.log(reference), color="gray", linestyle=":")
            else:
                ax.axhline(0, color="gray", linestyle=":")
                ax.set_ylim(0, 100)
            ax.set(
                title=label,
                xticks=np.arange(4),
                xticklabels=["Raw LR", "PCA LR", "CEBRA LR", "LDA"],
            )
            ax.tick_params(axis="x", labelrotation=20)
        axes[0].set_ylabel(ylabel)
        axes[0].legend(title="Training source pool")
        fig.suptitle(
            "27 units / 10 sessions · whole cue · seeds 0 (circle), 1 (cross)\nMeans and computational seeds, not biological uncertainty",
            fontsize=12,
        )
        fig.savefig(OUT / "images" / f"{filename}.png", dpi=150)
        plt.close(fig)

    fig, axes = plt.subplots(1, 3, figsize=(13, 4), constrained_layout=True)
    for ax, (head, label) in zip(axes, HEADS.items(), strict=True):
        for world, budget, offset, color in (
            ("observed", "full", -0.27, "#326ba8"),
            ("observed", "reduced", -0.09, "#d97928"),
            ("permuted", "full", 0.09, "#65a58d"),
            ("permuted", "reduced", 0.27, "#aa78a8"),
        ):
            vals = [
                100 * index[f"{world}_seed0_{budget}_{rep}_{head}"]["development_BA"]
                for rep in ("raw", "pca", "cebra")
            ]
            ax.bar(
                np.arange(3) + offset,
                vals,
                width=0.18,
                color=color,
                label=f"{world} {budget}",
            )
        ax.axhline(100 / (30 if head == "pair" else 6), color="gray", linestyle=":")
        ax.set(
            title=label,
            xticks=np.arange(3),
            xticklabels=["Raw LR", "PCA LR", "CEBRA LR"],
            ylim=(0, 100),
        )
    axes[0].set_ylabel("Development balanced accuracy (%)")
    axes[0].legend(fontsize=8)
    fig.suptitle(
        "Computational seed 0 only · one permutation world (50000)\nDifferent world assemblies; no null distribution or p-value",
        fontsize=12,
    )
    fig.savefig(OUT / "images/permutation_diagnostic.png", dpi=150)
    plt.close(fig)


def write_csv(rows):
    with (OUT / "tables/metrics_by_seed.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def render_html():
    from markdown_it import MarkdownIt

    markdown = (OUT / "README.md").read_text()
    html = MarkdownIt("commonmark", {"html": True}).enable("table").render(markdown)

    def embed(match):
        path = OUT / match.group(1)
        require(path.resolve().is_relative_to(OUT.resolve()), "Image outside report")
        return (
            '<img src="data:image/png;base64,'
            + base64.b64encode(path.read_bytes()).decode()
            + '"'
        )

    html = re.sub(r'<img src="(images/[^"]+)"', embed, html)
    require('src="images/' not in html, "Unembedded image")
    style = "body{font:17px/1.6 system-ui,sans-serif;margin:auto;padding:32px;max-width:1200px;color:#17202c}img{max-width:100%;height:auto}table{border-collapse:collapse;display:block;overflow:auto}td,th{padding:8px;border-bottom:1px solid #ddd;text-align:left}h2{border-bottom:2px solid #ddd}code{overflow-wrap:anywhere}details{margin:20px 0}summary{cursor:pointer;font-weight:bold}@media print{body{padding:0}details{display:block}}"
    (OUT / "report.html").write_text(
        '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>27-unit cue-only notebook study</title><style>'
        + style
        + "</style></head><body>"
        + html
        + "</body></html>"
    )


def main():
    receipt = checked_json(RUN / "receipt.json", RECEIPT_SHA)
    require(
        receipt["status"] == "fresh-notebooks-and-fit-blocked-replay-passed",
        "Unaccepted receipt",
    )
    require(
        receipt["fit_counts"]
        == {
            "cebra": 6,
            "pca": 10,
            "logistic": 78,
            "lda": 12,
            "optimizer_updates": 6000,
        },
        "Wrong fit counts",
    )
    require([s["name"] for s in receipt["stages"]] == list(STAGES), "Wrong stages")
    require(
        sum(s["replay"]["readout_splits_checked"] for s in receipt["stages"]) == 180,
        "Wrong historical replay count",
    )
    require(
        len({s["development_identity"] for s in receipt["stages"]}) == 1,
        "Development identity mismatch",
    )
    notebooks = {
        s["name"]: checked_json(
            RUN / s["name"] / (s["name"] + ".executed.ipynb"), s["executed_sha256"]
        )
        for s in receipt["stages"]
    }
    rows = combine_rows(
        metric_rows(notebooks[STAGES[1]]), metric_rows(notebooks[STAGES[2]])
    )
    accounting = source_accounting(notebooks)
    require((OUT / "README.md").is_file(), "Report prose must exist before rendering")
    for folder in ("images", "tables"):
        (OUT / folder).mkdir(parents=True, exist_ok=True)
    write_csv(rows)
    (OUT / "tables/source_accounting.json").write_text(
        json.dumps(accounting, indent=2) + "\n"
    )
    images = extract_images(notebooks)
    summary_plots(rows)
    render_html()
    provenance = {
        "study_date": "2026-10-23",
        "report_prepared": "2026-11-02",
        "receipt_sha256": RECEIPT_SHA,
        "source_run": str(RUN.relative_to(ROOT)),
        "source_notebooks": {
            s["name"]: s["executed_sha256"] for s in receipt["stages"]
        },
        "renderer": str(Path(__file__).resolve().relative_to(ROOT)),
        "renderer_sha256": sha256(Path(__file__)),
        "method": "Authenticated saved JSON text and PNG extraction; new charts summarize saved scalar rows only. No fitting, model loading, raw input access or biological replay.",
        "metric_rows": {
            "B": 36,
            "C": 54,
            "duplicates_checked_equal": 24,
            "unique_exported": len(rows),
        },
        "historical_fit_counts": receipt["fit_counts"],
        "historical_replayed_splits": 180,
        "saved_images": images,
        "outputs": {
            str(p.relative_to(OUT)): sha256(p)
            for p in sorted(OUT.rglob("*"))
            if p.is_file() and p.name != "provenance.json"
        },
    }
    (OUT / "provenance.json").write_text(json.dumps(provenance, indent=2) + "\n")
    print(
        f"Exported {len(rows)} unique summaries, 21 exact saved PNGs, 4 summary charts and self-contained HTML: {OUT.relative_to(ROOT)}"
    )


def self_test():
    def row(name):
        return validate_row(
            {
                "name": name,
                "head": name.rsplit("_", 1)[1],
                "accuracy": 0.2,
                "development_BA": 0.2,
                "macro_F1": 0.19,
                "log_loss": 2.0,
                "train_BA": 0.8,
                "train_development_gap": 0.6,
            }
        )

    b = [
        row(f"{case}_{rep}_{head}")
        for case in CASES[:4]
        for rep in ("raw", "pca", "lda")
        for head in HEADS
    ]
    c = [
        row(f"{case}_{rep}_{head}")
        for case in CASES
        for rep in ("raw", "pca", "cebra")
        for head in HEADS
    ]
    assert len(combine_rows(b, c)) == 66
    combined_text = json.dumps(
        [{k: v for k, v in b[0].items() if k in {"name", "head", *METRICS}}] * 9,
        sort_keys=True,
    )
    assert (
        len(
            metric_rows(
                {
                    "cells": [
                        {
                            "outputs": [
                                {"text": [combined_text + "\n", "Sampler: cue\n"]}
                            ]
                        }
                    ]
                }
            )
        )
        == 9
    )
    bad = [dict(r) for r in c]
    bad[0]["log_loss"] = 3.0
    for left, right in ((b[:-1], c), (b, bad), (b, c[:-1] + [c[0]])):
        try:
            combine_rows(left, right)
        except ValueError:
            pass
        else:
            raise AssertionError("Accepted incomplete, conflicting or duplicated rows")
    invalid = {k: v for k, v in b[0].items() if k in {"name", "head", *METRICS}}
    invalid["log_loss"] = float("nan")
    try:
        validate_row(invalid)
    except ValueError:
        pass
    else:
        raise AssertionError("Accepted nonfinite metric")
    print(
        "Invented aggregate parser/grid checks passed; no scientific inputs accessed."
    )


if __name__ == "__main__":
    if sys.argv[1:] == ["--self-test"]:
        self_test()
    elif not sys.argv[1:]:
        main()
    else:
        raise SystemExit("Usage: render_fresh_notebook_report.py [--self-test]")
