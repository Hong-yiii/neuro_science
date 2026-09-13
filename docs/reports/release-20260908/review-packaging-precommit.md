blocker — docs/reports/release-20260908/preservation-manifest.json:1 — regenerated preservation manifest is still untracked.
Verified: `git ls-files docs/reports/release-20260908/preservation-manifest.json` returned no entry and `git status --short` reports it as `??`. Impact: the corrected receipt will not be in the release/PR if published from Git as-is. Minimum fix: add/commit the regenerated manifest after parent’s final seal.
Resolved prior findings:
- Preservation manifest hashes now validate: 30 `source_copies` and 67 tracked code hashes recomputed with 0 mismatches.
- Code provenance now validates: 46 records / 23 unique contents; archives and non-null sources hash-match; the intermediate record is explicitly `source: null` archive-only.
- PCA provenance now validates through `code-provenance.json` and the repository-base archive.
- Current portable links checked in README/index/release/archive/path README/path STATUS: 0 missing; path package verifier passed 98 shipped hashes, 9 tables, 12 figures.
Residual risks: none beyond committing the untracked manifest; no network checks of external URLs.
```acceptance-report
{
  "criteriaSatisfied": [
    {
      "id": "criterion-1",
      "status": "satisfied",
      "evidence": "Returned one concrete blocker plus final disposition of the three prior findings and portable-link checks."
    }
  ],
  "changedFiles": [],
  "testsAddedOrUpdated": [],
  "commandsRun": [
    {
      "command": "read initial review and scoped current files",
      "result": "passed",
      "summary": "Loaded prior findings and current manifest/provenance/docs context."
    },
    {
      "command": "python preservation-manifest hash check",
      "result": "passed",
      "summary": "30 source_copies and 67 tracked code hashes matched current recorded hashes."
    },
    {
      "command": "python code-provenance hash/source check",
      "result": "passed",
      "summary": "46 records, 23 unique content hashes; archives and non-null sources matched; one null source had archive-only explanation."
    },
    {
      "command": "python markdown portable-link check for scoped README/index/release/archive/path docs",
      "result": "passed",
      "summary": "0 missing relative links in scoped portable docs."
    },
    {
      "command": "python3 scripts/verify_path_generalization_package.py",
      "result": "passed",
      "summary": "Verified 98 shipped hashes, 9 unchanged tables, and 12 figures."
    },
    {
      "command": "git status / git ls-files for release metadata",
      "result": "failed",
      "summary": "preservation-manifest.json is untracked, so it is not yet included in Git."
    }
  ],
  "validationOutput": [
    "preservation-manifest source_copies errs: 0",
    "tracked_code_hashes errs: 0",
    "code-provenance archive_missing/source_missing/source_mismatch: 0, with 1 intentional null source",
    "portable scoped markdown missing_relative_links: 0",
    "path package verifier: status verified, files 98, unchanged_tables 9, figures 12"
  ],
  "residualRisks": [
    "The regenerated preservation manifest must be added/committed before final publication.",
    "External URLs were not network-checked."
  ],
  "noStagedFiles": true,
  "diffSummary": "Read-only follow-up review; no files changed.",
  "reviewFindings": [
    "blocker: docs/reports/release-20260908/preservation-manifest.json:1 - regenerated preservation manifest is untracked"
  ],
  "manualNotes": "The three prior content/provenance/link findings are resolved aside from the Git tracking blocker above."
}
```
