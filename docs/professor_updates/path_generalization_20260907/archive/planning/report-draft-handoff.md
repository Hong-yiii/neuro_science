# Path-generalization report draft handoff

Status: final-ready HTML generated after B FINAL VERIFIED.

## Changed files / outputs
- `scripts/build_path_generalization_report.py`
- `docs/professor_updates/path_generalization_20260907/path-generalization-teaching-audit-20260907.html`
- `docs/professor_updates/path_generalization_20260907/path-generalization-teaching-audit-20260907.summary.json`
- `outputs/path-generalization-20260907/results-20260907T081200Z/report_assets/path_generalization_20260907/` (12 SVGs + 7 derived tables)
- `work/research-planning/report-draft-handoff.md`

## Incorporated guidance
- Added the read-only `audits/whole_cue_rank_bound.json` result as a concrete math box: WHOLE-CUE empirical-Q rank bound train ≤69, validation ≤9, exact validation matrix rank 9 for 30×290 at `1e-10`, `new_fits=0`. Caveat says this is not brain intrinsic dimension, pooled PCA covariance rank, or nonlinear CEBRA output rank.
- Track B inference now uses `track_b/summary_exact_audited.json` plus `audits/track_b_exact_audit.json`; original `summary.json` / `track_b_family_null_pvalues.json` are execution receipts only.
- Final B text reports exact observed max `7/12`, 18/20 inclusive exact-tie null exceedances, corrected p=`19/21`=`0.9047619048`; notes no models/predictions/checkpoints changed and independent artifact review approved the correction.
- Final report text now separates H1a/H1b from D1–D4, defines interior-corridor as positions `2..L-1`, clarifies no actual source-ID train/validation leak, frames Track C as operational per-unit real-trial prediction, and keeps all claims exploratory.
- Added A4 print CSS and verified inline SVG titles/roles/ID prefixes.

## Verification
- `python -m py_compile scripts/build_path_generalization_report.py` — passed.
- `python scripts/build_path_generalization_report.py --mode final --dry-run` — `track_b_final_ready: true`.
- `python scripts/build_path_generalization_report.py --mode final` — generated final HTML, 12 figures, 7 derived tables, word count 11906.
- HTML integrity scan — 0 `<script>`, 0 `<link>`, 0 `src/srcset`, 12 inline SVGs, 12 SVG roles/titles, 0 duplicate SVG IDs, A4 CSS present, exact B p and rank box present, no stale final pending phrases, no middle-slot phrasing.
- Derived table counts — B observed fits 62, B null maxima 20, B prefix checks 42, C unit rows 70; null19 is `7/12,0.5833333333333334`.
- `lsp_diagnostics scripts/build_path_generalization_report.py` — primary Python LSP clean.
- `lens_diagnostics mode=full` on generator — no issues. Generated one-file HTML has expected jscpd duplicate warnings from embedded Matplotlib SVG internals if actively scanned.
- `git diff --name-only --cached` — no staged files.

## Residual risks / boundaries
- No model fits, raw/importer/split internals, package installs, services, commits, or model artifacts were touched.
- This is still development evidence: original holdout exposure remains, 20 B null permutations give coarse p-value resolution, and parent owns final review/delivery.
- Frozen result manifests and generated provenance summaries contain SHA-256 digests; gitleaks generic-key hits on those digests were marked false-positive, not edited.

```acceptance-report
{
  "status": "final_ready_html_generated",
  "final_html": "docs/professor_updates/path_generalization_20260907/path-generalization-teaching-audit-20260907.html",
  "summary_json": "docs/professor_updates/path_generalization_20260907/path-generalization-teaching-audit-20260907.summary.json",
  "asset_dir": "outputs/path-generalization-20260907/results-20260907T081200Z/report_assets/path_generalization_20260907",
  "generator_sha256": "2c77fb2b025a316d6674000ca9d7547f2240b08910632ef6f0cf6ca10824062a",
  "html_sha256": "8fa2d4b7a6f89efdb80ca56b3d84425ec948d9c7885823e016a02de91831820c",
  "summary_sha256": "cfa337ca6f35a184a59d8ec02972800443a8b81112bd71ee9ccebc3a93ca7cf8",
  "derived_summary_sha256": "f8680625e5661204404b2b9e3d2bc3fe8376dd67ca9ccdf6e1406cf689ae63b7",
  "track_b": {
    "fit_count": 342,
    "optimizer_updates": 510000,
    "prefix_pairs": 42,
    "observed_family_max_exact": "7/12",
    "exceedances_including_exact_ties": 18,
    "family_max_pvalue_exact": "19/21",
    "family_max_pvalue": 0.9047619047619048,
    "inference_sources": [
      "track_b/summary_exact_audited.json",
      "audits/track_b_exact_audit.json"
    ]
  },
  "whole_cue_rank_bound": {
    "train_bound": 69,
    "validation_bound": 9,
    "exact_validation_matrix_rank": 9,
    "matrix_shape": [30, 290],
    "new_fits": 0,
    "not_claimed": [
      "brain_intrinsic_dimension",
      "pooled_pca_covariance_rank",
      "nonlinear_cebra_output_rank"
    ]
  },
  "html_checks": {
    "inline_svg_count": 12,
    "duplicate_svg_ids": 0,
    "script_tags": 0,
    "remote_autoloads": 0,
    "a4_print_css": true
  },
  "constraints_observed": {
    "new_fits_run": 0,
    "raw_importer_or_split_internals_read": false,
    "model_artifacts_modified": false,
    "packages_installed": false,
    "commits_created": false
  }
}
```
