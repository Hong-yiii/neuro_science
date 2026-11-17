"""Verify retrospective class-panel context with the frozen study's own functions.

Metadata feasibility only: no neural input, fitting, assembly or result replay.
Run from the repository root with PYTHONPATH=src:. and --output a fresh JSON path.
The output is written only after every supplied expectation and frozen design agree.
"""

from __future__ import annotations

import argparse
from contextlib import ExitStack
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
from unittest.mock import patch

import numpy as np
import scipy
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC

from experiments.source_reuse_width_20261114 import study
from neuro.notebook_artifacts import no_fitting


REVISION = "a0ca80180e2bb52b90e499357d3d6965b26806da"
COUNTS = (6, 8, 9, 10, 12, 15, 18, 24, 30)
EXPECTED_FRONTIER = {
    6: (4, 18, 29, 108), 8: (3, 19, 23, 95), 9: (3, 17, 20, 83),
    10: (3, 17, 13, 58), 12: (1, 8, 15, 66), 15: (1, 8, 12, 51),
    18: (0, 0, 10, 44), 24: (0, 0, 2, 12), 30: (0, 0, 0, 0),
}
EXPECTED_TRAIN = [
    [0, 275, 246, 286, 236, 241], [259, 0, 262, 256, 251, 268],
    [273, 253, 0, 270, 264, 291], [244, 246, 264, 0, 275, 275],
    [266, 253, 275, 275, 0, 249], [251, 261, 258, 265, 273, 0],
]
EXPECTED_DEV = [
    [0, 119, 103, 115, 97, 104], [111, 0, 106, 101, 111, 103],
    [107, 102, 0, 107, 109, 114], [102, 97, 113, 0, 122, 117],
    [113, 109, 120, 114, 0, 98], [112, 106, 105, 113, 115, 0],
]
EXPECTED_SUPPORT5 = [
    [0, 28, 25, 34, 22, 21], [25, 0, 28, 31, 25, 29],
    [32, 24, 0, 30, 25, 33], [26, 23, 28, 0, 33, 32],
    [28, 28, 31, 32, 0, 28], [26, 31, 30, 31, 28, 0],
]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def forbidden(*args, **kwargs):
    raise RuntimeError("This verification permits metadata feasibility only")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError("Use a fresh receipt path; earlier evidence is preserved")
    root = Path(__file__).resolve().parents[3]
    compact = root / "data/cue-source-v1"
    design_path = root / study.DESIGN_PATH
    design = json.loads(design_path.read_text())
    pins = {}
    for name in (
        "experiments/source_reuse_width_20261114/study.py",
        "src/neuro/studies/population_grid.py",
        "src/neuro/studies/source_support_ablation.py",
        study.DESIGN_PATH,
    ):
        value = (root / name).read_bytes()
        if value != subprocess.check_output(["git", "show", f"{REVISION}:{name}"], cwd=root):
            raise ValueError(f"Frozen implementation/design differs: {name}")
        pins[name] = hashlib.sha256(value).hexdigest()

    allowed = {str((compact / name).resolve()) for name in study.HASHES}
    accessed = set()

    def audit(event, values):
        if event != "open" or not isinstance(values[0], (str, bytes)):
            return
        path = Path(values[0]).resolve()
        if path.is_relative_to(root / "outputs"):
            forbidden()
        if path.is_relative_to(compact):
            if str(path) not in allowed:
                forbidden()
            accessed.add(path.name)

    sys.addaudithook(audit)
    with ExitStack() as stack:
        stack.enter_context(no_fitting())
        for cls in (SVC, KNeighborsClassifier):
            stack.enter_context(patch.object(cls, "fit", forbidden))
        for name in ("train_case", "materialize", "prepare_design"):
            stack.enter_context(patch.object(study, name, forbidden))
        stack.enter_context(patch.object(np, "load", forbidden))
        meta = study.metadata(compact)
        if len(meta["sessions"]) != 58 or int(meta["widths"].sum()) != 195:
            raise ValueError("Unexpected full-archive session/column inventory")
        if (meta["train"].min(axis=1) >= 3).any():
            raise ValueError("A session has three training sources in every one of the 30 classes")
        matrix_train = np.zeros((6, 6), dtype=int)
        matrix_dev = np.zeros((6, 6), dtype=int)
        matrix_support = np.zeros((6, 6), dtype=int)
        for c, pair in enumerate(meta["pairs"]):
            a, b = (int(x) - 1 for x in pair.split("->"))
            matrix_train[a, b] = meta["train"][:, c].sum()
            matrix_dev[a, b] = meta["development"][:, c].sum()
            matrix_support[a, b] = (
                (meta["train"][:, c] >= 5) & (meta["development"][:, c] >= 1)
            ).sum()
        for actual, expected in ((matrix_train, EXPECTED_TRAIN),
                                 (matrix_dev, EXPECTED_DEV),
                                 (matrix_support, EXPECTED_SUPPORT5)):
            if not np.array_equal(actual, expected):
                raise ValueError("Full-session matrix does not match the owner-supplied expectation")
        print("Authenticated metadata; all three full-session matrices agree", flush=True)
        frontier = []
        # Authenticate the frozen K=9 result first, then describe other fixed-K optima.
        for count in (9, *(k for k in COUNTS if k != 9)):
            panel = study.select_panel(meta, count=count)
            endpoints = [tuple(map(int, c.split("->"))) for c in panel["conditions"]]
            occurrences = {
                name: [sum(pair[axis] == endpoint for pair in endpoints) for endpoint in range(1, 7)]
                for axis, name in enumerate(("start", "goal"))
            }
            if len(set(endpoints)) != count or any(a == b for a, b in endpoints):
                raise ValueError("Class cardinality or exclusion rule differs")
            if any(not count // 6 <= degree <= (count + 5) // 6
                   for degrees in occurrences.values() for degree in degrees):
                raise ValueError("Endpoint incidence is outside the fixed-K bounds")
            cols = [meta["pairs"].index(c) for c in panel["conditions"]]
            gates = {}
            for minimum in (5, 3):
                admitted = ((meta["train"][:, cols] >= minimum)
                            & (meta["development"][:, cols] >= 1)).all(axis=1)
                gates[str(minimum)] = {
                    "sessions": int(admitted.sum()),
                    "columns": int(meta["widths"][admitted].sum()),
                    "session_aliases": [meta["aliases"][s] for s, yes in
                                        zip(meta["sessions"], admitted, strict=True) if yes],
                }
            actual = tuple(gates[str(g)][field] for g in (5, 3)
                           for field in ("sessions", "columns"))
            if actual != EXPECTED_FRONTIER[count]:
                raise ValueError(f"Class-count frontier differs at K={count}: {actual}")
            if count == 9:
                if panel != design["panel"] or study.derive_rosters(meta, panel["conditions"]) != design["rosters"]:
                    raise ValueError("K=9 does not reproduce the full frozen panel/rosters exactly")
            frontier.append({"K": count, "panel": panel, "gates": gates,
                             "endpoint_occurrences": occurrences})
            print(f"K={count}: certified, direct gate counts {actual}", flush=True)
        frontier.sort(key=lambda r: r["K"])
        lookup = {r["K"]: r for r in frontier}
        if set(lookup[10]["panel"]["conditions"]) != set(design["panel"]["conditions"]) | {"4->1"}:
            raise ValueError("K=10 is not the stated nine-class panel plus 4->1")
        if lookup[10]["gates"]["5"]["session_aliases"] != lookup[9]["gates"]["5"]["session_aliases"]:
            raise ValueError("K=10 does not retain the same core sessions")

    if set(accessed) != set(study.HASHES):
        raise ValueError("Unexpected metadata-access coverage")
    if any(name == "torch" or name == "cebra" for name in sys.modules):
        raise ValueError("Unexpected model runtime import")
    for name, expected in design["metadata_sha256"].items():
        if sha(compact / name) != expected:
            raise ValueError("Metadata changed during verification")
    if sha(design_path) != pins[study.DESIGN_PATH]:
        raise ValueError("Frozen design was modified")
    output = {
        "classification": "retrospective metadata feasibility; no decoding or new experiment",
        "verification_date": "2026-11-16",
        "source_revision": REVISION,
        "source_sha256": pins,
        "metadata_sha256": design["metadata_sha256"],
        "functions_called": ["study.metadata", "study.select_panel", "study.derive_rosters (K=9 only)"],
        "K_was_fixed_before_class_selection": 9,
        "K9_exact_frozen_panel_and_rosters_match": True,
        "archive_inventory": {"sessions": 58, "recorded_columns": 195},
        "no_session_has_3_training_sources_in_every_class": True,
        "matrix_axes": "rows start1..6, columns goal1..6; diagonal null, not an available class",
        "eligible_training_sources": matrix_train.astype(object).tolist(),
        "eligible_development_sources": matrix_dev.astype(object).tolist(),
        "sessions_passing_single_pair_gate5": matrix_support.astype(object).tolist(),
        "frontier": frontier,
        "data_files_opened": sorted(accessed),
        "model_fits": 0,
        "neural_value_arrays_read": 0,
        "notebooks_executed": 0,
        "torch_or_cebra_imported": False,
        "frozen_design_unchanged": True,
        "runtime": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__},
        "verification_script_sha256": sha(__file__),
        "status": "passed",
    }
    for key in ("eligible_training_sources", "eligible_development_sources", "sessions_passing_single_pair_gate5"):
        for i in range(6):
            output[key][i][i] = None
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n")
    print(f"All metadata expectations verified; receipt: {args.output}", flush=True)


if __name__ == "__main__":
    main()
