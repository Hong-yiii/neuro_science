# Is the CEBRA readout too linear? Evidence and proposed work

Date: 2026-09-23 (Asia/Singapore). **Research/planning only; no new model fits.**
Four read-only branches covered local evidence, code, original CEBRA sources,
and experimental design. The parent reconciled their findings, checked saved
metric tables, and retrieved the original paper's Methods.

## Recommendation

Test **decoder limitation**, not the assumed conclusion that CEBRA has already
preserved the relevant information. The smallest useful new experiment is a
**frozen-encoder readout comparison**: regularized logistic regression, cosine
k-nearest neighbours (kNN), and one fixed RBF-kernel SVM recipe. Keep neural
inputs, target, source splits, encoders, and evaluation rows unchanged.

This is not entirely untried: an earlier endpoint study already compared
logistic regression and cosine kNN on frozen CEBRA embeddings. kNN improved on
the original logistic configuration but did not clearly beat stronger logistic
regularization. The more specific gap is a matched nonlinear readout study of
**path-component embeddings**, with independent-source evaluation. RBF SVM on
CEBRA embeddings is also a gap in the inspected accepted code.

Default scientific priority: **future path component beyond start/goal**.
Endpoint decoding is a positive control, not the thesis outcome. If the team
instead means endpoint information, that should be stated explicitly before
implementation. This proposal does not execute or amend the separate
[matched PCA/non-PCA PRD](path-pca-matched-prd-20260913.md).

## 1. What the hunch actually predicts

For a fixed neural encoder, `z = f(cue activity)`, logistic regression models
class log-odds as an affine function of `z`. Its probability link is nonlinear,
but its binary decision boundary is linear in the supplied features. kNN or an
RBF kernel can separate locally structured or curved class regions that this
boundary misses. A nonlinear CEBRA encoder does not guarantee that every target
will be linearly accessible in its output.

The testable hypothesis is:

> On the same source-disjoint evaluation data, a bounded nonlinear readout of
> the same frozen CEBRA features improves path-component decoding relative to
> a reasonably regularized linear readout.

An improvement supports a limitation of the tested readout pipeline. It does
not uniquely isolate nonlinearity from regularization, distance geometry, or
other inductive biases. Failure does not prove the absence of neural information.
Training loss, attractive clusters and training accuracy cannot establish that
CEBRA is “good enough” on new source trials.

## 2. What our existing results say

### Endpoint decoding: nonlinear readout already tested

These are **three-seed mean, 30-class joint balanced accuracies** on the
previously inspected development pseudopopulation, not future-path scores.
Recomputed from saved `decoder_diagnostic.csv` without fitting:

| Frozen features | Original scaled logistic, C=1 | Stronger scaled logistic, C=.01 | Cosine kNN, k=5 |
| --- | ---: | ---: | ---: |
| PCA8 per bin | 82.50% | 83.61% | 78.33% |
| CEBRA-Time8 per bin | 42.78% | 51.67% | 50.14% |
| CEBRA-Behavior8 per bin | 18.61% | 25.56% | 25.69% |

This is evidence that readout settings matter, but not a large nonlinear rescue.
The kNN probability estimates were especially poor: mean log loss was **7.439**
for Time and **16.311** for Behavior, versus **1.919** and **2.499** for C=.01
logistic. Sparse kNN voting can assign zero probability to the true class;
clipping makes the loss finite, not well calibrated. Accuracy alone hides this.

This table is not a complete method ranking. For example, unscaled logistic
C=1 scored PCA 86.25%, Time 47.50% and Behavior 21.94%; scaling and effective
regularization both change. See the [original diagnosis](start-goal-cebra-diagnosis.md).

Later endpoint work changed the **encoder sampler**: same-pair/same-bin
positives and global negatives, temperature .3 and 250 updates, reached
**83.33% joint development accuracy with a logistic readout**, compared with
53.06% for the corresponding original Behavior sampler. At 3,000 updates the
same-bin-positive setting fell to 64.86%. Thus the encoder/sampling/training
choices can matter greatly even with a linear readout. These are adaptive
historical observations, not independent confirmation.

A raw-feature RBF SVM also already exists: **60.28%** mean endpoint development
accuracy, below the PCA/logistic reference in that study. It was not applied to
frozen CEBRA features. The supervised cross-entropy experiments changed the
encoder and objective; they were **not** frozen-embedding nonlinear probes.
See the [endpoint study](start-goal-autoresearch.md).

### Path decoding: source transfer is the important unresolved problem

| Evaluation object | Recorded evidence | Interpretation |
| --- | --- | --- |
| Old fixed-endpoint interior-component CEBRA benchmark | 29 selected units/7 sessions; 82 training + 22 validation source trials | A small cross-session condition-level assay, not a simultaneous 29-cell trial |
| New assemblies made from the same training sources | Mean BA: Time 99.25%, Behavior 99.77% | Transfers across recombinations of those sources; does not demonstrate generalization to new trials |
| Source-disjoint exact validation for the same 50-encoder factorial | Mean BA: Time 24.92%, Behavior 35.17% | Large source-pool gap; its cause is not uniquely identified |
| Prespecified Track B 14-configuration family | Maximum validation BA 58.33%; corrected family p=19/21 | No robust rescue in that tested family; not the same statistic as the 50-encoder means |
| Later, different path-preprocessing assay | 147 training + 41 historical-validation sources; 49 unit IDs/13 sessions; raw-rate logistic BA 55%; only 2/5 endpoint panels positive | Small, source-sensitive diagnostic; no CEBRA representation in this study |

The old path validation has **24 absent + 6 present possible session-block
combinations**, sharing just 22 real source trials. Exhausting these combinations
removes assembly sampling noise, not biological uncertainty. The later five-panel
assay has 17/28 singleton validation pools and is strongly influenced by 6→1.
Neither synthetic rows nor repeated seeds create independent biological samples.

Authorities: [path completion and correction receipt](path-generalization-completed-state-20260907.md),
[current path proposal](path-generalization-next-steps-20260908.md),
[latest preprocessing brief](path-preprocessing-autoresearch-20260908-agent.md).
**Do not combine these cohorts or transfer their scores between targets.**

## 3. Comparison with original CEBRA research

The original paper explicitly states: **“We primarily used a simple kNN
algorithm … as a decoding method for CEBRA.”** [1, Methods: Decoding analysis]
This directly supports testing more than logistic regression. It does not
establish that a nonlinear decoder will rescue our data.

| Published task | Verified decoding procedure | Difference from our question |
| --- | --- | --- |
| Rat CA1 position and running direction | kNN regression for position, classification for direction; cosine distance; k in {1,4,9,16,25}, selected using validation R²; round-trip trial splits with nested threefold evaluation | Current location/direction from 48–120 co-recorded units, 25 ms bins; not a cue predicting later path variation beyond endpoints |
| Macaque S1 reaching | kNN classification for direction and regression for hand position; k searched over 1–2,500; ridge classifier and Lasso as neural-input baselines | Current movement variables in −100 to +500 ms windows around movement onset, not hippocampal prospective path information |
| Allen movie responses | kNN on raw population vectors and CEBRA features; k searched over 1–100; repeats 1–8 train, 9 validation, 10 test; GaussianNB also tested | Repeated, externally controlled movie frame/scene identity; pooled recordings can align to the same stimulus, unlike an unknown future path |

Sources for all procedures are the original Methods, not inferred from demo
plots. The current official decoding tutorial uses **k=36** and a chronological
80/20 split [2]; that is a tutorial configuration, **not** the original rat
paper's k grid or trial-split design.

Other consequential differences:

- **Temporal input:** the paper used ten-sample temporal receptive fields for
  rat, monkey and two-photon data, and 40 for Neuropixels. Our inspected
  endpoint/path `offset1` encoders embed each 100 ms cue bin separately, then
  concatenate ten outputs for the decoder. Eight dimensions per bin means
  **80 classifier features**, not one eight-dimensional whole-trial code.
  Temporal convolutions would be a separate encoder experiment, with safeguards
  against crossing trial boundaries or including navigation after the cue.
- **Geometry:** CEBRA generally normalizes cosine-model outputs. Coordinate-wise
  z-scoring after embedding changes that geometry. Keep cosine kNN unscaled;
  compare an unscaled logistic control before calling a change purely nonlinear.
- **Validation:** original rat CEBRA-Time, UMAP and t-SNE used the full unlabeled
  dataset for embedding fitting, splitting only for decoder evaluation [1].
  That transductive setting differs from our inductive source-safe target.
  We should not loosen our boundary merely to copy a published benchmark.
- **Theory:** CEBRA's linear identifiability concerns agreement between fitted
  embeddings; latent/context recovery requires additional distributional,
  diversity, metric and optimization assumptions [1, theoretical guarantees].
  It is not an unconditional guarantee of linear decoding for this finite,
  sparse, discrete future-path task. Consistency R² is not decoding accuracy.
- **Care with terminology:** the paper calls its GaussianNB comparison “linear
  decoding.” GaussianNB does not generally have linear boundaries when
  class-conditional variances differ; it is not equivalent to logistic regression.

Our archive contains 195 place-selected units across 58 sessions, median three
selected units/session—not 195 simultaneous measurements on every trial. The
[earlier data-volume comparison](cebra-data-volume-comparison-20260907.md) explains
why total archive size is not the support of a particular path contrast. No
universal minimum-neuron/trial rule or uniquely data-count-based diagnosis follows.
Pseudopopulations remain valid for the narrower condition-level question.

## 4. Proposed work, in order

### A. Freeze the diagnostic question and artifact selection

**Label: exploratory analysis.** No new model fitting is authorized by this
planning note. The operational estimand for the cheap follow-up is the paired
difference in source-disjoint historical-validation balanced accuracy between
fixed readout recipes of fixed embeddings, **not** population-level conditional
mutual information or confirmatory H1.

Reuse the old path Track B target/cohort to test the *existing* latent-space
hunch. Freeze its original interior-presence semantics, fixed endpoint pair,
first-second ten-bin inputs, original sources, QC/exclusions, assembly manifests
and exact validation class weights. Independent observations remain source
trials nested in sessions; their serial independence is unresolved. Selected195
scope remains unchanged.

A reasonable bounded anchor is the already saved **dim8, 64 rows/class,
1,000-update** Time and Behavior configuration and its recorded crossed seeds;
list exact fit IDs before a new readout fit. No selecting the best historical
checkpoint or reopening encoder dimensions, samplers, windows or targets. The
existing original endpoint diagnostic above is the sanity-check reference; a
fresh endpoint sweep is unnecessary.

**Important feasibility boundary:** the later five-endpoint supported-middle
assay `D_N_C_M__N_C_B` does not have these CEBRA embeddings. Using that target
would require a separately approved representation study, not renaming old
checkpoints or silently adding GPU training.

### B. Change only the readout; keep the first pass cheap

Compare on identical arrays and labels:

1. **Linear controls:** replay original logistic predictions; include a fixed
   stronger-L2 logistic recipe and unscaled logistic geometry control. Freeze
   exact C/average-loss convention against the training-row count before fitting.
2. **Published-style nonlinear control:** cosine kNN, fixed k=5 to reuse our
   precedent. No coordinate-wise scaling, k search, or validation-selected rule.
3. **New nonlinear probe:** a single predeclared RBF SVM. Suggested engineering
   default: train-only StandardScaler, C=1, gamma='scale', probability=False,
   matching the existing raw RBF implementation. This is not a claim that these
   are optimal settings; failure rejects only this recipe, not all nonlinear
   readouts. It also does not isolate geometry from scaling without the controls.

Use matched raw and train-fitted PCA features with the same decoder families
where exact input/assembly lineage can be reconstructed. Do not substitute
scores from another study. Stop if feature identity/labels/weights cannot be
verified. Reuse or deterministically reconstruct training-only PCA; never fit
it to validation or confuse this with retraining CEBRA.

Primary comparison: balanced accuracy, with the fixed-endpoint chance reference
of 50%; class recalls and binary AUROC provide diagnostics. Probability-producing
logistic/kNN models must also report balanced log loss and Brier score, with a
predeclared clipping policy. SVM margins are **not probabilities**. Do not enable
`SVC(probability=True)` to obtain convenient log loss: its internal calibration
CV does not know our source lineage. A later probability-based comparison needs
source-safe calibration and a separately frozen design.

All candidates are reported. No validation-picked winner, sign flipping,
threshold tuning, MLP/transformer sweep, or additional CEBRA training. CPU-only
readout fitting should suffice; record the exact fit/runtime budget before
execution. This is an economical diagnostic, not a definitive method contest.

### C. Make the result distinguish generalization from memorization

- Evaluate the saved source-disjoint exact validation with its original weights.
  Same-training-source reassembly is a **separate diagnostic**, never the main
  success criterion. If reassembly features are regenerated, do forward-only
  inference with the frozen model and preserve lineage; no refitting.
- Preserve all source derivatives and session-block cells/bins together. Report
  source counts, singleton pools and source/session influence; seed ranges and
  the 30 exact combinations are not biological confidence intervals.
- New decoder CV on saved training embeddings is **not full-pipeline nested CV**
  if their encoder has already seen the inner held-out sources/labels. The cheap
  stage avoids new hyperparameter selection. If later tuning is needed, audit
  feasibility of encoder-training/probe-validation separation or refit encoders
  within source-safe folds. Do not promise this with zero new encoder fits.
- A decoder-only shuffle on target-trained embeddings is not a full CEBRA-null
  test. Biological interpretation would require source-coherent conditional
  shuffling through assembly, supervised encoder and readout/selection. Existing
  matched null-trained checkpoints may be reusable only after verifying their
  complete label maps, source manifests and recipe correspondence. The old
  p=19/21 **does not calibrate a new decoder family**. If that reuse fails, stop
  at descriptive diagnostics; new null encoder fitting needs a separate budget.
- For a future scientifically stronger path study, require endpoint and available
  nuisance baselines with matched fitting budgets, meaningful effect criteria,
  source-aware sensitivity and genuinely unexposed observations. Current
  cue/goal/history/view metadata gaps remain; fixed endpoints do not remove them.

### D. Decide using the pattern, not the highest number

| Observed pattern in the proposed study | Defensible conclusion |
| --- | --- |
| Nonlinear beats linear on independent sources and survives relevant checks | Evidence the tested linear readout underused these embeddings; not a unique nonlinear mechanism or confirmation from exposed data |
| kNN changes little but stronger linear regularization helps | Readout regularization is a simpler explanation worth prioritizing |
| Nonlinear improves training/reassembly but not independent sources | No source-generalizing decoder rescue; more capacity is not the next automatic step |
| Raw/PCA nonlinear readouts succeed but CEBRA does not | Suspect representation loss/mismatch; cannot assert CEBRA preserved the target |
| All representations benefit similarly from nonlinear readouts | Decoder choice matters, but no CEBRA-specific advantage demonstrated |
| All tested methods remain weak | No demonstrated predictive signal with these methods/data; not H1 absence |

Known-label pseudopopulation assembly defines **condition-level separability**.
Even a positive result cannot be called operational unknown-real-trial decoding,
verified simultaneity, intention, causal planning, neural dynamics, or H1b proof.
The historical holdout exposure is permanent.

### E. Minimal implementation and acceptance

Reuse the saved-artifact seam, not a new experiment framework:

| Existing location | Reuse |
| --- | --- |
| `scripts/place195_path_generalization_phase1.py:2685`, `run_one_cebra_fit_with_exposure` | Accepted CEBRA → flattened embeddings → logistic → saved state flow |
| `outputs/path-generalization-20260907/results-20260907T081200Z/track_b/fits/<id>/embeddings_predictions_decoder.npz` | `Z_train`, `Z_validation`, labels, validation weights, original decoder/scaler state |
| Same fit directory: `fit_info.json`, `generated_assembly_manifest.csv`, `exact_evaluation_manifest.csv` | Recipe, hashes and source/assembly provenance |
| `outputs/start-goal-diagnosis-20260907/diagnose_saved_embeddings.py` | Existing frozen logistic/kNN diagnostic precedent; preserve historical bytes |
| `scripts/start_goal_autoresearch.py:188`, `readout` | Existing StandardScaler + RBF SVC recipe and readout persistence |

Before implementation, verify exact live symbol names and artifact schemas;
these are reuse pointers, not permission to execute historical runners. One
small readout-only evaluator plus a runnable synthetic regression check is
enough. Checks must cover saved-logistic parity, source disjointness, weighted
metrics, train-only scaling, an invented nonlinear signal, null/no-signal
behavior, and refusal of mismatched labels/lineage. Save predictions/configs/
hashes in a fresh ignored output directory and verify without encoder fitting.
Independent code/scientific review precedes fitting and interpretation.

**Done:** one paired results table, probability diagnostics where valid,
source-support/influence summary, all attempted recipes and failures, and a
conservative conclusion. Do not turn a nonpositive result into another search.

## 5. Sources, verification and limitations

### Public primary/official sources

1. Schneider, Lee & Mathis (2023), *Learnable latent embeddings for joint
   behavioural and neural analysis*, Nature, DOI
   [10.1038/s41586-023-06031-6](https://doi.org/10.1038/s41586-023-06031-6).
   [Accessible full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC10172131/).
   Checked Methods: Datasets, CEBRA models, Decoding analysis, and Theoretical
   guarantees for linear identifiability. Decoding: “For embeddings obtained
   with cosine metrics we used cosine distance metrics for kNN”. Validation:
   “UMAP, t-SNE and CEBRA-Time were trained using the full dataset without label
   information when learning the embedding”.
2. [Official decoding tutorial](https://cebra.ai/docs/demo_notebooks/Demo_decoding.html).
   Checked 2026-09-23: “For a simple demo, we will use the fixed number of
   neighbors 36”; `cebra.KNNDecoder(n_neighbors=36, metric='cosine')`.
3. [Official usage guidance](https://cebra.ai/docs/usage.html).
   Behavior/Hybrid warning: “you will have to split your original data from
   start as you don't want decode labels from an embedding that is itself
   trained on those labels.”
4. [Official decoder API](https://cebra.ai/docs/api/sklearn/decoder.html) and
   [Allen demo](https://cebra.ai/docs/demo_notebooks/Demo_Allen.html).
   kNN and L1 regression are different supported decoders; an API example is
   not a validation guarantee or an exhaustive literature survey.

### Local evidence and execution boundary

The parent independently averaged all three seeds of the saved
`outputs/start-goal-diagnosis-20260907/decoder_diagnostic.csv` using Python's
stdlib `csv` and `statistics`; results agree with the endpoint table above.
Branches inspected other accepted CSV/JSON metrics and traced code; this was
not a complete forward replay of all saved models. No raw/test records, lab
server, new data downloads, model fits, dependency installs or services were
used. The current checkout's pre-existing changes were preserved.

Fanout artifact root (local/ignored):
`.pi-subagents/artifacts/outputs/9750222d-5f67-486d-ac69-e2ddf7dbe931/work/cebra-decoder-research-20260923/`.
Files: `local-evidence.md`, `code-map.md`, `cebra-primary-literature.md`,
`methods-challenge.md`. These are research drafts, not outcome authority.
The parent corrected omissions: prior latent kNN was already tested; CE heads
are not frozen latent probes; the newer supported-middle panel has no matching
old CEBRA embeddings; and macaque decoder details were verified in full Methods
after the literature branch could not access that text.

Independent fresh-context synthesis review returned **no findings** after the
reuse-symbol corrections. Receipt (local/ignored):
`.pi-subagents/artifacts/outputs/52776571-0cc8-4298-95d8-a40f7a150472/work/cebra-decoder-research-20260923/synthesis-review.md`.
Seven local Markdown links resolve; session diagnostics report no issues. This
is AI-assisted planning QA, not laboratory validation or scientific peer review.

This report is the durable synthesis. New numerical results, a final prefit
protocol, user approval of execution, and biological confirmation remain absent.
