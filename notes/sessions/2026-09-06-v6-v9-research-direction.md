# V6–V9 research direction: validation and proposed execution contract

Date: 2026-09-06 (+08:00)
Status: **V6–V9 completed, including pseudopopulation alternatives and GPU CEBRA; independent code/scientific and final report audits accepted the nonpositive exploratory result**.
Final teaching/audit report: [`../../docs/reports/place195-v6-v9-autoresearch-20260906.md`](../../docs/reports/place195-v6-v9-autoresearch-20260906.md). The detailed plan below is retained as historical prerefit/proposal context; actual iterations, deviations and metrics are in the report.
The original planning phase below had no implementation/fitting. Execution now follows `scratch/v6-v9-planning/EXECUTION.md`. IMPORTANT: execution reconnaissance breached the holdout rule via an unfiltered endpoint-position aggregate; parent stopped that worker and commissioned fresh derivation with mandatory split guards. Original test is no longer pristine. See `scratch/v6-v9-planning/holdout-exposure-audit.md`; final report must disclose this rather than repeat the original untouched-test intention.

## Resume here

User wants an iterative research program, not four blind model upgrades:

1. **V6:** formal geometrical maze graph; decision regions as nodes, corridors as edges; resilient path measurement.
2. **V7:** cue-time binning and progressively better temporal analysis.
3. **V8:** PCA-based baselines and low-dimensional organization.
4. **V9:** first meaningful graph-path CEBRA pilot (earlier API/software smoke tests already exist).

Subversions may revisit an earlier assumption when new diagnostics justify it. Return understanding and validated direction to user BEFORE implementation/training. All details below are proposals, not approved/frozen experimental choices.

Compaction-resilient local decision draft: this file (saved on disk, currently untracked/uncommitted; not yet in repository history or a verified backup). Working context and bounded research reports: `scratch/v6-v9-planning/` (ignored, on disk, not backed up by git). Run artifacts will continue under ignored `outputs/prospective_path_first_run/`. Persist approved decisions in repository history when authorized.

## Recovery and provenance

- Requested `/tmp/neuro_science_handoff_graph_path_support_audit_2026-09-01.md` no longer exists.
- Its archived read-tool result was recovered from the prior project session and preserved as `scratch/v6-v9-planning/recovered-2026-09-01-handoff.md`.
- That handoff predates completed V5 and the September 2 professor report. Some start-here/checklist docs still describe pre-V5 blockers; do not mistake these for the latest completed-work inventory.
- Initial repo branch: `place195-v5-report-methodology-update`; HEAD `c4eec75`.
- Pre-existing unstaged changes: `scripts/place195_graph_path_baseline.py` (32 additions / 11 deletions). Scout described formatting-only changes; preserve them and independently inspect before later editing. Do not attribute them to this planning session.
- V5 manifest records a different dirty code revision/hash. Any future rerun must record its actual source hash, not claim bitwise V5 reproduction automatically.
- Original geometry and V5 script graph hashes differ. Reconcile serialization/rules/provenance before freezing V6; mismatch alone does not prove different graph topology.

## What existing work establishes

Sources: latest V5 receipt and generated summary/metrics, `docs/geometry/README.md`, marker/support probes, `context/previous-student-analysis.md`, and independent read-only code/artifact audit.

| Finding | Implication |
| --- | --- |
| 195 place-selected cells across 58 sessions, 1–8 selected cells/session | Not a simultaneous 195-cell population; selected-cell and session biases remain. |
| Cue-relative spike events and actual cue windows are already exported | V7 can derive bins without another raw-data import. V5 itself uses total cue counts. |
| 1,344 floor centroids; 0.625 spacing; four 8×8 pillar cutouts in a 40×40 floor grid | Fine floor graph is a geometrical reference, not a corridor skeleton. |
| Fine graph degrees: 4 nodes degree 2, 280 degree 3, 1,060 degree 4 (researcher's read-only geometry check) | Contracting degree-two floor nodes or treating degree >2 as decisions will not solve V6. |
| 19,162 endpoint-labelled train/validation trials; 18,068 fine and 3,878 coarse5 signatures | Current representation distinguishes almost every fine path; fragmentation and nuisance variation need audit. |
| V5 audit: 10,190 train / 2,042 validation trials contain nonadjacent transitions, despite zero invalid mapped samples | Many paths are split by the current rule. Diagnose sampling/diagonal/grid effects versus real gaps; do not silently interpolate. |
| 908 condition-matched synthetic rows, 525 train / 383 validation; 74.28% entries masked | High-dimensional fitting is constrained by support, not just model expressivity. |
| Validation accuracy: start-goal baseline 7.83%, masked nearest-centroid neural 4.18%; 78/383 unsupported; mean overlap 9.17 cells on supported rows | No demonstrated incremental path information in V5; not evidence that biological information is absent. |
| Validation rows = classes = 383; component sessions per row median 7, observed cells median 25 | Synthetic evaluation is very sparse and not natural trial-frequency accuracy. Availability masks may encode route labels. |
| No start-goal pair supports all 195 cells in both train and validation, even before route subdivision | Graph coarsening cannot by itself solve the full-195 coverage ceiling. |
| Current marker and previous-successful-goal semantics are strongly data-supported | Good exploratory working labels, but formal protocol provenance remains needed for stronger claims. |

V5 pseudopopulations are assembled conditional on the behavior-derived target. They estimate synthetic route-condition separability under exchangeability assumptions, not prediction from an unknown real 195-cell trial. Session availability, sampling/pairing and missingness must not masquerade as neural information.

## Research verdict and supporting literature

**Supported order: improve behavioral measurement → establish time-resolved raw baselines → PCA → CEBRA.** Better models cannot repair unidentifiable targets or missing recording support. A valid negative result at one stage remains useful; no stage is required to produce a positive neural result to justify reporting it.

1. **Graph mapping:** Loren Frank Lab `track_linearization` supplies graph-based 2D path projection and optional HMM temporal continuity. This directly supports geometry-aware edge assignment instead of independent nearest-centroid labels. It is a method precedent, not proof that this broad maze has objectively discrete decision points.
   - <https://github.com/LorenFrankLab/track_linearization>
   - <https://raw.githubusercontent.com/LorenFrankLab/track_linearization/master/README.md>
2. **PCA/population analysis:** Cunningham & Yu (2014), *Dimensionality reduction for large-scale neural recordings*, reviews neural population dimensionality reduction, including PCA and interpretation limits. It motivates a transparent linear baseline, not a guaranteed low-dimensional path code.
   - <https://doi.org/10.1038/nn.3776>
3. **CEBRA:** Schneider et al. (2023), *Learnable latent embeddings for joint behavioural and neural analysis*, explicitly distinguishes time-only from behavior-supervised embeddings and downstream decoding. Supplied context shapes the embedding; apparent graph structure after graph supervision is not independent discovery.
   - <https://doi.org/10.1038/s41586-023-06031-6>
   - <https://cebra.ai/docs/api/sklearn/cebra.html>
   - <https://cebra.ai/docs/api/pytorch/data.html>
4. **Biological plausibility:** Johnson & Redish (2007) reports transient prospective spatial representations in simultaneously recorded rat CA3 ensembles at decision points. This motivates testing temporally resolved prospective information, not expecting the same phenomenon in monkey cue-period pseudopopulations.
   - <https://doi.org/10.1523/JNEUROSCI.3761-07.2007>
5. **Local temporal prior:** previous student used 100 ms bins and reported goal effects around 0.3–0.7 seconds. This supports retaining the whole cue's temporal resolution. Goal decoding is not observed-path decoding beyond endpoints, and historical all-data PCA/random pseudotrial folds should not be copied.
   - `context/previous-student-analysis.md`

Evidence is recoverable from the public URLs/DOIs above and the local bounded reports `graph-methods-research.md`, `temporal-pca-cebra-research.md`, and `biological-rationale.md` under `scratch/v6-v9-planning/`. No inference that a paper's result transfers to this dataset.

## V6 — formal, embedded behavior graph

### Operational definition

Use a geometry-embedded graph `G=(V,E)` with explicit maps:

- `V`: reviewed junction/decision **regions**, plus task endpoints where necessary. Geometrical choice opportunities, not inferred moments of intention.
- `R_v`: spatial region for node `v`.
- `E`: traversable corridor alternatives between regions. Give each corridor a stable identity; retain direction of traversal. Preserve parallel alternatives/loops when topology requires them.
- `gamma_e(s)`: edge centerline/polyline indexed by physical arclength `s` in `[0,L_e]`.
- `C_e`: corridor spatial support/width envelope; retain lateral displacement and assignment ambiguity, not just centerline snapping.
- Trial measurement: ordered edge traversals and node visits, edge progress, direction/reversals, dwell times, sample timestamps and explicit unknown/gap intervals.

Retain raw 2D paths and the existing fine geometry as the reference layer. The coarse graph should discard irrelevant lateral jitter, not erase real alternative routes, order, loops or pauses.

**Important limitation:** the maze is an open floor around pillars. A corridor graph is not unique. Centroids plus upstream Julia geometry describe floor/pillars, but do not independently verify Unity collision walls, invisible barriers or portal semantics. A skeleton is at most a candidate generator. Prefer one small hand-reviewed geometry-based graph initially over a large automatic graph-learning system; add automation only if the review/robustness audit warrants it.

### V6a: geometry/mapping audit

- Reconcile geometry provenance and graph hash definitions.
- Propose and plot decision regions, corridor geometry and raw-path overlays using training/development data, never locked test.
- Diagnose current nonadjacent transitions before choosing gap handling. Use elapsed time and feasible movement/topology to disambiguate; navigation timing here is mapping QA, distinct from V7 neural timing.
- Start with geometry projection plus an explicit unknown state. Add continuity-aware/HMM matching if ambiguity/jitter requires it; reuse an existing suitable implementation only after checking graph/loop support.
- Never use unobserved shortest paths as observed behavior. Any inferred bridge must remain separately flagged and undergo sensitivity analysis.
- Check topology, wall crossings, mapping residuals, ambiguous junctions, fragmentation, route stability under small mapping perturbations, and hand-reviewed examples including reversals/open-area paths.
- Compare V5 versus V6 labels on a common set of source trials; quantify how and why routes merge/split.

### V6b: support and comparable baseline

- Count within-start-goal route variation and support by route × session/cell block × split before fitting neural models.
- Pick a defensible shared cell panel within each planned contrast, or a small set of separately evaluated complete panels/session analyses. Do not require all 195 at any cost.
- Explicitly distinguish observed zero spikes from missing observations. Keep imputation out of the primary model unless separately justified; any allowed exploratory imputation remains a labelled sensitivity with burden reported.
- Check mask-only/session-availability controls and equal-support comparisons. Audit whether route labels reduce to endpoints/session identity.
- Choose a small supported route-family or branch/ordered-segment target and its metric before fitting. Retain ordered path information; shared-middle-segment contrasts are a complementary estimand, not silent replacement of within-endpoint H1a.
- Refit the simplest total-cue neural baseline and start-goal baseline with matched rows/features/coverage. Report all-row performance plus coverage and a clearly labelled common-supported-subset comparison.
- If no route contrast is identifiable/supportable, document the limitation and choose a narrower condition-level question or request data; do not progress by manufacturing synthetic sample size.

V6 starts behavior-only; a small raw neural baseline follows the freeze/support gate. A new learned graph or deep network is not required merely to call this a version.

## V7 — cue timebinning and temporal baselines

**V7a:** reconstruct complete cue-bin counts from existing events, initially 100 ms across the nominal 1-second cue. Preserve actual cue onset/offset and per-bin exposure; mask unobserved/partial bins appropriately. The sum of bins must reproduce the corresponding total-count convention.

For each synthetic row, a session's constituent source trial must remain the SAME across all cue bins. No independent per-bin rematching. Shape is `pseudotrial × cue_bin × selected_cell` only when the support and assembly assumptions are explicit.

- Diagnose firing-rate distribution, zero-count fraction, per-cell reliability, exposure, session differences and sampling/pairing stability on development data.
- Compare the total-count baseline, time-specific simple decoders, and a regularized whole-cue time-resolved decoder where support permits.
- Report source-trial/component-aware uncertainty, not ten times the trial count.
- Use rates/count-exposure models as a sensitivity when cue exposure varies; fixed equal-width counts versus rates alone are just rescaling.

**V7b, if justified:** small bin-width sensitivity (for example 50/100/200 ms), then cross-temporal generalization with compatible cell panels. Train-time/test-time decoding distinguishes stable versus changing decodable condition information; in a pseudopopulation it does not recover actual joint population dynamics. Any smoothing/windows must avoid crossing trials or including post-cue navigation in prospective features.

Temporal bins outperforming totals alone does NOT prove temporal coding: compare matched regularization/complexity and temporal-order controls while preserving exposure. Prior goal effects motivate analysis, not choosing a favorable time interval after looking at results.

## V8 — PCA-based baseline and structure analysis

**V8a:** train-only normalization and PCA on the support-consistent panel. Separate:

- trial-level total-count PCA;
- shared cell-space PCA fit on training trial×cue-bin observations, then project held-out cue time courses into the SAME basis.

Treat flattened unit×time PCA, per-time PCA, and shared cell-space PCA as different estimands; start with the latter for interpretable temporal coordinates. Ordinary PCA is not a solution for V5's NaNs. Do not automatically zero/mean-fill 74% of inputs.

Compare raw versus PCA with the same target, folds, downstream decoder, coverage and metric; choose component counts in development data. Report held-out prediction, dimension/performance curves and stability to session/pseudotrial assembly, not just variance explained or a 3D picture. Low-variance dimensions can carry path information; weak PCA decoding is not absence of information.

**V8b, if supported:** held-out raw/PCA representational geometry versus ordered/shared-middle path components after endpoint/session/cue controls. Pairwise distances share source observations; do not count all pairs as independent evidence. dPCA/FA/GPFA remain optional later methods tied to a diagnosed limitation, not mandatory additions.

## V9 — first meaningful CEBRA benchmark

Earlier CEBRA runs were API/synthetic/one-cell smoke tests. This milestone is the first leakage-audited graph-path comparison, not the first-ever `.fit()`.

**V9a:** CEBRA-Time without path context supplied to the encoder, then the same held-out decoder as raw/PCA. Fit encoder on train only. A valid null raw/PCA result does not forbid a predeclared exploratory nonlinear comparison; the prerequisite is valid targets/support/evaluation, not a required positive result.

Crucial distinction for both V8 and V9a: route-matched pseudopopulation ASSEMBLY already uses path labels. PCA or CEBRA-Time on those inputs is therefore not a wholly target-free discovery pipeline, even though the transform/encoder receives no path supervision. Call it assembly-conditioned exploratory geometry/temporal analysis and carry assembly through the null. A genuinely route-label-free input comparison requires a separately defensible construction, such as verified within-session recording groups; do not attach one component trial's exact path to an endpoint-matched cross-session pseudotrial.

Before fitting:

- Verify actual project environment and pinned CEBRA version; online `main`/docs are not the installed API.
- Prove temporal positives AND neural receptive-field windows cannot cross source/pseudotrial boundaries, during fit and transform. Trial-aware expansion alone does not necessarily constrain the positive sampler.
- Source verification at CEBRA `main` commit `d1842ccc659bdf2d458ab31784ae029b9d48d21f` and v0.6.1 commit `662892a08803f31f0c4f2562012a122cf64ba4b3`: `masking_kwargs` configures random neuron/timestep/block masking augmentation, NOT trial boundaries or sampler eligibility. sklearn `SklearnDataset.__getitem__` uses global `expand_index`, not native `expand_index_in_trial`; `TimeContrastive` has no per-trial border input. Native trial-aware expansion can help windows but does not alone fix positive sampling. Verify/reuse the smallest trial-aware dataset/sampling path and test both invariants; a pointwise encoder fixes only the window issue. See `scratch/v6-v9-planning/cebra-boundary-verification.md` for source symbols/URLs.
- Ten 100 ms bins imply very short sequences. Start with a pointwise/short-receptive-field encoder and small temporal offset if supported; tutorial offset=10 examples cannot be blindly used on ten-bin cues.
- Temporal continuity of a synthetic row is conditional pseudo-time structure only, not real simultaneous covariance/dynamics.
- Check source-session/mask and cue-time confounds, train/validation behavior, seeds and stability. More bins/bootstraps do not create independent examples.

**V9b:** behavior-conditioned CEBRA with frozen train-only route labels or a justified continuous graph-path feature representation; never Euclidean distances on arbitrary route IDs. Preserve the time-only comparison, run appropriate label-shuffle controls through all label-dependent stages (including synthetic assembly if affected), and evaluate a separate decoder on held-out data. Label-shaped geometry cannot independently establish a neural graph.

A positive biological interpretation needs baseline improvement and an appropriate null/confound analysis; a loss curve or attractive embedding is insufficient. If dense support or short-trial boundary handling is infeasible, return a clearly labelled limitation/smoke result rather than silently changing the claim.

## Common evaluation and adaptive-research rules

Before each fit, log analysis class (exploratory here), operational question/estimand, independent source unit, inclusion/exclusion rules, population/panel, baseline, null, split, metric and claim ceiling. Thresholds/budgets are not yet frozen; choose them after the behavior/support audit and before the relevant neural fit.

- Preserve existing immutable complete-source-trial split. Group derivatives and reused pseudotrial components in every outer and inner fold. Sequential history and session drift may require blocked/purged sensitivity analyses.
- Fit learned preprocessing only on training folds. Validation informs bounded exploratory tuning; repeatedly reused validation is NOT fresh confirmatory evidence.
- Keep locked test closed through V6–V9 development. Once it is used after a freeze, it cannot be reused for further tuning and still be called untouched. Strong confirmation may require new sessions/data and verified lab metadata.
- Use comparable targets/rows/features/coverage/decoders across methods. If graph revision changes labels or support, version the graph separately and rerun affected baselines. Do not directly compare accuracy across different classification problems.
- Build nulls at the source-trial/session/block level under justified exchangeability, normally within session and start-goal where support permits. Rebuild/refit all affected label-dependent stages. Do not shuffle bins independently or treat bootstrap copies as independent.
- Neural results can reveal a measurement problem worth investigating, but graph definitions must remain behavior/geometry justified. Selecting the graph that maximizes neural separation would make the measurement circular.
- Log every attempted variant, including failed/negative runs. Record hypothesis, changed factor, all settings/seeds, provenance/hashes/dirty state/packages/device, source/components/exclusions/shapes, results, diagnosis and next decision. Do not train indefinitely until a positive result appears.
- Independent code AND scientific-assumption review before interpreting each milestone; runnable checks for graph invariants, bin-count conservation, split/component integrity and temporal boundaries as introduced.

### Claim ceiling

With current metadata, this is an **exploratory condition-level selected-cell pseudopopulation program**. At best it can establish reproducible association/separability of behavior-defined future route conditions beyond stated endpoint baselines and available controls. It cannot establish an exact real-trial 195-cell state, intention, causal planning, a literal internal graph, simultaneous noise correlations or circuit dynamics. Generalization to animals/populations and missing gaze/view controls remain limited.

## Follow-up: shared-component pseudopopulations (proposal, not implementation approval)

Hongyi explicitly invited alternatives to V5 pseudopopulation construction and proposed pooling trials sharing graph nodes/edges despite different start/goal pairs, while recognizing possible endpoint confounding. This is consistent with the existing shared-path-components H1b direction in `docs/research-questions.md`; it is not a replacement for exact trial-specific H1a.

### What pooling would mean

Example: `A -> J -> K -> B` and `C -> J -> K -> D` share directed segment `J -> K` despite different endpoints. Their **cue-period** observations can contribute to a condition describing future traversal of that component. This pools more existing repetitions and may improve coverage relative to whole-route labels; it does not record new neurons, create new independent trials, or reconstruct a real trial-specific population vector.

Prefer directed edges or ordered middle subpaths over mere node visitation. At a physical junction, distinguish the incoming-edge / node / outgoing-edge motif: passing through a junction in opposite directions or taking different exits should not be one condition automatically. Separate prefix/middle/suffix, traversal direction, repeated encounters and distance/time-to-component when relevant. Obligatory prefixes are strongly start-related and obligatory suffixes goal-related; middle components are candidates, not automatically unconfounded.

Do not splice navigation-period neural snippets into cue features. Pool whole cue observations, preserving a component source trial across all its cue bins. If one trial contributes to multiple motifs, retain the dependence across every derived row, split, uncertainty estimate and null.

### Endpoint coding is signal, not removable measurement noise

A cell may jointly encode cue/goal, start/history, route components and interactions. The issue is whether the component explains something that an adequate endpoint model does not. Removing an additive `start + goal` fit is insufficient when start-goal PAIR interactions explain the component.

The behavior-only gate for each candidate component is a support table:

```text
component, endpoint_pair, session/cell_block, split,
trials_with_component, trials_without_component, observed_cell_panel
```

For fully endpoint-matched comparisons, identify endpoint pairs with both component-present and component-absent paths within usable recording support. Balance/match the JOINT endpoint-pair distribution across contrasted component conditions and across cell/session estimates; matching start and goal marginals alone does not control their interaction. When exact balance is unavailable, disclose the restricted contrast and assumptions instead of claiming complete deconfounding. Also audit cue identity, history, session/mask availability and available view/heading controls.

If component membership is completely determined by `(start, goal)`, the strict conditional-information question is not identifiable as a positive effect: no within-pair behavioral alternatives exist. Pooling, additive residualization, dPCA and nonlinear models cannot manufacture that variation. A held-out endpoint-combination transfer test can still assess generalization of a restricted compositional representation, but cannot by itself prove information beyond the full endpoint pair or a planning mechanism. Nearly deterministic relations require power/support reporting, not a binary model-success shortcut.

### Proposed construction comparisons

1. **Supported whole-route pseudopopulation:** retain as the comparison condition using shared, observed cell panels within each contrast. Missing vs zero stays distinct; no automatic full-195 requirement.
2. **Component-conditioned, endpoint-balanced pseudopopulation:** pool trials sharing a directed segment/motif, then sample one intact cue trial per contributing session/block under a declared common endpoint mixture. Assemble on train and validation source pools separately. Compare masks/session support and results across source-trial pairing seeds. Bootstraps quantify sampling variability; they do not increase the independent sample count. A synthetic row is labelled only by the shared component, not by one source trial's entire route.
3. **Condition-mean population:** for each observed cell, estimate the cue response for the component under the same supported endpoint mixture; collect these estimates into a cell vector. This uses multiple trials to estimate a condition mean rather than inventing pseudotrial fluctuations. Use independently split estimates and source-trial/session-aware uncertainty; retain the counts/exposures behind each mean and missing unsupported conditions. Appropriate for condition-average geometry, not biological noise covariance or single-trial dynamics.
4. **No stitching: per-cell/verified within-session analysis:** first compare held-out cue-count models with endpoint-pair/nuisance effects against models additionally containing component effects, using training-only fitting and appropriate exposure handling. Combine effect estimates conservatively without pretending every cell/session is an independent animal. This is the simplest check that component associations exist beyond stated controls before a larger synthetic representation pipeline. It need not find a per-cell effect for a later valid population comparison to be allowed.

Conditions can share cells only where those cells actually have source-trial support. Pooling may alleviate the V5 route-sparsity problem, but common-panel size and endpoint overlap are not yet measured. Do not promise a dense 195-cell matrix.

### Evaluation and place in roadmap

- Proposed **V6b** explicitly audits pseudopopulation construction/support as well as graph labels. Proposed **V6c** compares a small supported whole-route baseline against one or two directed-component/condition-mean alternatives if V6b supports them; do not implement every variant by default.
- Freeze geometrical motifs from behavior/geometry and choose the population construction before comparing V7/V8/V9 methods. Version graph and assembly separately.
- Use source-trial conditional shuffles and refit/reassemble affected stages, with within-session/endpoint exchangeability where feasible. With no within-endpoint variation, a conditional shuffle cannot identify the desired effect; it is not evidence that a weaker shuffle is acceptable.
- Add endpoint-only and mask/session-availability controls. Test transfer across held-out endpoint combinations as a complementary compositional analysis, not a replacement for full endpoint controls.
- Matching/averaging on the future component itself uses labels, so subsequent unsupervised PCA/CEBRA-Time remains assembly-conditioned. Synthetic validation with target-known assembly estimates condition-level separability, not real-trial prediction from an unknown path.
- dPCA is optional characterization, not an automatic endpoint-cleaning solution. Primary methodological reference: Kobak et al. (2016), <https://elifesciences.org/articles/10989>. A further reading lead is Bernardi et al. (2020), *The Geometry of Abstraction in the Hippocampus and Prefrontal Cortex*, DOI `10.1016/j.cell.2020.09.031`; only metadata, not its full methods, was verified in this follow-up.

Fresh bounded research check: `scratch/v6-v9-planning/shared-component-pseudopop-review.md`. No fitting, data-support recomputation or locked-test inspection was performed; the above is a proposal and its feasibility remains open.

## Decision log

- 2026-09-06: recovered the missing handoff; reconciled its earlier scope with completed V5 receipts.
- 2026-09-06: direction judged methodologically sensible, conditional on graph identifiability, recording support and leakage-safe evaluation. Not a promise of positive neural evidence.
- 2026-09-06: proposed V6 as region/corridor geometry plus support repair; reject naive branch-node contraction of a thick floor grid.
- 2026-09-06: proposed smallest robust temporal → PCA → CEBRA sequence, allowing subversions and negative findings.
- 2026-09-06: independent read-only plan review found no blockers; addressed explicit CEBRA mask/API clarification, local-only persistence wording and recoverable source references. Parent additionally clarified that route-conditioned assembly prevents claiming a wholly label-free PCA/CEBRA-Time pipeline.
- 2026-09-06: Hongyi invited pseudopopulation alternatives and suggested shared graph intersections/edges across endpoints. Proposed a V6b population-support workstream and optional V6c directed-component pilot; retain endpoint-pair controls, conditional-identifiability limits and independent-source counts. Shared-component pooling is complementary H1b, not automatic repair of trial-specific H1a.
- 2026-09-06: Hongyi authorized full exploratory V6–V9 autoresearch with GPU, independent audit gates, metrics and a verbose teaching/audit Markdown report. Runtime isolated and actual CUDA matmul verified.
- 2026-09-06: stopped first V6 writer following independently verified holdout endpoint-aggregate exposure and potential design contamination. No new graph code/artifacts were produced. Continued only fresh static/split-filtered derivation under reviewer conditions; test no longer pristine and excluded from further evaluation. Incident and rejected iterations preserved.
- 2026-09-06: completed V6/V7/V8/V8b/V9. Final primary panel: 29 cells, 7 sessions, 82 train / 22 validation source trials. Final GPU block: 12 observed + 40 full-pipeline source-null CEBRA fits, 1,000 updates each. No robust predictive improvement. Perfect 200–300 ms synthetic bin score had family-aware source-null p=0.2178; CEBRA-Time/Behavior predeclared dim8 seed0 p=0.857/0.619. All numerical results remain exploratory, not evidence of absent biology.
- 2026-09-06: final independent code/scientific review and written-report accuracy review found no remaining findings. Parent verified 26 focused tests, eight compiled source/test files, all 52 checkpoint reload parities zero and final source hash matching the run. Full LSP confirmation was incomplete (three checks timed out); no confirmed errors. No commits made.

## Supporting local artifacts

- `scratch/v6-v9-planning/STATE.md`
- `scratch/v6-v9-planning/recovered-2026-09-01-handoff.md`
- `scratch/v6-v9-planning/local-audit.md`
- `scratch/v6-v9-planning/graph-methods-research.md`
- `scratch/v6-v9-planning/temporal-pca-cebra-research.md`
- `scratch/v6-v9-planning/biological-rationale.md`
- `scratch/v6-v9-planning/cebra-boundary-verification.md` (follow-up primary-API check)
- `scratch/v6-v9-planning/independent-plan-review.md`
- `scratch/v6-v9-planning/shared-component-pseudopop-review.md`

Researcher reports are working notes, not runnable instructions or accepted code. In particular the graph report's example `audit-geometry` command is a proposed/nonexistent interface, not a verified command to run.
