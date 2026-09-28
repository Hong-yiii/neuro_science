# Analysis Contract

This document defines the data and evaluation contract for prospective-path
analysis. The [September27 agreed direction](project-direction.md) retains H1,
removes artificial-agent H2, narrows the encoder comparison and leaves decoder
choice open. This is not a frozen new-run protocol.

## Unit Of Analysis

The independent unit is a complete behavioral trial. Each trial links two
aligned sequences:

```text
cue-period population activity -> subsequent observed navigation path
```

A biological population feature is a curated neuron/unit represented by spike
counts or firing rates. PCA/LDA/CEBRA coordinates are derived features, not new
neurons or independent observations. Artificial-agent activation export is no
longer an active requirement.

Adjacent time bins are not independent samples. All bins from a source trial
must remain in one validation split. Trials and units are nested within recording
sessions; serial dependence and session structure must be respected in uncertainty
and null calculations. Neither cells nor sessions should silently be counted as
independent animals.

### Complementary condition-level contract (2026-09-08)

A source-safe pseudopopulation is a legitimate candidate evaluation object when
large simultaneous recordings are unavailable. Retain the real source table
(`source_trial_id × recorded unit × cue bin`, with session, exposure, endpoint,
behavior-defined target and provenance), then a separate assembly manifest linking
each synthetic row/session block to its actual source. Its target is reproducible
condition-level response differences beyond endpoints, not reconstruction of one
real simultaneous trial. Fixed195 is the selected-unit scope, not a requirement
that every analysis have195 fully observed columns.

Split actual trials before assembly and preserve a session block's source across
its cells and bins. Missing/unrecorded values remain masked, not zero. Use only
training data for learned transformations and target/support choices, with
source/session-aware uncertainty and matched conditional nulls. Future-label
matching defines a conditional benchmark; it does not turn its rows into an
operational unknown-label population measurement. Same-session grouping is not
proof of simultaneous recording, and assembly cannot recover unrecorded
cross-session noise correlations.

Per-unit real-trial checks and source-safe pseudopopulation analyses are
complementary; individual-cell significance is not required for population
information. See the [agreed direction](project-direction.md) and
[completed study](professor_updates/path_generalization_20260907/README.md).

The next methods artifact must trace source ledger → folds → matching pools →
session-block draws → pseudorow lineage → phase tensors, with a worked example
and runnable checks. Reuse existing code/tests; do not launch a broad validation
campaign by default. Check source overlap, timing/count/shape/label consistency,
missingness and reconstruction of lineage. Passing mechanical checks is not
proof of simultaneity or biological validity.

## Required Trial Identity And Events

Each trial should expose:

- `source_trial_id` and `previous_trial_id`;
- `session_id`;
- `simultaneous_recording_group`;
- trial index or time within session;
- `cue_onset` and `cue_offset` in the neural clock;
- navigation onset and end;
- `start_id`, `goal_id`, and `cue_id` as categorical labels;
- previous goal and previous-trial success where trials are sequentially linked;
- current success or timeout status and inclusion reason;
- links between neural, Unity behavior, and path samples.

`cue_id` means the identity of the visual/instruction stimulus displayed during
the cue period. Its relationship to `goal_id` must be verified from the task
protocol rather than assumed; retain both fields even if they are redundant in
the current experiment.

## Cue-Period Population Tensor

Preferred conceptual shape:

```text
trial x cue_time_bin x unit
```

Minimum biological fields:

```text
source_trial_id, session_id, simultaneous_recording_group,
cue_time_bin, cell_id, spike_count, start_id, goal_id, cue_id
```

Cell identities may differ across sessions; a claimed **real-trial** population
vector needs verified simultaneity. Label cross-session pseudopopulations
explicitly; they cannot fulfill exact trial-specific H1. Selected195 describes
the archive scope, not a mandatory fully observed195-column panel. Document the
actual matching key; current component-conditioned rows are not necessarily
matched by whole-route identity.

## Joint Cue/Navigation Training And Folds

Both phases of one real source trial and all their derivatives share one fold.
Assign folds before assembly or learned transformations. Only training-source
navigation activity may enter joint encoder learning. For the **primary encoder
comparison**, decoder training and held-out predictions use cue inputs only.
The separately agreed September28 supporting validation adds window-specific
navigation decoding and frozen within-/cross-phase transfer; see the
[validation plan](professor_updates/research_review_20260928/validation-plan.md).
In that assay, fit each decoder on the designated training-source phase/window,
then freeze the encoder, scalers, decoder, thresholds and calibration across
held-out evaluation windows/phases. Fit separate readouts for different encoder
coordinate systems. Match feature dimensions/target semantics and report support
at every window. No held-out navigation may enter fitting, alignment or selection.
This is a design extension, not an executed analysis or a frozen new-run protocol. Preserve source/bin/phase lineage,
clock units, boundary handling, masks and the chosen cross-session phase
alignment; normalized progress is not a simultaneously observed trajectory.

The next encoder comparison uses CEBRA-Time, cue-only versus joint training,
two predefined checkpoints and one configuration. Freeze phase exposure weights,
update counts, preprocessing policy, seed budget and readout policy before fitting.
Saving two checkpoints need not require two independent training trajectories.
Shared parameters and within-phase Time positives do not prove cross-phase
biological alignment; sequential navigation pretraining/cue fine-tuning is a
different intervention, not implicitly authorized.

Fold count/grouping and treatment of serial dependence remain open. Check class,
endpoint and session support before selecting a scheme; never split synthetic
rows while allowing their real sources to overlap. Session holdout changes
feature identity when different neurons were recorded, so it needs a separate
admissible design. Fit all transforms/readouts inside training folds; keep model
selection off outer evaluation folds. Exposed-source resplits remain exploratory.

## Subsequent Path Table

Preferred conceptual shape:

```text
trial x navigation_sample
```

Minimum fields:

```text
source_trial_id, navigation_sample, time_ms,
position_x, position_y_or_z, spatial_bin_id
```

Include when available:

- heading and speed;
- gaze coordinates, fixation mask, view/raycast bin, and viewed object;
- action or joystick input;
- reward and timeout details.

These variables can characterize paths and test sensory or motor confounds.

## Path Representation

**Path** means the observed ordered movement through the maze. **Trajectory
class** is reserved for the previous analysis's `(start, goal)` category.

A maze graph is the current proposed measurement method:

- the maze is one graph;
- nodes represent spatial regions;
- edges represent valid transitions;
- a trial path is an ordered walk through the graph.

Graph granularity, path clustering, the criterion for distinct paths, and the
primary distance metric remain open. The scientific hypothesis must not depend
on one graph construction.

Rules inherited from the verified spatial export:

- `spatial_bin_id` is categorical and mesh-topological, not ordinal;
- bin `0` is invalid/filtered and is not a location;
- the current refined mesh IDs are not row-major 40 x 40 coordinates;
- Euclidean analysis requires verified centroids;
- topology-aware analysis requires verified mesh or graph adjacency.

Path transformations, graph construction learned from data, clustering, and
other preprocessing must be fitted using training trials only. Create and hash
source-trial train/validation/test assignments before adaptive path-metric or
contrast selection. Use training/validation behavior to select rules; apply the
frozen mapping once to the untouched test behavior. Target labels must be
created from behavior alone, never jointly from neural activity.

Current exploratory place195 path work uses
`docs/geometry/maze_mesh_centroids_1344.txt` as the authoritative fine centroid
map: line number is node ID, `0` is invalid, and primary fine adjacency is
cardinal 4-neighbor adjacency at `0.625` Unity-coordinate spacing. Timeout trials
are dropped for the planned experiment. When `start_id` is inferred from the
previous goal, the primary endpoint-labelled subset is `success_after_success`:
the previous and current trials both ended successfully.

## Component Assay A And Ordered-Path Target B

A predicts a behavior-defined interior component/segment. B, the desired
capability, predicts an ordered graph walk. Both remain in scope; endpoint
classification does not replace them. Define a target-appropriate held-out
metric and start/goal-only predictor for each task. A is a simpler assay, not a
statistical baseline for a different B task, and not a universal significance
gate before B can be considered.

For B, first define meaningful graph granularity/order/revisit semantics and a
valid target for every evaluation object. Component-conditioned pseudorows may
combine different full paths: one contributing trial's path cannot silently
become the row's ground truth. Demonstrate route-level support and distinguish
condition-level route targets from genuine single-trial prediction. A canonical
endpoint-derived route is not incremental neural information. Metric, target
construction and success threshold must be specified before fitting.

## Shared Path Components Across Conditions

When exact route variation within one `(start, goal)` condition is sparse, a
complementary structural analysis may compare reusable path components across
conditions. A simple behavior-only representation is a directed-edge indicator
or count vector

```text
trial x directed_maze_edge
```

with ordered edge sequences retained when branch order or repeated visits
matter. Report initial, middle, and terminal overlap separately. An obligatory
prefix from one start is not, by itself, evidence beyond start coding; likewise,
an obligatory suffix can be explained by goal.

A pairwise analysis table should retain at least:

```text
trial_i, trial_j, session_i, session_j,
same_start, same_goal, same_start_goal, same_cue,
initial_edge_overlap, middle_edge_overlap, terminal_edge_overlap,
full_path_distance, neural_distance
```

Useful matched contrasts compare high- and low-overlap paths while holding start
or goal relationships fixed. Where data permit, paths with different starts and
goals but a shared middle segment provide a stronger separation from endpoint
identity. Cue identity, session, heading, view, and other available nuisance
variables must also be controlled.

Pairwise matrix entries are not independent observations. Uncertainty and nulls
must permute or resample source trials, sessions, or animals rather than treating
all trial pairs as independent. Before neural fitting, audit whether path-overlap
features are distinguishable from start and goal; near-collinearity is an
identifiability limit, not a modeling problem.

## Primary Evaluation Objects

Real-trial population analyses should expose results within each verified
simultaneous-recording group before group-level synthesis. For a condition-level
pseudopopulation analysis, instead retain session-block source support, assembly
lineage and source-aware uncertainty; report per-unit/session diagnostics where
estimable without requiring individually significant units or unrecorded
simultaneity. The relevant evaluation should also be able to produce:

- a start-and-goal-only path baseline;
- PCA and supervised LDA baselines, with their task-specific role specified;
- CEBRA-Time cue-only/joint representations at two predefined checkpoints;
- a bounded, matched decoder/readout policy, **still to be chosen**;
- held-out path predictions and path-appropriate errors;
- within-start-goal permutation nulls;
- for compositional H1b analyses, matched cross-condition path-component
  contrasts and target-free neural/path representational dissimilarity matrices.

CEBRA-Behavior is historical, not an optional new arm in this narrowed study.
Time's objective omits target labels, but existing assembly uses them, including
at evaluation. PCA does not use target labels in its transform; LDA does, with
at most K−1 discriminant dimensions for K classes. Fit it only on training labels;
its role for B is unresolved. Do not infer intrinsic geometry from LDA separation.
Raw features remain a possible simple reference, not another tuning grid.

Choose a justified, bounded null/uncertainty scheme for the actual target and
full label-dependent construction. Necessary leakage/null checks are not removed
by the decision to reduce candidate encoder settings. List all planned fitting
instances before execution, including readouts and null refits.

## Supporting Analysis Objects

Where data permits, retain support for:

- occupancy maps and unit rate/activation maps;
- place, view/visual, and conjunctive tuning;
- nuisance-variable models for heading, gaze, action, speed, trial time, and
  session;
- complete-trial train/test splits and null distributions.

These characterize and control H1; they are not the primary research question.
The mentor's cue/navigation selectivity and rotation question remains open
pending task-variable support, validation design and the referenced literature;
it is not an adopted phase-geometry hypothesis.

## Current Data Boundary

The legacy local JLD2 export starts at cue offset and contains selected
single-cell navigation-period spike counts plus spatial-bin IDs. It lacks the
cue period, start/goal labels, and a verified synchronized population matrix.
It therefore cannot instantiate this contract or test H1.

A separate 2026-08-30 note describes a bounded `20181105/session01` snapshot
with all six listed spike-timestamp files, 404 matching Ripple/Unity/Eyelink
trial-code rows, native Unity paths, and derived gaze/raycast data. That exact
six-unit directory is not present in the current checkout; treat the note as a
receipt for that earlier transfer, not as the active all-session input root.

The current active native-data root is
`data/raw/lab_server/cortex_picasso_misc_place195_20260830/`. It contains 58
sessions, 195 place-selected `spiketrain.mat` files, and one Ripple, Eyelink,
and native Unity log per session, but no `unity_raytrace.jld2` files. It supports
all-session importer/QC work: preserving cue-window spike events/counts and
native Unity path samples by source trial. It still does not pass this contract's
scientific gate: selected-cell provenance, unverified recording groups,
marker-label semantics, absent gaze/raycast controls, subject/session metadata,
and trial-level QC remain open. Clock-discrepant trials such as 20181105 trial
178 must be retained with explicit QC flags rather than silently repaired or
dropped.

The September exploratory import/graph/pseudopopulation/CEBRA studies are now
completed and documented in the [study package](professor_updates/path_generalization_20260907/README.md).
They do not remove the metadata/observability limits above. The original test was
exposed during early V6 reconnaissance and is not pristine; references above to
an untouched test describe a prospective design, not the status of that dataset.

## Open Decisions Before A New Run

- A's component/segment, B's target/feasibility, graph granularity and path metric;
- cue window/binning, cohort and handling of unsuccessful/timeout trials;
- source-fold grouping/count, temporal dependence, exposure and support checks;
- two checkpoint counts, one encoder configuration, phase weighting and seed policy;
- decoder type/training policy, baseline dimensions/roles (especially LDA for B);
- primary metric, meaningful improvement, null/uncertainty plan and total fit budget;
- phase-selectivity/rotation literature and interpretation after mentor input.

See [next-session sequence](project-direction.md#7-next-session-resolve-document-then-proposenot-launch).
No new biological fitting, data expansion or artifact migration is authorized by
this contract update.
