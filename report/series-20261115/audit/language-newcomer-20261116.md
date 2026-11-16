# Independent newcomer reading audit — 16 November 2026

**Verdict: PASS. UNDERSTANDABLE: yes.**

The paper gives an ML-literate lab member enough information to understand what the tested CEBRA pipelines improved, where Raw/PCA performed better, how the construction changes the prediction problem, and which practical comparisons the lab can make. I found no material reading blocker within that remit.

## Artifact and scope

- Reviewed PDF: `report/series-20261115/paper.pdf`, 21 pages.
- Final reviewed PDF SHA256: `d99b2d02cc25f15e6d5354ff684f376441563e159d8b23c49ddb6f8e5d6b27f5`.
- Final companion LaTeX SHA256: `088d75baa04f4cf29fbb7b496fe09641c71a79d2c4042683d09ff1feaf9e2353`.
- Read all 21 pages in order through the extracted text at `work/language-revision-20261116/paper.txt`. Visually inspected pages 1–4, 7–12, 14, 16–17 and 19, covering every numbered figure, Figures 1–14, and the early comparison table.
- Read the required `AGENTS.md`, `docs/workspace.md` and `context/learner-profile.md` context. I did not read the report package README, prior/current review files, other reviewers' findings, or author/probe memos. The separate class-panel note was unnecessary for comprehension.
- This is an independent AI artifact/readability review of an exploratory synthesis. It does not certify underlying measurements, recompute model results, or constitute human scientific peer review. No model, neural-value array, notebook execution, fitting, or scientific runner was used.

The full reading used initial PDF SHA256 `6991218294482bd0910b19cd17a0f98ae1df59b21082870dc9c4216387230bae` and initial companion LaTeX SHA256 `9924b5b6617d111ba4e7c4094079dfe18fb77b9d7e91023e677d5fdd86385223`. I then checked both reported final deltas through direct PDF text extraction and refreshed page renders: page 1 correctly italicizes `worlds`, and page 4 now says that outer validation/test records are excluded from this study's fitting and evaluation. The latter wording scopes the exclusion to the current study without implying an historically untouched archive split. I verified the final hashes above and the unchanged 21-page count. The verdict applies to these final hashes; both changes preserve the findings and the page-4 clarification improves the evaluation explanation.

## Concrete findings

1. **The paper states what CEBRA improved.** The abstract, page 2 and page 16 identify the fixed nine-class, 17-column source-budget result: Time/SVM mean pair balanced accuracy increases from 16.67% at two sources to 46.30% at five sources per session/class. The fixed 144 training rows and changed source reuse are stated alongside the comparison. Page 16 supplies the intermediate result and the observed-versus-shuffle contrast, making the improvement operationally specific.

2. **A matched-readout advantage is clearly distinguished from the best complete pipeline.** Page 2 says that the best Raw/PCA mean exceeds the best CEBRA mean in each of the six arms. Page 16 gives the useful positive cases: at B5, Time/kNN is 45.37% versus Raw/PCA 28.24%/29.63%, and Time/LDA is 35.65% versus 24.07%/19.91%; Time exceeds both alternatives in every repeat for those readouts. Raw/SVM reaches 59.72%. A reader can therefore see both a reason to test Time with a particular downstream classifier and the stronger full-pipeline benchmark.

3. **The evaluation's meaning is introduced before the detailed results.** Page 1 defines a source, session, unit, pseudopopulation row, encoder, readout, balanced accuracy and computational repeat. It explicitly says that assembly uses a known pair label. Pages 2 and 4 explain that development uses different current/predecessor contributors from the same sessions, remains historically inspected, and preserves within-session and serial dependence. Figures 1–2 make the predecessor-derived start label and exclusion rule concrete. The text supports an exploratory association on constructed inputs; unknown-label natural trials and transfer to new sessions/subjects require separate evaluation.

4. **Class/session support has a practical explanation.** Page 4 states why every retained session must supply every selected class: the available feature columns stay fixed across classes. Pages 7–9 show why nearly flat aggregate class totals can coexist with a narrow common roster. For the nine classes, five-source support yields three sessions/17 columns, while three-source support yields 20 sessions/83 columns. Page 8 explains the objective, alternative class counts and changed endpoint-only ceilings. This is enough to understand why deleting a class can change both task difficulty and population availability.

5. **The processing choices are explicit enough to interpret their effects.** Figures 5–8 distinguish eligible recorded trials, selected sources, reused session blocks and constructed rows. The U3 rule applies to training assembly, with development and optimization reuse explained on page 11. Page 12 and Figure 9 explain bin standardization, seven-coordinate embeddings, ten-bin concatenation, per-session Native encoders, pooling and separate readouts. The Time/Native comparison's changes in supervision and parameterization are visible.

6. **The width conclusion preserves the important repeat-level qualification.** Page 17 states PCA/SVM means of 33.33%, 68.06% and 72.22%, compared with Time/SVM 34.72%, 35.65% and 48.61%. It also states that PCA's final mean increase contains one improving repeat and two declines. Figure 11 shows those repeats and the controls; Figure 12 shows all readouts. The paper supplies a concrete PCA benchmark without implying that every expansion helps every repeat or that neuron count alone caused the change.

7. **The lab can derive useful next comparisons without treating the paper as a universal recipe.** Pages 2 and 20 support counting eligible sources before choosing width, distinguishing additional recorded responses from repeated assembly, and comparing complete encoder–readout pairs. Pages 17–20 identify the missing convergence, spatial-map, natural-trial and biological evidence. The fixed grid establishes usable benchmarks while leaving optimal source counts and CEBRA settings unresolved. The direct results headings on pages 16–18 support that reading.

The rendered figures are legible and support these explanations. Figure 13 explicitly identifies its high-scoring seed and provides count/normalized confusions. Figure 14 is small, but the external legend, explicit historical cohort, full-size link and distinction between same-window decoding and temporal generalization keep it usable for its supporting role.

## Material blockers

None identified for the requested newcomer/practical-interpretation review. This verdict concerns the paper's explanations and claim boundaries; it does not independently establish the scientific truth of its saved results.

## Resolved optional editorial suggestion

The initial PDF's page-1 sentence ended with an unmatched opening quotation mark around `worlds`. The final source uses `\emph{worlds}`, and the rebuilt PDF renders it correctly. No optional wording change remains requested from this review.
