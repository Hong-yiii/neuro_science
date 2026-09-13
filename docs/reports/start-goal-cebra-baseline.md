# Start–goal pseudopopulation baseline

Status: **exploratory analysis**, not confirmatory H1 evidence. Specification
written before model fitting, 2026-09-07. Branch: `baseline/start-goal-cebra`.

## Question and claim boundary

Can cue-period activity from the current 195 place-selected units decode the
30 ordered `(start, goal)` conditions in a condition-matched synthetic population?
The independent source is a real trial within session, not a time bin or a
resampled pseudotrial. Source trials and sessions can remain serially dependent.

This adapts the previous student's *condition-decoding* baseline, not the entire
20-page analysis or its exact 233-cell/314-pseudotrial dataset. The historical
method used chronological cross-session pairing, percentile-based resampling,
and LDA. Here we use random session-block pairing and explicit pre-assembly
source separation. No actual paths, route families, geometry, or future neural
activity enter the predictor or matching key.

Allowed claim: exploratory start–goal condition decoding under this synthetic
assembly and split. Not exact path prediction, information beyond endpoints,
planning, intention, simultaneous covariance/dynamics, or an unbiased estimate
for all hippocampal neurons. Goal/cue identity, visual input, current start /
previous goal, trial history, and selection on successful trials are confounds.
Formal label semantics and unit selection/recording metadata remain unresolved.

## Frozen design

- Inputs: existing hash-verified `place195-all-sessions-20260830-v4` importer
  tables; original `place195-splits-20260830-v3` assignments remain unchanged.
- Development support inspection found that **all 58 sessions lack at least one
  of 30 conditions in the original validation partition**. Do not zero-fill
  missing session/condition blocks: that can reveal the target to a decoder.
- Modeling reads **only original training rows**, through `SplitFilteredAccess`.
  The original validation/test data are not fitted or evaluated. The old test
  has a previously documented exposure incident; this does not repair it.
- Current and immediately previous trials must both be successful, in original
  training, same session, sequential, and free of importer QC flags. Require the
  **current trial's** finite Ripple cue duration in `[1.0, 1.5]` seconds; previous
  cue spikes are not features. Record every exclusion.
- Start = previous successful marker digit; goal = current marker digit. Verify
  importer label agreement, marker triplets, poster IDs 1–6, and unequal ends.
  These are provisionally supported semantics, not new protocol verification.
- Freeze an **inner**, session-and-condition-stratified source split before
  reading neural values: roughly 25% validation, at least one source on each
  side. This random within-session split is weaker than block/session-held-out
  validation and remains development-only; it is not a fresh confirmatory set.
  Abort if any of 195 cells' sessions lacks two eligible trials in any class.
- Every synthetic row draws one real source per session with the same ordered
  pair. Keep all that session's cells and all bins from that source together.
  Every class uses the identical 195-channel panel. Sampling is with replacement
  **within** inner split only; save complete component IDs and reuse counts.
- Cue features: ten half-open 100 ms bins, `[0,1)` seconds from Ripple event 1,
  fully before event 2. No time warping, rate imputation, smoothing or navigation
  spikes. Verify spike-event/count conservation and complete observed exposure.
- Defaults: 16 training / 8 validation pseudorows per class; assembly/model seeds
  0, 1, 2; fixed inner-split seed 20260907. The multiple seeds measure assembly /
  optimization sensitivity, **not** additional independent biological samples.
- Joint 30-way multinomial logistic decoder, C=1, with training-only scaling.
  Models: raw totals, raw ten-bin counts, PCA-8 per bin, CEBRA-Time-8 per bin,
  CEBRA-Behavior-8 per bin. Concatenate ten latent bins (80 decoder inputs).
  PCA/scalers/CEBRA/decoder fit only inner training. Behavior CEBRA receives
  categorical joint pair IDs (no ordinal poster-distance assumption).
- CEBRA reuses the audited offset1-model and same-pseudotrial temporal loader:
  hidden width 32, batch 256, learning rate 0.001, temperature 1, 1000 iterations.
  No validation-selected bins, hyperparameters, stopping, or architecture search.
  Time positives never cross a pseudotrial boundary; cross-session biological
  dynamics are not restored by this constraint. Even CEBRA-Time receives
  **label-conditioned assembled data**; it is not target-free discovery.
- Historical companion: shrinkage LDA separately on each of the ten raw cue bins,
  decoding the joint class. All bins are reported, no selected-bin significance.
  Endpoint accuracies are marginals of the predicted pair, not separate heads.
- Primary metric: inner-validation **joint balanced accuracy**; also joint
  accuracy, macro-F1, log loss, and start/goal accuracy. Balanced synthetic class
  chance: 1/30 joint, 1/6 each endpoint. Save predictions and confusion matrices.
- Null: 20 full-pipeline source-label permutations within session and inner
  split, permuting complete joint pairs, not bins or already-resampled rows.
  Rebuild populations and refit raw/PCA/CEBRA + decoders; average the same three
  assembly seeds for observed and null statistics. This is an exchangeability
  diagnostic, not a calibrated serial-dependence-preserving significance test.
  Report the finite tail fraction but do not claim confirmatory significance.
- Save input and code hashes, dirty diff, package versions, device, full config,
  split assignments/hash, shapes, exclusions, reuse, predictions, checkpoints,
  loss curves, train-only scaler/decoder parameters, save/load parity, failures,
  and a bounded results summary. Never overwrite a run directory.

## Independent pre-fit review

A fresh read-only reviewer found no fit-blocking leakage issue in this bounded
specification. Required cautions are retained: labels are **inferred marker-minor
transitions** interpreted provisionally as endpoints; random inner splits retain
serial dependence; both representations see condition-matched assembly; and this
is a place195 adaptation, not an exact historical replication. A separate code
and artifact review is required before interpreting the result.

Code review prompted a wording clarification: the full-second duration filter
applies to the **current** cue only; the preceding trial supplies a successful
endpoint label, not neural features. The implementation and source split frozen
before fitting were unchanged; a regression test now makes this explicit. An
initial reviewer concern about a missing split hash was checked against the
actual `inputs.json`, which records both the logical original hash and the CSV
byte hash. Automatic formatting during review left the analysis AST identical
to its saved run snapshot; the snapshot remains the exact executed source.

## Completed run: 2026-09-07

The single predeclared GPU run completed successfully in about **16.5 minutes**:
126 CEBRA fits (6 observed, 120 null), 1000 iterations each, plus raw/PCA/LDA
comparisons. No hyperparameter, time-bin, or source-split search followed the
scores. CEBRA checkpoint reload differences were zero in the saved fit receipts.

### Inner-validation results

Means across three assembly/model seeds; seed ranges are sensitivity, **not**
confidence intervals. Joint accuracy equals joint balanced accuracy because the
synthetic evaluation has eight rows per each of 30 classes. Start/goal scores
are marginals of the decoded pair, not separate classifier heads.

| Representation + decoder | Joint accuracy | Seed range | Start accuracy | Goal accuracy | Mean shuffled joint accuracy |
| --- | ---: | ---: | ---: | ---: | ---: |
| Uniform chance | 3.33% | — | 16.67% | 16.67% | — |
| Raw 1-second totals | 54.86% | 50.42–58.75% | 60.28% | 83.19% | 3.25% |
| Raw ten-bin counts | 71.39% | 69.58–73.33% | 76.39% | 89.31% | 3.01% |
| PCA-8 per bin | **82.50%** | 78.33–85.42% | 86.53% | 90.56% | 3.03% |
| CEBRA-Time-8 per bin | 42.78% | 36.67–50.42% | 54.58% | 73.47% | 2.99% |
| CEBRA-Behavior-8 per bin | 18.61% | 17.08–20.83% | 33.19% | 46.53% | 3.56% |

**The endpoint-condition baseline works in this synthetic benchmark, but this
fixed CEBRA configuration does not improve on PCA or raw-count decoding.** This
is not a comparison proving PCA universally better than CEBRA. CEBRA-Behavior
also has poor probability calibration here: mean joint log loss 5.06, worse than
uniform prediction (`log(30) = 3.40`), despite above-chance top-1 accuracy. PCA's
mean log loss is 0.66; CEBRA-Time's is 1.94.

All five observed mean joint accuracies exceed the 20 matched source-shuffle
means. The finite diagnostic tail fraction is therefore 1/21 for each, but it
is **not** a serial-dependence-calibrated p-value or confirmatory significance.

The historical-style joint LDA companion, reported without selecting a window,
gives mean accuracies of 7.78, 15.14, 13.61, 39.58, 37.08, 25.42, 27.08, 14.58,
21.67, and 11.67% in successive 100 ms bins from cue onset. This is not the
student's separate start/goal-head, 10-fold, 233-cell replication.

### Biological support versus synthetic sample count

- 195 selected units, 58 sessions; **15,553 eligible real source trials** from
  the old training partition only, divided into 12,288 inner training and 3,265
  inner validation sources.
- Per seed: 480 synthetic training rows and 240 synthetic validation rows,
  each with 195 cells × ten cue bins. These actually use 10,875–10,906 distinct
  training sources and 3,208–3,223 distinct validation sources across the three
  observed assemblies, rather than every eligible pool member. The source storage tensor is masked
  `15553 × 195 × 10`, not 15,553 simultaneous 195-cell trials.
- Exclusions among 16,859 original-training trials: 464 current failures, 562
  unavailable/unsuccessful predecessors, 32 current/predecessor QC flags, 248
  current cues shorter than the full-second inclusion requirement.
- Event/count conservation mismatches: zero. Each included bin has full 100 ms
  exposure; 6,300 eligible-cell spikes after nominal 1 s were intentionally
  omitted. Original validation/test rows yielded to modeling: zero.
- The sparsest session/condition pools have only **one source on each inner
  side**. More pseudorows do not create more evidence. Generalization to new
  sessions, subjects, or simultaneously recorded populations is untested.

Crucially, assembling an evaluation pseudotrial **uses its known true condition**
to select a real trial from every session. The neural decoder does not receive
that label as an input feature, but this measures a conditional synthetic
benchmark—not an end-to-end deployable decoder of one unknown-label real trial.

### Artifacts and verification

Run directory: `outputs/start-goal-cebra-20260907/` (about 495 MiB, retained and
ignored). It contains source splits/support/exclusions, masked source counts,
all pseudo component manifests, all predictions/probabilities, per-model
confusions, latent features, scalers/PCA/decoders, 126 final CEBRA checkpoints plus
intermediate checkpoints/loss traces, full configuration/package inventory,
code snapshot, and SHA-256 hashes.
See `summary.json`, `metrics.csv`, and `joint_accuracy.png` for the short result.
The original checkout and its uncommitted graph-path edit were not changed.

Validation receipts/scripts/logs are separately retained under
`outputs/start-goal-validation/`. Lint, runtime-configured Pyright, and all nine
synthetic/split-guard tests passed. One verifier attempt timed out from repeated
NPZ decompression; its cached-array retry changes verification only, not fitting
or results. The corrected verifier passed in 20 seconds: **2,251 artifact hashes**
and all input hashes matched, all **690 metric rows** recomputed from saved
probabilities, all **126 fit/loss/parity receipts** passed, and the observed plus
first-null source assemblies matched the stored source tensors exactly. All
20 source-label shuffles preserved within-session/inner-split class counts; no
original non-training source entered the analysis. See
`outputs/start-goal-validation/artifact-verification.json`.

Final independent read-only review found **no findings**: it separately checked
345 saved decoders (zero metric difference), observed prediction CSVs (zero
mismatches), all 15 summary aggregates, source/split/channel/null invariants,
observed and first-null reassembly, and all 126 CEBRA loss/parity receipts.
Its scientific limitations match those stated above. Full artifact hashes were
also confirmed by the parent verifier, closing its remaining verification item.

Follow-up: [CEBRA diagnosis, decoder ablations, and student comparison](start-goal-cebra-diagnosis.md).
Those are post-baseline development checks; they do not replace this frozen run.

## Run

From this worktree, reuse the existing research runtime without changing it:

```bash
export PYTHONNOUSERSITE=1 OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2
PY=/home/hongyi-home-lab/neuro_science/scratch/v6-v9-runtime/bin/python
$PY -m unittest scripts.test_start_goal_cebra_baseline
$PY -m scripts.start_goal_cebra_baseline \
  --import-dir ../neuro_science/outputs/prospective_path_first_run/place195-all-sessions-20260830-v4 \
  --split-dir ../neuro_science/outputs/prospective_path_first_run/place195-splits-20260830-v3 \
  --output-dir outputs/start-goal-cebra-20260907
```

Outputs are ignored/local. Input data are read in place: no raw-data copies,
shared-output writes, submodule edits, environment installs, or persistent
services. A temporary session-owned training command ends on completion.

Lazier comparison: raw counts plus LDA/logistic regression already test endpoint
decodability; CEBRA is included because it was explicitly requested, not because
an embedding is required to answer this baseline question.
