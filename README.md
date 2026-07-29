# Neuro Science Workspace

This folder is the top-level home for neuroscience work, lab context, and references to analysis code.

## Layout

- `AGENTS.md`: working instructions for coding agents.
- `context/`: living notes, repo maps, and durable observations.
- `Hippocampus.jl/`: Julia analysis repo, tracked as a submodule on `updates6`.
- `PyHipp/`: older Python reference repo, tracked as a submodule.

## Submodules

The external repos are submodules so this workspace can track exactly which versions were used while preserving each repo's own history.

After cloning this parent workspace somewhere else, run:

```sh
git submodule update --init --recursive
```

## Data

Raw or formatted neuroscience data should live under `data/` unless a project needs a different layout. Data and generated analysis outputs are ignored by default so they do not accidentally enter git.

