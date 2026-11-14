"""Authenticate/reconcile the completed new run without fits or model loading."""

from __future__ import annotations
import argparse
import csv
import gzip
import json
from collections import Counter
from pathlib import Path

import nbformat
import numpy as np
from neuro.evaluation import classification_metrics
from neuro.studies.population_models import frozen_models
from .. import study
from .tables import assembly_tables, compare_table, derived_reports, read_rows


def verify(run, receipt_hash, *, notebook_factory=None, notebook_names=None):
    run = Path(run).resolve()
    assert study.sha(run / "receipt.json") == receipt_hash
    receipt = json.loads((run / "receipt.json").read_text())
    assert receipt["status"] == "completed" and receipt["mode"] == "train"
    for name, digest in receipt["files_sha256"].items():
        path = (run / name).resolve()
        assert path.is_relative_to(run) and study.sha(path) == digest, name
    if "parent_receipt_sha256" in receipt:
        parent_receipt_path = run / "parent-evidence/receipt.json"
        assert study.sha(parent_receipt_path) == receipt["parent_receipt_sha256"]
        parent = json.loads(parent_receipt_path.read_text())
        boundary = json.loads((run / "continuation.json").read_text())
        assert (
            parent["status"] == "failed"
            and boundary["inherited_cases"] == 32
            and boundary["new_cases"] == 16
        )
        assert boundary["parent_receipt_sha256"] == receipt["parent_receipt_sha256"]
        assert (
            boundary["inherited_path_mapping"].keys() == parent["files_sha256"].keys()
        )
        for source, target in boundary["inherited_path_mapping"].items():
            assert study.sha(run / target) == parent["files_sha256"][source]
        assert (
            study.sha(run / "parent-evidence/continuation-amendment.md")
            == boundary["amendment_sha256"]
        )
        own = json.loads((run / "continuation-source-pins.json").read_text())
        for path, digest in own.items():
            assert study.sha(run / "continuation-source-snapshot" / path) == digest
        continuation_resources = json.loads(
            (run / "continuation-resources.json").read_text()
        )
        assert (
            continuation_resources["status"] == "completed"
            and continuation_resources["seconds"] < 7200
        )
        assert (
            receipt["resources"]["seconds"]
            == parent["resources"]["seconds"] + continuation_resources["seconds"]
        )
        assert all(
            int(line.split()[1]) == 0
            for line in parent["resources"]["memory_events"].splitlines()
        )
    config = json.loads((run / "configuration.json").read_text())
    assert config == study.configuration(config["design"])
    root = Path(__file__).resolve().parents[3]
    pins = json.loads((run / "code-pins.json").read_text())
    orchestration_changes = {}
    for path, digest in pins.items():
        assert study.sha(run / "source-snapshot" / path) == digest
        current = study.sha(root / path)
        if path == "experiments/source_reuse_width_20261114/run.py":
            # The archived orchestrator produced the original handoff failure.
            # This auditor neither imports nor executes it. All code used by
            # this audit still has to match the original live-source pins.
            if current != digest:
                orchestration_changes[path] = dict(
                    executed_snapshot_sha256=digest, current_sha256=current
                )
        else:
            assert current == digest, path
    meta = study.metadata(root / "data/cue-source-v1")
    assert study.validate_design(meta, config["design"])
    with gzip.open(root / "data/cue-source-v1/outer_splits.csv.gz", "rt") as handle:
        outer = {r["source_trial_id"]: r for r in csv.DictReader(handle)}
    conditions = set(config["design"]["panel"]["conditions"])
    full_sessions = {
        s
        for s in meta["sessions"]
        if meta["aliases"][s] in config["design"]["rosters"]["full"]["session_aliases"]
    }
    full_sources = {
        r["source_trial_id"]: r
        for r in meta["sources"]
        if r["session_id"] in full_sessions and r["label"] in conditions
    }
    maps = {}
    for world in ["observed"] + [f"permuted{p}" for p in study.PERMUTATIONS]:
        mapping = {sid: r["label"] for sid, r in full_sources.items()}
        if world != "observed":
            rng = np.random.default_rng(int(world[8:]))
            for block in sorted(full_sessions):
                for split in ("development", "train"):
                    ids = sorted(
                        sid
                        for sid, r in full_sources.items()
                        if r["session_id"] == block
                        and r["split"]
                        == ("validation" if split == "development" else "train")
                    )
                    shuffled = rng.permutation([mapping[sid] for sid in ids])
                    mapping.update(zip(ids, map(str, shuffled), strict=True))
        maps[world] = mapping
    assert (
        json.loads((run / "actual-fit-counts.json").read_text())
        == config["expected_fit_counts"]
    )
    checked = Counter()
    lineages = {}
    numeric_features = {}
    predictions, block_values = {}, {}
    all_metrics, class_errors = [], []
    all_learning, all_trajectories = {}, {}
    unit_blocks = {u["cell_id"]: u["session_id"] for u in meta["units"]}
    expected_ids = {r["id"] for r in study.schedule()}
    assert {p.name for p in (run / "cases").iterdir()} == expected_ids
    terminal = [
        json.loads(line)
        for line in (run / "attempt-log.jsonl").read_text().splitlines()
    ]
    assert Counter(r["status"] for r in terminal) == {"started": 48, "completed": 48}
    assert all(
        Counter(r["status"] for r in terminal if r["id"] == cid)
        == {"started": 1, "completed": 1}
        for cid in expected_ids
    )
    for part, case_count in (("reuse", 32), ("width", 16)):
        expected = [
            c
            for c in study.schedule()
            if c["arm"]
            in (study.PART_ARMS["reuse"] if part == "reuse" else ("Wmid", "Wfull"))
        ]
        attempts = json.loads((run / f"attempts_{part}.json").read_text())
        assert len(attempts) == case_count and all(
            r["status"] == "completed" for r in attempts
        )
        assert {r["id"] for r in attempts} == {r["id"] for r in expected}
        actual = json.loads((run / f"actual-fit-counts-{part}.json").read_text())
        assert actual == {
            k: v * case_count // 48 for k, v in config["expected_fit_counts"].items()
        }
        errors_handle = (run / f"aggregates_{part}/source_errors.csv").open()
        errors = csv.DictReader(errors_handle)
        for case in expected:
            folder = run / "cases" / case["id"]
            done = json.loads((folder / "completion.json").read_text())
            assert all(done[k] == v for k, v in case.items())
            assert (
                done["composed_readout_splits_checked"] == 96
                and done["reloaded_encoders_checked"] == 4
            )
            assert done["paired_contributors_overlap"] == 0
            assert done["fit_counts"] == {
                k: v // 48 for k, v in config["expected_fit_counts"].items()
            }
            for name, digest in done["artifact_sha256"].items():
                assert study.sha(folder / name) == digest
            checked["native_session_encoders"] += done["native_session_encoders"]
            selected_sessions = {
                s
                for s in full_sessions
                if meta["aliases"][s]
                in config["design"]["rosters"][case["roster"]]["session_aliases"]
            }
            expected_units = {
                u["cell_id"]
                for u in meta["units"]
                if u["session_id"] in selected_sessions
            }
            mapping = maps[case["world"]]
            saved = {
                split: json.loads((folder / f"{split}_lineage.json").read_text())
                for split in ("train", "development")
            }
            case_record = json.loads((folder / "case.json").read_text())
            assert case_record["plan_identities"] == done["plan_identities"]
            assert (
                saved["train"]["units"]
                == saved["development"]["units"]
                == case_record["units"]
            )
            assert (
                saved["train"]["blocks"]
                == saved["development"]["blocks"]
                == case_record["blocks"]
            )
            for split, lineage in saved.items():
                assert lineage["identity"] == done["plan_identities"][split]
                assert (
                    set(lineage["blocks"]) == selected_sessions
                    and set(lineage["units"]) == expected_units
                )
                assert len(lineage["blocks"]) == done["native_session_encoders"]
                quota = case["rows_per_class"] if split == "train" else 8
                assert Counter(row["pair"] for row in lineage["rows"]) == {
                    c: quota for c in conditions
                }
                assert len({r["row_id"] for r in lineage["rows"]}) == 9 * quota
                for row in lineage["rows"]:
                    assert len(row["source_ids"]) == len(lineage["blocks"])
                    for block, sid in zip(
                        lineage["blocks"], row["source_ids"], strict=True
                    ):
                        assert (
                            sid in full_sources
                            and full_sources[sid]["session_id"] == block
                        )
                        assert full_sources[sid]["split"] == (
                            "train" if split == "train" else "validation"
                        )
                        assert mapping[sid] == row["pair"]
            train_ids = {sid for r in saved["train"]["rows"] for sid in r["source_ids"]}
            wanted = set()
            for block in selected_sessions:
                for condition in conditions:
                    pool = [
                        sid
                        for sid, r in full_sources.items()
                        if r["session_id"] == block
                        and r["split"] == "train"
                        and mapping[sid] == condition
                    ]
                    wanted.update(
                        study.source_order(
                            pool, block=block, condition=condition, seed=case["seed"]
                        )[: case["source_budget"]]
                    )
            assert train_ids == wanted
            counts = Counter(
                sid for r in saved["train"]["rows"] for sid in r["source_ids"]
            )
            quota, b = case["rows_per_class"], case["source_budget"]
            assert set(counts.values()) == {quota // b, (quota + b - 1) // b}
            train_contributors = {
                x
                for sid in train_ids
                for x in (sid, outer[sid]["previous_source_trial_id"])
            }
            assert not train_contributors & meta["protected"]
            dev_ids = {
                sid for r in saved["development"]["rows"] for sid in r["source_ids"]
            }
            dev_contributors = {
                x
                for sid in dev_ids
                for x in (sid, outer[sid]["previous_source_trial_id"])
            }
            assert not train_contributors & dev_contributors
            lineages[case["id"]] = saved
            metrics = json.loads((folder / "metrics.json").read_text())
            all_metrics.extend(metrics)
            confusions = {
                (r["representation"], r["head"]): r
                for r in json.loads((folder / "confusions.json").read_text())
            }
            assert len(metrics) == len(confusions) == 48
            assert {(r["encoder"], r["decoder"], r["head"]) for r in metrics} == {
                (e, d, h)
                for e in ("raw", "pca", "cebra", "native")
                for d in ("logistic", "svm", "knn", "lda")
                for h in ("pair", "start", "goal")
            }
            appearances = Counter(
                sid for row in saved["development"]["rows"] for sid in row["source_ids"]
            )
            with np.load(folder / "numeric_records.npz", allow_pickle=False) as arrays:
                numeric_features[case["id"]] = {
                    split: arrays[split + "_values"]
                    for split in ("train", "development")
                }
                for split, values in numeric_features[case["id"]].items():
                    lineage = saved[split]
                    assert len(set(lineage["units"])) == len(lineage["units"])
                    assert len(set(lineage["blocks"])) == len(lineage["blocks"])
                    assert values.shape == (
                        len(lineage["rows"]),
                        len(lineage["units"]),
                        10,
                    )
                    assert (
                        np.isfinite(values).all()
                        and (values >= 0).all()
                        and np.equal(values, np.floor(values)).all()
                    )
                    for block_index, block in enumerate(lineage["blocks"]):
                        columns = [
                            i
                            for i, u in enumerate(lineage["units"])
                            if unit_blocks[u] == block
                        ]
                        columns.sort(key=lambda i: lineage["units"][i])
                        names = tuple(lineage["units"][i] for i in columns)
                        for row_index, row in enumerate(lineage["rows"]):
                            identity = (row["source_ids"][block_index], names)
                            value = values[row_index, columns, :]
                            if identity in block_values:
                                np.testing.assert_array_equal(
                                    value, block_values[identity]
                                )
                            else:
                                block_values[identity] = value.copy()
                            checked["saved_source_block_consistency_checks"] += 1
                for encoder in ("pca", "cebra", "native"):
                    values = arrays[encoder + "_development_features"].reshape(
                        72, 10, 7
                    )
                    assert np.isfinite(values).all()
                    truth = arrays[encoder + "_pair_truth"].astype(str)
                    trajectory = json.loads((folder / "trajectories.json").read_text())[
                        encoder
                    ]
                    assert set(trajectory) == conditions
                    for label in conditions:
                        assert np.isfinite(trajectory[label]).all()
                        np.testing.assert_allclose(
                            np.array(trajectory[label]),
                            values[truth == label, :, :3].mean(0),
                            rtol=0,
                            atol=1e-12,
                        )
                        checked["trajectory_class_means"] += 1
                for encoder in ("raw", "pca", "cebra", "native"):
                    for split in ("train", "development"):
                        features = arrays[encoder + "_" + split + "_features"]
                        assert features.shape == (
                            len(saved[split]["rows"]),
                            10 * len(expected_units) if encoder == "raw" else 70,
                        )
                        assert np.isfinite(features).all()
                for record in metrics:
                    assert record["representation"] == (
                        record["encoder"]
                        if record["decoder"] == "logistic"
                        else record["encoder"] + "_" + record["decoder"]
                    )
                    assert all(record[k] == v for k, v in case.items())
                    assert record["units"] == len(expected_units) and record[
                        "sessions"
                    ] == len(selected_sessions)
                    assert (
                        record["train_rows"] == 9 * case["rows_per_class"]
                        and record["development_rows"] == 72
                    )
                    assert record["readout_features"] == (
                        10 * len(expected_units) if record["encoder"] == "raw" else 70
                    )
                    assert record["classes"] == (9 if record["head"] == "pair" else 6)
                    ratio = 16 / case["rows_per_class"]
                    assert record["logistic_C"] == (
                        0.01 * ratio if record["decoder"] == "logistic" else ""
                    )
                    assert record["svm_C"] == (
                        ratio if record["decoder"] == "svm" else ""
                    )
                    assert np.isclose(
                        record["train_development_gap"],
                        record["train_BA"] - record["balanced_accuracy"],
                        rtol=0,
                        atol=1e-12,
                    )
                    key = record["representation"] + "_" + record["head"]
                    classes = np.unique(arrays[key + "_truth"])
                    for split, prefix in (("development", ""), ("train", "_train")):
                        truth, pred = (
                            arrays[key + prefix + "_truth"],
                            arrays[key + prefix + "_prediction"],
                        )
                        scores = arrays[
                            key
                            + prefix
                            + (
                                "_margins"
                                if record["decoder"] == "svm"
                                else "_probabilities"
                            )
                        ]
                        assert np.isfinite(scores).all()
                        assert scores.shape == (
                            len(saved[split]["rows"]),
                            record["classes"],
                        )
                        expected_truth = [
                            r["pair"]
                            if record["head"] == "pair"
                            else r["pair"].split("->")[
                                0 if record["head"] == "start" else 1
                            ]
                            for r in saved[split]["rows"]
                        ]
                        assert truth.astype(str).tolist() == expected_truth
                        predictions[
                            case["id"], record["representation"], record["head"], split
                        ] = (truth.astype(str), pred.astype(str))
                        m = classification_metrics(
                            truth,
                            pred,
                            classes=classes,
                            probabilities=None
                            if record["decoder"] == "svm"
                            else scores,
                        )
                        if split == "train":
                            assert np.isclose(
                                m["balanced_accuracy"],
                                record["train_BA"],
                                rtol=0,
                                atol=1e-12,
                            )
                        else:
                            for name in (
                                "accuracy",
                                "balanced_accuracy",
                                "macro_f1",
                                "log_loss",
                            ):
                                if record.get(name) is None:
                                    assert m.get(name) is None
                                else:
                                    assert np.isclose(
                                        m[name], record[name], rtol=0, atol=1e-12
                                    )
                            assert (
                                m["confusion_counts"]
                                == confusions[record["representation"], record["head"]][
                                    "counts"
                                ]
                            )
                            wrong = pred != truth
                            for label in classes:
                                choose = truth == label
                                class_errors.append(
                                    dict(
                                        case=case["id"],
                                        representation=record["representation"],
                                        head=record["head"],
                                        **{"class": str(label)},
                                        evaluated_rows=int(choose.sum()),
                                        wrong_rows=int(wrong[choose].sum()),
                                        error_rate=float(wrong[choose].mean()),
                                    )
                                )
                            involvement = Counter(
                                sid
                                for row, err in zip(
                                    saved[split]["rows"], wrong, strict=True
                                )
                                if err
                                for sid in row["source_ids"]
                            )
                            for sid in sorted(appearances):
                                actual = next(errors)
                                assert (
                                    actual["assembly_identity"]
                                    == saved["development"]["identity"]
                                )
                                assert (
                                    actual["case"],
                                    actual["representation"],
                                    actual["head"],
                                    actual["source"],
                                ) == (
                                    case["id"],
                                    record["representation"],
                                    record["head"],
                                    meta["source_aliases"][sid],
                                )
                                assert (
                                    actual["session"]
                                    == meta["aliases"][full_sources[sid]["session_id"]]
                                )
                                assert int(actual["appearances"]) == appearances[sid]
                                assert (
                                    int(actual["wrong_appearances"]) == involvement[sid]
                                )
                                assert (
                                    int(actual["correct_appearances"])
                                    == appearances[sid] - involvement[sid]
                                )
                                assert np.isclose(
                                    float(actual["wrong_fraction"]),
                                    involvement[sid] / appearances[sid],
                                )
                                checked["source_error_rows"] += 1
                        checked["split_metric_checks"] += 1
            learning_rows = json.loads((folder / "learning.json").read_text())
            assert len(learning_rows) == 2 and {r["case"] for r in learning_rows} == {
                case["id"] + "_" + e for e in ("cebra", "native")
            }
            for learning in learning_rows:
                assert (
                    len(learning["loss"]["total"]) == 1000
                    and np.isfinite(learning["loss"]["total"]).all()
                )
                assert (
                    learning["iterations"] == 1000 and learning["seed"] == case["seed"]
                )
                assert learning["case"] == case["id"] + "_" + learning["encoder"]
                assert learning["sampler_seed"] == case["seed"] + (
                    1009 if learning["encoder"] == "cebra" else 3011
                )
                all_learning[learning["case"]] = learning
                checked["learning_curves"] += 1
            all_trajectories[case["id"]] = json.loads(
                (folder / "trajectories.json").read_text()
            )
            checked["cases"] += 1
        assert next(errors, None) is None
        errors_handle.close()
        checked.update(
            assembly_tables(run, part, expected, lineages, maps, full_sources, meta)
        )
        part_ids = {r["id"] for r in expected}
        checked["aggregate_class_error_rows"] += compare_table(
            run / f"aggregates_{part}/class_errors.csv",
            [r for r in class_errors if r["case"] in part_ids],
            ("case", "representation", "head", "class"),
        )
    for world in maps:
        for seed in (0, 1, 2) if world == "observed" else (0,):
            names = {a: f"{world}_seed{seed}_{a}" for a in study.ARMS}
            for arm in ("B2", "B5", "U3"):
                assert (
                    lineages[names[arm]]["development"]["rows"]
                    == lineages[names["B3"]]["development"]["rows"]
                )
                np.testing.assert_array_equal(
                    numeric_features[names[arm]]["development"],
                    numeric_features[names["B3"]]["development"],
                )
            for arm in ("B3", "Wmid"):
                for split in ("train", "development"):
                    a, b = lineages[names[arm]][split], lineages[names["Wfull"]][split]
                    bi = [b["blocks"].index(v) for v in a["blocks"]]
                    for row, full in zip(a["rows"], b["rows"], strict=True):
                        assert (row["row_id"], row["pair"], row["source_ids"]) == (
                            full["row_id"],
                            full["pair"],
                            [full["source_ids"][i] for i in bi],
                        )
                    ui = [b["units"].index(v) for v in a["units"]]
                    np.testing.assert_array_equal(
                        numeric_features[names[arm]][split],
                        numeric_features[names["Wfull"]][split][:, ui],
                    )
            for arm in study.ARMS:
                if seed:
                    assert (
                        lineages[names[arm]]["development"]
                        == lineages[f"{world}_seed0_{arm}"]["development"]
                    )
                    np.testing.assert_array_equal(
                        numeric_features[names[arm]]["development"],
                        numeric_features[f"{world}_seed0_{arm}"]["development"],
                    )
    if notebook_factory is None:
        from ..build_notebooks import make_notebook

        notebook_factory = make_notebook
    if notebook_names is None:
        notebook_names = {
            "reuse": "source_reuse_20261114",
            "width": "population_width_20261114",
        }
    assert set(notebook_names) == {"reuse", "width"}
    for part, cases in (("reuse", 32), ("width", 24)):
        filename = notebook_names[part]
        notebook = nbformat.read(run / (filename + ".executed.ipynb"), as_version=4)
        frozen = notebook_factory(part)
        assert [(c.cell_type, c.source) for c in notebook.cells] == [
            (c.cell_type, c.source) for c in frozen.cells
        ]
        cells = [c for c in notebook.cells if c.cell_type == "code"]
        assert [c.execution_count for c in cells] == list(range(1, len(cells) + 1))
        assert not any(o.output_type == "error" for c in cells for o in c.outputs)
        checked["executed_notebook_code_cells"] += len(cells)
        manifest = json.loads((run / f"report_{part}/report_manifest.json").read_text())
        assert (
            manifest["metric_rows"] == cases * 48
            and manifest["confusion_matrices"] == cases * 96
        )
        for figure in manifest["figures"]:
            assert (
                study.sha(run / f"report_{part}" / figure["file"]) == figure["sha256"]
            )
        checked["report_figures"] += len(manifest["figures"])
        matrices = json.loads(
            (run / f"report_{part}/confusion_matrices.json").read_text()
        )
        selected_ids = {
            c["id"] for c in study.schedule() if c["arm"] in study.PART_ARMS[part]
        }
        actual_keys = {
            (r["case"], r["encoder"], r["decoder"], r["head"], r["split"])
            for r in matrices
        }
        expected_keys = {
            (cid, e, d, h, s)
            for cid in selected_ids
            for e in ("raw", "pca", "cebra", "native")
            for d in ("logistic", "svm", "knn", "lda")
            for h in ("pair", "start", "goal")
            for s in ("train", "development")
        }
        assert (
            actual_keys == expected_keys
            and len(matrices) == len(expected_keys) == cases * 96
        )
        for record in matrices:
            case_definition = next(
                c for c in study.schedule() if c["id"] == record["case"]
            )
            assert all(
                record[k] == case_definition[k] for k in ("world", "seed", "arm")
            )
            folder = run / "cases" / record["case"]
            prefix = "" if record["split"] == "development" else "_train"
            family = (
                record["encoder"]
                if record["decoder"] == "logistic"
                else record["encoder"] + "_" + record["decoder"]
            )
            truth, pred = predictions[
                record["case"], family, record["head"], record["split"]
            ]
            assert record["labels"] == sorted(set(truth))
            counts = np.array(
                [
                    [int(((truth == a) & (pred == b)).sum()) for b in record["labels"]]
                    for a in record["labels"]
                ]
            )
            np.testing.assert_array_equal(counts, record["counts"])
            checked["report_matrix_views"] += 1
        checked.update(derived_reports(run, part, all_metrics, predictions, matrices))
        compare_table(
            run / f"report_{part}/summary.csv",
            manifest["summary"],
            ("arm", "encoder", "decoder", "head"),
        )
        compare_table(
            run / f"report_{part}/best_worst.csv",
            manifest["best_worst"],
            ("encoder", "decoder"),
        )
        expected_pool_rows = []
        for source_part in ("reuse", "width") if part == "width" else ("reuse",):
            expected_pool_rows.extend(
                r
                for r in read_rows(run / f"aggregates_{source_part}/pool_usage.csv")
                if r["case"] in selected_ids
            )
        checked["report_pool_usage_rows"] += compare_table(
            run / f"report_{part}/actual_pool_usage.csv",
            expected_pool_rows,
            ("case", "split", "session", "pair"),
        )
        maps_expected = []
        for roster, info in config["design"]["rosters"].items():
            for unit in meta["units"]:
                session = meta["aliases"][unit["session_id"]]
                if (
                    session
                    not in config["design"]["rosters"]["full"]["session_aliases"]
                ):
                    continue
                maps_expected.append(
                    dict(
                        roster=roster,
                        unit=meta["unit_aliases"][unit["cell_id"]],
                        session=session,
                        retained=session in info["session_aliases"],
                        spatial_map_status="unknown",
                        reason="compact cue-source lacks authenticated field/occupancy/coordinate maps",
                    )
                )
        checked["map_availability_rows"] += compare_table(
            run / f"report_{part}/retained_removed_units_and_map_availability.csv",
            maps_expected,
            ("roster", "unit"),
        )
        learning = json.loads((run / f"report_{part}/learning.json").read_text())
        assert len(learning) == cases * 2 and {r["case"] for r in learning} == {
            cid + "_" + e for cid in selected_ids for e in ("cebra", "native")
        }
        assert all(r == all_learning[r["case"]] for r in learning)
        trajectories = json.loads(
            (run / f"report_{part}/trajectories.json").read_text()
        )
        assert (
            len(trajectories) == cases
            and {r["case"] for r in trajectories} == selected_ids
        )
        assert all(
            r["coordinates"] == all_trajectories[r["case"]] for r in trajectories
        )
    assert (
        checked["cases"] == 48
        and checked["split_metric_checks"] == 4608
        and checked["native_session_encoders"] == 344
    )
    assert checked["learning_curves"] == 96 and checked["report_figures"] == 61
    assert checked["report_matrix_views"] == 5376
    resources = receipt["resources"]
    assert resources["memory_peak_bytes"] < 4 * 2**30 and resources["seconds"] < 10800
    assert all(
        int(line.split()[1]) == 0 for line in resources["memory_events"].splitlines()
    )
    return dict(
        status="passed",
        receipt_sha256=receipt_hash,
        authenticated_files=len(receipt["files_sha256"]),
        checks=dict(checked),
        actual_fit_counts=config["expected_fit_counts"],
        post_execution_orchestration_changes=orchestration_changes,
        classification="no-fit numeric/lineage audit of this new run; no historical replay",
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--receipt-sha256", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    with frozen_models():
        result = verify(args.run, args.receipt_sha256)
    if args.output.exists():
        raise ValueError("audit output already exists")
    study.write_json(args.output, result)
    print(json.dumps(result, indent=2))
