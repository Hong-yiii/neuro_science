"""Dataset-specific lossless numeric export. No private default paths or model access."""

from __future__ import annotations

import csv
import gzip
import io
import json
import re
import zipfile
from pathlib import Path

import h5py  # type: ignore[reportMissingImports]
import numpy as np
from scipy.io import loadmat

from neuro.place195 import _rows, file_hash
from neuro.raw_io import _decode_matlab_string

OUTER_SHA = "b0ef8cce43c79d9e2b1ae0a804c7d48fefeb92469670f3031485d0009fb10ff3"
INNER_SHA = "ab158a23c4f3cc9dd46f27710c355fee74965a32892c6e662d2d4a29dd628bf8"
SCHEMA = "cue-source-v1"


def regular(root: Path, relative: str) -> Path:
    """Reject traversal, absolute names and symlink components, including final files."""
    rel = Path(relative)
    if rel.is_absolute() or not rel.parts or any(p in ("..", ".") for p in rel.parts):
        raise ValueError("unsafe relative input name")
    current = root.resolve()
    for part in rel.parts:
        current /= part
        if current.is_symlink():
            raise ValueError("symlink input is not permitted")
    if not current.is_file() or not current.resolve().is_relative_to(root.resolve()):
        raise ValueError("missing/nonregular/outside-root input")
    return current


def numeric(array):
    array = np.asarray(array)
    if array.dtype.kind not in "biufcUS":
        raise ValueError("object/reference arrays are not portable")
    return array


def write_npz(path, arrays):
    # Fixed ZIP metadata and sorted keys make identical array payloads byte-identical.
    with zipfile.ZipFile(
        path, "x", compression=zipfile.ZIP_DEFLATED, compresslevel=6
    ) as z:
        for key, array in sorted(arrays.items()):
            if not re.fullmatch(r"[A-Za-z0-9_]+", key):
                raise ValueError("invalid array key")
            buffer = io.BytesIO()
            np.lib.format.write_array(buffer, numeric(array), allow_pickle=False)
            info = zipfile.ZipInfo(key + ".npy", date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, buffer.getvalue(), compresslevel=6)
    with np.load(path, allow_pickle=False) as saved:
        for key, value in arrays.items():
            actual = saved[key]
            if actual.dtype != value.dtype or actual.shape != value.shape:
                raise ValueError("array dtype/shape conservation failed")
            np.testing.assert_array_equal(actual, value)


def write_csv(path, rows, fields):
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows({k: r[k] for k in fields} for r in rows)
    path.write_bytes(gzip.compress(buffer.getvalue().encode(), mtime=0))


def spike_arrays(path):
    if h5py.is_hdf5(path):
        with h5py.File(path) as handle:
            arrays = {
                k: numeric(handle[k][()])
                for k in ("timestamps", "reference", "components")
            }
        format_name = "matlab_v7_3_hdf5"
    else:
        mat = loadmat(path, squeeze_me=False, chars_as_strings=False)
        arrays = {k: numeric(mat[k]) for k in ("timestamps", "reference", "components")}
        format_name = "matlab_v5"
    if (
        arrays["timestamps"].dtype.kind not in "iuf"
        or not np.isfinite(arrays["timestamps"]).all()
    ):
        raise ValueError("nonfinite/nonnumeric spike timestamps")
    reference = _decode_matlab_string(arrays["reference"])
    if "/" in reference or "\\" in reference:
        raise ValueError("unexpected path-bearing native reference")
    return arrays, format_name


def event_arrays(path, role):
    """Explicit numeric allowlist: never traverse gaze, refs, embedded patch or paths."""
    arrays, origins, attributes = {}, {}, {}
    with h5py.File(path) as handle:
        if role == "ripple_markers":
            groups = [g for g in ("rp/data", "df/data") if g in handle]
            if len(groups) != 1:
                raise ValueError("unknown/ambiguous Ripple schema")
            prefix = groups[0]
            names = (
                "markers",
                "timeStamps",
                "trialIndices",
                "SampleRate",
                "session_start_sec",
                "numSets",
                "Args/Data/markers",
                "Args/Data/timeStamps",
                "Args/Data/SampleRate",
                "Args/StartMarker",
                "Args/aligned",
            )
            required = ("markers", "timeStamps")
        elif "el/data" in handle:
            prefix = "el/data"
            names = (
                "trial_codes",
                "trial_timestamps",
                "timeouts",
                "session_start",
                "session_start_index",
                "expTime",
                "noOfSessions",
                "noOfTrials",
                "numSets",
                "missing_idx",
            )
            required = ("trial_codes", "trial_timestamps")
        elif all(k in handle for k in ("triggers", "timestamps", "missing_idx")):
            prefix = ""
            names = ("triggers", "timestamps", "missing_idx", "session_start")
            required = ("triggers", "timestamps", "missing_idx")
        else:
            raise ValueError("unknown Eye schema")
        for name in names:
            origin = f"{prefix}/{name}".lstrip("/")
            if origin in handle:
                key = name.replace("/", "__")
                dataset = handle[origin]
                arrays[key] = numeric(dataset[()])
                origins[key] = origin
                attributes[key] = {}
                for attr in ("MATLAB_class", "MATLAB_empty", "MATLAB_int_decode"):
                    if attr in dataset.attrs:
                        value = np.asarray(dataset.attrs[attr]).tolist()
                        attributes[key][attr] = (
                            value.decode("ascii") if isinstance(value, bytes) else value
                        )
            elif name in required:
                raise ValueError("missing required event array")
        commit = None
        if "metadata/gitcommit" in handle:
            commit = _decode_matlab_string(handle["metadata/gitcommit"][()])
            if not re.fullmatch(r"[0-9a-f]{40}(?:-dirty)?", commit):
                raise ValueError("unknown processing commit syntax")
    return arrays, {
        "origins": origins,
        "attributes": attributes,
        "event_axis": 0,
        "processing_commit": commit,
    }


def unity_arrays(path):
    headers, rows = [], []
    with path.open() as handle:
        for line in handle:
            parts = line.split()
            try:
                is_row = len(parts) == 5 and all(np.isfinite(float(p)) for p in parts)
            except ValueError:
                is_row = False
            if is_row:
                rows.append(parts[:2])
            elif rows:
                raise ValueError("malformed Unity numeric row")
            elif line.strip():
                if ":" not in line or "/" in line or "\\" in line:
                    raise ValueError("unknown/path-bearing Unity header")
                headers.append(line.rstrip("\r\n"))
    if not rows:
        raise ValueError("empty Unity numeric stream")
    # Exact ASCII tokens avoid redundant binary doubles; float64 parsing is lossless
    # relative to the native text reader, including startup/orphan/zero-marker rows.
    tokens = np.asarray(rows, dtype="S")
    values = tokens.astype(np.float64)
    if (
        not np.equal(values[:, 0], np.rint(values[:, 0])).all()
        or (values[:, 1] < 0).any()
    ):
        raise ValueError("invalid Unity marker/delta")
    return {"timing_tokens": tokens}, headers


def export(*, root, inventory, outer, inner, output, revision):
    root, output = Path(root).resolve(), Path(output)
    rows = list(_rows(Path(inventory)))
    if len(rows) != 370 or len({r["path"] for r in rows}) != 370:
        raise ValueError("expected exactly 370 distinct native inputs")
    roles = {
        role: sum(r["role"] == role for r in rows) for role in {r["role"] for r in rows}
    }
    if roles != {
        "selection_list": 1,
        "spiketrain": 195,
        "ripple_markers": 58,
        "eyelink_markers": 58,
        "unity_raw": 58,
    }:
        raise ValueError("native role inventory mismatch")
    paths = {r["path"]: regular(root, r["path"]) for r in rows}

    def verify_originals():
        for row in rows:
            path = paths[row["path"]]
            if (
                path.stat().st_size != int(row["bytes"])
                or file_hash(path) != row["sha256"]
            ):
                raise ValueError("native input hash/size mismatch")

    verify_originals()
    if file_hash(Path(outer)) != OUTER_SHA or file_hash(Path(inner)) != INNER_SHA:
        raise ValueError("frozen assignment authentication failed")
    selection = next(r for r in rows if r["role"] == "selection_list")
    order = []
    for line in paths[selection["path"]].read_text().splitlines():
        match = re.fullmatch(
            r".*?/(\d{8}/session\d+/array\d+/channel\d+/cell\d+)", line.strip()
        )
        if not match:
            raise ValueError("unknown selection-list entry")
        order.append(match[1])
    spikes = [r for r in rows if r["role"] == "spiketrain"]
    if len(set(order)) != 195 or set(order) != {r["cell_id"] for r in spikes}:
        raise ValueError("selection order/unit inventory mismatch")
    sessions = sorted({r["session_id"] for r in spikes})
    if len(sessions) != 58:
        raise ValueError("session inventory mismatch")
    output.mkdir(parents=True, exist_ok=False)
    manifest = {
        "schema": SCHEMA,
        "export_revision": revision,
        "export_source_sha256": {
            "neuro.cue_source_export": file_hash(Path(__file__)),
            "neuro.place195": file_hash(Path(_rows.__code__.co_filename)),
            "neuro.raw_io": file_hash(Path(_decode_matlab_string.__code__.co_filename)),
        },
        "selection_order": order,
        "native_inputs": [],
        "units": [],
        "sessions": [],
        "files": {},
        "clocks": {
            "spikes": "native milliseconds; no sorting, deduplication or clipping",
            "ripple": "native seconds; sample rate/session start retained",
            "eye": "native milliseconds per Julia eyelink.jl; historical heuristic separately disclosed",
            "unity": "all marker/delta tokens; cumulative seconds from every row, including startup/orphans",
        },
        "policy": "historical outer train, frozen exposed inner assignments, global predecessor-contributor embargo; no pristine holdout or historical score reproduction",
        "omissions": [
            "dense Unity x/y/heading",
            "continuous gaze/analog/sample timestamps",
            "fixations/saccades",
            "private paths, embedded gitpatch and incidental MAT headers",
            "models, predictions and historical neural CSVs",
        ],
    }
    spike_payload = {}
    total_spikes = 0
    for index, row in enumerate(
        sorted(spikes, key=lambda r: order.index(r["cell_id"]))
    ):
        arrays, format_name = spike_arrays(paths[row["path"]])
        key = f"unit{index:03d}"
        for name, array in arrays.items():
            spike_payload[key + "__" + name] = array
        total_spikes += arrays["timestamps"].size
        manifest["units"].append(
            {
                "cell_id": row["cell_id"],
                "session_id": row["session_id"],
                "key": key,
                "format": format_name,
                "selection_provenance": "place_selective_195_snapshot",
            }
        )
    write_npz(output / "spikes.npz", spike_payload)
    for session in sessions:
        payload, details = {}, {}
        for role, prefix in (
            ("ripple_markers", "ripple"),
            ("eyelink_markers", "eye"),
            ("unity_raw", "unity"),
        ):
            matches = [
                r for r in rows if r["session_id"] == session and r["role"] == role
            ]
            if len(matches) != 1:
                raise ValueError("duplicate/missing session stream")
            row = matches[0]
            if prefix == "unity":
                arrays, headers = unity_arrays(paths[row["path"]])
                details[prefix] = {"ordered_headers": headers}
            else:
                arrays, details[prefix] = event_arrays(paths[row["path"]], role)
            payload.update({prefix + "__" + k: v for k, v in arrays.items()})
        filename = session + ".npz"
        write_npz(output / filename, payload)
        manifest["sessions"].append(
            {"session_id": session, "file": filename, **details}
        )
    for row in rows:
        public_name = (
            row["cell_id"] + "/spiketrain.mat"
            if row["role"] == "spiketrain"
            else row["session_id"] + "/" + row["role"]
        )
        manifest["native_inputs"].append(
            {
                "role": row["role"],
                "name": public_name.lstrip("/"),
                "bytes": int(row["bytes"]),
                "sha256": row["sha256"],
            }
        )
    write_csv(
        output / "outer_splits.csv.gz",
        list(_rows(Path(outer))),
        (
            "source_trial_id",
            "session_id",
            "trial_index",
            "previous_source_trial_id",
            "split",
            "split_version",
            "split_block_id",
        ),
    )
    write_csv(
        output / "inner_splits.csv.gz",
        list(_rows(Path(inner))),
        ("source_trial_id", "session_id", "split", "label", "original_split"),
    )
    manifest["assignment_inputs"] = {
        "outer_sha256": OUTER_SHA,
        "inner_sha256": INNER_SHA,
    }
    manifest["total_spike_timestamps"] = total_spikes
    for path in sorted(output.iterdir()):
        if path.stat().st_size >= 100 * 1024**2:
            raise ValueError("candidate exceeds ordinary Git blob budget")
        manifest["files"][path.name] = {
            "sha256": file_hash(path),
            "bytes": path.stat().st_size,
        }
    (output / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    )
    (output / "manifest.sha256").write_text(
        file_hash(output / "manifest.json") + "  manifest.json\n"
    )
    verify_originals()
    return {
        "files": len(manifest["files"]),
        "spikes": total_spikes,
        "bytes": sum(p.stat().st_size for p in output.iterdir()),
        "manifest_sha256": file_hash(output / "manifest.json"),
    }
