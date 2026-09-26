# One local research-review branch — September 26, 2026

**Working directory:** `/home/hongyi-home-lab/neuro_science`

**Working branch:** `review/research-consolidated-20260926`

Hongyi requested that all open PRs be combined into one review branch and that this checkout switch to it. This is **software integration/smoke testing**, not a new scientific analysis, research-direction decision or biological fit authorization.

## Included history

| Input | Exact input revision | Handling |
| --- | --- | --- |
| Refreshed `origin/main`, including PR #7 | `834063184085b8ff9eaa19264728a1bf79969d70` | Base; matched PCA is already merged, not rerun. |
| PR #8, saved latent atlas | `a401eb3f955bac5df241a9000e15cd5f794d3e55` | Local merge with original history and published package retained. |
| PR #9, broader-training experiment | `c19d07cf734bd009bdbe02c6e49aad38bb78c7e1` | Local merge after #8. |
| PR #10, teaching follow-up | `ea6a8fed62b886abfbcee20335245f771d606f73` | Local merge after its parent #9; no duplicate scientific execution. |
| Formerly dirty local source/docs | `8baf68faabd0820577baa6b42a4d3e2c2278352f` | Safety snapshot merged, retaining decoder, diagnosis, professor/weekly reports and Sept26 review. |

PRs #8/#9/#10 remain open on GitHub with their original bases. Remote `main` was not merged into, rewritten or pushed. This review branch is **local only**; there is no new aggregate PR or remote upstream. Publishing it later is a separate action.

## Conflict decisions

- PR8 versus PR9: report-index update-date conflict; retained both study entries.
- Local snapshot versus integrated main/PRs: semantically combined `README.md`, `docs/workspace.md` and `docs/reports/README.md`; retained the matched-PCA, atlas, transfer, teaching, decoder and diagnosis entries. Updated current branch/recovery guidance; dated historical reports remain historical.
- Atlas protocol/results: kept PR8's published versions. The older local versions predated publication, linked only to ignored output, omitted publication checks and retained stale “no PR” wording. Both originals are preserved in safety history and the byte-copy backup.
- Atlas tests: kept PR8's newer version, which adds the portable package/hash/embedded-metric check to all older tests. The runner and HTML template already matched byte-for-byte; no scientific implementation was rewritten.
- An initial `git diff --cached --check` flagged the existing two-space Markdown hard break in the professor review. It was intentionally preserved in the exact safety snapshot; the checkpoint was checked with `core.whitespace=-blank-at-eol`. No experiment code or provenance was reformatted to satisfy that check.

## Preservation and rollback

Before checkout/merges, copied and SHA256-verified **31 dirty/untracked source/doc files, 3,409,136 bytes**. Exact paths/hashes:

- `outputs/review-integration-20260926/before.json`
- `work/review-integration-20260926/before/`
- Safety branch: `safety/pre-review-integration-20260926`, commit `8baf68f`.
- Verified complete Git bundle: `work/review-integration-20260926/pre-integration.bundle`.

The old release branch remains at `438856e`; the safety branch contains the exact pre-integration working-file content as a clean commit. To inspect that checkpoint later, first preserve any new dirty work, then deliberately switch to the safety branch. Do not reset/clean the active review branch to recover one file. Prefer reading the backup or `git show 8baf68f:path` and reconciling that file explicitly.

**Git and this source/doc backup do not back up ignored research artifacts.** All private inputs, runtime environments, accepted models/predictions, failed attempts, and the three retained worktrees stay where they were. No artifact relocation or worktree deletion occurred. In particular, `work/issue-6-pca/outputs/path-pca-matched/` remains essential even though PR7 is merged. PR9 continues to resolve canonical outputs and its checkout-relative frozen protocol; no path abstraction was introduced.

## Older root-spawned rollouts

Confirmed the earlier durable consolidation session at:

`~/.pi/agent/sessions/--home-hongyi-home-lab--/2026-09-10T09-40-05-716Z_01a08ab0-4fd4-704c-ac18-3b002e40c116.jsonl`

Targeted user messages at JSONL lines 4 and 71 requested one neuroscience workspace and designated that session as durable at that time; line 525 discussed the PR/session relationship. They support preserving consolidated provenance, not restarting old pending studies or deleting new worktrees. The current user request authorizes this branch integration. The Sept26 scientific roadmap remains a proposal until chosen.

A read-only rollout researcher and compatibility scout checked session metadata, branch dependencies and atlas divergence. Parent additionally inspected the relevant historical user messages. Reports remain local under `.pi-subagents/artifacts/outputs/b7e1e34a-2c35-4c72-a9a4-2510dc4d06f4/`; original transcripts were not changed or copied into Git.

## Validation

**Passed:** all **134 software tests** in 50.758 seconds; the separate PR10 check verified **18 metric cells, four accessible diagrams, anchors and offline resources**; review HTML freshness/anchors/local-reference checks passed. Pi task `b181e04df` completed in 55 seconds with exit 0. Log: `outputs/review-integration-20260926/software-checks.log`. Independent review and final containment/preservation checks are recorded below before delivery.

Commands use the retained environment, two CPU threads, no GPU and no new packages:

```sh
export PYTHONDONTWRITEBYTECODE=1 PYTHONNOUSERSITE=1 CUDA_VISIBLE_DEVICES=''
export OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2
PY=/home/hongyi-home-lab/neuro_science/scratch/v6-v9-runtime/bin/python
"$PY" scripts/check_research_software.py
"$PY" learning/check_cebra_time_transfer_teach.py
"$PY" docs/reports/research-reset-20260926/render.py --check
```

The software suite includes tiny **invented-data** CPU fits and synthetic state replay, not biological-model refits. Two named pre-existing private-input checks remain excluded by its runner. The PR10 checker is run separately because test discovery only covers `scripts/test_*.py`. Full private saved-artifact replay is not part of this integration.

Static check before testing: six Python files requested via primary LSP; two confirmed clean and four timed out. Zero returned diagnostics is **not** a claim that those four completed a type check. Existing PR receipts and executable software checks provide separate evidence; no claim of project-wide static cleanliness.

Local execution/provenance receipts and logs are under `outputs/review-integration-20260926/`. No service, listener, scheduled job or new Git worktree was created.
