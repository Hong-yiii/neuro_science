# Project direction — agreed September 27, 2026

**Next-session priority updated October9:** start with the [observability/CEBRA handoff](observability-pivot-20261009.md). Hongyi requested developing that pivot in a new session after PR15 integration. Its operational definition and protocol remain open; no new fits or data access are authorized.

**Historical September27/28 decision record:** the scope below was agreed after the September26 review and PR11. Its H1-led next-work priority is now superseded, not its source-safety, validation or claim limits. Preserve it as history; do not execute its old task queue or treat the pivot as a negative H1 result.

Read this, then [research questions](research-questions.md), [analysis contract](analysis-contract.md), and [workspace/recovery](workspace.md). The [September26 retrospective](reports/research-reset-20260926/README.md) explains the evidence available when these choices were made; its recommendations are not all adopted.

## September28 follow-up — visualization and validation

Hongyi agreed to **source-support audit → saved-result plots → bounded prefit
protocol**, and authorized a new PR and merge carrying forward the professor
review. [Detailed agreed follow-up](professor_updates/research_review_20260928/validation-plan.md)
and [self-contained review](professor_updates/research_review_20260928/review.html).
Make future scientific reports independently readable and data/graph-backed:
real-source versus synthetic class distributions, performance, confusion matrices,
cue-time and navigation-time decoding, and appropriate controls. Missing results
must be labelled, not invented or silently obtained through new fits.

The primary method comparison remains **joint versus cue-only encoder training,
scored on held-out cue activity**. Separately validate time/phase transfer using
frozen encoders, preprocessing and decoder weights within each representation.
Window-specific decoders test accessible information, not a persistent shared
code. Cross-phase readout transfer supports a common task readout, not identical
biological geometry, rotation or H1 by itself. Navigation-time evaluation is an
agreed extension to design, not a completed result or a new encoder arm. Resolve
compatible windows/features, target semantics/support, folds and total fit budget
before independent review and explicit run authorization. H1/H2 scope below is unchanged.

## 1. Decisions made

| Area | Agreed direction |
| --- | --- |
| Central question | Retain H1: cue-period activity contains prospective information about the subsequently observed **path beyond start and goal**. No switch to a primarily phase-geometry or methods thesis. |
| H1 components | Retain H1a (incremental held-out information) and H1b (reproducible low-dimensional organization). Encoder/decoder success alone does not establish both. |
| H2 | **Remove the artificial-navigation-agent comparison from active scope**, not merely defer it as a stretch aim. Do not replace it with a new H2 without a decision. |
| Neural encoder family | **CEBRA-Time only** for the next comparison, with one predeclared architecture/configuration. No CEBRA-Behavior, architecture, temperature, dimension or broad hyperparameter sweep by default. Existing historical models remain preserved. |
| Training-data comparison | Build on **cue-only versus joint cue/navigation training**, evaluating path prediction from cue inputs only. |
| Training duration | Two predefined training durations/checkpoints, not an open-ended stopping-time search. Save both along one training trajectory per arm/fold/seed where possible; do not retrain identical prefixes unnecessarily. Counts and seed policy remain open. |
| Baselines | Retain **PCA and Linear Discriminant Analysis (LDA)**, alongside the task's start/goal-only reference. Baseline construction/dimensions remain to be specified. |
| Decoder | **Open decision.** Do not silently select logistic regression, RBF-SVM, an MLP, a graph network or end-to-end fine-tuning. A graph-valued output does not require a new neural encoder family. Resolve and bound decoder comparisons before fitting. |
| Evaluation | Deliberate folds of **real source trials before assembly**, not random splits of synthetic rows. Exact fold scheme, count and temporal treatment remain open. |
| Pseudopopulation deliverable | A clear construction/provenance artifact with runnable verification checks, not a new broad campaign of model ablations or pseudopopulation benchmarking. Preserve scientific claim limits. |
| Phase selectivity / rotation | Leave open for mentor clarification, validation design and the referenced literature. No paper has been identified or phase-rotation claim adopted. |

## 2. A and B: keep the path ambition

- **A — component-level graph assay:** predict whether an interior directed edge or route segment occurs in the later path. This is the simpler benchmark/minimum-resolution assay, not the definition of full path prediction.
- **B — desired capability:** predict the **ordered path through the maze graph**, including order/revisits where meaningful. This remains in scope, not replaced by start/end classification. It does not promise exact millisecond-by-millisecond continuous movement reconstruction.

A and B are different tasks. A is not the statistical comparison baseline for B; baseline methods must solve the **same target with the same held-out metric**. A positive result is component information, not full-route reconstruction. Failure on one component does not rule out every other path feature or make A significance a universal prerequisite for B.

For either task, compare a start/goal-only predictor with a predictor that additionally uses cue activity. A canonical route predictable from endpoints alone does not establish H1. For B, define a primary graph-path error/similarity metric before fitting; exact sequence matching can be an additional measure. Target, graph granularity, handling of multiple valid routes and meaningful improvement thresholds are unresolved. Choose targets from behavior/task meaning and support, not whichever old neural score was highest.

**B has a ground-truth gate.** Current component-conditioned pseudorows can combine source trials with different complete paths. Do not assign one source's path arbitrarily to the whole synthetic row. Before B, specify a defensible route-level construction/target and demonstrate its source support. Condition-level route prediction is distinct from prediction of one real trial's entire path. Exact trial-specific population claims still require verified simultaneous activity linked to that same trial; a simultaneous195 recording is not a prerequisite for valid condition-level work.

## 3. What joint training means

The comparison changes what observations are used to learn the encoder:

```text
cue-only arm:  training-source cue activity          -> encoder f_cue
joint arm:     training-source cue + navigation     -> encoder f_joint

both readouts: cue activity -> encoder -> chosen decoder -> path target
```

No evaluation-source navigation activity enters encoder fitting, preprocessing or cue prediction. Keep preprocessing, sources, architecture, optimization budget and readout policy matched except for the declared intervention. A fixed update budget with a cue/navigation mixture also changes cue exposure; the phase weighting and exposure accounting must be specified, not described simply as "more training."

The September28 supporting validation adds planned navigation-time and frozen
cross-phase readout tests separately from this primary cue-only evaluation.
It does not retrospectively change the completed assay.

Joint training means **shared encoder parameters**, not an established shared biological latent representation. The existing Time sampler uses within-phase temporal positives; it does not explicitly align matched cue/navigation states across phases. Improved cue decoding could reflect useful shared features, regularization, sampling effects or nuisance structure. It is not proof of shared geometry, rotation, intention or planning.

Use **joint cue/navigation training** for this comparison. Navigation-only pretraining followed by cue fine-tuning is a different intervention, not silently included under the same name. Decoder type and training policy remain open; end-to-end fine-tuning would alter the encoder intervention and needs an explicit protocol decision.

## 4. Deliberate folds and baseline fairness

Before any learned transform or pseudopopulation assembly:

1. Inventory eligible real source trials, session/unit identities, endpoints, path targets, exposure history and available nuisance metadata.
2. Assign complete sources to folds. Keep each source's cue/navigation bins and every derivative on one side; within-session serial dependence may require blocked/grouped splits rather than naïve random trials.
3. Check target/endpoint support per fold. Do not assume five/ten folds or silently discard unsupported folds after seeing neural outcomes. Whole-session holdout is not plug-and-play when neuron identities/feature columns change.
4. Fit normalization, PCA, LDA, learned graph/path processing, CEBRA and readouts on training sources only. Use the same folds and evaluation object across arms; selection/calibration, if any, needs an inner training partition, not evaluation-fold outcomes.
5. Compare both predefined checkpoints without cherry-picking the best on outer folds. Any selected model needs a separate selection/evaluation rule. Computational seeds and synthetic rows are not biological replications.

PCA is unsupervised dimensionality reduction; **LDA uses target labels** and, for K classes, provides at most K−1 discriminant dimensions (one for a binary target). It is not an unsupervised geometry control or intrinsically an eight-dimensional counterpart to CEBRA/PCA. LDA's role for a sequence-valued B target is unresolved. CEBRA-Time does not use path labels in its temporal objective, but the existing pseudopopulation assembly still uses known target labels, including at evaluation: this is a conditional benchmark, not an unknown-label natural-trial predictor.

Resplitting already inspected sources evaluates exploratory robustness; it does not restore a pristine confirmation set. Keep appropriate endpoint/nuisance controls, source-aware uncertainty and justified nulls. Reducing candidate settings is not permission to drop leakage safeguards or falsification controls. Predeclare the complete budget across arms, checkpoints, folds, seeds, readouts and necessary null refits; do not inherit old large search budgets automatically.

## 5. Pseudopopulation construction artifact

The agreed deliverable is a readable methods document/diagram plus small runnable checks, reusing existing construction code and tests where possible:

```text
source ledger -> source folds -> matching pools -> session-block draws
              -> pseudorow lineage -> phase tensors -> prediction inputs
```

It must explain:

- measured inputs versus derived labels/arrays; units, clocks, phase boundaries and inclusion rules;
- matching keys and their assumptions, with a worked example tracing one row to all real source trials;
- intact source/session blocks across cells and bins, masks for missing recordings, and exact tensor shapes;
- real trial/session counts separately from synthetic combinations, seeds and repeated bins;
- identities/hashes/manifests sufficient to reproduce construction without refitting biological models;
- checks for source leakage, count/shape/label consistency, phase/boundary errors, missing-as-zero errors and save/reload lineage;
- known limitations, including label-conditioned construction, unverified simultaneity and unavailable cross-session noise correlations;
- the target-definition gate before using component-conditioned rows for full ordered-path prediction.

This is **planned work, not an artifact claimed complete by writing this update**. Mechanical checks verify the declared procedure; they do not prove all biological assumptions. No individual-neuron-significance gate or new broad validation campaign was agreed.

## 6. Evidence motivating the direction—not a new result

The [completed broader-training study](reports/cebra-full-trial-transfer/README.md) already compared cue-only and joint training, with **trained logistic and nonlinear RBF-SVM readouts** on CEBRA, raw and PCA features. It was not just PCA plus logistic regression. A neural-network decoder would be a new choice, not the first trained decoder.

Time/logistic loss improved **1.010464 → 0.710618**, but remained worse than constant-.5 loss **0.693147**, failing the declared primary criterion. Absolute performance varied by seed. Its fixed 4→3 endpoints rule out changing goal identity as the within-assay class separator; they do not establish general goal-independent coding or remove other confounds. The [earlier nonlinear readout](reports/cebra-decoder-autoresearch-20260924.md) and [regularization diagnosis](reports/cebra-hyperparameter-diagnosis-20260924.md) did not rescue their frozen CEBRA family. Scores from their different constructions must not be pooled into a leaderboard.

This motivates a narrower training-data study, not a conclusion that joint training reveals one common brain manifold, that H1 is confirmed/absent, or that a more complex decoder must succeed.

## 7. Next session: resolve, document, then propose—not launch

1. Start from the integrated `main` handoff and these agreed decisions. Do not reopen model/objective sweeps or resurrect H2 from older reports.
2. Incorporate the mentor's phase-selectivity paper and clarify what "rotation" means: neuronal selectivity, population relationships, or arbitrary axes of separately fitted embeddings. Leave this line open until then; no invented citation.
3. Prepare the pseudopopulation construction artifact and a source-support/fold proposal using the agreed scope. It is not a demand to repeat every historical validation experiment.
4. Resolve the target(s), B ground truth/feasibility, fold count/grouping, two checkpoint counts, one encoder configuration, decoder policy, baseline roles, metrics, nulls and total fit budget in **one bounded prefit protocol**.
5. Obtain explicit authorization and independent code/scientific review before any new biological fitting or expanded data access. No model run, raw-data extraction, package install, artifact migration or worktree retirement is authorized by this documentation update.

Publication/PR reconciliation and local recovery evidence are maintained in [workspace](workspace.md). Historical protocols retain their executed settings; this update changes future intent, not their numerical results or provenance.
