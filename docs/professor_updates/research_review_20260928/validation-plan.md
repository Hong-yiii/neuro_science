# Visual evidence and temporal decoding — agreed follow-up

**Hongyi, 28 September 2026. Status: agreed analysis direction, not a frozen fit protocol.**
The primary question remains whether cue activity adds information about the later
**path beyond start and goal** (H1a), with reproducible low-dimensional organization
as H1b. Artificial-agent H2 remains removed. Endpoint decoding supports the assay;
it does not replace the path question.

## What is agreed, and what this delivery does

1. Make reports self-contained and substantially more graphical: source/class
   support, performance, confusion matrices, time courses and explicit limitations.
2. Inspect real-source distributions before interpreting balanced synthetic rows.
3. Keep improved **cue decoding after joint training** as the primary method
   comparison; add **frozen-readout temporal/cross-phase transfer** as a separate
   supporting validation, not a claim of identical biological spaces.
4. Examine decoding throughout cue, and plan decoding during navigation too.
5. Proceed in order: source support → saved-result visualization → bounded prefit
   protocol. Select decoder policy separately from outer evaluation.

This delivery redraws existing results and aggregates saved metadata/predictions.
It performs **exploratory descriptive reanalysis, with zero new model fits**, no
checkpoint loads, no raw recording extraction and no new display projections.
Missing temporal/generalization results remain explicitly unmeasured. Historical
exposed-source results do not become confirmatory because their figures improve.

## 1. Source-support audit before models

Keep three denominators separate:

- **Eligible real sources:** count each verified session–trial identity once,
  not once per unit or time bin. Show start and goal counts, start×goal heatmaps,
  and behavior-defined path/component frequencies; document exclusions and scope.
- **Support per session and source fold:** show missing class×session cells,
  within-pair route/component variation and source counts, not just pooled balance.
  Preserve unit-specific availability separately. Same-session is not proof of
  simultaneous recording. Subjects/animals must not be inferred from session counts.
- **Synthetic evaluation objects:** show requested and realized pseudorow counts,
  reuse of contributing sources, evaluation weights and class priors. Equal class
  weights or rows cannot replace scarce real-source support.

For full ordered paths, establish behavior-only route definitions and source
support before constructing route labels. Component absence/presence is not a
whole-route distribution. A component-conditioned pseudorow can combine sources
with different full routes; do not assign one constituent route as its ground truth.
An unsupported class/fold/window is **not estimable**, not zero performance. Freeze
exclusion/support rules before examining new neural outcomes.

## 2. Common reporting standard

Each empirical figure or caption must stand alone: question, target, cohort,
source and synthetic counts, units/time reference, split/exposure history, model
and decoder policy, metric and baseline, uncertainty meaning, provenance and
strongest allowed claim. Show individual seeds/folds where available, not only
means. Seeds are computational repeats, synthetic rows are dependent, and neither
supplies a biological confidence interval. Do not fabricate uncertainty from a
three-seed standard error.

Required result views, where estimable:

- Performance with individual seed/fold values and appropriate baseline; paired
  arm differences on the same sources. Keep incompatible studies in separate panels.
- Confusion matrices as counts **and** true-class-normalized recalls, with class
  support and weighting explained. Fix class order across panels. Pooled predictions
  across seeds are repeated evaluations, not additional real trials.
- For imbalanced targets: per-class recall and a declared macro/balanced metric;
  probabilities require a proper probability score and training-only calibration.
- Cue-time and navigation-time decoding, plus temporal-generalization matrices
  where actually computed. Label missing results rather than drawing invented curves.
- Source/class distributions, source reuse and null/control outcomes; link negative
  and failed results as well as favorable ones.

Every report distinguishes measurements, derived labels/features, statistical
associations and biological interpretation. Illustrative diagrams are labelled
**schematic**, never disguised as data. Essential figures/assets must remain
available in the offline HTML, with a readable narrative and reproducible checks.

## 3. Primary assay: does joint training improve cue readout?

```text
training-source cue              → encoder A → cue features → decoder A
training-source cue + navigation → encoder B → cue features → decoder B

both scored on the same held-out-source cue targets
```

Use CEBRA-Time, one declared architecture/configuration, two predefined checkpoints
and a common decoder-selection/training policy. Fit **separate decoder weights**
for every encoder/seed/fold/checkpoint representation; independently fitted latent
axes are not interchangeable. Match source folds, targets, preprocessing rules,
baselines and evaluation metrics. Save both checkpoints on one training trajectory
per arm where possible.

A fixed total update budget changes cue exposure when navigation is mixed in.
Record total updates, realized phase draws and cue/navigation exposure; improvement
is attributable to that intervention as a whole, not automatically to extra data or
shared biological geometry. An equal-cue-exposure control would be a separately
budgeted choice, not silently added.

Fit all learned processing within training sources. Decoder-policy selection and
calibration use inner source splits; inner validation sources must not enter encoder
fitting either. Outer evaluation outcomes cannot choose checkpoint, target, window
or decoder. Historical resplits remain exploratory. Raw/PCA/LDA references must
use the same targets/sources; LDA is supervised and limited to K−1 directions.

## 4. Temporal analysis: distinguish three questions

### A. Information accessible at each time

For each prespecified cue window, fit a readout on training-source features from
that window and test on held-out-source features at the same window. Repeat for
navigation windows once their definition/support is defensible. Plot all target
panels (pair, start, goal and component) for the relevant cohort, with a paired
joint-minus-cue-only performance curve where estimable.

These are **separately trained window-specific decoders**. Good performance across
many windows does not establish one persistent code. State whether start/goal
scores are endpoint components of the argmax pair, summed pair-probability
marginals, or separately trained heads. Whole-cue and
per-window performance answer different questions and have different feature counts.

### B. Temporal generalization with a frozen readout

For each declared training window t, fit one decoder on training sources, freeze
it, then evaluate every declared test window t′ using held-out sources only.
Rows of the resulting matrix are decoder-training times; columns are evaluation
times. The diagonal is same-window decoding; off-diagonal entries measure transfer.
**This is a family of frozen decoders, one per row—not one refitted decoder per cell.**

Freeze the encoder, input normalization, feature scaling, decoder weights,
thresholds and calibration when crossing windows. No evaluation-time recentering,
alignment fitting or recalibration. Use the same target semantics and compatible
features throughout. Predeclare comparisons and source-coherent multiplicity/null
handling; do not hunt for an isolated bright heatmap cell.

### C. Cross-phase transfer

Within each encoder arm/seed/fold/checkpoint:

```text
training navigation window → fit decoder → freeze entire prediction pipeline
held-out navigation window              → within-phase reference
held-out cue window                     → navigation-to-cue transfer
```

The reverse cue-to-navigation direction needs its own training-source decoder,
then the same freeze discipline. Do not reuse weights across independently fitted
encoders. A navigation-only encoder would be a new arm, not part of this agreement.
Including held-out navigation in encoder training would contaminate both tests.

A positive result supports **task information accessible to a common readout**.
It does not prove equal biological manifolds, phase rotation, intention, H1a or H1b.
A negative transfer result is ambiguous if the within-phase reference is weak, or
if target meaning, support or feature scale differs across phases. Nonlinear
readouts can map different geometries to the same label; cross-decoding is not a
unique test of geometric identity.

## 5. Time, feature and target gates

- The current pointwise encoder emits **8 features/bin**; the historical ten-bin
  whole-cue decoder consumes **80 concatenated features**. It cannot be applied
  unchanged to one navigation bin. Choose matched window aggregation/dimensions
  before fitting; do not truncate, pad or refit on the evaluation phase by convenience.
- Cue plots need actual onset-relative windows and cue-offset/missing-bin handling.
  “100–200 ms” is not encoder update100–200. A cumulative-prefix curve is a separate
  question from information within a fixed-width window.
- Navigation durations vary. Choose event-aligned physical time or an explicitly
  labelled normalized-progress assay; report source/class support at every window.
  A progress fraction is not physical time, position or a simultaneous trajectory.
  Long trials must not receive unintended extra weight. Do not interpolate counts
  or pad absent data with zero simply to obtain a complete matrix.
- For a cross-session population, window alignment and intact source blocks must
  be meaningful in **both** phases. Historical native adjacent-pair training banks
  are not automatically a valid time-resolved navigation evaluation tensor.
- Pair/start/goal and whole-trial component labels can retain identity across phases,
  but interpretation differs: navigation decoding after a component is traversed
  may reflect current/past behavior, not prospective information. Current location
  is not interchangeable with future goal or route. For path claims retain
  endpoint-conditioned and available sensory/motor/history controls.

## 6. Remaining prefit decisions and acceptance gates

Before any new fit, independently review and freeze: cohort/target support,
real-source grouping and serial dependence, folds, window/alignment policy,
feature aggregation, the two checkpoints, phase weights/exposure accounting,
encoder configuration/seeds, bounded decoder choices and calibration, primary
metric and meaningful effect, baselines/nulls, multiplicity and source-aware
uncertainty, plus the complete encoder/readout fit budget (including temporal
matrix rows and null refits). No existing arbitrary five-fold/ten-fold or broad
hyperparameter budget is inherited.

Required software checks include source/phase/fold separation, frozen-transform
reuse, equal feature dimensions and target mapping, valid-window masks, consistent
class order/counts/weights, metric reconstruction from saved predictions and
negative controls. Computational verification does not validate missing acquisition
metadata or turn reused historical sources into new biological replication.

**Approval here is to ship the plots and agreed plan, not silently pick unresolved
settings or launch a biological fitting campaign.**

## Evidence and scope authority

- [Agreed project direction](../../project-direction.md), [analysis contract](../../analysis-contract.md), [research questions](../../research-questions.md).
- [Completed joint study](../../reports/cebra-full-trial-transfer/README.md): fixed4→3 component,29 units/7 session blocks; cue-only evaluation. Relative improvement, failed complete success rule—not an existing cross-phase generalization result.
- [Endpoint baseline](../../reports/start-goal-cebra-baseline.md) and [follow-up](../../reports/start-goal-autoresearch.md): historical source-safe conditional endpoint assays, not matched joint-training endpoint results.
- [Self-contained empirical review](review.html), [readable source](review.md), [reproduction/runbook](README.md).
