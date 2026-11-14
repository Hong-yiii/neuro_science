"""Post-hoc error audit from authenticated saved predictions; never load models.

No neural values/features are read from the NPZ containers. Only named truth and
prediction members are opened. Original run and earlier deliverables are immutable.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
import csv
from fractions import Fraction
import hashlib
import json
from pathlib import Path

import numpy as np


RECEIPT = "6f070f514d98898df1121e6074e1ffef66e662963902706cab62032a85486869"
ENCODERS = ("raw", "pca", "cebra", "native")
DECODERS = ("logistic", "svm", "knn", "lda")
ROSTERS = ("S33", "S67", "S100")
POLICIES = ("U2", "R16", "F16")
K_VALUES = (30, 20, 15)
HEADS = ("pair", "start", "goal")


def sha(path):
    with Path(path).open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def write_json(path, data):
    Path(path).write_text(json.dumps(data, ensure_ascii=False, allow_nan=False) + "\n")


def write_csv(path, rows):
    if not rows:
        raise ValueError("empty result table")
    with Path(path).open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


class AuthenticatedRun:
    def __init__(self, root):
        self.root = Path(root).resolve()
        if sha(self.root / "receipt.json") != RECEIPT:
            raise ValueError("unrecognized immutable run receipt")
        self.receipt = json.loads((self.root / "receipt.json").read_text())
        assert self.receipt["status"] == "completed"
        self.used = {}

    def path(self, relative):
        path = (self.root / relative).resolve()
        assert path.is_relative_to(self.root)
        digest = self.receipt["files_sha256"][relative]
        if relative not in self.used:
            if sha(path) != digest:
                raise ValueError(f"input hash mismatch: {relative}")
            self.used[relative] = digest
        return path

    def json(self, relative):
        return json.loads(self.path(relative).read_text())

    def csv(self, relative):
        with self.path(relative).open() as handle:
            return list(csv.DictReader(handle))


def family(encoder, decoder):
    return encoder if decoder == "logistic" else encoder + "_" + decoder


def case_id(k, roster, policy, seed):
    return f"observed_seed{seed}_K{k}_{roster}_{policy}"


def average_ranks(values):
    """One-based ranks, assigning the mean rank to every tied observation."""
    order = sorted(range(len(values)), key=lambda i: values[i])
    result = np.empty(len(values), dtype=float)
    start = 0
    while start < len(order):
        stop = start + 1
        while stop < len(order) and values[order[stop]] == values[order[start]]:
            stop += 1
        result[order[start:stop]] = (start + 1 + stop) / 2
        start = stop
    return result


def rank_correlation(x, y):
    if len(x) != len(y) or len(x) < 2:
        raise ValueError("correlation needs paired class observations")
    if len(set(x)) == 1:
        return None, "constant support/reuse"
    if len(set(y)) == 1:
        return None, "constant error"
    value = float(np.corrcoef(average_ranks(x), average_ranks(y))[0, 1])
    assert np.isfinite(value)
    return value, "defined"


def confusion(truth, prediction, labels):
    if truth.shape != prediction.shape or truth.ndim != 1:
        raise ValueError("truth/prediction dimensions differ")
    lookup = {str(label): i for i, label in enumerate(labels)}
    result = np.zeros((len(labels), len(labels)), dtype=np.int64)
    for a, b in zip(truth, prediction, strict=True):
        result[lookup[str(a)], lookup[str(b)]] += 1
    assert np.all(result.sum(axis=1) > 0)
    return result


def matched_lineage(source, destination, *, same_units):
    """Verify pairing from complete lineage, never synthetic row IDs alone."""
    source_blocks, destination_blocks = source["blocks"], destination["blocks"]
    assert len(set(source_blocks)) == len(source_blocks)
    assert len(set(destination_blocks)) == len(destination_blocks)
    assert set(destination_blocks) <= set(source_blocks)
    assert set(destination["units"]) <= set(source["units"])
    if same_units:
        assert destination_blocks == source_blocks
        assert destination["units"] == source["units"]
    indices = [source_blocks.index(block) for block in destination_blocks]
    assert len(source["rows"]) == len(destination["rows"])
    for a, b in zip(source["rows"], destination["rows"], strict=True):
        assert a["pair"] == b["pair"] and a["row_id"] == b["row_id"]
        assert [a["source_ids"][i] for i in indices] == b["source_ids"]


def flip_counts(truth, before, after, label):
    mask = truth == label
    a, b = before[mask] == truth[mask], after[mask] == truth[mask]
    total = int(mask.sum())
    assert total > 0
    result = dict(
        evaluated_rows=total,
        both_correct=int(np.count_nonzero(a & b)),
        wrong_to_right=int(np.count_nonzero(~a & b)),
        right_to_wrong=int(np.count_nonzero(a & ~b)),
        both_wrong=int(np.count_nonzero(~a & ~b)),
        changed_wrong_label=int(
            np.count_nonzero(~a & ~b & (before[mask] != after[mask]))
        ),
        before_recall=float(a.mean()),
        after_recall=float(b.mean()),
        recall_change_pp=100 * float(b.mean() - a.mean()),
    )
    assert (
        sum(
            result[k]
            for k in ("both_correct", "wrong_to_right", "right_to_wrong", "both_wrong")
        )
        == total
    )
    assert np.isclose(
        result["recall_change_pp"],
        100 * (result["wrong_to_right"] - result["right_to_wrong"]) / total,
    )
    return result


def analyze(run_path, output):
    plan_path = (
        Path(__file__).resolve().parents[1]
        / "docs/reports/population-grid-20261111/error-analysis-plan.md"
    )
    start_script_sha256, start_plan_sha256 = sha(__file__), sha(plan_path)
    output = Path(output).resolve()
    if output.exists():
        raise FileExistsError("a fresh output directory is required")
    run = AuthenticatedRun(run_path)
    if output.is_relative_to(run.root):
        raise ValueError("never write inside immutable run")
    config = run.json("configuration.json")
    design = config["design"]
    original_confusions = run.json("aggregates/confusions.json")
    metrics = run.csv("aggregates/metrics.csv")
    supports = run.csv("report/tables/source_support.csv")
    pools = run.csv("aggregates/pool_usage.csv")
    exclusions = run.csv("report/tables/session_exclusions.csv")
    unit_inclusion = run.csv("report/tables/unit_inclusion.csv")
    metric_index = {(r["id"], r["representation"], r["head"]): r for r in metrics}
    matrix_index = {
        (r["id"], r["representation"], r["head"]): r for r in original_confusions
    }
    assert len(metric_index) == len(matrix_index) == 5328
    matrices = []
    for r in original_confusions:
        counts = np.array(r["counts"], dtype=np.int64)
        assert counts.shape == (len(r["labels"]), len(r["labels"]))
        assert np.all(counts >= 0) and np.all(counts.sum(axis=1) > 0)
        ba = float(np.mean(np.diag(counts) / counts.sum(axis=1)))
        assert np.isclose(
            ba,
            float(
                metric_index[r["id"], r["representation"], r["head"]][
                    "balanced_accuracy"
                ]
            ),
        )
        matrices.append({**r, "split": "development"})

    grid = {(g["class_count"], g["roster"]): g for g in design["grid"]}
    classes = {p["class_count"]: p["conditions"] for p in design["panels"]}
    support_index = defaultdict(list)
    for r in supports:
        support_index[r["configuration"], r["pair"]].append(r)
    pool_index = defaultdict(list)
    for r in pools:
        if r["case"].startswith("observed_"):
            pool_index[r["case"], r["pair"], r["split"]].append(r)

    usage, usage_index = [], {}
    for k in K_VALUES:
        for roster in ROSTERS:
            for seed in (0, 1, 2):
                for policy in POLICIES:
                    case = case_id(k, roster, policy, seed)
                    for label in classes[k]:
                        available = support_index[f"K{k}_{roster}", label]
                        assert len(available) == grid[k, roster]["sessions"]
                        sizes = [int(r["train_sources"]) for r in available]
                        record = dict(
                            case=case,
                            class_count=k,
                            roster=roster,
                            sampling=policy,
                            seed=seed,
                            pair=label,
                            sessions=grid[k, roster]["sessions"],
                            available_train_sources=sum(sizes),
                            minimum_session_train_pool=min(sizes),
                            # Exact rational arithmetic preserves mathematical ties
                            # before the common float representation is ranked.
                            harmonic_session_train_pool=float(
                                Fraction(len(sizes), 1)
                                / sum(Fraction(1, x) for x in sizes)
                            ),
                            available_development_sources=sum(
                                int(r["development_sources"]) for r in available
                            ),
                        )
                        for split in ("train", "development"):
                            selected = pool_index[case, label, split]
                            assert {r["session"] for r in selected} == {
                                r["session"] for r in available
                            }
                            used = sum(int(r["used"]) for r in selected)
                            draws = sum(int(r["draws"]) for r in selected)
                            policy_pool = sum(
                                int(r["eligible_sources"]) for r in selected
                            )
                            assert (
                                sum(int(r["extra_draws"]) for r in selected)
                                == draws - used
                            )
                            record.update(
                                {
                                    split + "_policy_pool_sources": policy_pool,
                                    split + "_used_sources": used,
                                    split + "_block_draws": draws,
                                    split + "_reuse_fraction": (draws - used) / draws,
                                    split + "_max_uses": max(
                                        int(r["max_use"]) for r in selected
                                    ),
                                }
                            )
                            if split == "development":
                                assert (
                                    policy_pool
                                    == record["available_development_sources"]
                                )
                        if policy == "F16":
                            assert (
                                record["train_used_sources"]
                                == record["available_train_sources"]
                                == record["train_policy_pool_sources"]
                            )
                        elif policy == "U2":
                            assert record["train_reuse_fraction"] == 0
                        else:
                            assert record["train_reuse_fraction"] == 0.875
                        usage.append(record)
                        usage_index[case, label] = record

    observed_ids = sorted(
        {r["id"] for r in original_confusions if r["world"] == "observed"}
    )
    assert len(observed_ids) == 81
    predictions, lineages, class_rows, class_index = {}, {}, [], {}
    loaded_members = 0
    for case in observed_ids:
        lineages[case] = run.json(f"cases/{case}/development_lineage.json")
        numeric_path = run.path(f"cases/{case}/numeric_records.npz")
        with np.load(numeric_path, allow_pickle=False) as saved:
            for encoder in ENCODERS:
                for decoder in DECODERS:
                    rep = family(encoder, decoder)
                    for head in HEADS:
                        original = matrix_index[case, rep, head]
                        labels = original["labels"]
                        counts_by_split = {}
                        for split, prefix in (("development", ""), ("train", "_train")):
                            keys = [
                                f"{rep}_{head}{prefix}_truth",
                                f"{rep}_{head}{prefix}_prediction",
                            ]
                            truth, predicted = (saved[key].astype(str) for key in keys)
                            loaded_members += 2
                            counts = confusion(truth, predicted, labels)
                            counts_by_split[split] = counts
                            metric_name = (
                                "balanced_accuracy"
                                if split == "development"
                                else "train_BA"
                            )
                            assert np.isclose(
                                np.mean(np.diag(counts) / counts.sum(axis=1)),
                                float(metric_index[case, rep, head][metric_name]),
                            )
                            if split == "development":
                                np.testing.assert_array_equal(
                                    counts, original["counts"]
                                )
                                if head == "pair":
                                    assert truth.tolist() == [
                                        r["pair"] for r in lineages[case]["rows"]
                                    ]
                                    predictions[case, rep] = (truth, predicted)
                            else:
                                matrices.append(
                                    {
                                        **original,
                                        "split": "train",
                                        "counts": counts.tolist(),
                                    }
                                )
                        if head != "pair":
                            continue
                        tr, dv = (
                            counts_by_split["train"],
                            counts_by_split["development"],
                        )
                        for i, label in enumerate(labels):
                            incorrect = dv[i].copy()
                            incorrect[i] = 0
                            wrong_index = int(incorrect.argmax())
                            row = dict(
                                **usage_index[case, label],
                                encoder=encoder,
                                decoder=decoder,
                                representation=rep,
                                train_correct=int(tr[i, i]),
                                train_rows=int(tr[i].sum()),
                                train_recall=float(tr[i, i] / tr[i].sum()),
                                development_correct=int(dv[i, i]),
                                development_rows=int(dv[i].sum()),
                                development_recall=float(dv[i, i] / dv[i].sum()),
                                development_error=1 - float(dv[i, i] / dv[i].sum()),
                                largest_wrong_prediction=labels[wrong_index]
                                if incorrect.sum()
                                else "",
                                largest_wrong_count=int(incorrect[wrong_index]),
                            )
                            assert row["development_rows"] == 8
                            class_rows.append(row)
                            class_index[case, rep, label] = row

    correlations = []
    association_fields = (
        "train_reuse_fraction",
        "available_train_sources",
        "harmonic_session_train_pool",
        "development_reuse_fraction",
        "available_development_sources",
    )
    for case in observed_ids:
        for encoder in ENCODERS:
            for decoder in DECODERS:
                rep = family(encoder, decoder)
                context = matrix_index[case, rep, "pair"]
                rows = [class_index[case, rep, label] for label in context["labels"]]
                results = {}
                for variable in association_fields:
                    rho, status = rank_correlation(
                        [r[variable] for r in rows],
                        [r["development_error"] for r in rows],
                    )
                    results[variable] = rho
                    correlations.append(
                        dict(
                            case=case,
                            class_count=context["class_count"],
                            roster=context["roster"],
                            sampling=context["sampling"],
                            seed=context["seed"],
                            encoder=encoder,
                            decoder=decoder,
                            representation=rep,
                            variable=variable,
                            class_observations=len(rows),
                            spearman_rho=rho,
                            status=status,
                        )
                    )
                a, b = (
                    results["train_reuse_fraction"],
                    results["available_train_sources"],
                )
                if context["sampling"] == "F16" and a is not None and b is not None:
                    assert np.isclose(a, -b)

    deletion, deletion_classes = [], []
    for source_k, destination_k in ((30, 20), (30, 15), (20, 15)):
        kept = sorted(set(classes[source_k]) & set(classes[destination_k]))
        dropped = sorted(set(classes[source_k]) - set(classes[destination_k]))
        added = sorted(set(classes[destination_k]) - set(classes[source_k]))
        assert not added  # Actual frozen panels are nested; never assume from K alone.
        for roster in ROSTERS:
            for policy in POLICIES:
                for seed in (0, 1, 2):
                    before, after = (
                        case_id(source_k, roster, policy, seed),
                        case_id(destination_k, roster, policy, seed),
                    )
                    for encoder in ENCODERS:
                        for decoder in DECODERS:
                            rep = family(encoder, decoder)
                            source = matrix_index[before, rep, "pair"]
                            labels = source["labels"]
                            a, b = (
                                [labels.index(c) for c in kept],
                                [labels.index(c) for c in dropped],
                            )
                            counts = np.array(source["counts"])
                            destination_rows = [
                                class_index[after, rep, label] for label in kept
                            ]
                            kept_rows = [
                                class_index[before, rep, label] for label in kept
                            ]
                            dropped_rows = [
                                class_index[before, rep, label] for label in dropped
                            ]
                            into_deleted = int(counts[np.ix_(a, b)].sum())
                            kept_total = int(counts[a].sum())
                            kept_errors = kept_total - int(sum(counts[i, i] for i in a))
                            context = dict(
                                source_k=source_k,
                                destination_k=destination_k,
                                roster=roster,
                                sampling=policy,
                                seed=seed,
                                encoder=encoder,
                                decoder=decoder,
                                representation=rep,
                            )
                            deletion.append(
                                dict(
                                    **context,
                                    retained_classes=len(kept),
                                    deleted_classes=len(dropped),
                                    added_classes=len(added),
                                    source_retained_recall=float(
                                        np.mean(
                                            [r["development_recall"] for r in kept_rows]
                                        )
                                    ),
                                    source_deleted_recall=float(
                                        np.mean(
                                            [
                                                r["development_recall"]
                                                for r in dropped_rows
                                            ]
                                        )
                                    ),
                                    destination_retained_recall=float(
                                        np.mean(
                                            [
                                                r["development_recall"]
                                                for r in destination_rows
                                            ]
                                        )
                                    ),
                                    retained_rows_in_source=kept_total,
                                    retained_errors_in_source=kept_errors,
                                    retained_rows_predicted_deleted=into_deleted,
                                    fraction_retained_rows_predicted_deleted=into_deleted
                                    / kept_total,
                                    fraction_retained_errors_predicted_deleted=into_deleted
                                    / kept_errors
                                    if kept_errors
                                    else None,
                                )
                            )
                            for label in classes[source_k]:
                                src = class_index[before, rep, label]
                                dst = (
                                    class_index[after, rep, label]
                                    if label in kept
                                    else None
                                )
                                deletion_classes.append(
                                    dict(
                                        **context,
                                        pair=label,
                                        status="retained" if dst else "deleted",
                                        source_recall=src["development_recall"],
                                        destination_recall=dst["development_recall"]
                                        if dst
                                        else None,
                                        source_train_sources=src[
                                            "available_train_sources"
                                        ],
                                        destination_train_sources=dst[
                                            "available_train_sources"
                                        ]
                                        if dst
                                        else None,
                                        source_train_reuse=src["train_reuse_fraction"],
                                        destination_train_reuse=dst[
                                            "train_reuse_fraction"
                                        ]
                                        if dst
                                        else None,
                                    )
                                )

    changes, contrasts, pairing_checks = [], [], 0
    for k in K_VALUES:
        for seed in (0, 1, 2):
            for roster in ROSTERS:
                for before, after in (("U2", "R16"), ("R16", "F16"), ("U2", "F16")):
                    contrasts.append(
                        (
                            "sampling",
                            k,
                            seed,
                            case_id(k, roster, before, seed),
                            case_id(k, roster, after, seed),
                        )
                    )
            for policy in POLICIES:
                for before, after in (("S100", "S67"), ("S100", "S33"), ("S67", "S33")):
                    contrasts.append(
                        (
                            "session_removal",
                            k,
                            seed,
                            case_id(k, before, policy, seed),
                            case_id(k, after, policy, seed),
                        )
                    )
    for kind, k, seed, before, after in contrasts:
        matched_lineage(
            lineages[before], lineages[after], same_units=kind == "sampling"
        )
        pairing_checks += 1
        for encoder in ENCODERS:
            for decoder in DECODERS:
                rep = family(encoder, decoder)
                truth, a = predictions[before, rep]
                truth_after, b = predictions[after, rep]
                np.testing.assert_array_equal(truth, truth_after)
                source, destination = (
                    matrix_index[before, rep, "pair"],
                    matrix_index[after, rep, "pair"],
                )
                for label in classes[k]:
                    values = flip_counts(truth, a, b, label)
                    assert np.isclose(
                        values["before_recall"],
                        class_index[before, rep, label]["development_recall"],
                    )
                    assert np.isclose(
                        values["after_recall"],
                        class_index[after, rep, label]["development_recall"],
                    )
                    changes.append(
                        dict(
                            kind=kind,
                            class_count=k,
                            seed=seed,
                            before_case=before,
                            after_case=after,
                            before_roster=source["roster"],
                            after_roster=destination["roster"],
                            before_policy=source["sampling"],
                            after_policy=destination["sampling"],
                            encoder=encoder,
                            decoder=decoder,
                            representation=rep,
                            pair=label,
                            **values,
                        )
                    )

    assert sha(__file__) == start_script_sha256 and sha(plan_path) == start_plan_sha256
    output.mkdir(parents=True, mode=0o700)
    (output / "tables").mkdir()
    all_tables = {
        "class_performance": class_rows,
        "class_source_usage": usage,
        "support_error_correlations": correlations,
        "class_deletion_groups": deletion,
        "class_deletion_details": deletion_classes,
        "paired_prediction_changes": changes,
    }
    for name, rows in all_tables.items():
        write_csv(output / "tables" / (name + ".csv"), rows)
    data = dict(
        classification="post-hoc exploratory descriptive saved-result analysis",
        receipt_sha256=RECEIPT,
        grid=design["grid"],
        panels=design["panels"],
        confusions=matrices,
        class_performance=class_rows,
        correlations=correlations,
        deletion_groups=deletion,
        deletion_details=deletion_classes,
        paired_changes=changes,
        exclusions=exclusions,
        unit_inclusion=unit_inclusion,
    )
    write_json(output / "analysis.json", data)
    manifest = dict(
        classification=data["classification"],
        original_receipt_sha256=RECEIPT,
        analysis_script_sha256=start_script_sha256,
        plan_sha256=start_plan_sha256,
        inputs_sha256=run.used,
        new_fits=0,
        model_loads=0,
        biological_replays=0,
        neural_array_members_read=0,
        saved_truth_prediction_members_read=loaded_members,
        original_development_matrices_authenticated=5328,
        observed_development_matrices_recomputed=3888,
        observed_training_matrices_recomputed=3888,
        all_confusion_matrices=len(matrices),
        verified_lineage_pairings=pairing_checks,
        table_rows={name: len(rows) for name, rows in all_tables.items()},
        files_sha256={
            p.relative_to(output).as_posix(): sha(p)
            for p in sorted(output.rglob("*"))
            if p.is_file()
        },
    )
    write_json(output / "analysis-receipt.json", manifest)
    return {
        k: v for k, v in manifest.items() if k not in ("inputs_sha256", "files_sha256")
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(analyze(args.run, args.output), indent=2))
