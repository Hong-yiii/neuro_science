"""Small shared execution operations, not a scientific runner.

Study-specific timestamps, JSON normalization, CSV and manifest schemas stay with
those studies. In particular, full-trial's fresh-directory exception is distinct.
"""

import hashlib
import shutil
import time
from collections.abc import Mapping
from pathlib import Path


def sha256_file(path: Path, *, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(chunk_size), b""):
            digest.update(block)
    return digest.hexdigest()


def ensure_fresh_dir(path: Path) -> None:
    """Endpoint/cue-time policy; never reuse an existing output directory."""
    if path.exists():
        raise RuntimeError(f"refusing to overwrite existing directory: {path}")
    path.mkdir(parents=True)


def check_deadline(deadline: float | None) -> None:
    """Full-trial/endpoint monotonic deadline (cue-time uses a wall clock)."""
    if deadline is not None and time.monotonic() >= deadline:
        raise RuntimeError("90-minute fitting deadline exceeded")


def snapshot_sources(destination: Path, paths: Mapping[str, Path]) -> None:
    """Copy the declared sources at their manifest paths, without certifying them."""
    for relative, source in paths.items():
        target = destination / relative
        if target.resolve() == destination.resolve() or destination.resolve() not in target.resolve().parents:
            raise ValueError(f"snapshot path escapes destination: {relative}")
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
