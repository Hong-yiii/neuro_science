# pyright: reportMissingImports=false
"""Vector dataset and exact row/phase samplers extracted from full_trial_transfer.

Scientific definitions are preserved verbatim; studies re-export these names.
No study, checkout paths, source manifests or Git state are imported here.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, cast

import cebra.data
import numpy as np
import torch
from cebra.data import BatchIndex
from cebra.data.single_session import SingleSessionDataset

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
