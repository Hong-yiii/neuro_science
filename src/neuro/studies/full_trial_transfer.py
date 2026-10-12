#!/usr/bin/env python3
# pyright: reportMissingImports=false
"""CEBRA full-trial-transfer exploratory runner.

Bounded implementation for docs/reports/cebra-full-trial-transfer/protocol.md.
Biological fitting is refused unless a hash-bound prefit approval JSON is supplied.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import itertools
import json
import math
import platform
import random
import shutil
import sys
import time
import warnings
from collections import Counter, defaultdict
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, cast

import cebra.data
import numpy as np
import torch
from cebra.data import BatchIndex
from cebra.data.single_session import SingleSessionDataset
from sklearn.decomposition import PCA
from sklearn.exceptions import ConvergenceWarning
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    balanced_accuracy_score,
    log_loss,
    recall_score,  # noqa: F401 — preserve the historical module export
    roc_auc_score,
)
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

from neuro.execution import check_deadline, sha256_file, snapshot_sources
from neuro.legacy_adapters import (
    _codes_at,
    _times_at,
    bin_events,
    make_solver,
    read_ripple_trials,
    read_spiketrain,
    session_from_cell,
    spikes_in_window,
)
from neuro.place195_split_access import SplitFilteredAccess
from neuro.provenance import REPOSITORY_ROOT, study_sources

WORKTREE_ROOT = REPOSITORY_ROOT
CANONICAL_ROOT = Path("/home/hongyi-home-lab/neuro_science")
RUNTIME_PYTHON = CANONICAL_ROOT / "scratch/v6-v9-runtime/bin/python"
OUTPUT_ROOT = CANONICAL_ROOT / "outputs/cebra-full-trial-transfer-20260924"
MANAGEMENT_DIR = OUTPUT_ROOT / "management"
PROTOCOL_PATH = WORKTREE_ROOT / "docs/reports/cebra-full-trial-transfer/protocol.md"
IMPORT_DIR = (
    CANONICAL_ROOT
    / "outputs/prospective_path_first_run/place195-all-sessions-20260830-v4"
)
SPLIT_DIR = (
    CANONICAL_ROOT / "outputs/prospective_path_first_run/place195-splits-20260830-v3"
)
V6_DIR = (
    CANONICAL_ROOT
    / "outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/v6-reset-graph-support-audit"
)
SOURCE_NPZ = CANONICAL_ROOT / (
    "outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/"
    "v7-v8-neural-experiments/primary29_min3train_min1val/bin100ms/source_level_cue_tensors.npz"
)
SOURCE_NPZ_SHA256 = "688e3b52f69a872c7aec420da99ebb6f0b80464351ded3813b077cd7ed3cf567"
PRIMARY_COMPONENT = "D_N_R_T__N_R_M"
PRIMARY_ENDPOINT = "4->3"
LABELS = ("absent", "present")
LABEL_TO_INT = {"absent": 0, "present": 1}
INT_TO_LABEL = {0: "absent", 1: "present"}
BIN_WIDTH_S = 0.1
CUE_BINS = 10
ROWS_PER_CLASS = 64
SEEDS = (0, 1, 2)
NULL_SEEDS = tuple(range(50000, 50020))
RESAMPLE_SEED = 20260924
RESAMPLES = 200
CEBRA_ARMS = ("cue_time", "full_time", "cue_behavior", "full_behavior")
REPRESENTATIONS = ("raw290", "pca8", *CEBRA_ARMS)
DECODERS = ("logistic", "svc")
EXPECTED_ENCODERS = 252
EXPECTED_PCAS = 63
EXPECTED_READOUTS = 756
LOG2 = float(math.log(2.0))


@dataclass(frozen=True)
class SourceMeta:
    source_trial_id: str
    session_id: str
    split: str
    label: str
    trial_index: int


@dataclass(frozen=True)
class CueCohort:
    X: np.ndarray
    exposure: np.ndarray
    mask: np.ndarray
    source_trial_ids: list[str]
    source_session_ids: list[str]
    source_splits: list[str]
    source_labels: list[str]
    cell_ids: list[str]
    metas: list[SourceMeta]
    source_index: dict[str, int]


@dataclass(frozen=True)
class NavData:
    path: Path
    source_trial_ids: list[str]
    source_session_ids: list[str]
    source_labels: list[str]
    source_trial_indices: np.ndarray
    offsets: np.ndarray
    n_bins: np.ndarray
    counts_flat: np.ndarray
    exposure_flat: np.ndarray
    observed_mask_flat: np.ndarray
    cell_ids: list[str]
    source_index: dict[str, int]


@dataclass(frozen=True)
class RowBundle:
    X_cue: np.ndarray
    y: np.ndarray
    weights: np.ndarray | None
    manifest: list[dict[str, str]]
    plans: list[dict[str, Any]]


@dataclass(frozen=True)
class PairBank:
    cue_samples: np.ndarray
    cue_labels: np.ndarray
    cue_pairs: np.ndarray
    cue_samples_by_row: list[np.ndarray]
    cue_pairs_by_row: list[np.ndarray]
    nav_samples: np.ndarray
    nav_labels: np.ndarray
    nav_pairs: np.ndarray
    nav_samples_by_row: list[np.ndarray]
    nav_pairs_by_row: list[np.ndarray]
    row_labels: np.ndarray
    pair_lineage: list[dict[str, Any]]
    coverage_rows: list[dict[str, Any]]


class CebraVectorDataset(SingleSessionDataset):
    def __init__(
        self, X: np.ndarray, labels: np.ndarray, phase: np.ndarray, *, device: str
    ):
        super().__init__(device=device)
        self.neural = torch.as_tensor(X, dtype=torch.float32, device=device)
        self.labels = torch.as_tensor(labels, dtype=torch.long, device=device)
        self.phase = torch.as_tensor(phase, dtype=torch.long, device=device)
        # CEBRA configures the concrete model offset before iteration.
        self.offset = None  # pyright: ignore[reportAttributeAccessIssue]

    @property
    def input_dimension(self) -> int:
        return int(self.neural.shape[1])

    @property
    def discrete_index(self):
        return self.labels

    def __len__(self) -> int:
        return int(self.neural.shape[0])

    def __getitem__(self, index):
        index = index.to(self.device).long()
        if torch.any(index < 0) or torch.any(index >= len(self)):
            raise IndexError("CEBRA dataset index out of bounds")
        return self.neural[index].unsqueeze(-1)


def pad_groups(
    groups: Sequence[np.ndarray], *, device: str
) -> tuple[torch.Tensor, torch.Tensor]:
    if not groups:
        raise ValueError("empty row group bank")
    lengths = torch.as_tensor([len(g) for g in groups], dtype=torch.long, device=device)
    if torch.any(lengths <= 0):
        raise ValueError("row group bank contains an empty row")
    width = int(torch.max(lengths).item())
    padded = torch.zeros(
        (len(groups), width) + tuple(np.asarray(groups[0]).shape[1:]),
        dtype=torch.long,
        device=device,
    )
    for i, group in enumerate(groups):
        arr = torch.as_tensor(group, dtype=torch.long, device=device)
        padded[i, : len(group)] = arr
    return padded, lengths


class PhaseTimeLoader(cebra.data.Loader):
    """Row-uniform Time sampler with 50/50 cue-navigation phase draws."""

    def __init__(
        self,
        *,
        dataset: CebraVectorDataset,
        pair_groups_by_phase: Mapping[int, Sequence[np.ndarray]],
        sample_groups_by_phase: Mapping[int, Sequence[np.ndarray]],
        num_steps: int,
        batch_size: int,
        seed: int,
        phase_probs: Sequence[float] = (0.5, 0.5),
    ) -> None:
        self.dataset = dataset
        self.time_offset = 1
        self.num_steps = int(num_steps)
        self.batch_size = int(batch_size)
        super().__post_init__()
        self.phase_probs = torch.as_tensor(
            phase_probs, dtype=torch.float32, device=self.device
        )
        self.phase_probs = self.phase_probs / self.phase_probs.sum()
        self.pair_bank = {
            phase: pad_groups(groups, device=self.device)
            for phase, groups in pair_groups_by_phase.items()
        }
        self.sample_bank = {
            phase: pad_groups(groups, device=self.device)
            for phase, groups in sample_groups_by_phase.items()
        }
        self.n_rows = int(next(iter(self.pair_bank.values()))[1].numel())
        self.sample_counts = torch.zeros((3, len(dataset)), dtype=torch.long, device=self.device)
        self.generator = torch.Generator(device=self.device)
        self.generator.manual_seed(int(seed))
        self.reference_phase_counts = torch.zeros(
            2, dtype=torch.long, device=self.device
        )
        self.negative_phase_counts = torch.zeros(
            2, dtype=torch.long, device=self.device
        )
        self.reference_row_counts = torch.zeros(
            (2, self.n_rows), dtype=torch.long, device=self.device
        )
        self.negative_row_counts = torch.zeros(
            (2, self.n_rows), dtype=torch.long, device=self.device
        )

    def _draw_phase(self, n: int) -> torch.Tensor:
        return torch.multinomial(
            self.phase_probs, n, replacement=True, generator=self.generator
        )

    def _draw_rows(self, n: int) -> torch.Tensor:
        return torch.randint(
            self.n_rows, (n,), generator=self.generator, device=self.device
        )

    def _draw_from_groups(
        self, bank: tuple[torch.Tensor, torch.Tensor], rows: torch.Tensor
    ) -> torch.Tensor:
        padded, lengths = bank
        cols = torch.floor(
            torch.rand(rows.shape, generator=self.generator, device=self.device)
            * lengths[rows]
        ).long()
        return padded[rows, cols]

    def get_indices(self, num_samples: int) -> BatchIndex:
        phase = self._draw_phase(num_samples)
        neg_phase = self._draw_phase(num_samples)
        ref = torch.empty(num_samples, dtype=torch.long, device=self.device)
        pos = torch.empty(num_samples, dtype=torch.long, device=self.device)
        neg = torch.empty(num_samples, dtype=torch.long, device=self.device)
        for phase_value in self.pair_bank:
            m = phase == phase_value
            rows = self._draw_rows(int(m.sum().item()))
            if rows.numel():
                pairs = self._draw_from_groups(self.pair_bank[phase_value], rows)
                ref[m] = pairs[:, 0]
                pos[m] = pairs[:, 1]
                self.reference_row_counts[phase_value] += torch.bincount(
                    rows, minlength=self.n_rows
                )
            nm = neg_phase == phase_value
            neg_rows = self._draw_rows(int(nm.sum().item()))
            if neg_rows.numel():
                neg[nm] = self._draw_from_groups(
                    self.sample_bank[phase_value], neg_rows
                )
                self.negative_row_counts[phase_value] += torch.bincount(
                    neg_rows, minlength=self.n_rows
                )
        self.reference_phase_counts += torch.bincount(phase, minlength=2)
        self.negative_phase_counts += torch.bincount(neg_phase, minlength=2)
        if not torch.all(cast(CebraVectorDataset, self.dataset).labels[ref] == cast(CebraVectorDataset, self.dataset).labels[pos]):
            raise AssertionError("Time positive changed label")
        for counts, indices in zip(self.sample_counts, (ref, pos, neg), strict=True):
            counts.index_add_(0, indices, torch.ones_like(indices))
        return BatchIndex(reference=ref, positive=pos, negative=neg)

    def exposure_summary(self) -> dict[str, Any]:
        return {
            "reference_phase_counts": {
                "cue": int(self.reference_phase_counts[0]),
                "nav": int(self.reference_phase_counts[1]),
            },
            "negative_phase_counts": {
                "cue": int(self.negative_phase_counts[0]),
                "nav": int(self.negative_phase_counts[1]),
            },
            "reference_row_counts": self.reference_row_counts.detach()
            .cpu()
            .numpy()
            .astype(int)
            .tolist(),
            "negative_row_counts": self.negative_row_counts.detach()
            .cpu()
            .numpy()
            .astype(int)
            .tolist(),
        }


class PhaseBehaviorLoader(cebra.data.Loader):
    """Row-uniform Behavior sampler with same-label positives."""

    def __init__(
        self,
        *,
        dataset: CebraVectorDataset,
        sample_groups_by_phase: Mapping[int, Sequence[np.ndarray]],
        row_labels: np.ndarray,
        num_steps: int,
        batch_size: int,
        seed: int,
        phase_probs: Sequence[float] = (0.5, 0.5),
    ) -> None:
        self.dataset = dataset
        self.time_offset = 1
        self.num_steps = int(num_steps)
        self.batch_size = int(batch_size)
        super().__post_init__()
        self.sample_bank = {
            phase: pad_groups(groups, device=self.device)
            for phase, groups in sample_groups_by_phase.items()
        }
        self.row_labels = torch.as_tensor(
            row_labels, dtype=torch.long, device=self.device
        )
        self.rows_by_label = {
            label: torch.nonzero(self.row_labels == label, as_tuple=False).flatten()
            for label in (0, 1)
        }
        if any(int(v.numel()) == 0 for v in self.rows_by_label.values()):
            raise ValueError("Behavior sampler requires both labels")
        self.n_rows = int(self.row_labels.numel())
        self.sample_counts = torch.zeros((3, len(dataset)), dtype=torch.long, device=self.device)
        self.phase_probs = torch.as_tensor(
            phase_probs, dtype=torch.float32, device=self.device
        )
        self.phase_probs = self.phase_probs / self.phase_probs.sum()
        self.generator = torch.Generator(device=self.device)
        self.generator.manual_seed(int(seed))
        self.reference_phase_counts = torch.zeros(
            2, dtype=torch.long, device=self.device
        )
        self.positive_phase_counts = torch.zeros(
            2, dtype=torch.long, device=self.device
        )
        self.negative_phase_counts = torch.zeros(
            2, dtype=torch.long, device=self.device
        )
        self.reference_row_counts = torch.zeros(
            (2, self.n_rows), dtype=torch.long, device=self.device
        )
        self.positive_row_counts = torch.zeros(
            (2, self.n_rows), dtype=torch.long, device=self.device
        )
        self.negative_row_counts = torch.zeros(
            (2, self.n_rows), dtype=torch.long, device=self.device
        )

    def _draw_phase(self, n: int) -> torch.Tensor:
        return torch.multinomial(
            self.phase_probs, n, replacement=True, generator=self.generator
        )

    def _draw_any_rows(self, n: int) -> torch.Tensor:
        return torch.randint(
            self.n_rows, (n,), generator=self.generator, device=self.device
        )

    def _draw_label_rows(self, labels: torch.Tensor) -> torch.Tensor:
        out = torch.empty(labels.shape, dtype=torch.long, device=self.device)
        for label, rows in self.rows_by_label.items():
            m = labels == label
            if int(m.sum().item()):
                pick = torch.randint(
                    int(rows.numel()),
                    (int(m.sum().item()),),
                    generator=self.generator,
                    device=self.device,
                )
                out[m] = rows[pick]
        return out

    def _draw_from_groups(self, phase: int, rows: torch.Tensor) -> torch.Tensor:
        padded, lengths = self.sample_bank[phase]
        cols = torch.floor(
            torch.rand(rows.shape, generator=self.generator, device=self.device)
            * lengths[rows]
        ).long()
        return padded[rows, cols]

    def get_indices(self, num_samples: int) -> BatchIndex:
        ref_phase = self._draw_phase(num_samples)
        pos_phase = self._draw_phase(num_samples)
        neg_phase = self._draw_phase(num_samples)
        ref_rows = self._draw_any_rows(num_samples)
        pos_rows = self._draw_label_rows(self.row_labels[ref_rows])
        neg_rows = self._draw_any_rows(num_samples)
        ref = torch.empty(num_samples, dtype=torch.long, device=self.device)
        pos = torch.empty(num_samples, dtype=torch.long, device=self.device)
        neg = torch.empty(num_samples, dtype=torch.long, device=self.device)
        for phase in self.sample_bank:
            m = ref_phase == phase
            if int(m.sum().item()):
                ref[m] = self._draw_from_groups(phase, ref_rows[m])
                self.reference_row_counts[phase] += torch.bincount(
                    ref_rows[m], minlength=self.n_rows
                )
            pm = pos_phase == phase
            if int(pm.sum().item()):
                pos[pm] = self._draw_from_groups(phase, pos_rows[pm])
                self.positive_row_counts[phase] += torch.bincount(
                    pos_rows[pm], minlength=self.n_rows
                )
            nm = neg_phase == phase
            if int(nm.sum().item()):
                neg[nm] = self._draw_from_groups(phase, neg_rows[nm])
                self.negative_row_counts[phase] += torch.bincount(
                    neg_rows[nm], minlength=self.n_rows
                )
        self.reference_phase_counts += torch.bincount(ref_phase, minlength=2)
        self.positive_phase_counts += torch.bincount(pos_phase, minlength=2)
        self.negative_phase_counts += torch.bincount(neg_phase, minlength=2)
        if not torch.all(cast(CebraVectorDataset, self.dataset).labels[ref] == cast(CebraVectorDataset, self.dataset).labels[pos]):
            raise AssertionError("Behavior positive label mismatch")
        for counts, indices in zip(self.sample_counts, (ref, pos, neg), strict=True):
            counts.index_add_(0, indices, torch.ones_like(indices))
        return BatchIndex(reference=ref, positive=pos, negative=neg)

    def exposure_summary(self) -> dict[str, Any]:
        return {
            "reference_phase_counts": {
                "cue": int(self.reference_phase_counts[0]),
                "nav": int(self.reference_phase_counts[1]),
            },
            "positive_phase_counts": {
                "cue": int(self.positive_phase_counts[0]),
                "nav": int(self.positive_phase_counts[1]),
            },
            "negative_phase_counts": {
                "cue": int(self.negative_phase_counts[0]),
                "nav": int(self.negative_phase_counts[1]),
            },
            "reference_row_counts": self.reference_row_counts.detach()
            .cpu()
            .numpy()
            .astype(int)
            .tolist(),
            "positive_row_counts": self.positive_row_counts.detach()
            .cpu()
            .numpy()
            .astype(int)
            .tolist(),
            "negative_row_counts": self.negative_row_counts.detach()
            .cpu()
            .numpy()
            .astype(int)
            .tolist(),
        }


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def stable_hash(payload: Any) -> str:
    return sha256_bytes(
        json.dumps(jsonable(payload), sort_keys=True, separators=(",", ":")).encode()
    )


def ndarray_hash(array: np.ndarray) -> str:
    arr = np.ascontiguousarray(array)
    h = hashlib.sha256()
    h.update(str(arr.dtype).encode())
    h.update(np.asarray(arr.shape, dtype=np.int64).tobytes())
    h.update(arr.tobytes())
    return h.hexdigest()


def jsonable(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, dict):
        return {str(k): jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [jsonable(v) for v in value]
    return value


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(jsonable(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def append_jsonl(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(jsonable(payload), sort_keys=True) + "\n")


def write_csv(
    path: Path,
    rows: Sequence[Mapping[str, Any]],
    fieldnames: Sequence[str] | None = None,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if fieldnames is None:
        keys: list[str] = []
        for row in rows:
            for key in row:
                if key not in keys:
                    keys.append(key)
        fieldnames = keys
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(fieldnames), extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    k: json.dumps(v, sort_keys=True)
                    if isinstance(v, (dict, list, tuple))
                    else v
                    for k, v in row.items()
                }
            )


def write_csv_gz(
    path: Path, rows: Iterable[Mapping[str, Any]], fieldnames: Sequence[str]
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, "wt", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(fieldnames), extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    k: json.dumps(v, sort_keys=True)
                    if isinstance(v, (dict, list, tuple))
                    else v
                    for k, v in row.items()
                }
            )


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", newline="", encoding="utf-8") as f:  # type: ignore[arg-type]
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError(f"missing CSV header: {path}")
        return list(reader)


def git_state() -> dict[str, Any]:
    def run(args: list[str]) -> str:
        import subprocess

        try:
            return subprocess.check_output(
                ["git", *args], cwd=WORKTREE_ROOT, text=True, stderr=subprocess.STDOUT
            ).strip()
        except Exception as exc:  # pragma: no cover - defensive provenance
            return f"ERROR: {exc}"

    return {
        "head": run(["rev-parse", "HEAD"]),
        "branch": run(["branch", "--show-current"]),
        "status_short": run(["status", "--short"]),
    }


def package_versions() -> dict[str, Any]:
    versions = {
        "python": sys.version,
        "platform": platform.platform(),
        "torch": torch.__version__,
    }
    for name in ("numpy", "sklearn", "cebra"):
        try:
            mod = __import__(name)
            versions[name] = getattr(mod, "__version__", "unknown")
        except Exception as exc:  # pragma: no cover
            versions[name] = f"unavailable: {exc}"
    return versions


def ensure_fresh_dir(path: Path) -> None:
    if path.exists():
        raise FileExistsError(f"refusing to reuse existing output path: {path}")
    path.mkdir(parents=True)


def ensure_under(path: Path, root: Path) -> None:
    p = path.resolve()
    r = root.resolve()
    if p != r and r not in p.parents:
        raise ValueError(f"path {path} is not under {root}")


def source_npz_hash_checked(path: Path = SOURCE_NPZ) -> str:
    got = sha256_file(path)
    if got != SOURCE_NPZ_SHA256:
        raise RuntimeError(f"source NPZ hash mismatch: {got} != {SOURCE_NPZ_SHA256}")
    return got


def load_cue_cohort(path: Path = SOURCE_NPZ, v6_dir: Path = V6_DIR) -> CueCohort:
    source_npz_hash_checked(path)
    z = np.load(path, allow_pickle=False)
    required = {
        "X_source_cell_bin",
        "exposure_source_bin",
        "observed_source_cell_mask",
        "source_trial_ids",
        "source_session_ids",
        "source_splits",
        "source_labels",
        "cell_ids",
        "bin_width_s",
    }
    missing = required - set(z.files)
    if missing:
        raise RuntimeError(f"source NPZ missing keys: {sorted(missing)}")
    X = np.asarray(z["X_source_cell_bin"], dtype=np.float32)
    exposure = np.asarray(z["exposure_source_bin"], dtype=np.float32)
    mask = np.asarray(z["observed_source_cell_mask"], dtype=bool)
    source_trial_ids = [str(x) for x in z["source_trial_ids"].tolist()]
    source_session_ids = [str(x) for x in z["source_session_ids"].tolist()]
    source_splits = [str(x) for x in z["source_splits"].tolist()]
    source_labels = [str(x) for x in z["source_labels"].tolist()]
    cell_ids = [str(x) for x in z["cell_ids"].tolist()]
    if (
        X.shape != (104, 29, 10)
        or exposure.shape != (104, 10)
        or mask.shape != (104, 29)
    ):
        raise RuntimeError(
            f"unexpected source NPZ shapes: X={X.shape} exposure={exposure.shape} mask={mask.shape}"
        )
    if not np.isclose(float(np.asarray(z["bin_width_s"]).reshape(-1)[0]), BIN_WIDTH_S):
        raise RuntimeError("source NPZ bin_width_s is not 0.1")
    if len(set(source_trial_ids)) != len(source_trial_ids):
        raise RuntimeError("duplicate source_trial_id in source NPZ")
    expected_mask = np.asarray(
        [
            [session_from_cell(c) == sess for c in cell_ids]
            for sess in source_session_ids
        ],
        dtype=bool,
    )
    if not np.array_equal(mask, expected_mask):
        raise RuntimeError("source mask does not match same-session cell membership")

    original_splits = {r["source_trial_id"]: r["split"] for r in read_csv_rows(SPLIT_DIR / "source_trial_splits.csv")}
    if any(original_splits.get(sid) != split for sid, split in zip(source_trial_ids, source_splits, strict=True)):
        raise RuntimeError("cohort differs from original source split assignments")
    trial_rows = {
        r["source_trial_id"]: r
        for r in read_csv_rows(
            v6_dir / "v6a_geometry_mapping/trial_mapping_metrics.csv"
        )
    }
    membership_rows = {
        r["source_trial_id"]: r
        for r in read_csv_rows(
            v6_dir
            / "v6c_population_membership/selected_component_source_membership.csv"
        )
    }
    metas: list[SourceMeta] = []
    failures: list[str] = []
    for sid, sess, split, label in zip(
        source_trial_ids, source_session_ids, source_splits, source_labels, strict=True
    ):
        tr = trial_rows.get(sid)
        mem = membership_rows.get(sid)
        if tr is None or mem is None:
            failures.append(f"{sid}: missing trial mapping or membership")
            continue
        semantic_label = (
            "present"
            if PRIMARY_COMPONENT in tr.get("middle_directed_components", "").split(";")
            else "absent"
        )
        if tr.get("endpoint_pair") != PRIMARY_ENDPOINT:
            failures.append(f"{sid}: endpoint {tr.get('endpoint_pair')}")
        if (
            tr.get("complete_directed_path_coverage") != "true"
            or tr.get("absence_labels_allowed") != "true"
        ):
            failures.append(f"{sid}: coverage/absence flags invalid")
        if tr.get("session_id") != sess or tr.get("split") != split:
            failures.append(f"{sid}: mapping session/split mismatch")
        if (
            mem.get("session_id") != sess
            or mem.get("split") != split
            or mem.get("component_status") != label
        ):
            failures.append(f"{sid}: membership mismatch")
        if semantic_label != label:
            failures.append(f"{sid}: semantic label {semantic_label} != {label}")
        try:
            trial_index = int(tr["trial_index"])
        except Exception:
            failures.append(f"{sid}: invalid trial_index")
            trial_index = -1
        metas.append(SourceMeta(sid, sess, split, label, trial_index))
    if failures:
        raise RuntimeError(
            "cue cohort semantic validation failed: " + "; ".join(failures[:10])
        )
    counts = Counter(zip(source_splits, source_labels, strict=True))
    if (
        sum(v for (split, _label), v in counts.items() if split == "train") != 82
        or sum(v for (split, _label), v in counts.items() if split == "validation")
        != 22
    ):
        raise RuntimeError(f"unexpected cohort split counts: {counts}")
    if any(
        counts[(split, label)] <= 0
        for split in ("train", "validation")
        for label in LABELS
    ):
        raise RuntimeError(f"unexpected missing split/label cell: {counts}")
    return CueCohort(
        X=X,
        exposure=exposure,
        mask=mask,
        source_trial_ids=source_trial_ids,
        source_session_ids=source_session_ids,
        source_splits=source_splits,
        source_labels=source_labels,
        cell_ids=cell_ids,
        metas=metas,
        source_index={sid: i for i, sid in enumerate(source_trial_ids)},
    )


def source_files_manifest(
    import_dir: Path = IMPORT_DIR, canonical_root: Path = CANONICAL_ROOT
) -> dict[tuple[str, str, str], dict[str, str]]:
    rows = read_csv_rows(import_dir / "source_files.csv")
    out: dict[tuple[str, str, str], dict[str, str]] = {}
    for row in rows:
        role = row["role"]
        sess = row.get("session_id", "")
        cell = row.get("cell_id", "")
        path = canonical_root / row["path"]
        if not path.exists():
            raise FileNotFoundError(path)
        out[(role, sess, cell)] = row
    return out


def manifest_path(
    row: Mapping[str, str], canonical_root: Path = CANONICAL_ROOT
) -> Path:
    path = canonical_root / row["path"]
    ensure_under(path, canonical_root)
    return path


def parse_ripple_codes(text: str) -> tuple[int, ...]:
    return tuple(int(x) for x in text.split()) if text else ()


def build_training_nav_export(
    *,
    cohort: CueCohort,
    output_dir: Path,
    import_dir: Path = IMPORT_DIR,
    split_dir: Path = SPLIT_DIR,
    canonical_root: Path = CANONICAL_ROOT,
) -> dict[str, Any]:
    access = SplitFilteredAccess(
        import_dir, split_dir, allowed_splits=("train", "validation")
    )
    trial_rows = {r["source_trial_id"]: r for r in access.iter_trials()}
    for meta in cohort.metas:
        row = trial_rows.get(meta.source_trial_id, {})
        if row.get("split") != meta.split or row.get("session_id") != meta.session_id or row.get("qc_flags") != "" or row.get("outcome") != "success" or int(row.get("trial_index", -1)) != meta.trial_index:
            raise RuntimeError(f"cohort QC/trial identity mismatch: {meta.source_trial_id}")
    # Loading cue rows through the gate proves no unknown/test rows are silently accepted.
    cue_rows: dict[tuple[str, str], dict[str, str]] = {}
    for row in access.iter_cue_counts():
        key = (row["source_trial_id"], row["cell_id"])
        if (
            row["source_trial_id"] in cohort.source_index
            and row["cell_id"] in cohort.cell_ids
        ):
            cue_rows[key] = row
    manifest = source_files_manifest(import_dir, canonical_root)
    opened_files: list[dict[str, Any]] = []
    ripple_by_session = {}
    spikes_by_cell = {}
    raw_hash_failures: list[str] = []
    sessions = sorted(set(cohort.source_session_ids))
    selected_cells = cohort.cell_ids
    for sess in sessions:
        rrow = manifest.get(("ripple_markers", sess, ""))
        if rrow is None:
            raise RuntimeError(f"missing ripple source file manifest row for {sess}")
        path = manifest_path(rrow, canonical_root)
        got = sha256_file(path)
        if got != rrow["sha256"]:
            raw_hash_failures.append(f"{path}: {got} != {rrow['sha256']}")
        ripple_by_session[sess] = read_ripple_trials(path)
        opened_files.append(
            {
                "role": "ripple_markers",
                "session_id": sess,
                "path": str(path),
                "sha256": got,
                "manifest_sha256": rrow["sha256"],
            }
        )
    for cell in selected_cells:
        sess = session_from_cell(cell)
        srow = manifest.get(("spiketrain", sess, cell))
        if srow is None:
            raise RuntimeError(
                f"missing spiketrain source file manifest row for {cell}"
            )
        path = manifest_path(srow, canonical_root)
        got = sha256_file(path)
        if got != srow["sha256"]:
            raw_hash_failures.append(f"{path}: {got} != {srow['sha256']}")
        spikes_by_cell[cell] = read_spiketrain(path).timestamps_seconds
        opened_files.append(
            {
                "role": "spiketrain",
                "session_id": sess,
                "cell_id": cell,
                "path": str(path),
                "sha256": got,
                "manifest_sha256": srow["sha256"],
            }
        )
    if raw_hash_failures:
        raise RuntimeError("raw hash failures: " + "; ".join(raw_hash_failures[:5]))

    train_indices = [i for i, m in enumerate(cohort.metas) if m.split == "train"]
    counts_chunks: list[np.ndarray] = []
    exposure_chunks: list[np.ndarray] = []
    mask_chunks: list[np.ndarray] = []
    source_trial_ids: list[str] = []
    source_session_ids: list[str] = []
    source_labels: list[str] = []
    source_trial_indices: list[int] = []
    offsets = [0]
    n_bins_list: list[int] = []
    cue_mismatch_rows: list[dict[str, Any]] = []
    window_rows: list[dict[str, Any]] = []
    tiny_cue_tails = []
    cue_after_nominal_rows = []
    tiny_nav_tails = []
    for si in train_indices:
        meta = cohort.metas[si]
        trial_row = trial_rows.get(meta.source_trial_id)
        if trial_row is None:
            raise RuntimeError(
                f"missing split-gated trial row for {meta.source_trial_id}"
            )
        if trial_row.get("split") != "train":
            raise RuntimeError(
                f"audit selected non-train nav source: {meta.source_trial_id}"
            )
        ripple = ripple_by_session[meta.session_id]
        trial0 = meta.trial_index - 1
        codes = tuple(_codes_at(ripple, trial0) or ())
        times = _times_at(ripple, trial0)
        if times is None or len(times) != 3:
            raise RuntimeError(f"missing raw Ripple triplet for {meta.source_trial_id}")
        if codes != parse_ripple_codes(trial_row.get("ripple_codes", "")):
            raise RuntimeError(
                f"raw/imported Ripple code mismatch for {meta.source_trial_id}"
            )
        cue_start, cue_end, nav_end = map(float, times)
        cue_duration = cue_end - cue_start
        nav_duration = nav_end - cue_end
        if cue_duration <= 0 or nav_duration <= 0:
            raise RuntimeError(
                f"nonpositive cue/nav duration for {meta.source_trial_id}"
            )
        if abs(cue_duration - float(trial_row["ripple_cue_duration_s"])) > 1e-5:
            raise RuntimeError(f"cue duration mismatch for {meta.source_trial_id}")
        if abs(nav_duration - float(trial_row["ripple_nav_duration_s"])) > 1e-5:
            raise RuntimeError(f"nav duration mismatch for {meta.source_trial_id}")
        same_cell_idx = np.flatnonzero(cohort.mask[si])
        if not np.all(
            [
                session_from_cell(cohort.cell_ids[int(ci)]) == meta.session_id
                for ci in same_cell_idx
            ]
        ):
            raise RuntimeError(f"mask/session mismatch for {meta.source_trial_id}")
        recomputed_cue = np.zeros((len(cohort.cell_ids), CUE_BINS), dtype=np.float32)
        cue_exposure: np.ndarray | None = None
        for ci in same_cell_idx:
            cell = cohort.cell_ids[int(ci)]
            cue_spikes = spikes_in_window(spikes_by_cell[cell], cue_start, cue_end)
            rel = cue_spikes - cue_start
            counts, exposure, omitted = bin_events(
                rel, cue_duration, BIN_WIDTH_S, nominal=1.0
            )
            if omitted:
                cue_after_nominal_rows.append(
                    {
                        "source_trial_id": meta.source_trial_id,
                        "cell_id": cell,
                        "omitted_after_nominal_1s": int(omitted),
                    }
                )
            recomputed_cue[int(ci)] = counts
            cue_exposure = exposure
            crow = cue_rows.get((meta.source_trial_id, cell))
            if crow is None or int(crow["cue_spike_count"]) != int(cue_spikes.size):
                cue_mismatch_rows.append(
                    {
                        "source_trial_id": meta.source_trial_id,
                        "cell_id": cell,
                        "reason": "cue_counts_table_mismatch",
                    }
                )
        if cue_exposure is None:
            raise RuntimeError(f"no observed cells for {meta.source_trial_id}")
        if not np.array_equal(
            recomputed_cue[same_cell_idx], cohort.X[si, same_cell_idx, :]
        ):
            where = np.argwhere(
                recomputed_cue[same_cell_idx] != cohort.X[si, same_cell_idx, :]
            )
            cue_mismatch_rows.append(
                {
                    "source_trial_id": meta.source_trial_id,
                    "reason": "source_npz_count_mismatch",
                    "first_mismatch": where[0].tolist() if where.size else [],
                }
            )
        if not np.allclose(cue_exposure, cohort.exposure[si], atol=1e-6):
            cue_mismatch_rows.append(
                {
                    "source_trial_id": meta.source_trial_id,
                    "reason": "source_npz_exposure_mismatch",
                }
            )
        if cue_duration < 1.0:
            tiny_cue_tails.append(
                {
                    "source_trial_id": meta.source_trial_id,
                    "cue_duration_s": cue_duration,
                    "clipped_tail_s": 1.0 - cue_duration,
                }
            )

        n_nav = int(math.floor((nav_duration + 1e-12) / BIN_WIDTH_S))
        if n_nav < 2:
            raise RuntimeError(
                f"source has fewer than two complete nav bins: {meta.source_trial_id}"
            )
        tail = nav_duration - n_nav * BIN_WIDTH_S
        if tail > 1e-9:
            tiny_nav_tails.append(
                {
                    "source_trial_id": meta.source_trial_id,
                    "nav_tail_s": tail,
                    "nav_duration_s": nav_duration,
                }
            )
        nav_counts = np.full((n_nav, len(cohort.cell_ids)), np.nan, dtype=np.float32)
        nav_exp = np.full((n_nav,), BIN_WIDTH_S, dtype=np.float32)
        nav_mask = np.zeros((n_nav, len(cohort.cell_ids)), dtype=bool)
        for ci in same_cell_idx:
            cell = cohort.cell_ids[int(ci)]
            rel = (
                spikes_in_window(
                    spikes_by_cell[cell], cue_end, cue_end + n_nav * BIN_WIDTH_S
                )
                - cue_end
            )
            bins = np.floor(rel / BIN_WIDTH_S).astype(int)
            valid = (bins >= 0) & (bins < n_nav)
            binc = np.bincount(bins[valid], minlength=n_nav).astype(np.float32)
            nav_counts[:, int(ci)] = binc
            nav_mask[:, int(ci)] = True
        counts_chunks.append(nav_counts)
        exposure_chunks.append(nav_exp)
        mask_chunks.append(nav_mask)
        source_trial_ids.append(meta.source_trial_id)
        source_session_ids.append(meta.session_id)
        source_labels.append(meta.label)
        source_trial_indices.append(meta.trial_index)
        n_bins_list.append(n_nav)
        offsets.append(offsets[-1] + n_nav)
        window_rows.append(
            {
                "source_trial_id": meta.source_trial_id,
                "session_id": meta.session_id,
                "split": meta.split,
                "label": meta.label,
                "trial_index": meta.trial_index,
                "cue_start_s": cue_start,
                "cue_end_s": cue_end,
                "nav_end_s": nav_end,
                "cue_duration_s": cue_duration,
                "nav_duration_s": nav_duration,
                "complete_nav_bins_100ms": n_nav,
                "discarded_nav_tail_s": max(0.0, tail),
                "observed_cells": int(len(same_cell_idx)),
            }
        )
    if cue_mismatch_rows:
        write_csv(output_dir / "cue_parity_failures.csv", cue_mismatch_rows)
        raise RuntimeError(
            f"cue recount parity failed for {len(cue_mismatch_rows)} rows"
        )
    counts_flat = np.concatenate(counts_chunks, axis=0)
    exposure_flat = np.concatenate(exposure_chunks, axis=0)
    mask_flat = np.concatenate(mask_chunks, axis=0)
    offsets_arr = np.asarray(offsets, dtype=np.int64)
    n_bins_arr = np.asarray(n_bins_list, dtype=np.int64)
    if (
        counts_flat.shape[0] != int(np.sum(n_bins_arr))
        or counts_flat.shape != mask_flat.shape
    ):
        raise AssertionError("nav flat array shape mismatch")
    nav_path = output_dir / "training_nav_source_data.npz"
    np.savez_compressed(
        nav_path,
        nav_counts_flat=counts_flat,
        nav_exposure_flat=exposure_flat,
        nav_observed_mask_flat=mask_flat,
        nav_offsets=offsets_arr,
        nav_n_bins=n_bins_arr,
        source_trial_ids=np.asarray(source_trial_ids),
        source_session_ids=np.asarray(source_session_ids),
        source_labels=np.asarray(source_labels),
        source_splits=np.asarray(["train"] * len(source_trial_ids)),
        source_trial_indices=np.asarray(source_trial_indices, dtype=np.int64),
        cell_ids=np.asarray(cohort.cell_ids),
        bin_width_s=np.asarray([BIN_WIDTH_S], dtype=np.float32),
    )
    write_csv(output_dir / "training_source_windows.csv", window_rows)
    write_csv(output_dir / "opened_raw_files.csv", opened_files)
    summary = {
        "created_utc": utc_now(),
        "source_npz": str(SOURCE_NPZ),
        "source_npz_sha256": SOURCE_NPZ_SHA256,
        "training_sources": len(source_trial_ids),
        "validation_sources_with_no_nav_export": sum(
            1 for m in cohort.metas if m.split == "validation"
        ),
        "cell_count": len(cohort.cell_ids),
        "sessions": sorted(set(source_session_ids)),
        "nav_complete_bins_min_median_max": [
            int(np.min(n_bins_arr)),
            float(np.median(n_bins_arr)),
            int(np.max(n_bins_arr)),
        ],
        "nav_tail_sources": len(tiny_nav_tails),
        "cue_under_one_second_sources": len(tiny_cue_tails),
        "cue_spikes_after_nominal_1s_rows": len(cue_after_nominal_rows),
        "tiny_cue_tails": tiny_cue_tails[:10],
        "cue_after_nominal_first10": cue_after_nominal_rows[:10],
        "tiny_nav_tails_first10": tiny_nav_tails[:10],
        "opened_file_count": len(opened_files),
        "training_nav_npz": str(nav_path),
        "training_nav_npz_sha256": sha256_file(nav_path),
        "split_gate_audit": access.audit.as_dict(),
        "counts_hash": ndarray_hash(counts_flat),
        "mask_hash": ndarray_hash(mask_flat),
    }
    write_json(output_dir / "audit_manifest.json", summary)
    write_data_audit_md(output_dir / "data-audit.md", summary, window_rows)
    write_design_audit_md(output_dir / "design-audit.md", summary)
    return summary


def write_data_audit_md(
    path: Path, summary: Mapping[str, Any], window_rows: Sequence[Mapping[str, Any]]
) -> None:
    bins = summary["nav_complete_bins_min_median_max"]
    text = f"""# CEBRA full-trial-transfer data audit

Generated: {summary["created_utc"]}

Status: PASS, no fitting performed.

- Source NPZ: `{summary["source_npz"]}`
- Source NPZ SHA256: `{summary["source_npz_sha256"]}`
- Training navigation export: `{summary["training_nav_npz"]}`
- Training navigation export SHA256: `{summary["training_nav_npz_sha256"]}`
- Training sources exported: {summary["training_sources"]}; validation navigation sources exported: 0
- Validation cue arrays remain accepted-NPZ only: {summary["validation_sources_with_no_nav_export"]} validation sources.
- Sessions: {", ".join(summary["sessions"])}
- Cells: {summary["cell_count"]}
- Complete native 100 ms navigation bins min/median/max: {bins[0]} / {bins[1]} / {bins[2]}
- Cue <1 s windows clipped at cue offset: {summary["cue_under_one_second_sources"]}
- Navigation partial-tail sources audited/discarded: {summary["nav_tail_sources"]}
- Raw files opened and hash-checked: {summary["opened_file_count"]}

No validation navigation arrays/counts/model inputs were written. Raw MAT reads are session-wide in memory; selected windows analyzed are exactly the whitelisted training source windows in `training_source_windows.csv`.
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_design_audit_md(path: Path, summary: Mapping[str, Any]) -> None:
    text = f"""# CEBRA full-trial-transfer design audit

Generated: {summary["created_utc"]}

Status: PASS, implementation gates mirror the frozen protocol.

- Native navigation bins are ragged source storage plus deterministic pair-bank sampling; no warp, padding, or physical path alignment.
- Full arms sample cue/navigation phases 50/50; cue readout remains cue-only.
- Shared neural scaler is fit on training cue bins within each world/seed.
- Manifest row IDs are class-qualified; validation lineage uses `(label, product_row)`.
- Source-label shuffles record actual changed-label fraction separately from stratum movability.
- Biological fitting remains locked behind prefit approval JSON with code/protocol/input/audit hashes.
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def cmd_audit(args: argparse.Namespace) -> None:
    out = Path(args.output_dir)
    ensure_fresh_dir(out)
    cohort = load_cue_cohort(args.source_npz, args.v6_dir)
    summary = build_training_nav_export(
        cohort=cohort,
        output_dir=out,
        import_dir=args.import_dir,
        split_dir=args.split_dir,
        canonical_root=args.canonical_root,
    )
    print(json.dumps(jsonable(summary), indent=2, sort_keys=True))


def load_nav_data(path: Path, cohort: CueCohort | None = None) -> NavData:
    z = np.load(path, allow_pickle=False)
    ids = [str(x) for x in z["source_trial_ids"].tolist()]
    sessions = [str(x) for x in z["source_session_ids"].tolist()]
    labels = [str(x) for x in z["source_labels"].tolist()]
    cells = [str(x) for x in z["cell_ids"].tolist()]
    splits = [str(x) for x in z["source_splits"].tolist()]
    if len(ids) != len(set(ids)):
        raise RuntimeError("nav data contains duplicate source_trial_ids")
    if set(splits) != {"train"}:
        raise RuntimeError("nav data must contain train sources only")
    if cohort is not None:
        if cells != cohort.cell_ids:
            raise RuntimeError("nav data cell_ids mismatch cue cohort")
        expected_train = {m.source_trial_id for m in cohort.metas if m.split == "train"}
        if set(ids) != expected_train:
            raise RuntimeError(
                "nav data source IDs are not the complete training cohort"
            )
        if len(expected_train) == 82 and len(ids) != 82:
            raise RuntimeError(
                "nav data source IDs are not the complete 82-source training cohort"
            )
        for sid, sess, label in zip(ids, sessions, labels, strict=True):
            ci = cohort.source_index.get(sid)
            if (
                ci is None
                or cohort.source_session_ids[ci] != sess
                or cohort.source_splits[ci] != "train"
                or cohort.source_labels[ci] != label
            ):
                raise RuntimeError(f"nav source not in accepted training cohort: {sid}")
    n_bins = np.asarray(z["nav_n_bins"], dtype=np.int64)
    offsets = np.asarray(z["nav_offsets"], dtype=np.int64)
    counts = np.asarray(z["nav_counts_flat"], dtype=np.float32)
    exposure = np.asarray(z["nav_exposure_flat"], dtype=np.float32)
    mask = np.asarray(z["nav_observed_mask_flat"], dtype=bool)
    if (
        len(ids) != len(n_bins)
        or len(offsets) != len(ids) + 1
        or offsets[0] != 0
        or offsets[-1] != counts.shape[0]
    ):
        raise RuntimeError("nav data offsets/counts mismatch")
    if not np.array_equal(np.diff(offsets), n_bins):
        raise RuntimeError("nav data offsets do not match per-source n_bins")
    if (
        counts.shape != mask.shape
        or counts.shape[0] != exposure.shape[0]
        or counts.shape[1] != len(cells)
    ):
        raise RuntimeError("nav data count/mask/exposure shapes mismatch")
    if not np.all(np.isfinite(exposure)) or not np.allclose(exposure, BIN_WIDTH_S):
        raise RuntimeError("nav exposure must be finite complete 100 ms bins")
    if int(np.min(n_bins)) < 2:
        raise RuntimeError("nav data contains source with <2 complete bins")
    if cohort is not None:
        expected_mask = np.asarray(
            [[session_from_cell(c) == sess for c in cells] for sess in sessions],
            dtype=bool,
        )
        expanded = np.repeat(expected_mask, n_bins, axis=0)
        if not np.array_equal(mask, expanded):
            raise RuntimeError(
                "nav observed mask does not match same-session cell membership"
            )
        if not np.all(np.isfinite(counts[mask])) or np.any(~np.isnan(counts[~mask])):
            raise RuntimeError(
                "nav counts must be finite for observed cells and NaN off-session"
            )
    return NavData(
        path=path,
        source_trial_ids=ids,
        source_session_ids=sessions,
        source_labels=labels,
        source_trial_indices=np.asarray(z["source_trial_indices"], dtype=np.int64),
        offsets=offsets,
        n_bins=n_bins,
        counts_flat=counts,
        exposure_flat=exposure,
        observed_mask_flat=mask,
        cell_ids=cells,
        source_index={sid: i for i, sid in enumerate(ids)},
    )


def shuffled_source_labels(
    metas: Sequence[SourceMeta], *, seed: int
) -> tuple[dict[str, str], dict[str, Any]]:
    rng = random.Random(seed)
    grouped: dict[tuple[str, str], list[SourceMeta]] = defaultdict(list)
    for meta in metas:
        grouped[(meta.session_id, meta.split)].append(meta)
    out: dict[str, str] = {}
    actual_changed = 0
    movable_by_stratum = 0
    total = 0
    stratum_rows = []
    for (session_id, split), rows in sorted(grouped.items()):
        labels = [m.label for m in rows]
        shuffled = labels[:]
        rng.shuffle(shuffled)
        changed = sum(a != b for a, b in zip(labels, shuffled, strict=True))
        movable = len(rows) if len(set(labels)) >= 2 and len(rows) >= 2 else 0
        actual_changed += changed
        movable_by_stratum += movable
        total += len(rows)
        for meta, label in zip(rows, shuffled, strict=True):
            out[meta.source_trial_id] = label
        stratum_rows.append(
            {
                "session_id": session_id,
                "split": split,
                "n": len(rows),
                "changed": changed,
                "movable_by_stratum": movable,
            }
        )
    info = {
        "seed": seed,
        "group_fields": ["session_id", "split"],
        "source_count": total,
        "actual_changed_count": actual_changed,
        "actual_changed_fraction": actual_changed / total if total else 0.0,
        "movable_by_stratum_count": movable_by_stratum,
        "movable_by_stratum_fraction": movable_by_stratum / total if total else 0.0,
        "shuffled_label_hash": stable_hash(out),
        "strata": stratum_rows,
    }
    return out, info


def cell_sessions(cell_ids: Sequence[str]) -> np.ndarray:
    return np.asarray([session_from_cell(c) for c in cell_ids])


def eligible_by_session(
    metas: Sequence[SourceMeta],
    cell_ids: Sequence[str],
    *,
    split: str,
    label: str,
    shuffled_labels: Mapping[str, str] | None = None,
) -> dict[str, list[str]]:
    sessions = sorted(set(cell_sessions(cell_ids)))
    out = {s: [] for s in sessions}
    for meta in metas:
        lab = (
            shuffled_labels.get(meta.source_trial_id, meta.label)
            if shuffled_labels
            else meta.label
        )
        if meta.split == split and lab == label and meta.session_id in out:
            out[meta.session_id].append(meta.source_trial_id)
    empty = [s for s, ids in out.items() if not ids]
    if empty:
        raise RuntimeError(f"cannot assemble {split}/{label}; empty sessions {empty}")
    return out


def make_training_plans(
    metas: Sequence[SourceMeta],
    cell_ids: Sequence[str],
    *,
    rows_per_class: int,
    seed: int,
    shuffled_labels: Mapping[str, str] | None = None,
) -> list[dict[str, Any]]:
    rng = np.random.default_rng(seed)
    sessions = sorted(set(cell_sessions(cell_ids)))
    plans = []
    for label in LABELS:
        by_session = eligible_by_session(
            metas, cell_ids, split="train", label=label, shuffled_labels=shuffled_labels
        )
        for r in range(rows_per_class):
            sources = {sess: str(rng.choice(by_session[sess])) for sess in sessions}
            plans.append(
                {
                    "split": "train",
                    "label": label,
                    "row_kind": "sampled",
                    "row_number": r,
                    "row_id": f"train:{label}:sample{r:05d}",
                    "sources": sources,
                }
            )
    return plans


def make_validation_plans(
    metas: Sequence[SourceMeta],
    cell_ids: Sequence[str],
    *,
    shuffled_labels: Mapping[str, str] | None = None,
) -> tuple[list[dict[str, Any]], dict[str, dict[str, int]]]:
    sessions = sorted(set(cell_sessions(cell_ids)))
    plans = []
    support: dict[str, dict[str, int]] = {}
    for label in LABELS:
        by_session = eligible_by_session(
            metas,
            cell_ids,
            split="validation",
            label=label,
            shuffled_labels=shuffled_labels,
        )
        support[label] = {sess: len(by_session[sess]) for sess in sessions}
        for product_row, combo in enumerate(
            itertools.product(*[by_session[sess] for sess in sessions])
        ):
            sources = dict(zip(sessions, combo, strict=True))
            plans.append(
                {
                    "split": "validation",
                    "label": label,
                    "row_kind": "product",
                    "product_row": product_row,
                    "row_id": f"validation:{label}:product{product_row:05d}",
                    "manifest_key": f"{label}|{product_row}",
                    "sources": sources,
                }
            )
    if len(sessions) == 7 and len(plans) != 30:
        raise RuntimeError(f"expected 30 validation product rows, got {len(plans)}")
    return plans, support


def materialize_cue_rows(
    cohort: CueCohort, plans: Sequence[Mapping[str, Any]]
) -> RowBundle:
    sessions_by_cell = cell_sessions(cohort.cell_ids)
    X = np.empty((len(plans), len(cohort.cell_ids), CUE_BINS), dtype=np.float32)
    y = np.empty(len(plans), dtype=np.int64)
    manifest: list[dict[str, str]] = []
    for ri, plan in enumerate(plans):
        label = str(plan["label"])
        y[ri] = LABEL_TO_INT[label]
        X[ri] = np.nan
        for sess, sid in dict(plan["sources"]).items():
            si = cohort.source_index[sid]
            if cohort.source_splits[si] != plan["split"] or cohort.source_session_ids[si] != sess:
                raise RuntimeError("assembly source split/session mismatch")
            cidx = np.flatnonzero(sessions_by_cell == sess)
            if not np.all(cohort.mask[si, cidx]):
                raise RuntimeError(f"observed cue mask failure for {sid}/{sess}")
            X[ri, cidx, :] = cohort.X[si, cidx, :]
            manifest.append(
                {
                    "split": str(plan["split"]),
                    "label": label,
                    "row_id": str(plan["row_id"]),
                    "row_kind": str(plan["row_kind"]),
                    "product_row": str(plan.get("product_row", "")),
                    "manifest_key": str(plan.get("manifest_key", "")),
                    "session_id": sess,
                    "source_trial_id": sid,
                }
            )
        if np.isnan(X[ri]).any():
            raise RuntimeError(f"pseudo row has unavailable cells: {plan['row_id']}")
    weights = exact_class_weights(y) if len(y) else None
    return RowBundle(
        X_cue=X, y=y, weights=weights, manifest=manifest, plans=[dict(p) for p in plans]
    )


def exact_class_weights(y: np.ndarray) -> np.ndarray:
    weights = np.zeros(len(y), dtype=np.float64)
    for cls in (0, 1):
        idx = np.flatnonzero(y == cls)
        if len(idx):
            weights[idx] = 0.5 / len(idx)
    return weights


def fit_cue_scaler(train_cue: np.ndarray) -> StandardScaler:
    flat = train_cue.transpose(0, 2, 1).reshape(-1, train_cue.shape[1])
    return StandardScaler().fit(flat)


def transform_cue_samples(X_cue: np.ndarray, scaler: StandardScaler) -> np.ndarray:
    rows, cells, bins = X_cue.shape
    flat = X_cue.transpose(0, 2, 1).reshape(rows * bins, cells)
    tx = np.asarray(scaler.transform(flat), dtype=np.float32)
    return tx.reshape(rows, bins, cells).transpose(0, 2, 1)


def flatten_cue(X_cue_scaled: np.ndarray) -> np.ndarray:
    return X_cue_scaled.reshape(X_cue_scaled.shape[0], -1)


def source_nav_slice(
    nav: NavData, sid: str
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    si = nav.source_index[sid]
    a = int(nav.offsets[si])
    b = int(nav.offsets[si + 1])
    return nav.counts_flat[a:b], nav.exposure_flat[a:b], nav.observed_mask_flat[a:b]


def build_pair_bank(
    train_bundle: RowBundle,
    nav: NavData,
    scaler: StandardScaler,
    cell_ids: Sequence[str],
) -> PairBank:
    sessions_by_cell = cell_sessions(cell_ids)
    cue_vectors = []
    cue_labels = []
    cue_pairs = []
    cue_samples_by_row: list[np.ndarray] = []
    cue_pairs_by_row: list[np.ndarray] = []
    row_labels: list[int] = []
    for row, label in zip(
        transform_cue_samples(train_bundle.X_cue, scaler), train_bundle.y, strict=True
    ):
        base = len(cue_vectors)
        row_labels.append(int(label))
        for b in range(CUE_BINS):
            cue_vectors.append(row[:, b])
            cue_labels.append(int(label))
        row_samples = np.arange(base, base + CUE_BINS, dtype=np.int64)
        row_pairs = np.asarray(
            [(base + b, base + b + 1) for b in range(CUE_BINS - 1)], dtype=np.int64
        )
        cue_samples_by_row.append(row_samples)
        cue_pairs_by_row.append(row_pairs)
        cue_pairs.extend(row_pairs.tolist())

    nav_vectors = []
    nav_labels = []
    nav_pairs = []
    nav_samples_by_row: list[np.ndarray] = []
    nav_pairs_by_row: list[np.ndarray] = []
    pair_lineage: list[dict[str, Any]] = []
    coverage_rows: list[dict[str, Any]] = []
    for plan in train_bundle.plans:
        label_int = LABEL_TO_INT[str(plan["label"])]
        sources = dict(plan["sources"])
        per_session: dict[str, tuple[np.ndarray, np.ndarray]] = {}
        max_pairs = 0
        for sess, sid in sources.items():
            counts, _exposure, mask = source_nav_slice(nav, sid)
            cidx = np.flatnonzero(sessions_by_cell == sess)
            if not np.all(mask[:, cidx]):
                raise RuntimeError(f"nav mask failure for {sid}/{sess}")
            per_session[sess] = (counts, cidx)
            max_pairs = max(max_pairs, counts.shape[0] - 1)
        if max_pairs < 1:
            raise RuntimeError(f"no nav adjacent pairs for {plan['row_id']}")
        coverage: dict[tuple[str, int], int] = defaultdict(int)
        row_nav_samples: list[int] = []
        row_nav_pairs: list[tuple[int, int]] = []
        for j in range(max_pairs):
            q = (j + 0.5) / max_pairs
            anchor = np.empty(len(cell_ids), dtype=np.float32)
            positive = np.empty(len(cell_ids), dtype=np.float32)
            block_rows = []
            for sess, (counts, cidx) in per_session.items():
                n_pairs = counts.shape[0] - 1
                native = min(n_pairs - 1, int(math.floor(q * n_pairs)))
                anchor[cidx] = counts[native, cidx]
                positive[cidx] = counts[native + 1, cidx]
                sid = sources[sess]
                coverage[(sid, native)] += 1
                block_rows.append(
                    {
                        "session_id": sess,
                        "source_trial_id": sid,
                        "anchor_native_bin": native,
                        "positive_native_bin": native + 1,
                    }
                )
            base = len(nav_vectors)
            nav_vectors.append(
                np.asarray(scaler.transform(anchor.reshape(1, -1)), dtype=np.float32).reshape(-1)
            )
            nav_vectors.append(
                np.asarray(scaler.transform(positive.reshape(1, -1)), dtype=np.float32).reshape(-1)
            )
            nav_labels.extend([label_int, label_int])
            nav_pairs.append((base, base + 1))
            row_nav_samples.extend([base, base + 1])
            row_nav_pairs.append((base, base + 1))
            pair_lineage.append(
                {
                    "row_id": plan["row_id"],
                    "label": plan["label"],
                    "pair_bank_index": j,
                    "phase_q": q,
                    "blocks": block_rows,
                }
            )
        for sess, sid in sources.items():
            n_pairs = source_nav_slice(nav, sid)[0].shape[0] - 1
            missing = [k for k in range(n_pairs) if coverage[(sid, k)] == 0]
            if missing:
                raise AssertionError(
                    f"pair bank coverage failed for {sid}: {missing[:5]}"
                )
            coverage_rows.append(
                {
                    "row_id": plan["row_id"],
                    "session_id": sess,
                    "source_trial_id": sid,
                    "native_adjacent_pairs": n_pairs,
                    "represented_pairs": n_pairs,
                    "max_pair_bank_L": max_pairs,
                }
            )
        nav_samples_by_row.append(np.asarray(row_nav_samples, dtype=np.int64))
        nav_pairs_by_row.append(np.asarray(row_nav_pairs, dtype=np.int64))
    cue_samples = np.asarray(cue_vectors, dtype=np.float32)
    nav_samples = np.asarray(nav_vectors, dtype=np.float32)
    return PairBank(
        cue_samples=cue_samples,
        cue_labels=np.asarray(cue_labels, dtype=np.int64),
        cue_pairs=np.asarray(cue_pairs, dtype=np.int64),
        cue_samples_by_row=cue_samples_by_row,
        cue_pairs_by_row=cue_pairs_by_row,
        nav_samples=nav_samples,
        nav_labels=np.asarray(nav_labels, dtype=np.int64),
        nav_pairs=np.asarray(nav_pairs, dtype=np.int64),
        nav_samples_by_row=nav_samples_by_row,
        nav_pairs_by_row=nav_pairs_by_row,
        row_labels=np.asarray(row_labels, dtype=np.int64),
        pair_lineage=pair_lineage,
        coverage_rows=coverage_rows,
    )


def cebra_dataset_for_arm(
    arm: str,
    train_scaled_cue: np.ndarray,
    y: np.ndarray,
    pair_bank: PairBank | None,
    *,
    device: str,
) -> tuple[CebraVectorDataset, dict[str, Any], dict[str, Any]]:
    cue_flat = train_scaled_cue.transpose(0, 2, 1).reshape(
        -1, train_scaled_cue.shape[1]
    )
    cue_labels = np.repeat(y, CUE_BINS)
    cue_samples_by_row = [
        np.arange(r * CUE_BINS, (r + 1) * CUE_BINS, dtype=np.int64)
        for r in range(len(y))
    ]
    cue_pairs_by_row = [
        np.asarray(
            [(r * CUE_BINS + b, r * CUE_BINS + b + 1) for b in range(CUE_BINS - 1)],
            dtype=np.int64,
        )
        for r in range(len(y))
    ]
    if arm.startswith("cue_"):
        phase = np.zeros(len(cue_flat), dtype=np.int64)
        ds = CebraVectorDataset(cue_flat, cue_labels, phase, device=device)
        payload = {
            "pair_groups_by_phase": {0: cue_pairs_by_row},
            "sample_groups_by_phase": {0: cue_samples_by_row},
            "row_labels": np.asarray(y, dtype=np.int64),
            "phase_probs": (1.0,),
        }
        return (
            ds,
            payload,
            {
                "sample_count": len(cue_flat),
                "cue_sample_count": len(cue_flat),
                "nav_sample_count": 0,
            },
        )
    if pair_bank is None:
        raise ValueError("full arm requires pair bank")
    X = np.concatenate([pair_bank.cue_samples, pair_bank.nav_samples], axis=0)
    labels = np.concatenate([pair_bank.cue_labels, pair_bank.nav_labels], axis=0)
    phase = np.concatenate(
        [
            np.zeros(len(pair_bank.cue_samples), dtype=np.int64),
            np.ones(len(pair_bank.nav_samples), dtype=np.int64),
        ]
    )
    ds = CebraVectorDataset(X, labels, phase, device=device)
    nav_offset = len(pair_bank.cue_samples)
    payload = {
        "pair_groups_by_phase": {
            0: pair_bank.cue_pairs_by_row,
            1: [g + nav_offset for g in pair_bank.nav_pairs_by_row],
        },
        "sample_groups_by_phase": {
            0: pair_bank.cue_samples_by_row,
            1: [g + nav_offset for g in pair_bank.nav_samples_by_row],
        },
        "row_labels": pair_bank.row_labels,
        "phase_probs": (0.5, 0.5),
    }
    return (
        ds,
        payload,
        {
            "sample_count": int(len(X)),
            "cue_sample_count": int(len(pair_bank.cue_samples)),
            "nav_sample_count": int(len(pair_bank.nav_samples)),
        },
    )


def set_all_seeds(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def train_encoder(
    *,
    arm: str,
    train_scaled_cue: np.ndarray,
    y_train: np.ndarray,
    pair_bank: PairBank | None,
    seed: int,
    outdir: Path,
    iterations: int,
    batch_size: int,
    lr: float,
    hidden: int,
    dim: int,
    device: str,
    deadline: float | None = None,
) -> tuple[Any, dict[str, Any]]:
    set_all_seeds(seed)
    ds, loader_payload, data_info = cebra_dataset_for_arm(
        arm, train_scaled_cue, y_train, pair_bank, device=device
    )
    solver = make_solver(ds.input_dimension, dim, hidden, lr, device)
    initial_hash = stable_hash({k: ndarray_hash(v.detach().cpu().numpy())
                               for k, v in solver.model.state_dict().items()})
    ds.configure_for(solver.model)
    if "time" in arm:
        loader = PhaseTimeLoader(
            dataset=ds,
            pair_groups_by_phase=loader_payload["pair_groups_by_phase"],
            sample_groups_by_phase=loader_payload["sample_groups_by_phase"],
            num_steps=iterations,
            batch_size=batch_size,
            seed=seed + 1009,
            phase_probs=loader_payload["phase_probs"],
        )
    else:
        loader = PhaseBehaviorLoader(
            dataset=ds,
            sample_groups_by_phase=loader_payload["sample_groups_by_phase"],
            row_labels=loader_payload["row_labels"],
            num_steps=iterations,
            batch_size=batch_size,
            seed=seed + 2003,
            phase_probs=loader_payload["phase_probs"],
        )
    solver._set_fitted_params(loader)
    solver.model.train()
    outdir.mkdir(parents=True, exist_ok=True)
    if torch.cuda.is_available():
        torch.cuda.reset_peak_memory_stats()
    t0 = time.time()
    checkpoints = []
    checkpoint_steps = {1, iterations}
    for step in (250, 500, 750):
        if step <= iterations:
            checkpoint_steps.add(step)
    # CEBRA 0.6.1's generator __iter__ is annotated as Batch, not Iterator.
    for step, batch in enumerate(cast(Iterable[Any], loader), start=1):
        if step % 100 == 1:
            check_deadline(deadline)
        solver.step(batch)
        if step in checkpoint_steps:
            ckpt = outdir / f"checkpoint_step{step:04d}.pth"
            torch.save(solver.state_dict(), ckpt)
            checkpoints.append(str(ckpt))
    wall = time.time() - t0
    loss_rows = [
        {
            "step": i + 1,
            "total": float(t),
            "pos": float(p),
            "neg": float(n),
            "temperature": float(temp),
        }
        for i, (t, p, n, temp) in enumerate(
            zip(
                solver.log["total"],
                solver.log["pos"],
                solver.log["neg"],
                solver.log["temperature"],
                strict=True,
            )
        )
    ]
    if not loss_rows or not np.isfinite([r["total"] for r in loss_rows]).all():
        raise RuntimeError(f"nonfinite CEBRA loss for {arm}")
    write_csv(outdir / "loss_trace.csv", loss_rows)
    final_ckpt = outdir / "checkpoint_final.pth"
    torch.save(solver.state_dict(), final_ckpt)
    exposure_path = outdir / "sample_exposure_counts.npz"
    np.savez_compressed(exposure_path, counts=loader.sample_counts.detach().cpu().numpy())
    info = {
        "sample_exposure_sha256": sha256_file(exposure_path),
        "arm": arm,
        "initial_model_sha256": initial_hash,
        "seed": seed,
        "iterations": iterations,
        "batch_size": batch_size,
        "lr": lr,
        "hidden": hidden,
        "dim": dim,
        "device": device,
        "wall_seconds": wall,
        "loss_first": loss_rows[0]["total"],
        "loss_last": loss_rows[-1]["total"],
        "loss_last100_mean": float(
            np.mean([x["total"] for x in loss_rows[-min(100, len(loss_rows)) :]])
        ),
        "checkpoints": checkpoints,
        "checkpoint_final": str(final_ckpt),
        "checkpoint_final_sha256": sha256_file(final_ckpt),
        "data_info": data_info,
        "exposure_summary": loader.exposure_summary()
        if hasattr(loader, "exposure_summary")
        else {},
    }
    write_json(outdir / "fit_info.json", info)
    return solver, info


def embed_cue(solver: Any, X_scaled_cue: np.ndarray, *, device: str) -> np.ndarray:
    rows, cells, bins = X_scaled_cue.shape
    flat = (
        X_scaled_cue.transpose(0, 2, 1).reshape(rows * bins, cells).astype(np.float32)
    )
    solver.model.eval()
    with torch.no_grad():
        z = (
            solver.transform(torch.as_tensor(flat, dtype=torch.float32, device=device))
            .detach()
            .cpu()
            .numpy()
            .astype(np.float32)
        )
    return z.reshape(rows, bins, -1).reshape(rows, bins * z.shape[1])


def raw_features(X_scaled_cue: np.ndarray) -> np.ndarray:
    return X_scaled_cue.reshape(X_scaled_cue.shape[0], -1).astype(np.float32)


def fit_pca_features(
    train_scaled_cue: np.ndarray, *others: np.ndarray
) -> tuple[PCA, list[np.ndarray]]:
    rows, cells, bins = train_scaled_cue.shape
    pooled = train_scaled_cue.transpose(0, 2, 1).reshape(rows * bins, cells)
    pca = PCA(n_components=8, svd_solver="full", whiten=False, random_state=0).fit(
        pooled
    )
    return pca, [apply_pca_object(pca, arr) for arr in (train_scaled_cue, *others)]


def apply_pca_object(pca: PCA, arr: np.ndarray) -> np.ndarray:
    r, c, b = arr.shape
    flat = arr.transpose(0, 2, 1).reshape(r * b, c)
    return pca.transform(flat).astype(np.float32).reshape(r, b, 8).reshape(r, b * 8)


def save_pca_state(path: Path, pca: PCA) -> None:
    np.savez_compressed(
        path,
        components=np.asarray(pca.components_),
        mean=pca.mean_,
        explained_variance_ratio=pca.explained_variance_ratio_,
    )


def apply_pca_state(path: Path, arr: np.ndarray) -> np.ndarray:
    state = np.load(path, allow_pickle=False)
    r, c, b = arr.shape
    flat = arr.transpose(0, 2, 1).reshape(r * b, c)
    z = (flat - state["mean"]) @ state["components"].T
    return z.astype(np.float32).reshape(r, b, 8).reshape(r, b * 8)


def fit_decoder(
    readout: str, Xtr: np.ndarray, ytr: np.ndarray, Xva: np.ndarray, *, outdir: Path
) -> tuple[
    np.ndarray, np.ndarray, np.ndarray, np.ndarray, Any, StandardScaler
]:
    scaler = StandardScaler().fit(Xtr)
    assert scaler.mean_ is not None and scaler.scale_ is not None
    Xtr_s = scaler.transform(Xtr)
    Xva_s = scaler.transform(Xva)
    if readout == "logistic":
        with warnings.catch_warnings():
            warnings.simplefilter("error", ConvergenceWarning)
            model = LogisticRegression(
                C=0.01,
                solver="liblinear",
                class_weight="balanced",
                max_iter=1000,
                random_state=0,
            ).fit(Xtr_s, ytr)
        prob_tr = model.predict_proba(Xtr_s)[:, 1]
        prob_va = model.predict_proba(Xva_s)[:, 1]
        pred_tr = model.predict(Xtr_s)
        pred_va = model.predict(Xva_s)
    elif readout == "svc":
        with warnings.catch_warnings():
            warnings.simplefilter("error", ConvergenceWarning)
            model = SVC(
                C=1.0,
                gamma="scale",
                class_weight="balanced",
                probability=False,
                max_iter=100000,
                random_state=0,
            ).fit(Xtr_s, ytr)
        if getattr(model, "fit_status_", 0) != 0:
            raise RuntimeError("SVC did not converge")
        pred_tr = model.predict(Xtr_s)
        pred_va = model.predict(Xva_s)
        prob_tr = model.decision_function(Xtr_s)
        prob_va = model.decision_function(Xva_s)
    else:
        raise ValueError(readout)
    state_path = outdir / f"{readout}_decoder_state.npz"
    outdir.mkdir(parents=True, exist_ok=True)
    if readout == "logistic":
        np.savez_compressed(
            state_path,
            readout=readout,
            scaler_mean=scaler.mean_,
            scaler_scale=scaler.scale_,
            coef=model.coef_,
            intercept=model.intercept_,
            classes=model.classes_,
        )
    else:
        np.savez_compressed(
            state_path,
            readout=readout,
            scaler_mean=scaler.mean_,
            scaler_scale=scaler.scale_,
            support_vectors=model.support_vectors_,
            dual_coef=np.asarray(model.dual_coef_),
            intercept=model.intercept_,
            classes=model.classes_,
            gamma=np.asarray([model._gamma]),
        )
    write_json(
        outdir / f"{readout}_decoder_state.json",
        {"path": str(state_path), "sha256": sha256_file(state_path)},
    )
    return pred_tr, prob_tr, pred_va, prob_va, model, scaler


def predict_decoder_state(
    state_path: Path, X: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    state = np.load(state_path, allow_pickle=False)
    readout = str(state["readout"].reshape(-1)[0])
    # Match sklearn's in-place float32 rounding before the library's float64 kernel.
    Xs = np.array(X, copy=True)
    Xs -= state["scaler_mean"]
    Xs /= state["scaler_scale"]
    classes = state["classes"].astype(int)
    if readout == "logistic":
        z = Xs @ state["coef"].reshape(-1) + float(state["intercept"].reshape(-1)[0])
        score = 1.0 / (1.0 + np.exp(-z))
        pred = np.where(z > 0.0, classes[1], classes[0])
        return pred.astype(int), score.astype(float)
    if readout == "svc":
        sv = state["support_vectors"]
        gamma = float(state["gamma"].reshape(-1)[0])
        diff = Xs[:, None, :] - sv[None, :, :]
        kernel = np.exp(-gamma * np.sum(diff * diff, axis=2))
        score = kernel @ state["dual_coef"].reshape(-1) + float(
            state["intercept"].reshape(-1)[0]
        )
        pred = np.where(score >= 0.0, classes[1], classes[0])
        return pred.astype(int), score.astype(float)
    raise RuntimeError(f"unknown decoder state readout {readout!r}")


def metric_row(
    y: np.ndarray,
    pred: np.ndarray,
    score: np.ndarray,
    *,
    weights: np.ndarray | None,
    readout: str,
    prefix: Mapping[str, Any],
) -> dict[str, Any]:
    row = dict(prefix)
    row["n"] = int(len(y))
    row["positive_fraction"] = float(np.mean(y)) if len(y) else math.nan
    if readout == "logistic":
        prob = np.clip(score.astype(float), 1e-9, 1 - 1e-9)
        row["balanced_log_loss"] = float(
            log_loss(
                y,
                np.column_stack([1 - prob, prob]),
                labels=[0, 1],
                sample_weight=weights,
            )
        )
        row["balanced_brier"] = (
            float(np.average((score - y) ** 2, weights=weights))
            if weights is not None
            else float(np.mean((score - y) ** 2))
        )
        ranking = score
    else:
        row["balanced_log_loss"] = ""
        row["balanced_brier"] = ""
        ranking = score.astype(float)
    row["balanced_accuracy"] = float(
        balanced_accuracy_score(y, pred, sample_weight=weights)
    )
    for label_int, label_name in INT_TO_LABEL.items():
        selected = y == label_int
        row[f"recall_{label_name}"] = float(np.average(pred[selected] == label_int, weights=None if weights is None else weights[selected]))
    try:
        row["auroc"] = float(roc_auc_score(y, ranking, sample_weight=weights))
    except ValueError:
        row["auroc"] = ""
    if not all(
        v == "" or np.isfinite(v) for k, v in row.items() if isinstance(v, float)
    ):
        raise RuntimeError(f"nonfinite metric row: {row}")
    return row


def prediction_rows(
    y: np.ndarray,
    pred: np.ndarray,
    score: np.ndarray,
    *,
    split: str,
    readout: str,
    prefix: Mapping[str, Any],
    plans: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    rows = []
    for i, (yy, pp, ss) in enumerate(zip(y, pred, score, strict=True)):
        plan = plans[i]
        rows.append(
            {
                **prefix,
                "split": split,
                "readout": readout,
                "row_index": i,
                "row_id": plan["row_id"],
                "label": INT_TO_LABEL[int(yy)],
                "pred_label": INT_TO_LABEL[int(pp)],
                "score_name": "prob_present" if readout == "logistic" else "svc_margin",
                "score": float(ss),
                "sources": ";".join(
                    f"{k}={v}" for k, v in sorted(dict(plan["sources"]).items())
                ),
                "manifest_key": plan.get("manifest_key", ""),
                "product_row": plan.get("product_row", ""),
            }
        )
    return rows


def locked_config(args: argparse.Namespace | None = None) -> dict[str, Any]:
    return {
        "protocol": "cebra-full-trial-transfer-20260924",
        "source_npz_sha256": SOURCE_NPZ_SHA256,
        "rows_per_class": ROWS_PER_CLASS,
        "seeds": list(SEEDS),
        "null_seeds": list(NULL_SEEDS),
        "cebra_arms": list(CEBRA_ARMS),
        "representations": list(REPRESENTATIONS),
        "decoders": list(DECODERS),
        "bin_width_s": BIN_WIDTH_S,
        "cue_bins": CUE_BINS,
        "encoder": {
            "dim": 8,
            "hidden": 32,
            "lr": 3e-4,
            "batch_size": 256,
            "iterations": 1000,
            "temperature": 1,
            "offset": 1,
        },
        "decoder_logistic": {
            "C": 0.01,
            "solver": "liblinear",
            "class_weight": "balanced",
            "max_iter": 1000,
            "random_state": 0,
        },
        "decoder_svc": {
            "C": 1.0,
            "gamma": "scale",
            "class_weight": "balanced",
            "probability": False,
            "max_iter": 100000,
            "random_state": 0,
        },
        "expected_accounting": {
            "encoders": EXPECTED_ENCODERS,
            "pcas": EXPECTED_PCAS,
            "readouts": EXPECTED_READOUTS,
        },
        "limits": {"fit_cap_minutes": 90, "output_cap_gib": 10, "threads": 2},
    }


def approval_facts(
    audit_manifest: Path, config: Mapping[str, Any] | None = None
) -> dict[str, str]:
    frozen_config = locked_config() if config is None else config
    return {
        "code_sha256": sha256_file(Path(__file__)),
        "protocol_sha256": sha256_file(PROTOCOL_PATH),
        "source_npz_sha256": source_npz_hash_checked(SOURCE_NPZ),
        "audit_manifest_sha256": sha256_file(audit_manifest),
        "navigation_sha256": sha256_file(audit_manifest.parent / "training_nav_source_data.npz"),
        "helper_code_sha256": stable_hash(helper_hashes()),
        "input_manifests_sha256": stable_hash(input_manifest_hashes()),
        "locked_config_sha256": stable_hash(frozen_config),
    }


def helper_paths() -> dict[str, Path]:
    return study_sources(Path(__file__))


def helper_hashes() -> dict[str, str]:
    return {name: sha256_file(path) for name, path in helper_paths().items()}


def input_manifest_hashes() -> dict[str, str]:
    paths = [IMPORT_DIR / "source_files.csv", SPLIT_DIR / "source_trial_splits.csv",
             SPLIT_DIR / "split_summary.json",
             V6_DIR / "v6a_geometry_mapping/trial_mapping_metrics.csv",
             V6_DIR / "v6c_population_membership/selected_component_source_membership.csv"]
    return {str(path.relative_to(CANONICAL_ROOT)): sha256_file(path) for path in paths}


def validate_run_config(args: argparse.Namespace) -> dict[str, Any]:
    config = locked_config()
    for key in ("iterations", "batch_size", "lr", "hidden", "dim"):
        if getattr(args, key) != config["encoder"][key]:
            raise RuntimeError(f"biological {key} differs from locked protocol")
    return config


def require_prefit_approval(
    path: Path, audit_manifest: Path, config: Mapping[str, Any] | None = None
) -> dict[str, Any]:
    approval = read_json(path)
    if approval.get("approved") is not True:
        raise RuntimeError("prefit approval JSON lacks approved=true")
    facts = approval_facts(audit_manifest, config)
    mismatches = {
        k: {"expected_current": v, "approval": approval.get(k)}
        for k, v in facts.items()
        if approval.get(k) != v
    }
    if mismatches:
        raise RuntimeError(f"prefit approval hash mismatch: {mismatches}")
    return {"approval": approval, "facts": facts}


def journal(path: Path, event: str, **payload: Any) -> None:
    append_jsonl(path, {"utc": utc_now(), "event": event, **payload})


def run_world_seed(
    *,
    world_name: str,
    world_index: int,
    seed: int,
    cohort: CueCohort,
    nav: NavData,
    shuffled_labels: Mapping[str, str] | None,
    outdir: Path,
    journal_path: Path,
    iterations: int,
    batch_size: int,
    lr: float,
    hidden: int,
    dim: int,
    device: str,
    deadline: float | None = None,
) -> dict[str, Any]:
    prefix = {"world": world_name, "world_index": world_index, "seed": seed}
    train_plans = make_training_plans(
        cohort.metas,
        cohort.cell_ids,
        rows_per_class=ROWS_PER_CLASS,
        seed=seed,
        shuffled_labels=shuffled_labels,
    )
    val_plans, support = make_validation_plans(
        cohort.metas, cohort.cell_ids, shuffled_labels=shuffled_labels
    )
    train_bundle = materialize_cue_rows(cohort, train_plans)
    val_bundle = materialize_cue_rows(cohort, val_plans)
    scaler = fit_cue_scaler(train_bundle.X_cue)
    assert scaler.mean_ is not None and scaler.scale_ is not None and scaler.var_ is not None
    Xtr_scaled = transform_cue_samples(train_bundle.X_cue, scaler)
    Xva_scaled = transform_cue_samples(val_bundle.X_cue, scaler)
    world_dir = outdir / "worlds" / f"{world_index:02d}_{world_name}" / f"seed{seed}"
    world_dir.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        world_dir / "cue_scaler.npz",
        mean=scaler.mean_,
        scale=scaler.scale_,
        var=scaler.var_,
        n_samples_seen=np.asarray([scaler.n_samples_seen_]),
    )
    write_json(world_dir / "validation_support.json", support)
    write_csv(world_dir / "train_manifest.csv", train_bundle.manifest)
    write_csv(world_dir / "validation_manifest.csv", val_bundle.manifest)
    pair_bank = build_pair_bank(train_bundle, nav, scaler, cohort.cell_ids)
    with gzip.open(world_dir / "pair_lineage.jsonl.gz", "wt", encoding="utf-8") as f:
        for row in pair_bank.pair_lineage:
            f.write(json.dumps(jsonable(row), sort_keys=True) + "\n")
    write_csv(world_dir / "pair_coverage.csv", pair_bank.coverage_rows)

    metrics_rows: list[dict[str, Any]] = []
    pred_rows: list[dict[str, Any]] = []
    readout_count = 0
    encoder_count = 0
    pca_count = 0
    journal(journal_path, "pca_started", world=world_name, seed=seed)
    features: dict[str, tuple[np.ndarray, np.ndarray]] = {
        "raw290": (raw_features(Xtr_scaled), raw_features(Xva_scaled))
    }
    pca, pca_features = fit_pca_features(Xtr_scaled, Xva_scaled)
    pca_count += 1
    journal(journal_path, "pca_completed", world=world_name, seed=seed)
    features["pca8"] = (pca_features[0], pca_features[1])
    pca_path = world_dir / "pca8_state.npz"
    save_pca_state(pca_path, pca)
    write_json(
        world_dir / "pca8_state.json",
        {
            "path": str(pca_path),
            "sha256": sha256_file(pca_path),
            "explained_variance_ratio": pca.explained_variance_ratio_.tolist(),
        },
    )

    initial_hashes = set()
    for arm in CEBRA_ARMS:
        check_deadline(deadline)
        fit_dir = world_dir / "encoders" / arm
        journal(journal_path, "encoder_started", world=world_name, seed=seed, arm=arm)
        solver, info = train_encoder(
            arm=arm,
            train_scaled_cue=Xtr_scaled,
            y_train=train_bundle.y,
            pair_bank=pair_bank if arm.startswith("full_") else None,
            seed=seed,
            outdir=fit_dir,
            iterations=iterations,
            batch_size=batch_size,
            lr=lr,
            hidden=hidden,
            dim=dim,
            device=device,
            deadline=deadline,
        )
        encoder_count += 1
        initial_hashes.add(info["initial_model_sha256"])
        if len(initial_hashes) != 1:
            raise RuntimeError("paired encoders did not share initialization")
        Ztr = embed_cue(solver, Xtr_scaled, device=device)
        Zva = embed_cue(solver, Xva_scaled, device=device)
        np.savez_compressed(
            fit_dir / "cue_embeddings.npz",
            Z_train=Ztr,
            Z_validation=Zva,
            y_train=train_bundle.y,
            y_validation=val_bundle.y,
        )
        features[arm] = (Ztr, Zva)
        journal(
            journal_path,
            "encoder_completed",
            world=world_name,
            seed=seed,
            arm=arm,
            info=info,
        )

    for rep, (Xtr, Xva) in features.items():
        for readout in DECODERS:
            dec_dir = world_dir / "readouts" / rep / readout
            journal(
                journal_path,
                "readout_started",
                world=world_name,
                seed=seed,
                representation=rep,
                readout=readout,
            )
            ptr, strn, pva, sva, model, _dscaler = fit_decoder(
                readout, Xtr, train_bundle.y, Xva, outdir=dec_dir
            )
            readout_count += 1
            metrics_rows.append(
                metric_row(
                    train_bundle.y,
                    ptr,
                    strn,
                    weights=exact_class_weights(train_bundle.y),
                    readout=readout,
                    prefix={
                        **prefix,
                        "split": "train",
                        "representation": rep,
                        "readout": readout,
                    },
                )
            )
            metrics_rows.append(
                metric_row(
                    val_bundle.y,
                    pva,
                    sva,
                    weights=val_bundle.weights,
                    readout=readout,
                    prefix={
                        **prefix,
                        "split": "validation",
                        "representation": rep,
                        "readout": readout,
                    },
                )
            )
            pred_rows.extend(
                prediction_rows(
                    train_bundle.y,
                    ptr,
                    strn,
                    split="train",
                    readout=readout,
                    prefix={**prefix, "representation": rep},
                    plans=train_bundle.plans,
                )
            )
            pred_rows.extend(
                prediction_rows(
                    val_bundle.y,
                    pva,
                    sva,
                    split="validation",
                    readout=readout,
                    prefix={**prefix, "representation": rep},
                    plans=val_bundle.plans,
                )
            )
            journal(
                journal_path,
                "readout_completed",
                world=world_name,
                seed=seed,
                representation=rep,
                readout=readout,
            )
    write_csv(world_dir / "metrics.csv", metrics_rows)
    write_csv_gz(world_dir / "predictions.csv.gz", pred_rows, list(pred_rows[0]))
    return {
        "metrics": metrics_rows,
        "predictions": pred_rows,
        "counts": {
            "encoders": encoder_count,
            "pcas": pca_count,
            "readouts": readout_count,
        },
    }


def summarize_results(
    metrics_rows: Sequence[Mapping[str, Any]],
    predictions: Sequence[Mapping[str, Any]],
    outdir: Path,
) -> dict[str, Any]:
    def matching(rep: str, seed: int, world: str, field: str) -> float:
        rows = [
            r
            for r in metrics_rows
            if r["world"] == world
            and r["split"] == "validation"
            and r["readout"] == "logistic"
            and r["representation"] == rep
            and str(r["seed"]) == str(seed)
        ]
        if len(rows) != 1:
            raise RuntimeError(f"missing metric {field} {world}/{seed}/{rep}")
        return float(rows[0][field])

    observed_seeds = sorted(
        {
            int(r["seed"])
            for r in metrics_rows
            if r["world"] == "observed"
            and r["split"] == "validation"
            and r["readout"] == "logistic"
            and r["representation"] == "cue_time"
        }
    )
    worlds = sorted(
        {str(r["world"]) for r in metrics_rows if str(r["world"]) != "observed"}
    )
    observed_time_gains = [
        matching("cue_time", s, "observed", "balanced_log_loss")
        - matching("full_time", s, "observed", "balanced_log_loss")
        for s in observed_seeds
    ]
    observed_behavior_gains = [
        matching("cue_behavior", s, "observed", "balanced_log_loss")
        - matching("full_behavior", s, "observed", "balanced_log_loss")
        for s in observed_seeds
    ]
    obs_mean = float(np.mean(observed_time_gains)) if observed_time_gains else math.nan
    null_means = []
    null_max2 = []
    for world in worlds:
        tg = [
            matching("cue_time", s, world, "balanced_log_loss")
            - matching("full_time", s, world, "balanced_log_loss")
            for s in observed_seeds
        ]
        bg = [
            matching("cue_behavior", s, world, "balanced_log_loss")
            - matching("full_behavior", s, world, "balanced_log_loss")
            for s in observed_seeds
        ]
        null_means.append(float(np.mean(tg)))
        null_max2.append(float(max(np.mean(tg), np.mean(bg))))
    p_time = (
        (1 + sum(v >= obs_mean - 1e-12 for v in null_means)) / (1 + len(null_means))
        if null_means
        else None
    )
    full_loss_mean = float(
        np.mean(
            [
                matching("full_time", s, "observed", "balanced_log_loss")
                for s in observed_seeds
            ]
        )
    )
    full_ba_mean = float(
        np.mean(
            [
                matching("full_time", s, "observed", "balanced_accuracy")
                for s in observed_seeds
            ]
        )
    )
    full_auroc_mean = float(
        np.mean([matching("full_time", s, "observed", "auroc") for s in observed_seeds])
    )
    lead = bool(
        obs_mean >= 0.01
        and full_loss_mean < LOG2
        and full_ba_mean > 0.5
        and full_auroc_mean > 0.5
    )
    observed_max2 = max(obs_mean, float(np.mean(observed_behavior_gains)))
    absolute_references = {}
    for objective in ("time", "behavior"):
        observed = LOG2 - float(np.mean([matching(f"full_{objective}", s, "observed", "balanced_log_loss") for s in observed_seeds]))
        null_values = [LOG2 - float(np.mean([matching(f"full_{objective}", s, w, "balanced_log_loss") for s in observed_seeds])) for w in worlds]
        absolute_references[objective] = {
            "observed_baseline_minus_full_loss": observed,
            "null_baseline_minus_full_losses": null_values,
            "inclusive_tail": (1 + sum(x >= observed - 1e-12 for x in null_values)) / (1 + len(null_values)) if null_values else None,
        }
    summary = {
        "absolute_full_arm_no_association_references": absolute_references,
        "observed_max_two_objectives_mean_gain": observed_max2,
        "null_max_two_objectives_inclusive_tail": (1 + sum(x >= observed_max2 - 1e-12 for x in null_max2)) / (1 + len(null_max2)) if null_max2 else None,
        "observed_time_logistic_seed_gains_cue_minus_full_loss": observed_time_gains,
        "observed_time_logistic_mean_gain": obs_mean,
        "observed_behavior_logistic_seed_gains_cue_minus_full_loss": observed_behavior_gains,
        "null_time_logistic_mean_gains": null_means,
        "null_time_logistic_inclusive_p_ge_observed": p_time,
        "null_max_two_objectives_mean_gains": null_max2,
        "full_time_logistic_loss_mean": full_loss_mean,
        "full_time_logistic_ba_mean": full_ba_mean,
        "full_time_logistic_auroc_mean": full_auroc_mean,
        "constant_reference": {"log_loss": LOG2, "balanced_accuracy": 0.5},
        "worthwhile_exploratory_followup_lead": lead,
        "criteria": {
            "gain_ge_0p01": obs_mean >= 0.01,
            "full_loss_lt_log2": full_loss_mean < LOG2,
            "full_ba_gt_0p5": full_ba_mean > 0.5,
            "full_auroc_gt_0p5": full_auroc_mean > 0.5,
        },
    }
    write_json(outdir / "summary.json", summary)
    return summary


def source_sensitivity(
    predictions: Sequence[Mapping[str, Any]], outdir: Path
) -> dict[str, Any]:
    obs = [p for p in predictions if p["world"] == "observed" and p["split"] == "validation"]
    if not obs:
        raise RuntimeError("missing observed validation predictions")
    index = unique_index(obs, lambda p: (int(p["seed"]), p["representation"], p["readout"], p["row_id"]))
    seeds = sorted({int(p["seed"]) for p in obs})
    row_info = {}
    source_info = {}
    for p in obs:
        blocks = dict(item.split("=", 1) for item in str(p["sources"]).split(";"))
        value = (str(p["label"]), blocks)
        if p["row_id"] in row_info and row_info[p["row_id"]] != value:
            raise RuntimeError("source lineage/label changes across observed seeds or methods")
        row_info[p["row_id"]] = value
        for session, source in blocks.items():
            meta = (session, str(p["label"]))
            if source in source_info and source_info[source] != meta:
                raise RuntimeError("inconsistent source session/class")
            source_info[source] = meta
    rows = sorted(row_info)
    y = np.array([LABEL_TO_INT[row_info[r][0]] for r in rows])
    row_sources = [tuple(row_info[r][1].values()) for r in rows]
    strata = defaultdict(list)
    for source, meta in sorted(source_info.items()):
        strata[meta].append(source)
    # Precompute per-row errors once; source weights, never pseudorow resampling.
    errors = {}
    for seed in seeds:
        for rep in REPRESENTATIONS:
            for readout in DECODERS:
                ps = [index[(seed, rep, readout, r)] for r in rows]
                correct = np.array([LABEL_TO_INT[p["pred_label"]] for p in ps]) == y
                probability = np.clip([float(p["score"]) for p in ps], 1e-9, 1 - 1e-9)
                loss = -(y * np.log(probability) + (1 - y) * np.log1p(-probability))
                errors[(seed, rep, readout)] = (correct, loss)

    def evaluate(weights, identity):
        weights = np.asarray(weights, dtype=float)
        class_mass = [float(weights[y == c].sum()) for c in (0, 1)]
        valid = min(class_mass) > 0
        balanced = np.zeros(len(y))
        if valid:
            for c in (0, 1):
                balanced[y == c] = .5 * weights[y == c] / class_mass[c]
        details = []
        for objective in ("time", "behavior"):
            for readout in DECODERS:
                seed_values = []
                for seed in seeds:
                    ca, cl = errors[(seed, f"cue_{objective}", readout)]
                    fa, fl = errors[(seed, f"full_{objective}", readout)]
                    vals = {
                        "cue_ba": float(balanced @ ca) if valid else None,
                        "full_ba": float(balanced @ fa) if valid else None,
                        "ba_gain_full_minus_cue": float(balanced @ (fa.astype(float) - ca)) if valid else None,
                        "loss_gain_cue_minus_full": float(balanced @ (cl - fl)) if valid and readout == "logistic" else None,
                    }
                    seed_values.append(vals)
                    details.append({**identity, "objective": objective, "readout": readout, "seed": seed,
                                    "estimable": valid, "absent_weight": class_mass[0], "present_weight": class_mass[1], **vals})
                means = {k: float(np.mean([v[k] for v in seed_values])) if seed_values[0][k] is not None else None for k in seed_values[0]}
                details.append({**identity, "objective": objective, "readout": readout, "seed": "mean",
                                "estimable": valid, "absent_weight": class_mass[0], "present_weight": class_mass[1], **means})
        return details, valid

    deletions, resamples, weight_rows = [], [], []
    invalid = 0
    for source in sorted(source_info):
        weights = [float(source not in members) for members in row_sources]
        details, valid = evaluate(weights, {"deleted_source_trial_id": source})
        deletions.extend(details)
        invalid += not valid
    rng = np.random.default_rng(RESAMPLE_SEED)
    for b in range(RESAMPLES):
        multiplicities = Counter()
        for members in strata.values():
            multiplicities.update(map(str, rng.choice(members, len(members), replace=True)))
        weights = [float(math.prod(multiplicities[s] for s in members)) for members in row_sources]
        details, _valid = evaluate(weights, {"resample": b})
        resamples.extend(details)
        weight_rows.extend({"resample": b, "source_trial_id": s, "multiplicity": multiplicities[s]} for s in sorted(source_info))
    write_csv(outdir / "validation_source_deletion.csv", deletions)
    write_csv(outdir / "validation_source_resamples.csv", resamples)
    write_csv(outdir / "validation_source_draws.csv", weight_rows)
    summary = {"deletions": len(source_info), "resamples": RESAMPLES, "seeds": seeds,
               "inestimable_deletions": int(invalid), "deletion_metric_rows": len(deletions),
               "resample_metric_rows": len(resamples), "sensitivity_not_confidence_intervals": True}
    for objective in ("time", "behavior"):
        values = [r["loss_gain_cue_minus_full"] for r in resamples if r["objective"] == objective and r["readout"] == "logistic" and r["seed"] == "mean" and r["estimable"]]
        summary[f"{objective}_mean_gain_quantiles_025_50_975"] = np.quantile(values, [.025, .5, .975]).tolist() if values else None
    write_json(outdir / "source_sensitivity_summary.json", summary)
    return summary


def directory_size_bytes(path: Path) -> int:
    return sum(p.stat().st_size for p in path.rglob("*") if p.is_file())


def check_output_budget(path: Path, *, limit_gib: float = 10.0) -> None:
    size = directory_size_bytes(path)
    if size > int(limit_gib * 1024**3):
        raise RuntimeError(f"output budget exceeded: {size} bytes > {limit_gib} GiB")


def validate_audit_nav_hash(audit_dir: Path, cohort: CueCohort) -> Path:
    manifest = read_json(audit_dir / "audit_manifest.json")
    nav_path = audit_dir / "training_nav_source_data.npz"
    if str(nav_path) != manifest.get("training_nav_npz"):
        raise RuntimeError(
            "audit manifest training_nav_npz does not match requested audit dir"
        )
    if sha256_file(nav_path) != manifest.get("training_nav_npz_sha256"):
        raise RuntimeError(
            "training_nav_source_data.npz hash mismatch vs audit_manifest.json"
        )
    load_nav_data(nav_path, cohort)
    return nav_path


def cmd_run(args: argparse.Namespace) -> None:
    outdir = Path(args.output_dir)
    ensure_fresh_dir(outdir)
    config = validate_run_config(args)
    deadline = time.monotonic() + config["limits"]["fit_cap_minutes"] * 60
    audit_manifest = Path(args.audit_dir) / "audit_manifest.json"
    approval = require_prefit_approval(
        Path(args.prefit_approval), audit_manifest, config
    )
    write_json(outdir / "locked_config.json", config)
    write_json(outdir / "prefit_approval_checked.json", approval)
    write_json(
        outdir / "runtime_manifest.json",
        {
            "created_utc": utc_now(),
            "git": git_state(),
            "versions": package_versions(),
            "command": sys.argv,
            "runtime_python": str(RUNTIME_PYTHON),
        },
    )
    shutil.copy2(Path(__file__), outdir / "code_snapshot_cebra_full_trial_transfer.py")
    shutil.copy2(PROTOCOL_PATH, outdir / "protocol_snapshot.md")
    snapshot_sources(outdir / "helper_snapshots", helper_paths())
    write_json(outdir / "input_manifest_hashes.json", input_manifest_hashes())
    journal_path = outdir / "journal.jsonl"
    journal(journal_path, "run_started", config=config)
    cohort = load_cue_cohort(SOURCE_NPZ, V6_DIR)
    nav_path = validate_audit_nav_hash(Path(args.audit_dir), cohort)
    nav = load_nav_data(nav_path, cohort)
    all_metrics: list[dict[str, Any]] = []
    all_preds: list[dict[str, Any]] = []
    accounting = Counter()
    worlds: list[tuple[str, int, Mapping[str, str] | None, dict[str, Any]]] = [
        ("observed", 0, None, {"kind": "observed"})
    ]
    for idx, ns in enumerate(NULL_SEEDS, start=1):
        shuf, info = shuffled_source_labels(cohort.metas, seed=ns)
        worlds.append((f"null{idx:02d}_seed{ns}", idx, shuf, info))
    write_json(
        outdir / "worlds.json",
        [{"world": w, "index": i, "shuffle_info": info} for w, i, _s, info in worlds],
    )
    try:
        for world_name, world_index, shuffled, _info in worlds:
            for seed in SEEDS:
                check_deadline(deadline)
                result = run_world_seed(
                    world_name=world_name,
                    world_index=world_index,
                    seed=seed,
                    cohort=cohort,
                    nav=nav,
                    shuffled_labels=shuffled,
                    outdir=outdir,
                    journal_path=journal_path,
                    iterations=args.iterations,
                    batch_size=args.batch_size,
                    lr=args.lr,
                    hidden=args.hidden,
                    dim=args.dim,
                    device=args.device,
                    deadline=deadline,
                )
                all_metrics.extend(result["metrics"])
                all_preds.extend(result["predictions"])
                accounting.update(result["counts"])
                check_output_budget(outdir)
                check_deadline(deadline)
        if accounting != Counter(
            {
                "encoders": EXPECTED_ENCODERS,
                "pcas": EXPECTED_PCAS,
                "readouts": EXPECTED_READOUTS,
            }
        ):
            raise RuntimeError(f"accounting mismatch: {dict(accounting)}")
        write_csv(outdir / "metrics.csv", all_metrics)
        write_csv_gz(
            outdir / "predictions.csv.gz",
            all_preds,
            fieldnames=list(all_preds[0].keys()) if all_preds else [],
        )
        summary = summarize_results(all_metrics, all_preds, outdir)
        sens = source_sensitivity(all_preds, outdir)
        journal(
            journal_path,
            "run_completed",
            accounting=dict(accounting),
            summary=summary,
            source_sensitivity=sens,
        )
        write_hash_manifest(outdir)
    except Exception as exc:
        journal(
            journal_path, "run_failed", error=repr(exc), accounting=dict(accounting)
        )
        raise


def load_predictions(path: Path) -> list[dict[str, str]]:
    return read_csv_rows(path)


def write_hash_manifest(root: Path) -> None:
    rows = []
    for path in sorted(root.rglob("*")):
        if path.is_file() and path.name != "hash_manifest.json":
            rows.append(
                {
                    "relative_path": str(path.relative_to(root)),
                    "bytes": path.stat().st_size,
                    "sha256": sha256_file(path),
                }
            )
    write_json(root / "hash_manifest.json", {"created_utc": utc_now(), "files": rows})


def verify_hash_manifest(root: Path) -> dict[str, Any]:
    manifest_path = root / "hash_manifest.json"
    if not manifest_path.exists():
        raise RuntimeError("missing required run hash manifest")
    payload = read_json(manifest_path)
    entries = payload.get("files", [])
    expected = {str(p.relative_to(root)) for p in root.rglob("*")
                if p.is_file() and p.name != "hash_manifest.json"}
    declared = [row["relative_path"] for row in entries]
    if not entries or len(declared) != len(set(declared)) or set(declared) != expected:
        raise RuntimeError("hash manifest has missing/extra/duplicate files")
    for row in entries:
        path = root / row["relative_path"]
        if (
            not path.is_file()
            or path.stat().st_size != row["bytes"]
            or sha256_file(path) != row["sha256"]
        ):
            raise RuntimeError(f"hash manifest mismatch: {row['relative_path']}")
    return {"status": "checked", "checked_files": len(payload.get("files", []))}


def verify_no_fit_monkeypatch() -> None:
    def forbid(*_args, **_kwargs):
        raise RuntimeError("fit/step API disabled during verification")

    torch.optim.Optimizer.step = forbid  # type: ignore[assignment]
    torch.optim.Adam.step = forbid  # type: ignore[assignment]
    LogisticRegression.fit = forbid  # type: ignore[assignment]
    SVC.fit = forbid  # type: ignore[assignment]
    PCA.fit = forbid  # type: ignore[assignment]
    StandardScaler.fit = forbid  # type: ignore[assignment]


def scaler_from_npz(path: Path) -> StandardScaler:
    state = np.load(path, allow_pickle=False)
    scaler = StandardScaler()
    scaler.mean_ = state["mean"]
    scaler.scale_ = state["scale"]
    scaler.var_ = state["var"]
    setattr(scaler, "n_features_in_", int(scaler.mean_.shape[0]))  # noqa: B010 — preserve historical replay AST
    scaler.n_samples_seen_ = int(np.asarray(state["n_samples_seen"]).reshape(-1)[0])
    return scaler


def plans_from_manifest(path: Path) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = {}
    for row in read_csv_rows(path):
        rid = row["row_id"]
        if rid not in grouped:
            grouped[rid] = {
                "split": row["split"],
                "label": row["label"],
                "row_kind": row["row_kind"],
                "row_id": rid,
                "sources": {},
            }
            if row.get("product_row", "") != "":
                grouped[rid]["product_row"] = int(row["product_row"])
                grouped[rid]["manifest_key"] = row.get("manifest_key", "")
        grouped[rid]["sources"][row["session_id"]] = row["source_trial_id"]
    return list(grouped.values())


def load_torch_state(path: Path, *, device: str) -> Any:
    # Own hash-checked checkpoints only; no unsafe pickle fallback.
    return torch.load(path, map_location=device, weights_only=True)


def replay_seed_dir(
    seed_dir: Path, cohort: CueCohort, *, device: str
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[str]]:
    world_index_text, world_name = seed_dir.parent.name.split("_", 1)
    seed = int(seed_dir.name.removeprefix("seed"))
    prefix = {"world": world_name, "world_index": int(world_index_text), "seed": seed}
    shuffled = None if world_index_text == "00" else shuffled_source_labels(cohort.metas, seed=NULL_SEEDS[int(world_index_text) - 1])[0]
    train_plans = make_training_plans(cohort.metas, cohort.cell_ids, rows_per_class=ROWS_PER_CLASS, seed=seed, shuffled_labels=shuffled)
    val_plans, _support = make_validation_plans(cohort.metas, cohort.cell_ids, shuffled_labels=shuffled)
    train_bundle = materialize_cue_rows(cohort, train_plans)
    val_bundle = materialize_cue_rows(cohort, val_plans)
    assert_equivalent(read_csv_rows(seed_dir / "train_manifest.csv"), train_bundle.manifest, tolerance=0)
    assert_equivalent(read_csv_rows(seed_dir / "validation_manifest.csv"), val_bundle.manifest, tolerance=0)
    scaler = scaler_from_npz(seed_dir / "cue_scaler.npz")
    Xtr_scaled = transform_cue_samples(train_bundle.X_cue, scaler)
    Xva_scaled = transform_cue_samples(val_bundle.X_cue, scaler)
    features: dict[str, tuple[np.ndarray, np.ndarray]] = {
        "raw290": (raw_features(Xtr_scaled), raw_features(Xva_scaled))
    }
    checked: list[str] = []

    pca_meta = read_json(seed_dir / "pca8_state.json")
    pca_path = Path(pca_meta["path"])
    if sha256_file(pca_path) != pca_meta["sha256"]:
        raise RuntimeError(f"PCA hash mismatch: {pca_path}")
    features["pca8"] = (
        apply_pca_state(pca_path, Xtr_scaled),
        apply_pca_state(pca_path, Xva_scaled),
    )
    checked.append(str(pca_path))

    for arm in CEBRA_ARMS:
        fit_dir = seed_dir / "encoders" / arm
        info = read_json(fit_dir / "fit_info.json")
        ckpt = Path(info["checkpoint_final"])
        if sha256_file(ckpt) != info["checkpoint_final_sha256"]:
            raise RuntimeError(f"checkpoint hash mismatch: {ckpt}")
        solver = make_solver(
            len(cohort.cell_ids),
            int(info["dim"]),
            int(info["hidden"]),
            float(info["lr"]),
            device,
        )
        solver.load_state_dict(load_torch_state(ckpt, device=device), strict=True)
        solver.n_features = len(cohort.cell_ids)
        Ztr = embed_cue(solver, Xtr_scaled, device=device)
        Zva = embed_cue(solver, Xva_scaled, device=device)
        saved = np.load(fit_dir / "cue_embeddings.npz", allow_pickle=False)
        if not np.array_equal(saved["y_train"], train_bundle.y) or not np.array_equal(saved["y_validation"], val_bundle.y):
            raise RuntimeError("saved embedding labels differ from source lineage")
        exposure_path = fit_dir / "sample_exposure_counts.npz"
        if sha256_file(exposure_path) != info["sample_exposure_sha256"]:
            raise RuntimeError("sample exposure hash mismatch")
        counts = np.load(exposure_path, allow_pickle=False)["counts"]
        if counts.shape != (3, info["data_info"]["sample_count"]) or np.any(counts < 0) or not np.all(counts.sum(axis=1) == info["iterations"] * info["batch_size"]):
            raise RuntimeError("sampler exposure accounting mismatch")
        max_diff = max(
            float(np.max(np.abs(Ztr - saved["Z_train"]))),
            float(np.max(np.abs(Zva - saved["Z_validation"]))),
        )
        if max_diff > 1e-5:
            raise RuntimeError(f"embedding replay mismatch {fit_dir}: {max_diff}")
        features[arm] = (Ztr, Zva)
        checked.append(str(ckpt))

    metrics_rows: list[dict[str, Any]] = []
    pred_rows: list[dict[str, Any]] = []
    for rep, (Xtr, Xva) in features.items():
        for readout in DECODERS:
            meta = read_json(
                seed_dir / "readouts" / rep / readout / f"{readout}_decoder_state.json"
            )
            state_path = Path(meta["path"])
            if sha256_file(state_path) != meta["sha256"]:
                raise RuntimeError(f"decoder state hash mismatch: {state_path}")
            ptr, strn = predict_decoder_state(state_path, Xtr)
            pva, sva = predict_decoder_state(state_path, Xva)
            metrics_rows.append(
                metric_row(
                    train_bundle.y,
                    ptr,
                    strn,
                    weights=exact_class_weights(train_bundle.y),
                    readout=readout,
                    prefix={
                        **prefix,
                        "split": "train",
                        "representation": rep,
                        "readout": readout,
                    },
                )
            )
            metrics_rows.append(
                metric_row(
                    val_bundle.y,
                    pva,
                    sva,
                    weights=val_bundle.weights,
                    readout=readout,
                    prefix={
                        **prefix,
                        "split": "validation",
                        "representation": rep,
                        "readout": readout,
                    },
                )
            )
            pred_rows.extend(
                prediction_rows(
                    train_bundle.y,
                    ptr,
                    strn,
                    split="train",
                    readout=readout,
                    prefix={**prefix, "representation": rep},
                    plans=train_bundle.plans,
                )
            )
            pred_rows.extend(
                prediction_rows(
                    val_bundle.y,
                    pva,
                    sva,
                    split="validation",
                    readout=readout,
                    prefix={**prefix, "representation": rep},
                    plans=val_bundle.plans,
                )
            )
            checked.append(str(state_path))
    return metrics_rows, pred_rows, checked


def unique_index(
    rows: Sequence[Mapping[str, Any]], key_fn
) -> dict[tuple[Any, ...], Mapping[str, Any]]:
    out: dict[tuple[Any, ...], Mapping[str, Any]] = {}
    for row in rows:
        key = key_fn(row)
        if key in out:
            raise RuntimeError(f"duplicate replay key: {key}")
        out[key] = row
    return out


def compare_replay(
    saved_metrics: Sequence[Mapping[str, Any]],
    saved_predictions: Sequence[Mapping[str, Any]],
    replay_metrics: Sequence[Mapping[str, Any]],
    replay_predictions: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    def metric_key(r: Mapping[str, Any]) -> tuple[Any, ...]:
        return (
            r["world"],
            str(r["seed"]),
            r["representation"],
            r["readout"],
            r["split"],
        )

    saved_metric_index = unique_index(saved_metrics, metric_key)
    replay_metric_index = unique_index(replay_metrics, metric_key)
    if set(saved_metric_index) != set(replay_metric_index):
        raise RuntimeError("saved/replayed metric keysets differ")
    max_metric_diff = 0.0
    for key, row in replay_metric_index.items():
        saved = saved_metric_index[key]
        if set(saved) != set(row):
            raise RuntimeError("metric columns changed")
        for field in ("balanced_log_loss", "balanced_brier", "balanced_accuracy", "auroc", "recall_absent", "recall_present", "positive_fraction", "n", "world_index"):
            a, b = row[field], saved[field]
            if a == "" or b == "":
                if a != b:
                    raise RuntimeError(f"metric presence mismatch: {field}")
                continue
            if not np.isfinite([float(a), float(b)]).all():
                raise RuntimeError("nonfinite replay metric")
            max_metric_diff = max(max_metric_diff, abs(float(a) - float(b)))

    def pred_key(r: Mapping[str, Any]) -> tuple[Any, ...]:
        return (
            r["world"],
            str(r["seed"]),
            r["representation"],
            r["readout"],
            r["split"],
            r["row_id"],
        )

    saved_pred_index = unique_index(saved_predictions, pred_key)
    replay_pred_index = unique_index(replay_predictions, pred_key)
    if set(saved_pred_index) != set(replay_pred_index):
        raise RuntimeError("saved/replayed prediction keysets differ")
    max_score_diff = 0.0
    for key, row in replay_pred_index.items():
        saved = saved_pred_index[key]
        if set(saved) != set(row):
            raise RuntimeError("prediction columns changed")
        for field in ("label", "pred_label", "sources", "manifest_key", "product_row", "row_index", "score_name", "world_index"):
            if str(row.get(field, "")) != str(saved.get(field, "")):
                raise RuntimeError(f"prediction {field} mismatch for {key}")
        if not np.isfinite([float(row["score"]), float(saved["score"])]).all():
            raise RuntimeError("nonfinite replay score")
        max_score_diff = max(
            max_score_diff, abs(float(row["score"]) - float(saved["score"]))
        )
    if max_metric_diff > 1e-6 or max_score_diff > 1e-5:
        raise RuntimeError(
            f"replay mismatch: metric={max_metric_diff} score={max_score_diff}"
        )
    return {
        "max_metric_abs_diff": max_metric_diff,
        "max_prediction_score_abs_diff": max_score_diff,
    }


def assert_equivalent(saved: Any, replayed: Any, *, tolerance: float = 1e-6) -> None:
    if isinstance(saved, dict) and isinstance(replayed, dict):
        if set(saved) != set(replayed):
            raise RuntimeError("replay object keys differ")
        for key in saved:
            assert_equivalent(saved[key], replayed[key], tolerance=tolerance)
    elif isinstance(saved, list) and isinstance(replayed, list):
        if len(saved) != len(replayed):
            raise RuntimeError("replay list lengths differ")
        for a, b in zip(saved, replayed, strict=True):
            assert_equivalent(a, b, tolerance=tolerance)
    elif saved != replayed:
        if isinstance(saved, (dict, list)) or isinstance(replayed, (dict, list)):
            raise RuntimeError("replay value types differ")
        try:
            a, b = float(saved), float(replayed)
        except (TypeError, ValueError) as exc:
            raise RuntimeError(f"replay values differ: {saved!r} vs {replayed!r}") from exc
        if not np.isfinite([a, b]).all() or abs(a - b) > tolerance:
            raise RuntimeError(f"replay values differ: {saved!r} vs {replayed!r}")


def compare_saved_json(path: Path, recomputed: Mapping[str, Any]) -> dict[str, Any]:
    saved = read_json(path)
    assert_equivalent(saved, recomputed)
    return {"status": "matched_within_1e-6", "path": str(path), "saved_sha256": sha256_file(path)}


def expected_seed_directories() -> set[str]:
    worlds = [(0, "observed")] + [(i, f"null{i:02d}_seed{seed}") for i, seed in enumerate(NULL_SEEDS, 1)]
    return {f"worlds/{i:02d}_{world}/seed{seed}" for i, world in worlds for seed in SEEDS}


def cmd_verify(args: argparse.Namespace) -> None:
    run_dir = Path(args.run_dir)
    outdir = Path(args.output_dir)
    ensure_fresh_dir(outdir)
    hash_manifest_status = verify_hash_manifest(run_dir)
    verify_no_fit_monkeypatch()
    journal_path = outdir / "verify_journal.jsonl"
    journal(
        journal_path,
        "verify_started",
        run_dir=str(run_dir),
        hash_manifest=hash_manifest_status,
    )
    saved_metrics = read_csv_rows(run_dir / "metrics.csv")
    saved_predictions = load_predictions(run_dir / "predictions.csv.gz")
    cohort = load_cue_cohort(SOURCE_NPZ, V6_DIR)
    replay_metrics: list[dict[str, Any]] = []
    replay_predictions: list[dict[str, Any]] = []
    checked: list[str] = []
    seed_dirs = sorted(run_dir.glob("worlds/*/seed*"))
    if {str(p.relative_to(run_dir)) for p in seed_dirs} != expected_seed_directories():
        raise RuntimeError("incomplete/extra world-seed grid")
    assert_equivalent(read_json(run_dir / "locked_config.json"), locked_config(), tolerance=0)
    for seed_dir in seed_dirs:
        m_rows, p_rows, c_rows = replay_seed_dir(seed_dir, cohort, device=args.device)
        replay_metrics.extend(m_rows)
        replay_predictions.extend(p_rows)
        checked.extend(c_rows)
    if len(replay_metrics) != EXPECTED_READOUTS * 2 or len(replay_predictions) != EXPECTED_READOUTS * (128 + 30) or len(checked) != EXPECTED_ENCODERS + EXPECTED_PCAS + EXPECTED_READOUTS:
        raise RuntimeError("forward replay fit/row accounting incomplete")
    comparison = compare_replay(
        saved_metrics, saved_predictions, replay_metrics, replay_predictions
    )
    write_csv(outdir / "metrics_replayed.csv", replay_metrics)
    write_csv_gz(
        outdir / "predictions_replayed.csv.gz",
        replay_predictions,
        fieldnames=list(replay_predictions[0].keys()) if replay_predictions else [],
    )
    summary = summarize_results(replay_metrics, replay_predictions, outdir)
    sens = source_sensitivity(replay_predictions, outdir)
    saved_summary_check = compare_saved_json(run_dir / "summary.json", summary)
    saved_sensitivity_check = compare_saved_json(
        run_dir / "source_sensitivity_summary.json", sens
    )
    for name in ("validation_source_deletion.csv", "validation_source_resamples.csv", "validation_source_draws.csv"):
        assert_equivalent(read_csv_rows(run_dir / name), read_csv_rows(outdir / name))
    receipt = {
        "created_utc": utc_now(),
        "run_dir": str(run_dir),
        "hash_manifest": hash_manifest_status,
        "checked_artifacts": len(checked),
        "comparison": comparison,
        "saved_summary_check": saved_summary_check,
        "saved_sensitivity_check": saved_sensitivity_check,
        "summary": summary,
        "source_sensitivity": sens,
        "status": "verified_forward_only",
    }
    write_json(outdir / "verification_receipt.json", receipt)
    journal(journal_path, "verify_completed", receipt=receipt)
    print(json.dumps(jsonable(receipt), indent=2, sort_keys=True))


def synthetic_cohort(seed: int = 0) -> tuple[CueCohort, NavData]:
    rng = np.random.default_rng(seed)
    sessions = ["S1_session01", "S2_session01"]
    cell_ids = [
        "S1/session01/array01/channel001/cell01",
        "S1/session01/array01/channel002/cell01",
        "S1/session01/array01/channel003/cell01",
        "S1/session01/array01/channel004/cell01",
        "S2/session01/array01/channel001/cell01",
        "S2/session01/array01/channel002/cell01",
        "S2/session01/array01/channel003/cell01",
        "S2/session01/array01/channel004/cell01",
    ]
    metas = []
    Xs = []
    expos = []
    masks = []
    ids = []
    sess_ids = []
    splits = []
    labels = []
    for split, per in (("train", 3), ("validation", 1)):
        for sess in sessions:
            for label in LABELS:
                for k in range(per):
                    sid = f"{sess}_{split}_{label}_{k}"
                    ids.append(sid)
                    sess_ids.append(sess)
                    splits.append(split)
                    labels.append(label)
                    metas.append(SourceMeta(sid, sess, split, label, len(metas) + 1))
                    mask = np.asarray([session_from_cell(c) == sess for c in cell_ids])
                    x = np.zeros((len(cell_ids), CUE_BINS), dtype=np.float32)
                    base = 2.0 if label == "present" else 0.0
                    x[mask] = rng.poisson(base + 0.2, size=(int(mask.sum()), CUE_BINS))
                    Xs.append(x)
                    expos.append(np.full(CUE_BINS, 0.1, dtype=np.float32))
                    masks.append(mask)
    cohort = CueCohort(
        np.stack(Xs),
        np.stack(expos),
        np.stack(masks),
        ids,
        sess_ids,
        splits,
        labels,
        cell_ids,
        metas,
        {sid: i for i, sid in enumerate(ids)},
    )
    train = [m for m in metas if m.split == "train"]
    counts = []
    exp = []
    mflat = []
    offsets = [0]
    n_bins = []
    for m in train:
        n = 2 + (m.trial_index % 3)
        mask = np.asarray([session_from_cell(c) == m.session_id for c in cell_ids])
        arr = np.full((n, len(cell_ids)), np.nan, dtype=np.float32)
        arr[:, mask] = rng.poisson(
            (2.0 if m.label == "present" else 0.0) + 0.2, size=(n, int(mask.sum()))
        )
        counts.append(arr)
        exp.append(np.full(n, 0.1, dtype=np.float32))
        mflat.append(np.tile(mask, (n, 1)))
        offsets.append(offsets[-1] + n)
        n_bins.append(n)
    nav = NavData(
        Path("synthetic"),
        [m.source_trial_id for m in train],
        [m.session_id for m in train],
        [m.label for m in train],
        np.asarray([m.trial_index for m in train]),
        np.asarray(offsets),
        np.asarray(n_bins),
        np.concatenate(counts),
        np.concatenate(exp),
        np.concatenate(mflat),
        cell_ids,
        {m.source_trial_id: i for i, m in enumerate(train)},
    )
    return cohort, nav


def run_synthetic_smoke(
    output_dir: Path,
    *,
    iterations: int = 2,
    batch_size: int = 8,
    device: str = "cpu",
    hidden: int = 32,
    dim: int = 8,
    lr: float = 3e-4,
) -> dict[str, Any]:
    ensure_fresh_dir(output_dir)
    cohort, nav = synthetic_cohort()
    metrics: list[dict[str, Any]] = []
    preds: list[dict[str, Any]] = []
    result = run_world_seed(
        world_name="observed",
        world_index=0,
        seed=0,
        cohort=cohort,
        nav=nav,
        shuffled_labels=None,
        outdir=output_dir,
        journal_path=output_dir / "journal.jsonl",
        iterations=iterations,
        batch_size=batch_size,
        lr=lr,
        hidden=hidden,
        dim=dim,
        device=device,
    )
    metrics.extend(result["metrics"])
    preds.extend(result["predictions"])
    write_csv(output_dir / "metrics.csv", metrics)
    write_csv_gz(
        output_dir / "predictions.csv.gz", preds, fieldnames=list(preds[0].keys())
    )
    summary = {
        "status": "synthetic_smoke_passed",
        "metrics_rows": len(metrics),
        "prediction_rows": len(preds),
        "accounting": result["counts"],
    }
    write_json(output_dir / "synthetic_summary.json", summary)
    return summary


def cmd_synthetic_smoke(args: argparse.Namespace) -> None:
    summary = run_synthetic_smoke(
        Path(args.output_dir),
        iterations=args.iterations,
        batch_size=args.batch_size,
        device=args.device,
        hidden=args.hidden,
        dim=args.dim,
        lr=args.lr,
    )
    print(json.dumps(jsonable(summary), indent=2, sort_keys=True))


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("audit", help="no-fit raw training-navigation audit/export")
    a.add_argument("--output-dir", type=Path, required=True)
    a.add_argument("--canonical-root", type=Path, default=CANONICAL_ROOT)
    a.add_argument("--import-dir", type=Path, default=IMPORT_DIR)
    a.add_argument("--split-dir", type=Path, default=SPLIT_DIR)
    a.add_argument("--v6-dir", type=Path, default=V6_DIR)
    a.add_argument("--source-npz", type=Path, default=SOURCE_NPZ)
    a.set_defaults(func=cmd_audit)

    r = sub.add_parser(
        "run", help="approved biological run; refuses without hash-bound approval"
    )
    r.add_argument("--audit-dir", type=Path, required=True)
    r.add_argument("--prefit-approval", type=Path, required=True)
    r.add_argument("--output-dir", type=Path, required=True)
    r.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    r.add_argument("--iterations", type=int, default=1000)
    r.add_argument("--batch-size", type=int, default=256)
    r.add_argument("--lr", type=float, default=3e-4)
    r.add_argument("--hidden", type=int, default=32)
    r.add_argument("--dim", type=int, default=8)
    r.set_defaults(func=cmd_run)

    v = sub.add_parser("verify", help="forward-only verification from fresh output dir")
    v.add_argument("--run-dir", type=Path, required=True)
    v.add_argument("--output-dir", type=Path, required=True)
    v.add_argument("--device", default="cpu")
    v.set_defaults(func=cmd_verify)

    s = sub.add_parser(
        "synthetic-smoke", help="invented-data tiny end-to-end software smoke"
    )
    s.add_argument("--output-dir", type=Path, required=True)
    s.add_argument("--device", default="cpu")
    s.add_argument("--iterations", type=int, default=2)
    s.add_argument("--batch-size", type=int, default=8)
    s.add_argument("--hidden", type=int, default=32)
    s.add_argument("--dim", type=int, default=8)
    s.add_argument("--lr", type=float, default=3e-4)
    s.set_defaults(func=cmd_synthetic_smoke)
    return p.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> None:
    args = parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
