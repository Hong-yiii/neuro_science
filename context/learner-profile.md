# Learner Profile

Created: 2026-07-29

Hongyi is experienced in ML, deep learning, and mostly NLP-oriented modeling, but is newer to neuroscience methods and terminology.

For this workspace, explanations should:

- translate neuroscience ideas into ML analogies when useful;
- clearly separate what is directly measured from what is inferred;
- emphasize observability limits of hippocampus and related brain areas;
- explain preprocessing steps as transformations from raw signals into analysis-ready tensors/tables;
- distinguish encoder training, decoder evaluation, task-information recoverability and formal dynamical-state observability;
- use the [October11 latent-model/observability agenda](../docs/cebra-observability-agenda-20261011.md) and [companion retrospective](../docs/reports/cebra-research-synthesis-20261011.md) as the current planning entry points. The new direction is requested, but its operational hypotheses/protocol remain proposals. H1 is retained as prior work, not a required next target; artificial-agent H2 stays removed.

Important teaching frame:

```text
Recorded spikes are measured; bins, pseudopopulations and embeddings are derived.
Shared encoder parameters do not establish shared biological representations.
A successful readout is an association, not direct observation of intention.
```

The user expects to receive higher-level formatted neural data from the professor, which may intentionally hide much of the preprocessing. Treat that as acceptable, but keep the analysis contract explicit so assumptions remain auditable.

Current focus (October11): narrow two documents—a rigorous completed-work synthesis
and a new CEBRA-centered agenda for estimable/reusable hippocampal task-state models.
Later fold a condensed future-work section into the synthesis. Distinguish task
recovery, frozen readout transfer, predictive-state estimation and model-relative
observability. The proposed neural forecasting/spatial-readout strawman needs
verified simultaneous data and a separately approved protocol; it is not a queued run.

Previous H1-focused scope — historical context:

- cue-period hippocampal information about the subsequently observed path beyond start and goal;
- reproducible low-dimensional organization of that information;
- component-level graph decoding as a simpler assay, with ordered graph-path prediction as the desired capability;
- place, view, heading, action, and conjunctive coding as supporting controls;
- CEBRA-Time cue-only versus joint cue/navigation training, two predefined checkpoints, deliberate source folds and PCA/LDA baselines;
- decoder choice left open, without broad encoder-setting sweeps;
- a traceable pseudopopulation construction artifact with runnable checks;
- phase-selectivity/rotation interpretation deferred for mentor/literature clarification.
