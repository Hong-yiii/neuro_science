# Biological Dataset and Experimental Setup Reference

Last verified from local files: 2026-08-03
Status: canonical for dataset facts and limitations only

For the active prospective-path question, use
[`research-questions.md`](research-questions.md). For the cue-population and
subsequent-path data required to test H1, use
[`analysis-contract.md`](analysis-contract.md).

## Purpose

This document describes the biological navigation dataset currently available in
this workspace, the larger experimental pipeline implied by the lab's active
Julia code, and the limits on what can presently be claimed. It is intended to
be copied into another LLM when asking whether published methods or findings are
applicable to this dataset.

The central distinction is:

- **Received data:** a small derived, single-cell, place-bin export that has been
  inspected locally.
- **Upstream experiment and processing:** neural, Unity behavior, and Eyelink
  streams represented in `Hippocampus.jl`, but not all of those streams are in
  the received export.
- **Unknowns:** experimental metadata that cannot be recovered safely from file
  names or code and must be confirmed with the lab.

Do not describe the current files as a full multimodal or population dataset.

## One-paragraph description

The lab dataset comes from a first-person Unity virtual-navigation experiment
with hippocampal single-unit recordings, task markers from a Ripple neural
recording system, and Eyelink gaze/fixation/saccade measurements. The local code
represents a square virtual maze with four internal pillars and six animal-image
landmarks. A trial has three task events: start/cue identity (`1x`), cue offset
and navigation onset (`2x`), and either successful completion (`3x`) or timeout
(`4x`), with the same final digit identifying the cue/landmark condition within
that trial. The main neural-behavior alignment normally analyzes the navigation
period from event 2 to event 3/4. Sorted spike timestamps are aligned to
Unity/raycast samples, allowing each spike to be associated with position, head
direction, three-dimensional gaze target, fixated object, and fixation status.
The data received so far is much narrower: one JLD2 file per preselected
place-responsive cell, containing ragged per-trial vectors of spike counts and
matching spatial-bin IDs. The best-verified example contains 395 retained trials
and 65,576 samples at an explicit 20 ms bin size. It does not contain raw physical coordinates, gaze/view, heading, actions,
rewards, participant metadata, or a synchronized multi-cell population matrix.
Its spatial-bin integer is a 1-based index into a refined floor mesh, so an
approximate `(x,y)` location can be recovered as that mesh element's centroid
when the exact mesh version and refinement parameters are available.

## Evidence labels used below

- **Observed:** directly inspected in the two local JLD2 files or cell list.
- **Code-established:** explicit in the checked-out `Hippocampus.jl` processing
  code, but not independently verified against the received raw experiment.
- **Lab-provided:** stated in the professor's message recorded in local notes.
- **Prior-write-up:** stated in the previous student's 20-page `Analysis
  Write-up.pdf`; informative but not equivalent to raw-data verification.
- **Inference:** plausible interpretation that must not be presented as fact.
- **Unknown:** not available in the current workspace.

## Experimental setup

### Subject and recording target

| Property | Current knowledge |
| --- | --- |
| Organism | **Unknown.** Code comments refer to a “monkey,” so nonhuman primate is likely, but species and subject count are not present in the received export. |
| Number, sex, age, or identifiers of subjects | **Unknown.** |
| Neural target | Hippocampus at the workspace/repository level; exact hemisphere, subfield, depth, and anatomical verification are **unknown** for these files. |
| Recording modality | Extracellular action-potential recordings processed into sorted single-unit spike timestamps (**code-established**). |
| Electrode/array details | File paths use `array01`–`array03`, `channelNNN`, and `cellNN`; hardware model, channel count, implant geometry, and simultaneous-recording groups are **unknown**. |
| Spike sorting and curation | Spike timestamps are already represented as cells/units. Sorting algorithm, quality thresholds, manual curation, and whether curation is final are **unknown**. |

A “cell” here is a sorted unit, not a direct measurement of a biological cell's
identity or morphology.

### Virtual environment

The checked-out Unity analysis code contains the following geometry
(**code-established; exact version for the received export still needs
confirmation**):

- first-person 3-D virtual environment;
- square outer boundary from approximately `-12.5` to `12.5` on each horizontal
  axis (25 by 25 Unity coordinate units);
- four square internal pillars, each approximately 5 by 5 units, occupying the
  four quadrants;
- pillar colors: blue, yellow, green, and red;
- six animal-image posters/landmarks: camel, cat, crocodile, donkey, pig, and
  rabbit;
- position is stored on two horizontal Unity axes; some code swaps Unity axes,
  so axis naming must be verified before calling them `(x,y)` or `(x,z)`;
- head direction is stored as an angle, with raytrace code converting degrees to
  radians;
- gaze is raycast into the 3-D maze to obtain a point of regard and the name of
  the fixated object.

The code includes hard-coded geometry plus TODO comments questioning whether
some values are the latest. Treat these values as a processing-model description,
not final experimental metadata.

### Trial structure

The event scheme is explicit in `Hippocampus.jl/src/unity.jl` and
`Hippocampus.jl/src/utils.jl`:

| Event column | Marker family | Meaning in code |
| ---: | --- | --- |
| 1 | `1x` | trial start; `x` identifies a poster/cue condition |
| 2 | `2x` | cue offset; cue for the participant to start navigating |
| 3 | `3x` or `4x` | success/end (`3x`) or timeout (`4x`) |

The minor digit `x` must agree across the three markers in a trial. Eyelink
messages use the strings `Start Trial`, `Cue Offset`, `End Trial`, and `Timeout`.

The previous student's write-up adds (**prior-write-up**):

- six posters serve as start/goal locations;
- start and goal differ, giving 30 ordered `{start, goal}` conditions;
- sessions average approximately 400 trials, roughly 13–14 per condition;
- the next trial starts at the preceding trial's goal poster;
- the cue phase lasts 1 second and navigation follows cue offset;
- the screen fades to black during the middle of the inter-trial interval;
- the preceding goal/current start poster is visible at the prior trial end and
  may remain partly visible behind the cue image.

The principal alignment object, `ViewAndPlaceRepresentationNew`, defaults to
`trial_start=2`. Therefore its analysis window starts at cue offset/navigation
onset and ends at the third event, whether that third event denotes success or
timeout. The current derived export was generated with `trial_start=2` and
`correct_after_correct_only=true`: retained trials are successful trials whose
immediately preceding trial was also successful. This is a selected subset of
behavior, not all attempted trials.

Exact instructions, navigation controls, success criterion, timeout duration,
reward type, full inter-trial timing, and participant training history are
**unknown**. Joystick control has been discussed as a possibility but is not
established by the received files; do not assume it.

### Synchronized acquisition streams

The upstream code expects four streams:

1. **Ripple neural timing**
   - session-level `rplparallel.mat`;
   - trial marker matrix and timestamp matrix, conceptually
     `n_trials × 3_events`;
   - provides the neural-system clock used to select trial spikes.
2. **Sorted spikes**
   - cell-level `spiketrain.mat` or `spiketrain.csv`;
   - fields include `timestamps`, a reference string, and component count;
   - stored timestamps are divided by 1,000 before the main alignment, indicating
     milliseconds converted to seconds.
3. **Eyelink eye tracking**
   - day-level `eyelink.mat`, derived from EDF data;
   - trial messages/timestamps, analog sample times, screen gaze `x/y`, fixation
     intervals, saccade intervals, and saccade start/end positions;
   - recorded eye and screen bounds are retained in a header.
4. **Unity behavior and raytrace**
   - session-level Unity position/head-direction records plus a day-level
     `unity_raytrace.jld2` derived by default from
     `unityfile_eyelink_new.csv`;
   - trial-indexed timestamps, position, head direction, raw 2-D gaze,
     three-dimensional gaze point, fixated-object label, and fixation mask;
   - default fixation filtering excludes `HintImage`, `CueImage`, and `Robot`.

### Neural-behavior alignment

For each cell and trial, the code:

1. obtains trial-relative Unity/raycast samples;
2. selects sorted spikes between Ripple event 2 and event 3 by default;
3. subtracts the Ripple event-2 timestamp to obtain trial-relative spike time;
4. maps each spike to the most recent preceding behavioral sample;
5. optionally retains only fixation-associated spikes;
6. stores a per-trial spike-time vector and a same-length vector of behavioral
   sample indices.

The upstream aligned object is therefore:

```text
trial
├── events:       spike times in seconds relative to navigation onset
└── placeviewidx: index of the corresponding Unity/raycast sample
```

This alignment makes multimodal analyses possible upstream, but those fields are
not present in the current place-bin export. The checked-out branch currently
has a return-arity mismatch: `UnityRaytraceData.get_trial` returns six values,
while this constructor destructures five. The intended alignment is clear from
surrounding code and existing derived files, but this exact constructor should
be fixed or version-matched before rerunning it.

## Current local data inventory

### Curated cell list

Observed in
`data/raw/lab_exports/place_spatial_bins_f1526be5/place_selective_cells_new.txt`:

- 195 unique cell paths;
- 58 recording dates from 2018-07-02 through 2018-11-05;
- every listed path uses `session01`;
- arrays: 99 paths from `array01`, 59 from `array02`, 37 from `array03`;
- 18 distinct channel labels, ranging from `channel006` to `channel093`;
- sorted-unit labels: 129 `cell01`, 55 `cell02`, 9 `cell03`, and 2 `cell04`;
- 1–8 listed cells per recording date (median 3).

This list is explicitly place-selective. It is a case-enriched subset suitable
for a positive-control analysis of known place coding. It cannot estimate place
cell prevalence, population-wide effect sizes, or false-positive rates in all
recorded units.

The professor clarified on 2026-08-27 that the 195 cells were selected for
spatial tuning. Individual cells could additionally have view tuning or
place-view conjunctions, but the amount of overlap was not quantified; the list
must not be described as a broadly view- or conjunction-selected population. The
professor recommended the 195 spatial cells as the first set for decoding space.
A broader all-recorded-cell list is available upstream at
`/Volumes/Hippocampus/Data/picasso-misc/AnalysisHM/Current Analysis/cell_list.txt`,
but has not been received or audited locally.

The previous student's broader cue/inter-trial analysis assembled 233 cells from
July–November 2018 into 314 artificial pseudotrials by matching ordered
start-goal conditions across sessions. That historical 233-cell
pseudopopulation is distinct from the current 195-cell selected list and is not
a simultaneously recorded population. See
`context/previous-student-analysis.md` for its construction and caveats.

A date/session/array path hierarchy does not by itself prove which units were
recorded simultaneously. A population tensor must not be created until shared
trial IDs, time windows, and simultaneous acquisition are verified.

### File-level schema

Each received JLD2/HDF5 file corresponds to one sorted unit and contains a scalar
`data` record. In the best-verified format:

```text
cell_file
└── data
    ├── spikecounts -> references to one Float64 vector per retained trial
    ├── bins        -> references to one Int64 vector per retained trial
    └── trialidx    -> original retained trial indices
```

Conceptually:

```text
spikecounts[t][k] = number of sorted spikes assigned to sample/bin k in trial t
bins[t][k]        = 1-based floor-mesh element index aligned to that response
trialidx[t]       = source trial index retained in output row t
```

The bin ID encodes location indirectly. In the Julia path, position is assigned
to the nearest element of
`Shadow("xy")(floor_topology3(nrefinements=nrefinements.p))`; the current
verified export records `nrefinements.p=3`. Executing the export-time mesh code
produced 1,344 navigable elements on 40 × 40 lattice centers: 1,600 nominal cells
minus four 8 × 8 pillar footprints. For valid mesh ID `i`, the representative
coordinate is `centroid(m_floor[i])`. This is the center of a 0.625-unit spatial
patch, not the original continuous Unity coordinate.

The mesh element list is **not row-major**. `divmod(i - 1, 40)` is invalid for
this JLD2 export because `QuadRefinement` groups children by parent mesh element.
A Docker reconstruction with Meshes.jl 0.57.25 found no mesh ID equal to its
corresponding full-grid row-major ID. It also turned the first trial's consecutive
valid transitions into a median 0.625-unit step; row-major interpretation created
jumps up to 23.76 units. Bin `0` is an invalid/filtered sentinel, not `(0,0)`.

The previous student's older `vmpv.mat` notebooks did use literal row-major IDs
from 1 to 1,600. The old and current formats share 40 × 40 geometry but not ID
ordering. See `notes/data_inspection/spatial_bin_ordering.md` for the executed
verification, conversion formula, and package-version caveat.

Trials are ragged: `T_t` varies by trial and can be zero. Within each trial,
`spikecounts[t]` and `bins[t]` have matching lengths.

### Best-verified example: hash `f1526be5`

Path:

```text
data/raw/lab_exports/place_spatial_bins_f1526be5/examples/
20181105_session01_array01_channel029_cell01/
spike_count_per_spatial_bin_f1526be5.jld2
```

Observed generation metadata:

```text
git commit:                    38f1684a0bcd1a1a10f149b4a4524a914558a34b-dirty
binsize:                       0.02 s
trial_start:                   2
correct_after_correct_only:    true
min_speed:                     1.0
min_place_duration:            0.05 s
min_place_observations:        5
min_view_duration:             0.02 s
min_view_observations:         5
place/view refinements:        p=3, g=2
do_compress_trajectories:      false
```

The file embeds a large uncommitted Git patch, so the commit hash alone does not
fully reproduce generation.

Observed shape and response statistics:

| Property | Value |
| --- | ---: |
| Retained trials | 395 |
| Source trial-index range | 2–404 |
| Missing indices inside that range | 87, 88, 137, 138, 230, 231, 330, 331 |
| Empty trial vectors | 1 |
| Total 20 ms samples | 65,576 |
| Samples/trial: min / median / mean / max | 0 / 163 / 166.02 / 433 |
| Approx. duration: median / max | 3.26 s / 8.66 s |
| Total spikes | 1,441 |
| Spikes/trial: min / median / mean / max | 0 / 3 / 3.65 / 19 |
| Nonzero samples/trial: median / mean / max | 2 / 2.70 / 14 |
| Maximum count in one 20 ms sample | 5 |
| Spatial-bin ID range | 0–1,342 |
| Unique observed spatial-bin IDs | 453 |
| Samples labeled spatial bin `0` | 12,037 (18.36%) |

Interpret this as:

```text
one selected cell
  -> 395 variable-length retained trials
    -> 20 ms temporal sample
      -> scalar spike count + categorical spatial-bin ID
```

Biological responses are sparse counts. Adjacent samples are highly correlated
and are not independent observations.

### Second example: hash `921269fc`

Path:

```text
data/raw/lab_exports/place_spatial_bins_f1526be5/examples/
20181105_session01_array02_channel045_cell01/
spike_count_per_spatial_bin_921269fc.jld2
```

Observed:

- 395 vectors, one empty;
- 7,909 total vector entries;
- vector length min/median/mean/max: 0/19/20.02/51;
- 2,308 total spikes;
- spatial IDs 21–1,342, with 452 unique values;
- no stored `trialidx`; the local loader's `0..394` values are generated fallback
  row numbers, not verified source trial IDs;
- generation commit `b93f635b504f3cd1bf4d6bf9254369235e0ef16f-dirty`;
- arguments include `trial_start=2`, `correct_after_correct_only=true`,
  `min_speed=1.0`, and the same occupancy/refinement thresholds, but do not
  record `binsize` or `do_compress_trajectories`.

Do **not** infer 20 ms durations from this second file. Its hash, commit, fields,
and sequence lengths differ from the verified export. It may reflect an older or
compressed trajectory representation. It cannot currently be stacked with the
`f1526be5` example.

## What is measured, derived, and inferred

| Variable or claim | Status |
| --- | --- |
| Extracellular voltage | Raw measurement upstream; not received locally |
| Spike timestamp | Derived through event detection and spike sorting upstream |
| Spike count in current export | Further derived by assigning spikes to retained temporal/spatial bins |
| Unity position/head direction | Behavioral/game-engine measurement upstream; not received locally |
| Eyelink screen gaze | Eye-tracker measurement upstream; not received locally |
| 3-D gaze point or object | Derived by raycasting gaze through the Unity scene |
| Fixation/saccade labels | Derived from Eyelink event processing |
| Spatial-bin ID | Derived categorical label supplied in current export |
| Physical maze coordinate | Raw coordinate is not supplied; an approximate bin-center coordinate is derivable from the exact floor mesh and bin index |
| Occupancy-normalized firing rate | Not supplied; compute as spikes divided by valid occupancy time |
| Place selectivity | Inference requiring occupancy correction, held-out stability, and null controls; cell list is preselected on this property |
| View, goal, memory, intention, or strategy coding | Not directly observed and not testable from the present place-only export |
| RNN–neuron equivalence | Not established and not the intended claim |

## Data currently absent from the derived export

The local JLD2 files do not provide:

- subject/species/session metadata beyond path labels;
- raw continuous `(x,z)` coordinate for each sample;
- an exported spatial-bin centroid/geometry/adjacency lookup (reconstructable
  from the exact Julia mesh version);
- explicit export documentation for bin `0`; code behavior indicates an
  invalid/filtered sentinel;
- head direction or speed;
- raw screen gaze, 3-D gaze, view/raycast bin, fixation mask, or object label;
- cue/goal identity, trial phase, success/timeout flag, or reward;
- joystick/control input or derived action;
- raw spike timestamps or waveforms;
- unit-quality metrics;
- non-place-selected cells;
- proof of simultaneous recording or shared time axes across files;
- an RNN checkpoint or rollout.

## Safe analysis scope with current files

The `f1526be5` example supports a narrow single-cell place-analysis prototype:

1. calculate occupancy per spatial-bin ID from valid 20 ms samples;
2. calculate firing rate as summed spikes divided by occupancy seconds;
3. impose minimum occupancy;
4. split by complete trials, never random rows;
5. measure held-out rate-map stability or held-out position prediction;
6. compare against within-trial circular time shifts or appropriate label
   shuffles that preserve temporal autocorrelation;
7. report that the cell was preselected as place-responsive.

It does not support a complete view/place/conjunctive analysis or population
geometry yet.

## Position units and decoding resolution

Physical units such as meters are not required for place prediction. Unity
coordinates, normalized coordinates, or shared categorical place bins are
sufficient provided that biological and model samples use the same mapping.
Arbitrary units preserve the question of whether population activity predicts
where the subject or agent is in the task environment.

The prior write-up describes the original place representation as 40 × 40. This
is a maximum nominal resolution of 1,600 grid locations; the navigable mesh has
fewer valid patches because pillars and invalid space are excluded. The verified
single-cell example contains 453 unique bin IDs (452 nonzero) and only 1,441
spikes,
with strongly uneven occupancy. Therefore 40 × 40 should be retained as the
highest available resolution, not assumed to be the best first prediction
target.

Use a multiresolution decoding ladder:

1. begin with coarse 5 × 5 or 10 × 10 place targets;
2. evaluate with complete held-out trials and occupancy-balanced metrics;
3. increase to 20 × 20 and then 40 × 40 only when training occupancy,
   held-out-bin coverage, and population spike support remain adequate;
4. report performance at every retained resolution rather than selecting the
   best resolution on the test set.

For modeling and evaluation:

- treat `spatial_bin_id` as a categorical or mesh-topological label, never as an
  ordinal scalar where bin 100 is assumed closer to bin 101 than bin 200;
- exclude bin `0` from valid position targets;
- classification needs only shared bin labels;
- coordinate regression or Euclidean error needs mesh-centroid coordinates;
- topology-aware error needs mesh adjacency or geodesic distance;
- arbitrary coordinate scale is acceptable for distance metrics, but state the
  scale or normalize distance by maze width/diameter;
- apply exactly the same binning or centroid normalization to biological and RNN
  trajectories.

Fine 40 × 40 decoding requires an aligned multi-cell population. The current
single-cell example is useful for rate maps and pipeline validation but is not
expected to support robust fine-grained position prediction by itself.

## Shape required for broader techniques

### Biological target

```text
behavior table: trial × time
response tensor: trial × time × simultaneously_recorded_cell
valid-time mask: trial × time
```

Minimum long-table fields:

```text
session_id, trial_id, time_start_ms, time_end_ms,
position_x, position_z, spatial_bin_id, heading, speed,
gaze_x, gaze_y, view_bin, fixated_object, fixation_mask,
cue_id, goal_id, trial_phase, success, timeout,
observed_displacement, control_input,
cell_id, spike_count
```

### RNN target

```text
session_or_seed, trial_id, native_step, time_start_ms, time_end_ms,
position_x, position_z, spatial_bin_id, heading, speed,
view_bin, observation, action, goal, reward, done, trial_phase,
hidden_unit_id, hidden_activation
```

Keep the model's native time steps, then create an explicit resampling layer.
Equal array lengths do not establish equivalent time bases.

## Applicability checklist for comparison with other studies

When another LLM evaluates a published technique, require it to answer:

1. Does the method accept spike counts, or does it require calcium imaging, LFP,
   raw waveforms, continuous firing rates, or simultaneous populations?
2. Does it work with one unit at a time, or require many simultaneously recorded
   units?
3. Can it handle ragged trials and explicit masks?
4. What independent sample does validation use: time bins, trials, sessions,
   subjects, or animals?
5. Does it require physical coordinates/geometry rather than categorical bins?
6. Does it require gaze, heading, action, reward, or task labels absent here?
7. Does it assume an unbiased unit sample? Our 195-cell list is preselected for
   place responsiveness.
8. Does it tolerate variable cell identities across sessions, or require a
   stable tracked population?
9. How does it control temporal autocorrelation and uneven occupancy?
10. Does it separate position from correlated view, heading, speed, cue, goal,
    action, and trial time?
11. Can it use condition averages when direct time-point pairing between biology
    and an RNN is unavailable?
12. What minimum number of independent trials, sessions, and units is required?
13. Does it offer held-out and shuffled/null evaluation rather than only
    in-sample visualization?
14. Is its output descriptive, predictive, representational, or causal? The
    current biological data is observational.
15. Which missing fields must be acquired before the technique becomes valid?

## Recommended claim boundary

With current data, a defensible statement is:

> We have a derived single-cell place-coding export from hippocampal virtual-
> navigation recordings. For one verified configuration, each selected cell is
> represented across ragged successful-after-successful navigation trials by
> 20 ms spike counts and matching categorical spatial-bin IDs. This supports
> occupancy-corrected, trial-held-out place analyses. It does not yet support an
> unbiased population estimate, synchronized population analysis, gaze/view or
> action-conditioned analysis, or direct comparison to RNN population geometry.

## LLM-ready context block

Copy the following with this document when asking another LLM to compare methods:

```text
Treat the attached dataset card as the authoritative description of our current
data. Distinguish (1) fields actually present in the local derived export,
(2) multimodal fields available only in the upstream processing design, and
(3) unknown metadata. Do not assume that 195 listed cells are simultaneous or
unbiased; they were selected as place-responsive. Do not treat adjacent 20 ms
bins as independent samples. Do not infer physical geometry from categorical
spatial-bin IDs; treat bin 0 as invalid/filtered while noting that lab
confirmation is pending. For every proposed technique,
state: direct applicability now, additional data required, necessary adaptation,
validation unit/split, null controls, sample-size assumptions, and the strongest
defensible claim. Prefer trial-held-out and session-held-out tests. Explicitly
flag any method requiring synchronized populations, gaze/view, heading, action,
reward, raw waveforms/LFP, or causal intervention.
```

## Highest-priority metadata requests

1. Experimental protocol or accessible export of the shared Google Doc.
2. Species, number of subjects, session-to-subject mapping, and recording site.
3. An authoritative lab-exported spatial-bin-to-mesh-centroid lookup, export
   environment manifest, and confirmation that bin `0` means invalid/filtered.
4. Confirmation that `f1526be5` means 20 ms, uncompressed trajectories and an
   explanation of every generation parameter.
5. Complete session populations, including non-place-selected units, with
   simultaneous-recording and shared-trial confirmation.
6. Spike-sorting/curation and unit-quality metadata.
7. Trial table with cue, goal, success/timeout, reward, and phase.
8. Position, heading, speed, gaze/view, fixation, and control/action aligned to
   the same retained trials.
9. RNN environment specification, rollout schema, checkpoints, and seeds.

## Provenance and caveats

Local sources:

- `context/previous-student-analysis.md`
- `notes/data_inspection/place_spatial_bins_f1526be5.md`
- `data/README.md`
- `data/manifests/latest.json`
- `context/code-map.md`
- `docs/analysis-contract.md`
- `Hippocampus.jl/src/unity.jl`
- `Hippocampus.jl/src/rawdata.jl`
- `Hippocampus.jl/src/eyelink.jl`
- `Hippocampus.jl/src/replay.jl`
- `Hippocampus.jl/src/spikedata.jl`

The supplied Google Doc URL could not be resolved, but its 20-page PDF export,
`/Users/hongyilin/Downloads/Analysis Write-up.pdf`, was reviewed and summarized
in `context/previous-student-analysis.md` (SHA-256
`b27a11d424e087ddc1674d399e18cb93b93f86654cc5a5895b054ca936e8c465`). The PDF
focuses on analysis rather than complete participant/acquisition metadata. Do
not identify this dataset with a published study solely from similarities in
task design.
