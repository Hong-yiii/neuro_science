No findings.

## Independent postfit numerical/code review

**Decision:** approve the bounded numerical result/code for the exploratory matched PCA/raw comparison, with the stated limitations. Do **not** treat this as final package acceptance until the parent’s full forward-only verifier receipt exists.

### Verified numerical facts

- Saved selected-arm effect from raw predictions:
  - Raw baseline Δ: `0.028583397042444635`
  - PCA baseline Δ: `0.035606295992569856`
  - Raw loss − PCA loss: `0.007022898950125221`
  - Equivalent losses: raw `0.664564`, PCA `0.657541`
- CV selection recomputed from `observed/cv_metrics.csv.gz`:
  - raw: `t1_raw_rate_variance_floor_l2_1`
  - PCA: `t1_raw_rate_variance_floor_pca90_l2_1`
- All-six historical coverage verified:
  - 6 candidates × 5 endpoints = 30 validation metric rows
  - all converged
  - 30 prediction groups present
- Anchor verified from artifact:
  - `anchor.json` status `passed`
  - maximum probability difference `0.0`
- Control/accounting checks:
  - fit budget sums to `26,266`
  - null worlds: 100 ordinary + 100 temporal-half
  - bootstraps: 200
  - assembly seeds: 2
  - leave-session refits: 13
- Null tails recomputed from `nulls.json` matched `summary.json`.
- Bootstrap quantiles recomputed from `bootstrap.json` matched `summary.json`.
- Bounded artifact hash spot-checks passed for summary, observed predictions/metrics/models, nulls, bootstrap, and anchor.

### Important limitations

- Full forward-only biological verifier receipt was not present yet; parent is running it.
- I did not rerun biological fits or duplicate the full replay.
- Historical validation is exposed; this remains descriptive/exploratory.
- Bootstrap/source resampling spans both signs for paired difference: `[-0.011444, +0.005029, +0.023426]`; not a confidence interval or superiority test.
- Source/session dependence, singleton validation pools, unresolved simultaneity/task/gaze/history metadata remain material claim limits.
- Report/HTML artifacts are not yet generated in `docs/reports/path-pca-matched/`; current README/evidence references should be treated as pending until verifier/render receipts exist.