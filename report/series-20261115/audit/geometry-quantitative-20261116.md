# Independent geometry and appendix quantitative audit

**PASS. UNDERSTANDABLE: yes.** Reviewed November 16, 2026 against baseline
`414496280088f9400114938c3b9ad65e417f82c2` and the final artifact identities below.
No blocking quantitative, provenance, preservation or plotting finding remains.

This is a presentation-only audit of existing exploratory results. I independently
authenticated the accepted saved aggregates, compared every selected value, inspected
the defining source and plotting code, checked the actual Matplotlib artists, rebuilt
the figures into ignored scratch space, and inspected the final PDF's geometry and
appendix pages. I did not consult the report package's README/validation files or
other review/probe memos. The original study ledger was used only as the public
delivery-manifest trust anchor.

**Authenticated source chain.** The original study ledger pins
`deliverables-20261115-03/delivery_manifest.json` to
`85e05fa820232245f37332e38bb70155507e869f1da69f0abb0d98cd1b4a0b37`.
The actual manifest matches, reports completion, and binds the four delivery inputs:

| Original delivery input | SHA256 |
| --- | --- |
| `source_reuse/trajectories.json` | `87afb9c46d122b5923eaba1318c50862c7c17efc3899d6c788d638640ab5cf1c` |
| `source_reuse/learning.json` | `cc7ec11399ea5bb63c0f4ca8c2958eb4ddc70aaa213b3d2a707596b22f22ef99` |
| `population_width/trajectories.json` | `152b842bae05027dcba33441abab518a9d055182bb52ee3db24333db938a061e` |
| `population_width/learning.json` | `216da27a4ce80127397d83fea14f661fad925046839b87ff6f68a7e54d290a00` |

The manifest's accepted-run receipt pin also matches the actual
`complete-01/receipt.json`:
`bd057c05a842a702d6d8c3fd2259ee4e54918fb3b49951b57f782b08e876c17b`.
That receipt authenticates the original reuse/width geometry and loss aggregates.
The reuse delivery is exactly the reuse aggregate; each width delivery is exactly
the saved B3 bridge followed by the original width aggregate. The delivery contains
32 reuse and 24 width cases; their eight identical B3 bridge cases yield 48 unique
cases and 96 unique encoder-loss traces. Nothing was discarded from the originals.

The receipt-bound `population_models.py`, `population_grid.py`, study and report
source snapshots are byte-identical to the primary source inspected. Their operations
establish development-bin coordinates, seven fitted dimensions, first-three-coordinate
class means, eight development rows per class and equal-session native pooling.
Original report manifests and the unchanged published-notebook manifest authenticate
the three selected original geometry PNGs and the two complete learning PNGs. Their
bytes exactly match the embedded reviewed notebook images; the new plots copy numeric
records and do not digitize those images.

**Complete value comparison.** The fixed selection is Time B2, Time B5, Time Wmid
and Native Wmid, each observed seed 0. Each selected geometry record has all nine
ordered endpoint classes, ten cue bins and three coordinates: 270 values per view,
1,080 total. Each matched `case_encoder` learning record supplies exactly 1,000
finite `loss.total` values: 4,000 total. All 5,080 numbers match their authenticated
originals both as exact parsed decimal values and as binary64 values, including sign.
Class labels, case/encoder identities, seed, iteration count and source-record keys
also match. There is no new projection, alignment, rounding, smoothing or model
computation.

The frozen design and primary schedule support the displayed counts: B2/B5 use
17 columns from three sessions, with 54/135 selected training sources and 56
available development sources; Wmid uses 49 columns from 11 sessions, with 297
selected training sources and 210 available development sources. The selected-source
counts are `9 × sessions × budget`. Each displayed case has 144 constructed
training rows and 72 constructed development rows, eight per class. These are
construction counts; they do not turn the row means into independent biological
replicates. I checked the stored design and source definitions without rerunning
metadata selection or assembly.

**Plotting and explanation.** Direct inspection of every plotted artist confirms
nine ten-point class traces per 3D panel, unchanged coordinates, correct class
colors, first/last markers at the saved 50/950-ms points, and all 1,000 unsmoothed
loss values at updates 1–1,000. All data fall inside their axes. Each 3D panel has
equal x/y/z spans, its own midpoint and limits, a fixed orthographic camera and a
cubic box. All logged minima, maxima, limits and camera settings match the actual
artists. Loss panels have independent y axes and remain attached to their matching
fitted encoder. Both geometry PDFs are vector-only.

The final one-row class legends, endpoint-marker legends, captions and training-loss
labels are legible and separated on physical PDF pages 14–15 (numbered 13–14).
The text identifies these as class means over constructed, exposed development
rows, displays only three of seven coordinates, and does not infer natural-trial
paths, simultaneity, per-row separation, biological uncertainty, shared coordinates
or decoder superiority from appearance. It distinguishes Time/native objectives
and leaves convergence open. The examples are design-selected illustrations;
the complete study and its other seeds/controls remain outside these four views.

Scratch-only regeneration of the final renderer produced byte-identical copies of
both PDF/PNG pairs and `geometry-figure-provenance.json`. The final legend-spacing
and statement-formatting changes preserve all data, markers, limits and camera
settings. Neither the renderer nor the artist checks imported `torch`, `cebra`,
`sklearn` or `neuro`.

**Appendix and preservation check.** Both former section bodies are byte-identical
to the baseline after allowing the added heading labels. The complete measurement
body is 4,183 bytes, SHA256
`2ec1367efc8d5f819a2f1c2bdc95175b466ba4e5912ebeee636ddf921b3e591b`;
the complete numerical body is 3,426 bytes, SHA256
`d614951d3db6fece252e125751e30cf0b34e061e41605a7e89fe1cc0804b634a`.
Each appears once after `\appendix`, as Appendix A/B on physical pages 22/23
(numbered 21/22). Their tables, original learning figure, prose, numbers and citations
remain present and legible. The final PDF has 24 physical pages: an unnumbered UROP
cover followed by 23 numbered pages; all 18 bibliography entries fit on the last page.
The shortened final administrative paragraphs preserve the no-fitting/replay and
review-scope boundaries.

All 52 baseline tracked files under this report's `data/` and `figures/` and the
reviewed walkthrough's `published/` directory remain byte-identical, including both
published notebooks/HTML files and their old figures. Tracked original study/notebook
sources have no baseline changes. The authenticated original aggregate files and
source snapshots remain unchanged. This bounded check does not claim a fresh audit
of every one of the 3,155 accepted-run receipt entries.

**Final identities.** Paths are relative to `report/series-20261115/`:

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

Audit scratch is retained at `work/geometry-quantitative-20261116/`, including the
independent value/source checks, artist checks, exact rebuilt outputs and inspected
PDF-page renders. Only this audit note was written into the production tree. No
neural observations/features, raw inputs or fitted model states were read; no model
was loaded, replayed or fitted; no notebook, study runner or metadata selection was
executed. Existing historical claims are preserved, not newly revalidated biologically.
