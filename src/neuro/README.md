# `neuro`: experiment workflows and reusable helpers

`neuro` is the checkout-backed Python implementation of the **latest maintained
full-trial, endpoint-time and cue-time experiment family**. It contains whole concrete
exploratory workflows **and** the reusable scientific/safety helpers they need.
It is **not** a pure helper library, a universal experiment runner or a stable,
versioned public API. Packaging does not authorize execution or strengthen a claim.

**Start with:** [safe checkout usage](#use-from-a-checkout) →
[module reference](#module-reference) → [workflow contracts](#whole-experiment-workflows) →
[actual coupling](#workflow-versus-helper-boundary).
The [software design](../../docs/software-design.md) is the maintained as-built
engineering reference, with lifecycle/UML/dependency diagrams; this page is the usage guide.
[Current report](../../report/README.md) and [evidence catalog](../../docs/reports/README.md)
own scientific interpretation, not package imports.

## Use from a checkout

### A data-free helper example

From the repository root, with Python's standard library only:

```sh
PYTHONPATH="$PWD/src" PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -B - <<'PY'
from pathlib import Path
from neuro.execution import sha256_file

digest = sha256_file(Path("README.md"))
assert len(digest) == 64
print(digest)
PY
```

This reads a documentation file, not lab inputs or model artifacts; it does not fit
anything. Import helpers from their owning module rather than importing a whole study
for hashing or other bookkeeping. `neuro`, `neuro.studies`, `execution` and `provenance`
are stdlib-only imports. Other modules have different requirements:

| Import | Existing dependencies | Side-effect boundary |
| --- | --- | --- |
| `neuro.execution` / `neuro.provenance` | Python stdlib | Hashing/snapshot functions read or write only when called; provenance checks current source paths |
| `neuro.place195_split_access` | Python stdlib | Source tables/rows are read when access methods are called |
| `neuro.neural_inputs` | NumPy | Count/exposure and session-identity helpers operate on supplied values |
| `neuro.raw_io` | NumPy, SciPy, h5py | Readers open supplied Ripple/spike paths only when called |
| `neuro.geometry` | NumPy, SciPy | Descriptive diagnostics operate on supplied arrays, not biological inference |
| `neuro.cebra_solver` | CEBRA, torch | `make_solver` constructs model/criterion/optimizer when called; it is not a data-free example |
| `neuro.studies.<module>` | Existing scientific runtime, including CEBRA/torch/NumPy/sklearn; endpoint also joblib | Imports do not open lab inputs or fit; invoking a workflow can do both |

### Inspect workflow commands

Use an **already provisioned** environment. On this host the retained runtime is
`scratch/v6-v9-runtime/bin/python`; no installation is part of these instructions.
From the checkout root:

```sh
PY=scratch/v6-v9-runtime/bin/python
export PYTHONPATH="$PWD/src" PYTHONDONTWRITEBYTECODE=1 PYTHONNOUSERSITE=1
"$PY" -B -m neuro.studies.full_trial_transfer --help
"$PY" -B -m neuro.studies.endpoint_time_readout --help
"$PY" -B -m neuro.studies.cue_time_readout --help
```

Only `--help` is demonstrated. Full-trial parser defaults may probe CUDA availability;
help/clean imports do not certify GPU execution. From another directory, set
`PYTHONPATH` to the **absolute checkout `src` path** and use an absolute interpreter
path. Python's `-B`/`PYTHONDONTWRITEBYTECODE` avoid writing bytecode into the checkout.

**This is not an installation or standalone-wheel guarantee.** Package modules do not
import `scripts` or mutate `sys.path`; external CLI aliases alone bootstrap checkout
paths. `pyproject.toml` gives Pyright a source path and describes the general environment;
it is not an installer for this source package or a complete historical replay recipe.
The general `uv.lock` and retained replay runtime are not interchangeable certifications.
Private defaults still name host-local dated study roots; cloning does not provide inputs.

**Execution authority is separate.** These commands do not authorize raw-data access,
fits, checkpoint loading, private replay or downloads. A command called `audit`, `verify`,
`geometry` or `report` can still open protected inputs and write artifacts. Even invented-
data `synthetic-smoke` fits models. Review source and owning protocol before any execution
beyond help or a data-free helper example.

### Retained external entry points

Existing callers can still use thin aliases, for example:

```sh
scratch/v6-v9-runtime/bin/python -B -m scripts.cebra_endpoint_time_readout --help
scratch/v6-v9-runtime/bin/python -B scripts/cebra_endpoint_time_readout.py --help
```

Full-trial and cue-time retain the analogous module/direct-file forms. New checkout
usage should prefer `neuro.studies.*`. Old `scripts.cebra_*`, bare `cebra_*` and package
imports resolve to one module, including private attributes and monkeypatch state.
Historical `scripts.cebra_*` pickle class lookups remain resolvable; new classes identify
the package. This does **not** certify arbitrary historical `__main__` pickle paths,
private checkpoint replay or portable standalone snapshots.

## Module reference

Paths below are relative to this directory. “Reusable” means actually shared by the
maintained workflows, not a promise to support every caller or future notebook.

| Module / source | Role | Useful entry points / objects |
| --- | --- | --- |
| [`studies/full_trial_transfer.py`](studies/full_trial_transfer.py) | **Whole experiment**, also current owner of shared cohort/training/readout machinery | `main`, `parse_args`; `CueCohort`, `RowBundle`, `CebraVectorDataset`, `train_encoder`, `embed_cue` and decoder-state helpers |
| [`studies/endpoint_time_readout.py`](studies/endpoint_time_readout.py) | **Whole experiment** with its own endpoint cohort, lineage and streamed outputs | `main`, `parse_args`, `run_full_budget`, `replay_run`; `EndpointCohort`, endpoint `RowBundle`, `FeatureBundle` |
| [`studies/cue_time_readout.py`](studies/cue_time_readout.py) | **Whole frozen-model readout workflow**, not a generic temporal-analysis utility | `main`, `parse_args`, `load_seed_features`, `extract_window_features`, `replay_run`; `SeedFeatures` |
| [`place195_split_access.py`](place195_split_access.py) | Shared source-split access/validation gate | `SplitFilteredAccess`, `SplitAccessError`, `SplitFilteredAudit.as_dict` |
| [`raw_io.py`](raw_io.py) | Ripple/spike input primitives and accepted CSV precision | `EventTrials`, `SpikeTrain`, `read_ripple_trials`, `read_spiketrain`, `spikes_in_window`; conversion/HDF5/MATLAB support |
| [`neural_inputs.py`](neural_inputs.py) | Count/exposure/omission rules and cell-to-session identity | `bin_events`, `session_from_cell` |
| [`cebra_solver.py`](cebra_solver.py) | Fixed offset1 model, cosine criterion and Adam optimizer construction | `make_solver` |
| [`geometry.py`](geometry.py) | Cue-time descriptive spectrum/projection fidelity | `spectrum`, `fidelity`, `rank_correlation`, `require` |
| [`execution.py`](execution.py) | Equivalent filesystem/budget bookkeeping | `sha256_file`, `ensure_fresh_dir`, `check_deadline`, `snapshot_sources` |
| [`provenance.py`](provenance.py) | Audited current implementation/local import closure | `REPOSITORY_ROOT`, `study_sources` |

No catch-all `utils.py`, base runner, plugin system, common result schema or shared
execution context is implied. Helper signatures and private state formats retain their
concrete scientific contracts; see source before adapting them to another cohort.

## Whole experiment workflows

Each study owns its CLI, scientific definition, approval gates and artifact lifecycle.
They are **exploratory**, not automatically confirmatory. The command lists are a
navigation reference—not suggested commands to run now.

| Workflow | Scientific contract | CLI surface and owning evidence |
| --- | --- | --- |
| Full-trial transfer | Binary interior path component at fixed 4→3; 29 selected units/seven session blocks, 82 train/22 historically exposed validation sources. Compare cue-only/broader × Time/Behavior encoders with raw/PCA references; cue-only readout inputs. Source-coherent nulls and source sensitivity are part of the workflow. | `audit`, `run`, `verify`, `synthetic-smoke`; [protocol](../../docs/reports/cebra-full-trial-transfer/protocol.md), [accepted results](../../docs/reports/cebra-full-trial-transfer/README.md) |
| Endpoint-time readout | Separate pair30/start6/goal6 heads; 195 units/58 sessions, 12,288 inner-train/3,265 exposed-development sources, all within original outer train. Cue-only vs joint CEBRA-Time, raw/PCA/logistic and SVD-LDA; whole cue/ten single bins, null families and source deletion. | `prepare-nav`, `run`, `verify`, `approval-facts`; [protocol](../../docs/reports/cebra-endpoint-time-readout-20261006/protocol.md), [accepted results](../../docs/reports/cebra-endpoint-time-readout-20261006/README.md) |
| Cue-time readout | Reuse accepted full-trial cohort/lineage, scalers, PCA, frozen encoder checkpoints and whole-cue decoder states. Fit new single-bin logistic/SVM readouts; replay saved whole-cue states; descriptive checkpoint geometry. **No encoder/PCA refits**, but readout fitting and saved-data/model access still require approval. | `audit`, `geometry`, `counts`, `run`, `verify`, `report`; [protocol](../../docs/reports/cebra-cue-time-readout-20261005/protocol.md), [accepted results](../../docs/reports/cebra-cue-time-readout-20261005/README.md) |

Source trials/sessions, not bins or synthetic combinations, define biological support.
Known labels condition assembly. Source-safe splits do not make a cross-session
pseudopopulation simultaneous, repair historical evaluation exposure, or enable exact
unknown-trial path/state/dynamics claims. Separate window readouts are not frozen
readout temporal generalization. Endpoint classification is not the binary component
assay, and neither is full ordered-route prediction. See the
[analysis contract](../../docs/analysis-contract.md).

## Workflow versus helper boundary

**Current separation is incomplete, deliberately documented rather than disguised.**
The studies contain orchestration **and** substantial algorithms/data classes. In
particular, `full_trial_transfer` serves both as one experiment and as shared machinery:

- Endpoint imports its `CebraVectorDataset`, training, embedding and solver objects.
- Cue-time imports it as `ft`, reusing cohorts, binary assembly, decoder states,
  comparators and other full-trial-specific definitions.
- Both full-trial and endpoint use `SplitFilteredAccess`; all three share execution/
  provenance seams and the required purpose-specific helper dependencies.

Thus importing an endpoint or cue-time study also brings in the full-trial scientific
runtime. They are not three isolated reusable APIs. Moving more common algorithms
out of the full-trial workflow would be **future architecture work**, not implemented
or required by this documentation change.

Do not merge objects by shape alone: full-trial `RowBundle.y` is a binary component
label, endpoint `RowBundle.y_pair` is a 30-class endpoint-pair label, and their pair-
lineage formats differ. Full-trial accumulates metrics/predictions; endpoint streams
seed outputs and confusion rows. Timestamp/JSON/CSV formats, replay guards and
manifests remain study-specific. Full-trial's fresh-directory error stays local;
endpoint/cue share an equivalent helper. Cue's wall-clock deadline was not changed
to the full-trial/endpoint monotonic deadline. These differences matter when reusing code.

## Active helper ownership and historical boundary

Retain code when the supported workflows need it end to end, **including validation,
scientific controls, provenance and verification**. Old callers, old result formats
or a hypothetical future notebook alone do not justify package features.

**October15 cleanup (independently reviewed):** `legacy_adapters` was
removed; the four active helper modules above contain 21 required definitions
extracted with exact AST preservation against pinned Git `ce31248729a9b54aaf3fea8c014fe16c0e0105b4`.
Origins: `raw_io` from `scripts/import_place195_sessions.py`, `neural_inputs` from
`scripts/place195_v7_v8_neural_experiments.py`, `cebra_solver` from
`scripts/place195_v8b_v9_cebra.py`, and `geometry` from `scripts/cebra_latent_atlas.py`.
The three study scientific bodies retain their earlier pinned AST checks.

Older implementations remain unchanged **outside package support** as historical
records—not a second current implementation to extend. Earlier endpoint, V6–V9,
path/preprocessing and decoder/atlas experiments are not supported package APIs or a
run queue. Only the three justified current external launch aliases and their initializer
remain in the current source closure; package-only imports do not depend on them.
[History](../../history/README.md) and [migration ledger](../../docs/reorganization.md)
preserve the chronology instead of turning it into compatibility requirements.

## Current provenance is not historical approval

`study_sources` binds the current implementation and audited local source closure.
Helper manifests use repository-relative keys, including nested `src/neuro/` and
`scripts/` snapshot paths. Historical flat-key schemas remain untouched. The full
closure sits beside the flat `code_snapshot_cebra_*.py` implementation snapshots;
source snapshots are not portable runtimes or newly approved standalone launchers.

Relocation/helper cleanup makes old current-source approvals and benchmarks stale.
Endpoint's exact-source replay gate is retained. No historical ledger, approval,
hash or frozen executed snapshot was rewritten; cue-time's old typing-only review
is explicitly historical, not approval of today's package.

Pre-migration source is recoverable at `cc0527e`, but that checkpoint is not necessarily
the exact executed runner. For separately authorized historical reproduction, use the
owning study's **retained executed snapshot, approval, runtime and private inputs**,
not current code with substituted hashes. Package checkpoint `8c98b52` and engineering
documentation at `ce31248` are published in
[PR20](https://github.com/Hong-yiii/neuro_science/pull/20), extended by the reviewed
helper cleanup and documentation refresh. The owner authorized publication and merge;
consult the PR for its authoritative status. This does not certify private replay.

## Safe validation and notebook decision

The existing focused checks use source and invented temporary inputs, not biological
fits; inspect their source before execution:

```sh
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -m unittest scripts.test_place195_split_filtered_access -v
PYTHONDONTWRITEBYTECODE=1 PYTHONNOUSERSITE=1 scratch/v6-v9-runtime/bin/python -B \
  -m unittest scripts.test_neuro_study_package -v
```

The package suite covers pinned scientific/helper ASTs, import/path boundaries,
equivalent bookkeeping, nested snapshots, cold module/legacy-pickle identity, current
source closure and nine CLI-help invocations. Cold import checks reject lab `data/`/
`outputs/` access and scaler/PCA/readout fitting/optimizer steps. AST regressions need
the pinned Git objects; scientific imports need the existing runtime. A passing software
check is not GPU/run/replay verification or biological evidence.

**Do not infer safety from a test name.** Many existing tests fit encoders, transforms
or readouts on invented arrays; the broad `scripts/check_research_software.py` includes
private embedding QA and is not a data-free runner.

There is **no companion notebook yet**. Its target/cohort and input contract, and
whether/how it uses this package, remain open. A tracked-aggregate presentation
notebook need not import study runners; if it actually needs existing algorithms,
prefer imports over copying them. No notebook, dependency install, fits, private replay
or service is part of this package reference. Use
[workspace/recovery](../../docs/workspace.md) for operational ownership and protected files.
