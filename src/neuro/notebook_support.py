"""Small observable notebook operations; experiment loops stay in notebook cells."""

from __future__ import annotations

import os
import tempfile
import warnings
from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from sklearn.exceptions import ConvergenceWarning
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from threadpoolctl import threadpool_limits

from neuro.pca_lda import feature_matrix
from neuro.pseudopopulation import (
    ablate_training_sources,
    materialize,
    sample_plan,
    source_usage,
    support,
)


def workspace() -> Path:
    supplied = os.environ.get("NEURO_NOTEBOOK_OUTPUT")
    if supplied is None:
        return Path(tempfile.mkdtemp(prefix="neuro-invented-notebook-"))
    root = Path(supplied)
    root.mkdir(mode=0o700, parents=True, exist_ok=False)
    return root


def fit_logistic(features, targets, *, C, max_iter):
    classifier = LogisticRegression(C=C, max_iter=max_iter, solver="lbfgs")
    model = make_pipeline(StandardScaler(), classifier)
    with warnings.catch_warnings(), threadpool_limits(limits=2):
        warnings.simplefilter("error", ConvergenceWarning)
        model.fit(feature_matrix(features), targets)
    if not all(
        np.isfinite(v).all() for v in (classifier.coef_, classifier.intercept_)
    ) or np.any(classifier.n_iter_ >= max_iter):
        raise RuntimeError("nonfinite or unconverged logistic readout")
    return model


def source_budget(data, effective, *, reduced, subset_seed):
    if not reduced:
        return data, effective
    pools = [
        r
        for r in support(data, effective_conditions=effective)
        if r["split_id"] == data.train_split
    ]
    if min(r["source_count"] for r in pools) < 2:
        raise ValueError("full pools need >=2 before floor-half intervention")
    reduced_data = ablate_training_sources(
        data, fraction=0.5, seed=subset_seed, effective_conditions=effective
    )
    ids = {s.source_id for s in reduced_data.sources}
    return reduced_data, {
        sid: condition for sid, condition in effective.items() if sid in ids
    }


def checked_assemblies(
    data, effective, development_plan, reference_development, *, config, seed
):
    training_plan = sample_plan(
        data,
        split_id=data.train_split,
        rows_per_condition=config["train_rows_per_condition"],
        seed=seed,
        effective_conditions=effective,
    )
    train = materialize(data, training_plan)
    development = materialize(data, development_plan)
    np.testing.assert_array_equal(development.values, reference_development.values)
    np.testing.assert_array_equal(development.targets, reference_development.targets)
    np.testing.assert_array_equal(development.exposure, reference_development.exposure)
    if development.plan != reference_development.plan:
        raise AssertionError("development lineage changed")
    train_ids = {sid for row in train.plan.rows for sid in row.source_ids}
    dev_ids = {sid for row in development.plan.rows for sid in row.source_ids}
    source_by_id = {s.source_id: s for s in data.sources}

    def contributors(ids):
        return {c for sid in ids for c in (sid, *source_by_id[sid].dependency_ids)}

    if contributors(train_ids) & contributors(dev_ids):
        raise AssertionError("assembly direct contributors overlap")
    return train, development


def usage_summary(data, assembly):
    usage = source_usage(data, assembly)
    counts = [r["uses"] for r in usage]
    return {
        "eligible_sources": len(counts),
        "used_sources": sum(n > 0 for n in counts),
        "unused_sources": sum(n == 0 for n in counts),
        "repeated_sources": sum(n > 1 for n in counts),
        "reuse_histogram": dict(sorted(Counter(counts).items())),
    }


def plot_input_audit(inspection, data, neural_audit):
    """Pseudonymous metadata timeline, selection waterfall, support and exposure."""
    blocks = sorted({s["block_id"] for s in inspection.eligible})
    aliases = {block: i for i, block in enumerate(blocks)}
    fig, axes = plt.subplots(2, 3, figsize=(14, 7), constrained_layout=True)
    for split, color in (("train", "tab:blue"), ("development", "tab:orange")):
        rows = [s for s in inspection.eligible if s["split_id"] == split]
        axes[0, 0].scatter(
            [s["trial_order"] for s in rows],
            [aliases[s["block_id"]] for s in rows],
            s=2,
            alpha=0.4,
            label=split,
            c=color,
        )
    axes[0, 0].set(
        title="Original exposed source assignment",
        xlabel="Within-block trial order",
        ylabel="Pseudonymous block index",
    )
    axes[0, 0].legend()
    a = inspection.audit
    labels = ["eligible", "surviving train", "selected train", "selected dev"]
    axes[0, 1].bar(
        labels,
        [
            a["eligible"],
            a["surviving_train"],
            a["selected_train"],
            a["selected_development"],
        ],
    )
    axes[0, 1].tick_params(axis="x", labelrotation=30)
    axes[0, 1].set(
        title="Metadata-only selection waterfall", ylabel="Real source examples"
    )
    rows = support(data)
    for split in ("train", "development"):
        axes[0, 2].hist(
            [r["source_count"] for r in rows if r["split_id"] == split],
            alpha=0.5,
            label=split,
        )
    axes[0, 2].set(
        title="Block × pair support", xlabel="Eligible sources per pool", ylabel="Pools"
    )
    axes[0, 2].legend()
    targets = Counter(t.condition for t in data.targets)
    axes[1, 0].bar(range(len(targets)), list(targets.values()))
    axes[1, 0].set(
        title="Selected source class distribution",
        xlabel="Ordered-pair class index",
        ylabel="Real sources",
    )
    axes[1, 1].bar(
        ["observed", "unavailable"],
        [int(data.observed.sum()), int((~data.observed).sum())],
    )
    axes[1, 1].set(
        title="Source × unit availability",
        ylabel="Source-unit pairs; missing is not zero",
    )
    axes[1, 2].hist(data.exposure.reshape(-1), bins=10)
    axes[1, 2].set(
        title="Validated source-bin exposure",
        xlabel=f"Exposure ({data.time_unit})",
        ylabel="Source bins",
    )
    return fig


def plot_confusions(rows, *, title):
    """Both count and row-normalized development confusions for every saved readout."""
    fig, axes = plt.subplots(
        len(rows),
        2,
        figsize=(8, max(3, len(rows) * 2.5)),
        squeeze=False,
        constrained_layout=True,
    )
    for axrow, row in zip(axes, rows, strict=True):
        for ax, key in zip(
            axrow, ("confusion_counts", "confusion_normalized"), strict=True
        ):
            image = ax.imshow(row["development"][key], vmin=0)
            ax.set(
                title=f"{row['name']} {key}",
                xlabel="Predicted class index",
                ylabel="Effective class index",
            )
            fig.colorbar(image, ax=ax, fraction=0.04)
    fig.suptitle(title)
    return fig


def compact_metrics(rows):
    return [
        {
            "name": row["name"],
            "head": row["head"],
            "train_BA": row["train"]["balanced_accuracy"],
            "development_BA": row["development"]["balanced_accuracy"],
            "accuracy": row["development"]["accuracy"],
            "macro_F1": row["development"]["macro_f1"],
            "log_loss": row["development"].get("log_loss"),
            "train_development_gap": row["balanced_accuracy_gap"],
        }
        for row in rows
    ]
