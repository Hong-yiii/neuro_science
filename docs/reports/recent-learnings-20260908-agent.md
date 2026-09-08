# Agent brief: recent neuroscience learning and next research gates

> **Release status update (2026-09-08):** original worktree names, uncommitted-state statements and synthesis-only authorization below are historical. The source/docs are collated in this PR; artifact roots remain in the original worktrees. Read the [handoff index](README.md): E1/E2 real-trial controls and the [condition-level pseudopopulation plan](path-generalization-next-steps-20260908.md) are distinct complementary lanes. Neither requires individually significant cells as a gate to population analysis. This packaging does not authorize more fitting or weaken the exact-trial claim boundary.

**Snapshot: 2026-09-08, Asia/Singapore. Status: exploratory synthesis; no new biological fitting.**  
Human companion: [What we have learned](recent-learnings-20260908.md). Read it for explanations, evidence tables and literature. This brief is the compact continuation contract, not permission to launch experiments or redefine H1.

## 1. Load-bearing conclusions

1. **Do not merge the endpoint and path benchmarks.** Strong 30-class start–goal pseudopopulation decoding is a supporting condition-separability result, not information about path beyond start/goal.
2. **CEBRA is not intrinsically incapable of learning the endpoint target.** Phase-appropriate positives, temperature, duration, readout L2 and source coverage matter. PCA remains the simple strong reference; early/selected competitive scores are development observations, not confirmed superiority.
3. **“Regularization works by reducing complexity” is not an established mechanism.** Frozen-readout L2 gains are direct evidence; encoder complexity attribution is untested. A separate CE weight-decay=.1 recipe collapsed to chance. Do not call this CEBRA weight decay.
4. **Accepted path evidence is nonpositive/non-supportive.** This includes broader *source-preserving per-unit* Track C, which has already been executed. Do not propose removing pseudopopulations as an untried universal fix.
5. **Data/design limits are demonstrated; their causal responsibility for failure is not.** Sparse within-condition support, place-cell selection, unverified groups, target semantics, missing nuisance controls and development exposure are distinct limitations. Neither H1=false nor H1=true-with-more-data follows.
6. **Previous goal equals current start under the reported task rule and importer convention.** Not current goal=current start. Within a fixed current endpoint pair, previous-goal identity is fixed too; investigate varying previous start/path/history instead. Exact collinearity is not repaired by adding two columns or residualization.
7. **H1a** = incremental held-out future-path prediction beyond endpoints. **H1b** = reproducible low-dimensional organization of that information. An embedding/rank result alone establishes neither. H2 stays a stretch aim; no mechanism/intention/internal-graph claims from decoding.
8. **Current data remain exploratory.** The early V6 holdout exposure is permanent provenance. No fresh random split of inspected sources restores pristine confirmation. Metadata verification and genuinely unexposed observations are still required.

Canonical authority for the question and data gate remains [research-questions.md](../research-questions.md), [analysis-contract.md](../analysis-contract.md), and repository `AGENTS.md`. Older checklists or frozen prefit documents can describe an earlier state; consult accepted completion artifacts below before treating work as pending.

## 2. Worktree and source map

All three accessible worktrees had HEAD **`a9d8dacbbe38d0d82b9f75444e5f538b5e411352`** at inspection. The code actually executed in experiments includes recorded dirty snapshots, not merely this Git commit.

| Alias used below | Absolute path | Branch and state before this synthesis |
| --- | --- | --- |
| `ROOT` | `/home/hongyi-home-lab/neuro_science` | `place195-v6-v9-audit-reports`; pre-existing modified `scripts/place195_graph_path_baseline.py`—preserve it. |
| `ENDPOINT` | `/home/hongyi-home-lab/neuro_science-start-goal-cebra` | `baseline/start-goal-cebra`; modified README/context and untracked experiment scripts/reports. |
| `PATH` | `/home/hongyi-home-lab/neuro_science-path-diagnosis` | `research/path-generalization-20260907`; modified README and untracked experiment scripts/reports/HTML. |

A registered `/Users/hongyilin/.codex/worktrees/c797/neuro_science` entry was prunable/nonexistent on this host. It was not inspected or pruned. “All worktrees” in this synthesis means the three accessible neuroscience checkouts, not an audit of inaccessible `/root` data or every remote Mac workspace.

Final receipts mark September 7 studies complete; no matching named experiment-driver Python processes were observed during the synthesis. Nothing was resumed/retrained. No services were created or changed. Do not start a job because a historical protocol still has a prefit gate or a run's original journal describes a long-running stage.

### Exact artifact roots

```text
OLD = ROOT/outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906
OLD_FINAL = OLD/v8b-v9-cebra-final-20260905T224554Z
SG0 = ENDPOINT/outputs/start-goal-cebra-20260907
SGD = ENDPOINT/outputs/start-goal-diagnosis-20260907
SG = ENDPOINT/outputs/start-goal-autoresearch-20260907
PG = PATH/outputs/path-generalization-20260907/results-20260907T081200Z
SYN = ROOT/outputs/research-synthesis-20260908
```

These are explanatory aliases, **not shell environment variables**. `outputs/` is ignored/local. Sibling scripts and uncommitted reports are not automatically recoverable from a clone at HEAD. Use source snapshots/manifests and reconcile ownership before future integration; do not silently commit a parent reference that depends on absent work.

Active native root, for provenance only: `ROOT/data/raw/lab_server/cortex_picasso_misc_place195_20260830/`. Do not inspect original raw/importer mixed-split tables merely to repeat this synthesis. The removed eight-unit supplement remains excluded; there is no active 203-cell cohort. No expansion beyond the 195 selected cells is authorized by this brief.

## 3. Evidence ledger: metrics and denominators

### 3.1 Main V6–V9 accepted path benchmark

- `ROOT/docs/reports/place195-v6-v9-autoresearch-20260906.md` and `place195-audit-and-next-steps-20260907.md` supply the accepted chronology, superseded attempts and exposure record.
- Archive: 195 selected units / 58 sessions / 23,901 imported source trials; 1–8 selected units/session, median 3. Same-session is **not verified simultaneity**.
- Accepted V6 development behavior: 19,162 successful-after-successful sources. Fixed provisional endpoints `4->3`; interior component `D_N_R_T__N_R_M`; 660 behavioral sources for this contrast.
- Primary neural panel: 29 units / 7 sessions / 104 real sources: 82 train, 22 validation. Tensor `104×29×10` is masked source storage, not simultaneous trials. Synthetic rows are `128×29×10` per split/seed, 64/class.
- Whole-cue mean validation BA: constant .500; raw-total .453; raw-ten-bin .474; PCA3 .521; PCA8 .453; CEBRA-Time8 .443; Behavior8 .414. PCA3 seed range .258–.789.
- Perfect raw 0.2–0.3 s bin: max-over-ten-bin diagnostic null p≈.2178; not a selected primary window.
- Final V9: 12 observed +40 null CEBRA fits. Do not combine final/fast/slow/superseded directories.

Authority: `OLD/final_report_manifest.json`, `OLD/v7-v8-neural-experiments/summary.json`, `OLD_FINAL/summary.json`, `OLD_FINAL/v9/v9_cebra_metrics.csv`, `OLD_FINAL/v8b/v8b_source_label_null_pvalues.json`, plus `OLD/audits/holdout-exposure-audit.md`.

### 3.2 Endpoint baseline and autoresearch

Read `ENDPOINT/docs/reports/start-goal-cebra-baseline.md`, `start-goal-cebra-diagnosis.md`, `start-goal-autoresearch.md` and its journal.

- Predict 30 categorical ordered endpoint pairs; chance 1/30. Source pool is **original training only**, then an inner source-stratified random development split: 15,553 sources =12,288 train +3,265 validation. All 195 units /58 sessions represented through true-condition-matched assembly.
- Per seed 480 training /240 validation pseudorows; all session blocks and ten bins from one source stay together; same channels in every class. True labels are needed to build evaluation rows. Not a real unknown-trial decoder.
- Initial `C=1` joint accuracy: raw total54.86%, binned71.39%, PCA82.50%, Time42.78%, Behavior18.61%. Original 126 CEBRA fits =6 observed +120 null.
- Follow-up 112 new neural fits =79 CEBRA +33 CE. Initial and follow-up sets are separate. New fit count is not 112 biological replications.
- PCA8/bin and CEBRA8/bin each give ten×8=80 decoder features, not a single 8-D whole-cue state.

**Exact selectors for `SG/all_metrics.csv`:** filter `split=development`, `target=joint`, `decoder=logistic`, `decoder_C=.01`; use `condition=""` for primary rows to avoid duplicate `reference` rows. Verify numeric strings rather than relying on one serialization spelling.

| Claim | Case / additional selector | Mean joint accuracy |
| --- | --- | ---: |
| Common PCA reference | `case=pca_bin8`, `condition=""` | .836111 |
| Phase-matched positive improvement | `case=positive_bin_t03`, step250, dim8, τ=.3 | .833333 |
| Same positives, longer duration | same case, step3000 | .648611 |
| Fully time-matched 16-row reference | `case=matched_bin_t03`, step3000, `condition=""` | .595833 |
| Same setting, 64 rows/class | `case=matched_bin_t03`, step3000, `condition=pseudo64` | .815278 |
| Strong CE weight decay | `case=ce_bin_wd01`, step3000, weight_decay=.1 | .033333 |

**Do not confuse `positive_bin_t03` with `matched_bin_t03`.** The former is same-pair/same-bin positives with global negatives; it supplies the 83.33% result. The latter's step250 score is about81.94%, and its step3000 row supplies59.58%.

`SGD/decoder_diagnostic.json`: fixed scaled C1→C.01 gives PCA82.50→83.61%, Time42.78→51.67%, Behavior18.61→25.56%. This isolates a downstream L2 change on frozen features; other comparisons changing scaling also change effective regularization. No new independent validation was created.

`SG/04-scaling/*/support.json`: reference source-use counts10906/10885/10875 versus pseudo64 counts12277/12279/12280; available pool12288 unchanged. Therefore16→64 synthetic-row benefit mixes Monte Carlo/optimization with increased actual coverage of existing sources. Quarter/half/full requested pools used3777/6551/12288 sources because support floors apply.

`SG/06-ce-followup/metrics.json`: one CE recipe did not rescue learning; strong CE weight decay collapse is not a direct CEBRA-encoder regularization ablation. Separate-goal LDA peak81.25% at .4–.5s is six-class, not joint30-class accuracy.

Baseline and follow-up source shuffles are diagnostics, not guaranteed serial-exchangeability-calibrated inference. The original inner validation has been repeatedly inspected. Strict all30-class 75/25 time-cut support1/58 sessions is design-specific; do not generalize it to every real-trial split.

### 3.3 Path Tracks A/B/C and assembly replay

Read `PATH/work/research-planning/FINAL_STATE.md` and the final HTML under `PATH/docs/professor_updates/path_generalization_20260907/`. Accepted Track A is **`PG/track_a_v2/`**. Initial `track_a/` remains as a failed/superseded CSV-reader attempt, not an extra analysis replicate.

**Track A / empirical product:** exact validation has24 absent +6 present combinations; total class weight=.5 each. For binary predictions:

```text
BA = correct_absent / 48 + correct_present / 12
```

This is not unweighted30-row accuracy. Rows share real source blocks; exhaustive enumeration removes synthetic evaluation-draw noise, not source-sampling uncertainty. Matrix30×290 has rank9 by construction, not intrinsic brain dimension. Finite-sample ridge approaches BA≈.479 at matched regularization. Source-budget/session influence is substantial; Gaussian controls establish a possible finite-source failure mode, not the actual biological mechanism.

**Track B:**342 completed CUDA fits =62 observed +280 null;510,000 optimizer updates;42 paired1000-step prefix checks. Primary25 assembly×optimizer fits per objective: training BA1.0; mean source-disjoint exact-Q validation Time .249167 /Behavior .351667. Fixed family14 configs has best BA7/12; full-pipeline20-permutation family null **19/21=.9047619048**,18 inclusive exceedances.

**Inference authority:** `PG/track_b/summary_exact_audited.json`, `PG/audits/track_b_exact_audit.json`. Raw `track_b/summary.json` / `track_b_family_null_pvalues.json` retain stale17-exceedance p=.8571429 due to a floating-point tie. Models/predictions unchanged; do not average or choose between the values. The broader5×5 seed grid is variance diagnosis, not part of the14-config family winner test.

**Assembly replay:** `PG/assembly_transfer/assembly_transfer_metrics.csv`, `summary.json`. Fifty frozen fits,250 CPU evaluations,zero new fits. Other assemblies from the SAME training source pools yield mean BA .9925 Time /.997656 Behavior. This rules against memorization of only the exact sampled mixtures as the full explanation; it does not identify why different source pools fail.

**Track C:** `PG/track_c/summary.json`, `track_c_unit_metrics.csv`, `track_c_joint_target_null_metrics.csv`, saved predictions. Completed source-preserving per-unit models, not a simultaneous population model:

```text
baseline:  component ~ unpenalized categorical endpoint-pair intercepts
                       + trial index + cue duration
augmented: baseline + log1p(cue count / observed exposure)
```

Continuous inputs centered within endpoint using training rows, then train-standardized; average-loss slope penalty fixed. Equal-session mean of within-session unit Δlogloss is the global statistic; positive=baseline loss−augmented loss>0. Unit/trial observations are not independent copies.

| Target | Units /sessions | Mean Δlogloss |
| --- | --- | ---: |
| `middle` (original edge, all interior runs) | 15 /5 | −.0106805323 |
| `anywhere` (original edge, full route) | 12 /4 | +.0018779947 |
| `supported_middle` (`D_N_C_M__N_C_B`) | 43 /11 | +.0038601435 |

Supported-middle cohort267 train /52 validation sources. Three-target family p=.4752475 ordinary /.4356436 temporal-half. Target-specific supported-middle p=.0990 /.1980 is not a family success. One hundred coherent joint-label nulls per family preserve source identity across units; temporal-half strata are only a coarse dependence sensitivity.

**Semantic correction:** interior means every corridor run after removing the first and last runs, NOT one ordinal middle slot.51/185 old-absent fixed4→3 development paths include the original edge elsewhere. Two-run paths have empty interior. No inference of truncation, clock bug or complete-path absence from those facts alone.

## 4. Claim and validation guardrails

- Exact trial-specific population H1 needs verified simultaneous cue activity tied to that real trial's endpoints and subsequent observed path. Pseudopopulations and session-specific latent mappings do not restore unmeasured joint states/noise correlations.
- Per-unit real-trial association is allowed without an invented population, but cannot test every population code. Negative whole-cue rate results do not rule out all temporal codes.
- A flexible **joint endpoint-pair baseline**, not only additive start+goal, is necessary across conditions. At fixed endpoints, use an appropriate constant baseline and proper metrics.
- Unknown behavioral occurrence is not “absent”; unrecorded cells are not zero. Keep source IDs, QC flags, clock units, half-open cue boundaries and exposure.
- Split source trials before learned scaling/PCA/path transformations/CEBRA. Keep all bins and derivatives together. History features require boundary embargo/grouping for the reused predecessor records; block splits do not remove all confounds automatically.
- Conditioning on extra history/view variables changes the estimand. Report endpoint-only and stricter nuisance-controlled comparisons; control variables can be mediators, not merely removable noise.
- Cue-time predictors use only available pre-cue/cue variables. Later navigation measurements may define targets or labelled sensitivities, not secretly strengthen a deployable baseline.
- Never treat time bins, synthetic draws, cell-trial rows, matrix pairs, random seeds or sessions from one animal as independent animals. Never flip below-chance predictions after inspecting validation.
- Conditional nulls must respect the input target/domain. A session/split shuffle from a one-endpoint analysis cannot be reused unchanged after pooling endpoint pairs. Preserve linked cells/bins and task constraints; state remaining exchangeability assumptions.
- No architecture/bin/target hunt to force significance. Retain failures, all tested arms, family/selection correction and actual source counts. A high p-value is not equivalence to zero.
- Holdout incident: early V6 endpoint aggregate exposure; later guarded access does not restore pristine data. A follow-up mixed-table metadata read also prevents blanket “no test-containing file accessed” language. Current synthesis used accepted saved artifacts, not raw/importer tables.

## 5. Proposed next work: E0–E5 (not executed by this synthesis)

Use the same IDs as human report §8. Do not start with a new neural architecture.

| ID | Hypothesis / question | Minimal design | Decision / stop |
| --- | --- | --- | --- |
| **E0** | Can the variables/contrast be identified and measured? | Lab metadata for cue/goal/history/recording groups; accepted-development session×endpoint×component×temporal-block support; inspect path semantics and covariate collinearity. | No real within-condition variation, unreliable labels or unestimable baseline → stop this target/design and specify needed metadata/data. Missing groups blocks population claims, not every per-unit analysis. |
| **E1** | Is apparent path association explained by available history/state? | Extend Track C, same eligible real trials: M0 endpoint/time; M1 +verified history/cue-state; M2 +neural. Primary held-out Δlogloss with source/block splits and defensible conditional nulls. | History improves but neural does not → prioritize history interpretation. Neural increment persists → candidate confirmation; no unmeasured-confound/causal claim. Sparse covariate support → do not extrapolate a correction. |
| **E2** | Does full-cue rate discard useful timing, or does exposure/alignment matter? | Whole-cue reference versus one prespecified coarse cue-bin representation; raw/simple regularized decoder, PCA only where a verified multivariate group supports it. Training-only preprocessing, cue-bounded kernels; known-signal/null smoke controls. | No stable gain over same endpoint/history baseline, or only selected bin/seed → stop escalation. Track C log1p(rate) and V7–V9 ten-bin tests already exist; describe the actual new comparison. |
| **E3** | What operational effect could this assay detect/rule out? | Supervisor-agreed smallest worthwhile Δlogloss/path error; simulation/sensitivity under observed source/session counts and plausible sparsity/drift, plus source-aware uncertainty. Plan BEFORE response search. | Adequate sensitivity and upper bound below meaningful effect → evidence against that operational effect/cohort. Otherwise under-sensitive/inconclusive → specific data request. No universal minimum N or post-hoc observed-power claim. |
| **E4** | Which endpoint CEBRA generalization mechanism matters? Optional methods-only work. | Freeze sources/arrays/sampler/temp/dim/readout; bounded single-factor readout L2 first, encoder penalty or duration only if warranted; nested selection; accuracy and logloss vs matched PCA/raw. | No reproducible source-disjoint improvement → close question. Endpoint improvement remains methods/condition evidence, not H1. |
| **E5** | Does the candidate survive confirmation, and then exhibit H1b structure? | Frozen target/metric/effect threshold/null on genuinely unexposed data; target-free raw/PCA geometry and matched confounds before supervised latents. | No confirmation → no H1 promotion. Endpoint-only geometry or synthetic rank is not established H1b. H2 deferred. |

Before E1/E2 fitting, turn E0 and E3 into a prefit contract: independent source unit/group, target and eligibility, baseline, training-only transforms, split/embargo, full family of choices, metric, uncertainty/null, effect threshold, seeds, runtime budget, stopping rule, allowed claim. Independent code **and scientific-assumption** review required. Every future fit records source/code hashes and dirty state, exact package/runtime/device, configuration, outputs and failed attempts.

Do not require a PCA-versus-CEBRA win as a biological gate: H1a needs incremental path information over baseline, regardless of which valid representation obtains it. Baseline-first ordering is a resource policy, not a theorem that nonlinear signal cannot exist without a linear effect.

## 6. Verification and resumption

Start read-only:

```bash
git -C /home/hongyi-home-lab/neuro_science worktree list
git -C /home/hongyi-home-lab/neuro_science status --short
git -C /home/hongyi-home-lab/neuro_science-start-goal-cebra status --short
git -C /home/hongyi-home-lab/neuro_science-path-diagnosis status --short
```

For saved path-artifact checks, read `PATH/scripts/verify_path_generalization_results.py` first. It uses stdlib, hashes saved artifacts, recalculates exact weighted BA/nulls and checks source separation. It neither fits models nor reads raw/importer tables:

```bash
cd /home/hongyi-home-lab/neuro_science-path-diagnosis
/home/hongyi-home-lab/neuro_science/scratch/v6-v9-runtime/bin/python \
  scripts/verify_path_generalization_results.py \
  outputs/path-generalization-20260907/results-20260907T081200Z
```

Expected:342 fits,510000 updates,4488 hashed artifacts,42 prefix pairs,exact observed family maximum7/12,18 exceedances,exact family p19/21,`new_fits=0`. Do not use `python -O`: verification uses assertions. A passed verifier is software/artifact evidence, not lab metadata validation or biological replication.

Endpoint saved authority: `SG/validation.json`, `delivery-validation.json`, stage metrics and `SGD/decoder_diagnostic.json`. Historical receipts report1618 recomputed metrics,5515 hashes,111 train-only scalers,112 reload checks; this synthesis spot-checked key endpoint metrics, not an independent rerun of every historical check. The complete-row metric file contains reference duplicates; use explicit selectors above.

## 7. Research/review provenance and reconciliation

Human report §10 supplies verified primary-literature links and scopes. Research suggestions are hypotheses, not experiments already performed. Do not copy the raw literature draft without reconciliation.

Retained local synthesis artifacts in `SYN` include:

- `source-snapshot.json`:19 source-file SHA-256 hashes and initial states of the3 accessible worktrees;
- `root-evidence.md`, `path-evidence.md`, `literature.md`, `scientific-critique.md`: first-pass research/critique receipts;
- corrected endpoint audit and final reviews/resolution, plus non-fitting verification receipts.

Important synthesis corrections:

1. The first endpoint-assigned agent mistakenly audited the ROOT benchmark. Its `start-goal-evidence.md` is **rejected as endpoint evidence**; the resumed endpoint audit (`d846bd04`) checked absolute ENDPOINT paths and CSV/JSON selectors. Do not infer consensus from duplicated root coverage.
2. A path research summary repeated “ordinal middle slot”; parent accepted final-state/code semantics instead: **all interior corridor runs**. Do not propagate the stale wording from the frozen prefit narrative.
3. A literature draft misattributed the2007 multiple-choice-point destination paper to Griffin; verified PubMed identifies **Ainge et al.**, PMID17804637, DOI10.1523/JNEUROSCI.2011-07.2007. It is not needed to establish any local result. Broad, bundled spike-variability references in that draft were not adopted without exact verification.
4. A literature suggestion to “pivot H1a to shared-component geometry” was **rejected as a replacement claim**. Shared-component analysis may remain complementary, but cannot silently substitute for H1a or establish H1b beyond endpoint confounds.
5. “Include previous goal and current start” is not an identifiability solution when they are equal. Distinguish nuisance availability from independent experimental variation.
6. Track B tie-corrected authority is19/21. CE collapse is not CEBRA regularization. Source-use coverage changed in the synthetic-row sweep. These caveats survived the synthesis rather than being buried in reviewer logs.

These are AI-assisted independent checks, not external human peer review. Laboratory task/recording metadata and the biological cause of failure remain unresolved. Preserve all other agents' uncommitted work; this documentation task does not authorize commits, pushes, data transfers, service changes or new long-running experiments.
