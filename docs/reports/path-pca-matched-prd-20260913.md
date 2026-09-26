# PRD: matched PCA versus non-PCA path-component experiment

Status: proposed exploratory experiment for the next session; no new biological fitting in this planning session. Prepared 2026-09-13.

## Problem Statement

Hongyi wants to know whether the latest simple path-component predictor underperforms PCA. Existing percentages do not answer that question: approximately 83% PCA endpoint accuracy measures start–goal condition separability; the earlier PCA path-component means of 52.1% and 45.3% concern a different segment, source panel, and assembly procedure. The latest 55% balanced accuracy belongs to a 20-recipe preprocessing study that did not include PCA.

There is no matched result showing whether adding PCA helps the latest path-component assay. Describing the best preprocessing recipe as the best method across the project would therefore be misleading. The desired deliverable is not another proposal or leaderboard: it is a completed, bounded experiment, verified results, independently reviewed explanation, and a pull request.

## Solution

Run a small, source-safe **exploratory analysis** comparing PCA and no PCA on the same accepted first-second, raw-rate, variance-floor-scaled path-component inputs. Use identical original source identities, endpoint panels, inner folds, synthetic draw plans, evaluation rows, and downstream logistic-regression tuning budgets. Compare six predeclared recipes, select within training-only CV, and evaluate on the already-exposed historical validation pool without pretending it is new confirmation data.

The operational question is: **On this fixed condition-level pseudopopulation benchmark, does adding a training-fitted PCA projection improve historical-validation probability loss relative to an otherwise matched non-PCA pipeline?** It is not a claim that PCA is universally better, that either method predicts an unknown-label natural trial, or that this study establishes H1.

The minimum experiment uses one pooled second only. It does not reproduce the old per-bin PCA-3/PCA-8 pipeline or rerun endpoint decoding. This limited scope is deliberate: it isolates a missing comparison without reopening a broad preprocessing search. Deliver a plain-language verdict even if the result is negative or mixed.

## User Stories

1. As the researcher, I want a matched PCA/non-PCA comparison, so that I can answer the actual question instead of comparing incompatible percentages.
2. As the researcher, I want the target expressed as a directed interior path component, so that endpoint decoding is not substituted for path information.
3. As the researcher, I want the same five start–goal panels in both methods, so that panel selection cannot favor one method.
4. As the researcher, I want original source and cell identities pinned, so that changing data is not mistaken for improving a method.
5. As the researcher, I want source trials split before assembly, so that derivatives of a trial cannot cross folds.
6. As the researcher, I want every session block's cells and time bins preserved together, so that assembly does not manufacture trial independence.
7. As the researcher, I want missing recordings kept masked rather than zero-filled, so that unrecorded activity is not interpreted as silence.
8. As the researcher, I want identical first-second raw-rate inputs and scaling, so that PCA is the explicit representation difference.
9. As the researcher, I want a PCA dimension rule that works with small panels, so that two-cell panels are not silently dropped or mislabelled PCA-8.
10. As the researcher, I want PCA and scaling fitted only on each training fold, so that evaluation recordings cannot shape preprocessing.
11. As the researcher, I want equal L2 tuning budgets, so that one method does not win simply by receiving more optimization attempts.
12. As the researcher, I want the historical winning raw recipe retained as an anchor, so that the new implementation can be checked against known results.
13. As the researcher, I want matching source-draw and evaluation manifests, so that method differences are paired rather than Monte Carlo accidents.
14. As the researcher, I want recipe selection frozen before the new evaluation stage, so that the historical score cannot pick the winner again.
15. As the researcher, I want probability loss as the primary measure and balanced accuracy as a secondary measure, so that confident mistakes are not hidden by a percentage.
16. As the researcher, I want results for all six recipes, so that an unfavorable method or setting cannot disappear from the report.
17. As the researcher, I want individual endpoint results and removal diagnostics, so that dominance by 6→1 is visible.
18. As the researcher, I want the number of retained PCA components and input features reported, so that PCA's actual compression is understandable.
19. As the researcher, I want source-coherent shuffled-label controls that repeat selection, so that the procedure's search opportunity is represented under the null.
20. As the researcher, I want paired source-resampling sensitivity, so that uncertainty about scarce recordings is not replaced by synthetic-row counts.
21. As the researcher, I want singleton pools and serial-dependence limitations disclosed, so that sensitivity summaries are not sold as biological confidence intervals.
22. As the researcher, I want available nuisance information audited, so that method comparison is not presented as exclusion of gaze, history, or task confounds.
23. As the researcher, I want positive-signal and no-signal software checks, so that implementation failure is distinguishable from a nonpositive biological result.
24. As the researcher, I want saved projections, scalers, coefficients, probabilities, and lineage, so that every reported comparison can be verified without fitting again.
25. As the researcher, I want failures and retries retained separately, so that operational recovery cannot inflate scientific evidence.
26. As the researcher, I want long runs to use bounded console output and durable file logs, so that logging cannot repeat the previous output-cap failure.
27. As the researcher, I want independent code and scientific reviews before fitting, so that errors are caught before spending the experiment budget.
28. As the researcher, I want independent result and claim reviews after verification, so that an attractive score cannot outrun what the data support.
29. As the researcher, I want a short child-friendly explanation alongside technical methods and plots, so that I can explain the outcome to my supervisor.
30. As the repository owner, I want code, methods, report, and lightweight verification evidence in a PR, so that the result is reviewable and durable.
31. As the repository owner, I want raw data and full model artifacts kept local and ignored, so that delivery does not expose private recordings.
32. As the next-session agent, I want explicit gates and completion criteria, so that I can run through results, review, documentation, and PR rather than stop after implementation.
33. As the repository owner, I want existing work and accepted artifacts preserved, so that this experiment does not damage another session's work or rewrite history.
34. As the researcher, I want a conclusion that distinguishes a higher point estimate from robust biological evidence, so that neither improvement nor failure is overstated.

## Implementation Decisions

### Scientific contract and source boundary

- This is a new, explicitly authorized **exploratory matched-method study**, not continuation of a historical pending run or confirmation. Protocol choices below are synthesized defaults for prefit review, not hyperparameters personally selected by Hongyi. Record any justified amendment before new biological fits; do not adapt after inspecting new outcomes.
- Reuse the accepted exported ten-bin count/exposure/mask tensor and frozen source/fold manifest. Check hashes against the accepted export and manager records. Prefer this validated export over reopening raw mixed-split files.
- Preserve the target `D_N_C_M__N_C_B`: presence among all interior corridor runs after removing the first and last runs. Preserve endpoints 2→1, 3→1, 4→1, 5→1, and 6→1, their separate cell panels, original train/validation assignments, and three inner folds.
- Expected support is 147 training plus 41 historical-validation original sources, 49 distinct selected-unit IDs, 13 sessions, and 756 observed unit–source pairs. Preserve the accepted behavior/QC/duration rules and exclusions. Eligibility previously used historical-validation class support; do not rebrand it as untouched or wholly training-only cohort discovery.
- The independent source object is the original behavioral trial, nested within session. Derivatives, resampled copies, and adjacent bins are not independent observations; serial independence is unresolved. Reuse session-block assembly and matched known-label construction for both methods, including evaluation. This defines condition-level response-distribution separability, not one simultaneously recorded population trial.
- Audit task/cue semantics, provenance, support, missingness, and available nuisances before fitting. Record unresolved metadata as limitations without guessing them. Stop for an input-identity, timing, label, or alignment contradiction that invalidates the fixed assay. Missing verified simultaneity or gaze alone does not block this explicitly narrower descriptive method comparison, but it blocks stronger claims.

### Six-recipe comparison

- Aggregate native counts and exposures over exactly `[0,1)` seconds into one rate per unit. Both arms use the existing training-only variance-floor scaler on the same flattened features. Do not change to ordinary z-scoring, log counts, variable cue tails, or temporal features in one arm only.
- Non-PCA arm: scaled rates directly into L2 logistic regression.
- PCA arm: the same scaled rates, followed by a deterministic, training-only full-SVD PCA retaining the smallest number of positive-variance components reaching at least 90% of total training variance, followed by the same L2 logistic regression. Use no whitening and no extra post-PCA component scaling. The 90% threshold is a fixed engineering choice, not a discovered biological optimum; record achieved variance and dimension in every fit.
- The component count is fitted separately per endpoint and training fold, then refitted on all original-training sources after selection. Never clamp to an impossible named dimension, drop a panel for having fewer than eight cells, or learn the dimension from held-out data. A completely constant training matrix uses an explicit intercept-only fallback shared by the arms, with the fallback recorded; numerical-rank tolerance and retained-variance boundary handling must be frozen and tested before biological fitting.
- Both arms use exactly average-loss L2 λ in `{0.01, 0.1, 1}`: six candidate recipes total. Use the established average-loss convention with an unpenalized intercept and `C = 1 / (λ × training-row count)`. Preserve solver settings unless a documented prefit numerical repair is required; report convergence rather than silently accepting failed fits.
- Primary comparison is between independently CV-selected raw and PCA recipes. Select one global λ per arm by equal-endpoint/equal-fold mean balanced logloss over the existing three inner folds, using seed 0 and 128 training rows per class per model. Freeze a deterministic tie rule: scores within 1e-12 prefer larger λ. The same rule applies to null worlds. No per-endpoint historical tuning is allowed.
- The fixed-λ matched comparisons are mandatory descriptive diagnostics, especially λ=1, so readers can separate a representation change at equal penalty from differing selected penalties. The historical raw one-bin/floor/λ=1 recipe is included, not added as another search family.
- Preserve the existing CV product-size cap and deterministic sampling fallback; record where evaluation is exact versus sampled. Use the full tractable historical-validation class products with half the total weight per class. All arms must share source-draw/evaluation lineage and weights at each endpoint/fold/seed.
- Reproduce the saved historical raw anchor on matching inputs before interpreting PCA results: historical Δlogloss approximately +0.0285834 and balanced accuracy 0.55. Compare detailed saved probabilities/metrics at predeclared tolerances, not merely rounded aggregate agreement. A mismatch is an implementation/provenance gate failure, not scientific evidence.

### Metrics, controls, and stopping

- Primary comparative statistic is the equal-endpoint mean of **raw-selected balanced logloss minus PCA-selected balanced logloss** on historical validation; positive favors PCA. This compares the two specified training-selection procedures, not all possible PCA methods.
- Report each arm's absolute loss and Δ versus the balanced constant-0.5 baseline. Secondary outputs are balanced accuracy, Brier score, AUROC, class recalls, train/CV gaps, source coverage, dimensions, convergence, and runtime. Higher accuracy does not override the primary loss criterion.
- Freeze the six recipes and selection policy before observed fitting, and record both selected λ values before the new historical evaluation stage. The historical pool was already exposed, including the raw anchor; the freeze is procedural discipline, not restored independence.
- Run 100 ordinary and 100 temporal-half source-label permutation worlds. Reuse established session×endpoint×split×training-fold strata, with training-defined temporal halves for the latter. Preserve source blocks, use paired label maps and draws across arms, and redo all six fits and both arm selections in each world. Save label movement and pure-stratum diagnostics.
- For each selected arm's baseline-relative score, report inclusive plus-one null tail references and the conservative maximum-over-six family reference. Freeze near-tie numerical handling before running. These are exploratory, assumption-dependent no-path-association references. **A shuffled-label p-value is not a test that PCA and raw have equal predictive risk.** Do not convert it into a PCA-superiority p-value. No confirmatory superiority inference is specified.
- Run 200 paired source-stratified bootstrap sensitivity refits of the two frozen selected recipes, sharing source resamples and retaining lineage. Report each arm and their paired difference. This is fixed-selection sensitivity, not selection-adjusted confidence intervals. Expose singleton pools, especially point/influence-only endpoints 2→1 and 4→1; copying one source cannot estimate unobserved variability.
- Repeat the two selected recipes with assembly seeds 1 and 2, without reselection. Report leave-one-endpoint-out point comparisons and paired leave-one-session-out refits at fixed selected recipes, comparing only common remaining endpoints; disclose any panel lost through removal. These are sensitivity checks, not independent replications.
- Existing nuisance-only failure is not confound exclusion. This bounded comparison adds no new nuisance-fitting family and claims no increment over unmeasured gaze/history/state. Report unresolved nuisance metadata and any existing comparator only as unmatched historical context.
- Use deterministic declared seeds for every stage, freeze fit counts and resource/time budget after a synthetic runtime estimate, and keep complete attempt accounting. Default to the retained CPU runtime with two computational threads; no dependency installs or GPU training are needed. Do not increase candidate/control counts in response to results. If the planned job exceeds the resource budget, stop and record the incomplete status rather than silently changing the protocol.
- No minimum biologically worthwhile effect has been agreed. Report effect sizes and fragility; do not claim absence, equivalence, universal superiority, or confirmatory H1 support regardless of p-values. A numerical advantage that is small, endpoint-dominated, or source-sensitive must be described that way. A completed negative study is a successful delivery.

### Reuse, artifacts, and delivery

- Reuse the accepted source-tensor loader, temporal aggregation, scaler, draw-plan/materialization, product evaluation, metric, permutation, bootstrap, and lineage machinery. Implement the smallest explicit PCA fit/forward/serialization extension and bounded comparison orchestration needed; do not clone the large historical driver or rewrite its frozen 20-arm policy.
- Preserve existing replay behavior and historical CLI defaults. If a new replay schema is needed, version it, store full scaler/PCA/decoder state and feature order, and retain backwards compatibility. Replay must not call scaler, PCA, or classifier fitting.
- Store experiment outputs in a fresh owned ignored directory, never inside an accepted historical run. Capture input hashes, Git revision/dirty state, exact executed code snapshot, environment versions, full configuration, seeds, shapes, exclusions, draw plans, probabilities, model state, and all attempts. Keep summaries compact; route per-fit output to durable files with bounded console summaries.
- Use prefit independent code/science review gates, then postfit independent numerical/claim/report review. The parent remains sole writer; reviewers are fresh-context read-only agents. Resolve findings and review revised claims before delivery. AI review is not laboratory metadata verification or human peer review.
- Deliver a concise human report, offline self-contained illustrated HTML, machine-readable summary, agent evidence index, saved-artifact verifier, tests, and reviewed methods. Lead with the primary paired effect and per-endpoint results; include both selected and all-six-recipe tables and explain why the old endpoint and segment PCA numbers are not matched benchmarks. Do not equate retained PCA variance with path information or intrinsic brain dimensionality.
- Final delivery is a real pull request linked to the issue, containing code, protocol, documentation, and lightweight verification/review evidence, with exact commands and local artifact inventory. Exclude raw data, full models, environments, and bulky generated output. Do not auto-merge. Run-to-completion means the next session executes through results and review, not that scientific validity gates may be bypassed.

## Testing Decisions

**Seam sketch:** use the existing source-tensor → fit/evaluate → saved-artifact replay → report pipeline. This sketch was presented to Hongyi in chat for expectation checking; no explicit reply confirming the seams has been recorded. No new service/API or broad test framework is proposed.

Good tests check observable outputs and safety properties, not incidental helper structure, mocked call counts, or a desired biological result. Use the existing unittest-based synthetic experiment and corruption-check patterns, at the highest useful boundary.

1. **Matched experiment integration:** a tiny invented-data run exercises all six candidates, three source-held-out folds, deterministic per-arm selection, historical evaluation, miniature null/bootstrap stages, and complete saved replay. Assert matched lineage/weights and expected candidate/stage coverage rather than implementation details.
2. **Training-only boundary:** perturb held-out values dramatically and confirm they cannot change fitted preprocessing or selected training-CV recipes. Preserve existing poisoned-original-test and unselected-source rejection checks; no new raw export is required for the actual study.
3. **PCA contract:** test known low-rank and full-rank synthetic matrices, small endpoint panels, constant inputs, dimension/variance reporting, no whitening, and stable forward predictions. A full-rank orthonormal rotation with identical average-loss L2 should reproduce the non-PCA classifier's predictions within numerical tolerance; this is a software diagnostic, not a seventh biological recipe. It detects accidental post-PCA rescaling or a changed penalty geometry.
4. **Source and metric invariants:** retain block coherence, missing-mask refusal, count/exposure conservation, source-disjoint folds, balanced exact-product weights, and row-duplication regularization invariance. Independently calculate a small weighted loss/paired difference, including confident errors and extreme-probability clipping.
5. **Selection and controls:** synthetic worlds must repeat each arm's tuning and deterministic tie policy; source resamples are paired across arms. Verify no accidental reuse of the observed λ in selection-aware null worlds. Test inclusive exceedances, all ties, pure strata, and zero actual label movement without claiming successful null randomization.
6. **Forward-only verification and corruption rejection:** forbid all fit entry points while regenerating predictions, metrics, selected settings, null summaries, paired bootstrap summaries, and report tables. Tamper independently with PCA components, feature order, lineage, a probability, a selected λ, and an aggregate; each corrupted artifact must be rejected. Reuse the existing saved-model/lineage verifier approach and document any shared-helper limitation.
7. **Known-signal checks:** deterministic positive and no-signal fixtures test that the pipeline can expose a designed signal and that the baseline is correctly computed. Do not require one finite random no-signal sample to be exactly at chance or guarantee PCA beats raw on every fixture. Synthetic sensitivity is not proof of biological assay power.
8. **Historical compatibility:** verify the raw anchor against accepted saved predictions, and retain focused existing software/replay checks for changed helpers. Run proactive LSP diagnostics before builds, the repository software suite in the retained isolated runtime, and session diagnostics before final delivery. Timeouts/unavailable checks are inconclusive, not passes.
9. **Report/PR acceptance:** generate tables and plots from saved summaries without fitting, assert agreement with verified values, check offline rendering/link validity and plain-language metric/task labels, review the complete PR diff, and scan the staged artifact set for private/bulky files. Scientific statements must survive independent review.

## Out of Scope

- New biological fitting in the current planning/handoff session.
- Endpoint decoding, CEBRA, artificial agents/H2, new model families, encoder training, or a general benchmarking framework.
- Repeating old PCA-3/PCA-8 ten-bin experiments, testing multiple PCA thresholds, temporal-bin searches, whitening, or transform/scaler searches. These would be separately justified follow-ups, not opportunistic extensions.
- New targets, graph definitions, endpoint selection, a 6→1-only rescue, new source splits, expanded selected-cell scope, external data transfers, or new original-test evaluation.
- Label-free deployment, exact same-trial population predictions, simultaneous covariance/dynamics, full-path reconstruction, causal planning/intention, H1b dimensionality, or H1 absence/equivalence claims.
- Treating shuffled labels as a matched-method equality test, or source sensitivity percentiles as confirmatory confidence intervals.
- Host upgrades, new services/viewers, package installs, raw-data commits, overwriting accepted outputs, deleting other sessions' work, or automatically merging the final PR.

## Further Notes

### Execution and done criteria

The user's requested next-session endpoint is **run the experiment → obtain results → independently review code/science/results → document → return a PR**. The next session is authorized to perform this bounded exploratory work after its prefit gates; historical notes saying an earlier completed study has no queued fits do not prohibit this new request. They do prohibit silently restarting old searches.

Proceed through: current-state/input audit; protocol freeze and implementation; synthetic checks and independent prefit reviews; observed CV and selection freeze; historical evaluation and declared controls; complete forward-only verification; independent result/report review and fixes; documentation and PR. If a gate cannot be satisfied, report the concrete blocker and retained evidence instead of claiming the experiment completed. No additional user interview is required for the synthesized defaults; a materially different experiment requires renewed scope agreement.

The six-recipe boundary is intentional. Adding PCA to the existing one-bin pipeline answers a useful narrow question while avoiding another open-ended search. A win here would not show that the earlier per-bin PCA method was reproduced; a loss would not reject PCA generally.

### Supporting authorities

- [Workspace and recovery guide](https://github.com/Hong-yiii/neuro_science/blob/main/docs/workspace.md). Live GitHub verification on September 13 confirms [PR #5](https://github.com/Hong-yiii/neuro_science/pull/5) is merged; preserve local work and branch from current remote main rather than relying on an older unmerged-status sentence.
- [Research questions](https://github.com/Hong-yiii/neuro_science/blob/main/docs/research-questions.md) and [analysis contract](https://github.com/Hong-yiii/neuro_science/blob/main/docs/analysis-contract.md).
- [Completed preprocessing agent brief](https://github.com/Hong-yiii/neuro_science/blob/main/docs/reports/path-preprocessing-autoresearch-20260908-agent.md) and [September 9 review](https://github.com/Hong-yiii/neuro_science/blob/main/docs/reports/path-preprocessing-review-20260909.md).
- [PCA segment explanation](https://github.com/Hong-yiii/neuro_science/blob/main/learning/place195-pca-and-below-chance-20260908.md) and [cross-study synthesis](https://github.com/Hong-yiii/neuro_science/blob/main/docs/reports/recent-learnings-20260908.md).

The old frozen readable methods use an imprecise square-root shorthand; the implemented transform included a 3/8 count offset. This new experiment uses raw rates only, so the discrepancy must not be propagated as an implemented arm.

Tracker: GitHub Issues for this private repository; apply `ready-for-agent`. That label denotes a specified work item, not scientific approval to skip review gates. The tracker and required label are established from the repository and this request; full interactive skills-configuration scaffolding is not part of this experiment.
