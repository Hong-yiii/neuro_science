> Historical validation of the original ten-page manuscript at commit
> `29364d8dc93e672112a1771ba83534f19171922c`. The hashes and approvals below
> belong to that version. See [current validation](validation.md) for the methods
> expansion; these earlier passes do not approve the new artifact.

# Synthesis validation — November 15, 2026

Status: **completed — all three blind auditors pass the final ten-page PDF and
explicitly find it understandable**. The publication package also passes an
isolated Git-tree build. Published for review as
[PR32](https://github.com/Hong-yiii/neuro_science/pull/32), stacked on PR31.
GitHub owns the current publication status; no merge is authorized or performed.

## Authority and evidence boundary

The owner requested a roughly ten-page, paper-quality LaTeX synthesis of the
entire repository series, weighted toward the latest work, after today's
experiment completed and appeared as a PR. Polling began while the complete
notebook reproduction was running. Its final receipt reported completed, the
validation ledger then recorded independent acceptance, and GitHub was checked
for [PR31](https://github.com/Hong-yiii/neuro_science/pull/31) before paper work
began. PR31 was open/draft with head
`a0ca80180e2bb52b90e499357d3d6965b26806da`.

The owner subsequently required three auditors, including a newcomer and an
experienced researcher, to pass the manuscript and find it understandable before
opening a PR. The third role is quantitative/provenance review. No new research
or experiment is authorized; small explanatory gaps may be filled.

Only existing tracked reports, protocols, code, public aggregate notebook outputs
and existing bibliographic entries were used. No raw/neural-array read, fitted
model deserialization, prediction replay, model fit, source reconstruction or new
literature search occurred. Diagrams restate the existing pipeline. Plotting and
checking already reported aggregates are presentation work, not a new study.

## Evidence probes and figure extraction

Two separate agents probed the recent scientific interpretation and historical
trajectory. A third built figures from the public notebook tables. These agents
are distinct from the final blind manuscript auditors. Their local working memos
live under ignored `work/series-paper-20261115/`.

The probes caught important compression hazards: PCA is not the only model with
increasing mean width scores; its final SVM width gain occurs in only one repeat;
latest once-only conclusions must not inherit stronger November11 endpoint-head
claims; and the three different nine-class/nine-population designs are distinct.
The manuscript retains these distinctions.

The figure builder authenticated both notebooks and the publication manifest at
the pinned revision. It extracted 1,536 reuse and 1,152 width score rows, removed
384 exactly equal B3 duplicates, and retained 2,304 unique score rows. All 2,688
paired contrasts equal their after-minus-before case scores exactly. Selected
confusions have nine class rows of eight, total72, and agree with recorded balanced
accuracy. No per-example predictions or full lineage are exported.

The three new quantitative figures are vector PDFs with embedded TrueType fonts.
The historical time-decoding PNG is byte-identical to the tracked source. Exact
inputs/outputs, extraction locations and plot-selection caveats are recorded in
`figure-provenance.json`. Two builds produced identical figure/table hashes;
Ruff passed for the figure builder. The final PDF has ten A4 pages, six labeled
figures, three tables, embedded fonts, 23 valid pinned repository links and no
unresolved references or missing figures. The final TeX log has no warnings,
overfull/underfull boxes or undefined references. All ten rendered pages were
inspected independently; changed pages were inspected again after the clarity pass.

## Blind manuscript panel and final identity

Each reviewer started in a separate context without the drafting discussion,
author probe memos or other reviewers' findings. The roles are AI-agent manuscript
audits, not external human peer review or biological replication. Their full
reports distinguish checked public aggregates from inherited private-run receipts.

| Reviewer | Initial verdict | Final-version verdict | Understandable |
| --- | --- | --- | --- |
| [ML-literate neuroscience newcomer](audit/newcomer.md) | Pass | Pass | Yes |
| [Experienced neuroscience researcher](audit/researcher.md) | Pass | Pass | Yes |
| [Quantitative/provenance auditor](audit/quantitative.md) | Pass | Pass | Yes |

The newcomer independently reconstructed the question, construction, counting
units, evaluation, results and claim ceiling from the paper. The researcher checked
scientific assumptions, implementation semantics, historical comparability and
all 2,304 published score rows. The quantitative reviewer independently parsed
the source tables, reconciled every contrast, recomputed metrics from all 4,608
unique published aggregate confusions, checked historical numbers from pinned
tables, and reproduced all13 CSV/figure outputs byte-for-byte in an isolated
renderer invocation. None of these reviews fitted or loaded a model.

The first reviewed manuscript is preserved at commit `cd31986`. The final clarity
pass names PCA/SVM in the abstract, defines source trials and the successful-after-
successful subset directly, names possible sensory/behavioral confounds, and links
the inherited time figure at full size. Numerical results and figure bytes did
not change. All three reviewers confirmed the new exact PDF/source identities
and retained **PASS / UNDERSTANDABLE**. Review Markdown whitespace was normalized
without changing its wording or conclusions.

| Final artifact | SHA256 |
| --- | --- |
| `paper.pdf` | `dc6ea8e5e2d422657b32ca8001eb706428bb329025fa473c9f75121bda05ba02` |
| `paper.tex` | `2f1630251df8d445e1242b028a72f94e17ce140d9dcae7164f9576c203eb6b1a` |

An isolated archive of Git tree `ddfec059a60c36109fc3b417dea1777f1c8b929f`
compiled successfully with `make -B` and Tectonic0.17.0, without the scientific
runtime or notebook sources. Its manuscript and seven figure files match the
publication bytes, and its ten-page PDF has identical extracted text and zero
TeX warnings. Only audit/administrative documentation changed after that check.
The package-local ignore exception includes the seven reviewed figure files;
unrelated generated figures remain ignored. Missing figure inputs now fail the
LaTeX build rather than producing a draft placeholder. Exact presentation checks
are recorded in [initial artifact checks](audit/initial-artifact-checks.json).

## Preservation and publication

Work is isolated to the new `report/series-20261115/` package and a link from
`report/README.md`, on `docs/series-paper-20261115`, based on PR31's completed head. Existing accepted
executions, source notebooks, prior reports, private artifacts and runtimes are
unchanged. The unrelated `src/neuro/_cebra_sampling.py` working edit and untracked
`docs/reports/current-state-20260927/` are excluded. A task-local Tectonic binary
was downloaded under ignored `work/series-paper-20261115/runtime/`; no scientific
environment was modified.

The manuscript PR follows the three final audit passes. With PR31 open, it is
stacked on that branch to keep the review diff limited to the paper. Neither PR
is merged by this task.
