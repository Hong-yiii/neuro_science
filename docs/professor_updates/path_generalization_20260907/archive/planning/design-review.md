## Goal
Diagnose whether poor Place195 CEBRA reflects method/assembly limits rather than biology, and define a bounded development-only path to a defensible methodological result.

## Findings
- **critical:** `outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/audits/holdout-exposure-audit.md` — original locked test is not pristine; future resplits are development diagnostics, not confirmation.
- **major:** `scripts/place195_v7_v8_neural_experiments.py:250,262,279,294` — pseudo rows are assembled with known class labels from session blocks; validation performance is for an empirical product distribution, not an operational unknown-trial decoder.
- **major:** `scripts/place195_v8b_v9_cebra.py:408-412,454,484-490` — CEBRA assembly seed and optimizer/model seed are coupled in accepted V9, so seed variance cannot be attributed cleanly.
- **major:** `outputs/.../v8b/v8b_session_label_bin2_source_counts.csv` — validation support is tiny: present per-session counts `[1,1,3,2,1,1,1]`, absent `[1,2,1,3,1,2,2]`; exact complete validation combinations are only `6` present and `24` absent.
- **major:** `docs/reports/place195-v6-v9-autoresearch-20260906.md` and `v9/v9_cebra_metrics.csv` — train BA is `1.0` for all observed CEBRA fits while validation BA is unstable/nonpositive; this is overfit/source-instability evidence, not negative biology.
- **minor:** `scripts/place195_v7_v8_neural_experiments.py:438` — `source_level_shuffle` groups by split/session only; valid for current one-endpoint input, but not reusable unchanged for broader endpoint/component enumeration.

## Plan
1. **Freeze claim ceiling first:** all proposed work remains exploratory/development-only; no “new clean holdout” language.
2. **Exact validation enumeration:** replace random validation pseudo rows with all feasible complete source-block combinations: 6 present and 24 absent, scored with class-balanced weights. Gate: if any result depends on duplicating sampled validation rows, stop interpreting BA.
3. **Seed factorization:** run CEBRA as `assembly_seed × optimizer_seed`, e.g. 5×5 minimum, with fixed validation enumeration. Prediction: if optimizer dominates at fixed assembly, implementation/objective instability; if assembly dominates, source-pool instability. Falsifies “one bad seed” only if both factors are low-variance.
4. **Rows-per-class exposure audit:** compare train pseudo rows `64/256/1024` while logging anchor/positive/negative exposure per source/session/label. Gate: do not call improvement “more data” unless fixed-source exposure explains it; pseudo rows add no biological N.
5. **Representation grid, no architecture search:** raw normalized input only; CEBRA output dims `3/8/16/29`; matched raw logistic and PCA `3/8/16/29`, including PCA-29 as “rotation/control,” not claimed dimensional biology.
6. **Exact product-distribution moments:** compute class-wise means/covariances for train and validation product distributions, including PCA-transformed moments fitted on train only. Gate: if train/validation class-difference directions are anti-aligned or dominated by one session, no CEBRA escalation.
7. **Source/session diagnostics:** report per-session label means, validation combination influence, leave-one-session-block-out, source reuse, and per-source exposure. Prediction: poor CEBRA should track sparse sessions like the bin-2 artifact; falsified if signal is stable after deleting any one session.
8. **Nulls matched to the whole adaptive family:** source-label shuffle within session/split/endpoint, rebuilding assembly, PCA, CEBRA, decoder, and selecting max over declared dims/seeds/rows. Gate: observed must beat family null before any “promising” language.
9. **Independent source resplitting:** create several source-disjoint train/validation resplits after all rules freeze; label as development robustness only. Gate: if direction/score flips, the direction is not reproducible.
10. **Only if supported, test source-preserving contextual models:** prefer per-session encoders/shared-context CEBRA or simple hierarchical encoding/decoding that keeps one real source trial per row. No common-panel stitching claim, no simultaneity claim.

## Files To Modify
- `scripts/place195_v8b_v9_cebra.py` — add separate `assembly_seed`/`optimizer_seed`, dims `16/29`, rows grid, fixed validation-combination scoring, and minibatch/source exposure logs.
- `scripts/place195_v7_v8_neural_experiments.py` — add exact product-distribution moment calculations and source/session diagnostic exports.
- `scripts/place195_split_filtered_access.py` — no scientific change unless broader endpoint enumeration needs an explicit allowed-artifact mode.
- `docs/reports/place195-v6-v9-autoresearch-20260906.md` — do not edit historical report; write a new dated follow-up if experiments are run.

## New Files
- `scripts/place195_v10_product_diagnostics.py` — exact validation enumeration, analytic moments, family-aware null summaries.
- `scripts/test_place195_v10_product_diagnostics.py` — fixture tests for product moments, validation weighting, and seed factorization.
- `docs/reports/place195-v10-development-diagnostics-YYYYMMDD.md` — future report if the bounded diagnostics are executed.

## Risks
- A behavior-conditioned CEBRA positive would be circular unless judged only by held-out, source-safe downstream prediction and matched full-pipeline nulls.
- Endpoint-fixed labels still correlate with cue identity, previous goal/history, gaze/view, action, speed, success selection, and session.
- Cross-endpoint shared-component analyses are near-circular if path overlap is determined by start/goal mixture.
- More pseudo rows or minibatches can improve optimizer exposure without adding independent observations.
- PCA covariance on product-assembled rows is not simultaneous population covariance.
- BA below 0.5 cannot justify post-hoc label flipping.
- A provable contribution would be methodological: a reproducible audit showing when source-limited pseudopopulation CEBRA is identifiable, leakage-safe, and non-operational—not positive hippocampal biology.