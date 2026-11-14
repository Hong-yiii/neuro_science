# Validation ledger — source reuse / width, November 14, 2026

**Updated November 15, 2026: all 48 scientific cases completed and independently
audited.** The original orchestration attempt failed after its first notebook;
the reviewed continuation finished only the 16 unattempted width cases. Read
[results and artifact links](README.md). No biological case was retried.

## Prefit review and software checks

- Independent scientific/code review (`protocol_review`) reproduced the exact
  metadata-only optimizer result and all three rosters. It accepted the six-arm
  scope and claim limits: 48 cases, 2,448 fits and 96,000 updates.
- Review findings were addressed before biological fitting: authenticated shared
  B3 evidence, complete-case requirements, explicit row/source lineage checks,
  failed terminal attempt records, separate notebook fit counters, imported-helper
  pins and start/end source/configuration/runtime-bound gates.
- Five invented tests passed, including exact two-stage MILP against exhaustive
  derangement enumeration, nested budgets, common development, exact width
  projections, null-before-subset construction and rejection of corrupted budgets.
  Independent review also rejected a deliberately mutated row identity.
- Both source notebooks compile, match the builder and have empty outputs.
- First invented full-width benchmark completed every model/readout and guarded
  reload in 58.796 seconds; 743.9 MiB cgroup peak, zero memory events, no swap.
  It passed its original headroom test. Its receipt remains preserved under
  `outputs/source-reuse-width-20261114/invented-01/`. Subsequent evidence/checking
  improvements changed code hashes, so a new benchmark is required for launch;
  the earlier receipt is not reused as if its pins matched.
- Final independent review found no remaining launch blocker, conditional on the
  updated invented benchmark and non-fitting all-48-plan biological preflight
  passing with frozen source/configuration/runtime and external containment.

## Runtime and resource contract

Interpreter: `scratch/endpoint-notebook-runtime/bin/python`.
`PYTHONPATH`: repository `src`, repository root, and
`scratch/v6-v9-runtime/lib/python3.13/site-packages` (existing dependency tooling).
`PYTHONNOUSERSITE=1`, `PYTHONDONTWRITEBYTECODE=1`, `OMP_NUM_THREADS=2`,
`OPENBLAS_NUM_THREADS=2`, `MKL_NUM_THREADS=2`, `CUDA_VISIBLE_DEVICES=` and
`MPLBACKEND=Agg`. Do not modify the runtimes.

Launch using `systemd-run --user --wait --pipe --collect`, with `Type=exec`,
`MemoryMax=4G`, `MemorySwapMax=0`, `CPUQuota=200%`, `KillMode=control-group`,
`TimeoutStopSec=15s`. `RuntimeMaxSec=900` for each gate and `10800` for the biological
two-notebook execution. The runner independently checks effective cgroup limits.
Conservative duration gate: 48 × full-width invented case seconds ×1.25 +900 <10800.

## Biological execution and result review

Gate attempt02 failed before fitting with an `AttributeError`: unused-import cleanup
removed the accounting class re-export used by the runner and notebook cells. Its
failed receipt/log are preserved (`invented-02`, `work/.../benchmark-02.log`). An
explicit re-export and focused entry-point test fix the software issue. No biological
case was attempted. The source change invalidates old gate pins; use new preflight
and benchmark receipts. The earlier preflight passed all48 cases with minimum
rank17,648.63MiB peak and13.87s elapsed, but is not substituted for the refreshed gate.

That checkpoint was prefit. The following records supersede its pending status
without replacing its failed or superseded evidence.

### Accepted launch gates

- `prefit-02/preflight.json`:
  `33efb2e72a0900f9decb3c810768f8356ccbf7212d462fb5db1a63227c2c93b2`.
  All 48 plans passed without fitting; minimum rank17, 13.835 seconds,
  597.71 MiB peak. Rank-table SHA256:
  `4ecab7ba06b2e1427db78fc3251d43df49880886fc6d678761b1abae796f9b7d`.
- `invented-03/benchmark.json`:
  `a30ddfb41522b8e2a29453d2b0b043b66ff85c0c707e747c590d1ff3e5006c97`.
  One complete invented case: 51 fits, 2,000 updates, 59.759 seconds/case,
  739.72 MiB peak. Conservative estimate 4,485.55 seconds <10,800.
  Whole benchmark receipt SHA256:
  `0201ae6e1796348f5069de81c11fe92b0a4e329e0dd21b01d7da5fe36c75a0db`.
- Six invented tests passed, including the accounting re-export regression.
  Invented report smoke exercised both report paths, all confusion data and
  61 figures with fitting blocked. Independent review authenticated the final
  matching code/configuration/runtime gate identities before launch.

All paths in this ledger are under `outputs/source-reuse-width-20261114/` unless
qualified. Gate outputs are software/resource or non-fitting input checks, not
biological performance evidence.

### Preserved handoff failure and bounded continuation

`real-01/receipt.json` remains **failed**, SHA256
`6d714a0b6a4ccbe2fcd08c3d56b07a647c9cc73871748bb7ff6b500281526ea3`.
Its 32 source-reuse cases, 1,632 fits, 64,000 updates, nine executed code cells and
34 figures succeeded. The runner then tried to replace an existing kernel JSON
using the exclusive-create writer and raised `FileExistsError`. This occurred
before any width case. All 2,096 receipt-bound files, the original attempt log and
resource counters remain unchanged.

The independently reviewed [continuation amendment](continuation-20261115.md)
authorized exactly the 16 unattempted Wmid/Wfull cases. It authenticated the exact
32-case boundary and 505 shared-bridge files, copied inherited evidence byte-for-byte
into a fresh sibling directory, preserved the failed parent receipt/log separately,
and recorded the full old-path→new-path mapping. A fresh width kernel received its
bridge hash before its specification was created. An invented two-kernel smoke
verified the mechanism without biological reads or fits.

Continuation source SHA256:
`2937276d6e2983b29e7fb6da91b20a4bc23793a28ba96ac2eed4aea1fd4ee512`;
amendment SHA256:
`d3415b320740d0f7c9ca309f5063db2a5a090f2c237d35be55c74d3ab11905e6`.
These are also preserved in the continuation source snapshot. The 7,200-second
continuation cap plus the original 592.043 seconds remained below the original
10,800-second envelope. No failed biological model was silently rerun.

### Accepted execution and numeric audit

**Accepted run:** `complete-01/receipt.json`, SHA256
`bd057c05a842a702d6d8c3fd2259ee4e54918fb3b49951b57f782b08e876c17b`.
Status completed; 3,155 authenticated files; 32 inherited cases plus 16 new cases.
Total 48 unique cases: 18 observed and 30 source-label cases. Actual instrumented
counts are 48 PCA, 48 Time, 48 native, and 576 each logistic/SVM/kNN/LDA:
2,448 fits excluding scalers, 96,000 optimizer updates. Native saves 344 individual
session networks. Two notebooks each completed nine code cells with no cell errors.

Combined execution phases took 1,373.865 seconds (22.90 minutes), peak 1,321.11 MiB
under 4-GiB/no-swap/two-core limits. Memory-event counters were zero in both phases.
The combined receipt sums phase duration and takes the maximum peak; root CPU
counters describe the continuation, with original counters preserved separately.

During the run, 192 representation reloads and 2,304 readout reloads passed
4,608 composed train/development checks with fitting blocked. The subsequent
numeric audit loaded saved arrays/predictions only, with no fits or model loading,
no original spike-file reads and no historical-study replay. It checked:

| Evidence | Checks / rows |
| --- | ---: |
| Cases / attempt boundaries | 48, exactly one start and completion each |
| Train/development metric and confusion checks | 4,608 |
| All report matrix views, labels and keys | 5,376 |
| Saved source-block consistency checks | 71,496 |
| Source-error rows | 299,904 |
| Source-use / pool-use / overlap rows | 15,896 / 6,192 / 864 |
| Aggregate class-error rows | 16,128 |
| Report metrics / summaries / contrasts | 2,688 / 336 / 2,688 |
| Report class-recall / paired-switch rows | 37,632 / 18,816 |
| Best/worst rankings | 32, exact integer pair-correct tie checks |
| Learning curves / latent class means | 96 / 1,296 |
| Original report figures / executed code cells | 61 / 18 |
| Map-availability rows | 498, all correctly unknown |

The audit also verifies source-label permutations before subset selection, exact
nested source budgets, shared-width arrays/lineage, common observed development
across seeds, contributors/embargo, dimensions, regularization, margins/probabilities,
all trajectories against saved features and source notebook text against the builder.

Independent result review (`teach_review`) reran the complete audit and separately
recomputed all 4,608 metrics using count-based formulas rather than the shared
metric helper. It confirmed all parent bytes, exact rankings, embedded figures,
and complete case coverage. Report text/tables and notebook outputs contain no raw
unit/session/source identities or binary neural-array MIME outputs. Generated
artifacts are ignored, not tracked. This review does not grant publication rights.

Original `audit-01/numeric-verification.json` SHA256:
`d7b4283762d3f65eced7a1c81f86beae8e4fab108daaa5e084c5d74c4ed54499`.
Its auditor hashes were `6bcfe4e888f47a361ae5182ba504c4a818971bdf77ded404d4f7c66ac656a84e`
(`verify.py`) and `a5c7bc3f5a55c5f17a8ef80f412566ce4956ae870fb95adcbd30f8950a4e2650`
(`tables.py`). These post-execution tools are separate from the original run pins.

### Post-execution orchestration repair

Current `run.py` creates a separate immutable kernel specification per notebook.
The complete two-notebook regression uses invented receipts and mocked notebook
execution, exercising real exclusive file creation, bridge hashing, unchanged
first specification and combined accounting under the fitting guard. It passed.
Independent `protocol_review` accepted the repair. **This repaired runner produced
no biological results in this study.** The actual run's archived runner remains
unchanged and records the failure faithfully.

The current auditor authenticates all 38 archived source hashes. It requires all
37 other live source pins to match, and records only drift in `run.py`, which it
neither imports nor executes. Independent inspection confirmed this dependency
boundary. The launch gates remain strict: the repaired runner rejects the old
benchmark source pin. The audit exception does not authorize a new training launch.

Full audit repeated successfully after this repair, preserving audit01. Current
`audit-02/numeric-verification.json` SHA256:
`92b667fd5b23a1a202bd1f29ec2e0d35f4160a6fd7dac345a548f133122a785f`.
It reproduces every original numeric check and explicitly records the runner change.

| Post-execution source | SHA256 |
| --- | --- |
| `audit/verify.py` | `f148da89c7042d3a123f444d1e9d9ef82c3e7d124fe5488c87368a8368289621` |
| `audit/tables.py` | `a5c7bc3f5a55c5f17a8ef80f412566ce4956ae870fb95adcbd30f8950a4e2650` |
| `audit/test_orchestration.py` | `53677f41a29ac5e628e8dce6ed3f5eb0d73047f5b23920eae65a8ba4ac8ebe2e` |
| Repaired `run.py` | `d628499f1a2ae0cdac2d13f5d3f38786b631de2e2f55b777b03297dd8fd35034` |
| Actually executed archived `run.py` | `bd46400813be851e938b81c5b8fb6d101a7e8b4e7ab531245637a37416230692` |

Safe numerical verification on the matching maintained scientific sources, with a
**fresh** output filename (never overwrite an earlier receipt):

```sh
env PYTHONPATH=src:.:scratch/v6-v9-runtime/lib/python3.13/site-packages \
  PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=2 \
  OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 CUDA_VISIBLE_DEVICES='' MPLBACKEND=Agg \
  scratch/endpoint-notebook-runtime/bin/python \
  -m experiments.source_reuse_width_20261114.audit.verify \
  --run outputs/source-reuse-width-20261114/complete-01 \
  --receipt-sha256 bd057c05a842a702d6d8c3fd2259ee4e54918fb3b49951b57f782b08e876c17b \
  --output outputs/source-reuse-width-20261114/audit-new/numeric-verification.json
```

This reads saved numerical results and public split metadata; it does not fit,
load models, or reconstruct original recordings. Pure hash inspection needs no
numeric audit and is sufficient for checking that an accepted artifact is unchanged.

## Dated delivery and interpretation review

Accepted delivery: `deliverables-20261115-03/`. Its two notebooks preserve
all 18 original cells each, including nine executed code cells each, then append
one labelled Markdown interpretation cell. Neither source nor original executed
notebook is modified. The first notebook retains its genuine original `real-01`
execution paths, whose targets remain preserved; delivery metadata binds that origin.

Two new paired-change figures per experiment accompany all original figures.
All 336 score summaries and 336 contrast summaries independently recompute from
saved tables. Independent inspection of all four added PNGs found their labels,
interval endpoints, signs and heatmap numbers correct. Reports retain all models,
heads and diagnostic worlds, not just headline SVM results.

Preserve superseded `deliverables-20261115/`, whose U3 prose omitted the specific
SVM/pair qualification, and `deliverables-20261115-02/`, whose notebook HTML still
included nbconvert's unused CDN script loaders. The current copy qualifies that
claim and removes unused loaders from the static notebook HTML; original outputs
and the separate offline interactive confusion explorers remain intact. There
are no mathematics/widget/JavaScript outputs requiring those notebook loaders.

Current delivery generator `audit/deliver.py` SHA256:
`6b4749b1d161426b6086c8036c8cceb67e984780df3354bb81c52c71f944039a`.
It performs saved-result collation with fitting blocked and no model loads.

| Artifact in `deliverables-20261115-03/` | SHA256 |
| --- | --- |
| `delivery_manifest.json` (102 files) | `85e05fa820232245f37332e38bb70155507e869f1da69f0abb0d98cd1b4a0b37` |
| `source_reuse_20261115.executed.ipynb` | `0c45e94fd4746fdc8bb43d8eb1e121359a41f3af317c144f1a829ddac639ccf2` |
| `population_width_20261115.executed.ipynb` | `bb34bb486b83a7a379fea2d1b6e89fc2e45b420bae0863c26428e1603034503b` |
| `source_reuse_20261115.executed.html` | `33d705f60437bd0323cc99c54338148e27ecb6719368b8d27804c5e55192fc81` |
| `population_width_20261115.executed.html` | `47935ac0fb3ba9825fb5fcec6240490dca6481ebe8995c1367f85b6bbea852c8` |
| `source_reuse/report.html` | `c0b7323880447c6967691a343b3bc94ba23993530cc8ee7bb761506fe81ac71c` |
| `population_width/report.html` | `34e01cfe3e3938953e6432c8e291beedb7a28b4587dc976fc647054fd034cf40` |

Final independent delivery/link/privacy/claim review (`teach_review`) accepted this
exact copy with no remaining blockers. All 102 files authenticate; both notebook
copies preserve all original cells and original metadata apart from the explicitly
added delivery metadata. Both report explorers and static notebook HTML have no
external resource dependencies or missing local links. A privacy scan of38delivery
text/data files and the results note found no underlying source/unit/session IDs.
All eight best/worst SVM rows, class-change counts, paired-switch totals and both
example recall changes in the results note were independently reconciled. The
accepted result note's SHA256 is
`1369e4d984f824ae7802b8765933ea61a73b96957e322f2f8113cf96c4f35f2e`.

The original width `all_models.png` has tightly packed panel labels; it is preserved,
and the supplemental single-panel all-model contrast plot provides a clearer view.
No numeric conclusion depends on that presentation issue.

Prior studies, runtimes, source notebooks, original attempts and unrelated sampling
code/current-state notes are preserved. No further fitting, retry, push, merge,
issue edit or outside message is queued.

Final file checks: all experiment Python files pass Ruff; all Python/notebook code
parses; source notebooks retain empty outputs; every local link in the eight changed
reading/status documents resolves. Expanding Ruff to the frozen source notebooks
reports six existing E401/E701/E702 import/statement style findings. Their exact
executed source is preserved rather than reformatted after the scientific run.
Whitespace checks pass. The unrelated sampling-code hash remains unchanged and
generated evidence remains ignored by Git.

Local closure commit `dd7de7f` records the audited handoff. Final independent
provenance review (`protocol_review`) reconciled all24directly available SHA256s
listed above; the historical audit01 source identity was recovered by reverting
only the documented runner-drift exception in memory. Both numeric-audit count
sets, phase durations/peaks and all102delivery hashes match. No provenance, count,
resource or runner-repair blocker remained. Subsequent entry-point wording makes
the PCA finding explicitly mean **pair balanced accuracy** across width steps.
