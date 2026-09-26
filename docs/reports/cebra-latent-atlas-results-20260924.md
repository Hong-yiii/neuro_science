# Executed: saved CEBRA latent-space atlas

Date: 2026-09-24. **Exploratory descriptive analysis.** No CEBRA/decoder training, checkpoint execution, original-test access or new topology/significance test. Implements the [frozen atlas protocol](cebra-latent-atlas-protocol-20260924.md), following the [paper/image review](cebra-latent-geometry-review-20260923.md).

## Open the deliverable

[**Interactive offline atlas**](../../outputs/cebra-latent-atlas-20260924/atlas/atlas.html)

The HTML is a standalone local file: download it and open it in a browser. It needs no server or internet. It contains derived private research data, so use approved sharing channels. Its `outputs/` path is ignored/local, not a GitHub download.

From the Mac, in a chosen output directory:

```sh
scp homelab:/home/hongyi-home-lab/neuro_science/outputs/cebra-latent-atlas-20260924/atlas/atlas.html ./cebra-latent-atlas.html
```

The page provides:

- 39 saved run/reference objects, with all three seeds, split across endpoint and V9 path-component studies;
- training/development point clouds with synchronized rotation and scale;
- separate cue-bin and whole-cue spaces;
- recoloring by start, goal, joint condition, path presence, cue bin or source reuse where defined;
- condition centroids alongside clouds and optional lines within one synthetic row;
- native/first-coordinate checks, training-fitted PCA3 views, full-space metric tables, and six embedded static figures;
- source counts, original decoder scores, method differences and interpretation warnings beside the plots.

**Suggested first view:** endpoint → `positive_bin_t03-step250 / seed 0` → cue-bin vectors → goal; then change to start and joint condition without changing coordinates. Inspect seeds 1 and 2. Compare `time_t1-step250`, then `positive_bin_t03-step3000`. Use the cue-bin filter to see which parts of the cloud belong to which cue phase; do not promote a visually selected phase to a confirmatory result.

## Main answer

**The strongest endpoint CEBRA result has substantial structure outside its first three display axes. A 3D picture is genuinely incomplete. But greater spread across dimensions did not imply better decoding, and no biological manifold topology was established.**

The endpoint Time embedding is much easier to represent in 3D than the promising same-bin Behavior embedding. This is a useful objective-dependent geometry difference, not a claim that Time is scientifically superior. In the accepted path study, visually structured embeddings still accompany nonpositive held-out decoding.

### Saved endpoint runs: quantitative comparison

Ranges are across seeds 0, 1 and 2; they are not confidence intervals. Original accuracy is the three-seed mean of the existing 30-class whole-cue readout.

| Saved recipe | Original development accuracy | Development energy retained by training-fitted 3D bin-space view | Development effective linear dimension (PR) | Full-space vs 3D distance Spearman |
| --- | ---: | ---: | ---: | ---: |
| Same-pair/same-bin Behavior positives, τ=.3, 250 steps | 83.33% | **56.3–64.2%** | **5.32–6.04** | .712–.762 |
| Same recipe, 3,000 steps | 64.86% | **39.5–42.2%** | **7.77–7.89** | .394–.514 |
| Time, τ=1, 250 steps | 69.72% | **95.2–98.9%** | **2.87–3.19** | .991–1.000 |
| Time, τ=1, 1,000 steps | 51.67% | 84.3–91.6% | 3.46–3.78 | .924–.972 |
| Ordinary Behavior, τ=.3, 250 steps | 53.06% | 80.9–90.1% | 3.07–4.05 | .943–.983 |
| Saved PCA8/bin reference, original C=1 readout | 82.50% | 67.7–67.8% | 4.93–4.96 | .890–.901 |

The **82.50% PCA score is not a correction to the earlier 83.61%**. This atlas reuses the original PCA feature/decoder NPZ with C=1; the later common readout used C=.01. CEBRA endpoint rows above use the later C=.01 readouts. The atlas is not a newly matched classifier benchmark.

The earlier review's **56–66%** referred to saved **training** spectrum fractions. The new **56.3–64.2%** is **development** energy retained using the training-fitted display basis. They differ in split and definition, not through revision of the historical result.

Interpretation:

- Early same-bin Behavior geometry needs more than three linear coordinates for a reasonably complete view. Its 3D neighborhoods retain only about **44–53%** of the full-space sampled top-10 neighbors.
- Later training makes this representation more evenly spread across its eight coordinates, while the original decoder performs worse. More dimensions occupied is not automatically more useful information.
- Time's early bin embedding is nearly captured in 3D but has lower endpoint decoding than early same-bin Behavior. A cleaner or more compressible cloud is not necessarily the stronger readout representation.
- The whole-cue vector is a different object: early same-bin Behavior's **80-feature whole-cue** PCA3 view retains only **46.4–46.9%** of development energy. Do not call this an eight-dimensional whole-cue representation.

### Reproducibility of condition geometry

For early same-bin Behavior, full-space within-bin condition-distance matrices correlate between training and development at **.735–.754**. Across saved seeds, development condition-distance correlations are **.792–.827**. For the late 3,000-step counterpart these fall to **.442–.470** and **.475–.528**, respectively.

The saved PCA reference has very stable development condition geometry across seeds (**.956–.959**). These are descriptive correlations on matched condition centroids, not pointwise latent-axis matches or a new statistical test. They do not establish stable individual-trial dynamics, independent-session replication or incremental path information. Behavior training explicitly encourages condition geometry; all seeds use the same underlying source pools.

### V9 path-component comparison

| Saved representation | Original mean validation balanced accuracy | Development 3D retained energy | Development linear PR |
| --- | ---: | ---: | ---: |
| CEBRA-Time-8 | **44.27%** | 90.7–95.4% | 3.10–3.31 |
| CEBRA-Behavior-8 | **41.41%** | 95.9–98.3% | 1.09–1.30 |

These results remain nonpositive relative to 50% balanced accuracy. Some projected views have arcs, shells or two-lobed configurations, but a visual shape does not rescue the decoding result. Normalization and the binary supervised objective are competing explanations for such geometry. We did not perform persistent cohomology or demonstrate a ring, torus, biological attractor or H1b.

All saved 3D/8D Time and Behavior runs are in the interactive atlas. Native E=3 views retain 100% by construction; that number is not evidence of a successful model. No condition-RDM stability statistic is reported for V9's two classes because a two-centroid geometry does not provide the same multi-condition comparison.

## What each point actually means

A cue-bin point is one assembled population vector for one 100 ms cue bin. Ten ordered bin vectors belong to a **synthetic** row. A whole-cue point flattens those ten vectors, so an E=8 encoder supplies 80 decoder features.

Each endpoint row combines **58 session blocks / 195 selected units**. Each V9 row combines **7 session blocks / 29 selected units**. All source-trial derivatives remain in their recorded training/development split, verified through the assembly manifests.

For seed 0:

| Lane/split | Synthetic rows | Unique source trials actually used | Unique full source combinations |
| --- | ---: | ---: | ---: |
| Endpoint train | 480 | 10,906 | 480 |
| Endpoint development | 240 | 3,212 | 240 |
| V9 train | 128 | 82 | 127 |
| V9 development | 128 | 22 | **29** |

These used-source counts are not the total available source pools. In particular, V9's 1,280 cue-bin points arise from 128 synthetic rows reusing just 22 development sources. Duplicate or nearly duplicate points must not be counted as independent support for a manifold. The atlas shows source reuse rather than inventing a single session label for a multi-session point. It does not supply calibrated source-level uncertainty or independently collected replication.

## Measurement and implementation details

- All saved embeddings loaded from numeric NPZ, with pickle disabled. No Torch, CEBRA, sklearn or joblib model runtime is imported by the new renderer.
- Native three-coordinate CEBRA is plotted directly. All other 3D views use a basis fitted only to the corresponding training features. The same basis applies to every cue bin and development point. Raw reference counts are training-standardized per cell for display; original decoders used their own feature scaling.
- **PCA terminology correction:** inspection of the actual producers establishes that these PCA8/bin implementations fit **one pooled training-bin basis**, not one independent basis per bin. The frozen protocol was corrected before new geometry computation. Endpoint PCA features were already saved numerically. The older V7/V8 PCA geometry is reconstructed from saved float32 directions/scaler and training-recentered; it is explicitly not a bitwise replay of the original PCA estimator.
- Retention is `sum(projected(x - train_mean)^2) / sum((x - train_mean)^2)`. Development mean shifts contribute to this energy. The separately computed development spectrum/PR is descriptive, not another display fit used on training.
- Euclidean full-space distances are chord distances for normalized CEBRA bin latents. Projection diagnostics use a deterministic, class-balanced sample of at most 64 synthetic rows, retaining their bins and excluding within-row comparisons. Source reuse still remains across sampled rows. Boundary-tie and zero-distance fractions are exposed.
- Endpoint condition-RDM comparisons use matching conditions in each cue bin, concatenating only within-bin distances. Whole-cue RDMs are separate. No label-selected rotation, cross-validated decoder refit, Procrustes or CCA was added.
- Existing source splits, unit scope, targets and original classifier settings were unchanged. No new path-distance/conditional-association test, shuffled model, significance threshold, intrinsic-dimension claim, hybrid fit or new latent-dimension sweep was introduced.

## Artifacts and replay

Root: `outputs/cebra-latent-atlas-20260924/atlas/`.

- `atlas.html`: standalone interactive page, with all data needed to view it locally.
- `summary.json`: complete per-run/bin-space/whole-cue metrics and cross-seed comparisons.
- `manifest.json`: input hashes, historical-hash-check scope, code hashes, versions, CPU/runtime identity, Git revision/dirty state, output hashes.
- `projections/*.npz`: means, display bases and full-precision train/development coordinates for every run.
- Six PNGs: endpoint/path projected and fixed-coordinate views, projection retention and spectra.
- `code/`: exact generating Python/template/test/protocol snapshots.
- `verification.json`: forward projection and retention checks without display-PCA refitting.
- `browser/`: offline browser checks and screenshots, produced after the scientific artifact manifest.

Rebuild into a **fresh** directory; accepted results are never overwritten:

```sh
export PYTHONDONTWRITEBYTECODE=1 PYTHONNOUSERSITE=1
export OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2
PY=scratch/v6-v9-runtime/bin/python
"$PY" -m unittest scripts.test_cebra_latent_atlas -v
"$PY" -m scripts.cebra_latent_atlas --output outputs/cebra-latent-atlas-20260924/rebuild-new
"$PY" -m scripts.cebra_latent_atlas --output outputs/cebra-latent-atlas-20260924/rebuild-new --verify
```

The forward verifier checks input/output hashes, all stored projection bases/coordinates and retention values. It is **not** an independent recomputation of every spectrum, neighborhood or RDM statistic; synthetic invariance/degeneracy tests and independent review complement it.

## Verification and review

- Original endpoint verifiers passed **7,766 artifact hashes and 2,308 saved metric records**; V9 verifier passed all **24 observed metric rows**, saved reload receipts and eight non-fitting software checks. No checkpoint was executed during this verification.
- Six new synthetic checks passed: train-only projection, row/bin order, identity/rotation fidelity, degeneracy, source joins/corruption rejection and prohibition of model-runtime imports. Targeted primary LSP checks were clean.
- Independent pre-execution protocol review: no findings. Independent code review found one low-severity issue in direct test invocation; the script import path was fixed and direct execution added to validation. No scientific code findings were reported.
- First full atlas build `attempt01/` completed successfully. Its desktop offline control smoke check passed. It is retained as a superseded QA attempt, not another biological experiment; the final build adds spectrum panels/color legends and the test-runner repair without changing the selected models or geometry definitions.
- Pre-final `attempt02/` added spectra/legends and passed control smoke checks. Manual mobile inspection then found a horizontal table overflow; the final template makes that table locally scrollable and checks document overflow automatically. A fractional synthetic-row input is now floored to prevent a displayed line crossing row boundaries. These are presentation/validation fixes, not scientific changes.
- Final `atlas/` passed **125 input hashes, 51 output hashes and all 156 forward projection/retention checks**, without display-PCA refitting. Its `summary.json` is byte-identical to `attempt01/`.
- Final offline Chrome checks passed at **1500×1400 and 390×1300**, including both studies/spaces, cue-bin filtering, centroids, sequence drawing, keyboard rotation, fractional-row guarding, six embedded figures, no document overflow and no external runtime resources. Screenshots and `browser/validation.json` are retained; redundant DOM dumps and disposable Chrome profiles were removed after validation.
- Independent final numerical/claim review found **no scientific-result issues**. Its minor note that final browser artifacts were not yet present was resolved by completing the final browser run; these late browser receipts are intentionally separate from the earlier scientific output manifest. Final atlas SHA-256: `dba38d33c0f03ecd9a10a4246175280788312f6abfdadb4fc6727f1dafa445d5`.
- Final session diagnostics found no blocking errors in the edited files. A broader diagnostics attempt timed out for unrelated heavyweight scanners; it is not claimed as a clean project-wide scan. Existing uncommitted work from other tasks was preserved.

Read-only review logs (temporary harness records): pre-execution `119ad5e0-d987-4efe-8049-3016296c21b2`, code `45cbd1cb-8564-4dbf-841e-5dccd704f519`, results `fd202488-85ca-441e-85b2-69a4788d8b95`, each under `/tmp/pi-subagents-uid-1000/async-subagent-runs/<id>/output-0.log`. Research/input scouting used `6d97be7a-6313-4e50-b73d-13e94b8a9ad9`. AI review does not verify missing laboratory metadata or replace peer review.

No daemon, new service, package installation, data upload, commit or PR was created. Optional later Track B/augmentation/topology work remains deferred; this delivery does not reopen those studies or change the separate PCA experiment PRD.
