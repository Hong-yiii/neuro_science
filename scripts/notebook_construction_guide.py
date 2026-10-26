"""Teaching cells for the non-fitting source-construction notebook."""

from __future__ import annotations


def enrich_construction_notebook(cells, md, code):
    """Keep construction executable and explain each scientific decision in place."""
    replacements = {
        "# 1 —": r"""# 1 — Can we construct a defensible pseudopopulation?

**Question:** do separately recorded, condition-matched sources support a reproducible
cue-response assay, and which distortions does assembly introduce? This chapter stops
before fitting. Its deliverable is an audited measurement object, not evidence that
the hippocampus predicts a path.

Start with [the research guide](00_research_guide.ipynb) for the completed research and
accepted results. Continue to [PCA/LDA](02_pca_lda.ipynb) and [CEBRA](03_cebra.ipynb)
only after you can explain the gates here. Each chapter can reconstruct its own inputs.
For the task/recording background, read [foundations](00a_experiment_foundations.ipynb).
For a tiny spike-to-prediction calculation with visible values, read the
[worked example](00b_worked_example.ipynb) before this larger construction workflow.

**Reading contract.** The default is an invented software example: three landmarks,
six ordered pairs, nine units in three blocks and four bins. It teaches mechanics;
its distributions are not lab findings. The explicitly selected compact lab route
has six landmarks, thirty ordered pairs and ten 100-ms cue bins. Its archive contains
195 units/58 sessions; the current eligible complete-support panel has 27 units/10
blocks. Archived scope and analyzed cohort are different counts. Current source cells
have no saved execution outputs; run this non-fitting chapter to obtain its diagnostics.

By the end, you should be able to trace one count to a spike window, explain why a
missing recording is not silence, reconstruct a synthetic row from its sources, and
explain why equal class counts do not imply equal independent evidence.

### From a recording to a research claim

A **unit** is a sorted spike train, a **source** is a real recorded trial, a **block**
is the group whose unit columns are copied together, and a **pseudotrial** is a new
row assembled from several sources sharing a known condition. For an ML analogy,
think of joining feature groups from different documents because they share a label:
the joined vector is useful for a conditional assay, but never existed as one document.

Here the conditions are ordered `(start, goal)` pairs. The target is condition-level
endpoint information in cue counts; the original beyond-endpoint path hypothesis
requires a different target. The finest provenance unit is the source trial, with
predecessor dependencies and nesting in sessions. Neither pseudorows nor time bins
are independent biological replicates.

`spike times → event-aligned counts → source split/selection → condition pools →
intact block draws → pseudopopulation → train-only transforms → readout`

The split and selection use metadata before neural reconstruction; the arrow above
describes the data objects, not permission to inspect all neural values before splitting.
The code below installs a fitting guard across the entire chapter.
""",
        "## Explicit metadata": r"""## 1. Establish identity and labels before opening neural arrays

We need to know what a row *means* before considering whether a model can classify it.
Hash authentication detects changed inputs; it does not validate the task interpretation.
Metadata joins establish trial order, event agreement, eligibility and historical split.
The compact source includes unsuccessful and inconsistent records so exclusions can
be accounted for, rather than silently deleting inconvenient trials.

The development split has already informed earlier work. We call it **exposed
development**, not an untouched test set. Source disjointness blocks direct reuse
across splits but cannot undo that historical exposure or remove all session effects.
The assertions below verify mechanical prerequisites; they do not certify the biology.
Missing supplied inputs fail rather than switching to invented examples.
""",
        "## A worked target": r"""## 2. Derive a target and expose the assumption it depends on

The working rule takes the preceding successful trial's goal digit as the current
start, and the current marker's goal digit as the current goal. For example, previous
goal `2` and current goal `3` yield pair `2→3`. The arrows encode order, not a distance
between poster IDs. The source must pass the successful-adjacent-trial and multimodal
event checks. A label derived this way is still **provisional task semantics**;
matching codes across systems is not an independent behavioral validation.

This predecessor rule creates a less obvious leakage route: if trial `t` contributes
to the label of `t+1`, separating their spike counts is insufficient. The contributor
embargo removes training sources whose own or predecessor ID occurs in the union of
development contributors, globally before choosing the complete-support panel.
The example below prints labels and checks, with the complete source ledger saved
locally. Explain both the derivation and its dependency before accepting the target.
""",
        "## Inventory, eligibility": r"""## 3. Is the cohort support sufficient, and what did selection remove?

For every retained block, every declared pair must have training and development
support. Otherwise a purported population row would need an unobserved unit/condition
response. We exclude blocks without the prescribed complete support; we never fill
that hole with zero. For the later half-source experiment, each training pool also
needs at least two sources before reduction. These are feasibility requirements, not
evidence that two trials are scientifically sufficient.

Read the maps in sequence: archive inventory → eligible outer-training sources →
contributor embargo → retained complete-support blocks. The pair-map diagonal is
structurally absent (`start == goal` is not one of the task conditions); a zero
off-diagonal cell is missing support. The block-by-pair maps retain zeros even for
blocks that are excluded later, making survivorship visible.

**Selection changes the estimand.** Results describe the retained place-selected
units and supported conditions. They do not describe all recorded hippocampal cells,
all sessions, animals, or the natural frequency of routes. The lab compact archive
and historical 195-unit endpoint result are therefore not interchangeable cohorts.
""",
        "## Fresh neural": r"""## 4. Turn timestamps into counts without inventing observations

The compact files retain native spike timestamps in milliseconds and Ripple event
times in seconds. After explicit clock conversion, a cue bin counts spikes in an
absolute half-open window `[onset + edge_i, onset + edge_(i+1))`: a spike exactly on
the right edge belongs in the next bin. Repeated timestamps remain repeated events;
the reader does not sort away or deduplicate measurements. Counts are dimensionless;
dividing by observed exposure in seconds gives rates in spikes/s.

The concrete tensor is `source × unit × bin`. A source records only its own block's
units. Off-block entries remain masked/NaN, not zero. A zero in an observed bin means
no detected spikes in that recorded interval. These cases would have radically
different meanings to a classifier if both were encoded as zero.

Native-precision counts can differ from historical rounded CSV counts near boundaries.
Fresh reconstruction is not a promise to reproduce old fitted scores bit for bit.
The load step checks timing, observation, exposure and contributor identity. Whole-file
authentication traverses the supplied bytes; it is not a claim of physical non-reading
of other timestamps stored in the same file.
""",
        "## One raw spike": r"""### Work one binning example by hand

In compact mode, the next cell retrieves one selected unit's unbinned train and
reconstructs the same counts independently through the declared boundary function.
The lab cue has ten 100-ms bins; the invented fixture uses four bins. `tail` records
spikes in any cue portion beyond the declared bin edges. Counts plus that tail must
account for the whole selected cue, without claiming that time outside the cue vanished
from the source archive. In invented mode there are no raw timestamps to demonstrate;
the observation/zero checks still run.
""",
        "## An intact assembled": r"""## 6. Construct one synthetic row, preserving the block's measured features

Let `P(block, pair, split)` be the eligible real-trial pool. For each synthetic row of
pair `c`, independently draw **one source per block** with replacement from that
block's pool. Copy all its unit columns and cue bins together. Concatenating these
blocks yields `row × unit × bin`; its label is the condition used to select the pools.

This preserves the recorded within-source block structure without claiming verified
simultaneity, cross-session noise covariance, or a real whole-population trajectory.
Never draw each neuron or time bin independently: that would destroy more structure.
The plan is an explicit recipe, so rematerializing it must reproduce every value.

Known labels are used even to construct development rows. The question is therefore
whether condition-matched responses are separable using source-disjoint measurements.
It is not the accuracy of decoding an unknown-label, naturally recorded trial. CEBRA's
Time objective later omits labels, but this upstream conditional construction still
uses them. Keeping that distinction visible is essential to a defensible claim.
""",
        "## Eligible / used": r"""## 7. Does balanced assembly conceal source reuse?

The sampler requests the same number of pseudorows per pair. This changes the class
prior by design; it does not balance the amount of recorded evidence. A small pool
must be reused more often than a large pool. The next display separates eligible,
used, unused and repeated real sources. A tall reuse tail identifies dependence and
potential sensitivity to individual sources, not additional neural observations.

For a pool with `m` real sources and `R` replacement draws, expected source reuse is
`R/m` and the expected number of distinct sources is
`m × [1 − (1 − 1/m)^R]`. Even indefinitely increasing `R` cannot produce more than `m`
distinct measurements. Seeds vary which sources are reused; their variation is
computational variation, not a biological confidence interval.
""",
        "## Interpretation limits": r"""## 8. What have we established, and what remains a scientific assumption?

Passing the reconstruction and overlap checks establishes that this particular
condition-level assay can be materialized under its declared policy. It does not
prove that cross-session responses are exchangeable conditional on `(start, goal)`.
Behavior, gaze, speed, previous-trial history and session drift can still covary with
those endpoints. The compact source intentionally omits dense behavior/gaze, so this
notebook cannot settle those confounds or construct a verified ordered-route target.

**Decision:** proceed to a bounded exploratory endpoint comparison only with its
selected-cohort, known-condition and exposed-development qualifiers. Stop and repair
the contract if a required pool is empty, contributors cross splits, timing is unknown,
or missing recordings were treated as zero. More synthetic rows cannot repair these.

Before handing this chapter on, answer in your own words:

1. Which observed source and time window supplied one block of the first pseudorow?
2. Which block/condition has least evidence, and which session supplies most columns?
3. Why can equal synthetic class counts coexist with heavily unequal source support?
4. What evidence would be needed to make a same-trial population-state claim?

Next, [Notebook 2](02_pca_lda.ipynb) asks what simple readouts recover, and
[Notebook 3](03_cebra.ipynb) asks whether CEBRA adds useful structure. The final cell
records zero fits and authenticates the saved construction. Provenance makes the
computation auditable; it is separate from formal neural-state observability.
""",
    }
    result = []
    for cell in cells:
        source = "".join(cell["source"])
        if cell["cell_type"] == "markdown":
            for prefix, replacement in replacements.items():
                if source.startswith(prefix):
                    cell = md(replacement)
                    break
        elif "print('All original block/pair training support" in source:
            source = source.replace(
                "print('All original block/pair training support (zeros retained):', block_support.tolist())",
                """fig, axes = plt.subplots(1, 2, figsize=(14, max(4, len(blocks) * .12)), constrained_layout=True)
for ax, split in zip(axes, ('train', 'development')):
    matrix = np.array([[pools[block, pair, split] for pair in pairs] for block in blocks])
    image = ax.imshow(matrix, aspect='auto', vmin=0)
    fig.colorbar(image, ax=ax, label='Real sources after contributor embargo')
    ax.set(title=split + ': all eligible blocks, including excluded blocks', xlabel='Ordered pair', ylabel='Pseudonymous block index', xticks=range(len(pairs)), xticklabels=pairs)
    ax.tick_params(axis='x', labelrotation=90)
display(fig); plt.close(fig)""",
            )
            cell = code(source)
        result.append(cell)
        if cell["cell_type"] == "code" and "fig = plot_input_audit(" in source:
            result.extend([md(SKEW_PROSE), code(SKEW_CODE), md(SKEW_READING)])
        if cell["cell_type"] == "code" and "store.save('construction_assembly'" in source:
            result.extend([md(LINEAGE_PROSE), code(LINEAGE_CODE)])
        if cell["cell_type"] == "code" and "usage = usage_summary(data, assembly)" in source:
            result.extend([code(BALANCE_CODE), md(BALANCE_READING)])
    return result


SKEW_PROSE = r"""## 5. Audit three different kinds of skew

**Class skew:** how many real sources support each pair in each split? **Pool skew:**
is support spread across blocks or carried by very few trials in one block?
**Feature skew:** which blocks supply most unit columns? Standardizing a unit does
not equalize the number of units supplied by each session.

The next cell measures all three before assembly. The ratios/CVs are descriptions,
not pass/fail cutoffs chosen after seeing scores. A low CV does not remove confounding;
a high one suggests a sensitivity question for the source ablation later. The average
rate plot distinguishes changing activity magnitude from changing class counts. These
are source-level rates, each averaged over that source's observed units/bins, with
exposure converted explicitly to seconds. They are not equal-weight animal summaries.
"""

SKEW_CODE = """from IPython.display import Markdown
def show_table(headers, rows):
    display(Markdown('| ' + ' | '.join(headers) + ' |\\n| ' + ' | '.join(['---'] * len(headers)) + ' |\\n' +
                     '\\n'.join('| ' + ' | '.join(map(str, row)) + ' |' for row in rows)))

conditions = [c for c, _ in data.target_definition.condition_to_target]
source_by_condition = {split: Counter(t.condition for s, t in zip(data.sources, data.targets) if s.split_id == split)
                       for split in ('train', 'development')}
pool_rows = support(data)
skew_rows = []
for split in ('train', 'development'):
    counts = np.array([r['source_count'] for r in pool_rows if r['split_id'] == split])
    skew_rows.append([split, int(counts.sum()), int(counts.min()), int(counts.max()),
                      round(float(counts.std() / counts.mean()), 3), int(np.sum(counts == 0))])
show_table(['Split', 'Real sources', 'Smallest pool', 'Largest pool', 'Pool CV', 'Empty pools'], skew_rows)
unit_counts = Counter(u.block_id for u in data.units)
show_table(['Block alias', 'Unit columns', 'Column share', 'Train sources', 'Dev sources'],
           [[f'block_{i+1:02d}', unit_counts[b], f'{unit_counts[b]/len(data.units):.1%}',
             sum(s.block_id == b and s.split_id == 'train' for s in data.sources),
             sum(s.block_id == b and s.split_id == 'development' for s in data.sources)]
            for i, b in enumerate(data.block_ids)])
fig, axes = plt.subplots(1, 3, figsize=(16, 4), constrained_layout=True)
x = np.arange(len(conditions))
for split, shift in (('train', -.2), ('development', .2)):
    axes[0].bar(x + shift, [source_by_condition[split][c] for c in conditions], .4, label=split)
axes[0].set(title='Selected source support, before resampling', xlabel='Pair', ylabel='Real sources', xticks=x, xticklabels=conditions)
axes[0].tick_params(axis='x', labelrotation=90); axes[0].legend()
axes[1].bar(range(len(data.block_ids)), [unit_counts[b] for b in data.block_ids])
axes[1].set(title='Session/block contribution to feature space', xlabel='Block index', ylabel='Unit columns')
seconds = data.exposure * (1 if data.time_unit == 's' else .001)
rates = data.values / seconds[:, None, :] if data.value_unit == 'count' else data.values
source_mean_rates = np.nanmean(rates, axis=(1, 2))
rate_edges = np.histogram_bin_edges(source_mean_rates, bins=12)
for split in ('train', 'development'):
    selected_rates = source_mean_rates[[s.split_id == split for s in data.sources]]
    axes[2].hist(selected_rates, bins=rate_edges, alpha=.5, label=split)
axes[2].set(title='Observed activity magnitude by source', xlabel='Mean spikes/s across recorded units and bins', ylabel='Real sources'); axes[2].legend()
display(fig); plt.close(fig)
print('Complete support is a construction requirement, not a test of representativeness.')"""

SKEW_READING = r"""**Read the evidence:** the pool minimum identifies the weakest block/condition;
the block-column table shows which sessions carry greatest feature weight. Compare
training and development class profiles before looking at synthetic balance. Similar
rate histograms are only a coarse check: condition-specific drift can remain even
when marginal histograms overlap. Different histograms call for diagnosis, not automatic
normalization across both splits. Any learned correction must be fitted on training only.
"""

LINEAGE_PROSE = r"""### Make the recipe inspectable, not just hashable

Below, pseudonymous aliases identify the source selected for each block of the first
row. The displayed label, source split and copied-unit count can be inspected directly;
the numerical equality assertion verifies the corresponding tensor slice. We then
construct development separately and audit the union of source and predecessor IDs.
The aliases are local teaching labels, not new biological identities.
"""

LINEAGE_CODE = """source_index = {s.source_id: i for i, s in enumerate(data.sources)}
source_alias = {s.source_id: f'source_{i+1:04d}' for i, s in enumerate(data.sources)}
lineage_rows = []
for bi, (block, sid) in enumerate(zip(data.block_ids, plan.rows[0].source_ids)):
    si = source_index[sid]
    ui = [i for i, u in enumerate(data.units) if u.block_id == block]
    np.testing.assert_array_equal(assembly.values[0, ui], data.values[si, ui])
    lineage_rows.append([f'block_{bi+1:02d}', source_alias[sid], data.sources[si].split_id,
                         data.targets[si].condition, len(ui), data.values.shape[2]])
show_table(['Block', 'Source alias', 'Split', 'Pair', 'Copied units', 'Copied bins'], lineage_rows)
development_plan = sample_plan(data, split_id='development', rows_per_condition=settings['development_rows_per_condition'], seed=0, effective_conditions=effective)
development_assembly = materialize(data, development_plan)
def contributor_ids(constructed):
    ids = {sid for row in constructed.plan.rows for sid in row.source_ids}
    return ids | {dependency for sid in ids for dependency in data.sources[source_index[sid]].dependency_ids}
overlap = contributor_ids(assembly) & contributor_ids(development_assembly)
assert not overlap
print('Train/dev contributor intersection:', len(overlap), '| train shape:', assembly.values.shape,
      '| development shape:', development_assembly.values.shape, '| no learned transformations')"""

BALANCE_CODE = """fig, axes = plt.subplots(1, 2, figsize=(13, 4), constrained_layout=True)
for ax, split, built in zip(axes, ('train', 'development'), (assembly, development_assembly)):
    real = np.array([source_by_condition[split][c] for c in conditions], dtype=float)
    synthetic = Counter(built.targets)
    created = np.array([synthetic[dict(data.target_definition.condition_to_target)[c]] for c in conditions], dtype=float)
    ax.bar(x - .2, real / real.sum(), .4, label='Real-source class fraction')
    ax.bar(x + .2, created / created.sum(), .4, label='Pseudorow class fraction')
    ax.set(title=split + ': real-source versus constructed class fractions', xlabel='Pair', ylabel='Fraction within split', xticks=x, xticklabels=conditions)
    ax.tick_params(axis='x', labelrotation=90); ax.legend(fontsize=8)
display(fig); plt.close(fig)
show_table(['Split', 'Pseudorows', 'Eligible real sources', 'Used', 'Unused', 'Used repeatedly'],
           [[split, len(built.plan.rows), summary['eligible_sources'], summary['used_sources'], summary['unused_sources'], summary['repeated_sources']]
            for split, built in [('train', assembly), ('development', development_assembly)]
            for summary in [usage_summary(data, built)]])"""

BALANCE_READING = r"""**Answer to “is this pseudopopulation skewed?”** Read two different answers
from these panels: constructed class frequencies are balanced by policy, while source
support, reuse and session/unit contributions can be unequal. A balanced class prior
makes a conditional classifier comparison easier; it does not recreate natural trial
prevalence or erase the selection process. Both full and reduced-source model runs
will use the same development recipe, so their comparison does not silently change
the evaluation samples while changing training support.
"""
