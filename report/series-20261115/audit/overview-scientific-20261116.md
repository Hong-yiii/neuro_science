# Independent scientific audit: qualitative overview

**Verdict: PASS. UNDERSTANDABLE: yes.** No scientific revision is required for the reviewed final artifacts.

Reviewer: independent AI agent `/root/blind_overview_scientific_20261116`, November 16, 2026. This is a review of the changed interpretation and construction descriptions, not a new validation of the historical fits or biological claims.

## Artifact identity and scope

| Artifact | SHA256 |
| --- | --- |
| `paper.pdf` | `ed5c207f3fd85a4e0d41f0d39d6c9b1219d85def770eede716947586615ac72c` |
| `paper.tex` | `8f30636542bee0768208a5536d1bdb7428b8445dfc798378bbda57cc5030204c` |
| Comparison TeX at `3416df8f085b4fce76951e922c61663e3147f5a2` | `088d75baa04f4cf29fbb7b496fe09641c71a79d2c4042683d09ff1feaf9e2353` |

I read the required `AGENTS.md`, `docs/workspace.md` and learner profile, compared the final TeX with the specified Git revision, and examined PDF text for pages 1–2, 6 and 16–17. I also read the manuscript's construction, model and concluding claim boundaries and the original prospective protocol. PDF geometry and visual rendering are outside this scientific review.

The final source differs from the initially assigned candidate only by the two announced page-2 clarifications: the opening no longer conflates the three-trial repeated and once-only constructions, and the final PCA/SVM expansion explicitly improved one repeat and worsened two. Reversing these two text replacements reproduced the initial candidate TeX hash exactly.

I did not read the package README, validation ledgers, other reviewer reports, or author/probe memos. Required orientation files contain historical status summaries; those summaries were not used as independent support for this verdict. No fitting, model loading/replay, neural-array access, notebook execution, metadata optimization, or scientific rerun occurred. Only this audit file was written by this reviewer.

## Direct evidence checked

I used ordinary CSV parsing and arithmetic on these saved scalar sources:

- `outputs/source-reuse-width-20261114/complete-01/aggregates_reuse/metrics.csv` and `aggregates_width/metrics.csv`;
- the same run's `report_reuse/paired_contrasts.csv` and `report_width/paired_contrasts.csv`;
- this manuscript's `data/case_scores.csv`, `model_pair_means.csv`, `model_pair_best_means.csv` and construction summaries;
- `docs/experiments/source-reuse-width-20261114/protocol.md` for the predefined construction and model differences.

All **768 pair-score records**, covering observed repeats and sampled label controls, exactly match the original scalar metrics. All **96 representation/readout/arm means and 288 underlying observed seed values** in the model summary agree with those records. The manuscript's entire `data/` directory is unchanged relative to the specified comparison revision. These checks authenticate the interpretation against saved scalars; they do not establish fresh prediction validity or independent biological replication.

| Changed finding | Independent check and scientific assessment |
| --- | --- |
| More distinct trials helped CEBRA-Time | B5 minus B2 mean gains are +21.30, +29.63, +25.46 and +13.89 percentage points for logistic, SVM, kNN and LDA. The fixed 16-row construction simultaneously broadens recorded response coverage and reduces reuse. The overview names both changes and leaves their separate contributions unresolved. |
| Repeated assembly has selective benefits | Time/kNN gains +17.13 points; all three observed changes exceed all five sampled control changes. Time/SVM gains +10.19 points, with observed/control overlap. Raw/PCA SVM means change by −2.78/−6.94 points, and both once-only observed score ranges exceed their sampled controls. The wording appropriately recommends checking reuse with the intended classifier. |
| Wider populations favor PCA in these comparisons | PCA and Time mean changes are positive for both width steps with all four readouts. PCA has the highest matched mean in all eight larger-roster/readout comparisons. Its final SVM changes are +16.67, −2.78 and −1.39 points across the three repeats; the final overview now states the one-improvement/two-decline pattern directly. |
| Configured multisession CEBRA struggles at the last expansion | Native's final mean changes are negative for all four readouts. Its SVM mean decline combines one large loss and two small gains. The overview says “mean,” identifies added session networks and pooling changes, and recommends further validation of this configuration. It does not conclude that multisession CEBRA generally fails to scale. |
| Encoder and classifier must be assessed together | At five trials, Time beats Raw and PCA with kNN and LDA in every repeat. Raw/SVM has the highest mean in that construction. Across all six constructions, the best full tested pipeline uses Raw or PCA. The overview correctly distinguishes these two kinds of comparison. |

## Construction clarity and advice strength

The replacement table explains three different operations before presenting arm codes: selecting more recorded trials at fixed units and row count, constructing more rows from the same recorded trials, and adding whole session blocks while fixing the per-pool source budget. Its 17/49/83-unit and 3/11/20-session counts and its once-only 3-row versus repeated 16-row comparison agree with the protocol. Page 6 supplies explicit descriptive construction names, codes and totals. A reader can understand the practical comparisons on page 2 without first decoding B2/B3/B5/U3/Wmid/Wfull.

The advice is proportionate to an exploratory comparison: prioritize recorded source coverage when preparing these inputs, test repeated assembly with the intended classifier, and retain PCA as a strong wider-input benchmark. The text does not present an optimal source count, a generally superior embedding, or a universal training recipe. “Population expansion” is explicitly expansion through additional sessions and their recordings; it is not presented as an isolated causal effect of neuron count. The Native comparison retains its architecture/pooling confounds, with fuller supervision, batch and convergence limitations on page 17.

The final opening also removes the earlier ambiguity between B3 and U3: both use three recorded trials per pool, but only the repeated construction has the stated mean Time advantage for both kNN and LDA. The surviving explicit every-repeat superiority claim concerns the five-trial construction and is supported by all twelve relevant paired comparisons.

## Retained inference limits

Pages 1–2 define the label-conditioned assembly and previously inspected development set. Page 2 expressly limits the findings to different contributing trials from the same sessions and leaves new sessions, subjects and unknown-label natural trials unevaluated. Computational repeats remain distinct from biological replication. The changed text does not turn recorded trial IDs, reused blocks, synthetic rows or cue bins into independent biological observations.

The overview keeps source coverage distinct from unmeasured spatial-field coverage; the later results explicitly leave authenticated place-field attribution unresolved. It makes no claim about simultaneous population dynamics, ordered-path recovery, intention, neural mechanism or formal observability. Shuffle comparisons remain descriptive sampled controls, without significance or biological uncertainty claims. Exact results and repeat-level qualifications remain available on pages 16–17 and in the unchanged scalar tables.

The revision therefore answers what input changes helped, which complete pipelines performed best, and where the configured CEBRA variants struggled, while preserving the evidence boundaries needed for a lab to interpret those observations.
