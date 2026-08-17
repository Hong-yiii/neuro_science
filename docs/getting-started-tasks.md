# Getting Started Tasks

This is the practical checklist for the prospective hippocampal path project and its later artificial-agent extension. Each task should be small enough to complete independently and leave behind a note, command, screenshot, or verified outcome.

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
- [ ] Confirm `ssh cortex` login works.
  - Done means: can enter and exit the lab gateway without typing the gateway password.
- [ ] Confirm VNC tunnel to one workstation works.
  - Done means: can connect to `vnc://localhost:1220` while the SSH tunnel is open.
- [ ] Confirm GitHub access to all relevant repos.
  - Repos to check: `Hippocampus.jl`, `PyHipp`, any RNN/Unity repo, any private lab repos.
- [ ] Confirm lab workstation access.
  - Done means: can log into assigned Mac workstation.
- [ ] Confirm data-server access.
  - Done means: can mount or otherwise read the lab data location without exposing credentials in this repo.
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
- [ ] Confirm whether spike trains are already curated.
  - Done means: know whether spike sorting/manual inspection is out of scope.
- [ ] Obtain or verify a cue-aligned biological export linked to subsequent paths.
  - Required: source trial, session, simultaneous group, cue window, start, goal,
    population spike counts, success/timeout, and subsequent path samples.
- [ ] Confirm which cells form real simultaneous populations.
- [ ] Write or verify a loader that produces both analysis-contract objects.
  - Cue shape: `trial x cue_time_bin x cell`.
  - Path shape: `trial x navigation_sample`.

## Phase 4: Behavioral Feasibility Audit

- [ ] Reconstruct and visualize every available observed path.
- [ ] Count trials and successful trials per `(start, goal)` condition.
- [ ] Quantify within-condition path variation before choosing a model.
- [ ] Construct and verify maze adjacency from authoritative geometry.
- [ ] Propose a graph resolution without treating it as final.
- [ ] Compare candidate path representations and distance measures.
- [ ] Fit a leakage-safe `start + goal -> path` baseline.
- [ ] Decide what constitutes a meaningfully different path only after the audit.

## Phase 5: H1a — Incremental Path Information

- [ ] Define complete-trial train/test splits before preprocessing.
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
- [ ] Separate low-dimensional-method failure from absence of path information.
- [ ] Characterize place, view, heading, action, speed, and trial-time confounds
  where those variables are available.
- [ ] Write a conservative result note with explicit claim boundaries.

## Phase 7: H2 — Artificial-Agent Stretch Aim

- [ ] Receive or locate the Unity agent rollout or checkpoint.
- [ ] Record environment, checkpoint, seed, observation, action, and reward provenance.
- [ ] Export cue/planning-equivalent hidden states and subsequent agent paths.
- [ ] Apply the same path representation, splits, baselines, and controls.
- [ ] Predefine whether comparison means information, geometry, or dynamics.
- [ ] Repeat across multiple seeds or checkpoints where available.

## Immediate Next Tasks

Start here:

1. [ ] Draft the exact cue-aligned population export request from
   `docs/analysis-contract.md`.
2. [ ] Confirm access to all recorded units and real simultaneous groups, not
   only the selected place-cell files or historical pseudopopulation.
3. [ ] Confirm authoritative maze geometry/adjacency and the meaning of bin `0`.
4. [ ] Audit real paths and within-`(start, goal)` variability.
5. [ ] Choose one provisional path representation and one start-goal baseline.
6. [x] Use Python first for loading, validation, and visualization; retain Julia
   as the upstream reference.
