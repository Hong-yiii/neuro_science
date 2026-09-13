#!/usr/bin/env python3
"""Forward-only issue #6 verification; never refit biological or synthetic models."""

from __future__ import annotations

import argparse
from contextlib import ExitStack
import json
import math
from pathlib import Path
import sys
from unittest.mock import patch

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from scripts import place195_path_preprocessing_autoresearch as pp  # noqa: E402
from scripts import place195_matched_pca as study  # noqa: E402
from scripts import verify_path_preprocessing_results as vr  # noqa: E402

if not __debug__:
    raise RuntimeError("verification requires assertions; do not use -O")


def assert_nested(saved, expected):
    if isinstance(expected, dict):
        assert saved.keys() == expected.keys(), (saved.keys(), expected.keys())
        for key in expected:
            assert_nested(saved[key], expected[key])
    elif isinstance(expected, list):
        assert len(saved) == len(expected)
        for a, b in zip(saved, expected, strict=True):
            assert_nested(a, b)
    elif isinstance(expected, (int, float)) and not isinstance(expected, bool):
        assert math.isclose(saved, expected, rel_tol=1e-9, abs_tol=1e-10), (
            saved,
            expected,
        )
    else:
        assert saved == expected, (saved, expected)


def check_projection(model, train):
    candidate = pp.candidate_from_dict(model)
    X = pp.feature_matrix(train.X_counts, train.E, candidate)
    mean, sd = X.mean(axis=0), X.std(axis=0)
    positive = sd[sd > 0]
    floor = float(np.median(positive)) if len(positive) else 1.0
    scale = np.maximum(sd, floor)
    np.testing.assert_allclose(model["scaler"]["mean"], mean, rtol=1e-12, atol=1e-12)
    np.testing.assert_allclose(model["scaler"]["scale"], scale, rtol=1e-12, atol=1e-12)
    assert_nested(model["scaler"]["floor"], floor)
    assert_nested(model["scaler"]["floored_fraction"], float(np.mean(sd < floor)))
    assert model["classes"] == [0, 1]
    assert model["input_features"] == X.shape[1]
    assert model["intercept_only"] == bool(np.all(sd == 0))
    if candidate.projection == "none":
        if not np.any(sd):
            np.testing.assert_allclose(model["coef"], 0, atol=1e-12)
        return
    state = model["projection_state"]
    assert model["replay_schema_version"] == 2 and state["schema_version"] == 1
    assert state["whiten"] is False and state["variance_target"] == 0.9
    Z = (X - mean) / scale
    np.testing.assert_allclose(state["mean"], Z.mean(axis=0), atol=1e-12)
    centered = Z - np.asarray(state["mean"])
    singular = np.asarray(state["singular_values"])
    tolerance = np.finfo(float).eps * max(Z.shape) * singular[0]
    rank = int(np.sum(singular > tolerance))
    assert (
        np.isfinite(singular).all()
        and np.all(singular >= 0)
        and np.all(np.diff(singular) <= 1e-12)
    )
    assert state["numerical_rank"] == rank and state["input_features"] == X.shape[1]
    assert_nested(state["singular_tolerance"], float(tolerance))
    total = float(np.sum(centered**2))
    np.testing.assert_allclose(np.sum(singular**2), total, rtol=1e-10, atol=1e-10)
    ratios = singular**2 / total if rank else np.zeros_like(singular)
    np.testing.assert_allclose(state["explained_variance_ratio"], ratios, atol=1e-10)
    cumulative = np.cumsum(ratios)
    k = next((i + 1 for i in range(rank) if cumulative[i] >= 0.9 - 1e-12), rank)
    assert state["n_components"] == k and state["intercept_only"] == (k == 0)
    if k == 0:
        assert not np.any(centered) and state["components"] == []
        np.testing.assert_allclose(model["coef"], 0, atol=1e-12)
        assert state["retained_variance"] == 0
        return
    components = np.asarray(state["components"])
    assert components.shape == (k, X.shape[1])
    np.testing.assert_allclose(components @ components.T, np.eye(k), atol=1e-10)
    covariance = centered.T @ centered
    np.testing.assert_allclose(
        components @ covariance,
        singular[:k, None] ** 2 * components,
        rtol=1e-8,
        atol=1e-9,
    )
    projected = centered @ components.T
    np.testing.assert_allclose(
        (projected**2).sum(axis=0), singular[:k] ** 2, rtol=1e-9, atol=1e-9
    )
    assert_nested(state["retained_variance"], float(cumulative[k - 1]))


def verify_stage(directory, prefix, tensor, recipes, rows_per_class, labels=None):
    values, count = vr.replay(
        directory,
        prefix,
        tensor,
        labels,
        rows_per_class=rows_per_class,
        repeated_lineage=prefix == "cv",
    )
    assert set(values) == {c.key for c in recipes}
    summaries = pp.read_json(directory / f"{prefix}_summary.json")
    vr.check_summaries(
        summaries,
        values,
        "primary_cv_delta_log_loss"
        if prefix == "cv"
        else "diagnostic_validation_delta_log_loss",
    )
    for row in vr.csv_rows(directory / f"{prefix}_metrics.csv.gz"):
        assert row["converged"] == "True" and 0 <= int(row["n_iter"]) < 1000
    trains = {}
    for model in pp.read_json(directory / f"{prefix}_models.json.gz"):
        candidate = pp.candidate_from_dict(model)
        assert candidate in recipes and model["candidate_key"] == candidate.key
        endpoint, fold, seed = model["endpoint_pair"], model.get("fold"), model["seed"]
        key = endpoint, fold, seed
        if key not in trains:
            et = pp.subset_tensor(tensor, endpoint)
            plan = pp.make_draw_plan(
                et.records,
                split="train",
                rows_per_class=rows_per_class,
                seed=seed,
                fold_mode="train" if prefix == "cv" else "all",
                fold=fold,
                shuffled_labels=labels,
            )
            trains[key] = pp.materialize_plan(et, plan)
        check_projection(model, trains[key])
    return values, count


def independent_selection(values):
    result = {}
    for name, projection in (("raw", "none"), ("pca", "pca90")):
        recipes = [
            pp.Candidate(1, "raw_rate", "variance_floor", lam, projection)
            for lam in (0.01, 0.1, 1)
        ]
        best = max(values[c.key]["delta"] for c in recipes)
        result[name] = next(
            c.key for c in reversed(recipes) if values[c.key]["delta"] >= best - 1e-12
        )
    return result


def pair_from_scores(values, selected):
    raw, pca = (values[selected[k]] for k in ("raw", "pca"))
    assert raw["endpoint_delta"].keys() == pca["endpoint_delta"].keys()
    return {
        "baseline_deltas": {"raw": raw["delta"], "pca": pca["delta"]},
        "raw_loss_minus_pca_loss": pca["delta"] - raw["delta"],
        "endpoint_difference": {
            ep: pca["endpoint_delta"][ep] - raw["endpoint_delta"][ep]
            for ep in raw["endpoint_delta"]
        },
    }


def check_selection(directory, values):
    selected = independent_selection(values)
    assert pp.read_json(directory / "selection.json") == {
        "selected": selected,
        "cv_sha256": pp.sha256_file(directory / "cv_summary.json"),
    }
    return selected


def verify(directory, tensor=None, *, integrity=True):
    summary = pp.read_json(directory / "summary.json")
    assert summary["status"] == "complete" and summary["schema_version"] == 1
    if integrity:
        hashes = pp.read_json(directory / "artifact-hashes.json")
        for relative, digest in hashes.items():
            path = (directory / relative).resolve()
            assert path.is_relative_to(directory.resolve())
            assert pp.sha256_file(path) == digest, relative
    if tensor is None:
        tensor = pp.load_source_tensor(directory / "tensor.npz")
        start = pp.read_json(directory / "start.json")
        for relative, digest in start["code_hashes"].items():
            assert pp.sha256_file(directory / "code" / relative) == digest
        if start["stage"] == "run":
            original, audit = study.audit_inputs(
                Path(start["source"]), Path(start["manifest"])
            )
            assert pp.read_json(directory / "input-audit.json") == audit
            assert (
                tensor.records == original.records
                and tensor.cell_ids == original.cell_ids
            )
            for name in ("X", "E", "M"):
                np.testing.assert_equal(getattr(tensor, name), getattr(original, name))
            assert summary["null_counts"] == {"ordinary": 100, "temporal_half": 100}
            assert (
                summary["bootstrap_count"] == 200 and summary["rows_per_class"] == 128
            )
            assert_nested(
                pp.read_json(directory / "anchor.json"),
                study.anchor_check(directory / "observed", Path(start["historical"])),
            )
    rows = summary["rows_per_class"]
    count = 0
    all_recipes = study.candidates()
    values, n = verify_stage(directory / "observed", "cv", tensor, all_recipes, rows)
    count += n
    selected = check_selection(directory / "observed", values)
    assert (
        selected
        == summary["selected"]
        == pp.read_json(directory / "SELECTION-FROZEN.json")["selected"]
    )
    assert pp.read_json(directory / "SELECTION-FROZEN.json")[
        "selection_sha256"
    ] == pp.sha256_file(directory / "observed/selection.json")
    values, n = verify_stage(
        directory / "observed", "validation", tensor, all_recipes, rows
    )
    count += n
    observed = pair_from_scores(values, selected)
    assert_nested(summary["observed"], observed)
    nulls = pp.read_json(directory / "nulls.json")
    references = {}
    for kind, seed0 in (("ordinary", 50000), ("temporal_half", 70000)):
        worlds = sorted((directory / f"null_{kind}").glob("world-*"))
        assert len(worlds) == summary["null_counts"][kind] == len(nulls[kind])
        pairs, maxima = [], []
        for index, world in enumerate(worlds):
            labels, audit = pp.make_label_permutation(
                tensor.records,
                seed=seed0 + index,
                temporal_half=kind == "temporal_half",
            )
            assert pp.read_json(world / "permutation.json") == {
                "labels": labels,
                "audit": audit,
            }
            cv, n = verify_stage(world, "cv", tensor, all_recipes, rows, labels)
            count += n
            chosen = check_selection(world, cv)
            val, n = verify_stage(
                world, "validation", tensor, all_recipes, rows, labels
            )
            count += n
            pair, maximum = (
                pair_from_scores(val, chosen),
                max(v["delta"] for v in val.values()),
            )
            expected = {
                "index": index,
                "seed": seed0 + index,
                "selected": chosen,
                "pair": pair,
                "max_six_delta": maximum,
                "changed_labels": sum(
                    labels[r.source_trial_id] != r.label for r in tensor.records
                ),
                "source_count": len(tensor.records),
                "pure_strata": sum(len(s["counts"]) == 1 for s in audit["strata"]),
                "pure_sources": sum(
                    s["n"] for s in audit["strata"] if len(s["counts"]) == 1
                ),
            }
            assert_nested(pp.read_json(world / "world.json"), expected)
            assert_nested(nulls[kind][index], expected)
            pairs.append(pair)
            maxima.append(maximum)
        references[kind] = {}
        for name in ("raw", "pca"):
            threshold = observed["baseline_deltas"][name] - 1e-12
            references[kind][name] = {
                "selected": (
                    1 + sum(p["baseline_deltas"][name] >= threshold for p in pairs)
                )
                / (1 + len(pairs)),
                "max_six": (1 + sum(v >= threshold for v in maxima))
                / (1 + len(maxima)),
            }
    assert_nested(summary["null_references"], references)
    fixed = study.selected_recipes(selected)
    bootstrap = []
    worlds = sorted((directory / "bootstrap").glob("resample-*"))
    assert len(worlds) == summary["bootstrap_count"]
    for index, world in enumerate(worlds):
        records, audit = pp._bootstrap_records(tensor.records, seed=90000 + index)
        assert pp.read_json(world / "resampling.json") == audit
        values, n = verify_stage(
            world, "validation", pp.bootstrap_tensor(tensor, records), fixed, rows
        )
        count += n
        bootstrap.append(pair_from_scores(values, selected))
    assert_nested(pp.read_json(directory / "bootstrap.json"), bootstrap)
    sensitivity = {
        name: dict(
            zip(
                ("q025", "q50", "q975"),
                np.quantile(
                    [p["baseline_deltas"][name] for p in bootstrap], [0.025, 0.5, 0.975]
                ),
                strict=True,
            )
        )
        for name in ("raw", "pca")
    }
    sensitivity["paired_difference"] = dict(
        zip(
            ("q025", "q50", "q975"),
            np.quantile(
                [p["raw_loss_minus_pca_loss"] for p in bootstrap], [0.025, 0.5, 0.975]
            ),
            strict=True,
        )
    )
    assert_nested(summary["bootstrap_fixed_selection_sensitivity"], sensitivity)
    for seed in (1, 2):
        values, n = verify_stage(
            directory / "assembly" / f"seed-{seed}", "validation", tensor, fixed, rows
        )
        count += n
        assert_nested(
            summary["assembly_seeds"][str(seed)], pair_from_scores(values, selected)
        )
    base = observed["endpoint_difference"]
    assert_nested(
        summary["leave_endpoint_out_difference"],
        {
            ep: float(np.mean([v for k, v in base.items() if k != ep]))
            for ep in base
            if len(base) > 1
        },
    )
    sessions = []
    for session in sorted({r.session_id for r in tensor.records}):
        reduced = study.reduced_tensor(tensor, session)
        if not reduced.records:
            continue
        values, n = verify_stage(
            directory / "session" / session, "validation", reduced, fixed, rows
        )
        count += n
        pair = pair_from_scores(values, selected)
        common = pair["endpoint_difference"]
        sessions.append(
            {
                "omitted_session": session,
                "pair": pair,
                "dropped_endpoints": sorted(set(base) - set(common)),
                "original_common_difference": float(np.mean([base[k] for k in common])),
            }
        )
    assert_nested(summary["leave_session_out"], sessions)
    budget = study.fit_budget(
        tensor, summary["null_counts"]["ordinary"], summary["bootstrap_count"]
    )
    assert pp.read_json(directory / "fit-budget.json") == budget
    assert count == summary["fit_count"] == sum(budget.values())
    return {
        "status": "verified",
        "new_fits": 0,
        "models_forward_replayed": count,
        "selected": selected,
        "primary_raw_loss_minus_pca_loss": observed["raw_loss_minus_pca_loss"],
        "summary_sha256": pp.sha256_file(directory / "summary.json"),
        "shared_helper_limitation": "assembly, permutation/bootstrap construction, feature aggregation and forward transform reused; metrics, selection and inferential summaries independently recalculated; PCA checked with covariance identities, not fitted again",
    }


def forbid_fits():
    stack = ExitStack()
    for obj, name in (
        (pp.LogisticRegression, "fit"),
        (pp, "fit_candidate_model"),
        (pp, "fit_scaler"),
        (pp, "fit_pca_projection"),
        (np.linalg, "svd"),
    ):
        stack.enter_context(
            patch.object(obj, name, side_effect=AssertionError("replay must not fit"))
        )
    return stack


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    with forbid_fits():
        result = verify(args.directory)
    result["verifier_sha256"] = pp.sha256_file(Path(__file__))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x") as stream:
        json.dump(result, stream, indent=2)
        stream.write("\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
