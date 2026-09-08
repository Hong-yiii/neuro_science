# Autonomous endpoint benchmark: pre-fit study plan

2026-09-07, `baseline/start-goal-cebra`. User authorized autonomous hypothesis
formation, experiments, validation, and a final teaching HTML. **Exploratory
method diagnosis** only; not confirmatory H1, unknown-real-trial deployment,
mechanistic neuroscience, or a clean test leaderboard. This extends, not
replaces, the frozen baseline and its small decoder diagnosis.

## Question, evidence unit and boundaries

Why does this CEBRA setup generalize worse than PCA for inferred ordered
start/goal conditions, and which simple alternatives or changes help?

All methods see the same original-training-only source pool, 195 place-selected
units, 58 sessions, 30 ordered classes, ten complete 100 ms cue bins. The real
source trial/session constrains evidence; bins, artificial rows and seed
replicates are not independent biological observations. The existing inner
validation is **inspected development data**. Original validation/test features
are never read; no resplitting pretends to restore a pristine holdout.

Evaluation pseudotrials use the true condition to collect one source/session.
The decoder receives neural features only, but the benchmark is conditional
synthetic separability. No claims about trial-specific paths, intent, circuits,
simultaneous covariance, new sessions or new animals. Cue/goal and
previous-goal/current-start confounds remain. Selection is success-after-success
with the previously audited QC and current-cue exposure rules unchanged.

## Fixed protocol

- Reuse hash-verified source tensor, source split table and three observed
  pseudo arrays from `outputs/start-goal-cebra-20260907/`.
- Seeds 0, 1, 2. Default arrays: 480 training, 240 development pseudo rows.
  Save exact source membership and actual source use for altered assemblies.
- Fit scalers, PCA, networks, feature probes and decoders on training only.
  Never split existing pseudorows into train/validation folds.
- Primary representation readout: train-fitted StandardScaler + multinomial
  logistic regression C=0.01, max_iter=2000. This deliberate development choice
  follows the earlier decoder diagnosis, not an independent preregistration.
  Keep the old C=1 scores visible but compare new representations at the common
  C=0.01 readout. No adaptive per-model decoder tuning in the first screen.
- Primary metric joint balanced accuracy; also joint/start/goal accuracy,
  macro F1 and multiclass log loss where probabilities exist. SVM margins are
  not calibrated probabilities: report its accuracy but no probability score.
- Record training and development scores, explicit dimensions/input windows,
  compute time/steps, trainable parameters, loss curves, spectra, all attempts,
  failed checks, full configs, code/inputs hashes, package versions and device.
- All candidates reported. No pseudo-row confidence intervals or p-values.
  Seed ranges are assembly/optimization sensitivity. Source label permutations
  are diagnostics under an exchangeability assumption, not calibrated serial nulls.

## Questions and falsification

Q1: Is the pipeline technically functional? Reproduce old saved scores, test
constant-input chance and a known synthetic condition signal, enforce sampler
invariants and checkpoint reload parity. Do not interpret before these pass.

Q2: Is useful learning still happening? Read existing CEBRA checkpoints at
1/250/500/750/1000 with the fixed decoder; compare training, development, loss,
and effective rank. Fresh compute curves for legacy Behavior and time-matched
Behavior extend to 10000 steps with checkpoints 250/1000/3000/10000. No
validation-based early stopping. A declining loss without decoding gain argues
against simply needing more compute.

Q3: Does the sampling objective discard useful cue-phase distinctions? At fixed
architecture, temperature and steps, compare original same-pair positives,
same-pair/same-bin positives (global negatives), a bin-homogeneous-reference
batch/global-negative bridge control, and bin-homogeneous references with
same-bin negatives. **Pre-fit implementation check:** installed CEBRA computes
all-to-all reference/negative similarities, not paired negative similarities.
Matching each individual negative to its reference would be wrong. One cue bin
per matched batch ensures every denominator candidate has the correct bin;
the extra grouped-reference/global-negative control isolates batching from
negative conditioning. Preserve the possibility of same-label negatives as in
legacy InfoNCE; do not silently also change that rule.

Q4: Is temperature/capacity restrictive? Fresh fixed temperature 1/0.3/0.1
Behavior; time-matched version at 1/0.3; width32/128 and dimension8/16 versus
the same Behavior-temperature0.3 reference. Defaults: offset1 MLP, hidden32,
dimension8/bin, Adam lr0.001, batch256, 3000steps. One-change comparisons, not
Cartesian optimization. Learnable temperature is optional follow-up only if the
installed API is verified and fixed-temperature evidence warrants it.

Q5: Can the same encoder learn a useful classification representation? Train
an identical binwise offset1 encoder with a supervised whole-trial linear head,
CE loss, Adam lr0.001, batch128 pseudo rows, weight decay0.001, 3000steps.
Evaluate encoder with the common frozen readout and also record head predictions.
This is a capability control; CE receives a different loss granularity and
numbers of input bins/negatives per update, so equal steps are not equal compute.

Q6: Does whole-cue context help? Whole-cue PCA8 and whole-cue CEBRA-Behavior
(input1950, hidden32, latent8, temperature0.3), plus full-cue raw logistic/LDA/SVM.
These deliberately change input window, parameter count and final feature count;
show them separately from the 8-per-bin/80-feature controlled comparisons.

Q7: Where is information retained? Probe hidden and pre-/post-unit-normalization
features from final legacy Behavior and time-matched-temperature0.3 encoders;
use the same training-only decoder. Per-bin start/goal/joint probes and a
train-defined PCA control distinguish time profiles. Spectral concentration is
not proof of collapse; weights/attributions are model sensitivity, not circuits.

Q8: How do we compare with the student? Raw 100ms separate start/goal/joint LDA
(default SVD) and shrinkage LDA; combine separate-head probabilities over the 30
valid pairs as an explicitly modern factorized comparator (not the student's
heuristic collision repair). Also report full-cue analogues and a cross-temporal
goal matrix. Same sources/assemblies/splits; not exact 233-cell/10-fold replication.
Never compare one-bin student accuracy directly to whole-cue accuracy.

Q9: What actually scales? Fixed predeclared PCA8 + time-matched-temperature0.3
CEBRA comparator, three seeds, 3000steps: source fractions0.25/0.5/1, retaining
at least one source/session/class and reporting actual counts; nested unit
subsets50/100/195; synthetic training rows/class8/16/64. Keep development arrays
unchanged except intentional unit slicing. Do not alter unit panel with source
budget. Retained-minimum flooring means these are not exact data multipliers.
Synthetic-row sweeps hold biological availability fixed but may change how many
sources are actually sampled: distinguish eligible from used counts.

Q10: Is the result sensitive to temporal ordering? Audit strict chronological
session cut support without model-based selection. Also run an explicit
within-session/condition chronological split of the existing source pool with
unchanged per-condition train/development counts. This is a sensitivity analysis,
not a pristine holdout and not globally block-separated across conditions.
Use the same predeclared PCA/CEBRA comparison; report feasibility/missing support.

## Falsification panel and follow-up budget

- Five source-label permutations, independently within session and design split,
  reassembled before fitting. Three seeds each. Fixed panel: PCA8, binwise CE,
  time-matched-temperature0.3 CEBRA, 3000steps. Do not select the panel based on
  current-screen scores. No significance claims from five permutations.
- At most one documented follow-up round, motivated by screen evidence: up to
  four additional configurations × three seeds, plus explicit matched controls.
  Record the question/prediction before running; descriptive results only.
- Stop expanding when the simple alternatives are adequate and the main causes
  have informative contrasts, or a data/support limitation prevents identification.
  Never run to obtain a desired winner. Negative results are deliverables.

## Validation and report

Small synthetic tests cover label/bin sampler groups, trial boundaries, full-cue
shape, source subsampling and class presence, no source overlap, decoder target
mapping, constant chance, serialization, finite embeddings, and normalization
probes. Verify used input hashes and all final predictions/summary aggregates.
A fresh read-only reviewer checks implementation and another checks conclusions.

Final self-contained HTML: offline navigation, problem/data explanation, original
baseline, chronological research journal, every experiment family including
failures/negative results, model/scaling/probe plots, student comparison,
limitations, concrete recommendations, provenance and references. Embed figures
and avoid external runtime assets. Browser-check opening/navigation and print
layout with an existing local renderer when available; do not install or start
persistent services just to show a report. Outputs stay local/ignored; maintain
one Markdown index in docs. No other worktree or raw dataset is modified.
