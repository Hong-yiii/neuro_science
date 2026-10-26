"""Research-first reading chapter assembled only from tracked public evidence."""

from __future__ import annotations

import base64
import hashlib
from pathlib import Path


def research_guide(md, code, root):
    """Return an offline-readable chapter; do not execute or load research inputs.

    ``code`` keeps the same builder interface as the executable chapters. This
    chapter deliberately needs no kernel: historical figures are PNG attachments,
    and all numbers below come from the linked, already-public accepted reports.
    """
    del code
    root = Path(root)
    evidence = "../docs/reports/cebra-endpoint-time-readout-20261006"

    def figure(filename, text):
        cell = md(f"![{filename.removesuffix('.png').replace('_', ' ')}](attachment:{filename})\n\n{text}")
        image = root / "docs/reports/cebra-endpoint-time-readout-20261006/figures" / filename
        image_bytes = image.read_bytes()
        cell["metadata"]["public_figure_source"] = {
            "path": image.relative_to(root).as_posix(),
            "sha256": hashlib.sha256(image_bytes).hexdigest(),
        }
        cell["attachments"] = {
            filename: {"image/png": base64.b64encode(image_bytes).decode("ascii")}
        }
        return cell

    return [
        md("""
# 0 — Read the research before running the pipeline

## A graduate student's guide to the questions, evidence and decisions

**The central finding:** endpoint conditions are decodable in constructed cue-period
populations, but CEBRA is not uniformly better than simple references. Joint cue/navigation
training helped ordered-pair decoding more than either endpoint separately. The path
studies did not establish robust information about subsequent paths beyond endpoints.
These conclusions concern specified, historically exposed evaluation pools.

This chapter explains the research without requiring a kernel, private files or a model
run. Its attached figures and numerical tables are **accepted historical exploratory
evidence**, not newly generated results. Chapters 1–3 teach and execute the fresh-input
workflow; their current source files do not contain saved current-model results. Their
invented default demonstrates software behavior, not biology. Reading the historical
figures does not reproduce their source construction or fit their models.

Read in order: **question → measurement → population construction → model → evidence →
claim**. Use [the notebook index](README.md) for execution instructions and
[the source contract](../data/README.md) for the compact lab-source contents.
"""),
        md("""
## 1. What was the scientific question?

The original question was whether cue-period hippocampal activity contains information
about the **subsequently observed path beyond start and goal**. H1a concerns incremental
path information; H1b concerns reproducible low-dimensional organization of that
information. A path is the ordered movement through the maze. A `(start, goal)` category
is an endpoint condition: multiple paths can share it. Predicting endpoints therefore
does not answer H1a, even with excellent accuracy.

Path components are limited summaries such as whether a particular interior corridor
occurs; they are not full ordered-route reconstruction. The later research direction asks whether a
compact representation can support reusable task readouts and eventually a restricted
predictive state. That direction is proposed, not an already validated state model.

The endpoint benchmark asks whether an analysis can recover a declared task condition
under a specified construction. It exposes differences between start, goal and pair recovery. The three
heads are related targets, not three independent confirmations. H1 remains unresolved;
the artificial-agent comparison formerly called H2 is removed.

Sources: [research synthesis](../docs/reports/cebra-research-synthesis-20261011.md),
[analysis contract](../docs/analysis-contract.md),
[future agenda](../docs/cebra-observability-agenda-20261011.md).
"""),
        md("""
## 2. What is measured, and what are we constructing?

| Object | Status and interpretation | What remains unknown or unsupported |
| --- | --- | --- |
| Sorted-unit spike timestamps | Recorded event times after the inherited spike-sorting process | They are not a complete hippocampal state; unit selection/sorting can matter |
| Ripple/Eye/Unity markers | Recorded task events on declared clocks, joined and checked | Marker agreement alone does not independently verify their behavioral meaning |
| Start/goal categories | Provisional labels derived from previous/current successful-trial marker digits | Not direct measurements of intention; task semantics and cue confounds remain |
| Cue-bin counts | Derived counts in explicit intervals relative to cue onset | A zero means observed silence only where recording/exposure exists |
| Pseudopopulation row | Condition-matched blocks from several source trials/sessions | No simultaneous cross-session trial or observed cross-session noise covariance |
| PCA/CEBRA coordinates | Features derived using training-fitted transformations | Neither axis identity nor a biological state is directly observed |
| Decoder performance | Predictive association in the declared evaluation object | Does not establish planning, mechanism, causality or full-state observability |

The pipeline is **events → aligned counts/masks → source split → matched assemblies →
training-fitted representation → readout → evaluation**. Think of building an ML dataset
from sensors whose recordings do not all overlap. Deciding which rows legitimately
belong together is central. The compact source includes unbinned spikes and cue-relevant event
records, but intentionally omits dense gaze/behavior. Do not infer missing confound
controls from its availability.
"""),
        md("""
## 3. Can we form this pseudopopulation, and what does it estimate?

Yes, **for a supported condition-level assay**. For a chosen condition, draw one real
source trial per retained session block, carrying all that block's selected units and
cue bins together. Concatenate those blocks. Repeat to create constructed rows. Keeping
the block intact preserves recorded within-source structure; it cannot recover
unrecorded cross-session dependencies. Known conditions determine development assembly
as well as training assembly, so this is not inference on an unknown-label natural trial.

The feasibility gate is concrete: every retained block must have support for every
required condition in both splits, with the stricter training support needed for the
reduced-source intervention. Missing support means exclude the block/condition under
the declared rule or narrow the question. It does not mean impute an unrecorded cell as
zero or borrow a development trial. The current complete-support rule yields a smaller
27-unit panel from the 195-unit source archive; the archive size is not the model width.

Split sources before assembly. Because target derivation also uses a previous trial,
the current route protects the union of development trials **and their predecessor
contributors**, then removes intersecting training contributors globally. This prevents
that direct dependency crossing splits. It does not remove all longer-range serial
dependence, shared-session confounds or prior exposure of development results.

More constructed rows can improve coverage of the available pools, but cannot create
new independent recordings. Source counts, used/unused sources and repeated-source
weights must accompany row counts. Reuse also affects training normalization because
statistics are fitted to assembled training vectors. Chapter 1 makes each of these
decisions inspectable; passing software checks is necessary but does not certify the
biological assumptions.
"""),
        md("""
## 4. Keep the cohorts and evidence generations distinct

| Study / purpose | Units and source pools | Evaluation object | Status |
| --- | --- | --- | --- |
| September path preprocessing / matched PCA | 49 unit IDs / 13 sessions; 147 train / 41 development across endpoint-specific panels | Supported binary path-component assays across five endpoints | Historical exploratory evidence; 17/28 development pools are singletons |
| September25 joint-training path assay; October5 time readouts | 29 units / 7 sessions; 82 train / 22 development | Fixed 4→3 component; 128 training rows; 30 weighted development combinations | Historical exploratory evidence; October5 reuses saved encoders |
| October7 endpoint assay | 195 units / 58 sessions; 12,288 train / 3,265 development | 30 endpoint pairs; 480/240 constructed rows per seed; seeds 0–2 | Main historical matched cue/joint comparison shown below |
| October23 fresh-input assay | 27 units / 10 sessions; 1,415 train / 551 development | 30 pairs; cue-only full/reduced source pools; two observed computational seeds | Accepted separate exploratory run; aggregate table below |
| Current compact-source chapters | Archive contains 195 units / 58 sessions; consumption selects the supported panel | Fresh reconstruction from unbinned public source; invented default | A non-fitting reconstruction was checked; regenerated B/C evidence requires execution |

All these development pools are historically exposed. Computational seeds vary assembly
and/or optimization; they are not independent biological folds. The new contributor
embargo and complete-support selection change the panel and estimand. Native-precision
compact binning can also differ from the older serialized input route. Do not interpret
scores across these rows as an improvement timeline or a matched replication.

Sources: [historical synthesis](../docs/reports/cebra-research-synthesis-20261011.md),
[fresh-run ledger](../docs/shareable-notebooks-execution-20261023.md),
[compact-source ledger](../docs/compact-cue-source-20261026.md).
"""),
        md("""
## 5. Is the constructed population skewed?

There are several different distributions to inspect. Real sources can have unequal
endpoint frequencies; individual session×condition pools can be small; an exactly
balanced constructed dataset can reuse rare sources many times. These are different
forms of imbalance. Equal class counts in the final tensor address readout class
weighting, but do not equalize source diversity or supply an independent sample size.

Read the next two figures together. First identify abundant and scarce pairs. Then ask
whether aggregate abundance hides weak support in a particular session. In Chapter 1,
repeat this inspection **after** the current contributor embargo and panel selection,
and compare real-source counts with constructed counts and source reuse. Historical
support pictures below describe the old endpoint cohort, not the new 27-unit panel.
"""),
        figure("source_class_counts.png", f"""
**Figure 1 — Real-source imbalance before considering constructed-row balance.**
October7 endpoint cohort: 195 selected units / 58 sessions; 12,288 training and 3,265
exposed-development real sources, within historical outer training. Ordered-pair source
counts are shown; 480/240 condition-balanced pseudorows per computational seed are a
different object. No decoder, time-window score or uncertainty interval appears here.
**Read it:** which conditions have fewer distinct contributors even though later
classifiers receive balanced rows? Source: [accepted report]({evidence}/README.md),
`figures/source_class_counts.png`; provenance in that study's `provenance.json`.
"""),
        figure("source_session_support.png", f"""
**Figure 2 — Support is a session-by-condition requirement.** October7 endpoint
cohort, 195 units / 58 sessions; 12,288 training / 3,265 exposed-development sources;
480/240 conditional rows per seed, seeds 0–2. Cells count real sources in each
session×pair pool; they are not neural activity, decoding scores or independent
replicates. No uncertainty interval is implied. **Read it:** can large marginal counts
conceal a thin contributing pool, and what would repeated sampling from it mean?
Source: [accepted report]({evidence}/README.md), `figures/source_session_support.png`.
"""),
        md("""
## 6. Why these representations and readouts?

Raw standardized counts ask how much a simple regularized readout already recovers.
PCA supplies one linear basis fitted to pooled training bins. CEBRA-Time tests a nonlinear representation
whose contrastive pairs follow temporal adjacency. Raw SVD-LDA is a supervised classifier
reference, not an eight-dimensional unsupervised embedding.

For the historical endpoint experiment, one 100-ms population bin has 195 raw values.
PCA and each pointwise CEBRA encoder produce eight coordinates per bin. Concatenating
ten bins gives 1,950 raw or 80 reduced whole-cue features. It does not yield a single
eight-dimensional whole-cue state. Input scaling, PCA, encoder training and readout
scaling/fitting use training inputs. Development transformations remain fixed.

Each pair/start/goal target has its own logistic readout; start and goal predictions
are not marginals of a predicted pair. Holding development assemblies and decoder
settings fixed makes within-study comparisons interpretable. It does not match raw
and reduced feature dimensions, erase task confounds or make one architecture universally
optimal. The historical logistic setting was `C=.01`; the notebooks expose the
corresponding declared configuration instead of silently selecting a better result.
"""),
        md("""
## 7. Is CEBRA learning, and what would a 3D picture establish?

Separate three questions. **Optimization:** are updates finite and does the declared
objective change? **Representation:** do outputs vary, avoid collapse and retain
structure in their full dimensionality? **Utility:** does a fixed readout generalize
to the specified development sources relative to raw/PCA references? A declining
contrastive training loss answers only the first question, and cannot by itself
establish convergence or biological information.

The current encoder takes one bin at a time. Time-positive samples are adjacent native
bins within a constructed row; negatives sample row/bin vectors. The full pipeline is
still condition-dependent because labels define assembly. Chapter 3 exposes the actual
loss components and sampler exposure alongside predictive results. Its invented default
uses only 20 updates: a software demonstration, not evidence for trained biological
representations. No current real learning curve is supplied by this reading chapter.

For a 3D view, first state whether each point is one row×bin, a whole-cue vector or a
condition average. State the world, source budget, seed, split and projection. Color
separately by endpoint and cue time to reveal different organizations. A display of
three coordinates discards the rest; a further learned projection must be fitted on
training inputs and its retained information reported. Preserve the actual model
dimension. Clusters, loops and visual separation are descriptive, not evidence of
biological dynamics or path planning. The historical latest-endpoint report did not
include a matched cue/joint 3D atlas; older path/endpoint pictures cannot stand in for it.
"""),
        md("""
## 8. What is the decoder performance?

Balanced accuracy (BA) averages class recall. Ordinary accuracy weights classes by
their observed counts. They agree in this balanced endpoint construction, but not
generally. Uniform BA references are 1/30 for pairs and 1/6 for endpoints; these are
not significance thresholds. Log loss assesses assigned probability to the true class:
confident mistakes are costly. A model can improve probability quality while making
fewer correct top-class decisions, so inspect both metrics and the confusion structure.

**Historical October7 whole-cue results; means of three computational seeds:**

| Representation / readout | Pair BA | Start BA | Goal BA | Pair log loss ↓ |
| --- | ---: | ---: | ---: | ---: |
| Raw + logistic | 70.28% | 78.75% | 90.83% | 2.1701 |
| PCA-8 + logistic | 83.61% | 89.44% | 86.81% | 1.6736 |
| Cue CEBRA-Time + logistic | 63.75% | 71.81% | 85.14% | 1.7795 |
| Joint CEBRA-Time + logistic | 75.56% | 72.64% | 83.89% | 1.6373 |
| Raw SVD-LDA | 48.47% | 57.22% | 80.97% | 3.7206 |

PCA leads pair/start BA; raw leads goal BA. Joint CEBRA has lower pair loss than PCA
despite lower pair BA. This is a metric tradeoff, not a contradiction or a reason to
choose whichever metric favors CEBRA. Report the prespecified measures together.
The [full seed table](../docs/reports/cebra-endpoint-time-readout-20261006/tables/observed_metrics_by_seed.csv)
also retains training scores, F1, Brier and every cue window.
"""),
        figure("wholecue_balanced_accuracy.png", f"""
**Figure 3 — Read all targets and all seeds.** October7, 195 units / 58 sessions;
12,288 train / 3,265 exposed-development sources; 480/240 condition-balanced rows per
seed. Development BA uses concatenated 0–1 s cue input: raw/PCA/cue/joint CEBRA with
logistic `C=.01`, plus supervised raw SVD-LDA. Bars are means and dots seeds 0–2,
not biological confidence intervals. Uniform references are shown. **Read it:** does
the method ranking change with the target? Source: [accepted report]({evidence}/README.md),
`figures/wholecue_balanced_accuracy.png`; numerical rows in the linked seed table.
"""),
        figure("wholecue_log_loss.png", f"""
**Figure 4 — Accuracy does not describe probability quality.** Same October7
195-unit / 58-session cohort and 12,288/3,265 source pools; 480/240 conditional rows
per seed. Development multiclass log loss, lower is better, on concatenated 0–1 s
cue; logistic `C=.01` for raw/PCA/cue/joint CEBRA, supervised raw SVD-LDA reference.
Bars/dots are computational mean/seeds 0–2, not biological uncertainty. Uniform
probability loss is the displayed reference. **Read it:** compare PCA and joint CEBRA
for pairs against Figure 3. Source: [accepted report]({evidence}/README.md),
`figures/wholecue_log_loss.png`.
"""),
        figure("confusions_goal6_seed0.png", f"""
**Figure 5 — Diagnose errors rather than only ranking scores.** October7 goal6,
declared illustrative seed 0, 0–1 s whole cue; 195 units / 58 sessions, 12,288 training /
3,265 exposed-development sources and 480/240 conditional rows. True classes are rows;
predictions are columns. Top panels are counts, bottom panels class recall fractions,
for the same five readout families. No interval or best-seed selection is implied.
**Read it:** which true goals are confused, and does improvement occur across classes?
These are 240 constructed rows, not 240 independent recordings. Source:
[accepted report]({evidence}/README.md), `figures/confusions_goal6_seed0.png`;
the report retains every target and seed.
"""),
        md("""
## 9. How did joint training change the result?

Joint **encoder training** adds training-source navigation vectors. It is different
from joint **pair classification**, which predicts `(start, goal)`. Historical cue and
joint encoders used matched 1,000-update budgets; the joint sampler drew cue/navigation
phases 50/50. Both decoder fitting and development evaluation used cue activity only.
The paired comparison uses identical development assemblies within each seed.

| Target | Joint − cue BA | Cue loss − joint loss; positive favors joint |
| --- | ---: | ---: |
| Pair30 | +11.81 percentage points | +0.1422 |
| Start6 | +0.83 percentage points | +0.0811 |
| Goal6 | −1.25 percentage points | +0.0001 |

The intervention helped pair recovery much more than individual endpoint accuracy.
It reallocates cue exposure while adding navigation, so it does not isolate the causal
effect of navigation content. Nor does shared encoder training establish a shared
biological geometry. The whole-cue joint-gain family tail was **8/21**, which did not
establish robust joint superiority under that diagnostic. The figure below is part
of the result, not optional decoration after the favorable pair difference.
"""),
        figure("null_families.png", f"""
**Figure 6 — Relative improvement needs its declared controls.** October7 endpoint
cohort: 195 units / 58 sessions; 12,288/3,265 train/exposed-development sources;
480/240 conditional rows per seed. Twenty session×split joint-label shuffle worlds
repeat construction and fitting; three-seed means precede family maxima. Bin families
span ten 100-ms cue windows; whole-cue gain spans three targets on 0–1 s cue with the
declared readouts. Inclusive plus-one tails have minimum 1/21 and are not biological
confidence intervals or pristine confirmatory p-values. **Read it:** the whole-cue
gain tail is 8/21; smaller bin-family tails do not validate a chosen peak or undo
historical exposure and serial/nuisance limitations. Source:
[accepted report]({evidence}/README.md), `figures/null_families.png`.
"""),
        md("""
## 10. Time in the cue is not training time or temporal transfer

The next plot asks how much a readout fitted for each cue window recovers **in that
same window**. Its horizontal axis is milliseconds after cue onset, not optimizer
updates. A different decoder is fitted at each time. An apparent peak is descriptive,
not a validated optimal window selected after inspection.

Temporal generalization asks a different question: fit at time `t`, freeze the entire
prediction pipeline, then evaluate at `t′`. Cross-phase transfer also changes cue to
navigation or the reverse. Historical raw-LDA goal temporal generalization exists;
matched October CEBRA cue/joint transfer and navigation-time decoding remain unexecuted.
See the [agenda](../docs/cebra-observability-agenda-20261011.md) for that distinction.
"""),
        figure("time_balanced_accuracy.png", f"""
**Figure 7 — Recoverability changes across cue windows.** October7 endpoint assay,
195 units / 58 sessions; 12,288 training / 3,265 exposed-development sources;
480/240 conditional rows per seed. Development BA from separately fitted readouts
on ten 100-ms bins after cue onset; encoders are fixed at 1,000 updates. Raw/PCA/cue/joint
CEBRA use logistic `C=.01`; raw SVD-LDA is supervised. Lines/shading summarize
mean/min–max over computational seeds 0–2, not biological confidence intervals.
**Read it:** which targets become recoverable when, and what extra test would be needed
to claim a stable readout? Source: [accepted report]({evidence}/README.md),
`figures/time_balanced_accuracy.png`. No selected-window or transfer claim follows.
"""),
        md("""
## 11. What did the path work establish, and what is new in the fresh notebooks?

The fixed 4→3 component study showed a useful relative change: Time/logistic BA rose
from **32.64% to 61.81%**, and loss fell from **1.010464 to 0.710618** with broader
training. However, loss remained worse than the constant binary baseline
`log(2)=0.693147`, so the predeclared primary criterion failed. Its paired-gain tail
was 1/21, while absolute broader-Time loss had tail 12/21. Improvement over a weak
comparator is not established absolute path information. Eight of 22 source deletions
were inestimable after losing class support. These limitations remain part of the result.

Across the [path studies](../docs/reports/cebra-research-synthesis-20261011.md), source
transfer and controls did not establish broad robust cue-period component/path
information. That does not prove absence of path coding or refute all of H1. Full
ordered-route prediction and H1b remain unestablished.
[Original joint-path report](../docs/reports/cebra-full-trial-transfer/README.md).

The fresh 27-unit workflow makes source reconstruction, stricter contributor separation,
full/reduced pools and module boundaries reproducible. It is a different assay. These
**previously reviewed October23 full-pool BA ranges** are context, not newly executed
compact-source results:

| Representation | Pair30 | Start6 | Goal6 |
| --- | ---: | ---: | ---: |
| Raw | 15.8–17.9% | 27.1–30.8% | 62.5–66.7% |
| PCA | 12.1–14.6% | 22.5–27.5% | 57.9–61.3% |
| CEBRA | 15.0–19.2% | 20.8–30.0% | 47.9–55.8% |

Ranges span two computational seeds, not biological uncertainty. The 1,415/551
training/development sources support a 27-unit/10-session panel; reduced training
retains 638 sources. This is neither a matched replication of the 195-unit scores nor
a calibrated sample-efficiency law. The fresh grid has no joint-navigation arm.
[Reviewed numerical ledger](../docs/shareable-notebooks-execution-20261023.md).
"""),
        md("""
## 12. Use the executable chapters to inspect each decision

| Chapter | What to inspect | What a successful run establishes |
| --- | --- | --- |
| [1 — Pseudopopulation](01_pseudopopulation.ipynb) | Targets, exclusions, support, missingness, exact bins, block assembly and reuse | A traceable supported construction; no model fitting or biological-state proof |
| [2 — PCA/LDA](02_pca_lda.ipynb) | Training-only transforms, full/reduced source intervention, metrics, confusions and geometry | Reproducible baseline comparisons on the declared development construction |
| [3 — CEBRA](03_cebra.ipynb) | Temporal sampler, losses/exposure, observed geometry, matched references and readouts | Optimization/prediction diagnostics for fresh cue-only models, with separate permutation worlds |

The single fresh label permutation breaks alignment; it is not a biological
exchangeability test or a significance distribution. Source-pool reduction refits every
learned stage while fixing development assemblies. It tests this source intervention,
not tolerance of a deployed model to missing neurons. The final artifact replay checks
that saved states reproduce their outputs; numerical reproducibility does not verify
task semantics. Current source notebooks contain no saved new real-model evidence.
The [execution guide](README.md) distinguishes invented software checks, permitted
non-fitting reconstruction and the separate review required for biological model runs.

## 13. What would make a reusable state claim defensible?

Computational observability here means being able to inspect the pipeline and its
evidence. **Formal model-relative observability** instead asks whether distinct states
of a specified dynamical/measurement model can be distinguished from observation
histories. A perfect classifier of one task label can leave other state components
entirely hidden. Standard pointwise CEBRA supplies neither a dynamics model nor a
complete observer with calibrated uncertainty.

The proposed progression is task recovery → frozen-readout reuse → causal predictive
state estimation → explicit model-relative observability. Same-trial state claims need
verified simultaneous, time-linked measurements; condition-level pseudopopulations
remain useful for narrower representation questions. Future work must choose one
output/horizon, available history, supported split, baseline, confounds, uncertainty
method and stop rule before fitting. Independent future neural/behavioral outputs are
stronger tests than predicting the same encoder's own coordinates.

For a handoff, be able to explain why each source entered, what information was available
at prediction time, which comparison changed one declared intervention, and which
claim the evidence actually supports. Unresolved task semantics, prior development
exposure, place-unit selection, serial dependence and visual/behavioral confounds stay
visible. The [future agenda](../docs/cebra-observability-agenda-20261011.md) contains
proposals, not a queued run. The [historical endpoint notebook](../report/endpoint_walkthrough.ipynb)
preserves the separate accepted saved-model replay; this guide neither replaces nor
re-executes it.
"""),
    ]
