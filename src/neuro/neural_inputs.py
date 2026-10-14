"""Count/exposure binning and cell-to-session identity for maintained cohorts.

Extracted from scripts/place195_v7_v8_neural_experiments.py; older implementations remain historical only.
"""

from __future__ import annotations

from collections.abc import Iterable

import numpy as np


def session_from_cell(cell_id: str) -> str:
    parts = cell_id.split("/")
    return f"{parts[0]}_{parts[1]}"


def bin_events(
    events: Iterable[float], duration: float, bin_width: float, nominal: float = 1.0
) -> tuple[np.ndarray, np.ndarray, int]:
    n_bins = int(round(nominal / bin_width))
    counts = np.zeros(n_bins, dtype=np.float32)
    exposure = np.zeros(n_bins, dtype=np.float32)
    included_end = min(duration, nominal)
    for i in range(n_bins):
        start = i * bin_width
        end = start + bin_width
        exposure[i] = max(0.0, min(end, included_end) - start)
    omitted = 0
    for t in events:
        if not (0.0 <= t < duration):
            continue
        if 0.0 <= t < included_end:
            idx = int(t / bin_width)
            if 0 <= idx < n_bins:
                counts[idx] += 1.0
        elif nominal <= t < duration:
            omitted += 1
    return counts, exposure, omitted
