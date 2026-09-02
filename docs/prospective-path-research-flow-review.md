# Prospective-Path Research Flow Review

Date pinned: 2026-08-31  
Status: high-level review of completed work; next step is behavior-only graph/path design  
Branch/commit pinned from previous session: `place195-import-qc-splits` / `c517b91 Add place195 import QC and split audit`  
PR: <https://github.com/Hong-yiii/neuro_science/pull/1>

This is the single start-here review doc. It summarizes the work already done and points to the detailed receipts instead of replacing them.

## Current verdict

The workspace now has enough local data plumbing to audit trial-linked cue spikes and native Unity paths across the fixed 195 selected-cell snapshot. It does **not** yet have enough verified metadata to run H1 modeling or interpret CEBRA.

Allowed next work:

```text
train/validation-only behavior design + metadata requests
```

2026-09-01 update: the centroid geometry file is now filed as authoritative at
`docs/geometry/maze_mesh_centroids_1344.txt`; the primary 4-neighbor fine-graph
hash is `1e7804c5d2167dcd8709a9760d8917034cb60e36e936229fad9056b1dae0f9ad`.
Graph/path rules are documented in `docs/graph-path-formalization.md`; visual
examples are in `docs/graph-path-similarity-examples.html`. Marker semantics
were probed in
`notes/data_inspection/place195_marker_semantics_probe_20260901.md`: current
marker digit is supported as cue/goal, and previous successful trial marker as
start. Current timeout trials are dropped for the planned experiment. Full-195
pseudopopulation support under the current split fails even for `(start, goal)`
validation, so `(start, goal, route_family)` needs support-declared subsets or a
new stratified exploratory split; see
`notes/data_inspection/fixed195_pseudopop_support_probe_20260901.md`.

Blocked work:

```text
PCA, decoders, CEBRA, final route families, H1 claims, simultaneous-population claims
```

Blockers:

1. marker-to-cue/start/goal semantics are data-supported but still lack formal lab/protocol provenance for confirmatory claims;
2. recording groups and unit-list completeness are not lab-confirmed;
3. coarse corridor/branch path mapping and support are not audited yet;
4. QC inclusion/exclusion rules are not frozen for H1;
5. start-goal baselines/nulls cannot be final until endpoint labels and route rules are frozen.

## Canonical review trail

Read order for full context:

1. this file;
2. `docs/research-questions.md` — canonical H1/H2 framing;
3. `docs/analysis-contract.md` — required trial/data shapes;
4. `docs/dataset-card.md` — verified dataset facts and limits;
5. `docs/cebra_pilot/verification.md` — scientific/design review trail;
6. `docs/cebra_pilot/implementation/REVIEW.md` — implementation review/closeout;
7. `notes/data_inspection/place195_all_sessions_import_20260830.md` — importer/QC receipt;
8. `notes/data_inspection/place195_split_behavior_audit_20260830.md` — split + behavior audit receipt;
9. `/tmp/neuro_science_handoff_graph_cebra_2026-08-31.md` — previous-session handoff for graph/grouping before CEBRA.

Latest reviewer pin: the handoff aligns with repo docs, but should include `docs/cebra_pilot/verification.md`, `docs/cebra_pilot/implementation/REVIEW.md`, `docs/cebra_pilot/formalization.md`, and `docs/cebra_pilot/cebra-pilot-plan.md` as required context.

## Research logic

Primary H1:

```text
Does cue-period hippocampal population activity predict the same trial's later path beyond start and goal?
```

Operational comparison:

```text
baseline: path ~ start + goal
neural:   path ~ start + goal + cue activity
```

Key rule: the independent unit is the complete `source_trial_id`. Every cue bin, path sample, plot, route label, pseudotrial, bootstrap derivative, PCA feature, CEBRA row, and decoder input derived from one source trial must stay in the same split.

A graph is only a behavior ruler:

```text
Unity path -> reviewed nodes/edges -> ordered directed path representation
```

CEBRA is only a later representation tool. It is not the hypothesis and is not evidence unless raw/PCA baselines, held-out decoding, nulls, and leakage checks already work.

## What has been done

| Work | Output | What it proves | Claim limit |
| --- | --- | --- | --- |
| Research pivot to prospective path | `docs/research-questions.md`, `docs/analysis-contract.md` | H1/H2 and required data shapes are explicit | framing only |
| CEBRA/math formalization | `docs/cebra_pilot/formalization.md`, `docs/cebra_pilot/cebra-pilot-plan.md` | execution order and claim ceilings are documented | no data result |
| CEBRA pilot framework | `docs/cebra_pilot/implementation/` | contracts, path cleaning, split hashing, manifests, preflights exist | software smoke only |
| Spatial-bin ordering audit | `notes/data_inspection/spatial_bin_ordering.md` | JLD2 bin IDs are Meshes.jl mesh IDs, not row-major grid IDs; bin `0` is invalid | older JLD2 export only |
| One-cell JLD2 loader smoke | `outputs/cebra_pilot/trial-20260825-current-export-v3/` | loader reads one selected-cell navigation export | no cue period, no population |
| Synthetic CEBRA smoke | `outputs/cebra_pilot/trial-20260825-cebra-v2/` | CEBRA 0.6.1 CPU fit/transform/save/load works for `256 x 12 -> 256 x 3` | API smoke only |
| One intact local CEBRA smoke | `outputs/cebra_pilot/trial-20260826-one-cell-cebra-v1/` | one intact trial can run `134 x 1 -> 134 x 3`, save/load diff `0.0` | one cell, one trial, one spike; no biology claim |
| All-session place195 importer/QC | `outputs/prospective_path_first_run/place195-all-sessions-20260830-v4/` | current selected-cell snapshot can be parsed into trial-linked cue-spike and Unity-path records | data-feasibility only |
| Source-trial split freeze | `outputs/prospective_path_first_run/place195-splits-20260830-v3/` | exploratory 70/15/15 complete-trial split exists and is hashed | not final H1 split |
| Train/validation behavior audit | `outputs/prospective_path_first_run/place195-behavior-audit-20260830-v3/` | behavior summaries exclude locked test and carry leakage guards | no graph, no route family, no H1 |

## Current data and shapes

### Required H1 shape

Final H1 requires the same source trial to expose:

```text
CuePopulation[trial, cue_time_bin, verified_simultaneous_unit]
ObservedPath[trial, navigation_sample]
start_id, goal_id, cue_id, outcome, trial history, QC, provenance
```

Current data does not yet satisfy that final contract because simultaneity, marker semantics, and graph geometry are unverified.

### Current active snapshot

Input root:

```text
data/raw/lab_server/cortex_picasso_misc_place195_20260830/
```

Inventory:

| Item | Count |
| --- | ---: |
| sessions | 58 |
| selected `spiketrain.mat` files | 195 |
| `rplparallel.mat` files | 58 |
| `eyelink.mat` files | 58 |
| native Unity `RawData_T1-400/session_*.txt` files | 58 |
| `unity_raytrace.jld2` files | 0 |

Importer output:

```text
outputs/prospective_path_first_run/place195-all-sessions-20260830-v4/
```

| Artifact | Rows | Shape meaning |
| --- | ---: | --- |
| `source_files.csv` | 370 | parsed source file hashes |
| `sessions.csv` | 58 | one QC row per session |
| `units.csv` | 195 | one selected-cell row per spike train |
| `trials.csv` | 23,901 | one source-trial QC/provenance row |
| `cue_counts.csv.gz` | 80,883 | one cue-window total per available `trial x selected unit` |
| `cue_spike_events.csv.gz` | 545,905 | one cue-relative spike event row |
| `path_samples.csv.gz` | 5,891,109 | one native Unity navigation sample row |

Main counts:

| Quantity | Value |
| --- | ---: |
| parsed trials | 23,901 |
| successful trials | 23,200 |
| timeout trials | 701 |
| cue-period spike events | 545,905 |
| trials with at least one cue spike | 23,198 |
| native Unity path rows | 5,891,109 |

Important schema fields:

- `trials.csv`: `session_id`, `source_trial_id`, `trial_index`, `previous_source_trial_id`, Ripple/Unity/Eyelink marker codes, unverified inferred cue/goal/start fields, outcome, durations, Unity path summaries, QC flags.
- `cue_counts.csv.gz`: `source_trial_id`, `cell_id`, `cue_spike_count`, cue window start/end.
- `cue_spike_events.csv.gz`: `source_trial_id`, `cell_id`, `cue_relative_time_s`, `spike_time_ripple_s`.
- `path_samples.csv.gz`: `source_trial_id`, `navigation_sample`, Unity row/time, `position_axis1`, `position_axis2`, `heading`, marker.

### Split and locked test data

Split output:

```text
outputs/prospective_path_first_run/place195-splits-20260830-v3/
split hash: 11237c8c35af4b09b6d81c1994ff3f8b702d245d3a262f70413dab2b182973d1
```

Policy: complete `source_trial_id`, within session, contiguous 20-trial blocks, deterministic SHA-256 assignment, no neural/path/graph/route labels used.

| Split | Trials | Success | Timeout |
| --- | ---: | ---: | ---: |
| train | 16,859 | 16,395 | 464 |
| validation | 3,401 | 3,309 | 92 |
| locked test | 3,641 | 3,496 | 145 |

The test split is locked. It was not used for behavior/path metric outputs. This split is still exploratory, not final H1, until verified labels and recording groups exist.

### Behavior audit data

Behavior audit output:

```text
outputs/prospective_path_first_run/place195-behavior-audit-20260830-v3/
```

| Artifact | Rows | Role |
| --- | ---: | --- |
| `trial_behavior_qc_train_validation.csv` | 20,260 | per-trial raw Unity path summary for train/validation only |
| `support_by_session_split_train_validation.csv` | 116 | session x split support and path medians |
| `support_by_inferred_marker_pair_train_validation.csv` | 144 | provisional support by raw marker-pair fields |
| `qc_flags_train_validation.csv` | 3 | QC flags among train/validation trials |
| `behavior_audit_summary.json` | n/a | hashes, counts, guardrails, stop conditions |

Findings:

- 3,641 locked-test trials were not used in path audit outputs.
- 167 train/validation rows had previous-trial-derived marker labels blanked because the previous source trial is locked test.
- 546 train/validation rows still have matching provisional start/current marker digits. Do not treat marker-derived fields as true start/goal labels.

### Older one-cell JLD2 export

Best-verified file:

```text
data/raw/lab_exports/place_spatial_bins_f1526be5/examples/20181105_session01_array01_channel029_cell01/spike_count_per_spatial_bin_f1526be5.jld2
```

Shape:

```text
one selected cell
  -> 395 ragged retained trials
    -> 20 ms navigation samples
      -> scalar spike count + mesh-topological spatial-bin ID
```

Counts: 65,576 samples, 1,441 spikes, one empty trial, spatial bin `0` invalid. This export starts at cue offset and cannot test cue-period H1.

## Preparation already locked in

- Use Python first for loading, validation, visualization, and small audits.
- Keep raw data under ignored `data/`; generated artifacts under ignored `outputs/`.
- Preserve raw records; attach QC flags rather than silently repairing/dropping.
- Do not use locked test behavior to select graph granularity, cleaning, route labels, path metrics, exclusions, targets, or contrasts.
- Build path labels from behavior only, never jointly with cue neural activity.
- Start with raw cue features and train-fitted PCA before any path-conditioned CEBRA.
- Treat cross-session pseudopopulations as exploratory condition-level objects, not simultaneous populations.
- Pairwise path/RDM entries are dependent; uncertainty/nulls must operate on source trials, blocks, sessions, or animals.

## The current research problem

The next problem is not “run CEBRA.” It is:

```text
Can train/validation Unity paths support a leakage-safe path representation and grouping rule that is identifiable beyond start/goal, and do verified recording groups support any fixed-195 path-family pseudopopulation design?
```

This splits into two pieces:

1. metadata that must come from lab/protocol/source code review:
   - formal provenance for marker-to-cue/start/goal semantics;
   - true simultaneous/session block definitions and whether the 195 list is complete for each block;
2. behavior-only design using train/validation rows:
   - plot raw Unity paths by `source_trial_id`;
   - inspect paths by provisional marker pair only as an unverified diagnostic;
   - define a reviewed position-to-node or coarse graph mapping;
   - convert paths to ordered directed edge/corridor signatures;
   - count exact signatures before clustering;
   - audit support by `recording_group x start_goal x route_family x split`;
   - freeze only contrasts that train/validation can identify.

If marker semantics or adjacency stay unresolved, outputs must remain `exploratory_only` and cannot become H1 evidence.

## Minimal next workflow

1. Draft the lab metadata request from `docs/analysis-contract.md`.
2. Inspect `path_samples.csv.gz` only through the frozen train/validation split.
3. Make the smallest behavior-only plotting/audit script:
   - no neural features;
   - no CEBRA/PCA/decoder;
   - no locked test rows;
   - output under `outputs/prospective_path_first_run/`.
4. Write a data-inspection receipt with hashes, exact filters, and remaining blockers.
5. Get independent review before freezing any graph/path/grouping rule.

## Claim language to use

Safe now:

> The current place195 snapshot supports selected-cell importer/QC and train/validation-only behavior feasibility work.

Unsafe now:

> The 195 cells form a simultaneous population.

Unsafe now:

> Marker-derived fields are verified start/goal labels.

Unsafe now:

> CEBRA found a prospective path manifold.

Future safe claim, only if gates pass:

> Cue-period population activity improves held-out prediction of subsequently observed path beyond verified start and goal, under the stated split, nulls, and confound controls.
