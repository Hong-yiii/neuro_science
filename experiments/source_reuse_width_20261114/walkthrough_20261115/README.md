# Complete experiment notebooks — November 15, 2026

This follow-up makes the same two-part study visible from input reconstruction to
training and interpretation. It is a fresh computational reproduction on the same
recordings and seeds, not another biological replicate. The accepted earlier run
and all failure records are preserved.

Start with the reviewed, fully executed [source-reuse notebook](published/source_reuse_20261115.executed.ipynb)
and [population-width notebook](published/population_width_20261115.executed.ipynb).
Standalone [reuse HTML](published/source_reuse_20261115.executed.html) and
[width HTML](published/population_width_20261115.executed.html) can be downloaded
and opened offline. Each contains19executed code cells; the shared B3 fits are
authenticated once. The new48-case execution exactly reproduced the accepted
study's saved numeric results. See the [validation ledger](../../../docs/experiments/source-reuse-width-20261114/notebook-validation-20261115.md)
and [publication manifest](published/manifest.json).

The two source notebooks below are frozen execution provenance. A methods
sentence in their original Markdown overstates simultaneity: assigning columns
to the same session/source trial does **not** verify simultaneous recording.
The reviewed executed publication copies explicitly correct that sentence and
preserve every executed code cell/output, with recorded editorial provenance.
Use those reviewed copies for scientific reading; retain these source versions
to authenticate the actual execution.

The two frozen notebook sources are:

- [Source reuse at fixed width](source_reuse_20261115.ipynb): B2/B3/B5 and once-only U3.
- [Population width at fixed source budget](population_width_20261115.ipynb): B3/Wmid/Wfull.

Each first case exposes actual train-only scaling, PCA, CEBRA-Time, native
multisession CEBRA, readout fitting and scoring in separate cells. Manual scaler,
PCA and logistic calculations verify the fitted pipeline without extra fits.
The remaining fixed cases then run once. Width authenticates the eight B3 cases
from the first notebook. All four readouts and pair/start/goal heads remain in the
results, including negative findings. The executed copies also include a labelled first-case figure rendered from saved
aggregate records after the original Agg cell produced only a text representation.

## Scope and execution

The [prospective plan](../../../docs/experiments/source-reuse-width-20261114/notebook-execution-20261115.md)
and [original protocol](../../../docs/experiments/source-reuse-width-20261114/protocol.md)
fix the sources, splits, nine classes, six arms, seeds, controls and budgets.
There are48unique cases,2,448model-fit calls excluding scalers, and96,000optimizer
updates. Reading saved outputs does not train anything. Running the notebooks does.

Use the existing read-only runtime and the exact gate/run commands recorded in the
new validation ledger. The runner entry point is:

```sh
python -m experiments.source_reuse_width_20261114.walkthrough_20261115.run --help
```

Its `benchmark` mode fits two **invented** full-width cases: the maintained routine
and the exact visible notebook cells. It compares every result and preserves
actual accounting. `preflight` reconstructs real inputs and checks all48plans
with model fitting blocked. `train` requires authenticated, matching receipts
from both gates. Every mode requires a hard4GiB/no-swap/two-core cgroup; training
has a three-hour ceiling. A fresh output directory is mandatory and failures do
not trigger automatic retries. The second notebook has its own immutable kernel
specification. No notebook initializes from an earlier fitted model.

```sh
python -m unittest experiments.source_reuse_width_20261114.walkthrough_20261115.test_execution
```

These tests are invented, fit-blocked orchestration checks. They verify the two
kernels, first-case accounting, complete schedule, shared bridge and failure
records; they are not neural evidence.

## Files and evidence boundaries

`staging.py` only separates the accepted saving/scoring/reload operations into
visible stages. `execution.py` owns attempts and actual fit counts. Scientific
estimators remain the maintained helpers. `build_notebooks.py` builds both clean
sources; `interpret.py` derives prose from this execution's tables. `verify.py`
runs the complete numeric audit and compares authenticated saved results with the
accepted execution. Raw feature arrays, full source lineage and model states
remain in ignored local outputs; notebook outputs show reviewed aggregates.

Pseudopopulation rows are condition-matched combinations of different session
trials. Distinct source IDs, constructed rows and optimizer updates are different
counts. Known-label assembly and historically exposed development constrain every
claim. Spatial-field loss/selectivity in issues#29/#30is not measured by these
cue endpoint results.
