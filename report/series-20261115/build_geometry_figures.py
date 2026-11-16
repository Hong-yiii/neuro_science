#!/usr/bin/env python3
"""Render four predetermined saved class-mean/loss examples; no model execution.

The default build reads only the curated public JSON beside this script. The
optional extraction command authenticates previously delivered aggregate JSON
against the tracked validation-ledger/delivery-manifest chain and matches saved
PNG outputs to the reviewed published notebooks. It never reads feature arrays,
models, source identities or neural observations, and never executes a notebook.

    python report/series-20261115/build_geometry_figures.py
    python report/series-20261115/build_geometry_figures.py --extract-from-delivery PATH

Requires only Python's standard library, NumPy and Matplotlib.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
from pathlib import Path
import re
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import MaxNLocator, ScalarFormatter
import numpy as np


ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
CURATED = OUT / "data/cebra_geometry_examples.json"
CURATED_SHA256 = "82838f544adcb15ba60517cc7b2cc196965d38fd4f686194c2edbf77eba4e67c"
DELIVERY_SHA256 = "85e05fa820232245f37332e38bb70155507e869f1da69f0abb0d98cd1b4a0b37"
PUBLICATION = ROOT / "experiments/source_reuse_width_20261114/walkthrough_20261115/published"
PUBLICATION_SHA256 = "8ef3a28e687e657c6429632b6a2011bfaa57dfadd62ff94fc276f21bef9a9e93"
LEDGER = ROOT / "docs/experiments/source-reuse-width-20261114/validation.md"
LABELS = ("1->2", "1->4", "2->5", "2->6", "3->1", "4->6", "5->3", "5->4", "6->2")
SELECTION = (
    ("time_B2", "source_reuse", "observed_seed0_B2", "cebra"),
    ("time_B5", "source_reuse", "observed_seed0_B5", "cebra"),
    ("time_Wmid", "population_width", "observed_seed0_Wmid", "cebra"),
    ("native_Wmid", "population_width", "observed_seed0_Wmid", "native"),
)
ARM_COUNTS = {
    "B2": {"columns": 17, "sessions": 3, "sources_per_training_pool": 2,
           "selected_training_source_ids": 54, "available_development_source_ids": 56},
    "B5": {"columns": 17, "sessions": 3, "sources_per_training_pool": 5,
           "selected_training_source_ids": 135, "available_development_source_ids": 56},
    "Wmid": {"columns": 49, "sessions": 11, "sources_per_training_pool": 3,
             "selected_training_source_ids": 297, "available_development_source_ids": 210},
}
INPUT_HASHES = {
    "source_reuse/trajectories.json": "87afb9c46d122b5923eaba1318c50862c7c17efc3899d6c788d638640ab5cf1c",
    "source_reuse/learning.json": "cc7ec11399ea5bb63c0f4ca8c2958eb4ddc70aaa213b3d2a707596b22f22ef99",
    "population_width/trajectories.json": "152b842bae05027dcba33441abab518a9d055182bb52ee3db24333db938a061e",
    "population_width/learning.json": "216da27a4ce80127397d83fea14f661fad925046839b87ff6f68a7e54d290a00",
}
COLORS = ("#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd",
          "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22")
CAMERA = {"elevation_degrees": 24, "azimuth_degrees": -58,
          "projection": "orthographic", "box_aspect": [1, 1, 1]}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative(path):
    return path.resolve().relative_to(ROOT).as_posix()


def read_pinned(path, expected):
    require(sha(path) == expected, f"SHA256 mismatch: {path.name}")
    return json.loads(path.read_text())


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n")


def one(rows, **keys):
    selected = [r for r in rows if all(r.get(k) == v for k, v in keys.items())]
    require(len(selected) == 1, f"Nonunique saved record: {keys}")
    return selected[0]


def validate(data):
    require(data["schema_version"] == 1, "Unknown curated-input schema")
    require(tuple(data["class_order"]) == LABELS, "Nine-class panel changed")
    require(data["bin_centers_ms"] == list(range(50, 1000, 100)), "Cue-bin times changed")
    require(data["display_coordinate_indices_one_based"] == [1, 2, 3]
            and data["fitted_dimension"] == 7, "Coordinate semantics changed")
    require([(v["id"], v["part"], v["case"], v["encoder"]) for v in data["views"]]
            == list(SELECTION), "Design-selected examples changed")
    checks = []
    for view in data["views"]:
        require(set(view["coordinates"]) == set(LABELS), "Class coverage changed")
        coords = np.asarray([view["coordinates"][label] for label in LABELS], dtype=float)
        loss = np.asarray(view["total_loss"], dtype=float)
        require(coords.shape == (9, 10, 3) and np.isfinite(coords).all(),
                "Expected finite nine-class, ten-bin, three-coordinate means")
        require(loss.shape == (1000,) and np.isfinite(loss).all()
                and view["iterations"] == 1000 and view["seed"] == 0,
                "Expected finite 1000-update seed0 training trace")
        require(view["counts"] == dict(ARM_COUNTS[view["arm"]], training_constructed_rows=144,
                                       development_constructed_rows=72, development_rows_per_class=8),
                "Cohort counts changed")
        checks.append({"view": view["id"], "coordinate_shape": list(coords.shape),
                       "loss_entries": len(loss), "all_finite": True})
    return checks


def extract(delivery):
    """Authenticate and copy only selected aggregate means and total loss."""
    require(DELIVERY_SHA256 in LEDGER.read_text(), "Tracked ledger no longer pins delivery manifest")
    manifest_path = delivery / "delivery_manifest.json"
    delivery_manifest = read_pinned(manifest_path, DELIVERY_SHA256)
    require(delivery_manifest["status"] == "completed", "Delivery did not complete")
    publication = read_pinned(PUBLICATION / "manifest.json", PUBLICATION_SHA256)
    aggregates, notebook_by_part, reports = {}, {}, {}
    for name, expected in INPUT_HASHES.items():
        require(delivery_manifest["files_sha256"][name] == expected, "Delivery input pin changed")
        aggregates[name] = read_pinned(delivery / name, expected)
    for part in ("source_reuse", "population_width"):
        name = part + "/report_manifest.json"
        reports[part] = read_pinned(delivery / name, delivery_manifest["files_sha256"][name])
        name = part + "_20261115.executed.ipynb"
        notebook_by_part[part] = read_pinned(PUBLICATION / name, publication["files_sha256"][name])
    require(len(aggregates["source_reuse/trajectories.json"]) == 32
            and len(aggregates["population_width/trajectories.json"]) == 24,
            "Complete source files no longer contain expected cases")
    require(len({r["case"] for p in ("source_reuse", "population_width")
                 for r in aggregates[p + "/trajectories.json"]}) == 48,
            "Bridge deduplication does not recover all 48 unique original cases")
    views, render_checks = [], []
    for view_id, part, case, encoder in SELECTION:
        trajectory_path, learning_path = (part + "/" + stem + ".json"
                                         for stem in ("trajectories", "learning"))
        geometry = one(aggregates[trajectory_path], case=case)["coordinates"][encoder]
        learning = one(aggregates[learning_path], case=case + "_" + encoder, encoder=encoder)
        figure_name = "figures/trajectory_" + case + ".png"
        figure = one(reports[part]["figures"], file=figure_name)
        require(delivery_manifest["files_sha256"][part + "/" + figure_name] == figure["sha256"],
                "Report/delivery geometry image hashes differ")
        image_matches, learning_matches = [], []
        learning_figure = one(reports[part]["figures"], file="figures/all_learning_curves.png")
        for cell in notebook_by_part[part]["cells"]:
            for output in cell.get("outputs", []):
                payload = output.get("data", {})
                content = payload.get("text/html", "")
                content = "".join(content) if isinstance(content, list) else content
                pattern = (r"<summary>trajectory_" + re.escape(case)
                           + r'</summary>.*?data:image/png;base64,([^\"]+)')
                for match in re.finditer(pattern, content, re.S):
                    image_matches.append(hashlib.sha256(base64.b64decode(match[1])).hexdigest())
                png = payload.get("image/png")
                if png:
                    encoded = "".join(png) if isinstance(png, list) else png
                    digest = hashlib.sha256(base64.b64decode(encoded)).hexdigest()
                    if digest == learning_figure["sha256"]:
                        learning_matches.append(digest)
        require(image_matches == [figure["sha256"]], "Published geometry PNG does not match accepted report")
        require(learning_matches == [learning_figure["sha256"]], "Published learning PNG does not match accepted report")
        arm = case.rsplit("_", 1)[1]
        views.append({
            "id": view_id, "part": part, "case": case, "arm": arm, "encoder": encoder,
            "seed": learning["seed"], "iterations": learning["iterations"],
            "counts": dict(ARM_COUNTS[arm], training_constructed_rows=144,
                           development_constructed_rows=72, development_rows_per_class=8),
            "coordinates": {label: geometry[label] for label in LABELS},
            "total_loss": learning["loss"]["total"],
            "source_records": {"geometry_file": trajectory_path, "geometry_case": case,
                               "coordinate_key": "coordinates." + encoder,
                               "learning_file": learning_path,
                               "learning_case": case + "_" + encoder,
                               "loss_key": "loss.total"},
        })
        render_checks.append({
            "view": view_id, "published_notebook": relative(PUBLICATION / (part + "_20261115.executed.ipynb")),
            "published_notebook_sha256": publication["files_sha256"][part + "_20261115.executed.ipynb"],
            "original_geometry_figure": part + "/" + figure_name,
            "geometry_png_sha256": image_matches[0],
            "all_learning_curves_png_sha256": learning_matches[0],
            "check": "Accepted report PNG equals embedded reviewed publication PNG; no pixel digitization",
        })
    data = {
        "schema_version": 1,
        "classification": "Presentation-only excerpts from completed exploratory study; no new analysis or fitting",
        "selection_rule": "Predetermined observed seed0: Time B2/B5 source-budget endpoints at17 columns; Time/native Wmid first width case at49 columns. Not selected by scores, apparent geometry or loss, and not representative seeds.",
        "class_order": list(LABELS), "bin_centers_ms": list(range(50, 1000, 100)),
        "display_coordinate_indices_one_based": [1, 2, 3], "fitted_dimension": 7,
        "semantics": {
            "geometry": "Per endpoint-class means of eight constructed exposed-development rows at each of ten cue bins, using first3 of7 fitted coordinates; not individual observations or whole-cue display PCA.",
            "native": "Fixed equal-session mean of corresponding7D bin embeddings from pair-supervised session encoders, followed by the same eight-row class mean.",
            "time": "CEBRA-Time uses adjacent-bin positives within constructed training rows.",
            "loss": "Saved unsmoothed own-objective total training loss, one value for updates1 through1000; not development loss or decoder accuracy. Objectives differ between Time and native.",
            "precision": "Selected JSON numeric values copied through Python float round-trip with no explicit rounding; plot conversion to float64 only. No new PCA, alignment, embedding transform or neural-array read.",
            "claim_limits": "Known-label construction; historically exposed contributor-disjoint development. No simultaneous population, natural-trial inference, biological uncertainty or geometry-comparison claim.",
        },
        "source_provenance": {
            "tracked_ledger": relative(LEDGER), "tracked_ledger_sha256_at_extraction": sha(LEDGER),
            "tracked_ledger_anchor": "Dated delivery table: delivery_manifest.json (102 files)",
            "original_delivery_directory": "outputs/source-reuse-width-20261114/deliverables-20261115-03",
            "original_delivery_manifest_sha256": DELIVERY_SHA256,
            "original_accepted_run_receipt_sha256": delivery_manifest["source_receipt_sha256"],
            "original_numeric_audit_sha256": delivery_manifest["numeric_audit_sha256"],
            "aggregate_files_sha256": INPUT_HASHES,
            "report_manifests_sha256": {p + "/report_manifest.json": delivery_manifest["files_sha256"][p + "/report_manifest.json"] for p in ("source_reuse", "population_width")},
            "publication_manifest": relative(PUBLICATION / "manifest.json"),
            "publication_manifest_sha256": PUBLICATION_SHA256,
            "reproduction_run_receipt_sha256": publication["run_receipt_sha256"],
            "published_png_cross_checks": render_checks,
            "complete_original_cases_preserved": 48,
            "class_mean_definition_source": "experiments/source_reuse_width_20261114/walkthrough_20261115/staging.py:328; development z[pair==label,:,:3].mean(0)",
            "native_pooling_definition_source": "src/neuro/studies/population_models.py:82; equal-session mean before row-class averaging",
            "cohort_counts_source": "docs/experiments/source-reuse-width-20261114/README.md: What was held fixed and what changed",
        },
        "views": views,
    }
    validate(data)
    write_json(CURATED, data)
    print("Authenticated aggregate extraction:", relative(CURATED), sha(CURATED))


def configure_style():
    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 8,
        "axes.labelsize": 8, "axes.titlesize": 9, "axes.titleweight": "normal",
        "xtick.labelsize": 7.5, "ytick.labelsize": 7.5, "legend.fontsize": 8,
        "axes.linewidth": 0.65, "xtick.major.width": 0.65, "ytick.major.width": 0.65,
        "pdf.fonttype": 42, "ps.fonttype": 42, "path.simplify": False,
        "figure.facecolor": "white", "savefig.facecolor": "white",
    })


def geometry_panel(ax, view):
    coords = np.asarray([view["coordinates"][label] for label in LABELS], dtype=float)
    for label, color, values in zip(LABELS, COLORS, coords, strict=True):
        ax.plot(*values.T, color=color, linewidth=1.0, marker=".", markersize=3,
                alpha=0.9, label=label.replace("->", "→"))
        ax.scatter(*values[0], marker="o", s=22, facecolors="white", edgecolors=color,
                   linewidths=1.15, depthshade=False, zorder=5)
        ax.scatter(*values[-1], marker="x", s=25, color=color, linewidths=1.25,
                   depthshade=False, zorder=5)
    flat = coords.reshape(-1, 3)
    low, high = flat.min(axis=0), flat.max(axis=0)
    centers = (low + high) / 2
    span = float((high - low).max()) * 1.16
    require(span > 0, "Degenerate geometry example")
    bounds = [[float(c - span / 2), float(c + span / 2)] for c in centers]
    ax.set_xlim(*bounds[0])
    ax.set_ylim(*bounds[1])
    ax.set_zlim(*bounds[2])
    ax.set_box_aspect((1, 1, 1))
    ax.set_proj_type("ortho")
    ax.view_init(elev=CAMERA["elevation_degrees"], azim=CAMERA["azimuth_degrees"])
    for axis, name in zip((ax.xaxis, ax.yaxis, ax.zaxis), ("Coordinate 1", "Coordinate 2", "Coordinate 3"), strict=True):
        axis.set_major_locator(MaxNLocator(nbins=3))
        formatter = ScalarFormatter(useOffset=False)
        formatter.set_scientific(False)
        axis.set_major_formatter(formatter)
        axis.set_label_text(name, fontsize=8)
        axis.labelpad = 1.5
        axis.set_tick_params(pad=0, labelsize=7)
        axis.pane.set_facecolor((0.96, 0.97, 0.98, 1))
        axis.pane.set_edgecolor((0.85, 0.87, 0.89, 1))
    # Place the z label in figure coordinates in render_pair: native ticks are
    # wider, and Matplotlib adjusts each 3D axes box after draw.
    ax.set_zlabel("")
    return {"view": view["id"], "coordinate_minimum": low.tolist(),
            "coordinate_maximum": high.tolist(), "axis_limits": bounds,
            "equal_axis_span": span, "camera": CAMERA}


def loss_panel(ax, view, title):
    values = np.asarray(view["total_loss"], dtype=float)
    color = "#236b91" if view["encoder"] == "cebra" else "#b66319"
    ax.plot(np.arange(1, 1001), values, linewidth=0.65, color=color)
    ax.set(xlim=(0, 1000), xticks=(0, 250, 500, 750, 1000), xlabel="Optimizer update",
           ylabel="Own-objective total loss", title=title)
    ax.yaxis.set_major_locator(MaxNLocator(nbins=4))
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", linewidth=0.5, alpha=0.2)
    ax.margins(y=0.08)
    return {"view": view["id"], "x_limits": list(ax.get_xlim()), "y_limits": list(ax.get_ylim()),
            "entries_drawn": len(values), "smoothing": None}


def render_pair(views, name, title, subtitle, geometry_titles, output):
    fig = plt.figure(figsize=(7, 6))
    fig.suptitle(title, fontsize=11, y=0.985)
    fig.text(0.5, 0.935, subtitle, ha="center", fontsize=8.5, color="#444444")
    panels, losses = [], []
    for i, view in enumerate(views):
        ax = fig.add_axes([0.015 + 0.50 * i, 0.48, 0.455, 0.405], projection="3d")
        ax.set_title(geometry_titles[i], pad=11, fontsize=9)
        panels.append(geometry_panel(ax, view))
        fig.text(0.485 + 0.50 * i, 0.69, "Coordinate 3", rotation=90,
                 ha="center", va="center", fontsize=8)
        ax = fig.add_axes([0.10 + 0.49 * i, 0.10, 0.355, 0.217])
        losses.append(loss_panel(ax, view, f"({'cd'[i]}) Training loss for panel ({'ab'[i]})"))
    handles = [Line2D([], [], color=color, marker=".", markersize=4, linewidth=1,
                      label=label.replace("->", "→")) for label, color in zip(LABELS, COLORS, strict=True)]
    fig.legend(handles=handles, title="Ordered endpoint class", title_fontsize=8, ncol=9,
               loc="upper center", bbox_to_anchor=(0.5, 0.452), frameon=False,
               columnspacing=0.9, handlelength=1.5, handletextpad=0.4, labelspacing=0.35)
    endpoint_handles = [
        Line2D([], [], color="#444444", marker="o", markerfacecolor="white", linestyle="None", label="50 ms"),
        Line2D([], [], color="#444444", marker="x", linestyle="None", label="950 ms"),
    ]
    fig.legend(handles=endpoint_handles, ncol=2, loc="upper center", bbox_to_anchor=(0.5, 0.387),
               frameon=False, handletextpad=0.4, columnspacing=1.6, fontsize=8)
    fig.text(0.5, 0.014, "Class means in coordinates 1–3 of 7 · independent panel limits · no cross-fit alignment",
             ha="center", fontsize=7.5, color="#444444")
    output.mkdir(parents=True, exist_ok=True)
    files = []
    for suffix in ("pdf", "png"):
        path = output / f"{name}.{suffix}"
        if suffix == "pdf":
            fig.savefig(path, metadata={"Creator": "build_geometry_figures.py", "Title": title,
                                        "CreationDate": None, "ModDate": None})
            require(b"/Subtype /Image" not in path.read_bytes(), "Expected vector-only PDF")
        else:
            fig.savefig(path, dpi=240, metadata={"Software": "build_geometry_figures.py"})
        files.append({"file": f"figures/{path.name}", "sha256": sha(path),
                      "width_inches": 7, "height_inches": 6, "vector": suffix == "pdf"})
    plt.close(fig)
    return {"name": name, "views": [v["id"] for v in views], "geometry_panels": panels,
            "loss_panels": losses, "files": files}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--extract-from-delivery", type=Path,
                        help="Optional one-time authenticated aggregate extraction; no rendering")
    parser.add_argument("--output-dir", type=Path, default=OUT,
                        help="Presentation artifact directory; default is this manuscript directory")
    args = parser.parse_args()
    if args.extract_from_delivery is not None:
        extract(args.extract_from_delivery)
        return
    data = read_pinned(CURATED, CURATED_SHA256)
    checks = validate(data)
    configure_style()
    rendered = [
        render_pair(data["views"][:2], "cebra_source_geometry",
                    "CEBRA-Time at two source budgets", "17 columns · 3 sessions · observed seed 0",
                    ("(a) Two sources per pool (B2)", "(b) Five sources per pool (B5)"), args.output_dir / "figures"),
        render_pair(data["views"][2:], "cebra_model_geometry",
                    "Two fitted CEBRA pipelines at 49 columns",
                    "Wmid · 11 sessions · 3 sources per pool · observed seed 0",
                    ("(a) CEBRA-Time", "(b) Native multisession"), args.output_dir / "figures"),
    ]
    require(not any(name in sys.modules for name in ("torch", "cebra", "sklearn", "neuro")),
            "Unexpected scientific model library imported")
    provenance = {
        "schema_version": 1,
        "classification": data["classification"],
        "renderer": relative(Path(__file__)), "renderer_sha256": sha(Path(__file__)),
        "curated_input": relative(CURATED), "curated_input_sha256": sha(CURATED),
        "selection_rule": data["selection_rule"], "semantics": data["semantics"],
        "source_provenance": data["source_provenance"], "validation": checks,
        "rendering": {
            "geometry": "Saved coordinates drawn unchanged; first and last bins use circle/cross. Same fixed orthographic camera and cubic box aspect for every panel.",
            "scaling": "Independently for each panel, equal x/y/z limit spans equal1.16 times that panel's largest coordinate range; each axis is centered on its own min/max midpoint. No coordinate normalization, PCA or cross-fit alignment. All actual bounds are recorded below.",
            "loss": "All1000 unsmoothed total-loss values; independent y limits for each own-objective trace. No loss-scale ranking between objectives.",
            "colors": dict(zip(LABELS, COLORS, strict=True)), "camera": CAMERA,
            "pdf_metadata": {"Creator": "build_geometry_figures.py", "CreationDate": None, "ModDate": None},
            "python": sys.version.split()[0], "numpy": np.__version__, "matplotlib": matplotlib.__version__,
            "default_build_access": "Curated input only; no original delivery tree, notebooks or model/source files read",
        },
        "figures": rendered,
        "scope_checks": {"new_model_fits": 0, "model_loads": 0, "notebooks_executed": 0,
                         "neural_feature_or_observation_arrays_read": 0,
                         "scientific_model_libraries_imported": False,
                         "original_results_modified": False},
    }
    write_json(args.output_dir / "geometry-figure-provenance.json", provenance)
    print("Rendered two saved-aggregate figure pairs:", args.output_dir)


if __name__ == "__main__":
    main()
