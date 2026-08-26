"""Validation and hashing for caller-supplied source-trial splits.

No split algorithm lives here. The caller supplies every sample/source/split row.
This module verifies derivative grouping and records the session and simultaneous
recording group needed to review the chosen split policy. Freeze the returned hash
before adaptive behavior cleaning, target selection, or neural fitting.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

ALLOWED_SPLITS = ("train", "validation", "test")


@dataclass(frozen=True)
class SplitRow:
    """One analysis sample and the real source trial that produced it."""

    sample_id: str
    source_trial_id: str
    session_id: str
    simultaneous_recording_group: str
    split: str


@dataclass(frozen=True)
class FrozenSplit:
    """Validated split table with a canonical JSON SHA-256."""

    rows: tuple[SplitRow, ...]
    allowed_labels: tuple[str, ...]
    expected_source_trial_ids: tuple[str, ...]
    canonical_json: str = field(init=False)
    sha256: str = field(init=False)

    def __post_init__(self) -> None:
        payload = {
            "allowed_labels": list(self.allowed_labels),
            "assignments": [
                {
                    "sample_id": row.sample_id,
                    "source_trial_id": row.source_trial_id,
                    "session_id": row.session_id,
                    "simultaneous_recording_group": row.simultaneous_recording_group,
                    "split": row.split,
                }
                for row in self.rows
            ],
            "expected_source_trial_ids": list(self.expected_source_trial_ids),
        }
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        object.__setattr__(self, "canonical_json", canonical)
        object.__setattr__(
            self,
            "sha256",
            hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
        )

    @property
    def source_trial_splits(self) -> dict[str, str]:
        return {
            source_id: metadata[2]
            for source_id, metadata in _source_metadata(self.rows).items()
        }

    @property
    def recording_group_split_counts(self) -> dict[str, dict[str, int]]:
        """Count independent source trials per recording group and split."""

        counts: dict[str, Counter[str]] = {}
        for _source_id, (_session, group, split) in _source_metadata(self.rows).items():
            counts.setdefault(group, Counter())[split] += 1
        return {
            group: dict(sorted(group_counts.items()))
            for group, group_counts in sorted(counts.items())
        }


def freeze_splits(
    assignments: Iterable[SplitRow | Mapping[str, Any]],
    expected_source_trial_ids: Sequence[str],
    allowed_labels: Sequence[str] = ALLOWED_SPLITS,
) -> FrozenSplit:
    """Validate supplied rows and return their stable hash.

    Rows sharing a ``source_trial_id`` are derivatives and must agree on split,
    session, and simultaneous recording group. Expected source-trial coverage is
    exact. This function records group composition but intentionally does not
    choose whether trials, contiguous blocks, sessions, or groups are held out;
    that policy depends on the audited dataset and must be supplied explicitly.
    """

    allowed = tuple(
        sorted({_require_text(label, "split label") for label in allowed_labels})
    )
    if not allowed:
        raise ValueError("allowed_labels must not be empty")

    expected_list = [
        _require_text(source, "expected source_trial_id")
        for source in expected_source_trial_ids
    ]
    if len(set(expected_list)) != len(expected_list):
        raise ValueError("expected_source_trial_ids must be unique")
    expected = tuple(sorted(expected_list))
    if not expected:
        raise ValueError("expected_source_trial_ids must not be empty")

    rows = tuple(_coerce_row(row) for row in assignments)
    if not rows:
        raise ValueError("at least one supplied split assignment is required")

    sample_ids: set[str] = set()
    for row in rows:
        if row.split not in allowed:
            raise ValueError(f"split {row.split!r} is not one of {allowed!r}")
        if row.sample_id in sample_ids:
            raise ValueError(f"duplicate sample_id: {row.sample_id!r}")
        sample_ids.add(row.sample_id)

    by_source = _source_metadata(rows)
    observed_sources = set(by_source)
    expected_sources = set(expected)
    missing = sorted(expected_sources - observed_sources)
    extra = sorted(observed_sources - expected_sources)
    if missing or extra:
        raise ValueError(
            f"source-trial coverage mismatch; missing={missing}, extra={extra}"
        )

    canonical_rows = tuple(
        sorted(
            rows,
            key=lambda row: (
                row.simultaneous_recording_group,
                row.session_id,
                row.source_trial_id,
                row.sample_id,
                row.split,
            ),
        )
    )
    return FrozenSplit(
        rows=canonical_rows,
        allowed_labels=allowed,
        expected_source_trial_ids=expected,
    )


def _coerce_row(row: SplitRow | Mapping[str, Any]) -> SplitRow:
    if isinstance(row, SplitRow):
        values = {
            "sample_id": row.sample_id,
            "source_trial_id": row.source_trial_id,
            "session_id": row.session_id,
            "simultaneous_recording_group": row.simultaneous_recording_group,
            "split": row.split,
        }
    else:
        required = (
            "sample_id",
            "source_trial_id",
            "session_id",
            "simultaneous_recording_group",
            "split",
        )
        missing = [name for name in required if name not in row]
        if missing:
            raise ValueError(f"split assignment is missing fields: {missing}")
        values = {name: row[name] for name in required}
    return SplitRow(
        **{name: _require_text(value, name) for name, value in values.items()}
    )


def _source_metadata(rows: Iterable[SplitRow]) -> dict[str, tuple[str, str, str]]:
    metadata_by_source: dict[str, tuple[str, str, str]] = {}
    for row in rows:
        metadata = (row.session_id, row.simultaneous_recording_group, row.split)
        existing = metadata_by_source.get(row.source_trial_id)
        if existing is not None and existing != metadata:
            raise ValueError(
                "all derivatives of one source_trial_id must share session, recording "
                f"group, and split; {row.source_trial_id!r} has {existing!r} and {metadata!r}"
            )
        metadata_by_source[row.source_trial_id] = metadata
    return metadata_by_source


def _require_text(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return value
