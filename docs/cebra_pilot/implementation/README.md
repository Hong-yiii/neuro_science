# First CEBRA Pilot Implementation

Status: **software framework present**  
Scientific status: **blocked on cue-aligned, trial-linked simultaneous population data**

This directory contains only first-run pilot code. It can run one explicitly
software-only CEBRA smoke on an intact current-export trial, but it does not
choose a graph metric, decode paths, or analyze that export scientifically.

## Interfaces

- `contracts.py`
  - `CueNavigationTrial`: immutable same-trial scientific record including
    population, cue/path linkage, timing, success/timeout, selection history,
    and previous-trial metadata or an explicit reason it is unavailable. Shape
    is always `cue_bin x unit`; at least two
    simultaneous units are required.
  - `MazeGraph`: explicit directed edges plus canonical SHA-256.
  - `CleanedPath`: raw valid path segments with repeats, collapsed route-shape
    segments, and audit counts.
- `neural.py`
  - `summarize_cue_activity`: mask-aware cue counts and exposure-normalized rates.
- `paths.py`
  - `clean_path`: split invalid `0`/`None` samples and nonadjacent transitions;
    no interpolation and no bridge edges.
  - `edge_jaccard`: directed-edge Jaccard distance; returns `None` when both
    paths have no edges.
  - `longest_shared_contiguous_directed_segment`: ordered shared edge run within
    segment pairs only.
- `splits.py`
  - `freeze_splits`: validates caller-supplied sample/source/split assignments,
    records session and simultaneous-group composition, and hashes canonical
    JSON. It does not invent a split policy.
- `manifest.py`
  - `RunManifest` plus safe writers that confine artifacts to new directories
    below `outputs/cebra_pilot/`.
- `preflight.py`
  - `synthetic-preprocessing`: synthetic neural/path/split smoke demo.
  - `jld2-smoke`: reuses `scripts.inspect_spatial_bin_jld2.read_trials`; always
    records `software_smoke_only` and the H1 stop reason.
  - `cebra-synthetic`: pinned CEBRA `0.6.1` CPU fit/transform/save/reload smoke
    with transform-fidelity and artifact-hash checks.
  - `cebra-jld2-smoke`: deterministically selects one intact eligible
    navigation-period trial and runs the same API check without crossing a trial
    boundary. It remains `software_smoke_only`.

## Environment

CEBRA is isolated in the `cebra-pilot` dependency group and pinned to `0.6.1`.
The workspace NumPy floor is `1.26.4` because CEBRA 0.6.1 requires NumPy below
2 on Windows; the lockfile resolves the platform-appropriate version.

## Stage Order

1. Provenance/schema check of real cue-linked simultaneous population data.
2. Freeze caller-supplied source-trial splits and record the split hash.
3. Training/validation behavior audit and graph/path metric selection.
4. Raw and train-fitted PCA baselines.
5. Boundary-safe CEBRA-Time only if the installed API can respect trials.
6. Optional path-conditioned CEBRA after behavior and baseline gates.
7. Independent review before any scientific interpretation.

## Claim Limits

The current local JLD2 export is one selected cell's navigation-period data. It
can smoke-test a loader and one intact CEBRA input, but it cannot instantiate
`CueNavigationTrial`, test H1, or estimate data efficiency. See
[`DATA_EFFICIENCY.md`](DATA_EFFICIENCY.md) for sample-size planning.

All run directories must be new children of ignored `outputs/cebra_pilot/`.
Run the checks from the repository root:

```sh
python -m unittest discover -s docs/cebra_pilot/implementation/tests
python -m docs.cebra_pilot.implementation.preflight synthetic-preprocessing \
  --output-dir outputs/cebra_pilot/<new-preprocessing-run>
uv run --group cebra-pilot \
  python -m docs.cebra_pilot.implementation.preflight cebra-synthetic \
  --output-dir outputs/cebra_pilot/<new-cebra-run>
uv run --group cebra-pilot \
  python -m docs.cebra_pilot.implementation.preflight cebra-jld2-smoke \
  data/raw/lab_exports/place_spatial_bins_f1526be5/examples/\
20181105_session01_array01_channel029_cell01/\
spike_count_per_spatial_bin_f1526be5.jld2 \
  --output-dir outputs/cebra_pilot/<new-one-cell-run>
```

Both current-export commands always record the H1 data stop and
`software_smoke_only` status.
