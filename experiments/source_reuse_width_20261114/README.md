# Two experiments — November 14, 2026

One fixed endpoint task, two focused questions, fresh training on existing recordings:

1. [Source reuse](source_reuse_20261114.ipynb): nested 2/3/5 distinct training sources
   at 17 recorded columns, plus the same-three-sources once-only standard control.
2. [Population width](population_width_20261114.ipynb): 17/49/83 recorded columns,
   all using three training sources/session × class. B3 is an authenticated shared
   bridge from experiment one, fitted once.

Four representations (raw, PCA7, CEBRA-Time7, native multisession7), four readouts
(logistic, RBF-SVM, kNN5, SVD-LDA), pair/start/goal heads, three observed repeats and
five source-label diagnostic worlds. Six unique arms, 48 unique cases, 2,448 fit
calls excluding scalers, 96,000 updates. No model hyperparameter sweep.

[Frozen protocol](../../docs/experiments/source-reuse-width-20261114/protocol.md) ·
[metadata design](../../docs/experiments/source-reuse-width-20261114/design.json) ·
[progress scratchpad](../../docs/experiments/source-reuse-width-20261114/scratchpad.md) ·
[validation](../../docs/experiments/source-reuse-width-20261114/validation.md).

Source notebooks intentionally have empty outputs. Executed notebooks, reports,
all fitted models, predictions and receipts belong in the ignored
`outputs/source-reuse-width-20261114/` directory. The notebooks contain actual
training calls; do not execute them casually to read the evidence.

The experiment is kept here as one unit. `study.py` owns its selection/plans and
schedule; it consumes maintained package helpers without changing package APIs.
`run.py` owns gates, resource checks and fresh kernels. `report.py` collates saved
predictions and makes all-matrix explorers. `build_notebooks.py` builds the two
source notebooks. `test_study.py` and `self_test_report.py` verify invented inputs
with fitting blocked. The renderer smoke produces invented results only.

## Execution contract

Use the documented existing runtime and `PYTHONPATH` from the validation ledger;
do not install into or modify an old runtime. The runner requires a systemd cgroup
with hard 4-GiB memory, zero swap, two-core CPU quota and control-group termination.
Its modes are:

```text
python -m experiments.source_reuse_width_20261114.run --mode benchmark --output <fresh-invented-directory>
python -m experiments.source_reuse_width_20261114.run --mode preflight --output <fresh-prefit-directory>
python -m experiments.source_reuse_width_20261114.run --mode train --output <fresh-run-directory> \
  --benchmark-receipt <benchmark.json> --benchmark-sha256 <pinned-hash> \
  --preflight-receipt <preflight.json> --preflight-sha256 <pinned-hash>
```

The biological modes require `NEURO_REUSE_ALLOW_BIOLOGICAL=1`; passing that flag
alone does not bypass the reviewed protocol or training gates. Every launch uses a
fresh output directory; no automatic retry/resume. The two gates bind numerical
source, configuration, design and runtime identities, and the train runner pins
the complete code/protocol snapshot. Hard biological runtime ceiling is three hours.

Distinct source IDs, added columns and repeated synthetic rows are not independent
biological replications. Width adds sessions and measured sources together. The
development set is historically exposed and label-conditioned. Spatial-field
coverage remains unknown; #29's place-field explanation needs authenticated maps.
