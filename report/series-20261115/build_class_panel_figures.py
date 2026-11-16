#!/usr/bin/env python3
"""Render the authenticated retrospective class-panel metadata receipt only.

No study imports, optimization, notebook execution, fitting, model access or
neural/assignment-data reads occur here. Existing manuscript figures and their
renderer/provenance are not modified.

    PYTHONDONTWRITEBYTECODE=1 python report/series-20261115/build_class_panel_figures.py
"""

from __future__ import annotations

import argparse
from collections import Counter
import csv
import hashlib
import itertools
import json
from pathlib import Path
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch, Rectangle
import numpy as np


ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
DEFAULT_RECEIPT = ROOT / "docs/experiments/source-reuse-width-20261114/class-panel-metadata-20261116.json"
RECEIPT_SHA256 = "8f6560aa172c86a53f211596bce9333ee410281210f2c518ad3a8503a572316a"
CLASS_COUNTS = (6, 8, 9, 10, 12, 15, 18, 24, 30)
BLUE, ORANGE, SELECTED = "#236b91", "#b66319", "#d18100"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def read_receipt(path: Path) -> tuple[dict, list[dict], list[dict]]:
    raw = path.read_bytes()
    require(sha256(raw) == RECEIPT_SHA256, "Class-panel receipt SHA256 mismatch")
    receipt = json.loads(raw)
    require(receipt["status"] == "passed" and receipt["K9_exact_frozen_panel_and_rosters_match"]
            and receipt["frozen_design_unchanged"], "Receipt did not pass frozen-design checks")
    require(receipt["K_was_fixed_before_class_selection"] == 9, "Frozen K changed")
    require(receipt["model_fits"] == receipt["neural_value_arrays_read"]
            == receipt["notebooks_executed"] == 0 and not receipt["torch_or_cebra_imported"],
            "Receipt scope is not metadata only")
    require(receipt["archive_inventory"] == {"sessions": 58, "recorded_columns": 195}
            and receipt["no_session_has_3_training_sources_in_every_class"],
            "Receipt archive/all-class feasibility checks changed")
    require(tuple(row["K"] for row in receipt["frontier"]) == CLASS_COUNTS, "Frontier K coverage changed")
    valid_pairs = {f"{start}->{goal}" for start in range(1, 7) for goal in range(1, 7) if start != goal}
    frontier = []
    for entry in receipt["frontier"]:
        k, panel, gates = entry["K"], entry["panel"], entry["gates"]
        require(panel["class_count"] == k == len(set(panel["conditions"]))
                and set(panel["conditions"]) <= valid_pairs, "Invalid frontier class identities")
        require(panel["solver_status"] == "optimal" and panel["mip_gap"] == 0.0,
                "Frontier optimization was not certified in receipt")
        for endpoint in (0, 1):
            degree = Counter(int(pair.split("->")[endpoint]) for pair in panel["conditions"])
            require(all(k // 6 <= degree[node] <= (k + 5) // 6 for node in range(1, 7)),
                    "Receipt panel violates its balanced endpoint-degree requirement")
        for gate in ("5", "3"):
            require(gates[gate]["sessions"] == len(set(gates[gate]["session_aliases"]))
                    and 0 <= gates[gate]["sessions"] <= 58 and 0 <= gates[gate]["columns"] <= 195,
                    "Invalid gate inventory")
        require(gates["5"]["columns"] == panel["maximum_columns_min5"]
                and gates["3"]["columns"] == panel["maximum_columns_min3_at_min5_optimum"],
                "Receipt gate width differs from objective value")
        require(gates["5"]["columns"] <= gates["3"]["columns"]
                and gates["5"]["sessions"] <= gates["3"]["sessions"], "Gate nesting failed")
        frontier.append({
            "K": k, "scope": "fixed_and_executed_design" if k == 9 else "metadata_only_alternative",
            "columns_gate5": gates["5"]["columns"], "sessions_gate5": gates["5"]["sessions"],
            "columns_gate3_conditional_on_gate5_optimum": gates["3"]["columns"],
            "sessions_gate3_for_the_selected_panel": gates["3"]["sessions"],
            "selected_classes": ";".join(panel["conditions"]),
            "solver_status": panel["solver_status"], "mip_gap": panel["mip_gap"],
        })
    frozen = next(row for row in frontier if row["K"] == 9)
    require((frozen["columns_gate5"], frozen["sessions_gate5"],
             frozen["columns_gate3_conditional_on_gate5_optimum"],
             frozen["sessions_gate3_for_the_selected_panel"]) == (17, 3, 83, 20),
            "Executed K9 cohort does not match the accepted study")
    selected = set(frozen["selected_classes"].split(";"))
    matrix_names = ("eligible_training_sources", "eligible_development_sources", "sessions_passing_single_pair_gate5")
    for name in matrix_names:
        matrix = receipt[name]
        require(len(matrix) == 6 and all(len(row) == 6 for row in matrix), "Expected full 6×6 matrix")
        for start, goal in itertools.product(range(6), repeat=2):
            value = matrix[start][goal]
            require(value is None if start == goal else type(value) is int and value >= 0,
                    "Diagonal availability or source-count type changed")
    marginals = []
    for start, goal in itertools.product(range(6), repeat=2):
        if start == goal:
            continue
        pair = f"{start + 1}->{goal + 1}"
        passing = receipt["sessions_passing_single_pair_gate5"][start][goal]
        require(passing <= 58, "Single-pair session count exceeds the archive")
        marginals.append({
            "start": start + 1, "goal": goal + 1, "pair": pair,
            "eligible_training_sources": receipt["eligible_training_sources"][start][goal],
            "eligible_development_sources": receipt["eligible_development_sources"][start][goal],
            "sessions_passing_single_pair_gate5": passing,
            "selected_in_fixed_K9_panel": pair in selected,
        })
    require(len(marginals) == 30 and sum(row["selected_in_fixed_K9_panel"] for row in marginals) == 9,
            "Marginal/selected-class coverage changed")
    require(sum(row["eligible_training_sources"] for row in marginals) == 7861
            and sum(row["eligible_development_sources"] for row in marginals) == 3265,
            "All-session marginal totals differ from frozen/global-embargo accounting")
    return receipt, marginals, frontier


def configure_style() -> None:
    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 9,
        "axes.labelsize": 9, "axes.titlesize": 9,
        "xtick.labelsize": 8, "ytick.labelsize": 8, "legend.fontsize": 8,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.linewidth": 0.65, "xtick.major.width": 0.65, "ytick.major.width": 0.65,
        "pdf.fonttype": 42, "ps.fonttype": 42,
        "figure.facecolor": "white", "savefig.facecolor": "white",
    })


def save_figure(fig, name: str) -> dict:
    require(name.startswith("class_panel_"), "Refusing to write an existing figure name")
    width, height = map(float, fig.get_size_inches())
    pdf, png = (OUT / "figures" / f"{name}.{suffix}" for suffix in ("pdf", "png"))
    fig.savefig(pdf, metadata={"Creator": "build_class_panel_figures.py", "CreationDate": None, "ModDate": None})
    fig.savefig(png, dpi=240)
    require(b"/Subtype /Image" not in pdf.read_bytes(), "Expected an entirely vector PDF")
    plt.close(fig)
    return {"width_inches": width, "height_inches": height, "png_dpi": 240, "pdf_raster_image_objects": 0}


def plot_support(receipt: dict, marginals: list[dict]) -> dict:
    selected = {(row["start"] - 1, row["goal"] - 1) for row in marginals if row["selected_in_fixed_K9_panel"]}
    fig = plt.figure(figsize=(7, 3.9))
    fig.suptitle("All 58 sessions · marginal support for each ordered endpoint class",
                 y=0.99, fontsize=10)
    axes = [fig.add_axes([0.08, 0.245, 0.355, 0.615]),
            fig.add_axes([0.575, 0.245, 0.355, 0.615])]
    names = ("eligible_training_sources", "sessions_passing_single_pair_gate5")
    titles = ("a  Sources: training / development", "b  Sessions passing the 5-source gate")
    for index, (ax, name, high) in enumerate(zip(axes, names, (300, 58), strict=True)):
        values = np.ma.masked_invalid(np.array(receipt[name], dtype=float))
        cmap = plt.get_cmap("Blues").copy()
        cmap.set_bad("#eeeeee")
        ax.set_facecolor("#eeeeee")
        im = ax.pcolormesh(np.arange(7) - 0.5, np.arange(7) - 0.5, values,
                           cmap=cmap, vmin=0, vmax=high, shading="flat", rasterized=False,
                           edgecolors="white", linewidth=0.65)
        ax.set_xlim(-0.5, 5.5)
        ax.set_ylim(5.5, -0.5)
        ax.set_xticks(range(6), range(1, 7))
        ax.set_yticks(range(6), range(1, 7))
        ax.set_xlabel("Goal")
        ax.set_ylabel("Start")
        ax.tick_params(length=0, pad=4)
        ax.set_title(titles[index], fontsize=8.5, pad=9)
        for start, goal in itertools.product(range(6), repeat=2):
            if start == goal:
                ax.text(goal, start, "—", ha="center", va="center", color="#737373", fontsize=10)
                continue
            value = int(values[start, goal])
            label = (f"{value}\n{receipt['eligible_development_sources'][start][goal]}" if index == 0 else str(value))
            ax.text(goal, start, label, ha="center", va="center", fontsize=8.3 if index == 0 else 9,
                    linespacing=1.2, color="white" if value > high * 0.65 else "#1c2833")
            if (start, goal) in selected:
                ax.add_patch(Rectangle((goal - 0.47, start - 0.47), 0.94, 0.94,
                                       fill=False, edgecolor=SELECTED, linewidth=1.6))
        for spine in ax.spines.values():
            spine.set_visible(False)
        cax = fig.add_axes([0.447 if index == 0 else 0.943, 0.245, 0.012, 0.615])
        bar = fig.colorbar(im, cax=cax, ticks=[0, 100, 200, 300] if index == 0 else [0, 20, 40, 58])
        bar.solids.set_rasterized(False)
        bar.ax.tick_params(labelsize=7.5, length=2)
    fig.text(0.50, 0.13, "Panel a: train count above development count; color shows train count.", ha="center", fontsize=8)
    fig.text(0.50, 0.085, "Panel b gate: at least five train and one development sources for that pair in a session.", ha="center", fontsize=8)
    fig.legend(handles=[Patch(facecolor="none", edgecolor=SELECTED, linewidth=1.6,
                              label="Nine fixed/executed classes"),
                        Patch(facecolor="#eeeeee", label="Self-pair unavailable")],
               loc="lower center", bbox_to_anchor=(0.5, -0.005), ncol=2, frameon=False, fontsize=8)
    return save_figure(fig, "class_panel_support")


def plot_frontier(frontier: list[dict]) -> dict:
    fig, axes = plt.subplots(1, 2, figsize=(7, 3.2))
    fig.subplots_adjust(left=0.085, right=0.985, bottom=0.30, top=0.78, wspace=0.26)
    fig.suptitle("Support at each fixed class count K", y=0.985, fontsize=10)
    fig.text(0.5, 0.875, "Three-source width is optimized among panels maximizing five-source width.", ha="center", fontsize=8)
    x = np.arange(len(CLASS_COUNTS))
    fixed_index = CLASS_COUNTS.index(9)
    for ax, fields, title, limit, ticks in (
        (axes[0], ("columns_gate5", "columns_gate3_conditional_on_gate5_optimum"),
         "a  Recorded columns", 120, [0, 30, 60, 90, 120]),
        (axes[1], ("sessions_gate5", "sessions_gate3_for_the_selected_panel"),
         "b  Admitted sessions", 32, [0, 10, 20, 30]),
    ):
        ax.axvspan(fixed_index - 0.40, fixed_index + 0.40, color="#e8e8e8", zorder=0)
        for field, color, marker, offset in zip(fields, (BLUE, ORANGE), ("o", "s"), (-0.07, 0.07), strict=True):
            values = [row[field] for row in frontier]
            ax.plot(x + offset, values, color=color, linewidth=1.0, zorder=2)
            ax.scatter(x + offset, values, marker=marker, s=24, facecolors="white",
                       edgecolors=color, linewidths=1, zorder=3, clip_on=False)
            ax.scatter(fixed_index + offset, values[fixed_index], marker=marker, s=31,
                       color=color, linewidths=1, zorder=4)
            ax.annotate(str(values[fixed_index]), (fixed_index + offset, values[fixed_index]),
                        xytext=(5, 5), textcoords="offset points", color=color, fontsize=8, weight="bold")
        ax.set_xticks(x, CLASS_COUNTS)
        ax.set_xlim(-0.45, len(CLASS_COUNTS) - 0.55)
        ax.set_ylim(0, limit)
        ax.set_yticks(ticks)
        ax.set_title(title, loc="left", fontsize=9, pad=7)
        ax.set_xlabel("Fixed class count K", fontsize=8.5)
        ax.grid(axis="y", color="#e3e3e3", linewidth=0.55)
        ax.set_axisbelow(True)
    handles = [
        Line2D([], [], color=BLUE, marker="o", markerfacecolor="white", linewidth=1, label="At least 5 train sources"),
        Line2D([], [], color=ORANGE, marker="s", markerfacecolor="white", linewidth=1, label="At least 3 train sources (conditional)"),
        Line2D([], [], color="#555555", marker="o", markerfacecolor="white", linestyle="None", label="Other K: metadata only"),
        Line2D([], [], color="#555555", marker="o", linestyle="None", label="K = 9: fixed and executed"),
    ]
    fig.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.52, 0.005), ncol=2,
               frameon=False, fontsize=7.7, handlelength=2.3, columnspacing=1.4)
    return save_figure(fig, "class_panel_frontier")


def write_csv(name: str, rows: list[dict]) -> Path:
    require(name.startswith("class_panel_"), "Refusing to write an existing CSV name")
    path = OUT / "data" / name
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=tuple(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path, default=DEFAULT_RECEIPT,
                        help="Exact authenticated metadata receipt; bytes must match the fixed SHA256")
    args = parser.parse_args()
    receipt, marginals, frontier = read_receipt(args.receipt)
    (OUT / "figures").mkdir(exist_ok=True)
    (OUT / "data").mkdir(exist_ok=True)
    written = [write_csv("class_panel_marginals.csv", marginals),
               write_csv("class_panel_frontier.csv", frontier)]
    configure_style()
    figures = {"class_panel_support": plot_support(receipt, marginals),
               "class_panel_frontier": plot_frontier(frontier)}
    written.extend(OUT / "figures" / f"{name}.{suffix}" for name in figures for suffix in ("pdf", "png"))
    provenance = {
        "classification": "Presentation of an authenticated retrospective metadata-feasibility receipt; no new optimization or experiment",
        "source_receipt": {"path": relative(args.receipt), "sha256": RECEIPT_SHA256,
                           "verification_date": receipt["verification_date"], "status": receipt["status"],
                           "source_revision_recorded_by_receipt": receipt["source_revision"]},
        "source_locations": {
            "class_panel_marginals.csv": ["/eligible_training_sources", "/eligible_development_sources",
                                           "/sessions_passing_single_pair_gate5", "/frontier/2/panel/conditions"],
            "class_panel_frontier.csv": "/frontier (all nine entries, unchanged order)",
        },
        "validation": {"marginal_rows": len(marginals), "frontier_rows": len(frontier),
                       "selected_K9_cells": 9, "diagonal": "null/unavailable, never counted as zero",
                       "total_eligible_training_sources": 7861, "total_eligible_development_sources": 3265,
                       "all_receipt_solver_statuses_optimal_with_zero_gap": True,
                       "all_panel_endpoint_degrees_balanced": True,
                       "K9_columns_gate5_gate3": [17, 83], "K9_sessions_gate5_gate3": [3, 20]},
        "figures": {
            "class_panel_support": {**figures["class_panel_support"],
                "scope": "All 58 recorded sessions, all 30 nonself ordered endpoint classes; eligible after frozen split/global contributor embargo",
                "left_text": "Training count above development count; color encodes training count",
                "right": "Number of sessions with at least 5 training and 1 development source for each pair considered separately",
                "selected_outline": "Nine classes of the already fixed/executed K9 design",
                "single_pair_support_is_not_joint_panel_feasibility": True},
            "class_panel_frontier": {**figures["class_panel_frontier"],
                "K_values": CLASS_COUNTS, "x_spacing": "Equally spaced fixed-K categories; lines only guide the eye",
                "marker_offsets": "Small fixed horizontal offsets distinguish the two gates; no y values altered",
                "gate5": "Maximum admitted recorded columns under at least 5 train and 1 development source for every selected class/session",
                "gate3": "Maximum admitted columns under at least 3 train and 1 development source, conditional on achieving the gate5 width optimum",
                "sessions": "Session counts for the chosen panels, not separately maximized session objectives",
                "execution": "Only K9 is the fixed/executed study; all other K values are retrospective metadata-only alternatives",
                "uncertainty_intervals": "None; these are deterministic metadata counts"},
        },
        "limits": [
            "K9 was fixed before class selection; this retrospective frontier does not show that nine globally maximizes width or decoding performance",
            "No alternative K was evaluated by fitting or decoding in this receipt",
            "Class panels can differ across K and are constrained by balanced start/goal degree; frontier points are not nested-class interventions",
            "Neither marginal source totals nor passing single-pair gates establish a joint multisession population",
            "Counts do not establish biological independence, simultaneity or natural-trial prediction",
        ],
        "execution": {"command": "PYTHONDONTWRITEBYTECODE=1 python report/series-20261115/build_class_panel_figures.py",
                      "python_version": sys.version.split()[0], "numpy_version": np.__version__,
                      "matplotlib_version": matplotlib.__version__, "model_fits": 0,
                      "optimizer_calls": 0, "study_imports": 0, "notebooks_executed": 0,
                      "neural_or_assignment_value_files_read": 0},
        "script_sha256": sha256(Path(__file__).read_bytes()),
        "generated_files_sha256": {relative(path): sha256(path.read_bytes()) for path in written},
    }
    (OUT / "class-panel-figure-provenance.json").write_text(
        json.dumps(provenance, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"source_sha256": RECEIPT_SHA256, "marginal_rows": len(marginals),
                      "frontier_rows": len(frontier), "figures": figures}, indent=2))


if __name__ == "__main__":
    main()
