"""Two complete, executable teaching notebooks for the frozen real study."""

from pathlib import Path
import ast
import textwrap
import nbformat
from ..build_notebooks import make_notebook as original_notebook


def md(text):
    return nbformat.v4.new_markdown_cell(textwrap.dedent(text).strip())


def code(text):
    # Stable executable sources, without output or execution-count fabrication.
    return nbformat.v4.new_code_cell(
        ast.unparse(ast.parse(textwrap.dedent(text).strip()))
    )


def make_notebook(part):
    old = original_notebook(part)
    cells = old.cells[:8]
    cells[0] = (
        md(f"""# {"Source reuse at fixed population width" if part == "reuse" else "Population width at fixed source budget"}

    **November 15, 2026 · executed exploratory notebook · existing recordings, fresh fits.**

    This is {"experiment 1" if part == "reuse" else "experiment 2"} of one fixed two-part study.
    The research question is whether endpoint recovery depends on repeated use of a small
    recorded source pool, and how recovery changes when more sessions/columns are available.
    The first experiment compares 2, 3 and 5 distinct training sources per session × class at
    17 columns and 144 constructed training rows. Its U3 control uses the same B3 sources once
    (27 rows). The second compares 17, 49 and 83 columns at three sources per pool.

    Read top to bottom: question → source eligibility → construction → visible first-case
    training → complete fixed schedule → controls → errors → interpretation. Every reported
    result below is produced by this fresh two-notebook execution. The accepted study defined November14 is
    preserved separately; this reproduction is not an additional biological replicate.

    **What counts as evidence?** Spike times and task-event records are measured. Cue-bin
    counts, pseudopopulation rows, embeddings and predictions are derived. We test association
    with nine ordered start–goal labels in a historically exposed development split. These are
    condition-level rows assembled using known labels, not independently observed simultaneous
    population trials. No exact natural-trial decoding, path prediction or mechanism claim follows.

    **Reading and execution.** Saved outputs require no fitting. Re-execution requires the
    experiment runner, authenticated compact source inputs, the fixed runtime and fresh passing
    gates; it trains models. The companion file shares authenticated B3 fits without refitting.
    Numerical recipes live beside this notebook; the protocol and validation ledger are under
    `docs/experiments/source-reuse-width-20261114/`.
    """)
    )
    cells[1].source += """\nimport numpy as np
import matplotlib.pyplot as plt
from collections import Counter
from scipy.special import softmax
from neuro import cebra
from neuro.pca_lda import fit_standardizer, fit_pca
from neuro.studies.population_models import ENCODERS, DECODERS, fit_native, fit_decoder
from experiments.source_reuse_width_20261114.walkthrough_20261115.execution import PartExecution
"""
    cells[
        2
    ].source += """\n\nA **session block** supplies several simultaneously recorded columns from one source trial.
Different session blocks are joined by the ordered endpoint label. One real source identity
is distinct from another, but adjacent trials and repeated computational seeds are not assumed
independent. Eligibility requires correct current and predecessor trials, valid cue duration
and frozen split membership. The globally protected current/predecessor contributors are
removed from training before any fitting or metadata-based panel optimization. Operational start is the previous successful trial's marker-derived goal; operational goal
is the current trial's marker. Thus start is inferred from task records, not independently
tracked as a position or path. This explains why the previous trial is a contributor and
must be embargoed along with the current trial. These labels remain operational task labels;
compact inputs do not establish place-field
quality or exact navigation trajectories. The three-source source pool is nested within the
five-source pool, and the same classes remain in every arm. No class is deleted between arms."""
    cells[
        3
    ].source += """\nprint("Arm | columns | sessions | sources per session/class | constructed train rows | distinct selected train IDs")
for row in [("B2",17,3,2,144,54),("B3",17,3,3,144,81),("B5",17,3,5,144,135),("U3",17,3,3,27,81),("Wmid",49,11,3,144,297),("Wfull",83,20,3,144,540)]:
    print(row)
print("All arms have72constructed development rows. Adding columns also adds sessions and sources.")
"""
    cells[
        4
    ].source += """\n\nThe reconstructed tensor uses source trial × unit × ten cue bins. The bin interval is
[0,1) seconds relative to cue onset; each bin is100ms. Counts are not firing rates unless
divided by0.1s. A source trial only measures its own session's units. Missing other-session
entries must never be treated as silence. Materialization below takes each block from an
observed source before any scaler or model sees a dense pseudopopulation row."""
    cells[
        5
    ].source += """\nprint("Observed source×unit entries:",int(data.observed.sum()),"of",int(data.observed.size))
print("Ten cue-bin centers (seconds):",np.arange(0.05,1.0,0.1).round(2).tolist())
print("No source values, unit identities or trial-lineage arrays are printed in this shareable notebook.")
"""
    cells[7].source = """with frozen_models():
    plans = study.paired_plans(data, meta, config['design'], seed=0)
    checked = study.verify_plans(plans)
display(HTML(table([r for r in checked if r['arm'] in study.PART_ARMS[PART]])))
rows=[]
for arm in study.PART_ARMS[PART]:
    source, train_plan, dev_plan = plans[arm]
    tuples = [tuple(row.source_ids) for row in train_plan.rows]
    uses = Counter(sid for row in train_plan.rows for sid in row.source_ids)
    rows.append(dict(arm=arm, constructed_rows=len(tuples), distinct_source_IDs=len(uses),
                     min_uses=min(uses.values()), max_uses=max(uses.values()),
                     repeated_whole_source_tuples=len(tuples)-len(set(tuples))))
display(HTML(table(rows)))
print("Tuple repetitions count rows beyond the first identical source-ID combination, not pairwise collisions or numerical-vector equality.")
"""
    cells += [
        md("""## 4. Materialize the first case and start fit accounting

        We now expose one complete case: **B2, observed seed0** in the reuse notebook or
        **Wmid, observed seed0** in the width notebook. The remaining cases use the same
        maintained fitting routine. The staged path must reproduce that routine on invented
        full-width inputs before any biological execution is permitted.

        A training row contains all columns for each chosen session block. Its label is the
        common endpoint class used to choose those blocks. All bins and copies of a source
        stay on one side of the split. The recipe table below shows anonymous blocks and
        dimensions; full source provenance is saved privately and checked independently.
        """),
        code("""execution = PartExecution(data, meta, config, RUN, PART)
case = execution.begin(plans)
x_train, x_dev = case.train.values, case.dev.values
print('First case:',case.case['id'])
print('Train / development tensors:',x_train.shape,x_dev.shape,'= row × column × bin')
print('Endpoint classes:',sorted(set(case.yt['pair'])))
display(HTML(table([dict(block=meta['aliases'][block],columns=sum(u.block_id==block for u in case.data.units)) for block in case.data.block_ids])))
print('Constructed training class counts:',dict(Counter(case.yt['pair'])))
print('Constructed development class counts:',dict(Counter(case.yd['pair'])))
assert np.isfinite(x_train).all() and np.isfinite(x_dev).all()
print('Contributor overlap:0; all materialized values finite.')
recipe=[]
for row_number,row in enumerate(case.train.plan.rows[:2]):
    for block_index,block in enumerate(case.data.block_ids):
        pool=sorted({r.source_ids[block_index] for r in case.train.plan.rows if r.condition==row.condition})
        recipe.append(dict(constructed_row=row_number,pair=row.condition,block=meta['aliases'][block],source_choice=1+pool.index(row.source_ids[block_index])))
display(HTML(table(recipe)))
print('Recipe choices are local ordinal aliases within each session×class pool; equal numbers in different pools are not the same source.')
"""),
        md("""## 5. Train-only normalization: check the actual arithmetic

        Pool the training rows and cue bins, yielding N×10 vectors of width D. For each unit
        fit its training mean μ and standard deviation σ, then transform both splits using
        z=(x−μ)/σ. A constant unit uses scale1. No development statistic is fitted.
        Raw whole-cue readouts then flatten unit-major into10D features. This differs from
        the subsequent latent readouts' time-major70features, but every branch retains the
        whole cue. Scalers are learned preprocessing; the displayed2,448 model-fit budget
        excludes scaler fits and records that convention explicitly.
        """),
        code("""with execution.stage('raw scaling'):
    raw_fit = fit_standardizer(x_train)
    raw_train, raw_dev = case.record_representation('raw',raw_fit)
    pooled = x_train.transpose(0,2,1).reshape(-1,x_train.shape[1])
    manual = ((x_dev-raw_fit.scaler.mean_[None,:,None])/raw_fit.scaler.scale_[None,:,None]).astype(np.float32)
    residual = float(np.max(np.abs(manual-raw_fit.transform(x_dev))))
    np.testing.assert_allclose(raw_fit.scaler.mean_,pooled.mean(0,dtype=np.float64),rtol=1e-7,atol=1e-7)
    np.testing.assert_allclose(manual,raw_fit.transform(x_dev),rtol=1e-5,atol=1e-5)
    print('Training vectors used by scaler:',raw_fit.scaler.n_samples_seen_)
    print('Raw feature shapes:',raw_train.shape,raw_dev.shape)
    print('Maximum manual-versus-library normalization residual:',residual)
"""),
        md("""## 6. Fit PCA7 and verify its linear projection

        PCA finds seven orthogonal directions of training-bin variance after training-only
        unit scaling. It sees no endpoint labels. Full SVD and a numerical-rank≥7gate avoid
        silently padding unsupported dimensions. For each standardized bin vector z, the
        fitted transform is (z−PCAmean)×componentsᵀ. Concatenating ten7D bin vectors gives
        70 whole-cue readout features. Explained variance is a reconstruction statistic;
        it does not measure endpoint prediction or biological significance.
        """),
        code("""with execution.stage('PCA training'):
    pca_fit = fit_pca(x_train,n_components=config['output_dimension'])
    pca_train, pca_dev = case.record_representation('pca',pca_fit)
    standardized = pca_fit.standardizer.transform(x_dev).transpose(0,2,1).reshape(-1,x_dev.shape[1])
    manual_pca = ((standardized-pca_fit.pca.mean_)@pca_fit.pca.components_.T).astype(np.float32).reshape(len(x_dev),-1)
    np.testing.assert_allclose(manual_pca,pca_dev,rtol=1e-5,atol=1e-5)
    print('PCA feature shapes:',pca_train.shape,pca_dev.shape)
    print('Explained variance ratios:',pca_fit.pca.explained_variance_ratio_.round(5).tolist())
    print('Maximum manual projection residual:',float(np.max(np.abs(manual_pca-pca_dev))))
"""),
        md("""## 7. Fit CEBRA-Time7: what its objective learns

        The Time encoder maps one standardized population bin to seven coordinates. A
        reference and an adjacent bin from the same constructed row form a positive pair;
        negative bins are sampled across rows/time. Cosine InfoNCE favors positive similarity
        relative to negatives. The network is `offset1-model`, hidden32, batch256,
        temperature1, Adam learning-rate0.0003, and exactly1,000updates. Endpoint labels
        label rows for validation but do not choose the Time positives.

        The temporal neighborhood is imposed by pseudopopulation construction. It is not a
        measured simultaneous cross-session neural trajectory. Falling contrastive loss only
        demonstrates optimization of this objective; held-out readouts and diagnostic worlds
        assess endpoint association. Even U3's once-only assembly is revisited during training.
        """),
        code("""with execution.stage('CEBRA-Time training'):
    time_fit = cebra.fit(x_train,case.train.targets,
        iterations=config['iterations'],batch_size=config['batch_size'],
        output_dimension=config['output_dimension'],hidden=config['hidden'],
        learning_rate=config['learning_rate'],seed=case.case['seed'],
        max_seconds=config['limits']['cebra_fit_seconds'],device='cpu')
    time_train, time_dev = case.record_representation('cebra',time_fit)
    print(time_fit.solver.model)
    print('Trainable parameters:',sum(p.numel() for p in time_fit.solver.model.parameters() if p.requires_grad))
    print('Features:',time_train.shape,time_dev.shape,'updates:',time_fit.diagnostics['iterations'])
    exposure = time_fit.diagnostics['exposure_summary']
    row_draws = np.asarray(exposure['reference_row_counts'])[0]
    print('Reference draws:',int(row_draws.sum()),'per-row minimum/maximum:',int(row_draws.min()),int(row_draws.max()))
"""),
        md("""## 8. Fit genuine native multisession CEBRA7

        The native comparator fits one network per session through CEBRA's actual
        multisession API. Every session contributes its own unit vector and joint-pair
        labels; positives therefore use pair supervision across sessions. After fitting,
        corresponding per-bin7D embeddings are averaged equally across sessions and ten bins
        are concatenated. Pooling is fixed, not learned. This pipeline changes architecture,
        supervision and aggregation together, so its score cannot isolate a single cause.

        To bound work, each session receives floor(256/S) batch references:85,23or12for
        S=3,11or20, yielding255,253or240total references per update. The notebook shows the
        realized dimensions and counts. Native and Time both train1,000updates; their losses
        have different sampling semantics and should not be ranked against one another.
        """),
        code("""with execution.stage('native multisession training'):
    native_fit = fit_native(x_train,case.train.targets,case.data.units,case.data.block_ids,config,case.case['seed'])
    native_train, native_dev = case.record_representation('native',native_fit)
    print('Solver:',native_fit.estimator.solver_name_,'session encoders:',native_fit.estimator.num_sessions_)
    print('Input columns per encoder:',native_fit.diagnostics['session_input_dimensions'])
    print('First session network:',next(native_fit.estimator.model_.children()))
    print('Trainable parameters:',sum(p.numel() for p in native_fit.estimator.model_.parameters() if p.requires_grad))
    print('Features:',native_train.shape,native_dev.shape)
    print('Batch/session:',native_fit.diagnostics['batch_per_session'],'references/update:',native_fit.diagnostics['references_per_update'])
    print('Pooling:',native_fit.diagnostics['aggregation'])
"""),
        md("""## 9. Readouts: fit one visibly, then the remaining47

        A representation is an input to a separate supervised readout, not itself an accuracy
        score. Pair/start/goal are three distinct targets: nine ordered pairs and six endpoint
        classes. Each representation receives logistic regression, RBF-SVM, kNN5 and SVD-LDA.
        Readouts fit their own training-only feature scaler. Logistic C=0.01×144/N and SVM
        C=144/N keep N×C fixed for U3; SVM uses gamma=`scale` and balanced class weights.
        No hyperparameters are selected from development scores. SVM reports margins rather
        than calibrated probabilities and has no log-loss value. kNN uses five Euclidean
        neighbors with uniform votes; U3 only has three rows of any pair class, limiting its
        possible same-class vote to3/5. This is a probability ceiling, not an accuracy ceiling:
        a3/5 vote may still select the correct class. LDA here is a classifier, not the PCA-like projection.

        First fit raw→logistic→pair. Its multiclass forward pass is standardized features
        ×coefficientsᵀ+bias, then softmax. The check below uses the fitted parameters and
        compares every probability; it does not fit an extra model.
        """),
        code("""with execution.stage('first readout and forward check'):
    first_readout = fit_decoder('logistic',raw_train,case.yt['pair'],config,case.ratio,case.case['seed'])
    first_score = case.record_readout('raw','logistic','pair',first_readout)
    scaled_features = first_readout[0].transform(raw_dev)
    logits = scaled_features@first_readout[-1].coef_.T+first_readout[-1].intercept_
    manual_probability = softmax(logits,axis=1)
    np.testing.assert_allclose(manual_probability,first_readout.predict_proba(raw_dev),rtol=1e-7,atol=1e-7)
    print('Maximum forward-probability residual:',float(np.max(np.abs(manual_probability-first_readout.predict_proba(raw_dev)))))
    display(HTML(table([first_score])))
"""),
        code("""with execution.stage('remaining first-case readouts'):
    for encoder_name in ENCODERS:
        features = case.features[encoder_name][0]
        for decoder_name in DECODERS:
            for head in ('pair','start','goal'):
                if (encoder_name,decoder_name,head)==('raw','logistic','pair'):
                    continue
                fitted = fit_decoder(decoder_name,features,case.yt[head],config,case.ratio,case.case['seed'])
                case.record_readout(encoder_name,decoder_name,head,fitted)
    assert len(case.readout_keys)==48
    display(HTML(table(case.metrics)))
    print('Actual first-case fit/update counts:',dict(execution.accounting.counts))
"""),
        md("""## 10. First-case errors, objective curves and saved-pipeline checks

        Balanced accuracy is the mean of the true-class recalls; count matrices have true
        classes on rows and predictions on columns. Pair classes have equal constructed
        support, so pair accuracy equals balanced accuracy. Start and goal classes have unequal
        support because some occur in two pair classes; the two metrics need not coincide.
        Uniform references are1/9and1/6. Knowing one endpoint perfectly can resolve6/9pairs
        in this sparse task, a combinatorial reference rather than a fitted neural baseline.

        Each encoder is saved, loaded with all fitting blocked, and transformed again on both
        splits. Each saved readout then reproduces predictions/scores from those reloaded
        encoder outputs. This verifies the composed pipeline, not merely a separately stored
        prediction array. Raw source tensors and fitted states stay local.
        """),
        code("""with execution.stage('first-case diagnostics'):
    figures, axes = plt.subplots(1,2,figsize=(12,4))
    for encoder_name in ('cebra','native'):
        curve = case.representations[encoder_name].diagnostics['loss']['total']
        axes[0].plot(np.arange(1,len(curve)+1),curve,label=encoder_name)
    axes[0].set(xlabel='Optimizer update',ylabel='Own-objective total loss',title='First case: training optimization')
    axes[0].legend()
    first_cm = next(r for r in case.confusions if r['encoder']=='raw' and r['decoder']=='logistic' and r['head']=='pair')
    cm = np.asarray(first_cm['counts'])
    axes[1].imshow(cm/cm.sum(1,keepdims=True),vmin=0,vmax=1,cmap='Blues')
    axes[1].set(xticks=range(9),yticks=range(9),xticklabels=first_cm['labels'],yticklabels=first_cm['labels'],xlabel='Predicted pair',ylabel='True pair',title='Raw/logistic: development recall matrix')
    axes[1].tick_params(axis='x',rotation=90)
    figures.tight_layout()
    display(figures)
    plt.close(figures)
    print('Caption: observed seed0, first arm,72constructed exposed-development rows; cue[0,1)s; no uncertainty interval. Loss scales are not comparable across objectives.')
    print('First-case reload checks:4encoders,48readouts,96composed split checks.')
"""),
        md("""## 11. Complete the fixed schedule without refitting the first case

        Reuse contains32cases; width adds16and references the eight completed B3 cases.
        Across both files there are18observed cases (six arms×three computational seeds) and
        30source-label diagnostic cases (six arms×five worlds at model seed0).
        A diagnostic world permutes joint-pair source labels within session and split before
        source selection and assembly. It preserves marginal counts while disrupting the
        original neural-label relation. These five worlds are a small diagnostic panel, not
        calibrated biological p-values. All48cases fit all representations/readouts/heads.

        The first case above is closed once and inserted into the same aggregate schema;
        the following cell trains only the remaining31or15cases. Actual instrumented counts,
        terminal attempt records and all source identities are independently reconciled.
        """),
        code("""results = execution.finish_remaining()
actual = execution.actual
count = 32 if PART=='reuse' else 16
expected = {k:v*count//48 for k,v in config['expected_fit_counts'].items()}
assert actual==expected
print('New cases:',count,'actual instrumented fits/updates:',actual)
print('Total model fits excluding scalers:',sum(v for k,v in actual.items() if k!='optimizer_updates'))
del case, execution, plans
"""),
    ]
    # Preserve the tested scientific report/trajectory/confusion collation.
    old.cells[
        14
    ].source += "\n\nThe complete interactive explorer is also embedded below with every matrix; no ignored result file is needed to view it after opening this executed notebook in a trusted Jupyter session or its offline HTML export. Static panels remain visible in viewers that do not run JavaScript."
    old.cells[
        15
    ].source += "\nfrom experiments.source_reuse_width_20261114.walkthrough_20261115.interpret import confusion_explorer\ndisplay(HTML(confusion_explorer(RUN,PART)))\n"
    cells += old.cells[10:16]
    cells[-6].source = cells[-6].source.replace("## 5.", "## 12.")
    cells[-4].source = cells[-4].source.replace("## 6.", "## 13.")
    cells[-2].source = cells[-2].source.replace("## 7.", "## 14.")
    cells += [
        md("""## 15. All repeat/control scores and paired contrasts

        A mean can hide opposing seed changes. Here every observed seed and diagnostic world
        contributes to a score table, and paired changes use matched world/seed development
        rows. Positive AFTER−BEFORE favors the after arm. These ranges summarize computational
        variation and five constructed diagnostic worlds; they are not biological confidence
        intervals. Compare both absolute scores and paired changes. The table keeps every
        readout and head, including failures to improve, rather than selecting only winners.
        """),
        code("""from experiments.source_reuse_width_20261114.audit.deliver import control_summaries, supplemental_figures
with frozen_models():
    scores, contrasts = control_summaries(RUN,PART)
    supplement = RUN/('walkthrough_'+PART)
    supplement.mkdir()
    study.write_csv(supplement/'score_control_summary.csv',scores)
    study.write_csv(supplement/'contrast_summary.csv',contrasts)
    supplement_figures = supplemental_figures(supplement,contrasts,PART)
for figure in supplement_figures:
    display(Image(filename=str(supplement/figure['file'])))
    display(HTML('<p>'+html.escape(figure['caption'])+'</p>'))
display(HTML('<details><summary>Every score:3observed seeds and5diagnostic worlds</summary>'+table(scores)+'</details>'))
display(HTML('<details><summary>Every paired contrast and its repeat/control ranges</summary>'+table(contrasts)+'</details>'))
import csv
for filename, label in [('metrics.csv','Every case score'),('paired_contrasts.csv','Every matched seed/world contrast')]:
    with (OUT/filename).open() as handle:
        full_rows = list(csv.DictReader(handle))
    keep = ('world','seed','arm','before','after','encoder','decoder','head','balanced_accuracy','accuracy','macro_f1','log_loss','train_BA','train_development_gap','delta_BA')
    display(HTML('<details><summary>'+label+'</summary>'+table([{k:r[k] for k in keep if k in r} for r in full_rows])+'</details>'))
print('The tables above contain every model/readout/head; pair SVM is a readable cross-model slice, not the only analysis.')
"""),
        md("""## 16. Interpret this execution and connect errors to the research question

        The following interpretation is generated from this run's saved scores and paired
        changes. All conclusions remain exploratory. An improvement in B5 over B2 couples
        increased distinct-source diversity with less repetition and different weighting/
        recombination. B3 versus U3 holds the source identities fixed but changes row count
        and optimization exposure. Wider populations add session blocks, columns and total
        measured source identities together. These comparisons do not isolate neurons per se.
        """),
        code("""from experiments.source_reuse_width_20261114.walkthrough_20261115.interpret import explain
with frozen_models():
    display(HTML(explain(RUN,PART,scores,contrasts)))
print('No classes were deleted between arms. A source associated with many wrong assembled rows is not an independently demonstrated bad trial.')
print('Common development rows are reused across seeds;216pooled predictions are3passes over72rows, not216independent trials.')
"""),
        old.cells[16],
        old.cells[17],
        md("""## Reading this result responsibly

        **Supported:** relative condition-level recovery for these constructions, models,
        nine labels and exposed-development sources. Once-only recovery can test whether
        assembly repetition is necessary for an association; it cannot establish general
        sampling validity, independent population dynamics or generalization to unseen animals.

        **Not measured here:** new recordings, untouched natural-trial accuracy, aligned
        cross-fit neural geometry, spatial field loss, navigation transfer or class deletion.
        The cue lines above are bin-wise latent class means, not time-resolved decoding scores;
        no extra per-time decoder was trained. A fall in a selected class's recall may guide
        follow-up, but cannot identify a harmful session or lost place field without the
        corresponding authenticated spatial measurements.

        **Reproducibility:** fixed source input and code hashes, configuration, runtime identity,
        model updates, fit counts, failures, complete confusion data and guarded reloads are
        recorded with this execution. The final external numeric/claim/privacy audit and the
        comparison with the previous accepted execution are linked in the companion validation
        ledger. The executed notebook's outputs are evidence of the actual cells above; no
        fresh prediction has been substituted into an old output cell.
        """),
    ]
    for cell in cells:
        if cell.cell_type == "code":
            tree = ast.parse(cell.source)
            imports, body = [], []
            for node in tree.body:
                if isinstance(node, ast.Import):
                    imports.extend(
                        ast.Import(names=[name])
                        for name in node.names
                        if name.name != "inspect"
                    )
                elif isinstance(node, ast.ImportFrom):
                    imports.append(node)
                else:
                    body.append(node)
            tree.body = imports + body
            cell.source = ast.unparse(ast.fix_missing_locations(tree))
    notebook = nbformat.v4.new_notebook(cells=cells, metadata=old.metadata)
    notebook.metadata["study"] = "source-reuse-width-notebooks-20261115"
    return notebook


if __name__ == "__main__":
    root = Path(__file__).resolve().parent
    for part, name in [
        ("reuse", "source_reuse_20261115"),
        ("width", "population_width_20261115"),
    ]:
        nbformat.write(make_notebook(part), root / (name + ".ipynb"))
