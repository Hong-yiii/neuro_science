# Single neuroscience workspace and current handoff

**Owner: Hongyi. Inspected September 10; takeover/consolidation resumed September 13,
2026 (Asia/Singapore).** The date `20260910` in consolidation paths identifies this
session, not the date every operation completed.

## One working copy, one current handoff

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
for exact evidence. Next steps are **decisions, not permission to run**: verify
metadata/nuisance controls, define a worthwhile effect, and freeze any 6→1
follow-up before genuinely new sources. Preserve the selected-195 scope.

## Where everything lives now

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

The latest accepted run is
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
was deleted or claimed backed up. There is now one registered local worktree.

## Recreate the software checkout

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
