# Path preprocessing: what worked, what did not, what remains unknown

**Study:** 8 September 2026. **Review:** 9 September 2026 (Singapore). Retrospective synthesis of three read-only reviews: methods, scientific validity, and engineering. No new experiments or model fits.

> **Decision:** keep first-second raw rates, variance-floor scaling, and strongly regularized logistic regression as the baseline. It improved probability prediction within the tested family; it did **not** establish reliable broad path decoding. The next priority is stronger source-level evidence and controls, not an open-ended search on the exposed validation set.

## 1. What this result actually measures

The target is whether a fixed directed component occurs among the later path's interior corridor runs, **not the complete path**. Each start–goal pair has its own model.

A **condition-level pseudopopulation** joins session feature blocks using known path labels. Original trials are split first; each block preserves its source's cells/bins. This tests conditional response reproducibility, **not unknown-label decoding of one natural simultaneous trial**.

Support: **147 training + 41 historical-validation source trials, 49 unit IDs, 13 sessions**. Neural input covers the first `[0,1)` seconds of the accepted operational cue window. These are not 188 simultaneous 49-unit recordings. Source identity separation does not guarantee independence of nearby trials. Validation was already development-exposed; its class support also helped freeze eligibility. [1,2]

## 2. What worked—and what did not help

The primary score is **Δlogloss = log(2) − balanced logloss**. Positive is better than predicting probability 0.5 in this balanced conditional benchmark. Accuracy alone ignores how confident the mistakes are.

| Choice | Decisive matched evidence | Verdict |
|---|---|---|
| Coarse versus fine time bins | Raw/standard, λ=0.1: moving from one to five bins reduced training loss **0.2728 → 0.0947**, but worsened source-held-out CV loss **0.7058 → 1.1431**. | Fine detail fitted training better, not held-out sources. Keep pooling as the baseline; do not infer absence of temporal neural coding. |
| Raw versus compressed rates | One bin, floor, λ=0.1: CV Δ was **+0.0739 raw**, **−0.0214 square root**, **−0.0702 log1p**. | Compression did not help this readout here. Invertible transforms can change linear decodability without destroying information. |
| Variance-floor versus standard scaling | One-bin raw, λ=0.1: CV Δ improved **−0.0126 → +0.0739**. | Avoid excessive amplification of tiny feature SDs. This is numerical regularization, not a validated neural-noise model. |
| Stronger L2 penalty | Raw/floor CV Δ for λ=0.01/0.1/1: **−0.2700 / +0.0739 / +0.0926**. Historical loss fell **0.8473 → 0.6646** from λ=0.1 to 1. | Stronger regularization improved the declared probability score. It does not independently prove calibration or biological reliability. |

Matched comparisons: [1,2].

**Important limits:** there were 18 initial recipes, then only two L2 extensions for the CV-winning representation: **20 observed-data candidates**, not a full hyperparameter grid. Strong L2 was not tried for every fine-bin or transformed representation. One bin means pooling time **within each unit**: the 6→1 model still has 23 inputs, versus 115 for five bins. Neither count estimates brain dimensionality.

A useful warning: λ=0.01 achieved **68.73% CV balanced accuracy**, versus **63.74%** for λ=1, yet its probability loss was much worse. “More labels correct” and “better probability predictions” were different objectives. Selection correctly followed the predeclared score. [1]

## 3. What the study did not establish

| Proposed conclusion | Evidence that limits it |
|---|---|
| Reliable performance across endpoint panels | Selected historical **Δ +0.0286; balanced accuracy 55%**. Only **2/5** endpoint deltas were positive. Omitting **6→1** changes the mean to **−0.0379**. |
| Clear separation from the declared nulls | Ordinary selected/max-family p-values: **0.168 / 0.356**. Temporal-half selected/max-family: **0.139 / 0.297**. All compare with the same observed CV-selected statistic; each null repeats the adaptive search. |
| Replication beyond the observed source pools | **17/28 validation pools are singletons.** Source-bootstrap 2.5th/50th/97.5th percentiles: **−0.0875 / +0.0154 / +0.1006**. These are sensitivity quantiles, not confidence intervals. |
| Confounds were excluded | Trial-index/cue-duration nuisance-only Δ was **−0.3561**, but this was a fixed-λ linear comparator, not a matched-tuned nuisance-versus-nuisance+neural test. Failure of this control does not rule out history, gaze, heading or state effects. |

Controls and limits: [2–4].

Additional assembly seeds retained small positive averages, but resampling existing observations is not new biological replication. Temporal conditioning also leaves **64/188 labels structurally fixed** in pure-label strata; it does not prove serial exchangeability.

**Still unknown:** whether the 6→1 pattern reproduces in genuinely new sources; whether verified task/cue/history variables explain it; and whether the design can detect a biologically worthwhile effect. No H1-absence/equivalence conclusion follows. H1b low-dimensional organization, H2 artificial-agent comparison, and new PCA/CEBRA models were **not tested** here. Earlier studies used different cohorts and are not matched preprocessing ablations.

## 4. Engineering: success is not scientific confirmation

- **Keep:** source-first splits, masked missing cells, training-only preprocessing, matched draws, adaptive-selection nulls, saved lineage, and no-fit replay. The completed receipt reports **82,283 forward replays, zero new fits**, alongside the prior 19-test pass. Those counts are computational checks—not biological sample size. [4]
- **Fixed failures:** the first final run exceeded the 20 MB console cap; an unchanged file-logged rerun succeeded. Its **12,850 interrupted-attempt fit records** remain retained and excluded from accepted inference. Missing verifier checks, its clipping mismatch, and three HTML formatting defects were also fixed. [5]
- **Remaining limits:** the verifier reuses some production helpers, so it is not wholly independent software. LSP checks were inconclusive. Raw data and full model artifacts remain local/ignored; neither Git nor the report/code ZIP is a complete backup. [4,5]

## 5. Three next decisions—not new work started

1. **Freeze the follow-up question.** If prioritizing 6→1, label that choice as performance-motivated and reserve genuinely new source sets before examining their outcomes. Keep other declared comparison contexts visible.
2. **Verify nuisance information and compare fairly.** Check task/cue timing and admissible history/view/heading metadata; plan nuisance-only versus nuisance+neural models with matched training-only tuning.
3. **Define a worthwhile effect and assess sensitivity.** Use explicit source/noise assumptions before deciding whether additional observations or richer models are justified. More pseudorows cannot manufacture missing source variability.

Do not abandon condition-level pseudopopulations, require individually significant neurons, invert labels post hoc, or keep tuning the same historical diagnostic until it looks positive.

## Evidence map

See the [full report](path-preprocessing-autoresearch-20260908.md) and [frozen methods](path-preprocessing-prefit-20260908.md) for complete tables. Below, `RUN` means `outputs/path-preprocessing-autoresearch-20260908/biological-20260908T115508Z/` in this worktree.

| Ref | Authority and what it proves |
|---|---|
| 1 | `RUN/round1/round1_cv_metrics.csv.gz` and `RUN/round2/round2_summary.json` → original training/CV comparisons, `family20_summary_rows`, CV-only selection. |
| 2 | `RUN/final-20260908T133200Z/final_summary.json` and `observed/validation_metrics.csv.gz` inside that final directory → observed point scores, endpoint influence, all four p-values, source quantiles and nuisance policy. |
| 3 | `RUN/descriptive-audit.json` → actual source-label movement, singleton pools and fit accounting. |
| 4 | `RUN/verification-final.json` → recorded replay coverage, count and verifier hash. The full replay was not rerun for this review. |
| 5 | Original manager `outputs/path-autoresearch-management-20260908/REVIEW-RESOLUTION.md` and `FINAL-ATTEMPT-1-FAILURE.json` under `/home/hongyi-home-lab/neuro_science/` → repair and failed-attempt history. |

New read-only review memos are retained under `/home/hongyi-home-lab/neuro_science/outputs/path-review-teach-20260908/`: `methods-review.md`, `science-review.md`, `engineering-review.md`. These are AI-assisted checks, not human peer review. This review is an addendum; the earlier report, package and scientific artifacts were not rewritten.
