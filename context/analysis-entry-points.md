# Analysis Entry Points

Created: 2026-07-29

This note records candidate functions and files for the first place/view/conjunctive analyses. It is not a full API guide yet.

## Julia: GLM And Encoding Models

Primary file:

```text
Hippocampus.jl/src/glmfits.jl
```

Important types:

- `GLMFit`
- `GLMFitH{N}`

`GLMFit` appears to store separate coefficient/deviance results for:

- position;
- gaze;
- head direction;
- all variables together.

`GLMFitH{N}` is the more general current-looking object. It stores:

- coefficients `β`;
- log-likelihood matrix `ll`;
- regularization values `α`;
- train/test indices;
- spike counts;
- occupancy durations `dt`;
- selected model dimensions `dims`;
- joint bin indices `qidx`;
- convergence/refinement metadata.

Candidate dimension symbols seen in the code:

- `:p`: place/spatial bins;
- `:g`: gaze/view bins;
- `:hd`: head direction bins;
- `:null`: intercept/null baseline.

Likely first model comparisons:

```julia
GLMFitH((:p,), ...)
GLMFitH((:g,), ...)
GLMFitH((:p, :g), ...)
GLMFitH((:p, :g, :hd), ...)
GLMFitH((:null,), ...)
```

These are useful for asking whether a unit is better explained by place, view, head direction, or combinations.

Key functions:

- `get_num_spikes(vpvrp::ViewAndPlaceRepresentationNew, vpoc::ViewAndPlaceOccupancy)`
- `fit_glm(vpvrp::ViewAndPlaceRepresentationNew, jocc::JointOccupancy, unity_gaze_data::UnityRaytraceData; ...)`
- `GLMFitH(dims::NTuple{N,Symbol}; ...)`
- `GLMFitH(dims, jocc, unity_gaze_data, vpvrp; ...)`
- `get_X(qidx, dims, nrefinements)`

Interpretation:

- `ViewAndPlaceRepresentationNew` supplies spikes aligned to behavioral sample indices.
- `JointOccupancy` supplies joint place/view/head-direction occupancy bins and durations.
- `fit_glm` extracts spike counts and valid joint bins after filters such as minimum occupancy and speed.
- `GLMFitH` constructs design matrices from requested dimensions and fits regularized models with train/test splits.

## Julia: Conjunctive Analyses

Primary file:

```text
Hippocampus.jl/src/conjunctions.jl
```

Important types:

- `FieldConjunctions`
- `PlaceViewConjunction`
- `ViewPlaceConjunction`
- `PlaceAccountingView`

Core idea:

The conjunction code asks whether activity for one representation changes when conditioned on fields from another representation.

Examples:

- place-conditioned view activity;
- view-conditioned place activity;
- firing/activity inside a field versus outside a field;
- null comparisons using shuffled or equivalent field neighborhoods.

Candidate functions:

- `conjunctions(jm::JointMap, fields::SpatialResponseFields, viewidx)`
- `conjunctions_new(jm::JointMap, fields1, fields2; nshuffles=1000)`
- `conjunctions2(...)`
- `FieldConjunctions(jm::JointMap, fields1, fields2; ...)`
- `PlaceViewConjunction(; ...)`
- `ViewPlaceConjunction(; ...)`
- `Hippocampus.issignificant(...)`
- `plot_conjunction(...)`
- `plot_conjunctions(...)`

Interpretation:

- `PlaceViewConjunction` likely asks how view responses change inside place fields.
- `ViewPlaceConjunction` likely asks how place responses change inside view fields.
- `FieldConjunctions` is a more generic abstraction over two response-field types.

This is directly relevant to Hongyi's interest in cells or RNN units that encode both place and visual/view variables.

## Julia Objects To Trace Next

These appear central but need their own map:

- `JointOccupancy`
- `JointMap`
- `ViewAndPlaceOccupancy`
- `SpatialResponseFields`
- `GazeResponseFields`
- `SpatialMapNew`
- `ViewMapNew`

Likely files:

```text
Hippocampus.jl/src/replay.jl
Hippocampus.jl/src/response_fields.jl
Hippocampus.jl/src/spatial.jl
```

## Python Reference: PyHipp

Primary role:

`PyHipp` is older reference code, useful for understanding legacy data objects and time-alignment logic. It does not appear to be the active analysis path.

Useful modules:

- `PyHipp/PyHipp/aligning_objects.py`
  - Reads `eyelink`, `unityfile`, and `rplparallel`.
  - Aligns timing between markers by scaling intervals to Ripple timing.
- `PyHipp/PyHipp/rplparallel.py`
  - Ripple markers/timestamps reference.
- `PyHipp/PyHipp/eyelink.py`
  - EDF/Eyelink processing and missing-marker handling.
- `PyHipp/PyHipp/unity.py`
  - Unity behavior object.
- `PyHipp/PyHipp/umaze.py`
  - Navigation/maze behavior analysis.
- `PyHipp/PyHipp/vmplacecell.py`
  - Older place-cell style analysis.
- `PyHipp/PyHipp/spiketrain.py`
  - Spike train object/export reference.
- `PyHipp/PyHipp/raycast.py`
  - Converts Unity/Eyelink data for raycasting workflows.

## First Practical Analysis Path

For biological data:

```text
Spiketrain
RippleData
UnityRaytraceData
JointOccupancy
ViewAndPlaceRepresentationNew
GLMFitH / conjunctions
```

For RNN data, mirror the same structure:

```text
RNN hidden activations
Unity/RNN trial markers
Unity/RNN behavior-view samples
Joint occupancy bins
RNN unit event/activity table
GLMFitH-like model comparison / conjunctions-like conditioning
```

## Open Questions

- Can `GLMFitH` be reused directly for RNN activations, or should we implement a parallel model-analysis layer that borrows only the concepts?
- Are `JointOccupancy` and `JointMap` the right shared abstraction for both biological cells and RNN units?
- Does the first result need GLM model comparison, or is a simpler occupancy-normalized map plus null test a better first deliverable?
- Which conjunctive definition should be reported first: interaction GLM, conditional field increase, or both?

