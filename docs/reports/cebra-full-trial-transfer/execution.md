# Execution and review ledger

**Completed September 25, 2026 (Asia/Singapore).** Request/artifact date: September 24. This is exploratory research on historically exposed sources, not confirmation. [Results](README.md) · [Protocol](protocol.md) · [PR #9](https://github.com/Hong-yiii/neuro_science/pull/9)

## Scope and prefit gates

- User authorized a separate worktree, bounded autoresearch-style experiment and PR. Branch `feat/cebra-full-trial-transfer` starts from refreshed `origin/main` `8340631`, after PR #7 merged. Canonical uncommitted work and issue #6's separate worktree were preserved.
- Scientific review approved the fixed 29-unit / seven-session, 82-training / 22-historical-validation-source protocol, including normalized-progress native-pair sampling and conditional-pseudopopulation limits.
- Initial code review found incomplete approval/input binding, configuration overrides, seed-collapsing source sensitivity and incomplete replay/integrity checks. **No biological fit preceded their repair.** Failed/rejected QA drafts remain in canonical `management/`; they are not alternative scientific results.
- Repeated no-fit audit: all 82 training sources exported navigation; **no validation source had navigation exported**. Complete native 100-ms bins/source: min 46, median 69.5, max 192. Seven Ripple and 29 spike MAT files were opened. These contain session-wide raw data in memory, but only training-source navigation windows were selected/binned. Training cue counts exactly matched the accepted source tensor. One subsecond cue was clipped; the small cue tail beyond one second and final partial navigation bins were audited and excluded.
- Eleven focused tests covered native-pair/row-uniform sampling, source lineage, input corruption/duplicates, three-seed sensitivity, positive/no-signal readouts and synthetic forward replay with fit APIs blocked. The complete clone-only suite passed 113 tests. Two named historical private-input checks remain excluded by the existing suite; this is not an all-data reconstruction test.
- An invented-data CPU timing check took 26.04 seconds for four 1,000-update encoders, one PCA and 12 readouts. It was software/runtime QA, not biological evidence.
- Fresh code re-review `57dcc9a8-5925-43d1-b65e-95900a6bd727` approved with no findings. Executed runner SHA256: `ad1dc989d65b43bf0bcdd55638f66d1918a6c61654f69eec3e98edabe2e1a4b4`. Code, protocol, helper, configuration and input hashes were bound in `management/prefit-approval.json` before launch.

## Actual execution and verification

One biological attempt, completed successfully under Pi task `bc5b33c2f`. Fitting journal ran **2026-09-24 16:29:15–17:09:22 UTC** (40 minutes 7 seconds); the supervisor, including its first verification pass, completed in 40 minutes 35 seconds. The fit had a 90-minute external timeout plus internal deadlines, two CPU threads, RTX 2070 CUDA and a 10-GiB output cap. Accepted run size is about **213 MiB**, plus small verification/QA outputs. No biological attempt failed or was selected away.

- Actual fit commit: `e171328d4eb2ed095f3b2af08315e9088cfe77de`, clean working tree at launch.
- Runtime: Python 3.13.2, CEBRA 0.6.1, NumPy 2.3.4, scikit-learn 1.7.2, PyTorch 2.12.0+cu130.
- Exactly 252 encoders, 63 PCA transforms and 756 readouts started and completed. No rescue fitting, configuration expansion, original-test analysis or validation-navigation model input occurred.
- Forward-only verification replayed **1,071 fitted artifacts**, checked **4,681 hashed files**, and rederived predictions, metrics, null summaries and all source sensitivities. Largest prediction/score discrepancy: **1.95e−7**; metric discrepancy: **7.69e−8**. Summary/sensitivity comparisons passed 1e−6 tolerance. Fit APIs were blocked during replay.
- Fresh independent numerical review `669bce07-7122-4d8b-bdb9-2bc085367134` approved with no findings. It independently recomputed all **1,512 metric groups from 119,448 saved predictions**, agreeing to **6.66e−16**, and checked fit counts, paired gains, null tails, source sensitivity seed accounting, source nonoverlap and native-pair coverage. See [review receipt](reviews/numerical-result-review.md).

### Postfit static-check correction, not a new fit

The harness LSP requests timed out and were inconclusive. A scoped Pyright CLI check then reported six CEBRA API annotation incompatibilities: temporary unconfigured offset, the base Dataset annotation hiding the concrete labels field, and a generator annotated upstream as returning Batch rather than Iterator.

The shipped runner adds only identity `typing.cast` calls, a typing import and explanatory comments/one scoped ignore for the transient offset. Removing identity casts yields **exactly the executed Python AST**. This is recorded in [the type-only receipt](reviews/postfit-type-only-proof.json); the exact executed snapshot remains in the accepted run and at `e171328`. The shipped file SHA256 is `5e8065af5cb7f61683a3cc05a4d022f05c79f214afaea093682cafb94695ff5e`.

After that clarification: scoped Pyright **0 errors / 0 warnings**, the same **113 software tests passed**, and a second complete no-fit replay succeeded under the shipped code (`-verify-shipping`). No biological fit was repeated. Old approval hashes intentionally do not authorize fitting changed source bytes: use the executed revision for exact reproduction or obtain new review before any newly authorized run.

## Final delivery review and browser QA

Fresh claim/delivery review `8a31cbf1-dd37-46b4-b12c-5b2543d12ce4`
[approved with no findings](reviews/final-claim-review.md). It checked report
numbers and limits, frozen-protocol identity, type-only changes and verification
receipts, and independently recalculated sampled source-resample/deletion rows.
No fitting or raw extraction was repeated by either result reviewer.

Parent headless-Chrome checks passed at 1280×1000 and 390×844. Both rendered DOMs
contained the expected result text and two embedded figures, with no script tags
or external resources. Desktop/mobile screenshots were inspected; temporary
browser profiles were removed. [Delivery QA receipt](reviews/delivery-qa.json)
records the report hash and checks. No server or remote endpoint was started.
The harness Lens cache had no dispatched worktree files; static assurance comes
from the explicit scoped Pyright CLI check, not from an empty cached result.

## Reproduction and artifact authorities

All commands below assume the private inputs and existing runtime are present. **Completed study: these are procedures, not permission for more fits.** Original fitting/audit commands and strict approval conditions are in the frozen protocol. No environment installation is necessary on this host.

```sh
cd /home/hongyi-home-lab/neuro_science/work/cebra-full-trial-transfer
export PYTHONPATH="$PWD" PYTHONDONTWRITEBYTECODE=1 PYTHONNOUSERSITE=1
export OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2
PY=/home/hongyi-home-lab/neuro_science/scratch/v6-v9-runtime/bin/python
ROOT=/home/hongyi-home-lab/neuro_science/outputs/cebra-full-trial-transfer-20260924
RUN="$ROOT/biological-run-20260924T162913Z"

# Saved-state replay only; use a fresh output path, never overwrite receipts.
"$PY" scripts/cebra_full_trial_transfer.py verify --run-dir "$RUN" \
  --output-dir "$ROOT/verify-$(date -u +%Y%m%dT%H%M%SZ)" --device cuda

# Re-render portable aggregate reports; reads accepted results, never fits.
"$PY" scripts/build_cebra_full_trial_report.py --run-dir "$RUN" \
  --verify-dir "${RUN}-verify" --output-dir docs/reports/cebra-full-trial-transfer
"$PY" scripts/check_research_software.py
```

Under canonical `outputs/cebra-full-trial-transfer-20260924/`:

| Path | Authority / disposition |
| --- | --- |
| `biological-run-20260924T162913Z/` | Sole accepted biological run: predictions, all states, journal, hashes, source manifests, pair lineage/exposures, snapshots and sensitivities. |
| `biological-run-20260924T162913Z-verify/` | Original successful no-fit replay; compact receipt copied into this report. |
| `biological-run-20260924T162913Z-verify-shipping/` | Second successful replay after type-only source clarification. |
| `audit-parent-20260924/` | Final no-fit audit and private training-navigation export. |
| `management/` | Approvals, rejected/repaired code reviews, independent numerical/claim review, static/test logs, and report QA. |
| Earlier `audit-*`, synthetic smoke/timing outputs | Retained QA history, excluded from biological results. |
| `report-figures/` | Small generated PNGs, ignored; portable HTML embeds them and needs no server. |

Git contains only code, protocol, compact aggregate/review receipts and human reports—not raw data, source tensors, checkpoints or prediction arrays. This is not an off-host backup of the private artifacts. Rendered HTML can be downloaded and opened offline; GitHub shows HTML source rather than rendering it.

The requested worktree remains through PR review. Do not merge or remove it without subsequent approval and artifact/cleanliness checks. No daemon, timer, listener or persistent service was introduced. All experiment/test/browser-check tasks are bounded, session-owned commands. No additional biological work is queued by this handoff.
