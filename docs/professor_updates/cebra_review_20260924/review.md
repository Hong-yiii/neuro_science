# CEBRA versus PCA: what the completed decoder studies establish

**Research progress review · Evidence through 24 September 2026**  
**Status:** exploratory, computationally verified analyses; not confirmatory evidence for prospective path coding. This synthesis adds no model fits.

## Executive assessment

The question is whether hippocampal cue-period activity contains information about the subsequently observed navigation path **beyond start and goal**. CEBRA is one candidate representation method, not the scientific hypothesis.

The latest frozen-encoder study does **not support excessive decoder regularization or the original RBF bandwidth as the main explanation** for poor path decoding within the tested family. Training separation is strong, but the fitted mappings do not transfer successfully to the historical-validation source pool. Confidence reduction improves probability loss without improving classification or ranking.

A simpler representation remains competitive: PCA followed by an RBF support-vector machine reaches **77.5% mean balanced accuracy** in the path assay. This is **not an all-linear pipeline**, and the available matched nulls do not establish it as a biological positive result. In the separate endpoint experiment, a phase-matched CEBRA sampler approaches PCA: **83.33% versus 83.61% joint start–goal development accuracy**. Thus neither universal PCA superiority nor intrinsic CEBRA/task incompatibility follows.

**Recommendation for discussion:** retain PCA and raw-count baselines; do not expand decoder grids on these same frozen embeddings merely to seek a positive result. Prioritize independent-source reproducibility and available nuisance controls before a narrowly specified encoder-design comparison.

## 1. Two evaluation questions—not one performance leaderboard

| | Endpoint-condition study | Recent path-component decoder study |
| --- | --- | --- |
| Target | One of 30 ordered start–goal pairs | Presence of one interior component, `D_N_R_T__N_R_M`, within fixed endpoints 4→3 |
| Recorded support | 195 selected units, 58 sessions | 29 selected units, 7 sessions |
| Real source trials | 12,288 training; 3,265 inner development | 82 training; 22 historical validation |
| Evaluation object | Label-conditioned cross-session pseudopopulations | Label-conditioned cross-session pseudopopulations; exact evaluation over 30 combinations |
| Cue representation | Ten 100 ms bins from the first cue second | Same nominal cue/bin arrangement |
| Principal metric | Joint classification accuracy; balanced 30-class evaluation, chance 3.33% | Balanced accuracy (BA): average recall across two classes, chance 50% |
| Repeated computational runs | Three assembly/model seeds | 25 assembly/optimizer settings per CEBRA objective; five raw/PCA assemblies |

These source counts are not simultaneous population trials. A synthetic row combines same-condition real trials across sessions, preserving each session's cells and bins. Repeated rows, bins and seeds are not independent biological replications. Source-disjoint evaluation does not imply unseen sessions, animals or a pristine test set. All quoted results are development/exploratory results; historical exposure remains permanent.

The endpoint task can be supported by cue identity, current start and previous-goal structure. It is therefore a useful pipeline comparison but **not evidence for path information beyond endpoints**. The two studies also differ markedly in available source support, so their percentage scores cannot measure relative task difficulty in isolation.

## 2. Path study: interventions and outcomes

The latest study held observed encoders, neural arrays, target, source assignments and evaluation weights fixed. Each model received its own training-fitted decoder; “frozen encoder” does not mean “untrained decoder.” CEBRA and PCA each supply eight features per bin, concatenated into 80 whole-cue decoder inputs. Raw counts supply 290 inputs. PCA is a parallel representation branch, not preprocessing before these CEBRA encoders.

The frozen family comprised six logistic penalties, C ∈ {0.001, 0.01, 0.1, 1, 10, 100}; nine scaled RBF-SVM combinations, C ∈ {0.1, 1, 10} × gamma multipliers {0.1, 1, 10}; and four retained legacy readouts. Smaller logistic C means stronger L2 regularization. Positive temperatures T ∈ {1, 2, 5, 10} softened the existing C=1 logistic scores without fitting or selecting a new threshold.

| Diagnostic | CEBRA-Time | CEBRA-Behavior | Interpretation |
| --- | --- | --- | --- |
| Logistic C=0.001 → 100 | Development BA **30.92% → 24.25%**; training BA 97.63% → 100% | Development BA remains **34.67–35.75%** across the grid; training BA 100% | Weaker regularization did not rescue transfer |
| Largest mean BA in the nine-setting SVM grid | **50.00%**, AUROC ≈0.286 | **49.83%**, AUROC ≈0.211 | Chance-level decisions are not a nonlinear rescue; ranking remains poor |
| Confidence-only T=1 → 10 | Log loss **2.6448 → 0.8110** | Log loss **1.6571 → 0.7478** | BA and AUROC unchanged; probability loss can improve without discrimination |

AUROC measures score ranking, with 0.5 as the no-discrimination reference; it is not thresholded accuracy. Both softened CEBRA losses remain worse than the balanced constant-probability loss, ln(2) ≈0.6931. No temperature, decision threshold or prediction sign was selected on validation data.

<!-- figure:regularization_ba -->

### What remains promising—and unconfirmed—about PCA

PCA plus the center RBF-SVM produces **77.50% BA / 0.829 AUROC**, averaged over five assemblies. In contrast, PCA plus scaled C=1 logistic gives **42.92% BA / 0.157 AUROC**; the best tested scaled-logistic BA is 46.25%. The apparent advantage is therefore a **representation–decoder interaction**, not proof that a linear classifier solves the task.

The new controls reconstruct 20 source-label-shuffled worlds before label-conditioned assembly; each world's PCA is fitted only on that world's training assembly. They do not reuse the observed PCA basis or merely shuffle final decoder labels.

| Predeclared anchored reference | Inclusive plus-one tail |
| --- | ---: |
| CEBRA: two objectives × 19 readouts | 18/21 = **0.8571** |
| Raw/PCA: two representations × 15 grid settings | 15/21 = **0.7143** |
| Joint family: 68 settings | 19/21 = **0.9048** |

These are maximum-over-family, no-association references at **assembly 0 / optimizer 0** for CEBRA and **assembly 0** for raw/PCA. They are **not p-values for the 25-run or five-assembly means, not PCA-versus-CEBRA superiority tests, and not correction for the whole adaptive research history**. The fixed center-PCA anchor scores 58.33% BA, with a descriptive tail of 7/21 =0.3333. Consequently, these null checks do not establish the PCA lead, but they do not directly reject its 77.5% mean either.

Fixed-model source-reweighting gives PCA-center BA quantiles of 55–100%; the 14 estimable source deletions give 68.33–88.33%. Eight additional deletions remove all support for a class and are inestimable. These are sensitivities to this source pool—not animal/session-adjusted confidence intervals or evidence of replication in new recordings.

## 3. Endpoint study: the initial CEBRA deficit was not permanent

| Endpoint comparison | Three-seed mean joint development accuracy |
| --- | ---: |
| Original PCA / Time / Behavior, all with scaled logistic C=1 | **82.50% / 42.78% / 18.61%** |
| Same original representations, scaled logistic C=0.01 | **83.61% / 51.67% / 25.56%** |
| Behavior, temperature 0.3, 250 updates; ordinary same-pair positives | **53.06%** |
| Behavior, same temperature/update budget; same-pair **and same-bin** positives, global negatives | **83.33%** |

The last two rows are the informative sampler contrast. Early and late cue responses need not be equivalent even when their endpoint pair is identical. Restricting positives to the same cue phase changes the invariance requested of the encoder. The result supports the importance of sampling/objective design; it does not uniquely establish which biological variables were retained or discarded.

Training the latter same-bin-positive recipe to 3,000 updates reduces accuracy to **64.86%**. In a separate, fully time-matched sampler experiment at 3,000 updates, increasing synthetic training rows per class from 16 to 64 raises CEBRA from **59.58% to 81.53%**, while matched PCA rises from **83.61% to 84.86%**. That is a different sampler contrast, not an extension of the 83.33% row. Additional rows also increase distinct source usage within the existing pool; they are not new recordings or a pure compute intervention.

The endpoint improvements remain exploratory selections on inspected development data. They show that CEBRA can be competitive on this conditional assay, not that an independently validated CEBRA winner or deployable unknown-trial decoder has been established.

## 4. Why a simpler representation can outperform a learned encoder

**Capacity is not the same as the representation selected by training.** PCA preserves dominant linear variance in standardized counts. CEBRA optimizes a contrastive similarity objective determined by its positive/negative sampling. Neither objective guarantees preserving the feature most useful for transfer to new sources. PCA can retain useful large-scale variation with fewer task-specific design choices, but it can also discard predictive low-variance structure.

A flexible nonlinear encoder can fit source-specific details, particularly when effective support is much smaller than the number of synthetic rows or time bins. These encoders were trained on the study's data; they are not foundation models importing large-scale external pretraining. Their extra flexibility has to earn its cost through held-out transfer.

The current evidence separates three propositions:

- **Observed:** fitted training mappings fail to transfer reliably in the path assay; relaxing decoder penalties and changing tested bandwidths do not resolve that failure.
- **Plausible, not isolated:** temporal/objective mismatch, nuisance associations, limited source support or discarded task-relevant structure may contribute.
- **Not established:** a unique CEBRA implementation fault, zero information in the embeddings, absence of prospective neural information, or inherent incompatibility between contrastive learning and a future behavioral target.

At the encoder's forward pass, only cue activity is supplied. A future-derived training label is not intrinsically invalid supervision. However, assembling the evaluated pseudopopulation itself uses its true condition: this remains a **condition-level assay**, not end-to-end prediction of an unknown natural trial. Below-chance AUROC may reflect reversed associations; it is not a license to flip predictions after observing validation labels.

## 5. Interpretation and proposed decisions

1. **Use the simplest defensible reference, not the preferred algorithm.** Keep raw/PCA baselines and distinguish linear representation from nonlinear decoder. CEBRA is optional for H1a; a supervised embedding's geometry alone does not establish H1b.
2. **Treat source reproducibility as the immediate evidence gap.** Audit source/session support and task, cue, history and gaze controls where available. A larger simultaneous recording is not a prerequisite for valid condition-level work; it is required for stronger exact-trial population claims.
3. **If a new encoder comparison is justified, isolate an encoder hypothesis.** A bounded trial-contained temporal-input or positive-sampling contrast is more informative than another unrestricted decoder search. Freeze target, independent-source evaluation, common readouts, nulls and stopping rules first. A phase-matched endpoint success is motivation, not a promised path remedy.
4. **Reserve genuinely unexposed observations for a new confirmatory claim.** No resplit makes the historical development/test exposure disappear. New-source evidence and a null targeting the intended multi-assembly statistic would be needed before treating the PCA mean as a robust positive result.

**Questions for the meeting:** Which nuisance variables and source blocks can be verified from available records? What source-level replication would be meaningful for the condition-level question? Is a temporally richer encoder comparison justified before that replication is available?

No new experiment is authorized or launched by these recommendations. H1 absence, H1b, artificial-agent equivalence, intention and causal planning have not been demonstrated.

## 6. Evidence and reproducibility

The latest hyperparameter study completed **1,700 new decoder fits and 20 null-only PCA transforms**, reused 800 prior model/forward outputs, and fitted **zero new CEBRA encoders or observed-data PCA transforms**. Fit-forbidden replay verified 2,500 model records, 395,000 predictions and 5,000 metric rows, plus source/temperature/PCA diagnostics. Independent prediction-based review found only numerical differences below 10⁻⁶; 117 software regression tests passed. Software checks do not establish biological metadata, scientific identifiability or pristine evaluation.

Primary reading and local authorities:

- [Full hyperparameter results and all-grid HTML](../../reports/cebra-hyperparameter-diagnosis-20260924.html); [frozen protocol](../../reports/cebra-hyperparameter-prefit-20260924.md). Accepted run: `outputs/cebra-hyperparameter-diagnosis-20260924/run-20260924T105957Z/`; `verify_receipt.json` binds the scientific inputs; `readout_metrics.csv` and `null_family_tails.json` preserve the complete results.
- [Earlier eight-readout study](../../reports/cebra-decoder-autoresearch-20260924.md). Its accepted no-fit recovery is historical input to the latest study; its earlier implementation failure and preflight-fit deviation remain disclosed there, not erased by this synthesis.
- [Endpoint investigation](../../reports/start-goal-autoresearch.md), [original endpoint baseline](../../reports/start-goal-cebra-baseline.md) and [decoder diagnosis](../../reports/start-goal-cebra-diagnosis.md). Primary endpoint follow-up metrics: `outputs/start-goal-autoresearch-20260907/all_metrics.csv`.
- [Research question](../../research-questions.md) and [analysis contract](../../analysis-contract.md) define the claim ceiling. The separate September 13 matched PCA/non-PCA PRD remains unexecuted. The older five-endpoint preprocessing study and three-seed V9 atlas scores are not substituted for this exact-product assay.

This document is a synthesis for laboratory review, not independent peer review. Detailed artifacts remain local/ignored; the portable report contains no raw neural recordings. Public sharing should follow laboratory policy.
