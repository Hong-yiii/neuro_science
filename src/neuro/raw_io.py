"""Ripple markers and spike timestamps required by maintained studies.

Readers open only supplied paths. CSV precision preserves accepted import boundaries.

Extracted from scripts/import_place195_sessions.py; older implementations remain historical only.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import h5py  # type: ignore[reportMissingImports]
import numpy as np
from scipy.io import loadmat


@dataclass(frozen=True)
class EventTrials:
    codes: np.ndarray
    times: np.ndarray
    rows: np.ndarray | None = None
    bad_event_count: int = 0
    first_numeric_line: int | None = None


@dataclass(frozen=True)
class SpikeTrain:
    timestamps_seconds: np.ndarray
    mat_format: str
    reference: str
    components: str
    sorted_input: bool


def _to_int(value: Any) -> int:
    try:
        if isinstance(value, np.generic):
            value = value.item()
        return int(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(f"expected integer-like value, got {value!r}") from exc


def _to_float(value: Any) -> float:
    try:
        if isinstance(value, np.generic):
            value = value.item()
        return float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(f"expected float-like value, got {value!r}") from exc


def read_ripple_trials(path: Path) -> EventTrials:
    with h5py.File(path, "r") as handle:
        group = _find_hdf5_group_with(
            handle, ("markers", "timeStamps"), ("rp/data", "df/data")
        )
        markers = _event_matrix(np.asarray(group["markers"]), path, "ripple markers")
        timestamps = _event_matrix(
            np.asarray(group["timeStamps"]), path, "ripple timeStamps"
        )
    return EventTrials(
        codes=np.rint(markers).astype(int), times=timestamps.astype(float)
    )


def read_spiketrain(path: Path) -> SpikeTrain:
    if h5py.is_hdf5(path):
        with h5py.File(path, "r") as handle:
            timestamps = np.asarray(handle["timestamps"], dtype=float).reshape(-1)
            reference = _decode_matlab_string(np.asarray(handle.get("reference", [])))
            components = _scalar_to_string(np.asarray(handle.get("components", [])))
        mat_format = "matlab_v7_3_hdf5"
    else:
        mat = loadmat(path, squeeze_me=True, chars_as_strings=True)
        timestamps = np.asarray(mat["timestamps"], dtype=float).reshape(-1)
        reference = _decode_matlab_string(mat.get("reference", ""))
        components = _scalar_to_string(mat.get("components", ""))
        mat_format = "matlab_v5"

    sorted_input = bool(np.all(np.diff(timestamps) >= 0)) if timestamps.size else True
    if not sorted_input:
        timestamps = np.sort(timestamps)
    return SpikeTrain(
        timestamps_seconds=timestamps / 1000.0,
        mat_format=mat_format,
        reference=reference,
        components=components,
        sorted_input=sorted_input,
    )


def spikes_in_window(
    timestamps_seconds: np.ndarray, start: float, end: float
) -> np.ndarray:
    left = _to_int(np.searchsorted(timestamps_seconds, start, side="left"))
    right = _to_int(np.searchsorted(timestamps_seconds, end, side="left"))
    return timestamps_seconds[left:right]


def _find_hdf5_group_with(
    handle: h5py.File, names: Sequence[str], preferred: Sequence[str]
) -> h5py.Group:
    for group_name in preferred:
        if group_name in handle:
            group = handle[group_name]
            if isinstance(group, h5py.Group) and all(name in group for name in names):
                return group
    found: list[h5py.Group] = []

    def visitor(_name: str, obj: h5py.Group | h5py.Dataset) -> None:
        if isinstance(obj, h5py.Group) and all(name in obj for name in names):
            found.append(obj)

    handle.visititems(visitor)
    if not found:
        raise KeyError(f"no HDF5 group contains {names}")
    return found[0]


def _event_matrix(array: np.ndarray, path: Path, name: str) -> np.ndarray:
    arr = np.asarray(array).squeeze()
    if arr.ndim != 2:
        raise ValueError(f"expected 2D {name} in {path}, got {arr.shape}")
    if arr.shape[1] == 3:
        return arr
    if arr.shape[0] == 3:
        return arr.T
    raise ValueError(f"expected one {name} axis of length 3 in {path}, got {arr.shape}")


def _codes_at(events: EventTrials, trial0: int) -> tuple[int, int, int] | None:
    if trial0 < 0 or trial0 >= len(events.codes):
        return None
    row = events.codes[trial0]
    return (_to_int(row[0]), _to_int(row[1]), _to_int(row[2]))


def _times_at(events: EventTrials, trial0: int) -> tuple[float, float, float] | None:
    if trial0 < 0 or trial0 >= len(events.times):
        return None
    row = events.times[trial0]
    return (_to_float(row[0]), _to_float(row[1]), _to_float(row[2]))


def _decode_matlab_string(value: Any) -> str:
    if value is None:
        return ""
    arr = np.asarray(value)
    if arr.size == 0:
        return ""
    if arr.dtype.kind in {"U", "S"}:
        return "".join(str(item) for item in arr.reshape(-1)).strip()
    if np.issubdtype(arr.dtype, np.integer):
        chars = [chr(_to_int(item)) for item in arr.reshape(-1) if _to_int(item) != 0]
        return "".join(chars).strip()
    return str(value).strip()


def _scalar_to_string(value: Any) -> str:
    arr = np.asarray(value)
    if arr.size == 0:
        return ""
    if arr.size == 1:
        item = arr.reshape(-1)[0]
        if isinstance(item, np.generic):
            item = item.item()
        return str(item)
    return _decode_matlab_string(arr)


def _csv_value(value: Any) -> str | int | float | bool:
    if value is None:
        return ""
    if isinstance(value, float):
        if not np.isfinite(value):
            return ""
        return f"{value:.9g}"
    if isinstance(value, np.generic):
        return _csv_value(value.item())
    return value  # type: ignore[return-value]
