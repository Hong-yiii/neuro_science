# A research guide, from recordings to defensible claims

This seven-chapter course is intended for a graduate student taking over the study.
Start with [00 — Research guide](00_research_guide.ipynb), then follow the table in
order. The foundations explain the task and measurements; a small executed example
traces the arithmetic; the practical chapters expose the implemented computation;
the retrospective explains what each experiment changed in our understanding.
Fourteen historical figures and the invented example's outputs are embedded for
reading without private files or model execution.

The practical chapters follow **question → design decision → calculation →
diagnostic → interpretation**. Each independently reconstructs its declared inputs.
B/C walk the first planned case through assembly, normalization, representation,
transformation, decoder fitting and scoring in separate cells, then finish the
remaining grid. Equations and arithmetic checks expose what the package computes.
[Scope and verification](../docs/notebook-course-20261027.md).

| Notebook | What you should understand afterward |
| --- | --- |
| [00 — Research guide](00_research_guide.ipynb) | Reading chapter: research history, cohort distinctions, accepted decoder and joint-training evidence, controls and claim limits; no execution |
| [00a — Experiment foundations](00a_experiment_foundations.ipynb) | Maze/cue task, spike sorting and count measurements, clocks and markers, units versus sessions, missingness, pseudopopulation assumptions, label conditioning and what remains undocumented |
| [00b — Worked numerical example](00b_worked_example.ipynb) | One invented dataset from timestamps through counts/masks, split, block recipes, scaling, given projection/logits, probabilities, confusion metrics and one contrastive term; saved outputs, no fitted model |
| [01 — Can we form this pseudopopulation?](01_pseudopopulation.ipynb) | Label/predecessor derivation, source support and exclusions, class/pool/session skew, count/exposure semantics, worked block lineage, balanced assembly versus real-source reuse; no fits |
| [02 — What can simple models recover?](02_pca_lda.ipynb) | Staged scaler/PCA/readout implementation, supervised LDA, logits and metrics, rationale for settings, seed/budget comparisons, confusions, gaps and explicit 3D PCA views |
| [03 — Is CEBRA learning something useful?](03_cebra.ipynb) | Actual network layers and temporal sampler, staged fit/transform/readout, contrastive terms, sampling coverage, spread/collapse checks, observed/full/seed0 3D views and controls |
| [04 — How the studies changed our understanding](04_study_evidence.ipynb) | Graph/path targets, source transfer versus recombination, preprocessing/sampling/readout ablations, actual historical loss and 3D figures, joint navigation construction and weighting, negative results and unresolved tests |

“Joint pair prediction” and “joint cue/navigation encoder training” are different
questions. The current runnable model chapters are cue-only. Chapters 00 and 04
explain the accepted historical joint experiments, including native navigation bins,
relative-duration pairing, changed cue exposure and mixed endpoint effects. There
is no matched joint arm for the new 27-unit panel.

**Suggested handoff:** read 00 → 00a → 00b → 01 → 02 → 03 → 04. Answer the
interpretation prompts before changing a
parameter. The 3D plots retain the fitted model's dimension and display three existing
coordinates; geometry is descriptive, while source-disjoint readouts test recovery.
Computational transparency is distinct from identifying a biological neural state.

The separate [historical endpoint notebook](../report/endpoint_walkthrough.ipynb)
replays accepted saved artifacts. It is preserved unchanged; it is not fresh source
reconstruction and is not required by these notebooks.

## Read or run the teaching examples

Chapters 00/00a need no kernel. Chapter 00b includes seven executed arithmetic cells
and three figures; Chapter 04 includes two executed symbolic examples alongside
historical evidence. All those new outputs use invented inputs and no fitted models.
After installing notebook dependencies, reproduce just these examples with:

```sh
jupyter nbconvert --to notebook --execute \
  notebooks/00b_worked_example.ipynb notebooks/04_study_evidence.ipynb \
  --output-dir /tmp/neuro-teaching-new-run
```

The practical A/B/C source outputs remain empty. A's code is unchanged from its
verified non-fitting run. B/C have not been rerun; their revised orchestration was
tested with actual invented assemblies and mocked fitting. Historical learning
curves do not attest learning by the current compact-source models.

## Install and run the practical workflows

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

Notebook cell source is maintained in `scripts/build_fresh_notebooks.py`, the three
`scripts/notebook_*_guide.py` sources, and `notebook_foundations.py`,
`notebook_worked_example.py`, `notebook_study_evidence.py`. Run
`python scripts/build_fresh_notebooks.py` to rebuild all seven. This reads only
tracked public PNG/HTML figure assets, performs no neural reconstruction or fitting,
and clears code outputs, including the saved invented examples. Re-execute those
two teaching chapters separately to restore their outputs. Embedded historical
figures survive rebuilding and include source/image hashes.
Structural checks accept empty notebooks; optional saved
execution evidence must match cell hashes/order. Whole-NotebookA uses the existing
`no_fitting` guard before source work, not only late zero fit counters. Do not replace
source notebooks with private ID-bearing outputs.
`scripts/test_teaching_notebook_grid.py` compares original and staged orchestration
under a no-fitting guard, with deterministic mock estimators and actual invented
source assembly. It checks every case/input/label/argument, development reuse,
artifact names and budgets: B has 4 PCA/24 logistic/12 LDA; C has 6 CEBRA/6 PCA/54
logistic and six times the configured updates. It does not certify actual training.
`scripts/test_notebook_diagnostics.py` checks metric units, time-major 3D
coordinates, collapse diagnostics and plotting using invented arrays with fitting
blocked. Existing checks include `scripts/test_public_workflow.py` and
`scripts/test_fresh_notebooks.py`; some focused cases fit invented models, so inspect
their requirements before running. Do not use broad research-test discovery as
a substitute: some historical tests access private artifacts.

Artifact replay uses trusted joblib states only after authenticating a separately
retained manifest hash. Never load an untrusted pickle/joblib directory. The initial
implementation/draft PR did not grant a code license or publish lab inputs. The separate
October26 owner authorization covers only the compact source view and cleaned
assignments described above; it grants no new license, model/result publication,
merge or package-registry release. Original private inputs, execution manifests, predictions and fitted results
remain local.
