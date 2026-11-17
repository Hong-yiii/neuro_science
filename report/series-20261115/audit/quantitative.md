# Independent quantitative and provenance audit

November 15, 2026. Reviewer: a separate AI agent acting as the quantitative/provenance auditor. This is an independent manuscript audit, not external human peer review.

**Verdict: PASS. Understandable: yes — UNDERSTANDABLE.**

The paper explains the construction, counting units, comparison arms and metric sufficiently to follow its numerical conclusions. Its main positive claims retain the relevant negative results and limitations. No blocking quantitative, provenance or presentation finding remains for the identities below.

| Reviewed artifact | Independently computed SHA-256 |
| --- | --- |
| `paper.pdf` | `6a3848d795668a8454041da003a416568a6eaff516cd11fbea44f7197ea76c1d` |
| `paper.tex` | `30feff7d23c66ce1fc4387b1318d6cecfc0a801bfcecc0f15960104380d95f3e` |
| `build_figures.py` | `21ce256d8c038493e07a037a1557fdf10a0242e5aebdc45592e3cf5f818f79f9` |
| `figure-provenance.json` | `dcd8b2ea83e5c83baa1c63cdd8bd501e7e1c38bedddd447de159e1247423e6d5` |

Evidence revision: `a0ca80180e2bb52b90e499357d3d6965b26806da`. Manuscript hashes were checked at the beginning and end of this review.

**Independence and access scope.** I read the manuscript, renderer, provenance, published executed notebooks, existing aggregate CSVs and pinned study records. I did not read the authors' drafting transcript, evidence-probe memos, the synthesis's author validation record, or the other manuscript auditors' reports. I wrote a separate HTML/table parser and numerical checks without importing the figure producer. I then inspected the producer and ran it separately with its output directory redirected into reviewer-owned scratch space. No manuscript or delivered figure was changed. No notebook cell, model fit, model load, prediction replay, raw reconstruction, neural-array read or literature search was performed.

**Verified quantitative scope.**

- Both published notebooks and their publication manifest match the pinned Git bytes and recorded SHA-256 values. Extraction locations, HTML hashes and the confusion explorer's decoded document hash match the provenance file. The extractor preserves every published score/contrast cell as text. It rejects conflicting duplicate identities.
- Independently extracted 2,688 score rows reduce to exactly **2,304 unique rows**, removing **384 identical B3 rows**. The identity grid is complete: six arms × eight seed/world combinations × four encoders × four readouts × three heads. There are **2,688 unique matched contrasts**, covering all seven declared comparisons. Every contrast equals the corresponding saved after-minus-before balanced accuracy; maximum discrepancy is **zero**. All train–development gaps also reconcile.
- Independently parsed both public confusion explorers: **4,608 unique aggregate matrices** after removing 768 identical shared matrices. For every matrix, I checked integer nonnegative counts, labels, dimensions, and totals. Development totals are 72; training totals are 144 except U3's 27. Recomputed development balanced accuracy, accuracy and macro-F1, and training balanced accuracy, agree with the complete score table. Maximum balanced-accuracy difference from floating-point representation is **1.11 × 10⁻¹⁶**. This calculation uses aggregate matrices, not per-example predictions.
- The three retained PCA/SVM seed-0 confusion matrices and their 243 count/normalized cells and 27 class recalls agree with their notebook originals. Every pair row contains eight constructed observations. The displayed Wfull matrix has **64/72 correct**, hence **88.8889%** balanced accuracy; each row sums to 100% after normalization. Its selection as the highest Wfull PCA/SVM repeat is accurately disclosed.
- All 32 width-summary entries, means, extrema, positive/zero-repeat counts and percentage-point conversions reconcile. All stated latest-study source counts, roster sizes, training-row counts, source multiplicities, eligible-source counts and singleton-pool counts match the published construction tables. The model schematic agrees with the notebooks' displayed network and feature dimensions; native reference counts follow `S × floor(256/S)` = 255/253/240 for 3/11/20 sessions.

Selected recomputations illustrate the checked claims; these are not the limits of the table audit:

| Claim | Independent result |
| --- | --- |
| PCA/SVM width means | 33.3333%, 68.0556%, 72.2222% |
| PCA/SVM final paired changes | +16.6667, −2.7778, −1.3889 pp: one positive repeat; diagnostic range overlaps |
| Raw/SVM B5−B3 | +21.7593 pp mean; every observed paired change exceeds every matched diagnostic change |
| Time/SVM B5−B2 | +29.6296 pp mean; same descriptive separation |
| Raw/PCA U3 means | 40.7407% / 40.2778%; each observed score exceeds all five corresponding diagnostics |
| B3−U3, Raw/PCA/Time/native | −2.7778/−6.9444/+10.1852/+3.2407 pp; all four observed/diagnostic ranges overlap |
| Final Raw/SVM width step | All three repeats decline |
| Final native/SVM width step | −36.1111, +1.3889, +1.3889 pp; one large loss dominates the mean |

PCA and Time have positive mean changes at both width steps for all four readouts; native declines at the final step for all four. Raw logistic width means reproduce 42.13/63.43/66.20%. The two post-hoc class-error examples each improve seven classes and worsen two. Raw B5−B2 gives +75 points for `1→4` and −12.5 for `2→5`; Time Wfull−B3 gives −50 for `6→2`.

The sparse-task reference is correct: both start and goal have six distinct categories across nine pair classes. With only perfect knowledge of one endpoint, the sum of attainable class recalls is six, giving pair BA **6/9**. This is a mathematical reference and is explicitly distinguished from a trained neural baseline.

**Historical evidence and computational accounting.** The October endpoint means were recomputed from the pinned seed CSV: 70.28/83.61/63.75/75.56% for raw/PCA/cue/joint with logistic readouts. The October 23 full-pool means independently reproduce 16.88/13.33/17.08%; its 27-unit/10-session and 1,415/551 source accounting matches the published aggregate JSON. The September exact-development Time result recomputes to 299/1200 = 24.9167% over 25 primary entries; the 99.25% training-source-mixture statement matches its pinned completed-study record. November 10's once-only values, diagnostic separation and −9.72/+7.87 pp changes, and November 11's cited roster sequences and population counts, agree with their pinned published report tables. These cohorts remain explicitly separate in the manuscript.

The 48-case grid implies 48 × (3 representation fits + 48 readouts) = **2,448 fits**, excluding scalers, and 48 × 2 × 1,000 = **96,000 updates**. Both published notebooks together contain **38 executed code cells**, with no saved error output. The earlier 3,188-file, 14,304-array and 96-learning-record verification claims match the pinned validation ledger and numeric verification record. This review checks those citations and arithmetic; it does not independently reopen the underlying run files or arrays.

**Figures and PDF.** The reviewed renderer reads only its declared public notebook/manifest/figure inputs, authenticates them, and does not execute scientific code. An isolated invocation reproduced **all 13 delivered CSV and figure files byte-for-byte**. The three new plots are vector PDFs with dimensions 7 × 4.65, 7 × 2.55 and 7 × 3.85 inches; their PNG copies match the stated 220-dpi dimensions. The historical image is an unchanged 2417 × 722-pixel copy of its pinned October source. Its original plotting code uses all ten cue windows, three-seed means and min–max bands, consistent with the caption.

I rendered and visually inspected all **10 A4 pages**, including six figures and three tables. Figure axes, normalization, units, references and cohort captions are coherent; no clipping, missing figure, unresolved `??` or misleading biological interval was found. All 11 explicit LaTeX labels resolve, all 13 citations are defined, and all 22 distinct pinned repository references exist at the cited Git revision and appear in PDF link annotations. No external HTTP availability or new literature verification is claimed.

**Findings by priority.**

- **Blocking/high/medium:** none.
- **Nonblocking presentation note:** Figure 6's inherited legend is small at whole-page viewing size and benefits from zoom. Its readable caption, explicit older-cohort boundary and linked original retain the interpretation; the main new quantitative figures are readable.
- **Nonblocking provenance detail:** the historical endpoint CSV has CRLF line endings in the checkout and LF in the pinned Git blob. Every parsed field is identical. Historical means above were recomputed from the pinned blob; this does not affect any reported number.
- **Scope limits:** log-loss strings were authenticated against the source tables but not recomputed from probabilities; aggregate confusions cannot determine log loss. Seed-0 identity and the disclosed high-score status were verified; the chronology of its predeclaration was not reconstructed from drafting history. Acquisition metadata, biological independence and prior run-file audits are not newly certified here.

The selection disclosures are adequate for an exploratory synthesis: the SVM figure's slice is named, all readouts accompany the width claim, all seeds and diagnostic worlds remain visible, the high-score confusion is labeled, and historical evidence is not pooled as replication. **PASS; UNDERSTANDABLE.**

## Final-version confirmation — November 15, 2026

**Final verdict: PASS. Understandable: yes — UNDERSTANDABLE.**

| Final reviewed artifact | Independently computed SHA-256 |
| --- | --- |
| `paper.pdf` | `dc6ea8e5e2d422657b32ca8001eb706428bb329025fa473c9f75121bda05ba02` |
| `paper.tex` | `2f1630251df8d445e1242b028a72f94e17ce140d9dcae7164f9576c203eb6b1a` |

I independently examined the entire LaTeX diff from the initially audited version preserved at `cd31986`. The changes identify PCA/SVM explicitly in the abstract, define source trial and the successful-after-successful restriction, name plausible endpoint confounds, add a pinned full-size Figure 6 link, and remove the missing-figure placeholder fallback. These changes clarify the already reviewed claims and introduce no new numerical result.

The renderer and provenance hashes remain exactly those recorded above; all 13 delivered figure/CSV files still match their previously audited hashes. The final PDF remains ten A4 pages. I newly rendered and inspected the affected pages 1, 2 and 8: the added prose and link fit without clipping or overlap, and the figures remain intact. The new full-size image link is present in the page-8 PDF annotation and names the existing, previously authenticated image at the pinned evidence revision. There are now 23 distinct pinned repository links, all represented in the PDF and resolvable in that Git revision. Extracted PDF text contains no unresolved-reference markers or draft placeholders.

The direct full-size link addresses the earlier nonblocking legend-size note without altering the historical image. No new finding requires broad recalculation; the original numerical audit and its stated scope limits continue to apply. I did not read other reviewers' files during this confirmation. Final publication/archive-build verification remains the publishing agent's separate check. **PASS; UNDERSTANDABLE.**
