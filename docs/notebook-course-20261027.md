# Standalone research course — October 27, 2026

The owner asked whether the notebooks alone teach the study's foundations and
implementation, and requested continued work toward that standard. The first
teaching revision left substantive gaps: experiment foundations, one complete
numerical trace, network internals, setting rationale, and the reasoning behind
the path/source-transfer/ablation studies. The owner explicitly allowed splitting
the material into multiple notebooks. This continues the authorized update to
[draft PR22](https://github.com/Hong-yiii/neuro_science/pull/22).

This is a **software and teaching revision of exploratory research**, with invented
arithmetic checks. It is not a new biological analysis or a confirmatory study.

## Reading course

The [notebook index](../notebooks/README.md) gives the seven-chapter reading order:

| Chapter | Role in a successor's understanding |
| --- | --- |
| [00 — Research guide](../notebooks/00_research_guide.ipynb) | Question, cohort and evidence map; accepted endpoint/time/joint comparisons and limits |
| [00a — Experiment foundations](../notebooks/00a_experiment_foundations.ipynb) | Task events, measured spikes and sorted units, clocks, counts/masks, source blocks, conditional assembly and biological interpretation |
| [00b — Worked example](../notebooks/00b_worked_example.ipynb) | The same invented timestamps carried through counts, source split, assembly, scaling, fixed projection/logits, probabilities, confusion metrics and a contrastive term |
| [01 — Pseudopopulation](../notebooks/01_pseudopopulation.ipynb) | Actual construction, support/exclusion decisions, contributor embargo, source skew and reuse |
| [02 — PCA/LDA](../notebooks/02_pca_lda.ipynb) | Visible scaler/PCA/classifier stages, forward arithmetic, setting rationale and matched comparisons |
| [03 — CEBRA](../notebooks/03_cebra.ipynb) | Actual network architecture, temporal sampling/objective, learning and geometry diagnostics, staged encoder/readout computation |
| [04 — Study evidence](../notebooks/04_study_evidence.ipynb) | Path measurement, source transfer versus recombination, preprocessing/sampling/readout ablations, historical learning/3D evidence and joint-navigation implementation/results |

Foundations separate documented task facts from missing organism, reward, apparatus
and acquisition details; they do not fill those gaps by guessing. The count example
distinguishes an observed zero from an unrecorded unit and demonstrates why copies
of a source cannot cross splits. The model chapters explain what each fitted object
contains, rather than treating its name as an explanation. The retrospective
includes negative findings and the controls that limited the strongest claims.

The worked example supplies its projection and decoder weights by hand. It does
not call them learned PCA or a trained classifier. Its loss comparison changes a
given positive vector, not an optimizer state. Historical figures come from tracked
public reports, never a new private checkpoint replay.

## Staging preserves the declared experiment

B/C now expose their first planned observed/full/seed-zero case in six stages:
assembly, training normalization, representation fitting, frozen transformation,
readout fitting and scoring. They reconstruct the scaler statistics, PCA projection
and logistic probabilities with explicit arithmetic and compare them to the fitted
objects. C also prints its network and parameter count. The final loops skip the
completed first case, keeping the original source/world/seed comparisons.

The teaching explains inherited settings without presenting rationale as evidence
of optimality. CEBRA's installed offset1 model is the verified affine/GELU network
with widths U→32→32→16→8 and output normalization, not a recurrent sequence model.
Temporal structure enters through the sampler. The raw baseline's unit-major
features and projected representations' time-major features remain explicit.

`scripts/test_teaching_notebook_grid.py` exercises the original and staged code
with actual invented source assembly, contributor gates, artifact bookkeeping and
metric computation. Deterministic mock estimators replace every fit under the
no-fitting guard. Tests compare each fitting call's case, exact inputs, labels,
arguments and order, all result records, artifact keys, fixed development plans,
values, targets and exposures, and the retained observed/full/seed-zero view.

- B remains 4 PCA, 24 logistic and 12 LDA fits in a future authorized execution.
- C remains 6 CEBRA, 6 PCA and 54 logistic fits, with six times the configured
  optimizer updates. The observed development artifact is saved only once.

These tests validate orchestration with mocks; they do not certify actual model
optimization or the new numeric assertions on a real fitted pipeline. **B/C were
not executed**, on invented or biological inputs, for this revision. Their source
outputs remain empty. A's code-cell hash is identical to the already verified
October26 no-fitting execution; only its reading links changed, so it was not rerun.

## Verification and readable outputs

All ten focused tests passed: three staged-grid checks, six diagnostic checks and
the existing notebook source/privacy check. Ruff and whitespace checks passed.
All seven notebooks validate against the schema; every code cell parses and local
Markdown links resolve. All fourteen attached historical PNGs match their public
source bytes and hashes. Four newly embedded images are extracted from tracked
HTML reports; metadata records both the HTML hash and exact image hash/alt selector.

Two fresh kernels executed only teaching arithmetic, with two numerical threads
and the existing scientific interpreter/notebook overlay borrowed read-only:

| Notebook | Executed code | Saved invented output | Elapsed |
| --- | --- | --- | --- |
| 00b | 7 cells | Tables, three figures, exact-count/scaling/prediction/metric assertions | 5.38 s |
| 04 | 2 cells | Symbolic interior-component labels and relative-duration native-bin pairs | 2.03 s |

No fitting API, optimizer, lab source adapter or saved model is used in those
cells. Sequential execution and output privacy checks passed. Public source
metadata records the executed code hash and classification. For 00b the hash is
`d38495bc4c36258a854fe1adc5fd6f1c35ad0163a4c427334168a3134c8532aa`;
for 04 it is `338587020ec3db12f463fbd6971b40ddc3c872e8573e6d5ffdc7787dd720b0b2`.
The saved outputs therefore make the numerical examples readable without a kernel.
The three new figures were visually inspected, and all seven chapters exported
successfully to HTML. Independent scientific/code reviews checked the foundations,
arithmetic, historical claims, navigation pair construction and staged grids;
all findings were resolved before publication.

Task-owned execution receipts, structural/hash checks, figures and HTML previews
are under `work/notebook-course-20261027/`. The existing build script regenerates
all seven notebooks with empty code outputs; it retains attached historical figures.
The index documents separately re-executing the two invented teaching chapters.
No dependency installation, retained runtime change, model fit, private source read
or checkpoint replay was performed for this teaching pass.

## What the course cannot supply

The course now connects the research's questions, foundations, decisions,
implementation and accepted evidence within the notebooks. Links remain for
provenance and deeper code review, rather than carrying an unexplained critical step.
It is not a reconstruction of every historical run or a claim that every task detail
is known. Missing acquisition metadata, unresolved clock/label semantics and
unperformed controls are identified explicitly.

Actual historical loss curves and 3D views do not show whether the current compact
27-unit model grid learned successfully. The earlier reviewed October23 run is
dated evidence on its own inputs/code. The current grid has no matched joint arm;
the retrospective explains the historical intervention, including changed cue
exposure, native navigation bins, relative-duration pairing and distinct weights.
It cannot supply missing temporal transfer, confound control, independent biological
replication or formal neural-state observability. Exposed development and
label-conditioned assembly remain limits, not issues resolved by better teaching.

Original notebooks/results, compact sources, private inputs/models, retained
runtimes, failed evidence, stash and unrelated changes remain preserved. This
update publishes teaching source, invented outputs and already-public historical
figures to the existing draft. It authorizes no merge, new license, release or
additional biological run.
