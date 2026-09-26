# CEBRA latent geometry: website references and a bounded next step

Date: 2026-09-23 (Asia/Singapore).
Status: literature/artifact review and **proposed exploratory visualization**; no new biological fits or latent-space measurements in this review. Not a replacement for the separate [matched PCA/non-PCA PRD](path-pca-matched-prd-20260913.md).

## Recommendation

**Yes: use the CEBRA website's linked neural/behavioral display and rotatable embedding as presentation references. Start with saved encoders, not another training search.** Compare train and source-held-out development geometry, keep the full latent dimension for quantitative checks, and distinguish endpoint separability from prospective path information.

The question should be: **which structure is reproducible, relates to the intended behavioral variable beyond relevant controls, and survives the choice of projection?** Not: can we find a run or viewing angle that resembles a ring?

For the team, separate three deliverables:

1. A saved-run atlas: existing CEBRA-Time/Behavior and PCA, multiple colorings and seeds, no encoder retraining.
2. Quantitative geometry checks: projection fidelity, dimensionality diagnostics, cross-run/source consistency, and existing matched decoding results.
3. Only if justified and separately frozen: a small matched dimension/objective experiment or topology analysis with appropriate full-pipeline controls.

## 1. Exact references for the supplied screenshot

The [CEBRA homepage](https://cebra.ai/) contains two different objects, verified from its HTML:

| Screenshot panel | Direct source | What it represents |
| --- | --- | --- |
| Left: neural raster, position/decoding trace, three latent traces and moving point | [Rat hippocampus video](https://cebra.ai/static/videos/rat.mp4) | CEBRA-Behavior on Grosmark–Buzsáki rat recordings during **current navigation**, not a cue-to-future-path experiment. |
| Right: rotatable colored point cloud | [Interactive hippocampus embedding](https://cebra.ai/static/img/hippocampus_posdir3_full.html) | A 3D latent display associated with position and movement direction; the axes are learned coordinates, not physical maze coordinates. |
| Reproducible teaching reference | [Official hippocampus notebook](https://cebra.ai/docs/demo_notebooks/Demo_hippocampus.html) | Demonstrates Behavior, shuffled Behavior, Time, Hybrid, decoding and topology. Demo settings and evaluation are not automatically a publishable protocol. |
| Scientific reference | [Schneider et al. 2023, Figure 2](https://www.nature.com/articles/s41586-023-06031-6/figures/2) | Panels b–d: objectives, labels, shuffle and decoding. Panels e–g: persistent cohomology and topology across dimensions. |

The official notebook also provides this directly relevant comparison image:

![Official CEBRA notebook: Behavior, shuffled Behavior, Time and Hybrid embeddings](https://cebra.ai/docs/_images/demo_notebooks_Demo_hippocampus_46_0.png)

*Credit: CEBRA authors, official hippocampus demo. Externally linked, not copied into this repository; requires internet. This particular demo image is not a guarantee that Time and Behavior recover identical shapes. The Time panel looks more broadly sphere-like than the Behavior panel.*

The paper's rat task is a 1.6 m linear track traversed in both directions. Its reported loop relates to position **and direction**; the physical track itself is not circular. Each point represents a time-binned neural population observation. The paper supplies quantitative evidence beyond the picture. We can borrow its presentation and validation logic without expecting the same topology from our different task and data construction.

## 2. What the papers contribute

### Schneider, Lee & Mathis (Nature, 2023): directly relevant

[Full paper](https://www.nature.com/articles/s41586-023-06031-6).

- Figure 1 and Methods, “Sampling”: CEBRA learns which neural observations should be similar through its positive/negative sampling distributions. Behavior uses auxiliary labels; Time uses temporal relationships; Hybrid combines objectives. Behavior conditioning shapes geometry rather than independently discovering the supplied labels.
- Figure 2b compares Time, Behavior, Hybrid and shuffled supervision. The published hybrid example uses five dimensions; the current demo is a separate configuration. Do not treat every implementation of `hybrid=True` as the same latent partition.
- Figure 2e–g and Methods, “Topological analysis”: the authors examined **3, 8, 16, 32 and 64** output dimensions, used persistent cohomology, and compared against shuffled-label-trained embeddings. Methods describe 1,000 sampled points and 500 shuffled fits for this analysis. These are their settings, not our recommended run budget.
- The reported ring has Betti numbers `(1,1,0)` for connected components, loops and two-dimensional cavities. That is evidence about topology, not evidence of three intrinsic degrees of freedom.
- Methods, “CEBRA models”: most cosine-based models normalize their final vectors. An E-coordinate normalized embedding lies on `S^(E-1)`. A spherical appearance can therefore arise from the model constraint. The paper explicitly contrasts its ring with a uniformly occupied sphere under shuffling.
- Methods, “Consistency”: embeddings are compared by linear-regression R²; corresponding samples/behavioral bins matter. Arbitrary learned axis names do not have fixed meanings across runs.
- Methods, “Decoding analysis”: rat CEBRA-Time and some unsupervised comparators were fitted on the full unlabeled dataset, splitting only the downstream decoder. The topology analysis also used the full dataset. **Our proposed source-held-out evaluation should instead fit encoders and learned transforms on training sources only.** Copying the picture is not permission to inherit a transductive evaluation.

### Jazayeri & Ostojic (2021): distinguish the dimensions

[Full review](https://pmc.ncbi.nlm.nih.gov/articles/PMC8688220/), especially Box 1 and “Dimensionality of Neural Activity.”

| Quantity | Meaning here | What it does not establish |
| --- | --- | --- |
| Output/ambient dimension E | Number of coordinates emitted by our encoder, such as 3 or 8 | Number of biological variables |
| Linear effective dimension | Number/participation of variance-bearing directions; PCA spectrum is one diagnostic | Intrinsic dimension of a curved object |
| Intrinsic dimension | Local degrees of freedom needed to describe the sampled structure | A reliable estimate merely because an estimator returns a number |
| Topology | Connectivity and holes that persist across distance scales | Circuit mechanism, intention, or predictive relevance |

A bent loop can occupy many coordinate axes while remaining intrinsically one-dimensional. An eight-dimensional CEBRA fit therefore need not represent eight independent factors; a 3D view can also hide structure. Noisy finite samples make intrinsic-dimension estimation difficult. The dimension of a learned, supervised pseudopopulation embedding is not automatically the dimension of hippocampal activity.

### Gardner et al. (Nature, 2022): how a shape claim is strengthened

[Toroidal topology of population activity in grid cells](https://www.nature.com/articles/s41586-021-04268-7), Figure 1 and “Quantification of toroidal topology.”

The authors distinguished a 3D UMAP illustration from persistent-cohomology calculations on a higher-dimensional representation, and compared topology with shuffled controls and across conditions. Borrow that separation of **view** from **measurement**. Do not borrow the expectation of a torus: their simultaneously recorded entorhinal grid-cell modules are not our selected hippocampal cue pseudopopulations.

### Schneider et al. (AISTATS, 2025): useful later, not required here

[Time-series attribution maps with regularized contrastive learning](https://proceedings.mlr.press/v258/schneider25a.html), Sections 2–4, 6–9; [full PDF](https://raw.githubusercontent.com/mlresearch/v258/main/assets/schneider25a/schneider25a.pdf).

xCEBRA adds Jacobian regularization and an inverted-gradient attribution method to relate latent factors to observed features. This addresses **which inputs relate to which factors**, not the initial need to view saved latent geometry. Its identifiability results depend on specified generative assumptions, optimization and asymptotic conditions; they are not a blanket causal interpretation of neuron importance. The paper discusses dimension selection through empirical consistency, but this is not proof that the peak of any finite-data consistency curve equals biological dimensionality. Defer xCEBRA unless attribution becomes an explicit follow-up question.

## 3. Which existing runs are worth displaying?

“Promising” needs a named task. Existing endpoint successes and path-component results must not share an undifferentiated leaderboard.

| Lane | Existing result | Role in the atlas |
| --- | --- | --- |
| Endpoint positive control | Same-pair/same-bin Behavior positives with global negatives, τ=.3, 250 updates: **83.33%** three-seed mean joint development accuracy; PCA8/bin + logistic C=.01: **83.61%** | Useful known-condition separation; not path information beyond start and goal. Include later checkpoints to show what changes as decoding worsens. |
| Endpoint Time comparison | Original Time: **69.72%** at 250 updates, **51.67%** at 1,000 | A genuine Time comparator already exists; do not relabel time-matched Behavior as Time. |
| Endpoint augmentation sensitivity | Time-matched Behavior, τ=.3, 3,000 updates: **81.53%** with 64 training pseudorows/class | Separate sensitivity, not an independently confirmed winner. Larger synthetic samples also use more of the existing source pool. |
| Accepted V9 path benchmark | Mean validation BA **0.4427 Time-8**, **0.4141 Behavior-8**; both 3D and 8D variants exist | Matched negative/fragile comparison, not a new path success discovered by visualization. |
| Later path generalization | Completed source-pool study; corrected Track B family p **19/21** | Distinguish training-source mixture transfer from independent-source transfer. No broad robust H1 result to illustrate as established. |

Authorities: [endpoint report](start-goal-autoresearch.md), [V6–V9 report](place195-v6-v9-autoresearch-20260906.md), [path completed-state report](path-generalization-completed-state-20260907.md), and [workspace relocation map](../workspace.md).

Select **recipes and checkpoint times before looking at their new plots**, include every saved seed for those choices, and retain a baseline and nonpositive comparator. The historical scores already participated in exploratory selection; calling this a frozen shortlist does not make them independent confirmation. The September 8 preprocessing study and September 13 proposed PCA comparison are not additional successful CEBRA fits.

### Existing evidence that a 3D view will be incomplete

The early endpoint recipe already has saved `geometry.json` diagnostics: across seeds 0–2 at step 250, the first three training singular directions account for only **56.0–65.8%** of the pooled cue-bin latent variance. Saved training participation ratios are **5.34–6.18**, and latent norms are approximately one. This is a concrete reason not to rely only on a 3D plot.

These are descriptive **linear** diagnostics of the eight-coordinate learned representation, not newly estimated intrinsic dimensions or biological evidence. `scripts/start_goal_autoresearch.py::geometry` reshapes saved features to `(-1, dim)` and computes separate spectra within each split. Its development spectrum is therefore not an out-of-sample projection-fidelity measurement; the proposed atlas must fit its display basis on training only. No new SVD or model fit was run for this review; the percentages above sum the first three saved variance fractions.

### Verified saved-artifact map

All roots below are relative to `~/neuro_science`; `s` means each of seeds 0, 1 and 2, not a chosen best seed.

- **Endpoint atlas root:** `outputs/start-goal-autoresearch-20260907/02-cebra/`. Start with `positive_bin_t03_seed{s}/readout00250/embeddings.npz`; retain its `readout03000/` counterpart. Add `time_t1_seed{s}/readout00250/` and `readout01000/`, plus `behavior_t03_seed{s}/readout00250/` to show the matched-temperature positive-sampling contrast. Each readout directory contains saved `geometry.json` and decoder metrics. Parent verified seed-zero NPZ headers: `train (480,80)`, `development (240,80)`; configurations specify E=8 and ten cue bins. The selected Time recipe uses τ=1, whereas the promising Behavior recipe uses τ=.3: their atlas comparison is not a pure objective-only ablation.
- **Optional augmentation sensitivity:** `outputs/start-goal-autoresearch-20260907/04-scaling/pseudo64_seed{s}/cebra/readout03000/embeddings.npz`, with the matching case's `arrays.npz`, config and lineage. Do not mix these rows with the smaller-sample recipe.
- **V9 matched path comparison root:** `outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/v8b-v9-cebra-final-20260905T224554Z/v9/observed/`. All **12** `embeddings_and_decoder.npz` files exist under `{cebra_time,cebra_behavior}/dim{3,8}/seed{s}/`. Parent checked representative headers: `Z_train` and `Z_validation` are `(128,30)` for E=3 and `(128,80)` for E=8, with labels and saved scaler/decoder parameters. Reshape by the verified ten-bin convention, not by guessed column meanings.
- **Later Track B:** `outputs/path-generalization-20260907/results-20260907T081200Z/track_b/fits/<fit-id>/embeddings_predictions_decoder.npz`, alongside `metrics.csv`, `generated_assembly_manifest.csv`, `exact_evaluation_manifest.csv` and the checkpoint. Use `summary_exact_audited.json` and the package's exact audit as the inferential authority; do not select the maximum saved validation BA as a fresh result. Source-product evaluation weights and repeated sources must remain attached to its points.

The parent directly confirmed file existence and read bounded numeric-array headers without deserializing model checkpoints. One literature branch's shallow search missed the V9 NPZ files; that absence claim is rejected. Replot saved embeddings first: neither retraining nor checkpoint execution is needed merely to obtain these coordinates. Before implementing, verify matching hashes, labels, row order and source manifests; inventory is not a new full artifact replay.

Reuse `scripts/place195_v8b_v9_cebra.py::{flatten_rows,embed_rows,SameTrialTimeLoader}`, `scripts/start_goal_autoresearch.py::geometry`, the endpoint report renderer, and existing package provenance conventions. There is no identified existing CEBRA-site-style interactive atlas or persistent-cohomology pipeline to claim as already implemented.

## 4. Minimum useful atlas

### The point must have a declared meaning

Our binwise encoders map `pseudorow × cue_bin × unit` to `pseudorow × cue_bin × E`. A plot can show one **synthetic cue-bin population vector** per point in E-dimensional space. A whole-cue decoder may instead flatten ten bins into **10E features**. Do not silently conflate that decoder space with a single E-dimensional state, or label pseudorows as real simultaneous trials.

### Views

- For a saved E=3 encoder: rotatable raw latent coordinates, without an additional learned reduction.
- For E>3: a single display PCA fitted to pooled **training embeddings** for that encoder, then applied unchanged to training and development observations and every cue bin. Show explained variance and retained distance/neighborhood fidelity. This display PCA is distinct from PCA used before CEBRA or as a neural baseline.
- Provide raw coordinate-pair views as a check; do not cherry-pick the three coordinates that best separate the desired labels. If a nonlinear view such as UMAP is added later, call it a visualization only and measure geometry before that reduction.
- Recolor the same fixed coordinates by start, goal, joint endpoint condition, future path component where defined, cue bin, split, and available nuisance/source diagnostics. Endpoints are categorical, not ordinal numbers to interpolate along a rainbow.
- Separate training and development panels; show all selected seeds, not just the cleanest one. Display condition means alongside dispersion/source sensitivity so averaging does not manufacture a thin manifold.
- Each cross-session pseudorow has multiple source sessions. Do not assign it a fictitious single session color; inspect source-block reuse/composition and session-specific contributions instead.
- Connect points only within an explicitly identified row's cue-bin sequence. Label those lines **synthetic condition-level cue sequences**, not a real neural trajectory or a future navigation path. Never connect different pseudorows to create a smooth movie.

Minimal output is an offline HTML atlas plus static panels and a small provenance/metric table. Reuse existing arrays, safe checkpoint loaders and plotting dependencies. No new server, dashboard framework, lab-data upload or experiment manager is needed.

## 5. Time versus Behavior: recommended comparison

| Representation | Training relation | Interpretive role |
| --- | --- | --- |
| Raw/PCA | Neural variation, no behavior objective | Basic geometry and decoder reference |
| CEBRA-Time | Adjacent valid cue bins, within one intact source-preserving sequence | Geometry without an explicit path-label encoder objective |
| CEBRA-Behavior: endpoints | Matching start/goal conditions, with explicitly stated time matching | Endpoint positive control and confound reference |
| CEBRA-Behavior: path | Behavior-defined future component/distance; endpoint-controlled evaluation | Supervised probe of the path question, not independent discovery |
| Hybrid, optional | Defined time and behavior objectives/subspaces | Follow-up only; more moving parts are not needed for the first atlas |

**Important local correction:** V9 already has a boundary-safe Time sampler. It pairs neighboring bins within one synthetic row while preserving that row's session source blocks, and uses a single-bin encoder to avoid receptive-field crossing. Compare the saved Time and Behavior models before proposing another implementation.

However, Time omitting labels from its objective does **not** make the entire existing pipeline label-free: source blocks were assembled conditional on the behavioral label. Time/Behavior agreement would therefore be weaker than agreement between independently constructed, behavior-blind populations.

For any new matched comparison, freeze source splits, unit panels, cue window, source draws, normalization, latent dimensions, encoder capacity, training budget and downstream selection policy. Keep architecture/receptive fields within cue and trial boundaries. If behavior sampling uses empirical temporal deltas, its deltas also require genuine within-sequence time; `conditional='time_delta'` is not a license to use arbitrary row order. Labels may inform supervised training and evaluation coloring, but held-out labels must not become encoder inputs.

A fair comparison uses the same held-out task and appropriately matched decoder/tuning budgets. **Raw InfoNCE losses across different sampling objectives are not a universal ranking of scientific quality.** Optional future dimensions such as `{3,8,16}` would be a bounded proposal, not a need to reproduce the paper's full 64D sweep.

## 6. Measure shape without overclaiming

Start with inexpensive checks on the full saved representation:

1. **Projection fidelity:** how much variance and which distances/neighborhoods the 3D display preserves. An apparently collapsed view may simply lose relevant dimensions.
2. **Linear spectrum:** PCA spectrum and, optionally, participation ratio `(sum λ)^2 / sum(λ^2)`. Call this effective linear dimension, not intrinsic dimension or amount of path information. Analyze binwise E-space and whole-cue 10E-space separately.
3. **Stability:** matched-sample/condition representational distances and cross-run consistency. Compare seeds on identical evaluation objects; across different source pools, compare explicitly matched condition summaries. Estimate any Procrustes/linear alignment on training correspondences and test it out of sample. Orthogonal alignment preserves distances; a general linear regression can stretch them, so its R² measures a different equivalence.
4. **Behavioral relevance:** retain the existing held-out decoder results, and assess geometry–path relationships conditional on endpoints and available nuisances. First examine raw/PCA/Time geometry; path-supervised geometry cannot independently validate the target used to train it. Correlation among pairwise distances does not create independent observations.
5. **Only then, if support permits:** intrinsic-dimension estimates across neighborhood scales and source resamples, or persistent (co)homology on full-E distances rather than the 3D display. Report instability or inadequate support instead of forcing an integer dimension or named shape.

Topology controls must account for normalization, sampling density, disconnected categories, duplicated sources and supervised training. A normalized E=3 sphere and an E=8 hypersphere have different topology; do not apply `(1,0,1)` as a universal null at every E. For cosine embeddings, specify whether filtration uses Euclidean chord distance or angular/geodesic distance; do not silently switch metrics or treat raw `1-cosine` as an ordinary Euclidean distance.

A label-shuffle null for supervised geometry must repeat all label-dependent assembly/training/selection stages relevant to the statistic. Recoloring the same embedding or shuffling decoder labels alone is insufficient. An endpoint-conditioned path null must preserve endpoints and source/session blocks, and cannot work if no admissible label exchanges exist. For Time, distinguish disrupting valid temporal relations from testing path association; they are different null questions. A normalization-only geometric reference is useful but does not replace a scientific null.

Quantify source/session sensitivity, not confidence from thousands of correlated pseudorows or matrix entries. Synthetic product sampling can manufacture volume and apparent dimension. More points made from the same few recordings do not provide new evidence about a biological manifold. Source resampling of sparse/singleton pools is a sensitivity diagnostic, not automatically a calibrated confidence interval.

## 7. Decision and claim boundaries

- **Do now in a follow-up implementation:** saved-run atlas with source/shape metadata, baseline and negative comparators; training-only display transforms; no new CEBRA training.
- **Do only after reviewing that atlas and a frozen protocol:** small matched Time/Behavior dimension comparison, additional geometry statistics or full-pipeline topology controls. This review does not restart historical tuning.
- **Do not require:** a large simultaneous 195-cell recording before condition-level representation work. Do require verified simultaneity for exact population-state/dynamics claims.
- **Allowed descriptive outcome:** a specified learned condition-level representation has reproducible geometry on the inspected source distributions, with stated endpoint/nuisance and normalization dependencies.
- **Not established by an attractive plot:** incremental future-path information, H1b, a brain ring/torus/maze graph, intention, causal planning, or a biological attractor. Failure to see a shape does not establish H1 absence.

The original holdout exposure remains permanent. All existing development views remain exploratory. Missing nuisance metadata is a limitation, not a reason to silently infer labels or a claim that confounds have been excluded.

## Review provenance

The request was fanned out into three read-only branches: original CEBRA paper/objectives, independent geometry/topology/attribution methods, and local saved-run/code audit. Public source text and the supplied screenshot were inspected by the parent; no private data were uploaded and no checkpoints were executed. Branch logs: `/tmp/pi-subagents-uid-1000/async-subagent-runs/1f458767-b49e-49bf-ad3f-9fb91a4ffb39/output-{0,1,2}.log` (temporary harness records, not required to use this note).

Convergence: reuse saved representations; show Time and Behavior with raw/PCA; evaluate full-space stability rather than prettiness; preserve condition-level claims. We do **not** adopt the suggestion to immediately plot every coordinate triple or run topology/circular coordinates: a fixed small set of views plus projection diagnostics answers the first question with less selection freedom. Nor do we require the neural representation's topology to equal the physical maze's topology. A specific topology hypothesis needs its own defensible behavioral/representational rationale.

Independent fresh-context synthesis review completed with **no findings**: `/tmp/pi-subagents-uid-1000/async-subagent-runs/563e5696-8f55-40e1-b373-9590e102fd8e/output-0.log`. The reviewer checked primary-paper/demo text and local code/artifact evidence; the supplied screenshot was inspected by the parent, not independently by that reviewer. This is bounded AI-assisted source/science review, not laboratory metadata verification or peer review.

Validation: all five relative report links resolve; all 15 endpoint-shortlist embedding paths exist; all 12 observed V9 embedding files were found. No model execution or full artifact hash replay was performed. Markdown checks passed and session diagnostics found no blocking errors; the existing research index retains an ambiguous-link warning and a scientific-abbreviation spelling flag. The parent's disposable downloaded comparison image was removed. The new durable deliverable is this note and its index entry; no analysis output directory, dependency, service or training job was created. Pre-existing uncommitted work was preserved; nothing was staged or committed.
