# Source reuse and population width — progress scratchpad

Started November 14, 2026. Classification: **exploratory analysis**.

**Original study status — November 15: completed.** All48unique cases trained, all numeric
evidence independently checked, both dated notebooks/reports delivered. Start with
[results and artifact links](README.md) and [validation](validation.md). The entries
below preserve intermediate states; old pending flags are not a new run queue.

**New follow-up in progress:** after `/teach max`, the owner requested fuller
end-to-end real-data notebooks and adding the completed work to a PR. The
[notebook execution plan](notebook-execution-20261115.md) fixes the same48-case
scope, separate fresh execution, visible first-case stages and publication review.
The earlier no-fit/no-publication closure remains history for the original run;
this new explicit request authorizes the bounded notebook follow-up. No merge.

## Owner's goal and scope

Use the existing recordings to construct new pseudopopulations, train fresh models
and evaluate two focused tests. Deliver two dated executed experiment notebooks,
training evidence, trajectories, confusion matrices and relevant documentation.

1. Select a population capable of at least five distinct eligible current training
   source identities per session × ordered start–goal class. Keep its columns,
   sessions, classes and evaluation fixed; compare nested budgets of 2, 3 and 5
   distinct sources at a fixed assembled training-row quota.
2. Fix the training-source budget at three and vary population width.

Keep the established raw/PCA/CEBRA-Time/native multisession comparisons and
logistic/RBF-SVM/kNN/LDA readouts plus standard source-label falsification controls.
Do not add model hyperparameter sweeps. After results, compare best/worst errors
and explain what issue #29 can establish with available coverage evidence.

The preceding coverage-first, wide knob draft is superseded by this owner steering.
No new biological recordings are needed or implied. Source identities and bins are
not independent biological replicates; the development set is historically exposed.

## Progress

- Read canonical workspace status and preserved the merged November 11 evidence.
- Owner explicitly authorized execution, fresh training and both final experiments.
- Began authenticated public-metadata feasibility checks for a common minimum-five
  cohort. The former 30/20/15 class lists have no minimum-five-eligible sessions;
  this new panel must therefore be chosen once from source availability before fits.
- No new biological model fits have started. Next: freeze the feasible panel and
  paired construction rules, review code/scientific assumptions, benchmark within
  resource limits, then train and collate both notebooks.
- Exact metadata selection completed: the nine classes retain 17 columns/3 sessions
  at minimum five and 83 columns/20 sessions at minimum three. Width ties were
  resolved using minimum-three width before lexicographic class order. The middle
  whole-session prefix has 49 columns/11 sessions. This uses no neural scores.
- Frozen intended scope is six unique arms: B2/B3/B5 at 16 rows/class, once-only U3,
  and two larger width arms at three sources. Three observed repeats and five
  source-label worlds cover all arms (48 unique cases; 2,448 fits; 96,000 updates).
  The shared B3 bridge is fitted once and referenced by both notebooks.
- Independent preliminary scientific review confirmed the two-part design and
  requested explicit distinct-not-independent wording, source-budget/weighting
  coupling, width/session confounding, sparse-endpoint baseline and map limitations.
- Frozen code/design committed as `4db1152`. All48 biological plans passed a
  non-fitting preflight (minimum training rank17,648.63MiB,13.87s). Invented report
  smoke passed both notebooks' collation paths,34+27figures and all confusion data.
- Final benchmark attempt02 stopped before any fit: automatic unused-import cleanup
  had removed the fit-accounting class exposed to the runner/notebooks. Preserved
  its failed receipt; restored an explicit re-export and added an entry-point check.
  Refreshed source-bound preflight/benchmark gates are required after this fix.
  No biological training case was attempted or retried.
- Corrected entry-point regression and all five scientific tests passed (six total).
  Refreshed prefit02 passed all48plans (minimum rank17); invented03 completed51fits
  and2,000updates,59.76s/case,739.72MiB,zero memory events. Independent gate review
  authenticated matching source/configuration/runtime and approved launch.
- Started the one planned biological run at `outputs/source-reuse-width-20261114/real-01/`
  under hard4GiB/zero-swap/two-CPU/10,800-second limits. Study/request date remains
  November14; Singapore's calendar crossed to November15 during preparation, so
  actual execution timestamps are retained rather than backdated.
- All12 observed source-reuse cases completed without fit/replay failures; the
  corresponding20source-label control cases are finishing. The first notebook
  then collates its evidence before the width notebook starts16new cases. The
  downstream auditor is being independently reviewed; it checks complete numeric
  tables, exact ties, saved source-block consistency and all report matrix views.
- The source experiment completed all32cases, its9executed code cells and34figures.
  The runner then failed at the notebook handoff: exclusive-create JSON correctly
  refused to overwrite an existing kernel specification. No width fit started.
  The failed `real-01` receipt and every completed case remain unchanged.
- The bounded [continuation amendment](continuation-20261115.md) preserves this
  boundary and permits only the16unattempted width cases in a fresh output directory,
  with32inherited cases distinguished from new execution. An invented two-kernel
  handoff smoke passed with separate immutable specs and no biological reads/fits.
  Independent continuation review is pending; no automatic biological retry.
- Independent review cleared the completed continuation implementation and exact
  parent boundary. Launched the16unattempted width cases once under hard7,200-second,
  4-GiB/zero-swap/two-CPU limits. Accepted output is being assembled separately at
  `outputs/source-reuse-width-20261114/complete-01/`; original `real-01` remains
  failed and immutable, with its32successful biological cases preserved byte-for-byte.
- The continuation completed all16new cases and the second notebook, with no case
  failure/retry. Combined48cases used2,448fits and96,000updates in22.90minutes;
  maximum1,321.11MiB, all memory-event counters zero. Both notebooks have9executed
  code cells. The8B3cases are authenticated shared evidence, not refits.
- Full numeric audit passed all3,155files,4,608split metrics,5,376report matrix views,
  all source/pool/error/paired tables,96learning curves and1,296latent class means.
  Independent review separately reproduced metrics with count-based formulas,
  verified exact best/worst ties and authenticated every inherited parent byte.
- Results are mixed by pipeline: Raw/PCA SVM pair association survives once-only
  assembly; broader source support helps Raw/Time SVM. PCA mean pair balanced accuracy
  rises at both width steps across all4readouts. Repetition and native width effects
  are not uniformly beneficial. Best/worst class errors were collated; missing
  spatial maps remain unknown and do not establish the#29place-field explanation.
- Fixed the normal runner's future handoff using separate immutable kernel specs;
  complete two-notebook no-fit regression passed. Independent review accepted the
  repair and narrow auditor handling of unused historical run.py drift. Old launch
  gates still reject changed source. This repair produced no biological evidence.
  A second full audit passed and preserves the first audit.
- Dated delivery adds one labelled interpretation cell per notebook while preserving
  all18original cells each, and adds4paired-change figures. Independent review caught
  a missing SVM/pair qualifier in U3 prose and unused nbconvert CDN loaders; corrected
  copies are `deliverables-20261115-03/`, with01/02preserved. All102delivery files,
  336score/336contrast summaries, local links, static/offline rendering dependencies
  and all eight SVM best/worst error summaries passed independent review.
- Durable results/validation and workspace pointers now identify the completed
  study. Source notebook outputs stay empty; generated neural evidence stays local.
  No new model sweep, fitting, retry, publication or issue modification is queued.
- Local closure commit `dd7de7f` saves the full audited handoff. Final independent
  provenance review reconciled all24available ledger hashes, historical auditor
  identity, both audit count sets, phase resources and all102delivery files. Entry
  points now explicitly qualify PCA width gains as mean pair balanced accuracy.

## Preservation

Prior outputs/runtimes and unrelated `src/neuro/_cebra_sampling.py` edits and
`docs/reports/current-state-20260927/` remain untouched. No publication, push,
merge, issue modification or old-experiment retry is part of this run.

## November15 end-to-end notebook follow-up

- `/teach max` completed first: self-contained interactive lesson at
  `/tmp/pi-teach/20261115-015340-reuse-width-max/results.html`, SHA256
  `f60c2f9d85356f29ce8641fbc56196124ce39b08ff30f23b1a4b3b2fafeafd93`.
  Independent methods/claims reviews and94browser states passed. The cmux
  terminal had no unique owning pane, so no native tab/server was created;
  explicit SSH-copy/open instructions were supplied. The lesson stays disposable.
- Implemented two richer notebook sources in `walkthrough_20261115/`, preserving
  original study sources and outputs. First-case numerical fitting is visible in
  separate cells; all later cases retain the fixed schedule. New local persistence
  code reuses maintained estimators, with no shared-package API changes.
- Three fit-blocked invented orchestration tests passed: distinct immutable
  kernels and exact bridge,48cases with first cases once, and staged failure
  accounting/no retry. Ruff passed new Python and notebook sources.
- Started the bounded invented full-width equivalence benchmark in
  `outputs/source-reuse-width-notebooks-20261115/invented-01/`. It executes the
  exact seven notebook fitting/arithmetic/diagnostic cells and compares the
  maintained routine. Independent code/notebook review is ongoing; no fresh
  biological fit for this follow-up has started.

- Invented01preserved as failed after both complete paths (102fits/4,000updates):
  strict archive-key ordering differed although all298saved arrays were bitwise
  equal. Corrected the staged serializer to preserve the original key order;
  no numerical tolerance or prediction changed. Independent code review found
  no remaining scientific/model-path blocker, conditional on refreshed gates.
  Teaching review clarified previous-goal start labels, U3's probability ceiling,
  the shared B3 execution and complete class/secondary-metric tables.

- Invented02passed all298arrays and complete tables,102fits/4,000updates,
  115.95seconds,699.27MiB. Prefit01stopped before reconstruction for a missing
  explicit launcher flag; preserved. Corrected prefit02passed48plans/minrank17
  with fitting blocked,13.72seconds,599.97MiB. Matching gates independently
  authenticated140files/51codepins/64input hashes and cleared one launch.
- Started fresh bounded biological reproduction `source-reuse-width-notebooks-
  20261115/real-01` after both reviews and gates, using4GiB/no swap/two CPUs/
  three-hour ceiling. The earlier accepted48cases are not used to initialize
  models and are not pooled as additional biological evidence.

- Publication review caught one overstatement in a methods Markdown sentence:
  same-session/source-trial grouping does not establish simultaneous recording.
  Preserve running source pins and its frozen snapshot; correct that sentence
  explicitly in publication copies, append an editorial note, and independently
  verify that every executed code cell and output is unchanged. The main entry
  points will link the corrected copies; frozen sources retain execution provenance.
  No fitting changes are needed.
- Fresh reproduction completed all12observed reuse cases and is finishing its
  20source-label control cases without fitting failures. Numerical interpretation
  and publication remain pending the completed-run audit.
