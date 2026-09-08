blocker — scripts/place195_path_generalization_phase1.py:2668 — Track A gated runner is ridge-only but reports `status: complete`.

Verified: `run_track_a_gated` loads accepted V7 tensors, enumerates exact validation, loops only over `args.ridge_lambdas`, writes `track_a_exact_validation_metrics.csv`, then marks complete at lines 2668-2726. It does not replay the 12 accepted CEBRA checkpoints, replay saved raw/PCA C=1 heads, run finite rows/class sampling arms, raw-total/raw-binned/PCA3/8/16/29 references, source-budget checks, margin/leave-one-session diagnostics, or 100-seed Gaussian oracle/trace controls required by the protocol. Impact: biological execution would silently skip most Track A acceptance stages. Minimum fix: implement those stages or fail/mark incomplete until present.

blocker — scripts/place195_path_generalization_phase1.py:2737 — Track B null family is not implemented as null permutations.

Verified: `cebra_config_manifest` claims `null_permutations: 20` and `expected_null_fit_count: 280` at lines 1059-1068, but `run_track_b_gated --null-family-only` uses only `null_family_cebra_specs(permutation_index=0)` at lines 2737-2740. The subsequent `build_dataset(...)` call at lines 2760-2768 never passes `shuffled_labels`. Impact: it runs one unpermuted 14-config family, not the 20 full-pipeline source-label permutations needed for the 14-family-max null. Minimum fix: generate 20 stratified label permutations, pass them into dataset assembly/scalers/encoder/head, and aggregate family-max BA/p-values.

blocker — scripts/place195_path_generalization_phase1.py:1271 — Track B evaluates sampled pseudo-validation rows, not exact empirical-Q validation.

Verified: CEBRA metrics use `yva/pva` from `arrays["validation"]` at lines 1189-1190 and 1271-1284. Those arrays are built by `build_dataset(... rows_per_class=spec.rows_per_class, seed=spec.assembly_seed)` at lines 2760-2768. Impact: row-count arms change validation support and evaluation noise; null/observed BA is not the required exact class-balanced validation Q. Minimum fix: train on sampled training rows, but evaluate every fitted encoder/head on the exact validation product with 0.5/0.5 class weights.

major — scripts/place195_path_generalization_phase1.py:1253 — 5000-update prefix parity cannot be verified for biological Track B runs.

Verified: checkpoints are saved only at `{1,250,500,750,spec.updates}` at lines 1250-1256, so a 5000-step run lacks a step-1000 checkpoint. The only prefix comparison is synthetic-only `cebra_prefix_parity_smoke`, not used in `run_track_b_gated`. Impact: required 1000/5000 prefix equivalence is not auditable after biological execution. Minimum fix: save step 1000 for long runs and compare long-run first-1000 losses/weights or embeddings to the matched short run.

major — scripts/place195_path_generalization_phase1.py:2809 — Track C null inference is incomplete and can report complete.

Verified: `fit-track-c-models` defaults `--nulls 0`; for `target_mode != both`, lines 2848-2869 ignore `args.nulls` entirely. For `both`, lines 2317-2421 write null metric rows only; there is no 100-default source shuffle, no 100 temporal-half sensitivity using `add_training_temporal_halves`, and no p-value/exceedance calculation. Impact: Track C could output observed model scores without the required null family. Minimum fix: require/execute the declared nulls, include temporal-stratum sensitivity, compute family p-values, or mark inference incomplete.

major — scripts/place195_path_generalization_phase1.py:2769 — Track B resume safety reuses stale fits based only on spec hash.

Verified: fit directories are named from `stable_hash(spec.as_dict())`, and existing `fit_info.json` is accepted if `fit_spec_hash` matches at lines 2769-2775. The reuse check does not verify source NPZ hash, config hash, manifest/source lineage hash, scaler input hash, or code hash. Impact: reruns can silently mix stale fits with changed inputs/code/config. Minimum fix: include and verify source/config/code/input-manifest hashes in each fit identity and resume check.

Review metadata:
- Code hash at review: `91954431d4cbbd94179ddb2b0907a6f0da7107ab8eb3994438ad06cc66e591c0`
- Test hash: `e77f3068170127b33cbdc150399c02e85cad85a84dbf7a7ec9fd9eadfa45a8fb`
- Protocol hash: `27f8181586dae1093441bbcc9dd7eb0b7117a4c799d1b72af3a000f9597290e9`
- Base HEAD: `a9d8dac`
- Unit tests passed: 17/17.

Grades:
- Content success: not successful for biological gate; several declared stages are missing.
- Operational success: synthetic/unit tests pass, but they do not cover the missing gated stages.
- Instruction compliance: review stayed read-only; no biological fits or raw/importer tables accessed.

Residual risks: I did not execute CEBRA smoke or inspect raw biological artifacts; findings are from static code review plus CPU unit tests.