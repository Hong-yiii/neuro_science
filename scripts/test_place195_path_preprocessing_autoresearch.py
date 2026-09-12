from __future__ import annotations

import csv
import gzip
import json
import math
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

import numpy as np

from scripts import place195_path_preprocessing_autoresearch as pp
from scripts import verify_path_preprocessing_results as verifier


class PathPreprocessingExporterTest(unittest.TestCase):
    def test_relocated_cv_package_preserves_frozen_hash_checks(self) -> None:
        self.assertEqual(
            pp.MANAGER_ROOT,
            pp.REPO_ROOT / "outputs/path-autoresearch-management-20260908",
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manager = root / "manager"
            manager.mkdir()
            for name in (
                "prefit-selected-sources.json",
                "PROTOCOL-FROZEN-V1.md",
                "SELECTION-FROZEN.json",
            ):
                (manager / name).write_text("fixture")
            export = root / "export"
            export.mkdir()
            for name in ("source_tensors.npz", "export_manifest.json"):
                (export / name).write_text("fixture")
            snapshots = (
                pp.REPO_ROOT
                / "docs/reports/archive/path-preprocessing-20260908/code/gated-export-round1"
            )
            hashes = {
                key: pp.sha256_file(snapshots / f"{name}.txt")
                for key, name in (
                    ("driver", "place195_path_preprocessing_autoresearch.py"),
                    ("split_filtered_access", "place195_split_filtered_access.py"),
                    ("v7_v8_neural_helpers", "place195_v7_v8_neural_experiments.py"),
                )
            }
            for phase in ("round1", "round2"):
                directory = root / phase
                directory.mkdir()
                for suffix in (
                    "summary.json",
                    "cv_metrics.csv.gz",
                    "cv_predictions.csv.gz",
                    "model_replays.json.gz",
                    "source_lineage.json.gz",
                ):
                    (directory / f"{phase}_{suffix}").write_text("fixture")
                (directory / "command_start.json").write_text(
                    json.dumps({"runtime": {"code_hashes": hashes}})
                )
                (directory / "command_result.json").write_text("fixture")
            original = "/removed/exploratory-checkout/round1/round1_summary.json"
            freeze = {
                "input_hashes": {
                    original: pp.sha256_file(root / "round1/round1_summary.json")
                }
            }
            with patch.object(pp, "MANAGER_ROOT", manager):
                result = pp.package_observed_cv(
                    freeze,
                    root / "round2/round2_summary.json",
                    export / "source_tensors.npz",
                    root / "package",
                )
                self.assertEqual(result["new_fits"], 0)
                (root / "round1/round1_summary.json").write_text("corrupt")
                with self.assertRaisesRegex(
                    ValueError, "differs from selection freeze"
                ):
                    pp.package_observed_cv(
                        freeze,
                        root / "round2/round2_summary.json",
                        export / "source_tensors.npz",
                        root / "bad-package",
                    )

    def test_relocated_final_cli_checks_content_before_any_fit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            tensor, summary = root / "source_tensors.npz", root / "round2_summary.json"
            tensor.write_text("tensor fixture")
            summary.write_text("summary fixture")
            freeze = {
                "selected_candidate": {},
                "input_hashes": {
                    f"/removed/checkout/{path.name}": pp.sha256_file(path)
                    for path in (tensor, summary)
                },
            }
            (root / "SELECTION-FROZEN.json").write_text(json.dumps(freeze))
            args = pp.parse_args(
                [
                    "final-diagnostic",
                    "--source-tensor",
                    str(tensor),
                    "--round2-summary",
                    str(summary),
                    "--output-dir",
                    str(root / "out"),
                    "--authorized-phase",
                    pp.FINAL_REVIEW_GATE_TOKEN,
                ]
            )
            with (
                patch.object(pp, "MANAGER_ROOT", root),
                patch.object(pp, "load_source_tensor"),
                patch.object(
                    pp,
                    "_load_round2",
                    return_value={
                        "selected_family20_candidate": {},
                        "family20_summary_rows": [],
                    },
                ),
                patch.object(pp, "package_observed_cv", return_value={}),
                patch.object(
                    pp, "run_final_diagnostic", return_value={"new_fits": 0}
                ) as runner,
            ):
                self.assertEqual(pp.cmd_final(args), {"new_fits": 0})
                runner.assert_called_once()
                tensor.write_text("corrupt tensor")
                with self.assertRaisesRegex(
                    ValueError, "differs from pre-diagnostic selection freeze"
                ):
                    pp.cmd_final(args)
                runner.assert_called_once()

    def test_poisoned_test_and_unselected_rows_are_not_exported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            import_dir, split_dir, selected_path = _export_fixture(root)

            manifest = pp.export_binned_cue_counts(
                import_dir=import_dir,
                split_dir=split_dir,
                selected_sources_path=selected_path,
                output_dir=root / "out",
                authorized_phase=pp.REVIEW_GATE_TOKEN,
                strict_expected=False,
            )

            self.assertEqual(manifest["forbidden_rows_yielded"], 0)
            self.assertEqual(manifest["skipped_unselected_cell_rows"], 1)
            self.assertGreater(manifest["skipped_unselected_source_rows"], 0)
            with gzip.open(
                root / "out" / "development_binned_cue_counts.csv.gz",
                "rt",
                encoding="utf-8",
                newline="",
            ) as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(
                {r["source_trial_id"] for r in rows},
                {"train_trial", "validation_trial"},
            )
            self.assertNotIn("999999", json.dumps(rows))
            self.assertEqual(
                sum(
                    int(r["spike_count"])
                    for r in rows
                    if r["source_trial_id"] == "train_trial"
                ),
                3,
            )
            tail = {
                r["source_trial_id"]: int(r["tail_spike_count_1s_to_cue_end"])
                for r in rows
                if r["cue_bin_100ms"] == "0"
            }
            self.assertEqual(tail["train_trial"], 2)
            self.assertAlmostEqual(float(rows[0]["exposure_s"]), 0.1, places=6)

    def test_export_requires_integer_counts_and_gate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            import_dir, split_dir, selected_path = _export_fixture(
                root, selected_count="3.5"
            )
            with self.assertRaises(PermissionError):
                pp.export_binned_cue_counts(
                    import_dir=import_dir,
                    split_dir=split_dir,
                    selected_sources_path=selected_path,
                    output_dir=root / "out",
                    authorized_phase=None,
                )
            with self.assertRaisesRegex(ValueError, "nonnegative integer"):
                pp.export_binned_cue_counts(
                    import_dir=import_dir,
                    split_dir=split_dir,
                    selected_sources_path=selected_path,
                    output_dir=root / "out",
                    authorized_phase=pp.REVIEW_GATE_TOKEN,
                    strict_expected=False,
                )


class PathPreprocessingArrayTest(unittest.TestCase):
    def test_boundary_count_conservation_and_exact_q_weights(self) -> None:
        counts = np.arange(20, dtype=np.float32).reshape(1, 2, 10)
        exposure = np.full((1, 2, 10), 0.1, dtype=np.float32)
        for bins in (1, 2, 5, 10):
            agg, exp = pp.aggregate_temporal(counts, exposure, bins)
            self.assertEqual(agg.shape[-1], bins)
            np.testing.assert_allclose(agg.sum(axis=-1), counts.sum(axis=-1))
            np.testing.assert_allclose(exp.sum(axis=-1), 1.0)

        tensor = _tiny_tensor(
            mean_difference=0.0, sessions=2, train_per_label=3, validation_per_label=2
        )
        product = pp.build_product_rows(
            tensor, split="validation", max_combinations_per_class=None
        )
        self.assertEqual(product.support["absent"]["product_combinations"], 4)
        self.assertEqual(product.support["present"]["product_combinations"], 4)
        self.assertAlmostEqual(float(product.weights[product.y == 0].sum()), 0.5)
        self.assertAlmostEqual(float(product.weights[product.y == 1].sum()), 0.5)

    def test_missing_masks_refuse_zero_fill_and_source_blocks_stay_together(
        self,
    ) -> None:
        tensor = _tiny_tensor(
            mean_difference=1.0, sessions=2, train_per_label=3, validation_per_label=1
        )
        bad_x = tensor.X.copy()
        bad_e = tensor.E.copy()
        bad_m = tensor.M.copy()
        bad_m[0, -1] = False
        bad_x[0, -1, :] = 0.0
        bad_e[0, -1, :] = 0.0
        with self.assertRaisesRegex(ValueError, "not zero-filled"):
            pp._validate_masks_no_zero_fill(bad_x, bad_e, bad_m)

        plan = pp.make_draw_plan(
            tensor.records,
            split="train",
            rows_per_class=3,
            seed=0,
            fold_mode="train",
            fold=0,
        )
        rows = pp.materialize_plan(tensor, plan)
        by_pseudo = {}
        for entry in rows.manifest:
            by_pseudo.setdefault(entry["pseudo_row"], []).append(entry)
        for entries in by_pseudo.values():
            self.assertEqual(
                {e["session_id"] for e in entries}, {"syn0_session01", "syn1_session01"}
            )
            for entry in entries:
                self.assertIn("cell_ids", entry)
        train_sources = {e["source_trial_id"] for e in rows.manifest}
        eval_rows = pp.build_product_rows(
            tensor, split="train", fold_mode="validation", fold=0
        )
        eval_sources = {e["source_trial_id"] for e in eval_rows.manifest}
        self.assertTrue(train_sources.isdisjoint(eval_sources))

    def test_train_only_scaler_replay_and_replication_invariant_c(self) -> None:
        tensor = _tiny_tensor(
            mean_difference=4.0, sessions=2, train_per_label=4, validation_per_label=1
        )
        train = pp.materialize_plan(
            tensor,
            pp.make_draw_plan(tensor.records, split="train", rows_per_class=8, seed=1),
        )
        validation = pp.build_product_rows(
            tensor, split="validation", max_combinations_per_class=None
        )
        candidate = pp.Candidate(1, "raw_rate", "standard", 0.1)
        fit = pp.fit_candidate_model(train, candidate)
        scaler_mean = fit.scaler.mean.copy()
        scaler_scale = fit.scaler.scale.copy()
        prob = pp.predict_candidate(fit, validation)
        replay = pp.predict_from_replay(
            pp.model_replay_payload(fit), validation.X_counts, validation.E
        )
        np.testing.assert_allclose(prob, replay, atol=1e-12)
        np.testing.assert_allclose(fit.scaler.mean, scaler_mean)
        np.testing.assert_allclose(fit.scaler.scale, scaler_scale)

        doubled = pp.RowBundle(
            X_counts=np.concatenate([train.X_counts, train.X_counts], axis=0),
            E=np.concatenate([train.E, train.E], axis=0),
            y=np.concatenate([train.y, train.y], axis=0),
            weights=pp.exact_class_weights(np.concatenate([train.y, train.y], axis=0)),
            manifest=train.manifest + train.manifest,
            support=train.support,
        )
        fit2 = pp.fit_candidate_model(doubled, candidate)
        np.testing.assert_allclose(fit.model.coef_, fit2.model.coef_, atol=1e-6)
        np.testing.assert_allclose(
            fit.model.intercept_, fit2.model.intercept_, atol=1e-6
        )
        self.assertAlmostEqual(
            pp.average_loss_logistic_c(0.1, 10), pp.average_loss_logistic_c(0.1, 20) * 2
        )

    def test_null_counts_and_selection_replay(self) -> None:
        tensor = _tiny_tensor(
            mean_difference=2.0, sessions=2, train_per_label=3, validation_per_label=1
        )
        labels, audit = pp.make_label_permutation(tensor.records, seed=7)
        before = {}
        after = {}
        for rec in tensor.records:
            fold = rec.inner_fold if rec.split == "train" else -1
            key = (rec.session_id, rec.endpoint_pair, rec.split, fold)
            before[key] = before.get(key, 0) + (rec.label == "present")
            after[key] = after.get(key, 0) + (labels[rec.source_trial_id] == "present")
        self.assertEqual(before, after)
        self.assertEqual(audit["source_count"], len(tensor.records))

        family_rows, best, candidates = pp.select_family_for_world(
            tensor, rows_per_class=6, seed=0, shuffled_labels=labels
        )
        self.assertEqual(len(family_rows), 20)
        self.assertEqual(len(candidates), 20)
        self.assertIn(best["candidate_key"], {r["candidate_key"] for r in family_rows})


class PathPreprocessingSyntheticTest(unittest.TestCase):
    def test_positive_beats_no_signal_in_round1_and_round2(self) -> None:
        positive = _tiny_tensor(
            mean_difference=5.0, sessions=2, train_per_label=4, validation_per_label=2
        )
        no_signal = _tiny_tensor(
            mean_difference=0.0, sessions=2, train_per_label=4, validation_per_label=2
        )
        pos_r1 = pp.run_round1_cv(positive, rows_per_class=8)
        pos_r2 = pp.run_round2_adapt(positive, pos_r1, rows_per_class=8)
        null_r1 = pp.run_round1_cv(no_signal, rows_per_class=8)
        null_r2 = pp.run_round2_adapt(no_signal, null_r1, rows_per_class=8)
        self.assertEqual(pos_r1["candidate_count"], 18)
        self.assertEqual(len(pos_r2["family20_summary_rows"]), 20)
        self.assertGreater(
            pos_r2["selected_family20_candidate"]["primary_cv_delta_log_loss"],
            max(
                0.05,
                null_r2["selected_family20_candidate"]["primary_cv_delta_log_loss"],
            ),
        )


class PathPreprocessingReviewRegressionTest(unittest.TestCase):
    def test_cli_refuses_external_existing_and_symlink_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            owned = root / "owned"
            owned.mkdir()
            existing = owned / "accepted"
            existing.mkdir()
            (existing / "failure.json").write_text("preserve me")
            (owned / "link").symlink_to(root, target_is_directory=True)
            with patch.object(pp, "OWNED_OUTPUT_ROOT", owned):
                for path in (root / "external", existing, owned / "link" / "escaped"):
                    with self.assertRaises((ValueError, FileExistsError)):
                        pp.main(
                            [
                                "round1-cv",
                                "--source-tensor",
                                str(root / "missing.npz"),
                                "--output-dir",
                                str(path),
                            ]
                        )
                fresh = owned / "failed-new-attempt"
                with self.assertRaises(PermissionError):
                    pp.main(
                        [
                            "round1-cv",
                            "--source-tensor",
                            str(root / "missing.npz"),
                            "--output-dir",
                            str(fresh),
                        ]
                    )
            self.assertEqual((existing / "failure.json").read_text(), "preserve me")
            self.assertFalse((root / "external").exists())
            self.assertFalse((root / "escaped").exists())
            self.assertTrue((fresh / "command_start.json").is_file())
            self.assertTrue((fresh / "failure.json").is_file())
            receipt = pp.read_json(fresh / "command_start.json")
            self.assertIn("driver", receipt["runtime"]["code_hashes"])
            self.assertIn("scikit-learn", receipt["runtime"]["package_versions"])

    def test_frozen_allowlist_and_tensor_gate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bogus = root / "selected.json"
            bogus.write_text("[]")
            with self.assertRaisesRegex(ValueError, "SHA256 mismatch"):
                pp.load_selected_source_records(bogus, strict_expected=True)
            tensor = _tiny_tensor(
                mean_difference=0, sessions=2, train_per_label=3, validation_per_label=1
            )
            path = root / "synthetic.npz"
            pp.save_source_tensor(path, tensor)
            with self.assertRaises(ValueError):
                pp.load_source_tensor(path, strict_expected=True)
            self.assertEqual(
                len(pp.load_source_tensor(path).records), len(tensor.records)
            )

    def test_raw_metadata_mismatch_fails_before_export(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            imported, splits, selected = _export_fixture(root)
            access = pp.SplitFilteredAccess(imported, splits)
            rec = pp.load_selected_source_records(selected)[0]
            bad = pp._row_metadata_mismatches(
                {"split": "validation", "qc_flags": "bad"},
                rec,
                access=access,
                cell_id=rec.cell_ids[0],
                duration=1.2,
            )
            self.assertTrue(
                {"split", "row.qc_flags", "cue_duration_s"} <= {r["field"] for r in bad}
            )
            _write_csv(
                splits / "source_trial_splits.csv",
                [
                    {"source_trial_id": sid, "split": split}
                    for sid, split in (
                        ("train_trial", "validation"),
                        ("validation_trial", "validation"),
                        ("test_trial", "test"),
                        ("other_train", "train"),
                    )
                ],
                ["source_trial_id", "split"],
            )
            with self.assertRaisesRegex(ValueError, "metadata mismatch"):
                pp.export_binned_cue_counts(
                    import_dir=imported,
                    split_dir=splits,
                    selected_sources_path=selected,
                    output_dir=root / "out",
                    authorized_phase=pp.REVIEW_GATE_TOKEN,
                    strict_expected=False,
                )
            self.assertFalse((root / "out" / "source_tensors.npz").exists())
            self.assertTrue(
                (root / "out" / "accessor_metadata_mismatch_audit.json").is_file()
            )

    def test_cv_progress_and_historical_validation_independence(self) -> None:
        tensor = _tiny_tensor(
            mean_difference=1, sessions=2, train_per_label=3, validation_per_label=1
        )
        candidate = pp.Candidate(1, "raw_rate", "standard", 0.1)
        with tempfile.TemporaryDirectory() as tmp:
            log = Path(tmp) / "progress.jsonl"
            with patch.object(pp, "ACTIVE_PROGRESS_PATH", log):
                metrics, predictions, _, _ = pp.evaluate_candidate_cv(
                    tensor, candidate, rows_per_class=8
                )
            self.assertEqual(len(log.read_text().splitlines()), 3)
        self.assertTrue(all("train_metrics" in r and "converged" in r for r in metrics))
        changed = tensor.X.copy()
        for i, rec in enumerate(tensor.records):
            if rec.split == "validation":
                changed[i] += 10000
        _, predictions2, _, _ = pp.evaluate_candidate_cv(
            replace(tensor, X=changed), candidate, rows_per_class=8
        )
        self.assertEqual(predictions, predictions2)

    def test_nuisance_metadata_uses_exact_neural_draws_not_labels(self) -> None:
        tensor = _tiny_tensor(
            mean_difference=1, sessions=2, train_per_label=3, validation_per_label=1
        )
        plan = pp.make_draw_plan(
            tensor.records, split="train", rows_per_class=8, seed=0
        )
        rows = pp.materialize_plan(tensor, plan)
        features = pp.nuisance_features(rows, tensor.records)
        flipped_records = tuple(
            replace(r, label="absent" if r.label == "present" else "present")
            for r in tensor.records
        )
        np.testing.assert_equal(features, pp.nuisance_features(rows, flipped_records))
        lookup = {r.source_trial_id: r for r in tensor.records}
        sessions = sorted({r.session_id for r in tensor.records})
        for entry in rows.manifest:
            col = 2 * sessions.index(entry["session_id"])
            rec = lookup[entry["source_trial_id"]]
            np.testing.assert_equal(
                features[entry["pseudo_row"], col : col + 2],
                [rec.trial_index, rec.cue_duration_s],
            )

    def test_complete_synthetic_inference_replays_selection_and_metrics(self) -> None:
        tensor = pp.synthetic_tensor(mean_difference=1.0, seed=71, endpoints=("2->1",))
        first = pp.run_round1_cv(tensor, rows_per_class=8)
        second = pp.run_round2_adapt(tensor, first, rows_per_class=8)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = pp.run_final_diagnostic(
                tensor,
                second["family20_summary_rows"],
                second["selected_family20_candidate"],
                rows_per_class=8,
                ordinary_nulls=1,
                temporal_nulls=1,
                bootstraps=2,
                output_dir=root,
            )
            self.assertEqual(
                [r["seed"] for r in result["assembly_sensitivity"]], [1, 2]
            )
            self.assertTrue(
                all(not r["selection_allowed"] for r in result["assembly_sensitivity"])
            )
            self.assertEqual(len(result["nuisance_control"]["endpoint_metrics"]), 4)
            self.assertTrue(result["influence"]["leave_session_out"])
            self.assertEqual(
                result["selected_candidate"]["candidate_key"],
                second["selected_family20_candidate"]["candidate_key"],
            )
            for name in ("null_ordinary", "null_temporal_half"):
                world = root / name / "world-000"
                family = pp.read_json(world / "cv_family20.json")
                base = [r for r in family if r["lambda_l2"] == 0.1]
                best = pp.select_best_candidate(base)
                extras = [r for r in family if r["lambda_l2"] != 0.1]
                self.assertEqual(len(extras), 2)
                self.assertTrue(
                    all(
                        r["representation_key"] == best["representation_key"]
                        for r in extras
                    )
                )
                for prefix, summaries, metric in (
                    ("cv", family, "primary_cv_delta_log_loss"),
                    (
                        "validation",
                        pp.read_json(world / "validation_candidate_summaries.json"),
                        "diagnostic_validation_delta_log_loss",
                    ),
                ):
                    with gzip.open(world / f"{prefix}_predictions.csv.gz", "rt") as f:
                        rows = list(csv.DictReader(f))
                    values = {}
                    for row in rows:
                        key = (
                            row["candidate_key"],
                            row["endpoint_pair"],
                            row.get("fold", ""),
                        )
                        prob = min(1 - 1e-9, max(1e-9, float(row["prob_present"])))
                        term = -math.log(
                            prob if row["true_label"] == "present" else 1 - prob
                        )
                        values.setdefault(key, []).append((float(row["weight"]), term))
                    for summary in summaries:
                        losses = [
                            sum(w * loss for w, loss in terms)
                            / sum(w for w, _ in terms)
                            for key, terms in values.items()
                            if key[0] == summary["candidate_key"]
                        ]
                        self.assertAlmostEqual(
                            math.log(2) - sum(losses) / len(losses),
                            summary[metric],
                            places=10,
                        )
                self.assertTrue((world / "cv_models.json.gz").is_file())
                self.assertTrue((world / "validation_source_lineage.json.gz").is_file())
                labels = pp.read_json(world / "permutation.json")["labels"]
                with patch.object(
                    pp.LogisticRegression,
                    "fit",
                    side_effect=AssertionError("replay cannot fit"),
                ):
                    _, cv_models = verifier.replay(
                        world, "cv", tensor, labels, rows_per_class=8
                    )
                    _, validation_models = verifier.replay(
                        world, "validation", tensor, labels, rows_per_class=8
                    )
                self.assertEqual((cv_models, validation_models), (60, 20))
            self.assertTrue(
                (
                    root
                    / "source_bootstrap"
                    / "resample-001"
                    / "validation_predictions.csv.gz"
                ).is_file()
            )
            selected = result["selected_candidate"]["candidate_key"]
            with patch.object(
                pp.LogisticRegression,
                "fit",
                side_effect=AssertionError("verification cannot fit"),
            ):
                self.assertEqual(
                    verifier.check_bootstraps(
                        tensor, root, selected, count=2, rows_per_class=8
                    ),
                    2,
                )
                self.assertEqual(
                    verifier.check_nuisance(tensor, root, rows_per_class=8), 4
                )
                saved_summary = pp.read_json(root / "final_summary.json")
                altered = dict(saved_summary)
                altered["bootstrap_delta_quantiles"] = {
                    "q025": 99,
                    "q50": 99,
                    "q975": 99,
                }
                pp.write_json(root / "final_summary.json", altered)
                with self.assertRaises(AssertionError):
                    verifier.check_bootstraps(
                        tensor, root, selected, count=2, rows_per_class=8
                    )
                pp.write_json(root / "final_summary.json", saved_summary)
                audit_path = root / "source_bootstrap/resample-000/resampling.json"
                audit = pp.read_json(audit_path)
                pp.write_json(audit_path, {**audit, "seed": 1})
                with self.assertRaises(AssertionError):
                    verifier.check_bootstraps(
                        tensor, root, selected, count=2, rows_per_class=8
                    )
                pp.write_json(audit_path, audit)
                world = root / "null_ordinary/world-000"
                labels = pp.read_json(world / "permutation.json")["labels"]
                lineage_path = world / "validation_source_lineage.json.gz"
                lineage = pp.read_json(lineage_path)
                pp.write_json(lineage_path, [])
                with self.assertRaises(AssertionError):
                    verifier.replay(
                        world, "validation", tensor, labels, rows_per_class=8
                    )
                pp.write_json(lineage_path, lineage)
                metric_path = world / "validation_metrics.csv.gz"
                metrics = verifier.csv_rows(metric_path)
                metrics[0]["brier"] = "99"
                pp.write_csv(metric_path, metrics)
                with self.assertRaises(AssertionError):
                    verifier.replay(
                        world, "validation", tensor, labels, rows_per_class=8
                    )


def _tiny_tensor(
    *,
    mean_difference: float,
    sessions: int,
    train_per_label: int,
    validation_per_label: int,
) -> pp.SourceTensor:
    cells = tuple(f"syn{i}/session01/array/channel000/cell01" for i in range(sessions))
    records: list[pp.SourceRecord] = []
    x_rows: list[np.ndarray] = []
    e_rows: list[np.ndarray] = []
    m_rows: list[np.ndarray] = []
    for sess_i in range(sessions):
        session = f"syn{sess_i}_session01"
        for split, n in (
            ("train", train_per_label),
            ("validation", validation_per_label),
        ):
            for label in pp.LABELS:
                for j in range(n):
                    records.append(
                        pp.SourceRecord(
                            source_trial_id=f"{session}_{split}_{label}_{j}",
                            session_id=session,
                            split=split,
                            endpoint_pair="2->1",
                            label=label,
                            inner_fold=-1 if split == "validation" else j % 3,
                            trial_index=100 * sess_i
                            + j
                            + (1000 if split == "validation" else 0),
                            cue_duration_s=1.0,
                            cell_ids=(cells[sess_i],),
                        )
                    )
                    x = np.full((sessions, 10), np.nan, dtype=np.float32)
                    e = np.full((sessions, 10), np.nan, dtype=np.float32)
                    m = np.zeros(sessions, dtype=bool)
                    value = 1.0 + (mean_difference if label == "present" else 0.0)
                    x[sess_i, :] = value
                    e[sess_i, :] = 0.1
                    m[sess_i] = True
                    x_rows.append(x)
                    e_rows.append(e)
                    m_rows.append(m)
    return pp.SourceTensor(
        np.stack(x_rows),
        np.stack(e_rows),
        np.stack(m_rows),
        tuple(records),
        cells,
        {"fixture": "tiny"},
    )


def _export_fixture(
    root: Path, *, selected_count: str = "5"
) -> tuple[Path, Path, Path]:
    import_dir = root / "import"
    split_dir = root / "splits"
    import_dir.mkdir()
    split_dir.mkdir()
    cell = "syn0/session01/array/channel000/cell01"
    unselected_cell = "syn0/session01/array/channel999/cell99"
    records = [
        pp.SourceRecord(
            "train_trial",
            "syn0_session01",
            "train",
            "2->1",
            "present",
            0,
            1,
            1.1,
            (cell,),
        ),
        pp.SourceRecord(
            "validation_trial",
            "syn0_session01",
            "validation",
            "2->1",
            "absent",
            -1,
            2,
            1.0,
            (cell,),
        ),
    ]
    selected_path = root / "prefit-selected-sources.json"
    selected_path.write_text(
        json.dumps([pp.record_to_json(r) for r in records]), encoding="utf-8"
    )
    _write_csv(
        split_dir / "source_trial_splits.csv",
        [
            {"source_trial_id": "train_trial", "split": "train"},
            {"source_trial_id": "validation_trial", "split": "validation"},
            {"source_trial_id": "test_trial", "split": "test"},
            {"source_trial_id": "other_train", "split": "train"},
        ],
        ["source_trial_id", "split"],
    )
    (split_dir / "split_summary.json").write_text(
        json.dumps({"split_hash": "fixture"}), encoding="utf-8"
    )
    _write_gzip_csv(
        import_dir / "cue_spike_events.csv.gz",
        [
            *(
                {
                    "source_trial_id": "train_trial",
                    "cell_id": cell,
                    "cue_relative_time_s": str(t),
                }
                for t in (0.0, 0.1, 0.9999, 1.0, 1.05)
            ),
            {
                "source_trial_id": "validation_trial",
                "cell_id": cell,
                "cue_relative_time_s": "0.0",
            },
            {
                "source_trial_id": "test_trial",
                "cell_id": cell,
                "cue_relative_time_s": "999999",
            },
            {
                "source_trial_id": "other_train",
                "cell_id": cell,
                "cue_relative_time_s": "0.5",
            },
            {
                "source_trial_id": "train_trial",
                "cell_id": unselected_cell,
                "cue_relative_time_s": "0.2",
            },
        ],
        ["source_trial_id", "cell_id", "cue_relative_time_s"],
    )
    _write_gzip_csv(
        import_dir / "cue_counts.csv.gz",
        [
            {
                "source_trial_id": "train_trial",
                "cell_id": cell,
                "cue_spike_count": selected_count,
                "cue_window_start_ripple_s": "0",
                "cue_window_end_ripple_s": "1.1",
            },
            {
                "source_trial_id": "validation_trial",
                "cell_id": cell,
                "cue_spike_count": "1",
                "cue_window_start_ripple_s": "0",
                "cue_window_end_ripple_s": "1",
            },
            {
                "source_trial_id": "test_trial",
                "cell_id": cell,
                "cue_spike_count": "999999",
                "cue_window_start_ripple_s": "0",
                "cue_window_end_ripple_s": "1",
            },
            {
                "source_trial_id": "other_train",
                "cell_id": cell,
                "cue_spike_count": "1",
                "cue_window_start_ripple_s": "0",
                "cue_window_end_ripple_s": "1",
            },
            {
                "source_trial_id": "train_trial",
                "cell_id": unselected_cell,
                "cue_spike_count": "1",
                "cue_window_start_ripple_s": "0",
                "cue_window_end_ripple_s": "1",
            },
        ],
        [
            "source_trial_id",
            "cell_id",
            "cue_spike_count",
            "cue_window_start_ripple_s",
            "cue_window_end_ripple_s",
        ],
    )
    return import_dir, split_dir, selected_path


def _write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _write_gzip_csv(
    path: Path, rows: list[dict[str, str]], fieldnames: list[str]
) -> None:
    with gzip.open(path, "wt", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    unittest.main()
