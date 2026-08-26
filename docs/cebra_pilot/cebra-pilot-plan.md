# CEBRA Shared-Path Scientific Feasibility Pilot

Date: 2026-08-25  
Status: approved first software framework present; blocked on scientifically adequate cue-to-path data

Scientific status: exploratory feasibility analysis, not confirmatory evidence  
Scope: behavior audit, direct neural baselines, target-free geometry, then an
optional supervised CEBRA sensitivity analysis

This execution plan is governed by [`AGENTS.md`](AGENTS.md) and the mathematical
definitions in [`formalization.md`](formalization.md). Review findings and their
disposition are recorded in [`verification.md`](verification.md). Historical
handoffs under `sources/` are evidence inputs, not instructions.

## Purpose

Determine whether shared components of subsequently observed navigation paths
are behaviorally identifiable beyond start and goal, and whether cue-period
hippocampal population activity contains corresponding information. Cue,
session, initial view/heading, first action, trial history, and other available
variables form nuisance-adjusted sensitivity analyses. If they are unavailable,
the resulting confounding remains explicit and the claim stays “beyond start
and goal,” not “beyond all recorded task variables.”

The motivating example is:

```text
A -> B: A -- shared segment -- branch 1 -- B
A -> C: A -- shared segment -- branch 2 -- C
```

The shared segment could produce similar cue-period population states even though
the goals differ. However, an obligatory segment from start `A` can also be
explained by start location, view, or initial action. The pilot must distinguish
these explanations rather than assuming shared neural geometry implies a planned
graph representation.

This plan replaces the earlier software-smoke-centered execution order. A small
synthetic CEBRA API check remains a prerequisite, but the first scientific work
is the behavioral identifiability audit and raw/PCA neural analysis.

## Relationship To The Canonical Hypotheses

The canonical H1 remains unchanged:

- **H1a — information:** cue-period population activity improves held-out
  prediction of the same trial's subsequent observed path beyond start and goal.
- **H1b — structure:** any such prospective path information has reproducible
  low-dimensional organization.

Shared path components across different start-goal conditions are a
complementary structural analysis within the H1 program and a bridge to H2. They
do not replace H1a. If exact within-condition route variation is sparse, this
analysis may remain feasible while trial-specific H1a is weakly identifiable,
but it answers a different question.

The allowed compositional claim is:

> Cue-period population geometry covaries with shared components of subsequently
> observed paths after controlling endpoint-related and recorded nuisance
> variables.

The pilot cannot establish intention, a planning mechanism, or that the brain
literally represents a graph.

## Analysis Labels

Keep the stages distinct:

- **Software smoke test:** synthetic API and shape checks only.
- **Exploratory behavioral feasibility:** define and audit candidate path
  representations without neural data.
- **Exploratory neural analysis:** evaluate raw/PCA and target-free geometry on
  held-out trials.
- **Later confirmatory analysis:** only after the target, split, metric, nulls,
  exclusions, and effect threshold are frozen independently of the final test.

No smoke-test or exploratory output may be promoted into confirmatory evidence.

## Hard Data Gate

A real neural analysis requires each source trial `i` to link:

```text
source_trial_id
session_id
simultaneous_recording_group
cue_id
start_id
goal_id
cue_onset and cue_offset
cue-period spike counts for verified simultaneous units
navigation onset and end
success or timeout
subsequently observed path samples
```

Conceptually:

\[
S_i\in\mathbb N_0^{B_i\times U_{g(i)}},
\]

where \(B_i\) is the number of cue bins and \(U_{g(i)}\) is the verified
simultaneous population for recording group \(g(i)\).

The independent unit is the complete source trial. All cue bins, path samples,
windows, and bootstrapped derivatives from one trial remain in one split.

The current local `f1526be5` export does not pass this gate. It contains one
selected cell's navigation-period spike counts and spatial-bin IDs, not cue
activity, start/goal labels, or a verified trial-level simultaneous population.
It may support loader checks but not this scientific pilot.

A cross-session pseudopopulation also does not pass the trial-specific gate. It
can support condition-average prototypes, but it cannot recover one real trial's
population state, covariance, or exact subsequent path.

## Behavioral Object

### Graph as a candidate ruler

The graph is a proposed behavioral measurement model, not part of H1. Let

\[
\mathcal G=(V,E)
\]

represent authoritative navigable regions and valid directed transitions. A
trial's observed path is mapped to

\[
P_i=(v_{i1},v_{i2},\ldots,v_{iT_i}),
\qquad (v_{it},v_{i,t+1})\in E.
\]

Before use, path cleaning must declare:

- how invalid samples, including spatial bin `0`, are handled;
- whether invalid gaps split or exclude paths;
- whether repeated nodes are retained or compressed;
- whether nonadjacent transitions are rejected or interpolated; and
- how many samples, transitions, and trials each rule changes.

Interpolation can invent unobserved edges and therefore requires a sensitivity
analysis against exclusion.

The provisional primary cleaning rule drops invalid samples, splits paths at
invalid gaps, collapses consecutive repeated nodes only for route-shape metrics,
and rejects/splits nonadjacent transitions. It does not interpolate missing
edges. Shortest-path interpolation is sensitivity-only; imputed edges are
flagged and excluded from primary overlap counts. Record the authoritative
graph/adjacency hash and every affected sample, transition, segment, and trial.

The graph remains a working proposal until the training/validation behavior
audit shows that it captures meaningful route distinctions better than simpler
branch or region features.

### Shared path components

For a simple unordered representation, define a directed-edge indicator

\[
e_i\in\{0,1\}^{|E|}.
\]

Retain the ordered edge sequence separately when order, repeated visits, or
branch timing matter. Decompose overlap into:

- initial segment;
- middle segment;
- terminal segment;
- complete directed-edge overlap; and
- first informative branch decision.

This decomposition is essential:

- an obligatory initial segment may be start coding;
- an obligatory terminal segment may be goal coding;
- a shared middle segment across different endpoints provides stronger
  separation from endpoint identity.

### Candidate path distances

Behavior-only candidates include:

1. directed-edge Jaccard distance;
2. first-branch disagreement;
3. graph-aware dynamic time warping;
4. ordered shared-segment length; and
5. a simple directed-edge occupancy/count target.

No metric is selected before the audit. Candidate distance matrices must be
plotted and correlated with start, goal, cue, duration, and session. If two
metrics are nearly identical, the dataset cannot distinguish their scientific
interpretations.

Any learned target transformation, clustering, or dimensionality reduction is
fitted using training behavior only.

## Scientific Questions And Estimands

### Question 0: is path structure identifiable?

Before neural fitting, determine whether the dataset contains contrasts such as:

- same start, different goals, high versus low path overlap;
- same goal, different starts, high versus low path overlap;
- different starts and goals sharing a middle segment;
- different routes within the same start-goal condition, where available.

If shared path components are almost deterministic functions of start and goal,
the compositional question is not separately identifiable.

### H1a: incremental held-out path information

Let \(C_i=(A_i,G_i)\) denote start and goal, \(X_i\) the cue population, and
\(Y_i=h(P_i)\) a frozen behavior-only path target.

\[
\widehat Y_i^{(0)}=f_0(C_i),
\]

\[
\widehat Y_i^{(1)}=f_1(C_i,R(X_i)).
\]

Using the same held-out path loss \(\ell_P\), define

\[
\Delta_{\mathrm{neural}}=
\mathcal R_0-\mathcal R_1.
\]

A positive uncertainty-qualified value means neural features improve held-out
prediction beyond start and goal. A second sensitivity comparison adds available
nuisances \(W_i\) to both baseline and neural models:

\[
\widehat Y_i^{(0,+)}=f_0^+(C_i,W_i),
\qquad
\widehat Y_i^{(1,+)}=f_1^+(C_i,W_i,R(X_i)).
\]

The strongest wording is limited to variables included in \(W_i\). A separate
first-action/first-edge adjustment is required before arguing against a motor-
preparation explanation when action data exists. None of these estimands by
itself establishes intention or low-dimensional organization.

### Compositional path-geometry screen

For representation \(Z_i=R(X_i)\), define

\[
D^Z_{ij}=d_Z(Z_i,Z_j),
\qquad
D^P_{ij}=D_{\mathrm{path}}(P_i,P_j).
\]

Test whether path overlap explains held-out cue-state geometry after matching or
controlling:

```text
same start
same goal
same cue
same session or compatible recording group
available heading, view, speed, action, and trial-time variables
```

Prefer matched high-overlap versus low-overlap contrasts within the same nuisance
stratum. For held-out anchor trial \(i\), let \(\mathcal H_i\) and
\(\mathcal L_i\) be matched high- and low-overlap comparison sets. One
non-naive anchor statistic is

\[
\delta_i=
\frac{1}{|\mathcal L_i|}\sum_{j\in\mathcal L_i}D^Z_{ij}
-

\frac{1}{|\mathcal H_i|}\sum_{j\in\mathcal H_i}D^Z_{ij}.
\]

Positive \(\delta_i\) means high-overlap paths have closer cue states than
matched low-overlap paths. Pairwise RDM entries are dependent; uncertainty and
nulls operate on source trials, contiguous blocks, sessions, or animals rather
than treating all matrix entries as independent.

### H1b: reproducible low-dimensional organization

A candidate H1b result requires more than a 2D or 3D plot:

1. a low-dimensional representation retains held-out incremental information;
2. its geometry relates to path geometry after endpoint controls;
3. the result is stable across dimensions, splits, and seeds; and
4. where data permit, the result recurs across recording groups or sessions.

## Representation And Evaluation Order

Every scientifically interpreted representation uses the same source-trial
splits, downstream decoder family, target, and path loss.

| Representation | Future-path labels used to learn representation? | Role |
| --- | ---: | --- |
| Raw cue population | No | Primary direct information baseline |
| Train-fitted PCA | No | Primary linear low-dimensional baseline |
| Trial-aware CEBRA-Time | No future-path label; temporal bias remains | Secondary target-free representation |
| Graph/path-conditioned CEBRA | Yes | Supervised sensitivity analysis |
| Start-goal-conditioned CEBRA | Uses condition | Shortcut control |
| Shuffled-path CEBRA/control | Uses broken correspondence | Null control |

Different CEBRA samplers define different contrastive tasks. Their training
losses are not directly comparable. Compare them with the common held-out
decoder and \(\ell_P\), not by choosing the cleanest plot or lowest InfoNCE loss.

## Contrastive-Learning Design

### Trial-aware CEBRA-Time

CEBRA-Time is target-free only with respect to future path. Temporal positives
must remain inside the same source trial:

\[
(i,b)^+=(i,b+\delta),
\qquad 1\le b+\delta\le B_i.
\]

Never concatenate trials and allow temporal pairs to cross boundaries. Never
apply standard CEBRA-Time to an `N_trials x U` matrix whose row order is merely
trial order. If the installed API cannot express trial boundaries, this stage is
blocked until a boundary-aware sampler is implemented and reviewed.

### Path-conditioned CEBRA

For eligible training trials, a candidate positive sampler is

\[
p_+(j\mid i)=
\frac{\exp[-D_{\mathrm{path}}(P_i,P_j)^2/(2\sigma^2)]}
{\sum_{k\in\mathcal A_i}
 \exp[-D_{\mathrm{path}}(P_i,P_k)^2/(2\sigma^2)]}.
\]

The reference distribution \(p(i)\), positive distribution \(p_+\), negative
distribution \(q_-\), eligible set \(\mathcal A_i\), and scale \(\sigma\) must
all be declared. At minimum,

\[
\mathcal A_i=\{j\in\mathcal T_{\mathrm{train}}:
 j\ne i,\
 \operatorname{source}(j)\ne\operatorname{source}(i),\
 j\notin\operatorname{derivatives}(i),\
 j\text{ satisfies the predeclared nuisance stratum}\}.
\]

Validation and test trials never supply training positives or negatives. Block a
sampler when a stratum has too few independent eligible comparisons.

Two designs answer different questions:

1. **Within-start-goal sampler:** positives and negatives share start and goal;
   tests residual route variation but does not align global cross-condition
   geometry.
2. **Cross-condition matched sampler:** positives have high path-component
   overlap and negatives have lower overlap while matching same-start,
   same-goal, cue, and session relationships; tests compositional shared-path
   structure.

The second design is feasible only if the behavioral audit finds enough matched
contrasts. It must not be improvised after viewing neural embeddings.

Because path supervision explicitly rewards path-shaped geometry, successful
held-out performance supports supervised extractability. It does not
independently show that the native neural manifold was graph-shaped. Raw, PCA,
and path-label-free analyses therefore come first.

The CEBRA framework permits custom sampling distributions, but the inspected
public sklearn API does not expose an arbitrary precomputed graph-distance
sampler as a one-line option. Any such sampler requires lower-level CEBRA/PyTorch
work and independent API/code review after the scientific gates pass.

## Nulls And Controls

Minimum controls are:

- start-goal-only prediction;
- within-start-goal permutation of neural-to-path trial assignments;
- matched-pair path-overlap permutations preserving nuisance strata;
- session or recording-group controls;
- seed and latent-dimension sensitivity;
- raw and PCA representation baselines;
- target-free CEBRA-Time when trial boundaries can be represented safely;
- available cue, view, heading, action, speed, duration, and trial-time controls;
- previous-trial/previous-goal and success-selection sensitivity; and
- contiguous-block or session-level sensitivity where sample size permits.

All preprocessing and hyperparameter selection occur inside training/validation
data. Before final testing, freeze one primary target, path loss, null,
effect-size/uncertainty criterion, inclusion rule, and validation-only model
selection procedure. The final test remains untouched until the analysis is
frozen.

## First Experiment

### Phase 0 — bounded software preflight

Use synthetic data only to verify the pinned CEBRA API can fit, transform, save,
and reload a small two-dimensional array. Record package versions, constructor
parameters, seed, device, and shapes. Do not inspect or interpret embedding
geometry.

The current one-cell navigation export needs only a loader/shape check; fitting
CEBRA to it is optional and has no scientific value for this hypothesis.

**Software result (2026-08-26):** CEBRA `0.6.1` passed the bounded CPU
`256 x 12 -> 256 x 3` fit/transform/save/load smoke. The saved and reloaded
transforms matched exactly in this run. Artifacts and versions are recorded at
`outputs/cebra_pilot/trial-20260825-cebra-v2/`. This is not H1 evidence.

**Gate:** stop and amend this plan if a later CEBRA release or API differs from
the reviewed implementation.

### Phase 1 — data, provenance, and immutable split audit

Verify the hard data contract, trial identity, simultaneity, cue timing, path
linkage, units, missingness, inclusion rules, preprocessing history, previous-
trial fields, and success-selection history. Define and hash source-trial
training/validation/test assignments before adaptive path-metric selection.
Derivatives of one source trial share its assignment; primary neural evaluation
stays within each verified simultaneous-recording group.

**Gate:** no neural analysis without cue-aligned trial-linked simultaneous
population data. If no untouched test set can be reserved, the entire run remains
exploratory and cannot become confirmatory evidence.

### Phase 2 — training/validation behavior-only path audit

1. reconstruct training/validation observed paths;
2. map paths to candidate directed edges or simpler branch features;
3. apply and audit the provisional primary cleaning rule;
4. label obligatory and variable initial, middle, and terminal components;
5. count trials for every start-goal and matched-overlap stratum;
6. compute candidate path-distance matrices;
7. quantify correlations with start, goal, cue, duration, session, previous-trial
   variables, and available sensory/motor nuisances; and
8. freeze only the contrasts the training/validation data can identify.

Do not inspect test-path results to redesign graph granularity, cleaning,
exclusions, targets, metrics, or contrasts. Apply the frozen behavior mapping to
test trials once during final evaluation.

**Primary artifact:** a behavior-only identifiability report and candidate matched
contrast table. No neural data enters this phase.

**Gate:** if no adequate high/low-overlap contrasts exist, stop the compositional
analysis and report the identifiability limit.

### Phase 3 — target and analysis freeze

Using the immutable assignments from Phase 1, freeze:

- inclusion and exclusion rules;
- one provisional path target and common loss;
- nuisance matching/adjustment rules;
- decoder family;
- primary null;
- dimensionality and seed ranges;
- one primary effect-size/uncertainty criterion;
- within-recording-group evaluation and group-level synthesis rule; and
- strongest allowed claim.

### Phase 4 — direct H1a baselines

Fit and compare:

```text
start + goal -> path
start + goal + raw cue population -> path
start + goal + PCA cue population -> path
```

Use the same held-out target and path loss. Report per-trial predictions,
\(\Delta_{\mathrm{neural}}\), uncertainty, and within-condition nulls.

### Phase 5 — compositional geometry screen

Using raw and train-fitted PCA representations first:

1. compute held-out cue-state distances;
2. compare matched high- versus low-path-overlap pairs;
3. separate initial, middle, terminal, and full-path overlap;
4. control start, goal, cue, session, and available nuisances; and
5. use source-trial/session-aware uncertainty and nulls.

This is the first experiment directly addressing shared path components.

### Phase 6 — trial-aware CEBRA-Time

Proceed only if time-resolved cue data and boundary-aware temporal sampling are
available. Use the same downstream decoder and path loss as raw/PCA.

### Phase 7 — supervised path-conditioned CEBRA

Proceed only after Phases 2–6 establish adequate contrasts and valid baselines.
Predeclare the sampler, negatives, \(\sigma\), architecture, dimensions, seeds,
and stopping rule. Evaluate with the same held-out decoder and loss.

This phase is secondary. A cleaner embedding is not a successful result unless
it improves common held-out evaluation and survives matched nulls.

### Phase 8 — independent review and closeout

An independent reviewer must check:

- leakage and train/test boundaries;
- pseudoreplication and pairwise dependence;
- simultaneity and trial linkage;
- start/goal/cue/session confounds;
- path-metric sensitivity;
- CEBRA supervision and claim language; and
- whether conclusions exceed the observed data.

Record all attempted runs, including failures and negative results.

## Required Outputs

Each scientific method must retain:

1. source-trial split assignments;
2. data hashes, code revision, dirty state, package versions, and configuration;
3. fitted behavior transformation from training data;
4. start-goal baseline and neural-model predictions;
5. per-trial path losses and \(\Delta_{\mathrm{neural}}\);
6. matched path-component contrast definitions;
7. within-condition and matched null distributions;
8. seed and dimension sensitivity;
9. neural and path RDMs where geometry is tested;
10. exclusions and missing-data counts; and
11. explicit scientific-status and claim-boundary text.

Generated outputs belong under ignored `outputs/cebra_pilot/`. Do not modify raw
data or silently overwrite prior runs.

## Interpretation Ladder

| Result | Strongest allowed interpretation |
| --- | --- |
| Synthetic API check passes | The software accepts the expected shapes |
| Path overlap is determined by start/goal | Compositional structure is not separately identifiable here |
| Raw/PCA improves held-out path prediction | Preliminary H1a evidence, subject to the full data contract and nulls |
| Raw/PCA cue geometry tracks matched shared segments | Preliminary evidence for compositional prospective path structure |
| Trial-aware CEBRA-Time preserves the result | The relation is recoverable without future-path supervision, under temporal bias |
| Only path-conditioned CEBRA succeeds | Path information may be supervised-extractable; native geometry remains uncertain |
| Path-conditioned CEBRA succeeds only in training | Memorization, overfitting, or leakage is likely |
| Matched shuffled controls perform similarly | No convincing trial-specific or compositional neural-path relationship |
| Independently trained ANN and biological RDMs agree | Representational convergence, not shared mechanism |

## Link To Artificial Navigation Networks

Train the artificial navigation agent independently on its navigation objective.
Extract cue/planning-equivalent hidden states and apply the same frozen graph or
path-component ruler:

- incremental path prediction beyond start and goal;
- matched shared-component geometry;
- target-free representational dissimilarity matrices;
- held-out conditions; and
- multiple agent seeds.

Do not make biological and artificial representations similar by using the same
path-conditioned contrastive objective as primary evidence. Shared supervision
can induce apparent cross-system agreement.

## Deferred Decisions

The behavioral audit and adequate cue data must precede decisions about:

- graph granularity;
- directed-edge, branch, graph-DTW, or other primary target;
- cue count versus rate and cue-window definition;
- cue aggregation versus time-resolved modeling;
- unsuccessful and timeout trials;
- decoder family and effect-size threshold;
- secondary trial-block, session-, animal-, route-, or condition-held-out
  generalization beyond the fixed within-recording-group primary evaluation;
- CEBRA sampler, architecture, dimensions, and seed count; and
- ANN comparison metric.

## Stop Conditions

Stop rather than infer or improvise when:

- simultaneous population or source-trial identity is unverified;
- cue activity and observed path are not linked to the same trial;
- path overlap is inseparable from start, goal, or cue in available contrasts;
- temporal sampling would cross trial boundaries;
- a pseudopopulation would be treated as a real trial population;
- path preprocessing would use test behavior;
- pairwise RDM entries would be treated as independent samples;
- graph interpolation would silently invent route edges;
- incompatible exports would need to be stacked; or
- interpretation begins to exceed the declared exploratory claim boundary.

## Authority And Evidence References

Canonical authority:

- `AGENTS.md`
- `docs/research-questions.md`
- `docs/analysis-contract.md`
- `docs/dataset-card.md`

Pilot-local specification and audit:

- `docs/cebra_pilot/AGENTS.md`
- `docs/cebra_pilot/formalization.md`
- `docs/cebra_pilot/verification.md`

Historical source, preserved but noncanonical:

- `docs/cebra_pilot/sources/cebra-graph-navigation-handoff.md`

Published method citation:

- Schneider, Lee, and Mathis (2023),
  <https://doi.org/10.1038/s41586-023-06031-6>

Official CEBRA release and API documentation must be rechecked immediately before
implementation.
