"""Aggregate-only report for the fresh class × session study; never fits models."""

from __future__ import annotations

import base64
import csv
import html
import shutil
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from neuro.studies.population_grid import (
    CLASS_COUNTS,
    ROSTERS,
    POLICIES,
    sha,
    write_csv,
    write_json,
)
from scripts.source_support_report import table
from neuro.studies.population_models import ENCODERS, DECODERS, FAMILIES

REPS = ENCODERS
COLORS = {"raw": "#245a81", "pca": "#57986c", "cebra": "#b44b43", "native": "#8b75aa"}

CAPTION = "Cue [0,1) s; ten100-ms bins; frozen exposed development, eight constructed rows/pair. Training-only transforms. Seed variation is computational, not a biological confidence interval."
PCOLORS = {"U2": "#276b91", "R16": "#c26d35", "F16": "#32866e"}


def summaries(metrics):
    grouped = defaultdict(list)
    for r in metrics:
        if r["world"] == "observed":
            grouped[r["arm"], r["head"], r["representation"]].append(r)
    result = []
    for (arm, head, rep), rows in grouped.items():
        assert sorted(r["seed"] for r in rows) == [0, 1, 2]
        r = rows[0]
        result.append(
            dict(
                arm=arm,
                class_count=r["class_count"],
                roster=r["roster"],
                sampling=r["sampling"],
                units=r["units"],
                sessions=r["sessions"],
                head=head,
                representation=rep,
                mean_BA_percent=100 * np.mean([x["balanced_accuracy"] for x in rows]),
                min_BA_percent=100 * min(x["balanced_accuracy"] for x in rows),
                max_BA_percent=100 * max(x["balanced_accuracy"] for x in rows),
                mean_log_loss=None
                if rows[0]["log_loss"] is None
                else np.mean([x["log_loss"] for x in rows]),
                mean_macro_F1=np.mean([x["macro_f1"] for x in rows]),
                mean_train_BA_percent=100 * np.mean([x["train_BA"] for x in rows]),
            )
        )
    assert len(result) == 1296
    return result


def paired_contrasts(metrics):
    lookup = {
        (r["arm"], r["head"], r["representation"], r["seed"]): r
        for r in metrics
        if r["world"] == "observed"
    }
    comparisons = []
    for k in CLASS_COUNTS:
        for roster in ROSTERS:
            for left, right, label in [
                ("R16", "U2", "recombination"),
                ("F16", "R16", "distinct_sources"),
            ]:
                comparisons.append(
                    (
                        k,
                        roster,
                        label,
                        f"K{k}_{roster}_{left}",
                        f"K{k}_{roster}_{right}",
                    )
                )
        for policy in POLICIES:
            for left in ("S67", "S100"):
                comparisons.append(
                    (
                        k,
                        policy,
                        "sessions_" + left,
                        f"K{k}_{left}_{policy}",
                        f"K{k}_S33_{policy}",
                    )
                )
    out = []
    for k, held, label, left, right in comparisons:
        for head in ("pair", "start", "goal"):
            for rep in FAMILIES:
                for seed in (0, 1, 2):
                    a, b = lookup[left, head, rep, seed], lookup[right, head, rep, seed]
                    out.append(
                        dict(
                            class_count=k,
                            held=held,
                            contrast=label,
                            left=left,
                            right=right,
                            head=head,
                            representation=rep,
                            seed=seed,
                            BA_difference_pp=100
                            * (a["balanced_accuracy"] - b["balanced_accuracy"]),
                            log_loss_difference=None
                            if a["log_loss"] is None
                            else a["log_loss"] - b["log_loss"],
                        )
                    )
    return out


def support_tables(meta, design):
    pools, exclusions, units = [], [], []
    for g in design["grid"]:
        k = g["class_count"]
        classes = next(
            p["conditions"] for p in design["panels"] if p["class_count"] == k
        )
        ci = [meta["pairs"].index(c) for c in classes]
        for i, s in enumerate(meta["sessions"]):
            deficient = sum(
                meta["train"][i, c] < 2 or meta["development"][i, c] < 1 for c in ci
            )
            included = meta["aliases"][s] in g["session_aliases"]
            exclusions.append(
                dict(
                    configuration=g["configuration"],
                    session=meta["aliases"][s],
                    included=included,
                    deficient_classes=deficient,
                    reason="included"
                    if included
                    else "insufficient_class_support"
                    if deficient
                    else "roster_rank_cut",
                )
            )
            if included:
                for c in ci:
                    pools.append(
                        dict(
                            configuration=g["configuration"],
                            session=meta["aliases"][s],
                            pair=meta["pairs"][c],
                            train_sources=int(meta["train"][i, c]),
                            development_sources=int(meta["development"][i, c]),
                        )
                    )
        for u in meta["units"]:
            units.append(
                dict(
                    configuration=g["configuration"],
                    unit=meta["unit_aliases"][u["cell_id"]],
                    session=meta["aliases"][u["session_id"]],
                    included=meta["aliases"][u["session_id"]] in g["session_aliases"],
                )
            )
    return pools, exclusions, units


def usage_summary(run):
    grouped = defaultdict(
        lambda: dict(
            eligible=0, used=0, draws=0, repeated=0, max_use=0, pools=0, singletons=0
        )
    )
    with (run / "aggregates/pool_usage.csv").open() as handle:
        for r in csv.DictReader(handle):
            d = grouped[r["case"], r["split"]]
            for field, target in [
                ("eligible_sources", "eligible"),
                ("used", "used"),
                ("draws", "draws"),
                ("repeated", "repeated"),
            ]:
                d[target] += int(r[field])
            d["max_use"] = max(d["max_use"], int(r["max_use"]))
            d["pools"] += 1
            d["singletons"] += int(r["eligible_sources"]) == 1
    return [
        dict(case=c, split=s, **d, reuse_fraction=1 - d["used"] / d["draws"])
        for (c, s), d in grouped.items()
    ]


def make_figures(results, meta, design, usage, out):
    images = out / "images"
    images.mkdir()
    plt.rcParams.update(
        {"font.size": 10, "axes.spines.top": False, "axes.spines.right": False}
    )
    records = []

    def save(fig, name, caption, group="overview"):
        fig.savefig(images / name, dpi=120, bbox_inches="tight", facecolor="white")
        plt.close(fig)
        records.append(
            dict(
                file="images/" + name,
                caption=caption,
                group=group,
                sha256=sha(images / name),
            )
        )

    grid = design["grid"]
    fig, axes = plt.subplots(2, 3, figsize=(13, 7), layout="constrained")
    for ax, field, title in zip(
        axes.flat,
        [
            "units",
            "sessions",
            "train_sources",
            "development_sources",
            "balanced_no_reuse_rows",
            "development_singletons",
        ],
        [
            "Recorded columns",
            "Sessions",
            "Distinct training current sources",
            "Distinct development current sources",
            "Balanced no-reuse complete rows",
            "Singleton development pools",
        ],
    ):
        vals = np.array(
            [
                [
                    next(
                        g[field]
                        for g in grid
                        if g["class_count"] == k and g["roster"] == r
                    )
                    for r in ROSTERS
                ]
                for k in CLASS_COUNTS
            ]
        )
        ax.imshow(vals, cmap="Blues", aspect="auto")
        for (i, j), v in np.ndenumerate(vals):
            ax.text(
                j,
                i,
                str(v),
                ha="center",
                va="center",
                color="white" if v > vals.max() * 0.6 else "black",
            )
        ax.set(
            xticks=range(3),
            xticklabels=["1/3", "2/3", "all"],
            yticks=range(3),
            yticklabels=CLASS_COUNTS,
            xlabel="Fraction of ranked eligible sessions",
            ylabel="Required pair classes",
            title=title,
        )
    save(
        fig,
        "nine_configurations.png",
        "Nine metadata-selected configurations. Source counts are real current trials after global embargo; row capacity is K times the minimum training pool, not total sources. No neural score selected this grid.",
    )
    fig, axes = plt.subplots(2, 2, figsize=(12, 8), layout="constrained")
    frontier = design["class_count_width_frontier"]
    axes[0, 0].plot(
        [p["class_count"] for p in frontier],
        [p["maximum_columns"] for p in frontier],
        "-o",
    )
    axes[0, 0].set(
        xlabel="Required pair classes K",
        ylabel="Maximum available recorded columns",
        title="Exact metadata width optimum",
    )
    for k in CLASS_COUNTS:
        p = [x for x in design["prefix_frontier"] if x["class_count"] == k]
        for ax, y in [
            (axes[0, 1], "units"),
            (axes[1, 0], "train_sources"),
            (axes[1, 1], "classwise_no_reuse_rows"),
        ]:
            ax.plot(
                [x["sessions"] for x in p],
                [x[y] for x in p],
                "-o",
                ms=2,
                label=f"K={k}",
            )
    for ax, y in [
        (axes[0, 1], "Recorded columns"),
        (axes[1, 0], "Distinct training sources"),
        (axes[1, 1], "Class-wise no-reuse complete rows"),
    ]:
        ax.set(xlabel="Included sessions in fixed ranked order", ylabel=y)
        ax.legend()
    save(
        fig,
        "availability_frontiers.png",
        "Exact width optimum under complete support and balanced endpoint-degree constraints. K=6…30 metadata only; models fit only30/20/15. Constraint families are not nested: K6→7 need not decrease. Other panels show every prefix of the fixed harmonic-support-ranked session roster. Class-wise capacity permits unequal numbers of rows/class, unlike the balanced U2 training quota.",
    )
    pools, _, _ = support_tables(meta, design)
    fig, axes = plt.subplots(3, 2, figsize=(13, 11), layout="constrained")
    for i, k in enumerate(CLASS_COUNTS):
        labels = next(
            p["conditions"] for p in design["panels"] if p["class_count"] == k
        )
        sessions = next(
            g["session_aliases"]
            for g in grid
            if g["class_count"] == k and g["roster"] == "S100"
        )
        rows = [r for r in pools if r["configuration"] == f"K{k}_S100"]
        idx = {(r["session"], r["pair"]): r for r in rows}
        for j, field in enumerate(["train_sources", "development_sources"]):
            arr = [[idx[s, c][field] for c in labels] for s in sessions]
            im = axes[i, j].imshow(arr, aspect="auto", cmap="viridis", vmin=0)
            axes[i, j].set(
                title=f"K{k} {field}",
                xticks=range(k),
                xticklabels=labels,
                yticks=range(len(sessions)),
                yticklabels=sessions,
                xlabel="Retained endpoint pair",
                ylabel="Ranked sessions",
            )
            axes[i, j].tick_params(axis="x", labelrotation=90, labelsize=6)
            axes[i, j].tick_params(axis="y", labelsize=5)
            fig.colorbar(im, ax=axes[i, j])
    save(
        fig,
        "source_distributions.png",
        "Distinct current-source counts after the global embargo. Full rosters shown in exact support rank; smaller rosters are prefixes. All classes and sessions are shown, including development singleton pools. Colors count measured sources, not upsampled rows.",
    )
    observed = [r for r in results["metrics"] if r["world"] == "observed"]
    for decoder in DECODERS:
        for head in ("pair", "start", "goal"):
            for metric, label in [
                ("balanced_accuracy", "Development balanced accuracy (%)"),
                ("log_loss", "Development log loss (nats)"),
            ]:
                if decoder == "svm" and metric == "log_loss":
                    continue
                fig, axes = plt.subplots(3, 4, figsize=(15, 10), layout="constrained")
                for i, k in enumerate(CLASS_COUNTS):
                    for j, rep in enumerate(REPS):
                        ax = axes[i, j]
                        for policy in POLICIES:
                            rows = [
                                r
                                for r in observed
                                if r["class_count"] == k
                                and r["head"] == head
                                and r["encoder"] == rep
                                and r["decoder"] == decoder
                                and r["sampling"] == policy
                            ]
                            widths = sorted({r["units"] for r in rows})
                            scale = 100 if metric == "balanced_accuracy" else 1
                            means = [
                                scale
                                * np.mean([r[metric] for r in rows if r["units"] == w])
                                for w in widths
                            ]
                            ax.plot(
                                widths,
                                means,
                                "-o",
                                color=PCOLORS[policy],
                                label=policy,
                                ms=3,
                            )
                            ax.scatter(
                                [r["units"] for r in rows],
                                [scale * r[metric] for r in rows],
                                color=PCOLORS[policy],
                                s=10,
                                alpha=0.6,
                            )
                        classes = k if head == "pair" else 6
                        reference = (
                            100 / classes
                            if metric == "balanced_accuracy"
                            else np.log(classes)
                        )
                        ax.axhline(
                            reference,
                            color="gray",
                            ls=":",
                            label="uniform" if i == j == 0 else None,
                        )
                        if head == "pair" and metric == "balanced_accuracy":
                            ax.axhline(
                                600 / k,
                                color="purple",
                                ls="--",
                                alpha=0.4,
                                label="perfect goal only" if i == j == 0 else None,
                            )
                        ax.set(
                            title=f"K{k} · {rep.upper()}",
                            xlabel="Recorded columns",
                            ylabel=label,
                        )
                axes[0, 0].legend(fontsize=7)
                save(
                    fig,
                    f"performance_{decoder}_{head}_{metric}.png",
                    f"{decoder} / {head} whole-cue readouts; {label}. Lines=three-seed means; dots=all seeds0/1/2. U2 uses two sources once, R16 reuses those same sources eight times, F16 uses all sources. All representations use the named decoder, with training-only feature scaling. Native is pair-supervised and equal-session pooled; CEBRA-Time is time-supervised on concatenated inputs. Uniform references:1/K or1/6 and ln(K) or ln(6). Dashed purple pair reference6/K assumes perfect goal and no start information; mathematical reference, not a fitted baseline. Compare within K: class tasks differ. "
                    + CAPTION,
                )
    fig, axes = plt.subplots(3, 3, figsize=(13, 9), layout="constrained")
    lookup = {(u["case"], u["split"]): u for u in usage}
    for i, k in enumerate(CLASS_COUNTS):
        for j, roster in enumerate(ROSTERS):
            ax = axes[i, j]
            selected = [
                lookup[f"observed_seed0_K{k}_{roster}_{p}", "train"] for p in POLICIES
            ]
            ax.bar(
                np.arange(3) - 0.18,
                [r["used"] for r in selected],
                width=0.36,
                label="distinct current sources",
            )
            ax.bar(
                np.arange(3) + 0.18,
                [r["draws"] for r in selected],
                width=0.36,
                label="source-block appearances",
            )
            ax.set(
                xticks=range(3),
                xticklabels=POLICIES,
                title=f"K{k} {roster}",
                ylabel="Count",
            )
    axes[0, 0].legend(fontsize=7)
    save(
        fig,
        "reuse.png",
        "Actual training source use at seed0. U2/R16 source identities match, with1/8uses each; F16 covers every eligible source. Appearances=count of synthetic rows × included session blocks. Counts are identical across observed seeds, identities may differ. More appearances do not create new measurements; all cases use1000CEBRAupdates.",
    )
    for decoder in DECODERS:
        fig, axes = plt.subplots(3, 2, figsize=(13, 10), layout="constrained")
        for i, k in enumerate(CLASS_COUNTS):
            for j, policy in enumerate(("U2", "F16")):
                ax = axes[i, j]
                for x, rep in enumerate(REPS):
                    rows = [
                        r
                        for r in results["metrics"]
                        if r["arm"] == f"K{k}_S100_{policy}"
                        and r["head"] == "pair"
                        and r["encoder"] == rep
                        and r["decoder"] == decoder
                    ]
                    obs = [
                        100 * r["balanced_accuracy"]
                        for r in rows
                        if r["world"] == "observed"
                    ]
                    null = [
                        100 * r["balanced_accuracy"]
                        for r in rows
                        if r["world"] != "observed"
                    ]
                    assert len(obs) == 3 and len(null) == 5
                    ax.scatter(
                        [x - 0.12] * 3,
                        obs,
                        color=COLORS[rep],
                        label="observed3seeds" if x == 0 else None,
                    )
                    ax.scatter(
                        [x + 0.12] * 5,
                        null,
                        facecolors="none",
                        edgecolors=COLORS[rep],
                        marker="s",
                        label="five label worlds" if x == 0 else None,
                    )
                ax.axhline(100 / k, color="gray", ls=":")
                ax.set(
                    xticks=range(4),
                    xticklabels=REPS,
                    ylabel="Pair balanced accuracy (%)",
                    title=f"K{k} full roster · {policy}",
                )
        axes[0, 0].legend(fontsize=8)
        save(
            fig,
            f"source_label_controls_{decoder}.png",
            f"{decoder} readouts. Joint pair labels permuted within session×split before subset/assembly, seeds60000…60004, model seed0; all five outcomes shown. Observed dots use computational seeds0/1/2. Full roster U2/F16 only; smaller-roster/R16 nulls were not run. No biological p-value. "
            + CAPTION,
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
        fig = plt.figure(figsize=(18, 6), layout="constrained")
        for i, rep in enumerate(("pca", "cebra", "native")):
            ax = fig.add_subplot(1, 3, i + 1, projection="3d")
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
            "Class-mean exposed-development trajectories through the first three native coordinates of a training-fitted seven-dimensional representation. Ten points: cue-bin centers50–950ms; circle=50ms, triangle=950ms. Means over eight constructed rows/class; no uncertainty interval. Axes are unaligned across fits. Not maze movement, simultaneous activity, manifold topology or biological dynamics.",
            "trajectories",
        )

    case_ids = list(
        dict.fromkeys(
            r["id"]
            for r in results["confusions"]
            if r["world"] == "observed" and r["seed"] == 0
        )
    )
    for case in case_ids:
        for decoder in DECODERS:
            head = "pair"
            fig, axes = plt.subplots(4, 2, figsize=(11, 13), layout="constrained")
            for i, rep in enumerate(REPS):
                r = next(
                    r
                    for r in results["confusions"]
                    if r["id"] == case
                    and r["head"] == head
                    and r["encoder"] == rep
                    and r["decoder"] == decoder
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
            fig.suptitle(case + " / " + decoder + " / " + head, fontsize=11)
            save(
                fig,
                "confusion_" + case + "_" + decoder + "_" + head + ".png",
                "Whole-cue held-out constructed rows; true classes on rows, predictions on columns. Left=count, right=row-normalized recall. Rendered matrices show pair prediction for every observed configuration/policy/decoder at seed0. All5328matrices, including seeds1/2 and nulls, are also shown numerically in HTML and saved in JSON. Numeric matrices and class denominators are also exported. "
                + CAPTION,
                "confusions",
            )
    return records


def create_report(results, meta, out, *, config, reconstruction_audit):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=False)
    run = out.parent
    tables = out / "tables"
    tables.mkdir()
    design = config["design"]
    summary = summaries(results["metrics"])
    contrasts = paired_contrasts(results["metrics"])
    usage = usage_summary(run)
    pools, exclusions, units = support_tables(meta, design)
    for name, rows in [
        ("summary", summary),
        ("paired_contrasts", contrasts),
        ("usage_summary", usage),
        ("nine_configurations", design["grid"]),
        ("prefix_frontier", design["prefix_frontier"]),
        ("class_width_frontier", design["class_count_width_frontier"]),
        ("source_support", pools),
        ("session_exclusions", exclusions),
        ("unit_inclusion", units),
    ]:
        write_csv(tables / (name + ".csv"), rows)
    for p in (run / "aggregates").iterdir():
        if p.suffix in (".csv", ".json"):
            shutil.copyfile(p, tables / p.name)
    figures = make_figures(results, meta, design, usage, out)
    write_json(out / "figure_provenance.json", figures)
    write_json(out / "configuration.json", config)
    safe = {
        k: {
            name: value
            for name, value in a["neural"].items()
            if name
            in {
                "events_accepted",
                "tail_spikes",
                "observed_values",
                "unavailable_values",
                "full_exposure",
            }
        }
        for k, a in reconstruction_audit.items()
    }
    write_json(out / "reconstruction_accounting.json", safe)
    pairsummary = [r for r in summary if r["head"] == "pair"]
    body = [
        "<h1>Class requirements, population width and learning</h1>",
        "<p>November11,2026 · New exploratory training on existing cue recordings. Nine class × session configurations, three sampling policies, three computational seeds;30source-label diagnostic cases. All111cases freshly fitted.</p>",
        "<h2>What this study measures</h2><p>Reducing required endpoint pairs can admit more sessions and recorded columns. Retaining more sessions also increases total measured trials, while the weakest session–class pool limits complete rows without reuse. The design maximizes available columns, then training-source total among ties; it is not a global optimizer of accuracy or of both competing objectives.</p>",
        "<p>Every K retains all six starts and goals, with nearly balanced endpoint degrees. The exact class list is chosen from metadata before neural scores. Nested session thirds are ranked by harmonic training support, with exact rational tie handling. Class tasks differ across K; performance comparisons are primarily within each K.</p>",
        table(
            design["grid"],
            [
                "configuration",
                "sessions",
                "units",
                "train_sources",
                "development_sources",
                "train_min",
                "train_max",
                "balanced_no_reuse_rows",
                "classwise_no_reuse_rows",
                "development_singletons",
                "session_class_pools",
            ],
        ),
        "<h2>Sampling comparisons</h2><p><b>U2:</b> exactly two distinct current sources/session×pair, used once in assembly,2Krows. <b>R16:</b> the same sources,16Krows, each used eight times. <b>F16:</b> all eligible sources,16Krows, balanced coverage. R16−U2 measures recombination and row multiplicity at fixed measurements. F16−R16 changes source coverage, empirical weighting and joint combinations at fixed row quota; it is not a pure count-only intervention.</p>",
        "<p>All policies share the exact development rows; smaller rosters project the largest roster’s training and development plans. Adding sessions changes width and source composition together. Scalers, PCA7, CEBRA-Time7 and native multisession CEBRA7 are fitted on training only. Every representation has whole-cue logistic, RBF-SVM, kNN5 and SVD-LDA readouts, using raw10U or latent70features. SVM probabilities/log loss are absent; margins are saved. Native fits one encoder/session with pair-supervised positive alignment and averages aligned coordinates, changing supervision, pooling and exposure versus Time; it is a complete-pipeline comparison. Logistic C=.08for U2 and.01otherwise, preserving N×C within K. Each CEBRA branch uses1000updates and hidden32. Time uses two torch threads; native uses one, under the same two-core process ceiling. Time batch256; native batch floor(256/S) per session, at most256total references per update. Native discrete positives share pair label, with no time-bin alignment. SVM C=16K/N, gamma=scale, class_weight=balanced; kNN5uniform and SVD-LDA have no tuning.</p>",
        "<h2>All pair-readout summaries</h2><p>Mean/min/max across computational seeds0/1/2. Accuracy is conditional on known-label assembly and exposed development, not an untouched test set. Every raw/PCA/Time/native representation is decoded by logistic, RBF-SVM, kNN5 and SVD-LDA. SVM log loss is undefined.</p>",
        table(pairsummary),
        "<details><summary>All1296pair/start/goal summaries</summary>"
        + table(summary)
        + "</details>",
        "<details><summary>All5328individual observed and diagnostic metric rows</summary>"
        + table(results["metrics"])
        + "</details>",
        "<details><summary>All prespecified paired contrasts, every seed</summary>"
        + table(contrasts)
        + "</details>",
    ]
    for group, title in [
        ("overview", "Availability, performance, reuse and controls"),
        ("learning", "Every CEBRA-Time and native optimization curve"),
        ("trajectories", "Every observed class-mean cue trajectory"),
        ("confusions", "Observed seed0 pair confusions, every decoder"),
    ]:
        body.append("<h2>" + title + "</h2>")
        for f in figures:
            if f["group"] != group:
                continue
            encoded = base64.b64encode((out / f["file"]).read_bytes()).decode()
            fig = (
                '<figure><img loading="lazy" alt="'
                + html.escape(f["file"])
                + '" src="data:image/png;base64,'
                + encoded
                + '"><figcaption>'
                + html.escape(f["caption"])
                + "</figcaption></figure>"
            )
            if group in ("trajectories", "confusions"):
                fig = (
                    "<details><summary>"
                    + html.escape(Path(f["file"]).stem)
                    + "</summary>"
                    + fig
                    + "</details>"
                )
            body.append(fig)
    body.append(
        "<h2>Every numeric confusion matrix, all seeds and label worlds</h2><p>Rows=true; columns=predicted. Each cell contains count and row recall. All5328matrices are also in tables/confusions.json.</p>"
    )
    for r in results["confusions"]:
        vals = np.array(r["counts"])
        body.append(
            "<details><summary>"
            + html.escape(r["id"] + " " + r["representation"] + " " + r["head"])
            + "</summary>"
            + table(
                [
                    {
                        "true": label,
                        **{
                            p: f"{int(v)} ({v / sum(row):.3f})"
                            for p, v in zip(r["labels"], row)
                        },
                    }
                    for label, row in zip(r["labels"], vals)
                ],
                ["true", *r["labels"]],
            )
            + "</details>"
        )
    body.extend(
        [
            "<h2>What the evidence can support</h2><p>U2 removes repeated current-source blocks in training assembly. It does not remove repeated optimizer exposure, time-bin dependence, serial/predecessor relationships or repeated development sources. Five shuffled label worlds are diagnostics, not a calibrated biological p-value. Smaller-roster and R16 nulls, new-session transfer and time-resolved readouts were not run.</p>",
            "<p>All inputs retain original outer-train membership and frozen inner assignments. The global5872development-contributor embargo is applied before class/session selection. Development availability participates in selection and has been historically exposed. Session grouping does not establish simultaneity. Results concern condition-level recoverability, not exact natural-trial state, intention, mechanism, maze paths or formal observability.</p>",
            "<p>Trajectories are ten class-mean points in the first three native coordinates of seven-dimensional PCA/CEBRA. They are not actual maze paths or simultaneous biological dynamics. CEBRA loss describes optimization; predictive readouts and controls determine utility. Unit/source/error tables record involvement and exclusion, not causal blame.</p>",
            "<p>All111attempts, actual5661model fit calls excluding scalers,222000updates,444encoder reloads and10656composed readout/split checks are retained. Source/input/code hashes, exact source lineage, numeric features/predictions and models remain in the local run. No prior experiment result was used. Adjacent tables and images are standalone exports; this HTML embeds all rendered figures.</p>",
        ]
    )
    style = "body{font:16px/1.55 system-ui;max-width:1400px;margin:40px auto;padding:0 28px;color:#18323e;background:#fbfaf7}h1{font-size:36px}h2{margin-top:40px}table{border-collapse:collapse;font-size:12px;display:block;overflow:auto;margin:16px 0}th,td{border:1px solid #cbd4d8;padding:5px 8px;text-align:right}th{background:#e5ecee}img{max-width:100%;height:auto}figure{margin:24px 0}figcaption{font-size:13px;color:#405760}details{margin:12px 0;padding:10px;background:white;border:1px solid #d7dfe2}summary{cursor:pointer;font-weight:600}"
    (out / "report.html").write_text(
        '<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Population grid research report</title><style>'
        + style
        + "</style></head><body>"
        + "\n".join(body)
        + "</body></html>"
    )
    return dict(summary=summary, contrasts=contrasts, figures=figures)
