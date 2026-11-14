# Independent newcomer manuscript audit

Date: 15 November 2026  
Role: AI manuscript auditor reading as an ML-literate newcomer to neuroscience  
Verdict: **PASS**  
Understandable: **YES**

This is an independent AI-agent manuscript review, not human peer review, a user comprehension study, or biological replication. The pass concerns standalone comprehensibility and the connection between displayed evidence and written claims. It does not substitute for the separate quantitative/provenance audit.

## Exact reviewed artifacts and scope

I independently computed these SHA-256 hashes before reading and again after inspecting the PDF; both checks agreed:

| Artifact | SHA-256 |
| --- | --- |
| `report/series-20261115/paper.pdf` | `6a3848d795668a8454041da003a416568a6eaff516cd11fbea44f7197ea76c1d` |
| `report/series-20261115/paper.tex` | `30feff7d23c66ce1fc4387b1318d6cecfc0a801bfcecc0f15960104380d95f3e` |

I read the complete LaTeX manuscript and all ten PDF pages. I inspected rendered versions of every page, including a higher-resolution rendering of page 8 to check the historical plot. Inspection copies are under the ignored `work/series-paper-20261115/naive-review/` directory. I did not read drafting/probe memos, other audit files, other reviewers' findings, the linked study records, aggregate source tables, raw data, neural arrays, or fitted objects. I read the mandatory `docs/workspace.md` for workspace safety before the manuscript; I did not use its scientific summaries to repair missing explanations in the paper. No manuscript, source figure, experiment, or Git state was changed by this review.

## What I understand from the paper itself

**Question.** The series began with a stronger question: does cue-period hippocampal activity contain information about the subsequent ordered route beyond start and goal? The completed evidence does not answer that question affirmatively or establish its absence. The current paper instead asks what endpoint information can be recovered from explicitly constructed populations, and how source diversity, source reuse, population composition, representations, and readouts affect that conditional assay.

**Measurement and assembly.** The measurements are sorted-unit spike times and task events. Event alignment converts the one-second cue into ten 100-ms spike-count bins, with missing observations distinguished from measured zeros. A source is an eligible recorded current trial identified within a session; predecessor-trial information can also contribute to its label. A constructed row combines one same-class source block from each selected session. Within that block, retained columns and cue bins follow the same source. Across sessions, the row is an artificial combination rather than one naturally observed population trial. Neither common array shapes nor session grouping prove simultaneity.

**Evaluation object.** Endpoint labels are known when training and development populations are assembled. The decoder consequently measures whether these condition-matched response constructions retain endpoint association; it is not asked to infer an unknown condition from a natural simultaneous trial. Train/development contributor separation happens before selection and learned preprocessing uses training values, but development labels and availability help define the assay. Historically reused development, repeated source blocks, serial/session dependence, and unresolved acquisition metadata limit generalization. The three seeds describe computational variation, not three animals or independent biological samples.

**Design.** B2/B3/B5 keep 17 columns, three sessions, nine classes, and 144 training rows fixed while selecting two/three/five sources per session–class pool. U3 uses B3's same sources once, producing 27 training rows. B3 is reused as the bridge to 49-column and 83-column rosters at three sources per pool. For example, B3 has 9 classes × 3 sessions × 3 sources = 81 selected source IDs; U3's 27 constructed rows each contain three session blocks. Thus there is no contradiction between 81 sources and 27 rows. Width also adds sessions and measured source support, so it is not an isolated intervention on neuron count.

**Models and metric.** Standardized raw bins, seven-dimensional PCA, pointwise CEBRA-Time, and session-specific pair-supervised CEBRA are followed by separate supervised readouts. Ten seven-coordinate bin outputs produce 70 whole-cue features. CEBRA-Time encourages nearby bins from the same constructed row to be similar; native multisession changes supervision, number of encoders, and pooling together. Balanced accuracy is mean class recall, with 1/9 as the uniform pair reference. Source-label worlds permute pair labels before constructing and fitting the pipelines, providing sampled alignment diagnostics. Their five values are explicitly not a significance test. The paper also explains why a sparse pair task can be solved partly from one endpoint, so beating 1/9 does not establish joint endpoint coding or route information.

**Main results.** Once-only Raw/SVM and PCA/SVM retain endpoint association relative to the displayed diagnostic worlds. Repetition is therefore unnecessary for those observed associations, although once-only assembly does not mean once-only optimizer exposure or independent evaluation rows. More selected sources help Raw/SVM and Time/SVM much more than PCA/SVM in this configuration. PCA/SVM width means rise from 33.33% to 68.06% to 72.22%, but the last mean increase comes from only one improving repeat. The all-readout heatmap shows that both PCA and Time have positive mean width steps across the four readouts; raw and native results are mixed. No universal representation winner or isolated biological mechanism follows.

**Progression.** Source-transfer failures motivated distinguishing new combinations from new measurements. Endpoint comparisons were more interpretable than broad path claims. Stricter source accounting changed the cohort and scores, so historical accuracies were not portable benchmarks. November then made source use explicit, discovered that changing class requirements changes the task, and moved to the latest fixed-class budget/width design. The reproduction repeats the same computation on the same recordings rather than adding biological replication. This sequence is understandable without reading repository history.

**Strongest permitted conclusion.** Under these source-separated, label-conditioned, historically exposed constructions, some endpoint association persists when each selected training source is assembled once, and construction/model choices materially affect the observed scores. The paper does not deliver natural-trial prediction, ordered-route recovery beyond endpoints, simultaneous population dynamics, a causal cell/session explanation, or a generally reusable neural-state model.

## Findings by priority

**Blocking findings: none.** I found no blocking confusion in the question, source/row distinction, conditional evaluation, primary metric, progression, or strongest claim. I found no unsupported inferential leap that prevents a newcomer from interpreting the paper within its stated exploratory scope. Numerical provenance beyond internal consistency remains the separate quantitative review's responsibility.

**Low priority, nonblocking — Figure 6 is the least comfortable figure to read at page size (page 8).** Its historical raster legend and axis text are noticeably smaller than the other figures. They become readable when enlarged, and the caption makes the cohort, readout procedure, computational ranges, and lack of frozen-decoder transfer clear. A larger placement or a separately enlarged legend would improve print and laptop reading. This does not obscure the primary results, which use the much more legible Figures 3–5.

**Low priority, nonblocking — unpack two compressed source definitions earlier (page 2).** The explanation eventually establishes that sources are current-trial IDs and that the previous trial can contribute to a label. A short direct sentence introducing “source trial,” followed by a plain-language explanation of “successful-after-successful,” would reduce the need to assemble those definitions across page 2 and Table 2. A compact example such as the B3/U3 arithmetic above would help, although the current equation and table already allow it to be reconstructed correctly.

**Low priority, nonblocking — name the readout in the abstract's PCA width sentence (page 1).** The values 33.33/68.06/72.22% are explicitly PCA/SVM in Section 7. Writing “PCA/SVM mean pair balanced accuracy” in the abstract would prevent a skim reader from mistaking them for a mean across readouts. The full text and all-readout figure remove that ambiguity.

## Diagram, equation, and caption checks

- Figure 1 follows the measured-events → source separation → known-label construction → train-only fitting → conditional evaluation chain. Its missingness and non-simultaneity statements prevent the most consequential newcomer misreading. Equation (1) has an explicit clock, bin duration, and interval convention; Equation (2) identifies the session blocks being concatenated.
- Figure 2 distinguishes one Time encoder from per-session native encoders and shows how 70 readout features arise. The contrastive equation is identified as schematic, not a recovered training loss. Its positive-pair rule is explained in words.
- Figure 3 makes computational repeats and the mean separately visible, shows source-label worlds rather than replacing them with an unexplained error bar, and identifies the uniform reference. Its caption states the exposed constructed development object. Connecting U3 after B5 is a categorical display, not an inferred source-budget trend; the labels and caption make that distinction adequate.
- Figure 4's signs, units, readout labels, and two width steps are readable. Its accompanying text explicitly corrects the possible mistake of treating a positive mean as improvement in every repeat.
- Figure 5 gives both counts and percentages, labels prediction/true axes, states eight rows per class, and discloses that the illustrated seed has the highest score. It does not silently present that seed as typical. The clear distinction between constructed counts and biological trials is maintained.
- Figure 6 is explicitly historical and uses a different cohort and target count. Its caption and nearby paragraph distinguish same-window classifiers from a frozen decoder tested across time. The small lettering is the presentation suggestion above, not an unmarked methodological substitution.
- Table 3 and the final prose preserve the difference between absent evidence and evidence of biological absence. The 6/9 one-endpoint reference strengthens, rather than weakens, the conditional interpretation of the results.

**Final verdict: PASS. Explicit understanding verdict: UNDERSTANDABLE — YES.** The suggestions above are optional readability improvements; no revision is required to resolve a blocking newcomer misunderstanding in these exact artifacts.
