# Repository spring cleaning: proposed organization and separate publishing flow

Date: 2026-10-12. **Original proposal; bounded filing subsequently authorized.**

**Execution update:** Hongyi subsequently asked to file away stale material,
including initial trials, and center work on evidence used in the report. The
root/report indexes now follow that focus; four obsolete planning files were
archived verbatim with old-path pointers. Initial-trial records are cataloged
as historical in place; dependency-coupled code/tests and private artifacts were
not moved. See the [archive manifest and scope](reports/archive/early-work-20261012/README.md)
and [script/test map](../scripts/README.md). Pre-edit local changes were preserved
under `outputs/repo-cleanup-20261012/before/`. The proposal below records the
original assessment, not a claim that all its suggestions are now implemented.
No blanket deletion, executable migration or worktree retirement is authorized.

Hongyi requested that the current retrospective be kept as one complete file,
then asked for parallel recommendations for reorganizing the repository.
Three fresh-context, read-only audits covered navigation, technical workflows,
and research-evidence retention (run `7231d49f-006b-4ba3-a1ae-ac58a215051d`).
The parent checked representative findings and synthesized the proposal below.
No scientific fitting, private-data inspection, replay, download, repository
move, deletion, staging, commit, submodule change or worktree retirement occurred.

## Recommendation

**Clean the entry points first; preserve the evidence paths.** The main problem
is competing “current” instructions and mixed document roles, not the mere number
of files. A wholesale move into `src/`, `experiments/` and `archive/` would break
real dependencies before improving the research workflow.

Separate three activities:

1. **Read/publish:** the retrospective and its single-file reading release.
2. **Plan:** the proposed reusable-latent-model agenda and explicit approval gates.
3. **Audit/reproduce:** original studies, executed code, protocols and recovery records.

Teaching and dated notes support these activities; they do not define a competing
run queue. H1 remains unresolved; H2 stays removed. Cleaning does not authorize
new experiments or turn historical development results into confirmation.

## Already preserved: one complete offline report

[Download/read the frozen retrospective](reports/cebra-retrospective-20261012/retrospective-frozen-20261012.html).
The subsequent authorized PR includes this exact-byte copy in the manuscript
package; the original local export and receipt below remain protected.

- Exact file: `outputs/cebra-retrospective-20261012/retrospective-frozen-20261012.html`.
- SHA-256: `86497662096908f5fa92f1d00747377b2046e07a37ea225ae8fdbedcc9dfbde6`.
- 2,670,108 bytes; all 14 PNGs and five SVGs embedded; no scripts or server.
- Byte-identical to the last desktop/mobile-checked reading copy. Adjacent
  `.receipt.json` records the original build and browser receipt.
- Editable source, builder, tests and feedback stay together in
  [the manuscript package](reports/cebra-retrospective-20261012/README.md).
- Preserve this frozen filename; the existing builder writes the separate
  `manuscript.html` output and must not overwrite this milestone.

“Frozen” means an editorial reading milestone, **not publication readiness**.
The existing shuffle/loss/training-section feedback remains recorded, not silently
completed. The original export is local/ignored; the versioned copy preserves
this reading milestone through Git, not the private scientific artifacts.
Optional evidence links still require access to the private repository.

## What the audits found

At inspection: 470 tracked entries, including 362 under `docs/` and 62 under
`scripts/`; seven modified tracked documents and four untracked paths reported
by Git. Four worktrees are registered: canonical main plus three review worktrees.
These counts exclude ignored scientific/runtime contents and submodule internals.

| Observation | Proposed repair, not yet applied |
| --- | --- |
| `docs/reports/README.md` still advertises revision 02 and `outline.html` | Link the current manuscript package/frozen release first; label older reading copies as historical. |
| Root `README.md` starts with the blueprint/agenda rather than the report | Give readers three clear entrances: retrospective, proposed next research, workspace/recovery. |
| `docs/getting-started-tasks.md` says September27/28 is active and “no central-question pivot” | Label that checklist historical and point to the October11 agenda; do not mark unperformed tasks completed. |
| `todo/README.md` advertises prospective-path work as active | Retain the old checklist as history; do not treat unchecked fits as permission to resume. |
| `AGENTS.md`, `docs/workspace.md` and several indexes duplicate changing priorities | Keep short authority links and dated status; avoid several independently edited roadmaps. |
| `learning/README.md` and `papers/README.md` retain older path-first navigation | Distinguish current learning/reading priorities from valid historical material. |
| Manuscript package, blueprint and agenda are untracked | Preserve/review their exact contents before a separately approved checkpoint; untracked is not disposable. |
| Some scientific scripts import code under `docs/cebra_pilot/implementation/` | Do not assume everything under `docs/` can be moved as prose. |
| Paths, bare imports and test discovery depend on today's layout | Catalog workflows before moving code. |

The retention auditor's concern that the report README called all presentation
artifacts disposable has been addressed **only for the requested freeze**: its
README now protects the frozen export and requires a separate retention decision
for other presentation artifacts. Other navigation findings remain proposed work.

## Proposed layout: mostly the existing directories

```text
README.md                         short front door, not the full research history
AGENTS.md                         operating/scientific safeguards + authority links

docs/
  workspace.md                    current recovery map; dated history kept distinct
  analysis-contract.md            scientific/data safeguards
  cebra-observability-agenda-...   proposed next direction, not an approved protocol
  reports/
    README.md                     catalog by role/status, not only chronology
    cebra-retrospective-20261012/ manuscript source + builder + tests + feedback
    <existing study packages>/    accepted results/protocols/aggregates in place
    archive/                      existing frozen provenance in place
  professor_updates/              historical audience-specific deliveries in place
  cebra_pilot/implementation/     executable dependencies: preserve paths

scripts/
  README.md                       proposed NEW map of runners/builders/checks
  <existing code and tests>       unchanged initially

context/                          durable context and code/data orientation
learning/                         explanations, not active protocols
papers/                           literature notes and reading priorities
notes/                            dated sessions and data-inspection findings
todo/                             clearly labeled historical/current checklists

Hippocampus.jl/, PyHipp/           submodules: unchanged
outputs/                          ignored evidence AND publication artifacts;
                                  retain by purpose, never blanket-clean
 data/, scratch/, work/           protected local data, runtimes and worktrees
```

No new top-level hierarchy or packaging framework is required. The proposed
`scripts/README.md` is the only new operational index needed initially; reuse
existing report/learning/paper indexes rather than inventing parallel catalogs.

### The reports catalog should answer five questions

- **What do I read now?** Current retrospective package and frozen reading release.
- **What might we do next?** Proposed agenda and unresolved decisions.
- **What actually ran?** Completed study packages, each with its own cohort/target.
- **What helps me learn?** Lessons and professor-facing explanations.
- **What is retained history?** Frozen protocols, corrections, failed attempts and archives.

Use the existing status vocabulary in [the reports index](reports/README.md).
Archive logically first: change the catalog/status banner, not evidence bytes or
paths. Never rewrite hash-bound historical protocols just to modernize their status.

## Separate publishing workflow

```text
Edit the one manuscript source
          ↓
Presentation-only tests + existing builder
          ↓
Offline rendering / source-claim checks
          ↓
One standalone HTML + hash/receipt
          ↓
Deliberate local download; retain the reading milestone
```

The existing commands are sufficient; no new command dispatcher is proposed:

```sh
/usr/bin/python3 docs/reports/cebra-retrospective-20261012/test_build.py
/usr/bin/python3 docs/reports/cebra-retrospective-20261012/test_path_summary.py
/usr/bin/python3 docs/reports/cebra-retrospective-20261012/build.py manuscript.html
```

Always pass `manuscript.html`: the no-argument build still selects frozen
revision 02's `outline.html`. Changing that default could be a later small fix,
with its tests, but is not part of this proposal's execution.

Publishing may reuse existing figures and perform presentation arithmetic on
tracked aggregates. It must not launch scientific fits, model replay, raw-data
extraction or missing-analysis generation. A standalone HTML is the reading
artifact; source/build/tests and provenance remain necessary for maintenance.
A later release receipt should record exact source/builder hashes and dirty state,
not imply the manuscript itself came from evidence revision `4862267`.

## Why not physically move everything now?

- `build.py` in the manuscript package uses `HERE.parents[2]`, relative source
  paths and evidence links pinned to `4862267`. Its pinned-path check proves
  existence, not equality of current source bytes with historical evidence bytes.
- `scripts/cebra_full_trial_transfer.py` fixes the canonical root and retained
  runtime path; `cebra_cue_time_readout.py` imports it and atlas/history helpers.
- `scripts/data.py` uses a sibling import; `check_research_software.py` discovers
  `scripts/test_*.py` with named exclusions. Moving tests changes what runs.
- General `pyproject.toml`/`uv.lock`, historical `requirements-replay.txt`, and
  `scratch/v6-v9-runtime/` are different environment contracts, not duplicates
  to consolidate casually.
- The three retained review worktrees include documented unique ignored artifacts.
  Merged Git branches do not imply those artifacts are backed up or expendable.

## Phased implementation, subject to approval

### 0. Protect before reorganizing

**Done:** freeze the current whole-file reading export and document retention.

**Before migration:** review/preserve existing modifications and untracked source;
choose a separately authorized Git checkpoint or protected source snapshot.
Confirm the exact worktree inventory and artifact ownership. Off-host scientific
backups/restore coverage remain unresolved; do not claim this local freeze fixes them.

### 1. Navigation and stale authority — recommended next task

Edit only root `README.md`, `AGENTS.md`, `docs/workspace.md`,
`docs/reports/README.md`, the onboarding/todo status headers and learning/paper
indexes. Add `scripts/README.md` with categories and links to owning protocols:
utilities, cross-study dependencies, study runners, replayers/verifiers,
presentation builders and tests. Label which commands are data-free and which
require authorization; do not infer safety from a filename containing `test`.

Acceptance: correct report reachable from the root; one current planning
entry point; no legacy queue advertised as authorization; historical conclusions
and corrections preserved; no code/data/worktree moves. Validate changed links
and the existing presentation checks only—not a blanket scientific test run.

### 2. Optional bounded physical regrouping

Only after phase 1: propose an exact old→new path list for genuinely useful moves.
Audit imports, relative links, root calculations, pinned references and runtime
ownership. For private artifacts, verify a copy/manifest before considering source
removal; retain original paths in historical receipts and add a relocation map.
For tracked files, use a dedicated reviewed change with an explicit rollback.
There is currently **no approved move list**.

### 3. Separate storage cleanup

This needs a path-specific inventory and approval, not a wildcard command.
Ordinary test/lint caches and redundant rendering intermediates may be candidates
only after checking ownership, active jobs and retained provenance. Do not delete
anything merely because it is large, old, ignored, or under `scratch`/`work`.
No disk-usage survey or reclaimable-space estimate was performed in this audit.

Always preserve accepted inputs/lineage, executed code/configs, models/predictions,
failed-attempt history, verification receipts, feedback images, frozen reading
releases, environments, submodules, `.pi`/session history and all review worktrees
unless a later explicit plan accounts for recovery.

## Coverage and decision

The three auditors inspected source/documentation and Git metadata only. They
did not validate private artifacts, evaluate scientific models, inspect broad
ignored trees or verify off-host backups. Parent verification covered the frozen
HTML's exact hash, byte equality and self-contained assets; prior browser checks
apply to those identical bytes. No Mac delivery was performed.

**Suggested approval scope: phase 1 only.** It resolves the concrete wrong-version
and stale-task problems while preserving recovery. Physical migration and deletion
remain separate decisions, not implied by approving clearer navigation.
