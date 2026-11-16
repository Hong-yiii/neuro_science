"""No-fit regression of the complete two-notebook handoff with invented receipts."""

import json
import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import nbformat

from neuro.studies.population_models import frozen_models
from .. import study
from . import run


class HandoffTests(unittest.TestCase):
    def test_both_notebooks_get_fresh_immutable_specs_and_exact_bridge(self):
        with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ):
            root = Path(directory)
            out = root / "run"
            out.mkdir()
            args = SimpleNamespace(
                benchmark_receipt=root / "benchmark.json",
                preflight_receipt=root / "preflight.json",
                benchmark_sha256="invented-benchmark",
                preflight_sha256="invented-preflight",
            )
            for path in (
                args.benchmark_receipt,
                args.preflight_receipt,
                root / "rank-and-plan-checks.json",
            ):
                study.write_json(path, {"invented": True})
            config = study.configuration({})
            counts = config["expected_fit_counts"]
            equivalence_path = root / "equivalence.json"
            study.write_json(
                equivalence_path,
                dict(
                    status="passed", fit_counts={k: v // 24 for k, v in counts.items()}
                ),
            )
            kernels = []

            def gate(*_):
                return dict(
                    conservative_budget_seconds=1,
                    equivalence_sha256=study.sha(equivalence_path),
                    cases=48,
                    minimum_rank=17,
                    design_sha256=study.sha(run.ROOT / study.DESIGN_PATH),
                    rank_checks_sha256=study.sha(root / "rank-and-plan-checks.json"),
                )

            class InventedClient:
                def __init__(self, notebook, *, kernel_name, **kwargs):
                    self.notebook = notebook
                    self.name = kernel_name

                def execute(self):
                    part = ("reuse", "width")[len(kernels)]
                    path = out / "jupyter/kernels" / self.name / "kernel.json"
                    spec = json.loads(path.read_text())
                    if part == "reuse":
                        # The supplied bridge hash is created after notebook one.
                        assert "NEURO_BRIDGE_SHA256" not in spec["env"]
                        case = out / "cases/invented_B3"
                        case.mkdir(parents=True)
                        (case / "saved.txt").write_text("invented saved evidence")
                        (out / "aggregates_reuse").mkdir()
                    else:
                        assert spec["env"]["NEURO_BRIDGE_SHA256"] == study.sha(
                            out / "bridge-receipt.json"
                        )
                        bridge = json.loads((out / "bridge-receipt.json").read_text())
                        assert bridge["files_sha256"] == {
                            "cases/invented_B3/saved.txt": study.sha(
                                out / "cases/invented_B3/saved.txt"
                            )
                        }
                    assert all(study.sha(p) == digest for p, digest in kernels)
                    kernels.append((path, study.sha(path)))
                    study.write_json(
                        out / f"actual-fit-counts-{part}.json",
                        {
                            k: v // 3 * (2 if part == "reuse" else 1)
                            for k, v in counts.items()
                        },
                    )
                    self.notebook.cells[0].execution_count = 1
                    return self.notebook

            def notebook(_):
                return nbformat.v4.new_notebook(
                    cells=[nbformat.v4.new_code_cell("# invented; never executed")]
                )

            with (
                frozen_models(),
                patch.dict(os.environ, {"NEURO_BRIDGE_SHA256": ""}),
                patch.object(run, "validate_gate", side_effect=gate),
                patch.object(run, "code_hashes", return_value={}),
                patch.object(run, "gate_contract", return_value={}),
                patch("nbclient.NotebookClient", InventedClient),
                patch(
                    "experiments.source_reuse_width_20261114.walkthrough_20261115.build_notebooks.make_notebook",
                    side_effect=notebook,
                ),
            ):
                os.environ.pop("NEURO_BRIDGE_SHA256", None)
                run.execute(out, config, args)
            self.assertEqual(len(kernels), 2)
            self.assertEqual(len({p for p, _ in kernels}), 2)
            self.assertTrue(all(study.sha(p) == digest for p, digest in kernels))
            self.assertEqual(
                json.loads((out / "actual-fit-counts.json").read_text()), counts
            )
            self.assertEqual(len(list(out.glob("*.executed.ipynb"))), 2)


class ScheduleTests(unittest.TestCase):
    def test_staged_first_case_exactly_once_and_remaining_grid(self):
        from .execution import PartExecution
        from . import execution
        from ..test_study import fixture

        data, meta, design = fixture()
        config = study.configuration(design)
        called = []
        per_case = {k: v // 48 for k, v in config["expected_fit_counts"].items()}

        class Counting:
            def __init__(self, **kwargs):
                self.counts = {k: 0 for k in per_case}

            def start(self):
                return self

            def stop(self):
                return dict(self.counts)

        def result(case):
            # Fabricated software results only; no data/model inference.
            return {
                **{
                    k: [{"case": case["id"], "invented": True}]
                    for k in (
                        "source_usage",
                        "pool_usage",
                        "source_errors",
                        "class_errors",
                        "overlap",
                        "metrics",
                        "confusions",
                        "learning",
                    )
                },
                "trajectories": {"case": case["id"], "invented": True},
                "fit_counts": per_case,
            }

        class Staged:
            def __init__(self, case, *args, **kwargs):
                self.case = case

            def finish(self):
                called.append(("staged", self.case["id"]))
                for k, v in per_case.items():
                    active.accounting.counts[k] += v
                return result(self.case)

        def train(case, *args, **kwargs):
            called.append(("remaining", case["id"]))
            for k, v in per_case.items():
                active.accounting.counts[k] += v
            return result(case)

        with (
            tempfile.TemporaryDirectory() as directory,
            frozen_models(),
            patch.object(study, "GridFitAccounting", Counting),
            patch.object(execution, "StagedCase", Staged),
            patch.object(study, "train_case", side_effect=train),
        ):
            for part, first, count in [
                ("reuse", "observed_seed0_B2", 32),
                ("width", "observed_seed0_Wmid", 16),
            ]:
                plans = study.paired_plans(data, meta, design, seed=0)
                active = PartExecution(data, meta, config, Path(directory), part)
                active.begin(plans)
                active.finish_remaining()
                selected = called[-count:]
                self.assertEqual(selected[0], ("staged", first))
                self.assertEqual(len(selected), count)
                self.assertEqual(len(set(c for _, c in selected)), count)
                self.assertEqual(
                    active.actual, {k: v * count for k, v in per_case.items()}
                )
        self.assertEqual({c for _, c in called}, {c["id"] for c in study.schedule()})
        self.assertEqual(sum(c.endswith("_B3") for _, c in called), 8)

    def test_failed_staged_cell_records_actual_counts_and_refuses_retry(self):
        from .execution import PartExecution
        from ..test_study import fixture

        data, meta, design = fixture()
        with tempfile.TemporaryDirectory() as directory, frozen_models():
            active = PartExecution(
                data, meta, study.configuration(design), Path(directory), "reuse"
            )
            plans = study.paired_plans(data, meta, design, seed=0)
            active.begin(plans)
            with self.assertRaisesRegex(RuntimeError, "invented failure"):
                with active.stage("invented interruption"):
                    raise RuntimeError("invented failure")
            failure = json.loads((Path(directory) / "failure_reuse.json").read_text())
            self.assertEqual(failure["attempts"][0]["status"], "failed")
            self.assertTrue(all(v == 0 for v in failure["actual_fit_counts"].values()))
            with self.assertRaisesRegex(ValueError, "no retry"):
                with active.stage("should reject"):
                    pass


if __name__ == "__main__":
    unittest.main()
