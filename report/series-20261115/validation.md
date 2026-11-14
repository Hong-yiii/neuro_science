# Synthesis validation — November 15, 2026

Status: manuscript and figures implemented; rendered-page checks and the three
blind manuscript audits are in progress. No publication or merge has occurred
for this paper yet.

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
Ruff passed for the figure builder. The paper PDF will additionally receive page,
cross-reference, text and visual checks before audit.

## Preservation and publication

Work is isolated to the new `report/series-20261115/` package on
`docs/series-paper-20261115`, based on PR31's completed head. Existing accepted
executions, source notebooks, prior reports, private artifacts and runtimes are
unchanged. The unrelated `src/neuro/_cebra_sampling.py` working edit and untracked
`docs/reports/current-state-20260927/` are excluded. A task-local Tectonic binary
was downloaded under ignored `work/series-paper-20261115/runtime/`; no scientific
environment was modified.

The manuscript PR will follow the three audit passes. If PR31 remains open, it
will be stacked on that branch to keep the review diff limited to the paper.
Neither PR will be merged by this task.
