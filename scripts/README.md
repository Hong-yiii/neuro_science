# Scripts and tests: report-backed work versus historical trials

Updated 2026-10-12. Current focus is the
[retrospective and its evidence](../docs/reports/README.md), not restarting runs.
This map classifies existing entry points; it is not execution authorization.

**Three-study package implemented:** full-trial transfer, endpoint-time and cue-time
scientific bodies now live in [`neuro.studies`](../src/neuro/README.md), beside the
shared split gate and equivalent execution/provenance seams. Their `cebra_*.py`
files here are thin CLI/import aliases preserving module identity and old class
lookup paths. Other scientific families remain legacy code outside the package;
the audited `neuro.legacy_adapters` boundary reuses their original helpers.
Historical executed-source identities/approvals remain separate from changed
current source. See [migration status](../docs/reorganization.md).

## 1. Current manuscript publishing — no scientific execution

The tools live beside the manuscript, not in this directory:

```sh
/usr/bin/python3 report/test_build.py
/usr/bin/python3 report/test_path_summary.py
/usr/bin/python3 report/test_layout.py
/usr/bin/python3 report/build.py
```

They check presentation/archived aggregate arithmetic and package existing PNGs
plus inline SVGs. They do not access raw data, fit or replay scientific models.
The default now builds `manuscript.html`; revision02 requires explicit `outline.html`.
The frozen checksum check still flags the preserved pre-existing local mismatch.
See [publishing and frozen-copy policy](../report/README.md).

## 2. Retained scientific families behind the report

Keep each family's tests, original configurations, builders and verifiers with
its provenance. Read the owning protocol before running anything.

| Family | Representative existing scripts | Owning evidence |
| --- | --- | --- |
| Latest endpoint readouts | `cebra_endpoint_time_readout.py`, `render_cebra_endpoint_report.py`, `verify_cebra_endpoint_run.py` | [Endpoint study](../docs/reports/cebra-endpoint-time-readout-20261006/README.md) |
| Path whole-cue/joint and time-resolved readouts | `cebra_full_trial_transfer.py`, `cebra_cue_time_readout.py`, their builders/renderers | [Joint study](../docs/reports/cebra-full-trial-transfer/README.md), [cue-time study](../docs/reports/cebra-cue-time-readout-20261005/README.md) |
| Earlier endpoint development | `start_goal_cebra_baseline.py`, `start_goal_autoresearch.py`, `verify_endpoint_saved_artifacts.py` | [Endpoint baseline](../docs/reports/start-goal-cebra-baseline.md), [follow-up](../docs/reports/start-goal-autoresearch.md) |
| Source support and V6–V9 | `place195_v6_graph_support_audit.py`, `place195_v7_v8_neural_experiments.py`, `place195_v8b_v9_cebra.py` | [V6–V9](../docs/reports/place195-v6-v9-autoresearch-20260906.md) |
| Source-transfer diagnostics | `place195_path_generalization_phase1.py`, `replay_path_generalization_assemblies.py`, path package/result verifiers | [Completed path study](../docs/reports/path-generalization-completed-state-20260907.md) |
| Preprocessing and matched PCA | `place195_path_preprocessing_autoresearch.py`, `place195_matched_pca.py`, matched builders/verifiers | [Preprocessing](../docs/reports/path-preprocessing-autoresearch-20260908.md), [PCA](../docs/reports/path-pca-matched/README.md) |
| Frozen readout and geometry diagnostics | `cebra_decoder_autoresearch.py`, `cebra_hyperparameter_diagnosis.py`, `cebra_latent_atlas.py` | [Decoders](../docs/reports/cebra-decoder-autoresearch-20260924.md), [diagnosis](../docs/reports/cebra-hyperparameter-diagnosis-20260924.md), [atlas](../docs/reports/cebra-latent-atlas-results-20260924.md) |

The three aliases support both `python -m scripts.cebra_<name> --help` and direct
`python scripts/cebra_<name>.py --help`; package imports use
`from neuro.studies import full_trial_transfer, endpoint_time_readout, cue_time_readout`
with `PYTHONPATH=src`. No installation is needed. Package code manifests include the
actual implementations and transitive helpers, not only these aliases. Current
approvals intentionally become stale; do not rewrite old hashes to accept this checkout.

A historical report builder can read private results or saved models. It is not
interchangeable with the manuscript's presentation-only builder. Scientific
verification/replay can access private predictions even without fitting; obtain
separate approval for that work. No new fit is queued.

## 3. Shared dependencies, not disposable initial-trial code

- `import_place195_sessions.py`, V7/V8 helpers and V8b/V9 solver helpers are
  imported across retained studies. `place195_split_filtered_access.py` now only
  aliases `src/neuro/place195_split_access.py`, the shared scientific implementation.
- `place195_graph_path_baseline.py` and `place195_split_and_behavior_audit.py`
  carry graph/source-split infrastructure despite their early names.
- `docs/cebra_pilot/implementation/{contracts,paths,splits}.py` are imported by
  later code. Its package initializer also imports `neural.py`; preserve it.
- `data.py` and `inspect_spatial_bin_jld2.py` remain local data utilities, not
  authorized data-access commands merely because they are listed here.
- The packaged family's source paths/manifests now resolve its actual implementation.
  Other legacy families still have original-path/bare-import assumptions; another
  relocation needs a caller/provenance audit, not only a successful import.

## 4. Historical smoke or excluded modeling branches

File these in the [historical reading lane](../docs/reports/archive/early-work-20261012/README.md),
not the main workflow, while retaining their executable paths:

- Pilot `preflight.py` and `manifest.py`: initial synthetic/one-cell smoke CLI
  and output writer. Pilot tests and documented module commands still refer to them.
- `start_goal_ce_followup.py`: **deprecated for new Time-focused work**, the older
  cross-entropy encoder branch excluded from the current manuscript. Its path remains
  available for historical provenance/tests; deprecation is not deletion.
- Early data feasibility, V4/V5 notes and initial-trial outputs: historical
  software/selection evidence, not current neural prediction results.

Deprecation proceeds in phases: package this supported family (done), migrate shared
legacy helpers with all consumers/provenance (not done), then remove an old entry
point only after dependency proof and historical recovery coverage. Earlier endpoint,
V6–V9, path/preprocessing and decoder/atlas experiments are historical retained families,
not a run queue or disposable code. No scientific test/private output was removed;
no whole older helper/test was established as safely obsolete.

## 5. Tests are not all clone-only or private-input-free

`check_research_software.py` discovers every `scripts/test_*.py`, imports modules,
then excludes two **method names** (`test_actual_input_gate` and
`test_saved_manifest_has_seven_session_components_per_pseudorow`). Moving a test
out of that directory would silently reduce coverage. Some artifact verifiers
also load tests explicitly.

**Existing issue found during cleanup:**
`test_cebra_cue_time_report.py::CueTimeReportTest.test_final_geometry_against_saved_embeddings_without_producer_helpers`
reads ignored `cue_embeddings.npz` files. It is not one of those exclusions.
Thus the broad runner's “without private lab inputs” description is not a safe
execution guarantee. This was found by reading source; the test was not run.
Classifying/gating private-input tests is a separate follow-up, not solved by
archiving their coverage. Import-time side effects must also be checked.

For the new package use the focused, non-fitting `scripts.test_neuro_study_package`
suite in the existing runtime and the stdlib split suite; commands/coverage are in
[the package README](../src/neuro/README.md#safe-validation-and-notebook-decision).
The migration AST check requires the pinned `cc0527e` Git object. Do not run whole
study-test modules as a substitute: several fit even on invented arrays. Notebook
integration remains the user's open decision; this package adds no notebook.

The pilot `tests/test_framework.py` mixes historical smoke checks with shared
contract/path/split checks. Keep the whole module until a reviewed split retains
both discoverability and compatibility. Manuscript tests above are separate from
this discovery scheme.

## Environments and preservation

General `pyproject.toml`/`uv.lock`, `requirements-replay.txt` and retained
`scratch/v6-v9-runtime/` serve different roles. Do not unify, upgrade or delete
them as filing cleanup. Use original study runtime/protocol records for any
separately approved reproduction; frozen executed snapshots remain authoritative.
