## Answer

### Concrete direction

**Recommendation: stop treating synthetic pseudo-row count as the evidence unit.** The next defensible analysis should be a **source-trial-preserving, session/context-conditioned count model**, with a separate diagnostic that partitions:

1. **Monte Carlo assembly variance** at fixed source pool; versus  
2. **true data learning curves** from adding whole source trials/sessions/cells.

This is lazier than another architecture sweep and better matched to the current bottleneck.

### Verified prior-document facts

- Current place195 archive: **195 selected units / 58 sessions**; primary V7–V9 panel: **29 cells / 7 sessions / 82 train + 22 validation source IDs**.
- Synthetic primary arrays: **128 pseudo rows/split/seed, 64/class**, derived from finite sources, not new recordings.
- V9 CEBRA full-cue result was **nonpositive** under accepted exploratory benchmark.

### New evidence from primary/official sources

**High severity — finite-source uncertainty is the main statistical risk.**  
Aarts et al. warn that nested neuroscience observations are not independent and that ignoring nesting can inflate false positives “up to 80%” at nominal 5%. Varoquaux shows small-sample cross-validation can have large error bars, e.g. ±10% for 100 samples, and fold-to-fold SE underestimates uncertainty. This directly applies because pseudo rows share source trials/sessions.

**High severity — CEBRA multisession is not row stitching.**  
Official CEBRA docs state multisession training fits **one model per session** while positive/negative sampling is across sessions, and allows different neuron/sample counts. That supports a possible future direction only if shared labels/context are valid; it does not infer missing simultaneous population covariance.

**Medium severity — count/point-process models are the better first model.**  
Truccolo et al. provide the primary framework for modeling spiking probability with spiking history, ensemble activity, and behavioral covariates via conditional intensity / point-process likelihood. For this dataset, use the count-model simplification first: unit-trial-bin spike count with cue-exposure offset and endpoint/session/unit controls.

**Medium severity — big heterogeneous neural transformers are precedents, not remedies.**  
POYO and NDT2 explicitly target large-scale heterogeneous recordings: POYO reports 158 sessions, 27,373 units, >100 h; NDT2 targets multi-session/task iBCI pretraining. These justify avoiding fixed neuron correspondence, but not training a bigger model on 1–8 selected units/session.

### Testable hypotheses

1. **Assembly-null hypothesis:** at fixed source pool, increasing pseudo rows mostly shrinks Monte Carlo noise but does not improve source-disjoint validation.  
   Test: hold source IDs fixed; vary pseudo rows/seeds; compare to source-level label shuffles.

2. **Source-learning hypothesis:** performance uncertainty decreases only when adding whole independent source trials/sessions/cells, not pseudo rows.  
   Test: learning curves over source-trial/session subsamples; preprocessing inside each train fold.

3. **Real-trial cue association hypothesis:** cue-period counts contain path-component information beyond endpoint/session/time controls.  
   Test: Poisson or logistic mixed/regularized model on real unit-trial-bin rows; metric = held-out Δ log-likelihood / AUROC / balanced accuracy over grouped source trials.

4. **Multisession representation hypothesis, later:** session-specific encoders with shared behavioral labels outperform the count baseline without using future navigation samples.  
   Test only after support audit; compare against the real-trial GLM baseline and matched source-level nulls.

## Evidence

- Local required docs:
  - `/home/hongyi-home-lab/neuro_science-path-diagnosis/docs/reports/cebra-data-volume-comparison-20260907.md`
  - `/home/hongyi-home-lab/neuro_science-path-diagnosis/docs/reports/place195-audit-and-next-steps-20260907.md`
  - `/home/hongyi-home-lab/neuro_science-path-diagnosis/docs/reports/place195-v6-v9-autoresearch-20260906.md`

- Aarts et al. 2014, *Nature Neuroscience*, DOI `10.1038/nn.3648`: nested neuroscience observations violate independence; abstract retrieved via NCBI/Crossref.
- Varoquaux 2018, *NeuroImage*, DOI `10.1016/j.neuroimage.2017.06.061`: small-sample CV error bars; abstract retrieved via NCBI/Crossref.
- Nadeau & Bengio 2003, *Machine Learning*, DOI `10.1023/A:1024068626366`: inference for generalization error; Crossref verified.
- Truccolo et al. 2005, *Journal of Neurophysiology*, DOI `10.1152/jn.00697.2004`: point-process GLM framework; NCBI/Crossref verified.
- Schneider et al. 2023 CEBRA, *Nature*, DOI `10.1038/s41586-023-06031-6`.
- Official CEBRA multisession docs: `https://cebra.ai/docs/demo_notebooks/Demo_hippocampus_multisession.html`.
- POYO NeurIPS 2023 proceedings: `https://proceedings.neurips.cc/paper_files/paper/2023/hash/8ca113d122584f12a6727341aaf58887-Abstract-Conference.html`, DOI shown there as `10.52202/075280-1948`.
- NDT2 NeurIPS 2023 paper PDF: DOI `10.52202/075280-3523`.

## Commands Or Config

Suggested next commands, data-equipped checkout only:

```sh
# 1. no-fitting support audit
python scripts/<new_or_existing_support_audit>.py \
  --unit-scope place195 \
  --group-by session,start,goal,path_component,label \
  --real-trials-only

# 2. assembly-vs-source learning diagnostic
python scripts/<learning_curve_diagnostic>.py \
  --vary pseudo_rows,source_trials,sessions,cells \
  --grouped-split source_trial,session \
  --null source_level_label_shuffle

# 3. real-trial baseline model
python scripts/<real_trial_count_model>.py \
  --model poisson_or_logistic \
  --offset cue_exposure \
  --controls endpoint,session,time_bin,unit \
  --metric heldout_delta_loglik,auroc,balanced_accuracy
```

Minimal model formula target:

```text
count ~ label + start_goal + time_bin + session + unit + label:time_bin
offset = log(cue_exposure)
split/group = source trial, nested in session
```

## Uncertainties

- Did not inspect raw/importer/test data; no model fitting.
- Did not verify whether current Python environment already has mixed-model tooling.
- A full hierarchical Bayesian model may be useful later, but first pass should be regularized/frequentist or per-session pooled because 58 sessions include very sparse selected units.
- Multisession CEBRA remains plausible but should be treated as secondary, not as the next default.