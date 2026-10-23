"""Seeded condition-matched, intact-block pseudopopulations from supplied sources.

Sampling with replacement is an explicit policy, not Cartesian enumeration. Rows
are condition-level synthetic observations, never independent biological trials.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from dataclasses import dataclass, replace

import numpy as np

from neuro.source_data import SourceData


@dataclass(frozen=True)
class AssemblyRow:
    row_id: str
    condition: str
    target: str
    source_ids: tuple[str, ...]  # One source per SourceData.block_ids, in that order.

    def __post_init__(self):
        object.__setattr__(self, "source_ids", tuple(self.source_ids))


@dataclass(frozen=True)
class AssemblyPlan:
    split_id: str
    seed: int
    split_identity: str
    effective_conditions: tuple[tuple[str, str], ...]
    rows: tuple[AssemblyRow, ...]
    policy: str = "sample-with-replacement"

    def __post_init__(self):
        object.__setattr__(
            self,
            "effective_conditions",
            tuple(tuple(pair) for pair in self.effective_conditions),
        )
        object.__setattr__(self, "rows", tuple(self.rows))

    @property
    def effective_condition_identity(self) -> str:
        """Effective map identity; split_identity separately binds observed targets/data."""
        return hashlib.sha256(
            json.dumps(sorted(self.effective_conditions)).encode()
        ).hexdigest()


@dataclass(frozen=True, eq=False)
class Assembly:
    values: np.ndarray  # row × unit × bin; raw features retain this unit-major order.
    exposure: np.ndarray  # row × block × bin; blocks need not have equal exposure.
    targets: np.ndarray
    plan: AssemblyPlan
    unit_ids: tuple[str, ...]
    block_ids: tuple[str, ...]
    # plan.rows + unit/block order + source contract reconstruct all values and labels.


def _effective(data: SourceData, effective_conditions=None) -> dict[str, str]:
    observed = {t.source_id: t.condition for t in data.targets}
    if effective_conditions is None:
        return observed
    effective = dict(effective_conditions)
    if (
        len(effective) != len(effective_conditions)
        or effective.keys() != observed.keys()
    ):
        raise ValueError("effective conditions must cover every source exactly once")
    allowed = dict(data.target_definition.condition_to_target)
    if any(condition not in allowed for condition in effective.values()):
        raise ValueError("unknown effective condition")
    return effective


def support(data: SourceData, *, effective_conditions=None) -> list[dict]:
    effective = _effective(data, effective_conditions)
    counts = Counter(
        (s.split_id, s.block_id, effective[s.source_id]) for s in data.sources
    )
    return [
        {
            "split_id": split.split_id,
            "block_id": block,
            "condition": condition,
            "source_count": counts[split.split_id, block, condition],
        }
        for split in data.splits
        for block in data.block_ids
        for condition, _ in data.target_definition.condition_to_target
    ]


def sample_plan(
    data: SourceData,
    *,
    split_id: str,
    rows_per_condition: int,
    seed: int,
    effective_conditions=None,
    max_rows: int = 100_000,
) -> AssemblyPlan:
    if (
        isinstance(rows_per_condition, bool)
        or not isinstance(rows_per_condition, int)
        or rows_per_condition < 1
    ):
        raise ValueError("rows_per_condition must be a positive integer")
    if isinstance(seed, bool) or not isinstance(seed, int) or seed < 0:
        raise ValueError("seed must be a nonnegative integer")
    conditions = data.target_definition.condition_to_target
    if isinstance(max_rows, bool) or not isinstance(max_rows, int) or max_rows < 1:
        raise ValueError("max_rows must be a positive integer")
    if rows_per_condition * len(conditions) > max_rows:
        raise ValueError("assembly exceeds max_rows")
    effective = _effective(data, effective_conditions)
    identity = data.split_identity(split_id)
    rng = np.random.default_rng(seed)
    rows = []
    for condition, target in conditions:
        pools = [
            sorted(
                s.source_id
                for s in data.sources
                if s.split_id == split_id
                and s.block_id == block
                and effective[s.source_id] == condition
            )
            for block in data.block_ids
        ]
        if any(not pool for pool in pools):
            raise ValueError(
                f"incomplete split/block/condition support: {split_id}/{condition}"
            )
        for i in range(rows_per_condition):
            rows.append(
                AssemblyRow(
                    f"{split_id}:condition{len(rows) // rows_per_condition}:row{i}",
                    condition,
                    target,
                    tuple(str(rng.choice(pool)) for pool in pools),
                )
            )
    split_sources = {s.source_id for s in data.sources if s.split_id == split_id}
    return AssemblyPlan(
        split_id,
        seed,
        identity,
        tuple(
            sorted(
                (sid, condition)
                for sid, condition in effective.items()
                if sid in split_sources
            )
        ),
        tuple(rows),
    )


def materialize(
    data: SourceData, plan: AssemblyPlan, *, max_rows: int = 100_000
) -> Assembly:
    """Revalidate even hand-built plans, including effective-label/split/block identity."""
    if (
        isinstance(max_rows, bool)
        or not isinstance(max_rows, int)
        or max_rows < 1
        or len(plan.rows) > max_rows
    ):
        raise ValueError("invalid or exceeded max_rows")
    if plan.policy != "sample-with-replacement" or not plan.rows:
        raise ValueError("unsupported or empty assembly plan")
    if isinstance(plan.seed, bool) or not isinstance(plan.seed, int) or plan.seed < 0:
        raise ValueError("invalid plan seed")
    if plan.split_identity != data.split_identity(plan.split_id):
        raise ValueError("plan input split identity mismatch")
    effective = dict(plan.effective_conditions)
    expected_ids = {s.source_id for s in data.sources if s.split_id == plan.split_id}
    allowed = dict(data.target_definition.condition_to_target)
    if (
        len(effective) != len(plan.effective_conditions)
        or effective.keys() != expected_ids
        or any(c not in allowed for c in effective.values())
    ):
        raise ValueError("plan effective conditions must cover its split exactly")
    source_index = {s.source_id: i for i, s in enumerate(data.sources)}
    target_map = dict(data.target_definition.condition_to_target)
    row_ids = [r.row_id for r in plan.rows]
    if any(not isinstance(s, str) or not s.strip() for s in row_ids) or len(
        set(row_ids)
    ) != len(row_ids):
        raise ValueError("empty or duplicate row IDs")
    values = np.empty(
        (len(plan.rows), len(data.units), data.values.shape[2]), dtype=data.values.dtype
    )
    exposure = np.empty(
        (len(plan.rows), len(data.block_ids), data.values.shape[2]),
        dtype=data.exposure.dtype,
    )
    unit_indices = {
        block: [i for i, u in enumerate(data.units) if u.block_id == block]
        for block in data.block_ids
    }
    for row_index, row in enumerate(plan.rows):
        if row.condition not in target_map or target_map[row.condition] != row.target:
            raise ValueError("plan effective-label/target mismatch")
        if len(row.source_ids) != len(data.block_ids) or len(
            set(row.source_ids)
        ) != len(row.source_ids):
            raise ValueError("plan must have one distinct source per block")
        for block_index, (block, sid) in enumerate(
            zip(data.block_ids, row.source_ids, strict=True)
        ):
            if sid not in source_index:
                raise ValueError("unknown plan source")
            si = source_index[sid]
            source = data.sources[si]
            if (
                source.split_id != plan.split_id
                or source.block_id != block
                or effective[sid] != row.condition
            ):
                raise ValueError("plan source split/block/effective-label mismatch")
            ui = unit_indices[block]
            values[row_index, ui] = data.values[si, ui]
            exposure[row_index, block_index] = data.exposure[si]
    if {r.condition for r in plan.rows} != set(target_map):
        raise ValueError("plan omits declared conditions")
    targets = np.asarray([r.target for r in plan.rows])
    for arr in (values, exposure, targets):
        arr.setflags(write=False)
    return Assembly(
        values,
        exposure,
        targets,
        plan,
        tuple(u.unit_id for u in data.units),
        data.block_ids,
    )


def source_usage(data: SourceData, assembly: Assembly) -> list[dict]:
    """Eligible/used/unused/repeated source accounting; not an IID sample-size claim."""
    effective = dict(assembly.plan.effective_conditions)
    counts = Counter(sid for row in assembly.plan.rows for sid in row.source_ids)
    return [
        {
            "source_id": s.source_id,
            "block_id": s.block_id,
            "condition": effective[s.source_id],
            "uses": counts[s.source_id],
        }
        for s in data.sources
        if s.split_id == assembly.plan.split_id
    ]


def ablate_training_sources(
    data: SourceData,
    *,
    seed: int,
    sources_per_condition_block: int | None = None,
    fraction: float | None = None,
    effective_conditions=None,
) -> SourceData:
    """Subsample real training sources, retaining all conditions and exact evaluation.

    This returns unfitted source data. Reassemble training rows and REFIT every
    scaler/encoder/PCA/readout. Reuse the original evaluation plan unchanged.
    No deletion of already-fitted pseudorows is represented as a refitted ablation.
    """
    if (sources_per_condition_block is None) == (fraction is None):
        raise ValueError("choose exactly one of source count or fraction")
    if sources_per_condition_block is not None and (
        isinstance(sources_per_condition_block, bool)
        or not isinstance(sources_per_condition_block, int)
        or sources_per_condition_block < 1
    ):
        raise ValueError("sources_per_condition_block must be positive")
    if fraction is not None and (not np.isfinite(fraction) or not 0 < fraction <= 1):
        raise ValueError("fraction must be in (0,1]")
    effective = _effective(data, effective_conditions)
    if isinstance(seed, bool) or not isinstance(seed, int) or seed < 0:
        raise ValueError("invalid ablation seed")
    rng = np.random.default_rng(seed)
    keep = {s.source_id for s in data.sources if s.split_id != data.train_split}
    for block in data.block_ids:
        for condition, _ in data.target_definition.condition_to_target:
            pool = sorted(
                s.source_id
                for s in data.sources
                if s.split_id == data.train_split
                and s.block_id == block
                and effective[s.source_id] == condition
            )
            count = (
                sources_per_condition_block
                if fraction is None
                else max(1, int(np.floor(len(pool) * fraction)))
            )
            if count is None or len(pool) < count:
                raise ValueError(f"insufficient ablation support: {block}/{condition}")
            keep.update(str(sid) for sid in rng.choice(pool, count, replace=False))
    indices = [i for i, s in enumerate(data.sources) if s.source_id in keep]
    # Preserve group/dependency safeguards: unresolved dependencies may make an ablation invalid.
    return replace(
        data,
        values=data.values[indices],
        observed=data.observed[indices],
        exposure=data.exposure[indices],
        sources=tuple(data.sources[i] for i in indices),
        targets=tuple(data.targets[i] for i in indices),
    )
