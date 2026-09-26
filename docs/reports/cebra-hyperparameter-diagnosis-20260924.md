# What is failing in our CEBRA pipeline? Hyperparameter diagnosis

**September24,2026 · Completed, forward-verified exploratory research.**
[Offline illustrated HTML](cebra-hyperparameter-diagnosis-20260924.html) · [Frozen protocol](cebra-hyperparameter-prefit-20260924.md) · [Earlier decoder comparison](cebra-decoder-autoresearch-20260924.md)

## Direct answer

**Excessive decoder regularization is not supported as the main explanation for the failure of these frozen CEBRA features.** Weakening it did not recover held-out-source performance. A wider RBF-kernel search did not produce above-chance mean CEBRA decoding either.

The clearest failure mode is **source-pool transfer**: the models separate their training assemblies extremely well, but the learned relationships do not work on the different historical-validation sources. That is an observed property of this pipeline, **not a uniquely identified causal fault in CEBRA**. We did not manipulate the encoder objective, temporal architecture, nuisance structure or biological source support.

**It is not established that future-path tasks are inherently unsuitable for CEBRA.** A future behavioral label can legitimately supervise an encoder of earlier cue activity; it is not supplied at inference. What must exist is a stable cue–path association that the encoder preserves and that transfers to new sources. This particular configuration has not demonstrated that transfer.

A meaningful diagnosis is therefore possible, but it is narrower than “CEBRA is broken” or “the latent space contains no information.”

## 1. The intervention, not another open-ended search

We kept the observed neural arrays, labels, source splits, scalers/PCA representations and50CEBRA encoders fixed. Target: interior **D_N_R_T__N_R_M**, within endpoint **4→3**, first-second cue counts. The assay has29selected unit IDs across7sessions,82training sources and22historical-validation sources. The30 evaluation combinations are condition-matched cross-session pseudopopulations, not30 independent or simultaneous natural trials.

The frozen comparison was:

- Scaled logistic C=`0.001,0.01,0.1,1,10,100`:100,000-fold range, from strongest to weakest penalty.
- Scaled RBF SVM C=`0.1,1,10` × gamma=`0.1,1,10` times its training-derived `gamma='scale'` value. Larger gamma makes the kernel narrower/more local.
- Confidence-only temperatures T=`1,2,5,10` on the old C1 logistic margins: **no fitting and no changed decision boundary or ranking**.
- Raw/PCA comparisons on the same assemblies; source-coherent raw/PCA shuffled controls that were missing from the earlier experiment.
- All existing readout context retained. No threshold tuning, sign flipping, MLP, validation-selected deployment winner, new source split or observed-encoder retraining.

Observed CEBRA means average25assembly/optimizer settings per objective; raw/PCA means average five assemblies. These are computational sensitivities, not25 or five independent biological replications. The September8 five-endpoint/49-unit study with a55% baseline is a **different target/cohort** and was not rerun. “Best” here always names the metric and this fixed comparison family.

## 2. Is regularization squishing out the useful data?

**L2 shrinks decoder weights, not the stored neural data or frozen embeddings.** The practical question is whether weakening that shrinkage restores useful discrimination on different sources.

### CEBRA-Time: weakening the penalty made transfer worse

| Logistic C | Training BA | Development BA | Development AUROC | Development log loss ↓ |
| --- | ---: | ---: | ---: | ---: |
| 0.001 — strongest | 97.63% | 30.92% | 0.189 | 0.781 |
| 0.01 | 98.84% | 28.83% | 0.159 | 1.061 |
| 0.1 | 99.84% | 26.50% | 0.122 | 1.662 |
| 1 — original | 100.00% | 24.92% | 0.111 | 2.645 |
| 10 | 100.00% | 24.50% | 0.111 | 3.905 |
| 100 — weakest | 100.00% | 24.25% | 0.107 | 5.330 |

The mean coefficient L2 norm rose from0.165 to4.156 across those endpoints; held-out probability spread rose from0.056 to0.359. This produced **larger, more confident errors**, not a recovered path decoder. Norms are interpreted within this representation/scaling convention, not across arbitrary embedding geometries.

### CEBRA-Behavior: the same qualitative problem

Training BA stayed100% for every logistic C. Development BA stayed between34.67% and35.75%, and AUROC between0.206 and0.211. Log loss worsened from0.813 at C0.001 to2.413 at C100. These are not signs that the decoder simply lacked enough training iterations to fit the training examples; no convergence warnings were reported.

There is a genuine trade-off elsewhere: PCA/logistic development BA rises from31.67% at C0.001 to46.25% at C10/100, while probability loss becomes worse. That confirms that regularization can suppress discrimination in a particular pipeline. It **does not rescue CEBRA** and still leaves PCA's tested linear decoders below50% BA.

For raw features, C0.001 gives49.17% BA,0.699 AUROC and0.6816 log loss, slightly better loss than the balanced constant0.5 baseline of0.6931. Its low BA reflects its operating point/class predictions, not an absence of score ranking. This remains a small descriptive result on exposed sources.

<!-- figure:regularization_ba -->

## 3. Why “better log loss” can be misleading about discrimination

We divided existing logistic margins by T before applying the sigmoid. No coefficients, encoders, labels or thresholds changed. Positive T preserved every model's BA and score-based AUROC.

| Representation | Log loss T1 | Log loss T10 | BA unchanged | AUROC unchanged |
| --- | ---: | ---: | ---: | ---: |
| CEBRA-Time | 2.6448 | 0.8110 | 24.92% | 0.111 |
| CEBRA-Behavior | 1.6571 | 0.7478 | 35.17% | 0.206 |
| Raw | 0.9570 | 0.6885 | 48.33% | 0.646 |
| PCA | 1.9909 | 0.7724 | 42.92% | 0.157 |

**Your concern about the word “best” was justified.** Large probability-loss gains can come from making errors less confident, with no improved classification or ranking. This is not a fitted calibration study and no T was selected for deployment. The CEBRA losses remain worse than the constant baseline even at T10.

This diagnostic does not prove that all improvements from L2 are confidence-only: changing L2 can also change the boundary, as the BA/AUROC curves show. It isolates one mechanism that can improve the reported loss without extracting additional discriminative information.

<!-- figure:confidence_vs_discrimination -->

## 4. Does a more appropriate kernel boundary rescue the embeddings?

Nine scaled-SVM settings per feature set varied penalty and bandwidth independently.

| Representation | Original center BA/AUROC | Largest mean BA in grid | Interpretation |
| --- | ---: | ---: | --- |
| CEBRA-Time | 37.33% /0.141 | 50.00%, AUROC≈0.286 | Chance-level decision performance, not rescue |
| CEBRA-Behavior | 35.67% /0.201 | 49.83%, AUROC0.211 | Still nonpositive |
| Raw | 45.83% /0.338 | 50.00%, AUROC0.068 | A chance-level decision rule is not useful ranking |
| PCA | 77.50% /0.829 | 77.50%, AUROC0.829–0.833 | Stronger descriptive control, not established biology |

**No CEBRA nonlinear setting meets the frozen follow-up criterion:** mean BA>50%, mean AUROC>0.5 and a5-point advantage over the tested linear envelope. Neither does raw. Three PCA-SVM grid cells meet that descriptive rule (C0.1/1/10 at the original gamma), but that is not an independent winner validation or biological effect-size criterion.

An informative counterexample appears at PCA's10×gamma: **AUROC1.0 but BA50%**, with all validation examples predicted present. Ranking, the learned zero-margin decision threshold, and confidence are different properties. We did **not** fix this by selecting a threshold on validation labels. Perfect ranking on these small constructed source pools is not proof of generalizable prospective coding, and the declared null tests below concern BA, not this AUROC result.

For CEBRA, the ranking scores themselves remain nonpositive across the tested grid, so the failure is not explained merely by a slightly inconvenient decision threshold. Below-chance rankings can reflect reversed source relationships; they are not proof that the features contain zero information, nor permission to invert predictions after seeing validation labels.

<!-- figure:svm_grid_ba -->

## 5. What the new matched nulls say about the PCA lead

For each of20source-label-shuffled worlds, we reconstructed raw arrays from the exact audited null manifests and fitted PCA **only on that world's training assembly**. The observed PCA transforms were unchanged. Time/Behavior share the same source maps/assemblies within each null world. A decoder-only label shuffle or reuse of the observed PCA basis would not have repeated the full label-conditioned construction.

| Predeclared maximum-over-family reference | Observed maximum BA at anchor | Inclusive exceedances | Plus-one tail |
| --- | ---: | ---: | ---: |
| CEBRA:2objectives ×19readouts | 56.25% | 17/20 | **18/21 =0.8571** |
| Raw/PCA:2representations ×15grid settings | 58.33% | 14/20 | **15/21 =0.7143** |
| Joint68settings | 58.33% | 18/20 | **19/21 =0.9048** |

These references use **CEBRA A0/O0 and raw/PCA assembly0**, not the means over25/five runs. For the fixed PCA center SVM, the anchor BA is58.33% and its descriptive fixed-recipe tail is7/21=0.3333.

Thus the new anchored null checks **do not establish the PCA lead as robust signal**. They also **do not directly test or reject its77.5% five-assembly mean**, because that is a different statistic. No superiority p-value, five-seed-mean p-value or AUROC1.0 p-value is supplied. Historical adaptive exposure is not corrected by this family test;20worlds give only1/21 resolution and questionable serial exchangeability remains.

The correct update is: the PCA lead persists descriptively, but the added null context does not justify promoting it into an established positive control or H1 discovery.

## 6. Source sensitivity and what “transfer failure” means

We reused the exact200source-reweighting worlds and22deletions from the earlier study. Every model remained fixed; shared sources carried their weights through every combination. These are **pool-weight sensitivities, not biological confidence intervals**.

| Fixed readout, mean across its computational runs | BA | Source-weight2.5–97.5% quantiles | Estimable deletion range |
| --- | ---: | ---: | ---: |
| Time logistic C0.001 | 30.92% | 25.66–36.00% | 28.33–33.50% |
| Time SVM C0.1, original gamma | 39.83% | 36.15–45.00% | 38.17–41.50% |
| Behavior SVM C0.1,10×gamma | 49.83% | 49.33–50.00% | 49.67–50.00% |
| PCA center SVM | 77.50% | 55.00–100.00% | 68.33–88.33% |

Eight of22deletions are inestimable because a singleton session×class source supplies all of one class's product support. Fourteen deletions are estimable. Singleton pools also cannot reveal unseen source variability under resampling.

We additionally compared the **class-mean difference vector** in training versus validation, using each representation's saved C1 training scaler:

| Representation | Mean cosine of training/development class contrasts | Negative directions |
| --- | ---: | ---: |
| CEBRA-Time | −0.124 | 22/25 |
| CEBRA-Behavior | −0.196 | 23/25 |
| Raw | +0.017 | 0/5 |
| PCA | −0.081 | 5/5 |

This is compatible with a mapping that depends strongly on the source pool. It is not a causal mechanism or an independence test. The seeds share the same22validation sources;22/25 is **not** a binomial significance calculation. Importantly, **PCA also has reversed mean contrasts despite its nonlinear ranking/decoding lead**. A first-moment diagnostic cannot rule out nonlinear information. Cosines in differently scaled representations are not direct mutual-information comparisons.

## 7. What exactly did these CEBRA encoders learn?

Read-only inspection found no clear silent encoder implementation bug. The inspected frozen driver and saved configuration specify:

- Raw29-cell cue counts, standardized using training data only; no PCA before CEBRA.
- An `offset1-model`: one100ms bin as input,29→32→32→16→8, L2-normalized output. The decoder concatenates ten bin embeddings into80features.
- CEBRA-Time positives: next bin in the **same pseudotrial**, with boundary checks; global random negative bins. This was not accidental chaining across trial boundaries.
- CEBRA-Behavior: the binary path-component label repeated across cue bins, with the discrete empirical-prior loader.
- Fixed-cosine InfoNCE temperature1, Adam learning rate3e−4, batch256 and1000updates in the reused crossed-seed family.

The original paper's hippocampus benchmark decoded current position/direction and used temporal receptive fields rather than this single-bin encoding. That makes objective/temporal-design mismatch plausible, **not proven**. Binary/future labels do not make CEBRA intrinsically invalid. We have not compared a differently trained temporal encoder, nor established the latent identifiability assumptions for this sparse task.

Evidence: `outputs/path-generalization-20260907/frozen/driver.py` (encoder fitting around2685–2912), saved fit metadata and current helper `scripts/place195_v8b_v9_cebra.py` (`TrialCueDataset`, boundary-aware loader). The historical driver hash is recorded; helper behavior was inspected in the current checkout, not established by mistaking its hash for the driver's hash. We did not reload neural checkpoints in this diagnostic. See the [earlier paper/method comparison](cebra-nonlinear-readout-research-20260923.md).

## 8. Diagnosis: supported, weakened, unresolved

| Explanation | What this experiment supports |
| --- | --- |
| “Heavy decoder regularization caused CEBRA to lose the signal” | **Not supported as the main explanation in this range.** Weaker penalties did not rescue CEBRA and often worsened transfer. |
| “The decoder was not trained / needed more iterations” | **Not supported.** Training separation was near-perfect, fitting completed, and no convergence warnings were reported. This does not prove optimal regularization. |
| “Our loss winner partly reflects reduced confidence” | **Supported.** Temperature alone substantially improves loss without changing discrimination. |
| “The old SVM bandwidth was the only problem” | **Not supported by the grid.** CEBRA reaches at most chance mean BA with poor mean AUROC. |
| “The learned relation is not stable across the source pools” | **Observed failure mode.** Training/development gaps and contrast reversals are consistent with it; their biological cause is unresolved. |
| “CEBRA discarded all relevant information” | **Not established.** Failed finite readouts and low AUROC cannot prove zero information. |
| “PCA solves the biological task” | **Not established.** Descriptive scores are stronger, but the anchored null checks do not establish robust support; no pristine evaluation exists here. |
| “Prospective-path encoding is inherently unsuitable for CEBRA” | **Not established.** The encoder/task/data alternatives were not experimentally isolated. |

**Practical conclusion:** do not spend the next budget merely widening decoder C/gamma on these same frozen embeddings. First determine whether the intended cue–path association is reproducible across genuinely different source pools and admissible nuisance controls. If another encoder experiment is justified, compare a narrowly specified trial-contained temporal/objective change under the same source-safe evaluation. That would isolate an encoder hypothesis; this decoder-only ablation cannot do so retrospectively. No next experiment is launched by this recommendation.

Condition-level pseudopopulations remain a legitimate research lane. Lack of a large simultaneous recording does not bar that work, but these results cannot support exact natural-trial population states, intention, causal planning, H1b or H2. Task/cue/history/gaze/recording metadata limitations remain unresolved.

## 9. Execution, checks and artifacts

This new study completed **1700new decoder fits +20null-world PCA transforms**, reused800prior model/forward outputs, and added **zero CEBRA or observed-PCA fits**. All models and all attempted configurations are retained. The fitting/analysis stage took about44.5seconds; the bounded run plus replay/report stage finished in about108seconds. Earlier implementation/review time is not biological fitting time.

The implementation worker timed out after leaving code and passing synthetic tests. Independent prefit review then identified missing integrity/accounting gates; the parent fixed them **before biological fitting**. Six focused tests and a90-fit invented-data SVM precision check passed. The actual biological run completed without a failed fit or convergence warning. The prior decoder study's earlier failure/three preflight PCA fits remain separately documented, not recounted as new runs here.

Forward verification blocked all fit entry points and replayed2500model records,395,000predictions,5000metric rows,20null PCA transforms,480temperature rows,140class-alignment rows,228,000source-weight rows and25,080deletion rows. Shared-code numerical discrepancies were0. Independent prediction-level review recomputed all5000groups: maximum BA/AUROC/logloss differences were1.11e−16 /2.55e−15 /1.41e−8, below the declared1e−6tolerance. It returned no findings. The repository regression suite passed117tests. Primary static checking confirmed one file and timed out on the other; intentional fail-closed conversion heuristics are documented, not presented as a complete static-analysis pass.

Accepted local authority:

`outputs/cebra-hyperparameter-diagnosis-20260924/run-20260924T105957Z/`

- `verify_receipt.json`, `run_config.json`, `audit_manifest.json`, `event_journal.jsonl`, model/feature manifests, PCA ledger and `source_snapshots/` contain the execution identity and replay evidence.
- `readout_metrics.csv`, `readout_predictions.csv`, `confidence_temperature_metrics.csv`, `class_contrast_alignment.csv`, `source_bootstrap_metrics.csv`, `delete_source_influence.csv` and `null_family_tails.json` preserve complete results.
- `report-machine/review_tables.json` contains all76observed summaries, confidence/alignment tables, source sensitivity and descriptive point decisions. The offline HTML embeds all grid figures and the numerical appendix.
- `outputs/cebra-hyperparameter-diagnosis-20260924/management/` retains the protocol journal, no-fit audit/test/run logs and figure-generation script.
- Prefit science review: `48a8e7d1-df62-42ec-b4b4-06de10cae73f` (reviewer index1); code review/fixes: `6bcfc959-4636-4186-8f12-63ae38c0e592` → `cdcda3ad`; independent numerical review: `59431cdb-41d5-4d41-bb9b-8bf1475aac66`; encoder forensics: `e8aee30d-58fa-4451-abd8-425f6ce3a3a0`. Review outputs live under their `.pi-subagents/artifacts/outputs/<run-id>/work/cebra-hyperparameter-20260924/` directories where saved. Fresh-context final claim/HTML review `de58ef95-8492-49d7-b754-969f7132ec42` approved with the exploratory/frozen-encoder limits above; its receipt is `final-claim-review.md` in that run's artifact directory.

Executed code snapshots are authoritative; subsequent automatic formatting changed working-file bytes but was checked to leave its AST identical. No install, GPU training, raw/original-test import, lab access, branch switch, commit/push or persistent service was introduced. Retained lab artifacts are ignored/local; Git and the portable HTML are not a full data backup. AI review is QA, not laboratory metadata validation or scientific peer review.
