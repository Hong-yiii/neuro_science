# From decodable embeddings to reusable estimates of hippocampal task state

**Document 2 · Proposed research direction and document structure · 11 October 2026**

**Owner steering:** Hongyi requested a new CEBRA-centered latent-representation direction, with observability and downstream reuse as central ambitions. The previous prospective-path goal is no longer the default objective: write its conclusions into [Document1, the retrospective](reports/cebra-research-synthesis-20261011.md), rather than keep tuning toward it. H1 is unresolved, not disproved; artificial-navigation-agent H2 stays removed.

**Decision status:** this change of direction is requested. The operational definition of observability, replacement hypotheses, data lane, model family, primary metric, thresholds and experiment budget below are **proposals**, not approved protocols. This document authorizes no fits, saved-model reanalysis, locked-test access, data download/extraction, installation or service. It supersedes the October9 handoff as the planning entry point while retaining its [source/evaluation safeguards](analysis-contract.md).

## 1. The positive ambition

> **Can we learn a compact, task-relevant hippocampal representation that can be estimated from limited neural observation history and reused to predict independent neural or behavioral outputs across time and recording conditions?**

The proposed contribution is not “CEBRA gets the best endpoint accuracy.” It is a **characterization of when a learned state estimate is recoverable and useful**, what measurement history it needs, what information it preserves, and where reuse breaks.

A plausible eventual deliverable is an **empirical recoverability profile**: for a specified task/state model, quantify prediction and uncertainty as the available units, history duration, noise/missingness and target domain change. This could guide recording choices and reveal which components of a task representation are stable versus context-specific. It is more informative than one attractive embedding or decoder leaderboard. Whether a particular implementation would constitute a novel literature contribution still needs a focused prior-art review; no first-of-its-kind claim is made.

Calling this an “observability profile” would require the explicit model-relative analysis in §4. Until then, call it **recoverability and transfer**, not a proof of hippocampal observability. The useful object may be a restricted task-state representation, not a complete model of the hippocampus. A robust negative result identifying nonrecoverable components or a strong linear baseline would also answer the question.

### Proposed final structure of this research-direction document

| Chapter | Purpose / decision it should support |
| --- | --- |
| **1. Motivation from the retrospective** | Why endpoint decodability, source-transfer failures and objective-dependent geometry motivate a new question; what previous goals are closed as a work stage. |
| **2. What “latent model,” “observable” and “reusable” mean** | Separate representation, state estimator, dynamics, observation model, readout, identifiability and controllability. Provide counterexamples, not just definitions. |
| **3. CEBRA's role and alternatives** | What contrastive sampling can buy; what it cannot guarantee; raw/PCA/linear-state-space baselines; when an explicit dynamics model becomes necessary. |
| **4. Candidate hypotheses and their falsifiers** | One primary question at a time, competing explanations, independent outputs and stop rules. |
| **5. Data/measurement routes** | Existing condition-level archive; verified local simultaneous groups; optional public simultaneous hippocampus bridge. Match claim strength to each route. |
| **6. Gated research programme** | Cheap representation-transfer pilot → predictive-state study → model-relative observability/measurement study → one reuse demonstration. No automatic cascade of experiments. |
| **7. Evaluation and falsification** | Source splits, frozen pipelines, nuisance/history baselines, causal timing, null/uncertainty, state ambiguity, domain shift and confirmation. |
| **8. Applications and scientific payoff** | Stable readouts, recording-efficient inference, cross-session reuse, independent behavioral/neural prediction; distinguish methodological promise from mechanism. |
| **9. Decision card and bounded next protocol** | Select claim level, data route, primary output/metric, meaningful effect and resource ceiling before implementation. |
| **Appendices** | Literature decision map; data-readiness contract; future figure specifications; retrospective evidence links and review dispositions. |

Eventually condense Chapters1–6 into Document1's future-work section. Keep the full definitions, gates and competing hypotheses here so the retrospective does not grow into a speculative grant proposal.

## 2. What the existing work contributes—not just what it lacks

| Finding carried forward | Design implication |
| --- | --- |
| Endpoints are decodable in constructed pools; raw/PCA remain strong. | There is a concrete task-information assay and a serious low-complexity reference. We need not invent a new target merely to favor CEBRA. |
| Cue/navigation training helped pair accuracy more than start/goal accuracy. | Broader training may change which information is accessible. Test a declared transfer benefit, not just assume it learned a shared biological manifold. |
| Within-window performance and losses vary sharply across windows/recipes. | Measure whether one readout remains useful elsewhere. Accuracy, probability quality and representation stability must be separated. |
| Strong training-assembly performance did not ensure transfer to other sources. | A reusable model must face source/domain change, not just new recombinations of familiar data. |
| Geometry and decoder quality can move in different directions. | Use independent output prediction and measured representation fidelity together. Do not optimize the research claim around a visually simple cloud. |
| Pseudopopulations provide condition structure but no simultaneous population state. | Use the archive for condition-level methodological work; use an explicitly different data lane for trial-specific state estimation. |

The [October7 endpoint](reports/cebra-endpoint-time-readout-20261006/README.md) and [October5 path](reports/cebra-cue-time-readout-20261005/README.md) studies are not temporal/cross-phase state-model tests. Historical **within-cue raw-LDA goal generalization already exists** in the [September28 report](professor_updates/research_review_20260928/README.md); matched October CEBRA cue/joint transfer remains a proposed extension, not the invention of temporal decoding from scratch.

## 3. A vocabulary that makes the ambition testable

Use the following as a **conceptual model**, not a claim that its quantities are observed or its equations already fit:

```text
latent task/neural state s_t ── dynamics F, inputs u_t ──► s_(t+1)
          │ observation map G_j                         │
          ▼                                             ▼
recorded subset x_t, mask m_t                        future recordings
          │ causal estimator E(x_≤t, m_≤t, allowed inputs)
          ▼
state estimate z_t ── readout H_k ──► independent output y_(t+Δ)
```

- **Recordings `x_t`:** sorted spike counts/events from a specified set of units. Selection, exposure, missingness and noise belong to the measurement model; unavailable is not zero spikes.
- **Representation `z_t = E(x)`:** a learned feature vector. Standard CEBRA supplies an encoder of specified input windows; it does not automatically supply a transition law, generative observation model or uncertainty-calibrated observer.
- **Dynamics:** `s_(t+1) = F(s_t, u_t) + process noise`. Inputs include stimuli/actions/history where justified. Omitting important external inputs can make an apparently autonomous model misleading.
- **Observation model:** `x_t ~ p(x_t | s_t, recording configuration j, m_t)`. This describes how a latent state would generate partial recorded activity; it is not a task classifier.
- **Readout:** `y_(t+Δ) ~ p(y | z_t)`, for a specified external behavioral quantity or withheld neural observation. The output must not be available to the estimator at prediction time.
- **Predictive state representation:** a compact summary useful for a declared family of future predictions. It need not equal a unique physical brain state or be sufficient for every possible downstream task.
- **Identifiability:** whether model parameters/representations can be distinguished from the data, often only up to an allowed transformation. This differs from estimating the current state when a particular model is given.
- **Controllability:** whether inputs can move a system among states. It is not implied by observing/decoding a state, and no intervention/control application is established here.

**Important non-circularity:** predicting tomorrow's `z` computed by the same encoder is not sufficient validation of `z`. A phase clock or nearly constant code could excel at that task. Evaluate withheld measured outputs as well. Even good output prediction supports an empirically useful model, not unique recovery of the actual biological state.

**Three endpoint heads are not three independent downstream applications.** Pair identity contains start and goal by definition; separating their heads tests factor readout, not broad transfer. A reuse claim should eventually include an independently motivated output or domain absent from the representation-selection criterion.

## 4. An observability ladder, with explicit ceilings

| Level | Operational question | Evidence required | Strongest allowed conclusion |
| --- | --- | --- | --- |
| **A. Task-information recovery** | Can neural-derived features predict a specified task variable? | Source-safe held-out readouts, sensible baselines/controls and valid target construction. | Information is accessible to these predictors in this evaluation object. Current studies mostly live here. |
| **B. Readout/representation reuse** | Does a fixed readout or limited adaptation work across time, phase or domain? | Freeze declared pipeline; evaluate matched target semantics and domain support; state adaptation budget. | Tested predictive relation/feature utility transfers within the stated scope. Not a state-observability theorem. |
| **C. Predictive state estimation** | Does a neural-history-derived estimate support independent future neural and/or behavioral predictions beyond task/history baselines? | Genuine time-linked observations, causal filtering, explicit prediction horizon, independent outputs and linear/static controls. | Evidence for a useful restricted predictive state under this measurement regime. True-state recovery still unproved. |
| **D. Model-relative observability** | For stated dynamics/measurements, can distinct candidate states be distinguished from output histories, and robustly under noise? | Explicit model, identifiability/gauge conventions, structural/local analysis plus finite-data ambiguity/uncertainty tests. | Observability or practical recoverability of the **specified model**, in tested regions/conditions—not of the entire hippocampus. |

### Why high decoding accuracy is not enough: an analytic counterexample

Let a state have two independent components, `s=(a,b)`, and let the recording contain only `x=a`. If the target is `sign(a)`, a decoder can be perfect while `b` remains completely hidden. If future `a` also never depends on `b`, no observation history recovers `b`. A perfect task readout does not establish full-state observability. Conversely, a bad finite classifier need not imply that a state component is structurally unobservable.

For the elementary **linear, known-model, noiseless** case `s_(t+1)=A s_t`, `x_t=C s_t`, the stacked observation matrix is

```text
O_H = [C; CA; CA²; ...; CA^(H−1)]
```

Full column rank permits reconstruction of the initial state from that output history; for a d-dimensional time-invariant system, the usual rank test uses at least the d-step observability matrix. Rank is not a guarantee of useful estimation with finite noisy data: a poorly conditioned problem can amplify noise severely. For smooth nonlinear systems, Hermann–Krener Theorem3.1 gives the observability rank condition as **sufficient for local weak observability**; this is not a global uniqueness certificate. Their Example3.3 explicitly illustrates locally distinguishable states with globally indistinguishable counterparts [R4, pp.733–734]. A failed rank test at a singular point is not, without the relevant converse assumptions, proof of nonobservability.

The same representation can be expressed as `z' = T(z)` for an invertible transformation with corresponding changes to dynamics/readouts. A rotation or rescaling need not change predictions. Therefore **latent-axis agreement is not required for useful reuse**, but any learned alignment must be fitted on training data and its adaptation budget disclosed. Numerical conditioning/singular values depend on coordinate scale; fix the state convention and prefer output-based uncertainty checks rather than comparing arbitrary latent condition numbers.

A theoretical observability calculation can be done on a proposed model without new recordings. What current pseudopopulations cannot validate is that this is the observable **single-trial biological population model**. Small verified simultaneous groups may be useful; no universal “195 simultaneous neurons” requirement follows.

## 5. Candidate research hypotheses—not a new numbered H1/H2 yet

### Candidate A — reusable task coordinates (near-term bridge)

**Question:** does broader cue/navigation CEBRA-Time training produce a readout that transfers across cue times or phases more reliably than cue-only CEBRA, and how does that compare with raw/PCA?

- **Proposed benefit:** off-diagonal/cross-phase predictive utility, not mandatory superiority in same-window accuracy.
- **Competing explanation:** joint training changes exposure/regularization, or simply learns time/condition structure imposed by assembly.
- **Test:** one predeclared source-safe train-time × test-time summary; separately report diagonal reference and whole-cue context. A fixed1,000-update50/50 comparison reallocates cue exposure. If the claim is specifically about navigation content, add an exposure-matched control in a later approved design rather than call the existing comparison causal isolation of that content.
- **Falsifier/bounded negative:** no reproducible absolute transfer or joint benefit at the agreed effect size on admissible evaluation. High diagonal scores with weak transfer are themselves informative.
- **Ceiling:** current archive yields exploratory **condition-level readout transfer**, not an online state estimator or proof of biological geometry.

### Candidate B — a restricted predictive state (recommended central ambition)

**Question:** can a compact representation estimated from past neural observations predict an independently measured future output beyond current-bin, task-clock and behavioral-history models, while retaining useful readouts for another declared output?

- **Proposed benefit:** the latent estimate summarizes neural history in a way useful outside the single label used to tune it.
- **Test:** verified time-linked recordings; compare static/raw-history/PCA-history, a simple dynamical model, and one justified CEBRA-based representation/transition design. Same available history, causal timing and training budget must be respected. Define a primary future neural or behavioral output and one secondary reuse test before results.
- **Falsifiers:** performance explained by cue/phase/history alone; no benefit over a matched linear model; future information enters the encoder; supposed reuse requires retraining the entire model; output skill disappears on a new supported domain. A linear model winning rejects the nonlinear advantage, **not** the usefulness of a predictive-state question.
- **Ceiling:** predictive sufficiency is relative to the measured outputs/horizons. Neither all hippocampal functions nor hidden cognitive mechanisms are identified.

### Candidate C — measurement-limited recovery (the deeper observability arm)

**Question:** which aspects of the specified predictive state remain distinguishable as measurement coverage and history are limited?

- **Test:** after a model/data contract exists, define a small design over unit availability and causal history length; assess held-out output quality, empirical ambiguity and calibrated predictive uncertainty. On a known synthetic system, additionally measure true-state recovery up to declared equivalence. On real data, do not invent latent ground truth.
- **Competing explanation:** smooth task timing makes the state appear recoverable; latent dimension was chosen to make a rank test pass; subsampling changes task support or preprocessing; remaining units encode the same nuisance.
- **Falsifier:** different candidate states remain observationally indistinguishable yet imply materially different allowed predictions, or estimates fail under the declared measurement regime. Failed estimation alone does not prove structural nonobservability; distinguish model misspecification, data scarcity and algorithmic failure.
- **Ceiling:** a finite-recording property of this model and task distribution, not a universal minimum neuron count or whole-hippocampus reconstruction result.

**Recommendation:** use A as an optional cheap bridge, B as the central scientific ambition, and C as the explicit observability extension. Do not require a positive A result to permit B with genuinely different data; a transfer failure may motivate a time-varying or dynamic representation rather than a stable readout. Do not run all three automatically.

## 6. Data routes: one current lane and two conditional extensions

| Route | What it can answer | Readiness / boundary |
| --- | --- | --- |
| **Existing saved pseudopopulation archive** | Condition-level recoverability; matched frozen time transfer; source/assembly sensitivity; descriptive geometry. | Available reports/models, but only reports were read here. Historical exposure and known-label assembly remain. It cannot supply an unknown-trial full-population state. Condition-averaged temporal structure may be described; unrecorded trial-specific covariance/dynamics may not. |
| **Verified local simultaneous groups** | Within-group causal history → future neural/behavior prediction; limited state estimation and masking studies. | Verify actual simultaneity, clocks, unit inclusion, task semantics and longitudinal support. Current selected snapshot has1–8 listed units/session, not a verified complete population. Existing manifests first; request only the data needed after design. No speculative raw extraction. |
| **Public simultaneous hippocampal benchmark** | Method development, measurement/noise validation and a feasibility bridge for B/C if local data are unsuitable. | Optional separate authorization, license/access check and frozen split. CEBRA's rat linear-track example is a precedent, not equivalent to this lab's task/species or evidence about its recordings. A public-method result cannot fill missing lab metadata. No download proposed as an automatic task. |

If local simultaneity/target semantics cannot be established, choose explicitly between a **condition-level representation paper** and a **methods study on appropriate simultaneous data**. Do not claim that stitching sessions fixes the missing measurement. Conversely, do not block useful condition-level work pending a large new recording campaign.

### Minimum lab questions for the state-model route

1. Which units share a verified acquisition interval, neural clock and trial identity? Is the selected list complete for that group, and what were sorting/selection criteria?
2. What are species/subject/session relationships, cue/goal/start meanings and behavioral timing? Which external inputs actually reach the animal, and when?
3. Which behavior/view/heading/speed/history measures are reliable enough to model confounds or inputs? What cannot be separated because of task design—for example goal from its unique cue image?
4. Is there enough source support within each proposed group/condition/horizon? Which sources are genuinely unexposed or can be prospectively reserved?
5. Which **one downstream use** matters to the lab: across-time goal readout, future neural prediction, reduced-channel estimation or another independently measured variable?

## 7. A gated programme, not a model shopping list

| Stage | Deliverable | Gate to proceed / stop |
| --- | --- | --- |
| **0. Close and define — current documentation task** | Document1 structure/evidence audit; this agenda; a chosen meaning of observability and proposed contribution. | Hongyi/mentor narrow one question and data route. No fits are part of this stage. |
| **1. Optional saved-model transfer pilot** | Reviewed compatibility map and, only after authorization, a matched cue-time transfer matrix with predefined summaries/nulls. | Existing encoder/readout/scalers and lineage must be compatible. If not, return a bounded fitting proposal rather than silently refit. Historical result stays exploratory. |
| **2. Predictive-state feasibility** | Verified-data contract; one output/horizon; one simple baseline and one CEBRA-based design; causal/source-safe evaluation. | Simultaneity needed for same-trial multineuron claims; task/nuisance support and sufficient held-out observations. If unsupported, narrow output/claim or choose another authorized dataset. |
| **3. Observability/measurement study** | Known-system sanity checks; model-relative distinguishability analysis; limited measurement/history robustness profile on real data. | Explicit model, coordinate conventions and outputs. Do not call a performance-vs-neuron curve a formal rank proof. |
| **4. One downstream reuse demonstration** | Frozen-encoder or explicitly budgeted adaptation comparison on an output/domain excluded from original selection. | Same measurement/target meaning or an explicit training-only alignment. Failure is reported, not erased by full target-domain retraining. |

### Smallest useful next experiment proposal—not yet a protocol

If we choose the existing-data bridge, prepare **one endpoint temporal-transfer question** using the October saved cue/joint models and raw/PCA references. Pick the primary target from task meaning/support—not from the best historical joint gain. Start/goal/pair can remain secondary context, but pair/start/goal are not independent confirmations.

For this saved-model bridge, each evaluated input is exactly **one100-ms cue bin** passed through the saved pointwise encoder (or raw/PCA transform), not a500-ms history or the whole cue. Score it only after that bin ends; it contains no later bins or symmetric context. A causal-history encoder would be a separate new design, not something recovered by relabelling these features.

For a matrix row at training time `t`, freeze the encoder, input scaling, decoder scaling, readout, thresholds and calibration, and evaluate across development times `t'`. No row-wise refitting on test-time inputs. Separate encoders get their own trained readouts; do not transplant weights into independently fitted latent coordinates. All source derivatives remain in the same split. Verify matrix diagonals against saved same-window results.

Choose a fixed off-diagonal region or other scientifically justified summary **before computation**, with an absolute predictive baseline as well as any cue/joint contrast. Avoid unstable ratios when diagonal performance is near chance. Include a guard against overlap of input receptive fields masquerading as temporal stability. If matched null models permit replay, use the same matrix/summary in every null world; otherwise the missing control changes the scope or requires a separately approved budget. Do not select the brightest cells or infer biological rotation from a diagonal/off-diagonal pattern alone [R3].

This is deliberately smaller than all-target × all-decoder × all-objective × all-phase experimentation. Its value is deciding whether a particular transfer claim is promising, not exhausting an ablation grid. If the lab means formal dynamical observability rather than readout reuse, Stage1 may be skipped in favor of the model/data design for Stage2.

### Recommended state-model strawman for discussion — not frozen

To make “reuse” concrete, the following is a **default design to criticize**, not the chosen experiment. It belongs to Stage2, requires verified simultaneous recordings, and cannot be run on stitched endpoint pseudotrials. It is more demanding than the optional saved-model bridge.

| Decision | Proposed default |
| --- | --- |
| Scientific object | A within-recording-group, navigation-period predictive state; no claim to all hippocampal state variables. |
| Primary output | Next100-ms spike counts in designated held-out units, predicted from the preceding500ms of other simultaneously recorded units. These durations are illustrative starting choices, to be justified from task timescales and support before freezing. |
| Estimator inputs | Neural history ending at prediction time, unit identities/masks and no future spikes, test target labels or test-time condition-based assembly. The held-out-unit mapping may use separate training trials; their evaluation activity is never an input. |
| CEBRA role | One causal-history CEBRA-Time representation with a small prediction head/transition model; no position labels used to learn or select the encoder in this version. A simple latent transition is a candidate addition, not a built-in property of current CEBRA. |
| Primary comparison/metric | Held-out predictive count log-likelihood gain relative to a predeclared baseline; report calibration and per-unit/source detail. A Poisson likelihood is a modeling choice to check, not an assumption that standardized counts are Poisson. Include task/history-only, matched raw/PCA-history and a simple dynamical reference; select a compact baseline set before fitting. |
| Covariate contract | Evaluate whether neural history adds to known current/past task/behavior variables by comparing covariate-only versus covariate+neural predictions. Keep a separately reported neural-only arm if that is the desired deployment use; no future behavior is an input. |
| Concrete reuse test | Freeze the resulting encoder and fit one small **current-position** readout on separate training examples; evaluate on held-out trials. Position must be independently measured/aligned, not an endpoint-derived canonical route. This tests feature reuse for another output, not zero-shot inference or proof of a cognitive map. |
| Selection boundary | Representation/hyperparameter selection uses training-only neural-prediction validation. The position reuse evaluation is not used to choose the encoder, dimension or checkpoint; any readout tuning stays inside training data. |
| Success/stop | Agree an effect size/uncertainty criterion in advance. Stop the nonlinear-benefit claim if simple/history controls match it, with uncertainty accounted for. If there are too few verified simultaneous units or independent sources, return a feasibility limit or propose an authorized public-data route—do not repair support by pseudopopulation assembly. |

A successful version would show **neural-predictive features reused for a separately measured spatial output**, under an explicit observation budget. It would still not prove recovery of every hidden biological state. A position readout alone is a weak novelty claim in place-selected cells; the proposed contribution is the controlled reuse/measurement result, not rediscovery of spatial selectivity. If the mentor prioritizes memory/goal rather than spatial prediction, replace the secondary output before protocol freeze and audit whether it is distinguishable from cue identity.

## 8. Evaluation requirements that make the research more than decoding

### Independent outputs and causal timing

- Distinguish **filtering** from smoothing: an online estimate at time`t` uses only information available by`t`. A symmetric receptive field or whole-trial encoder may use the future; useful offline reconstruction must be labelled as such and cannot be reported as forecasting.
- Split complete source trials before learning and exclude temporal overlap across folds. Decide serial/block structure and uncertainty at the actual independent unit, including session/animal nesting; seeds/bins are not N.
- **Held-out-neuron prediction** means infer state without those neural observations at evaluation. Their mapping can be learned from separate training trials. This is not automatically prediction of an entirely unseen cell with no identity/calibration data.
- Separate same-time co-smoothing from future prediction. They answer different questions; future prediction may be limited by unpredictable external inputs [R5–R6]. State the forecast horizon and which inputs are known at inference.
- Future **behavioral history** must not be supplied to a supposed neural-only predictor. A joint neural+behavior model is a legitimate different input contract, reported separately.

### Baselines, nulls and confounds

Use a small justified ladder: constant/condition or task-phase reference → allowed behavioral-history-only reference → raw current-bin/history regularized readout → PCA/static or simple linear dynamical reference → candidate CEBRA design. The exact set follows the output; no need to fit every listed model. For joint neural+covariate models, compare the incremental neural contribution against the identical allowed covariates alone.

Time/cue/history models are essential: an endpoint, phase clock or average trajectory can predict much without recovering richer state. If cue identity perfectly determines goal, this observational task cannot cleanly separate cue sensory information from goal meaning. Controls expose this limit; they cannot conjure missing independent variation. Report selection, gaze/view/heading/speed and session dependencies where data permit; label unavailable controls, not fabricate them.

Behavior-supervised CEBRA can legitimately use training labels. Evaluation must withhold test labels from **all inference inputs, assembly and adaptive alignment** for a deployable-state claim. Test transfer to something not already hard-coded by supervision, and compare an appropriate supervised reference. A shuffled-label control must respect source/time structure and repeat any label-dependent construction/selection; a naive bin shuffle changes the problem.

Agree the primary metric, minimum useful effect, multiplicity family, uncertainty method and fit budget before fitting. Use meaningful absolute performance alongside improvement over another model. Failure to reject a null is not equivalence; noninferiority requires a predefined margin and adequate uncertainty, not two similar means. No numerical threshold is adopted by this agenda.

### Two different robustness experiments

1. **Refit on fewer available units:** estimates training/data efficiency for that restricted sensor set. Fit scalers/encoder/readout within each training subset. It is not robustness of the same deployed model.
2. **Remove/mask units after training:** tests fault tolerance of one fixed estimator, only if its inference contract handles masks/missingness. Arbitrary zero-filling after standardization is an intervention, not a faithful “unrecorded neuron.”

For pseudopopulations both are condition-level representation tests. For verified simultaneous data, they can address same-trial sensor limitations. Neither makes unobserved covariance recoverable by assumption. Specify session-block versus unit sampling, source coverage and whether nuisance/task support changes.

### Transfer must specify what is allowed to change

| Transfer regime | Frozen / allowed to learn | Interpretation |
| --- | --- | --- |
| Fixed readout across time/phase | All transforms/encoder/readout frozen within a coordinate system. | Stability of that predictive relation. |
| New output from an existing representation | Encoder frozen; small readout trained only on target-task training examples. | Feature reuse, not zero-shot task prediction. |
| New session with different neurons | Measurement adapter/alignment may be trained on declared calibration data; backbone policy explicit. | Adaptation/data efficiency, not literal identical-input transfer. |
| Entire model retrained in target domain | Nothing meaningfully frozen. | New model performance, not evidence of a reusable original representation. |

## 9. What could we use the model for?

**Near-term scientific applications:** test recurrence/stability of task information across cue/navigation; distinguish a generic task-clock account from neural-history prediction; quantify recording coverage/history needed for a declared predictive objective. Negative results can show that a stationary readout is inadequate or that observation limits dominate a model choice.

**Later methodological applications:** infer a useful state with fewer recorded channels; reuse an encoder with a small readout for another measured variable; adapt across recording sessions with explicit calibration; predict missing neural channels or forecast activity with uncertainty. Each requires its own data/transfer contract, not a claim that a latent foundation model has already been built.

**Blue-sky extension:** a shared task-relevant latent core with session-specific observation maps and a context-dependent dynamical model. CEBRA could supply a consistent representation or initialization; an explicit transition/observation model could support prediction and uncertainty. Test whether shared structure helps held-out outputs under a fixed calibration budget before claiming a general hippocampal model. Excessive invariance can erase useful context; task-driven latents may lose information needed by an unforeseen downstream task. The desired invariance is itself a scientific choice [R1,R7].

**Outside current claims:** intention/planning mechanisms, whole-hippocampus digital twins, causal intervention policies, cross-species universality, or an artificial navigation agent matched to the brain. A fitted neural-state RNN/latent dynamical model is not a reinstatement of the removed artificial-agent H2, but it still needs its own justification and protocol.

## 10. Figure plan for this document / future paper

No unexecuted result is drawn as data. Until the relevant study runs, these are **figure specifications**, not empirical placeholders.

| Figure | Purpose | Availability |
| --- | --- | --- |
| Representation → readout versus state → observations diagram | Prevent category errors and show inference-time inputs. | Conceptual diagram in §3; explicitly schematic. |
| Retrospective evidence bridge | Motivate stability/reuse rather than a score chase. | Link/reuse Document1's source/performance/null panels, with unchanged captions. |
| Train-time × test-time matrices plus seed/source detail | Test fixed-readout reuse; show absolute skill and paired contrasts. | Historical LDA exists; matched October CEBRA comparison not yet run. |
| Independent future-output predictions and residuals | Show whether state estimates add beyond clock/history/linear models. | Unavailable; requires Stage2. |
| Recovery/uncertainty versus sensor/history budget | Operational measurement limits; distinguish refit from fixed masking. | Unavailable; requires Stage3. |
| Known-state synthetic recovery and ambiguity examples | Check that the proposed procedure detects recoverable and nonrecoverable cases. | Not executed; methodology check, never biological evidence. |
| Calibration-budget versus transferred performance | Demonstrate reuse rather than target-domain retraining. | Unavailable; requires Stage4 and a specified application. |

## 11. Literature decision map

Primary methodological sources and official materials inspected during planning. These motivate design choices, not evidence for our lab dataset. No claim of a comprehensive systematic review or newest-method survey is made.

| Ref | Source / inspected section | What to borrow | What not to import |
| --- | --- | --- | --- |
| **R1** | Schneider, Lee & Mathis (2023), [*Learnable latent embeddings for joint behavioural and neural analysis*](https://www.nature.com/articles/s41586-023-06031-6). Main sections “Joint behavioural and neural embeddings,” “Robust and decodable latent embeddings,” Fig1–2 and identifiability discussion. | Explicit positive/negative sampling; time/behavior/hybrid objectives; decodability and consistency as separate checks; training-only downstream evaluation. | Its consistency/identifiability results depend on model/distribution/diversity assumptions and allowed transformations. They do not prove our finite noisy embeddings recover physical state or establish formal observability. |
| **R2** | Official [CEBRA consistency example](https://cebra.ai/docs/demo_notebooks/Demo_consistency.html) and [best practices](https://cebra.ai/docs/demo_notebooks/CEBRA_best_practices.html). | Explicitly name alignment, labels and consistency metric; repeat-run checks and proper validation. | Behavior-aligned agreement is not independent confirmation of the same biological coordinates; exact current notebook API is not audited for our installed runtime. |
| **R3** | King & Dehaene (2014), [*Characterizing the dynamics of mental representations: the temporal generalization method*](https://pmc.ncbi.nlm.nih.gov/articles/PMC5635958/). Box1 and generalization-across-time sections. | Train-at-one-time/test-at-other-times with held-out observations; separate diagonal and off-diagonal information. | A transfer pattern is not a formal observability analysis or unique diagnosis of rotation/processing stages. |
| **R4** | Hermann & Krener (1977), [*Nonlinear controllability and observability*](https://www.math.ucdavis.edu/~krener/1-25/10.IEEETAC77.pdf). Pages733–734, definitions, Theorem3.1 and Example3.3 (visually checked from the scanned original). | Explicit dynamics/measurement map, distinguishability, local versus global claims. | Rank/local weak observability is not finite-noise performance or proof that the chosen state model is the biological truth. The simple linear example in §4 is illustrative, not a new nonlinear derivation. |
| **R5** | Pandarinath et al. (2018), [*Inferring single-trial neural population dynamics using sequential auto-encoders*](https://pmc.ncbi.nlm.nih.gov/articles/PMC6380887/). LFADS model and held-out-neuron/behavior prediction. | Separate generative dynamics, neural observation model and external validation. | Offline inferred trajectories and successful predictions alone are not online causal filtering or unique circuit identification; motor examples do not establish hippocampal applicability. |
| **R6** | Pei, Ye et al. (2021), [*Neural Latents Benchmark ’21*](https://arxiv.org/abs/2109.04463), metrics; [official benchmark overview](https://neurallatents.github.io/). | Distinguish co-smoothing, behavior prediction and forward prediction. | A benchmark metric does not prove true latent-state recovery; future external inputs can limit forecasting. Public evaluation data are not automatically pristine confirmation. |
| **R7** | Sani et al. (2024), [*Dissociative and prioritized modeling of behaviorally relevant neural dynamics using recurrent neural networks*](https://www.nature.com/articles/s41593-024-01731-2). DPAD model/results rationale. | Separate behavior-relevant dynamics from other neural variation; state the trade-off between neural reconstruction and task utility. | Excellent reconstruction need not retain the task information we want; excellent task prediction need not preserve all neural dynamics. DPAD is a comparison/design reference, not an instruction to implement another large model suite. |

Formal-state reconstruction, identifiable representations, temporal readout transfer and prioritized predictive dynamics are related **but different** literatures. No single citation licenses collapsing them into “CEBRA learns the observable hippocampus.”

## 12. Recommended choices for our next discussion

1. **Adopt the ambition, not a promised outcome:** a restricted, estimable and reusable task-state representation; no universal CEBRA-win requirement.
2. **Choose claim level:** is the first deliverable condition-level recovery/readout reuse (ladder levels A/B in §4), or predictive-state/model observability (levels C/D)? Recommendation: **Candidate B, predictive-state estimation (§5)** as the long-term scientific center, with the cheap readout-transfer pilot optional. These candidate names are not replacement H1/H2 labels.
3. **Choose the measurement route:** existing archive for a bounded bridge; verified local simultaneous groups for biological state claims; an explicitly separate public-data methods route if local data cannot support them.
4. **Choose one downstream use and primary metric before choosing a larger model.** Recommendation: independent future-output prediction with an allowed-input/history baseline, followed by one frozen-encoder reuse test.
5. **Decide how much new work Document1 needs.** Recommendation: none to begin writing; missing ablations are transparent gaps, not an obligation to fill a Cartesian grid.

The shortest defensible path is **retrospective closure → explicit target state/use case → admissible data → one falsifiable protocol**. It is not “observe a nice CEBRA cloud, then name it a hippocampal model.”

## 13. Review and remaining decisions

All reviews were read-only; the parent was the sole writer. Review artifacts remain in the existing host-local Pi session store; the dispositions below are the portable record, not a dependency on those transcripts.

| Iteration / run prefix | Finding / disposition |
| --- | --- |
| Evidence and literature audit `4e57d948` | Scout mapped completed cohorts/ablations/assets; researcher separated recovery, transfer and formal observability. Parent corrected an overbroad missing-temporal-work statement: historical raw-LDA goal matrices exist. |
| Research-design challenge `1176a39f` | Incorporated non-circular future-output validation, clock/history/unknown-input alternatives, causal filtering, measurement limits and a positive reuse ambition. Did **not** adopt new numbered H1/H2 labels, a presumed sharp neuron-count phase transition, or mandatory CEBRA superiority. |
| Actual draft review `4133aefb` | Researcher requested a concrete downstream-use default, narrower heterogeneous-path closure, scoped metric-winner wording and explicit saved-bridge inputs. All four addressed: Stage2 decision card, Document1 closure, pair30 metric distinction, and single100-ms input contract. Independent evidence reviewer found no issues in representative/high-risk results and coverage. |
| Revised-draft research review `b2d77650` | Approved with no major scientific-design blockers; minor ladder-level versus candidate-letter ambiguity corrected in §12. Reviewer read both revised documents fully; did not repeat raw/numerical/literature verification. |

Parent verification: all15 endpoint whole-cue BA means and pair losses recomputed from the tracked aggregate CSV, not model predictions; all205 local Markdown/image links in the nine changed/new documents resolved at the pre-delivery check. The scanned Hermann–Krener pp.733–734 were visually read after automated text extraction failed; downloaded paper/page images were temporary and removed. No new HTML rendering or browser validation is claimed. Existing source figures/reports retain their original QA/provenance. `git diff --check` passed; session diagnostics found no blocking errors and one Marksman ambiguous-link warning on README's unchanged V6–V9 link (its local target resolves). No full-project/software test run was needed for these documentation-only changes.

AI research review is QA, not mentor agreement, acquisition verification or external peer review. Novelty, data readiness and a final inferential protocol remain open; the reviews approve the **planning document**, not an experiment.

No model/data experiment is part of this proposal. The lab's intended meaning of observability, measurement metadata, an independently meaningful output and a worthwhile effect size remain explicit decisions for the next conversation.
