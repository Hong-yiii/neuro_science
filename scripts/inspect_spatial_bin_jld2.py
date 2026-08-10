#!/usr/bin/env python3
"""Inspect professor-provided spike_count_per_spatial_bin JLD2/HDF5 files.

JLD2 stores Julia objects as HDF5 datasets with object references. These files
store a scalar `data` object whose fields point to arrays:

- spikecounts: one reference per trial, each pointing to a vector of spike counts
- bins: one reference per trial, each pointing to matching spatial-bin labels
- trialidx: optional vector of original Julia trial indices
"""

from __future__ import annotations

import argparse
from pathlib import Path

import h5py
import numpy as np


def read_trials(fname: Path):
    with h5py.File(fname, "r") as f:
        data = f["data"]
        if not isinstance(data, h5py.Dataset):
            raise ValueError(f"expected 'data' to be a dataset in {fname}")
        record = data[()]
        spike_refs = f[record["spikecounts"]]
        bin_refs = f[record["bins"]]
        if not isinstance(spike_refs, h5py.Dataset) or not isinstance(
            bin_refs, h5py.Dataset
        ):
            raise ValueError(f"expected spikecounts and bins datasets in {fname}")
        if data.dtype.names and "trialidx" in data.dtype.names:
            trialidx = np.asarray(f[record["trialidx"]])
        else:
            trialidx = np.arange(len(spike_refs))

        for i in range(len(spike_refs)):
            spikecounts = np.asarray(f[spike_refs[i]])
            spatial_bins = np.asarray(f[bin_refs[i]])
            yield int(trialidx[i]), spikecounts, spatial_bins


def summarize(fname: Path) -> None:
    lengths = []
    totals = []
    nonzero = []
    max_counts = []
    all_bins = []
    examples = []

    for i, (trialidx, spikecounts, spatial_bins) in enumerate(read_trials(fname)):
        if spikecounts.shape != spatial_bins.shape:
            raise ValueError(
                f"trial {i} has mismatched shapes: "
                f"{spikecounts.shape} vs {spatial_bins.shape}"
            )
        lengths.append(len(spikecounts))
        totals.append(float(spikecounts.sum()))
        nonzero.append(int(np.count_nonzero(spikecounts)))
        max_counts.append(float(spikecounts.max()) if spikecounts.size else 0.0)
        if spatial_bins.size:
            all_bins.append(spatial_bins)
        if i < 5:
            nz = np.flatnonzero(spikecounts)[:8]
            examples.append(
                {
                    "i": i,
                    "trialidx": trialidx,
                    "length": len(spikecounts),
                    "spikes": float(spikecounts.sum()),
                    "unique_bins": len(np.unique(spatial_bins)),
                    "first_bins": spatial_bins[:8].astype(int).tolist(),
                    "first_spike_locs": [
                        (int(j), float(spikecounts[j]), int(spatial_bins[j]))
                        for j in nz
                    ],
                }
            )

    all_bins_arr = np.concatenate(all_bins) if all_bins else np.array([], dtype=int)

    print(f"file: {fname}")
    print(f"n_trials: {len(lengths)}")
    print(
        "time_bins_per_trial min/median/mean/max: "
        f"{min(lengths)} / {np.median(lengths):.1f} / "
        f"{np.mean(lengths):.2f} / {max(lengths)}"
    )
    print(
        "approx_trial_duration_seconds min/median/max: "
        f"{min(lengths) * 0.02:.2f} / {np.median(lengths) * 0.02:.2f} / "
        f"{max(lengths) * 0.02:.2f}"
    )
    print(
        "spikes_per_trial min/median/mean/max/total: "
        f"{min(totals):.1f} / {np.median(totals):.1f} / "
        f"{np.mean(totals):.2f} / {max(totals):.1f} / {sum(totals):.1f}"
    )
    print(
        "nonzero_20ms_bins_per_trial median/mean/max: "
        f"{np.median(nonzero):.1f} / {np.mean(nonzero):.2f} / {max(nonzero)}"
    )
    print(f"max_count_in_one_20ms_bin: {max(max_counts):.1f}")
    if all_bins_arr.size:
        print(
            "spatial_bin_id min/max/n_unique: "
            f"{int(all_bins_arr.min())} / {int(all_bins_arr.max())} / "
            f"{len(np.unique(all_bins_arr))}"
        )

    print("first_5_trials:")
    for row in examples:
        print(row)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="+", type=Path)
    args = parser.parse_args()
    for fname in args.files:
        summarize(fname)


if __name__ == "__main__":
    main()
