# Blind newcomer manuscript audit — November 16, 2026

**Decision: PASS. UNDERSTANDABLE: yes.** The candidate explains why the fixed nine-class task was workable, how common-session support limits width, and why the additional class-count comparisons are metadata feasibility rather than decoding evidence. No material correction is required for those conclusions.

This is an independent AI manuscript reading audit from the perspective of an ML-literate reader newer to neuroscience. It is not external biological peer review, a new scientific experiment, or an independent re-execution of the optimizer.

## Reviewed artifacts and read scope

The following SHA-256 values were calculated from the files, rather than accepted from the assignment. They matched the assigned candidate and were checked again at the end of the reading:

| Artifact | SHA-256 |
| --- | --- |
| `report/series-20261115/paper.pdf` | `f5a1783a3673ff5a788af8210bfb876e7045fb531d06354f1a248dbd4ba270f9` |
| `report/series-20261115/paper.tex` | `a3df343e3add19089e7e497d872d4d45eb36aca74ef4a79ddfe65aebe6667d28` |
| `docs/experiments/source-reuse-width-20261114/class-panel-metadata-20261116.json` | `8f6560aa172c86a53f211596bce9333ee410281210f2c518ad3a8503a572316a` |
| `report/series-20261115/class-panel-figure-provenance.json` | `dee2b1ccb57194dccd1bbcc8db4650084486a7d7a8a3c6e85191229e76d549b5` |
| `docs/experiments/source-reuse-width-20261114/class-panel-20261116.md` | `45deee5bb81b6c4fb7a71ff109674655ef06e1eedce071edccc1ebbc3954712a` |

I read the full 20-page manuscript and inspected every page image, emphasizing pages 1–10, 17, 19 and 20. I also read the corresponding TeX for sections 6–7 and checked the changed scope/reference text. After forming the initial reading assessment, I read the dated class-panel note, the receipt's complete nine-entry frontier and the figure-provenance record. Their stated counts and distinctions agree with the displayed explanation. This audit does not certify the optimizer implementation or independently recompute the underlying session counts.

Required context was limited to the applicable root `AGENTS.md`, the current-state portion of `docs/workspace.md` and `context/learner-profile.md`. No earlier manuscript audit, author/probe memo, package README approval headline, or another reviewer's findings was consulted. Historical queues were not resumed.

The supplied extracted text matched a fresh `pdftotext -layout` extraction of the candidate PDF exactly; its SHA-256 is `4b9ba20e27614b0a47ed5a06f8dde702b2640aa5b6f596292e7bdcc0605f100e`. `pdfinfo` confirmed 20 A4 pages. In-memory 110-dpi rendering matched 19 supplied page images exactly. The initial page-6 preview differed only in the color of the `34` label for start 1, goal 4 in Figure 3b. I inspected a fresh render directly; the coordinator then refreshed the preview, and I confirmed exact pixel equality with the final PDF. This preview discrepancy is resolved; the PDF and TeX hashes did not change.

No models, neural value/feature arrays, notebooks or completed result artifacts were loaded or executed. No fitting or selection optimization was run. The only file written by this audit is this report.

## Can a reader reconstruct the design?

**Yes.** The manuscript supplies the necessary chain without requiring the external study note:

1. Pages 1–3 define a pseudopopulation, a recorded source and its predecessor contributor, then explain global contributor separation. They explicitly distinguish the conditional, known-label assay from unknown-label natural-trial prediction. The reader does not have to infer that distinction from a later limitations section.
2. Page 5 lists the exact nine ordered pairs and says that nine was fixed before class identities were selected. Table 4 separates columns, sessions, sources per pool, selected IDs, training rows and uses per source. This prevents the main numerical denominators from becoming interchangeable.
3. Page 6 distinguishes a pair's marginal source totals and individually qualifying sessions from the intersection of sessions qualifying for every selected pair. Equation 3 and the adjacent sentence about one deficient pool excluding the entire session block express the same rule mathematically and in plain language. The reported 3-session/17-column core and 20-session/83-column wider roster are understandable consequences of this intersection, not evidence of a shortage of aggregate trials.
4. The fixed-K selection rule is explicit: balanced start/goal incidence, maximum five-source width, maximum three-source width conditional on that first optimum, then a deterministic class-list tie-break. The objective is recorded columns, not session count or decoding accuracy. Development availability is acknowledged as part of eligibility.
5. Page 7 makes the concrete restriction visible: adding `4→1` at K = 10 preserves the core but reduces the wider roster from 20/83 to 13/58. It also states that separately selected panels need not be nested. The K = 12/15 discussion concerns the returned width optima and does not declare every alternative panel infeasible.
6. The text explicitly acknowledges wider alternatives at K = 8 and K = 6. The degree-one task at K = 6, the endpoint-only ceiling of 6/K, and the changing uniform reference explain why wider metadata support is not a comparable decoding result. Nine is presented as workable, not uniquely best or chosen by optimizing over K.

The later construction sections reinforce this account. Figures 5–8 distinguish available sources, selected blocks, constructed rows, repeated whole tuples and singleton development pools. The claim that no repeated whole tuple implies independent observations is expressly rejected. Pages 11–19 consistently distinguish model/readout performance, computational repeats and biological evidence; the new feasibility material does not weaken those boundaries.

## Figure and layout assessment

Figures 3 and 4 are legible at the supplied full-page scale. Figure 3 identifies axes, training/development number order, the single-pair gate, and the frozen classes. Figure 4 distinguishes the two support thresholds and highlights the executed K = 9; Table 5 provides exact values and states that session count was not optimized. I found no clipped annotation, overlap, missing glyph, or unreadable number in the new figures. The conditional three-source objective is repeated in the figure subtitle, prose and table header.

The remaining page layouts are readable. Figure 14's inherited internal labels are comparatively small, but its external legend, explanatory caption and full-size link preserve access to the historical comparison. That figure is clearly a different cohort and does not serve as evidence for the new class-count frontier.

Page 1 dates the metadata addition separately from the November 15 experimental cutoff. Page 20 identifies the metadata receipt and verification code separately from the completed experimental evidence, and describes the manuscript reviews as AI-agent audits. These statements prevent the added material from implying another model run or biological replication.

## Issues by severity

- **Critical/high:** none found within this reading and presentation scope.
- **Medium:** none found.
- **Low, optional wording refinement:** Figure 3's legend says “Self-pair unavailable,” while its caption and the study note correctly call the diagonal excluded self-pairs. “Excluded self-pair” would avoid any momentary suggestion of a missing measurement. The caption already resolves the distinction, so this is not a condition of passing.
- **Resolved review-artifact issue:** the stale page-6 preview label color was refreshed and verified against the unchanged final PDF, as recorded above.

**Final verdict: PASS; UNDERSTANDABLE: yes.** The manuscript supports reconstruction of the class-panel logic and its limits without treating metadata counts as decoding scores or independent samples. This verdict is confined to the exact artifacts and reading scope above.
