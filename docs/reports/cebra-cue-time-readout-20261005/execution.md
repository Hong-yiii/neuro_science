# Execution, review and recovery

## Scope and authorization

Hongyi explicitly asked to execute the proposed bounded study on October5,2026.
This is an exploratory decomposition of the accepted September24 source pools,
not an independently sourced replication. Performance uses final1000 updates;
checkpoint250/500/750/1000 geometry is separate and descriptive. No encoder,
PCA, GRU, new-source, goal, navigation-evaluation or whole-path fitting was added.
The original whole-cue readouts and preprocessing were preserved.

## Gates and attempts

1. Read-only scientific preflight `5773a0b1-af9e-4e87-a402-844b0d3dddd5`
   required explicit null families and cue-bin validity. These were frozen before
   biological readout fitting. Historical LDA remains context, not a newly fitted
   baseline family in this bounded decomposition.
2. Preparation worker `996e2827-3590-4867-8545-64252174fb90` hit its20-minute
   limit after preparing code/docs,7 passing invented-data tests and a no-fit
   audit. One initial test's expected null arithmetic was corrected before any
   biological fit. The first geometry attempt produced no artifacts and is not
   counted as a completed scientific result. Worker transcript is retained under
   `/tmp/pi-subagents-uid-1000/async-subagent-runs/996e2827-3590-4867-8545-64252174fb90/`.
3. Independent code review `9320161e-25e9-4aa8-ab74-f6cb97c7e8cd` found two
   prefit blockers: accepted-manifest enforcement and missing window identity in
   the inherited replay comparator. Parent fixed both; also added original
   whole-cue numerical parity, source-map reconstruction, full summary/sensitivity
   replay, bin-versus-whole source sensitivity, full spectra/per-bin stability,
   source-audit hash binding and runtime/helper snapshots.
4. Task `bbfd8ba82` passed20 invented-data tests, full accepted-manifest/source
   audit and observed-only geometry. All63 world/seed assemblies were reconstructed.
   Source audit: `preparation/audit-reviewed-20261005/source_support_audit.json`;
   SHA256 `15a6718256f2ed17f7b2dd5bfaae4825001e4388b6cf5c5fd704567add0318fa`.
5. Independent re-review `1745db7b-a5a8-44e1-84f1-3752d053572e` found no
   remaining launch blockers. Parent then wrote the hash-bound approval at
   `preparation/prefit-approval.json`, explicitly limiting execution to5040
   single-bin fits and504 whole-cue replays. Frozen fitter SHA256:
   `1521683a91cb958de6c12b0d1745df4e7168269bd2446f1ae5ed3a42bd0ee75b`.

All preparation/run paths in this document are relative to
`outputs/cebra-cue-time-readout-20261005/` unless otherwise stated. Initial audit
and review logs are retained for provenance; they are not additional fitted runs.

## Completed execution and no-fit replay

Task `b3209f873` completed in3m10s with exit0, using the existing
`scratch/v6-v9-runtime/bin/python`, CPU and two numerical threads. No installation,
raw recording extraction, test-source access, network service or GPU training.

- Accepted new run: `run-reviewed-20261005/` (about112MiB).
- Forward verification: `run-reviewed-20261005-verify/` (about7.7MiB).
- 5040 new readouts:2520 logistic +2520 SVM, each with its train-only readout
  scaler;504 saved whole-cue readouts replayed, zero whole-cue refits.
- 0 new biological CEBRA encoders and0 new biological PCA transforms.
  Invented-data software smoke tests exercise tiny training calls separately;
  they are excluded from scientific fit counts and never used as evidence.
- 11088 train/evaluation metric rows and875952 prediction rows across all
  observed/null worlds, seeds, representations, readouts and windows.
- No-fit verification reproduced every prediction and both secondary null
  families, all whole-cue references, confusions and source sensitivities.
  Maximum prediction-score difference was2.554e-14; maximum metric difference
  1.111e-16. The new run's whole-cue outputs replayed with exactly0 difference.
  Comparison with the original historical CUDA-produced files differed by up to
  1.57e-6 in score and3.39e-7 in metrics (within frozen tolerances); labels and
  sources were identical, and no historical decoder was refitted.
- Verification completed2026-10-05T14:00:16Z (22:00:16SGT).
- Geometry: `preparation/geometry-reviewed-20261005/`;24 saved checkpoints,
  528 spectra rows and528 stability rows, no trained readouts. Its own manifest
  verifies the generated artifacts. Final-to-final stability is1 by construction.

Logs remain in canonical `.pi/tasks/session-3046298-3046298/`:
`bbfd8ba82.output`, `b3209f873.output`, and report task `b088ed838.output`.
The `journal.jsonl` records every started/completed readout. Code/helper/protocol
snapshots, runtime versions, command, Git revision/dirty state, approval and
hash manifests live with the accepted run. No failed biological readout attempt
was pooled into the result.

## Report and verification commands

The separate renderer consumes verified CSVs only, under a fit-blocking guard.
It produces16 figure files, embedded offline images,88 mean rows with seed
vectors,528 observed train/evaluation seed metric rows,1056 confusion rows,
source counts and full geometry exports. No browser/server is required.

```sh
export PYTHONDONTWRITEBYTECODE=1 PYTHONNOUSERSITE=1
export OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2
PY=/home/hongyi-home-lab/neuro_science/scratch/v6-v9-runtime/bin/python
ROOT=outputs/cebra-cue-time-readout-20261005
# Read-only numeric replay; choose a fresh receipt directory, never repeat fitting.
$PY scripts/cebra_cue_time_readout.py verify \
  --run-dir "$ROOT/run-reviewed-20261005" \
  --output-dir "$ROOT/verify-FRESH-TIMESTAMP" --device cpu
# Regenerate the report from the existing accepted verification.
$PY scripts/render_cebra_cue_time_readout.py \
  --run-dir "$ROOT/run-reviewed-20261005" \
  --verified-dir "$ROOT/run-reviewed-20261005-verify" \
  --geometry-dir "$ROOT/preparation/geometry-reviewed-20261005"
$PY -m unittest scripts.test_cebra_cue_time_readout \
  scripts.test_cebra_full_trial_transfer scripts.test_cebra_cue_time_report
```

The earlier `cebra_cue_time_readout.py report` subcommand is a minimal preparation
renderer, not the final delivery route; use `render_cebra_cue_time_readout.py`
above. The **executed snapshot** in the accepted run remains byte-frozen at the
recorded approval hash. Before publication, the working-copy fitter received
formatting-only changes: its current SHA256 is
`f3b745f3ddfb81f11d5fc6f3180bad09726c7253145dc401b6f910ae4ba653cb`.
A location-free Python AST comparison verified it is identical to the executed
snapshot. This does not re-authorize fitting: the historical approval remains
bound to the original bytes. Its old preparation renderer was deliberately not
removed during publication; the separate final renderer above is authoritative.

Final delivery task `b5c2cce93` passed22 tests (20 invented-data tests plus2
artifact-QA checks). QA verifies all16 embedded PNGs and their alt text, all
local report links,88 mean rows with seed arithmetic,1056 confusion rows,
verification/render receipts, and132 final-checkpoint participation ratios
independently computed from saved embeddings with a covariance identity rather
than the producer's SVD helper. Those last two tests require the retained private
outputs and generated report; they are not data-free software tests. The
renderer/report tests have clean primary LSP diagnostics and Ruff checks;
session-wide lens diagnostics reported no remaining blocking errors. Intentional
fail-fast numeric conversions in the offline renderer were marked as structural
scanner false positives, not hidden behind exception swallowing. Key performance,
null and confusion figures were also visually inspected.

## Interpretation and review status

Independent numerical/claim review `e7d00f04-318f-4546-89bf-4f6a8504f205`
recomputed every metric group directly from saved predictions without producer
summary helpers: maximum difference8.88e-16, no mismatches. It independently
verified all counts, the9/21,17/21 and8/21 family tails, historical whole-cue
parity and sampled source sensitivities. Two low-severity documentation issues
were resolved: this execution link now exists, and the report says completed
**new**, not "missing", readouts. Review stayed read-only; checkpoint internals,
raw acquisition metadata and every rendered pixel were outside its coverage.
This is independent computational QA, not laboratory/scientific peer review.

The main limits remain historical exposure, sparse real-source support,
label-conditioned pseudopopulations, unresolved serial/nuisance exchangeability
and synthetic-row dependence. Window-specific readouts do not test frozen-readout
temporal or cross-phase generalization. High single-bin peaks are not validated
window selections, and negative null comparisons do not prove absence of biology.

## Preservation and lifecycle

Existing `evidence.py`, reports index, atlas test and untracked current-state
report were not changed. During the October5 analysis, no branch switch, staging,
commit, push, worktree change, package installation or persistent process was
requested or performed. The subsequent publication request is documented below. The
worker's own empty initial geometry directory was removed with `rmdir`; initial
audit and transcript evidence are retained. Session checks and runs terminate; no new host service registry entry is needed. Ignore
private model/data outputs in Git; retain them for reproducibility. Git alone
cannot restore them. Do not rerun fitting to recreate missing private artifacts.

## October6 publication handoff — leave PR open

Hongyi requested a focused PR targeting `main`, explicitly **not a merge yet**;
more work will be added on branch `analysis/cue-time-readout-20261005`. Scope is
this study's runner/renderer, regression and artifact checks, useful report
figures/aggregate tables, and the current-workspace pointer. The standalone HTML
embeds its figures for offline use; PNGs are retained for the Markdown report.
Private source arrays, fitted models, full predictions, task logs and publication
receipts stay under ignored `outputs/`, not in the PR. No unrelated pre-existing
changes are included.

At Hongyi's request the publication commit's author timestamp is
**2026-10-05T23:00:00+08:00** (yesterday in Singapore); the committer timestamp and
GitHub PR creation timestamp remain the actual publication time. Scientific
execution dates and saved records are unchanged. GitHub commit contribution
credit normally requires the commit to reach the default branch, so opening the
draft does not guarantee a yesterday contribution square before merge.
Publication preservation/validation receipts live under
`outputs/cebra-cue-time-readout-20261005/publication-20261006/`.
