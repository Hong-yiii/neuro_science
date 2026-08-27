# First CEBRA Pilot Formalization

Date: 2026-08-25  
Status: formalized design; first software framework implemented

Scientific status: exploratory feasibility; neural analysis blocked by current data

## Authority And Evidence Labels

This document formalizes the pilot-specific mathematics. It derives from
`../research-questions.md` and `../analysis-contract.md`; it does not replace
them.

Statements are labelled implicitly by role:

- **measured:** directly recorded upstream;
- **derived:** produced by a declared transformation of measurements;
- **estimand:** the statistical quantity the analysis seeks to estimate;
- **proposal:** a method that remains subject to behavioral audit;
- **interpretation:** the strongest scientific language permitted by the
  measurements and evaluation.

The graph-navigation handoff under `sources/` is a historical proposal. Published
CEBRA and hippocampal studies motivate methods and biological plausibility, but
none establishes this dataset's result in advance.

## Research Questions And Claim Hierarchy

### Canonical H1a

Does cue-period hippocampal population activity improve held-out prediction of
the same trial's subsequently observed path beyond start and goal?

### Canonical H1b

If H1a has support, does the path-relevant cue information exhibit reproducible
low-dimensional organization?

### Complementary shared-path question

Do cue-period population states covary with reusable components shared by future
paths across task conditions after endpoint and available nuisance controls?

This is a structural screen within the H1 program. It is not a substitute for
H1a. It is potentially informative when within-start-goal route variation is
limited, but it answers a different question.

### Claim ceiling

The strongest planned claim is an association between cue-period population
activity and the subsequently observed path. Decoding or geometry cannot by
itself establish intention, causal planning, a literal internal graph, or a
shared mechanism with an artificial agent.

## Indices And Core Objects

For real source trial \(i\):

| Symbol | Meaning | Status |
| --- | --- | --- |
| \(r_i\) | recording session | measured metadata |
| \(g_i\) | verified simultaneous-recording group | required metadata |
| \(s_i\) | start identity | measured task label |
| \(q_i\) | goal/instruction cue identity shown during cue period | measured task label; exact semantics require lab verification |
| \(g^*_i\) | goal identity | measured task label |
| \(N_i\) | cue-period unit-by-time spike-count object | derived from sorted spikes and event alignment |
| \(P_i\) | cleaned subsequently observed graph path | derived behavior |
| \(W_i\) | available nuisance variables | measured or derived, declared field by field |
| \(X_i\) | declared neural trial representation | derived from \(N_i\) |
| \(Z_i\) | learned neural representation | derived from \(X_i\) |

Goal uses \(g^*_i\) so that \(g_i\) remains reserved for simultaneous-recording
group.

A minimum nuisance set is

\[
W_i=(q_i,r_i,\text{trial index}_i,\text{previous goal}_i,
     \text{previous success}_i).
\]

Where available, extend it with cue-period or navigation-onset view, heading,
gaze, speed, first action/first edge, success/timeout, and exposure. Absence of a
nuisance variable limits the claim; it is not evidence that the nuisance is
irrelevant.

## Neural Data Object

For trial \(i\), let

\[
N_i\in\mathbb N_0^{B_i\times U_{g_i}},
\]

where \(B_i\) is the number of cue bins and \(U_{g_i}\) is the number of curated
units in the verified simultaneous group. Let \(M_{ib}\in\{0,1\}\) be a valid
cue-bin mask and \(\Delta t_{ib}\) its exposure.

Two candidate trial summaries are

\[
X^{\mathrm{count}}_{iu}
=

\sum_{b=1}^{B_i}M_{ib}N_{ibu},
\]

and

\[
X^{\mathrm{rate}}_{iu}
=

\frac{\sum_bM_{ib}N_{ibu}}
     {\sum_bM_{ib}\Delta t_{ib}}.
\]

Count versus rate and the cue window are deferred until timing and missingness
are verified. If all valid trials have equal exposure, counts preserve the
Poisson observation scale most directly. If exposure differs, rates or a count
model with exposure must be considered.

The independent evaluation unit is source trial \(i\), not bin \((i,b)\). All
bins, windows, augmentations, and bootstrapped derivatives of one source trial
remain in one split.

## Sequential Dependence And Selection

The next trial may begin at the previous trial's goal. Current derived exports
also used a successful-after-successful filter. Therefore trial \(i\) may depend
on trial \(i-1\), and the retained sample may be selected.

The future trial table must retain:

```text
source_trial_id, previous_trial_id, trial_index,
previous_goal_id, previous_success,
current_success, timeout, inclusion_reason
```

Primary uncertainty remains trial-aware, with contiguous-block or session-level
split/resampling sensitivity where sample size permits. Exclusion counts and
path distributions are reported by start, goal, cue, session, and success
history.

## Immutable Split Before Adaptive Audit

Let source trials be partitioned into

\[
\mathcal T_{\mathrm{train}},\quad
\mathcal T_{\mathrm{validation}},\quad
\mathcal T_{\mathrm{test}}.
\]

The partition is created and hashed after provenance/schema checks but before
adaptive path-metric selection or neural fitting. Derivatives of one source
trial share its assignment. Splits respect recording groups and, where needed,
contiguous blocks.

- Training behavior can be explored to construct candidate graph/path rules.
- Validation behavior selects among predeclared candidates and hyperparameters.
- Test behavior receives the frozen mapping once and is not used to redesign
  graph granularity, cleaning, targets, exclusions, metrics, or contrasts.

If all behavior is inspected before a split is reserved, the result is labelled
exploratory and a later confirmatory claim requires a new untouched session or
dataset.

## Graph And Path Construction

### Authoritative graph

A graph at provisional granularity \(\eta\) is

\[
\mathcal G_\eta=(V_\eta,E_\eta).
\]

It must come from authoritative geometry or adjacency, not ordinal arithmetic on
`spatial_bin_id`. Record the graph construction code revision, parameters, and
content hash.

### Raw mapping

Let navigation sample \(t\) map through \(\mu_\eta\):

\[
\overline v_{it}=\mu_\eta(\text{behavior}_{it})
\in V_\eta\cup\{\bot\},
\]

where \(\bot\) denotes invalid/unmapped behavior, including spatial bin `0`.
The raw mapped sequence is

\[
\overline P_i=(\overline v_{i1},\ldots,\overline v_{iT_i}).
\]

### Primary cleaning function

The provisional primary cleaning function returns an ordered list of valid
segments, not one silently concatenated sequence:

\[
\mathcal P_i
=

\Gamma_\eta(\overline P_i)
=

(P_{i1},\ldots,P_{iK_i}).
\]

Until validation evidence justifies another rule, \(\Gamma_\eta\):

1. removes invalid samples and **splits** at invalid runs rather than stitching
   across them;
2. retains raw repeats/dwell duration in a side representation but collapses
   consecutive repeated nodes for route-shape metrics;
3. rejects or splits nonadjacent transitions in the primary path; and
4. performs no shortest-path interpolation in the primary analysis.

A sensitivity analysis may interpolate nonadjacent transitions through the
verified graph, but every imputed edge is flagged and excluded from primary
shared-edge counts. Report changed samples, transitions, segments, and trials.

If \(K_i=0\), the trial has no valid graph target and is excluded with a recorded
reason. A one-node segment is retained for occupancy accounting but has no edge
and is ineligible for edge-based targets. A path target or metric must declare
how it combines multiple segments; it may not concatenate across a gap. Later
notation writes \(P_i\) as shorthand for the complete segment list
\(\mathcal P_i\), not for a bridged sequence.

### Directed edge sequences

For valid segment \(k\),

\[
P_{ik}=(v_{ik1},\ldots,v_{ikT'_{ik}}),
\qquad
(v_{ikt},v_{ik,t+1})\in E_\eta.
\]

Its directed edge sequence is

\[
Q_{ik}=(a_{ik1},\ldots,a_{ikL_{ik}}),
\qquad
a_{ikt}=(v_{ikt},v_{ik,t+1}).
\]

For set-based metrics, define the trial edge set without adding bridge edges:

\[
E(P_i)=\bigcup_{k=1}^{K_i}E(P_{ik}).
\]

The directed-edge indicator \(e_i\in\{0,1\}^{|E_\eta|}\) encodes this union.
Pairs for which both edge sets are empty are ineligible for edge Jaccard and are
reported rather than assigned an arbitrary distance.

## Candidate Shared-Path Functions

All functions in this section are behavior-only proposals. One primary target
and loss are selected using training/validation behavior before final testing.

### Directed-edge Jaccard distance

For edge sets \(E(P_i)\) and \(E(P_j)\),

\[
D_{\mathrm{edge}}(i,j)
=

1-
\frac{|E(P_i)\cap E(P_j)|}
     {|E(P_i)\cup E(P_j)|}.
\]

This captures unordered directed-edge presence. It discards order and repeated
visits, so ordered sequences remain available.

### Shared contiguous directed segment

For segment sequences \(Q_{ik},Q_{jm}\), define

\[
L_{\mathrm{contig}}(i,j)
=

\max_{k,m,a,b,\ell}
\left\{
\ell:
Q_{ik}[a:a+\ell-1]=Q_{jm}[b:b+\ell-1]
\right\}.
\]

A maximizing segment is classified relative to the original trial boundaries,
not merely its cleaned segment:

- **initial** only if it starts at the first observed edge of both trials;
- **terminal** only if it ends at the last observed edge of both trials;
- **middle** if it touches neither trial endpoint; or
- **mixed** otherwise.

If an invalid gap obscures the relevant endpoint, the corresponding
initial/terminal label is unavailable rather than inferred.

An initial segment shared only by paths with the same start is vulnerable to
start/view/action confounding. A terminal segment is vulnerable to goal coding.
A shared middle segment across different endpoints is a stronger—but still
observational—contrast.

### First informative branch

Let \(B_i\) be the first node along \(P_i\) with more than one eligible outgoing
edge under the task. Let \(A_i^{\mathrm{branch}}\) be the directed edge selected
there. Candidate branch disagreement is

\[
D_{\mathrm{branch}}(i,j)
=

\mathbf 1
\left[A_i^{\mathrm{branch}}\ne A_j^{\mathrm{branch}}\right],
\]

computed only when the branch definition is comparable for the two paths.

### Graph-aware DTW sensitivity

Dynamic time warping is grounded in the standard recurrence of Sakoe and Chiba
(1978). Using graph shortest-path distance as the local cost is a project-specific
proposal:

\[
C(a,b)=d_{\mathcal G_\eta}(v_{ia},v_{jb})
+
\min\{C(a-1,b),C(a,b-1),C(a-1,b-1)\}.
\]

Report endpoint initialization, slope/warping constraints, unreachable-node
handling, normalization by path length, and the predeclared method for combining
multiple cleaned segments. Graph-DTW is undefined for a trial until that segment
aggregation rule is fixed. It is a sensitivity metric, not a CEBRA result or a
settled primary target.

## Behavioral Identifiability Gate

Let \(O_{ij}\) be one frozen path-overlap feature and let

\[
M_{ij}=(
\mathbf 1[s_i=s_j],
\mathbf 1[g^*_i=g^*_j],
\mathbf 1[q_i=q_j],
\mathbf 1[r_i=r_j],
\text{available nuisance relations}
).
\]

The shared-path question is identifiable only if \(O_{ij}\) retains variation
within predeclared nuisance strata. Required counts include:

- same start, different goals, high versus low overlap;
- same goal, different starts, high versus low overlap;
- different starts and goals sharing versus not sharing a middle segment; and
- same-start-goal route variants, where available.

If overlap is almost deterministic from start, goal, cue, or session, no model
can identify a separate shared-path explanation from this dataset. This is a
data limitation, not a reason to add model capacity.

## H1a Estimands

### Canonical start-goal estimand

Let

\[
C_i=(s_i,g^*_i),
\qquad
Y_i=h(P_i),
\]

where \(h\) is a frozen behavior-only path target. For representation
\(R(X_i)\), fit

\[
\widehat Y_i^{(0)}=f_0(C_i),
\qquad
\widehat Y_i^{(1)}=f_1(C_i,R(X_i)).
\]

Using one common path loss \(\ell_P\),

\[
\mathcal R_m(C)
=

\mathbb E_{i\in\mathcal T_{\mathrm{test}}}
\left[
\ell_P(Y_i,\widehat Y_i^{(m)})
\right],
\]

and

\[
\Delta_C
=

\mathcal R_0(C)-\mathcal R_1(C).
\]

A positive uncertainty-qualified \(\Delta_C\) means cue neural features improve
held-out path prediction beyond start and goal for the analyzed population and
trial inclusion rules.

### Nuisance-adjusted sensitivity estimand

Let

\[
C_i^+=(s_i,g^*_i,W_i).
\]

Fit matched-capacity models

\[
\widehat Y_i^{(0,+)}=f_0^+(C_i^+),
\qquad
\widehat Y_i^{(1,+)}=f_1^+(C_i^+,R(X_i)),
\]

and define

\[
\Delta_{C^+}
=

\mathcal R_0(C^+)-\mathcal R_1(C^+).
\]

The canonical hypothesis remains beyond start and goal. The strongest empirical
wording is limited to variables actually present in \(C_i^+\). If cue, session,
view, heading, or action is unavailable, report that confounding as unresolved.
A separate first-action/first-edge-adjusted sensitivity is required before
interpreting a result as more than motor preparation when action data exists.

## Neural Representations

All learned representations are fitted on training trials only.

| Representation | Definition | Future-path supervision? |
| --- | --- | ---: |
| Raw | \(Z_i=X_i\) | No |
| PCA | \(Z_i=W_d^\top(X_i-\mu)\), with \(W_d,\mu\) fit on training data | No |
| Trial-aware CEBRA-Time | \(Z_{ib}=R_\theta(N_{i,b:\,})\) with within-trial temporal positives | No future-path label; temporal bias |
| Path-conditioned CEBRA | \(Z_i=R_\theta(X_i)\) with path-derived pairs | Yes |

Primary evaluation is within each verified simultaneous-recording group because
unit identities and dimensions can differ across groups. Estimate
\(\Delta_{C,g}\) or geometry effects within group and combine them with a
predeclared group-level summary/meta-analysis. Cross-session comparison uses
condition/path RDMs or prototypes, not pooled raw unit vectors with mismatched
columns.

## Shared-Path Geometry Estimand

For a representation \(Z\), define neural distance

\[
D^Z_{ij}=d_Z(Z_i,Z_j).
\]

For each held-out anchor trial \(i\), define the eligible comparison pool

\[
\mathcal J_i=
\{j\in\mathcal T_{\mathrm{test}}:
 j\ne i,\
 g_j=g_i,\
 \operatorname{source}(j)\ne\operatorname{source}(i),\
 j\notin\operatorname{derivatives}(i)\}.
\]

Construct matched sets from \(\mathcal J_i\) and the same predeclared nuisance
stratum:

- \(\mathcal H_i\subset\mathcal J_i\): high shared-path overlap;
- \(\mathcal L_i\subset\mathcal J_i\): low shared-path overlap.

Train/validation anchors use only their own partition while developing the
statistic; the final reported anchor statistic uses the untouched test
partition and the already frozen matching rules.

Define one anchor-level statistic

\[
\delta_i
=

\frac{1}{|\mathcal L_i|}
\sum_{j\in\mathcal L_i}D^Z_{ij}
-

\frac{1}{|\mathcal H_i|}
\sum_{j\in\mathcal H_i}D^Z_{ij}.
\]

Positive \(\delta_i\) means high-overlap paths have closer cue representations
than matched low-overlap paths. Do not treat all pairwise matrix entries as
independent samples.

Uncertainty and nulls operate on source trials, contiguous blocks, sessions, or
animals as supported by the data. A blocked permutation reassigns paths/neural
trials only within the predeclared nuisance and recording-group strata while
keeping derivatives together. Group-level effects summarize anchor statistics
without claiming \(N(N-1)/2\) independent observations.

## H1b Criteria

Let \(Z_i^{(d,a)}\) be dimension \(d\), seed/split \(a\). A candidate H1b result
requires:

1. retained held-out incremental prediction over a predeclared range of \(d\);
2. positive matched shared-path geometry effects or another frozen path-geometry
   statistic after endpoint controls;
3. stability across dimensions, splits, and seeds; and
4. recurrence across appropriate simultaneous groups/sessions where data permit.

Across two fits, linear consistency may be assessed through

\[
Z^{(a)}\approx Z^{(b)}L,
\]

with the alignment map fitted without test leakage. Consistency means agreement
up to the declared transformation under assumptions, not identical coordinates
or biological mechanism.

## CEBRA Objective And Sampling

For encoder \(R_\theta\) and normalized-dot-product similarity,

\[
\psi_\theta(x,y)
=

\frac{R_\theta(x)^\top R_\theta(y)}{\tau}.
\]

CEBRA specifies reference, positive, and negative distributions

\[
x\sim p(x),
\qquad
y^+\sim p_+(y\mid x),
\qquad
y^-_k\sim q_-(y\mid x).
\]

The sampled CEBRA objective in Schneider, Lee, and Mathis (2023) is

\[
\mathcal L_n
=

\mathbb E
\left[
-\psi_\theta(x,y^+)
+
\log\sum_{k=1}^{n}\exp\psi_\theta(x,y^-_k)
\right].
\]

The implementation must use the installed CEBRA objective rather than a local
reimplementation. Normalized loss is a within-sampler training diagnostic, not
the primary comparison across samplers with different pair distributions.

### Trial-aware CEBRA-Time

For cue bin \((i,b)\), a temporal positive must satisfy

\[
(i,b)^+=(i,b+\delta),
\qquad 1\le b+\delta\le B_i.
\]

No positive crosses a trial boundary. CEBRA `0.6.1` is now pinned and its
fit/transform/save/load path has passed a contiguous synthetic smoke test. Its
public sklearn API does not expose explicit trial-boundary metadata, and public
source inspection indicates contiguous index offsets. Therefore trial-aware
CEBRA-Time remains blocked pending a reviewed boundary-aware lower-level sampler;
the synthetic smoke does not relax this requirement.

### Path-conditioned sampler

For training anchor \(i\), the eligible set is

\[
\mathcal A_i=
\left\{
 j\in\mathcal T_{\mathrm{train}}:
 j\ne i,
 \operatorname{source}(j)\ne\operatorname{source}(i),
 j\notin\operatorname{derivatives}(i),
 j\text{ satisfies the predeclared nuisance stratum}
\right\}.
\]

A candidate positive distribution is

\[
p_+(j\mid i)
=

\frac{\exp[-D_{\mathrm{path}}(P_i,P_j)^2/(2\sigma^2)]}
     {\sum_{k\in\mathcal A_i}
      \exp[-D_{\mathrm{path}}(P_i,P_k)^2/(2\sigma^2)]}.
\]

Declare \(p(i)\), \(p_+\), \(q_-\), \(\mathcal A_i\), \(\sigma\), batch
construction, and behavior preprocessing before fitting. Block the sampler if a
stratum has too few nonderivative positives/negatives.

Two distinct designs are permitted only after the behavior audit:

1. **within-start-goal:** all eligible comparisons share \((s,g^*)\), targeting
   residual route variation;
2. **cross-condition matched:** high/low path overlap varies while same-start,
   same-goal, cue, session/group, and available nuisance relationships are
   matched or adjusted.

The CEBRA mathematical framework allows custom distributions, but the inspected
public sklearn API does not expose an arbitrary precomputed graph-distance
sampler as a simple argument. A graph sampler therefore requires lower-level
CEBRA/PyTorch extension and independent code review; it is not part of the first
software preflight.

### Forced-geometry interpretation

Path conditioning explicitly rewards

\[
D_{\mathrm{path}}(P_i,P_j)\downarrow
\Longrightarrow
D^Z_{ij}\downarrow.
\]

Training separation can be optimization or memorization. Held-out improvement
supports supervised extractability of path-related neural features. It does not
independently prove that the native neural manifold was graph-shaped. Raw, PCA,
and path-label-free analyses therefore precede path-conditioned CEBRA.

## Common Evaluation And Nulls

Every representation uses the same frozen source-trial split, target \(Y=h(P)\),
decoder family, and path loss \(\ell_P\).

Minimum nulls and controls are:

1. start-goal-only prediction;
2. nuisance-adjusted baseline where fields exist;
3. within-start-goal neural/path permutation within compatible groups;
4. matched shared-path permutation preserving nuisance strata;
5. source-trial derivative grouping;
6. session/group and contiguous-block sensitivity;
7. raw and train-fitted PCA baselines;
8. seed and latent-dimension sensitivity; and
9. path-cleaning/graph-granularity sensitivity.

Before the final test, freeze one primary target, one path loss, one primary null,
one effect-size/uncertainty criterion, inclusion rules, and validation-only model
selection. Other metrics remain explicitly exploratory sensitivity analyses.

Do not compare XY-, graph-, start-goal-, trajectory-, and shuffled CEBRA models
by choosing the lowest contrastive loss. Their sampling problems differ. Use the
common held-out decoder/loss and predeclared geometry statistics.

## Pseudopopulation Boundary

For condition \(c=(s,g^*)\), a cross-session pseudopopulation has form

\[
\widetilde X_{c,m}
=

\left[
X^{(1)}_{c,\pi_1(m)},
\ldots,
X^{(R)}_{c,\pi_R(m)}
\right],
\]

where the components come from different real trials. There is generally no one
observed path belonging to all columns of \(\widetilde X_{c,m}\).

It may support condition-average prototypes such as
\(\mathbb E[X\mid s,g^*]\). It cannot support exact trial-specific H1a,
simultaneous covariance, population dynamics, or intention. A CEBRA run on such
an object is a condition-level or software analysis unless a different valid
linkage is demonstrated.

### Fixed-195 path-family pseudopopulation

The first exploratory pseudopopulation fixes the 195 cells selected for spatial
tuning; expansion to all recorded cells is deferred. Let

\[
f_i=\phi(P_i;s_i,g^*_i)
\]

be a behavior-only route-family label defined within one start-goal condition.
The provisional \(\phi\) is the exact ordered directed corridor/branch-decision
signature after frozen graph cleaning. Distance-based clustering is permitted
only if the training/validation audit shows that exact signatures are too
sparse.

Let recording group \(a\) contain unit block \(X_i^{(a)}\). For route family
\(f\), pseudotrial \(m\) is

\[
\widetilde X_{s,g^{\star},f,m} = \left[
X^{(1)}_{\pi_1(s,g^{\star},f,m)},\ldots,
X^{(R)}_{\pi_R(s,g^{\star},f,m)}
\right].
\]

All units in one verified recording group use the same real source trial
\(\pi_a\); cells are not sampled independently within that group. Every selected
source trial must share start, goal, and the frozen route-family label, but the
component trials need not—and generally do not—share one exact path. The target
attached to \(\widetilde X\) is therefore \(f\), or a frozen family prototype,
never the exact path of one component trial.

Source-trial splits are fixed before fitting \(\phi\). Pseudotrials are assembled
separately inside each split, and every source trial and bootstrap derivative
remains in one split. Design eligibility requires independent training/validation
source-trial support for each retained route family in every contributing
recording group. Missing blocks are not imputed. The frozen mapping is applied to
test behavior once; a predeclared test-support failure makes the affected
contrast non-evaluable and cannot trigger redesign. The primary null permutes
route-family labels within recording group, start, and goal before pseudotrial
reconstruction.

This analysis estimates condition-level route-family discrimination beyond
endpoints. Because the route label is used to align trials across sessions, it
is a retrospective pseudopopulation comparison, not online prediction of an
unknown real trial. It cannot establish trial-specific H1a, simultaneous
geometry, covariance, population dynamics, or intention.

## Artificial-Agent Link

Let \(H_i^A\) be an independently task-trained agent's cue/planning-equivalent
hidden state and \(P_i^A\) its subsequent path. Apply the same frozen path ruler,
baselines, and held-out metrics to biology and agent separately.

For condition/path RDMs \(D^B,D^A\), a descriptive comparison is

\[
\rho_{BA}
=

\rho(\operatorname{vec}D^B,\operatorname{vec}D^A).
\]

Use predeclared matched conditions, endpoint controls, biological
trial/session-aware uncertainty, and multiple agent seeds. Pairwise RDM entries
are dependent. If both systems receive the same path-conditioned CEBRA
objective, shared geometry may be analysis-induced; such a comparison is
secondary. Similarity supports representational convergence, not unit-neuron
equivalence or a shared mechanism.

## Decision Register

| Item | Status | Current decision or gate |
| --- | --- | --- |
| Independent unit | Fixed | Complete source trial |
| Scientific order | Fixed | Data/split audit → behavior audit → raw/PCA → boundary-safe CEBRA-Time → optional path-conditioned CEBRA |
| Current local neural data | Blocked | Does not satisfy cue/simultaneity/path linkage |
| Pseudopopulation claim | Fixed | Condition-level route-family discrimination only; exact path and simultaneous-population claims remain blocked |
| First pseudopopulation cells | Fixed | 195 spatially selected cells; all-cell expansion is future work |
| Pseudopopulation route target | Provisional | Exact ordered corridor/branch signature within start-goal; cluster only if the support audit requires it |
| Graph role | Fixed | Candidate behavioral ruler, not hypothesis |
| Primary graph cleaning | Provisional | Split invalid gaps; collapse repeats for shape; reject nonadjacent transitions; no primary interpolation |
| Primary neural evaluation scope | Fixed | Within verified simultaneous group, then group-level synthesis |
| H1a estimand | Fixed | \(\Delta_C\), plus nuisance-adjusted sensitivity \(\Delta_{C^+}\) |
| Shared-path statistic | Provisional | Matched per-anchor \(\delta_i\), source-level resampling/nulls |
| CEBRA-Time | Blocked with public sklearn API | Installed 0.6.1 preflight passes, but grouped trial boundaries are not exposed |
| Path-conditioned sampler | Deferred | Requires identifiable contrasts and lower-level implementation review |
| Cue count/rate/window | Deferred | Requires verified exposure/timing |
| Graph granularity | Deferred | Training/validation behavior only |
| Primary path target/loss | Deferred | Freeze before final test |
| Effect threshold | Deferred | Freeze with target/null before final test |
| ANN metric | Deferred | Only after biological result and matched agent data |

## Evidence Base And Limits

### CEBRA

Schneider, Lee, and Mathis (2023), “Learnable latent embeddings for joint
behavioural and neural analysis,” _Nature_ 617, 360–368.
<https://doi.org/10.1038/s41586-023-06031-6>

Supports the contrastive framework, time/behavior-conditioned sampling,
decoding, and conditional consistency claims. It does not test this project's
cue-to-future-path hypothesis or graph-distance extension.

### Dynamic time warping

Sakoe and Chiba (1978), “Dynamic programming algorithm optimization for spoken
word recognition,” _IEEE Transactions on Acoustics, Speech, and Signal
Processing_ 26(1), 43–49.
<https://doi.org/10.1109/TASSP.1978.1163055>

Supports the DTW recurrence and warping constraints. Substituting graph
shortest-path distance as local cost is this project's proposed sensitivity
metric, not a result of that paper.

### Biological plausibility, not direct validation

- Johnson and Redish (2007), “Neural ensembles in CA3 transiently encode paths
  forward of the animal at a decision point,” _Journal of Neuroscience_ 27,
  12176–12189. <https://doi.org/10.1523/JNEUROSCI.3761-07.2007>
- Pfeiffer and Foster (2013), “Hippocampal place-cell sequences depict future
  paths to remembered goals,” _Nature_ 497, 74–79.
  <https://doi.org/10.1038/nature12112>
- Ferbinteanu and Shapiro (2003), “Prospective and retrospective memory coding
  in the hippocampus,” _Neuron_ 40, 1227–1239.
  <https://doi.org/10.1016/S0896-6273(03)00752-9>

These rat studies show prospective/path-related hippocampal phenomena in
different tasks, recording states, and analyses. They motivate the question but
do not establish cue-period shared-path coding in the current virtual-navigation
dataset.

### Metric implementation references

- SciPy Jaccard dissimilarity documentation:
  <https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.distance.jaccard.html>
- NetworkX shortest-path documentation:
  <https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.shortest_paths.generic.shortest_path_length.html>
- CEBRA API documentation:
  <https://cebra.ai/docs/api/sklearn/cebra.html>

These support definitions and implementation expectations, not neuroscientific
claims.

## Formal Dataflow

```mermaid
flowchart LR
    N[Measured cue spikes N_i] --> X[Declared cue representation X_i]
    B[Measured navigation samples] --> MAP[Graph mapping and cleaning Gamma]
    MAP --> P[Observed path P_i]
    P --> Y[Behavior-only target h(P_i)]
    X --> RAW[Raw/PCA/target-free representations]
    X --> SUP[Optional path-conditioned CEBRA]
    Y --> SUP
    C[Start goal and nuisances] --> BASE[Baseline f_0]
    RAW --> NEURAL[Neural model f_1]
    SUP --> NEURAL
    C --> NEURAL
    BASE --> EVAL[Common held-out loss and nulls]
    NEURAL --> EVAL
```

The path target is derived from behavior alone. Neural data never defines path
clusters, graph structure, or graph cleaning.
