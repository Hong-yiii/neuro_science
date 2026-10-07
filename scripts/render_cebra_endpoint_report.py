#!/usr/bin/env python3
"""Render saved, replay-verified endpoint results; never load raw data or fit models."""

from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import json
import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from markdown_it import MarkdownIt

TARGETS = {"pair30": 30, "start6": 6, "goal6": 6}
REPS = {
    "raw": "Raw + logistic",
    "pca8": "PCA-8 + logistic",
    "cebra_cue": "Cue CEBRA + logistic",
    "cebra_joint": "Joint CEBRA + logistic",
    "raw_svd_lda": "Raw SVD-LDA",
}
COLORS = ["#0072B2", "#56B4E9", "#E69F00", "#009E73", "#CC79A7"]
WINDOWS = [f"bin{i:02d}" for i in range(10)] + ["wholecue"]
PAIRS = [f"{s}→{g}" for s in range(1, 7) for g in range(1, 7) if s != g]


def read_json(path):
    try:
        return json.loads(path.read_text())
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Unreadable report input: {path}") from exc


def read_metric_rows(path):
    rows = []
    try:
        with path.open() as handle:
            for number, line in enumerate(handle, 1):
                try:
                    row = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise RuntimeError(f"Invalid metric JSON: {path}:{number}") from exc
                if not isinstance(row, dict):
                    raise RuntimeError(f"Non-object metric row: {path}:{number}")
                rows.append(row)
    except (OSError, UnicodeError) as exc:
        raise RuntimeError(f"Unreadable metrics: {path}") from exc
    return rows


def sha256(path):
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def index_metrics(rows):
    keys = ["world", "seed", "target", "representation", "window", "split"]
    indexed = {tuple(row[k] for k in keys): row for row in rows}
    if len(indexed) != len(rows):
        raise ValueError("duplicate metric identities")
    if len(indexed) != 20790:
        raise ValueError("incomplete metric coverage")
    return indexed


def values(index, target, rep, metric, windows=WINDOWS, split="development"):
    return np.asarray(
        [
            [index[("observed", seed, target, rep, w, split)][metric] for w in windows]
            for seed in range(3)
        ],
        dtype=float,
    )


def tail_fraction(observed, nulls):
    return (1 + sum(v >= observed for v in nulls)) / (1 + len(nulls))


def matrix(rows, target, rep):
    selected = [
        r
        for r in rows
        if r["target"] == target
        and r["representation"] == rep
        and r["window"] == "wholecue"
        and r["split"] == "development"
    ]
    classes = sorted({r["true"] for r in selected})
    if len(classes) != TARGETS[target] or len(selected) != len(classes) ** 2:
        raise ValueError("incomplete confusion matrix")
    positions = {v: i for i, v in enumerate(classes)}
    count = np.zeros((len(classes), len(classes)), dtype=int)
    normalized = np.zeros_like(count, dtype=float)
    for row in selected:
        i, j = positions[row["true"]], positions[row["pred"]]
        count[i, j] = row["count"]
        normalized[i, j] = row["row_normalized_recall"]
    if count.sum() != 240:
        raise ValueError("confusion totals do not match development pseudorows")
    np.testing.assert_allclose(normalized, count / count.sum(axis=1, keepdims=True))
    return count, normalized, classes


class Report:
    def __init__(self, run, verified, out):
        self.run, self.out = run, out
        self.verification = read_json(verified)
        verification = self.verification.get("verification", {})
        if self.verification.get("status") != "passed" or not verification.get(
            "fits_blocked"
        ):
            raise ValueError(
                "refusing an interpreted report before successful fit-blocked replay"
            )
        if (
            verification.get("encoder_replays") != 126
            or verification.get("readout_replays") != 10395
            or verification.get("metric_replays") != 20790
            or verification.get("confusion_replays") != 6735960
            or verification.get("source_lineage_replays") != 63
        ):
            raise ValueError("incomplete replay receipt")
        if Path(self.verification["run_dir"]).resolve() != run.resolve():
            raise ValueError("replay receipt belongs to another run")
        if (
            sha256(run / "hash_manifest.json")
            != self.verification["run_hash_manifest_sha256"]
        ):
            raise ValueError("run manifest changed after replay")
        manifest = read_json(run / "hash_manifest.json")
        used = [
            "metrics.jsonl",
            "summary.json",
            "source_support.json",
            "source_deletion_sensitivity.json",
        ]
        used += [f"observed/seed{seed}/confusions.json" for seed in range(3)]
        for relative in used:
            if sha256(run / relative) != manifest[relative]:
                raise ValueError(f"report input changed after replay: {relative}")
        self.rows = read_metric_rows(run / "metrics.jsonl")
        self.index = index_metrics(self.rows)
        self.summary = read_json(run / "summary.json")
        self.sensitivity = read_json(run / "source_deletion_sensitivity.json")
        self.captions = []
        (out / "figures").mkdir(parents=True, exist_ok=True)
        (out / "tables").mkdir(exist_ok=True)
        self.provenance = {
            "run": str(run.resolve()),
            "run_manifest_sha256": sha256(run / "hash_manifest.json"),
            "metrics_sha256": sha256(run / "metrics.jsonl"),
            "verification_receipt": str(verified.resolve()),
            "verification_sha256": sha256(verified),
            "renderer_sha256": sha256(Path(__file__)),
            "new_fits": 0,
        }

    def save(self, fig, name, caption, performance=True):
        common = (
            "Endpoint cohort:195 units/58 sessions;12,288 train and3,265 historically exposed development real sources. "
            "Label-conditioned cross-session pseudopopulations,480 train/240 development rows per seed. "
        )
        if performance:
            common += (
                "Cue-only evaluation; frozen1,000-update encoders; train-only scaling/PCA/readouts. "
                "Logistic C=0.01 for raw/PCA/CEBRA; raw SVD-LDA is a supervised reference. "
            )
        common += "Source: run-reviewed-20261007 saved artifacts (hashes in provenance.json). Not trial-specific or path/H1 evidence."
        path = self.out / "figures" / f"{name}.png"
        fig.savefig(path, dpi=150, bbox_inches="tight", facecolor="white")
        plt.close(fig)
        self.captions.append((name, caption + " " + common))

    def support(self):
        rows = read_json(self.run / "source_support.json")
        sessions = sorted({r["session_id"] for r in rows})
        labels = [v.replace("→", "->") for v in PAIRS]
        grids = {}
        for split, total in (("train", 12288), ("development", 3265)):
            lookup = {
                (r["session_id"], r["label"]): r["sources"]
                for r in rows
                if r["split"] == split
            }
            grids[split] = np.array(
                [[lookup[(s, label)] for label in labels] for s in sessions]
            )
            assert grids[split].sum() == total
        fig, axes = plt.subplots(2, 1, figsize=(13, 7), layout="constrained")
        for ax, (split, grid) in zip(axes, grids.items(), strict=True):
            ax.bar(
                np.arange(30),
                grid.sum(axis=0),
                color="#0072B2" if split == "train" else "#E69F00",
            )
            ax.set(
                xticks=np.arange(30),
                xticklabels=PAIRS,
                ylabel="Real source trials",
                title=split,
            )
            ax.tick_params(axis="x", rotation=60)
        self.save(
            fig,
            "source_class_counts",
            "Eligible real sources by ordered endpoint pair; no decoder/uncertainty interval. These are not synthetic row counts.",
            False,
        )
        fig, axes = plt.subplots(1, 2, figsize=(14, 10), layout="constrained")
        for ax, (split, grid) in zip(axes, grids.items(), strict=True):
            im = ax.imshow(grid, aspect="auto", cmap="viridis", vmin=0)
            ax.set(
                title=split,
                xticks=np.arange(30),
                xticklabels=PAIRS,
                xlabel="Ordered pair",
                ylabel="Session (anonymized sorted order)",
            )
            ax.tick_params(axis="x", labelsize=7, rotation=90)
            ax.set_yticks(
                np.arange(0, 58, 5), [f"S{i + 1:02d}" for i in range(0, 58, 5)]
            )
            fig.colorbar(im, ax=ax, label="Real sources per session × pair")
        self.save(
            fig,
            "source_session_support",
            "Session-by-class support for the fixed inner split. No decoder, inference or confidence interval;58 session blocks are not58 outer-test folds.",
            False,
        )

    def performance(self):
        for metric, title in (
            ("balanced_accuracy", "Balanced accuracy"),
            ("log_loss", "Multiclass log loss"),
        ):
            fig, axes = plt.subplots(1, 3, figsize=(16, 4.7), layout="constrained")
            for ax, (target, nclasses) in zip(axes, TARGETS.items(), strict=True):
                for (rep, name), color in zip(REPS.items(), COLORS, strict=True):
                    y = values(self.index, target, rep, metric, WINDOWS[:10])
                    x = np.arange(50, 1000, 100)
                    ax.plot(x, y.mean(axis=0), label=name, color=color, marker=".")
                    ax.fill_between(
                        x, y.min(axis=0), y.max(axis=0), color=color, alpha=0.12
                    )
                baseline = (
                    1 / nclasses if metric == "balanced_accuracy" else np.log(nclasses)
                )
                ax.axhline(baseline, color="black", ls=":", label="Uniform reference")
                ax.set(
                    title=target, xlabel="Cue-relative bin midpoint (ms)", ylabel=title
                )
                if metric == "balanced_accuracy":
                    ax.set_ylim(0, 1)
            axes[-1].legend(fontsize=7)
            self.save(
                fig,
                f"time_{metric}",
                f"All ten predeclared100-ms cue windows, development {title.lower()}. Lines are three-seed means; shading is min–max computational-seed variation, NOT biological confidence intervals. No inspected peak is a validated chosen window.",
            )
            fig, axes = plt.subplots(1, 3, figsize=(15, 4.8), layout="constrained")
            for ax, target in zip(axes, TARGETS, strict=True):
                for i, ((rep, _name), color) in enumerate(
                    zip(REPS.items(), COLORS, strict=True)
                ):
                    y = values(self.index, target, rep, metric, ["wholecue"])[:, 0]
                    ax.bar(i, y.mean(), color=color, alpha=0.7)
                    ax.scatter(i + np.array([-0.12, 0, 0.12]), y, c="black", s=16)
                ax.set(
                    title=target,
                    ylabel=title,
                    xticks=range(5),
                    xticklabels=["Raw", "PCA8", "Cue", "Joint", "LDA"],
                )
                reference = (
                    1 / TARGETS[target]
                    if metric == "balanced_accuracy"
                    else np.log(TARGETS[target])
                )
                ax.axhline(reference, color="black", ls=":")
                if metric == "balanced_accuracy":
                    ax.set_ylim(0, 1)
            self.save(
                fig,
                f"wholecue_{metric}",
                f"Concatenated0–1s cue development {title.lower()}; bar=three-seed mean, black points=seeds0/1/2 from left to right. Uniform reference shown. Not an eleventh selectable bin; dots are not biological replicates.",
            )
        fig, axes = plt.subplots(1, 3, figsize=(16, 4.5), layout="constrained")
        for ax, target in zip(axes, TARGETS, strict=True):
            for (rep, name), color in zip(REPS.items(), COLORS, strict=True):
                gap = values(
                    self.index, target, rep, "balanced_accuracy", split="train"
                ) - values(self.index, target, rep, "balanced_accuracy")
                ax.plot(
                    range(11), gap.mean(axis=0), color=color, label=name, marker="."
                )
                ax.fill_between(
                    range(11), gap.min(axis=0), gap.max(axis=0), alpha=0.12, color=color
                )
            ax.axhline(0, color="black", ls=":")
            ax.set(
                title=target,
                ylabel="Training − development BA",
                xticks=range(11),
                xticklabels=[str(i) for i in range(10)] + ["Whole"],
            )
        axes[-1].legend(fontsize=7)
        self.save(
            fig,
            "training_development_gap",
            "Train–development balanced-accuracy gaps for every cue bin(index0=0–100ms) and wholecue. Mean/min–max across three computational seeds; not confidence intervals. Same targets/representation readouts; large gaps indicate exposed-pool generalization limits.",
        )

    def controls(self):
        family = self.summary["null_families"]
        fig, axes = plt.subplots(2, 2, figsize=(14, 8), layout="constrained")
        for ax, (stat, saved_tail) in zip(
            axes.flat, family["plus_one_upper_tail"].items(), strict=True
        ):
            obs = family["by_world"]["observed"][stat]
            nulls = [
                v[stat] for key, v in family["by_world"].items() if key != "observed"
            ]
            assert (
                len(nulls) == 20 and abs(tail_fraction(obs, nulls) - saved_tail) < 1e-12
            )
            ax.scatter(range(1, 21), nulls, color="#666666", label="Null-world maximum")
            ax.axhline(obs, color="#009E73", label="Observed maximum")
            ax.set(
                title=stat.replace("_", "\n", 2),
                xlabel="Null world",
                ylabel="Normalized family statistic",
            )
            ax.text(
                0.04,
                0.94,
                f"Inclusive tail: {round(saved_tail * 21)}/21",
                transform=ax.transAxes,
                va="top",
            )
            ax.legend(fontsize=8, loc="best")
        self.save(
            fig,
            "null_families",
            "All20 joint-pair-label shuffles within session×inner split, with complete reassembly/refitting. Seed means precede family maxima. BA normalized by uniform reference; loss skill/gain normalized by log(K). Bin families span targets/windows (absolute families also representations); wholecue gain spans three targets. Inclusive plus-one tails have minimum1/21 and are diagnostic, not pristine confirmatory p-values or universal superiority tests.",
        )
        fig, axes = plt.subplots(1, 3, figsize=(14, 4.5), layout="constrained")
        for ax, target in zip(axes, TARGETS, strict=True):
            selected = sorted(
                [
                    r
                    for r in self.sensitivity["paired_joint_logloss_gain"]
                    if r["target"] == target and r["window"] == "wholecue"
                ],
                key=lambda r: r["seed"],
            )
            for row in selected:
                b = row["gain_normalized_by_log_classes"]
                ax.plot([row["seed"]] * 2, [b["min"], b["max"]], color="#009E73", lw=4)
                ax.scatter(row["seed"], b["median"], color="black")
                lost = row["source_deletions"] - row["estimable_deletions"]
                ax.annotate(
                    f"{lost} inestimable",
                    (row["seed"], b["max"]),
                    xytext=(0, 6),
                    textcoords="offset points",
                    ha="center",
                    fontsize=8,
                )
            ax.axhline(0, color="black", ls=":")
            ax.set(
                title=target,
                xticks=[0, 1, 2],
                xlabel="Computational seed",
                ylabel="(Cue loss − joint loss) / log(K)",
            )
            ax.margins(y=0.25)
        self.save(
            fig,
            "source_deletion",
            "Wholecue paired joint advantage after deleting every pseudorow containing each used real development source, with predictions fixed. Line=min/max and dot=median of estimable deletions, NOT a confidence interval. Lost-class deletions are inestimable, not evidence of robustness; pair30 has571–579 per seed. No pseudorow bootstrap or refit.",
        )

    def confusions(self):
        for seed in range(3):
            rows = read_json(self.run / "observed" / f"seed{seed}" / "confusions.json")
            for target in TARGETS:
                fig, axes = plt.subplots(2, 5, figsize=(22, 9), layout="constrained")
                for col, (rep, name) in enumerate(REPS.items()):
                    count, normalized, classes = matrix(rows, target, rep)
                    labels = PAIRS if target == "pair30" else [str(v) for v in classes]
                    for row, (data, maximum, kind) in enumerate(
                        (
                            (count, 240 / TARGETS[target], "Count"),
                            (normalized, 1, "Row recall"),
                        )
                    ):
                        ax = axes[row, col]
                        im = ax.imshow(data, vmin=0, vmax=maximum, cmap="Blues")
                        ax.set(
                            title=f"{name}\n{kind}",
                            xlabel="Predicted",
                            ylabel="True",
                            xticks=range(len(classes)),
                            yticks=range(len(classes)),
                            xticklabels=labels,
                            yticklabels=labels,
                        )
                        ax.tick_params(
                            labelsize=5 if target == "pair30" else 9, axis="both"
                        )
                        ax.tick_params(axis="x", rotation=90)
                        fig.colorbar(im, ax=ax, shrink=0.65)
                self.save(
                    fig,
                    f"confusions_{target}_seed{seed}",
                    f"{target}, observed seed{seed}, wholecue0–1s development predictions. Top=count, bottom=row-normalized recall, all five representation/readout families;240 synthetic rows, not240 independent biological trials. No seed aggregation or uncertainty interval. Pair labels are ordered(start,goal); endpoint IDs are provisional marker-derived categories.",
                )

    def document(self):
        observed = [r for r in self.rows if r["world"] == "observed"]
        fields = [
            "seed",
            "target",
            "representation",
            "window",
            "split",
            "n",
            "accuracy",
            "balanced_accuracy",
            "macro_f1",
            "log_loss",
            "brier",
        ]
        with (self.out / "tables/observed_metrics_by_seed.csv").open("w") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(observed)
        lines = [
            "# Endpoint cue-time comparison — October7,2026",
            "",
            "**Exploratory, computationally replay-verified development-pool analysis.** Not a confirmatory or trial-specific path/H1 test.",
            "",
            "## Bottom line",
            "",
            "Endpoint labels are decodable in this historically exposed, label-conditioned pseudopopulation pool. Joint cue/navigation CEBRA improves mean wholecue ordered-pair prediction relative to cue-only CEBRA, gives a small start-accuracy gain, and does not improve goal accuracy. Strong raw/PCA references matter: CEBRA is not uniformly best. The wholecue arm-gain null family does **not** establish robust joint superiority.",
            "",
            "## Cohort, construction, and scope",
            "",
            "195 units across58 sessions;12,288 inner-training and3,265 historical-development real sources, all within original outer training. Each computational seed assembles480/240 pair-balanced train/development pseudorows from intact session blocks. This requires known condition labels: it is not an operational unknown-label natural-trial predictor. No simultaneous195-unit trial population is implied. Three seeds are computational variation, not biological replication; this is one exposed source split, not three independent folds.",
            "",
            "Direct pair30, start6, and goal6 heads use the same assemblies. Input scaler/PCA/readouts use training data only. CEBRA-Time compares cue-only vs50/50 cue/navigation training at exactly1,000updates; only training-source navigation enters. Every readout evaluates cue activity only: ten100-ms bins or concatenated first1s. Logistic C=0.01,max_iter=2000; PCA8/bin and latent8/bin give80 wholecue features; raw has195/bin and1950 wholecue features. SVD-LDA is supervised and not dimension-matched. No geometry, navigation-time decoding, temporal transfer, SVM sweep or new source folds.",
            "",
            "## Wholecue development scores",
            "",
            "Three-seed means; full seed/window/train/development detail is in `tables/observed_metrics_by_seed.csv`. Accuracy equals BA in this pair-balanced construction. Lower loss/Brier is better; higher BA/F1 is better.",
            "",
            "| Target | Representation/readout | BA | Macro-F1 | Log loss | Brier |",
            "|---|---|---:|---:|---:|---:|",
        ]
        for target in TARGETS:
            for rep, name in REPS.items():
                nums = [
                    values(self.index, target, rep, field, ["wholecue"]).mean()
                    for field in ("balanced_accuracy", "macro_f1", "log_loss", "brier")
                ]
                lines.append(
                    f"| {target} | {name} | {nums[0]:.1%} | {nums[1]:.4f} | {nums[2]:.4f} | {nums[3]:.4f} |"
                )
        lines += [
            "",
            "## Paired cue-only versus joint CEBRA",
            "",
            "Identical development pseudorows within each seed. Positive differences favor joint. Values below are computational seed means, not biological confidence intervals.",
            "",
            "| Target | Joint − cue BA | Cue loss − joint loss |",
            "|---|---:|---:|",
        ]
        for target in TARGETS:
            ba = values(
                self.index, target, "cebra_joint", "balanced_accuracy", ["wholecue"]
            ) - values(
                self.index, target, "cebra_cue", "balanced_accuracy", ["wholecue"]
            )
            loss = values(
                self.index, target, "cebra_cue", "log_loss", ["wholecue"]
            ) - values(self.index, target, "cebra_joint", "log_loss", ["wholecue"])
            lines.append(
                f"| {target} | {100 * ba.mean():+.2f} percentage points | {loss.mean():+.4f} |"
            )
        lines += [
            "",
            "The wholecue joint-gain family tail is8/21(0.381). Absolute bin BA, absolute bin loss-skill, and bin joint-gain families each have1/21(0.0476), the lowest possible resolution with20nulls. These session×split label shuffles do not repair historical exposure, adaptive choices, serial exchangeability or nuisance confounds. Do not turn inspected peaks into validated windows. No position/view/heading/action/session conditional controls or exact future-path test were added.",
            "",
            "## Full visual evidence",
            "",
        ]
        for name, caption in self.captions:
            lines += [
                f"### {name.replace('_', ' ')}",
                f"![{name.replace('_', ' ')}](figures/{name}.png)",
                caption,
                "",
            ]
        lines += [
            "## Verification and limits",
            "",
            "All126 encoder fits,63 PCA fits and10,395 readouts completed in32m10s, retaining all20null worlds and three seeds. Original replay false negatives were retained: float32 scaler accumulation, a PCA dtype/arithmetic-order mismatch, and CPU-vs-CUDA rounding. Separate reviewed verification uses original float64 scaler statistics, saved-float32 sklearn PCA.transform and the fitted CUDA backend; no model refits or tolerance relaxation. All63 scalers and378 PCA/encoder train/development feature arrays independently reproduced exactly. The complete amended replay checks hashes, lineage, all encoders/readouts, metrics, confusions, nulls, paired comparisons and source sensitivity; see the bound receipt and execution ledger.",
            "",
            "Independent saved-prediction review recomputed all20,790 metric rows (max error0 except macro-F1≈3.3e−16). Probability row sums differ from1 by at most3.53e−7; optional renormalization would alter log loss by at most2.23e−8. Reported values retain the original saved-prediction computation. No metric was changed to select a favorable model.",
            "",
            "The independent unit is the real source trial/session, not a bin or synthetic row. Source-deletion ranges are finite-pool sensitivity, not uncertainty intervals. Endpoint IDs are provisional. This study cannot establish prospective path information beyond start/goal, intention, simultaneous population dynamics, biological rotation, or encoder superiority on independent future recordings.",
            "",
            "## Separate completed path assay",
            "",
            "The October5 fixed4→3 component study remains separate:29units/7sessions,82training/22historical-validation sources. Its descriptive joint/logistic100–200ms peak was88.9%, but its primary family tail was9/21 and absolute family tail17/21. It is not rerun or pooled with these endpoint results. See `../cebra-cue-time-readout-20261005/README.md`. Full ordered-path prediction remains outside this study.",
            "",
            "## Provenance and operation",
            "",
            f"Run: `{self.run}`. Run-manifest SHA256: `{self.provenance['run_manifest_sha256']}`. Verification-receipt SHA256: `{self.provenance['verification_sha256']}`. Full artifact pointers and renderer hash: `provenance.json`. See `protocol.md`, `execution.md`, and `run-operations.md`. No raw data or model fits are created by this renderer. PR15 remains draft/unmerged.",
            "",
        ]
        markdown = "\n".join(lines)
        (self.out / "README.md").write_text(markdown)
        html = MarkdownIt("commonmark", {"html": True}).enable("table").render(markdown)

        def embed(match):
            path = self.out / match.group(1)
            return (
                '<img src="data:image/png;base64,'
                + base64.b64encode(path.read_bytes()).decode()
                + '"'
            )

        html = re.sub(r'<img src="(figures/[^\"]+)"', embed, html)
        style = "body{font:17px/1.6 system-ui,sans-serif;color:#17202c;background:#f4f6f9;margin:0}main{max-width:1280px;margin:auto;padding:36px;background:white}h1,h2,h3{line-height:1.2}h2{border-bottom:2px solid #dde5ee;padding-top:24px}img{max-width:100%;height:auto}table{border-collapse:collapse;width:100%;font-size:14px}th,td{padding:8px;border-bottom:1px solid #ddd;text-align:left}thead{background:#eaf0f7}code{overflow-wrap:anywhere;font-size:.9em}p{max-width:1100px}@media print{body{background:white}main{padding:0}h3{break-before:page}img{max-height:80vh}}"
        (self.out / "report.html").write_text(
            '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Endpoint cue-time comparison</title><style>'
            + style
            + "</style><main>"
            + html
            + "</main></html>"
        )
        self.provenance["figure_count"] = len(self.captions)
        self.provenance["figure_captions"] = dict(self.captions)
        (self.out / "provenance.json").write_text(
            json.dumps(self.provenance, indent=2) + "\n"
        )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--verified", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    report = Report(args.run, args.verified, args.out)
    report.support()
    report.performance()
    report.controls()
    report.confusions()
    report.document()
    print(
        json.dumps(
            {
                "figures": len(report.captions),
                "report": str(args.out / "report.html"),
                "new_fits": 0,
            }
        )
    )


if __name__ == "__main__":
    main()
