"""Minimal run manifests for the first CEBRA pilot framework."""

from __future__ import annotations

import hashlib
import json
import platform
import subprocess
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from importlib import metadata
from importlib.metadata import PackageNotFoundError
from pathlib import Path
from typing import Any

DEFAULT_PACKAGES = ("numpy", "h5py", "cebra", "torch", "scikit-learn", "scipy")


@dataclass(frozen=True)
class RunManifest:
    created_utc: str
    stage: str
    status: str
    scientific_status: str
    input_hashes: Mapping[str, str]
    artifact_hashes: Mapping[str, str]
    config: Mapping[str, Any]
    shape_summary: Mapping[str, Any]
    exclusion_summary: Mapping[str, Any]
    stop_conditions: Sequence[str]
    git_revision: str
    git_dirty: bool
    python_version: str
    package_versions: Mapping[str, str]
    graph_hash: str | None = None
    split_hash: str | None = None
    notes: Sequence[str] = field(default_factory=tuple)

    def to_json_dict(self) -> dict[str, Any]:
        return _jsonable(asdict(self))


def build_manifest(
    *,
    stage: str,
    status: str,
    scientific_status: str,
    input_hashes: Mapping[str, str] | None = None,
    artifact_hashes: Mapping[str, str] | None = None,
    config: Mapping[str, Any] | None = None,
    shape_summary: Mapping[str, Any] | None = None,
    exclusion_summary: Mapping[str, Any] | None = None,
    stop_conditions: Sequence[str] = (),
    graph_hash: str | None = None,
    split_hash: str | None = None,
    notes: Sequence[str] = (),
    package_names: Sequence[str] = DEFAULT_PACKAGES,
    cwd: Path | str = ".",
) -> RunManifest:
    """Collect reproducibility fields into one manifest object."""

    git = git_state(cwd)
    return RunManifest(
        created_utc=datetime.now(UTC).isoformat(),
        stage=stage,
        status=status,
        scientific_status=scientific_status,
        input_hashes=dict(input_hashes or {}),
        artifact_hashes=dict(artifact_hashes or {}),
        config=dict(config or {}),
        shape_summary=dict(shape_summary or {}),
        exclusion_summary=dict(exclusion_summary or {}),
        stop_conditions=tuple(stop_conditions),
        git_revision=git["revision"],
        git_dirty=git["dirty"],
        python_version=platform.python_version(),
        package_versions=package_versions(package_names),
        graph_hash=graph_hash,
        split_hash=split_hash,
        notes=tuple(notes),
    )


def require_pilot_output_path(
    output_dir: Path | str,
    cwd: Path | str = ".",
) -> Path:
    """Resolve a run path strictly below ignored ``outputs/cebra_pilot``."""

    root_result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=Path(cwd),
        capture_output=True,
        text=True,
        check=False,
    )
    if root_result.returncode != 0:
        raise ValueError("pilot outputs require a Git workspace")
    root = Path(root_result.stdout.strip()).resolve()
    base = (root / "outputs" / "cebra_pilot").resolve()
    candidate = Path(output_dir)
    path = (
        candidate.resolve() if candidate.is_absolute() else (root / candidate).resolve()
    )
    try:
        relative_run = path.relative_to(base)
    except ValueError as exc:
        raise ValueError(f"output directory must be below {base}: {path}") from exc
    if not relative_run.parts:
        raise ValueError(
            "output directory must name a new run below outputs/cebra_pilot"
        )

    ignored = subprocess.run(
        ["git", "check-ignore", "-q", str(path)],
        cwd=root,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    if ignored.returncode != 0:
        raise ValueError(f"pilot output directory is not Git-ignored: {path}")
    return path


def create_output_dir(output_dir: Path | str) -> Path:
    """Create a new pilot run directory and fail if it already exists."""

    path = require_pilot_output_path(output_dir)
    if path.exists():
        raise FileExistsError(
            f"refusing to overwrite existing output directory: {path}"
        )
    path.mkdir(parents=True)
    return path


def write_manifest_file(output_dir: Path | str, manifest: RunManifest) -> Path:
    """Write ``manifest.json`` inside an already-created run directory."""

    output_path = require_pilot_output_path(output_dir)
    manifest_path = output_path / "manifest.json"
    if manifest_path.exists():
        raise FileExistsError(
            f"refusing to overwrite existing manifest: {manifest_path}"
        )
    manifest_path.write_text(
        json.dumps(manifest.to_json_dict(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return manifest_path


def write_run_manifest(output_dir: Path | str, manifest: RunManifest) -> Path:
    """Create a new output directory and write its manifest."""

    path = create_output_dir(output_dir)
    return write_manifest_file(path, manifest)


def git_state(cwd: Path | str = ".") -> dict[str, Any]:
    """Return the current Git revision and dirty flag without failing outside Git."""

    root = Path(cwd)
    try:
        revision = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=root,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        status = subprocess.check_output(
            ["git", "status", "--short"],
            cwd=root,
            text=True,
            stderr=subprocess.DEVNULL,
        )
    except (OSError, subprocess.CalledProcessError):
        return {"revision": "unavailable", "dirty": True}
    return {"revision": revision, "dirty": bool(status.strip())}


def package_versions(packages: Sequence[str] = DEFAULT_PACKAGES) -> dict[str, str]:
    """Collect installed package versions, recording absent optional packages."""

    versions: dict[str, str] = {}
    for package in packages:
        try:
            versions[package] = metadata.version(package)
        except PackageNotFoundError:
            versions[package] = "not-installed"
    return versions


def sha256_file(path: Path | str) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path | str, payload: Mapping[str, Any]) -> Path:
    out = Path(path).resolve()
    require_pilot_output_path(out.parent)
    if out.exists():
        raise FileExistsError(f"refusing to overwrite existing file: {out}")
    out.write_text(
        json.dumps(_jsonable(payload), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return out


def _jsonable(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, tuple | list):
        return [_jsonable(item) for item in value]
    if isinstance(value, set | frozenset):
        return sorted(_jsonable(item) for item in value)
    return value
