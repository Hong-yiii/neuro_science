#!/usr/bin/env python3
"""Small offline checks for the professor-review presentation widgets."""

from __future__ import annotations

import json
import math
import re
import subprocess
import sys
import tempfile
from pathlib import Path

EXPECTED_IDS = [
    *(f"endpoint-time_t1-step250-seed{s}" for s in range(3)),
    *(f"endpoint-time_t1-step1000-seed{s}" for s in range(3)),
    *(f"endpoint-pca8-seed{s}" for s in range(3)),
]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text())
    except (OSError, ValueError) as error:
        raise AssertionError(f"Cannot read saved evidence: {path}: {error}") from error
    require(isinstance(value, dict), f"Expected JSON object: {path}")
    return value


def finite_point(point: object) -> bool:
    return (
        isinstance(point, list)
        and len(point) == 3
        and all(isinstance(v, (int, float)) and math.isfinite(v) for v in point)
    )


def check_payload(cwd: Path) -> None:
    payload = read_json(cwd / "payload.json")
    require(
        payload.get("sourceRunIds") == EXPECTED_IDS,
        "source run IDs are not the accepted curated values",
    )
    runs = payload.get("runs")
    if not isinstance(runs, list) or len(runs) != 9:
        raise AssertionError("payload must contain 9 curated runs")
    ids = [run["id"] for run in runs]
    require(sorted(ids) == sorted(EXPECTED_IDS), "payload run id set mismatch")
    for run in runs:
        require(
            "metrics" not in run, f"decoder metric leaked into payload: {run['id']}"
        )
        for split_name, expected_count in (("train", 480), ("development", 240)):
            split = run["splits"][split_name]
            require(
                split["count"] == expected_count,
                f"{run['id']} {split_name} count mismatch",
            )
            require(
                len(split["coords"]) == expected_count,
                f"{run['id']} {split_name} coords mismatch",
            )
            require(
                len(split["labels"]) == expected_count,
                f"{run['id']} {split_name} labels mismatch",
            )
            require(
                len(split["reuse"]) == expected_count,
                f"{run['id']} {split_name} reuse mismatch",
            )
            require(
                all(finite_point(point) for point in split["coords"]),
                f"{run['id']} {split_name} non-finite coordinate",
            )
            require(
                all(
                    isinstance(label, int) and 0 <= label < 30
                    for label in split["labels"]
                ),
                f"{run['id']} {split_name} label out of range",
            )


def check_losses(cwd: Path) -> None:
    losses = read_json(cwd / "loss-curves.json")
    endpoint = losses["endpoint"]["traces"]
    joint = losses["joint"]["traces"]
    require(len(endpoint) == 3, "endpoint loss trace count mismatch")
    require(len(joint) == 6, "joint loss trace count mismatch")
    require(
        all(len(trace["points"]) == 3000 for trace in endpoint),
        "endpoint loss points must preserve 3000 steps",
    )
    require(
        all(len(trace["points"]) == 1000 for trace in joint),
        "joint loss points must preserve 1000 steps",
    )
    require(
        losses["endpoint"]["config"]["markers"] == [250, 1000],
        "endpoint checkpoint markers missing",
    )
    for source in losses["provenance"]:
        path = source["path"]
        if "/worlds/" in path:
            require(
                "/worlds/00_observed/" in path,
                f"non-observed world leaked into loss provenance: {path}",
            )
            require(
                "null" not in path,
                f"null-world path leaked into loss provenance: {path}",
            )


def check_widgets(cwd: Path) -> None:
    viewer = (cwd / "viewer.html").read_text()
    ids = re.findall(r'\bid="([^"]+)"', viewer)
    require(bool(ids) and len(ids) == len(set(ids)), "missing or duplicate viewer IDs")
    require(
        all(value.startswith("w-") for value in ids), "viewer IDs must use w- prefix"
    )
    require(
        "<script" not in viewer and "@@" not in viewer,
        "renderer owns data/script integration",
    )
    combined = (
        viewer + (cwd / "widgets.css").read_text() + (cwd / "widgets.js").read_text()
    )
    blocked = [
        "<script src=",
        "<link ",
        "fetch(",
        "XMLHttpRequest",
        "import(",
        "https://",
        "http://",
    ]
    for token in blocked:
        require(token not in combined, f"external resource token found: {token}")
    for svg_name in ("endpoint-loss.svg", "joint-loss.svg"):
        svg = (cwd / svg_name).read_text()
        require(
            "<svg" in svg and "<script" not in svg and "href=" not in svg,
            f"unsafe or malformed {svg_name}",
        )


def check_node(cwd: Path) -> None:
    result = subprocess.run(
        ["node", "--check", "widgets.js"], cwd=cwd, text=True, capture_output=True
    )
    require(
        result.returncode == 0, result.stderr or result.stdout or "node --check failed"
    )


def check_sources(cwd: Path) -> None:
    """Re-extract saved artifacts in disposable storage and compare every output byte."""
    with tempfile.TemporaryDirectory(prefix="prof-review-recheck-") as tmp:
        subprocess.run(
            [
                sys.executable,
                str(cwd / "extract.py"),
                "--root",
                str(cwd.parents[2]),
                "--out",
                tmp,
            ],
            check=True,
            timeout=60,
        )
        for name in (
            "payload.json",
            "loss-curves.json",
            "endpoint-loss.svg",
            "joint-loss.svg",
        ):
            require(
                (Path(tmp) / name).read_bytes() == (cwd / name).read_bytes(),
                f"saved source re-extraction differs: {name}",
            )
    print(
        "source replay passed: all curated coordinates, loss points, provenance and SVG bytes"
    )


def main() -> None:
    require(sys.argv[1:] in ([], ["--sources"]), "Usage: self_check.py [--sources]")
    cwd = Path(__file__).resolve().parent
    check_payload(cwd)
    check_losses(cwd)
    check_widgets(cwd)
    check_node(cwd)
    require(
        finite_point([1, 2, 3])
        and not finite_point([1, 2])
        and not finite_point([1, 2, math.nan]),
        "finite-coordinate guard regression",
    )
    if sys.argv[1:]:
        check_sources(cwd)
    print(
        "self-check passed: 9 viewer runs, preserved loss traces, unique w-* controls, offline assets, node syntax ok"
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # noqa: BLE001 - tiny standalone check, fail loud.
        print(f"self-check failed: {exc}", file=sys.stderr)
        raise
