# Analysis Contract

This document defines the minimum shared data shape for prospective-path
analysis and the later biological/artificial-agent comparison.

## Unit Of Analysis

The independent unit is a complete behavioral trial. Each trial links two
aligned sequences:

```text
cue-period population activity -> subsequent observed navigation path
```

For biological data, a population feature is a curated neuron/unit represented
by spike counts or firing rates. For model data, it is an RNN or other agent
hidden dimension represented by its activation.

Adjacent time bins are not independent samples. All bins from a source trial
must remain in one validation split.

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

Minimum model fields for H2:

```text
source_trial_id, cue_time_bin, hidden_unit_id, activation,
start_id, goal_id, cue_id
```

Cell identities may differ across sessions, but units within one claimed
population vector must be verified as simultaneous. A cross-session
pseudopopulation must be labeled as such and cannot answer trial-specific H1.

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

Every analysis should be able to produce results within each verified
simultaneous-recording group before any group-level synthesis. It should also be
able to produce:

- a start-and-goal-only path baseline;
- raw-population and PCA neural baselines;
- a trial-aware CEBRA-Time representation;
- optionally, a behavior-conditioned CEBRA representation;
- the same simple downstream path decoder for each neural representation;
- held-out path predictions and path-appropriate errors;
- within-start-goal permutation nulls;
- for compositional H1b analyses, matched cross-condition path-component
  contrasts and target-free neural/path representational dissimilarity matrices.

In behavior-conditioned CEBRA, path labels or continuous path features supervise
the embedding. A separate downstream decoder is still required to evaluate
held-out prediction.

## Supporting Analysis Objects

Where data permits, retain support for:

- occupancy maps and unit rate/activation maps;
- place, view/visual, and conjunctive tuning;
- nuisance-variable models for heading, gaze, action, speed, trial time, and
  session;
- complete-trial train/test splits and null distributions.

These characterize and control H1; they are not the primary research question.

## Current Data Boundary

The current local JLD2 export starts at cue offset and contains selected
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

## Open Decisions

- graph granularity and path-distance metric;
- whether stable path clusters exist;
- handling of unsuccessful and timeout trials;
- cue window and neural bin size;
- decoder target and primary metric;
- trial-, session-, and start-goal-held-out evaluation levels;
- Python, Julia, or mixed implementation.
