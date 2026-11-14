"""Collate new saved predictions and training traces; no model loading or fitting."""

from __future__ import annotations
import base64
import csv
import html
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from scripts.source_support_report import table
from . import study

ENCODERS = ("raw", "pca", "cebra", "native")
DECODERS = ("logistic", "svm", "knn", "lda")
NAMES = {
    "raw": "Raw",
    "pca": "PCA7",
    "cebra": "CEBRA-Time7",
    "native": "Native multisession7",
}
COLORS = ("#245c9c", "#d27d21", "#2d897b", "#9a4b92")
CONTRASTS = {
    "reuse": (("B2", "B3"), ("B3", "B5"), ("B2", "B5"), ("U3", "B3")),
    "width": (("B3", "Wmid"), ("Wmid", "Wfull"), ("B3", "Wfull")),
}


def summarize(metrics):
    rows = []
    for arm in study.ARMS:
        for encoder in ENCODERS:
            for decoder in DECODERS:
                for head in ("pair", "start", "goal"):
                    group = [
                        r
                        for r in metrics
                        if r["world"] == "observed"
                        and (r["arm"], r["encoder"], r["decoder"], r["head"])
                        == (arm, encoder, decoder, head)
                    ]
                    if not group:
                        continue
                    values = np.array([r["balanced_accuracy"] for r in group])
                    rows.append(
                        dict(
                            arm=arm,
                            encoder=encoder,
                            decoder=decoder,
                            head=head,
                            mean_BA=float(values.mean()),
                            min_BA=float(values.min()),
                            max_BA=float(values.max()),
                            train_BA=float(np.mean([r["train_BA"] for r in group])),
                            mean_train_development_gap=float(
                                np.mean([r["train_development_gap"] for r in group])
                            ),
                            units=group[0]["units"],
                            sessions=group[0]["sessions"],
                            computational_repeats=len(group),
                        )
                    )
    return rows


def comparisons(metrics, part):
    indexed = {
        (r["world"], r["seed"], r["arm"], r["representation"], r["head"]): r
        for r in metrics
    }
    result = []
    for before, after in CONTRASTS[part]:
        for r in metrics:
            if r["arm"] != before:
                continue
            s = indexed[r["world"], r["seed"], after, r["representation"], r["head"]]
            result.append(
                dict(
                    world=r["world"],
                    seed=r["seed"],
                    before=before,
                    after=after,
                    encoder=r["encoder"],
                    decoder=r["decoder"],
                    head=r["head"],
                    before_BA=r["balanced_accuracy"],
                    after_BA=s["balanced_accuracy"],
                    delta_BA=s["balanced_accuracy"] - r["balanced_accuracy"],
                    delta_training_BA=s["train_BA"] - r["train_BA"],
                )
            )
    return result


def matrices_and_errors(run, metrics, part):
    matrices, recalls, switches = [], [], []
    cache = {}
    lineages = {}
    for case_id in dict.fromkeys(r["id"] for r in metrics):
        records = [r for r in metrics if r["id"] == case_id]
        case_confusions = json.loads(
            (run / "cases" / case_id / "confusions.json").read_text()
        )
        lineages[case_id] = json.loads(
            (run / "cases" / case_id / "development_lineage.json").read_text()
        )
        labels_by = {
            (r["representation"], r["head"]): r["labels"] for r in case_confusions
        }
        with np.load(
            run / "cases" / case_id / "numeric_records.npz", allow_pickle=False
        ) as numeric:
            for r in records:
                name = r["representation"] + "_" + r["head"]
                labels = labels_by[r["representation"], r["head"]]
                for split, prefix in (("development", ""), ("train", "_train")):
                    truth = numeric[name + prefix + "_truth"].astype(str)
                    prediction = numeric[name + prefix + "_prediction"].astype(str)
                    index = {label: i for i, label in enumerate(labels)}
                    counts = np.zeros((len(labels), len(labels)), dtype=int)
                    for actual, pred in zip(truth, prediction, strict=True):
                        counts[index[actual], index[pred]] += 1
                    row = dict(
                        case=case_id,
                        world=r["world"],
                        seed=r["seed"],
                        arm=r["arm"],
                        encoder=r["encoder"],
                        decoder=r["decoder"],
                        head=r["head"],
                        split=split,
                        labels=labels,
                        counts=counts.tolist(),
                    )
                    matrices.append(row)
                    for label, n, correct in zip(
                        labels, counts.sum(1), np.diag(counts), strict=True
                    ):
                        recalls.append(
                            {
                                k: v
                                for k, v in row.items()
                                if k not in ("labels", "counts")
                            }
                            | dict(
                                label=label,
                                appearances=int(n),
                                correct=int(correct),
                                recall=float(correct / n),
                            )
                        )
                    if split == "development":
                        cache[
                            r["world"],
                            r["seed"],
                            r["arm"],
                            r["representation"],
                            r["head"],
                        ] = (truth, prediction)
    for before, after in CONTRASTS[part]:
        for key, (truth, prediction) in cache.items():
            world, seed, arm, representation, head = key
            if arm != before:
                continue
            other_truth, other = cache[world, seed, after, representation, head]
            before_lineage = lineages[f"{world}_seed{seed}_{before}"]
            after_lineage = lineages[f"{world}_seed{seed}_{after}"]
            common_blocks = [
                b for b in before_lineage["blocks"] if b in after_lineage["blocks"]
            ]
            if not common_blocks:
                raise ValueError("no shared session blocks for paired errors")
            before_indices = [before_lineage["blocks"].index(b) for b in common_blocks]
            after_indices = [after_lineage["blocks"].index(b) for b in common_blocks]
            for a, b in zip(before_lineage["rows"], after_lineage["rows"], strict=True):
                if (
                    a["row_id"],
                    a["pair"],
                    [a["source_ids"][i] for i in before_indices],
                ) != (
                    b["row_id"],
                    b["pair"],
                    [b["source_ids"][i] for i in after_indices],
                ):
                    raise ValueError("paired-error row/source identity mismatch")
            np.testing.assert_array_equal(truth, other_truth)
            for label in sorted(set(truth)):
                mask = truth == label
                a, b = prediction[mask] == truth[mask], other[mask] == truth[mask]
                switches.append(
                    dict(
                        world=world,
                        seed=seed,
                        before=before,
                        after=after,
                        representation=representation,
                        head=head,
                        label=label,
                        rows=int(mask.sum()),
                        right_to_wrong=int((a & ~b).sum()),
                        wrong_to_right=int((~a & b).sum()),
                        both_right=int((a & b).sum()),
                        both_wrong=int((~a & ~b).sum()),
                    )
                )
    return matrices, recalls, switches


def best_worst(summary, part):
    arms = [a for a in study.PART_ARMS[part] if a != "U3"]
    result = []
    for encoder in ENCODERS:
        for decoder in DECODERS:
            rows = [
                r
                for r in summary
                if r["encoder"] == encoder
                and r["decoder"] == decoder
                and r["head"] == "pair"
                and r["arm"] in arms
            ]
            best = min(rows, key=lambda r: (-r["mean_BA"], arms.index(r["arm"])))
            worst = min(rows, key=lambda r: (r["mean_BA"], arms.index(r["arm"])))
            result.append(
                dict(
                    encoder=encoder,
                    decoder=decoder,
                    best=best["arm"],
                    worst=worst["arm"],
                    best_mean_BA=best["mean_BA"],
                    worst_mean_BA=worst["mean_BA"],
                    gap=best["mean_BA"] - worst["mean_BA"],
                    best_ties=",".join(
                        r["arm"]
                        for r in rows
                        if abs(r["mean_BA"] - best["mean_BA"]) < 1e-12
                    ),
                    worst_ties=",".join(
                        r["arm"]
                        for r in rows
                        if abs(r["mean_BA"] - worst["mean_BA"]) < 1e-12
                    ),
                )
            )
    return result


def create_report(run, part, config, meta):
    run = Path(run)
    out = run / ("report_" + part)
    out.mkdir(parents=True, exist_ok=False)
    figs = out / "figures"
    figs.mkdir()
    results = study.load_results(run, part)
    metrics = results["metrics"]
    arms = study.PART_ARMS[part]
    summary = summarize(metrics)
    contrasts = comparisons(metrics, part)
    matrices, recalls, switches = matrices_and_errors(run, metrics, part)
    ranked = best_worst(summary, part)
    for name, rows in (
        ("metrics", metrics),
        ("summary", summary),
        ("paired_contrasts", contrasts),
        ("class_recall", recalls),
        ("paired_error_switches", switches),
        ("best_worst", ranked),
    ):
        study.write_csv(out / (name + ".csv"), rows)
    study.write_json(out / "confusion_matrices.json", matrices)
    study.write_json(out / "learning.json", results["learning"])
    study.write_json(out / "trajectories.json", results["trajectories"])
    support = []
    for roster, record in config["design"]["rosters"].items():
        for unit in meta["units"]:
            alias = meta["aliases"][unit["session_id"]]
            if alias not in config["design"]["rosters"]["full"]["session_aliases"]:
                continue
            support.append(
                dict(
                    roster=roster,
                    unit=meta["unit_aliases"][unit["cell_id"]],
                    session=alias,
                    retained=alias in record["session_aliases"],
                    spatial_map_status="unknown",
                    reason="compact cue-source lacks authenticated field/occupancy/coordinate maps",
                )
            )
    study.write_csv(out / "retained_removed_units_and_map_availability.csv", support)
    pool_rows = []
    for source_part in ("reuse", "width") if part == "width" else ("reuse",):
        with (run / ("aggregates_" + source_part) / "pool_usage.csv").open() as handle:
            pool_rows.extend(
                r
                for r in csv.DictReader(handle)
                if r["case"].rsplit("_", 1)[-1] in arms
            )
    study.write_csv(out / "actual_pool_usage.csv", pool_rows)
    figures = []

    def save(fig, name, caption, group):
        path = figs / (name + ".png")
        fig.savefig(path, dpi=125, bbox_inches="tight", facecolor="white")
        plt.close(fig)
        figures.append(
            dict(
                file=str(path.relative_to(out)),
                sha256=study.sha(path),
                caption=caption,
                group=group,
            )
        )

    common = "Existing cue recordings; fixed nine endpoint classes; frozen contributor-disjoint, historically exposed development. Dots/ranges are computational repeats, not biological confidence intervals. "
    fig, axs = plt.subplots(1, 3, figsize=(13, 3.7))
    chosen = [
        next(r for r in metrics if r["world"] == "observed" and r["arm"] == a)
        for a in arms
    ]
    for ax, key, label in zip(
        axs,
        ("units", "sessions", "source_budget"),
        (
            "Recorded unit columns",
            "Recording sessions",
            "Distinct train sources per session × class",
        ),
    ):
        ax.bar(arms, [r[key] for r in chosen], color="#47799b")
        ax.set_title(label)
        ax.set_ylim(0, max(r[key] for r in chosen) * 1.2)
        for i, r in enumerate(chosen):
            ax.text(i, r[key], str(r[key]), ha="center", va="bottom")
    save(
        fig,
        "design",
        common
        + "Source counts differ from constructed rows: B2/B3/B5 and width arms use144 training rows; U3 uses27. Every arm evaluates72 constructed rows.",
        "overview",
    )

    fig, axs = plt.subplots(1, 3, figsize=(14, 4.7))
    families = [(e, d) for e in ENCODERS for d in DECODERS]
    for ax, head in zip(axs, ("pair", "start", "goal")):
        matrix = np.array(
            [
                [
                    next(
                        r["mean_BA"]
                        for r in summary
                        if (r["arm"], r["encoder"], r["decoder"], r["head"])
                        == (a, e, d, head)
                    )
                    for a in arms
                ]
                for e, d in families
            ]
        )
        im = ax.imshow(matrix, vmin=0, vmax=1, cmap="viridis", aspect="auto")
        ax.set_xticks(range(len(arms)), arms)
        ax.set_yticks(range(16), [e + "/" + d for e, d in families], fontsize=7)
        ax.set_title(head + " development balanced accuracy")
        for y in range(16):
            for x in range(len(arms)):
                ax.text(
                    x,
                    y,
                    f"{100 * matrix[y, x]:.1f}",
                    ha="center",
                    va="center",
                    fontsize=7,
                    color="white" if matrix[y, x] < 0.55 else "black",
                )
    fig.colorbar(
        im, ax=axs.tolist(), fraction=0.025, label="Mean BA across three repeats"
    )
    save(
        fig,
        "all_models",
        common
        + "All16 fixed encoder/readout combinations; cells show mean percentages. Pair uniform reference11.11%; start/goal16.67%.",
        "overview",
    )

    fig, axs = plt.subplots(1, 2, figsize=(12, 4))
    x = np.arange(len(arms))
    for e, color in zip(ENCODERS, COLORS):
        rows = [
            next(
                r
                for r in summary
                if (r["arm"], r["encoder"], r["decoder"], r["head"])
                == (a, e, "svm", "pair")
            )
            for a in arms
        ]
        y = np.array([r["mean_BA"] for r in rows])
        axs[0].errorbar(
            x,
            y,
            yerr=[y - [r["min_BA"] for r in rows], [r["max_BA"] for r in rows] - y],
            label=NAMES[e],
            color=color,
            marker="o",
            capsize=3,
        )
        axs[1].plot(
            x,
            [r["mean_train_development_gap"] for r in rows],
            marker="o",
            color=color,
            label=NAMES[e],
        )
        for i, a in enumerate(arms):
            null = [
                r["balanced_accuracy"]
                for r in metrics
                if r["world"] != "observed"
                and (r["arm"], r["encoder"], r["decoder"], r["head"])
                == (a, e, "svm", "pair")
            ]
            axs[0].scatter(
                [i] * len(null), null, color=color, alpha=0.4, marker="x", s=20
            )
    axs[0].axhline(1 / 9, color="gray", ls=":", label="Uniform reference")
    axs[1].axhline(0, color="gray", ls=":")
    for ax in axs:
        ax.set_xticks(x, arms)
        ax.grid(alpha=0.2)
    axs[0].set_ylabel("Pair balanced accuracy")
    axs[1].set_ylabel("Training BA − development BA")
    axs[0].set_title("SVM: observed repeat range and five label worlds")
    axs[1].set_title("SVM: mean train–development gap")
    axs[0].legend(fontsize=7)
    save(
        fig,
        "svm_scores_and_gaps",
        common
        + "Four fixed representations with RBF-SVM. Lines/vertical ranges: observed repeat mean/min/max. Crosses: five source-label diagnostic worlds at modelseed0; no p-values.",
        "overview",
    )

    fig, axs = plt.subplots(1, 2, figsize=(12, 3.8))
    for i, a in enumerate(arms):
        rows = [
            r
            for r in pool_rows
            if r["case"] == f"observed_seed0_{a}" and r["split"] == "train"
        ]
        frac = sum(int(r["extra_draws"]) for r in rows) / sum(
            int(r["draws"]) for r in rows
        )
        axs[0].bar(a, frac, color="#9a6a46")
        axs[1].bar(
            i - 0.16,
            sum(int(r["used"]) for r in rows),
            width=0.32,
            color="#2d897b",
            label="Distinct current source IDs" if i == 0 else None,
        )
        axs[1].bar(
            i + 0.16,
            sum(int(r["draws"]) for r in rows),
            width=0.32,
            color="#8f9caf",
            label="Session-block draws" if i == 0 else None,
        )
    axs[0].set_ylim(0, 1)
    axs[0].set_ylabel("Extra draws / all training block draws")
    axs[1].set_xticks(range(len(arms)), arms)
    axs[1].legend(fontsize=8)
    save(
        fig,
        "actual_reuse",
        common
        + "Actual observed seed0 lineage. Reuse fraction is fixed by the chosen budget, so a within-arm reuse/error correlation is undefined. Additional block draws are repeated measurements, not new trials.",
        "overview",
    )

    fig, axs = plt.subplots(len(arms), 2, figsize=(12, 2.4 * len(arms)), squeeze=False)
    for row, a in enumerate(arms):
        for col, e in enumerate(("cebra", "native")):
            ax = axs[row, col]
            for learning in results["learning"]:
                if learning["case"].rsplit("_", 2)[-2] != a or learning["encoder"] != e:
                    continue
                observed = learning["case"].startswith("observed_")
                loss = learning["loss"]["total"]
                ax.plot(
                    np.arange(1, len(loss) + 1),
                    loss,
                    alpha=0.8 if observed else 0.3,
                    lw=1 if observed else 0.6,
                    color=None if observed else "gray",
                    label=learning["case"].split("_")[1] if observed else None,
                )
            ax.set_title(a + " · " + NAMES[e])
            ax.set_xlabel("Optimizer update")
            ax.set_ylabel("InfoNCE loss")
            ax.legend(fontsize=6)
    fig.tight_layout()
    save(
        fig,
        "all_learning_curves",
        "All observed and diagnostic optimization curves for this experiment. Colored: three observed repeats; gray: five label worlds. Each encoder has1000updates. Different objectives/batches make Time/native loss scales incomparable; falling loss alone is not learning evidence.",
        "learning",
    )

    conditions = config["design"]["panel"]["conditions"]
    for trajectory in results["trajectories"]:
        if not trajectory["case"].startswith("observed_"):
            continue
        fig = plt.figure(figsize=(14, 4))
        for j, e in enumerate(("pca", "cebra", "native"), 1):
            ax = fig.add_subplot(1, 3, j, projection="3d")
            for label, color in zip(conditions, plt.cm.tab10.colors):
                z = np.array(trajectory["coordinates"][e][label])
                ax.plot(z[:, 0], z[:, 1], z[:, 2], marker=".", color=color, label=label)
                ax.scatter(*z[0], color=color, marker="o", s=20)
                ax.scatter(*z[-1], color=color, marker="x", s=25)
            ax.set_title(NAMES[e])
            ax.set_xlabel("Coordinate1")
            ax.set_ylabel("Coordinate2")
            ax.set_zlabel("Coordinate3")
        fig.suptitle(trajectory["case"])
        fig.legend(
            *ax.get_legend_handles_labels(), loc="lower center", ncol=9, fontsize=7
        )
        save(
            fig,
            "trajectory_" + trajectory["case"],
            common
            + "Class means across8constructed development rows; ten bin centers50–950ms after cue onset, circle=start, cross=end. First3 of7 fitted coordinates, unaligned between fits. These are cue representation trajectories, not spatial paths or simultaneous population dynamics.",
            "trajectories",
        )

    for arm in arms:
        for decoder in DECODERS:
            fig, axs = plt.subplots(4, 2, figsize=(11, 15))
            for row, e in enumerate(ENCODERS):
                record = next(
                    r
                    for r in matrices
                    if (
                        r["world"],
                        r["seed"],
                        r["arm"],
                        r["encoder"],
                        r["decoder"],
                        r["head"],
                        r["split"],
                    )
                    == ("observed", 0, arm, e, decoder, "pair", "development")
                )
                counts = np.array(record["counts"])
                norm = counts / counts.sum(1, keepdims=True)
                for col, data in enumerate((counts, norm)):
                    ax = axs[row, col]
                    ax.imshow(data, cmap="Blues", vmin=0, vmax=8 if col == 0 else 1)
                    ax.set_xticks(range(9), record["labels"], rotation=70, fontsize=7)
                    ax.set_yticks(range(9), record["labels"], fontsize=7)
                    ax.set_xlabel("Predicted pair")
                    ax.set_ylabel("True pair")
                    ax.set_title(
                        NAMES[e] + (" · counts" if col == 0 else " · row recall")
                    )
                    for y in range(9):
                        for x in range(9):
                            if data[y, x]:
                                ax.text(
                                    x,
                                    y,
                                    str(int(data[y, x]))
                                    if col == 0
                                    else f"{data[y, x]:.2f}",
                                    ha="center",
                                    va="center",
                                    fontsize=6,
                                    color="white"
                                    if data[y, x] > (4 if col == 0 else 0.5)
                                    else "black",
                                )
            fig.suptitle(arm + " · " + decoder + " · observed repeat0")
            fig.tight_layout(rect=(0, 0, 1, 0.97))
            save(
                fig,
                "confusion_" + arm + "_" + decoder,
                common
                + "Observed repeat0, every encoder, "
                + decoder
                + " pair readout; rows=true, columns=prediction. Count and normalized views use8constructed rows per true pair. Explorer below retains every repeat, world, readout, head and train/development split.",
                "confusions",
            )

    fig, ax = plt.subplots(figsize=(12, 5))
    deltas = []
    labels = []
    for r in ranked:
        values = []
        for label in conditions:
            means = []
            for arm in (r["worst"], r["best"]):
                group = [
                    v["recall"]
                    for v in recalls
                    if (
                        v["world"],
                        v["arm"],
                        v["encoder"],
                        v["decoder"],
                        v["head"],
                        v["split"],
                        v["label"],
                    )
                    == (
                        "observed",
                        arm,
                        r["encoder"],
                        r["decoder"],
                        "pair",
                        "development",
                        label,
                    )
                ]
                means.append(float(np.mean(group)))
            values.append(means[1] - means[0])
        deltas.append(values)
        labels.append(
            r["encoder"] + "/" + r["decoder"] + ": " + r["best"] + " − " + r["worst"]
        )
    im = ax.imshow(deltas, cmap="RdBu", vmin=-1, vmax=1, aspect="auto")
    ax.set_xticks(range(9), conditions)
    ax.set_yticks(range(16), labels, fontsize=7)
    fig.colorbar(im, ax=ax, label="Mean class recall change")
    ax.set_title("Post-hoc best/worst: where performance differences occur")
    save(
        fig,
        "best_worst_class_changes",
        common
        + "Best/worst selected within each fixed encoder/readout by mean observed pairBA across3repeats; no independent confirmation. U3 excluded from primary reuse ranking. Positive cells mean more correct predictions under the selected best arm. Spatial-field coverage remains unknown.",
        "errors",
    )

    title = (
        "Source reuse at fixed population width"
        if part == "reuse"
        else "Population width at three training sources"
    )
    body = [
        "<h1>" + title + "</h1>",
        "<p>November14,2026 · Fresh exploratory training on existing recordings. "
        + (
            "32 newly fitted cases."
            if part == "reuse"
            else "16 newly fitted cases plus8authenticated B3 bridge cases from experiment1."
        )
        + "</p>",
        "<p>One fixed nine-class endpoint task. Primary reuse test:17units/3sessions, nested2/3/5distinct training sources per session×class,16assembled rows/class. U3 uses the same3sources once. Width test:17/49/83units across3/11/20sessions, exactly3sources/pool. All observed repeats share the same projected development plan.</p>",
        "<p>Raw/PCA7/CEBRA-Time7/native multisession7 × logistic/RBF-SVM/kNN5/SVD-LDA, pair/start/goal heads. Scalers, representations and decoders fit training only. Native is pair-supervised and equal-session pooled; Time uses adjacent-bin positives. Fixed settings,1000updates per encoder, no hyperparameter sweep.</p>",
        "<p>Reading guide: compare observed scores with shuffled-source-label controls and training gaps; then inspect per-class errors. More measured sources and fewer repetitions are coupled at fixed row quota. Adding width also adds sessions and measured sources. Neither analysis establishes natural-trial or biological independence.</p>",
        "<h2>All fixed model comparisons</h2>",
        table([r for r in summary if r["head"] == "pair"]),
        "<details><summary>All pair/start/goal summaries</summary>"
        + table(summary)
        + "</details>",
        "<h2>Post-hoc best/worst within each model</h2>",
        table(ranked),
        "<p>Every primary arm remains in the full tables. This ranking describes the observed results, not validated model selection. Count/normalized matrices below include training and development. Uniform pairBA=1/9; a hypothetical perfect-single-endpoint pair reference is6/9 because this sparse panel couples start and goal.</p>",
    ]
    for group, label in (
        ("overview", "Design, source use and predictive results"),
        ("learning", "Actual optimization traces"),
        ("trajectories", "All observed cue representation trajectories"),
        ("confusions", "Count and normalized pair confusion panels"),
        ("errors", "Where best/worst errors differ"),
    ):
        body.append("<h2>" + label + "</h2>")
        for f in figures:
            if f["group"] != group:
                continue
            encoded = base64.b64encode((out / f["file"]).read_bytes()).decode()
            content = (
                '<figure><img loading="lazy" src="data:image/png;base64,'
                + encoded
                + '"><figcaption>'
                + html.escape(f["caption"])
                + "</figcaption></figure>"
            )
            if group in ("trajectories", "confusions"):
                content = (
                    "<details><summary>"
                    + html.escape(Path(f["file"]).stem)
                    + "</summary>"
                    + content
                    + "</details>"
                )
            body.append(content)
    body.append(
        '<h2 id="confusion-explorer">Every confusion matrix</h2><p>Select any observed/null case, model, head and split. Rows are true labels; columns predicted. Normalization is by true-class count. Repeated rows are not independent observations.</p><div id="explorer"></div>'
    )
    body.append(
        "<h2>Issue29: error propagation and coverage boundary</h2><p>Paired-error-switch tables align common constructed row labels and source blocks. The retained/removed-unit table records every admitted column with map status <b>unknown</b>. Compact cue inputs provide no authenticated spatial fields, occupancy, map-source trials or endpoint-to-coordinate map. These results identify changed errors and removed/added recorded columns; a lost-place-field explanation remains untested. No class is deleted between these arms.</p><p>To complete spatial attribution later, join session-qualified unit maps with verified coordinates, phase, occupancy, reliability and source-trial provenance. Navigation place selectivity must remain distinct from cue decoding. Do not count an absent map as zero selectivity.</p>"
    )
    body.append(
        "<h2>Machine-readable evidence</h2><ul>"
        + "".join(
            '<li><a href="' + n + '">' + n + "</a></li>"
            for n in (
                "metrics.csv",
                "summary.csv",
                "paired_contrasts.csv",
                "class_recall.csv",
                "paired_error_switches.csv",
                "best_worst.csv",
                "confusion_matrices.json",
                "learning.json",
                "trajectories.json",
                "actual_pool_usage.csv",
                "retained_removed_units_and_map_availability.csv",
            )
        )
        + "</ul>"
    )
    payload = json.dumps(matrices, separators=(",", ":")).replace("</", "<\\/")
    script = """<script>
const records=DATA;const host=document.getElementById('explorer');const keys=['world','seed','arm','encoder','decoder','head','split'];const controls={};
for(const key of keys){const l=document.createElement('label');l.textContent=key+' ';const s=document.createElement('select');controls[key]=s;l.append(s);host.append(l);s.onchange=()=>refresh(key);}
const norm=document.createElement('input');norm.type='checkbox';norm.checked=true;const nl=document.createElement('label');nl.append(norm,' Row normalized');host.append(nl);const panel=document.createElement('div');host.append(panel);norm.onchange=draw;
function refresh(changed){let rows=records;for(const key of keys){const s=controls[key],old=s.value;const vals=[...new Set(rows.map(r=>String(r[key])))];s.replaceChildren(...vals.map(v=>{let o=document.createElement('option');o.value=o.textContent=v;return o;}));if(vals.includes(old))s.value=old;rows=rows.filter(r=>String(r[key])===s.value);}draw();}
function draw(){const r=records.find(r=>keys.every(k=>String(r[k])===controls[k].value));panel.replaceChildren();if(!r)return;const p=document.createElement('p');p.textContent=r.case+' | '+r.split+' | '+r.head;panel.append(p);const t=document.createElement('table');const h=document.createElement('tr');h.append(document.createElement('th'));for(const label of r.labels){let th=document.createElement('th');th.textContent=label;h.append(th);}t.append(h);r.counts.forEach((row,i)=>{const tr=document.createElement('tr'),th=document.createElement('th');th.textContent=r.labels[i];tr.append(th);let total=row.reduce((a,b)=>a+b,0);row.forEach(v=>{const td=document.createElement('td');td.textContent=norm.checked?(v/total).toFixed(3):v;td.style.backgroundColor='rgba(38,102,164,'+(v/total*.8)+')';tr.append(td);});t.append(tr);});panel.append(t);}
refresh();</script>""".replace("DATA", payload)
    document = (
        '<!doctype html><html><head><meta charset="utf-8"><title>'
        + title
        + "</title><style>body{font:16px/1.55 system-ui,sans-serif;max-width:1280px;margin:40px auto;padding:0 24px;color:#182b3b}h1,h2{line-height:1.2}table{border-collapse:collapse;font-size:12px;display:block;overflow:auto;max-width:100%}th,td{padding:5px 9px;border:1px solid #ccd6df;text-align:right}th{background:#edf2f6}img{width:100%;height:auto}figure{margin:24px 0}figcaption{font-size:13px;color:#455b6b}details{margin:12px 0}summary{cursor:pointer;font-weight:600}label{display:inline-block;margin:5px}select{padding:5px}a{color:#1e5a90}</style></head><body>"
        + "".join(body)
        + script
        + "</body></html>"
    )
    (out / "report.html").write_text(document)
    report = dict(
        part=part,
        figures=figures,
        summary=summary,
        best_worst=ranked,
        metric_rows=len(metrics),
        confusion_matrices=len(matrices),
        error_switch_rows=len(switches),
    )
    study.write_json(out / "report_manifest.json", report)
    return report
