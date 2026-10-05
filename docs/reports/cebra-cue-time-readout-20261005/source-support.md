# Source support and lineage: CEBRA cue-time readout

**Prepared:** 2026-10-05 SGT. This is the no-fit source/provenance artifact for `scripts/cebra_cue_time_readout.py`. It traces existing saved numeric arrays and accepted manifests only; it does not execute old raw-data audit CLIs and does not read lab recording files.

## Artifact chain

```text
source ledger / source tensor
  -> fixed historical train/validation split
  -> accepted source-coherent null label worlds
  -> per-world/per-seed session-block pseudorow draws
  -> row-level lineage manifests
  -> saved cue phase arrays and accepted transforms
  -> single-bin readout inputs after approval
```

Authority paths:

- source tensor: `outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/v7-v8-neural-experiments/primary29_min3train_min1val/bin100ms/source_level_cue_tensors.npz`
- accepted source/manifold run: `outputs/cebra-full-trial-transfer-20260924/biological-run-20260924T162913Z/`
- new preparation outputs: `outputs/cebra-cue-time-readout-20261005/preparation/`

## Source tensor support

Saved tensor shapes and support:

| Field | Value |
| --- | ---: |
| sources | 104 |
| cells | 29 |
| cue bins | 10 |
| exposure shape | 104 × 10 |
| observed source-cell mask | 104 × 29 |
| train sources | 82 |
| historical-validation sources | 22 |
| train absent/present | 30 / 52 |
| validation absent/present | 12 / 10 |
| source labels total absent/present | 42 / 62 |

Measured-count and exposure validity gate:

- observed-cell counts are finite and nonnegative; observed count range: 0 to 8 spikes/bin;
- source-bin exposures are finite and positive;
- minimum exposure is `0.09903399646282196 s` at `20180810_session01_trial090`, bin 9; this is the known clipped cue bin and is retained as valid shorter exposure;
- maximum exposure is `0.10000000149011612 s`;
- saved source-cell mask must match session membership (`session_from_cell(cell_id) == source_session_id`);
- unobserved cells are never materialized as zeros in pseudorows; every assembled row requires all session-block cells to be observed.

## Fixed split and pseudorow lineage

The accepted run uses source-complete train/validation separation. For observed seed 0:

| Split | Pseudorows | Manifest rows | Class rows | Unique sources used |
| --- | ---: | ---: | --- | ---: |
| train | 128 | 896 | 64 absent / 64 present | 82 |
| validation | 30 | 210 | 24 absent / 6 present | 22 |

Each pseudorow has seven session blocks. A row's `sources` map is the row-level lineage; all cells and bins for a session block come from the chosen source trial for that session. Row IDs are class-qualified (`validation:absent:product00000`, not a class-local number alone), preventing the old product-row merge bug.

### Worked training row

Observed world, seed 0, first training row:

```text
row_id: train:absent:sample00000
label: absent
row_kind: sampled
sources:
  20180705_session01 -> 20180705_session01_trial375
  20180730_session01 -> 20180730_session01_trial010
  20180731_session01 -> 20180731_session01_trial242
  20180810_session01 -> 20180810_session01_trial133
  20180912_session01 -> 20180912_session01_trial232
  20180920_session01 -> 20180920_session01_trial053
  20181022_session01 -> 20181022_session01_trial118
```

For each of the seven session entries, only the 29-unit columns whose cell IDs belong to that session are filled from that source's ten cue bins; all other session blocks are filled by their own listed sources. If any required block is missing, materialization stops rather than filling zero.

### Worked validation row

Observed world, seed 0, first validation row:

```text
row_id: validation:absent:product00000
manifest_key: absent|0
label: absent
row_kind: product
sources:
  20180705_session01 -> 20180705_session01_trial212
  20180730_session01 -> 20180730_session01_trial230
  20180731_session01 -> 20180731_session01_trial351
  20180810_session01 -> 20180810_session01_trial053
  20180912_session01 -> 20180912_session01_trial157
  20180920_session01 -> 20180920_session01_trial158
  20181022_session01 -> 20181022_session01_trial065
```

Validation rows are the exact product of per-session source pools within class. The resulting 24 absent and 6 present rows are balanced by exact class weights during metric calculation, not by pretending there are equal row counts.

## Validation support and singleton limits

Observed seed0 validation support by class/session:

| Label | Session | Sources |
| --- | --- | ---: |
| absent | 20180705_session01 | 1 |
| absent | 20180730_session01 | 2 |
| absent | 20180731_session01 | 1 |
| absent | 20180810_session01 | 3 |
| absent | 20180912_session01 | 1 |
| absent | 20180920_session01 | 2 |
| absent | 20181022_session01 | 2 |
| present | 20180705_session01 | 1 |
| present | 20180730_session01 | 1 |
| present | 20180731_session01 | 3 |
| present | 20180810_session01 | 2 |
| present | 20180912_session01 | 1 |
| present | 20180920_session01 | 1 |
| present | 20181022_session01 | 1 |

Several session×class pools are singletons. Delete-one-source sensitivity therefore has inestimable cases when a class loses support; those are retained and labelled, not dropped. Future independent folds are limited by these singleton cells and by reuse of the historically exposed validation source pool. More folds cannot be claimed without new source-support design and review.

## Null worlds and source reuse

The study reuses all 20 saved source-coherent null worlds and all three accepted seeds. Null labels are source-level maps before assembly; cue/navigation/source identities remain coherent within each null world. For each world/seed, training manifests contain 128 pseudorows × 7 session blocks and validation manifests contain 30 pseudorows × 7 session blocks.

The no-fit audit verifies:

- exactly 21 worlds (observed + 20 nulls);
- seed directories `seed0`, `seed1`, `seed2` in every world;
- no train/validation source overlap in every world/seed manifest;
- exact validation class-qualified row IDs;
- expected new fit/replay counts: 5040 single-bin readouts and 504 saved whole-cue replays.

## Phase arrays and feature views

The source tensor stores cue activity as source × cell × bin. The accepted run materializes pseudorows as row × cell × bin before transforms.

Feature-order contract:

- raw whole cue: `row × cell × bin` flattened cell-major to 290 features; bin `b` is recovered as `reshape(n, 29, 10)[:, :, b]`;
- PCA/CEBRA whole cue: `row × bin × coord` flattened bin-major to 80 features; bin `b` is recovered as `reshape(n, 10, 8)[:, b, :]`.

A regression test covers this contrast so a bin extraction bug cannot silently swap raw/PCA ordering. Whole-cue ordering remains byte-compatible with the accepted readout states.

## Claim limits

These rows are condition-level, label-conditioned pseudopopulations. They are not simultaneous natural trials, not a pristine test set, and not an operational unknown-label predictor. Seeds are computational repeats; pseudorows share sources. The assay can describe whether frozen representations expose the fixed path-component label to simple readouts at each cue bin, under source-coherent nulls and source-pool sensitivity. It cannot establish exact trial-specific population state, biological mechanism, intention, full ordered-path prediction or H1 confirmation by itself.
