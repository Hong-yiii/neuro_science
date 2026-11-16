# Evaluating CEBRA for hippocampal cue decoding

Read the [paper](paper.pdf) and its [LaTeX source](paper.tex). The 21-page synthesis
helps a lab interpret CEBRA's performance under different choices of recorded
sources, population construction and readout. It covers the research series through
November 15, with the November 16 class-panel explanation and language revision.

**Start with pages 1–2.** They define the task and data units, then explain what
improves with more recorded trials, repeated row assembly and larger populations.
The overview describes each comparison in plain language without arm codes or a
score-ranking table. Page 6 names every construction beside its figure code.
Pages 16–17 retain the exact results, individual repeats and controls.

The current revision has 14 figures and 11 tables. Three fresh independent AI-agent
reviews—scientific, quantitative and newcomer—passed and found the paper
understandable. The [audit index](audit/README.md) and [validation ledger](validation.md)
bind those reviews to the delivered version and state their scope.
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

- Pages 1–2: task, terminology, three data-construction comparisons and qualitative
  interpretation for using CEBRA.
- Pages 3–6: data inventory, trial eligibility, contributor separation, history
  and the six fixed constructions.
- Pages 7–11: class-panel feasibility, complete session support, block assembly
  and reuse of recorded responses.
- Pages 12–15: encoder/readout operations and completed measurement, numerical,
  reproduction and shuffle-control checks.
- Pages 16–20: measured results, training/development gaps, endpoint classifiers,
  errors, temporal evaluation and conclusions for using CEBRA.
- Page 21: evidence sources and reproducibility references.

## Evidence and source files

The experimental evidence is pinned at
`a0ca80180e2bb52b90e499357d3d6965b26806da`. The class-panel note is pinned at
`082b5e1a3cb9a87bc22a9ce80006d2e882adc404`; its original metadata verification
receipt and all numbers are preserved. The new representation/readout table
summarizes the public scores from `6f362603d302d07de6cc33d80c846e1df92efe17`.
The existing result tables, figures and completed notebook outputs are unchanged.

- [data/](data/) contains all 2,304 unique score rows, 2,688 matched contrasts,
  source counts, assembly recipes, reuse summaries, endpoint-head diagnostics,
  confusions and the new model-comparison summaries.
- [build_figures.py](build_figures.py) authenticates the published notebooks and
  metadata, extracts aggregate outputs and renders the existing result and
  construction figures. [Figure provenance](figure-provenance.json) records
  their sources and hashes.
- [build_class_panel_figures.py](build_class_panel_figures.py) renders the recorded
  feasibility receipt. Its [provenance](class-panel-figure-provenance.json) binds
  the full pair grids and class-count frontier.
- [summarize_model_comparisons.py](summarize_model_comparisons.py) reads the
  authenticated scalar score CSV. It writes 96 representation/readout means
  with all three seed values and ranges, 24 within-arm rankings and an accompanying
  LaTeX ranking table. [Comparison provenance](model-comparison-provenance.json) states
  the exact arithmetic, tie handling and interpretation.
- [Class-panel study explanation](../../docs/experiments/source-reuse-width-20261114/class-panel-20261116.md)
  gives the complete distribution tables and selection rationale.
- [Current reviews](audit/README.md) and [validation](validation.md) record the
  qualitative overview revision. The [preceding full language validation](validation-language-20261116.md)
  and [its reviews](audit/language-index-20261116.md) retain their original artifact
  identities and complete numerical checks. The earlier class-panel records remain
  linked from those ledgers.

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

The summary uses Python's standard library and rejects a changed input identity.
The optional `figures` and `class-panel-figures` targets rebuild the established
figures with Python, NumPy and Matplotlib. Their numerical evidence stays pinned.
Neither rendering workflow fits models or executes notebooks.

Reproducibility claims apply to the recorded software environment. TeX timestamps
and cross-version plotting changes can alter binary hashes; reviews identify the
actual delivered PDF. The [earlier follow-up](audit/followup-20261116.md) retains
its remaining development-utilization, task-orientation, accessibility and
cross-version limitations. The current PDF remains untagged and the historical
time figure retains its full-size link for zoomed reading.
