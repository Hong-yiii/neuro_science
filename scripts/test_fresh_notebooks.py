"""Invented six-ledger adapter, timing regression and fresh-artifact checks."""

from __future__ import annotations

import copy
import csv
import gzip
import hashlib
import json
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

import numpy as np

from neuro.notebook_artifacts import (
    ArtifactStore,
    FitAccounting,
    no_fitting,
    verify_artifacts,
)
from neuro.notebook_inputs import (
    demo_configuration,
    effective_pair_map,
    inspect_inputs,
    load_inputs,
)
from neuro.notebook_support import checked_assemblies, fit_logistic, source_budget
from neuro.pca_lda import fit_pca, fit_standardizer
from neuro.place195 import file_hash, reconstruct_neural, select_metadata
from neuro.pseudopopulation import materialize, sample_plan


def write_table(path, rows):
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "wt", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def invented_ledgers(root):
    landmarks = [1, 2, 3]
    trials, units, outer, inner = [], [], [], []
    current = []
    for block in ("invented-A", "invented-B", "invented-C"):
        for i in range(3):
            units.append(
                {
                    "session_id": block,
                    "cell_id": f"{block}/unit{i}",
                    "selection_provenance": "place_selective_195_snapshot",
                }
            )
        order = 0
        for start in landmarks:
            for goal in landmarks:
                if start == goal:
                    continue
                for _ in range(8):
                    previous = f"{block}/trial{order:03d}"
                    for digit, predecessor in ((start, ""), (goal, previous)):
                        sid = f"{block}/trial{order:03d}"
                        rows = {
                            "source_trial_id": sid,
                            "session_id": block,
                            "trial_index": str(order),
                            "previous_source_trial_id": predecessor,
                            "outcome": "success",
                            "qc_flags": "",
                            "ripple_cue_duration_s": "1.2",
                            "marker_minor_digit": str(digit),
                            "inferred_start_id_from_previous_marker": f"marker_{start}",
                            "inferred_goal_id": f"marker_{digit}",
                        }
                        for key in ("ripple_codes", "unity_codes", "eyelink_codes"):
                            rows[key] = " ".join(
                                str(base + digit) for base in (10, 20, 30)
                            )
                        trials.append(rows)
                        outer.append(
                            {
                                "source_trial_id": sid,
                                "session_id": block,
                                "trial_index": str(order),
                                "previous_source_trial_id": predecessor,
                                "split": "train",
                            }
                        )
                        if predecessor:
                            current.append(
                                {
                                    "source_trial_id": sid,
                                    "session_id": block,
                                    "label": f"{start}->{goal}",
                                    "original_split": "train",
                                }
                            )
                        order += 1
    rng = np.random.default_rng(20260907)
    for block in ("invented-A", "invented-B", "invented-C"):
        for start in landmarks:
            for goal in landmarks:
                if start == goal:
                    continue
                pool = sorted(
                    [
                        row
                        for row in current
                        if row["session_id"] == block
                        and row["label"] == f"{start}->{goal}"
                    ],
                    key=lambda r: r["source_trial_id"],
                )
                for i, index in enumerate(rng.permutation(len(pool))):
                    inner.append(
                        {
                            **pool[int(index)],
                            "split": "validation" if i < 2 else "train",
                        }
                    )
    # Poisoned outer-test metadata/neural payload must never be numerically interpreted.
    outsider = {
        **trials[0],
        "source_trial_id": "invented-outer-test",
        "marker_minor_digit": "POISON",
        "ripple_cue_duration_s": "POISON",
    }
    trials.append(outsider)
    outer.append(
        {**outer[0], "source_trial_id": "invented-outer-test", "split": "test"}
    )
    counts, events = [], []
    by_id = {r["source_trial_id"]: r for r in trials}
    for source in current:
        row = by_id[source["source_trial_id"]]
        for u, unit in enumerate(
            [u for u in units if u["session_id"] == row["session_id"]]
        ):
            start = 100 + 2 * int(row["trial_index"])
            base = {
                key: row[key]
                for key in ("source_trial_id", "session_id", "trial_index")
            }
            base["cell_id"] = unit["cell_id"]
            ts = [0.05, 0.15, 1.1] if u else []
            counts.append(
                {
                    **base,
                    "cue_spike_count": str(len(ts)),
                    "cue_window_start_ripple_s": str(start),
                    "cue_window_end_ripple_s": str(start + 1.2),
                }
            )
            for t in ts:
                events.append(
                    {
                        **base,
                        "cue_relative_time_s": str(t),
                        "spike_time_ripple_s": str(start + t),
                    }
                )
    counts.append(
        {
            **counts[0],
            "source_trial_id": "invented-outer-test",
            "cue_spike_count": "POISON",
            "cue_window_start_ripple_s": "POISON",
            "cue_window_end_ripple_s": "POISON",
        }
    )
    events.append(
        {
            **events[0],
            "source_trial_id": "invented-outer-test",
            "cue_relative_time_s": "POISON",
            "spike_time_ripple_s": "POISON",
        }
    )
    tables = {
        "trials": trials,
        "units": units,
        "outer_splits": outer,
        "inner_splits": inner,
        "counts": counts,
        "events": events,
    }
    paths = {
        key: root / (key + (".csv.gz" if key in {"counts", "events"} else ".csv"))
        for key in tables
    }
    for key, rows in tables.items():
        write_table(paths[key], rows)
    manifest = {
        "mode": "place195",
        "landmarks": landmarks,
        "inner_split_seed": 20260907,
        "bin_width_s": 0.1,
        "nominal_s": 1.0,
        "inputs": {
            k: {"path": str(p), "sha256": file_hash(p)} for k, p in paths.items()
        },
    }
    return manifest, tables, paths


class AdapterTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.manifest, self.tables, self.paths = invented_ledgers(self.root)

    def tearDown(self):
        self.temporary.cleanup()

    def rewrite(self, key):
        write_table(self.paths[key], self.tables[key])
        self.manifest["inputs"][key]["sha256"] = file_hash(self.paths[key])

    def test_metadata_reproduction_and_poisoned_numeric_gate(self):
        selection = select_metadata(self.manifest)
        self.assertEqual(selection.audit["eligible"], 144)
        self.assertEqual(selection.audit["selected_train"], 108)
        self.assertEqual(selection.audit["selected_development"], 36)
        self.assertEqual(selection.audit["selected_units"], 9)
        with self.assertRaises(PermissionError):
            reconstruct_neural(selection)
        data, audit = reconstruct_neural(selection, interpret_neural=True)
        self.assertEqual(audit["counts_rejected"], 1)
        self.assertEqual(audit["events_rejected"], 1)
        self.assertEqual(audit["tail_spikes"], 288)
        self.assertEqual(data.values.shape, (144, 9, 10))
        self.assertTrue(np.isnan(data.values[~data.observed]).all())
        self.assertEqual(data.dependency_audit()["overlapping_contributor_ids"], [])

    def test_mutated_and_forged_selection_rejected_before_numeric(self):
        selection = select_metadata(self.manifest)
        selection.selected[0]["condition"] = (
            "2->1" if selection.selected[0]["condition"] != "2->1" else "1->2"
        )
        with (
            patch(
                "neuro.place195._finite",
                side_effect=AssertionError(
                    "numeric interpretation before selection check"
                ),
            ),
            self.assertRaisesRegex(ValueError, "changed or was forged"),
        ):
            reconstruct_neural(selection, interpret_neural=True)
        canonical = select_metadata(self.manifest)
        altered = copy.deepcopy(canonical.selected)
        altered[0]["split_id"] = "development"
        with (
            patch(
                "neuro.place195._finite",
                side_effect=AssertionError(
                    "numeric interpretation before selection check"
                ),
            ),
            self.assertRaisesRegex(ValueError, "changed or was forged"),
        ):
            reconstruct_neural(
                replace(canonical, selected=altered), interpret_neural=True
            )

    def test_bad_eligibility_linkage_and_frozen_assignment(self):
        row = next(r for r in self.tables["trials"] if r["previous_source_trial_id"])
        row["trial_index"] = str(int(row["trial_index"]) + 2)
        outer = next(
            r
            for r in self.tables["outer_splits"]
            if r["source_trial_id"] == row["source_trial_id"]
        )
        outer["trial_index"] = row["trial_index"]
        self.rewrite("trials")
        self.rewrite("outer_splits")
        with self.assertRaisesRegex(ValueError, "linkage"):
            select_metadata(self.manifest)

    def test_inner_assignment_mismatch(self):
        self.tables["inner_splits"][0]["split"] = (
            "train"
            if self.tables["inner_splits"][0]["split"] == "validation"
            else "validation"
        )
        self.rewrite("inner_splits")
        with self.assertRaisesRegex(ValueError, "frozen assignment"):
            select_metadata(self.manifest)

    def test_duplicates_missing_joins_conservation_and_window_errors(self):
        mutations = (
            "duplicate",
            "missing",
            "count",
            "short",
            "window",
            "wrongunit",
            "duplicate-event",
        )
        for mutation in mutations:
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as td:
                manifest, tables, paths = invented_ledgers(Path(td))
                if mutation == "duplicate":
                    tables["counts"].append(dict(tables["counts"][0]))
                elif mutation == "missing":
                    tables["counts"].pop(0)
                elif mutation == "count":
                    tables["counts"][0]["cue_spike_count"] = "999"
                elif mutation == "short":
                    tables["counts"][0]["cue_window_end_ripple_s"] = str(
                        float(tables["counts"][0]["cue_window_start_ripple_s"]) + 0.5
                    )
                elif mutation == "window":
                    tables["counts"][1]["cue_window_start_ripple_s"] = str(
                        float(tables["counts"][1]["cue_window_start_ripple_s"]) + 0.001
                    )
                elif mutation == "wrongunit":
                    tables["counts"][0]["cell_id"] = "invented-B/unit0"
                    tables["counts"][0]["cue_spike_count"] = "POISON"
                else:
                    tables["events"].append(dict(tables["events"][0]))
                for key in ("counts", "events"):
                    write_table(paths[key], tables[key])
                    manifest["inputs"][key]["sha256"] = file_hash(paths[key])
                selection = select_metadata(manifest)
                if mutation == "wrongunit":
                    with (
                        patch(
                            "neuro.place195._finite",
                            side_effect=AssertionError(
                                "numeric parsing before wrong-unit gate"
                            ),
                        ),
                        self.assertRaisesRegex(ValueError, "wrong-block unit identity"),
                    ):
                        reconstruct_neural(selection, interpret_neural=True)
                else:
                    with self.assertRaises(ValueError):
                        reconstruct_neural(selection, interpret_neural=True)


class TimingAndArtifactTests(unittest.TestCase):
    def test_unsigned_descending_and_complex_timing_rejected(self):
        data, _ = load_inputs(inspect_inputs(demo_configuration()))
        for change in (
            {"bin_edges": np.array([0, 2, 1, 3, 4], dtype=np.uint8)},
            {"bin_edges": data.bin_edges.astype(complex)},
            {"exposure": data.exposure.astype(complex)},
            {"exposure": data.exposure.astype(str)},
        ):
            with self.subTest(change=list(change)), self.assertRaises(ValueError):
                replace(data, **change)

    def test_nested_effective_source_budgets_and_fixed_development(self):
        config = demo_configuration()
        data, _ = load_inputs(inspect_inputs(config))
        effective = effective_pair_map(data, permutation_seed=50000)
        observed = {t.source_id: t.condition for t in data.targets}
        self.assertNotEqual(effective, observed)
        dev_plan = sample_plan(
            data,
            split_id="development",
            rows_per_condition=4,
            seed=0,
            effective_conditions=effective,
        )
        reference = materialize(data, dev_plan)
        selected, reduced = source_budget(
            data, effective, reduced=True, subset_seed=20261023
        )
        train, dev = checked_assemblies(
            selected, reduced, dev_plan, reference, config=config["execution"], seed=1
        )
        self.assertEqual(dev.plan, reference.plan)
        self.assertTrue({s.source_id for s in selected.sources} <= set(effective))
        self.assertEqual(len(train.plan.rows), 48)
        self.assertEqual({t.source_id: t.condition for t in data.targets}, observed)

    def test_loaded_model_replay_authentication_and_no_fit_guard(self):
        config = demo_configuration()
        data, _ = load_inputs(inspect_inputs(config))
        train = materialize(
            data, sample_plan(data, split_id="train", rows_per_condition=8, seed=0)
        )
        dev = materialize(
            data,
            sample_plan(data, split_id="development", rows_per_condition=4, seed=0),
        )
        with tempfile.TemporaryDirectory() as td:
            store = ArtifactStore(Path(td) / "artifacts")
            accounting = FitAccounting().start()
            encoder = fit_pca(train.values, n_components=8)
            train_x, dev_x = (
                encoder.transform(train.values),
                encoder.transform(dev.values),
            )
            model = fit_logistic(train_x, train.targets, C=0.01, max_iter=2000)
            store.save_bundle("pair", train, dev)
            store.save_encoder("pca", encoder, kind="pca")
            store.readout(
                "readout",
                model,
                encoder="pca",
                bundle="pair",
                head="pair",
                train_features=train_x,
                development_features=dev_x,
            )
            counts = accounting.stop()
            identity = store.finish(
                fit_counts=counts,
                expected_counts={
                    "pca": 1,
                    "logistic": 1,
                    "lda": 0,
                    "cebra": 0,
                    "optimizer_updates": 0,
                },
            )
            self.assertEqual(
                verify_artifacts(store.root, expected_manifest_hash=identity)[
                    "readout_splits_checked"
                ],
                2,
            )
            with no_fitting(), self.assertRaisesRegex(RuntimeError, "forbids fitting"):
                fit_standardizer(train.values)
            path = store.root / "readout_model.joblib"
            path.write_bytes(b"tampered")
            with (
                patch(
                    "joblib.load",
                    side_effect=AssertionError("unauthenticated pickle load"),
                ),
                self.assertRaisesRegex(ValueError, "hash mismatch"),
            ):
                verify_artifacts(store.root, expected_manifest_hash=identity)

    def test_known_signal_and_constant_logistic_controls(self):
        from neuro.evaluation import classification_metrics

        y = np.tile(["a", "b", "c"], 20)
        signal = np.eye(3)[np.tile(np.arange(3), 20)]
        for features, expected in ((signal, 1.0), (np.zeros_like(signal), 1 / 3)):
            model = fit_logistic(features, y, C=0.01, max_iter=2000)
            result = classification_metrics(
                y,
                model.predict(features),
                classes=model.classes_,
                probabilities=model.predict_proba(features),
            )
            self.assertAlmostEqual(result["balanced_accuracy"], expected)

    def test_kernel_code_identity_drift_rejected(self):
        from neuro.notebook_artifacts import (
            runtime_identity,
            stable_kernel_identity,
            validate_kernel_identity,
        )

        config = demo_configuration()
        config["expected_kernel_identity"] = stable_kernel_identity(runtime_identity())
        validate_kernel_identity(config)
        config["expected_kernel_identity"]["neuro_module_sha256"]["source_data.py"] = (
            "changed"
        )
        with self.assertRaisesRegex(
            ValueError, "kernel interpreter/dependencies/package code"
        ):
            validate_kernel_identity(config)

    def test_final_exit_zero_output_over_budget_is_rejected(self):
        import sys
        from types import SimpleNamespace

        from scripts import execute_fresh_notebooks as executor

        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "fresh"
            args = SimpleNamespace(
                output=root,
                timeout_seconds=10,
                memory_gib=6,
                manifest=None,
                manifest_sha256=None,
                allow_biological=False,
                output_limit_bytes=2048,
                runtime_python=Path(sys.executable),
                notebook_directory=Path("notebooks"),
                notebooks=["01_pseudopopulation"],
                dependency_path=[],
            )

            def exited_worker(*args, **kwargs):
                (root / "late-success-write.bin").write_bytes(b"x" * 4096)
                return SimpleNamespace(pid=0, poll=lambda: 0, returncode=0)

            with (
                patch.object(executor, "probe_kernel_identity", return_value={}),
                patch.object(executor.subprocess, "Popen", side_effect=exited_worker),
                self.assertRaisesRegex(RuntimeError, "final output/deadline budget"),
            ):
                executor.execute(args)
            self.assertTrue((root / "failure.json").is_file())
            self.assertFalse((root / "resources.json").exists())
            self.assertEqual(
                executor.expected_fit_counts(["01_pseudopopulation", "02_pca_lda"], 20),
                {
                    "pca": 4,
                    "logistic": 24,
                    "lda": 12,
                    "cebra": 0,
                    "optimizer_updates": 0,
                },
            )

    def test_notebooks_expose_calls_and_have_no_private_default_paths(self):
        root = Path(__file__).resolve().parents[1]
        for name in ("01_pseudopopulation", "02_pca_lda", "03_cebra"):
            notebook = json.loads((root / "notebooks" / (name + ".ipynb")).read_text())
            source = "\n".join("".join(c["source"]) for c in notebook["cells"])
            self.assertIn("inspect_inputs(configuration)", source)
            self.assertIn("load_inputs(inspection)", source)
            self.assertNotIn("/home/", source)
            self.assertNotIn("outputs/start-goal", source)
            self.assertNotIn("run_everything", source)
            codes = [c for c in notebook["cells"] if c["cell_type"] == "code"]
            if name == "01_pseudopopulation":
                self.assertIn(
                    "whole_notebook_no_fitting.__enter__()", "".join(codes[0]["source"])
                )
            else:
                self.assertNotIn("whole_notebook_no_fitting", source)
            evidence = notebook["metadata"].get("fresh_demo_execution")
            if evidence is None:
                self.assertTrue(
                    all(
                        c["execution_count"] is None and not c["outputs"] for c in codes
                    )
                )
            else:
                self.assertEqual(
                    [c["execution_count"] for c in codes],
                    list(range(1, len(codes) + 1)),
                )
                self.assertEqual(
                    evidence["code_sha256"],
                    hashlib.sha256(
                        "\n".join("".join(c["source"]) for c in codes).encode()
                    ).hexdigest(),
                )
                self.assertEqual(
                    evidence["fit_blocked_loaded_model_replay"],
                    "fit-blocked-loaded-model-replay-passed",
                )
            public = json.dumps([c["outputs"] for c in codes])
            self.assertNotIn("/home/", public)
            self.assertNotIn("invented/block", public)
            self.assertTrue(
                all(o["output_type"] != "error" for c in codes for o in c["outputs"])
            )


if __name__ == "__main__":
    unittest.main()
