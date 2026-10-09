# Endpoint comparison execution ledger — October 7, 2026

**Classification: exploratory analysis.** This is the separate endpoint cohort, not a path-study rerun or confirmatory H1 test. Hongyi explicitly authorized execution with “please go ahead and run it.” PR #15 remains draft/unmerged; no publication/merge is requested by this authorization.

## Integration update — October 9, 2026

Hongyi subsequently authorized the final PR15 update and merge, superseding the
earlier draft-only restrictions recorded below. Keep both studies and original
commit ancestry; do not squash/rebase or delete branches/worktrees/data. The
[observability/CEBRA handoff](../../observability-pivot-20261009.md) is indexed for
the next session; no new analysis is executed by this integration. Post-review
Markdown clarifications do not change numeric tables, figures, fitted artifacts,
verified offline HTML or original execution hashes. Preservation/merge receipts:
`outputs/pr15-merge-20261009/`.

## Completed execution — October 7, 2026

Independent review `5938a5d2-516b-4bb9-b716-5efa2364ff23` cleared the final cache/audit and resource gate; follow-up `7e1ba226` approved executing the exact immutable reviewed runner despite later canonical formatting. The frozen approval-facts audit passed (`b3bbbd45a`), and `preparation-20261007/prefit-approval-3816068.json` binds the code, accepted inputs, navigation, configuration and budget. Approval SHA256: `25083bb13112369ed6c6b2063be30f89c46ca785cdde1cd0e72425a2bfb30725`.

**Biological endpoint fitting completed:** task `b574f1f8f` exited0 after all126 encoder fits,63 PCA fits and10,395 readouts across the observed world and all20 null worlds/3 seeds. Outputs remain in `outputs/cebra-endpoint-time-readout-20261006/run-reviewed-20261007/`; the fit scope is inactive.

**Native fit-blocked replay passed:** task `b0870da81` exited0 using the exact frozen runner and separately reviewed adapter. Receipt: `outputs/cebra-endpoint-time-readout-20261006/replay-native-cuda-20261007/receipt.json` (SHA-256 `998724e5c4722ecd4da280e003c916e76f08e2e3bca294f12c7409bec9aa0778`). Adapter SHA-256 `52f04481878af6f801d821a2a1093d08043e6f9d8f7fe8ab94baec7a006dc1bf`; frozen runner SHA-256 `12a0f27c11fbf3d075331cfc235d17eaf0c36ac874a3c706f4e7ee21058a812b`. The receipt confirms hash-manifest verification for32,544 files, CUDA replay, `fits_blocked: true`, and exact counts:126 encoder,10,395 readout,20,790 metric,6,735,960 confusion and63 lineage replays. Tolerances and fitted artifacts were unchanged. The replay scope is inactive; prior scaler-only and PCA-failing replay receipts/logs remain preserved.

Independent receipt audit found no replay blocker. A separate scientific review cleared descriptive/exploratory reporting with the cohort and pseudopopulation limitations retained. The renderer produced [18 figures and tables](./README.md) and a self-contained [HTML report](report.html) in task `bfcc360eb`; five renderer regressions and primary LSP diagnostics passed. Final independent artifact-coverage review cleared the artifacts: `report.html` embeds all18 PNGs with no external figure references; `provenance.json` records18 figures, zero new fits, and verified run/replay hashes; `tables/observed_metrics_by_seed.csv` contains990 unique seed/target/representation/window/split rows. The README wholecue table matches previously verified rounded values, and reviewed source-count/confusion figures were consistent with their captions. `y_prob` normalization warnings persisted; the reviewer judged them numerically negligible but not silently removed, so disclose them in any report. PR #15 remains draft/unmerged; this replay repair authorizes no publication or merge. [Run lifecycle and recovery](run-operations.md).

Actual executable: `preparation-20261007/frozen-launch/cebra_endpoint_time_readout.py`, SHA256 `12a0f27c11fbf3d075331cfc235d17eaf0c36ac874a3c706f4e7ee21058a812b`. The reviewed native-operation verifier loads this same frozen entry; do not use the subsequently edited canonical runner or repeat the original unamended replay. Its frozen resource receipt SHA256 `35e5c8c1d4db286f82c471efe1344f7513660211932cf9732c8628be8b746f20` projects3223.53s including25% margin and4.57GiB including the navigation-cache estimate. The full protocol remains126/63/10,395 fits,90minutes/10GiB; separate cgroup limits are6GiB RAM,512MiB swap and200% CPU. No new service installation, listener, path rerun or PR merge.

## Prefit preparation — historical checkpoints (superseded above)

- Accepted-artifact hashes and all three observed assemblies passed exact reconstruction before extraction or fitting. Metadata preflight: `preparation-20261007/input-preflight.json` (SHA-256 `9c96487a209cc76ef601ff6fe586ac01cb0520faa53ac572c62426346ce7fb8f`), with zero fits and no raw-navigation access during preflight.
- Training-only navigation extraction attempt 4 is retained at `outputs/cebra-endpoint-time-readout-20261006/navigation-20261007-attempt4/`. Audit SHA-256 `02864881a01be2aaf0bad735182283407c4cc3671e5582c0f4a3237bd7dbb4d0`; NPZ SHA-256 `d0bf8ef5cb4332665a250d0b0da57e5fb68bec90047ff73df6fb226411d0d17b`. The audit passed for exactly 12,288 endpoint inner-training sources and 1,062,395 bins; development navigation was not selected. It validates the 16,859-row outer-training gate before applying the inner-training allowlist and rejects duplicate/missing rows.
- `navigation-validation-attempt4.json` records `source_hashes_stable: false`: the extraction snapshot runner (`3871ddb...`) and then-current canonical runner (`12a0f27...`) differed only in the fit-resource validator's CUDA-availability guard, not extraction or scientific logic. Independent review found no extraction blocker and confirmed no re-extraction is required.
- The reviewed resource receipt is preserved byte-for-byte as `preparation-20261007/current-hash/synthetic-benchmark-reviewed-runner12a0.json` (SHA-256 `35e5c8c1d4db286f82c471efe1344f7513660211932cf9732c8628be8b746f20`). Its companion benchmark script is SHA-256 `c6b3aa3d3ef24868bae2c0bbe7e20685d3383b6fb8bd3513e3c55a424d54087d`; preflight SHA-256 is above. It covered 165 readout states, 106,920 confusion rows per seed with JSON write/read round-trips, and 495 source-deletion states over 3,265 invented sources. It projects 3,223.5 s with the 25% margin and 4.57 GiB output including the cache estimate (within the 90-minute/10-GiB caps); peak RSS was 3,618,900 KiB. The benchmark read no raw navigation and performed zero biological fits.
- A separate receipt for the formatter-drifted canonical runner (`7d399f...`, receipt SHA-256 `01015ed5...`) and its approval-facts output are preserved in `preparation-20261007/current-hash/`. Do not substitute them for the reviewed frozen bundle; the independent reviewer conditioned its verdict on the exact `12a0f27...` runner and `35e5c8...` receipt.
- The immutable bundle is `outputs/cebra-endpoint-time-readout-20261006/frozen-launch/`; runner SHA-256 `12a0f27c11fbf3d075331cfc235d17eaf0c36ac874a3c706f4e7ee21058a812b`. Its receipt, benchmark script, and preflight copies match the exact hashes above. The protocol remains SHA-256 `e42d49be8f733e3e13a104bdf85faccce3d063887589ea0d74c1c121309d2a73`.
- Direct-file `approval-facts` validation and CLI help passed using the frozen runner and attempt-4 cache/audit. Facts are in `frozen-launch/prefit-approval-facts.json` (SHA-256 `e729e8a1fe5a8b9d67b0461e810ba9603fca47e7b91c07715905b2fa658b09b6`); config hash `d475d3d9dd37cc4168dc05c615d3aaea5eec71a20ad2fc0c585311341a3296aa`. The file contains facts, not owner approval. The budget remains 126 encoder, 63 PCA, and 10,395 readout fits; all 20 null worlds are retained.
- The endpoint suite passes all 26 invented-data tests; Ruff and byte-compilation pass. No resource-budget changes, dropped null worlds, or biological fits were made.

Preparation subsequently included three retained failed extraction attempts (marker-code separators, imported timestamp precision, then native-versus-imported cue bin boundaries). Diagnosis exactly reproduced all12,288 training sources' accepted cue counts/exposures through the original CSV precision. Attempt4 produced1,062,395 native navigation bins with no development navigation and passed its cache audit; its nonzero wrapper exit recorded a concurrent resource-check-only code change. Independent snapshot comparison cleared that change without re-extraction. Frozen approval validation then passed and fitting began as recorded above. All20null worlds and the126/63/10,395 budget remain intact.

## Draft-PR update — October 8, 2026 (Singapore)

Hongyi subsequently requested opening or updating a PR for the completed study.
Update existing draft [PR #15](https://github.com/Hong-yiii/neuro_science/pull/15)
on `analysis/cue-time-readout-20261005`; do not merge. Publish this separate
endpoint report,18 figures,990-row aggregate metric table, provenance, runner,
verifier and tests. Keep the October5 path study intact and distinct. Exclude raw
inputs, fitted models, full predictions, private approvals/logs and unrelated
working-tree changes; those remain local. The PR permission authorizes no new
biological fits or broader scientific claims.

Publication checks passed:39 invented-data regression tests, Ruff and compilation.
The canonical runner and verifier differ from their executed frozen snapshots
only in formatting (AST-identical); their publication SHA256 values are
`7d399f083e7c7fa344d970f814158c1b8cf178ad024015f676d8bc6dbf0e6ca0` and
`596b5deeebc3272e851a7731df3e89d56e429a93a2a65d586f46fd58acf22c20`, respectively.
The renderer matches the report provenance byte-for-byte. Approved frozen source
snapshots and private inputs remain required for the recorded replay; publishing
the formatted sources does not replace the approval-bound byte identities.
The earlier October5-author-dated commit is preserved; this follow-up uses its
actual publication date. Publication/preservation receipts are retained under
`outputs/cebra-endpoint-time-readout-20261006/publication-20261008/`.

## Operations

Owner: HY, canonical repository `~/neuro_science`; normal account; runtime `scratch/v6-v9-runtime/bin/python` with explicit two-thread BLAS/OpenMP settings. No listener, service restart, package installation, boot persistence, auto-restart or new worktree. Logs are session-owned Pi task outputs under `.pi/tasks/`; private data/cache/models stay under ignored `outputs/cebra-endpoint-time-readout-20261006/`. Stop an active job through its owning Pi task, not a historical PID; partial outputs are retained and cannot be approved as complete. Recompute only with a new deliberate run and preserved attempt history.

Full runs must be fit-blocked replayed and independently reviewed before interpretation. Source pools are historically exposed and label-conditioned cross-session pseudopopulations; synthetic rows/seeds are not biological replications. Results must distinguish targets, real-source support, all cue windows, baselines, nulls and source-deletion sensitivity. No claim of simultaneous population dynamics, biological rotation, path information beyond endpoints, or pristine confirmation follows from endpoint decoding.
