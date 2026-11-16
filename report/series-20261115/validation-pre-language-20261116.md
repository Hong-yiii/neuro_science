# Class-panel context validation — November 16, 2026

Status: **complete — the final 20-page manuscript passes all three fresh blind
reviews; every reviewer explicitly finds it understandable**.
The [preceding 18-page validation](validation-pre-panel-20261116.md), its exact
approvals and the [earlier November 16 follow-up](audit/followup-20261116.md)
remain intact. [PR32](https://github.com/Hong-yiii/neuro_science/pull/32) reviews
against `main` after PR31 merged; this task does not merge either PR.

## Authorized addition and evidence boundary

The owner requested a defensible explanation of the frozen nine-class task:
full 6×6 source distributions, per-pair session support, the fixed-K frontier,
and why complete class support constrains population width. This is dated
**metadata feasibility**, not a new decoding experiment. K=9 was fixed before
selecting its pairs. Other class counts contextualize the design; they do not
replace it or alter any of the completed 48-case results.

The [study note](../../docs/experiments/source-reuse-width-20261114/class-panel-20261116.md),
[verification script](../../docs/experiments/source-reuse-width-20261114/verify_class_panel_20261116.py)
and [receipt](../../docs/experiments/source-reuse-width-20261114/class-panel-metadata-20261116.json)
are pinned in the manuscript at commit `5a9e54cb75efa1ca1e9d1e918fa9defd57967ee4`.
Experimental evidence remains pinned at `a0ca80180e2bb52b90e499357d3d6965b26806da`.

## Verification actually performed

The script calls the study's own `metadata()` and `select_panel()` on
`data/cue-source-v1`. All 90 off-diagonal counts in the three matrices agree
with the supplied expectations. All nine fixed-K frontier rows agree; the
returned panels report optimal, zero-gap outcomes. Direct checks reconcile
session membership, width, class cardinality and endpoint incidence. At K=9,
the complete panel and all three `derive_rosters()` outputs match the frozen
`design.json` exactly. A direct training-only check confirms that no session
has three training sources in every one of the 30 classes.

Only the public manifest and frozen outer/inner assignment tables were read
from the compact source. Named fitting entrypoints, `study.materialize()`,
`study.prepare_design()` and `numpy.load()` were blocked, with an audit hook
rejecting other compact data and local output reads. These are explicit checks,
not a universal filesystem sandbox. Scikit-learn definitions were imported;
Torch and CEBRA were not. No model fit/replay, notebook execution or neural-array
access occurred. The input, original code and frozen design hashes authenticate.

The initial successful receipt and verifier are preserved under ignored
`work/class-panel-20261116/`. A second metadata-only verification corrected an
overly broad runtime-field name and added direct inventory/incidence checks;
its final receipt is the tracked one. Both agree on every displayed number.
No completed scientific run was repeated.

## Paper and figures

The paper now has **20 A4 pages, 14 labeled figures and 10 tables**. Pages 6–7
add the all-pair distribution and session-support figure, the intersection
formula, exact optimizer hierarchy, class-count plot/table and endpoint-only
6/K ceiling. The 16/8 training/development row counts explicitly apply to the
primary arms. The once-only arm and every completed result retain their prior
values and interpretation.

The new renderer consumes the authenticated receipt, without importing study
code or invoking optimization. Its 30-row marginal CSV, nine-row frontier CSV
and four vector/preview figures authenticate in
[class-panel-figure-provenance.json](class-panel-figure-provenance.json).
Deterministic rebuilding passed in the recorded environment. The prior 32
CSV/figure artifacts, original renderer and original provenance are unchanged.
Cross-version figure-binary identity is not promised.

A Tectonic 0.17.0 build passed with zero warnings, unresolved references or
bad boxes. All pages were rendered; the added pages and changed reference page
were inspected at full-page size. An isolated archive of Git tree
`fa96cbabed22e44485fd05e48014fdeedee5a3b3`, containing only TeX, Makefile and
figures, rebuilt with identical extracted text and no scientific runtime or
notebooks. All 39 PDF fonts are embedded and all 33 pinned repository links
resolve in Git. TeX timestamps can change PDF bytes between builds; review
binds the delivered artifact below.

| Delivered artifact | SHA256 |
| --- | --- |
| `paper.pdf` | `f5a1783a3673ff5a788af8210bfb876e7045fb531d06354f1a248dbd4ba270f9` |
| `paper.tex` | `a3df343e3add19089e7e497d872d4d45eb36aca74ef4a79ddfe65aebe6667d28` |
| Metadata receipt | `8f6560aa172c86a53f211596bce9333ee410281210f2c518ad3a8503a572316a` |
| New figure provenance | `dee2b1ccb57194dccd1bbcc8db4650084486a7d7a8a3c6e85191229e76d549b5` |

## Independent review

Fresh newcomer, neuroscience-researcher and quantitative/provenance agents review
the changed paper and its evidence without the drafting transcript, author-side
probe, old review findings or one another's reports. Their final artifact-bound
verdicts are recorded in the [audit index](audit/README.md). These are AI
manuscript/evidence audits, not external human peer review or new biological
replication. The earlier 18-page approvals are not reused as approval of this
revision.

All three reviewers returned PASS / UNDERSTANDABLE for the exact hashes above.
The newcomer read and inspected all 20 pages. The researcher independently
recounted the three matrices and all returned-panel gates, while the quantitative
reviewer additionally reproduced both width optima with a separately formulated
binary optimization and reran the exact metadata verifier to an identical receipt.
Both checked the frozen rosters and the interpretation of the endpoint-only bound.
The primary-arm wording finding was corrected before final approval. A disposable
page-6 preview was refreshed to match the unchanged final PDF; the newcomer
confirmed pixel equality. The optional diagonal-legend wording suggestion remains
nonblocking because the caption already identifies excluded self-pairs.

[Class-panel artifact checks](audit/class-panel-artifact-checks-20261116.json)
bind the final artifact, input and review identities. No scientific outputs
changed during the review.

## Preservation and remaining limits

All 45 pre-existing study files other than the two deliberately extended entry
notes are byte-identical to `5ac3e5a681e0eee3229adc8f36088c1c37906f48`. This covers
the frozen protocol/design, study implementation, source notebooks, published
executed notebooks/HTML, aggregate figures and prior validation records. No
original output directory, failure or model state was accessed or modified.
The follow-up audit already on the remote branch was fast-forwarded into this
checkout before adding the new record, preserving its text and remaining gaps.

The earlier follow-up's development-utilization, task-orientation, accessibility
and cross-version binary limits remain; this addition addresses class feasibility.
The PDF remains untagged, and a full grayscale/print audit is not claimed.
Known-label construction, exposed development, source dependence and missing
acquisition/spatial evidence still bound the scientific conclusions.

The current checkout's unrelated `src/neuro/_cebra_sampling.py` edit remains at
SHA256 `63489315c5a21257ed037edd77161f639beb23199321719d8fe22a562c1659f5`;
untracked `docs/reports/current-state-20260927/` is excluded. The earlier follow-up
records a different checkout state; its historical preservation account is not
rewritten. No new fits, notebook outputs, model results or merge accompany this
publication update.
