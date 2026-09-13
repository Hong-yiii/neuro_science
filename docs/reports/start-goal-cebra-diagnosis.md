# Why did the start–goal CEBRA baseline underperform PCA?

2026-09-07. **Exploratory diagnosis**, not a confirmed mechanism or new held-out
benchmark. Original run and source splits are unchanged. This note separates
saved evidence, a small executed decoder ablation, and proposed experiments.
See [the baseline report](start-goal-cebra-baseline.md) for full data limitations.

## Saved evidence

| Representation | Mean training joint accuracy | Mean inner-validation joint accuracy |
| --- | ---: | ---: |
| Raw totals | 100.00% | 54.86% |
| Raw ten-bin counts | 100.00% | 71.39% |
| PCA-8 per bin | 100.00% | 82.50% |
| CEBRA-Time-8 per bin | 99.44% | 42.78% |
| CEBRA-Behavior-8 per bin | 92.57% | 18.61% |

These are decoder accuracies on the fitted representations, **not** encoder
training classification objectives. CEBRA is trained with InfoNCE. The gap is
consistent with poor generalization of the encoder-plus-decoder pipeline; it
does not identify which component is responsible or exclude under-optimization.

Additional direct observations:

- The encoder is a small per-bin MLP, `195 -> 32 -> 32 -> 16 -> 8`, with GELU
  nonlinearities and final unit-length normalization: 7,992 trainable model
  parameters. It sees one 100 ms bin at a time, not the whole cue. The downstream
  decoder concatenates ten bins into 80 features. PCA uses the same ten-bin / 80
  feature arrangement; neither is a single 8-D whole-trial embedding.
- Centered singular spectra of the saved 8-D bin embeddings concentrate almost
  all variance in roughly three directions for Behavior and four for Time,
  across all three seeds. This is **spectral concentration**, not proof of total
  collapse or information loss: low-variance directions can still be useful,
  and 30 classes do not mathematically require 29 embedding dimensions.
- All CEBRA bin embeddings have norm approximately one. The current decoder
  z-scores each latent coordinate, which can change the learned angular geometry
  and upweight low-variance directions. Its effect needs measurement, not an
  assumption that z-scoring is intrinsically wrong.
- Contrastive loss continues to decrease near step 1000, but slowly. Behavior's
  final versus preceding 100-step means improve by roughly 0.013–0.017; Time's
  by roughly 0.007–0.010. A falling training loss does not establish improving
  held-out decoding. No held-out contrastive-loss or checkpoint-decoding curve
  has yet been measured.
- PCA's first eight components explain about 14.8% of the standardized training
  variance for seed 0. Strong decoding from them does not mean that 85% of
  biological variance is irrelevant or that the brain has eight dimensions.

## Ranked, falsifiable hypotheses

1. **Time/supervision mismatch.** Behavior positives have the same ordered pair
   but can come from any cue bin. Early start-related and later goal-related
   responses need not resemble one another. Time positives favor adjacent-bin
   similarity, not endpoint discriminability. Test same-pair/same-bin positives
   with time-matched negatives, and separate start/goal supervision. If this is
   important, generalization should improve at matched dimension and compute.
2. **Decoder geometry/regularization.** Coordinate-wise scaling and weak
   regularization may exploit unstable details. Test no scaling, stronger L2,
   and an angular-neighborhood decoder on frozen embeddings. If this fully
   explains the gap, these changes should close most of it without encoder fits.
3. **Representation bottleneck / response magnitude.** Normalization or learned
   compression may discard useful endpoint/time information. Probe hidden layers
   and pre-normalization outputs, test latent norm as an added feature, and
   compare PCA with/without per-bin normalization. The last comparison is only
   a control; it does not identify what the nonlinear encoder has discarded.
4. **Optimization/capacity.** Fixed temperature 1, width 32 and 1000 steps may be
   a poor configuration. Test compute, temperature and width separately. More
   steps helping training loss but not validation would argue against a simple
   insufficient-training explanation.

These hypotheses were stated before the small decoder ablation below. Several
may act together; no root cause has been established.

## Executed: cheap frozen-embedding decoder ablation

No CEBRA retraining or raw-data reassembly. Reuse the three original saved
train/validation arrays, train-fit any scaler/decoder, report every candidate.
C=0.01 means stronger logistic L2 regularization than C=1. Both scaling and C
change effective regularization, so do not attribute every difference to one
geometric mechanism.

| Decoder setting | PCA | CEBRA-Time | CEBRA-Behavior |
| --- | ---: | ---: | ---: |
| Original: z-scored, logistic C=1 | 82.50% | 42.78% | 18.61% |
| No z-scoring, logistic C=1 | 86.25% | 47.50% | 21.94% |
| Z-scored, logistic C=0.01 | 83.61% | 51.67% | 25.56% |
| Cosine k-NN, k=5 | 78.33% | 50.14% | 25.69% |

PCA normalized separately within each bin, then decoded with the original
z-scored C=1 pipeline, scores 79.86% versus 82.50% without normalization.
Magnitude removal hurts that PCA control modestly, not enough to reproduce the
large CEBRA gap. This does not rule out a different effect in the CEBRA encoder.

**Interpretation:** the decoder contributes to the gap, but these changes do
not eliminate it. No claim that a chosen alternative is a confirmed winner:
these are post-baseline development comparisons on previously seen validation.
Original source-shuffle controls have not been rerun for the new configurations.
Cosine k-NN improves CEBRA top-1 accuracy but its sparse voting probabilities have
very poor log loss (Time 7.44; Behavior 16.31); accuracy alone is insufficient.

Retained local artifacts: `outputs/start-goal-diagnosis-20260907/` contains the
pre-fit-contract diagnostic script, 78 metric rows (30 new decoder fits plus
saved baselines), input hashes, geometry spectra, package versions, and logs.
There were no failed decoder runs. This is a bounded diagnostic, not a fix to a
proven software bug. The original 126 CEBRA fits remain unchanged.

## Next ablations, ordered by diagnostic value

1. **Read out existing checkpoints:** steps 1/250/500/750/1000; fit the same
   fixed decoder anew on training embeddings at each checkpoint. Plot training
   and development decoding, log loss, embedding spectra and contrastive loss.
   This distinguishes useful learning from memorization without new GPU fits.
2. **Training duration:** continue comparable runs to 3000 and 10000 steps if
   justified by those curves. Keep pseudo arrays, seeds and decoder protocol
   fixed. Do not compare absolute InfoNCE losses across different temperatures,
   batch sizes, or samplers as if they were the same objective.
3. **Sampling and target:** same-time positives/negatives; start-only, goal-only,
   and joint labels; a same-input/same-encoder cross-entropy control. One change
   at a time. A larger temporal receptive field must remain inside each cue
   trial, with the same input window supplied to comparison methods.
4. **Temperature and capacity:** temperature 1/0.3/0.1 or learnable temperature;
   latent dimension 3/8/16 and width 32/64/128 in separate bounded sweeps. Inspect
   effective rank, not just requested output dimension. Avoid a huge factorial
   search. CEBRA documents learnable temperature and k-NN decoding (links below).
5. **Assembly sensitivity:** random versus chronological condition pairing;
   session-block/unit subsets; more synthetic assemblies at a fixed real-source
   pool. Keep feature availability identical across target classes.

### Scaling curves, not yet scaling laws

Separate four axes:

- **Compute:** optimizer steps / measured runtime at fixed data/model.
- **Independent source data:** fractions of real training source trials; retain
  whole-trial bins and all same-session unit values together.
- **Units:** predefined unit/session subsets, keeping source data budget fixed.
- **Synthetic augmentation:** pseudorows per class at a fixed source pool.

Generating 16/64/256 pseudorows per class is not a 16-fold increase in biological
sample size. The sparsest session/condition has one training source, so a
source-count sweep needs a fixed common-support panel, or explicit reporting
of actual counts; it cannot invent extra sources or change its cell panel at
each budget. Plot means/ranges over matched seeds and source-aware uncertainty,
not error bars treating pseudorows as independent. Do not fit a power-law claim
to a handful of small, dependent observations.

Use training-only/nested development selection for larger sweeps. The existing
inner validation is now an inspected development set, not a new confirmatory
holdout, and the original test's historical exposure is not repaired by tuning.

## Interpretability: useful, but specify whose mechanism

For the **trained model**, start with layerwise linear probes of start, goal
and cue time, pre-/post-normalization comparisons, source-held-out distances
between condition means, and leave-unit/session-block-out refits. Ask whether
the encoder retains goal but loses start, or replaces condition information
with time-in-cue. Compare matching controls for raw/PCA/CEBRA, including random
or untrained representations if attributing an effect specifically to learning.

For the **biological responses**, inspect training-defined start, goal, and
start×goal contributions, held-out tuning curves, and cross-temporal decoding.
Use count-appropriate models (e.g. Poisson with exposure, and check dispersion)
or simple descriptive models with source-aware validation. Do not call a
classifier weight, gradient, attribution map, or pseudopopulation correlation
a biological circuit, causal neuron, intention or planning mechanism. Cue
identity is tied to goal and previous goal to current start. Their confounds
remain even if a representation is interpretable. An SAE is not the first tool
for an 8-D embedding with this source-support limit.

## Comparison with the previous student

A bounded read-only inspection of the public repository was performed at commit
`2f12016c58472888b83298d163be1daaf5291a1e`:

- `neurosci_2023_pseudopop.ipynb`, zero-based cell 15: custom split helper assigns
  test rows by `row_index % 10 == fold`; it has no source-trial group argument.
- Cells 36/39: bootstrap helper and 25th-percentile / 0.67-threshold support rules.
- Cell 49: PCA fit to pooled data for visualization, not our train-only PCA
  decoding baseline. Do not assume that visualization alone contaminated LDA.
- Cell 72: separate 100 ms start, goal and joint LDA models, plus a factorized
  start/goal comparison. Cell 73 adds the extended window and a heuristic for
  resolving invalid equal-start/equal-goal separate predictions.
- Cell 70 flattens each trial's ten time bins and applies the modulo-10 split:
  that code path puts one bin in test and other bins from the same trial in
  training. This is a concrete within-trial leakage path. Do not confuse it with
  cells 72/73's per-bin evaluation, where cross-fold reuse of bootstrapped source
  components still requires source tracing. This is not proof every historical
  result or the write-up's main per-bin result used the leaky pooled-bin path.

We therefore **cannot claim numerical superiority to the student** from 82.5%.
A fair bridge is student-style LDA-start, LDA-goal and LDA-joint on the same 195
cells, same cue bins, same success/QC rules and same source splits as our methods.
Compare single-bin against single-bin and full-cue against full-cue. Separate
heads are not the same as deriving start/goal from a predicted joint label.

A faithful historical reproduction is a separate exercise requiring the original
233-cell selection, preprocessing and result artifacts. Report it alongside a
source-safe reimplementation; do not silently reproduce duplicate leakage. A
10-fold source-safe design may be infeasible for the rare session/conditions;
use a justified feasible design rather than splitting copies or filling missing
channels. Source-safe chronological versus random assembly is a useful ablation,
not an excuse to change the split after seeing scores.

The historical note reports strongest goal-related separation around 0.3–0.6 s.
Our existing **joint**, not separate-goal, LDA peaks at 0.3–0.4 s (39.58% mean).
That is broadly timing-compatible, not a matched quantitative reproduction.
No exact original numeric accuracy table was recovered in this bounded audit;
notebooks were inspected, not executed against missing historical data.

Independent bounded review found no issues in the new diagnostic script/output
claims. It confirmed the legacy pooled-bin leakage path and the original
split helper's lack of source grouping; these limitations are kept separate
from claims about the student's other analyses.

Sources:

- [Original student repository](https://github.com/josephchengyx/Hippocampus_Decoding/tree/2f12016c58472888b83298d163be1daaf5291a1e).
- [Historical write-up summary](../../context/previous-student-analysis.md).
- [CEBRA learnable temperature](https://cebra.ai/docs/demo_notebooks/Demo_learnable_temperature.html).
- [CEBRA decoding tutorial](https://cebra.ai/docs/demo_notebooks/Demo_decoding.html).
