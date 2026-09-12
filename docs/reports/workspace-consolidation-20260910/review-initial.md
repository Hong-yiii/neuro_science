# Initial independent consolidation review — September 13, 2026

Summary of reviewer run `6735f0eb-78e5-4578-b64e-e113aa959a5b`.
The full tool/session trace remains local, not in Git.

The first review withheld deletion/push approval for three findings:

1. **Final CLI relocation:** `cmd_final` still indexed the frozen input hashes by
   old absolute paths. Required fix: bind each input to its unique frozen role and
   original content hash; add a no-fit final-CLI regression.
2. **Package manifest:** the ledger described a current `SHA256SUMS` that had not
   yet been generated. Required fix: create and verify it before publication.
3. **Replay status:** the 82,283-model no-fit replay had completed while the
   reviewer worked, but the ledger still said in progress. Required fix: record
   the completed result and receipt.

The reviewer also inspected the generic scanner findings: invalid scientific
inputs intentionally fail closed; the CLI records `failure.json` and re-raises.
It did not request swallowing parsing exceptions. The existing specific
`PackageNotFoundError` handler is not a bare exception clause.

These findings were addressed and submitted for follow-up review. See the
[consolidation ledger](README.md) for final acceptance, tests and residual limits.
