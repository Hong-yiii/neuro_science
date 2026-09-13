# Completed path-generalization study — 2026-09-07

> **Historical completion receipt.** Hashes, working-tree status and preview claims below describe the original September 7 release. Later presentation fixes, current hashes and proposal status are in the [packaged study index](../professor_updates/path_generalization_20260907/README.md) and [correction ledger](../professor_updates/path_generalization_20260907/CORRECTIONS.md). Do not compare the archived release hash to a subsequently corrected HTML file.

## Deliverable

- Worktree: `/home/hongyi-home-lab/neuro_science-path-diagnosis`
- Branch: `research/path-generalization-20260907`, base `a9d8dacbbe38d0d82b9f75444e5f538b5e411352`.
- Final self-contained HTML: `docs/professor_updates/path_generalization_20260907/path-generalization-teaching-audit-20260907.html`.
- HTML SHA256: `31c745a626d4fcad3a38f7e9842dce1ac57321594aca0464904ce3718d55a2d7`.
- Manifest beside HTML: `report-manifest.json`; duplicate under the run root.
- Preview: `http://localhost:8765/path-generalization-teaching-audit-20260907.html`; exact-byte HTTP200 verified; cmux browser open succeeded on surface:38/pane:12.
- Original checkout and its preexisting modified baseline script remain unchanged. Nothing staged, committed or pushed.

## Completed evidence

Run root: `outputs/path-generalization-20260907/results-20260907T081200Z`.

- A: accepted `track_a_v2/`; initial `track_a/` preserved after a V9 CSV-reader `C`-column error. Core fitting/data choices unchanged in the rerun. 1,847 metric rows, 55,410 predictions, 1,800 known-truth Gaussian cases, 1,980 real-session relaxed40 controls.
- B: `track_b/`: 342 native CUDA fits (62 observed +280 null), 510,000 optimizer updates, 42 paired 1000/5000 prefix checks with zero numerical differences, all producer reload differences zero. Wall time 1:18:29.
- C: `track_c/`: three source-preserving per-unit targets, 100 ordinary and 100 temporal joint-label nulls. Export: 64,051 unit-trial rows, 19,162 sources, 195 units; zero forbidden rows yielded. Original mixed tables were streamed through SplitFilteredAccess, not physically avoided.
- Cross-assembly: `assembly_transfer/`: 50 frozen checkpoints, 250 CPU-only evaluations, no new fits.
- Audit: 4,488 fit artifacts hashed; 38 unit/regression tests passed plus synthetic native and full-runner checks.

## Findings

- New mixtures of the SAME training sources: Time mean BA0.9925, Behavior0.997656; own training BA1.0. Source-disjoint exact validation: factorial means Time0.249167, Behavior0.351667. This localizes the gap across source pools; it does not establish its biological cause.
- Finite-sample ridge stabilizes near exact-Q BA0.479, rather than improving with more synthetic rows. Source subsets and session-block influence have much larger effects.
- Exact validation is only24 absent+6 present combinations. Its 290-feature whole-cue matrix has rank9 by construction; this is NOT a brain-intrinsic-dimensionality result.
- Old absent means absence from ALL interior corridor runs after removing first/last, not absence from the full path. 51/185 fixed4→3 absent paths traverse the edge outside the interior.
- A more supported interior target `D_N_C_M__N_C_B` was selected by TRAIN behavior/support only. Its C cohort:43 units/11 sessions/267 train/52 validation sources. Mean Δ log loss +0.003860, but three-target family p≈0.475 ordinary/0.436 temporal: no convincing incremental cue-rate evidence.

## Inference authority / correction

Use `track_b/summary_exact_audited.json` and `audits/track_b_exact_audit.json`, NOT the raw producer p-value. Null19 and the observed maximum both equal7/12, but floating reductions differed by1e-16. Exact inclusive counting yields18/20 exceedances and p19/21=0.9047619, not17/20 and0.8571429. Models and predictions were not changed.

Frozen producers remain in `outputs/path-generalization-20260907/frozen/`: original driver SHA2821317f... forB/C; TrackA reader-only fix SHA340bd4fa...; protocol SHA14e13571.... Live analysis source subsequently gained a regression-tested floating-tie comparison fix. These are deliberately different provenance versions, not mixed model fits.

## Verification / report

- Runnable read-only audit: `python scripts/verify_path_generalization_results.py RUN_ROOT` from worktree root. No fitting/raw access.
- Regenerate HTML with the existing research runtime and `scripts/build_path_generalization_report.py --mode final`.
- Builder SHA: `593bc21f8b82cd1bee7eb63e1972cc0b4437c7e136234dfddc96a6099ce816d3`; exact source archived in run-root `audits/report_builder_used.py`.
- Deterministic regeneration yielded identical HTML SHA. Twelve embedded figures; no remote autoloads/JS; desktop and graph views checked. Full print is35 mixed portrait/landscape A4 pages including readable audit tables.
- Independent reviews: `track-a-results-review.md`, `track-b-final-review.md`, `track-c-results-review.md`, `assembly-transfer-review.md`, `final-html-pedagogy-review.md`, `final-html-factual-review.md`, `final-release-followup-review.md` in this planning directory. Final release approved; reviews are AI-assisted QA, not external human peer review.
- Render evidence retained under run-root `audits/render_checks/`. Own temporary Chrome profiles removed. Existing loopback viewer was reused, not a newly exposed service.

## Next direction and limits

Source-preserving, endpoint/time/nuisance-controlled route-component work with verified task/recording metadata and genuinely reserved observations. The methods/rank/finite-source results are reproducible; prospective biological coding remains unconfirmed. Do not resume architecture/seed/window searching merely to force significance. The original holdout remains exposed; resplitting inspected data cannot restore pristine confirmation.
