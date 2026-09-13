#!/usr/bin/env python3
"""Split-filtered table access for place195 development analyses.

Callers get rows only after ``source_trial_splits.csv`` has mapped the
``source_trial_id`` to an allowed development split. This module is deliberately
small: it is the guardrail, not a new data framework.
"""

from __future__ import annotations

import csv
import gzip
import json
from collections import Counter, defaultdict
from collections.abc import Iterable, Iterator, Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, TextIO, cast

DEVELOPMENT_SPLITS = frozenset({"train", "validation"})
TABLE_FILENAMES = {
    "trials": "trials.csv",
    "path_samples": "path_samples.csv.gz",
    "cue_counts": "cue_counts.csv.gz",
    "cue_spike_events": "cue_spike_events.csv.gz",
}


class SplitAccessError(ValueError):
    """Raised when a table cannot be proven split-safe before row yield."""


@dataclass
class SplitFilteredAudit:
    allowed_splits: tuple[str, ...]
    table_rows_seen_by_split: dict[str, Counter[str]] = field(
        default_factory=lambda: defaultdict(Counter)
    )
    table_rows_yielded_by_split: dict[str, Counter[str]] = field(
        default_factory=lambda: defaultdict(Counter)
    )
    table_rows_skipped_by_split: dict[str, Counter[str]] = field(
        default_factory=lambda: defaultdict(Counter)
    )

    def as_dict(self) -> dict[str, Any]:
        def clean(source: Mapping[str, Counter[str]]) -> dict[str, dict[str, int]]:
            return {
                table: dict(sorted(counter.items()))
                for table, counter in sorted(source.items())
            }

        forbidden_yielded = 0
        for counter in self.table_rows_yielded_by_split.values():
            forbidden_yielded += sum(
                count
                for split, count in counter.items()
                if split not in self.allowed_splits
            )
        return {
            "allowed_splits": list(self.allowed_splits),
            "rows_seen_by_split": clean(self.table_rows_seen_by_split),
            "rows_yielded_by_split": clean(self.table_rows_yielded_by_split),
            "rows_skipped_by_split": clean(self.table_rows_skipped_by_split),
            "forbidden_rows_yielded": forbidden_yielded,
        }


class SplitFilteredAccess:
    """Read place195 trial/path/cue rows through a mandatory split gate."""

    def __init__(
        self,
        import_dir: Path,
        split_dir: Path,
        allowed_splits: Iterable[str] = DEVELOPMENT_SPLITS,
    ) -> None:
        self.import_dir = Path(import_dir)
        self.split_dir = Path(split_dir)
        allowed = tuple(sorted(set(allowed_splits)))
        if not allowed:
            raise SplitAccessError("allowed_splits must be non-empty")
        if not set(allowed) <= DEVELOPMENT_SPLITS:
            raise SplitAccessError(
                "place195 development access forbids non-development splits; "
                f"got {allowed!r}"
            )
        self.allowed_splits = allowed
        self.split_rows = self._load_split_rows(
            self.split_dir / "source_trial_splits.csv"
        )
        self.split_by_source = {
            row["source_trial_id"]: row["split"] for row in self.split_rows
        }
        self.split_metadata_by_source = {
            row["source_trial_id"]: row for row in self.split_rows
        }
        self.allowed_source_ids = frozenset(
            source
            for source, split in self.split_by_source.items()
            if split in self.allowed_splits
        )
        self.split_hash = self._read_split_hash(self.split_dir / "split_summary.json")
        self.audit = SplitFilteredAudit(allowed_splits=self.allowed_splits)
        self._validated_tables: set[str] = set()

    def iter_trials(self) -> Iterator[dict[str, str]]:
        yield from self.iter_table("trials")

    def iter_path_samples(self) -> Iterator[dict[str, str]]:
        yield from self.iter_table("path_samples")

    def iter_cue_counts(self) -> Iterator[dict[str, str]]:
        yield from self.iter_table("cue_counts")

    def iter_cue_spike_events(self) -> Iterator[dict[str, str]]:
        yield from self.iter_table("cue_spike_events")

    def iter_table(self, table: str) -> Iterator[dict[str, str]]:
        try:
            filename = TABLE_FILENAMES[table]
        except KeyError as exc:
            raise SplitAccessError(f"unknown split-filtered table: {table}") from exc
        path = self.import_dir / filename
        self._validate_table_sources(table, path)
        with _open_text(path) as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames is None:
                raise SplitAccessError(f"missing CSV header: {path}")
            if "source_trial_id" not in reader.fieldnames:
                raise SplitAccessError(f"{path} lacks source_trial_id")
            for row_number, row in enumerate(reader, 2):
                source = row.get("source_trial_id", "")
                if source not in self.split_by_source:
                    raise SplitAccessError(
                        f"{table} row {row_number} has no split mapping for "
                        f"source_trial_id={source!r}"
                    )
                split = self.split_by_source[source]
                self.audit.table_rows_seen_by_split[table][split] += 1
                if split not in self.allowed_splits:
                    self.audit.table_rows_skipped_by_split[table][split] += 1
                    continue
                merged = dict(row)
                merged["split"] = split
                split_meta = self.split_metadata_by_source[source]
                for field_name in (
                    "split_block_id",
                    "candidate_recording_group",
                    "simultaneity_status",
                ):
                    if field_name in split_meta and field_name not in merged:
                        merged[field_name] = split_meta[field_name]
                self.audit.table_rows_yielded_by_split[table][split] += 1
                yield merged

    def table_header(self, table: str) -> tuple[str, ...]:
        try:
            filename = TABLE_FILENAMES[table]
        except KeyError as exc:
            raise SplitAccessError(f"unknown split-filtered table: {table}") from exc
        path = self.import_dir / filename
        with _open_text(path) as handle:
            reader = csv.reader(handle)
            try:
                return tuple(next(reader))
            except StopIteration as exc:
                raise SplitAccessError(f"missing CSV header: {path}") from exc

    def _validate_table_sources(self, table: str, path: Path) -> None:
        if table in self._validated_tables:
            return
        with _open_text(path) as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames is None:
                raise SplitAccessError(f"missing CSV header: {path}")
            if "source_trial_id" not in reader.fieldnames:
                raise SplitAccessError(f"{path} lacks source_trial_id")
            for row_number, row in enumerate(reader, 2):
                source = row.get("source_trial_id", "")
                if source not in self.split_by_source:
                    raise SplitAccessError(
                        f"{table} row {row_number} has no split mapping for "
                        f"source_trial_id={source!r}"
                    )
        self._validated_tables.add(table)

    @staticmethod
    def _load_split_rows(path: Path) -> list[dict[str, str]]:
        with _open_text(path) as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames is None:
                raise SplitAccessError(f"missing split CSV header: {path}")
            required = {"source_trial_id", "split"}
            missing = required - set(reader.fieldnames)
            if missing:
                raise SplitAccessError(f"split CSV missing fields {sorted(missing)}")
            rows = list(reader)
        seen: set[str] = set()
        for row in rows:
            source = row.get("source_trial_id", "")
            split = row.get("split", "")
            if not source:
                raise SplitAccessError("split CSV contains blank source_trial_id")
            if source in seen:
                raise SplitAccessError(f"duplicate split mapping for {source!r}")
            if not split:
                raise SplitAccessError(f"split CSV contains blank split for {source!r}")
            seen.add(source)
        return rows

    @staticmethod
    def _read_split_hash(path: Path) -> str:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return ""
        value = payload.get("split_hash", "")
        return value if isinstance(value, str) else ""


def _open_text(path: Path) -> TextIO:
    try:
        if path.suffix == ".gz":
            return cast(TextIO, gzip.open(path, "rt", encoding="utf-8", newline=""))
        return cast(TextIO, path.open("rt", encoding="utf-8", newline=""))
    except OSError as exc:
        raise SplitAccessError(f"could not open {path}") from exc
