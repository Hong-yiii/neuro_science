# Independent scientific language audit — November 16, 2026

**Verdict: PASS. UNDERSTANDABLE: yes.** The revised manuscript gives the lab a supported decision frame: distinguish improvement within a configured CEBRA pipeline, advantage over Raw/PCA with the same readout, and the highest-scoring complete pipeline. Its direct headings and conclusions retain the exploratory evaluation scope and the important mixed or negative results. No scientific revision remains required for the reviewed version.

## Reviewed identity and independence

| Object | Identity / SHA256 |
| --- | --- |
| Final `paper.pdf`, 21 pages | `d99b2d02cc25f15e6d5354ff684f376441563e159d8b23c49ddb6f8e5d6b27f5` |
| Final `paper.tex` | `088d75baa04f4cf29fbb7b496fe09641c71a79d2c4042683d09ff1feaf9e2353` |
| Comparison baseline | Git commit `6f362603d302d07de6cc33d80c846e1df92efe17` |
| Baseline `paper.tex`, read with `git show` | `a3df343e3add19089e7e497d872d4d45eb36aca74ef4a79ddfe65aebe6667d28` |
| `model-comparison-provenance.json` | `d691b4caa7f8b4738c700d28155a6d9f175e87ff11b4cd709ad9879de82719d8` |
| `data/case_scores.csv` | `1661ff9d7b55644d586ad8efb21a440032c23d18f0121767100fd162acb89249` |
| `data/model_pair_means.csv` | `1f0d976f1cd648bdb938d3511dfa5fa34312e7935f1c90af80aaef82708ca16d` |
| `data/model_pair_best_means.csv` | `b115a3f52d43c40d349d06e62684abee357478b61cc931f4c32894178f556d49` |
| `data/model_pair_best_rows.tex` | `4de3731c616b262e31532b88a744c3e227af91929d3cfa4c3545957dc804017c` |
| Class explanation, commit `082b5e1a3cb9a87bc22a9ce80006d2e882adc404` | `172fb39d25af45057f65232e1ef5c16a514df7a7c546be933a894af14da823de` |

This was a fresh independent reading. I read the full current and baseline manuscript source, checked extracted PDF text and the 21-page count, and visually inspected pages 1, 2, 4, 17 and 20. The scope is scientific meaning and readability, with targeted scalar verification; it is not a complete visual-layout audit.

Primary context/evidence consulted: the required workspace and learner context; `docs/analysis-contract.md`; `docs/experiments/source-reuse-width-20261114/protocol.md`; the class explanation at the exact commit above; `docs/reports/population-grid-20261111/error-analysis.md`; and the manuscript's saved scalar tables. The class explanation's working-copy bytes match its pinned commit. I did not consult the report package README, its validation files, other reviewer reports, or the author/rewrite/probe memos. Communications with the author were limited to findings and the resulting two small corrections.

I ran independent standard-library arithmetic on the existing scalar CSV. I performed no model fitting/loading, neural-array reads, notebook execution, metadata optimization, or regeneration of experimental results. Historical statements were checked for preservation against the baseline; this audit does not repeat the historical run-authentication reviews. Only this audit file was written by this reviewer.

## Findings by severity

**Critical/high: none. Moderate: none. Open low-severity findings: none.**

Two low-severity observations were corrected before the final hash binding:

1. Page 1, source line 53: the initial revision left an opening quotation before “worlds” unclosed. The final version renders the term in italics.
2. Page 4, source line 136: “Outer validation/test records remain unused” could suggest a historically untouched archive partition. The analysis contract records earlier V6 test exposure. The final sentence specifies that these records are excluded from this study's fitting and evaluation, consistent with Table 3 and the actual latest-study scope.

I checked both final corrections in the source and refreshed page renders. Reversing only the second correction reconstructs TeX hash `f7bfd4c1b8856e117017536c54ec49d5e83274047ada44feb068e5ca707c6c70`; reversing both reconstructs the initially reviewed hash `9924b5b6617d111ba4e7c4094079dfe18fb77b9d7e91023e677d5fdd86385223`. No additional scientific text changed during that final verification.

## Scientific checks supporting the verdict

**The practical comparison frame is numerically supported.** The source CSV has 2,304 rows and is byte-identical to its baseline-commit version. Selecting observed pair results yields 288 scores: six arms, four representations, four readouts and three seeds. Independent rational arithmetic reproduced all 96 representation/readout means and ranges and all 24 winning-representation records, within `1e-12` percentage points of the saved decimal summaries. Table 1's winners agree throughout.

The complete-pipeline comparison in Section 2 is also correct. The highest means among the four tested readouts are:

| Arm | Best Raw/PCA pipeline | Mean pair BA | Best configured CEBRA pipeline | Mean pair BA |
| --- | --- | ---: | --- | ---: |
| B2 | Raw/logistic | 37.96% | Native/LDA | 32.87% |
| B3 | Raw/logistic | 42.13% | Time/logistic | 36.57% |
| B5 | Raw/SVM | 59.72% | Time/SVM | 46.30% |
| U3 | PCA/logistic | 46.30% | Native/logistic | 29.63% |
| Wmid | PCA/SVM | 68.06% | Time/kNN5 | 47.69% |
| Wfull | PCA/SVM | 72.22% | Time/logistic | 50.46% |

These are post-hoc maxima of means on the inspected development construction. The manuscript labels its rankings as descriptive, states that the seeds share development inputs, and requires fresh evaluation to validate a selected configuration. It supplies no significance claim or claim of universal model superiority. The table also retains Native's matched-readout wins in B2 and U3, so the simpler-pipeline conclusion does not erase every CEBRA advantage.

**The CEBRA improvement statements preserve their actual comparison.** Time's B5 mean exceeds B2 with all four readouts. Its SVM gain is 29.63 percentage points; all three observed gains exceed all five matched shuffle gains. At B5, Time exceeds both Raw and PCA for kNN5 and LDA in every observed seed. Raw/SVM nevertheless scores higher than every configured CEBRA pipeline in that arm. Sections 2 and 16 present all three facts clearly.

**Reuse remains a combined construction intervention.** Sections 6, 11 and 16 explain that changing the distinct-source budget also changes multiplicity and combinations, while U3/B3 changes constructed row count on the same selected source identities. The final manuscript retains U3 Raw/PCA SVM scores above every sampled control; the negative Raw/PCA mean reuse changes; the positive Time/Native changes; and overlap with the control ranges for all four SVM reuse contrasts. The newly highlighted Time/kNN5 reuse gain is supported: every observed change exceeds all five control changes. Development-block reuse and repeated optimization remain explicit. These findings support readout-dependent comparisons without identifying a pure causal repetition effect.

**The width heading is supported by the stated mean comparison.** PCA has the highest mean for every matched readout at 49 and 83 columns. Both PCA and Time have positive mean changes at both width steps with all four readouts. The manuscript retains the essential exceptions: PCA/SVM's final mean gain improves only one seed; its control range overlaps; Raw/SVM declines in all three final-step repeats; Native's final mean falls for every readout. Native/SVM's mean decline is dominated by one large loss, with two small gains. These statements match the scalar source.

**The Native caveats remain substantive.** Sections 12, 14 and 17 retain different supervision, network count, capacity, equal-session pooling and batch allocation; the absence of a matched concatenated pair-supervised comparator and untrained-encoder control; and the lack of a convergence demonstration for 1,000 updates. The prose does not attribute the decline to an individually harmful session or to multisession learning generally.

**Source separation retains its correct evidential level.** Pages 1–4 and 20 distinguish known-label construction, disjoint current/predecessor contributors, shared sessions, serial dependence, reused development blocks and previously inspected development scores. The three seeds describe computation on the same recordings. New-session, subject-level and unknown-label natural-trial performance remain unevaluated. The text preserves incomplete simultaneity/acquisition metadata and the selected-unit sampling limitation. Nothing in the direct headings upgrades these results to independent biological generalization.

**The important historical and measurement distinctions survive.** The revision retains the September 99.25% versus 24.92% source-evaluation gap, limited preprocessing robustness, changed October cohorts, mixed November class/roster outcomes, training–development gaps and class-level regressions. It keeps ordered pairs separate from measured paths; source counts separate from constructed rows; unavailable entries separate from observed zeros; fitted endpoint heads separate from pair-head predictions; and same-window decoding separate from frozen temporal transfer. The endpoint-only `6/K` ceiling remains mathematical task structure. Authenticated spatial maps and the conjunction/path tests remain missing. The November 11 reuse/coverage algebra and lack of individual-session causal attribution are preserved. Reproduction is still confined to the same recordings and seeds.

**The class-selection prerequisites are understandable.** Definitions of class, session, source, pool, panel, roster and width precede the later construction arguments. The source gate requires every selected class in each admitted session. Nine was fixed before choosing pair identities; the wider-class frontier is retrospective metadata feasibility, with the three-source optimum conditional on the five-source optimum. Alternative counts carry no new decoding result. These statements agree with the pinned class explanation and frozen protocol.

The result-first revision therefore improves the lab-facing decision order while retaining the evidence needed to interpret the comparisons. The final manuscript passes this independent scientific language audit at the exact hashes above.
