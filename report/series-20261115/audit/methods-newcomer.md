# Independent methods review for an ML-literate newcomer

Review date: 15 November 2026. Reviewer role: blind newcomer-methods reader.

**Verdict: PASS — APPROVED and UNDERSTANDABLE for the declared exploratory evidence synthesis.** There are no material blockers under the requested methods, sample-accounting, and claim-boundary criteria. This approval concerns the manuscript's explanation and defensibility of its stated scope; it is not independent authentication of every underlying numerical result or an endorsement of stronger biological claims.

## Candidate and inspected scope

- PDF: `report/series-20261115/paper.pdf`, 18 pages; SHA-256 `0939cc63d64b39c68400a031bc0e6153bdf30d7de43281d62541d7f6b8d52740`.
- TeX: `report/series-20261115/paper.tex`; SHA-256 `1e4ba52ab3dc1b4155fb57821c19ca1f46b600599b45df765e17cf5afd8a5eec`.
- Both hashes matched the requested candidate before reading and remained unchanged at the end of the review.
- Read the entire extracted PDF text and all 540 TeX lines. Inspected every rendered page, 1–18, at 140 dpi, including all 12 figures and nine tables. The figures central to the latest study are readable at that size; I found no clipping or overlapping text that prevented understanding.
- Read `docs/workspace.md` first for current status, root `AGENTS.md`, and `context/learner-profile.md`. No additional applicable `AGENTS.md` was found under the review paths.
- After completing the manuscript reading, consulted only the development/construction-related passages of `docs/experiments/source-reuse-width-20261114/protocol.md` to assess an optional clarification below. The verdict did not require that source to reconstruct the main assay.
- Did not read author/probe memos, drafting conversations, other audit files, or other reviewers' findings. Did not access raw/neural arrays, private outputs, fitted models, or execute notebooks or research code. Temporary text and renders are under `work/series-paper-20261115/blind-methods-newcomer/`.

## What I can explain from the paper alone

**One input sample and the counting units are clear.** A recorded source is a current trial in one session. Its current cue spikes provide the measured response, while its immediate predecessor contributes the operational start label. A decoder sample is a constructed whole-cue row: choose one source of the known endpoint class from each admitted session, keep each source's session columns and all ten bins together, and concatenate those blocks. It is not a single measured population trial. For example, a B2 row contains 17 columns by ten bins assembled from three session-specific sources, giving 170 raw readout features. B2 has 54 selected current-source IDs but 144 constructed training rows; these are different counts, not competing estimates of biological sample size (pp. 2–3, 5, 7–9).

The paper also avoids inventing an independent biological denominator. Sources can remain serially dependent and clustered within session even after contributor separation. Subject-level replication structure is unknown; neither columns, bins, rows, seeds, nor repeated runs supplies that missing structure. This is a successful explanation of the limit, rather than a failure to report a justified independent sample size.

**The measurement-to-evaluation chain is recoverable without opening code.** The manuscript explains native spike timestamps, neural-clock cue alignment, ten half-open 100-ms count bins, current-goal/predecessor-goal labels, eligibility exclusions, the frozen inner split within original outer training, and the global current/predecessor embargo. It then explains complete session–class support, fixed source budgets, blockwise assembly, training-only scaling and learned transformations, whole-cue readouts, and mean class recall on exposed development constructions. Equations 1–3 and Figures 1–5 have a real explanatory role; they are not decorative substitutes for the method (pp. 2–9).

**Recorded support and constructed balance are distinguished quantitatively.** Table 2 gives the archive-to-eligible accounting. Table 4 gives selected IDs, training rows, and source multiplicities. Figure 3 shows every latest-study session–class source count rather than only an aggregate total. Figure 4 explains why the full source tensor is mostly unavailable entries, not measured zeros. The manuscript makes clear why 72 equally class-balanced development rows can rest on uneven measured support, including singleton pools (pp. 3, 5–8).

**Actual reuse is visible.** The reader is given actual training recipes, source-use ranges, whole-tuple repetitions, the extra-draw fraction, and the distinction between partial block sharing and complete repeated rows. The 77/23/6 repeated B2/B3/B5 tuples are explicitly counts beyond the first occurrence. U3 removes training-assembly repetition while retaining development reuse and repeated optimization draws. This prevents the tempting but incorrect inference that zero repeated whole tuples means independent observations (pp. 7–8, 11).

**The model comparison is understandable.** PCA and Time operate pointwise on bins before ten outputs are concatenated; native multisession uses session-specific networks with pair-label supervision and equal-session pooling. The manuscript distinguishes input-construction labels from objective supervision, and it states the changes in representation size, parameters, batches, exposure, and readout regularization that prevent a pure causal comparison of encoder modes (pp. 9, 11, 14). The description is sufficient for understanding the scientific comparison, although reproducing exact library behavior still appropriately requires the linked implementation.

## Why the validity and interpretation pass

The paper provides completed evidence at distinct levels: behavioral corroboration of marker meanings, event/QC and export checks, source/embargo/plan checks, manual-versus-library arithmetic, saved-pipeline checks, source-label diagnostic worlds, and a full computational reproduction. Tables 5–7 state what each supports and what it leaves open. A reader is not asked to equate successful software execution, many checks, or exact array equality with biological validity (pp. 10–12).

The conditional nature of decoding is stated early and repeatedly. Known labels are used to construct the population before a classifier predicts those labels. This supports response–label association under that construction, but does not establish an unknown-trial predictor, independent prospective generalization, intention, mechanism, simultaneous dynamics, ordered-path recovery, or formal state observability. The same-session split, historical development exposure, unknown acquisition structure, and possible cue/gaze/predecessor-state explanations remain visible (pp. 1–3, 12, 15, 17).

Results are sufficiently qualified to support those limits. All three observed repeats and five diagnostic scores appear in the main SVM figure; the final PCA width increase is explicitly positive in only one repeat. The all-readout width table, training–development gaps, separately fitted endpoint heads, and the mathematical single-endpoint reference keep the discussion from resting on one favorable mean. The high-scoring confusion example is labeled as such. Historical same-window decoding is distinguished from a frozen-decoder transfer test (pp. 13–17).

## Material blockers

None found for the requested self-contained methods explanation and exploratory claims. In particular, missing acquisition metadata and independent biological validation are disclosed limitations of the underlying evidence, not concealed facts that the paper purports to have resolved.

## Optional improvements

1. **Make the development draw rule explicit (pp. 6–8).** Training balanced cycles are specified precisely; development is described as one fixed, projected recipe with eight draws per class. Add one sentence identifying how eligible development sources are allocated to those eight draws, whether all eligible IDs appear, and the resulting use counts or range. Singleton dependence is already clear, so this is a completeness improvement rather than a blocker. The protocol passages consulted also leave that allocation implicit.
2. **Remove a small predecessor ambiguity in Figure 1 (p. 2).** “Previous successful trial” could mean skipping an intervening failed trial. “Immediately preceding trial, required to be successful” would match the adjacent-trial example and eligibility exclusion described elsewhere.
3. **Enlarge Figure 12's legend (p. 16).** The historical plot's traces are visible, but the embedded legend is much smaller than the rest of the paper. A larger figure or a short paper-native legend would make print reading easier without needing the external full-size image. This does not obstruct the latest-study methodology or its main results.

These edits would improve local clarity. None changes my approval of this candidate under the stated review criteria.

## Final-version addendum — 15 November 2026

**Final exact-artifact verdict: PASS — APPROVED and UNDERSTANDABLE. No material blocker.** The three optional clarity points above are resolved in the revised manuscript. The earlier assessment remains applicable to the unchanged scientific narrative and results.

- Final PDF SHA-256: `a12d4936438baa79322a8c615db2112d8d0980f621a94c0fbbb45cb541812956`.
- Final TeX SHA-256: `ee2027cac9a0d9c2ae911a6355a74016c5a76fe519f3221888e1e0f6aa740923`.
- Confirmed that the PDF still has 18 pages. Inspected revised pages 2, 8, 16 and 18 at 140 dpi, the corresponding TeX, and the full extracted-text difference against my retained first-candidate extraction. The textual changes are confined to the described clarifications, legend and implementation references, apart from extraction spacing. No result numbers or scientific conclusions changed in that comparison.

On page 2, Figure 1 now says the immediately preceding trial must succeed, removing the possible interpretation that a failed trial can be skipped. The caption identifies the cue, navigation and outcome marker-code families while retaining the manuscript's operational-label and provisional-semantics limits. The revised diagram and caption are readable.

On page 8, development construction now explicitly uses eight rows per class and uniform draws with replacement from each eligible session–class pool, with seed 0. It also states that eligible IDs can be unused and that the support figure reports eligibility, not realized use. I read the existing `paired_plans` and `sample_plan` function bodies, without importing or executing them: the former specifies development, eight rows and seed 0; the latter repeatedly draws from the unchanged eligible pools with `rng.choice(pool)` and no weighting. That supports the new explanation and resolves the prior allocation ambiguity. The separate training balanced-cycle policy and the limits of once-only assembly remain clear.

On page 16, the new paper-native legend is legible and identifies all five curves and the dotted reference, including historical PCA-8. The historical-versus-latest cohort distinction remains intact. On page 18, the matched-plan and sampler references are present and readable.

This was a narrow final-version reading and source inspection, not a new scientific execution or complete numerical provenance audit. No other review files were consulted, and no manuscript, data, figure or analysis-code files were edited. The final rendering files and text extraction remain in this reviewer's existing temporary directory.
