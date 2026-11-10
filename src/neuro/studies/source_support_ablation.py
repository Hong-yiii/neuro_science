"""November 2026 bounded cue-source/sampling study; explicit stages, no import-time IO.

Metadata choices precede neural reads. Models consume complete source blocks and
frozen exposed development. Synthetic rows are never biological replicates.
"""

from __future__ import annotations

import csv
import gzip
import hashlib
import itertools
import json
import os
import platform
import time
from collections import Counter
from dataclasses import replace
from pathlib import Path

import numpy as np

from neuro.pseudopopulation import AssemblyPlan, AssemblyRow, materialize, sample_plan

PAIRS9 = tuple(f"{s}->{g}" for s in (2, 3, 5) for g in (1, 4, 6))
ARMS = (
    "A_30class_27unit",
    "B_9class_27unit",
    "C_9class_144unit",
    "D_9class_43unit",
    "E_9class_80unit",
    "F_80unit_balanced",
    "G_80unit_unique3",
    "H_80unit_recombined3",
)
NULL_ARMS = (ARMS[0], ARMS[4], ARMS[6])
PERMUTATIONS = (50000, 50001, 50002, 50003, 50004)
HASHES = {
    "manifest.json": "8af267ca189a98a3bcc3c24e498259d36079e41402a6cf2fdb9a0d9e5291ed11",
    "inner_splits.csv.gz": "34fa1c5a0f5c6d9443d435c98ba64830c68f2792306172c12d53ad60792f219f",
    "outer_splits.csv.gz": "c42b2dd2bf184dca8f9ed86908d35f16caf40bd52b4221d17380a2156d1eee56",
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    with path.open("x") as handle:
        json.dump(obj, handle, indent=2, sort_keys=True, allow_nan=False)
    path.chmod(0o600)


def write_csv(path, rows):
    rows = list(rows)
    if not rows:
        raise ValueError("refusing an empty evidence table")
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    with path.open("x", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    path.chmod(0o600)


def inventory(root):
    """Read only the three frozen public metadata files, not event/spike arrays."""
    root = Path(root)
    for name, expected in HASHES.items():
        if sha(root / name) != expected:
            raise ValueError(f"metadata identity mismatch: {name}")
    with gzip.open(root / "inner_splits.csv.gz", "rt") as f:
        inner = list(csv.DictReader(f))
    with gzip.open(root / "outer_splits.csv.gz", "rt") as f:
        outer_rows = list(csv.DictReader(f))
    outer = {r["source_trial_id"]: r for r in outer_rows}
    if len(outer) != len(outer_rows) or len(
        {r["source_trial_id"] for r in inner}
    ) != len(inner):
        raise ValueError("duplicate source identity")
    units = json.loads((root / "manifest.json").read_text())["units"]
    units = sorted(units, key=lambda r: r["cell_id"])
    sessions = sorted({u["session_id"] for u in units})
    aliases = {s: f"S{i + 1:02d}" for i, s in enumerate(sessions)}
    unit_aliases = {u["cell_id"]: f"U{i + 1:03d}" for i, u in enumerate(units)}
    sources = []
    for r in inner:
        current = outer[r["source_trial_id"]]
        previous = outer[current["previous_source_trial_id"]]
        if not (
            current["split"] == previous["split"] == r["original_split"] == "train"
            and current["session_id"] == previous["session_id"] == r["session_id"]
            and int(current["trial_index"]) == int(previous["trial_index"]) + 1
        ):
            raise ValueError("frozen source/predecessor contract violated")
        sources.append(
            {
                "source_id": r["source_trial_id"],
                "block_id": r["session_id"],
                "condition": r["label"],
                "split_id": "development" if r["split"] == "validation" else "train",
                "previous_id": current["previous_source_trial_id"],
            }
        )
    protected = {
        v
        for r in sources
        if r["split_id"] == "development"
        for v in (r["source_id"], r["previous_id"])
    }
    surviving = [
        r
        for r in sources
        if r["split_id"] == "development"
        or not {r["source_id"], r["previous_id"]} & protected
    ]
    if (
        len(sources) != 15553
        or len(protected) != 5872
        or len(sources) - len(surviving) != 4427
    ):
        raise ValueError("frozen global accounting changed")
    counts = Counter((r["block_id"], r["condition"], r["split_id"]) for r in surviving)
    before = Counter((r["block_id"], r["condition"], r["split_id"]) for r in sources)
    all_pairs = tuple(f"{a}->{b}" for a in range(1, 7) for b in range(1, 7) if a != b)
    unit_count = Counter(u["session_id"] for u in units)

    def retained(pairs, minimum):
        return tuple(
            s
            for s in sessions
            if all(
                counts[s, p, "train"] >= minimum and counts[s, p, "development"] >= 1
                for p in pairs
            )
        )

    rectangles = []
    for starts in itertools.combinations(range(1, 7), 3):
        goals = tuple(g for g in range(1, 7) if g not in starts)
        pairs = tuple(f"{s}->{g}" for s in starts for g in goals)
        for minimum in (2, 3, 4, 5):
            blocks = retained(pairs, minimum)
            rectangles.append(
                {
                    "starts": ",".join(map(str, starts)),
                    "goals": ",".join(map(str, goals)),
                    "minimum_train": minimum,
                    "sessions": len(blocks),
                    "units": sum(unit_count[s] for s in blocks),
                    "train_sources": sum(
                        counts[s, p, "train"] for s in blocks for p in pairs
                    ),
                    "development_sources": sum(
                        counts[s, p, "development"] for s in blocks for p in pairs
                    ),
                }
            )
    for minimum, expected in ((2, (144, 43)), (3, (80, 20))):
        best = sorted(
            (r for r in rectangles if r["minimum_train"] == minimum),
            key=lambda r: (-r["units"], -r["sessions"], r["starts"]),
        )[0]
        if best["starts"] != "2,3,5" or (best["units"], best["sessions"]) != expected:
            raise ValueError("frozen metadata-only rectangle decision changed")
    if any(r["sessions"] for r in rectangles if r["minimum_train"] == 5):
        raise ValueError("minimum-five infeasibility changed")
    cohorts = {
        "current": retained(all_pairs, 2),
        "wide": retained(PAIRS9, 2),
        "supported": retained(PAIRS9, 3),
    }
    pools = [
        {
            "session": aliases[s],
            "pair": p,
            "units": unit_count[s],
            "train_before_embargo": before[s, p, "train"],
            "train_after_embargo": counts[s, p, "train"],
            "development": counts[s, p, "development"],
        }
        for s in sessions
        for p in all_pairs
    ]
    exclusions = []
    for s in sessions:
        row = {"session": aliases[s], "units": unit_count[s]}
        for name, pairs, minimum in (
            ("current", all_pairs, 2),
            ("wide", PAIRS9, 2),
            ("supported", PAIRS9, 3),
        ):
            bad = [
                p
                for p in pairs
                if counts[s, p, "train"] < minimum or counts[s, p, "development"] < 1
            ]
            row[name + "_included"] = s in cohorts[name]
            row[name + "_failing_conditions"] = ";".join(bad)
        exclusions.append(row)
    source_aliases = {
        r["source_id"]: f"T{i + 1:05d}"
        for i, r in enumerate(sorted(sources, key=lambda r: r["source_id"]))
    }
    return {
        "sources": sources,
        "surviving": surviving,
        "counts": counts,
        "units": units,
        "sessions": sessions,
        "aliases": aliases,
        "unit_aliases": unit_aliases,
        "source_aliases": source_aliases,
        "cohorts": cohorts,
        "rectangles": rectangles,
        "pool_table": pools,
        "exclusions": exclusions,
        "protected": protected,
    }


def frozen_configuration():
    return {
        "study": "source-support-ablation-20261110",
        "classification": "exploratory",
        "starts": [2, 3, 5],
        "goals": [1, 4, 6],
        "conditions": list(PAIRS9),
        "observed_seeds": [0, 1, 2],
        "permutation_seeds": list(PERMUTATIONS),
        "arms": list(ARMS),
        "null_arms": list(NULL_ARMS),
        "null_model_seed": 0,
        "iterations": 1000,
        "batch_size": 256,
        "output_dimension": 8,
        "hidden": 32,
        "learning_rate": 0.0003,
        "base_logistic_C": 0.01,
        "logistic_max_iter": 2000,
        "C_policy": "C_eff=base_C*(16*number_of_classes)/training_rows",
        "standard_rows_per_class": 16,
        "development_rows_per_class": 8,
        "development_seed": 0,
        "subset_seed_base": 20261110,
        "unique_rows_per_class": 3,
        "recombined_rows_per_class": 15,
        "primary_contrasts": ["C-D", "F-E", "H-G"],
        "primary_target": "pair9",
        "primary_metrics": ["balanced_accuracy", "log_loss"],
        "expected_fit_counts": {
            "cebra": 39,
            "pca": 39,
            "logistic": 351,
            "lda": 117,
            "optimizer_updates": 39000,
        },
        "limits": {
            "memory_gib": 4,
            "cpu_cores": 2,
            "swap_bytes": 0,
            "run_seconds": 5400,
            "cebra_fit_seconds": 180,
        },
        "metadata_sha256": HASHES,
        "evaluation": "historically exposed; label-conditioned; contributor-disjoint",
    }


def restrict_data(data, *, unit_ids=None, train_source_ids=None):
    chosen_units = (
        set(unit_ids) if unit_ids is not None else {u.unit_id for u in data.units}
    )
    indices = [i for i, u in enumerate(data.units) if u.unit_id in chosen_units]
    if len(indices) != len(chosen_units) or not indices:
        raise ValueError("invalid unit restriction")
    blocks = {data.units[i].block_id for i in indices}
    rows = [
        i
        for i, s in enumerate(data.sources)
        if s.block_id in blocks
        and (
            train_source_ids is None
            or s.split_id != data.train_split
            or s.source_id in train_source_ids
        )
    ]
    if train_source_ids is not None and not set(train_source_ids) <= {
        data.sources[i].source_id for i in rows
    }:
        raise ValueError("unknown requested source subset")
    return replace(
        data,
        values=data.values[np.ix_(rows, indices, range(data.values.shape[2]))],
        observed=data.observed[np.ix_(rows, indices)],
        exposure=data.exposure[rows],
        sources=tuple(data.sources[i] for i in rows),
        units=tuple(data.units[i] for i in indices),
        targets=tuple(data.targets[i] for i in rows),
    )


def reconstruct(root, meta):
    """Authorized compact source access; selected sources/units only, no old artifacts."""
    if os.environ.get("NEURO_SUPPORT_ALLOW_BIOLOGICAL") != "1":
        raise PermissionError("explicit biological execution flag required")
    from neuro.cue_source import inspect_compact, reconstruct_compact

    root = Path(root).resolve()
    base = json.loads((root / "notebook-config.json").read_text())
    base.update(data_root=str(root), manifest_directory=str(root))
    wide_config = {
        **base,
        "analysis_panel": {
            "conditions": list(PAIRS9),
            "minimum_train_sources": 2,
            "minimum_development_sources": 1,
        },
    }
    current_selection = inspect_compact(base)
    wide_selection = inspect_compact(wide_config)
    current, ca = reconstruct_compact(current_selection, interpret_neural=True)
    wide, wa = reconstruct_compact(wide_selection, interpret_neural=True)
    if (len(current.units), len(wide.units)) != (27, 144):
        raise ValueError("unexpected reconstructed panels")
    current_units = {u.unit_id for u in current.units}
    supported = set(meta["cohorts"]["supported"])
    one_per_block = [
        next(u.unit_id for u in wide.units if u.block_id == b) for b in wide.block_ids
    ]
    data = {
        "current": current,
        "wide": wide,
        "common": restrict_data(wide, unit_ids=current_units),
        "one_per_block": restrict_data(wide, unit_ids=one_per_block),
        "supported": restrict_data(
            wide, unit_ids=[u.unit_id for u in wide.units if u.block_id in supported]
        ),
    }
    if len(data["supported"].units) != 80 or len(data["one_per_block"].units) != 43:
        raise ValueError("restricted panel width changed")
    return data, {
        "current": ca,
        "wide": wa,
        "current_metadata": current_selection.audit,
        "wide_metadata": wide_selection.audit,
    }


def effective(data, permutation=None):
    from neuro.notebook_inputs import effective_pair_map

    return effective_pair_map(data, permutation_seed=permutation)


def project_plan(plan, source_data, target_data, mapping):
    positions = [source_data.block_ids.index(b) for b in target_data.block_ids]
    ids = {s.source_id for s in target_data.sources if s.split_id == plan.split_id}
    return AssemblyPlan(
        plan.split_id,
        plan.seed,
        target_data.split_identity(plan.split_id),
        tuple(sorted((sid, mapping[sid]) for sid in ids)),
        tuple(
            replace(row, source_ids=tuple(row.source_ids[i] for i in positions))
            for row in plan.rows
        ),
        plan.policy,
    )


def allocation_plan(data, mapping, *, rows_per_class, seed, policy):
    if policy not in {"balanced-cycle", "sample-without-replacement"}:
        raise ValueError("unknown allocation policy")
    rng = np.random.default_rng(seed)
    rows = []
    for ci, (condition, target) in enumerate(
        data.target_definition.condition_to_target
    ):
        draws = []
        for block in data.block_ids:
            pool = sorted(
                s.source_id
                for s in data.sources
                if s.split_id == data.train_split
                and s.block_id == block
                and mapping[s.source_id] == condition
            )
            if not pool or (
                policy == "sample-without-replacement" and rows_per_class > len(pool)
            ):
                raise ValueError("insufficient distinct sources")
            order = rng.permutation(pool).tolist()
            if policy == "sample-without-replacement":
                drawn = order[:rows_per_class]
            else:
                drawn = (order * ((rows_per_class + len(pool) - 1) // len(pool)))[
                    :rows_per_class
                ]
                rng.shuffle(drawn)
            draws.append(drawn)
        for i in range(rows_per_class):
            rows.append(
                AssemblyRow(
                    f"train:condition{ci}:row{i}",
                    condition,
                    target,
                    tuple(d[i] for d in draws),
                )
            )
    ids = {s.source_id for s in data.sources if s.split_id == data.train_split}
    return AssemblyPlan(
        data.train_split,
        seed,
        data.split_identity(data.train_split),
        tuple(sorted((sid, mapping[sid]) for sid in ids)),
        tuple(rows),
        policy,
    )


def three_sources(data, mapping, seed):
    rng = np.random.default_rng(20261110 + seed)
    keep = set()
    for condition, _ in data.target_definition.condition_to_target:
        for block in data.block_ids:
            pool = sorted(
                s.source_id
                for s in data.sources
                if s.split_id == data.train_split
                and s.block_id == block
                and mapping[s.source_id] == condition
            )
            if len(pool) < 3:
                raise ValueError("three-source control infeasible")
            keep.update(rng.choice(pool, 3, replace=False).tolist())
    return restrict_data(data, train_source_ids=keep)


def plans(data, *, seed, permutation=None):
    """Build paired plans before any fitting; null labels precede subset selection."""
    current, wide = data["current"], data["wide"]
    cm, wm = effective(current, permutation), effective(wide, permutation)
    ct = sample_plan(
        current,
        split_id="train",
        rows_per_condition=16,
        seed=seed,
        effective_conditions=cm,
    )
    cd = sample_plan(
        current,
        split_id="development",
        rows_per_condition=8,
        seed=0,
        effective_conditions=cm,
    )
    wt = sample_plan(
        wide,
        split_id="train",
        rows_per_condition=16,
        seed=seed,
        effective_conditions=wm,
    )
    wd = sample_plan(
        wide,
        split_id="development",
        rows_per_condition=8,
        seed=0,
        effective_conditions=wm,
    )
    result = {ARMS[0]: (current, ct, cd), ARMS[2]: (wide, wt, wd)}
    for arm, key in (
        (ARMS[1], "common"),
        (ARMS[3], "one_per_block"),
        (ARMS[4], "supported"),
    ):
        small = data[key]
        result[arm] = (
            small,
            project_plan(wt, wide, small, wm),
            project_plan(wd, wide, small, wm),
        )
    supported = data["supported"]
    sd = project_plan(wd, wide, supported, wm)
    result[ARMS[5]] = (
        supported,
        allocation_plan(
            supported, wm, rows_per_class=16, seed=seed, policy="balanced-cycle"
        ),
        sd,
    )
    reduced = three_sources(supported, wm, seed)
    rd = project_plan(wd, wide, reduced, wm)
    result[ARMS[6]] = (
        reduced,
        allocation_plan(
            reduced,
            wm,
            rows_per_class=3,
            seed=seed,
            policy="sample-without-replacement",
        ),
        rd,
    )
    result[ARMS[7]] = (
        reduced,
        allocation_plan(
            reduced, wm, rows_per_class=15, seed=seed + 700000, policy="balanced-cycle"
        ),
        rd,
    )
    return result


def plan_digest(plan, blocks, units):
    payload = {
        "split": plan.split_identity,
        "seed": plan.seed,
        "policy": plan.policy,
        "effective": plan.effective_conditions,
        "blocks": blocks,
        "units": units,
        "rows": [(r.row_id, r.condition, r.source_ids) for r in plan.rows],
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()


def check_pairing(case_plans):
    wide, wt, wd = case_plans[ARMS[2]]
    full = [materialize(wide, p) for p in (wt, wd)]
    for arm in (ARMS[1], ARMS[3], ARMS[4]):
        data, train, dev = case_plans[arm]
        ui = [full[0].unit_ids.index(u.unit_id) for u in data.units]
        for i, plan in enumerate((train, dev)):
            small = materialize(data, plan)
            np.testing.assert_array_equal(small.values, full[i].values[:, ui])
            np.testing.assert_array_equal(small.targets, full[i].targets)
    for arm in (ARMS[5], ARMS[6], ARMS[7]):
        data, _, dev = case_plans[arm]
        small = materialize(data, dev)
        ui = [full[1].unit_ids.index(u.unit_id) for u in data.units]
        np.testing.assert_array_equal(small.values, full[1].values[:, ui])
    return True


def usage_tables(data, plan, meta, case):
    counts = Counter(sid for row in plan.rows for sid in row.source_ids)
    mapping = dict(plan.effective_conditions)
    source_rows, pool_rows = [], []
    for condition, _ in data.target_definition.condition_to_target:
        for block in data.block_ids:
            sources = [
                s
                for s in data.sources
                if s.split_id == plan.split_id
                and s.block_id == block
                and mapping[s.source_id] == condition
            ]
            use = [counts[s.source_id] for s in sources]
            draws = sum(use)
            if not sources or draws != sum(r.condition == condition for r in plan.rows):
                raise ValueError("per-pool draw accounting failed")
            pool_rows.append(
                {
                    "case": case,
                    "split": plan.split_id,
                    "session": meta["aliases"][block],
                    "pair": condition,
                    "eligible_sources": len(sources),
                    "draws": draws,
                    "expected_uses": draws / len(sources),
                    "used": sum(x > 0 for x in use),
                    "unused": sum(x == 0 for x in use),
                    "repeated": sum(x > 1 for x in use),
                    "extra_draws": draws - sum(x > 0 for x in use),
                    "max_use": max(use),
                    "max_share": max(use) / draws,
                    "concentration": sum((x / draws) ** 2 for x in use),
                }
            )
            for source, count in zip(sources, use, strict=True):
                source_rows.append(
                    {
                        "case": case,
                        "split": plan.split_id,
                        "session": meta["aliases"][block],
                        "pair": condition,
                        "source": meta["source_aliases"][source.source_id],
                        "uses": count,
                    }
                )
    if sum(counts.values()) != len(plan.rows) * len(data.block_ids):
        raise ValueError("total block draw accounting failed")
    return pool_rows, source_rows


def overlap_summary(plan):
    summaries = []
    for condition in sorted({r.condition for r in plan.rows}):
        rows = [r.source_ids for r in plan.rows if r.condition == condition]
        shared = [
            sum(a == b for a, b in zip(x, y, strict=True))
            for x, y in itertools.combinations(rows, 2)
        ]
        summaries.append(
            {
                "pair": condition,
                "rows": len(rows),
                "blocks": len(rows[0]),
                "exact_duplicate_rows": len(rows) - len(set(rows)),
                "mean_shared_blocks": float(np.mean(shared)) if shared else 0.0,
                "minimum_shared_blocks": min(shared, default=0),
                "maximum_shared_blocks": max(shared, default=0),
            }
        )
    return summaries


def metric_scalars(metric):
    return {
        k: float(metric[k])
        for k in ("accuracy", "balanced_accuracy", "macro_f1", "log_loss")
    }


def train_case(case, data, train_plan, dev_plan, *, meta, config, run_root):
    """One fresh declared case, with saved states and fit-blocked persistence checks."""
    import joblib
    from neuro import cebra
    from neuro.evaluation import classification_metrics
    from neuro.notebook_artifacts import no_fitting, target_heads
    from neuro.notebook_support import fit_logistic
    from neuro.pca_lda import fit_lda, fit_pca, fit_standardizer, raw_features

    root = Path(run_root) / "cases" / case["id"]
    root.mkdir(parents=True, exist_ok=False, mode=0o700)
    started = time.monotonic()
    train, dev = materialize(data, train_plan), materialize(data, dev_plan)
    by_id = {s.source_id: s for s in data.sources}
    unions = [
        {
            v
            for row in a.plan.rows
            for sid in row.source_ids
            for v in (sid, *by_id[sid].dependency_ids)
        }
        for a in (train, dev)
    ]
    if unions[0] & unions[1]:
        raise ValueError("training/development contributor overlap")
    identities = {
        split: plan_digest(a.plan, a.block_ids, a.unit_ids)
        for split, a in (("train", train), ("development", dev))
    }
    write_json(
        root / "case.json",
        {
            **case,
            "plan_identities": identities,
            "units": list(train.unit_ids),
            "blocks": list(train.block_ids),
            "train_rows": len(train.values),
            "development_rows": len(dev.values),
        },
    )
    # Lineage is stored explicitly, independently of numeric arrays or pickle states.
    for split, a in (("train", train), ("development", dev)):
        write_json(
            root / f"{split}_lineage.json",
            {
                "identity": identities[split],
                "policy": a.plan.policy,
                "blocks": list(a.block_ids),
                "units": list(a.unit_ids),
                "rows": [
                    {
                        "row_id": r.row_id,
                        "pair": r.condition,
                        "source_ids": list(r.source_ids),
                    }
                    for r in a.plan.rows
                ],
            },
        )
    yt, yd = target_heads(train), target_heads(dev)
    classes = len(set(yt["pair"]))
    C = config["base_logistic_C"] * (16 * classes) / len(train.values)
    raw = fit_standardizer(train.values)
    pca = fit_pca(train.values, n_components=8)
    encoder = cebra.fit(
        train.values,
        train.targets,
        iterations=config["iterations"],
        batch_size=config["batch_size"],
        output_dimension=8,
        hidden=config["hidden"],
        learning_rate=config["learning_rate"],
        seed=case["seed"],
        max_seconds=config["limits"]["cebra_fit_seconds"],
        device="cpu",
    )
    representations = {"raw": raw, "pca": pca, "cebra": encoder}
    metrics, confusions, error_rows, class_errors, state_hashes = [], [], [], [], {}
    projections = {}
    fit_counts = {
        "cebra": 1,
        "pca": 1,
        "logistic": 0,
        "lda": 0,
        "optimizer_updates": config["iterations"],
    }
    arrays = {"train_values": train.values, "development_values": dev.values}
    for name, representation in representations.items():
        saved_readouts = []
        tr, dv = (
            representation.transform(train.values),
            representation.transform(dev.values),
        )
        if name == "raw":
            tr, dv = raw_features(tr), raw_features(dv)
        else:
            projections[name] = dv.reshape(len(dv), 10, 8).copy()
        arrays[name + "_train_features"], arrays[name + "_development_features"] = (
            tr,
            dv,
        )
        state = root / f"{name}_encoder.joblib"
        joblib.dump(representation, state, compress=3)
        state.chmod(0o600)
        state_hashes[state.name] = sha(state)
        for family in [name, "lda"] if name == "raw" else [name]:
            for head in ("pair", "start", "goal"):
                model = (
                    fit_lda(tr, yt[head])
                    if family == "lda"
                    else fit_logistic(
                        tr, yt[head], C=C, max_iter=config["logistic_max_iter"]
                    )
                )
                fit_counts["lda" if family == "lda" else "logistic"] += 1
                train_predictions, train_probabilities = (
                    model.predict(tr),
                    model.predict_proba(tr),
                )
                mt = classification_metrics(
                    yt[head],
                    train_predictions,
                    classes=model.classes_,
                    probabilities=train_probabilities,
                )
                predictions, probabilities = model.predict(dv), model.predict_proba(dv)
                md = classification_metrics(
                    yd[head],
                    predictions,
                    classes=model.classes_,
                    probabilities=probabilities,
                )
                readout = family + "_" + head
                metric = {
                    **case,
                    "representation": family,
                    "head": head,
                    "units": len(data.units),
                    "sessions": len(data.block_ids),
                    "classes": len(model.classes_),
                    "train_rows": len(tr),
                    "development_rows": len(dv),
                    "logistic_C": C if family != "lda" else "",
                    "train_BA": float(mt["balanced_accuracy"]),
                    **metric_scalars(md),
                    "train_development_gap": float(
                        mt["balanced_accuracy"] - md["balanced_accuracy"]
                    ),
                }
                metrics.append(metric)
                labels = [str(c) for c in model.classes_]
                matrix = np.zeros((len(labels), len(labels)), dtype=int)
                index = {v: i for i, v in enumerate(labels)}
                for truth, prediction in zip(yd[head], predictions, strict=True):
                    matrix[index[str(truth)], index[str(prediction)]] += 1
                if matrix.sum() != len(dv) or not np.isclose(
                    np.mean(np.diag(matrix) / matrix.sum(axis=1)),
                    md["balanced_accuracy"],
                ):
                    raise ValueError("confusion/metric reconciliation failed")
                confusions.append(
                    {
                        **case,
                        "representation": family,
                        "head": head,
                        "labels": labels,
                        "counts": matrix.tolist(),
                    }
                )
                arrays[readout + "_truth"] = yd[head]
                arrays[readout + "_prediction"] = predictions
                arrays[readout + "_probabilities"] = probabilities
                arrays[readout + "_train_truth"] = yt[head]
                arrays[readout + "_train_prediction"] = train_predictions
                arrays[readout + "_train_probabilities"] = train_probabilities
                model_path = root / f"{readout}_readout.joblib"
                joblib.dump(model, model_path, compress=3)
                model_path.chmod(0o600)
                state_hashes[model_path.name] = sha(model_path)
                saved_readouts.append(
                    (
                        model_path,
                        train_predictions,
                        train_probabilities,
                        predictions,
                        probabilities,
                    )
                )
                # Trusted newly produced files are authenticated immediately before loading.
                with no_fitting(cebra=True):
                    if sha(model_path) != state_hashes[model_path.name]:
                        raise ValueError("new state hash drift")
                    restored = joblib.load(model_path)
                    np.testing.assert_array_equal(restored.predict(dv), predictions)
                    np.testing.assert_allclose(
                        restored.predict_proba(dv), probabilities, rtol=1e-7, atol=1e-7
                    )
                wrong = predictions != yd[head]
                appearances, errors = Counter(), Counter()
                for row, error in zip(dev_plan.rows, wrong, strict=True):
                    appearances.update(row.source_ids)
                    if error:
                        errors.update(row.source_ids)
                for sid in sorted(appearances):
                    total, incorrect = appearances[sid], errors[sid]
                    error_rows.append(
                        {
                            "case": case["id"],
                            "representation": family,
                            "head": head,
                            "assembly_identity": identities["development"],
                            "source": meta["source_aliases"][sid],
                            "session": meta["aliases"][by_id[sid].block_id],
                            "appearances": total,
                            "wrong_appearances": incorrect,
                            "correct_appearances": total - incorrect,
                            "wrong_fraction": incorrect / total,
                        }
                    )
                if sum(errors.values()) != int(wrong.sum()) * len(data.block_ids):
                    raise ValueError("error involvement accounting failed")
                for label in labels:
                    chosen = np.asarray([str(x) == label for x in yd[head]])
                    class_errors.append(
                        {
                            "case": case["id"],
                            "representation": family,
                            "head": head,
                            "class": label,
                            "evaluated_rows": int(chosen.sum()),
                            "wrong_rows": int(wrong[chosen].sum()),
                            "error_rate": float(wrong[chosen].mean()),
                        }
                    )
        with no_fitting(cebra=True):
            if sha(state) != state_hashes[state.name]:
                raise ValueError("new encoder hash drift")
            restored = joblib.load(state)
            replay_train, replay_dev = (
                restored.transform(train.values),
                restored.transform(dev.values),
            )
            if name == "raw":
                replay_train, replay_dev = (
                    raw_features(replay_train),
                    raw_features(replay_dev),
                )
            np.testing.assert_allclose(replay_train, tr, rtol=1e-5, atol=1e-5)
            np.testing.assert_allclose(replay_dev, dv, rtol=1e-5, atol=1e-5)
            for model_path, tp, tprob, dp, dprob in saved_readouts:
                if sha(model_path) != state_hashes[model_path.name]:
                    raise ValueError("new readout hash drift")
                readout_model = joblib.load(model_path)
                for features, expected_prediction, expected_probability in (
                    (replay_train, tp, tprob),
                    (replay_dev, dp, dprob),
                ):
                    np.testing.assert_array_equal(
                        readout_model.predict(features), expected_prediction
                    )
                    np.testing.assert_allclose(
                        readout_model.predict_proba(features),
                        expected_probability,
                        rtol=1e-7,
                        atol=1e-7,
                    )
    np.savez_compressed(root / "numeric_records.npz", **arrays)
    (root / "numeric_records.npz").chmod(0o600)
    pool_rows, source_rows, overlaps = [], [], []
    for plan in (train_plan, dev_plan):
        p, s = usage_tables(data, plan, meta, case["id"])
        pool_rows.extend(p)
        source_rows.extend(s)
        overlaps.extend(
            {"case": case["id"], "split": plan.split_id, **r}
            for r in overlap_summary(plan)
        )
    learning = {
        k: encoder.diagnostics[k]
        for k in (
            "loss",
            "iterations",
            "seed",
            "sampler_seed",
            "wall_seconds",
            "exposure_summary",
        )
    }
    # Aggregate class means in native latent coordinates; no new geometry fit.
    trajectories = {
        name: {
            str(label): z[np.asarray(yd["pair"]) == label, :, :3].mean(axis=0).tolist()
            for label in sorted(set(yd["pair"]))
        }
        for name, z in projections.items()
    }
    write_json(root / "metrics.json", metrics)
    write_json(root / "confusions.json", confusions)
    write_json(root / "learning.json", learning)
    write_json(root / "trajectories.json", trajectories)
    write_json(
        root / "completion.json",
        {
            **case,
            "fit_counts": fit_counts,
            "state_sha256": state_hashes,
            "numeric_sha256": sha(root / "numeric_records.npz"),
            "artifact_sha256": {
                p.name: sha(p) for p in sorted(root.iterdir()) if p.is_file()
            },
            "paired_contributors_overlap": 0,
            "wall_seconds": time.monotonic() - started,
            "reloaded_readouts_checked": 12,
            "composed_readout_splits_checked": 24,
            "reloaded_encoders_checked": 3,
            "plan_identities": identities,
        },
    )
    return {
        "metrics": metrics,
        "confusions": confusions,
        "pool_usage": pool_rows,
        "source_usage": source_rows,
        "source_errors": error_rows,
        "class_errors": class_errors,
        "overlap": overlaps,
        "trajectories": {"case": case["id"], "coordinates": trajectories},
        "learning": {"case": case["id"], **learning},
        "fit_counts": fit_counts,
    }


def run_grid(data, meta, config, run_root):
    """Preserve actual fits on every exit, including failures outside a model case."""
    from neuro.notebook_artifacts import FitAccounting

    accounting = FitAccounting(cebra=True).start()
    try:
        return _run_grid(data, meta, config, run_root, accounting)
    except BaseException as exc:
        write_json(
            Path(run_root) / "grid-failure.json",
            {
                "status": "failed",
                "exception_type": type(exc).__name__,
                "actual_fit_counts": dict(accounting.counts),
            },
        )
        raise
    finally:
        write_json(Path(run_root) / "actual-fit-counts.json", accounting.stop())


def _run_grid(data, meta, config, run_root, accounting):
    if config != frozen_configuration():
        raise ValueError("run configuration differs from reviewed grid")
    results = {
        key: []
        for key in (
            "metrics",
            "confusions",
            "pool_usage",
            "source_usage",
            "source_errors",
            "class_errors",
            "overlap",
            "trajectories",
            "learning",
        )
    }
    counts = Counter()
    started = time.monotonic()
    attempts = []
    worlds = [("observed", None, config["observed_seeds"], ARMS)]
    worlds += [(f"permuted{p}", p, [0], NULL_ARMS) for p in PERMUTATIONS]
    for world, permutation, seeds, arms in worlds:
        for seed in seeds:
            case_plans = plans(data, seed=seed, permutation=permutation)
            check_pairing(case_plans)
            for arm in arms:
                if time.monotonic() - started > config["limits"]["run_seconds"]:
                    raise TimeoutError("bounded grid deadline exceeded")
                case = {
                    "id": f"{world}_seed{seed}_{arm}",
                    "world": world,
                    "seed": seed,
                    "arm": arm,
                }
                print("Fitting", case["id"], flush=True)
                attempts.append({**case, "status": "started"})
                with (Path(run_root) / "attempt-log.jsonl").open("a") as log:
                    log.write(json.dumps(attempts[-1]) + "\n")
                (Path(run_root) / "attempt-log.jsonl").chmod(0o600)
                try:
                    result = train_case(
                        case,
                        *case_plans[arm],
                        meta=meta,
                        config=config,
                        run_root=run_root,
                    )
                except BaseException as exc:
                    attempts[-1].update(
                        status="failed", exception_type=type(exc).__name__
                    )
                    write_json(Path(run_root) / "attempts-failed.json", attempts)
                    write_json(
                        Path(run_root) / "fits-before-failure.json",
                        dict(accounting.counts),
                    )
                    raise
                attempts[-1]["status"] = "completed"
                with (Path(run_root) / "attempt-log.jsonl").open("a") as log:
                    log.write(json.dumps(attempts[-1]) + "\n")
                counts.update(result.pop("fit_counts"))
                for key, value in result.items():
                    results[key].extend(value if isinstance(value, list) else [value])
    observed_counts = dict(accounting.counts)
    if dict(counts) != config["expected_fit_counts"] or observed_counts != dict(counts):
        raise ValueError(f"unexpected fit accounting: {dict(counts)}")
    write_json(Path(run_root) / "attempts.json", attempts)
    aggregate = Path(run_root) / "aggregates"
    aggregate.mkdir(mode=0o700)
    for key, value in results.items():
        if key in {"confusions", "trajectories", "learning"}:
            write_json(aggregate / f"{key}.json", value)
        else:
            write_csv(aggregate / f"{key}.csv", value)
    write_json(
        aggregate / "fit_accounting.json",
        {
            "counts": dict(counts),
            "cases": len(attempts),
            "reloaded_readouts_checked": 12 * len(attempts),
            "composed_readout_splits_checked": 24 * len(attempts),
            "reloaded_encoders_checked": 3 * len(attempts),
            "python": platform.python_version(),
            "numpy": np.__version__,
            "wall_seconds": time.monotonic() - started,
        },
    )
    print("Completed", len(attempts), "cases; fits:", dict(counts), flush=True)
    return results
