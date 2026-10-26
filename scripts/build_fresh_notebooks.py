"""Build the research guide and three teaching notebooks; no neural data or fits."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def md(text):
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": text.strip().splitlines(keepends=True),
    }


def code(text):
    return {
        "cell_type": "code",
        "metadata": {},
        "source": text.strip().splitlines(keepends=True),
        "execution_count": None,
        "outputs": [],
    }


COMMON = """import json, os, sys, time, warnings
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from IPython.display import display
from IPython import get_ipython
get_ipython().run_line_magic('matplotlib', 'inline')
from neuro.notebook_inputs import configuration_from_environment, inspect_inputs, load_inputs, effective_pair_map
from neuro.pseudopopulation import sample_plan, materialize, support
from neuro.notebook_artifacts import ArtifactStore, FitAccounting, target_heads, write_private_json, verify_artifacts, runtime_identity, validate_kernel_identity
from neuro.notebook_support import workspace, usage_summary, source_budget, checked_assemblies, compact_metrics, plot_confusions

configuration = configuration_from_environment()
settings = configuration['execution']
output = workspace()
def private_warning(message, category, filename, lineno, file=None, line=None):
    # Preserve full provenance privately; do not render host paths in shared figures/output.
    warning_path = output / 'warnings-private.jsonl'
    with warning_path.open('a') as handle:
        handle.write(json.dumps({'message': str(message), 'category': category.__name__, 'filename': filename, 'lineno': lineno}) + '\\n')
    warning_path.chmod(0o600)
    print(category.__name__ + ': ' + str(message), file=sys.stderr)
warnings.showwarning = private_warning
store = ArtifactStore(output / 'artifacts')
store.save('configuration', configuration)
store.save('kernel_runtime_before_inputs', validate_kernel_identity(configuration))
print('Input mode:', configuration['mode'], '| exploratory computational assay; no biological IID inference')"""
INSPECT = """inspection = inspect_inputs(configuration)  # Metadata/hash step only for supplied inputs.
store.save('metadata_selection', inspection)  # Protected provenance; never displayed.
print(json.dumps(inspection.audit, sort_keys=True))
assert inspection.audit['contributor_overlap'] == 0
assert inspection.audit['selected_train'] > 0 and inspection.audit['selected_development'] > 0"""
LOAD = """data, neural_audit = load_inputs(inspection)  # Supplied neural path remains explicitly review-gated.
store.save('source_data', data)
store.save('neural_audit', neural_audit)
print(json.dumps(neural_audit, sort_keys=True))
assert np.isfinite(data.values[data.observed]).all()
assert np.isnan(data.values[~data.observed]).all()
assert not data.dependency_audit()['overlapping_contributor_ids']
print('Source × unit × bin shape:', data.values.shape, '| units:', data.value_unit, '| clock units:', data.time_unit)"""
LIMIT = """## Interpretation limits
These are source-safe conditional pseudopopulations, not simultaneous trials. Matching uses known labels; this is not an unknown-trial prediction pipeline. Bins, synthetic rows and computational seeds are dependent. Place-selected units, provisional marker meaning, inherited preprocessing and historical exposure remain limitations. Contributor separation does not remove long-range serial/session confounds. No biological confidence intervals, p-values, mechanism, dynamics or prospective-path claim follows from these figures. The permutation diagnostic is alignment-breaking, not a biological exchangeability test."""


def finish(expected):
    return code(f"""fit_counts = accounting.stop()
store.save('kernel_runtime_final', runtime_identity())
expected_counts = {expected}
manifest_hash = store.finish(fit_counts=fit_counts, expected_counts=expected_counts)
replay = verify_artifacts(output / 'artifacts', expected_manifest_hash=manifest_hash)
write_private_json(output / 'completion.json', {{'manifest_sha256': manifest_hash, 'fit_counts': fit_counts, 'replay': replay}})
print(json.dumps(replay, sort_keys=True))
assert replay['status'] == 'fit-blocked-loaded-model-replay-passed' """)


def build():
    if __package__:
        from .notebook_construction_guide import enrich_construction_notebook
        from .notebook_model_guide import enrich_model_notebooks
        from .notebook_research_guide import research_guide
    else:
        from notebook_construction_guide import enrich_construction_notebook
        from notebook_model_guide import enrich_model_notebooks
        from notebook_research_guide import research_guide

    common = [
        code(COMMON),
        md(
            "## Explicit metadata and target boundary\nAuthenticate only supplied files, regenerate eligibility/assignments, freeze the contributor embargo and complete-support panel before neural interpretation. The public default is invented data. Missing supplied inputs fail; no demo or historical-result fallback."
        ),
        code(INSPECT),
    ]
    a = [
        md(
            "# 1 — Construct and audit a pseudopopulation\nFresh source-level computation. Public default: invented three-landmark/six-pair data. Supplied-data mode uses an explicit protected manifest and requires independent execution approval. No model fitting."
        ),
        *common,
        md(
            "## A worked target derivation\nPrevious/current successful adjacent-trial marker digits give provisional start/goal. The adapter checks multimodal triplets, importer agreement, QC and eligibility. Only a pseudonymous worked example is printed; the full joined derivation/exclusions remain protected."
        ),
        code("""example = inspection.selected[0]
worked = {'example': 'source_example', 'previous_marker_digit': example['start'], 'current_marker_digit': example['goal'],
          'derived_pair': f"{example['start']}->{example['goal']}", 'status': 'derived/provisional, not independently measured truth'}
print(json.dumps(worked))
assert worked['derived_pair'] == example['condition']
print('Exclusion waterfall:', json.dumps(inspection.audit['exclusion_counts'], sort_keys=True))"""),
        md(
            "## Inventory, eligibility and support are different questions\nCompact source mode retains all records, including failed/mismatched trials. The historical outer-train gate, frozen development labels and global predecessor-contributor embargo apply only to consumption. Eye masked placeholders are never observed events. Metadata summaries do not create a pristine holdout."
        ),
        code("""from collections import Counter
landmarks = configuration['landmarks']
pair_counts = Counter(s['condition'] for s in inspection.eligible)
selected_counts = Counter(s['condition'] for s in inspection.selected)
print('Before/after source counts:', len(inspection.eligible), len(inspection.selected))
print('Input inventory:', {k: inspection.audit[k] for k in ('exported_trials', 'exported_units', 'unity_timing_rows', 'native_eye_missing_events') if k in inspection.audit})
print('Metadata all-record outcomes (historically exposed, not a holdout):', inspection.audit.get('all_record_outcomes', {}))
for title, counts in [('Eligible outer-train ordered pairs', pair_counts), ('Selected ordered pairs', selected_counts)]:
    matrix = np.array([[counts[f'{a}->{b}'] for b in landmarks] for a in landmarks])
    print(title, '(rows=start, columns=goal; diagonal/unsupported cells remain zero):'); print(matrix)
    fig, ax = plt.subplots(figsize=(5, 4)); image = ax.imshow(matrix); fig.colorbar(image, ax=ax, label='Real source trials')
    ax.set(xticks=range(len(landmarks)), xticklabels=landmarks, yticks=range(len(landmarks)), yticklabels=landmarks, xlabel='Goal', ylabel='Start', title=title)
    display(fig); plt.close(fig)
# Every original block/pair appears, including zero surviving training support.
eligible = inspection.eligible
contributors = {sid for s in eligible if s['split_id'] == 'development' for sid in (s['source_id'], s['previous_id'])}
surviving = [s for s in eligible if s['split_id'] == 'development' or not {s['source_id'], s['previous_id']} & contributors]
pools = Counter((s['block_id'], s['condition'], s['split_id']) for s in surviving)
blocks = sorted({s['block_id'] for s in eligible})
pairs = [f'{a}->{b}' for a in landmarks for b in landmarks if a != b]
block_support = np.array([[pools[block, pair, 'train'] for pair in pairs] for block in blocks])
print('All original block/pair training support (zeros retained):', block_support.tolist())
print('Predecessor edges:', inspection.audit.get('directed_edges', {}))
print('Development contributor union / embargo removed:', len(contributors), inspection.audit['embargo_removed_train'])
if inspection.place195_selection is not None:
    joined = inspection.place195_selection.trials[example['source_id']]
    print('Worked marker join:', {k: joined[k] for k in ('ripple_codes', 'unity_codes', 'eyelink_codes', 'eye_observed', 'outcome', 'qc_flags') if k in joined})
    print('Native-precision cue seconds:', joined['ripple_cue_duration_s'])"""),
        md(
            "## Fresh neural measurements, observation and exposure\nThe compact adapter consumes only the selected outer-train panel, retains repeated native spikes, and uses explicit absolute half-open boundaries without the historical binning epsilon. Full-precision results need not equal old nine-significant-digit CSV results. The older six-file adapter retains its own conservation checks; neither route loads fitted results. Whole-file hashes traverse all supplied bytes, not physical non-reading."
        ),
        code(LOAD),
        md(
            "## One raw spike train → ten cue bins\nThe input stores unbinned native timestamps, not cached counts. The exact boundary policy is visible below; zeros are observed only within the source's recorded block, while off-block values remain masked/NaN."
        ),
        code("""if configuration['mode'] == 'compact':
    from neuro.cue_source import authenticate, exact_bins
    root, dataset_manifest = authenticate(inspection.place195_selection.manifest)
    first_source = inspection.selected[0]
    ui = next(i for i, u in enumerate(inspection.units) if u['session_id'] == first_source['block_id'])
    unit = inspection.units[ui]
    trial = inspection.place195_selection.trials[first_source['source_id']]
    with np.load(root / 'spikes.npz', allow_pickle=False) as archive:
        native_ms = archive[unit['key'] + '__timestamps']
    counts, tail, full = exact_bins(native_ms, trial['ripple_start_s'], trial['ripple_end_s'], data.bin_edges)
    np.testing.assert_array_equal(counts, data.values[0, ui])
    print('Cue edges (seconds from onset):', data.bin_edges.tolist())
    print('Fresh counts:', counts.tolist(), '| omitted cue tail:', tail, '| all cue spikes:', full)
print('Observed zero count bins:', int(np.sum(data.values[data.observed] == 0)))
print('Off-block unavailable bins:', int(np.isnan(data.values).sum()))"""),
        code("""from neuro.notebook_support import plot_input_audit
fig = plot_input_audit(inspection, data, neural_audit)
display(fig); plt.close(fig)
print('Selected block×condition×split support: min/max', min(r['source_count'] for r in support(data)), max(r['source_count'] for r in support(data)))"""),
        md(
            "## An intact assembled row and exact reconstruction\nOne source block supplies all of that block’s units and bins. Unit order is preserved. Plans bind observed input bytes separately from effective conditions. All ID-bearing lineage is saved privately."
        ),
        code("""effective = effective_pair_map(data, permutation_seed=None)
plan = sample_plan(data, split_id='train', rows_per_condition=settings['train_rows_per_condition'], seed=0, effective_conditions=effective)
assembly = materialize(data, plan)
reconstructed = materialize(data, assembly.plan)
np.testing.assert_array_equal(assembly.values, reconstructed.values)
np.testing.assert_array_equal(assembly.targets, reconstructed.targets)
store.save('construction_assembly', assembly)
print('Constructed rows:', len(plan.rows), '| intact blocks per row:', len(data.block_ids))
print('First row aliases:', {f'block_{i+1:02d}': 'contributing_source' for i in range(len(data.block_ids))})
fig, ax = plt.subplots(figsize=(8, 3))
illustration = assembly.values[0] if configuration['mode'] == 'invented' else np.nanmean(data.values, axis=0)
image = ax.imshow(illustration, aspect='auto'); fig.colorbar(image, ax=ax, label='Count per bin' if configuration['mode'] == 'invented' else 'Mean count per bin')
ax.set(xlabel='Native cue bin', ylabel='Stable unit index', title='Invented intact row' if configuration['mode'] == 'invented' else 'Aggregate unit/bin means across selected sources')
display(fig); plt.close(fig)"""),
        md(
            "## Eligible / used / unused / repeated source accounting\nThe constructed-row count is not an independent biological sample size."
        ),
        code("""usage = usage_summary(data, assembly)
print(json.dumps(usage, sort_keys=True))
fig, ax = plt.subplots(figsize=(6, 3)); ax.bar(list(usage['reuse_histogram']), list(usage['reuse_histogram'].values()))
ax.set(xlabel='Uses of a real source', ylabel='Real sources', title='Source reuse distribution')
display(fig); plt.close(fig)"""),
        md(LIMIT),
        finish(
            "{'pca': 0, 'logistic': 0, 'lda': 0, 'cebra': 0, 'optimizer_updates': 0}"
        ),
    ]
    b = [
        md(
            "# 2 — Fresh PCA and LDA baselines\nEach run independently rebuilds sources, targets, splits and assemblies. PCA is unsupervised pooled-bin full SVD with rank≥8. LDA is explicitly a supervised classifier, not a dimension-matched embedding. Full/reduced interventions refit all stages."
        ),
        *common,
        code(LOAD),
        md(
            "## Freeze development lineage before interventions\nObserved computational seeds 0/1 share development seed 0. Reduced training pools use a nested floor-half subset with fixed subset seed. No singleton fallback."
        ),
        code("""from neuro.pca_lda import fit_standardizer, raw_features, fit_pca, fit_lda
from neuro.notebook_support import fit_logistic
observed = effective_pair_map(data, permutation_seed=None)
dev_plan = sample_plan(data, split_id='development', rows_per_condition=settings['development_rows_per_condition'], seed=0, effective_conditions=observed)
reference_development = materialize(data, dev_plan)
store.save('fixed_development', reference_development)
accounting = FitAccounting().start()
results = []"""),
        md(
            "## Visible refit/readout grid\nRaw features retain unit-major ordering; PCA features are time-major. Both use training-only pooled-bin normalization. Readouts separately scale training features. Three explicit heads are pair/start/goal; logistic convergence and finiteness are mandatory."
        ),
        code("""for seed in settings['seeds']:
    for budget in ('full', 'reduced'):
        selected, effective = source_budget(data, observed, reduced=budget == 'reduced', subset_seed=settings['subset_seed'])
        train, development = checked_assemblies(selected, effective, dev_plan, reference_development, config=settings, seed=seed)
        key = f'observed_seed{seed}_{budget}'
        store.save_bundle(key, train, development)
        print(key, 'source accounting:', json.dumps(usage_summary(selected, train), sort_keys=True))
        standardizer = fit_standardizer(train.values)
        raw_train, raw_dev = raw_features(standardizer.transform(train.values)), raw_features(standardizer.transform(development.values))
        pca = fit_pca(train.values, n_components=settings['pca_components'])
        pca_train, pca_dev = pca.transform(train.values), pca.transform(development.values)
        store.save_encoder(key + '_raw', standardizer, kind='raw')
        store.save_encoder(key + '_pca', pca, kind='pca')
        print(key, 'PCA explained variance:', pca.pca.explained_variance_ratio_.round(4).tolist())
        run_results = []
        for representation, train_x, dev_x in (('raw', raw_train, raw_dev), ('pca', pca_train, pca_dev)):
            for head, y in target_heads(train).items():
                model = fit_logistic(train_x, y, C=settings['logistic_C'], max_iter=settings['logistic_max_iter'])
                row = store.readout(key + '_' + representation + '_' + head, model, encoder=key + '_' + representation,
                                    bundle=key, head=head, train_features=train_x, development_features=dev_x)
                run_results.append(row)
        for head, y in target_heads(train).items():
            model = fit_lda(raw_train, y)
            row = store.readout(key + '_lda_' + head, model, encoder=key + '_raw', bundle=key, head=head,
                                train_features=raw_train, development_features=raw_dev)
            run_results.append(row)
        results.extend(run_results)
        print(json.dumps(compact_metrics(run_results), sort_keys=True))
        fig = plot_confusions(run_results, title=key + ': development counts and row-normalized confusions')
        display(fig); plt.close(fig)
store.save('aggregate_metrics', results)"""),
        md(
            "## Training statistics and descriptive projection\nThe shown projection is not held-out predictive evidence; the numerical held-out scores and confusions above are the assay."
        ),
        code("""print('Last training pooled-bin mean/scale:', standardizer.scaler.mean_.round(3).tolist(), standardizer.scaler.scale_.round(3).tolist())
fig, ax = plt.subplots(figsize=(5, 3)); ax.scatter(pca_dev[:, 0], pca_dev[:, 1], s=6)
ax.set(xlabel='PC1, first cue bin', ylabel='PC2, first cue bin', title='Development projection (descriptive only)')
display(fig); plt.close(fig)
print('Uniform balanced-accuracy references:', {h: 1 / len(np.unique(y)) for h, y in target_heads(development).items()})"""),
        md(LIMIT),
        finish(
            "{'pca': 4, 'logistic': 24, 'lda': 12, 'cebra': 0, 'optimizer_updates': 0}"
        ),
    ]
    c = [
        md(
            "# 3 — Fresh cue-only CEBRA-Time and matched references\nIndependent source reconstruction; no old encoder, standardized array or notebook cache. Existing offset1-model/temperature1/Adam and exact row-uniform native-adjacent-bin Time sampler. Public demo uses20updates; reviewed biological configuration requires1000, unchanged."
        ),
        *common,
        code(LOAD),
        md(
            "## Declare optimization, temporal pairs and worlds\nThe permutation shuffles joint pair labels at source level within block×split before matching. It preserves observed provenance and uses its own fixed development world. It is an alignment-breaking diagnostic, not a statistical null."
        ),
        code("""import neuro.cebra as cebra
validate_kernel_identity(configuration)  # Includes actual optional dependency origins/code before fitting.
from neuro.pca_lda import fit_standardizer, raw_features, fit_pca
from neuro.notebook_support import fit_logistic
assert settings['seeds'] == [0, 1]
print({k: settings[k] for k in ('iterations', 'batch_size', 'hidden', 'output_dimension', 'learning_rate')})
print('Native positives:', [[b, b + 1] for b in range(data.values.shape[2] - 1)], '| references row-uniform; negatives row/bin-uniform')
accounting = FitAccounting(cebra=True).start()
results = []"""),
        md(
            "## Visible fresh encoder, reference and readout fits\nEvery source-budget/world/seed refits normalization, PCA, CEBRA and three separate logistic heads. Development transformations cannot refit. Paired seeds do not represent biological replication."
        ),
        code("""for world in ('observed', 'permuted'):
    world_map = effective_pair_map(data, permutation_seed=None if world == 'observed' else settings['permutation_seed'])
    development_plan = sample_plan(data, split_id='development', rows_per_condition=settings['development_rows_per_condition'], seed=0, effective_conditions=world_map)
    reference_development = materialize(data, development_plan)
    store.save(world + '_fixed_development', reference_development)
    for seed in (settings['seeds'] if world == 'observed' else [0]):
        for budget in ('full', 'reduced'):
            selected, effective = source_budget(data, world_map, reduced=budget == 'reduced', subset_seed=settings['subset_seed'])
            train, development = checked_assemblies(selected, effective, development_plan, reference_development, config=settings, seed=seed)
            key = f'{world}_seed{seed}_{budget}'
            store.save_bundle(key, train, development)
            print(key, 'source accounting:', json.dumps(usage_summary(selected, train), sort_keys=True))
            standardizer = fit_standardizer(train.values)
            raw_train, raw_dev = raw_features(standardizer.transform(train.values)), raw_features(standardizer.transform(development.values))
            pca = fit_pca(train.values, n_components=settings['pca_components'])
            remaining = float(os.environ.get('NEURO_DEADLINE_MONOTONIC', time.monotonic() + 120)) - time.monotonic()
            encoder = cebra.fit(train.values, train.targets, iterations=settings['iterations'], batch_size=settings['batch_size'],
                                output_dimension=settings['output_dimension'], hidden=settings['hidden'], learning_rate=settings['learning_rate'],
                                seed=seed, max_seconds=remaining, device='cpu')
            store.save_encoder(key + '_raw', standardizer, kind='raw')
            store.save_encoder(key + '_pca', pca, kind='pca')
            store.save_encoder(key + '_cebra', encoder, kind='cebra')
            feature_pairs = {'raw': (raw_train, raw_dev), 'pca': (pca.transform(train.values), pca.transform(development.values)),
                             'cebra': (encoder.transform(train.values), encoder.transform(development.values))}
            run_results = []
            for representation, (train_x, dev_x) in feature_pairs.items():
                for head, y in target_heads(train).items():
                    model = fit_logistic(train_x, y, C=settings['logistic_C'], max_iter=settings['logistic_max_iter'])
                    row = store.readout(key + '_' + representation + '_' + head, model, encoder=key + '_' + representation,
                                        bundle=key, head=head, train_features=train_x, development_features=dev_x)
                    run_results.append(row)
            results.extend(run_results)
            print(json.dumps(compact_metrics(run_results), sort_keys=True))
            print('Realized sampler phase exposure:', encoder.diagnostics['exposure_summary']['reference_phase_counts'])
            assert len(encoder.diagnostics['loss']['total']) == settings['iterations']
            assert np.isfinite(encoder.diagnostics['loss']['total']).all()
            fig, axes = plt.subplots(1, 2, figsize=(9, 3))
            axes[0].plot(encoder.diagnostics['loss']['total']); axes[0].set(xlabel='Optimizer update', ylabel='InfoNCE loss', title=key)
            axes[1].hist(encoder.diagnostics['sample_exposure_counts'].reshape(-1), bins=15)
            axes[1].set(xlabel='Realized reference/positive/negative uses', ylabel='Native vector entries', title='Sampler exposure, not effective biological n')
            display(fig); plt.close(fig)
            fig = plot_confusions(run_results, title=key + ': development counts and row-normalized confusions')
            display(fig); plt.close(fig)
store.save('aggregate_metrics', results)"""),
        md(
            "## Inspect transformed held-out coordinates\nThis descriptive plot does not establish neural-state dynamics or override matched readout scores."
        ),
        code("""z = feature_pairs['cebra'][1]
fig, ax = plt.subplots(figsize=(5, 3)); ax.scatter(z[:, 0], z[:, 1], s=6)
ax.set(xlabel='CEBRA coordinate1, first cue bin', ylabel='CEBRA coordinate2, first cue bin', title='Transformed development (descriptive)')
display(fig); plt.close(fig)
print('Grid summary: 6CEBRA,6PCA,54logistic; observed and permuted worlds are not pooled.')"""),
        md(LIMIT),
        finish(
            "{'pca': 6, 'logistic': 54, 'lda': 0, 'cebra': 6, 'optimizer_updates': 6 * settings['iterations']}"
        ),
    ]
    a = enrich_construction_notebook(a, md, code)
    b, c = enrich_model_notebooks(b, c, md, code)
    overview = research_guide(md, code, ROOT)
    # Hold the existing no-fitting guard across *all* A cells, not just final replay.
    a[1] = dict(a[1])  # The common cell is shared with B/C; guard only A.
    a[1]["source"] = (
        "from neuro.notebook_artifacts import no_fitting, FitAccounting\n"
        "whole_notebook_no_fitting = no_fitting()\n"
        "whole_notebook_no_fitting.__enter__()\n"
        "accounting = FitAccounting().start()\n" + "".join(a[1]["source"])
    ).splitlines(keepends=True)
    a[-1]["source"] = (
        "".join(a[-1]["source"])
        + "\nwhole_notebook_no_fitting.__exit__(None, None, None)"
    ).splitlines(keepends=True)
    for name, cells in zip(
        ("00_research_guide", "01_pseudopopulation", "02_pca_lda", "03_cebra"),
        (overview, a, b, c),
        strict=True,
    ):
        notebook = {
            "nbformat": 4,
            "nbformat_minor": 5,
            "metadata": {
                "kernelspec": {
                    "name": "python3",
                    "display_name": "Python3",
                    "language": "python",
                },
                "language_info": {"name": "python"},
                "scope": (
                    "reading guide; previously public aggregate evidence; no execution"
                    if name == "00_research_guide"
                    else "fresh-input exploratory computation; invented default; supplied-data gated"
                ),
            },
            "cells": cells,
        }
        for i, cell in enumerate(cells):
            cell["id"] = f"{name}-{i:02d}"
        path = ROOT / "notebooks" / (name + ".ipynb")
        path.parent.mkdir(exist_ok=True)
        path.write_text(json.dumps(notebook, indent=1) + "\n")
        print(path.relative_to(ROOT))


if __name__ == "__main__":
    build()
