"""Descriptive notebook diagnostics; no fitting, checkpoint or source-file access.

The notebook retains the experiment and its decisions. These functions render the
already computed metrics/coordinates and summarize optimization instrumentation.
Pseudorows, bins and seeds never become independent biological observations here.
"""

from __future__ import annotations

from collections.abc import Mapping
import re

import matplotlib.pyplot as plt
import numpy as np


_RUN = re.compile(
    r"^(observed|permuted)_seed(\d+)_(full|reduced)_(raw|pca|cebra|lda)_(pair|start|goal)$"
)
_ROLES = ("reference", "positive", "negative")


def metrics_table(rows):
    """Readable, unpooled readouts; percentages and percentage points are explicit."""
    table = []
    for row in rows:
        match = _RUN.fullmatch(row["name"])
        if match is None:
            raise ValueError(
                "readout name must declare world, seed, budget, model and head"
            )
        world, seed, budget, model, head = match.groups()
        if head != row["head"]:
            raise ValueError("readout head disagrees with its name")
        dev, train = row["development"], row["train"]
        confusion = np.asarray(dev["confusion_counts"])
        if (
            confusion.ndim != 2
            or confusion.shape[0] < 2
            or confusion.shape[0] != confusion.shape[1]
            or not np.isfinite(confusion).all()
            or np.any(confusion < 0)
            or np.any(confusion.sum(axis=1) == 0)
        ):
            raise ValueError("complete nonnegative square confusion counts required")
        classes = len(confusion)
        values = {
            "world": world,
            "seed": int(seed),
            "budget": budget,
            "model": model,
            "head": head,
            "classes": classes,
            "constructed_development_rows": int(confusion.sum()),
            "train_BA_percent": 100 * float(train["balanced_accuracy"]),
            "development_BA_percent": 100 * float(dev["balanced_accuracy"]),
            "uniform_BA_percent": 100 / classes,
            "gap_percentage_points": 100
            * (float(train["balanced_accuracy"]) - float(dev["balanced_accuracy"])),
            "accuracy_percent": 100 * float(dev["accuracy"]),
            "macro_F1": float(dev["macro_f1"]),
            "log_loss_nats": dev.get("log_loss"),
            "uniform_log_loss_nats": float(np.log(classes)),
        }
        table.append(values)
    return table


def plot_decoder_summary(rows):
    """Show each seed, each source budget and each world; no inferred error bars."""
    table = metrics_table(rows)
    if not table:
        raise ValueError("at least one readout is required")
    worlds = [
        w for w in ("observed", "permuted") if any(r["world"] == w for r in table)
    ]
    heads = [h for h in ("pair", "start", "goal") if any(r["head"] == h for r in table)]
    panels = [
        (w, h)
        for w in worlds
        for h in heads
        if any(r["world"] == w and r["head"] == h for r in table)
    ]
    fig, axes = plt.subplots(
        len(panels),
        2,
        figsize=(12, 3.1 * len(panels)),
        squeeze=False,
        constrained_layout=True,
    )
    colors = {"full": "tab:blue", "reduced": "tab:orange"}
    for axes_row, (world, head) in zip(axes, panels, strict=True):
        records = [r for r in table if r["world"] == world and r["head"] == head]
        class_counts = {r["classes"] for r in records}
        if len(class_counts) != 1:
            raise ValueError("compared readouts need identical target class support")
        models = [
            m
            for m in ("raw", "pca", "cebra", "lda")
            if any(r["model"] == m for r in records)
        ]
        seeds = sorted({r["seed"] for r in records})
        for budget, offset in (("full", -0.14), ("reduced", 0.14)):
            selected = [r for r in records if r["budget"] == budget]
            if not selected:
                continue
            x = [
                models.index(r["model"])
                + offset
                + 0.05 * (seeds.index(r["seed"]) - (len(seeds) - 1) / 2)
                for r in selected
            ]
            axes_row[0].scatter(
                x,
                [r["development_BA_percent"] for r in selected],
                color=colors[budget],
                label=budget + " training sources",
                s=38,
            )
            axes_row[1].scatter(
                x,
                [r["gap_percentage_points"] for r in selected],
                color=colors[budget],
                s=38,
            )
            for ax, metric in zip(
                axes_row,
                ("development_BA_percent", "gap_percentage_points"),
                strict=True,
            ):
                for xi, record in zip(x, selected, strict=True):
                    ax.annotate(
                        str(record["seed"]),
                        (xi, record[metric]),
                        xytext=(4, 4),
                        textcoords="offset points",
                        fontsize=7,
                    )
        chance = 100 / next(iter(class_counts))
        axes_row[0].axhline(
            chance,
            color="0.4",
            linestyle=":",
            label=f"Uniform reference: {chance:.1f}%",
        )
        axes_row[1].axhline(0, color="0.4", linestyle=":")
        axes_row[0].set(ylabel="Development balanced accuracy (%)", ylim=(-3, 107))
        axes_row[1].set(ylabel="Train − development BA (percentage points)")
        for ax, suffix in zip(
            axes_row, ("readout performance", "generalization gap"), strict=True
        ):
            ax.set(
                xticks=range(len(models)),
                xticklabels=[m.upper() for m in models],
                title=f"{world} · {head} · {suffix}",
            )
            ax.grid(axis="y", alpha=0.15)
        axes_row[0].legend(fontsize=8, loc="best")
    fig.suptitle(
        "Every dot is one computational seed (numbered); no biological confidence intervals"
    )
    return fig


def _time_tensor(features, n_bins):
    values = np.asarray(features)
    if (
        isinstance(n_bins, bool)
        or not isinstance(n_bins, (int, np.integer))
        or n_bins < 1
    ):
        raise ValueError("n_bins must be a positive integer")
    if (
        values.ndim != 2
        or not all(values.shape)
        or values.shape[1] % n_bins
        or values.dtype.kind not in "fiu"
        or not np.isfinite(values).all()
    ):
        raise ValueError(
            "finite nonempty time-major rows × (bins × coordinates) required"
        )
    return values.reshape(len(values), n_bins, -1)


def _embedding_pair(train_features, development_features, n_bins):
    train = _time_tensor(train_features, n_bins)
    development = _time_tensor(development_features, n_bins)
    if train.shape[1:] != development.shape[1:]:
        raise ValueError("training and development coordinate/bin dimensions differ")
    return train, development


def embedding_summary(train_features, development_features, *, n_bins):
    """Distribution/collapse diagnostics in the existing coordinates, without fitting.

    Effective rank is the participation ratio (sum(lambda)**2 / sum(lambda**2))
    of the centered coordinate covariance. It is descriptive, not a state count.
    The first-three fraction concerns this fitted embedding, not raw neural data.
    """
    train, development = _embedding_pair(train_features, development_features, n_bins)
    summary = {
        "layout": "time-major",
        "bins_per_pseudorow": int(n_bins),
        "coordinate_count": int(train.shape[2]),
    }
    for name, tensor in (("train", train), ("development", development)):
        vectors = tensor.reshape(-1, tensor.shape[-1]).astype(float)
        centered = vectors - vectors.mean(axis=0)
        covariance = centered.T @ centered / max(len(vectors) - 1, 1)
        eigenvalues = np.maximum(np.linalg.eigvalsh(covariance), 0)[::-1]
        total = float(eigenvalues.sum())
        denominator = float(eigenvalues @ eigenvalues)
        trace = np.diag(covariance)
        summary[name] = {
            "finite": True,
            "pseudorows": int(len(tensor)),
            "dependent_bin_vectors": int(len(vectors)),
            "norm_quantiles_0_50_100": np.quantile(
                np.linalg.norm(vectors, axis=1), [0, 0.5, 1]
            ).tolist(),
            "coordinate_std": vectors.std(axis=0).tolist(),
            "covariance_eigenvalues": eigenvalues.tolist(),
            "effective_rank_participation_ratio": total * total / denominator
            if denominator > 0
            else 0.0,
            "first_three_coordinate_variance_fraction": float(trace[:3].sum() / total)
            if total > 0
            else None,
            "zero_centered_variance": total == 0,
        }
    return summary


def _heads(targets, n_rows):
    if isinstance(targets, Mapping):
        if not {"start", "goal"} <= set(targets):
            raise ValueError("targets mapping requires start and goal arrays")
        result = {name: np.asarray(targets[name]) for name in ("start", "goal")}
    else:
        pair = np.asarray(targets)
        if pair.ndim != 1:
            raise ValueError("ordered-pair target array must be one-dimensional")
        components = [str(value).split("->") for value in pair]
        if any(
            len(value) != 2 or not all(value) or value[0] == value[1]
            for value in components
        ):
            raise ValueError("explicit unequal start->goal pair labels required")
        result = {
            "start": np.array([v[0] for v in components]),
            "goal": np.array([v[1] for v in components]),
        }
    if any(value.shape != (n_rows,) for value in result.values()):
        raise ValueError("one start/goal target per development pseudorow required")
    return result


def plot_embedding_views(
    train_features, development_features, targets, *, n_bins, title
):
    """Three direct-coordinate 3D views; no PCA/t-SNE/UMAP fitted for the display.

    targets accepts target_heads(development) or explicit start->goal strings.
    Native coordinates 1–3 preserve the fitted model; remaining dimensions are
    omitted. Pooled cue bins are dependent and are never connected as trajectories.
    """
    train, development = _embedding_pair(train_features, development_features, n_bins)
    if train.shape[-1] < 3:
        raise ValueError("3D views require at least three fitted coordinates")
    heads = _heads(targets, len(development))
    fig = plt.figure(figsize=(15, 4.8))
    axes = [fig.add_subplot(1, 3, i + 1, projection="3d") for i in range(3)]
    train_first, dev_first = train[:, 0, :3], development[:, 0, :3]
    for ax, head in zip(axes[:2], ("start", "goal"), strict=True):
        ax.scatter(*train_first.T, color="0.75", alpha=0.25, s=8, label="Train, bin 0")
        for i, label in enumerate(np.unique(heads[head])):
            points = dev_first[heads[head] == label]
            ax.scatter(
                *points.T,
                s=13,
                alpha=0.7,
                color=plt.get_cmap("tab10")(i % 10),
                label=str(label),
            )
        ax.set_title(f"Development bin 0, coloured by {head}", fontsize=10)
        ax.legend(
            title=head + " (categorical)",
            fontsize=7,
            title_fontsize=8,
            loc="upper left",
        )
    points = development[:, :, :3].reshape(-1, 3)
    colours = np.tile(np.arange(n_bins), len(development))
    view = axes[2].scatter(
        *points.T,
        c=colours,
        cmap="viridis",
        vmin=0,
        vmax=max(n_bins - 1, 1),
        s=5,
        alpha=0.35,
    )
    axes[2].set_title("Development, every cue bin (dependent)", fontsize=10)
    fig.colorbar(
        view, ax=axes[2], shrink=0.6, pad=0.1, label="Native cue bin index (0-based)"
    )
    # The same view and physical coordinate scales make panels directly comparable.
    all_points = np.concatenate((train[:, :, :3].reshape(-1, 3), points))
    bounds = [
        (float(all_points[:, i].min()), float(all_points[:, i].max())) for i in range(3)
    ]
    for ax in axes:
        ax.set(xlabel="Coordinate 1", ylabel="Coordinate 2", zlabel="Coordinate 3")
        ax.view_init(elev=20, azim=35)
        for setter, (lower, upper) in zip(
            (ax.set_xlim, ax.set_ylim, ax.set_zlim), bounds, strict=True
        ):
            padding = max((upper - lower) * 0.05, 1e-6)
            setter(lower - padding, upper + padding)
    fig.suptitle(
        title
        + f"\nDirect coordinates 1–3 of {train.shape[-1]}; no additional projection fit",
        fontsize=11,
    )
    fig.text(
        0.5,
        0.015,
        "Points are constructed rows/bins, not simultaneous trials. Separation is descriptive; readout scores assess recoverability.",
        ha="center",
        fontsize=9,
    )
    fig.subplots_adjust(top=0.79, bottom=0.12, wspace=0.15)
    return fig


def _learning_arrays(encoder):
    diagnostics = encoder.diagnostics
    loss = {
        name: np.asarray(values, dtype=float)
        for name, values in diagnostics["loss"].items()
    }
    if "total" not in loss or not len(loss["total"]):
        raise ValueError("nonempty total loss history required")
    if any(
        values.ndim != 1 or len(values) != len(loss["total"])
        for values in loss.values()
    ):
        raise ValueError("loss components must have one entry per optimizer update")
    counts = np.asarray(diagnostics["sample_exposure_counts"])
    if (
        counts.ndim != 2
        or counts.shape[0] != 3
        or not counts.shape[1]
        or not np.isfinite(counts).all()
        or np.any(counts < 0)
    ):
        raise ValueError(
            "nonnegative reference/positive/negative × vector exposure required"
        )
    return diagnostics, loss, counts


def learning_summary(encoder):
    """Optimization/exposure evidence only; a falling loss is not decoding evidence."""
    diagnostics, loss, counts = _learning_arrays(encoder)
    window = max(1, min(50, len(loss["total"]) // 5))
    return {
        "updates_recorded": len(loss["total"]),
        "finite_loss_components": {
            name: bool(np.isfinite(values).all()) for name, values in loss.items()
        },
        "summary_window_updates": window,
        "loss_components": {
            name: {
                "first_window_mean": float(values[:window].mean()),
                "last_window_mean": float(values[-window:].mean()),
                "last_minus_first": float(
                    values[-window:].mean() - values[:window].mean()
                ),
            }
            for name, values in loss.items()
        },
        "sampler": {
            role: {
                "available_vectors": int(len(values)),
                "vectors_used": int(np.count_nonzero(values)),
                "coverage_fraction": float(np.mean(values > 0)),
                "uses_min_median_max": np.quantile(values, [0, 0.5, 1]).tolist(),
                "total_draws": int(values.sum()),
            }
            for role, values in zip(_ROLES, counts, strict=True)
        },
        "reference_phase_counts": diagnostics.get("exposure_summary", {}).get(
            "reference_phase_counts", {}
        ),
        "reading_rule": "Loss measures optimization. Coverage includes structurally unavailable edge roles; it is not biological sample size. Check geometry and matched development readouts separately.",
    }


def plot_learning(encoder, *, title):
    """Display actual solver components and separate sampling roles, without smoothing."""
    _, loss, counts = _learning_arrays(encoder)
    fig, axes = plt.subplots(1, 3, figsize=(14, 3.8), constrained_layout=True)
    updates = np.arange(1, len(loss["total"]) + 1)
    axes[0].plot(updates, loss["total"], label="total", linewidth=1)
    axes[0].set(
        xlabel="Optimizer update",
        ylabel="Logged InfoNCE loss",
        title="Optimization objective",
    )
    for name in ("pos", "neg"):
        if name in loss:
            axes[1].plot(updates, loss[name], label="solver " + name, linewidth=1)
    axes[1].set(
        xlabel="Optimizer update",
        ylabel="Logged component value",
        title="Positive / negative components",
    )
    if axes[1].lines:
        axes[1].legend(fontsize=8)
    maximum = max(int(counts.max()), 1)
    bins = np.linspace(-0.5, maximum + 0.5, min(maximum + 2, 31))
    for role, values in zip(_ROLES, counts, strict=True):
        axes[2].hist(values, bins=bins, histtype="step", linewidth=1.3, label=role)
    axes[2].set(
        xlabel="Uses per constructed row/bin vector",
        ylabel="Vector count",
        title="Sampler coverage, by role",
    )
    axes[2].legend(fontsize=8)
    fig.suptitle(
        title + " · optimization/exposure, not biological evidence", fontsize=11
    )
    return fig
