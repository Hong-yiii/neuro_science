# Place195 source-trial split and behavior-QC audit

Date: 2026-08-30
Status: **exploratory split + train/validation behavior-QC audit; not H1 evidence**

## Purpose

Continue after the all-session importer/QC run by freezing a source-trial split
before any adaptive graph, route-family, PCA, CEBRA, decoder, or path-target
choice.

This does **not** resolve the scientific blockers: task-label semantics,
recording-group simultaneity, unit completeness, and authoritative path geometry
remain unverified.

## Inputs

Importer/QC run:

```text
outputs/prospective_path_first_run/place195-all-sessions-20260830-v4/
```

Important input hash carried forward:

```text
trials.csv sha256: aa0dc3e402a8a3c3c0fa355c0342f5061314f2c571d2f96dfaecc94e69fcd223
```

## Split freeze

Output:

```text
outputs/prospective_path_first_run/place195-splits-20260830-v3/
```

Command:

```sh
uv run python -m scripts.place195_split_and_behavior_audit freeze-splits \
  --import-dir outputs/prospective_path_first_run/place195-all-sessions-20260830-v4 \
  --output-dir outputs/prospective_path_first_run/place195-splits-20260830-v3
```

Split hash:

```text
11237c8c35af4b09b6d81c1994ff3f8b702d245d3a262f70413dab2b182973d1
```

Policy:

- unit: complete `source_trial_id`;
- scope: within session, using candidate same-session recording-group labels;
- block: contiguous 20-trial blocks to reduce adjacent-trial leakage;
- assignment: deterministic SHA-256 ranking of block IDs into 70/15/15
  train/validation/test by block;
- not used for assignment: neural activity, path samples, path metrics, graph
  labels, route labels, or verified start/goal labels.

Counts:

| Split | Trials | Success | Timeout |
| --- | ---: | ---: | ---: |
| train | 16,859 | 16,395 | 464 |
| validation | 3,401 | 3,309 | 92 |
| locked test | 3,641 | 3,496 | 145 |
| total | 23,901 | 23,200 | 701 |

The test split is locked for later use. Do not redesign graph granularity,
cleaning, exclusions, targets, metrics, or contrasts using test behavior.

## Train/validation behavior-QC audit

Output:

```text
outputs/prospective_path_first_run/place195-behavior-audit-20260830-v3/
```

Command:

```sh
uv run python -m scripts.place195_split_and_behavior_audit behavior-audit \
  --import-dir outputs/prospective_path_first_run/place195-all-sessions-20260830-v4 \
  --split-dir outputs/prospective_path_first_run/place195-splits-20260830-v3 \
  --output-dir outputs/prospective_path_first_run/place195-behavior-audit-20260830-v3
```

Artifacts:

| File | Rows | Role |
| --- | ---: | --- |
| `trial_behavior_qc_train_validation.csv` | 20,260 | per-trial raw Unity path summary for train/validation only |
| `support_by_session_split_train_validation.csv` | 116 | session x split support and path medians |
| `support_by_inferred_marker_pair_train_validation.csv` | 144 | provisional support by raw marker-pair fields |
| `qc_flags_train_validation.csv` | 3 | QC flags among train/validation trials |
| `behavior_audit_summary.json` | n/a | hashes, counts, guardrails, stop conditions |
| `decisions.md` | n/a | generated audit decision log |

QC flags in train/validation:

| QC flag | Trials |
| --- | ---: |
| `ripple_unity_nav_duration_discrepancy_gt_2s` | 20 |
| `ripple_eyelink_marker_mismatch` | 1 |
| `eyelink_nonmonotonic_trial_time` | 1 |

Behavior support notes:

- 20,260 train/validation trials were summarized.
- 3,641 locked test trials were not used for behavior/path metric outputs.
- In train/validation, 36 nonblank success rows exist in the provisional
  marker-pair support table for both train and validation.
- 167 train/validation rows had previous-trial-derived markers blanked because
  their previous source trial is locked test.
- 546 train/validation rows still have the same inferred start marker and current
  marker digit; this contradicts the prior-write-up expectation that start and
  goal differ, so these fields must stay labelled **unverified marker-derived
  fields** rather than real start/goal labels.

## Current stop boundary

The workflow can continue only to non-neural, train/validation behavior design
or metadata requests. It must stop before H1 modeling until:

1. marker-to-cue/start/goal semantics are lab-confirmed;
2. recording groups and unit completeness are lab-confirmed;
3. authoritative maze geometry/adjacency or a reviewed position-to-node mapping
   exists;
4. QC inclusion/exclusion rules are frozen without using test behavior;
5. start-goal baselines and nulls are specified with verified labels.

## Code added

- `scripts/place195_split_and_behavior_audit.py`
- `scripts/test_place195_split_and_behavior_audit.py`
- `scripts/__init__.py`

Validation:

```sh
uv run python -m unittest scripts/test_import_place195_sessions.py scripts/test_place195_split_and_behavior_audit.py
# 12 tests passed
```
