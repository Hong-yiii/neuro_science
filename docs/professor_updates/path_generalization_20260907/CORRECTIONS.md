# Packaging corrections and provenance — 2026-09-08

The original report was released7 September with SHA256 `31c745a626d4fcad3a38f7e9842dce1ac57321594aca0464904ce3718d55a2d7`. Its HTML, summary and manifest are retained byte-for-byte under [archive/release-20260907](archive/release-20260907/). The earlier8fa2d4… review copy and original593bc21… generator are also retained. Current report identity is recorded in [report-manifest.json](report-manifest.json).

## 1. Figure1: mislabeled negative-route example

The99-source route `RT→CT→CM→RM→RB` was drawn correctly, but its label said **“old absent, edge elsewhere.”** The selected edge is `RT→RM`; that route does not contain it. The [saved behavior-only route-count table](evidence/target_semantics/target_semantics_route_counts.csv) classifies all99 as `old_absent_never_component`.

The current diagram label is **“old absent: no selected edge.”** The50-source `CT→RT→RM` example remains an edge-outside-interior example. The overall51/185 old-absent paths containing the edge outside the interior, all neural target assignments, metrics and conclusions are unchanged. This was a presentation error, not a relabeling or refit.

## 2. Practical interpretation after the recording-constraint discussion

The report's direction section now explicitly keeps source-safe pseudopopulations central for condition-level prospective-path coding. It does not demand a large simultaneous195 recording. Track C provides complementary real-trial checks, not an individual-cell-significance gate or a reason to abandon population analyses.

Independent source-trial support, reproducibility, condition semantics and nuisance controls are priorities. The observed gap is not proof that insufficient data is its sole cause; another CEBRA formulation is neither ruled out nor a demonstrated cure. The [current plan](../../reports/path-generalization-next-steps-20260908.md) is a proposal, not another completed experiment.

## 3. Historical status versus PR state

Old planning documents, reviews, manifests and code snapshots are preserved rather than rewritten to erase failures or fix their historical hashes. The [status ledger](STATUS.md) identifies what each version supersedes. In particular, earlier “final” blocking reviews were resolved before the frozen execution gate, and the original release's “no commits” statement describes that date, not the later PR.

The B floating-tie correction predates this packaging change. Its authoritative result remains18/20 inclusive exceedances and **p19/21**, not the raw producer's17/20 and0.8571429. All accepted model artifacts and frozen producers remain untouched.

## Validation boundary

Packaging re-runs software and saved-artifact checks, compares all nine embedded tables against the original release, and rechecks rendering after the presentation changes. It does not train new biological models, parse raw lab data, evaluate the original test, or change selected-cell scope. See the verification receipts and final packaging review under `evidence/`.
