# Shareable scientific modules and executable notebooks

**October 23, 2026 — owner-approved north star; implemented and bounded real run accepted.**
The owner subsequently requested building and running this end to end on real data,
with independent subagent validation. [Execution ledger](shareable-notebooks-execution-20261023.md)
and [bounded real-data protocol](shareable-notebooks-protocol-20261023.md) record that
authority, actual progress and execution gates. The planning-time inventory below
is preserved as the baseline, not a claim that every proposed feature has shipped.
Inspected checkout: `3f84018` (`main`). Owner requested clearer package boundaries,
fresh-input runnable notebooks, visible source/target/split construction and dataset
ablations. Three independent read-only scouts covered models/packaging, data/labels,
and notebook/testing boundaries. This document records that direction and a proposed
sequence. It does not authorize private-data access, installation, fitting or publication.
The [as-built design](software-design.md) still describes current implementation.

## 1. Decision in plain language

Ship **one installable Python distribution with three independently usable public
modules**: pseudopopulation construction, PCA/LDA baselines and CEBRA. These are not
three separate PyPI projects unless independent ownership/releases later require it.
Reuse NumPy, sklearn, CEBRA and our existing algorithms; do not reimplement their models.

Notebooks own the visible experiment: question, supplied inputs, target formulation,
stepwise calls, intermediate tables/plots, assertions and interpretation. The library
owns reusable computation and validation. Study code owns dataset-specific semantics
and protocol choices. Neither a giant hidden `run_everything()` call nor copied
algorithm implementations in notebook cells meets this goal.

**Fresh computation and saved-result replay are different products.** Preserve
`report/endpoint_walkthrough.ipynb` as the accepted historical saved-input replay.
Add fresh-computation notebooks; do not relabel the existing replay as raw-to-result
reproduction or overwrite its execution evidence during experiments. Once the fresh
workflow is implemented and its biological execution separately approved/validated,
make that workflow the active source-to-result walkthrough; retain the old notebook
as a clearly labelled historical replay, not the only runnable scientific entry point.

## 2. What exists, and how complete it is

| Area | Implemented today | Missing for a shareable first release |
| --- | --- | --- |
| Pseudopopulation | Endpoint and binary-component planners/materializers, lineage, support and split checks | Independent supplied-input API; validation at the public boundary; dimensions/classes not tied to one cohort; construction notebook |
| PCA | Training-bin PCA and transformation in both endpoint/full-trial studies | Independent sklearn-based API and explicit feature layout/component policy; no CEBRA import required |
| LDA | Endpoint SVD-LDA **classifier**, training-only scaler, probabilities and saved sklearn model | Independent classifier workflow; LDA projection must be explicitly introduced if wanted, not claimed as existing |
| CEBRA | Solver, vector dataset, phase-aware samplers, training, embedding, checkpoints and exposure accounting | Separate reusable fit/transform from study filesystem/approval policy; standalone bounded example |
| Data/targets/splits | Raw readers, binning, outer-split access gate; actual endpoint producer and label/inner-split logic in historical scripts | Explicit source/target/unit contract and adapter; visible derivation/exclusions/dependency audit |
| Evaluation | Readouts, metrics, confusion matrices, nulls and source-deletion sensitivity in studies | Small reusable evaluation functions and explicit distinction between sensitivity and refitted ablations |
| Notebook | One tracked notebook; genuine model inference and readout replay on authenticated saved inputs | Fresh source-to-assembly-to-fit execution without old result directories |
| Distribution | Checkout imports and general project metadata | Explicit build/package discovery, direct dependencies/extras, installed-wheel checks, documented support and licensing decision |

This is implemented research software for the locked studies, **not yet a finished
portable toolkit**. Roughly 9,100 lines sit in three study modules; full-trial supplies
algorithms to endpoint and cue-time. No percentage-complete estimate is justified.

Evidence:

- [`src/neuro/README.md`](../src/neuro/README.md): current modules and dependencies.
- [`endpoint_time_readout.py:533–681`](../src/neuro/studies/endpoint_time_readout.py#L533-L681): endpoint construction.
- [`endpoint_time_readout.py:1709–1901`](../src/neuro/studies/endpoint_time_readout.py#L1709-L1901): feature/readout fitting and persistence.
- [`full_trial_transfer.py:1713–1884`](../src/neuro/studies/full_trial_transfer.py#L1713-L1884): shared CEBRA training/embedding and PCA.
- [`report/endpoint_replay.py`](../report/endpoint_replay.py): fixed saved-run adapter, not a general dataset loader.
- [`pyproject.toml`](../pyproject.toml): no explicit build backend/discovery; current general dependencies do not establish standalone sklearn/CEBRA notebook support.

## 3. Proposed boundaries

Names below are proposed, not existing imports or a finalized API specification.

| Public area | Owns | Must not own |
| --- | --- | --- |
| `neuro.pseudopopulation` | Support checks, seeded source-selection plans, intact block materialization, row/block lineage and reconstruction | Inferring biological label meaning, selecting a favorable cohort, model fitting |
| `neuro.pca_lda` | Small sklearn-based train-only scaling/PCA and LDA classification operations; explicit layout and fitted state | Hardcoded 195 units/ten bins/eight dimensions; study output directories; importing torch/CEBRA |
| `neuro.cebra` | Existing dataset/sampler/solver/training/embedding machinery, resource checks and returned training diagnostics | Importing a concrete study, discovering private inputs, defaulting to a dated run, automatic publication |
| Supporting input/split code | Validated source/unit/target tables, counts/masks/exposure, split and dependency checks | Universal data-format ingestion or an automatic target-definition engine |
| Supporting evaluation code | Predictions, metrics/confusions, support accounting and declared controls | Treating synthetic rows as independent biological observations |
| `neuro.studies.*` | Concrete dataset adapters, label rules, experiment configuration, budgets/approvals and result writing | Being the owner of common algorithms that other public modules must import |

Retain useful existing helpers: `raw_io`, `neural_inputs`, `place195_split_access`,
`geometry`, `execution`, `provenance`. Extract only necessary shared operations; do not
create one package per helper, an abstract runner, plugin registry or execution service.
Checkout-specific `study_sources` belongs to study provenance; installed library use
must not depend on finding repository scripts/docs or Git history.

Dependency direction: **notebook/study → public algorithms → validated inputs and
third-party libraries**. Public modules must not import studies, notebooks or `scripts`.
Pseudopopulation use must not require CEBRA or a GPU. Declare directly used dependencies;
make CEBRA/torch and notebook tooling optional installation extras where practical.

Preserve scientific differences during extraction:

- Endpoint assembly samples both splits; binary full-trial validation enumerates a
  Cartesian product. Keep these named policies distinct and bound any enumeration.
- Endpoint PCA pads reduced-rank outputs to eight coordinates; full-trial assumes
  eight components. Padding remains an explicit legacy-study policy, not a hidden
  property of general PCA. Preserve raw unit-major versus latent time-major layouts.
- LDA is supervised; PCA is not. Existing raw SVD-LDA is a classifier, not a
  dimension-matched unsupervised embedding baseline.
- Keep CEBRA's actual phase/row/native-bin sampling and exposure diagnostics. Replacing
  these with the library default sampler would be a scientific change, not cleanup.

## 4. Data and target contracts come before model extraction

First supported public input: **explicitly supplied binned source data and metadata**,
not preassembled/standardized pseudorows or fitted results. It is acceptable to start
from professor-provided formatted source data; record inherited preprocessing and
missing provenance rather than pretending raw reconstruction occurred. A separate
explicit adapter handles available raw/event ledgers.

Keep these linked objects inspectable:

| Object | Minimum meaning |
| --- | --- |
| Source ledger | Dataset-qualified source ID, session/block ID, trial order and predecessor/dependency IDs where relevant, inclusion/exclusion reason, provenance |
| Unit ledger | Stable unit IDs and block membership; selection provenance; verified simultaneity status/evidence or explicitly unknown |
| Neural values | Declared source × unit × bin layout, count/rate units, bin edges/event reference/clock, exposure, and observation mask; distinguish zero from missing |
| Target table | Source ID, target name/value, derivation and version, source fields, measured/derived/unverified status, allowed classes and exclusions |
| Split table | Source/group assignments frozen before assembly/learned processing, independence policy and historical exposure; all phases/derivatives stay together |
| Assembly plan | Matching keys, unit panel/blocks, sampling/replacement policy, row budget and seed, effective condition map for observed/null worlds |
| Assembly lineage | Each synthetic row/block → exact contributing source and bins, with reconstructable values and targets |

The first implementation should support only its declared mask/exposure semantics.
Current source × unit masks assume complete observed bins within a block; reject
unit-specific/per-bin dropout that cannot be represented, or implement and test that
support deliberately. Do not flatten unavailable measurements into zero counts.

### What our current “ground truth” actually is

The current endpoint producer is
[`scripts/start_goal_cebra_baseline.py`](../scripts/start_goal_cebra_baseline.py),
not the latest notebook. Its chain is:

```text
selected recording snapshot → imported trial/unit/spike ledgers
→ outer source split/access gate → eligible endpoint trials → inner split
→ binned source tensor → condition-matched session-block assemblies
```

It derives start from the previous successful trial's marker digit and goal from the
current marker digit, with adjacency, success and multimodal/QC rules. The notebook
must show those raw fields, derived values, exclusions and a worked join. Call this a
**derived target table**, not independently verified behavioral truth. Marker agreement
does not confirm the laboratory meaning of the endpoints. Unit preselection is inherited.

Separate **matching condition** from **prediction target**. Pair-conditioned assembly
can support pair/start/goal targets through a declared mapping; a binary-component
assembly cannot silently inherit one constituent trial's full route as its target.
Known-label matching in development defines a conditional assay, not an unknown-trial
prediction pipeline, even when CEBRA uses a Time objective. Derive behavioral targets
from behavioral/task evidence, not the neural values being tested. If a target mapping
is learned (for example, behavioral clustering), learn it on training sources only,
then freeze and apply it to evaluation sources.

The current inner split randomizes within session/pair; it is not globally chronological
and does not group predecessor-linked trials. New analyses must explicitly assess and
handle serial/label dependencies (appropriate grouping, temporal blocking/embargo or an
honestly limited estimand), not merely assert disjoint tensor row IDs. Do not silently
change historical splits or call exposed development a clean test set.

## 5. Runnable notebook family

Use three teaching/work notebooks, one per requested scientific unit. Each is runnable
from its declared source inputs in a fresh kernel; none requires another notebook to
have run or a historical `outputs/` tree. Shared upstream steps call the same library
functions rather than copying code or executing another notebook.

### A. `notebooks/01_pseudopopulation.ipynb` — proposed

1. State the question, input boundary, target and strongest permitted claim.
2. Load source/unit metadata and neural data; show units, timing, mask/exposure and QC.
3. Build the target table in visible steps; show contributing fields, assumptions,
   exclusions and target consistency checks. Private examples stay local; public ones
   use invented identifiers/values or reviewed aggregates.
4. Freeze/validate source splits; plot per-session chronological assignment, class
   balance and predecessor/group dependencies. Show source overlap checks.
5. Plot eligible session × class × split support, unit counts, missingness/exposure,
   and an inclusion/exclusion waterfall. Report absent support, not only pooled totals.
6. Build one annotated synthetic row from selected source blocks; then assemble the
   bounded cohort and reconstruct it from lineage.
7. Compare **eligible / used / unused / repeatedly used** real sources and constructed
   row distributions; show reuse histograms, pair/marginal balance and source overlap.
8. Separate pass/fail mechanical checks from unresolved biological assumptions.

No model fitting is needed to demonstrate construction. Downstream predictive validity
requires a declared baseline/control protocol; attractive distributions alone do not
prove it.

### B. `notebooks/02_pca_lda.ipynb` — proposed

Rebuild validated assemblies from supplied source inputs; fit preprocessing/PCA/LDA on
training only. Show feature layouts, scaling statistics, PCA explained variance and
projections, LDA's label use, class support, train/development predictions, balanced
accuracy and count/normalized confusion matrices. Use a common readout for comparing
representations; report direct LDA classification as a distinct supervised baseline.
All figures derive from this run. Never present a 2D separation plot as held-out evidence.

### C. `notebooks/03_cebra.ipynb` — proposed

Rebuild the same declared inputs; expose training-only normalization, temporal pairs,
boundaries, objective, architecture, seeds, update budget, device and realized sampling
exposure. Fit CEBRA, transform evaluation inputs and fit/evaluate the declared readout;
compare with newly fitted raw/PCA references on matched evaluation support. Plot training
diagnostics, embeddings, held-out metrics/confusions and controls. Start with the bounded
cue-only workflow; joint navigation is a separate step requiring valid phase timing and
pairing, not a default hidden dependency. A tiny demo is not a reproduction of the
historical 1,000-update biological study or evidence of biological dynamics.

Every meaningful notebook section follows:
**declared input → package call → visible intermediate → assertion/diagnostic → limit**.
The notebook may contain orchestration and figure styling, but not duplicate numerical
algorithms or hide important choices inside a single opaque pipeline call.

### Execution and sharing contract

- Public default: a small, clearly invented source-level dataset, bounded CPU execution,
  no private files, credentials, network download or old fitted result required.
- Explicit supplied-data mode: dataset path, adapter/target/split policy and budget.
  Demo and supplied-data modes use the same validated computational path, not a
  synthetic-only implementation. Missing inputs fail; never silently substitute demo
  data or saved results.
- Initial demo fits are software smoke tests. Real biological fits/raw access need
  separately approved inputs, protocol, budget and independent scientific review.
- Start with empty outputs; restart-and-run-all must execute all cells in order. No
  obligatory cache. Writing fresh artifacts for inspection/replay is allowed but cannot
  replace computation with historical results. Do not add cache/resume machinery now.
- Record input/config hashes, source revision/dirty identity or installed-package
  identity, dependencies, seeds, device/threads, exclusions and output hashes. Define
  numerical tolerances; CPU portability is not bitwise historical CUDA equivalence.
- Write to a fresh run-owned directory; validate/export before any explicit promotion.
  Do not overwrite accepted notebooks/artifacts. Review text, figures and metadata for
  private values; a keyword denylist is not a privacy proof.

## 6. Dataset ablations must name what changes

Use a small explicit comparison table in the notebooks, not a sweep framework.

| Question | Required action |
| --- | --- |
| Sensitivity to evaluation sources | Freeze fitted models; remove evaluation-source contributions and rescore. This is not retraining. |
| Less/different training data | Select source-level training subsets, reassemble and refit scaler/PCA/encoder/readout. Keep declared evaluation support fixed for matched comparisons. |
| Different units/session panel | Revalidate support, masks, feature identity and dimensions; rebuild/refit. Report changed population/estimand. |
| Different bins/window or input processing | Recompute from an input boundary that supports the change; changing a pre-binned file's metadata is not rebinning. |
| Another dataset/label definition | Supply its adapter and target provenance; establish comparable target/time/units or report a separate experiment, not a paired leaderboard. |

Never select ablations or rescue support using held-out neural outcomes. Predeclare
comparisons, preserve the split, report lost classes as inestimable, and distinguish
computational seeds from biological replication. Held-out session designs need special
care because a different recorded unit panel changes the feature space.

## 7. Implementation sequence and release gates

1. **Contract and first vertical slice:** extract input validation and pseudopopulation
   planning/materialization; build notebook A on a hand-checkable public fixture and a
   second differently shaped fixture. Expose target/split/lineage first. This is the
   first useful deliverable for the current reviewer concerns.
2. **Independent baselines:** extract sklearn-based PCA/LDA and minimal evaluation;
   notebook B executes fresh fits and one full-versus-reduced-training-source ablation.
   Keep historical shape/padding/label policies explicit.
3. **Independent CEBRA:** extract actual sampler/trainer/embedding machinery and separate
   optional saving from fitting; notebook C executes a bounded fresh CPU demo and the
   same kind of refitted source ablation. Retain resource, finite-loss, pairing and
   exposure checks.
4. **Distribution and preservation:** establish build/discovery and dependency extras
   during the first slice; certify wheel install/import/notebooks outside the checkout
   before release. Obtain code-license permission (no tracked license was found by the
   inventory), and keep private lab-data rights separate. Preserve accepted source/run
   history; migrate concrete studies only with reviewed equivalence checks.
5. **Approved biological use:** only after code/data-contract review, choose supplied
   biological inputs and ablation estimands. Execute fresh studies with a separately
   bounded plan. No biological run is queued by this design.

Acceptance is concrete, not “the notebook renders”:

- Standalone imports do not open data, fit or depend on study modules/Git checkout;
  pseudopopulation/PCA work without CEBRA installed.
- Invented inputs exercise different unit/session/bin/class counts, repeated sources
  and missing support. Check duplicate IDs, joins, exposure, block identity, effective
  labels (including null maps), split/dependency policy, shape ordering and complete
  lineage reconstruction. Public-boundary validation must not trust arbitrary plans.
- Leakage, invalid metadata, unsupported missingness and missing classes fail explicitly.
  The current loader/materializer's reliance on authenticated internal inputs is not
  sufficient validation for arbitrary supplied data.
- Train-only learned stages are checked; independent hand calculations/sklearn references
  verify small examples. Negative and known-signal controls distinguish broken plumbing
  from predictive performance. Geometry remains descriptive.
- In notebooks B/C, demonstrate a bounded invented-data ablation: full versus reduced
  training-source pools, reassembly and fresh fits of every learned stage used by each
  method. Assert identical evaluation-source/row lineage and target support; display
  source counts, reuse, configuration and paired metrics. No performance improvement is
  required. This gate cannot be satisfied by rescoring stored predictions.
- Fresh kernels with old results unavailable execute all three demos; input changes are
  recorded and a hand-checkable input perturbation verifies recomputation. A clean
  installed-wheel environment, not `PYTHONPATH=src`, validates distribution claims.
- Test selections distinguish non-fitting checks, synthetic fitting and authorized
  private execution. Reuse `unittest` and existing notebook tooling; do not run broad
  research discovery without inspecting private/fitting boundaries.
- Existing pinned-AST and source-listing checks are migration evidence. Account for
  every moved definition and add behavioral equivalence at new boundaries; do not
  simply loosen historical tests/hashes to obtain green results. Changed policies need
  explicit new tests and evidence, not a claim of historical parity.
- Preserve the accepted notebook's source listings against immutable source blobs at
  `3f84018`, rather than editing its frozen listings to follow new line locations.
  Historical checkout-only tests can verify those pinned blobs/hashes; new notebooks
  link to their actual package version. Keep original replay source/runtime available
  for separately authorized re-execution; refactoring does not certify historical
  replay against the new package. Installed-library tests must not require Git history.

## 8. Limits and unresolved release decisions

Mechanical checks can establish linkage, support, count/mask integrity, source separation
under the declared policy and reproducible computation. They cannot establish laboratory
marker semantics, simultaneous recording, biological independence/exchangeability,
unbiased unit selection or missing cross-session noise correlations. Report these
separately rather than a single “pseudopopulation valid” badge.

Before implementation/release, settle the exact supported input schema and first target,
code license/distribution name, and bounded synthetic-fit scope. LDA classification is
already implemented; LDA projection would be additional behavior. A biological input
cohort, wider raw import and the ablation grid require their own agreement.

Independent read-only review found one gap: ablations were described but not an
executable release gate. The plan now requires the bounded refitted comparison above;
it also explicitly separates frozen notebook-listing checks from current source.

This planning pass performed source/document inspection and documentation updates only.
No scientific imports/tests, fits, notebook execution, dependency installation, private
input/artifact access, stash operation or accepted-result modification was performed.
