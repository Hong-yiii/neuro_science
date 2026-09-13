blocker — docs/reports/release-20260908/preservation-manifest.json:153 — preservation manifest hashes are stale.

Verified: recomputing `source_copies` hashes found 6 mismatches, including current packaged files whose `packaged_sha256` no longer matches the file bytes and source files whose `sha256` no longer matches the sibling. Non-path examples include `docs/reports/recent-learnings-20260908.md` and `docs/reports/recent-learnings-20260908-agent.md`; path-leaf examples are expected to be resynced. Impact: the preservation attestation cannot be trusted as a final release receipt. Minimum fix: after final path sync, regenerate/update `preservation-manifest.json` from current source and destination bytes and rerun the manifest hash check.

medium — docs/reports/archive/research-20260908/code-provenance.json:332 — provenance source path is not portable/verifiable.

Verified: the entry points to `isolated first-copy/scripts/build_path_generalization_report.py`, but that path does not exist under `/home/hongyi-home-lab`; `find` located only the path-diagnosis and release copies. The archive file itself exists and hashes correctly, but the source-side provenance for 1/42 entries cannot be independently checked. Minimum fix: either point to an existing retained source, or explicitly mark this as an unavailable/superseded intermediate with archive-only provenance.

low — docs/reports/research-release-20260908.md:10 — PCA “original plotting script” byte-for-byte claim lacks provenance.

Verified: the docs claim the original PCA plotting script is preserved byte-for-byte, but it is not listed in `code-provenance.json` or `preservation-manifest.json`; `find /home/hongyi-home-lab -name pca-explainer-build-20260907.py` found only the release copy. Impact: readers cannot verify “original” or byte identity. Minimum fix: add a provenance/manifest entry with source path and hash, or reword as an archived release helper without original-source attestation.

Grades:
- content success: partial, blocked by stale preservation/provenance metadata.
- operational success: partial, endpoint verifier passed but manifest validation failed.
- instruction compliance: satisfied; review stayed read-only and did not inspect raw/importer/original-split contents.

Residual risks:
- Known path leaf sync still needs final checks: `docs/professor_updates/path_generalization_20260907/README.md:43` links to missing `scripts/verify_path_generalization_package.py`, and `STATUS.md:67` links to missing `local-artifact-inventory.json`.
- External citation URLs were not network-checked.