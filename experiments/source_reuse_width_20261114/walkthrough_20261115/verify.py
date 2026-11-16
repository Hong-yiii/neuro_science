"""Full numeric audit plus notebook-stage and authenticated reproduction checks."""

from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np
from neuro.studies.population_models import frozen_models
from .. import study
from ..audit.verify import verify as full_verify
from ..audit.deliver import control_summaries
from ..audit.tables import compare_table
from .build_notebooks import make_notebook

NAMES = {"reuse": "source_reuse_20261115", "width": "population_width_20261115"}
ACCEPTED_RECEIPT = "bd057c05a842a702d6d8c3fd2259ee4e54918fb3b49951b57f782b08e876c17b"


def verify(run, receipt_hash, previous):
    result = full_verify(
        run, receipt_hash, notebook_factory=make_notebook, notebook_names=NAMES
    )
    run, previous = Path(run), Path(previous)
    assert study.sha(previous / "receipt.json") == ACCEPTED_RECEIPT
    accepted = json.loads((previous / "receipt.json").read_text())
    assert accepted["status"] == "completed"
    for path, digest in accepted["files_sha256"].items():
        target = (previous / path).resolve()
        assert target.is_relative_to(previous.resolve()) and study.sha(target) == digest
    exact_arrays = continuous_arrays = 0
    maximum_difference = 0.0
    for case in study.schedule():
        left = previous / "cases" / case["id"]
        right = run / "cases" / case["id"]
        for filename in (
            "case.json",
            "train_lineage.json",
            "development_lineage.json",
            "metrics.json",
            "confusions.json",
            "trajectories.json",
        ):
            assert json.loads((left / filename).read_text()) == json.loads(
                (right / filename).read_text()
            ), (case["id"], filename)
        with (
            np.load(left / "numeric_records.npz", allow_pickle=False) as a,
            np.load(right / "numeric_records.npz", allow_pickle=False) as b,
        ):
            assert a.files == b.files
            for key in a.files:
                if key.endswith(("_truth", "_prediction")) or key.endswith("_values"):
                    np.testing.assert_array_equal(a[key], b[key])
                    exact_arrays += 1
                else:
                    np.testing.assert_allclose(a[key], b[key], rtol=1e-7, atol=1e-7)
                    maximum_difference = max(
                        maximum_difference, float(np.max(np.abs(a[key] - b[key])))
                    )
                    continuous_arrays += 1
    for part in NAMES:
        stages = sorted(run.glob("stage-" + part + "-*.json"))
        assert len(stages) == 9
        records = [json.loads(p.read_text()) for p in stages]
        assert all(r["completed"] for r in records)
        assert records[-1]["actual_fit_counts"] == json.loads(
            (run / ("actual-fit-counts-" + part + ".json")).read_text()
        )
        assert records[0]["attempts"][0]["id"] == (
            "observed_seed0_B2" if part == "reuse" else "observed_seed0_Wmid"
        )
        scores, contrasts = control_summaries(run, part)
        compare_table(
            run / ("walkthrough_" + part) / "score_control_summary.csv",
            scores,
            ("arm", "encoder", "decoder", "head"),
        )
        compare_table(
            run / ("walkthrough_" + part) / "contrast_summary.csv",
            contrasts,
            ("before", "after", "encoder", "decoder", "head"),
        )
    result["reproduction_comparison"] = dict(
        accepted_receipt_sha256=ACCEPTED_RECEIPT,
        accepted_files_authenticated=len(accepted["files_sha256"]),
        cases=48,
        exact_arrays=exact_arrays,
        continuous_arrays=continuous_arrays,
        maximum_continuous_difference=maximum_difference,
        stage_checkpoints=18,
        conclusion="same recorded data and seeds; no added biological replication",
    )
    return result


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--run", type=Path, required=True)
    p.add_argument("--receipt-sha256", required=True)
    p.add_argument("--previous", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    with frozen_models():
        result = verify(args.run, args.receipt_sha256, args.previous)
    study.write_json(args.output, result)
    print(json.dumps(result, indent=2))
