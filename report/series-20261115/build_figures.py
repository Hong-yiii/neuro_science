#!/usr/bin/env python3
"""Render existing published aggregates; never execute notebooks or study code.

Run from the canonical checkout with its existing Python/numpy/matplotlib:
    PYTHONDONTWRITEBYTECODE=1 python report/series-20261115/build_figures.py

This is an editorial re-presentation of an exploratory study. It authenticates
published notebooks, figures, the frozen design and public assignment metadata
against a pinned revision. It extracts literal HTML tables / explorer JSON and
regenerates source-count distributions under the unchanged metadata-only embargo.
Public current/predecessor IDs are checked in memory but are never exported.
It does not read predictions, spike/event values, neural arrays or fitted models.
"""

from __future__ import annotations

import csv
from collections import Counter
import gzip
import hashlib
import io
import itertools
import json
import math
from pathlib import Path
import re
import struct
import subprocess
import sys
from html.parser import HTMLParser

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch, Rectangle
import numpy as np


ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
SOURCE = ROOT / "experiments/source_reuse_width_20261114/walkthrough_20261115/published"
HISTORICAL_TIME = ROOT / "docs/reports/cebra-endpoint-time-readout-20261006/figures/time_balanced_accuracy.png"
FROZEN_DESIGN = ROOT / "docs/experiments/source-reuse-width-20261114/design.json"
PUBLIC_METADATA = ROOT / "data/cue-source-v1"
REVISION = "a0ca80180e2bb52b90e499357d3d6965b26806da"
MANIFEST_SHA256 = "8ef3a28e687e657c6429632b6a2011bfaa57dfadd62ff94fc276f21bef9a9e93"
NOTEBOOKS = (
    "source_reuse_20261115.executed.ipynb",
    "population_width_20261115.executed.ipynb",
)
ARMS = ("B2", "B3", "B5", "U3", "Wmid", "Wfull")
ENCODERS = ("raw", "pca", "cebra", "native")
DECODERS = ("logistic", "svm", "knn", "lda")
HEADS = ("pair", "start", "goal")
WORLDS = tuple(f"permuted{i}" for i in range(61000, 61005))
REPEATS = (("observed", "0"), ("observed", "1"), ("observed", "2")) + tuple(
    (world, "0") for world in WORLDS
)
SCORE_KEYS = ("world", "seed", "arm", "encoder", "decoder", "head")
CONTRAST_KEYS = ("world", "seed", "before", "after", "encoder", "decoder", "head")
SCORE_COLUMNS = SCORE_KEYS + (
    "balanced_accuracy", "accuracy", "macro_f1", "log_loss", "train_BA",
    "train_development_gap",
)
CONTRAST_COLUMNS = CONTRAST_KEYS + ("delta_BA",)
DESIGN_COLUMNS = (
    "arm", "units", "sessions", "source_budget", "rows_per_class",
    "distinct_train_sources", "training_source_extra_draw_fraction",
    "overlapping_contributors",
)
ENCODER_LABELS = ("Raw", "PCA7", "CEBRA-Time7", "Native multisession7")
SHORT_ENCODER_LABELS = ("Raw", "PCA7", "Time7", "Native7")
DECODER_LABELS = ("Logistic", "RBF-SVM", "kNN5", "SVD-LDA")
COLORS = ("#176b8c", "#17845b", "#b46a19", "#7856a0")
ROSTER_COLORS = ("#246b94", "#399982", "#cf983a")
ROSTER_COLUMNS = (
    "roster", "available_development_sources", "available_train_sources",
    "development_singleton_pools", "minimum_development_sources",
    "minimum_train_sources", "session_aliases", "sessions", "units",
)
REALIZATION_COLUMNS = (
    "arm", "constructed_rows", "distinct_source_IDs", "min_uses", "max_uses",
    "repeated_whole_source_tuples",
)
PREFIT_COLUMNS = (
    "arm", "constant_columns", "distinct_train_sources", "overlapping_contributors",
    "rows_per_class", "seed", "sessions", "source_budget", "training_rank",
    "training_source_extra_draw_fraction", "units", "world",
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def authenticated_bytes(path: Path) -> bytes:
    data = path.read_bytes()
    pinned = subprocess.check_output(
        ["git", "show", f"{REVISION}:{relative(path)}"], cwd=ROOT
    )
    require(data == pinned, f"Source differs from pinned revision: {relative(path)}")
    return data


class TableParser(HTMLParser):
    """Extract one literal table, preserving each numeric cell's source text."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.rows: list[list[str]] = []
        self.row: list[str] | None = None
        self.cell: list[str] | None = None
        self.tables = 0

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            self.tables += 1
        elif tag == "tr":
            require(self.row is None, "Nested table row")
            self.row = []
        elif tag in ("th", "td"):
            require(self.cell is None and self.row is not None, "Malformed table cell")
            self.cell = []

    def handle_data(self, data):
        if self.cell is not None:
            self.cell.append(data)

    def handle_endtag(self, tag):
        if tag in ("th", "td"):
            require(self.cell is not None and self.row is not None, "Unmatched cell")
            self.row.append("".join(self.cell))
            self.cell = None
        elif tag == "tr":
            require(self.row is not None and self.cell is None, "Unmatched row")
            self.rows.append(self.row)
            self.row = None


def parse_table(html: str, columns: tuple[str, ...]) -> list[dict[str, str]]:
    parser = TableParser()
    parser.feed(html)
    parser.close()
    require(parser.tables == 1 and len(parser.rows) > 1, "Expected exactly one table")
    require(tuple(parser.rows[0]) == columns, "Unexpected table schema")
    require(all(len(row) == len(columns) for row in parser.rows), "Ragged table")
    return [dict(zip(columns, row, strict=True)) for row in parser.rows[1:]]


class IframeParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.srcdocs: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag == "iframe":
            attrs = dict(attrs)
            require(attrs.get("title") == "Complete confusion explorer", "Wrong iframe")
            self.srcdocs.append(attrs["srcdoc"])


def parse_explorer(html: str) -> tuple[list[dict], str]:
    parser = IframeParser()
    parser.feed(html)
    parser.close()
    require(len(parser.srcdocs) == 1, "Expected one confusion explorer")
    srcdoc = parser.srcdocs[0]
    matches = list(re.finditer(r"\bconst\s+records\s*=", srcdoc))
    require(len(matches) == 1, "Expected one literal records array")
    start = matches[0].end()
    records, end = json.JSONDecoder().raw_decode(srcdoc[start:])
    require(srcdoc[start + end:].startswith(";const host="), "Unexpected JSON boundary")
    require(isinstance(records, list), "Explorer records are not a list")
    return records, sha256(srcdoc.encode("utf-8"))


def html_output(notebook: dict, cell: int, output: int) -> str:
    value = notebook["cells"][cell]["outputs"][output]["data"]["text/html"]
    return value if isinstance(value, str) else "".join(value)


def deduplicate(rows: list[dict], keys: tuple[str, ...]) -> tuple[list[dict], int]:
    unique: dict[tuple, dict] = {}
    duplicates = 0
    for row in rows:
        key = tuple(row[k] for k in keys)
        if key in unique:
            require(row == unique[key], f"Non-identical duplicate: {key}")
            duplicates += 1
        else:
            unique[key] = row
    return sorted(unique.values(), key=lambda row: tuple(row[k] for k in keys)), duplicates


def write_csv(name: str, rows: list[dict], columns: tuple[str, ...] | None = None) -> Path:
    path = OUT / "data" / name
    require(bool(rows), f"Empty CSV: {name}")
    columns = columns or tuple(rows[0])
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return path


def configure_matplotlib() -> None:
    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 9,
        "axes.titlesize": 9, "axes.labelsize": 9,
        "xtick.labelsize": 8, "ytick.labelsize": 8, "legend.fontsize": 8,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.linewidth": 0.65, "xtick.major.width": 0.65, "ytick.major.width": 0.65,
        "pdf.fonttype": 42, "ps.fonttype": 42,
        "savefig.facecolor": "white", "figure.facecolor": "white",
    })


def save_figure(fig, stem: str) -> dict:
    # Fixed dates make PDFs reproducible; do not use tight cropping, which changes
    # the physical size used to interpret the 8–9 pt publication typography.
    sizes = [float(value) for value in fig.get_size_inches()]
    for suffix in ("pdf", "png"):
        kwargs = {"dpi": 220} if suffix == "png" else {
            "metadata": {"Creator": "build_figures.py", "CreationDate": None, "ModDate": None}
        }
        fig.savefig(OUT / "figures" / f"{stem}.{suffix}", **kwargs)
    require(b"/Subtype /Image" not in (OUT / "figures" / f"{stem}.pdf").read_bytes(),
            f"Expected an entirely vector PDF: {stem}")
    plt.close(fig)
    return {"width_inches": sizes[0], "height_inches": sizes[1], "png_dpi": 220,
            "pdf_raster_image_objects": 0}


def recent_svm(scores: dict[tuple, dict]) -> dict:
    fig, axes = plt.subplots(2, 4, figsize=(7, 4.65), sharey=True)
    fig.subplots_adjust(left=0.085, right=0.985, bottom=0.19, top=0.855,
                        wspace=0.19, hspace=0.70)
    fig.suptitle("Whole-cue RBF-SVM · nine ordered endpoint classes", y=0.985, fontsize=10)
    fig.text(0.085, 0.925, "17 columns: B2/B3/B5 = 2/3/5 sources per session/class; U3 = once-only",
             fontsize=8.5)
    fig.text(0.085, 0.505, "Population width: three sources per session/class", fontsize=8.5)
    for row_index, arms in enumerate((("B2", "B3", "B5", "U3"), ("B3", "Wmid", "Wfull"))):
        x = np.arange(len(arms))
        for encoder_index, encoder in enumerate(ENCODERS):
            ax = axes[row_index, encoder_index]
            color = COLORS[encoder_index]
            observations = np.array([
                [float(scores[("observed", str(seed), arm, encoder, "svm", "pair")]
                       ["balanced_accuracy"]) * 100 for arm in arms]
                for seed in range(3)
            ])
            for seed in range(3):
                ax.plot(x + (seed - 1) * 0.035, observations[seed], "o-", color=color,
                        alpha=0.43, linewidth=0.65, markersize=3.2, zorder=3)
            for world_index, world in enumerate(WORLDS):
                values = [float(scores[(world, "0", arm, encoder, "svm", "pair")]
                                ["balanced_accuracy"]) * 100 for arm in arms]
                ax.scatter(x + (world_index - 2) * 0.055, values, marker="x", s=16,
                           linewidths=0.8, color="#737373", alpha=0.9, zorder=2, clip_on=False)
            ax.plot(x, observations.mean(axis=0), "o-", color=color, linewidth=1.8,
                    markersize=4.1, markeredgecolor="white", markeredgewidth=0.35, zorder=4)
            ax.axhline(100 / 9, color="#555555", linestyle=(0, (2, 2)), linewidth=0.65)
            ax.set_ylim(0, 100)
            ax.set_yticks([0, 25, 50, 75, 100])
            ax.set_xlim(-0.35, len(arms) - 0.65)
            ax.set_xticks(x, arms if row_index == 0 else ["B3\n17", "Wmid\n49", "Wfull\n83"])
            ax.grid(axis="y", color="#e5e5e5", linewidth=0.55, zorder=0)
            letter = chr(ord("a") + row_index * 4 + encoder_index)
            label = ENCODER_LABELS[encoder_index]
            if encoder == "native":
                label = "Native7"
            ax.set_title(f"{letter}  {label}", loc="left", pad=7)
            if encoder_index == 0:
                ax.set_ylabel("Pair balanced accuracy (%)")
    fig.text(0.53, 0.105, "Columns (bottom row)", ha="center", fontsize=8)
    handles = [
        Line2D([], [], marker="o", color="#444444", alpha=0.43, linewidth=0.65,
               markersize=3.2, label="Observed seeds 0–2"),
        Line2D([], [], marker="o", color="#444444", linewidth=1.8, markersize=4.1,
               label="Observed mean"),
        Line2D([], [], marker="x", color="#737373", linestyle="None", markersize=4.2,
               label="Five label worlds (seed 0)"),
        Line2D([], [], color="#555555", linestyle=(0, (2, 2)), linewidth=0.65,
               label="Uniform reference (11.11%)"),
    ]
    fig.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.52, 0.005),
               ncol=2, frameon=False, columnspacing=1.7, handlelength=2.5)
    return save_figure(fig, "recent_svm")


def width_readouts(contrasts: list[dict]) -> tuple[dict, list[dict]]:
    transitions = (("B3", "Wmid"), ("Wmid", "Wfull"))
    lookup = {tuple(row[key] for key in CONTRAST_KEYS): row for row in contrasts}
    panels = []
    summary = []
    for before, after in transitions:
        grid = np.zeros((4, 4))
        for i, encoder in enumerate(ENCODERS):
            for j, decoder in enumerate(DECODERS):
                values = [float(lookup[("observed", str(seed), before, after, encoder,
                                       decoder, "pair")]["delta_BA"]) for seed in range(3)]
                mean = math.fsum(values) / 3
                grid[i, j] = mean * 100
                summary.append({
                    "before": before, "after": after, "encoder": encoder,
                    "decoder": decoder, "head": "pair", "observed_mean_delta_BA": mean,
                    "observed_mean_delta_percentage_points": mean * 100,
                    "observed_min_delta_percentage_points": min(values) * 100,
                    "observed_max_delta_percentage_points": max(values) * 100,
                    "positive_repeats": sum(value > 0 for value in values),
                    "zero_repeats": sum(value == 0 for value in values),
                    "computational_repeats": 3,
                })
        panels.append(grid)
    limit = max(abs(panel).max() for panel in panels)
    fig, axes = plt.subplots(1, 2, figsize=(7, 2.55))
    fig.subplots_adjust(left=0.11, right=0.89, bottom=0.22, top=0.80, wspace=0.38)
    titles = ("a  17 → 49 columns (Wmid − B3)", "b  49 → 83 columns (Wfull − Wmid)")
    for index, (ax, values) in enumerate(zip(axes, panels, strict=True)):
        edges = np.arange(5) - 0.5
        im = ax.pcolormesh(edges, edges, values, cmap="RdBu_r", vmin=-limit, vmax=limit,
                           shading="flat", rasterized=False)
        ax.set_xlim(-0.5, 3.5)
        ax.set_ylim(3.5, -0.5)
        ax.set_title(titles[index], pad=9, fontsize=8.5)
        ax.set_xticks(np.arange(4), DECODER_LABELS, fontsize=7.8)
        ax.set_yticks(np.arange(4), SHORT_ENCODER_LABELS, fontsize=8)
        ax.tick_params(length=0, pad=5)
        for spine in ax.spines.values():
            spine.set_visible(False)
        for i, j in itertools.product(range(4), repeat=2):
            ax.text(j, i, f"{values[i, j]:+.2f}", ha="center", va="center", fontsize=8.3,
                    color="white" if abs(values[i, j]) > limit * 0.60 else "#1d1d1d")
        ax.set_xticks(np.arange(-0.5, 4, 1), minor=True)
        ax.set_yticks(np.arange(-0.5, 4, 1), minor=True)
        ax.grid(which="minor", color="white", linewidth=1)
        ax.tick_params(which="minor", length=0)
    cax = fig.add_axes([0.92, 0.22, 0.016, 0.58])
    bar = fig.colorbar(im, cax=cax)
    bar.solids.set_rasterized(False)
    bar.ax.set_title("pp", fontsize=8, pad=5)
    bar.ax.tick_params(labelsize=7.5)
    fig.text(0.50, 0.035, "Pair balanced-accuracy change (pp) · mean of three matched repeats",
             ha="center", fontsize=8.5)
    return save_figure(fig, "width_readouts"), summary


def errors(record: dict) -> dict:
    matrix = np.asarray(record["counts"], dtype=int)
    normalized = matrix / matrix.sum(axis=1, keepdims=True) * 100
    labels = [label.replace("->", "→") for label in record["labels"]]
    fig = plt.figure(figsize=(7, 3.85))
    axes = [fig.add_axes([0.07, 0.20, 0.36, 0.66]),
            fig.add_axes([0.55, 0.20, 0.36, 0.66])]
    fig.suptitle("PCA7 / RBF-SVM · Wfull (83 columns), observed seed 0", y=0.985, fontsize=10)
    for index, (ax, values, high, title) in enumerate(zip(
        axes, (matrix, normalized), (8, 100),
        ("a  Constructed-row counts", "b  Row-normalized (%)"), strict=True,
    )):
        edges = np.arange(10) - 0.5
        im = ax.pcolormesh(edges, edges, values, cmap="Blues", vmin=0, vmax=high,
                           shading="flat", rasterized=False)
        ax.set_xlim(-0.5, 8.5)
        ax.set_ylim(8.5, -0.5)
        ax.set_aspect("equal")
        ax.set_title(title, fontsize=9, pad=8)
        ax.set_xticks(np.arange(9), labels, rotation=45, ha="right", rotation_mode="anchor")
        ax.set_yticks(np.arange(9), labels)
        ax.tick_params(length=0, labelsize=7.8)
        ax.set_xlabel("Predicted endpoint pair", fontsize=8.5)
        if index == 0:
            ax.set_ylabel("True endpoint pair", fontsize=8.5)
        for i, j in itertools.product(range(9), repeat=2):
            text = str(int(values[i, j])) if index == 0 else f"{values[i, j]:g}"
            ax.text(j, i, text, ha="center", va="center", fontsize=7.1,
                    color="white" if values[i, j] > high * 0.55 else "#252525")
        for spine in ax.spines.values():
            spine.set_visible(False)
        if index == 1:
            cax = fig.add_axes([0.93, 0.20, 0.012, 0.66])
            bar = fig.colorbar(im, cax=cax, ticks=[0, 25, 50, 75, 100])
            bar.solids.set_rasterized(False)
            bar.ax.tick_params(labelsize=7, length=2)
    fig.text(0.50, 0.035, "72 exposed-development constructed rows; eight per true class",
             ha="center", fontsize=8.5)
    return save_figure(fig, "errors")


def text_output(notebook: dict, cell: int, output: int) -> str:
    value = notebook["cells"][cell]["outputs"][output]["text"]
    return value if isinstance(value, str) else "".join(value)


def extract_methods(notebooks: dict, sources: list[dict]) -> dict:
    """Extract already displayed counts, checks and the complete displayed recipes."""
    rosters, realizations, prefit, recipes, blocks, observations = [], [], [], [], [], []
    for source in sources:
        name = Path(source["path"]).name
        notebook = notebooks[name]
        arm = "B2" if name.startswith("source_reuse") else "Wmid"
        for cell, output, columns, target, label in (
            (3, 1, ROSTER_COLUMNS, rosters, "Eligible current-source pools by frozen roster"),
            (7, 1, REALIZATION_COLUMNS, realizations, "Observed seed0 sampling realization"),
            (5, 1, PREFIT_COLUMNS, prefit, "Observed seed0 prefit checks"),
            (9, 2, ("block", "columns"), blocks, "First-case columns per session block"),
            (9, 4, ("constructed_row", "pair", "block", "source_choice"), recipes,
             "All displayed first-two-row source-choice ordinals"),
        ):
            html = html_output(notebook, cell, output)
            rows = parse_table(html, columns)
            if cell == 9:
                rows = [{"arm": arm, "seed": "0", **row} for row in rows]
            target.extend(rows)
            source["extractions"].append({
                "cell_index_zero_based": cell, "output_index_zero_based": output,
                "mime_type": "text/html", "table": label, "rows": len(rows),
                "html_sha256": sha256(html.encode("utf-8")),
            })
        shape_text = text_output(notebook, 5, 0)
        mask_text = text_output(notebook, 5, 2)
        shape = re.search(r"Fresh source tensor: \((\d+), (\d+), (\d+)\)", shape_text)
        mask = re.search(r"Observed source×unit entries: (\d+) of (\d+)", mask_text)
        require(shape is not None and mask is not None, "Missing published source/mask summary")
        observations.append(dict(zip(
            ("source_rows", "columns", "cue_bins", "observed_source_column_entries",
             "possible_source_column_entries"), map(int, (*shape.groups(), *mask.groups())), strict=True,
        )))
        for output, content in ((0, shape_text), (2, mask_text)):
            source["extractions"].append({
                "cell_index_zero_based": 5, "output_index_zero_based": output,
                "mime_type": "stream/text", "purpose": "Published tensor dimensions and observed-mask scalar",
                "text_sha256": sha256(content.encode("utf-8")),
            })
    rosters, nr = deduplicate(rosters, ("roster",))
    realizations, ns = deduplicate(realizations, ("arm",))
    prefit, nprefit = deduplicate(prefit, ("arm", "world", "seed"))
    require((len(rosters), nr, len(realizations), ns, len(prefit), nprefit) == (3, 3, 6, 1, 6, 6),
            "Unexpected duplicate methods-table coverage")
    require(observations[0] == observations[1], "Published mask summaries disagree")
    require(len(recipes) == 28 and len(blocks) == 14, "Published recipe coverage changed")
    require({row["pair"] for row in recipes} == {"1->2"}, "Example class changed")
    require({row["constructed_row"] for row in recipes} == {"0", "1"}, "Recipe rows changed")
    require(all(row["overlapping_contributors"] == "0" and row["constant_columns"] == "0"
                and int(row["training_rank"]) >= 7 for row in prefit), "Published prefit checks disagree")
    return {"rosters": rosters, "realizations": realizations, "prefit": prefit,
            "recipes": recipes, "blocks": blocks, "observation": observations[0]}


def regenerate_metadata_support(methods: dict) -> dict:
    """Count public assignments under the existing embargo; no study imports/values.

    This independently spells out population_grid.metadata's fixed identity rules.
    It does not optimize/select a new panel or export current/predecessor identities.
    """
    design_bytes = authenticated_bytes(FROZEN_DESIGN)
    design = json.loads(design_bytes)
    metadata_bytes = {}
    input_hashes = {relative(FROZEN_DESIGN): sha256(design_bytes)}
    for name, expected in design["metadata_sha256"].items():
        data = authenticated_bytes(PUBLIC_METADATA / name)
        require(sha256(data) == expected, f"Frozen metadata hash mismatch: {name}")
        metadata_bytes[name] = data
        input_hashes[relative(PUBLIC_METADATA / name)] = sha256(data)
    outer_rows = list(csv.DictReader(io.StringIO(gzip.decompress(metadata_bytes["outer_splits.csv.gz"]).decode())))
    inner = list(csv.DictReader(io.StringIO(gzip.decompress(metadata_bytes["inner_splits.csv.gz"]).decode())))
    outer = {row["source_trial_id"]: row for row in outer_rows}
    require(len(outer) == len(outer_rows), "Duplicate outer identity")
    require(len({row["source_trial_id"] for row in inner}) == len(inner), "Duplicate inner identity")
    units = json.loads(metadata_bytes["manifest.json"])["units"]
    sessions = sorted({unit["session_id"] for unit in units})
    aliases = {session: f"S{i + 1:02d}" for i, session in enumerate(sessions)}
    widths = Counter(aliases[unit["session_id"]] for unit in units)
    pairs = {f"{start}->{goal}" for start in range(1, 7) for goal in range(1, 7) if start != goal}
    for row in inner:
        current = outer[row["source_trial_id"]]
        previous = outer[current["previous_source_trial_id"]]
        require(current["split"] == previous["split"] == row["original_split"] == "train"
                and current["session_id"] == previous["session_id"] == row["session_id"]
                and int(current["trial_index"]) == int(previous["trial_index"]) + 1
                and row["label"] in pairs and row["split"] in {"train", "validation"},
                "Frozen current/predecessor metadata mismatch")
    protected = {
        identity for row in inner if row["split"] == "validation"
        for identity in (row["source_trial_id"], outer[row["source_trial_id"]]["previous_source_trial_id"])
    }
    retained = [row for row in inner if row["split"] == "validation" or not {
        row["source_trial_id"], outer[row["source_trial_id"]]["previous_source_trial_id"]
    } & protected]
    require((len(outer), len(inner), len(protected), len(inner) - len(retained))
            == (23901, 15553, 5872, 4427), "Global assignment/embargo accounting changed")
    original_counts = Counter(row["split"] for row in inner)
    retained_counts = Counter(row["split"] for row in retained)
    require(original_counts == {"train": 12288, "validation": 3265}
            and retained_counts == {"train": 7861, "validation": 3265}, "Global split totals changed")
    counts = Counter((aliases[row["session_id"]], row["label"], row["split"]) for row in retained)
    conditions = design["panel"]["conditions"]
    require(len(conditions) == 9 and len(units) == 195 and len(sessions) == 58, "Frozen inventory changed")
    rosters = design["rosters"]
    core, middle, full = (set(rosters[key]["session_aliases"]) for key in ("core", "middle", "full"))
    require(core < middle < full, "Rosters are not strictly nested")
    order = sorted(core) + sorted(middle - core) + sorted(full - middle)
    pool_rows, session_rows, summaries = [], [], []
    for alias in order:
        group = "core" if alias in core else "added_middle" if alias in middle else "added_full"
        for pair in conditions:
            for split in ("train", "validation"):
                pool_rows.append({"session_alias": alias, "columns": widths[alias], "roster_group": group,
                                  "pair": pair, "split": "development" if split == "validation" else split,
                                  "eligible_current_sources": counts[alias, pair, split]})
        train = sum(counts[alias, pair, "train"] for pair in conditions)
        dev = sum(counts[alias, pair, "validation"] for pair in conditions)
        session_rows.append({"session_alias": alias, "columns": widths[alias], "roster_group": group,
                             "available_train_sources": train, "available_development_sources": dev,
                             "available_total_sources": train + dev,
                             "within_session_source_column_entries": (train + dev) * widths[alias]})
    published_rosters = {row["roster"]: row for row in methods["rosters"]}
    for name in ("core", "middle", "full"):
        roster = rosters[name]
        train = [counts[alias, pair, "train"] for alias in roster["session_aliases"] for pair in conditions]
        dev = [counts[alias, pair, "validation"] for alias in roster["session_aliases"] for pair in conditions]
        summary = {"roster": name, "sessions": len(roster["session_aliases"]),
                   "columns": sum(widths[alias] for alias in roster["session_aliases"]),
                   "session_class_pools": len(train), "available_train_sources": sum(train),
                   "available_development_sources": sum(dev), "minimum_train_sources": min(train),
                   "minimum_development_sources": min(dev), "development_singleton_pools": dev.count(1)}
        for field in ("sessions", "available_train_sources", "available_development_sources",
                      "minimum_train_sources", "minimum_development_sources", "development_singleton_pools"):
            require(summary[field] == roster[field] == int(published_rosters[name][field]),
                    f"Recorded roster total differs: {name}/{field}")
        require(summary["columns"] == roster["units"] == int(published_rosters[name]["units"]),
                f"Roster width differs: {name}")
        summaries.append(summary)
    observation = methods["observation"]
    require(sum(row["available_total_sources"] for row in session_rows) == observation["source_rows"] == 1277,
            "Published source-row total differs from metadata")
    require(sum(row["columns"] for row in session_rows) == observation["columns"] == 83, "Column mismatch")
    require(sum(row["within_session_source_column_entries"] for row in session_rows)
            == observation["observed_source_column_entries"] == 5375, "Published observed-mask total mismatch")
    require(observation["source_rows"] * observation["columns"]
            == observation["possible_source_column_entries"] == 105991, "Possible-entry count mismatch")
    require(observation["cue_bins"] == 10, "Cue-bin count changed")
    return {"pool_rows": pool_rows, "session_rows": session_rows, "rosters": summaries,
            "conditions": conditions, "order": order, "input_hashes": input_hashes,
            "global_counts": {"outer_assignment_records": len(outer), "inner_records": len(inner),
                              "inner_train_before_embargo": original_counts["train"],
                              "inner_development_records": original_counts["validation"],
                              "protected_current_or_predecessor_ids": len(protected),
                              "embargoed_training_records": len(inner) - len(retained),
                              "training_records_after_embargo": retained_counts["train"]},
            "classification": "Regenerated metadata distribution of the unchanged accepted design, not a new study or neural-mask read"}


def source_support(metadata: dict) -> dict:
    lookup = {(row["session_alias"], row["pair"], row["split"]): row["eligible_current_sources"]
              for row in metadata["pool_rows"]}
    widths = {row["session_alias"]: row["columns"] for row in metadata["session_rows"]}
    order, conditions = metadata["order"], metadata["conditions"]
    fig, axes = plt.subplots(1, 2, figsize=(7, 6.4), sharey=True)
    fig.subplots_adjust(left=0.17, right=0.94, bottom=0.23, top=0.89, wspace=0.10)
    fig.suptitle("Eligible current sources in the fixed nine-class task", y=0.985, fontsize=10)
    for index, (ax, split) in enumerate(zip(axes, ("train", "development"), strict=True)):
        values = np.array([[lookup[alias, pair, split] for pair in conditions] for alias in order])
        im = ax.pcolormesh(np.arange(10) - 0.5, np.arange(21) - 0.5, values,
                           cmap="Blues", vmin=0, vmax=9, shading="flat", rasterized=False,
                           edgecolors="white", linewidth=0.35)
        ax.set_xlim(-0.5, 8.5)
        ax.set_ylim(19.5, -0.5)
        ax.set_xticks(range(9), [pair.replace("->", "→") for pair in conditions], rotation=45,
                      ha="right", rotation_mode="anchor", fontsize=8)
        ax.set_yticks(range(20), [f"{alias}  ({widths[alias]})" for alias in order], fontsize=8)
        ax.tick_params(length=0, pad=4)
        ax.set_xlabel("Ordered endpoint pair", fontsize=8.5)
        ax.set_title(f"{'a' if index == 0 else 'b'}  {'Training after embargo' if index == 0 else 'Exposed development'}",
                     fontsize=9, pad=8)
        for row, column in itertools.product(range(20), range(9)):
            value = values[row, column]
            ax.text(column, row, str(value), ha="center", va="center", fontsize=8,
                    color="white" if value >= 6 else "#1f2933")
            if split == "development" and value == 1:
                ax.add_patch(Rectangle((column - 0.46, row - 0.46), 0.92, 0.92,
                                       fill=False, edgecolor="#a9650a", linewidth=0.8))
        for boundary in (2.5, 10.5):
            ax.axhline(boundary, color="#292929", linewidth=1.15)
        for spine in ax.spines.values():
            spine.set_visible(False)
    axes[0].set_ylabel("Session alias (recorded columns)", fontsize=8.5, labelpad=5)
    cax = fig.add_axes([0.36, 0.075, 0.39, 0.022])
    bar = fig.colorbar(im, cax=cax, orientation="horizontal", ticks=range(10))
    bar.solids.set_rasterized(False)
    bar.ax.tick_params(labelsize=8, length=2)
    fig.text(0.555, 0.025, "Eligible current sources per session × class", ha="center", fontsize=8.5)
    fig.text(0.17, 0.935, "Row groups: core (3) | added to middle (8) | added to full (9)", fontsize=8.5)
    fig.text(0.17, 0.13, "Outlined 1s: singleton development pools (41 of 180 at full width)", fontsize=8)
    return save_figure(fig, "source_support")


def source_structure(metadata: dict, observation: dict) -> dict:
    rows = metadata["session_rows"]
    xedges = np.r_[0, np.cumsum([row["columns"] for row in rows])]
    yedges = np.r_[0, np.cumsum([row["available_total_sources"] for row in rows])]
    values = np.zeros((20, 20))
    for index, row in enumerate(rows):
        values[index, index] = {"core": 1, "added_middle": 2, "added_full": 3}[row["roster_group"]]
    fig = plt.figure(figsize=(7, 2.6))
    ax = fig.add_axes([0.09, 0.24, 0.53, 0.64])
    ax.pcolormesh(xedges, yedges, values, cmap=ListedColormap(["#eeeeee", *ROSTER_COLORS]),
                  vmin=0, vmax=3, shading="flat", rasterized=False)
    ax.set_xlim(0, 83)
    ax.set_ylim(1277, 0)
    ax.set_xticks([0, 17, 49, 83])
    ax.set_yticks([0, 216, 753, 1277])
    ax.set_xlabel("Recorded columns (grouped by session)", fontsize=8.5)
    ax.set_ylabel("Available source rows", fontsize=8.5)
    ax.set_title("Session membership from public metadata", fontsize=9, pad=7)
    for i in (3, 11):
        ax.axvline(xedges[i], color="#666666", linewidth=0.55, linestyle=(0, (2, 2)))
        ax.axhline(yedges[i], color="#666666", linewidth=0.55, linestyle=(0, (2, 2)))
    observed, possible = observation["observed_source_column_entries"], observation["possible_source_column_entries"]
    fig.text(0.68, 0.86, f"{observed:,} / {possible:,}", fontsize=13, weight="bold")
    fig.text(0.68, 0.70, f"source–column entries observed\n({observed / possible:.2%}); ten bins each", fontsize=8.5)
    fig.text(0.68, 0.47, "Gray: other-session columns\nunavailable for that source.\nUnavailable ≠ zero spikes.", fontsize=8.5,
             linespacing=1.5)
    fig.legend(handles=[Patch(facecolor=color, label=label) for color, label in zip(
        ROSTER_COLORS, ("Core", "Added to middle", "Added to full"), strict=True)],
        loc="lower center", bbox_to_anchor=(0.49, -0.005), frameon=False, ncol=3, fontsize=8)
    return save_figure(fig, "source_structure")


def assembly_recipe(methods: dict) -> dict:
    fig = plt.figure(figsize=(7, 3.1))
    fig.suptitle("Actual first two training-row recipes · observed seed 0 · pair 1→2", y=0.985, fontsize=10)
    for arm, bounds, title, title_y in (
        ("B2", [0.12, 0.53, 0.38, 0.19], "a  B2: 17 columns across 3 sessions", 0.865),
        ("Wmid", [0.12, 0.15, 0.84, 0.17], "b  Wmid: 49 columns across 11 sessions", 0.445),
    ):
        ax = fig.add_axes(bounds)
        block_rows = [row for row in methods["blocks"] if row["arm"] == arm]
        aliases = [row["block"] for row in block_rows]
        widths = [int(row["columns"]) for row in block_rows]
        lookup = {(int(row["constructed_row"]), row["block"]): int(row["source_choice"])
                  for row in methods["recipes"] if row["arm"] == arm}
        colors = [ROSTER_COLORS[0] if alias in {"S16", "S27", "S34"} else ROSTER_COLORS[1] for alias in aliases]
        for row, column in itertools.product(range(2), range(len(aliases))):
            ax.add_patch(Rectangle((column - 0.5, row - 0.5), 1, 1, facecolor=colors[column],
                                   alpha=0.18, edgecolor="white", linewidth=1))
            ax.text(column, row, str(lookup[row, aliases[column]]), ha="center", va="center", fontsize=10)
        ax.set_xlim(-0.5, len(aliases) - 0.5)
        ax.set_ylim(1.5, -0.5)
        ax.set_xticks(range(len(aliases)), [f"{alias}\n{width} col" for alias, width in zip(aliases, widths, strict=True)],
                      fontsize=8)
        ax.xaxis.tick_top()
        ax.set_yticks([0, 1], ["Row 0", "Row 1"], fontsize=9)
        ax.tick_params(length=0, pad=3)
        fig.text(0.12, title_y, title, fontsize=9)
        for spine in ax.spines.values():
            spine.set_visible(False)
    fig.text(0.55, 0.54, "Number = source-choice ordinal\nwithin that session × class pool.\nEqual numbers across sessions\ndo not identify the same trial.",
             fontsize=8.5, linespacing=1.35)
    fig.text(0.12, 0.065, "Each selected block contributes all its columns and all ten cue bins to the constructed row.", fontsize=8.5)
    fig.text(0.12, 0.02, "Cells have equal display width; recorded column counts are shown above. No neural values are plotted.", fontsize=8)
    return save_figure(fig, "assembly_recipe")


def sampling_realization(methods: dict, design: list[dict], metadata: dict) -> tuple[dict, list[dict]]:
    availability = {row["roster"]: row for row in metadata["rosters"]}
    selected = {row["arm"]: row for row in design}
    realized = {row["arm"]: row for row in methods["realizations"]}
    rows = []
    for arm in ARMS:
        roster = "middle" if arm == "Wmid" else "full" if arm == "Wfull" else "core"
        a, d, r = availability[roster], selected[arm], realized[arm]
        nrows, sessions = int(r["constructed_rows"]), int(d["sessions"])
        nselected, repeats = int(d["distinct_train_sources"]), int(r["repeated_whole_source_tuples"])
        require(nselected == int(r["distinct_source_IDs"]), "Selected-ID tables disagree")
        require(abs((1 - nselected / (nrows * sessions)) - float(d["training_source_extra_draw_fraction"])) < 1e-15,
                "Published repetition fraction disagrees with source/block counts")
        rows.append({"arm": arm, "world": "observed", "seed": 0, "roster": roster,
                     "columns": int(d["units"]), "sessions": sessions,
                     "eligible_train_sources": a["available_train_sources"], "selected_train_sources": nselected,
                     "constructed_train_rows": nrows, "training_source_block_uses": nrows * sessions,
                     "minimum_uses_per_selected_source": int(r["min_uses"]),
                     "maximum_uses_per_selected_source": int(r["max_uses"]),
                     "unique_whole_source_tuples": nrows - repeats, "repeated_whole_source_tuples": repeats,
                     "source_extra_draw_fraction": d["training_source_extra_draw_fraction"],
                     "eligible_development_sources": a["available_development_sources"],
                     "development_session_class_pools": a["session_class_pools"],
                     "development_singleton_pools": a["development_singleton_pools"]})
    fig, axes = plt.subplots(2, 2, figsize=(7, 4.7))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.12, top=0.88, hspace=0.75, wspace=0.34)
    fig.suptitle("Sampling realization: sources, block uses and constructed rows are different counts", y=0.995, fontsize=9.5)
    x = np.arange(6)
    ax = axes[0, 0]
    for offset, field, color, label in ((-0.18, "eligible_train_sources", "#d2d8dc", "Eligible"),
                                       (0.18, "selected_train_sources", COLORS[0], "Selected")):
        values = [row[field] for row in rows]
        ax.bar(x + offset, values, width=0.34, color=color, label=label)
    for i, row in enumerate(rows):
        ax.text(i, row["eligible_train_sources"] + 20,
                f"{row['eligible_train_sources']}/{row['selected_train_sources']}",
                ha="center", fontsize=7)
    ax.set_ylim(0, 1100)
    ax.set_ylabel("Distinct current-source IDs", fontsize=8)
    ax.set_title("a  Eligible / selected training source IDs", loc="left", fontsize=8.5)
    ax.legend(frameon=False, fontsize=7, loc="upper left", ncol=2, handlelength=1)
    ax = axes[0, 1]
    unique = [row["unique_whole_source_tuples"] for row in rows]
    repeated = [row["repeated_whole_source_tuples"] for row in rows]
    ax.bar(x, unique, bottom=repeated, color="#d2d8dc", label="Unique whole tuples")
    ax.bar(x, repeated, color="#b46a19", label="Extra identical tuples")
    for i, row in enumerate(rows):
        ax.text(i, row["constructed_train_rows"] + 4, f"{row['constructed_train_rows']}", ha="center", fontsize=7)
        ax.text(i, repeated[i] / 2 if repeated[i] > 10 else repeated[i] + 7,
                str(repeated[i]), ha="center", va="center", fontsize=8,
                color="white" if repeated[i] > 10 else "#262626")
    ax.set_ylim(0, 205)
    ax.set_ylabel("Constructed training rows", fontsize=8)
    ax.set_title("b  Repeated whole tuples (orange)", loc="left", fontsize=8.5)
    ax.legend(frameon=False, fontsize=6.8, loc="upper left", ncol=2, handlelength=1, columnspacing=0.8)
    ax = axes[1, 0]
    for i, row in enumerate(rows):
        low, high = row["minimum_uses_per_selected_source"], row["maximum_uses_per_selected_source"]
        ax.plot([i, i], [low, high], color=COLORS[0], linewidth=3, solid_capstyle="round")
        ax.scatter([i, i], [low, high], color=COLORS[0], s=15)
        ax.text(i, high + 0.35, str(low) if low == high else f"{low}–{high}", ha="center", fontsize=8)
    ax.set_ylim(0, 10)
    ax.set_yticks(range(0, 11, 2))
    ax.set_ylabel("Uses per selected training source", fontsize=8)
    ax.set_title("c  Actual min–max uses; no uncertainty interval", loc="left", fontsize=8.5)
    ax = axes[1, 1]
    totals = [row["session_class_pools"] for row in metadata["rosters"]]
    singletons = [row["development_singleton_pools"] for row in metadata["rosters"]]
    ax.bar(range(3), totals, color="#d2d8dc")
    ax.bar(range(3), singletons, color="#b46a19")
    for i, (singleton, total) in enumerate(zip(singletons, totals, strict=True)):
        ax.text(i, total + 6, f"{singleton}/{total}", ha="center", fontsize=8)
    ax.set_ylim(0, 220)
    ax.set_ylabel("Development session × class pools", fontsize=8)
    ax.set_title("d  Singleton development pools (orange)", loc="left", fontsize=8.5)
    ax.set_xticks(range(3), ["Core\n17 col", "Middle\n49 col", "Full\n83 col"])
    for ax in axes.flat:
        ax.grid(axis="y", color="#e6e6e6", linewidth=0.5)
        ax.set_axisbelow(True)
    for ax in (axes[0, 0], axes[0, 1], axes[1, 0]):
        ax.set_xticks(x, ARMS)
    fig.text(0.53, 0.015, "Panels b–c: observed seed 0; use ranges describe assembly, not biological uncertainty.",
             ha="center", fontsize=8)
    return save_figure(fig, "sampling_realization"), rows


def svm_head_tables(scores: list[dict]) -> tuple[list[dict], list[dict]]:
    selected = [{key: row[key] for key in (*SCORE_KEYS, "train_BA", "balanced_accuracy", "train_development_gap")}
                for row in scores if row["world"] == "observed" and row["decoder"] == "svm"]
    require(len(selected) == 216, "SVM head diagnostic coverage changed")
    require(all(abs(float(row["train_BA"]) - float(row["balanced_accuracy"])
                    - float(row["train_development_gap"])) <= 1e-15 for row in selected),
            "Published SVM training/development gaps disagree with scores")
    means = []
    for arm, encoder, head in itertools.product(ARMS, ENCODERS, HEADS):
        rows = [row for row in selected if (row["arm"], row["encoder"], row["head"]) == (arm, encoder, head)]
        require({row["seed"] for row in rows} == {"0", "1", "2"}, "Missing SVM head repeat")
        summary = {"arm": arm, "encoder": encoder, "decoder": "svm", "head": head, "computational_repeats": 3}
        for field in ("train_BA", "balanced_accuracy", "train_development_gap"):
            values = [float(row[field]) for row in rows]
            summary[f"mean_{field}"] = math.fsum(values) / 3
            summary[f"min_{field}"] = min(values)
            summary[f"max_{field}"] = max(values)
        means.append(summary)
    return selected, means


def main() -> None:
    manifest_bytes = authenticated_bytes(SOURCE / "manifest.json")
    require(sha256(manifest_bytes) == MANIFEST_SHA256, "Unrecognized publication manifest")
    manifest = json.loads(manifest_bytes)
    all_scores, all_contrasts, all_design = [], [], []
    sources = []
    notebooks = {}
    explorer_records = None
    for name in NOTEBOOKS:
        raw = authenticated_bytes(SOURCE / name)
        require(sha256(raw) == manifest["files_sha256"][name], "Notebook manifest hash mismatch")
        notebook = json.loads(raw)
        notebooks[name] = notebook
        source = {"path": relative(SOURCE / name), "sha256": sha256(raw), "extractions": []}
        for cell, output, columns, target, label in (
            (33, 6, SCORE_COLUMNS, all_scores, "Every case score"),
            (33, 7, CONTRAST_COLUMNS, all_contrasts, "Every matched seed/world contrast"),
            (7, 0, DESIGN_COLUMNS, all_design, "Arm construction summary"),
        ):
            html = html_output(notebook, cell, output)
            rows = parse_table(html, columns)
            target.extend(rows)
            source["extractions"].append({
                "cell_index_zero_based": cell, "output_index_zero_based": output,
                "mime_type": "text/html", "table": label, "rows": len(rows),
                "html_sha256": sha256(html.encode("utf-8")),
            })
        if name.startswith("population_width"):
            html = html_output(notebook, 31, 17)
            explorer_records, srcdoc_hash = parse_explorer(html)
            source["extractions"].append({
                "cell_index_zero_based": 31, "output_index_zero_based": 17,
                "mime_type": "text/html", "structure": "iframe srcdoc / literal const records JSON",
                "available_aggregate_matrices": len(explorer_records),
                "html_sha256": sha256(html.encode("utf-8")), "srcdoc_sha256": srcdoc_hash,
                "retained_selection": "observed seed0, PCA/SVM, pair, development; B3/Wmid/Wfull",
            })
        sources.append(source)

    scores, duplicate_scores = deduplicate(all_scores, SCORE_KEYS)
    contrasts, duplicate_contrasts = deduplicate(all_contrasts, CONTRAST_KEYS)
    design, duplicate_design = deduplicate(all_design, ("arm",))
    methods = extract_methods(notebooks, sources)
    metadata = regenerate_metadata_support(methods)
    require((len(scores), duplicate_scores) == (2304, 384), "Unexpected score coverage")
    require((len(contrasts), duplicate_contrasts) == (2688, 0), "Unexpected contrast coverage")
    require((len(design), duplicate_design) == (6, 1), "Unexpected arm coverage")
    expected_scores = {
        (world, seed, arm, encoder, decoder, head)
        for (world, seed), arm, encoder, decoder, head in itertools.product(
            REPEATS, ARMS, ENCODERS, DECODERS, HEADS
        )
    }
    score_lookup = {tuple(row[key] for key in SCORE_KEYS): row for row in scores}
    require(set(score_lookup) == expected_scores, "Score identity grid incomplete")
    contrast_pairs = {("B2", "B3"), ("B3", "B5"), ("B2", "B5"), ("U3", "B3"),
                      ("B3", "Wmid"), ("Wmid", "Wfull"), ("B3", "Wfull")}
    expected_contrasts = {
        (world, seed, before, after, encoder, decoder, head)
        for (world, seed), (before, after), encoder, decoder, head in itertools.product(
            REPEATS, contrast_pairs, ENCODERS, DECODERS, HEADS
        )
    }
    require({tuple(row[key] for key in CONTRAST_KEYS) for row in contrasts} == expected_contrasts,
            "Contrast identity grid incomplete")
    maximum_contrast_error = 0.0
    for row in contrasts:
        prefix = row["world"], row["seed"]
        suffix = row["encoder"], row["decoder"], row["head"]
        delta = (float(score_lookup[prefix + (row["after"],) + suffix]["balanced_accuracy"])
                 - float(score_lookup[prefix + (row["before"],) + suffix]["balanced_accuracy"]))
        maximum_contrast_error = max(maximum_contrast_error, abs(delta - float(row["delta_BA"])))
    require(maximum_contrast_error <= 1e-15, "Published contrasts do not match case scores")

    require(explorer_records is not None and len(explorer_records) == 2304, "Unexpected explorer size")
    selected = [record for record in explorer_records
                if record["world"] == "observed" and record["seed"] == 0
                and record["encoder"] == "pca" and record["decoder"] == "svm"
                and record["head"] == "pair" and record["split"] == "development"]
    require(len(selected) == 3 and {record["arm"] for record in selected} == {"B3", "Wmid", "Wfull"},
            "Unexpected confusion selection")
    confusion_rows, recall_rows = [], []
    for record in selected:
        counts = record["counts"]
        require(len(record["labels"]) == 9 and len(counts) == 9
                and all(len(row) == 9 for row in counts), "Wrong confusion shape")
        require(all(type(value) is int and value >= 0 for row in counts for value in row),
                "Counts must be nonnegative integers")
        require(all(sum(row) == 8 for row in counts), "A pair class does not contain eight rows")
        require(sum(map(sum, counts)) == 72, "Wrong development total")
        ba = math.fsum(counts[i][i] / 8 for i in range(9)) / 9
        source_ba = float(score_lookup[("observed", "0", record["arm"], "pca", "svm", "pair")]
                         ["balanced_accuracy"])
        require(abs(ba - source_ba) <= 1e-15, "Matrix BA differs from published score")
        for i, true_label in enumerate(record["labels"]):
            recall_rows.append({"arm": record["arm"], "seed": 0, "encoder": "pca",
                                "decoder": "svm", "class": true_label, "correct": counts[i][i],
                                "constructed_rows": 8, "recall": counts[i][i] / 8})
            for j, predicted_label in enumerate(record["labels"]):
                confusion_rows.append({"arm": record["arm"], "seed": 0, "encoder": "pca",
                                       "decoder": "svm", "head": "pair", "split": "development",
                                       "true_class": true_label, "predicted_class": predicted_label,
                                       "count": counts[i][j], "row_normalized": counts[i][j] / 8})

    (OUT / "data").mkdir(parents=True, exist_ok=True)
    (OUT / "figures").mkdir(parents=True, exist_ok=True)
    written = [write_csv("case_scores.csv", scores, SCORE_COLUMNS),
               write_csv("matched_contrasts.csv", contrasts, CONTRAST_COLUMNS),
               write_csv("arm_design.csv", design, DESIGN_COLUMNS),
               write_csv("pca_svm_seed0_confusions.csv", confusion_rows),
               write_csv("pca_svm_seed0_class_recalls.csv", recall_rows)]
    svm_head_rows, svm_head_means = svm_head_tables(scores)
    written.extend([
        write_csv("session_class_source_counts.csv", metadata["pool_rows"]),
        write_csv("source_session_structure.csv", metadata["session_rows"]),
        write_csv("roster_support_summary.csv", metadata["rosters"]),
        write_csv("published_assembly_recipes.csv", methods["recipes"]),
        write_csv("published_recipe_block_columns.csv", methods["blocks"]),
        write_csv("published_source_observation.csv", [methods["observation"]]),
        write_csv("published_prefit_arm_checks.csv", methods["prefit"]),
        write_csv("svm_head_diagnostics.csv", svm_head_rows),
        write_csv("svm_head_diagnostic_means.csv", svm_head_means),
    ])
    configure_matplotlib()
    figure_dimensions = {"recent_svm": recent_svm(score_lookup)}
    dimensions, width_summary = width_readouts(contrasts)
    figure_dimensions["width_readouts"] = dimensions
    written.append(write_csv("width_pair_changes.csv", width_summary))
    figure_dimensions["errors"] = errors(next(row for row in selected if row["arm"] == "Wfull"))
    figure_dimensions["source_support"] = source_support(metadata)
    figure_dimensions["source_structure"] = source_structure(metadata, methods["observation"])
    figure_dimensions["assembly_recipe"] = assembly_recipe(methods)
    dimensions, sampling_rows = sampling_realization(methods, design, metadata)
    figure_dimensions["sampling_realization"] = dimensions
    written.append(write_csv("arm_sampling_realization.csv", sampling_rows))
    written.extend(OUT / "figures" / f"{stem}.{extension}"
                   for stem in figure_dimensions for extension in ("pdf", "png"))
    historical_bytes = authenticated_bytes(HISTORICAL_TIME)
    require(historical_bytes[:8] == b"\x89PNG\r\n\x1a\n", "Historical figure is not PNG")
    historical_size = struct.unpack(">II", historical_bytes[16:24])
    historical_destination = OUT / "figures" / "historical_time.png"
    historical_destination.write_bytes(historical_bytes)
    written.append(historical_destination)
    first_case_source = SOURCE / "figures/first_case_width.png"
    first_case_bytes = authenticated_bytes(first_case_source)
    require(sha256(first_case_bytes) == manifest["files_sha256"]["figures/first_case_width.png"],
            "First-case figure manifest hash mismatch")
    first_case_destination = OUT / "figures/first_case_width.png"
    first_case_destination.write_bytes(first_case_bytes)
    written.append(first_case_destination)
    provenance = {
        "classification": "Editorial re-presentation of existing exploratory aggregate evidence; no new fits or analysis cases",
        "source_revision": REVISION,
        "source_manifest": {"path": relative(SOURCE / "manifest.json"), "sha256": MANIFEST_SHA256},
        "sources": sources,
        "regenerated_metadata_distributions": {
            "classification": metadata["classification"], "input_files_sha256": metadata["input_hashes"],
            "rule_reference": "src/neuro/studies/population_grid.py:44–120, inspected but not imported",
            "embargo": "Before selecting fixed rosters/classes, exclude training current rows if current or predecessor ID overlaps the union of development current and predecessor IDs",
            "global_counts": metadata["global_counts"],
            "fixed_roster_totals": metadata["rosters"],
            "roster_totals_match_design_and_both_notebooks": True,
            "source_column_membership_count_matches_published_observed_mask_scalar": True,
            "public_assignment_ids_exported": False,
            "new_panel_or_source_selection": False,
        },
        "first_case_figure_copy": {
            "source": relative(first_case_source), "source_sha256": sha256(first_case_bytes),
            "destination": relative(first_case_destination), "byte_identical": True,
            "manifest_authenticated": True, "width_pixels": struct.unpack(">II", first_case_bytes[16:24])[0],
            "height_pixels": struct.unpack(">II", first_case_bytes[16:24])[1],
            "operation": "Byte-for-byte copy of published first-case training curves and confusion; no re-render or model access",
            "selection": "Predetermined first width case, observed seed0 Wmid; not selected by model performance",
        },
        "historical_figure_copy": {
            "source": relative(HISTORICAL_TIME), "source_sha256": sha256(historical_bytes),
            "authenticated_against_revision": REVISION,
            "destination": relative(historical_destination), "byte_identical": True,
            "width_pixels": historical_size[0], "height_pixels": historical_size[1],
            "operation": "Byte-for-byte copy; no reinterpretation, data extraction, or image alteration",
            "cohort_boundary": "Historical October endpoint study, 195 units / 58 sessions; separate from the November width study",
            "interpretation_boundary": "Same-window 100 ms decoding, not temporal generalization; seed ranges are computational variation",
        },
        "deduplication": {
            "rule": "Exact identity keys; all source-text cells must agree for duplicate identities",
            "score_identity": SCORE_KEYS, "score_rows_read": len(all_scores),
            "score_rows_unique": len(scores), "identical_shared_B3_rows_removed": duplicate_scores,
            "contrast_identity": CONTRAST_KEYS, "contrast_rows_unique": len(contrasts),
            "contrast_duplicates_removed": duplicate_contrasts,
            "arm_rows_unique": len(design), "identical_shared_B3_design_rows_removed": duplicate_design,
        },
        "validation": {
            "unique_cases": 48, "encoders": ENCODERS, "readouts": DECODERS, "heads": HEADS,
            "observed_seeds": [0, 1, 2], "diagnostic_worlds_at_seed0": WORLDS,
            "score_identity_grid_complete": True, "contrast_identity_grid_complete": True,
            "all_published_contrasts_checked_against_scores": len(contrasts),
            "maximum_absolute_contrast_rounding_error": maximum_contrast_error,
            "retained_confusion_matrices": 3, "confusion_rows_per_class": 8,
            "confusion_total_constructed_rows_per_matrix": 72,
            "matrix_balanced_accuracy_matches_published_scores": True,
        },
        "figures": {
            "recent_svm": {
                **figure_dimensions["recent_svm"],
                "selection": "RBF-SVM pair head; all six arms, all 3 observed seeds and all 5 source-label worlds",
                "shared_B3": "Displayed in both rows, counted once in the score CSV",
                "jitter": "Small fixed horizontal offsets separate coincident points; no y values altered",
                "y_axis_percent": [0, 100], "uniform_reference_percent": 100 / 9,
            },
            "width_readouts": {
                **figure_dimensions["width_readouts"],
                "selection": "Pair head; both adjacent width contrasts; all 16 encoder/readout combinations",
                "aggregation": "Arithmetic mean of 3 paired computational-repeat delta_BA values, multiplied by 100",
                "display_decimal_places": 2, "units": "percentage points",
            },
            "errors": {
                **figure_dimensions["errors"],
                "case": "observed_seed0_Wfull", "encoder": "pca", "decoder": "svm",
                "head": "pair", "split": "development",
                "balanced_accuracy": float(score_lookup[("observed", "0", "Wfull", "pca", "svm", "pair")]["balanced_accuracy"]),
                "selection_reason": "Fixed seed0 identity predeclared in the figure task; not rank-selected",
                "selection_caveat": "Seed0 happens to be the highest of the three Wfull PCA/SVM repeats; all three appear in recent_svm",
                "left": "Constructed-row counts", "right": "Counts divided by true-class row total, as percent",
            },
            "source_support": {
                **figure_dimensions["source_support"],
                "selection": "All180 session×class pools of the fixed full roster, each split shown separately",
                "meaning": "Eligible current-source IDs after global contributor embargo, before budget selection/assembly",
                "order": "Core, added-to-middle, added-to-full; aliases sorted within each group",
                "color_scale": [0, 9], "outlined_cells": "Development pools with exactly one eligible current source",
            },
            "source_structure": {
                **figure_dimensions["source_structure"],
                "meaning": "Metadata-derived session membership layout; not a neural-value plot or inspected elementwise neural mask",
                "row_heights": "Eligible training plus development current sources in each session",
                "column_widths": "Manifest unit count per retained session",
                "aggregate_crosscheck": methods["observation"],
                "unavailable_entries_are_not_observed_zeros": True,
            },
            "assembly_recipe": {
                **figure_dimensions["assembly_recipe"],
                "selection": "All published entries for rows0/1 of predetermined observed seed0 B2/Wmid first cases",
                "pair": "1->2", "source_choice": "Ordinal alias local to each session×class pool",
                "display_width": "Equal per-session display cells; actual recorded column counts are printed",
                "neural_values_shown": False,
            },
            "sampling_realization": {
                **figure_dimensions["sampling_realization"],
                "selection": "All six arms, observed seed0 published realizations; development availability by fixed roster",
                "tuple_repetitions": "Rows beyond the first identical whole source-ID tuple; not pairwise collisions or neural-vector equality",
                "use_ranges": "Minimum/maximum realized assembly uses over selected training IDs, not uncertainty intervals",
                "development_counts": "Eligible pools, not selected/used development IDs or independent trials",
            },
        },
        "separately_fitted_head_diagnostics": {
            "per_seed_rows": len(svm_head_rows), "mean_range_rows": len(svm_head_means),
            "selection": "All six arms, four representations, observed seeds0/1/2, separately fitted SVM pair/start/goal heads",
            "source_fields": ["train_BA", "balanced_accuracy", "train_development_gap"],
            "gap_definition": "Training balanced accuracy minus exposed-development balanced accuracy, same fitted head",
            "endpoint_heads_are_not_pair_confusion_marginals": True,
        },
        "data_precision": "case_scores.csv and matched_contrasts.csv preserve the exact published numeric strings; derived summaries use Python float representations",
        "limitations": [
            "Known-label condition-matched pseudopopulations; not simultaneous recordings or natural-trial population predictions",
            "Frozen source-disjoint, historically exposed development; 72 constructed rows are not 72 independent biological trials",
            "Three computational seeds and five source-label worlds do not define biological confidence intervals or permutation p-values",
            "Notebook reproduction reused the same recordings and seeds and adds no biological replication",
            "Width also changes included sessions/units; no spatial-field coverage or independent biological-width effect is identified",
            "Whole-cue [0,1) s inputs, 100 ms bins; these figures are not temporal-generalization or path-prediction results",
        ],
        "execution": {
            "command": "PYTHONDONTWRITEBYTECODE=1 python report/series-20261115/build_figures.py",
            "python_version": sys.version.split()[0], "numpy_version": np.__version__,
            "matplotlib_version": matplotlib.__version__, "backend": matplotlib.get_backend(),
            "notebook_cells_executed": 0, "model_fits": 0, "model_loads": 0,
            "predictions_or_neural_arrays_read": 0,
            "public_assignment_metadata_read": True, "public_assignment_ids_exported": False,
        },
        "script_sha256": sha256(Path(__file__).read_bytes()),
        "generated_files_sha256": {relative(path): sha256(path.read_bytes()) for path in written},
    }
    (OUT / "figure-provenance.json").write_text(
        json.dumps(provenance, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps({"score_rows": len(scores), "contrast_rows": len(contrasts),
                      "shared_score_rows_deduplicated": duplicate_scores,
                      "selected_confusion_matrices": len(selected),
                      "figures": figure_dimensions, "contrast_check_max_error": maximum_contrast_error}, indent=2))


if __name__ == "__main__":
    main()
