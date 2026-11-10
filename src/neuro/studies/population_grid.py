"""Fresh class-requirement × session-roster study; exploratory, no import-time IO.

The design is selected from authenticated source metadata before neural scores.
Only construction/fitting implementation helpers are shared with the earlier
study: none of its panels, grids, data reconstructions or results are consumed.
"""

from __future__ import annotations

import csv
import gc
import gzip
import json
import math
import os
import time
from collections import Counter
from fractions import Fraction
from pathlib import Path

import numpy as np

from neuro.notebook_inputs import effective_pair_map
from neuro.pseudopopulation import materialize, sample_plan
from neuro.studies.source_support_ablation import (
    HASHES,
    allocation_plan,
    project_plan,
    restrict_data,
    sha,
    write_csv,
    write_json,
)

from neuro.studies.population_models import GridFitAccounting, train_case

CLASS_COUNTS = (30, 20, 15)
ROSTERS = ("S33", "S67", "S100")
POLICIES = ("U2", "R16", "F16")
PERMUTATIONS = (60000, 60001, 60002, 60003, 60004)
DESIGN_PATH = "docs/population-grid-design-20261111.json"


def metadata(root):
    """Frozen public metadata only, with embargo applied before any design choice."""
    root = Path(root)
    for name, expected in HASHES.items():
        if sha(root / name) != expected:
            raise ValueError("public metadata identity mismatch")
    with gzip.open(root / "outer_splits.csv.gz", "rt") as handle:
        outer_rows = list(csv.DictReader(handle))
    outer = {r["source_trial_id"]: r for r in outer_rows}
    with gzip.open(root / "inner_splits.csv.gz", "rt") as handle:
        inner = list(csv.DictReader(handle))
    if len(outer) != len(outer_rows) or len(
        {r["source_trial_id"] for r in inner}
    ) != len(inner):
        raise ValueError("duplicate source identity")
    units = sorted(
        json.loads((root / "manifest.json").read_text())["units"],
        key=lambda x: x["cell_id"],
    )
    sessions = sorted({u["session_id"] for u in units})
    pairs = [f"{a}->{b}" for a in range(1, 7) for b in range(1, 7) if a != b]
    for row in inner:
        current = outer[row["source_trial_id"]]
        previous = outer[current["previous_source_trial_id"]]
        if not (
            current["split"] == previous["split"] == row["original_split"] == "train"
            and current["session_id"] == previous["session_id"] == row["session_id"]
            and int(current["trial_index"]) == int(previous["trial_index"]) + 1
            and row["label"] in pairs
            and row["split"] in {"train", "validation"}
        ):
            raise ValueError("source/predecessor/label metadata disagreement")
    protected = {
        sid
        for row in inner
        if row["split"] == "validation"
        for sid in (
            row["source_trial_id"],
            outer[row["source_trial_id"]]["previous_source_trial_id"],
        )
    }
    sources = [
        row
        for row in inner
        if row["split"] == "validation"
        or not {
            row["source_trial_id"],
            outer[row["source_trial_id"]]["previous_source_trial_id"],
        }
        & protected
    ]
    if (len(inner), len(protected), len(inner) - len(sources)) != (15553, 5872, 4427):
        raise ValueError("global frozen accounting changed")
    counts = Counter((r["session_id"], r["label"], r["split"]) for r in sources)
    train = np.array(
        [[counts[s, p, "train"] for p in pairs] for s in sessions], dtype=int
    )
    dev = np.array(
        [[counts[s, p, "validation"] for p in pairs] for s in sessions], dtype=int
    )
    widths = Counter(u["session_id"] for u in units)
    return {
        "units": units,
        "sessions": sessions,
        "pairs": pairs,
        "train": train,
        "development": dev,
        "widths": np.array([widths[s] for s in sessions], dtype=int),
        "aliases": {s: f"S{i + 1:02d}" for i, s in enumerate(sessions)},
        "unit_aliases": {u["cell_id"]: f"U{i + 1:03d}" for i, u in enumerate(units)},
        "source_aliases": {
            r["source_trial_id"]: f"T{i + 1:05d}"
            for i, r in enumerate(sorted(inner, key=lambda r: r["source_trial_id"]))
        },
        "protected": protected,
        "sources": sources,
    }


def optimize_classes(meta, count, *, complete_ties):
    """Exact width optimum; optional source-total and lexicographic tie resolution."""
    from scipy.optimize import Bounds, LinearConstraint, milp
    from scipy.sparse import lil_matrix, vstack

    train, dev, widths = meta["train"], meta["development"], meta["widths"]
    ns, nc = train.shape
    bad = np.argwhere((train < 2) | (dev < 1))
    # x=class selected, z=session selected, y=x*z for source-count tie objective.
    nv = nc + ns + (ns * nc if complete_ties else 0)
    nr = len(bad) + 13 + (ns * nc * 3 if complete_ties else 0)
    matrix = lil_matrix((nr, nv), dtype=float)
    lower, upper = np.full(nr, -np.inf), np.full(nr, np.inf)
    for i, (s, c) in enumerate(bad):
        matrix[i, c] = matrix[i, nc + s] = 1
        upper[i] = 1
    offset = len(bad)
    matrix[offset, :nc] = 1
    lower[offset] = upper[offset] = count
    for c, pair in enumerate(meta["pairs"]):
        start, goal = map(int, pair.split("->"))
        matrix[offset + start, c] = 1
        matrix[offset + 6 + goal, c] = 1
    lower[offset + 1 : offset + 13] = count // 6
    upper[offset + 1 : offset + 13] = math.ceil(count / 6)
    if complete_ties:
        i = offset + 13
        for s in range(ns):
            for c in range(nc):
                y = nc + ns + s * nc + c
                matrix[i, y], matrix[i, c], upper[i] = 1, -1, 0
                matrix[i + 1, y], matrix[i + 1, nc + s], upper[i + 1] = 1, -1, 0
                (
                    matrix[i + 2, y],
                    matrix[i + 2, c],
                    matrix[i + 2, nc + s],
                    upper[i + 2],
                ) = -1, 1, 1, 1
                i += 3
    constraints = LinearConstraint(matrix.tocsr(), lower, upper)
    integrality = np.r_[np.ones(nc + ns), np.zeros(nv - nc - ns)]
    lb, ub = np.zeros(nv), np.ones(nv)

    def solve(objective, *, infeasible_allowed=False):
        result = milp(
            objective,
            integrality=integrality,
            bounds=Bounds(lb, ub),
            constraints=constraints,
            options={"time_limit": 30, "mip_rel_gap": 0},
        )
        if infeasible_allowed and result.status == 2:
            return None
        if result.status != 0 or result.x is None or result.mip_gap > 1e-8:
            raise RuntimeError(
                f"metadata optimization is not certified optimal: {result.message}"
            )
        return result

    objective = np.zeros(nv)
    objective[nc : nc + ns] = -widths
    result = solve(objective)
    best_width = int(round(-result.fun))
    optimal_sources = None
    if complete_ties:
        width_constraint = -objective
        constraints = LinearConstraint(
            vstack([constraints.A, width_constraint]),
            np.r_[constraints.lb, best_width],
            np.r_[constraints.ub, best_width],
        )
        objective = np.zeros(nv)
        objective[nc + ns :] = -train.reshape(-1)
        result = solve(objective)
        optimal_sources = int(round(-result.fun))
        constraints = LinearConstraint(
            vstack([constraints.A, -objective]),
            np.r_[constraints.lb, optimal_sources],
            np.r_[constraints.ub, optimal_sources],
        )
        # Canonical first lexicographic class list among both objective ties.
        objective = np.zeros(nv)
        for c in range(nc):
            lb[c] = 1
            trial = solve(objective, infeasible_allowed=True)
            if trial is None:
                lb[c] = ub[c] = 0
            else:
                result = trial
                ub[c] = 1
        result = solve(objective)
    selected = np.flatnonzero(result.x[:nc] > 0.5)
    sessions = np.flatnonzero(
        np.all((train[:, selected] >= 2) & (dev[:, selected] >= 1), axis=1)
    )
    if len(selected) != count or int(widths[sessions].sum()) != best_width:
        raise ValueError("optimizer solution failed direct width reconciliation")
    if (
        optimal_sources is not None
        and int(train[np.ix_(sessions, selected)].sum()) != optimal_sources
    ):
        raise ValueError("optimizer source objective failed reconciliation")
    return {
        "class_count": count,
        "conditions": [meta["pairs"][c] for c in selected],
        "maximum_columns": best_width,
        "eligible_sessions": len(sessions),
        "optimal_training_sources_at_maximum_width": optimal_sources,
        "solver_status": "optimal",
        "mip_gap": float(result.mip_gap),
    }


def describe_prefix(meta, conditions, selected):
    ci = [meta["pairs"].index(c) for c in conditions]
    si = [meta["sessions"].index(s) for s in selected]
    train, dev = meta["train"][np.ix_(si, ci)], meta["development"][np.ix_(si, ci)]
    k = len(conditions)
    return {
        "class_count": k,
        "sessions": len(si),
        "units": int(meta["widths"][si].sum()),
        "train_sources": int(train.sum()),
        "development_sources": int(dev.sum()),
        "train_min": int(train.min()),
        "train_p25": float(np.quantile(train, 0.25)),
        "train_median": float(np.median(train)),
        "train_p75": float(np.quantile(train, 0.75)),
        "train_max": int(train.max()),
        "train_harmonic_mean": float(train.size / np.sum(1 / train)),
        "development_singletons": int((dev == 1).sum()),
        "session_class_pools": int(dev.size),
        "balanced_no_reuse_rows": int(k * train.min()),
        "classwise_no_reuse_rows": int(train.min(axis=0).sum()),
        "session_aliases": [meta["aliases"][s] for s in selected],
    }


def selection_tables(meta, panel):
    conditions = panel["conditions"]
    ci = [meta["pairs"].index(c) for c in conditions]
    eligible = np.flatnonzero(
        np.all((meta["train"][:, ci] >= 2) & (meta["development"][:, ci] >= 1), axis=1)
    )
    ranked = sorted(
        eligible,
        key=lambda i: (
            -Fraction(len(ci), 1)
            / sum((Fraction(1, int(n)) for n in meta["train"][i, ci]), Fraction()),
            -int(meta["widths"][i]),
            -int(meta["train"][i, ci].sum()),
            meta["sessions"][i],
        ),
    )
    ordered = [meta["sessions"][i] for i in ranked]
    prefixes = [
        describe_prefix(meta, conditions, ordered[:n])
        for n in range(1, len(ordered) + 1)
    ]
    grid = []
    for tag, number in zip(
        ROSTERS,
        (math.ceil(len(ordered) / 3), math.ceil(2 * len(ordered) / 3), len(ordered)),
        strict=True,
    ):
        record = {
            "configuration": f"K{len(ci)}_{tag}",
            "roster": tag,
            **describe_prefix(meta, conditions, ordered[:number]),
        }
        if record["units"] < 8:
            raise ValueError(
                "frozen common eight-dimensional representation infeasible"
            )
        grid.append(record)
    if len({r["sessions"] for r in grid}) != 3:
        raise ValueError("three distinct rosters required")
    return prefixes, grid


def prepare_design(root, destination):
    """Metadata-only optimization and durable public/aliased frozen design."""
    import scipy

    meta = metadata(root)
    panels = [optimize_classes(meta, k, complete_ties=True) for k in CLASS_COUNTS]
    frontier = [optimize_classes(meta, k, complete_ties=False) for k in range(6, 31)]
    prefixes, grid = [], []
    for panel in panels:
        p, g = selection_tables(meta, panel)
        prefixes.extend(p)
        grid.extend(g)
    design = {
        "study": "population-grid-20261111",
        "classification": "exploratory",
        "metadata_sha256": HASHES,
        "global_development_contributors": len(meta["protected"]),
        "class_counts": list(CLASS_COUNTS),
        "panels": panels,
        "grid": grid,
        "prefix_frontier": prefixes,
        "class_count_width_frontier": frontier,
        "selection": "maximize width, then training-source total, then lexicographic class list; nested harmonic-support-ranked roster thirds",
        "scipy": scipy.__version__,
    }
    write_json(destination, design)
    return design


def validate_design(meta, design):
    if design["metadata_sha256"] != HASHES or design["class_counts"] != list(
        CLASS_COUNTS
    ):
        raise ValueError("frozen design metadata/configuration differs")
    for panel in design["panels"]:
        k = panel["class_count"]
        pairs = panel["conditions"]
        if len(pairs) != k or len(set(pairs)) != k:
            raise ValueError("invalid fixed class list")
        for endpoint in (0, 1):
            counts = Counter(int(p.split("->")[endpoint]) for p in pairs)
            if set(counts) != set(range(1, 7)) or any(
                n not in {k // 6, math.ceil(k / 6)} for n in counts.values()
            ):
                raise ValueError("endpoint degree constraint violated")
        p, g = selection_tables(meta, panel)
        if g != [r for r in design["grid"] if r["class_count"] == k] or p != [
            r for r in design["prefix_frontier"] if r["class_count"] == k
        ]:
            raise ValueError("frozen support/roster accounting changed")
    return True


def configuration(design):
    return {
        "study": "population-grid-20261111",
        "classification": "exploratory",
        "design": design,
        "observed_seeds": [0, 1, 2],
        "policies": list(POLICIES),
        "permutation_seeds": list(PERMUTATIONS),
        "null_roster": "S100",
        "null_policies": ["U2", "F16"],
        "iterations": 1000,
        "batch_size": 256,
        "output_dimension": 7,
        "hidden": 32,
        "learning_rate": 0.0003,
        "base_logistic_C": 0.01,
        "logistic_max_iter": 2000,
        "decoder_families": ["logistic", "svm", "knn", "lda"],
        "native_mode": "discrete joint-pair supervised; equal-session mean; per-session batch floor256/S",
        "development_rows_per_class": 8,
        "development_seed": 0,
        "source_subset_seed_base": 20261111,
        "limits": {
            "memory_gib": 4,
            "cpu_cores": 2,
            "swap_bytes": 0,
            "run_seconds": 21600,
            "cebra_fit_seconds": 180,
            "native_fit_seconds": 180,
        },
        "expected_fit_counts": {
            "cebra": 111,
            "pca": 111,
            "native": 111,
            "logistic": 1332,
            "lda": 1332,
            "svm": 1332,
            "knn": 1332,
            "optimizer_updates": 222000,
        },
    }


def reconstruct(root, meta, design):
    if os.environ.get("NEURO_GRID_ALLOW_BIOLOGICAL") != "1":
        raise PermissionError("explicit new-study biological flag required")
    from neuro.cue_source import inspect_compact, reconstruct_compact

    validate_design(meta, design)
    root = Path(root).resolve()
    base = json.loads((root / "notebook-config.json").read_text())
    base.update(data_root=str(root), manifest_directory=str(root))
    result, audits = {}, {}
    for panel in design["panels"]:
        k = panel["class_count"]
        cfg = {
            **base,
            "analysis_panel": {
                "conditions": panel["conditions"],
                "minimum_train_sources": 2,
                "minimum_development_sources": 1,
            },
        }
        selection = inspect_compact(cfg)
        data, audit = reconstruct_compact(selection, interpret_neural=True)
        full = next(
            g for g in design["grid"] if g["class_count"] == k and g["roster"] == "S100"
        )
        if len(data.units) != full["units"] or set(
            meta["aliases"][s] for s in data.block_ids
        ) != set(full["session_aliases"]):
            raise ValueError("native reconstruction differs from metadata-only roster")
        counts = Counter(s.split_id for s in data.sources)
        if counts != {
            "train": full["train_sources"],
            "development": full["development_sources"],
        }:
            raise ValueError("native source counts differ from frozen design")
        result[k], audits[str(k)] = data, {"metadata": selection.audit, "neural": audit}
    return result, audits


def select_two(full, mapping, seed):
    rng = np.random.default_rng(20261111 + seed)
    keep = set()
    for condition, _ in full.target_definition.condition_to_target:
        for block in full.block_ids:
            pool = sorted(
                s.source_id
                for s in full.sources
                if s.split_id == "train"
                and s.block_id == block
                and mapping[s.source_id] == condition
            )
            if len(pool) < 2:
                raise ValueError("two-source control is infeasible")
            keep.update(rng.choice(pool, 2, replace=False).tolist())
    return restrict_data(full, train_source_ids=keep)


def paired_plans(full, meta, design, *, seed, permutation=None):
    k = len(full.target_definition.condition_to_target)
    mapping = effective_pair_map(full, permutation_seed=permutation)
    reduced = select_two(full, mapping, seed)
    train = {
        "U2": (
            reduced,
            allocation_plan(
                reduced,
                mapping,
                rows_per_class=2,
                seed=seed,
                policy="sample-without-replacement",
            ),
        ),
        "R16": (
            reduced,
            allocation_plan(
                reduced,
                mapping,
                rows_per_class=16,
                seed=700000 + seed,
                policy="balanced-cycle",
            ),
        ),
        "F16": (
            full,
            allocation_plan(
                full, mapping, rows_per_class=16, seed=seed, policy="balanced-cycle"
            ),
        ),
    }
    dev = sample_plan(
        full,
        split_id="development",
        rows_per_condition=8,
        seed=0,
        effective_conditions=mapping,
    )
    plans = {}
    for roster in (g for g in design["grid"] if g["class_count"] == k):
        aliases = set(roster["session_aliases"])
        unit_ids = [
            u.unit_id for u in full.units if meta["aliases"][u.block_id] in aliases
        ]
        for policy, (sources, plan) in train.items():
            smaller = restrict_data(sources, unit_ids=unit_ids)
            plans[roster["roster"], policy] = (
                smaller,
                project_plan(plan, sources, smaller, mapping),
                project_plan(dev, full, smaller, mapping),
            )
    return plans


def verify_plans(plans, *, numerical_rank=False):
    """Actual plan/array invariants; optional training-only rank diagnostic, no fit."""
    ranks = []
    for policy in POLICIES:
        full_data, ft, fd = plans["S100", policy]
        full = [materialize(full_data, p) for p in (ft, fd)]
        for roster in ROSTERS:
            data, train, dev = plans[roster, policy]
            ui = [u.unit_id for u in full_data.units]
            indices = [ui.index(u.unit_id) for u in data.units]
            small = [materialize(data, p) for p in (train, dev)]
            for a, b in zip(full, small, strict=True):
                np.testing.assert_array_equal(b.values, a.values[:, indices])
                np.testing.assert_array_equal(b.targets, a.targets)
            usage = Counter(sid for r in train.rows for sid in r.source_ids)
            if policy == "U2" and set(usage.values()) != {1}:
                raise ValueError("U2 source multiplicity violated")
            if policy == "R16" and set(usage.values()) != {8}:
                raise ValueError("R16 source multiplicity violated")
            if policy == "F16" and set(usage) != {
                s.source_id for s in data.sources if s.split_id == "train"
            }:
                raise ValueError("F16 did not cover all eligible current sources")
            if numerical_rank:
                flat = (
                    small[0]
                    .values.transpose(0, 2, 1)
                    .reshape(-1, len(data.units))
                    .astype(np.float64)
                )
                sd = flat.std(axis=0)
                standardized = (
                    (flat - flat.mean(axis=0)) / np.where(sd > 0, sd, 1)
                ).astype(np.float32)
                standardized -= standardized.mean(axis=0)
                singular = np.linalg.svd(standardized, compute_uv=False)
                tolerance = (
                    max(standardized.shape) * np.finfo(np.float32).eps * singular[0]
                )
                rank = int(np.count_nonzero(singular > tolerance))
                if rank < 7:
                    raise ValueError(
                        "training numerical rank cannot support common PCA7"
                    )
                ranks.append(
                    {
                        "roster": roster,
                        "policy": policy,
                        "training_rank": rank,
                        "constant_columns": int(np.count_nonzero(sd == 0)),
                    }
                )
    for roster in ROSTERS:
        arrays = [
            materialize(plans[roster, policy][0], plans[roster, policy][2])
            for policy in POLICIES
        ]
        for array in arrays[1:]:
            np.testing.assert_array_equal(array.values, arrays[0].values)
            np.testing.assert_array_equal(array.targets, arrays[0].targets)
        pools = [
            {sid for r in plans[roster, p][1].rows for sid in r.source_ids}
            for p in ("U2", "R16")
        ]
        if pools[0] != pools[1]:
            raise ValueError("U2/R16 actual source identities differ")
    return ranks


def run_grid(data, meta, config, run_root):
    root = Path(run_root)
    if config != configuration(config["design"]):
        raise ValueError("grid differs from frozen configuration")
    aggregate = root / "aggregates"
    aggregate.mkdir(mode=0o700)
    results = {k: [] for k in ("metrics", "confusions", "learning", "trajectories")}
    streamed = (
        "source_usage",
        "pool_usage",
        "source_errors",
        "class_errors",
        "overlap",
    )
    handles, writers = {}, {}
    attempts, rank_checks = [], []
    accounting = GridFitAccounting(cebra=True).start()
    started = time.monotonic()
    try:
        for key in streamed:
            handles[key] = (aggregate / (key + ".csv")).open("x", newline="")
        worlds = [("observed", None, (0, 1, 2))] + [
            (f"permuted{p}", p, (0,)) for p in PERMUTATIONS
        ]
        for world, permutation, seeds in worlds:
            for k in CLASS_COUNTS:
                for seed in seeds:
                    plans = paired_plans(
                        data[k],
                        meta,
                        config["design"],
                        seed=seed,
                        permutation=permutation,
                    )
                    ranks = verify_plans(plans, numerical_rank=True)
                    rank_checks.extend(
                        {"world": world, "K": k, "seed": seed, **r} for r in ranks
                    )
                    selected = (
                        [(r, p) for r in ROSTERS for p in POLICIES]
                        if permutation is None
                        else [("S100", p) for p in ("U2", "F16")]
                    )
                    for roster, policy in selected:
                        if time.monotonic() - started > config["limits"]["run_seconds"]:
                            raise TimeoutError("new study grid exceeded deadline")
                        arm = f"K{k}_{roster}_{policy}"
                        case = {
                            "id": f"{world}_seed{seed}_{arm}",
                            "world": world,
                            "seed": seed,
                            "arm": arm,
                            "class_count": k,
                            "roster": roster,
                            "sampling": policy,
                        }
                        print("Fitting", case["id"], flush=True)
                        attempts.append({**case, "status": "started"})
                        with (root / "attempt-log.jsonl").open("a") as log:
                            log.write(json.dumps(attempts[-1]) + "\n")
                        result = train_case(
                            case,
                            *plans[roster, policy],
                            meta=meta,
                            config=config,
                            run_root=root,
                        )
                        for key in streamed:
                            values = result.pop(key)
                            if key not in writers:
                                writers[key] = csv.DictWriter(
                                    handles[key], fieldnames=list(values[0])
                                )
                                writers[key].writeheader()
                            writers[key].writerows(values)
                            handles[key].flush()
                        result.pop("fit_counts")
                        for key, value in result.items():
                            results[key].extend(
                                value if isinstance(value, list) else [value]
                            )
                        attempts[-1]["status"] = "completed"
                        with (root / "attempt-log.jsonl").open("a") as log:
                            log.write(json.dumps(attempts[-1]) + "\n")
                        gc.collect()
        if (
            dict(accounting.counts) != config["expected_fit_counts"]
            or len(attempts) != 111
        ):
            raise ValueError("actual fit accounting differs from frozen budget")
        for key, value in results.items():
            if key == "metrics":
                write_csv(aggregate / (key + ".csv"), value)
            else:
                write_json(aggregate / (key + ".json"), value)
        write_json(root / "attempts.json", attempts)
        write_json(root / "training-rank-checks.json", rank_checks)
        write_json(
            aggregate / "fit_accounting.json",
            {
                "cases": 111,
                "counts": dict(accounting.counts),
                "reloaded_encoders_checked": 444,
                "reloaded_readouts_checked": 5328,
                "composed_readout_splits_checked": 10656,
                "grid_seconds": time.monotonic() - started,
            },
        )
        print("Completed111cases; actual fits", dict(accounting.counts), flush=True)
        return results
    except BaseException as exc:
        if attempts and attempts[-1]["status"] == "started":
            attempts[-1].update(status="failed", exception=type(exc).__name__)
            with (root / "attempt-log.jsonl").open("a") as log:
                log.write(json.dumps(attempts[-1]) + "\n")
        write_json(
            root / "grid-failure.json",
            {
                "status": "failed",
                "exception": type(exc).__name__,
                "actual_fit_counts": dict(accounting.counts),
                "attempts": attempts,
            },
        )
        raise
    finally:
        for handle in handles.values():
            handle.close()
        write_json(root / "actual-fit-counts.json", accounting.stop())
