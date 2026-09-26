# CEBRA broader-training → cue-only decoding: exploratory protocol

Prepared 2026-09-24, before biological fitting. User explicitly authorized a new
worktree, an autoresearch-style trial, and a PR. This is a bounded **exploratory
analysis**, not confirmation, an unlimited search, or a restart of prior studies.

## Question and fixed observation unit

Does adding navigation-period neural observations from **training sources only**
to CEBRA training improve a decoder trained/evaluated on **cue-only** embeddings?
Primary effect: mean paired balanced log-loss(cue-Time) minus log-loss(full-Time)
over the three computational seeds. Positive favors broader encoder training.
Behavior-conditioned comparison is secondary. This tests a specified sampling
intervention, not CEBRA universally or a simultaneous neural population.

Retain the old 4→3 interior `D_N_R_T__N_R_M` benchmark: 29 selected units, seven
session blocks, 82 training and 22 historically exposed validation source trials.
The accepted source tensor is
`outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/v7-v8-neural-experiments/primary29_min3train_min1val/bin100ms/source_level_cue_tensors.npz`,
SHA256 `688e3b52f69a872c7aec420da99ebb6f0b80464351ded3813b077cd7ed3cf567`.
Use absolute inputs under the canonical `~/neuro_science`; no copied private data
or dependency on its uncommitted new scripts. New worktree starts at origin/main
`834063184085b8ff9eaa19264728a1bf79969d70`.

Real source trials nested within sessions, not bins/pseudorows/seeds, are the
independent source objects. Current label-conditioned assembly is a conditional
benchmark requiring known labels, not unknown-natural-trial prediction. Shared
session grouping is not proof of simultaneity. The original split/target/cohort
are frozen and already exposed; eligibility was historically support-selected.

## Data and leakage gate

Use the accepted source NPZ as the exact source/cell/split/label whitelist; verify
against the original split manifest and behavior-only membership. Refuse test,
unknown, duplicate or changed sources. Preserve the original endpoint and target,
QC-empty/successful inclusion; stop rather than silently drop cohort members.

Reuse `read_ripple_trials` and `read_spiketrain` from the existing importer:
Ripple timestamps are seconds; sorted spikes are milliseconds converted to
seconds. Verify raw-file hashes against the imported source-file manifest and
source trial indices/marker codes/boundaries against the imported development
rows. Raw session MAT files necessarily contain session-wide data in memory;
only whitelisted training source navigation intervals may be selected/binned.
**No validation navigation arrays, counts, model inputs or test-trial features.**
Validation cue arrays come solely from the accepted NPZ. Do not rederive paths,
fetch lab data or expand the unit panel. Record what files were opened versus
what source windows were analyzed; do not falsely claim no session-wide raw read.

Recount training cue windows against saved cue bins as a numerical provenance
gate (clip at actual cue offset, including the known slightly subsecond cue).
Require exact count parity. Retain original ten-bin cue counts and exposures for
both arms; no smoothing or future receptive field. Missing/unrecorded cells are
masked in source storage and never replaced by zero in population rows.

Navigation bins: half-open native `[cue_offset + .1*k, cue_offset + .1*(k+1))`
intervals entirely before navigation end. Discard and audit only the final
partial <100-ms navigation remainder. The original first-second cue window is
retained; the small cue tail beyond one second is not added. Thus `full` is a
short arm label for **cue plus full-span complete navigation bins**, not a claim
that every millisecond of the trial is used. All accepted sources must have at
least two complete navigation bins; otherwise stop before fitting.

## Pseudopopulation and time semantics

Use the existing 64 rows/class source-block assembly, seeds 0,1,2, preserving
all units and bins from the chosen source within each session block. Historical
validation is the exact 30 class-conditioned combinations (24 absent, six
present), half the total evaluation mass/class. Retain class-qualified row IDs
and every source choice. Sources are disjoint across train/validation.

For navigation, variable duration must not be padded, interpolated into spike
counts, or interpreted as matched physical positions. For each training
pseudorow, build a deterministic normalized-duration **pair-bank**. Let L be the
largest (number of complete native navigation bins minus one) among its seven
source blocks. At q=(j+.5)/L, j=0..L-1, each block selects native anchor
floor(q*(n_bins-1)) and its own immediate next native100-ms bin. Stack those
blocks into anchor and positive vectors. Every native adjacent pair of every
chosen block is represented at least once; shorter sequences repeat bins.
Save the native indices and source IDs so this property is checked, not assumed.

This is phase-progress-matched synthetic sampling, **not physical path alignment,
real cross-session dynamics or a uniformly spaced full pseudotrajectory**. Do
not link consecutive pair-bank rows as Time positives. Within each pair, all
blocks advance exactly one native100-ms bin in their own intact source. Cue
positives are the original adjacent cue bins. Never pair across cue/navigation
or source boundaries. Navigation negative/Behavior candidate banks contain both
members of the native pair bank, with their known path-component label. Pair-bank
multiplicity and phase probabilities are part of the declared intervention.

## Frozen model family and budget

Four encoder arms: `cue_time`, `full_time`, `cue_behavior`, `full_behavior`.
Use offset1 encoder, 29 inputs, hidden32, output8, cosine InfoNCE temperature1,
Adam lr3e-4, batch256, exactly1000 updates. Shared cue-trained StandardScaler
within an assembly/world; no scaler fit on validation or navigation, isolating
encoder sampling rather than scaling. Optimizer and assembly paired seeds0,1,2
are computational sensitivity, not biological replicates. Preserve common model
initialization for each paired full/cue comparison.

Cue arms use cue samples only. Full arms sample cue/navigation phases with
probability .5/.5 for anchors and independent background negatives; within a
phase sample pseudorows uniformly, then eligible bins/pairs uniformly. Time
positives are the designated native next bin. Behavior positives sample the same
binary path class, independently selecting phase by the same .5/.5 rule; no
same-bin/phase constraint, no path coordinates at inference. Record realized
phase/label/source/bin exposure and contrastive loss, without early stopping.

Freeze encoders, transform **only the ten cue bins** for all decoder fits and
validation. Concatenate 10×8=80 features. Two fixed decoders, no tuning:
- Primary: train-only StandardScaler + logistic C=.01, liblinear,
  balanced class weights, max_iter1000, random_state0.
- Secondary: train-only StandardScaler + RBF SVC C1, gamma=scale,
  balanced weights, probability=False, max_iter100000, random_state0.
Matched raw290 and PCA8/bin→80 controls use the exact same cue assemblies;
PCA uses one pooled training-bin StandardScaler/full-SVD basis, no whitening.
No predictor may receive labels or post-cue neural data as input at evaluation.

Observed budget: four arms × three seeds =12 CEBRA fits. Twenty null worlds
repeat all four arms/all three seeds =240 fits. Total **252 encoders**,
**63 PCA transforms**, **756 decoder fits** (6 representations ×3 seeds ×21
worlds ×2 readouts). Synthetic tests are separate. No new dimensions, checkpoints,
thresholds, label flipping, model families or hyperparameter search after results.
Stop on convergence/nonfinite/integrity failure; preserve incomplete attempts.
Hard fitting cap90min and outputs10GiB, two CPU threads, existing RTX2070 when
available. Measure synthetic runtime before launch; revise budget openly BEFORE
any biological fit if the cap is implausible. No installs, daemons or services.

## Evaluation, nulls and source sensitivity

Primary paired log-loss effect uses Time/logistic and mean over the same three
seeds. Report both objectives, both readouts and controls completely; balanced
logloss/Brier (logloss clipping1e-9), BA, AUROC, class recalls, training gaps,
constant.5 reference (loss log2, BA.5), per-seed paired effects. SVM margins are
not probabilities; no SVM logloss. No validation-selected winner.

Twenty source-label-shuffle worlds, seeds50000..50019, within session×split
(endpoint fixed), before both phases' assembly. Preserve one coherent source
label for cue/navigation, recompute scaler/PCA/CEBRA/readouts and exact evaluation
assembly for each world. Paired arms share maps and draws. Record actual label
movement and invariant strata. Compare observed **three-seed mean** Time/logistic
paired gain to the same statistic in every world using inclusive plus-one tails
and1e-12 tolerance; also give max-over-two-objectives paired-gain and absolute
full-arm above-chance references. These are limited-resolution **no-association
references**, not general equal-risk/superiority tests or correction for the
project's adaptive history; serial exchangeability remains unresolved.

For observed predictions only, 200 seed20260924 source-stratified validation
resamples (session×class), shared across methods; source multiplicities multiply
through exact combinations, then balance class mass. Also delete each of22
validation sources, renormalizing surviving classes. Mark singleton/one-class
cases inestimable. Models fixed: report paired gain and BA sensitivity, not
animal/selection-adjusted confidence intervals. No resampling pseudorows as if
independent. No new nuisance model; unresolved cue/history/view/task/recording
metadata and source-selection bias remain explicit limitations.

A worthwhile *exploratory follow-up lead* for primary Time/logistic requires
mean loss gain≥.01 nats, full loss<log2, full BA>.5 and AUROC>.5. Report criterion
components, null/source context and all seeds even if none pass. This is an
engineering prioritization rule, not a biological effect-size/significance claim.
Negative/mixed outcomes are complete deliverables; never expand to rescue them.

## Gates, evidence, delivery and lifecycle

Before fitting: audited count/identity/split/coverage parity, invented-data
positive/no-signal checks, sampler boundaries/phase semantics, leakage poison
checks, deterministic paired initialization, save/reload and tiny forward-replay
checks. Independent read-only scientific and code review; fix and hash-bind
approval to executed code/config. A mutable working copy is not run provenance.

Save source/raw hashes, complete configuration, code revision+dirty state,
versions/device/seeds, all started/completed/failed fits, raw/PCA/neural scalers,
encoder/decoder states, cue embeddings, predictions, source/native-bin lineage,
exposure, all metrics and null/sensitivity results. Use fresh output directories
under canonical `outputs/cebra-full-trial-transfer-20260924/` so worktree removal
cannot strand evidence. No raw/model artifacts in Git.

Postfit verification: no-fit forward replay of every encoder/decoder, recompute
metrics, paired summaries/nulls/source sensitivities, and reject hash/lineage/
prediction corruption. Independent result/claim review before interpretation.
Deliver code/tests, frozen protocol, human report with figures/offline HTML,
compact machine/review/verification receipts and a PR (do not merge).

Worktree `~/neuro_science/work/cebra-full-trial-transfer`, branch
`feat/cebra-full-trial-transfer`, is explicitly requested and retained through PR
review. No automatic removal: after approved merge verify canonical artifact
hashes and worktree cleanliness, then remove only this worktree deliberately.
Do not touch the separate issue6 worktree or canonical uncommitted work. No
persistent service introduced. AI QA cannot verify missing laboratory metadata.
