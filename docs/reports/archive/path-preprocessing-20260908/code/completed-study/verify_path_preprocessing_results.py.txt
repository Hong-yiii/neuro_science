#!/usr/bin/env python3
"""Verify saved metrics, source lineage, resampling and model forward passes; no fits."""
from __future__ import annotations

import argparse
from collections import defaultdict
import csv
from dataclasses import replace
import gzip
import hashlib
import json
import math
from pathlib import Path
import random
import sys
from unittest.mock import patch

import numpy as np
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from scripts import place195_path_preprocessing_autoresearch as pp

if not __debug__:
    raise RuntimeError("Verification requires assertions; do not run Python with -O")


def load(path: Path):
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt") as stream:
        return json.load(stream)


def csv_rows(path: Path):
    with gzip.open(path, "rt") as stream:
        return list(csv.DictReader(stream))


def row_key(row):
    return row["candidate_key"], row["endpoint_pair"], row.get("fold", "")


def prediction_groups(path: Path):
    groups = defaultdict(list)
    for row in csv_rows(path):
        p, w = float(row["prob_present"]), float(row["weight"])
        assert math.isfinite(p) and 0 <= p <= 1
        assert math.isfinite(w) and w > 0
        assert row["true_label"] in ("absent", "present")
        groups[row_key(row)].append(row)
    return groups


def group_metrics(rows):
    weights = [float(r["weight"]) for r in rows]
    total = math.fsum(weights)
    truth = [r["true_label"] == "present" for r in rows]
    raw_probs = [float(r["prob_present"]) for r in rows]
    probs = [max(1e-9, min(1 - 1e-9, p)) for p in raw_probs]
    # Match the declared probability clipping BEFORE log/Brier, not after selecting p(y).
    loss = math.fsum(-w * (math.log(p) if y else math.log1p(-p))
                    for y, p, w in zip(truth, probs, weights, strict=True)) / total
    recalls = []
    for label in (False, True):
        support = math.fsum(w for y, w in zip(truth, weights, strict=True) if y == label)
        assert math.isclose(support / total, .5, abs_tol=1e-10)
        correct = math.fsum(w for y, p, w in zip(truth, probs, weights, strict=True)
                            if y == label and (p >= .5) == label)
        recalls.append(correct / support)
    return {
        "log_loss": loss, "delta_log_loss_baseline_minus_model": math.log(2) - loss,
        "balanced_accuracy": sum(recalls) / 2,
        "weighted_accuracy": math.fsum(w for y, p, w in zip(truth, probs, weights, strict=True) if y == (p >= .5)) / total,
        "brier": math.fsum(w * (p - y) ** 2 for y, p, w in zip(truth, probs, weights, strict=True)) / total,
        "auroc": float(roc_auc_score(truth, raw_probs, sample_weight=weights)),
        "positive_rate_true_weighted": math.fsum(w for y, w in zip(truth, weights, strict=True) if y) / total,
        "positive_rate_pred_weighted": math.fsum(w for p, w in zip(probs, weights, strict=True) if p >= .5) / total,
        "n_rows": len(rows),
    }


def close_fields(saved, expected):
    for key, value in expected.items():
        assert math.isclose(float(saved[key]), float(value), rel_tol=1e-9, abs_tol=1e-10), (key, saved[key], value)


def scores(groups):
    panels = defaultdict(lambda: defaultdict(list))
    for (candidate, endpoint, _fold), rows in groups.items():
        panels[candidate][endpoint].append(group_metrics(rows))
    result = {}
    for candidate, by_endpoint in panels.items():
        endpoint_delta = {ep: float(np.mean([v["delta_log_loss_baseline_minus_model"] for v in values])) for ep, values in by_endpoint.items()}
        result[candidate] = {
            "delta": float(np.mean(list(endpoint_delta.values()))),
            "ba": float(np.mean([np.mean([v["balanced_accuracy"] for v in values]) for values in by_endpoint.values()])),
            "endpoint_delta": endpoint_delta,
        }
    return result


def check_summaries(summaries, derived, field):
    assert len(summaries) == len(derived)
    for row in summaries:
        values = derived[row["candidate_key"]]
        close_fields(row, {field: values["delta"]})
        for key, value in (("mean_cv_balanced_accuracy", values["ba"]), ("mean_cv_log_loss", math.log(2) - values["delta"])):
            if key in row:
                close_fields(row, {key: value})
        for key in ("endpoint_mean_delta_log_loss", "endpoint_delta_log_loss"):
            if key in row:
                assert set(row[key]) == set(values["endpoint_delta"])
                close_fields(row[key], values["endpoint_delta"])


def choose(rows):
    # Independent implementation of the frozen deterministic tie order.
    ordered = sorted(rows, key=lambda r: (int(r["temporal_bins"]),
        ["raw_rate", "sqrt_rate", "log1p_rate"].index(r["transform"]),
        ["standard", "variance_floor"].index(r["scaler"]), float(r["lambda_l2"])))
    return max(ordered, key=lambda r: r["primary_cv_delta_log_loss"])["candidate_key"]


def bundle_metrics(bundle, probs):
    return group_metrics([{"weight": w, "true_label": "present" if y else "absent", "prob_present": p}
                          for y, p, w in zip(bundle.y, probs, bundle.weights, strict=True)])


def replay(directory: Path, prefix: str, tensor, labels=None, *, prediction_file=None,
           model_file=None, metric_file=None, lineage_file=None, repeated_lineage=False,
           rows_per_class=128):
    groups = prediction_groups(directory / (prediction_file or f"{prefix}_predictions.csv.gz"))
    models = load(directory / (model_file or f"{prefix}_models.json.gz"))
    rows = csv_rows(directory / (metric_file or f"{prefix}_metrics.csv.gz"))
    metrics = {row_key(row): row for row in rows}
    assert len(metrics) == len(rows) == len(models) == len(groups)
    expected_groups = {(candidate, endpoint, fold)
        for candidate in {m["candidate_key"] for m in models}
        for endpoint in {r.endpoint_pair for r in tensor.records}
        for fold in (("0", "1", "2") if prefix == "cv" else ("",))}
    assert set(groups) == set(metrics) == expected_groups
    assert len({m["seed"] for m in models}) == 1
    bundles, expected_lineage = {}, []
    for model in models:
        endpoint, fold, seed = model["endpoint_pair"], model.get("fold"), model["seed"]
        key = endpoint, fold, seed
        first = key not in bundles
        if first:
            et = pp.subset_tensor(tensor, endpoint)
            plan = pp.make_draw_plan(et.records, split="train", rows_per_class=rows_per_class, seed=seed,
                fold_mode="train" if prefix == "cv" else "all", fold=fold, shuffled_labels=labels)
            train = pp.materialize_plan(et, plan)
            evaluation = pp.build_product_rows(et, split="train" if prefix == "cv" else "validation",
                fold_mode="validation" if prefix == "cv" else "all", fold=fold,
                seed=seed + 10_000 + fold if prefix == "cv" else seed + 20_000,
                max_combinations_per_class=10_000 if prefix == "cv" else None, shuffled_labels=labels)
            bundles[key] = train, evaluation, pp.stable_hash(plan), list(et.cell_ids)
        train, evaluation, plan_hash, cell_ids = bundles[key]
        if "cell_ids" in model:
            assert model["cell_ids"] == cell_ids
        if first or repeated_lineage:
            manifest = train.manifest + evaluation.manifest
            expected_lineage.extend(manifest if prefix == "cv" else [{"endpoint_pair": endpoint, **r} for r in manifest])
        group = model["candidate_key"], endpoint, str(fold) if prefix == "cv" else ""
        predictions, metric = groups[group], metrics[group]
        probs = pp.predict_from_replay(model, evaluation.X_counts, evaluation.E)
        np.testing.assert_allclose(probs, [float(r["prob_present"]) for r in predictions], rtol=1e-9, atol=1e-10)
        np.testing.assert_allclose(evaluation.weights, [float(r["weight"]) for r in predictions], atol=1e-12)
        np.testing.assert_array_equal(evaluation.y, [r["true_label"] == "present" for r in predictions])
        assert model["train_plan_hash"] == metric["train_plan_hash"] == plan_hash
        assert int(metric["train_rows"]) == 2 * rows_per_class
        assert int(metric["train_distinct_source_count"]) == len({r["source_trial_id"] for r in train.manifest})
        close_fields(metric, group_metrics(predictions))
        train_score = bundle_metrics(train, pp.predict_from_replay(model, train.X_counts, train.E))
        close_fields(json.loads(metric["train_metrics"]), train_score)
        if prefix == "cv":
            close_fields(metric, {"train_cv_log_loss_gap": group_metrics(predictions)["log_loss"] - train_score["log_loss"]})
    assert load(directory / (lineage_file or f"{prefix}_source_lineage.json.gz")) == expected_lineage
    return scores(groups), len(models)


def check_bootstraps(tensor, final, selected, *, count=200, rows_per_class=128):
    directories = sorted((final / "source_bootstrap").glob("resample-*"))
    assert len(directories) == count
    aggregate = load(final / "bootstrap_summaries.json.gz")
    assert len(aggregate) == count
    original = {r.source_trial_id: r for r in tensor.records}
    pools = defaultdict(list)
    for record in tensor.records:
        pools[(record.session_id, record.endpoint_pair, record.split, record.label)].append(record)
    deltas, model_count = [], 0
    for index, directory in enumerate(directories):
        seed = 90_000 + index
        rng, lineage = random.Random(seed), []
        for stratum, pool in sorted(pools.items()):
            for j in range(len(pool)):
                source = pool[rng.randrange(len(pool))].source_trial_id
                lineage.append({"bootstrap_source_trial_id": f"{source}__boot{seed}_{j}",
                                "original_source_trial_id": source, "stratum": list(stratum)})
        expected = {"seed": seed, "lineage": lineage, "strata": {"|".join(k): len(v) for k, v in pools.items()}}
        assert load(directory / "resampling.json") == expected
        saved = load(directory / "bootstrap_summary.json")
        assert saved == aggregate[index]
        assert saved["bootstrap_index"] == index and saved["seed"] == seed
        assert saved["audit"] == expected and saved["lineage_hash"] == pp.stable_hash(lineage)
        assert saved["selected_candidate_key"] == selected
        records = [replace(original[r["original_source_trial_id"]], source_trial_id=r["bootstrap_source_trial_id"]) for r in lineage]
        values, n = replay(directory, "validation", pp.bootstrap_tensor(tensor, records), rows_per_class=rows_per_class)
        model_count += n
        assert list(values) == [selected]
        close_fields(saved, {"diagnostic_validation_delta_log_loss": values[selected]["delta"]})
        close_fields(saved["endpoint_delta_log_loss"], values[selected]["endpoint_delta"])
        deltas.append(values[selected]["delta"])
    expected_quantiles = dict(zip(("q025", "q50", "q975"), np.quantile(deltas, [.025, .5, .975]), strict=True))
    close_fields(load(final / "final_summary.json")["bootstrap_delta_quantiles"], expected_quantiles)
    return model_count


def check_nuisance(tensor, final, *, rows_per_class=128):
    saved = load(final / "nuisance/summary.json")
    groups = defaultdict(list)
    for row in csv_rows(final / "nuisance/predictions.csv.gz"):
        groups[row["endpoint_pair"], row["fold"]].append(row)
    metrics = {(r["endpoint_pair"], r["fold"]): r for r in saved["endpoint_metrics"]}
    models = load(final / "nuisance/models.json.gz")
    cv_losses, val_losses = [], []
    assert len(models) == len(groups) == len(metrics)
    for model in models:
        endpoint, fold = model["endpoint_pair"], model["fold"]
        et = pp.subset_tensor(tensor, endpoint)
        evaluation = pp.build_product_rows(et, split="validation" if fold is None else "train",
            fold_mode="all" if fold is None else "validation", fold=fold, seed=20_000 if fold is None else 10_000 + fold)
        plan = pp.make_draw_plan(et.records, split="train", rows_per_class=rows_per_class, seed=0,
            fold_mode="all" if fold is None else "train", fold=fold)
        train_x = pp.nuisance_features(pp.materialize_plan(et, plan), et.records)
        X = pp.nuisance_features(evaluation, et.records)
        assert model["evaluation_lineage"] == evaluation.manifest
        assert model["sessions"] == sorted({r.session_id for r in et.records})
        np.testing.assert_allclose(X, model["evaluation_features"], atol=1e-12)
        np.testing.assert_allclose(np.mean(train_x, axis=0), model["mean"], atol=1e-12)
        sd = np.std(train_x, axis=0)
        np.testing.assert_allclose(np.where(sd > 0, sd, 1), model["scale"], atol=1e-12)
        logits = ((X - np.asarray(model["mean"])) / np.asarray(model["scale"])) @ np.asarray(model["coef"]) + model["intercept"]
        probs = 1 / (1 + np.exp(-logits))
        rows = groups[endpoint, "" if fold is None else str(fold)]
        np.testing.assert_allclose(probs, [float(r["prob_present"]) for r in rows], atol=1e-10)
        np.testing.assert_allclose(evaluation.weights, [float(r["weight"]) for r in rows], atol=1e-12)
        np.testing.assert_array_equal(evaluation.y, [r["true_label"] == "present" for r in rows])
        result = group_metrics(rows)
        close_fields(metrics[endpoint, fold], result)
        assert metrics[endpoint, fold]["train_plan_hash"] == pp.stable_hash(plan)
        (val_losses if fold is None else cv_losses).append(result["delta_log_loss_baseline_minus_model"])
    close_fields(saved, {"cv_delta_log_loss": np.mean(cv_losses), "validation_delta_log_loss": np.mean(val_losses)})
    return len(models)


def verify(run: Path, final: Path):
    summary = load(final / "final_summary.json")
    assert summary["status"] == "complete" and summary["rows_per_class"] == 128
    assert (summary["ordinary_null_count"], summary["temporal_half_null_count"], summary["bootstrap_count"]) == (100, 100, 200)
    tensor = pp.load_source_tensor(run / "export/source_tensors.npz", strict_expected=True)
    model_count = 0
    package = summary["observed_cv_package"]
    assert package["new_fits"] == 0
    for relative, receipt in package["files"].items():
        assert pp.sha256_file(final / relative) == receipt["sha256"]
    assert load(final / "label_map.json") == summary["label_map"] == {"absent": 0, "present": 1, "positive_probability": "present"}
    cv_family = []
    for phase in ("round1", "round2"):
        directory = final / "observed_cv" / phase
        values, n = replay(directory, "cv", tensor, prediction_file=f"{phase}_cv_predictions.csv.gz",
            model_file=f"{phase}_model_replays.json.gz", metric_file=f"{phase}_cv_metrics.csv.gz",
            lineage_file=f"{phase}_source_lineage.json.gz", repeated_lineage=True)
        model_count += n
        saved = load(directory / f"{phase}_summary.json")
        rows = saved["summary_rows" if phase == "round1" else "round2_summary_rows"]
        check_summaries(rows, values, "primary_cv_delta_log_loss")
        cv_family.extend(rows)
    assert len(cv_family) == 20
    selected = summary["selected_candidate"]["candidate_key"]
    assert choose(cv_family) == selected
    observed, n = replay(final / "observed", "validation", tensor)
    model_count += n
    check_summaries(load(final / "final_observed_candidate_summary.json"), observed, "diagnostic_validation_delta_log_loss")
    check_summaries([summary["observed_selected_diagnostic"]], {selected: observed[selected]}, "diagnostic_validation_delta_log_loss")
    null_values, all_worlds = {}, []
    for kind in ("ordinary", "temporal_half"):
        worlds = sorted((final / f"null_{kind}").glob("world-*"))
        assert len(worlds) == 100
        values = []
        for index, world in enumerate(worlds):
            permutation = load(world / "permutation.json")
            labels = permutation["labels"]
            cv, n = replay(world, "cv", tensor, labels)
            model_count += n
            family = load(world / "cv_family20.json")
            check_summaries(family, cv, "primary_cv_delta_log_loss")
            base = [r for r in family if r["lambda_l2"] == .1]
            assert len(base) == 18 and len(family) == 20
            best1 = next(r for r in base if r["candidate_key"] == choose(base))
            extra = [r for r in family if r["lambda_l2"] != .1]
            assert sorted(r["lambda_l2"] for r in extra) == [.01, 1.0]
            assert all(r["representation_key"] == best1["representation_key"] for r in extra)
            chosen = choose(family)
            validation, n = replay(world, "validation", tensor, labels)
            model_count += n
            check_summaries(load(world / "validation_candidate_summaries.json"), validation, "diagnostic_validation_delta_log_loss")
            recorded = load(world / "world_summary.json")
            assert chosen == recorded["selected_candidate_key"]
            pair = validation[chosen]["delta"], max(r["delta"] for r in validation.values())
            close_fields(recorded, {"null_selected_diagnostic_delta_log_loss": pair[0],
                "null_max_family_diagnostic_delta_log_loss": pair[1], "selected_cv_delta_log_loss": cv[chosen]["delta"]})
            assert recorded["seed"] == (50_000 if kind == "ordinary" else 70_000) + index
            regenerated, audit = pp.make_label_permutation(tensor.records, seed=recorded["seed"], temporal_half=kind == "temporal_half")
            assert regenerated == labels and audit == permutation["audit"] == recorded["audit"]
            assert recorded["shuffled_label_hash"] == pp.stable_hash(labels)
            values.append(pair)
            all_worlds.append(recorded)
            if index % 20 == 0:
                print(f"verified {kind} world {index}; replayed {model_count} models", flush=True)
        null_values[kind] = values
    assert load(final / "null_world_summaries.json.gz") == all_worlds
    obs = observed[selected]["delta"]
    for kind, values in null_values.items():
        for column, policy in ((0, "selected"), (1, "max_family")):
            p = (1 + sum(pair[column] >= obs for pair in values)) / 101
            assert p == summary["p_values"][f"{kind}_null_{policy}_policy_ge_observed_selected"]
    model_count += check_bootstraps(tensor, final, selected)
    for index, seed in enumerate((1, 2)):
        directory = final / "assembly_sensitivity" / f"seed-{seed}"
        saved = load(directory / "candidate_summaries.json")
        item = load(directory / "sensitivity_summary.json")
        assert item == summary["assembly_sensitivity"][index]
        assert item["fixed_selected_candidate"] == selected and not item["selection_allowed"]
        for prefix, field, selected_field in (("cv", "primary_cv_delta_log_loss", "selected_cv"),
                                               ("validation", "diagnostic_validation_delta_log_loss", "selected_validation")):
            values, n = replay(directory, prefix, tensor)
            model_count += n
            check_summaries(saved[prefix], values, field)
            check_summaries([item[selected_field]], {selected: values[selected]}, field)
    influence = load(final / "influence/summary.json")
    assert influence == summary["influence"]
    base = observed[selected]["endpoint_delta"]
    for item in influence["leave_endpoint_out"]:
        close_fields(item, {"remaining_equal_endpoint_delta": np.mean([v for k, v in base.items() if k != item["omitted_endpoint"]])})
    for item in influence["leave_session_out"]:
        session = item["omitted_session"]
        indices = [i for i, r in enumerate(tensor.records) if r.session_id != session]
        reduced = replace(tensor, X=tensor.X[indices], E=tensor.E[indices], M=tensor.M[indices], records=tuple(tensor.records[i] for i in indices))
        values, n = replay(final / "influence" / session, "validation", reduced)
        model_count += n
        common = values[selected]["endpoint_delta"]
        close_fields(item["remaining_endpoint_deltas"], common)
        assert item["dropped_endpoints"] == sorted(set(base) - set(common))
        original_common = np.mean([base[k] for k in common])
        close_fields(item, {"remaining_equal_endpoint_delta": values[selected]["delta"],
            "original_common_endpoint_delta": original_common, "change_on_common_endpoints": values[selected]["delta"] - original_common})
    model_count += check_nuisance(tensor, final)
    assert load(final / "nuisance/summary.json") == summary["nuisance_control"]
    assert model_count == 82_283
    return {"status": "verified", "new_model_fits": 0, "models_forward_replayed": model_count,
            "ordinary_nulls": 100, "temporal_half_nulls": 100, "source_bootstraps": 200,
            "selected_candidate": selected, "selected_validation_delta": obs,
            "selected_validation_balanced_accuracy": observed[selected]["ba"],
            "bootstrap_delta_quantiles": summary["bootstrap_delta_quantiles"], "p_values": summary["p_values"],
            "coverage": ["evaluation and training metrics", "saved and regenerated source lineage", "adaptive null selection",
                         "bootstrap seed/strata/lineage/hash/quantiles", "nuisance features and metrics", "seed and influence summaries"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", required=True, type=Path)
    parser.add_argument("--final-dir", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    with patch.object(pp.LogisticRegression, "fit", side_effect=AssertionError("verification must not fit")):
        result = verify(args.run_dir, args.final_dir)
    files = sorted(p for p in args.run_dir.rglob("*") if p.is_file() and p != args.output)
    result["artifact_hashes"] = {str(p.relative_to(args.run_dir)): pp.sha256_file(p) for p in files}
    result["verifier_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x") as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps({k: v for k, v in result.items() if k != "artifact_hashes"}, indent=2))


if __name__ == "__main__":
    main()
