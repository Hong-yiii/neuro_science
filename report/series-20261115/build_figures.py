#!/usr/bin/env python3
"""Render existing published aggregates; never execute notebooks or study code.

Run from the canonical checkout with its existing Python/numpy/matplotlib:
    PYTHONDONTWRITEBYTECODE=1 python report/series-20261115/build_figures.py

This is an editorial re-presentation of an exploratory study.  It reads only the
two published notebooks, their publication manifest and one historical aggregate
PNG, authenticates them against a pinned Git revision, and extracts literal HTML
tables / explorer JSON. The historical PNG is copied byte-for-byte.
It does not read predictions, neural arrays, raw data, fitted models, or lineage.
"""

from __future__ import annotations

import csv
import hashlib
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
import numpy as np


ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
SOURCE = ROOT / "experiments/source_reuse_width_20261114/walkthrough_20261115/published"
HISTORICAL_TIME = ROOT / "docs/reports/cebra-endpoint-time-readout-20261006/figures/time_balanced_accuracy.png"
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


def main() -> None:
    manifest_bytes = authenticated_bytes(SOURCE / "manifest.json")
    require(sha256(manifest_bytes) == MANIFEST_SHA256, "Unrecognized publication manifest")
    manifest = json.loads(manifest_bytes)
    all_scores, all_contrasts, all_design = [], [], []
    sources = []
    explorer_records = None
    for name in NOTEBOOKS:
        raw = authenticated_bytes(SOURCE / name)
        require(sha256(raw) == manifest["files_sha256"][name], "Notebook manifest hash mismatch")
        notebook = json.loads(raw)
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
    configure_matplotlib()
    figure_dimensions = {"recent_svm": recent_svm(score_lookup)}
    dimensions, width_summary = width_readouts(contrasts)
    figure_dimensions["width_readouts"] = dimensions
    written.append(write_csv("width_pair_changes.csv", width_summary))
    figure_dimensions["errors"] = errors(next(row for row in selected if row["arm"] == "Wfull"))
    written.extend(OUT / "figures" / f"{stem}.{extension}"
                   for stem in figure_dimensions for extension in ("pdf", "png"))
    historical_bytes = authenticated_bytes(HISTORICAL_TIME)
    require(historical_bytes[:8] == b"\x89PNG\r\n\x1a\n", "Historical figure is not PNG")
    historical_size = struct.unpack(">II", historical_bytes[16:24])
    historical_destination = OUT / "figures" / "historical_time.png"
    historical_destination.write_bytes(historical_bytes)
    written.append(historical_destination)
    provenance = {
        "classification": "Editorial re-presentation of existing exploratory aggregate evidence; no new fits or analysis cases",
        "source_revision": REVISION,
        "source_manifest": {"path": relative(SOURCE / "manifest.json"), "sha256": MANIFEST_SHA256},
        "sources": sources,
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
