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

Latest exploratory results: [`V6–V9 teaching and audit report`](docs/reports/place195-v6-v9-autoresearch-20260906.md)
(2026-09-06): geometry graph, pseudopopulation support, cue bins, PCA, and GPU CEBRA.
The bounded benchmark was nonpositive; the report documents sparse source support
and an early holdout-exposure incident, so it is not confirmatory H1 evidence.

- [Professor HTML report](docs/professor_updates/place195_v6_v9_20260906/place195-v6-v9-professor-methods-results-validity-20260906.html): download for offline reading with embedded figures.
- [Audit instructions and non-pseudopopulation next steps](docs/reports/place195-audit-and-next-steps-20260907.md).
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
