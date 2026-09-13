#!/usr/bin/env python3
"""Verify this study's frozen outputs and recompute the exact inclusive BA null test.

No fitting or raw/importer access. Fractions avoid treating equal BA values as
unequal merely because their floating-point reductions differed.
"""

import argparse
import collections
import csv
import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path


def csv_rows(path):
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def check(run_root):
    b = run_root / "track_b"
    summary = json.loads((b / "summary.json").read_text())
    assert summary["status"] == "complete"
    assert summary["fit_count"] == summary["expected_fit_count"] == 342
    files = sorted((b / "fits").glob("*/fit_info.json"))
    assert len(files) == 342
    observed, nulls = {}, collections.defaultdict(dict)
    updates, hashed = 0, 0
    for file in files:
        info = json.loads(file.read_text())
        spec = info["fit_spec"]
        assert info["device"] == "cuda" and info["peak_allocated_bytes"] > 0
        assert info["save_load_max_abs_embedding_diff"] == 0
        for name, digest in info["artifact_sha256"].items():
            assert (
                hashlib.sha256((file.parent / name).read_bytes()).hexdigest() == digest
            )
            hashed += 1
        losses = csv_rows(file.parent / "loss_trace.csv")
        assert [int(r["step"]) for r in losses] == list(range(1, spec["updates"] + 1))
        assert all(math.isfinite(float(r["total"])) for r in losses)
        updates += len(losses)
        predictions = [
            r
            for r in csv_rows(file.parent / "predictions.csv")
            if r["split"] == "validation_exact_q"
        ]
        count = collections.Counter(r["true_label"] for r in predictions)
        assert count == {"absent": 24, "present": 6}
        correct = collections.Counter(
            r["true_label"] for r in predictions if r["true_label"] == r["pred_label"]
        )
        ba = Fraction(correct["absent"], 48) + Fraction(correct["present"], 12)
        for row in predictions:
            assert (
                abs(float(row["evaluation_weight"]) - 0.5 / count[row["true_label"]])
                < 1e-14
            )
            assert row["pred_label"] == (
                "present" if float(row["prob_present"]) >= 0.5 else "absent"
            )
        stored = next(
            r["balanced_accuracy"]
            for r in info["metrics"]
            if r["split"] == "validation_exact_q"
        )
        assert abs(float(ba) - stored) < 1e-12
        train_ids = {
            r["source_trial_id"]
            for r in csv_rows(file.parent / "generated_assembly_manifest.csv")
            if r["split"] == "train"
        }
        val_ids = {
            r["source_trial_id"]
            for r in csv_rows(file.parent / "exact_evaluation_manifest.csv")
        }
        assert train_ids.isdisjoint(val_ids) and len(val_ids) == 22
        key = tuple(
            spec[k]
            for k in (
                "objective",
                "dim",
                "rows_per_class",
                "updates",
                "assembly_seed",
                "optimizer_seed",
            )
        )
        if spec["permutation_index"] is None:
            if spec["assembly_seed"] == spec["optimizer_seed"] == 0:
                assert key not in observed
                observed[key] = ba
        else:
            index = spec["permutation_index"]
            assert key not in nulls[index]
            nulls[index][key] = ba
    assert updates == 510000
    assert len(observed) == 14 and set(nulls) == set(range(20))
    assert all(set(values) == set(observed) for values in nulls.values())
    observed_max = max(observed.values())
    null_maxima = {i: max(values.values()) for i, values in nulls.items()}
    exceedances = sum(value >= observed_max for value in null_maxima.values())
    pvalue = Fraction(exceedances + 1, len(nulls) + 1)
    prefix = csv_rows(b / "track_b_prefix_parity.csv")
    assert len(prefix) == 42
    assert all(
        int(r["prefix_steps_compared"]) == 1000
        and float(r["weight_prefix_max_abs_diff"]) == 0
        and float(r["loss_prefix_max_abs_diff"]) == 0
        for r in prefix
    )
    exact_audit = json.loads((run_root / "audits/track_b_exact_audit.json").read_text())
    assert str(pvalue) == exact_audit["family_max_pvalue_exact"]
    assert exceedances == exact_audit["exceedances_including_exact_ties"]
    assert all(
        str(value) == exact_audit["null_maxima_exact"][str(i)]
        for i, value in null_maxima.items()
    )
    for family in ("session_endpoint_split", "session_endpoint_split_temporal_half"):
        c_summary = json.loads((run_root / "track_c/summary.json").read_text())
        all_nulls = csv_rows(run_root / "track_c/track_c_joint_target_null_metrics.csv")
        values = [r for r in all_nulls if r["null_family"] == family]
        assert len(values) == 400
        assert all(
            r["eligible_signature_matches_observed"] == "True"
            and int(r["middle_implies_anywhere_violations"]) == 0
            for r in values
        )
        for target, receipt in c_summary["pvalues"][family].items():
            scores = [
                float(r["equal_session_mean_delta_log_loss"])
                for r in values
                if r["target_mode"] == target
            ]
            assert len(scores) == 100
            count_ge = sum(v >= receipt["observed"] for v in scores)
            assert count_ge == receipt["exceedances"]
            assert abs((count_ge + 1) / 101 - receipt["p_value"]) < 1e-14
    return {
        "status": "verified",
        "fits": len(files),
        "updates": updates,
        "hashed_artifacts": hashed,
        "numeric_prefix_pairs": len(prefix),
        "exact_observed_family_max": str(observed_max),
        "inclusive_exceedances": exceedances,
        "exact_family_p": str(pvalue),
        "family_p": float(pvalue),
        "new_fits": 0,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_root", type=Path)
    args = parser.parse_args()
    print(json.dumps(check(args.run_root), indent=2))


if __name__ == "__main__":
    main()
