# Place195 V6–V9: learning what a prospective-path experiment can actually tell us

**Date:** 2026-09-06 (+08). **Teaching rewrite; scientific results unchanged.**  
**Review status:** separate pedagogical review passed; factual review approved after repairing two reproduction-command destinations. Scientific results are unchanged. Appendix E distinguishes the original scientific audits from these teaching-rewrite reviews.  
**Scope:** exploratory, development-only selected-cell/condition-level pseudopopulation benchmark. No new analysis or model fitting was performed for this rewrite.

## 0. Before the experiment: what are we trying to learn?

Imagine that an animal is told where to go, waits through a cue period, and then navigates a familiar maze. We want to know whether hippocampal activity during that earlier cue contains information about **which path the animal will subsequently take**, beyond information about its starting point and destination. This is not primarily a competition between PCA and CEBRA. It is an attempt to make a biological question observable, then ask whether the available recordings can distinguish plausible explanations.

For an NLP analogy, knowing that a model has represented the prompt's destination is not the same as knowing which of several valid continuations it will generate. Here, however, we cannot inspect the complete hidden-state vector. We observe spike timestamps from selected recorded units. A spike is an electrical event assigned to a unit by recording and sorting procedures; a spike count is our summary of those events over an interval. A firing rate, a low-dimensional state, a route representation, and an intention are progressively more inferred objects. None is directly handed to us by a spike timestamp.

The relevant order is:

```text
previous trial/history → current cue onset → cue-period spikes → cue offset
                      → subsequent navigation → measured path and outcome
```

The exact task meanings and clock alignment still need authoritative metadata. Nevertheless, this order explains the central safeguard: the predictor uses cue activity, whereas the target is derived from later behavior. Navigation-period spikes cannot be quietly included in a purported cue predictor. Equally, predicting later behavior does not by itself establish planning: a cue, gaze direction, motor preparation, trial history, or session-specific state could affect both cue firing and the later path.

### The objective and its competing explanations

The conceptual information question is

\[
I(P;X\mid S,G)>0.
\]

Here \(P\) is the subsequent observed path, \(X\) is cue activity, and \(S,G\) are start and goal. Conditional information means that learning \(X\) reduces uncertainty about \(P\) *after* start and goal are known. We did not directly estimate this information quantity. Its practical inspiration is a held-out comparison between an endpoint-only predictor and an endpoint-plus-neural predictor.

**H1a concerns information:** does cue activity improve prediction of future path beyond endpoints? **H1b concerns structure:** does that information, if present, have reproducible low-dimensional organization? These are linked components of one hypothesis, not interchangeable tests. A failed embedding does not show that information is absent. Conversely, an attractive embedding does not show that it contains incremental path information.

Before looking at outcomes, at least four explanations deserve consideration:

1. Cue responses contain something related to the upcoming route beyond endpoints.
2. Cue responses encode the goal, visual cue, or current state, and these variables correlate with the route. Goal decoding alone would fit this explanation.
3. Apparent prediction arises from session availability, source reuse, selection, or train–validation instability rather than a reproducible route relationship.
4. Relevant biological information exists but is inaccessible to this selected-cell sample, timing convention, behavioral target, or model family.

A useful experiment must do more than produce a score: it must say which explanations that score weakens, and which remain indistinguishable. The present data cannot fully separate them. The following iterations therefore teach both the measurement progress and the reason the biological claim remains bounded.

### What was known when: a knowledge timeline, not hindsight

**Before V6:** the available snapshot comprised 195 place-selected cue-accessible cells across 58 sessions, with 1–8 selected cells per session. It was not a verified simultaneous 195-cell population. Imported cue events and cue-window metadata already existed. Start inference from the previous successful goal motivated a success-after-success endpoint-labelled subset; formal task-label semantics remained unresolved. The geometry was a thick floor around four pillars, not a narrow track. V5 had already exposed fragmented route signatures and 74.28% masked entries in its older pseudopopulation. These were warnings about representation and support, not V6–V9 neural outcomes.

**During an initial, rejected V6 probe:** unfiltered endpoint aggregates included, or almost certainly included, locked-test rows. This was a real exposure incident, not a harmless final-report detail. Design state could have been influenced even though no accepted graph artifacts came from that probe. The worker was stopped; graph derivation was restarted using static geometry and guarded development access. That reset did not erase what had been seen. All results here are development-only; there was no subsequent test model evaluation. A fresh random split of already inspected data does **not** restore an untouched holdout. Confirmation needs genuinely unexposed data.

**After accepted V6 and its support refinement, before neural fitting:** a directed component within a fixed endpoint pair and a small common panel were selected from behavior/support evidence, not neural predictive performance. At this point we knew that synthetic resampling would be severely source-limited; we did not yet know whether neural decoding would work.

**After V7/V8:** whole-cue baselines were unstable, and an independent reviewer identified a perfect individual time bin that the short summary had not emphasized. This prompted V8b diagnostics, not a new primary time-window choice.

**Before V9:** the whole-cue target, panel, dimensions, seeds, decoder, and bounded training/null budgets were fixed. V9 was authorized as an exploratory engineering and representation benchmark despite nonpositive baselines, not because a positive biological result was guaranteed. **After V9:** the accepted results were nonpositive. The remaining sections reconstruct those decisions in that order.

### What the literature contributed—and what it did not

You need not have read these sources to follow the report. Each supplies an idea, not a license to transfer its conclusions.

- **Johnson & Redish (2007)** reported rat CA3 ensemble representations of locations ahead of the animal during decisions, including sweeps down alternative paths. The useful idea is that neural activity can relate to locations other than the animal's immediate position, motivating a prospective question and attention to time. It does not establish the same phenomenon during a pre-navigation cue in this monkey dataset, nor permit sequence claims from stitched cross-session recordings.
- **Loren Frank Lab's track-linearization work** shows how a graph can connect continuous position to interpretable track segments and progress. The transferable idea is an explicit behavioral ruler. Its narrow-track assumptions and HMM map-matching implementation were not automatically appropriate or adopted wholesale for our broad floor.
- **Cunningham & Yu (2014)** explain why a population with many recorded units may admit lower-dimensional descriptions. The useful question is whether shared variation can be summarized without losing relevant information. A low-dimensional projection is not, on its own, evidence for a biological manifold or a particular task variable.
- **Schneider et al. (2023), CEBRA**, motivates learning embeddings through deliberately chosen relationships between observations. Time or behavior can define what should be nearby. The choice of relationships is part of the experiment, and behavior supervision shapes the answer. Their results do not guarantee performance with our sparse synthetic population.
- **Kobak et al. (2016)** supplies context for separating task-related population variation: variation can mix multiple experimental factors. We did not fit demixed PCA here. Its relevance is a warning that total variance and route-specific information are different objects.

Only previously verified source scope is used here; URLs and local research notes are in the appendices. Bernardi et al. was optional reading metadata, not a full-methods source verified for this report. The Ferbinteanu–Shapiro primary full text was not verified in planning and is not used to establish a result here.

## 1. One invented example to carry through all the methods

**Everything in this section is invented for teaching. It is not additional experimental data, a simulation result, or a model fit.**

Suppose two trials start at A and end at B. One path goes through a right-hand corridor from its upper region to its middle region; the other goes around a different side. Call that ordered corridor traversal \(e\). Label the first path “present” and the second “absent.” Both have the same start and goal. An endpoint-only predictor cannot distinguish them. A cue-based predictor could, in principle, improve on that constant prediction.

Notice the choices already made. We have not attempted to predict every x–y position. We have turned an ordered continuous path into one binary question about a component. Passing through the same corridor in the reverse direction is not the same directed component. Two different whole paths can share \(e\), and two paths that both contain \(e\) may differ elsewhere. Component prediction is therefore a restricted path measurement, not complete route decoding.

Now invent one cell's spike counts in four successive 100 ms bins:

| Invented trial | Future component | Bin 0 | Bin 1 | Bin 2 | Bin 3 | Total |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| A-to-B trial u | present | 0 | 1 | 3 | 0 | 4 |
| A-to-B trial v | absent | 3 | 1 | 0 | 0 | 4 |

A whole-window count sees “4” in both trials and loses the difference. An ordered vector sees an early versus later response. This shows why preserving time might help; it does not show that the real data follow this pattern. It also shows why a zero matters: bin 0 of u was observed and contained no spike. If the cell was not recorded on v, writing zero would be a different and false statement.

Next invent three recording sessions. Session A contains cells a1 and a2; session B contains b1; session C contains c1 and c2. Each session has its own real trials with present/absent labels. A synthetic present-labelled row might combine:

```text
[a1 and a2, all bins, from session A's present trial u]
[b1, all bins, from session B's present trial w]
[c1 and c2, all bins, from session C's present trial z]
```

All cells from session A must come from the same source trial u, and u must supply all their cue bins. Choosing a1 from u but a2 from another trial would destroy even the within-session block relationship. Choosing a new source independently at each bin would invent a temporal sequence. The real pipeline preserves both blocks. That does not prove simultaneity from metadata; it preserves the source relationships that are available rather than breaking them further.

A rectangular source-storage array can have columns for a1, a2, b1, c1, c2. In row u, only a1 and a2 are observed. The other columns are unavailable and masked. The dense synthetic row is assembled from several such partially observed source rows. It is not a recovered measurement of all five cells on one real trial.

In probabilistic language, the synthetic construction samples approximately from

\[
Q(X\mid y)=\prod_s \widehat P_s(X_s\mid y).
\]

Here \(y\) is the known component label, \(s\) indexes sessions, \(X_s\) is a whole session's cell-by-bin block, and \(\widehat P_s\) is that session's finite empirical source pool within one split and endpoint pair. The product means independently selecting session blocks conditional on the label; it does not measure their true cross-session joint dependence. Sampling 128 rows estimates properties of this constructed distribution more densely. It does not create 128 new biological trials.

There is a second important consequence: **we know the label in order to assemble the row**. This is a condition-level distribution benchmark, not an operational unknown-label real-trial decoder. If handed a new real trial whose future route is unknown, we could not use that route to fetch matching recordings from other dates. Train-only fitting and source-separated splits control leakage *within* this benchmark; they do not remove the assembly conditioning or turn it into the full H1a experiment.

Keep this example in mind. V6 defines \(e\). The support refinement asks whether u, w, and z exist often enough for both labels. V7 preserves the ordered counts. PCA learns shared cell-space directions from the synthetic vectors. CEBRA learns which vectors to bring together under time- or label-based sampling. At every stage the biological source information remains the same; transformations do not manufacture it.

## 2. V6 — first build a trustworthy ruler for behavior

### Question / what we knew entering

What should count as a meaningful path difference in this maze? Before training any neural model, we needed a behavior-defined target that did not confuse tiny coordinate changes with different routes. The V5 floor-grid representation fragmented signatures and had severe missingness downstream. Its older multi-class validation scores were not a matched baseline for the new binary component task. Comparing those accuracies as model progress would compare different questions.

### Concept from first principles

A graph is a lossy measurement of a path. A **region** is an area the animal occupies; a **corridor** links regions; a **directed component** specifies traversing that corridor in one direction. A **raw path** remains the time-ordered coordinate sequence. Keeping all four objects lets us audit whether a graph label agrees with the underlying movement rather than merely trusting the label.

The floor geometry is a 40×40 grid minus four 8×8 pillar footprints: \(1600-4\times64=1344\) walkable centroids, spaced 0.625 **Unity-coordinate units**, not assumed meters. A floor-mesh node often has three or four neighboring floor cells simply because it lies in a broad open area. Its mesh degree is not evidence that the animal faced three or four cognitive choices. Contracting every degree-two chain would not transform this thick floor into meaningful decision junctions.

The accepted operational graph instead has nine node/plaza regions and twelve corridor regions, with twenty-four directed corridor components. “Decision region” describes an analysis convention. It is not a literal neural node or a verified full cognitive-choice model. A broad plaza permits continuous movement that a simple graph cannot completely summarize.

The implementation preserves raw coordinates and maps them to static region bands. Within a corridor, progress is a normalized coordinate along its axis; for a horizontal corridor it is \((x-x_{min})/(x_{max}-x_{min})\), with the analogous y expression vertically. This is progress through the corridor's region, not a full arbitrary-path arclength solver. Lateral distance from the centerline is also retained. Direction uses neighboring node evidence first, then net progress when available; weaker one-adjacent-node inference is identified separately. We do not claim every reversal or plaza distance is fully modeled, or that the planned general polyline/HMM framework was implemented.

### Why this choice over alternatives

A static geometry-aware map gave an interpretable target without learning its boundaries from neural prediction. A learned graph, skeletonization, arbitrary fine-grid signatures, and a full HMM map matcher would introduce additional assumptions before support was known. They were candidate ideas in planning, not all executed comparisons. The accepted choice was deliberately narrower: distinguish stable regions, corridors, direction, and observed gaps while retaining the continuous path for inspection.

In the invented example, we need to know whether the animal traversed \(e\), not whether every slight lateral deviation deserves its own route class. Conversely, filling an unobserved gap with a shortest path would create evidence for \(e\) rather than measure it. Unknown is not absent. That distinction matters because an “absent” neural label is only valid if the behavior supports absence under the mapping rules.

### What changed and actual dataflow

The accepted flow was static geometry plus split-filtered development behavior → region/corridor mapping → ordered traversals and junction motifs → component support by endpoint pair → neural-observation membership support. No neural-response-performance-driven graph selection or neural model fitting occurred in V6. Observation metadata was used to ask which cells had source records; that is not a response decoder or a training loss.

The behavior subset used successful trials following successful trials, reflecting the provisional previous-goal start inference; timeout trials were not in the primary contrast. Train/validation filtering preceded permitted record inspection in the reset pipeline. No shortest-path gap invention or unknown-as-absent conversion was accepted. Geometry, split, and mapping hashes were frozen and recorded for later reuse.

### What observed: measurement results, not neural performance

| Matched measurement | Accepted development result | Meaning |
| --- | ---: | --- |
| Eligible trials, train / validation | 15,947 / 3,215 | 19,162 behavioral trials |
| Trials mapped / eligible | 19,162 / 19,162 | Complete coverage under this operational mapping |
| Mapped coordinate samples | 4,461,200 | Dependent samples within paths, not trials |
| Whole-route signatures / middle components / motifs | 481 / 24 / 124 | Different behavioral summaries |
| Selected pair 4→3: present / absent, train | 393 / 153 | Behavior-level support |
| Same pair: present / absent, validation | 82 / 32 | Development behavior-level support |

The selected component is `D_N_R_T__N_R_M`, the right-hand upper-to-middle corridor direction, within pair `4->3`. These endpoint IDs are **provisional marker-derived labels**: start uses the previous successful goal, and the current minor marker is interpreted as cue/goal; authoritative protocol mapping remains unverified. Fixing this inferred pair controls operational endpoint identity, not a metadata gate that has already passed. Across pairs, an endpoint baseline must retain pair interactions; additive start and goal terms alone can miss them. We will call this **the selected component** below. It was selected for behavioral support, not because it decoded well.

**Before Figure 1, ask:** does the representation distinguish open regions from corridors rather than treating every floor-cell neighbor as a decision? The horizontal and vertical axes are Unity spatial coordinates; the region/corridor layout is a behavioral measurement overlay.

![V6 static region and corridor graph][fig1]

**Notice:** the graph compresses a two-dimensional floor into a manageable set of named regions and connections. **Do not infer:** these named nodes exist as discrete structures in the animal's brain, or that all motion inside a region is equivalent cognitively.

**Before Figure 2, ask:** do example continuous movements plausibly pass through the labeled geometry? Each subplot places a development path over spatial coordinates; train/validation examples are mapping checks, not neural predictions.

![V6 development path overlays][fig2]

**Notice:** the retained path makes the coarse interpretation inspectable. **Do not infer:** selected example overlays prove every path label correct, show intended routes, or supply an untouched-test evaluation. The full coverage statistic refers to the algorithm's rules, not perfect recovery of cognition.

### What this DOES / DOES NOT tell us

V6 established a reusable behavioral ruler and a within-endpoint route-component contrast. Fixing start and goal makes endpoint-only prediction constant within that contrast, a stronger question than merely decoding destination. But it predicts one binary component, not a complete path; it does not match gaze, heading, visual cue, action preparation, history, or every other nuisance variable.

There is **no neural training-loss curve for V6** because no learned brain model was trained. Its performance report is coverage, support, direction evidence, and provenance. Treating the absence of a loss trace as missing neural evidence would misunderstand the stage; inventing one would be worse.

### Audit finding / repair and why the next iteration followed

The initial independent V6 review blocked progression: one run had mapped paths but not completed support artifacts; graph edge hashes appeared inconsistent; required split-by-label panels were not explicit; weaker direction inference was not adequately separated; and focused graph/support tests were missing. Repairs required a completed rerun, explicit four-condition gates, synthetic tests, direction sensitivity, and hash-schema reconciliation.

The selected component's accepted middle traversals used adjacent-node evidence in 475 traversals, with zero dependence on the one-adjacent-node-only rule; strict support counts were unchanged. Legacy bare-integer and typed-node edge hashes were shown to serialize the same edge list differently, rather than silently equating matching counts with identical topology. The final V6 reviewer reported no findings and allowed exploratory neural work. But “many behavior trials” still did not answer “how many usable neural repeats?” That was the next gate.

## 3. V6 support refinement — a common label is not a common recording

### Question / what we knew entering

Could the behavior-defined contrast support a common neural panel for both labels in both splits? We knew that the selected component had hundreds of behavioral examples. We did not know whether those examples occurred in the same recording sessions as the cells needed for a dense comparison.

### Concept from first principles

Return to sessions A, B, and C. Suppose session C has many present trials but no validation absent trial. We cannot form a fully observed absent validation block containing c1 and c2. Borrowing a present block would change the target; inserting zeros would invent silence; borrowing training data would contaminate validation. The relevant support table is therefore session × endpoint pair × label × split, with cell membership and source identities attached.

A “common observed panel” requires cells available under all four conditions: train-present, train-absent, validation-present, validation-absent. Availability once is only the first gate. If a session has one absent validation source, every absent pseudo row uses that same block. The number of complete no-replacement rows is limited by the smallest required session/label pool, not by the total number of rows in the behavior table.

This explains three apparently contradictory counts: 19,162 development behavior trials, 50 cells with all-four-condition observation support, and a primary panel with only 22 validation source IDs can all be correct. They count different things. None licenses 19,162 independent usable neural examples for the chosen population contrast.

### Why this choice over alternatives

The primary threshold required at least three training sources per label and one validation source per label. It traded panel breadth against repetition, yielding a modest pilot rather than a pretend fixed-195 population. A 40-cell panel relaxed training support; a six-cell panel required more validation repeats but collapsed to one session. They were sensitivities, not candidates chosen by neural validation success.

Shared-component pooling across endpoint pairs was scientifically attractive: in the invented example, A→B and A→D might share \(e\). But label pooling helps only if the necessary recordings overlap. Matching marginal starts and marginal goals would also be insufficient; the **joint endpoint-pair mixture** must be controlled. Otherwise a classifier might exploit which start-goal combinations were included rather than reusable route structure.

### What changed and actual dataflow

Generated V6 membership/support artifacts were recounted under explicit repeat thresholds before neural fitting. The primary panel was frozen at 29 cells across seven sessions. Condition means were the first descriptive readout; balanced sampled pseudopopulations became a bounded comparison distribution for raw, PCA, and CEBRA representations. No all-195 blind imputation was adopted.

| Minimum train / validation per label | Cells / sessions | Complete no-replacement ceiling | Decision |
| --- | ---: | --- | --- |
| At least one in each of four conditions | 50 / 14 | Some pools have only one source | Common observation, not adequate repetition |
| 3 / 1 | 29 / 7 | Train 3 per label; validation 1 per label | Primary |
| 2 / 1 | 40 / 11 | Train present 3, absent 2; validation 1 per label | Relaxed sensitivity |
| 3 / 2 | 6 / 1 | Train 3 per label; validation present 2, absent 3 | Single-session sensitivity |
| 5 / 2 | 0 / 0 | Infeasible | Not fitted |

The primary selected-panel sources were train present/absent **52/30** and validation **10/12**, hence **82 train and 22 validation source IDs**. These are distinct source IDs, still nested in seven sessions and not evidence for independent animals or a simultaneous cross-session population.

### What observed: the support bottleneck

For the same component, alternative endpoint pairs had much weaker matched recording overlap. Pair `2->3` had train present/absent 25/495 and validation 9/107; `4->1` had 39/456 and 7/80; `6->3` had 16/493 and 3/112. Each listed alternative shared only one both-label validation session with the selected pair; the broader candidate situation was 0–1. Other-pair cell overlap was not established from selected-pair membership files. Cross-endpoint pooling was therefore **not adopted as the primary neural analysis**.

### What this DOES / DOES NOT tell us

The common component made behavior labels reusable. It did not manufacture common recordings or establish compositional H1b evidence. The primary panel made synthetic rows fully observed within the chosen assembly scheme. It did not turn 29 nonsimultaneous channels into a verified real population state.

The empirical product construction can still answer a modest question: are label-conditioned session-block distributions distinguishable under a fixed assembly and decoder? It cannot directly answer whether the population on a single future trial predicts that trial's path. Keeping this limitation explicit is more informative than simply calling the matrix “neural data.”

### Audit finding / repair and why the next iteration followed

Support review narrowed the meaning of the original 50-cell result and established the no-replacement ceiling before fitting. This prevented a misleading dense-looking 195-cell expansion. With a finite primary panel and transparent sensitivities, the next useful task was not another graph redesign: it was to preserve cue timing and verify that every stored count referred to the intended observation window.

## 4. V7 — preserve time without pretending to have learned dynamics

**Execution note:** V7 and V8 were implemented and run together in one predeclared baseline job. The separate chapters teach their different questions; they do not imply a new adaptive PCA selection after inspecting all raw-baseline results.

### Question / what we knew entering

Do total cue counts discard a potentially useful temporal arrangement, and can we construct ordered bins without mixing sources or exposure windows? Previous cue-related findings motivated keeping time resolution, not selecting a successful-looking interval in advance. The original V7 ambition included more sophisticated temporal modeling; the actual support audit justified a simpler first comparison.

### Concept from first principles

The invented count vectors had equal totals but different order. A sum is invariant to rearrangement, whereas concatenated bins preserve which cell fired in which interval. A linear classifier on binned features can assign different weights to an early and a late count from the same cell. It does **not** learn recurrence, latent-state transitions, or a continuous neural dynamical system. It is a time-indexed readout.

A simple illustrative model clarifies the bin-size tradeoff:

\[
N_b\sim\mathrm{Poisson}(\lambda_b\Delta_b),\qquad E[N_b]=\lambda_b\Delta_b.
\]

\(N_b\) is a bin's count, \(\lambda_b\) a rate in spikes per second, and \(\Delta_b\) observed duration in seconds. This is an explanatory counting model, **not a fitted or validated Poisson model of these recordings**. At a hypothetical rate of 10 spikes/s, 100 ms gives an expected count of one. Finer bins give more temporal detail but more sparse counts; coarser bins average over temporal differences. Observing a longer interval can increase count without any rate change. That is why exposure belongs in the audit.

### Why this choice over alternatives

The primary choice was ten 100 ms bins spanning the nominal first cue second. Fifty and 200 ms were limited sensitivities. This held the time horizon constant while varying granularity. A recurrent model, wider temporal receptive field, or broad window search would add complexity before the source pool could support it. The executed temporal comparison was total counts, flattened time-resolved counts, individual-bin diagnostics, and bin-width sensitivity—not a validated sequence-model study.

The target interval was explicitly the **nominal first second**, not each trial's variable full cue duration. Count-based decoders were retained; saved exposure does not mean every model was exposure-normalized. A rate-based or offset-model sensitivity remained a possible future check, not a reported successful analysis.

### What changed and actual dataflow

Previously imported cue-relative events and count metadata, guarded by permitted source IDs, were converted into counts and exposure arrays. The inclusion interval was

\[
0\le t<\min(D,1\ \mathrm{s}),
\]

where \(D\) is actual cue duration and \(t\) is time from cue onset. The convention is half-open: the start is included and the upper boundary excluded. Events at or beyond actual cue end are not cue inputs. A spike at 1 s in a longer cue falls outside the primary horizon and is counted as omitted, not silently reassigned to the last bin. Internal bins follow the implemented integer time/bin-width indexing; the intended intervals are [0,0.1), [0.1,0.2), and so on. The source code and conservation tests, not an assumption of infinite floating-point precision, define exact numerical handling.

For short cues, the final bin's exposure is the observed overlap, not an invented full 100 ms. For longer cues, the extra tail is not used. The conservation check compared full-window events with original counts over the *same full window*; it was separate from checking what the nominal one-second tensor included.

The source tensor was **104×29×10 masked storage**, not 104 simultaneous 29-cell trials. A source row contains its session's observed cells; other-session cells remain unavailable. Assembly chooses one same-label source per session, preserves all same-session cells and bins, and refuses missing-value imputation. Each split and seed then has **128×29×10 synthetic rows**, 64 per class. All derivatives of a source remain in its assigned split.

### What observed: matched timing and raw-count checks

| Audit or primary readout | Result | Reading |
| --- | --- | --- |
| Loaded source-cell cue duration, min / median / mean / max | 0.999034 / 1.01804 / 1.01863 / 1.05004 s | Not all windows exactly one second |
| Original full-window event/count mismatches | 0 | Matching-window conservation passed |
| Spikes outside nominal first second, within longer cue windows | 39 | Disclosed exclusion, not lost unnoticed |
| Constant balanced prediction, validation BA | 0.500 / 0.500 / 0.500 | Seeds 0 / 1 / 2 |
| Raw total counts, validation BA | 0.438 / 0.422 / 0.500 | Mean 0.453 |
| Raw ten-bin whole cue, validation BA | 0.445 / 0.477 / 0.500 | Mean 0.474 |

Duration summaries refer to loaded **source-cell windows**, not an independent sample of new trials. For the balanced synthetic validation rows, ordinary accuracy equals balanced accuracy (BA). BA averages correct-class rates for present and absent; always predicting one class gives 0.5. Within this fixed endpoint pair, endpoint-only identity supplies no varying feature. The selected training-source prior was 52/82 ≈ 0.634 present, but applying that constant probability to balanced synthetic validation still gives BA 0.5.

### What this DOES / DOES NOT tell us

Whole-cue time indexing did not produce robust validation improvement in this construction. This does not mean timing is biologically irrelevant. A linear binned readout may miss nonlinear relationships, and source support is weak. It does establish that merely retaining ten bins did not resolve the benchmark's instability.

The descriptive condition-mean check was also nonpositive. Think of subtracting the absent mean vector from the present mean vector separately in train and validation. If the same population contrast recurs, their directions should align. The observed cosine was **−0.099**, weakly negative and nearly orthogonal rather than a strong global inversion, and validation present-minus-absent margin along the training difference was **−18.785**. These are descriptive direction/alignment measures, not hundreds of independent validation observations: the two validation condition means are two summaries.

No-stitch session controls retained actual sources rather than cross-session rows, but primary-session validation counts were only 2–5 and BA ranged 0–1. The 19 saved low-N control rows did not provide stable population generalization. Fixed observed-panel assembly also prevents a varying missing-cell mask from directly serving as the class feature; it does not remove other session-specific response differences or certify absent confounds.

### Audit finding / repair and why the next iteration followed

V7's arrays passed source/mask and exposure checks, but the V7/V8 review later found missing training-fit metrics and an underreported perfect individual bin. Those became V8b repair requirements. An initial shell command had also failed because `tee` targeted a missing log directory; its artifacts were overwritten by the rerun, leaving a real provenance gap disclosed in the appendix.

At this point the scientifically useful next representation was PCA: a train-fitted linear compression that asks whether the noisy high-dimensional count vectors contain a more stable shared description, without building a new temporal model or retargeting the experiment.

## 5. V8 — what PCA compresses, and why explained variance is not the answer

### Question / what we knew entering

Could a small shared cell-space projection preserve useful structure better than raw counts? We already had a fixed panel, ordered bins, source-aware assembly, and raw baselines. PCA was not introduced because one validation seed looked good; dimensions three and eight were bounded comparisons selected before their results.

### Concept from first principles

Return to the invented cells. Suppose a1 and a2 tend to increase together across the observed vectors. Their joint movement can be summarized by a direction that averages them; their difference is a second direction. PCA finds orthogonal directions with maximal variance in the training data. It is like choosing a coordinate system aligned with the cloud's longest axes, not with the route label.

For a standardized cell vector \(\widetilde x\), the projection is

\[
z=W_d^\top(\widetilde x-\mu).
\]

\(\mu\) is the training PCA mean, the columns of \(W_d\) are \(d\) learned cell-space directions, and \(z\) gives coordinates along those directions. Training standardization puts cells on comparable scales; it is learned without looking at validation values. Covariance records which cell features vary together across the supplied observations. PCA summarizes that covariance.

The key word is **supplied**. Our covariance is calculated from label-conditioned pseudo rows, pooled across cue bins. It can reflect differences in condition means, time, source reuse, or independent session-block assembly. It is not verified simultaneous biological noise covariance—the trial-to-trial joint fluctuations one would measure from a real simultaneously recorded population. PCA is mathematically well-defined here; the biological interpretation of its covariance is restricted.

### Why this choice over alternatives

PCA is a useful baseline precisely because its objective is simple and not trained to separate the component label. If it provides a stable predictive compression, that is informative; if not, a nonlinear method must still beat it under the same conditions. But PCA's *input construction* remains label-conditioned. Calling its whole pipeline label-free would hide that dependency.

A high-variance direction could describe nonspecific firing-rate variation with no route relevance. A low-variance direction could carry route information. Therefore “eight components explain more variance than three” is not evidence that eight should decode better. Neither dimensionality reduction nor a prettier plot fixes sparse validation sources.

### What changed and actual dataflow

The exact shape transformation is central:

```text
training pseudo counts: 128 rows × 29 cells × 10 bins
transpose/stack bins: 1,280 cell vectors × 29 cells
fit per-cell scaler and PCA using these TRAINING vectors only
transform each split: 128 rows × 10 bins × d coordinates
flatten within row: 128 rows × (10d) decoder features
fit fixed C=1 logistic decoder on training; score validation
```

Thus **PCA-3 gives 30 whole-cue decoder features; PCA-8 gives 80**, not three or eight variables per whole trial. The same learned cell-space basis is reused at every bin. In the invented example, the a1/a2 combination is evaluated at each time point before those coordinates are concatenated. The 1,280 bin vectors are dependent derivatives of 128 synthetic rows, themselves assembled from 82 training source IDs. They are not 1,280 independent biological observations.

Raw total counts use 29 decoder features; raw ten-bin counts use 290. All compared representations share the same pseudo arrays for a given seed and use train-only downstream standardization and the fixed logistic comparator. The method comparison is therefore matched to the assembly, not to a new dataset for each method.

### What observed: compression did not stabilize the contrast

| Representation | Seed 0 BA | Seed 1 BA | Seed 2 BA | Mean BA |
| --- | ---: | ---: | ---: | ---: |
| Constant | 0.500 | 0.500 | 0.500 | 0.500 |
| Raw total | 0.438 | 0.422 | 0.500 | 0.453 |
| Raw ten-bin | 0.445 | 0.477 | 0.500 | 0.474 |
| PCA-3 | 0.789 | 0.516 | 0.258 | 0.521 |
| PCA-8 | 0.367 | 0.492 | 0.500 | 0.453 |

Seed 0 explained-variance sums were **0.212 for PCA-3** and **0.444 for PCA-8**. More retained variance did not yield better route-component validation. The PCA-3 range is particularly instructive: one assembly looks encouraging and another is below chance. Seeds change the pseudo assembly and model stochasticity where applicable; they are not isolated encoder-only replications, confidence intervals, or biological repeats.

**Before Figure 3, ask:** is an apparently favorable representation favorable across seeds? The x-axis lists representation/seed combinations; the y-axis is validation BA. The dashed 0.5 line is the constant balanced baseline.

![V7/V8 primary balanced accuracy by representation and seed][fig3]

**Notice:** PCA-3's one high bar coexists with a low bar, while raw whole-cue results cluster near or below the baseline. **Do not infer:** bars are independent experiments or error bars on a biological effect. They reuse a small source pool.

Bin-width sensitivities did not produce a stable rescue. With the primary panel, 50 ms raw-binned mean BA was 0.461 and PCA-8 0.219; 200 ms gave 0.531 and 0.422. The relaxed 40-cell/11-session 100 ms panel gave raw-total 0.510 and raw-binned 0.323. The strict six-cell/one-session panel gave raw-total 0.604, but that is not evidence of multi-session generalization. These are disclosed sensitivity comparisons, not a validation leaderboard from which a winner was chosen.

### What this DOES / DOES NOT tell us

This PCA setup did not establish reproducible low-dimensional prospective-path information. It also did not establish that such information is absent, or that every linear/nonlinear dimension-reduction method must fail. H1b is not synonymous with “PCA-3 works.” H1a remains a distinct information question, and neither is resolved biologically by this sparse synthetic benchmark.

Probability scores add another warning. Log loss penalizes confident errors strongly; Brier score is the mean squared error of predicted probabilities. These assess probability prediction, not standalone calibration tests. Raw-total seed 0 had validation BA **0.4375** and log loss **2.5237**, much worse than constant p=0.5 log loss **0.6931**. Later V8b training metrics showed BA **1.0** and log loss **0.0159** on train. That sharp train–validation mismatch is consistent with overfit/instability and confident errors; it is not proof of one specific cause.

### Audit finding / repair and why the next iteration followed

The independent review verified train-only PCA and saved transforms, but the original artifacts lacked training predictions/metrics needed to diagnose this mismatch. It also found bin 2 at BA 1.0 for all three seeds. Proceeding directly to a CEBRA success story or burying that bin would both be poor science. V8b was inserted to explain the surprising result and repair the evidence record, while leaving the whole cue and original C=1 comparator intact.

## 6. V8b — the perfect bin is a lesson in selection, not a discovery

### Question / what we knew entering

How can one 100 ms bin be perfect when whole-cue models are unstable, and does that result survive a null that reproduces the way it was noticed? The important result was **raw bin 2**, zero-based, corresponding to **0.2–0.3 s**. It was identified after examining development results. V8b used saved V7/V8 arrays only, not new raw or test access.

### Concept from first principles

Suppose our invented session C has only one validation source for each label. If those two blocks differ strongly in a particular bin, all resampled rows inherit that difference. Repeating the assembly with three seeds can preserve it because there are no alternative blocks to choose. A perfect pseudo-row score is then a statement about a tiny empirical pool, not the same evidential event as perfect prediction on many new real trials.

There is also a selection problem. If we inspect ten bins and report the best, the relevant null question is not merely “how often is bin 2 this good?” It is “how often would **some** inspected bin look this good under the same selection process?” This is the difference between a pointwise statistic and a max-over-family statistic.

### Why this choice over alternatives

The response was not to restrict V9 to bin 2, expand a window search, or select helpful cells. The bounded diagnosis kept the same primary arrays and evaluated source counts, classifier margins, session-cell-block ablations, regularization sensitivity, and matched source-label permutations. The aim was to challenge the interpretation, not optimize a new result on validation.

A null that shuffled individual pseudo rows or independent bins would break the wrong dependencies. It would pretend that repeated derivatives were independent. The adopted null works earlier in the causal dataflow: shuffle source labels, then rebuild everything affected by those labels.

### What changed and actual dataflow

Labels were permuted **within (session, split, endpoint pair)**, preserving class counts. A source trial's cells and bins stayed together under one shuffled label. The pipeline then reassembled synthetic rows and refitted normalization, PCA where applicable, and the decoder. V8b's statistics matched the observed mean across assembly seeds 0/1/2; for each permutation it also took the maximum of those mean BAs across all ten bins.

The assumption is conditional exchangeability: within a specified stratum, labels can be reassigned under the chosen null without destroying relevant nuisance structure that should be preserved. This is not a magic guarantee. Unmeasured within-session history or cue covariates may violate an ideal exchangeability argument, and tiny pools give broad, discrete null distributions. The resulting p-values are bounded development diagnostics, not probabilities that the null hypothesis is true.

For \(B\) permutations and \(k\) statistics at least as large as observed, the reported finite estimate is

\[
p=(1+k)/(B+1).
\]

The extra one includes the observed arrangement in the reference calculation and avoids a reported zero from a finite shuffle budget. With 100 shuffles the resolution is 1/101 ≈ 0.0099. The max-bin diagnostic corrects the specified ten-bin inspection, not every adaptive choice made throughout V6–V9.

### What observed: matched null and sensitivity results

| Statistic | Observed BA | Exceedances / 100 | Finite p | Interpretation |
| --- | ---: | ---: | ---: | --- |
| Bin 2, mean over three seeds | 1.000 | 9 | 0.0990 | Pointwise diagnostic |
| Maximum over ten bin means | 1.000 | 21 | 0.2178 | Accounts for the inspected bin family |
| Raw ten-bin whole cue | 0.474 | 57 | 0.5743 | Nonpositive matched whole-cue comparison |
| PCA-8 whole cue | 0.453 | 60 | 0.6040 | Nonpositive matched PCA comparison |

So the pointwise calculation is 10/101, and the family calculation is 22/101. A score of one is not automatically improbable in this construction: some shuffled source assignments also produce one.

Removing the **20180810_session01 cell block** reduced bin-2 mean BA to **0.732**, with seed values 0.500/1.000/0.695. Removing **20180912_session01** reduced it to **0.589**, with 0.625/0.648/0.492. Removing any of the other five session blocks left all three seeds perfect. These were feature-block ablations on the same source setting, not training on six sessions and generalizing to a wholly new seventh session.

The regularization check fixed the same arrays and reported all \(C=1,0.1,0.01\) results. In logistic regression smaller C means stronger regularization. Validation means for raw total were 0.453/0.448/0.391; raw binned 0.474/0.484/0.492; PCA-3 0.521/0.471/0.365; PCA-8 0.453/0.404/0.404. C=1 stayed the comparator. There was no validation-winner replacement. Saved train/validation metrics and predictions now made the high-training-fit/poor-validation pattern auditable.

### What this DOES / DOES NOT tell us

The perfect-bin calculation was real for the saved synthetic arrays. The corrected interpretation is neither “it never happened” nor “we found the planning time.” Its family-aware null was not supportive, and its sensitivity was localized to sparse recording blocks. Localization does not prove those sessions are artifacts, identify causal neurons, or show that their cells are biologically irrelevant. Removing features changes a decoder's input; it is not a neural intervention.

Likewise, BA below 0.5 does not license flipping labels after seeing validation. That would use the evaluation labels to repair the model. An inverted relation can be informative as a diagnostic of instability, but its direction must be established without such post-hoc correction if it is to become a predictor.

### Audit finding / repair and why the next iteration followed

The initial V8b/V9 review asked for missing margin/source-component evidence, session-block contributions, same-array baseline rows, and additional sampler/manifest tests. Final artifacts supplied **768 margin rows**, **42 ablation rows**, **36 comparator rows**, and the required checks. The regularization output comprised **252 metric rows** and **32,256 prediction rows**. The original V7 null table's lack of matched observed p-statistics was addressed by the matched V8b calculation rather than comparing an incompatible observed mean with an old single-seed null.

No invalid array or label bug required abandoning the benchmark. The appropriate next step was therefore the authorized bounded CEBRA comparison on the **whole ten-bin cue**, not the tempting selected bin.

## 7. V9 — what CEBRA learns when we tell it what belongs together

### Question / what we knew entering

Can a nonlinear learned cell-space representation improve this same whole-cue benchmark beyond raw/PCA, and do time-conditioned and behavior-conditioned objectives behave differently? We entered knowing the support limitation, the negative/unstable baselines, and the nonpositive perfect-bin diagnosis. This was the first actual native CEBRA benchmark here, not a confirmation stage or an exhaustive optimization exercise.

### Concept from first principles

Contrastive learning starts with relationships. An **anchor** is a training observation. A **positive** is another observation the sampler says should have a related representation. **Negatives** provide other observations against which that similarity is compared. An encoder maps a cell vector to a latent vector; cosine similarity measures alignment of latent directions. A temperature controls how sharply similarity differences affect the objective.

A schematic contrastive objective is

\[
\mathcal L\approx-s(z_a,z_+)/\tau+
\log\sum_{j\in\mathcal N}\exp(s(z_a,z_j)/\tau).
\]

Here \(z_a,z_+,z_j\) are anchor, positive, and comparison embeddings, \(s\) is cosine similarity, \(\tau\) is temperature, and \(\mathcal N\) represents sampled comparisons. This is an explanatory schematic, **not a claim that the native criterion has an explicit positive inside its denominator**. The accepted implementation uses native CEBRA's cosine contrastive criterion; conventions differ from the commonly written positive-plus-negatives InfoNCE formula. The intuition is to make chosen positives relatively similar, not to minimize route-decoder error directly.

In our invented example, a **Time positive** for one cell-population vector at bin 1 is the next bin in the same synthetic row. All session source components remain fixed across those two bins. A **Behavior positive** is sampled under the same component label, potentially from another synthetic row and another bin. The two choices encode different assumptions: neighboring times should relate, versus same future-component conditions should relate.

Neither choice discovers its own notion of relevance without assumptions. Behavior labels deliberately shape the training geometry. Time does not receive component labels as its encoder training context, but the underlying rows were assembled using them. It is therefore not a wholly label-free pipeline. If supervised labels make two groups separate in training, separation alone cannot be treated as independent discovery of a hippocampal route map.

### Why this choice over alternatives

Ten bins per cue create two distinct boundary hazards. A temporal sampler on globally concatenated observations might pair a final bin from one row with the first bin of another. Separately, a model with a multi-bin receptive field might read across that boundary even if its positive indices are safe. CEBRA masking augmentation does not solve either trial-identity problem by itself.

The accepted solution was a custom boundary-safe native sampler plus **offset1-model**, a **pointwise encoder receiving one 29-cell bin vector**. The temporal positive at +1 bin affects which vectors are compared during training; it does not give the encoder a temporal receptive field. This distinction matters: V9 is not a recurrent model, does not ingest a full cue sequence in one encoder call, and cannot establish learned simultaneous population dynamics.

Dimensions three/eight, hidden width 32, seeds 0/1/2, batch 256, temperature 1.0, learning rate 3e-4, and 1,000 steps formed a small declared budget. A training-loss-based extension had been contemplated, not a validation-success extension; no extension was used. We did not run a broad architecture search or choose a best seed. A negative finite pilot is a legitimate endpoint for this program.

### What changed and actual dataflow

Only saved accepted primary arrays were used. Training-only per-cell normalization preceded native CEBRA training on CUDA. Safe Time pairs stayed in one pseudo row with stable source-component identities; Behavior pairs shared the training component label. Negatives came from training data. The encoder transformed each of the ten bin vectors independently into d coordinates; the resulting **128×10×d** embeddings were flattened to **128×(10d)** and passed to the same fixed **C=1 logistic decoder**, with train-only downstream standardization.

The primary fit count was two variants × two dimensions × three seeds = **12 observed fits**. Full-pipeline source-label nulls were restricted in advance to dimension eight, seed zero: **20 Time and 20 Behavior**, each rebuilding assembly and refitting normalization, encoder, and decoder for the same 1,000 steps. Freezing a behavior-supervised encoder while shuffling only decoder labels would not test the full label-dependent pipeline; that was not the accepted procedure.

Actual training used **CEBRA 0.6.1**, **torch 2.12.0+cu130**, and an **NVIDIA GeForce RTX 2070**. Geometry, raw decoders, and PCA used CPU; they were not relabeled GPU work. The final accepted run contained **52 fits and 52,000 optimizer steps**. Checkpoints, loss traces, predictions, and reload parity were saved.

### What observed: same-array validation remained nonpositive

| Whole-cue representation | BA seeds 0 / 1 / 2 | Mean BA |
| --- | --- | ---: |
| Constant p=0.5 | 0.500 / 0.500 / 0.500 | 0.5000 |
| Raw ten-bin | 0.445 / 0.477 / 0.500 | 0.4740 |
| PCA-8 | 0.367 / 0.492 / 0.500 | 0.4531 |
| CEBRA-Time-3 | 0.430 / 0.500 / 0.000 | 0.3099 |
| CEBRA-Time-8 | 0.406 / 0.484 / 0.438 | 0.4427 |
| CEBRA-Behavior-3 | 0.602 / 0.000 / 0.281 | 0.2943 |
| CEBRA-Behavior-8 | 0.500 / 0.422 / 0.320 | 0.4141 |

**Before Figure 4, ask:** does CEBRA provide a consistent improvement when judged by the same downstream task, rather than its own training objective? The x-axis lists representations and the y-axis is validation BA; bar heights show seed means and whiskers show the three-seed ranges, not confidence intervals.

![Same-array validation balanced accuracy and seed ranges][fig4]

**Notice:** no CEBRA configuration provides a stable above-baseline whole-cue result. **Do not infer:** a ranking of these means establishes universal superiority or failure of a representation method. The comparison is bounded by the same tiny synthetic validation source pool.

For dimension-eight seed-zero nulls, Time observed BA was **0.40625**, null median **0.51171875**, and p **0.8571428571** (17 exceedances). Behavior observed BA was **0.5**, null median **0.5**, and p **0.6190476190** (12 exceedances). Each had twenty nulls, so resolution was **1/21 ≈ 0.047619**. Neither was promising; these coarse development p-values are not posterior probabilities or untouched-test evidence.

**Before Figure 5, ask:** did optimization make progress even though task prediction did not? The x-axis is optimizer step and the y-axis is native contrastive training loss; curves identify observed variant/dimension/seed fits.

![Observed native CEBRA training losses][fig5]

**Notice:** losses decrease from roughly 5.54 toward approximately 4.9–5.1. The model optimized the relationship objective. **Do not infer:** a lower Time loss than Behavior loss means better route prediction. The samplers define different learning tasks, and their raw loss levels are not an apples-to-apples behavioral score. Within-fit loss reduction is also not evidence of generalization; the held-out decoder and nulls address that separate question.

### What this DOES / DOES NOT tell us

This bounded CEBRA implementation did not improve the benchmark into robust evidence for future-component information. It does not show that CEBRA generally fails, that a better-supported population could not work, or that the hippocampus lacks prospective information. The task and sampling objectives may be poorly matched to what matters; the data may not support stable learning; the relevant signal may be missing. Those alternatives remain open.

One secondary metric deserves explicit teaching: Time-3 seed one had **BA 0.5 but AUROC 0.946289**, with predicted-positive rate **0.0**. AUROC measures ranking across possible thresholds; BA here uses the fitted decision rule's fixed threshold. This model ranked the validation positives relatively highly while still classifying every row as negative. Thus poor BA does not mean literally zero information in every score. But Time-3 seeds zero/two had AUROC **0.022217/0.0**: the favorable ranking was not robust across seeds and was not established by the predeclared BA null. We did not retune the threshold using validation or turn an isolated secondary score into the primary result.

The two BA=0 fits—Time dimension three seed two and Behavior dimension three seed one—were independently audited. Saved train/validation labels matched source pseudo arrays; predictions were inverted on validation while training BA was one. The artifacts did not support a label-swap or reshape explanation. They support reporting an extreme train–validation inversion, not secretly flipping outputs using validation labels or inventing an identified biological cause.

### Audit finding / repair and why the program stopped here

A slow partial run exposed an implementation bottleneck in trial-index expansion. Direct pointwise indexing made the same computation faster: the old/new Time-3 seed-zero comparison matched **all 1,000 loss steps exactly** and had validation embedding maximum absolute difference **0.0**, while wall time fell **102.01→7.08 s**, a **14.4× engineering speedup**. A separate approximately 30× profiler microbenchmark included different overhead; it is not the real-fit speedup and certainly not neural improvement.

The initial review also required the V8b contribution/comparator evidence and missing sampler/manifest tests discussed above. The final scientific review reported **no findings**, verified 12 observed plus 40 null fits, 1,000 loss rows each, actual CUDA allocation, and **0.0 checkpoint reload embedding differences**. Final accepted runtime was **363.999 s**, about 364 seconds for those 52 fits only—not the total workflow, prior attempts, or total GPU expenditure.

The program stopped because the authorized finite comparison and its repairs were complete, not because significance had finally been reached. No raw/test access, fits, installs, or analysis-code changes were performed for the present teaching rewrite. The rewrite was subsequently reviewed separately for pedagogy and factual accuracy (Appendix E).

## 8. Synthesis — three different kinds of finding

### Behavioral measurement improved

We moved from fragmented fine-grid signatures toward an explicit region/corridor/direction ruler, retained continuous paths, and identified a component that varies within one endpoint pair. That is meaningful progress: it makes “future path beyond start and goal” into an auditable restricted target. It does not show that this graph is the brain's representation, nor that every possible behavioral distinction is captured.

The most consequential support result was not the large behavior count. It was the collapse from a 195-cell union to a 29-cell/seven-session primary panel with only 22 validation source IDs and one complete no-replacement validation row per label. This changes which scientific questions the dataset can answer. The common component helps reuse labels across conditions, but the missing common recordings block a strong cross-endpoint composition test.

### The constructed sample distributions did not yield stable whole-cue evidence

Raw total counts, raw binned counts, PCA, and the bounded CEBRA variants did not produce a reproducible above-baseline whole-cue result under this condition-level assembly. One PCA seed and one time bin looked favorable; neither justified promotion after the relevant sensitivity/null checks. Proper probability scores and training comparisons exposed confident errors and instability rather than an overlooked stable success.

This is evidence about a particular constructed distribution, selected panel, target, timing choice, and finite model budget. It is not an estimate of how accurately an operational decoder would predict the unknown path of a new real trial. The synthetic label-conditioned assembly explicitly separates this benchmark from that stronger experiment.

### Evidence for a biological mechanism remains missing

The report does not establish H1a or H1b. **Not established is not false.** Decoding alone would not prove intention or causal planning even with a positive result; the present nonsimultaneous, selected-cell, development-only evidence is further from that claim. A negative embedding is not a negative assay of every possible hippocampal code.

Consider counterfactuals rather than only labels such as “success” or “failure.” If a stable cue response merely encoded a visual instruction correlated with route, stronger decoding could appear without incremental route planning. If a few repeated source blocks dominated a bin, the pseudo-row score could remain perfect across seeds without robust new-trial performance. If genuine population information were carried in simultaneously observed relationships destroyed by cross-session assembly, the current benchmark could be negative even though a real population decoder would succeed. If endpoint-fixed route variants were themselves poorly controlled for history or gaze, a positive association could remain ambiguous. Current results do not uniquely choose among all these possibilities.

### What observation would change the interpretation?

A more persuasive H1a result would use verified simultaneous cue activity linked to each real trial's later path; demonstrate incremental prediction over start/goal and relevant nuisance baselines; remain stable across enough genuinely independent held-out source trials or sessions; and exceed a justified conditional null under choices frozen before confirmation. A score on genuinely unexposed recordings would change the evidential status in a way that another seed on these arrays cannot.

For H1b, useful evidence would be reproducible organization of the relevant information across dimensions, sessions, and defensible representations—not a single nice supervised plot. Target-free comparisons and shared-component contrasts across endpoint pairs could help, but only if joint endpoint mixtures and common recording support make the comparison identifiable. Stable geometry of real simultaneously observed activity would answer a different and stronger question than covariance of the empirical product assembly.

Before architecture escalation, obtain or verify: simultaneous recording-group membership; cell-selection and sorting provenance; authoritative cue/start/goal marker meanings; clock alignment and cue/navigation events; trial identities/history and subject/session metadata; sufficient within-endpoint route repeats; and available gaze, view, heading, speed, action, and success-selection controls. A new split of inspected data cannot substitute for genuinely unexposed confirmation material.

The next practical model should be the simplest source-aware or within-session baseline that those data support. Only then would a richer temporal encoder, exposure-model sensitivity, cross-endpoint contrast, or expanded CEBRA budget answer a clearer question. The lazier alternative to a bigger architecture here is also the more scientific one: improve source support and metadata first, rather than give the same uncertain observations more parameters.

The overall finding is therefore neither “we decoded planning” nor “there is no planning signal.” **We built a better behavioral measurement and a source-accounted exploratory benchmark, learned that the available condition-level evidence is unstable/nonpositive, and identified what a stronger biological test genuinely requires.**

---

# Audit appendices

The main narrative explains the decisions. The appendices below preserve exact results, training evidence, run history, and review access without requiring filenames at every teaching step. Links resolve from this report's location in `docs/reports`. Large source/prediction tables remain in accepted artifacts; they are not new analyses. The archived pre-rewrite report is a byte-preserved historical snapshot whose old relative links are not promised to be portable from its archive directory.

## Appendix A. Complete primary numerical comparison

All three seeds use matched primary arrays. Accuracy equals BA because each synthetic split is balanced. Ranges are seed sensitivities, not confidence intervals; probability scores and AUROC supplement rather than replace the declared primary BA comparison.

| Representation | BA values | BA mean | BA range | Accuracy mean/range | Log loss mean/range | Brier mean/range | AUROC mean/range |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Constant p=0.5 | 0.500000 / 0.500000 / 0.500000 | 0.500000 | 0.500000–0.500000 | 0.500000 (0.500000–0.500000) | 0.693147 (0.693147–0.693147) | 0.250000 (0.250000–0.250000) | 0.500000 (0.500000–0.500000) |
| Train-source prior | 0.500000 / 0.500000 / 0.500000 | 0.500000 | 0.500000–0.500000 | 0.500000 (0.500000–0.500000) | 0.730499 (0.730499–0.730499) | 0.267995 (0.267995–0.267995) | 0.500000 (0.500000–0.500000) |
| Raw total | 0.437500 / 0.421875 / 0.500000 | 0.453125 | 0.421875–0.500000 | 0.453125 (0.421875–0.500000) | 2.334245 (1.581000–2.898077) | 0.506297 (0.432704–0.557233) | 0.298503 (0.223633–0.413818) |
| Raw 10-bin | 0.445312 / 0.476562 / 0.500000 | 0.473958 | 0.445312–0.500000 | 0.473958 (0.445312–0.500000) | 0.960772 (0.835937–1.091908) | 0.353050 (0.315335–0.389428) | 0.629476 (0.495117–0.781006) |
| PCA-3 | 0.789062 / 0.515625 / 0.257812 | 0.520833 | 0.257812–0.789062 | 0.520833 (0.257812–0.789062) | 1.328667 (0.373449–2.595502) | 0.357970 (0.118885–0.613305) | 0.478597 (0.000000–0.936279) |
| PCA-8 | 0.367188 / 0.492188 / 0.500000 | 0.453125 | 0.367188–0.500000 | 0.453125 (0.367188–0.500000) | 1.974602 (1.174905–3.212605) | 0.470498 (0.386773–0.551790) | 0.132487 (0.000000–0.284180) |
| CEBRA-Time-3 | 0.429688 / 0.500000 / 0.000000 | 0.309896 | 0.000000–0.500000 | 0.309896 (0.000000–0.500000) | 2.414546 (1.050091–3.546035) | 0.591495 (0.365582–0.872590) | 0.322835 (0.000000–0.946289) |
| CEBRA-Time-8 | 0.406250 / 0.484375 / 0.437500 | 0.442708 | 0.406250–0.484375 | 0.442708 (0.406250–0.484375) | 1.898843 (0.824563–2.966580) | 0.454036 (0.296908–0.561718) | 0.304118 (0.017090–0.719727) |
| CEBRA-Behavior-3 | 0.601562 / 0.000000 / 0.281250 | 0.294271 | 0.000000–0.601562 | 0.294271 (0.000000–0.601562) | 1.488746 (1.011290–2.271045) | 0.465574 (0.363146–0.654387) | 0.237549 (0.000000–0.382080) |
| CEBRA-Behavior-8 | 0.500000 / 0.421875 / 0.320312 | 0.414062 | 0.320312–0.500000 | 0.414062 (0.320312–0.500000) | 1.734319 (1.082172–2.513742) | 0.459918 (0.405982–0.546293) | 0.254476 (0.050781–0.394775) |

For complete machine-readable precision and per-seed train/validation metrics, use [same-array summary CSV](../../outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/v8b-v9-cebra-final-20260905T224554Z/report_assets/final_same_array_validation_summary.csv), [all comparator rows](../../outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/v8b-v9-cebra-final-20260905T224554Z/v8b/v8b_v9_same_array_comparator_baselines.csv), and [CEBRA metrics](../../outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/v8b-v9-cebra-final-20260905T224554Z/v9/v9_cebra_metrics.csv). The full original sensitivity grid is [V7/V8 metrics](../../outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/v7-v8-neural-experiments/metrics.csv) (495 rows); [V8b regularization metrics](../../outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/v8b-v9-cebra-final-20260905T224554Z/v8b/v8b_regularization_metrics.csv) supplies both train and validation. These linked tables are the complete numerical record, not selected successful runs.

## Appendix B. Training, device, and loss evidence

V6 ran on CPU in 4m33s and had no neural training objective. V7/V8 CPU runtime was 44.210 s; the original run saved validation metrics rather than full decoder training-loss traces. V8b repaired training-score/prediction evidence on saved arrays, not a retrospectively recovered optimizer trace. PCA has an explained-variance objective rather than a neural-network loss curve. CEBRA below used actual CUDA training. Peak memory is torch allocated/reserved bytes, not total board usage; reload parity is maximum absolute embedding difference.

| Variant | Dim | Seed | Wall s | Loss first→last | Prev100 mean | Last100 mean | Peak alloc | Peak reserved | Save-load parity |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Behavior | 3 | 0 | 6.225 | 5.544871→5.085263 | 5.079721 | 5.075853 | 18,668,032 | 23,068,672 | 0.0 |
| Behavior | 3 | 1 | 6.538 | 5.545621→5.042245 | 5.056499 | 5.057948 | 18,668,032 | 23,068,672 | 0.0 |
| Behavior | 3 | 2 | 6.991 | 5.545464→5.072145 | 5.089003 | 5.083957 | 18,668,032 | 23,068,672 | 0.0 |
| Behavior | 8 | 0 | 6.206 | 5.544046→5.050716 | 5.061741 | 5.059491 | 18,698,752 | 23,068,672 | 0.0 |
| Behavior | 8 | 1 | 5.838 | 5.544506→5.050831 | 5.086046 | 5.079524 | 18,698,752 | 23,068,672 | 0.0 |
| Behavior | 8 | 2 | 6.859 | 5.545794→5.057981 | 5.086774 | 5.084569 | 18,698,752 | 23,068,672 | 0.0 |
| Time | 3 | 0 | 7.084 | 5.544830→4.934290 | 4.980703 | 4.969800 | 18,656,768 | 23,068,672 | 0.0 |
| Time | 3 | 1 | 6.135 | 5.545476→4.933596 | 4.982585 | 4.964663 | 18,656,768 | 23,068,672 | 0.0 |
| Time | 3 | 2 | 5.936 | 5.543832→4.923173 | 4.932457 | 4.912819 | 18,656,768 | 23,068,672 | 0.0 |
| Time | 8 | 0 | 6.638 | 5.543346→4.902602 | 4.942385 | 4.926632 | 18,687,488 | 23,068,672 | 0.0 |
| Time | 8 | 1 | 6.069 | 5.542702→4.936636 | 4.983963 | 4.967864 | 18,687,488 | 23,068,672 | 0.0 |
| Time | 8 | 2 | 6.474 | 5.543330→4.925395 | 4.945939 | 4.927517 | 18,687,488 | 23,068,672 | 0.0 |

All 52 accepted fits have 1,000 loss rows. [Observed-fit metadata index](../../outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/v8b-v9-cebra-final-20260905T224554Z/v9/v9_fit_infos.json) contains the 12 observed fits; the [null fit directories](../../outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/v8b-v9-cebra-final-20260905T224554Z/v9/nulls) retain the other 40 per-fit records; [observed fit directories](../../outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/v8b-v9-cebra-final-20260905T224554Z/v9/observed) and [V9 directory](../../outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/v8b-v9-cebra-final-20260905T224554Z/v9) retain native loss traces, checkpoints, and embeddings. An example is [Time-3 seed-zero loss trace](../../outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/v8b-v9-cebra-final-20260905T224554Z/v9/observed/cebra_time/dim3/seed0/loss_trace.csv). [Old/new parity comparison](../../outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/v8b-v9-cebra-final-20260905T224554Z/speedfix_old_new_comparison.json) isolates the 14.4× runtime repair from any neural-performance claim.

## Appendix C. Commands, inputs, environment, and hashes

The following recipes reproduce historical stage settings; they were **not executed for this rewrite**. Run from the repository root only with appropriate renewed data authorization. Replace each `NEW-TIMESTAMPED-*` output placeholder with a fresh, nonexistent path before running; never substitute an accepted artifact directory. Each recipe uses the accepted upstream inputs. To chain newly reproduced stages instead, also update the downstream input directories. V8b/V9 can consume saved arrays, whereas V6/V7 input access must retain the development split guard.

### V6

```sh
/home/hongyi-home-lab/neuro_science/scratch/v6-v9-runtime/bin/python \
  -m scripts.place195_v6_graph_support_audit run \
  --import-dir outputs/prospective_path_first_run/place195-all-sessions-20260830-v4 \
  --split-dir outputs/prospective_path_first_run/place195-splits-20260830-v3 \
  --geometry docs/geometry/maze_mesh_centroids_1344.txt \
  --output-dir outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/NEW-TIMESTAMPED-V6-RUN
```

### V7/V8

```sh
scratch/v6-v9-runtime/bin/python \
  -m scripts.place195_v7_v8_neural_experiments run \
  --import-dir outputs/prospective_path_first_run/place195-all-sessions-20260830-v4 \
  --split-dir outputs/prospective_path_first_run/place195-splits-20260830-v3 \
  --v6-dir outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/v6-reset-graph-support-audit \
  --output-dir outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/NEW-TIMESTAMPED-V7-V8-RUN \
  --rows-per-class 64 \
  --seeds 0 1 2 \
  --bin-widths 0.1 0.05 0.2 \
  --nulls 100
```

### V8b/V9 (interpreter made explicit)

```sh
scratch/v6-v9-runtime/bin/python -m scripts.place195_v8b_v9_cebra run \
  --v7v8-dir outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/v7-v8-neural-experiments \
  --output-dir outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/NEW-TIMESTAMPED-REPRO-RUN \
  --rows-per-class 64 --v8b-nulls 100 --v9-nulls 20 \
  --iterations 1000 --batch-size 256 --hidden 32 \
  --old-partial-dir outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/v8b-v9-cebra-20260905T215914Z
```

The historical accepted output directory was `v8b-v9-cebra-final-20260905T224554Z`; `NEW-TIMESTAMPED-REPRO-RUN` is a safety placeholder, not another completed run. The historical `summary.json` records Python's script argv without an interpreter; the recipe above supplies the actual runtime explicitly.

### Identity ledger

Hashes identify bytes and schemas, not biological validity. Recorded input hashes below are read from accepted manifests; this rewrite did not reopen their underlying raw/import tables.

| Object | Recorded SHA-256 / revision |
| --- | --- |
| Git HEAD (dirty run) | `c4eec752a0eab95e5c48300bc327191aefa57778` |
| Immutable split semantic hash | `11237c8c35af4b09b6d81c1994ff3f8b702d245d3a262f70413dab2b182973d1` |
| V6 static graph | `301519ec5fc45cea6aa663eb3c9d9d7cbf2d84af264ff5998f89de3e741ea496` |
| Fine documented primary | `1e7804c5d2167dcd8709a9760d8917034cb60e36e936229fad9056b1dae0f9ad` |
| Fine legacy bare-integer edges | `ab31ee91f615bd4165282e8dd9ab2c4298a4f5285cb76fd3c4aeea38096a4ebb` |
| Fine typed MazeGraph edges | `46f113070ca5f3b94c06c0b2943ef9d011b8dd432d8d6956481f8b6de36ccda3` |
| Input cue_counts.csv.gz | `e355af169b661650c4cc02aeaafd96a1443698afa67648a8b888a3adeee4c7b0` |
| Input cue_spike_events.csv.gz | `76cd94486604fdbc3746de9eba4835bb8e2a035eb4071531f59ee498f279ab24` |
| Input geometry | `479f0df501e92e167206248eff2d0a44ba5f26cd62cfcc879dcaad979d7a7e66` |
| Input path_samples.csv.gz | `a8c689fefedf4fab9fed2ac75fe021dc1a05307ea7d94c4061e3e35a133f316f` |
| Input source_trial_splits.csv | `b0ef8cce43c79d9e2b1ae0a804c7d48fefeb92469670f3031485d0009fb10ff3` |
| Input trials.csv | `aa0dc3e402a8a3c3c0fa355c0342f5061314f2c571d2f96dfaecc94e69fcd223` |
| V7/V8 script | `39ed10704d7b3258a4d7109c9c4ce7ddecc5de98d4c11efe66f019d3cb973089` |
| V6 source membership | `888a0b71aa51fe20a9cd4b0275e008c7fc4dcd7ef9dace6aba30a815b57b5cea` |
| V6 condition-mean membership | `52b3eb13fb7b849b6befb326c106e80924021dcec910cf5c8883139907e0f6fa` |
| V9 script | `737ad148dcc261c3ec1bbbd1ada395b34b47b2b37c5920370d3107c209976f9a` |
| V9 source tensor NPZ | `688e3b52f69a872c7aec420da99ebb6f0b80464351ded3813b077cd7ed3cf567` |

Exact V6 code/input hash receipts and post-log artifact identities are in [hash log](../../outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/v6-reset-graph-support-audit/logs/hash_inputs_code.log) and [post-run provenance](../../outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/v6-reset-graph-support-audit/review_validation_provenance.json). Graph serialization differences, including the separate V5-style primary contract, are documented in [hash reconciliation](../../outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/v6-reset-graph-support-audit/v6a_geometry_mapping/static_hash_reconciliation.md). Do not compare unlike hash contracts as if they were the same object.

The run used Python 3.13.2, runtime NumPy 2.3.4, scikit-learn 1.7.2, CEBRA 0.6.1, torch 2.12.0+cu130, and RTX 2070 hardware. Driver 580.173.02 advertised CUDA 13.0 support; that is distinct from the installed torch build tag. Initial project-venv package availability was not the final fitting environment. [Runtime validation](../../outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/environment/runtime.json), [complete package freeze](../../outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/environment/pip-freeze.txt), [GPU receipt](../../outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/environment/nvidia-smi.txt), [original environment setup log](../../outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/environment/env-a-install.log), and [environment check log](../../outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/environment/env-b-validation.log) retain the exact evidence. No installs were performed for the rewrite.

The working tree was dirty at the recorded revision; manifests retain status snapshots. The pre-existing baseline edit was preserved, no commits were requested or made, and a Git revision alone is not a clean-code reproduction guarantee. Use stage code hashes and dirty-state receipts as well. Where a separate complete historical dirty-diff snapshot/hash was not retained, this report does not invent one. The current [report manifest](../../outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/final_report_manifest.json) identifies this reviewed teaching rewrite. The [prior report manifest](../../outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/audits/report-before-teaching-rewrite-manifest.json) is archived separately, so approval and byte identity of the old report are not silently transferred to new prose.

## Appendix D. Every known failed, superseded, interrupted, and accepted run

| Iteration/run | Status | Path / log | What happened |
| --- | --- | --- | --- |
| Initial V6 reconnaissance | rejected / contaminated | `../../scratch/v6-v9-planning/holdout-exposure-audit.md`; copied audit `../../outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/audits/holdout-exposure-audit.md` | Unfiltered all-session endpoint aggregate likely included locked test rows. No accepted artifacts; fresh derivation required, but prior exposure could not be undone. |
| V6 failed slow support | failed/preserved | `../../outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/v6-reset-graph-support-audit-failed-slow-support-20260905T2037Z/` | Earlier V6 attempt preserved, not accepted. |
| V6 edge-hash note | superseded/preserved | `../../outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/v6-reset-graph-support-audit-superseded-edgehash-note-20260905T2048Z/` | Superseded by fuller review-fix/final runs. |
| V6 review fixes | superseded/preserved | `../../outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/v6-reset-graph-support-audit-superseded-review-fixes-20260905T2058Z/` | Intermediate accepted-code direction but not final artifact. |
| V6 interrupted review rerun | interrupted/preserved | `../../outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/v6-reset-graph-support-audit-interrupted-review-rerun-20260905T2058Z/` | Preserved incomplete rerun. |
| V6 final behavior/support audit | accepted | `../../outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/v6-reset-graph-support-audit/` | Split-filtered graph/support audit; final V6 independent review had no findings. |
| V7 first `tee` command | failed shell / overwritten artifacts | history note in `../../outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/v8b-v9-cebra-final-20260905T224554Z/V8B-V9-HANDOFF.md` | Started 2026-09-05T21:30:43Z, exited 1 because log directory was missing. Artifacts were overwritten by final rerun; exact first-run artifact hashes unavailable. |
| V7/V8 final neural baseline run | accepted after review fixes | `../../outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/v7-v8-neural-experiments/` | CPU cue-binning/raw/PCA baselines and source-label nulls. Review found issues requiring V8b diagnostics before interpretation. |
| V8b/V9 no-clobber/log-dir attempt | failed/preserved | `../../outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/v8b-v9-cebra-20260905T215838Z/` | Failed setup attempt, preserved. |
| V8b/V9 slow partial | stopped/preserved | `../../outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/v8b-v9-cebra-20260905T215914Z/` | Slow partial run killed after runtime diagnosis; used for old/new speed comparison. |
| V8b/V9 speedfix run | superseded/preserved | `../../outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/v8b-v9-cebra-fast-20260905T223541Z/` | Completed speed-fixed run later superseded by final test/assert cleanup. |
| V8b/V9 final CEBRA run | accepted | `../../outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/v8b-v9-cebra-final-20260905T224554Z/` | Final 52 fits, complete artifacts, independent V9 review approved with no findings. |

### Evidence gaps and interpretation limits of the ledger

The initial V6 probe exposed endpoint aggregates before a hard split gate; discarding its artifacts/design direction did not undo possible human/agent exposure. Reset continuation is not pristine confirmation. The first V7 `tee` attempt began 2026-09-05T21:30:43Z and exited 1 because its log directory was absent. Its outputs were overwritten by the rerun, so exact first-run artifact hashes/timing cannot be reconstructed. [V8b/V9 history handoff](../../outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/v8b-v9-cebra-final-20260905T224554Z/V8B-V9-HANDOFF.md) records the recovery and overwrite disclosure; it is not restored first-run evidence.

Environment setup also had a failed validation step: env-a installed CEBRA but its runtime import check exposed missing h5py; env-b supplied the working isolated runtime documented above. This was an environment repair, not a model result or an install performed during this rewrite.

The failed setup attempt, slow partial CEBRA run, completed-but-superseded speedfix run, and final accepted run must not be pooled as one inference. A reviewer's system-Python CEBRA import failed because that interpreter lacked CEBRA; the research runtime import succeeded. That environment diagnostic is separate from a failed model fit. The final 363.999 s is not total project elapsed time. No reliable total GPU-cost figure is supplied.

## Appendix E. Independent reviews and verification scope

These are **unaltered exact review artifacts**, not paraphrases substituted for the reviewers. Their dates/stages and old-report scope matter.

- [holdout-exposure-audit.md](../../outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/audits/holdout-exposure-audit.md): Exposure incident: critical/major findings; mandatory reset and development-only ceiling.
- [v6-initial-review.md](../../outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/audits/v6-initial-review.md): Initial V6: block progression pending completeness, hashes, support/direction gates and tests.
- [v6-final-independent-review.md](../../outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/audits/v6-final-independent-review.md): Final V6: no findings; approved exploratory progression.
- [v6-panel-feasibility.md](../../outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/audits/v6-panel-feasibility.md): Support refinement: repeat ceilings and cross-endpoint limitations.
- [v6-hash-provenance.md](../../outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/audits/v6-hash-provenance.md): Hash contract/provenance audit.
- [v7-v8-independent-review.md](../../outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/audits/v7-v8-independent-review.md): V7/V8: fitting allowed, diagnostics required before interpretation.
- [v8b-v9-initial-review.md](../../outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/audits/v8b-v9-initial-review.md): Initial V8b/V9: contribution/comparator/test findings; active incomplete run.
- [v8b-v9-final-review.md](../../outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/audits/v8b-v9-final-review.md): Final V8b/V9: no findings; approved nonpositive exploratory reporting.
- [v9-runtime-diagnosis.md](../../outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/audits/v9-runtime-diagnosis.md): Runtime bottleneck and parity scope.
- [final-report-independent-review.md](../../outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/audits/final-report-independent-review.md): Old report accuracy/claim audit: no findings; DOES NOT approve this rewrite.

Separate reviews for this teaching rewrite:

- [Pedagogical prereview of the old report](../../outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/audits/teaching-prereview.md): identified results before foundations, uneven iteration reasoning, and disconnected dataflow. Numerical accuracy alone had not satisfied the teaching goal.
- [New main-narrative pedagogy review](../../outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/audits/teaching-rewrite-pedagogy-review.md): passed; checked whether the explanations answer eight concrete learner questions, not merely whether terms and numbers appear.
- [Initial rewrite factual review](../../outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/audits/teaching-rewrite-factual-review-initial.md): found two reproduction recipes still pointing to accepted output directories. Both now require fresh output placeholders.
- [Final factual follow-up](../../outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/audits/teaching-rewrite-factual-review-final.md): finding closed; release approved under the prior factual review plus inspected correction scope. This was not an independent refit.

Historical parent verification: [26 focused tests and compile log](../../outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/audits/final-focused-tests.log) reports 26 tests passed in 2.03 s and eight source/test files compiled. [parent artifact assertions](../../outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/audits/parent-final-artifact-checks.json) verified fit counts, 52,000 steps, parity zero, matching code hash, `original_test_pristine=false`, and `original_test_evaluated_by_final_v9=false`. Earlier [V6 test log](../../outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/audits/parent-v6-tests.log) records its stage gate. Parent LSP checks returned zero errors for completed files but three of eight timed out; full LSP confirmation was not obtained. These are prior checks, not rerun fits or fresh software validation by the rewrite writer.

The writer's [53 saved document checks](../../outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/audits/teaching-rewrite-checks.json) verified links/figures, numerical transcriptions, and provenance at the initial rewrite hash. [Parent final checks](../../outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/audits/teaching-rewrite-parent-final-checks.json) cover the reviewed command corrections and review-status closure, including unchanged numerical tables. Neither independently reanalyzes recordings. The [pre-rewrite archive](../../outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/audits/report-before-teaching-rewrite.md) preserves the prior report exactly; only the live report's links are promised relative to `docs/reports`. Pedagogical and factual reviews are complete with the scopes stated above.

## Appendix F. Complete artifact access and glossary

### V6 behavior and support

- [summary.json](../../outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/v6-reset-graph-support-audit/summary.json)
- [v6_teaching_audit.md](../../outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/v6-reset-graph-support-audit/v6_teaching_audit.md)
- [v6a_geometry_mapping/preread_frozen_graph_config.md](../../outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/v6-reset-graph-support-audit/v6a_geometry_mapping/preread_frozen_graph_config.md)
- [v6a_geometry_mapping/trial_mapping_metrics.csv](../../outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/v6-reset-graph-support-audit/v6a_geometry_mapping/trial_mapping_metrics.csv)
- [v6a_geometry_mapping/trial_corridor_traversals.csv](../../outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/v6-reset-graph-support-audit/v6a_geometry_mapping/trial_corridor_traversals.csv)
- [v6a_geometry_mapping/trial_junction_motifs.csv](../../outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/v6-reset-graph-support-audit/v6a_geometry_mapping/trial_junction_motifs.csv)
- [v6b_component_support/component_candidate_behavior_support_summary.csv](../../outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/v6-reset-graph-support-audit/v6b_component_support/component_candidate_behavior_support_summary.csv)
- [v6b_component_support/component_endpoint_session_split_support.csv](../../outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/v6-reset-graph-support-audit/v6b_component_support/component_endpoint_session_split_support.csv)
- [v6b_component_support/whole_route_behavior_support_summary.csv](../../outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/v6-reset-graph-support-audit/v6b_component_support/whole_route_behavior_support_summary.csv)
- [v6c_population_membership/selected_component_panel_summary.json](../../outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/v6-reset-graph-support-audit/v6c_population_membership/selected_component_panel_summary.json)
- [v6c_population_membership/selected_component_source_membership.csv](../../outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/v6-reset-graph-support-audit/v6c_population_membership/selected_component_source_membership.csv)
- [logs/stage_events.jsonl](../../outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/v6-reset-graph-support-audit/logs/stage_events.jsonl)

### V7/V8 arrays and full outputs

- [prefit_config_before_neural_access.json](../../outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/v7-v8-neural-experiments/prefit_config_before_neural_access.json)
- [summary.json](../../outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/v7-v8-neural-experiments/summary.json)
- [predictions.csv](../../outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/v7-v8-neural-experiments/predictions.csv)
- [source_level_null_metrics.csv](../../outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/v7-v8-neural-experiments/source_level_null_metrics.csv)
- [condition_mean_metrics.json](../../outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/v7-v8-neural-experiments/condition_mean_metrics.json)
- [no_stitch_session_metrics.csv](../../outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/v7-v8-neural-experiments/no_stitch_session_metrics.csv)
- [primary29_min3train_min1val/bin100ms/source_level_cue_tensors.npz](../../outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/v7-v8-neural-experiments/primary29_min3train_min1val/bin100ms/source_level_cue_tensors.npz)
- [primary29_min3train_min1val/bin100ms/pseudo_arrays_seed0.npz](../../outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/v7-v8-neural-experiments/primary29_min3train_min1val/bin100ms/pseudo_arrays_seed0.npz)
- [primary29_min3train_min1val/bin100ms/pseudo_arrays_seed1.npz](../../outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/v7-v8-neural-experiments/primary29_min3train_min1val/bin100ms/pseudo_arrays_seed1.npz)
- [primary29_min3train_min1val/bin100ms/pseudo_arrays_seed2.npz](../../outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/v7-v8-neural-experiments/primary29_min3train_min1val/bin100ms/pseudo_arrays_seed2.npz)
- [primary29_min3train_min1val/bin100ms/pseudo_manifest_seed0.csv](../../outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/v7-v8-neural-experiments/primary29_min3train_min1val/bin100ms/pseudo_manifest_seed0.csv)
- [primary29_min3train_min1val/bin100ms/train_only_pca_seed0.npz](../../outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/v7-v8-neural-experiments/primary29_min3train_min1val/bin100ms/train_only_pca_seed0.npz)
- [primary29_min3train_min1val/bin100ms/cue_exposure_conservation_audit.json](../../outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/v7-v8-neural-experiments/primary29_min3train_min1val/bin100ms/cue_exposure_conservation_audit.json)

### V8b/V9 diagnostics, nulls, and final output

- [prefit_config_manifest.json](../../outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/v8b-v9-cebra-final-20260905T224554Z/prefit_config_manifest.json)
- [summary.json](../../outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/v8b-v9-cebra-final-20260905T224554Z/summary.json)
- [v8b/v8b_regularization_predictions.csv](../../outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/v8b-v9-cebra-final-20260905T224554Z/v8b/v8b_regularization_predictions.csv)
- [v8b/v8b_session_label_bin2_source_counts.csv](../../outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/v8b-v9-cebra-final-20260905T224554Z/v8b/v8b_session_label_bin2_source_counts.csv)
- [v8b/v8b_bin2_margin_rows.csv](../../outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/v8b-v9-cebra-final-20260905T224554Z/v8b/v8b_bin2_margin_rows.csv)
- [v8b/v8b_bin2_leave_one_session_cell_block_ablation.csv](../../outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/v8b-v9-cebra-final-20260905T224554Z/v8b/v8b_bin2_leave_one_session_cell_block_ablation.csv)
- [v8b/v8b_source_label_null_pvalues.json](../../outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/v8b-v9-cebra-final-20260905T224554Z/v8b/v8b_source_label_null_pvalues.json)
- [v8b/v8b_source_label_null_stats.csv](../../outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/v8b-v9-cebra-final-20260905T224554Z/v8b/v8b_source_label_null_stats.csv)
- [v9/v9_cebra_predictions.csv](../../outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/v8b-v9-cebra-final-20260905T224554Z/v9/v9_cebra_predictions.csv)
- [v9/v9_dim8_seed0_source_label_null_metrics.csv](../../outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/v8b-v9-cebra-final-20260905T224554Z/v9/v9_dim8_seed0_source_label_null_metrics.csv)
- [v9/v9_null_pvalues.json](../../outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/v8b-v9-cebra-final-20260905T224554Z/v9/v9_null_pvalues.json)
- [v8b_v9_teaching_audit.md](../../outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/v8b-v9-cebra-final-20260905T224554Z/v8b_v9_teaching_audit.md)
- [report_assets/build_report_assets.py](../../outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/v8b-v9-cebra-final-20260905T224554Z/report_assets/build_report_assets.py)

Parallel seed/panel files are retained in their respective linked directories; no omitted configuration is claimed as successful. The complete CSVs preserve the full sensitivity/diagnostic grids and predictions without embedding tens of thousands of derivative rows in the lesson.

### Quick glossary for rereading

- **Observed path:** ordered measured movement; not automatically intention. **Trajectory class:** the previous analysis's endpoint category, not a synonym for path.
- **Source trial:** the real trial identified before resampling. **Pseudo row:** a condition-matched combination of session blocks; never a new biological trial.
- **Mask:** unavailable observation. **Observed zero:** an observed interval with no spike. **Exposure:** actual observed time within an analysis bin.
- **Population vector:** a vector of unit measurements; simultaneous biological interpretation requires verified co-recording. Array shape alone does not establish that.
- **Conditional control:** comparing within the defined endpoint stratum, with remaining nuisance limitations explicit. **Exchangeability:** the assumption justifying which labels may be permuted under a null.
- **PCA dimension:** a shared cell-space coordinate per bin here, not a whole-trial variable. **Receptive field:** the input window the encoder actually reads, distinct from which observations its sampler pairs.
- **BA:** mean class-wise accuracy. **AUROC:** ranking across thresholds. **Log loss/Brier:** probability-prediction scores; neither by itself isolates calibration.
- **Seed range:** assembly/model sensitivity, not confidence interval or biological replication. **Development validation:** inspected during choices and diagnostics, not untouched confirmation.

### Verified-context reading links

- [Johnson & Redish (2007)](https://doi.org/10.1523/JNEUROSCI.3761-07.2007)
- [Cunningham & Yu (2014)](https://doi.org/10.1038/nn.3776)
- [Schneider et al. (2023), CEBRA](https://doi.org/10.1038/s41586-023-06031-6)
- [Kobak et al. (2016)](https://doi.org/10.7554/eLife.10989)
- [Track linearization README](https://raw.githubusercontent.com/LorenFrankLab/track_linearization/master/README.md)
- [Official CEBRA documentation](https://cebra.ai/docs/)

Local source-verification scope: [biological-rationale.md](../../scratch/v6-v9-planning/biological-rationale.md), [graph-methods-research.md](../../scratch/v6-v9-planning/graph-methods-research.md), [temporal-pca-cebra-research.md](../../scratch/v6-v9-planning/temporal-pca-cebra-research.md), [cebra-boundary-verification.md](../../scratch/v6-v9-planning/cebra-boundary-verification.md), [EXECUTION.md](../../scratch/v6-v9-planning/EXECUTION.md). Canonical question/contract: [research-questions.md](../../docs/research-questions.md) and [analysis-contract.md](../../docs/analysis-contract.md).

[fig1]: ../../outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/v6-reset-graph-support-audit/v6a_geometry_mapping/figures/static_region_corridor_graph.png
[fig2]: ../../outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/v6-reset-graph-support-audit/v6a_geometry_mapping/figures/raw_path_overlays_train_validation_examples.png
[fig3]: ../../outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/v7-v8-neural-experiments/figures/primary100_balanced_accuracy.png
[fig4]: ../../outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/v8b-v9-cebra-final-20260905T224554Z/report_assets/v9_same_array_validation_ba_seed_range.png
[fig5]: ../../outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/v8b-v9-cebra-final-20260905T224554Z/report_assets/v9_observed_cebra_loss_curves.png
