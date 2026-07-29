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
- [ ] Skim `Hippocampus.jl/src/glmfits.jl` for place/view/conjunctive analysis entry points.
  - Output: list candidate functions to revisit.
- [ ] Skim `Hippocampus.jl/src/conjunctions.jl`.
  - Output: list existing conjunctive-coding concepts or functions.
- [ ] Skim `PyHipp` for older equivalents.
  - Output: map Python reference modules to Julia concepts.

## Phase 3: Data Contract

- [ ] Receive or locate the formatted biological data.
  - Store under ignored `data/` unless instructed otherwise.
- [ ] Record biological data provenance.
  - Output: `context/data-notes.md` with dataset name, source, date received, and schema notes.
- [ ] Identify the smallest known-good biological subset.
  - Ideally one session and a few cells.
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
3. [ ] Ask/confirm where the formatted biological data will arrive.
4. [ ] Ask/confirm where the RNN/Unity rollout or checkpoint lives.
5. [ ] Pick the first analysis language: Julia-first, Python-first, or bridge.
