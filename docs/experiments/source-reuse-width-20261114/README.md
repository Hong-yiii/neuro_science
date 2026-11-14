# Source reuse, then population width — results, November 15, 2026

**Completed exploratory study on existing recordings.** More distinct training
sources helped some pipelines; repeating the same sources was not consistently
helpful. Wider rosters helped PCA across all four readouts, while raw and native
multisession results depended on the decoder and roster. These results support
condition-level endpoint information under this construction; they do not establish
that upsampling creates independent data or validate unknown-trial prediction.

The study was defined November 14. Training and delivery completed November 15
(Singapore). All **48 unique cases, 2,448 model-fit calls excluding scalers, and
96,000 optimizer updates** completed. No biological case was retried. The standard
comparators remained fixed; there was no hyperparameter sweep.

## The two delivered experiments

| Experiment | Executed notebook dated November 15 | Offline evidence report |
| --- | --- | --- |
| 1. Source reuse: 2/3/5 distinct sources at fixed width, plus once-only control | [Notebook](../../../outputs/source-reuse-width-20261114/deliverables-20261115-03/source_reuse_20261115.executed.ipynb) · [static HTML](../../../outputs/source-reuse-width-20261114/deliverables-20261115-03/source_reuse_20261115.executed.html) | [Source reuse report](../../../outputs/source-reuse-width-20261114/deliverables-20261115-03/source_reuse/report.html) |
| 2. Width: 17/49/83 columns at three sources per pool | [Notebook](../../../outputs/source-reuse-width-20261114/deliverables-20261115-03/population_width_20261115.executed.ipynb) · [static HTML](../../../outputs/source-reuse-width-20261114/deliverables-20261115-03/population_width_20261115.executed.html) | [Population width report](../../../outputs/source-reuse-width-20261114/deliverables-20261115-03/population_width/report.html) |

Each notebook preserves its nine executed code cells and all original outputs, then
adds one labelled interpretation cell. Both reports include source distributions,
training/development scores, learning curves, cue-time latent trajectories,
count/normalized confusion explorers and best/worst error comparisons. There are
4,608 unique split-level confusion matrices; the reports expose 5,376 views because
the B3 bridge appears in both. There are 61 original figures plus four supplemental
paired-change figures. Large artifacts remain local and ignored by Git.

[Frozen protocol](protocol.md) · [metadata design](design.json) ·
[progress scratchpad](scratchpad.md) · [validation and exact identities](validation.md) ·
[implementation/source notebooks](../../../experiments/source_reuse_width_20261114/README.md).

## What was held fixed and what changed

One fixed nine-class task is used throughout:
`1→2, 1→4, 2→5, 2→6, 3→1, 4→6, 5→3, 5→4, 6→2`.
These are ordered endpoints, not measured paths or a Cartesian 3×3 grid. Metadata
selection maximized the width supporting five training sources per session–class
pool, then the width supporting three, then used a fixed class-order tie-break.
The selection used source availability, not neural accuracy.

| Arm | Recorded columns / sessions | Distinct training sources per session × class | Total selected training source IDs | Constructed training rows | Uses per selected source |
| --- | ---: | ---: | ---: | ---: | ---: |
| B2 | 17 / 3 | 2 | 54 | 144 | 8 |
| B3, shared between experiments | 17 / 3 | 3 | 81 | 144 | 5 or 6 |
| B5 | 17 / 3 | 5 | 135 | 144 | 3 or 4 |
| U3, once-only control | 17 / 3 | Same three as B3 | 81 | 27 | 1 |
| Wmid | 49 / 11 | 3 | 297 | 144 | 5 or 6 |
| Wfull | 83 / 20 | 3 | 540 | 144 | 5 or 6 |

Before budget selection, the core/middle/full rosters provide 160/543/912 eligible
training sources and 56/210/365 development sources. All arms use 72 constructed
development rows. Five/18/41 development pools are singletons, respectively.
Available sources, selected source IDs and synthetic rows are different quantities;
none is a count of independent animals or simultaneous population trials.

![Recorded width, available sources and constructed rows across the three rosters](../../../outputs/source-reuse-width-20261114/deliverables-20261115-03/population_width/figures/design.png)

*Design counts for the fixed nine endpoint classes, using the frozen outer-training
subset after the global current/predecessor embargo. Counts distinguish recorded
columns, available real sources and constructed rows. This is a source-availability
figure, with no decoder, statistical interval or performance claim. Provenance:
accepted `complete-01/report_width`, authenticated in the delivery manifest.*

Train and development contributors were separated before fitting. Shared columns
and development source assignments match exactly across width arms; training source
budgets are nested on the core. Three paired computational seeds vary source
selection, assembly and optimization. Five within-session/split source-label worlds
are matched across arms. They are diagnostic controls, not a calibrated significance
test. The development set has historical exposure and is assembled using known labels.

Every arm includes raw, PCA7, CEBRA-Time7 and native multisession CEBRA7, each with
logistic, RBF-SVM, kNN5 and SVD-LDA for pair/start/goal. Both CEBRA branches train
for 1,000 updates per case. Readouts use the whole cue, ten 100-ms bins from 0–1 s.
Latent readouts have 70 features; raw readouts have 170/490/830. Native training
uses pair labels and one encoder per session; Time uses within-row temporal
positives. This compares complete pipelines with different supervision and pooling.

## Experiment 1: distinct sources and repeated assembly

Pair balanced accuracy (%) with RBF-SVM; entries are mean [minimum, maximum] across
three computational repeats. The uniform pair reference is 11.11%. Ranges are not
biological confidence intervals. All other readouts, heads and controls are in the
reports and CSV tables.

| Representation | B2 | B3 | B5 | U3, once-only |
| --- | ---: | ---: | ---: | ---: |
| Raw | 36.57 [12.50, 54.17] | 37.96 [25.00, 47.22] | 59.72 [56.94, 63.89] | 40.74 [36.11, 43.06] |
| PCA7 | 32.41 [16.67, 45.83] | 33.33 [18.06, 47.22] | 34.26 [25.00, 43.06] | 40.28 [33.33, 44.44] |
| CEBRA-Time7 | 16.67 [11.11, 22.22] | 34.72 [22.22, 44.44] | 46.30 [41.67, 52.78] | 24.54 [16.67, 36.11] |
| Native multisession7 | 25.00 [18.06, 34.72] | 29.63 [22.22, 36.11] | 28.70 [23.61, 36.11] | 26.39 [16.67, 33.33] |

The clearest source-budget gains under the sampled controls are **Raw/SVM B5−B3
at +21.76 percentage points** and **Time/SVM B5−B2 at +29.63 points**. Each of their
three observed paired changes exceeds all five matched diagnostic changes. Other
positive averages do not all have that separation; the plot retains every contrast.

![Observed paired changes and source-label diagnostic changes at fixed width](../../../outputs/source-reuse-width-20261114/deliverables-20261115-03/source_reuse/paired_svm_changes.png)

*Fixed 17 columns/3 sessions and nine endpoint classes; whole-cue RBF-SVM pair
balanced accuracy on 72 constructed development rows. Dots/thin ranges show mean
and min–max of three paired computational repeats; crosses/thick ranges show five
source-label worlds at model seed0. Units are percentage points, after minus before.
Zero is the no-change reference. Source identities and constructed row counts are
given above. These are diagnostic ranges, not p-values or biological intervals.
Provenance: authenticated saved paired-contrast tables; no fits during plotting.*

**Once-only assembly retains evidence of endpoint association.** Every observed
Raw/SVM and PCA/SVM U3 pair score exceeds all five corresponding sampled label-world
scores. Repeating those same source IDs in B3 lowers their mean pair scores by
2.78 and 6.94 points, while Time/SVM and native/SVM rise by 10.19 and 3.24 points.
None of these four B3−U3 changes separates all observed changes from the diagnostic
range. Repetition is therefore neither necessary for these Raw/PCA results nor
uniformly beneficial across pipelines.

This is a sampling-policy comparison. Increasing the source budget at fixed row
count simultaneously changes response diversity, repetition, weighting and joint
combinations. U3/B3 holds source identities fixed but changes rows, combinations,
weights and exposure. U3 has uniform once-only weights; B3 has five/six uses per
source. Neither comparison estimates a pure causal effect of repetition.

## Experiment 2: horizontal population expansion

Same metric, decoder, repeat summaries and exposed development construction:

| Representation | 17 columns, B3 | 49 columns, Wmid | 83 columns, Wfull |
| --- | ---: | ---: | ---: |
| Raw | 37.96 [25.00, 47.22] | 52.31 [45.83, 55.56] | 46.30 [44.44, 48.61] |
| PCA7 | 33.33 [18.06, 47.22] | 68.06 [62.50, 72.22] | 72.22 [59.72, 88.89] |
| CEBRA-Time7 | 34.72 [22.22, 44.44] | 35.65 [29.17, 40.28] | 48.61 [40.28, 52.78] |
| Native multisession7 | 29.63 [22.22, 36.11] | 38.89 [23.61, 51.39] | 27.78 [15.28, 43.06] |

PCA mean pair accuracy increases at both expansion steps **for all four readouts**.
Raw is decoder-dependent: logistic rises 42.13→63.43→66.20%, whereas SVM peaks at
49 columns. Native mean pair accuracy falls from 49 to 83 columns for all four
readouts. Its SVM drop is dominated by one repeat; the other two have small gains.
Raw/SVM falls from 49 to 83 in all three repeats.

![Every fixed encoder/readout's paired width changes](../../../outputs/source-reuse-width-20261114/deliverables-20261115-03/population_width/all_model_paired_changes.png)

*Fixed nine-class pair task and three sources/session × class, 144 training and
72 development pseudorows. Cells show mean percentage-point change across three
paired computational repeats, for every fixed whole-cue encoder/readout. Positive
values favor the left-hand arm in each after−before label; zero is the reference.
No uncertainty interval is displayed here; every repeat and control range is in
`contrast_summary.csv`. Width adds measured sources and sessions as well as columns.
Provenance: saved, authenticated paired-contrast tables.*

Among SVM width contrasts, **PCA Wmid−B3 (+34.72 points)** and **Time Wfull−Wmid
(+12.96 points)** separate all three observed changes from all five matched
diagnostic changes. The other positive SVM means overlap diagnostic ranges. A
large absolute score and a reliable improvement over another arm are distinct.

The population expansion changes sessions, selected source IDs, and native-model
parameterization/pooling together. Native uses 3/11/20 networks and 255/253/240
total references per update. The experiment does not isolate neuron count or
identify individually harmful cells/sessions.

## Best/worst errors and the issue #29 handoff

Best/worst is selected separately within each representation/readout by mean
observed pair balanced accuracy, with frozen-order ties. Reuse ranking includes
B2/B3/B5; U3 remains a separate control. The following SVM summaries are post-hoc
descriptions, not additional validation. Counts pool three predictions on each of
72 matched synthetic development rows; 216 predictions are not 216 independent trials.

| Part / SVM representation | Best versus worst | Classes improved / worsened / unchanged | Wrong→right / right→wrong when moving worst→best |
| --- | --- | ---: | ---: |
| Reuse / Raw | B5 versus B2 | 7 / 2 / 0 | 60 / 10 |
| Reuse / PCA | B5 versus B2 | 5 / 2 / 2 | 28 / 24 |
| Reuse / Time | B5 versus B2 | 6 / 3 / 0 | 85 / 21 |
| Reuse / Native | B3 versus B2 | 3 / 4 / 2 | 31 / 21 |
| Width / Raw | Wmid versus B3 | 5 / 3 / 1 | 48 / 17 |
| Width / PCA | Wfull versus B3 | 8 / 1 / 0 | 97 / 13 |
| Width / Time | Wfull versus B3 | 7 / 2 / 0 | 69 / 39 |
| Width / Native | Wmid versus Wfull | 6 / 3 / 0 | 55 / 31 |

For example, Raw/SVM B5 versus B2 improves `1→4` recall by 75 points but reduces
`2→5` by 12.5 points. Time/SVM Wfull versus B3 improves `4→6` by 79.17 points but
reduces `6→2` by 50 points. A better overall score can conceal substantial
class-specific regressions. These are means over 24 predictions per class across
three repeats, with the same development construction within each comparison.

![Best/worst pair-class recall changes across all fixed models](../../../outputs/source-reuse-width-20261114/deliverables-20261115-03/population_width/figures/best_worst_class_changes.png)

*Width experiment, same fixed task/split and whole-cue readouts. Each cell is mean
class-recall change from that model's worst to best arm across three computational
repeats, using eight constructed development rows/class/repeat. Selected rankings
and all values are saved in `best_worst.csv` and `class_recall.csv`; ties were checked
with exact integer pair-correct totals. This post-hoc view has no biological interval
and does not attribute an error to a particular source/session.*

No classes were deleted between these arms. Retained/removed unit and session
aliases, source-use tables, full count/normalized confusions, class recalls and
paired prediction switches are in both reports. They locate changed errors but
cannot explain them through lost place fields: authenticated spatial rate maps,
occupancy and maze-coordinate joins are absent from compact cue-source v1.
**Field coverage is unknown, not zero.** A later #29 analysis needs maps tied to
these exact unit/session identities, occupancy/quality support and common maze
coordinates before associating retained coverage with errors. The source-budget
constraint follows the constraint-based idea behind #30; its spatial-selectivity
criterion was not tested here.

## What this evidence supports next

Keep distinct-source budgets and realized reuse as explicit construction metadata;
do not count upsampled rows as newly observed data. Five-capable core populations
provide a useful controlled comparison, while three-source rosters permit broader
width. The observed PCA width gains and Raw/Time source-budget gains justify
retaining these simple comparisons when planning the next study, without selecting
a universal winner from an exposed development set.

This run measured whole-cue decoding and latent class-mean cue trajectories. It did
not fit new time-resolved decoders, temporal-transfer matrices, navigation/path
models or spatial-field models. The trajectory figures are unaligned latent
coordinates, not simultaneous neural dynamics. Known-label pseudopopulation
assembly, historical development exposure and dependent sources bound every claim.
The hypothetical perfect-single-endpoint pair reference is 66.67% for this sparse
task; it is a mathematical reference, not a fitted baseline or a path-coding test.

The [validation ledger](validation.md) records independent numerical/claim reviews,
all attempt boundaries, the preserved orchestration failure and its continuation.
No further fit, retry, push, merge or issue modification is queued.
