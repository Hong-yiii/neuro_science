# Endpoint learning after reducing classes and source reuse

November 10, 2026 · **Completed exploratory analysis with new biological model fits.**
These are new computations on existing recordings, not newly collected neural data.

**The main finding:** endpoint information remains recoverable when every selected
current trial is used only once in the assembled training rows. Repeated assembly
draws are therefore not necessary for the observed learning. The results also show
substantial sensitivity to which recorded columns are included and how source
trials are allocated. They support a condition-level pseudopopulation assay, with
important limits on generalization; they do not establish universal sampling validity.

Read the [complete offline report](../../../outputs/source-support-20261110/deliverables/report.html)
or the [executed notebook with interpretation](../../../outputs/source-support-20261110/deliverables/source_support.executed.ipynb).
Both contain all 157 figures: support/reuse and performance diagnostics, every
CEBRA learning curve, 24 observed cue-time trajectory figures, and 117 panels of
count and normalized confusion matrices. The
[complete tables](../../../outputs/source-support-20261110/deliverables/tables/metrics.csv)
retain every case, seed, target and model family. These large artifacts remain local.

## What was actually trained

The [prefit protocol](../../source-support-protocol-20261110.md) fixed eight observed
arms, three computational seeds, and five source-label shuffle worlds on three
key arms. All **39 cases completed**, comprising **39 CEBRA encoders, 39 PCA fits,
351 logistic readouts and 117 LDA fits**, plus training-only scalers. CEBRA completed
39,000 optimizer updates. These are fresh fits from authenticated compact source;
historical fitted results were not used as substitutes.

All readouts use the ten 100-ms bins in the first cue second. Raw, PCA8 and CEBRA8
features feed logistic readouts; raw SVD-LDA is a fourth reference. Start, goal and
ordered start–goal pair are separate targets. The CEBRA-Time encoder uses hidden
width 32, output width 8, batch 256 and 1,000 updates. No hyperparameter search was
performed. When training row counts change, logistic regularization is adjusted
to keep `N_train × C = 1.44` within the nine-class task.

Source identity and predecessor contributors remain separated across the frozen
training/development assignments. The **global 5,872-contributor development
embargo** is applied before dropping classes or sessions. All model preprocessing
is training-only. Development has already been exposed in the research history;
it is not a pristine test set.

## The 3 × 3 panel and population sizes

The selected conditions are **starts {2,3,5} × goals {1,4,6}**, giving nine valid
ordered pairs. All 20 disjoint rectangles were compared using source metadata,
before neural scores were available. This rectangle maximized retained recording
columns, with sessions and lexicographic order as tie-breakers.

| Required sources per session × pair | Selected units / sessions | Eligible training / development current trials |
| --- | ---: | ---: |
| Original 30 classes, at least 2 training / 1 development | 27 / 10 | 1,415 / 551 |
| Nine classes, at least 2 training / 1 development | 144 / 43 | 1,796 / 722 |
| Nine classes, at least 3 training / 1 development | 80 / 20 | 863 / 342 |
| Nine classes, at least 5 training / 1 development | 0 / 0 | No feasible rectangle |

“Units” means recorded feature columns. These are cross-session pseudopopulations,
not a simultaneous 144-neuron recording. Retaining fewer conditions makes a much
wider panel feasible; it does not automatically eliminate source reuse. The
minimum-five version of this disjoint 3 × 3 task is infeasible under the preserved
split/embargo, rather than an unrun model comparison. This does not rule out every
other class subset at minimum five.

| Arm | Pair classes | Units / sessions | Assembled training rows | Construction |
| --- | ---: | ---: | ---: | --- |
| A | 30 | 27 / 10 | 480 | 16 rows/class, ordinary replacement draws |
| B | 9 | 27 / 10 | 144 | Reference columns projected from C's source plans |
| C | 9 | 144 / 43 | 144 | Full eligible pools, ordinary replacement draws |
| D | 9 | 43 / 43 | 144 | One fixed column/session, same sources and rows as C |
| E | 9 | 80 / 20 | 144 | Minimum-three panel projected from C |
| F | 9 | 80 / 20 | 144 | Same pools as E, balanced source allocation |
| G | 9 | 80 / 20 | 27 | Three distinct sources/pool, each used once |
| H | 9 | 80 / 20 | 135 | Exactly G's sources, each used five times in recombined rows |

B–H share the same fixed development assembly, projected onto their respective
columns/blocks: eight rows/class, 72 constructed rows. A has 240 development rows.
Those row counts are not independent biological sample sizes. C versus D isolates
additional recorded columns within the same sessions/source plans. A versus B,
and C versus E, change more than one design property and are descriptive comparisons.

## All observed pair-decoding results

Balanced accuracy (%) averaged over seeds 0, 1 and 2; brackets give their full
range. Ranges describe computational variation, not confidence intervals.
The uniform reference is 3.33% for A and 11.11% for B–H. Different class sets have
different difficulty, so A-to-B score increases are not a controlled model gain.

| Arm | Raw + logistic | PCA + logistic | CEBRA + logistic | Raw LDA |
| --- | ---: | ---: | ---: | ---: |
| A: 30 classes / 27 units | 16.67 [15.83–17.92] | 13.19 [12.08–14.58] | 18.61 [15.00–21.67] | 9.86 [8.33–11.25] |
| B: 9 classes / 27 units | 27.31 [19.44–37.50] | 28.24 [22.22–36.11] | 46.76 [37.50–58.33] | 26.39 [18.06–31.94] |
| C: 144 units | 59.26 [56.94–63.89] | 62.50 [58.33–65.28] | 48.15 [38.89–56.94] | 28.24 [25.00–30.56] |
| D: one unit/session | 39.81 [37.50–41.67] | 36.11 [26.39–41.67] | 35.65 [26.39–51.39] | 30.09 [20.83–45.83] |
| E: 80 units, ordinary draws | 56.02 [52.78–59.72] | 56.02 [51.39–61.11] | 41.67 [30.56–55.56] | 24.54 [11.11–36.11] |
| F: 80 units, balanced draws | 57.87 [56.94–58.33] | 64.81 [56.94–75.00] | 53.70 [50.00–56.94] | 36.57 [26.39–45.83] |
| G: three sources, used once | 47.22 [41.67–54.17] | 54.17 [48.61–58.33] | 31.94 [27.78–40.28] | 24.54 [19.44–31.94] |
| H: same sources, used five times | 49.07 [45.83–54.17] | 44.44 [36.11–52.78] | 39.81 [31.94–52.78] | 27.31 [13.89–36.11] |

CEBRA is not consistently the best representation. It leads the nine-class
27-column comparison, but PCA achieves higher mean pair accuracy in the wider
C and E–H arms. LDA often produces poor probability estimates: mean pair log loss
is 30.457 in A and 7.587 in H. Those results are retained, not removed as outliers.

## Three matched questions

Each entry below is **mean balanced-accuracy change in percentage points / mean
natural-log-loss change**. Higher accuracy and lower log loss favor the first arm.
The complete report provides every paired seed value and all secondary targets.

| Contrast | Raw + logistic | PCA + logistic | CEBRA + logistic | Raw LDA |
| --- | ---: | ---: | ---: | ---: |
| C − D: 144 versus 43 columns, same sessions and source plans | +19.44 / −0.198 | +26.39 / −0.315 | +12.50 / −0.185 | −1.85 / −7.999 |
| F − E: balanced versus ordinary source allocation | +1.85 / −0.049 | +8.80 / −0.089 | +12.04 / −0.209 | +12.04 / −1.428 |
| H − G: recombination using exactly the same three-source pools | +1.85 / −0.010 | −9.72 / +0.010 | +7.87 / −0.310 | +2.78 / +5.437 |

**More recorded columns helped.** C outperformed D on both pair accuracy and log
loss in every seed for raw, PCA and CEBRA. This is evidence for useful additional
features within these sessions, conditional on the one predefined column chosen
for D. It does not separate the value of every individual neuron or establish
simultaneous population coding.

**Balanced allocation helped average performance.** F improved log loss in all
three seeds for raw, PCA and CEBRA. Their accuracy gains were positive on average
but not in every seed. Balancing includes previously unused eligible sources and
changes which session blocks occur together; the effect is not solely a causal
test of source weighting.

**Synthetic recombination had mixed effects.** H added no new neural measurements.
PCA pair accuracy fell in all three seeds, while CEBRA improved in two and declined
in one (+25.00, +6.94, −8.33 percentage points). CEBRA log loss improved in all
three. More constructed rows can change representation learning and readouts;
they cannot be counted as new independent evidence.

## Does learning survive without repeated assembly draws?

Yes, for this conditional endpoint assay. G uses 540 selected current trials:
three per pair in each of 20 sessions. Each appears once across the 27 assembled
training rows. No two same-class training rows share a current-source block.

| G pair readout | Observed mean BA | Observed seed range | Five source-label shuffle scores: range |
| --- | ---: | ---: | ---: |
| Raw + logistic | 47.22% | 41.67–54.17% | 4.17–22.22% |
| PCA + logistic | 54.17% | 48.61–58.33% | 1.39–18.06% |
| CEBRA + logistic | 31.94% | 27.78–40.28% | 0.00–13.89% |
| Raw LDA | 24.54% | 19.44–31.94% | 4.17–22.22% |

Every observed G seed exceeds all five corresponding shuffled scores for raw,
PCA and CEBRA. LDA's observed and shuffled ranges overlap. Shuffles permute the
joint endpoint label within session and split before source selection/assembly;
they break neural/label alignment. Five diagnostic worlds are not a formal
significance test or an independent biological null distribution.

“Used once” refers to current-source blocks in assembled training rows. CEBRA
still revisits bins during optimization, source trials can have serial/predecessor
dependence, and the development assembly still reuses sources. The experiment
rules out repeated training assembly draws as a necessary explanation; it does
not eliminate every possible confound or dependence.

Goal information is much stronger than start information. For G, mean start / goal
balanced accuracy is **61.57 / 94.44% raw, 64.81 / 96.30% PCA, 40.28 / 91.67% CEBRA**
(three-class reference 33.33%). The CEBRA start scores overlap the shuffle range.
For perspective, perfect goal knowledge with no start information can yield an
expected 33.33% pair score on this balanced 3 × 3 task. This is a mathematical
reference, not a newly fitted baseline. Above 11.11% pair accuracy alone therefore
does not demonstrate strong information about both endpoints. Cue identity and
other correlated signals remain plausible contributors; no path-beyond-endpoints
or intention claim follows.

## What the reuse and error audits show

The following source-use figures are seed 0; the tables retain every seed. A source
is a real current trial, while a draw is its contribution to one session block of
a constructed row. Distinct sources remain nested within sessions.

| Training arm | Eligible sources | Used / unused | Maximum uses of one source | Mean shared blocks between same-class rows |
| --- | ---: | ---: | ---: | ---: |
| C: 144 units | 1,796 | 1,710 / 86 | 13 | 10.65 / 43 |
| E: 80 units, ordinary | 863 | 824 / 39 | 9 | 4.54 / 20 |
| F: 80 units, balanced | 863 | 863 / 0 | 6 | 3.59 / 20 |
| G: three sources, once | 540 | 540 / 0 | 1 | 0 / 20 |
| H: same sources, five times | 540 | 540 / 0 | 5 | 5.71 / 20 |

The shared 80-unit development assembly has only 342 eligible current sources;
334 appear in 1,440 block draws. **46 of 180 session × pair pools are singletons**,
and two same-class development rows share an average 12.41 of 20 blocks. Thus
72 rows are emphatically not 72 independent trials. In A, the development assembly
even contains six excess exact duplicate rows. These dependencies are reported
rather than hidden behind row-level confidence intervals.

The error audit produces 197,496 source/error summary records from authenticated
joins on exact case, world, seed, row and source identities, and reconciles correct
plus incorrect appearances with source-use counts. The report includes class errors and their
relation to training support, session exclusions for all 58 sessions, per-unit
session membership, column positions and worked row traces. This does not identify
“bad neurons”: every prediction combines many session blocks, and excluded
sessions have no prediction score in the panel that excludes them. No classes or
sources were removed after inspecting their scores.

## Trajectories and learning evidence

The full report/notebook includes all 24 observed arm × seed trajectory figures,
each with PCA and CEBRA views. Lines connect class-mean development embeddings at
50, 150, …, 950 ms from cue onset; circle/triangle mark the first/last bin. The
display uses the first three native coordinates of each training-fitted 8D model,
with no display projection fitted afterward. Coordinates are not aligned across
separately fitted models; the arm/support tables give the cohort and eligible
source counts.

These are **cue-time representation trajectories**, not measured maze movement,
simultaneous neural trajectories or evidence for a shared manifold across phases.
They are descriptive: class averaging and repeated sources can make structure
look more stable. Whole-cue readouts provide the quantitative recovery test.
Every CEBRA loss curve is included, but falling contrastive loss alone is not a
learning conclusion. This study did not fit bin-specific readouts, frozen temporal
transfer matrices, navigation models or ordered-path decoders.

## Issue coverage and the next data collection decision

| Research-group issue | Delivered here | Still unresolved |
| --- | --- | --- |
| [#25: source reuse](https://github.com/Hong-yiii/neuro_science/issues/25) | Eligible/used/unused distributions, block overlap, exact duplicates, balanced and once-only controls | Independent prospective validation; serial and development dependence |
| [#26: errors and exclusions](https://github.com/Hong-yiii/neuro_science/issues/26) | Class errors, source involvement, all-session exclusions, column inheritance and row traces | Causal neuron/session attribution; performance for excluded sources |
| [#24: class count and support](https://github.com/Hong-yiii/neuro_science/issues/24) | Owner-requested nine-class adaptation: all 20 rectangles audited; panels up to 144 columns; min-three controls; min-five infeasibility | Original proposed 15/20-class fits were not run; generalization to a newly collected, adequately supported cohort remains open |
| [#23: multi-session design](https://github.com/Hong-yiii/neuro_science/issues/23) | No expanded study was added | Remains deferred |

The most useful next data are **additional distinct trials across every selected
session × condition**, with prospective evaluation reserved before fitting.
The bottleneck is support in the weakest pools, especially singleton development
pools. Increasing synthetic rows cannot fix that bottleneck. A follow-up should
carry forward raw/PCA baselines, balanced allocation and an assembly-once control,
and evaluate the frozen pipeline on new sources. This is a recommendation, not a
queued or claimed completed experiment. GitHub issues were not modified.

## Execution, reproducibility and independent review

The biological run and complete notebook/report rendering finished in **452.55 s**;
model-grid work took 240.75 s. Peak cgroup memory was **1,277,837,312 bytes
(1,218.6 MiB)** under a 4-GiB hard cap, zero swap and a two-core CPU quota. There
were no OOM events, automatic retries or failed biological cases. An invented
full-shape benchmark was run separately and is not biological evidence.

Twelve focused software checks passed before execution. A fresh pinned kernel
completed all 12 notebook code cells. Newly saved encoders/readouts were reloaded
with fitting blocked: 117 encoder checks and **936 composed training/development
readout checks** passed. Actual fit/update calls matched the declared budget.

The independent protocol/code/results reviewer verified all 468 metric/confusion
records against new saved predictions, all source/error records, paired plans and
global embargo, **1,167 receipt-bound files and 157 figure hashes**. No blocking
scientific, provenance or privacy finding remained. Report/notebook outputs and
report tables contained no detected raw recording IDs or private absolute paths.
This review is a computational/scientific audit, not independent biological
replication. Minor dense plot annotations do not replace the exact numeric tables.

The immutable run is `outputs/source-support-20261110/real-01/`. It retains input,
configuration and code hashes, exact source snapshots, package versions, dirty
Git state, models, arrays, lineage, counts and execution resources. Its
`receipt.json` SHA256 is
`a6e6d5d5078ce1428d78e2aacff70981877578a2ebb8bbc57236b70eef6a7273`.
Git base: `0c6e066858f054b65a7e777ae172bb6fd260b3c3`, with the recorded local
implementation changes; the source snapshot, not that commit alone, identifies
the executed code. Python 3.13.2 and NumPy 2.3.4 were used; the complete runtime
identity is preserved with the run.

The sibling `deliverables/` adds this interpretation to a copy of the executed
notebook and offline report. All original code cells, execution counts and outputs
are preserved; no fit or model replay occurs during collation. Its own manifest
binds the final files, this note and the immutable run receipt. Open the notebook
to read its saved evidence; rerunning its training cells creates a new experiment
and must use a fresh output directory and reviewed runtime/resource controls.

All prior artifacts, runtimes, original data, unrelated edits and retained stash
were preserved. This study is complete; no additional fit, retry, push or merge
is queued.
