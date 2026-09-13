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
