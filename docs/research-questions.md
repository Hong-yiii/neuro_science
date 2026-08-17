# Research Questions

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

## H2 — Artificial-Agent Comparison (Stretch Aim)

If H1 is supported, test whether an artificial navigation agent trained on an
analogous task independently develops hidden representations with similar
information content, geometry, or temporal dynamics.

This supports a claim of representational convergence only after the comparison
metric is specified. Similar decodability or geometry does not establish the
same biological mechanism, and RNN hidden units are not treated as neurons.

## Supporting Analyses

Place, view/visual, heading, action, goal, and conjunctive coding are no longer
the thesis-level primary question. They remain useful for:

- validating the biological and model data pipelines;
- characterizing what the cue representation contains;
- testing sensory, spatial, and motor confounds;
- explaining apparent path information through correlated variables.

## CEBRA's Role

CEBRA is a candidate measurement instrument, not the hypothesis and not, by
itself, a path decoder.

For a behavior-conditioned analysis:

```text
cue neural activity --CEBRA encoder--> latent representation --simple decoder--> path representation
                              ^
                    path-derived training context
```

Path representations or clusters must be constructed from behavior only, never
jointly from cue neural activity. CEBRA uses the path-derived context to learn a
neural embedding; a separate held-out decoder such as k-nearest neighbors or
ridge regression/classification tests whether the embedding predicts path.

Clustering is optional. A continuous path representation or path-distance-based
sampler may preserve graded similarity better than premature discrete clusters.
Any path preprocessing or clustering must be fitted within training folds.

A trial-aware CEBRA-Time model, which receives no path labels during
representation learning, is an important companion analysis because supervised
CEBRA intentionally shapes its embedding with the supplied context.

## Core Nulls And Controls

- keep every sample from a source trial in one validation split;
- compare against start-and-goal-only prediction;
- shuffle path labels or neural features within start-goal condition;
- fit path processing, clustering, dimensionality reduction, and decoders using
  training data only;
- compare raw population and PCA baselines with CEBRA representations;
- use simple downstream decoders before expressive sequence models;
- control available gaze, heading, cue identity, action, speed, trial time, and
  session variables;
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

The current local place-bin export begins at cue offset and lacks the cue window,
start/goal labels, and a verified synchronized population matrix. It cannot yet
test H1.

## First Milestone

Before fitting CEBRA:

1. obtain or verify cue-aligned, trial-linked simultaneous population data;
2. reconstruct observed paths and audit variation within each start-goal pair;
3. define one leakage-safe path representation and start-goal baseline;
4. test raw-neural and PCA incremental prediction;
5. run a trial-aware CEBRA-Time pilot with the same held-out decoder;
6. add behavior-conditioned CEBRA only after those checks establish feasibility.
