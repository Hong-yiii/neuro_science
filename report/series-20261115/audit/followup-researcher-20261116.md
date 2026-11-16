# Follow-up neuroscience-researcher review — November 16, 2026

Fresh Pi reviewer context; experienced-neuroscience-researcher role. The
reviewer received the target hashes and review criteria but no earlier audits,
detailed findings, validation ledgers or drafting/session transcripts. Harness
metadata is omitted; the substantive response is preserved below.

Reviewed PDF SHA256:
`a12d4936438baa79322a8c615db2112d8d0980f621a94c0fbbb45cb541812956`.
Reviewed TeX SHA256:
`ee2027cac9a0d9c2ae911a6355a74016c5a76fe519f3221888e1e0f6aa740923`.

No findings.

**Verdict: PASS** for an exploratory methodological synthesis.

**UNDERSTANDABLE: yes.**

## Scientific assessment

The manuscript’s conclusions stay within the evidence inspected:

- **Estimand and operational labels:** Pages 1–3 distinguish ordered endpoints
  from paths, explain the predecessor-derived start label, and explicitly
  identify known-label construction as a conditional assay—not unknown-trial
  prediction.
- **Source separation and independence:** The global contributor embargo agrees
  with public split metadata. Independence is appropriately qualified: retained
  trials share sessions, development blocks recur, and computational seeds are
  not biological replicates.
- **Construction contrasts:** Pages 5–8 correctly distinguish available sources,
  selected sources, block uses and constructed rows. Budget, repetition and
  width comparisons are described as bundled pipeline contrasts, not isolated
  causal effects.
- **Controls:** Pages 9 and 12–15 treat the five source-label worlds
  descriptively, without calibrated significance claims. Once-only training
  assembly is not misrepresented as eliminating development reuse or optimizer
  exposure.
- **Encoder/readout comparisons:** The manuscript discloses unequal raw/latent
  dimensions and native-versus-Time differences in supervision,
  parameterization, pooling and batch allocation. Fixed training duration is
  not presented as demonstrated convergence.
- **Results and interpretation:** Training–development gaps, endpoint-head
  discrepancies, adverse class changes and unfavorable repeats remain visible.
  The 66.67% perfect-single-endpoint reference is mathematically appropriate
  for this sparse panel.
- **Historical synthesis:** Different cohorts and protocols are not pooled into
  a common effect estimate. Computational reproduction is explicitly separated
  from biological replication.

These boundaries are especially clear in
`report/series-20261115/paper.tex:209–215`, `:307–317`, `:417–431`, and
`:459–505`.

## Checks actually performed

- HEAD and base match the supplied revisions; PDF and TeX SHA256 values match
  both expected hashes.
- Rendered and visually inspected **all 18 PDF pages**; read the complete
  548-line TeX source.
- Independently extracted public notebook scalar tables: **2,688 displayed rows
  reduce to 2,304 unique score records**, all matching the paper CSV exactly.
- Recomputed **all 2,688 matched contrasts** from score records: maximum
  discrepancy **0**.
- Confirmed the principal SVM means, claimed diagnostic-range separations,
  once-only Raw/PCA results, and width trends across all four readouts.
- Confirmed PCA/SVM’s final width improvement occurs in only **one of three**
  repeats; Raw/SVM declines in all three.
- Confirmed all **24** U3/Wfull SVM pair training scores equal 100%; checked
  every tabulated training–development gap.
- Independently reconstructed the global embargo using authenticated public
  metadata: **5,872 protected contributors, 4,427 excluded training records,
  7,861 retained training records**, with no cross-split contributor
  intersection.
- Reconciled roster totals, development singleton counts and **5,375 observed
  source–column memberships**.
- Compared three public notebook confusion matrices with paper tables and
  recomputed their balanced accuracies.
- Cross-checked October endpoint and October23 headline means against their
  public scalar tables.

Implementation inspection included
`experiments/source_reuse_width_20261114/study.py`,
`src/neuro/studies/population_grid.py`,
`src/neuro/studies/population_models.py`, and
`src/neuro/notebook_inputs.py`. No manuscript-building script was executed.

## Inherited evidence and coverage limits

Historical fitting, model reloads, resource gates, native-input conservation,
dense-behavior marker corroboration and the **14,304-array reproduction
equality** were **not independently rerun or re-attested**. They remain
inherited claims; this audit verified public aggregates and relevant
implementation, not their underlying private execution artifacts.

Residual scientific risks remain substantial but are disclosed: exposed
development, label-conditioned construction, serial/session dependence, missing
subject/anatomical replication metadata, unresolved nuisance explanations, and
absent natural-trial/path-beyond-endpoints validation. PASS does not establish
general biological validity.

## Assessment dimensions

- **Content success — satisfied:** understandable, numerically consistent
  synthesis with appropriately bounded scientific claims.
- **Operational success — satisfied for this audit:** identity, rendering and
  public-evidence checks succeeded. Historical execution gates remain
  independently **unknown**.
- **Instruction compliance — satisfied:** read-only repository inspection;
  temporary rendering only under `/tmp`; prohibited reviews/memos and private
  outputs were not opened; no fitting, model replay, notebook execution or
  repository/GitHub edits.
