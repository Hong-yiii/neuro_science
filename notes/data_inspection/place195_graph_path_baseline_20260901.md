# place195 graph-path baseline receipt

Date: 2026-09-01
Status: exploratory_graph_path_and_imputed_selected_cell_baseline_not_h1_evidence

## Inputs

- import dir: `outputs/prospective_path_first_run/place195-all-sessions-20260830-v4`
- split dir: `outputs/prospective_path_first_run/place195-splits-20260830-v3`
- geometry: `docs/geometry/maze_mesh_centroids_1344.txt`
- output dir: `outputs/prospective_path_first_run/place195-graph-path-baseline-20260901-v4`

## Graph/path rule

- graph schema: `maze_graph_1344_4neighbor_v1`
- script graph hash: `f83908e027012e49f1be2396bb0f7aeb514b807c43b6e703625a40647a3738a0`
- pinned receipt graph hash: `1e7804c5d2167dcd8709a9760d8917034cb60e36e936229fad9056b1dae0f9ad`
- mapping tolerance: `0.4419417382415922`
- no interpolation; split at invalid/unmapped and nonadjacent transitions; collapse repeats.
- exploratory route family: fixed 5x5 graph-node signature.

## Main counts

```json
{
  "coarse5_signatures": 3878,
  "endpoint_labelled_train_validation_trials": 19162,
  "fine_signatures": 18068,
  "train_trials": 15947,
  "trials_collapsed_to_other": 5179,
  "validation_trials": 3215
}
```

## Commands

```sh
uv run python -m unittest scripts.test_import_place195_sessions scripts.test_place195_split_and_behavior_audit scripts.test_place195_graph_path_baseline docs.cebra_pilot.implementation.tests.test_framework
uv run python -m scripts.place195_graph_path_baseline run --import-dir outputs/prospective_path_first_run/place195-all-sessions-20260830-v4 --split-dir outputs/prospective_path_first_run/place195-splits-20260830-v3 --geometry docs/geometry/maze_mesh_centroids_1344.txt --output-dir outputs/prospective_path_first_run/place195-graph-path-baseline-20260901-v4 --receipt notes/data_inspection/place195_graph_path_baseline_20260901.md --min-train 5 --min-validation 2
# post-run: artifact hashes recomputed; supportable_training_table.csv and validation_predictions.csv checked for zero test rows
```

## Validation

```json
{
  "baseline": {
    "model": "start_goal_majority",
    "validation_accuracy": 0.39097978227060654,
    "validation_classes": 383,
    "validation_macro_class_accuracy": 0.0783289817232376,
    "validation_macro_start_goal_accuracy": 0.39159772388335745,
    "validation_rows": 3215,
    "validation_start_goal_pairs": 30
  },
  "imputation_burden": {
    "features": 195,
    "imputed_entries": 3672539,
    "imputed_fraction": 0.982858435097241,
    "observed_entries": 64051,
    "rows": 19162,
    "train_fit_policy": "observed train marginal mean per cell, represented as zero after train z-scoring"
  },
  "imputed_neural_nearest_centroid": {
    "model": "imputed_cue_counts_nearest_centroid_within_start_goal",
    "validation_accuracy": 0.223950233281493,
    "validation_classes": 383,
    "validation_macro_class_accuracy": 0.08347794157990433,
    "validation_macro_start_goal_accuracy": 0.2236392699791372,
    "validation_rows": 3215,
    "validation_start_goal_pairs": 30
  }
}
```

## Decision log

- Imputation was used only for the exploratory selected-cell cue baseline.
- The imputed baseline is not primary evidence because most global trial×cell entries are structurally missing.
- Marker semantics and simultaneous-population metadata remain unverified.
- Locked test is still untouched for final evaluation.
