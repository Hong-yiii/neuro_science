## Files Retrieved

- `/home/hongyi-home-lab/neuro_science-path-diagnosis/AGENTS.md:1-116` — project rules, H1/pseudopopulation cautions, alignment context.
- `/home/hongyi-home-lab/neuro_science-path-diagnosis/README.md:1-38` — accepted V6–V9 run root and low-result context.
- `/home/hongyi-home-lab/neuro_science-path-diagnosis/docs/reports/place195-audit-and-next-steps-20260907.md:1-86` — audit order, accepted final CEBRA dir, non-pseudopop alternatives.
- `/home/hongyi-home-lab/neuro_science-path-diagnosis/docs/analysis-contract.md:1-180` — required trial/tensor/path fields and simultaneity constraints.
- `/home/hongyi-home-lab/neuro_science-path-diagnosis/scripts/place195_v7_v8_neural_experiments.py:109-338,438-516` — source tensor build, masks, pseudopop assembly, source shuffle.
- `/home/hongyi-home-lab/neuro_science-path-diagnosis/scripts/place195_v8b_v9_cebra.py:110-219` — saved-array CEBRA/comparator seams.
- `/home/hongyi-home-lab/neuro_science-path-diagnosis/scripts/place195_split_filtered_access.py:69-155` — source-safe split-gated reader seam.
- Allowed local artifacts under `/home/hongyi-home-lab/neuro_science/outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/` — schemas/metrics only; no raw/importer/split-table access.

## Key Code

```py
# v7/v8 source tensors
X = np.full((len(source_ids), len(cell_ids), n_bins), np.nan)
M = np.zeros((len(source_ids), len(cell_ids)), dtype=bool)
# off-session cells remain unavailable, not zero
if session_from_cell(cid) == meta.session_id and not M[si, ci]: raise RuntimeError
```

```py
# pseudopop assembly
sid = rng.choice(by_session[sess])
cidx = np.where(cell_sessions == sess)[0]
X[r, cidx, :] = Xsrc[si, cidx, :]
if np.isnan(X[r]).any(): raise RuntimeError("refusing imputation")
```

## Architecture

Entry: accepted run root is `.../place195-v6-v9-autoresearch-20260906/`; final V9 dir is `v8b-v9-cebra-final-20260905T224554Z`.

Core flow:
1. V6 behavior/support artifacts define selected endpoint/component: `endpoint_pair=4->3`, `selected_component_id=D_N_R_T__N_R_M`.
2. V6 membership files map `source_trial_id/session_id/split/component_status/cell_ids`.
3. V7/V8 reads split-gated cue events/counts via `SplitFilteredAccess`, bins cue spikes into source-level tensors, records `observed_source_cell_mask`, then assembles label-conditioned pseudopop rows.
4. V8b/V9 uses saved V7/V8 `source_level_cue_tensors.npz` and `pseudo_arrays_seed*.npz`; final CEBRA policy says “no raw/test access; source_level_cue_tensors.npz and pseudo_arrays_seed*.npz only”.

Saved development source-level cue tensors found:
- `v7-v8-neural-experiments/primary29_min3train_min1val/bin50ms|bin100ms|bin200ms/source_level_cue_tensors.npz`
  - shapes: `(104,29,20)`, `(104,29,10)`, `(104,29,5)`
  - counts: train present 52, train absent 30, validation present 10, validation absent 12; 7 sessions; observed mask `423/3016` at 100 ms.
- `v7-v8-neural-experiments/relaxed40_min2train_min1val/bin50ms|bin100ms|bin200ms/source_level_cue_tensors.npz`
  - shapes: `(146,40,20)`, `(146,40,10)`, `(146,40,5)`
  - counts: train present 76, train absent 38, validation present 16, validation absent 16; 11 sessions; observed mask `543/5840` at 100 ms.
- `v7-v8-neural-experiments/strict6_min3train_min2val/bin50ms|bin100ms|bin200ms/source_level_cue_tensors.npz`
  - shapes: `(11,6,20)`, `(11,6,10)`, `(11,6,5)`
  - counts: train present 3, train absent 3, validation present 2, validation absent 3; 1 session; observed mask `66/66`.

NPZ schema: `X_source_cell_bin`, `exposure_source_bin`, `observed_source_cell_mask`, `source_trial_ids`, `source_session_ids`, `source_splits`, `source_labels`, `cell_ids`, `bin_width_s`.

V6 development-only membership/behavior artifacts:
- `v6-reset-graph-support-audit/v6c_population_membership/selected_component_source_membership.csv`
  - 660 rows; columns include `source_trial_id`, `session_id`, `split`, `endpoint_pair`, `selected_component_id`, `component_status`, `complete_directed_path_coverage`, `route_signature`, `observed_cells_for_source_trial`, `cell_ids`.
- `v6-reset-graph-support-audit/v6c_population_membership/selected_component_condition_mean_source_membership.csv`
  - 621 rows; per-cell source support by split/status.
- `v6-reset-graph-support-audit/v6b_component_support/component_endpoint_session_split_support.csv`
  - 488,674 rows; component/session/split/status trial counts.
- `v6-reset-graph-support-audit/v6a_geometry_mapping/trial_mapping_metrics.csv`
  - 19,162 rows; has `start`, `goal`, `endpoint_pair`, `route_signature`, `middle_directed_components`, QC/coverage fields.

Nearest tests:
- `scripts/test_place195_split_filtered_access.py:13-50` — test split cannot leak through development access.
- `scripts/test_place195_v7_v8_neural_experiments.py:15-61` — bin conservation, session/split-preserving shuffle, one-source-per-session pseudopop assembly.
- `scripts/test_place195_v8b_v9_cebra.py:21-86` — CEBRA flatten/loader/manifest/parity smoke tests.

## Findings

1. **high: CEBRA low results are consistent with overfit + weak independent support, not a proven absence of path information.** Final V9 train BA is 1.0 for both CEBRA variants/dims, but validation medians are below/near chance: behavior dim3 median 0.28125, behavior dim8 0.421875, time dim3 0.429688, time dim8 0.4375. Null p-values: behavior `p=0.619`, time `p=0.857`.
2. **high: primary CEBRA operates on synthetic condition-level rows, not real simultaneous population trials.** Primary source tensor has 29 cells across 7 sessions, only 104 source trials; pseudopop rows are assembled by known label and session block.
3. **medium: strict6 is real same-session support but tiny.** Strict panel is fully observed (`66/66`) but only 11 source trials from one session; useful for smoke/audit, not robust H1.
4. **medium: relaxed40 widens cells/sessions without new raw access.** Existing saved tensors already support wider endpoint/cell support checks inside accepted artifacts, but mask density is low (`543/5840` observed source-cell entries at 100 ms).
5. **medium: confound fields are partial in saved tensors.** Source tensors retain `session`, `split`, label/status, cell ordering and exposure; endpoint/start/goal live in V6 CSVs, not in NPZ. Candidate recording group/simultaneity is only a code seam from split metadata, not present in saved NPZ.

## Unknowns / Stop Reason

- Did not inspect original importer, raw data, or split tables by instruction.
- Did not inspect locked test rows or compute new scientific results.
- Simultaneous recording group validity remains unresolved from saved artifacts alone.
- Cue/stimulus identity, gaze/action/view/heading confounds are not present in saved NPZ tensors.

## Start Here

Start with `/home/hongyi-home-lab/neuro_science/outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/v7-v8-neural-experiments/primary29_min3train_min1val/bin100ms/source_level_cue_tensors.npz`: it is the smallest accepted source-level seam behind V8b/V9 and exposes masks, source IDs, labels, sessions, cell order, and exposure.