# Neuroscience: CEBRA retrospective

A report-led research workspace: current interpretation up front, historical evidence
organized by week, and a reusable [scientific readout package](src/neuro/README.md).

## Start here

| Goal | Entry point |
| --- | --- |
| Read or edit the manuscript | **[Current report](report/README.md)** |
| Understand package engineering | **[Software design and Mermaid diagrams](docs/software-design.md)** — maintained as-built reference |
| Read the historical design preview | [Visual HTML overview](docs/codebase-design.html) — may lag current package; open locally |
| Follow the research chronology | **[Weekly history](history/README.md)** |
| Find methods, evidence or recovery | [Documentation map](docs/README.md) |

## Structure

```text
report/                 current manuscript, feedback and publishing tools
history/week-.../       weekly overview → studies → historical reading files
src/neuro/              scientific implementation and genuinely shared objects
scripts/                launch/compatibility layer; legacy scientific bodies remain
docs/                   living methods, evidence catalog and workspace recovery
```

**Implemented:** report promotion, seven weekly overviews, eleven byte-preserved HTML
moves, the shared split-access gate and a three-study `neuro.studies` package
(full-trial, endpoint-time and cue-time readouts) with thin legacy entry points.
**Still pending:** other scientific/evidence migrations and the audited legacy-helper
boundary. **Whether/how the future notebook uses this package remains open**,
depending on its needs and complexity; no notebook is implemented here.
See [migration status and checks](docs/reorganization.md); this is not a universal
pipeline rewrite. Shared code is factored by scientific meaning, not put into a
catch-all `utils.py`.

## Limits worth knowing

- The frozen reading file has a preserved pre-existing checksum difference. Its
  integrity test still fails; see [report status](report/README.md#frozen-whole-file-reading-milestone--october-12).
- Source-safe pseudopopulations are not simultaneous trial-specific recordings.
  Endpoint, binary-component and full ordered-route prediction are distinct;
  full ordered routes were not evaluated. H1 is unresolved; H2 is removed.
- No new fit is queued. [Scientific safeguards](docs/analysis-contract.md) and
  [future research proposals](docs/cebra-observability-agenda-20261011.md) stay separate.

Private `data/`, `outputs/`, `scratch/`, `work/`, PDFs, sessions and retained worktrees
are protected. Git cannot recover ignored models/data. `Hippocampus.jl/` and `PyHipp/`
remain unchanged submodules. See [workspace/recovery](docs/workspace.md) and
[agent instructions](AGENTS.md) before changing them.
