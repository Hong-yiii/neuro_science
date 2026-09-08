No findings.

## Read-only Track-C scientific/numerical audit

[verified] Frozen driver identity matched the task: `outputs/path-generalization-20260907/frozen/driver.py` SHA256 recalculated as `2821317f843ca2b285f2db20d9587c5dd594511e42b5fd63ad304130e4417de1`, matching `track_c/prefit_config_frozen.json:29-30`.

[verified] Data gate matches requested cohort metadata: `data_gate_checks.json:2-6` reports `64051` count rows, `19162` source IDs, rectangular within-session source-cell layout, and data SHA `b0f00...6919d2`. Modeled cohorts match: middle `5` sessions/`15` cells/`134` train/`25` validation at `data_gate_checks.json:8-15`; anywhere `4`/`12`/`108`/`22` at `data_gate_checks.json:17-24`; supported_middle `11`/`43`/`267`/`52` at `data_gate_checks.json:26-33`. I independently recomputed from `track_c_export/development_cue_counts.csv.gz`: `0` rectangular-source failures; modeled rows had empty QC flags only (`middle=506`, `anywhere=420`, `supported_middle=1252`).

[verified] Target definition is as requested. `track_c_allowlist/development_component_allowlists_manifest.json:585,617` states original middle/anywhere use `D_N_R_T__N_R_M`; `:611,622,628-630` states supported_middle selected `D_N_C_M__N_C_B`, by a train-behavior-only support ranking with no neural response values. Ranking details also appear in `track_c_allowlist/track_c_supported_middle_component_ranking_manifest.json:4-8,13-21`.

[verified] Per-unit log-loss values and equal-session aggregation reproduce from saved prediction CSVs. Recomputed maximum absolute difference from `track_c_unit_metrics.csv` was `2.22e-16` for middle, `1.11e-16` for anywhere, `3.33e-16` for supported_middle. Recomputed prediction rows/unit/session/source counts:
- middle: `78` prediction rows, `15` units, `5` sessions, `25` unique validation sources; equal-session gain `-0.01068053227734155`.
- anywhere: `68` rows, `12` units, `4` sessions, `22` validation sources; equal-session gain `0.001877994673923064`.
- supported_middle: `217` rows, `43` units, `11` sessions, `52` validation sources; equal-session gain `0.0038601434776949304`.

These match `track_c/summary.json:611-690`.

[verified] Null metrics are coherent with the stated family policy. `track_c/prefit_config_frozen.json:37-38` and `summary.json:3-5` specify three-target shared joint source-label permutations and max-over-three family statistic. Recomputed from `track_c_joint_target_null_metrics.csv`: each null family has `100` indices and `400` rows (`middle`, `anywhere`, `supported_middle`, `family_max_three_targets`), all eligible signatures match observed, and all `middle_implies_anywhere_violations` are `0`. Recomputed p-values match `summary.json:693-744`: ordinary family max `47/100`, p=`0.4752475247524752`; temporal-half family max `43/100`, p=`0.43564356435643564`.

## Defensible scientific direction

The defensible direction is **not positive proof of real-unit path information**. Old middle is negative: augmented neural-count model is worse than baseline (`-0.0106805`, `summary.json:614,645`). Anywhere and supported_middle point estimates are weakly positive (`0.001878`, `0.003860`, `summary.json:612,615,623,668`), but the family-corrected nulls are large (`p=.475` ordinary, `p=.436` temporal; `summary.json:701-705,727-731`). Supported_middle alone is only nominally suggestive under ordinary null (`p=.099`, `summary.json:713-717`) and weaker under temporal null (`p=.198`, `summary.json:739-743`). Minimum claim: Track-C found no reliable held-out log-loss improvement beyond endpoint/time/exposure; small positive estimates for anywhere/supported_middle are exploratory direction only, with old-middle opposite.

## Residual risks

- Upstream raw/importer/split correctness was not re-audited, per task constraint. This review attests the frozen derived export, saved predictions, model summaries, and null metrics only.
- The behavior-only target-selection claim is supported by frozen manifests/code and derived CSVs, not by re-reading original raw behavioral files.