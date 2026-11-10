# Smaller endpoint panels and source reuse — frozen exploratory protocol

Prepared November 10, 2026, before new biological fitting. The owner explicitly
requested execution, fresh model training, smaller start–goal class panels, tests
of a larger population and reduced reuse, and a final report with trajectories
and an executed notebook. This supersedes the preceding assessment's planning-only
status for this bounded cue-only study. No publication, merge or unrelated study
is implied.

## Question and interpretation

Can endpoint information be recovered from the existing cue recordings when the
class set is reduced, additional recorded columns are included, source draws are
balanced, or each current source occurs only once in the assembled training set?
Separate added-unit information, finite-pool sampling sensitivity and synthetic
recombination. These are new fitted-model results from existing recordings, not
new biological measurements or confirmation on an unexposed population.

Provenance units are current trials and predecessor contributors, nested within
sessions. Observations supplied to models are known-condition synthetic rows.
Neither rows, bins, optimizer steps, computational seeds nor recorded columns are
independent biological replicates. The assay cannot validate simultaneous
covariance/dynamics, natural unknown-label population prediction or intention.

## Fixed metadata decision and inputs

Use only authenticated public `data/cue-source-v1/` and new task-owned outputs.
Retain all historical eligibility rules, original outer-train membership, frozen
inner assignments and the union of all **5,872 original development contributors**.
Remove intersecting training contributors before ANY class/session restriction.
No source can be reclaimed because its class was dropped. Development is exposed.
Reconstruct selected sources from native-precision spikes and Ripple cue windows:
ten nonoverlapping 100-ms bins over `[0,1)` seconds. Retain masks, zero counts,
predecessor identity and native boundary conservation checks. Do not read historical
private inputs, models or predictions. Reconcile native metadata through the existing
compact adapter and fail on selected missing Eye events or incompatible metadata.

Evaluate all 20 disjoint choices of three starts and three complementary goals
using metadata only. Same-start/goal pairs are absent, so disjoint sets are necessary
for nine valid pairs. Choose maximum unit columns, then sessions, then lexicographic
starts, independently of neural activity or performance. The chosen panel is:

**Starts 2,3,5 × goals 1,4,6.** At minimum two training and one development source
per session × condition: 144 units/43 sessions, 1,796 training/722 development
sources. At minimum three: 80 units/20 sessions, 863/342 sources. The same rectangle
maximizes width at both thresholds. All 20 rectangles have zero sessions at minimum
five. Report the entire availability table; do not search neural scores for another
rectangle. Metadata use of exposed development availability limits future-selection
claims. The observed panel choice is explicitly exploratory.

The original reference has all 30 pairs, 27 units/10 sessions, 1,415/551 sources.
Its sessions are contained in the wide nine-class panel. Session grouping retains
the previous unverified simultaneity status; “unit” means a selected recording column.

## Eight observed arms

Each uses model/assembly seeds 0,1,2. Ordered pairs are the primary target; start and
goal are secondary readouts. All trials retain their ten bins and intact session
blocks. No tuning, alternative rectangle search or post-result exclusions.

| Arm | Classes / columns / sessions | Training construction |
| --- | --- | --- |
| A | 30 / 27 / 10 | Historical sampling policy: 16 rows/class with replacement; fresh native inputs/fits |
| B | 9 / 27 / 10 | Project C's exact training plan onto the reference columns |
| C | 9 / 144 / 43 | 16 rows/class with replacement from all eligible pools, minimum two |
| D | 9 / 43 / 43 | Project C onto one metadata-selected column per session (lexicographically first unit ID) |
| E | 9 / 80 / 20 | Project C onto the minimum-three panel |
| F | 9 / 80 / 20 | 16 rows/class, balanced allocation of all eligible sources in each pool |
| G | 9 / 80 / 20 | Select three distinct sources/pool; three rows/class, each source used once |
| H | 9 / 80 / 20 | The SAME three sources/pool as G; 15 recombined rows/class, each source used five times |

Balanced allocation permutes a pool, cycles it to the requested length, then shuffles
that block's assigned row positions. Per-pool use counts differ by at most one,
including eligible zero-use sources. G's subset seed is `20261110 + computational
seed`; selection is by condition then block over sorted source IDs, without replacement.
H reuses that exact subset, with allocation seed `700000 + computational seed`.
G removes repeated current-source blocks in assembled training rows, not repeated
optimizer exposure, temporal bins or serial/predecessor dependence.

For B–H, freeze eight development rows/class at seed 0 in the widest panel, then
project onto the corresponding blocks/columns. B/C/D/E share the same widest
training plan at each seed as well. Rebind projected plan identities, filter source
positions in block order, rematerialize, and assert exact tensor/target equality to
the corresponding widest-array slices. Source-budget restrictions leave development
bytes/lineage unchanged. A uses its own fixed 30-class development assembly.

Primary paired contrasts, within representation and computational seed:

- **C − D:** additional selected unit columns within the same 43 sessions, exact
  source plans and task. One fixed unit selection gives a conditional result.
- **F − E:** balanced allocation versus finite uniform draws, same eligible pools,
  row quota and task. Joint block combinations also change; not pure causal weighting.
- **H − G:** recombination/assembly multiplicity on identical three-source pools.
  No additional neural measurements are introduced.

A/B and C/E are descriptive practical panel comparisons. They change task/classes
or session/source support and cannot identify a causal class-count/support effect.
Chance-corrected scores do not remove differing task difficulty. Report all arms.

## Models, decoders and controls

Training-only pooled-bin scaling; raw flattened counts, full-SVD PCA8 and cue-only
CEBRA-Time offset1 (hidden32, output8, fixed cosine temperature1, Adam learning
rate0.0003, batch256, 1,000 updates, CPU). Preserve the maintained row-uniform,
within-row adjacent-bin Time sampler. Every arm refits all learned transformations.
No padding when PCA rank is insufficient; record and stop on failure.

Fit separately scaled logistic readouts for pair/start/goal. To keep summed-loss
regularization comparable when rows change, use
`C_eff = 0.01 * (16 * number_of_pair_classes) / training_rows`.
Thus ordinary/balanced arms use0.01, G uses0.053333…, H uses0.010666….
Within the nine-class task `N_train*C_eff=1.44`. Fix max_iter2000 and solverlbfgs;
record nonconvergence instead of silently retrying. Raw SVD-LDA is a fourth
descriptive reference; retain poor probability calibration and rank failures.

Run five alignment-breaking source-label worlds, seeds **50000–50004**, for A, E
and G at computational seed0. Permute joint pair labels within session × split
BEFORE subset selection and assembly; derive start/goal jointly. Each null world
has its own fixed compatible development assembly. Never reuse observed rows with
incompatible shuffled truth or tune to these controls. Five worlds are a descriptive
diagnostic, not an exchangeable biological null distribution, p-value or family-wise
test. Compare their full score range with observed scores; preserve every result.

Exactly **39 model cases: 24 observed +15 permuted**. Expected fits excluding scalers:
39 CEBRA,39 PCA,351 logistic,117 LDA;39,000 optimizer updates. FitAccounting instruments
actual fit/solver/update calls, not just expected loops. Separately label all invented
benchmark fits. No retries or expanded grid based on results.

## Outputs, checks and resource envelope

Report accuracy, balanced accuracy, macro-F1, natural-log loss, training/development
gaps, count/normalized confusions and all seed values. Uniform references are1/30,
1/6,1/9,1/3 as applicable, not significance cutoffs. Primary metrics are pair9
balanced accuracy and log loss. Seed ranges describe computation, not biological CIs.

Export support/exclusion maps for all58sessions, source usage including zeros,
unit-to-session inheritance, shared-block overlap and exact duplicate rows. Join
newly computed errors to explicit full case/world/seed/assembly identity plus row ID.
Reconcile correct+wrong appearances with use totals and confusions with metrics.
Source participation in errors is an association, not that trial's or session's
causal error. Excluded sessions have no prediction score from the excluded panel.

For every observed seed and arm show class-mean cue-time paths through the first
three native PCA/CEBRA coordinates, with bin-center milliseconds and fixed class
colors. No projection/alignment is fitted for display; axes are not comparable
between independently fitted models. These are trajectories of constructed cue
representations, not measured maze paths or simultaneous neural dynamics. Display
all cases, not a selected attractive embedding. Include every CEBRA learning curve.

Save new model states, numeric arrays, explicit row/source lineage and authenticated
manifests privately under a fresh `outputs/source-support-20261110/` attempt directory.
Reload every newly saved encoder and readout under a fit/update guard; compare
features, probabilities and predictions to pre-save values. Preserve failures. The
executed notebook and offline report display aggregates/aliases only, with machine-
readable tables, code/input/configuration hashes and clear limitations.

Use the existing notebook runtime plus existing scientific dependencies read-only.
No runtime installation/upgrade. Sequential CPU work, two numerical threads, hard
4GiB memory cap, zero cgroup swap, CPU quota200%, 90-minute execution cap; stop on
integrity failure, OOM, timeout or fit failure. Benchmark invented data at an equal
or larger shape and full1,000updates before the biological launch. Record actual
cgroup limits/peak/events, disk usage, package versions and source dirty state.

## Independent review

Protocol reviewer `protocol_review` independently reproduced the metadata counts,
nesting and minimum-five infeasibility. The reviewed design incorporated explicit
sampling policies/invariants, projected-plan equality, fixed permutation seeds,
normalized logistic regularization and bounded claim language. Scientific design
accepted as exploratory, subject to implementation tests, independent code review,
resource benchmark and final independent results review. These gates implement the
owner's execution request; they do not require another permission round.
