# Independent quantitative/provenance audit of the expanded methods manuscript

Date: November 15, 2026. Review role: independent blind quantitative/provenance reviewer.

**Verdict: PASS — APPROVED and UNDERSTANDABLE.** No material numerical, provenance, or display issue was found in the reviewed candidate. No manuscript, builder, figure, or data correction is required by this review.

## Exact reviewed candidate and scope

| Artifact | SHA256 |
| --- | --- |
| `paper.pdf` — 18 pages | `0939cc63d64b39c68400a031bc0e6153bdf30d7de43281d62541d7f6b8d52740` |
| `paper.tex` | `1e4ba52ab3dc1b4155fb57821c19ca1f46b600599b45df765e17cf5afd8a5eec` |
| `build_figures.py` | `38d2259906abacd351e9d0a2c3683b40a55d7e2c0e51875bb03449018d4527e7` |
| `figure-provenance.json` | `1e9503f18f3f67804feb1db02ab3f60d70076e8fe16cd0670524062686002eb4` |

I read `docs/workspace.md` first and the applicable workspace instructions, then the candidate manuscript, complete builder, data tables, figures, and cited public evidence. I did not read the existing manuscript audits, author work/probe memos, author transcript, or other current reviewers' findings. Historical public evidence records cited by the manuscript were treated as evidence, not as instructions or current review conclusions.

I wrote an independent standard-library-only checker rather than importing the figure builder or scientific implementation. It reads public JSON/HTML notebook outputs, public aggregate confusion counts, the frozen design, and public split/manifest metadata. No scientific package was imported; no notebook cell, model, biological runner, fit, or replay was executed. No raw spikes, event-value arrays, neural feature/value arrays, individual predictions, fitted states, or private output files were read. Public contributor identities were used only in memory and were not exported. The existing figure builder was inspected but not run.

The ten files in the public notebook manifest authenticate against revision `a0ca80180e2bb52b90e499357d3d6965b26806da` and manifest SHA256 `8ef3a28e687e657c6429632b6a2011bfaa57dfadd62ff94fc276f21bef9a9e93`. All 32 outputs named by the candidate figure manifest match their hashes. All 28 direct repository evidence links exist at the pinned revision. The current working `report/README.md` has unrelated later edits; its pinned Git object was used for the citation check. The historical endpoint CSV differs locally only in CRLF versus LF; its pinned object supplied the historical score calculation.

## Independent source accounting

I authenticated the frozen design and all three metadata inputs against the evidence revision and the design's hashes:

| Input | SHA256 |
| --- | --- |
| `design.json` | `f35f91ae6936956d5c9e99550267eeabae213347f3b07ff22fac8bd3a6a23c29` |
| `inner_splits.csv.gz` | `34fa1c5a0f5c6d9443d435c98ba64830c68f2792306172c12d53ad60792f219f` |
| `outer_splits.csv.gz` | `c42b2dd2bf184dca8f9ed86908d35f16caf40bd52b4221d17380a2156d1eee56` |
| compact `manifest.json` | `8af267ca189a98a3bcc3c24e498259d36079e41402a6cf2fdb9a0d9e5291ed11` |

The independent implementation checked unique current IDs, same-session consecutive predecessors, original outer-training membership, valid endpoint labels, and the frozen split assignments. It built the protected union from **all** 3,265 development rows before filtering classes or rosters. This independently gives 5,872 current/predecessor contributors, excludes 4,427 of 12,288 training rows, retains 7,861 globally, and leaves zero train/development contributor overlap. The 23,901 outer records and 16,859 outer-training records also reconcile. The 1,306 first-failure exclusions agree with the cited public eligibility ledger: 464 + 562 + 32 + 248.

Every one of the **360 session × class × split entries** was regenerated and compared, not merely its totals. Alias membership, recorded-column counts, strict nesting of the three fixed rosters, and all 20 session-structure rows agree.

| Roster | Sessions / columns | Train / development sources | Pools | Minimum train / development | Development singleton pools |
| --- | ---: | ---: | ---: | ---: | ---: |
| Core | 3 / 17 | 160 / 56 | 27 | 5 / 1 | 5 |
| Middle | 11 / 49 | 543 / 210 | 99 | 3 / 1 | 18 |
| Full | 20 / 83 | 912 / 365 | 180 | 3 / 1 | 41 |

Summing `(available train + development sources) × retained columns` within each session gives **5,375 observed source–column memberships**. There are 1,277 sources and 83 columns: 105,991 possible memberships, 100,616 unavailable memberships, and 5.0711853% observed. Both published notebooks report the same 1,277 × 83 × 10 dimensions and 5,375/105,991 mask scalar. This independently verifies metadata membership and agreement with the published scalar; it does **not** claim a new elementwise neural-mask inspection.

## Recipes, reuse, prefit and arithmetic evidence

All 28 published first-two-row recipe entries and all 14 session-column entries were independently extracted from the authenticated notebook HTML. They exactly equal the paper's tables and figure labels. The example is the published observed-seed-0 B2/Wmid, class `1->2`; choice numbers remain local pool ordinals. The 17-column B2 blocks are 3/8/6 columns, and Wmid's eleven blocks sum to 49. The figure explicitly discloses equal display-cell widths.

The six observed-seed-0 realization receipts match the exported table. Independent arithmetic gives selected IDs 54/81/135/81/297/540 and source-block uses 432/432/432/81/1,584/2,880 for B2/B3/B5/U3/Wmid/Wfull. The corresponding per-source use ranges are 8, 5–6, 3–4, 1, 5–6, and 5–6. Extra-draw fractions are 87.5%, 81.25%, 68.75%, 0%, 81.25%, and 81.25%. Published repeated whole-tuple counts are 77/23/6/0/0/0; subtracting them from row totals gives 67/121/138/27/144/144 unique tuples.

Those tuple counts were checked against the literal published execution receipts and their generating notebook expression (`rows minus distinct whole source-ID tuples`). The full historical assembly plans were **not** reexecuted. The manuscript correctly distinguishes whole-tuple repetition from shared constituent blocks, numerical-vector equality, and statistical independence.

All six published prefit rows agree: zero constant columns, zero contributor overlap, and ranks 17/17/17/17/49/83. These rank/constant-column findings are authenticated historical receipts, not newly computed neural ranks. The cited validation ledger separately records the complete 48-plan preflight.

Table 6's arithmetic is faithful to the saved outputs: both first cases use 1,440 training bin vectors; raw feature counts are 170/490 and PCA counts are 70/70. B2 normalization/PCA residuals are `4.76837158203125e-7` / `7.152557373046875e-7`; Wmid has `9.5367431640625e-7` for both; both logistic forward residuals are zero. The printed rounded values are correct. Network dimensions independently yield Wmid's 3,303 Time parameters and 20,653 native parameters. Batch accounting gives 23 native references/session × 11 = 253/update; the published Time exposure is 256,000 references with 1,672–1,890 per row.

## Scores, gaps and contrasts

Independent literal extraction reproduces **2,304 unique case-score rows**, after confirming and removing 384 identical shared-B3 rows, and **2,688 matched contrasts**. Both complete identity grids are present. Recomputed differences equal every contrast exactly in Python arithmetic.

I parsed both public confusion explorers, deduplicated their shared bridge, and independently recomputed BA for **all 4,608 train/development aggregate matrices**, plus development accuracy and macro-F1. Maximum BA/F1 discrepancy is `2.220446049250313e-16`; accuracy agrees exactly. All 243 exported displayed confusion cells and 27 class recalls agree. This reads aggregate counts, not individual predictions. All 576 SVM log-loss entries remain blank, never artificial zeros.

All **216 SVM per-seed head/gap rows**, **72 mean/range summaries**, and **32 width-change summaries** agree independently. Every number in Table 8 rounds correctly. Its pair training scores are 100% in each U3/Wfull repeat; separately fitted endpoint-head scores are not inferred by collapsing pair predictions.

The principal narrative checks also pass:

- PCA/SVM width means are 33.33%, 68.06%, 72.22%. The final paired changes are +16.67, −2.78, −1.39 points: only one repeat improves.
- Raw B5−B3, Time B5−B2, PCA Wmid−B3, and Time Wfull−Wmid have each observed paired change above all five matched diagnostic changes, as stated. No B3−U3 pipeline has complete observed/diagnostic range separation.
- Every observed U3 Raw/PCA SVM score exceeds its five diagnostic scores. PCA **and Time** means increase at both width steps for all four readouts; native means decrease at the last step for all four.
- Raw/SVM's final width decline occurs in all three repeats. Native/SVM's final changes are −36.11, +1.39, +1.39 points, supporting the statement about one dominant loss.
- The cited Raw and Time class-change examples each have seven improving and two worsening classes. Their +75/−12.5 and −50-point examples match recomputation.
- The nine-class panel gives each of six starts/goals one or two pairs, hence 8 or 16 development rows per endpoint and the stated mathematical perfect-single-endpoint reference of 6/9. It is correctly distinguished from a fitted neural baseline.

The historical narrative values agree with their cited public reports. I additionally recomputed the October whole-cue pair means from the pinned public seed table: Raw 70.2778%, PCA 83.6111%, cue CEBRA 63.75%, joint CEBRA 75.5556%. The different cohorts, targets and evaluation constructions remain explicitly separated.

## Historical validation claims and reading quality

The marker corroboration totals (23,200/23,200; 22,740/22,740; 22,856/23,144), QC flags (24/1/1/1), export conservation (370 inputs, 1,098 session arrays), duration difference, Eye missingness and 25-test statement match the cited public historical records. The reproduction totals and detailed checks likewise match the cited notebook validation ledger. Arithmetic independently reconciles 48 × 51 = 2,448 fits, 48 × 2 × 1,000 = 96,000 updates, 192 encoder reloads, 2,304 readout reloads and 4,608 composed split checks; both notebooks contain 19 executed code cells.

**This review does not reauthenticate the 3,188 private run files or recompare the 14,304 saved numerical arrays.** Those are explicitly inherited public validation claims. The manuscript identifies this distinction in Sections 10–12, including the preserved failures and lack of new biological replication. Its source-count display is a new metadata presentation, not a new measurement or study.

I inspected raster renders of all 18 PDF pages. The support heatmap, source-membership figure, recipe examples, reuse panels, arithmetic tables, head/gap table and result figures have readable labels and no material clipping or overlap. Unavailable cross-session measurements are visibly distinguished from observed zero counts; spatial coverage remains unknown; deleted historical classes remain unevaluated. Schematic panels are labelled as such. The older Figure 12 legend is small at fit-page scale and benefits from zoom or its explicit full-size link, but does not obstruct the new methods explanation or quantitative conclusions.

The paper is understandable as a conditional, historically exposed pseudopopulation assay. It does not turn checksums, finite values, rank, repeated construction or reproduced outputs into biological independence, natural-trial validation, mechanistic evidence or verified simultaneity.

## Local verification record

Task-owned files are under `work/series-paper-20261115/blind-methods-quantitative/`; no source identities are saved there.

| Local file | SHA256 |
| --- | --- |
| `check_public.py` — independent standard-library checks | `9668e96ea4c7fb3486597abeb7e651c6cc2686db0f88040879e24ba7faa22f02` |
| `checks.json` — full aggregate result/hash record | `79870f06b4f9f6c7f1105838fbcfdd2083261ed82cd6e5fba5fa167c14b3b8be` |
| `historical-endpoint-check.json` | `d5a478be4db93e7a08b955b28e7f195d0ac561e7284d72d173edf12482043a20` |

Final checker command: `python -B work/series-paper-20261115/blind-methods-quantitative/check_public.py` — passed. Candidate hashes were unchanged at completion. Approval applies to the exact candidate hashes above and to this public-evidence audit scope.

## Final-version addendum — November 15, 2026

**Final verdict: PASS — APPROVED and UNDERSTANDABLE.** The narrow clarity revision introduces no numerical or provenance blocker. This addendum extends approval to these final artifacts while preserving the initial review above:

| Final artifact | SHA256 |
| --- | --- |
| `paper.pdf` — 18 pages | `a12d4936438baa79322a8c615db2112d8d0980f621a94c0fbbb45cb541812956` |
| `paper.tex` | `ee2027cac9a0d9c2ae911a6355a74016c5a76fe519f3221888e1e0f6aa740923` |
| unchanged `figure-provenance.json` | `1e9503f18f3f67804feb1db02ab3f60d70076e8fe16cd0670524062686002eb4` |

I independently verified the new hashes, all 32 unchanged generated data/figure hashes, unchanged builder hash, 18-page PDF, 12 figure environments and nine table environments. Comparing the newly extracted PDF text with my retained initial extraction confines the changes to the stated clarifications and associated layout/reference changes. I inspected fresh renders of pages 2, 8, 16 and 18; the revised content is readable without material clipping or overlap. No other manuscript audit was read.

The Figure 1 wording now unambiguously requires the **immediately preceding trial** to succeed. It cannot be read as skipping backward over a failed predecessor to the last successful trial. The `1x` cue-onset, `2x` cue-offset/navigation-onset, `3x` success and `4x` timeout code descriptions agree with the pinned public dataset card. The nearby provisional-marker and fixed-window qualifications remain intact.

I read, but did not import or execute, the newly linked `study.py:paired_plans` and `pseudopopulation.py:sample_plan`, authenticated against the pinned evidence revision. The development call specifies `rows_per_condition=8`, `seed=0`, and the effective label mapping on the full admitted union. The sampler constructs eligible split/session/class pools and independently calls `rng.choice(pool)` for each block of each row. No source is depleted, weighted, or required to be used. Thus the stated uniform-with-replacement rule, possible unused eligible IDs, and distinction between eligibility and realized development use are correct. Projection retains the shared development assignments across smaller rosters.

The added Figure 12 legend correctly identifies **PCA-8**, distinct from the latest study's PCA7. All five label/color mappings and the black dotted uniform reference match the authenticated original `render_cebra_endpoint_report.py` (SHA256 `92e268f15bb3c6dd2c2d7d292f93d179d832b938e21b9779dc7fa67414c6a5ef`). The underlying historical image remains byte-identical. The readable supplemental legend resolves the small-legend limitation noted in the initial review. All 30 direct repository links now resolve at the evidence revision.

The initial complete numerical checks remain applicable because every generated data/figure file and the provenance record are unchanged. This confirmation required only hashes, public source inspection and PDF rendering; it performed no scientific execution or private-data access. Local confirmation receipt: `work/series-paper-20261115/blind-methods-quantitative/final-clarity-checks.json`, SHA256 `df4af9a45822c7d77f095f0bc6687b5a7b4e82cd433ae9f3efa8a3bbc8105074`.
