## Files Retrieved

- `README.md:31-46` — current path-generalization entry point, local-only results contract, verify/report commands.
- `docs/reports/path-generalization-prefit-20260907.md:1-31,120-157` — frozen protocol, claim ceiling, V6-V9 dependency/runtime contract.
- `work/research-planning/FINAL_STATE.md:1-41` — final release state, hashes, accepted run root, no-code-loss notes.
- `docs/professor_updates/path_generalization_20260907/report-manifest.json:1-52` — released HTML manifest and immutable hashes.
- `scripts/verify_path_generalization_results.py:1-164` — stdlib-only verifier; checks 342 B fits, exact p, C nulls.
- `scripts/build_path_generalization_report.py:1-80,2368-2536` — generator imports, required local result tree, final/draft guards, write behavior.
- `outputs/path-generalization-20260907/results-20260907T081200Z/{final_report_manifest.json,data_gate_checks.json,execution_gate.json}` — core local receipts.
- `outputs/path-generalization-20260907/results-20260907T081200Z/track_a_reader_fix.json` — failed Track A supersession receipt.
- `work/research-planning/{track-a-results-review.md,track-b-final-review.md,track-c-results-review.md,assembly-transfer-review.md,final-*.md}` — final independent QA evidence.

## Key Code

```py
# scripts/verify_path_generalization_results.py:23-29
summary = json.loads((b / "summary.json").read_text())
assert summary["status"] == "complete"
assert summary["fit_count"] == summary["expected_fit_count"] == 342
files = sorted((b / "fits").glob("*/fit_info.json"))
assert len(files) == 342
```

```py
# scripts/build_path_generalization_report.py:2459-2464
if args.mode == "final" and not track_b["final_ready"]:
    raise SystemExit("Final HTML blocked: Track B full family-null summary is incomplete ...")
```

## Architecture

Entry point for PR packaging is `README.md:31-46`: committed docs point to released HTML, local ignored run root, verifier, and generator. Scientific contract is frozen in `docs/reports/path-generalization-prefit-20260907.md`; executed artifacts live under ignored `outputs/path-generalization-20260907/results-20260907T081200Z/`; final user-facing immutable release is already in `docs/professor_updates/path_generalization_20260907/`.

Git status shows only existing uncommitted/untracked packaging candidates: `README.md` modified; new docs/scripts/report dir untracked. No staging.

## Findings

1. **Promote to Git — essential docs/release**
   - `README.md` — project landing page updated with local-only artifact contract and commands.
   - `docs/reports/path-generalization-prefit-20260907.md` — frozen protocol, SHA `14e135...483b`.
   - `docs/professor_updates/path_generalization_20260907/path-generalization-teaching-audit-20260907.html` — released immutable HTML, SHA `31c745...d55a2d7`.
   - `docs/professor_updates/path_generalization_20260907/path-generalization-teaching-audit-20260907.summary.json`
   - `docs/professor_updates/path_generalization_20260907/report-manifest.json`

2. **Promote to Git — runnable reproduction/verification code**
   - `scripts/verify_path_generalization_results.py` — no fitting/raw access; stdlib-only verifier.
   - `scripts/build_path_generalization_report.py` — report generator; writes derived tables/figures/HTML unless `--dry-run`.
   - `scripts/place195_path_generalization_phase1.py`
   - `scripts/replay_path_generalization_assemblies.py`
   - `scripts/test_place195_path_generalization_execution.py`
   - `scripts/test_place195_path_generalization_phase1.py`

3. **Promote or archive as small local receipts/aggregates, not full data**
   - `outputs/.../results-20260907T081200Z/final_report_manifest.json`
   - `outputs/.../execution_gate.json`
   - `outputs/.../data_gate_checks.json`
   - `outputs/.../track_a_reader_fix.json`
   - `outputs/.../track_b/summary_exact_audited.json` and `outputs/.../audits/track_b_exact_audit.json`
   - `outputs/.../track_a_v2/summary.json`, `track_b/summary.json`, `track_c/summary.json`, `assembly_transfer/summary.json`
   - `outputs/.../report_assets/path_generalization_20260907/derived_*.{json,csv}` only; skip SVGs if released HTML embeds them.
   - `outputs/.../frozen/{protocol.md,driver.py,driver_track_a_v2.py}` and `outputs/.../audits/report_builder_used.py` as provenance snapshots if size acceptable.

4. **Do not promote bulky/local artifacts**
   - `track_b/fits/**` checkpoints/losses/predictions, full `track_b_fit_infos.json`, `track_a*_exact_validation_predictions.csv`, `track_c_export/development_component_labels.csv`, `track_c_allowlist/development_component_allowlist.csv`, render PNG/PDFs, raw/importer data. Keep local/ignored.

5. **Status labels needed**
   - **superseded/failed:** `outputs/.../track_a/` — no `summary.json`; superseded by `track_a_v2/` after V9 `C`-column reader failure (`track_a_reader_fix.json`).
   - **superseded execution receipt:** `outputs/.../track_b/track_b_family_null_pvalues.json` and raw `track_b/summary.json` p-value: use audited `p=19/21`, not producer float `0.8571429`.
   - **superseded drafts:** `outputs/.../audits/report_before_parent_clarifications.html`, `audits/report_before_parent_clarifications.html`.
   - **obsolete planning reviews:** `code-review-ab.md`, `code-review-ab-final.md`, `code-review-c.md`, `code-review-c-final.md`, `protocol-preflight-review.md` contain blockers later resolved; retain with “historical/resolved” label if committed.
   - **failed smoke:** `outputs/path-generalization-20260907/audits/phase1_failed_smoke_broadcasting.md`.
   - **superseded phase outputs:** non-final `phase1_*`, `target_semantics_audit*`, `track_b_config*`, `track_c_allowlist*` directories without `_final` or outside final run root.

## Unknowns / Stop Reason

Did not run verifier/generator/tests, inspect raw data, original `/home/hongyi-home-lab/neuro_science` worktree, start-goal worktrees, or mutate git. Frozen results/released HTML treated immutable.

## Start Here

Start with `work/research-planning/FINAL_STATE.md`: it names the accepted run root, released hashes, inference authority, and exact supersession caveats.