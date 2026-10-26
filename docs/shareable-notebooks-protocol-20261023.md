# Fresh notebook real-data protocol — October 23, 2026

**Frozen scientific scope before neural reconstruction/fitting.** Owner requested
end-to-end implementation and real-data execution under the approved
[north star](notebook-package-plan-20261023.md). Independent protocol review accepts
this design in principle; implementation/data-path review and resource benchmark must
pass before execution. [Execution ledger](shareable-notebooks-execution-20261023.md)
records actual status. This is a new exploratory computational assay, not a replay
or independent confirmation of the historical endpoint study.

## Question, units and claim ceiling

Can the new supplied-input package/notebook workflow freshly reconstruct a
condition-matched source population, fit PCA/LDA/CEBRA readouts, and compare full and
reduced training-source pools on identical development assemblies?

Provenance unit is a real source trial; target derivation also uses its predecessor.
Trials remain nested within sessions and serially dependent. Synthetic rows, bins,
units and computational seeds are not independent biological replications.

Primary cohort: **metadata-selected, historically exposed, directly contributor-disjoint
27-unit/10-session pseudopopulation panel**. It differs from the historical195-unit
panel. Development assignments remain unchanged but its membership is restricted.
No matched score comparison to the historical panel, causal attribution to embargo,
pristine test, independent generalization, biological CI/p-value, sample-efficiency
law, simultaneous dynamics, path-beyond-endpoints or mechanism claim is permitted.

## Input/access boundary

Only explicitly supplied imported INPUT files are allowed. Paths below identify the
local inputs; portable notebooks take a manifest, not these hardcoded directories.

- `I=outputs/prospective_path_first_run/place195-all-sessions-20260830-v4`
- `S=outputs/prospective_path_first_run/place195-splits-20260830-v3`
- `E=outputs/start-goal-cebra-20260907`

| Required input | SHA256 |
| --- | --- |
| `I/trials.csv` | `aa0dc3e402a8a3c3c0fa355c0342f5061314f2c571d2f96dfaecc94e69fcd223` |
| `I/units.csv` | `fca36f2927af13a10db3df2312ad51689cf9c7ec28740bb0682b40918f65368f` |
| `I/cue_counts.csv.gz` | `e355af169b661650c4cc02aeaafd96a1443698afa67648a8b888a3adeee4c7b0` |
| `I/cue_spike_events.csv.gz` | `76cd94486604fdbc3746de9eba4835bb8e2a035eb4071531f59ee498f279ab24` |
| `S/source_trial_splits.csv` | `b0ef8cce43c79d9e2b1ae0a804c7d48fefeb92469670f3031485d0009fb10ff3` |
| `E/source_splits.csv` | `ab158a23c4f3cc9dd46f27710c355fee74965a32892c6e662d2d4a29dd628bf8` |

These last two tables are frozen source assignments, not fitted results. Re-derive
eligible targets and regenerate the original inner assignment rule (seed20260907)
from metadata, comparing to the frozen assignment map before selecting the new panel.
No old tensor, pseudorows, standardized arrays, models, predictions or scores are
required or loaded. Historical imported timestamps/selection/preprocessing remain
inherited; this does not re-read raw acquisition files.

Whole-file hashing and sequential traversal of mixed-split gzip streams are allowed
and must be disclosed. **Gate source and unit identities before numeric neural-field
interpretation/retention.** Interpret only exact selected source/unit pairs, all within
original outer train; count accepted/rejected rows without examining rejected neural
values. Do not claim physical non-reading of compressed bytes. No outer validation/test
neural interpretation, navigation/path tables, recursive artifact verification, embedded
raw-file path access, credential access or downloads.

Manifest/IDs/source tables remain private. Public figures use aggregates and pseudonymous
block/source labels; no private path, raw session/unit/source identifier or row-level
prediction is published. Code licensing/public upload remain separate decisions.

## Target derivation and metadata selection

Reproduce original eligibility from outer-train trial metadata:

- Current and predecessor are successful, adjacent, same-session and QC-clean.
- Current cue duration is1.0–1.5seconds.
- Previous/current marker minor digits derive start/goal; unequal IDs1–6 yield30pairs.
- Ripple/Unity/Eyelink triplets and importer-derived endpoint fields agree.
- Preserve all exclusions and target provenance. Marker meanings and unit simultaneity
  remain unverified; label the table derived/provisional, not measured ground truth.

Reproduce15,553 eligible sources,12,288train/3,265development,195units/58sessions,
all original outer train. Original inner assignment randomizes within session/pair;
regenerate with its exact seeded ordering and verify equality, not a new split.

For each eligible source define contributors `{current_source, previous_source}`.
Missing or invalid predecessors fail. Freeze the union of contributors of **all3,265**
original development examples. Remove any training example with an intersecting
contributor set. Then select exactly the sessions supporting every30pair with
at least2 remaining train and1development source; retain all their selected units.
Do not tune the panel using neural values or model scores.

Required metadata totals (must be reproduced or reconciled before proceeding):

- Original directed predecessor edges: train→train9,226; train→dev2,441;
  dev→train2,465; dev→dev658;763predecessors outside eligible cohort but in outer train.
- Full development contributor union:5,872IDs.
- Embargo removes4,427training sources, leaving7,861 globally.
- Global session/pair pools:13zero,73one,1,654at least2 training sources.
- Complete selected panel:10sessions,27units,1,415training/551development sources.
- Final union(train contributors) ∩ union(dev contributors) is empty.

Original metadata distributions and the selection waterfall appear in notebookA.
Excluded sources' neural values are unnecessary. Remaining long-range serial/session
dependence, inherited exposure and place-selected units remain limitations.

## Fresh measurement reconstruction and assembly

From accepted event/count rows, freshly bin cue-relative spikes into ten100-ms
half-open bins `[0,1)` seconds using the maintained binning rule and inherited CSV
serialization. Check finite times, duration/exposure consistency across units,
full-window event/count conservation, duplicate count rows and exact unit/block joins.
Record omitted tail spikes. Observed zeros remain zero; off-block measurements remain
NaN/masked. Every selected unit in a source's block must be observed with full exposure.

Assembly matches ordered pair, copying one intact source block's units×allbins per
session. Use16training and8development rows per pair (480/240), sampling with replacement.
Use fixed development assembly seed0 across observed seeds, models and source budgets.
Verify exact value/target/exposure/lineage equality and contributor separation.

Source-pool intervention: full versus a deterministic nested `floor(n/2)` selection
within each session×effective-pair training pool. Full pools must all have at least2;
otherwise stop, do not add an unreviewed singleton fallback. Use fixed subset seed20261023
across observed training assembly/optimization seeds0,1. Preserve the unit panel, all
classes, binning, pseudorow budget and development assembly. Report eligible/retained/
actually used/unused/repeated sources and realized reduction; not an exact50% measurement
reduction. Reassemble and refit every learned stage for each budget.

## Models, readouts and controls

Whole-cue prediction only; no ten-bin readout factorial, navigation or parameter search.
Three separate targets: pair30/start6/goal6, derived from the effective matched pair.

- Raw: training-only pooled-bin normalization, unit-major flattening.
- PCA: training-only pooled-bin normalization and sklearn full-SVD PCA8, time-major
  flattening. Require numerical rank≥8; no implicit padding or dimension change.
- CEBRA: cue-only Time, existing row-uniform/within-row adjacent-bin sampler;
  offset1-model, hidden32, output8, temperature1, Adam lr0.0003, batch256,
  exactly1,000updates. Record losses, native pairs and realized sampling exposure.
- Raw/PCA/CEBRA readouts: separate training-only StandardScaler + logistic regression
  per target, `C=0.01`, `max_iter=2000`, lbfgs. Stop on nonconvergence.
- LDA: raw supervised SVD-LDA classifier with training-only readout scaling, not an
  unsupervised or dimension-matched embedding comparison.

Two observed computational seeds0,1; full/reduced initialization and sampler seeds paired.
No biological-replication interpretation. One permutation seed50000 shuffles **joint pair
labels at source level within retained session×split** before assembly, preserving
observed provenance separately. Its reduced pools are nested under the effective labels.
Use computational seed0 and full/reduced budgets, with identical development assembly
within that diagnostic world. This breaks alignment, not a biologically exchangeable
null; no tail probability or significance interpretation.

Preflight invented-data known-signal and constant/no-signal checks. Then biological fit
accounting is fixed:

| Notebook | Fits |
| --- | --- |
| A construction | 0models |
| B PCA/LDA:2observed seeds×2budgets | 4PCA,24logistic,12LDA |
| C CEBRA:4observed+2permutation configurations | 6CEBRA,6PCA,54logistic |
| Total (excluding scalers) | **6CEBRA,10PCA,78logistic,12LDA** |

Each notebook reconstructs from supplied inputs independently, not another notebook's
outputs. Show accuracy, balanced accuracy, macro-F1, log loss, count and normalized
confusions, and training/development gaps. Uniform BA1/30 or1/6 is a reference, not a
significance threshold. Refitted raw/PCA references in notebookC are included in counts.

## Execution, verification and stopping

Before biological fits:

1. Independent source/target/assembly/model code review; fix findings.
2. Fresh-kernel synthetic notebooks and installed-wheel validation outside checkout.
3. Shape-matched invented27-unit480/240row benchmark, projected total including
   preparation, notebooks, artifacts and fit-blocked verification, with25%headroom
   inside90minutes; final input/code/config hashes pinned after fixes.
4. Record immutable metadata selection/input hashes and current resource sample.

Real run: CPU, two numerical threads, one kernel/fit process at a time, aggregate
owned memory≤6GiB with no swap reliance, overall90-minute deadline, output≤2GiB.
Use an owned bounded task/transient scope; register its lifecycle before launching.
No automatic retry/resume, no unrelated process/service changes. Abort on unexpected
state, numerical failure, nonconvergence, missing support, leakage, altered manifests,
wrong evaluation lineage, unexpected fit count or resource/deadline violation.

Fresh private outputs, mode0700directories/0600files; no accepted-result overwrite.
Save sufficient fitted states/features/predictions/lineage for fit-blocked replay of
this new run, authenticate before loading trusted joblib/checkpoints, verify metrics
and figures. Record package/code/config/input identities, device/threads/seeds, fit
counts and observed resource use. Independently review results and rendered-output
privacy before any public aggregate promotion. Preserve failures and explain them.
