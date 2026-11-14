# November11 execution and independent validation

The [result note](README.md) owns the scientific interpretation; the
[frozen protocol](../../population-grid-protocol-20261111.md) and
[metadata design](../../population-grid-design-20261111.json) own the prospective
choices. This is an exploratory analysis of existing recordings. Separate agents
reviewed code, scientific assumptions, numerical evidence and presentation; this is
independent computational review, not external human peer review or biological
replication. No reviewer fitted or loaded models, replayed biological models or
reconstructed neural arrays from raw spikes.

## Preflight and preserved failures

Nine focused software tests passed before fitting: three new exact-optimization,
tie-breaking and nested-projection tests, plus six existing construction/control
checks. Independent review exercised 72 invented plan comparisons. All 216 native
non-fitting source plans passed eligibility, contributor separation, selected Eye
availability and rank-seven checks. A separate invented rendering check produced
29 overview figures.

The earlier rank-eight preflight failed only in K30/S33/U2 and R16 under null
60002, a smaller-roster control outside the scheduled fit family. Seven dimensions
were fixed before biological fitting; this is a conservative engineering choice,
not a biological dimension estimate or proof that a scheduled eight-dimensional
fit was infeasible. The failed check and rank inventory remain in
`work/population-grid-20261111/`.

Benchmark01 preceded the expanded native/decoder matrix and was superseded.
Benchmark02 completed all 51 invented fits and 2,000 updates, but failed the
original three-hour resource estimate: 129.74 seconds per case, native 109.23.
Benchmark03 used one thread for native fitting and completed all fits/replays,
but also failed that estimate: 121.3859 seconds per case, 126.030517 for the full
runner, native 101.8542; peak about 829.8 MiB, zero OOM. Neither failed receipt
was relabelled as passing.

Before any biological fit, an independently reviewed resource-only amendment
accepted a six-hour ceiling: 111 × 126.030517 × 1.25 + 1,200 = 18,686.73 seconds,
below 21,600. The model grid and update counts were unchanged. The review
authenticated all 66 benchmark files and the gate
`work/population-grid-20261111/expanded-resource-gate-reviewed.json`, SHA256
`df8f7cfeff287643804c8cf869f529564cc294f9b4ec6018f9f790e974b77c6c`.
These are invented computation/resource checks, not scientific model evidence.

## Completed biological computation

The sole new run is `outputs/population-grid-20261111/real-01/`, executed by
`neuro-grid-real-20261111.service`. The unit finished successfully and is inactive.
All 111 cases have exactly one started/completed event pair; there were no
biological failures or retries. The 81 observed cases cover nine configurations ×
three policies × seeds 0/1/2; the 30 controls cover three full-roster tasks ×
U2/F16 × five joint pair-label permutations.

| Accounting item | Completed |
| --- | ---: |
| PCA fits | 111 |
| CEBRA-Time encoder fits | 111 |
| Native multisession ensemble fits | 111 |
| Session-specific networks inside native ensembles | 2,174 |
| Logistic / SVM / kNN / LDA fits, each | 1,332 |
| Model-fit calls, excluding scalers | 5,661 |
| Adam updates | 222,000 |
| Saved encoder objects checked | 444 |
| Saved readouts checked | 5,328 |
| Composed train/development readout passes, fits/updates blocked | 10,656 |
| Sequential notebook code cells without errors | 12 |

Wall time was 7,054.9485 seconds (117.5825 minutes), with peak cgroup memory
2,776,887,296 bytes = 2,648.2461 MiB. Hard limits were `memory.max=4294967296`,
`memory.swap.max=0`, `cpu.max=200000 100000`, and six hours. All memory-event
counters were zero, including OOM and OOM-kill. Execution source revision is
`8ee7b69`; the exact pre-existing dirty sampling-file hash, package versions,
input hashes, configuration and source closure are recorded in the run. It is
not represented as a clean-tree run.

## Numerical and scientific review

The parent verifier, `scripts/verify_population_grid_results.py`, loaded saved
numeric arrays and predictions only, with no model loading/fitting/replay. Its
receipt `work/population-grid-20261111/final-numeric-audit.json` reports:

- All 7,210 immutable-run files authenticated against the supplied receipt.
- All 5,328 metric/confusion records recomputed and reconciled.
- All 3,666,288 source-error participation records reconciled.
- All 2,174 native session-encoder records accounted for.
- 54 exact nested-array comparisons, 27 common-source policy comparisons and
  39 fixed development-world comparisons passed.
- All 246 figure identities and 12 executed cells accounted for.

The independent protocol reviewer authenticated all 7,210 files and 6,771 case
artifact references, the full case/event schedule and all fit/update counts.
Additional independent checks during execution covered:

- Nine K30 seed0 observed cases: 549 files and 432 readouts on both splits;
  source eligibility/embargo, subsets, F16 coverage, projection and SVM handling.
- Twelve K20/K15 full-roster U2/F16 observed cases: 732 files and 576 readouts on
  both splits; 111,996 repeated source/unit-block comparisons matched, spanning
  4,794 distinct blocks. Frozen development arrays and lineage were identical
  across policies/seeds. No exact complete raw row crossed splits in this subset;
  this does not assert statistical independence or absence of shared components
  within a split.
- Six null60000 cases: 366 files, independent reconstruction of permutations and
  source selection from public metadata, 49,130 assembled source appearances and
  576 truth arrays. Original session×split class counts were preserved.

The review explicitly checked source leakage, predecessor exclusion, dependent
bins/rows, label-conditioned assembly, exposed selection/evaluation, degree
constraints, decoder regularization, SVM margins, native supervision/pooling,
control scope and the difference between optimization and endpoint association.
The native U2 pair/start control overlaps and nonmonotonic width/source effects
remain in the report. Five null worlds and three computational seeds are not
p-values or biological uncertainty intervals.

Review corrected two explanatory statements before collation: unused development
sources arise from random draws with replacement, not an eight-row quota smaller
than their pools; increasing total source availability as K falls is true for the
full eligible rosters, not every smaller roster. No data or model was changed.

## Original artifact and privacy review

The independent artifact reviewer verified that original HTML and notebook each
embed exactly the 246 PNG hashes in `figure_provenance.json`: 29 overview pages,
28 loss pages, 81 trajectories and 108 pair-confusion pages. The notebook has
12 sequential code-cell execution counts and no errors. There are 3,888 observed
and 1,440 control metric records; invented benchmark outputs are not used as
biological evidence.

Against 15,806 known metadata identifiers, the reviewer detected no original
unit/session/trial identifiers in displayed report/notebook content. All
7,829,238 checked alias fields across 3,957,260 sidecar rows follow the declared
alias formats. No credentials, original private-input paths, raw-array/model-state
binary payloads or individual prediction dumps were detected in advertised
report/notebook payloads. Aggregate results are still exploratory data, not a
public release authorization.

Representative actual figures were viewed by the parent and reviewer, including
availability, reuse, log loss, control plots, learning curves, confusion matrices
and trajectories. Data, ticks and axes are legible; some native trajectory panels
partly clip the rightmost “Coordinate3” label. This is a nonblocking layout limit;
the data and tick values remain visible and numeric coordinates are retained.

The original `population_grid.notebook.html` nbconvert derivative requires CDN
RequireJS/MathJax. It remains immutable and is **not** an advertised offline
deliverable. The standalone report, saved `.ipynb` outputs and disposable teaching
HTML are the intended reading artifacts.

## Interpreted deliverables

`scripts/collate_population_grid_deliverables.py` authenticated the completed run
and added the independently reviewed interpretation. It imported no scientific
model and performed no fitting, model loading or biological replay. The result
is the separate `outputs/population-grid-20261111/deliverables/` directory.

The independent final collation review authenticated all 271 manifest files
(876,059,045 bytes), including 268 byte-identical copied artifacts. All 24 original
notebook cells remain unchanged and ordered, including all 12 executed code cells
and saved outputs. One interpretation Markdown cell adds three authenticated
PNG attachments. Report and notebook each contain 249 image occurrences,
representing the 246 original distinct figures plus three narrative repetitions.
All 19 copied numeric tables are retained. Every relative report link resolves.
All 7,210 original receipt-bound files were rechecked and remain unchanged.

The final report is self-contained, with no required external scripts/styles.
The privacy review found no model binaries, raw neural arrays, individual
prediction dumps, secrets, original private-input paths or unaliased record
identifiers in the advertised payloads. The report is about 127.7 MiB and the
notebook about 104.4 MiB; the numeric table sidecars account for much of the
larger deliverables directory. Read saved outputs rather than rerunning models.

The disposable `/teach max` HTML embeds the exact 5,328 aggregate metric records,
222 complete optimization curves and 81 observed trajectory sets, plus five
receipt-authenticated figure occurrences. All 81 design/target selections and
encoder/decoder/seed/geometry controls passed a DOM check. Independent review
identified small interactive-trajectory clipping; the display now uses isotropic
radius-based scaling with visible coordinate extents. All 2,369,250 checked
point/rotation combinations stay inside the viewport. The independent final
teaching review accepted the corrected artifact, its source references and all
stated numerical/causal claims. These checks validate payloads and control logic,
not native Mac rendering.

Ruff passed for the new numeric verifier and collator; final whitespace and
local-link checks passed (196 local document links). All 34 pinned execution
source files remain unchanged, and source Notebook06 has empty outputs. No further
model execution was used for presentation.

## Artifact identities

| Artifact | SHA256 |
| --- | --- |
| Immutable run receipt | `6f070f514d98898df1121e6074e1ffef66e662963902706cab62032a85486869` |
| Reviewed result-note source | `2df1167470cb3737d98e91777efd1f3e1573109f13df75cd1dff51fa769e6453` |
| Interpreted report HTML | `8c587158471f487ba90b804ed1af0b3cc18ae6a3e2d06dc7461f21c922d3eec7` |
| Executed notebook | `b54e933629802ed6f7dd9c33aa964621dd8da943d939f6fccfe1f4c5978a4858` |
| Collation manifest | `2fd29557e906718f465ae4a1eff3c78d45cc9436c06fc788024bb0e7c048af89` |
| Final numeric audit | `253196a6ecd4b04f755bdd55e8a5b9b91d731106288c0a7d5d237ee3d26931b5` |
| Disposable teach HTML | `10eec3b5d205639c6a7abc69e4622b0073f3ef48fb04a2fd4efb71bfde942121` |

Numeric verifier SHA256:
`8d4c596d4308b9da7a07affac56906bcedca0d11f0191dbe168ce4168b937940`.
Collator SHA256:
`4831003a12ffbf29504757b59e28122c0a4e9054bb2103758d4afb4a096a8d22`.
The independent narrative review checked 138 numerical entries/groups plus all
stated control-separation and class-error findings before the note was frozen.

## Preservation and delivery

The original run, model states, predictions, failed preflights/benchmarks and all
older studies remain intact. Scientific run outputs and interpreted artifacts
remain ignored/local; Git receives only implementation, empty-output source
Notebook06, reviewed aggregate notes and entry-point updates. The pre-existing
sampling-file edit, current-state notes, runtimes, submodules and stash remain
outside this change. No push, merge or issue edit was performed; no additional
fit or automatic retry is queued.

The single disposable lesson is on `hongyi-server` at
`/tmp/pi-teach/20261111-032858-population-grid-max/population-grid-max.html`.
Its directory/file permissions are 0700/0600. The delivery preflight's session API
and tab listing succeeded, but the inherited terminal had zero matching pane
placements. The teach skill requires a unique owning pane, so no browser tab or
HTTP server was created and no existing owner/relay was changed. A private-copy
Mac handoff is supplied with the result; native rendering is unverified.
Delivery and interaction receipts remain under `work/population-grid-20261111/`.
Delete only the disposable lesson with:

```sh
rm /tmp/pi-teach/20261111-032858-population-grid-max/population-grid-max.html
```

The lesson is temporary and outside the repository; the scientific report,
notebook and durable conclusions are independent of that file.
