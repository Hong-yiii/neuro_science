# Issue #6 — matched PCA/raw exploratory protocol

Prepared 2026-09-13, before new biological fits. Authority: [issue #6](https://github.com/Hong-yiii/neuro_science/issues/6). These are synthesized prefit defaults, not previously discovered optima. This directory will record amendments, gates, results and reviews separately.

## Question and measurement

On the fixed condition-level pseudopopulation benchmark, does training-fitted PCA improve historical-validation balanced probability loss relative to otherwise matched raw rates? Primary effect: equal-endpoint mean **raw-selected loss minus PCA-selected loss**; positive favors PCA. This compares two specified training-selection procedures, not all PCA methods or unknown-label natural trials.

Reuse the accepted export `biological-20260908T115508Z/export/source_tensors.npz`, SHA256 `6fa3e836fad756b6007f69115de5e6758c7238cfb9a786b4a4e7a0d4ac849e3a`, and source/fold manifest SHA256 `36c72e8f1f9c55ca3af9458963cf1e1062c8803cb57b33af29df4502e46c2b2f`. Strict loader checks source/cell/fold identity, masks, finite integer counts, exposures, export receipt and panel support. No raw re-export or original-test evaluation.

Target `D_N_C_M__N_C_B` is presence among **all interior corridor runs after removing first/last runs**, not one midpoint, endpoints, or full-path reconstruction. Preserve accepted behavior coverage/valid-absence rules, empty QC flags, cue duration [1,1.5] s, selected195 scope, and session×endpoint eligibility (≥3 train/class, ≥1 historical-validation/class). The two earlier sub-second exclusions stay excluded. Eligibility used validation support; this is not wholly training-only cohort discovery.

| Endpoint | Session blocks | Unit inputs | Train | Historical validation |
|---|---:|---:|---:|---:|
| 2→1 | 1 | 2 | 12 | 3 |
| 3→1 | 3 | 14 | 31 | 11 |
| 4→1 | 1 | 3 | 9 | 2 |
| 5→1 | 3 | 12 | 33 | 8 |
| 6→1 | 6 | 23 | 62 | 17 |

Total: 147 train + 41 validation original sources, 49 distinct units, 13 sessions, 756 observed unit–source pairs. Some sessions/units occur in multiple panels. Independent source object: original behavioral trial nested in session; serial independence is unresolved. Match known path labels across sessions, preserving every session block's cells and time bins together. Missing measurements remain masked, never zero-filled. These are not simultaneous 49-unit trials and synthetic row counts are not sample sizes.

## Six recipes and selection

- Sum native ten-bin counts and exposures over exactly [0,1) s; one raw rate/unit. Do not include variable cue tails.
- Training-only variance-floor scaling: subtract training mean and divide by max(training SD, median strictly positive training SD); all-constant scale=1.
- Raw arm: scaled features → L2 logistic regression.
- PCA arm: same scaled features → deterministic full SVD on centered training matrix → L2 logistic regression. No whitening or post-PCA scaling. Economy-shaped SVD computes the full singular spectrum, not randomized/truncated approximation. Canonicalize each component sign by its largest-absolute loading, first-index tie.
- Numerical rank: singular value > `eps(float64)*max(n_rows,n_features)*largest_singular_value`. Smallest positive-rank component count reaching cumulative variance ≥0.9−1e−12, capped at numerical rank. Variance denominator includes the full singular spectrum. Record all singular values, tolerance, rank, components, achieved variance, input dimension and fitted means. The 90% rule is engineering, not brain dimensionality or percentage of path information.
- A completely constant matrix is intercept-only in both arms. Raw's scaled zero columns already enforce zero coefficients; PCA uses a single zero placeholder column and explicitly records zero retained components. Balanced training implies probability .5. No panel is dropped for being smaller than eight cells.
- Exactly λ∈{.01,.1,1} per arm; six recipes. Average-loss L2, unpenalized intercept, sklearn `C=1/(λ*N)`; existing lbfgs/max_iter=1000/random_state=0/tol default retained. Convergence warnings/nonconverged fits stop the attempt, not disappear from reports.
- Original source folds remain unchanged. Every inner fold learns its scaler/PCA using only its training rows. Seed0, 128 training rows/class. All six recipes share deterministic source draws, evaluation lineage, and weights. CV: exact class products up to 10,000/class; otherwise 2,048 deterministic draws/class. Historical evaluation: full tractable class products. Half the total weight/class.
- Select one global λ per arm by equal-endpoint/equal-fold CV loss. Scores within 1e−12 of the minimum prefer larger λ. Write both selected recipes before new historical evaluation. No per-endpoint tuning. Keep all-six and fixed-λ paired results, especially λ=1.
- Historical raw λ=1 anchor must reproduce detailed saved row identities, weights, probabilities (rtol 1e−9, atol 1e−10), and aggregate Δlogloss .028583397042444624 (atol 1e−10) before interpreting PCA. It is one of the six observed fits, not an extra search family.

## Evaluation and falsification

Primary: paired loss difference. Also absolute loss and Δ=`log(2)−loss` vs balanced .5 baseline; BA, Brier, AUROC, class recalls, train/CV gaps, source coverage, dimensions, convergence, runtime. Use existing probability clipping [1e−9,1−1e−9] for loss/Brier. Accuracy cannot override loss selection.

100 ordinary label worlds, seeds 50000–50099; 100 temporal-half worlds, seeds 70000–70099. Reuse source-coherent session×endpoint×split×innerfold (train only) permutation strata, adding temporal halves defined by training trial-index median for the second family. Pair label maps and source draws across arms. Repeat all six CV recipes and both selections, then all six historical recipes in every world. Save actual label movement, pure strata/sources and original audit fields; the old `movable_fraction` does not mean fraction of labels actually changed.

For each observed selected arm's baseline-relative Δ, report inclusive plus-one selected-policy and max-over-six null tail references. Count null≥observed−1e−12 as an exceedance. These are assumption-dependent no-path-association references, **not tests that PCA and raw have equal predictive risk**. No confirmatory PCA-superiority test is specified.

200 paired source-stratified bootstrap refits, seeds 90000–90199, session×endpoint×split×label strata; two fixed selected recipes, no reselection. Share source resamples and seed0 draws. Report each arm and paired-difference percentiles 2.5/50/97.5. These are fixed-selection sensitivity quantiles, not selection-adjusted/animal confidence intervals. Singleton pools cannot estimate missing variability; especially endpoints 2→1 and 4→1 are point/influence-only.

Repeat the two fixed recipes on assembly seeds1/2 without reselection; historical evaluation only. Report leave-one-endpoint-out point effects and paired leave-one-session-out fixed-recipe refits, removing corresponding sources and columns. Compare common remaining endpoints and disclose panel loss. These overlapping resamples are not independent replications.

No new nuisance-fitting family. Audit existing trial index, cue duration, selected/QC history and candidate recording labels. Cue/goal/start semantic confirmation, verified simultaneity, admissible gaze/view/heading/action/history/state and animal/anatomical provenance remain unresolved laboratory metadata. No new contradiction is inferred from absence of metadata. Stop on an input-identity/timing/label/alignment contradiction invalidating the fixed assay; missing gaze or simultaneity alone limits claims but does not block this descriptive benchmark.

## Gates, budget and artifacts

Before fitting: synthetic integration/positive/no-signal checks, active diagnostics, independent fresh-context read-only code and science reviews, recorded resolution and hash-bound approval gate. Sole writer is the parent agent. No biological fits in review tasks. Code changes after approval invalidate its hashes.

Budget: default retained CPU interpreter, two BLAS/OpenMP threads, no installs/GPU. Biological completed fit budget **26,266**: observed90 CV+30 historical; 24,000 null; 2,000 bootstrap; 20 assembly; 126 session refits. Freeze resource estimate after invented-data runtime measurement, before approving run. Maximum 2h wall time and 10GiB output; external supervisor timeout provides a further hard ceiling. Stop and keep incomplete attempts rather than changing controls/candidates. Any retry is a new directory with the original failure retained and accounting reported; no pooling of attempts.

Fresh outputs only beneath this worktree's `outputs/path-pca-matched/`. Preserve input hashes, source snapshot, feature order, scaler/PCA/decoder state, labels, probabilities, lineage, fit ledger, code snapshots and hashes, Git revision/dirty state, package versions, seeds, complete configuration, all attempts. File-route per-fit stdout/stderr; bounded console summary only. No daemon/service or external artifact transfer. Worktree is user-requested temporary PR workspace, retained through review; after merge migrate/hash its accepted local outputs to canonical outputs before removal.

Postfit: complete forward-only replay with fitting entry points forbidden; check lineage, training projection properties, probabilities, independent metrics, all selections, nulls, resampling, sensitivity and report values. Test corruption of projection, feature order, lineage, probability, selection, aggregate. Some assembly/metric-summary helpers are shared and must be disclosed. Independently review numerical results, scientific claims, human report and offline illustrated HTML, then resolve findings. AI reviews are not laboratory verification or human peer review.

Delivery: code/tests/verifier, this protocol, report/HTML, machine summary, agent evidence index and lightweight verification/review receipts in a **draft PR** linked to #6. Raw inputs/full models/runtime remain ignored and local. Do not merge without subsequent user agreement.

## Claim ceiling

Historical validation was already exposed, including the anchor; procedural freezing cannot restore independence. No minimum biologically worthwhile effect has been agreed. Report a negative or mixed result plainly, with endpoint/source fragility. No universal superiority, absence/equivalence, causal planning, trial-specific population state/dynamics, H1 confirmation, H1b intrinsic dimensionality or H2 claim. Old ~83% PCA endpoint decoding and old segment PCA percentages are different assays, not matched baselines here.
