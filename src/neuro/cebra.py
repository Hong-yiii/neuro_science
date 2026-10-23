# pyright: reportMissingImports=false
"""Independent cue-only CEBRA-Time fitting with the maintained vector sampler.

Uses offset1-model / FixedCosineInfoNCE(temperature=1) / Adam through the existing
solver. References are row-uniform, positives adjacent native bins in that row,
negatives row/bin-uniform. No generic CEBRA.fit defaults or study imports.
Joint/Behavior study machinery remains in neuro._cebra_sampling unchanged.
"""

from __future__ import annotations

import time
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

import numpy as np
import torch

from neuro._cebra_sampling import CebraVectorDataset, PhaseTimeLoader
from neuro.cebra_solver import make_solver
from neuro.pca_lda import Standardizer, fit_standardizer, neural_tensor


@dataclass(frozen=True)
class CEBRAFit:
    solver: Any
    standardizer: Standardizer
    diagnostics: dict
    device: str

    def transform(self, values: np.ndarray, *, batch_vectors: int = 8192) -> np.ndarray:
        """Transform only: no fitting, optimizer, or evaluation-time normalization."""
        if (
            isinstance(batch_vectors, bool)
            or not isinstance(batch_vectors, int)
            or batch_vectors < 1
        ):
            raise ValueError("batch_vectors must be positive")
        arr = self.standardizer.transform(values)
        flat = arr.transpose(0, 2, 1).reshape(-1, arr.shape[1])
        self.solver.model.eval()
        embeddings = []
        with torch.no_grad():
            for start in range(0, len(flat), batch_vectors):
                tensor = torch.as_tensor(
                    flat[start : start + batch_vectors],
                    dtype=torch.float32,
                    device=self.device,
                )
                embeddings.append(self.solver.transform(tensor).detach().cpu().numpy())
        z = np.concatenate(embeddings).astype(np.float32)
        if not np.isfinite(z).all():
            raise RuntimeError("nonfinite CEBRA transform")
        return z.reshape(arr.shape[0], arr.shape[2], -1).reshape(arr.shape[0], -1)

    def save(self, path: str | Path) -> None:
        """Explicit optional trusted checkpoint; refuses to overwrite existing files."""
        payload = {
            "solver": self.solver.state_dict(),
            "diagnostics": self.diagnostics,
            "standardizer_mean": self.standardizer.scaler.mean_,
            "standardizer_scale": self.standardizer.scaler.scale_,
            "standardizer_var": self.standardizer.scaler.var_,
            "standardizer_samples": self.standardizer.scaler.n_samples_seen_,
            "input_shape": self.standardizer.shape,
        }
        with Path(path).open("xb") as handle:
            torch.save(payload, handle)


def fit(
    train: np.ndarray,
    train_targets: np.ndarray,
    *,
    iterations: int,
    batch_size: int,
    output_dimension: int,
    hidden: int,
    learning_rate: float,
    seed: int,
    max_seconds: float,
    device: str = "cpu",
) -> CEBRAFit:
    """Fit fresh on training only; supplied targets label rows, not temporal bins.

    max_seconds is a monotonic cooperative deadline checked before/after every
    update (not a subprocess kill guarantee). Caller owns process/memory limits.
    At most two numerical torch threads; the previous setting is restored.
    """
    for name, value in (
        ("iterations", iterations),
        ("batch_size", batch_size),
        ("output_dimension", output_dimension),
        ("hidden", hidden),
    ):
        if isinstance(value, bool) or not isinstance(value, int) or value < 1:
            raise ValueError(f"{name} must be a positive integer")
    if isinstance(seed, bool) or not isinstance(seed, int) or seed < 0:
        raise ValueError("seed must be nonnegative")
    if (
        not np.isfinite(learning_rate)
        or learning_rate <= 0
        or not np.isfinite(max_seconds)
        or max_seconds <= 0
    ):
        raise ValueError("finite positive learning_rate/max_seconds required")
    if device != "cpu" and not (
        device.startswith("cuda") and torch.cuda.is_available()
    ):
        raise ValueError("device must be cpu or available cuda")
    arr = neural_tensor(train)
    labels = np.asarray(train_targets)
    if labels.ndim != 1 or len(labels) != len(arr) or arr.shape[2] < 2:
        raise ValueError("one target per row and >=2 native bins required")
    if labels.dtype.kind in "fc" and not np.isfinite(labels).all():
        raise ValueError("nonfinite training targets")
    classes, codes = np.unique(labels, return_inverse=True)
    started = time.monotonic()
    deadline = started + max_seconds

    def check_budget():
        if time.monotonic() >= deadline:
            raise TimeoutError("CEBRA fitting deadline exceeded")

    previous_threads = torch.get_num_threads()
    torch.set_num_threads(2)
    cuda_devices = [torch.device(device)] if device.startswith("cuda") else []
    try:
        with torch.random.fork_rng(devices=cuda_devices):
            torch.default_generator.manual_seed(seed)
            if cuda_devices:
                torch.cuda.manual_seed(seed)
            standardizer = fit_standardizer(arr)
            scaled = standardizer.transform(arr)
            flat = scaled.transpose(0, 2, 1).reshape(-1, scaled.shape[1])
            rows, _, bins = scaled.shape
            groups = [
                np.arange(r * bins, (r + 1) * bins, dtype=np.int64) for r in range(rows)
            ]
            pairs = [np.column_stack((g[:-1], g[1:])) for g in groups]
            dataset = CebraVectorDataset(
                flat,
                np.repeat(codes, bins),
                np.zeros(len(flat), dtype=np.int64),
                device=device,
            )
            solver = make_solver(
                flat.shape[1], output_dimension, hidden, learning_rate, device
            )
            dataset.configure_for(solver.model)
            loader = PhaseTimeLoader(
                dataset=dataset,
                pair_groups_by_phase={0: pairs},
                sample_groups_by_phase={0: groups},
                num_steps=iterations,
                batch_size=batch_size,
                seed=seed + 1009,
                phase_probs=(1.0,),
            )
            solver._set_fitted_params(loader)
            solver.model.train()
            for batch in cast(Iterable[Any], loader):
                check_budget()
                solver.step(batch)
                if not all(
                    np.isfinite(solver.log[key][-1])
                    for key in ("total", "pos", "neg", "temperature")
                ):
                    raise RuntimeError("nonfinite CEBRA loss")
                if any(
                    not torch.isfinite(p).all().item()
                    for p in solver.model.parameters()
                ):
                    raise RuntimeError("nonfinite CEBRA parameters")
                check_budget()
            loss = {
                key: np.asarray(solver.log[key], dtype=float).tolist()
                for key in ("total", "pos", "neg", "temperature")
            }
            if len(loss["total"]) != iterations:
                raise RuntimeError("incomplete CEBRA update count")
            diagnostics = {
                "objective": "cue_time",
                "architecture": "offset1-model",
                "temperature": 1.0,
                "seed": seed,
                "sampler_seed": seed + 1009,
                "iterations": iterations,
                "batch_size": batch_size,
                "output_dimension": output_dimension,
                "hidden": hidden,
                "learning_rate": learning_rate,
                "device": device,
                "wall_seconds": time.monotonic() - started,
                "classes": classes.tolist(),
                "loss": loss,
                "pairs_by_row": [p.tolist() for p in pairs],
                "sample_exposure_counts": loader.sample_counts.detach()
                .cpu()
                .numpy()
                .copy(),
                "exposure_summary": loader.exposure_summary(),
                "feature_layout": "time-major",
                "torch_threads": 2,
            }
            return CEBRAFit(solver, standardizer, diagnostics, device)
    finally:
        torch.set_num_threads(previous_threads)
