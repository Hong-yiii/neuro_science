# Final review resolution — path preprocessing, 2026-09-08

Owner: parent session; sole code/document writer. This record does not authorize new fits.

## Scientific claims

`science-outcomes-preliminary.md`, `teaching-evaluator.md` and `final-science-results-review.md` establish claim boundaries, not requirements to obtain a positive result. The released narrative explicitly says:

- only2/5 historical endpoint deltas are positive;6→1 dominates, and omitting it reverses the aggregate;
- all four declared null p-values are reported (.168/.356 ordinary; .139/.297 temporal), with the fixed observed CV-selected statistic;
- source-bootstrap quantiles cross0 and are sensitivity only;17/28 validation pools are singletons;
- seed/LSO/bootstrap repetition is not biological replication; nuisance-only fixedλ.1 is not tuned/nested confound exclusion;
- temporal conditional-null movement is limited; true changed-label fractions are separately computed, not confused with the producer's stratum-level `movable_fraction` field;
- no broad H1 success, H1 absence, H1b/H2, intention, mechanism or exact simultaneous-trial claim;
- condition-level pseudopopulations remain a valid central assay, without per-neuron-significance gating.

The scientific review's stale-draft note was resolved by inserting the completed control values. Fitting completion and forward-verification completion are distinct; full verification subsequently passed.

## Execution/code gates

Initial blockers on source allowlists, metadata, output ownership, code/input provenance, observability and controls were fixed before their scoped biological stages. The final self-contained observed-CV package and explicit label-map gaps were fixed before final inference approval. Original review receipts and original CV/final execution snapshots remain retained; no retrospective rewriting of gate history.

A timed-out implementation child made no biological fits/export. The first final-stage run was externally killed by the runner's20MB console cap, not a statistical failure. The unchanged rerun used a fresh directory and file-routed logs. `FINAL-ATTEMPT-1-FAILURE.json` records the failed prefix, missing last267 coefficient packages, any unknown in-flight fit, the >20MB routing regression, and identical decompressed observed/control predictions. Repeated attempts are not extra null worlds.

## Verifier findings

`verifier-integration-evaluator.md` correctly identified missing checks of bootstrap resampling/quantiles, secondary metrics, and saved lineage. Parent added independent seed/stratum bootstrap regeneration, lineage/hash/summary/quantile checks; training/evaluation BA/logloss/Brier/AUC and probability summaries; exact regenerated source-manifest/plan comparisons; nuisance features and metrics; seed/influence aggregates and tie-order selection.

Synthetic corruption checks reject wrong quantiles, resampling seed, saved lineage and Brier scores. An extreme-probability test exposed the verifier's clipping-convention mismatch; corrected to clip probability before log/Brier, while AUROC uses raw probabilities. Fitter and scientific policy never changed. Follow-up reviewer returned No findings;820 bounded forward checks passed.

Full verification then completed (`bd3e89a26`):82,283 model forward replays, zero new fits, all200 null worlds and200 bootstraps. Verifier SHA256`b8b1030d6e322faf0d8e3e6fdf19e5aec1e6a0a5cb0ab9474cf6ede2385c3dea`; original fitter SHA256`0b49c6d84e4b59842e4d64d8f6e18e075811590bd11dcd2834f1e0555b32782f`. Test count is19 across three files, of which13 are in the new study test file; the review's13-versus19 note reflects scope, not conflicting test results.

## Delivery checks

Final teaching reviewer returned No findings. Final code/evidence reviewer verified hashes/counts/controls and found one low-severity HTML defect: missing spaces after three closing bold delimiters rendered literal Markdown. Parent fixed the source Markdown, not the CommonMark renderer, and added an exact strong-label regression. The old HTML failed this new check as expected; regenerated HTML passed (`bdb0ea7b5`,2s, exit0). `report-validation.json` confirms20 table rows,4 accessible embedded SVGs,0 duplicate IDs/external resources,5 local links, and all4,193 original run-file hashes unchanged. The report also explicitly distinguishes time pooling within each unit from averaging neurons: one-bin6→1 remains23-dimensional; five-bin is115, not a brain-dimensionality estimate.

All four PNG previews were visually inspected. The null legend was moved outside the plotting area. The SVGs/styles are embedded; no browser scripts or externally loaded resources are required. The report table checks all20 candidate rows against saved metrics. Original4,193 run-file hashes remain unchanged after report generation. Original report-validation receipt is retained under its before-format-fix label.

Final follow-up `e81824c5` returned **No findings** after checking the corrected labels,23/115-feature clarification, report-validation receipt and unchanged fitter/verifier hashes. Final teaching and corrected code/evidence release gates are satisfied. Portable report/code packaging is a subsequent byte-copy/check step, not another scientific analysis.

LSP remains a disclosed tooling limitation: repeated primary/scoped scans timed out (final bounded four-file sweep0confirmed/4unconfirmed). Do not claim type-clean confirmation. Runtime compilation,19 focused tests, full numerical verification and independent review provide separate evidence. No environment/tooling configuration was changed to hide these timeouts.
