# Frozen-representation hyperparameter diagnosis — prefit contract

2026-09-24. **New user-authorized exploratory analysis; not yet executed.** Hongyi requested execution of hyperparameter ablations and a meaningful diagnosis of the CEBRA failure. A unique algorithmic fault or inherent task unsuitability is not an achievable guarantee from this design. We test competing explanations—readout regularization/bandwidth, confidence, and source transfer—without changing the observed encoder or target.

## Fixed question, inputs and allowed claims

Reuse the verified `outputs/cebra-decoder-autoresearch-20260924/recovery-20260924T042259Z/` artifact package, not the failed original attempt. Preserve the prior4→3 / interior `D_N_R_T__N_R_M` question,29selected units/7sessions,82training+22historical-validation source trials, first-second ten100ms bins, labels, training assemblies and exact evaluation weights. No original-test/raw imports, new cohort, new source split, encoder fitting, observed PCA fitting or outcome-driven recipe expansion. The September8 five-endpoint/49-unit study and separate PCA PRD are different tasks and are not rerun.

CEBRA has50 observed encoders (Time/Behavior × five assembly × five optimizer seeds), plus40 saved matched null encoders (two objectives ×20worlds atA0/O0). Observed raw/PCA have five assembly-matched feature sets each. Each training array has128known-label-conditioned rows (64/class); exact validation has30combinations (24absent/6present), sharing22actual sources. Half the evaluation mass belongs to each class. Source trials nested in sessions—not pseudorows, neurons, or seeds—supply independent-source support; serial independence is unresolved.

This is known-label-conditioned pseudopopulation separability, not prediction from a simultaneous natural trial, intention, causal planning, or H1b. Prior development/test exposure is permanent. Even a positive null reference remains exploratory; a negative result is not absence of information. No decoder calibration or winner selection is performed on an allegedly pristine test.

## Fixed comparison family and budget

All learned scalers/decoders use training arrays only, CPU and two computational threads. Each encoder receives its own decoder; no transfer of coefficients between differently oriented embeddings. No new features or thresholds.

1. **Scaled logistic L2 path:** C in `{0.001,0.01,0.1,1,10,100}`. Smaller C is stronger regularization. Same liblinear solver, balanced classes, max_iter1000, random_state0 and train-only StandardScaler as the prior assay. Reuse the verified C0.01/C0.1/C1 models; fit only three new settings where saved models exist. Numeric C comparisons are within the same128-row/scaling convention, not directly with the older study's average-loss λ or an SVM penalty.
2. **Scaled RBF-SVM grid:** C in `{0.1,1,10}` crossed with gamma multipliers `{0.1,1,10}` relative to the training-only sklearn `gamma='scale'` value. Define gamma0=1/(D×variance of scaled training matrix in float64), or1 for zero variance. Center C1/multiplier1 reuses the verified SVM. Other settings use the same SVC class weighting, probabilityFalse, tol0.001, max_iter100000 and cache_size200. Persist effective gamma, parameters and convergence warnings. No probability estimates from SVM margins.
3. **Confidence-only diagnostic:** for observed representations' existing C1 logistic predictions only, T in `{1,2,5,10}`, p=expit(original margin/T). No fitting or validation-selected T. Keep original labels/prediction boundary; positive temperatures must preserve BA and score-based AUROC. Report all settings. This tests how much loss changes can come from confidence alone; it is not calibration on new data.
4. Retain the four remaining legacy readouts (unscaled logistic, two kNNs, unscaled SVM) as context and include their existing CEBRA null results in the expanded CEBRA-family maximum. Do not refit or expand these four recipes.

**New readout fits:**60observed feature sets ×11new settings =660;40saved CEBRA-null sets ×11 =440;40new matched raw/PCA-null sets ×15grid settings =600. **Total1700new readout fits**, plus **20training-only PCA fits for null worlds only**. Reuse all800 prior saved model/forward outputs (400overlap the new15-setting grid;400legacy-only context). Thus2500model/readout records, of which2100belong to the new grid. **Zero new CEBRA fits and zero new observed-PCA fits.** Synthetic software checks are separate, invented-data fits.

Execution cap30minutes for the fitting/analysis stage; verification is separately bounded to30minutes. Do not increase the family, retry warnings with changed settings, select a checkpoint or stop at the first positive result. Persist started/completed/failed events and model/prediction state incrementally, but do not repeatedly rewrite the entire accumulated CSV after every fit. An interruption is retained as an incomplete attempt, not silently restarted or treated as a replication.

## Matched raw/PCA nulls — close the earlier control gap

Raw/PCA's earlier77.5% mean had no matched null. Add source-coherent controls now rather than interpreting that control as established signal.

The accepted audit shows that Time and Behavior share identical generated/exact manifests and reconstructed neural-array hashes in all20null worlds. Recheck this before fitting. For each world atA0, reconstruct raw training/validation arrays from its audited manifests and the accepted source tensor; verify reconstructed array hashes against the saved null entry. These are source-label shuffles within session×split performed before assembly. Do not shuffle only final decoder labels.

Raw features are the same flattened29×10 counts. Fit a separate scaler+PCA8/bin on that null world's training assembly only, no whitening/full SVD, preserving the existing transform convention. This adds20null PCA transforms. Reusing the observed PCA basis would fail to repeat label-conditioned assembly/preprocessing under the null; do not do that. Preserve numerical state and forward-replay these transforms. Source tensor hash remains `688e3b52f69a872c7aec420da99ebb6f0b80464351ded3813b077cd7ed3cf567`.

Report three predeclared one-sided max(BA−0.5) references with inclusive plus-one tails and tolerance1e−12:

- CEBRA family: two objectives ×19recipes (new15grid plus four legacy-only) =38;
- raw/PCA family: two representations ×15grid recipes =30;
- joint family: all68above.

Use observedA0/O0 for CEBRA andA0 for raw/PCA against the same20matched worlds. Also show fixed-recipe tails clearly labelled descriptive/exploratory. These are no-association references, **not decoder-superiority tests, not p-values for25-encoder or five-assembly means**, and not correction for the entire adaptive history of the project. Resolution is1/21; finite and partly immovable source pools/exchangeability caveats remain.

## Metrics, source sensitivity and diagnostic interpretation

For every model report training and exact validation BA, AUROC, class recalls, predicted-positive fraction, train–validation gap and paired deltas against its same-feature C1 logistic baseline. Logistic models additionally report clipped logloss (1e−9), unclipped Brier, weighted probability spread, weighted margin spread and fraction of probability mass near0.5 (|p−0.5|≤0.05). Coefficient norms are comparable only within a fixed feature/scaling representation; do not infer neural dimensionality from them. SVM margins retain their own arbitrary scale, not probability loss.

Show all six-C curves and all nine C×gamma cells, not just the best development score. Any maximum over this grid is a descriptive envelope, not an independently validated selected model. For consistency with the earlier study, a nonlinear follow-up lead requires mean BA>0.5, mean AUROC>0.5 and BA≥largest tested linear mean+0.05 within a representation. Include legacy unscaled logistic in that linear envelope. This is an engineering prioritization rule, not biological effect-size validation.

Reuse the exact200saved session×class source-resampling worlds and22source deletions; validate their hashes and alignment with every observed feature set. Models remain fixed. Report **BA and paired baseline-delta sensitivities** for all observed grid and legacy readouts. Numeric matrix storage/vectorized BA is acceptable: with half weight per surviving class, weighted correct fraction equals BA. Independently cross-check with explicit class recalls and tamper tests. Eight singleton deletions are inestimable rather than successful or discarded; preserve masks, original removed weights and remaining class support. These are pool-weight sensitivities, not animal/session/selection-adjusted confidence intervals. No training-source bootstrap refits or pseudorow CV.

Add a fixed, labelled **descriptive class-contrast alignment** diagnostic: in each representation's existing train-standardized coordinates compute delta_train=mean(train_present)−mean(train_absent), and delta_validation analogously from the exact class-conditioned validation rows; report their cosine and norms. Undefined zero-norm cases stay undefined. This uses validation labels for diagnosis only, not fitting/selection or a new decoder. A reversed contrast can suggest a source-specific mapping but cannot identify its biological cause or prove absence of other nonlinear information.

Allowed conclusions distinguish:

- reduced logloss with unchanged BA/AUROC under temperature: confidence effect, not newly decoded information;
- a weak-penalty or bandwidth rescue: evidence against blaming these frozen features solely from old decoder defaults;
- high training separation and consistently nonpositive held-out CEBRA despite the grid: failure of transfer in this tested pipeline, not proof of zero latent information;
- raw/PCA lead surviving/failing its matched null and source checks: strengthens/weakens that alternative explanation; never infer CEBRA suitability universally from one cohort;
- reversed class contrast: source-dependent association is plausible, not uniquely caused by an encoder bug, nor permission to flip labels posthoc.

Encoder objective, temporal architecture, sampling, representation dimension, nuisance variables and limited source support remain unmanipulated causal alternatives. The paper's current-position/direction benchmark differs from cue-to-future-path information. Do not conclude that prospective tasks are inherently incompatible with contrastive encoding.

## Software and acceptance gates

Prefer a thin new evaluator/test module reusing the accepted runner's numeric state, reconstruction, masks, class-local lineage, source-weight and metric helpers. Preserve prior code and output bytes. New outputs belong under `outputs/cebra-hyperparameter-diagnosis-20260924/`. Parent owns protocol/report; one worker owns code; independent reviewers are read-only. No installs, GPU, services, branch changes, commits/pushes or lab access.

Before biological fitting: no-fit audit of source/accepted receipt/input hashes, shapes, actual30×7lineage including class-local row IDs, source disjointness and20matched null maps; freeze protocol/code/dependency hashes; synthetic positive/no-signal tests, temperature invariance, RBF center/native prediction parity and a small end-to-end run→verify with fit methods forbidden during replay. Code and science reviews must approve. Verify all expected feature/recipe pairs and attempted-fit accounting, not only a total count.

Save all model states, predictions, source hashes, exact executed source snapshots, version/runtime/thread metadata, transforms, scalar diagnostics and full-family decisions. Forward-only verification forbids scaler/PCA/classifier fit APIs; recomputes predictions, all metric fields, temperatures, null tails, source BA/deltas, class alignment and summary copies; rejects missing/duplicate rows or tampering. Reused models are replayed, not merely copied metrics. Preserve failures separately and do not claim completion without accepted verification.

Deliver a human Markdown report and self-contained offline HTML showing regularization curves, kernel grids, confidence versus discrimination, source/null context, and a diagnosis table separating supported/unsupported/unresolved explanations. Independent numerical and final claim reviews precede acceptance. Update the workspace/index minimally while preserving existing work. No result is guaranteed by this contract; a bounded negative/unresolved diagnosis is a complete outcome.
