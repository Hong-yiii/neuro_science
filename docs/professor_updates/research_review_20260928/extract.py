#!/usr/bin/env python3
"""Extract isolated presentation payloads from saved Git-backed artifacts only.

No raw data, checkpoints, model fitting, projection fitting, or third-party packages.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import math
import re
from pathlib import Path
from statistics import mean
from typing import Any, cast

SPLITS = ("train", "development")
SEEDS = (0, 1, 2)
MODELS = (
    ("time250", "endpoint-time_t1-step250", "CEBRA-Time, 250 updates"),
    ("time1000", "endpoint-time_t1-step1000", "CEBRA-Time, 1000 updates"),
    ("pca8", "endpoint-pca8", "PCA8 saved baseline"),
)
EXPECTED_SOURCE_IDS = [
    f"{prefix}-seed{seed}" for _, prefix, _ in MODELS for seed in SEEDS
]
ROOT_REL_ATLAS = Path("docs/reports/cebra-latent-atlas/atlas.html")
ENDPOINT_ROOT = Path("outputs/start-goal-autoresearch-20260907/02-cebra")
JOINT_ROOT = Path(
    "outputs/cebra-full-trial-transfer-20260924/biological-run-20260924T162913Z"
)
JOINT_OBSERVED = JOINT_ROOT / "worlds/00_observed"
SVG_NS = "http://www.w3.org/2000/svg"


class ExtractError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ExtractError(message)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def rel(root: Path, path: Path) -> str:
    return str(path.resolve().relative_to(root.resolve()))


def finite_number(value: Any, label: str) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError) as exc:
        raise ExtractError(f"non-numeric {label}: {value!r}") from exc
    require(math.isfinite(out), f"non-finite {label}")
    return out


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text())
    except (OSError, ValueError) as error:
        raise ExtractError(f"Cannot read saved JSON: {path}: {error}") from error


def extract_atlas_json(root: Path) -> dict[str, Any]:
    path = root / ROOT_REL_ATLAS
    text = path.read_text()
    match = re.search(r'<script[^>]*\bid="data"[^>]*>(.*?)</script>', text, re.S)
    if match is None:
        raise ExtractError(f"missing embedded atlas JSON in {ROOT_REL_ATLAS}")
    try:
        data = cast(dict[str, Any], json.loads(match.group(1)))
    except ValueError as error:
        raise ExtractError("Malformed embedded atlas JSON") from error
    require(isinstance(data, dict), "atlas payload is not an object")
    require(isinstance(data.get("runs"), list), "atlas runs missing")
    require(
        isinstance(data.get("pairs"), list) and len(data["pairs"]) == 30,
        "atlas endpoint pairs missing",
    )
    expected_pairs = [[s, g] for s in range(1, 7) for g in range(1, 7) if s != g]
    require(data["pairs"] == expected_pairs, "atlas endpoint-pair order changed")
    return data


def clean_fractions(values: Any, label: str) -> list[float]:
    require(
        isinstance(values, list) and len(values) >= 3, f"missing fractions for {label}"
    )
    return [finite_number(v, f"{label} fraction {i}") for i, v in enumerate(values[:3])]


def clean_coords(values: Any, count: int, label: str) -> list[list[float]]:
    require(
        isinstance(values, list) and len(values) == count,
        f"{label} coordinate count mismatch",
    )
    out: list[list[float]] = []
    for i, row in enumerate(values):
        require(
            isinstance(row, list) and len(row) == 3, f"{label} coordinate {i} is not 3D"
        )
        out.append(
            [finite_number(row[j], f"{label} coordinate {i}.{j}") for j in range(3)]
        )
    return out


def clean_labels(values: Any, count: int, label: str) -> list[int]:
    require(
        isinstance(values, list) and len(values) == count,
        f"{label} labels count mismatch",
    )
    out: list[int] = []
    for i, value in enumerate(values):
        require(
            isinstance(value, int) and 0 <= value < 30,
            f"{label} label {i} out of range",
        )
        out.append(value)
    return out


def clean_reuse(values: Any, count: int, label: str) -> list[float]:
    require(
        isinstance(values, list) and len(values) == count,
        f"{label} reuse count mismatch",
    )
    return [finite_number(v, f"{label} reuse {i}") for i, v in enumerate(values)]


def clean_support(value: Any, split: str) -> dict[str, Any]:
    require(isinstance(value, dict), f"missing support for {split}")
    keys = (
        "pseudorows",
        "session_blocks_per_row",
        "unique_sources_used",
        "max_source_reuse",
        "unique_source_combinations",
        "mean_source_reuse_per_row_range",
    )
    for key in keys:
        require(key in value, f"support.{split}.{key} missing")
    for key in keys[:-1]:
        require(
            isinstance(value[key], int) and value[key] >= 0,
            f"support.{split}.{key} is not a count",
        )
    rng = value["mean_source_reuse_per_row_range"]
    require(
        isinstance(rng, list) and len(rng) == 2,
        f"support.{split}.mean_source_reuse_per_row_range bad",
    )
    return {
        "pseudorows": value["pseudorows"],
        "sessionBlocksPerRow": value["session_blocks_per_row"],
        "uniqueSourcesUsed": value["unique_sources_used"],
        "maxSourceReuse": value["max_source_reuse"],
        "uniqueSourceCombinations": value["unique_source_combinations"],
        "meanSourceReusePerRowRange": [
            finite_number(rng[0], f"support.{split}.reuse range low"),
            finite_number(rng[1], f"support.{split}.reuse range high"),
        ],
    }


def build_viewer_payload(root: Path) -> dict:
    atlas = extract_atlas_json(root)
    by_id = {r.get("id"): r for r in atlas["runs"] if isinstance(r, dict)}
    runs = []
    for model, prefix, label in MODELS:
        for seed in SEEDS:
            source_id = f"{prefix}-seed{seed}"
            r = by_id.get(source_id)
            if r is None:
                raise ExtractError(f"missing atlas run {source_id}")
            require(
                r.get("lane") == "endpoint" and r.get("seed") == seed,
                f"bad atlas identity for {source_id}",
            )
            require(
                "metrics" in r, "atlas schema changed before metrics omission check"
            )
            spaces = r.get("spaces", {})
            whole = spaces.get("whole") if isinstance(spaces, dict) else None
            if not isinstance(whole, dict):
                raise ExtractError(f"missing whole-cue space for {source_id}")
            require(
                whole.get("projection") == "training-fitted display PC1–3",
                f"unexpected projection for {source_id}",
            )
            require(
                whole.get("ambient_dimension") == 80,
                f"unexpected whole-cue feature dimension for {source_id}",
            )
            split_payload: dict[str, dict] = {}
            all_coords: list[list[float]] = []
            for split, count in (("train", 480), ("development", 240)):
                views = r.get("views", {})
                view = views.get(split) if isinstance(views, dict) else None
                if not isinstance(view, dict):
                    raise ExtractError(f"missing {split} view for {source_id}")
                coords = clean_coords(
                    view.get("whole"), count, f"{source_id}.{split}.whole"
                )
                labels = clean_labels(view.get("labels"), count, f"{source_id}.{split}")
                reuse = clean_reuse(view.get("reuse"), count, f"{source_id}.{split}")
                space_splits = whole.get("splits", {})
                stats = (
                    space_splits.get(split) if isinstance(space_splits, dict) else None
                )
                if not isinstance(stats, dict):
                    raise ExtractError(f"missing whole stats for {source_id}.{split}")
                all_coords.extend(coords)
                split_payload[split] = {
                    "count": count,
                    "coords": coords,
                    "labels": labels,
                    "reuse": reuse,
                    "retainedEnergy": finite_number(
                        stats.get("retained_energy_training_center"),
                        f"{source_id}.{split}.retained_energy_training_center",
                    ),
                    "pcFractions": clean_fractions(
                        stats.get("fractions"), f"{source_id}.{split}"
                    ),
                    "support": clean_support(
                        (
                            r.get("support", {})
                            if isinstance(r.get("support", {}), dict)
                            else {}
                        ).get(split),
                        split,
                    ),
                }
            extent = max(math.sqrt(sum(v * v for v in p)) for p in all_coords)
            require(extent > 0, f"zero display extent for {source_id}")
            runs.append(
                {
                    "id": source_id,
                    "model": model,
                    "modelLabel": label,
                    "seed": seed,
                    "projection": whole["projection"],
                    "ambientDimension": 80,
                    "extent": extent,
                    "splits": split_payload,
                }
            )
    source_path = root / ROOT_REL_ATLAS
    return {
        "version": 1,
        "artifact": "curated-saved-evidence-20260928",
        "pairs": atlas["pairs"],
        "sourceRunIds": EXPECTED_SOURCE_IDS,
        "runs": runs,
        "caveats": [
            "Each dot is one complete synthetic whole-cue row: 80 saved features projected to three display PCs.",
            "Display PCA was previously fitted on training coordinates in the saved atlas; this extractor does not refit or project raw data.",
            "The common canvas extent includes development coordinates only so both panels fit on the same scale; it is not a PCA fit or analysis step.",
            "Dots are synthetic pseudopopulation rows with source reuse, not simultaneous biological population states, physical paths, or an H1b test.",
        ],
        "provenance": {
            "atlasHtml": {
                "path": rel(root, source_path),
                "sha256": sha256(source_path),
            },
            "coordinatePrecision": "saved atlas values rounded to 5 decimals",
            "omitted": "decoder metrics and full atlas menus intentionally omitted to avoid a leaderboard",
        },
    }


def read_csv_points(
    path: Path,
    expected_header: list[str],
    expected_steps: int,
    require_temperature: bool = False,
) -> list[list[float]]:
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        require(
            reader.fieldnames == expected_header,
            f"unexpected CSV header for {path}: {reader.fieldnames}",
        )
        points: list[list[float]] = []
        for index, row in enumerate(reader, start=1):
            step = index
            require(
                row["step"] == str(step),
                f"non-contiguous or malformed step in {path}: expected {step}",
            )
            if require_temperature:
                require(
                    finite_number(row["temperature"], f"temperature {path}:{step}")
                    == 1.0,
                    f"temperature not 1 at {path}:{step}",
                )
            points.append([step, finite_number(row["total"], f"loss {path}:{step}")])
    require(
        len(points) == expected_steps, f"wrong step count for {path}: {len(points)}"
    )
    return points


def read_losses(root: Path) -> dict:
    sources: list[dict] = []
    endpoint_traces = []
    for seed in SEEDS:
        folder = root / ENDPOINT_ROOT / f"time_t1_seed{seed}"
        config_path = folder / "config.json"
        loss_path = folder / "loss.csv"
        cfg = read_json(config_path)
        require(
            cfg.get("seed") == seed
            and cfg.get("steps") == 3000
            and cfg.get("batch_size") == 256
            and cfg.get("temperature") == 1
            and cfg.get("mode") == "time"
            and cfg.get("dim") == 8
            and isinstance(cfg.get("whole"), bool)
            and not cfg["whole"],
            f"unexpected endpoint CEBRA config for seed {seed}",
        )
        points = read_csv_points(loss_path, ["step", "total"], 3000)
        endpoint_traces.append(
            {
                "id": f"endpoint-time_t1-seed{seed}",
                "seed": seed,
                "arm": "time_t1",
                "points": points,
            }
        )
        for path in (config_path, loss_path):
            sources.append({"path": rel(root, path), "sha256": sha256(path)})

    locked_path = root / JOINT_ROOT / "locked_config.json"
    locked = read_json(locked_path)
    enc = locked.get("encoder", {}) if isinstance(locked, dict) else {}
    require(locked.get("seeds") == [0, 1, 2], "joint locked_config seeds changed")
    require(
        enc.get("iterations") == 1000
        and enc.get("batch_size") == 256
        and enc.get("temperature") == 1
        and enc.get("offset") == 1,
        "joint encoder locked_config changed",
    )
    sources.append({"path": rel(root, locked_path), "sha256": sha256(locked_path)})
    joint_traces = []
    for seed in SEEDS:
        for arm in ("cue_time", "full_time"):
            path = root / JOINT_OBSERVED / f"seed{seed}/encoders/{arm}/loss_trace.csv"
            require(
                "worlds/00_observed" in str(path), f"not observed-world path: {path}"
            )
            points = read_csv_points(
                path,
                ["step", "total", "pos", "neg", "temperature"],
                1000,
                require_temperature=True,
            )
            joint_traces.append(
                {
                    "id": f"joint-{arm}-seed{seed}",
                    "seed": seed,
                    "arm": arm,
                    "points": points,
                }
            )
            sources.append({"path": rel(root, path), "sha256": sha256(path)})
    return {
        "version": 1,
        "artifact": "curated-saved-evidence-20260928",
        "smoothing": {"blockAverageUpdates": 25, "fullPointsPreserved": True},
        "endpoint": {
            "title": "Endpoint CEBRA-Time saved encoder training loss",
            "config": {
                "steps": 3000,
                "batchSize": 256,
                "temperature": 1,
                "seeds": [0, 1, 2],
                "markers": [250, 1000],
            },
            "traces": endpoint_traces,
        },
        "joint": {
            "title": "Observed-world joint cue/navigation saved encoder training loss",
            "config": {
                "steps": 1000,
                "batchSize": 256,
                "temperature": 1,
                "seeds": [0, 1, 2],
                "arms": ["cue_time", "full_time"],
                "world": "00_observed",
            },
            "traces": joint_traces,
        },
        "provenance": sources,
        "caveat": "Training InfoNCE curves only; not validation prediction log loss and not evidence that lower loss means a better biological representation.",
    }


def block_average(
    points: list[list[float]], block: int = 25
) -> list[tuple[float, float]]:
    out = []
    for i in range(0, len(points), block):
        chunk = points[i : i + block]
        out.append((mean(p[0] for p in chunk), mean(p[1] for p in chunk)))
    return out


def mean_trace(traces: list[dict]) -> list[list[float]]:
    require(bool(traces), "empty mean trace")
    steps = [p[0] for p in traces[0]["points"]]
    for trace in traces[1:]:
        require(
            [p[0] for p in trace["points"]] == steps, "loss traces use different steps"
        )
    return [
        [step, mean(trace["points"][i][1] for trace in traces)]
        for i, step in enumerate(steps)
    ]


def scale(
    value: float, lo: float, hi: float, pixels_lo: float, pixels_hi: float
) -> float:
    if hi == lo:
        return (pixels_lo + pixels_hi) / 2
    return pixels_lo + (value - lo) * (pixels_hi - pixels_lo) / (hi - lo)


def path_data(
    points: list[tuple[float, float]],
    x0: float,
    x1: float,
    y0: float,
    y1: float,
    xmin: float,
    xmax: float,
    ymin: float,
    ymax: float,
) -> str:
    parts = []
    for i, (x, y) in enumerate(points):
        px = scale(x, xmin, xmax, x0, x1)
        py = scale(y, ymin, ymax, y1, y0)
        parts.append(("M" if i == 0 else "L") + f"{px:.2f} {py:.2f}")
    return " ".join(parts)


def make_svg(
    title: str,
    desc: str,
    traces: list[dict],
    marks: list[int],
    arms: list[str],
    arm_labels: dict[str, str],
) -> str:
    width, height = 920, 470
    left, right, top, bottom = 72, 24, 52, 124
    x0, x1 = left, width - right
    y0, y1 = top, height - bottom
    all_points = [point for trace in traces for point in trace["points"]]
    xmin, xmax = 0, max(p[0] for p in all_points)
    ymin, ymax = min(p[1] for p in all_points), max(p[1] for p in all_points)
    pad = (ymax - ymin) * 0.08 or 1.0
    ymin -= pad
    ymax += pad
    colors = {"time_t1": "#416db0", "cue_time": "#416db0", "full_time": "#168477"}
    dashes = {0: "", 1: "6 5", 2: "2 5"}
    title_id = (
        "w-svg-title-" + re.sub(r"[^a-z0-9-]+", "-", title.lower()).strip("-")[:40]
    )
    desc_id = title_id + "-desc"
    chunks = [
        f'<svg class="w-loss-svg" xmlns="{SVG_NS}" role="img" aria-labelledby="{title_id}" aria-describedby="{desc_id}" viewBox="0 0 {width} {height}">',
        "<style>.w-loss-svg text{font-family:system-ui,sans-serif;fill:#17324d} .w-loss-svg .axis{stroke:#46627d;stroke-width:1.2} .w-loss-svg .grid{stroke:#d7e4eb;stroke-width:1} .w-loss-svg .mean{fill:none;stroke-width:3.2;stroke-linecap:round;stroke-linejoin:round} .w-loss-svg .seed{fill:none;stroke-width:1.3;stroke-linecap:round;stroke-linejoin:round;opacity:.5}</style>",
        f'<title id="{title_id}">{html.escape(title)}</title>',
        f'<desc id="{desc_id}">{html.escape(desc)}</desc>',
        '<rect width="100%" height="100%" rx="18" fill="#fff8ed"/>',
        f'<text x="{left}" y="28" font-size="18" font-weight="700">{html.escape(title)}</text>',
        f'<text x="{left}" y="47" font-size="12">25-update block averages; full traces retained in the embedded loss-data JSON.</text>',
    ]
    for frac in (0, 0.25, 0.5, 0.75, 1):
        y = y1 - frac * (y1 - y0)
        value = ymin + frac * (ymax - ymin)
        chunks.append(
            f'<line class="grid" x1="{x0}" y1="{y:.2f}" x2="{x1}" y2="{y:.2f}"/>'
        )
        chunks.append(
            f'<text x="{x0 - 10}" y="{y + 4:.2f}" text-anchor="end" font-size="11">{value:.2f}</text>'
        )
    for frac in (0, 0.25, 0.5, 0.75, 1):
        x = x0 + frac * (x1 - x0)
        step = xmin + frac * (xmax - xmin)
        chunks.append(
            f'<line class="grid" x1="{x:.2f}" y1="{y0}" x2="{x:.2f}" y2="{y1}"/>'
        )
        chunks.append(
            f'<text x="{x:.2f}" y="{y1 + 18}" text-anchor="middle" font-size="11">{step:.0f}</text>'
        )
    for mark in marks:
        mx = scale(mark, xmin, xmax, x0, x1)
        chunks.append(
            f'<line x1="{mx:.2f}" y1="{y0}" x2="{mx:.2f}" y2="{y1}" stroke="#b45309" stroke-width="1.5" stroke-dasharray="5 4"/>'
        )
        chunks.append(
            f'<text x="{mx + 4:.2f}" y="{y0 + 14}" font-size="11" fill="#7c2d12">step {mark}</text>'
        )
    chunks.append(f'<line class="axis" x1="{x0}" y1="{y1}" x2="{x1}" y2="{y1}"/>')
    chunks.append(f'<line class="axis" x1="{x0}" y1="{y0}" x2="{x0}" y2="{y1}"/>')
    chunks.append(
        f'<text x="{(x0 + x1) / 2:.2f}" y="{height - 30}" text-anchor="middle" font-size="13">training update</text>'
    )
    chunks.append(
        f'<text transform="translate(22 {(y0 + y1) / 2:.2f}) rotate(-90)" text-anchor="middle" font-size="13">InfoNCE total loss</text>'
    )

    for arm in arms:
        arm_traces = [t for t in traces if t["arm"] == arm]
        for trace in arm_traces:
            smooth = block_average(trace["points"])
            chunks.append(
                f'<path class="seed" d="{path_data(smooth, x0, x1, y0, y1, xmin, xmax, ymin, ymax)}" '
                f'stroke="{colors[arm]}" stroke-dasharray="{dashes.get(trace["seed"], "")}"/>'
            )
        smooth_mean = block_average(mean_trace(arm_traces))
        chunks.append(
            f'<path class="mean" d="{path_data(smooth_mean, x0, x1, y0, y1, xmin, xmax, ymin, ymax)}" stroke="{colors[arm]}"/>'
        )

    legend_x, legend_y = x0, height - 86
    for i, arm in enumerate(arms):
        y = legend_y + i * 18
        chunks.append(
            f'<line x1="{legend_x}" y1="{y}" x2="{legend_x + 32}" y2="{y}" stroke="{colors[arm]}" stroke-width="3.2"/>'
        )
        chunks.append(
            f'<text x="{legend_x + 40}" y="{y + 4}" font-size="12">{html.escape(arm_labels[arm])} mean; faint lines: seed0 solid, seed1 dashed, seed2 dotted</text>'
        )
    chunks.append(
        f'<text x="{x1}" y="{height - 12}" text-anchor="end" font-size="11">Training loss only — not validation prediction log loss.</text>'
    )
    chunks.append("</svg>\n")
    return "\n".join(chunks)


def write_outputs(root: Path, out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    payload = build_viewer_payload(root)
    loss_payload = read_losses(root)
    dump = {"sort_keys": True, "allow_nan": False, "separators": (",", ":")}
    (out / "payload.json").write_text(json.dumps(payload, **dump) + "\n")
    (out / "loss-curves.json").write_text(json.dumps(loss_payload, **dump) + "\n")
    endpoint_svg = make_svg(
        "Endpoint CEBRA-Time encoder loss",
        "Saved endpoint time_t1 loss.csv traces for seeds 0, 1, and 2; tau 1, batch 256, 3000 steps; vertical reference lines at the curated 250 and 1000 update checkpoints.",
        loss_payload["endpoint"]["traces"],
        [250, 1000],
        ["time_t1"],
        {"time_t1": "endpoint time_t1"},
    )
    joint_svg = make_svg(
        "Observed-world joint encoder losses",
        "Saved worlds/00_observed joint cue_time and full_time loss_trace.csv traces for seeds 0, 1, and 2; tau 1, batch 256, 1000 steps. Null worlds are intentionally excluded.",
        loss_payload["joint"]["traces"],
        [],
        ["cue_time", "full_time"],
        {"cue_time": "cue-only", "full_time": "joint cue/navigation"},
    )
    (out / "endpoint-loss.svg").write_text(endpoint_svg)
    (out / "joint-loss.svg").write_text(joint_svg)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root", type=Path, required=True, help="neuro_science repository root"
    )
    parser.add_argument(
        "--out", type=Path, required=True, help="output directory for payload/SVG files"
    )
    args = parser.parse_args()
    root = args.root.resolve()
    out = args.out.resolve()
    require(
        (root / ROOT_REL_ATLAS).is_file(),
        f"not a neuro_science root or missing {ROOT_REL_ATLAS}",
    )
    write_outputs(root, out)
    print(
        f"wrote payload.json, loss-curves.json, endpoint-loss.svg, joint-loss.svg to {out}"
    )


if __name__ == "__main__":
    main()
