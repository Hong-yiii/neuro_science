# AGENTS.md

This is Hongyi's neuroscience workspace. Treat it as a living context repo for lab onboarding, analysis notes, and references to active neuroscience code.

## Workspace Role

- This parent repo tracks context, notes, and references.
- External code repos are tracked as git submodules, not copied into the parent history.
- Large data, credentials, generated figures, and analysis artifacts should stay out of git unless Hongyi explicitly asks otherwise.

## Repositories

- `Hippocampus.jl`: primary Julia analysis code.
  - Upstream: `https://github.com/grero/Hippocampus.jl`
  - Active branch found from the remote: `updates6`
  - Hongyi referred to this as `update6`; verify branch names before assuming.
- `PyHipp`: older Python reference implementation.
  - Upstream found: `https://github.com/shihchengyen/PyHipp`
  - Hongyi referred to `PyHippocampus`, but that exact GitHub URL was not reachable from this environment.

## Scientific Context

The lab analyzes neural, behavioral, and eye-tracking data from hippocampus/navigation experiments.

Important data streams:

- `RippleData`: markers/timestamps recorded by the Ripple neural recording system.
- `EyelinkData`: markers, gaze samples, fixations, and saccades from the eye-tracking system.
- Unity/VirtualMaze data: behavioral position, view, gaze-on-maze, and trial timing.
- Raw spike trains: spike timestamps for each sorted unit/cell.

The most relevant Julia code for neural-behavior alignment is:

- `Hippocampus.jl/src/replay.jl`
- Type: `ViewAndPlaceRepresentationNew`
- Related types: `RippleData`, `EyelinkData`, `UnityRaytraceData`, `Spiketrain`

`ViewAndPlaceRepresentationNew` aligns spikes to behavior by:

1. Taking spike timestamps for a cell.
2. Using Ripple trial marker timestamps to identify the trial interval.
3. Using Unity/raytrace behavioral samples as the 1 ms behavioral time base.
4. Mapping each spike in a trial to the behavioral sample index at which it occurred.
5. Optionally retaining only spikes during fixation samples.
6. Returning per-trial spike times and their corresponding behavioral sample indices.

In the current code, the default `trial_start` is `2`, so alignment begins at the second trial marker and runs to marker `3`.

## Working Guidelines

- Read local context before changing code: `README.md`, this file, and `context/*.md`.
- Prefer adding dated notes under `context/` when learning something durable.
- Do not commit raw lab data, credentials, private links, tokens, large `.mat`/`.jld2` outputs, or generated figure/video dumps by default.
- If analyzing data from Hongyi, ask where it should live if unclear. Default to `data/` for ignored local data and `outputs/` for ignored generated results.
- For code changes inside submodules, work within that submodule's own git history. Do not make parent-repo commits that silently depend on uncommitted submodule changes.
- Keep explanations grounded in the actual code. For the Julia alignment path, start with `Hippocampus.jl/src/replay.jl` around `ViewAndPlaceRepresentationNew`.

## Useful Commands

Initialize this workspace after cloning elsewhere:

```sh
git submodule update --init --recursive
```

Check submodule branches:

```sh
git -C Hippocampus.jl status --short --branch
git -C PyHipp status --short --branch
```

Update the Julia reference to the latest remote branch tip:

```sh
git -C Hippocampus.jl fetch origin
git -C Hippocampus.jl checkout updates6
git -C Hippocampus.jl pull --ff-only
git add Hippocampus.jl
```

