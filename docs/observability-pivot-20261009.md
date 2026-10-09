# Next session: hippocampal observability and CEBRA

**Recorded October 9, 2026 (Singapore). Status: owner-requested next-session direction; operational question and protocol still open.** Hongyi asked to update and merge [PR #15](https://github.com/Hong-yiii/neuro_science/pull/15), keep the observability pivot indexed, and take it up in a new session. This note preserves that handoff; it does not start an experiment.

## Decision and authority

The lab is interested in **observability of the hippocampus**, with **CEBRA a specific methodological interest**. The next session should develop this direction rather than automatically extend the H1-led prospective-path programme or search until CEBRA wins.

This supersedes the next-work priority in the [September27 direction](project-direction.md), not the historical results or scientific safeguards. H1a/H1b remain documented questions and were neither confirmed nor disproved; they are not the automatic next-session objective. Artificial-agent H2 stays removed. No replacement numbered hypothesis, final thesis title, CEBRA objective, dataset expansion or fit budget has been adopted.

**First question for Hongyi/the mentor:** does "observability" mean recoverability of measured task variables from limited neural recordings, or reconstruction of an underlying dynamical state?

- **Recommended initial operational meaning, not yet a lab-agreed definition:** recoverability and stability of task-related information under the recording/representation constraints.
- **Formal dynamical-system observability:** reconstructing system state from partial measurements over time. This requires an explicit dynamical model and suitable assumptions/data; accurate decoding or a CEBRA embedding alone does not establish it.
- Stable readout transfer, reproducible embeddings and formal observability are distinct properties. Do not silently substitute one for another.

## Candidate research question — proposal

> How do recording limitations and encoder-training choices affect the recoverability and temporal stability of task-related hippocampal information?

A narrower first comparison could ask whether joint cue/navigation CEBRA-Time produces task readouts that transfer across time/phase better than cue-only CEBRA, PCA and raw features. This is a proposal, not a frozen design or an expected positive result. Endpoint decoding could become a primary assay under the pivot once its target semantics and interpretation are agreed; it still is not evidence for path information beyond endpoints.

CEBRA remains a central tool under evaluation, not a required winner. Define its proposed benefit before evaluating it: same-window decoding, temporal transfer, cross-phase transfer, source reproducibility or sampling robustness. Do not change the success criterion after seeing which metric favors it. A robust PCA advantage or bounded negative result remains useful.

## What is already complete

Keep the cohorts and evaluation objects separate. See the linked reports for source distributions, curves, confusions, nulls, provenance and reviewed execution records.

| Study | Completed work | Interpretation |
| --- | --- | --- |
| [October5 path-component study](reports/cebra-cue-time-readout-20261005/README.md), [offline HTML](reports/cebra-cue-time-readout-20261005/report.html) | Fixed 4→3 component;29 units/7 sessions;82 training/22 historical-development sources.5,040 new bin readouts and504 whole-cue replays; no encoder/PCA refits. | Joint/logistic descriptive peak88.9%; primary gain tail9/21, absolute BA tail17/21. No validated best window or robust H1 result. |
| [October7 endpoint study](reports/cebra-endpoint-time-readout-20261006/README.md), [offline HTML](reports/cebra-endpoint-time-readout-20261006/report.html) | 195 units/58 sessions;12,288 training/3,265 historical-development sources.126 encoders,63PCA fits,10,395 readouts; all20null worlds/3seeds. Full fit-blocked replay and independent QA passed. | Whole-cue cue→joint BA: pair63.75→75.56%, start71.81→72.64%, goal85.14→83.89%. PCA pair/start83.61/89.44%; raw goal90.83%. Whole-cue joint-gain tail8/21 does not establish robust superiority. |

Both use label-conditioned cross-session pseudopopulations and historically exposed source pools. Three seeds are computational variation, not independent biological replications or confidence intervals. Original failed verification attempts remain retained; corrected replay changed no fitted artifacts or tolerances. AI review and numerical replay are QA, not laboratory verification of biological assumptions.

### Interpretation learned in this discussion

- Raw endpoint features are standardized100-ms spike counts, not unprocessed voltage. A bin has195 inputs; the first-second whole-cue view concatenates ten bins into1,950 inputs. PCA/CEBRA use8 coordinates/bin,80 inputs for whole cue. No temporal averaging is implied.
- Readouts are separately trained by target, representation and window. Same-window curves are not frozen temporal generalization.
- PCA plus logistic is a constrained linear predictor in the original features. Its advantage can be consistent with useful regularization or retained task-relevant variance; it does not uniquely diagnose CEBRA overfitting or irreversible information loss.
- CEBRA-Time's temporal objective is not endpoint classification. The encoder is frozen before the readout, not trained end-to-end from its errors. Equal latent dimensions or logistic C do not equate objectives or effective capacity.
- A chosen latent dimension is not an estimate of biological dimension. Shared encoder weights or cross-phase readout transfer do not prove shared geometry, intention or rotation.

## Proposed sequence for the new session — not executed

1. **Define the question before choosing another model.** Resolve the lab's meaning of observability, target semantics, independent unit, primary metric, meaningful effect, comparator, nuisance controls and allowed claims. Use existing source/support audits; do not rebuild the whole pipeline. Resplitting exposed sources does not restore confirmation. Whole-session holdout is not plug-and-play when neuron identities differ.
2. **Consider within-cue temporal generalization first.** Existing per-bin classifiers/features can support a train-time × test-time matrix without new encoder/readout fits. Freeze the encoder, input and readout scalers, decoder and decision policy for each row. Compare raw/PCA/CEBRA on identical sources; predeclare summaries/null handling rather than select bright cells. Verify compatible inputs and source lineage before execution. Existing-pool results remain exploratory and do not prove formal observability.
3. **Then design cue/navigation transfer if justified.** Compatible windows, target meanings, source-safe splits and within-phase references are required. Endpoint development-navigation features were not extracted in the completed study; do not pretend cross-phase evaluation exists or obtain those features without separately authorized preparation. Freeze the prediction pipeline within each encoder; never transfer decoder weights directly between independently fitted latent coordinate systems.
4. **Only then consider a bounded sampling-robustness arm if it answers the lab's question.** Unit subsampling of a pseudopopulation measures robustness of that condition-level assay, not observability of a simultaneous whole-hippocampus network. Refit requirements, cohort/support changes, dimensions and budget need a separate explicit design.

Do not automatically run this list. The next session starts with clarification and a bounded proposal. New biological fits or expanded raw-data access require explicit authorization and independent prefit review. Even a no-fit temporal reanalysis is future work, not an already completed deliverable of PR15.

## Carry forward / do not reopen

- Preserve training-only learned transforms, source-before-assembly splits, masks, provenance, nulls and appropriate source-aware uncertainty from the [analysis contract](analysis-contract.md). Pseudopopulations remain valid for condition-level questions; they do not restore simultaneity or missing cross-session covariance. A simultaneous195 recording is not a prerequisite for that lane.
- No locked outer-test neural access, source-pool relabeling as pristine testing, automatic fitting restart, or publication of private arrays/models. Do not infer source/animal independence from seed, bin or synthetic-row counts.
- The [September24 decoder study](reports/cebra-decoder-autoresearch-20260924.md) and [hyperparameter diagnosis](reports/cebra-hyperparameter-diagnosis-20260924.md) already tried kNN/RBF and regularization changes on the older path cohort without robust CEBRA rescue. They are not endpoint-specific tests, but they are not an untried next step either. Do not launch another broad decoder/objective/architecture sweep by default.
- Read [workspace/recovery](workspace.md) before Git or runtime changes. Start from updated `main` after verifying PR15's merged status, using this canonical checkout; preserve the three existing review worktrees and all ignored artifacts.
- Original October5-author-dated commit `712744c` and endpoint commit `724108a` must remain in history via a merge commit, not a squash/rebase. Merge authorization does not authorize branch/worktree/data deletion or any new experiment. Local integration receipts live under `outputs/pr15-merge-20261009/`.

Useful methodological references: [CEBRA paper](https://www.nature.com/articles/s41586-023-06031-6) and [official decoding example](https://cebra.ai/docs/demo_notebooks/Demo_decoding.html). Neither establishes formal hippocampal observability for these recordings.
