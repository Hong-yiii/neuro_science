"""Fresh training/evidence notebook for the November11 class × session grid."""

import nbformat


def make_notebook():
    md, code = nbformat.v4.new_markdown_cell, nbformat.v4.new_code_cell
    cells = [
        md("""# Class requirements × session selection: population width and learning

**New exploratory biological training, November11,2026.** This notebook reconstructs existing authenticated cue recordings and fits fresh models. It does not use the previous experiment's results. The nine configurations are **three class requirements (30/20/15) × three nested session rosters (one-third/two-thirds/all)**. They are not nine endpoint classes.

Each configuration has three sampling policies: U2 uses exactly two measured current sources/session×pair once; R16 recombines those same sources into16rows/pair; F16 uses all available sources in16rows/pair. Three computational seeds give81observed cases. Five within-session/split label worlds on full-roster U2/F16 give30diagnostic cases. Exactly111cases are trained:5661fit calls excluding scalers,222000updates. A prefit rank-eight failure (zero fits) in an unfitted smaller-roster null prompted a conservative common dimension7 across the216-plan preflight family before any biological scores; this does not imply8D is infeasible for a scheduled fitted case.

Reading this saved notebook needs no model runtime. Execution requires the dedicated reviewed runner, pinned configuration and bounded cgroup. All results are exploratory, label-conditioned and based on historically exposed development."""),
        code("""from pathlib import Path
import os, json, html, base64, inspect
from IPython.display import display, HTML, Image
from neuro.studies import population_grid as study
from neuro.notebook_artifacts import no_fitting, runtime_identity, stable_kernel_identity
from scripts.population_grid_report import table, create_report
PROJECT=Path(os.environ['NEURO_PROJECT_ROOT'])
RUN=Path(os.environ['NEURO_GRID_RUN'])
config=json.loads((RUN/'configuration.json').read_text())
design=json.loads((PROJECT/study.DESIGN_PATH).read_text())
assert config == study.configuration(design)
pins=json.loads((RUN/'code-pins.json').read_text())
assert all(study.sha(PROJECT/path)==digest for path,digest in pins.items())
identity=runtime_identity()
assert stable_kernel_identity(identity)==stable_kernel_identity(json.loads((RUN/'runtime.json').read_text()))
study.write_json(RUN/'kernel-runtime.json',identity)
print('Classification:',config['classification'])
print('Runtime packages:',identity['packages'])
print('Planned actual fit counts, excluding scalers:',config['expected_fit_counts'])
"""),
        md("""## 1. Frozen design before neural scores

Global current/predecessor contributor separation precedes class/session selection. Metadata optimization maximizes recorded width at each K, then distinct training-source total among ties, then the lexicographically first class list. All six starts and goals remain represented with nearly balanced degree. Session ranking uses the harmonic mean of training counts, exactly for ties. Selection uses exposed development availability, so this is exploratory."""),
        code("""with no_fitting(cebra=True):
    metadata=study.metadata(PROJECT/'data/cue-source-v1')
    assert study.validate_design(metadata,design)
print('Protected development contributors:',len(metadata['protected']))
display(HTML(table(design['grid'],['configuration','sessions','units','train_sources','development_sources','balanced_no_reuse_rows','classwise_no_reuse_rows','development_singletons','session_class_pools'])))
for panel in design['panels']:
    print(panel['class_count'],'classes:',', '.join(panel['conditions']))
"""),
        md("""## 2. Reconstruct source measurements

Native selected-unit spike timestamps are counted in ten half-open100-ms bins over cue[0,1)s. Real zeros remain zeros; unmeasured cross-session entries remain masked. Spike timestamps convert from milliseconds to seconds on the absolute Ripple clock; cue boundaries are already seconds. The adapter authenticates inputs, regenerates native event eligibility/frozen assignments, checks selected Eye events and counts retained/tail spikes. No historical model or result is loaded."""),
        code("""with no_fitting(cebra=True):
    data,reconstruction_audit=study.reconstruct(PROJECT/'data/cue-source-v1',metadata,design)
study.write_json(RUN/'reconstruction_audit.json',reconstruction_audit)
for k,source in data.items():
    print('K',k,'source tensor',source.values.shape,'overlapping contributor IDs',len(source.dependency_audit()['overlapping_contributor_ids']))
"""),
        md("""## 3. Match sampling and session comparisons

Plans are built for the largest roster then projected onto smaller rosters, preserving the exact common-source arrays and labels. Development has8rows/pair at fixed seed0, identical across policies. U2/R16 use identical source sets; R16 uses each8times. F16 covers all eligible sources. Source coverage also changes empirical weighting and joint combinations; it is not a count-only intervention. Every source block retains all its units and bins."""),
        code("""with no_fitting(cebra=True):
    prefit=[]
    for k,source in data.items():
        for permutation,seeds in [(None,(0,1,2))]+[(p,(0,)) for p in study.PERMUTATIONS]:
            for seed in seeds:
                plans=study.paired_plans(source,metadata,design,seed=seed,permutation=permutation)
                prefit.extend(dict(K=k,seed=seed,permutation=permutation,**r) for r in study.verify_plans(plans,numerical_rank=True))
study.write_json(RUN/'prefit-rank-checks.json',prefit)
print('Verified216plans across all24observed/null bundles before fitting: exact nested arrays, common development, source multiplicity and PCA7 rank.')
display(HTML(table(prefit)))
del plans
"""),
        md("""## 4. Actual fitting computation

All models are newly fitted. Pooled training-only scaling precedes PCA7 or CEBRA-Time7; each bin has7coordinates and each whole-cue readout70features. Raw features have10×unit-count columns. Every representation (raw, PCA7, CEBRA-Time7, native multisession7) has logistic, RBF-SVM, kNN5 and SVD-LDA pair/start/goal readouts. SVM uses uncalibrated margins, no probability/log-loss fabrication. Its C=16K/N, gamma=scale, balanced class weights; kNN uses uniform Euclidean votes. All readout scaling fits training only.

CEBRA is a per-bin MLP U→32→32→16→7 with normalized output. Adjacent bins from the same row supply positives, not a recurrent sequence input.1000Adamupdates at.0003,batch256,cosine temperature1. Training InfoNCE loss is distinct from held-out prediction quality. Native multisession uses the actual discrete CEBRA API: a separate encoder for each session, joint-pair supervised positive alignment and equal-session mean pooling of aligned coordinates. It has no temporal-positive constraint. Batch floor(256/S) per session,1000updates,one native torch thread under a two-core process ceiling; at most256total references/update. This changes objective, parameterization and pooling versus Time, so it compares complete pipelines, not an isolated multisession benefit. Logistic C=.01×16K/Ntrain (.08forU2,.01otherwise) keeps N×C fixed within K."""),
        code("""display(HTML('<details><summary>Exact source: new plan construction</summary><pre>'+html.escape(inspect.getsource(study.paired_plans))+'</pre></details>'))
display(HTML('<details><summary>Exact new fitting/save/replay implementation</summary><pre>'+html.escape(inspect.getsource(study.train_case))+'</pre></details>'))
"""),
        md("""## 5. Train all111cases

Observed seeds0/1/2 cover the whole grid. Five joint-pair permutations60000…60004 precede subset selection and assembly, preserve within-session/split counts and have compatible development worlds. They cover full-rosterU2/F16 only, modelseed0. These are diagnostic controls, not p-values. Every attempt and actual call/update count is saved. No automatic retry or post-result tuning."""),
        code("""results=study.run_grid(data,metadata,config,RUN)
assert json.loads((RUN/'actual-fit-counts.json').read_text())==config['expected_fit_counts']
print('Newly completed111cases;5328whole-cue readout results:',len(results['metrics']))
"""),
        md("""## 6. Collate the evidence

Numeric CSV/JSON tables retain all5328metric and confusion records, all222learning curves, source usage/error involvement, exclusions and lineage. The HTML renders81observed trajectories and seed0pair confusions for every configuration/policy/decoder; all other confusions are retained numerically. No prior-run result enters this collation."""),
        code("""report=create_report(results,metadata,RUN/'report',config=config,reconstruction_audit=reconstruction_audit)
print('Standalone report figures:',len(report['figures']))
display(HTML(table([r for r in report['summary'] if r['head']=='pair'])))
def show_group(group):
    for figure in report['figures']:
        if figure['group']!=group: continue
        path=RUN/'report'/figure['file']
        assert study.sha(path)==figure['sha256']
        if group in ('trajectories','confusions'):
            encoded=base64.b64encode(path.read_bytes()).decode()
            display(HTML('<details><summary>'+html.escape(path.stem)+'</summary><img style="max-width:100%" src="data:image/png;base64,'+encoded+'"><p>'+html.escape(figure['caption'])+'</p></details>'))
        else:
            display(Image(filename=str(path)))
            display(HTML('<p>'+html.escape(figure['caption'])+'</p>'))
"""),
        md("""## 7. Availability, sources, reuse and predictive scores

Compare width within each K. Adding sessions changes width and source composition together. R16−U2 holds measured sources fixed; F16−R16 holds row quota fixed. Uniform pairBA is1/K; the perfect-goal/no-start mathematical reference is6/K. Source counts, assembled rows and optimizer draws are different quantities. Dots are all computational seeds, not biological uncertainty."""),
        code("show_group('overview')"),
        md(
            "## 8. All222CEBRAlearning curves\n\nOptimization curves do not establish generalization."
        ),
        code("show_group('learning')"),
        md("""## 9. Every observed cue-time trajectory

PCA, CEBRA-Time and native multisession class means in their first three native coordinates,10bin centers50–950ms,8constructed development rows per pair. These are not maze paths or simultaneous population dynamics. Seven dimensions were fitted; only three are displayed. Coordinates are unaligned across independent models."""),
        code("show_group('trajectories')"),
        md("""## 10. Count and normalized confusion matrices

Every observed seed0configuration/policy/decoder pair result is rendered below. All5328matrices including other seeds and permutations are saved in JSON and expanded numeric tables in the report. True labels are rows, predicted labels columns."""),
        code("show_group('confusions')"),
        md("""## 11. Evidence limits and verification

The analysis is a condition-level, known-label-assembled assay on exposed development. U2 removes repeated current sources in assembly, not optimizer/bin/serial dependence. Development has singleton pools. More recorded columns or assembled rows do not create independent biological replicates. No natural unknown-trial prediction, new-session transfer, time-resolved decoder, simultaneity or formal observability claim is supported.

All newly saved encoders/readouts were authenticated and composed on both splits with fitting blocked. The resource receipt and independent result review follow notebook completion. No historical result is substituted for a failed new run."""),
        code("""assert all(study.sha(PROJECT/path)==digest for path,digest in pins.items())
accounting=json.loads((RUN/'aggregates/fit_accounting.json').read_text())
assert accounting['counts']==config['expected_fit_counts']
assert accounting['cases']==111
print('Actual fit accounting:',accounting)
print('All declared new fits and artifacts completed; independent results review follows.')
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
            "study": "population-grid-20261111",
        },
    )


if __name__ == "__main__":
    nbformat.write(make_notebook(), "notebooks/06_population_grid.ipynb")
