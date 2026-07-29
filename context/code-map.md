# Code Map

Created: 2026-07-29

This map records the current understanding of the active Julia alignment path in `Hippocampus.jl`.

## Primary Alignment Chain

```text
Spiketrain
    +
RippleData
    +
UnityRaytraceData
        ->
ViewAndPlaceRepresentationNew
```

The output is a per-trial representation of spike events and the behavioral/view sample index associated with each spike.

## Key Types

### `Spiketrain`

Location:

```text
Hippocampus.jl/src/spikedata.jl
```

Fields:

- `timestamps::Vector{Float64}`
- `reference::String`
- `components::Int64`

Loader behavior:

- Loads `spiketrain.mat` if present.
- Falls back to `spiketrain.csv` if present.
- Returns an empty spike train otherwise.

Important unit note:

- `ViewAndPlaceRepresentationNew(spikes::Spiketrain, ...)` divides `spikes.timestamps` by `1000.0`, so the stored spike timestamps are treated as milliseconds before alignment.

### `RippleData`

Location:

```text
Hippocampus.jl/src/rawdata.jl
```

Fields:

- `triggers::Matrix{Int64}`
- `timestamps::Matrix{Float64}`
- `header::Dict`

Level and file:

- Level: `session`
- File: `rplparallel.mat`

Role:

- Provides trial marker codes and marker timestamps from the neural recording system.
- In the alignment path, `rp.timestamps[i, trial_start]` is the trial start time and `rp.timestamps[i, 3]` is the trial end boundary.

### `EyelinkData`

Location:

```text
Hippocampus.jl/src/eyelink.jl
```

Fields include:

- trial triggers and timestamps;
- analog gaze sample times;
- gaze x/y;
- fixation start/end;
- saccade start/end and positions.

Level and file:

- Level: `day`
- File: `eyelink.mat`

Role:

- Supplies eye-tracking markers and fixation masks.
- `UnityRaytraceData` uses `EyelinkData` to split raytrace/behavior data into trials and match fixation status to behavioral time points.

### `UnityRaytraceData`

Location:

```text
Hippocampus.jl/src/replay.jl
```

Fields:

- `analogtime::Vector{UInt64}`
- `positions::Matrix{Float32}`
- `directions::Vector{Float32}`
- `triggers::Matrix{Union{UInt64,Missing}}`
- `rawgaze::Vector{Matrix{Float64}}`
- `gaze::Vector{Matrix{Float64}}`
- `position::Vector{Matrix{Float64}}`
- `head_direction::Vector{Vector{Float64}}`
- `timestamps::Vector{Vector{Float64}}`
- `fixated_object::Vector{Vector{String}}`
- `fixating::Vector{Vector{Bool}}`
- `unityfile::String`

Level and file:

- Level: `day`
- Saved file: `unity_raytrace.jld2`
- Default raytrace input: `unityfile_eyelink_new.csv`

Role:

- Stores trial-indexed behavioral and visual/raycast data.
- `numtrials(gdata)` is `length(gdata.gaze)`.
- `get_trial(gdata, i; trial_start=...)` returns time, gaze, position, fixation mask, fixated object, and head direction for a trial.

The current `get_trial` return values are:

```text
tt, tg, tp, fixmask, fo, hd
```

where:

- `tt`: trial-relative timestamps in seconds;
- `tg`: gaze/fixated 3D points;
- `tp`: position samples;
- `fixmask`: Boolean mask of fixation samples, filtered to exclude objects like hint/cue images and robot by default;
- `fo`: fixated object labels;
- `hd`: head direction samples.

### `ViewAndPlaceRepresentationNew`

Location:

```text
Hippocampus.jl/src/replay.jl
```

Fields:

- `events::Vector{Vector{Float64}}`
- `placeviewidx::Vector{Vector{Int64}}`

Level and file:

- Level: `cell`
- File: `view_and_place_representation.jld2`

Default:

- `trial_start=2`

Role:

- Aligns a cell's spike train to trial-indexed Unity/raycast behavioral samples.
- For each trial:
  1. load trial time, gaze, position, fixation mask, object labels, and head direction via `get_trial`;
  2. offset behavioral trial time to begin at zero;
  3. use `RippleData.timestamps` to select spikes between marker `trial_start` and marker `3`;
  4. subtract the Ripple trial-start timestamp from spike times;
  5. for each spike, find the last behavioral time sample before that spike;
  6. keep the spike if it maps to a valid sample and either `fixation_only=false` or the sample is a fixation;
  7. store the spike time in `events` and the behavioral sample index in `placeviewidx`.

## First Analysis Implication

For a matched biological/RNN analysis, the biological side can be flattened from:

```text
trial -> spike events -> behavioral sample indices
```

into a table like:

```text
trial_id, time_bin, cell_id, spike_count, position, head_direction, gaze/view, fixated_object, fixation_mask
```

The RNN side should expose the same trial-time variables plus hidden activations:

```text
trial_id, time_bin, hidden_unit_id, activation, position, head_direction, gaze/view, action, goal
```

## Open Questions

- Is `unityfile_eyelink_new.csv` the current canonical raytrace source for the dataset Hongyi will receive?
- Should view coding be based on `gaze`, `fixated_object`, raycast bins, or all of them as separate analyses?
- Should the first biological analysis use the default `trial_start=2`, or should this be confirmed with Prof Yen for the formatted data?
- Does the formatted data already flatten `ViewAndPlaceRepresentationNew`, or will we need to run/load this Julia path directly?

