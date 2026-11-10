# Class requirements, session rosters and learning — November 11, 2026

**Completed exploratory analysis: 111 cases, 5,661 fitted-model calls and 222,000 optimizer updates.**
This is a new exploratory study on existing recordings, replacing the previous
nine-pair rectangle experiment. The nine configurations now mean **three class
requirements × three session rosters**. No previous model states or numerical
results were used as evidence for this run.

The trained pipelines recover endpoint information even when each selected current
source is used only once in training assembly: for raw, PCA and CEBRA-Time with
SVM, every observed seed exceeds all five source-label controls for pair, start
and goal in each full-roster task. Repeated training blocks are therefore not
necessary for this conditional association. This does **not** validate all
pseudopopulation uses or establish independent natural-trial prediction.

Dropping class requirements makes many more columns available, but every selected
population still has a two-source training bottleneck. Wider rosters and repeated
rows do not improve all models. With full source coverage, full-roster PCA/SVM
reaches 70.4% and 81.1% pair balanced accuracy for 20 and 15 classes; on the
30-class task, CEBRA-Time/SVM reaches 20.3% versus PCA/SVM's 10.3%. These are
separate tasks, not a common leaderboard. Native multisession CEBRA was genuinely
trained, but its specified pooled readout is generally weaker and has mixed
control separation. All decoder and seed results, including failures to improve,
are retained below and in the notebook.

## Read the completed evidence

- [Standalone report, including every figure and numerical result](../../../outputs/population-grid-20261111/deliverables/report.html).
- [Executed evidence notebook](../../../outputs/population-grid-20261111/deliverables/population_grid.executed.ipynb).
- [All case-level metrics](../../../outputs/population-grid-20261111/deliverables/tables/metrics.csv),
  [seed summaries](../../../outputs/population-grid-20261111/deliverables/tables/summary.csv)
  and [paired contrasts](../../../outputs/population-grid-20261111/deliverables/tables/paired_contrasts.csv).
- [Source notebook](../../../notebooks/06_population_grid.ipynb),
  [prospective protocol](../../population-grid-protocol-20261111.md),
  [frozen metadata design](../../population-grid-design-20261111.json)
  and [independent validation](validation.md).

The executed notebook is the evidence artifact: read its saved outputs without
rerunning training. Its added interpretation cell is labelled as post-execution;
all original executed cells and outputs are preserved. Large figures, numeric
records, model states and predictions remain local and ignored by Git.

## What the nine configurations change

The class requirements are 30, 20 or 15 ordered start→goal pairs, with all six
starts and all six goals retained. For each class count, exact metadata optimization
maximizes eligible recorded columns, then total training sources among width ties,
then breaks remaining ties lexicographically. Each retained session must have at
least two training and one development current source for every retained pair.
Endpoint-degree constraints prevent removing whole starts or goals simply to
make the task easier.

Eligible sessions are ranked by harmonic mean training support, then columns,
training-source total and session ID. The first third, first two-thirds and full
roster give three nested populations per class task. Smaller rosters are exact
column/block projections of the largest assembly. This optimizes width under the
declared constraints; it does not jointly optimize accuracy and the worst source
pool, or establish that these are the best possible rosters under another rule.

| K | Roster | Sessions | Columns | Eligible train | U2/R16 used | Development sources | Balanced no-reuse rows | Classwise no-reuse rows | Dev singleton pools |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 30 | S33 | 4 | 8 | 592 | 240 | 219 | 60 | 95 | 40/120 |
| 30 | S67 | 7 | 19 | 1009 | 420 | 387 | 60 | 86 | 70/210 |
| 30 | S100 | 10 | 27 | 1415 | 600 | 551 | 60 | 72 | 103/300 |
| 20 | S33 | 10 | 38 | 1009 | 400 | 383 | 40 | 54 | 59/200 |
| 20 | S67 | 19 | 73 | 1837 | 760 | 735 | 40 | 45 | 116/380 |
| 20 | S100 | 28 | 103 | 2620 | 1120 | 1066 | 40 | 41 | 174/560 |
| 15 | S33 | 13 | 52 | 998 | 390 | 366 | 30 | 41 | 64/195 |
| 15 | S67 | 26 | 93 | 1915 | 780 | 746 | 30 | 32 | 123/390 |
| 15 | S100 | 39 | 138 | 2785 | 1170 | 1122 | 30 | 31 | 184/585 |

Here K is the number of retained pair classes. S33/S67/S100 mean the first
ceiling(S/3), ceiling(2S/3) and all eligible sessions, respectively. Counts refer
to distinct session×current-trial sources, not bins. “Classwise no-reuse rows”
sums the smallest session pool separately for each class; unlike the balanced
capacity, it permits unequal rows per class and is descriptive only. The last
column counts development session×pair pools with just one available source.
The roster rank is support-based; only the full eligible roster attains the
metadata optimizer's maximum width. Smaller rosters are not separately optimized
for maximum width under a fixed session budget.

![Nine population configurations and their source support](../../../outputs/population-grid-20261111/real-01/report/images/nine_configurations.png)

*Measured availability, before neural-score selection: recorded columns, retained
sessions and distinct current trials after the global contributor embargo. Complete
balanced no-reuse rows equal class count times the smallest training pool. These
are counts, with no statistical uncertainty interval. The exact class lists and
rosters are in the frozen design; the full report also plots every ranked roster
prefix and the metadata-only class-count frontier from 6 to 30.*

All nine populations still have a smallest training pool of two. Their balanced
complete-row capacities without repeated training blocks are therefore 60, 40
and 30 for the respective class tasks. For the full eligible rosters, dropping
class requirements increases available columns and total measured trials, but
does not automatically increase that bottleneck. This finding applies to the declared nine choices, not every
possible class list or stricter support threshold.

**Population width and latent dimension are different.** The input width varies
from 8 to 138 recorded columns. PCA and both CEBRA branches always produce seven
coordinates per 100-ms bin, so their whole-cue readouts have 70 features; raw
readouts have ten times the recorded-column count. Seven dimensions were frozen
before biological fitting after the broader preflight found rank seven in an
unfitted small-roster null. It is an engineering choice, not a biological dimension
estimate or evidence that a scheduled eight-dimensional fit was impossible.

## Measured sources versus constructed training rows

| Policy | Sources per session × pair | Rows per pair | Interpretation |
| --- | --- | ---: | --- |
| U2 | Exactly two selected current sources | 2 | Each selected current source used once during training assembly |
| R16 | The identical two sources as U2 | 16 | Eight uses per source; more combinations and multiplicity, no new measurements |
| F16 | Every eligible source | 16 | More distinct coverage at the same row quota, with changed weighting and combinations |

All three training policies balance source use: U2 samples without replacement,
and R16/F16 use balanced cycles. Each draw copies a complete session×trial
unit-by-time block. They do not independently resample individual
neurons or time bins. This study tests that balanced construction, not every
historical random-replacement sampler.

U2 removes repeated current blocks during assembly, not repeated optimizer access.
Both CEBRA branches still take 1,000 updates in every case. R16−U2 therefore tests
recombination/multiplicity on the same measurements. F16−R16 adds distinct source
coverage while also changing empirical weights and joint combinations; it is not
a pure count-only intervention. Adding sessions changes columns and source
composition together, so it is a roster comparison rather than an isolated
neuron-count effect.

Development draws with replacement to construct eight rows per pair. Its sources
are separated from
training by the frozen source/predecessor embargo, but are themselves reused,
including singleton pools. The development construction is identical across
policies and observed seeds within each class/roster, with exact projections
between rosters. It is historically exposed and assembled using known labels.

Actual full-roster usage is below. Source/draw counts are constant across observed
seeds; the chosen U2/R16 identities can change. A block draw copies every retained
column and all ten bins of one session×current-trial source.

| Classes | U2 sources / draws | R16 sources / draws | F16 sources / draws | Development used / eligible | Development draws |
| --- | --- | --- | --- | --- | --- |
| 30 | 600 / 600 | 600 / 4,800 | 1,415 / 4,800 | 544 / 551 | 2,400 |
| 20 | 1,120 / 1,120 | 1,120 / 8,960 | 2,620 / 8,960 | 1,050 / 1,066 | 4,480 |
| 15 | 1,170 / 1,170 | 1,170 / 9,360 | 2,785 / 9,360 | 1,104 / 1,122 | 4,680 |

The fraction of draws beyond each source's first appearance is 0% for U2 and
87.5% for R16. For F16 it is 70.52%, 70.76% and 70.25% at K=30/20/15.
Development fractions are 77.33%, 76.56% and 76.41%; 7, 16 and 18 eligible
sources, respectively, remain unused because fixed replacement draws can miss
eligible sources even when a pool is smaller than eight.
These fractions describe reuse, not effective sample size. No evaluation error
rate is assigned to an unused source.

## What changed in model performance

Every case fitted raw, PCA7, CEBRA-Time7 and native multisession CEBRA7 pipelines,
each with logistic, scaled RBF-SVM, kNN5 and SVD-LDA readouts for pair, start and goal.
All learned scaling, projections, encoders and readouts used training only.
SVM follows the historical scaled RBF family, with regularization adjusted for
row count. SVM margins remain margins: probability loss is intentionally absent.

The table gives **full-roster SVM pair balanced accuracy**, mean and minimum–maximum
across seeds 0/1/2, in percent. Balanced accuracy averages class recall. Uniform
references are 3.33%, 5% and 6.67% for K=30/20/15. Ranges describe computational
variation on the same development construction, not confidence intervals.

| Classes | Features | U2 | R16 | F16 |
| --- | --- | --- | --- | --- |
| 30 | Raw | 15.83 (14.17–18.33) | 12.78 (10.00–14.58) | 17.78 (17.08–19.17) |
| 30 | PCA7 | 15.42 (10.00–21.25) | 14.03 (10.00–17.50) | 10.28 (7.50–12.50) |
| 30 | CEBRA-Time7 | 11.81 (7.50–15.00) | 13.47 (11.67–16.25) | 20.28 (17.08–24.17) |
| 30 | Native multisession7 | 8.89 (3.33–14.17) | 7.50 (5.42–10.42) | 8.89 (3.75–15.83) |
| 20 | Raw | 36.04 (28.12–46.25) | 18.54 (10.00–27.50) | 37.71 (36.88–38.75) |
| 20 | PCA7 | 46.25 (39.38–52.50) | 50.83 (43.12–56.88) | 70.42 (66.88–75.00) |
| 20 | CEBRA-Time7 | 24.38 (16.25–30.00) | 30.21 (28.12–32.50) | 45.62 (42.50–49.38) |
| 20 | Native multisession7 | 11.67 (5.62–20.00) | 13.33 (5.00–21.88) | 20.42 (14.37–31.87) |
| 15 | Raw | 48.33 (40.83–54.17) | 25.83 (15.00–33.33) | 51.11 (49.17–52.50) |
| 15 | PCA7 | 55.00 (40.00–72.50) | 61.94 (55.83–69.17) | 81.11 (78.33–85.00) |
| 15 | CEBRA-Time7 | 20.83 (13.33–30.83) | 39.72 (35.00–46.67) | 45.00 (42.50–46.67) |
| 15 | Native multisession7 | 11.39 (5.83–14.17) | 15.56 (11.67–19.17) | 17.22 (12.50–20.83) |

More rows from the same sources are not reliably better. R16−U2 lowers raw/SVM
by 3.06, 17.50 and 22.50 percentage points for K=30/20/15, while raising
CEBRA-Time/SVM by 1.67, 5.83 and 18.89 points. At equal 16-row quotas,
F16−R16 raises Time/SVM by 6.81, 15.42 and 5.28 points. PCA/SVM improves by
19.58 and 19.17 points for K=20/15 but falls 3.75 points for K=30. Those
contrasts do not isolate distinct-source count from weighting and combinations.

Wider rosters also have different effects within a fixed task. Under F16,
PCA/SVM at K=20 rises 35.62% → 63.96% → 70.42% over S33/S67/S100; at K=15,
50.56% → 73.06% → 81.11%. But K=30 falls 19.03% → 15.42% → 10.28%.
At K=15, Time/SVM falls from 52.78% at S33 to 45.00% at S100, and native/SVM
from 26.94% to 17.22%. Adding columns is not a universal improvement rule.

For the other decoders, the next table gives **F16 full-roster means** on exactly
the same pair tasks. The report's numerical appendix preserves all three policies,
individual seeds, all rosters and all three prediction heads.

| Classes | Features | Logistic | RBF-SVM | kNN5 | SVD-LDA |
| --- | --- | --- | --- | --- | --- |
| 30 | Raw | 16.25 | 17.78 | 6.53 | 11.81 |
| 30 | PCA7 | 8.61 | 10.28 | 7.64 | 10.28 |
| 30 | CEBRA-Time7 | 19.31 | 20.28 | 16.39 | 17.22 |
| 30 | Native multisession7 | 8.06 | 8.89 | 4.58 | 10.42 |
| 20 | Raw | 49.17 | 37.71 | 17.71 | 24.17 |
| 20 | PCA7 | 68.96 | 70.42 | 61.67 | 65.21 |
| 20 | CEBRA-Time7 | 45.63 | 45.62 | 41.67 | 46.88 |
| 20 | Native multisession7 | 18.75 | 20.42 | 15.83 | 19.38 |
| 15 | Raw | 62.50 | 51.11 | 32.22 | 41.11 |
| 15 | PCA7 | 82.50 | 81.11 | 77.78 | 80.83 |
| 15 | CEBRA-Time7 | 49.72 | 45.00 | 51.39 | 51.39 |
| 15 | Native multisession7 | 19.17 | 17.22 | 12.50 | 19.72 |

SVM is useful but is not the best readout everywhere: K=15 PCA/logistic is
82.50%, while its SVM is 81.11%; K=15 Time/kNN and Time/LDA each average
51.39%, while Time/SVM is 45.00%. No hyperparameters were selected using these
results. Logistic and SVM keep N×C constant within a task when the row quota
changes; kNN5 and SVD-LDA retain their fixed declared settings.

Accuracy and probability quality disagree. For K=15 F16 full-roster PCA,
logistic/kNN/LDA pair log losses are 1.512/3.001/2.478 nats versus uniform
2.708. At K=30, their values are 2.973/24.688/14.167 versus uniform 3.401.
kNN's zero votes receive a large clipped loss; U2 supplies only two examples
per pair, so its five-neighbor pair probability cannot exceed 0.4, which is
**not** an accuracy ceiling. SVM has no probability-loss score because it was
not probability-calibrated. High classification accuracy alone does not establish
well-calibrated confidence.

![All nine population configurations, three sampling policies and four feature pipelines with SVM](../../../outputs/population-grid-20261111/real-01/report/images/performance_svm_pair_balanced_accuracy.png)

*Whole-cue pair balanced accuracy, in percent, on the exposed source-separated
development construction. Each class task is shown separately; panels have individual vertical scales, so
compare tick values rather than line heights across panels. Lines are means
over computational seeds 0/1/2 and dots show every seed. U2/R16/F16 differ as
defined above; measured-source and synthetic-row counts are separate in the
availability and use tables. Uniform references are 1/K. The purple 6/K line is
the expected pair BA with perfect goal information and no start information,
not a fitted baseline or significance threshold. Native is pair-supervised and
mean-pooled; Time uses temporal positives on concatenated inputs. This figure
comes from the new run; its exact hash is in figure_provenance.json.*

Start and goal heads are fitted separately, not obtained by collapsing the pair
classifier's predictions. Their scores need not bound the independently fitted
pair classifier's score. The complete report retains every decoder, target and
seed, including unfavorable outcomes. The seeds vary source subsets, assembly
and model randomness where applicable; they reuse the fixed development data and
are not biological replicates or confidence intervals.

## Does learning survive once-only training assembly?

For raw, PCA and Time with SVM, the minimum observed U2 pair score exceeds the
maximum of the five label-permuted scores at every full-roster K. The same is
true for their separately fitted start and goal heads. Thus endpoint recovery
survives removing repeated current blocks from training assembly. The comparison
remains conditional on label-matched construction and the exposed development
sources; it is not evidence that synthetic rows are independent trials.

| K | Features | Policy | Observed seeds 0,1,2 | Null range | Every observed seed above null maximum |
| --- | --- | --- | --- | --- | --- |
| 30 | Raw | U2 | 15.00, 18.33, 14.17 | 1.67–5.42 | Yes |
| 30 | PCA7 | U2 | 10.00, 15.00, 21.25 | 1.25–7.08 | Yes |
| 30 | CEBRA-Time7 | U2 | 7.50, 15.00, 12.92 | 2.50–4.58 | Yes |
| 30 | Native multisession7 | U2 | 14.17, 3.33, 9.17 | 0.42–5.00 | No |
| 20 | Raw | U2 | 46.25, 28.12, 33.75 | 1.88–9.38 | Yes |
| 20 | PCA7 | U2 | 46.88, 52.50, 39.38 | 1.88–15.00 | Yes |
| 20 | CEBRA-Time7 | U2 | 26.88, 30.00, 16.25 | 3.12–10.62 | Yes |
| 20 | Native multisession7 | U2 | 5.62, 20.00, 9.38 | 1.25–11.88 | No |
| 15 | Raw | U2 | 40.83, 50.00, 54.17 | 1.67–17.50 | Yes |
| 15 | PCA7 | U2 | 72.50, 40.00, 52.50 | 2.50–6.67 | Yes |
| 15 | CEBRA-Time7 | U2 | 18.33, 13.33, 30.83 | 2.50–10.00 | Yes |
| 15 | Native multisession7 | U2 | 14.17, 14.17, 5.83 | 1.67–10.00 | No |
Native U2 is less consistent: pair and start ranges overlap controls at all
three class counts. Its goal head exceeds every control in every observed seed.
Native F16 pair scores separate from controls at K=20 and K=15, but still overlap
at K=30. These negative findings are part of the result.

The endpoint table shows observed mean (seed range), followed by the five-world
null range. Every number is percent balanced accuracy; the uniform reference
for either endpoint is 16.67%.

| K | Features | Start: observed mean (range) / null range | Goal: observed mean (range) / null range |
| --- | --- | --- | --- |
| 30 | Raw | 34.72 (30.83–40.83) / 12.92–18.75 | 46.39 (42.08–48.75) / 10.00–22.50 |
| 30 | PCA7 | 27.08 (21.25–35.00) / 14.58–20.42 | 52.92 (50.42–54.58) / 10.00–22.08 |
| 30 | CEBRA-Time7 | 30.00 (28.75–30.83) / 12.92–21.25 | 42.92 (35.00–54.58) / 13.75–25.42 |
| 30 | Native multisession7 | 22.92 (20.42–26.67) / 11.25–24.58 | 39.58 (34.17–43.33) / 12.50–20.83 |
| 20 | Raw | 25.52 (23.78–27.08) / 13.54–21.35 | 35.36 (30.73–40.97) / 7.81–22.92 |
| 20 | PCA7 | 56.13 (54.69–57.29) / 10.24–30.38 | 75.41 (73.61–76.39) / 14.76–25.69 |
| 20 | CEBRA-Time7 | 33.56 (28.82–38.89) / 15.28–23.78 | 56.13 (53.82–57.99) / 8.33–20.14 |
| 20 | Native multisession7 | 20.14 (11.63–24.83) / 7.99–27.95 | 37.09 (33.85–41.15) / 17.36–24.83 |
| 15 | Raw | 34.95 (31.94–39.58) / 9.03–25.69 | 44.33 (42.36–47.57) / 14.58–25.69 |
| 15 | PCA7 | 59.49 (47.22–65.97) / 15.62–20.83 | 74.88 (71.18–77.08) / 18.75–23.26 |
| 15 | CEBRA-Time7 | 31.13 (24.31–40.62) / 15.28–22.57 | 43.98 (37.85–51.04) / 13.19–19.79 |
| 15 | Native multisession7 | 17.01 (12.50–21.18) / 12.50–26.04 | 35.53 (33.33–39.58) / 14.58–22.92 |

![Five source-label control worlds for each full-roster U2 and F16 comparison with SVM](../../../outputs/population-grid-20261111/real-01/report/images/source_label_controls_svm.png)

*Pair BA percentages for the same full-roster tasks, representations and SVM
recipe: three observed computational seeds and all five joint pair-label
permutations, 60000–60004, with model seed 0. Permutation occurs within session ×
split before source selection and assembly; each world has a compatible fixed
development construction. Controls were run only for full-roster U2/F16 at each
K. Their range is diagnostic, not a biological confidence interval or p-value;
smaller-roster and R16 controls were not run.*

## What the learning curves and trajectories establish

Both encoder objectives decreased during training, including in permuted-label
worlds. The following first/last values average the first and last 100 updates,
then average three observed seeds or five null worlds for full-roster F16.
These are contrastive training losses, not classification log loss.

| K | Encoder | Observed first | Observed last | Null first | Null last |
| --- | --- | --- | --- | --- | --- |
| 30 | CEBRA-Time7 | 5.527 | 5.241 | 5.539 | 5.274 |
| 30 | Native multisession7 | 5.596 | 5.522 | 5.604 | 5.522 |
| 20 | CEBRA-Time7 | 5.450 | 4.914 | 5.490 | 5.030 |
| 20 | Native multisession7 | 5.607 | 5.531 | 5.607 | 5.531 |
| 15 | CEBRA-Time7 | 5.429 | 4.817 | 5.489 | 4.890 |
| 15 | Native multisession7 | 5.533 | 5.462 | 5.528 | 5.462 |
Training accuracy is also insufficient. At K=15/F16/full roster, native/SVM
has 100% training pair BA but 17.22% development BA; PCA/SVM has 100% versus
81.11%, and Time/SVM has 96.81% versus 45.00%. Each model can fit the constructed
training rows much more readily than it transfers to the exposed development
sources. Source-label controls and held-apart source IDs are therefore more
informative than a falling optimization curve alone.

Completing the fixed 1,000-update budget does not establish encoder convergence
or optimal hyperparameters. All 222 optimization curves retain every update from the 111 Time and 111 native
fits, including controls. Falling contrastive loss shows optimization under the
chosen positive/negative rule; it does not by itself show endpoint recovery.
Time and native use different sampling objectives and negative banks, so their
loss magnitudes are not a ranking of representation quality. No untrained/random
encoder control was included: successful readout from trained features does not
isolate the benefit of CEBRA optimization over a fixed feature map. The strongest
learning claim concerns the complete trained prediction pipeline.

Every observed case has PCA, Time and native class-mean cue trajectories. The
81 trajectory figures show ten bin centers from 50 to 950 ms, averaged over eight
constructed development rows per class, in the first three of seven coordinates.
Axes are not aligned across fits; these are not maze paths, simultaneous
trial-specific dynamics or evidence of manifold topology. The interactive
teach artifact rotates these saved coordinates without fitting an alignment.

Readouts in this study are whole-cue only. Single-bin decoding, a frozen
train-time × test-time transfer matrix, navigation decoding and unseen-session
transfer were not executed. A ten-point embedding trajectory is not a
time-resolved decoding result.

## What native multisession CEBRA adds—and what it does not isolate

This is the installed CEBRA 0.6.1 native list-input API, with a separate encoder
for each session and shared discrete pair-label sampling. It is not a renamed
concatenated pseudopopulation fit. Positive examples match the training pair in
randomly assigned sessions, without cue-bin matching; a positive can remain in
its own session. Transforming development uses neural values and session index,
never its labels.

Aligned seven-dimensional outputs are averaged equally across sessions at each
constructed row/bin, without learned pooling or renormalizing the mean. This
choice can discard session-specific information. The full pipeline changes
supervision, parameterization, pooling and exposure relative to Time, so a score
difference cannot isolate an advantage or disadvantage of multisession training.

U2 and R16 have exactly the same native per-session empirical point/label
distribution. Native encoder training does not consume their cross-session row
combinations; R16 supplies no new encoder information. Differences can arise
from finite stochastic/numerical training and the recombined downstream pooled
readout rows. Native uses a total reference budget no greater than 256/update:
64 per session with four sessions, but six with 39. Equal global budget is not
equal per-session exposure across rosters.

At full-roster F16, native/SVM pair BA is 8.89%, 20.42% and 17.22% for
K=30/20/15; Time/SVM is 20.28%, 45.62% and 45.00%. This configured native
comparator does not show a performance advantage. Pooling, objective, finite
training budget and per-session exposure remain plausible limitations; this
study cannot identify which one caused the difference or rule out a stronger
native multisession design.

## Source reuse, exclusions and prediction errors

The source-use tables preserve eligible/used counts, block appearances, balanced
multiplicities and complete-row/shared-block overlaps. Unit columns inherit the
usage profile of their entire session block. Zero exact duplicate complete rows
would not mean zero reuse of component measurements.

Study-level exclusions list all 58 sessions for every configuration, separating
insufficient retained-class support from the frozen roster-rank cut. Unit
inclusion tables cover all 195 recorded columns. Original experimental acquisition
and spike-sorting exclusions are not newly established by those tables.

Every prediction has an explicit assembly identity and source lineage. Error
participation records reconcile wrong + correct appearances with source use.
Each wrong constructed row involves every retained session; source participation
is descriptive, not causal blame for one trial, neuron or recording. Excluded
sessions and unused sources have no evaluated error rate. Sorting class recalls
alone also does not establish a source-support/error relationship.

As a concrete example, full-roster F16 Time/SVM has zero recall in all three
seeds for 8 of 30 pair classes, including 1→3, 1→5, 1→6 and 6→1; its largest
mean class recall is 70.83% for 5→6. At K=20, 2→1 and 6→3 have zero mean
recall, while 4→6 reaches 95.83%. At K=15, 1→6 and 2→1 each average 4.17%,
while 1→4 reaches 83.33%. The full class/error tables retain every class, seed
and decoder. These post-hoc differences motivate inspection; they do not justify
dropping classes on the same development scores or identify the causal source
of an error.

## What this resolves for the research-group issues

| Issue | Evidence supplied by this run | Remaining boundary |
| --- | --- | --- |
| [24: population/class/source sensitivity](https://github.com/Hong-yiii/neuro_science/issues/24) | Fresh metadata-selected class × session grid, availability frontiers and trained within-task comparisons | No causal single-neuron effect, universal minimum-source threshold or globally optimal accuracy policy |
| [25: reuse](https://github.com/Hong-yiii/neuro_science/issues/25) | Exact row/source lineage, source usage, shared blocks and U2/R16/F16 controls | Synthetic rows do not create independent biological replication |
| [26: exclusions/errors](https://github.com/Hong-yiii/neuro_science/issues/26) | Support/rank exclusion map, all confusions, class errors and reconciled source participation | Participation does not identify a causally bad session or unit |
| [23: native multisession](https://github.com/Hong-yiii/neuro_science/issues/23) | Newly trained native discrete multisession comparator and all four readouts | This is not natural-trial or unseen-session transfer; no matched concatenated pair-supervised control |

No GitHub issue was edited or closed. The previous experiment is retained as
history and is not pooled with these results.

## What to prioritize in additional recordings

Raise distinct trial support in the weakest session×pair pools, especially the
two-training/one-development bottlenecks, rather than only adding columns or
synthetic rows. Preserve a fresh evaluation partition before class selection,
tuning or inspecting model scores, and document which units were actually
recorded simultaneously. This study does not establish that any particular
minimum count, including two or five, is scientifically sufficient.

Keep raw/PCA and multiple readouts as baselines. A further native comparison
would need a matched supervision/pooling design before attributing a difference
to multisession training itself. These are proposed next steps; no additional
fits or automatic retries are queued.

## Completion, provenance and claim ceiling

All 81 observed cases and 30 diagnostic controls completed without biological
failures or retries. The run fitted 111 PCA states, 111 Time encoders and 111
native ensembles, plus 1,332 each of logistic, SVM, kNN and LDA readouts: 5,661
fit calls excluding scalers. The native ensembles contain 2,174 session-specific
networks. Both encoder branches used 1,000 updates/case, totaling 222,000.

The run took 7,054.95 seconds (117.58 minutes), peaking at 2,648.25 MiB under
a 4-GiB, no-swap, two-core, six-hour ceiling; all memory-event counters were zero.
The 12 notebook code cells completed sequentially without errors. The original
report contains 246 distinct figures: 29 overview, 28 loss-curve pages, 81 cue
trajectory pages and 108 pair-confusion pages. All 5,328 readout/target/case
confusions are retained numerically; the plotted pair-confusion pages use
observed seed 0 and are not pooled seed estimates.

Saved pipelines passed 10,656 composed train/development replay checks with
fitting and optimizer updates blocked. A subsequent no-fit/no-model-load audit
authenticated all 7,210 receipt files, reconciled all 5,328 metric/confusion
records and 3,666,288 source-error participation records, and checked exact
nested arrays, shared U2/R16 sources and fixed development worlds. Independent
code/scientific and results/privacy reviews found no blocking issue; see the
[validation ledger](validation.md) for scope and the nonblocking layout/export
limits. The immutable run receipt SHA256 is
`6f070f514d98898df1121e6074e1ffef66e662963902706cab62032a85486869`.

New fitting used source revision `8ee7b69` plus the recorded pre-existing dirty
sampling-file hash. The original run and failure evidence remain unchanged;
interpretation and presentation are added separately without new fitting,
model loading or biological replay.

The source input is the authenticated compact cue-source v1, using original
outer-train membership, frozen inner assignments and the global 5,872-ID
development current/predecessor embargo before filtering. Cue activity was
reconstructed from spikes into ten 100-ms bins over [0,1) s. Spike timestamps
convert from milliseconds to seconds; Ripple cue boundaries are already seconds.
Selected events passed the recorded eligibility/full-cue rules, with no selected
missing Eye events. Missing recordings were not turned into zero firing.

Contributor separation does not establish statistical independence: time bins
remain dependent, and longer-range serial/session dependence can persist across
splits. Class/session selection uses exposed availability. Known-label
pseudopopulation construction supports a conditional endpoint association assay,
not unknown-label natural-trial deployment, simultaneous covariance, exact
trial-specific population states, intention, mechanism or formal observability.
This study does not test path information beyond endpoints or establish H1a/H1b.
