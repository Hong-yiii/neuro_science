# Complete experiment notebooks — November 15, 2026

## New owner request and scope

After the completed study and `/teach max`, Hongyi requested notebooks following
the main course's end-to-end principle, executed and populated with real data,
explaining today's experiments completely. The owner also explicitly requested
adding the completed work to a PR. This supersedes the earlier no-further-fit and
no-publication checkpoint for this bounded notebook follow-up only. No merge is
requested. The disposable teaching HTML remains outside the repository.

Classification: **exploratory study reproduction for a complete notebook handoff**.
The operational question, fixed nine classes, six arms, model/readout settings,
source splits/embargo, three observed seeds and five diagnostic worlds remain the
[frozen November14 protocol](protocol.md). No new ablation, tuning axis, source
split, label target, source recording or spatial-field study is added. A fresh
48-case execution provides actual training outputs in the richer notebooks; it is
not additional biological replication and is not pooled with the accepted run.

The two notebook files are dated November15 and live together under
`experiments/source_reuse_width_20261114/walkthrough_20261115/`. Original source and
executed notebooks, `complete-01/`, all failures and the accepted report remain
unchanged. New outputs use a fresh root beneath
`outputs/source-reuse-width-notebooks-20261115/`.

## Notebook flow

Each notebook follows question → design → real source reconstruction → paired
assembly → training → scoring → controls → errors/trajectories → interpretation.
The first planned case is exposed in separate cells, using the same fitting
helpers as the accepted implementation:

1. Inspect/authenticate compact source metadata, marker-derived labels and the
   global current/predecessor embargo; distinguish measured from derived objects.
2. Reconstruct the real source tensor; show aggregate count/missingness/support
   diagnostics without printing raw source/unit identities or neural arrays.
3. Build the exact paired plans, display anonymous block recipes and realized
   multiplicities, and materialize the first case (B2 for reuse; Wmid for width).
4. Fit training normalization and PCA explicitly, check their arithmetic against
   fitted transforms, and explain per-bin versus whole-cue feature dimensions.
5. Fit Time and native multisession CEBRA explicitly, display their real network
   structure, actual update/loss summaries, supervision and pooling differences.
6. Fit all four readouts and three heads, show logistic forward-arithmetic checks,
   SVM margin semantics, count/normalized confusions and whole-cue metrics.
7. Save and fit-blocked-reload that first case, then finish only the remaining
   cases. The staged first case is never refitted. B3 remains an authenticated
   bridge fitted once by the first notebook.
8. Collate every observed/control score, paired contrast, class error, source-use
   diagnostic, learning curve and observed cue trajectory. Explain actual results
   and their limits within the notebooks, not only in an external report.

The local staging/persistence code stays inside this experiment. It reuses the
maintained numerical fit/transform/metric helpers and preserves their settings;
there is no new shared-package API or scientific model implementation.

## Prospective execution and acceptance gates

- Independent scientific/code review before biological fitting.
- Invented equivalence check: compare the staged first-case path against the
  accepted `population_models.train_case` on the same invented full-width inputs,
  seed and configuration. Match transforms/predictions/metrics/source tables and
  instrumented fit/update counts. Exact checks cover plan/row identities, labels,
  predictions, confusion counts, source tables and complete metric records.
  Continuous numeric arrays use rtol=atol=1e-7; existing serialized encoder
  reload checks retain1e-5 and readout scores1e-7. Wall times and serialized byte
  hashes are excluded from cross-implementation equality. The staged branch
  executes the exact seven fitting/arithmetic/diagnostic notebook cells; teaching
  arithmetic does not fit extra models. Both cases are software checks, not
  biological evidence. Expected combined invented budget:102fits,4,000updates.
- Bind benchmark and preflight receipts to the complete actual source,
  configuration, notebook code, runtime and input identities. All48 real plans
  must pass source/nesting/projection/rank checks with fitting blocked. Rank≥7.
- Run two fresh kernels under hard4GiB memory, zero swap, two CPU cores and a
  three-hour total limit. Use the existing read-only runtime. Require conservative
  headroom48×max(reference_seconds,staged_seconds)×1.25+900<10,800.
  A no-fit mock checks both immutable kernels, the exact48-case schedule, first
  cases once, the eight-case B3 bridge and staged failure accounting. Nine stage
  checkpoints per notebook preserve actual counts across cell boundaries. Fresh directories only; preserve
  failures and stop rather than automatically retry biological cases.
- Fresh biological budget remains48cases,2,448fit calls excluding scalers and
  96,000updates. The first notebook fits32cases; the second fits16new cases and
  references8authenticated B3 cases. Validate the richer notebook's actual calls
  and complete case receipts, not just plotted summaries.
- Reuse the full numeric/lineage audit with explicit expected notebook sources
  and filenames for this execution. Authenticate every state/receipt and verify
  every fitted encoder/readout on both splits under fit guards during the run.
- Compare the new saved aggregate scores/predictions with the accepted execution
  to detect implementation drift. Authenticate the complete accepted receipt
  before comparison. Require exact case/lineage/metrics/confusions/predictions
  and continuous arrays within rtol=atol=1e-7; no post-result tolerance relaxation. A difference must be explained before replacing
  any conclusion; do not select whichever execution scores better.
- Independent numeric, scientific-claim and publication/privacy review before
  publishing the notebooks and documentation. Make aggregate outputs readable
  without private fitted states. Do not publish raw feature arrays, fitted model
  states, full source-lineage manifests or private/unrelated files.

## Publication and preservation

The authorized PR contains the experiment implementation, the two complete
executed notebooks with reviewed aggregate outputs, their source/reproduction
instructions and supporting documentation. Existing merged PR27/28 are history;
if this branch has no open PR, create a draft for the completed unit. No issue
comments, reviewer requests, merge, release, new license or unrelated change.

Preserve the pre-existing sampling-code edit and current-state notes. The sampling
edit is whitespace-only relative to Git; actual source hashes and dirty state
still belong in the run receipt. It is not included in the publication diff.

Status: implementation and prefit review in progress. No new biological fit has
started for this follow-up at this checkpoint.
