# Learner Profile

Created: 2026-07-29

Hongyi is experienced in ML, deep learning, and mostly NLP-oriented modeling, but is newer to neuroscience methods and terminology.

For this workspace, explanations should:

- translate neuroscience ideas into ML analogies when useful;
- clearly separate what is directly measured from what is inferred;
- emphasize observability limits of hippocampus and related brain areas;
- explain preprocessing steps as transformations from raw signals into analysis-ready tensors/tables;
- connect methods back to the main goal: comparing RNN hidden representations with neural coding data.

Important teaching frame:

```text
RNN hidden activations are easy to observe but artificial.
Neural activity is biological but partially observed, noisy, sparse, and heavily mediated by preprocessing.
The project lives in the careful comparison layer between those two worlds.
```

The user expects to receive higher-level formatted neural data from the professor, which may intentionally hide much of the preprocessing. Treat that as acceptable, but keep the analysis contract explicit so assumptions remain auditable.

Current focus:

- place-like coding;
- visual/view coding;
- conjunctive place-view coding;
- ablations over neural data representations such as bin size, smoothing, fixation filtering, and null controls.
