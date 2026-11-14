"""Independent table arithmetic from authenticated saved lineage/predictions."""

import csv
import itertools
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np


def read_rows(path):
    with Path(path).open() as handle:
        return list(csv.DictReader(handle))


def indexed(rows, keys):
    result = {tuple(str(r[k]) for k in keys): r for r in rows}
    assert len(result) == len(rows), "duplicate table keys"
    return result


def compare_table(path, expected, keys):
    actual = indexed(read_rows(path), keys)
    wanted = indexed(expected, keys)
    assert actual.keys() == wanted.keys(), str(path) + " key coverage"
    for key, record in wanted.items():
        for column, value in record.items():
            observed = actual[key][column]
            if isinstance(value, (float, np.floating)):
                assert np.isclose(float(observed), value, rtol=0, atol=1e-12), (
                    str(path),
                    key,
                    column,
                )
            else:
                assert observed == ("" if value is None else str(value)), (
                    str(path),
                    key,
                    column,
                )
    return len(expected)


def assembly_tables(run, part, cases, lineages, maps, full_sources, meta):
    pools, sources, overlap = [], [], []
    for case in cases:
        mapping = maps[case["world"]]
        for split, lineage in lineages[case["id"]].items():
            counts = Counter(
                sid for row in lineage["rows"] for sid in row["source_ids"]
            )
            eligible = (
                set(counts)
                if split == "train"
                else {
                    sid
                    for sid, r in full_sources.items()
                    if r["session_id"] in lineage["blocks"]
                    and r["split"] == "validation"
                }
            )
            for condition in sorted({r["pair"] for r in lineage["rows"]}):
                for block in lineage["blocks"]:
                    ids = [
                        sid
                        for sid in eligible
                        if full_sources[sid]["session_id"] == block
                        and mapping[sid] == condition
                    ]
                    use = [counts[sid] for sid in ids]
                    draws = sum(use)
                    used = sum(v > 0 for v in use)
                    pools.append(
                        dict(
                            case=case["id"],
                            split=split,
                            session=meta["aliases"][block],
                            pair=condition,
                            eligible_sources=len(ids),
                            draws=draws,
                            expected_uses=draws / len(ids),
                            used=used,
                            unused=len(ids) - used,
                            repeated=sum(v > 1 for v in use),
                            extra_draws=draws - used,
                            max_use=max(use),
                            max_share=max(use) / draws,
                            concentration=sum((v / draws) ** 2 for v in use),
                        )
                    )
                    sources.extend(
                        dict(
                            case=case["id"],
                            split=split,
                            session=meta["aliases"][block],
                            pair=condition,
                            source=meta["source_aliases"][sid],
                            uses=counts[sid],
                        )
                        for sid in ids
                    )
                rows = [
                    tuple(r["source_ids"])
                    for r in lineage["rows"]
                    if r["pair"] == condition
                ]
                shared = [
                    sum(a == b for a, b in zip(left, right, strict=True))
                    for left, right in itertools.combinations(rows, 2)
                ]
                overlap.append(
                    dict(
                        case=case["id"],
                        split=split,
                        pair=condition,
                        rows=len(rows),
                        blocks=len(lineage["blocks"]),
                        exact_duplicate_rows=len(rows) - len(set(rows)),
                        mean_shared_blocks=float(np.mean(shared)),
                        minimum_shared_blocks=min(shared),
                        maximum_shared_blocks=max(shared),
                    )
                )
    agg = Path(run) / ("aggregates_" + part)
    return {
        "pool_usage_rows": compare_table(
            agg / "pool_usage.csv", pools, ("case", "split", "session", "pair")
        ),
        "source_usage_rows": compare_table(
            agg / "source_usage.csv", sources, ("case", "split", "source")
        ),
        "overlap_rows": compare_table(
            agg / "overlap.csv", overlap, ("case", "split", "pair")
        ),
    }


def derived_reports(run, part, metrics, predictions, matrices):
    folder = Path(run) / ("report_" + part)
    arms = ("B2", "B3", "B5", "U3") if part == "reuse" else ("B3", "Wmid", "Wfull")
    contrasts = (
        (("B2", "B3"), ("B3", "B5"), ("B2", "B5"), ("U3", "B3"))
        if part == "reuse"
        else (("B3", "Wmid"), ("Wmid", "Wfull"), ("B3", "Wfull"))
    )
    selected = [r for r in metrics if r["arm"] in arms]
    results = {}
    results["report_metric_rows"] = compare_table(
        folder / "metrics.csv", selected, ("id", "representation", "head")
    )
    groups = defaultdict(list)
    for r in selected:
        if r["world"] == "observed":
            groups[r["arm"], r["encoder"], r["decoder"], r["head"]].append(r)
    summaries = []
    for (arm, encoder, decoder, head), rows in groups.items():
        assert {r["seed"] for r in rows} == {0, 1, 2} and len(rows) == 3
        values = [r["balanced_accuracy"] for r in rows]
        summaries.append(
            dict(
                arm=arm,
                encoder=encoder,
                decoder=decoder,
                head=head,
                mean_BA=sum(values) / 3,
                min_BA=min(values),
                max_BA=max(values),
                train_BA=sum(r["train_BA"] for r in rows) / 3,
                mean_train_development_gap=sum(r["train_development_gap"] for r in rows)
                / 3,
                units=rows[0]["units"],
                sessions=rows[0]["sessions"],
                computational_repeats=3,
            )
        )
    results["report_summary_rows"] = compare_table(
        folder / "summary.csv", summaries, ("arm", "encoder", "decoder", "head")
    )
    lookup = {
        (r["world"], r["seed"], r["arm"], r["representation"], r["head"]): r
        for r in selected
    }
    differences, switches = [], []
    for before, after in contrasts:
        for r in selected:
            if r["arm"] != before:
                continue
            s = lookup[r["world"], r["seed"], after, r["representation"], r["head"]]
            differences.append(
                dict(
                    world=r["world"],
                    seed=r["seed"],
                    before=before,
                    after=after,
                    encoder=r["encoder"],
                    decoder=r["decoder"],
                    head=r["head"],
                    before_BA=r["balanced_accuracy"],
                    after_BA=s["balanced_accuracy"],
                    delta_BA=s["balanced_accuracy"] - r["balanced_accuracy"],
                    delta_training_BA=s["train_BA"] - r["train_BA"],
                )
            )
            truth, old = predictions[
                r["id"], r["representation"], r["head"], "development"
            ]
            other_truth, new = predictions[
                s["id"], s["representation"], s["head"], "development"
            ]
            np.testing.assert_array_equal(truth, other_truth)
            for label in sorted(set(truth)):
                choose = truth == label
                a = old[choose] == truth[choose]
                b = new[choose] == truth[choose]
                switches.append(
                    dict(
                        world=r["world"],
                        seed=r["seed"],
                        before=before,
                        after=after,
                        representation=r["representation"],
                        head=r["head"],
                        label=label,
                        rows=int(choose.sum()),
                        right_to_wrong=int((a & ~b).sum()),
                        wrong_to_right=int((~a & b).sum()),
                        both_right=int((a & b).sum()),
                        both_wrong=int((~a & ~b).sum()),
                    )
                )
    results["report_contrast_rows"] = compare_table(
        folder / "paired_contrasts.csv",
        differences,
        ("world", "seed", "before", "after", "encoder", "decoder", "head"),
    )
    results["report_error_switch_rows"] = compare_table(
        folder / "paired_error_switches.csv",
        switches,
        ("world", "seed", "before", "after", "representation", "head", "label"),
    )
    recalls = []
    for r in matrices:
        counts = np.array(r["counts"])
        for label, total, correct in zip(
            r["labels"], counts.sum(1), np.diag(counts), strict=True
        ):
            recalls.append(
                {k: v for k, v in r.items() if k not in ("labels", "counts")}
                | dict(
                    label=label,
                    appearances=int(total),
                    correct=int(correct),
                    recall=float(correct / total),
                )
            )
    results["report_class_recall_rows"] = compare_table(
        folder / "class_recall.csv",
        recalls,
        ("case", "encoder", "decoder", "head", "split", "label"),
    )
    ranking = []
    primary = [a for a in arms if a != "U3"]
    for encoder in ("raw", "pca", "cebra", "native"):
        for decoder in ("logistic", "svm", "knn", "lda"):
            rows = [
                r
                for r in summaries
                if r["encoder"] == encoder
                and r["decoder"] == decoder
                and r["head"] == "pair"
                and r["arm"] in primary
            ]
            rows.sort(key=lambda r: primary.index(r["arm"]))
            family = encoder if decoder == "logistic" else encoder + "_" + decoder
            correct = {
                arm: sum(
                    int(
                        (
                            predictions[
                                f"observed_seed{seed}_{arm}",
                                family,
                                "pair",
                                "development",
                            ][0]
                            == predictions[
                                f"observed_seed{seed}_{arm}",
                                family,
                                "pair",
                                "development",
                            ][1]
                        ).sum()
                    )
                    for seed in (0, 1, 2)
                )
                for arm in primary
            }
            # All pair classes have8development rows; three repeats have216rows.
            # Integer correct totals resolve mathematical ties before arm order.
            best = max(rows, key=lambda r: correct[r["arm"]])
            worst = min(rows, key=lambda r: correct[r["arm"]])
            ranking.append(
                dict(
                    encoder=encoder,
                    decoder=decoder,
                    best=best["arm"],
                    worst=worst["arm"],
                    best_mean_BA=best["mean_BA"],
                    worst_mean_BA=worst["mean_BA"],
                    gap=best["mean_BA"] - worst["mean_BA"],
                    best_ties=",".join(
                        r["arm"]
                        for r in rows
                        if correct[r["arm"]] == correct[best["arm"]]
                    ),
                    worst_ties=",".join(
                        r["arm"]
                        for r in rows
                        if correct[r["arm"]] == correct[worst["arm"]]
                    ),
                )
            )
    results["report_best_worst_rows"] = compare_table(
        folder / "best_worst.csv", ranking, ("encoder", "decoder")
    )
    return results
