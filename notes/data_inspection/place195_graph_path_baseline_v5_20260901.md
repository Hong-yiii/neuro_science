# place195 graph-path baseline receipt

Date: 2026-09-01
Status: exploratory_graph_path_condition_matched_pseudopop_baseline_not_h1_evidence

## Inputs

- import dir: `outputs/prospective_path_first_run/place195-all-sessions-20260830-v4`
- split dir: `outputs/prospective_path_first_run/place195-splits-20260830-v3`
- geometry: `docs/geometry/maze_mesh_centroids_1344.txt`
- output dir: `outputs/prospective_path_first_run/place195-graph-path-baseline-20260901-v5`

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
  "pseudopopulation_rows": 908,
  "pseudopopulation_train_rows": 525,
  "pseudopopulation_validation_rows": 383,
  "train_trials": 15947,
  "trials_collapsed_to_other": 5179,
  "validation_trials": 3215
}
```

## Commands

```sh
uv run python -m unittest scripts.test_import_place195_sessions scripts.test_place195_split_and_behavior_audit scripts.test_place195_graph_path_baseline docs.cebra_pilot.implementation.tests.test_framework
uv run python -m scripts.place195_graph_path_baseline run --import-dir outputs/prospective_path_first_run/place195-all-sessions-20260830-v4 --split-dir outputs/prospective_path_first_run/place195-splits-20260830-v3 --geometry docs/geometry/maze_mesh_centroids_1344.txt --output-dir outputs/prospective_path_first_run/place195-graph-path-baseline-20260901-v5 --receipt notes/data_inspection/place195_graph_path_baseline_v5_20260901.md --min-train 5 --min-validation 2
# post-run: artifact hashes recomputed; supportable_training_table.csv, condition_pseudopopulation_rows.csv, and validation_predictions.csv checked for zero test rows
```

## Validation

```json
{
  "baseline": {
    "model": "pseudopop_start_goal_majority",
    "validation_accuracy": 0.0783289817232376,
    "validation_classes": 383,
    "validation_macro_class_accuracy": 0.0783289817232376,
    "validation_macro_start_goal_accuracy": 0.08245946591534828,
    "validation_rows": 383,
    "validation_start_goal_pairs": 30
  },
  "condition_matched_pseudopop_nearest_centroid": {
    "model": "condition_matched_pseudopop_nearest_centroid_within_start_goal",
    "validation_accuracy": 0.04177545691906005,
    "validation_classes": 383,
    "validation_macro_class_accuracy": 0.04177545691906005,
    "validation_macro_start_goal_accuracy": 0.04461880711880712,
    "validation_mean_overlap_cells_when_supported": 9.170491803278688,
    "validation_min_overlap_cells_when_supported": 5,
    "validation_rows": 383,
    "validation_start_goal_pairs": 30,
    "validation_supported_rows": 305,
    "validation_unsupported_rows": 78
  },
  "pseudopop_coverage": {
    "features": 195,
    "imputation_policy": "none; missing cells stay masked and distances use overlap only",
    "missing_entries": 131520,
    "missing_fraction": 0.7427990511690952,
    "normalization_policy": "per-cell mean/std fit on observed train pseudopop values only",
    "observed_entries": 45540,
    "observed_fraction": 0.2572009488309048,
    "rows": 908
  }
}
```

## Decision log

- V5 replaces the trial-wise imputed baseline with condition-matched pseudopopulation rows.
- Missing cells stay masked; the neural distance uses overlapping observed cells only.
- This remains a cross-session pseudopopulation, not a simultaneous 195-cell population.
- Marker semantics and simultaneous-population metadata remain unverified.
- Locked test is still untouched for final evaluation.
