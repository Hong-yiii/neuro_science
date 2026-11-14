"""Authenticate and reconcile NEW-grid numeric evidence; no model loading or fitting."""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
from collections import Counter
from pathlib import Path

import numpy as np
from neuro.evaluation import classification_metrics


def sha(path):
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def verify(run, receipt_hash):
    assert sha(run / "receipt.json") == receipt_hash
    receipt = json.loads((run / "receipt.json").read_text())
    assert receipt["status"] == "completed"
    for relative, digest in receipt["files_sha256"].items():
        path = (run / relative).resolve()
        assert path.is_relative_to(run.resolve()) and sha(path) == digest, relative
    config = json.loads((run / "configuration.json").read_text())
    assert (
        config["study"] == "population-grid-20261111"
        and config["output_dimension"] == 7
    )
    attempts = json.loads((run / "attempts.json").read_text())
    assert len(attempts) == 111 and all(r["status"] == "completed" for r in attempts)
    assert len({r["id"] for r in attempts}) == 111
    expected_schedule = {
        f"observed_seed{s}_K{k}_{r}_{p}"
        for k in (30, 20, 15)
        for s in (0, 1, 2)
        for r in ("S33", "S67", "S100")
        for p in ("U2", "R16", "F16")
    } | {
        f"permuted{n}_seed0_K{k}_S100_{p}"
        for n in range(60000, 60005)
        for k in (30, 20, 15)
        for p in ("U2", "F16")
    }
    assert {r["id"] for r in attempts} == expected_schedule
    metrics = list(csv.DictReader((run / "aggregates/metrics.csv").open()))
    assert len(metrics) == 5328
    indexed = {(r["id"], r["representation"], r["head"]): r for r in metrics}
    assert len(indexed) == 5328
    root = Path(__file__).resolve().parents[1]
    source_root = root / "data/cue-source-v1"
    code_pins = json.loads((run / "code-pins.json").read_text())
    assert sha(root / "src/neuro/evaluation.py") == code_pins["src/neuro/evaluation.py"]
    for relative, digest in config["design"]["metadata_sha256"].items():
        assert sha(source_root / relative) == digest
    with gzip.open(source_root / "outer_splits.csv.gz", "rt") as h:
        outer = {r["source_trial_id"]: r for r in csv.DictReader(h)}
    counts = Counter()
    checked_errors = checked_readouts = native_networks = 0
    errors = csv.DictReader((run / "aggregates/source_errors.csv").open())
    confusions = json.loads((run / "aggregates/confusions.json").read_text())
    ci = {(r["id"], r["representation"], r["head"]): r for r in confusions}
    assert len(ci) == 5328
    source_alias = {}
    with gzip.open(source_root / "inner_splits.csv.gz", "rt") as h:
        inner = list(csv.DictReader(h))
    for i, r in enumerate(sorted(inner, key=lambda r: r["source_trial_id"])):
        source_alias[r["source_trial_id"]] = f"T{i + 1:05d}"
    protected = {
        s
        for r in inner
        if r["split"] == "validation"
        for s in (
            r["source_trial_id"],
            outer[r["source_trial_id"]]["previous_source_trial_id"],
        )
    }
    assert len(protected) == 5872
    original = {r["source_trial_id"]: r for r in inner}
    units = sorted(
        json.loads((source_root / "manifest.json").read_text())["units"],
        key=lambda u: u["cell_id"],
    )
    sessions = sorted({u["session_id"] for u in units})
    aliases = {s: f"S{i + 1:02d}" for i, s in enumerate(sessions)}
    contracts = {}
    for panel in config["design"]["panels"]:
        k, conditions = panel["class_count"], panel["conditions"]
        full = next(
            g
            for g in config["design"]["grid"]
            if g["class_count"] == k and g["roster"] == "S100"
        )
        blocks = list(
            dict.fromkeys(
                u["session_id"]
                for u in units
                if aliases[u["session_id"]] in full["session_aliases"]
            )
        )
        eligible = {
            sid: row
            for sid, row in original.items()
            if row["session_id"] in blocks
            and row["label"] in conditions
            and (
                row["split"] == "validation"
                or not {sid, outer[sid]["previous_source_trial_id"]} & protected
            )
        }
        for permutation in (None, *range(60000, 60005)):
            mapping = {sid: r["label"] for sid, r in eligible.items()}
            if permutation is not None:
                rng = np.random.default_rng(permutation)
                for block in sorted(blocks):
                    for split in (
                        "validation",
                        "train",
                    ):  # SourceData sorts development before train.
                        ids = sorted(
                            sid
                            for sid, r in eligible.items()
                            if r["session_id"] == block and r["split"] == split
                        )
                        values = rng.permutation([mapping[sid] for sid in ids])
                        mapping.update(zip(ids, map(str, values), strict=True))
            for seed in (0, 1, 2) if permutation is None else (0,):
                rng = np.random.default_rng(20261111 + seed)
                chosen = set()
                for condition in conditions:
                    for block in blocks:
                        pool = sorted(
                            sid
                            for sid, r in eligible.items()
                            if r["split"] == "train"
                            and r["session_id"] == block
                            and mapping[sid] == condition
                        )
                        chosen.update(rng.choice(pool, 2, replace=False).tolist())
                contracts[k, permutation, seed] = eligible, mapping, chosen
    input_case = {}
    for attempt in attempts:
        case = attempt["id"]
        directory = run / "cases" / case
        completion = json.loads((directory / "completion.json").read_text())
        counts.update(completion["fit_counts"])
        native_networks += completion["native_session_encoders"]
        assert completion["paired_contributors_overlap"] == 0
        assert (
            completion["reloaded_encoders_checked"] == 4
            and completion["composed_readout_splits_checked"] == 96
        )
        for name, digest in completion["artifact_sha256"].items():
            assert sha(directory / name) == digest
        for name, digest in completion["state_sha256"].items():
            assert sha(directory / name) == digest
        case_meta = json.loads((directory / "case.json").read_text())
        lineage = {
            split: json.loads((directory / (split + "_lineage.json")).read_text())
            for split in ("train", "development")
        }
        input_case[case] = (case_meta, lineage)
        k = attempt["class_count"]
        permutation = (
            None
            if attempt["world"] == "observed"
            else int(attempt["world"].removeprefix("permuted"))
        )
        eligible, mapping, chosen = contracts[k, permutation, attempt["seed"]]
        grid = next(
            g
            for g in config["design"]["grid"]
            if g["configuration"] == f"K{k}_{attempt['roster']}"
        )
        expected_blocks = list(
            dict.fromkeys(
                u["session_id"]
                for u in units
                if aliases[u["session_id"]] in grid["session_aliases"]
            )
        )
        assert case_meta["blocks"] == expected_blocks
        assert case_meta["units"] == [
            u["cell_id"] for u in units if u["session_id"] in expected_blocks
        ]
        conditions = next(
            p["conditions"] for p in config["design"]["panels"] if p["class_count"] == k
        )
        unions = []
        for split in ("train", "development"):
            assert (
                lineage[split]["blocks"] == case_meta["blocks"]
                and lineage[split]["units"] == case_meta["units"]
            )
            assert lineage[split]["identity"] == case_meta["plan_identities"][split]
            quota = (
                8
                if split == "development"
                else 2
                if attempt["sampling"] == "U2"
                else 16
            )
            assert Counter(r["pair"] for r in lineage[split]["rows"]) == {
                c: quota for c in conditions
            }
            assert len({r["row_id"] for r in lineage[split]["rows"]}) == quota * k
            for row in lineage[split]["rows"]:
                assert len(row["source_ids"]) == len(expected_blocks)
                for block, sid in zip(expected_blocks, row["source_ids"], strict=True):
                    assert sid in eligible and eligible[sid]["session_id"] == block
                    assert original[sid]["split"] == (
                        "train" if split == "train" else "validation"
                    )
                    assert mapping[sid] == row["pair"]
                    assert (
                        outer[sid]["split"]
                        == outer[outer[sid]["previous_source_trial_id"]]["split"]
                        == "train"
                    )
            current = {
                sid for row in lineage[split]["rows"] for sid in row["source_ids"]
            }
            contributors = current | {
                outer[sid]["previous_source_trial_id"] for sid in current
            }
            if split == "train":
                assert not contributors & protected
            unions.append(contributors)
        assert not unions[0] & unions[1]
        use = Counter(
            sid for row in lineage["train"]["rows"] for sid in row["source_ids"]
        )
        if attempt["sampling"] == "U2":
            assert set(use.values()) == {1}
        if attempt["sampling"] == "R16":
            assert set(use.values()) == {8}
        expected_sources = {
            sid
            for sid, r in eligible.items()
            if r["split"] == "train"
            and r["session_id"] in expected_blocks
            and (attempt["sampling"] == "F16" or sid in chosen)
        }
        assert set(use) == expected_sources
        for block in expected_blocks:
            for condition in conditions:
                values = [
                    use[sid]
                    for sid in expected_sources
                    if original[sid]["session_id"] == block
                    and mapping[sid] == condition
                ]
                assert values and max(values) - min(values) <= 1
        native = json.loads((directory / "native_diagnostics.json").read_text())
        assert native["iterations"] == 1000 and native["torch_threads"] == 1
        assert native["sessions"] == len(case_meta["blocks"])
        assert native["session_input_dimensions"] == [
            sum(u["session_id"] == block for u in units) for block in expected_blocks
        ]
        assert (
            native["references_per_update"]
            == native["batch_per_session"] * native["sessions"]
            <= 256
        )
        learning = json.loads((directory / "learning.json").read_text())
        assert len(learning) == 2 and all(
            len(r["loss"]["total"]) == 1000 for r in learning
        )
        with np.load(directory / "numeric_records.npz", allow_pickle=False) as arrays:
            for split in ("train", "development"):
                assert arrays[split + "_values"].shape == (
                    len(lineage[split]["rows"]),
                    len(case_meta["units"]),
                    10,
                )
            expected_truth = {
                split: {
                    "pair": np.array([r["pair"] for r in lineage[split]["rows"]]),
                    "start": np.array(
                        [r["pair"].split("->")[0] for r in lineage[split]["rows"]]
                    ),
                    "goal": np.array(
                        [r["pair"].split("->")[1] for r in lineage[split]["rows"]]
                    ),
                }
                for split in ("train", "development")
            }
            for encoder in ("raw", "pca", "cebra", "native"):
                for split in ("train", "development"):
                    assert arrays[encoder + "_" + split + "_features"].shape[1] == (
                        10 * len(case_meta["units"]) if encoder == "raw" else 70
                    )
                for decoder in ("logistic", "svm", "knn", "lda"):
                    family = (
                        encoder if decoder == "logistic" else encoder + "_" + decoder
                    )
                    for head in ("pair", "start", "goal"):
                        name = family + "_" + head
                        metric = indexed[case, family, head]
                        matrix = ci[case, family, head]
                        for split, suffix in [("train", "_train"), ("development", "")]:
                            truth = arrays[name + suffix + "_truth"]
                            pred = arrays[name + suffix + "_prediction"]
                            np.testing.assert_array_equal(
                                truth, expected_truth[split][head]
                            )
                            score = arrays[
                                name
                                + suffix
                                + ("_margins" if decoder == "svm" else "_probabilities")
                            ]
                            assert np.isfinite(score).all()
                            assert score.shape == (
                                len(truth),
                                k if head == "pair" else 6,
                            )
                            if (
                                decoder == "knn"
                                and head == "pair"
                                and attempt["sampling"] == "U2"
                            ):
                                assert score.max() <= 0.4 + 1e-7
                            computed = classification_metrics(
                                truth,
                                pred,
                                classes=np.asarray(matrix["labels"]),
                                probabilities=None if decoder == "svm" else score,
                            )
                            if split == "train":
                                np.testing.assert_allclose(
                                    float(metric["train_BA"]),
                                    computed["balanced_accuracy"],
                                    atol=1e-12,
                                    rtol=1e-12,
                                )
                            else:
                                assert (
                                    abs(
                                        float(metric["train_development_gap"])
                                        - (
                                            float(metric["train_BA"])
                                            - computed["balanced_accuracy"]
                                        )
                                    )
                                    < 1e-12
                                )
                                for field in (
                                    "balanced_accuracy",
                                    "accuracy",
                                    "macro_f1",
                                ):
                                    np.testing.assert_allclose(
                                        float(metric[field]),
                                        computed[field],
                                        atol=1e-12,
                                        rtol=1e-12,
                                    )
                                if decoder == "svm":
                                    assert metric["log_loss"] == ""
                                else:
                                    np.testing.assert_allclose(
                                        float(metric["log_loss"]),
                                        computed["log_loss"],
                                        atol=1e-12,
                                        rtol=1e-12,
                                    )
                                np.testing.assert_array_equal(
                                    matrix["counts"], computed["confusion_counts"]
                                )
                                appearances, wrong = Counter(), Counter()
                                for row, error in zip(
                                    lineage["development"]["rows"],
                                    pred != truth,
                                    strict=True,
                                ):
                                    appearances.update(row["source_ids"])
                                    if error:
                                        wrong.update(row["source_ids"])
                                for sid in sorted(appearances):
                                    er = next(errors)
                                    checked_errors += 1
                                    assert (
                                        er["case"],
                                        er["representation"],
                                        er["head"],
                                        er["source"],
                                    ) == (case, family, head, source_alias[sid])
                                    assert (
                                        er["session"]
                                        == aliases[original[sid]["session_id"]]
                                    )
                                    assert (
                                        er["assembly_identity"]
                                        == case_meta["plan_identities"]["development"]
                                    )
                                    assert (
                                        int(er["appearances"]) == appearances[sid]
                                        and int(er["wrong_appearances"]) == wrong[sid]
                                    )
                                    assert (
                                        int(er["correct_appearances"])
                                        == appearances[sid] - wrong[sid]
                                    )
                                    assert (
                                        abs(
                                            float(er["wrong_fraction"])
                                            - wrong[sid] / appearances[sid]
                                        )
                                        < 1e-12
                                    )
                        checked_readouts += 1
        print("Verified", case, flush=True)
    assert next(errors, None) is None
    assert native_networks == 2174 and checked_readouts == 5328
    assert (
        dict(counts)
        == config["expected_fit_counts"]
        == json.loads((run / "actual-fit-counts.json").read_text())
    )
    # Exact common plans and arrays for every observed comparison, no model replay.
    projections = policy_pairs = 0
    for k in (30, 20, 15):
        for seed in (0, 1, 2):
            for policy in ("U2", "R16", "F16"):
                full = f"observed_seed{seed}_K{k}_S100_{policy}"
                meta, lin = input_case[full]
                with np.load(
                    run / "cases" / full / "numeric_records.npz", allow_pickle=False
                ) as full_values:
                    for roster in ("S33", "S67"):
                        small = f"observed_seed{seed}_K{k}_{roster}_{policy}"
                        sm, sl = input_case[small]
                        cols = [meta["units"].index(u) for u in sm["units"]]
                        positions = [meta["blocks"].index(b) for b in sm["blocks"]]
                        for split in ("train", "development"):
                            assert sl[split]["rows"] == [
                                {
                                    **row,
                                    "source_ids": [
                                        row["source_ids"][i] for i in positions
                                    ],
                                }
                                for row in lin[split]["rows"]
                            ]
                        with np.load(
                            run / "cases" / small / "numeric_records.npz",
                            allow_pickle=False,
                        ) as smaller:
                            for split in ("train", "development"):
                                np.testing.assert_array_equal(
                                    smaller[split + "_values"],
                                    full_values[split + "_values"][:, cols],
                                )
                        projections += 1
            for roster in ("S33", "S67", "S100"):
                ids = [
                    f"observed_seed{seed}_K{k}_{roster}_{p}"
                    for p in ("U2", "R16", "F16")
                ]
                ls = [input_case[i][1] for i in ids]
                assert {
                    sid for r in ls[0]["train"]["rows"] for sid in r["source_ids"]
                } == {sid for r in ls[1]["train"]["rows"] for sid in r["source_ids"]}
                assert (
                    ls[0]["development"]["rows"]
                    == ls[1]["development"]["rows"]
                    == ls[2]["development"]["rows"]
                )
                with np.load(
                    run / "cases" / ids[0] / "numeric_records.npz", allow_pickle=False
                ) as reference:
                    for case in ids[1:]:
                        with np.load(
                            run / "cases" / case / "numeric_records.npz",
                            allow_pickle=False,
                        ) as other:
                            np.testing.assert_array_equal(
                                reference["development_values"],
                                other["development_values"],
                            )
                policy_pairs += 1
    fixed_development_checks = 0
    for k in (30, 20, 15):
        comparisons = [
            (f"observed_seed0_K{k}_S100_F16", f"observed_seed{s}_K{k}_S100_{p}")
            for s in (0, 1, 2)
            for p in ("U2", "R16", "F16")
            if (s, p) != (0, "F16")
        ] + [
            (f"permuted{n}_seed0_K{k}_S100_U2", f"permuted{n}_seed0_K{k}_S100_F16")
            for n in range(60000, 60005)
        ]
        for left, right in comparisons:
            assert (
                input_case[left][1]["development"]["rows"]
                == input_case[right][1]["development"]["rows"]
            )
            with np.load(
                run / "cases" / left / "numeric_records.npz", allow_pickle=False
            ) as a:
                with np.load(
                    run / "cases" / right / "numeric_records.npz", allow_pickle=False
                ) as b:
                    np.testing.assert_array_equal(
                        a["development_values"], b["development_values"]
                    )
            fixed_development_checks += 1
    fig = json.loads((run / "report/figure_provenance.json").read_text())
    assert len(fig) == 246
    for r in fig:
        assert sha(run / "report" / r["file"]) == r["sha256"]
    nb = json.loads((run / "population_grid.executed.ipynb").read_text())
    cells = [c for c in nb["cells"] if c["cell_type"] == "code"]
    assert [c["execution_count"] for c in cells] == list(range(1, 13))
    assert all(o["output_type"] != "error" for c in cells for o in c["outputs"])
    return dict(
        status="passed",
        new_fits=0,
        model_loads=0,
        receipt_sha256=receipt_hash,
        authenticated_files=len(receipt["files_sha256"]),
        cases=111,
        metric_confusion_records=checked_readouts,
        source_error_records=checked_errors,
        native_session_encoders=native_networks,
        exact_nested_array_comparisons=projections,
        common_source_policy_comparisons=policy_pairs,
        fixed_development_world_comparisons=fixed_development_checks,
        figures=len(fig),
        executed_cells=len(cells),
        actual_fit_counts=dict(counts),
        verifier_sha256=sha(Path(__file__)),
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--receipt-sha256", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    answer = verify(args.run.resolve(), args.receipt_sha256)
    with args.output.open("x") as h:
        json.dump(answer, h, indent=2)
    print(json.dumps(answer, indent=2))
