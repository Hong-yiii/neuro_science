# Lab-server session feasibility audit: 20181105/session01

Date: 2026-08-30
Status: **software smoke test and data-feasibility audit; not scientific evidence**

## Operational question

Can one bounded lab-server session supply the native data needed to build the
two H1 inputs without copying the full raw recording?

```text
CuePopulation[trial, cue_time_bin, simultaneously_recorded_unit]
ObservedPath[trial, navigation_sample]
```

This audit does not fit a model or test H1. The independent unit for later
evaluation remains a complete source trial.

## Transfer receipt

The files were read over the configured `cortex` SSH account directly from:

```text
/volume1/Hippocampus/Data/picasso-misc
```

They were copied, with source-relative paths preserved, to the ignored local
directory:

```text
data/raw/lab_server/cortex_picasso_misc_20260830/
```

Transfer scope:

- 22 files;
- 675,994,365 bytes (about 645 MiB);
- the exact source-relative file list is in the ignored local file
  `data/manifests/20181105_session01_candidate_source_files.txt`;
- local byte counts and SHA-256 hashes are in ignored
  `data/manifests/latest.json`;
- a checksum-mode `rsync` dry run after transfer reported no changed files.

The local copies are immutable inputs. The transfer intentionally excludes the
roughly 157 GiB complete `session01` tree, broadband neural data, redundant
sorting workspaces, GLM/map outputs, and the large source raytrace CSV because
those files are not needed for the first cue-to-path feasibility import.

## Copied dependency bundle

### Trial timing and task events

- `20181105/session01/rplparallel.mat`
  - legacy MATLAB 7.3/HDF5 object used by `RippleData`;
  - neural-clock marker codes and timestamps for 404 trials x 3 events.
- `20181105/session01/RawData_T1-400/session_1_5112018105323.txt`
  - native Unity session log;
  - header plus rows of `marker, delta_time, position_axis_1,
    position_axis_2, heading`.
- `20181105/session01/eyelink.mat`
  - legacy MATLAB 7.3/HDF5 object;
  - 404 trial-code rows, 5,546,618 gaze samples, and fixation/saccade events.
- `20181105/session01/unity_raytrace.jld2`
  - trial-ragged position, heading, gaze/raycast point, viewed object, fixation
    mask, and timestamps;
  - useful for view/gaze controls, but not required to define the primary path.

### Candidate session population

The session contains exactly six cell-level `spiketrain.mat` files under its
array/channel/cell tree, and all six occur in the copied 364-line
`AnalysisHM/Current Analysis/cell_list.txt`:

```text
array01/channel029/cell01
array01/channel030/cell01
array02/channel043/cell01
array02/channel043/cell02
array02/channel043/cell03
array02/channel045/cell01
```

Each MATLAB v5 file contains sorted timestamps in milliseconds plus a
`reference` to `firings.curated2.mda` and a component label. Spike counts in the
cue must be reconstructed from the timestamps; they are not stored directly.

Only `array02/channel045/cell01` appears in the separate 195-cell
place-selective list. The six-cell session list is therefore a different and
broader object than the fixed 195-cell cross-session selection.

Six matching `view_and_place_representation.jld2` files were retained only as
navigation-alignment reference artifacts. Their default event-2-to-event-3
window excludes the cue and cannot supply H1 cue activity.

### Provenance metadata

The snapshot also includes session notes, `sessionInfo.mat`,
`CellActivityLog.new.xlsx`, `Electrode movement notes.xlsx`, and the Unity batch
log. These were retained for later curation and acquisition review; their
presence does not itself prove simultaneity or unit quality.

## Verified trial linkage

The native Unity, Ripple, and Eyelink files each expose 404 ordered three-event
trial rows. All 404 marker-code triplets match exactly across those three
streams.

Observed event-code pattern:

```text
1x -> trial/cue onset
2x -> cue offset and navigation onset
3x -> successful end
4x -> timeout end
```

Within every row, the minor digit `x` matches across all three events. There
are 400 successful rows and 4 timeout rows. The first-to-second interval is
approximately one second in all clocks (Ripple median 1.021 s).

This establishes a strong row-level crosswalk for a loader. The exact semantic
mapping from `x` to `cue_id` and `goal_id`, and the rule used to derive
`start_id`, still require protocol/lab confirmation. Code comments and the
behavioral sequence support those interpretations, but the importer must retain
the raw codes and label any decoded task fields as inferred until verified.

## Cue-population smoke extraction

Using half-open Ripple-clock windows `[event_1, event_2)` and all six spike
trains produced an event-count matrix with shape:

```text
404 trials x 6 units
```

There were 4,902 cue-period spikes in total; 403 of 404 trials contained at
least one spike across the six units. Median total activity was 12 spikes per
trial, with a median of 3 active units per trial.

These counts only demonstrate that cue events are accessible and linked. The
primary importer should preserve individual cue-relative spike events first.
Cue bin size, exposure handling, and any time-collapsed summary remain deferred
analysis decisions.

## QC anomaly: source trial 178

Trial row 178 has codes `[16, 26, 36]`. Unity records a 7.660 s navigation
interval, while Ripple and Eyelink contain an approximately 305.269 s
event-2-to-event-3 interval. From the next row onward, the Ripple-versus-Unity
clock offset is about 297.61 s larger, consistent with an unrepresented pause
or clock discontinuity.

The raytrace object's third trigger for this row is missing and every
trial-ragged raytrace field is empty. The raw Unity path is present.

The loader must retain this row and record separate QC flags rather than silently
repairing or dropping it. It is not eligible for a fully multimodal trial until
the discontinuity is explained. An analysis inclusion decision must be frozen
later and applied without deleting the raw record.

## Normalized import design

The reusable Python import should decode the immutable files into normalized
interim tables before constructing any model tensor:

1. `source_files`
   - local/source path, byte count, SHA-256, source mtime, format, and role.
2. `units`
   - `session_id`, provisional recording-group ID, stable `cell_id`, array,
     channel, sorted-unit label, curation reference, selection provenance, and
     simultaneity status/evidence.
3. `trials`
   - stable `source_trial_id`, row IDs for Ripple/Unity/Eyelink/raytrace, raw
     three-event codes/times, cue/navigation boundaries, outcome, previous-trial
     link, inferred-versus-verified task labels, and per-stream QC flags.
4. `cue_spike_events`
   - `source_trial_id`, `cell_id`, and spike time relative to cue onset.
5. `path_samples`
   - `source_trial_id`, native Unity sample index/time, two continuous position
     axes, heading, and validity; optional gaze/view/fixation fields joined only
     after their timestamps and trial availability pass QC.

The analysis object is derived only after these checks:

```text
trial record
├── cue counts: cue_bin x unit, with exposure and validity masks
└── subsequent path: navigation_sample x behavioral fields
```

Graph nodes, spatial bins, cleaned edge sequences, route families, PCA, and
other learned transformations are downstream derivatives and must not be
embedded into the raw importer.

## Current project state after this audit

The previous local single-cell place export remains navigation-only and cannot
test H1. This new session snapshot removes the basic *file access* blocker and
supports development of a real cue-to-path importer and behavioral feasibility
audit.

Scientific H1 remains blocked pending at least:

- explicit confirmation that the six units form one genuine simultaneous
  recording group on the shared Ripple clock;
- authoritative cue/goal/start marker semantics and subject/session metadata;
- a documented decision for trial 178 and other loader QC results;
- an independently reviewed reusable loader and leakage-safe trial split;
- sufficient within-start-goal path variation and a frozen path target/baseline.

The checked-out Julia `ViewAndPlaceRepresentationNew` path should not be rerun
unchanged: it currently destructures five values from a six-value
`UnityRaytraceData.get_trial` return. Python remains the chosen first language
for import, validation, and visualization; Julia is the upstream semantic
reference.
