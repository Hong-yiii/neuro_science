# First Trial Run — Repo Understanding Before Running Anything

Date: 2026-08-30
Status: **understanding-only; no experiment/model run yet**

## What I did first

- Fanned out three read-only agents:
  - repo/context scout;
  - previous trial/run artifact investigator;
  - local data/schema/command investigator.
- Read the canonical local context myself:
  - `README.md`
  - `AGENTS.md`
  - `context/*.md`
  - `docs/research-questions.md`
  - `docs/analysis-contract.md`
  - `docs/getting-started-tasks.md`
  - `docs/dataset-card.md`
  - `docs/cebra_pilot/*`
  - `notes/data_inspection/*`
  - previous session notes under `notes/sessions/`
- Checked current filesystem inventory and previous output manifests.

## Repo role

This repo is not primarily an analysis package yet. It is a neuroscience workspace:

- `docs/` holds canonical research framing, contracts, and pilot specs.
- `context/` holds durable lab/code/project notes.
- `notes/` holds session and data-inspection notes.
- `scripts/` has small data lifecycle/JLD2 inspection helpers.
- `docs/cebra_pilot/implementation/` has approved **software-smoke** code.
- `Hippocampus.jl/` and `PyHipp/` are submodules/reference code, not code copied into this repo.
- `data/` and `outputs/` are ignored local state.

## Scientific target

The primary question is H1:

> Does hippocampal cue-period population activity predict the subsequently observed navigation **path** beyond start and goal?

Important terminology:

- Use **path** for ordered movement through the maze.
- Reserve **trajectory class** for the old `(start, goal)` category.
- A maze graph is only a proposed path ruler, not the hypothesis.
- CEBRA is only a candidate representation tool, not the scientific result.

The core operational comparison is:

```text
baseline: path ~ start + goal
neural:   path ~ start + goal + cue activity
```

Strong claim boundary:

- okay later, if gates pass: cue-period activity contains held-out information about subsequently observed path;
- not okay from decoding alone: intention, causal planning, literal graph representation, or shared mechanism with an artificial agent.

## Data contract I must respect

A real H1 trial needs the same source trial to link:

```text
cue-period population activity from verified simultaneous units
+ start_id / goal_id / cue_id
+ subsequent observed path samples
+ trial outcome/QC/provenance
```

Minimum conceptual objects:

```text
CuePopulation[trial, cue_time_bin, simultaneous_unit]
ObservedPath[trial, navigation_sample]
```

All derivatives of one source trial must stay in one split. Learned preprocessing, graph choices, clustering, PCA, CEBRA, and decoders must be fit inside training folds only.

## What previous trials actually were

The previous runs under `outputs/cebra_pilot/` are useful, but they are not scientific H1 evidence:

| Previous output | What it proved | Claim limit |
| --- | --- | --- |
| `trial-20260825-preprocessing-v4/` | synthetic path/neural/split framework works | software smoke only |
| `trial-20260825-current-export-v3/` | one-cell JLD2 loader reads 395 trials / 65,576 samples / 1,441 spikes | navigation-period one-cell export; no cue population |
| `trial-20260825-cebra-v2/` | CEBRA 0.6.1 CPU can fit/transform/save/reload `256 x 12 -> 256 x 3` synthetic data | API smoke only; not deterministic enough for exact embedding hashes |
| `trial-20260826-one-cell-cebra-v1/` | one intact local navigation trial can pass CEBRA API path: `134 x 1 -> 134 x 3`, one spike | one cell, one trial, no cue, no population, no path decoding |

The old previous-student analysis used cross-session pseudopopulations. That can support condition-level route/trajectory-class questions, but not exact same-trial population-state claims.

## Current local data reality

There is an important mismatch between recent notes and the current filesystem.

Docs/notes describe a bounded six-unit `20181105/session01` snapshot at:

```text
data/raw/lab_server/cortex_picasso_misc_20260830/
```

But that directory is **not present** locally right now.

What is present locally is:

```text
data/raw/lab_server/cortex_picasso_misc_place195_20260830/
```

Current inventory from the filesystem:

- 58 session directories, from `20180702` through `20181105`.
- 195 `spiketrain.mat` files total.
- 58 `rplparallel.mat` files.
- 58 `eyelink.mat` files.
- 58 native Unity `RawData_T1-400/*.txt` files.
- 0 `unity_raytrace.jld2` files in this snapshot.
- For `20181105/session01`, only one local `spiketrain.mat` is present: `array02/channel045/cell01`.

So the next run should first reconcile the documented six-unit snapshot versus the actual `place195` snapshot. I should not assume six 20181105 units are available just because the note says so.

## Current data that can likely support a first real-data smoke

The present `place195` snapshot may support a **data/importer feasibility smoke** across selected place cells and sessions:

- cue windows can likely be reconstructed from `rplparallel.mat` event 1 -> event 2;
- paths can likely be reconstructed from native Unity text rows after event 2;
- one or more selected cells are available per session;
- session-level pseudopopulation or recording-group-aware route-family work may be possible later.

But this is still below H1 unless we verify:

- exact marker semantics for `cue_id`, `goal_id`, and derived `start_id`;
- which units form genuine simultaneous recording groups;
- whether per-session unit lists are complete or only place-selected;
- trial QC rules, including known row anomalies;
- authoritative maze geometry/adjacency;
- sufficient route/path variation beyond start+goal.

## Key code entry points

Existing code to reuse before writing anything new:

- `scripts/data.py`
  - data dirs, manifests, simple JLD2 inspect/visualize.
- `scripts/inspect_spatial_bin_jld2.py`
  - current JLD2 trial reader.
- `docs/cebra_pilot/implementation/preflight.py`
  - previous smoke commands and manifest writing.
- `docs/cebra_pilot/implementation/contracts.py`
  - `CueNavigationTrial`, `MazeGraph`, path contract checks.
- `docs/cebra_pilot/implementation/paths.py`
  - simple path cleaning and overlap metrics.
- `Hippocampus.jl/src/replay.jl`
  - upstream reference for spike-to-behavior alignment; do not rerun unchanged because current docs note a `get_trial` return-arity mismatch.

## My current understanding of the first trial run

The safest first real-data run is **not** CEBRA and not path decoding.

It should be a small, reproducible **software/data-feasibility run** that:

1. reads one chosen session from `cortex_picasso_misc_place195_20260830/`;
2. parses Ripple trial marker codes/times;
3. parses native Unity rows into trial path samples;
4. parses available `spiketrain.mat` timestamps;
5. extracts cue-relative spike events/counts using `[event_1, event_2)`;
6. links all of that by source trial row;
7. emits a QC summary under a new ignored output directory;
8. clearly labels the result `software_smoke_only` or `exploratory_data_feasibility`, not H1 evidence.

The first target session should probably be `20181105/session01` because previous notes and prior outputs use it heavily, but the actual available local version has only one selected unit, so it cannot satisfy the multi-unit H1 contract by itself.

## Stop conditions before modeling

I should stop rather than model if:

- the documented six-unit snapshot cannot be found or recovered;
- marker rows do not match across streams;
- Unity trial segmentation cannot be linked to Ripple rows;
- cue windows cannot be identified cleanly;
- a run would treat one selected cell as a population;
- a pseudopopulation would be described as simultaneous;
- path processing would use test data or inferred graph rules prematurely.

## Immediate unknowns

1. Is `cortex_picasso_misc_place195_20260830/` now the intended dataset for this session, replacing the absent six-unit snapshot?
2. Should the first data smoke use only `20181105/session01`, or should it inventory all 58 sessions first?
3. Do we want a minimal throwaway script in `scratch/`, or a reusable importer under `scripts/`?
4. Is writing new ignored outputs under `outputs/cebra_pilot/` acceptable for this first trial run?

## What I attempted after this understanding note

Hongyi approved proceeding autonomously through all 58 sessions.

I added a reusable first-run importer/QC script:

```text
scripts/import_place195_sessions.py
scripts/test_import_place195_sessions.py
```

Successful current run:

```text
outputs/prospective_path_first_run/place195-all-sessions-20260830-v4/
```

Summary:

- 58/58 sessions parsed;
- 195/195 place-selective spiketrains matched to the professor-provided list;
- 23,901 trial rows;
- 23,200 success trials and 701 timeout trials;
- 545,905 cue-period spike events using half-open Ripple `[event_1, event_2)`;
- 5,891,109 native Unity path rows;
- 24 Ripple/Unity navigation-duration discrepancy flags;
- 1 cue-duration outlier;
- 1 Eyelink marker/time anomaly.

Detailed receipt: `notes/data_inspection/place195_all_sessions_import_20260830.md`.

Still not H1 evidence: no splits, graph, route families, PCA, CEBRA, decoder, or
scientific claim were created.
