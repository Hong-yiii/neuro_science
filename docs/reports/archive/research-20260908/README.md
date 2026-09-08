# Historical source archive — not active entry points

**Status: archival, 2026-09-08 consolidation.** [Code provenance](code-provenance.json) maps 49 recorded project-code sources (including one superseded packaging intermediate, the original PCA helper and three historical transfer-audit helpers) to 26 distinct byte-preserved snapshots. Relative source locations are under `/home/hongyi-home-lab/`; explicit `/tmp/` locations are historical temporary sources. `source: null` marks the replaced intermediate as archive-only, not a still-verifiable original file. Archive paths are relative to this directory unless `archive_base` is `repository` (the PCA helper in `learning/`). Identical source versions share one archive file; distinct versions are not silently replaced by the latest script. Active consolidated runners/tests live in `scripts/` at repository root.

These `.py.txt` files are retained for execution provenance, not automatically imported/discovered as tests. A snapshot is not proof of a successful or scientifically valid run. Some contain historical absolute paths or assumptions. **Do not rename and run them blindly.** In particular:

- Old `verify_artifacts` reads the original outer split-assignment table and writes a receipt. It is not the new saved-artifacts-only verification route.
- Old `verify_study` can load trusted local checkpoints and writes `validation.json`; it is not a read-only receipt check. Older unrestricted `torch.load` calls are historical, not recommended loaders.
- `recheck_delivery` rebuilds into disposable files and updates a delivery receipt. Do not execute it against a frozen accepted delivery merely to read results.
- Initial path drivers and raw floating-point inference are superseded where the current exact tie audit says so; do not choose the more favorable p-value.
- Plot/report builders may write historical output destinations. Preserve accepted reports before rebuilding; active report builders expose their own output options.

The separate [PCA plot builder](../../../../learning/archive/pca-explainer-build-20260907.py) is also retained byte-for-byte and documented by the current teaching lesson. Its `/tmp` browser links are disposable and superseded by tracked documents.

The source archive contains no checkpoints, arrays, raw lab tables, model runtimes or imported third-party package trees. It is not a backup of the approximately gigabyte-scale local study outputs. See the [retention ledger](../../research-release-20260908.md) and [current index](../../README.md) for accepted authorities and recovery limitations.
