No findings.

APPROVE execution with limits. Content success: satisfied for the execution gate. Operational success: satisfied for bounded tests/static checks available to this review. Instruction compliance: satisfied; I did not run biological fits, raw/importer/split exports, or unbounded experiments.

Verified evidence:
- Frozen artifacts match the requested hashes: `outputs/path-generalization-20260907/frozen/driver.py` SHA256 `2821317f843ca2b285f2db20d9587c5dd594511e42b5fd63ad304130e4417de1`; `frozen/protocol.md` SHA256 `14e13571233b12727b7ab5e51022eddb6e379bfbe881ba83f405afcd6e14483b`. The live script and frozen driver bytes are identical.
- Prior AB/C review blockers are stale against the current snapshot. Current code enforces named Track-C target columns without fallback in `per_unit_rows_from_export`; regression test `test_named_target_cannot_fall_back_to_old_middle_label` passed.
- Static 24-component behavior ranking now uses gate-qualified training totals for tie-breaks. In-memory check on accepted V6 mapping selected `D_N_C_M__N_C_B` with `11` qualifying sessions and `267` qualified sources; old middle `D_N_R_T__N_R_M` is rank 5 with `5` sessions and `134` qualified sources. Winner remains prechosen and behavior-only.
- Relaxed40 controls use actual per-session source rows (`raw_total`, `raw_binned`, `trial_index_only`) and are tested not to call `build_dataset`.
- Source-budget curves use moment-exact ridge with nested source subsets and sliced `X/M/metas` alignment. Source-ID control is train-manifest-only; exact validation one-hot features are asserted all zero.
- Moment-exact train-Q PCA is wired into Track A outputs and matched same-row PCA heads are included in the row grid.
- Known-truth Gaussian control uses the declared `5,3,2,6,6,6,1` layout, vectorized validation draws, true analytic metrics, and raw ranking scores for AUROC.
- Track B config reports 62 observed fits, 14 family configs, and 280 null fits; code enforces exact-Q validation, full 20-null completion for non-quick runs, artifact hash reuse checks, reload parity, and 1000-step long/short prefix equality.
- Track C model gate requires `--target-mode both`, at least 100 ordinary + 100 temporal nulls, coherent joint label shuffles for all three targets, and family-max p-values.

Commands run:
- `sha256sum outputs/path-generalization-20260907/frozen/driver.py outputs/path-generalization-20260907/frozen/protocol.md` — passed, hashes matched.
- `cmp -s scripts/place195_path_generalization_phase1.py outputs/path-generalization-20260907/frozen/driver.py` — passed, bytes equal.
- `PYTHONDONTWRITEBYTECODE=1 /home/hongyi-home-lab/neuro_science/scratch/v6-v9-runtime/bin/python -m pytest -q -p no:cacheprovider scripts/test_place195_path_generalization_execution.py scripts/test_place195_path_generalization_phase1.py` — passed, 30 tests.
- In-memory behavior-ranking check against accepted V6 mapping — passed, selected supported_middle rank 1 with 11/267 and old middle 5/134.
- `cebra_config_manifest()` inspection — passed, 62/14/280.

Execution limits: launch only the frozen bounded plan; keep original test exposure off-limits; label outputs exploratory/smoke as appropriate; do not claim simultaneous population biology, intention, mechanism, or confirmation. If executing `outputs/.../frozen/driver.py` directly, run from repo root with `PYTHONPATH=.` or use the byte-identical reviewed `scripts/place195_path_generalization_phase1.py` entrypoint.

Residual risks: biological runtime and full GPU null family were not run by this review; positive development results remain exploratory and require the protocol’s claim ceiling.

```acceptance-report
{
  "criteriaSatisfied": [
    {
      "id": "criterion-1",
      "status": "satisfied",
      "evidence": "No blocking findings; frozen hashes verified, stale prior blockers checked against current code/tests, residual risks listed."
    }
  ],
  "changedFiles": [
    "work/research-planning/frozen-execution-gate-review.md"
  ],
  "testsAddedOrUpdated": [],
  "commandsRun": [
    {
      "command": "sha256sum outputs/path-generalization-20260907/frozen/driver.py outputs/path-generalization-20260907/frozen/protocol.md",
      "result": "passed",
      "summary": "Matched requested driver/protocol SHA256 values."
    },
    {
      "command": "pytest -q -p no:cacheprovider scripts/test_place195_path_generalization_execution.py scripts/test_place195_path_generalization_phase1.py",
      "result": "passed",
      "summary": "30 passed in 1.63s under the V6-V9 runtime."
    },
    {
      "command": "in-memory Track-C component ranking and cebra_config_manifest checks",
      "result": "passed",
      "summary": "Ranking selected D_N_C_M__N_C_B with 11/267; old middle 5/134; CEBRA grid 62 observed, 14 family configs, 280 null fits."
    }
  ],
  "validationOutput": [
    "driver SHA 2821317f843ca2b285f2db20d9587c5dd594511e42b5fd63ad304130e4417de1",
    "protocol SHA 14e13571233b12727b7ab5e51022eddb6e379bfbe881ba83f405afcd6e14483b",
    "30 passed"
  ],
  "residualRisks": [
    "Full biological execution and GPU null family were not run by this review.",
    "Direct frozen-driver launch needs repo-root PYTHONPATH=. or use the byte-identical scripts entrypoint."
  ],
  "noStagedFiles": true,
  "diffSummary": "Review artifact only; no source edits.",
  "reviewFindings": [
    "no blockers"
  ],
  "manualNotes": "APPROVE execution with protocol claim limits; do not treat smoke tests or development outputs as confirmatory biological results."
}
```
