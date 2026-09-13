# Execution ledger and review gates

## Workspace and scope

User requested a separate worktree and draft PR on 2026-09-13. Branch `feat/issue-6-matched-pca` starts at `origin/main` merge `d1228d3`. Worktree: `/home/hongyi-home-lab/neuro_science/work/issue-6-pca`. The canonical checkout's existing modified workspace/report index and untracked PRD/weekly report remain untouched. No historical worktree was recreated.

Retain this worktree during PR review. After user-approved merge, hash/migrate its owned accepted outputs to canonical `outputs/path-pca-matched/`, record paths, then remove the worktree. Do not remove raw inputs, retained runtime, other sessions' artifacts or the worktree while review is active. This task introduces no daemon, service, schedule, external data transfer, dependency install or GPU job.

## Before biological fitting

- Strict input audit passed: accepted source-tensor and selected-source hashes, 147+41 sources,49 units,13 sessions,756 observed pairs; all188 records have empty accepted QC flags and unverified candidate simultaneity. Cue durations1–1.127033s; analyzed window remains[0,1).17/28 validation pools are singletons. Full audit is retained locally and a lightweight copy accompanies the PR.
- Initial synthetic execution completed272 invented-data fits but its replay failed: historical model payloads store the scaler as a state mapping, whereas candidate rows store a name. The new verifier's roundtrip assertion exposed the parser treating that mapping as a string. Fixed the shared parser to read `kind` for saved mappings; normal recipe parsing and historical prediction math unchanged. Regression covers raw and PCA roundtrips.
- Synthetic attempt02 completed272 fits and forward-only replay passed. Attempt03 additionally covers explicit raw/PCA fallback metadata and exact-constant numerical handling. It too completed272 fits and272 forward replays with zero fits during verification. Attempts01–03 remain separately retained; these are software tests, not biological evidence.
- Focused suite:20 tests (6 new+14 historical) passed. Repository suite:102 tests passed, with the existing two named private-input tests excluded by its runner. Retained Python environment, no installation. LSP checked four affected files; two confirmed clean, two timed out even at4000ms. No reported errors, but timeouts are **inconclusive**, not passes. Ruff checks on the three new scripts passed.
- Independent fresh-context read-only scientific review found the test file missing while implementation was still in progress. File now exists and tests pass; its methodological limitations were accepted rather than presented as repaired metadata. Independent code reviewer approved the current bounded implementation. Full review texts and their follow-up resolution are retained under this package's `reviews/`.
- Synthetic attempt02:272 fits in3.3356s; full directory1,504,303bytes. Linear26,266-fit extrapolation322s; an explicit8× overhead allowance for larger real panels/products gives2577s(~43min) and1.16GB. This is a planning estimate, not a performance guarantee. Frozen caps remain2h and10GiB, no reduction of controls if exceeded.
- Biological budget:26,266 completed fit instances; no new biological fits have occurred at this ledger's initial creation. A hash-bound approval gate must be recorded before launch. Later outcomes belong in the appended result section, not backdated into this prefit record.

## Reproduction commands

From the PR worktree (keep full inputs/models local):

```sh
export PYTHONDONTWRITEBYTECODE=1 PYTHONNOUSERSITE=1
export OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2
PY=/home/hongyi-home-lab/neuro_science/scratch/v6-v9-runtime/bin/python
"$PY" -m unittest scripts.test_matched_pca scripts.test_place195_path_preprocessing_autoresearch
"$PY" scripts/check_research_software.py
# New synthetic output directory required; never overwrite an accepted run.
"$PY" scripts/place195_matched_pca.py synthetic --output outputs/path-pca-matched/synthetic-NEW
"$PY" scripts/verify_matched_pca.py outputs/path-pca-matched/synthetic-NEW \
  --output outputs/path-pca-matched/synthetic-verification-NEW.json
```

Do not rerun biological fitting just to render the report or verify saved results. Private inputs/models are not recoverable from this PR alone. The source/export/manager remain at the canonical checkout's accepted locations.

## Biological execution — completed September 14

Science follow-up resolved the initial missing-file blocker and approved the descriptive study. The hash-bound [prefit gate](prefit-gate.json) was written with **zero biological fits before approval**. Code/protocol hashes remained unchanged throughout fitting. Executed clean commit: `c85409b5026aeeb196d20e1c0dea2e0aaaf6b632`.

```sh
# Under the environment above; this is the recorded command, NOT a queued rerun.
"$PY" scripts/place195_matched_pca.py run \
  --source /home/hongyi-home-lab/neuro_science/outputs/path-preprocessing-autoresearch-20260908/biological-20260908T115508Z/export/source_tensors.npz \
  --manifest /home/hongyi-home-lab/neuro_science/outputs/path-autoresearch-management-20260908/prefit-selected-sources.json \
  --historical /home/hongyi-home-lab/neuro_science/outputs/path-preprocessing-autoresearch-20260908/biological-20260908T115508Z/final-20260908T133200Z \
  --review-gate docs/reports/path-pca-matched/prefit-gate.json \
  --output outputs/path-pca-matched/biological-attempt-01 \
  > work/biological-attempt-01-launch.log 2>&1
```

Supervisor task `b49f4ffe1` completed successfully; no worker remains from it. Internal budget1408.738s (~23.48min),26,266 completed fits,297,558,917bytes of artifacts, all converged. One biological attempt only.90 observed CV+30 historical;24,000 null;2,000 bootstrap;20 assembly;126 session fits. Both arms selected λ=1 at15:51:53Z on September13 before new historical evaluation. Exact original raw probabilities reproduced (max difference0); a separate compatibility check forward-replayed100 saved historical models across20 old recipes with zero fitting.

The summary records raw loss0.664563784 versus PCA0.657540885; paired difference+0.007022899. Both BA=.55. Source sensitivity spans both signs. This is a small descriptive method difference, not a broad biological result. See the [human verdict](README.md), full generated tables and independent postfit reviews. Verification/report receipts are recorded separately; do not interpret this run-completion entry as proof of their completion.

## Final verification and review — passed September 14

- Supervisor task `b1a43d27c` completed the full verifier and report in9m49s. [Verification receipt](verification.json): **26,266 forward replays, zero new fits**, matching all declared controls, resamples, selections, lineage and summaries. Scientific summary SHA256 `b6117dede4dda6c7872823a0192594935d035ccbd25c03e8a3229fe7cf077013`.
- Independent numerical reviewer approved the result/code; independent claim/report reviewer approved the actual generated Markdown/HTML and receipts after the earlier missing-artifact blocker was resolved. [Numerical review](reviews/postfit-numerical.md), [initial claim review](reviews/postfit-claims-initial.md), [final approval](reviews/postfit-claims-approved.md). Their unchanged scientific limitations remain in the reports.
- Final repository software suite: **102 tests passed**. Ruff passed all five affected Python files; Python3.11 syntax parsing passed. Primary LSP confirmed the smaller files clean, but the historical driver/new verifier still timed out even at10000ms. Those type checks remain inconclusive. Session lens cache reported no dispatched files for the ignored worktree, so it is not independent clean-project evidence.
- Report generation runs with fit entry points forbidden, checks matching verification/summary and input hashes, and recalculates observed table metrics. Headless Chrome rendered the actual offline HTML. Parent visually checked both SVGs and tables, corrected figure ordering and a pipeline-box text collision, then rerendered. These final cosmetic edits changed no scientific values or claims. Private screenshots/logs remain in `work/report-preview*.png` and `work/chrome-render*.log`; the disposable browser profile was removed after browser exit.
- Link/HTML and staged-artifact checks are recorded in `delivery-checks.json`. Only code, methods, reports, aggregate summaries and small audit/review receipts go to Git. No raw inputs, full models, per-trial tables, screenshots, environments or large generated artifacts are staged. Accepted run/logs remain local and ignored for review/recovery.

No biological fits were performed after the single completed run. Draft PR#7 stays open, unmerged, for Hongyi's review and discussion.
