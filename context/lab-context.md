# Lab Context

Created: 2026-07-29

## Current Understanding

The lab analyzes navigation experiments combining:

- neural recordings from Ripple,
- behavioral traces from Unity/VirtualMaze,
- gaze, fixation, and saccade data from Eyelink,
- sorted spike trains for individual cells.

The current primary analysis code is the Julia repo `Hippocampus.jl`. The older Python repo is useful as historical/reference code, but is not actively used.

## Julia Alignment Path

Hongyi highlighted `ViewAndPlaceRepresentationNew` as the key type for aligning neural data with behavior.

Location:

```text
Hippocampus.jl/src/replay.jl
```

High-level behavior:

- Load spike timestamps for a cell.
- Load trial marker timestamps from `RippleData`.
- Load behavioral/gaze samples from `UnityRaytraceData`, whose timing is aligned through Unity/Eyelink processing.
- For each trial, select spikes between the relevant Ripple markers.
- Convert each spike time into a behavioral sample index.
- Store one spike list and one behavioral-index list per trial.

Important detail from the code: `trial_start=2` by default. That means the aligned trial window begins at the second marker and ends at the third marker unless overridden.

## Repo Notes

- `Hippocampus.jl` remote has branch `updates6`, not `update6`.
- The exact URL `https://github.com/shihchengyen/PyHippocampus` was not reachable here.
- The reachable Python reference repo is `https://github.com/shihchengyen/PyHipp`.

