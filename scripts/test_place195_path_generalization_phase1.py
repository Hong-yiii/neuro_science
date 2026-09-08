from __future__ import annotations

import csv
import gzip
import json
import tempfile
import unittest
from pathlib import Path

import numpy as np

from scripts.place195_path_generalization_phase1 import (
    AUTH_TOKEN,
    PRIMARY_COMPONENT,
    SUPPORTED_MIDDLE_COMPONENT,
    TRACK_C_FAMILY_MAX_TARGET,
    ProductMoments,
    RidgeModel,
    analytic_gaussian_linear_metrics,
    balanced_mixture_moments,
    cebra_config_manifest,
    coherent_joint_target_shuffle,
    component_label_from_trial_mapping_row,
    convolve_linear_scores,
    exact_validation_product,
    expected_spurious_between_class_trace,
    export_development_cue_counts,
    fit_endpoint_penalized_logistic,
    fit_ridge_from_moments,
    fit_track_c_three_target_family,
    normalized_logistic_c,
    pooled_time_cell_moments,
    predict_endpoint_penalized_logistic,
    product_conditional_moments,
    ridge_score_to_probability,
    run_track_a_row_grid,
    rotation_invariance_check,
    route_signature_tokens,
    selected_cell_scope_hash,
    validate_accepted_root,
    eligible_contexts_train_only,
    weighted_binary_metrics,
)
from scripts.place195_v7_v8_neural_experiments import SourceMeta


class Phase1ProductDiagnosticsTest(unittest.TestCase):
    def test_exact_validation_weights_are_class_balanced_not_row_balanced(self) -> None:
        X, M, metas, cells = _product_fixture(
            absent_counts=(2, 3, 4), present_counts=(1, 2, 3)
        )
        Xv, yv, weights, _manifest, support = exact_validation_product(
            X, M, metas, cells
        )
        self.assertEqual(Xv.shape[0], 30)
        self.assertEqual(int(np.sum(yv == 0)), 24)
        self.assertEqual(int(np.sum(yv == 1)), 6)
        self.assertEqual(
            support["absent"], {"s0_session01": 2, "s1_session01": 3, "s2_session01": 4}
        )
        self.assertAlmostEqual(float(weights[yv == 0][0]), 0.5 / 24)
        self.assertAlmostEqual(float(weights[yv == 1][0]), 0.5 / 6)
        self.assertAlmostEqual(float(np.sum(weights[yv == 0])), 0.5)
        self.assertAlmostEqual(float(np.sum(weights[yv == 1])), 0.5)

    def test_product_moments_match_tiny_exhaustive_rows_and_mixture_term(self) -> None:
        X, M, metas, cells = _product_fixture(
            absent_counts=(2, 2), present_counts=(2, 2), split="train"
        )
        absent = product_conditional_moments(
            X, M, metas, cells, split="train", label="absent"
        )
        present = product_conditional_moments(
            X, M, metas, cells, split="train", label="present"
        )
        for label, moments in (("absent", absent), ("present", present)):
            rows, _y, _w, _manifest, _support = exact_validation_product(
                _copy_split(X, metas, split="validation"),
                M,
                _copy_metas_split(metas, split="validation"),
                cells,
            )
            # Exact product rows above contain both labels; make a direct class subset using the fixture values.
            class_rows = (
                rows[_y == (1 if label == "present" else 0)]
                .reshape(-1, X.shape[1] * X.shape[2])
                .astype(float)
            )
            np.testing.assert_allclose(moments.mean, class_rows.mean(axis=0))
            centered = class_rows - class_rows.mean(axis=0)
            np.testing.assert_allclose(
                moments.covariance, centered.T @ centered / len(class_rows), atol=1e-7
            )
        mix_mean, mix_cov = balanced_mixture_moments(absent, present)
        stacked = []
        weights = []
        for label in ("absent", "present"):
            rows, _manifest, _support = _enumerate_label_from_fixture(
                X, M, metas, cells, label=label
            )
            flat = rows.reshape(rows.shape[0], -1).astype(float)
            stacked.append(flat)
            weights.extend([0.5 / len(flat)] * len(flat))
        all_rows = np.vstack(stacked)
        weights_arr = np.asarray(weights)
        empirical_mean = weights_arr @ all_rows
        centered = all_rows - empirical_mean
        empirical_cov = (centered.T * weights_arr) @ centered
        np.testing.assert_allclose(mix_mean, empirical_mean)
        np.testing.assert_allclose(mix_cov, empirical_cov, atol=1e-7)

    def test_pooled_time_cell_moments_include_time_and_class_mean_covariance(
        self,
    ) -> None:
        cells = ["s0/session01/array/channel000/cell01"]
        metas = [
            SourceMeta("a0", "s0_session01", "train", "absent"),
            SourceMeta("p0", "s0_session01", "train", "present"),
        ]
        X = np.asarray([[[0.0, 2.0]], [[4.0, 6.0]]], dtype=np.float32)
        M = np.ones((2, 1), dtype=bool)
        mean, cov, info = pooled_time_cell_moments(X, M, metas, cells, split="train")
        self.assertAlmostEqual(float(mean[0]), 3.0)
        self.assertAlmostEqual(float(cov[0, 0]), 5.0)
        self.assertEqual(info["class_weight"], 0.5)

    def test_linear_score_convolution_matches_materialized_product(self) -> None:
        X, M, metas, cells = _product_fixture(
            absent_counts=(2, 3), present_counts=(2, 3), split="validation"
        )
        rng = np.random.default_rng(3)
        model = RidgeModel(rng.normal(size=X.shape[1] * X.shape[2]), 0.25, 1.0)
        rows, _manifest, _support = _enumerate_label_from_fixture(
            X, M, metas, cells, label="present"
        )
        materialized = (
            rows.reshape(rows.shape[0], -1) @ model.coefficients + model.intercept
        )
        convolved = convolve_linear_scores(
            X, M, metas, cells, model, split="validation", label="present"
        )
        np.testing.assert_allclose(np.sort(materialized), np.sort(convolved))

    def test_ridge_controls_positive_and_true_null(self) -> None:
        absent = ProductMoments(
            "train", "absent", ("s",), np.array([-0.5, -0.5]), np.eye(2), {"s": 30}
        )
        present = ProductMoments(
            "train", "present", ("s",), np.array([0.5, 0.5]), np.eye(2), {"s": 30}
        )
        model = fit_ridge_from_moments(absent, present, lambda_l2=1.0)
        self.assertGreater(
            analytic_gaussian_linear_metrics(model, np.array([1.0, 1.0]))[
                "true_balanced_accuracy"
            ],
            0.6,
        )
        null_model = RidgeModel(np.array([1.0, -2.0]), 0.7, 1.0)
        self.assertAlmostEqual(
            analytic_gaussian_linear_metrics(null_model, np.zeros(2))[
                "true_balanced_accuracy"
            ],
            0.5,
        )

    def test_ridge_score_probability_link_for_plus_minus_one_targets(self) -> None:
        got = ridge_score_to_probability(np.array([-2.0, -1.0, 0.0, 1.0, 2.0]), eps=1e-6)
        np.testing.assert_allclose(got, [1e-6, 1e-6, 0.5, 1 - 1e-6, 1 - 1e-6])

    def test_sampled_ridge_moment_arm_is_emitted(self) -> None:
        X, M, metas, cells, _delta, _sessions = _small_train_validation_fixture()
        Xv, yv, wv, manifest, _support = exact_validation_product(X, M, metas, cells)
        source_index = {m.source_trial_id: i for i, m in enumerate(metas)}
        rows, _preds = run_track_a_row_grid(
            Xsrc=X,
            Msrc=M,
            metas=metas,
            source_index=source_index,
            cells=cells,
            Xval=Xv,
            yval=yv,
            wval=wv,
            val_manifest=manifest,
            rows_per_class_grid=[4],
            seeds=[0],
            pca_dims=[],
        )
        self.assertTrue(any(r["stage"] == "finite_sample_ridge_convergence" for r in rows))

    def test_expected_spurious_between_class_trace_formula(self) -> None:
        got = expected_spurious_between_class_trace(
            np.array([2.0, 3.0, 4.0]),
            ["a", "a", "b"],
            {"a": 2, "b": 4},
            {"a": 8, "b": 4},
        )
        expected = (
            4 * (1 / 2 + 1 / 8) / 4 + 9 * (1 / 2 + 1 / 8) / 4 + 16 * (1 / 4 + 1 / 4) / 4
        )
        self.assertAlmostEqual(got, expected)


class Phase1ModelAndTargetTest(unittest.TestCase):
    def test_normalized_logistic_c(self) -> None:
        self.assertEqual(normalized_logistic_c(64), 1.0)
        self.assertEqual(normalized_logistic_c(256), 0.25)
        self.assertEqual(normalized_logistic_c(1024), 0.0625)

    def test_weighted_metrics_handle_one_class_auc_as_none(self) -> None:
        out = weighted_binary_metrics(np.zeros(3, dtype=int), np.array([0.1, 0.2, 0.3]))
        self.assertIsNone(out["auroc"])
        self.assertIsNone(out["balanced_accuracy"])

    def test_context_eligibility_counts_unique_sources(self) -> None:
        rows = [
            {"split": "train", "endpoint_pair": "A->B", "y": 0, "source_trial_id": "a0"},
            {"split": "train", "endpoint_pair": "A->B", "y": 0, "source_trial_id": "a0"},
            {"split": "train", "endpoint_pair": "A->B", "y": 1, "source_trial_id": "p0"},
            {"split": "train", "endpoint_pair": "A->B", "y": 1, "source_trial_id": "p1"},
        ]
        self.assertEqual(eligible_contexts_train_only(rows, min_per_class=2), set())

    def test_endpoint_intercepts_are_not_penalized(self) -> None:
        endpoint = ["A", "A", "A", "A", "B", "B", "B", "B"]
        y = np.array([1, 1, 1, 0, 1, 0, 0, 0])
        slopes = np.zeros((len(y), 1))
        model = fit_endpoint_penalized_logistic(y, endpoint, slopes, penalty=1e6)
        prob, unseen = predict_endpoint_penalized_logistic(
            model, ["A", "B"], np.zeros((2, 1))
        )
        self.assertFalse(unseen.any())
        np.testing.assert_allclose(prob, [0.75, 0.25], atol=1e-5)

    def test_rotation_invariance_control_uses_no_second_scaler(self) -> None:
        check = rotation_invariance_check(0)
        self.assertEqual(check["status"], "pass")
        self.assertLess(check["max_abs_probability_diff"], 1e-6)

    def test_cebra_config_counts_and_caveats(self) -> None:
        manifest = cebra_config_manifest()
        self.assertEqual(manifest["observed_fit_count"], 62)
        self.assertEqual(manifest["null_family_config_count"], 14)
        self.assertIn("29->32->32->16->output_dim", manifest["architecture_caveat"])
        self.assertIn("not a full-dimensional", manifest["architecture_caveat"])

    def test_target_semantics_middle_vs_anywhere(self) -> None:
        row = {
            "middle_directed_components": "OTHER_EDGE",
            "route_signature": f"{PRIMARY_COMPONENT}>OTHER_EDGE",
            "complete_directed_path_coverage": "true",
            "absence_labels_allowed": "true",
        }
        self.assertEqual(
            component_label_from_trial_mapping_row(
                row, component_id=PRIMARY_COMPONENT, target_mode="middle"
            ),
            "absent",
        )
        self.assertEqual(
            component_label_from_trial_mapping_row(
                row, component_id=PRIMARY_COMPONENT, target_mode="anywhere"
            ),
            "present",
        )
        self.assertEqual(route_signature_tokens("A>B>C"), ["A", "B", "C"])

    def test_joint_target_shuffle_preserves_middle_implies_anywhere_and_strata_counts(
        self,
    ) -> None:
        rows = [
            _label_row("s1", "A->B", "train", "m0", "absent", "absent"),
            _label_row("s1", "A->B", "train", "m1", "absent", "present"),
            _label_row("s1", "A->B", "train", "m2", "present", "present"),
            _label_row("s1", "A->B", "validation", "v0", "absent", "absent"),
            _label_row("s1", "A->B", "validation", "v1", "present", "present"),
        ]
        shuffled, info = coherent_joint_target_shuffle(rows, seed=1)
        self.assertEqual(info["middle_implies_anywhere_violations"], 0)
        before = _joint_counts(rows)
        after_rows = [{**r, **shuffled[r["source_trial_id"]]} for r in rows]
        self.assertEqual(before, _joint_counts(after_rows))

    def test_three_target_family_reports_eligibility_signature_mismatches(self) -> None:
        rows = _track_c_count_rows()
        observed, nulls, summary = fit_track_c_three_target_family(
            rows, min_train_sources_per_unit=8, min_context_class_train=2, nulls=2, temporal_nulls=1
        )
        self.assertTrue(observed)
        self.assertEqual(summary["nulls"], 2)
        self.assertTrue(
            any(r["target_mode"] == TRACK_C_FAMILY_MAX_TARGET for r in nulls)
        )
        self.assertIn("null_policy", summary)
        self.assertIn("observed_eligibility_signatures", summary)
        self.assertIn("pvalues", summary)
        self.assertTrue(any(r["null_family"] == "session_endpoint_split_temporal_half" for r in nulls))


class Phase1GuardedExportTest(unittest.TestCase):
    def test_accepted_root_gate_rejects_other_paths(self) -> None:
        with self.assertRaises(ValueError):
            validate_accepted_root(Path("/tmp/not-the-accepted-root"))

    def test_export_requires_authorization(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            import_dir, split_dir, allowlist, selected = _export_fixture(Path(tmp))
            with self.assertRaises(PermissionError):
                export_development_cue_counts(
                    import_dir=import_dir,
                    split_dir=split_dir,
                    allowlist_csv=allowlist,
                    selected_cells_path=selected,
                    output_dir=Path(tmp) / "out",
                    authorized_phase=None,
                    selected_scope_hash=None,
                    selected_scope_count=None,
                )

    def test_poisoned_test_rows_and_unselected_cells_cannot_reach_export(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            import_dir, split_dir, allowlist, selected = _export_fixture(root)
            manifest = export_development_cue_counts(
                import_dir=import_dir,
                split_dir=split_dir,
                allowlist_csv=allowlist,
                selected_cells_path=selected,
                output_dir=root / "out",
                authorized_phase=AUTH_TOKEN,
                selected_scope_hash=None,
                selected_scope_count=None,
            )
            self.assertEqual(manifest["forbidden_rows_yielded"], 0)
            self.assertEqual(manifest["skipped_unselected_cell_rows"], 1)
            with gzip.open(
                root / "out" / "development_cue_counts.csv.gz",
                "rt",
                encoding="utf-8",
                newline="",
            ) as handle:
                exported = list(csv.DictReader(handle))
            self.assertEqual(
                {r["source_trial_id"] for r in exported},
                {"train_trial", "validation_trial"},
            )
            self.assertNotIn("999999", json.dumps(exported))
            self.assertNotIn("3.5", json.dumps(exported))

    def test_selected_fractional_cue_count_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            import_dir, split_dir, allowlist, selected = _export_fixture(root, selected_count="3.5")
            with self.assertRaisesRegex(ValueError, "noninteger"):
                export_development_cue_counts(
                    import_dir=import_dir,
                    split_dir=split_dir,
                    allowlist_csv=allowlist,
                    selected_cells_path=selected,
                    output_dir=root / "out",
                    authorized_phase=AUTH_TOKEN,
                    selected_scope_hash=None,
                    selected_scope_count=None,
                )

    def test_selected_cell_scope_hash_uses_canonical_sorted_json(self) -> None:
        cells = {"b/session01/x", "a/session01/x"}
        self.assertEqual(
            selected_cell_scope_hash(cells),
            selected_cell_scope_hash(reversed(sorted(cells))),
        )


# Helpers


def _product_fixture(
    absent_counts: tuple[int, ...],
    present_counts: tuple[int, ...],
    split: str = "validation",
):
    assert len(absent_counts) == len(present_counts)
    n_sessions = len(absent_counts)
    cells = [f"s{i}/session01/array/channel000/cell01" for i in range(n_sessions)]
    rows = []
    masks = []
    metas = []
    row_i = 0
    for sess_i, (na, npresent) in enumerate(
        zip(absent_counts, present_counts, strict=True)
    ):
        sess = f"s{sess_i}_session01"
        for label, n in (("absent", na), ("present", npresent)):
            for j in range(n):
                arr = np.full((n_sessions, 2), np.nan, dtype=np.float32)
                arr[sess_i, :] = [row_i + 1, (10 if label == "present" else -10) + j]
                mask = np.zeros(n_sessions, dtype=bool)
                mask[sess_i] = True
                sid = f"{sess}_{split}_{label}_{j}"
                metas.append(SourceMeta(sid, sess, split, label))
                rows.append(arr)
                masks.append(mask)
                row_i += 1
    return np.stack(rows), np.stack(masks), metas, cells


def _copy_metas_split(metas: list[SourceMeta], split: str) -> list[SourceMeta]:
    return [SourceMeta(m.source_trial_id, m.session_id, split, m.label) for m in metas]


def _copy_split(X: np.ndarray, _metas: list[SourceMeta], split: str) -> np.ndarray:
    _ = split
    return X.copy()


def _enumerate_label_from_fixture(X, M, metas, cells, *, label: str):
    from scripts.place195_path_generalization_phase1 import enumerate_product_rows

    return enumerate_product_rows(X, M, metas, cells, split=metas[0].split, label=label)


def _label_row(
    sess: str,
    endpoint: str,
    split: str,
    sid: str,
    middle: str,
    anywhere: str,
    supported: str = "absent",
) -> dict[str, str]:
    return {
        "source_trial_id": sid,
        "session_id": sess,
        "endpoint_pair": endpoint,
        "split": split,
        "trial_index": "1",
        "middle_component_label": middle,
        "anywhere_component_label": anywhere,
        "supported_middle_component_label": supported,
    }


def _joint_counts(rows: list[dict[str, str]]) -> dict[tuple[str, str, str, str, str], int]:
    out = {}
    for row in rows:
        key = (
            row["split"],
            row["endpoint_pair"],
            row["middle_component_label"],
            row["anywhere_component_label"],
            row["supported_middle_component_label"],
        )
        out[key] = out.get(key, 0) + 1
    return out


def _track_c_count_rows() -> list[dict[str, str]]:
    rows = []
    rng = np.random.default_rng(4)
    for target_i, endpoint in enumerate(("A->B", "A->C")):
        for split, n in (("train", 12), ("validation", 4)):
            for i in range(n):
                middle = "present" if i % 2 else "absent"
                anywhere = (
                    "present"
                    if middle == "present" or (i + target_i) % 4 == 0
                    else "absent"
                )
                supported = "present" if (i + target_i) % 3 else "absent"
                for cell in ("cell0", "cell1"):
                    rows.append(
                        {
                            "source_trial_id": f"{endpoint}_{split}_{i}",
                            "session_id": "s0_session01",
                            "split": split,
                            "trial_index": str(
                                i + (100 if split == "validation" else 0)
                            ),
                            "endpoint_pair": endpoint,
                            "middle_component_label": middle,
                            "anywhere_component_label": anywhere,
                            "supported_middle_component_label": supported,
                            "component_label": middle,
                            "cell_id": cell,
                            "cue_spike_count": str(
                                int(rng.poisson(3 + (middle == "present")))
                            ),
                            "cue_duration_s": "1.0",
                        }
                    )
    return rows


def _small_train_validation_fixture():
    return __import__(
        "scripts.place195_path_generalization_phase1", fromlist=["gaussian_source_fixture"]
    ).gaussian_source_fixture(
        session_cell_counts=(2, 1),
        n_bins=2,
        train_per_class_session=4,
        validation_per_class_session=2,
        mean_difference=0.7,
        seed=11,
    )


def _export_fixture(root: Path, *, selected_count: str = "3") -> tuple[Path, Path, Path, Path]:
    import_dir = root / "import"
    split_dir = root / "split"
    import_dir.mkdir()
    split_dir.mkdir()
    selected_cell = "s0/session01/array/channel000/cell01"
    unselected_cell = "s0/session01/array/channel999/cell99"
    _write_csv(
        split_dir / "source_trial_splits.csv",
        [
            {"source_trial_id": "train_trial", "split": "train"},
            {"source_trial_id": "validation_trial", "split": "validation"},
            {"source_trial_id": "test_trial", "split": "test"},
        ],
        ["source_trial_id", "split"],
    )
    (split_dir / "split_summary.json").write_text(
        json.dumps({"split_hash": "fixture"}), encoding="utf-8"
    )
    _write_gzip_csv(
        import_dir / "cue_counts.csv.gz",
        [
            _cue_row("train_trial", selected_cell, selected_count, "0", "1"),
            _cue_row("train_trial", unselected_cell, "3.5", "0", "1"),
            _cue_row("validation_trial", selected_cell, "4", "0", "1"),
            _cue_row("test_trial", selected_cell, "999999", "0", "1"),
        ],
        [
            "source_trial_id",
            "cell_id",
            "cue_spike_count",
            "cue_window_start_ripple_s",
            "cue_window_end_ripple_s",
        ],
    )
    # SplitFilteredAccess validates only the table being read; tiny placeholders keep the root shape familiar.
    _write_csv(import_dir / "trials.csv", [], ["source_trial_id"])
    _write_gzip_csv(import_dir / "path_samples.csv.gz", [], ["source_trial_id"])
    _write_gzip_csv(import_dir / "cue_spike_events.csv.gz", [], ["source_trial_id"])
    allowlist = root / "allowlist.csv"
    common = {
        "session_id": "s0_session01",
        "split": "train",
        "trial_index": "1",
        "endpoint_pair": "A->B",
        "start_id": "A",
        "goal_id": "B",
        "component_id": PRIMARY_COMPONENT,
        "target_mode": "middle",
        "component_label": "present",
        "middle_component_label": "present",
        "anywhere_component_label": "present",
        "supported_middle_component_label": "absent",
        "supported_middle_component_id": SUPPORTED_MIDDLE_COMPONENT,
        "primary_component_id": PRIMARY_COMPONENT,
        "qc_flags": "",
    }
    rows = [
        {**common, "source_trial_id": "train_trial", "split": "train"},
        {**common, "source_trial_id": "validation_trial", "split": "validation"},
    ]
    _write_csv(allowlist, rows, list(rows[0].keys()))
    selected = root / "selected_cells.csv"
    _write_csv(selected, [{"cell_id": selected_cell}], ["cell_id"])
    return import_dir, split_dir, allowlist, selected


def _cue_row(
    source: str, cell: str, count: str, start: str, end: str
) -> dict[str, str]:
    return {
        "source_trial_id": source,
        "cell_id": cell,
        "cue_spike_count": count,
        "cue_window_start_ripple_s": start,
        "cue_window_end_ripple_s": end,
    }


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
