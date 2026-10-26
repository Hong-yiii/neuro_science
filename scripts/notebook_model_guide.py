"""Teaching layers for the fresh PCA/LDA and CEBRA notebooks.

This source builder changes exposition and adds descriptive, non-fitting
diagnostics around the existing approved grids. It never executes notebooks.
"""

from __future__ import annotations

from copy import deepcopy


INPUT_EXPLANATION = r"""
## Establish what the observations and targets mean

The direct measurements are sorted spike timestamps and recorded task-event markers.
A sorted unit is an inferred spike cluster, not a census of every hippocampal neuron.
For lab inputs, the analysis converts spikes into counts in ten half-open 100-ms
cue bins spanning 0–1 s from cue onset; the smaller invented fixture has four bins.
The marker-derived start and goal are provisional task labels:
agreement between recording streams is a consistency check, not independent proof of
the experiment's semantic meaning. Source eligibility, exclusions and the marker
join must be inspected before interpreting a decoder.

One source trial records only the units in its session block. A zero means an observed
bin containing no spikes; an off-block NaN means that unit was not recorded in that
source. Treating both as zero would manufacture measurements. To form a complete
pseudopopulation row, we match one source from **each block on the known ordered
start→goal pair** and copy that block's units and all bins together. Each resulting
row is assembled, not simultaneously recorded. This preserves within-block observations
while imposing a cross-block combination; it cannot preserve unmeasured cross-session
noise correlations or reveal a real animal's full population state.

This construction is defensible for a **condition-level assay** when every retained
block supports every requested condition in each split, units and timing agree, and
source contributors stay separated. It is not an unknown-label single-trial prediction
pipeline: the condition is needed before constructing the input. Balanced numbers of
assembled rows do not imply balanced numbers of real sources. Sparse block/pair pools
are reused more, some source measurements are never drawn, and complete-support
selection changes the population being studied. Notebook A exposes the selection
waterfall, support matrices, exclusions and source reuse in greater detail; this
notebook independently reconstructs its own inputs and repeats the core gates.

For supplied lab inputs, use only the original outer-training partition. Keep the
historically exposed development assignment frozen, embargo any training example
sharing a current or predecessor contributor with **any original development
example**, then select the complete-support panel. The predecessor matters because
the previous trial contributes the current start label. The historical source route
selected 27 units in 10 sessions; the 195-unit/58-session compact inventory does not
mean that all those units survive this analysis. The printed audit is authoritative
for this execution. Contributor separation still leaves session and longer-range
serial dependence, and development is not a pristine test set.

**Read the next outputs as a gate.** Inspect selected train/development counts,
exclusion reasons, contributor overlap and the source×unit×bin tensor. Missing support,
unexplained selection differences or overlap require investigation before fitting;
they are not reasons to silently repair labels or fill absent neural values.
"""


SPLIT_EXPLANATION = r"""
## Freeze the comparison before learning from spikes

We hold the development **values, labels, exposure and contributing sources** fixed
across observed seeds, representations and source budgets. The function
`checked_assemblies` tests this equality, not merely an equal row count. Each observed
training seed changes the constructed training sample (and CEBRA initialization and
sampler when present), while development assembly seed remains zero. These are
computational perturbations, not new subjects or independent biological replications.

The full/reduced intervention asks how sensitive this fixed workflow is to its
available training-source pool. Within every block×condition pool, reduced mode keeps
a deterministic nested `floor(n/2)` subset using the same fixed subset seed. The unit
panel, condition list, bin definitions and synthetic-row budget stay fixed. Every
learned transformation and decoder is refitted on the new training assembly. This
is not deletion of half the neurons, a new development set, or an exact 50% reduction
in independent measurements: floor rounding and source reuse matter. Inspect eligible,
actually used, unused and repeated counts alongside the score changes.

The independent provenance unit is a real source trial **plus its target
contributors**, with trials nested in sessions. Our estimand is descriptive
recoverability of the matched condition in this selected pseudopopulation, under the
declared source split and construction. A higher development score supports a better
readout of these constructed examples. It does not establish trial-specific path
prediction, intention, causal mechanism or generalization to a new animal/session.
"""


METRICS_EXPLANATION = r"""
## Decide what a successful decoder would mean

The decoder sees the entire cue, with bins concatenated in order; it does not decode
each time bin separately. We fit **three independent classification heads**: ordered
pair, start, and goal. Pair classification asks which joint endpoint condition was
used to assemble a row; start/goal ask its components. None asks which ordered path
the animal took beyond those endpoints. A strong goal head can coexist with a weak
pair head, and an easy marginal target must not be presented as successful path decoding.

For K supported classes, balanced accuracy is the mean of the K class recalls.
Accuracy counts all correct rows equally; macro-F1 averages each class's precision/recall
tradeoff. With truly equal evaluation support, accuracy and balanced accuracy coincide;
we still show both to expose support mistakes and make the metric definition explicit.
Log loss is the average negative log probability assigned to the correct class, so
it can worsen when a model becomes confidently wrong even if hard accuracy improves.
Uniform-probability references are **1/K balanced accuracy** and **ln(K) log loss**.
They are descriptive references, not significance cutoffs; macro-F1 has no general
1/K reference. See the [official metric definitions](https://scikit-learn.org/stable/modules/model_evaluation.html).

Always read count **and row-normalized** confusion matrices. Rows are true classes,
columns predicted classes; the diagonal of the normalized matrix is per-class recall.
A concentrated prediction column reveals a decoder favoring one label, even if a
single average looks acceptable. The matrices describe constructed rows, not independent
source-trial counts. The training-minus-development balanced-accuracy gap is a
diagnostic of fitting versus transfer within this assay: a large positive gap invites
an overfitting/distribution-shift explanation; a small gap with low scores is not success.

Compare representations on the same development rows, head, seed and source budget.
Compare raw logistic with PCA/CEBRA logistic to assess the consequences of the
representation under this readout choice; compare raw LDA with raw logistic to assess
the classifier assumption. Fixed regularization is a controlled workflow choice, not
proof that every representation has its optimal decoder. Do not choose the best seed
or hyperparameter after looking at development and call that a held-out result.
The figures below show individual cases and references; no confidence interval or
biological p-value is inferred from pseudorows or the two seeds.
"""


PCA_METHOD = r"""
## Follow the feature tensor: counts → standardized vectors → readout

Let X have shape **R assembled rows × U units × T cue bins**. Encoder normalization
pools only the R×T **training** unit vectors, estimating one mean and scale for each
unit. It then applies those frozen values to development. Pooling improves the
numerical definition of each feature's scale; it does not make adjacent bins independent.
The values fed to the models are standardized counts, not firing rates or directly
measured latent states. A nearly silent unit and a missing unit are different cases;
the source contract must already have resolved observation support.

The raw baseline flattens X as unit-major features: unit 1 at bins 1…T, then unit 2,
and so on. PCA fits a full-SVD linear projection to the R×T training vectors after
the same kind of train-only unit standardization. Its eight components maximize
retained training variance, without start/goal labels. It requires numerical training
rank ≥8 and does not pad a deficient representation. PCA output is flattened
**time-major**: the eight coordinates at bin 1, then eight at bin 2. Both retain time
order, but column indices have different meanings. The shown dimensions below make
the distinction checkable. Explained-variance ratios quantify retained standardized
training variance; they do not measure task information or decoder performance.

Each logistic readout additionally fits its own training-only per-feature scaler.
This step has U×T columns for raw features and 8×T for PCA, and differs from the
earlier unit scaler shared across time. A separate classifier is fitted for each
target. LDA here is a **supervised SVD classifier on the raw whole-cue features**,
with its own scaler. Its class-conditional, shared-covariance linear decision rule
is another readout assumption; it is not an unsupervised eight-dimensional embedding
and no LDA scatterplot is used to claim label-free separation. These choices are
visible in [the local implementation](../src/neuro/pca_lda.py) and the
[official LDA reference](https://scikit-learn.org/stable/modules/generated/sklearn.discriminant_analysis.LinearDiscriminantAnalysis.html).

The grid below has two observed seeds × two source budgets. It fits four PCA models,
24 logistic heads and 12 LDA classifiers. It records each bundle and fitted state so
the final cell can replay transformations and predictions with fitting blocked.
That replay checks computational reproducibility; it cannot validate the biological
meaning of the labels, the appropriateness of source selection or the scientific claim.
"""


PCA_VIEWS = r"""
## Inspect the distribution in three dimensions

The following display is fixed in advance to **observed seed 0, full sources**. It
uses the PCA learned on that case's training data, applied unchanged to its matched
development rows. It does not accidentally use whichever reduced case happened to
finish last. The three-dimensional panels show the **first three existing PCA
coordinates at the first cue bin**, colored in turn by start and goal, with gray
training points behind them. Pair information is assessed by its readout. No
second dimensionality-reduction model is fitted for the picture. The companion
all-bin view uses those same coordinates colored by native bin to reveal temporal
organization; bins and repeated source combinations are dependent observations.

Each plotted first-bin point is one condition-matched synthetic population row.
Distances are in PCA coordinates of standardized counts, not physical positions in
the maze. The model and whole-cue readout can use eight coordinates at every bin,
so a three-axis first-bin projection can hide information that the decoder retains.
Conversely, visible clusters may reflect assembly, endpoint matching, time or a
small group of heavily reused sources. The development geometry and train/development
variance/effective-rank summaries are useful diagnostics, not evidence of a neural manifold's
topology or an independent population trajectory.

Before interpreting separation, connect it to the exact head's development score,
confusion pattern and full/reduced sensitivity. Ask whether the result survives
removing source support, whether minority pools dominate reuse, and whether a raw
readout performs just as well. The selected 3D illustration is a reading aid;
the per-case numerical diagnostics above cover all four fitted PCA cases.
"""


CEBRA_METHOD = r"""
## What is CEBRA-Time being asked to learn here?

CEBRA is a contrastive encoder: the sampling rule specifies which neural vectors
should be similar, and an optimization objective rewards those similarities relative
to negatives. Time-only and behavior-conditioned sampling are different scientific
choices; the name CEBRA alone does not specify one. The original method is described
by [Schneider, Lee and Mathis (2023)](https://www.nature.com/articles/s41586-023-06031-6).
The statements below describe **this repository's cue-only implementation**, whose
sampler and normalization must be reviewed directly.

An input vector contains all U standardized units at one native cue bin. Select an
assembled training row uniformly, then select one of its forward adjacent-bin pairs
uniformly: (0,1), (1,2), …, (T−2,T−1). The first vector is the reference and the next
is its positive. Draw each negative from a uniformly selected row and bin. Pairing
does not require negatives to have a different endpoint label: same-condition
negatives are possible. Positive pairing
never crosses a row or jumps from its last bin to the next row's first bin. In this
cue-only route phase probability is one for cue; the logged navigation exposure must
be zero. The generic sampler also supports historical joint-phase work, but that
default is overridden here. References cannot occupy the last bin and positives
cannot occupy the first, so their exposure histograms need not look identical.

The encoder is the existing `offset1-model`, with eight outputs, fixed cosine
InfoNCE temperature 1 and Adam. It transforms a single native unit vector; the
temporal structure is supplied by **which vectors are paired**, not by feeding the
entire cue as one encoder input. Conceptually the loss rewards similarity between
the reference and positive while penalizing similarity to sampled negatives through
a log-sum-exp contrast. The implementation logs total, positive and negative loss
terms and temperature; their absolute values depend on the objective and sampling,
so compare trends within a matched configuration, not with classifier log loss.
The exact solver is in [cebra_solver.py](../src/neuro/cebra_solver.py), and
the audited native-pair construction is in [cebra.py](../src/neuro/cebra.py).

For reference rᵢ, positive pᵢ and a sampled negative bank nⱼ, its objective is
the batch mean of −sim(f(rᵢ), f(pᵢ))/τ + log Σⱼ exp(sim(f(rᵢ), f(nⱼ))/τ),
with τ=1 and cosine similarity. The positive is not explicitly appended to this
denominator; a source/vector can recur through sampling. The sampler therefore
defines the learning problem as much as the network architecture does.

The Time sampler does not use goal equality to select positives; it uses within-row
adjacency. Nonetheless **the input rows were already constructed using known pair
labels**, so this pipeline is not label-free in the broader experimental sense.
`train_targets` annotate rows and support an assertion that positive pairing stays
within their labels; they are not a supervised goal loss. An NLP analogy is learning
from adjacency in a corpus whose documents were deliberately assembled by label:
an unsupervised objective does not erase the selection mechanism of its inputs.

Normalization is fitted only on pooled training row/bin vectors, then frozen.
CEBRA and PCA transform each bin to eight coordinates, concatenate them in
time-major order, and feed a separate training-scaled logistic head for pair/start/goal.
Raw features are unit-major. All three readouts see the whole cue and identical
development lineage. The readout is a second learning stage; a contrastive encoder
can optimize successfully while its whole-cue features carry little information useful
to this particular linear classifier.
"""


LEARNING_EXPLANATION = r"""
## Is the model learning? Separate optimization, geometry and readout transfer

There are three questions to inspect for **every** fitted case. First, does the
declared optimization run finish with finite losses and parameters, the expected
number of updates, and the intended sampler exposure? Look at total, positive and
negative terms together. A falling total loss means the model is improving its
training contrastive objective; stochastic curves need not decrease at every update.
It does not measure held-out endpoint recovery. The demo's **20 updates** are a
software exercise, not a convergence experiment; the reviewed real configuration
fixes **1,000 updates**. Neither budget can be optimized by inspecting development
scores during this notebook, and this revision does not execute another fit.

Second, has the representation become degenerate? Inspect coordinate standard
deviations, the coordinate-covariance eigenvalue spectrum and descriptive effective
rank of pooled embeddings on training and development. Very small variation or
near-rank-one features can explain an apparently uninformative point cloud; an
eight-output network does not guarantee eight useful dimensions. Effective rank
here is the covariance participation ratio, (sum of eigenvalues)² / sum of squared
eigenvalues; it describes concentration of variance, not a count of biological
states. Treat it as a diagnostic rather than a pass/fail biological test. Broadly
distributed variance also does not guarantee useful task information.
The sampled-vector use histogram describes optimization exposure, not the number of
independent recorded trials; resampling a source does not create new neural evidence.

Third, do fixed, matched development readouts improve relative to raw/PCA and the
uniform references, and which classes account for that result? Use all seeds,
confusions, source-budget comparisons and the train/development gaps. A falling loss
with no readout improvement means the temporal objective improved without a matching
gain in this endpoint assay. A good readout with a large gap invites scrutiny of
overfitting and source composition. A clear 3D cluster on its own answers neither
question. There is no held-out contrastive-loss curve, checkpoint accuracy sweep or
early-stopping study in this grid; the final readouts cannot establish when performance
emerged or which update budget is optimal.
"""


CONTROL_EXPLANATION = r"""
## Keep observed and permuted worlds separate

Observed seeds 0 and 1 each run full and reduced sources. The alignment-breaking
control uses computational seed 0 and the same two source budgets, for six CEBRA,
six PCA and 54 logistic fits in total. In the control, joint **pair labels** are
permuted at the real-source level within each retained block×split **before**
matching. This keeps the observed provenance intact while changing the effective
condition used to assemble rows and train readouts. Permuting only the already
assembled row labels would test a different mechanism.

Each world has its own fixed development assembly. Within that world, the
full/reduced comparison has identical development values and lineage; between
worlds, construction itself changes. Label permutation preserves block/split
label counts but does not make serially dependent biological trials exchangeable.
One permutation is therefore an **alignment-breaking diagnostic**, not a calibrated
null distribution or a p-value. A residual score can reflect finite samples,
structured dependence or the construction; it cannot be declared significant.

The source-budget intervention complements this control. It asks whether a
reported score depends strongly on available real training sources while holding
the synthetic-row count fixed. More synthetic rows can improve numerical sampling
of an existing pool without adding independent measurements. Read source usage,
losses, rank and the scores together, and keep world/seed/budget in every table and
caption. Do not average the observed and permuted results into a single headline.
"""


CEBRA_VIEWS = r"""
## A 3D distribution view, with an explicit provenance

The displayed case is preselected: **observed seed 0, full sources**. We retain only
that case's train/development feature arrays for this illustration; all six cases
already have saved numerical geometry and learning summaries. The development plots
use its frozen CEBRA/PCA models, never the final permuted reduced model left in a loop
variable. The first-bin panels show coordinates 1–3, colored by start and goal, with
gray training points for reference; pair information has its own decoder head.
The companion all-bin view colors the same coordinates by native cue-bin index.
No extra projection, dimensionality search or supervised plotting model is fitted.

PCA axes are ordered by training variance. CEBRA coordinates are not ordered by
task relevance and their orientation is not a biological coordinate system; coordinate
1 from another fit is not automatically the same axis. A slice of three coordinates
from an eight-dimensional representation can conceal readout information. Points
are constructed population rows (or bins of those rows in the time view), not
simultaneously observed whole-population trials. Apparent separation by endpoint is
descriptive because endpoint matching helped construct the input. Apparent temporal
order may reflect adjacent-bin sampling, common trial timing or source reuse.

Interpret the PCA and CEBRA views alongside their matched scores, not by deciding
which cloud looks prettier. Tight clouds, smooth paths and high numerical rank do
not identify a neural-state manifold, prove dynamics or establish intention. We
deliberately avoid connecting independent synthetic rows with lines: there is no
measured population trajectory between them. Units remain arbitrary standardized
embedding coordinates. The plot is an inspection surface for distribution, spread,
outliers and color organization; the quantitative assay remains the declared readout.
"""


JOINT_CONTEXT = r"""
## How did joint cue/navigation training change the historical result?

**This cue-only notebook cannot estimate the joint-training effect.** The compact
source contract reconstructs cue activity and omits dense navigation behavior.
Reusing a cue-only loss curve or adding a second target head would not create a joint
training comparison. “Joint pair target” (start together with goal) and “joint
cue/navigation training” (two task phases) are different uses of the word joint.

In the historical endpoint study, the same encoder was trained using cue and
navigation vectors, with the joint Time sampler allocating phase draws equally
between cue and navigation. Positives were adjacent native bins **within a phase and
row**; sharing encoder weights did not impose a cross-phase positive pair or align
the phases biologically. At a fixed number of updates, joint training also reallocates
sampling exposure away from cue, so any score difference bundles a change in training
distribution and phase exposure. It is not a pure test of “more neural data.”

The accepted October 7 endpoint evidence used the historical **195-unit/58-session**
panel, three seeds, eight-dimensional 1,000-update CEBRA-Time encoders, and matched
cue readouts. Joint training improved some endpoint scores but did not uniformly
beat raw/PCA references, and the whole-cue arm-gain controls did not establish robust
joint superiority. That is an endpoint result, not evidence that cue and navigation
have the same geometry, that one representation rotates into the other, or that path
information beyond start/goal was recovered. The present complete-support panel and
predecessor embargo differ, so comparing its score directly with the historical joint
score would confound the cohort and construction with training phase.

The [research walkthrough](00_research_guide.ipynb) places the actual historical
figures and their provenance in the full story. For the accepted original numbers,
seed detail, nulls and confusions, use the
[historical endpoint report](../docs/reports/cebra-endpoint-time-readout-20261006/README.md)
and the [saved-model review notebook](../report/endpoint_walkthrough.ipynb).
Those artifacts own their execution evidence; this notebook does not replay them.
A new matched joint experiment would need navigation inputs, an explicit scientific
protocol and fresh execution approval. It is a research design question, not a
missing plotting option in the current cue-only workflow.
"""


GLOSSARY_AND_REVIEW = r"""
## What the next researcher should be able to defend

**Source trial** means a recorded trial, with a predecessor contributor when required
for label derivation. **Block** is the group of units copied from one recording
session. **Pseudorow** is the condition-matched assembly across blocks; its count is
not biological n. **Representation/encoder** maps neural vectors to features;
**readout/decoder** predicts an operational target from those features. **Development**
means the fixed, historically exposed evaluation assignment here, not an untouched
test set. **Observability in this notebook** means that decisions, intermediate
quantities, failures and provenance can be inspected. **Formal state observability**
would require a specified dynamical system and measurement model showing which
hidden states can be distinguished; classification accuracy does not provide that.

Before handing off a result, write an evidence paragraph containing its target,
source cohort, synthetic counts, split/embargo, time window, representation/readout,
score relative to a named reference, seed and source-budget sensitivity, and strongest
allowed claim. A useful conclusion can be negative: “the encoder's objective improved,
but the matched decoder did not improve over the raw reference” is a complete research
observation. Avoid changing “not established” into evidence that hippocampal coding
is absent. Historical H1 concerns path information beyond endpoints and reproducible
organization; these endpoint heads do not settle it.

As a reading exercise, trace one tensor column back to unit and cue bin, then trace
one assembled row back to its block contributors without exporting their identities.
Explain why class balance in that row table can coexist with skewed source reuse.
Choose one head and reconcile its mean score with the worst recall in its confusion
matrix. Explain why the full/reduced difference is a source-sensitivity result and
why a change in a three-axis display is not automatically a readout improvement.
Finally, list which claims remain impossible even if every software assertion passes.
These exercises require inspecting existing outputs, not running additional models.

The final cell closes fit accounting, authenticates this execution's artifact manifest
and replays its saved transformations/predictions with fitting blocked. Read its
status as a computational check. A defensible scientific result additionally needs
the source/label reasoning above and an independent review of leakage, dependence,
confounds and the written claim. This source notebook's outputs are intentionally
cleared; the revised figures are specifications until an authorized execution produces
them. Earlier successful runs attest their recorded code, not these newly added cells.
"""


SUMMARY_CODE = """# Summaries use already-computed predictions; no model is fitted in this cell.
from html import escape
from IPython.display import HTML
metric_rows = metrics_table(results)
columns = [('world', 'World'), ('seed', 'Seed'), ('budget', 'Sources'), ('model', 'Model'),
           ('head', 'Target'), ('classes', 'K'), ('train_BA_percent', 'Train BA %'),
           ('development_BA_percent', 'Development BA %'), ('uniform_BA_percent', 'Uniform BA %'),
           ('gap_percentage_points', 'Gap (pp)'), ('accuracy_percent', 'Accuracy %'),
           ('macro_F1', 'Macro F1'), ('log_loss_nats', 'Log loss (nats)'),
           ('uniform_log_loss_nats', 'Uniform loss (nats)')]
def metric_text(value):
    return f'{value:.3f}' if isinstance(value, (float, np.floating)) else str(value)
header = '<tr>' + ''.join('<th>' + escape(label) + '</th>' for _, label in columns) + '</tr>'
body = ''.join('<tr>' + ''.join('<td>' + escape(metric_text(row[key])) + '</td>'
                              for key, _ in columns) + '</tr>' for row in metric_rows)
display(HTML('<div style="overflow-x:auto"><table><caption>Matched whole-cue readouts; '
             'constructed rows, no biological uncertainty intervals</caption><thead>'
             + header + '</thead><tbody>' + body + '</tbody></table></div>'))
fig = plot_decoder_summary(results)
display(fig); plt.close(fig)
print('How to read this execution:')
for row in results:
    score = row['development']
    k = len(score['classes'])
    ba = score['balanced_accuracy']
    gap = row['balanced_accuracy_gap']
    relation = 'above' if ba > 1 / k else ('below' if ba < 1 / k else 'at')
    print(f\"{row['name']}: development BA {ba:.3f} is {relation} uniform {1 / k:.3f}; \"
          f\"train minus development {gap:+.3f}; log loss {score['log_loss']:.3f} vs uniform {np.log(k):.3f}.\")
print('These are constructed-row summaries, without biological significance or independence claims.')
by_name = {row['name']: row for row in results}
example = by_name['observed_seed0_full_raw_pair']['development']
counts = np.asarray(example['confusion_counts'], dtype=float)
class_support = counts.sum(axis=1)
assert np.all(class_support > 0)
recall = np.diag(counts) / class_support
worked_ba = recall.mean()
worked_accuracy = np.trace(counts) / counts.sum()
np.testing.assert_allclose(worked_ba, example['balanced_accuracy'])
np.testing.assert_allclose(worked_accuracy, example['accuracy'])
print('Worked confusion arithmetic: observed seed 0 / full / raw logistic / pair')
print('True-class supports:', class_support.astype(int).tolist())
print('Diagonal / true-class support = recalls:', np.round(recall, 3).tolist())
print(f'Mean class recall = BA {worked_ba:.3f}; diagonal sum / all rows = accuracy {worked_accuracy:.3f}.')
worst = int(np.argmin(recall))
print('Lowest recall class (first on ties):', example['classes'][worst], f'{recall[worst]:.3f}')
print('Matched source-budget sensitivity (full minus reduced development BA):')
for name, full in by_name.items():
    if '_full_' in name:
        reduced = by_name[name.replace('_full_', '_reduced_', 1)]
        delta = full['development']['balanced_accuracy'] - reduced['development']['balanced_accuracy']
        print(f\"{name}: {delta:+.3f}; same development rows within this world/seed.\")
print('Inspect the source reuse reports and confusion rows before attributing a difference to representation quality.')"""


def _source(cell):
    return "".join(cell["source"])


def _replace_once(text, old, new):
    if text.count(old) != 1:
        raise ValueError(f"Notebook guide expected exactly one code anchor: {old!r}")
    return text.replace(old, new, 1)


def _revise_baseline_loop(text):
    text = _replace_once(
        text,
        "        run_results = []",
        """        print(key, 'Tensor/feature shapes:', {'row_unit_bin': train.values.shape,
              'raw_unit_major': raw_train.shape, 'pca_time_major': pca_train.shape})
        geometry = embedding_summary(pca_train, pca_dev, n_bins=train.values.shape[2])
        case_diagnostics[key] = {'pca_geometry': geometry}
        print(key, 'PCA geometry:', json.dumps(geometry, sort_keys=True))
        if key == 'observed_seed0_full':
            reference_view = {'key': key, 'train': pca_train.copy(), 'development': pca_dev.copy(),
                              'targets': target_heads(development), 'n_bins': train.values.shape[2],
                              'unit_mean': standardizer.scaler.mean_.copy(),
                              'unit_scale': standardizer.scaler.scale_.copy(),
                              'variance_ratio': pca.pca.explained_variance_ratio_.copy()}
        run_results = []""",
    )
    return text + "\nstore.save('diagnostic_summaries', case_diagnostics)"


def _revise_cebra_loop(text):
    text = _replace_once(
        text,
        "            run_results = []",
        """            print(key, 'Tensor/feature shapes:', {'row_unit_bin': train.values.shape,
                  **{name: pair[0].shape for name, pair in feature_pairs.items()}})
            learned = learning_summary(encoder)
            geometry = {name: embedding_summary(*feature_pairs[name], n_bins=train.values.shape[2])
                        for name in ('pca', 'cebra')}
            case_diagnostics[key] = {'optimization': learned, 'geometry': geometry}
            print(key, 'Optimization:', json.dumps(learned, sort_keys=True))
            print(key, 'Geometry:', json.dumps(geometry, sort_keys=True))
            if key == 'observed_seed0_full':
                reference_view = {'key': key, 'n_bins': train.values.shape[2],
                                  'targets': target_heads(development),
                                  'features': {name: tuple(x.copy() for x in feature_pairs[name])
                                               for name in ('pca', 'cebra')}}
            run_results = []""",
    )
    text = _replace_once(
        text,
        """            fig, axes = plt.subplots(1, 2, figsize=(9, 3))
            axes[0].plot(encoder.diagnostics['loss']['total']); axes[0].set(xlabel='Optimizer update', ylabel='InfoNCE loss', title=key)
            axes[1].hist(encoder.diagnostics['sample_exposure_counts'].reshape(-1), bins=15)
            axes[1].set(xlabel='Realized reference/positive/negative uses', ylabel='Native vector entries', title='Sampler exposure, not effective biological n')""",
        """            fig = plot_learning(encoder, title=key + ': training objective and realized exposure')""",
    )
    return text + "\nstore.save('diagnostic_summaries', case_diagnostics)"


def enrich_model_notebooks(b, c, md, code):
    """Return enriched cells, leaving first code and final accounting intact."""
    baseline = []
    for original in deepcopy(b):
        text = _source(original)
        if original["cell_type"] == "markdown":
            if text.startswith("# 2 —"):
                baseline.append(md(r"""
# 2 — What do simple models recover from the cue?

This notebook is a research guide to the **PCA and LDA reference experiment**.
Its question is whether ordered endpoint pair, start and goal can be recovered
from a source-separated, condition-matched cue pseudopopulation, and how sensitive
that recovery is to the real training-source pool. It builds from fresh inputs;
Notebook A is useful background but is not an execution dependency.

Read each decision before its code, then use the resulting diagnostics to decide
what can be defended. We first justify observations and source separation, then
trace normalization and feature shapes, compare raw/PCA logistic and raw LDA
readouts, inspect 3D geometry and source sensitivity, and finish with an artifact
replay. The [research walkthrough](00_research_guide.ipynb) connects this bounded
experiment to the historical path, endpoint and joint-training work.

**Evidence status:** the default invented inputs are a software smoke test, with
three landmarks and six ordered pairs; their scores are not neuroscience evidence.
The supplied biological route is a separately gated exploratory analysis with six
landmarks/30 pairs and a selected complete-support panel. Neither is confirmatory.
The current notebook is unexecuted teaching source with empty outputs; saved older
execution records do not validate these revised cells. Nothing here changes the
accepted fit grid or authorizes another biological run.
"""))
            elif text.startswith("## Explicit metadata"):
                baseline.append(md(INPUT_EXPLANATION))
            elif text.startswith("## Freeze development"):
                baseline.append(md(SPLIT_EXPLANATION))
            elif text.startswith("## Visible refit"):
                baseline.extend([md(PCA_METHOD), md(METRICS_EXPLANATION)])
            elif text.startswith("## Training statistics"):
                baseline.extend([
                    md("""## Read the scores before looking at the clouds

Each table row names its source budget, seed, representation and target. The summary
shows train/development performance together; a seed is a computational sensitivity
case, not an error bar. The text below reports the numbers actually produced by this
execution rather than assuming that PCA or LDA must win. Positive full-minus-reduced
differences indicate sensitivity to source availability under this one nested subset;
they do not establish a sample-efficiency law or a causal biological effect."""),
                    code(SUMMARY_CODE),
                    md(PCA_VIEWS),
                ])
            elif text.startswith("## Interpretation limits"):
                baseline.extend([md(text), md(GLOSSARY_AND_REVIEW)])
            else:
                baseline.append(original)
        elif text.startswith("from neuro.pca_lda import"):
            baseline.append(code(text + """
from neuro.notebook_diagnostics import metrics_table, plot_decoder_summary, embedding_summary, plot_embedding_views
case_diagnostics = {}
reference_view = None"""))
        elif text.startswith("for seed in settings['seeds']"):
            baseline.append(code(_revise_baseline_loop(text)))
        elif text.startswith("print('Last training pooled-bin"):
            baseline.append(code("""assert reference_view is not None and reference_view['key'] == 'observed_seed0_full'
print('Displayed case:', reference_view['key'])
print('Frozen training unit means/scales:', reference_view['unit_mean'].round(3).tolist(), reference_view['unit_scale'].round(3).tolist())
print('Training explained-variance ratio:', reference_view['variance_ratio'].round(4).tolist())
fig = plot_embedding_views(reference_view['train'], reference_view['development'], reference_view['targets'],
                           n_bins=reference_view['n_bins'], title='Observed seed 0 / full sources / PCA')
display(fig); plt.close(fig)
print('Per-case diagnostics cover:', sorted(case_diagnostics))"""))
        else:
            baseline.append(original)

    contrastive = []
    for original in deepcopy(c):
        text = _source(original)
        if original["cell_type"] == "markdown":
            if text.startswith("# 3 —"):
                contrastive.append(md(r"""
# 3 — Is CEBRA learning a useful cue representation?

This standalone notebook follows a fresh **cue-only CEBRA-Time** experiment from
source interpretation to its optimization, embedding geometry and matched decoder
results. It asks three distinct questions: does optimization behave as intended,
does the representation retain variation, and can fixed downstream readouts recover
endpoint conditions on source-separated development assemblies? The answer to one
need not be the answer to the others. We also test source-budget sensitivity and
an alignment-breaking permutation control.

The package supplies tested operations, while the cells below expose the scientific
choices: what counts as an observation, why conditions are matched, how contributors
are separated, which vectors form contrastive pairs, what a readout measures and
what a three-dimensional view cannot establish. No previous notebook's objects or
historical fitted models are required. The [research walkthrough](00_research_guide.ipynb)
connects this cue assay to the historical work, including joint cue/navigation training.

**Evidence status:** invented inputs and 20 optimizer updates demonstrate the
software; their scores are not biological evidence or a convergence study. Supplied
lab inputs use a separately gated exploratory protocol with 1,000 updates and a
selected source panel. The revised source notebook has empty outputs and is not an
executed result. Existing historical runs belong to their recorded code and cohort.
This revision adds inspection and explanation without changing the fit grid, fitting
another model or authorizing a new study.
"""))
            elif text.startswith("## Explicit metadata"):
                contrastive.append(md(INPUT_EXPLANATION))
            elif text.startswith("## Declare optimization"):
                contrastive.extend([md(SPLIT_EXPLANATION), md(CEBRA_METHOD), md(CONTROL_EXPLANATION)])
            elif text.startswith("## Visible fresh encoder"):
                contrastive.extend([md(LEARNING_EXPLANATION), md(METRICS_EXPLANATION)])
            elif text.startswith("## Inspect transformed"):
                contrastive.extend([
                    md("""## Read the matched decoder evidence

The summary keeps observed and permuted worlds distinct and names every seed/source
budget. Compare raw, PCA and CEBRA within one case before comparing budgets. The
printed statements describe the scores just computed; they do not automatically
interpret a difference as learning, significance or biological information. There
are no decoder accuracy-versus-update curves in this grid: each readout uses the
final representation. Revisit the optimization and rank summaries for cases where
the readout result does not match the visual impression."""),
                    code(SUMMARY_CODE),
                    md(CEBRA_VIEWS),
                ])
            elif text.startswith("## Interpretation limits"):
                contrastive.extend([md(JOINT_CONTEXT), md(text), md(GLOSSARY_AND_REVIEW)])
            else:
                contrastive.append(original)
        elif text.startswith("import neuro.cebra as cebra"):
            contrastive.append(code(text + """
from neuro.notebook_diagnostics import metrics_table, plot_decoder_summary, embedding_summary, plot_embedding_views, learning_summary, plot_learning
case_diagnostics = {}
reference_view = None"""))
        elif text.startswith("for world in ('observed', 'permuted')"):
            contrastive.append(code(_revise_cebra_loop(text)))
        elif text.startswith("z = feature_pairs['cebra'][1]"):
            contrastive.append(code("""assert reference_view is not None and reference_view['key'] == 'observed_seed0_full'
print('Displayed case:', reference_view['key'])
for representation in ('pca', 'cebra'):
    train_x, development_x = reference_view['features'][representation]
    fig = plot_embedding_views(train_x, development_x, reference_view['targets'],
                               n_bins=reference_view['n_bins'],
                               title='Observed seed 0 / full sources / ' + representation.upper())
    display(fig); plt.close(fig)
print('Per-case optimization and geometry diagnostics cover:', sorted(case_diagnostics))
print('Grid summary: 6 CEBRA, 6 PCA, 54 logistic; observed and permuted worlds remain separate.')"""))
        else:
            contrastive.append(original)
    return baseline, contrastive
