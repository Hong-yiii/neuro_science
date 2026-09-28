# Getting Started Tasks

> **Current entry point: [September27 agreed direction](project-direction.md).**
> The active next-session checklist is immediately below. Phases0–6 and the
> September8 list farther down are historical onboarding/planning, not commands
> to repeat completed experiments. H2 is removed, not waiting in a stretch queue.
> The [completed-study/status index](professor_updates/path_generalization_20260907/README.md)
> preserves earlier evidence and claim limits.
> Fixed195 is a scope restriction, not a requirement for a195-column common panel.
> Original test exposure is permanent; old “locked/untouched” statements are dated.

This is the practical checklist for the prospective hippocampal path project.

## Active Next Session — September27 direction + September28 follow-up

- [ ] Follow the [agreed visual-evidence/temporal-validation plan](professor_updates/research_review_20260928/validation-plan.md): source/class support first, saved-result visualization second, bounded prefit protocol third. The review redraws historical data; new navigation and joint-model temporal decoding remain unexecuted.
- [ ] Specify cue/navigation windows, target support and comparable features for per-window decoding and separately frozen temporal/cross-phase generalization. Improving held-out cue decoding remains primary. Include all temporal readout/null fits in the budget; do not reuse an80-feature whole-cue decoder on an8-feature bin.
- [ ] Read [direction](project-direction.md), [hypotheses](research-questions.md)
  and [contract](analysis-contract.md). Retain H1, remove H2; no central-question pivot.
- [ ] Prepare the pseudopopulation construction artifact: provenance, a worked
  row example, source/phase lineage, shapes, counts and runnable mechanical checks.
  Reuse existing code/tests; do not launch a new broad validation campaign.
- [ ] Propose deliberate real-source folds before assembly, with class/endpoint
  support, temporal dependence, exposure and session/feature identity documented.
- [ ] Specify A's component assay and B's ordered graph-path target/feasibility;
  define valid B ground truth for the evaluation object, not an arbitrary source's path.
- [ ] Freeze one CEBRA-Time configuration, cue-only/joint arms, two checkpoint
  counts, PCA/LDA roles and a full bounded fit budget. No encoder-setting sweep.
- [ ] Resolve the **open decoder choice/training policy**, metrics, endpoint
  reference and necessary nulls/uncertainty; do not silently choose an MLP or rerun
  a broad readout grid. Earlier logistic and RBF decoders were already trained.
- [ ] Incorporate the mentor's phase-selectivity/rotation literature and intended
  validation once clarified. Do not invent a shared-latent hypothesis meanwhile.
- [ ] Obtain explicit run authorization and independent protocol/code review
  before biological fits, expanded data access or cleanup. This update runs nothing.

## How To Use This

- Mark tasks with `[x]` when completed.
- Add short notes under the task when something important changes.
- Prefer documenting verified current workflow over copying legacy instructions.
- Do not paste passwords, private keys, tokens, or raw protected data into this repo.

## Phase 0: Workspace Hygiene

- [x] Create top-level workspace at `~/neuro_science`.
- [x] Initialize parent git repo.
- [x] Add `Hippocampus.jl` as a submodule.
- [x] Add `PyHipp` as a submodule.
- [x] Add `AGENTS.md`, README, project context, and analysis contract.
- [ ] Add a remote for the parent workspace repo, if Hongyi wants this backed up.
- [ ] Decide whether active analysis code should live in this parent repo or in a separate package/repo.

## Phase 1: Access And Accounts

- [ ] Confirm NUS VPN access.
  - Done means: can connect to lab/network-only resources from offsite.
- [x] Add local `cortex` SSH shortcut.
  - Configured in `~/.ssh/config`; see `context/remote-mac-access.md`.
- [ ] Send SSH public key to lab for gateway access.
  - Done means: key is added to the gateway authorized keys.
- [x] Confirm `ssh cortex` login works.
  - Done means: can enter and exit the lab gateway without typing the gateway password.
  - Verified 2026-08-30; the same SSH account can read the lab share directly at
    `/volume1/Hippocampus/Data/picasso-misc`.
- [ ] Confirm VNC tunnel to one workstation works.
  - Done means: can connect to `vnc://localhost:1220` while the SSH tunnel is open.
- [ ] Confirm GitHub access to all relevant repos.
  - Repos to check: `Hippocampus.jl`, `PyHipp`, any RNN/Unity repo, any private lab repos.
- [ ] Confirm lab workstation access.
  - Done means: can log into assigned Mac workstation.
- [x] Confirm data-server access.
  - Done means: can mount or otherwise read the lab data location without exposing credentials in this repo.
  - Verified through `ssh cortex`; a bounded 20181105/session01 snapshot was
    copied under ignored `data/raw/lab_server/` and checksum-validated.
- [ ] Confirm who provides day-to-day unblock help.
  - Names/roles only; no private contact details unless Hongyi wants them stored.

## Phase 2: Codebase Orientation

- [x] Read `Hippocampus.jl/src/replay.jl` around `ViewAndPlaceRepresentationNew`.
  - Output: short note explaining how spikes map to trial behavioral sample indices.
- [x] Read `Hippocampus.jl/src/rawdata.jl` around `RippleData`.
  - Output: short note explaining marker/timestamp shape and trial boundaries.
- [x] Read `Hippocampus.jl/src/eyelink.jl` around `EyelinkData`.
  - Output: short note explaining gaze/fixation/saccade fields.
- [x] Identify where `UnityRaytraceData` is defined and loaded.
  - Output: note its file inputs and time/bin semantics.
- [x] Skim `Hippocampus.jl/src/glmfits.jl` for place/view/conjunctive analysis entry points.
  - Output: list candidate functions to revisit.
- [x] Skim `Hippocampus.jl/src/conjunctions.jl`.
  - Output: list existing conjunctive-coding concepts or functions.
- [x] Skim `PyHipp` for older equivalents.
  - Output: map Python reference modules to Julia concepts.

## Phase 3: Data Contract

- [x] Receive or locate the formatted biological data.
  - A small place-spatial-bin export is stored under ignored `data/raw/`.
- [x] Record initial biological data provenance and schema.
  - See `notes/data_inspection/place_spatial_bins_f1526be5.md`.
- [x] Identify the smallest known-good biological subset.
  - One exact-hash cell example has 395 readable trials; a second example uses a different hash.
- [x] Copy one bounded native/derived session bundle for importer development.
  - `20181105/session01`: 404 trials, six spike trains, Ripple markers, native
    Unity behavior, Eyelink, and raytrace data. See
    `notes/data_inspection/lab_server_20181105_session01.md`.
  - This is a software/data-feasibility snapshot, not yet a verified
    simultaneous population for H1.
- [ ] Confirm whether spike trains are already curated.
  - Done means: know whether spike sorting/manual inspection is out of scope.
- [ ] Obtain or verify cue-aligned data for the fixed 195 spatially selected
  cells, linked to subsequent paths.
  - Required: source trial, session, simultaneous group, cue window, start, goal,
    per-cell spike counts, success/timeout, and subsequent path samples.
  - Expanding to the upstream all-cell list is future work.
- [ ] Confirm which of the 195 cells form real simultaneous recording groups.
- [ ] Write or verify a loader that produces both analysis-contract objects.
  - Cue shape: `trial x cue_time_bin x cell`.
  - Path shape: `trial x navigation_sample`.
  - 2026-08-30: first all-session place195 importer/QC smoke passed for the
    current selected-cell snapshot. It produced cue spike events/counts and
    native Unity path samples for 58 sessions under
    `outputs/prospective_path_first_run/place195-all-sessions-20260830-v4/`.
    This remains a data-feasibility audit, not a verified H1 loader, because
    recording groups, task-label semantics, splits, graph/path representation,
    and QC inclusion rules are still open.

## Phase 4: Behavioral Feasibility Audit

- [ ] Create and hash source-trial train/validation/test assignments before
  adaptive graph, path-metric, exclusion, or contrast selection.
  - 2026-08-30: exploratory place195 source-trial split frozen at
    `outputs/prospective_path_first_run/place195-splits-20260830-v3/` with hash
    `11237c8c35af4b09b6d81c1994ff3f8b702d245d3a262f70413dab2b182973d1`.
    Keep unchecked for final H1 until labels and recording groups are verified.
- [ ] Reconstruct and visualize training/validation observed paths; keep test
  behavior untouched until the rules are frozen.
  - 2026-08-30: train/validation-only native Unity behavior QC summaries written
    to `outputs/prospective_path_first_run/place195-behavior-audit-20260830-v3/`;
    no visualization, graph, or route family yet.
- [ ] Count trials and successful trials per `(start, goal)` condition.
  - 2026-08-30: counted provisional marker-pair support only.
  - 2026-09-01: marker probe supports current minor digit as cue/goal and
    previous successful trial's minor digit as start; use `success_after_success`
    for endpoint-labelled primary audits. See
    `notes/data_inspection/place195_marker_semantics_probe_20260901.md`.
- [ ] Quantify within-condition path variation before choosing a model.
  - 2026-08-30: recorded train/validation native Unity duration/distance/path-row
    summaries by provisional marker pair.
  - 2026-09-01: authoritative fine geometry is filed at
    `docs/geometry/maze_mesh_centroids_1344.txt`; next step is train/validation
    mapped-path and route-signature support audit.
- [ ] Construct and verify maze adjacency from authoritative geometry.
- [ ] Convert paths to directed edge sequences and mark obligatory versus
  variable initial, middle, and terminal segments.
- [ ] Derive ordered corridor/branch signatures within each `(start, goal)` and
  count exact repeats before attempting clustering.
- [ ] Build a training/validation
  `recording_group x start_goal x route_family x design_split` support table and
  stop if a fixed 195-channel pseudopopulation is not supportable. Apply the
  frozen mapping to test once; do not redesign around test support.
- [ ] Quantify shared path components across different `(start, goal)`
  conditions.
- [ ] Compare same-start high/low-overlap, same-goal high/low-overlap, and—where
  available—different-endpoint paths sharing a middle segment.
- [ ] Audit correlations among path overlap, start, goal, cue identity, duration,
  session, and available sensory/motor variables.
- [ ] Propose a graph resolution without treating it as final.
- [ ] Compare candidate path representations and distance measures.
- [ ] Fit a leakage-safe `start + goal -> path` baseline.
- [ ] Decide what constitutes a meaningfully different path only after the audit.

## Phase 5: H1a — Incremental Path Information

- [ ] Use the immutable complete-trial splits defined before the behavioral
  audit; keep all source-trial derivatives together.
- [ ] Predict held-out paths from raw cue-period population activity.
- [ ] Repeat with PCA features and the same simple decoder.
- [ ] Compare `start + goal` against `start + goal + cue activity`.
- [ ] Run within-start-goal path/neural permutation controls.
- [ ] Run a trial-aware CEBRA-Time pilot and use the same downstream decoder.
- [ ] If justified, train behavior-conditioned CEBRA using path-only context.
- [ ] Keep path preprocessing and clustering inside training folds.

## Phase 6: H1b — Low-Dimensional Organization

- [ ] Test whether any H1a signal is stable across latent dimensions and sessions.
- [ ] Compare path-distance and latent-distance geometry on held-out trials.
- [ ] Before path-conditioned CEBRA, test whether raw or PCA cue-state geometry
  tracks shared directed path components in matched cross-condition contrasts.
- [ ] Test initial, middle, and terminal path-component overlap separately while
  matching or controlling start and goal.
- [ ] Separate low-dimensional-method failure from absence of path information.
- [ ] Characterize place, view, heading, action, speed, and trial-time confounds
  where those variables are available.
- [ ] Write a conservative result note with explicit claim boundaries.

## Former Phase 7: H2 — Removed

Artificial-agent comparison was removed from active scope on September27.
Historical implementation/reading notes are not pending tasks.

## Historical Proposed Tasks — September8, Superseded

The active next-session checklist is at the top. This list records the earlier
proposal; it is not authorization for another study.

1. [ ] Freeze a meaningful route-component definition and cue window using task
   meaning and training support, not a neural-outcome winner. Distinguish
   interior from anywhere presence explicitly.
2. [ ] Resolve outstanding task/clock/recording-group and nuisance metadata
   within the195 selected units; no excluded-unit recovery or scope expansion.
3. [ ] Measure independent-source population-pattern reproducibility and simple
   regularized decoding, with a neural-only positive control across conditions
   where its target varies. Individual-cell significance is not a gate.
4. [ ] Preserve the existing source-first, session-block/bin-aware pseudopopulation
   construction; quantify source uncertainty separately from synthetic-row noise.
5. [ ] Define a bounded comparison of representations and matched nulls, plus
   source-level reliability/injected-signal checks for any proposed collection.
6. [ ] Reserve genuinely unexposed observations prospectively if confirmation is
   intended. Do not rename inspected development resplits as pristine test data.

A large simultaneous population is not required for this condition-level lane.
The stricter exact-trial population/dynamics contract remains unchanged.
