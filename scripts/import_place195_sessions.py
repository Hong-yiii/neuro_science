#!/usr/bin/env python3
"""Import/QC smoke for the local place195 lab-server snapshot.

This is a data-feasibility importer, not a model. It preserves raw marker codes,
uses only native Unity paths, and labels task fields inferred until lab protocol
confirmation exists.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import platform
import subprocess
from collections import defaultdict
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import h5py  # type: ignore[reportMissingImports]
import numpy as np
from scipy.io import loadmat

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT_ROOT = ROOT / "data/raw/lab_server/cortex_picasso_misc_place195_20260830"
DEFAULT_SELECTION_LIST = (
    ROOT
    / "data/raw/lab_exports/place_spatial_bins_f1526be5/place_selective_cells_new.txt"
)
DEFAULT_OUTPUT_PARENT = ROOT / "outputs/prospective_path_first_run"
SCIENTIFIC_STATUS = "data_feasibility_audit_not_scientific_evidence"
TASK_LABEL_STATUS = "inferred_from_marker_minor_digit_unverified"
SELECTION_PROVENANCE = "place_selective_195_snapshot"
SIMULTANEITY_STATUS = "candidate_same_session_unverified"
CLOCK_DISCREPANCY_THRESHOLD_SECONDS = 2.0
CUE_DURATION_RANGE_SECONDS = (0.5, 1.5)


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


class CsvWriter:
    def __init__(self, path: Path, fieldnames: Sequence[str]) -> None:
        self.path = path
        self.fieldnames = list(fieldnames)
        if path.suffix == ".gz":
            self.handle = gzip.open(path, "wt", newline="", encoding="utf-8")  # noqa: SIM115
        else:
            self.handle = path.open("w", newline="", encoding="utf-8")  # noqa: SIM115
        self.writer = csv.DictWriter(self.handle, fieldnames=self.fieldnames)
        self.writer.writeheader()

    def writerow(self, row: Mapping[str, Any]) -> None:
        self.writer.writerow(
            {key: _csv_value(row.get(key, "")) for key in self.fieldnames}
        )

    def close(self) -> None:
        self.handle.close()


class OutputBundle:
    def __init__(self, output_dir: Path) -> None:
        output_dir.mkdir(parents=True, exist_ok=False)
        self.output_dir = output_dir
        self.source_files = CsvWriter(
            output_dir / "source_files.csv",
            (
                "role",
                "session_id",
                "cell_id",
                "path",
                "bytes",
                "sha256",
            ),
        )
        self.sessions = CsvWriter(
            output_dir / "sessions.csv",
            (
                "session_id",
                "date",
                "session_path",
                "n_units",
                "ripple_trials",
                "unity_trials",
                "eyelink_trials",
                "success_trials",
                "timeout_trials",
                "marker_match_ripple_unity_trials",
                "marker_match_ripple_eyelink_trials",
                "clock_discrepancy_trials",
                "cue_duration_outlier_trials",
                "unity_bad_event_count",
                "nav_path_samples_inclusive",
                "cue_spikes_total",
                "qc_flags",
            ),
        )
        self.units = CsvWriter(
            output_dir / "units.csv",
            (
                "session_id",
                "cell_id",
                "array_id",
                "channel_id",
                "unit_id",
                "spiketrain_path",
                "mat_format",
                "reference",
                "components",
                "selection_provenance",
                "simultaneity_status",
                "n_spikes_total",
                "first_spike_s",
                "last_spike_s",
                "timestamps_sorted",
                "cue_spikes_total",
                "cue_trials_with_spikes",
            ),
        )
        self.trials = CsvWriter(
            output_dir / "trials.csv",
            (
                "session_id",
                "source_trial_id",
                "trial_index",
                "previous_source_trial_id",
                "ripple_codes",
                "unity_codes",
                "eyelink_codes",
                "marker_minor_digit",
                "inferred_cue_id",
                "inferred_goal_id",
                "inferred_start_id_from_previous_marker",
                "task_label_status",
                "outcome",
                "ripple_cue_duration_s",
                "unity_cue_duration_s",
                "eyelink_cue_duration_s",
                "ripple_nav_duration_s",
                "unity_nav_duration_s",
                "eyelink_nav_duration_s",
                "ripple_unity_nav_duration_abs_diff_s",
                "unity_path_rows_inclusive",
                "unity_path_rows_exclusive",
                "unity_path_distance_axis_units",
                "unity_start_axis1",
                "unity_start_axis2",
                "unity_end_axis1",
                "unity_end_axis2",
                "qc_flags",
            ),
        )
        self.cue_counts = CsvWriter(
            output_dir / "cue_counts.csv.gz",
            (
                "session_id",
                "source_trial_id",
                "trial_index",
                "cell_id",
                "cue_spike_count",
                "cue_window_start_ripple_s",
                "cue_window_end_ripple_s",
            ),
        )
        self.cue_events = CsvWriter(
            output_dir / "cue_spike_events.csv.gz",
            (
                "session_id",
                "source_trial_id",
                "trial_index",
                "cell_id",
                "cue_relative_time_s",
                "spike_time_ripple_s",
            ),
        )
        self.path_samples = CsvWriter(
            output_dir / "path_samples.csv.gz",
            (
                "session_id",
                "source_trial_id",
                "trial_index",
                "navigation_sample",
                "unity_raw_row",
                "unity_time_since_nav_onset_s",
                "unity_time_s",
                "position_axis1",
                "position_axis2",
                "heading",
                "unity_event_marker",
            ),
        )

    def close(self) -> None:
        for writer in (
            self.source_files,
            self.sessions,
            self.units,
            self.trials,
            self.cue_counts,
            self.cue_events,
            self.path_samples,
        ):
            writer.close()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


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


def read_eyelink_trials(path: Path) -> EventTrials:
    with h5py.File(path, "r") as handle:
        if "el/data" in handle and all(
            name in handle["el/data"] for name in ("trial_codes", "trial_timestamps")
        ):
            group = handle["el/data"]
            codes = _event_matrix(
                np.asarray(group["trial_codes"]), path, "eyelink trial_codes"
            )
            timestamps = _event_matrix(
                np.asarray(group["trial_timestamps"]), path, "eyelink trial_timestamps"
            )
        elif all(name in handle for name in ("triggers", "timestamps")):
            codes = _event_matrix(
                np.asarray(handle["triggers"]), path, "eyelink triggers"
            )
            timestamps = _event_matrix(
                np.asarray(handle["timestamps"]), path, "eyelink timestamps"
            )
        else:
            group = _find_hdf5_group_with(
                handle,
                ("trial_codes", "trial_timestamps"),
                ("el/data",),
            )
            codes = _event_matrix(
                np.asarray(group["trial_codes"]), path, "eyelink trial_codes"
            )
            timestamps = _event_matrix(
                np.asarray(group["trial_timestamps"]), path, "eyelink trial_timestamps"
            )
    return EventTrials(
        codes=np.rint(codes).astype(int), times=_eyelink_times_seconds(timestamps)
    )


def _eyelink_times_seconds(timestamps: np.ndarray) -> np.ndarray:
    times = timestamps.astype(float)
    if len(times) == 0:
        return times
    cue_durations = times[:, 1] - times[:, 0]
    median_cue_duration = np.nanmedian(cue_durations)
    # ponytail: unit heuristic only for QC; lab protocol confirmation still required.
    if median_cue_duration > 10.0:
        return times / 1000.0
    return times


def read_unity_trials(path: Path) -> tuple[EventTrials, np.ndarray, dict[str, str]]:
    first_numeric_line, header = _find_first_numeric_line(path)
    raw = np.loadtxt(path, skiprows=first_numeric_line)
    if raw.ndim == 1:
        raw = raw.reshape(1, -1)
    if raw.shape[1] != 5:
        raise ValueError(f"expected 5 Unity columns in {path}, got {raw.shape[1]}")

    markers = np.rint(raw[:, 0]).astype(int)
    times = np.cumsum(raw[:, 1].astype(float))
    event_rows = [
        row.item()
        for row in np.flatnonzero(markers != 0)
        if markers[row].item() // 10 in (1, 2, 3, 4)
    ]
    parsed: list[tuple[int, int, int]] = []
    bad = 0
    i = 0
    while i < len(event_rows):
        if i + 2 >= len(event_rows):
            bad += len(event_rows) - i
            break
        a, b, c = event_rows[i : i + 3]
        triplet = tuple(markers[[a, b, c]].tolist())
        if _is_trial_triplet(triplet):
            parsed.append((a, b, c))
            i += 3
        else:
            bad += 1
            i += 1

    rows = np.asarray(parsed, dtype=int)
    if rows.size == 0:
        codes = np.empty((0, 3), dtype=int)
        trial_times = np.empty((0, 3), dtype=float)
    else:
        codes = markers[rows]
        trial_times = times[rows]
    return (
        EventTrials(
            codes=codes,
            times=trial_times,
            rows=rows,
            bad_event_count=bad,
            first_numeric_line=first_numeric_line,
        ),
        raw,
        header,
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


def discover_sessions(input_root: Path) -> list[Path]:
    return sorted(
        path / "session01"
        for path in input_root.iterdir()
        if (path / "session01").is_dir()
    )


def import_all_sessions(
    input_root: Path,
    output_dir: Path,
    expected_sessions: int,
    expected_units: int,
    selection_list: Path,
) -> dict[str, Any]:
    if not input_root.exists():
        raise FileNotFoundError(f"input root does not exist: {input_root}")
    validate_output_dir(output_dir, input_root)

    session_dirs = discover_sessions(input_root)
    spiketrain_paths = sorted(
        input_root.glob("*/session01/array*/channel*/cell*/spiketrain.mat")
    )
    ripple_paths = sorted(input_root.glob("*/session01/rplparallel.mat"))
    eyelink_paths = sorted(input_root.glob("*/session01/eyelink.mat"))
    raw_paths = sorted(input_root.glob("*/session01/RawData_T1-400/session_*.txt"))
    raytrace_paths = sorted(input_root.glob("*/session01/unity_raytrace.jld2"))

    selection_keys = read_selection_keys(selection_list)
    spiketrain_keys = {
        "/".join(path.relative_to(input_root).parts[:-1]) for path in spiketrain_paths
    }
    missing_from_snapshot = sorted(selection_keys - spiketrain_keys)
    extra_in_snapshot = sorted(spiketrain_keys - selection_keys)
    preflight = {
        "sessions": len(session_dirs),
        "spiketrain_mat": len(spiketrain_paths),
        "rplparallel_mat": len(ripple_paths),
        "eyelink_mat": len(eyelink_paths),
        "unity_raw_txt": len(raw_paths),
        "unity_raytrace_jld2": len(raytrace_paths),
        "selection_list_cells": len(selection_keys),
        "selection_list_matches": len(selection_keys & spiketrain_keys),
        "selection_missing_from_snapshot": len(missing_from_snapshot),
        "spiketrains_not_in_selection_list": len(extra_in_snapshot),
    }
    if len(session_dirs) != expected_sessions:
        raise ValueError(
            f"expected {expected_sessions} sessions, found {len(session_dirs)}"
        )
    if len(spiketrain_paths) != expected_units:
        raise ValueError(
            f"expected {expected_units} spiketrains, found {len(spiketrain_paths)}"
        )
    if (
        len(ripple_paths) != expected_sessions
        or len(eyelink_paths) != expected_sessions
        or len(raw_paths) != expected_sessions
    ):
        raise ValueError(
            f"expected one Ripple/Eyelink/Unity file per session, found {preflight}"
        )
    if missing_from_snapshot or extra_in_snapshot:
        raise ValueError(
            "spiketrain snapshot does not match selection list: "
            f"missing={len(missing_from_snapshot)} extra={len(extra_in_snapshot)}"
        )

    bundle = OutputBundle(output_dir)
    bundle.source_files.writerow(
        _source_file_row(input_root, "", "", "selection_list", selection_list)
    )
    summary: dict[str, Any] = {
        "created_utc": datetime.now(UTC).isoformat(),
        "scientific_status": SCIENTIFIC_STATUS,
        "input_root": str(input_root),
        "output_dir": str(output_dir),
        "preflight_counts": preflight,
        "selection_list": {
            "path": str(selection_list.relative_to(ROOT)),
            "sha256": sha256_file(selection_list),
            "listed_cells": len(selection_keys),
            "matched_spiketrains": len(selection_keys & spiketrain_keys),
            "missing_from_snapshot": missing_from_snapshot,
            "spiketrains_not_in_selection_list": extra_in_snapshot,
        },
        "decisions": decisions(),
        "sessions": 0,
        "units": 0,
        "trials": 0,
        "success_trials": 0,
        "timeout_trials": 0,
        "marker_mismatch_trials": 0,
        "clock_discrepancy_trials": 0,
        "cue_duration_outlier_trials": 0,
        "cue_spikes_total": 0,
        "cue_trials_with_any_spike": 0,
        "path_samples_rows": 0,
        "spiketrain_formats": defaultdict(int),
        "trial_count_by_session": {},
        "unit_count_by_session": {},
        "qc_flag_counts": defaultdict(int),
        "git": git_state(),
        "python_version": platform.python_version(),
        "package_versions": package_versions(),
    }
    session_errors: list[dict[str, str]] = []

    try:
        for session_dir in session_dirs:
            try:
                session_summary = import_session(input_root, session_dir, bundle)
            except (
                Exception
            ) as exc:  # fail after closing CSVs so partial evidence is visible.
                session_errors.append({"session": str(session_dir), "error": repr(exc)})
                continue
            summary["sessions"] += 1
            for key in (
                "units",
                "trials",
                "success_trials",
                "timeout_trials",
                "marker_mismatch_trials",
                "clock_discrepancy_trials",
                "cue_duration_outlier_trials",
                "cue_spikes_total",
                "cue_trials_with_any_spike",
                "path_samples_rows",
            ):
                summary[key] += session_summary[key]
            for fmt, count in session_summary["spiketrain_formats"].items():
                summary["spiketrain_formats"][fmt] += count
            for flag, count in session_summary["qc_flag_counts"].items():
                summary["qc_flag_counts"][flag] += count
            summary["trial_count_by_session"][session_summary["session_id"]] = (
                session_summary["trials"]
            )
            summary["unit_count_by_session"][session_summary["session_id"]] = (
                session_summary["units"]
            )
    finally:
        bundle.close()

    summary["session_errors"] = session_errors
    summary["spiketrain_formats"] = dict(summary["spiketrain_formats"])
    summary["qc_flag_counts"] = dict(summary["qc_flag_counts"])
    summary["artifact_hashes"] = {
        path.name: sha256_file(path)
        for path in sorted(output_dir.iterdir())
        if path.is_file() and path.name not in {"summary.json", "decisions.md"}
    }
    if session_errors:
        summary["status"] = "failed"
        summary_path = write_json(output_dir / "summary.json", summary)
        write_decisions(output_dir / "decisions.md", summary)
        raise RuntimeError(
            f"failed to import {len(session_errors)} sessions; see {summary_path}"
        )

    summary["status"] = "passed"
    write_json(output_dir / "summary.json", summary)
    write_decisions(output_dir / "decisions.md", summary)
    return summary


def import_session(
    input_root: Path, session_dir: Path, bundle: OutputBundle
) -> dict[str, Any]:
    date = session_dir.parent.name
    session_id = f"{date}_session01"
    ripple_path = session_dir / "rplparallel.mat"
    eyelink_path = session_dir / "eyelink.mat"
    raw_file = _one(
        session_dir.glob("RawData_T1-400/session_*.txt"),
        f"Unity RawData for {session_id}",
    )
    spiketrain_paths = sorted(session_dir.glob("array*/channel*/cell*/spiketrain.mat"))

    for role, path, cell_id in (
        ("ripple_markers", ripple_path, ""),
        ("eyelink_markers", eyelink_path, ""),
        ("unity_raw", raw_file, ""),
    ):
        bundle.source_files.writerow(
            _source_file_row(input_root, session_id, cell_id, role, path)
        )

    ripple = read_ripple_trials(ripple_path)
    eyelink = read_eyelink_trials(eyelink_path)
    unity, unity_raw, _header = read_unity_trials(raw_file)
    unity_time = np.cumsum(unity_raw[:, 1].astype(float))

    units = []
    for spiketrain_path in spiketrain_paths:
        cell = cell_metadata(input_root, spiketrain_path)
        bundle.source_files.writerow(
            _source_file_row(
                input_root, session_id, cell["cell_id"], "spiketrain", spiketrain_path
            )
        )
        spike_train = read_spiketrain(spiketrain_path)
        units.append((cell, spike_train, spiketrain_path))

    max_trials = max(len(ripple.codes), len(unity.codes), len(eyelink.codes))
    session_counts: dict[str, Any] = {
        "session_id": session_id,
        "units": len(units),
        "trials": max_trials,
        "success_trials": 0,
        "timeout_trials": 0,
        "marker_mismatch_trials": 0,
        "clock_discrepancy_trials": 0,
        "cue_duration_outlier_trials": 0,
        "cue_spikes_total": 0,
        "cue_trials_with_any_spike": 0,
        "path_samples_rows": 0,
        "spiketrain_formats": defaultdict(int),
        "qc_flag_counts": defaultdict(int),
    }
    unit_cue_totals: dict[str, int] = defaultdict(int)
    unit_cue_trial_hits: dict[str, int] = defaultdict(int)
    session_qc_flags: set[str] = set()
    marker_match_ru = 0
    marker_match_re = 0
    nav_path_samples = 0

    for trial0 in range(max_trials):
        trial_index = trial0 + 1
        source_trial_id = f"{session_id}_trial{trial_index:03d}"
        previous_source_trial_id = (
            f"{session_id}_trial{trial_index - 1:03d}" if trial_index > 1 else ""
        )
        flags: list[str] = []
        r_codes = _codes_at(ripple, trial0)
        u_codes = _codes_at(unity, trial0)
        e_codes = _codes_at(eyelink, trial0)
        r_times = _times_at(ripple, trial0)
        u_times = _times_at(unity, trial0)
        e_times = _times_at(eyelink, trial0)

        if r_codes is None:
            flags.append("missing_ripple_trial")
        if u_codes is None:
            flags.append("missing_unity_trial")
        if e_codes is None:
            flags.append("missing_eyelink_trial")
        if (
            r_codes is not None
            and u_codes is not None
            and tuple(r_codes) == tuple(u_codes)
        ):
            marker_match_ru += 1
        elif r_codes is not None and u_codes is not None:
            flags.append("ripple_unity_marker_mismatch")
        if (
            r_codes is not None
            and e_codes is not None
            and tuple(r_codes) == tuple(e_codes)
        ):
            marker_match_re += 1
        elif r_codes is not None and e_codes is not None:
            flags.append("ripple_eyelink_marker_mismatch")

        codes_for_labels = r_codes or u_codes or e_codes
        minor = _minor_digit(codes_for_labels)
        previous_minor = _minor_digit(
            _codes_at(ripple, trial0 - 1) if trial0 > 0 else None
        )
        outcome = _outcome(codes_for_labels)
        if outcome == "success":
            session_counts["success_trials"] += 1
        elif outcome == "timeout":
            session_counts["timeout_trials"] += 1

        r_cue = _duration(r_times, 0, 1)
        u_cue = _duration(u_times, 0, 1)
        e_cue = _duration(e_times, 0, 1)
        r_nav = _duration(r_times, 1, 2)
        u_nav = _duration(u_times, 1, 2)
        e_nav = _duration(e_times, 1, 2)
        nav_diff = _abs_diff(r_nav, u_nav)
        if nav_diff is not None and nav_diff > CLOCK_DISCREPANCY_THRESHOLD_SECONDS:
            flags.append("ripple_unity_nav_duration_discrepancy_gt_2s")
            session_counts["clock_discrepancy_trials"] += 1
        if r_cue is not None and not (
            CUE_DURATION_RANGE_SECONDS[0] <= r_cue <= CUE_DURATION_RANGE_SECONDS[1]
        ):
            flags.append("ripple_cue_duration_outside_0p5_1p5s")
            session_counts["cue_duration_outlier_trials"] += 1
        if r_times is not None and not (r_times[0] < r_times[1] < r_times[2]):
            flags.append("ripple_nonmonotonic_trial_time")
        if u_times is not None and not (u_times[0] < u_times[1] < u_times[2]):
            flags.append("unity_nonmonotonic_trial_time")
        if e_times is not None and not (e_times[0] < e_times[1] < e_times[2]):
            flags.append("eyelink_nonmonotonic_trial_time")

        path_summary = unity_path_summary(unity, unity_raw, unity_time, trial0)
        nav_path_samples += path_summary["path_rows_inclusive"]
        session_counts["path_samples_rows"] += path_summary["path_rows_inclusive"]
        if path_summary["path_rows_inclusive"] == 0:
            flags.append("no_unity_path_rows")
        else:
            write_path_samples(
                bundle,
                session_id,
                source_trial_id,
                trial_index,
                unity,
                unity_raw,
                unity_time,
                trial0,
            )

        if flags:
            session_counts["marker_mismatch_trials"] += _to_int(
                any("marker_mismatch" in flag for flag in flags)
            )
        for flag in flags:
            session_counts["qc_flag_counts"][flag] += 1

        trial_cue_spikes = 0
        if r_times is not None:
            for cell, spike_train, _path in units:
                cue_spikes = spikes_in_window(
                    spike_train.timestamps_seconds, r_times[0], r_times[1]
                )
                count = _to_int(cue_spikes.size)
                trial_cue_spikes += count
                unit_cue_totals[cell["cell_id"]] += count
                unit_cue_trial_hits[cell["cell_id"]] += _to_int(count > 0)
                bundle.cue_counts.writerow(
                    {
                        "session_id": session_id,
                        "source_trial_id": source_trial_id,
                        "trial_index": trial_index,
                        "cell_id": cell["cell_id"],
                        "cue_spike_count": count,
                        "cue_window_start_ripple_s": r_times[0],
                        "cue_window_end_ripple_s": r_times[1],
                    }
                )
                for spike_time in cue_spikes:
                    spike_time_s = _to_float(spike_time)
                    bundle.cue_events.writerow(
                        {
                            "session_id": session_id,
                            "source_trial_id": source_trial_id,
                            "trial_index": trial_index,
                            "cell_id": cell["cell_id"],
                            "cue_relative_time_s": spike_time_s - r_times[0],
                            "spike_time_ripple_s": spike_time_s,
                        }
                    )
        session_counts["cue_spikes_total"] += trial_cue_spikes
        session_counts["cue_trials_with_any_spike"] += _to_int(trial_cue_spikes > 0)
        for flag in flags:
            session_qc_flags.add(flag)

        bundle.trials.writerow(
            {
                "session_id": session_id,
                "source_trial_id": source_trial_id,
                "trial_index": trial_index,
                "previous_source_trial_id": previous_source_trial_id,
                "ripple_codes": _triplet_text(r_codes),
                "unity_codes": _triplet_text(u_codes),
                "eyelink_codes": _triplet_text(e_codes),
                "marker_minor_digit": minor if minor is not None else "",
                "inferred_cue_id": f"marker_{minor}" if minor is not None else "",
                "inferred_goal_id": f"marker_{minor}" if minor is not None else "",
                "inferred_start_id_from_previous_marker": f"marker_{previous_minor}"
                if previous_minor is not None
                else "",
                "task_label_status": TASK_LABEL_STATUS,
                "outcome": outcome,
                "ripple_cue_duration_s": r_cue,
                "unity_cue_duration_s": u_cue,
                "eyelink_cue_duration_s": e_cue,
                "ripple_nav_duration_s": r_nav,
                "unity_nav_duration_s": u_nav,
                "eyelink_nav_duration_s": e_nav,
                "ripple_unity_nav_duration_abs_diff_s": nav_diff,
                "unity_path_rows_inclusive": path_summary["path_rows_inclusive"],
                "unity_path_rows_exclusive": path_summary["path_rows_exclusive"],
                "unity_path_distance_axis_units": path_summary["path_distance"],
                "unity_start_axis1": path_summary["start_axis1"],
                "unity_start_axis2": path_summary["start_axis2"],
                "unity_end_axis1": path_summary["end_axis1"],
                "unity_end_axis2": path_summary["end_axis2"],
                "qc_flags": ";".join(flags),
            }
        )

    if unity.bad_event_count:
        session_qc_flags.add("unity_bad_event_count_nonzero")
        session_counts["qc_flag_counts"]["unity_bad_event_count_nonzero"] += 1
    if len(ripple.codes) != len(unity.codes):
        session_qc_flags.add("ripple_unity_trial_count_mismatch")
    if len(ripple.codes) != len(eyelink.codes):
        session_qc_flags.add("ripple_eyelink_trial_count_mismatch")

    for cell, spike_train, spiketrain_path in units:
        session_counts["spiketrain_formats"][spike_train.mat_format] += 1
        timestamps = spike_train.timestamps_seconds
        bundle.units.writerow(
            {
                "session_id": session_id,
                "cell_id": cell["cell_id"],
                "array_id": cell["array_id"],
                "channel_id": cell["channel_id"],
                "unit_id": cell["unit_id"],
                "spiketrain_path": str(spiketrain_path.relative_to(ROOT)),
                "mat_format": spike_train.mat_format,
                "reference": spike_train.reference,
                "components": spike_train.components,
                "selection_provenance": SELECTION_PROVENANCE,
                "simultaneity_status": SIMULTANEITY_STATUS,
                "n_spikes_total": _to_int(timestamps.size),
                "first_spike_s": _to_float(timestamps[0]) if timestamps.size else "",
                "last_spike_s": _to_float(timestamps[-1]) if timestamps.size else "",
                "timestamps_sorted": spike_train.sorted_input,
                "cue_spikes_total": unit_cue_totals[cell["cell_id"]],
                "cue_trials_with_spikes": unit_cue_trial_hits[cell["cell_id"]],
            }
        )

    bundle.sessions.writerow(
        {
            "session_id": session_id,
            "date": date,
            "session_path": str(session_dir.relative_to(ROOT)),
            "n_units": len(units),
            "ripple_trials": len(ripple.codes),
            "unity_trials": len(unity.codes),
            "eyelink_trials": len(eyelink.codes),
            "success_trials": session_counts["success_trials"],
            "timeout_trials": session_counts["timeout_trials"],
            "marker_match_ripple_unity_trials": marker_match_ru,
            "marker_match_ripple_eyelink_trials": marker_match_re,
            "clock_discrepancy_trials": session_counts["clock_discrepancy_trials"],
            "cue_duration_outlier_trials": session_counts[
                "cue_duration_outlier_trials"
            ],
            "unity_bad_event_count": unity.bad_event_count,
            "nav_path_samples_inclusive": nav_path_samples,
            "cue_spikes_total": session_counts["cue_spikes_total"],
            "qc_flags": ";".join(sorted(session_qc_flags)),
        }
    )
    return session_counts


def write_path_samples(
    bundle: OutputBundle,
    session_id: str,
    source_trial_id: str,
    trial_index: int,
    unity: EventTrials,
    unity_raw: np.ndarray,
    unity_time: np.ndarray,
    trial0: int,
) -> None:
    if unity.rows is None or trial0 >= len(unity.rows):
        return
    start_row = _to_int(unity.rows[trial0, 1])
    end_row = _to_int(unity.rows[trial0, 2])
    nav_start = _to_float(unity_time[start_row])
    for sample_idx, row in enumerate(range(start_row, end_row + 1)):
        bundle.path_samples.writerow(
            {
                "session_id": session_id,
                "source_trial_id": source_trial_id,
                "trial_index": trial_index,
                "navigation_sample": sample_idx,
                "unity_raw_row": row,
                "unity_time_since_nav_onset_s": _to_float(unity_time[row] - nav_start),
                "unity_time_s": _to_float(unity_time[row]),
                "position_axis1": _to_float(unity_raw[row, 2]),
                "position_axis2": _to_float(unity_raw[row, 3]),
                "heading": _to_float(unity_raw[row, 4]),
                "unity_event_marker": _to_int(round(unity_raw[row, 0])),
            }
        )


def unity_path_summary(
    unity: EventTrials, unity_raw: np.ndarray, unity_time: np.ndarray, trial0: int
) -> dict[str, Any]:
    if unity.rows is None or trial0 >= len(unity.rows):
        return {
            "path_rows_inclusive": 0,
            "path_rows_exclusive": 0,
            "path_distance": "",
            "start_axis1": "",
            "start_axis2": "",
            "end_axis1": "",
            "end_axis2": "",
        }
    start_row = _to_int(unity.rows[trial0, 1])
    end_row = _to_int(unity.rows[trial0, 2])
    if end_row < start_row:
        return {
            "path_rows_inclusive": 0,
            "path_rows_exclusive": 0,
            "path_distance": "",
            "start_axis1": "",
            "start_axis2": "",
            "end_axis1": "",
            "end_axis2": "",
        }
    positions = unity_raw[start_row : end_row + 1, 2:4].astype(float)
    if len(positions) > 1:
        distance = _to_float(np.linalg.norm(np.diff(positions, axis=0), axis=1).sum())
    else:
        distance = 0.0
    return {
        "path_rows_inclusive": _to_int(end_row - start_row + 1),
        "path_rows_exclusive": _to_int(max(end_row - start_row - 1, 0)),
        "path_distance": distance,
        "start_axis1": _to_float(positions[0, 0]),
        "start_axis2": _to_float(positions[0, 1]),
        "end_axis1": _to_float(positions[-1, 0]),
        "end_axis2": _to_float(positions[-1, 1]),
    }


def spikes_in_window(
    timestamps_seconds: np.ndarray, start: float, end: float
) -> np.ndarray:
    left = _to_int(np.searchsorted(timestamps_seconds, start, side="left"))
    right = _to_int(np.searchsorted(timestamps_seconds, end, side="left"))
    return timestamps_seconds[left:right]


def cell_metadata(input_root: Path, spiketrain_path: Path) -> dict[str, str]:
    rel = spiketrain_path.relative_to(input_root)
    date, session, array_id, channel_id, unit_id, _file = rel.parts
    return {
        "session_id": f"{date}_{session}",
        "cell_id": "/".join((date, session, array_id, channel_id, unit_id)),
        "array_id": array_id,
        "channel_id": channel_id,
        "unit_id": unit_id,
    }


def decisions() -> list[dict[str, str]]:
    return [
        {
            "decision": "scientific_status",
            "value": SCIENTIFIC_STATUS,
            "reason": "place195 is selected-cell importer/QC data, not verified H1-ready simultaneous population data",
        },
        {
            "decision": "input_root",
            "value": str(DEFAULT_INPUT_ROOT.relative_to(ROOT)),
            "reason": "this is the actual 58-session local snapshot; the older six-unit snapshot path is absent in this checkout",
        },
        {
            "decision": "selection_list",
            "value": str(DEFAULT_SELECTION_LIST.relative_to(ROOT)),
            "reason": "attests that the 195 local spiketrains match the professor-provided place-selective list",
        },
        {
            "decision": "cue_window",
            "value": "half-open Ripple-clock [event_1, event_2)",
            "reason": "matches the 20181105 feasibility audit and avoids double-counting event-boundary spikes",
        },
        {
            "decision": "path_source",
            "value": "native Unity RawData rows from event_2 through event_3 inclusive",
            "reason": "raytrace JLD2 is absent from the place195 snapshot; native path is directly available and keeps end-marker row for later rule choice",
        },
        {
            "decision": "task_labels",
            "value": TASK_LABEL_STATUS,
            "reason": "marker minor digit is preserved, but cue/goal/start semantics still require protocol/lab confirmation",
        },
        {
            "decision": "eyelink_time_units",
            "value": "divide by 1000 when median event1-event2 duration is >10 raw units",
            "reason": "place195 Eyelink trial timestamps are millisecond-like while Ripple/Unity are second-like; this affects QC reporting only",
        },
        {
            "decision": "simultaneity",
            "value": SIMULTANEITY_STATUS,
            "reason": "same session and shared Ripple clock are candidate evidence only; no lab-confirmed recording group metadata yet",
        },
        {
            "decision": "clock_discrepancy_qc_flag",
            "value": f"Ripple vs Unity navigation-duration absolute difference > {CLOCK_DISCREPANCY_THRESHOLD_SECONDS:g}s",
            "reason": "flags trial-178-like discontinuities without dropping or repairing raw records",
        },
        {
            "decision": "no_modeling",
            "value": "no splits, graph, PCA, CEBRA, decoder, or route-family labels in this run",
            "reason": "those choices require provenance review and immutable source-trial splits first",
        },
    ]


def write_decisions(path: Path, summary: Mapping[str, Any]) -> None:
    lines = [
        "# Place195 First All-Session Import Decisions",
        "",
        f"Date: {summary['created_utc']}",
        f"Status: **{summary['scientific_status']}**",
        "",
        "This file is generated with the run to make the first-run calls auditable.",
        "",
        "## Decisions",
        "",
    ]
    for row in decisions():
        lines.extend(
            [
                f"### {row['decision']}",
                "",
                f"- Value: `{row['value']}`",
                f"- Reason: {row['reason']}",
                "",
            ]
        )
    lines.extend(
        [
            "## Stop boundary",
            "",
            "This run may support importer and QC work only. It must not be used as H1 evidence until recording groups, task-marker semantics, trial QC, splits, path representation, and baselines are independently reviewed.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def _source_file_row(
    input_root: Path, session_id: str, cell_id: str, role: str, path: Path
) -> dict[str, Any]:
    stat = path.stat()
    return {
        "role": role,
        "session_id": session_id,
        "cell_id": cell_id,
        "path": str(path.relative_to(ROOT)),
        "bytes": stat.st_size,
        "sha256": sha256_file(path),
    }


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


def _find_first_numeric_line(path: Path) -> tuple[int, dict[str, str]]:
    header: dict[str, str] = {}
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for line_number, line in enumerate(handle):
            parts = line.split()
            if len(parts) == 5:
                try:
                    [_to_float(part) for part in parts]
                except ValueError:
                    continue
                else:
                    return line_number, header
            if ":" in line:
                key, value = line.split(":", 1)
                header[key.strip()] = value.strip()
    raise ValueError(f"no numeric Unity rows found in {path}")


def _is_trial_triplet(codes: Sequence[int]) -> bool:
    return (
        len(codes) == 3
        and codes[0] // 10 == 1
        and codes[1] // 10 == 2
        and codes[2] // 10 in (3, 4)
        and codes[0] % 10 == codes[1] % 10 == codes[2] % 10
    )


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


def _duration(
    times: tuple[float, float, float] | None, start: int, end: int
) -> float | None:
    if times is None:
        return None
    return _to_float(times[end] - times[start])


def _abs_diff(left: float | None, right: float | None) -> float | None:
    if left is None or right is None:
        return None
    return abs(_to_float(left - right))


def _minor_digit(codes: Sequence[int] | None) -> int | None:
    if codes is None or len(codes) != 3:
        return None
    minors = {_to_int(code) % 10 for code in codes}
    if len(minors) != 1:
        return None
    return minors.pop()


def _outcome(codes: Sequence[int] | None) -> str:
    if codes is None or len(codes) != 3:
        return "unknown"
    family = _to_int(codes[2]) // 10
    if family == 3:
        return "success"
    if family == 4:
        return "timeout"
    return "unknown"


def _triplet_text(codes: Sequence[int] | None) -> str:
    return "" if codes is None else " ".join(str(_to_int(code)) for code in codes)


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


def _one(items: Iterable[Path], label: str) -> Path:
    found = list(items)
    if len(found) != 1:
        raise ValueError(f"expected one {label}, found {len(found)}")
    return found[0]


def validate_output_dir(output_dir: Path, input_root: Path) -> None:
    output = output_dir.resolve()
    raw_root = (ROOT / "data/raw").resolve()
    input_root = input_root.resolve()
    if output == raw_root or raw_root in output.parents:
        raise ValueError(
            f"output directory must not be inside immutable raw data: {output}"
        )
    if output == input_root or input_root in output.parents:
        raise ValueError(f"output directory must not be inside input root: {output}")
    if not _is_ignored(output):
        raise ValueError(f"output directory must be Git-ignored: {output}")


def read_selection_keys(selection_list: Path) -> set[str]:
    keys = set()
    for line in selection_list.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        parts = Path(line).parts
        for index, part in enumerate(parts):
            if len(part) == 8 and part.isdigit() and index + 4 < len(parts):
                keys.add("/".join(parts[index : index + 5]))
                break
    return keys


def _is_ignored(path: Path) -> bool:
    path = path.resolve()
    root = subprocess.check_output(
        ["git", "rev-parse", "--show-toplevel"], cwd=ROOT, text=True
    ).strip()
    result = subprocess.run(
        ["git", "check-ignore", "-q", str(path)],
        cwd=root,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return result.returncode == 0


def git_state() -> dict[str, Any]:
    revision = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()
    status = subprocess.check_output(["git", "status", "--short"], cwd=ROOT, text=True)
    return {"revision": revision, "dirty": bool(status.strip())}


def package_versions() -> dict[str, str]:
    from importlib import metadata
    from importlib.metadata import PackageNotFoundError

    packages = ("numpy", "h5py", "scipy")
    versions = {}
    for package in packages:
        try:
            versions[package] = metadata.version(package)
        except PackageNotFoundError:
            versions[package] = "not-installed"
    return versions


def write_json(path: Path, payload: Mapping[str, Any]) -> Path:
    path.write_text(
        json.dumps(_jsonable(payload), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return path


def _jsonable(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, tuple | list):
        return [_jsonable(item) for item in value]
    if isinstance(value, defaultdict):
        return dict(value)
    if isinstance(value, np.generic):
        return value.item()
    return value


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-root", type=Path, default=DEFAULT_INPUT_ROOT)
    parser.add_argument("--selection-list", type=Path, default=DEFAULT_SELECTION_LIST)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--expected-sessions", type=int, default=58)
    parser.add_argument("--expected-units", type=int, default=195)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    summary = import_all_sessions(
        args.input_root.resolve(),
        args.output_dir.resolve(),
        args.expected_sessions,
        args.expected_units,
        args.selection_list.resolve(),
    )
    print(json.dumps(_jsonable(summary), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
