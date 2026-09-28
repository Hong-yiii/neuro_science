<!-- markdownlint-disable MD033 MD051 -->
<!-- Trusted local presentation markup. render.py inserts the saved-artifact widgets and diagrams. -->

# From neural recordings to prospective-path decoding

<p class="subtitle">Pseudopopulations → CEBRA-Time → cue-only readout → what joint cue/navigation training changed.</p>

**Professor discussion · 28 September 2026 · completed exploratory research, with proposed next steps clearly separated.** This review redraws saved results and reuses saved projections; it adds no biological model fits.

<div class="takeaways">
<div><b>What works</b><p>Endpoint conditions are decodable in the synthetic-population benchmark. Representation, training duration and readout choices matter.</p></div>
<div><b>What changed</b><p>Joint cue/navigation training improved CEBRA-Time's cue-only path-component readout relative to cue-only training.</p></div>
<div><b>What remains open</b><p>The complete success rule failed. Prospective path information beyond endpoints—and its reproducible geometry—are not established.</p></div>
</div>

The biological question is: **before movement, does hippocampal activity contain information about the subsequently observed path beyond start and goal?** Endpoint classification is a useful supporting benchmark, not that hypothesis itself. H1a concerns incremental path information; H1b concerns its reproducible low-dimensional organization. [S1](#s1)

## 1. Raw recordings → pseudopopulations

### What is measured, and what we construct

The inputs are sorted spike timestamps, Ripple trial markers, and behavioral records from Unity/VirtualMaze; eye-tracking is another potential alignment/confound stream. A sorted **unit** is treated as a cell's activity, but its identity has already been inferred upstream. Counts, endpoint labels, graph components and embeddings are derived quantities—not direct measurements of intention.

@@DATAFLOW@@

For a complete 100-ms interval, three detected spikes mean a **count of 3** (equivalently 30 spikes/s if expressed as a rate). These analyses use count features. Zero recorded spikes and an unrecorded cell are different: the latter is missing, not zero. The cue representation uses ten nominal 100-ms bins from cue onset. The endpoint study requires a complete first second; the later path pipeline clips to actual cue offset where needed. [S2](#s2) [S3](#s3)

In the endpoint study, start/goal IDs are operational labels inferred from marker digits: the previous successful trial supplies the start digit, and the current successful trial supplies the goal digit. Their formal task semantics and recording-group metadata still need laboratory confirmation; they are not measured Cartesian coordinates. [S2](#s2)

### Assemble intact source blocks, not an imaginary simultaneous trial

A session contributes one eligible real trial, with **all its recorded units and all ten bins kept together**. Concatenate matching blocks across sessions. Keep the chosen source fixed across bins; do not redraw it at each time point.

@@ASSEMBLY@@

<p class="caption">Illustrative numbers, not laboratory observations. The matching key is the known start–goal pair for the endpoint benchmark, or fixed endpoints plus component absent/present for the path benchmark. The same principle applies to many session blocks.</p>

<div class="two-col">
<div class="card"><span class="tag">Endpoint benchmark</span><h3>195 units · 58 sessions</h3><p>15,553 eligible real sources, split into 12,288 training and 3,265 development sources within the old training partition. Per seed: <b>480 training / 240 development pseudorows</b>, each 195 units × 10 bins.</p></div>
<div class="card"><span class="tag">Latest path-component benchmark</span><h3>29 units · 7 session blocks</h3><p><b>82 training / 22 historical-validation sources.</b> Per seed: 128 training pseudorows; all 30 supported evaluation combinations, 24 absent and 6 present, with each class weighted equally.</p></div>
</div>

These are **two different cohorts and evaluation objects**, not successive sample sizes in one leaderboard. The archive is place-selected, not an unbiased sample of all hippocampal cells. The smaller component panel reflects behavioral/source support, not an individual-cell significance gate. [S2](#s2) [S3](#s3)

<div class="warning"><b>What this construction can support:</b> condition-level associations across disjoint real-source pools. <b>What it cannot recover:</b> cross-session noise correlations, a simultaneous population state, or the full path of one real trial. True labels also determine evaluation assembly: this is a <b>known-condition benchmark</b>, not deployment on an unknown natural trial. Reusing one source in 50 rows does not produce 50 independent observations. Same-session grouping alone does not verify simultaneity.</div>

### What the real-source and synthetic class distributions show

@@SOURCE_SUPPORT@@

These counts describe **eligible analysis cohorts**, not every trial recorded by the lab. Near-balanced aggregate endpoint counts do not guarantee robust session-level support. The smaller fixed4→3 assay reverses the apparent class proportions between real validation sources (12 absent/10 present) and synthetic combinations (24/6). Balance the metric deliberately; do not mistake resampling or weighting for new biological evidence. Whole ordered-path distributions across endpoint pairs still require a defensible behavior-only route definition and support audit; component presence is not that distribution.

**The essential split rule:** assign real sources before assembly or learning; keep their cue, navigation and all derivatives on the same side. Train normalization, encoders and readouts only on training sources. Existing development pools have been repeatedly inspected; resplitting them cannot create a pristine confirmation set. Fold count and serial/temporal handling for new work remain to be specified.

## 2. Model architecture: learn features, then learn a readout

### A pointwise neural encoder—not an RNN

CEBRA-Time maps **one population count vector from one bin** into eight coordinates. “Time” describes how training pairs are sampled; it does not mean the network recurrently reads the entire trial. The actual `offset1-model` is a small multilayer perceptron with GELU activations and a unit-length output. [S4](#s4)

@@ENCODER@@

<p class="caption">Exact layer widths: 195→32→32→16→8 for endpoints; 29→32→32→16→8 for the later path cohort. Circles are schematic, not a drawing of every artificial unit. These are model layers, not a proposed biological circuit.</p>

For each cue, apply the **same encoder** to all ten bins, preserving order. Concatenate the ten eight-coordinate outputs to make **80 readout features**. Eight dimensions per bin are not eight dimensions for the whole cue, and choosing eight outputs does not identify the brain's dimensionality.

### The two learning problems

<div class="two-col">
<div class="card"><span class="tag">1 · Encoder training</span><h3>Contrastive / InfoNCE objective</h3><p>Make a reference bin relatively more similar to its designated nearby-time partner than to sampled background bins. “Positive pair” means related examples, not a path-present trial. Background samples need not have opposite behavioral labels.</p></div>
<div class="card"><span class="tag">2 · Decoder training</span><h3>Supervised target prediction</h3><p>Freeze the encoder, transform training cues, then fit a target-specific readout. Logistic regression learns a linear boundary in 80-feature space; a nonlinear decoder can learn a different boundary. Every representation gets newly fitted decoder weights.</p></div>
</div>

CEBRA-Time does not use endpoint/path labels **in its temporal objective**. The assembled inputs are nevertheless condition-matched. Thus “Time is label-free” would be misleading for the full pipeline. Lower InfoNCE loss proves neither successful readout nor biological path information.

### Baselines are parallel routes—not PCA before CEBRA

@@BASELINES@@

**Raw counts** test whether compression is needed. **PCA** fits a training-only linear basis retaining variance, not necessarily the most target-relevant information; eight coordinates/bin again give 80 readout features. **LDA** is supervised: it uses labels to find discriminating directions and/or classify. It has at most K−1 discriminant dimensions for K classes—one for a binary component target—not an automatic eight-dimensional counterpart to PCA. Historical LDA companions used per-bin raw inputs; a newly matched LDA policy remains to be defined. [S1](#s1) [S2](#s2)

## 3. Evaluation: distinguish endpoints from path information

There are **four outputs, grouped into two questions**. “Start/end” here means the ordered start–goal pair; start-only and goal-only are distinct diagnostics.

@@TARGETS@@

<div class="two-col">
<div class="card"><h3>A · Endpoint conditions</h3><ul><li><b>Ordered pair:</b> 30 classes; balanced chance 3.33%.</li><li><b>Start alone:</b> six classes; chance 16.67%.</li><li><b>Goal alone:</b> six classes; chance 16.67%.</li></ul><p>In the original baseline and endpoint follow-up, start/goal scores use the <b>endpoint components of the argmax predicted pair</b>, not separately trained heads or sums of pair probabilities. A later separate-goal LDA diagnostic exists; it is not a joint-training endpoint comparison.</p></div>
<div class="card"><h3>B · One graph component</h3><p>Within fixed 4→3 endpoints, predict whether the later path contains <code>D_N_R_T__N_R_M</code> after boundary corridor runs are excluded. This binary assay asks about one interior directed component—not an entire ordered route.</p><p>Balanced accuracy chance 50%; AUROC chance 0.5; constant-.5 probability loss ln2 ≈ 0.693147.</p></div>
</div>

The diagram's maze is a **teaching schematic**, not the laboratory map. Its two paths share endpoints but differ in one edge. Fixing endpoints removes changing endpoint identity as the within-assay separator, not all cue, view, history or session confounds. Component-conditioned pseudorows can combine sources with different full routes: they do not automatically have one valid ordered-path ground truth. [S1](#s1) [S3](#s3)

### Three complementary readings of a binary decoder

- **Balanced accuracy:** average recall of absent and present classes at the fixed decision rule. Avoid being rewarded simply for the more numerous synthetic class.
- **AUROC:** how well scores rank present above absent examples across thresholds. It need not agree with accuracy at one threshold.
- **Balanced log loss:** probability quality, with each class receiving half the total weight. Confident errors are costly; smaller is better.

The latest study required **all four**: joint-training loss gain≥0.01nats, joint BA>50%, joint AUROC>0.5, and joint loss<ln2. Improvement over a weak cue-only model is not sufficient. Source-coherent nulls and source sensitivity address additional questions; computational seeds and synthetic rows are not biological replicates. [S3](#s3)

## 4. Cue-only training: sampling, saved curves and latent views

### How one training example is produced

```text
# One-time assembly, separately within each real-source split
for condition in supported_conditions:
    for requested synthetic row:
        choose one eligible real source per session, with replacement
        retain all observed units and cue bins from each chosen source
        concatenate session blocks; save contributing source IDs

# CEBRA-Time optimization on training rows only
for update in fixed_budget:
    sample reference row and a valid adjacent-bin pair (t, t+1)
    sample background row/bin independently from the training pool
    encode reference, partner and backgrounds with shared parameters
    update encoder using contrastive loss

freeze encoder
fit target readout on encoded training cues
evaluate encoded development cues from disjoint real-source pools
```

This is conceptual pseudocode, not a second implementation. The executed samplers keep temporal positives inside a source-derived pseudorow and within a phase. Assembly is fixed per run, rather than creating independent biological trials every optimizer update. More pseudorows may improve coverage of the existing pool but cannot manufacture new sources. [S4](#s4) [S5](#s5)

### Encoder loss and held-out decoding can move in different directions

@@ENDPOINT_LOSS@@

The overlaid curves are **saved training InfoNCE traces for all three endpoint Time seeds**, not validation losses. The 250- and 1,000-update markers belong to the same training trajectories. All traces extend to 3,000 updates; the curated viewer below deliberately compares only the two selected historical checkpoints.

<div class="result-strip"><div><span>Time ·250 updates</span><b>69.72%</b><small>pair development accuracy</small></div><div><span>Time ·1,000 updates</span><b>51.67%</b><small>same logistic C=.01 policy</small></div><div><span>PCA reference</span><b>83.61%</b><small>C=.01 follow-up, same endpoint task</small></div></div>

These are three-seed means from the exploratory endpoint follow-up, not the original C=1 baseline. Training loss can decrease while development decoding worsens. That supports inspecting representation **and readout together**; it does not establish a universally optimal early stop, prove an information-free late representation, or show that a stronger decoder would rescue it. The historical sampler/objective investigations are preserved, but **CEBRA-Behavior is outside the next comparison's scope**. [S5](#s5)

### Performance across the three selected endpoint representations

@@ENDPOINT_PERFORMANCE@@

Counts and row-normalized confusion matrices are both retained above. The complete30-class pair view is dense by necessity; the six-class endpoint views help locate start-versus-goal errors. All seeds are included in the performance plots. Pooling their confusion counts is descriptive only; it does not increase the biological sample size.

### How decoding changes throughout the cue

@@TEMPORAL_RESULTS@@

**These are real saved results, but a different readout assay:** historical plain LDA on raw195-unit count bins, trained separately for pair, start and goal. The direct start/goal heads here are not the endpoint components of the whole-cue pair decoder above. Three-seed thin curves show computational variation, not biological confidence intervals. A changing curve may reflect changing target accessibility to this readout; it does not uniquely identify changing neural information or a mechanism.

The goal heatmap freezes one decoder per training-time row across evaluation times. This already tests **within-cue temporal generalization**, not cue↔navigation transfer and not joint-trained CEBRA. Its diagonal matches the direct-goal cue curve. No window or bright cell is selected as a new confirmatory finding. **Time-arm per-window comparisons, navigation decoding and cross-phase generalization remain unmeasured in this delivery.**

### A small saved-model viewer

@@VIEWER@@

**How to read it:** choose Time 250, Time 1,000 or PCA; then inspect all three computational seeds. Start/goal color identifies the known assembly condition. Every dot is a **whole synthetic cue**, not one natural trial or a maze location. Its three plotted coordinates come from a saved training-fitted display projection of the 80-feature whole-cue representation. The actual decoder used all 80 features, not these three display coordinates. No new projection was fitted for this review. [S6](#s6)

Cluster appearance, spherical shape and arbitrary axis orientation do not establish H1b or a cross-phase rotation. In particular, CEBRA's unit-length per-bin output constrains geometry by design. Train/development separation, source reuse and projection loss remain important even when a plot looks clean. The menu is a **geometry comparison**, not a matched decoder leaderboard: the archived atlas PCA scores used C=1 whereas these Time checkpoint readouts used C=.01; scores are intentionally omitted from the viewer.

## 5. Joint cue/navigation training: more coverage, not more updates

### The completed comparison

The 24–25 September experiment trained **two Time encoder arms from paired initializations**, using the same 29-unit cohort, source split, architecture and 1,000-update budget. One arm saw cue only. The other sampled cue and navigation with equal phase probability. After training, **both were tested using cue only**. This completed study predicts the binary 4→3 component—not endpoint pairs. The proposed joint-training endpoint benchmark has **not been run**. [S3](#s3)

@@JOINT_PIPELINE@@

The shared input scaler was fitted to training cue only and applied to both phases. Each readout also had training-only feature scaling. Neither held-out navigation activity nor its neural features entered learning or cue prediction. Behavior still supplied labels and conditional assembly. “Joint” means shared encoder parameters—not navigation pretraining followed by cue fine-tuning and not proven shared biological geometry.

### Unequal amounts of cue and navigation data

Cue has ten nominal bins. Navigation durations vary: the 82 training sources had **46–192 complete 100-ms navigation bins**, median 69.5. Simply pooling all bins would change the relative phase exposure substantially. The executed design instead used:

1. **Phase balance:** draw cue/navigation with probability .5/.5; cue-only uses cue probability 1. The same 1,000 updates therefore mean less cue exposure in the joint arm, not identical cue exposure plus free navigation.
2. **Row balance:** draw a training pseudorow uniformly, then a valid within-row pair. Longer navigation does not automatically receive a larger row-selection probability; real-source reuse still varies.
3. **Native adjacency:** align a pair bank by relative navigation duration, while each source contributes two genuinely adjacent native bins. No padded zero counts or interpolated spike values. Cue tails beyond the first second and final partial navigation bins are not included.

@@NAV_PAIRS@@

<p class="caption">Fictional two-source example: A has 4 complete bins, B has 7. At bank position j of L=max(n−1), q=(j+.5)/L and source index k=floor(q(n−1)); take k→k+1. A can repeat a pair while B advances. Relative duration is <b>not physical-position alignment</b>; consecutive bank entries are not a single uniformly sampled population trajectory.</p>

Time positives stay within cue or within navigation: there are **no explicit cue↔navigation positive pairs**. The intervention changes phase coverage, positive/background distributions and cue exposure together. Better cue decoding could reflect useful shared features, sampling or regularization effects; this design alone cannot identify the mechanism.

@@JOINT_LOSS@@

These saved encoder curves are separate from the endpoint chart because their cohorts, optimization settings and sampling distributions differ. Even within this chart, the joint arm has a different sampling objective: absolute InfoNCE values are not a common held-out performance metric.

### What the cue-only readout actually achieved

@@JOINT_RESULTS@@

| Three-seed mean · logistic C=.01 | Cue-trained | Joint-trained | Uninformative reference |
| --- | ---: | ---: | ---: |
| Balanced log loss ↓ | 1.010464 | 0.710618 | 0.693147 |
| Balanced accuracy ↑ | 32.64% | 61.81% | 50% |
| AUROC ↑ | 0.146 | 0.574 | 0.5 |

@@JOINT_DETAIL@@

**Loss improved in all three paired seeds; the average gain was 0.299846 nats.** The first three rule components passed, but joint loss remained worse than ln2: **the complete success rule failed**. Only seed 0 had joint AUROC above .5; seeds 1/2 were .361/.472. A favorable average should not hide this variability. [S7](#s7)

<div class="warning"><b>Strongest defensible statement:</b> joint Time training improved this particular exploratory, conditional cue-readout comparison relative to cue-only training. It did not establish reliable absolute path discrimination, unknown-real-trial prediction, intention, H1a or H1b.</div>

<details>
<summary>Nulls, support and computational verification—in brief</summary>
<p>The finite relative-Time null tail was 1/21, but the historical maximum across both tested objectives was 3/21 and the absolute joint-Time tail was 12/21. These ask different questions; selecting the smallest does not establish biology. Only 22 real evaluation sources underlie 30 combinations; deleting 8 particular singleton sources separately makes the full class comparison inestimable. The accepted study forward-replayed 1,071 fitted artifacts with 4,681 hashes; this report reuses those receipts rather than rerunning fits. Verified computations do not verify acquisition metadata or eliminate historical selection and confounds.</p>
</details>

## 6. Decoder comparisons: capacity matters, but it is not the proven bottleneck

A decoder is an assay of the representation, not an oracle for all information it may contain. A weak score can reflect features, training sources, labels, regularization, readout choice or mismatch to the scientific target. A more flexible model can also overfit the limited independent sources.

@@DECODERS@@

<div class="three-col">
<div class="card"><span class="tag">Endpoint diagnosis · frozen features</span><h3>Regularization helped</h3><p>Time pair accuracy: <b>42.78%→51.67%</b> when scaled logistic C changed 1→.01. Cosine kNN reached 50.14%, but had very poor probability loss. Same task; no encoder refitting.</p><p class="caption">Changing readout policy matters, but did not close the PCA gap. <a href="#s4">S4</a>.</p></div>
<div class="card"><span class="tag">Older frozen path encoders</span><h3>No nonlinear Time rescue</h3><p>Time BA: <b>24.92%→37.33%</b>, logistic→best tested nonlinear RBF. Still below 50%. PCA in that study went 42.92%→77.50%, an exploratory control lead—not a confirmed biological result.</p><p class="caption">Eight tested policies; no MLP sweep. <a href="#s8">S8</a>.</p></div>
<div class="card"><span class="tag">Latest joint Time encoders</span><h3>More flexible was not better on BA</h3><p>Joint-trained Time: logistic <b>61.81% BA</b>, RBF <b>50.69% BA</b>. RBF's mean AUROC was higher (.634 vs.574), illustrating that metric choice also matters.</p><p class="caption">Fixed policies, three seeds; not proof logistic is globally best. <a href="#s7">S7</a>.</p></div>
</div>

**Do not pool these cards into one leaderboard.** The endpoint target, frozen path encoders and new joint-training experiment differ. Likewise, the earlier matched raw/PCA preprocessing study is a separate completed experiment—not an unexecuted task to restart. [S9](#s9)

For probabilities, logistic uses softmax for the pair task or sigmoid for a binary component. The tested RBF-SVM produced **uncalibrated margins**, so log loss was not assigned to it. A future probability-loss comparison would require **training-only calibration** under the same source-safe selection policy. The proposed MLP would be a new bounded challenger, not a decoder already shown to work.

## 7. Future steps: separate decoder selection from the joint-training comparison

**Agreed direction:** keep H1, remove artificial-agent H2, focus on CEBRA-Time, cue-only versus joint training, two predefined checkpoints, deliberate source folds, and PCA/LDA references. Decoder and detailed run protocol remain open. Phase-selectivity/rotation awaits the mentor's clarification and literature, not an inference from shared weights. [S1](#s1)

@@FUTURE@@

### September28 agreement: support → plots → bounded validation protocol

**Agreed, not merely suggested:** all future scientific documents should stand on their own with data and graphs. Each empirical figure states its question/target, cohort, source versus synthetic counts, split, time/units, model/readout, baseline, uncertainty meaning and provenance. Schematics and unavailable results must be labelled. Existing exposed data remain exploratory. The [full agreed validation plan](validation-plan.md) records this decision and the remaining prefit gates.

1. **Source support first:** audit unique real-trial start, goal, pair and path/component distributions; within-pair path variation; session/fold support; and synthetic source reuse. Do not count neurons, bins or synthetic combinations as additional real trials.
2. **Expose saved results:** show performance, paired arm differences, counts plus normalized confusion matrices, and all available temporal results—not just a favorable headline or latent picture. This delivery supplies the saved evidence above; it does not claim a complete new methods-validation program.
3. **Primary future comparison:** evaluate whether cue+navigation encoder training improves held-out **cue** decoding relative to cue-only training. Use separately fitted decoders under the same selected policy for each encoder/seed/fold/checkpoint.
4. **Separate supporting assay:** freeze encoder, input scaler, readout scaler, decoder weights/thresholds/calibration within each representation. Train a readout on training-source navigation and score both held-out navigation and cue; optionally test the reverse direction with a separately trained cue readout. No evaluation-phase refitting or learned alignment. A working within-phase reference is needed to interpret transfer failure.

<div class="two-col">
<div class="card"><span class="tag">Planned · per-window decoding</span><h3>When is a target accessible?</h3><p>Fit a separate decoder per cue/navigation window on training sources. Score the same window on held-out sources. Plot pair/start/goal/component performance and paired joint-minus-cue differences where estimable.</p></div>
<div class="card"><span class="tag">Planned · frozen generalization</span><h3>Does the readout transfer?</h3><p>Fit once per training-window row; freeze across all held-out evaluation-window columns. Show cue→cue, navigation→navigation and cross-phase blocks separately. Never refit each matrix cell or transfer weights blindly across independently fitted encoders.</p></div>
</div>

**Feature/time gates:** a historical80-feature whole-cue decoder cannot be applied to an8-feature bin. Predefine compatible windows/aggregation. Cue axes need onset-relative time and boundary handling; navigation needs declared event-time or normalized-progress alignment and per-window support. Relative progress is not physical time, position or simultaneity. Historical navigation pair banks are training samples, not automatically valid time-resolved population evaluation tensors. Long trials and missing bins need explicit weighting/masks, not zero padding.

**Interpretation:** successful frozen transfer supports task information accessible to a common readout, not identical biological manifolds, phase rotation, intention or H1 by itself. During navigation, decoding a component already traversed can concern current/past behavior, not prospective coding. Keep target semantics and endpoint/nuisance controls explicit. Source folds must keep both phases and every derivative together; every learned transform and inner selection step excludes evaluation sources. New target/windows/folds/checkpoints, decoder policy, calibration, controls, multiplicity and the complete fit budget still require a reviewed frozen protocol and run authorization.

### Proposed endpoint representation benchmark—not yet frozen or run

1. **Define the target and metric.** A suggested arrangement is pair prediction primary, with separately trained start/goal heads as diagnostics. This remains a proposal, not a decision or a substitute for path beyond endpoints. Specify whether selection uses accuracy, balanced accuracy or calibrated probability loss.
2. **Stage A: choose a bounded decoder policy.** Compare logistic with RBF-SVM; add a small MLP only if explicitly justified and budgeted. Represent both encoder-training arms and both checkpoints so the policy is not selected for one favorable representation. All learned transforms—including the encoder—must respect the inner source boundary; do not let an inner validation source enter encoder fitting.
3. **Stage B: lock the policy, compare the encoders.** On separate outer source folds, evaluate cue-trained versus joint-trained Time at both predefined checkpoints. Fit new decoder weights for each representation, but keep a common family/training-selection policy and matched metric. Retain logistic as an interpretability diagnostic if a nonlinear policy wins.
4. **Keep baseline and source fairness.** Fit raw/PCA/LDA references on identical sources and folds. Check endpoint support and serial dependence before fixing fold count. Predefine phase weighting, exposure accounting, checkpoints, seeds, nulls and total fit budget; save both checkpoints along each training trajectory where possible.

“Best among the tested, selected policies” is defensible; **“optimal decoder” is not**. Neither this report nor a PR authorizes a new fit.

### Return to the biological question

A successful endpoint comparison would help choose a representation/readout policy. The subsequent path assay must still compare **start+goal alone** against **start+goal+cue activity**, with appropriate nuisance controls and source-aware evaluation. For full ordered graph paths, first establish a defensible route-level target and construction: do not assign an arbitrary constituent trial's route to a component-matched pseudorow.

The next methods artifact is the agreed construction/provenance document with runnable source, mask, count, phase-boundary and lineage checks. This review explains the construction; its software checks verify the presentation, **not completion of that methods-validation program**.

<div class="callout"><b>Questions for the professor:</b> Which path distinction is biologically meaningful and adequately supported? Is the endpoint benchmark a useful intermediate assay? Which recording-group, marker and history metadata can resolve the largest uncertainties? What evidence would distinguish useful joint-training transfer from a claim about common biological geometry?</div>

### Evidence and reproduction

The report is self-contained: figures, saved geometry, loss traces, controls and the HTML download work without a network. Source links below open private GitHub records only when deliberately followed; the local source Markdown is readable separately. Derived research coordinates remain private—share only through approved channels.

- <span id="s1"></span>**S1 · Current authority:** [agreed direction](../../project-direction.md), [research questions](../../research-questions.md), [analysis contract](../../analysis-contract.md).
- <span id="s2"></span>**S2 · Endpoint construction and original scores:** [start–goal baseline](../../reports/start-goal-cebra-baseline.md).
- <span id="s3"></span>**S3 · Completed joint-training design:** [protocol](../../reports/cebra-full-trial-transfer/protocol.md), [report](../../reports/cebra-full-trial-transfer/README.md), [execution](../../reports/cebra-full-trial-transfer/execution.md), [implementation](../../../scripts/cebra_full_trial_transfer.py).
- <span id="s4"></span>**S4 · Architecture and readout diagnosis:** [endpoint diagnosis](../../reports/start-goal-cebra-diagnosis.md), [CEBRA helper](../../../scripts/place195_v8b_v9_cebra.py), [endpoint study code](../../../scripts/start_goal_autoresearch.py).
- <span id="s5"></span>**S5 · Saved endpoint follow-up:** [report](../../reports/start-goal-autoresearch.md), [journal](../../reports/start-goal-autoresearch-journal.md). Curves: <code>outputs/start-goal-autoresearch-20260907/02-cebra/time_t1_seed{0,1,2}/loss.csv</code>.
- <span id="s6"></span>**S6 · Previously generated geometry:** [atlas results](../../reports/cebra-latent-atlas-results-20260924.md), [portable atlas](../../reports/cebra-latent-atlas/atlas.html), [saved summary](../../reports/cebra-latent-atlas/summary.json). Nine endpoint run/checkpoint objects are selected; no new projection fit.
- <span id="s7"></span>**S7 · Joint numerical evidence:** [machine summary](../../reports/cebra-full-trial-transfer/summary.json), [verification](../../reports/cebra-full-trial-transfer/verification.json), [independent numerical review](../../reports/cebra-full-trial-transfer/reviews/numerical-result-review.md). Curves: observed world only, <code>outputs/cebra-full-trial-transfer-20260924/biological-run-20260924T162913Z/worlds/00_observed/seed{0,1,2}/encoders/{cue_time,full_time}/loss_trace.csv</code>.
- <span id="s8"></span>**S8 · Frozen-path decoder evidence:** [decoder study](../../reports/cebra-decoder-autoresearch-20260924.md), [later regularization diagnosis](../../reports/cebra-hyperparameter-diagnosis-20260924.md).
- <span id="s9"></span>**S9 · Separate matched preprocessing study:** [completed raw/PCA comparison](../../reports/path-pca-matched/README.md). Executed13–14 September; merged23 September. It is not the PCA control in S8.

<p class="caption">Evidence revision:fac639b. Small presentation payloads preserve source paths and hashes. Read the adjacent README for deterministic rebuild/check commands, review receipts and the temporary-preview lifecycle. Historical reports can contain superseded recommendations; S1 governs future scope.</p>
