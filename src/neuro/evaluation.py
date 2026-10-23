"""Matched-support descriptive classification metrics, without pseudorow IID CIs."""

from __future__ import annotations

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
    log_loss,
)


def classification_metrics(
    targets, predictions, *, classes, probabilities=None
) -> dict:
    """Class order is explicit and must cover every declared class in evaluation.

    Values summarize these constructed rows. They are not biological uncertainty
    estimates; source-block/seed sensitivity requires a separately declared design.
    """
    y, pred, order = np.asarray(targets), np.asarray(predictions), np.asarray(classes)
    if (
        y.ndim != 1
        or pred.shape != y.shape
        or not len(y)
        or order.ndim != 1
        or len(order) < 2
    ):
        raise ValueError("invalid target/prediction/class shape")
    if (
        len(np.unique(order)) != len(order)
        or set(y.tolist()) != set(order.tolist())
        or not set(pred.tolist()) <= set(order.tolist())
    ):
        raise ValueError("duplicate classes, incomplete support or unknown predictions")
    counts = confusion_matrix(y, pred, labels=order)
    result = {
        "n_constructed_rows": len(y),
        "classes": order.tolist(),
        "accuracy": float(accuracy_score(y, pred)),
        "balanced_accuracy": float(balanced_accuracy_score(y, pred)),
        "macro_f1": float(f1_score(y, pred, labels=order, average="macro")),
        "confusion_counts": counts.tolist(),
        "confusion_normalized": (counts / counts.sum(axis=1, keepdims=True)).tolist(),
        "uncertainty": "none; synthetic rows are not independent biological observations",
    }
    if probabilities is not None:
        p = np.asarray(probabilities, dtype=float)
        if (
            p.shape != (len(y), len(order))
            or not np.isfinite(p).all()
            or np.any((p < 0) | (p > 1))
            or not np.allclose(p.sum(axis=1), 1)
        ):
            raise ValueError("invalid class probabilities")
        # Preserve validated distributions while removing float32 row-sum rounding
        # before sklearn's float64 log-loss check (sklearn normalizes internally too).
        p = p / p.sum(axis=1, keepdims=True)
        # sklearn log_loss sorts labels, so explicitly reorder caller columns first.
        sorted_order = np.argsort(order)
        result["log_loss"] = float(
            log_loss(y, p[:, sorted_order], labels=order[sorted_order])
        )
    return result
