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

### Shared Path Components Across Conditions

Limited path variation within one `(start, goal)` condition weakens the exact
trial-specific H1a comparison, but it creates a complementary question: do cue
states reflect reusable components shared by paths from different task
conditions? For example, paths from `A` to `B` and from `A` to `C` may share a
directed corridor segment before diverging.

This is a candidate structural analysis within H1b and a bridge to H2, not a
replacement for H1a. Its behavioral object is a shared future path component,
such as a directed edge, ordered segment, or branch decision. Initial, middle,
and terminal overlap should be distinguished because an obligatory initial
segment can be confounded with start location and an obligatory terminal segment
with goal.

The key comparison is not merely “high-overlap trials have similar cue states.”
It is whether path overlap explains held-out cue-state similarity after matching
or controlling same start, same goal, cue identity, session, and other available
confounds. Stronger contrasts include:

- same start and different goals: high versus low future-path overlap;
- same goal and different starts: high versus low overlap;
- different starts and goals that nevertheless share a middle route segment;
- the limited within-start-goal route variants, where available.

If path overlap is almost completely determined by start and goal, the dataset
cannot distinguish compositional path structure from task-condition coding.
The strongest allowed claim is that cue-period population geometry covaries with
shared components of subsequently observed paths; it does not establish an
internal graph, intention, or a planning mechanism.

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
information content, geometry, or temporal dynamics. Shared directed path
components provide one common behavioral ruler even when biological units and
artificial hidden dimensions do not correspond.

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

- create and hash source-trial train/validation/test assignments before adaptive
  graph, path-metric, exclusion, or contrast selection;
- keep every sample and derivative from a source trial in one validation split;
- compare against start-and-goal-only prediction;
- shuffle path labels or neural features within start-goal condition;
- fit path processing, clustering, dimensionality reduction, and decoders using
  training data only;
- compare raw population and PCA baselines with CEBRA representations;
- test shared path-component geometry first in raw, PCA, or other representations
  not trained with future-path labels;
- use simple downstream decoders before expressive sequence models;
- control available gaze, heading, cue identity, action, speed, trial time,
  session, previous goal/trial, and success-selection variables;
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

### Current condition-level pseudopopulation lane (2026-09-08)

Given the operational difficulty of large simultaneous monkey recordings,
pseudopopulations remain central to a complementary question: do independent
source-trial sets reproduce population response differences associated with
future path components after endpoint/nuisance control? This is related evidence
for prospective coding, not fulfillment of the exact same-trial population-state
contract above. It does not redefine H1 or prove H1b from a supervised embedding.

Use behavior-only targets with explicit interior/anywhere semantics, source
splits before assembly, session-block/cue-bin preservation, training-only
preprocessing, and coherent source/session/temporal nulls. Do not fill missing
recordings with zero or count synthetic rows as independent trials. Per-unit
checks complement population analyses; no individually significant-neuron gate
is required. More data or another CEBRA formulation may help, but neither is a
proven remedy for the observed source-pool gap.

The [completed study and status index](professor_updates/path_generalization_20260907/README.md)
separates accepted results, corrected inference, failed attempts, and proposals.
The [current next-study plan](reports/path-generalization-next-steps-20260908.md)
replaces the earlier simultaneous-data-first milestone for this condition-level
lane. Original test exposure remains permanent; development resplits do not
restore confirmation.

The legacy local place-bin export begins at cue offset and lacks the cue window,
start/goal labels, and a verified synchronized population matrix. It cannot yet
test H1.

The current all-session `place195` native snapshot contains 58 sessions, 195
place-selected cue-accessible spike trains, and same-session Ripple/Eyelink/Unity
trial logs, so a real importer/QC audit can now be run across the selected-cell
set. It remains below the scientific gate: cells are selected rather than an
unbiased complete population, simultaneous recording groups are not confirmed,
marker-label semantics remain unverified, raytrace/gaze controls are absent from
this snapshot, and clock-discrepant trials such as 20181105 trial 178 require
explicit QC flags.

An earlier bounded `20181105/session01` six-unit transfer is documented in
`notes/data_inspection/lab_server_20181105_session01.md`, but that exact data
root is not present in the current checkout.

## Next Milestone — Proposed, Not Yet Executed

V6–V9 and the path-generalization follow-up have already completed bounded
exploratory raw/PCA/CEBRA experiments. Their nonpositive/unstable results do not
confirm H1 or verify missing laboratory metadata. The next condition-level study
should:

1. freeze a meaningful route contrast, cue window, cohort and endpoint controls
   using task meaning and training support rather than neural outcomes;
2. audit source-trial support and recording provenance without requiring every
   selected cell in a common195-column panel;
3. measure independent-source population-pattern reproducibility and neural-only
   positive controls, with simple regularized baselines;
4. separate pseudorow sampling from source/session uncertainty and preserve
   within-session cells/bins through construction and splits;
5. compare CEBRA only in a bounded, matched evaluation family, and use reliability
   or injected-signal checks to inform any additional trial collection;
6. reserve genuinely unexposed observations before adapting to them if a new
   confirmatory evaluation is intended.

Exact trial-specific population/dynamics claims still require the verified
simultaneous-trial contract; condition-level progress need not wait for that.
