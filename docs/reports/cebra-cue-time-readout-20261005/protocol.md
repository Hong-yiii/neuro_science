# CEBRA cue-time frozen-readout protocol

**Prepared:** 2026-10-05 SGT. **Status:** preparation only; no real single-bin decoder fitting has been run from this protocol. This is a bounded exploratory study on historically exposed sources, not confirmation.

## Gate and authority

Hongyi explicitly authorized execution in the current conversation on October5 ("okay can you please execute this?"). Operational launch remains gated on independent protocol/code review and a hash-bound approval recorded by the parent agent; this is not authorization for any encoder retraining or broader search. The runner refuses `run` without an approval JSON matching the current script, protocol, source-support document, accepted-run manifest and count contract.

Current accepted source authority is the completed full-trial-transfer run:

```text
outputs/cebra-full-trial-transfer-20260924/biological-run-20260924T162913Z/
```

The current `scripts/cebra_full_trial_transfer.py` hash is `5e8065af5cb7f61683a3cc05a4d022f05c79f214afaea093682cafb94695ff5e`, while the accepted executed snapshot hash was `ad1dc989d65b43bf0bcdd55638f66d1918a6c61654f69eec3e98edabe2e1a4b4`. Parent inspection found only typing/Pyright-only edits (`typing.cast`, offset ignore, iterable cast); scientific functions and all four helper hashes match the accepted run. This protocol records that harmless snapshot difference and binds the current file in any new approval.

Pre-existing local work to preserve, per parent hashes:

- `docs/professor_updates/research_review_20260928/evidence.py` — `15dd91f31afe58e1a969cd54389fd8698b6e7d8aaf43c3c1660b9e0e3a5e8a54`
- `docs/reports/README.md` — `7880a6c8483934d49f14b77b909fcd0236d74d1e20ddc5132ec605f35d5f71dd`
- `scripts/test_cebra_latent_atlas.py` — `d38a866edc1bb37a416ad4b290ff8056d0efa50c73cb8a05b40292bc3ef45fc3`

Scientific preflight guidance recorded here: `scientific-preflight-review-run5773a0b1`.

## Fixed cohort and target

Reuse exactly the accepted September24 fixed cohort:

- endpoint: fixed `4->3`;
- component target: `D_N_R_T__N_R_M` interior path component;
- units/session blocks: 29 selected units from seven sessions;
- source split: 82 training sources and 22 historical-validation sources;
- validation pseudorows: exact 30 class-conditioned combinations, 24 absent and 6 present;
- class weighting: exact balanced weights, not row-count balance (`0.5 / n_class`);
- no goal-prediction head is possible or added for this cohort.

The source tensor remains:

```text
outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/v7-v8-neural-experiments/primary29_min3train_min1val/bin100ms/source_level_cue_tensors.npz
sha256 688e3b52f69a872c7aec420da99ebb6f0b80464351ded3813b077cd7ed3cf567
```

Validity gate: finite nonnegative measured counts/exposures for observed source cells, saved mask equals session-cell membership, every source/bin has positive support, and no missing-to-zero conversion. The known clipped cue exposure is retained: minimum exposure is the valid shorter final bin (`0.09903399646282196 s`, source `20180810_session01_trial090`, bin 9), not an exclusion.

## Intervention

The main intervention is **decoder input window**, not encoder training duration. Encoders, source assemblies, scalers and PCA/CEBRA transforms are reused from the accepted run.

Representations:

1. `raw290`: saved cue-scaled raw counts. Whole-cue order is cell-major `(row, cell, bin) -> 290`; a single bin is `reshape(n, 29, 10)[:, :, b] -> 29`.
2. `pca8`: saved pooled train-bin PCA state. Whole-cue order is bin-major `(row, bin, coord) -> 80`; a single bin is `reshape(n, 10, 8)[:, b, :] -> 8`.
3. `cue_time`: accepted final1000 cue-trained CEBRA-Time checkpoint/embeddings, bin-major 8D per bin.
4. `full_time`: accepted final1000 broader cue+navigation CEBRA-Time checkpoint/embeddings, bin-major 8D per bin.

Behavior encoders and LDA remain historical/contextual references only. No LDA readout family is added in this bounded decomposition.

Readouts:

- logistic regression: train-only StandardScaler + `C=.01`, `liblinear`, balanced class weights, `max_iter=1000`, `random_state=0`;
- RBF SVC: train-only StandardScaler + `C=1`, `gamma=scale`, balanced class weights, `probability=False`, `max_iter=100000`, `random_state=0`.

The ten focal windows are the ten 100 ms cue bins. Whole-cue outputs already exist and are replayed from accepted decoder states as a fixed comparator; whole-cue is **not** an eleventh selected bin.

## Fit and replay counts

Confirmed count contract before fitting:

```text
new single-bin readouts = 4 representations × 2 readouts × 10 bins × 3 seeds × 21 worlds = 5040
saved whole-cue replays = 4 representations × 2 readouts × 3 seeds × 21 worlds = 504
```

The 21 worlds are the observed world plus all 20 accepted source-coherent null worlds. All three accepted seeds (`0,1,2`) are reused. Null encoders/PCA/scalers/manifests are reused; no null world is silently dropped and no encoder/PCA is refit.

## Metrics and null families

Report every bin curve and effect. Do not choose a winning bin, checkpoint or readout.

Primary new null statistic, per scientific reviewer:

```text
max over 10 bins of the three-seed mean paired logistic balanced-loss gain:
loss(cue_time) - loss(full_time)
```

The observed statistic is compared with the same statistic in each null world using the inclusive plus-one tail. This is a limited-resolution no-association reference, not a superiority p-value and not a correction for project adaptivity.

Secondary absolute families:

- balanced-accuracy family: max over `10 bins × 4 representations × 2 readouts` (80 views) of the three-seed mean validation BA, compared with the matched null statistic;
- logistic-loss absolute family: max over `10 bins × 4 representations` of `log(2) - balanced_log_loss`, compared with the matched null statistic.

Whole-cue fixed reference is reported separately and never enters those max-over-bin families. Report BA, AUROC, class recalls and count/true-class-normalized confusions; report balanced log loss and Brier only for logistic.

## Source sensitivity

For observed predictions only, reuse the accepted fixed-model sensitivity design:

- 200 source reweight worlds, sampling within `session × class` strata;
- delete-one-source sensitivity for all 22 validation sources;
- seeds fixed and averaged;
- metrics for every bin plus whole-cue paired `full_time - cue_time` BA and logistic `cue_time - full_time` loss gain;
- for each of the four representations/readouts, paired bin-minus-whole BA and whole-minus-bin logistic loss under the same source weights, with every bin retained.

This is source-pool sensitivity, not a pseudorow bootstrap and not a biological confidence interval. Singleton/one-class deletions are marked inestimable.

## Geometry diagnostic

Separate descriptive diagnostic only, observed world only:

- arms: `cue_time`, `full_time`;
- seeds: 0, 1, 2;
- saved checkpoints: 250, 500, 750, 1000 updates;
- same source assemblies as the accepted observed world;
- output: bin-8D and whole-cue-80D spectra/participation ratio, plus train/validation distance and neighborhood stability versus the 1000-step checkpoint.

No readout selection uses checkpoint geometry. No binary two-centroid RDM correlation or inferred biological rotation is introduced.

## Commands

No-fit audit and count confirmation:

```sh
export PYTHONDONTWRITEBYTECODE=1 PYTHONNOUSERSITE=1
export OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2
PY=/home/hongyi-home-lab/neuro_science/scratch/v6-v9-runtime/bin/python
$PY scripts/cebra_cue_time_readout.py counts
$PY scripts/cebra_cue_time_readout.py audit \
  --output-dir outputs/cebra-cue-time-readout-20261005/preparation/audit-YYYYMMDDTHHMMSSZ
$PY scripts/cebra_cue_time_readout.py geometry --device cpu \
  --output-dir outputs/cebra-cue-time-readout-20261005/preparation/geometry-YYYYMMDDTHHMMSSZ
```

Real readout run, only after parent supplies a matching approval JSON:

```sh
PY=/home/hongyi-home-lab/neuro_science/scratch/v6-v9-runtime/bin/python
RUN=outputs/cebra-cue-time-readout-20261005/run-$(date -u +%Y%m%dT%H%M%SZ)
$PY scripts/cebra_cue_time_readout.py run \
  --approval outputs/cebra-cue-time-readout-20261005/preparation/prefit-approval.json \
  --output-dir "$RUN" \
  --device cuda
```

No-fit verification and report rendering after a completed approved run:

```sh
VERIFY=${RUN}-verify
$PY scripts/cebra_cue_time_readout.py verify --run-dir "$RUN" --output-dir "$VERIFY" --device cpu
$PY scripts/cebra_cue_time_readout.py report --run-dir "$RUN" \
  --output-dir docs/reports/cebra-cue-time-readout-20261005
```

Run outputs are private under `outputs/cebra-cue-time-readout-20261005/`. The docs package keeps only protocol/report/aggregate figures/data; raw arrays, checkpoints, decoder states and prediction tables stay ignored.

## Stop conditions

The complete accepted hash manifest is verified before audit/run/verification. Each of the63 observed/null assemblies is reconstructed from the frozen source-label maps and seeds and compared with saved lineage. Whole-cue predictions/metrics are compared numerically with the historical saved results. Approval includes the successful source-audit path and hash. New exact code/helper snapshots, runtime, dirty state, attempted/completed/failed fits, predictions and state hashes are retained. No-fit verification compares all11 windows independently, both secondary families, whole-cue references, confusions and all source sensitivities; fit APIs are blocked.

Stop without fitting if approval facts mismatch, protocol/docs/script changed after approval, source counts/exposures fail, a world/seed/readout count is missing, any saved state hash fails, a fit does not converge, output exceeds 10 GiB, or the run exceeds the 90 minute budget.
