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
from .. import run, study


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
            kernels = []

            def gate(*_):
                return dict(
                    conservative_budget_seconds=1,
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
                patch("nbclient.NotebookClient", InventedClient),
                patch(
                    "experiments.source_reuse_width_20261114.build_notebooks.make_notebook",
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


if __name__ == "__main__":
    unittest.main()
