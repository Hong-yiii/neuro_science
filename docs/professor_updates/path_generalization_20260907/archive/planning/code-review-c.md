blocker — scripts/place195_path_generalization_phase1.py:1796 — Track-C export does not enforce selected-195 unit scope

Verified: `export_development_cue_counts()` iterates every `access.iter_cue_counts()` row for allowed sources and appends `row["cell_id"]` directly at lines 1796-1841. The CLI only accepts `--allowlist-csv` for sources, not selected cells, at lines 2981-2989. Impact: an authorized export can include unselected cells from the mixed importer, violating the “original selected195 scope” and changing eligibility/models. Minimum fix: require a selected-unit/cell allowlist from accepted artifacts, filter `cell_id` before export, and test with a poisoned allowed source containing an unselected cell.

major — scripts/place195_path_generalization_phase1.py:1853 — export provenance and join/QC audit are incomplete

Verified: manifest records totals, `forbidden_rows_yielded`, split audit, and `allowlist_sha256` only at lines 1853-1862. It does not hash `cue_counts.csv.gz`, `source_trial_splits.csv`, split summary/import paths, or report allowlist sources missing from yielded counts. QC flags are copied at line 1840 but no flag catalogue or exclusion accounting is emitted. Impact: immutable-input provenance and source join/missing/QC handling required by the protocol are not auditable. Minimum fix: add source-set reconciliation, missing/extra reports, QC flag counts/exclusions, and hashes for all export inputs.

major — scripts/place195_path_generalization_phase1.py:1984 — training context eligibility counts rows, not unique source IDs

Verified: `eligible_contexts_train_only()` increments `counts[(endpoint_pair, y)] += 1` for every row at lines 1987-1990. The requirement says eligibility counts must be UNIQUE sources, not unit rows. Export rejects duplicate `(source, cell)` rows, but `fit-track-c-models` accepts any `--development-counts` file and the model function has no local uniqueness guard. Impact: duplicated source rows can make a context eligible and bias fits/null cohorts. Minimum fix: count `source_trial_id` sets per endpoint/label, and test duplicated-source input.

major — scripts/place195_path_generalization_phase1.py:2354 — temporal-half null sensitivity is not implemented in the Track-C model path

Verified: `add_training_temporal_halves()` exists at lines 2275-2294, but `fit_track_c_two_target_family()` calls `coherent_joint_target_shuffle(label_rows, seed=...)` with default strata only at lines 2353-2355. The CLI exposes only `--nulls` defaulting to `0` at line 3004 and has no temporal-half null option. Impact: authorized runs can complete without the required 100 coarse temporal-stratum sensitivity and without immovable temporal-strata reporting. Minimum fix: add a separate temporal-half null family using training-derived halves, default/preconfigure the required count, and emit stratum immovability counts.

Code hashes reviewed:
- `scripts/place195_path_generalization_phase1.py`: `91954431d4cbbd94179ddb2b0907a6f0da7107ab8eb3994438ad06cc66e591c0`
- `scripts/test_place195_path_generalization_phase1.py`: `e77f3068170127b33cbdc150399c02e85cad85a84dbf7a7ec9fd9eadfa45a8fb`
- `docs/reports/path-generalization-prefit-20260907.md`: `27f8181586dae1093441bbcc9dd7eb0b7117a4c799d1b72af3a000f9597290e9`

Verified positives: gated biological Track A/B/C fit/export commands require `--authorized-phase`; `SplitFilteredAccess` is used before cue-count row yield; poisoned-test and endpoint-intercept tests exist and pass; endpoint intercepts are unpenalized and slopes are train-standardized.

Residual risks: review did not run biological fits/exports and inspected saved accepted artifacts only at schema/header level.