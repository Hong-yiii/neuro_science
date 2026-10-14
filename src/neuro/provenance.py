"""Current source identities for the three packaged readout studies.

This explicit, audited closure includes package initializers and the
actively required helper modules. It reads source only when called.
It is not an approval, a historical hash substitution, or a portable environment.
"""

from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


def study_sources(study_path: Path) -> dict[str, Path]:
    """Active closure plus retained CLI aliases needed by current source snapshots."""
    name = study_path.stem
    if name not in {"full_trial_transfer", "endpoint_time_readout", "cue_time_readout"}:
        raise ValueError(f"unknown readout study: {name}")
    sources = {
        "src/neuro/__init__.py",
        "src/neuro/studies/__init__.py",
        "src/neuro/execution.py",
        "src/neuro/provenance.py",
        "src/neuro/raw_io.py",
        "src/neuro/neural_inputs.py",
        "src/neuro/cebra_solver.py",
        "src/neuro/place195_split_access.py",
        "src/neuro/studies/full_trial_transfer.py",
        f"src/neuro/studies/{name}.py",
        "scripts/__init__.py",
        "scripts/cebra_full_trial_transfer.py",
        f"scripts/cebra_{name}.py",
    }
    if name == "cue_time_readout":
        sources.add("src/neuro/geometry.py")
    paths = {relative: REPOSITORY_ROOT / relative for relative in sorted(sources)}
    if study_path.resolve() != paths[f"src/neuro/studies/{name}.py"].resolve():
        raise ValueError("study implementation is outside this source checkout")
    for path in paths.values():
        if not path.is_file():
            raise FileNotFoundError(f"missing current source: {path}")
    return paths
