# Research notebook teaching revamp — October 26, 2026

The owner requested notebooks that teach the research to a successor: why a
pseudopopulation is admissible, what biases construction introduces, how to judge
CEBRA optimization and representation quality, what three-dimensional views mean,
how decoders perform, and how joint training changed the accepted results. This is
a **software/presentation revision of exploratory research**, not a new analysis or
confirmatory study.

## Deliverable and reading order

- [00 — Research guide](../notebooks/00_research_guide.ipynb) is readable without
  execution, with previously public aggregate figures embedded as attachments. It
  owns the overview, historical result comparisons, evidence status and handoff.
- [01 — Pseudopopulation](../notebooks/01_pseudopopulation.ipynb) explains target
  derivation, predecessor contributors, support/exclusions, missingness/exposure,
  class/pool/session skew, explicit source aliases and block reconstruction, and
  synthetic balance versus source reuse. Its whole-notebook no-fitting guard remains.
- [02 — Baselines](../notebooks/02_pca_lda.ipynb) teaches scaling, PCA and supervised
  LDA roles, metric interpretation, matched source ablations and descriptive geometry.
- [03 — CEBRA](../notebooks/03_cebra.ipynb) teaches the actual contrastive sampler,
  optimization diagnostics, sampling coverage, embedding spread, decoder comparisons,
  controls and claim limits.

The model chapters previously plotted whichever representation happened to be left
after the fit loop. In C this was the **permuted, reduced-source seed-zero** result;
in B it was a reduced-source result. The revision captures the explicitly named
**observed/full/seed-zero** PCA/CEBRA coordinates for illustrative geometry. It shows
direct coordinates 1–3 of the existing embedding, retains the full model dimension,
and reports their fraction of centered embedding variance. No new projection is
fitted. These coordinates have no cross-fit alignment or intrinsic biological meaning.

## Evidence and execution boundaries

The guide's historical endpoint figures describe 195 units/58 sessions, 12,288/3,265
train/exposed-development sources and 480/240 pseudorows per seed. Its joint comparison
is the accepted October7 cue-only versus 50/50 cue/navigation encoder comparison at
1,000 updates. All downstream evaluation is cue-only. The intervention changes both
navigation content and cue exposure. Its whole-cue joint-gain family tail is 8/21;
the descriptive pair-accuracy gain is not general joint superiority.

The fresh 27-unit/10-block panel and October23 reviewed aggregate ranges are separate.
Those aggregates do not attest current regenerated compact-source notebook outputs.
The current runnable B/C grid has no joint arm. Default fresh execution remains an
invented software example. The four notebook source files contain no private
execution outputs; only chapter 00 embeds existing public aggregate figures.

The initial teaching revision was local. The owner subsequently requested updating
[draft PR22](https://github.com/Hong-yiii/neuro_science/pull/22), authorizing the commit,
push and revised review description for this work. GitHub owns the publication status.
No new biological fit, checkpoint replay, source export, package release or merge
is part of this revision. Original notebooks/results, runtimes, inputs, failed
evidence, stash, submodules and pre-existing sampling formatting remain preserved.
The model grid and fit accounting remain unchanged. This revision does not make the
exposed development pool pristine or resolve provisional marker semantics.

## Implementation and verification

`scripts/build_fresh_notebooks.py` composes teaching cells from
`notebook_construction_guide.py`, `notebook_model_guide.py` and
`notebook_research_guide.py`. Building reads already-public presentation PNGs only.
`neuro.notebook_diagnostics` summarizes supplied arrays/metrics without fitting,
loading checkpoints or accessing source files.

Verified on the final sources:

- Six invented-array diagnostic tests passed, including metric units, separate worlds,
  time-major bin/coordinate indexing, constant/rank-one/full-rank distributions,
  role-specific sampling coverage and figure rendering with fitting blocked.
- The existing notebook source/privacy contract test passed. All four notebooks
  validate against the notebook schema; every code cell parses; local Markdown links
  resolve. All seven embedded PNGs exactly match their tracked public source bytes
  and SHA256 metadata. The historical table was independently recomputed from the
  public per-seed CSV and agrees at displayed precision.
- AST comparison with the prior three source notebooks confirms every model-fitting
  call and its arguments remain identical. This check does not substitute for B/C
  execution, which was **not performed**. The new decoder summary cell was separately
  exercised on fabricated metrics with fitting blocked, including its worked
  confusion-matrix arithmetic.
- Final A executed in a fresh invented-input kernel: **13 code cells, eight rendered
  figures, 6.56 seconds**, all fit counters and optimizer updates zero. Final source
  hash matches the execution receipt. Artifact verification also ran with fitting
  blocked. Numerical threads were limited to two; sampled owned-process RSS peaked
  at 533,331,968 bytes under a 4-GiB monitored budget, without a claim of hard cgroup
  containment. No dependency or retained runtime was changed.
- Construction-skew/balance figures and invented-array 3D/learning diagnostics were
  visually inspected. Train/development rate histograms now share bin edges; the
  balance caption does not imply a distribution changed when the invented source
  prior was already uniform. Independent scientific/code review found no remaining
  blockers. Ruff checks and whitespace checks passed.

Task-owned receipts, executed invented A and the offline HTML reading preview live
under `work/notebook-revamp-20261026/`. The final A receipt is in `invented-a-final/`;
the earlier successful `invented-a/` check is retained separately. Source notebook
outputs remain empty. No biological reconstruction was repeated for this revamp;
the earlier compact reconstruction has its own dated ledger and source identity.

Remaining limits are substantive: no new real learning curves or current compact
model scores are claimed, no matched joint arm exists for the fresh panel, and the
historical figures cannot supply missing confound controls or formal state
observability. A future model run must retain the existing execution review boundary.
