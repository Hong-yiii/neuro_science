# Population coverage: proposed knobs and analyses

**November 14, 2026 · Draft exploratory design · Fresh construction, training and evaluation intended.**

Hongyi requested a concrete definition of the next experiment's knobs and analyses
after merging PR28. This draft follows [issues #29 and #30](../../professor-feedback-next-steps-20261114.md)
and the [completed population/error study](../../reports/population-grid-20261111/error-analysis.md).
The accompanying [machine-readable proposal](proposed-design.json) is a design
inventory, not an executable runner configuration. No neural data or fitted models
were opened, and no new scientific computation occurred while preparing it.

**Owner clarification:** there are no newly collected recordings. The intended work
uses existing recordings to form new pseudopopulations, fit new models from scratch
and evaluate those fits. New training runs produce new experimental results; new
assembly draws do not add biological observations. No earlier fitted checkpoint is
an initialization or substitute for a proposed fresh fit. Existing development data
remain exposed; a new split of already inspected observations is not a fresh test.
Fresh exploratory training on the existing recordings is the intended scope.

## Questions and order

1. **Coverage:** at a fixed task and recording/source budget, does a population
   selected to preserve reliable spatial coverage decode better than support-based
   selection and matched coverage-blind selections?
2. **Source diversity:** on one fixed population, how do additional distinct measured
   sources compare with additional assembly draws from the same sources?
3. **Model sensitivity:** on one fixed population/assembly, do longer optimization,
   temperature, dimension or temporal pairing change learning and held-out errors?

These are separate comparisons. Do not multiply every knob into one Cartesian grid.
First authenticate maps and examine feasibility; then freeze the coverage comparison.
A small convergence sensitivity can be scoped separately while the map inputs are
being prepared. It does not substitute for the coverage experiment.

## A. Population and source knobs

| Knob | Proposed levels | First use and interpretation |
| --- | --- | --- |
| Class task | Existing fixed K=30,20,15 lists for feasibility; one K for primary training | Choose the largest K with an admissible matched comparison using metadata/map availability, never decoder accuracy. Do not reselect classes separately for each arm. |
| Session budget | Two reduced budgets near one-third and two-thirds of eligible sessions | Specify exact counts after inventory. Also match recorded columns. At the full eligible roster, selection policies can collapse to the same population; that is a reference, not a useful selection contrast. |
| Selection rule | Support-based; coverage-constrained; matched coverage-blind random | Three policy families at each budget. Preserve whole-session blocks initially. |
| Selectivity quality | One fixed qualifying rule for primary analysis | Numerical metric/cutoff, occupancy and reliability requirements await verified maps. Unknown maps cannot satisfy a coverage requirement. |
| Required spatial coverage | Minimum qualifying units per required region m=0,1,2 in feasibility | m=0 is no coverage constraint, not no responsive cells. Propose m=1 for the first constrained policy; m=2 is feasibility/sensitivity, not a second mandatory training sweep. Neither is a proven sufficient biological minimum. |
| Session diversity per region | Report distinct contributing sessions; no extra minimum initially | An optional session minimum is another constraint, not interchangeable with unit counts. |
| Eligible training support | At least 2,3,5 distinct sources/session×pair, feasibility only | Do not presume stricter panels exist. Keep the global source/predecessor embargo and development minimum. |
| Used training-source budget b | One common b for all primary selection arms | Select the largest feasible value in {2,3,5} across the complete planned comparison, before fitting. Same-session shared sources use the same deterministic selection. |
| Synthetic training rows r | 16/class in the selection comparison | Use balanced cycles. With b fixed, all arms have the same reuse fraction; differences in coverage are not also differences in training-row quota. |
| Separate source comparison | (b,r)=(2,2),(2,16),(b_high,16) | Third arm requires b_high>2 on the same fixed population. Source subsets are nested. If infeasible, report it; do not silently change the roster/class task to manufacture that contrast. |

A qualifying-unit threshold determines which units count toward coverage. It does
not automatically remove every nonqualifying column from a retained session.
Filtering individual columns would be a separate declared intervention. Every
class uses the same retained column set.

Define regions, field-overlap rules, coordinates and start/goal mappings before
examining coverage/error associations. Navigation place fields do not automatically
measure cue-goal selectivity. Prefer training-only or independent-localizer maps;
historical maps using evaluation observations support a retrospective atlas only.
Map-estimation sources must themselves respect the protected contributor boundary,
including predecessor overlap; a localizer's independence must be checked explicitly.
The compact cue export lacks dense position/heading, so map availability and
provenance are genuine unresolved inputs.

The existing Julia field implementation provides a concrete inventory starting
point: [`SpatialResponseFields`](../../../Hippocampus.jl/src/response_fields.jl)
stores field-bin indices, rates and generation arguments. Its default uses all
trials; that does not prove which trials an existing file used. Inspect the actual
arguments and trial provenance before treating any exported map as training-only.
Its shuffle significance cutoff is also not a selectivity effect-size threshold.

Report the trials used to estimate field maps separately from the b trials used
per session×pair to train encoders/readouts, including their overlap. If map
estimation uses a broader training pool or a localizer, b describes the model-fit
source budget, not the total measured data used by the complete selection pipeline.

For each proposed session budget, start from the support-ranked roster's column
budget and require alternatives to match both counts. Freeze deterministic
support-ranking/tie rules and matching tolerances before decoding. Match training
quality/firing summaries where feasible; disclose residual differences. If a
coverage-constrained or suitable random roster does not exist, record that cell
as infeasible. If policies select identical rosters, record the duplicate instead
of treating it as independent evidence.

The proposed feasibility priority is fixed class lists in descending K, then the
two baseline recording budgets under the original minimum-two/minimum-one source
gate, then admissible matched rosters at both budgets, and finally the largest common
b in {2,3,5} for those frozen rosters. Do not silently trade away classes or change
rosters again to raise b. The exact constrained-roster objective/ties, quality-match
tolerances, random-roster sampling distribution and handling fewer than three distinct
admissible random rosters must be specified before execution. Matching counts does
not isolate every neural/session trait: the estimand is the effect of the declared
coverage-informed selection rule in this assay.

## B. A bounded first coverage comparison

The proposed design is **three selection families × two recording budgets**, on
one fixed class task, source-use policy and model recipe. Use three independently
declared random-roster draws for the random family and three paired computational
repeats. Each repeat records separate source-subset, assembly and model seeds. These
are computational sensitivity repeats, not independent biological replications.

At each budget: one support roster + one constrained roster + three random rosters
= five memberships. Two budgets × five memberships × three paired repeats gives
**30 observed cases**, conditional on feasibility. Within a repeat, share the
source-subset/assembly/model seed tuple across selection arms and use a compatible
master plan so shared sessions have identical source draws. Keep the three random
roster memberships fixed across repeats, and keep observed development construction
fixed across all arms/repeats with verified shared-block projections. Spread across
repeats combines construction and optimization variation; it is not model-only
uncertainty. The separate model-knob studies hold assembly fixed.

Build the master plan on the union of admitted sessions using canonical
(session,pair,split,repeat) source choices. Drawing sequential RNG samples separately
inside each roster would not guarantee shared sources. Alternative rosters need not
be nested: record shared, added and removed sessions/columns. A prediction switch
then compares corresponding constructed rows with changed contributors, not one
unchanged measured trial. If no blocks are shared, do not present the comparison as
source-matched; class-level policy contrasts can still be reported descriptively.

Keep raw/PCA7/CEBRA-Time7/native multisession7 and logistic/RBF-SVM/kNN5/SVD-LDA,
with independently fitted pair/start/goal heads. The proposed primary outcome is
the within-task difference in **pair balanced accuracy with SVM**; goal and start
confusions/recall provide the prespecified spatial interpretation. Report the primary
contrast separately for each representation, not only the winning model.

For this first selection comparison, retain the earlier fixed recipe: ten 100-ms
cue bins over [0,1) s, dimension 7, hidden 32, learning rate 0.0003, temperature 1,
1,000 updates, Time batch 256, and the native per-session batch rule. Its conclusion
is conditional on that recipe. A separate convergence study does not silently
replace these settings after inspecting selection-arm results.

Propose five source-label diagnostic worlds for each of the four nonrandom
budget×selection configurations, using the first declared repeat tuple:
**20 diagnostic cases**. Each world's label map and development plan are shared
canonically across the compared arms.
Permute each session×split map once on the union before b-subsetting, then reuse
that map everywhere the session occurs.
Permute complete source labels within the declared session/split strata with class
counts preserved; rerun label-dependent source selection, assembly and all fitted
stages. Keep the field-derived roster fixed: these are alignment diagnostics
conditional on a selected population, not a permutation test of the whole
field-selection procedure. Five worlds do not supply a calibrated significance test.

Under the previous 51-fits/case accounting, 50 total cases would mean 2,550 fit
calls excluding scalers: 50 PCA, 50 Time, 50 native ensemble fits and 600 of each
readout family; 100,000 encoder updates at 1,000 per branch/case. Native ensemble
member counts total 25 × (S_small + S_large) if all 50 cases remain. These are **conditional
planning totals**, not a run approval or measured resource estimate. Independent
review and a representative resource benchmark must set final limits before fitting.
Optional model-sensitivity and temporal-readout studies below have separate fit
budgets and are excluded from this total. Required descriptive analyses use the
main study's saved outputs.

## C. Model knobs on a fixed population

Start with duration sensitivity, then select at most one additional small study.
Every sweep holds the population, source IDs, assembly and evaluation contract fixed.

| Knob | Current value | Proposed sensitivity | Interpretation and constraint |
| --- | --- | --- | --- |
| Training duration | 1,000 updates | Checkpoints at 1,000 / 3,000 / 10,000 | Continue a single seeded training path and save checkpoints. Each checkpoint still needs separately fitted readouts. Loss alone does not establish useful learning. |
| Temperature | 1, fixed | 0.1/0.3/1 | Changes contrastive similarity weighting. Evaluate readouts and stability; do not pick the prettiest embedding. Keep learning rate fixed for this sensitivity and preserve unstable/failed settings. |
| Latent dimension | 7 | 3/7/16 | Check training-only PCA rank/width across every included case/control first. Skip infeasible dimensions openly. Raw input width is a different knob. |
| Time-positive separation | Adjacent 100-ms bins | 1 / 2 / 4 bins = 100 / 200 / 400 ms | Time branch only. Use common reference anchors 0–5 for these three arms so reference-time support is matched; positives stay in the same row/phase. This is a new matched-lag design, not the historical lag 1 construction. |
| SVM regularization | Base C=1 with row-count adjustment | Base multiplier 0.1 / 1 / 10 | Keep gamma=scale and the existing N×C adjustment within a fixed K. This changes readout fitting only. |
| Learning rate / hidden width / batch | 0.0003 / 32 / current rule | Hold fixed initially | A later optimization study can vary them. A larger batch changes negative sampling and optimizer exposure, not the number of measured trials. |

Checkpointing must preserve optimizer, sampler/RNG and training-mode state. Save
checkpoints along one fresh 10,000-update path and fit/evaluate readouts from copies
afterwards so evaluation cannot perturb later training. Count 10,000 updates per
path, not 1,000 + 3,000 + 10,000; budget each checkpoint's readouts separately.
For lag sensitivity, keep the negative-bin distribution fixed and report realized
reference/positive exposure. Positive-time marginals still shift with lag, so this
is a sensitivity with matched reference anchors. If a dimension fails the declared
training-rank requirement in any arm/control, omit it from the whole matched family,
not only the failing case.

The [official CEBRA guide](https://cebra.ai/docs/usage.html) discusses temperature,
temporal separation, dimension and convergence, and suggests longer training than
1,000 updates as a general starting point. That motivates a duration check; it does
not prove that the previous run was undertrained or that 10,000 is optimal here.
These numerical grids are our proposed sensitivities, not prescribed optimal values.

Native multisession in the completed study is **pair-supervised**, while the Time
encoder uses temporal positives. Retain that configured comparator in the coverage
study, but do not attribute its difference from Time solely to multisession training.
For a separate native-method comparison, add a **concatenated pair-supervised CEBRA
control** with matching label access, decoder and latent budget. Declare native
aggregation and total reference draws. Mean pooling remains part of the intervention;
matching supervision does not isolate every architectural difference. The
[native multisession tutorial](https://cebra.ai/docs/demo_notebooks/Demo_hippocampus_multisession.html)
provides the API context, not a validation of our pseudopopulation assay.

Do not vary pooling in the first run. Concatenating session embeddings instead of
averaging them changes downstream feature dimension and needs its own capacity control.
Time-lag changes are not an active knob for the existing discrete pair-supervised
native objective.

## D. Required analyses

| Analysis | What it answers |
| --- | --- |
| Availability/coverage frontier | What columns, sessions, spatial regions and distinct sources survive each constraint? Include infeasible/unknown cases and no-reuse capacity. |
| Retained/lost/gained coverage maps beside errors | Do verified coverage changes accompany errors at the true/predicted locations? Include gained coverage when rosters replace sessions. Show absolute and prespecified normalized coverage, occupancy and missing maps; unknown coverage is not measured absence. |
| Train/development confusions and class recall | Which conditions are learned in training but fail on development? Show counts and row-normalized values for every declared case/head. |
| Matched prediction switches | Which common rows change right→wrong or wrong→right across selection/source arms? Verify full shared-source lineage before pairing. |
| Source support/reuse versus error | Are errors associated with sparse pools? Keep eligibility, used sources, repeated draws and optimizer exposure distinct; do not treat repeated rows as independent observations. |
| Learning and checkpoint curves | Do readout performance and train–development gaps change with optimization, beyond changes in training loss? Keep seeds separate. |
| Cue-time trajectories and representation checks | Display condition-averaged embeddings over cue bins using train-fitted projections. They are derived cue trajectories, not observed navigation paths or simultaneous neural dynamics. |
| Within-cue temporal generalization, optional separate readout study | Train a readout at each bin and freeze it across all test bins, including its preprocessing. Contrast diagonal performance with off-diagonal transfer; current whole-cue readouts cannot simply be reused for this. |

For the optional 10×10 temporal-generalization matrix, each train-bin row uses one
fitted readout evaluated at 10 times; do not fit 100 readouts per matrix. Use a fixed
frozen pointwise representation and training-only readout preprocessing, with the
same source partitions. This tests readout reuse within the cue, not cross-phase
transfer or a causal online state estimate. Account for the extra readout fits.

## E. Evaluation, implementation and unresolved choices

Use training-only selection/preprocessing. Genuine hyperparameter selection needs
source-safe inner validation; confirm that sparse pools support it before promising
nested cross-validation. If they do not, report predeclared sensitivities on exposed
development as exploratory and defer confirmation to new data. Preserve the original
outer partition and global contributor embargo; do not unlock an old protected test
or redraw folds to make a convenient grid.
For inner validation, training-derived map selection and learned preprocessing
must be estimated inside each inner-training fold; independent localizer information
can remain fixed only if its independence from that validation fold is verified.

There is no new biological holdout available for this study. Keep its conclusions
exploratory and report computational seed/roster variation
without presenting it as a biological confidence interval. Condition-matched
assembly remains label-conditioned even with new sources; natural-trial inference
requires a different input/evaluation design. Report all contrasts and negative
results. Do not select classes, regions or thresholds from evaluation mistakes.

Implementation remains an experiment-scoped change under the existing study
organization, with dedicated config, scripts, notebook and report. Current code
does not expose every proposed knob: Time temperature is fixed in
[`cebra_solver.py`](../../../src/neuro/cebra_solver.py), positive pairs are built in
[`cebra.py`](../../../src/neuro/cebra.py), and native temperature/hidden width/learning
rate/batch plus SVM settings are fixed in
[`population_models.py`](../../../src/neuro/studies/population_models.py).
Changing a config file alone would not vary them. Any later implementation must
verify parameter consumption and preserve existing defaults and historical artifacts.
The unrelated local sampling edit must not be silently absorbed into a new study.

Before freezing execution, resolve: available authenticated maps and permitted
source trials; spatial regions and quality metric/cutoff; exact K,
matching budgets/rosters and common b; feasibility of inner validation; optional
model/temporal studies and their separate fit/resource budgets. No analysis code,
new model run, data transfer, publication or merge has been performed while defining
this draft. Fresh fits are the intended next execution, after these design and
scientific/resource preflight details are settled.

An independent read-only scientific design review accepted the conditional count
arithmetic and exploratory scope, and prompted the canonical-plan, repeat,
checkpoint and nonnested-roster clarifications above. This is review of a draft,
not a completed code/data/resource preflight or an executed scientific result.
