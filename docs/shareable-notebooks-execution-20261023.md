# Shareable notebook implementation — October 23, 2026

## Authority and north star

The owner approved [the package/notebook plan](notebook-package-plan-20261023.md)
and requested implementation, real-data end-to-end execution and independent subagent
validation as a long-running task. This supersedes that plan's earlier planning-only
status, not its scientific safeguards. Work is exploratory scientific software and
bounded exploratory reanalysis, not confirmatory evidence or a new independent test.
No public publication, license grant, merge, data redistribution or service change is
implied.

Starting checkout: `3f84018`, `main`; the plan/workspace/index documentation changes
are preserved, as are unrelated untracked current-state notes and the user's stash.
Protected baseline: `work/shareable-notebooks-20261023/baseline.json`. Accepted saved
notebook/results, private original inputs and scientific runtime must remain intact.

## Execution stages

1. Implement validated public source/assembly/PCA-LDA/CEBRA interfaces, focused tests,
   standalone packaging, three fresh-input notebooks and their bounded executor.
2. Validate invented data, installed-wheel imports outside the checkout, and fresh
   notebook execution; keep synthetic and biological results distinctly labelled.
3. Inspect only the necessary existing endpoint source/label/split inputs and establish
   a specific real-data protocol and access manifest. Reconstruct from source-level
   measurements/ledgers where available; do not consume old fitted models, assembled
   standardized rows or scores as fresh computation.
4. Independently review data/label/split and scientific code before biological fitting.
   Record input/code identities, fitting budget, safeguards and shared-host resources.
5. Execute the reviewed notebooks into fresh private run directories; check fresh
   fits, matched ablations, provenance, publication privacy and preservation.
6. Independently review final implementation and scientific interpretation; fix
   findings and revalidate affected paths. Report residual limitations honestly.

Default boundaries: endpoint cue-only condition-level assay, inherited exposed
training/development sources; no outer-test access, navigation extension, new download
or historical null-world rerun. Actual cohort/target/ablation details and resource
ceiling will be frozen after input inspection, before fits. Real-data execution uses
at most two numerical threads and one fit process at a time, with a bounded deadline,
fresh output and host-memory budget. Lack of support or unresolved lineage stops that
path rather than silently changing the target or filling missing measurements.

## Implementation and pre-fit checkpoints (historical)

- Initial host sample: 8.6 GiB available RAM, 223 GiB disk free; RTX2070 idle (1 MiB of
  8192 MiB in use). These are snapshots, not permission to consume all host resources.
- Phase1 implemented the public source/assembly/PCA-LDA/CEBRA/evaluation APIs and
  explicit setuptools distribution. Worker reported16/16 public/frozen-notebook checks
  and54/54 scoped study compatibility/synthetic checks passing. Tiny synthetic CPU
  fitting and offline installed-wheel smoke passed; inherited dependencies, not a
  fresh dependency-resolution certification. Independent review found and resolved
  unsigned/complex timing validation and stale lock metadata.
- Input scouts authenticated the six required source-input files and inspected
  metadata only. Full direct-predecessor embargo is feasible with a deterministic
  27-unit/10-session panel (1,415train/551development). It changes the estimand;
  original195-unit outcomes will not be compared as matched scores.
- Independent scientific protocol review accepted that narrower design in principle.
  [Frozen scope and gates](shareable-notebooks-protocol-20261023.md) require fresh
  event/count binning, contributor-disjointness, observed/reduced/permuted fitting,
  and exact fit/resource accounting. Data-path and model/executor reviews are now closed;
  resource benchmarking remains the last pre-execution gate.
- Phase2 added the adapter, three executed invented notebooks, protected model replay,
  and bounded executor. Final focused checks passed36/36 in86.994seconds (`b3ecfc763`).
  The installed-wheel full demo passed6CEBRA/10PCA/78logistic/12LDA,120updates and180
  readout-split forward replays. A/B also passed without CEBRA installed/imported.
  `uv lock --check --offline` passed with no pre-existing dependency version changes.
- Independent reviews fixed mutable metadata selection, weak numeric-gate coverage,
  actual fitting-kernel code identity, final-exit disk/deadline validation, and the
  supplied-data single-row illustration (now an aggregate). Data review395b4c1f and
  model/executor reviewd89318a2 closed their scoped gates. No biological values/fits yet.

## Bounded launch operations — prepared October23,19:40SGT

Owner: HY; current Pi session in the canonical checkout. This is a finite exploratory
run, not a daemon, scheduled task, new deployment, or permission for future experiments.
The existing application services are not dependencies and will not be restarted.

- Installed runtime: absolute `work/shareable-notebooks-20261023/phase2-runtime/bin/python`.
  Scientific and notebook dependencies/template assets are inherited read-only; this
  is installed-wheel validation, not a fresh environment resolution certification.
- Frozen notebook/executor copies and pin manifests:
  `work/shareable-notebooks-20261023/launch-preparation/`. The original reviewed wheel
  remains unchanged. A post-handoff19:28 formatting pass changed five working module
  byte hashes, not any library AST or TOML meaning; both identities are retained in
  `formatting-delta.json`. No formatted changes were reverted. Execution uses the exact
  reviewed installed module bytes, with actual kernel identity checked before fitting.
- User transient units: `neuro-notebook-benchmark-20261023.service` (30minutes) then,
  only after its gate passes, `neuro-notebook-real-20261023.service` (90minutes).
  The inspected pre-kernel launch correction uses the new exact unit
  `neuro-notebook-benchmark-v2-20261023.service`, not a resumed old process.
  Launch: `systemd-run --user --wait --pipe --collect`, `Type=exec`,
  `MemoryMax=4G`, `MemorySwapMax=0`, `CPUQuota=200%`, `KillMode=control-group`,
  `TimeoutStopSec=15s`, and the respective `RuntimeMaxSec`. Four GiB is a deliberately
  tighter cap than the approved six-GiB ceiling. The one-time receipt wrapper verifies
  actual cgroup limits and pinned bytes and records cgroup peak/events before exiting.
- Commands use absolute interpreters and a clean explicit environment, two numerical
  threads, private IPython/Jupyter/MPL directories, no boot enablement/restart, no
  application listener or external ingress. Jupyter uses temporary local kernel IPC
  only; the unit owns all descendants. Stop only the active exact unit via
  `systemctl --user stop UNIT` or its owning Pi task. Do not signal historical PIDs.
- Outputs: ignored `outputs/fresh-notebooks-20261023/`, directories0700/files0600.
  Logs: current Pi task output, protected per-run `execution.log`, and user-unit journal.
  No original inputs, accepted results, runtime, stash or unrelated notes are modified.
  No off-host copy, cleanup of historical runs, or public/private-data publication.
- Benchmark: invented27units/10bins,480train/240development, the complete1000-update
  grid and full fresh-kernel/export/replay workflow. Reserve900seconds across the three
  real reconstructions, then require25%headroom inside90minutes. This reserve is not a
  measured numeric-parser duration: metadata-only reproduction took0.667seconds and
  byte-only gzip traversal took0.461seconds (73.9MB decompressed, no numeric parsing).
- Preflight:223GiB disk free,6.8GiB available RAM; existing swap use2.1GiB is not this
  run's allocation (its cgroup forbids swap). User manager was already degraded with
  Framed and two desktop-portal units failed; these unrelated failures were not
  investigated, reset or changed. Recheck memory/pressure before the real launch.
- Failure/deadline/OOM/nonconvergence/wrong fit count or integrity failure stops the
  run. Preserve all failure evidence; no automatic retry/resume. Success requires
  exact counts,180fit-blocked readout-split replays, shared development identity,
  private output validation, cgroup cleanup and independent final interpretation review.

### First launch — stopped before kernels/fits

Benchmark task `b720eaea2` exited1 at19:39:51SGT after1.85seconds: the clean controller
PYTHONPATH omitted the explicitly borrowed notebook tooling, so `nbformat` was absent.
No kernel, neural reconstruction or fit began. Its original `benchmark/` directory,
protected traceback and `benchmark-cgroup.json` remain intact. Pins were preserved;
cgroup peak146,378,752bytes, swap0, OOM0. The unit is now not-found/inactive.

The correction adds the read-only notebook site-packages path to both controller
PYTHONPATH and kernel `--dependency-path`, alongside the scientific path. A bounded
import probe confirms all notebook imports and **exact equality** to the validated demo's
kernel identity. No source/runtime installation or scientific configuration changed.
A new explicitly inspected `benchmark-v2/` launch follows; no automatic retry/resume.

### Corrected full-size benchmark — passed

Task `bdb7e72e2`, unit `neuro-notebook-benchmark-v2-20261023.service`, completed
19:44:45SGT, exit0:94.811seconds,6CEBRA/10PCA/78logistic/12LDA/6000updates,
all fresh kernels/export/model replay. Sampled owned RSS1,647,575,040bytes;
actual cgroup memory peak1,130,082,304bytes, swap0, memory-max/OOM events0;
output33,584,501bytes. Cgroup and RSS are different accounting quantities.
The terminal systemd summary's tiny peak is not used; the in-cgroup counter is retained.
`(94.811 + 900) × 1.25 = 1243.513seconds` (20.73minutes), within90minutes.
All pinned bytes remained exact; unit is now not-found/inactive. Receipts:
`outputs/fresh-notebooks-20261023/benchmark-v2/benchmark-receipt.json` and
`benchmark-v2-cgroup.json`. Independent preparation review255f65fd found no blocker.

### Real launch — approved, fresh output only

User authorization already covers this bounded execution. Metadata/data-path review395b4c1f,
model/executor reviewd89318a2, preparation review255f65fd and the completed full-size
benchmark satisfy the prefit gates. New `launch-preparation/real-execution-manifest.json`
sets the explicit biological flag and pins the validated kernel, leaving the original
false-flag manifest untouched. SHA256`bee786f3fc8239b1c22c36cf5f28ec44b0645539d525384a238ea51f5e632737`;
real pins SHA256`dbaee7f15cdc53a8d43d02271024ff2924bc196b1bcaeea72646c956c09a3c7f`.
All six input hashes and protected baseline hashes match; selected-metadata digest remains
`7862b0ea68d24a4bbfe349cb6c81df8c058840d313967092471708bca0efc028`.
Current preflight has7.4GiB available RAM and zero recent memory pressure.

The new real unit uses the same reviewed frozen executor, both explicit dependency paths,
4GiB/no-swap/two-core cgroup,90-minute deadline and fresh `outputs/fresh-notebooks-20261023/real/`.

### Real execution — passed and independently accepted

Task **`b0497792d`** completed19:50:49SGT, exit0,115.275seconds under the owned unit.
All three notebooks freshly reconstructed inputs and ran every cell in order (8/7/7),
producing3/5/13rendered figures. Exact fit counts: **6CEBRA,10PCA,78logistic,12LDA,
6000optimizer updates**, excluding scalers. Loaded-model, fitting/update-blocked replay
checked72B+108Creadout splits; observed development inputs and assembly lineage matched
across notebooks. No old models/tensors/standardized arrays were used.

- Private delivered notebooks/HTML: `outputs/fresh-notebooks-20261023/real/01_pseudopopulation/`,
  `02_pca_lda/`, `03_cebra/`; each contains its `.executed.ipynb`, `.html`, completion
  record and protected new artifacts. Source-visible notebooks still contain invented
  outputs only. No real output was copied into the shareable source notebooks or published.
- Receipt `real/receipt.json` SHA256`bbc59a6899cb2c42b20a985baaaf7b55cec4f7d37c3e92f076d73c8325dafebe`.
  Sibling `real-cgroup.json` SHA256`9a60cda9054e39fa929e88f8b37513c07627b37a52aa083bc895fd06c5260c9a`.
- Actual cgroup peak1,170,518,016bytes (1.09GiB); sampled process-tree RSS1,702,289,408bytes.
  Swap0; memory-high/max/OOM events0. Output36,209,854bytes, safely below2GiB.
  All pinned inputs/code/protected artifacts remained exact before/after execution.
- The real unit is now not-found/inactive; no retained fit process, automatic restart,
  server or scheduled task. No further fit/retry is queued.
- Final independent reviewer **`cf4ffdf8` accepted** the bounded exploratory run:
  independently authenticated all indexed artifacts and repeated180fit-blocked
  readout/split replays. All21real-run PNGs were visually inspected; no private
  identifiers, paths or row-level predictions were observed. Public notebooks remain
  invented and contain no real-run PNG. No further fits were performed for review.

### Reviewed numerical and interpretation checks

Conservation: **27,598 binned + 518 omitted-tail spikes = 28,116 accepted events**.
Masks, exposure, intact-block lineage, contributor separation and fixed development
assemblies passed. Reduced pools retain638/1415training sources, nested within full
pools; this is floor-half per pool, not exactly50%overall. All six CEBRA fits have1000
finite updates and verified native-bin sampling. Logistic convergence took9–33iterations.

Full-pool development balanced accuracy ranges across two **computational** seeds:

| Representation | Pair30 | Start6 | Goal6 |
| --- | ---: | ---: | ---: |
| Raw | 15.8–17.9% | 27.1–30.8% | 62.5–66.7% |
| PCA | 12.1–14.6% | 22.5–27.5% | 57.9–61.3% |
| CEBRA | 15.0–19.2% | 20.8–30.0% | 47.9–55.8% |

Uniform BA references are1/30 and1/6, not significance thresholds. These ranges are
not biological uncertainty; the results establish neither general CEBRA superiority
nor a sample-efficiency law. LDA's large development log losses warrant calibration
caution. Full/reduced/permutation metrics and confusions remain in the private notebooks.

One accepted **nonblocking presentation defect** remains: full readout titles overlap
between confusion-grid columns (`notebook_support.plot_confusions`). Matrices, axes
and configuration supertitles are intact. Preserve the authenticated run; any later
short-heading export must be a separately labelled presentation copy, not a rewritten
execution receipt. No flawless-layout claim is made. The final reviewer checked stored
new-run arrays/conservation, but did not independently re-read/re-bin original streams.

## Retained material and limits

Task-owned environments/wheels, failed invented attempts, the pre-kernel benchmark
failure, successful benchmark and real outputs are intentionally retained for verification
and recovery under the named ignored work/output roots. Original research runtimes,
source inputs, accepted notebook/helper/results, HEAD/stash and unrelated notes remain
preserved. Final audit `work/shareable-notebooks-20261023/final-preservation.json`
rechecks all launch pins, HEAD/stash, no staged files, private run permissions and all
three units unloaded. The benchmark and real run's task-generated, non-data IPython
startup READMEs needed mode0644→0600 tightening; their0700parents already restricted
access and contents were unchanged. The complete task output tree is owner-private. Final review is retained as `final-independent-review.log` in that work
root. Session diagnostics report no issues across ten dispatched files; focused Python
LSP checks and runtime tests are recorded separately, not a full-project scan.
At the execution checkpoint, nothing had been uploaded, committed, merged or licensed.
The later draft-PR request below changes only the publication scope.
The new panel is historically exposed and label-conditioned; direct contributor
separation is not biological independence, simultaneity or unknown-trial generalization.
The source-pool intervention is not a calibrated biological sample-efficiency law;
the single permutation is an alignment-breaking diagnostic, not a significance test.

## Draft-PR follow-up — October24

The owner subsequently requested a draft PR explaining the structure and how to review
it. Branch `feat/fresh-input-notebooks` contains the implementation, executed invented
source notebooks and reviewed documentation/aggregate notes. The PR description is
its review guide; earlier uncommitted/no-publication statements are dated execution
checkpoints, not a restriction on this separately requested draft.

Private inputs, real executed notebooks/figures, predictions, fitted models, manifests,
launch wrappers, runtimes and receipts remain ignored/local. Unrelated current-state
notes and the stash are excluded. No further scientific execution, automatic retry,
merge, license grant or package-registry publication is authorized by opening the PR.
