# Executed: saved CEBRA latent-space atlas

Date: 2026-09-24. **Exploratory descriptive analysis.** No CEBRA/decoder training, checkpoint execution, original-test access or new topology/significance test. Implements the [frozen atlas protocol](cebra-latent-atlas-protocol-20260924.md). The [illustrated HTML review](cebra-latent-atlas/review.html) explains the pipeline from first principles and compares it with the primary papers.

## Open the deliverable

- [**Interactive offline atlas**](cebra-latent-atlas/atlas.html)
- [**Illustrated pipeline and paper review**](cebra-latent-atlas/review.html)

Download each HTML using GitHub's **Download raw file** control, then open it locally in a browser. GitHub's source view does not render the visualization. Both pages embed their figures/data and need no server or internet; public paper links are optional. Download both into the same directory to use the review's atlas link. Neither page depends on the expired cmux preview.

This explicitly authorized package is in the existing **private** repository. It contains derived research coordinates/figures, not raw recordings, checkpoints or full source-trial manifests. Do not republish it through a public HTML preview service.

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

## Published package and local replay

The Git-backed [package directory](cebra-latent-atlas/) contains the unchanged accepted `atlas.html`, cleaned portable `review.html`, [complete metrics](cebra-latent-atlas/summary.json), [original execution manifest](cebra-latent-atlas/execution-manifest.json), [historical forward-verification receipt](cebra-latent-atlas/verification.json), [historical browser receipt](cebra-latent-atlas/browser-validation.json), and [publication checksums](cebra-latent-atlas/delivery-checks.json). The manifest/receipts describe the original **full local archive**, not a claim that every input/output they enumerate is committed.

Full local archive: `outputs/cebra-latent-atlas-20260924/atlas/`. Its contents remain ignored:

- `atlas.html`: standalone interactive page, with all data needed to view it locally.
- `summary.json`: complete per-run/bin-space/whole-cue metrics and cross-seed comparisons.
- `manifest.json`: input hashes, historical-hash-check scope, code hashes, versions, CPU/runtime identity, Git revision/dirty state, output hashes.
- `projections/*.npz`: means, display bases and full-precision train/development coordinates for every run.
- Six PNGs: endpoint/path projected and fixed-coordinate views, projection retention and spectra.
- `code/`: exact generating Python/template/test/protocol snapshots.
- `verification.json`: forward projection and retention checks without display-PCA refitting.
- `browser/`: offline browser checks and screenshots, produced after the scientific artifact manifest.

Viewing and package/software checks need **no private inputs**. From a checkout with the dependencies in `pyproject.toml` installed:

```sh
python -m unittest scripts.test_cebra_latent_atlas -v
```

The browser's embedded control smoke check is available by opening `atlas.html?selftest=1`; success sets `data-ui-tests="passed"` on the document body. No package installation, model training or server is needed to view the downloaded HTML.

Rebuilding/replaying the full analysis additionally requires the authorized historical private artifact tree; Git alone cannot restore it. References to adjacent `manifest.json` and `projections/` inside the unchanged atlas describe that **local archive**. Rebuild into a **fresh** directory; accepted results are never overwritten:

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

Historical read-only reviews covered the protocol, code and numerical/claim interpretation; their outcomes and resolved findings are recorded above. Their temporary harness transcripts are **local-only provenance, not distributed evidence or a dependency of this package**. AI review does not verify missing laboratory metadata or replace peer review.

## Publication cleanup

The owner subsequently requested this PR. The atlas and numerical summary are copied byte-for-byte from the accepted run; no geometry is recomputed and no model is fitted. The generator is Python-AST-identical to its execution snapshot (formatting differs). The portable HTML review removes temporary server/session/delete instructions, adds package navigation, and corrects stale neighboring-study status. The separate [matched PCA/raw comparison](path-pca-matched/README.md) is completed and was merged in [PR #7](https://github.com/Hong-yiii/neuro_science/pull/7) on 2026-09-23 (merge `834063184085b8ff9eaa19264728a1bf79969d70`, checked against GitHub during publication). Its own historical README still describes a draft; that is not current PR state. The comparison is not part of this atlas or an unexecuted task to restart.

Only this visualization package, its two documents, HTML review, generator/template/tests and index entry belong to the PR. Unrelated decoder/hyperparameter work and all other working copies are left untouched. Original artifacts and earlier attempts remain local. No daemon, public hosting, new dependency, raw-data upload or additional experiment is introduced. Optional Track B/augmentation/topology work remains deferred.

Publication validation:

- **Seven tests passed** both as `python -m unittest scripts.test_cebra_latent_atlas -v` and by direct script execution. The new test binds the distributed file hashes to the execution manifest, compares all embedded atlas metrics with `summary.json`, and rejects expired preview instructions.
- **Fresh forward replay passed on a disposable copy** of the full accepted archive: 125 input hashes, 51 output hashes, 156 projection/retention checks; zero encoder/decoder/display-PCA fits. The receipt was byte-identical to the historical one. No accepted artifact was overwritten.
- **Offline Chrome checks passed** for the atlas at 1500×1400 and 390×1300 and the review at 756×1100 and 390×1000. Atlas controls/selftest, review figures, document width and local navigation were checked; no external runtime resources were found.
- Python primary LSP checks passed. The template was also confirmed clean; the large illustrated HTML's language-server check timed out, so HTML validation relies on the explicit parser/link and real-browser checks rather than a claimed clean LSP scan.
- Independent read-only package review raised two low-severity documentation notes: temporary transcript paths were not portable, and the neighboring matched-PCA draft/merge status conflicted. The first was removed from the portable evidence contract; the second was checked against GitHub and linked to the actual merge above. The reviewer did not independently rerun the parent’s browser/replay checks.

The machine-readable publication checksum/check record is [delivery-checks.json](cebra-latent-atlas/delivery-checks.json). These checks establish delivery integrity, not new biological evidence.
