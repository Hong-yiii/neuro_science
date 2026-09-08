# Endpoint autoresearch journal

Companion to [the pre-fit plan](start-goal-autoresearch-plan.md). Dates are UTC
unless explicitly stated. This is the **research trajectory**, not the
navigation path prediction target. All results after the original baseline are
adaptive exploratory development diagnostics.

## 2026-09-07 — Starting question

User: is CEBRA itself the problem; should other models be tried? Authorized
independent question formation, experiments, validation and a teaching HTML.
Starting observation: frozen baseline PCA8/bin 82.50%, Time 42.78%, Behavior
18.61% joint accuracy. Stronger decoder regularization helped CEBRA but did not
close the gap. Do not confuse decoder training accuracy with the contrastive
encoder objective or concentrated variance with complete representational collapse.

## Before new real-data fits — independent challenge

Three read-only agents examined mechanisms/literature, methodological design and
local APIs. They agreed on source-trial splits, complete session blocks, label-
conditioned evaluation and inspected-development limitations. Proposed chronology
and support checks were added. No fresh confirmatory evaluation was invented.

Primary sources motivating tests:

- [CEBRA Nature paper](https://www.nature.com/articles/s41586-023-06031-6):
  learned embeddings depend on contrastive sampling and auxiliary variables.
- [CEBRA usage](https://cebra.ai/docs/usage.html) and
  [API](https://cebra.ai/docs/api/sklearn/cebra.html): discrete/continuous
  supervision and temperature controls.
- [Discrete sampling source](https://github.com/AdaptiveMotorControlLab/CEBRA/blob/main/cebra/distributions/discrete.py):
  matching a categorical label alone does not also match cue time. Installed
  0.6.1 source, rather than moving upstream main, defines executed semantics.
- [LFADS](https://www.nature.com/articles/s41592-018-0109-9): latent single-trial
  population dynamics require an observation design absent from this assembled
  cross-session dataset. GPFA/LFADS are not default replacements here.
- [Student notebook](https://github.com/josephchengyx/Hippocampus_Decoding/blob/2f12016c58472888b83298d163be1daaf5291a1e/neurosci_2023_pseudopop.ipynb):
  source-safe matched LDA is an adaptation, not exact historical reproduction.

## Before fitting — a consequential sampler implementation check

CEBRA 0.6.1 `models/criterions.py:dot_similarity` uses
`einsum("ni,mi->nm", ref, neg)`: every reference contrasts with every sampled
negative. Merely matching each negative's bin to its paired reference would
NOT time-match the denominator. This was caught before any fit of the proposed
sampler. Correct implementation draws one bin per matched reference batch;
all negatives share it. Added a grouped-reference/global-negative bridge
control to isolate batching effects. Unit test checks the complete B×B bin
relation. Independent implementation reviewer confirmed the fix and inspected
source-null grouping, target/probability mapping and chronological ID order.

Reviewer also checked direct-file execution: use documented module invocation
`python -m scripts.start_goal_autoresearch`, from repository root. No new path
bootstrap is needed; existing scripts use this project convention.

## Validation attempts (not scientific findings)

Initial typecheck stopped before tests or fits: CEBRA's dynamic exports,
inherited dataclass constructors and incorrectly annotated iterator exposed
third-party typing issues, plus overly broad sklearn array annotations.
Resolved through direct Loader import, dataset validation, explicit ndarray
conversion and narrow documented API annotation exceptions. Kept failed
`typecheck.txt` and the successful/retry receipts under the study output root.
The experiment command fails fast and records failed phases; never silently
substitutes CPU, drops a case or repairs an invalid source pool.

Large local artifacts and reproducibility receipts live under
`outputs/start-goal-autoresearch-20260907/` (ignored). Code snapshots and input
hashes accompany each phase. No raw/original holdout features are loaded.

## Observed first screen — before the one allowed follow-up

Original-checkpoint Time accuracy fell from 69.72% at 250 updates to 51.67% at
1000, at the common C=.01 readout. Behavior fell from 41.39% to 25.56%.
Temperature .3 + same-bin positives/global negatives reached 83.33% at 250
updates but 64.86% at 3000. The matching-temperature original Behavior scores
were 53.06% and 35.83%. Making every negative time-matched was not an additional
improvement. These diagnose sampling and duration rather than universal CEBRA
failure. The early checkpoint is an inspected development observation.

The stock binwise cross-entropy control also generalized poorly at 3000 updates
(20.00% common readout; 17.22% trained head). This suggests generic neural
training/finite-assembly overfitting, not only a contrastive-loss problem.
However, CE sees 128 complete pseudotrials/update: 3000 updates are roughly 800
training-set passes. Equal encoder steps are not equal exposure to CEBRA's
256 reference bins/update plus positives and negatives. It would be misleading
to call this one end-of-training CE score a fair rejection of supervised MLPs.

### Follow-up declaration — recorded before its fits

One bounded round, four recipes × seeds0/1/2, no new model family or dependencies:

1. Replay binwise CE with snapshots10/25/100/250/1000/3000.
2. Replay whole-cue CE at the same snapshots.
3. Binwise CE with weight decay0.1 (versus0.001), otherwise identical.
4. Binwise CE with the already saved 64-pseudorows/class training assembly,
   unchanged development arrays and original weight decay0.001.

Prediction: if excessive training on a small synthetic assembly is a common
problem, early CE checkpoints and/or stronger regularization or more training
recombinations should improve development scores. If none improves, the encoder
and optimization choices still have not been shown adequate for this dataset.
Evaluate all checkpoints only after training, so decoder/probe initialization
cannot perturb the training RNG. Require the two replay recipes to match their
original final checkpoints and predictions. Save both the common readout and
the actual trained head; do not select one per recipe. These are explicitly
adaptive diagnostics, without new null-based significance claims. No further
fit expansion after this round; finish validation and the teaching report.

## Follow-up outcome and stopping

All 12 follow-up fits completed. Six replay fits matched the original final
encoder/head weights and both readouts' predictions exactly. Binwise CE's early
common-readout maximum was only 28.75% (100 updates); increasing to 64
pseudorows/class reached 49.03% at 3000. Weight decay0.1 drove this recipe to
chance, rather than rescuing it. Whole-cue CE was still improving at its final
sampled checkpoint (37.92% common readout), so do not generalize the binwise
training-duration result to every network. Neither the tested supervised
alternative nor the tested larger CEBRA capacity replaced the PCA reference.

The source-count and augmentation results differ: requested quarter/half/full
source pools yield PCA58.75/73.75/83.61 and CEBRA24.44/43.06/59.58 percent.
The synthetic 16→64 rows/class change raises CEBRA59.58→81.53 percent, but also
raises actually used sources10,889→12,279 within the same available12,288.
No new biological recordings were created. A strict chronological cut supports
all classes in only 1/58 sessions. The weaker within-condition sensitivity does
not establish globally block-held-out generalization.

Stop here, as declared. Dedicated cue-time classifiers, PCA-compressed
hidden-layer matched-dimension probes, cell/session knockout probes, learnable
temperature, moderate CE weight-decay sweeps, FA/count-aware models, and exact
historical replication were not run. Existing hidden probes have differing
feature budgets; their scores cannot uniquely localize information loss.

## Final independent verification and browser checks

Saved outputs passed independent metric/source recomputation: 5,515 artifact
hashes, 1,618 metrics, 1,769,760 session/source components, 111 training-only
scalers, 33 CE-head CPU replays, 300 cross-temporal entries and 112 checkpoint
reload checks. A fresh read-only artifact/content review returned no findings;
this is an artifact audit, not a biological replication.

Initial headless CLI screenshots rendered the top page but a direct deep anchor
was blank (capture timing). A dependency-free DevTools-pipe check waited for
image decoding and rendering, exercised a real navigation click, and detected
a six-pixel mobile overflow plus a heading obscured by the sticky menu. Fixed
inline-code wrapping and anchor scroll margins. The failed browser receipt is
retained, rather than treating Chrome's initial zero exit code as verification.

Runtime-configured Pyright and the runnable tests passed. The auxiliary harness
heuristic treats numeric conversions without a *local* catch as errors even
though the whole study has a recorded fail-fast exception boundary; these were
reviewed as diagnostic noise, not patched with silent recovery. Report-parser
ignores explain intentional error propagation. Checkpoint readers were hardened
to `weights_only=True` after verifying the stored native state dictionaries
support restricted loading. Fitted artifacts and their executed-code snapshots
were not rewritten by that reader-only change.

The completed report index is [start-goal-autoresearch.md](start-goal-autoresearch.md).
All model work is stopped; no new service or environment installation remains.

### Delivery recheck after delayed task notifications

A user-requested completion check confirmed no experiment jobs remained active.
Automatic formatting/diagnostic comments had changed three source-file byte
hashes after the earlier finalization receipt. Both model-source ASTs still
matched the executed snapshots after only the six approved restricted-loader
changes. A disposable rebuild reproduced the entire HTML, including embedded
figures, identically except its build timestamp, and the metric CSV byte-for-byte.
The delivered report was not overwritten and no experimental fits were added.
Ruff, runtime Pyright, and all 12 tests passed again. Current source/artifact
hashes and semantic checks are in `delivery-validation.json`; the earlier
`finalization.json` is retained as a historical receipt. Disposable rebuild
files were removed.
