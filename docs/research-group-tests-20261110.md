# Research-group tests: evidence review and proposed work — November 10, 2026

**Subsequent owner decision:** the owner authorized fresh model training, smaller
start–goal panels, larger populations and source-reuse controls, and requested all
results, a report, trajectories and an executed notebook. The resulting bounded
[execution protocol](source-support-protocol-20261110.md) supersedes this assessment's
planning-only status for that study. The assessment below remains the pre-run record.
The study is now complete; see the
[interpreted results, report and executed notebook](reports/source-support-ablation-20261110/README.md).

**Status: assessment and proposed work, not a frozen execution protocol.** Hongyi
asked to review the latest notebook evidence and the issues from the previous
Monday, then explain what can be tested and how to work on the issues. This pass
read public issues, tracked source/docs/notebooks and three public metadata files.
It performed metadata consistency checks and a data-free report self-test. It did
not access private results, load models/predictions, reconstruct neural arrays,
execute scientific notebooks, fit models or change GitHub issues.

## Which issues and which evidence?

GitHub inspection on November 10 found the relevant Monday batch on **November 2**:
[#25](https://github.com/Hong-yiii/neuro_science/issues/25) and
[#26](https://github.com/Hong-yiii/neuro_science/issues/26) were opened that day;
[#24](https://github.com/Hong-yiii/neuro_science/issues/24) was opened November 1
and updated November 2 with the minimum-five-source sensitivity.
[#23](https://github.com/Hong-yiii/neuro_science/issues/23), opened November 1,
is explicitly deferred. All four are open, labeled `enhancement` and
`needs-triage`, with no comments. No newer issue was returned by the repository
search for issues created since October 26. These dates resolve the likely intended
batch without treating “last Monday” as an instruction to invent a November 9 batch.

There are three different evidence artifacts:

| Artifact | What was collated and verified | What it can establish |
| --- | --- | --- |
| [Historical endpoint walkthrough](../report/endpoint_walkthrough.ipynb) | October 19 saved-input replay of the October 7 **195-unit/58-session** study; 14 executed code cells, six CEBRA encoders, three PCA states, 495 fitted readouts and 990 split-level score rows | An inspectable chain from authenticated standardized cue inputs through fitted transformations, predictions and aggregates. Original assembly, scaler fitting and controls remain inherited; no new fitting occurred. |
| [Seven-chapter course](../notebooks/README.md) | October 26–27 teaching source, invented executed arithmetic and 14 public historical figures | Research explanation and runnable implementation. Current practical A/B/C notebooks have **empty outputs**; their current biological model grids were not executed. Historical figures keep their original cohorts. |
| [27-unit report](reports/cebra-27unit-notebooks-20261023/README.md) and [offline HTML](reports/cebra-27unit-notebooks-20261023/report.html) | November 2 presentation of the accepted **October 23 27-unit/10-session** run: authenticated saved notebook text/PNGs, 66 unique scalar rows and 25 figures | Evidence for that run's whole-cue full/reduced-source comparison and one permutation diagnostic. It is output extraction, not a new model run or verification of current compact-source B/C numerics. |

The October 23 workflow freshly reconstructed supplied source inputs, assembled
condition-matched blocks, fitted train-only raw/PCA/CEBRA/readout pipelines and saved
private executed notebooks plus authenticated artifacts. Its accepted execution
included 6 CEBRA, 10 PCA, 78 logistic and 12 LDA fits, with 180 fit-blocked readout/split
replays. The November 2 renderer extracted 36 B and 54 C scalar summaries, reconciled
24 duplicate raw/PCA summaries, preserved 21 saved PNGs and made four aggregate charts.
That provenance chain makes the report reviewable; the notebook format alone is not
scientific validation. See the [protocol](shareable-notebooks-protocol-20261023.md),
[execution ledger](shareable-notebooks-execution-20261023.md) and
[report provenance](reports/cebra-27unit-notebooks-20261023/provenance.json).

GitHub confirms [PR22](https://github.com/Hong-yiii/neuro_science/pull/22) merged
November 2. The separate report [PR27](https://github.com/Hong-yiii/neuro_science/pull/27)
is open, not draft and not merged. Old issue references to “draft PR22” are stale.

The latest reported full-pool mean balanced accuracies over two computational seeds
are raw/PCA/CEBRA **16.88/13.33/17.08% for pair30** and
**64.58/59.58/51.88% for goal6**. They motivate retaining strong simple baselines;
they do not establish general CEBRA superiority. The existing full/reduced comparison
changes training-source availability while holding the 27 unit columns fixed. It
does not answer the proposed class-count or recording-unit-count questions.

## Recommended sequence

### 1. Issue 25: measure reuse before changing the model

**Question:** which session–condition source pools provide little distinct trial
diversity, and which unit columns inherit that reuse?

All 27 columns occur in every complete synthetic row. Sampling chooses a real trial
for a session, then copies its whole retained unit-by-time block. Units in the same
session therefore share the same reuse profile; they are not individually sampled
neurons. With 16 training draws per condition, a two-source pool has expected use
eight per source, while a ten-source pool has expected use 1.6. This expectation is
not a test of abnormal sampling or a feature-importance score.

Build a metadata/plan report for the exact 27-unit panel, observed training seeds
0 and 1, and the single fixed development seed 0. Start with full pools; keep the
reduced-source arm separate. Produce:

- Session × condition support/reuse heatmaps; eligible, used, unused and repeatedly
  used source counts; extra draws, maximum share and the complete distribution.
- A 27-row column-to-session lookup with shared profiles explicitly grouped.
- A worked source → session block → unit-column trace and within-class row-overlap
  summaries, separating shared blocks from exact whole-row duplication.

Reuse the semantics of `support`, `sample_plan`, `AssemblyPlan` and `source_usage`
in [pseudopopulation.py](../src/neuro/pseudopopulation.py). The existing APIs accept
`SourceData`/`Assembly`, which also hold neural arrays; a small metadata/plan counting
entry point is needed for a strict ID-only audit. Do not fabricate neural arrays
merely to satisfy those constructors. The current metadata-only compact inspector
also reads event/timing files; the narrower assignment-table route is sufficient
for frozen eligibility/support accounting, but cannot independently rederive QC.

Prefer an authorized plan export. If reconstructing an ID-only plan from public
metadata, preserve condition order, sorted block/source order, NumPy version,
sampling calls and seeds. Label it **reconstructed**; matching aggregate totals alone
does not authenticate row-by-row identity with a historical fitted run.

Completion checks: 4,800 training and 2,400 development block draws per seed;
per-pool counts sum to 16/8; zero-use eligible sources remain visible; same-session
units inherit identical profiles; contributors remain separated across splits.
Existing invented assembly tests already cover several invariants. Add only missing
zero-count/overlap arithmetic tests. This work requires no model fitting.

### 2. Issue 26: separate exclusions from prediction errors

There are two deliverables with different input requirements:

**Exclusion map, available from metadata:** retain all 58 sessions and explain which
session–condition pools fail the fixed support gate before/after the global
contributor embargo. The 48 omitted sessions have no model-error rate in the
27-unit evaluation. Original QC/behavior failure reasons require their recorded
provenance; the frozen assignment tables alone do not supply all those stages.

**Error association, requiring compatible saved records:** join each truth/prediction
to its authenticated assembly row, then its ten source blocks and issue 25's usage
table. Start with pair30 whole-cue errors by true class, then source participation
within class. Match raw/PCA/CEBRA by world, seed, budget, sources and evaluation.
Keep start/goal summaries supplementary and retain their own denominators.

The public report has scalar summaries and confusion PNGs, not a machine-readable
row-to-source prediction table. Code inspection of
[notebook_artifacts.py](../src/neuro/notebook_artifacts.py) shows that saved prediction
records also contain feature arrays, and saved bundles contain assembly arrays and
plans. The prediction payload does not carry explicit row IDs. A narrow authenticated
export must therefore verify the manifest's bundle association, row order, target
sequence, cohort and configuration before attaching row IDs. A same-length join or
matching labels alone is insufficient. Current private artifact availability was
not checked in this assessment.

Prepare that exporter against invented records first. Access to the original
bundled artifacts needs a separately scoped decision covering their actual contents;
it cannot honestly be called a metadata-only read. Export only the needed prediction,
class and lineage fields to a restricted local table, plus approved aggregates for
the report. Do not call `verify_artifacts` to obtain a “no-replay” export: that helper
loads encoders/readouts and performs forward replay. No new inference or fitting is
needed if the saved records can be authenticated.

For each source report appearances in all rows and in wrong rows, with the fraction
wrong among appearances. Reconcile correct + wrong involvement with total usage and
reproduce the accepted confusion/metric totals. A heavily reused source participates
in more errors mechanically. A constructed-row error involves ten session blocks;
it is not a prediction error of one real trial or evidence that one session caused it.
Begin with descriptive class-level comparisons, not row-IID significance tests.
If compatible records are unavailable, deliver support/exclusions and report the
error-lineage gap explicitly.

### 3. Issue 24: choose one controlled comparison

The advertised panels are feasible under **at least two training / one development
source per session × condition**, after the unchanged global contributor embargo:

| Fixed class list | Unit columns | Sessions | Eligible training sources | Development sources |
| --- | ---: | ---: | ---: | ---: |
| Current 30 | 27 | 10 | 1,415 | 551 |
| Proposed 20 | 108 | 32 | 2,998 | 1,218 |
| Proposed 15 | 140 | 41 | 2,917 | 1,181 |

This review reproduced those counts from the three public metadata files. Applying
**at least five training sources to these same class lists retains zero sessions**.
The issue's newly optimized minimum-five panels are different selections: 15 classes
can retain 14 columns/two sessions, and 20 can retain six columns/one session.
Those optimization results are inherited from issue 24, not newly solved here.

The research group must distinguish three questions:

| Question | Controlled test | Interpretation |
| --- | --- | --- |
| Do additional recording-unit columns help on a fixed task? | Freeze the 20-class/32-session panel, all source IDs and evaluation; compare metadata-selected nested 32 versus 108 columns, with 64 only as a prespecified sensitivity. Retain at least one column per session. | A more direct unit-budget comparison. Use fixed selection rules/repeats to expose dependence on the chosen columns. |
| Does additional condition coverage help a common readout? | Freeze the common 108-column/32-session panel; train encoders on the specified 15 versus 20 classes; train/evaluate a common-15-class readout on identical source assemblies. | The 15/108 bridge separates condition coverage from changing sessions/columns. Extra training-source and optimizer exposure must be controlled or explicitly treated as part of the intervention. |
| Do more real training trials per pool help? | Choose a fixed five-capable panel and compare prespecified nested two-versus-five source subsets, keeping development and unit/class identities fixed. | Source-budget sensitivity. The two-source arm needs explicit exploratory justification if five is otherwise mandatory. |

Recommend selecting **one** of these contrasts after the audit, rather than their
Cartesian product. The fixed-task unit-budget contrast is the cleanest first test
if the group's question is whether the narrow 27-column panel limits performance.
Its conclusion applies to the selected 20-class panel; it cannot explain the old
27-unit score causally. A direct 15/140 versus 20/108 comparison can describe two
practical designs, but changes task difficulty, sessions, columns and sources
together. Chance correction does not make their scores a controlled comparison.

Use matched raw + logistic, PCA + logistic and CEBRA + logistic; refit every learned
stage within each training arm. Report balanced accuracy, log loss, all class
confusions, source support and every declared seed/selection repeat. Freeze exact
rosters, primary target/contrast, exposure, tuning, controls, uncertainty/sensitivity,
fit counts and resource limits before any fit. Check source-safe inner-fold
feasibility if tuning is proposed. More synthetic rows or a new exposed-data split
cannot supply independent biological replication or a pristine test set.

The minimum-five policy remains **unresolved**: a preference question was sent during
this assessment. Until answered, both policy branches remain proposals; neither
threshold is declared scientifically sufficient or adopted for execution.

### 4. Keep issue 23 deferred; distinguish the longer-term usefulness test

Native multi-session CEBRA fits session-specific encoders with shared auxiliary
sampling and permits different feature counts. This is a different observation and
training design, as described in the
[official tutorial](https://cebra.ai/docs/demo_notebooks/Demo_hippocampus_multisession.html).
It requires a clear real-trial/transfer target, verified session provenance,
training-only alignment variables and per-session baselines. It is not a repair to
the present pseudopopulation benchmark and should remain a separate proposal.

The older [issue 18](https://github.com/Hong-yiii/neuro_science/issues/18) asks whether
CEBRA improves **frozen readout transfer across time**. This remains a useful eventual
criterion for CEBRA's added complexity, after source support is established. The
current 27-unit run has whole-cue readouts only: its fitted 270-dimensional raw or
80-dimensional latent readouts cannot simply be applied to single 27/8-dimensional
bins. A cue-time matrix on that panel needs separately scoped bin-readout fitting.
The historical 195-unit study has saved bin readouts, but using those is a different
cohort and separately scoped private replay. Same-window curves are not an existing
cross-temporal result.

## Proposed final artifact and completion evidence

Create a separate, executed **support-and-errors evidence notebook**, with an offline
HTML view, leaving accepted artifacts intact. Its sequence should be:

1. Exact question/cohort, source contracts and a worked construction trace.
2. Session/class support, per-source reuse and unit-column inheritance.
3. The separate exclusion map and, when available, authenticated error associations.
4. Metadata-feasible candidate panels and explicit infeasibility under stricter rules.
5. A claim/evidence ledger: executed checks, inherited results, missing inputs,
   unexecuted proposals, hashes, software identity and limitations.

Keep useful accounting/joins in small tested helpers and visible scientific choices
in the notebook. Export tables alongside figures, preserve every case and failure,
and bind artifacts to input/configuration/code identities. Independently review the
new audit and any subsequent experiment protocol before interpreting new analyses.
Any later fitted ablation should have its own execution receipt and results section;
availability tables or invented join tests must never stand in for model evidence.

## Checks performed in this assessment

- Inspected local revision `0c6e066858f054b65a7e777ae172bb6fd260b3c3`; preserved the
  pre-existing `_cebra_sampling.py` formatting edits and unrelated untracked notes.
- Verified these metadata SHA-256 values against issue 24:
  `manifest.json`: `8af267ca189a98a3bcc3c24e498259d36079e41402a6cf2fdb9a0d9e5291ed11`;
  `inner_splits.csv.gz`: `34fa1c5a0f5c6d9443d435c98ba64830c68f2792306172c12d53ad60792f219f`;
  `outer_splits.csv.gz`: `c42b2dd2bf184dca8f9ed86908d35f16caf40bd52b4221d17380a2156d1eee56`.
- A Python-stdlib check verified unique assignment IDs, outer-train membership,
  adjacent same-session predecessors and the union of all 5,872 development
  contributors. It reproduced 4,427 embargoed training sources, 7,861 surviving
  training sources, the three fixed panels above and their minimum-five
  infeasibility. No event, spike, sampled-plan, prediction or model files were read;
  eligibility/QC and the full optimization frontier were not independently rerun.
- Inspected notebook JSON execution state without executing cells: historical
  endpoint 14/14 code cells executed; practical A/B/C 0/13, 0/14, 0/14 with no saved
  outputs; invented arithmetic 7/7 and historical-study symbolic examples 2/2.
- Verified the public report renderer hash, all 21 saved-image hashes and the
  66-row public metric CSV count against tracked provenance. This is public-artifact
  consistency, not fresh authentication of the private original run.
- `python scripts/render_fresh_notebook_report.py --self-test` passed its invented
  scalar/parser/grid checks. No scientific inputs were accessed by that test.

No issue is closed by this assessment. Issue 25's detailed reuse audit, issue 26's
prediction join and issue 24's reviewed execution protocol remain work to do.
