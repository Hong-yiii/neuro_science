# Independent quantitative and provenance audit — 16 November 2026

**PASS. UNDERSTANDABLE: yes.** No quantitative correction is required for the
reviewed overview, construction labels/counts, pool definition or accompanying-data
statement. This verdict concerns the narrow manuscript revision and the existing
public scalar evidence; it is not a new scientific execution or a complete audit
of the historical studies.

Reviewed final identities:

| Item | SHA256 / revision |
| --- | --- |
| `paper.pdf` | `ed5c207f3fd85a4e0d41f0d39d6c9b1219d85def770eede716947586615ac72c` |
| `paper.tex` | `8f30636542bee0768208a5536d1bdb7428b8445dfc798378bbda57cc5030204c` |
| Comparison baseline | Git commit `3416df8f085b4fce76951e922c61663e3147f5a2` |

## Scope and independence

Read the mandatory `AGENTS.md` and `docs/workspace.md`, the manuscript diff,
relevant manuscript methods, and extracted PDF text for pages 1, 2, 6 and 21.
Checked the final page-2 opening and the final explicit PCA/SVM repeat sentence
after those two wording changes. This is a quantitative/readability-of-terms
assessment, not a separate visual-layout inspection.

Evidence comprised the existing public `case_scores.csv`,
`model_pair_means.csv`, `model_pair_best_means.csv`, `matched_contrasts.csv` and
`arm_design.csv`, plus the frozen November 14 protocol and `design.json`.
No package README, validation document, author/probe memo or other review was
read. The verdict was derived independently from those scalar tables and frozen
design records, without another reviewer's findings.

Only standard-library arithmetic, Git inspection, hashes and PDF text extraction
were used. No metadata/scientific pipeline script was run. No model was fitted,
loaded or replayed; no neural array was read; no notebook was executed or parsed.

## Scalar-table checks

The source table contains 2,304 score rows. The relevant pair-head subset contains
768 rows: 288 observed rows and 480 source-label-control rows. Recomputed, directly
from those pair scores:

- All 96 representation/readout/arm summaries, including three seed scores,
  their mean, minimum and maximum: 576 numeric cells agree, with maximum absolute
  discrepancy `1.4210854715202004e-14` percentage points from floating-point
  arithmetic.
- All 24 accompanying best-mean comparison rows, including their four input
  means, best mean and winning representation.
- All 896 pair-head matched contrasts: maximum absolute discrepancy
  `1.1102230246251565e-16` in balanced-accuracy units.

These checks establish internal scalar provenance for this revision. They do not
reconstruct scores from predictions or reauthenticate the original biological run.

## Overview claims

All scores below are development pair balanced accuracy. Changes are percentage
points; averages use the three computational repeats, not biological replicates.

**More distinct recorded trials.** CEBRA-Time's B5 minus B2 mean changes are
`+21.30`, `+29.63`, `+25.46` and `+13.89` for logistic, SVM, kNN and LDA,
respectively. Thus the stated improvement in mean with every classifier is
correct. This does not assert improvement in every repeat: the LDA seed-2 change
is `-2.78`. The text correctly leaves broader response coverage and reduced reuse
unseparated. The fixed construction selects nested 2/3/5-source budgets at 16 rows
per class, with 8, 5–6 and 3–4 uses per selected source, respectively.

**Repeated assembly.** For CEBRA-Time, B3 minus U3 kNN gains are
`18.06`, `22.22` and `11.11`; all exceed the maximum of the five matched shuffled
gains, `9.72`. This readout also has the largest CEBRA-Time mean repetition gain,
`17.13`, compared with `10.65`, `10.19` and `5.56` for logistic, SVM and LDA.
The SVM observed changes span `5.56–16.67`, while the control changes span
`-4.17–19.44`; the stated overlap is correct. Raw/PCA SVM mean changes are
`-2.78/-6.94`. In U3, the minimum observed Raw/PCA SVM scores are `36.11/33.33`,
above their maximum sampled control scores of `18.06/15.28`. The overview's
selective-benefit interpretation is therefore supported descriptively.

**Population expansion.** The following directly reconstructed means verify
both expansion steps for every stated classifier:

| Classifier | PCA, 17 → 49 → 83 units | CEBRA-Time, 17 → 49 → 83 units |
| --- | --- | --- |
| Logistic | 37.50 → 65.74 → 71.30 | 36.57 → 44.44 → 50.46 |
| SVM | 33.33 → 68.06 → 72.22 | 34.72 → 35.65 → 48.61 |
| kNN | 32.87 → 54.63 → 66.20 | 35.65 → 47.69 → 49.54 |
| LDA | 23.15 → 53.24 → 55.09 | 29.17 → 41.20 → 43.98 |

PCA has the highest mean among the four representations in each of the eight
larger-population/readout comparisons. The final PCA/SVM step changes by
`+16.67`, `-2.78` and `-1.39` in seeds 0, 1 and 2: exactly one improves and two
worsen. Native's corresponding mean changes are `-14.81`, `-11.11`, `-15.74` and
`-16.67` for logistic, SVM, kNN and LDA. All are negative. The protocol confirms
that this expansion changes the session roster, number of session-specific
encoders and equal-session pooling, so the manuscript does not isolate width as
the sole cause.

**Encoder and classifier together.** At B5, CEBRA-Time exceeds both Raw and PCA
with kNN and LDA in all three repeats: all 12 stated paired comparisons are
positive. The smallest advantage is `5.56` points. The best complete mean
pipeline across all four representations and four readouts is:

| Construction | Best complete pipeline | Mean (%) |
| --- | --- | ---: |
| B2 | Raw / logistic | 37.96 |
| B3 | Raw / logistic | 42.13 |
| B5 | Raw / SVM | 59.72 |
| U3 | PCA / logistic | 46.30 |
| Wmid | PCA / SVM | 68.06 |
| Wfull | PCA / SVM | 72.22 |

Each exceeds the best CEBRA-Time/Native mean in that construction. The opening
and concluding overview statements are correct as descriptive mean comparisons
among the tested pipelines. They do not validate a configuration selected on
these repeatedly inspected development scores. The existing scope paragraph
states the known-label construction and unevaluated transfer settings.

## Pool definition and construction counts

The new page-1 source-pool definition agrees with the protocol's session–class
pools. Table 1 distinguishes distinct trials, additional constructed rows and
additional units/sessions. Table 5's caption specifies per-pool budgets versus
construction-wide trial-ID and training-row totals. Those denominators make the
descriptive row labels understandable.

Checked all six arms against the frozen design's nine classes and core/middle/full
rosters, and the protocol's source budgets, balanced reuse and row rules:

| Arm | Units / sessions | Trials per pool | Selected training IDs | Training rows | Uses per trial |
| --- | --- | ---: | ---: | ---: | --- |
| B2 | 17 / 3 | 2 | 54 | 144 | 8 |
| B3 | 17 / 3 | 3 | 81 | 144 | 5 or 6 |
| B5 | 17 / 3 | 5 | 135 | 144 | 3 or 4 |
| U3 | 17 / 3 | 3 | 81 | 27 | 1 |
| Wmid | 49 / 11 | 3 | 297 | 144 | 5 or 6 |
| Wfull | 83 / 20 | 3 | 540 | 144 | 5 or 6 |

Selected IDs equal `9 × sessions × trial budget`; rows equal `9 × rows per
class`. All constructions have `9 × 8 = 72` development rows. The frozen protocol
specifies U3's shared selected sources with B3, nested width rosters, shared
development construction and B3's single fit per repeat/control. These are checks
against the frozen records; source identities and construction were not rerun.

## Preservation and accompanying artifacts

Byte-for-byte SHA256 comparisons against the baseline Git blobs passed for all
**21 existing package data files and 20 figures**. This includes all scalar
tables, the retained `model_pair_best_rows.tex` ranking artifact, and the existing
figure files. The page-21 statement that accompanying tables retain the scalar
scores and mean rankings is accurate. The removed ranking-table TeX input and
matching Makefile dependency do not alter those artifacts.

Git comparison with the same baseline reports no tracked changes under `data/`,
`experiments/` or `notebooks/`, or to the frozen design/protocol. Thus the tracked
experimental inputs, source/published notebooks and their figures remain unchanged
by this revision. Ignored historical run trees were not accessed or reauthenticated;
this report makes no fresh receipt-audit claim for them. The audit made no changes
to the pre-existing `src/neuro/_cebra_sampling.py` edit or untracked
`docs/reports/current-state-20260927/` directory. Its only written file is this
report.

Evidence hashes:

| File | SHA256 |
| --- | --- |
| `data/case_scores.csv` | `1661ff9d7b55644d586ad8efb21a440032c23d18f0121767100fd162acb89249` |
| `data/model_pair_means.csv` | `1f0d976f1cd648bdb938d3511dfa5fa34312e7935f1c90af80aaef82708ca16d` |
| `data/model_pair_best_means.csv` | `b115a3f52d43c40d349d06e62684abee357478b61cc931f4c32894178f556d49` |
| `data/matched_contrasts.csv` | `c66d7eac5aea706ccd4c4b90cd30012ca4e241047cc0f966d74dc418e820ec42` |
| `data/arm_design.csv` | `1bcdf75e45452338f376c031b9502f2f430ea3039403a83e4d30a2e41a4a62bc` |
| Frozen `design.json` | `f35f91ae6936956d5c9e99550267eeabae213347f3b07ff22fac8bd3a6a23c29` |
| Frozen `protocol.md` | `7d1dbd5d26352725eb522389c5400dd753bb301ea7894328afde25d820b18005` |

The first five paths are relative to `report/series-20261115/`; the frozen records
are under `docs/experiments/source-reuse-width-20261114/`.
