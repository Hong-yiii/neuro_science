# Evaluating CEBRA for hippocampal cue decoding

**Effects of Trial Sampling and Population Construction**

Lin Hong Yi · Semester 1, AY 2026/2027 · UROP, National University of Singapore

Read the [paper](paper.pdf) and its [LaTeX source](paper.tex). The 24-page PDF
contains an unnumbered UROP cover and 23 numbered report pages. The synthesis
helps a lab interpret CEBRA's performance under different choices of recorded
sources, population construction and readout. It covers the research series through
November 15, with the November 16 class-panel explanation and language revision.

**Start with pages 1–2.** They define the task and data units, then explain what
improves with more recorded trials, repeated row assembly and larger populations.
The overview describes each comparison in plain language without arm codes or a
score-ranking table. Page 6 names every construction beside its figure code.
The main text includes four saved 3D CEBRA views with their matching training
curves. The detailed measurement and numerical checks are preserved in Appendices
A and B. The result sections retain the exact scores, individual repeats and controls.

The [audit index](audit/README.md) and [validation ledger](validation.md) record
the delivered version and verification scope. Three fresh independent AI reviews
pass the cover, geometry and appendix revision. The report contains 16 figures
and 11 tables.
[PR32](https://github.com/Hong-yiii/neuro_science/pull/32) reviews against `main`
after PR31 merged. PR32 remains unmerged.

## Main findings

- At 17 columns, increasing from two to five recorded training sources per session
  and class raises CEBRA-Time/SVM mean pair balanced accuracy from 16.67% to 46.30%.
  Raw/SVM reaches 59.72% with five sources.
- CEBRA-Time gives higher scores than matched Raw/PCA features with kNN and LDA
  under the five-source construction. Choosing the readout changes the ranking.
- At 49 and 83 columns, PCA has the highest mean with each of the four readouts.
  At 83 columns, PCA/SVM reaches 72.22%, compared with Time/SVM's 48.61%.
- Across each of the six arms, the best Raw/PCA mean among the four tested
  readouts exceeds the best configured CEBRA mean. These are retrospective
  descriptions of the inspected development scores.

Development uses different contributing trials from training, drawn from the same
sessions. Known pair labels are used to assemble each population vector. The
recordings and development results have been examined during the research series.
These facts define the evaluated task and the scope of its performance claims.
The paper states the remaining questions about new sessions, natural trials and
biological interpretation alongside the practical findings.

## Reading route

Page numbers below refer to the printed report numbers, following the cover.

- Pages 1–2: task, terminology, three data-construction comparisons and qualitative
  interpretation for using CEBRA.
- Pages 3–6: data inventory, trial eligibility, contributor separation, history
  and the six fixed constructions.
- Pages 7–11: class-panel feasibility, complete session support, block assembly
  and reuse of recorded responses.
- Page 12: encoder/readout operations.
- Pages 13–14: four 3D views of trained CEBRA encoders, each paired with its
  recorded training-loss curve.
- Page 15: completed controls and their interpretation.
- Pages 16–20: measured results, training/development gaps, endpoint classifiers,
  errors, temporal evaluation and conclusions for using CEBRA.
- Pages 21–22, Appendices A–B: full measurement/construction checks and numerical
  verification.
- Page 23: evidence sources and reproducibility references.

## Evidence and source files

The experimental evidence is pinned at
`a0ca80180e2bb52b90e499357d3d6965b26806da`. The class-panel note is pinned at
`082b5e1a3cb9a87bc22a9ce80006d2e882adc404`; its original metadata verification
receipt and all numbers are preserved. The new representation/readout table
summarizes the public scores from `6f362603d302d07de6cc33d80c846e1df92efe17`.
The existing result tables, figures and completed notebook outputs are unchanged.

- [data/](data/) contains all 2,304 unique score rows, 2,688 matched contrasts,
  source counts, assembly recipes, reuse summaries, endpoint-head diagnostics,
  confusions, model-comparison summaries and the curated geometry/loss examples.
- [build_figures.py](build_figures.py) authenticates the published notebooks and
  metadata, extracts aggregate outputs and renders the existing result and
  construction figures. [Figure provenance](figure-provenance.json) records
  their sources and hashes.
- [build_class_panel_figures.py](build_class_panel_figures.py) renders the recorded
  feasibility receipt. Its [provenance](class-panel-figure-provenance.json) binds
  the full pair grids and class-count frontier.
- [build_geometry_figures.py](build_geometry_figures.py) renders the four saved
  CEBRA examples from the curated aggregate input. Its
  [provenance](geometry-figure-provenance.json) records the original delivery
  hashes, case selection and plotting choices. Each view shows development class
  means in coordinates 1–3 of a seven-coordinate encoder; each loss curve belongs
  to that same fitted model.
- [summarize_model_comparisons.py](summarize_model_comparisons.py) reads the
  authenticated scalar score CSV. It writes 96 representation/readout means
  with all three seed values and ranges, 24 within-arm rankings and an accompanying
  LaTeX ranking table. [Comparison provenance](model-comparison-provenance.json) states
  the exact arithmetic, tie handling and interpretation.
- [Class-panel study explanation](../../docs/experiments/source-reuse-width-20261114/class-panel-20261116.md)
  gives the complete distribution tables and selection rationale.
- [Current reviews](audit/README.md) and [validation](validation.md) record the
  appendix and geometry revision. The [preceding overview validation](validation-overview-20261116.md)
  and [its reviews](audit/overview-index-20261116.md) retain their original artifact
  identities. Full language and class-panel reviews remain linked from those ledgers.

The accompanying ranking table reports mean rankings after inspecting the completed
study. It supplies a benchmark set for further evaluation. Seed ranges describe
computational variation. They provide no estimate of biological uncertainty.

## Build

From this directory:

```sh
make TECTONIC=/path/to/tectonic
```

Tectonic 0.17.0 builds the PDF from the TeX and committed figures. First use may
download the TeX/font bundle. The numerical ranking tables are preserved alongside
the paper. To regenerate only those scalar summaries:

```sh
make comparisons
```

To redraw the geometry and matching loss curves from the committed aggregate
input, without the original run directories:

```sh
make geometry-figures
make TECTONIC=/path/to/tectonic
```

The summary uses Python's standard library and rejects a changed input identity.
The `geometry-figures`, `figures` and `class-panel-figures` targets use Python,
NumPy and Matplotlib. Their numerical evidence stays pinned. These rendering
workflows fit no models and execute no notebooks.

Reproducibility claims apply to the recorded software environment. TeX timestamps
and cross-version plotting changes can alter binary hashes; reviews identify the
actual delivered PDF. The [earlier follow-up](audit/followup-20261116.md) retains
its remaining development-utilization, task-orientation, accessibility and
cross-version limitations. The current PDF remains untagged and the historical
time figure retains its full-size link for zoomed reading.
