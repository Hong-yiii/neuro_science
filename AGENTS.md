# AGENTS.md

This is Hongyi's neuroscience workspace. Treat it as a living context repo for lab onboarding, analysis notes, and references to active neuroscience code.

## Current Session Authority

Use `~/neuro_science` as the canonical working copy. Hongyi designated session
`01a08ab0-4fd4-704c-ac18-3b002e40c116` (begun September 10; consolidation resumed
September 13, 2026) as the current durable session; earlier sessions are
exploratory history. Read `docs/workspace.md` first for the consolidated paths,
PR status, recovery records and safe verification commands. Do not recreate old
sibling worktrees or restart experiments from historical pending-work flags.
Keep new durable decisions in Git-backed notes, not only in a chat transcript.

**September 26 review refresh:** read
`docs/reports/research-reset-20260926/README.md` for the latest three-session
synthesis and proposed decision/cleanup sequence. PR #7 is completed and merged;
PRs #8/#9/#10 remain open at inspection, and three retained review worktrees
exist under `work/`. Older single-worktree/PCA-pending statements are historical.
No new fits or worktree retirement are authorized by the review itself.

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

Hongyi is experienced in ML, deep learning, and mostly NLP, but is newer to neuroscience methods, terminology, and the observability limits of brain recordings. Explain neuroscience concepts by bridging from familiar ML ideas when helpful, and clearly separate directly measured signals from inferred constructs.

## Current Research Direction

The thesis-level question is whether hippocampal population activity during the
cue period contains information about the subsequently observed navigation path
beyond start and goal.

H1 is one hypothesis with two components:

- H1a: incremental held-out path information beyond start and goal;
- H1b: reproducible low-dimensional organization of that information.

Use **path** for the ordered movement through the maze. Reserve **trajectory
class** for the previous analysis's `(start, goal)` category. A maze graph is a
proposed path measurement method, not part of H1.

A later comparison with an artificial navigation agent is H2 and a stretch aim.
The intended comparison is not "RNN units are neurons" and does not claim shared
mechanisms from similar geometry alone.

Place-like, view/visual-like, and conjunctive coding remain supporting pipeline
checks, representation characterization, and confound controls. Position, view,
heading, goal, time in trial, action, and session can covary, so apparent path
information must be tested against start-goal baselines and shuffled/null or
conditional models.

Trial-specific H1 requires cue activity from a verified simultaneous population
linked to that same trial's start, goal, and observed path. A cross-session
pseudopopulation cannot support exact trial-specific claims. It remains a central,
valid candidate for **condition-level** prospective-path coding under source-safe
splits and endpoint/nuisance controls; a large simultaneous195 recording is not
a prerequisite for that work. Per-unit real-trial checks are complementary, not
an individual-cell-significance gate. Follow the current proposed direction in
`docs/reports/path-generalization-next-steps-20260908.md` and the evidence/status
index in `docs/professor_updates/path_generalization_20260907/README.md`. Frozen
protocols, failed attempts, historical reviews, and current recommendations must
not be conflated; never pool superseded output directories with accepted runs.

The bounded September8 preprocessing study is complete: read
`docs/reports/path-preprocessing-autoresearch-20260908-agent.md` and its human/HTML
companions. It tested20 observed recipes on147train+41historical-validation
sources (49unit IDs/13sessions). Stronger regularization helped probability loss,
but only2/5 endpoint diagnostics were positive,6→1 dominated, and the declared
nulls/source sensitivity did not support broad robustness.82,283 accepted model-fit
instances were forward-verified with zero new fits. Do not reopen tuning or treat
historical pending-review flags as current instructions. This does not reject
condition-level pseudopopulations, establish H1 absence, or test H1b/H2.

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
- Read `context/learner-profile.md` before teaching or explaining neuroscience methods.
- For the active prospective-path project, also read `docs/research-questions.md`, `docs/analysis-contract.md`, and `docs/getting-started-tasks.md`.
- Prefer adding dated notes under `context/` when learning something durable.
- Use `learning/` for neuroscience learning scaffolds, glossaries, and method explainers.
- Use `papers/` for paper notes and reading queues; do not commit copyrighted PDFs by default.
- Do not commit raw lab data, credentials, private links, tokens, large `.mat`/`.jld2` outputs, or generated figure/video dumps by default.
- If analyzing data from Hongyi, ask where it should live if unclear. Default to `data/` for ignored local data and `outputs/` for ignored generated results.
- For code changes inside submodules, work within that submodule's own git history. Do not make parent-repo commits that silently depend on uncommitted submodule changes.
- Keep explanations grounded in the actual code. For the Julia alignment path, start with `Hippocampus.jl/src/replay.jl` around `ViewAndPlaceRepresentationNew`.

## Research Rigor

Research code is not complete merely because it runs. Agents must preserve the
chain from scientific question to data, analysis, evaluation, and claim.

- Label work as a **software smoke test**, **exploratory analysis**, or
  **confirmatory analysis** before implementation. Do not promote smoke-test or
  exploratory output into scientific evidence.
- State the estimand or operational question, independent unit, inclusion and
  exclusion rules, baseline, null, split, metric, and strongest allowed claim
  before fitting a model.
- Audit provenance, schema, units, timing, trial identity, simultaneity, missing
  values, selection criteria, and preprocessing history. Stop rather than infer
  missing scientific metadata from filenames or array shapes.
- Split independent source trials or sessions before learned preprocessing. Fit
  normalization, dimensionality reduction, path construction learned from data,
  clustering, representation learning, and decoders on training data only.
- Keep bootstrapped copies and other derivatives of one source trial in the same
  fold. Treat adjacent time bins as dependent observations.
- Predefine simple baselines and falsification controls. Compare methods with a
  common held-out metric; training loss or an attractive embedding is not, by
  itself, evidence for the hypothesis.
- Record data hashes, code revision and dirty state, package versions, complete
  configuration, random seeds, device, input/output shapes, exclusions, and all
  attempted runs, including failures and negative results.
- Distinguish directly measured variables, derived representations, statistical
  associations, and biological interpretations in every result note.
- Require an independent review of both code and scientific assumptions before
  interpreting a new analysis. Review must check leakage, pseudoreplication,
  confounds, nulls, and whether the written claim exceeds the data.
- Never describe a pseudopopulation as simultaneous or use it to support exact
  trial-specific population-state, covariance, dynamics, intention, or mechanism
  claims.

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
