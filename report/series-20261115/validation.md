# Synthesis validation — methods expansion, November 15, 2026

Status: **complete — all three original fresh blind auditors approve the final
18-page manuscript and explicitly find it understandable**. A [November 16
fresh-context follow-up](audit/followup-20261116.md) also returns PASS /
UNDERSTANDABLE in all three roles, with no material finding and a disclosed
quantitative blinding limitation. The
[original ten-page validation](validation-initial.md) and its exact approvals
are preserved separately. [PR32](https://github.com/Hong-yiii/neuro_science/pull/32)
was originally stacked on PR31. PR31 subsequently merged into `main` at
`ec730ee8d024a959d30520cb9f41bdb98882de81`; PR32 now reviews against that base
and remains unmerged.

## Authority and scope

The original request was a paper-quality LaTeX synthesis of the complete series,
weighted toward recent work, after today's experiment completed and appeared as
a PR. That gate was met at PR31 revision
`a0ca80180e2bb52b90e499357d3d6965b26806da`, before paper work began.
The owner subsequently required stronger visible methodology: what data exist,
how sources/samples are distributed, actual pseudopopulation construction, and
the results of existing validity checks. The owner asked the researcher agent
what evidence was missing, then directed work to continue until approval and the
draft update. The [critical gap review](audit/methods-gap-review.md) changed the
assessment to REVISE under that criterion. Earlier passes were not reused.

This revision adds presentation and explanation of existing evidence. It reads
tracked reports, code, public aggregate notebooks, and authenticated public
frozen assignment metadata. No raw spike/event value arrays, private outputs,
fitted models, prediction replay, notebook execution, model fitting or new
literature research are used. Metadata-only counting is a new display of the
accepted design, not a new panel, selection procedure or biological study.

## What the revision makes visible

The 18-page manuscript has 12 labeled figures and 9 tables. It adds the measured
stream inventory and physical units; inherited eligibility attrition and global
current/predecessor embargo; all latest session/class source counts and singleton
pools; the sparse source–unit membership pattern; actual published two-row B2 and
Wmid recipes; realized source use and whole-tuple repetition; and recorded
measurement, construction and numerical validation results.

The paper now includes the existing marker-to-Unity endpoint corroboration and
QC findings, first-case scaler/PCA/logistic residuals, actual learning curves,
all-case preflight/reload/reproduction results and their limits. A diagnostic
table shows training/development gaps and separately fitted start/goal heads.
Existing per-seed/control results, negative contrasts, confusions and historical
context remain. Acquisition unknowns, label-conditioned construction, exposed
development, serial/session dependence and absent spatial/transfer evidence
remain explicit. No completed software check is promoted into general biological
sampling validity.

## Extraction and independent reconciliation

The figure builder authenticates inputs against the fixed source revision and
recorded manifest hashes before parsing. The original 2,304 unique score rows,
2,688 matched contrasts, selected aggregate confusions and 13 original generated
artifacts remain byte-identical. The four new vector figures display source
support, structural membership, actual recipes and sampling realization. The
first-case image is copied byte-for-byte from the published supplement; LaTeX
crops only its two learning panels for readable printed labels. The full image
remains in the package.

New tables contain 360 session/class/split counts, 20 session summaries, 3 roster
summaries, 28 published recipe entries, 14 block-width entries, 6 published prefit
rows, one observed-mask scalar summary, 6 sampling summaries, 216 observed SVM
head/seed rows and 72 derived head summaries. Source identities are used only to
count and apply the frozen embargo; no full current/predecessor lineage is
exported. The code does not import scientific study implementations.

A separate evidence probe independently counted every metadata entry from the
public inputs. All 360 pool rows, 20 session rows and 3 roster summaries matched,
including 5,375 observed source–unit entries out of 105,991 possible entries.
The aggregate membership count is checked against the executed notebook mask
summary; no elementwise neural mask was read. Both notebooks' printed recipe,
prefit and use tables are authenticated and extracted with exact schema checks.

The builder reproduced all 32 CSV/figure artifacts deterministically under the
recorded environment. The
source manifest and [figure-provenance.json](figure-provenance.json) record
input hashes, cell/output indices, output hashes, meanings and limitations.
The working environment uses Python3.13.2, NumPy2.3.4, Matplotlib3.10.7/Agg and
Tectonic0.17.0; no scientific runtime was changed. Ruff and whitespace checks
passed. A fresh LaTeX build has 18 A4 pages and zero warnings, unresolved
references or overfull/underfull boxes. All pages were rendered and inspected;
labels and crops were corrected before the blind panel received the candidate.

## Fresh blind panel

Three new AI-agent contexts independently review the expanded manuscript:
ML-literate neuroscience newcomer, experienced neuroscience researcher, and
quantitative/provenance auditor. They receive the PDF/source identities and
review criteria, not the drafting transcript, probes, old approval records or
one another's findings. These are manuscript/evidence audits, not external
human peer review or independent biological replication.

Final approved identities:

| Artifact | SHA256 |
| --- | --- |
| `paper.pdf` | `a12d4936438baa79322a8c615db2112d8d0980f621a94c0fbbb45cb541812956` |
| `paper.tex` | `ee2027cac9a0d9c2ae911a6355a74016c5a76fe519f3221888e1e0f6aa740923` |
| `figure-provenance.json` | `1e9503f18f3f67804feb1db02ab3f60d70076e8fe16cd0670524062686002eb4` |

| Reviewer | Final verdict | Understandable |
| --- | --- | --- |
| [Newcomer](audit/methods-newcomer.md) | PASS — APPROVED | Yes |
| [Researcher](audit/methods-researcher.md) | PASS — APPROVED | Yes |
| [Quantitative](audit/methods-quantitative.md) | PASS — APPROVED | Yes |

Every reviewer read all 18 pages and inspected rendered figures. The researcher
independently reconciled all 2,304 score rows, 2,688 contrasts and source
accounting; the quantitative reviewer also checked all 360 source counts,
4,608 aggregate-confusion balanced accuracies, 2,304 accuracy/F1 records, new
recipe/reuse/prefit/head tables and historical receipt claims. These checks used
only public metadata and aggregate outputs, not the underlying private arrays.

All three suggested only optional clarity improvements. The final pass names
the immediate predecessor and event-code families, makes development sampling
with replacement explicit, and adds a paper-native historical plot legend.
The original image bytes and all numerical tables are unchanged. Each reviewer
then independently checked the final hashes, affected pages and relevant source
and retained APPROVED / UNDERSTANDABLE. Earlier reports and the initial methods
candidate verdicts remain in their own records; no prior approval is relabeled.

An isolated archive of Git tree `020f20436acdf503eb6fd2fe79131b1524e27202`
compiled with `make -B` and Tectonic0.17.0. All source and figure bytes match the
reviewed package; the resulting 18-page PDF has identical extracted text and
zero TeX warnings. The scientific runtime and source notebooks were absent.
Only audit/administrative records changed after this build. All 30 pinned
repository links resolve, all PDF fonts are embedded, and all 32 generated
CSV/figure artifacts authenticate. [Artifact checks](audit/artifact-checks.json)
record these results and the three final review identities. TeX build timestamps
can change PDF bytes; the review binds the delivered PDF, not a promise of
byte-identical TeX output on different machines.

## Preservation and publication

Changes remain confined to `report/series-20261115/` and its reading link in
`report/README.md`, on `docs/series-paper-20261115`. Existing studies, completed
runs, raw inputs, source notebooks, failures and runtimes are untouched. The
November 15 working-tree record named an unrelated
`src/neuro/_cebra_sampling.py` edit at SHA256
`63489315c5a21257ed037edd77161f639beb23199321719d8fe22a562c1659f5` and
untracked `docs/reports/current-state-20260927/`; neither was present during the
November 16 follow-up. The current tracked sampling file has SHA256
`be5467607ec2766f3f8b0ff906de7d9f2f55898cd6d583f45b8d0f16fbd7d7b5`.
PR31 has since merged; PR32 remains unmerged after this documentation-only
follow-up. Exact checkout differences and preservation boundaries are recorded
in the [follow-up synthesis](audit/followup-20261116.md).
