# Path-generalization study: report, code, evidence and next steps

**Completed exploratory study; packaged 2026-09-08. No confirmatory biological claim.**

## Start here

1. [Self-contained teaching report](path-generalization-teaching-audit-20260907.html) — download/open locally;12 embedded figures, full numerical tables, methods and reasoning. No JavaScript or remote autoloads.
2. [Current next-study plan](../../reports/path-generalization-next-steps-20260908.md) — source-safe pseudopopulations remain central under the monkey-recording constraints; source-level replication matters more than manufactured row count. Per-unit controls are complementary, not a requirement for individually significant cells.
3. [Status / deprecation ledger](STATUS.md) — accepted versus failed/superseded results, historical reviews and corrected inference.
4. [Packaging corrections](CORRECTIONS.md) — original release preserved; Figure1 label corrected and post-release interpretation collated. Models and numerical tables unchanged.
5. [Frozen prefit protocol](../../reports/path-generalization-prefit-20260907.md) — executed historical specification, not the next-study plan.

The preceding [V6–V9 report](../../reports/place195-v6-v9-autoresearch-20260906.md) and its code were already merged into `main` in PR#4. This package adds the follow-up rather than duplicating that work. H1a/H1b and exact-trial observability limits remain in [research questions](../../research-questions.md) and [analysis contract](../../analysis-contract.md).

## Findings worth carrying forward

- **342 new native CEBRA fits, 510,000 updates:**62 observed and280 source-null fits. All42 paired1000-step prefix comparisons and producer reload checks agree numerically.
- **Same-source versus source-disjoint:** unseen mixtures of training sources give Time BA0.9925/Behavior0.997656, versus factorial source-disjoint exact-Q means0.249167/0.351667. This locates a failure boundary, not a uniquely established cause.
- **No consistent rescue:** more synthetic rows, dimensions or training steps did not consistently improve transfer. Exact ridge BA0.479167 supplies a finite-source reference.
- **Corrected B-family inference:**18/20 inclusive exceedances, **p19/21≈0.904762**. The observed maximum and null19 both equal7/12; raw float comparison incorrectly excluded that tie. See [exact audit](evidence/audits/track_b_exact_audit.json) and [authoritative B summary](evidence/track_b/summary_exact_audited.json), not the archived producer p-value.
- **Track C:** the train-behavior-selected supported-interior target has43 units/11 sessions,267 train/52 validation sources. Its weak positive Δlogloss does not pass the three-target family null (p≈0.475 ordinary/0.436 temporal).
- **Provable construction result:** the290-feature whole-cue validation matrix has rank9 under the finite-source product construction. This is not the brain's intrinsic dimension.

All work stays within the195 selected-unit scope. No excluded supplement was restored. Original test exposure is permanent; no new test-model evaluation or pristine confirmation occurred. Pseudopopulations do not reconstruct simultaneous cross-session dynamics, and BA here is binary component classification—not full-path accuracy.

## What this PR actually contains

| Included in Git | Retained locally, NOT uploaded by this package |
| --- | --- |
| Current and archived teaching reports; current plan; frozen protocol | Native lab/importer data and the original test records |
| All analysis/report/replay/verification code and tests | Source/pseudo arrays, saved neural checkpoints and per-trial predictions |
| Exact B/C and A-v2 executed driver snapshots; original report-generator snapshot | Full fit inventories, loss traces and loader exposure/manifests |
| Compact aggregate tables, gate/correction receipts and independent review documents | Full local preflight/failed-run outputs and render PDF/PNG checks |
| Status ledger, byte-preserved provenance mapping and checksums | Existing isolated research runtime and other worktrees' work |

The source files are:

- [Full A/B/C driver](../../../scripts/place195_path_generalization_phase1.py) — historical `phase1` filename; includes the completed execution stages and the later floating-tie regression fix.
- [Source/analytic tests](../../../scripts/test_place195_path_generalization_phase1.py) and [execution regressions](../../../scripts/test_place195_path_generalization_execution.py).
- [Frozen-checkpoint assembly replay](../../../scripts/replay_path_generalization_assemblies.py).
- [Report generator](../../../scripts/build_path_generalization_report.py).
- [Read-only saved-results verifier](../../../scripts/verify_path_generalization_results.py).
- [Portable package/presentation checker](../../../scripts/verify_path_generalization_package.py) — stdlib only; no local science data needed.

[Exact historical code](archive/code/) uses `.py.txt` so it is clearly an archive, not another active entry point. B/C used `driver_bc_20260907.py.txt`; A-v2 used the reader-only corrected snapshot. These are deliberately distinct from the live driver. Helpers inherited from V6–V9 remain tracked in `scripts/`.

[Promoted-file mapping](promoted-files.json) records source locations, sizes and hashes of byte-preserved receipts. Historical absolute paths, `work/` links, gate states, HEADs and “no commits” statements describe their recorded moment; they are not the current PR state. Resolve them through this index rather than treating an old handoff's `ACTIVE_RUN` or `final` filename as live status.

**Retention is not offsite backup.** The checksum inventory proves which local artifacts were present at packaging; it does not upload or back up their bytes. A code-only clone supports reading and package-integrity checks, not full scientific reproduction. All present source and executed snapshots are preserved; the package does not claim every transient preflight edit was independently snapshotted.

## Verify without fitting

Run commands from the repository root; do not use Python `-O` because the result verifier uses assertions.

### Any clone: shipped bytes

```sh
sha256sum -c docs/professor_updates/path_generalization_20260907/SHA256SUMS
python scripts/verify_path_generalization_package.py
```

The second command also checks unchanged numerical tables,12 embedded figures,
internal references and the corrected route-example label against packaged
behavioral evidence. It is not a replacement for the full scientific audit.

### Data-equipped homelab: retained bytes and saved results

The current run lives in `/home/hongyi-home-lab/neuro_science-path-diagnosis/outputs/path-generalization-20260907/results-20260907T081200Z`. Earlier V6–V9 inputs remain under `/home/hongyi-home-lab/neuro_science/outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906`.

```sh
sha256sum -c docs/professor_updates/path_generalization_20260907/LOCAL_SHA256SUMS
python scripts/verify_path_generalization_results.py \
  outputs/path-generalization-20260907/results-20260907T081200Z
```

The stdlib-only verifier hashes4488 fit artifacts, checks342 fit inventories/510000 loss rows/42 saved prefix receipts, source disjointness and weights, and recomputes exact B inference plus both C null families. It does not refit, reload checkpoints, audit raw laboratory data, or validate all of A's mathematics. It needs the retained complete run tree, not only the compact `evidence/` copies.

### Research runtime: software and report checks

Existing host interpreter: `/home/hongyi-home-lab/neuro_science/scratch/v6-v9-runtime/bin/python`. [Environment receipt](evidence/environment.json) records versions; it is not a portable lockfile. No environment was installed or changed for this PR.

```sh
PY=/home/hongyi-home-lab/neuro_science/scratch/v6-v9-runtime/bin/python
export PYTHONPATH="$PWD" PYTHONDONTWRITEBYTECODE=1
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
"$PY" -m unittest \
  scripts.test_place195_path_generalization_phase1 \
  scripts.test_place195_path_generalization_execution \
  scripts.test_place195_split_filtered_access \
  scripts.test_place195_v7_v8_neural_experiments
"$PY" scripts/build_path_generalization_report.py --mode final --dry-run
```

The38-test suite and complete saved-result audit passed again at packaging. The existing V6–V9 auditor also passed its8 selected tests and recomputed24 CEBRA metric rows. Those test sets overlap: do not claim46 unique tests. [Verification log](evidence/packaging-verification.log).

For a deliberate rebuild, use fresh destinations rather than overwrite either release:

```sh
STAMP=$(date -u +%Y%m%dT%H%M%SZ)
RUN=outputs/path-generalization-20260907/results-20260907T081200Z
"$PY" scripts/build_path_generalization_report.py --mode final \
  --assets-dir "$RUN/report_assets/rebuild-$STAMP" \
  --output "docs/professor_updates/path_generalization_20260907/rebuild-$STAMP.html"
```

Scientific refitting is separate: it requires the retained source inputs, frozen configuration/runtime, fresh output destinations, and reviewed data-access gates. Do not rerun against an accepted output directory or infer that these aggregate copies are a new training dataset.
