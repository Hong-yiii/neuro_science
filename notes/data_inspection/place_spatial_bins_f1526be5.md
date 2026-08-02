# Place Spatial Bin Spike Counts

Created: 2026-08-03

Source message from professor:

- Place-selective cell list: `/Volumes/Hippocampus/Data/picasso-misc/place_selective_cells_new.txt`
- Example derived files: `spike_count_per_spatial_bin_f1526be5.jld`
- File format: JLD2/HDF5, readable with `h5py`
- Nominal binning: spike counts in 20 ms bins, with a matching spatial label per bin

Local pulled slice:

- `data/lab_exports/place_spatial_bins_f1526be5/place_selective_cells_new.txt`
- `data/lab_exports/place_spatial_bins_f1526be5/examples/20181105_session01_array01_channel029_cell01/spike_count_per_spatial_bin_f1526be5.jld2`
- `data/lab_exports/place_spatial_bins_f1526be5/examples/20181105_session01_array02_channel045_cell01/spike_count_per_spatial_bin_921269fc.jld2`

Important path note:

The professor's `/Volumes/Hippocampus/...` path corresponds to the lab Mac AFP
mount. Over SSH, the same share was mounted at:

```text
/Users/linhongyi/Hippocampus/...
```

## File Shape

The `f1526be5` example stores a scalar HDF5 dataset called `data` with fields:

- `spikecounts`
- `bins`
- `trialidx`

`spikecounts` and `bins` are arrays of object references. Each item points to one
trial vector.

Conceptually:

```text
cell_file
  -> trials
    -> spikecounts[t]: vector length T_t
    -> bins[t]:        vector length T_t
    -> trialidx[t]:    original trial index
```

For trial `t`, `spikecounts[t][k]` and `bins[t][k]` describe the same 20 ms time
bin:

```text
spikecounts[t][k] = how many spikes this cell fired in time bin k
bins[t][k]        = spatial bin occupied during time bin k
```

This is a ragged sequence because each trial can have a different number of time
bins.

## Example Summary

For:

```text
20181105/session01/array01/channel029/cell01/spike_count_per_spatial_bin_f1526be5.jld2
```

Observed locally:

- trials: 395
- time bins per trial: min 0, median 163, mean 166.02, max 433
- approximate trial duration: median 3.26 s, max 8.66 s
- spikes per trial: min 0, median 3, mean 3.65, max 19, total 1441
- nonzero 20 ms bins per trial: median 2, mean 2.70, max 14
- max spikes in one 20 ms bin: 5
- spatial bin ids: min 0, max 1342, 453 unique ids observed

## ML Translation

Treat each cell file as one output dimension observed across many variable-length
episodes:

```text
episode/trial -> timestep/bin -> scalar spike count
```

The matching `bins` vector is the label/covariate sequence:

```text
episode/trial -> timestep/bin -> spatial state id
```

For the RNN comparison, this is analogous to:

```text
trial -> time_bin -> hidden_unit_activation
trial -> time_bin -> spatial_bin_id
```

The key difference is that the biological side is sparse count data from one
recorded cell, while the RNN side is dense activation data from every hidden
unit.

## Analysis Implication

The first simple place-coding readout for one cell is:

1. group all 20 ms time bins by `spatial_bin_id`;
2. sum spikes in each spatial bin;
3. divide by occupancy time in that spatial bin;
4. compare the resulting rate map against shuffled/null maps.

This is the biological analogue of asking whether an RNN hidden unit's activation
is predictably high in particular spatial bins.
