# How our data volume compares with CEBRA and hippocampal population studies

Date: 2026-09-07 Asia/Singapore (web research began 2026-09-06 UTC).
Status: bounded literature/provenance comparison, not a new neural analysis or power calculation. Four independent research branches covered original CEBRA hippocampus, original motor/visual benchmarks, independent CEBRA applications, and prospective hippocampal studies. Independent read-only scientific/source synthesis review completed with no findings; scope and evidence limits are recorded below.

## Bottom line

“Not enough lab data” was too broad. The current archive is not unusually small in total behavioral trial count. The demonstrated bottleneck is **usable source support for the particular fixed-endpoint route contrast, plus very few selected neurons recorded in each session**. This does not establish that sample size is the only cause of the nonpositive V6–V9 result.

CEBRA has been used with tens of simultaneous spike units, hundreds to thousands of calcium-imaged cells, and cross-session pseudopopulations. No universal neuron/trial minimum was established by the sources checked. Successful published examples are not a minimum-N calibration experiment for our task.

## 1. Our denominator: archive versus actual model inputs

| Object | Neurons and recording groups | Real trial support | Meaning |
| --- | --- | --- | --- |
| Current place195 archive | 195 spatially selected units across 58 sessions; 1–8/session, median 3 | 23,901 imported trials; 400–493/session | Not a 23,901 × 195 simultaneous population matrix |
| V6 development behavioral subset | Same source collection | 19,162 successful-after-successful train/validation trials | Distributed over endpoints, routes, sessions and splits |
| Primary V7–V9 panel | 29 cells assembled across 7 sessions | 82 train + 22 validation source trial IDs | Masked source tensor 104 × 29 × 10, not 104 fully observed 29-cell trials |
| Primary synthetic arrays | 29 columns; ten 100 ms cue bins | 128 synthetic rows/split/seed, 64/class | Repeated derivatives of the source pools, not new recordings |

The validation pool sizes across the seven sessions are `[1,1,3,2,1,1,1]` for component-present and `[1,2,1,3,1,2,2]` for component-absent. Thus only **6 present and 24 absent full session-block source-ID combinations** are possible. These combinations share trials and are not independent biological replicates. There can be only one complete source-disjoint validation row per label; that ceiling is not a formal effective sample size of one.

Local sources: [V6–V9 report](../../docs/reports/place195-v6-v9-autoresearch-20260906.md), [import receipt](../../notes/data_inspection/place195_all_sessions_import_20260830.md), [latest transfer/provenance audit](../../context/2026-09-06-place-data-transfer-audit.md), and [saved validation source counts](../../outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/v8b-v9-cebra-final-20260905T224554Z/v8b/v8b_session_label_bin2_source_counts.csv).

The latest local audit records that the professor-supplied 195-place-cell list is complete and unchanged upstream. A broader 364-unit list exists but is outside the clarified place-selected scope. An eight-unit candidate supplement was excluded and removed from the homelab; it is not part of these counts. This research did not change that scope or import anything.

## 2. Quantitative comparisons

Numbers refer to different units of replication; read the caveat column rather than comparing the largest integers.

| Study / benchmark | Neural population | Trials, duration and replication | Target and comparison limit |
| --- | --- | --- | --- |
| **Original CEBRA rat CA1, Schneider et al. 2023** [1,2] | **48–120 simultaneously recorded putative pyramidal units/session**, four rats / four selected datasets | **29–46 round-trip trial segments/dataset**, derived using official preprocessing/split convention; 6,577–47,431 retained 25 ms bins | Current linear-track position and running direction, not future route beyond endpoints |
| **Original CEBRA macaque S1 reaching** [1] | Single-session Area 2 spike recordings; exact unit count not verified here | Fig. 3 reports **364 active trials**; a hand-position decoding example reports **26 held-out trials**. Each modeled window is 600 ms, sampled at 1 ms and smoothed with 40 ms Gaussian s.d. | Hand position, direction, active/passive condition. Hundreds of bins per trial are not hundreds of independent trials; these quoted counts are not a reconstructed complete split inventory |
| **Original CEBRA Allen visual benchmark** [1,3] | **10–1,000 neuron subsampling sweep**; main sweep uses **pseudomice stacked across recordings**, not 1,000 simultaneous cells in one mouse | **10 repeats of a 30 s movie**; 900 distinct frames/repeat, calcium 30 Hz or spikes 120 Hz. Paper decoding uses repeats 1–8 train, 9 validation, 10 test | Repeated stimulus frame identity/content; shared externally controlled stimulus provides alignment. Not prospective unknown-path decoding |
| **Shin & Jadhav 2025, CEBRA rule switching** [4] | Recorded CA1 totals **19–49 units/animal-day**, including pyramidal cells and interneurons; pyramidal-only counts 14–44. Four rats, one recording day each | 3–4 run epochs/day; Methods says 20–25 min/epoch, Results says 20–30 min. Exact total CEBRA training-trial count not reported in checked sections | CEBRA conditioned on spatial–temporal bin, trajectory and rule; single-animal and multi-animal encoders, testing within animals. Current rule/context rather than our cue-to-future-route target |
| **Jiang et al. 2026, CEBRA CA1 spatial-map learning** [5] | Reported same-FOV populations of **409–1,387 calcium-imaged cells per animal** | 12 listed population counts; six-day protocol with **8 min familiar + 14 min novel** environment/day; about 160 ms bins; one early-condition animal excluded for z-drift | Current track location, including comparison under CA3 perturbation. Calcium and sparse spike counts are not equivalent measurement modalities |
| **Prince et al. 2025, prospective navigation, not CEBRA** [6] | Decoding excluded sessions with **<20 units in the analyzed region**; actual per-session range not verified | Also excluded **<50 behavioral trials/session**; seven mice, 6–12 recording sessions/animal, up to five hours/day | Cue-triggered goal/choice updating and outcome prediction. These are that paper's inclusion floors, not universal recommended minima |
| **Johnson & Redish 2007, prospective CA3, not CEBRA** [7] | Key ensemble dataset: **33–72 simultaneous cells in four sessions**; 237 spike trains from three rats overall | Lap-based tasks, 30–40 or 40 min sessions; exact laps per ensemble session not enumerated here | Decoded nonlocal positions/sweeps toward potential future paths, not an unknown future-choice classifier; tuning curves used whole-session data |
| **Sun et al. 2025, orthogonalized state machine, not CEBRA** [8] | Thousands of same-session CA1 calcium cells: mean of per-mouse session-average counts **4,682 ± 827**; 11 mice | **80–200 trials per one-hour session**, reported 124 ± 43; 97 sessions in a main comparison | Two cue/reward trial types; population correlations, UMAP and learning/model comparisons, not held-out route decoding beyond endpoints |

### Exact original rat benchmark dimensions

The research branch inspected small official compressed preprocessed files, not the large raw recording archive. Trial counts apply the CEBRA rule grouping every second running-direction change as a round-trip boundary, with start/end boundaries added. They are algorithm-defined trial segments; no raw-video lap audit was performed.

| Dataset | Spike matrix (time bins × neurons) | Derived round-trip segments | Retained bins × 25 ms |
| --- | ---: | ---: | ---: |
| Achilles | 10,178 × 120 | 42 | 254.450 s |
| Buddy | 6,577 × 48 | 29 | 164.425 s |
| Cicero | 47,431 × 55 | 46 | 1,185.775 s |
| Gatsby | 17,026 × 66 | 42 | 425.650 s |

**These seconds are retained analyzed-bin exposure, not raw elapsed session duration.** The upstream hc-11 collection has eight exploration sessions in four rats, with approximately 45 min MAZE epochs and much longer PRE/POST rest. The CEBRA selected/preprocessed data are not the entire source collection [2,9].

The original benchmark therefore does not establish that one needs thousands of independent laps for CEBRA. It does show much denser same-session population sampling than our median three selected cells. Relative to that median, 48–120 cells is **16–40 times as many co-recorded features**, not a 16–40-fold guarantee of information or statistical power.

## 3. What changes the interpretation

### Total trial count is not the main demonstrated shortage

Our approximately 400 trials/session are not obviously below all successful neuroscience datasets. For example, the state-machine study reports 80–200/session. But its trials have thousands of cell measurements and two trial types; ours have a few selected cells and 30 endpoint pairs before subdividing actual paths.

The historical task arithmetic is roughly `400 trials / 30 endpoint pairs ≈ 13 trials/pair/session`, before route subdivision, QC/inclusion and train/validation allocation. This is an illustration of fragmentation, not an estimate of support for every real condition. Our actual support audit, not that average, establishes the current validation shortage.

### Dense time sampling helps represent a signal, but does not create independent trials

CEBRA's rat data supply many 25 ms population vectors while position changes continuously. Our ten cue bins contain a single trial's future-route label and sparse counts. Sampling our cue at 1 ms would increase array rows but would not recreate macaque reaching information or additional independent route outcomes. Smoothing and temporal receptive fields also change which observations contribute to each prediction.

### Pseudopopulations themselves are not disqualified

CEBRA's visual example is a direct counterexample to “pseudopopulations cannot be useful.” Ten controlled movie repeats provide the same stimulus sequence across sessions, supporting a well-defined stimulus-conditioned population comparison. Our unknown future route varies across trials and is used to select matching source blocks. Both constructions have claim limits, but they answer different questions.

Thus, moving away from pseudotrials for our primary H1 analysis is a recommendation about preserving the real trial's neural/path link and avoiding a restrictive common-panel intersection—not a verdict against every CEBRA pseudopopulation analysis.

### Multi-session CEBRA is an alternative to row stitching, not a cure

Official multi-session CEBRA fits a separate encoder for each session and samples relationships across sessions using shared context. It explicitly allows different neuron and sample counts [10]. We could investigate that after source-level baselines and support checks, while keeping each real trial intact. It does not recover unrecorded simultaneous covariance, add route alternatives, establish information in a one-cell session, or make supervised geometry independent confirmation.

### A published analysis is not automatically our validation standard

The original CEBRA paper states that CEBRA-Time and some unsupervised comparators saw the full unlabeled dataset for representation fitting, with the split applied to downstream decoding. Its topology analyses are also distinct from held-out decoding. Shin & Jadhav describe z-scoring across task epochs before dimensionality reduction. This comparison has not exhaustively audited all papers for leakage or inferential validity; it is not permission to copy their preprocessing unchanged.

## 4. Practical conclusion for the fixed-place195 project

1. Keep the current dataset scope: do not quietly reintroduce excluded units or assume the export is incomplete.
2. Audit **real per-session/per-endpoint/per-route support** before a new model. The desired contrast may be infeasible even though the archive is sizeable.
3. Establish a source-safe goal/start positive control and simple within-session or per-cell path associations. Pool estimates conservatively rather than treating cells or sessions as independent animals.
4. Consider multi-session representation learning only if those measurements and shared labels support it. No extra pseudorow count, architecture sweep or universal minimum-N rule is justified by this review.
5. If a supported design emerges, estimate data needs with **whole-source-trial learning curves** and, where possible, neuron subsampling. Preserve session/time structure and evaluate the actual beyond-endpoint target. A larger future collection would ideally add route repetitions and genuine simultaneous population coverage, not merely more dates with sparse units.

The accepted V6–V9 benchmark remains development-only because of the previously documented holdout exposure. No genuinely untouched confirmation set was created by this literature review.

## 5. Source passages and provenance

**[1] Schneider, Lee & Mathis (2023), Nature.** *Learnable latent embeddings for joint behavioural and neural analysis.* [Primary paper](https://www.nature.com/articles/s41586-023-06031-6).

- Methods, Rat hippocampus dataset: “numbers of recorded putative pyramidal neurons for each rat ranged between 48 and 120”; “spikes were binned into 25 ms time windows.”
- Same section: trial is “a round trip from one end of the track”; nested threefold train/validation/test decoding.
- Fig. 3: 364 active macaque trials; text reports 26 held-out hand-position test trials. Exact macaque unit count was not retrieved.
- Methods, Decoding analysis: visual decoding first eight repeats train, ninth validation, last test. Some current dataset classes call the first nine repeats the training object; that implementation distinction does not replace the paper's validation description.

**[2] Official CEBRA rat loader and preprocessed files.** [Pinned loader](https://github.com/AdaptiveMotorControlLab/CEBRA/blob/d1842ccc659bdf2d458ab31784ae029b9d48d21f/cebra/datasets/hippocampus.py), particularly URL table and `SingleRatTrialSplitDataset._split`; [single-session demo](https://cebra.ai/docs/demo_notebooks/Demo_hippocampus.html).

- File URL pattern: `https://cebra.fra1.digitaloceanspaces.com/data/rat_hippocampus/{achilles,buddy,cicero,gatsby}.jl.gz`.
- Declared compressed checksums, in that order: `5d7b243e07b24c387e5412cd5ff46f0b`, `339290585be2188f48a176f05aaf5df6`, `f262a87d2e59f164cb404cd410015f3a`, `564e431c19e55db2286a9d64c86a94c4`.
- Exact initial temporary clone commit was not captured. A follow-up verified the loader/counting convention at the pinned revision above. These are source-declared checksums, not claimed independent retained hash receipts. Temporary public data files were cleaned up.

**[3] Official Allen CEBRA demo.** [Documentation](https://cebra.ai/docs/demo_notebooks/Demo_Allen.html).

- “pseudomice (stacked neurons from multiple mice)” and “Natural Movie1 stimulus (30sec, 30Hz) ... 10 repeats.”
- `num_neurons` options: `[10, 30, 50, 100, 200, 400, 600, 800, 900, 1000]`. This is a tested sweep, not a minimum sufficient count.

**[4] Shin & Jadhav (2025), J Neurosci.** *Ventral Tegmental Area Dopamine Neural Activity Switches Simultaneously with Rule Representations in the Medial Prefrontal Cortex and Hippocampus.* [Full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC12424963/), [DOI](https://doi.org/10.1523/JNEUROSCI.1670-24.2025).

- Table 1 CA1 pyramidal/interneuron pairs: 34/7, 14/5, 44/5, 31/3; total recorded CA1 counts 41, 19, 49, 34.
- Methods: “Training labels included spatial–temporal bin, trajectory, and rule”; spiking from each region trained separately for individual animals.
- Trial selection: rewarded trials above the day's 60th performance percentile; 20% of these and all lower-performance trials left out. Exact model-by-model neuronal inclusion was not independently reconstructed from source code.

**[5] Jiang et al. (2026), Nature Communications.** *Distinct CA3 inputs differentially shape the learning-dependent evolution of right CA1 spatial maps.* [Full text](https://www.nature.com/articles/s41467-026-72275-1).

- Fig. 3D lists cell counts 946, 666, 409, 764, 771, 761, 804, 485, 829, 1387, 926, 1085. The caption mentions n=11 while listing 12; Methods documents one early-condition z-drift exclusion, with that animal retained for late-condition analysis. Do not claim every analysis used all 12 animals.
- Methods: each imaging day familiar environment “8 min” then novel “14 min”; same FOV throughout the protocol. Fig. 2E/4 and Methods document CEBRA plus KNN position decoding and approximately 160 ms bins.

**[6] Prince et al. (2025), Nature Communications.** *New information triggers prospective codes to adapt for flexible navigation.* [Full text](https://www.nature.com/articles/s41467-025-60122-8).

- Neural-decoding Methods exclude sessions with fewer than 20 units in the region or 50 trials. This is a study-specific inclusion rule.
- Seven final mice, 6–12 sessions/animal; 3,892 hippocampal units and 2,557 mPFC units are aggregate recordings, not simultaneous population sizes. Supplementary per-session trial counts were not retrieved.

**[7] Johnson & Redish (2007), J Neurosci.** *Neural Ensembles in CA3 Transiently Encode Paths Forward of the Animal at a Decision Point.* [Full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC6673267/).

- Key recordings: four sessions, 33–72 simultaneous cells. The larger behavioral cohorts are not the same N as this ensemble subset.
- The paper's nonlocal sweep evidence is not equivalent to correctly classifying the subsequently chosen path; exact lap counts per ensemble session were not recovered here.

**[8] Sun et al. (2025), Nature.** *Learning produces an orthogonalized state machine in the hippocampus.* [Full text](https://www.nature.com/articles/s41586-024-08548-w).

- Main text: “80–200 trials (124 ± 43 trials, n = 11 mice)” in one-hour sessions.
- Imaging section: “within single sessions: 4,682 ± 827 on average per mouse across all sessions.” These are calcium imaging cells, not extracellular spike units.
- Fig. 2 main comparison: 97 sessions from 11 mice. The low-dimensional visualization is UMAP, not CEBRA.

**[9] Grosmark/Buzsáki source collection, CRCNS hc-11.** [Dataset description](https://crcns.org/data-sets/hc/hc-11/about-hc-11).

- Eight recordings, four male Long–Evans rats; approximately four-hour PRE, 45-minute MAZE and four-hour POST epochs. Do not attribute all those hours to the selected CEBRA training data.

**[10] Official multi-session CEBRA.** [Documentation](https://cebra.ai/docs/demo_notebooks/Demo_hippocampus_multisession.html).

- “It fits one model per session but the pos/neg sampling is performed across all sessions”; neuron and sample counts can differ. This is not a common-column pseudo-trial matrix.

### Additional screened study, not a primary size comparator

Zhang et al. (2026), PLoS Biology, *Flexible goal learning involves coordinated population activity in dCA1 and medial orbitofrontal cortex* ([paper](https://journals.plos.org/plosbiology/article?id=10.1371/journal.pbio.3003824)): 14 sessions in five rats; 40 learning trials/session plus probes. Aggregate units are 272 dCA1 and 285 mOFC, but exact simultaneous counts were not reported in the inspected text. CEBRA was visualization only; GaussianNB supplied the quantitative decoder. Aggregate units divided by sessions would not establish the actual recording distribution, so that inferred average is not used in the comparison table.

## 6. Verification limits and retained research artifacts

No local raw or locked-test records were opened, no lab-server access was performed, and no neural models were fit. Research used public primary text, official code/docs, small public preprocessed rat files in one branch, and existing local reports/metadata. Raw public acquisition datasets were not downloaded. Source-count comparisons are not a full methods replication, meta-analysis, or prospective power analysis.

Research branch logs are retained by the harness under `/tmp/pi-subagents-uid-1000/async-subagent-runs/2c13ec99-3c35-45ca-abec-57e86c95737b/output-{0,1,2,3}.log`; rat-provenance follow-up is under `/tmp/pi-subagents-uid-1000/async-subagent-runs/ad4087bf/output-0.log`. These are temporary harness artifacts; this report is the named durable source summary. Public small-download scratch directories were cleaned by their owning researchers.

Independent synthesis review: `/tmp/pi-subagents-uid-1000/async-subagent-runs/1bd20c55-226f-4e12-b676-3f0d590e3e7b/output-0.log`, verdict **no findings**. Review checked local denominators, recorded rat-count provenance, and units/caveats for Allen, Shin, Jiang, Prince and Sun; it was not a refit or exhaustive replication. Parent checks confirmed four local report links resolve, the validation source-combination arithmetic, and no remaining Markdown diagnostics.
