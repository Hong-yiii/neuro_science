# Local Data Workspace

This directory is the single local home for research data used by this workspace.
The **directory rules are version-controlled; the data files are not**. Lab data
can contain sensitive information and is usually too large for Git.

`Hippocampus.jl/data/` belongs to the upstream Julia package. Do not place our
working datasets there: changing it mixes lab data with a submodule that has its
own Git history. Our copies belong here, under the repository-level `data/`.

## Directory layout

```text
data/
├── README.md          # tracked policy (this file)
├── raw/               # immutable copies received from the lab
│   └── lab_exports/
├── interim/           # reversible intermediate conversions
├── processed/         # analysis-ready tables produced by scripts
└── manifests/         # local inventories: provenance, sizes, checksums
```

| Stage | Meaning | May scripts overwrite it? | Example |
| --- | --- | ---: | --- |
| `raw` | Bytes as received from the lab | **No** | `.jld2`, cell lists |
| `interim` | Decoded or reshaped data that is not analysis-ready | Yes | flattened trial records |
| `processed` | Stable inputs consumed by analyses | Yes, reproducibly | rate-map table |
| `outputs` | Figures, statistics, reports—not input data | Yes | place-field plot |

The distinction is like an ML pipeline: `raw` is the downloaded dataset,
`interim` is tokenized/cache data, `processed` is the model-ready tensor, and
`outputs` contains evaluation artifacts.

```mermaid
flowchart LR
    L[Lab share] -->|copy once| R[data/raw]
    R -->|decode + validate| I[data/interim]
    I -->|derive analysis table| P[data/processed]
    P --> A[analysis code]
    A --> O[outputs]
    R -. inventory .-> M[data/manifests]
    I -. inventory .-> M
    P -. inventory .-> M
```

## One entry point

Use `scripts/data.py` for local data operations:

```sh
# Create the Python environment and standard data directories
uv sync
uv run python scripts/data.py init

# Record what exists, including SHA-256 checksums
uv run python scripts/data.py manifest

# Inspect one professor-provided spatial-bin JLD2 file
uv run python scripts/data.py inspect \
  data/raw/lab_exports/place_spatial_bins_f1526be5/examples/CELL/file.jld2

# Create a four-panel overview under ignored outputs/
uv run python scripts/data.py visualize \
  data/raw/lab_exports/place_spatial_bins_f1526be5/examples/CELL/file.jld2
```

The manifest is a **local receipt**, not a backup. A checksum proves that two
files contain identical bytes; it does not explain the scientific meaning of
the file. Scientific schema and interpretation belong in `notes/data_inspection/`
or `context/`.

## Rules for a neuroscience beginner

1. **Never edit `raw/`.** If a correction is necessary, keep the original and
   generate a corrected file under `interim/`.
2. **Record provenance.** Note who supplied the dataset, when, its original lab
   path, and any message describing preprocessing.
3. **Separate measured from derived values.** A spike count is derived from
   detected and sorted electrical events; a firing-rate map is derived again by
   dividing counts by occupancy. Neither is a direct image of a memory or idea.
4. **Keep trial and time alignment.** Neural activity only becomes interpretable
   relative to behavior when timestamps and trial boundaries match.
5. **Do not treat a curated list as an unbiased sample.** The current list is
   explicitly place-selective; it cannot estimate how common place cells are in
   the full recorded population.
6. **Do not commit data or manifests by default.** They may expose participant,
   session, workstation, or lab path information even when the neural arrays are
   not personally identifying.

## Current biological export

The current files contain one cell per file and ragged trials:

```mermaid
flowchart TD
    F[cell JLD2 file] --> T1[trial 1]
    F --> T2[trial 2]
    F --> TN[trial N]
    T1 --> S[spikecounts: count per 20 ms]
    T1 --> B[bins: spatial-bin ID per 20 ms]
```

Aligned entries `spikecounts[t][k]` and `bins[t][k]` mean: during trial `t`, in
time window `k`, the sorted cell produced that many detected spikes while the
subject occupied that spatial bin. See
`notes/data_inspection/place_spatial_bins_f1526be5.md` for verified details.

## Native lab-server snapshots

Two related 2026-08-30 native-data receipts are documented:

- `data/raw/lab_server/cortex_picasso_misc_20260830/` — earlier bounded
  `20181105/session01` six-unit dependency bundle described in
  `notes/data_inspection/lab_server_20181105_session01.md`. That exact directory
  is not present in the current checkout.
- `data/raw/lab_server/cortex_picasso_misc_place195_20260830/` — current local
  all-session place-selected snapshot used for the first importer/QC run. It
  contains 58 `session01` directories, 195 selected `spiketrain.mat` files, one
  Ripple `rplparallel.mat`, one Eyelink `eyelink.mat`, and one native Unity
  `RawData_T1-400/session_*.txt` file per session. It contains no
  `unity_raytrace.jld2` files.

The all-session importer/QC entry point is:

```sh
uv run python scripts/import_place195_sessions.py \
  --output-dir outputs/prospective_path_first_run/<new-run-dir>
```

It writes ignored outputs only: source-file hashes, session/unit/trial QC, native
Unity path samples, cue spike events, cue counts, a summary, and logged
decisions. It is a **data-feasibility audit**, not H1 evidence.

Next-step split and behavior-QC commands are:

```sh
uv run python -m scripts.place195_split_and_behavior_audit freeze-splits \
  --import-dir outputs/prospective_path_first_run/place195-all-sessions-20260830-v4 \
  --output-dir outputs/prospective_path_first_run/<new-split-run>

uv run python -m scripts.place195_split_and_behavior_audit behavior-audit \
  --import-dir outputs/prospective_path_first_run/place195-all-sessions-20260830-v4 \
  --split-dir outputs/prospective_path_first_run/<split-run> \
  --output-dir outputs/prospective_path_first_run/<new-behavior-audit-run>
```

The current split hash is recorded in
`notes/data_inspection/place195_split_behavior_audit_20260830.md`.

Do not treat the 195 selected cells as an unbiased sample or a verified
simultaneous population. Do not silently drop clock-discrepant trials such as
20181105 trial 178; retain them with explicit QC flags.
