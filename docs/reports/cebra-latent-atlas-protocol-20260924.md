# Saved CEBRA latent atlas — frozen exploratory protocol

Prepared 2026-09-24 before computing new geometry metrics. Implements the first stage of the [September 23 review](cebra-latent-geometry-review-20260923.md), authorized by Hongyi's “can you execute this?”. This is **exploratory descriptive analysis**, not confirmation, new CEBRA training, or the separate matched-PCA experiment.

## Question and selection

How much of the saved representation does a 3D view retain, and which condition-level geometry is stable across training/development observations and saved seeds? The independent biological sources remain original trials nested in sessions. Points are synthetic population rows or their cue bins, not independent real simultaneous population states.

Freeze all seeds 0,1,2 of:

- Endpoint `02-cebra/positive_bin_t03` at 250 and 3000 steps; `time_t1` at 250 and 1000; `behavior_t03` at 250. Fifteen saved embedding objects, selected in the previous review, not by new pictures.
- Accepted V9 `cebra_time` and `cebra_behavior`, dimensions 3 and 8, final checkpoints, all three seeds. Twelve objects; retain their nonpositive path results.
- Matching raw-bin and saved PCA8/bin references for both lanes. **Pre-execution correction from producer inspection:** these implementations fit one PCA to all pooled training cue bins, not separate bases per bin. Bin-space views are therefore valid. Endpoint PCA features are saved numerically in the original baseline decoder NPZ; use its original C=1 readout and explicitly distinguish it from the later C=.01 result. V7/V8 PCA saves float32 directions and input scaler, not PCA's residual standardized-input center: apply those saved directions and recenter using training only, label the result a reconstructed geometry reference rather than bitwise model replay. Centering does not change pairwise distances; rounding limits exact parity.

Optional augmentation, later Track B, hybrid, new dimension sweeps, intrinsic-dimension estimation, persistent cohomology and new null fits are deferred. No original-test, raw lab, extra cells or lab-server access. Never execute checkpoint/pickle loading or fitting entry points. Numeric NPZ loads use `allow_pickle=False`; saved PCA forward transforms are permitted, and new **display-only** PCA is fitted on training data only.

## Inputs and provenance gates

Preserve current files/branch and accepted outputs. Record input hashes, producing receipts, exact code/dirty state, runtime/packages, shapes, configuration and exclusions. Check source-split separation, row/class correspondence, ten-bin order, session block coverage, finite data and saved normalized latent norms. Reuse original artifact verifiers and trace producers. Stop on contradictory metadata; do not infer labels from filenames/shape. Historical source/test exposure remains permanent.

## Display

- Separate training and development panels with shared coordinates and scale within one run. E=3 CEBRA uses native coordinates; E>3 uses pooled training-bin PCA. Whole-cue views use one row and a training-only display PCA of flattened features. Raw references are training-standardized per cell for display; label that transformation explicitly.
- Recolor fixed coordinates by categorical start/goal/pair or path presence, cue bin, and available source-reuse diagnostics. No fictitious single-session label for a multi-session pseudorow. No missing-gaze coloring or inferred nuisance labels.
- Show point clouds plus condition centroids; centroids do not replace dispersion. Optional lines link only bins of one explicitly selected synthetic row. Never link independent rows or call synthetic cue sequences real neural dynamics.
- Include fixed first-coordinate pair views and static overview/spectrum panels. Use all selected seeds; do not align by choosing an attractive rotation. Browser rotation is navigation, not an estimator.
- Offline HTML, no external runtime/CDN or new web service. Include accessible controls, explanatory text and static fallback.

## Descriptive metrics (no p-values or confidence intervals)

1. Full-space centered spectrum, participation ratio and unit-norm diagnostics, separately for bin space and whole-cue feature space. Development spectrum is a separate descriptive estimate, not a training-fitted projection.
2. Display variance/energy retention: squared projected energy divided by total energy **relative to the training center**, for each split. Native E=3 retains all dimensions. A low number means the view is incomplete, not lack of information.
3. Projection fidelity: Euclidean distances in the declared representation (chord distances for normalized latents), versus displayed distances; Spearman correlation and mean k=10 neighbor overlap. Use deterministic balanced sampling of up to 64 synthetic rows, retaining all bins; exclude comparisons between bins of the same row. These rows may still reuse biological sources: scores are visualization diagnostics only. Report undefined/degenerate cases, ties and actual sample counts. Sampling RNG seed 20260924.
4. Condition geometry: distances among matching condition centroids in each cue bin (pooled as within-bin distances), or whole-cue centroids. Spearman correlation between train/development and between saved seeds on corresponding conditions. At least three conditions required; V9's binary target therefore does not support the same condition-RDM stability statistic. No fitted alignment, CCA or test-fitted rotation. Cross-seed variation changes assembly and/or optimization and is not independent-session replication.
5. Show existing whole-cue decoder metrics without fitting or choosing new readouts. Endpoint accuracy and path balanced accuracy remain different tasks. Report source reuse/unique-source support, not uncertainty derived from the point count.

No geometry–path association test or topology null is added in this pass. The endpoint data do not supply the same within-endpoint path contrast as V9; neither a supervised cluster nor a positive RDM correlation establishes H1a/H1b. Time omits labels in its objective but existing assemblies were label-conditioned. Endpoint Time τ=1 vs selected Behavior τ=.3 is not an objective-only ablation.

## Checks and finish

Use synthetic tests for training-only projection, bin/row ordering, degeneracy, distance invariance, identity-projection fidelity and rejected corrupt labels/shapes. Run source artifact verification, targeted LSP/tests, offline browser checks and independent code/scientific review before interpreting the new metrics. Save projections and machine-readable metrics for forward verification without new model fitting. Retain failed attempts separately, document deviations, and report unfavorable results. No automatic commit, publication or PR was requested.
