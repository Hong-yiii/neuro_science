# Matched PCA versus raw: verified exploratory results

**Primary paired effect: +0.007023 nats (raw-selected loss − PCA-selected loss).** The historical point comparison favors **PCA**. This is not a confirmatory superiority result.

Training-source CV selected λ=1 (raw) and λ=1 (PCA), before new historical evaluation. Absolute selected losses are **0.664564 raw** and **0.657541 PCA**. Balanced constant-.5 loss is **0.693147**.

## Explain it simply

We gave two methods the same recordings and the same question: did a particular middle corridor component appear in the later path, while start and goal stayed fixed? One method kept each unit's first-second rate. The other first mixed those rates into fewer summary numbers using PCA. Both then used the same type of simple probability predictor and the same three penalty choices.

Probability loss punishes confident mistakes; smaller is better. The difference above is the missing like-for-like comparison. It does not mean PCA predicts whole paths, reads intentions, or that synthetic rows are new animals/trials. We already knew the evaluation recordings from earlier work.

<figure><svg role="img" aria-labelledby="pipeline-title pipeline-desc" viewBox="0 0 800 150" style="font-size:14px" xmlns="http://www.w3.org/2000/svg">
<title id="pipeline-title">What differs between the two methods</title><desc id="pipeline-desc">Both arms use identical source-safe rows and training-only scaling. Only the PCA arm adds a training-fitted projection. Each arm selects from the same three penalties using training CV.</desc>
<rect x="5" y="20" width="280" height="90" rx="8" fill="#e7edf4"/><text x="20" y="48">Same source-safe training rows</text><text x="20" y="73">One first-second rate per unit</text><text x="20" y="98">Training-only variance-floor scale</text>
<text x="315" y="48">→ Raw → logistic λ selection</text><text x="315" y="98">→ PCA (90%, no whitening) → logistic λ selection</text>
<text x="20" y="140">Each arm: λ .01 / .1 / 1; same held-out rows and weights. No endpoint decoder substituted.</text></svg><figcaption>Figure 1. PCA makes new weighted combinations of the same unit rates; it does not add recordings.</figcaption></figure>

## Selected-arm results by endpoint

| Endpoint | Raw loss | PCA loss | Raw−PCA | Raw BA | PCA BA |
|---|---|---|---|---|---|
| 2→1 | 0.694618 | 0.694618 | 0.000000 | 0.500000 | 0.500000 |
| 3→1 | 0.775618 | 0.771723 | 0.003895 | 0.250000 | 0.250000 |
| 4→1 | 0.643258 | 0.642561 | 0.000697 | 0.500000 | 0.500000 |
| 5→1 | 0.810584 | 0.785025 | 0.025559 | 0.500000 | 0.500000 |
| 6→1 | 0.398740 | 0.393778 | 0.004963 | 1.000000 | 1.000000 |

<figure><svg role="img" aria-labelledby="endpoint-title endpoint-desc" viewBox="0 0 720 300" xmlns="http://www.w3.org/2000/svg"><title id="endpoint-title">Matched loss differences by endpoint</title><desc id="endpoint-desc">Bars right of zero favor PCA; left favor raw. Values are descriptive historical-validation loss differences, not confidence intervals.</desc><line x1="370" y1="35" x2="370" y2="235" stroke="#64748b"/><text x="120" y="25">Favors raw ←</text><text x="405" y="25">→ Favors PCA</text><text x="15" y="62">2→1</text><rect x="370.00" y="45" width="0.00" height="23" fill="#087f5b"/><text x="580" y="62">+0.000000</text><text x="15" y="100">3→1</text><rect x="370.00" y="83" width="28.96" height="23" fill="#087f5b"/><text x="580" y="100">+0.003895</text><text x="15" y="138">4→1</text><rect x="370.00" y="121" width="5.18" height="23" fill="#087f5b"/><text x="580" y="138">+0.000697</text><text x="15" y="176">5→1</text><rect x="370.00" y="159" width="190.00" height="23" fill="#087f5b"/><text x="580" y="176">+0.025559</text><text x="15" y="214">6→1</text><rect x="370.00" y="197" width="36.89" height="23" fill="#087f5b"/><text x="580" y="214">+0.004963</text><text x="160" y="275">Raw-selected loss − PCA-selected loss (nats)</text></svg><figcaption>Figure 2. Equal-endpoint comparisons on an exposed, known-label pseudopopulation benchmark.</figcaption></figure>

A positive paired difference can occur even when both methods are worse than the .5 baseline. Inspect absolute losses as well as the difference. Endpoints 2→1 and 4→1 are point/influence-only because source support is exceptionally small.

## All six recipes (nothing hidden)

| Arm | λ | Selected | CV loss | Historical loss | Baseline Δ | BA | Brier | AUROC | Training loss |
|---|---|---|---|---|---|---|---|---|---|
| Raw | 0.01 | no | 0.963192 | 1.507000 | -0.813853 | 0.512500 | 0.346203 | 0.425000 | 0.245166 |
| Raw | 0.1 | no | 0.619286 | 0.847324 | -0.154177 | 0.500000 | 0.288352 | 0.425000 | 0.325549 |
| Raw | 1.0 | yes | 0.600535 | 0.664564 | 0.028583 | 0.550000 | 0.237659 | 0.400000 | 0.514047 |
| PCA | 0.01 | no | 1.046015 | 1.319855 | -0.626707 | 0.512500 | 0.325108 | 0.437500 | 0.249745 |
| PCA | 0.1 | no | 0.645902 | 0.792375 | -0.099228 | 0.500000 | 0.276591 | 0.437500 | 0.328433 |
| PCA | 1.0 | yes | 0.605598 | 0.657541 | 0.035606 | 0.550000 | 0.234320 | 0.512500 | 0.514708 |

CV means weight each endpoint and fold equally. Historical means weight endpoints equally and each endpoint's two classes equally. Training loss is on assembled fitting rows, not new sources. BA is balanced accuracy, not accuracy under natural class prevalence.

### Same-penalty paired diagnostics

| λ | Mean raw−PCA | 2->1 | 3->1 | 4->1 | 5->1 | 6->1 |
|---|---|---|---|---|---|---|
| 0.01 | 0.187145 | 0.000000 | 0.095055 | 0.045691 | 0.746427 | 0.048553 |
| 0.1 | 0.054948 | -0.000000 | 0.018997 | 0.006497 | 0.229063 | 0.020184 |
| 1.0 | 0.007023 | 0.000000 | 0.003895 | 0.000697 | 0.025559 | 0.004963 |

The λ=1 raw anchor reproduces accepted historical probabilities exactly (maximum difference 0); this verifies compatibility, not independent replication. The old ~83% PCA endpoint accuracy and earlier 52.1%/45.3% path-segment means involved different targets/panels/assembly and are not matched benchmarks here.

## What PCA actually compressed

| Endpoint | Unit inputs | CV components folds0/1/2 | Final components | Final variance fraction | Distinct training sources drawn | Historical product rows |
|---|---|---|---|---|---|---|
| 2→1 | 2 | 2/2/2 | 2 | 1.000000 | 12 | 3 |
| 3→1 | 14 | 7/7/8 | 9 | 0.938474 | 31 | 10 |
| 4→1 | 3 | 2/2/2 | 2 | 0.991994 | 9 | 2 |
| 5→1 | 12 | 5/7/7 | 7 | 0.917225 | 33 | 4 |
| 6→1 | 23 | 11/11/11 | 13 | 0.918927 | 62 | 12 |

One input per unit; the whole first second is pooled, not ten separate temporal features. PCA is full-SVD, training-only, no whitening, with the smallest positive-rank dimension reaching 90% variance. Retained variance is not percent path information or brain dimensionality. Product rows reuse original sources; they are not independent observations. Every fit's full state, singular spectrum, feature order and convergence are saved locally.

### Class recalls

| Endpoint | Arm | Absent recall | Present recall |
|---|---|---|---|
| 2→1 | raw | 1.000000 | 0.000000 |
| 2→1 | pca | 1.000000 | 0.000000 |
| 3→1 | raw | 0.000000 | 0.500000 |
| 3→1 | pca | 0.000000 | 0.500000 |
| 4→1 | raw | 0.000000 | 1.000000 |
| 4→1 | pca | 0.000000 | 1.000000 |
| 5→1 | raw | 0.000000 | 1.000000 |
| 5→1 | pca | 0.000000 | 1.000000 |
| 6→1 | raw | 1.000000 | 1.000000 |
| 6→1 | pca | 1.000000 | 1.000000 |


## Declared shuffled-label references

| Null | Arm | Selected-policy tail | Maximum-six tail |
|---|---|---|---|
| ordinary | pca | 0.128713 | 0.178218 |
| ordinary | raw | 0.168317 | 0.188119 |
| temporal_half | pca | 0.168317 | 0.198020 |
| temporal_half | raw | 0.198020 | 0.227723 |

Inclusive plus-one references, with 1e−12 near-tie handling; 100 worlds of each kind, repeating all six CV recipes and both selections. These test no-path-association reference assumptions for each arm versus baseline. **They are not p-values for PCA/raw equal predictive risk or PCA superiority.**

| Null | Worlds | Median actually changed fraction | Pure strata | Sources in pure strata |
|---|---|---|---|---|
| ordinary | 100 | 0.446809 | 0 | 0 |
| temporal_half | 100 | 0.313830 | 52 | 64 |

Temporal halves use training-defined trial-index boundaries. Pure strata cannot change labels. Neither conditioning nor label movement verifies serial exchangeability.

## Source-resampling sensitivity, not confidence intervals

| Quantity | 2.5th percentile | Median | 97.5th percentile |
|---|---|---|---|
| paired_difference | -0.011444 | 0.005029 | 0.023426 |
| pca | -0.073380 | 0.021788 | 0.109630 |
| raw | -0.087513 | 0.015385 | 0.100612 |

Raw/PCA rows above are baseline-relative Δloss; paired_difference is raw loss minus PCA loss. 200 paired source-stratified refits use the two frozen selections, without reselection. These are **fixed-selection sensitivity percentiles**, not selection-adjusted confidence intervals, animal replication, or a superiority test. 17/28 validation session×endpoint×label pools are singletons; copying one source cannot estimate missing variability. Aggregate summaries inherit that limitation.

### Assembly randomness (no reselection)

| Seed | Raw baseline Δ | PCA baseline Δ | Raw−PCA |
|---|---|---|---|
| 1 | 0.018083 | 0.024200 | 0.006118 |
| 2 | 0.020706 | 0.030420 | 0.009714 |

These change mixtures of existing recordings, not biological samples.

### Leave one endpoint out (point effects)

| Omitted endpoint | Remaining mean raw−PCA |
|---|---|
| 2->1 | 0.008779 |
| 3->1 | 0.007805 |
| 4->1 | 0.008604 |
| 5->1 | 0.002389 |
| 6->1 | 0.007538 |


### Leave one session out (paired fixed-recipe refits)

| Omitted session | Raw baseline Δ | PCA baseline Δ | Remaining raw−PCA | Original common-endpoint difference | Dropped endpoints |
|---|---|---|---|---|---|
| 20180705_session01 | 0.018443 | 0.029104 | 0.010661 | 0.007023 | none |
| 20180706_session01 | 0.036582 | 0.042480 | 0.005898 | 0.007023 | none |
| 20180710_session01 | 0.021350 | 0.028929 | 0.007578 | 0.007023 | none |
| 20180716_session01 | 0.036097 | 0.044876 | 0.008779 | 0.008779 | 2->1 |
| 20180727_session01 | 0.021623 | 0.028813 | 0.007190 | 0.007023 | none |
| 20180731_session01 | 0.012297 | 0.018203 | 0.005906 | 0.007023 | none |
| 20180802_session01 | 0.036429 | 0.043208 | 0.006779 | 0.007023 | none |
| 20180807_session01 | 0.002695 | 0.005871 | 0.003176 | 0.007023 | none |
| 20180810_session01 | 0.056784 | 0.063555 | 0.006771 | 0.007023 | none |
| 20180814_session01 | -0.003931 | 0.004510 | 0.008441 | 0.007023 | none |
| 20180823_session01 | 0.009517 | 0.015580 | 0.006063 | 0.007023 | none |
| 20180917_session01 | 0.074168 | 0.082082 | 0.007914 | 0.007023 | none |
| 20180919_session01 | 0.023257 | 0.031861 | 0.008604 | 0.008604 | 4->1 |

Session removal drops its sources and unit columns. Comparisons use only common remaining endpoints; overlapping refits are not independent replications or unit-identity transfer.

## Data, limits, and verification

147 original-training + 41 historical-validation sources; 49 distinct selected-unit IDs, 13 sessions, 756 observed unit–source pairs. Different endpoints have separate panels. Each artificial row uses known path labels to join session blocks, preserving each source's cells/bins. This is **condition-level response-distribution separability**, not a simultaneous natural trial with an unknown label. Missing recordings stay masked, not zero-filled.

The window is exactly [0,1) s of the accepted operational cue, excluding variable tails. Eligibility previously used historical-validation support. The target is directed component `D_N_C_M__N_C_B` among all interior corridor runs after removing first/last runs, not a single midpoint or full-path reconstruction. Start/goal conditioning is not control for all varying history, gaze, heading, cue, or state. No new nuisance family was fitted; the older nuisance-only failure does not exclude confounds. Simultaneity, cue/task/animal/anatomical metadata and serial independence remain unresolved.

No minimum biologically worthwhile effect is agreed. No absence/equivalence, universal superiority, confirmatory H1, H1b low-dimensional organization, H2, causal planning or mechanism claim follows from this benchmark.

Completed **26,266** fit instances in **23.48 min**; all converged. Forward-only verifier replayed **26,266** with **zero new fits**, checking saved predictions, source lineage, preprocessing, selections, nulls, bootstrap and sensitivity summaries. It independently calculates probability metrics/selection/reference summaries but shares assembly, label/resampling and forward helpers; it is not wholly independent software. AI review is not human peer review or lab metadata verification.

Full raw data/models/lineage/logs remain local and ignored. Git contains only code, methods, reports, lightweight summary and verification/review receipts. Use the execution ledger for paths and exact commands. This offline report needs no network, JavaScript, server, or model fitting.
