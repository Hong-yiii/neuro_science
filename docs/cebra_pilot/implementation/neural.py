"""Mask-aware cue-period count and rate summaries.

Public arrays are always ``(cue_bin, unit)``. This module rejects mismatched axes
instead of transposing or guessing.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np

from .contracts import CueNavigationTrial


@dataclass(frozen=True)
class CueSummary:
    """Per-unit cue summary with unit order copied from the input columns."""

    unit_ids: tuple[str, ...]
    counts_by_unit: np.ndarray
    rates_hz_by_unit: np.ndarray
    valid_bin_count: int
    total_exposure_seconds: float


def _readonly(array: np.ndarray) -> np.ndarray:
    out = np.array(array, copy=True)
    out.setflags(write=False)
    return out


def summarize_cue_activity(
    counts_by_bin_unit: np.ndarray,
    valid_mask: np.ndarray,
    exposure_seconds_by_bin: np.ndarray,
    unit_ids: Sequence[str],
) -> CueSummary:
    """Return mask-aware cue counts and exposure-normalized rates.

    ``counts_by_bin_unit[b, u]`` is the spike count for cue bin ``b`` and unit
    ``u``. The rate denominator is the sum of exposure over valid cue bins.
    """

    counts = np.asarray(counts_by_bin_unit)
    if counts.ndim != 2:
        raise ValueError("counts_by_bin_unit must have shape (cue_bin, unit)")
    if not np.issubdtype(counts.dtype, np.integer):
        raise ValueError("counts_by_bin_unit must contain integer counts")
    if np.any(counts < 0):
        raise ValueError("counts_by_bin_unit must be nonnegative")

    units = tuple(unit_ids)
    if any(not isinstance(unit, str) or not unit for unit in units):
        raise ValueError("unit_ids must be non-empty strings")
    if len(units) != counts.shape[1]:
        raise ValueError("unit_ids length must match the second axis (unit)")
    if len(set(units)) != len(units):
        raise ValueError("unit_ids must be unique")

    mask = np.asarray(valid_mask)
    if mask.dtype != np.bool_ or mask.ndim != 1 or mask.shape[0] != counts.shape[0]:
        raise ValueError("valid_mask must be a bool vector aligned to cue bins")

    exposure = np.asarray(exposure_seconds_by_bin, dtype=float)
    if exposure.ndim != 1 or exposure.shape[0] != counts.shape[0]:
        raise ValueError("exposure_seconds_by_bin must align to cue bins")

    valid_exposure = exposure[mask]
    if valid_exposure.size == 0:
        raise ValueError("at least one valid cue bin is required")
    if not np.all(np.isfinite(valid_exposure)) or np.any(valid_exposure <= 0.0):
        raise ValueError("valid cue bins require positive finite exposure")

    try:
        denominator = float(np.sum(valid_exposure))
        valid_bin_count = int(np.count_nonzero(mask))
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError("cue mask/exposure could not be summarized") from exc
    if denominator <= 0.0:
        raise ValueError("valid exposure denominator must be nonzero")

    counts_by_unit = np.sum(counts[mask, :], axis=0)
    rates = counts_by_unit.astype(float) / denominator
    return CueSummary(
        unit_ids=units,
        counts_by_unit=_readonly(counts_by_unit),
        rates_hz_by_unit=_readonly(rates),
        valid_bin_count=valid_bin_count,
        total_exposure_seconds=denominator,
    )


def summarize_trial_cue_activity(trial: CueNavigationTrial) -> CueSummary:
    """Summarize a validated scientific trial contract."""

    return summarize_cue_activity(
        trial.cue_counts_by_bin_unit,
        trial.cue_valid_mask,
        trial.cue_exposure_seconds,
        trial.unit_ids,
    )
