# Fresh-input neuroscience notebooks

These are the active **source-to-result** walkthroughs. Each notebook starts from its
own declared inputs, constructs source-safe pseudopopulations and computes fresh results.
The saved source-notebook outputs are **invented-data software smoke tests**, not biological evidence.

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

`neuro.source_data.SourceData` is the explicit binned-input contract: source/unit/target
ledgers, observation mask, exposure, timing, units, provenance and declared split policy.
`neuro.pseudopopulation`, `neuro.pca_lda` and `neuro.cebra` can be used independently.
The current notebook manifest adapter is specifically the authenticated six-file
place195 input route; arbitrary file formats require an explicit adapter, not a guessed
label/timing interpretation. Missing supplied inputs never fall back to a demo.

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
produces empty outputs. The current saved outputs were executed from the same cell text
and record their software-smoke provenance. Do not replace them with private outputs.
Focused checks are `scripts/test_public_workflow.py` and `scripts/test_fresh_notebooks.py`;
inspect their requirements before running. Do not use broad research-test discovery as
a substitute: some historical tests access private artifacts.

Artifact replay uses trusted joblib states only after authenticating a separately
retained manifest hash. Never load an untrusted pickle/joblib directory. No code license
or lab-data redistribution permission has been granted by this implementation. The
owner-requested draft PR includes code, invented outputs and reviewed documentation/
aggregate notes only; private inputs/results and package-registry publication remain
outside its scope.
