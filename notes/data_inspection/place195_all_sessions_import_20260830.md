# Place195 all-session first importer/QC run

Date: 2026-08-30
Status: **data-feasibility audit; not scientific evidence**

## Operational question

Can the current local all-session place-selected native snapshot be decoded into
trial-linked cue spike and native Unity path records across all 58 sessions?

This run does not fit a model, build a graph, freeze splits, run PCA/CEBRA, or
test H1.

## Input root

```text
data/raw/lab_server/cortex_picasso_misc_place195_20260830/
```

Preflight counts from the successful run:

| Input type | Count |
| --- | ---: |
| sessions | 58 |
| `spiketrain.mat` | 195 |
| `rplparallel.mat` | 58 |
| `eyelink.mat` | 58 |
| native Unity `RawData_T1-400/session_*.txt` | 58 |
| `unity_raytrace.jld2` | 0 |
| place-selective list cells | 195 |
| selection-list/spiketrain matches | 195 |
| selection-list mismatches | 0 |

Selection list hashed in the run:

```text
data/raw/lab_exports/place_spatial_bins_f1526be5/place_selective_cells_new.txt
sha256: 6ff311aab2feb4eafdbd16270deba1c57e0dd0261ea175dd59b88e5d966af35e
```

## Successful output

```text
outputs/prospective_path_first_run/place195-all-sessions-20260830-v4/
```

Artifacts:

| File | Rows | Role |
| --- | ---: | --- |
| `source_files.csv` | 370 | parsed source file hashes, including selection list |
| `sessions.csv` | 58 | one QC summary row per session |
| `units.csv` | 195 | one selected-cell summary row per spike train |
| `trials.csv` | 23,901 | one source-trial QC row per parsed trial |
| `cue_counts.csv.gz` | 80,883 | trial-by-available-unit cue spike counts |
| `cue_spike_events.csv.gz` | 545,905 | cue-relative spike events |
| `path_samples.csv.gz` | 5,891,109 | native Unity path rows from event 2 through event 3 inclusive |
| `summary.json` | n/a | aggregate counts, hashes, versions, decisions |
| `decisions.md` | n/a | generated decision log |

Run command:

```sh
uv run python scripts/import_place195_sessions.py \
  --output-dir outputs/prospective_path_first_run/place195-all-sessions-20260830-v4
```

Environment recorded by the run:

```text
python: 3.13.2
numpy: 2.5.1
h5py: 3.16.0
scipy: 1.17.1
git revision: 4946c1b24ed2246f65c0ae50a795ca870c69a996
git dirty: true
```

## Main results

Across all 58 sessions:

| Quantity | Value |
| --- | ---: |
| parsed trials | 23,901 |
| successful trials | 23,200 |
| timeout trials | 701 |
| selected units | 195 |
| MATLAB v5 spike files | 176 |
| MATLAB v7.3/HDF5 spike files | 19 |
| cue-period spikes | 545,905 |
| trials with at least one cue spike among available selected units | 23,198 |
| native Unity path rows | 5,891,109 |

Trial counts are not always 400. They range from 400 to 493 trials per session;
`RawData_T1-400` and `SpecifiedRewardNo` must not be used as attempted-trial
counts.

## Decisions logged in the run

- Scientific status: `data_feasibility_audit_not_scientific_evidence`.
- Cue window: half-open Ripple-clock `[event_1, event_2)`.
- Path source: native Unity rows from event 2 through event 3 inclusive.
- Task labels: raw marker minor digit retained; cue/goal/start labels remain
  `inferred_from_marker_minor_digit_unverified`.
- Eyelink time units: divide by 1000 when median event1-event2 duration is
  greater than 10 raw units; this is for QC reporting only.
- Simultaneity: same-session/shared-clock is only
  `candidate_same_session_unverified`.
- Clock discrepancy QC: flag Ripple-vs-Unity navigation-duration absolute
  difference greater than 2 s.
- No modeling: no splits, graph labels, route families, PCA, CEBRA, decoders, or
  H1 claims.

## QC findings

Aggregate flags:

| QC flag | Count |
| --- | ---: |
| `ripple_unity_nav_duration_discrepancy_gt_2s` | 24 trials |
| `ripple_cue_duration_outside_0p5_1p5s` | 1 trial |
| `ripple_eyelink_marker_mismatch` | 1 trial |
| `eyelink_nonmonotonic_trial_time` | 1 trial |

Sessions with flags:

- `20180906_session01`: 4 Ripple/Unity navigation-duration discrepancies.
- `20180910_session01`: 3 discrepancies.
- `20180914_session01`: 1 Ripple cue-duration outlier.
- `20180920_session01`: 4 discrepancies.
- `20181010_session01`: 4 discrepancies.
- `20181022_session01`: 1 discrepancy.
- `20181031_session01`: 4 discrepancies.
- `20181101_session01`: one Eyelink marker/time anomaly at trial 212.
- `20181105_session01`: 4 discrepancies, including the previously known trial
  178 discontinuity.

No raw records were repaired or dropped by the importer. QC flags are attached to
trial rows.

## Failed/partial attempts retained

- `place195-all-sessions-20260830-v1/` failed after 57 sessions because
  `20181101/session01/eyelink.mat` uses root-level `triggers`/`timestamps`
  instead of `el/data/trial_codes`/`trial_timestamps`.
- `place195-all-sessions-20260830-v2/` passed all 58 sessions. A reviewer then
  required tighter raw-output protection and selection-list provenance.
- `place195-all-sessions-20260830-v3/` passed after reviewer-requested provenance fixes.
- `place195-all-sessions-20260830-v4/` is the current successful run, rerun after a lint-only parser cleanup so the kept output matches the final script.

## Scientific interpretation boundary

This run establishes that the current local place195 snapshot can be parsed into
trial-linked cue-spike and native-path records across all 58 sessions. It does
**not** establish prospective path coding.

Do not use this output to claim H1 until at least:

1. recording-group simultaneity and unit-list completeness are lab-confirmed;
2. cue/goal/start marker semantics are verified;
3. trial QC and inclusion rules are frozen;
4. source-trial splits are created and hashed before adaptive path decisions;
5. maze geometry/adjacency and a path representation are selected using
   training/validation behavior only;
6. start-goal baselines and nulls are implemented; and
7. an independent scientific/code review checks leakage, pseudoreplication,
   confounds, and claim language.

## Code added

- `scripts/import_place195_sessions.py`
- `scripts/test_import_place195_sessions.py`

The importer rejects output paths under `data/raw` or inside the input root and
writes generated artifacts only to ignored output directories.
