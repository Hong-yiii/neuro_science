# Research-series synthesis — November 15, 2026

Read [the paper](paper.pdf), **From cue activity to defensible condition-level
decoding**. Its [LaTeX source](paper.tex) is editable. The synthesis centers the
November source-support, reuse and width experiments and uses the earlier series
to explain why the questions and evaluation changed.

The expanded **18-page** paper puts its data, source distributions, construction
and completed validity checks before the results. All three original fresh
[blind manuscript auditors](audit/README.md) approve the final version and
explicitly find it understandable. A [November 16 fresh-context follow-up
panel](audit/followup-20261116.md) also returned PASS / UNDERSTANDABLE in all
three roles; its quantitative review's incidental exposure to the old approval
headline is disclosed there. The [validation ledger](validation.md) records
the exact reviewed identities and isolated package build.

Published for review as [PR32](https://github.com/Hong-yiii/neuro_science/pull/32).
PR31 merged into `main` at `ec730ee8d024a959d30520cb9f41bdb98882de81` on
November 16; PR32 now reviews against that merged base and remains unmerged.

This is an exploratory research synthesis of existing evidence, not a new
experiment or biological replication. Work began only after the completed,
independently reviewed experiment appeared as [PR31](https://github.com/Hong-yiii/neuro_science/pull/31).
The evidence cutoff is `a0ca80180e2bb52b90e499357d3d6965b26806da`.
No model fitting, notebook execution, raw-neural reconstruction, model loading or
new literature research is part of this paper. The new source-distribution plots
count authenticated public frozen assignment metadata under the accepted design;
they do not select a new panel or inspect spike/event values.

## Reading the methods

- Pages 2–3: what was recorded, clock units, label derivation, eligibility counts
  and current/predecessor protection.
- Pages 5–8: the fixed design, all 20-session × 9-class support counts, missing
  source–unit entries, actual two-row recipes, source reuse and development
  singleton pools.
- Pages 9–12: model operations, existing label/measurement corroboration,
  preflight results, manual numerical checks, learning curves, controls and
  computational reproduction.
- Pages 13–17: every displayed seed/control, width contrasts, training–development
  gaps, separately fitted endpoint heads, confusions and scientific limits.

The paper has 12 labeled figures and 9 tables. Data plots are distinguished from
schematics. Source IDs, session blocks, constructed rows and optimizer draws have
separate meanings; the paper does not treat them as independent biological trials.

## Contents and traceability

- [paper.pdf](paper.pdf) and [paper.tex](paper.tex): manuscript and source, including
  labeled method diagrams, quantitative figures, source accounting, claims and
  limitations, and pinned evidence references.
- [build_figures.py](build_figures.py): authenticates the two published notebooks,
  manifest, fixed design and public split metadata. It extracts aggregate tables,
  independently repeats the declared global embargo for source-count displays,
  deduplicates shared B3 records and draws figures. It never executes notebook
  cells or imports scientific study code.
- [data/](data/): all 2,304 unique development score rows and 2,688 matched
  contrasts; 360 session/class/split source counts; complete displayed recipe and
  reuse evidence; 216 observed SVM head rows and 72 summaries; arm, width and
  confusion tables. No neural features, fitted states, per-example predictions
  or full source lineage are exported.
- [figure-provenance.json](figure-provenance.json): source hashes, exact extraction
  locations, figure identities and deterministic output hashes.
- [audit/](audit/): independent manuscript audit records and reviewed identities.
- [validation.md](validation.md): scope, rendering/numeric checks and publication
  status for this synthesis.

The displayed Wfull confusion uses the predeclared seed 0. It happens to be the highest
Wfull PCA/SVM repeat (88.89%); it is labeled as a high-score illustration. The
main score figure retains all repeats, including the two that worsen in the final
PCA width step. The [full-size historical time figure](figures/historical_time.png)
is an unchanged public image from a distinct 195-unit cohort, with its own source
counts and interpretation. The paper adds a readable external legend and links the full-size source from
the PDF caption. The first-case Wmid image is also retained unchanged; LaTeX
crops its two learning panels for larger printed labels, as the caption states.

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
identities instead of silently updating the paper's evidence. Its figure-PDF
metadata is fixed to support repeatable hashes under the recorded software
environment; cross-version binary identity is not promised. In the November 16
follow-up, all 16 numeric CSVs were byte-identical under different Python,
NumPy and Matplotlib versions, while some figure binaries changed without a
numerical or meaningful visual difference. The TeX PDF's own build timestamps
can vary, so the audit binds the delivered PDF and source hashes, not a claim of
byte-identical TeX output across machines.

The requested three-persona audit panel consists of separate AI agents: a newcomer,
an experienced neuroscience researcher and a quantitative/provenance reviewer.
The expanded-methods review used three fresh contexts with no drafting transcript,
evidence-probe memos, old approval records or other reviewers' findings. The
November 16 follow-up repeated those roles and boundaries; its quantitative
blinding limitation and the remaining transparency/accessibility gaps are
recorded in the [follow-up synthesis](audit/followup-20261116.md). These are AI
manuscript checks, not external human peer review. Publication required all
three original reviewers to pass and explicitly find the paper understandable.
PR32 remains unmerged after the follow-up update.
