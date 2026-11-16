# Independent scientific audit — geometry and appendix revision

Date: 16 November 2026

Verdict: **PASS**

**UNDERSTANDABLE: yes**

Required revisions: **none within this review scope**.

This review covers the saved CEBRA geometry/loss additions, movement of the former
measurement/construction and numerical-check sections to appendices, and the
scientific consistency of the UROP cover. The comparison baseline is commit
`414496280088f9400114938c3b9ad65e417f82c2`. It is a review of a presentation revision
to completed exploratory evidence, not a new analysis or a fresh validation of
all historical results.

## Final artifact identity

All paths below are relative to `report/series-20261115/`. These hashes were read
from the final files, not copied solely from the handoff message.

| Artifact | SHA256 |
| --- | --- |
| `paper.pdf` | `2d1b9efe6b370ae631c5888c2b4261646449d049ef11d8dac3f347f960c390d7` |
| `paper.tex` | `0dc9d74a49bf2fa994df46ef33e0cd3f71c260b24bc1c7f1adf9afed9bec4aea` |
| `build_geometry_figures.py` | `420d322c80bc9d1ef1edcaf99a8ef393400e0d36af7183b419283ecb82baec4f` |
| `data/cebra_geometry_examples.json` | `82838f544adcb15ba60517cc7b2cc196965d38fd4f686194c2edbf77eba4e67c` |
| `geometry-figure-provenance.json` | `a3b4d5f262a2ad05c4a3eb76f3d65d16d06316c9f7e9174ce9547b14f99f09c0` |
| `figures/cebra_source_geometry.pdf` | `c7873acb28bf0a0b0e2e18878e6e39c563ca0502840e19c776b957c8c320f0ce` |
| `figures/cebra_source_geometry.png` | `b5435653ee27684bf2c5d21c65e99931bda2ea400b57c3d32e9009281718f34c` |
| `figures/cebra_model_geometry.pdf` | `4444458b0fe0beba736ff73ee66413ead872d11ced9668781a3f2d2322d91071` |
| `figures/cebra_model_geometry.png` | `da9b3116c31e0a65c1a39ab37f5db32cfe64da206feff0093e3da1e610316798` |

The renderer, curated-input and four figure hashes also match the final geometry
provenance file. The PDF contains 24 physical pages: an unnumbered cover followed
by 23 main-document pages. Its title and author metadata agree with the cover.

## Independent evidence checks

I authenticated the original delivery manifest against the explicit pin in
`docs/experiments/source-reuse-width-20261114/validation.md`:
`85e05fa820232245f37332e38bb70155507e869f1da69f0abb0d98cd1b4a0b37`.
The four original `source_reuse`/`population_width` trajectory and learning JSON
files each match that manifest. Comparing their selected records directly with
the curated input gives exact equality for all **1,080 displayed coordinate
values and 4,000 loss entries**. Every selected trace has 1,000 updates and seed 0;
every geometry view has nine classes, ten cue bins and three coordinates.

The accepted original run receipt independently matches
`bd057c05a842a702d6d8c3fd2259ee4e54918fb3b49951b57f782b08e876c17b`.
Receipt-bound configuration, case, lineage and native-diagnostic records confirm:

| Case | Columns / sessions | Distinct selected training sources | Training / development rows |
| --- | --- | ---: | ---: |
| B2, observed seed 0 | 17 / 3 | 54 | 144 / 72 |
| B5, observed seed 0 | 17 / 3 | 135 | 144 / 72 |
| Wmid, observed seed 0 | 49 / 11 | 297 | 144 / 72 |

Each development class contains eight constructed rows. B2/B5 share the same
development plan and unit roster. The native Wmid diagnostics specify eleven
session encoders, seven output coordinates and equal-session averaging. The
displayed class means are already saved aggregates; I did not recompute them
from neural inputs or model outputs.

Inspection of the original report source, the staged notebook implementation and
`src/neuro/studies/population_models.py` confirms the stated order of operations:
development embedding, first three of seven coordinates, then the mean over
rows with the same pair label at each cue bin. Native first averages corresponding
session outputs. The learning records are each model's saved training total
loss, not development loss or decoder accuracy. The renderer preserves these
values, uses equal spans for the three axes within each panel, and labels its
independent panel limits and absence of cross-fit alignment.

## Scientific interpretation and preservation

The selection is explicit: the B2/B5 source-budget endpoints and the first wider
case, Wmid, all at observed seed 0. These are design-based illustrations, not a
claim that seed 0 represents the repeats or that these are the strongest models.
The complete score comparisons and controls remain in the main manuscript.

The new section correctly identifies eight constructed development rows per
class, ten 100-ms bins, centers at 50–950 ms, and a three-coordinate view of a
seven-coordinate representation. It does not equate visually separated class
means with individual-row separability or successful decoding. The prior
exposure of development data, known-label assembly, shared source blocks and
absence of biological uncertainty remain explicit in the manuscript.

The Time/native comparison acknowledges the joint changes in supervision,
network count and pooling. It does not treat loss heights as comparable scores,
or geometry across independently fitted frames as a common biological
coordinate system. The descriptive early loss decrease and slower, noisy later
changes agree with the saved traces and final plots. The fixed update budget is
not presented as proof of convergence. The manuscript leaves natural-trial
generalization, simultaneous population dynamics, biological replication and
formal observability unresolved.

Both moved section bodies are **exactly equal to the baseline** after removing
only the newly added appendix labels: 4,240 and 3,475 UTF-8 bytes respectively.
This comparison includes their tables, captions, first-case loss figure
reference, numerical residuals, execution counts, citations and limitations.
The main controls section points explicitly to Appendices A and B.

## Readability and review boundary

I inspected final rendered physical pages 1, 2, 14, 15, 22, 23 and 24, including
the cover, opening scope, both geometry pages, both appendices and references.
The geometry pages are printed pages 13/14; the appendices are printed pages
21/22. The figures' class legends, bin markers, coordinate axes, matching
loss-panel labels, captions and interpretation are readable without clipping
that changes their meaning. Both appendix tables and the preserved learning
curves remain readable. The cover consistently states Lin Hong Yi, Semester 1,
AY 2026/2027, and the cue-decoding/trial-sampling/population-construction title.
Institutional formatting-policy compliance is outside this scientific review.

I read the required workspace/learner context and the permitted original study
ledger for its primary artifact pins. I did not read the manuscript package's
README or validation documents, prior/current audit reports, author/probe memos,
or other reviewers' findings. I performed no fitting, model loading or replay,
neural tensor/value-array reads, reconstruction, scientific reruns or notebook
execution. This audit used source inspection, scalar/aggregate JSON equality,
metadata counts, hashes, PDF text and the supplied final page renders. Only this
audit file was written.
