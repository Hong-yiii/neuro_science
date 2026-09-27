# Frozen CEBRA decoder autoresearch — prefit contract

2026-09-24 (Asia/Singapore). **New user-authorized exploratory analysis.**
User requested execution of the [decoder research plan](cebra-nonlinear-readout-research-20260923.md), anchored to the current experiment and baseline, with delegated autoresearch. This contract freezes the bounded comparison before new biological readout fits. It does not restart historical encoder searches or the separate PCA PRD.

## Question, authority and independent observations

Does a different fixed readout recover more source-disjoint path-component separability from the *same* saved CEBRA embeddings than the archived linear decoder? The target is **D_N_R_T__N_R_M**, interior presence after excluding first/last corridor runs, at fixed endpoint **4→3**. Reuse original accepted QC/inclusion, first-second ten100ms bins, 29 selected units/7 sessions, 82 original training trials and22 historical-validation trials. No data/cohort/target expansion.

Source trials nested in sessions are the independent source objects; serial independence is unresolved. The30 exact validation combinations (24 absent,6 present) reuse22 sources. Half of evaluation weight belongs to each class. This is known-label-conditioned cross-session pseudopopulation separability, not unknown-real-trial prediction or verified simultaneous activity. Missing recordings remain masked during source-block reconstruction; no zero-filling. The original test/development exposure is permanent. All results remain exploratory, with unresolved cue/history/view and laboratory metadata confounds.

Accepted source tensor SHA256:
`688e3b52f69a872c7aec420da99ebb6f0b80464351ded3813b077cd7ed3cf567`.

Inputs: `outputs/path-generalization-20260907/results-20260907T081200Z/track_b/`; selected source tensor under `outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/v7-v8-neural-experiments/primary29_min3train_min1val/bin100ms/`.

Observed eligibility: both `cebra_time`/`cebra_behavior`, `family_role=crossed_seed_primary`, dim8,64 rows/class,1000 updates, assembly and optimizer seeds each0..4, no permutation: **50 frozen encoders**, each train(128,80), validation(30,80). Eight coordinates/bin are80 readout features, not an8D whole-trial state. Freeze exact fit IDs/hashes in the audit receipt before run. No historical winner/checkpoint selection.

## Fixed recipe family

All learned transforms fit training data only. Binary classes are0=absent,1=present. All random_state values0, CPU threads2. No inner CV, threshold tuning, validation selection, sign flipping, automatic retries with new settings, or additional recipes after results.

| ID | Recipe | Role |
| --- | --- | --- |
| logistic_scaled_c1 | StandardScaler + L2 LogisticRegression C1, solver liblinear, class_weight balanced, max_iter1000 | Archived current baseline: forward-replay saved state for CEBRA; fit same recipe for raw/PCA |
| logistic_scaled_c01 | Same, C0.1 | Stronger regularization |
| logistic_scaled_c001 | Same, C0.01 | Strongest fixed linear control |
| logistic_unscaled_c1 | Same C1 logistic without StandardScaler | Geometry/scaling control |
| knn_cosine_5 | KNeighborsClassifier k5, metric cosine, weights uniform, algorithm brute, n_jobs1, no scaling | Local nonlinear readout |
| knn_cosine_15 | Same, k15 | Fixed smoother neighbourhood |
| svm_rbf_scaled | StandardScaler + SVC C1, kernel rbf, gamma scale, probabilityFalse, class_weight balanced, tol0.001, max_iter100000, cache_size200 | Smooth nonlinear boundary |
| svm_rbf_unscaled | Same SVC without StandardScaler | Angular-geometry-preserving input control |

Both SVM recipes are mandatory, not optional after inspection. Library defaults not explicitly named must be captured in saved estimator parameters/version. Any convergence warning is retained and the affected fit flagged; no silent promotion, budget expansion or refit. Exact original training-row count stays128, so the fixed C values are comparable within this assay. Do not transplant them into larger synthetic training matrices.

Matched representations: raw290 count features and train-fitted cellspace PCA8/bin→80 features, separately for each of5 training assembly seeds. Reconstruct from source tensor and manifests; prove neural arrays reproduce archived hashes and scaler state. Fit StandardScaler/PCA(full SVD,8 components,no whitening) on training pooled bins only; apply to both splits and save state. This is **five newly fitted training-only PCA transforms**, not five new CEBRA encoders or execution of the newer PCA PRD. Record any discrepancy from old PCA implementations rather than silently claiming byte-equivalent old PCA scores.

## Sequential rounds and maximum budget

1. Audit hashes, shapes, finite values, masks, trial/label/block identities, exact weights and source disjointness. Forward-replay all saved baseline probabilities/metrics against archived predictions. Abort on contradiction.
2. Fit the three additional linear controls, all fixed arrays; log results without changing the family.
3. Fit all four nonlinear recipes, same arrays. Matched raw/PCA fit all eight recipes.
4. Run the predeclared null and source-sensitivity diagnostics, forward-only verification, independent results/claim review, and report.

**Observed:**50×7=350 new CEBRA-feature readout fits, plus10 raw/PCA feature sets×8=80 readout fits. **Null:**40 saved matched null encoders×7=280 new readout fits if lineage passes. Total maximum **710 new readout fits +5 PCA fits**,90 saved-baseline forwards, **zero new CEBRA fits**. kNN fit calls count in this ledger even though they store rather than optimize neighbours. No GPU, installs, lab access, raw/test imports or checkpoint deserialization/inference needed. Same-training-source reassembly has saved metrics but no embeddings: cite it as historical context, do not regenerate it in this run.

Synthetic software checks and runtime estimate precede independent prefit code review. Execution cap30minutes/two computational threads; stop incomplete on cap or integrity failure, retain partial artifacts separately. Operational retries with exactly unchanged inputs/config may use fresh attempt directories and explicit failure records; they are not replications. No adapting recipes to a negative result. No daemon or persistent viewer.

## Metrics and decisions

Primary descriptive comparison: paired change in exact-Q **balanced accuracy** relative to saved logistic_scaled_c1, summarized separately for Time/Behavior over25 matched crossed seeds; report all50 rows and min/max. These are algorithm/assembly sensitivities, not25 biological replicates. Raw/PCA have5 assembly seeds and must not acquire artificial replication from encoder seeds. Report paired raw/PCA comparisons with appropriate assembly matching.

Also report BA−0.5, class recalls, predicted-positive fraction, AUROC, training-vs-validation gap, and baseline-relative deltas. For logistic/kNN include balanced logloss (probability clipping1e−9) and Brier (state clipping convention matching historical metric). SVM uses signed decision scores and fixed0 threshold, with probabilities/logloss/Brier explicitly absent; do not sigmoid margins or enable internal probability-calibration CV. Probability-producing methods use p≥0.5; odd-k voting avoids an even-neighbour tie.

A **descriptive nonlinear follow-up candidate**, not a biological discovery, requires within an objective: mean BA>0.5, mean AUROC>0.5, and mean BA at least0.05 above the largest mean BA of the four fixed linear recipes. The5percentage-point margin is an engineering prioritization rule, not a lab-agreed meaningful effect or power calculation. Comparing against the linear envelope is descriptive, not nested selection. A gain that stays at/below chance is labelled **improvement over a below-chance baseline only**. No candidate passing is a complete, reportable outcome. Even a passing point estimate needs source-sensitivity and null context; never label it confirmed H1 or robust biology from this development set.

## Null reuse — narrowly matched and exploratory

There are20 source-label-shuffled saved encoders per objective for dim8/rows64/1000,A0/O0. Source-label maps are stratified by session×split (endpoint fixed) and applied before conditional training/validation assembly, neural scaler and encoder training. Verify each map against both manifests and source tensor, class support and hashes before using it. Encoder supervision and assembly in each null must correspond to that world. Omit null inference with an explicit failed gate if this cannot be shown; do not fit new null encoders.

Apply **the same eight decoder recipes** to both observed A0/O0 fits and all40 null fits. Report inclusive plus-one tails using tolerance1e−12 for each fixed observed score and the new family statistic **max(BA−0.5)** over2 objectives×8 readouts, compared with the same maximum in each null world. This is a one-sided above-chance/no-association reference, **not** a test of equal decoder predictive risk or of the50-encoder seed mean. Twenty worlds give resolution1/21 and questionable serial exchangeability; state this prominently. The historical p19/21 is not reused as a p-value for this study. Raw/PCA are not part of this CEBRA-only null family.

Review reconciliation: a strategy reviewer requested centered absolute deviations. We center BA at0.5 but deliberately retain a **one-sided maximum**, because our question is correctly oriented above-chance prediction and we forbid flipping below-chance labels. A two-sided |BA−0.5| would answer a different question. Improvement-over-linear null differences may be shown descriptively but are not decoder-superiority p-values.

## Source sensitivity, not pseudorow confidence intervals

For all observed recipes, delete validation combinations containing one real validation source, keeping models fixed. Report number/class weight lost, remaining-class support, original retained-weight summaries, and class-rebalanced metrics when both classes survive. One-class/singleton deletion is inestimable, not a zero effect or missing result to hide. Never remove a unit/session by replacing its values with zero.

Use200 predeclared evaluation-only source-resampling worlds, RNGseed20260924: resample source identities within each session×class validation pool with replacement, carry each multiplicity to every product row using that source, normalize product weights to half per class. Share worlds across all observed representations/readouts. Save source draws/weights and paired metric sensitivities. Fixed models, no training-source resampling or reselection. Quantiles are empirical pool-weight sensitivity, **not** biological/animal/selection-adjusted confidence intervals. Singleton pools cannot reveal unseen source variability.

## Software, artifacts and acceptance

Reuse accepted reconstruction/metric/hash helpers when safe; do not clone the historical runner or alter accepted artifacts. Parent is scientific manager; one worker is sole code writer; fresh-context reviewers are read-only. Code lives in one new evaluator and one focused synthetic test module. Reuse installed NumPy/scikit-learn/scipy and retained runtime. Source snapshots, package versions, Git revision/dirty state, complete estimator/config values, fit IDs/hashes, labels/weights/lineage, model states, predictions, all fits/failures/warnings, elapsed time and outputs are recorded under a fresh `outputs/cebra-decoder-autoresearch-20260924/` attempt directory. No raw/bulky data in Git, commits, pushes or PR are requested here.

Save replayable models (numeric state or trusted locally created, hash-checked estimator files) and transform/input references. Forward-only verification must forbid fit entry points, recompute predictions, metric tables, null maxima/tails, bootstrap/source influence and decisions, and detect tampering. Synthetic tests cover nonlinear signal, no-signal/constant controls, class weights, masks/source-disjointness, label/lineage mismatch, train-only fitting, ties, baseline parity and fitting-forbidden replay. One small invented-data end-to-end check is preferable to an extensive framework.

Deliver human Markdown and compact offline HTML with figures/tables generated from verified summaries, an execution journal, all-recipe CSV/JSON summaries, replay receipt and independent code/science/results review receipts. Emphasize whether the decoder hypothesis was supported, weakened or unresolved, not merely the highest accuracy. AI review is QA, not lab verification or scientific peer review. Update the research index/workspace minimally after completion without overwriting existing edits.

## Prefit provenance

Read-only audit and strategy review:
`.pi-subagents/artifacts/outputs/00e771c8-78aa-455a-b44c-a22e1e1eb954/work/cebra-decoder-autoresearch-20260924/{artifact-audit,strategy-review}.md`.
The audit verified50 observed NPZ hashes/schema/source disjointness and availability of the40 matching null fits; execution still independently validates full manifests/null label maps. Current baseline mean BA historical Time0.249167/Behavior0.351667 is context, not a reason to select one new recipe.
