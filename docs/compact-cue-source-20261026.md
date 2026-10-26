# Compact unbinned cue source — October26, 2026

## Authority and outcome

The owner confirmed lab permission, requested public source without incidental
metadata, then explicitly chose **compact unbinned source in ordinary Git only**.
This supersedes the earlier proposed full-native archive and the October23 private
input restriction only for this bounded source view. No Release was created/uploaded,
no LFS/new license/merge/package publication, and no model fitting was performed.
Independent artifact/privacy and code reviews passed after the corrections recorded
below. The existing [draft PR22](https://github.com/Hong-yiii/neuro_science/pull/22)
is the publication/review authority; this is not a GitHub Release or merge.

`data/cue-source-v1/` has64files, **54,685,403 bytes**, largest blob
21,562,316bytes (`spikes.npz`). Final manifest SHA256:
`8af267ca189a98a3bcc3c24e498259d36079e41402a6cf2fdb9a0d9e5291ed11`.
The manifest authenticates61payloads; its checksum and opt-in notebook configuration
are separate. [Data schema, clocks, omissions and checksum usage](../data/README.md)
are the public source contract, not a promise to reconstruct full native MAT objects.

## Export and conservation

The exporter was run with the retained scientific runtime, one numerical thread and
a360-second timeout. Initial arguments were explicit:

```sh
PYTHONPATH=src scratch/v6-v9-runtime/bin/python scripts/export_cue_source.py \
  --root . \
  --inventory outputs/prospective_path_first_run/place195-all-sessions-20260830-v4/source_files.csv \
  --outer outputs/prospective_path_first_run/place195-splits-20260830-v3/source_trial_splits.csv \
  --inner outputs/start-goal-cebra-20260907/source_splits.csv \
  --output work/compact-cue-source-20261026/candidate-final \
  --revision d926c60184594f233dced2b287c3990ed71caad2+compact-working-tree
```

All370native file hashes/sizes were checked before and after export. The two assignment
input hashes are pinned in the exporter and recorded in the public manifest. Written
numeric array values, dtypes and shapes were compared immediately with input arrays;
NPZ contains no pickle/object arrays. Fixed ZIP metadata, sorted keys and deterministic
gzip timestamps avoid run-time timestamps in artifact hashes. The original selection
list order is preserved after removing machine prefixes.

Coverage:195units/58sessions; **5,576,459 unbinned spike timestamps** (all splits,
no sorting/deduplication/clipping); **7,761,853 Unity marker/delta rows**, including
zero/startup rows; **23,901 ordinal-joined trial records**,23,200success and701timeout.
Ripple raw marker stream/trial references and small Eye event/mask/clock arrays are
retained. Continuous gaze, dense Unity x/y/heading, private paths, MAT scaffolding,
embedded patch, notes/logs/spreadsheets, fitted states and predictions are excluded.
No numeric trial record is dropped by the export because of eligibility or mismatch.
The first redundant-double/Unicode-token candidate was118,700,936bytes. It was retained
locally and rejected for size; final exact ASCII timing tokens avoid duplicated floats.
The older full sanitized archive/rejected evidence remains untouched and unuploaded.

Independent review rejected the first compact manifest `d7dd682d…8170`: five Eye
`timeouts` arrays lost their MATLAB-empty interpretation, and three raw Ripple sample
rates were omitted. The corrected exporter retains essential per-array MATLAB
class/empty/integer-decode attributes and `Args/Data/SampleRate`, without changing
existing backing values. It also records SHA256s of its three producer/helper modules.
Task `ba8fe5bef` reran the command above with output `candidate-reviewed` and revision
`d926c60184594f233dced2b287c3990ed71caad2+reviewed-compact-working-tree`; it passed in68s.
The old Git candidate is retained at `work/compact-cue-source-20261026/pre-review-git-candidate/`.

Final independent artifact/privacy review `386fc1ca` authenticated the final hash:
370 original inputs before/after; 195 ordered units; 1,738 pre-existing arrays unchanged;
1,098 current session arrays bit-exact against native HDF5; 1,103 essential attributes;
23,901 outer/15,553 inner assignment rows; all61payload hashes and three producer hashes.
The prior full native comparison of every spike/Unity value carries forward through
unchanged authenticated payloads. All five empty encodings and three added rates passed.
A scan of12,279JSON strings and1,741NPZ members found no private paths/embedded patches
or unrelated metadata. Dates/recording identities intentionally remain public.

## Historical metadata reconciliation, not historical result identity

QA-only reads of authenticated historical `trials.csv` and `units.csv` compared fresh
metadata, not source truth/runtime dependencies. All23,901trial ID/session/order/
predecessor/outcome/digit/provisional endpoint/multimodal-code/QC fields matched;
all195unit identities matched. Largest native versus nine-significant-digit CSV cue
duration difference: **3.3342204552866406e-9seconds**. Native values were not rounded
away. No historical neural count/event CSV, saved model, prediction or score was read
for comparison; no historical score or bin-identity claim is made.

The shared pure historical selector reproduces:

-15,553eligible outer-train sources,12,288inner train/3,265exposed development;
-5,872development contributors;4,427training sources embargoed,7,861survive globally;
-13zero/73singleton/1,654two-plus original block/pair training pools;
-10complete-support blocks,27units;1,415train/551development sources;
-zero overlap of final train/development contributor unions.

Native Eye `missing_idx` contains three masked events (all events of one trial).
They remain raw evidence plus an explicit one-based observation mask, not observed
zero codes/timestamps. None is a selected source or its predecessor. The historical
QC-policy ledger is explicitly distinguished from native observed validity; selected
contributors with missing Eye events fail closed. Labels and ordinal stream joins
remain provisional, and historical exposure is not repaired by this export.

## Executed checks and NotebookA

Initial invented-only tests passed14/14. Review added regressions and the final
combined run `b5f6d97e4` passed **25/25** (0failures,0.604s). These are overlapping
suites, not additive totals. No broad discovery or fitting test classes were launched:

```sh
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONPATH=src:. \
  scratch/v6-v9-runtime/bin/python -m unittest -v \
  scripts.test_cue_source scripts.test_fresh_notebooks.AdapterTests \
  scripts.test_fresh_notebooks.TimingAndArtifactTests.test_notebooks_expose_calls_and_have_no_private_default_paths \
  scripts.test_fresh_notebooks.TimingAndArtifactTests.test_kernel_code_identity_drift_rejected \
  scripts.test_public_workflow.SourceContractTests scripts.test_public_workflow.AssemblyTests
```

These cover MATv5/v7.3 full-precision order/duplicates, deterministic no-object NPZ,
Unity orphan/startup/all-delta reconstruction, explicit event axes/singletons/3×3,
Eye one-based masking and zero observations, exact half-open bins, source identity/
frozen assignment joins, embargo/support/reuse, root confinement/hash failures,
duplicate/oversized payload rejection, forged selection and compact kernel/biological
gates. Legacy six-file adapter tests still pass. A structural regression prevents the
whole-A guard leaking into the shared B/C common cell. Review also exposed a forged
NPY-header allocation path and mutable dataset-pin rebinding. Headers/names/dtypes/
shape-byte totals now validate before allocation (including zero-width string dtypes),
and both compact/legacy selections retain immutable configuration fingerprints checked
before reinspection. New tests reject actual nested pin mutations before data access.
Independent code re-review `59858adc` found no remaining findings; it inspected tests
but did not execute them. Parent executed the final25-test suite above.

Non-fitting native reconstruction QA used `no_fitting()` **before input inspection**:
`work/compact-cue-source-20261026/validate_candidate.py` → `validation.json`.
It freshly produced shape(1966,27,10),53,090observed bins/477,730unavailable bins,
38,012observed zeros;28,116full-cue spikes,518tail spikes beyond the first second.
480train/240development synthetic rows reconstructed exactly from their plans.
Train:1,351used/64unused/1,157repeated real sources. Development:544used/7unused/
510repeated. Resampling does not produce new measurements. QA took15.56seconds wall,
415,988KiB peak RSS, zero swaps observed by `/usr/bin/time`.

NotebookA was actually executed in a fresh kernel with the existing `no_fitting`
context held across all10code cells, before source work; fit accounting began early.
All cells and authenticated no-fit artifact replay passed. The first executor attempt
failed *after* cell completion because the inherited read-only notebook tooling overlay
lacked its Jupyter HTML template search path. Failure is retained at `executed-a/`.
A deliberate corrected run set `JUPYTER_PATH` to the existing overlay's `share/jupyter`
and passed at `executed-a-v2/`:17.36seconds stage execution,623,448,064bytes sampled
peak owned RSS,2,538,495bytes outputs;120s/2GiB/128MiB limits, two numerical threads.
No dependency was installed or runtime changed. Kernel/model/data configuration pins,
output privacy checks and fit-blocked replay passed. Zero PCA/logistic/LDA/CEBRA/
optimizer updates; no optional torch/CEBRA module loaded in A.

The command was `scripts/execute_fresh_notebooks.py --notebooks 01_pseudopopulation
--allow-biological --timeout-seconds 120 --memory-gib 2 --output-limit-bytes 134217728`,
with explicit scientific interpreter, source/tooling dependency paths and the hash-pinned
private `execute-a-config.json`; full invocation/receipt/resource evidence is retained
under `work/compact-cue-source-20261026/` and Pi task logs. A current-cell-source equality
check against the executed notebook passed. Source notebooks intentionally retain empty
outputs deliberately; no private executed artifacts were copied into Git.

After review corrections, fresh task `be12a0507` repeated only NotebookA against the
final source/data pins, using `execute-a-reviewed-config.json` and `executed-a-reviewed/`.
All10cells and no-fit replay passed in17.413s stage time; sampled peak owned RSS
623,017,984bytes, output2,538,608bytes, same120s/2GiB/128MiB bounds. Zero fits/optimizer
updates and no optional torch/CEBRA imports. Earlier attempts remain retained; the final
receipt, not `executed-a-v2`, binds the corrected code and final dataset.

B/C were **not executed**. Every B/C markdown/code cell source equals HEAD byte-for-byte;
only stale outputs/execution metadata were cleared. Their model grids are unchanged.
Both compact and legacy modes require equivalent biological/config/kernel gates.
Default notebooks remain invented and explicitly opt in to real source.

Ruff check/format and `git diff --check` passed. Primary LSP diagnostics found no errors
in10affected files, with8confirmed clean and2initially timing out (not a full-project
certification). No service/network change or retained worker was introduced.

## Limits and handoff

This is software/source validation and an exploratory non-fitting construction, not a
new biological study. Native precision/boundary policy can change fresh bins versus
historical serialized pipelines. No causal, simultaneous-dynamics, pristine holdout,
biological-IID or historical score reproduction claim. Dates/session/unit IDs and
scientific headers remain intentionally public, so sanitization is not anonymity.
The compact view cannot replace full raw recordings or reproduce omitted dense streams.
Independent artifact/privacy and code reviews passed within their stated scopes;
parent-run final checks and NotebookA passed. The PR head records publication status.
No staging, commit, push or publication was performed by the implementation worker. Protected originals, saved
models/results, retained runtimes, stash, unrelated dirty sampling formatting and
untracked current-state notes were preserved.
