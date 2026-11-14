# Source reuse, then population width — November 14, 2026

**Prospective exploratory protocol. Fresh construction and training authorized by
the owner; existing recordings only.** This replaces the broad coverage/model-knob
draft. [Design](design.json), [scratchpad](scratchpad.md), and the atomic
[experiment implementation](../../../experiments/source_reuse_width_20261114/)
are the working record. Freeze this protocol, code and design before biological fits.

## Questions and independent observations

1. On exactly the same recorded columns and ordered endpoint classes, does increasing
   the distinct training-source budget from 2 to 3 to 5 improve held-development
   decoding when assembled row count is fixed? How does repeated assembly compare
   with using the same three sources once?
2. At exactly three training sources/session × class, how does adding recorded
   population columns through nested session rosters affect learning and errors?

"Class" or informal "route" here means the ordered `(start, goal)` pair, not a
measured navigation path. The source unit is a recorded current trial with its
predecessor contributor, nested within session. Distinct source IDs are not a
guarantee of serial independence. Units, bins, recombined rows and computational
seeds are not new independent biological observations. The assay is conditional
on known-label assembly, with historically exposed development data.

## Fixed task and source gate

Use authenticated public compact cue-source v1 only. Reuse unchanged frozen outer
and inner assignments; restrict to outer train and apply the global development
current/predecessor embargo **before** any selection. The public metadata contains
15,553 inner rows, 5,872 protected contributors and 4,427 embargoed training rows.
Do not re-split or relax protection. Reconstruction authenticates event identities,
timing, native spike counts and masking; cue bins are ten half-open 100-ms intervals
in [0,1) seconds from cue onset.

Freeze one nine-class task, with every start and goal appearing once or twice:
`1→2, 1→4, 2→5, 2→6, 3→1, 4→6, 5→3, 5→4, 6→2`.
Nine is a compact fixed task with a feasible multisession minimum-five cohort.
It is not a Cartesian 3×3 endpoint rectangle. The examined width-optimal balanced
12/15-class solutions retain only one minimum-five session in the preliminary
metadata frontier and cannot themselves support this native multisession comparison.
This does not prove every panel of those sizes is multisession-infeasible. No class
count is a fitted knob.

An exact binary optimizer selects classes using metadata only: maximize recorded
width admitted by ≥5 training and ≥1 development sources/session × class; among
ties maximize width admitted by ≥3 training and ≥1 development; then choose the
lexicographically first class list. Both width objectives have certified zero gaps.
This uses exposed development **availability**, not neural outcomes. Retain solver
and direct-support receipts; no claim that this maximizes decoding accuracy.

The core has **17 columns/3 sessions**, 160 eligible training and 56 development
current sources. All 27 session–class pools support five training sources.
The same classes admit **83 columns/20 sessions** at minimum three, with 912
eligible training and 365 development current sources. Five core and 41 full-roster
development pools are singletons. Development reuse is explicit, not new sample size.

For width, retain the core and add whole-session blocks in descending exact harmonic
training-support order, ties by fixed session alias. Choose the interior prefix
closest to the midpoint of core/full recorded width, ties toward fewer additions.
This gives **17/49/83 columns and 3/11/20 sessions**. All units of admitted sessions
are retained. Width therefore changes session composition, total measured sources,
and native-model parameterization/pooling; this is a horizontal roster-expansion
test, not an isolated causal effect of feature count or evidence of bad sessions.

## Six unique arms; two experiment files

| Arm | Experiment | Columns/sessions | Distinct training sources per pool | Assembled rows/class | Uses/source |
| --- | --- | --- | --- | --- | --- |
| B2 | 1, reuse | 17/3 | 2 | 16 | 8 |
| B3 | 1 and shared bridge in 2 | 17/3 | 3 | 16 | 5 or 6 |
| B5 | 1, reuse | 17/3 | 5 | 16 | 3 or 4 |
| U3 | 1, once-only standard control | 17/3 | same three as B3 | 3 | 1 |
| Wmid | 2, width | 49/11 | 3 | 16 | 5 or 6 |
| Wfull | 2, width | 83/20 | 3 | 16 | 5 or 6 |

Primary arms have 144 assembled training rows and 72 development rows. U3 has 27
training rows, the same source identities as B3. Its change in constructed sample
count/combinations is part of that standard control. Train each unique case once;
the second notebook imports authenticated B3 evidence from the first, explicitly.

For each of three computational repeats (0/1/2), deterministically rank training
source identities separately within each session × effective class using SHA256
of the frozen seed, session, class and source ID. Take nested first 2/3/5 choices
on the core. Build the three-source training plan on the full admitted session
union then project to smaller rosters. Same-session columns always share a source
and all its bins. Balanced cycles cover every selected source; no full-pool arm
silently changes the intended source budget. Allocate extra repetitions by the
seeded balanced plan and record realized multiplicity, duplicate whole rows and
shared-block overlap. Extra-draw fractions for B2/B3/B5 are 87.5/81.25/68.75%.

Create one development plan per world on the full union, 8 rows/class with seed0,
then project. All observed repeats share exactly the same development arrays at
fixed roster. Shared columns across widths have exact matching source arrays and
targets. No newly added block is called the same natural trial. Fresh models use
paired computational seeds across arms; seed variation bundles source selection,
assembly and optimization and is not an estimate of biological uncertainty.

At fixed 16 rows, larger source budgets reduce repetition **and** broaden measured
responses and alter weighting/combinations. The primary test measures that combined
sampling-policy effect. U3/B3 holds source identities fixed and tests once-only
versus repeated assembly. Neither isolates serial dependence or optimizer exposure.

## Standard models, readouts and falsification

Reuse the maintained fitting/save/replay implementation without changing its
numerics. Four representations: training-scaled raw counts, PCA7, CEBRA-Time7 and
native discrete multisession CEBRA7. Every representation has logistic, RBF-SVM,
uniform Euclidean kNN5 and SVD-LDA readouts for pair, start and goal. These are
fixed comparators, not another model-selection sweep.

CEBRA-Time has 1,000 updates, batch256, hidden32, output7, learning rate0.0003,
fixed cosine temperature1 and within-row adjacent-bin positives. Native uses the
actual CEBRA multisession API, one encoder/session, joint-pair supervised positives,
1,000 updates and equal-session mean pooling of aligned coordinates. Per-session
batch is floor(256/S), at most256 total references/update; native uses one torch
thread. Native differs in supervision, architecture and pooling from Time, so
comparison concerns whole pipelines, not an isolated native-mode advantage.

Readouts use ten concatenated bin representations (70 latent features; 10U raw).
All scaling/PCA/encoder/readout learning uses training only. Logistic C=0.01×144/N
and SVM C=144/N keep N×C fixed at the common class task (U3 is the only smaller N).
SVM: RBF, gamma=scale, class_weight=balanced, no probability calibration or invented
log loss. U3 has three rows/pair, so uniform kNN5 pair probabilities are bounded by
3/5, a structural difference to remember when comparing its probability loss.
Other established settings stay fixed. No optimizer-length, dimension,
temperature, lag, phase or decoder-hyperparameter sweep. Preflight actual training
rank ≥7 for every scheduled case before fitting; failures stop with receipts.

Five source-label diagnostic worlds (61000…61004) cover all six arms at modelseed0.
Generate each whole-pair permutation once on the full admitted source union,
within session × split, before source-budget selection and assembly. Reuse the
same effective source-label map across arms. This preserves per-pool counts and
creates compatible train/development null tasks. Never shuffle synthetic rows as
if independent. These worlds test label alignment; they are not a calibrated
randomization test, biological p-values, or evidence about every nuisance variable.

Schedule: 6 arms ×3 observed repeats +6 arms ×5 diagnostic worlds = **48 unique
cases**. Actual instrumented fit budget: 48 each of PCA, Time and native, 576 each
of logistic/SVM/kNN/LDA = **2,448 fits**, excluding scalers, and **96,000 updates**.
Experiment1 fits32 cases; experiment2 fits16 new cases and reuses8 bridge cases.
No automated hyperparameter tuning or result-driven retries.

## Metrics, figures, error follow-up and claim limits

Primary metric is whole-cue pair balanced accuracy; report accuracy, macro-F1,
training BA and train–development gap, plus log loss only for probabilistic
decoders. Report start/goal heads separately and all seed-level scores. Uniform
references: pair1/9, start/goal1/6. A hypothetical perfect single-endpoint decoder
can attain pairBA6/9 under this panel; it is a mathematical task reference, not
a trained neural baseline. Do not infer start/goal independence from pair success.

Within each encoder/readout/head/repeat, contrast B3−B2, B5−B3, B5−B2, B3−U3 and
Wmid−B3, Wfull−Wmid, Wfull−B3. Display paired means and individual repeat ranges,
not row-IID confidence intervals. Compare observed scores and contrasts with all
five matched diagnostic worlds descriptively. Negative/flat results remain results.

Both notebooks/reports show source availability and actual use, widths, learning
curves, all observed class-mean cue trajectories in first3 fitted coordinates,
count and row-normalized confusions, per-class recall and paired prediction switches.
Save all predictions/margins/probabilities, all split confusions and every numeric
comparison, not just illustrated examples. Trajectories are unaligned latent
class means across cue bins, not maze paths or simultaneous neural dynamics.

After the primary tables, select best/worst **within each experiment and each
fixed encoder/readout** by mean observed pairBA across repeats; ties use arm order
in the frozen schedule. Reuse ranking excludes U3 from the primary 2/3/5 ranking
and reports U3 separately. Retain the full tables; these selected error views are
post-hoc descriptive illustrations, not new independent validation.

For #29, export retained/removed unit and session aliases, common-row right→wrong /
wrong→right switches, true/predicted endpoint confusions and source support/reuse.
Compact inputs have no authenticated spatial rate maps, occupancy or preferred
field locations. Mark field availability **unknown**, never zero selectivity.
This run can locate errors and lost recorded columns but cannot attribute them to
lost spatial coverage. Do not invent maps or add an unrelated private-data/map
study. The error handoff documents exact missing map/provenance/coordinate joins
needed for the later #29 step. The source-support constraint is related to #30's
constraint-based idea, but it does not implement #30's spatial-selectivity test.

## Execution, provenance and review

Use the existing read-only runtime. First run invented tests and a bounded invented
benchmark with 144×83×10 training, 72×83×10 development, 20 blocks and all configured
models/readouts. Conservatively require 48×benchmark-duration×1.25 +900 seconds
below the three-hour hard ceiling. Biological preflight is non-fitting and verifies
all48 plans, nesting, contributors, source budgets, rank and model prerequisites.

Run fresh kernels under hard 4GiB memory, zero swap, two-core CPU quota and three-hour
deadline. Preserve every attempt/failure; stop on integrity/rank/model/resource
failure, with no automatic biological retry. Record actual fit/update counts,
runtime/package versions, code/dirty-state snapshot, data hashes, full config,
lineage, fitted state and all outputs. Authenticated reloads of every new encoder
and readout must reproduce features/predictions on both splits with fitting blocked.

Require independent scientific/code review before fits and independent
numeric/results/privacy review before interpreting outputs. Keep generated neural
artifacts in ignored `outputs/source-reuse-width-20261114/`, source notebooks with
empty outputs in the experiment directory, and durable protocols/reports/scratchpad
in Git. Preserve old studies, runtimes, unrelated edits and failed receipts.
No push, merge, issue change or outside communication is requested.
