# Single neuroscience workspace and current handoff

**Owner: Hongyi. Inspected September 10; takeover/consolidation resumed September 13,
2026 (Asia/Singapore).** The date `20260910` in consolidation paths identifies this
session, not the date every operation completed.

## October12 — approved hierarchy, first implementation slice

Current entry points: [report](../report/README.md), [weekly history](../history/README.md)
and [migration status](reorganization.md). The manuscript package and eleven
standalone historical HTML files have physically moved with legacy symlinks;
protocols/source packages remain in place. The shared split-access implementation
moved unchanged into `src/neuro/`; current callers/provenance are updated, so old
approval identities must not be treated as valid for the changed current scripts.
Most scientific bodies still await extraction from `scripts/`. No private replay,
fit, service, worktree cleanup, commit/push or PR merge accompanies this slice.
The frozen HTML's pre-existing local byte difference is preserved and its exact
checksum check remains failing. Original working/committed copies are retained
in `work/reorganization-weekly-audit/before-build/`. The untracked current-state
package remains untouched. One companion notebook is intended, not two; its
scientific scope is still a separate decision. Earlier checkpoints below are history.

## October12 — PR preparation and next-work sequence

Hongyi authorized a PR targeting `main` for the retrospective, separate research
agenda and report-first archival work. The exact frozen reading HTML is now
included alongside its source package, with a checksum regression check, so
reading it does not depend on ignored outputs. Opening the PR does not imply
merging it or completing the pending scientific/editorial work. The unrelated
untracked `reports/current-state-20260927/` stays outside the PR.

Next: **sharpen the report, then create an interpretable high-observability
Jupyter notebook**. The [package's next-work contract](reports/cebra-retrospective-20261012/README.md#next-work-report-first-then-notebook)
records pending report revisions, the unresolved meaning of “pair,” and a proposed
aggregate-only notebook before any separately authorized scientific execution.
Preserve all private artifacts, runtimes, submodules and retained worktrees.

## October12 — report-first workflow and bounded archival cleanup

Hongyi asked to retain the report as one whole file, then file away stale plans
and initial trials so current work centers on evidence used in the manuscript.
Start with the [manuscript package](reports/cebra-retrospective-20261012/README.md)
and [report-focused evidence index](reports/README.md). The frozen standalone
reading copy has SHA-256 `86497662096908f5fa92f1d00747377b2046e07a37ea225ae8fdbedcc9dfbde6`;
the frozen and original portable HTML bytes remain unchanged, and pending
feedback is preserved. Packaging the current editable source has only a
whitespace-formatting difference, verified by normalized HTML element/attribute/text
comparison; no scientific content or frozen export was replaced.

Four obsolete planning documents are archived byte-for-byte with old-path
pointers; [archive index and manifest](reports/archive/early-work-20261012/README.md)
record scope and recovery. Initial pilot/V5/session records are a historical
reading lane, retained in place because some carry source and exposure provenance.
The [script/test map](../scripts/README.md) records why shared pilot code and tests
were not moved. No executable code/test, raw data, model, prediction, runtime,
submodule or review worktree was moved or deleted. No fits or scientific replay.
Pre-edit navigation copies, including existing local modifications, are retained
under `outputs/repo-cleanup-20261012/before/`; no commit or staging occurred
during that filing pass. The subsequent PR preparation is recorded above.
The untracked `reports/current-state-20260927/` remains untouched.
The October11 research agenda remains proposed, not an automatically queued run.

## October11 — two-document synthesis and future-direction planning

Hongyi requested an overall structure and iterative research review for two
separate documents: [completed-work synthesis](reports/cebra-research-synthesis-20261011.md)
and [CEBRA/observable reusable latent-model agenda](cebra-observability-agenda-20261011.md).
Narrow both next, then condense the agreed future direction into the retrospective.
The old prospective-path objective is no longer the default target; summarize its
conclusions without declaring H1 false. H2 stays removed. Candidate hypotheses,
state-model examples, data routes and protocols remain proposals, not approved runs.

Read-only report/aggregate audit and public-methods research informed these drafts.
No raw data/checkpoints, fits, saved-model reanalysis, new data download or service
were introduced. At task start local `main` and cached `origin/main` were `4862267`,
containing PR15's merge and both original study commits; no GitHub refresh or new
merge was performed. The pre-existing untracked `docs/reports/current-state-20260927/`
remains untouched. Preserve all retained worktrees/private artifacts. The historical
handoffs below are evidence, not automatic task queues.

## October9 — PR15 integration and observability next-session handoff

Hongyi authorized updating and **merging [PR15](https://github.com/Hong-yiii/neuro_science/pull/15)**,
then taking up the [observability/CEBRA pivot](observability-pivot-20261009.md) in a
new session. This supersedes earlier draft/do-not-merge instructions below and
in the dated reports; those are historical checkpoints, not current restrictions.
Use a merge commit to preserve `712744c`'s October5 author date and endpoint
commit `724108a`; retain the branch and all three review worktrees/artifacts.
Verify the PR's merged state and start from updated `main` in this canonical repo.

**First next-session task:** clarify the lab's meaning of observability, then
formulate one bounded question/protocol. H1-led path work is not the default next
queue; H1 is neither confirmed nor refuted and H2 remains removed. Temporal
readout transfer is a candidate, not a completed analysis. No new model fit,
locked-test access, navigation extraction, installation or server is authorized.

This integration includes the completed studies, interpretation clarifications
and indexed direction handoff. Raw data/models/approvals remain local. Preserve
unrelated `evidence.py`, atlas-test changes, and the pre-existing
`docs/reports/current-state-20260927/` plus its unstaged reports-index entry;
they are excluded, not abandoned. Local preservation/merge receipts are under
`outputs/pr15-merge-20261009/`. Offline report HTML remains the verified rendering;
later Markdown clarifications and this direction note do not change its numerical
results or claim that a new render/replay/experiment occurred.

## October7 — separate endpoint comparison completed and replay-verified

Hongyi authorized the bounded endpoint study and independent subagent approval.
[Results and18figures](reports/cebra-endpoint-time-readout-20261006/README.md)
([offline HTML](reports/cebra-endpoint-time-readout-20261006/report.html)),
[execution ledger](reports/cebra-endpoint-time-readout-20261006/execution.md), and
[run/recovery operations](reports/cebra-endpoint-time-readout-20261006/run-operations.md).
All126 encoders,63PCA fits and10,395 readouts completed in32m10s, including all20null
worlds/3seeds. Full fit-blocked native replay and independent numerical/scientific
review passed. The reviewed verifier corrected scaler/PCA/backend reconstruction
only; no fitted artifact, source split, tolerance or probability metric changed.

Wholecue mean development balanced accuracy, cue-only→joint CEBRA: pair30
63.75→75.56%, start6 71.81→72.64%, goal6 85.14→83.89%. PCA pair/start references
(83.61/89.44%) and raw goal(90.83%) are stronger accuracy comparators. Wholecue
joint-loss-gain family tail8/21 does not establish robust superiority; absolute/bin
families have low-resolution1/21 tails. Historically exposed, label-conditioned
195-unit/58-session pseudopopulations, not unknown-label natural-trial prediction,
trial-specific dynamics or path/H1 evidence. The completed path assay is separate.

Fit/replay scopes are inactive; no restart or new fitting is queued. No locked
outer-test features, path-study rerun, new worktree, installation, daemon or PR15
merge. Earlier pending/paused endpoint notes are superseded by these results.
On October8 (Singapore), Hongyi requested a PR update for this completed study:
use existing draft [PR15](https://github.com/Hong-yiii/neuro_science/pull/15),
keep the October5 path assay separate, and preserve unrelated local changes.
Only code/tests, aggregate figures/tables, provenance and documentation belong in
the update; private models/data and full predictions remain local. The October8
do-not-merge request is historical and superseded by the October9 authorization above.

## October5 follow-up — frozen cue-time readouts completed

Hongyi explicitly authorized the bounded study after discussion of single-bin
versus concatenated decoding. [Results and16 figures](reports/cebra-cue-time-readout-20261005/README.md)
([offline HTML](reports/cebra-cue-time-readout-20261005/report.html)),
[source construction/audit](reports/cebra-cue-time-readout-20261005/source-support.md),
and [review/execution ledger](reports/cebra-cue-time-readout-20261005/execution.md).
The latest decision separates **fixed1000-update performance** from descriptive
saved-checkpoint geometry; training duration is not a performance factorial.
Cue-only/joint CEBRA-Time × logistic/RBF-SVM were compared at each of ten cue
bins and whole cue, alongside matched raw/PCA references. Historical LDA remains
context, not a new baseline family in this decomposition.

Exactly5040 new single-bin readouts and504 saved whole-cue replays completed;
**zero encoder/PCA refits**. All20 saved source-null worlds and three seeds were
retained; full fit-blocked replay and independent numerical review passed. The
fixed4→3 assay has29 selected units/7session blocks,82train/22exposed-validation
sources. Joint/logistic's descriptive100–200ms peak was88.89% BA versus61.81%
whole cue; raw/logistic's200–300ms peak was94.44%. Those are **not validated best
windows**: the predeclared bin-family gain tail was9/21 and absolute80-view BA
family tail17/21. Sixteen of20null maxima matched/exceeded94.44%; do not promote
the peaks to H1 confirmation or infer absence of neural information from the null
comparison. Eight singleton-pool source deletions were inestimable.

Accepted local outputs: `outputs/cebra-cue-time-readout-20261005/run-reviewed-20261005/`,
its `-verify/` sibling, and `preparation/geometry-reviewed-20261005/` under that
study root. Geometry uses saved250/500/750/1000checkpoints descriptively; no model
selection or biological rotation claim. On October6, Hongyi requested a focused
**draft PR into main, to remain unmerged while more work is added**. Publication
uses branch `analysis/cue-time-readout-20261005`; only this study and its handoff
are included. The publication commit author date is October5 (Singapore), at
Hongyi's request; experiment timestamps remain unchanged. No new service or
worktree is introduced, and existing unrelated local changes remain preserved.
Goal/navigation/temporal-transfer, new source folds and ordered-path work remain
unexecuted. Next priority is a source-support/fold and nuisance-control
proposal, not an automatic model/tuning expansion; no further fitting is queued.

## September28 follow-up — visual evidence and temporal validation

[PR#14](https://github.com/Hong-yiii/neuro_science/pull/14) carries forward the
professor-ready review from PR13 plus49 additional empirical figure panels and
the [agreed validation plan](professor_updates/research_review_20260928/validation-plan.md).
Read the [offline review](professor_updates/research_review_20260928/review.html)
for saved source/class distributions, performance/confusions, historical cue-bin
LDA curves and within-cue goal generalization. Prioritize **source support → saved
plots → bounded prefit protocol**. Improved cue decoding remains primary; frozen
cue/navigation transfer is a separate supporting assay. New navigation-time and
joint-model temporal decoding remain unexecuted; no model-run authorization is
implied by shipping/merging this documentation. H1 retained, H2 removed.

Hongyi explicitly authorized a new PR and merge. Verify updated main before the
next session; local publication/merge receipts and preservation hashes live under
`outputs/professor-review-followup-20260928/`. Both8767/8768 previews have expired;
use the saved HTML offline. The unrelated atlas-test change, reports-index edit
and earlier untracked overview are preserved outside PR14. No worktree cleanup,
new service or experiment restart accompanies this delivery.

## Current navigation refresh — September 27, 2026

**Start next session with [agreed project direction](project-direction.md), then
[research questions](research-questions.md) and [analysis contract](analysis-contract.md).**
H1 remains; H2 is removed. Narrow to CEBRA-Time cue-only/joint training, two
checkpoints, source-safe folds and PCA/LDA baselines. Decoder choice is open;
component assay A supports the desired ordered graph-path capability B, not
replacement by endpoints. Construction documentation/checks are the next methods
artifact; phase-selectivity/rotation interpretation awaits mentor input.

[Direction follow-up PR #12](https://github.com/Hong-yiii/neuro_science/pull/12)
was authored on `planning/project-direction-20260927` from
merged main (`e8f2308`). Hongyi authorized publishing and merging this follow-up;
**after that merge, start from updated `main` in this canonical checkout**.
Do not infer a model-run authorization from the Git operation. The
[September26 retrospective](reports/research-reset-20260926/README.md)
([HTML](reports/research-reset-20260926/review.html)) remains evidence/history,
not authority to substitute its unadopted recommendations. Original recovery
history below is retained. Final publication/merge checks and preservation
receipts live under `outputs/project-direction-20260927/convergence/`.

[Consolidated PR #11](https://github.com/Hong-yiii/neuro_science/pull/11) merged
September27 at 09:09:51 UTC with its commit ancestry preserved. It includes
PRs #8/#9/#10 and the local studies/review; GitHub automatically marked #8/#9
merged. Stacked #10 was subsequently closed as already included, after verifying
its full head ancestry in main. No source branch was deleted or retargeted.
See the [integration/recovery receipt](reports/review-integration-20260926.md).
The original dirty release checkout was captured in safety commit `8baf68f` and
a verified local Git bundle before switching branches.

PR #7 merged September23 after its experiment completed September13–14.
Statements below or in Sept24 reports calling it unexecuted are superseded. Its
[matched result](reports/path-pca-matched/README.md) is now in this checkout.

There are **four registered worktrees**, not one: this root plus
`work/issue-6-pca`, `work/cebra-full-trial-transfer` (merged PR #9), and
`work/cebra-time-teach` (PR #10 closed as included via #11). Atlas PR #8 is
merged too; merge status does not authorize deleting any of these worktrees.
PR7's unique ignored model/output files remain inside its worktree. Do not remove
any worktree from merge status alone. Decoder, diagnosis and professor-review
work is now preserved in Git on main and the planning branch; ignored private artifacts
remain in their original locations. Branch integration does not authorize new
biological fits, artifact migration or worktree deletion.

## September 10–13 historical consolidation handoff

Use **`~/neuro_science`** for neuroscience work. This session
`01a08ab0-4fd4-704c-ac18-3b002e40c116` is the current durable handoff, at Hongyi's
explicit request. Earlier sessions are exploratory history, not competing task
queues. Read this document and the [research index](reports/README.md) rather than
reconstructing instructions from old transcripts. Do not spawn lasting sibling
worktrees without an explicit need and a removal/handoff plan.

**Remote status refreshed September 13:** [PR #5](https://github.com/Hong-yiii/neuro_science/pull/5)
merged into `main` at `d1228d3`. The canonical checkout's branch and uncommitted
work are preserved; base new branches on refreshed `origin/main`, not old local
`main`. No force-push, branch deletion or fitting was part of consolidation.

**Explicit temporary exception, issue #6:** Hongyi requested a separate worktree
and draft PR for the matched PCA/raw exploratory study. Its branch is
`feat/issue-6-matched-pca`, worktree `~/neuro_science/work/issue-6-pca`.
Read its [protocol and execution ledger](reports/path-pca-matched/execution.md).
Keep it through PR review; after user-approved merge, hash/migrate its local
outputs back to canonical storage before removal. This is not a competing
research queue or permission to restart historical searches. No new service.
The study completed September 14: [human verdict and reviewed evidence](reports/path-pca-matched/README.md).
PCA's matched historical loss advantage was small (+.007023), with unchanged 55%
balanced accuracy and source sensitivity spanning both signs. All 26,266 fits
were forward-replayed without fitting. [PR #7](https://github.com/Hong-yiii/neuro_science/pull/7)
was still a draft at that checkpoint; it merged September23. No more biological
fits are queued by this historical handoff.

**Explicit temporary exception, September 24–25:** Hongyi requested a PR for a
bounded exploratory CEBRA broader-training → cue-only decoding trial. Branch
`feat/cebra-full-trial-transfer` lives at
`~/neuro_science/work/cebra-full-trial-transfer`, based on refreshed `origin/main`
`8340631` (PR #7 is now merged; the older open/draft statement above is historical).
The [frozen protocol](reports/cebra-full-trial-transfer/protocol.md) defines the
fixed 29-unit/7-session, 4→3 comparison. Private inputs/runtime remain canonical;
new artifacts go directly to
`~/neuro_science/outputs/cebra-full-trial-transfer-20260924/`. Preserve this worktree
through PR review. After approved merge, verify canonical artifact hashes and
worktree cleanliness before deliberately removing only this worktree. Do not
remove the independent issue #6 worktree as part of this task. No new service.

**Completed September 25:** [Results and report](reports/cebra-full-trial-transfer/README.md),
[execution/review ledger](reports/cebra-full-trial-transfer/execution.md),
[PR #9](https://github.com/Hong-yiii/neuro_science/pull/9). Broader-training
CEBRA-Time improved cue-only logistic loss 1.010464→0.710618 and mean balanced
accuracy 32.64%→61.81%; Behavior loss worsened. The primary criterion failed
because loss remained worse than constant-.5, and absolute discrimination varied
strongly by seed. All 1,071 fitted artifacts were forward-replayed without fitting;
independent numerical review passed. Accepted run:
`outputs/cebra-full-trial-transfer-20260924/biological-run-20260924T162913Z/`.
Known-label-conditioned historical source pools, not simultaneous natural trials
or confirmed H1. No further fitting, merge or worktree removal is queued.

**Explicit teaching-PR exception, September 25:** user requested `/teach max`
on the CEBRA-Time transfer result and a PR. The standalone
[lesson](../learning/cebra-time-transfer-teach-max-20260925.html) lives on
`docs/cebra-time-transfer-teach-max` in `~/neuro_science/work/cebra-time-teach`,
branched from experiment PR #9 at `c19d07c`. [Teaching PR #10](https://github.com/Hong-yiii/neuro_science/pull/10)
was originally open and stacked on `feat/cebra-full-trial-transfer`, not `main`,
to avoid duplicating the experiment before #9 merged. **Superseded September27:**
its commits entered main through #11, and #10 was closed as already included.
The teaching work described here was documentation QA only: no new model
fitting, raw extraction, scientific-code change, tuning or merging. Preserve both
worktrees and canonical dirty work. Retain this teaching worktree until review;
remove only after approval and cleanliness/artifact checks. QA lives directly in
canonical `outputs/cebra-time-teach-20260925/`, so removal cannot strand it.
The explicitly bounded preview on loopback8766 uses Pi task `be7695c35` and expires
2026-09-25 23:54 SGT; the lesson footer, learning index and host registry document
health/stop/expiry. No boot service or new public ingress was introduced.

Pi/Codex transcripts were not concatenated, rewritten or deleted. This session
started from the account home; its transcript remains in the host-local Pi session
store. The previous canonical Pi process was not killed. Do not continue writing
from its superseded exploratory conversation. For a future session, enter this
repository first and use these Git-backed notes as context.

## What the exploratory sessions taught

- **V6–V9:** cue bins/PCA/CEBRA and a fixed interior path component did not show
  robust whole-cue improvement. The original holdout was exposed; no resplit or
  cleanup restores pristine-test status.
- **Endpoint follow-up:** sampler, readout and regularization choices improved
  condition separability. Decoding start/goal conditions is not path information
  beyond start/goal and does not establish H1.
- **Path generalization:** mixing training sources is easier than generalizing
  to independent source pools. Exact Track B family p is **19/21**. Track C is
  completed, not an untried future fix.
- **Latest preprocessing study:** 20 observed recipes; 147 training + 41 historical
  validation sources, 49 unit IDs, 13 sessions. Coarse raw rates, variance-floor
  scaling and stronger L2 helped probability loss, but only 2/5 endpoint deltas
  were positive and 6→1 dominated. No broad robustness, H1 absence, H1b or H2 claim.

Read the [September 9 review](reports/path-preprocessing-review-20260909.md) for
what worked and the [agent brief](reports/path-preprocessing-autoresearch-20260908-agent.md)
for exact evidence. Historical next steps remain **decisions, not permission to
restart old studies**: verify metadata/nuisance controls, define a worthwhile
effect, and freeze any 6→1 follow-up before genuinely new sources. Preserve the
selected-195 scope.

**New request, September 13:** Hongyi requested a PRD and new-session handoff for
a matched PCA/non-PCA path-component experiment, ending in results, independent
reviews, documentation, and a PR. The [new exploratory PRD](reports/path-pca-matched-prd-20260913.md)
defined a bounded six-recipe comparison and prefit gates. **Status corrected
September 26:** it ran September 13–14 and merged as PR #7 on September 23; see
the current navigation above. The original PRD is preserved as planning history,
not a pending queue or permission to rerun.

## September24 hyperparameter diagnosis — completed

Professor-facing synthesis: [meeting document](professor_updates/cebra_review_20260924/review.md)
and [portable HTML](professor_updates/cebra_review_20260924/review.html).
This reconciles endpoint/PCA performance with the new path diagnosis; it adds no
fits. Delivery PDF/checks are in `outputs/cebra-review-delivery-20260924/`.
The first-principles `/teach max` lesson was updated in place at
`/tmp/pi-teach/20260924T095420Z-cebra-first-principles.html`; its temporary preview
is not durable scientific authority. Use the report if that preview expires.

[Human diagnosis](reports/cebra-hyperparameter-diagnosis-20260924.md) and
[offline illustrated HTML](reports/cebra-hyperparameter-diagnosis-20260924.html)
report the separately authorized six-C/nine-SVM-setting ablation on the same
frozen29-unit/4→3 representations.1700new readouts and20null-only PCA transforms,
zero CEBRA or observed-PCA refits;2500model records/395000predictions verified;
117software tests passed. Weakening decoder regularization did not rescue CEBRA.
Confidence changes explain large loss improvements without better discrimination;
source-transfer failure is observed, but its unique cause and CEBRA's intrinsic
task suitability remain unresolved. PCA's77.5% mean remains descriptive; new
anchored raw/PCA null checks do not establish it and do not directly test that mean.

Accepted run:
`outputs/cebra-hyperparameter-diagnosis-20260924/run-20260924T105957Z/`.
Protocol, full curves/grids, source/null caveats and code/review provenance are in
the report. This is complete, not a pending encoder-tuning task. The separate
September13 five-panel PCA/non-PCA study is also complete (PR #7; corrected in the
September26 navigation above). No new service,
raw/test/lab access, installs, branch change or commit/push occurred.

## September 24 frozen-CEBRA decoder follow-up — completed

[Human results](reports/cebra-decoder-autoresearch-20260924.md) and
[offline HTML](reports/cebra-decoder-autoresearch-20260924.html) report the separately
authorized eight-readout experiment on retained29-unit/7-session4→3 embeddings.
No nonlinear CEBRA criterion passed (best mean BA37.33% Time/35.67% Behavior).
Matched PCA+scaled RBF reached77.50% BA, an exploratory control lead requiring its
own matched null/nuisance checks and new-source evaluation, not a confirmed H1 result.
The separate September13 PCA/non-PCA study is also complete; see the September26
status correction above.

Accepted artifacts:
`outputs/cebra-decoder-autoresearch-20260924/recovery-20260924T042259Z/`.
Exactly710 new readouts and90 saved-baseline forwards were completed; zero new
biological CEBRA fits. Five planned PCA transforms plus three disclosed preflight
PCA fits make eight cumulatively. Postprocessing initially failed because
class-local product-row IDs were merged; the fresh recovery repaired only lineage
and replayed800 saved models with all fit APIs blocked. Original fit arrays/models
were unchanged. Verification, independent numerical review and111 software tests
passed. Preserve the failed attempt and journal as provenance; do not pool it as
another result or restart fitting from its stale running flag. No new daemon,
branch change, commit/push, lab access or raw/test import was introduced.

## September 13 relocation map — historical

All paths below are relative to `~/neuro_science`.

| Former worktree | Retained authority / disposition |
| --- | --- |
| `neuro_science` | Main data, runtime, papers and existing `outputs/` stay in place. PR #5 supplies the later reviewed code/docs; original dirty state is recoverable below. |
| `neuro_science-start-goal-cebra` | Code/reports already covered by PR #5. All local outputs moved to `outputs/start-goal-{cebra,autoresearch,diagnosis}-20260907/` and `outputs/start-goal-validation/`. |
| `neuro_science-path-diagnosis` | Commit `9e04574` is included in PR #5. All outputs moved to `outputs/path-generalization-20260907/`. |
| `neuro_science-path-autoresearch-20260908` | Previously uncommitted completed study added to PR #5. All outputs moved to `outputs/path-preprocessing-autoresearch-20260908/`. |
| `neuro_science-release-20260908` | PR branch now checked out here; its original formatting-only edits retained as patches, not substituted for reviewed scientific bytes. |

Non-output local files from siblings—including original `work/`, `.pi/` task
logs, `.pi-subagents/` review/session artifacts and caches—are preserved under
`work/retired-worktrees/<former-worktree>/`. This is an archive of local material,
**not another Git worktree**. Nothing there authorizes a new run. No environment,
model, PDF, raw data, failed-attempt record or session history was discarded.

The accepted September8 preprocessing run is
`outputs/path-preprocessing-autoresearch-20260908/biological-20260908T115508Z/final-20260908T133200Z/`.
The interrupted `final-20260908T125617Z/` is retained separately and excluded from
accepted inference. The manager remains `outputs/path-autoresearch-management-20260908/`.

Absolute old paths embedded in historical reports/manifests are **provenance**,
not live dependencies. Substitute the table above when locating them. Accepted
artifacts and old receipts were moved byte-for-byte, not edited to pretend their
execution happened here. The active preprocessing runner resolves the manager
from its repository, resolves the frozen Round1 summary beside Round2 and verifies
its original hash, validates relocated final-CLI inputs by their unique frozen role and original
hash, and gets original CV source snapshots from Git. Its scientific fitter is
unchanged; the original exact driver is archived.

## Git recovery versus private data recovery

Git preserves code, reports, portable HTML, protocols, original source snapshots,
patches, lightweight receipts, package hashes and this handoff. See
[original dirty-state archive](reports/archive/workspace-20260910/README.md) and
[preprocessing execution archive](reports/archive/path-preprocessing-20260908/README.md).

**Git alone cannot restore private lab inputs or the exact historical model/output
files.** They remain deliberately ignored. To reproduce analyses or verify saved
results elsewhere, restore the authorized private data/artifact copy too; do not
rerun biological fitting just to regenerate files. Keeping them on this disk is
not an off-host backup or a restore rehearsal.

Local recovery:

- `work/workspace-consolidation-20260910/before-consolidation.bundle`: verified
  pre-cleanup Git history, refs and canonical stash; no ignored data inside.
- `work/workspace-consolidation-20260910/originals/`: exact original dirty/untracked
  source/doc copies; `originals.json` records their hashes and original commits.
- `outputs/workspace-consolidation-20260910/local-files.json`: original→current
  path map, hashes/symlink identities for **17,668 files / 2,040,409,009 bytes**.
- `outputs/workspace-consolidation-20260910/MIGRATED_SHA256SUMS`: repeatable local
  migration check. Run from repository root:
  `sha256sum --quiet -c outputs/workspace-consolidation-20260910/MIGRATED_SHA256SUMS`.
- `work/workspace-consolidation-20260910/migrate.py verify` additionally checks
  symlink identities and 2,697 original directory permission modes. The migration scripts are retained as one-off audit tools;
  do not repeat the move operation.

The inaccessible Mac worktree at
`/Users/hongyilin/.codex/worktrees/c797/neuro_science` has no inspected filesystem
contents on this host. Its stale registration was pruned only after verifying its
index matched retained commit `4946c1b` and copying its metadata to
`work/workspace-consolidation-20260910/stale-mac-registration/`. No Mac directory
was deleted or claimed backed up. There was one registered local worktree at that
consolidation checkpoint; the September26 inventory above supersedes that count.

## Recreate the historical software checkout

The clone below restores the historical release branch. For the consolidated
software and accepted direction follow-up, substitute `--branch main` after
verifying the direction PR is merged. Historical branches are recovery points,
not competing instructions. Every checkout needs private inputs/artifacts separately;
cloning Git does not restore those.

```sh
git clone --branch release/research-consolidation-20260908 \
  https://github.com/Hong-yiii/neuro_science.git neuro_science
cd neuro_science
git submodule update --init --recursive
# Private data/outputs are a separate authorized restore, never downloaded by this step.
```

`pyproject.toml` / `uv.lock` describe the general workspace environment. The
historical research runtime differs from that lock: Python 3.13.2, NumPy 2.3.4,
SciPy 1.16.3, scikit-learn 1.7.2, Torch 2.12.0, CEBRA 0.6.1, matplotlib 3.10.7,
h5py 3.16.0 and markdown-it-py 2.2.0. Use the recorded
[`requirements-replay.txt`](../requirements-replay.txt) in an isolated environment
for the replay/software checks. It records the installed dependency closure, not
a promise of cross-platform bitwise GPU determinism. The original runtime is
retained at `scratch/v6-v9-runtime/`; do not delete it based on this recipe.

```sh
uv venv --python 3.13.2 work/replay-env
uv pip install --python work/replay-env/bin/python -r requirements-replay.txt
export PYTHONDONTWRITEBYTECODE=1 PYTHONNOUSERSITE=1
export OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2
work/replay-env/bin/python scripts/check_research_software.py
```

The software suite uses invented data and tiny CPU fits, not biological fits.
It excludes two named private-input tests; the V6–V9 saved-artifact check separately
covers its saved-manifest test. Installing a brand-new runtime is a separate step
from checking a fresh Git checkout with the retained known-working interpreter.

## Saved-artifact verification after relocation

Run from the repository root, with the thread/environment settings above. Do not
use Python `-O`; assertions enforce scientific consistency. These commands do not
fit biological models or load model checkpoints.

```sh
PY=scratch/v6-v9-runtime/bin/python
"$PY" scripts/verify_place195_v6_v9_artifacts.py
"$PY" scripts/verify_path_generalization_results.py \
  outputs/path-generalization-20260907/results-20260907T081200Z
"$PY" scripts/verify_endpoint_saved_artifacts.py \
  outputs/start-goal-cebra-20260907 outputs/start-goal-autoresearch-20260907
python3 scripts/verify_path_generalization_package.py
```

The longer preprocessing verifier replays 82,283 fitted instances (roughly 12
minutes), with fitting explicitly forbidden. It **writes a new verification
receipt**, not accepted scientific artifacts. Choose a fresh receipt path:

```sh
RUN=outputs/path-preprocessing-autoresearch-20260908/biological-20260908T115508Z
RECEIPT=outputs/workspace-consolidation-20260910/preprocessing-replay-new.json
test ! -e "$RECEIPT" && "$PY" scripts/verify_path_preprocessing_results.py \
  --run-dir "$RUN" --final-dir "$RUN/final-20260908T133200Z" --output "$RECEIPT"
```

Verification results, removal status and remaining limitations are recorded in
[the consolidation ledger](reports/workspace-consolidation-20260910/README.md).
No new daemon, scheduled job, network service or external artifact upload was
created. Only the Git-backed research package goes to the existing PR.
