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

Start with [`docs/prospective-path-research-flow-review.md`](docs/prospective-path-research-flow-review.md)
for the pinned current-state review. See [`docs/research-questions.md`](docs/research-questions.md)
for the canonical framing and [`docs/analysis-contract.md`](docs/analysis-contract.md)
for the data required to test it.

## Submodules

The external repos are submodules so this workspace can track exactly which versions were used while preserving each repo's own history.

After cloning this parent workspace somewhere else, run:

```sh
git submodule update --init --recursive
```

## Data

Raw or formatted neuroscience data should live under `data/` unless a project needs a different layout. Data and generated analysis outputs are ignored by default so they do not accidentally enter git.
