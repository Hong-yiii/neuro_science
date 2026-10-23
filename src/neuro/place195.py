"""Explicit imported-ledger adapter, not a raw reader or historical-result loader.

Metadata selection is separate from neural interpretation. Only six caller-supplied
files are opened. Mixed-split gzip bytes are traversed; rejected numeric fields are
never converted. No filename parsing, studies import, or private default paths.
"""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from neuro.neural_inputs import bin_events
from neuro.source_data import Source, SourceData, Split, Target, TargetDefinition, Unit

INPUT_KEYS = frozenset(
    {"trials", "units", "counts", "events", "outer_splits", "inner_splits"}
)


def file_hash(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def authenticate_inputs(manifest: dict, *, base: Path) -> dict[str, Path]:
    if set(manifest["inputs"]) != INPUT_KEYS:
        raise ValueError("exactly the six declared input files are required")
    paths = {}
    for key, entry in manifest["inputs"].items():
        path = (base / entry["path"]).resolve()
        if not path.is_file() or file_hash(path) != entry["sha256"]:
            raise ValueError(f"input authentication failed: {key}")
        paths[key] = path
    if len(set(paths.values())) != len(INPUT_KEYS):
        raise ValueError("input paths must be distinct")
    return paths


def _rows(path: Path):
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or len(set(reader.fieldnames)) != len(
            reader.fieldnames
        ):
            raise ValueError("missing/duplicate CSV header")
        for row in reader:
            if None in row or any(v is None for v in row.values()):
                raise ValueError("malformed CSV row")
            yield row


def _index(rows, field):
    result = {}
    for row in rows:
        key = row[field]
        if not key or key in result:
            raise ValueError(f"empty/duplicate {field}")
        result[key] = row
    return result


@dataclass(frozen=True)
class MetadataSelection:
    paths: dict[str, Path]
    manifest: dict
    trials: dict[str, dict]
    units: tuple[dict, ...]
    eligible: tuple[dict, ...]
    selected: tuple[dict, ...]
    exclusions: tuple[dict, ...]
    audit: dict


def select_metadata(manifest: dict, *, base: Path = Path(".")) -> MetadataSelection:
    """Reproduce original eligibility/assignment, then embargo and select support.

    No numeric neural fields are interpreted by this function. Unit selection is
    inherited; endpoints are provisional marker-derived, not measured ground truth.
    """
    manifest = json.loads(
        json.dumps(manifest)
    )  # Own a value snapshot, not caller-owned nested dictionaries.
    paths = authenticate_inputs(manifest, base=base)
    outer = _index(_rows(paths["outer_splits"]), "source_trial_id")
    trials_all = _index(_rows(paths["trials"]), "source_trial_id")
    if outer.keys() != trials_all.keys():
        raise ValueError("outer assignment/trial ID mismatch")
    trials = {
        sid: row for sid, row in trials_all.items() if outer[sid]["split"] == "train"
    }
    for sid, row in trials.items():
        assigned = outer[sid]
        if (
            row["session_id"] != assigned["session_id"]
            or row["trial_index"] != assigned["trial_index"]
            or row["previous_source_trial_id"] != assigned["previous_source_trial_id"]
        ):
            raise ValueError("outer split identity metadata mismatch")
    units_by_id = _index(_rows(paths["units"]), "cell_id")
    units = tuple(units_by_id[key] for key in sorted(units_by_id))
    if any(u["selection_provenance"] != "place_selective_195_snapshot" for u in units):
        raise ValueError("unexpected inherited unit selection provenance")
    landmarks = tuple(manifest["landmarks"])
    if len(set(landmarks)) != len(landmarks) or len(landmarks) < 2:
        raise ValueError("invalid landmark IDs")
    pairs = tuple(f"{s}->{g}" for s in landmarks for g in landmarks if s != g)
    eligible, exclusions = [], []
    for sid, row in trials.items():
        previous = trials.get(row["previous_source_trial_id"])
        reason = ""
        if row["outcome"] != "success":
            reason = "current_not_success"
        elif previous is None or previous["outcome"] != "success":
            reason = "previous_unavailable_or_not_success"
        elif previous["session_id"] != row["session_id"] or int(
            previous["trial_index"]
        ) + 1 != int(row["trial_index"]):
            raise ValueError("invalid previous-trial linkage")
        elif row["qc_flags"] or previous["qc_flags"]:
            reason = "current_or_previous_qc"
        elif not 1 <= float(row["ripple_cue_duration_s"]) <= 1.5:
            reason = "cue_not_full_nominal_second"
        if reason:
            exclusions.append({"source_id": sid, "reason": reason})
            continue
        if previous is None:
            raise ValueError("eligible trial lost its predecessor")
        start, goal = (
            int(previous["marker_minor_digit"]),
            int(row["marker_minor_digit"]),
        )
        pair = f"{start}->{goal}"
        if (
            pair not in pairs
            or row["inferred_start_id_from_previous_marker"] != f"marker_{start}"
            or row["inferred_goal_id"] != f"marker_{goal}"
        ):
            raise ValueError("importer endpoint disagreement")
        for member in (previous, row):
            digit = int(member["marker_minor_digit"])
            expected = [10 + digit, 20 + digit, 30 + digit]
            if any(
                [int(x) for x in member[k].split()] != expected
                for k in ("ripple_codes", "unity_codes", "eyelink_codes")
            ):
                raise ValueError("multimodal marker disagreement")
        eligible.append(
            {
                "source_id": sid,
                "block_id": row["session_id"],
                "condition": pair,
                "trial_order": int(row["trial_index"]),
                "previous_id": previous["source_trial_id"],
                "start": start,
                "goal": goal,
            }
        )
    pools = defaultdict(list)
    for source in eligible:
        pools[source["block_id"], source["condition"]].append(source)
    rng = np.random.default_rng(manifest["inner_split_seed"])
    sessions = sorted({u["session_id"] for u in units})
    for session in sessions:
        for pair in pairs:
            pool = sorted(pools[session, pair], key=lambda s: s["source_id"])
            if len(pool) < 2:
                raise ValueError("original inner split lacks complete class support")
            for i, index in enumerate(rng.permutation(len(pool))):
                pool[int(index)]["split_id"] = (
                    "development" if i < max(1, len(pool) // 4) else "train"
                )
    frozen = _index(_rows(paths["inner_splits"]), "source_trial_id")
    if frozen.keys() != {s["source_id"] for s in eligible}:
        raise ValueError("regenerated eligible IDs differ from frozen assignments")
    for source in eligible:
        saved = frozen[source["source_id"]]
        split = "validation" if source["split_id"] == "development" else "train"
        if (
            saved["split"] != split
            or saved["label"] != source["condition"]
            or saved["session_id"] != source["block_id"]
            or saved["original_split"] != "train"
        ):
            raise ValueError("regenerated inner split differs from frozen assignment")
    by_id = {s["source_id"]: s for s in eligible}
    edges = Counter()
    for source in eligible:
        previous = by_id.get(source["previous_id"])
        a = "dev" if source["split_id"] == "development" else "train"
        b = (
            ("dev" if previous["split_id"] == "development" else "train")
            if previous
            else "external"
        )
        edges[f"{b}->{a}"] += 1  # Direction is predecessor -> current.
    development_contributors = {
        sid
        for s in eligible
        if s["split_id"] == "development"
        for sid in (s["source_id"], s["previous_id"])
    }
    surviving = [
        s
        for s in eligible
        if s["split_id"] == "development"
        or not {s["source_id"], s["previous_id"]} & development_contributors
    ]
    support = Counter((s["block_id"], s["condition"], s["split_id"]) for s in surviving)
    selected_sessions = {
        session
        for session in sessions
        if all(
            support[session, pair, "train"] >= 2
            and support[session, pair, "development"] >= 1
            for pair in pairs
        )
    }
    selected = tuple(
        sorted(
            (s for s in surviving if s["block_id"] in selected_sessions),
            key=lambda s: s["source_id"],
        )
    )
    selected_units = tuple(u for u in units if u["session_id"] in selected_sessions)
    train_union = {
        sid
        for s in selected
        if s["split_id"] == "train"
        for sid in (s["source_id"], s["previous_id"])
    }
    dev_union = {
        sid
        for s in selected
        if s["split_id"] == "development"
        for sid in (s["source_id"], s["previous_id"])
    }
    if train_union & dev_union:
        raise ValueError("selected direct contributors overlap")
    global_train = [
        support[session, pair, "train"] for session in sessions for pair in pairs
    ]
    audit = {
        "eligible": len(eligible),
        "original_train": sum(s["split_id"] == "train" for s in eligible),
        "original_development": sum(s["split_id"] == "development" for s in eligible),
        "original_units": len(units),
        "original_sessions": len(sessions),
        "development_contributor_union": len(development_contributors),
        "embargo_removed_train": len(eligible) - len(surviving),
        "surviving_train": sum(s["split_id"] == "train" for s in surviving),
        "global_zero_pools": sum(n == 0 for n in global_train),
        "global_one_pools": sum(n == 1 for n in global_train),
        "global_two_plus_pools": sum(n >= 2 for n in global_train),
        "selected_sessions": len(selected_sessions),
        "selected_units": len(selected_units),
        "selected_train": sum(s["split_id"] == "train" for s in selected),
        "selected_development": sum(s["split_id"] == "development" for s in selected),
        "external_predecessors": sum(s["previous_id"] not in by_id for s in eligible),
        "directed_edges": dict(edges),
        "edge_direction": "predecessor->current",
        "contributor_overlap": 0,
        "exclusion_counts": dict(Counter(e["reason"] for e in exclusions)),
        "access": "six explicit input files; whole-file hashes; metadata only, no neural numeric interpretation",
    }
    for key, expected in manifest.get("expected_metadata", {}).items():
        if audit.get(key) != expected:
            raise ValueError(f"frozen metadata total mismatch: {key}")
    if not selected:
        raise ValueError("empty complete support panel")
    normalized = {
        **manifest,
        "inputs": {
            key: {**manifest["inputs"][key], "path": str(path)}
            for key, path in paths.items()
        },
    }
    return MetadataSelection(
        paths,
        normalized,
        trials,
        selected_units,
        tuple(eligible),
        selected,
        tuple(exclusions),
        audit,
    )


def _finite(text: str) -> float:
    value = float(text)
    if not np.isfinite(value):
        raise ValueError("nonfinite numeric neural field")
    return value


def _serialization_tolerance(*values: float) -> float:
    # Imported CSV floats have nine significant digits, not acquisition precision.
    return 1e-9 + sum(
        0.51 * 10 ** (np.floor(np.log10(abs(v))) - 8) for v in values if v
    )


def reconstruct_neural(
    selection: MetadataSelection, *, interpret_neural: bool = False
) -> tuple[SourceData, dict]:
    """Explicit authorized numerical step; never invoked by metadata inspection."""
    if not interpret_neural:
        raise PermissionError(
            "neural interpretation requires explicit execution authorization"
        )
    # Frozen dataclasses do not freeze nested dictionaries. Recompute canonical
    # metadata from authenticated files and compare VALUES before interpreting
    # any neural numeric payload. Use only that independent canonical selection.
    canonical = select_metadata(selection.manifest, base=Path("."))
    for field in (
        "paths",
        "manifest",
        "trials",
        "units",
        "eligible",
        "selected",
        "exclusions",
        "audit",
    ):
        if getattr(selection, field) != getattr(canonical, field):
            raise ValueError("metadata selection changed or was forged")
    selection = canonical
    paths = selection.paths
    sources = selection.selected
    source_index = {s["source_id"]: i for i, s in enumerate(sources)}
    units = selection.units
    unit_index = {u["cell_id"]: i for i, u in enumerate(units)}
    width, nominal = (
        float(selection.manifest["bin_width_s"]),
        float(selection.manifest["nominal_s"]),
    )
    n_bins = int(round(nominal / width))
    if width <= 0 or nominal <= 0 or not np.isclose(n_bins * width, nominal):
        raise ValueError("invalid cue bin geometry")
    expected_pairs = {
        (s["source_id"], u["cell_id"])
        for s in sources
        for u in units
        if s["block_id"] == u["session_id"]
    }
    windows, counts = {}, {}
    audit = {
        "counts_seen": 0,
        "counts_rejected": 0,
        "events_seen": 0,
        "events_rejected": 0,
        "counts_accepted": 0,
        "events_accepted": 0,
        "tail_spikes": 0,
        "access": "mixed gzip bytes traversed; source/unit gate precedes numeric neural interpretation",
    }

    def gate(row):
        sid, cid = row["source_trial_id"], row["cell_id"]
        if sid not in source_index:
            return None
        if (
            cid not in unit_index
            or row["session_id"] != sources[source_index[sid]]["block_id"]
            or units[unit_index[cid]]["session_id"] != row["session_id"]
        ):
            raise ValueError("selected source has unknown/wrong-block unit identity")
        if (sid, cid) not in expected_pairs:
            raise ValueError("source/unit pair outside selected blocks")
        if int(row["trial_index"]) != sources[source_index[sid]]["trial_order"]:
            raise ValueError("neural trial identity mismatch")
        return sid, cid

    for row in _rows(paths["counts"]):
        audit["counts_seen"] += 1
        pair = gate(row)
        if pair is None:
            audit["counts_rejected"] += 1
            continue
        if pair in counts:
            raise ValueError("duplicate cue count source/unit row")
        start, end = (
            _finite(row["cue_window_start_ripple_s"]),
            _finite(row["cue_window_end_ripple_s"]),
        )
        count = _finite(row["cue_spike_count"])
        duration = end - start
        if (
            count < 0
            or count != int(count)
            or duration < nominal
            or duration > 1.5 + _serialization_tolerance(start, end)
        ):
            raise ValueError("invalid count/duration/full exposure")
        declared_duration = float(selection.trials[pair[0]]["ripple_cue_duration_s"])
        if abs(duration - declared_duration) > _serialization_tolerance(
            start, end, declared_duration
        ):
            raise ValueError("cue window and trial duration disagree")
        prior = windows.setdefault(pair[0], (start, end))
        if prior != (start, end):
            raise ValueError("cue windows differ across units")
        counts[pair] = int(count)
        audit["counts_accepted"] += 1
    if counts.keys() != expected_pairs:
        raise ValueError("incomplete selected source/unit count support")
    events = defaultdict(list)
    seen_events = set()
    for row in _rows(paths["events"]):
        audit["events_seen"] += 1
        pair = gate(row)
        if pair is None:
            audit["events_rejected"] += 1
            continue
        relative, absolute = (
            _finite(row["cue_relative_time_s"]),
            _finite(row["spike_time_ripple_s"]),
        )
        start, end = windows[pair[0]]
        if relative < 0 or not relative < end - start:
            raise ValueError("event outside imported cue window")
        if abs((absolute - start) - relative) > _serialization_tolerance(
            absolute, start, relative
        ):
            raise ValueError("absolute/relative event time disagreement")
        key = (*pair, relative, absolute)
        if key in seen_events:
            raise ValueError("duplicate cue spike event row")
        seen_events.add(key)
        events[pair].append(relative)
        audit["events_accepted"] += 1
    values = np.full((len(sources), len(units), n_bins), np.nan, dtype=np.float32)
    observed = np.zeros(values.shape[:2], dtype=bool)
    exposure = np.empty((len(sources), n_bins), dtype=np.float32)
    for sid, cid in sorted(expected_pairs):
        si, ui = source_index[sid], unit_index[cid]
        if len(events[sid, cid]) != counts[sid, cid]:
            raise ValueError("full-window count/event conservation failed")
        start, end = windows[sid]
        binned, exp, tail = bin_events(events[sid, cid], end - start, width, nominal)
        if (
            not np.allclose(exp, width, rtol=0, atol=1e-7)
            or int(binned.sum()) + tail != counts[sid, cid]
        ):
            raise ValueError("bin conservation/full exposure failed")
        values[si, ui], observed[si, ui], exposure[si] = binned, True, exp
        audit["tail_spikes"] += tail
    # Authenticate again after traversal; changed input bytes invalidate the new data.
    authenticate_inputs(selection.manifest, base=Path("."))
    data = SourceData(
        values,
        observed,
        exposure,
        tuple(
            Source(
                s["source_id"],
                s["block_id"],
                s["split_id"],
                s["trial_order"],
                s["source_id"],
                "imported outer-train metadata; fresh binned events",
                (s["previous_id"],),
                "successful adjacent predecessor marker in authenticated outer-train metadata",
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
                "development",
                "evaluation",
                "historically exposed development; restricted panel",
            ),
        ),
        TargetDefinition(
            "ordered endpoint pair",
            "imported-marker-v1",
            "previous/current marker digits; provisional biological meaning",
            ("previous_marker_minor_digit", "marker_minor_digit"),
            "derived",
            tuple(
                (f"{a}->{b}", f"{a}->{b}")
                for a in selection.manifest["landmarks"]
                for b in selection.manifest["landmarks"]
                if a != b
            ),
        ),
        np.arange(n_bins + 1) * width,
        "s",
        "count",
        "imported Ripple cue start",
        "Ripple seconds; nine-significant-digit CSV",
        "contributors-disjoint",
        "global original development-contributor union embargo; serial dependence remains",
    )
    return data, audit
