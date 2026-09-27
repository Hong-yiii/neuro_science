# Research reset: independent review and delivery checks

Date: 2026-09-26. Review/synthesis only; no new biological fits, raw-data extraction, model loading, branch changes, commits, pushes or PR mutations.

## Two fan-outs and parent convergence

1. **Evidence round** `e63456e8-fbfd-403d-91dc-82b5f9b74d6e`: three fresh-context researchers, one per recent session, plus a read-only codebase scout.
2. **Challenge round** `21435888-0dea-4e18-9f02-72e5404b3018`: independent scientific reviewer, cleanup planner and research-priority challenger. All read-only.
3. **Parent**: sole writer; checked branch-specific PCA and transfer reports, live GitHub metadata and preservation state; synthesized the report and applied review findings.

Seven briefs are retained under `work/research-reset-20260926/`:
`session-transfer.md`, `session-atlas.md`, `session-decoders.md`, `codebase-audit.md`, `science-review.md`, `cleanup-review.md`, `strategy-challenge.md`.
Their original harness outputs remain under `.pi-subagents/artifacts/outputs/<run-id>/work/research-reset-20260926/`. Private session transcripts were not copied into tracked docs. Exact source→copy references are in `outputs/research-reset-20260926/review-artifacts.json`.

## Findings and disposition

| Finding | Disposition |
| --- | --- |
| First-round decoder brief repeated “PCA experiment unexecuted.” | **Rejected as stale.** PR7 execution ledger records completion Sept13–14; live GitHub records merge Sept23. Current navigation corrected; historical scientific reports remain intact and explicitly superseded for status. |
| Scientific reviewer could not substantiate “live GitHub” from its inspected sources. | **Evidence supplied, claim retained.** Parent queried `gh pr list` at 09:24:17 UTC. Receipt: `outputs/research-reset-20260926/publication-state.json`. This was not independently queried by the reviewer. |
| Review-checks, renderer and HTML were missing during early review. | **Resolved.** Files added; renderer and actual browser checks passed as recorded below. Reviewers inspected a draft while parent prepared presentation files. |
| 27-file backup is not enough to delete worktrees or ignored artifacts. | **Accepted.** Report explicitly limits its coverage and adds targeted manifest gates for PR7, Sept24 and PR9 outputs before any future move/delete. |
| Unclassified `work/cebra-hyperparameter-20260924/` and other work dirs. | **Accepted.** Retained untouched; no disposable classification. |
| Avoid speculative package rewrite or directory migration. | **Accepted.** Today changes navigation/review only; active research scripts, frozen evidence and worktrees stay in place. |
| No-fit milestone must produce a decision, not another caution memo. | **Accepted.** Added support table, exposure ledger, lab questions and go/no-go output with explicit stop conditions. Missing new sources preclude confirmation, not all exploratory progress. |
| Scientific claims/null comparability. | **Supported by independent reviewer.** Relative versus absolute transfer, failed criterion, different PCA benchmarks, selected scope and pseudopopulation limits remain explicit. No core scientific blocker reported. |

## Live PR receipt summary

Parent read-only inspection: **2026-09-26T09:24:17.571217+00:00**. This is a dated snapshot, not a promise about future status.

| PR | State | Base | Head | Merge time |
| --- | --- | --- | --- | --- |
| 7 | MERGED | main | `018d5f6` | `2026-09-23T11:28:46Z` |
| 8 | OPEN | main | `a401eb3` | none |
| 9 | OPEN | main | `c19d07c` | none |
| 10 | OPEN | feat/cebra-full-trial-transfer | `ea6a8fe` | none |

Canonical checkout remains `438856e`; cached `origin/main` remains `8340631`. No `git fetch`, merge, checkout or worktree mutation was needed for this review. Live PR7 status and cached main revision are distinct observations.

## Preservation

Before navigation changes, copied and SHA256-verified **27 files / 3,332,830 bytes**: all pre-existing dirty/untracked code/docs plus clean `README.md` and `AGENTS.md`. Manifest: `outputs/research-reset-20260926/before.json`. Exact originals: `work/research-reset-20260926/before/`.

No private outputs, raw inputs, environments, historical failed attempts or registered worktrees were moved/deleted. This is local source/doc protection only, not an all-data or off-host backup. Later cleanup must preserve the specific affected ignored artifacts and retain originals until verified.

## Delivery validation

- Renderer `--check`: passed byte-for-byte HTML freshness, seven review sections, section anchors, local reference existence and no active/external resource tags. Three negative controls reject an external script, missing local reference and unexpected section. An initial extra-section check raised `ValueError` before the intended assertion; moved the section-count assertion before strict zip, then all controls passed. Temporary check files were removed.
- Python primary LSP: confirmed clean. `git diff --check`: passed. Lens reports no blocking errors; remaining pre-existing Marksman ambiguity warnings on V6–V9 links are unrelated to this review (relative target files exist), and `BA` is the scientific abbreviation for balanced accuracy, not a spelling error.
- Preservation: all 27 backup hashes still match; 23 originals are byte-identical, only the four planned navigation files changed. HEAD and four-worktree registration are unchanged; zero staged files. Receipt: `outputs/research-reset-20260926/preservation-check.json`.
- cmux: fresh **workspace:18**, “Neuroscience · research reset”, **surface:70**. Browser DOM confirms title, seven sections, failed-criterion caveat, no broken section anchors and **zero scripts / zero resource requests** in the final `about:blank` document. Desktop document/viewport widths both 1566px; screenshot visually inspected. Receipts: `outputs/research-reset-20260926/{browser-check.json,review-desktop.png}`.
- Preview transport correction: cmux's URL entry treated the initial generic data-URL placeholder and `about:blank` strings as search input. That path was abandoned. Final delivery uses JavaScript navigation to a verified blank document followed by bounded local HTML injection; no HTTP server or persistent worker. The full report's direct data-URL attempt failed. Reloading clears the disposable in-memory view; the durable HTML remains.
- Existing research software/model suites were not rerun for this documentation-only slice. No scientific scripts or model artifacts were changed.

## Residual limits

- Historical replay/test counts are read from existing evidence; not re-executed here.
- Neither review round verified laboratory metadata, every underlying prediction, or all 17,668 historically migrated files.
- Plans in the report are proposals; scientific direction, new fits, PR decisions and destructive cleanup remain unapproved.
- This adds a browser-only cmux workspace and an in-memory HTML review, not a daemon, server, listener, Git worktree or new public endpoint.
