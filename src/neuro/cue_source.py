"""Authenticated compact cue-source reader, historical policy, fresh native-precision bins.

Only this dataset's explicit schema is supported. Raw records are not eligibility;
ordinal cross-stream joins and provisional marker meanings remain assumptions.
"""

from __future__ import annotations

import copy
import json
import math
import re
import zipfile
from collections import Counter
from pathlib import Path

import numpy as np

from neuro.cue_source_export import SCHEMA, regular
from neuro.place195 import _index, _rows, file_hash, select_tables
from neuro.source_data import Source, SourceData, Split, Target, TargetDefinition, Unit


def authenticate(config):
    base = Path(config.get("manifest_directory", "."))
    root = (base / config["data_root"]).resolve()
    manifest_path = regular(root, "manifest.json")
    if file_hash(manifest_path) != config["dataset_manifest_sha256"]:
        raise ValueError("compact manifest authentication failed")
    manifest = json.loads(manifest_path.read_text())
    if manifest["schema"] != SCHEMA:
        raise ValueError("unsupported compact schema")
    expected = {"spikes.npz", "outer_splits.csv.gz", "inner_splits.csv.gz"} | {
        s["file"] for s in manifest["sessions"]
    }
    if (
        set(manifest["files"]) != expected
        or len(manifest["sessions"]) != 58
        or len(manifest["units"]) != 195
    ):
        raise ValueError("compact inventory mismatch")
    for name, entry in manifest["files"].items():
        path = regular(root, name)
        if path.stat().st_size != entry["bytes"] or file_hash(path) != entry["sha256"]:
            raise ValueError("compact file hash/size mismatch")
    return root, manifest


def validate_npz(path):
    # Bound decompression before trusting any numpy header; allow_pickle=False always.
    with zipfile.ZipFile(path) as archive:
        infos = archive.infolist()
        if (
            len({i.filename for i in infos}) != len(infos)
            or sum(i.file_size for i in infos) > 512 * 1024**2
        ):
            raise ValueError("duplicate/oversized NPZ payload")
        for info in infos:
            if not re.fullmatch(r"[A-Za-z0-9_]+\.npy", info.filename):
                raise ValueError("invalid NPZ member name")
            with archive.open(info) as member:
                version = np.lib.format.read_magic(member)
                if version not in ((1, 0), (2, 0)):
                    raise ValueError("unsupported NPY header version")
                reader = (
                    np.lib.format.read_array_header_1_0
                    if version == (1, 0)
                    else np.lib.format.read_array_header_2_0
                )
                shape, _, dtype = reader(member)  # NumPy's 10,000-byte header bound.
                size = math.prod(shape) * dtype.itemsize
                if (
                    dtype.hasobject
                    or dtype.itemsize <= 0
                    or dtype.kind not in "biufcUS"
                    or any(n < 0 for n in shape)
                    or size > 512 * 1024**2
                    or size != info.file_size - member.tell()
                ):
                    raise ValueError(
                        "invalid/oversized NPY shape, dtype or payload size"
                    )


def load_arrays(path):
    validate_npz(path)
    with np.load(path, allow_pickle=False) as handle:
        arrays = {key: handle[key] for key in handle.files}
    if "unity__timing_tokens" in arrays:
        arrays["unity__timing"] = arrays["unity__timing_tokens"].astype(np.float64)
    return arrays


def event_matrix(array, *, event_axis):
    array = np.asarray(array)
    if event_axis not in (0, 1) or array.ndim != 2 or array.shape[event_axis] != 3:
        raise ValueError("explicit three-event axis required")
    return array.T if event_axis == 0 else array.copy()


def eye_observed(arrays, details):
    """Return trial-major observation mask, never mistake native zero for missingness."""
    codes = arrays.get("eye__trial_codes", arrays.get("eye__triggers"))
    shape = event_matrix(codes, event_axis=details["event_axis"]).shape
    observed = np.ones(shape, dtype=bool)
    if "eye__missing_idx" in arrays:
        # HDF5 dimension reversal: native MATLAB N×2 is stored 2×N.
        indices = arrays["eye__missing_idx"]
        if (
            indices.ndim != 2
            or indices.shape[0] != 2
            or not np.equal(indices, np.rint(indices)).all()
        ):
            raise ValueError("unknown one-based Eye missing_idx schema")
        for trial, event in indices.T.astype(int):
            if not (1 <= trial <= shape[0] and 1 <= event <= 3):
                raise ValueError("Eye missing_idx out of bounds")
            observed[trial - 1, event - 1] = False
    return observed


def unity_trials(timing):
    if timing.ndim != 2 or timing.shape[1] != 2 or not np.isfinite(timing).all():
        raise ValueError("invalid Unity timing")
    markers, times = np.rint(timing[:, 0]).astype(int), np.cumsum(timing[:, 1])
    event_rows = [
        int(i) for i in np.flatnonzero(markers) if markers[i] // 10 in (1, 2, 3, 4)
    ]
    parsed, orphan = [], []
    i = 0
    while i < len(event_rows):
        rows = event_rows[i : i + 3]
        codes = markers[rows]
        if (
            len(rows) == 3
            and tuple(codes // 10)[:2] == (1, 2)
            and codes[2] // 10 in (3, 4)
            and len(set(codes % 10)) == 1
        ):
            parsed.append(rows)
            i += 3
        else:
            orphan.append(event_rows[i])
            i += 1
    rows = np.asarray(parsed, dtype=int).reshape(-1, 3)
    return markers[rows], times[rows], rows, orphan


def trial_rows(session, arrays):
    sid = session["session_id"]
    rc = event_matrix(
        arrays["ripple__markers"], event_axis=session["ripple"]["event_axis"]
    )
    rt = event_matrix(
        arrays["ripple__timeStamps"], event_axis=session["ripple"]["event_axis"]
    )
    ec = event_matrix(
        arrays.get("eye__trial_codes", arrays.get("eye__triggers")),
        event_axis=session["eye"]["event_axis"],
    )
    et = event_matrix(
        arrays.get("eye__trial_timestamps", arrays.get("eye__timestamps")),
        event_axis=session["eye"]["event_axis"],
    )
    if rc.shape != rt.shape or ec.shape != et.shape:
        raise ValueError("event code/time shape mismatch")
    observed = eye_observed(arrays, session["eye"])
    uc, ut, ur, orphan = unity_trials(arrays["unity__timing"])
    # Historical importer heuristic is retained only in the *policy comparison* ledger.
    # Native Eye values/mask stay separate; milliseconds per Julia, never overwritten.
    historical_eye_scale = (
        1000 if len(et) and np.nanmedian(et[:, 1] - et[:, 0]) > 10 else 1
    )
    rows = []
    for i in range(max(len(rc), len(ec), len(uc))):
        flags = []
        codes, times = {}, {}
        for name, c, t in (
            ("ripple", rc, rt),
            ("unity", uc, ut),
            ("eyelink", ec, et / historical_eye_scale),
        ):
            codes[name] = c[i] if i < len(c) else None
            times[name] = t[i] if i < len(t) else None
            if codes[name] is None:
                flags.append("missing_" + name + "_trial")
        for name in ("unity", "eyelink"):
            if (
                codes["ripple"] is not None
                and codes[name] is not None
                and not np.array_equal(codes["ripple"], codes[name])
            ):
                flags.append("ripple_" + name + "_marker_mismatch")
        r, u = times["ripple"], times["unity"]
        if r is not None and u is not None and abs((r[2] - r[1]) - (u[2] - u[1])) > 2:
            flags.append("ripple_unity_nav_duration_discrepancy_gt_2s")
        if r is not None and not 0.5 <= r[1] - r[0] <= 1.5:
            flags.append("ripple_cue_duration_outside_0p5_1p5s")
        for name, t in times.items():
            if t is not None and not t[0] < t[1] < t[2]:
                flags.append(name + "_nonmonotonic_trial_time")
        path_rows = int(ur[i, 2] - ur[i, 1] + 1) if i < len(ur) else 0
        if path_rows <= 0:
            flags.append("no_unity_path_rows")
        label_codes = next((c for c in codes.values() if c is not None), None)
        digit = (
            int(label_codes[0] % 10)
            if label_codes is not None and len(set(label_codes % 10)) == 1
            else None
        )
        previous_digit = (
            int(rc[i - 1, 0] % 10)
            if 0 < i <= len(rc) and len(set(rc[i - 1] % 10)) == 1
            else None
        )
        outcome = (
            {3: "success", 4: "timeout"}.get(int(label_codes[2] // 10), "unknown")
            if label_codes is not None
            else "unknown"
        )
        row = {
            "source_trial_id": f"{sid}_trial{i + 1:03d}",
            "session_id": sid,
            "trial_index": str(i + 1),
            "previous_source_trial_id": f"{sid}_trial{i:03d}" if i else "",
            "marker_minor_digit": str(digit) if digit is not None else "",
            "outcome": outcome,
            "inferred_start_id_from_previous_marker": f"marker_{previous_digit}"
            if previous_digit is not None
            else "",
            "inferred_goal_id": f"marker_{digit}" if digit is not None else "",
            "ripple_cue_duration_s": str(float(r[1] - r[0])) if r is not None else "",
            "ripple_start_s": float(r[0]) if r is not None else None,
            "ripple_end_s": float(r[1]) if r is not None else None,
            "qc_flags": ";".join(flags),
            "unity_path_rows_inclusive": path_rows,
            "eye_observed": observed[i].tolist() if i < len(observed) else [False] * 3,
        }
        for name, c in codes.items():
            row[name + "_codes"] = (
                " ".join(str(int(v)) for v in c) if c is not None else ""
            )
        rows.append(row)
    return rows, {
        "unity_rows": len(arrays["unity__timing"]),
        "unity_orphan_trial_markers": len(orphan),
        "eye_missing_events": int((~observed).sum()),
        "eye_native_time_unit": "ms",
        "historical_eye_scale": historical_eye_scale,
    }


def inspect_compact(config):
    config = copy.deepcopy(config)
    root, manifest = authenticate(config)
    trials, session_audits = [], []
    for session in manifest["sessions"]:
        rows, audit = trial_rows(session, load_arrays(root / session["file"]))
        trials.extend(rows)
        session_audits.append(audit)
    paths = {name: root / name for name in manifest["files"]}
    selection = select_tables(
        config,
        paths=paths,
        outer=_index(_rows(root / "outer_splits.csv.gz"), "source_trial_id"),
        trials_all=_index(trials, "source_trial_id"),
        units_by_id=_index(manifest["units"], "cell_id"),
        frozen=_index(_rows(root / "inner_splits.csv.gz"), "source_trial_id"),
    )
    masked_selected = [
        s["source_id"]
        for s in selection.selected
        if not all(selection.trials[s["source_id"]]["eye_observed"])
        or not all(selection.trials[s["previous_id"]]["eye_observed"])
    ]
    if masked_selected:
        raise ValueError(
            "historically selected panel contains native Eye missingness; reconcile before use"
        )
    selection.audit.update(
        {
            "access": "authenticated compact source files; metadata only; no spike array interpretation",
            "exported_trials": len(trials),
            "exported_units": len(manifest["units"]),
            "native_eye_missing_events": sum(
                a["eye_missing_events"] for a in session_audits
            ),
            "unity_timing_rows": sum(a["unity_rows"] for a in session_audits),
            "unity_orphan_trial_markers": sum(
                a["unity_orphan_trial_markers"] for a in session_audits
            ),
            "native_missing_selected_contributors": len(masked_selected),
            "metadata_policy": "historical QC ledger regenerated with native precision; masked Eye values are not measurements",
            "all_record_outcomes": dict(Counter(t["outcome"] for t in trials)),
        }
    )
    return selection


def exact_bins(timestamps_ms, start_s, end_s, edges):
    """Native precision, absolute half-open boundaries; repeated spikes count repeatedly.

    No legacy neural_inputs epsilon. Comparing on the absolute Ripple second clock
    avoids subtraction introducing a different rounding at every trial boundary.
    """
    native = np.asarray(timestamps_ms)
    if native.dtype.kind not in "iuf":
        raise ValueError("real numeric spike timestamps required")
    times = native.reshape(-1).astype(np.float64) / 1000
    if (
        not np.isfinite(times).all()
        or not np.isfinite([start_s, end_s]).all()
        or end_s < start_s + edges[-1]
    ):
        raise ValueError("invalid spike/window/full exposure")
    in_cue = times[(times >= start_s) & (times < end_s)]
    absolute_edges = start_s + edges
    indices = np.searchsorted(absolute_edges, in_cue, side="right") - 1
    in_window = (indices >= 0) & (indices < len(edges) - 1)
    counts = np.bincount(indices[in_window], minlength=len(edges) - 1)
    tail = int((~in_window).sum())
    if counts.sum() + tail != len(in_cue):
        raise ValueError("spike conservation failed")
    return counts, tail, len(in_cue)


def reconstruct_compact(selection, *, interpret_neural=False):
    if not interpret_neural:
        raise PermissionError("compact neural interpretation requires authorization")
    selection.validate_manifest()
    canonical = inspect_compact(selection.manifest)
    if canonical != selection:
        raise ValueError("compact metadata selection changed or was forged")
    root, manifest = authenticate(canonical.manifest)
    sources, units = canonical.selected, canonical.units
    edges = np.arange(11, dtype=float) / 10
    if (
        canonical.manifest["bin_width_s"] != 0.1
        or canonical.manifest["nominal_s"] != 1.0
    ):
        raise ValueError("compact cue geometry must match frozen ten-bin protocol")
    values = np.full((len(sources), len(units), 10), np.nan, dtype=np.float32)
    observed = np.zeros(values.shape[:2], dtype=bool)
    tail = accepted = 0
    # Load only selected unit members: other units' compressed numeric arrays remain uninterpreted.
    validate_npz(root / "spikes.npz")
    with np.load(root / "spikes.npz", allow_pickle=False) as archive:
        for ui, unit in enumerate(units):
            timestamps = archive[unit["key"] + "__timestamps"]
            for si, source in enumerate(sources):
                if source["block_id"] != unit["session_id"]:
                    continue
                trial = canonical.trials[source["source_id"]]
                count, omitted, full = exact_bins(
                    timestamps, trial["ripple_start_s"], trial["ripple_end_s"], edges
                )
                values[si, ui], observed[si, ui] = count, True
                tail += omitted
                accepted += full
    authenticate(canonical.manifest)
    data = SourceData(
        values,
        observed,
        np.full((len(sources), 10), 0.1),
        tuple(
            Source(
                s["source_id"],
                s["block_id"],
                s["split_id"],
                s["trial_order"],
                s["source_id"],
                "native-precision compact outer-train source",
                (s["previous_id"],),
                "historical provisional predecessor marker",
            )
            for s in sources
        ),
        tuple(
            Unit(
                u["cell_id"],
                u["session_id"],
                u["selection_provenance"],
                "unknown",
                "inherited; unverified",
            )
            for u in units
        ),
        tuple(Target(s["source_id"], s["condition"], s["condition"]) for s in sources),
        (
            Split("train", "train", "historically exposed; contributor embargo"),
            Split(
                "development", "evaluation", "historically exposed; restricted panel"
            ),
        ),
        TargetDefinition(
            "ordered endpoint pair",
            "compact-native-marker-v1",
            "previous/current marker digits; provisional",
            ("previous_marker_minor_digit", "marker_minor_digit"),
            "derived",
            tuple(
                (f"{a}->{b}", f"{a}->{b}")
                for a in range(1, 7)
                for b in range(1, 7)
                if a != b
            ),
        ),
        edges,
        "s",
        "count",
        "native Ripple cue start",
        "spikes ms / 1000; Ripple seconds; full precision",
        "contributors-disjoint",
        "global frozen development contributor embargo; serial/session dependence remains",
    )
    return data, {
        "events_accepted": accepted,
        "tail_spikes": tail,
        "observed_values": int(observed.sum()) * 10,
        "unavailable_values": int((~observed).sum()) * 10,
        "full_exposure": True,
        "boundary_policy": "absolute Ripple-second [start+edge,start+next_edge); no legacy epsilon; duplicate spikes retained",
        "access": "only selected outer-train panel source/unit values binned; hashes traverse all files; no historical neural/results input",
    }
