major — docs/reports/path-pca-matched/README.md:36 — generated report/HTML/verification package is advertised but absent at review time

Verified evidence: `README.md:36-38` links `report.md`, `report.html`, `summary.json`, `verification.json`, and `report-evidence.json`; `evidence.md:26-27` lists the verification/report receipts as evidence; direct filesystem inspection found only `outputs/path-pca-matched/biological-attempt-01/summary.json` among those target artifacts, and no `docs/reports/path-pca-matched/report.md`, `report.html`, `summary.json`, `verification.json`, or `report-evidence.json`. The numerical review also states the full verifier/report were not present yet (`reviews/postfit-numerical.md:36-41`). Impact: final package approval cannot be granted from the README/generator alone; the rendered human report/offline HTML and full replay receipt still need review. Minimum fix: complete forward-only verification and report rendering, then re-check the actual `report.md`, `report.html`, `summary.json`, `verification.json`, and `report-evidence.json`.

## Approval / revise decision

**Revise before final approval.**

I approve the current claim framing in `README.md` and the report generator’s planned claim ceiling, but final approval is conditional on checking the real generated Markdown/HTML and full verification receipt after replay completes.

## Verified claim checks

- Small matched loss advantage is correctly stated: raw `0.6645637835`, PCA `0.6575408846`, raw−PCA `+0.007022899`.
- Both selected λ=1 and both have mean BA `0.55`.
- Endpoint framing correctly separates:
  - largest PCA-over-raw contribution: `5→1` raw−PCA `+0.025559`, while both remain worse than `.5` baseline;
  - absolute baseline-relative dominance: `6→1`; omitting `6→1` gives raw Δ `-0.037872`, PCA Δ `-0.030335`.
- Source bootstrap sensitivity is correctly limited: paired percentiles `[-0.011444, +0.005029, +0.023426]`, spanning both signs and not a CI/superiority test.
- Null references are correctly described as no-path-association arm-vs-baseline references, not PCA-superiority p-values.
- Pseudopopulation/lab-metadata limits are explicitly stated: not simultaneous trials, exposed validation, unresolved gaze/history/task/recording metadata, no H1/H1b/H2 or absence/equivalence claim.

## Residual risks

- Actual rendered `report.md`/`report.html` were not available, so numeric tables, offline HTML accessibility/rendering, and receipt hashes remain unchecked.
- Verifier shares some helpers by design; even after receipt exists, this remains software replay evidence, not lab metadata or human peer review.