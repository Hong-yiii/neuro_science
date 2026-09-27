# Single neuroscience workspace and current handoff

**Owner: Hongyi. Inspected September 10; takeover/consolidation resumed September 13,
2026 (Asia/Singapore).** The date `20260910` in consolidation paths identifies this
session, not the date every operation completed.

## Current navigation refresh — September 27, 2026

Start with the [research reset and decision trajectory](reports/research-reset-20260926/README.md)
([offline HTML](reports/research-reset-20260926/review.html)). This is the current
cross-session review/cleanup map; proposals there are not authorization to fit.
The original consolidation/recovery history below is retained, not rewritten.

**Current working branch:** `planning/project-direction-20260927`, created and
checked out here at Hongyi's request from merged `main` (`e8f2308`). This new
branch is local-only, without an upstream or PR yet. Its purpose is to make
high-level decisions to steer the project; no research direction, new experiment
or cleanup beyond branch setup has been chosen.

[Consolidated PR #11](https://github.com/Hong-yiii/neuro_science/pull/11) merged
September27 at 09:09:51 UTC with its commit ancestry preserved. It includes
PRs #8/#9/#10 and the local studies/review; GitHub automatically marked #8/#9
merged. Stacked #10 remains open against its original base although its head
is included in main. No source branch was deleted or manually retargeted.
See the [integration/recovery receipt](reports/review-integration-20260926.md).
The original dirty release checkout was captured in safety commit `8baf68f` and
a verified local Git bundle before switching branches.

PR #7 merged September23 after its experiment completed September13–14.
Statements below or in Sept24 reports calling it unexecuted are superseded. Its
[matched result](reports/path-pca-matched/README.md) is now in this checkout.

There are **four registered worktrees**, not one: this root plus
`work/issue-6-pca`, `work/cebra-full-trial-transfer` (merged PR #9), and
`work/cebra-time-teach` (open PR #10, already included via #11). Atlas PR #8 is
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
were forward-replayed without fitting. [Draft PR #7](https://github.com/Hong-yiii/neuro_science/pull/7)
remains open for user review; no more biological fits are queued by this handoff.

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
branched from experiment PR #9 at `c19d07c`. [Teaching PR #10](https://github.com/Hong-yiii/neuro_science/pull/10) is open, not merged, and stacked on
`feat/cebra-full-trial-transfer`, not `main`, to avoid duplicating the experiment
changes before #9 merges. This is teaching/documentation QA only: no new model
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
software merged through PR #11, substitute `--branch main`. The new
`planning/project-direction-20260927` branch is local-only until deliberately
published. Every checkout needs authorized private inputs/artifacts separately;
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
