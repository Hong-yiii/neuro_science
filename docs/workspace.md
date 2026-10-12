# Workspace and recovery

Updated October12, 2026. Canonical checkout: **`~/neuro_science`**. Owner: Hongyi.
Read [agent instructions](../AGENTS.md) before changing scientific code or artifacts.

## Current state

- [Current report](../report/README.md) → [weekly history](../history/README.md) →
  [source/evidence catalog](reports/README.md).
- [PR19](https://github.com/Hong-yiii/neuro_science/pull/19) is merged into `main`
  at `a169edf` (verified October12). PR15's studies remain in ancestry.
- Reorganization checkpoint: **`ebe8256`**, branch
  `refactor/report-first-weekly-layout`, based on that merged main. This branch is
  being published as a separate **draft**, not merged by this task.
- [Implementation status](reorganization.md): report promoted, seven weekly overviews,
  eleven byte-preserved HTML relocations, shared split access and the full-trial/
  endpoint-time/cue-time [`neuro.studies` package](../src/neuro/README.md). Older helper
  families stay behind an audited legacy adapter; other evidence migrations remain open.
- The package consolidation starts from `cc0527e` on this branch and remains unstaged
  for independent review; draft PR20 already exists. It makes no commit/publication.
- Whether/how the intended companion notebook uses this package remains open,
  depending on its scope and complexity. No notebook, fit, private replay, installation
  or service is added.

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

`pyproject.toml`/`uv.lock` describe the general environment; `requirements-replay.txt`
and retained `scratch/v6-v9-runtime/` describe a different historical runtime. Filing
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
