# Neuroscience: CEBRA retrospective and evidence

## Start with the report

- **[Current report](report/README.md)** — manuscript, feedback and publishing commands.
- **[Standalone reading milestone](report/retrospective-frozen-20261012.html)** —
  download raw HTML and open locally. A pre-existing local checksum difference is
  preserved and remains flagged; see the report README.
- **[Research history by week](history/README.md)** — what happened, conclusions,
  offline reports and links to each study's protocol/evidence.

The notebook will be one companion to the report, using the same maintained
scientific implementation. It has not been built; no new fitting is queued.

## Code and working structure

```text
report/                 current manuscript and presentation checks
history/week-.../       weekly overview → studies → reading artifacts
src/neuro/              scientific implementation and genuine shared objects
scripts/                launch/compatibility layer; legacy bodies still being migrated
docs/                   living methods, dataset, direction and recovery
```

The [first shared extraction](src/neuro/README.md) is the place195 split-access
guard: validation, filtered readers and audit objects, shared by existing studies.
It is not a generic utilities framework. Remaining scientific bodies in `scripts/`
are explicitly migration debt, not the intended architecture.

[Migration scope and checks](docs/reorganization.md) distinguish completed physical
moves from remaining full-package/code work. Eleven historical reading files have
moved byte-for-byte; old paths are compatibility symlinks. Source packages and
hash-bound protocols remain in place in this slice. [Script map](scripts/README.md)
explains which commands need private artifacts or scientific execution approval.

## Scientific safeguards and next direction

- [Analysis contract](docs/analysis-contract.md) and [dataset card](docs/dataset-card.md)
- [Future latent-model agenda](docs/cebra-observability-agenda-20261011.md) — proposal only
- [Workspace/recovery](docs/workspace.md) and [agent instructions](AGENTS.md)

Endpoint decoding, binary path-component decoding and full ordered-route prediction
are different questions; full ordered-route prediction was not evaluated. H1 remains
unresolved; H2 is removed. Cross-session pseudopopulations are not simultaneous
trial-specific populations. Historical source exposure and selection limits remain.

## Protected local material

`data/`, `outputs/`, `scratch/`, `work/`, local PDFs and session history are not
cleanup targets. Git cannot recover ignored private inputs/models. Preserve the
three retained review worktrees. `Hippocampus.jl/` and `PyHipp/` remain unchanged
submodules; do not upgrade or remove them as part of filing.
