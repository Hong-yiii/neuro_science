# Complete notebook reproduction — validation, November 15, 2026

Status: independent launch review passed and the bounded real-data reproduction
is running at `outputs/source-reuse-width-notebooks-20261115/real-01/`. The original accepted
study remains unchanged. This ledger records the separate owner-requested
end-to-end notebook reproduction and subsequent publication.

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

## Post-execution acceptance

Pending:38successful code cells, exact48case/fit/update accounting, full numeric
and contributor audit, authenticated comparison with accepted `complete-01`,
independent scientific/privacy review of the actual outputs, byte-preserved
executed copies, offline HTML checks, and the authorized draft PR. No merge.
