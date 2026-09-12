# Workspace consolidation ledger

Session began September 10; takeover and filesystem work resumed **September 13,
2026 (Asia/Singapore)**. Authorized by Hongyi: use this as the one current durable
session, preserve recorded exploratory work, and remove redundant neuroscience
folders after PR/log coverage. No other project is included.

## Preservation and publication

- PRs #1–4 merged; [PR #5](https://github.com/Hong-yiii/neuro_science/pull/5) remains
  the open research-consolidation PR. Its reviewed `af5c3eb` was the integration
  base. Consolidation does not merge the PR or alter remote history.
- All **33 original dirty/untracked source/doc files** recorded in the
  [original-state inventory](../archive/workspace-20260910/originals.json).
  Formatting-only differences retained as patches; superseded reports retained
  separately rather than overwriting corrected release text.
- The latest preprocessing study's nine previously untracked report/code/test
  files, navigation changes, execution snapshots, lightweight receipts and
  required-private-input hashes are included in this update.
- **17,668 local-only files, 2,040,409,009 bytes**, moved and SHA-256/symlink-verified
  under the canonical repository. Scientific outputs remain in `outputs/`;
  exploratory work/session artifacts remain in `work/retired-worktrees/`.
- Raw data, main-checkout outputs, PDFs, runtime environments, accepted and failed
  experiments, Git branches/stash and native session history were retained.
  They were not uploaded as a substitute for private backups.
- Current source package: `SHA256SUMS` beside this ledger, verified from repo root.
  The old September 8 broad checksum list is historical at `af5c3eb`; it is not a
  current-tree checksum claim. Original checksum lists are archived.

## Verification

| Check | Result / boundary |
| --- | --- |
| Original dirty-file preservation | 33 files copied with matching SHA-256 before switching branches; original commits recorded. |
| Git rollback bundle | `git bundle verify` passed; includes refs and canonical stash, not ignored data. |
| Local migration | All 17,668 mapped destinations matched original hashes/symlink identities; 2,697 directory modes checked and 427 restored to their original permissions. |
| Consolidated software suite | Final 97 tests passed (earlier candidate: 96); invented data/tiny CPU fits only; two named private-input tests excluded. Relocation regressions cover both CV packaging and the final CLI, with fitting mocked/forbidden and corrupted frozen inputs rejected. |
| V6–V9 | Report/code/tensor hashes, 52 fit records, 52,000 saved loss rows, 24 recomputed metric rows and eight non-fitting tests passed. Saved checkpoint-reload receipts checked, not checkpoint reload repeated. |
| Path generalization | 342 fit records, 510,000 updates, 4,488 artifact hashes and 42 numeric-prefix pairs checked; exact family p remains 19/21; zero new fits. |
| Endpoint | 2,251 baseline + 5,515 follow-up hashes and 690 + 1,618 metric rows checked; zero fits/checkpoint loads/raw or original-split access. |
| Preprocessing numerical replay | Passed in 12m02s: 82,283 forward replays, 100 ordinary + 100 temporal null worlds, 200 source bootstraps, zero new fits. Local `preprocessing-replay.json`; tracked summary in `verification.json`. |
| Fresh Git checkout and package | Commit `2e17e73`: both submodules initialized from remotes; 97 tests, 298 current package checksums and the 98-file path package passed; clean clone afterward. Retained interpreter used; no new-runtime installation claim. |
| Independent final review | [No findings; approved immutable `2e17e73`](review-final.md) for push/deletion from preservation standpoint. That commit was published to PR #5 before removal. |
| LSP/static checks | Two initial imported files and the small software runner confirmed clean; large driver/test checks timed out. Independent review classified pre-existing generic throw flags as fail-closed propagation: the CLI logs failures and re-raises. The named PackageNotFoundError catch is not bare. No blanket type-clean claim. |

Detailed local commands/logs/receipts live in
`outputs/workspace-consolidation-20260910/`. The inventory/removal scripts and
rollback source copies are retained in `work/workspace-consolidation-20260910/`.
The one failed integration attempt was a `git apply --check` against a README
changed since the preprocessing branch fork; nothing was applied by that check.
The newer release correction (50 observed encoders checked, not all 342 fits)
was retained during manual integration.

## Removal status

**Complete:** four redundant neuroscience worktrees removed with Git's worktree
command after publication, review and per-file recovery checks. The final
preflight checked 243 preprocessing, 182 path, 244 release and 102 endpoint
remaining source/doc files, plus all 17,668 migrated local files and 2,697
directory modes. Only `~/neuro_science` remains as a local folder and registered
worktree. Branches, stash, source snapshots, local artifacts and native session
history are retained. The exact removal receipt is `removal.json` beside this
ledger.

The first removal attempt correctly stopped before deleting anything because
this audit's own marksman language server still used a sibling cwd. Only that
identified child (PID 47459, parent current Pi) was stopped; the prior user Pi
process was not killed. The successful retry retained its failure log locally.

The stale Mac registration's index matched Git commit `4946c1b`; its metadata was
copied to `work/workspace-consolidation-20260910/stale-mac-registration/` before
pruning just that stale registration. No inaccessible Mac contents were touched
or claimed backed up. See [current workspace guide](../../workspace.md) for paths
and remaining private-backup requirements.

No biological model fitting, new data acquisition, cohort expansion, Pi-history
rewriting, user-session termination, service change or non-neuroscience cleanup
was performed. Reproducible code/report delivery is **not** a verified off-host backup
of the private dataset and exact historical outputs.
