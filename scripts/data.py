#!/usr/bin/env python3
"""Single entry point for the workspace's local data lifecycle."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
STAGES = ("raw", "interim", "processed", "manifests")


def init_data() -> None:
    for stage in STAGES:
        (DATA / stage).mkdir(parents=True, exist_ok=True)
    print(f"ready: {DATA}")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_manifest(output: Path | None) -> None:
    init_data()
    files = []
    for stage in ("raw", "interim", "processed"):
        for path in sorted((DATA / stage).rglob("*")):
            if path.is_file():
                stat = path.stat()
                files.append(
                    {
                        "path": str(path.relative_to(ROOT)),
                        "bytes": stat.st_size,
                        "sha256": sha256(path),
                    }
                )

    output = output or DATA / "manifests" / "latest.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "created_utc": datetime.now(UTC).isoformat(),
        "repository": str(ROOT),
        "files": files,
    }
    output.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"wrote {len(files)} files: {output}")


def inspect(files: list[Path]) -> None:
    from inspect_spatial_bin_jld2 import summarize

    for path in files:
        summarize(path)


def visualize(file: Path, output: Path, min_occupancy: float) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    from inspect_spatial_bin_jld2 import read_trials

    trials = list(read_trials(file))
    if not trials:
        raise ValueError(f"no trials found in {file}")

    spikecounts = np.concatenate([row[1].reshape(-1) for row in trials])
    spatial_bins = np.concatenate([row[2].reshape(-1) for row in trials]).astype(int)
    if spikecounts.shape != spatial_bins.shape:
        raise ValueError("spike-count and spatial-bin arrays do not align")

    bin_ids, inverse = np.unique(spatial_bins, return_inverse=True)
    samples = np.bincount(inverse)
    spikes = np.bincount(inverse, weights=spikecounts)
    occupancy_seconds = samples * 0.020
    rates = spikes / occupancy_seconds
    reliable = occupancy_seconds >= min_occupancy

    fig, axes = plt.subplots(2, 2, figsize=(13, 8), constrained_layout=True)
    lengths = np.asarray([len(row[1]) for row in trials]) * 0.020
    totals = np.asarray([row[1].sum() for row in trials])

    axes[0, 0].hist(lengths, bins=30)
    axes[0, 0].set(xlabel="Trial duration (s)", ylabel="Trials", title="Trial lengths")

    axes[0, 1].hist(totals, bins=np.arange(totals.max() + 2) - 0.5)
    axes[0, 1].set(
        xlabel="Spikes in trial", ylabel="Trials", title="Sparse cell activity"
    )

    axes[1, 0].plot(bin_ids, occupancy_seconds, ".", markersize=3)
    axes[1, 0].axhline(
        min_occupancy, color="tab:red", linestyle="--", label="rate-map threshold"
    )
    axes[1, 0].set(
        xlabel="Spatial-bin ID",
        ylabel="Occupancy (s)",
        title="Where behavior was sampled",
    )
    axes[1, 0].legend()

    axes[1, 1].plot(bin_ids[reliable], rates[reliable], ".", markersize=4)
    axes[1, 1].set(
        xlabel="Spatial-bin ID",
        ylabel="Firing rate (spikes/s)",
        title=f"Occupancy-normalized rate (≥ {min_occupancy:g} s)",
    )

    fig.suptitle(
        f"{file.parent.name} — {len(trials)} trials, {len(bin_ids)} visited bins\n"
        "Bin IDs are labels, not physical x/y coordinates"
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=160)
    plt.close(fig)
    print(f"wrote: {output}")
    print(
        f"shape: {len(trials)} ragged trials -> {len(spikecounts)} time samples; "
        f"{len(bin_ids)} visited spatial bins; {reliable.sum()} pass occupancy threshold"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("init", help="create raw/interim/processed/manifests")

    manifest = commands.add_parser("manifest", help="inventory data with checksums")
    manifest.add_argument("--output", type=Path)

    inspector = commands.add_parser("inspect", help="inspect spatial-bin JLD2 files")
    inspector.add_argument("files", nargs="+", type=Path)

    plotter = commands.add_parser("visualize", help="plot one spatial-bin JLD2 cell")
    plotter.add_argument("file", type=Path)
    plotter.add_argument(
        "--output", type=Path, default=ROOT / "outputs" / "cell_overview.png"
    )
    plotter.add_argument(
        "--min-occupancy",
        type=float,
        default=1.0,
        help="minimum seconds observed before showing a bin's firing rate",
    )

    args = parser.parse_args()
    if args.command == "init":
        init_data()
    elif args.command == "manifest":
        write_manifest(args.output)
    elif args.command == "inspect":
        inspect(args.files)
    else:
        visualize(args.file, args.output, args.min_occupancy)


if __name__ == "__main__":
    main()
