# Release receipts and review chronology

**Current disposition: prior findings resolved; final committed-snapshot reviews report no findings within their stated scopes.** These are AI-assisted packaging/scientific-claim checks, not human peer review or biological replication.

## Current evidence

- [Preservation manifest](preservation-manifest.json): 30 origin/copy records, 70 shipped Python/archive-code hashes, 49 archival provenance records / 26 unique contents. Capture-time and final source identities are distinct. The replaced intermediate is archive-only; new concurrent management work is explicitly outside this completed-study snapshot.
- [Leaf integration](leaf-integration.json): exact reviewed leaf `9e0457438c901ad6aa0c06be107d2cc130e7a884`; four documentation checksum entries resealed for combined navigation/scope. Protected code, report, archives and local inventory unchanged.
- [Merged-tree checks](final-merged-checks.log): 82 software/synthetic tests, Python parsing, rejection of optimized verification, 98 package hashes, nine unchanged tables, 12 figures and retained local artifact hashes. The local inventory is relative to the **owning path worktree**, not this code-only release checkout.
- [Saved-artifact verification](saved-artifact-verification.log): accepted V6–V9/path checks and 2,308 endpoint metric recalculations. No biological fitting or checkpoint reload.
- [Final snapshot review](review-snapshot-final.md): committed `ffe72ad981b7eb513aa490c67ebf816993a46c34`, no findings. At that snapshot the archive had 46 records / 23 contents and 67 code hashes.
- [Final preservation-delta review](review-snapshot-delta.md): committed `9ab784ce4b6791fb3a4d691fc4de0b3517e43a5c`, no findings. Added three historical transfer-helper text archives and updated counts to 49 / 26 / 70; no helpers executed or cohorts expanded.

## Historical receipts — not unresolved blockers

- [Initial scientific review](review-scientific-initial.md) found stale simultaneous-data-first normative gates. [Scientific recheck](review-scientific-final.md) verified resolution: condition-level pseudopopulation work stays legitimate; exact same-trial claims keep stronger observation requirements.
- [Initial packaging review](review-packaging-initial.md) found stale copy hashes, an unavailable intermediate source pointer and missing PCA provenance. All were corrected without rewriting protected scientific bytes.
- [Precommit recheck](review-packaging-precommit.md) validated those corrections but found the manifest untracked. Commit `350ae17` added it; both committed-snapshot reviews confirmed its presence and matching hashes.
- [Earlier code-only tests](code-only-tests.log) passed on the integration candidate. The merged-tree log above is the later check; repeated tests/receipts are not additional independent experiments.

An initial local-inventory attempt (`b171b675c`) failed because its cwd had no retained outputs. The corrected owner-cwd run (`bba7f2930`) passed with the inventory and artifacts unchanged. This was a command-location error, not repaired data corruption.

`SHA256SUMS` in this directory inventories the final changed-file delivery, excluding itself. From repository root, run `sha256sum -c docs/reports/release-20260908/SHA256SUMS`. It checks shipped bytes, not ignored model/data recovery. Original worktrees and runtime remain necessary for the separately scoped saved-result checks.
