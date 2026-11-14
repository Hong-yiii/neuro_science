# Complete notebook reproduction — validation, November 15, 2026

Status: **completed and independently reviewed**. Both complete notebooks and
offline HTML copies are ready for the authorized draft PR. The original accepted
study and all failed attempts remain unchanged. This ledger records the separate
owner-requested end-to-end notebook reproduction and publication.


## Frozen scope and source

The [prospective plan](notebook-execution-20261115.md) retains48cases,
2,448model fits excluding scalers and96,000updates on the same recordings/seeds.
Source implementation is committed at `d8eb31d`. Both source notebooks have38cells,
19code cells; seven shared cells expose the actual first-case training, arithmetic
and diagnostic operations. First cases are observed seed0 B2/Wmid, followed by
31/15remaining cases. Eight B3 cases are shared once. The two kernels have separate,
immutable specifications. Nine per-notebook stage checkpoints preserve actual
fit counts and failure boundaries.

The existing sampling-file edit is byte-preserved at
`63489315c5a21257ed037edd77161f639beb23199321719d8fe22a562c1659f5`;
its AST equals committed source. It is pinned as actually executed but excluded
from the publication diff. Unrelated current-state notes, old studies, runtimes,
source data, failures and accepted output directories remain unchanged.

Independent code review and an independent notebook/scientific content review
accepted the implementation subject to refreshed gates. Three no-fit invented
orchestration tests passed, independently repeated: immutable two-kernel handoff,
exact schedule/bridge/first-case behavior, and staged failure accounting with
retry rejection. New Python and notebook sources pass Ruff. The content review
independently checked all144class-change rows per part and5,376embedded confusion
views using accepted aggregate files as a read-only fixture. The final inherited
section number8following16is a nonblocking editorial nit retained in the frozen
source. No fitted parameter/value array is printed by the teaching cells.

## All prefit attempts

| Attempt | Result and actual work | Resource receipt |
| --- | --- | --- |
| invented-01 | Both invented full-width paths completed102fits/4,000updates. Gate failed because NPZ key order differed; all298arrays were independently found bitwise equal. Fixed serializer ordering; no tolerance relaxation. Preserved failure. | 118.79s;735.50MiB |
| invented-02 | Passed strict original/staged comparison. Exact plans/labels/predictions/metrics/confusions/source tables;298numeric arrays;192composed split reload checks;102invented fits/4,000updates. | 115.95s;699.27MiB |
| prefit-01 | Explicit source-reconstruction flag omitted from launcher; correctly stopped before reconstruction/model fitting. Preserved failure; no biological fit. | 1.86s;512.85MiB |
| prefit-02 | Correct authorized environment flag, all48plans passed with fitting blocked. Minimum training rank17; exact source nesting, projected values, contributor exclusions and quotas checked. | 13.72s;599.97MiB |

Total invented fitting across both attempts:204fits/8,000updates, separate from
any biological budget. Each attempt used a fresh directory under
`outputs/source-reuse-width-notebooks-20261115/`. No biological case has been
retried. The slower successful invented path took56.560709s; conservative
headroom48×56.560709×1.25+900=4,293.642546s is below10,800s.
Both passing gates agree on all source/notebook/configuration/design/runtime and
compact-input identities. Continuous cross-path arrays use rtol=atol=1e-7;
encoder/readout serialization checks retain1e-5/1e-7. Wall times and state-file
byte hashes are excluded from cross-path equality.

| Receipt | SHA256 |
| --- | --- |
| invented-01/receipt.json | `82145dc1c8356f2d7c53e90c6a47182407d8a925d606f25c27fd4c17091468ad` |
| invented-02/receipt.json | `5e8563898bd64be96f0a8fc20e87b1e9a8724ad2a868e3e6d8cf4b7b178f2cb9` |
| invented-02/benchmark.json | `18cb3fe8990bc47a5822b491feb835f32831ddf299efe330533bdbb735d104fa` |
| invented-02/equivalence.json | `dba17eb410f5ab07871d76e9fc5bdd48e179e1a90b54870f320a1a8ec7f6c09d` |
| prefit-01/receipt.json | `823331911b422bcb11bc528212e92e10840c29f34e94cefc4fd57aaa73f8079d` |
| prefit-02/receipt.json | `39883076f503c1f7794a7922e279d1fd7394f19e0362f0e25a13a8a959ff41a5` |
| prefit-02/preflight.json | `6ac5b70c28768d86f4e08dc4bd208c44363dc54d99bc9758d8916f8e7ecbc772` |

## Commands and environment

Use canonical repository root and the existing read-only runtime. All execution
modes run under `systemd-run --user --wait --pipe --collect`, with
`Type=exec`, `MemoryMax=4G`, `MemorySwapMax=0`, `CPUQuota=200%`,
`KillMode=control-group`, `TimeoutStopSec=15s`. Gates use `RuntimeMaxSec=900`;
training uses `RuntimeMaxSec=10800`. Set:

```text
PYTHONPATH=src:.:scratch/v6-v9-runtime/lib/python3.13/site-packages
PYTHONNOUSERSITE=1
PYTHONDONTWRITEBYTECODE=1
NEURO_REUSE_ALLOW_BIOLOGICAL=1
OMP_NUM_THREADS=2
OPENBLAS_NUM_THREADS=2
MKL_NUM_THREADS=2
CUDA_VISIBLE_DEVICES=
MPLBACKEND=Agg
```

Then use `scratch/endpoint-notebook-runtime/bin/python -m
experiments.source_reuse_width_20261114.walkthrough_20261115.run` with
`--mode benchmark|preflight|train` and a fresh `--output` directory.
Training additionally requires `--benchmark-receipt`, `--benchmark-sha256`,
`--preflight-receipt`, `--preflight-sha256` matching the exact passing receipts.
Never reuse a gate after changing pinned numerical/notebook code or inputs.

## Launch review

An independent reviewer authenticated140gate artifact files,51current code pins
and64compact-input hashes; matched runtime/configuration; independently checked
all298invented arrays bitwise, all48real preflight plans and zero contributor
overlap. Both gate cgroups had zero memory events. One biological launch was
cleared under the frozen4GiB/zero-swap/two-CPU/10,800-second limits. The fresh
run began November15at approximately02:42Singapore time. Full source/runtime/
configuration snapshots and final exact timing are owned by the run receipt.

## Completed execution and numerical audit

The fresh `real-01/` completed48cases once,2,448model fits excluding scalers and
96,000CEBRA updates. Both original notebooks have38cells/19executed code cells,
with counts1–19 and no errors. Every instrumented stage/attempt total reconciles.
Actual runtime was1,362.603478seconds (22.71minutes), peak1,388.875MiB; all memory
event counters were zero under4GiB/no-swap/two-CPU limits. No failed biological
case was retried.

The [full numeric audit](notebook-numeric-verification-20261115.json) authenticates
all3,188run files and54archived/current code pins. It reconciles71,496saved source
block joins;299,904source-error records;4,608split metrics;96learning curves;
1,296trajectory class means; all source/pool/overlap/error tables; and every
reported class recall, paired switch, contrast and ranking. The report has61original
figures and5,376matrix views (4,608unique matrices; shared B3 is shown twice).
Every saved pipeline was checked during execution:192encoder reloads,
2,304readout reloads,4,608composed train/development checks,344native session
encoders across all cases.

The accepted old receipt and all3,155old files were authenticated before comparison.
All14,304numeric arrays are identical:9,312exact-label/prediction/raw-tensor arrays
and4,992continuous score/feature arrays, maximum difference0.0. Complete case,
lineage, metric, confusion and trajectory records match exactly. A separate saved
JSON comparison confirmed all96learning records match apart from wall time. This
is a computational reproduction with the same recordings/seeds; it supplies no
additional biological independence and is not pooled as new statistical evidence.

An independent read-only agent recomputed metrics without calling the project
verification functions. It checked all4,608split evaluations from saved truth,
predictions, probabilities or margins;2,304case metrics;5,376report matrices;
37,632class-recall rows;18,816paired switches;2,688contrasts;336score summaries;
336contrast summaries; and32best/worst records, all within1e-12. It independently
regenerated the five source-label worlds and all48hashed source subsets from
public metadata, checked all71,496joins and the5,872-contributor embargo, and
confirmed13,824prediction-related arrays bitwise across executions. It did not
load fitted models, read neural feature arrays/raw spikes or fit anything.

The independently verified conclusions remain those in the [result report](README.md):
U3 Raw/PCA SVM pair BA40.74%/40.28%, each observed repeat above all five diagnostic
scores; mixed B3−U3 changes without complete contrast-range separation; PCA mean
pair gains at both width steps for all four readouts, with only1/3positive repeats
for the final PCA/SVM49→83step. Spatial-field attribution remains untested.

## Reviewed publication copies

The [published handoff](../../../experiments/source_reuse_width_20261114/walkthrough_20261115/README.md)
contains two40-cell notebooks with19executed code cells each, two self-contained
HTML reading copies, six curated aggregate PNGs and a hash manifest. Every
executed code/output object and original notebook metadata is unchanged. Only
original Markdown cell2 is corrected: same-session/source-trial grouping does
not verify biological simultaneity. A labelled saved-aggregate figure is inserted
after original cell22, because the Agg backend had displayed that figure as text.
An appended editorial note records both changes and identifies generic stdout
paths as execution-host provenance, not public links. Frozen source notebooks
and original execution snapshots retain their historical text; the reviewed
publication copies own the corrected scientific explanation.

Each added figure uses only authenticated `learning.json` and `confusions.json`
from the first case. It separates the two objectives' loss axes and shows count
text with row-normalized confusion color (diagonal=recall). Their raw/logistic
pair scores are34/72=47.22% and48/72=66.67%; each loss curve has1,000updates.
No model was loaded or refitted, and no neural feature/value array was decoded
for publication. Four further PNGs are byte-preserved excerpts for the result
report; its design caption was corrected to describe columns/sessions/source
budget, with available-source/row counts in the adjacent table/text.

Independent actual-output and final-package reviews passed: all10manifest-bound
files authenticate, all executed cells/outputs are preserved, embedded images
match their PNGs, and no credentials/private inputs/source identities/neural
arrays/fitted coefficients appear. Printed values are aggregates, anonymous
aliases/ordinal recipe choices, architecture and verification residuals.

The [offline browser audit](notebook-browser-verification-20261115.json) checked
all5,376matrix totals,496interactive count/normalized views and67loaded figure
views (37reuse,30width); no external resources loaded. Both first-case figures
also passed visual inspection. HTML copies can be downloaded and opened locally;
interactive output may require a trusted notebook viewer. No native cmux pane
was opened because this terminal had no unique owning pane.

| Final artifact / receipt | SHA256 |
| --- | --- |
| real-01/receipt.json | `717d49dc5d061be3f7933ea6684115939cfb8aa72375e1b41b6ba758957a27d3` |
| numeric verification | `73030f75359f06fdbedab556eab12a17e2aed23ad9adb88784d7b02de35a8fe5` |
| delivery manifest | `8ef3a28e687e657c6429632b6a2011bfaa57dfadd62ff94fc276f21bef9a9e93` |
| source reuse executed publication notebook | `64f05b415c99b702299e735076e5c04aabd3d3194400631c63428f01a268480c` |
| width executed publication notebook | `8fab810ce58d6bebc579d66033268b1cbca89da873e089b70f5c4886f7cc9c13` |
| source reuse offline HTML | `9e58f73461837b55ba998afe58a649b3500f8495fa449557f3ee0e77615ede04` |
| width offline HTML | `fc0ff3b75516c591682f32e07c15bac02d04011cefcfca355a3ebdbef65e903d` |
| publication helper | `ba94ee7e3594339eb9955ab5ffbc8b443081d11f8df46b5b14ab8185081c8e4d` |

The earlier `/teach max` lesson remains disposable outside Git at
`/tmp/pi-teach/20261115-015340-reuse-width-max/results.html`, SHA256
`f60c2f9d85356f29ce8641fbc56196124ce39b08ff30f23b1a4b3b2fafeafd93`.
It describes the accepted study whose numeric results this reproduction matches.
Independent methods/claims reviews and94UI-state checks passed before notebook
work began. No extra teaching copy or new biological conclusion is created here.

Draft-PR publication is the remaining administrative step. No merge, issue edit,
further fit or automatic retry is queued.
