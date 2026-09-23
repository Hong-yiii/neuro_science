# Agent evidence index — issue #6

**Authority:** [draft PR #7](https://github.com/Hong-yiii/neuro_science/pull/7), [question/protocol](protocol.md), [human verdict](README.md). Biological fitting is complete. Verification/review status must be checked in the receipts below; this index does not authorize another fit.

## Exact local roots

- Canonical checkout: `/home/hongyi-home-lab/neuro_science` (its pre-existing dirty documentation is untouched).
- PR worktree: `/home/hongyi-home-lab/neuro_science/work/issue-6-pca`; branch `feat/issue-6-matched-pca`.
- New run, relative to PR worktree: `outputs/path-pca-matched/biological-attempt-01/`.
- Accepted historical root, relative to canonical checkout: `outputs/path-preprocessing-autoresearch-20260908/biological-20260908T115508Z/`; accepted final `final-20260908T133200Z/`.
- Manager/source manifest, relative to canonical checkout: `outputs/path-autoresearch-management-20260908/prefit-selected-sources.json`.
- Retained runtime: canonical `scratch/v6-v9-runtime/bin/python`. No dependencies installed or changed.

## Data → fitting → verification → report

| Evidence | What it establishes |
|---|---|
| `input-audit.json`, historical `export/export_manifest.json`, pinned source/tensor hashes in protocol | Fixed observed counts/exposures/masks, source/cell/fold identity and accepted exclusions; **not lab verification of missing metadata** |
| `prefit-gate.json`, `reviews/prefit-*.md` | Independent prefit code/science approvals, synthetic checks, exact code/protocol hashes and bounded budget |
| Run `start.json`, `code/`, `tensor.npz` | Clean execution commit `c85409b5026aeeb196d20e1c0dea2e0aaaf6b632`, exact executed snapshots, runtime, source copy and original input paths |
| Run `observed/cv_*`, `observed/selection.json`, `SELECTION-FROZEN.json` | Six recipes × five endpoints × three source folds; both λ=1 selections saved before new historical evaluation |
| Run `observed/validation_*`, `anchor.json` | All-six same-source historical evaluation; raw anchor probability difference exactly zero |
| Run `null_ordinary/world-*`, `null_temporal_half/world-*`, `nulls.json` |100 worlds/kind with both arm selections repeated and full per-world state/probabilities/lineage; actual movement and pure strata |
| Run `bootstrap/resample-*`, `bootstrap.json`, `assembly/seed-*`, `session/` |200 shared source resamples, two fixed-recipe assembly seeds, paired13-session influence refits |
| Run `fits.jsonl`, `console.log`, `fit-budget.json`, `summary.json`, `artifact-hashes.json` |26,266 completed fit instances, full attempt log, scientific aggregates and local artifact integrity |
| `verification.json` | Full forward-only replay receipt; inspect status/count rather than assuming success from a process exit |
| `summary.json`, `report.md`, `report.html`, `report-evidence.json` | Lightweight result summary and generated numeric tables/figures; no fitting during rendering |
| `reviews/postfit-*.md` | Independent numerical and claim/report checks; AI assistance is not human peer review |

## No-fit verification and rendering

Run in the PR worktree, using a **fresh** verification receipt path. Do not use Python `-O`; assertions are part of verification.

```sh
export PYTHONDONTWRITEBYTECODE=1 PYTHONNOUSERSITE=1
export OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2
PY=/home/hongyi-home-lab/neuro_science/scratch/v6-v9-runtime/bin/python
RUN=outputs/path-pca-matched/biological-attempt-01
"$PY" scripts/verify_matched_pca.py "$RUN" \
  --output outputs/path-pca-matched/biological-verification-NEW.json
"$PY" scripts/build_matched_pca_report.py "$RUN" \
  --verification outputs/path-pca-matched/biological-verification-NEW.json \
  --output docs/reports/path-pca-matched
```

The verifier forbids classifier/scaler/PCA fit entry points and SVD. It regenerates source draws, uses saved scalers/projections/coefficients, checks PCA covariance/orthogonality identities, independently recomputes metrics/selection/tails/paired summaries, and rejects corruptions. Assembly, label permutation, bootstrap construction and forward helpers are shared: not wholly independent software.

The renderer requires a matching verified summary, checks input artifact hashes and independently recalculates observed table metrics, then emits two inline SVG illustrations, Markdown, HTML and their evidence hashes. No viewer/server is installed or left running. The HTML has no scripts or external assets; download and open locally.

## Attempts and retention

Three numbered invented-data CLI attempts are retained separately. Attempt01 fitted272 synthetic models but replay exposed a model-payload parser bug; attempts02/03 passed complete replay after repair. Unit-test fixtures are temporary and cleaned by their test context. Their synthetic fits are not part of the biological fit count.

There is exactly one biological attempt,26,266 fit instances, completed in1408.738s (~23.48min). Its local artifact set at completion was297,558,917bytes, under the2h/10GiB cap. No biological retry or tuning extension occurred. Postfit verification/rendering do not add scientific fits. Full logs and review-agent output live in this worktree's ignored `work/`; the failed synthetic records are not pooled with accepted biological evidence.

Keep the PR worktree and local run while review is open. After user-approved merge, migrate/hash its accepted outputs into canonical storage and update this map before removing the worktree. Preserve the canonical data/runtime and other sessions' work. Git alone cannot restore private inputs/full models; no off-host backup or restore rehearsal was performed.
