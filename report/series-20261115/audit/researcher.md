# Independent researcher audit

Date: 15 November 2026

Role: experienced neuroscience research reader and evidence reviewer

Verdict: **PASS**

Understandable: **yes — UNDERSTANDABLE as a research synthesis for a colleague.**

This is an independent AI-agent manuscript and evidence audit, not external human
peer review. The verdict applies to the ten-page exploratory synthesis below. It
does not certify a new confirmatory biological result or approve another study.

## Reviewed identity and independence

I independently computed these SHA256 hashes before and after review:

| Artifact | SHA256 |
| --- | --- |
| `paper.pdf` (10 A4 pages) | `6a3848d795668a8454041da003a416568a6eaff516cd11fbea44f7197ea76c1d` |
| `paper.tex` | `30feff7d23c66ce1fc4387b1318d6cecfc0a801bfcecc0f15960104380d95f3e` |
| Evidence revision | `a0ca80180e2bb52b90e499357d3d6965b26806da` |

I began with the required workspace boundaries, manuscript source and rendered
paper. I did not read the authors' probe memos, other current manuscript audit
files, or other current reviewers' conclusions. I inspected all ten rendered PDF
pages. Evidence checks used tracked reports, protocols, implementation source and
public notebook aggregate outputs at the pinned revision. No literature browsing,
neural-array/raw-data reads, model loading/replay, notebook execution or fitting
occurred. Temporary PDF page renders were used only for visual inspection.

## Findings by priority

**Blocking scientific or understandability findings: none.**

**Major corrections required: none.**

The paper is defensible because its positive conclusions refer to the declared
conditional construction. The reader is told early, and reminded at the relevant
results, that labels enter assembly, development is exposed, and source separation
does not create biological independence. The narrative explains why the question
and evaluation object changed without treating different cohorts as successive
replications or as a common performance leaderboard.

The following substantive checks support the verdict:

- **Measurement and population semantics (pages 1–2, 9).** Spikes, binned counts,
  pseudopopulations, embeddings and decoded labels are kept distinct. The source
  tensor/mask and half-open cue-bin description agree with the compact-source
  contract. The manuscript does not equate the 195-unit archive with each study's
  population, a sorted unit with a verified anatomical cell, or session grouping
  with proven simultaneity. Missing subject/anatomical metadata and place-oriented
  selection are acknowledged. No dynamics, intention, mechanism or formal
  observability conclusion is inferred from an embedding or decoder.
- **Separation and dependence (pages 2, 4, 9).** The global current/predecessor
  embargo precedes panel selection in `population_grid.metadata`; the latest
  `paired_plans` constructs a shared development plan and projects whole session
  blocks across rosters. U3 and B3 use the same selected source identities. The
  paper correctly distinguishes selected sources, constructed rows, optimization
  exposure and computational seeds, including singleton development pools.
  Development availability entering eligibility is disclosed. It is not presented
  as an untouched prospective test.
- **Models and estimands (pages 4–5, 7).** The implementation supports train-only
  pooled-bin standardization/PCA and separate readout scaling. The printed public
  first-case network confirms the stated Time architecture. Native fitting uses
  joint-pair labels, separate session networks and equal-session mean pooling;
  its total references per update are 255/253/240 for the three rosters. The paper
  therefore correctly treats native versus Time as a comparison of pipelines
  differing in supervision, parameterization and pooling. Width changes sessions
  and measured support as well as columns; B3/U3 changes combinations, weights
  and row count. None is called an isolated causal neuron-count or duplication
  effect. Fixed update counts are not claimed to prove convergence.
- **Latest scores, controls and error example (pages 6–8).** I independently
  parsed the two pinned published notebook score tables, deduplicated their shared
  B3 identities, and matched every field of all 2,304 unique manuscript score rows
  exactly to those tables. The two published notebook hashes also match the
  publication record. Independent arithmetic confirms the highlighted Raw
  B5−B3, Time B5−B2, PCA Wmid−B3 and Time Wfull−Wmid contrasts each exceed their
  five sampled control changes in all three observed repeats. Raw/PCA U3 scores
  exceed their sampled controls; all four B3−U3 contrast ranges overlap controls.
  The PCA final-width mean improves while only one repeat improves. Both PCA and
  Time improve in mean at both width steps for all four readouts; native's final
  mean declines for all four. The Wfull PCA/SVM seed-0 published confusion contains
  64 correct predictions out of 72, with eight per true class, matching Figure 5.
  Its unusually high score is explicitly disclosed rather than presented as
  typical. Five label worlds are descriptive checks, not p-values, and seed
  variation is not a biological interval.
- **Historical progression and comparability (pages 3–4, 8–9).** The path-study
  completion/correction records support the 99.25% versus 24.92% source-pool
  comparison and its limited interpretation. The October endpoint score table
  independently gives the four quoted whole-cue means, 70.2778%, 83.6111%, 63.75%
  and 75.5556%. The 27-unit report, November 10 support report and November 11
  grid report support their quoted cohorts and results. Different targets,
  class sets and source protections are not silently harmonized. The older
  raw-LDA temporal-transfer evidence is distinguished from separately fitted
  same-window readouts and the unexecuted matched CEBRA transfer study. The error
  follow-up supports the cautions about unevaluated deleted classes, algebraically
  coupled reuse/coverage and noncausal session attribution.
- **Claim boundaries and reproducibility (pages 7, 9–10).** Spatial coverage is
  correctly unknown rather than absent or zero. The six-category/ nine-pair
  single-endpoint reference of 6/9 is mathematically correct and is not called a
  fitted baseline or a conjunction test. The 48 cases, 2,448 nonscaler fits,
  96,000 updates and 38 executed code cells agree with the frozen protocol and
  reproduction ledger. The 3,188-file/14,304-array reproduction claim is reported
  with its correct same-recordings interpretation. I verified its documentary
  provenance, not the private arrays themselves. All 22 repository-linked
  reference paths exist at the pinned revision.

## Nonblocking suggestions

1. A short sentence naming visual cue identity, preceding-trial state and eye or
   behavioral variables as uncontrolled possible contributors would make the
   confound boundary more concrete for a neuroscience reader. The existing
   condition-level and no-mechanism limits already prevent a stronger claim, so
   this is a clarification rather than a publication blocker.
2. Figure 6's inherited legend and ticks are small at whole-page viewing size.
   Enlarging those labels or providing a larger linked view would improve reading.
   The caption clearly identifies the historical cohort, metric and computational
   ranges; the figure is intact and readable with zoom. No material clipping,
   caption/panel mismatch, misleading uncertainty display or misplaced figure
   was found on any rendered page.

No revision is required for this reviewer to accept the reviewed artifact as an
understandable, appropriately bounded synthesis. Any material change to claims,
figures or evidence would require checking the changed artifact and recording its
new hashes; this verdict does not transfer automatically to a different version.

## Final-version addendum — 15 November 2026

Verdict: **PASS**

Understandable: **yes — UNDERSTANDABLE as a research synthesis for a colleague.**

I independently reviewed the complete manuscript-source diff from the previously
audited version at commit `cd31986`, recomputed the following hashes, and inspected
the newly rendered pages 1, 2 and 8. The PDF remains ten A4 pages. I did not read
other manuscript audit files or other reviewers' conclusions for this follow-up.

| Final artifact | SHA256 |
| --- | --- |
| `paper.pdf` | `dc6ea8e5e2d422657b32ca8001eb706428bb329025fa473c9f75121bda05ba02` |
| `paper.tex` | `2f1630251df8d445e1242b028a72f94e17ce140d9dcae7164f9576c203eb6b1a` |

The abstract now identifies the quoted width scores explicitly as PCA/SVM. The
new source-trial and successful-after-successful definitions accurately explain
the current-trial/predecessor relationship without presenting the operational
endpoint label as directly measured intention. Naming cue identity, visual input,
gaze and preceding-trial state makes the confound boundary concrete and resolves
my first nonblocking suggestion.

Figure 6's added full-size figure/legend link resolves my second suggestion. Its
destination exists at the pinned evidence revision. The inherited plot remains
small on the page, but the enlarged view is now directly available from its
caption. Revised pages have no material overlap, clipping or caption displacement;
the added page-2 explanation remains readable alongside the schematic and
equations. The TeX log contains no warning/error, overfull/underfull-box or
undefined-reference matches. Direct figure inclusion also removes the earlier
draft-placeholder fallback.

The tracked numeric tables, figures and figure-provenance manifest are unchanged
from `cd31986`; no repeated numerical audit was needed. The initial evidence
checks and their stated access limits therefore remain applicable. These
revisions clarify the existing assay and do not add a biological inference.

**No blocking findings or required revisions remain for this final version.**
This remains an AI-agent reading and evidence audit, not external human peer
review. Only this audit addendum was written; manuscript, figures and Git state
were not modified by the reviewer.
