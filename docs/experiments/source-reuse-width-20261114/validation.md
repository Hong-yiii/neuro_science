# Validation ledger — source reuse / width, November 14, 2026

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

Pending. No biological model fitting has occurred at this checkpoint. All source,
rank, fit, numeric-artifact and final review receipts will be recorded here.
