# Phase 1 implementation handoff — path generalization diagnosis

Status: phase 1 complete: implementation, unit/synthetic tests, saved-artifact schema inspection, behavior-only target support/ranking, and behavior-label target semantics audit only. No biological fits, semantic response analysis, original importer/split table access, or mixed-importer cue-count extraction were run.

## Current authorization gate

Parent gate remains closed for biological/development neural execution. The CLI enforces `--authorized-phase reviewed-code-data-gate` before `run-track-a`, `run-track-b`, `export-track-c-counts`, or `fit-track-c-models`.

Protocol hash after final steering sentence: `8122691b8c28fc67d3582580cfcb55557ed95bc3366506aa8ef54b054829cf76` for `docs/reports/path-generalization-prefit-20260907.md`.

## Changed files

- `docs/reports/path-generalization-prefit-20260907.md` — phase gate, Track A/B/C caveats, three frozen Track C targets, and final Track B evaluation-only replay sentence.
- `scripts/place195_path_generalization_phase1.py` — phase-1 CLI and gated future runners for Track A/B/C, plus schema/behavior inspections, exact-Q utilities, synthetic smokes, and plots.
- `scripts/test_place195_path_generalization_phase1.py` — 22 focused unit/synthetic tests.
- `work/research-planning/implementation-phase1.md` — this handoff.

Own outputs were written only under `outputs/path-generalization-20260907/`, including final `*_three_target_final/` directories.

## Final implementation summary

### Track A

- Exact validation empirical-Q support and class-balanced weights.
- Product moments with block-diagonal conditional covariance and balanced-mixture between-class term.
- Train-Q standardized ridge, mapped back to raw coordinates, using `P(present)=clip((score+1)/2)` for probability metrics.
- Finite-sample matched ridge convergence arm, raw/PCA/source-index controls, source margins, leave-one-session blocks, source-budget controls, relaxed40 source-preserving checks, known-truth simulations, and legacy V8b/V9 replay paths.

### Track B

- Frozen config remains 62 observed fits and 14 null-family configs × 20 permutations; no new architecture/target/fit budget added.
- Gated future runner has exact-Q validation, label-shuffle full pipeline, fit identity/resume checks, loader exposure summaries, checkpoint/loss/prediction artifacts, family-max BA p-values, and prefix parity checks.
- Final steering incorporated as protocol text only: parent may later replay the 50 factorial checkpoints on training pseudo-arrays from other assembly seeds with all weights/preprocessing frozen; this tests memorized sampled combinations vs same-training-source-pool transfer and is not independent biological validation.

### Track C

- Scope frozen to exactly three targets: `middle`, `anywhere`, and `supported_middle`.
- `supported_middle` is fixed to `D_N_C_M__N_C_B`, selected by behavior/support-only ranking of 24 static directed components; no neural performance search.
- Allowlist/export/model paths carry `middle_component_label`, `anywhere_component_label`, and `supported_middle_component_label`.
- Selected-cell scope is fixed to 195 cells; canonical hash verified as `2924d60f9a52ad7c02e802c28e84a85c6267da023267ac1b507b957e0587f60d`.
- Per-unit models use unique-source eligibility, endpoint intercepts, train-only centering/standardization, convergence checks, saved predictions/artifacts, and 100 ordinary + 100 temporal null gate for biological inference.
- Null family uses one joint source-label tuple shuffle across all three targets and family max target `family_max_three_targets`.

## Final saved artifacts / checks

- Schema inspection: `outputs/path-generalization-20260907/phase1_schema_inspection_three_target_final/`, `schema_count=21`, manifest hash `4d04038fc05b84091376b2b39989b72456a3398e2012d1dbb660ee65682871b3`.
- Track B config: `outputs/path-generalization-20260907/track_b_config_three_target_final/`, `observed_fit_count=62`, `null_family_config_count=14`, hash `09a15c80f942939eb8c4de586a5933c503420df6d59268bf3236616180c6c780`.
- Track C three-target allowlist: `outputs/path-generalization-20260907/track_c_allowlist_three_target_final/`, source count `19162`, manifest hash `e58e8c2bf43d81456886a029dd0bfa607977f955f33a1e135ed486b792c44be8`.
  - `middle`: 38 eligible contexts, 5 sessions meeting >=20 source gate, 408 eligible train sources.
  - `anywhere`: 29 eligible contexts, 4 sessions meeting >=20 source gate, 317 eligible train sources.
  - `supported_middle`: 49 eligible contexts, 11 sessions meeting >=20 source gate, 507 eligible train sources.
- Behavior target semantics audit: `outputs/path-generalization-20260907/target_semantics_audit_three_target_final/`, audit hash `333f323bd953100b25bbc5732403af00d86cfa98462ec71ecd2747fdb11e1dfe`.
  - Fixed selected-pair sources: 475 middle-present, 134 old-absent/never component, 51 old-absent/anywhere-present outside middle.
  - Primary104 old-absent: train 24 never + 6 outside-middle; validation 10 never + 2 outside-middle.
- Synthetic smoke: `outputs/path-generalization-20260907/phase1_synthetic_smoke_three_target_final/`, summary hash `44c3897cdff663f3deb4a2036b208e055bce8a0e4822ae676bfb8d6c9c5d31f9`.
  - Track A synthetic ridge BA `0.875`.
  - Synthetic CEBRA prefix/reload diffs all `0.0`.
  - Track C three-target smoke targets `middle`, `anywhere`, `supported_middle`; null rows `12`; plots `7`.

## Verification commands run

```sh
/home/hongyi-home-lab/neuro_science/scratch/v6-v9-runtime/bin/python -m py_compile scripts/place195_path_generalization_phase1.py scripts/test_place195_path_generalization_phase1.py
/home/hongyi-home-lab/neuro_science/scratch/v6-v9-runtime/bin/python -m unittest scripts.test_place195_path_generalization_phase1 -v
/home/hongyi-home-lab/neuro_science/scratch/v6-v9-runtime/bin/python -m ruff check scripts/place195_path_generalization_phase1.py scripts/test_place195_path_generalization_phase1.py
# passed: 22 tests, ruff clean, py_compile clean
```

```sh
/home/hongyi-home-lab/neuro_science/scratch/v6-v9-runtime/bin/python -m unittest scripts.test_place195_split_filtered_access scripts.test_place195_v7_v8_neural_experiments -v
# passed: 6 existing split/V7 tests
```

```sh
/home/hongyi-home-lab/neuro_science/scratch/v6-v9-runtime/bin/python -m scripts.place195_path_generalization_phase1 inspect-schemas --output-dir outputs/path-generalization-20260907/phase1_schema_inspection_three_target_final
# schema_count=21
```

```sh
/home/hongyi-home-lab/neuro_science/scratch/v6-v9-runtime/bin/python -m scripts.place195_path_generalization_phase1 cebra-config --output-dir outputs/path-generalization-20260907/track_b_config_three_target_final
# observed_fit_count=62; null_family_config_count=14
```

```sh
/home/hongyi-home-lab/neuro_science/scratch/v6-v9-runtime/bin/python -m scripts.place195_path_generalization_phase1 build-track-c-allowlist --output-dir outputs/path-generalization-20260907/track_c_allowlist_three_target_final
# selected supported_middle=D_N_C_M__N_C_B; selected_matches_expected=true
```

```sh
/home/hongyi-home-lab/neuro_science/scratch/v6-v9-runtime/bin/python -m scripts.place195_path_generalization_phase1 target-semantics-audit --output-dir outputs/path-generalization-20260907/target_semantics_audit_three_target_final
# metadata-only behavior audit passed
```

```sh
/home/hongyi-home-lab/neuro_science/scratch/v6-v9-runtime/bin/python -m scripts.place195_path_generalization_phase1 smoke --include-cebra --output-dir outputs/path-generalization-20260907/phase1_synthetic_smoke_three_target_final
# synthetic only; no biological arrays; 7 plots
```

```sh
sha256sum docs/reports/path-generalization-prefit-20260907.md scripts/place195_path_generalization_phase1.py scripts/test_place195_path_generalization_phase1.py
# docs=8122691b8c28fc67d3582580cfcb55557ed95bc3366506aa8ef54b054829cf76
# script=76547bf65aa0a1245df1a66491050e5e21cc01df118105f18111b54608214ac8
# tests=13b7adbde5630e35743ffb7d182bf3a23b731fefbd328620fb2bf78c6ee6661d
```

Diagnostics: pi-lens `mode=all` on changed code/doc files reported no issues. Primary LSP returned zero diagnostics but one file timed out/unconfirmed, so final confidence rests on ruff, py_compile, unit tests, and smokes.

## Residual risks / closed gates

- Biological Track A/B/C execution and mixed-importer export remain blocked until parent review explicitly authorizes `--authorized-phase reviewed-code-data-gate`.
- Original holdout exposure remains permanent; all future results here are exploratory development until genuinely unexposed confirmation exists.
- Existing legacy V8b/V9 saved-manifest test was previously known to fail in this worktree because it expects a relative old-output path that is absent; focused new tests and existing split/V7 tests pass.
- Track C selected-edge traversals use `direction_source=adjacent_nodes`; no extra direction filter was added. `route_signature` remains inferred corridor directions, not guaranteed exact graph walks.

Skipped: new runner for the parent replay sentence; parent asked for protocol text only and will handle postprocessing after fits.

```acceptance-report
{
  "criteriaSatisfied": [
    {
      "id": "phase1_scope",
      "status": "satisfied",
      "evidence": "Implemented phase-1 code, tests, saved-artifact schema inspection, behavior-only ranking/allowlist, target-semantics audit, and synthetic smokes only."
    },
    {
      "id": "execution_gate",
      "status": "satisfied",
      "evidence": "Biological Track A/B/C and mixed-importer export require --authorized-phase reviewed-code-data-gate; none were run."
    },
    {
      "id": "track_c_three_targets",
      "status": "satisfied",
      "evidence": "Track C is frozen to middle, anywhere, and supported_middle; family max is family_max_three_targets with joint tuple nulls."
    },
    {
      "id": "parent_evaluation_clarification",
      "status": "satisfied",
      "evidence": "Added one Track B protocol sentence for later parent evaluation-only replay on other assembly-seed training pseudo-arrays with frozen weights/preprocessing; no runner added."
    }
  ],
  "changedFiles": [
    "docs/reports/path-generalization-prefit-20260907.md",
    "scripts/place195_path_generalization_phase1.py",
    "scripts/test_place195_path_generalization_phase1.py",
    "work/research-planning/implementation-phase1.md"
  ],
  "testsAddedOrUpdated": [
    "scripts/test_place195_path_generalization_phase1.py"
  ],
  "commandsRun": [
    {
      "command": "/home/hongyi-home-lab/neuro_science/scratch/v6-v9-runtime/bin/python -m py_compile scripts/place195_path_generalization_phase1.py scripts/test_place195_path_generalization_phase1.py",
      "result": "passed",
      "summary": "Syntax check clean"
    },
    {
      "command": "/home/hongyi-home-lab/neuro_science/scratch/v6-v9-runtime/bin/python -m unittest scripts.test_place195_path_generalization_phase1 -v",
      "result": "passed",
      "summary": "22 tests passed"
    },
    {
      "command": "/home/hongyi-home-lab/neuro_science/scratch/v6-v9-runtime/bin/python -m ruff check scripts/place195_path_generalization_phase1.py scripts/test_place195_path_generalization_phase1.py",
      "result": "passed",
      "summary": "All checks passed"
    },
    {
      "command": "/home/hongyi-home-lab/neuro_science/scratch/v6-v9-runtime/bin/python -m unittest scripts.test_place195_split_filtered_access scripts.test_place195_v7_v8_neural_experiments -v",
      "result": "passed",
      "summary": "6 existing tests passed"
    },
    {
      "command": "/home/hongyi-home-lab/neuro_science/scratch/v6-v9-runtime/bin/python -m scripts.place195_path_generalization_phase1 inspect-schemas --output-dir outputs/path-generalization-20260907/phase1_schema_inspection_three_target_final",
      "result": "passed",
      "summary": "schema_count=21"
    },
    {
      "command": "/home/hongyi-home-lab/neuro_science/scratch/v6-v9-runtime/bin/python -m scripts.place195_path_generalization_phase1 cebra-config --output-dir outputs/path-generalization-20260907/track_b_config_three_target_final",
      "result": "passed",
      "summary": "observed_fit_count=62; null_family_config_count=14"
    },
    {
      "command": "/home/hongyi-home-lab/neuro_science/scratch/v6-v9-runtime/bin/python -m scripts.place195_path_generalization_phase1 build-track-c-allowlist --output-dir outputs/path-generalization-20260907/track_c_allowlist_three_target_final",
      "result": "passed",
      "summary": "supported_middle=D_N_C_M__N_C_B; source_count=19162; selected_matches_expected=true"
    },
    {
      "command": "/home/hongyi-home-lab/neuro_science/scratch/v6-v9-runtime/bin/python -m scripts.place195_path_generalization_phase1 target-semantics-audit --output-dir outputs/path-generalization-20260907/target_semantics_audit_three_target_final",
      "result": "passed",
      "summary": "metadata-only audit: 475 middle-present, 134 old-absent never, 51 old-absent outside-middle"
    },
    {
      "command": "/home/hongyi-home-lab/neuro_science/scratch/v6-v9-runtime/bin/python -m scripts.place195_path_generalization_phase1 smoke --include-cebra --output-dir outputs/path-generalization-20260907/phase1_synthetic_smoke_three_target_final",
      "result": "passed",
      "summary": "synthetic-only: Track A BA=0.875; CEBRA prefix/reload diffs=0.0; Track C three-target null rows=12; plot_count=7"
    }
  ],
  "validationOutput": [
    "selected_cell_count=195",
    "selected_scope_hash=2924d60f9a52ad7c02e802c28e84a85c6267da023267ac1b507b957e0587f60d",
    "protocol_hash=8122691b8c28fc67d3582580cfcb55557ed95bc3366506aa8ef54b054829cf76",
    "script_hash=76547bf65aa0a1245df1a66491050e5e21cc01df118105f18111b54608214ac8",
    "test_hash=13b7adbde5630e35743ffb7d182bf3a23b731fefbd328620fb2bf78c6ee6661d",
    "schema_manifest_hash=4d04038fc05b84091376b2b39989b72456a3398e2012d1dbb660ee65682871b3",
    "track_c_allowlist_manifest_hash=e58e8c2bf43d81456886a029dd0bfa607977f955f33a1e135ed486b792c44be8",
    "smoke_summary_hash=44c3897cdff663f3deb4a2036b208e055bce8a0e4822ae676bfb8d6c9c5d31f9"
  ],
  "residualRisks": [
    "Parent review gate still required before any biological fit, biological replay, mixed-importer export, or Track C per-unit development model execution",
    "Primary LSP diagnostics had zero findings but one file timed out/unconfirmed; ruff, py_compile, unit tests, and synthetic smokes passed",
    "Existing legacy V8b/V9 saved-manifest test assumes a relative old-output path absent in this worktree",
    "Future biological results remain exploratory development because original holdout exposure is permanent"
  ],
  "noStagedFiles": true,
  "diffSummary": "Added phase1 CLI/tests/protocol; implemented exact-Q Track A utilities, gated Track B CEBRA spec/execution scaffolding, guarded Track C export/per-unit modeling, three-target behavior allowlist/nulls, and final protocol-only replay clarification.",
  "manualNotes": "No commits, pushes, installs, lab-server access, subagents, original importer/split table reads, biological fits, or mixed-importer extraction were performed."
}
```
