# Way forward: reliable prospective-path coding with pseudopopulations

Date: 2026-09-08. **Current proposed direction, not a new experiment or positive biological result.**

This consolidates the discussion after the [completed path-generalization study](../professor_updates/path_generalization_20260907/README.md). It supersedes any reading of the earlier recommendations as requiring a large simultaneous population or abandoning pseudopopulations. H1a/H1b remain defined in [research questions](../research-questions.md).

## Answer in brief

The priority is **reproducible independent source-trial evidence for a meaningful route contrast**, not simply a larger synthetic matrix. Pseudopopulations can remain central given the operational difficulties of large simultaneous monkey recordings. A data-count-only explanation has not been established; more data is not a guaranteed cure, and CEBRA has not been isolated as the root cause.

The practical question is:

> Across separately recorded neurons, do independent trial sets reproduce an endpoint-controlled population response pattern associated with future paths?

That is a condition-level population-coding question. It is not reconstruction of the exact simultaneous neural state on one real trial, and does not establish intention or causal planning.

## What was actually learned

| Observation | Justified interpretation | Not established |
| --- | --- | --- |
| New mixtures of the same training sources: Time BA0.9925; Behavior BA0.997656 | The models are not merely memorizing 64 particular combinations | Generalization to new biological trials or recording sessions |
| Source-disjoint exact-Q factorial means: Time BA0.249167; Behavior BA0.351667 | The gap appears across the two source pools | Its unique cause, or absence of prospective hippocampal information |
| Increasing synthetic rows stabilizes ridge near its exact-Q reference, BA0.479167 | Evaluation/assembly Monte Carlo noise can shrink without new information | A biological sample-size increase |
| More dimensions, rows, and training steps do not consistently rescue CEBRA; matched B-family p19/21 | No robust rescue in the tested family | Failure of every CEBRA formulation or nonlinear model |
| Supported-interior C target: 43 units/11 sessions, 267 train/52 validation sources; mean Δlogloss+0.003860 | Better conditional support and a weak positive point estimate | Convincing family-corrected evidence: p≈0.475 ordinary/0.436 temporal |
| Constructed 290-feature validation matrix has rank9 | A finite-source construction bound, verified on that matrix | The brain's intrinsic dimensionality or a bound on every nonlinear embedding |

These seed means/ranges are descriptive. They are not biological confidence intervals. The B null covers the specified14 A0/O0 configurations, not selection of the best among50 factorial fits.

## Why keep pseudopopulations?

Condition-matched pseudopopulations estimate population response differences without requiring every neuron to be recorded together. Using a known behavioral condition to assemble evaluation rows defines a conditional benchmark; that is not automatically leakage when independent source pools and training-only preprocessing are respected. It does mean that the assembled input is not an operational unknown-label vector from one real simultaneous trial.

Preserve:

- actual source-trial splits before assembly, with all derivatives grouped;
- one source per session block across its cells and time bins;
- behavioral target and nuisance-condition semantics;
- unavailable observations as unavailable, never filled with zero;
- source/session-aware uncertainty and matched nulls.

**Those assembly protections were already implemented in this study.** Repeating them is not a newly discovered fix. A thousand resamples of one source remain dependent on that one source. Nor can synthetic assembly recover trial-to-trial correlations between neurons never recorded together. Same-session membership itself remains candidate, not lab-verified simultaneity.

## Is the CEBRA formulation weak?

There are plausible limitations:

1. Temporal proximity during the cue need not organize responses by future route.
2. A binary route label can separate empirical training source pools without identifying a reproducible path representation.
3. The current offset1 encoder embeds bins individually. The downstream decoder receives all ten bins, but the encoder is not an explicit sequence model for cross-bin patterns.
4. Sparse conditional support permits very confident fits to unstable patterns.

These are hypotheses about the formulation, not diagnoses established by the experiments. Larger output dimension is not automatically less compression: the tested dimension29 model still has a16-unit hidden bottleneck and L2 normalization. Keep CEBRA as a comparison instrument rather than define success as making its score high.

## Proposed next study: four bounded steps

### 1. Freeze the measurement and support

Specify one route component, its presence rule, one cue window, the eligible cohort, endpoint controls, and a scientifically meaningful effect before fitting. Choose by behavioral meaning and training support, not neural outcomes. The existing candidate is `D_N_C_M__N_C_B`, a directed central-middle→central-bottom corridor component; its current test uses **interior positions after dropping first and last corridor runs**, not edge-anywhere presence.

Pool compatible contexts only with endpoint-pair and available nuisance controls. Do not turn broader endpoint coverage into an easier start/goal decoder and call it prospective path information. Keep the195 selected-unit scope; do not recover the excluded supplement or assume missing units are available.

### 2. Measure independent-source reproducibility

Using the existing development data, compare condition contrasts and regularized population decoding across independent source subsets. Preserve temporal/session structure; report source counts, class support, effect sizes, probability scores, and source-level uncertainty.

A neural-only positive control can decode an easier known task variable across contexts where it varies. Do not supply the control target, its one-hot encoding, or a duplicate proxy as an input. A fixed-endpoint cohort cannot test start decoding when start is constant.

Per-unit real-trial models are complementary checks, not a replacement for pseudopopulations. **Do not require each neuron to be individually significant**: weak distributed effects can combine, and cancellation of signed coefficients is not absence of population information. Lack of a stable mean contrast also does not rule out every nonlinear or temporal code.

### 3. Separate assembly uncertainty from source uncertainty

Use the existing exact/moment-Q references to isolate synthetic-sampling effects. Vary source subsets separately from pseudorow draws. Keep cells/bins from a source grouped in every split and resampling scheme. If assessing replication across recording groups, compare independently constructed panels; do not feed different neuron identities into an unchanged fixed-column decoder and call it transfer.

Resplitting already inspected observations estimates development sensitivity. It cannot restore a pristine confirmatory test. Reserve genuinely unexposed observations before adapting to them if a new confirmation is intended.

### 4. Let evidence guide representation and collection

Compare raw/regularized and PCA baselines with CEBRA using the same source-safe splits and endpoint-aware nulls. Predeclare the comparison family, stopping rule, and validation allocation; do not keep changing bins, targets, labels, or thresholds to find significance.

If additional recording is feasible, prioritize usable repetitions of relevant route alternatives within recordings and independent session replication. Large simultaneous195 recordings are not required for this condition-level study. Extra unmatched cells or synthetic rows need not improve the contrast. Estimate useful budgets with source-level reliability/learning curves and explicitly assumed injected-signal checks, rather than promise a universal minimum N.

## Decision criteria

- **Proceed:** a supported, interpretable contrast and sufficiently reproducible measurement justify a bounded representation comparison.
- **Redesign measurement:** semantics, clocks, recording-group provenance, class support, or nuisance balance prevent interpretation. Do not hide this with a larger network.
- **Report limited evidence:** a prespecified analysis remains weak/nonpositive. Preserve the result rather than claim that more data must rescue it.

The concrete project is **reliable endpoint-controlled prospective-path coding from pseudopopulations, with source-level uncertainty and independent-trial replication**. Exact same-trial population-state/dynamics claims remain a different, more demanding data contract. No new fitting, data expansion, or lab collection was performed to write this plan.
