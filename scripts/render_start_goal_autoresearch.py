"""Build the offline teaching report from completed, source-safe study artifacts."""

from __future__ import annotations

import argparse
import base64
import csv
import html
import io
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
NAMES = {
    "pca_bin8": "PCA: 8/bin → 80",
    "pca_whole8": "PCA: whole cue → 8",
    "raw_total": "Raw cue totals",
    "raw_binned": "Raw ten-bin counts",
    "raw_rbf_svm": "Raw ten-bin RBF SVM",
    "total_shrink_lda": "Totals, shrinkage LDA",
    "fullcue_lda": "Whole-cue SVD LDA",
    "pls_whole8": "PLS: whole cue → 8",
    "time_t1": "CEBRA-Time, τ=1",
    "behavior_t1": "CEBRA-Behavior, τ=1",
    "behavior_t03": "CEBRA-Behavior, τ=.3",
    "behavior_t01": "CEBRA-Behavior, τ=.1",
    "positive_bin_t03": "Same-bin positives, τ=.3",
    "positive_grouped_t03": "Same-bin positives + grouped batch",
    "matched_bin_t1": "Time-matched CEBRA, τ=1",
    "matched_bin_t03": "Time-matched CEBRA, τ=.3",
    "matched_bin_goal_t03": "Time-matched, goal labels",
    "matched_bin_start_t03": "Time-matched, start labels",
    "behavior_w128_t03": "Behavior, width128, τ=.3",
    "behavior_d16_t03": "Behavior, dim16/bin, τ=.3",
    "behavior_whole_t03": "Behavior, whole cue → 8, τ=.3",
    "ce_bin": "CE binwise encoder + common readout",
    "ce_whole": "CE whole-cue encoder + common readout",
    "ce_bin_head": "CE binwise encoder + trained head",
    "ce_whole_head": "CE whole-cue encoder + trained head",
}
SCOPE = "Inspected development set · true-label-conditioned pseudopopulations · three assembly/training seeds · not independent biological replicates"


def table(headers, rows):
    head = "".join(f"<th scope='col'>{html.escape(str(h))}</th>" for h in headers)
    body = "".join(
        "<tr>" + "".join(f"<td>{html.escape(str(v))}</td>" for v in row) + "</tr>"
        for row in rows
    )
    return f"<div class='scroll'><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div><p class='scope'>{SCOPE}</p>"


def group(rows, keys):
    result = defaultdict(list)
    for row in rows:
        result[tuple(row.get(k) for k in keys)].append(row)
    return result


def avg(rows, key="accuracy"):
    return np.mean([r[key] for r in rows])


def pct(x):
    return f"{100 * x:.2f}%"


def primary(rows):
    return [
        r
        for r in rows
        if r["split"] == "development"
        and r["target"] == "joint"
        and not r.get("probe")
        and not r.get("condition")
        and r["case"] in NAMES
        and r.get("step") in (None, 3000)
    ]


def picture(fig, out, name, caption):
    fig.tight_layout()
    path = out / f"{name}.png"
    fig.savefig(path, dpi=145, facecolor="white", bbox_inches="tight")
    plt.close(fig)
    encoded = base64.b64encode(path.read_bytes()).decode()
    return f"<figure><img src='data:image/png;base64,{encoded}' alt='{html.escape(caption, quote=True)}'><figcaption>{html.escape(caption)}</figcaption></figure>"


def overview(rows, assets):
    groups = group(primary(rows), ["case"])
    if {k[0] for k in groups} != set(NAMES) or any(
        len(v) != 3 for v in groups.values()
    ):
        raise ValueError(
            "screen must include every declared setting and all three seeds"
        )
    ordered = sorted(groups, key=lambda k: avg(groups[k]), reverse=True)
    fig, ax = plt.subplots(figsize=(10, 8))
    means = [100 * avg(groups[k]) for k in ordered]
    ax.barh(
        range(len(ordered)),
        means,
        color=["#b25b32" if k[0].startswith("pca") else "#356b86" for k in ordered],
    )
    for i, k in enumerate(ordered):
        ax.plot(
            [100 * r["accuracy"] for r in groups[k]],
            [i] * len(groups[k]),
            "|",
            color="black",
            markersize=10,
        )
    ax.set_yticks(range(len(ordered)), [NAMES[k[0]] for k in ordered])
    ax.invert_yaxis()
    ax.axvline(100 / 30, linestyle=":", color="gray")
    ax.set(
        xlim=(0, 100),
        xlabel="Joint development accuracy (%) — marks show three seeds",
        title="Fixed-setting method screen; neural models shown at 3,000 updates",
    )
    plot = picture(
        fig,
        assets,
        "method-screen",
        "Development benchmark, not a test leaderboard. Methods below change input window, feature budget and objective; this overview does not isolate causes.",
    )
    values = []
    for k in ordered:
        rr = groups[k]
        losses = [r["log_loss"] for r in rr if r["log_loss"] is not None]
        values.append(
            [
                NAMES[k[0]],
                rr[0].get("features", "—"),
                pct(avg(rr)),
                f"{pct(min(r['accuracy'] for r in rr))}–{pct(max(r['accuracy'] for r in rr))}",
                pct(avg(rr, "start_accuracy")),
                pct(avg(rr, "goal_accuracy")),
                f"{np.mean(losses):.3f}" if losses else "not calibrated",
            ]
        )
    return plot + table(
        [
            "Representation / decoder",
            "Readout features",
            "Joint mean",
            "Seed range",
            "Start from joint",
            "Goal from joint",
            "Log loss",
        ],
        values,
    ), groups


def checkpoints(rows, study, assets):
    old = [r for r in rows if r["case"].startswith("old_") and r["target"] == "joint"]
    fresh = [
        r
        for r in rows
        if r["case"] in ("behavior_t1", "matched_bin_t03")
        and not r.get("condition")
        and not r.get("probe")
        and r["target"] == "joint"
    ]
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    for name, label, color in (
        ("old_cebra_time", "Time", "#2e6580"),
        ("old_cebra_behavior", "Behavior", "#ab5e34"),
    ):
        for split, style in (("train", "--"), ("development", "-")):
            gg = group(
                [r for r in old if r["case"] == name and r["split"] == split], ["step"]
            )
            steps = sorted(k[0] for k in gg)
            axes[0].plot(
                steps,
                [100 * avg(gg[s,]) for s in steps],
                style,
                color=color,
                marker="o",
                label=f"{label}: {split}",
            )
    for name, color in (("behavior_t1", "#ab5e34"), ("matched_bin_t03", "#2e6580")):
        for split, style in (("train", "--"), ("development", "-")):
            gg = group(
                [r for r in fresh if r["case"] == name and r["split"] == split],
                ["step"],
            )
            steps = sorted(k[0] for k in gg)
            axes[1].plot(
                steps,
                [100 * avg(gg[s,]) for s in steps],
                style,
                color=color,
                marker="o",
                label=f"{name}: {split}",
            )
    for ax in axes:
        ax.set(xlabel="Encoder update", ylabel="Joint accuracy (%)", ylim=(0, 102))
        ax.legend(fontsize=7)
    axes[0].set_title("Existing checkpoints, fixed C=.01 decoder")
    axes[1].set_title("Fresh extended training: no early stopping")
    result = picture(
        fig,
        assets,
        "checkpoint-curves",
        "Dashed: training readout. Solid: development readout. Decoder fitted anew to training embeddings at each checkpoint. Selecting the best point here would be development tuning.",
    )
    fig, axes = plt.subplots(1, 2, figsize=(11, 3.5))
    for ax, case in zip(axes, ("behavior_t1", "matched_bin_t03"), strict=True):
        for p in sorted(study.glob(f"02-cebra/{case}_seed*/loss.csv")):
            with p.open() as f:
                # pi-lens-ignore: unchecked-throwing-call-python
                losses = np.array([float(r["total"]) for r in csv.DictReader(f)])
            width = 100
            smooth = np.convolve(losses, np.ones(width) / width, mode="valid")
            ax.plot(np.arange(width, len(losses) + 1), smooth, alpha=0.7)
        ax.set(title=case, xlabel="Update", ylabel="InfoNCE loss (100-step mean)")
    return result + picture(
        fig,
        assets,
        "loss-curves",
        "Losses have different temperatures/sampling distributions, so absolute values across these panels are not comparable. Falling loss need not improve a downstream development decoder.",
    )


def checkpoint_table(rows):
    selected = [
        r
        for r in rows
        if r.get("phase") == "cebra"
        and r["split"] == "development"
        and r["target"] == "joint"
        and not r.get("probe")
    ]
    groups = group(selected, ["case", "step"])
    values = []
    for case in sorted({r["case"] for r in selected}):
        values.append(
            [
                NAMES[case],
                *[
                    pct(avg(groups[case, step]))
                    if (case, step) in groups
                    else "not run"
                    for step in (250, 1000, 3000, 10000)
                ],
            ]
        )
    return table(
        ["Encoder (common C=.01 readout)", "250 updates", "1,000", "3,000", "10,000"],
        values,
    )


def ablation_table(groups):
    contrasts = [
        ("Temperature 1 → .3", "behavior_t03", "behavior_t1"),
        ("Temperature 1 → .1", "behavior_t01", "behavior_t1"),
        ("Same-bin positives only", "positive_bin_t03", "behavior_t03"),
        ("Group reference batches by bin", "positive_grouped_t03", "positive_bin_t03"),
        (
            "Match every negative to reference time",
            "matched_bin_t03",
            "positive_grouped_t03",
        ),
        ("Width32 → 128", "behavior_w128_t03", "behavior_t03"),
        (
            "Dim8 → 16/bin (80 → 160 readout features)",
            "behavior_d16_t03",
            "behavior_t03",
        ),
        (
            "Whole-cue input (not one-factor controlled)",
            "behavior_whole_t03",
            "behavior_t03",
        ),
        ("CE whole-trial loss (same binwise encoder)", "ce_bin", "behavior_t03"),
    ]
    values = []
    for label, a, b in contrasts:
        aa = {r["seed"]: r["accuracy"] for r in groups[a,]}
        bb = {r["seed"]: r["accuracy"] for r in groups[b,]}
        delta = np.array([aa[s] - bb[s] for s in sorted(aa)]) * 100
        values.append(
            [
                label,
                f"{delta.mean():+.2f} pp",
                f"{delta.min():+.2f} to {delta.max():+.2f}",
                f"{sum(delta > 0)}/3",
            ]
        )
    return table(
        [
            "Change, all at 3,000 updates",
            "Mean paired change",
            "Seed-change range",
            "Seeds improved",
        ],
        values,
    )


def student_section(rows, study, assets):
    rr = [r for r in rows if r["case"] == "student_lda" and r["split"] == "development"]
    fig, ax = plt.subplots(figsize=(9, 4))
    series = {}
    for target, color in (
        ("start", "#346d84"),
        ("goal", "#b75f31"),
        ("joint", "#68527e"),
    ):
        series[target] = {
            b: avg([r for r in rr if r["target"] == target and r["bin"] == b])
            for b in range(-1, 10)
        }
        ax.plot(
            np.arange(10) * 0.1 + 0.05,
            [100 * series[target][b] for b in range(10)],
            "o-",
            label=target,
            color=color,
        )
    ax.axhline(100 / 6, linestyle=":", color="gray", label="endpoint chance")
    ax.axhline(100 / 30, linestyle="--", color="gray", label="joint chance")
    ax.set(
        xlabel="100 ms bin centre after cue onset (s)",
        ylabel="Development accuracy (%)",
        ylim=(0, 100),
        title="Student-style separate-target SVD LDA, source-safe inputs",
    )
    ax.legend(ncols=3, fontsize=8)
    result = picture(
        fig,
        assets,
        "student-timecourse",
        "Separate start/goal heads answer easier six-class questions; joint prediction has 30 classes. Bin means are descriptive. Selecting a peak is development selection, not a measured biological onset.",
    )
    values = []
    for b in range(10):
        shrink = [
            r
            for r in rows
            if r["case"] == "student_shrink_lda"
            and r["split"] == "development"
            and r["bin"] == b
        ]
        values.append(
            [
                f"{b * 0.1:.1f}–{(b + 1) * 0.1:.1f} s",
                *(pct(series[t][b]) for t in ("start", "goal", "joint")),
                pct(avg(shrink)),
            ]
        )
    values.append(
        [
            "Whole cue, 1950 inputs",
            *(pct(series[t][-1]) for t in ("start", "goal", "joint")),
            "not run",
        ]
    )
    result += table(
        ["Input window", "Start LDA", "Goal LDA", "Joint LDA", "Joint shrinkage LDA"],
        values,
    )
    matrices = []
    for path in sorted(
        study.glob("01-baselines/student_seed*/cross_temporal_goal.csv")
    ):
        matrix = np.zeros((10, 10))
        with path.open() as f:
            for r in csv.DictReader(f):
                # pi-lens-ignore: unchecked-throwing-call-python
                matrix[int(r["train_bin"]), int(r["development_bin"])] = float(
                    r["accuracy"]
                )
        matrices.append(matrix)
    fig, ax = plt.subplots(figsize=(6, 5))
    image = ax.imshow(
        100 * np.mean(matrices, axis=0),
        origin="lower",
        vmin=0,
        vmax=100,
        extent=(0, 1, 0, 1),
        cmap="viridis",
    )
    ax.set(
        xlabel="Development cue time (s)",
        ylabel="Training cue time (s)",
        title="Cross-temporal goal decoding (mean of 3 seeds)",
    )
    fig.colorbar(image, ax=ax, label="Accuracy (%)")
    return result + picture(
        fig,
        assets,
        "cross-temporal-goal",
        "A goal decoder trained at one bin is applied to every development bin. This probes portability of a readout over cue time, not a simultaneous neural trajectory.",
    ), series


def probes_section(rows, study, assets):
    fig, ax = plt.subplots(figsize=(9, 4))
    keys = ("hidden1", "hidden2", "hidden3", "prenorm", None)
    values = []
    for case, color in (("behavior_t1", "#b75f31"), ("matched_bin_t03", "#346d84")):
        scores = []
        for key in keys:
            rr = [
                r
                for r in rows
                if r["case"] == case
                and r.get("step") == 10000
                and r.get("probe") == key
                and r["split"] == "development"
                and r["target"] == "joint"
                and not r.get("condition")
            ]
            scores.append(100 * avg(rr))
            values.append(
                [case, key or "unit normalized", rr[0]["features"], pct(avg(rr))]
            )
        ax.plot(range(5), scores, "o-", label=case, color=color)
    ax.set_xticks(range(5), ["GELU 1", "GELU 2", "GELU 3", "Pre-norm", "Unit sphere"])
    ax.set(
        ylabel="Joint development accuracy (%)",
        ylim=(0, 100),
        title="Which layer still exposes endpoint information to a linear probe?",
    )
    ax.legend()
    result = picture(
        fig,
        assets,
        "layer-probes",
        "Common C=.01 train-only probes at 10,000 updates. Earlier layers have more coordinates; only pre-norm versus unit-normalized features have the same dimension. Probes assess accessible information, not biological identity of neurons.",
    )
    result += table(
        ["Encoder", "Probe location", "Readout features", "Joint development"], values
    )
    rankrows = []
    for case in ("behavior_t1", "matched_bin_t03"):
        for step in (250, 1000, 3000, 10000):
            values = []
            for p in study.glob(
                f"02-cebra/{case}_seed*/readout{step:05}/geometry.json"
            ):
                values.append(
                    # pi-lens-ignore: unchecked-throwing-call-python
                    json.loads(p.read_text())["development"]["participation_ratio"]
                )
            rankrows.append([case, step, f"{np.mean(values):.2f}"])
    return result + table(
        ["Encoder", "Update", "Development participation ratio (out of 8)"], rankrows
    )


def scaling_section(rows, study, assets):
    conditions = [
        ("source25", "source50", "reference"),
        ("units50", "units100", "reference"),
        ("pseudo8", "reference", "pseudo64"),
    ]
    xlabels = [
        ("25% requested", "50% requested", "full pool"),
        ("50 units", "100 units", "195 units"),
        ("8/class", "16/class", "64/class"),
    ]
    fig, axes = plt.subplots(1, 3, figsize=(12, 4))
    for ax, labels, ticks, title in zip(
        axes,
        conditions,
        xlabels,
        ("Real-source availability", "Nested unit panels", "Synthetic training rows"),
        strict=True,
    ):
        for case, color in (("pca_bin8", "#b75f31"), ("matched_bin_t03", "#346d84")):
            scores = [
                100
                * avg(
                    [
                        r
                        for r in rows
                        if r.get("phase") == "scaling"
                        and r.get("condition") == cond
                        and r["case"] == case
                        and r["split"] == "development"
                    ]
                )
                for cond in labels
            ]
            ax.plot(range(3), scores, "o-", label=case, color=color)
        ax.set_xticks(range(3), ticks, rotation=20)
        ax.set(title=title, ylim=(0, 100), ylabel="Development accuracy (%)")
    axes[0].legend(fontsize=7)
    result = picture(
        fig,
        assets,
        "scaling",
        "These are sensitivity curves, not scaling laws. Source flooring, session composition, source reuse and model/input parameter counts differ. All development arrays remain identical except deliberate unit slicing; chronology is separate.",
    )
    support = []
    for condition in (
        "source25",
        "source50",
        "reference",
        "units50",
        "units100",
        "pseudo8",
        "pseudo64",
        "chronological",
    ):
        vv = [
            # pi-lens-ignore: unchecked-throwing-call-python
            json.loads(p.read_text())
            for p in study.glob(f"04-scaling/{condition}_seed*/support.json")
        ]
        support.append(
            [
                condition,
                f"{np.mean([v['n_units'] for v in vv]):.0f}",
                f"{np.mean([v['n_sessions'] for v in vv]):.1f}",
                f"{np.mean([v['eligible_train_sources'] for v in vv]):.0f}",
                f"{np.mean([v['used_train_sources'] for v in vv]):.0f}",
                f"{np.mean([v['used_development_sources'] for v in vv]):.0f}",
                min(v["minimum_pool"] for v in vv),
                vv[0]["train_rows_per_class"] * 30,
            ]
        )
    result += table(
        [
            "Condition",
            "Units",
            "Sessions",
            "Available train sources",
            "Used train sources",
            "Used dev sources",
            "Minimum source pool",
            "Synthetic train rows",
        ],
        support,
    )
    vv = []
    for condition in ("reference", "chronological"):
        for case in ("pca_bin8", "matched_bin_t03"):
            rr = [
                r
                for r in rows
                if r.get("phase") == "scaling"
                and r.get("condition") == condition
                and r["case"] == case
                and r["split"] == "development"
            ]
            vv.append([condition, case, pct(avg(rr))])
    with (study / "04-scaling/strict_chronological_support.csv").open() as f:
        strict = list(csv.DictReader(f))
    feasible = sum(
        # pi-lens-ignore: unchecked-throwing-call-python
        int(r["min_train"]) > 0 and int(r["min_development"]) > 0
        for r in strict
    )
    result += f"<h3>Temporal-order sensitivity</h3><p>A strict 75/25 session chronology has complete 30-class support in <b>{feasible}/58 sessions</b>. The fixed 195-unit panel therefore {'does not support' if feasible < 58 else 'supports'} this exact strict-block construction. No outcome-driven session/condition selection was used to rescue it.</p>"
    result += table(["Split sensitivity", "Representation", "Joint development"], vv)
    result += "<p>The executed chronological sensitivity instead preserves each session/condition's original training/development counts and assigns earlier sources to training. It is <b>not globally time-separated across conditions</b>, not a new untouched holdout, and does not resolve serial dependence or generalization to new sessions.</p>"
    return result


def null_section(rows, groups, assets):
    values = []
    fig, ax = plt.subplots(figsize=(8, 3.5))
    for i, case in enumerate(("pca_bin8", "matched_bin_t03", "ce_bin")):
        rr = [
            r
            for r in rows
            if r.get("phase") == "null"
            and r["case"] == case
            and r["split"] == "development"
            and r.get("decoder") != "trained_ce_head"
        ]
        by_null = group(rr, ["condition"])
        means = [avg(v) for v in by_null.values()]
        ax.scatter(
            100 * np.array(means),
            [i] * len(means),
            color="#346d84",
            label="null mean" if i == 0 else None,
        )
        observed = avg(groups[case,])
        ax.scatter(
            [100 * observed],
            [i],
            marker="D",
            color="#b75f31",
            label="observed mean" if i == 0 else None,
        )
        values.append(
            [
                NAMES[case],
                pct(observed),
                pct(np.mean(means)),
                f"{pct(min(means))}–{pct(max(means))}",
                len(means),
            ]
        )
    ax.set_yticks(
        range(3), [NAMES[c] for c in ("pca_bin8", "matched_bin_t03", "ce_bin")]
    )
    ax.axvline(100 / 30, linestyle=":", color="gray")
    ax.set(xlabel="Joint development accuracy (%)", xlim=(0, 100))
    ax.legend()
    result = picture(
        fig,
        assets,
        "source-nulls",
        "Five source-label permutations × three seeds per predeclared method. Entire pair labels permuted within session and split before rebuilding and refitting. These do not preserve serial dependence and do not produce calibrated p-values.",
    )
    return result + table(
        [
            "Fixed method",
            "Observed",
            "Null grand mean",
            "Five null-mean range",
            "Null permutations",
        ],
        values,
    )


def followup_section(rows, assets):
    cases = {
        "ce_bin_replay": "Binwise CE replay",
        "ce_whole_replay": "Whole-cue CE replay",
        "ce_bin_wd01": "Binwise CE, weight decay .1",
        "ce_bin_pseudo64": "Binwise CE, 64 pseudorows/class",
    }
    fig, axes = plt.subplots(2, 2, figsize=(11, 7))
    values = []
    for ax, (case, title) in zip(axes.flat, cases.items(), strict=True):
        selected = [
            r
            for r in rows
            if r.get("phase") == "followup" and r["case"] in (case, case + "_head")
        ]
        groups = group(selected, ["case", "split", "step"])
        steps = sorted({r["step"] for r in selected})
        for name, split, style, color, label in (
            (case + "_head", "train", "--", "#777777", "trained head, training"),
            (
                case + "_head",
                "development",
                "-",
                "#2e6580",
                "trained head, development",
            ),
            (case, "development", ":", "#ab5e34", "common readout, development"),
        ):
            ax.plot(
                steps,
                [100 * avg(groups[name, split, step]) for step in steps],
                style,
                color=color,
                marker=".",
                label=label,
            )
        ax.set(
            title=title,
            xlabel="CE optimizer update",
            ylabel="Joint accuracy (%)",
            xscale="log",
            ylim=(0, 100),
        )
        ax.legend(fontsize=7)
        for step in steps:
            common = groups[case, "development", step]
            head = groups[case + "_head", "development", step]
            if len(common) != 3 or len(head) != 3:
                raise ValueError("incomplete follow-up checkpoint")
            values.append(
                [
                    title,
                    step,
                    pct(avg(common)),
                    pct(avg(head)),
                    f"{avg(head, 'log_loss'):.3f}",
                ]
            )
    result = picture(
        fig,
        assets,
        "ce-followup",
        "One adaptive follow-up round. Six replay fits must reproduce the original final encoder/head weights and predictions exactly. Earlier checkpoints are decoded after training; they do not steer the training RNG or provide a pristine selection set.",
    )
    result += table(
        [
            "Adaptive recipe",
            "Update",
            "Common readout, development",
            "Trained head, development",
            "Head log loss",
        ],
        values,
    )
    return result


def build(study, validation):
    rows, manifests = [], []
    for path in sorted(study.glob("*/manifest.json")):
        # pi-lens-ignore: unchecked-throwing-call-python
        m = json.loads(path.read_text())
        manifests.append((path.parent.name, m))
        if m["status"] != "completed":
            raise ValueError(f"incomplete phase: {path}")
        if set(m["config"]["seeds"]) != {0, 1, 2}:
            raise ValueError("report requires the three declared seeds")
        # pi-lens-ignore: unchecked-throwing-call-python
        for row in json.loads((path.parent / "metrics.json").read_text()):
            row = {**row, "phase": m["config"]["phase"]}
            if row.get("decoder") == "trained_ce_head":
                row["case"] += (
                    "_head"  # display alias only; saved phase metrics stay unchanged.
                )
                row["features"] = 8 if row["whole"] else 80
            rows.append(row)
    if {m["config"]["phase"] for _, m in manifests} != {
        "smoke",
        "baseline",
        "cebra",
        "supervised",
        "scaling",
        "null",
        "followup",
    }:
        raise ValueError("missing planned phase")
    if validation["status"] != "passed" or validation["metrics"] != len(rows):
        raise ValueError("a passing artifact verification for these rows is required")
    assets = study / "report-assets"
    assets.mkdir(exist_ok=True)
    screen, groups = overview(rows, assets)
    check = checkpoints(rows, study, assets) + checkpoint_table(rows)
    student, series = student_section(rows, study, assets)
    probes = probes_section(rows, study, assets)
    scaling = scaling_section(rows, study, assets)
    nulls = null_section(rows, groups, assets)
    followup = followup_section(rows, assets)
    oldrows = []
    with (ROOT / "outputs/start-goal-cebra-20260907/metrics.csv").open() as f:
        original = list(csv.DictReader(f))
    for case in ("raw_total", "raw_binned", "pca8", "cebra_time", "cebra_behavior"):
        oldrows.append(
            [
                case,
                pct(
                    np.mean(
                        [
                            # pi-lens-ignore: unchecked-throwing-call-python
                            float(r["joint_accuracy"])
                            for r in original
                            if r["representation"] == case
                            and r["null_id"] == "-1"
                            and r["split"] == "validation"
                        ]
                    )
                ),
            ]
        )
    original_table = table(
        ["Original frozen baseline (C=1)", "Joint development mean"], oldrows
    )
    best = max(groups, key=lambda k: avg(groups[k]))[0]
    method_count = len(groups)
    duration = sum(m["elapsed_seconds"] for _, m in manifests) / 60
    provenance = table(
        ["Phase", "Status", "Wall minutes", "Metric rows"],
        [
            [n, m["status"], f"{m['elapsed_seconds'] / 60:.1f}", m["metric_rows"]]
            for n, m in manifests
        ],
    )
    outcsv = io.StringIO()
    writer = csv.DictWriter(outcsv, fieldnames=sorted({k for r in rows for k in r}))
    writer.writeheader()
    writer.writerows(rows)
    (study / "all_metrics.csv").write_text(outcsv.getvalue())
    csvdata = base64.b64encode(outcsv.getvalue().encode()).decode()
    pca = pct(avg(groups["pca_bin8",]))
    behavior = pct(avg(groups["behavior_t1",]))
    cbwhole = pct(avg(groups["behavior_whole_t03",]))
    ce = pct(avg(groups["ce_bin",]))
    same = pct(avg(groups["matched_bin_t03",]))
    early_positive = pct(
        avg(
            [
                r
                for r in rows
                if r["case"] == "positive_bin_t03"
                and r.get("step") == 250
                and r["split"] == "development"
                and r["target"] == "joint"
            ]
        )
    )
    peak_goal = max(range(10), key=lambda b: series["goal"][b])
    content = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Is CEBRA the problem? A source-safe endpoint decoding investigation</title>
<style>
:root{{color-scheme:light;--ink:#193544;--muted:#475965;--paper:#f5f3ed;--accent:#a44823}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:17px/1.65 system-ui,sans-serif}}
code{{overflow-wrap:anywhere}}section[id],main[id]{{scroll-margin-top:5rem}}@media(max-width:650px){{section[id],main[id]{{scroll-margin-top:11rem}}}}
a{{color:#165b7a;text-underline-offset:3px}}a:focus-visible,summary:focus-visible{{outline:3px solid var(--accent);outline-offset:3px}}
header,main,footer{{max-width:1160px;margin:auto;padding:2rem}}header{{padding-top:4rem}}h1{{font-size:clamp(2rem,5vw,3.8rem);line-height:1.12;max-width:950px}}h2{{font-size:1.9rem;border-top:2px solid #c4cdd0;padding-top:1.2rem;margin-top:3rem;scroll-margin-top:5rem}}h3{{font-size:1.25rem;margin-top:2rem}}
nav{{position:sticky;top:0;background:#e8ecebf5;z-index:2;border-block:1px solid #b7c4c8;padding:.65rem 1rem;display:flex;flex-wrap:wrap;gap:.3rem 1rem;justify-content:center;font-size:.86rem}}
.kicker{{text-transform:uppercase;letter-spacing:.1em;font-size:.8rem;color:var(--accent);font-weight:750}}.lead{{font-size:1.25rem;max-width:900px}}.warning,.finding,.aside{{padding:1.2rem 1.5rem;background:white;border-left:5px solid var(--accent);margin:1.5rem 0}}.finding{{border-color:#2d6b84}}.aside{{border-color:#69826a}}
.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:1rem}}.card{{background:white;padding:1.3rem;border:1px solid #cbd2d2;border-radius:8px}}.card b{{display:block;font-size:1.8rem;line-height:1.3}}.scope,figcaption{{font-size:.85rem;color:var(--muted)}}.scroll{{overflow-x:auto}}table{{width:100%;border-collapse:collapse;background:white;font-size:.87rem}}th,td{{text-align:left;padding:.55rem .7rem;border-bottom:1px solid #d5dcdd;vertical-align:top}}th{{background:#e6ecee}}figure{{margin:2rem 0}}figure img{{width:100%;height:auto;display:block;background:white}}figcaption{{padding:.5rem .3rem}}code,pre{{font-size:.88em;background:#e8eceb}}pre{{padding:1rem;overflow:auto}}details{{padding:1rem;background:white;margin:1rem 0}}summary{{cursor:pointer;font-weight:700}}li{{margin:.5rem 0}}.skip{{position:absolute;left:-9999px}}.skip:focus{{left:1rem;top:1rem;background:white}}footer{{font-size:.88rem}}
@media print{{nav,.skip{{display:none}}body{{background:white;font-size:10pt}}header,main,footer{{padding:0}}h1{{font-size:27pt}}h2{{break-after:avoid;scroll-margin-top:0}}figure,.card{{break-inside:avoid}}.scroll{{overflow:visible}}table{{font-size:8pt}}details{{display:block}}a{{color:inherit}}}}
</style></head><body><a class="skip" href="#main">Skip to report</a>
<header><p class="kicker">Research notebook → experiments → teaching report · 7 September 2026</p><h1>Is CEBRA the problem?</h1><p class="lead">A controlled investigation of endpoint information, contrastive objectives, model capacity, cue time and synthetic population construction.</p>
<div class="warning"><b>Read this before the scores.</b> We predict inferred ordered <b>(start, goal)</b>, not a navigation path. Evaluation rows are assembled using their <b>known true condition</b> from different sessions. This is conditional synthetic separability—not decoding one unknown real trial. Every new comparison uses an already inspected development set.</div>
<div class="cards"><div class="card"><b>195 units</b>58 session labels; fixed original panel</div><div class="card"><b>15,553 sources</b>12,288 training / 3,265 development</div><div class="card"><b>{method_count} settings</b>fixed-setting method screen, all reported</div><div class="card"><b>{duration:.1f} min</b>sum of successful phase wall times; not just GPU kernels</div></div></header>
<nav aria-label="Report sections"><a href="#answer">Answer</a><a href="#design">Data &amp; design</a><a href="#models">Models</a><a href="#screen">Results</a><a href="#diagnosis">Diagnosis</a><a href="#ce-followup">CE follow-up</a><a href="#inside">Inside the models</a><a href="#student">Student comparison</a><a href="#scaling">Scaling</a><a href="#nulls">Nulls</a><a href="#journal">Research trail</a><a href="#limits">Limits &amp; next steps</a><a href="#reproduce">Reproduce</a></nav>
<main id="main"><section id="answer"><h2>1. The answer, at the right level of certainty</h2>
<p><b>Do not conclude that CEBRA is intrinsically broken.</b> A CEBRA synthetic positive control reached 100% on new draws of a strong condition signal; constant features produced exactly 3.33% chance. Real-data performance depends on the representation objective, information window, training duration and decoder—not just the method name.</p>
<p>At the common 3,000-update comparison, PCA8/bin scores <b>{pca}</b>, legacy Behavior at τ=1 <b>{behavior}</b>, time-matched Behavior at τ=.3 <b>{same}</b>, whole-cue Behavior <b>{cbwhole}</b>, and the binwise cross-entropy encoder <b>{ce}</b>. The descriptively highest screened setting is <b>{html.escape(NAMES[best])}</b> ({pct(avg(groups[best,]))}). This ranking is a development observation, not independent evidence of method superiority.</p>
<div class="finding"><b>A key diagnostic result:</b> matching positive examples by pair <em>and cue bin</em>, while retaining global negatives, reaches <b>{early_positive}</b> at 250 updates—close to the PCA baseline. Its later checkpoints deteriorate. This implicates the original time-mixing objective and overtraining, rather than an inherent inability of CEBRA to represent endpoint information. This early checkpoint is now an inspected development result, not a newly selected confirmatory winner.</div>
<p>More importantly, good endpoint decoding does not answer the thesis question of <b>path information beyond endpoints</b>. The task here is a diagnostic stepping stone, not evidence for planning or H1.</p></section>
<section id="design"><h2>2. What one example actually is</h2>
<ol><li>A <b>source</b> is a real behavioral trial with a session identity. Its start is inferred from the preceding successful trial's marker; its goal from the current marker. These semantics are provisional.</li><li>Only eligible original-training trials are used: successful current and preceding trials, sequential in the same session, required QC checks and a complete current cue of at least one second. The previous trial supplies a label, not spike features.</li><li>Count spikes in ten half-open 100 ms bins from cue onset: [0,.1), …, [.9,1). A cell contributes ten counts.</li><li>Split sources <b>before</b> assembly. For a condition such as 2→5, draw one matching source per session and retain that session's selected cells and all bins together.</li><li>Concatenate the session blocks: one artificial example is <b>195 cells × 10 bins</b>. Repeat 16 times/class for training (480 rows) and 8 times/class for development (240 rows), for three seeds.</li></ol>
<pre>real sources ── source split ─┬─ training pools ── conditional assembly ── fit preprocessing/model/readout
                             └─ development pools ── conditional assembly ── transform and predict only
condition label ───────────────────────↑ selects matching components on BOTH sides</pre>
<p><b>ML analogy:</b> imagine a dataset assembled by taking one feature block from each of 58 documents known to have the same topic. You can measure topic information in the assembled vector, but it is not a classifier for one naturally occurring document. Cross-document co-occurrence is manufactured by construction.</p>
<p>The inner split is session-and-condition-stratified with frozen seed 20260907. All original validation/test features remain excluded. Same-source bins never cross this split. Success-conditioned eligibility, place-cell selection, previous/current label dependence and session drift are still possible sources of bias.</p>
<div class="aside"><b>Three distinct sample counts:</b> 195 units are channels; 15,553 source trials are recorded observations across sessions; 480/240 pseudorows are synthetic recombinations. None of these equals 480 independent simultaneous-population trials.</div></section>
<section id="models"><h2>3. The models in ML terms</h2>
<h3>PCA versus CEBRA versus a classifier</h3><ul>
<li><b>PCA</b> learns high-variance linear directions after train-only count standardization. Here eight dimensions are learned from single-bin 195-vectors, then ten embeddings are concatenated into <b>80 readout features</b>. This is not an eight-dimensional whole-trial representation.</li>
<li><b>CEBRA</b> learns a nonlinear metric from positive/negative sampling. Its original encoder is <code>195 → 32 → 32 → 16 → 8</code>, GELU nonlinearities, then unit normalization: 7,992 parameters. It sees <b>one bin at a time</b>, not a recurrent sequence or attention window.</li>
<li><b>Contrastive objective:</b> increase similarity to sampled positives relative to negatives. CEBRA's installed cosine criterion uses <code>−similarity(ref,pos)/τ + logsumexp(similarity(ref,negatives)/τ)</code>. Which examples count as positives determines what should be invariant.</li>
<li><b>Time positives</b> are the next cue bin within the same pseudotrial. <b>Behavior positives</b> share the pair label but may come from different cue bins. “Same class” is not automatically “same latent state.”</li>
<li><b>Cross-entropy control</b> uses the same binwise encoder but a 30-way linear head on the concatenated whole cue. It asks the network to classify the complete example, not to make every bin look like every same-label bin. Its loss granularity, batch size and additional head parameters differ; this is a capability control, not an isolated loss-only experiment.</li>
<li><b>Whole-cue controls</b> flatten all 1,950 counts first, then learn an eight-dimensional representation. They change input context, parameter count and readout dimension. Report them separately from strict binwise ablations.</li></ul>
<p>The new common learned-representation readout is train-fitted StandardScaler + multinomial logistic regression, <b>C=.01</b>. This was chosen from the previous development diagnosis, not independently preregistered. LDA, shrinkage LDA, PLS8 and RBF SVM are fixed comparator recipes, not exhaustively tuned families.</p>
<h3>Why not immediately try LFADS or GPFA?</h3><p>The present data do not establish simultaneous cross-session population activity. Models designed to infer single-trial population dynamics would invite an interpretation unsupported by the observation design. First test simple condition decoders and the concrete CEBRA mismatches.</p></section>
<section id="screen"><h2>4. Results: first retain the original baseline</h2>{original_table}<p>Original readout C=1 above; new common C=.01 below. Do not attribute this decoder change to encoder learning. All new neural settings below use 3,000 updates; longer-training diagnostics appear separately.</p>{screen}
<p><b>How to read the columns:</b> joint chance = 1/30 = 3.33%; start/goal chance = 1/6 = 16.67%. “Start from joint” extracts the start of the predicted pair—it is not a separately fitted start classifier. Uniform joint log loss = log(30) ≈ 3.401; confident wrong probabilities can be worse than uniform despite above-chance accuracy. SVM margins were not turned into unvalidated probabilities.</p></section>
<section id="diagnosis"><h2>5. Diagnosing the gap, not merely finding a winner</h2><h3>Training longer: does the objective help the target?</h3>{check}
<p>A rising training-readout score with a falling development-readout score is overfitting of the <b>combined representation/readout pipeline</b>. Declining InfoNCE while endpoint decoding worsens shows that progress on the training objective is not progress on this generalization question. It does not by itself prove that every neuron feature is memorized or that CEBRA cannot work elsewhere.</p>
<h3>One-change contrasts and deliberate non-matched controls</h3>{ablation_table(groups)}
<p><b>Sampler precision matters:</b> CEBRA contrasts every reference with every negative, a B×B matrix. Matching only each reference's paired negative would leave the denominator time-mixed. The matched variant draws one bin per reference batch; the grouped-reference/global-negative bridge separates batching from negative conditioning. Self positives and same-label negatives remain permitted, as in the legacy sampler; narrowing the positive pool also changes its self-match rate.</p>
<p><b>Temperature</b> scales similarity logits and hence gradients and neighborhood pressure; lower is not universally better. <b>Width</b> changes network capacity. <b>Latent dimension</b> also changes the final readout feature count and, in this stock offset1 architecture, the preceding hidden layer (16 → 32 when output8 → 16). It is not a pure output-width-only intervention. A common regularizer is fair as a fixed recipe, but not equal effective complexity across dimensions.</p></section>
<section id="ce-followup"><h2>5b. Was the supervised MLP also trained too long?</h2><p>The poor 3,000-update CE endpoint was not enough to reject supervised networks. At 128 complete examples/update and 480 training rows, that is about <b>800 passes through the artificial training set</b>. CEBRA instead samples reference bins plus positives/negatives; equal updates are not equal exposure. The one allowed adaptive follow-up therefore replayed both CE input windows, increased binwise weight decay from .001 to .1, and tested the already saved 64-pseudorows/class assembly. No further neural fit expansion followed.</p>{followup}<p>These results distinguish early training from final-checkpoint performance. The common fixed readout and the actual trained head are both retained; neither is selected separately per configuration. Larger synthetic assemblies simultaneously reduce repeats per artificial example and increase use of the fixed recorded source pool. These curves are diagnostics, not independently validated hyperparameters.</p><div class="finding"><b>Follow-up outcome:</b> earlier checkpoints only modestly improved binwise CE; more recombinations helped substantially but did not close the PCA gap. Weight decay0.1 over-regularized this recipe to chance. The simple explanation “CE only needed early stopping or much stronger regularization” was insufficient here. Moderate regularization and other architectures remain untested; these results do not reject supervised neural networks as a family.</div></section>
<section id="inside"><h2>6. Look inside: accessible information, not a circuit diagram</h2>{probes}
<p>A hidden-layer probe is analogous to linear probing a transformer's intermediate residual stream. It asks: <em>can a new linear readout extract the target from these coordinates on development examples?</em> It does not tell us what a biological neuron “means.” Earlier layers have different feature budgets, so a higher score alone is not a controlled localization of information loss.</p>
<p>The pre-normalization versus normalized comparison is sharper: both have eight coordinates per bin. Unit normalization retains direction but removes vector length. If the pre-norm probe works better, useful linear-readout information may reside in that radial degree of freedom or the resulting geometry. Coordinate standardization and finite-sample regularization still influence this contrast. Here pre-norm probing improves legacy Behavior only slightly and worsens the time-matched encoder, so final unit normalization alone does not explain the large gap.</p>
<p>Spectral concentration is summarized by the <b>participation ratio</b>, 1/Σp² for normalized variance eigenvalues p. A ratio near three means variance is concentrated in roughly three directions—not “only three classes are represented,” not mutual information, and not proof of total collapse. Learned coordinates can rotate between seeds, so dimensions are not named biological axes.</p></section>
<section id="student"><h2>7. A fairer comparison with the previous student</h2>{student}
<p>The separate-goal LDA mean peaks descriptively at <b>{peak_goal * 0.1:.1f}–{(peak_goal + 1) * 0.1:.1f} s</b> ({pct(series["goal"][peak_goal])}). This is a six-class, single-bin result. It cannot be compared directly with a 30-class joint score or an 80-feature whole-cue decoder.</p>
<p><b>What was matched:</b> our 195 cells, identical source splits, identical pseudo arrays and cue bins, with separately fitted start, goal and joint LDA. The modern factorized comparator multiplies separate start/goal probabilities and renormalizes over the 30 valid unequal pairs; it is not the student's heuristic collision repair.</p>
<p><b>What was not replicated:</b> the student's exact historical cell selection (reported 233), preprocessing artifacts, bootstrap history and ten-fold evaluation. Those inputs/results were not recovered. In the public notebook at the audited commit, pooled-time-bin cell 70 uses row-index folds that can put bins of one trial on both sides. That concrete leakage finding does <b>not</b> invalidate every separate per-bin historical analysis by association.</p>
<div class="warning">The later-cue goal profile is compatible with current-cue sensory/task information. The early start profile may include previous-goal/location/history information. Neither pattern establishes prospective planning, a navigated path, or causal memory mechanisms.</div></section>
<section id="scaling"><h2>8. What scales: recordings, channels, or recombinations?</h2>{scaling}
<p><b>Source sweep:</b> nested fractions of inner-training sources with at least one source per session/condition; actual counts differ from the requested percentages. <b>Unit sweep:</b> nested random channels with identical source arrays before slicing; it also changes represented sessions and input-layer parameter count. <b>Pseudorow sweep:</b> more combinations of the same available source pool; it can expose more distinct available sources to the model without collecting any new biological data.</p>
<p>The 16-to-64-row/class change increases mean distinct training sources actually used from about <b>10,889 to 12,279</b>, out of the same 12,288 available. Its gain therefore mixes broader use of existing recordings with recombination/optimization effects; it is not a pure synthetic-sample-count intervention. No new biological observations were collected.</p>
<p>These distinctions explain why additional synthetic rows can help optimization or population averaging without increasing evidence for a simultaneous circuit. Three seeds describe assembly and optimization sensitivity; they are not a source-aware confidence interval.</p></section>
<section id="nulls"><h2>9. Try to make the result disappear</h2>{nulls}
<p>The fixed null panel was selected before the new real-data screen: PCA8/bin, time-matched τ=.3 CEBRA, and binwise CE, all three seeds. Labels are shuffled at source level <b>before</b> assembly and learned preprocessing. Shuffling existing pseudo-row labels after assembly would answer a different question and leave label-conditioned construction intact.</p>
<p>These five permutations are a falsification diagnostic. They are not a calibrated significance test, do not preserve trial-history dependence, and were not rerun for an adaptively chosen “winner.” Above-null performance only supports the limited conditional-assembly information claim.</p></section>
<section id="journal"><h2>10. The research trail: what changed, and why</h2>
<ol><li><b>Observation:</b> original CEBRA underperformed PCA; stronger decoder regularization helped partially. Working hypotheses were objective/sampling mismatch, optimization, bottleneck/normalization, and assembly limitations.</li>
<li><b>Independent challenge before fitting:</b> mechanism/literature, source-safety and methodological reviewers emphasized inspected-development status, label-conditioned evaluation, source reuse and time dependence. Added a temporal support audit and bounded sensitivity split.</li>
<li><b>Implementation falsification:</b> caught the all-to-all-negative sampler issue before fitting it. Added the bridge control and B×B sampler test, then checked synthetic signal, constant chance, normalization probes and old checkpoint parity.</li>
<li><b>Checkpoint readout first:</b> inspected original training trajectories with the common readout rather than assuming the last checkpoint is best. No encoder retraining was needed for that question.</li>
<li><b>Fixed screen:</b> ran simple alternatives, explicit sampler/temperature/capacity/context ablations and CE controls without validation early stopping. Retained every setting and every seed, not only favorable results.</li>
<li><b>Source-aware sensitivity and falsification:</b> separated source availability, channel count and recombination count; checked chronology and fully refitted the predeclared null panel.</li>
<li><b>One adaptive follow-up:</b> poor final CE performance prompted the four declared early-training/regularization/augmentation recipes, with exact replay checks and both readouts retained. These are separate from the fixed initial screen.</li>
<li><b>Stopping rule:</b> this is a bounded diagnostic study, not a search for a CEBRA setting that must win. Future tuning needs training-only/nested selection and a genuinely independent evaluation strategy; reusing these curves cannot manufacture one.</li></ol>
<p>Initial static checking failed on third-party dynamic typing and array annotations before any new fit. Those receipts are retained. Narrow API annotation fixes and runtime dataset guards produced a clean typecheck; 12 tests and the synthetic controls passed. The independent implementation reviewer confirmed the sampler and source/target flows. Completed phase details:</p>{provenance}
<p><b>Independent recomputation passed:</b> {validation["artifact_hashes"]:,} fitted-study artifact hashes, {validation["metrics"]:,} metric rows, {validation["checked_session_source_components"]:,} session/source components, {validation["training_only_scalers"]} train-only input scalers, {validation["ce_head_cpu_replays"]} CPU head replays, {validation["cross_temporal_entries"]} cross-temporal entries and {validation["parity_checks"]} checkpoint reload checks. Six CE replay fits also matched original final weights and predictions exactly. Fresh read-only artifact/content review returned no findings; this is not an independent biological replication.</p>
<p>The original checkout and original run artifacts were preserved. Work remains on <code>baseline/start-goal-cebra</code> in its isolated worktree. No original validation/test features were used and no persistent server was started.</p></section>
<section id="limits"><h2>11. What this does—and does not—teach us</h2><h3>Defensible conclusions</h3>
<ul><li>Endpoint condition information is accessible from this source-safe, cross-session assembly design.</li><li>The checkpoint, sampler, temperature, capacity, context and probe comparisons show how these specific recipes behave on an inspected development set.</li><li>A good neural embedding must be assessed against simpler alternatives on matched inputs, dimensions and evaluation—not only its training loss or visualization.</li></ul>
<h3>Still unresolved</h3><ul><li>No clean confirmatory ranking, p-value, animal/session generalization or source-aware interval follows from the three seeds. The original test also had earlier project exposure, although it was not used here.</li><li>Label-conditioned assembly is not unknown-real-trial deployment. Pseudopopulations cannot reconstruct simultaneous cross-session noise covariance.</li><li>Start/goal marker semantics and simultaneous recording metadata remain incompletely verified. Eligibility and place-cell selection limit generality.</li><li>Chronological-within-condition sensitivity is weaker than a strict contiguous-time or session-held-out evaluation. It cannot remove all serial/history confounding.</li><li>Linear probes measure accessible target information under their own regularization, not causal encoding or unique biological mechanisms.</li><li>The study does not predict actual paths, nor test path information conditional on start and goal. Goal decoding can reflect the displayed cue.</li></ul>
<h3>Recommended next move</h3><ol><li><b>For a working endpoint baseline:</b> retain the simple PCA/logistic recipe, with exact source-level provenance and a clearly named development endpoint. Do not replace it merely because a nonlinear method is more modern.</li><li><b>For representation research:</b> prioritize the matched contrasts above. Distinguish “CEBRA on whole examples” from forcing every local bin to identify a complete pair. Freeze selection rules inside training before another broad search.</li><li><b>For the thesis:</b> verify marker semantics and recording metadata, define actual path labels and their endpoint-conditioned alternatives, and establish a support-feasible independent evaluation. That changes the scientific question; higher endpoint accuracy alone does not advance H1.</li></ol></section>
<section id="reproduce"><h2>12. Reproduce, audit, and read further</h2><p>This file is self-contained: figures are embedded and no script/font/CDN is required. <a download="endpoint_experiment_metrics.csv" href="data:text/csv;base64,{csvdata}">Download every metric row as CSV</a> ({len(rows):,} rows, including training, probes and nulls).</p>
<pre>cd /home/hongyi-home-lab/neuro_science-start-goal-cebra
export PYTHONNOUSERSITE=1 OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2
PY=/home/hongyi-home-lab/neuro_science/scratch/v6-v9-runtime/bin/python
$PY -m unittest scripts.test_start_goal_autoresearch scripts.test_start_goal_cebra_baseline
$PY -m scripts.start_goal_autoresearch --phase smoke --output-dir outputs/NEW-RUN/00-smoke
# Then phase baseline, cebra, supervised, scaling, null in distinct NEW directories.
$PY -m scripts.start_goal_ce_followup --study-dir outputs/NEW-RUN
# The retained verifier resolves its own study directory; copy it into NEW-RUN for a rerun.
$PY outputs/start-goal-autoresearch-20260907/verify_study.py
$PY -m scripts.render_start_goal_autoresearch --study-dir outputs/start-goal-autoresearch-20260907</pre>
<p>Output directories must be new; existing artifacts are never overwritten by a training phase. Per-phase manifests record inputs, executable, package versions, GPU, configuration, dirty Git state and wall time. Code snapshots, hashes, checkpoints, scalers, prediction arrays, decoder artifacts, source components, support/reuse summaries and failures remain under the ignored study output directory. Load only these trusted local model artifacts; joblib/PyTorch files are not safe interchange formats for unknown downloads.</p>
<p>Runtime: CEBRA 0.6.1, PyTorch 2.12.0, NumPy 2.3.4, scikit-learn 1.7.2, RTX 2070. Sources were reused from the frozen baseline, not reimported. The build script and the Markdown pre-fit plan/journal preserve the process alongside this teaching artifact.</p>
<ul><li><a href="https://www.nature.com/articles/s41586-023-06031-6">CEBRA: Learnable latent embeddings for joint behavioural and neural analysis</a> (Nature, 2023).</li>
<li><a href="https://cebra.ai/docs/usage.html">Official CEBRA usage</a> · <a href="https://cebra.ai/docs/api/sklearn/cebra.html">API and temperature/supervision parameters</a>. Executed behavior was checked against installed 0.6.1, not assumed from current web docs.</li>
<li><a href="https://github.com/AdaptiveMotorControlLab/CEBRA/blob/main/cebra/models/criterions.py">CEBRA criterion source</a> · <a href="https://github.com/AdaptiveMotorControlLab/CEBRA/blob/main/cebra/distributions/discrete.py">Discrete sampling source</a>.</li>
<li><a href="https://www.nature.com/articles/s41592-018-0109-9">LFADS: Inferring single-trial neural population dynamics using sequential auto-encoders</a> (Nature Methods, 2018).</li>
<li><a href="https://github.com/josephchengyx/Hippocampus_Decoding/blob/2f12016c58472888b83298d163be1daaf5291a1e/neurosci_2023_pseudopop.ipynb">Audited student notebook at the inspected commit</a>; code inspection, not execution or exact historical replication.</li></ul></section></main>
<footer><p>Built {datetime.now(timezone.utc).isoformat()} · source-safe endpoint development study · research trajectory preserved in <code>docs/reports/start-goal-autoresearch-plan.md</code> and <code>start-goal-autoresearch-journal.md</code>.</p><p><b>Bottom line:</b> choose the method that answers the controlled question with the least unsupported interpretation. Endpoint separability is real evidence about this benchmark; it is not yet a story about prospective paths or planning.</p></footer></body></html>"""
    path = study / "endpoint-research-report.html"
    path.write_text(content, encoding="utf-8")
    print(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--study-dir", type=Path, required=True)
    args = parser.parse_args()
    try:
        study = args.study_dir.resolve()
        validation = json.loads((study / "validation.json").read_text())
        build(study, validation)
    except Exception as exc:
        raise SystemExit(f"Report build failed: {exc}") from exc


if __name__ == "__main__":
    main()
