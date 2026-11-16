# CEBRA interpretation and language revision — November 16, 2026

Status: **complete — all three fresh independent AI-agent reviews pass and find
the final 21-page manuscript understandable**. The revision explains the measured
results for a lab considering CEBRA, defines prerequisites before using them and
states practical takeaways directly. [PR32](https://github.com/Hong-yiii/neuro_science/pull/32)
reviews against `main` after PR31 merged and remains unmerged.

The exact preceding [20-page validation](validation-pre-language-20261116.md)
and [class-panel audit index](audit/class-panel-index-20261116.md) are preserved.
Earlier reviews remain attached to their original artifacts.

## What changed

The paper is now titled **Evaluating CEBRA for hippocampal cue decoding**. Pages
1–2 introduce the task and measurement units, then compare the tested constructions,
representations and readouts. The results explain three distinct comparisons:

- Adding distinct training sources improved the configured CEBRA-Time pipeline.
- With five sources per session/class, Time outperformed matched Raw/PCA features
  with kNN and LDA. The readout changes the ranking.
- PCA had the highest mean with all four readouts on the 49- and 83-column
  populations. Across all six arms, the best Raw/PCA mean among the tested
  readouts exceeded the best configured CEBRA mean.

These are descriptive comparisons of the completed development scores. The
paper preserves the same-session evaluation, known-label assembly, historically
inspected development data and computational-repeat limits. The methods explain
how class support, session inclusion, source budgets and repeated assembly shape
those comparisons. Mixed seed-level changes and negative results remain explicit.

The class-panel study note received the same prerequisite and language treatment.
Its numeric-token sequence, all 27 Markdown table rows and code blocks remain
unchanged. The note is pinned at `082b5e1a3cb9a87bc22a9ce80006d2e882adc404`.
Experimental evidence remains pinned at `a0ca80180e2bb52b90e499357d3d6965b26806da`.

## Saved-score summary and numerical checks

The new [summary script](summarize_model_comparisons.py) authenticates
`data/case_scores.csv` against commit `6f362603d302d07de6cc33d80c846e1df92efe17`
and its SHA256, then verifies the full 2,304-row schema and case grid. Its scientific
input is this existing scalar CSV. It selects the 288 observed pair scores and
uses exact rational arithmetic on their decimal strings to calculate 96
representation/readout means, seed values and ranges. It also writes 24 rankings
and the six-row LaTeX table. Rankings use unrounded means and retain exact ties.
The [provenance record](model-comparison-provenance.json) specifies the selection,
precision, outputs and interpretation. Regeneration produced identical bytes;
Ruff passed for the new script.

The independent quantitative reviewer used a separately written standard-library
checker, without importing or executing that generator. All **268 checks passed**:
the 96 summary rows, 24 rankings, all 2,688 saved contrasts, width/head/confusion
arithmetic, source accounting and preservation. The scientific reviewer separately
reconciled all means and winners. These checks verify saved scalar arithmetic and
its interpretation. Historical array-equality, fit/reload and acquisition claims
retain their original evidence and review scope.

No model fit, model load/replay, neural-array read, notebook execution or study
rerun occurred. The metadata optimizer and its verification were not rerun for
this language revision. The earlier metadata-only verification remains recorded
in the preceding validation and class-panel receipt.

## Build and visual checks

The final paper has **21 A4 pages, 14 labeled figures and 11 tables**. Tectonic
0.17.0 builds it without warnings, unresolved references or bad boxes. All 21
pages were rendered. The independent newcomer read the entire paper and inspected
pages covering every figure; the scientific and quantitative reviewers inspected
their relevant pages. The historical time figure retains a full-size link for
zoomed reading.

An isolated archive of Git tree `e1190ecff6f981725c414671b336c87b58f99658`
contained only the TeX, Makefile, comparison-table macro and committed figures.
It rebuilt successfully with identical extracted text. That build required no
scientific runtime or notebooks. All **40 fonts are embedded**; all **33 pinned
repository paths** resolve at their stated revisions. TeX timestamps can change
PDF bytes between builds. Reviews bind the delivered PDF below.

| Delivered artifact | SHA256 |
| --- | --- |
| `paper.pdf` | `d99b2d02cc25f15e6d5354ff684f376441563e159d8b23c49ddb6f8e5d6b27f5` |
| `paper.tex` | `088d75baa04f4cf29fbb7b496fe09641c71a79d2c4042683d09ff1feaf9e2353` |
| `model-comparison-provenance.json` | `d691b4caa7f8b4738c700d28155a6d9f175e87ff11b4cd709ad9879de82719d8` |
| Unchanged class-panel metadata receipt | `8f6560aa172c86a53f211596bce9333ee410281210f2c518ad3a8503a572316a` |

## Independent review

Three fresh agents reviewed the artifact and primary evidence without the
drafting transcript, author-side probe memos, prior detailed reviews or one
another's findings. The author-side researcher was a separate agent from the
final scientific auditor. The [audit index](audit/README.md) links the final
reports, each bound to the hashes above.

All three returned **PASS / UNDERSTANDABLE**, with no material blockers. Two
minor findings were corrected and checked in the final artifact: typography
around the word “worlds,” and a sentence specifying that outer validation/test
records are excluded from this study's fitting and evaluation. The latter now
avoids implying that the archive's outer partitions were historically untouched.

These are independent AI manuscript, arithmetic and readability audits. Their
reports state which historical claims they inherited. External human peer review
and independent biological replication remain separate steps.

## Preservation and remaining limits

All 38 pre-existing report data/figure artifacts, both figure renderers and both
figure provenance files are unchanged from `6f362603d302d07de6cc33d80c846e1df92efe17`.
The quantitative audit additionally checked 83 pre-existing files across report
data/figures, experiment implementation, source/executed notebooks, protocol,
design and panel verification; all are unchanged. The original 48-case results,
notebook outputs and their interpretation boundaries are preserved. New model
comparison tables summarize those existing scores.

[Language artifact checks](audit/language-artifact-checks-20261116.json) bind
source, artifact, build, preservation and review identities. All prior audit files
remain intact. The [earlier follow-up](audit/followup-20261116.md) retains its
remaining development-utilization, physical task-orientation, accessibility and
cross-version figure-binary limits. The PDF remains untagged; a full
grayscale/print audit is outside the recorded checks. Acquisition/spatial
metadata and a fresh prospective evaluation remain needed for broader claims.

The unrelated `src/neuro/_cebra_sampling.py` edit remains at SHA256
`63489315c5a21257ed037edd77161f639beb23199321719d8fe22a562c1659f5`.
Untracked `docs/reports/current-state-20260927/` is excluded. No original output
root, failure record or model state was modified. This publication update leaves
the PR open for review.
