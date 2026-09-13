# Original exploratory working states

Captured before takeover of the canonical checkout; consolidated September 13,
2026 in the session begun September 10. These are **recovery sources**, not a
second live research handoff.

`originals.json` records the five worktrees' original commits/branches and all
33 dirty/untracked source/doc files, including hashes and comparison with PR #5
at `af5c3eb`. Each worktree's `tracked.patch` is a binary-capable Git diff against
its listed original commit. Apply only to a scratch checkout at that commit, not
blindly to current code. The old commits remain in Git history.

Untracked files identical to PR #5 are recoverable there. New preprocessing files
are now active tracked files, with original driver/test/verifier/renderer bytes
also in the [study archive](../path-preprocessing-20260908/README.md). Differing
older untracked synthesis/endpoint notes are preserved here as `.txt` files, not
allowed to replace the corrected current reports. Exact working copies of every
inventoried file also remain in ignored
`work/workspace-consolidation-20260910/originals/`.

The baseline, path-package verifier and endpoint-verifier dirty patches were
independently AST-compared and contain formatting-only changes. They are retained
but not substituted for hash-identified execution/release code.

`checksums-before/` preserves the two old package checksum lists before the
current navigation documents changed. The path package's active checksum list
has only its AGENTS/README entries resealed; protected path code, report and
scientific evidence remain unchanged. The original broad September 8 release
checksum list remains historical, verifiable at commit `af5c3eb`; use the new
consolidation ledger's checksum list for the current tree.

Local data, models, environments, PDFs and session logs are not in this archive
or in Git. See [workspace recovery](../../../workspace.md) for the hash-verified
migration and the separately retained pre-cleanup Git bundle.
