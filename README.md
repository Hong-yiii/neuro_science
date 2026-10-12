# Neuro Science Workspace

Canonical working copy: `~/neuro_science`. **Current focus: the retrospective and
its supporting evidence.** Early trial plans are archived, not an active queue.

## Read the report

- **[Current manuscript package](docs/reports/cebra-retrospective-20261012/README.md)** — source, presentation checks, feedback and download instructions.
- **[Frozen whole-file reading copy](docs/reports/cebra-retrospective-20261012/retrospective-frozen-20261012.html)** — all figures embedded and versioned. Download the raw HTML from GitHub and open it locally; no build or server required.
- **[Evidence actually used by the report](docs/reports/README.md)** — endpoint, path-component, decoder and geometry studies, with their original protocols and limitations.
- **[Remaining editorial feedback](docs/reports/cebra-retrospective-20261012/feedback-20261012.md)** — freezing the reading copy did not mark every request complete.

The manuscript concerns CEBRA-Time and relevant baselines. Endpoint decoding,
binary interior-component decoding and full ordered-route prediction are different
questions; the last was not evaluated. Historical source studies remain unchanged,
including variants excluded from this manuscript. H1 remains unresolved; H2 is removed.

## Work on the report without running experiments

The [publishing workflow](docs/reports/cebra-retrospective-20261012/README.md#edit-and-build)
uses existing figures/aggregates and produces one standalone HTML. It does not
fit models, replay private predictions or fill missing analyses automatically.
See the [script and test map](scripts/README.md) before executing other tools.

**Next:** sharpen the report, then create an interpretable, high-observability
Jupyter notebook. The [next-work contract](docs/reports/cebra-retrospective-20261012/README.md#next-work-report-first-then-notebook)
records the remaining decisions and scope; no new fitting is queued.

## Planning and safeguards

- [Future latent-model / observability agenda](docs/cebra-observability-agenda-20261011.md): proposed direction, not an approved experiment.
- [Retrospective evidence/coverage blueprint](docs/reports/cebra-research-synthesis-20261011.md): supporting audit, not a competing reading version.
- [Workspace and recovery](docs/workspace.md), [agent instructions](AGENTS.md), [analysis contract](docs/analysis-contract.md) and [dataset card](docs/dataset-card.md).

The prior prospective-path goal is not the default next run. CEBRA is central but
not a required winner; new data access, fitting and reanalysis need separate approval.

## Background and archive

- [Filed early plans and initial-trial records](docs/reports/archive/early-work-20261012/README.md).
- [Learning](learning/README.md), [papers](papers/README.md), `context/` and [dated notes](notes/sessions/README.md).
- [Reorganization proposal and applied scope](docs/repo-reorganization-plan-20261012.md).

Initial-trial code is not automatically dead code: some pilot helpers and tests
are still dependencies of the report-backed pipeline. Keep them at their existing
paths unless a reviewed migration preserves imports, coverage and provenance.

## Local data and external repositories

`data/`, `outputs/`, `scratch/` and `work/` contain protected local data, scientific
artifacts, runtimes and three retained review worktrees. Ignored does not mean
expendable. Git is not an off-host backup of these contents. Do not prune them.

`Hippocampus.jl/` and `PyHipp/` remain submodules with their own histories. For a
fresh clone only, initialize them with `git submodule update --init --recursive`.
Do not update their revisions as part of documentation cleanup.
