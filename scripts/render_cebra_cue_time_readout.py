#!/usr/bin/env python3
# pyright: reportMissingImports=false
"""Render only verified frozen-readout outputs; no fitting or model selection."""

from __future__ import annotations

import argparse
import base64
import json
import shutil
import sys
from pathlib import Path
from typing import Any

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from markdown_it import MarkdownIt

from scripts import cebra_cue_time_readout as ct

NAMES = {
    "raw290": "Raw neural",
    "pca8": "PCA",
    "cue_time": "Cue-only CEBRA-Time",
    "full_time": "Joint CEBRA-Time",
}
READOUTS = {"logistic": "Logistic", "svc": "RBF-SVM"}
TIMES = np.arange(50, 1000, 100)
COLORS = ["#087e8b", "#e88922", "#6e44aa"]
CONTEXT = (
    "Fixed4→3 interior component D_N_R_T__N_R_M;29 selected units/7 session blocks. "
    "82 training sources (30 absent/52 present),22 historical-validation sources (12/10); "
    "128 training pseudorows (64/64),30 evaluation combinations (24/6), half evaluation mass/class. "
    "Sources split before assembly; rows share sources; seeds0/1/2 are computational repeats, not biological replication. "
    "Cue time is milliseconds from cue onset; last bin retains measured clipping. All readouts use frozen final1000 features; "
    "raw29 or latent8 features/bin, raw290 or latent80 whole-cue. No window/decoder/checkpoint selected for future prediction. "
)


def render(run: Path, verified: Path, geometry: Path, out: Path):
    receipt = ct.read_json(verified / "verification.json")
    if (
        receipt["status"] != "verified"
        or Path(receipt["run_dir"]).resolve() != run.resolve()
    ):
        raise RuntimeError("a matching successful verification receipt is required")
    ct.ft.verify_hash_manifest(run)
    ct.ft.verify_hash_manifest(geometry)
    summary = ct.read_json(verified / "summary.json")
    metrics = [r for r in ct.read_csv(run / "metrics.csv") if r["world"] == "observed"]
    index = {
        (r["representation"], r["readout"], r["window"], int(r["seed"]), r["split"]): r
        for r in metrics
    }
    confusions = [
        r
        for r in ct.read_csv(verified / "confusions_validation.csv")
        if r["world"] == "observed"
    ]
    sensitivity = ct.read_csv(verified / "validation_source_resamples.csv")
    geom = ct.read_csv(geometry / "geometry_spectra.csv")
    stability = ct.read_csv(geometry / "geometry_stability_vs_final.csv")
    cohort = ct.ft.load_cue_cohort()
    out.mkdir(parents=True, exist_ok=True)
    figures = out / "figures"
    figures.mkdir(exist_ok=True)
    captions = {}

    def values(rep, decoder, field, split="validation", windows=ct.BIN_WINDOWS):
        return np.array(
            [
                [float(index[(rep, decoder, w, s, split)][field]) for w in windows]
                for s in ct.EXPECTED_SEEDS
            ]
        )

    def save(fig, name, caption):
        fig.tight_layout()
        fig.savefig(figures / f"{name}.png", dpi=140, bbox_inches="tight")
        plt.close(fig)
        captions[name] = (
            caption
            + " "
            + CONTEXT
            + f"Provenance: {run.relative_to(ct.CANONICAL_ROOT)}; verified numeric exports linked below."
        )

    # Actual source counts, not synthetic balance.
    sessions = sorted(set(cohort.source_session_ids))
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    support_rows = []
    for ax, split in zip(axes, ("train", "validation"), strict=True):
        a = np.array(
            [
                [
                    sum(
                        m.session_id == sess and m.split == split and m.label == label
                        for m in cohort.metas
                    )
                    for label in ct.ft.LABELS
                ]
                for sess in sessions
            ]
        )
        ax.imshow(a, cmap="Blues", vmin=0)
        ax.set(
            xticks=[0, 1],
            xticklabels=ct.ft.LABELS,
            yticks=range(len(sessions)),
            yticklabels=sessions,
            title=f"Unique real source trials: {split}",
        )
        for i, sess in enumerate(sessions):
            for j, label in enumerate(ct.ft.LABELS):
                ax.text(j, i, str(a[i, j]), ha="center", va="center", color="black")
                support_rows.append(
                    {
                        "split": split,
                        "session": sess,
                        "label": label,
                        "real_sources": int(a[i, j]),
                    }
                )
    save(
        fig,
        "source_support",
        "Real-source support by session and class. Eight validation session×class pools are singletons; synthetic replication does not repair their support. No decoder or uncertainty estimate applies to these counts.",
    )
    ct.write_csv(out / "source_support.csv", support_rows)

    for field, title, baseline in (
        ("balanced_accuracy", "Balanced accuracy", 0.5),
        ("auroc", "AUROC", 0.5),
    ):
        fig, axes = plt.subplots(4, 2, figsize=(12, 12), sharex=True, sharey=True)
        for i, rep in enumerate(ct.REPRESENTATIONS):
            for j, decoder in enumerate(ct.DECODERS):
                ax = axes[i, j]
                v, whole = (
                    values(rep, decoder, field),
                    values(rep, decoder, field, windows=("wholecue",)),
                )
                for s in ct.EXPECTED_SEEDS:
                    ax.plot(TIMES, v[s], color=COLORS[s], alpha=0.45, lw=1)
                ax.plot(TIMES, v.mean(0), "o-", color="black", label="bin mean")
                ax.axhline(
                    float(whole.mean()),
                    color="#d1495b",
                    linestyle="--",
                    label="whole-cue mean",
                )
                ax.axhline(
                    baseline, color="gray", linestyle=":", label="chance reference"
                )
                ax.set(
                    title=f"{NAMES[rep]} / {READOUTS[decoder]}",
                    ylim=(-0.03, 1.03),
                    xlabel="cue-bin center (ms)",
                    ylabel=title,
                )
        axes[0, 0].legend(fontsize=8)
        save(
            fig,
            field,
            f"{title}: thin colored lines show the three paired seeds, black shows their mean; red dashed is the separately trained whole-cue readout. No SEM/confidence interval is inferred from seeds. BA is mean class recall; AUROC uses logistic probabilities or uncalibrated SVM margins. Null reference=.5, not a significance threshold.",
        )

    fig, axes = plt.subplots(2, 2, figsize=(11, 7), sharex=True)
    for ax, rep in zip(axes.flat, ct.REPRESENTATIONS, strict=True):
        v = values(rep, "logistic", "balanced_log_loss")
        for s in ct.EXPECTED_SEEDS:
            ax.plot(TIMES, v[s], color=COLORS[s], alpha=0.5)
        ax.plot(TIMES, v.mean(0), "ko-", label="bin mean")
        ax.axhline(
            float(
                values(
                    rep, "logistic", "balanced_log_loss", windows=("wholecue",)
                ).mean()
            ),
            color="#d1495b",
            linestyle="--",
            label="whole cue",
        )
        ax.axhline(ct.ft.LOG2, color="gray", linestyle=":", label="constant .5")
        ax.set(
            title=NAMES[rep],
            xlabel="cue-bin center (ms)",
            ylabel="balanced log loss (nats), lower better",
        )
    axes[0, 0].legend(fontsize=8)
    save(
        fig,
        "logistic_loss",
        "Logistic-only probability loss, including all seeds and whole-cue references. Constant-.5 loss=log(2)=.693147. Lower loss can reflect calibration rather than better discrimination. No SVM probability loss is fabricated.",
    )

    fig, axes = plt.subplots(4, 2, figsize=(12, 12), sharex=True)
    for i, rep in enumerate(ct.REPRESENTATIONS):
        for j, decoder in enumerate(ct.DECODERS):
            ax = axes[i, j]
            v = values(rep, decoder, "balanced_accuracy")
            train = values(rep, decoder, "balanced_accuracy", split="train")
            whole = values(rep, decoder, "balanced_accuracy", windows=("wholecue",))
            for s in ct.EXPECTED_SEEDS:
                ax.plot(TIMES, v[s] - whole[s], color=COLORS[s], alpha=0.4)
            ax.plot(TIMES, (v - whole).mean(0), "ko-", label="bin−whole BA")
            ax.plot(
                TIMES,
                (train - v).mean(0),
                color="#d1495b",
                linestyle="--",
                label="train−validation BA",
            )
            ax.axhline(0, color="gray", linestyle=":")
            ax.set(
                title=f"{NAMES[rep]} / {READOUTS[decoder]}",
                xlabel="cue-bin center (ms)",
                ylabel="balanced-accuracy difference",
            )
    axes[0, 0].legend(fontsize=8)
    save(
        fig,
        "window_effects_and_gaps",
        "Paired bin-minus-whole BA (black, positive favors the bin) and train-minus-validation gap (red). Thin traces are per-seed bin-minus-whole effects. Different feature counts and fixed regularization mean this is predictive utility, not a capacity-matched proof of temporal information.",
    )

    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    for ax, decoder in zip(axes[:2], ct.DECODERS, strict=True):
        gain = values("full_time", decoder, "balanced_accuracy") - values(
            "cue_time", decoder, "balanced_accuracy"
        )
        for s in ct.EXPECTED_SEEDS:
            ax.plot(TIMES, gain[s], color=COLORS[s], alpha=0.5)
        ax.plot(TIMES, gain.mean(0), "ko-")
        ax.axhline(
            float(
                (
                    values(
                        "full_time", decoder, "balanced_accuracy", windows=("wholecue",)
                    )
                    - values(
                        "cue_time", decoder, "balanced_accuracy", windows=("wholecue",)
                    )
                ).mean()
            ),
            color="#d1495b",
            linestyle="--",
        )
        ax.set(title=f"Joint−cue BA / {READOUTS[decoder]}")
    gain = values("cue_time", "logistic", "balanced_log_loss") - values(
        "full_time", "logistic", "balanced_log_loss"
    )
    for s in ct.EXPECTED_SEEDS:
        axes[2].plot(TIMES, gain[s], color=COLORS[s], alpha=0.5)
    axes[2].plot(TIMES, gain.mean(0), "ko-")
    axes[2].axhline(
        float(
            (
                values(
                    "cue_time", "logistic", "balanced_log_loss", windows=("wholecue",)
                )
                - values(
                    "full_time", "logistic", "balanced_log_loss", windows=("wholecue",)
                )
            ).mean()
        ),
        color="#d1495b",
        linestyle="--",
    )
    axes[2].set(title="Cue−joint logistic loss (nats)")
    for ax in axes:
        ax.axhline(0, color="gray", linestyle=":")
        ax.set_xlabel("cue-bin center (ms)")
    save(
        fig,
        "joint_training_effects",
        "Paired joint-training effects. Positive favors joint training in all panels. Black=three-seed mean; thin=individual seeds; red dashed=whole cue. The predeclared primary new statistic is the maximum mean logistic gain across ten bins, with matched null maxima—not a selected-bin superiority test.",
    )

    fig, axes = plt.subplots(1, 3, figsize=(14, 4))
    for ax, key, title in zip(
        axes,
        (
            "primary_null_family",
            "secondary_absolute_ba_family",
            "secondary_absolute_logistic_loss_family",
        ),
        (
            "Max paired logistic gain (10 bins)",
            "Max BA (80 views)",
            "Max log2−loss (40 views)",
        ),
        strict=True,
    ):
        family = summary[key]
        ax.hist(family["null"], bins=8, color="#6c9a8b", edgecolor="white")
        ax.axvline(family["observed"], color="#d1495b", lw=2)
        ax.set(
            title=f"{title}\ntail={family['inclusive_plus_one_tail']:.4f}",
            ylabel="null worlds",
            xlabel="same three-seed-mean family statistic",
        )
    save(
        fig,
        "null_families",
        "Twenty accepted source-coherent label-null worlds (bars), observed statistic (red). Inclusive plus-one tails have minimum resolution1/21. Every world uses the same seed average and maximum family; whole cue is excluded. These are no-association references, not equal-risk/superiority p-values or correction for the project's adaptive history.",
    )

    fig, axes = plt.subplots(2, 2, figsize=(11, 7), sharex=True)
    for ax, rep in zip(axes.flat, ct.REPRESENTATIONS, strict=True):
        q = []
        for w in ct.BIN_WINDOWS:
            selected = [
                float(r[f"{rep}_loss_whole_minus_bin"])
                for r in sensitivity
                if r["window"] == w
                and r["readout"] == "logistic"
                and r["seed"] == "mean"
                and r["estimable"] == "True"
            ]
            q.append(np.quantile(selected, [0.025, 0.5, 0.975]))
        q = np.asarray(q)
        ax.fill_between(TIMES, q[:, 0], q[:, 2], alpha=0.25, color="#087e8b")
        ax.plot(TIMES, q[:, 1], color="#087e8b", label="reweight median")
        effect = (
            values(rep, "logistic", "balanced_log_loss", windows=("wholecue",))
            - values(rep, "logistic", "balanced_log_loss")
        ).mean(0)
        ax.plot(TIMES, effect, "ko-", label="original source weights")
        ax.axhline(0, color="gray", linestyle=":")
        ax.set(
            title=NAMES[rep],
            xlabel="cue-bin center (ms)",
            ylabel="whole−bin logistic loss (nats)",
        )
    axes[0, 0].legend(fontsize=8)
    save(
        fig,
        "source_sensitivity",
        "Fixed-model source-pool sensitivity of whole-minus-bin logistic loss. Positive favors the bin. Bands are2.5–97.5% quantiles over200 within-session×class source reweights, NOT biological confidence intervals. Predictions/seeds remain fixed. Eight of22 source deletions lose class support and are inestimable; singleton variability cannot be learned.",
    )

    # Count annotations and normalized-color confusions retain individual seeds, not pooled pseudo-replication.
    for decoder in ct.DECODERS:
        for seed in ct.EXPECTED_SEEDS:
            fig, axes = plt.subplots(4, 11, figsize=(22, 8))
            for i, rep in enumerate(ct.REPRESENTATIONS):
                for j, w in enumerate(ct.WINDOWS):
                    ax = axes[i, j]
                    selected = [
                        r
                        for r in confusions
                        if r["representation"] == rep
                        and r["readout"] == decoder
                        and int(r["seed"]) == seed
                        and r["window"] == w
                    ]
                    if len(selected) != 4:
                        raise RuntimeError("incomplete confusion export")
                    matrix = np.zeros((2, 2))
                    counts = np.zeros((2, 2), dtype=int)
                    for r in selected:
                        a, b = (
                            ct.ft.LABEL_TO_INT[r["true_label"]],
                            ct.ft.LABEL_TO_INT[r["predicted_label"]],
                        )
                        matrix[a, b], counts[a, b] = (
                            float(r["true_class_normalized"]),
                            int(r["count"]),
                        )
                    ax.imshow(matrix, vmin=0, vmax=1, cmap="Blues")
                    for a in (0, 1):
                        for b in (0, 1):
                            ax.text(
                                b,
                                a,
                                f"{counts[a, b]}\n{matrix[a, b]:.0%}",
                                ha="center",
                                va="center",
                                fontsize=7,
                                color="white" if matrix[a, b] > 0.6 else "black",
                            )
                    ax.set(
                        xticks=[0, 1],
                        yticks=[0, 1],
                        xticklabels=["A", "P"],
                        yticklabels=["A", "P"],
                    )
                    if i == 0:
                        ax.set_title(
                            "whole"
                            if w == "wholecue"
                            else f"{j * 100}–{(j + 1) * 100}ms",
                            fontsize=8,
                        )
                    if j == 0:
                        ax.set_ylabel(NAMES[rep], fontsize=9)
            save(
                fig,
                f"confusions_{decoder}_seed{seed}",
                f"{READOUTS[decoder]}, seed{seed}. Rows=true class; columns=predicted class, A=absent/P=present. Each cell prints the actual synthetic count and true-class-normalized recall; color is normalized0–1. Denominators are24 absent/6 present; do not sum seeds as independent trials. Every window and reference representation is shown.",
            )

    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    for arm, color in (("cue_time", "#087e8b"), ("full_time", "#d1495b")):
        for split, linestyle in (("train", "-"), ("validation", "--")):
            for ax, table, field in (
                (axes[0], geom, "participation_ratio"),
                (axes[1], stability, "distance_spearman"),
                (axes[2], stability, "knn10_overlap"),
            ):
                arr = np.array(
                    [
                        [
                            float(
                                next(
                                    r[field]
                                    for r in table
                                    if r["arm"] == arm
                                    and r["split"] == split
                                    and r["space"] == "wholecue80"
                                    and int(r["seed"]) == seed
                                    and int(r["checkpoint_step"]) == step
                                )
                            )
                            for step in ct.CHECKPOINT_STEPS
                        ]
                        for seed in ct.EXPECTED_SEEDS
                    ]
                )
                for seed in ct.EXPECTED_SEEDS:
                    ax.plot(
                        ct.CHECKPOINT_STEPS,
                        arr[seed],
                        color=color,
                        alpha=0.2,
                        linestyle=linestyle,
                    )
                ax.plot(
                    ct.CHECKPOINT_STEPS,
                    arr.mean(0),
                    color=color,
                    linestyle=linestyle,
                    marker="o",
                    label=f"{arm}/{split}",
                )
    for ax, title in zip(
        axes,
        (
            "Whole-cue80 effective dimension",
            "Pairwise-distance rank stability",
            "10-neighbour overlap",
        ),
        strict=True,
    ):
        ax.set(title=title, xlabel="saved encoder updates")
    axes[0].legend(fontsize=7)
    save(
        fig,
        "geometry_evolution",
        "Observed-only saved-checkpoint diagnostics; no decoder/checkpoint selection. Participation ratio=(sum eigenvalues)²/sum squared eigenvalues. Stability compares identical rows to their1000-update representation using full80D Euclidean distances (rank correlation) and10-neighbour overlap. Final self-comparison is1 by construction. Train/validation are separate; thin lines=seeds. This is synthetic representation geometry, not simultaneous brain dynamics or H1b proof.",
    )

    fig, axes = plt.subplots(2, 2, figsize=(12, 7))
    for i, arm in enumerate(ct.CEBRA_REPRESENTATIONS):
        for j, table_field in enumerate(
            ((geom, "participation_ratio"), (stability, "knn10_overlap"))
        ):
            table, field = table_field
            a = np.array(
                [
                    [
                        np.mean(
                            [
                                float(r[field])
                                for r in table
                                if r["arm"] == arm
                                and r["split"] == "validation"
                                and r["space"] == f"bin{b:02d}_8d"
                                and int(r["checkpoint_step"]) == step
                            ]
                        )
                        for b in ct.WINDOW_BINS
                    ]
                    for step in ct.CHECKPOINT_STEPS
                ]
            )
            im = axes[i, j].imshow(
                a,
                aspect="auto",
                cmap="viridis",
                vmin=0,
                vmax=8 if field == "participation_ratio" else 1,
            )
            axes[i, j].set(
                title=f"{NAMES[arm]}: {field}",
                yticks=range(4),
                yticklabels=ct.CHECKPOINT_STEPS,
                xticks=range(10),
                xticklabels=TIMES,
                xlabel="cue-bin center (ms)",
                ylabel="saved updates",
            )
            fig.colorbar(im, ax=axes[i, j])
    save(
        fig,
        "bin_geometry",
        "Validation single-bin8D geometry, averaged across three computational seeds. Left=participation ratio; right=neighbour overlap against the same bin at1000updates. Full spectra and each seed are exported. No label-separation or biological-axis-rotation claim is inferred from these diagnostics.",
    )

    means = []
    for rep in ct.REPRESENTATIONS:
        for decoder in ct.DECODERS:
            for w in ct.WINDOWS:
                row: dict[str, Any] = {
                    "representation": rep,
                    "readout": decoder,
                    "window": w,
                }
                for field in (
                    "balanced_accuracy",
                    "auroc",
                    "recall_absent",
                    "recall_present",
                    "balanced_log_loss",
                    "balanced_brier",
                ):
                    if decoder == "svc" and field in (
                        "balanced_log_loss",
                        "balanced_brier",
                    ):
                        continue
                    v = values(rep, decoder, field, windows=(w,)).ravel()
                    row[field] = float(v.mean())
                    row[field + "_seeds"] = json.dumps(v.tolist())
                means.append(row)
    ct.write_csv(out / "observed_means.csv", means)
    ct.write_csv(out / "observed_seed_metrics.csv", metrics)
    ct.write_csv(out / "observed_confusions.csv", confusions)
    for filename in (
        "geometry_spectra.csv",
        "geometry_stability_vs_final.csv",
        "geometry_summary.json",
    ):
        shutil.copy2(geometry / filename, out / filename)
    shutil.copy2(verified / "verification.json", out / "verification.json")
    shutil.copy2(
        verified / "source_sensitivity_summary.json",
        out / "source_sensitivity_summary.json",
    )
    ct.write_json(out / "summary.json", summary)

    lines = [
        "# When is path-component information readable from the cue?",
        "",
        "**Completed exploratory frozen-model study · October5,2026.** [Offline illustrated report](report.html) · [Frozen protocol](protocol.md) · [Source construction](source-support.md) · [Execution/review](execution.md)",
        "",
        "## Scope and how to read this",
        "",
        "We tested all ten100-ms cue bins separately and compared them with the existing concatenated whole cue, using frozen cue-only/joint CEBRA-Time plus matched raw/PCA references. Logistic and RBF-SVM settings were fixed. **5,040 completed new single-bin readouts;504 saved whole-cue replays;zero encoder/PCA refits.** This includes20 source-coherent null worlds and three computational seeds. Every result was forward-replayed with fitting blocked.",
        "",
        "This predicts a **binary interior path component within fixed4→3**, not goal or a complete ordered route. Goal never varies here. The previously observed400–500ms goal peak came from a different195-unit LDA experiment and did not define this study's window. Historical evaluation sources are exposed; this study diagnoses these frozen representations, not independent biological confirmation.",
        "",
        "## Main finding and advice",
        "",
        "**Whole-cue concatenation was not automatically better in this historical benchmark.** Joint CEBRA + logistic reached88.89% mean balanced accuracy at100–200ms versus61.81% for the whole cue; raw-neural logistic reached94.44% at200–300ms versus46.53% whole-cue. Those are descriptive peaks found while inspecting all bins—not validated windows. A more complex decoder is not necessary to produce a high historical score.",
        "",
        "**The controls prevent treating those peaks as established prospective path coding.** Sixteen of20 source-label null worlds had an80-view maximum at least as large as the observed94.44%; the inclusive plus-one tail is17/21. The predeclared maximum joint-training logistic gain likewise was not exceptional (9/21). This does not prove that hippocampal path information is absent, but these exposed source pools do not validate a best bin. The next scientific priority is a source-support/fold and nuisance-control design, not a GRU or a larger tuning grid. No new-source study is automatically authorized by this result.",
        "",
        "Separately, whole-cue effective dimension in the historical evaluation combinations changed from3.50→3.99 for cue-only and2.92→2.79 for joint across250→1000updates. Training values followed different trends (cue7.73→5.20; joint10.05→9.71). Those train/evaluation differences and source reuse rule out interpreting a lower number as a verified biological manifold dimension. No checkpoint was selected from this diagnostic.",
        "",
        "### Whole cue versus descriptive single-bin peaks",
        "",
        "The maxima below describe the complete curves; **they are not validated best windows or model selections**. Checking many bins makes isolated peaks optimistic. Consult the family-wide nulls and all-seed plots before interpretation.",
        "",
        "|Representation|Readout|Whole BA|Highest observed mean bin BA|Window|Whole AUROC|",
        "|---|---|---:|---:|---|---:|",
    ]
    for rep in ct.REPRESENTATIONS:
        for decoder in ct.DECODERS:
            relevant = [
                r
                for r in means
                if r["representation"] == rep and r["readout"] == decoder
            ]
            whole = next(r for r in relevant if r["window"] == "wholecue")
            peak = max(
                (r for r in relevant if r["window"] != "wholecue"),
                key=lambda r: r["balanced_accuracy"],
            )
            b = ct.bin_label(peak["window"])
            assert b is not None
            lines.append(
                f"|{NAMES[rep]}|{READOUTS[decoder]}|{whole['balanced_accuracy']:.2%}|{peak['balanced_accuracy']:.2%}|{b * 100}–{(b + 1) * 100}ms|{whole['auroc']:.3f}|"
            )
    lines += [
        "",
        "### Controls constrain the claim",
        "",
        f"- Primary maximum paired joint-training logistic gain across10bins: **{summary['primary_null_family']['observed']:.6f}nats**; matched no-association tail **{summary['primary_null_family']['inclusive_plus_one_tail']:.6f}**.",
        f"- Maximum absolute BA across80bin/representation/readout views: **{summary['secondary_absolute_ba_family']['observed']:.2%}**; family tail **{summary['secondary_absolute_ba_family']['inclusive_plus_one_tail']:.6f}**.",
        f"- Maximum constant-baseline logistic loss improvement across40views: **{summary['secondary_absolute_logistic_loss_family']['observed']:.6f}nats**; family tail **{summary['secondary_absolute_logistic_loss_family']['inclusive_plus_one_tail']:.6f}**.",
        "- These20-world references cannot establish equal-risk superiority or undo historical adaptivity/serial dependence. A relative gain over a poor representation is not itself evidence of absolute path information.",
        "- Eight of22 leave-one-source deletions lose class support. Reweighting bands describe the fixed historical source pool, not uncertainty about new animals/sessions.",
        "",
        "## Figures and interpretation boundaries",
        "",
    ]
    for name, caption in captions.items():
        heading = name.replace("_", " ").capitalize()
        if name.startswith("confusions_"):
            lines.extend(
                [
                    f"<details><summary>{heading}: counts and normalized recalls</summary>",
                    "",
                ]
            )
        else:
            lines.extend([f"### {heading}", ""])
        lines.extend([f"![{heading}](figures/{name}.png)", "", caption, ""])
        if name.startswith("confusions_"):
            lines.extend(["</details>", ""])
    lines += [
        "## What this does not establish",
        "",
        "Window-specific decoders are fitted separately: their curves measure accessible information, not a persistent shared code or temporal generalization. Concatenation versus one bin also changes feature count and effective regularization. A predictive difference cannot uniquely identify temporal integration or biological dynamics. Shared encoder weights do not prove shared biological manifolds; checkpoint spectra/stability do not establish H1b. Known labels condition pseudopopulation construction, so these are not predictions of an unknown natural trial. Cue identity/history/view, acquisition simultaneity and source-selection confounds remain unresolved.",
        "",
        "Navigation-time decoding, cross-phase/frozen-decoder temporal-transfer matrices, a matched joint-training goal experiment, new source folds and ordered-path prediction were **not run**. No GRU, new encoder, hyperparameter search, checkpoint selection or window-selection rule was introduced. A future selected-window predictor requires source-safe inner selection, including encoder fitting boundaries, and a separately reviewed run.",
        "",
        "## Numeric evidence",
        "",
        "Figure seed colors for the decoding/effect panels: teal=seed0, orange=seed1, purple=seed2. Thin traces show computational sensitivity, not biological uncertainty.",
        "",
        "[All88 observed mean rows, with seed vectors](observed_means.csv) · [All528 observed train/evaluation seed metric rows](observed_seed_metrics.csv) · [Every observed confusion](observed_confusions.csv) · [Source counts](source_support.csv) · [Full geometry spectra](geometry_spectra.csv) · [Geometry stability](geometry_stability_vs_final.csv) · [Summary](summary.json) · [No-fit verification](verification.json)",
        "",
        "Complete predictions,5040 fitted decoder states, all null-world metrics, per-source sensitivities, original-source mappings and code/runtime snapshots remain in the ignored local run directory. Only small aggregate report exports are placed here; Git does not back up private inputs/models.",
    ]
    lines += [
        "",
        "<details><summary>All observed means (88 rows; no selected-window filtering)</summary>",
        "",
        "|Representation|Decoder|Window|BA|AUROC|Absent recall|Present recall|Log loss|Brier|",
        "|---|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in means:
        cells = [NAMES[row["representation"]], READOUTS[row["readout"]], row["window"]]
        cells += [
            f"{row[field]:.4f}" if field in row else "—"
            for field in (
                "balanced_accuracy",
                "auroc",
                "recall_absent",
                "recall_present",
                "balanced_log_loss",
                "balanced_brier",
            )
        ]
        lines.append("|" + "|".join(cells) + "|")
    lines += ["", "</details>"]
    markdown = "\n".join(lines) + "\n"
    (out / "README.md").write_text(markdown)
    body = MarkdownIt("commonmark", {"html": True}).enable("table").render(markdown)
    for name in captions:
        encoded = base64.b64encode((figures / f"{name}.png").read_bytes()).decode()
        body = body.replace(f"figures/{name}.png", f"data:image/png;base64,{encoded}")
    style = "body{font:17px/1.6 system-ui,sans-serif;color:#20333b;background:#f7f9fa;max-width:1250px;margin:auto;padding:35px}h1,h2,h3{line-height:1.25}h2{border-top:2px solid #dce5e9;padding-top:25px}img{max-width:100%;height:auto;background:white}table{border-collapse:collapse;width:100%;font-size:14px}th,td{padding:7px;border:1px solid #cdd7dc;text-align:left}pre{overflow:auto}a{color:#087e8b}details{margin:24px 0}summary{cursor:pointer;font-weight:700}@media print{body{background:white;padding:0}details{display:block}h2{break-before:page}}"
    (out / "report.html").write_text(
        f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>CEBRA cue-time decoding study</title><style>{style}</style></head><body>{body}</body></html>'
    )
    ct.write_json(
        out / "render_receipt.json",
        {
            "created_utc": ct.utc_now(),
            "run_dir": str(run),
            "verification_dir": str(verified),
            "geometry_dir": str(geometry),
            "renderer_sha256": ct.sha256_file(Path(__file__)),
            "fit_calls": 0,
            "figures": len(captions),
            "html_sha256": ct.sha256_file(out / "report.html"),
        },
    )
    print(
        json.dumps(
            {
                "report": str(out / "report.html"),
                "figures": len(captions),
                "means": len(means),
            }
        )
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--verified-dir", type=Path, required=True)
    parser.add_argument("--geometry-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=ct.DOC_DIR)
    args = parser.parse_args()
    with ct.no_fit_guard():
        render(
            args.run_dir.resolve(),
            args.verified_dir.resolve(),
            args.geometry_dir.resolve(),
            args.output_dir.resolve(),
        )


if __name__ == "__main__":
    main()
