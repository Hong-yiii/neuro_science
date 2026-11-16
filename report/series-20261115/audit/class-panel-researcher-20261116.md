# Independent researcher audit of the class-panel revision

**Verdict: PASS. UNDERSTANDABLE: yes.**

Reviewed November 16, 2026, as a fresh neuroscience researcher, independently of
the other manuscript reviewers. No material scientific or explanatory correction
is required for the candidate identified below. This verdict covers the new
class-selection/feasibility explanation and its integration with the surrounding
pseudopopulation construction. It does not revalidate every historical result in
the synthesis or authorize further scientific execution.

## Exact candidate and evidence identity

The final reviewed manuscript is the 20-page A4 PDF. I verified these SHA256 values
from the actual files, including the rebuilt page 7 wording that limits 16 training
rows per pair to the primary arms.

| Artifact | SHA256 |
| --- | --- |
| `report/series-20261115/paper.pdf` | `f5a1783a3673ff5a788af8210bfb876e7045fb531d06354f1a248dbd4ba270f9` |
| `report/series-20261115/paper.tex` | `a3df343e3add19089e7e497d872d4d45eb36aca74ef4a79ddfe65aebe6667d28` |
| `docs/experiments/source-reuse-width-20261114/class-panel-20261116.md` | `45deee5bb81b6c4fb7a71ff109674655ef06e1eedce071edccc1ebbc3954712a` |
| `docs/experiments/source-reuse-width-20261114/class-panel-metadata-20261116.json` | `8f6560aa172c86a53f211596bce9333ee410281210f2c518ad3a8503a572316a` |
| `docs/experiments/source-reuse-width-20261114/verify_class_panel_20261116.py` | `c615e32feaa652d0960fe01d2b9b8ba9b67708ba01a085528c7de5b09f3e16df` |
| `docs/experiments/source-reuse-width-20261114/protocol.md` | `7d1dbd5d26352725eb522389c5400dd753bb301ea7894328afde25d820b18005` |
| `docs/experiments/source-reuse-width-20261114/design.json` | `f35f91ae6936956d5c9e99550267eeabae213347f3b07ff22fac8bd3a6a23c29` |
| `report/series-20261115/class-panel-figure-provenance.json` | `dee2b1ccb57194dccd1bbcc8db4650084486a7d7a8a3c6e85191229e76d549b5` |
| `report/series-20261115/build_class_panel_figures.py` | `40243cbff31f396ca1f900ba241d163793d67c794864ece473b08e8cc3bea594` |

The figure provenance authenticates the following generated artifacts; I checked
every listed file against its recorded hash and compared every CSV data row with
the metadata receipt.

| Artifact under `report/series-20261115/` | SHA256 |
| --- | --- |
| `data/class_panel_marginals.csv` | `ea9b89a7c39b6f76157e7ed2fe00c4106afbe0b4b2f8d14a93699ac823e643ff` |
| `data/class_panel_frontier.csv` | `130967e57dd54818417f48320fb64a1193f094b4e8bc7611f2628bacaa4aa482` |
| `figures/class_panel_support.pdf` | `3b28afec262b3b5466f5214d26586dc52caed4b65522137d02fddb74a88398fd` |
| `figures/class_panel_support.png` | `b82ec0b1c3e6c950b8e6a69ea6725fab28363db4eaec0c7323056e82dda53d13` |
| `figures/class_panel_frontier.pdf` | `3313082cc9e79a21eada603f1edca1a69b93c632022aa4b12a24c507113222e4` |
| `figures/class_panel_frontier.png` | `17cf448f73ceed93d5a0e64002e8670492611fdf4d125b3ea6d069d3c5c6808f` |

## Independence, sources and work performed

I read the mandatory workspace instructions, `docs/workspace.md` and
`context/learner-profile.md`, then began with the dated class-panel note, receipt,
verification script and original protocol/design. I did not read prior audits,
author/probe memos, package README approval headlines or other reviewers' findings.
The first PDF read was the supplied revision candidate, followed by the final
rebuilt candidate above. This is an independent AI-agent artifact audit, not
external biological replication or journal peer review.

I inspected `select_panel()` and `derive_rosters()` in
`experiments/source_reuse_width_20261114/study.py`, `metadata()` in
`src/neuro/studies/population_grid.py`, and the imported public metadata identities
in `src/neuro/studies/source_support_ablation.py`. Their bytes and the frozen
design matched revision `a0ca80180e2bb52b90e499357d3d6965b26806da` and the receipt:

| Source | SHA256 |
| --- | --- |
| `experiments/source_reuse_width_20261114/study.py` | `36dba2acf3ca8128799b480637841c15137a1eb235dbe13ca2c40f8391b36948` |
| `src/neuro/studies/population_grid.py` | `1851133f689da302e67dc17b5fcc14b990fecd8b678eae4f090a7adf4687d1f6` |
| `src/neuro/studies/source_support_ablation.py` | `413a4871b961c8508b588d2b803df19155f8f6ddafb0bddd0e7d79de4be5233e` |
| `data/cue-source-v1/manifest.json` | `8af267ca189a98a3bcc3c24e498259d36079e41402a6cf2fdb9a0d9e5291ed11` |
| `data/cue-source-v1/inner_splits.csv.gz` | `34fa1c5a0f5c6d9443d435c98ba64830c68f2792306172c12d53ad60792f219f` |
| `data/cue-source-v1/outer_splits.csv.gz` | `c42b2dd2bf184dca8f9ed86908d35f16caf40bd52b4221d17380a2156d1eee56` |

An independent standard-library recount read only those three public data files.
It checked unique source identities, outer-train membership, predecessor adjacency,
session consistency, allowed labels/splits and the global contributor embargo.
It reproduced 58 sessions, 195 columns, 15,553 inner rows, 5,872 protected
contributors and 4,427 embargoed training rows. All 90 off-diagonal matrix values
and 18 unavailable diagonal entries matched the receipt. Direct intersections
reproduced all 18 frontier gates, every returned panel's endpoint incidences, and
the full frozen core/middle/full roster objects, including exact harmonic-order
middle selection, available source totals and singleton counts. The all-30-class
minimum-three failure was also independently confirmed.

I did not rerun the optimizer. Its optimality statements were assessed through the
authenticated receipt and the actual binary formulation, objective-fixing sequence,
solver-status checks and direct width reconciliation. My independent recount
checks the support of every returned panel, not a second global-optimality proof.
No study or model runtime was imported for that recount. No fitting, model replay,
neural-array read, notebook execution, new literature search or result modification
occurred. The renderer was inspected, not executed by this reviewer. Only this
audit file was written.

For the manuscript, I read the new sections and their LaTeX, directly extracted
PDF text on pages 1, 5–10 and 20, and visually inspected the supplied page 6 and
final page 7 renders. The surrounding material establishes the condition-level
assay, source/row distinction, block concatenation, reuse and exposed-development
limits needed to interpret the addition.

## Scientific and explanatory assessment

1. **Fixed task size versus class identities is clear.** The original protocol
   specifies nine classes and the implementation supplies `count=9` to the
   selector. Pages 5–7 explain what is optimized *at that count*. They do not
   claim that nine maximizes width across counts or was chosen by decoding
   performance. The retrospective alternatives make that boundary visible:
   eight is wider, and ten retains the same five-source core. The documented
   operational sequence does not imply that choosing nine was blind to all
   earlier metadata exploration; the manuscript does not make that stronger claim.

2. **Marginals and common support are distinguished correctly.** Figure 3 shows
   all 30 ordered nonself classes, eligible current-source counts and single-pair
   session counts. It identifies the selected classes without suggesting they
   were the nine most frequent pairs. The intersection equation and the whole
   session-block exclusion rule explain why abundant aggregate support cannot
   fill a deficient session–class pool. The three five-source sessions and the
   20 three-source sessions match the data. The following fixed-panel support and
   assembly pages connect this selection to actual pseudopopulation construction.

3. **The optimization hierarchy is faithful to the code.** Five-source width is
   maximized first; three-source width is maximized only among those optima;
   lexicographic class-list selection follows. Recorded columns are the objective,
   not session count. Endpoint bounds apply separately to start and goal. The
   text also acknowledges that development availability enters eligibility;
   metadata selection does not create an untouched test set. It does not replace
   source safety, independence or scientific validity with a width optimum.

4. **Larger panels and one-session optima are not overclaimed.** The K=10 panel
   really is the frozen nine pairs plus `4→1`, so its loss of wider-roster sessions
   is a valid nested example. K=12 and K=15 each return one eight-column session
   at five sources. Such a core cannot provide the same shared multisession
   2/3/5-budget design; the text explicitly does not infer that all panels of those
   sizes are infeasible. This distinction matters because maximizing width is
   not maximizing session count. Nor does the discussion imply single-session
   fitting is generally impossible. The K≥18 statement is limited to the displayed
   panels; the all-30-class minimum-three failure is separately supported.

5. **Task and metric arithmetic are correct.** All selected endpoints occur once
   or twice at K=9. A prediction rule supplied only with the true start can recover
   at most one pair per start group, giving at most six total class recalls and
   pair balanced accuracy 6/K. Randomizing within each group preserves that ceiling
   in expectation; the same argument applies to goal. At K=6, degree one makes
   either endpoint sufficient to identify the pair. These are task properties,
   not observed neural baseline scores. Equal per-pair counts make pair accuracy
   and pair balanced accuracy coincide; endpoint heads need not share that equality.
   The final PDF correctly scopes the 16/8 training/development counts to primary
   arms, while U3's three training rows per pair remain explicit nearby. Changing K
   also changes the 1/K uniform reference, preventing a decoding interpretation of
   the feasibility frontier.

6. **The new figures are understandable and appropriately limited.** Figure 3's
   two matrices, unavailable diagonal, selected-class outlines and train/development
   annotations remain legible at manuscript size. Figure 4 distinguishes the two
   support thresholds and marks the executed K=9 separately from metadata-only
   alternatives; Table 5 gives every exact session/column count. The caption says
   panels need not be nested, and the section identifies the secondary objective
   as conditional. The plotted connections should be read as guides between the
   displayed fixed-K categories, not continuous slopes or a learning curve.
   Neither figure substitutes synthetic row counts for measured support or adds
   biological uncertainty to deterministic metadata counts.

The new explanation makes the design scientifically understandable: the reader
can follow the chain from eligible recorded sources, through complete per-class
session support, to a fixed task and nested column rosters, and then to constructed
rows used for decoding. It preserves the distinction between explaining why the
construction is feasible and claiming what a decoder has established. No additional
study is needed to accept this bounded manuscript revision.
