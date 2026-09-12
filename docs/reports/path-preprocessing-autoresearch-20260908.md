# What preprocessing could—and could not—fix in path decoding

2026-09-08 · **Completed exploratory methods research** · 82,283 numerical model replays verified; zero verification fits.

[Readable frozen methods](path-preprocessing-prefit-20260908.md) · [Offline illustrated report](path-preprocessing-autoresearch-20260908.html)

> **Bottom line:** stronger regularization improved probability loss relative to the other tested recipes, but did **not establish reliable broad path decoding**. The selected historical diagnostic had Δlogloss **+0.0286**, balanced accuracy **55%**, and only **2/5** positive endpoint panels. P-values across the four declared null comparisons were **0.139–0.356**, and source-resampling quantiles crossed zero. The small aggregate was dominated by **6→1**. This is neither proof of planning nor evidence that H1 is false.

## 1. What question did we actually ask?

The thesis question is whether cue activity contains information about the subsequently observed **path beyond start and goal**. Here we tested a narrower operational version: within a fixed start–goal pair, do independently held-out source responses distinguish whether a particular directed interior path component will later occur?

The component is central-middle→central-bottom, `D_N_C_M__N_C_B`. “Interior” means **all corridor runs after removing first and last**, not one middle instant. This is a binary feature of an ordered path, not reconstruction of that whole path. The target had already been selected from training behavior/support; we did not search for a different path label after neural results.

Three objects must remain separate:

| Object | What it is | What it is not |
|---|---|---|
| Measurement | Sorted-unit spike events/counts in the export's operational cue window | A direct observation of a thought, plan, or latent brain state |
| Derived target | Later behavioral presence/absence of the fixed interior component | The old `(start,goal)` “trajectory class,” or the complete path |
| Model input | A condition-matched pseudopopulation assembled from session-specific source blocks | One natural, verified simultaneous49-unit trial |

**ML bridge:** imagine drawing feature blocks from different records with the same known class, then concatenating them. Split the original records first, not the synthetic concatenations. This can test whether class-conditional response differences reproduce across source pools. Because evaluation labels help assemble the vectors, it is **not an operational decoder of an unknown-label natural trial**.

```text
Original source trials ── frozen train / historical-validation split
          │
          ├─ training sources: three inner source-held-out folds
          │       └─ matched block assemblies → fit preprocessing + decoder
          │
          └─ historical-validation sources: untouched by the new CV selection
                  └─ separate known-label block assemblies → diagnostic
```

Same-source cells and time bins stay together. Cross-session covariance is not recovered. Source identity separation also does not guarantee independence from nearby trials or changing session state. Known-label assembly defines the conditional question; it is not hidden sharing of training source trials with validation. It nevertheless changes the evaluation object from a natural trial.

Previous endpoint-class decoding answers a different question. Nor is a numerical comparison with the earlier path study a clean preprocessing ablation: its source panels and eligibility differed. The matched comparisons below are **within this frozen study**.

## 2. How much biological support was there?

**147 training + 41 historical-validation sources; 49 unique unit IDs; 13 sessions.** These are a subset of the selected195 archive—not a simultaneous195 recording. There are756 observed unit–source pairs; unrecorded cells remain masked/NaN, never zero-filled.

| Start→goal | Sessions | Unit IDs | Training sources | Historical-validation sources |
|---|---:|---:|---:|---:|
| 2→1* | 1 | 2 | 12 | 3 |
| 3→1 | 3 | 14 | 31 | 11 |
| 4→1* | 1 | 3 | 9 | 2 |
| 5→1 | 3 | 12 | 33 | 8 |
| 6→1 | 6 | 23 | 62 | 17 |

Units/sessions overlap across panels; do not sum those columns as independent subjects. Asterisks denote **point/influence-only** panels. Even the larger panels contain some single-source validation session×class pools.

Eligibility was frozen using behavior, recorded QC, duration, and **existing validation class support**, not neural success. This is openly development-conditioned panel selection, not strictly training-only cohort discovery. Two sources with cues shorter than1s explain the earlier149→147 training count change.

We exported ten half-open100ms bins covering exactly **the first `[0,1)` seconds**, not every variable-duration cue count. Tail counts were saved and conservation checked. The guarded accessor streamed files containing skipped original-test rows but yielded zero forbidden rows. No new original-test evaluation occurred.

Synthetic training has128 rows/class per model. Exact validation products remove assembly-sampling noise for these small panels, but neither128 nor the number of Cartesian combinations is biological sample size. Previously exposed validation does not become pristine confirmation because this new CV loop withheld its predictive outcomes.

## 3. The research trajectory: hypotheses, not an unlimited leaderboard

We froze the target, sources, folds, window and comparison family before fitting. Separate models hold each endpoint pair fixed; scores average endpoints equally. The balanced conditional benchmark's baseline is constant probability0.5.

**Primary score:** `Δlogloss = log(2) − balanced logloss` (nats). Positive means better probability predictions than that constant baseline. Balanced accuracy, Brier score and AUROC are secondary. These are scores under the constructed conditional distribution, not natural-prevalence calibration of ordinary trials.

| Hypothesis | Matched intervention | What the comparison can teach |
|---|---|---|
| Fine time detail may cost too much estimation capacity | 1,2,5 bins across the same first second | Pooling versus temporal detail at this source budget |
| Sparse counts may benefit from compression | Raw rate, square root, log1p | Geometry accessible to this regularized linear readout |
| Tiny feature SDs may cause unstable effective weighting | Standard z-score versus a training variance floor | A featurewise regularization choice |

Pooling is over **time within each unit**, not across neurons. The one-bin6→1 model still has23 inputs; its five-bin counterpart has115. One time bin is not a one-dimensional population or an estimate of brain dimensionality.

Round 1 crossed these factors: 18 candidates, all with average-loss L2 λ=0.1. After an independent checkpoint, the predeclared Round 2 added **only λ=0.01 and 1 for the CV-winning representation**. Selection then froze among 20 candidates. No PCA, residualization, CEBRA, new target, or posthoc label inversion was added.

<!-- figure:family -->

### Hypothesis update A: more bins fitted training better, not CV

| Representation, λ=0.1 | Training logloss | Source-held-out CV logloss | CV Δlogloss |
|---|---:|---:|---:|
| 1s raw rate, standard scaling | 0.2728 | 0.7058 | −0.0126 |
| 1s raw rate, variance floor | 0.2896 | 0.6193 | +0.0739 |
| Five bins, raw rate, standard scaling | 0.0947 | 1.1431 | −0.4500 |

The richer model learned its training assemblies very well and generalized worse. That is compatible with a finite-source estimation problem; **it does not prove that the brain lacks temporal coding**. Raw fine-bin features can represent their pooled average, but estimating separate weights changes capacity and the effective regularization problem. We did not isolate biological time coding from that tradeoff.

Square root and log1p are invertible on nonnegative rates: worse linear decoding after those transforms does not mean they destroyed Shannon information. They change which relationships are easy for a regularized linear model. Likewise, the variance floor is a numerical prior, not a verified hippocampal noise model or proof of Poisson spikes.

### Hypothesis update B: the most accurate model was not the best probability model

Round 1's winner was the first-second raw rate (spikes/s) with variance-floor scaling. The deliberately bounded L2 refinement gave:

| L2 λ | CV balanced accuracy | CV Δlogloss | Decision |
|---:|---:|---:|---|
| 0.01 | 68.73% | −0.2700 | Reject by the declared primary score |
| 0.1 | 66.37% | +0.0739 | Round1 winner |
| **1** | **63.74%** | **+0.0926** | **Frozen final selection** |

<!-- figure:regularization -->

A classifier can get more labels right while making its mistakes more costly through excessive confidence. For intuition only:70% accuracy with99%-confident predictions gives about1.389nats logloss;60% accuracy with60%-confident predictions gives about0.673. The latter beats the0.693 constant baseline despite lower accuracy. These are illustrative numbers, not experimental observations.

Our actual result is an improvement in probability loss, not a separately demonstrated calibration curve. L2 can change the decision boundary as well as confidence; we did not fit a calibration model on historical validation. The fitted objective uses average loss plus `(λ/2)||β||²`, implemented with sklearn `C=1/(λ*N_training_rows)`. Repeating synthetic rows therefore cannot silently weaken regularization. The regression check tests this invariance.

## 4. Did that improvement transfer to held-out source responses?

There was a clear **numerical improvement relative to the other tested recipes**, but weak and uneven performance relative to the constant baseline. For the same raw/floor features, stronger λ=1 reduced historical logloss from0.8473 (λ=0.1) to0.6646. It was the only declared candidate with positive historical Δ; that is a point comparison, not a separately tested biological effect.

The frozen recipe's mean **Δlogloss is+0.02858**, versus+0.09261 in CV; mean **balanced accuracy is55%**.

| Endpoint | Selected CV Δ | Historical-validation Δ | Historical BA |
|---|---:|---:|---:|
| 2→1* | −0.0018 | −0.0015 | 50% |
| 3→1 | +0.1386 | −0.0825 | 25% |
| 4→1* | +0.0062 | +0.0499 | 50% |
| 5→1 | +0.0174 | −0.1174 | 50% |
| 6→1 | +0.3027 | +0.2944 | 100% |

<!-- figure:endpoints -->

**Only 2/5 endpoint deltas are positive. Remove 6→1 and the remaining equal-endpoint average is−0.03787.** Its 100% BA is a result on small, label-conditioned combinations—not100% prediction of17 natural simultaneous trials. It is a useful follow-up lead, not a posthoc replacement for the frozen five-panel estimand.

The predeclared “improvement” rail required positive loss improvement, consistent direction across most endpoints, and performance above the coherent selection null. Broad consistency already fails here. Even favorable null results could not turn this into consistent coding across the endpoint panels.

## 5. What do the controls say?

All planned controls completed. The full zero-fit verifier independently recomputed the statistics below from saved predictions and replayed the models.

| Null/reference policy | Inclusive exceedances | Plus-one p-value |
|---|---:|---:|
| Ordinary: null's CV-selected recipe | 16/100 | 17/101 = **0.168** |
| Ordinary: null's maximum validation score across its family | 35/100 | 36/101 = **0.356** |
| Temporal-half: null's CV-selected recipe | 13/100 | 14/101 = **0.139** |
| Temporal-half: null's maximum validation score across its family | 29/100 | 30/101 = **0.297** |

The observed statistic is the same frozen CV-selected model in every comparison. The maximum-family reference is deliberately conservative. Neither policy supplies convincing separation from its declared null; do not select whichever p-value looks better.

The 200 fixed-recipe source bootstraps gave empirical **2.5th/50th/97.5th percentiles of −0.08751 / +0.01538 / +0.10061**. This source-resampling sensitivity spans zero; it is **not an inferential confidence interval** or an absence test.

<!-- figure:nulls -->

The two null types each contain100 complete source-label permutation worlds. Every world repeats its **own18-arm CV search and its own L2 refinement**, rather than borrowing the observed winner. Both the null-CV-selected and null-max-family validation references are compared against the **observed CV-selected** statistic. Both policies are reported; we cannot choose the favorable one. Inclusive `>=` plus-one p-values retain ties and finite Monte Carlo resolution.

**What could actually move under the temporal null?** Ordinary strata were all mixed-label (56/56); temporal conditioning produced **52 pure-label strata out of101**, containing64/188 sources. Those64 labels cannot change under this conditional null. The median fraction of individual source labels actually changed was44.7% in ordinary worlds and31.4% in temporal-half worlds (ranges36.2–55.3% and20.2–39.4%). This is not proof of serial exchangeability. The producer's field named `movable_fraction` counts records in strata with *any realized change*, not individual changed labels; the numbers here were recomputed from label maps.

**How degenerate are the validation pools?** **17/28 session×endpoint×class pools contain one source**:1/2 pools for2→1,3/6 for3→1,2/2 for4→1,4/6 for5→1 and7/12 for6→1. Resampling a singleton cannot expose uncertainty about additional, unobserved trials.

Other diagnostics show:

- **Assembly seeds1/2:** fixed-recipe validation Δ+0.01808/+0.02071. The small positive aggregate does not depend on one training-assembly draw. This is Monte Carlo sensitivity, not biological replication, and cannot reselect the model.
- **Nuisance-only trial index/full-cue duration:** CV Δ−0.34866; historical Δ−0.35606. This fixed-λ0.1 linear control did not decode reliably as implemented. It is neither an optimized nuisance benchmark nor a nested neural-plus-nuisance conditional test. It cannot rule out nonlinear time, cue, gaze, heading, history or state confounds.
- **Source bootstrap:** 200 fixed-recipe refits, not recipe reselection. Empirical quantiles measure source-resampling sensitivity only; one-source pools cannot reveal missing variance. They are not animal-level or selection-adjusted confidence intervals.
- **Influence:** 12/13 session-removal refit aggregates remained positive, but values ranged from−0.00393 to+0.07417. Removing the shared20180814 session changed the common-panel aggregate by−0.03251 and crossed zero. These overlapping refits are not13 independent replications. Dropping a tiny panel's only session drops that endpoint; comparisons correctly use common remaining panels. Endpoint omission still shows that6→1 drives the overall point advantage.

Under the reported task rule, current start equals previous goal. Fixing the endpoint pair therefore also fixes previous-goal identity; that identity alone cannot explain within-pair differences. Other history variables can still vary. A weak nuisance score does not establish abstract planning.

## 6. What changed in our understanding?

**Observed:** coarse raw features with stronger regularization predicted CV probabilities better than the tested finer-bin, compressed, or weakly regularized alternatives. Historical transfer was smaller and heterogeneous.

**Interpretation:** preprocessing/readout choices mattered for estimation stability in this assay. They did not create new biological observations, recover simultaneity, remove all confounds, or restore an untouched holdout. The positive aggregate point is6→1-dominated.

**Not established:** broad prospective-path decoding, full-path reconstruction, intention, causal planning, absence of path information, or a unique reason for prior CEBRA failures. H1b low-dimensional organization and H2 artificial-agent comparisons were not tested. No individually significant-neuron gate is implied by this result.

A weak result from this20-arm linear family does not show that every possible decoder would fail. Conversely, an attractive embedding or more synthetic training rows would not by itself repair the source/generalization problem.

## 7. What should happen next—not automatically executed

| Remaining uncertainty | Small discriminating next step | What not to do |
|---|---|---|
| Is6→1's pattern reproducible beyond these pools? | Freeze that now-performance-motivated follow-up and test genuinely new source sets, with declared comparison contexts | Rebrand the current6→1 subset as a pristine positive finding |
| Do admissible cue/history variables explain it? | Verify task events/recording groups and pre-cue covariates; compare nuisance versus nuisance+neural models with matched training-only tuning | Treat this weak fixed nuisance baseline as confound exclusion |
| Could this design detect a worthwhile signal? | Agree an effect threshold, then run explicit source-aware sensitivity simulations under stated noise assumptions | Conclude absence, or assume “more data fixes it” |
| Is a richer representation scientifically justified? | Write a separate selection-safe question and validation plan before adding it | Continue tuning this historical diagnostic until something wins |

The simpler working baseline is first-second raw rate, variance-floor scaling and a strongly regularized logistic readout. It is a baseline to carry forward, not a discovered biological law. More machinery needs a new discriminating question.

## 8. Reproducibility, mistakes and review status

This work used an isolated branch/worktree, existing CPU runtime with thread caps2, and no dependency installation, GPU training, commits, pushes, raw transfers or service changes. Scientific/code gates preceded biological stages; independent review is AI-assisted, not human peer review.

Engineering failures are retained, not narrated as rejected neuroscience hypotheses:

1. A direct-script import issue and prototype assertions were fixed in synthetic development.
2. An implementation worker timed out; parent completed the missing gates/controls and obtained fresh independent reviews before execution.
3. The first final-stage attempt was killed by the background runner's20MB console cap after12850 durable fit records and29 complete ordinary worlds. It has no accepted final summary. The incomplete next world's267 recorded fits lack a completed original coefficient package; any further in-flight fit is unknown.
4. The unchanged deterministic protocol was restarted into a fresh directory with file-routed logs. Observed, nuisance and seed-sensitivity predictions matched the first attempt exactly after decompression. Repeated fits/seeds are not replication or extra null worlds.
5. Independent verification review caught gaps in bootstrap quantiles, secondary metrics and saved lineage checks. The verifier was strengthened without changing the scientific fitter. A synthetic extreme-probability check caught and fixed its clipping-convention mismatch; corrupt-metric/lineage/resample tests now reject those defects.

**Recorded completion:** 300 original CV fits plus81,983 accepted-final-stage fits = **82,283 fit instances**. Another12,850 durable fit records belong to the interrupted duplicate attempt: **95,133 recorded biological fits across attempts**, not95,133 biological observations. Of the 81,983 final fits, 80,000 implement the two 100-world null families. There were 20 observed-data candidates; each null repeats its own adaptive 20-candidate search. The accepted final stage took 52m22s wall time and recorded 2–18 solver iterations, with no recorded `converged=false` flags. Full forward verification passed: **82,283 models replayed, zero new fits**, including training/evaluation metrics, regenerated source lineage, adaptive null selection, bootstrap seed/strata/hash/quantiles, nuisance features and seed/influence summaries. The focused test command passed **19 tests across three files** (13 in the new study's test file plus six existing split/bin checks).

The original300 CV model replays and original fit-code snapshots were copied into the final package without refitting. The independent verifier performs numerical forward passes and recomputes metrics, selection, null comparisons, source lineage and resampling; successful script exit alone is not the acceptance standard.

Local reproduction uses the data-equipped worktree `/home/hongyi-home-lab/neuro_science-path-autoresearch-20260908`:

- Analysis: `scripts/place195_path_preprocessing_autoresearch.py`.
- Verifier: `scripts/verify_path_preprocessing_results.py`.
- Tests: `scripts/test_place195_path_preprocessing_autoresearch.py` plus split/bin tests.
- Rendering: `scripts/build_path_preprocessing_report.py`.
- Accepted run: `outputs/path-preprocessing-autoresearch-20260908/biological-20260908T115508Z/final-20260908T133200Z/`.
- Numerical receipt: that run's parent directory, `verification-final.json`; descriptive count/mobility receipt: `descriptive-audit.json`.
- Frozen protocol, decisions, failure history and evaluator receipts: sibling ROOT `outputs/path-autoresearch-management-20260908/`.

The Markdown's tables are readable independently of local data. The HTML embeds its figures/styles for offline reading; raw sources and detailed model artifacts remain local/ignored and are not a Git backup.

## All declared candidates

All scores below are equal-endpoint point summaries, not independent-source confidence intervals. The bold row was selected by CV, not by this historical table. Higher historical accuracy in several five-bin arms did not translate into better probability loss.

| Bins / transform / scaling / λ | CV Δ | Historical Δ | Historical BA |
|---|---:|---:|---:|
| 1 / raw / standard / 0.1 | −0.01260 | −0.19697 | 50.00% |
| 1 / raw / floor / 0.01 | −0.27004 | −0.81385 | 51.25% |
| 1 / raw / floor / 0.1 | +0.07386 | −0.15418 | 50.00% |
| **1 / raw / floor / 1** | **+0.09261** | **+0.02858** | **55.00%** |
| 1 / sqrt / standard / 0.1 | −0.12654 | −0.16958 | 55.00% |
| 1 / sqrt / floor / 0.1 | −0.02144 | −0.15422 | 55.00% |
| 1 / log1p / standard / 0.1 | −0.22224 | −0.15875 | 55.00% |
| 1 / log1p / floor / 0.1 | −0.07021 | −0.18342 | 55.00% |
| 2 / raw / standard / 0.1 | −0.23000 | −0.12301 | 55.00% |
| 2 / raw / floor / 0.1 | −0.07534 | −0.01380 | 55.00% |
| 2 / sqrt / standard / 0.1 | −0.29415 | −0.15348 | 50.00% |
| 2 / sqrt / floor / 0.1 | −0.19811 | −0.10791 | 50.00% |
| 2 / log1p / standard / 0.1 | −0.40545 | −0.20582 | 42.50% |
| 2 / log1p / floor / 0.1 | −0.29860 | −0.19308 | 45.00% |
| 5 / raw / standard / 0.1 | −0.45000 | −0.58367 | 58.75% |
| 5 / raw / floor / 0.1 | −0.39683 | −0.44363 | 60.00% |
| 5 / sqrt / standard / 0.1 | −0.35256 | −0.30882 | 60.00% |
| 5 / sqrt / floor / 0.1 | −0.29476 | −0.28582 | 62.50% |
| 5 / log1p / standard / 0.1 | −0.38214 | −0.22902 | 60.00% |
| 5 / log1p / floor / 0.1 | −0.28777 | −0.24919 | 62.50% |

## Reading context: motivation, not validation of this recipe

These primary references motivate count-noise or prospective/retrospective questions. This study's methods memo verified their bibliographic/abstract scope, not full-text claims about an optimal preprocessing method.

1. Anscombe (1948), count transforms: [doi:10.2307/2332343](https://doi.org/10.2307/2332343).
2. Tolhurst, Movshon & Dean (1983), neural response variability: [doi:10.1016/0042-6989(83)90200-6](https://doi.org/10.1016/0042-6989(83)90200-6).
3. Frank, Brown & Wilson (2000), trajectory coding: [doi:10.1016/S0896-6273(00)00018-0](https://doi.org/10.1016/S0896-6273(00)00018-0).
4. Ferbinteanu & Shapiro (2003), prospective/retrospective coding: [doi:10.1016/S0896-6273(03)00752-9](https://doi.org/10.1016/S0896-6273(03)00752-9).
5. Johnson & Redish (2007), fast forward-path representations: [doi:10.1523/JNEUROSCI.3761-07.2007](https://doi.org/10.1523/JNEUROSCI.3761-07.2007). Their neural sweeps are not reproduced by cross-session first-second rate assemblies.
