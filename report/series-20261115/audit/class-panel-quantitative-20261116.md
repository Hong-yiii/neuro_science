# Independent quantitative and provenance audit — class-panel revision

Date: November 16, 2026. Role: fresh quantitative/provenance reviewer.

**Verdict: PASS. UNDERSTANDABLE: yes.** No unresolved high-, medium-, or low-severity finding remains in the reviewed revision. This verdict covers the retrospective metadata addition and preservation of the tracked experimental evidence; it is not a new audit or replication of the biological fits.

I worked independently from the manuscript, its cited metadata/code, the frozen protocol/design, and direct verification. I did not read author/probe memos, earlier audit reports, package README approval statements, or other reviewers' findings. The required workspace/AGENTS authority was read without resuming historical tasks. The only feedback exchanged concerned my own primary-arm wording finding, recorded below.

## Exact candidate reviewed

All SHA256 values below were recomputed locally rather than accepted from the handoff.

| Artifact | SHA256 |
| --- | --- |
| `report/series-20261115/paper.pdf` | `f5a1783a3673ff5a788af8210bfb876e7045fb531d06354f1a248dbd4ba270f9` |
| `report/series-20261115/paper.tex` | `a3df343e3add19089e7e497d872d4d45eb36aca74ef4a79ddfe65aebe6667d28` |
| `docs/experiments/source-reuse-width-20261114/class-panel-metadata-20261116.json` | `8f6560aa172c86a53f211596bce9333ee410281210f2c518ad3a8503a572316a` |
| `report/series-20261115/class-panel-figure-provenance.json` | `dee2b1ccb57194dccd1bbcc8db4650084486a7d7a8a3c6e85191229e76d549b5` |
| `report/series-20261115/build_class_panel_figures.py` | `40243cbff31f396ca1f900ba241d163793d67c794864ece473b08e8cc3bea594` |
| `docs/experiments/source-reuse-width-20261114/verify_class_panel_20261116.py` | `c615e32feaa652d0960fe01d2b9b8ba9b67708ba01a085528c7de5b09f3e16df` |

The PDF has 20 A4 pages. I independently rendered and inspected pages 1, 5, 6, 7, 8, and 20, including both new figures, the exact frontier table, the revised contextual statements, and the separate metadata citation. I inspected the complete LaTeX diff against `5ac3e5a681e0eee3229adc8f36088c1c37906f48`.

## Quantitative reconciliation

I rebuilt eligibility from only `manifest.json`, `inner_splits.csv.gz`, and `outer_splits.csv.gz`. This calculation did not import the study implementation. It checked unique current-source IDs; current/predecessor same-session adjacency and outer-training assignments; all 30 nonself labels; the global development current/predecessor embargo; and recorded unit counts. It reproduced 15,553 inner rows, 5,872 protected contributors, 4,427 excluded training rows, 58 sessions, and 195 columns. Eligible totals are 7,861 training and 3,265 development current-source IDs.

All **90 non-diagonal matrix values** agree exactly: 30 training marginals, 30 development marginals, and 30 single-pair five-training/one-development session counts. The diagonals are unavailable self-pairs, not zero observations. Training marginals range from 236 to 291; development marginals from 97 to 122. The largest training marginal is `3→6`, with 291/114, and that pair is absent from the frozen panel. The figure therefore supports the distinction between plentiful marginal counts and a restricted common-session intersection.

For every returned panel I independently counted the complete all-class gate, session aliases, width, distinct classes, and start/goal degrees. I also solved an independently formulated binary optimization: an aggregate disqualification constraint forces each session indicator to equal its whole-panel gate. This differs from the study's per-bad-pair inequalities. Both width objectives matched at every K, each with zero solver gap:

| Fixed K | Five-source gate: sessions / columns | Three-source gate: sessions / columns |
| ---: | ---: | ---: |
| 6 | 4 / 18 | 29 / 108 |
| 8 | 3 / 19 | 23 / 95 |
| 9 | 3 / 17 | 20 / 83 |
| 10 | 3 / 17 | 13 / 58 |
| 12 | 1 / 8 | 15 / 66 |
| 15 | 1 / 8 | 12 / 51 |
| 18 | 0 / 0 | 10 / 44 |
| 24 | 0 / 0 | 2 / 12 |
| 30 | 0 / 0 | 0 / 0 |

The three-source objective is conditional on the five-source width optimum. Session count is a reported consequence, not the optimized quantity. Inspection of `select_panel()` confirms the fixed cardinality, separate floor(K/6)–ceil(K/6) endpoint bounds, objective freezing, and sequential preference for the first feasible class in lexicographic order. A fresh run of the actual verification script reproduced every complete returned panel and produced JSON identical to the committed receipt. Thus the independent optimizer verifies the two width optima, while original-function reproduction and code inspection verify the exact class-list tie resolution.

At K=9, I separately reconstructed the harmonic-support ordering and the midpoint-prefix selection. The complete core, middle, and full roster objects equal the frozen design: 3/11/20 sessions, 17/49/83 columns, 160/543/912 available training IDs, 56/210/365 development IDs, and 5/18/41 singleton development pools. The five-source core is exactly S16, S27, S34. K=10 adds only `4→1`, keeps that core, and reduces the wider roster to 13 sessions/58 columns. The stated K=12/15 single-session returned optima and the all-30-class failure even at three training sources are correct.

## Arithmetic and interpretation

The manuscript correctly distinguishes a supplied K from optimization of class identities. K=9 is the frozen experimental task; the later frontier does not optimize K, establish that nine is uniquely best, or add decoding results. In particular, K=8 has greater admitted width, and the returned one-session K=12/15 panels do not prove that all alternative panels at those counts are multisession-infeasible. The text retains these qualifications.

The endpoint-only bound is correct. A deterministic start-only rule can recover at most one pair per represented start, hence at most six of K class recalls; pair balanced accuracy is at most 6/K. Goal-only rules have the same bound, and randomization has that bound in expectation. At K=6, each endpoint degree is one, so either endpoint identifies the pair. These are task properties, not observed neural baseline scores.

For the primary arms, 9×16=144 training rows and 9×8=72 development rows give equal true-pair counts, so pair accuracy equals mean class recall. Endpoint frequencies are unequal because the frozen start degrees are [2,2,1,1,2,1] and goal degrees [1,2,1,2,1,2]. Separate endpoint accuracy and balanced accuracy need not coincide. U3 remains the explicit three-training-rows-per-pair control, totaling 27 training rows.

The new claims stay within metadata feasibility. They do not treat counts as independent biological replicates, infer simultaneity, change known-label construction into natural-trial prediction, or infer neural firing sparsity from support sparsity. Development availability enters the gate; the text does not portray it as an untouched test set.

## Authentication, presentation, and preservation

The three metadata input hashes match the frozen design. The study implementation, metadata implementation, shared source-support file, and design match their receipt hashes and the cited `a0ca80180e2bb52b90e499357d3d6965b26806da` source revision. The dated note, verification script, and receipt match their pinned addendum commit `5a9e54cb75efa1ca1e9d1e918fa9defd57967ee4`.

All 30 rows of the new marginal CSV and all nine frontier CSV rows—including every class list, scope label, gate count, and solver field—match the receipt. All six generated file hashes match the new figure provenance, as does the renderer hash. Both new figure PDFs contain no raster image objects. The renderer reads the pinned receipt and makes presentation artifacts; it does not call the optimizer or inspect assignments/neural values.

The rendered matrices preserve the start/goal axes, all exact counts, nine selected-cell outlines, and unavailable diagonals. Captions distinguish single-pair support from all-class eligibility. The frontier marks the executed K=9 task, labels the conditional objective, and gives an exact adjacent table. Text states that the separately selected panels need not be nested. No clipping, overlapping labels, or unreadable figure text was found on the inspected pages. The explanatory sequence from marginals to intersection to fixed-K optimization is understandable without consulting an audit approval.

Against baseline `5ac3e5a681e0eee3229adc8f36088c1c37906f48`, all **34 prior figure/data/renderer/provenance files** are byte-identical. The complete tracked experiment directory, including source and published notebooks, has an empty diff, as do the frozen protocol/design, validation ledgers, and relevant metadata implementations. The manuscript diff adds this context and separate citation without revising experimental scores, arm tables, or conclusions. Ignored private/biological output directories were not opened or re-audited; this preservation finding concerns the tracked artifacts and the absence of any such operation in this audit, not a fresh authentication of every private run file.

## Findings and verification record

- **Low severity, corrected before final review:** the first candidate said “Equal 16/8 train/development rows per pair” without specifying the primary arms. U3 has three training rows per pair. The final reviewed PDF/TeX explicitly says “In the primary arms”; Table 4 continues to give U3's 27 training rows. No data or experimental result changed.
- **Unresolved findings:** none.

Fresh audit evidence is retained under `work/class-panel-quantitative-blind-20261116/`: `independent_check.py`, `independent-check-receipt.json`, `exact-functions-receipt.json`, `authentication-preservation-receipt.json`, `candidate-identities.json`, extracted PDF text, and independent page renders. No fitting, neural-array/model loading, notebook execution, saved-result replay, or modification of completed-case evidence occurred. The audit wrote only its fresh work directory and this report.

**Final determination: PASS; UNDERSTANDABLE: yes, for the exact candidate hashes above.**
