# Prefit protocol draft — path preprocessing autoresearch 2026-09-08

Status: frozen scientific protocol v1 before new cue-bin export or biological fitting. User-authorized exploratory methods research; not confirmatory H1. Independent scientific review accepted scope conditional on support reconciliation, exact adaptive axis, and interval downgrades; all three are resolved below. Biological fitting and binned-export execution remain CLOSED until independent code review and synthetic checks. Implementation may proceed now. Read latest new-worktree condition-level contract; pseudopopulations central.

## Question / assay

Can simple count transforms, coarse temporal summaries and variance-controlled scaling improve independent-source **within-endpoint path-component** decoding? Component fixed from previous behavior-only training-support ranking: D_N_C_M__N_C_B, presence among ALL interior corridor runs after removing first and last. No target search or graph changes.

Primary evaluation object: separate condition-level pseudopopulation per fixed endpoint pair. Separate models/cell panels; equal-endpoint aggregate is not pooled endpoint decoding. Same-session cell/bin blocks preserved; no simultaneous195 or individual-unit significance gate. Known component labels used to assemble evaluation rows; not operational unknown-label real-trial inference.

## Data / eligibility / prefit support

Existing accepted PATH track_c_export contains development labels and fullcue counts/durations. No original test evaluation. Use those saved tables to freeze sources; for new bins, reuse reviewed SplitFilteredAccess and V7 bin_events/load_cue_data or equivalent guarded adapter, with only these allowed source/unit IDs yielded.

Primary inclusion: existing accepted behavior-label source, valid present/absent supported_middle label, empty recorded QC flags, finite cue duration in [1.0,1.5] s, all observed selected same-session cells available. Cue inputs exactly [0,1) Ripple-relative seconds; last1.0s boundary excluded. Ten100ms event-count bins are canonical storage. Full count over actual cue can include tail1.0..D; save omitted tail and assert conservation. Event accessor may stream mixed-split file but skips forbidden rows; do not describe physical absence of test-containing-file access.

Fixed context eligibility: at least3 TRAIN sources per class and at least1 existing-validation source per class, based on prefit support/duration metadata only. This deliberately uses historical development-validation support to make a conditional benchmark possible; report it as development-conditioned panel selection, not strictly training-only eligibility or pristine final test.

Parent prefit counts after these filters (independently recheck before freeze):
- 2->1:1 session,2 cells,12 train /3 validation sources.
- 3->1:3 sessions,14 cells,31 train /11 validation sources.
- 4->1:1 session,3 cells,9 train /2 validation sources.
- 5->1:3 sessions,12 cells,33 train /8 validation sources.
- 6->1:6 sessions,23 cells,62 train /17 validation sources.
Total147 training +41 validation sources,49 unique selected units,13 sessions across panels (not147 complete multicell common-population trials). Units/sessions overlap between endpoint panels; do not sum as independent subjects. Authoritative metadata receipt: prefit-support-audit.json; frozen IDs/cells/innerfolds: prefit-selected-sources.json; all source exclusion reasons: prefit-source-exclusions.csv.gz. Earlier parent-behavior-support.json was explicitly before duration/QC filtering (149train). Two train sources excluded for duration<1s:20180705_session01_trial386 (3->1,0.99804s),20180814_session01_trial147 (5->1,0.98303s). No unexplained count change. No additional endpoint search. Stop if recheck differs unexplained; don't relax thresholds after fitting.

## Source splitting / adaptive boundary

- Original train/validation source assignments unchanged and original test prohibited.
- Before neural values, frozen prefit-selected-sources.json contains3-fold inner assignments within each original-training session×endpoint×label pool using stdlib random.Random(20260908), sorted(context), absent/present order, shuffled sorted source IDs then index%3; use these exact assignments, not a new RNG interpretation. All same-source cells/bins remain together. Each pool>=3 means at least1 inner validation/class and2 inner training/class.
- Round1 preprocessing ranking uses only these inner source-held-out CV folds. Save per-fold/session/panel support and exact assignments/hash.
- Original validation neural metrics withheld from researcher decision loop until Round2 candidate family frozen, then used once as **previously exposed historical diagnostic**, never pristine confirmation. Final table may show every declared arm; primary selected candidate must have been chosen using inner CV only.
- Repeated CV folds/seeds are dependent, not independent biological replicates. No posthoc label flipping.

## Round1:18 matched preprocessing arms

Full factorial: temporal bins [1,2,5] × transform [raw_rate, sqrt_rate, log1p_rate] × scaling [standard, variance_floor]. Aggregation is exact sums of canonical100ms bins, rates count/exposure. sqrt_rate is a heuristic compression, not exact Poisson variance stabilization with varying exposure. Full observed exposure1s assures group lengths known.

Scaler fit ONLY training arrays; standard center/std, zero-variance scale1. Variance floor =max(feature SD, median strictly-positive TRAIN SD); if allzero use1. Save means/scales/floored fraction.

Decoder: binary logistic ridge, fixed average-loss L2 lambda=.1, unpenalized intercept. sklearn C=1/(lambda*n_training_rows) if using sum-loss convention; test replication invariance numerically. Per fold/class128 pseudo rows for training, exact validation product if <=10000 combinations/class else fixed2048 draws/class, saved weights/source lineage. Primary fitting/selection/null uses assembly seed0 throughout; seeds1,2 are separately labelled observed-assembly sensitivity and cannot change the selected recipe or primary/null statistic. Apply each seed's identical source draws across every arm. This compute reduction is frozen before outcomes. Exhaustive product preferred for tiny known supports; balanced class weight. Save actual distinct sources used and product-combination counts, not fake sample N.

Primary metric: equal-endpoint, then equal-fold mean delta logloss at fixed assembly seed0 vs balanced endpoint-constant p=.5 (log2). Secondary BA, Brier, AUC and train/CV gaps. Constant chance BA=.5. Endpoints fixed per model, so constant baseline fully controls endpoint identity in this conditional experiment. Include nuisance-only trial-index/cue-duration decoder with identical source draws as descriptive control; no future behavior covariates.

No PCA input in primary18 (hypotheses are count/time/variance). No PCA, diagonal contrast or nonlinear model added in this bounded protocol.

## Round2:one bounded adaptive diagnostic

After full Round1 inner-CV table and evaluator review, select best representation by primary CV delta logloss. Tie-break uses temporal1,2,5; transform raw,sqrt,log1p; scaler standard,floor in that order (strict greater score wins). Keep all18 Round1 arms. EXACT single refinement axis: selected representation's L2 lambda [.01,.1,1] (.1 already present), adding ONLY2 candidates. Parent records winning representation and CV-based rationale BEFORE executing Round2. Final recipe is CV-best across resulting20 candidates, including original18. No residualizer/contrast/PCA/CEBRA extension in this run. If all nonpositive, still complete the bounded estimation-stability diagnostic; no requirement to obtain a positive score. No target/panel/source/window change.

Every null world must repeat this adaptive algorithm: fit18 base candidates, select its OWN best representation by null CV, evaluate that representation at .01 and1, then select its own best20. Do NOT merely fit the observed winner's extra lambdas in every null, which would omit representation selection. Diagnostic validation is evaluated only after each world's CV selection. Also save max-over-that-world's20 validation statistic as a different maximum-selection diagnostic. Assembly seeds1,2 can repeat observed base/refined20 as sensitivity but cannot reopen recipe selection.

## Nulls / uncertainty / results gate

At finalization, run at least100 ordinary source-label permutations coherently within session×endpoint×original split×innerfold (innerfold applies originaltrain), preserving every source's cells/bins and the frozen stratified support. Refit all training-dependent transformations/decoder and redo CV selection inside each null world. For1source/class inner strata, report what can actually exchange. Compare observed CV-selected diagnostic validation improvement to null-selected diagnostic improvements; also maximum over same full candidate family as a conservative selection-aware diagnostic. Report both policies separately, not choose favorable p.

Additionally100 coarse temporal-half conditional permutations if mobile support permits; use boundaries derived from TRAIN trial index and freeze. Preserve label counts; report immobile strata and movement fraction. They are sensitivity checks, not guaranteed serial exchangeability.

Uncertainty: source-stratified bootstrap within session/endpoint/class/split with refitting for frozen selected recipe,200 replicates, seed0 assembly; intervals are empirical source-resampling sensitivity and may be degenerate with1-source pools, not independent-animal CI or pristine population inference. Save endpoint/session leave-block-out influence and real-source support; cannot swap neuron columns to claim session transfer. Keep assembly Monte Carlo variation separate. Endpoints2->1 and4->1 (one session and/or<2 validation sources/class) receive POINT/INFLUENCE DIAGNOSTICS ONLY; no interval-backed repeatability claim. Aggregate intervals including them inherit this limitation, and every bootstrap interval is labelled source-resampling sensitivity, not an inferential CI. Other panels still have single-source session×class strata: report their fraction and do not imply that aggregate class>=2 removes this ceiling. No results-informed stopping/reduction of100+100 nulls or200 bootstraps.

Engineering outcome labels (not supervisor-approved biological effect threshold): improvement only if delta logloss>0, consistent direction across most endpoint panels and above coherent selection null; stronger repeatability if across CV/diagnostic and not one-panel driven. Smallest biologically worthwhile effect unresolved; no equivalence/absence claim. Above-chance on one tiny exact-Q endpoint is not a global win.

## Required software/control checks

- synthetic positive/constant/null inputs; case where distributed weak signal exists despite no single-cell-significance requirement;
- poison originaltest rows and ensure no features yielded; source/endpoint/session joins and masks; boundaries/count/exposure conservation;
- exact validation weights; all source derivatives grouped; no source overlap across folds;
- transforms/scaler unchanged by validation perturbation; coefficient/transform replay from saved numeric arrays; C normalization/replication invariance;
- null source-coherence and perstratum counts; redo candidate selection; save predictions and recompute metrics independently;
- no accepted-directory clobber; failures retained with tracebacks; immutable input/code/config/runtime hashes.

## Observability / runtime

Single code writer, no new dependency, existing ROOT scratch/v6-v9-runtime/bin/python. CPU thread cap2, one GPU task maximum if later authorized. Every stage has start/end status, seed/candidate/fold counts, progress log, exact commands, all attempted runs, elapsed time and loss/score curves. Keep parent, methods, science, data, code and teaching scratchpads persistent.

Outputs only new worktree outputs/path-preprocessing-autoresearch-20260908/<unique-run>/; manager receipts only ROOT outputs/path-autoresearch-management-20260908/. Teaching Markdown/selfcontained HTML must show hypothesis→intervention→matched result→null→interpretation→next step; figures labelled real-source vs synthetic counts. Code/CLI verifier and reproducibility package plus final independent code/science/teaching reviews. Stop all owned jobs at completion; no commit/push/shared-service changes.
