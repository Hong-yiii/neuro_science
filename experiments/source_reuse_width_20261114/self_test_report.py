"""Invented evidence-shape/render smoke test; never scientific results or fits."""

import argparse
from pathlib import Path
import numpy as np
from neuro.notebook_artifacts import target_heads
from neuro.evaluation import classification_metrics
from neuro.pseudopopulation import materialize
from neuro.studies.population_models import frozen_models
from neuro.studies.source_support_ablation import usage_tables
from .test_study import fixture
from . import study, report


def smoke(out):
    out.mkdir(parents=True, exist_ok=False)
    data, meta, design = fixture()
    design["panel"] = {
        "conditions": [c for c, _ in data.target_definition.condition_to_target]
    }
    meta["units"] = [dict(cell_id=u.unit_id, session_id=u.block_id) for u in data.units]
    meta["unit_aliases"] = {u.unit_id: f"U{i:03d}" for i, u in enumerate(data.units)}
    config = study.configuration(design)
    aggregates = {
        part: {
            k: []
            for k in ("metrics", "confusions", "learning", "trajectories", "pool_usage")
        }
        for part in ("reuse", "width")
    }
    for case in study.schedule():
        part = "reuse" if case["arm"] in study.PART_ARMS["reuse"] else "width"
        agg = aggregates[part]
        permutation = None if case["world"] == "observed" else int(case["world"][8:])
        source, tp, dp = study.paired_plans(
            data, meta, design, seed=case["seed"], permutation=permutation
        )[case["arm"]]
        train, dev = materialize(source, tp), materialize(source, dp)
        yt, yd = target_heads(train), target_heads(dev)
        folder = out / "cases" / case["id"]
        folder.mkdir(parents=True)
        metrics, confusions, arrays = [], [], {}
        for encoder in report.ENCODERS:
            for decoder in report.DECODERS:
                family = encoder if decoder == "logistic" else encoder + "_" + decoder
                for head in ("pair", "start", "goal"):
                    classes = np.unique(yt[head])
                    pred = np.roll(yd[head], case["seed"] + 1)
                    metric = classification_metrics(yd[head], pred, classes=classes)
                    metrics.append(
                        dict(
                            **case,
                            representation=family,
                            encoder=encoder,
                            decoder=decoder,
                            head=head,
                            units=len(source.units),
                            sessions=len(source.block_ids),
                            train_BA=0.5,
                            train_development_gap=0.5 - metric["balanced_accuracy"],
                            **{
                                k: metric[k]
                                for k in ("balanced_accuracy", "accuracy", "macro_f1")
                            },
                        )
                    )
                    confusions.append(
                        dict(
                            **case,
                            representation=family,
                            head=head,
                            labels=list(classes),
                            counts=metric["confusion_counts"],
                        )
                    )
                    name = family + "_" + head
                    arrays[name + "_truth"] = yd[head]
                    arrays[name + "_prediction"] = pred
                    arrays[name + "_train_truth"] = yt[head]
                    arrays[name + "_train_prediction"] = np.roll(yt[head], 1)
        study.write_json(folder / "metrics.json", metrics)
        study.write_json(folder / "confusions.json", confusions)
        np.savez_compressed(folder / "numeric_records.npz", **arrays)
        study.write_json(
            folder / "development_lineage.json",
            dict(
                blocks=list(dev.block_ids),
                units=list(dev.unit_ids),
                rows=[
                    dict(
                        row_id=r.row_id, pair=r.condition, source_ids=list(r.source_ids)
                    )
                    for r in dp.rows
                ],
            ),
        )
        study.write_json(
            folder / "completion.json",
            dict(
                **case,
                classification="INVENTED REPORT SMOKE; ZERO FITS",
                artifact_sha256={
                    p.name: study.sha(p) for p in folder.iterdir() if p.is_file()
                },
            ),
        )
        agg["metrics"] += metrics
        agg["confusions"] += confusions
        agg["learning"] += [
            dict(
                case=case["id"] + "_" + e,
                encoder=e,
                loss={"total": np.linspace(4, 3, 1000).tolist()},
            )
            for e in ("cebra", "native")
        ]
        agg["trajectories"].append(
            dict(
                case=case["id"],
                coordinates={
                    e: {
                        c: np.zeros((10, 3)).tolist()
                        for c in design["panel"]["conditions"]
                    }
                    for e in ("pca", "cebra", "native")
                },
            )
        )
        for plan in (tp, dp):
            agg["pool_usage"] += usage_tables(source, plan, meta, case["id"])[0]
    for part, agg in aggregates.items():
        folder = out / ("aggregates_" + part)
        folder.mkdir()
        for key, values in agg.items():
            if key in ("metrics", "pool_usage"):
                study.write_csv(folder / (key + ".csv"), values)
            else:
                study.write_json(folder / (key + ".json"), values)
    for part in ("reuse", "width"):
        result = report.create_report(out, part, config, meta)
        assert result["metric_rows"] == (32 if part == "reuse" else 24) * 48
        assert result["confusion_matrices"] == 2 * result["metric_rows"]
        assert result["error_switch_rows"] == (4 if part == "reuse" else 3) * 8 * 16 * (
            9 + 6 + 6
        )
        print(
            part,
            {
                k: result[k]
                for k in ("metric_rows", "confusion_matrices", "error_switch_rows")
            },
            "figures",
            len(result["figures"]),
            flush=True,
        )
    # A missing shared artifact must fail instead of silently dropping a bridge case.
    missing = out / "cases/observed_seed0_B3/metrics.json"
    missing.rename(missing.with_suffix(".removed"))
    try:
        study.load_results(out, "width")
    except FileNotFoundError:
        pass
    else:
        raise AssertionError("missing bridge evidence was silently accepted")
    missing.with_suffix(".removed").rename(missing)
    print("Invented report smoke passed; zero biological access or fits.", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    with frozen_models():
        smoke(args.output)
