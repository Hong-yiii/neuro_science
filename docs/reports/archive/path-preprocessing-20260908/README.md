# Completed preprocessing study: historical execution evidence

Packaged during the September 10 session, resumed September 13, 2026. These are
byte-preserved sources/receipts from the completed September 8 study, **not new
execution or permission to reopen fitting**.

- `provenance.json` maps each archived file to its original location and SHA-256.
- `code/gated-export-round1/` and `code/final-inference/` preserve the execution
  snapshots. `code/completed-study/` preserves the final driver, test, verifier and
  renderer before consolidation's path-portability change.
- `code/helpers/` preserves the prefit audit, descriptive summary, delivery check
  and bundle builder. Historical helpers may write files or access broader input
  metadata; `.py.txt` files are archival text, not recommended entry points.
- `receipts/` preserves the protocol, selection, decision/failure/review record,
  descriptive audit, accepted final aggregate and original no-fit verification.
  Pending-review flags inside frozen receipts are historical chronology.
- `required-local-inputs.json` identifies required private inputs and manager files
  by repository-relative path, size and hash. Their contents remain ignored; no
  raw tables, source tensor, checkpoint or protected source manifest is uploaded.

The original verifier receipt records 82,283 forward replays with zero new fits.
It is not the new post-migration check. Its file map only covers artifacts present
at its execution time; later delivery files are covered by the local migration
inventory. Full accepted and interrupted outputs are retained in `outputs/`.

The active driver differs only in repository-relative manager resolution,
hash-checked resolution of the old Round1 path alongside the supplied Round2 run,
role/hash validation of relocated final-CLI inputs, and use of these Git-backed CV
snapshots. The fitter, selected sources, controls,
model predictions and historical receipts were not rewritten.

See [workspace/recovery instructions](../../../workspace.md) and the
[current study review](../../path-preprocessing-review-20260909.md).
