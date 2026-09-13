# Path-preprocessing study: frozen methods and execution gates

Date: 2026-09-08. **Exploratory analysis, not confirmatory H1.** This readable contract accompanies the immutable prefit protocol, source/fold manifest, and dated independent reviews. It supersedes the initial implementation-only status of this file; the scientific comparison family has not changed.

## Question and allowed claim

Do source-disjoint trial sets reproduce a cue-response pattern associated with the subsequent presence of a particular **interior path component**, within fixed start–goal pairs? The target is the previously behavior/support-selected directed central-middle→central-bottom component, `D_N_C_M__N_C_B`.

“Interior” means all corridor runs after removing the first and last—not one midpoint. This binary target is not reconstruction of a complete ordered path. It is not the previous endpoint-based “trajectory class.”

Separate, condition-matched pseudopopulations remain the primary assay. Evaluation uses known path labels to assemble its inputs. That defines a conditional response-reproducibility benchmark, **not an operational decoder of an unknown-label simultaneous trial**. It does not recover cross-recording covariance, intention, causal planning, or H1b dimensionality. Individually significant neurons and a simultaneous195 recording are not prerequisites for this narrower question.

## Frozen measurement and support

- Scope: selected195 archive only; no removed supplement and no new original-test evaluation.
- Target labels and coverage/QC metadata: previously accepted development export in the path-diagnosis worktree.
- Include validated present/absent labels with complete directed-path coverage, valid absence labels, empty recorded QC flags, and cue duration in `[1.0, 1.5]` seconds.
- Neural input: exactly the first `[0,1)` seconds of the accepted operational cue window. Store ten half-open100ms bins. Save excluded cue-tail counts and verify conservation against each full-cue count. A one-bin representation means the **entire analyzed first second**, not the variable-duration cue tail.
- Fixed session×endpoint eligibility: ≥3 original-training sources/class and ≥1 historical-validation source/class. Validation support is intentionally part of this development-conditioned benchmark design; do not call cohort selection strictly training-only.
- Two sources were excluded because their cues ended at0.99804s and0.98303s. This implements the complete-one-second window rule; it does not establish that those recordings were intrinsically bad.

| Endpoint | Session blocks | Unit IDs | Train sources | Historical-validation sources |
|---|---:|---:|---:|---:|
| 2→1 | 1 | 2 | 12 | 3 |
| 3→1 | 3 | 14 | 31 | 11 |
| 4→1 | 1 | 3 | 9 | 2 |
| 5→1 | 3 | 12 | 33 | 8 |
| 6→1 | 6 | 23 | 62 | 17 |

There are **147 train +41 historical-validation sources,49 unique unit IDs and13 unique sessions**. Units/sessions overlap across endpoint panels, so their table columns must not be summed as independent subjects. The export contains756 observed unit–source pairs, not188 simultaneous49-unit trials.

Cue events are streamed through `SplitFilteredAccess`, then restricted to the exact pinned source/cell allowlist. Physical files contain skipped original-test rows; zero forbidden rows may be yielded. Unrecorded cells remain masked/NaN, never filled with zero. One source supplies all cells and time bins of its session block in each assembled row. Same-session membership remains candidate, not lab-verified simultaneity.

## Splits and two research rounds

Original train/validation source identities are unchanged. Original-training sources have three frozen inner folds, stratified within session×endpoint×label, using `random.Random(20260908)` on sorted IDs with round-robin assignment. Sources and all their derivatives stay together. Identity-disjoint folds are not a guarantee of serial independence.

**Round1:18 matched arms**, all with average-loss L2 λ=0.1:

| Factor | Levels | Hypothesis, not a presumed fact |
|---|---|---|
| Temporal summary | 1,2,5 bins over the same first second | Coarse pooling may trade temporal detail for lower estimation variance |
| Count transform | raw rate, sqrt(rate), log1p(rate) | Compression may alter the geometry accessible to a regularized linear readout |
| Scaling | ordinary training z-score; training variance floor | Near-constant sparse features may receive unstable effective weights |

The variance floor is the median strictly positive training feature SD. Divide by `max(SD,floor)`; use a scale of1 if everything is constant. It is a numerical regularizer, not an established hippocampal noise model. Square-root rate is a compression heuristic, not an assertion of Poisson counts.

Fit logistic regression with an unpenalized intercept and average-loss L2 λ. The sklearn setting is `C=1/(λ*N_training_rows)`; the regression test checks invariance to duplicating every training row. Primary training assembly uses seed0 and128 rows/class. Source draws are matched across every preprocessing arm. Report actual source coverage separately from synthetic row count.

**Round2:one predeclared adaptive axis.** Take the Round1 CV-best representation and add only λ=0.01 and1.0. Keep the original18 arms, then select by seed0 inner CV among the resulting20. No new target, source panel, time window, PCA, residualizer, or CEBRA model is added. The dated `ROUND2-DECISION.md` records the decision before these fits.

Historical-validation **predictive outcomes** remain withheld until this selection freezes. The underlying data have prior exposure: this procedure cannot restore pristine confirmation.

## Evaluation and controls

Each endpoint has its own model/panel. The primary score is the equal-endpoint, equal-fold mean of:

`Δlogloss = log(2) − balanced conditional-pseudopopulation logloss`.

The endpoint baseline is constant probability0.5 because each model holds both endpoints fixed and evaluation weights assign equal class mass. This is not natural-prevalence calibration on ordinary real trials. Report balanced accuracy, Brier score, AUROC, training loss/gaps, convergence, and source coverage as secondary diagnostics. Exact validation products remove evaluation-assembly Monte Carlo noise when tractable; they do not create biological observations.

After the20-arm selection freezes:

1. Evaluate the declared family on the already-exposed historical-validation pool.
2. Run100 source-label permutations within session×endpoint×split×innerfold strata, and100 further permutations additionally conditioned on training-defined temporal halves. Cells/bins of a source move together. Each null chooses **its own** Round1 representation and L2 refinement. Save all candidate metrics, predictions, coefficients/scalers, and source lineage.
3. Report inclusive `>=`, plus-one p-values for the CV-selected policy, and a conservative max-family null reference against that same observed CV-selected statistic. Do not choose whichever policy gives a favorable answer. Temporal-half exchangeability is a sensitivity assumption, not proof that serial dependence is solved.
4. Repeat the observed family with assembly seeds1/2 as **non-selecting sensitivity**. Synthetic-draw variation is not source uncertainty.
5. Fit a fixed nuisance-only trial-index/cue-duration decoder on identical draws/folds, with training-only scaling and λ=0.1. This is a descriptive comparator, **not a nested neural-plus-nuisance conditional test**.
6. Run200 source-stratified bootstrap refits of the frozen recipe, preserving session/endpoint/class/split. These are source-resampling sensitivity quantiles, not animal-level or selection-adjusted confidence intervals. Single-source pools cannot reveal unobserved variance.
7. Report leave-endpoint-out point influence and leave-session-out refits, actually removing that session's source rows and cell columns. Compare common remaining endpoints; do not swap neuron identities and call it transfer.

Endpoints2→1 and4→1 provide **point/influence diagnostics only**, not interval-backed repeatability. Aggregate intervals inherit this limitation. Other panels also contain single-source session×class pools, which must be disclosed.

A positive aggregate alone is insufficient: inspect endpoint/session dominance, nuisance results, source sensitivity, and the declared nulls. A smallest biologically worthwhile effect is unresolved; no absence/equivalence claim is licensed. Fixed endpoints also fix previous-goal identity under the reported task rule; that identity alone cannot explain a within-pair difference. Other varying history, cue, gaze, and state variables remain unresolved.

## Evidence and implementation

- Main CLI: `scripts/place195_path_preprocessing_autoresearch.py`.
- Forward-replay/no-fit verifier: `scripts/verify_path_preprocessing_results.py`.
- Synthetic and regression checks: `scripts/test_place195_path_preprocessing_autoresearch.py`, plus existing split/bin tests.
- Immutable prefit copies: `work/path-autoresearch-20260908/immutable-prefit-inputs/`.
- Original CV and final code snapshots: `work/path-autoresearch-20260908/code-snapshots/`.
- Manager/evaluator history: `/home/hongyi-home-lab/neuro_science/outputs/path-autoresearch-management-20260908/`.
- Biological run: `outputs/path-preprocessing-autoresearch-20260908/biological-20260908T115508Z/`.

Prefit scientific review, export/CV code gates, the adaptive-round review, and final inference review are distinct receipts. AI-assisted independent review is not human peer review. Original prototype failures and a timed-out implementation worker remain in the management history; they are software events, not biological findings.

Production commands enforce pinned sources, fresh owned output directories, input/code/runtime hashes, and explicit scoped review gates. Per-fit progress and per-world artifacts are retained; accepted directories must never be overwritten. The final package copies all300 original CV model replays and their original code snapshots **without refitting**, along with an explicit label map. No services, dependencies, commits, or pushes are required by this study.
