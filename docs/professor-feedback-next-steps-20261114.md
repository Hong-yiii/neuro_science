# Professor feedback: spatial coverage and the next experiment — November 14, 2026

**Assessment and recommendation, not an agreed or frozen execution protocol.**
Hongyi asked what to do next after the completed population/reuse study and the
latest issues recording the professor's feedback. This review read GitHub issues,
local source and existing reviewed reports. It performed no new scientific
analysis, neural-data access, model fitting or replay, and changed no GitHub issue.

## Recommendation

Prioritize **#29's verified spatial-coverage/error analysis**, then **#30's
selection-feasibility study**, then one bounded comparison of selection policies.
The immediate deliverable is a unit-to-field audit and an atlas aligning retained
and lost spatial coverage with the existing confusion matrices. A new accuracy
sweep would not supply the missing field measurements.

The operational question is: **at a fixed decoding task and comparable recording
and source budgets, does preserving reliable spatial coverage improve condition-level
decoding, and which errors change?** This is a proposed measurement/selection
question within the broader recoverability-and-transfer agenda. It is not yet
evidence that particular cells are biologically necessary or that a latent neural
state has been recovered.

## Latest issues and completed evidence

GitHub search and the repository's issue collection were inspected on November 14.
The newest issues are [#29](https://github.com/Hong-yiii/neuro_science/issues/29)
(created November 11 at 01:47:57 UTC) and
[#30](https://github.com/Hong-yiii/neuro_science/issues/30)
(01:51:22 UTC). Both remain open, labelled `enhancement` and `needs-triage`, with
zero comments. Their bodies describe proposed work; the user's description supplies
the link to the professor's feedback, rather than a separately inspected professor
transcript. No later issue was returned by the direct collection query.

| Issue | What the current evidence contributes | What remains |
| --- | --- | --- |
| [#24: classes versus width](https://github.com/Hong-yiii/neuro_science/issues/24) | Nine trained class/roster populations and explicit source/width tradeoffs. | A fixed-task, budget-matched comparison that isolates a declared selection question. Different K values remain different tasks. |
| [#25: reuse](https://github.com/Hong-yiii/neuro_science/issues/25) | Authenticated source use and U2/R16/F16 controls in the replacement study. | More independent measured support; reuse statistics do not create it or establish a universally adequate minimum. |
| [#26: exclusions and errors](https://github.com/Hong-yiii/neuro_science/issues/26) | Confusions, class errors, exclusion reasons and verified prediction changes. | Spatial tuning/coverage joins; source participation does not identify a bad cell or session. |
| [#29: lost place-field coverage](https://github.com/Hong-yiii/neuro_science/issues/29) | Retained/removed rosters and the prediction side already exist. | Authenticate field maps, coordinates, trial provenance and endpoint locations; compute the retained/lost coverage views. |
| [#30: minimum selectivity and coverage](https://github.com/Hong-yiii/neuro_science/issues/30) | A current source-support selector to compare against. | Define separate quality and coverage requirements, establish feasibility and test their value. |
| [#23: native multisession](https://github.com/Hong-yiii/neuro_science/issues/23) | November 11 actually trained a native discrete multisession comparator with multiple readouts. | Its broader real-session prediction/transfer question is unresolved; the existing pooled comparison does not isolate multisession training itself. |

This maps underlying questions to the replacement study. It does not certify every
acceptance criterion of the older, specifically scoped 27-unit issues as complete.
Their open status should not be interpreted as an instruction to repeat completed
experiments.

The [completed study](reports/population-grid-20261111/README.md) and
[error follow-up](reports/population-grid-20261111/error-analysis.md) establish the
starting point:

- Raw/PCA/CEBRA-Time with SVM retain endpoint association under once-only training
  assembly. Repeated training blocks are not necessary for that association.
- The nine populations span 8–138 columns, but all retain a minimum training pool
  of two real sources per session and pair. More columns did not remove this bottleneck.
- Deleted classes are not uniformly harder. In F16, greater reuse is algebraically
  the same ranking as lower total source availability at a fixed roster; the
  correlation cannot separate the two explanations.
- Removing sessions has model-dependent effects. For the 15-class F16/SVM comparison,
  S100→S33 reduces PCA pair balanced accuracy by 30.56 percentage points but increases
  CEBRA-Time by 7.78 points, averaging three computational seeds. These are separate
  refitted pipelines. A spatial-coverage explanation must accommodate both patterns.

## 1. Authenticate the tuning information

Inventory compatible existing maps before requesting another export or calculating
new maps. For each session-qualified recording unit, identify the field map, spatial
coordinates, preferred region/field extent, occupancy (time sampled in each region),
selectivity strength, reliability, measurement phase and source-trial membership.
Verify the start/goal-label-to-maze-location mapping independently of decoding errors.
Keep unavailable and unreliable maps explicit; neither is measured zero selectivity.

The [compact cue-source contract](../data/README.md) explicitly omits dense position
and heading. It can support the completed cue assay but cannot alone reconstruct
spatial rate maps. This assessment has not inspected private map files or established
how many current units have compatible maps. A place-selected cohort flag is not a
map of each unit's field or its tuning strength.

Use training-source-only estimates or an independent localizer for prospective
selection. Historical maps that include evaluation observations can inform a labelled
retrospective atlas; they cannot independently validate a policy selected using those
maps. If compatible maps are absent, the next scoped task is the required map export
or computation, with alignment/provenance review, before testing the policy.

Navigation place tuning and cue-period endpoint decoding describe different phases
and variables. A field near a goal does not automatically mean that unit encodes the
goal during the cue. The proposed analysis tests that relationship. A start–goal
pair is a condition label, not a physical location or measured path.

**Deliverable:** a field-availability/provenance table and validated coordinate joins,
including a clear count of unmatched, exposed and unreliable maps.

## 2. Complete the retrospective coverage/error atlas for #29

Within each fixed K, align S100→S67 and S100→S33 comparisons with the authenticated
common development rows and shared session-block projections already checked in the
error follow-up. Show all nine populations rather than only a successful example.

For each comparison, align retained/lost maze coverage, the independently fitted
start and goal confusions, pair confusions, per-class recall changes and wrong→right/
right→wrong counts. Show absolute coverage and a prespecified per-column-normalized
coverage summary, with occupancy/unreliable bins marked. Include raw/PCA/CEBRA-Time/
native results and SVM; retain other readouts and all computational seeds for context.
Keep both correct and incorrect classes visible beside source support and reuse.

Keep task changes across K separate. Do not pair their synthetic rows or give deleted
labels a destination score. Annotate width, session composition, source support,
firing/sparsity and occupancy differences. Treat the atlas as descriptive: the
current development set has already been inspected, related constructed rows are
dependent, and a session-group removal plus refitting is not a single-cell causal test.

**Decision:** determine whether lost coverage tracks errors consistently, only for
certain pipelines/regions, or not clearly. An absent association is a useful result;
it should weaken confidence in coverage as the explanation rather than trigger
error-driven region/threshold changes. The atlas does not prove sufficiency or necessity.

## 3. Define and check #30 before more training

Separate two requirements:

- **Unit quality:** a countable unit meets a prespecified selectivity-strength and
  reliability rule, with adequate occupancy.
- **Population coverage:** every independently defined required region has at least
  a prespecified number of qualifying recording units. A distinct-session minimum,
  if used, is a separate requirement and is not proof of biological independence.

Many strongly selective units can cover the same region while leaving another
region uncovered. Raising average selectivity alone therefore does not implement
the proposed coverage guarantee. No numerical selectivity cutoff or minimum unit
count is adopted by this assessment.

For the first feasibility pass, preserve the current K=30/20/15 class lists and
whole-session selection granularity. Count qualifying units within each candidate
session; do not additionally filter individual columns without declaring another
intervention. Retain one consistent feature set across classes. Decide whether
the three rosters must remain nested and enforce the coverage constraints on every
reduced roster, not only the largest.

The current [class optimizer](../src/neuro/studies/population_grid.py#L123) maximizes
recorded width, then total training sources among ties; the
[roster construction](../src/neuro/studies/population_grid.py#L261) ranks sessions by
harmonic training support. Neither uses spatial tuning. Adding coverage changes
which rosters are admissible and may reduce the available width or source support.

Plot a small declared feasibility grid: coverage/quality requirements versus columns,
sessions, distinct eligible/used trials, smallest class pool, no-reuse capacity and
expected reuse. Retain source/predecessor protections. Report infeasible settings
without silently dropping an endpoint or relaxing a threshold. Prospective policy
rules must be fixed without selecting the best accuracy on the same inspected data.

**Deliverable:** a coverage-versus-support tradeoff table/plot, explicit selection
rules and reasons for retained/excluded units or sessions. This identifies a concrete
bounded experiment; it does not require fitting encoders.

## 4. Then run one matched learning comparison

Choose one class panel and a feasible common budget from the measurement/feasibility
results, without choosing the panel that gives the preferred accuracy. Compare the
current support-based rule with a coverage-constrained rule. Include coverage-blind
matched selections from the same eligible candidate pool where feasible, matching
unit/session counts, tuning quality, firing characteristics and source support.
Prespecify any random selection repeats. This helps distinguish covering particular
locations from simply retaining more or cleaner columns.

Fix the target, evaluation construction, sampling policy, latent capacity and fit/
tuning budget across selection arms. Use the same source draws for shared session
blocks; different rosters necessarily change some contributors, which must be
reported. Equal column counts alone cannot remove every cohort or source difference.
If an adequate match is infeasible, report that limitation and scope a more controlled
within-session unit selection contrast separately.

Refit the complete training pipeline for each chosen population. This matches the
question of learning from the available recording set. Masking inputs to an already
fitted model answers a different question and is not an interchangeable shortcut.
Keep raw/PCA and CEBRA-Time, retain native multisession as a clearly specified
comparator, and prespecify SVM as a primary readout if continuing the current assay.
Existing alternative readouts can be secondary checks; freeze the actual small
fit grid and controls rather than automatically repeating every prior combination.

A separate targeted-removal versus matched-random-removal experiment could more
directly test model dependence on particular coverage. Choose removal sets from
admissible maps before looking at evaluation errors. Even a selective loss would
show dependence of this model assay, not biological necessity of the removed cells.

For new data, reserve an untouched evaluation partition before policy/threshold
selection. Reusing the current development set yields another exploratory comparison,
not independent confirmation. Independent code/scientific review and a frozen
resource/provenance protocol precede any new scientific execution.

## Recording priorities and the longer-term direction

As new data are collected, prioritize distinct trials in the weakest session×pair
pools and reliable sampling of prespecified poorly covered regions. Retain occupancy,
timing/phase, coordinate and unit/session identity metadata; record which units are
verified simultaneous. Protect fresh evaluation data now. Neither extra pseudorows
nor stronger field selectivity repairs a two-source bottleneck by itself. The present
results do not establish a scientifically sufficient universal minimum trial count.

The [broader agenda](cebra-observability-agenda-20261011.md) is a useful, reusable
representation. Once measurement coverage is characterized, a focused frozen-readout
transfer test, as in [#18](https://github.com/Hong-yiii/neuro_science/issues/18), is a
natural next model question. Current whole-cue fits do not by themselves supply a
matched train-time×test-time experiment; compatible inputs/readouts need their own
scope. A natural-trial or new-session claim requires session-preserving evaluation
without using held-out targets to assemble or adapt its inputs. Spatial coverage
constraints do not turn a condition-matched pseudopopulation into a simultaneous
population or establish formal observability.

**Next concrete work item:** authenticate the field maps and build the #29 atlas,
then use #30's feasibility results to choose one controlled training experiment.
The completed November11 study, error handoff and original artifacts remain the
accepted evidence; no additional model run is queued by this recommendation.
