# Neuro Science Workspace

This folder is the top-level home for neuroscience work, lab context, and references to analysis code.

## Layout

- `AGENTS.md`: working instructions for coding agents.
- `context/`: living notes, repo maps, and durable observations.
- `learning/`: Hongyi's neuroscience learning path, explained from an ML/deep-learning background.
- `notes/data_inspection/`: durable findings from inspecting local datasets.
- `notes/sessions/`: dated session summaries, diagrams, decisions, and next steps.
- `papers/`: paper notes, reading queues, and references.
- `docs/research-questions.md`: active prospective-path research framing.
- `docs/analysis-contract.md`: cue-population and subsequent-path data contract.
- `docs/getting-started-tasks.md`: individual onboarding and first-analysis tasks.
- `Hippocampus.jl/`: Julia analysis repo, tracked as a submodule on `updates6`.
- `PyHipp/`: older Python reference repo, tracked as a submodule.

## Current Project

The thesis-level direction is to test whether hippocampal population activity
during the cue period contains information about the subsequently observed
navigation path beyond start and goal.

H1 has two linked components: incremental prospective path information and its
possible low-dimensional organization. A later comparison with representations
learned independently by an artificial navigation agent is H2, a stretch aim.
Place, view, and conjunctive analyses remain supporting validation and confound
checks rather than the primary question.

Latest completed study: [**Path-generalization package — start here**](docs/professor_updates/path_generalization_20260907/README.md)
(2026-09-07; presentation/roadmap updated2026-09-08). It contains the self-contained
HTML, code/tests, exact executed-source snapshots, compact evidence, and a
status-labelled archive of intermediate/failed work.

The342 native CEBRA fits transfer across new mixtures of training sources but not
reliably across source pools. Neither data scarcity nor CEBRA formulation is a
proven unique cause, and this is not evidence of absent prospective biology.
The old “absent” target meant absence from interior corridor positions, not
necessarily from the whole path. Corrected B-family inference is **p19/21**.

- [Teaching HTML:12 embedded figures and full tables](docs/professor_updates/path_generalization_20260907/path-generalization-teaching-audit-20260907.html).
- [Current next-study proposal](docs/reports/path-generalization-next-steps-20260908.md):
  keep source-safe pseudopopulations central; prioritize source-trial replication,
  support/semantics and endpoint controls, not merely more synthetic rows or a
  large simultaneous195 recording. Per-unit checks are complementary; individual
  neuron significance is not a gate.
- [Status and deprecation ledger](docs/professor_updates/path_generalization_20260907/STATUS.md)
  and [packaging corrections](docs/professor_updates/path_generalization_20260907/CORRECTIONS.md).
- [Frozen prefit protocol](docs/reports/path-generalization-prefit-20260907.md).
- [Verification, regeneration and retention instructions](docs/professor_updates/path_generalization_20260907/README.md#verify-without-fitting).
  Checkpoints/arrays remain local and checksummed, not uploaded or backed up by
  this PR. A code-only clone cannot rerun the complete saved-result audit.

Earlier exploratory results: [`V6–V9 teaching and audit report`](docs/reports/place195-v6-v9-autoresearch-20260906.md)
(2026-09-06): geometry graph, pseudopopulation support, cue bins, PCA, and GPU CEBRA.
The bounded benchmark was nonpositive; the report documents sparse source support
and an early holdout-exposure incident, so it is not confirmatory H1 evidence.

- [Professor HTML report](docs/professor_updates/place195_v6_v9_20260906/place195-v6-v9-professor-methods-results-validity-20260906.html): download for offline reading with embedded figures.
- [Earlier audit guide and alternatives to forced common-panel pseudopopulations](docs/reports/place195-audit-and-next-steps-20260907.md).
- [Data-volume comparison with CEBRA and hippocampal studies](docs/reports/cebra-data-volume-comparison-20260907.md).

Raw data, detailed run artifacts, and runtime environments remain local/ignored;
links into `outputs/` in the audit Markdown require the data-equipped checkout.

For earlier context, see [`docs/prospective-path-research-flow-review.md`](docs/prospective-path-research-flow-review.md).
See [`docs/research-questions.md`](docs/research-questions.md) for the canonical framing
and [`docs/analysis-contract.md`](docs/analysis-contract.md) for the data required to test it.

## Submodules

The external repos are submodules so this workspace can track exactly which versions were used while preserving each repo's own history.

After cloning this parent workspace somewhere else, run:

```sh
git submodule update --init --recursive
```

## Data

Raw or formatted neuroscience data should live under `data/` unless a project needs a different layout. Data and generated analysis outputs are ignored by default so they do not accidentally enter git.
