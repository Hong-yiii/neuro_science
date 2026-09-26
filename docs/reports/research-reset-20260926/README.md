# Research reset: evidence → decisions → cleanup

**Review date:** 26 September 2026, Asia/Singapore. **Evidence window:** 19–26 September; three most recently active prior neuroscience sessions. **Status:** retrospective evidence review and proposed roadmap, not a new analysis or authorization to fit. [Portable review](review.html).

> **Bottom line:** we have learned more about the measurement pipeline than established new biology. Stop treating CEBRA as the question. Decide which prospective-path claim the available recordings can identify; then consolidate the software around that evaluation.

## 1. The review trajectory — a 30-minute decision meeting

| Stop | Read / discuss | Decision to leave with |
| --- | --- | --- |
| **1 · 5 min: reset the question** | Cue-period information about the later observed **path beyond start and goal**. Not endpoint classification, intention or attractive latent plots. | Keep H1 as the thesis question; explicitly choose the next operational research lane. |
| **2 · 8 min: reconcile the week** | The evidence ledger below. Separate relative improvement, absolute prediction, null support and independent replication. | Agree what is established, what is a lead, and what has already been tried. |
| **3 · 7 min: choose the next uncertainty** | Source support/identifiability versus another encoder or decoder tweak. | Select one bounded milestone with an explicit stop condition. |
| **4 · 5 min: agree the cleanup boundary** | Four worktrees, dirty source, three open PRs, private artifacts. | Authorize staged integration and preservation, not a bulk move/delete. |
| **5 · 5 min: freeze the handoff** | Answer the decision card at the end. | One current roadmap, one owner, one evaluation contract. No automatic experiment queue. |

**Recommended default:** preserve the condition-level pseudopopulation lane, pause broad model searches on the exposed benchmark, and make the next milestone a no-fit support/provenance/identifiability audit. This is a recommendation for Hongyi's decision—not an already approved pivot. Exact trial-specific H1 remains a separate, stronger recording contract; we do not need a simultaneous 195-unit recording to make useful condition-level progress.

## 2. What actually happened

### The last three sessions

Identified by the most recently modified parent transcripts before this review, excluding this session and child-agent logs. Read targeted user/final messages and checked their claims against reports, lightweight summaries and Git/PR state. Session history was not rewritten or exported into this report.

| Session | User's question | What was completed | What it changed |
| --- | --- | --- | --- |
| **Sept 23–25 · `01a0ce04…`** | Is logistic regression too simple to read the CEBRA latent? Is excessive regularization the problem? | Literature/readout review; eight frozen-embedding decoder recipes; C/gamma diagnosis; professor-facing synthesis and teaching update. | No tested nonlinear CEBRA rescue; reducing regularization did not resolve poor historical-source transfer. A PCA+RBF lead remains descriptive. |
| **Sept 23–25 · `01a0ce08…`** | Can we visualize Time/Behavior like the CEBRA website? | Saved-run atlas, spectra and projection diagnostics; reviewed package in **PR #8**; temporary previews ended. | A 3D plot can omit much of the representation. Shape and apparent complexity are not evidence of prospective-path information or biological topology. |
| **Sept 24–25 · `01a0d2ef…`** | Can navigation-period training teach a representation that helps cue-only decoding? | Bounded cue-only versus broader-training experiment in **PR #9**; teaching-only explanation in **PR #10**. | Broader CEBRA-Time training improved relative loss and mean BA, but failed its absolute-loss success condition. Behavior did not improve loss. |

**Week boundary matters:** no additional Sept 19–22 work was found in these session records or inspected recent Git history; that is not proof that nothing happened elsewhere. **PR #7 merged on Sept 23, but its matched PCA experiment ran Sept 13–14.** Count the merge as integration this week, not 26,266 new fits this week.

### Evidence ledger — not a cross-study leaderboard

| Study / evaluation object | Result | Strongest safe reading |
| --- | --- | --- |
| **Matched raw/PCA, five endpoint panels** · 147 train + 41 historical-validation sources; 49 unit IDs / 13 sessions; first-second pooled rates | Raw loss **0.664564**, PCA **0.657541**; paired difference **+0.007023 nats**; both BA **55%**. Fixed-selection source sensitivity for the difference spans **−0.011444 to +0.023426**. | Small descriptive PCA advantage on exposed sources; not PCA superiority or broad prospective coding. Completed and merged in PR #7. |
| **Frozen-CEBRA readouts, 4→3 path component** · 29 units / 7 sessions; 82 + 22 sources | Best nonlinear mean BA: Time **37.33%**, Behavior **35.67%**. PCA + scaled RBF SVM **77.50%**. | No tested decoder rescue for these embeddings. PCA+RBF is a lead, not an all-linear model or a null-established H1 result. |
| **C/gamma diagnosis on those saved representations** | Weaker L2 did not rescue CEBRA; temperature could improve probability loss without changing discrimination. Anchored CEBRA/raw-PCA/joint family tails **18/21, 15/21, 19/21**. | Poor source-pool transfer is observed; its unique cause and CEBRA's general suitability remain unresolved. These anchored nulls do **not** test the PCA five-assembly 77.5% mean. |
| **Saved-run latent atlas** · 39 saved objects, no encoder/decoder fits | Strong early endpoint Behavior displays retained roughly **56.3–64.2%** of development energy in three axes; participation ratio **5.32–6.04**. | Three axes are an incomplete view. Neither those values nor visible shapes establish intrinsic biological dimension, topology or H1b. |
| **Broader-training transfer, same 4→3 target/cohort but newly matched construction/training** | Time/logistic loss **1.010464 → 0.710618**, BA **32.64% → 61.81%**, AUROC **0.146 → 0.574**. Constant-.5 loss is **0.693147**. | Relative Time improvement, **primary criterion failed**. Only one of three seeds had AUROC above .5. Not confirmed absolute path information. |

BA means balanced accuracy; its binary chance reference is 50%. Probability loss penalizes confident errors. The model with improved loss need not have improved discrimination; a better model than a weak baseline need not beat a useful baseline.

**Do not compare 77.5%, 61.8%, 55% and endpoint ~83% as a league table.** Different panels, path components, assembly seeds, feature construction, fitting procedures and readouts change the evaluation object. Endpoint decoding is a different target. The later transfer experiment's own PCA+RBF control was **55.56% BA**, not the earlier 77.5%; that is not an independent replication or refutation of the earlier score.

### The most tempting misreading: “1/21 means broader training works”

The broader-Time mean paired loss gain was **+0.299846 nats**. Its source-coherent, full-pipeline label-null tail was **1/21**. But:

- Maximum-over-Time/Behavior paired-gain tail: **3/21**.
- Absolute broader-Time loss-based no-association tail: **12/21**.
- The frozen success rule required gain ≥ .01 nats **and** loss < log2 **and** BA > .5 **and** AUROC > .5. The loss requirement failed.
- BA source-weight sensitivity: **44.44 / 61.81 / 76.42%**; **8/22** source deletions became inestimable. These are sensitivity diagnostics, not biological confidence intervals.

The gain concerns improvement over a poor cue-only model under a particular null. It is not a general equal-risk superiority test, a passed absolute-performance null, or confirmation on untouched sources.

### What “broader training” did—and did not—mean

Navigation activity entered **encoder training from training sources only**. Decoder fitting and historical-validation predictions used **cue-only** inputs. The comparison used a fixed 1,000-update budget with 50/50 cue/navigation sampling, not simply extra optimization. Native bins were not time-warped; normalized-progress assembly is not a simultaneously observed physical path. CEBRA-Time's objective omits path labels, but its pseudopopulation assembly remains label-conditioned.

This is a valid bounded engineering question. It is not proof that we have learned a label-free navigation manifold, decoded unknown real trials, or observed planning.

### Execution and failure accounting

- Decoder study: **710 new readouts**, zero new biological CEBRA fits. Five planned PCA transforms plus three disclosed preflight transforms. A class-local product-row ID merge broke postprocessing; the recovery repaired lineage and replayed **800** saved models with fitting blocked. Preserve the failed attempt, not as a second result.
- Hyperparameter study: **1,700 new readouts**, **20 null-only PCA transforms**, zero CEBRA or observed-PCA refits. Verification covered **2,500 model records / 395,000 predictions**; records include reused models, not 2,500 new fits.
- Atlas: no encoder/decoder fitting or checkpoint loading; display/projection operations are descriptive. Retain failed/repaired build attempts separately.
- Transfer: one completed biological attempt, **252 encoders + 63 PCA transforms + 756 readouts**; recorded forward-only replay of **1,071 fitted artifacts**. Teaching PR #10 adds no fits.
- Historical verification and software-test counts are reported from their receipts. **This reset did not rerun model verification, inspect raw recordings, or fit models.** AI review is not laboratory metadata validation or human scientific peer review.

## 3. What the week resolves—and what it leaves open

**Resolved enough to stop repeating:** the decoder was trained; nonlinear readouts were tested; reducing L2 was tested; an atlas exists; broader-training transfer was tested; matched raw/PCA was executed and merged. Old “pending” checklists are not an experiment queue.

**Still open:** whether a meaningful future-path contrast is identifiable beyond endpoints and nuisance variables; how much independent source support it has; why these source pools transfer poorly; whether any lead reproduces on genuinely unexposed observations; the biological interpretation of any reproducible signal.

The 195 selected units across 58 sessions are an archive scope, not a simultaneous 195-column recording or the sample size of each benchmark. Synthetic rows, cue bins, optimizer seeds and plotted points do not create independent biological trials. Selection, marker/clock semantics, cue/history/gaze/heading confounds and original holdout exposure remain limitations. A negative result here does not establish absence of H1.

## 4. High-level choices

| Decision | Recommended default | Alternative and what it costs |
| --- | --- | --- |
| **Research lane** | Condition-level reproducibility beyond endpoints, with exact H1 language kept separate. | Exact same-trial population prediction requires verified simultaneous recordings linked to the same trial's path. No pseudo-assembly can supply that missing observation. |
| **Next uncertainty to reduce** | Source support, identifiability and recording/nuisance provenance before more model variants. | Another bounded CEBRA engineering study is legitimate if declared methodological, but cannot by itself repair exposure, support or missing metadata. |
| **Role of CEBRA** | Candidate representation beside raw/PCA, not the project's success criterion. Keep broader Time as a secondary candidate. | Making CEBRA/manifold methodology the central deliverable is a thesis-scope change to discuss explicitly with the professor. |
| **Geometry / H2** | Keep atlas for diagnostics and teaching; defer biological topology and artificial-agent comparison as primary aims. | A descriptive geometry project is possible, but must not be relabelled as prospective-path evidence. |
| **Software target** | One supported evaluation path plus frozen study runners/evidence. Integrate before reorganizing files. | A package-wide rewrite now adds provenance and regression risk without creating better scientific identification. |

### Proposed next milestone: a no-fit go/no-go memo

A bounded **2–3 working-day planning target**, subject to lab availability—not a promise and not authorization to access new data.

1. **Freeze the operational claim.** Pick a behavior-defined interior component or route contrast, cue window, population lane and strongest allowed claim. Do not pick it because it produced the highest neural score.
2. **Audit existing manifests first.** Map real sources × sessions × endpoints × target class, singleton pools, prior exposure and exclusions. Label missing metadata; do not infer simultaneity or cue identity from file names. Any new raw-data extraction needs a scoped protocol.
3. **Ask the lab targeted questions.** Verify marker/cue semantics, recording groups, unit selection and whether required nuisance variables/new source trials are available. Retain selected195 scope unless explicitly changed; do not resurrect the excluded eight-unit supplement.
4. **Define the decision rule before outcomes.** Agree minimum worthwhile incremental performance, baseline, primary metric, split unit, uncertainty/null assumptions and stop rule. The .01-nat rule in PR #9 is not automatically a biologically meaningful threshold for the thesis.
5. **Return go/no-go options, not fits.** If adequate support exists, propose one frozen raw/PCA-led, matched evaluation with bounded CEBRA secondary comparisons and source-aware controls. If not, choose targeted data/metadata collection or an explicitly narrower methodological deliverable.

**Make the memo decisive:** deliver one candidate-contrast support table, an exposure ledger, a short list of lab-verifiable unknowns, and a go/no-go recommendation. Pause the biological interpretation if the contrast is effectively determined by endpoints, class support collapses after conditioning, or plausible critical nuisance variables cannot be addressed. No new confirmation set means **no confirmatory claim**, not a ban on explicitly exploratory or methodological work. If these gates are already satisfied, do not spend three days rewriting caveats: proceed to proposing one frozen matched study.

**Gate for a subsequent experiment:** independent code and scientific review, source-first splits, training-only learned transformations, endpoint/nuisance baselines, coherent nulls and a fixed budget. Reserve genuinely unexposed observations prospectively if confirmation is intended. Another shuffle/resplit of already inspected sources does not restore a pristine test. Per-unit checks are complementary, not a requirement that each neuron first be significant.

## 5. Cleanup: what is actually wrong

The immediate problem is **fragmented authority**, not insufficient folder nesting.

| Location / publication | Inspected state on Sept 26 | Handling |
| --- | --- | --- |
| Canonical `~/neuro_science` | Dirty old release branch, **`438856e`**; Sept24 decoder/diagnosis/professor files are not committed. Local `main` is older still. | Preserve exact dirty bytes before integrating. Do not reset or switch over them. |
| Cached `origin/main` | **`8340631`**, includes merged **PR #7**. Live GitHub confirms #7 merged Sept23. | Recheck main before integration; base the integration branch on current main, not the old release. |
| `work/issue-6-pca` | Clean branch **`018d5f6`**; PR #7 merged. **Its ignored fitted artifacts remain here.** | Candidate for later retirement only after hashed copy/migration, verification and owner confirmation. Merge coverage is not data backup. |
| Atlas **PR #8** | Open, head **`a401eb3`**; no registered atlas worktree. Local runner matches PR bytes, at least one report differs. | Reconcile local edits; do not overwrite one version wholesale. Derived private research content remains access-sensitive. |
| `work/cebra-full-trial-transfer` / **PR #9** | Clean **`c19d07c`**, open against main; outputs deliberately live in canonical `outputs/`. | Keep during review; code has live canonical-root/protocol coupling. |
| `work/cebra-time-teach` / **PR #10** | Clean **`ea6a8fe`**, open **against PR #9's branch**, not main. | Review #9 first; if approved/merged, reconcile #10's base/diff. Retain worktree until its own review completes. |

Publication status is not scientific acceptance. No PR was merged, retargeted, closed or pushed by this reset.

### Active code map — preserve these relationships

| Layer | Existing entry points / dependencies | Cleanup implication |
| --- | --- | --- |
| Import, QC, source splits | `scripts/import_place195_sessions.py`, `place195_split_*`; retained source tensors/manifests | Preserve private data, source identities and frozen split hashes. Do not reimport as a cleanup shortcut. |
| Historical V6–V9 and path studies | `place195_v7_v8_neural_experiments.py`, `place195_v8b_v9_cebra.py`, `place195_path_generalization_phase1.py` and their verifiers | Older runners are also imported helpers and replay dependencies, not automatically dead code. |
| Preprocessing / matched PCA | `place195_path_preprocessing_autoresearch.py`; main/PR7 adds `place195_matched_pca.py`, `verify_matched_pca.py` and replay schema changes | Integrate the PR7 helper change before assessing compatibility of dirty Sept24 runners. Do not cherry-pick only pretty reports. |
| Frozen decoder → diagnosis | `cebra_decoder_autoresearch.py` → `cebra_hyperparameter_diagnosis.py`; paired tests | Package uncommitted implementation and scientific records together; audit imports before any moves. |
| Atlas | `cebra_latent_atlas.py`, `.html`, paired test; PR8 package | Descriptive saved-artifact viewer; distinguish local output from authorized PR copies. |
| Broader transfer | PR9 `cebra_full_trial_transfer.py`, builder/test | `WORKTREE_ROOT` resolves protocol; hardcoded `CANONICAL_ROOT` resolves outputs/runtime. These are live dependencies. |
| Software checks | `scripts/check_research_software.py` discovers `scripts/test_*.py` | A move into `src/`/`tests/` breaks current discovery/import/root assumptions unless changed and tested together. |
| External lab references | `Hippocampus.jl`, `PyHipp` submodules | Keep their histories/pointers intact; do not fold them into a new Python package. |

### Safe cleanup sequence

**Phase 0 — done in this reset:** created a fresh **cmux review workspace**, not another Git worktree; recorded four-worktree/PR state; hash-verified copies of pre-existing dirty/untracked source/docs plus navigation files (**27 files / 3,332,830 bytes**). Added this consolidated review and refreshed current navigation. No biological files moved or deleted.

**Phase 1 — integration checkpoint, proposed:** inventory and preserve the rest of each worktree's unique ignored evidence; create a recoverable Git snapshot/bundle before branch operations. Build targeted manifests for PR7's worktree-local outputs, the root Sept24 outputs and canonical PR9 outputs before touching those locations. Other `work/` directories, including `work/cebra-hyperparameter-20260924/`, remain unclassified, not disposable. Reconcile root Sept24 source/reports against main and PR8. Review PR9, then stacked PR10. Preserve failure logs, frozen protocols and exact executed snapshots. One writer; independent reviewers remain read-only.

**Phase 2 — consolidate accepted artifacts, proposed:** first copy—not move—`work/issue-6-pca/outputs/path-pca-matched/` to a canonical named output location with a source→destination hash/symlink map. Check branch containment, all unique untracked/ignored files, path resolution and no-fit replay before any worktree removal. Record relocated paths without rewriting old execution manifests. Only remove the exact owned, verified worktree after approval.

**Phase 3 — structural cleanup, proposed:** designate the supported pipeline and group navigation by **question → protocol → runner → accepted run → verifier → report**. Keep completed study runners and hash-bound snapshots frozen. Extract or relocate shared helpers only when the selected next study needs it; update every importer, test-discovery rule and root-relative path in that bounded change. Avoid a speculative framework or mass renaming.

**Phase 4 — archive and prune, proposed:** only retire items with documented owner, retained replacement, dependency checks, hashes and rollback. `work/retired-worktrees`, `.pi`, `.pi-subagents`, runtime environments and unknown caches are not blanket deletion targets. Report disk savings after verified deletion, not projected from directory names.

**Validation for integration:** existing clone-only software suite on the actual integrated tree, focused regression tests for shared-helper/replay compatibility, link checks and explicitly authorized saved-artifact replay with fits blocked. A clean type checker or process exit alone is insufficient. Never recreate missing accepted outputs by fitting models during cleanup.

**Recovery:** pre-reset copies and manifest are under `work/research-reset-20260926/before/` and `outputs/research-reset-20260926/before.json`. Compare current hashes before selectively restoring a file so later edits are not lost. These copies protect the current source/docs only; **they are not an off-host backup of raw data, models or all worktrees**. Broader migration requires its own recovery manifest and retained originals.

## 6. Decision card — answer these before the next run

1. **Priority:** condition-level biological evidence first, or a deliberately methodological CEBRA thesis lane? **Recommendation: evidence first.**
2. **Next deliverable:** authorize the no-fit support/metadata go/no-go memo, or choose one explicit competing study? **Recommendation: the memo.**
3. **Data:** can we obtain genuinely new source trials and the missing task/nuisance metadata if support fails? If not, what narrower claim would still be useful?
4. **Cleanup authority:** approve preservation/integration first, then a separately verified PCA-artifact relocation/worktree retirement? **Recommendation: yes in stages, no bulk deletion.**
5. **Stop rule:** what minimum useful effect and replication would justify more representation work? Agree this with the professor, rather than inheriting an arbitrary score from an old study.

A good answer to this review is a short set of choices, not another giant parameter sweep.

## 7. Evidence and review provenance

Canonical question and constraints: [`docs/research-questions.md`](../../research-questions.md), [`docs/analysis-contract.md`](../../analysis-contract.md). Workspace recovery: [`docs/workspace.md`](../../workspace.md).

Primary sources checked:

- Matched PCA: [merged report at main commit `8340631`](https://github.com/Hong-yiii/neuro_science/blob/8340631/docs/reports/path-pca-matched/report.md); local `work/issue-6-pca/docs/reports/path-pca-matched/{report.md,summary.json,execution.md}`. Execution Sept13–14, merge Sept23.
- Frozen decoders: [result](../cebra-decoder-autoresearch-20260924.md); `outputs/cebra-decoder-autoresearch-20260924/recovery-20260924T042259Z/summary.json`.
- Hyperparameter diagnosis: [result](../cebra-hyperparameter-diagnosis-20260924.md); `outputs/cebra-hyperparameter-diagnosis-20260924/run-20260924T105957Z/{summary.json,null_family_tails.json}`.
- Atlas: [result](../cebra-latent-atlas-results-20260924.md); `outputs/cebra-latent-atlas-20260924/atlas/`; [PR #8](https://github.com/Hong-yiii/neuro_science/pull/8).
- Broader transfer: [report at `c19d07c`](https://github.com/Hong-yiii/neuro_science/blob/c19d07c/docs/reports/cebra-full-trial-transfer/README.md); local `work/cebra-full-trial-transfer/docs/reports/cebra-full-trial-transfer/{README.md,summary.json,execution.md}`; [PR #9](https://github.com/Hong-yiii/neuro_science/pull/9).
- Teaching only: `work/cebra-time-teach/learning/cebra-time-transfer-teach-max-20260925.html`; [stacked PR #10](https://github.com/Hong-yiii/neuro_science/pull/10).
- Earlier professor synthesis: [Sept24 review](../../professor_updates/cebra_review_20260924/review.md). Historical source reports remain intact even where their PCA-pending wording is superseded by PR7.

**First fan-out:** three fresh-context session researchers and one codebase scout. **Parent convergence:** reconciled their evidence with live GitHub PR status, branch-specific PCA results and transfer summaries. Rejected one inherited assertion that the Sept13 PCA experiment was still unexecuted: its execution ledger and merged PR7 establish completion. Local branch copies can carry stale facts even when a recent transcript repeats them.

**Second fan-out:** independent scientific-claim review, research-priority challenge and cleanup safety review. Findings and parent dispositions are recorded in [review-checks.md](review-checks.md). The scientific reviewer supported the core interpretation; low delivery/provenance findings were addressed. The cleanup reviewer recommended the navigation-only slice before integration. The strategy challenger ranked support/identifiability first, then a bounded matched raw/PCA-led study, then another broader-Time methods experiment. Live PR evidence was captured by the parent at **2026-09-26 09:24:17 UTC**, in `outputs/research-reset-20260926/publication-state.json`; the reviewers did not independently query GitHub. Agent briefs stay local under `work/research-reset-20260926/`; original harness artifacts/transcripts remain untouched. No web literature search was needed for this retrospective, and no new laboratory access was used.

### Reading and preview operations

`review.html` is self-contained, with no network resources or server. The cmux browser displays an in-memory copy in a verified `about:blank` document; reloading clears that disposable view. The durable HTML can be reopened locally. Source links are optional and may require private GitHub access. No listener, daemon, timer or public ingress is introduced; existing cmux lifecycle rules apply. Close the browser/workspace to dismiss it. The durable Markdown/HTML remain here.

Rebuild/check with the retained environment: `scratch/v6-v9-runtime/bin/python docs/reports/research-reset-20260926/render.py` or append `--check`. The renderer reads this Markdown, checks existence of its local references, and writes/checks the sibling HTML. In the standalone browser view, local-only references are shown as filesystem paths instead of broken relative links; optional GitHub links remain clickable. It does not import research runners or load data/models.
