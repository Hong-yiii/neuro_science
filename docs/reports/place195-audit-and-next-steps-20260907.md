# Place195 audit guide and alternatives to forced pseudopopulations

Status: documentation of completed exploratory work and a proposed next step, not a new fitting stage. The original holdout is not pristine. This guide preserves the earlier inline audit instructions without depending on temporary cmux URLs.

## What is portable in this repository

- [Professor-facing HTML](../professor_updates/place195_v6_v9_20260906/place195-v6-v9-professor-methods-results-validity-20260906.html): download and open locally; figures and styling are embedded.
- [Full V6–V9 teaching/audit report](place195-v6-v9-autoresearch-20260906.md): reasoning, results, commands, failed attempts and provenance.
- [CEBRA/data-volume literature comparison](cebra-data-volume-comparison-20260907.md): distinguishes archive size, same-session population size, usable contrasts and independent observations.
- Analysis code and tests under `scripts/`.

Raw lab data, source/pseudo arrays, checkpoints, runtime environments, detailed output receipts and temporary browser views remain **local and ignored by Git**. Links into `outputs/`, `scratch/` or `/tmp/` in historical documents are local provenance references, not downloadable GitHub artifacts. The self-contained HTML is the portable figure-bearing report. Recorded analysis HEADs and dirty-state descriptions are historical, not claims that those runs were performed at this PR's commit.

## Audit in this order

For each finding, trace **claim → metric → predictions → feature construction → source identity → behavioral definition**.

| Step | Read | Challenge |
| --- | --- | --- |
| Question | [Research questions](../research-questions.md), [analysis contract](../analysis-contract.md) | Is the target path information beyond endpoints? Does the observed data satisfy the claimed unit of analysis? |
| Provenance | [Dataset card](../dataset-card.md), [import audit](../../notes/data_inspection/place195_all_sessions_import_20260830.md), [latest transfer audit](../../context/2026-09-06-place-data-transfer-audit.md) | Check clocks, cue windows, cell selection, marker semantics, recording groups and unavailable controls. The removed eight-unit supplement is not part of the dataset. |
| History | [Previous student analysis](../../context/previous-student-analysis.md), [earlier flow](../prospective-path-research-flow-review.md), [V5 note](../../notes/data_inspection/place195_graph_path_baseline_v5_20260901.md) | Targets and evaluation objects changed. V5's untouched-test statement is historical, superseded by the early V6 exposure. |
| Current findings | [V6–V9 report](place195-v6-v9-autoresearch-20260906.md), especially Appendices C–F | Separate predeclared specifications, diagnostics, accepted runs and superseded attempts. Do not select a favorable seed, bin or metric after inspection. |
| Support and transformations | [V6 code](../../scripts/place195_v6_graph_support_audit.py), [V7/V8 code](../../scripts/place195_v7_v8_neural_experiments.py) | Inspect `panel_cells`, `assemble_pseudo`, masks, time bins, train-only scaling/PCA and source reuse. Does construction require the future label? |
| Evaluation | [Split access](../../scripts/place195_split_filtered_access.py), [V8b/V9 code](../../scripts/place195_v8b_v9_cebra.py) | Check trial boundaries, source-aware nulls, matching observed/null pipelines, metric calculation and the distinction between training loss and validation performance. |

The accepted local run root is:

```text
outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/
```

Within it, inspect `audits/holdout-exposure-audit.md`, the initial and final review files, `final_report_manifest.json`, and the final V9 directory **`v8b-v9-cebra-final-20260905T224554Z`**. Its `v9_cebra_metrics.csv`, `v9_cebra_predictions.csv`, `v9_null_pvalues.json` and per-fit loss traces are under `v9/`; the selection-aware bin null is under `v8b/`. Do not pool superseded directories with this accepted run.

## Runnable verification on the data-equipped checkout

Read [the verification helper](../../scripts/verify_place195_v6_v9_artifacts.py) before executing it. It requires the existing local accepted artifacts and research environment; a code-only clone is insufficient.

```sh
cd /path/to/neuro_science
scratch/v6-v9-runtime/bin/python scripts/verify_place195_v6_v9_artifacts.py
```

The helper checks report/code/source-tensor hashes, 52 final fit records and 52,000 saved loss rows, and saved checkpoint-reload parity receipts. It independently recalculates all 24 observed CEBRA train/validation metric rows from predictions, then runs eight selected non-fitting software tests. It does **not** reload checkpoints, refit models, read the raw importer/test table, validate laboratory metadata or certify biological conclusions. Do not use Python's `-O` option: the checks use assertions.

The historical 26-test receipt has a different scope. Eight rerun tests are not eight additional scientific replications. Reproducing model fitting is a separate operation requiring the recorded environment and a fresh output directory; never copy an accepted output destination into a new run.

## Follow-up audit findings retained, not erased

1. **Mixed-split metadata access:** one follow-up scout, despite a saved-artifact-only instruction, materialized the original importer trial table to count rows/source IDs/sessions and counted split assignments. It did not compute test endpoint/path/neural statistics or fit a model. Its blanket statement of no test-containing-file access was rejected. Read-only is not equivalent to split-safe; future delegation needs an enforceably restricted artifact set.
2. **HTML identity drift:** the on-disk professor HTML was reformatted after release. Normalized markup/text-node content and attributes, including embedded images, matched the release copy; browser-parsed CSS and non-whitespace body characters matched. The responsible formatting process was not independently established. Old HTML and receipt were preserved; the current receipt records the formatted version instead of silently claiming byte identity.
3. **Literature corrections:** two researcher-supplied PMC links pointed to unrelated articles. They were rejected; the Truccolo reference below uses the verified PubMed record.

Detailed follow-up scope, failure/success logs and HTML reconciliation receipts remain under the local run root's `audits/`, including `followup-audit-scope-and-corrections.md`, `followup-verification.log`, and `professor-html-format-reconciliation.json`. These corrections do not change the accepted numerical results or restore an unexposed holdout.

## What is actually lost through the current design?

The archive contains 195 selected units across 58 sessions and 23,901 imported source trials. That is not a dense simultaneous population or a training-set count. The selected endpoint/component contrast contains 660 development behavioral sources; the primary neural panel uses 29 cells, seven sessions and 104 sources (82 train, 22 validation). The relaxed panel uses 40 cells/11 sessions/146 sources; the strict panel uses six cells/one session/11 sources.

The reduction combines behavioral eligibility, a fixed endpoint contrast, neural availability and repeated-support/common-panel requirements. It cannot all be attributed to pseudopopulation assembly, nor has it been shown to cause the nonpositive model result. Excluded observations were not deleted. Synthetic replacement increases row count without increasing independent biological evidence.

## Proposed next step: real observations before another architecture

**First perform a no-fitting, session-local support audit within the existing 195 selected units, without requiring a global common panel.** Classify observations usable for baseline estimation, conditional path association, and real-trial held-out decoding. Verify recording groups before population claims. More endpoint pairs help only where path variation remains beyond a sufficiently flexible endpoint-pair baseline.

Then consider, in order:

1. **Per-unit encoding and supported per-session decoding.** Model observed cue counts with exposure and appropriate endpoint/context controls; use unit/session effects and partial pooling only where supported. Encoding association is not automatically operational decoding. For decoding, preserve one real trial per row and aggregate held-out performance improvements across sessions, not fake population vectors. Do not average signed neuronal coefficients and interpret cancellation as absent information.
2. **Shared latent models with session-specific mappings.** LFADS dynamic stitching is a relevant precedent: separate readin/readout mappings share a generative model. Its demonstrated alignment used condition-averaged PCA and must be training-only in our design. A bidirectional encoder must receive cue-period input only, not later navigation activity. Shared latent structure does not establish unobserved simultaneity.
3. **Larger multi-session models only after support checks.** POYO/NDT2 show how heterogeneous recordings can share models without fixed neuron correspondence. Their data regimes do not establish effectiveness on our sparse selected-unit cohort or a universal minimum sample size.

If expanding endpoint coverage, do not reuse the current `source_level_shuffle` unchanged: it groups by split/session because its input already contains one endpoint pair. A broader analysis needs a defensible conditional null. One-class/endpoint-confounded sessions do not gain identifiable path effects merely through partial pooling.

### Targeted reading

- [Truccolo et al. 2005: neural point-process/GLM framework](https://pubmed.ncbi.nlm.nih.gov/15356183/).
- [Aarts et al. 2014: multilevel analysis for nested neuroscience observations](https://www.nature.com/articles/nn.3648). Parent check was abstract-level; full text was paywalled.
- [Pandarinath et al. 2018: LFADS](https://pmc.ncbi.nlm.nih.gov/articles/PMC6380887/), especially Fig. 4 and Methods 1.9. Demonstration: 44 sessions with 24-channel arrays in a motor task, not our 1–8 selected units/session.
- [POYO primary proceedings](https://proceedings.neurips.cc/paper_files/paper/2023/hash/8ca113d122584f12a6727341aaf58887-Abstract-Conference.html): heterogeneous-unit architecture; much larger pretraining regime.
- [NDT2 primary paper](https://proceedings.neurips.cc/paper_files/paper/2023/file/fe51de4e7baf52e743b679e3bdba7905-Paper-Conference.pdf): multi-context neural pretraining, not a proven remedy for this dataset.

No non-pseudopopulation model was fitted by this follow-up review. The recommendation is to preserve real trial–neural links and share parameters where justified, not to invent missing observations or expand the selected-cell scope silently.
