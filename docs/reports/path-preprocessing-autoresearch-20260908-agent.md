# Agent handoff — completed path-preprocessing autoresearch

2026-09-08. **Complete exploratory study; no further fitting is queued or authorized by this handoff.** Read the [human report](path-preprocessing-autoresearch-20260908.md), [offline illustrated HTML](path-preprocessing-autoresearch-20260908.html), and [readable frozen methods](path-preprocessing-prefit-20260908.md).

## Outcome, without promotion

- Source-safe, condition-level pseudopopulation assay; not unknown-label natural-trial decoding, simultaneity, intention, dynamics or mechanism. Pseudopopulations remain a valid central assay; individual-neuron significance is not a gate.
- Fixed target: `D_N_C_M__N_C_B`, presence among **all interior corridor runs** after removing first/last. No new target/graph/panel search.
- First `[0,1)` seconds only: ten100ms native bins, aggregated to1/2/5 bins. “Whole cue” must not imply the excluded variable-duration tail.
- 147 train +41 historical-validation sources,49 unique unit IDs,13 sessions,756 observed unit–source pairs. Five separate endpoint models; validation support participated in prefit eligibility. Original holdout exposure remains in force.
- Round1:18 temporal×transform×scaling arms at average-loss L2 λ=.1. Round2 adds λ=.01/1 only for the CV-winning representation. Selected **`t1_raw_rate_variance_floor_l2_1`** before historical predictive evaluation: CV Δlogloss+.0926123, BA.637397.
- Historical selected Δ+.0285834, BA.55. Endpoint deltas:2→1−.0014706;3→1−.0824712;4→1+.0498888;5→1−.1174369;6→1+.2944069. Only2/5 positive; omit6→1 and mean−.0378725. The selected recipe is the only observed-family arm with positive historical Δ, but **broad robustness criteria failed**.
- Ordinary selected/max-family p:17/101=.1683 and36/101=.3564. Temporal-half:14/101=.1386 and30/101=.2970. Both references compare with the fixed observed CV-selected statistic. Each null repeats its own adaptive20-arm algorithm; never mix policies or count repeated seeds as extra worlds.
- 200 source-bootstrap q025/q50/q975:−.0875134/+.0153847/+.1006115. Sensitivity quantiles only, not inferential/animal/selection-adjusted CIs.17/28 validation pools are singletons;2→1 and4→1 remain point/influence only.
- Seeds1/2 validation Δ+.0180827/+.0207059: Monte Carlo sensitivity, no reselection/replication. Nuisance-only trial index/full-cue duration Δ−.356060; fixedλ.1, non-nested, not tuned nuisance exclusion.12/13 leave-session refit means positive; shared20180814 removal yields−.003931. Overlapping refits are not independent replications.
- Temporal null has52/101 pure strata covering64/188 sources. Actual changed-label median fraction31.38% versus44.68% ordinary. Producer `movable_fraction` instead counts records in strata with any realized change. Neither establishes serial exchangeability.
- No H1b/H2 result, no absence/equivalence claim, no unique explanation of previous CEBRA failure. Do not compare old/new path percentages as a matched ablation across different source panels.

## Authoritative paths

Worktree: `/home/hongyi-home-lab/neuro_science-path-autoresearch-20260908`.
Branch: `research/path-preprocessing-autoresearch-20260908`; base`a50016807ab14fbdfceb242e673f2a39a1f42a91`. No commits/pushes in this task.

Run root relative to that worktree:
`outputs/path-preprocessing-autoresearch-20260908/biological-20260908T115508Z/`.

- `export/`, `round1/`, `round2/`: original accepted export/CV.
- **`final-20260908T133200Z/`**: accepted complete final stage. `final_summary.json` is the scientific aggregate authority; per-world models/predictions/lineage support it.
- **`verification-final.json`**:82,283 numerical model forward replays, **zero new fits**, with recomputed training/evaluation metrics, source lineage, adaptive selection/nulls, bootstrap seeds/strata/hash/quantiles, nuisance features and seed/influence summaries; hashes of then-existing run artifacts.
- `descriptive-audit.json`: fit ledger, actual null-label movement, singleton pools.
- `final-20260908T125617Z/`: interrupted operational attempt, NOT an alternate final result.

Manager: `/home/hongyi-home-lab/neuro_science/outputs/path-autoresearch-management-20260908/`. Read `SCRATCHPAD.md`, frozen protocol/source manifest, `ROUND2-DECISION.md`, `SELECTION-FROZEN.json`, review receipts and `FINAL-ATTEMPT-1-FAILURE.json`. **Historical pending-review flags are chronology, not current instructions to restart.**

## Execution and verification integrity

Accepted300 CV +81,983 final-stage fit instances =82,283;80,000 final fits are null controls, not80,000 chosen hypotheses. Interrupted attempt adds12,850 durable records:95,133 recorded biological-data fit instances across attempts, not biological sample size. Its last267 completed-fit records lack a completed original coefficient package; any further in-flight fit is unknown.

The first final attempt hit the background runner's20MB stdout cap. The unchanged deterministic rerun used a fresh directory and file-routed stdout/stderr; observed/nuisance/seed predictions matched after decompression. No source/method/selection/seed/control-count changes.

Main code: `scripts/place195_path_preprocessing_autoresearch.py`; fitter SHA256`0b49c6d84e4b59842e4d64d8f6e18e075811590bd11dcd2834f1e0555b32782f`. Original CV and final execution snapshots are under `work/path-autoresearch-20260908/code-snapshots/`. The verifier was strengthened after independent findings without modifying this fitter. Verified verifier SHA256`b8b1030d6e322faf0d8e3e6fdf19e5aec1e6a0a5cb0ab9474cf6ede2385c3dea`.

Focused checks:19 tests across three files (13 study tests +6 existing split/bin tests), including corrupt resampling/quantile/lineage/Brier rejection and fitting-forbidden numerical replay. Some primary LSP checks timed out; do not equate that with confirmed absence of type errors.

Runtime: `/home/hongyi-home-lab/neuro_science/scratch/v6-v9-runtime/bin/python`, CPU threads2. No installs, GPU training, original-test evaluation, transfers, or service changes. Raw test-containing files were physically streamed only during guarded export; zero forbidden rows were yielded.

Reverification needs the data-equipped checkout and a **fresh receipt path**; it takes about12minutes, performs no model fitting, and must not run with Python `-O`. Detailed model/data artifacts remain local/ignored: Git and the portable report bundle are not full backups.

## Next decisions, not automatic execution

Verify task/cue/recording-group and admissible history/view/heading metadata; agree an effect threshold and source-aware sensitivity assumptions; freeze any6→1 follow-up before genuinely new source data. A stronger nuisance comparator requires matched training-only tuning and a nested comparison. Do not continue adapting on this historical diagnostic or require per-cell significance before condition-level work.
