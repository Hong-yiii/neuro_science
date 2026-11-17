# Critical methods review after the expanded user request

15 November 2026. Independent researcher-agent assessment; not external human peer review.

**Recommendation: REVISE before approval under the expanded criterion.** The paper's bounded conclusions are generally defensible, but the paper does not yet give a colleague enough visible evidence to assess its data selection, construction and validation. My previous PASS concerned the bounded synthesis and the correctness/readability of its claims. It is not acceptance of methodological completeness under this request.

Reviewed current PDF SHA256: `dc6ea8e5e2d422657b32ca8001eb706428bb329025fa473c9f75121bda05ba02`.
Reviewed current TeX SHA256: `2f1630251df8d445e1242b028a72f94e17ce140d9dcae7164f9576c203eb6b1a`.
Evidence anchor remains `a0ca80180e2bb52b90e499357d3d6965b26806da`.

This assessment used the current manuscript, its already inspected unchanged ten-page PDF, public reports/protocols/code, and saved public notebook aggregates and images. No fitting, model loading, scientific replay, raw/neural-array or private-output access occurred. I did not inspect the other current manuscript reviewers' memos. Only this working memo is written; no tracked manuscript change is made.

## Main diagnosis

The paper gives the reader two schematic workflows, an arm-count table and strong caveats, then moves quickly to model scores. It does not visibly connect the archive to the analyzed sources, show the source-support distribution behind the eligibility rule, walk through an actual constructed row, or report the results of the construction checks next to the method they validate. Its final paragraph about thousands of authenticated files verifies a computational record; that count is not an explanation of why the assay is valid.

This is a presentation and methodological-evidence gap, not a request to repeat the experiment. Much of the missing evidence already exists. More result plots alone would not repair it. The revision should let a reader answer: **what was recorded; what survived which selection; what one model input actually contains; how often the same recordings reappear; what was checked; and which scientific questions those checks leave unresolved.**

## Prioritized gaps and required remedies

| Priority | Current gap | Required change in the paper |
| --- | --- | --- |
| 1 | Archive inventory, analysis cohort and constructed sample size are scattered across prose. | Add an inventory/schema table and a counted eligibility diagram. Separate archive records, eligible current trials, protected contributors, selected source IDs, session-block draws, pseudorows and optimizer exposures. |
| 1 | The construction equation is correct but does not teach an actual input. | Add an evidence-backed worked row: one endpoint class, actual session-block widths, anonymous source choices, all ten bins copied together, then concatenation. Show a second row that reuses blocks. |
| 1 | Totals conceal uneven support and development dependence. | Show latest-cohort training/development source counts by session and class, plus the constructed class quotas and realized training reuse/duplicate-tuple counts. Include development singleton pools visibly. |
| 1 | Safeguards are mostly asserted, with verification outsourced to references. | Put a compact table of completed validity checks, numerical results, scope and remaining limits inside the paper, adjacent to construction and training. |
| 2 | Final development scores are shown without their training gap or actual endpoint-head diagnostics. | Add a compact training/development and pair/start/goal diagnostic view using existing case tables. Do not diagnose a unique cause of the gaps. |
| 2 | The model page explains objectives but supplies no direct optimization/exposure evidence. | Include a saved learning example or small complete learning panel, tied to the fixed updates and sampling exposure. Keep its objective distinct from held-development prediction. |
| 2 | Historical progression consumes space without a compact cohort comparison. | Replace part of the historical prose with a cohort/evaluation table that makes the changing class count, unit/session count, source protection, feature dimension and evaluation object explicit. |
| 3 | Some images repeat final-score information while the key methods are invisible. | Prefer construction/support/validation images over another attractive embedding or selected high-score confusion. A latent trajectory can be supplementary, explicitly descriptive. |

## Exact existing evidence and extraction locations

Notebook indices below are **zero-based cells and outputs in the reviewed 40-cell publication copies**, not the frozen 38-cell source notebooks. The extra supplement and editorial note shift later locations.

- **R** = `experiments/source_reuse_width_20261114/walkthrough_20261115/published/source_reuse_20261115.executed.ipynb`.
- **W** = `experiments/source_reuse_width_20261114/walkthrough_20261115/published/population_width_20261115.executed.ipynb`.

| Evidence | Exact source | What can be shown now |
| --- | --- | --- |
| Archive contents, physical units and omissions | `data/README.md`, lines 19–63; `docs/compact-cue-source-20261026.md`, lines 36–95 | 195 selected units/58 sessions; 5,576,459 full unbinned timestamps; 23,901 trial records, including 23,200 successes/701 timeouts; spike milliseconds versus Ripple seconds; Eye events/masks and Unity marker/deltas; omitted dense position/heading/gaze and spatial maps. These are archive totals, not the current model's training sample. |
| Global source filtering | `docs/compact-cue-source-20261026.md`, lines 82–88; latest `protocol.md`, lines 27–49 | 15,553 eligible original-outer-training rows, split as 12,288 inner training/3,265 exposed development; 5,872 protected current/predecessor contributors; 4,427 training rows embargoed, leaving 7,861 globally. Do not subtract contributors as though they were training-row exclusions. |
| Latest panel selection and rosters | `docs/experiments/source-reuse-width-20261114/design.json`; `protocol.md`, lines 35–63; R/W cell 3, output 1 | Fixed nine classes; exact metadata optimization and zero-gap certificates; core/middle/full 17/49/83 columns, 3/11/20 sessions, eligible training 160/543/912 and development 56/210/365; singleton development pools 5/18/41. |
| Source tensor and observation mask | R/W cell 5, outputs 0 and 2 | Shape `(1277,83,10)`; only 5,375 observed source×unit entries out of 105,991; ten bins per observed entry. Each source measures its own session columns, not the other sessions' columns. This makes the mask's importance concrete. |
| Prefit construction results | R/W cell 5, output 1 and output 0; latest notebook validation ledger | All 48 scheduled plans checked; zero contributor overlap; required rank ≥7, actual global minimum rank 17 reported in the ledger. The displayed observed seed-0 arms have ranks 17/49/83 and zero constant columns. Do not present a selected seed's table as the complete 48-case rank table. |
| Actual training multiplicity and identical source-tuple repeats | R cell 7, output 1; W cell 7, output 1 | Seed-0 repeated whole source tuples: B2 77, B3 23, B5 6, U3 0, Wmid 0, Wfull 0. These count rows after the first identical tuple, not pairwise collisions or numerical feature equality. Zero full-tuple repeats does not mean no reused blocks. |
| Worked construction | R cell 9, outputs 1–5; W cell 9, outputs 1–5 | B2 seed 0: training `(144,17,10)`, development `(72,17,10)`; blocks S16/S27/S34 contain 3/8/6 columns. For class `1→2`, row 0 uses local source choices `(2,2,2)`; row 1 uses `(1,2,2)`. The latter shares two blocks with the former. The choices are local ordinal aliases, not globally equal source IDs. |
| Class quotas | R/W cell 9, output 3; cell 7, output 0 | Training 16 rows per pair and development 8; U3 training 3 per pair. Balanced constructed counts are a design choice, not evidence of balanced recorded source availability. |
| Saved source-use figure | R/W cell 27, output 8, with caption at output 9 | Two panels show extra-draw fractions and distinct training sources versus training block draws. Reuse: 54/81/135/81 sources versus 432/432/432/81 draws. Width: 81/297/540 versus 432/1,584/2,880. Fractions 87.5%, 81.25%, 68.75%, 0% for B2/B3/B5/U3. This existing figure is training-only. |
| Direct arithmetic checks | R/W cells 11, 13 and 19 | Manual scaler residuals `4.768e-7`/`9.537e-7`, PCA projection residuals `7.153e-7`/`9.537e-7`, logistic forward-probability residual 0. These verify specific first-case arithmetic, not every biological assumption. |
| Architecture, optimizer and sampling exposure | R/W cells 15 and 17 | Printed Time/native architectures and parameter counts; 1,000 updates; Time 256,000 reference draws per first case; native 255/253 references per update in B2/Wmid; equal-session pooling. These distinguish assembly reuse from repeated optimizer access. |
| Saved learning curves | R/W cell 27, output 10, caption output 11 | All observed and diagnostic curves for the corresponding experiment, with separate Time/native axes. A smaller already curated example is `published/figures/first_case_reuse.png` or `first_case_width.png`, also embedded in Markdown cell 23. |
| All scores, gaps, heads and controls | R/W cell 33, output 6; current paper `data/case_scores.csv` | `train_BA`, `balanced_accuracy`, `train_development_gap`, all pair/start/goal heads, four representations, four readouts, three observed seeds and five worlds. No predictions or fitted objects are needed for these displays. |
| Complete validation results | `docs/experiments/source-reuse-width-20261114/notebook-validation-20261115.md`, lines 102–143; sibling `notebook-numeric-verification-20261115.json` | 71,496 source-block consistency checks; 4,608 split metric checks; 192 encoder/2,304 readout reloads and 4,608 composed checks during execution; complete table/confusion reconciliation; reproduction results. |

The full latest session×class availability matrix is **not displayed in the public notebook cells I inspected**. The public design contains roster totals, not that matrix. The existing public frozen assignments are sufficient to display it without neural reads: `data/cue-source-v1/{outer_splits.csv.gz,inner_splits.csv.gz,manifest.json}`, with the exact metadata-only rule in `src/neuro/studies/population_grid.py:45–103`, projected onto `design.json`'s nine classes and rosters. Any such new display should be labelled a presentation of existing metadata, preserve the global embargo, and reconcile to the published totals and singleton counts. It must not optimize a new panel or access spikes. Alternatively, use an already authenticated, suitably public aggregate support table if available. Do not substitute the historical 195-unit support heatmap for the latest population.

## Recommended figure and table set

### 1. Data inventory and eligibility, before any score

Use one compact table for each data stream's unit, content, role and availability. Pair it with a counted flow from the 195-unit/58-session archive through frozen assignments and the global contributor embargo to the latest fixed-class population. Show the 27-unit/30-class study as a historical branch, not a stage that somehow turns into the latest 83-unit cohort. Different class requirements admit different sessions.

Show the latest sparse tensor `(1277,83,10)` with its observed-mask count, then the dense constructed tensor. A small block diagram can illustrate the mask pattern, but label it schematic unless the exact mask is already public. Do not invent a neural raster or call a schematic source-distribution evidence. The archive totals do not all enter fitting, and Unity marker rows are not position samples.

### 2. Latest source-support distributions

Show two aligned heatmaps: eligible training and development current-source counts, 20 retained session aliases × nine pair classes. Mark the core/middle/full roster membership and display the training minima. A small adjacent class-total bar chart and the fixed constructed quotas make the difference between measured support and balanced pseudorows visible. Mark all development singleton cells and report 5/27, 18/99 and 41/180 singleton pools for core/middle/full.

Availability is not actual use. Do not relabel the 365 eligible development sources as 365 used sources without checking an existing usage summary. The current public source-use figure only covers training. Development block-draw totals are 72×3/11/20; use those with availability and singleton counts if actual used-source totals are not publicly supplied, and label the missing distinction.

### 3. One real construction recipe plus reuse accounting

Replace or extend the generic pipeline diagram with the recorded B2 seed-0 example above. Draw the three source blocks with widths 3, 8 and 6, each carrying ten bins, and concatenate them to a 17×10 row. Show both rows and their repeated S27/S34 blocks. Explain that `1→2` is used to select all three blocks before the readout predicts it.

Follow the example through training-only normalization and the two feature paths: 170 raw coordinates, or ten seven-coordinate representations yielding 70 features. Show the once-only U3 and repeated B3 source sets beside it. Include the exact duplicate-tuple table and the saved source-use panel. This directly explains why many constructed rows, and even zero identical full tuples at larger width, do not create many independent observations.

### 4. A validity-results table inside the method

Use columns **question/check**, **completed result and scope**, **what it does not establish**. Include at least the following:

| Check | Existing completed result | Remaining boundary |
| --- | --- | --- |
| Did the compact source preserve the declared inputs? | Documented native/export conservation and hash checks; original timestamps/units retained; clock units and missing-event encoding explicit. | Metadata reconciliation is not independent verification of behavioral truth, species, simultaneity or sorting quality. |
| Can the declared assay be constructed without forbidden contributor overlap? | Global embargo, all 48 prefit plans, zero cross-split contributors; exact nesting, quotas and shared-width projections; 71,496 saved source-block checks. | Disjoint IDs do not remove serial dependence or yield new animals/sessions. |
| Is seven-dimensional fitting numerically feasible? | Prefit minimum rank 17 exceeds required seven. | Rank is neither biological intrinsic dimension nor evidence that seven is optimal. |
| Was learned preprocessing fitted on training only? | Source/code boundary plus visible first-case scaler/PCA/readout arithmetic checks; development transform-only. | Development availability entered selection and development outcomes were historically exposed. |
| Were labels controlled at the correct level? | Five whole-pair source-label worlds, within session and split, before selection/assembly; same effective map across matched arms. | Five worlds are not calibrated biological inference, nuisance adjustment or a pristine confirmation. |
| Do stored fitted pipelines reproduce their outputs? | 192 encoder and 2,304 readout reloads; 4,608 composed split checks; independent metrics/confusions and source joins. | Correct computation does not prove the representation's biological meaning. |
| Did the fuller notebooks reproduce the accepted execution? | 14,304 numerical arrays match exactly on the same recordings/seeds; 96 learning records match apart from time. | Computational reproduction is not biological replication. |

Keep failures and the reviewed continuation in a brief provenance sentence. Do not replace these substantive checks with a count of software tests or authenticated files. Distinguish checks actually executed in prior studies from anything checked anew for this paper.

### 5. Learning and generalization diagnostics

Add one saved learning example and a compact train/development/head table. The public score tables already show large gaps: all four SVM pair pipelines have 100% mean training BA for U3 and Wfull. U3 development means are Raw/PCA/Time/native 40.74/40.28/24.54/26.39%; Wfull means are 46.30/72.22/48.61/27.78%. Those gaps materially qualify the result and belong in the paper, without attributing them uniquely to overfitting, source shortage or biological absence.

Include actual start/goal results or a compact figure for a declared scientifically motivated slice, such as U3 and Wfull across all four representations. For example, Wfull PCA/SVM pair/start/goal means are 72.22/56.94/78.47%. These heads are separately fitted classifiers, not pair-confusion collapses; they need not make mutually consistent predictions. Keep the appropriate chance references and explain the sparse task's 6/9 perfect-single-endpoint reference.

The saved first-case image is useful evidence that optimization was performed and errors remain. It is not evidence of convergence or a fair comparison of Time/native loss magnitudes. The complete public learning grids can be linked or included in a supplement. A 3D latent plot is lower priority than the missing support and construction displays.

## Scientific validity that remains unresolved

The revised paper can become a defensible, inspectable **conditional exploratory assay** with the evidence above. It cannot become a confirmatory neuroscience paper merely by adding verification receipts. Keep these limits explicit:

- The visual/task cue, gaze, preceding-trial state and other endpoint-correlated variables are not separated by the present controls.
- Labels are operational marker/predecessor labels, and the source join has provisional semantics. Code consistency does not independently validate acquisition meaning.
- Session grouping does not verify biological simultaneity. Cross-session noise covariance and natural-trial population dynamics are unavailable.
- Known-label assembly does not deliver unknown-label trial prediction. Repeatedly exposed development and shared recipes limit prospective generalization.
- Source IDs, session blocks, seeds and animals are different units; no row-level IID interval or seed-based biological confidence interval is justified.
- Native versus Time changes supervision, architecture, pooling and exposure. No matched pair-supervised concatenated or untrained-encoder control exists, and 1,000 updates does not establish convergence.
- Spatial-field coverage, occupancy and authenticated map joins remain unavailable; no attribution of errors to lost place fields is established.
- Ordered-path recovery, matched frozen CEBRA temporal/cross-phase transfer and reusable neural-state observability remain undemonstrated.

These are limitations to disclose, not an instruction to collect data, fit another model or reopen a historical experiment for this revision.

## Acceptance requirements for the revision

I will approve under the expanded criterion only after the final PDF itself satisfies all of these:

1. A reader can distinguish the archive inventory, eligible source cohort, selected IDs, block draws, constructed rows and optimizer updates without consulting a notebook.
2. The inventory, clocks, omitted streams and eligibility rules are explicit; the counted flow reconciles and does not mix different counting units or historical cohorts.
3. At least one latest-cohort distribution display shows training and development support, including the singleton bottleneck, alongside constructed class quotas.
4. A worked, authenticated or explicitly schematic construction example makes a row, its target, its session blocks, source reuse, bins and feature shapes understandable. Real recipe aliases are described correctly.
5. Realized reuse and whole-tuple repetition appear; absence of full-tuple duplicates is not called independence. Development dependence is visible, not only a warning in the discussion.
6. The paper reports results of the completed validation checks with their scope and residual limits. At least contributor separation, shared/nested construction, training-only preprocessing, source-label controls and computational replay/reproduction are covered.
7. Training/development gaps and actual endpoint-head diagnostics accompany final pair scores. The existing observed/control and seed details are retained; scientific caveats are not traded away for figure space.
8. Every new figure/table is traceable to a pinned public artifact, notebook cell/output or authenticated metadata-only presentation. No new raw neural reads, fits or model replay are needed. Any new aggregation is labelled accurately and reconciled with the existing record.
9. Figures are legible at the intended reading size, with complete target/cohort, source versus row counts, split, time units, metric/reference, uncertainty meaning, provenance and claim limits. More panels at unreadable size do not meet this requirement.
10. Independent review of the revised PDF/source and new figure extractions finds no material mismatch. Prior PASS files must not be represented as acceptance of the expanded revision before that review.

If ten pages remains a hard constraint, compress the repeated historical narrative and repeated caveat prose to make room for roughly three to four pages of data/construction/validity evidence. Keep one compact historical cohort comparison. Do not solve the space problem by shrinking the source-support or recipe figure until its method cannot be read. The goal is a paper that explains and demonstrates its assay, not a longer score catalogue.
