# Independent quantitative and provenance review — 16 November 2026

**Verdict: PASS. UNDERSTANDABLE: yes.** The checked numerical claims, new model-comparison summaries, paired-control wording and preservation claims agree with the saved scalar evidence. No critical, major or minor quantitative finding requires revision.

This is a fresh independent review of the final 21-page language revision. It is an artifact and arithmetic review; it does not revalidate biological fits. I read the required workspace context, manuscript/source, saved scalar CSVs, frozen protocol/design and relevant tracked implementation. I did not consult the manuscript package's README verdicts, other reviewer reports or author/probe memos. No model loads, neural-array reads, fitting, notebook execution, metadata reconstruction, optimizer reruns or private output access occurred. The manuscript's final page-1 typography and page-4 outer-partition clarification are included in the reviewed version.

The reviewed identities are SHA-256:

| Artifact | SHA-256 |
| --- | --- |
| `paper.pdf` — 833,768 bytes, 21 pages | `d99b2d02cc25f15e6d5354ff684f376441563e159d8b23c49ddb6f8e5d6b27f5` |
| `paper.tex` | `088d75baa04f4cf29fbb7b496fe09641c71a79d2c4042683d09ff1feaf9e2353` |
| `data/case_scores.csv` | `1661ff9d7b55644d586ad8efb21a440032c23d18f0121767100fd162acb89249` |
| `summarize_model_comparisons.py` | `cee166f6418adf1316c64b75684a6a38ce33e3ed2c008204a8dab97fe9d7e70e` |
| `model-comparison-provenance.json` | `d691b4caa7f8b4738c700d28155a6d9f175e87ff11b4cd709ad9879de82719d8` |
| `data/model_pair_means.csv` | `1f0d976f1cd648bdb938d3511dfa5fa34312e7935f1c90af80aaef82708ca16d` |
| `data/model_pair_best_means.csv` | `b115a3f52d43c40d349d06e62684abee357478b61cc931f4c32894178f556d49` |
| `data/model_pair_best_rows.tex` | `4de3731c616b262e31532b88a744c3e227af91929d3cfa4c3545957dc804017c` |

The comparison baseline is `6f362603d302d07de6cc33d80c846e1df92efe17`. The entire 292,209-byte case-score CSV equals that committed blob. Its 2,304 rows contain every expected world/seed/arm/representation/readout/head key exactly once. There are 48 distinct cases: 18 observed cases and 30 shuffled-label cases, each with 48 scores. All pair balanced accuracies agree with accuracy within floating-point precision, and every saved training–development gap agrees with subtraction of its two scores.

An independently written standard-library checker uses 70-digit Decimal arithmetic on the CSV strings. It does not import or execute the new summary generator or scientific code. All **268 checks pass**. The new 96-row mean table reconciles all 576 seed/mean/minimum/maximum cells; the 24-row ranking table reconciles all 120 numeric cells and every winning label. Maximum discrepancy is `3.34e-16` percentage points, within the declared 17-significant-digit CSV serialization. The generated six-row LaTeX table matches independently constructed text exactly. There are no exact top-mean ties. I inspected the rendered page-2 table and the PDF's extracted text; they display the checked values.

The generator's source authentication, fixed schema/grid, equal weighting of seeds 0–2, unrounded ranking, exact-tie policy and percentage conversion agree with its provenance record. Its input and output hashes and byte sizes match the files. It uses only the authenticated scalar score input for scientific calculations.

The readout-specific conclusions are supported. Native wins the B2 kNN/LDA comparisons and U3 kNN comparison. Time wins B3 and B5 kNN/LDA. Raw wins B3/B5 logistic/SVM; PCA wins every matched readout at Wmid and Wfull. In B5, Time beats both Raw and PCA in every one of the three repeats for kNN and LDA. These seven CEBRA wins among the 24 within-readout comparisons coexist with the manuscript's across-readout result:

| Arm | Highest Raw/PCA mean | Highest CEBRA mean | Difference, percentage points |
| --- | --- | --- | ---: |
| B2 | Raw/logistic 37.96% | Native/LDA 32.87% | 5.09 |
| B3 | Raw/logistic 42.13% | Time/logistic 36.57% | 5.56 |
| B5 | Raw/SVM 59.72% | Time/SVM 46.30% | 13.43 |
| U3 | PCA/logistic 46.30% | Native/logistic 29.63% | 16.67 |
| Wmid | PCA/SVM 68.06% | Time/kNN 47.69% | 20.37 |
| Wfull | PCA/SVM 72.22% | Time/logistic 50.46% | 21.76 |

The difference is calculated from unrounded means, so it can differ by 0.01 from subtracting displayed percentages. These are descriptive rankings on the inspected development construction, as the paper states; the table supplies no validated configuration selection or significance test.

All 2,688 saved matched contrasts reconcile to independent subtraction of case scores, with maximum absolute discrepancy `1e-16` BA. The emphasized control comparisons are correct. The following ranges are minima/maxima of three observed changes and five corresponding shuffled-label changes, respectively, in percentage points:

| Contrast and readout | Mean change | Observed range | Control range | Manuscript interpretation |
| --- | ---: | --- | --- | --- |
| B2→B5 Time/SVM | +29.63 | +22.22 to +36.11 | −9.72 to +15.28 | Every observed change exceeds every control |
| B3→B5 Raw/SVM | +21.76 | +16.67 to +31.94 | −5.56 to +8.33 | Every observed change exceeds every control |
| U3→B3 Raw/SVM | −2.78 | −11.11 to +4.17 | −2.78 to +8.33 | Ranges overlap |
| U3→B3 PCA/SVM | −6.94 | −15.28 to +2.78 | −4.17 to +16.67 | Ranges overlap |
| U3→B3 Time/SVM | +10.19 | +5.56 to +16.67 | −4.17 to +19.44 | Ranges overlap |
| U3→B3 Native/SVM | +3.24 | +1.39 to +5.56 | −11.11 to +6.94 | Ranges overlap |
| U3→B3 Time/kNN | +17.13 | +11.11 to +22.22 | −12.50 to +9.72 | Every observed change exceeds every control |
| B3→Wmid PCA/SVM | +34.72 | +22.22 to +44.44 | −20.83 to +12.50 | Every observed change exceeds every control |
| Wmid→Wfull PCA/SVM | +4.17 | −2.78 to +16.67 | −15.28 to +19.44 | Ranges overlap |
| Wmid→Wfull Time/SVM | +12.96 | +11.11 to +15.28 | −18.06 to +6.94 | Every observed change exceeds every control |

Time's B2→B5 mean increases with all four readouts. Every U3 Raw/PCA SVM observed score exceeds its five control scores. The paper correctly separates that once-only association from the weaker evidence for an improvement caused by repeating assembly. Its range statements refer to sampled controls and do not claim calibrated p-values.

The width summaries reconcile all 32 mean/range rows and repeat counts. PCA and Time have positive mean changes in both width steps with all four readouts. PCA/SVM's final changes are `+16.67, −2.78, −1.39` points: the stated one improving repeat and two declines are correct. Raw/SVM declines in all three final-step repeats. Native/SVM changes are `−36.11, +1.39, +1.39` points, explaining the mean decline despite two small gains; Native's final mean declines with every readout. The interpretation keeps the simultaneous changes in session composition, source support and Native parameterization visible.

The diagnostic tables also reconcile: 216 SVM head rows, all 72 head mean/range rows and all 40 numeric cells of the manuscript's handwritten U3/Wfull table. All 24 U3/Wfull SVM pair training scores are 100%. The three retained PCA/SVM seed-0 confusion matrices contain 243 cells, eight observations per true class and 72 per arm; their count/normalization/score arithmetic agrees. Wfull seed 0 has 64 correct predictions, giving the displayed 88.89%.

The design accounting agrees across scalar exports and the frozen protocol: selected IDs are `9 × sessions × source budget`; training rows are 144 except U3's 27; development has 72 constructed rows. Source reuse ranges and extra-draw fractions are consistent. Independently summing the session/class tables reproduces core/middle/full support of 160/543/912 training and 56/210/365 development sources, with 5/18/41 singleton development pools. The source-mask arithmetic gives `1,277 × 83 = 105,991` possible source–column entries, 5,375 observed entries (5.07%) and 100,616 unavailable entries. These are scalar consistency checks, without reconstructing the neural tensor.

The 48-case accounting is internally consistent: 48 PCA, 48 Time and 48 Native fits plus `48 × 4 × 4 × 3 = 2,304` readout fits give 2,448 fits excluding scalers. Raw standardization is excluded from that fit total. Two CEBRA branches with 1,000 updates per case give 96,000 updates. Four representation reload records per case give 192; two split checks per readout give 4,608. Shared B3 cases contribute once to the unique grid. This arithmetic checks the stated schedule and recorded scalar grid; it does not rerun execution receipts.

The class note's numerical content is preserved. All 27 Markdown table rows equal the baseline byte for byte; the changed numeric prose preserves its values and formulas. The nine frontier rows reconcile with the saved frontier CSV, including the K=10 addition of `4→1`, unchanged 17-column core and 58-column wider roster. Every saved panel satisfies its endpoint-incidence bounds. Marginal totals/ranges reproduce 7,861 training and 3,265 development sources, 236–291/97–122 per pair, and excluded maximum-frequency pair `3→6` at 291/114. The `6/K` endpoint-only ceiling and equal pair accuracy/BA under balanced pair counts are consistent with the declared construction. No selection or metadata function was rerun.

Preservation was checked against the 83 pre-existing tracked files in scope: 18 report data files, 20 figures, 37 experiment source/notebook/published-artifact files, and eight renderer/provenance/protocol/design/panel-verification files. None differs from the baseline. The three new comparison tables are additions and were checked separately. Unrelated working changes were untouched. The final PDF retains the distinction between study-specific exclusion of outer validation/test and historical development exposure.

Two available historical scalar CSVs independently reproduce the October endpoint means (70.28/83.61/63.75/75.56%) and October 23 full-pool means (16.88/13.33/17.08%). The former has CRLF working-tree lines versus LF in Git; normalized content is identical. Earlier marker audits, fit/reload/array-equality receipts, November 10–11 historical results and the Raw/Time class-error summaries remain inherited evidence. This review preserves their source artifacts and checks the language's stated scope; it does not claim fresh verification of underlying predictions, arrays or biological provenance.

Fresh work records are `work/language-quantitative-20261116/independent_audit.py` (SHA-256 `e358315aceccb44e159abdbdbad0aed50d422ca08fca1e0a4f2cdfc13df3af4c`), `independent-receipt.json` (`075beba6f7cf14e1cbe7e5b8879a6be64939124034b7faf2edc85626d7753eb3`) and final `paper-layout.txt` (`71b9b4d184f8289cac1ecb7083e2fdc071a0a3574ffe52549c39ed388c72b0c9`). A retained intermediate checker receipt records two checker-assumption corrections: staged additions were initially included in a preservation test, and an unchanged historical CSV used different line endings. Neither was a manuscript or numerical defect.

The practical comparison is understandable: the paper defines the source/row distinction, gives readout-specific CEBRA successes alongside stronger complete Raw/PCA combinations, and states the repeated-development and known-label-construction prerequisites adjacent to the conclusions. **No quantitative revision is requested for the reviewed hashes.**
