# Does broader CEBRA training help cue-only decoding?

**Completed exploratory experiment · September 24–25, 2026.**
[Offline illustrated HTML](report.html) · [Frozen protocol](protocol.md) · [Execution/review ledger](execution.md)

## Answer

**The predeclared primary exploratory follow-up criterion did not pass.** Time/logistic balanced loss changed from **1.010464** with cue-only encoder training to **0.710618** with broader training: paired gain **+0.299846 nats**. Its balanced accuracy changed from **32.64%** to **61.81%**. Constant-.5 loss is **0.693147** and chance BA is **50%**.

**Your idea improved this cue-only readout for CEBRA-Time; Behavior was not similarly helped.** Time loss improved in all three computational seeds, but absolute discrimination was uneven: only one seed had AUROC above .5. That is an informative pipeline result, not established biological path information.

The experiment distinguishes training coverage from prediction inputs. Navigation activity was added **only while training the encoder on training source trials**. Both decoder fitting and historical-validation prediction received **only the original cue window**. This is not decoding the path after observing its navigation activity.

## Matched results

All numbers below are means of three paired assembly/optimizer seeds. Seeds are computational sensitivity, not three independent biological replications. Lower loss and higher BA/AUROC mean different things; a loss improvement that remains worse than the constant baseline does not, by itself, satisfy this study's declared success rule or establish prospective coding.

| Representation | Logistic loss ↓ | Logistic BA | Logistic AUROC | RBF BA | RBF AUROC |
|---|---|---|---|---|---|
| Cue Time | 1.010464 | 32.64% | 0.146 | 40.28% | 0.002 |
| Broader Time | 0.710618 | 61.81% | 0.574 | 50.69% | 0.634 |
| Cue Behavior | 0.915000 | 34.03% | 0.359 | 35.42% | 0.331 |
| Broader Behavior | 1.075865 | 36.11% | 0.155 | 44.44% | 0.271 |
| Raw cue | 0.742886 | 46.53% | 0.549 | 30.56% | 0.000 |
| PCA cue | 0.892401 | 22.22% | 0.072 | 55.56% | 0.525 |

[View the matched-result figures in the offline report](report.html).

| Seed | Time cue−broader loss | Broader Time BA | Broader Time AUROC | Behavior cue−broader loss |
|---|---|---|---|---|
| 0 | +0.407785 | 79.17% | 0.889 | -0.335365 |
| 1 | +0.102276 | 43.75% | 0.361 | -0.046634 |
| 2 | +0.389476 | 62.50% | 0.472 | -0.100597 |

The frozen primary follow-up rule required all four: Time loss gain ≥ .01 nats, broader-Time loss<log2, BA>50%, AUROC>.5. Component decisions are `{"full_auroc_gt_0p5": true, "full_ba_gt_0p5": true, "full_loss_lt_log2": false, "gain_ge_0p01": true}`. Behavior and the RBF readout were predeclared secondary comparisons, not outcome-selected replacements for the primary analysis. No hyperparameter/threshold/checkpoint was selected after observing these results.

## Null and source sensitivity

The source-coherent label null repeats the entire conditional assembly, scaler, encoder, PCA and decoder pipeline in 20 worlds, with all three seeds in each world. The observed **three-seed mean** gain is compared to that same statistic in each null world—not to an unrelated single-seed anchor.

- Primary Time/logistic paired-gain inclusive plus-one tail: **0.047619** (1/21).
- Maximum-over-two-objectives paired-gain tail: **0.142857** (3/21).
- **Absolute broader-Time performance:** its loss-based no-association tail is **0.571429** (12/21). The small primary paired-gain tail concerns improvement over a poor cue-only model; it is not evidence that the broader model's absolute path decoding passed its null.
- These are limited-resolution no-association references, **not general tests of equal predictive risk/superiority**, and they do not undo prior adaptive exposure or unresolved serial exchangeability.
- Paired source-reweighting gain 2.5/50/97.5% quantiles: **+0.098554 / +0.316961 / +0.523363**. These are fixed-model pool-weight sensitivity, **not biological confidence intervals**.
- Broader-Time BA source-weight 2.5/50/97.5% quantiles: **44.44% / 61.81% / 76.42%**. Absolute discrimination is more fragile than the relative loss gain.
- 8/22 source deletions are inestimable because a class loses support; these were retained explicitly. Singleton pools cannot estimate variability from unseen sources.

[View the paired-gain null figure in the offline report](report.html).

Full-arm baseline-relative null references, all observed seed/metric rows, and sensitivity summaries are in [summary.json](summary.json). Complete per-source/per-world arrays remain in the ignored local run directory. The primary rule alone cannot establish biological signal.

## What was actually compared?

- **Fixed cohort/target:** 29 selected unit IDs, seven session blocks; 82 training + 22 historical-validation sources; endpoint 4→3; presence of `D_N_R_T__N_R_M` among all interior corridor runs after removing first/last runs. It is not full-path reconstruction or endpoint classification.
- **Population construction:** 64 known-label-conditioned training rows/class; exact validation 30 combinations (24 absent / 6 present), half the evaluation mass/class. These synthetic combinations are not 30 independent natural trials or a simultaneous 29-unit population. Time omits path labels from its objective, but assembly is still label-conditioned.
- **Cue readout:** ten 100-ms bins in the original first-second window, with actual cue-offset clipping where needed. Encoder: 8 coordinates/bin → 80 decoder features; raw cue has 290 features. PCA 8/bin uses one pooled training-bin basis.
- **Broader training:** retained cue window plus complete native 100-ms navigation bins across the training sources' navigation span. Small cue tails beyond one second and final partial navigation bins are excluded and audited. “Full” in machine arm IDs is shorthand, not literal use of every millisecond.
- **Variable duration:** navigation source bins are never time-warped or zero-filled. A normalized-duration pair bank matches relative phase progress across session blocks. Each Time positive advances every block by its own actual next 100-ms bin. Pair-bank rows are **not a real continuous pseudotrajectory or physical-position alignment**.
- **Matched encoder budget:** four arms (cue/broader × Time/Behavior), shared cue-fitted scaler, paired model initialization, offset1 pointwise encoder, hidden 32 / output 8, cosine temperature 1, Adam 3e−4, batch 256, 1,000 updates. Broader training samples 50/50 cue/navigation; the intervention therefore reallocates a fixed contrastive budget, not additional optimization steps.
- **Fixed readouts:** scaled logistic C=.01 and scaled RBF-SVM C=1 / gamma=scale; no new tuning. Raw/PCA controls use identical newly assembled cue rows. Do not transplant scores from older differently assembled/optimized experiments.

## What can and cannot follow

This tests whether one specified broader-training representation transfers better to cue-only decoding across historically disjoint source pools **within the existing sessions**. Any positive result remains condition-level association beyond a fixed endpoint, with unresolved cue/history/view and selected-cell/source-support confounds. Known future labels also define validation assembly, so this is not an operational unknown-trial predictor.

It does not establish intention, causal planning, a simultaneous population state, H1 confirmation, H1b geometry or H2. A negative result does not show absence of cue information or that broader pretraining can never help. Different coverage weighting, temporal encoders or independent recordings are untested—not queued automatically by this report. The historically exposed validation pool is not a pristine test set.

## Execution and reproducibility

Exactly **252 CEBRA encoders** (12 observed + 240 null), **63 PCA transforms** and **756 readouts** were fitted under the frozen family. Verification replays every model without fitting; shared helper logic is complemented by independent numerical/claim review. Software controls and rejected implementation drafts are not biological replications.

- Fit code revision: `e171328d4eb2ed095f3b2af08315e9088cfe77de`; exact executed code/protocol/helper snapshots and package/device metadata are retained with the run.
- Accepted local run: `/home/hongyi-home-lab/neuro_science/outputs/cebra-full-trial-transfer-20260924/biological-run-20260924T162913Z`.
- Forward-only verification: `/home/hongyi-home-lab/neuro_science/outputs/cebra-full-trial-transfer-20260924/biological-run-20260924T162913Z-verify`; [compact verification receipt](verification.json).
- The new worktree is retained through PR review; private data/models live in canonical outputs, not Git. No persistent service or public endpoint was created.

See [execution.md](execution.md) for review resolutions, commands, static-check limitations, and retained QA attempts. Git is not a backup of ignored private inputs/models. AI review is QA, not laboratory metadata verification or scientific peer review.
