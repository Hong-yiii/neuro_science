"""Descriptive saved-embedding fidelity and spectrum for cue-time geometry.

Extracted from scripts/cebra_latent_atlas.py; older implementations remain historical only.
"""

from __future__ import annotations

import numpy as np
from scipy.spatial.distance import cdist
from scipy.stats import spearmanr


def require(condition, message):
    if not condition:
        raise ValueError(message)


def spectrum(x):
    power = np.linalg.svd(x - x.mean(axis=0), compute_uv=False) ** 2
    total = power.sum()
    if total <= np.finfo(float).eps:
        return {
            "fractions": [],
            "participation_ratio": None,
            "norm_mean": float(np.linalg.norm(x, axis=1).mean()),
        }
    fractions = power / total
    return {
        "fractions": fractions.tolist(),
        "participation_ratio": float(1 / (fractions @ fractions)),
        "norm_mean": float(np.linalg.norm(x, axis=1).mean()),
    }


def rank_correlation(a, b):
    if len(a) < 3 or np.ptp(a) == 0 or np.ptp(b) == 0:
        return None
    return np.asarray(spearmanr(a, b)[0], dtype=float).item()


def fidelity(full, view, row_ids, k=10):
    d, p = cdist(full, full), cdist(view, view)
    allowed = row_ids[:, None] != row_ids[None, :]
    upper = np.triu(allowed, 1)
    require(allowed.sum(axis=1).min() > k, "too few cross-row neighbors")
    dv, pv = d[upper], p[upper]
    d[~allowed] = p[~allowed] = np.inf
    near_d, near_p = (
        np.argsort(d, axis=1, kind="stable")[:, :k],
        np.argsort(p, axis=1, kind="stable")[:, :k],
    )
    overlap = np.mean(
        [len(set(a) & set(b)) / k for a, b in zip(near_d, near_p, strict=True)]
    )
    # ponytail: fixed-size diagnostic sample bounds pairwise memory; not source-independent inference.
    return {
        "distance_spearman": rank_correlation(dv, pv),
        "knn10_overlap": float(overlap) if np.ptp(dv) > 0 and np.ptp(pv) > 0 else None,
        "sample_points": len(full),
        "sample_rows": len(np.unique(row_ids)),
        "zero_distance_pair_fraction": float(np.mean(dv < 1e-12)),
        "k_boundary_tie_fraction": float(
            np.mean(np.sort(d, axis=1)[:, k - 1] == np.sort(d, axis=1)[:, k])
        ),
    }
