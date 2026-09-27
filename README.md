# Neuro Science Workspace

Canonical neuroscience workspace: `~/neuro_science`.
**Start here next session: [agreed project direction — September27](docs/project-direction.md).**
Keep H1; remove H2. Narrow encoder comparisons to CEBRA-Time, cue-only versus
joint cue/navigation training and two checkpoints, with source-safe folds and
PCA/LDA baselines. **Decoder choice is open.** Component-level graph decoding is
the simpler assay; ordered graph-path prediction remains the desired capability.
This is an agreed scope update, not authorization to launch model fits.

Then read [research questions](docs/research-questions.md),
[analysis contract](docs/analysis-contract.md), and [workspace/recovery](docs/workspace.md).
[Consolidated PR #11](https://github.com/Hong-yiii/neuro_science/pull/11) merged the
studies; stacked #10 was closed as already included. The
[September26 review](docs/reports/research-reset-20260926/README.md)
([offline HTML](docs/reports/research-reset-20260926/review.html)) is the evidence
retrospective, not the new decision authority. Three review worktrees remain
under `work/` with retained artifacts; merging is not permission to remove them.

## Layout

- `AGENTS.md`: working instructions for coding agents.
- `context/`: living notes, repo maps, and durable observations.
- `learning/`: Hongyi's neuroscience learning path, explained from an ML/deep-learning background.
- `notes/data_inspection/`: durable findings from inspecting local datasets.
- `notes/sessions/`: dated session summaries, diagrams, decisions, and next steps.
- `papers/`: paper notes, reading queues, and references.
- `docs/project-direction.md`: agreed scope, open decisions, and next-session entry point.
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
possible low-dimensional organization. The artificial-agent comparison formerly
called H2 is removed from active scope, not retained as a stretch aim.
Place, view, and conjunctive analyses remain supporting validation and confound
checks rather than the primary question.

**Use the [research handoff index](docs/reports/README.md)** (refreshed 2026-09-27):
current synthesis, completed endpoint and path studies, portable teaching reports,
source-code preservation, verification, and explicit supersession labels.
Endpoint-condition decoding improved in later settings; neither that success nor
the nonpositive path analyses establish confirmatory H1 evidence. The original
holdout-exposure record remains in force.

- **Matched PCA comparison:** [PCA versus raw verdict](docs/reports/path-pca-matched/README.md), [offline HTML](docs/reports/path-pca-matched/report.html), and [evidence index](docs/reports/path-pca-matched/evidence.md). PCA improved historical loss by 0.007023 nats; both arms had 55% balanced accuracy and source sensitivity spanned both signs. All 26,266 fit instances replayed without fitting. Small exploratory method advantage, not robust biological generalization or H1 confirmation.
- **Historical September 8 preprocessing study:** [path-preprocessing report](docs/reports/path-preprocessing-autoresearch-20260908.md), [offline HTML](docs/reports/path-preprocessing-autoresearch-20260908.html), [agent brief](docs/reports/path-preprocessing-autoresearch-20260908-agent.md), and [September 9 review](docs/reports/path-preprocessing-review-20260909.md). Stronger regularization helped probability loss, but the historical result was 6→1-dominated and did not establish broad robustness. The prior verification replayed 82,283 model-fit instances with zero new fits.
- [Earlier cross-study synthesis](docs/reports/recent-learnings-20260908.md) and [agent brief](docs/reports/recent-learnings-20260908-agent.md).
- [PCA and below-chance explanation with plots](learning/place195-pca-and-below-chance-20260908.md).
- [Artifact preservation and verification](docs/reports/research-release-20260908.md): Git is not a backup of ignored data/models.
- [Path-generalization package](docs/professor_updates/path_generalization_20260907/README.md): corrected self-contained report, code, evidence and historical status labels. The study ran 342 CEBRA fits; cross-assembly checks of 50 observed encoders transferred across mixtures of training sources, but did not establish reliable source-pool generalization. Corrected family p is **19/21**; the cause of the gap is not uniquely established.
- [Earlier condition-level proposal](docs/reports/path-generalization-next-steps-20260908.md) (scope superseded by the agreed direction): source-safe pseudopopulations, independent-source replication and endpoint controls; per-unit checks are complementary, not individual-significance gates. Exact same-trial claims retain their stronger recording contract.
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
