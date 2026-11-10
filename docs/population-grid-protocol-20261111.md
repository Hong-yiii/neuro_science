# Class requirements × session selection — prospective exploratory protocol

November11,2026. The owner corrected the intended3×3 design and explicitly asked
to pivot from the November10 experiment: vary retained classes and retained
sessions to obtain different pseudopopulation widths/support, then train models
to measure the effects of size and upsampling. Deliver a new report, executed
notebook and maximum-context `/teach` walkthrough. This is new exploratory
training on existing recordings. The previous endpoint-rectangle study is history,
not the design or result basis for this experiment. No publication/merge is implied.

## Operational question and independent units

How do metadata-selected endpoint class requirements and nested session rosters
change recorded feature width, available real current trials, and the capacity
for complete pseudorows without reuse? Within each resulting task/population,
how do synthetic recombination and additional distinct training sources change
whole-cue readout performance?

Current trials and predecessor contributors are provenance units nested within
sessions. Unit columns, synthetic rows, bins, seeds and optimizer updates are not
independent biological replicates. Session grouping is inherited and simultaneity
remains unverified. This is a condition-level, known-label-conditioned assay on
historically exposed development, not natural unknown-trial prediction.

## Inputs and selection, before neural scores

Use authenticated public `data/cue-source-v1/` only, with new task-owned outputs.
Preserve original outer-train membership, frozen inner assignments and the global
union of all5,872development current/predecessor contributors. Remove intersecting
training sources BEFORE selecting classes or sessions. Retain the native event,
quality, identity, mask and full-cue rules. No historical model/result replay.

The class-count axis is **30,20,15 ordered endpoint pairs**. Select each class list
from scratch using metadata, not the old nine-pair rectangle or old15/20lists.
Require every one of six starts and six goals to have degree floor(K/6) or ceil(K/6)
among the retained pairs; same-start/goal pairs are absent. This limits endpoint
imbalance. Pair-balanced assembly does not make secondary heads exactly balanced
when K is not divisible by six.

For each K, an exact mixed-integer program chooses the pair list maximizing
eligible recorded columns under >=2training and >=1development current sources
per session×pair. Among width ties maximize total eligible training current sources,
then resolve class-list ties lexicographically. The generated design records solver
status, objective and class list. Require optimal status/zero gap; a timeout is not
an optimum. Selection sees exposed development availability, so it is exploratory.
The broad metadata plot also reports maximal width for class counts6…30 under the
same endpoint-balance/support constraints; those other class counts are not fitted.

Freeze each selected class list across its three session rosters. Rank eligible
sessions by decreasing harmonic mean of per-class training source counts, computed with exact
rational arithmetic for ties, then
decreasing recorded columns, decreasing training-source total, then session ID.
Retain the top **ceil(S/3), ceil(2S/3), and S sessions**. These are nested rosters,
not three different support thresholds. Require nine distinct configurations and
at least eight recorded columns in each; training-only numerical PCA rank must
also support seven components in all24class/world/seed bundles before the first fit. Do not silently pad or change dimensions.

Report every prefix of each ranked roster: sessions, columns, distinct training
and development current sources, training pool minimum/quantiles/harmonic mean,
development singleton pools, balanced no-reuse row capacity K×min(n_train), and
class-wise no-reuse capacity sum_c min_session(n_train). The last capacity permits
unequal class row counts and is a descriptive availability measure, not the
balanced training quota below. Larger total source counts are not automatically
larger per-condition support or more independent complete rows.

## Three sampling policies within each of nine configurations

All policies preserve whole session×trial blocks and all ten cue bins.

| Policy | Source pool | Training rows per pair | Meaning |
| --- | --- | ---: | --- |
| U2 | Exactly two selected sources/session×pair | 2 | Each selected current source used once in training assembly |
| R16 | Exactly the SAME sources as U2 | 16 | Eight uses/source, with balanced recombination |
| F16 | All eligible sources/session×pair | 16 | Balanced allocation across the full real pool |

The maximum eligible training pool in these public metadata is12, so F16 can
include every eligible training source. Assert actual coverage; do not rely on
the policy name. Balanced counts differ by at most one within each pool, including
eligible zeros. U2 removes repeated current-source blocks during assembly, not
optimizer/bin exposure or serial/predecessor dependence.

For each class list, seed and label world, construct the largest roster's plans
first and project them to smaller rosters. U2's two-source subset is selected
before row assembly using seed20261111+computational_seed over sorted conditions,
blocks and source IDs. R16 uses exactly that subset with allocation seed700000+seed;
F16 uses all pools with allocation seed seed. U2 uses allocation seed seed.
Projection must preserve exact common-block arrays/targets and rebind input identity.

Development has eight rows/pair, fixed at seed0 within each class/label world,
drawn in the largest roster and projected to all smaller rosters/policies. The
development source pool is unchanged by U2/R16 restrictions. Verify exact equality
across policies and exact slice equality across rosters before fitting.

Observed computational seeds0,1,2 cover all9×3configurations: **81observed cases**.
Primary sampling contrasts are **R16−U2** (recombination, same measurements) and
**F16−R16** (more distinct sources at the same row quota, also changing empirical weighting
and joint combinations; not a pure count-only intervention). Main population contrasts
are two-thirds−one-third and all−one-third, within K/policy/seed. Adding sessions
changes both recorded columns and source composition; it is not an isolated
single-neuron causal effect. Across K, tasks differ; report separate chance
references and do not rank a pooled best accuracy as representation superiority.

## Models, controls and metrics — amended before biological fitting

The owner subsequently requested additional CEBRA decoders, specifically SVM, and
native multisession CEBRA. This amendment replaces the earlier logistic-focused
model matrix; no biological model had been fitted. The first invented benchmark
passed but does not authorize this expanded matrix. The rank-eight native-input
preflight stopped on K30/S33/U2 in permutation60002; zero model fits. A complete
216-plan training-only float32 rank inventory found minimum7. Freeze **seven**
latent coordinates for all representations/cases, the largest common feasible
rank across this preflight. Do not pad, alter the nine rosters, or select dimensions
from decoder scores. Preserve both the failed preflight and rank inventory.

Reconstruct cue[0,1)s as ten100-ms count bins. Each case freshly fits four feature
pipelines: raw training-scaled counts, PCA7, CEBRA-Time7, and native discrete
multisession CEBRA7. All learned preprocessing uses training only. Raw whole-cue
features have10Ucolumns; all latent whole-cue features have70columns.

Time uses the existing pointwise offset1 MLP U→32→32→16→7, cosine temperature1,
Adam0.0003, batch256,1000updates and CPU/two numerical threads. Positive pairs are
forward-adjacent bins in the same assembled row; labels do not choose positives.

Native uses the installed CEBRA0.6.1 **CEBRA.fit(list_of_session_arrays,
list_of_discrete_pair_labels)** API, DiscreteMultiSessionDataLoader,
DiscreteMultisessionSampler and MultiSessionSolver. Each array contains only that
session's own units, from the same training plan's row/bin blocks. One pointwise
encoder/session maps its input to7coordinates. Pair labels are repeated over bins,
with positives matched by joint pair in randomly assigned sessions. This is
**pair-supervised**, has no cue-time matching, and is not CEBRA-Time. Native
transforms require session index and neural values only; no development labels
are passed. Average the aligned per-session coordinates with equal session weight
at each assembled row/bin, producing7coordinates/bin without learned pooling.
The mean is a predeclared consensus representation; it can discard session-specific
information and does not reconstruct simultaneous covariance.

Native batch size is **max(2,floor(256/S)) per session**, hence at most256reference
vectors/update for this grid. Use1000updates, hidden32, Adam0.0003, cosine temp1,
CPU/one torch thread (two-core outer ceiling). Seed NumPy and torch with3011+case seed, restore their caller state,
and record actual references/update, session encoder count and input widths.
Hide CUDA before imports in the runner/kernel because the installed multisession
sampler has a module-global auto-selected device; assert its device is CPU.
U2 and R16 have the same per-session empirical point/label distribution: R16
repeats every point eight times. Native training never consumes cross-session row
combinations, so it gains no new encoder information from R16. Differences can
arise from stochastic sampling/index order and the recombined downstream readout
rows. Native versus Time changes supervision, parameterization, pooling and exposure;
compare complete pipelines, not an isolated multisession effect. A matched
concatenated pair-supervised encoder is not included in this bounded study.

Every representation gets **four decoders × three targets** (pair/start/goal):

| Decoder | Frozen training-only recipe | Probability loss |
| --- | --- | --- |
| Logistic | Feature StandardScaler; lbfgs; C=.01×16K/N; max_iter2000 | Yes |
| RBF-SVM | Feature StandardScaler; SVC; C=1×16K/N; gamma=scale; class_weight=balanced; tol.001; max_iter100000; cache200MiB; probability=False | Absent; save margins |
| kNN | Feature StandardScaler; k5; uniform votes; Euclidean; brute; n_jobs2 | Yes; zero vote probabilities retained with standard metric clipping |
| LDA | Feature StandardScaler; SVD-LDA | Yes |

The SVM recipe follows the codebase's prior scaled RBF readout, with N×C held fixed
within K across row quotas. No internal SVM probability calibration/CV is allowed:
synthetic row folds would not respect source dependence. A margin is not a probability. With U2 only two pair rows
exist, so kNN5 can assign at most2/5vote probability to a given pair class; its
probability loss has this structural row-count dependence.
Logistic C=.08(U2),.01(R16/F16); SVM C=8(U2),1(R16/F16). kNN can change merely because
training rows repeat; the matched sampling contrasts deliberately expose that.
No hyperparameter tuning, automatic fit retries, post-result panel choice or
performance-selected decoder. Fail on convergence/nonfinite errors and retain evidence.

Observed cases remain81. Five joint-pair permutations60000…60004 operate within
session×split BEFORE two-source selection/assembly. They cover U2/F16 at full
roster, each K, modelseed0:30diagnostic cases, including both CEBRA pipelines and
all decoders. Each world has compatible fixed development truth/assembly. Smaller
roster/R16 nulls are not fitted. Five worlds are diagnostics, not biological p-values.

Exactly **111cases**:111TimeCEBRA,111nativeCEBRA ensemble fits,111PCA,
1332each logistic/SVM/kNN/LDA = **5661fit calls excluding scalers**,222,000Adamupdates.
Native internal session encoders total2174 (1404observed +770null), counted separately. There are5328metric and
confusion records,222optimization curves,444saved encoder objects,
5328readout objects and10,656composed train/development replay checks. Count actual
calls/updates, not only configured expectations.

Primary outcomes: pair balanced accuracy, plus log loss where probabilities exist.
Report accuracy, macro-F1, train/development gaps, endpoint scores, all seed values,
confusions, curves and observed trajectories. Uniform BA references are1/K and1/6;
uniform probability losses ln(K),ln(6). Perfect-goal/no-start expected pairBA6/K
is a mathematical reference, not a fitted baseline or significance threshold.
SVM comparisons use discrimination metrics; probability-loss panels omit SVM.

Native API references: [official usage](https://cebra.ai/docs/usage.html),
[native multisession example](https://cebra.ai/docs/demo_notebooks/Demo_hippocampus_multisession.html).
Installed implementation, not changing online defaults, determines this run.

## Evidence, resource bounds and review

Retain new source lineage, model states, numeric features/predictions, complete
configuration, source hashes/dirty state/snapshot, imported dependency versions,
attempt/failure logs, exclusions, actual source reuse and shared-block/duplicate
row counts. Source/error involvement is associative, not causal attribution.
Display aggregate/aliased outputs only. Save complete numeric results, every
observed trajectory and every confusion matrix; choose clear report layouts
without pooling computational seeds into biological sample sizes.

Reload each newly saved pipeline under a fitting/update guard and reconcile
features, predictions and probabilities on both splits. Require independent
protocol/code review before fitting and independent scientific/results/privacy
review before final interpretation. Tests on invented inputs verify software,
not biological validity. Preserve all original and prior-run artifacts.

Use existing runtimes read-only. First run an invented full-size benchmark with
480×144×10training and240×144×10development,1000updates per CEBRA branch. Then a single
fresh-kernel biological execution under hard4GiB memory, zero swap, two-core quota
and360-minute timeout. The expanded invented benchmark includes all four feature pipelines and48readouts.
Benchmark conservatively estimates111cases plus rendering
headroom; refuse a launch exceeding that bound. Stop on OOM, integrity failure,
rank/fit failure or timeout; retain failure evidence. No automatic expanded sweep.

The first expanded invented benchmark completed every model/readout but failed
the conservative three-hour total-grid headroom gate (129.74s/case,109.23s native).
Before biological fits, reduce native torch parallelism from two to one thread
for its many small networks and rebenchmark; retain the failed budget receipt.
This engineering change uses invented data only. Benchmark03 also completed
every fit/replay but failed the original three-hour headroom gate:121.39s/case,
101.85s native,829.81MiB peak, zero OOM. Do not relabel either receipt as passed.
A resource-only amendment accepts a **six-hour hard ceiling**, retaining the full
111-case matrix and all1000updates per branch:111×126.0305×1.25+1200 ≈18,687s (full benchmark elapsed),
below21,600s. A new authenticated resource-gate receipt references the completed
invented case and unchanged numerical code hashes; no extra invented training
is needed just to change a time-limit comparison. Independent review authenticated all66benchmark receipt files, all case artifacts
and unchanged numerical code, and accepted the resource-only amendment before
biological launch. The model/decoder matrix and update counts are unchanged.

The source notebook will execute the new design, input construction and model grid.
The final report and saved notebook will collate that run's evidence. `/teach max`
will explain the new study from its actual code/results in one disposable HTML,
without adding another fit or altering accepted results.
