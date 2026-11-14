# Confusions, deleted classes and source reuse — November11 follow-up

**Post-hoc exploratory saved-result analysis. No new model fitting or model replay.**
The owner requested confusion matrices inside the handoff and an examination of
whether removed classes/sessions or heavily reused sources correspond to mistakes.
The analysis uses the completed111-case study and preserves the original evidence.

Deleted classes were **not consistently the hardest classes**. Higher training
source reuse often accompanies more errors, particularly for raw/PCA/Time with
SVM in the20- and15-class tasks, but reuse and available source coverage cannot be
separated in this design. Removing session groups helps some fitted pipelines and
hurts others. The full handoff shows the actual classes and prediction switches
behind those statements, including exceptions.

## Read and interact

- [Updated handoff: confusion explorer and full report](../../../outputs/population-grid-20261111/handoff-errors-01/report.html#error-explorer).
- [Updated executed notebook with added saved-result figures](../../../outputs/population-grid-20261111/handoff-errors-01/population_grid.executed.ipynb).
- [Per-class performance/support](../../../outputs/population-grid-20261111/handoff-errors-01/error-tables/class_performance.csv),
  [class-removal details](../../../outputs/population-grid-20261111/handoff-errors-01/error-tables/class_deletion_details.csv),
  [correlations](../../../outputs/population-grid-20261111/handoff-errors-01/error-tables/support_error_correlations.csv)
  and [paired prediction changes](../../../outputs/population-grid-20261111/handoff-errors-01/error-tables/paired_prediction_changes.csv).
- [Declared calculation plan](error-analysis-plan.md), [validation and artifact identities](error-analysis-validation.md),
  and [original study interpretation](README.md).

Select the class requirement, roster, sampling policy, encoder, decoder, seed and
prediction head. The detailed confusion matrix supports counts and row-normalized
percentages; rows are true labels and columns are predicted labels. A nine-panel
overview opens any of the nine population configurations. Training/development
matrices are separate. Endpoint heads were independently fitted; they are not
obtained by collapsing the pair matrix. Hover a cell for exact counts or export
the selected matrix as CSV.

The explorer contains9,216 matrices:5,328 original development matrices
(including existing controls) and3,888 observed training matrices recomputed from
saved predictions. Only full-roster U2/F16 have the five diagnostic control worlds.
Unfitted combinations are labelled **not fitted**; fitted controls' training
matrices are labelled **not included in this view**. Neither is displayed as a
zero matrix. Seeds
remain separate; the small static SVM comparison sheets use observed seed0, while
older notebook figures and all numerical records remain intact.

## Were deleted classes already harder?

For30→20,30→15 and20→15, compare the later-retained and later-deleted classes **in
the source task before deletion**. Their class lists were chosen using metadata
availability, not error scores. A removed class has no prediction or accuracy in
the reduced task; it is not a zero-recall class there.

The table uses full rosters, F16 and SVM. Each number is macro recall over the
specified class group, averaged across computational seeds0/1/2. Both source
columns refer to the same larger-task fit. The destination column is a separate
smaller-task fit with changed population and construction, so the difference is
not a paired causal deletion effect.

| Class change | Features | Source: retained recall | Source: deleted recall | Destination: retained recall |
| --- | --- | --- | --- | --- |
| 30→20 | Raw | 11.88% | 29.58% | 37.71% |
| 30→20 | PCA7 | 10.00% | 10.83% | 70.42% |
| 30→20 | CEBRA-Time7 | 24.17% | 12.50% | 45.62% |
| 30→20 | Native multisession7 | 7.71% | 11.25% | 20.42% |
| 30→15 | Raw | 13.06% | 22.50% | 51.11% |
| 30→15 | PCA7 | 11.94% | 8.61% | 81.11% |
| 30→15 | CEBRA-Time7 | 21.11% | 19.44% | 45.00% |
| 30→15 | Native multisession7 | 8.06% | 9.72% | 17.22% |
| 20→15 | Raw | 43.89% | 19.17% | 51.11% |
| 20→15 | PCA7 | 74.44% | 58.33% | 81.11% |
| 20→15 | CEBRA-Time7 | 46.94% | 41.67% | 45.00% |
| 20→15 | Native multisession7 | 20.00% | 21.67% | 17.22% |

For30→20, the removed classes are easier for raw/SVM (29.58% versus11.88%),
harder for Time/SVM (12.50% versus24.17%), and similar for PCA/SVM. For20→15,
PCA's removed classes have lower source-task recall (58.33% versus74.44%).
Yet some Time/native contrasts change direction across seeds. There is no
pipeline-independent group of classes that can simply be called the bad classes.

The exact initial30-class outcomes below show this directly. Values are **K30,
full roster, F16, SVM development recall percentages**, means across three seeds.
The selection columns indicate future membership only; every listed class was
evaluated in this30-class fit. All six starts/goals remain represented in each task.

| Pair | Kept in20? | Kept in15? | Raw | PCA | CEBRA-Time | Native |
| --- | --- | --- | --- | --- | --- | --- |
| 1→2 | Yes | Yes | 12.50 | 4.17 | 12.50 | 4.17 |
| 1→3 | Deleted | Deleted | 0.00 | 0.00 | 0.00 | 0.00 |
| 1→4 | Yes | Yes | 54.17 | 45.83 | 62.50 | 8.33 |
| 1→5 | Deleted | Deleted | 58.33 | 0.00 | 0.00 | 4.17 |
| 1→6 | Yes | Yes | 0.00 | 0.00 | 0.00 | 0.00 |
| 2→1 | Yes | Yes | 45.83 | 0.00 | 16.67 | 8.33 |
| 2→3 | Yes | Yes | 0.00 | 8.33 | 4.17 | 0.00 |
| 2→4 | Yes | Deleted | 0.00 | 0.00 | 33.33 | 4.17 |
| 2→5 | Yes | Deleted | 0.00 | 16.67 | 37.50 | 0.00 |
| 2→6 | Deleted | Deleted | 0.00 | 0.00 | 12.50 | 0.00 |
| 3→1 | Yes | Yes | 0.00 | 33.33 | 37.50 | 0.00 |
| 3→2 | Deleted | Deleted | 0.00 | 20.83 | 0.00 | 29.17 |
| 3→4 | Yes | Yes | 0.00 | 0.00 | 58.33 | 12.50 |
| 3→5 | Yes | Yes | 0.00 | 0.00 | 8.33 | 12.50 |
| 3→6 | Deleted | Deleted | 100.00 | 8.33 | 29.17 | 16.67 |
| 4→1 | Deleted | Deleted | 87.50 | 29.17 | 66.67 | 8.33 |
| 4→2 | Yes | Yes | 0.00 | 0.00 | 0.00 | 0.00 |
| 4→3 | Yes | Deleted | 0.00 | 0.00 | 4.17 | 0.00 |
| 4→5 | Deleted | Deleted | 0.00 | 4.17 | 4.17 | 4.17 |
| 4→6 | Yes | Yes | 4.17 | 0.00 | 12.50 | 45.83 |
| 5→1 | Yes | Deleted | 0.00 | 4.17 | 20.83 | 0.00 |
| 5→2 | Deleted | Deleted | 0.00 | 12.50 | 12.50 | 0.00 |
| 5→3 | Yes | Yes | 70.83 | 0.00 | 29.17 | 4.17 |
| 5→4 | Yes | Yes | 8.33 | 33.33 | 41.67 | 0.00 |
| 5→6 | Yes | Deleted | 41.67 | 0.00 | 70.83 | 29.17 |
| 6→1 | Deleted | Deleted | 0.00 | 0.00 | 0.00 | 29.17 |
| 6→2 | Yes | Yes | 0.00 | 0.00 | 0.00 | 8.33 |
| 6→3 | Yes | Yes | 0.00 | 50.00 | 29.17 | 16.67 |
| 6→4 | Deleted | Deleted | 50.00 | 33.33 | 0.00 | 20.83 |
| 6→5 | Yes | Yes | 0.00 | 4.17 | 4.17 | 0.00 |

The explorer also counts errors on retained source-task classes that point into a
subsequently deleted label. For30→20 Time/SVM, their fraction averages39.67% of
errors across the three seeds. Those errors cannot be assumed to become correct
merely by removing that label: the new model, competitors, sessions, source
subsets and development construction also change. No synthetic row IDs are paired
across different K values.

## Did heavily reused classes get predicted correctly?

Every class gets the same constructed-row quota within a policy:2 for U2,16 for
R16/F16. Thus there are no classes given a larger row quota than their neighbors.
What differs is reuse of the underlying session×trial sources. We measure
`extra draws / all block draws = (draws-used_sources)/draws`, separately for
training and development. This is neither class frequency nor effective sample size.

The following complete15-class example uses the full39-session/138-column roster
and SVM. Available sources are distinct session×current-trial sources summed across
sessions, not complete simultaneous trials. F16 makes624block draws per pair
(16rows×39sessions). All recall columns are three-seed means in percent. U2/R16
share selected sources within each seed; F16 adds measured coverage and changes
weights/combinations at the same16-row quota as R16.

| Pair | Available train sources | F16 extra draws | Time U2 | Time R16 | Time F16 | Time F16 training | PCA F16 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1→2 | 180 | 71.15% | 16.67 | 33.33 | 41.67 | 93.75 | 83.33 |
| 1→4 | 197 | 68.43% | 16.67 | 75.00 | 83.33 | 100.00 | 83.33 |
| 1→6 | 169 | 72.92% | 16.67 | 33.33 | 4.17 | 100.00 | 54.17 |
| 2→1 | 175 | 71.96% | 4.17 | 4.17 | 4.17 | 100.00 | 0.00 |
| 2→3 | 193 | 69.07% | 8.33 | 33.33 | 50.00 | 91.67 | 83.33 |
| 3→1 | 192 | 69.23% | 45.83 | 33.33 | 29.17 | 97.92 | 100.00 |
| 3→4 | 187 | 70.03% | 16.67 | 20.83 | 54.17 | 97.92 | 62.50 |
| 3→5 | 179 | 71.31% | 16.67 | 37.50 | 20.83 | 97.92 | 95.83 |
| 4→2 | 176 | 71.79% | 33.33 | 20.83 | 29.17 | 100.00 | 58.33 |
| 4→6 | 194 | 68.91% | 29.17 | 75.00 | 58.33 | 95.83 | 100.00 |
| 5→3 | 197 | 68.43% | 8.33 | 37.50 | 58.33 | 95.83 | 100.00 |
| 5→4 | 196 | 68.59% | 29.17 | 58.33 | 66.67 | 85.42 | 100.00 |
| 6→2 | 188 | 69.87% | 45.83 | 16.67 | 54.17 | 100.00 | 95.83 |
| 6→3 | 174 | 72.12% | 12.50 | 79.17 | 45.83 | 100.00 | 100.00 |
| 6→5 | 188 | 69.87% | 12.50 | 37.50 | 75.00 | 95.83 | 100.00 |

Examples illustrate why a single average score is insufficient. For1→6, Time/SVM
changes from33.33% under R16 to4.17% under F16 despite broader source coverage;
its F16 training recall is100%. For1→4, Time improves from16.67% under U2 to75%
under R16 and83.33% under F16. Pair2→1 remains at4.17% for Time under all three
policies, and PCA/F16 is0%. These examples are descriptive, not grounds to drop
classes based on the same development data. The full tables and explorer expose
every class, roster, decoder and seed, not only these examples.

## What the correlations say

Below are Spearman rank associations between training-source reuse and development
error **across pair classes within each F16/full-roster/SVM fit**. Positiveρ means
more reuse accompanies more error. Each seed supplies K class observations; seeds
are not pooled as independent trials. Tied support values receive average ranks,
with harmonic support computed exactly before ranking. No p-values or biological
confidence intervals are reported.

| Classes | Features | Seed0ρ | Seed1ρ | Seed2ρ |
| --- | --- | --- | --- | --- |
| 30 | Raw | 0.447 | 0.455 | 0.380 |
| 30 | PCA7 | 0.103 | 0.049 | -0.070 |
| 30 | CEBRA-Time7 | 0.090 | 0.457 | 0.055 |
| 30 | Native multisession7 | 0.304 | -0.146 | 0.312 |
| 20 | Raw | 0.401 | 0.373 | 0.354 |
| 20 | PCA7 | 0.672 | 0.653 | 0.517 |
| 20 | CEBRA-Time7 | 0.404 | 0.307 | 0.346 |
| 20 | Native multisession7 | 0.246 | -0.069 | 0.200 |
| 15 | Raw | 0.526 | 0.562 | 0.618 |
| 15 | PCA7 | 0.489 | 0.343 | 0.470 |
| 15 | CEBRA-Time7 | 0.605 | 0.379 | 0.578 |
| 15 | Native multisession7 | 0.246 | 0.152 | 0.413 |

The association is consistently positive here for raw at all three K, for PCA and
Time at K20/15, and for native at K15. It is weak or changes sign in some other
comparisons, particularly PCA/native at K30. Thus higher reuse/lower coverage often
accompanies more error, but this is not universal.

Crucially, in F16 all available training sources are used, so at fixed roster:

`reuse = 1 − available_training_sources / (16 × sessions)`.

Consequently, the total-support correlation is exactly the negative of the reuse
correlation. These are **one association**, not independent evidence that separates
harmful reuse from limited coverage. U2 reuse is always0 and R16 always0.875
across classes; their reuse/error correlations are **undefined**, not zero.
Development reuse also varies and is exposed in the explorer; for K15 raw/SVM it
correlates with error atρ=.714/.711/.764 across the three seeds. Class identity,
recording quality, endpoint confounds and evaluation composition are not controlled
by these descriptive correlations.

## Which predictions changed when sampling or sessions changed?

The handoff reports wrong→right, right→wrong, both-right and both-wrong counts for
each pair class. The counts partition the same eight development rows/class.
Policy comparisons are U2→R16, R16→F16 and U2→F16. Roster removals are
S100→S67, S100→S33 and S67→S33. Every pairing checks complete source lineage,
not merely equal synthetic row IDs: exact common rows across policies, and exact
shared-block projections across rosters. Only fixed-K observed comparisons are
paired. These dependent constructed rows are not independent biological samples.

For example, with F16/SVM, removing sessions from S100 to S33 changes mean pair
balanced accuracy by −34.79percentage points for K20/PCA and−30.56 for K15/PCA.
The same K15 session cut increases Time by7.78points and native by9.72points.
These directions are consistent across all three computational seeds for those
four named comparisons. The effect concerns the entire removed session group,
changed feature width and a separately refitted pipeline. It does not identify
an individually bad session.

The session table names retained/removed aliases and the original support/rank
exclusion reasons. Every evaluated pseudorow contains every retained session;
therefore simply counting participation in wrong rows would give all retained
sessions the same overall case-level error rate. Excluded sessions have no
standalone evaluated score. The study cannot say a removed session's trials were
wrong merely because removing that group improved a model.

## Evidence and interpretation limits

The corrected calculation authenticated169inputs, recomputed7,776observed
train/development matrices from15,552saved truth/prediction array members, and
reconciled28,080class records,6,480correlations,1,296class-deletion summaries,
34,560class-deletion details and56,160paired-change records over162verified
lineage comparisons. Independent numerical/scientific review passed. Original
control matrices were authenticated; no new control fits or training-null
confusions were invented.

This is a further descriptive view of the same exposed, known-label-assembled
recordings, not new biological evidence or a pristine test. It supports examining
class difficulty, coverage and model sensitivity; it does not establish that
upsampling causes errors, that removed classes/sessions were biologically
uninformative, or that these scores predict an unknown natural trial. All original
run files and earlier interpreted artifacts are retained unchanged. The added
notebook section is labelled post-execution and preserves all prior code cells.
