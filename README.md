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

**Start with the [research handoff index](docs/reports/README.md)** (2026-09-08):
current synthesis, completed endpoint and path studies, portable teaching reports,
source-code preservation, verification, and explicit supersession labels.
Endpoint-condition decoding improved in later settings; neither that success nor
the nonpositive path analyses establish confirmatory H1 evidence. The original
holdout-exposure record remains in force.

- [Current human synthesis](docs/reports/recent-learnings-20260908.md) and [agent brief](docs/reports/recent-learnings-20260908-agent.md).
- [PCA and below-chance explanation with plots](learning/place195-pca-and-below-chance-20260908.md).
- [Artifact preservation and verification](docs/reports/research-release-20260908.md): Git is not a backup of ignored data/models.
- [Path-generalization package](docs/professor_updates/path_generalization_20260907/README.md): corrected self-contained report, code, evidence and historical status labels. The study ran 342 CEBRA fits; cross-assembly checks of 50 observed encoders transferred across mixtures of training sources, but did not establish reliable source-pool generalization. Corrected family p is **19/21**; the cause of the gap is not uniquely established.
- [Current condition-level proposal](docs/reports/path-generalization-next-steps-20260908.md): source-safe pseudopopulations, independent-source replication and endpoint controls; per-unit checks are complementary, not individual-significance gates. Exact same-trial claims retain their stronger recording contract.
- [Path-study status/deprecation ledger](docs/professor_updates/path_generalization_20260907/STATUS.md) and [presentation corrections](docs/professor_updates/path_generalization_20260907/CORRECTIONS.md).

The [V6–V9 teaching and audit report](docs/reports/place195-v6-v9-autoresearch-20260906.md)
remains the accepted historical account of geometry, support, cue bins, PCA, and GPU CEBRA.

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
