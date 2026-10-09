# Research Questions

**Current next-session priority (October9):** develop the [observability/CEBRA pivot](observability-pivot-20261009.md), with its operational definition and protocol still open. The H1-led framing below is retained history, not the default next run queue. H1 is neither confirmed nor refuted; H2 remains removed. No new fitting or data access is authorized by this update.

The [September27 direction](project-direction.md) records the previous scope. Its source/evaluation safeguards remain applicable.

## Primary Question

Does hippocampal population activity during the cue period contain prospective
information about the subsequently observed navigation path beyond what is
already explained by start and goal?

The observed path is the measured behavioral outcome. Interpreting it as the
animal's intended path additionally assumes that a maze-familiar animal usually
executes its intention. The analysis can support prospective path information;
it cannot establish intention or causal planning from decoding alone.

## H1 — Prospective Hippocampal Path Representation

H1 is one hypothesis with two linked components, not two independent
hypotheses:

- **H1a — information:** cue-period hippocampal population activity improves
  held-out prediction of the trial's subsequent path beyond start and goal.
- **H1b — structure:** that prospective path information exhibits reproducible
  low-dimensional organization.

The split prevents failure of one embedding method or dimensionality assumption
from being mistaken for absence of prospective information.

### Shared Path Components Across Conditions

Limited path variation within one `(start, goal)` condition weakens the exact
trial-specific H1a comparison, but it creates a complementary question: do cue
states reflect reusable components shared by paths from different task
conditions? For example, paths from `A` to `B` and from `A` to `C` may share a
directed corridor segment before diverging.

This is a candidate structural analysis within H1b, not a replacement for H1a. Its behavioral object is a shared future path component,
such as a directed edge, ordered segment, or branch decision. Initial, middle,
and terminal overlap should be distinguished because an obligatory initial
segment can be confounded with start location and an obligatory terminal segment
with goal.

The key comparison is not merely “high-overlap trials have similar cue states.”
It is whether path overlap explains held-out cue-state similarity after matching
or controlling same start, same goal, cue identity, session, and other available
confounds. Stronger contrasts include:

- same start and different goals: high versus low future-path overlap;
- same goal and different starts: high versus low overlap;
- different starts and goals that nevertheless share a middle route segment;
- the limited within-start-goal route variants, where available.

If path overlap is almost completely determined by start and goal, the dataset
cannot distinguish compositional path structure from task-condition coding.
The strongest allowed claim is that cue-period population geometry covaries with
shared components of subsequently observed paths; it does not establish an
internal graph, intention, or a planning mechanism.

The primary operational comparison is:

```text
baseline: path ~ start + goal
neural:   path ~ start + goal + cue activity
```

The conditional-information expression
`I(path; neural representation | start, goal) > 0` is conceptual. The practical
test is incremental held-out prediction with appropriate nulls.

## Path Terminology And Measurement

Use **path** for the animal's ordered movement through the maze. Reserve
**trajectory class** only for the previous analysis's categorical `(start,
goal)` label; do not use it as a synonym for path.

A maze graph is the current proposed measurement method, not part of H1:

- the maze is one graph;
- spatial regions are nodes and valid transitions are edges;
- one trial's path is an ordered walk through that graph.

Graph granularity, the criterion for distinct paths, and the primary path
similarity metric remain open decisions.

## Graph Decoding: Component Assay And Full-Path Ambition

**A:** predict an interior directed edge/component or route segment. This is the
simpler path-information assay. **B:** predict the ordered path through the maze
graph, the desired capability still in scope. Endpoints alone are not the target
that replaces either task. A is not a statistical baseline for B; each task needs
its own matched start/goal-only predictor, neural baselines and held-out metric.
A success is not full-path reconstruction; failure on one component does not
rule out information about other aspects of the path.

B requires an unambiguous route-level target and source support. A pseudorow
matched only on component presence can combine different full paths; do not
assign one source's path to it arbitrarily. Distinguish condition-level route
prediction from exact single-real-trial reconstruction. The latter retains the
simultaneous-trial contract below. A canonical endpoint-derived path does not
establish incremental neural information.

## H2 — Removed From Active Scope

Hongyi removed the artificial-navigation-agent comparison on September27, 2026.
It is not a stretch aim, run queue or prerequisite. Historical H2 notes remain
provenance; no replacement H2 or switch of the central question was adopted.

## Supporting Analyses

Place, view/visual, heading, action, goal, and conjunctive coding are no longer
the thesis-level primary question. They remain useful for:

- validating biological data and analysis pipelines;
- characterizing what the cue representation contains;
- testing sensory, spatial, and motor confounds;
- explaining apparent path information through correlated variables.

## CEBRA's Role

CEBRA is a candidate measurement instrument, not the hypothesis and not, by
itself, a path decoder.

The next bounded encoder comparison is **CEBRA-Time**, cue-only versus joint
cue/navigation training, with two predefined checkpoints and deliberate source
folds. PCA and supervised LDA remain baselines. Architecture/configuration,
checkpoint counts, decoder, metrics and complete budget must be frozen before
fitting; no broad objective/architecture/hyperparameter sweep is authorized.

```text
training sources: cue-only OR cue + navigation -> learn CEBRA-Time encoder
prediction:       cue activity -> encoder -> chosen decoder -> graph/path target
```

Joint training shares encoder parameters across phases. It does not establish
shared biological geometry; the existing Time sampler has within-phase temporal
positives, not explicit cross-phase alignment. This is not navigation-only
pretraining followed by cue fine-tuning. Decoder type/training policy remain
open; keep the eventual readout policy matched across encoder arms.

Path targets/representations must be derived from behavior, not neural outcomes;
learned processing/clustering must be fitted within training folds. CEBRA-Time
omits path labels from its temporal objective, but label-conditioned assembly
can still use them. Do not describe the whole current pipeline as label-free.
LDA uses target labels and is a supervised prediction baseline, not evidence
for intrinsic low-dimensional structure. CEBRA-Behavior remains historical,
not an optional extra arm in the new run queue.

## Core Nulls And Controls

- create and hash source-trial train/validation/test assignments before adaptive
  graph, path-metric, exclusion, or contrast selection;
- keep every sample and derivative from a source trial in one validation split;
- compare against start-and-goal-only prediction;
- shuffle path labels or neural features within start-goal condition;
- fit path processing, clustering, dimensionality reduction, and decoders using
  training data only;
- retain task-matched start/goal references and PCA/LDA comparisons; raw features
  remain available as a simple reference, not a new tuning grid;
- test shared path-component geometry first in raw, PCA, or other representations
  not trained with future-path labels;
- resolve the currently open decoder choice in a bounded protocol before fitting,
  rather than silently launching another decoder sweep;
- control available gaze, heading, cue identity, action, speed, trial time,
  session, previous goal/trial, and success-selection variables;
- do not interpret pseudopopulation covariance as simultaneous population
  dynamics.

## Data Feasibility Boundary

Exact trial-specific H1 requires the same real trial to contain:

```text
cue-period activity from a verified simultaneous population
+
start and goal labels
+
the subsequently observed path
```

A cross-session pseudopopulation can support route-condition or
condition-average analyses, but cannot reconstruct the exact neural population
state or path of one real trial. Multi-session representation learning does not
restore simultaneity that was never recorded.

### Current condition-level pseudopopulation lane (2026-09-08)

Given the operational difficulty of large simultaneous monkey recordings,
pseudopopulations remain central to a complementary question: do independent
source-trial sets reproduce population response differences associated with
future path components after endpoint/nuisance control? This is related evidence
for prospective coding, not fulfillment of the exact same-trial population-state
contract above. It does not redefine H1 or prove H1b from a supervised embedding.

Use behavior-only targets with explicit interior/anywhere semantics, source
splits before assembly, session-block/cue-bin preservation, training-only
preprocessing, and coherent source/session/temporal nulls. Do not fill missing
recordings with zero or count synthetic rows as independent trials. Per-unit
checks complement population analyses; no individually significant-neuron gate
is required. More data or another CEBRA formulation may help, but neither is a
proven remedy for the observed source-pool gap.

The [completed study and status index](professor_updates/path_generalization_20260907/README.md)
separates accepted results, corrected inference, failed attempts, and proposals.
The [September8 plan](reports/path-generalization-next-steps-20260908.md)
replaced an earlier simultaneous-data-first milestone; its next-study scope is
now superseded by the [September27 decisions](project-direction.md). Original test exposure remains permanent; development resplits do not
restore confirmation.

The legacy local place-bin export begins at cue offset and lacks the cue window,
start/goal labels, and a verified synchronized population matrix. It cannot yet
test H1.

The current all-session `place195` native snapshot contains 58 sessions, 195
place-selected cue-accessible spike trains, and same-session Ripple/Eyelink/Unity
trial logs, so a real importer/QC audit can now be run across the selected-cell
set. It remains below the scientific gate: cells are selected rather than an
unbiased complete population, simultaneous recording groups are not confirmed,
marker-label semantics remain unverified, raytrace/gaze controls are absent from
this snapshot, and clock-discrepant trials such as 20181105 trial 178 require
explicit QC flags.

An earlier bounded `20181105/session01` six-unit transfer is documented in
`notes/data_inspection/lab_server_20181105_session01.md`, but that exact data
root is not present in the current checkout.

## Next Milestone — Agreed Scope, Protocol Still Open

Prepare the pseudopopulation construction/provenance artifact with runnable
checks; resolve source folds and the bounded joint-training protocol in
[project direction](project-direction.md). Do not turn this into another broad
pseudopopulation/model-validation campaign. Necessary leakage checks, justified
nulls and claim limits remain in force.

Mentor guidance on cue/navigation place/view selectivity, rotation, validation
and literature is pending. It does not yet define a new hypothesis or experiment.
The completed studies do not establish H1, its absence, or missing laboratory
metadata. New biological fitting requires a reviewed frozen protocol and explicit
authorization; no run is launched by this scope update.
