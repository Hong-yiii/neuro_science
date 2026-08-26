# Prospective Path Representation Project

Updated: 2026-08-25

The 2026-08-25 revision adds the shared-path-component feasibility screen and
keeps it subordinate to canonical H1a/H1b. Pilot-specific formalization lives in
[`docs/cebra_pilot/`](../docs/cebra_pilot/README.md).

## One-Sentence Aim

Test whether hippocampal cue-period population activity contains information
about the subsequently observed navigation path beyond start and goal, then—if
supported—compare that representation with one learned independently by an
artificial navigation agent.

## Current Framing

H1 is the thesis core. The artificial-agent comparison is H2, a stretch aim,
not a requirement for H1 to succeed.

```text
cue-period hippocampal activity
        -> prospective path information beyond start + goal
        -> possible low-dimensional organization
        -> optional comparison with agent hidden states
```

This is a representational and predictive study. Decoding an observed future
path does not establish causal planning or directly measure intention. An
intended-path interpretation assumes that the maze-familiar animal generally
executes its intention.

The canonical hypothesis and controls are maintained in
[`docs/research-questions.md`](../docs/research-questions.md).

## H1 Components

H1 remains one hypothesis with two components:

- **H1a:** cue activity adds held-out information about the subsequent path
  beyond start and goal.
- **H1b:** that information has reproducible low-dimensional organization.

This distinction protects the biological information claim from depending on
one representation-learning method.

## Path Language

Use **path** for an observed ordered movement through the maze. Reserve
**trajectory class** for the previous student's `(start, goal)` category.

The current proposed operationalization treats the maze as one graph and each
trial path as a walk over it. Graph resolution, path clustering, distinct-route
criteria, and path distance remain deferred design decisions.

## Shared Path Components

When trials with one start and goal show little route variation, paths from
different conditions may still share reusable directed edges or ordered
segments. For example, `A -> B` and `A -> C` may share an initial corridor before
diverging. This motivates a complementary compositional analysis: ask whether
cue-state similarity tracks shared future path components after controlling
start, goal, cue identity, session, and available sensory or motor confounds.

An obligatory segment from start `A` is confounded with start coding. Stronger
evidence comes from matched high/low-overlap paths with the same start or goal,
or from different-endpoint paths that share a middle segment. If path overlap is
nearly determined by start and goal, the data cannot identify a distinct
compositional representation.

This analysis is a candidate test of H1b and a common behavioral ruler for H2.
It does not replace H1a's incremental held-out prediction and does not imply that
the hippocampus literally represents a graph.

## CEBRA And Decoding

CEBRA learns an encoder from neural activity to a latent representation. In
CEBRA-Behaviour, a path-derived context shapes that representation during
training; CEBRA does not by itself demonstrate held-out path prediction.

The intended evaluation is:

```text
cue activity -> CEBRA latent -> simple held-out path decoder
```

Path representations or clusters are constructed from behavioral paths only.
They must never be constructed jointly from neural activity. Clustering is
optional; graded graph-path distances may be preferable if behavior does not
show stable route families.

Use CEBRA-Time as a companion analysis without path supervision, and compare all
representations using the same simple decoder and trial-level splits. Test
shared path-component geometry in raw or PCA cue activity before using graph- or
path-conditioned CEBRA, which remains a secondary supervised probe.

## Role Of Earlier Place/View Work

Place-like, view/visual-like, and conjunctive coding no longer define the primary
research question. They remain supporting analyses for pipeline validation,
representation characterization, and control of spatial, sensory, and motor
confounds.

## Feasibility Gate

Trial-specific H1 requires cue-period activity from a genuinely simultaneous
population linked to that same trial's start, goal, and subsequent path.
Cross-session pseudopopulations can support condition-level summaries, not exact
trial-specific future-path claims.

The current local export is navigation-period, selected single-cell place data.
A new cue-aligned population export is required before H1 can be tested.

## Deferred Decisions

- maze-graph granularity;
- what constitutes a meaningfully different path;
- path representation and distance;
- treatment of unsuccessful and timeout trials;
- cue-window and spike-bin resolution;
- success metrics and required effect size;
- exact CEBRA configuration and sampler;
- artificial-agent architecture and comparison metric.
