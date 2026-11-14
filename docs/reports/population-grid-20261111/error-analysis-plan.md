# Saved-result error analysis — November11 follow-up

Classification: **post-hoc exploratory descriptive analysis**, authorized by the
owner's request to add confusion matrices and examine removed classes/sessions
and source reuse inside the research handoff. This is not a new fitting protocol.
The original run and its first interpreted deliverables remain unchanged.

## Question and evidence

Do classes removed by the metadata-selected smaller tasks already have different
recall in the larger task? Within a fixed task, how do class errors relate to
source support/reuse, and which development predictions change when the sampling
policy or session roster changes?

Read only receipt-authenticated configuration, confusions, metrics, source-support
and usage tables, saved prediction/truth arrays and development lineage from
`outputs/population-grid-20261111/real-01/`. Receipt SHA256:
`6f070f514d98898df1121e6074e1ffef66e662963902706cab62032a85486869`.
No model loading, biological replay, new fitting, raw-spike reconstruction or
hyperparameter selection. Individual predictions and original source identifiers
are used only for reconciliation; the handoff contains aggregate outputs.

The observed family is all81cases: nine class×roster configurations, three
sampling policies and three computational seeds. Every raw/PCA/Time/native
feature pipeline and logistic/SVM/kNN/LDA decoder is included. Display pair,
start and goal confusions independently; these are separately fitted heads.
Existing control confusions may be displayed only where actually fitted.

## Declared calculations

1. Show counts and row-normalized confusion matrices, explicitly true rows versus
   predicted columns. Retain individual seeds. Training matrices are recomputed
   from saved training predictions; development matrices must exactly match the
   original confusion records. Do not pool seeds as independent evaluations.
2. Compare30→20,30→15 and20→15 class lists. Within the source task, report macro
   recall separately for classes later retained and deleted, plus errors on retained
   classes directed into deleted labels. Report destination recall only for retained
   classes; removed classes are **not evaluated**, never assigned zero recall.
   No synthetic rows are paired across class tasks. Population, competitors, source
   subsets and construction change together, so this is descriptive selection
   sensitivity, not the causal effect of deleting classes.
3. For each observed pair class, record training/development recall, support,
   used sources, block draws and extra-draw fraction `(draws-used)/draws`.
   Original available support comes from the authenticated source-support table
   and must match F16 availability. U2/R16's policy pools contain only two selected
   sources per session/class and must not be called all available sources.
4. Compute average-tie-rank Spearman associations between per-class development
   error and training/development reuse, total available training sources and
   harmonic per-session training support, separately within each fixed task,
   roster, policy, encoder, decoder and seed. Report K and undefined reasons if
   either vector is constant. No p-values, row-based confidence intervals,
   biological replication claim or pooled-seed correlation. U2 reuse is always0
   and R16 always0.875. Under F16, reuse equals `1-support/(16*sessions)`;
   its association is the sign reversal of total-support association, not separate
   evidence isolating reuse from coverage.
5. Compare U2→R16, R16→F16 and U2→F16 within K/roster/seed. Compare roster
   removals S100→S67, S100→S33 and S67→S33 within K/policy/seed. Before pairing,
   verify identical row order, pair labels and source IDs across policies, or
   exact shared-block lineage projections across rosters. Report per-pair-class
   both-correct, wrong→right, right→wrong and both-wrong counts, retaining the
   common eight development rows/class. Counts are dependent synthetic rows.
   Roster effects involve a whole session group plus pipeline refitting; no
   individual session is assigned causal blame or an invented excluded-source score.

## Interpretation and delivery

Independent protocol review accepted this scope with the above safeguards before
implementation. Independent code/numeric/claim review is required before interpreting
the new results. Retain negative findings, unidentifiable correlations, all seeds,
all feature/readout families and explicit source-versus-row denominators.

The outcome is a versioned handoff with an interactive matrix explorer, saved
figures/tables and an added post-execution notebook section. Preserve every
original executed cell/output; new descriptive outputs are labelled separately.
Update the disposable teaching artifact without changing historical execution
evidence. No issue edit, push, merge or additional experiment is implied.
