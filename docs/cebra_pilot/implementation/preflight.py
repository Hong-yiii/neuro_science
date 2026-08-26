"""CLI preflights for the first CEBRA pilot framework.

All writers require a caller-supplied new directory below
``outputs/cebra_pilot/`` and refuse to reuse it.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections.abc import Callable, Iterable, Sequence
from importlib import metadata
from pathlib import Path
from typing import Any

import numpy as np

from .contracts import MazeGraph, _canonical_json
from .manifest import (
    build_manifest,
    create_output_dir,
    sha256_file,
    write_json,
    write_manifest_file,
)
from .neural import summarize_cue_activity
from .paths import (
    clean_path,
    edge_jaccard,
    longest_shared_contiguous_directed_segment,
)
from .splits import freeze_splits

H1_CURRENT_EXPORT_STOP = (
    "H1 stop: current one-cell navigation export lacks cue-period, same-trial, "
    "trial-linked simultaneous population data."
)
SOFTWARE_SMOKE_ONLY = "software_smoke_only"
PINNED_CEBRA_VERSION = "0.6.1"

TrialReader = Callable[[Path], Iterable[tuple[int, np.ndarray, np.ndarray]]]


def run_synthetic_preprocessing_demo(output_dir: Path | str) -> dict[str, Any]:
    """Run a deterministic synthetic preprocessing smoke demo and write outputs."""

    out = create_output_dir(output_dir)

    graph = MazeGraph((("A", "B"), ("B", "C"), ("B", "D"), ("C", "E"), ("D", "E")))
    left_path = clean_path(("A", "A", "B", None, "C", "E"), graph)
    right_path = clean_path(("A", "B", "D", "E"), graph)
    cue = summarize_cue_activity(
        np.array([[1, 0], [2, 3], [0, 4]], dtype=np.int64),
        np.array([True, False, True]),
        np.array([0.02, 0.02, 0.03]),
        ("unit-a", "unit-b"),
    )
    split = freeze_splits(
        (
            {
                "sample_id": "s1",
                "source_trial_id": "trial-1",
                "session_id": "session-1",
                "simultaneous_recording_group": "group-1",
                "split": "train",
            },
            {
                "sample_id": "s1-window",
                "source_trial_id": "trial-1",
                "session_id": "session-1",
                "simultaneous_recording_group": "group-1",
                "split": "train",
            },
            {
                "sample_id": "s2",
                "source_trial_id": "trial-2",
                "session_id": "session-1",
                "simultaneous_recording_group": "group-1",
                "split": "validation",
            },
            {
                "sample_id": "s3",
                "source_trial_id": "trial-3",
                "session_id": "session-1",
                "simultaneous_recording_group": "group-1",
                "split": "test",
            },
        ),
        expected_source_trial_ids=("trial-1", "trial-2", "trial-3"),
    )

    shared = longest_shared_contiguous_directed_segment(left_path, right_path)
    summary = {
        "scientific_status": SOFTWARE_SMOKE_ONLY,
        "graph_hash": graph.sha256,
        "split_hash": split.sha256,
        "neural": {
            "axis": "cue_bin_by_unit",
            "unit_ids": list(cue.unit_ids),
            "counts_by_unit": cue.counts_by_unit.tolist(),
            "rates_hz_by_unit": cue.rates_hz_by_unit.tolist(),
            "valid_bin_count": cue.valid_bin_count,
            "total_exposure_seconds": cue.total_exposure_seconds,
        },
        "paths": {
            "left_raw_valid_segments": left_path.raw_valid_segments,
            "left_route_shape_segments": left_path.route_shape_segments,
            "left_audit": left_path.audit.__dict__,
            "right_route_shape_segments": right_path.route_shape_segments,
            "edge_jaccard_distance": edge_jaccard(left_path, right_path),
            "longest_shared_directed_segment": {
                "length": shared.length,
                "edges": shared.edges,
                "classification": shared.classification,
                "unavailable_reason": shared.unavailable_reason,
            },
        },
        "split_assignments": [row.__dict__ for row in split.rows],
        "recording_group_split_counts": split.recording_group_split_counts,
        "stop_conditions": ["synthetic preprocessing only; no biological claim"],
    }
    summary_path = write_json(out / "synthetic_preprocessing_summary.json", summary)

    manifest = build_manifest(
        stage="synthetic_preprocessing_demo",
        status="passed",
        scientific_status=SOFTWARE_SMOKE_ONLY,
        input_hashes={
            "synthetic_config_sha256": _payload_sha256(summary["split_assignments"])
        },
        artifact_hashes={summary_path.name: sha256_file(summary_path)},
        config={"cleaning": "split invalid and nonadjacent gaps; no interpolation"},
        shape_summary={
            "cue_counts_by_bin_unit": [3, 2],
            "left_raw_path_samples": 6,
            "right_raw_path_samples": 4,
        },
        exclusion_summary={"invalid_samples": left_path.audit.invalid_sample_count},
        stop_conditions=summary["stop_conditions"],
        graph_hash=graph.sha256,
        split_hash=split.sha256,
    )
    write_manifest_file(out, manifest)
    return summary


def summarize_one_cell_jld2_files(
    files: Sequence[Path | str],
    reader: TrialReader | None = None,
) -> dict[str, Any]:
    """Summarize current one-cell exports without making a scientific contract."""

    read_trials = reader or _import_jld2_reader()
    file_summaries: list[dict[str, Any]] = []
    for file in files:
        path = Path(file)
        trials = 0
        samples = 0
        total_spikes = 0.0
        empty_trials = 0
        saw_shape_mismatch = False
        for trialidx, spikecounts, spatial_bins in read_trials(path):
            spikecounts = np.asarray(spikecounts)
            spatial_bins = np.asarray(spatial_bins)
            if spikecounts.shape != spatial_bins.shape:
                saw_shape_mismatch = True
            trials += 1
            try:
                samples += int(spikecounts.size)
                total_spikes += float(np.sum(spikecounts))
                empty_trials += int(spikecounts.size == 0)
            except (TypeError, ValueError, OverflowError) as exc:
                raise ValueError(
                    f"could not summarize trial {trialidx} in {path}"
                ) from exc
            _ = trialidx  # source-trial adequacy is intentionally not inferred here.
        file_summaries.append(
            {
                "file": str(path),
                "n_trials": trials,
                "n_samples": samples,
                "empty_trials": empty_trials,
                "total_spikes": total_spikes,
                "spike_bin_shape_mismatch": saw_shape_mismatch,
            }
        )
    return {
        "scientific_status": SOFTWARE_SMOKE_ONLY,
        "stop_conditions": [H1_CURRENT_EXPORT_STOP],
        "files": file_summaries,
        "contract_boundary": "loader rows are single-cell navigation samples, not cue-bin x simultaneous-unit trials",
    }


def run_one_cell_jld2_smoke(
    files: Sequence[Path | str],
    output_dir: Path | str,
) -> dict[str, Any]:
    """Import the existing JLD2 reader, smoke-load files, and write a manifest."""

    out = create_output_dir(output_dir)
    summary = summarize_one_cell_jld2_files(files)
    summary_path = write_json(out / "one_cell_jld2_smoke_summary.json", summary)
    manifest = build_manifest(
        stage="current_one_cell_jld2_loader_smoke",
        status="passed",
        scientific_status=SOFTWARE_SMOKE_ONLY,
        input_hashes={str(Path(file)): sha256_file(file) for file in files},
        artifact_hashes={summary_path.name: sha256_file(summary_path)},
        config={"reader": "scripts.inspect_spatial_bin_jld2.read_trials"},
        shape_summary={"files": summary["files"]},
        exclusion_summary={},
        stop_conditions=summary["stop_conditions"],
        notes=(summary["contract_boundary"],),
    )
    write_manifest_file(out, manifest)
    return summary


def run_synthetic_cebra_preflight(output_dir: Path | str) -> dict[str, Any]:
    """Fit, transform, save, and reload CEBRA on contiguous synthetic data."""

    out = create_output_dir(output_dir)
    config = {
        "cebra_version": PINNED_CEBRA_VERSION,
        "device": "cpu",
        "model_architecture": "offset1-model",
        "conditional": "time",
        "output_dimension": 3,
        "max_iterations": 10,
        "time_offsets": 1,
        "batch_size": 32,
        "input_shape": [256, 12],
        "numpy_input_seed": 0,
        "external_torch_seed": 0,
    }
    rng = np.random.default_rng(config["numpy_input_seed"])
    x = rng.normal(size=tuple(config["input_shape"])).astype(np.float32)
    input_hash = hashlib.sha256(x.tobytes()).hexdigest()
    artifact_paths: list[Path] = []

    try:
        installed = metadata.version("cebra")
        if installed != PINNED_CEBRA_VERSION:
            raise RuntimeError(
                f"CEBRA version must be {PINNED_CEBRA_VERSION}, got {installed}"
            )

        import cebra  # type: ignore[import-not-found]
        import torch

        torch.manual_seed(config["external_torch_seed"])
        model = cebra.CEBRA(
            model_architecture=config["model_architecture"],
            conditional=config["conditional"],
            output_dimension=config["output_dimension"],
            max_iterations=config["max_iterations"],
            time_offsets=config["time_offsets"],
            batch_size=config["batch_size"],
            device=config["device"],
            verbose=False,
        )
        model.fit(x)
        embedding = np.asarray(model.transform(x))

        model_path = out / "cebra_model.pt"
        model.save(model_path)
        loaded = cebra.CEBRA.load(model_path)
        reloaded_embedding = np.asarray(loaded.transform(x))
        if embedding.shape != reloaded_embedding.shape:
            raise RuntimeError("reloaded CEBRA embedding shape changed")
        if not np.allclose(embedding, reloaded_embedding, rtol=1e-6, atol=1e-7):
            raise RuntimeError(
                "reloaded CEBRA transform does not match the saved model"
            )
        max_abs_difference = float(np.max(np.abs(embedding - reloaded_embedding)))

        embedding_path = out / "embedding.npy"
        reloaded_path = out / "reloaded_embedding.npy"
        np.save(embedding_path, embedding)
        np.save(reloaded_path, reloaded_embedding)
        artifact_paths.extend((model_path, embedding_path, reloaded_path))
        summary = {
            "scientific_status": SOFTWARE_SMOKE_ONLY,
            "status": "passed",
            "embedding_shape": list(embedding.shape),
            "reloaded_embedding_shape": list(reloaded_embedding.shape),
            "save_load_max_abs_difference": max_abs_difference,
            "notes": [
                "NumPy input and external Torch seeds were set, but the public sklearn CEBRA API does not guarantee full training determinism.",
                "No trial-boundary claim is made by this contiguous synthetic time smoke.",
            ],
        }
        manifest_status = "passed"
    except Exception as exc:
        summary = {
            "scientific_status": SOFTWARE_SMOKE_ONLY,
            "status": "failed",
            "error": str(exc),
            "notes": [
                "CEBRA synthetic smoke failed before any scientific analysis.",
                "The public sklearn CEBRA API does not guarantee full training determinism.",
                "No trial-boundary claim is made.",
            ],
        }
        manifest_status = "failed"

    summary_path = write_json(out / "synthetic_cebra_preflight_summary.json", summary)
    artifact_paths.append(summary_path)
    manifest = build_manifest(
        stage="synthetic_cpu_cebra_preflight",
        status=manifest_status,
        scientific_status=SOFTWARE_SMOKE_ONLY,
        input_hashes={"synthetic_input_float32_sha256": input_hash},
        artifact_hashes={path.name: sha256_file(path) for path in artifact_paths},
        config=config,
        shape_summary={
            key: value for key, value in summary.items() if key.endswith("shape")
        },
        exclusion_summary={},
        stop_conditions=["synthetic API smoke only; no biological claim"],
        notes=tuple(summary.get("notes", ())),
    )
    write_manifest_file(out, manifest)
    if manifest_status == "failed":
        raise RuntimeError(summary["error"])
    return summary


def _import_jld2_reader() -> TrialReader:
    from scripts.inspect_spatial_bin_jld2 import read_trials

    return read_trials


def _payload_sha256(payload: Any) -> str:
    return hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    synthetic = subparsers.add_parser("synthetic-preprocessing")
    synthetic.add_argument("--output-dir", required=True, type=Path)

    jld2 = subparsers.add_parser("jld2-smoke")
    jld2.add_argument("files", nargs="+", type=Path)
    jld2.add_argument("--output-dir", required=True, type=Path)

    cebra_parser = subparsers.add_parser("cebra-synthetic")
    cebra_parser.add_argument("--output-dir", required=True, type=Path)

    args = parser.parse_args(argv)
    if args.command == "synthetic-preprocessing":
        summary = run_synthetic_preprocessing_demo(args.output_dir)
    elif args.command == "jld2-smoke":
        summary = run_one_cell_jld2_smoke(args.files, args.output_dir)
    elif args.command == "cebra-synthetic":
        summary = run_synthetic_cebra_preflight(args.output_dir)
    else:  # pragma: no cover - argparse prevents this.
        parser.error(f"unknown command {args.command!r}")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
