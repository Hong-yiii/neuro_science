# Workspace and recovery

Updated October26, 2026. Canonical checkout: **`~/neuro_science`**. Owner: Hongyi.
Read [agent instructions](../AGENTS.md) before changing scientific code or artifacts.

## Current state

- **October26 research teaching revamp:** the owner asked for defensible notebooks
  that teach the research and expose decisions, construction skew, model learning,
  3D geometry, decoder performance and historical joint-training impact. Begin with
  [the standalone research guide](../notebooks/00_research_guide.ipynb), whose figures
  are existing public aggregates, then the three practical notebooks. Model grids
  remain cue-only and unchanged; no new biological fits or private replay accompany
  this revision. The owner requested publishing the revision to existing
  [draft PR22](https://github.com/Hong-yiii/neuro_science/pull/22); GitHub owns its
  publication/review status. [Scope and verification](notebook-research-guide-20261026.md).
- **October26 owner-approved compact unbinned source:** `data/cue-source-v1/`
  contains all195 units' spikes, all58 sessions' event/timing records and cleaned frozen
  assignment metadata in ordinary Git (about54.7MB). No Release was created/uploaded;
  no LFS or new license. [Scope and checksums](../data/README.md) describe intentional
  dense-stream omissions, native precision and public identity limits. The old full
  sanitized archive remains local under `work/lab-source-publication-20261026/`.
  Compact notebook mode needs no old private native/import/result files. Metadata
  selection reproduces historical assignments/embargo; non-fitting reconstruction
  passed fresh Notebook A execution with fitting blocked, with zero selected-contributor
  Eye missing events. Independent artifact/privacy and code reviews closed all findings;
  25 focused no-fit tests passed. Source notebooks retain empty outputs; B/C were not run. New bounded receipts live at
  `work/compact-cue-source-20261026/`; [dated ledger](compact-cue-source-20261026.md)
  separates executed checks from unexecuted notebook evidence. Originals, runtimes,
  models, stash and unrelated work remain untouched.
- **October24 publication request:** prepare a draft PR on `feat/fresh-input-notebooks`
  with the structure and review guide in its description. The owner authorized code,
  invented notebooks and reviewed documentation/aggregate notes, not private input or
  result artifacts, a merge, a new license, a package-registry release or further fits.
  GitHub owns the authoritative draft/review status. Unrelated current-state notes and
  the retained stash remain outside this PR.
- **October23 direction:** the owner requested shareable pseudopopulation, PCA/LDA and
  CEBRA modules with runnable notebooks that compute from supplied source inputs, show
  target/split/assembly construction and support dataset ablations—not depend on old
  fitted results. [Read-only reconnaissance and proposed implementation plan](notebook-package-plan-20261023.md)
  records module boundaries, validity limits and release gates. The owner subsequently
  approved building and running it end to end on real data. [Execution ledger](shareable-notebooks-execution-20261023.md)
  and [bounded protocol](shareable-notebooks-protocol-20261023.md) own current status:
  public APIs/adapter and the then-[executed invented notebooks](../notebooks/README.md)
  were implemented and independently reviewed (October26 source regeneration clears
  those old outputs; that earlier evidence does not attest the current cells). Installed-wheel/no-CEBRA checks passed;
  the exact-shape benchmark and authorized real run completed under hard resource limits.
  Real runb0497792d:6CEBRA/10PCA/78logistic/12LDA/6000updates and180loaded-model replay
  checks,115seconds, no swap/OOM; independent final results/privacy review accepted
  the run with a nonblocking confusion-title overlap limitation.
  New private results: `outputs/fresh-notebooks-20261023/real/`. Preserve the accepted
  replay below as historical evidence; no additional fit is queued. Code publication
  follows the separate draft-PR request above.
- Historical review artifact: [executed endpoint notebook](../report/endpoint_walkthrough.ipynb).
  October19 authorized observed-only saved-input replay passed in a fresh native kernel:
  six CEBRA encoders, three PCA states,495 readouts and990 score rows, zero fitting.
  [Runtime, verification and privacy boundaries](../report/README.md#saved-artifact-notebook-execution-and-boundaries).
  The notebook and manuscript editorial pass are now on local `main` at `3f84018`,
  the PR21 merge inspected October23 after the owner's pull. The original October19
  request was a PR, not a merge; that earlier publication status is historical.
  PR20 remains in ancestry at `19ae1b0`.
- [Current report](../report/README.md) → [weekly history](../history/README.md) →
  [source/evidence catalog](reports/README.md).
- [PR19](https://github.com/Hong-yiii/neuro_science/pull/19) is merged into `main`
  at `a169edf` (verified October12). PR15's studies remain in ancestry.
- Reorganization checkpoint: **`ebe8256`**, branch
  `refactor/report-first-weekly-layout`, based on that merged main. This branch is
  delivered through [PR20](https://github.com/Hong-yiii/neuro_science/pull/20).
  The owner authorized publication and merge to close this session; consult the PR
  for the authoritative merge result before selecting a branch for new work.
- [Implementation status](reorganization.md): report promoted, seven weekly overviews,
  eleven byte-preserved HTML relocations, shared split access and the full-trial/
  endpoint-time/cue-time [`neuro.studies` package](../src/neuro/README.md). October15's
  reviewed active-helper cleanup removes the legacy adapter and packages
  only necessary raw IO/binning/solver/geometry dependencies. Historical-only experiment
  implementations remain unchanged outside package support; other evidence migrations remain open.
- Package consolidation from `cc0527e` is committed at **`8c98b52`** and pushed to
  [PR20](https://github.com/Hong-yiii/neuro_science/pull/20), followed by reviewed
  helper extraction and README/showcase improvements in the same PR.
  Earlier local validation/review receipts describe the historical pre-commit state.
  [Software design](software-design.md) is the maintained engineering reference;
  the preserved HTML preview may lag the package.
- October15's open notebook scope is superseded by the narrow October19 saved-input
  walkthrough above. It uses current package operations without an architecture migration.
  Only a separate notebook-tooling overlay was installed under
  `scratch/endpoint-notebook-runtime/`; the retained scientific runtime is unchanged.
  No service, new fit, raw reconstruction or null replay was added.

The historical durable-session designation is
`01a08ab0-4fd4-704c-ac18-3b002e40c116`. It identifies the consolidation history, not
permission to resume old task queues. Store current decisions in Git-backed notes.

## Preserve before changing

- Untracked `docs/reports/current-state-20260927/` and the pre-existing dirty
  `docs/codebase-design.html` are unrelated to the package change and preserved
  byte-for-byte. Do not absorb, overwrite or remove them opportunistically.
- The frozen report's pre-existing checksum difference is preserved in the checkpoint.
  Its exact-integrity check still fails; both original versions are retained under
  `work/reorganization-weekly-audit/before-build/`. See the report README for hashes.
- Preserve `data/`, `outputs/`, `scratch/`, `work/`, local PDFs, session history and
  submodules. Git alone cannot recover ignored data, models or predictions.
- Four worktrees remain registered: canonical root plus `work/issue-6-pca`,
  `work/cebra-full-trial-transfer`, and `work/cebra-time-teach`. Merged branches are
  not deletion permission; issue6 retains unique ignored artifacts.

Safe inventory commands: `git status --short --branch` and `git worktree list`.
Do not auto-start old runners, preview servers or historical processes.

## Git recovery versus private data recovery

| Recovery point | What it preserves |
| --- | --- |
| `b55b10f` | Pre-reorganization source/report layout and original frozen Git blob |
| `ebe8256` | First implemented reorganization slice and preserved working frozen file |
| [Relocation manifest](../history/relocations.json) | Eleven old/new reading paths and exact hashes |
| `work/reorganization-weekly-audit/` | Local scout audits, baseline copies, review and validation scripts |
| `work/workspace-consolidation-20260910/before-consolidation.bundle` | Historical pre-consolidation Git refs/history, not private inputs |
| `work/workspace-consolidation-20260910/originals/` | Original source/document preservation and hashes |
| `outputs/workspace-consolidation-20260910/local-files.json` and `MIGRATED_SHA256SUMS` | Earlier private/local-file relocation inventory |
| `work/retired-worktrees/` | Retained local files from retired exploratory siblings, not active worktrees |

Consult the [consolidation ledger](reports/workspace-consolidation-20260910/README.md)
and [complete preserved workspace log](../history/operations/navigation-20261012/workspace-before-tidy.md.txt)
for old→new private artifact paths, failed-attempt identities and recovery procedures.
Those dated commands describe historical conditions; review current ownership and
obtain scope before replaying or migrating anything. Do not recreate removed siblings.

## Execution and environment boundary

`pyproject.toml`/`uv.lock` now support the installable public APIs and optional extras;
`requirements-replay.txt` and retained `scratch/v6-v9-runtime/` describe a different
historical runtime. October23 validation used a task-owned installed-wheel runtime
under `work/shareable-notebooks-20261023/`, borrowing dependencies read-only. Filing
is not environment consolidation. Do not install, upgrade or delete either by default.

Use [focused software/presentation checks](reorganization.md#focused-validation-no-broad-scientific-runner).
The broad `scripts/check_research_software.py` has an unexcluded private-embedding test;
its name is not a data-free execution guarantee. Changed current imports/hash collectors
are not the exact historical runner. Replay requires the recorded source identity,
approval and private inputs; do not update old hashes to make relocated code pass.

## October5 follow-up — frozen cue-time readouts completed

This heading is retained because the frozen endpoint protocol links to it. The completed
October5 study separates **fixed 1,000-update predictive scores** from descriptive saved
checkpoint geometry; duration was not a performance factorial. It performed 5,040
single-bin readouts and 504 whole-cue replays, with zero encoder/PCA refits.
[Original execution ledger](reports/cebra-cue-time-readout-20261005/execution.md) and
[weekly overview](../history/week-2026-10-05-cue-and-endpoint-readouts/README.md) retain
cohort, controls, limitations and later publication history. This is not a rerun queue.

## Historical navigation

[Operations archive](../history/operations/README.md) preserves the former long-form
workspace and publishing logs byte-for-byte. Scientific interpretation belongs in the
owning study/report; current authority belongs here and in `AGENTS.md`, not in old
“next steps,” draft-status statements or expired preview instructions.
