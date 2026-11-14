# Research-series synthesis — November 15, 2026

Read [the paper](paper.pdf), **From cue activity to defensible condition-level
decoding**. Its [LaTeX source](paper.tex) is editable. The synthesis centers the
November source-support, reuse and width experiments and uses the earlier series
to explain why the questions and evaluation changed.

All three [blind manuscript auditors](audit/README.md) passed the final PDF and
explicitly found it understandable. The [validation ledger](validation.md)
records the exact reviewed hashes and isolated package build.

This is an exploratory research synthesis of existing evidence, not a new
experiment or biological replication. Work began only after the completed,
independently reviewed experiment appeared as [PR31](https://github.com/Hong-yiii/neuro_science/pull/31).
The evidence cutoff is `a0ca80180e2bb52b90e499357d3d6965b26806da`.
No model fitting, notebook execution, raw reconstruction, model loading or new
literature research is part of this paper.

## Contents and traceability

- [paper.pdf](paper.pdf) and [paper.tex](paper.tex): manuscript and source, including
  labeled method diagrams, quantitative figures, source accounting, claims and
  limitations, and pinned evidence references.
- [build_figures.py](build_figures.py): reads the two public executed notebooks as
  JSON/HTML, authenticates their bytes, extracts aggregate tables, deduplicates
  shared B3 records, and draws the figures. It never executes notebook cells or
  imports scientific study code.
- [data/](data/): all 2,304 unique development score rows and 2,688 matched
  contrasts, plus the displayed arm, width and confusion summaries. No neural
  features, fitted states, per-example predictions or full source lineage.
- [figure-provenance.json](figure-provenance.json): source hashes, exact extraction
  locations, figure identities and deterministic output hashes.
- [audit/](audit/): independent manuscript audit records and reviewed identities.
- [validation.md](validation.md): scope, rendering/numeric checks and publication
  status for this synthesis.

The displayed confusion uses the predeclared seed 0. It happens to be the highest
Wfull PCA/SVM repeat (88.89%); it is labeled as a high-score illustration. The
main score figure retains all repeats, including the two that worsen in the final
PCA width step. The [full-size historical time figure](figures/historical_time.png)
is an unchanged public image from a distinct 195-unit cohort, with its own source
counts and interpretation. Its small printed legend is also linked directly from
the PDF caption.

## Build

From this directory, using Tectonic 0.17.0 (or a compatible installation):

```sh
make TECTONIC=/path/to/tectonic
```

The PDF builds from committed figures and requires no neural-analysis runtime.
On first use, Tectonic may download its TeX/font bundle. To regenerate the
aggregate figures from the pinned notebooks in a full repository checkout:

```sh
PYTHONDONTWRITEBYTECODE=1 python build_figures.py
make TECTONIC=/path/to/tectonic
```

The figure script uses Python, NumPy and Matplotlib. It rejects changed notebook
identities instead of silently updating the paper's evidence. Its PDF metadata is
fixed so figure hashes repeat. The TeX PDF's own build timestamps can vary, so the
audit binds the delivered PDF and source hashes, not a claim of byte-identical TeX
output across machines.

The requested three-persona audit panel consists of separate AI agents: a newcomer,
an experienced neuroscience researcher and a quantitative/provenance reviewer.
They receive no drafting transcript, evidence-probe memos or other reviewers'
findings before their first verdict. This is a blinded manuscript check, not
external human peer review. Publication requires all three to pass and explicitly
find the paper understandable. No merge is requested.
