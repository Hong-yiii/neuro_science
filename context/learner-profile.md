# Learner Profile

Created: 2026-07-29

Hongyi is experienced in ML, deep learning, and mostly NLP-oriented modeling, but is newer to neuroscience methods and terminology.

For this workspace, explanations should:

- translate neuroscience ideas into ML analogies when useful;
- clearly separate what is directly measured from what is inferred;
- emphasize observability limits of hippocampus and related brain areas;
- explain preprocessing steps as transformations from raw signals into analysis-ready tensors/tables;
- connect methods to cue-period path information beyond start and goal, graph-based targets, and the distinction between encoder training and decoder evaluation;
- use the [September27 agreed direction](../docs/project-direction.md): the artificial-agent H2 is removed from active scope.

Important teaching frame:

```text
Recorded spikes are measured; bins, pseudopopulations and embeddings are derived.
Shared encoder parameters do not establish shared biological representations.
A successful readout is an association, not direct observation of intention.
```

The user expects to receive higher-level formatted neural data from the professor, which may intentionally hide much of the preprocessing. Treat that as acceptable, but keep the analysis contract explicit so assumptions remain auditable.

Current focus:

- cue-period hippocampal information about the subsequently observed path beyond start and goal;
- reproducible low-dimensional organization of that information;
- component-level graph decoding as a simpler assay, with ordered graph-path prediction as the desired capability;
- place, view, heading, action, and conjunctive coding as supporting controls;
- CEBRA-Time cue-only versus joint cue/navigation training, two predefined checkpoints, deliberate source folds and PCA/LDA baselines;
- decoder choice left open, without broad encoder-setting sweeps;
- a traceable pseudopopulation construction artifact with runnable checks;
- phase-selectivity/rotation interpretation deferred for mentor/literature clarification.
