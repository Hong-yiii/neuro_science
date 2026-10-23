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

**October19 review deliverable:** the owner requested an executed professor-facing
saved-artifact notebook and a PR (not a merge). Start with
`report/endpoint_walkthrough.ipynb` and `report/README.md`. The notebook replays only
the accepted October7 observed endpoint seeds0–2 from saved standardized cue: six
CEBRA encoders, three PCA states and495 fitted readouts; no fits, raw access or null
replay. Public outputs contain aggregates only. Source assembly/scaler fitting and
historical controls are inherited, not newly reproduced. A fresh native kernel passed
all14 code cells with the original two-thread numerical budget and unchanged tolerances.
This narrow approval does not authorize other private replay or new studies. The
manuscript editorial pass is included; unrelated design HTML and current-state files
remain untouched. See workspace status and the PR for publication, not old task queues.

**October15 session closure / publication (historical):** PR19 merged at `a169edf`. The owner authorized
publishing and merging [PR20](https://github.com/Hong-yiii/neuro_science/pull/20),
including reviewed helper extraction and the README showcase, to conclude this session.
The PR records the authoritative merge result; do not resume historical task queues.
Start with `README.md`, `docs/workspace.md` and `src/neuro/README.md`.
`docs/software-design.md` is the current architecture reference; `docs/codebase-design.html`
is a preserved older preview. Next: sharpen the retrospective, then agree the companion
notebook's target and inputs. No new fits, private access or further architecture
migration is authorized by merging. Long logs remain under `history/operations/`.

**Standing package scope — October15:** `src/neuro/` supports the latest maintained
experiments end to end, including their necessary input validation, scientific controls,
provenance and verification. Historical reproducibility, old callers or possible future
notebook use alone do not justify package features or compatibility layers. Keep obsolete
experiments and any historical-only compatibility outside the package; preserve their
records/snapshots without promising support from current package APIs. October15 cleanup
(independently reviewed) extracted only currently required
helpers into `neuro.raw_io`, `neuro.neural_inputs`, `neuro.cebra_solver` and `neuro.geometry`,
then removed `neuro.legacy_adapters`. Older implementations remain outside package
support. Do not delete
still-required helpers or weaken scientific safeguards to remove a legacy-named module.
The future notebook's package use remains open; it does not define package scope yet.

**October12 package consolidation (historical checkpoint):** start at
`report/README.md`, `history/README.md`,
`src/neuro/README.md` and `docs/reorganization.md`. Seven weekly overviews and eleven
byte-preserved HTML moves remain implemented. Full-trial transfer, endpoint-time and
cue-time scientific bodies now live in `neuro.studies`; old `scripts/cebra_*.py` paths
are thin module/CLI aliases. Shared split access and equivalent execution/provenance
seams were packaged with a temporary legacy adapter, superseded by the October15
active-helper extraction above. Historical script implementations remain unchanged;
current source closure includes only active helpers and justified external CLI aliases.
Keep distinct label/lineage objects distinct and launchers thin. Historical approvals
are not valid automatically for relocated/current source; no old hashes were rewritten.
The frozen HTML's pre-existing checksum mismatch is preserved. Whether/how the future
companion notebook uses this package remains open, depending on its scope and complexity.
No notebook is created now. No new fits/private replay.

**October12 report-first filing (earlier checkpoint):** Hongyi wants the current retrospective and
its actually used evidence to be the main working flow. Start with
`docs/reports/cebra-retrospective-20261012/README.md` and `docs/reports/README.md`.
The exact frozen reading HTML is versioned alongside the manuscript package;
its original local copy remains under `outputs/cebra-retrospective-20261012/`.
**Next sequence:** sharpen the report, then scope the intended companion notebook.
Its target/cohort and input contract remain open; using this package is optional,
not a requirement to make the notebook more complex.
Computational transparency is distinct from formal neural-state observability;
no new fits or private-data access are authorized by publishing.
Retired onboarding/RNN/V4–V5 checklists are filed under
`docs/reports/archive/early-work-20261012/`, with old-path pointers. Initial-trial
records are historical, not a run queue. Pilot helpers and mixed contract/smoke
tests still support later analyses: preserve their executable paths and coverage.
Use `scripts/README.md` to distinguish publishing from scientific execution.
This filing does not authorize private-artifact moves, worktree removal or new fits;
the future agenda below remains a separate proposal.

**October11 steering — retrospective closure and reusable latent models:** read
`docs/reports/cebra-research-synthesis-20261011.md` (Document1: proposed rigorous
retrospective, evidence/ablation/figure coverage) and
`docs/cebra-observability-agenda-20261011.md` (Document2: proposed future direction).
Hongyi wants these narrowed separately, then a condensed future-work section folded
into Document1. Stop pursuing the previous path goal as the default objective;
record its bounded conclusions without declaring H1 false. H2 remains removed.
The new ambition is an estimable, reusable hippocampal task-state representation
with CEBRA central but not a required winner. Task recovery, readout transfer,
predictive-state estimation and formal model-relative observability are distinct.
Candidate hypotheses/data routes/protocols remain proposals, not authorization for
fits, saved-model reanalysis, raw access or downloads. Local main contains PR15
merge `4862267`; preserve unrelated local work and retained artifacts/worktrees.
The October9 handoff remains history, not a competing run queue.

**September27 prior direction — historical, superseded for next-work priority:** read
`docs/project-direction.md`, then `docs/research-questions.md` and
`docs/analysis-contract.md`. H1 remains; H2/artificial-agent comparison is removed
from active scope. Narrow future encoder comparisons to CEBRA-Time, cue-only
versus joint cue/navigation training, two predefined checkpoints, deliberate
source folds, and PCA/LDA baselines. Decoder choice remains open. Component-level
graph decoding is the simpler assay; ordered graph-path prediction remains the
desired capability. Pseudopopulation construction documentation/checks are the
next methods artifact; phase-selectivity/rotation interpretation awaits mentor
clarification. These are scope decisions, not a frozen run protocol or permission
to fit. Do not substitute the September26 review's proposed pivot for this decision.

**September28 agreed follow-up:** read
`docs/professor_updates/research_review_20260928/validation-plan.md` and its
self-contained `review.html`. Prioritize source/class support → saved-result plots
→ bounded prefit protocol. Add cue-time and navigation-time decoding and separate
frozen temporal/cross-phase transfer validation; improving cue decoding remains
the primary comparison. Freeze the full prediction pipeline across evaluation
windows/phases within an encoder, not weights across independently fitted encoders.
Window-specific decoding is not temporal generalization. Detailed settings remain
open; shipping the plan/plots does not authorize new biological fits.

Consolidated PR #11 merged into `main` at `e8f2308`, including #8/#9/#10 and
preserved local studies. GitHub marked #8/#9 merged; #10 was subsequently closed
as already included, without deleting its branch/worktree. Three retained review
worktrees and ignored artifacts remain. New sessions should use updated `main`
after the direction follow-up merges, not resume historical branch task queues.
See `docs/workspace.md` and `docs/reports/review-integration-20260926.md`.

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

Use the October11 two-document plan above. Document1 closes and synthesizes the
completed endpoint/path/ablation work; Document2 develops a reusable latent-model
research question with explicit observability/measurement limits. Narrow the
question and admissible data before choosing another model. Historical raw-LDA
goal temporal generalization exists; matched October CEBRA temporal/cross-phase
transfer is still unexecuted. All source-safe evaluation and biological claim
limits below remain in force. No new experiment is queued.

### Previous prospective-path framing — retained history

The prior thesis-level question was whether hippocampal population activity during
the cue period contains information about the subsequently observed navigation
path beyond start and goal.

H1 is one hypothesis with two components:

- H1a: incremental held-out path information beyond start and goal;
- H1b: reproducible low-dimensional organization of that information.

Use **path** for the ordered movement through the maze. Reserve **trajectory
class** for the previous analysis's `(start, goal)` category. A maze graph is a
proposed path measurement method, not part of H1.

H2, the artificial-navigation-agent comparison, was removed from active scope
on September27. Do not plan agent training, brain–RNN matching or a replacement
H2 from historical notes. Shared cue/navigation encoder parameters do not prove
shared biological geometry or a rotation between phases.

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
an individual-cell-significance gate. Follow the agreed direction in
`docs/project-direction.md`; the September8 plan is background, not the active
run queue. The evidence/status index remains
`docs/professor_updates/path_generalization_20260907/README.md`. Frozen
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
- For the next session, start with the manuscript package and report-focused index named in the October12 filing note, plus `docs/analysis-contract.md`. Consult `docs/cebra-observability-agenda-20261011.md` for separately proposed future research. `docs/research-questions.md` retains prior framing; `docs/getting-started-tasks.md` is now an archive pointer, not a run queue.
- Prefer adding dated notes under `context/` when learning something durable.
- Use `learning/` for neuroscience learning scaffolds, glossaries, and method explainers.
- Keep relevant citations with the report or methods note, not a second paper-reading queue. Local `papers/*.pdf` remain protected and ignored; do not commit or delete copyrighted/lab PDFs as filing cleanup.
- Do not commit raw lab data, credentials, private links, tokens, large `.mat`/`.jld2` outputs, or generated figure/video dumps by default.
- If analyzing data from Hongyi, ask where it should live if unclear. Default to `data/` for ignored local data and `outputs/` for ignored generated results.
- For code changes inside submodules, work within that submodule's own git history. Do not make parent-repo commits that silently depend on uncommitted submodule changes.
- Keep explanations grounded in the actual code. For the Julia alignment path, start with `Hippocampus.jl/src/replay.jl` around `ViewAndPlaceRepresentationNew`.

## Research Rigor

Research code is not complete merely because it runs. Agents must preserve the
chain from scientific question to data, analysis, evaluation, and claim.

- **Report standard agreed September28:** scientific documents must stand on
  their own with data-backed figures, not only prose/headline scores. Include
  source/class distributions, performance with seed/fold detail, count and
  normalized confusion matrices, time-resolved decoding and controls where
  available. Each figure states target/cohort, source versus synthetic counts,
  split, units/time reference, decoder, metric/baseline, uncertainty meaning,
  provenance and claim limits. Mark unavailable analyses explicitly; do not fit
  new models merely to fill a plotting gap. Schematic figures are not data.
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
