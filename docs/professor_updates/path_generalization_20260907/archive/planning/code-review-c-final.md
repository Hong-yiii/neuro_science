blocker — scripts/place195_path_generalization_phase1.py:1 — reviewed script does not match requested ScriptSHA

Verified: `sha256sum` reports `fe4dc6b57b97e87cee54a1232130d704aeccc13434f2c6c29015553955c18798` for `scripts/place195_path_generalization_phase1.py`, while the task pins `76547bf65aa0a1245df1a66491050e5e21cc01df118105f18111b54608214ac8`. Protocol hash matches. Impact: I cannot approve the requested pinned implementation artifact for export/model execution. Minimum fix: either restore the pinned script or update the requested hash and re-review that exact file.

major — scripts/place195_path_generalization_phase1.py:3831 — Track-C model parsing still falls back to `component_label`

Verified: `per_unit_rows_from_export()` uses `label = row.get(label_col) or row.get("component_label", "")`. For `target_mode="anywhere"` or `"supported_middle"`, a missing/blank target-specific label silently becomes the old middle `component_label`. Impact: malformed or older development-count files can fit the wrong target without failing, violating “model entry no target fallback.” Minimum fix: require the exact `target_label_column(target_mode)` to exist and be valid for each row; only legacy single-target tests should opt into fallback explicitly.

major — scripts/place195_path_generalization_phase1.py:2895 — supported-middle ranking reports/ranks total eligible sources, not gate-qualified train sources

Verified: code sums every session in `eligible_train_source_count_total` and ranking tie-breaks on that field at line 2983. The saved final manifest reports supported_middle as `11` sessions but `507` eligible train sources; summing only `unit_model_train_source_gate_met=true` sessions in the same manifest gives the task’s `267`. Old middle similarly reports `408` total rather than task’s gate-qualified `134`. Impact: frozen selection metadata does not match the stated `11/267 vs 5/134` criterion, and a future tie on session count would use the wrong tie-breaker. Minimum fix: add/report `qualified_train_source_count_total` over sessions meeting the >=20 gate and use it for the ranking tie-breaker.

Do not approve Track-C export/model gate until these are fixed or the parent explicitly accepts the hash/count/fallback deviations.

Verified positives: selected-cell allowlist is loaded before `SplitFilteredAccess`; unselected cell rows are skipped before cue-count parsing; export records input hashes and split/session/duplicate/finite checks; `fit-track-c-models` requires both 100 primary and 100 temporal nulls; endpoint intercepts are unpenalized and continuous predictors are train-endpoint demeaned then train-standardized.

Residual risks: I did not run tests or biological/export commands due read-only/no-artifact-write constraints; review is static plus saved-artifact inspection.