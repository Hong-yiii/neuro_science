blocker — work/research-planning/implementation-phase1.md:102 — claimed/current script SHA is stale.

Verified: user and handoff claim `scripts/place195_path_generalization_phase1.py` SHA `76547bf65aa0a1245df1a66491050e5e21cc01df118105f18111b54608214ac8`, but `sha256sum` on the actual file returned `fe4dc6b57b97e87cee54a1232130d704aeccc13434f2c6c29015553955c18798`. Impact: I cannot attest the requested script artifact, and execution could run code different from the reviewed/handed-off hash. Minimum fix: reconcile the file to the intended SHA or regenerate handoff metadata and re-review that exact artifact.

blocker — scripts/place195_path_generalization_phase1.py:1924 — relaxed40 Track A source-index control is still missing while the stage reports complete.

Verified: protocol requires relaxed40/11-session “raw per-session total/binned and source-index controls” at `docs/reports/path-generalization-prefit-20260907.md:46`. Current `run_relaxed40_source_controls` loops only `("raw_total", "raw_binned")` at line 1924 and returns `"status": "complete"` at line 1941. Impact: Track A execution would silently skip a required source-control arm. Minimum fix: add the relaxed40 source-index control, or mark this stage/output incomplete.

major — scripts/place195_path_generalization_phase1.py:2097 — Track A moment-exact PCA stage is not wired into the biological runner.

Verified: protocol requires shared 29-cell PCA moments over class and cue-bin plus moment-exact standardization/PCA at `docs/reports/path-generalization-prefit-20260907.md:42-43`. The only biological completion labels are `moment_ridge` and sampled `row_grid_raw_pca_source_controls` at lines 2097-2102. `pca_from_moments` is only called in synthetic smoke at lines 4641-4647. Impact: the required moment-PCA diagnostic can be absent from a `"status": "complete"` Track A run. Minimum fix: run/write moment-PCA metrics in `run_track_a_program`, or explicitly mark that protocol stage unimplemented.

Verdict: **block combined Track A/B execution** until the hash mismatch and Track A silent-complete gaps are fixed. Subject to the hash mismatch, the prior **Track B** blockers appear closed in current code: 62 observed specs, 14-family × 20 null jobs, shuffled labels passed to sampled training and exact validation, row-normalized decoder C, family-max p-value, step-1000 checkpoint/loss parity, and fit identity hashing are present.

Unimplemented / nonblocking protocol items observed: parent evaluation-only replay sentence has no runner, but protocol says parent may run it later; no biological fits/export/importer/raw access were run by this review; GPU path was not executed.

Grades: content success **not approved** for Track A/B execution; operational success **not attested** because artifact hash mismatch and no GPU run; instruction compliance **satisfied** for this review: read-only inspection, no edits/subagents/biological fits.