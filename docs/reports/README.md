# Research handoff: what to read, what is current, what is retained

**Updated: 2026-09-26.** This index separates the scientific question, completed exploratory studies, teaching explanations and historical evidence. The earlier consolidation did not fit models; the subsequent bounded preprocessing study below did. Both preserve the selected195 scope.

## Start here

**Current cross-session review:** [September26 research reset and decision trajectory](research-reset-20260926/README.md)
([portable HTML](research-reset-20260926/review.html)). Reconciles the last three
sessions, matched PCA completion, decoder/atlas/transfer results and four-worktree
cleanup risks. Includes a proposed no-fit next milestone; no new research fits.

**Completed broader-training experiment (PR #9, open):**
[verified report](https://github.com/Hong-yiii/neuro_science/blob/c19d07c/docs/reports/cebra-full-trial-transfer/README.md).
Time cue-only readout improved relative to cue-only encoder training, but the
predeclared primary rule failed. PR #10 is a teaching-only follow-up stacked on
PR #9. Local reports live under `work/cebra-full-trial-transfer/`; private accepted
outputs remain canonical. Neither PR was merged by this reset.

**Current workspace/recovery:** [workspace guide](../workspace.md), including the
September26 four-worktree inventory. The [September10–13 consolidation ledger](workspace-consolidation-20260910/README.md)
is retained history. Its single-worktree state is no longer current; historical
absolute paths remain provenance. The latest review above adds no biological fits.

**Professor-facing CEBRA/PCA review (evidence through September 24):** [meeting document](../professor_updates/cebra_review_20260924/review.md), [portable HTML](../professor_updates/cebra_review_20260924/review.html). Reconciles the recent path decoder/null results with the endpoint sampler improvements, explains representation versus readout complexity, and proposes bounded discussion decisions. Synthesis only; no new fits. Printable PDF and delivery checks are retained in `outputs/cebra-review-delivery-20260924/`.

**Completed hyperparameter diagnosis, September24:** [meaningful diagnosis](cebra-hyperparameter-diagnosis-20260924.md), [offline illustrated HTML](cebra-hyperparameter-diagnosis-20260924.html), [frozen protocol](cebra-hyperparameter-prefit-20260924.md).1700new decoder fits and20null-world PCA transforms; zero CEBRA/observed-PCA retraining. Weakening L2 did not rescue CEBRA; bandwidth changes reached at most chance mean BA. Temperature improved loss without discrimination. Source-transfer failure is observed, but no unique encoder fault or intrinsic task incompatibility is established. New A0 matched raw/PCA null checks do not establish the77.5% PCA lead; they do not directly test its five-assembly mean.2500model records/395000predictions replayed;117software tests passed.

**Completed frozen-CEBRA decoder experiment, September 24:** [results and interpretation](cebra-decoder-autoresearch-20260924.md), [offline HTML](cebra-decoder-autoresearch-20260924.html), [frozen protocol](cebra-decoder-prefit-20260924.md). Eight fixed recipes,710 new readout fits, zero new biological CEBRA fits; all800 saved model/forward outputs verified after a no-fit lineage repair. No nonlinear CEBRA rescue: best mean BA37.33% Time/35.67% Behavior. Matched PCA+scaled RBF reached77.50% BA, an exploratory lead with no matched PCA null test here. No extra tuning or execution of the separate PCA study within that decoder session; the PCA
study had already completed separately and merged as PR #7.

**Executed CEBRA visualization, September 24:** [results and offline atlas](cebra-latent-atlas-results-20260924.md), [frozen protocol](cebra-latent-atlas-protocol-20260924.md). Thirty-nine saved Time/Behavior/raw/PCA objects across three seeds; rotatable train/development views, full-space spectra and projection/condition-geometry checks. Zero encoder/decoder fits. Early endpoint Behavior needs more than three linear display axes; visual structure does not rescue the nonpositive path results.

**CEBRA visualization research, September 23:** [latent geometry, website image references and saved-run atlas proposal](cebra-latent-geometry-review-20260923.md). Three-angle paper/artifact review; exact interactive/video links, existing Time/Behavior embedding inventory, higher-dimensional interpretation and bounded next steps. No new fits or latent plots; does not replace the separate matched PCA experiment PRD.

**Concise retrospective:** [what worked, what did not, and what remains unknown](path-preprocessing-review-20260909.md) — three-angle review of the completed preprocessing study; no new fits.

**Completed September13–14; merged September23 as PR #7:**
[matched PCA/non-PCA results](https://github.com/Hong-yiii/neuro_science/blob/8340631/docs/reports/path-pca-matched/report.md).
Same-source six-recipe comparison: raw−PCA loss **+0.007023 nats**, both selected
arms **55% BA**; source sensitivity spans zero. A descriptive PCA lead, not
superiority or H1 confirmation. The [original PRD](path-pca-matched-prd-20260913.md)
is planning history. The root checkout is stale; code/results are in current
main and `work/issue-6-pca`, whose ignored artifacts must be preserved before
retirement. Earlier Sept24 “unexecuted” statements are superseded.

**Completed preprocessing study, September 8:** [path-preprocessing teaching report](path-preprocessing-autoresearch-20260908.md), [offline illustrated HTML](path-preprocessing-autoresearch-20260908.html), and [agent handoff](path-preprocessing-autoresearch-20260908-agent.md). Twenty observed-data recipes and source-coherent controls are complete. Stronger regularization improved probability loss, but the small historical diagnostic was6→1-dominated and did not establish broad robustness. All82,283 accepted model-fit instances were forward-replayed without fitting. [Frozen methods](path-preprocessing-prefit-20260908.md).

Earlier cross-study context:

1. **[Current human synthesis](recent-learnings-20260908.md)** — what changed across endpoint and path investigations, what the results do/not establish, and gated next work.
2. **[Agent continuation brief](recent-learnings-20260908-agent.md)** — exact targets, artifact authorities, corrections, source counts and execution boundaries.
3. **[PCA and below-chance explainer](../../learning/place195-pca-and-below-chance-20260908.md)** — 3/8 components per bin → 30/80 linear-classifier inputs; training versus validation; class bias versus reversed predictions; portable figure.
4. **[Preservation and verification ledger](research-release-20260908.md)** — what Git contains, what remains local, how checks were run, and known gaps.

Normative authority remains [research questions](../research-questions.md) and [analysis contract](../analysis-contract.md). Current H1 requires incremental path information beyond endpoints; successful endpoint decoding is not H1. Original holdout exposure remains part of the record.

**Follow-up proposals, not new experiments:** the [path-study plan](path-generalization-next-steps-20260908.md) keeps source-safe pseudopopulations central for a complementary **condition-level** question under recording constraints. The synthesis's E1/E2 real-trial/history/temporal proposals are complementary arms, not a requirement that each cell be significant or that a simultaneous 195-cell recording exist before any progress. Exact same-trial population claims still require the stronger contract. Freeze the chosen estimand/arm and controls before another fit; do not silently substitute one lane for another.

## Completed studies — keep their evaluation objects separate

| Study | Best entry point | Scope / status |
| --- | --- | --- |
| CEBRA hyperparameter diagnosis, September24 | [Results](cebra-hyperparameter-diagnosis-20260924.md), [offline HTML](cebra-hyperparameter-diagnosis-20260924.html) | Same29-unit/4→3 source assay, fixed observed embeddings. Six logistic C values/nine RBF settings: no CEBRA rescue; confidence versus transfer distinguished. Anchored CEBRA/raw-PCA/joint family tails18/21,15/21,19/21 are new-family references, not seed-mean/superiority tests. |
| Frozen CEBRA decoders, September 24 | [Results](cebra-decoder-autoresearch-20260924.md), [offline HTML](cebra-decoder-autoresearch-20260924.html) | Existing29-unit/7-session4→3 component;82train+22development sources. No CEBRA nonlinear criterion passes; A0/O0 CEBRA-only family17/21. PCA+RBF77.5% is a control lead, not a PCA null result or H1 discovery.710new readouts; recovery added0fits. |
| Path preprocessing, September 8 | [Teaching report](path-preprocessing-autoresearch-20260908.md), [offline HTML](path-preprocessing-autoresearch-20260908.html), [agent brief](path-preprocessing-autoresearch-20260908-agent.md) | Completed exploratory first-second count/time/scaling/L2 study:147train+41historical-validation sources,49unit IDs,13sessions. Selected Δ+.0286/BA55%; only2/5 positive; declared null p=.139–.356 and source sensitivity crosses0. No broad H1 win. |
| V6–V9, September 6 | [Teaching/audit Markdown](place195-v6-v9-autoresearch-20260906.md), [self-contained professor HTML](../professor_updates/place195_v6_v9_20260906/place195-v6-v9-professor-methods-results-validity-20260906.html) | Accepted **historical** 29-cell/7-session, fixed-endpoint interior-component benchmark. Whole-cue generalization nonpositive/unstable; not superseded numerically by a different task. |
| Endpoint baseline/diagnosis, September 7 | [Baseline](start-goal-cebra-baseline.md), [diagnosis](start-goal-cebra-diagnosis.md) | Accepted initial 30-class endpoint benchmark and subsequent diagnostics; original settings are not the latest best development settings. |
| Endpoint follow-up, September 7 | [Study index](start-goal-autoresearch.md), [portable teaching HTML](../professor_updates/start_goal_20260907/endpoint-research-report.html) | Completed sampler, readout, duration, coverage and CE investigations. Useful condition separability, not unknown-real-trial deployment or path information beyond endpoints. |
| Path generalization, September 7 | [Completed state](path-generalization-completed-state-20260907.md), [self-contained teaching HTML](../professor_updates/path_generalization_20260907/path-generalization-teaching-audit-20260907.html) | Exact-product evaluation, source transfer, and real-trial per-unit Track C completed. Non-supportive for reliable incremental path information. Exact Track B family p is **19/21**, not the superseded floating-point result. |

Download the HTML reports to read their embedded figures offline. GitHub's source view is not the rendered report. Historical links into ignored `outputs/`, `scratch/`, `work/`, `/tmp/` or original absolute worktree paths still need the data-equipped host; they are not remote downloads.

## Status vocabulary

- **Current:** preferred synthesis, instructions or corrected inference authority for its stated scope.
- **Accepted historical:** valid record of a completed stage, not the latest protocol or a new confirmation sample. Do not erase negative results because a different task later performed well.
- **Frozen plan / journal:** retained protocol or chronology. It records prior authorization and amendments; it is not permission to restart fitting or an up-to-date task list.
- **Superseded / rejected:** a draft, failed attempt, incorrect interpretation or obsolete receipt. Retained for audit, not an alternative result to choose from.
- **Local-only:** deliberately excluded from Git. Continued existence on this host is not an off-host backup guarantee.

## Explicit supersession map

| Earlier material / claim | Status and authority now |
| --- | --- |
| V5's “untouched test” wording | Historical at that stage only; superseded for current inference by the early V6 holdout-exposure record. V5's target/scores remain historical, not a comparable binary-path result. |
| Original V6–V9 report before its teaching rewrite | Superseded pedagogically by the tracked teaching report. Its earlier bytes and review receipts remain in local `audits/`; factual QA was not proof of teaching quality. |
| First V7 attempt without a usable tee log; failed/slow/fast intermediate V9 runs | Failed or superseded attempts, not additional accepted replications. The original report's attempt ledger records missing first-run timing/hashes rather than inventing them. Accepted V9 is `v8b-v9-cebra-final-20260905T224554Z`. |
| Original professor-HTML byte identity | Superseded by the documented formatting reconciliation and current receipt; old report/receipt retained. Scientific content was not refitted. |
| “Absent means the edge is nowhere in the path” | Incorrect shorthand. Original path target is absence from **all interior corridor runs**, excluding first/last runs; Track C separately tests anywhere occurrence. |
| “Below 50% means always predicting absent” | Incorrect: constant-absent BA is 50%. See the saved confusion tables in the PCA/below-chance explainer. |
| September 7 proposal to try source-preserving per-unit analyses | Historical proposal; **Track C is now completed**, not a future untried fix. Current synthesis sets the next gates. |
| Path initial `track_a/` and pre-final report drafts | Failed/superseded; use `track_a_v2/`, final report and completed-state document. Keep the frozen protocol as chronology. |
| Track B raw producer family p≈.8571429 | **Superseded** by exact inclusive-tie p=**19/21≈.9047619** in `summary_exact_audited.json` and `track_b_exact_audit.json`. Models/predictions did not change. This is unrelated to the earlier V9 Time null's numerically similar p. |
| Endpoint `finalization.json` / first browser-layout attempt | Historical/superseded delivery receipts; use `delivery-validation.json` and successful browser receipt, while retaining prior versions. |
| Uncorrected researcher drafts | Not authoritative. The synthesis agent brief records rejected endpoint coverage, incorrect literature attributions and rejected “geometry replaces H1a” proposals. Earlier audit guide records two unrelated PMC citations and the mixed-split metadata-access deviation. |
| Temporary cmux/HTTP views | Disposable navigation snapshots. Prefer tracked lessons and portable HTML; URLs may stop working without loss of the collated explanations. |

## Frozen plans and supporting context

- [Endpoint prefit plan](start-goal-autoresearch-plan.md) and [chronological journal](start-goal-autoresearch-journal.md): executed historical plan/amendments, not a pending queue.
- [Path prefit protocol](path-generalization-prefit-20260907.md): frozen historical gates; final completion and correction authorities above take precedence for outcome interpretation.
- [Earlier audit/alternatives guide](place195-audit-and-next-steps-20260907.md): retained audit procedure; subsequent Track C supersedes its “next step not yet run” status.
- [CEBRA/data-volume comparison](cebra-data-volume-comparison-20260907.md): archive size versus effective same-estimand support, not a universal minimum-N rule.
- [Archived source provenance](archive/research-20260908/README.md): byte-preserved execution/verification/plotting snapshots, including superseded implementations. Do not run them as current entry points without reviewing their inputs and writes.
