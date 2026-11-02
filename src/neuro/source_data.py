"""Explicit supplied binned-source contract; no file discovery or label inference.

Values are source × unit × bin. A source observes its complete recording block;
other blocks are unavailable (NaN), never zero-filled. Exposure is source × bin
in the declared time unit. Per-unit/per-bin dropout is deliberately unsupported.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Literal

import numpy as np


def _text(value: str, name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a nonempty string")


def _unique(values, name: str) -> None:
    for value in values:
        _text(value, name)
    if len(set(values)) != len(values):
        raise ValueError(f"duplicate {name}")


@dataclass(frozen=True)
class Source:
    source_id: str  # Dataset-qualified identity supplied by the caller.
    block_id: str
    split_id: str
    trial_order: int
    group_id: str
    provenance: str
    dependency_ids: tuple[str, ...] = ()
    dependency_provenance: str = (
        ""  # Required even for external label-only predecessors.
    )

    def __post_init__(self):
        object.__setattr__(self, "dependency_ids", tuple(self.dependency_ids))
        if isinstance(self.trial_order, np.integer):
            object.__setattr__(self, "trial_order", int(self.trial_order))


@dataclass(frozen=True)
class Unit:
    unit_id: str
    block_id: str
    provenance: str
    simultaneity: Literal["verified", "unknown"] = "unknown"
    simultaneity_evidence: str = "unknown"


@dataclass(frozen=True)
class Split:
    split_id: str
    role: Literal["train", "evaluation"]
    description: str  # Include historical exposure, not just a role name.


@dataclass(frozen=True)
class Target:
    source_id: str
    condition: str  # Assembly matching condition, not necessarily prediction target.
    value: str


@dataclass(frozen=True)
class TargetDefinition:
    name: str
    version: str
    derivation: str
    source_fields: tuple[str, ...]
    status: Literal["measured", "derived", "unverified"]
    condition_to_target: tuple[tuple[str, str], ...]

    def __post_init__(self):
        object.__setattr__(self, "source_fields", tuple(self.source_fields))
        object.__setattr__(
            self,
            "condition_to_target",
            tuple(tuple(pair) for pair in self.condition_to_target),
        )


@dataclass(frozen=True, eq=False)
class SourceData:
    values: np.ndarray
    observed: np.ndarray
    exposure: np.ndarray
    sources: tuple[Source, ...]
    units: tuple[Unit, ...]
    targets: tuple[
        Target, ...
    ]  # Exactly source order; joins must be explicit upstream.
    splits: tuple[Split, ...]
    target_definition: TargetDefinition
    bin_edges: np.ndarray
    time_unit: Literal["s", "ms"]
    value_unit: Literal["count", "rate"]
    event_reference: str
    clock: str
    dependency_policy: Literal[
        "group-disjoint", "contributors-disjoint", "declared-dependent"
    ]
    dependency_description: str

    def __post_init__(self) -> None:
        # Own immutable copies: later mutation of caller arrays/tables cannot change a plan.
        for name in ("sources", "units", "targets", "splits"):
            object.__setattr__(self, name, tuple(getattr(self, name)))
        for name in ("values", "observed", "exposure", "bin_edges"):
            arr = np.array(getattr(self, name), copy=True)
            arr.setflags(write=False)
            object.__setattr__(self, name, arr)
        self.validate()

    def validate(self) -> None:
        if not self.sources or not self.units or not self.splits:
            raise ValueError("empty source/unit/split table")
        _unique([s.source_id for s in self.sources], "source ID")
        _unique([u.unit_id for u in self.units], "unit ID")
        _unique([s.split_id for s in self.splits], "split ID")
        _unique([t.source_id for t in self.targets], "target source ID")
        if tuple(t.source_id for t in self.targets) != tuple(
            s.source_id for s in self.sources
        ):
            raise ValueError("target table must match source IDs and order exactly")
        for name in ("event_reference", "clock", "dependency_description"):
            _text(getattr(self, name), name)
        if self.time_unit not in {"s", "ms"} or self.value_unit not in {
            "count",
            "rate",
        }:
            raise ValueError("unsupported time/value unit")
        if self.dependency_policy not in {
            "group-disjoint",
            "contributors-disjoint",
            "declared-dependent",
        }:
            raise ValueError("declare dependency policy")
        if sum(s.role == "train" for s in self.splits) != 1:
            raise ValueError("exactly one training split required")
        for split in self.splits:
            if split.role not in {"train", "evaluation"}:
                raise ValueError("invalid split role")
            _text(split.description, "split description")
        definition = self.target_definition
        for name in ("name", "version", "derivation"):
            _text(getattr(definition, name), f"target {name}")
        if (
            definition.status not in {"measured", "derived", "unverified"}
            or not definition.source_fields
        ):
            raise ValueError("declare target status and source fields")
        _unique(list(definition.source_fields), "target source field")
        conditions = [c for c, _ in definition.condition_to_target]
        _unique(conditions, "condition")
        mapping = dict(definition.condition_to_target)
        if not mapping:
            raise ValueError("empty target mapping")
        for value in mapping.values():
            _text(value, "target value")
        blocks = self.block_ids
        split_ids = {s.split_id for s in self.splits}
        group_splits: dict[str, set[str]] = {}
        source_by_id = {s.source_id: s for s in self.sources}
        block_orders = set()
        for source, target in zip(self.sources, self.targets, strict=True):
            for name in ("block_id", "group_id", "provenance"):
                _text(getattr(source, name), name)
            if source.block_id not in blocks or source.split_id not in split_ids:
                raise ValueError("source has unknown block/split")
            if (
                isinstance(source.trial_order, bool)
                or not isinstance(source.trial_order, (int, np.integer))
                or source.trial_order < 0
            ):
                raise ValueError("trial_order must be a nonnegative integer")
            key = (source.block_id, source.trial_order)
            if key in block_orders:
                raise ValueError("duplicate block/trial order")
            block_orders.add(key)
            group_splits.setdefault(source.group_id, set()).add(source.split_id)
            _unique(list(source.dependency_ids), "dependency ID")
            if source.source_id in source.dependency_ids:
                raise ValueError("self dependency")
            if source.dependency_ids:
                _text(source.dependency_provenance, "dependency provenance")
            if self.dependency_policy == "group-disjoint":
                for sid in source.dependency_ids:
                    if (
                        sid in source_by_id
                        and source_by_id[sid].split_id != source.split_id
                    ):
                        raise ValueError("cross-split dependency")
            if (
                target.condition not in mapping
                or mapping[target.condition] != target.value
            ):
                raise ValueError("target does not match declared condition mapping")
        if self.dependency_policy == "group-disjoint" and any(
            len(v) != 1 for v in group_splits.values()
        ):
            raise ValueError("group crosses splits")
        if (
            self.dependency_policy == "contributors-disjoint"
            and self.dependency_audit()["overlapping_contributor_ids"]
        ):
            raise ValueError("direct source/label contributors overlap across splits")
        for unit in self.units:
            _text(unit.block_id, "unit block")
            _text(unit.provenance, "unit provenance")
            _text(unit.simultaneity_evidence, "simultaneity evidence")
            if unit.simultaneity not in {"verified", "unknown"}:
                raise ValueError("invalid simultaneity status")
            if (
                unit.simultaneity == "verified"
                and unit.simultaneity_evidence == "unknown"
            ):
                raise ValueError("verified simultaneity needs evidence")
        edges = self.bin_edges
        if (
            edges.ndim != 1
            or len(edges) < 2
            or edges.dtype.kind not in "iuf"
            or not np.isfinite(edges).all()
            or np.any(edges[1:] <= edges[:-1])
        ):
            raise ValueError("finite strictly increasing bin edges required")
        widths = np.diff(edges.astype(np.float64))
        if not np.isfinite(widths).all() or np.any(widths <= 0):
            raise ValueError(
                "bin widths must be representable as positive finite floats"
            )
        shape = (len(self.sources), len(self.units), len(edges) - 1)
        if (
            self.values.shape != shape
            or self.observed.shape != shape[:2]
            or self.observed.dtype != np.bool_
        ):
            raise ValueError("values/mask shape or mask dtype mismatch")
        if not np.issubdtype(self.values.dtype, np.number) or np.iscomplexobj(
            self.values
        ):
            raise ValueError("real numeric values required")
        expected_mask = np.array(
            [[s.block_id == u.block_id for u in self.units] for s in self.sources]
        )
        if not np.array_equal(self.observed, expected_mask):
            raise ValueError("incomplete block support or off-block observations")
        seen = self.values[self.observed]
        if not np.isfinite(seen).all() or np.any(seen < 0):
            raise ValueError("nonfinite or negative observed values")
        if self.value_unit == "count" and np.any(seen != np.floor(seen)):
            raise ValueError("counts must be nonnegative integers")
        if not np.isnan(self.values[~self.observed]).all():
            raise ValueError("unavailable measurements must be NaN, not zero")
        if (
            self.exposure.shape != (shape[0], shape[2])
            or self.exposure.dtype.kind not in "iuf"
            or not np.isfinite(self.exposure).all()
            or np.any(self.exposure <= 0)
        ):
            raise ValueError("finite positive source × bin exposure required")
        if np.any(self.exposure > widths + 1e-7 * np.max(widths)):
            raise ValueError("exposure exceeds bin width")

    @property
    def block_ids(self) -> tuple[str, ...]:
        """First-appearance block order; unit order itself is never rearranged."""
        return tuple(dict.fromkeys(u.block_id for u in self.units))

    @property
    def train_split(self) -> str:
        return next(s.split_id for s in self.splits if s.role == "train")

    def dependency_audit(self) -> dict:
        by_id = {s.source_id: s for s in self.sources}
        cross, unresolved = [], []
        groups: dict[str, set[str]] = {}
        contributors: dict[str, set[str]] = {}
        for source in self.sources:
            groups.setdefault(source.group_id, set()).add(source.split_id)
            for contributor in (source.source_id, *source.dependency_ids):
                contributors.setdefault(contributor, set()).add(source.split_id)
            for sid in source.dependency_ids:
                if sid not in by_id:
                    unresolved.append((source.source_id, sid))
                elif by_id[sid].split_id != source.split_id:
                    cross.append((source.source_id, sid))
        return {
            "cross_split_dependencies": cross,
            "external_dependencies": unresolved,
            "overlapping_contributor_ids": sorted(
                sid for sid, splits in contributors.items() if len(splits) > 1
            ),
            "cross_split_groups": sorted(
                g for g, splits in groups.items() if len(splits) > 1
            ),
            "policy": self.dependency_policy,
            "description": self.dependency_description,
        }

    def split_identity(self, split_id: str) -> str:
        """Bind plans to exact split bytes/metadata; unchanged evaluation survives ablation."""
        from dataclasses import asdict

        indices = [i for i, s in enumerate(self.sources) if s.split_id == split_id]
        if not indices:
            raise ValueError(f"empty or unknown split: {split_id}")
        metadata = {
            "sources": [asdict(self.sources[i]) for i in indices],
            "targets": [asdict(self.targets[i]) for i in indices],
            "units": [asdict(u) for u in self.units],
            "split": [asdict(s) for s in self.splits if s.split_id == split_id],
            "target_definition": asdict(self.target_definition),
            "time_unit": self.time_unit,
            "value_unit": self.value_unit,
            "event_reference": self.event_reference,
            "clock": self.clock,
            "dependency_policy": self.dependency_policy,
            "dependency_description": self.dependency_description,
        }
        digest = hashlib.sha256(json.dumps(metadata, sort_keys=True).encode())
        for arr in (
            self.values[indices],
            self.observed[indices],
            self.exposure[indices],
            self.bin_edges,
        ):
            digest.update(str((arr.shape, arr.dtype.str)).encode())
            digest.update(np.ascontiguousarray(arr).tobytes())
        return digest.hexdigest()
