blocker — scripts/place195_matched_pca.py:31 — Hash-bound prefit gate references missing `scripts/test_matched_pca.py`.

Verified evidence: `CODE_FILES` includes `scripts/test_matched_pca.py` at lines 31–39, but `find **/*matched*pca*` found only `scripts/place195_matched_pca.py` and `scripts/verify_matched_pca.py`. `code_hashes()` hashes every listed file at line 95, and `main()` computes those hashes before synthetic/run stages at line 311. Impact: synthetic budget smoke checks and biological run gate cannot execute as written. Minimum fix: add/rename the test file or correct `CODE_FILES`, then refresh hashes/reviews before fitting.

limitation — docs/reports/path-pca-matched/protocol.md:7 — Primary PCA-vs-raw effect is descriptive on exposed historical validation, not confirmatory PCA superiority.

Verified evidence: line 7 defines the estimand as equal-endpoint raw-selected loss minus PCA-selected loss; line 42 says no confirmatory PCA-superiority test is specified; line 64 states historical validation was already exposed. Impact: a positive point effect can answer this bounded matched-method question only for this frozen benchmark. Minimum fix: report as exploratory/descriptive and require new unexposed sources for confirmatory claims.

limitation — docs/reports/path-pca-matched/protocol.md:21 — Source scarcity and nesting remain the main inferential boundary.

Verified evidence: line 21 says original trials are nested in session, serial independence is unresolved, and synthetic rows are not sample sizes; lines 15–19 show endpoints as small as 2–3 validation sources and 1 session block. Impact: endpoint/session influence can dominate, especially 2→1, 4→1, and likely 6→1. Minimum fix: lead with per-endpoint, leave-one-endpoint/session, and fixed-selection source sensitivity; do not present bootstrap quantiles as animal/source CIs.

limitation — docs/reports/path-pca-matched/protocol.md:29 — PCA 90% rank rule has small-panel boundary risk.

Verified evidence: line 29 freezes rank tolerance and 90% cumulative-variance retention; lines 15–17 include 2- and 3-unit panels. Impact: retained component count may change discontinuously across folds/endpoints and may discard low-variance path signal or retain nuisance variance; retained variance is not neural dimensionality. Minimum fix: record singular values, tolerance, numerical rank, retained components, achieved variance, and fixed-λ diagnostics exactly as specified.

limitation — docs/reports/path-pca-matched/protocol.md:40 — Permutation and bootstrap outputs are reference/sensitivity checks, not matched-risk equality inference.

Verified evidence: line 40 defines label-world controls; line 42 says these are no-path-association references, not tests that PCA and raw have equal predictive risk; line 44 says bootstrap quantiles are fixed-selection sensitivity, not confidence intervals. Impact: null tails cannot be used as a PCA-superiority p-value. Minimum fix: keep permutation interpretation arm-baseline-relative and disclose actual label movement, pure strata, singleton pools, and fixed-selection status.

limitation — docs/reports/path-pca-matched/protocol.md:54 — Budget is itself a gate, not a tunable analysis parameter.

Verified evidence: line 54 freezes 26,266 fits, 2h wall time, 10GiB output, and says incomplete attempts must be retained rather than changing controls/candidates. Impact: exceeding budget means “no completed bounded result,” not permission to reduce nulls/bootstrap or pool retries. Minimum fix: record invented-data runtime/resource estimate after the missing-test blocker is fixed and before biological fitting.

Approve/revise opinion: revise the operational hash manifest blocker before any fit. Scientifically, the protocol is approvable for the bounded descriptive study if all stated gates pass and claims stay within the exposed, condition-level pseudopopulation ceiling.

Residual risks: unresolved lab metadata remain material—cue/goal/start semantics, simultaneity, gaze/view/heading/action/history, animal/anatomical provenance, and serial exchangeability.