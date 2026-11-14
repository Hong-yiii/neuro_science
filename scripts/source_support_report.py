"""Aggregate-only figures and offline report for the declared source-support study."""

from __future__ import annotations

import base64
import html
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from neuro.studies.source_support_ablation import (
    ARMS,
    PAIRS9,
    sha,
    write_csv,
    write_json,
)

COLORS = {"raw": "#245a81", "pca": "#57986c", "cebra": "#b44b43", "lda": "#8b75aa"}
REPS = tuple(COLORS)
SHORT = (
    "A: 30 / 27",
    "B: 9 / 27",
    "C: 9 / 144",
    "D: 9 / 43",
    "E: 9 / 80",
    "F: balanced",
    "G: unique 3",
    "H: recombined 3",
)
CAPTION = "Exposed development; condition-matched pseudopopulations. Seeds are computational variation, not biological uncertainty."


def table(rows, columns=None):
    if not rows:
        return "<p>No records.</p>"
    columns = list(rows[0]) if columns is None else columns

    def fmt(x):
        if isinstance(x, (float, np.floating)):
            return f"{x:.4g}"
        return str(x)

    return (
        "<table><thead><tr>"
        + "".join(f"<th>{html.escape(c)}</th>" for c in columns)
        + "</tr></thead><tbody>"
        + "".join(
            "<tr>"
            + "".join(f"<td>{html.escape(fmt(r.get(c, '')))}</td>" for c in columns)
            + "</tr>"
            for r in rows
        )
        + "</tbody></table>"
    )


def summaries(metrics):
    observed = [r for r in metrics if r["world"] == "observed"]
    result = []
    for arm in ARMS:
        for head in ("pair", "start", "goal"):
            for rep in REPS:
                rows = [
                    r
                    for r in observed
                    if (r["arm"], r["head"], r["representation"]) == (arm, head, rep)
                ]
                if len(rows) != 3 or sorted(r["seed"] for r in rows) != [0, 1, 2]:
                    raise ValueError("missing or duplicate observed result")
                result.append(
                    {
                        "arm": arm,
                        "head": head,
                        "representation": rep,
                        "mean_BA_percent": 100
                        * np.mean([r["balanced_accuracy"] for r in rows]),
                        "min_BA_percent": 100
                        * min(r["balanced_accuracy"] for r in rows),
                        "max_BA_percent": 100
                        * max(r["balanced_accuracy"] for r in rows),
                        "mean_log_loss": np.mean([r["log_loss"] for r in rows]),
                        "mean_macro_F1": np.mean([r["macro_f1"] for r in rows]),
                        "mean_train_BA_percent": 100
                        * np.mean([r["train_BA"] for r in rows]),
                    }
                )
    return result


def paired_contrasts(metrics):
    rows = []
    indexed = {
        (r["arm"], r["seed"], r["representation"], r["head"]): r
        for r in metrics
        if r["world"] == "observed"
    }
    for label, left, right in (
        ("C-D: additional columns", ARMS[2], ARMS[3]),
        ("F-E: balanced allocation", ARMS[5], ARMS[4]),
        ("H-G: recombination", ARMS[7], ARMS[6]),
    ):
        for head in ("pair", "start", "goal"):
            for rep in REPS:
                for seed in (0, 1, 2):
                    a, b = (
                        indexed[left, seed, rep, head],
                        indexed[right, seed, rep, head],
                    )
                    rows.append(
                        {
                            "contrast": label,
                            "head": head,
                            "representation": rep,
                            "seed": seed,
                            "BA_difference_pp": 100
                            * (a["balanced_accuracy"] - b["balanced_accuracy"]),
                            "log_loss_difference": a["log_loss"] - b["log_loss"],
                        }
                    )
    return rows


def make_figures(results, meta, out):
    out = Path(out)
    images = out / "images"
    images.mkdir(parents=True, exist_ok=False)
    plt.rcParams.update(
        {"font.size": 10, "axes.spines.top": False, "axes.spines.right": False}
    )
    records = []

    def save(fig, name, caption, group="overview"):
        fig.savefig(images / name, dpi=130, bbox_inches="tight", facecolor="white")
        plt.close(fig)
        records.append(
            {
                "file": "images/" + name,
                "caption": caption,
                "group": group,
                "sha256": sha(images / name),
            }
        )

    fig, ax = plt.subplots(figsize=(10, 5), layout="constrained")
    rectangles = meta["rectangles"]
    labels = sorted({r["starts"] for r in rectangles})
    arr = np.array(
        [
            [
                next(
                    r["units"]
                    for r in rectangles
                    if r["starts"] == s and r["minimum_train"] == n
                )
                for n in (2, 3, 4, 5)
            ]
            for s in labels
        ]
    )
    im = ax.imshow(arr, aspect="auto", cmap="viridis")
    ax.set(
        xticks=range(4),
        xticklabels=[2, 3, 4, 5],
        yticks=range(20),
        yticklabels=labels,
        xlabel="Minimum distinct training sources per session × pair",
        ylabel="Three starts (goals are complementary)",
        title="Metadata availability of all twenty 3 × 3 rectangles",
    )
    for i in range(20):
        for j in range(4):
            ax.text(
                j,
                i,
                str(arr[i, j]),
                ha="center",
                va="center",
                fontsize=8,
                color="white" if arr[i, j] < 80 else "black",
            )
    fig.colorbar(im, ax=ax, label="Retained unit columns")
    save(
        fig,
        "rectangle_availability.png",
        "Frozen assignments and global contributor embargo; >=1 development source per pool. Values count recorded columns, not model performance. Minimum five is infeasible for every disjoint rectangle.",
    )

    pool = meta["pool_table"]
    sessions = sorted({r["session"] for r in pool})
    pairs = sorted({r["pair"] for r in pool})
    fig, axes = plt.subplots(1, 2, figsize=(15, 13), layout="constrained")
    for ax, field, title in zip(
        axes,
        ("train_after_embargo", "development"),
        ("Training after global embargo", "Exposed development"),
        strict=True,
    ):
        matrix = np.array(
            [
                [
                    next(r[field] for r in pool if r["session"] == s and r["pair"] == p)
                    for p in pairs
                ]
                for s in sessions
            ]
        )
        im = ax.imshow(matrix, aspect="auto", cmap="magma", vmin=0)
        ax.set(
            xticks=range(30),
            xticklabels=pairs,
            yticks=range(58),
            yticklabels=sessions,
            title=title,
            xlabel="Ordered start → goal",
            ylabel="Session alias",
        )
        ax.tick_params(axis="x", labelrotation=90, labelsize=7)
        ax.tick_params(axis="y", labelsize=6)
        for tick, pair in zip(ax.get_xticklabels(), pairs, strict=True):
            if pair in PAIRS9:
                tick.set_color("#196e34")
                tick.set_fontweight("bold")
        fig.colorbar(im, ax=ax, label="Distinct eligible current trials")
    save(
        fig,
        "source_support.png",
        "All58sessions ×30pairs, including excluded pools; counts are real current sources, not pseudorows. Green labels identify the frozen nine-pair rectangle. Pre-embargo counts and failure conditions are in the CSV tables.",
    )

    metrics = results["metrics"]
    observed = [r for r in metrics if r["world"] == "observed"]
    for metric, name, ylabel, scale in (
        (
            "balanced_accuracy",
            "performance.png",
            "Development balanced accuracy (%)",
            100,
        ),
        ("log_loss", "log_loss.png", "Development log loss (natural-log units)", 1),
        (
            "train_development_gap",
            "train_development_gap.png",
            "Training − development BA (percentage points)",
            100,
        ),
    ):
        fig, axes = plt.subplots(3, 1, figsize=(13, 12), layout="constrained")
        for ax, head in zip(axes, ("pair", "start", "goal"), strict=True):
            for j, rep in enumerate(REPS):
                for i, arm in enumerate(ARMS):
                    rows = [
                        r
                        for r in observed
                        if (r["arm"], r["head"], r["representation"])
                        == (arm, head, rep)
                    ]
                    values = [scale * r[metric] for r in rows]
                    x = i + (j - 1.5) * 0.16
                    ax.scatter(
                        [x] * 3,
                        values,
                        color=COLORS[rep],
                        s=24,
                        marker="o",
                        alpha=0.6,
                        label=rep if i == 0 else None,
                    )
                    ax.plot(
                        [x - 0.065, x + 0.065],
                        [np.mean(values)] * 2,
                        color=COLORS[rep],
                        lw=3,
                    )
            if metric != "train_development_gap":
                cls = [30 if head == "pair" else 6] + [9 if head == "pair" else 3] * 7
                references = [
                    100 / k if metric == "balanced_accuracy" else np.log(k) for k in cls
                ]
                ax.plot(range(8), references, "k--", lw=1, label="uniform reference")
            else:
                ax.axhline(0, color="black", lw=1)
            if metric == "log_loss":
                ax.set_yscale("log")
            ax.set(
                xticks=range(8),
                xticklabels=SHORT,
                ylabel=ylabel,
                title=head + " readout",
            )
        axes[0].legend(ncol=5)
        save(
            fig,
            name,
            "All24 observed cases; three dots per arm/family are computational seeds0–2, short bars are means. Whole-cue0–1s readouts. A changes target/cohort; only declared within-task contrasts are paired. "
            + CAPTION,
        )

    contrasts = paired_contrasts(metrics)
    fig, axes = plt.subplots(1, 2, figsize=(13, 5), layout="constrained")
    labels = list(dict.fromkeys(r["contrast"] for r in contrasts))
    for ax, field, ylabel in zip(
        axes,
        ("BA_difference_pp", "log_loss_difference"),
        (
            "Pair9 BA difference (pp; positive favors first arm)",
            "Pair9 log-loss difference (negative favors first arm)",
        ),
        strict=True,
    ):
        for j, rep in enumerate(REPS):
            for i, contrast in enumerate(labels):
                vals = [
                    r[field]
                    for r in contrasts
                    if r["contrast"] == contrast
                    and r["representation"] == rep
                    and r["head"] == "pair"
                ]
                x = i + (j - 1.5) * 0.15
                ax.scatter(
                    [x] * 3, vals, color=COLORS[rep], label=rep if i == 0 else None
                )
                ax.plot(
                    [x - 0.06, x + 0.06], [np.mean(vals)] * 2, color=COLORS[rep], lw=3
                )
        ax.axhline(0, color="black", lw=1)
        ax.set(
            xticks=range(3),
            xticklabels=[
                "C − D\nAdditional columns",
                "F − E\nBalanced allocation",
                "H − G\nRecombination",
            ],
            ylabel=ylabel,
        )
    axes[0].legend(ncol=4)
    save(
        fig,
        "paired_contrasts.png",
        "Prespecified primary contrasts, pair9 whole-cue readouts, same evaluation and paired computational seeds. Logistic N×C is fixed within the nine-class task. F−E changes allocation and joint combinations; H−G changes recombination and row count on exactly the same three-source pools. No biological confidence interval.",
    )

    for arm in (ARMS[0], ARMS[4], ARMS[6]):
        fig, axes = plt.subplots(1, 3, figsize=(13, 4), layout="constrained")
        for ax, head in zip(axes, ("pair", "start", "goal"), strict=True):
            for j, rep in enumerate(REPS):
                obs = [
                    r["balanced_accuracy"] * 100
                    for r in observed
                    if (r["arm"], r["head"], r["representation"]) == (arm, head, rep)
                ]
                null = [
                    r["balanced_accuracy"] * 100
                    for r in metrics
                    if r["world"] != "observed"
                    and (r["arm"], r["head"], r["representation"]) == (arm, head, rep)
                ]
                if len(null) != 5:
                    raise ValueError("missing permutation diagnostic")
                ax.scatter(
                    [j - 0.12] * 3,
                    obs,
                    color=COLORS[rep],
                    marker="o",
                    label="observed seeds0–2" if j == 0 else None,
                )
                ax.scatter(
                    [j + 0.12] * 5,
                    null,
                    color="#777777",
                    marker="x",
                    label="five source shuffles; seed0" if j == 0 else None,
                )
            n = (
                (30 if head == "pair" else 6)
                if arm == ARMS[0]
                else (9 if head == "pair" else 3)
            )
            ax.axhline(100 / n, ls="--", color="black", lw=1)
            ax.set(
                xticks=range(4),
                xticklabels=REPS,
                ylabel="Development BA (%)",
                title=head,
            )
        fig.suptitle(arm)
        axes[0].legend(fontsize=7)
        save(
            fig,
            "permutation_" + arm[0] + ".png",
            "Observed seed range versus all five frozen within-session/split pair-label permutations, rebuilt before assembly/fitting. Joint pair labels define start/goal. Each world has its own fixed development. These are alignment-breaking diagnostics, not a p-value or biological null distribution.",
        )

    fig, axes = plt.subplots(2, 3, figsize=(14, 8), layout="constrained")
    for row, split in enumerate(("train", "development")):
        for col, arm in enumerate((ARMS[4], ARMS[5], ARMS[6])):
            selected = [
                r
                for r in results["pool_usage"]
                if r["case"] == "observed_seed0_" + arm and r["split"] == split
            ]
            blocks = sorted({r["session"] for r in selected})
            matrix = np.array(
                [
                    [
                        next(
                            r["max_share"]
                            for r in selected
                            if r["session"] == s and r["pair"] == p
                        )
                        for p in PAIRS9
                    ]
                    for s in blocks
                ]
            )
            im = axes[row, col].imshow(
                matrix, vmin=0, vmax=1, aspect="auto", cmap="magma"
            )
            axes[row, col].set(
                xticks=range(9),
                xticklabels=PAIRS9,
                yticks=range(len(blocks)),
                yticklabels=blocks,
                title=f"{arm[0]} / {split}: maximum single-source draw share",
            )
            axes[row, col].tick_params(axis="x", rotation=90, labelsize=7)
            axes[row, col].tick_params(axis="y", labelsize=6)
            fig.colorbar(im, ax=axes[row, col])
    save(
        fig,
        "reuse_maps.png",
        "Same80-column/20-session panel. E: ordinary replacement; F: balanced allocation; G: selected three-source pools with unique training draws. Development is identical across arms and can contain singleton pools. All source counts, including zero use, are exported for every seed/world.",
    )

    fig, axes = plt.subplots(1, 2, figsize=(12, 5), layout="constrained")
    for ax, arm in zip(axes, (ARMS[0], ARMS[4]), strict=True):
        for rep in REPS:
            errors = [
                r
                for r in results["class_errors"]
                if r["case"] == "observed_seed0_" + arm
                and r["head"] == "pair"
                and r["representation"] == rep
            ]
            for r in errors:
                pp = [
                    p
                    for p in results["pool_usage"]
                    if p["case"] == r["case"]
                    and p["split"] == "train"
                    and p["pair"] == r["class"]
                ]
                x = np.mean([p["eligible_sources"] for p in pp])
                ax.scatter(x, 100 * r["error_rate"], color=COLORS[rep], s=25)
                if rep == "cebra":
                    ax.annotate(r["class"], (x, 100 * r["error_rate"]), fontsize=6)
            ax.scatter([], [], color=COLORS[rep], label=rep)
        ax.set(
            xlabel="Mean eligible training trials per session × true pair",
            ylabel="Pair error rate (%)",
            title=arm + " / seed0",
        )
        ax.legend(fontsize=8)
    save(
        fig,
        "support_and_errors.png",
        "Prespecified descriptive class-level support summary, seed0 A/E whole-cue evaluation. Each class has eight development pseudorows; one dot is a class/family, not an independent biological sample. Labels annotate CEBRA points. Endpoints/class difficulty confound this association; all seed/class/source records are in tables. No causal session attribution or significance test.",
    )

    for index in range(0, len(results["learning"]), 8):
        page = results["learning"][index : index + 8]
        fig, axes = plt.subplots(4, 2, figsize=(13, 11), layout="constrained")
        for ax, record in zip(axes.flat, page):
            ax.plot(
                np.arange(1, len(record["loss"]["total"]) + 1),
                record["loss"]["total"],
                lw=0.8,
                color=COLORS["cebra"],
            )
            ax.set(
                title=record["case"],
                xlabel="Optimizer update",
                ylabel="Training InfoNCE loss",
            )
            ax.title.set_fontsize(8)
        for ax in list(axes.flat)[len(page) :]:
            ax.set_visible(False)
        save(
            fig,
            f"learning_{index // 8 + 1}.png",
            "All declared fits, in execution order; actual total training InfoNCE loss at every one of1,000updates. No smoothing or best-fit selection. Loss is optimization evidence; decoder/control results test useful information.",
            "learning",
        )

    for record in results["trajectories"]:
        if not record["case"].startswith("observed_"):
            continue
        fig = plt.figure(figsize=(13, 6), layout="constrained")
        for i, rep in enumerate(("pca", "cebra")):
            ax = fig.add_subplot(1, 2, i + 1, projection="3d")
            labels = sorted(record["coordinates"][rep])
            cmap = plt.get_cmap("tab10" if len(labels) <= 10 else "hsv")
            for j, label in enumerate(labels):
                xyz = np.asarray(record["coordinates"][rep][label])
                color = cmap(j % 10) if len(labels) <= 10 else cmap(j / len(labels))
                ax.plot(*xyz.T, color=color, lw=1.3, label=label)
                ax.scatter(*xyz[0], color=color, marker="o", s=12)
                ax.scatter(*xyz[-1], color=color, marker="^", s=28)
            ax.set(
                xlabel="Coordinate 1",
                ylabel="Coordinate 2",
                zlabel="Coordinate 3",
                title=rep.upper(),
            )
            ax.legend(fontsize=6, ncol=3 if len(labels) > 9 else 2, loc="upper left")
        fig.suptitle(record["case"], fontsize=11)
        save(
            fig,
            "trajectory_" + record["case"] + ".png",
            "Class-mean exposed-development trajectories through the first three native coordinates of a training-fitted eight-dimensional representation. Ten points: cue-bin centers50–950ms; circle=50ms, triangle=950ms. Means over eight constructed rows/class; no uncertainty interval. Axes are unaligned across fits. Not maze movement, simultaneous activity, manifold topology or biological dynamics.",
            "trajectories",
        )

    case_ids = list(dict.fromkeys(r["id"] for r in results["confusions"]))
    for case in case_ids:
        for head in ("pair", "start", "goal"):
            fig, axes = plt.subplots(4, 2, figsize=(11, 13), layout="constrained")
            for i, rep in enumerate(REPS):
                r = next(
                    r
                    for r in results["confusions"]
                    if r["id"] == case
                    and r["head"] == head
                    and r["representation"] == rep
                )
                counts = np.asarray(r["counts"])
                normalized = counts / counts.sum(axis=1, keepdims=True)
                for j, (values, label) in enumerate(
                    ((counts, "count"), (normalized, "row recall"))
                ):
                    ax = axes[i, j]
                    im = ax.imshow(
                        values,
                        cmap="Blues",
                        vmin=0,
                        vmax=1 if j else None,
                        aspect="equal",
                    )
                    ax.set(
                        title=f"{rep.upper()} · {label}",
                        xticks=range(len(values)),
                        xticklabels=r["labels"],
                        yticks=range(len(values)),
                        yticklabels=r["labels"],
                        xlabel="Predicted",
                        ylabel="True",
                    )
                    ax.tick_params(
                        axis="x",
                        labelrotation=90,
                        labelsize=5 if len(values) > 9 else 7,
                    )
                    ax.tick_params(axis="y", labelsize=5 if len(values) > 9 else 7)
                    fig.colorbar(im, ax=ax, fraction=0.035)
            fig.suptitle(case + " / " + head, fontsize=11)
            save(
                fig,
                "confusion_" + case + "_" + head + ".png",
                "Whole-cue held-out constructed rows; true classes on rows, predictions on columns. Left=count, right=row-normalized recall. Every model family and every declared case is retained. Numeric matrices and class denominators are also exported. "
                + CAPTION,
                "confusions",
            )
    return records


def create_report(results, meta, out, *, config, reconstruction_audit):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=False)
    summary, contrasts = (
        summaries(results["metrics"]),
        paired_contrasts(results["metrics"]),
    )
    write_csv(out / "tables/summary.csv", summary)
    write_csv(out / "tables/paired_contrasts.csv", contrasts)
    write_csv(out / "tables/rectangle_availability.csv", meta["rectangles"])
    write_csv(out / "tables/source_support.csv", meta["pool_table"])
    write_csv(out / "tables/session_exclusions.csv", meta["exclusions"])
    unit_table = []
    column_maps = {
        name: {
            u["cell_id"]: i
            for i, u in enumerate(
                [u for u in meta["units"] if u["session_id"] in blocks]
            )
        }
        for name, blocks in meta["cohorts"].items()
    }
    for u in meta["units"]:
        unit_table.append(
            {
                "unit": meta["unit_aliases"][u["cell_id"]],
                "session": meta["aliases"][u["session_id"]],
                **{
                    name + "_included": u["session_id"] in blocks
                    for name, blocks in meta["cohorts"].items()
                },
                **{
                    name + "_column_index": mapping.get(u["cell_id"], "")
                    for name, mapping in column_maps.items()
                },
            }
        )
    write_csv(out / "tables/unit_membership.csv", unit_table)
    traces = []
    for arm in (ARMS[0], ARMS[4], ARMS[6]):
        case = "observed_seed0_" + arm
        case_root = out.parent / "cases" / case
        completion = json.loads((case_root / "completion.json").read_text())
        path = case_root / "development_lineage.json"
        if sha(path) != completion["artifact_sha256"][path.name]:
            raise ValueError("worked trace lineage authentication failed")
        lineage = json.loads(path.read_text())
        row = lineage["rows"][0]
        for block, source in zip(lineage["blocks"], row["source_ids"], strict=True):
            columns = [
                i
                for i, unit in enumerate(lineage["units"])
                if next(u["session_id"] for u in meta["units"] if u["cell_id"] == unit)
                == block
            ]
            use = next(
                r["uses"]
                for r in results["source_usage"]
                if r["case"] == case
                and r["split"] == "development"
                and r["source"] == meta["source_aliases"][source]
            )
            traces.append(
                {
                    "case": case,
                    "row_id": row["row_id"],
                    "pair": row["pair"],
                    "session": meta["aliases"][block],
                    "source": meta["source_aliases"][source],
                    "column_indices": ",".join(map(str, columns)),
                    "appearances_in_development": use,
                }
            )
    write_csv(out / "tables/worked_row_trace.csv", traces)
    for key in (
        "metrics",
        "pool_usage",
        "source_usage",
        "source_errors",
        "class_errors",
        "overlap",
    ):
        write_csv(out / "tables" / (key + ".csv"), results[key])
    for key in ("confusions", "learning", "trajectories"):
        write_json(out / "tables" / (key + ".json"), results[key])
    figures = make_figures(results, meta, out)
    write_json(out / "figure_provenance.json", figures)
    write_json(out / "configuration.json", config)
    # Only safe aggregate reconstruction fields, never paths or actual source IDs.
    safe_audit = {
        k: {
            n: v
            for n, v in a.items()
            if n
            in {
                "events_accepted",
                "tail_spikes",
                "observed_values",
                "unavailable_values",
                "full_exposure",
            }
        }
        for k, a in reconstruction_audit.items()
        if k in {"current", "wide"}
    }
    write_json(out / "reconstruction_accounting.json", safe_audit)
    body = [
        "<h1>Can endpoint learning survive changes to pseudopopulation sampling?</h1>",
        "<p>November10,2026 · New exploratory cue-only training · Eight observed arms, three computational seeds, five source-label diagnostic worlds on three key arms.</p>",
        "<p><strong>Question:</strong> distinguish added recorded columns, balanced source allocation, and synthetic recombination. Starts2,3,5 × goals1,4,6 form the chosen nine conditions. Models are raw + logistic, PCA8 + logistic, CEBRA8 + logistic and raw SVD-LDA. All transformations use training only.</p>",
        "<p>Original global predecessor embargo and frozen exposed development retained. Source metadata selected the panel before neural results. More units, rows, seeds and optimizer updates do not create independent biological trials. Five shuffles are descriptive controls, not p-values.</p>",
        "<h2>All observed whole-cue results</h2>",
        table(summary),
        "<h2>Prespecified paired differences, every seed</h2>",
        table([r for r in contrasts if r["head"] == "pair"]),
        "<p>Positive BA difference favors the first arm; negative log-loss difference favors the first arm. C−D keeps all43sessions/source plans; F−E changes source allocation and combinations; H−G keeps exactly three sources/pool. A/B and C/E are practical panel changes, not isolated causal tests.</p>",
    ]
    for group, title in (
        ("overview", "Support, reuse, performance and controls"),
        ("learning", "Every CEBRA training curve"),
        ("trajectories", "All observed cue-time trajectories"),
        ("confusions", "All count and normalized confusion matrices"),
    ):
        body.append(f"<h2>{title}</h2>")
        for figure in (f for f in figures if f["group"] == group):
            encoded = base64.b64encode((out / figure["file"]).read_bytes()).decode()
            image = f'<figure><img src="data:image/png;base64,{encoded}" alt="{html.escape(figure["file"])}"><figcaption>{html.escape(figure["caption"])}</figcaption></figure>'
            if group in {"trajectories", "confusions"}:
                image = f"<details><summary>{html.escape(Path(figure['file']).stem)}</summary>{image}</details>"
            body.append(image)
    body.extend(
        [
            "<h2>Limits and verification</h2>",
            "<p>The unique arm removes repeated current-source blocks during training assembly; it still uses repeated optimizer/bin exposures and historically exposed development with singleton pools. Source participation in an error is not a causal attribution to a session or trial. Development is assembled with the known condition; these are conditional population assays, not natural unknown-trial prediction.</p>",
            "<p>Trajectories show class means through native PCA/CEBRA coordinates during the first cue second. They are not measured maze paths or simultaneous neural dynamics. Coordinates are not aligned between independently fitted models. Training InfoNCE loss is not decoder performance.</p>",
            "<p>Every new encoder and readout was saved, authenticated and composed again under a no-fitting guard on training and development. Explicit lineage, exact fit accounting, source/input hashes and resource receipts accompany the local run. All declared cases and poor scores are retained. No private historical replay was used.</p>",
            "<p>Machine-readable tables are in the adjacent tables directory. Figure hashes are in figure_provenance.json. The frozen protocol and independently reviewed implementation live in the workspace.</p>",
        ]
    )
    style = "body{font:16px/1.55 system-ui,sans-serif;max-width:1250px;margin:40px auto;padding:0 28px;color:#182a34;background:#fbfaf7}h1{font-size:34px}h2{margin-top:46px}table{border-collapse:collapse;font-size:12px;display:block;overflow:auto;margin:20px 0}th,td{border:1px solid #cbd4d8;padding:6px 9px;text-align:right}th{background:#e5ecee;position:sticky;top:0}img{max-width:100%;height:auto}figure{margin:30px 0}figcaption{font-size:13px;color:#405760}details{margin:16px 0;padding:10px;background:white;border:1px solid #d7dfe2}summary{cursor:pointer;font-weight:600}"
    (out / "report.html").write_text(
        '<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Source support and learning</title><style>'
        + style
        + "</style></head><body>"
        + "\n".join(body)
        + "</body></html>"
    )
    return {"summary": summary, "contrasts": contrasts, "figures": figures}
