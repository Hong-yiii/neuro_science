# Phase-1 failed smoke attempt

Status: preserved own smoke failure; no biological arrays or importer/split tables were accessed.

Command:

```sh
/home/hongyi-home-lab/neuro_science/scratch/v6-v9-runtime/bin/python -m scripts.place195_path_generalization_phase1 smoke --output-dir outputs/path-generalization-20260907/phase1_synthetic_smoke
```

Failure caught before any biological execution:

```text
ValueError: shape mismatch in gaussian_source_fixture: block_mean had flattened shape (4,) while numpy normal size was (2, 2)
```

Fix: reshape session-block mean to `(len(cidx), n_bins)` before synthetic draw. Follow-up unit tests and synthetic smoke passed.
