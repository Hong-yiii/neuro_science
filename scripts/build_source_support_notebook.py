"""Build the explicit training/evidence notebook for the bounded November study."""

from __future__ import annotations

import nbformat


def make_notebook():
    md = nbformat.v4.new_markdown_cell
    code = nbformat.v4.new_code_cell
    cells = [
        md("""# Learning, source support and pseudopopulation sampling

**New exploratory biological training · November 10, 2026.** This notebook trains
the frozen comparison and retains all its outputs. It uses existing cue recordings,
not newly recorded biological data. The supplied compact source, frozen protocol,
code identities, private model states and aggregate report form its evidence chain.

The question is whether endpoint learning persists when we reduce the condition
set, include more recorded columns, balance real-trial reuse, or assemble each
current training source only once. These tests address different mechanisms;
they do not establish simultaneous population covariance or natural unknown-label
prediction. Development was historically exposed.

The nine-pair task is **starts 2,3,5 × goals 1,4,6**. Disjoint sets avoid the absent
start=goal combinations. Metadata, not neural performance, chose this rectangle.
All twenty possible disjoint rectangles are shown, including minimum-five failure.

Execution is deliberately gated: run through the task-owned runner with its pinned
configuration, reviewed code and resource cap. Reading the saved notebook requires
neither private historical results nor a model runtime.
"""),
        code("""from pathlib import Path
import os, json, inspect, html, base64
import numpy as np
from IPython.display import display, HTML, Image
from neuro.studies import source_support_ablation as study
from neuro.notebook_artifacts import no_fitting, runtime_identity, stable_kernel_identity
from scripts.source_support_report import table, create_report

PROJECT = Path(os.environ['NEURO_PROJECT_ROOT'])
RUN = Path(os.environ['NEURO_SUPPORT_RUN'])
config = json.loads((RUN / 'configuration.json').read_text())
assert config == study.frozen_configuration()
pins = json.loads((RUN / 'code-pins.json').read_text())
assert all(study.sha(PROJECT / path) == digest for path, digest in pins.items())
identity = runtime_identity()
assert stable_kernel_identity(identity) == stable_kernel_identity(json.loads((RUN / 'runtime.json').read_text()))
study.write_json(RUN / 'kernel-runtime.json', identity)
print('Classification:', config['classification'])
print('Runtime versions:', identity['packages'])
print('Planned actual fit counts, excluding scalers:', config['expected_fit_counts'])
print('Code files authenticated:', len(pins))
"""),
        md("""## 1. Establish source support before opening spike arrays

Keep current/predecessor contributors separated across folds. The full original
development contributor union is protected before any class/session selection.
Fewer classes cannot reclaim embargoed sources. We compare source eligibility,
distinct sources actually drawn, synthetic rows and unit columns separately.
"""),
        code("""with no_fitting(cebra=True):
    metadata = study.inventory(PROJECT / 'data/cue-source-v1')
study.write_csv(RUN / 'metadata_rectangles.csv', metadata['rectangles'])
print('Global development contributor IDs protected:', len(metadata['protected']))
display(HTML(table(metadata['rectangles'])))
print('Chosen current/wide/supported session counts:', {k: len(v) for k, v in metadata['cohorts'].items()})
"""),
        md("""## 2. Reconstruct native cue measurements, retaining provenance

Selected-unit spike timestamps are counted in ten half-open100-ms intervals over
the first cue second. Zero is observed silence; other sessions' unrecorded columns
remain masked. The compact adapter regenerates historical eligibility and frozen
splits, authenticates public inputs, and checks selected Eye events. This stage
fits no model and reads no old model/result files.
"""),
        code("""with no_fitting(cebra=True):
    data, reconstruction_audit = study.reconstruct(PROJECT / 'data/cue-source-v1', metadata)
study.write_json(RUN / 'reconstruction_audit.json', reconstruction_audit)
panel_rows = []
for name, source in data.items():
    panel_rows.append({'panel': name, 'units': len(source.units), 'sessions': len(source.block_ids),
        'training_sources': sum(s.split_id == 'train' for s in source.sources),
        'development_sources': sum(s.split_id == 'development' for s in source.sources),
        'bins': source.values.shape[2], 'contributor_overlap': len(source.dependency_audit()['overlapping_contributor_ids'])})
display(HTML(table(panel_rows)))
print('Spike conservation accounting:', {k: {f: v for f, v in a.items() if f in ('events_accepted','tail_spikes','observed_values')} for k, a in reconstruction_audit.items() if k in ('current','wide')})
"""),
        md("""## 3. Freeze the eight arms and matched evaluation

| Arm | Classes/columns/sessions | Training assembly |
|---|---|---|
| A |30/27/10|16 rows/class with replacement|
| B |9/27/10|C's plan projected onto the reference columns|
| C |9/144/43|16 rows/class with replacement|
| D |9/43/43|C's plan, one fixed recorded column per session|
| E |9/80/20|C's plan restricted to pools with at least three training trials|
| F |9/80/20|16 rows/class with balanced source counts|
| G |9/80/20|Three sources/pool, three rows/class; each source used once|
| H |9/80/20|Same three sources as G;15 recombined rows/class, five uses/source|

B–H share widest-panel development blocks projected onto their columns, eight
rows/class, seed0. B/C/D/E also share training blocks within computational seed.
G/H have identical real-source sets. Unique assembly does not remove optimizer,
time-bin, serial or predecessor dependence.

Primary pair9 comparisons are **C−D**, **F−E**, **H−G**. A/B and C/E change multiple
design properties and are descriptive. This is not a search for a winning panel.
"""),
        code("""with no_fitting(cebra=True):
    first_plans = study.plans(data, seed=0)
    assert study.check_pairing(first_plans)
    arm_rows = []
    for arm, (source, training, development) in first_plans.items():
        n = len(training.rows)
        k = len(source.target_definition.condition_to_target)
        arm_rows.append({'arm': arm, 'units': len(source.units), 'train_rows': n,
            'development_rows': len(development.rows), 'policy': training.policy,
            'logistic_C': 0.01 * 16 * k / n})
display(HTML(table(arm_rows)))
del first_plans
"""),
        md("""## 4. Inspect the actual fitting and verification computation

All scaler/PCA/encoder/readout fitting uses training inputs. PCA and CEBRA produce
eight coordinates per bin, concatenated over ten bins. CEBRA-Time uses native adjacent
bins in the same constructed row,1,000updates and a pointwise offset1 network.
Raw, PCA and CEBRA feed separate logistic readouts; raw SVD-LDA is descriptive.

Logistic regularization uses `C_eff=0.01*(16*K)/N_train`, keeping `N_train*C_eff`
fixed within the nine-class task. Otherwise duplicating rows would inadvertently
change the summed-loss penalty. This does not make synthetic rows independent.

The expandable listing is the exact current training function, covered by code pins.
It includes new state saving and composed encoder→readout replay on both splits
with fitting and optimizer updates blocked.
"""),
        code("""display(HTML('<details><summary>Exact implementation: train_case</summary><pre>' + html.escape(inspect.getsource(study.train_case)) + '</pre></details>'))
"""),
        md("""## 5. Train every declared observed and shuffled case

Observed seeds0,1,2 cover all eight arms. Five frozen label permutations50000–50004
cover A/E/G at model seed0. Pair labels are permuted within session×split before
source-subset selection and assembly; start/goal derive jointly. Development is
fixed within each world. These are diagnostic controls, not calibrated biological
p-values. Every attempt and actual fit/update count is retained; no automatic retry.
"""),
        code("""results = study.run_grid(data, metadata, config, RUN)
actual_counts = json.loads((RUN / 'actual-fit-counts.json').read_text())
assert actual_counts == config['expected_fit_counts']
print('Actual completed fits:', actual_counts)
print('Readout results:', len(results['metrics']))
print('Observed cases:24; source-label diagnostic cases:15')
"""),
        md("""## 6. Collate aggregate evidence into the report

The report contains every scalar row, count/normalized confusion, CEBRA loss curve
and observed class-mean cue-time trajectory. CSV/JSON tables accompany figures.
Explicit source/row joins remain authenticated; the readable artifacts use aliases.
Session exclusion and evaluated prediction error remain separate quantities.
"""),
        code("""report = create_report(results, metadata, RUN / 'report', config=config, reconstruction_audit=reconstruction_audit)
print('Standalone report generated; figure count:', len(report['figures']))
display(HTML(table(report['summary'])))
display(HTML(table([r for r in report['contrasts'] if r['head'] == 'pair'])))
"""),
        md("""## 7. Support, reuse, performance and controls

Dots/ranges show computational seeds, never biological confidence intervals.
Uniform references are1/30 or1/9 for pair readouts,1/6 or1/3 for endpoint readouts.
Log loss is in natural-log units; lower is better. All fitted families, including
poor LDA losses, remain visible. Support/error associations can reflect class
difficulty and endpoints; they do not identify a causal bad neuron or session.
"""),
        code("""def show_group(group, collapsible=False):
    for figure in report['figures']:
        if figure['group'] != group:
            continue
        path = RUN / 'report' / figure['file']
        assert study.sha(path) == figure['sha256']
        if collapsible:
            encoded = base64.b64encode(path.read_bytes()).decode()
            display(HTML('<details><summary>' + html.escape(path.stem) + '</summary><img style="max-width:100%" src="data:image/png;base64,' + encoded + '"><p>' + html.escape(figure['caption']) + '</p></details>'))
        else:
            display(Image(filename=str(path)))
            display(HTML('<p>' + html.escape(figure['caption']) + '</p>'))
show_group('overview')
"""),
        md(
            "## 8. Every CEBRA learning curve\n\nTraining InfoNCE loss records optimization. It is not a held-out decoding metric."
        ),
        code("show_group('learning')"),
        md("""## 9. All observed cue-time trajectories

These are class means across constructed development rows, plotted in the first
three coordinates of the existing eight-dimensional PCA/CEBRA representation.
Ten bin centers run50–950ms; circles start and triangles end each path. All observed
arms/seeds are retained below. Models are fitted independently and axes are not
aligned. The plots do not show actual maze movement, simultaneous neural dynamics
or formal state observability. A smooth or separated path is not itself evidence
of useful learning; use the readout and control results.
"""),
        code("show_group('trajectories', collapsible=True)"),
        md(
            "## 10. Every count and normalized confusion matrix\n\nExpand a case/head to inspect every model family. Numeric matrices are also exported."
        ),
        code("show_group('confusions', collapsible=True)"),
        md("""## 11. Verification and claim boundary

Successful fitting establishes that this declared computational assay ran. Performance
above the shuffled diagnostics, especially in G, can show recoverable condition
information without repeated current-source blocks in training assembly. It cannot
establish independent biological replication, simultaneous covariance, unknown-label
trial prediction, or that all pseudopopulation methods are valid. Balanced allocation
and recombination contrasts have the narrower meanings declared above.

Development contains singleton pools and remains label-conditioned and historically
exposed. Five shuffles do not support a formal p-value. This notebook preserves both
positive and negative results, with no post-result model or panel tuning.
"""),
        code("""assert all(study.sha(PROJECT / path) == digest for path, digest in pins.items())
accounting = json.loads((RUN / 'aggregates/fit_accounting.json').read_text())
assert accounting['counts'] == config['expected_fit_counts']
assert accounting['cases'] == 39
print('Completed cases:', accounting['cases'])
print('Composed saved-pipeline split checks:', accounting['composed_readout_splits_checked'])
print('Saved encoder checks:', accounting['reloaded_encoders_checked'])
print('All primary/secondary metrics, failures ledger, figure provenance and explicit lineage retained.')
print('Scientific status: exploratory; independent result review follows this execution.')
"""),
    ]
    return nbformat.v4.new_notebook(
        cells=cells,
        metadata={
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {"name": "python"},
            "study": "source-support-ablation-20261110",
        },
    )


if __name__ == "__main__":
    nbformat.write(make_notebook(), "notebooks/05_source_support_ablation.ipynb")
