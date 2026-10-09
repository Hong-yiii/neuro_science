# Neuro Science Workspace

Canonical neuroscience workspace: `~/neuro_science`.
**Start here next session: [observability and CEBRA pivot — October9](docs/observability-pivot-20261009.md).**
Hongyi requested completing/merging PR15 and taking up the observability direction
in a new session. First clarify the lab's meaning of observability; candidate
within-cue and cross-phase transfer analyses are proposals, not completed work or
fit authorization. H1-led path work is no longer the default next task; H1 is not
declared false, and artificial-agent H2 remains removed.

Then read [workspace/recovery](docs/workspace.md) and the safeguards in the
[analysis contract](docs/analysis-contract.md). The [September27 direction](docs/project-direction.md)
and [research questions](docs/research-questions.md) retain the prior path framing.
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
- `docs/observability-pivot-20261009.md`: current next-session entry point, open observability definition and proposed work.
- `docs/project-direction.md`: prior September27/28 scope and scientific safeguards; links to the current handoff.
- `docs/research-questions.md`: retained prospective-path research framing.
- `docs/analysis-contract.md`: cue-population and subsequent-path data contract.
- `docs/getting-started-tasks.md`: individual onboarding and first-analysis tasks.
- `Hippocampus.jl/`: Julia analysis repo, tracked as a submodule on `updates6`.
- `PyHipp/`: older Python reference repo, tracked as a submodule.

## Current Project

The next priority is to formulate an observability-centered question with CEBRA:
what task information is recoverable and stable under recording/representation
constraints? This is a direction to develop, not an adopted dynamical model or
final thesis hypothesis. Raw/PCA references remain essential; CEBRA is not a
required winner. The lab's operational definition and the next protocol are open.

The completed path and endpoint studies remain separate historical evidence.
H1a (incremental path information) and H1b (its low-dimensional organization)
were not established, and the pivot is not evidence that they are absent.

**Use the [research handoff index](docs/reports/README.md)** (refreshed 2026-10-09):
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
See [`docs/research-questions.md`](docs/research-questions.md) for the historical path framing
and [`docs/analysis-contract.md`](docs/analysis-contract.md) for retained data/evaluation safeguards.
The [October9 handoff](docs/observability-pivot-20261009.md) controls next-session priorities.

## Submodules

The external repos are submodules so this workspace can track exactly which versions were used while preserving each repo's own history.

After cloning this parent workspace somewhere else, run:

```sh
git submodule update --init --recursive
```

## Data

Raw or formatted neuroscience data should live under `data/` unless a project needs a different layout. Data and generated analysis outputs are ignored by default so they do not accidentally enter git.
