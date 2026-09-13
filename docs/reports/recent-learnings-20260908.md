# What we have learned: CEBRA, path prediction, and what to do next

> **Consolidation note (2026-09-08):** the worktree/dirty-state descriptions below record the synthesis snapshot. The cited source scripts and reports are now collated in this release; large artifacts remain local. Its E1/E2 real-trial/history proposals are complementary to the [current condition-level pseudopopulation plan](path-generalization-next-steps-20260908.md), not a mandatory individual-cell-significance or simultaneous195 gate. Follow the [two-lane handoff](README.md) and freeze the chosen next protocol before fitting.

**Evidence snapshot: 8 September 2026. Audience: Hongyi and human research collaborators.**  
**Status: literature-informed synthesis of exploratory development analyses; not confirmatory evidence.** No new biological models were fitted for this synthesis. The companion [agent brief](recent-learnings-20260908-agent.md) supplies artifact locations, inference rules, and execution gates.

## 1. The short answer

> We can decode start–goal conditions in a constructed pseudopopulation. CEBRA's initial poor performance was not an intrinsic inability to learn: readout regularization, better positive sampling, training duration, and synthetic-source coverage matter. Some endpoint settings became competitive with PCA. However, neither the earlier path-component benchmark nor the newer source-preserving analysis established reliable cue-period path information beyond endpoints. The data/design has demonstrable limitations, but we have not established that these limitations—rather than weak/absent accessible signal, measurement choices, or confounds—caused the nonpositive results.

**The next priority is a better-identified real-trial question, not another large architecture search.** Audit task/history and behavioral support, establish what effect this design could detect, then run one bounded preprocessing/temporal analysis with honest stop rules.

### Updating your current understanding

| Your interpretation | What the evidence supports now |
| --- | --- |
| “We are not just training CEBRA and losing to PCA.” | **Correct.** The endpoint investigations diagnosed sampler and generalization problems. But PCA remains the simplest strong endpoint reference; no independently validated CEBRA advantage has been established. |
| “Regularization is working very well, possibly by decreasing complexity.” | **Partly supported, mechanism unproven.** Stronger logistic-readout L2 helped frozen CEBRA features. The larger gains also involved positive sampling, temperature, duration, or source coverage. Those are not one isolated complexity intervention. Strong weight decay in a separate cross-entropy recipe actually collapsed it to chance. |
| “H1 is not looking good because the data is not representative enough, not because H1 is false.” | **H1 remains unconfirmed, and the tested analyses are non-supportive.** Sparse conditional support, selected cells, missing verified simultaneity, and exposed development data limit inference. They do not prove why the analyses failed. Neither “H1 is false” nor “H1 would work with better data” follows. |
| “Previous start/goal and other confounders may matter.” | **A serious, specific hypothesis.** Previous goal equals current start under the reported task rule. Other history, cue appearance, gaze, heading, and drift may matter. Their actual contributions have not been established. |
| “We should investigate preprocessing.” | **Yes, narrowly.** Improve alignment, exposure handling, and temporal summaries before learned denoising. Preprocessing cannot create missing independent trials, dissociate identical task variables, or reconstruct unrecorded simultaneous population states. |

## 2. Zoom out: what is the actual scientific question?

**H1a:** does cue-period neural activity improve held-out prediction of the *subsequently observed path*, beyond start and goal?

**H1b:** does that incremental path information have reproducible low-dimensional organization?

```text
Endpoint baseline:    future path/component ~ full start–goal condition
H1a comparison:       future path/component ~ full start–goal condition + cue activity
Stronger control:    compare both again with prespecified history/sensory/time controls
```

“Full start–goal condition” matters: a categorical pair baseline can express interactions that an additive start-plus-goal model misses. Otherwise neural features can appear useful merely by compensating for an underfit baseline.

Predicting *which goal was cued* is not predicting *which route was taken to that goal*. In ML terms, recognizing a prompt's topic is not predicting its particular continuation after controlling that topic. Here we observe only selected spike trains, not the complete hidden state.

CEBRA is a representation-learning instrument; PCA is a comparator. Neither is the hypothesis. A supervised embedding is deliberately shaped by its labels and needs an independent downstream evaluation. H2—the artificial navigation-agent comparison—remains a stretch aim, not a way to rescue unsupported H1. Similar geometry would not establish a shared mechanism.

**Measured:** spike timestamps, event markers, behavioral samples. **Derived:** cue counts/rates, provisional endpoints, graph components, embeddings. **Statistical claim:** held-out association or predictive improvement. **Not directly measured:** intention, planning mechanism, or an internal neural graph. See [canonical research questions](../research-questions.md) and [analysis contract](../analysis-contract.md).

## 3. What work was actually completed?

Three accessible neuroscience worktrees were inspected, including the main checkout and both home-directory sibling worktrees. They shared base HEAD `a9d8dac`; the sibling experiments and reports contained uncommitted work. A registered Mac worktree was stale and unavailable here, not silently counted as reviewed. No matching Python process for the named experiment drivers was observed during this audit; final receipts also mark the September 7 fitting complete.

| Development | Question | What changed / outcome |
| --- | --- | --- |
| Earlier export and V5 | Can we reconstruct appropriate cue/path inputs? | Navigation-only exports were insufficient; native cue events became available. Fine path signatures and a globally stitched panel were poorly supported. |
| V6–V9, main checkout, September 6 | Can cue activity distinguish a future directed component within one endpoint pair? | Static behavioral graph, explicit source support, ten cue bins, raw/PCA/CEBRA and nulls. Whole-cue results nonpositive/unstable. |
| Endpoint baseline and autoresearch, September 7 | Why did CEBRA underperform on the easier 30-class start–goal task? | 126 initial CEBRA fits, then 112 new neural fits: 79 CEBRA and 33 cross-entropy (CE). Sampler/checkpoint/readout/source investigations found specific improvements, not a universal cure. |
| Path-generalization Tracks A/B/C, September 7 | Is the path result due to synthetic sampling, optimization, or source support? Can real-trial analyses do better? | Exact finite-product evaluation; 342 CEBRA fits, including 280 null fits; broader per-unit real-trial comparisons; 50-checkpoint assembly replay. No convincing incremental path evidence. |

These are different evaluation objects, not successive entries in one accuracy leaderboard. Hundreds of fits and thousands of metric rows do not constitute hundreds of biological replications. Detailed provenance is indexed in §10.

## 4. Endpoint decoding: real engineering progress, limited biological claim

### 4.1 What was decoded, and from how much data?

The endpoint study predicted **30 ordered start–goal conditions**, with joint chance accuracy **3.33%**. It used the existing 195 selected units across 58 sessions, restricted to original-training sources, then created an inner development split:

- 15,553 eligible real source trials: **12,288 inner training / 3,265 inner validation**;
- per seed, 480 synthetic training and 240 synthetic validation rows;
- ten 100 ms cue bins, no post-cue neural inputs;
- one same-condition source trial from each session supplies that session's whole cell-by-time block;
- three seeds quantify assembly/optimization sensitivity, **not confidence intervals or new biological samples**.

**Crucial restriction:** assembling even an evaluation row uses its *true* start–goal condition. The classifier does not receive the label as a feature, but the complete synthetic vector could not be constructed for an unknown-label real trial. This is condition-distribution separability, not a deployable 195-cell decoder. CEBRA-Time is also exposed to label-conditioned assembly, despite not using endpoint labels in its contrastive objective. [E2]

### 4.2 The initial result and the useful corrections

All endpoint numbers below are three-seed mean joint development accuracy; balanced evaluation classes make it equal to balanced accuracy.

| Matched endpoint comparison | Result | Interpretation |
| --- | --- | --- |
| Original raw totals / raw ten-bin / PCA8 per bin | **54.86 / 71.39 / 82.50%** | Temporal features and a simple linear compression were useful in this benchmark. |
| Original CEBRA-Time / Behavior | **42.78 / 18.61%** | This initial configuration generalized poorly relative to PCA. |
| Frozen features, logistic `C=1 → .01`, same coordinate scaling | Time **42.78 → 51.67%**; Behavior **18.61 → 25.56%**; PCA **82.50 → 83.61%** | Stronger **downstream readout** L2 helps, but does not close the original gap. |
| At temperature .3 and 250 updates: original Behavior positives versus same-pair/**same-bin** positives, global negatives | **53.06 → 83.33%** | A large improvement from defining positive examples appropriately for cue phase. Competitive descriptively with the 83.61% common PCA reference. |
| Extend that same-bin-positive setting to 3,000 updates | **83.33 → 64.86%** | More training is not automatically better generalization. |
| At 3,000 updates: grouped-bin references/global negatives versus also same-bin negatives | **68.47 → 59.58%** | Time-matching negatives was not automatically beneficial. |
| Time-matched setting, synthetic training rows/class 16 → 64 | CEBRA **59.58 → 81.53%**; PCA **83.61 → 84.86%** | Better sampling/coverage of the same real pool can help; it is not new biological data. |
| Separate-goal LDA | Peak **81.25%**, 0.4–0.5 s | A six-class descriptive temporal result, **not** 30-class joint accuracy or a matched replication of the previous student. |

The synthetic-row comparison is **not a pure optimization experiment**: mean distinct sources used rose from about **10,889 to 12,279**, within the same 12,288-source training pool. Requested quarter/half/full real-source budgets also changed results: PCA **58.75/73.75/83.61%**, CEBRA **24.44/43.06/59.58%**. Minimum support floors make actual quarter/half pools 3,777/6,551, not literal fractions. [E2–E3]

### 4.3 What “regularization” means here

There are several distinct mechanisms:

1. **Readout regularization:** smaller logistic `C` penalizes large decoder weights more strongly. This was directly tested on frozen representations.
2. **Training duration:** early checkpoints sometimes generalize better. This is consistent with overfitting of the encoder/readout pipeline; it is not a clean measurement of reduced representational complexity.
3. **Positive sampling:** matching cue phase changes what the objective tells the encoder to preserve. It can fix a poor learning target without making the network smaller.
4. **Temperature:** changes contrastive weighting/optimization; lower temperature is not synonymous with stronger L2 or fewer effective degrees of freedom.
5. **Synthetic coverage:** additional combinations change which existing sources the learner sees, not the recording sample size.

A CE control replaced InfoNCE with a classification objective. Its binwise common-readout score was **20.00% at 3,000 updates**, early sampled maximum **28.75%**, and **49.03%** with 64 rows/class. Stronger CE weight decay **0.1 produced 3.33% chance**. That is evidence against this particular “regularize more” recipe, not against all CE, all encoder regularization, or CEBRA itself. [E3]

**Accepted conclusion:** objective design and generalization matter. **Not established:** reduced complexity is the single cause, CEBRA has beaten PCA on independent confirmation, or biological path coding has been recovered. Lower embedding rank, falling InfoNCE loss, and smaller weight norms are not interchangeable with better held-out information. The initial PCA8/bin and CEBRA8/bin readouts each concatenate ten bins into **80 features**, not one eight-dimensional whole-trial state.

### 4.4 Other useful findings and failed shortcuts

- More width, latent dimensions, training updates, or whole-cue inputs did **not** provide a general cure in the bounded endpoint screen. Replacing InfoNCE with the tested CE recipe did not either. This is evidence about those tested configurations, not all neural networks.
- Saved CEBRA spectra were concentrated in roughly three Behavior/four Time directions. That is not proof of total collapse: low-variance directions can retain information. Removing per-bin magnitude in a PCA control hurt only modestly, so that control did not explain the large initial CEBRA gap.
- Cosine k-nearest-neighbor readout improved initial CEBRA top-1 accuracy but had poor probability log loss. Changing the metric can change which method looks best; accuracy alone is not enough.
- The previous student's 233-cell/314-pseudotrial analysis is not this 195-cell study. The endpoint worktree's code review found a concrete pooled-time-bin leakage path in one historical notebook analysis, but did **not** establish that every historical per-bin result used it. No numerical-superiority or faithful-replication claim is justified. [E2–E3]

## 5. Path information: the nonpositive evidence must not disappear

### 5.1 V6–V9: the primary path contrast was severely source-limited

The main archive contains **195 selected units / 58 sessions / 23,901 imported source trials**, with only **1–8 selected units per session** (median 3). That is not a simultaneous 195-neuron population, nor 23,901 examples for every path comparison.

The primary contrast fixed provisional endpoints **4→3** and asked whether component `D_N_R_T__N_R_M` occurred among the **interior corridor traversals**. Common-panel requirements left **29 units / 7 sessions / 104 real sources**, only **82 training / 22 validation**. Hundreds of synthetic draws reuse these sources.

| Whole-cue V7–V9 representation | Mean validation balanced accuracy |
| --- | ---: |
| Constant baseline | 0.500 |
| Raw total / raw ten-bin | 0.453 / 0.474 |
| PCA3 / PCA8 | 0.521 / 0.453 |
| CEBRA-Time8 / Behavior8 | 0.443 / 0.414 |

PCA3's three-seed range was **0.258–0.789**: its small positive mean is not stable evidence. A seemingly perfect **0.2–0.3 s** bin did not survive the max-over-ten-bin diagnostic null (**p≈0.218**). We must not choose that window now and describe it as independently supported. [E1]

### 5.2 Tracks A/B: the problem extends beyond one sampled array

The new path investigation enumerated the entire empirical validation product: **24 absent + 6 present session-block combinations**, with **half the total weight assigned to each class**. This removes randomness from drawing validation pseudorows. It does not create an independent validation population or eliminate uncertainty in the source pools.

- Finite-sample ridge settled near exact-product balanced accuracy **0.479** rather than improving indefinitely with synthetic rows.
- The primary CEBRA crossed-seed grid had training BA **1.0**. On other assemblies built from the **same training sources**, means remained **0.9925 Time / 0.9977 Behavior**.
- On **source-disjoint exact validation**, primary grid means were only **0.2492 Time / 0.3517 Behavior**.
- A fixed 14-configuration family reached best observed BA **7/12≈0.5833**, but its selection-aware null was **19/21≈0.9048**. A floating-point tie correction supersedes the older stored 0.8571; models and predictions did not change.

**What this localizes:** the dominant failure is not merely memorizing the exact randomly assembled training rows. Transfer fails across the empirical source pools. **What it does not identify:** whether the cause is biological drift, history imbalance, measurement error, weak signal, or ordinary finite-sample noise. Below-chance scores do not justify flipping labels after looking at validation. [E4–E5]

The 30-row, 290-feature exact validation matrix has rank **9 by construction**. This is a property of combining a few source blocks, **not a nine-dimensional hippocampal manifold**. Known-truth Gaussian simulations showed that tiny finite source pools can produce extreme empirical synthetic validation scores even when true discrimination is chance. Those simulations establish a possible failure mode, not that the actual brain data were generated by the simulation.

### 5.3 Track C: preserving real trials helped the design, not the result

An important advance was **already executed**, not just proposed: per-unit models kept real trial–neural links and dropped the global common-panel requirement. They compared a full endpoint-pair + trial-index + cue-duration baseline against the same model with one cue-rate feature, `log1p(count/exposure)`. Training-only within-endpoint centering and scaling were used. Unit improvements were averaged within session, then sessions equally.

| Target | Eligible units / sessions | Mean held-out Δ log loss, baseline minus neural |
| --- | ---: | ---: |
| Original edge, interior occurrence | 15 / 5 | **−0.010681** |
| Original edge, anywhere in path | 12 / 4 | **+0.001878** |
| Better-supported interior edge `D_N_C_M__N_C_B` | 43 / 11 | **+0.003860** |

Positive Δ means lower prediction loss after adding cue rate. The better-supported target had **267 training / 52 validation source trials**, not 43×319 independent trials. Its tiny gain did not establish a reliable family-level effect: **p≈0.475** under the ordinary conditional null and **p≈0.436** under a coarse temporal-half sensitivity. The nulls remain assumption-dependent, not complete serial-confound control. [E6]

This genuinely weakens the proposal that *simply removing pseudopopulation assembly* will uncover a strong whole-cue single-unit rate effect. It does **not** test every time-resolved, nonlinear, or simultaneous-population code. We should neither erase this negative result nor overgeneralize it to all of H1.

### 5.4 The path-label correction is substantive

Old “absent” meant **absent from all interior corridor runs after dropping the first and last runs**—not absent from the whole path, and not merely absent from one central slot. **51 of 185** old-absent 4→3 development paths traversed the edge outside the interior. A two-corridor path has no interior runs at all.

Track C explicitly separated interior versus anywhere occurrence and a training-support-selected alternative edge. This is why better path measurement is worth investigating. It does not prove a recording bug, truncation, or the cause of the neural results. [E4, E6]

## 6. What exactly is “insufficient data” here?

| Limitation | What is demonstrated | What would address it |
| --- | --- | --- |
| **Sparse conditional support** | Many archive trials become few repeats within session × endpoint × path contrast; tiny real-source validation pools. | More *relevant independent repeats*, or a scientifically justified target with existing within-condition support. |
| **Missing verified simultaneity** | Cross-session vectors do not measure one real population state; same-session identity is still unverified recording-group metadata. | Verify recorded groups and use actual within-trial populations. Neither denoising nor multi-session alignment restores missing simultaneity. |
| **Selection / representativeness** | The cohort is place-selected, not a complete unbiased hippocampal population. Success-after-success also restricts trials. | State the selected-population/success-conditioned estimand. Broader inclusion or new recording requires a separate authorized design. Selection's effect on scores has not been measured. |
| **Identifiability** | Some explanatory variables are identical by design; some path features may be almost determined by endpoints. | Contrasts in which variables differ independently. More repeats of identical confounded conditions do not solve this. |
| **Measurement / nuisance uncertainty** | Provisional marker semantics, clock/QC questions, no derived gaze/raycast in active snapshot, incomplete history controls. | Task/recording metadata, source-preserving QC, verified covariates and explicit target semantics. |
| **Validation limitations** | Original holdout exposure and extensive development reuse; trials remain serially dependent. | Source/block-aware development evaluation and genuinely unexposed confirmation data. Resplitting inspected data does not erase exposure. |

“Insufficient” is therefore not a universal neuron/trial minimum. **The dataset is sufficient for some exploratory questions, but not for the strongest proposed claim.** No power analysis yet establishes which biologically meaningful effect this exact design could rule out. A large p-value is not the probability that H1 is false, nor evidence of equivalence to zero.

A strict 75/25 chronological split supporting *all 30 endpoint classes in every session* was feasible for only **1/58 sessions** in the endpoint audit. That is a failure of that demanding design, not proof that every session-local/block-held-out target is impossible. [E3]

## 7. Your history/confound suspicion: plausible, but make it testable

### 7.1 Previous goal and current start cannot be disentangled in the existing rule

The historical task description states:

```text
previous goal = current start
cue/poster identity is tied to the instructed goal (exact mapping still needs verification)
```

The importer provisionally infers current start from the preceding successful goal. A neuron tracking the previous rewarded location and a neuron tracking current start could therefore produce the same statistical pattern. Two identical columns in a regression do not separate those explanations. Regularization may assign coefficients, but it cannot identify their biological meaning.

Within one fixed current start–goal pair, **previous goal itself is also fixed**. It cannot explain within-pair route differences merely by varying its identity. More discriminating candidates are **previous start, previous path, previous duration/reward timing, elapsed inter-trial time, cue-period view/heading, or session drift**, where these actually vary and are available. This is more precise than treating “previous goal” as an extra independent covariate. [E7]

### 7.2 What can and cannot be learned from controls

A useful nested comparison is:

```text
M0: component ~ full endpoint pair + prespecified time/exposure terms
M1: component ~ M0 + available pre-cue history + cue-period sensory/state variables
M2: component ~ M1 + cue neural features
```

Compare all three on the **same real trials and held-out metric**. If M1 improves and M2 does not, measured history/state is a better supported explanation of prediction than additional neural information under this model. If M2 improves, it establishes incremental prediction over the included controls—not absence of every unmeasured confound or causal planning.

The original H1a comparison conditions on endpoints; adding history/view defines a **stricter estimand**, not just a cosmetically cleaner version of the same number. Some “nuisances” may also mediate planning. Removing them can remove valid path-related signal. Report both endpoint-only and stronger-control comparisons, and justify variables rather than residualizing everything.

Do not use later navigation speed, action, or duration as if available to a cue-time predictor. Those can describe the target or be separately labelled explanatory sensitivities; they cannot silently enter the deployable baseline.

### 7.3 What the literature contributes

- **CEBRA:** Schneider et al. (2023) explicitly make positive/negative sampling and auxiliary variables part of what shapes the embedding. This supports investigating sampler semantics and held-out decoding, not assuming a visually clean supervised latent proves a neural representation. [L1]
- **History versus future:** Ferbinteanu & Shapiro (2003) found current, retrospective, and prospective coding in rat hippocampal ensembles; journey origin influenced firing even on detours. History is a biologically motivated competitor, not merely a statistical nuisance invented after failure. The evidence is from a different species/task, not confirmation here. [L2]
- **Separating explanations by design:** Catanese et al. (2014) studied all four provenance/destination combinations on a common T-maze path and found distinct retrospective/prospective distributions. The transferable lesson is to independently vary history and destination; their timing/spatial pattern is not a template guaranteed to hold during this monkey cue. [L3]
- **Cue versus destination:** Ainge et al. (2012) manipulated visual-stimulus presentation and reported prospective place firing not directly controlled by that discriminative stimulus. This motivates a cue/goal dissociation experiment; it does not show our current cue responses are stimulus-independent. [L4]
- **Preprocessing and valid inference:** Truccolo et al. (2005) provide a covariate-based point-process/GLM framework for spikes, including goodness-of-fit checks. Kriegeskorte et al. (2009) demonstrate how selection and testing on non-independent data create spurious effects. Together they motivate small count-aware models and training-only selection—not a particular denoiser, bin width, or guaranteed null for this dataset. [L5–L6]

The research-informed recommendation is therefore **improve the identifying contrasts and measurement before escalating the model**, not assume that hippocampal decoding is either impossible or automatically rescued by denoising.

## 8. Next investigations, in priority order

**All items below are proposals, not newly executed experiments or authorization to fetch excluded data.** Before fitting, write the estimand, independent unit, exclusions, baseline, null, split, primary metric, and strongest allowed claim. Keep current inspected data exploratory.

### E0 — Resolve metadata and conditional support before more fitting

**Question:** can any existing real-trial contrast distinguish future path variation from endpoints/history with defensible measurements?

- Ask the lab to verify cue/goal marker meanings, visual cue mapping, previous-goal/current-start rule, recording groups/overlap, unit provenance, and behavioral capture completeness.
- Reuse accepted development support tables first; add only authorized, split-guarded metadata. Tabulate session/group × endpoint × component × temporal block, with real source counts and available history/gaze/heading fields.
- Audit original interior and anywhere targets against behavior, especially two-run paths. Define which distinction is scientifically intended before examining neural scores.
- Quantify conditional variation and nuisance collinearity. A target determined by endpoint/history cannot identify the incremental effect in that stratum.

**Why:** establishes whether the comparison exists, rather than whether a sufficiently flexible model can be fitted.

**Decision:** proceed only for contrasts with real variation, an estimable baseline, and enough independent support for the prespecified sensitivity target below. Otherwise deliver a concrete metadata/new-data request—not a silently relaxed inclusion rule. Missing simultaneity blocks a population H1 claim, not all per-unit work.

### E1 — Test the history/state explanation on real trials

**Hypothesis:** route prediction reflects measured carryover/context, with little additional cue-rate information.

Use Track C as the existing baseline; do **not** present its whole-cue real-trial analysis as work not yet done. Extend only with verified pre-cue/current-cue variables, prioritizing previous start/path and trial-time effects. Compare M0/M1/M2 above on identical eligible trials; use held-out log-loss improvement, session-level summaries, and conditional nulls justified by the actual task sequence.

Split contiguous source-trial blocks before learned preprocessing. When features reach back to trial t−1, embargo adjacent boundary trials so the same predecessor record does not bridge folds. A session-held-out analysis requires a model that handles different units; do not call ordinary within-session validation cross-session generalization. Coarse temporal stratification or circular shifts are sensitivities, not guaranteed exchangeability under an unverified schedule.

**Decision:** if history adds prediction but neural features do not, prioritize task/history interpretation over CEBRA. If neural improvement persists, carry it into an independent confirmation design. If covariate support collapses, report non-identifiability rather than extrapolating a fitted nuisance correction.

### E2 — One small, source-preserving preprocessing/time experiment

**Hypothesis:** a single full-cue rate conceals reproducible temporal information, or measurement/exposure differences obscure it.

After E0, compare **full-cue rate** with **one prespecified coarse temporal representation**, for example five 200 ms cue bins, on the same trials. Treat 200 ms as a proposed engineering choice, not a discovered optimum. Use raw counts/rates and one simple regularized decoder; add train-only PCA only for a verified multivariate group. Retain the existing ten-bin analysis as historical context, not an untouched comparator selected after seeing results.

- Verify neural-clock alignment, half-open windows, count conservation, actual exposure and QC. Never mix future navigation spikes into cue bins.
- Choose raw rates versus a count-stabilizing transform inside training only; Track C already used `log1p(count/exposure)`, so this is not an entirely new idea.
- If performing **encoding** instead of decoding, use raw counts with a duration offset in a Poisson GLM and check dispersion; transformed/z-scored responses are not Poisson counts. Negative-binomial or other extensions require a demonstrated fit problem.
- If smoothing, keep every kernel inside the observed cue/trial; no future-neural leakage across cue offset. Do not warp cue activity using the eventual navigation path.
- Include a synthetic known-signal/null control at the observed source budgets. Simulations test assay sensitivity under stated assumptions, not biological truth.

**Decision:** accept only a stable held-out gain beyond the same endpoint/history baseline, with selection-aware nulls. If only a selected bin/seed works, stop. Do not escalate to LFADS, a transformer, an SAE, or broad denoising searches merely because this bounded comparison is nonpositive.

### E3 — Quantify what the design could detect; then decide whether to collect data

**Question:** is the assay capable of detecting a meaningful incremental effect?

Before another search, agree with the supervisor on a **smallest effect worth pursuing**, expressed in the chosen held-out metric—not a post-hoc threshold picked from the observed gain. Simulate signal/no-signal scenarios preserving session/source counts, imbalance, count sparsity, missingness and plausible drift; vary relevant real repeats and verified simultaneous units separately. Derive required support for that effect and uncertainty.

Use source/block/session-aware uncertainty, not bootstrapped pseudorows or independent-cell assumptions. With few sessions, state uncertainty-method assumptions and show session-specific results; sessions do not automatically provide independent animals.

**Decision:** if sensitivity is adequate and a prespecified upper uncertainty bound excludes the worthwhile effect, record evidence against that *operational effect in this cohort*. If not, label the result inconclusive/under-sensitive and request the specific missing design element. A broad H1 cannot be ruled out by this one assay.

A future data/task request should prioritize repeated different paths for the same endpoints, verified simultaneous groups, separated history/current-start or cue/goal factors where feasible, and recorded gaze/heading/history—not just “more neurons.” Keep the current 195 selected-cell scope unless Hongyi explicitly approves expansion.

### E4 — A bounded CEBRA mechanism study, only if it serves an explicit goal

If the aim is specifically **why the endpoint encoder generalizes**, freeze the task, sources, arrays, sampler, temperature, representation size and readout. Test one factor at a time: readout L2 on saved embeddings first; then a small encoder-regularization or duration comparison if still warranted. Select inside training/development folds, retain all arms, and compare accuracy **and log loss** to matched PCA/raw references. Weight decay and temperature are not interchangeable regularizers.

**Decision:** no reproducible source-disjoint gain → close this method question for the present cohort. Competitive endpoint accuracy alone → a useful method result, still not H1. For H1, CEBRA becomes a secondary instrument after a supported real-trial assay, not a requirement that must beat PCA to make the biology meaningful.

### E5 — Confirmation and H1b, only after the gates pass

Freeze one target, one preprocessing rule, one primary contrast and metric, exclusions, effect threshold, null family and analysis script. Evaluate once on **genuinely unexposed observations**. Preserve the historical holdout-exposure record; do not relabel a new random split as pristine.

If incremental path information is supported, test H1b with target-free raw/PCA geometry and stability across dimensions/recording groups before interpreting behavior-conditioned embeddings. Control endpoints and available nuisances; resample source trials/groups rather than treating pairwise distances as independent. If geometry exists without incremental H1a support, describe it as exploratory condition structure, not established H1b path organization.

## 9. The practical recommendation

**Do E0, then specify E1/E2 together with E3's sensitivity/stop rule. Defer E4 unless the endpoint-method question itself is worth answering.** The existing code and linear baselines cover the next useful stage; no new model family is needed yet.

A concise supervisor update would be:

> We recovered strong endpoint-condition separability and identified CEBRA sampling/generalization issues. Those successes do not establish path information beyond endpoints. Both the narrow synthetic path benchmark and the broader real-trial whole-cue analysis remain non-supportive. We propose to verify task/history and route semantics, quantify within-condition support and detectable effect size, then test one source-preserving temporal/neural increment over endpoint-plus-history baselines. If that design cannot identify or detect a meaningful effect, the deliverable is a targeted data/task redesign, not another open-ended model sweep.

## 10. Evidence and reading map

The conclusions and key numbers are included above so this file can be read alone. Sibling-worktree and `outputs/` links require the data-equipped homelab; they are not portable GitHub artifacts. The [agent brief](recent-learnings-20260908-agent.md) records exact artifact roots and which summaries supersede older ones.

### Local evidence

- **[E1]** [V6–V9 teaching/audit report](place195-v6-v9-autoresearch-20260906.md); [follow-up audit and data boundary](place195-audit-and-next-steps-20260907.md); [archive versus effective data volume](cebra-data-volume-comparison-20260907.md).
- **[E2]** Endpoint worktree: [baseline](start-goal-cebra-baseline.md) and [diagnosis/readout ablations](start-goal-cebra-diagnosis.md). Accepted baseline `outputs/start-goal-cebra-20260907/summary.json`; diagnostic results under `outputs/start-goal-diagnosis-20260907/`.
- **[E3]** Endpoint worktree: [completed autoresearch report](start-goal-autoresearch.md), [journal](start-goal-autoresearch-journal.md); `outputs/start-goal-autoresearch-20260907/all_metrics.csv` and stage metrics, including `06-ce-followup/metrics.json`.
- **[E4]** Path worktree: [completed state](path-generalization-completed-state-20260907.md), [frozen protocol](path-generalization-prefit-20260907.md), [self-contained final teaching HTML](../professor_updates/path_generalization_20260907/path-generalization-teaching-audit-20260907.html). Final run `outputs/path-generalization-20260907/results-20260907T081200Z/`; accepted Track A is `track_a_v2/`.
- **[E5]** Same path run: `track_b/summary_exact_audited.json`, `audits/track_b_exact_audit.json`, `assembly_transfer/assembly_transfer_metrics.csv`. Correct Track B family p is **19/21**. The raw producer summary's older value is not the authority.
- **[E6]** Same path run: `track_c/summary.json`, unit metrics/predictions and joint-label null tables. `observed_global_statistics` and `pvalues.*.family_max_three_targets` supply the reported gains/nulls.
- **[E7]** [Historical task/student summary](../../context/previous-student-analysis.md), [marker-semantics probe](../../notes/data_inspection/place195_marker_semantics_probe_20260901.md), [selected-data transfer audit](../../context/2026-09-06-place-data-transfer-audit.md). The removed eight-unit supplement is **not** an active 203-cell cohort.

### Primary literature

- **[L1] Schneider, Lee & Mathis (2023), “Learnable latent embeddings for joint behavioural and neural analysis,” Nature.** [DOI: 10.1038/s41586-023-06031-6](https://doi.org/10.1038/s41586-023-06031-6). Primary text checked, particularly auxiliary-variable and positive/negative sampling definitions. It supplies a method, not a guarantee for this cohort or evidence that preprocessing fixes our results.
- **[L2] Ferbinteanu & Shapiro (2003), “Prospective and retrospective memory coding in the hippocampus,” Neuron.** [DOI: 10.1016/S0896-6273(03)00752-9](https://doi.org/10.1016/S0896-6273(03)00752-9); [verified PubMed abstract](https://pubmed.ncbi.nlm.nih.gov/14687555/). Abstract-level scope here; no claim of a new full-methods replication review.
- **[L3] Catanese et al. (2014), “Retrospectively and Prospectively Modulated Hippocampal Place Responses Are Differentially Distributed along a Common Path in a Continuous T-Maze,” Journal of Neuroscience.** [DOI: 10.1523/JNEUROSCI.0819-14.2014](https://doi.org/10.1523/JNEUROSCI.0819-14.2014); [PubMed abstract/figure descriptions](https://pubmed.ncbi.nlm.nih.gov/25253861/). Supports the value of separated provenance/destination contrasts, not direct extrapolation to cue-period monkey recordings.

- **[L4] Ainge et al. (2012), “Hippocampal place cells encode intended destination, and not a discriminative stimulus, in a conditional T-maze task,” Hippocampus.** [DOI: 10.1002/hipo.20919](https://doi.org/10.1002/hipo.20919); [verified abstract](https://pubmed.ncbi.nlm.nih.gov/21365712/). Publication year 2012, first online 2011. Abstract-level evidence for stimulus-presentation manipulation and its bounded interpretation, not a claim to have audited the complete experiment.
- **[L5] Truccolo et al. (2005), “A point process framework for relating neural spiking activity to spiking history, neural ensemble, and extrinsic covariate effects,” Journal of Neurophysiology.** [DOI: 10.1152/jn.00697.2004](https://doi.org/10.1152/jn.00697.2004); [PubMed](https://pubmed.ncbi.nlm.nih.gov/15356183/). Abstract checked through indexed primary records after direct-page retrieval failed. Supports covariate-aware spike modeling and diagnostics; does not validate Poisson dispersion or a preprocessing choice in our data.
- **[L6] Kriegeskorte et al. (2009), “Circular analysis in systems neuroscience: the dangers of double dipping,” Nature Neuroscience.** [DOI: 10.1038/nn.2303](https://doi.org/10.1038/nn.2303); [verified indexed abstract](https://pubmed.ncbi.nlm.nih.gov/19396166/). Supports independence between selection and inference under the null. Our source/block splitting rules are a project-specific application, not a split prescription demonstrated by that paper.

### Review and remaining uncertainty

This synthesis combines worktree-specific evidence audits, literature research, an independent scientific skeptic, and final artifact/claim and clarity reviews. These are **AI-assisted research checks, not external human peer review or laboratory metadata verification**. The parent resolves disagreements against accepted artifacts rather than voting among agents. Review receipts and a 19-file source-hash/worktree snapshot are retained locally under `outputs/research-synthesis-20260908/`; the agent brief records corrections and residual risks.
