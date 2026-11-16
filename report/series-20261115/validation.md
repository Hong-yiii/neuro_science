# Qualitative CEBRA overview — November 16, 2026

**Complete: all three fresh independent AI-agent reviews pass and find the
changed explanation understandable.** The paper remains 21 pages with 14 figures
and 11 tables. [PR32](https://github.com/Hong-yiii/neuro_science/pull/32) remains
open against `main`.

## Change and evidence

Page 2 now explains what improves with distinct recorded trials, repeated row
assembly and larger populations. A plain-language comparison table states what
changes and what stays fixed. The overview uses descriptive constructions; page
6 pairs each later figure code with its construction name. Page 1 adds the
source-pool definition before later uses. The exact mean rankings remain in the
unchanged accompanying CSV/LaTeX artifacts, and pages 16–17 retain the detailed
results, repeats and controls. The PDF build now uses only TeX and figures.

The interpretation remains specific to the tested constructions and classifiers:
CEBRA-Time benefits from more distinct trials; repeated assembly helps selectively;
PCA has the strongest wider-population means; and the configured multisession
CEBRA mean falls at the final expansion. The overview explicitly retains the
one-improving/two-declining PCA/SVM repeats and the scope of the development data.
The opening avoids conflating once-only and repeated three-trial constructions.

This is an editorial change. No fitting, model loading/replay, neural-array read,
notebook execution or metadata optimizer rerun occurred. Review arithmetic used
existing saved scalar scores. The completed 48 cases and all experimental outputs
are preserved.

## Checks and review

The [fresh review panel](audit/README.md) assessed the changed interpretation,
construction clarity and saved-scalar evidence without the drafting transcript,
prior audit findings or one another's reports. All three returned
**PASS / UNDERSTANDABLE**, with no required revisions. The newcomer visually
checked pages 1, 2 and 6 and read the supporting results. The scientific reviewer
matched all 768 pair scores and 96 means to original saved scalars. The quantitative
reviewer independently checked all 96 summaries, 24 rankings, 896 pair contrasts
and the six construction counts. These are scoped AI artifact reviews; they do
not repeat the historical biological execution audits.

Tectonic 0.17.0 produces 21 A4 pages with 40 embedded fonts and no warnings,
unresolved references or bad boxes. An isolated archive of Git tree
`f032bbf6902a4a863f15518f39020a925ef3778b`, containing TeX, Makefile and figures,
builds with identical extracted text. All 33 pinned repository paths resolve.
Only pages 1, 2, 6 and 21 have changed extracted text relative to
`3416df8f085b4fce76951e922c61663e3147f5a2`; all other page text is identical.

| Delivered artifact | SHA256 |
| --- | --- |
| `paper.pdf` | `ed5c207f3fd85a4e0d41f0d39d6c9b1219d85def770eede716947586615ac72c` |
| `paper.tex` | `8f30636542bee0768208a5536d1bdb7428b8445dfc798378bbda57cc5030204c` |

The [artifact checks](audit/overview-artifact-checks-20261116.json) bind the build,
preservation checks and reviewer identities. All 97 pre-existing files in the
protected evidence scope match their baseline bytes: report data/figures and
generators, study implementation, source/executed notebooks and study records.
This includes all 41 package data/figure artifacts. No numerical artifact was
regenerated for this revision.

## Preserved records and limits

The [preceding full language validation](validation-language-20261116.md) and
[its audit index](audit/language-index-20261116.md) are exact copies of their
baseline versions. Their 268-check full quantitative review remains attached to
its original PDF/source identities. All prior detailed reviews remain unchanged.

The prior development-utilization, acquisition/task-context, spatial-evidence,
PDF-accessibility and cross-version limits remain recorded in the earlier
ledgers. The PDF remains untagged; a full grayscale/print audit is outside these
checks. Known-label assembly, shared sessions, source dependence and inspected
development data still constrain interpretation.

The unrelated `src/neuro/_cebra_sampling.py` edit remains at SHA256
`63489315c5a21257ed037edd77161f639beb23199321719d8fe22a562c1659f5`.
Untracked `docs/reports/current-state-20260927/` is excluded. This publication
update leaves the PR open for review.
