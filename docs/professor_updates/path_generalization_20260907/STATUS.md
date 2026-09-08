# Status and deprecation ledger

Updated for PR packaging, 2026-09-08. **Use this index, not a filename containing “final” or “ACTIVE_RUN”, to choose an authoritative object.** Nothing here promotes exploratory results to confirmation.

## Current versus historical documents

| Object | Status | Read/use instead when appropriate |
| --- | --- | --- |
| [Current HTML](path-generalization-teaching-audit-20260907.html) | Current teaching report;8 September diagram correction and practical follow-up incorporated | [Current manifest](report-manifest.json), [corrections](CORRECTIONS.md) |
| [Next-study plan](../../reports/path-generalization-next-steps-20260908.md) | Current **proposal**, not fitted work | Freeze a new protocol before execution |
| [Prefit protocol](../../reports/path-generalization-prefit-20260907.md) | Exact executed historical specification; hash unchanged | Not a live roadmap or permission for more fits |
| [V6–V9 teaching report](../../reports/place195-v6-v9-autoresearch-20260906.md) and professor HTML | Accepted earlier exploratory results; unchanged by this package | Follow-up adds diagnostics; it does not erase the earlier study |
| [Older audit/alternatives guide](../../reports/place195-audit-and-next-steps-20260907.md) | Audit procedures retained; next-step recommendation partially superseded | Current plan keeps source-safe pseudopopulations central |
| [Data-volume comparison](../../reports/cebra-data-volume-comparison-20260907.md) | Literature/denominator evidence retained; roadmap clarified | Not a universal minimum-N or data-only causal explanation |
| [August flow review](../../prospective-path-research-flow-review.md), [onboarding checklist](../../getting-started-tasks.md) | Dated history with current banners/pointers | Their old “blocked models”/“untouched test” wording is not current state |
| [Original released HTML and receipts](archive/release-20260907/) | Archived, superseded for presentation; original SHA31c745a… retained | Current HTML fixes Figure1 and includes later interpretation |
| [Earlier reviewed HTML](archive/release-before-parent-clarifications.html) | Archived; SHA8fa2d4…; predates parent clarifications | Never substitute for current report |

Archived contents are byte-preserved. Their original relative/absolute paths describe where things lived at the time. The [promoted-file map](promoted-files.json) resolves copies; archived release manifests must be read with their archived HTML, not compared blindly against the updated live filename. The original run-root `final_report_manifest.json` remains a historical7 September receipt.

## Execution ledger

Local base: `outputs/path-generalization-20260907/`; accepted run: `results-20260907T081200Z/`.

| Artifact/stage | Status and permitted interpretation | Replacement/authority |
| --- | --- | --- |
| Early Gaussian fixture smoke | **Failed preflight:** flattened block mean needed a cell×bin reshape; no biological data used | [Failure note](archive/execution/phase1_failed_smoke_broadcasting.md), subsequent synthetic checks |
| Source-budget regression test | **Failed preflight:** source metadata and subset tensor were misaligned; fixed before biological execution | [Original test log](archive/execution/preflight-source-budget-failed.log), final38-test receipt |
| Preflight schema, synthetic and target/config iterations outside the accepted run | Historical support/debugging snapshots, not extra biological replications | Frozen protocol + [execution gate](evidence/execution_gate.json) identify the executed version |
| First `track_a/` | **Failed/incomplete:** legacy V9 prediction CSV lacks a `C` column; partial outputs retained locally, never pooled | [Original failure](archive/execution/track-a-first-failed.log), [reader-fix receipt](evidence/track_a_reader_fix.json), accepted `track_a_v2/` |
| `track_a_v2/` | Accepted complete Track A | [Summary](evidence/track_a_v2/summary.json), [review](evidence/reviews/track-a-results-review.md) |
| `track_b/`342 fits | Accepted complete observed/null fits and predictions | [Audited summary](evidence/track_b/summary_exact_audited.json), [exact audit](evidence/audits/track_b_exact_audit.json) |
| Raw B `summary.json`/`track_b_family_null_pvalues.json` | **Execution receipts only; p-value superseded.** Float reduction excluded a mathematical tie; raw p0.8571429 is not authoritative | [Archived originals](archive/execution/track_b/); corrected18/20 inclusive exceedances, p19/21 |
| First cross-assembly replay | **Failed postprocess:** assumed first50 completed receipts were all factorial models | [Original failure](archive/execution/assembly-replay-first-failed.log); corrected selection by `family_role`;50 frozen checkpoints×5 assemblies, no new fits |
| `assembly_transfer/` | Accepted corrected CPU replay; own source pools only | [Summary](evidence/assembly_transfer/summary.json), [review](evidence/reviews/assembly-transfer-review.md) |
| `track_c/` and guarded export | Accepted complete three-target per-unit/control/null analysis | [Summary](evidence/track_c/summary.json), [guard receipt](evidence/track_c_export/development_cue_counts_manifest.json), [review](evidence/reviews/track-c-results-review.md) |
| Late queued failure/completion notifications | Delayed receipts for the above attempts, not new jobs after release | Evaluate attempt identity and supersession, not notification arrival time |

The B exact correction changes inference arithmetic only. No checkpoint, prediction, optimizer step or frozen driver was edited. Later live code adds a floating-tie tolerance regression; the completed B result is authoritative because it was independently recomputed using exact fractions, not because it was refit with that tolerance.

## Code versions — all retained

| File | Used for | SHA256 |
| --- | --- | --- |
| [B/C driver snapshot](archive/code/driver_bc_20260907.py.txt) | Frozen B and C execution | `2821317f843ca2b285f2db20d9587c5dd594511e42b5fd63ad304130e4417de1` |
| [A-v2 driver snapshot](archive/code/driver_track_a_v2_20260907.py.txt) | Reader-only corrected Track A rerun | `340bd4fa14ee90b0a57cbc384785dff5be5936ab08146aee1e6620c0050d7bfb` |
| [Live analysis driver](../../../scripts/place195_path_generalization_phase1.py) | Includes the later floating-tie maintenance fix | `aaaf174114de0db500fb85a153fe7d5e9c447cb4702c172863bd4f6da29cf6f4` |
| [Original report builder](archive/code/report_builder_20260907.py.txt) | Generated the original released31c745a… HTML | `593bc21f8b82cd1bee7eb63e1972cc0b4437c7e136234dfddc96a6099ce816d3` |
| [Current report builder](../../../scripts/build_path_generalization_report.py) | Packaging correction and follow-up text; no model changes | See current manifest and `SHA256SUMS` |

`.py.txt` is deliberate: archived producers are evidence, not alternate current entry points. No execution should target an accepted output directory.

## Review and planning status

- [Final packaging integrity review](evidence/reviews/pr-package-integrity-review.md)
  and [final scientific/docs review](evidence/reviews/pr-package-scientific-review.md)
  approved the currentcc941bed… HTML and its source/documentation delta. Parent
  subsequently added these receipts, updated manifest status and resealed checksums;
  the reviewed HTML and analysis source did not change.
- [Frozen execution review](evidence/reviews/frozen-execution-gate-review.md) approved the exact2821317… snapshot; later B floating-tie inference was corrected separately.
- `evidence/reviews/track-*-results-review.md`, `track-b-final-review.md` and `assembly-transfer-review.md` review completed results within their stated scopes.
- `evidence/reviews/final-html-{pedagogy,factual}-review.md` apply to the8fa2d4… report; `final-release-followup-review.md` applies to31c745a…. They remain valid historical receipts, not a claim that the new HTML was reviewed at those hashes.
- `archive/planning/code-review-{ab,c}.md` and `code-review-{ab,c}-final.md` are **superseded blocking implementation reviews**. “Final” in their filenames does not mean current unresolved blockers. The execution-gate review records their resolution before fitting.
- `archive/planning/protocol-preflight-review.md`, `implementation-phase1.md`, `design-review.md`, `artifact-feasibility.md`, and `primary-literature.md` are design/research history, not current results.
- `archive/planning/report-draft-handoff.md` contains a stale generator hash. It is retained verbatim, not patched to pretend it described the later source.
- `archive/planning/ACTIVE_RUN.json`, `FINAL_STATE.md`, and `manager_history.md` are dated snapshots. The current PR supersedes their “no commits”/running-state language. Manager history also contains earlier closed gates superseded by later entries.

All reviews are AI-assisted quality assurance, not human peer review, laboratory verification, or independent biological replication.

## Retention boundaries

`LOCAL_SHA256SUMS` inventories the complete present local study-output tree at packaging, including failed and preflight outputs. [Local inventory summary](local-artifact-inventory.json) records counts and scope. Files are not deleted, pooled or moved out of their original run locations. Raw inputs, runtime, original V6–V9 dependencies and unrelated worktrees are outside this new-output inventory.

**Combined-release scope:** this directory documents the path-study subpackage. The umbrella PR also includes endpoint work and the recent-learnings synthesis; see the [global handoff](../../reports/README.md). The original main-worktree baseline formatting patch remains there and is AST-identical to tracked code. Current implementation files and exact executed snapshots are included; transient edits never snapshotted during development cannot be reconstructed merely from a checksum catalog. Full data/checkpoint recovery still requires the retained host artifacts or a separately authorized backup.
