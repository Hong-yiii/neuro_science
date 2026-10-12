# What CEBRA has—and has not—shown in our hippocampal recordings

**Document 1 · Research synthesis blueprint and evidence audit · 11 October 2026**

**Status:** proposed structure with a substantive, source-linked results spine, not a finished paper or a new experiment. Hongyi requested a rigorous retrospective, including path decoding, before narrowing a separate [future research agenda](../cebra-observability-agenda-20261011.md). The completed studies remain exploratory. This document proposes how to organize their conclusions; it does not retrospectively change their protocols or success criteria.

## 1. Recommendation: one research narrative, not a concatenation of run reports

**Organizing question:** what did the successive data constructions, representations and readouts let us recover, and which limitations remained after the ablations?

The report should have two reading depths: a short overview with the main conclusions and figures, followed by a methods/results deep dive and complete evidence appendices. Organize the main text by scientific question; put the chronological experiment ledger in an appendix. Otherwise repeated descriptions of the same sources will look like independent replications.

**Proposed title:** *CEBRA for hippocampal task representations: endpoint recovery, path-component decoding, and the limits of latent-space inference.*

### Proposed final structure

| Part / chapter | Question it answers | Required content and evidence |
| --- | --- | --- |
| **Overview · 1. Executive synthesis** | What have we learned, and why change direction? | Six conclusions below; separate endpoint success, weak path evidence, and untested state-model claims. One within-study comparison figure; no cross-study leaderboard. |
| **2. Task, recordings and evaluation objects** | What is measured, and what constitutes an observation? | Cue/navigation timeline; provisional start/goal semantics; selected units; three principal cohorts; source versus synthetic counts; exposure ledger; target definitions. |
| **3. From spikes to latent coordinates to predictions** | What does each processing step do? | Source split → session-block assembly → train-only scaling → raw/PCA/CEBRA → window construction → readout. Distinguish learning objectives, encoder architecture, decoder architecture and plotting projection. |
| **Deep dive · 4. Endpoint recovery** | What can be decoded about start, goal and their ordered pair? | September baseline and sampler/readout/coverage ablations; October direct-head cue-only/joint comparison; all-seed accuracy, loss and confusions; source/null controls. |
| **5. Path information beyond endpoints** | What happened to the original biological question? | Behavior-derived graph/components; V6–V9; exact-product/source-transfer/per-unit checks; five-endpoint preprocessing and matched PCA; fixed 4→3 joint-training and cue-bin results. Component prediction is not ordered-route prediction. |
| **6. What the ablations diagnose** | Is failure explained by the decoder, regularization, time window or training coverage? | Controlled contrasts and their scope; kNN/SVM/logistic; confidence versus discrimination; Time/Behavior sampling; checkpoint and data-volume studies. Distinguish isolated interventions from comparisons changing several factors. |
| **7. What the latent geometry shows** | Do the pictures support the performance narrative? | Atlas, projection distortion, full-space geometry, seed/source stability and saved-checkpoint diagnostics. Explain what a plotted point is. No intrinsic-dimensionality/topology claim from a chosen latent size. |
| **8. Synthesis, limitations and closure** | Which explanations were weakened, and which remain unresolved? | Claim-by-evidence table, missing metadata/nuisance controls, finite support and historical exposure. Close the old H1 work as a research stage without declaring H1 false. |
| **9. Future-work bridge** | What question follows from these lessons? | Eventually insert a condensed 1–2-page version of Document 2, after its direction is narrowed. Not a list of every missing model combination. |
| **Appendices A–E** | Can a reader audit the argument? | A: study/cohort ledger; B: exact configurations and crossed-factor coverage; C: all metrics/seed detail/count and normalized confusions; D: full figure catalogue; E: provenance, failed attempts, corrections and replay scope. |

Suggested size, not a requirement: 2–3 pages of overview, roughly 15–25 pages of illustrated deep dive, then appendices. Reuse the existing September28 review/atlas and October figures rather than build another reporting framework. The final length should follow the evidence, not this page estimate.

## 2. The conclusions the document can already carry

1. **The endpoint-condition benchmark contains recoverable information.** Raw/PCA and some CEBRA settings decode the provisional start/goal conditions well in the constructed development pools. This is not an unknown-label natural-trial deployment result.
2. **CEBRA's benefit is configuration- and question-dependent.** Sampling, training duration, representation and readout choices mattered. Joint cue/navigation training helped the October pair head more than the individual endpoint heads. There is no general CEBRA-over-PCA verdict.
3. **The prospective-path programme did not establish robust incremental path information.** Several descriptive leads survived particular checks, but source support, nulls, exposed evaluation and nuisance ambiguity prevented a strong biological conclusion. This is not evidence that path information is absent.
4. **A simple-decoder explanation was investigated, not left entirely untried.** Nonlinear readouts and broad decoder-regularization changes did not rescue the tested frozen path CEBRA family. That conclusion does not transfer automatically to the endpoint cohort or every possible decoder.
5. **A latent picture and a decoder score answer different questions.** Three-dimensional displays omit important structure in some good endpoint representations; attractive path displays coexist with weak source transfer. Neither establishes a uniquely identified biological state.
6. **The next question can be representation reuse and state estimation, not another attempt to win the same benchmark.** The retrospective provides an empirical starting point, not proof that an observable hippocampal model already exists.

## 3. Shared methods spine: what must be explained once, clearly

### Three distinct evaluation objects

| Object | Sources and construction | Target / scope |
| --- | --- | --- |
| **Endpoint cohort** | 195 selected units / 58 sessions; 12,288 inner-training and 3,265 exposed-development sources. Standard October assembly: 480 train / 240 development pseudorows per seed. | 30 ordered pairs, six starts, six goals. Known pair labels select source blocks, including during evaluation. |
| **Fixed 4→3 path-component cohort** | 29 selected units / seven session blocks; 82 train / 22 historical-development sources. Later exact evaluation enumerates 24 absent + six present combinations, balanced by class weight. Earlier V9 sampled rows rather than using this exact-product measure. | Presence of directed `D_N_R_T__N_R_M` among **interior corridor runs**, after excluding first/last runs. Not absence everywhere in the full path; not goal decoding. |
| **Five-endpoint preprocessing / matched-PCA cohort** | 49 unit IDs / 13 sessions; 147 train / 41 historical-development sources, distributed over endpoint-specific panels. Seventeen of 28 development pools are singletons. | A supported directed-component assay across five endpoint panels; first-second rates. Not the fixed 29-unit tensor or the 30-way endpoint task. |

Track C's source-preserving per-unit analyses are a separate evaluation lane, not another simultaneous population or another row in a pooled accuracy table. Use its study-specific cohort/target accounting in the path chapter.

The synthetic construction is approximately a product of empirical session-block distributions conditional on known labels. It preserves a block's cells/bins from the same source, but does not recover unrecorded cross-session covariance. More synthetic rows can improve coverage of existing sources; they are not more biological trials. Same-session membership alone is not verified simultaneity.

### Pipeline diagram — conceptual, not an empirical figure

```text
real source ledger + task/clock/QC metadata
          │ split sources before assembly or learned preprocessing
          ▼
train source blocks                     development source blocks
          │ label-conditioned assembly within each split
          ▼
train-only scaler → raw / pooled-bin PCA / CEBRA encoder
          │ fixed transforms applied to development inputs
          ▼
one cue bin OR ordered concatenation of ten cue bins
          ▼
training-only readout → development predictions → metrics / nulls / sensitivity
```

For the October endpoint assay: raw = standardized 100-ms spike counts, **195 inputs/bin or 1,950/whole cue**. PCA/CEBRA = eight coordinates/bin, **80/whole cue**. “PCA8/bin” uses one pooled training-bin basis, not ten independently fitted bases. Whole-cue concatenation is not time averaging. The path assay instead has 29 raw inputs/bin or 290/whole cue.

CEBRA-Time learns contrastive temporal relationships; CEBRA-Behavior uses specified auxiliary labels to shape sampling. Neither is an end-to-end downstream logistic classifier. “Time” is not a guarantee of a recurrent dynamics model: the reused path `offset1` encoder is pointwise, with temporal structure supplied through positive pairs. Its source assembly remains label-conditioned. A training loss measures its objective, not the downstream task's success.

PCA + logistic is a constrained linear predictor of the original features; CEBRA + logistic is generally nonlinear in those original features. PCA + RBF is nonlinear too. Equal output dimension or equal logistic `C` does not equate objectives, preprocessing, regularization or effective capacity. These studies are bounded pipeline comparisons, not a universal capacity-matched algorithm ranking.

**Two meanings of “joint” must never be merged:** joint **pair classification** means predicting `(start, goal)`; joint **encoder training** means exposing a shared encoder to cue and navigation inputs. A factorized start/goal head is a third, different construction.

## 4. Results spine: facts to develop into the chapters

### 4.1 Endpoint study: use the latest matched direct heads as the main table

October7, whole cue, logistic `C=.01` for raw/PCA/CEBRA; raw SVD-LDA is a supervised reference. Three computational-seed means on the **same endpoint development construction**, not biological confidence intervals. Accuracy equals balanced accuracy here because classes are balanced. Source: [endpoint results and all figures](cebra-endpoint-time-readout-20261006/README.md), [seed-level table](cebra-endpoint-time-readout-20261006/tables/observed_metrics_by_seed.csv).

| Representation/readout | Pair30 BA | Start6 BA | Goal6 BA | Pair30 log loss ↓ |
| --- | ---: | ---: | ---: | ---: |
| Raw + logistic | 70.28% | 78.75% | 90.83% | 2.1701 |
| PCA-8 + logistic | 83.61% | 89.44% | 86.81% | 1.6736 |
| Cue-only CEBRA-Time + logistic | 63.75% | 71.81% | 85.14% | 1.7795 |
| Joint cue/navigation CEBRA-Time + logistic | 75.56% | 72.64% | 83.89% | 1.6373 |
| Raw SVD-LDA | 48.47% | 57.22% | 80.97% | 3.7206 |

Uniform BA references are 1/30 and 1/6; corresponding uniform log losses are `log(30)` and `log(6)`. Joint CEBRA has slightly lower pair loss than PCA while PCA has higher pair BA: even for pair30 there is no metric-independent winner. Across heads, raw/PCA remain strong accuracy references.

The joint-minus-cue BA differences are +11.81, +0.83 and −1.25 percentage points for pair/start/goal. The whole-cue joint-gain no-association family tail is **8/21**, not a demonstrated general superiority effect. Some bin-family tails reach **1/21**, the minimum resolution with 20 null worlds, without repairing exposure or serial/nuisance limitations. Full loss/Brier/F1, train gaps, all bins and confusions belong beside the accuracy table, not hidden behind the best head.

**Historical endpoint ablations explain why one snapshot is insufficient.** [September7 follow-up](start-goal-autoresearch.md) changed same-pair positives to same-pair/**same-bin** positives at matched temperature/update count: pair accuracy 53.06% → 83.33%. That recipe fell to 64.86% at 3,000 updates. More synthetic rows improved one later recipe from 59.58% → 81.53%, while also increasing distinct source coverage; this was not pure optimization or new biological N. The original baseline's start/goal scores were marginals of a predicted pair, whereas October has separately trained direct heads. Its PCA82.50% at `C=1` and later PCA83.61% at `C=.01` are not conflicting measurements.

The September study also includes LDA/shrinkage/factorized-head comparisons, a bounded cross-entropy neural-training alternative, layer probes and source-fraction/checkpoint diagnostics. The cross-entropy network is not a frozen-CEBRA nonlinear-decoder ablation. Retain those distinctions in the configuration appendix.

### 4.2 Path work: close the question honestly, with its positive and negative observations

| Study | Main observation | Conclusion that survives its controls |
| --- | --- | --- |
| [V6–V9](place195-v6-v9-autoresearch-20260906.md) | Built auditable behavior/graph targets and cue tensors; V9 Time-8/Behavior-8 mean BA 44.27%/41.41%. | Measurement/pipeline progress; unstable or nonpositive whole-cue source generalization. Earlier V5 route signatures were a different target, not a matched performance baseline. |
| [Path generalization A/B/C](path-generalization-completed-state-20260907.md) | Time/Behavior transfer across mixtures of **training** sources near 99%; across the other source pool about 24.92%/35.17%. Corrected Track B family tail **19/21**. Per-unit Track C was completed too. | Source-pool failure is real for these pipelines; its unique biological or algorithmic cause is unresolved. Synthetic recombination is not independent-source generalization. |
| [Preprocessing](path-preprocessing-autoresearch-20260908.md) | Twenty observed recipes; selected mean loss improvement over constant about .0286 nats, BA55%; only 2/5 endpoints positive, 6→1 dominant. | Stronger regularization helped loss; no broad robust path finding. |
| [Matched PCA/raw](path-pca-matched/README.md) | Raw/PCA losses .664564/.657541; paired gain .007023 nats; both BA55%. Source sensitivity spans both signs. | Small exploratory loss advantage, not a resolution of H1 or validation of the separate PCA+RBF lead. |
| [Frozen decoders](cebra-decoder-autoresearch-20260924.md) | Strongest tested nonlinear means: Time37.33%, Behavior35.67% BA. PCA+scaled RBF77.50%. | No tested nonlinear CEBRA rescue. PCA lead lacked a matched PCA null in this experiment. |
| [Regularization/kernel diagnosis](cebra-hyperparameter-diagnosis-20260924.md) | Weaker L2 did not rescue CEBRA; wider kernel grid reached at most chance mean CEBRA BA. Temperature changed loss without discrimination. | Decoder undercapacity/over-regularization was not supported as the main explanation within this range. Later anchored nulls did not establish the PCA lead and do not directly test its five-assembly mean. |
| [Cue versus joint training](cebra-full-trial-transfer/README.md) | Time/logistic loss 1.010464 → .710618; BA32.64% → 61.81%. Behavior loss worsened. | Relative Time improvement, but primary criterion failed because loss stayed above `log(2)=.693147`. The primary gain tail1/21 is not absolute path evidence; absolute loss tail12/21. |
| [October5 cue-time readouts](cebra-cue-time-readout-20261005/README.md) | Joint/logistic descriptive peak88.89% at100–200ms; raw/logistic94.44% at200–300ms. Gain-family tail9/21; absolute80-view BA tail17/21. | No validated best window or robust H1 result; eight source deletions were inestimable. No encoder/PCA refits in this study. |

Do not plot these scores as improvement over calendar time. The same nominal 4→3 cohort can still have different assemblies, optimizers, scalers, exact versus sampled evaluation and readouts. October5 whole-cue values replay September25 models; they are **not a new replication**. The later joint-study PCA+RBF value55.56% and earlier decoder-study value77.50% are not interchangeable controls.

**Closure wording:** “These studies did not establish robust cue-period component/path information under the endpoint-fixed and endpoint-panel constructions studied. They identify important methodological constraints and several bounded descriptive effects, but are not one uniform test of the entire H1 claim. They neither refute hippocampal path coding nor justify continued tuning as the default research objective.” Full ordered-route prediction remains untested; we do not need to complete it to close and summarize this research stage.

### 4.3 Geometry: characterize representations without turning displays into discoveries

The [saved atlas](cebra-latent-atlas/atlas.html) contains 39 saved objects with Time/Behavior/raw/PCA references; the [atlas report](cebra-latent-atlas-results-20260924.md) explains point definitions and fidelity metrics. An early strong endpoint Behavior representation retains only 56.3–64.2% of development energy in its training-fitted three-dimensional bin display. Later training spreads it across more dimensions while decoding worsens. V9 path pictures remain structured despite weak decoding.

The [October5 checkpoint figures](cebra-cue-time-readout-20261005/README.md) describe spectra, participation ratio and neighborhood/distance stability at saved250/500/750/1000updates. They do not test checkpoint-selected performance, biological rotation or H1b. There is not yet an equivalent atlas for the **October7 cue-only/joint endpoint models**; older endpoint plots cannot be captioned as those models.

## 5. Is anything unfinished in the basic CEBRA → latent → decode story?

**Yes, some combinations are missing; no, the retrospective is not blocked by completing them.** The archive is a sequence of bounded studies, not one complete factorial experiment.

| Requested axis | Actual coverage | Gap / recommendation |
| --- | --- | --- |
| Start, goal, ordered pair | Direct heads in October7; earlier pair marginals, direct LDA and factorized references documented separately. | Core coverage complete for a retrospective. Do not quietly equate marginal and direct-head scores. |
| Cue-only versus joint training | Path Time/Behavior comparison in September25; Time path bins in October5; Time endpoint bins/whole cue in October7. | Core engineering comparison complete. It is not navigation evaluation or cross-phase transfer. |
| Decoder architectures | Path: logistic, cosine kNN, RBF-SVM and regularization/kernel ablations; October5 logistic/SVM by bin. Endpoints: logistic, LDA variants/factorized reference, separate CE-trained network investigation. | **No matched nonlinear frozen-latent decoder grid for October endpoint cue/joint representations.** Optional bounded gap if claiming architecture robustness; not a reason to run MLP/GRU/Transformer sweeps. |
| Objective/sampler | Historical Time/Behavior and endpoint sampler/temperature contrasts; September25 Time/Behavior × training coverage. | Not fully crossed across modern targets/cohorts. Do not claim October Time results characterize all CEBRA variants. |
| Time windows | October endpoint/path ten bins and concatenated whole cue. | Complete same-window curves. Neither selected optimal windows nor temporal generalization follow from them. |
| Temporal generalization | **September7 direct-goal raw-feature LDA matrix exists**, republished in the September28 review; 300 seed/time-pair entries were verified. | Matched October CEBRA cue/joint versus raw/PCA train-time × test-time matrices are **not done**. Saved models might suffice after compatibility/lineage review; no-fit is not no-analysis. |
| Navigation and phase transfer | Training-source navigation exposed only in joint encoders. | Navigation-time decoding and frozen cue↔navigation readout transfer remain undone; endpoint development-navigation features were not extracted. Separate preparation permission required. |
| Latent pictures | Historical endpoint/path atlas and October path-checkpoint geometry available. | Latest endpoint cue/joint geometry is an optional **new descriptive analysis**, not an existing image or a prerequisite for the summary. |
| Independent confirmation / nuisance isolation | Source-separated development, multiple nulls and sensitivity checks; several metadata/confound gaps persist. | New splits of exposed sources do not fix this. Metadata or genuinely unexposed observations are needed for stronger claims, not more pseudorows. |
| Ordered path / formal observability | Component labels and representation diagnostics only. | Neither completed. Ordered path is retired from the default queue; model/state observability belongs to Document2, not an overdue endpoint ablation. |

### Separate three kinds of remaining work

- **Editorial, no new scientific analysis:** harmonize terminology, extract already-saved aggregate panels, consolidate captions/configurations, link all negative results, and build the final portable narrative. This is the recommended next step for Document1.
- **Optional bounded analyses:** latest endpoint geometry or matched endpoint nonlinear readouts. Necessary only if the final paper makes corresponding new claims. Request a protocol/budget before running anything; even descriptive geometry changes the evidence inventory.
- **New-direction research:** temporal/cross-phase transfer, deployable state estimates, recording robustness and explicit dynamics. Keep these in Document2 rather than indefinitely postponing the retrospective.

## 6. Figure architecture: reuse the evidence we already have

Every final caption must identify target/cohort, independent sources versus synthetic rows, split/exposure, time reference/units, representation/readout, metric/baseline, uncertainty meaning, source artifact and claim limit. Seed dots/ranges are computational variation, not biological confidence intervals. Inestimable support failures remain visible.

| Figure family | Main-text purpose | Existing authority / availability |
| --- | --- | --- |
| Task/data/architecture schematic | Explain measured spikes → constructed features → predictions. Label schematic. | [September28 illustrated review](../professor_updates/research_review_20260928/review.html), [narrative](../professor_updates/research_review_20260928/review.md). |
| Cohort/support panels | Show where the apparent sample size comes from. | October endpoint `figures/source_class_counts.png`, `source_session_support.png`; October path `source_support.png`; five-endpoint report. |
| Endpoint performance | Side-by-side BA **and** loss, cue bins and whole cue; all heads/seeds. | [Endpoint18figures](cebra-endpoint-time-readout-20261006/README.md); all seed tables in its `tables/` directory. |
| Endpoint error structure | Pair/start/goal count and row-normalized confusions. | All nine endpoint `confusions_{target}_seed{0,1,2}.png` panels. Main text may show seed0 clearly labelled; appendix retains all seeds. |
| Path findings/controls | Separate component tasks; full curves and family nulls beside peaks. | [October path16figures](cebra-cue-time-readout-20261005/README.md); [path generalization report](../professor_updates/path_generalization_20260907/path-generalization-teaching-audit-20260907.html); [matched PCA figures](path-pca-matched/report.html). |
| Decoder/regularization diagnosis | Show nonlinear versus linear readout, train/development gap, C/gamma and confidence effects. | [Decoder HTML](cebra-decoder-autoresearch-20260924.html), [diagnosis HTML](cebra-hyperparameter-diagnosis-20260924.html); figures are embedded, not missing. |
| Sampler/coverage/checkpoint contrasts | Explain historical endpoint improvements and reversals. | [Endpoint follow-up HTML](../professor_updates/start_goal_20260907/endpoint-research-report.html), including later teaching addendum; do not relabel its original validation receipt as QA of the addendum. |
| Joint training | Separate encoder exposure from cue-only prediction; paired seed results and nulls. | [Joint-study report](cebra-full-trial-transfer/report.html); October endpoint/path paired-effect figures. |
| Latent geometry | Same saved model in full-space diagnostics and train-fitted display; disclose distorted/missing dimensions. | [Atlas/review](cebra-latent-atlas/review.html) and October path `geometry_evolution.png`, `bin_geometry.png`; no new latest-endpoint geometry yet. |
| Existing temporal generalization | Include the historical raw-LDA goal matrix with correct identity. | [September28 review](../professor_updates/research_review_20260928/review.html), aggregate `evidence.json` key `cue_goal_cross_temporal`. Not CEBRA/joint. |
| Provenance/coverage | Show which factors were actually crossed and which results reuse models. | Tables above plus original protocols/execution ledgers; no new fitted results. |

**Small evidence preview:** these are unchanged existing figures, not newly computed panels. The final report should combine a curated main-text subset with a complete linked appendix rather than duplicate every figure on its opening pages.

![Endpoint real-source class counts](cebra-endpoint-time-readout-20261006/figures/source_class_counts.png)

**Preview A — endpoint support.** Provisional ordered-pair counts among12,288 training/3,265 exposed-development real sources,195 selected units/58sessions. These are real-source counts, not the480/240 synthetic rows per seed; no decoder or uncertainty interval. Original October7 accepted-run provenance is in the linked endpoint report. This describes support, not independent biological replication.

![Endpoint whole-cue balanced accuracy](cebra-endpoint-time-readout-20261006/figures/wholecue_balanced_accuracy.png)

**Preview B — endpoint performance.** October7 pair/start/goal whole-cue0–1s BA on240 label-conditioned development pseudorows/seed;195 units/58sessions and source pool as PreviewA. Raw/PCA/cue/joint CEBRA use logisticC=.01; SVD-LDA is a separate supervised reference. Bars are three-seed means, dots computational seeds; uniform references shown. Train-only transforms, no biological confidence interval or path claim. Original source: endpoint accepted-run figures/tables.

![Path-component cue-bin balanced accuracy](cebra-cue-time-readout-20261005/figures/balanced_accuracy.png)

**Preview C — path cue time.** Fixed4→3 interior component;29 units/7sessions,82train/22exposed-development sources,128training rows and30weighted evaluation combinations. Ten100-ms cue bins versus separately fitted whole cue, logistic/RBF readouts on raw/PCA/cue/joint CEBRA. Thin lines are computational seeds, black their mean, red whole cue; binary BA reference50%. No confidence interval or selected best window; consult the following family controls. Original source: October5 accepted frozen-model study.

![Path cue-time family nulls](cebra-cue-time-readout-20261005/figures/null_families.png)

**Preview D — why the peaks are not the conclusion.** Same path cohort/split as PreviewC. Twenty full-construction source-coherent null worlds; observed versus null family statistics over predefined windows/representations/readouts, with seed means taken before maxima. Minimum tail resolution1/21; primary gain9/21 and absolute BA17/21. These are no-association diagnostics, not superiority tests or correction for the entire project's adaptive history. No uncertainty interval is implied.

## 7. Evidence and reporting contract for the final synthesis

- **Authority:** original accepted study reports, aggregate tables and corrected inference ledgers. Old “draft PR/unmerged/pending” lines are chronology; local `main` at review start was `4862267`, containing PR15. Do not rewrite numerical history to match current Git status.
- **Claims:** distinguish direct measurement, derived quantity, descriptive association, generalization evidence and biological interpretation. Loss, accuracy, AUROC and geometry cannot substitute for one another.
- **Nulls:** always name the family, source-label construction, anchor versus seed-mean statistic and denominator. A no-association permutation tail is not automatically a paired method-superiority test.
- **Uncertainty:** sources are nested/dependent; independent-animal count is unresolved. Synthetic rows/bins/optimizer seeds are not replications. Source-weight/deletion ranges are finite-pool sensitivity, not biological intervals.
- **Provenance:** link executed code snapshots, input hashes, split/exposure, settings, attempts and replay receipt. Numerical replay and AI review are QA, not lab verification of task/recording assumptions or external peer review.
- **Privacy:** keep raw arrays, full predictions, credentials and models local. Reuse only the already-authorized aggregate/report assets in this private repository; no external upload or public preview is implied.

## 8. Decisions to narrow next

1. Approve a **question-led overview + deep dive**, with chronological detail in appendices, rather than a monolithic experiment diary.
2. Use **October7 as the main matched endpoint comparison**, while preserving September sampler/architecture insights and their differing protocols.
3. Close the path programme with its bounded conclusions; do not require ordered-route prediction or a significant path result to “finish” the summary.
4. Default to **writing from existing evidence**. Only commission an endpoint decoder/geometry supplement if its scientific question is worth the extra analysis.
5. Narrow Document2 independently, then fold its agreed question, one proposed hypothesis and gated next steps into Chapter9. Keep the full agenda as a companion.

### Review provenance for this draft

Preparation used a read-only evidence scout and literature researcher, followed by two actual draft research-review rounds and an independent evidence review. Revisions made path closure specific to endpoint-fixed/panel assays and distinguished pair30 accuracy from loss; historical raw-LDA temporal generalization was retained. Final research rereview found no major scientific-design blockers. Detailed dispositions and bounded validation are in Section13 of the companion agenda.

This synthesis uses tracked reports/aggregates only; no raw data or checkpoints were loaded, no model analysis was rerun, and no fits were performed. Representative aggregate means and local links were checked, not every historical result independently revalidated. The full illustrated final manuscript remains a writing task after Hongyi narrows the structure; this is its reviewed blueprint/evidence audit.
