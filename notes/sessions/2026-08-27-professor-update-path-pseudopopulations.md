# Session: Professor Update And Path-Matched Pseudopopulations

Date: 2026-08-27

## Lab clarification

The 195 supplied cells were selected for spatial tuning. Individual cells could
also show view tuning or place-view conjunctions, but the overlap was not
quantified. The list should therefore be treated as the spatially selected set,
not as a broadly view- or conjunction-selected population.

The professor recommended using these 195 cells for the best initial chance of
decoding space. A broader list of all recorded cells exists upstream at:

```text
/Volumes/Hippocampus/Data/picasso-misc/AnalysisHM/Current Analysis/cell_list.txt
```

The first pseudopopulation will use the fixed 195 spatial cells. An all-cell
pseudopopulation is future work.

## Revised exploratory question

Within a fixed `(start, goal)` condition, do cue-period response distributions
distinguish graph-defined route families?

This is a condition-level pseudopopulation question. It complements but does not
instantiate exact same-trial H1a, because cells combined across sessions do not
share one real trial or one exact subsequently observed path.

## Proposed behavioral ruler

Start with the simplest topology-aware representation:

1. map paths through verified mesh centroids and adjacency;
2. collapse the fine mesh to an interpretable corridor/decision graph;
3. remove invalid samples and split at invalid gaps;
4. collapse consecutive repeated nodes for route shape;
5. represent each trial by its ordered directed corridor/branch signature; and
6. define route families within each fixed `(start, goal)` condition.

Count exact signature repetitions before clustering. If exact signatures are too
sparse, evaluate a small k-medoids or hierarchical sensitivity analysis using a
frozen precomputed path distance. Candidate comparators are directed-edge
Jaccard, ordered sequence edit/shared-subpath distance, and graph-aware DTW as a
sensitivity analysis.

## Pseudopopulation construction boundary

- Split real source trials before route-family fitting.
- Build pseudotrials separately inside training, validation, and test splits.
- Preserve real recording groups: cells recorded together use the same source
  trial rather than being sampled independently.
- For one route family, select one eligible source trial from each recording
  group and concatenate the group-level cue vectors across the fixed 195 cells.
- Never impute a missing recording-group block.
- Keep every bootstrap copy and derivative of one source trial in one split.
- Attach only the shared route-family label or frozen family prototype to a
  pseudotrial, not one component trial's exact path.

Design eligibility uses training/validation behavior only. Every contributing
recording group must have enough independent source trials for those assignments.
If support is inadequate, merge overly specific route families or restrict
eligible start-goal conditions rather than silently changing channels. Apply the
frozen mapping to test once; insufficient test support makes the affected
contrast non-evaluable and must not trigger redesign.

## Evaluation

Compare:

```text
baseline: start + goal -> route family
neural:   start + goal + cue pseudopopulation -> route family
```

Use raw and train-fitted PCA features before path-conditioned CEBRA. The primary
null shuffles route-family labels within recording group, start, and goal before
rebuilding pseudotrials.

The strongest allowed result wording is that cue-period responses distinguish
behaviorally defined route families beyond start and goal at the
pseudopopulation condition level. It does not imply exact trial-specific path
prediction, simultaneous population geometry, intention, or mechanism.
