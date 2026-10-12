# Early work and retired planning — filed away

Filed 2026-10-12 at Hongyi's request: focus the main navigation on the current
retrospective and the evidence actually used by it. **Archive, not deletion.**
Return to the [report/evidence index](../../README.md).

## Physically archived, byte for byte

These four documents are not scientific sources directly cited by the current
manuscript. Their active-looking queues are superseded. Small pointers remain
at the old paths so existing references still reach the original text.

| Original path | Verbatim record | Why filed away |
| --- | --- | --- |
| `docs/getting-started-tasks.md` | [Onboarding and old task queues](getting-started-tasks.md.txt) | September27/28 and earlier priorities are not the current queue. |
| `docs/supervisor-meeting-prep.md` | [Supervisor scratchpad](supervisor-meeting-prep.md.txt) | Pre-pivot neural–agent/place-first plan. |
| `learning/neural-agent-action-plan.md` | [Old curriculum](neural-agent-action-plan.md.txt) | Deprecated RNN comparison and eight-week sequence. |
| `todo/graph-path-pseudopopulation.md` | [V4/V5 checklist](graph-path-pseudopopulation.md.txt) | Initial trials and old pending baseline steps, not an instruction to rerun. |

[Checksums and original paths](manifest.json) make the moves reversible. The
`.md.txt` form intentionally preserves the original Markdown **without rendering
its old relative links as if they belonged to this directory**. Interpret paths
using the original locations above. No scientific claims, hashes, or old checkbox
states were rewritten.

[The full pre-cleanup reports index](reports-index-before-cleanup.md.txt) is also
retained verbatim. Its “current/latest” labels describe its former navigation;
use the new [report index](../../README.md), not those labels, for current focus.

## Initial trials and background — filed in place

These are now a historical reading lane, not the main report workflow. Their
physical paths remain because they carry provenance or executable dependencies.

- [Initial CEBRA pilot](../../../cebra_pilot/README.md): synthetic and one-cell
  API/software smoke, not evidence of path prediction. Its source handoffs,
  formalization, reviews and recorded smoke outcomes remain together.
- [August30 first-trial notebook](../../../../notes/sessions/2026-08-30-first-trial-run-understanding.md):
  also contains completed importer/QC results, not just an abandoned proposal.
- [Early V5 professor report](../../../professor_updates/place195_v5_20260902/README.md):
  accepted historical context with original exposure limitations, not the current assay.
- [Dated session history](../../../../notes/sessions/README.md): includes hypothesis,
  acquisition and holdout-exposure decisions; not a task queue.
- `notes/data_inspection/`: retained schema, marker, support, import and graph
  receipts underlying later studies. Do not discard them as initial-trial clutter.
- Existing `docs/reports/archive/` siblings: frozen code, failed attempts,
  correction records and previous consolidation recovery remain untouched.

## Code and tests intentionally not relocated

Read-only dependency audit `ff26d0e9` found that later graph/split analyses import
pilot contracts, paths and splits; the package initializer also imports neural
helpers. The pilot test module combines those shared contracts with old smoke
checks. Moving it wholesale would remove useful coverage.

All `scripts/test_*.py` participate in discovery; some verifiers load tests
explicitly. Scripts also hash dependencies at their original paths. Even an
apparently isolated initial-trial runner can have documented CLI and replay
references. **No code or test was demonstrated safe for a bare archival move.**
Use the [script/workflow map](../../../../scripts/README.md) to distinguish the
report-backed pipeline from historical smoke and excluded modeling branches.
A future code migration needs compatibility and coverage checks, not deletion
based on age or absence of a direct manuscript link.

## Retention and recovery

- Manuscript source, frozen standalone HTML, current agenda, data contract,
  report-cited evidence and all original scientific artifacts are preserved.
- No raw data, predictions, checkpoints, environments, worktrees, submodules or
  ignored scientific outputs were read, moved or deleted by this filing pass.
- Pre-edit navigation/source copies, including pre-existing local modifications,
  are retained in `outputs/repo-cleanup-20261012/before/`. This is local recovery,
  not an off-host backup. Do not blindly restore over later edits.
- To undo a pointer replacement, compare its current content for intervening
  changes, verify the archived checksum, then restore that exact text to its
  recorded original path. The archived file remains available afterward.
- During the filing pass, nothing was staged, committed or pushed; subsequent
  owner-authorized PR preparation is recorded in the workspace handoff.
  The unrelated untracked
  `docs/reports/current-state-20260927/` was not inspected or modified.

## Verification

Independent read-only review `a2720d1e` found no findings. Five archived snapshots
match their pre-edit bytes/checksums; all four old-path pointers and 157 local
Markdown links passed. Manuscript presentation/aggregate tests passed; scripts,
pilot implementation, submodules and all four registered worktrees are unchanged.
The original and frozen reading HTML retain their exact SHA-256. Current source
packaging differs only in whitespace formatting, with identical normalized
HTML elements/attributes/text; no frozen output was replaced to hide the difference.

Receipt: `outputs/repo-cleanup-20261012/verification.json`. Successful task
`bbd23050e` and the initial formatting-equality failure `bfb4180ac` retain their
logs in this session's `.pi/tasks/` directory. Markdown LSP had inconclusive
silent-on-clean results and stale/ambiguous path warnings; filesystem/link checks
provide the positive validation. No broad scientific test suite was run.
