#!/usr/bin/env python3
"""Issue #6: bounded exploratory matched PCA/raw comparison, never original-test data."""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import replace
import datetime as dt
import json
from pathlib import Path
import shutil
import sys
import time
import traceback
import warnings

import numpy as np
from sklearn.exceptions import ConvergenceWarning

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from scripts import place195_path_preprocessing_autoresearch as pp  # noqa: E402

TENSOR_HASH = "6fa3e836fad756b6007f69115de5e6758c7238cfb9a786b4a4e7a0d4ac849e3a"
LAMBDAS = (0.01, 0.1, 1.0)
ARMS = ("raw", "pca")
TIE_ATOL = 1e-12
PROTOCOL = "docs/reports/path-pca-matched/protocol.md"
CODE_FILES = (
    "scripts/place195_path_preprocessing_autoresearch.py",
    "scripts/place195_matched_pca.py",
    "scripts/verify_matched_pca.py",
    "scripts/test_matched_pca.py",
    "scripts/place195_split_filtered_access.py",
    "scripts/place195_v7_v8_neural_experiments.py",
    "scripts/verify_path_preprocessing_results.py",
    PROTOCOL,
)


def candidates():
    return [
        pp.Candidate(1, "raw_rate", "variance_floor", lam, projection)
        for projection in ("none", "pca90")
        for lam in LAMBDAS
    ]


def arm(row):
    return "pca" if row.get("projection", "none") == "pca90" else "raw"


def select(rows):
    selected = {}
    for name in ARMS:
        group = [r for r in rows if arm(r) == name]
        if sorted(float(r["lambda_l2"]) for r in group) != list(LAMBDAS):
            raise ValueError(
                "selection requires exactly three declared recipes per arm"
            )
        best = min(float(r["mean_cv_log_loss"]) for r in group)
        chosen = max(
            (r for r in group if float(r["mean_cv_log_loss"]) <= best + TIE_ATOL),
            key=lambda r: float(r["lambda_l2"]),
        )
        selected[name] = chosen["candidate_key"]
    return selected


def selected_recipes(selected):
    by_key = {c.key: c for c in candidates()}
    return [by_key[selected[name]] for name in ARMS]


def audit_inputs(source: Path, manifest: Path):
    if pp.sha256_file(source) != TENSOR_HASH:
        raise ValueError("not the accepted source tensor")
    tensor = pp.load_source_tensor(
        source, strict_expected=True, selected_sources_path=manifest
    )
    pools = Counter(
        (r.session_id, r.endpoint_pair, r.split, r.label) for r in tensor.records
    )
    audit = {
        "status": "fixed-assay-input-gate-passed",
        "source_sha256": pp.sha256_file(source),
        "selected_sources_sha256": pp.sha256_file(manifest),
        "export_manifest_sha256": pp.sha256_file(
            source.parent / "export_manifest.json"
        ),
        "shape": list(tensor.X.shape),
        "observed_pairs": int(tensor.M.sum()),
        "support": pp.support_summary(tensor.records),
        "validation_pools": sum(k[2] == "validation" for k in pools),
        "validation_singletons": sum(
            k[2] == "validation" and n == 1 for k, n in pools.items()
        ),
        "cue_duration_range_s": [
            min(r.cue_duration_s for r in tensor.records),
            max(r.cue_duration_s for r in tensor.records),
        ],
        "simultaneity_status_counts": dict(
            Counter(r.simultaneity_status for r in tensor.records)
        ),
        "qc_flags_counts": dict(Counter(r.qc_flags for r in tensor.records)),
        "unresolved": [
            "lab confirmation of cue/goal/start marker semantics",
            "verified simultaneity",
            "gaze/view/heading/action and admissible previous-trial history",
            "serial exchangeability",
            "anatomical/selection provenance and animal replication",
        ],
        "claim_ceiling": "exposed historical, known-label condition-level pseudopopulation method comparison",
    }
    return tensor, audit


def code_hashes():
    return {name: pp.sha256_file(ROOT / name) for name in CODE_FILES}


def reduced_tensor(tensor, session):
    indices = [i for i, r in enumerate(tensor.records) if r.session_id != session]
    return replace(
        tensor,
        X=tensor.X[indices],
        E=tensor.E[indices],
        M=tensor.M[indices],
        records=tuple(tensor.records[i] for i in indices),
    )


def fit_budget(tensor, nulls, bootstraps):
    endpoints = {r.endpoint_pair for r in tensor.records}
    session_fits = sum(
        2 * len({r.endpoint_pair for r in tensor.records if r.session_id != session})
        for session in {r.session_id for r in tensor.records}
    )
    return {
        "observed": 24 * len(endpoints),
        "null": 2 * nulls * 24 * len(endpoints),
        "bootstrap": bootstraps * 2 * len(endpoints),
        "assembly": 4 * len(endpoints),
        "session": session_fits,
    }


def run_cv(tensor, directory, *, rows_per_class, labels=None):
    metrics, predictions, models, lineage = [], [], [], []
    for candidate in candidates():
        m, p, f, source_lineage = pp.evaluate_candidate_cv(
            tensor,
            candidate,
            rows_per_class=rows_per_class,
            seed=0,
            shuffled_labels=labels,
        )
        for model in f:
            model["cell_ids"] = list(
                pp.subset_tensor(tensor, model["endpoint_pair"]).cell_ids
            )
        metrics.extend(m)
        predictions.extend(p)
        models.extend(f)
        lineage.extend(source_lineage)
    if not all(r["converged"] for r in metrics):
        raise RuntimeError("nonconverged CV fit")
    pp.write_csv(directory / "cv_metrics.csv.gz", metrics)
    pp.write_csv(directory / "cv_predictions.csv.gz", predictions)
    pp.write_json(directory / "cv_models.json.gz", models)
    pp.write_json(directory / "cv_source_lineage.json.gz", lineage)
    summary = pp.summarize_cv_metrics(metrics)
    pp.write_json(directory / "cv_summary.json", summary)
    selected = select(summary)
    # This file is closed before any new historical evaluation in this world.
    pp.write_json(
        directory / "selection.json",
        {
            "selected": selected,
            "cv_sha256": pp.sha256_file(directory / "cv_summary.json"),
        },
    )
    return selected


def run_validation(tensor, directory, recipes, *, rows_per_class, labels=None, seed=0):
    metrics, _, _ = pp.train_evaluate_validation(
        tensor,
        recipes,
        rows_per_class=rows_per_class,
        seed=seed,
        shuffled_labels=labels,
        artifact_dir=directory,
    )
    if not all(r["converged"] for r in metrics):
        raise RuntimeError("nonconverged validation fit")
    summary = pp.aggregate_validation_rows(metrics)
    pp.write_json(directory / "validation_summary.json", summary)
    return summary


def paired(summary, selected):
    by_key = {r["candidate_key"]: r for r in summary}
    rows = {name: by_key[selected[name]] for name in ARMS}
    ep = {name: rows[name]["endpoint_delta_log_loss"] for name in ARMS}
    if ep["raw"].keys() != ep["pca"].keys():
        raise ValueError("unpaired endpoint support")
    deltas = {name: rows[name]["diagnostic_validation_delta_log_loss"] for name in ARMS}
    return {
        "baseline_deltas": deltas,
        "raw_loss_minus_pca_loss": deltas["pca"] - deltas["raw"],
        "endpoint_difference": {k: ep["pca"][k] - ep["raw"][k] for k in ep["raw"]},
    }


def tail_reference(observed, values):
    return (1 + sum(v >= observed - TIE_ATOL for v in values)) / (len(values) + 1)


def anchor_check(directory, historical):
    from scripts import verify_path_preprocessing_results as vr

    anchor = candidates()[2].key
    current = vr.prediction_groups(directory / "validation_predictions.csv.gz")
    previous = vr.prediction_groups(
        historical / "observed/validation_predictions.csv.gz"
    )
    maximum = 0.0
    for key, rows in current.items():
        if key[0] != anchor:
            continue
        old = previous[key]
        if len(rows) != len(old):
            raise ValueError("anchor row count mismatch")
        for field in ("true_label", "weight", "validation_row"):
            if [r[field] for r in rows] != [r[field] for r in old]:
                raise ValueError(f"anchor {field} mismatch")
        a, b = (
            [float(r["prob_present"]) for r in rows],
            [float(r["prob_present"]) for r in old],
        )
        np.testing.assert_allclose(a, b, rtol=1e-9, atol=1e-10)
        maximum = max(maximum, float(np.max(np.abs(np.asarray(a) - b))))
    summary = next(
        r
        for r in pp.read_json(directory / "validation_summary.json")
        if r["candidate_key"] == anchor
    )
    np.testing.assert_allclose(
        summary["diagnostic_validation_delta_log_loss"],
        0.028583397042444624,
        rtol=0,
        atol=1e-10,
    )
    return {
        "status": "passed",
        "maximum_probability_difference": maximum,
        "probability_rtol": 1e-9,
        "probability_atol": 1e-10,
        "historical_predictions_sha256": pp.sha256_file(
            historical / "observed/validation_predictions.csv.gz"
        ),
    }


def summarize_run(
    directory, selected, nulls, bootstraps, seed_results, session_results
):
    observed = paired(
        pp.read_json(directory / "observed/validation_summary.json"), selected
    )
    references = {}
    for kind, worlds in nulls.items():
        references[kind] = {
            name: {
                "selected": tail_reference(
                    observed["baseline_deltas"][name],
                    [w["pair"]["baseline_deltas"][name] for w in worlds],
                ),
                "max_six": tail_reference(
                    observed["baseline_deltas"][name],
                    [w["max_six_delta"] for w in worlds],
                ),
            }
            for name in ARMS
        }
    sensitivity = {
        name: pp.quantiles([b["baseline_deltas"][name] for b in bootstraps])
        for name in ARMS
    }
    sensitivity["paired_difference"] = pp.quantiles(
        [b["raw_loss_minus_pca_loss"] for b in bootstraps]
    )
    differences = observed["endpoint_difference"]
    leave_endpoint = {
        ep: float(np.mean([v for k, v in differences.items() if k != ep]))
        for ep in differences
        if len(differences) > 1
    }
    return {
        "schema_version": 1,
        "status": "complete",
        "analysis": "exploratory",
        "selected": selected,
        "observed": observed,
        "null_references": references,
        "bootstrap_fixed_selection_sensitivity": sensitivity,
        "assembly_seeds": seed_results,
        "leave_endpoint_out_difference": leave_endpoint,
        "leave_session_out": session_results,
        "null_counts": {k: len(v) for k, v in nulls.items()},
        "bootstrap_count": len(bootstraps),
        "warning": "No matched-risk superiority p-value or confirmatory confidence interval; no H1/H1b/H2 or absence/equivalence claim.",
    }


def execute(
    tensor,
    output,
    *,
    rows_per_class=128,
    null_count=100,
    bootstrap_count=200,
    historical=None,
    max_seconds=7200,
):
    started, initial_fits = time.monotonic(), pp.FIT_COUNT
    budget = fit_budget(tensor, null_count, bootstrap_count)
    pp.write_json(output / "fit-budget.json", budget)
    pp.ACTIVE_PROGRESS_PATH = output / "fits.jsonl"

    def checkpoint():
        if time.monotonic() - started > max_seconds:
            raise TimeoutError(
                "frozen execution budget exhausted; retain incomplete attempt"
            )
        if (
            sum(p.stat().st_size for p in output.rglob("*") if p.is_file())
            > 10 * 1024**3
        ):
            raise RuntimeError("frozen 10GiB artifact budget exhausted")

    selected = run_cv(tensor, output / "observed", rows_per_class=rows_per_class)
    pp.write_json(
        output / "SELECTION-FROZEN.json",
        {
            "selected": selected,
            "frozen_at": dt.datetime.now(dt.timezone.utc).isoformat(),
            "selection_sha256": pp.sha256_file(output / "observed/selection.json"),
        },
    )
    observed = run_validation(
        tensor, output / "observed", candidates(), rows_per_class=rows_per_class
    )
    if historical is not None:
        pp.write_json(
            output / "anchor.json", anchor_check(output / "observed", historical)
        )
    fixed = selected_recipes(selected)
    nulls = {}
    for kind, seed0 in (("ordinary", 50_000), ("temporal_half", 70_000)):
        worlds = []
        for index in range(null_count):
            checkpoint()
            directory = output / f"null_{kind}" / f"world-{index:03d}"
            labels, audit = pp.make_label_permutation(
                tensor.records,
                seed=seed0 + index,
                temporal_half=kind == "temporal_half",
            )
            movement = sum(labels[r.source_trial_id] != r.label for r in tensor.records)
            pp.write_json(
                directory / "permutation.json", {"labels": labels, "audit": audit}
            )
            chosen = run_cv(
                tensor, directory, rows_per_class=rows_per_class, labels=labels
            )
            summary = run_validation(
                tensor,
                directory,
                candidates(),
                rows_per_class=rows_per_class,
                labels=labels,
            )
            worlds.append(
                {
                    "index": index,
                    "seed": seed0 + index,
                    "selected": chosen,
                    "pair": paired(summary, chosen),
                    "max_six_delta": max(
                        r["diagnostic_validation_delta_log_loss"] for r in summary
                    ),
                    "changed_labels": movement,
                    "source_count": len(tensor.records),
                    "pure_strata": sum(len(s["counts"]) == 1 for s in audit["strata"]),
                    "pure_sources": sum(
                        s["n"] for s in audit["strata"] if len(s["counts"]) == 1
                    ),
                }
            )
            pp.write_json(directory / "world.json", worlds[-1])
        nulls[kind] = worlds
    bootstrap = []
    for index in range(bootstrap_count):
        checkpoint()
        directory = output / "bootstrap" / f"resample-{index:03d}"
        records, audit = pp._bootstrap_records(tensor.records, seed=90_000 + index)
        pp.write_json(directory / "resampling.json", audit)
        bt = pp.bootstrap_tensor(tensor, records)
        summary = run_validation(bt, directory, fixed, rows_per_class=rows_per_class)
        bootstrap.append(paired(summary, selected))
    seeds = {}
    for seed in (1, 2):
        checkpoint()
        summary = run_validation(
            tensor,
            output / "assembly" / f"seed-{seed}",
            fixed,
            rows_per_class=rows_per_class,
            seed=seed,
        )
        seeds[str(seed)] = paired(summary, selected)
    sessions = []
    base = paired(observed, selected)["endpoint_difference"]
    for session in sorted({r.session_id for r in tensor.records}):
        checkpoint()
        reduced = reduced_tensor(tensor, session)
        if not reduced.records:
            continue
        summary = run_validation(
            reduced, output / "session" / session, fixed, rows_per_class=rows_per_class
        )
        pair = paired(summary, selected)
        common = pair["endpoint_difference"]
        sessions.append(
            {
                "omitted_session": session,
                "pair": pair,
                "dropped_endpoints": sorted(set(base) - set(common)),
                "original_common_difference": float(np.mean([base[k] for k in common])),
            }
        )
    summary = summarize_run(output, selected, nulls, bootstrap, seeds, sessions)
    summary.update(
        {
            "fit_count": pp.FIT_COUNT - initial_fits,
            "rows_per_class": rows_per_class,
            "elapsed_seconds": time.monotonic() - started,
        }
    )
    if summary["fit_count"] != sum(budget.values()):
        raise RuntimeError("fit accounting mismatch")
    checkpoint()
    pp.write_json(output / "nulls.json", nulls)
    pp.write_json(output / "bootstrap.json", bootstrap)
    pp.write_json(output / "summary.json", summary)
    pp.ACTIVE_PROGRESS_PATH = None
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=("audit", "synthetic", "run"))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--source", type=Path)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--historical", type=Path)
    parser.add_argument("--review-gate", type=Path)
    args = parser.parse_args()
    owned = ROOT / "outputs/path-pca-matched"
    output = args.output.resolve()
    if not output.is_relative_to(owned.resolve()) or output == owned.resolve():
        raise ValueError(f"output must be a fresh child of {owned}")
    if output.exists():
        raise FileExistsError(output)
    output.mkdir(parents=True)
    try:
        if args.stage == "synthetic":
            tensor, audit = (
                pp.synthetic_tensor(mean_difference=6, seed=314),
                {"status": "invented-data-only"},
            )
        else:
            if args.source is None or args.manifest is None:
                raise ValueError("source and manifest required")
            tensor, audit = audit_inputs(args.source, args.manifest)
        pp.write_json(output / "input-audit.json", audit)
        if args.stage == "audit":
            print(json.dumps(audit, indent=2))
            return
        hashes = code_hashes()
        if args.stage == "run":
            if args.review_gate is None or args.historical is None:
                raise ValueError("review gate and historical anchor required")
            gate = pp.read_json(args.review_gate)
            if (
                gate["status"] != "approved-for-bounded-exploratory-fit"
                or gate["code_hashes"] != hashes
            ):
                raise PermissionError("missing or stale independent prefit review gate")
            pp.write_json(output / "review-gate.json", gate)
        for name in CODE_FILES:
            destination = output / "code" / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, destination)
        pp.save_source_tensor(output / "tensor.npz", tensor)
        pp.write_json(
            output / "start.json",
            {
                "stage": args.stage,
                "code_hashes": hashes,
                "runtime": pp.runtime_manifest(sys.argv),
                "source": str(args.source),
                "manifest": str(args.manifest),
                "historical": str(args.historical),
            },
        )
        with warnings.catch_warnings(), (output / "console.log").open("x") as log:
            from contextlib import redirect_stdout, redirect_stderr

            warnings.simplefilter("error", ConvergenceWarning)
            with redirect_stdout(log), redirect_stderr(log):
                result = execute(
                    tensor,
                    output,
                    rows_per_class=16 if args.stage == "synthetic" else 128,
                    null_count=2 if args.stage == "synthetic" else 100,
                    bootstrap_count=2 if args.stage == "synthetic" else 200,
                    historical=args.historical if args.stage == "run" else None,
                )
        pp.write_json(
            output / "artifact-hashes.json",
            {
                str(p.relative_to(output)): pp.sha256_file(p)
                for p in sorted(output.rglob("*"))
                if p.is_file()
            },
        )
        print(
            json.dumps(
                {
                    "status": "complete",
                    "output": str(output),
                    "fits": result["fit_count"],
                }
            )
        )
    except Exception:
        pp.write_json(
            output / "FAILED.json",
            {
                "status": "incomplete",
                "traceback": traceback.format_exc(),
                "fit_count": pp.FIT_COUNT,
            },
        )
        raise


if __name__ == "__main__":
    main()
