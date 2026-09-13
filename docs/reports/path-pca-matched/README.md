# Did PCA improve the matched path-component predictor?

**Status:** complete; full forward-only replay passed and independent numerical/claim/report reviews approved. Exploratory study, 13–14 September 2026. [Draft PR #7](https://github.com/Hong-yiii/neuro_science/pull/7), addressing [issue #6](https://github.com/Hong-yiii/neuro_science/issues/6).

## Short answer

**PCA gave a small improvement in probability loss on this fixed historical benchmark—not a robust biological win.** Raw loss was **0.664564**, versus **0.657541** with PCA: a paired advantage of **0.007023 nats**. Lower loss is better. Both selected λ=1 from the same three training-CV options, and both had **55% balanced accuracy**.

PCA compressed the same unit rates into fewer weighted combinations. It did not add recordings or turn these artificial, known-label population rows into real simultaneous trials. A useful plain-language verdict is: **“PCA made the probability guesses slightly better here, but did not solve the weak generalization result.”**

| Start→goal | Raw loss | PCA loss | Improvement from PCA |
|---|---:|---:|---:|
| 2→1 | 0.694618 | 0.694618 | 0.000000 |
| 3→1 | 0.775618 | 0.771723 | +0.003895 |
| 4→1 | 0.643258 | 0.642561 | +0.000697 |
| 5→1 | 0.810584 | 0.785025 | +0.025559 |
| 6→1 | 0.398740 | 0.393778 | +0.004963 |

Balanced constant-.5 loss is **0.693147**. Only **2/5 endpoints** beat that baseline in either arm. The biggest **PCA-over-raw improvement** came from 5→1, where both methods still lost to baseline. By contrast, the positive **overall baseline-relative score** in both arms remained 6→1-dominated: omitting 6→1 gives raw Δ−0.037872 and PCA Δ−0.030335. These are different comparisons; do not conflate them.

## How fragile was the difference?

- Paired source-resampling 2.5th/50th/97.5th percentiles: **−0.011444 / +0.005029 / +0.023426**. These are fixed-selection sensitivity percentiles, **not confidence intervals or a superiority test**. They span both signs.
- Assembly seeds 1/2 retained small positive differences: +0.006118/+0.009714. All leave-endpoint/session-out mean paired point effects were positive, but these reuse overlapping sources and are not independent replications.
- PCA selected-policy ordinary/temporal-half label-null references were **13/101** and **17/101**; maximum-six references **18/101** and **20/101**. These are no-path-association references for PCA versus baseline, **not PCA-superiority p-values**. See the full report for both arms.
- There are only **147 training + 41 historical-validation original sources**, across **49 units and 13 sessions**. **17/28 validation pools are singletons**. Endpoints 2→1 and 4→1 are point/influence-only.

## What was compared—and what was not?

Exactly six recipes: raw/PCA × λ{.01,.1,1}, same first-second rates, training-only variance-floor scaling, original source splits, session-block draws, evaluation rows, and tuning budget. Final PCA dimensions were **2/2, 9/14, 2/3, 7/12, 13/23** inputs across the five endpoints. The 90% variance rule measures compression, not path information or intrinsic brain dimensionality.

The target was one directed component among all interior path corridor runs, not the whole path or start–goal classification. Old ~83% PCA endpoint accuracy and earlier PCA segment percentages are different benchmarks. Historical validation was already exposed; eligibility used its support. Unresolved gaze/history/task/recording metadata and source dependence remain. No absence/equivalence, universal superiority, confirmatory H1, H1b or H2 claim follows.

## Reviewable package

- [Full tables, methods and figures](report.md); [self-contained offline HTML](report.html).
- [Frozen protocol](protocol.md), [execution/attempt ledger](execution.md), [agent evidence index](evidence.md).
- [Machine summary](summary.json), [verification receipt](verification.json), [report-generation evidence](report-evidence.json).
- [Input audit](input-audit.json), [historical compatibility](historical-compatibility.json), [independent reviews](reviews/).

The draft PR remains open for Hongyi's review. Full inputs, model states, predictions, lineage and logs remain ignored/local; Git is not their backup. No merge is authorized by this result.
