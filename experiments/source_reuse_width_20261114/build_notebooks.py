"""Two dated, self-contained experiment source notebooks; outputs remain empty."""

from pathlib import Path
import nbformat


def make_notebook(part):
    if part not in ("reuse", "width"):
        raise ValueError("unknown experiment")
    md, code = nbformat.v4.new_markdown_cell, nbformat.v4.new_code_cell
    title = (
        "Source reuse at fixed population width"
        if part == "reuse"
        else "Population width at three training sources"
    )
    question = (
        "Does broader measured training support help when the population and assembled row quota stay fixed? "
        "The17-unit/3-session cohort supports at least5training sources per class. Compare nested2/3/5source budgets "
        "at16assembled rows/class. U3 is the standard once-only control: the same three sources as B3, used once."
        if part == "reuse"
        else "Does horizontal population expansion help at a fixed training-source budget? Compare17/49/83recorded columns "
        "across3/11/20nested sessions, each using exactly3training sources/session×class and16assembled rows/class. "
        "The17-column B3 anchor is the exact fit from experiment1, authenticated here; it is not fitted again."
    )
    cells = [
        md(
            "# "
            + title
            + "\n\n**November14,2026 · Exploratory analysis · Actual fresh training on existing recordings.**\n\n"
            + question
            + "\n\nOne nine-class ordered start–goal task is frozen throughout both experiments. This is a condition-level "
            "pseudopopulation assay, not a new biological recording or an independent natural-trial test. Read the saved "
            "outputs without running anything; execution requires the bounded runner and passed benchmark/preflight gates."
        ),
        code(
            """from pathlib import Path
import os, json, inspect, html, base64
from IPython.display import display, HTML, Image
from neuro.notebook_artifacts import runtime_identity, stable_kernel_identity
from neuro.studies.population_models import frozen_models
from experiments.source_reuse_width_20261114 import study
from experiments.source_reuse_width_20261114.report import create_report, table
PROJECT=Path(os.environ['NEURO_PROJECT_ROOT'])
RUN=Path(os.environ['NEURO_REUSE_RUN'])
PART="""
            + repr(part)
            + """
config=json.loads((RUN/'configuration.json').read_text())
assert config==study.configuration(config['design'])
pins=json.loads((RUN/'code-pins.json').read_text())
assert all(study.sha(PROJECT/path)==digest for path,digest in pins.items())
identity=runtime_identity()
assert stable_kernel_identity(identity)==stable_kernel_identity(json.loads((RUN/'runtime.json').read_text()))
study.write_json(RUN/('kernel-runtime-'+PART+'.json'),identity)
if PART=='width':
    assert study.sha(RUN/'bridge-receipt.json')==os.environ['NEURO_BRIDGE_SHA256']
    bridge=json.loads((RUN/'bridge-receipt.json').read_text())
    assert all(study.sha(RUN/path)==digest for path,digest in bridge['files_sha256'].items())
    print('Authenticated8completed B3 bridge cases and their saved artifacts; no bridge refitting.')
print('Classification:',config['classification'])
print('Runtime packages:',identity['packages'])
print('Complete two-experiment budget:',config['expected_fit_counts'])
"""
        ),
        md(
            "## 1. Fixed task and available measurements\n\n"
            "The global current/predecessor contributor embargo is applied before source and population selection. "
            "Metadata-only optimization first maximized width with≥5training/≥1development sources per pool, then "
            "width with≥3training/≥1development among ties, then selected the lexicographically first class list. "
            "All six starts and goals occur once or twice. This uses historically exposed development availability. "
            "Nine ordered pairs are not a3×3rectangle or measured maze paths. No performance score selected this panel."
        ),
        code("""with frozen_models():
    meta=study.metadata(PROJECT/'data/cue-source-v1')
    assert study.validate_design(meta,config['design'])
print('Classes:',', '.join(config['design']['panel']['conditions']))
print('Protected current/predecessor development contributors:',len(meta['protected']))
display(HTML(table([dict(roster=name,**row) for name,row in config['design']['rosters'].items()])))
print('Distinct training sources used: B2=54; B3/U3=81; B5=135; Wmid=297; Wfull=540.')
print('Constructed rows:144train/72development, except U3=27train. These are not independent sample sizes.')
"""),
        md(
            "## 2. Reconstruct authenticated source signals\n\n"
            "Selected-unit spike timestamps are counted in ten half-open100-ms bins over cue[0,1)s. "
            "Timing uses the validated Ripple clock and cue markers. Missing cross-session measurements stay masked; "
            "measured zeros remain zeros. No prior model, embedding or historical prediction initializes this run."
        ),
        code("""with frozen_models():
    data,reconstruction_audit=study.reconstruct(PROJECT/'data/cue-source-v1',meta,config['design'])
study.write_json(RUN/('reconstruction-'+PART+'.json'),reconstruction_audit)
print('Fresh source tensor:',data.values.shape)
print('Recorded units:',len(data.units),'session blocks:',len(data.block_ids))
print('Overlapping cross-split contributors:',len(data.dependency_audit()['overlapping_contributor_ids']))
prefit=json.loads((RUN/'prefit-evidence/rank-and-plan-checks.json').read_text())
assert len(prefit)==48 and min(r['training_rank'] for r in prefit)>=7
print('Before fitting:48scheduled plans passed exact source nesting, projected arrays, quotas, contributors and rank≥7.')
display(HTML(table([r for r in prefit if r['world']=='observed' and r['seed']==0])))
"""),
        md(
            "## 3. Paired construction and standard controls\n\n"
            "Per-session×class source rankings give nested2⊂3⊂5source sets. The three-source full-width plan is "
            "projected into smaller rosters; shared columns retain exactly the same source blocks, row IDs and values. "
            "One development plan per label world is projected into every arm. Observed development remains fixed across "
            "all three repeats. Balanced cycles cover all selected sources: B2 uses each8times, B3 uses5or6, B5 uses3or4. "
            "U3 uses the same B3 sources once. Five joint-pair source-label worlds preserve session/split counts and "
            "are generated before selection/assembly. They are diagnostic controls, not biological p-values."
        ),
        code("""with frozen_models():
    plans=study.paired_plans(data,meta,config['design'],seed=0)
    checked=study.verify_plans(plans)
display(HTML(table([r for r in checked if r['arm'] in study.PART_ARMS[PART]])))
display(HTML('<details><summary>Actual paired construction implementation</summary><pre>'+html.escape(inspect.getsource(study.paired_plans))+'</pre></details>'))
del plans
"""),
        md(
            "## 4. Fixed model comparisons and actual training\n\n"
            "Each new case fits train-only raw scaling, PCA7, CEBRA-Time7 and native multisession CEBRA7. "
            "Each has logistic, RBF-SVM, kNN5 and SVD-LDA pair/start/goal readouts. Whole-cue readouts concatenate ten bins: "
            "70latent features or10×recorded-width raw features. CEBRA branches each receive1000updates, hidden32, "
            "learning rate.0003, cosine temperature1. Time uses within-row adjacent-bin positives and batch256; "
            "native uses actual session encoders, joint-pair-supervised positives, floor(256/S) references/session "
            "and equal-session mean pooling. Thus native changes the whole pipeline, including supervision. "
            "Logistic C=.01×144/N and SVM C=144/N preserve N×C for the U3 row-count control; SVM gamma=scale, "
            "balanced class weights, uncalibrated margins. There is no hyperparameter sweep.\n\n"
            + (
                "This cell fits32new cases:4arms×(3observed repeats+5label worlds)."
                if part == "reuse"
                else "This cell fits16new cases:2additional width arms×(3observed repeats+5label worlds). Eight B3 bridge cases remain shared."
            )
        ),
        code("""display(HTML('<details><summary>Exact fitting, artifact saving and guarded replay</summary><pre>'+html.escape(inspect.getsource(study.train_case))+'</pre></details>'))
accounting=study.GridFitAccounting(cebra=True).start()
try:
    results=study.run_part(data,meta,config,RUN,PART,accounting)
finally:
    actual=accounting.stop()
    study.write_json(RUN/('actual-fit-counts-'+PART+'.json'),actual)
count=32 if PART=='reuse' else 16
expected={k:v*count//48 for k,v in config['expected_fit_counts'].items()}
assert actual==expected
print('New cases:',count,'actual instrumented fit/update counts:',actual)
"""),
        md(
            "## 5. Scores, source use and learning curves\n\n"
            "The report authenticates every completed case before collation. Balanced accuracy is mean class recall. "
            "Uniform pair reference=1/9; start/goal=1/6. The hypothetical perfect-single-endpoint pair reference=6/9 "
            "describes this sparse task, not a trained neural baseline. Report all computational repeats and diagnostic "
            "worlds. Repeated rows and seeds are not biological confidence intervals."
        ),
        code("""with frozen_models():
    report=create_report(RUN,PART,config,meta)
OUT=RUN/('report_'+PART)
print('Metric rows:',report['metric_rows'],'train/development confusion matrices:',report['confusion_matrices'])
display(HTML(table([r for r in report['summary'] if r['head']=='pair'])))
def show(group):
    for f in report['figures']:
        if f['group']!=group:continue
        path=OUT/f['file'];assert study.sha(path)==f['sha256']
        if group in ('confusions','trajectories'):
            encoded=base64.b64encode(path.read_bytes()).decode()
            display(HTML('<details><summary>'+html.escape(path.stem)+'</summary><img style="max-width:100%" src="data:image/png;base64,'+encoded+'"><p>'+html.escape(f['caption'])+'</p></details>'))
        else:
            display(Image(filename=str(path)))
            display(HTML('<p>'+html.escape(f['caption'])+'</p>'))
show('overview')
show('learning')
"""),
        md(
            "## 6. Cue representation trajectories\n\n"
            "Every observed arm/repeat is shown. Lines are class means over8constructed development rows and ten "
            "bin centers50–950ms from cue onset. Only the first three of seven coordinates are plotted; separate fits "
            "are not aligned. These describe learned cue representations, not maze paths or simultaneous neural dynamics."
        ),
        code("show('trajectories')"),
        md(
            "## 7. Confusions and best/worst error comparisons\n\n"
            "Count and row-normalized pair confusions below show every model/readout at observed repeat0. "
            "The standalone report embeds an interactive explorer covering every repeat, label world, pair/start/goal "
            "head and training/development split. The complete matrices and per-class recalls are also numeric JSON/CSV. "
            "Best/worst arms are selected within each fixed encoder/readout using mean observed pairBA. U3 is a "
            "separate control and is excluded from primary reuse ranking. These views are post-hoc descriptions."
        ),
        code("""show('confusions')
display(HTML(table(report['best_worst'])))
show('errors')
print('Interactive complete confusion explorer:',OUT/'report.html')
print('Numeric complete matrices:',OUT/'confusion_matrices.json')
print('Paired right→wrong / wrong→right tables:',OUT/'paired_error_switches.csv')
"""),
        md(
            "## 8. What this can establish, and the issue29 follow-up\n\n"
            "The primary reuse comparison couples greater measured source diversity with less repetition and changed "
            "weighting/recombination. U3/B3 holds measured sources fixed. The width comparison adds sessions, columns "
            "and total sources together; native encoder counts and per-session batch exposure also change. "
            "All conclusions concern this condition-level, known-label-assembled and historically exposed-development assay.\n\n"
            "The error handoff records retained/removed column aliases and common-row prediction changes. No class is "
            "deleted between arms. Spatial-map availability is unknown: compact inputs lack authenticated field location, "
            "occupancy/reliability, map-source trials and coordinate joins. Therefore lost-field explanations from issue29 "
            "remain untested. Navigation place fields cannot be substituted with cue confusion labels. This gap does not "
            "erase the completed source-reuse/width measurements.\n\n"
            "Every saved encoder/readout was reloaded under fit guards and reproduced train/development transformations "
            "and predictions. The final run receipt and independent numeric/scientific review are recorded after both "
            "notebooks finish. No prior experiment has been overwritten."
        ),
        code("""assert all(study.sha(PROJECT/path)==digest for path,digest in pins.items())
assert all(study.sha(OUT/f['file'])==f['sha256'] for f in report['figures'])
print('Completed experiment',PART,'with',count,'new cases and',len(report['figures']),'figures.')
print('Independent cross-run receipt/numeric review follows completion of both files.')
"""),
    ]
    return nbformat.v4.new_notebook(
        cells=cells,
        metadata={
            "kernelspec": {
                "display_name": "Python3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {"name": "python"},
            "study": "source-reuse-width-20261114",
            "part": part,
        },
    )


if __name__ == "__main__":
    folder = Path(__file__).resolve().parent
    for part, name in (
        ("reuse", "source_reuse_20261114"),
        ("width", "population_width_20261114"),
    ):
        nbformat.write(make_notebook(part), folder / (name + ".ipynb"))
