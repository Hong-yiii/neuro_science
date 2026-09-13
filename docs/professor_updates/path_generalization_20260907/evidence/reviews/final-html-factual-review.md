medium — work/research-planning/report-draft-handoff.md:40 — generator hash no longer matches the current generator file

Verified evidence: the handoff records `generator_sha256` as `2c77fb2b025a316d6674000ca9d7547f2240b08910632ef6f0cf6ca10824062a`, but `sha256sum scripts/build_path_generalization_report.py` now returns `98726528f5fcc0d50c428a06734c4f0e53e2f97b6dd339a4f885281b01e03a95`. Impact: HTML hash/provenance is otherwise intact, but the requested generatorSHA cannot be attested against the current file. Minimum fix: restore the exact generator used for the handoff or update provenance to explicitly say the current generator has changed after producing the reviewed HTML.

No science/content blockers found in the HTML. Verified highlights:
- HTML SHA-256 matches requested `8fa2d4b7a6f89efdb80ca56b3d84425ec948d9c7885823e016a02de91831820c`.
- Track B exact audit is authoritative: 342 fits, 510,000 updates, 42 prefix pairs, exact corrected `p=19/21=0.9047619047619048`; raw producer `0.8571428571428571` is retained only as an execution artifact.
- Track C values match saved summaries: Δ log loss `-0.0106805 / 0.001878 / 0.003860`; family p-values `0.475 / 0.436`; supported-middle cohort `267 train / 52 validation sources`, `43 units`, `11 sessions`, train-behavior-only target selection.
- Rank/covariance/statistical caveats are correctly bounded: Q validation `24/6`, class weight `0.5`, WHOLE-CUE `30×290` rank `9`, not brain/PCA29/CEBRA rank; covariance assumptions and proper-score caveats are stated.
- Artifact integrity: 12 inline SVGs, 12 SVG title/role pairs, no duplicate SVG IDs, no missing internal refs, no scripts/links/src/srcset/external autoloads, mode final, no “pending”.
- Appendix row counts match derived CSVs: A1 `88`, B1 `62`, B2 `20`, B3 `42`, C1 `70`.

Residual risks: browser rendering is explicitly left to parent; this was a read-only artifact/text review, not a raw/importer/split-file audit or new-fit validation. Existing development limits remain: exposed original holdout, coarse B/C null resolution, no confirmatory biological claim.