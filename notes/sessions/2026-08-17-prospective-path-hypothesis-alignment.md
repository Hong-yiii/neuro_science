# Prospective Path Hypothesis Alignment

Date: 2026-08-17

Source discussion: `/Users/hongyilin/Downloads/neuroscience_research_handoff.md`

Canonical outcomes are maintained in:

- [`docs/research-questions.md`](../../docs/research-questions.md)
- [`docs/analysis-contract.md`](../../docs/analysis-contract.md)
- [`context/rnn-unity-neural-coding-project.md`](../../context/rnn-unity-neural-coding-project.md)

## Scope Decision

The prospective-path question replaces matched place/view/conjunctive coding as
the thesis-level primary direction. Those coding analyses remain useful as
pipeline checks, representation characterization, and confound controls.

The artificial-agent comparison remains H2 and a stretch aim. H1 can succeed
without training or comparing an artificial agent.

## H1 Decision

H1 remains one hypothesis with two components:

- **H1a — information:** cue-period hippocampal population activity improves
  held-out prediction of the subsequently observed path beyond start and goal.
- **H1b — structure:** that prospective path information has reproducible
  low-dimensional organization.

The components are distinguished so that failure of CEBRA, a chosen latent
dimension, or another geometry assumption does not imply absence of path
information.

The practical H1a comparison is:

```text
path ~ start + goal
versus
path ~ start + goal + cue activity
```

The conditional mutual-information expression is conceptual; incremental
held-out prediction and within-condition nulls are the operational test.

## Observation And Interpretation

The directly measured target is the subsequently observed path. Intended path
is latent. An intention-oriented interpretation assumes that a monkey familiar
with the maze generally executes its intention; familiarity does not make
observed and intended paths identical in every trial.

No claim of causal planning follows from decoding alone.

## Terminology

**Path** is the canonical term for the animal's ordered movement through the
maze. **Trajectory class** is reserved only for the prior analysis's overloaded
`(start, goal)` category.

Avoid using “trajectory” as a synonym for physical path in new project docs.

## Maze Graph Proposal

The maze graph is a proposed path measurement method, not part of H1:

```text
one maze graph
  nodes: spatial regions
  edges: valid transitions
  trial path: ordered walk through the graph
```

This representation respects obstacles and adjacency without treating spatial
bin IDs as ordinal values. Existing refined-mesh IDs are not row-major 40 x 40
coordinates.

The following remain deliberately unresolved until real paths are audited:

- graph granularity;
- whether corridor sections, junctions, landmarks, or mesh regions become nodes;
- what counts as a meaningfully different path;
- whether stable discrete path clusters exist;
- path distance and primary evaluation metric.

## CEBRA Clarification

CEBRA learns a neural encoder and latent representation. It is not, by itself,
the final path predictor.

For behavior-conditioned CEBRA:

```text
path behavior only -> path representation or cluster -> training context
                                                    |
cue neural activity -> CEBRA encoder -> latent Z ---+-> simple held-out decoder -> predicted path
```

The path-derived context shapes the CEBRA embedding. A separate decoder such as
k-nearest neighbors or ridge regression/classification evaluates whether held-
out cue activity predicts path. The CEBRA software provides compatible decoder
utilities, but decoding is a separate evaluation stage conceptually.

Path labels, clusters, or features must be created from behavior only. Jointly
clustering cue activity and paths would make the target circular. Any path
clustering or learned preprocessing must be fitted within training folds.

Clustering is not required. If path similarity is graded, a continuous path
representation or custom path-distance sampling may retain more information
than discrete route clusters. Clustering should be used only if behavioral audit
shows stable path families.

CEBRA-Time is an important companion because it learns without path labels.
Temporal pairings must respect trial boundaries. A supervised path-organized
embedding alone is not independent evidence that the unconstrained neural
manifold naturally has that organization.

## Data Feasibility Boundary

The historical 233-cell pseudopopulation was assembled from different sessions
by start-goal condition. It cannot link one real cue-period population state to
one exact subsequent path. It can support condition-level or average-path
questions only.

Trial-specific H1 requires:

```text
same source trial
├── cue-period activity from verified simultaneous cells
├── start and goal
└── observed subsequent path
```

Multi-session representation learning can accommodate different neural
feature dimensions across sessions, but cannot restore simultaneity absent from
the source recordings.

The current local selected-cell export starts at cue offset and contains
navigation-period spike counts plus spatial-bin IDs. It lacks the cue period,
start/goal labels, and a verified synchronized population matrix. The next step
is therefore data acquisition and behavioral audit, not CEBRA training.

## Initial Analysis Order

1. Obtain cue-aligned simultaneous population data linked to observed paths.
2. Audit repetitions and within-start-goal path variation.
3. Verify maze geometry and construct a provisional graph.
4. Fit the start-goal-only path baseline.
5. Test raw-neural and PCA incremental prediction with complete trials held out.
6. Run trial-aware CEBRA-Time with the same simple decoder.
7. Add path-conditioned CEBRA only after feasibility is established.
8. Characterize low-dimensional organization if H1a has support.
9. Proceed to the artificial-agent H2 only after the biological result is
   sufficiently stable.

## Deferred Edge Cases And Design Decisions

- unsuccessful and timeout trial handling (reported as approximately 10% of
  trials, not yet verified from local data);
- observed-path versus intended-path divergence on individual trials;
- cue window and spike bin size;
- success threshold and statistical power;
- held-out session or start-goal generalization;
- exact conditional CEBRA sampler/API;
- artificial-agent architecture and representation-comparison metric.

These were intentionally deferred during alignment rather than silently fixed.

## Documentation Pivot Markers

The following pre-pivot documents are preserved but now carry prominent status
notices and links to the canonical H1/H2 documents:

- `docs/supervisor-meeting-prep.md`: archived RNN/place-first scratchpad;
- `context/analysis-entry-points.md`: supporting place/view/conjunctive code map;
- `context/previous-student-analysis.md`: historical source summary;
- `notes/sessions/2026-08-10-spatial-mesh-replay-and-pseudopopulations.md`:
  historical session and terminology;
- `papers/reading-roadmap.md`: supporting roadmap with RNN comparison deferred to
  H2;
- `learning/neural-agent-action-plan.md`: deprecated staged RNN-comparison plan,
  retained for measurement and validation lessons.

`docs/dataset-card.md` is canonical for dataset facts only. Current scientific
framing lives in `docs/research-questions.md`, required data in
`docs/analysis-contract.md`, and execution order in
`docs/getting-started-tasks.md`.
