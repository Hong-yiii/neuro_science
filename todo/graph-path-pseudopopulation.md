# Todo — Graph Path And Fixed-195 Pseudopopulation

Status: next workflow before PCA/CEBRA

## Done / pinned

- [x] Treat geometry file as authoritative: `docs/geometry/maze_mesh_centroids_1344.txt`.
- [x] Hash geometry file: `479f0df501e92e167206248eff2d0a44ba5f26cd62cfcc879dcaad979d7a7e66`.
- [x] Build/hash fine 4-neighbor graph: `1e7804c5d2167dcd8709a9760d8917034cb60e36e936229fad9056b1dae0f9ad`.
- [x] Use success-only trials for the experiment; drop timeout trials from analysis for now.
- [x] Probe marker semantics against Unity starts/ends: `notes/data_inspection/place195_marker_semantics_probe_20260901.md`.
- [x] Document graph/path formalization: `docs/graph-path-formalization.md`.
- [x] Add visual similarity examples: `docs/graph-path-similarity-examples.html`.
- [x] Check full-195 support under current split: not supported without imputation; see `notes/data_inspection/fixed195_pseudopop_support_probe_20260901.md`.
- [x] Choose primary cue feature approach: 100 ms cue-time bins, with total-count collapse and rate/exposure sensitivity later.

## Next: behavior-only audit

- [x] Build the fine graph from `docs/geometry/maze_mesh_centroids_1344.txt`.
- [x] Validate 4-neighbor adjacency and record graph hash.
- [x] Use only train/validation successful trials for route-design decisions.
- [x] Use `success_after_success` when a clean inferred `(start, goal)` label is required.
- [x] Map native Unity paths to nearest graph nodes with the documented tolerance.
- [x] Plot sample mapped paths by source trial and by provisional `(start, goal)`.
- [x] Produce raw mapped paths, cleaned segments, directed edge sequences, and exact signatures.
- [x] Count exact route signatures before trying clustering.
- [x] Build support tables for:
  - old-style `(start, goal)` pseudopopulation baseline;
  - fixed-195 `(start, goal, route_family)` pseudopopulation;
  - smaller support-declared pseudopopulations if full 195 fails;
  - cross-condition shared-edge/middle-segment contrasts.
- [x] Decide whether all 195 cells are supportable without imputation under current split: no.
- [x] Freeze exploratory model route-family vocabulary from train support only; final route families remain review-gated.
- [x] Get independent review before PCA; reviewer accepted as somewhat validated exploratory output.

Receipt: `notes/data_inspection/place195_graph_path_baseline_20260901.md`. Output: `outputs/prospective_path_first_run/place195-graph-path-baseline-20260901-v4/`.

## Current exploratory neural baseline

- [x] Fit total-cue-count selected-cell nearest-centroid baseline with train-fit marginal imputation.
- [x] Validate against start-goal majority baseline on validation only.
- [x] Record imputation burden: 98.29% of global trial × 195-cell entries imputed.
- [x] Keep claim ceiling: exploratory only, not H1 evidence.

## Later: neural baselines

- [ ] Build 100 ms cue-bin pseudopopulation features.
- [ ] Fit raw time-binned decoder/baseline.
- [ ] Fit train-only PCA and same decoder.
- [ ] Compare against total-count collapse baseline.
- [ ] Use exposure-normalized rates as sensitivity if cue-bin exposure varies.
- [ ] Do not run CEBRA until raw/PCA and support audits pass.
