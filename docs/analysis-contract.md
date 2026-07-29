# Analysis Contract

This document defines the shared shape that biological and model data should expose before matched analyses are written.

## Unit Of Analysis

The common unit is:

```text
trial x time_bin x unit
```

For biological data, `unit` means a curated neuron/cell and values are spike counts or firing rates.

For model data, `unit` means an RNN hidden dimension and values are hidden activations.

## Required Trial-Time Variables

Each trial should provide a time-indexed table with:

- `trial_id`
- `time_ms` or `time_bin`
- `position_x`
- `position_y` or `position_z`
- `heading`
- `view_bin` or visual-scene identifier
- `gaze_x`, when available
- `gaze_y`, when available
- `fixation_mask`, when available
- `action`, for model data and biological behavior when defined
- `goal` or target identity, when available
- `reward_or_timeout`, when available

## Biological Side

Expected source concepts from `Hippocampus.jl`:

- `RippleData`: neural recording markers and timestamps.
- `EyelinkData`: gaze, fixation, saccade, and marker data.
- `UnityRaytraceData`: behavioral/view samples.
- `Spiketrain`: spike timestamps for a cell.
- `ViewAndPlaceRepresentationNew`: maps spikes to per-trial behavioral sample indices.

Minimum biological export for matched analysis:

```text
trial_id, time_bin, cell_id, spike_count, position, heading, view_bin, fixation_mask
```

## Model Side

Expected source concepts from the RNN/Unity environment:

- Unity environment state;
- agent observation;
- action;
- reward;
- done/trial boundary;
- RNN hidden state at each time step;
- task variables that can be binned in the same way as biological data.

Minimum model export for matched analysis:

```text
trial_id, time_bin, hidden_unit_id, activation, position, heading, view_bin, action, goal
```

## Shared Derived Objects

Analyses should be able to build:

- occupancy maps;
- unit rate or activation maps;
- place tuning scores;
- view/visual tuning scores;
- joint place-view maps;
- train/test splits by trial;
- null distributions.

## Open Decisions

- Whether model time bins should be exactly 1 ms or resampled to match behaviorally meaningful frames.
- Whether biological spike counts should be binary per millisecond, binned counts, or smoothed rates for the first analysis.
- Whether visual coding should be defined by gaze bins, allocentric view bins, object identity, raycast bins, or multiple versions.
- Whether the first implementation should be in Julia, Python, or a mixed bridge.

