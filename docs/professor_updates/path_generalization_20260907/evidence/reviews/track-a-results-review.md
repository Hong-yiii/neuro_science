minor — outputs/path-generalization-20260907/results-20260907T081200Z/track_a_v2/track_a_legacy_v9_cebra_metrics.csv:1 — replay table omits model-specific `C`/decoder-iteration metadata present in accepted legacy metrics.

Verified: accepted legacy `.../v9/v9_cebra_metrics.csv:1` has `C,decoder_n_iter`; TrackA replay header has neither. Similarly TrackA `track_a_legacy_v8b_head_metrics.csv:1` keeps `C` but drops legacy `n_iter`. Impact: final report cannot audit decoder iteration/C from TrackA replay tables alone. Minimum fix: cite accepted legacy metrics as authoritative metadata or add these columns to replay outputs.

## Scientific/numerical audit

Reviewed protocol: `/home/hongyi-home-lab/neuro_science-path-diagnosis/docs/reports/path-generalization-prefit-20260907.md`. Reviewed completed root only: `/home/hongyi-home-lab/neuro_science-path-diagnosis/outputs/path-generalization-20260907/results-20260907T081200Z/track_a_v2/`, plus accepted legacy V6–V9 artifacts under `/home/hongyi-home-lab/neuro_science/outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/`. Did not pool failed `track_a`.

Verified producer SHA: `outputs/path-generalization-20260907/frozen/driver_track_a_v2.py` = `340bd4fa14ee90b0a57cbc384785dff5be5936ab08146aee1e6620c0050d7bfb`.

Exact-Q support is as specified: `track_a_exact_validation_manifest.csv` has 30 product rows × 7 sessions = 210 lineage rows; absent/present products = 24/6; weights sum to 0.5 per class in `track_a_exact_validation_predictions.csv`.

Key tables:
- `track_a_exact_validation_metrics.csv`
- `track_a_exact_validation_predictions.csv`
- `track_a_legacy_v8b_head_metrics.csv`
- `track_a_legacy_v9_cebra_metrics.csv`
- `track_a_moment_pca_metrics.csv`
- `track_a_source_budget.csv`
- `track_a_relaxed40_source_controls.csv`
- `track_a_known_truth_simulations.csv`
- `track_a_leave_one_session.csv`
- `track_a_source_margins.csv`

Main results:
- Legacy replay parity succeeded: max old prediction diff V8b `9.10e-08`, V9 CEBRA `8.67e-08`.
- Exact-Q vs old validation changes are small, not transformative: V8b max BA diff `0.034`; V9 max BA diff `0.031`.
- Legacy V8b exact-Q mean BA `0.469`, range `0.250–0.771`; AUROC mean `0.395`, range `0–0.931`. Best PCA3 seed is a counterexample, not discovery.
- Legacy V9 CEBRA exact-Q mean BA `0.365`, range `0–0.583`; AUROC mean `0.283`, range `0–0.938`.
- Moment-exact ridge lambda1: BA `0.479`, AUROC `0.507`; lambda range BA `0.438–0.500`.
- Finite sampled ridge converges toward exact ridge: rows/class 16/64/256/1024 mean BA `0.475/0.481/0.480/0.480`; log-loss approaches `0.749`.
- Row-grid C policies are present: row-normalized C = `4,1,0.25,0.0625`; legacy C = `1`. Mean BA by row budget rises only `0.389→0.439` for legacy C and `0.389→0.425` for normalized C.
- PCA sensitivity is unstable: PCA3 can score high, PCA8/16 often inverted; PCA29 near chance. Do not treat latent dimension selection as neural evidence.
- Source-budget exact ridge: fractions 0.5/0.75/1.0 mean BA `0.444/0.471/0.479`, with 0.5 ranging `0.021–0.854`; source subset dominates.
- Relaxed40 real-session controls: raw_binned/raw_total/trial_index mean BA `0.465/0.447/0.413`; all have extreme per-session ranges `0–1`, consistent with tiny validation support.
- Leave-one-session block out is heterogeneous: BA range `0.333–0.833`; leaving out `20180810_session01` gives BA `0.833`, leaving out `20180912_session01` gives `0.333`.
- Gaussian oracle has 1800 simulation cases, not biological replications. Zero-signal true BA/AUROC exactly `0.5`, yet empirical-Q BA can be `0–1` with tiny validation; positive signal recovers true performance.

Hypotheses surviving:
- H1 survives as numerical-method diagnosis: finite synthetic sampling variance shrinks with rows.
- H2 survives only as representation/regularization sensitivity, not evidence for CEBRA/PCA neural discovery.
- H3 survives: source/session-conditioned relationships and margins vary enough to explain instability.
- H4 remains motivated, not proven: relaxed40 controls do not establish robust real-trial evidence.

Limitations: exploratory development only; original test permanently exposed; exact-Q rows are dependent product combinations, not independent trials; no raw/importer/split audit; no new fitting; accepted legacy artifacts trusted for provenance; pseudopopulation results cannot support simultaneous population-state claims.