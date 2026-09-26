# Frozen CEBRA decoder experiment: no CEBRA rescue, a PCA control lead

**September 24, 2026 · Completed exploratory analysis, verified after a no-fit bookkeeping recovery.**
[Offline HTML](cebra-decoder-autoresearch-20260924.html) · [Frozen protocol](cebra-decoder-prefit-20260924.md) · [Research rationale](cebra-nonlinear-readout-research-20260923.md)

## Answer

**The tested nonlinear-readout explanation for poor frozen CEBRA generalization is weakened.** Across the complete fixed recipe family, neither Time nor Behavior CEBRA achieved mean balanced accuracy (BA) or mean AUROC above chance. No CEBRA recipe passed the predeclared nonlinear follow-up criterion.

- **Time:** original logistic BA **24.92%** → strongest nonlinear mean **37.33%** with scaled RBF SVM: **+12.42 percentage points**, but still below 50% chance; AUROC **0.141**.
- **Behavior:** original logistic **35.17%** → strongest nonlinear mean **35.67%**: **+0.50 points**, AUROC **0.201**. Stronger logistic regularization reached **35.75%**, slightly above that nonlinear mean.
- **Important control:** training-only PCA + scaled RBF SVM achieved **77.50% BA / 0.829 AUROC**, versus PCA's original logistic **42.92% / 0.157**. This is an exploratory representation/readout lead, **not a confirmed PCA result or H1 discovery**. Raw/PCA controls were outside this study's matched null family; there is **no PCA p-value** here.

The scope matters: this does **not** establish that all nonlinear decoders fail, that CEBRA is generally unsuitable, or that hippocampal path information is absent. It tests eight fixed readouts on this retained representation family and historically exposed development cohort. No MLP/deep-decoder sweep was performed.

## What stayed fixed

Target: interior presence of **D_N_R_T__N_R_M**, after excluding first/last corridor runs, within endpoint **4→3**. This is not the earlier start–goal classification task. Data comprise **29 selected unit IDs / 7 sessions**, with **82 training and 22 historical-validation source trials**. Recorded spikes are measured signals; count bins, PCA/CEBRA coordinates and the path-component label are derived representations; decoding is an association, not a measurement of intention.

Each cue contributes ten100ms bins. Eight coordinates per bin give **80 decoder inputs**, not an eight-dimensional whole-cue population state. Fifty frozen encoders cover Time/Behavior × five assembly seeds × five optimizer seeds. All eight readouts use the same training/evaluation arrays for a given representation. Raw counts have290 inputs; cellspace PCA8/bin has80, with five training-only StandardScaler/PCA transforms. Raw/PCA each have **five assembly-matched runs**, not25 artificial encoder replications. Mean CEBRA–control comparisons average the five optimizer runs within each shared assembly before the five assembly means; this equals the displayed balanced-grid means.

Evaluation enumerates **30 known-label-conditioned pseudopopulation combinations**:24 absent and6 present, each class receiving half the total weight. Those are not30 independent trials, and the25 CEBRA seeds are not25 biological replicates. The features combine separately recorded units. This is condition-level source-pool transfer, **not unknown-real-trial prediction from a simultaneous population**.

The old Track B cohort was chosen because its frozen embeddings exist. It is not the newer49-unit/five-panel preprocessing study, and the separate matched PCA/non-PCA PRD has **not** been executed by this assay.

## All eight CEBRA readouts

Means over25 fixed runs/objective. BA chance is50%; AUROC chance is0.5. `scaled` means training-only StandardScaler. Lower C means stronger logistic regularization. Both SVMs use C1/gamma=scale and uncalibrated decision margins; they do not supply probabilities.

| Readout | Time BA | Time AUROC | Behavior BA | Behavior AUROC |
| --- | ---: | ---: | ---: | ---: |
| Logistic scaled C1 — archived baseline | 24.92% | 0.111 | 35.17% | 0.206 |
| Logistic scaled C0.1 | 26.50% | 0.122 | 35.67% | 0.209 |
| Logistic scaled C0.01 | 28.83% | 0.159 | 35.75% | 0.210 |
| Logistic unscaled C1 | 27.25% | 0.181 | 32.67% | 0.202 |
| Cosine kNN, k5 | 35.00% | 0.292 | 31.08% | 0.288 |
| Cosine kNN, k15 | 35.83% | 0.267 | 32.92% | 0.253 |
| RBF SVM scaled | 37.33% | 0.141 | 35.67% | 0.201 |
| RBF SVM unscaled | 31.42% | 0.181 | 34.92% | 0.201 |

The predeclared criterion required mean BA>50%, mean AUROC>0.5, and mean BA at least5points above the best fixed linear mean within an objective. **Zero of eight nonlinear objective–recipe combinations pass.** The5-point cutoff is an engineering prioritization rule, not a validated biological effect-size threshold.

Time SVM's improvement is real as a descriptive difference but remains **improvement over a below-chance baseline only**. Both original logistic and scaled SVM averaged100% training BA for Time/Behavior, yet generalized poorly. Training separability was therefore not sufficient. We did not reverse predictions or tune validation thresholds. Constant-class prediction would yield50% BA, so the lower values cannot simply mean “always predicts absent.” For example, Time scaled SVM's absent/present recalls are52.67%/22.00%; Behavior's are9.33%/62.00%.

Seed ranges also discourage choosing a favorable checkpoint: Time scaled SVM BA spans4.17–58.33%, Behavior8.33–66.67%. The all-recipe machine tables retain every observed row, seed range, paired baseline delta, class recall, predicted-positive fraction, training gap, log loss and Brier where defined. SVM loss/Brier are absent rather than computed from invented probabilities.

## Matched raw/PCA controls

Means over five assemblies, on the same30 evaluation combinations and22 source trials.

| Readout | Raw BA | Raw AUROC | PCA BA | PCA AUROC |
| --- | ---: | ---: | ---: | ---: |
| Logistic scaled C1 | 48.33% | 0.646 | 42.92% | 0.157 |
| Logistic scaled C0.1 | 48.75% | 0.664 | 37.08% | 0.136 |
| Logistic scaled C0.01 | 49.17% | 0.679 | 34.17% | 0.114 |
| Logistic unscaled C1 | 17.50% | 0.057 | 28.33% | 0.006 |
| Cosine kNN, k5 | 15.42% | 0.083 | 37.08% | 0.315 |
| Cosine kNN, k15 | 20.00% | 0.039 | 36.67% | 0.253 |
| RBF SVM scaled | 45.83% | 0.338 | **77.50%** | **0.829** |
| RBF SVM unscaled | 12.08% | 0.056 | 41.25% | 0.494 |

PCA scaled SVM improves **34.58points** over its matched logistic baseline, with assembly BA58.33–87.50%, absent/present recalls81.67%/73.33%, and a weighted predicted-present fraction45.83%. It is not merely predicting the majority class. Its training BA is100%; that alone says nothing about generalization.

The scaled raw C0.01 model illustrates the distinction between ranking and threshold decisions: AUROC0.679 but BA49.17%, with present recall0%. This does not authorize selecting a new threshold from these validation labels. For calibration context, its mean log loss/Brier are0.7094/0.2595; the archived CEBRA Time baseline is2.6448/0.6296 and Behavior1.6571/0.5014. Fair-coin probabilities would give about0.6931/0.25 under the balanced evaluation measure.

The PCA finding means “nonlinearity helped a matched PCA representation here,” not “a nonlinear decoder rescued frozen CEBRA.” It is worth falsifying under its own frozen controls; the CEBRA-only decision/null family cannot certify it.

## Nulls and source sensitivity

**CEBRA-only null family:** at assembly0/optimizer0, apply all eight recipes to both observed objectives and20 matched source-label-shuffled encoder worlds. Observed family max BA−0.5 was0.0625;16/20 null maxima were at least as large. The inclusive plus-one tail is **17/21 = 0.809524**. This differs from the old study's19/21 because the tested family changed. It is **not** a decoder-superiority test, **not** a p-value for the50-encoder means, and **not** a PCA test. Resolution is1/21; serial exchangeability remains questionable.

**Fixed-model source sensitivity:**200 shared source-resampling worlds, within session×class validation pools, with source multiplicities carried through product rows and each class rebalanced to half the weight. Delete-source checks remove all combinations containing one real source; original removed-weight/count summaries are retained before class rebalancing. No source model was refitted.

| Readout, averaged over its fixed runs | Observed BA | Source-weight2.5–97.5% quantiles | Estimable delete-source BA range |
| --- | ---: | ---: | ---: |
| Time CEBRA scaled SVM | 37.33% | 31.33–42.34% | 34.00–40.67% |
| Behavior CEBRA scaled SVM | 35.67% | 28.99–42.03% | 33.00–38.67% |
| PCA scaled SVM | 77.50% | 55.00–100.00% | 68.33–88.33% |

PCA scaled SVM stayed above chance in199/200 source-weight worlds, but one world reached46.67%. It stayed above chance in all14 estimable source deletions. **Eight of22 deletions were inestimable** because removing a singleton session×class source erased the entire class's product support. They were not scored as successes or silently dropped. Singleton pools also remain constant under source resampling.

These ranges are **empirical pool-weight sensitivities, not confidence intervals** for animals, sessions, unseen trials or selected models. They leave substantial biological/source uncertainty and do not substitute for the missing matched PCA null. The source-reweighted PCA SVM–logistic BA delta had2.5–97.5% quantiles23.33–50.00points; that is likewise descriptive, not a superiority interval/test.

## Accounting, failure and verification

The model-fitting budget was completed once: **350 observed CEBRA-feature readouts +280 null-feature readouts +80 raw/PCA readouts =710 new readout fits**, plus90 archived baseline forwards. There were **zero new biological CEBRA fits** and no reported convergence warnings. Synthetic software-test fits are separate from scientific fit accounting.

Two operational deviations are visible rather than erased:

1. An early implementation audit inadvertently fitted **three training-only PCA transforms** before code approval. No biological decoder/CEBRA fits occurred then. The five planned PCA transforms were later fitted during the gated run: **eight actual PCA fits cumulatively**, not five. No recipe was chosen from the early PCA diagnostics.
2. After all800 model/forward outputs completed, source-sensitivity postprocessing crashed: archived `product_row` IDs restart within each class, but the lineage serializer grouped by row number alone, merging30rows into24. The neural arrays, labels, weights and fitted predictions were separate and unaffected. A regression test reproduced this; the shared helper now keys `(label, product_row)`. Original artifacts and failure receipt remain retained.

The approved recovery copied the failed attempt into a fresh directory, repaired source lineage from hash-checked original manifests, and proved every feature's neural/label/weight hashes unchanged. Model manifest and fit ledger hashes also matched. **All fit APIs were blocked during recovery and verification: zero additional readout, PCA or CEBRA fits.** Fitter and corrected finalizer snapshots/hashes are distinct; the recovery is not an independent replication.

Verification replayed **800 saved models,126,400 predictions,1,600 metric rows,96,000 source-resampling rows,10,560 delete-source rows and five PCA transforms**. Recorded numerical discrepancies were zero. An independent reviewer recomputed validation metrics from prediction rows with maximum difference2.22e−16, confirmed the null/sensitivity calculations and found no remaining findings. **Eight focused tests and111 repository software tests passed.** Primary LSP checks remained inconclusive due to timeouts; heuristic uncaught-conversion warnings are not represented as a clean static-analysis pass. AI review is QA, not lab metadata verification or scientific peer review.

## What to do next — not executed

Prefer the simpler lead over escalating decoder complexity on these frozen CEBRA features: freeze **PCA + scaled RBF SVM** against its matched linear/raw controls, add source-coherent matched nulls and nuisance/history checks, then test genuinely new source pools if available. Do not tune against these22 sources or interpret their repeated reuse as confirmation. This report does not authorize that next experiment.

Condition-level pseudopopulations remain a valid research lane; this result does not require abandoning them or obtaining a large simultaneous195 recording first. Exact trial-specific population/intention claims still require simultaneous trial-linked activity. H1b geometry and H2 artificial-agent comparisons were not tested here.

## Artifacts and continuation

Accepted local authority (ignored lab artifacts, not portable through Git alone):

`outputs/cebra-decoder-autoresearch-20260924/recovery-20260924T042259Z/`

- `verify_receipt.json`, `recovery_completion.json`, `lineage_repair_receipt.json` and `source_snapshots/` establish replay/provenance.
- `readout_metrics.csv`, `readout_predictions.csv`, `fit_ledger.csv`, `pca_fit_ledger.csv`, `null_family_tails.json`, `source_bootstrap_worlds.json`, `source_bootstrap_metrics.csv`, `delete_source_influence.csv` retain all recipes, nulls and source diagnostics.
- `report/all_observed_recipe_means.csv`, `report/review_tables.json`, `report/machine_summary.json` and `report/summary.html` are verified numerical outputs. The companion offline HTML above provides the human summary and all32 observed recipe summaries without external assets.
- Failed fitting attempt: `../run-20260924T040037Z/`; `FAILURE.json` overrides its stale `run_config` status. It is excluded as a separate result. Early deviation: `../audit-implementation-check-20260924T000000Z/SEQUENCING_DEVIATION.md`.
- Journal, logs and no-fit recovery/table scripts: `../management/`. Numerical review: `.pi-subagents/artifacts/outputs/c8878d9b-9d04-402a-825b-a0174173912f/work/cebra-decoder-autoresearch-20260924/numerical-results-review.md`. Prefit/recovery review run IDs: `0ff8fbc7`, `3f69da2a`; final numerical review `539f8e59`. Fresh-context final claim/HTML review `338114d4-9bd1-4c54-8c90-819d28f523d3` approved with the limitations above; receipt at `.pi-subagents/artifacts/outputs/338114d4-9bd1-4c54-8c90-819d28f523d3/work/cebra-decoder-autoresearch-20260924/final-claim-review.md`.

No branch switch, install, commit/push, raw/test import, lab-server access, persistent service or biological encoder training was introduced. Existing workspace/atlas changes were preserved. Retain failed attempts as provenance; do not rerun fitting to regenerate reports. The accepted source tensor SHA256 remains `688e3b52f69a872c7aec420da99ebb6f0b80464351ded3813b077cd7ed3cf567`.
