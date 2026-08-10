# Getting Started Tasks

This is the practical onboarding checklist for the neuroscience/RNN project. Each task should be small enough to complete independently and leave behind a note, command, screenshot, or verified outcome.

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
- [ ] Write or verify a loader that produces the biological analysis contract.
  - Target shape: `trial x time_bin x cell`.
- [ ] Receive or locate RNN/Unity rollout data or checkpoint.
- [ ] Record model data provenance.
  - Output: `context/model-notes.md` with environment, checkpoint, seed, observation/action/reward notes.
- [ ] Write or verify a loader that produces the model analysis contract.
  - Target shape: `trial x time_bin x hidden_unit`.

## Phase 4: First Matched Analysis

- [ ] Define place bins.
  - Output: binning rule and occupancy correction choice.
- [ ] Define view/visual bins.
  - Output: decide between raycast bins, object identity, gaze bins, or another visual variable.
- [ ] Compute occupancy-normalized place maps for biological cells.
- [ ] Compute occupancy-normalized place maps for RNN hidden units.
- [ ] Compute view/visual tuning for biological cells.
- [ ] Compute view/visual tuning for RNN hidden units.
- [ ] Define conjunctive criterion.
  - Candidate: model comparison between position-only, view-only, additive, and interaction models.
- [ ] Run at least one null control.
  - Candidate: time shift, trial shuffle, or label shuffle.
- [ ] Produce first figure set in ignored `outputs/`.
- [ ] Write first interpretation note.
  - Keep claims descriptive unless controls are already done.

## Phase 5: Robustness And Scope

- [ ] Repeat first analysis across more biological cells.
- [ ] Repeat first analysis across more RNN units.
- [ ] Repeat across multiple RNN seeds or checkpoints, if available.
- [ ] Check sensitivity to bin size and smoothing.
- [ ] Check whether position, view, heading, action, goal, and trial time are separable.
- [ ] Decide whether the first deliverable is a notebook, script, report section, or talk figure.

## Immediate Next Tasks

Start here:

1. [x] Create `context/code-map.md` from the Julia alignment path.
2. [x] Identify `UnityRaytraceData` definition and write down its schema.
3. [x] Receive and inspect a small formatted biological-data example.
4. [ ] Confirm spatial-bin geometry, bin `0`, synchronized cell trials, and access to a complete session population.
5. [ ] Ask/confirm where the RNN/Unity rollout or checkpoint lives.
6. [x] Use Python first for loading, validation, and visualization; retain Julia as the upstream reference.
