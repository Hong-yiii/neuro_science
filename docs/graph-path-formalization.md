# Graph Path Formalization For Fixed-195 Pseudopopulations

Date: 2026-09-01  
Status: **historical exploratory design spec**, not a current execution protocol.

The [September27 agreed direction](project-direction.md) and
[analysis contract](analysis-contract.md) supersede this file's active-looking
choices, full-195/imputation history and model queue. Component-level assay A
and ordered graph-path capability B remain in scope; B needs a defensible
route-level target for each evaluation object. Retain the design/provenance below
as background, not permission to reuse unsupported targets or launch old fits.

## Current decisions

- Use `docs/geometry/maze_mesh_centroids_1344.txt` as the authoritative centroid map.
- Treat line number `1..1344` as graph node/bin ID; `0` is invalid.
- Treat Unity `position_axis1, position_axis2` as aligned with the geometry axes.
- Use successful trials only for the experiment.
- For true `(start, goal)` labels, use the stricter `success_after_success` subset unless another start source is verified.
- Do the behavior-only graph/path audit before PCA, decoders, or CEBRA.

## Marker labels

Current exploratory interpretation:

```text
current marker minor digit = current cue/goal poster
previous successful trial's marker minor digit = current start poster
```

Evidence is in `notes/data_inspection/place195_marker_semantics_probe_20260901.md`.

Marker digit still matters because the baseline is `start + goal -> path`. If the
path task is "beyond start and goal," wrong endpoint labels make the baseline
wrong. The path graph itself can be built without marker labels, but any claim of
route information beyond endpoints needs them.

## Fine graph

Authoritative centroid map:

```text
node_id = line number in docs/geometry/maze_mesh_centroids_1344.txt
centroid(node_id) = (axis1, axis2)
```

Primary fine graph:

```text
V = 1344 centroid nodes
E = directed 4-neighbor edges between nodes exactly 0.625 units apart
```

Observed from the file:

| Quantity | Value |
| --- | ---: |
| nodes | 1,344 |
| undirected 4-neighbor edges | 2,544 |
| directed 4-neighbor edges | 5,088 |
| connected components | 1 |

Primary graph hash:

```text
1e7804c5d2167dcd8709a9760d8917034cb60e36e936229fad9056b1dae0f9ad
```

Receipt: `notes/data_inspection/maze_graph_hash_20260901.md`.

## Mapping Unity samples to graph nodes

For each native Unity path sample:

```text
sample coordinate -> nearest centroid node
```

Primary rule:

1. map to nearest centroid if it lies within one half-cell diagonal;
2. otherwise mark `unmapped`;
3. split paths at unmapped runs;
4. collapse consecutive repeated nodes for route-shape signatures;
5. keep dwell/repeat counts as side features;
6. split at nonadjacent transitions;
7. do not interpolate in the primary analysis.

Half-cell diagonal:

```text
sqrt(2) * 0.625 / 2 ≈ 0.442
```

## Cleaned trial path

A trial path is not one raw coordinate series anymore. It becomes:

```text
source_trial_id
  raw Unity samples
  -> mapped node sequence, including repeats and invalid gaps
  -> cleaned segment list
  -> directed edge sequence(s)
  -> route signature / path features
```

Example:

```text
raw mapped nodes:  A A B C 0 D E E
cleaned segments:  [A B C], [D E]
edges:             A->B, B->C, D->E
```

No edge is added from `C` to `D` because the invalid gap split the path.

## First path target

Primary target for fixed-195 pseudopopulation:

```text
route_family = exact ordered corridor/branch signature within verified (start, goal)
```

Do **not** start by clustering. Count exact signatures first. Cluster only if the
support audit shows exact route signatures are too sparse.

The fine 1344-node sequence is probably too detailed for final labels. Use it as
the measured path source, then collapse to interpretable corridor/branch
signatures after visual inspection and train/validation support counts.

## Pseudopopulation construction

Previous student matched trials by:

```text
(start, goal)
```

New design matches by:

```text
(start, goal, route_family)
```

One pseudotrial is synthetic:

```text
session/group 1 cue vector from a trial with route_family R
+ session/group 2 cue vector from a trial with route_family R
+ ...
= one pseudopopulation cue vector labelled R
```

The target attached to that pseudotrial is `route_family` or a frozen prototype,
not the exact path of any one component trial.

2026-09-01 support probe: under the current split, full 195 is not supported in
validation even for old-style `(start, goal)` labels; therefore full 195 cannot
support `(start, goal, route_family)` without imputation. Receipt:
`notes/data_inspection/fixed195_pseudopop_support_probe_20260901.md`.

Primary analyses should use support-declared variants instead of silently imputing missing cells:

1. subset pseudopopulations for evaluable route families/conditions;
2. old-style `(start, goal)` pseudopopulation as a historical baseline;
3. a new stratified exploratory split if full-195 validation is required;
4. cross-condition shared-edge/segment contrasts if route-family labels are too sparse.

2026-09-01 user decision: imputation is allowed for exploratory training runs
only. The first implemented policy was train-fit marginal mean imputation per
cell, represented as zero after train-set z-scoring, with the imputation burden
reported. Receipt: `notes/data_inspection/place195_graph_path_baseline_20260901.md`.

2026-09-01 V5 pivot: the current baseline replaces the crude
`source_trial × 195 cells` matrix with condition-matched pseudopopulation rows.
Rows are matched on `(split, start, goal, route_family)`; each contributing
session supplies one same-condition source trial, and that session's cells take
cue counts from that trial. Missing cells stay masked; no V5 neural score uses
cell-value imputation. Receipt:
`notes/data_inspection/place195_graph_path_baseline_v5_20260901.md`.

## Cue feature approaches

### 1. 100 ms cue-time bins — chosen primary neural feature

Shape:

```text
pseudotrial x cue_time_bin x cell
```

Use this because cue-period activity can be dynamic: the question is not only
"does the cue period contain route-family information?" but also "when does it
appear after cue onset?" The previous-student summary also reported goal-related
cue effects around `0.3–0.7 s`, so a time-resolved representation is worth
preserving.

Primary binning:

```text
1 s cue window -> 10 bins of 100 ms
```

Rules:

- all bins from one source trial stay in the same split;
- adjacent bins are dependent, not extra independent trials;
- PCA/decoders must treat the unit of evaluation as pseudotrial/source trial;
- record cue exposure per bin and mask short/missing bins.

CEBRA analogy: this keeps the same sample structure CEBRA-like temporal methods
need later, without running CEBRA yet. A later CEBRA-Time or behavior-conditioned
CEBRA pass can use `(pseudotrial, cue_bin)` samples only with explicit trial
boundary masks so temporal positives never cross source-trial boundaries.

### 2. Total cue spike count per cell — collapse/sanity baseline

Shape:

```text
pseudotrial x cell
```

Compute this by summing the 100 ms bins. It is useful as a simple sanity check:
if time-binned models work but total counts fail, the signal is temporally
structured; if both work similarly, route-family information is mostly in overall
cue firing rate.

### 3. Exposure-normalized rates — sensitivity

Shape:

```text
pseudotrial x cue_time_bin x cell
```

Use if cue-bin exposure differs materially. If cue windows are near 1 s and bins
are complete, rates mostly rescale counts and add little. Counts remain the
primary observation scale; rates/exposure offsets are sensitivity checks.

Recommended order:

```text
100 ms cue bins -> total-count collapse baseline -> rate/exposure sensitivity -> CEBRA later
```

## Success-only versus success-after-success

`success_only` means the current trial ended with marker `3x`.

`success_after_success` means:

```text
previous trial ended with 3x
current trial ended with 3x
```

Why this matters: the current start poster is inferred from the previous goal.
That inference is clean only when the previous trial was completed. In the
current all-session output:

| Split | current success | success-after-success |
| --- | ---: | ---: |
| train | 16,395 | 16,075 |
| validation | 3,309 | 3,243 |
| locked test | 3,496 | 3,422 |

Primary route-family work should use `success_after_success` when endpoint labels
are needed. Pure path visualization may show all current-success trials, clearly
labelled.

## Audit before PCA

Before fitting PCA, produce a train/validation-only support report:

```text
start, goal, route_family, split, session/group, cell_count, trial_count
```

Stop or simplify if route families are too sparse. Do not use locked-test path
support to revise the graph, route signatures, filters, or labels.

## Why this cannot prove intention

The measured target is the path Picasso actually took. Intention is a hidden
state. Even if cue activity predicts a future route family, the data only show
association with the later observed path. The monkey could change plan, hesitate,
follow habit, or react to view/action variables we did not record here. So the
safe claim is prospective path information, not decoded intention.
