"""Focused November 14 source reuse / width study; no import-time data access."""

from __future__ import annotations

import csv
import gc
import hashlib
import json
import math
import os
from collections import Counter
from fractions import Fraction
from pathlib import Path

import numpy as np

from neuro.notebook_inputs import effective_pair_map
from neuro.pseudopopulation import materialize, sample_plan
from neuro.studies.population_grid import metadata
from neuro.studies.population_models import train_case
from neuro.studies.population_models import GridFitAccounting as GridFitAccounting
from neuro.studies.source_support_ablation import (
    HASHES,
    allocation_plan,
    project_plan,
    restrict_data,
    sha,
    write_csv,
    write_json,
)

STUDY = "source-reuse-width-20261114"
DESIGN_PATH = "docs/experiments/source-reuse-width-20261114/design.json"
PERMUTATIONS = tuple(range(61000, 61005))
ARMS = ("B2", "B3", "B5", "U3", "Wmid", "Wfull")
PART_ARMS = {"reuse": ("B2", "B3", "B5", "U3"), "width": ("B3", "Wmid", "Wfull")}


def select_panel(meta, count=9):
    """Certified lexicographic metadata objectives: width@5, width@3, classes.

    Each endpoint occurs floor(K/6)..ceil(K/6) times. No neural values or scores
    enter selection. Complete eligibility is recomputed from the chosen classes.
    """
    from scipy.optimize import Bounds, LinearConstraint, milp
    from scipy.sparse import lil_matrix, vstack

    train, dev, widths = meta["train"], meta["development"], meta["widths"]
    ns, nc = train.shape
    bad = [
        (level, s, c)
        for level, minimum in enumerate((5, 3))
        for s, c in np.argwhere((train < minimum) | (dev < 1))
    ]
    nv = nc + 2 * ns
    a = lil_matrix((len(bad) + 13, nv), dtype=float)
    lower, upper = np.full(a.shape[0], -np.inf), np.full(a.shape[0], np.inf)
    for row, (level, s, c) in enumerate(bad):
        a[row, c] = a[row, nc + level * ns + s] = 1
        upper[row] = 1
    offset = len(bad)
    a[offset, :nc] = 1
    lower[offset] = upper[offset] = count
    for c, pair in enumerate(meta["pairs"]):
        start, goal = map(int, pair.split("->"))
        a[offset + start, c] = a[offset + 6 + goal, c] = 1
    lower[offset + 1 :] = count // 6
    upper[offset + 1 :] = math.ceil(count / 6)
    constraints = LinearConstraint(a.tocsr(), lower, upper)
    lb, ub = np.zeros(nv), np.ones(nv)

    def solve(objective, allow_infeasible=False):
        result = milp(
            objective,
            integrality=np.ones(nv),
            bounds=Bounds(lb, ub),
            constraints=constraints,
            options={"time_limit": 60, "mip_rel_gap": 0},
        )
        if allow_infeasible and result.status == 2:
            return None
        if result.status != 0 or result.x is None or result.mip_gap > 1e-8:
            raise RuntimeError("uncertified metadata optimization: " + result.message)
        return result

    objectives = []
    for level in range(2):
        objective = np.zeros(nv)
        objective[nc + level * ns : nc + (level + 1) * ns] = -widths
        result = solve(objective)
        optimum = int(round(-result.fun))
        objectives.append(optimum)
        constraints = LinearConstraint(
            vstack([constraints.A, -objective]),
            np.r_[constraints.lb, optimum],
            np.r_[constraints.ub, optimum],
        )
    for c in range(nc):
        lb[c] = 1
        if solve(np.zeros(nv), allow_infeasible=True) is None:
            lb[c] = ub[c] = 0
        else:
            ub[c] = 1
    result = solve(np.zeros(nv))
    indices = np.flatnonzero(result.x[:nc] > 0.5)
    if len(indices) != count:
        raise ValueError("wrong selected class count")
    for minimum, optimum in zip((5, 3), objectives, strict=True):
        admitted = ((train[:, indices] >= minimum) & (dev[:, indices] >= 1)).all(1)
        if int(widths[admitted].sum()) != optimum:
            raise ValueError("width objective failed direct reconciliation")
    return {
        "conditions": [meta["pairs"][i] for i in indices],
        "class_count": count,
        "maximum_columns_min5": objectives[0],
        "maximum_columns_min3_at_min5_optimum": objectives[1],
        "solver_status": "optimal",
        "mip_gap": 0.0,
    }


def derive_rosters(meta, conditions):
    cols = [meta["pairs"].index(c) for c in conditions]
    eligible = {
        minimum: [
            s
            for s in range(len(meta["sessions"]))
            if (
                (meta["train"][s, cols] >= minimum)
                & (meta["development"][s, cols] >= 1)
            ).all()
        ]
        for minimum in (5, 3)
    }
    core = eligible[5]
    extras = [s for s in eligible[3] if s not in core]

    def harmonic(s):
        return Fraction(len(cols), 1) / sum(
            (Fraction(1, int(meta["train"][s, c])) for c in cols), Fraction()
        )

    extras.sort(key=lambda s: (-harmonic(s), meta["aliases"][meta["sessions"][s]]))
    target = (sum(meta["widths"][core]) + sum(meta["widths"][eligible[3]])) / 2
    candidates = [
        (abs(sum(meta["widths"][core + extras[:n]]) - target), n)
        for n in range(1, len(extras))
    ]
    if len(core) < 2 or not candidates:
        raise ValueError("insufficient sessions for native and three nested widths")
    middle_n = min(candidates)[1]
    rosters = {"core": core, "middle": core + extras[:middle_n], "full": core + extras}
    result = {}
    for name, indices in rosters.items():
        selected_train = meta["train"][np.ix_(indices, cols)]
        selected_dev = meta["development"][np.ix_(indices, cols)]
        result[name] = {
            "sessions": len(indices),
            "units": int(meta["widths"][indices].sum()),
            "session_aliases": sorted(
                meta["aliases"][meta["sessions"][s]] for s in indices
            ),
            "available_train_sources": int(selected_train.sum()),
            "available_development_sources": int(selected_dev.sum()),
            "minimum_train_sources": int(selected_train.min()),
            "minimum_development_sources": int(selected_dev.min()),
            "development_singleton_pools": int((selected_dev == 1).sum()),
        }
    return result


def prepare_design(root, destination):
    meta = metadata(root)
    panel = select_panel(meta)
    design = {
        "study": STUDY,
        "classification": "exploratory",
        "date": "2026-11-14",
        "metadata_sha256": HASHES,
        "panel": panel,
        "rosters": derive_rosters(meta, panel["conditions"]),
        "selection": "maximize minimum-five width, then minimum-three width, then lexicographic class list; balanced endpoint degree; exact harmonic order for added sessions",
    }
    write_json(destination, design)
    return design


def validate_design(meta, design):
    if design["study"] != STUDY or design["metadata_sha256"] != HASHES:
        raise ValueError("design provenance mismatch")
    panel = design["panel"]
    if len(set(panel["conditions"])) != 9 or panel["class_count"] != 9:
        raise ValueError("fixed nine-class task changed")
    for endpoint in (0, 1):
        degrees = Counter(c.split("->")[endpoint] for c in panel["conditions"])
        if set(degrees) != set(map(str, range(1, 7))) or set(degrees.values()) != {
            1,
            2,
        }:
            raise ValueError("endpoint balance changed")
    if derive_rosters(meta, panel["conditions"]) != design["rosters"]:
        raise ValueError("frozen roster support changed")
    if (
        design["rosters"]["core"]["units"] != panel["maximum_columns_min5"]
        or design["rosters"]["full"]["units"]
        != panel["maximum_columns_min3_at_min5_optimum"]
    ):
        raise ValueError("width objective mismatch")
    return True


def configuration(design):
    from neuro.studies.population_grid import configuration as base_configuration

    cfg = base_configuration(design)
    for key in ("policies", "null_roster", "null_policies"):
        cfg.pop(key)
    cfg.update(
        study=STUDY,
        source_subset_seed_base=20261114,
        permutation_seeds=list(PERMUTATIONS),
        arms=list(ARMS),
        part_arms={k: list(v) for k, v in PART_ARMS.items()},
        training_rows_per_class=16,
        case_count=48,
    )
    cfg["limits"]["run_seconds"] = 10800
    cfg["expected_fit_counts"] = {
        k: v * 48 // 111 for k, v in cfg["expected_fit_counts"].items()
    }
    return cfg


def reconstruct(root, meta, design):
    if os.environ.get("NEURO_REUSE_ALLOW_BIOLOGICAL") != "1":
        raise PermissionError("explicit new-study biological flag required")
    from neuro.cue_source import inspect_compact, reconstruct_compact

    validate_design(meta, design)
    root = Path(root).resolve()
    cfg = json.loads((root / "notebook-config.json").read_text())
    cfg.update(
        data_root=str(root),
        manifest_directory=str(root),
        analysis_panel={
            "conditions": design["panel"]["conditions"],
            "minimum_train_sources": 3,
            "minimum_development_sources": 1,
        },
    )
    selection = inspect_compact(cfg)
    data, audit = reconstruct_compact(selection, interpret_neural=True)
    roster = design["rosters"]["full"]
    if (
        len(data.units) != roster["units"]
        or sorted(meta["aliases"][b] for b in data.block_ids)
        != roster["session_aliases"]
    ):
        raise ValueError("reconstruction differs from frozen full roster")
    if Counter(s.split_id for s in data.sources) != {
        "train": roster["available_train_sources"],
        "development": roster["available_development_sources"],
    }:
        raise ValueError("source counts differ from metadata")
    return data, {"metadata": selection.audit, "neural": audit}


def source_order(pool, *, block, condition, seed):
    # Stable per-pool ordering: unchanged by adding/removing other pools/columns.
    def key(sid):
        return hashlib.sha256(
            json.dumps(
                [20261114, seed, block, condition, sid], separators=(",", ":")
            ).encode()
        ).hexdigest()

    return sorted(pool, key=key)


def paired_plans(full, meta, design, *, seed, permutation=None):
    # One map and one development plan on the full admitted union per world.
    mapping = effective_pair_map(full, permutation_seed=permutation)
    dev = sample_plan(
        full,
        split_id="development",
        rows_per_condition=8,
        seed=0,
        effective_conditions=mapping,
    )
    pool_orders = {}
    for condition, _ in full.target_definition.condition_to_target:
        for block in full.block_ids:
            pool = [
                s.source_id
                for s in full.sources
                if s.split_id == "train"
                and s.block_id == block
                and mapping[s.source_id] == condition
            ]
            pool_orders[block, condition] = source_order(
                pool, block=block, condition=condition, seed=seed
            )
    sets = {
        r: {
            u.unit_id
            for u in full.units
            if meta["aliases"][u.block_id] in design["rosters"][r]["session_aliases"]
        }
        for r in ("core", "middle", "full")
    }
    plans = {}
    # The three-source full-width plan is projected, not resampled, for width arms.
    for arm, b, roster, rows in (
        ("B2", 2, "core", 16),
        ("B3", 3, "full", 16),
        ("B5", 5, "core", 16),
        ("U3", 3, "core", 3),
    ):
        population = restrict_data(full, unit_ids=sets[roster])
        keep = set()
        for condition, _ in population.target_definition.condition_to_target:
            for block in population.block_ids:
                pool = pool_orders[block, condition]
                if len(pool) < b:
                    raise ValueError("requested source budget infeasible")
                keep.update(pool[:b])
        population = restrict_data(population, train_source_ids=keep)
        plan = allocation_plan(
            population,
            mapping,
            rows_per_class=rows,
            seed=700000 + seed,
            policy="sample-without-replacement" if arm == "U3" else "balanced-cycle",
        )
        projected_dev = project_plan(dev, full, population, mapping)
        if arm == "B3":
            plans["Wfull"] = (population, plan, projected_dev)
            for name, target_roster in (("Wmid", "middle"), ("B3", "core")):
                smaller = restrict_data(population, unit_ids=sets[target_roster])
                plans[name] = (
                    smaller,
                    project_plan(plan, population, smaller, mapping),
                    project_plan(dev, full, smaller, mapping),
                )
        else:
            plans[arm] = (population, plan, projected_dev)
    return {arm: plans[arm] for arm in ARMS}


def verify_plans(plans, *, numerical_rank=False):
    arrays, summaries = {}, []
    for arm, (data, train, dev) in plans.items():
        arrays[arm] = [materialize(data, p) for p in (train, dev)]
        by_id = {s.source_id: s for s in data.sources}
        contributors = [
            {
                v
                for row in p.rows
                for sid in row.source_ids
                for v in (sid, *by_id[sid].dependency_ids)
            }
            for p in (train, dev)
        ]
        if contributors[0] & contributors[1]:
            raise ValueError("cross-split contributor overlap")
        b = {"B2": 2, "B5": 5}.get(arm, 3)
        quota = 3 if arm == "U3" else 16
        conditions = {c for c, _ in data.target_definition.condition_to_target}
        if (
            len(conditions) != 9
            or Counter(r.condition for r in train.rows)
            != {c: quota for c in conditions}
            or Counter(r.condition for r in dev.rows) != {c: 8 for c in conditions}
        ):
            raise ValueError("class identities or per-class row quotas changed")
        counts = Counter(sid for row in train.rows for sid in row.source_ids)
        if len(counts) != len(data.block_ids) * 9 * b or set(counts.values()) != {
            quota // b,
            math.ceil(quota / b),
        }:
            raise ValueError("source multiplicity/budget changed")
        record = {
            "arm": arm,
            "units": len(data.units),
            "sessions": len(data.block_ids),
            "source_budget": b,
            "rows_per_class": quota,
            "distinct_train_sources": len(counts),
            "training_source_extra_draw_fraction": 1 - b / quota,
            "overlapping_contributors": 0,
        }
        if numerical_rank:
            values = arrays[arm][0].values
            flat = (
                values.transpose(0, 2, 1)
                .reshape(-1, len(data.units))
                .astype(np.float64)
            )
            sd = flat.std(0)
            scaled = ((flat - flat.mean(0)) / np.where(sd > 0, sd, 1)).astype(
                np.float32
            )
            scaled -= scaled.mean(0)
            singular = np.linalg.svd(scaled, compute_uv=False)
            rank = int(
                (
                    singular
                    > max(scaled.shape) * np.finfo(np.float32).eps * singular[0]
                ).sum()
            )
            if rank < 7:
                raise ValueError("training rank below frozen PCA7")
            record.update(training_rank=rank, constant_columns=int((sd == 0).sum()))
        summaries.append(record)
    for arm in ("B2", "B5", "U3"):
        if plans[arm][2].rows != plans["B3"][2].rows:
            raise ValueError("fixed-roster development row/source lineage changed")
        np.testing.assert_array_equal(arrays[arm][1].values, arrays["B3"][1].values)
        np.testing.assert_array_equal(arrays[arm][1].targets, arrays["B3"][1].targets)
    for arm in ("B3", "Wmid"):
        indices = [
            arrays["Wfull"][0].unit_ids.index(u) for u in arrays[arm][0].unit_ids
        ]
        block_indices = [
            plans["Wfull"][0].block_ids.index(b) for b in plans[arm][0].block_ids
        ]
        for smaller_plan, full_plan in zip(
            plans[arm][1:], plans["Wfull"][1:], strict=True
        ):
            for smaller_row, full_row in zip(
                smaller_plan.rows, full_plan.rows, strict=True
            ):
                if (
                    smaller_row.row_id,
                    smaller_row.condition,
                    smaller_row.target,
                    smaller_row.source_ids,
                ) != (
                    full_row.row_id,
                    full_row.condition,
                    full_row.target,
                    tuple(full_row.source_ids[i] for i in block_indices),
                ):
                    raise ValueError("width projection changed row/source lineage")
        for small, full in zip(arrays[arm], arrays["Wfull"], strict=True):
            np.testing.assert_array_equal(small.values, full.values[:, indices])
            np.testing.assert_array_equal(small.targets, full.targets)
    sources = {
        a: {s for row in plans[a][1].rows for s in row.source_ids}
        for a in ("B2", "B3", "B5", "U3")
    }
    if (
        not sources["B2"] < sources["B3"] < sources["B5"]
        or sources["U3"] != sources["B3"]
    ):
        raise ValueError("nested/shared source identities changed")
    return summaries


def schedule():
    return [
        {
            "id": f"{world}_seed{seed}_{arm}",
            "world": world,
            "seed": seed,
            "arm": arm,
            "class_count": 9,
            "source_budget": {"B2": 2, "B5": 5}.get(arm, 3),
            "rows_per_class": 3 if arm == "U3" else 16,
            "roster": {"Wmid": "middle", "Wfull": "full"}.get(arm, "core"),
        }
        for world, seeds in [("observed", (0, 1, 2))]
        + [(f"permuted{p}", (0,)) for p in PERMUTATIONS]
        for seed in seeds
        for arm in ARMS
    ]


def run_part(data, meta, config, root, part, accounting):
    """Fit the part's new cases; B3 is a shared bridge fitted only by part one."""
    root = Path(root)
    if config != configuration(config["design"]):
        raise ValueError("execution configuration differs from frozen study")
    arms = PART_ARMS[part] if part == "reuse" else ("Wmid", "Wfull")
    selected = [c for c in schedule() if c["arm"] in arms]
    aggregate = root / ("aggregates_" + part)
    aggregate.mkdir(mode=0o700)
    results = {k: [] for k in ("metrics", "confusions", "learning", "trajectories")}
    streamed = (
        "source_usage",
        "pool_usage",
        "source_errors",
        "class_errors",
        "overlap",
    )
    handles, writers, attempts = {}, {}, []
    previous, plans = None, None
    try:
        for key in streamed:
            handles[key] = (aggregate / (key + ".csv")).open("x", newline="")
        for case in selected:
            key = case["world"], case["seed"]
            if key != previous:
                permutation = None if key[0] == "observed" else int(key[0][8:])
                plans = paired_plans(
                    data, meta, config["design"], seed=key[1], permutation=permutation
                )
                verify_plans(plans)
                previous = key
            print("Fitting", case["id"], flush=True)
            attempts.append({**case, "status": "started"})
            with (root / "attempt-log.jsonl").open("a") as log:
                log.write(json.dumps(attempts[-1]) + "\n")
            result = train_case(
                case, *plans[case["arm"]], meta=meta, config=config, run_root=root
            )
            for name in streamed:
                values = result.pop(name)
                if name not in writers:
                    writers[name] = csv.DictWriter(
                        handles[name], fieldnames=list(values[0])
                    )
                    writers[name].writeheader()
                writers[name].writerows(values)
                handles[name].flush()
            result.pop("fit_counts")
            for name, value in result.items():
                results[name].extend(value if isinstance(value, list) else [value])
            attempts[-1]["status"] = "completed"
            with (root / "attempt-log.jsonl").open("a") as log:
                log.write(json.dumps(attempts[-1]) + "\n")
            gc.collect()
        for name, values in results.items():
            if name == "metrics":
                write_csv(aggregate / (name + ".csv"), values)
            else:
                write_json(aggregate / (name + ".json"), values)
        write_json(root / ("attempts_" + part + ".json"), attempts)
        write_json(
            root / ("fit-counts-after-" + part + ".json"), dict(accounting.counts)
        )
        return results
    except BaseException as exc:
        if attempts and attempts[-1]["status"] == "started":
            attempts[-1].update(status="failed", exception=type(exc).__name__)
            with (root / "attempt-log.jsonl").open("a") as log:
                log.write(json.dumps(attempts[-1]) + "\n")
        write_json(
            root / ("failure_" + part + ".json"),
            {
                "exception": type(exc).__name__,
                "message": str(exc),
                "attempts": attempts,
                "actual_fit_counts": dict(accounting.counts),
            },
        )
        raise
    finally:
        for handle in handles.values():
            handle.close()


def load_results(root, part):
    root = Path(root)
    result = {k: [] for k in ("metrics", "confusions", "learning", "trajectories")}
    for source_part in ("reuse", "width") if part == "width" else ("reuse",):
        agg = root / ("aggregates_" + source_part)
        if not agg.exists():
            raise ValueError("missing completed experiment aggregates: " + source_part)
        expected = [
            c
            for c in schedule()
            if c["arm"] in PART_ARMS[part]
            and c["arm"]
            in (PART_ARMS["reuse"] if source_part == "reuse" else ("Wmid", "Wfull"))
        ]
        for case in expected:
            folder = root / "cases" / case["id"]
            completion = json.loads((folder / "completion.json").read_text())
            if any(completion[k] != v for k, v in case.items()):
                raise ValueError("case completion differs from scheduled case")
            for name, digest in completion["artifact_sha256"].items():
                path = (folder / name).resolve()
                if not path.is_relative_to(folder.resolve()) or sha(path) != digest:
                    raise ValueError("case artifact authentication failed")
        for key in result:
            if key == "metrics":
                # JSON case metrics retain numeric types and exact identifiers.
                values = [
                    r
                    for case in expected
                    for r in json.loads(
                        (root / "cases" / case["id"] / "metrics.json").read_text()
                    )
                ]
            else:
                values = json.loads((agg / (key + ".json")).read_text())
            if key in ("metrics", "confusions"):
                values = [r for r in values if r["arm"] in PART_ARMS[part]]
            elif key == "trajectories":
                values = [
                    r for r in values if r["case"].rsplit("_", 1)[-1] in PART_ARMS[part]
                ]
            else:
                values = [
                    r for r in values if r["case"].rsplit("_", 2)[-2] in PART_ARMS[part]
                ]
            result[key].extend(values)
    return result
