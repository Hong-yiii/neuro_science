# UROP cover, trained CEBRA figures and appendices — November 16, 2026

**Complete: three fresh independent AI-agent reviews return PASS / UNDERSTANDABLE,
with no required revisions.** The delivered PDF has 24 A4 pages: an unnumbered
cover and 23 numbered report pages, with 16 figures and 11 tables.
[PR32](https://github.com/Hong-yiii/neuro_science/pull/32) remains open against
`main`.

## Change and evidence

The cover follows the supplied UROP sample and names **Lin Hong Yi**, **Semester 1,
AY 2026/2027**. The project title is **Evaluating CEBRA for Hippocampal Cue Decoding:
Effects of Trial Sampling and Population Construction**. The institution block
uses the wording in the sample. PDF title and author metadata agree with the cover.

Printed pages 13–14 show four trained CEBRA examples, each paired with its own
1,000-update training-loss curve. The examples are CEBRA-Time at two and five
sources per session/class with 17 columns, followed by Time and native multisession
CEBRA with 49 columns. All use observed seed 0. This selection follows the
source-budget endpoints and the first wider walkthrough case. It illustrates
the design without claiming to represent variation across repeats.

Each 3D view shows the saved development class means in coordinates 1–3 of a
seven-coordinate encoder. Each class mean averages eight constructed rows at each
of ten cue bins. Circle/cross markers identify the 50/950-ms bin centers. The
figures use equal coordinate spans within each panel, independent limits between
panels and a fixed orthographic camera. No projection, alignment, normalization
or smoothing was added. Native averages corresponding session outputs before
forming the class mean. The text distinguishes class-mean appearance, training
objective progress and development decoding performance.

The new curated input copies **1,080 coordinates and 4,000 loss values** from
authenticated original delivery JSON records. The original study ledger pins the
delivery manifest; that manifest binds all four source files. The original
geometry/loss PNGs also match the reviewed published notebook images. The numeric
traces come from the saved JSON records. Their values were compared exactly by
the independent scientific and quantitative reviewers.

The former measurement/construction and numerical-check sections now appear as
Appendices A and B on printed pages 21–22. Their bodies match the preceding
version exactly after allowing the added appendix labels. This preserves their
tables, original first-case learning figure, values, citations and limits. The
main controls section summarizes the checks and points to both appendices.

## Checks and independent review

The [fresh review panel](audit/README.md) assessed the final artifact without the
drafting transcript, author/probe memos, prior audit findings or one another's
reports. The newcomer compared the cover with the supplied image and inspected
the geometry, controls, appendix and reference pages. The scientific reviewer
checked source definitions, saved aggregates, construction counts and claim
boundaries. The quantitative reviewer checked all 5,080 copied values, plotted
artists, source identities, deterministic regeneration and preservation. These
are scoped AI artifact audits of this revision. Earlier full-paper and execution
reviews retain their original artifact identities.

Tectonic 0.17.0 builds the final PDF with 45 embedded fonts and no warnings,
unresolved references, duplicate anchors or bad boxes. An isolated archive of Git
tree `fa2b98e592f895e72fbf42998bb88291c43edce5` contains only the TeX, Makefile,
figures, geometry renderer and curated aggregate input. It reproduces both new
PDF/PNG pairs and their provenance byte for byte, then builds a complete PDF with
identical extracted text. The delivered PDF remains the reviewed original build.
The renderer passes Ruff. All 33 pinned repository paths resolve.

| Delivered artifact | SHA256 |
| --- | --- |
| `paper.pdf` | `2d1b9efe6b370ae631c5888c2b4261646449d049ef11d8dac3f347f960c390d7` |
| `paper.tex` | `0dc9d74a49bf2fa994df46ef33e0cd3f71c260b24bc1c7f1adf9afed9bec4aea` |
| `data/cebra_geometry_examples.json` | `82838f544adcb15ba60517cc7b2cc196965d38fd4f686194c2edbf77eba4e67c` |

The [artifact checks](audit/geometry-artifact-checks-20261116.json) record the
build, preservation, pinned links and reviewer hashes. The
[geometry provenance](geometry-figure-provenance.json) binds the original
sources, curated input, renderer, exact plot limits and generated figures.

## Preservation and limits

All 97 pre-existing files in the protected evidence scope match baseline
`414496280088f9400114938c3b9ad65e417f82c2`: report data/figures and generators,
study implementation, source/executed notebooks and study records. All 28 earlier
detailed audit/check files remain unchanged. The
[preceding overview validation](validation-overview-20261116.md) and
[its audit index](audit/overview-index-20261116.md) are exact copies of the previous
current ledgers. They retain the earlier full-language, class-panel and methods
reviews and their original hashes.

This revision reads saved aggregate geometry and loss. It performs no fitting,
model loading/replay, neural-observation or individual-feature-array read,
notebook execution or metadata optimizer rerun. The completed 48 cases, original
outputs and failures remain preserved.

The existing development-utilization, acquisition/task-context, spatial-evidence,
PDF-accessibility and cross-version limits remain. The PDF is untagged; a full
grayscale/print audit is outside these checks. The cover was checked against the
provided sample; broader institutional formatting requirements were not assessed.
Known-label assembly, shared sessions, dependent sources and inspected development
data still constrain interpretation. Class-mean geometry leaves individual-row
overlap unshown. Loss curves alone establish neither decoding quality nor
convergence.

The unrelated `src/neuro/_cebra_sampling.py` edit remains at SHA256
`63489315c5a21257ed037edd77161f639beb23199321719d8fe22a562c1659f5`.
Untracked `docs/reports/current-state-20260927/` is excluded. This publication
update leaves the PR open for review.
