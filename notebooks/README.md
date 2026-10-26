# Fresh-input neuroscience notebooks

These are the active **source-to-result** walkthroughs. Each notebook starts from its
own declared inputs, constructs source-safe pseudopopulations and computes fresh results.
Current source-notebook outputs are cleared, not reused from the earlier invented
software checks. The [October26 ledger](../docs/compact-cue-source-20261026.md) records
actual non-fitting validation; B/C were not executed for this change.

| Notebook | What it computes |
| --- | --- |
| [01 — Pseudopopulation](01_pseudopopulation.ipynb) | Target/split provenance, exclusions, masks/exposure, source support, intact block assembly, reconstruction and reuse; no fits |
| [02 — PCA/LDA](02_pca_lda.ipynb) | Train-only normalization/PCA, logistic heads and supervised SVD-LDA; full versus reduced source pools, refitting every learned stage |
| [03 — CEBRA](03_cebra.ipynb) | Fresh cue-only CEBRA-Time, raw/PCA references, source-level alignment-breaking diagnostic, matched readouts, losses/exposure and loaded-model replay |

The separate [historical endpoint notebook](../report/endpoint_walkthrough.ipynb)
replays accepted saved artifacts. It is preserved unchanged; it is not fresh source
reconstruction and is not required by these notebooks.

## Install and run the invented examples

Use a **new** Python environment, not this host's retained research runtimes. From a
checkout, install the distribution with the extras you need:

```sh
python -m pip install '.[notebooks,cebra]'
python scripts/execute_fresh_notebooks.py \
  --output /tmp/neuro-invented-new-run \
  --timeout-seconds 600 --memory-gib 4
```

The output directory must not exist. The Linux executor starts sequential fresh
kernels, clears saved outputs, checks actual kernel code identity, exports HTML and
replays newly fitted models with fitting/optimizer updates blocked. It does not serve
pages or resume failed runs. RSS/disk monitoring is sampled; use an external cgroup
for hard containment. On other platforms, open the notebooks in an appropriately
provisioned Jupyter frontend and restart/run all; that platform's executor is not certified.

For construction/baselines without CEBRA/torch:

```sh
python -m pip install '.[notebooks]'
python scripts/execute_fresh_notebooks.py \
  --notebooks 01_pseudopopulation 02_pca_lda \
  --output /tmp/neuro-baselines-new-run --timeout-seconds 600
```

The public default is nine units, three source blocks, four bins and six unequal
ordered pairs. CEBRA has only20updates. No private data, old results or download is
needed at execution time. Installation itself may download declared dependencies.
Linux/Python3.13 CPU execution was validated; other platforms/dependency resolutions
are not thereby certified.

## Supplied inputs and scientific boundaries

**Actual lab source is included in Git:** [compact unbinned cue-source v1](../data/README.md#compact-unbinned-cue-source--october26-2026)
contains all selected-unit spikes and event/timing records, not old binned tensors or
results. No Release, LFS or private raw download is needed. Dense gaze/behavior are
intentionally omitted; original native sources stay local. All three notebooks use
the shared compact inspection/load route without old private imports/results/splits.

To inspect real metadata only (no biological execution flag/kernel pin needed), load
`data/cue-source-v1/notebook-config.json`, set `manifest_directory` to its parent,
and call `inspect_inputs`. The data guide contains a runnable checkout example.
For actual neural reconstruction, copy that configuration to your own output area,
set `data_root` explicitly to the compact directory and `biological_execution=true`,
record a reviewed `expected_kernel_identity` from the intended runtime using
`stable_kernel_identity(runtime_identity())`, then pass its SHA256 and
`--allow-biological` to the executor. Select **only** `--notebooks 01_pseudopopulation`
for this non-fitting walkthrough. Set `NEURO_NOTEBOOK_CONFIG` when using a Jupyter
frontend; biological loads additionally require `NEURO_ALLOW_BIOLOGICAL=1`.
No B/C model run is authorized by this source-data update. Default execution remains
invented; wrong/missing supplied files fail, never fall back.

`neuro.source_data.SourceData` is the explicit binned-input contract: source/unit/target
ledgers, observation mask, exposure, timing, units, provenance and declared split policy.
`neuro.pseudopopulation`, `neuro.pca_lda` and `neuro.cebra` can be used independently.
Supported manifest adapters are the compact unbinned source view and the preserved
six-file place195 route. Arbitrary formats require explicit semantics, not guessed
labels/timing. Missing supplied inputs never fall back to a demo.

The authorized local real-data protocol uses a **new27-unit/10-session panel**, with
1,415training/551exposed-development sources after direct-contributor embargo. It is
not a matched replication of the historical195-unit panel. Full/reduced training pools
share identical development assemblies and refit every learned stage. Pair-conditioned
assembly is a conditional assay, not natural unknown-label trial prediction.

Real execution requires a reviewed manifest, exact kernel identity, explicit biological
flag, code/data review and resource benchmark. See the [frozen protocol](../docs/shareable-notebooks-protocol-20261023.md)
and [execution/results ledger](../docs/shareable-notebooks-execution-20261023.md), which
own actual run status. Private manifests, source IDs, predictions and fitted artifacts
are never included in these shareable source notebooks. No further biological run is implied.

## Rebuild, verify and share

Notebook cell source is maintained in `scripts/build_fresh_notebooks.py`; rebuilding
produces empty outputs. Structural checks accept empty notebooks; optional saved
execution evidence must match cell hashes/order. Whole-NotebookA uses the existing
`no_fitting` guard before source work, not only late zero fit counters. Do not replace
source notebooks with private ID-bearing outputs.
Focused checks are `scripts/test_public_workflow.py` and `scripts/test_fresh_notebooks.py`;
inspect their requirements before running. Do not use broad research-test discovery as
a substitute: some historical tests access private artifacts.

Artifact replay uses trusted joblib states only after authenticating a separately
retained manifest hash. Never load an untrusted pickle/joblib directory. The initial
implementation/draft PR did not grant a code license or publish lab inputs. The separate
October26 owner authorization covers only the compact source view and cleaned
assignments described above; it grants no new license, model/result publication,
merge or package-registry release. Original private inputs, execution manifests, predictions and fitted results
remain local.
