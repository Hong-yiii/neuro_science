# API And Math Notes

Terms: a **source trial** is one real behavioral trial; a **derivative** is any
window, bin, bootstrap, or feature row made from that same source trial; a
**valid cue bin** is a cue-period time bin kept by the mask; **exposure** is that
bin's observed duration in seconds.

## `CueNavigationTrial` (`contracts.py`)

Math object: `N_i in N0^(B_i x U_g)`.

Required linkage metadata includes source trial, session, simultaneous recording
group, cue/start/goal identities, cue and navigation timing, trial index,
previous-trial/goal/success fields, current success versus timeout, and the
inclusion reason. Previous-trial fields are either all present or all absent;
absence requires an explicit audited reason rather than an assumption about
zero- versus one-based trial numbering. Exactly one of `current_success` and
`timeout` is true. These
fields make sequential dependence and successful-after-successful selection
visible before an object can pass the scientific contract.

Code mapping:

- `cue_counts_by_bin_unit[b, u]` is `N_ibu`.
- `cue_valid_mask[b]` is `M_ib`.
- `cue_exposure_seconds[b]` is `Delta t_ib`.
- `unit_ids[u]` fixes the unit column order.

Edge cases in code: counts must be integer and nonnegative; valid exposure must
be positive and finite; the unit axis must match `unit_ids`; one unit is rejected
because the current one-cell export is not a simultaneous population.

## `summarize_cue_activity` (`neural.py`)

Count equation:

```text
X_count[u] = sum_b M[b] * N[b, u]
```

Rate equation:

```text
X_rate[u] = sum_b M[b] * N[b, u] / sum_b M[b] * exposure[b]
```

Code mapping: `counts[mask, :]` selects valid bins, sums over axis `0`, and
uses the same denominator for every unit. The public shape is only
`(cue_bin, unit)`. A transposed array fails by alignment checks; it is not fixed
silently.

## `MazeGraph` And `clean_path` (`contracts.py`, `paths.py`)

A graph is `G=(V,E)` from explicit directed edges. The code hashes sorted
canonical JSON of those edges. There is no factory that infers maze geometry.

Cleaning rule:

1. `0` and `None` are invalid and split segments.
2. Consecutive repeats stay in `raw_valid_segments`.
3. `route_shape_segments` collapses only consecutive repeats.
4. If `(previous, current)` is not an explicit directed edge, the path splits.
5. No interpolation and no bridge edges are added.

A one-node segment is kept for occupancy accounting, but it has no directed edge.

## Directed-Edge Jaccard (`paths.py`)

For a cleaned path, `directed_edge_set` is the union of edges from each segment.
It never adds an edge across a split. Distance is:

```text
D_edge = 1 - |E_left intersect E_right| / |E_left union E_right|
```

If both edge sets are empty, `edge_jaccard` returns `None` instead of inventing a
zero or one distance.

## Longest Shared Contiguous Segment (`paths.py`)

The code compares directed-edge sequences only within pairs of cleaned segments.
It searches the longest equal contiguous run. Ties are deterministic: canonical
edge content, then segment/start indices.

Endpoint labels:

- `initial`: the run starts at the first available edge in both trials.
- `terminal`: the run ends at the last available edge in both trials.
- `middle`: it touches neither trial endpoint.
- `complete`: the run starts and ends at both trial endpoints.
- `mixed`: any other known endpoint combination.
- `unavailable`: a leading/trailing invalid gap or earlier/later split obscures
  the relevant endpoint, so the code refuses to infer the label.

## Frozen Splits (`splits.py`)

No split equation is implemented. The caller supplies rows:

```text
sample_id, source_trial_id, session_id,
simultaneous_recording_group, split
```

Validation enforces allowed labels, exact expected source-trial coverage, unique
sample IDs, and one session/group/split tuple per source trial. Canonical sorted
JSON is SHA-256 hashed. The report counts independent source trials by recording
group and split so a reviewer can inspect the data-dependent holdout policy.
Freeze this hash before adaptive behavior work so derivatives cannot leak across
train/validation/test. The code records a supplied policy; it does not choose
whether trials, blocks, sessions, or groups should be held out.

## Run Manifest (`manifest.py`)

A manifest records creation time, stage/status/scientific status, input and
artifact hashes, config, shapes, exclusions, stop conditions, Git revision/dirty
state, Python/package versions, and graph/split hashes. CEBRA runs record NumPy,
CEBRA, Torch, scikit-learn, SciPy, and HDF5 package versions. Path confinement
lives in `manifest.py`, so both the CLI and imported writer interfaces accept
only a new directory below `outputs/cebra_pilot/` and never overwrite a
manifest.

## Preflights (`preflight.py`)

- Synthetic preprocessing writes shape/path/split summaries only.
- Current JLD2 smoke imports the existing loader and always records the H1 stop
  reason.
- Synthetic CEBRA preflight pins `cebra==0.6.1`, CPU, `offset1-model`,
  `conditional='time'`, `output_dimension=3`, ten iterations, and contiguous
  synthetic input with shape `256 x 12`. It checks that the saved and reloaded
  model produce numerically matching transforms. NumPy and Torch seeds are
  recorded, but the public sklearn API does not guarantee full training
  determinism. The smoke makes no ragged-trial boundary claim.
