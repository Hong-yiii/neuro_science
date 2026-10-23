"""Explicit invented/supplied source routes for the fresh notebooks, no cache fallback."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from neuro.place195 import MetadataSelection, reconstruct_neural, select_metadata
from neuro.source_data import Source, SourceData, Split, Target, TargetDefinition, Unit


def demo_configuration() -> dict:
    return {
        "mode": "invented",
        "landmarks": [1, 2, 3],
        "fixture_seed": 73,
        "demo_units": 9,
        "demo_blocks": 3,
        "demo_bins": 4,
        "demo_train_sources_per_pool": 8,
        "demo_development_sources_per_pool": 4,
        "execution": {
            "iterations": 20,
            "train_rows_per_condition": 8,
            "development_rows_per_condition": 4,
            "seeds": [0, 1],
            "subset_seed": 20261023,
            "permutation_seed": 50000,
            "pca_components": 8,
            "hidden": 32,
            "output_dimension": 8,
            "batch_size": 32,
            "learning_rate": 0.0003,
            "logistic_C": 0.01,
            "logistic_max_iter": 2000,
        },
    }


def configuration_from_environment() -> dict:
    path = os.environ.get("NEURO_NOTEBOOK_CONFIG")
    if path is None:
        return (
            demo_configuration()
        )  # Explicit public default, not a missing-input fallback.
    config = json.loads(Path(path).read_text())
    config["manifest_directory"] = str(Path(path).resolve().parent)
    return config


def _invented_metadata(config):
    landmarks = config["landmarks"]
    if len(set(landmarks)) != len(landmarks) or len(landmarks) < 3:
        raise ValueError("invented fixture requires >=3 distinct landmarks")
    n_units, n_blocks, n_bins = (
        int(config[k]) for k in ("demo_units", "demo_blocks", "demo_bins")
    )
    if n_units < 9 or not 1 <= n_blocks <= n_units or n_bins < 4:
        raise ValueError("invented fixture requires >=9 units and >=4 bins")
    units = [
        {
            "cell_id": f"invented/block{b}/unit{i}",
            "session_id": f"invented/block{b}",
            "selection_provenance": "invented Poisson source fixture",
        }
        for b in range(n_blocks)
        for i in range(n_units // n_blocks + int(b < n_units % n_blocks))
    ]
    sources = []
    for b in range(n_blocks):
        order = 0
        for split, field in (
            ("train", "demo_train_sources_per_pool"),
            ("development", "demo_development_sources_per_pool"),
        ):
            count = int(config[field])
            if count < (2 if split == "train" else 1):
                raise ValueError("incomplete invented source support")
            for start in landmarks:
                for goal in landmarks:
                    if start == goal:
                        continue
                    for _ in range(count):
                        sid = f"invented/block{b}/trial{order}"
                        sources.append(
                            {
                                "source_id": sid,
                                "block_id": f"invented/block{b}",
                                "split_id": split,
                                "trial_order": order,
                                "condition": f"{start}->{goal}",
                                "previous_id": f"{sid}/label-only-predecessor",
                                "start": start,
                                "goal": goal,
                            }
                        )
                        order += 1
    return tuple(sources), tuple(units)


@dataclass(frozen=True)
class InputInspection:
    config: dict
    selected: tuple[dict, ...]
    eligible: tuple[dict, ...]
    units: tuple[dict, ...]
    audit: dict
    place195_selection: MetadataSelection | None = None


def inspect_inputs(config: dict) -> InputInspection:
    if config["mode"] == "place195":
        selection = select_metadata(
            config, base=Path(config.get("manifest_directory", "."))
        )
        return InputInspection(
            config,
            selection.selected,
            selection.eligible,
            selection.units,
            selection.audit,
            selection,
        )
    if config["mode"] != "invented":
        raise ValueError(
            "unknown input mode; missing supplied inputs never become demo data"
        )
    sources, units = _invented_metadata(config)
    train = sum(s["split_id"] == "train" for s in sources)
    dev = len(sources) - train
    audit = {
        "eligible": len(sources),
        "original_train": train,
        "original_development": dev,
        "original_units": len(units),
        "original_sessions": config["demo_blocks"],
        "selected_train": train,
        "selected_development": dev,
        "selected_units": len(units),
        "selected_sessions": config["demo_blocks"],
        "embargo_removed_train": 0,
        "surviving_train": train,
        "contributor_overlap": 0,
        "exclusion_counts": {},
        "access": "invented fixture; no biological input files",
    }
    return InputInspection(config, sources, sources, units, audit)


def load_inputs(inspection: InputInspection) -> tuple[SourceData, dict]:
    config = inspection.config
    if inspection.place195_selection is not None:
        if (
            not config.get("biological_execution")
            or os.environ.get("NEURO_ALLOW_BIOLOGICAL") != "1"
        ):
            raise PermissionError(
                "biological neural interpretation remains gated pending independent review"
            )
        return reconstruct_neural(inspection.place195_selection, interpret_neural=True)
    rng = np.random.default_rng(config["fixture_seed"])
    sources, units = inspection.selected, inspection.units
    bins = config["demo_bins"]
    values = np.full((len(sources), len(units), bins), np.nan, dtype=np.float32)
    mask = np.array(
        [[s["block_id"] == u["session_id"] for u in units] for s in sources]
    )
    pairs = [
        f"{a}->{b}" for a in config["landmarks"] for b in config["landmarks"] if a != b
    ]
    for si, source in enumerate(sources):
        indices = np.flatnonzero(mask[si])
        # Independent invented count noise supplies rank; explicit pair-index signal is a smoke control.
        rate = (
            2
            + 3
            * np.sin(
                (pairs.index(source["condition"]) + 1)
                * (np.arange(len(indices))[:, None] + 1)
                + np.arange(bins)[None, :]
            )
            ** 2
        )
        values[si, indices] = rng.poisson(rate)
    data = SourceData(
        values,
        mask,
        np.full((len(sources), bins), 0.1),
        tuple(
            Source(
                s["source_id"],
                s["block_id"],
                s["split_id"],
                s["trial_order"],
                s["source_id"],
                "invented fixture",
                (s["previous_id"],),
                "invented label-only predecessor",
            )
            for s in sources
        ),
        tuple(
            Unit(u["cell_id"], u["session_id"], u["selection_provenance"])
            for u in units
        ),
        tuple(Target(s["source_id"], s["condition"], s["condition"]) for s in sources),
        (
            Split("train", "train", "invented source train"),
            Split("development", "evaluation", "invented source development"),
        ),
        TargetDefinition(
            "invented ordered pair",
            "fixture-v1",
            "explicit invented start/goal",
            ("fixture_start", "fixture_goal"),
            "derived",
            tuple((p, p) for p in pairs),
        ),
        np.arange(bins + 1) * 0.1,
        "s",
        "count",
        "invented cue start",
        "invented seconds",
        "contributors-disjoint",
        "invented source and label contributors are split-disjoint",
    )
    return data, {
        "observed_values": int(mask.sum() * bins),
        "unavailable_values": int((~mask).sum() * bins),
        "full_exposure": True,
        "access": "fresh invented count generation",
    }


def effective_pair_map(
    data: SourceData, *, permutation_seed: int | None
) -> dict[str, str]:
    """Joint-pair permutation within source block×split, never synthetic-row shuffle."""
    mapping = {t.source_id: t.condition for t in data.targets}
    if permutation_seed is None:
        return mapping
    rng = np.random.default_rng(permutation_seed)
    for block in sorted(data.block_ids):
        for split in sorted(s.split_id for s in data.splits):
            ids = sorted(
                s.source_id
                for s in data.sources
                if s.block_id == block and s.split_id == split
            )
            values = rng.permutation([mapping[sid] for sid in ids])
            mapping.update(zip(ids, (str(v) for v in values), strict=True))
    return mapping
