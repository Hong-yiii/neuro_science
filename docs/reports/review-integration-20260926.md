# One consolidated research-review branch — September 26–27, 2026

**Working directory:** `/home/hongyi-home-lab/neuro_science`

**Consolidation branch (merged):** `review/research-consolidated-20260926`

**Direction follow-up:** authored on `planning/project-direction-20260927`;
[agreed September27 scope](../project-direction.md) is now the next-session
starting point. Use updated main after its authorized follow-up PR merges.

Hongyi requested that all open PRs be combined into one review branch and that this checkout switch to it. This is **software integration/smoke testing**, not a new scientific analysis, research-direction decision or biological fit authorization.

## Included history

| Input | Exact input revision | Handling |
| --- | --- | --- |
| Refreshed `origin/main`, including PR #7 | `834063184085b8ff9eaa19264728a1bf79969d70` | Base; matched PCA is already merged, not rerun. |
| PR #8, saved latent atlas | `a401eb3f955bac5df241a9000e15cd5f794d3e55` | Local merge with original history and published package retained. |
| PR #9, broader-training experiment | `c19d07cf734bd009bdbe02c6e49aad38bb78c7e1` | Local merge after #8. |
| PR #10, teaching follow-up | `ea6a8fed62b886abfbcee20335245f771d606f73` | Local merge after its parent #9; no duplicate scientific execution. |
| Formerly dirty local source/docs | `8baf68faabd0820577baa6b42a4d3e2c2278352f` | Safety snapshot merged, retaining decoder, diagnosis, professor/weekly reports and Sept26 review. |

**Published September27 at Hongyi's request:** [consolidated PR #11](https://github.com/Hong-yiii/neuro_science/pull/11), base `main`, head `review/research-consolidated-20260926`. At publication, source PRs and main were unchanged; the review branch gained its origin upstream.

**Subsequently merged at Hongyi's request:** September27, **09:09:51 UTC**, merge commit `e8f2308a1204fd887ab062e0664c1cf4585bb89f`. Used a normal merge commit with expected-head guard `87e16af`, no admin bypass, squash or deletion. GitHub reported clean/mergeable with no status checks returned; the earlier 134-test/independent-review evidence still applies to the unchanged scientific code. GitHub automatically marked #8/#9 merged two seconds later. At that merge checkpoint #10 remained open against its original stacked base. During subsequent owner-authorized convergence, #10 was closed as already included after its head ancestry was checked; no branch/worktree was deleted or retargeted.

Created and checked out **`planning/project-direction-20260927`** from that merged main, without an upstream or new PR. The branch initially had no direction decisions; the later discussion produced the [agreed scope update](../project-direction.md). All other worktrees/artifacts remain in place. The uncommitted formatting-only atlas-test change was copied to `work/project-direction-20260927/atlas-test-before.py`, with a patch and hash receipt in `outputs/project-direction-20260927/before.json`, then carried across unchanged. No new fits or artifact migration.

The September26 integration was local-only; September27 publication is a separate, subsequently authorized action. A newly observed local formatting-only change in `scripts/test_cebra_latent_atlas.py` was checked for identical Python AST, left untouched and **excluded** from the PR. The earlier clean-tree receipt describes its original checkpoint, not the later formatting edit.

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

Targeted user messages at JSONL lines 4 and 71 requested one neuroscience workspace and designated that session as durable at that time; line 525 discussed the PR/session relationship. They support preserving consolidated provenance, not restarting old pending studies or deleting new worktrees. The current user request authorizes this branch integration. The Sept26 roadmap was a proposal; the later September27 decision record specifies which scope choices were actually adopted.

A read-only rollout researcher and compatibility scout checked session metadata, branch dependencies and atlas divergence. Parent additionally inspected the relevant historical user messages. Reports remain local under `.pi-subagents/artifacts/outputs/b7e1e34a-2c35-4c72-a9a4-2510dc4d06f4/`; original transcripts were not changed or copied into Git.

## Validation

**Passed:** all **134 software tests** in 50.758 seconds; the separate PR10 check verified **18 metric cells, four accessible diagrams, anchors and offline resources**; review HTML freshness/anchors/local-reference checks passed. Pi task `b181e04df` completed in 55 seconds with exit 0. Log: `outputs/review-integration-20260926/software-checks.log`. The subsequent integration-status banner was regenerated and the HTML freshness check passed again.

**Preservation/containment passed at merge `2a1525f`:** all five input tips are ancestors; **46 PR-file comparisons** are byte-identical outside navigation; all **31 backup copies and safety-commit originals** match their recorded hashes; **22 current local files** remain identical and **nine** have the documented atlas/navigation/status reconciliation. The three other worktrees retain their original commits and clean status. The canonical working tree was clean after the merge. Receipt: `outputs/review-integration-20260926/integration-check.json`.

**Independent final review:** fresh-context, read-only reviewer `df62541c-844c-4d43-9356-61e4f535c10a` returned **no findings**, confirming it is safe to continue source/doc work on the combined branch. It inspected Git, source/docs, receipts and test logs, but did not independently rerun tests or inspect/replay private raw/model artifacts. Review: `.pi-subagents/artifacts/outputs/df62541c-844c-4d43-9356-61e4f535c10a/work/review-integration-20260926/final-review.md`. This receipt's final update is documentation-only.

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

Static check before testing: six Python files requested via primary LSP; two confirmed clean and four timed out. Zero returned diagnostics is **not** a claim that those four completed a type check. Existing PR receipts and executable software checks provide separate evidence; no claim of project-wide static cleanliness. Final session diagnostics reported **no blocking errors**. Marksman missing/ambiguous-document warnings were checked against **128 local links, all existing** (`outputs/review-integration-20260926/link-check.json`); retained duplicate worktree docs and the newly merged files explain the index warnings. Spelling warnings on BA/PN and an assertion-in-test warning do not warrant changing historical scientific terminology or tests.

Local execution/provenance receipts and logs are under `outputs/review-integration-20260926/`. No service, listener, scheduled job or new Git worktree was created.

## September27 cmux delivery

Opened the consolidated review in a right-hand browser pane beside the active neuroscience session: `workspace:17`, `pane:38`, `surface:75`. The old `workspace:18` view no longer existed. The replacement displays the tracked portable HTML in a verified `about:blank` document, using the existing cmux relay, with seven review sections and no scripts or external resources. No HTTP server, new ingress or detached worker is needed. Reload clears the disposable view; the Markdown/HTML remain in Git. Close that browser pane to dismiss it, not the owning SSH workspace. Local receipt: `outputs/review-integration-20260926/cmux-preview-20260927.json`.

## September27 agreed-direction follow-up

The [decision record](../project-direction.md) is the next-session authority;
active contracts/onboarding now agree, and old pilot/roadmap settings remain
explicitly historical. This slice changes documentation and regenerated HTML
only. It does not rerun the earlier134-test suite, analyze private data or fit
models. The pre-existing atlas-test formatting edit remains excluded and intact.

Independent reviewer `2272639e-cf8e-4677-a7ce-4ca635acb3b3` identified one stale
historical PR10-status sentence; corrected it and the analogous PR7 wording.
Follow-up `77096d08` verified closure with **no remaining findings**. It inspected
the diff/links/preservation and saved validation artifacts, not private data or
an independent renderer run. Parent checks passed:189 local Markdown targets,
direction anchors, renderer freshness/seven sections/offline resources, dirty-test
bytes and AST, source-tip ancestry, and three unchanged clean retained worktrees.
Session diagnostics reported no blocking errors; pre-existing index/spelling
warnings remain. No claim of a full project-wide static/data audit is made.

Retained local evidence: `outputs/project-direction-20260927/convergence/`
(`before.json`, `validation.json`, `document-checks.log`, independent review and
publication/merge receipts). Runnable no-fit documentation/preservation check:
`work/project-direction-20260927/convergence/check_docs.py`, using the existing
`scratch/v6-v9-runtime/bin/python`. These are retained task records, not new
runtime dependencies. Branches, worktrees, ignored artifacts and recovery copies
are preserved; no cleanup or new service is part of convergence.
