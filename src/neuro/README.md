# Scientific package: `neuro`

The maintained full-trial, endpoint and cue-time readout family now lives here.
These are **explicit exploratory workflows**, not a universal experiment runner.
Packaging does not authorize execution or turn their results into confirmatory evidence.

## Architecture and scientific boundaries

```text
neuro/
  place195_split_access.py     shared source-split gate and access audit
  execution.py                file hashing, equivalent fresh-directory/deadline rules,
                              bounded-path source snapshot copying
  provenance.py               audited current-source closure for this study family
  legacy_adapters.py          explicit boundary to retained helpers under scripts/
  studies/
    full_trial_transfer.py    binary path-component whole-cue / joint-phase workflow
    endpoint_time_readout.py  pair30/start6/goal6 readouts with streaming seed outputs
    cue_time_readout.py       frozen full-trial encoders and single-bin readouts
```

The existing scientific bodies were relocated, not copied into notebooks or weekly
folders. Scientific definitions retain their pre-migration AST; changes concern
imports, source paths, equivalent bookkeeping and current provenance. Full-trial's
accumulated metrics/predictions and endpoint's seed-streamed confusion output remain
separate. The cue-time workflow does not train encoders, but its readout fitting and
saved-model/data access still require the original approval process.

**Shared scientific objects:** endpoint already reuses full-trial's
`CebraVectorDataset`, temporal loader/training implementation and embedding helper;
cue-time already reuses full-trial's cohorts, binary bundles, decoder states and
comparators. These now refer directly to the same packaged objects. Both full-trial
and endpoint use `SplitFilteredAccess`. No algorithms were merged merely because
classes look alike: full-trial `RowBundle.y` is a binary component label, endpoint
`RowBundle.y_pair` is a 30-class endpoint-pair label; their pair-lineage formats are
also different. They remain distinct classes.

**Shared execution seams:** streaming SHA-256 for identical file bytes; the identical
endpoint/cue-time `ensure_fresh_dir`; the already-common full-trial/endpoint monotonic
deadline; and source-snapshot copying with nested manifest paths. Full-trial's different
fresh-directory exception/message remains local. Timestamp formats, JSON normalization,
CSV formats, manifests and replay guards differ and stay study-specific. Cue-time's
wall-clock deadline was not replaced with a monotonic one. No base class, plugin,
shared result schema or speculative execution context was added.

## Imports and retained commands

From the checkout, no installation is needed:

```sh
PYTHONPATH=src scratch/v6-v9-runtime/bin/python -B -c \
  'from neuro.studies import full_trial_transfer, endpoint_time_readout, cue_time_readout'
PYTHONPATH=src scratch/v6-v9-runtime/bin/python -B -m neuro.studies.endpoint_time_readout --help
```

For library use:

```python
from neuro.place195_split_access import SplitFilteredAccess
from neuro.studies import full_trial_transfer as ft
from neuro.studies import endpoint_time_readout as endpoint
from neuro.studies import cue_time_readout as cue_time
```

Importing `neuro`, `neuro.studies`, `execution` or `provenance` is stdlib-only.
Importing an individual study needs the existing scientific runtime (including
CEBRA, torch and sklearn), but opens no lab inputs and performs no fits. A supplied
path is opened only when the relevant loader/workflow is called. For another working
directory, set `PYTHONPATH` to the checkout's absolute `src` path. This is a
checkout-backed package, **not a certified standalone wheel**; the legacy adapter
adds the owning checkout to the import path. `pyproject.toml` records the source path
for Pyright; it does not install or change the historical runtime.

All three old entry points remain thin aliases:

```sh
scratch/v6-v9-runtime/bin/python -B -m scripts.cebra_full_trial_transfer --help
scratch/v6-v9-runtime/bin/python -B scripts/cebra_full_trial_transfer.py --help
# The endpoint_time_readout and cue_time_readout names support both forms too.
```

Old `scripts.cebra_*`, bare `cebra_*` and new `neuro.studies.*` imports resolve to
one module, including private attributes and monkeypatch state. Historical pickle
class lookup paths under `scripts.cebra_*` remain resolvable; newly serialized
classes identify the package. Arbitrary historical `__main__` pickle paths and
private checkpoint replay are not certified by that import compatibility.

## Audited legacy boundary and deprecation

`legacy_adapters.py` imports the original helpers; it does not duplicate them:

| Retained source | Used interface / why it stays outside for now |
| --- | --- |
| `scripts/import_place195_sessions.py` | Ripple/spike readers, marker lookup, window selection and accepted CSV precision; still used by importer and older studies |
| `scripts/place195_v7_v8_neural_experiments.py` | `bin_events`, `session_from_cell`; still owns older cohorts/assemblies and imports the shared split gate |
| `scripts/place195_v8b_v9_cebra.py` | `make_solver`; imports V7/V8 objects and remains an executed V8/V9 study |
| `scripts/cebra_latent_atlas.py` | cue-time-only `fidelity`, `spectrum`, including their original supporting functions; still used by atlas/geometry reports |

This explicit `src → scripts` adapter is a **remaining migration boundary**, not the
target architecture. Extracting all those older families now would broaden this
three-study change and alter more historical provenance collectors. Before another
extraction, inspect all callers and migrate their source hashes/snapshot writers
without blessing old approvals. The current manifests include these actual transitive
sources, their initializers, the adapter and the packaged study implementations.

Deprecation is phased: (1) use the package for this family; keep old aliases for tests,
report builders/verifiers and saved-class lookup; (2) migrate genuinely shared legacy
helpers only with their consumers/provenance; (3) consider removal only after dependency
proof and historical recovery coverage. Older exploratory branches remain outside the
package. `start_goal_ce_followup.py` is deprecated for new Time-focused work, not deleted;
pilot smoke CLIs are archival while pilot contract/split helpers still serve later code.
[Scripts inventory](../../scripts/README.md) names those retained dependencies. No old
experiment was established as safely removable in this consolidation.

## Current provenance is not historical approval

`study_sources` binds current implementation files and the audited local import closure.
`helper_paths`/`helper_hashes` now include package code, bootstraps and actual transitive
legacy helpers, not just the wrappers. Current helper manifests use repository-relative
paths throughout, so a snapshot's `scripts/` and `src/neuro/` files agree with imports;
historical flat-key manifest schemas remain untouched. Writers create the nested directories.
The old flat `code_snapshot_cebra_*.py` names now contain the actual implementation;
the full closure lives alongside them. Snapshots record source, not a portable runtime
or a newly approved standalone launcher.

Canonical private input/output defaults remain unchanged. Current protocols and
implementation hashes resolve from this checkout, not from an assumed old `__file__`
location. Current approvals/benchmarks intentionally become stale after relocation;
endpoint's exact-source replay gate is unchanged. No historical ledger/hash/approval
or frozen source snapshot was rewritten. The cue-time facts explicitly label its old
typing-only review as historical, not approval of the package.

Pre-migration source is recoverable at Git **`cc0527e`** (not necessarily the exact
executed historical runner):

| Original script | SHA-256 at that checkpoint |
| --- | --- |
| `cebra_full_trial_transfer.py` | `bea7561b922f1c3a36dfe563ba1c1d08b85749d4a3221243bf1adc35d425b7d1` |
| `cebra_endpoint_time_readout.py` | `0967a9a69c56e7d0b59aa20600817d48c34deeb7fd9aceabec11b3706a4f84a5` |
| `cebra_cue_time_readout.py` | `746a570a5bda809bdd3659e02e12ba5cad226444f6f889e9a93abd1296f47b55` |

The split implementation remains byte-identical to its original SHA-256
`2cd7e7a14f6a045078c59d2489e6d06a615f033dc0f6c0cbea14533561608c0d`.
For exact historical reproduction, use the owning study's retained executed snapshot,
approval, runtime and separately authorized private artifacts—not changed current
sources with substituted hashes. This consolidation does not certify private replay.

## Safe validation and notebook decision

```sh
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -m unittest scripts.test_place195_split_filtered_access -v
PYTHONDONTWRITEBYTECODE=1 PYTHONNOUSERSITE=1 scratch/v6-v9-runtime/bin/python -B \
  -m unittest scripts.test_neuro_study_package -v
```

The focused package suite checks source AST against the pinned checkpoint, equivalent
bookkeeping, nested snapshots, cold import/module/legacy-pickle identity, source closure
and nine CLI-help invocations. It uses source and temporary invented files only; cold
imports actively reject lab `data/`/`outputs/` access. The AST regression needs the
checkpoint's Git object. Existing fitting smoke checks are **not** authorized by this
command; do not run the broad `check_research_software.py` (it includes private embedding
QA). Selected existing non-fitting checks can be used after source review; many similarly
named tests fit encoders, PCA/scalers or readouts even on invented arrays.

Whether/how the intended companion notebook uses this package remains **open**,
depending on the notebook's needs and complexity. A tracked-aggregate presentation
notebook need not import these scientific runners. If it needs existing algorithms,
prefer shared imports over copied implementations. Its target/cohort/input contract
and restart-and-run-all validation remain separate work. No notebook, fits, private
replay, installations or services are implied.
