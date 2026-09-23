"""Invented-data checks for issue #6; no private data or biological fits."""

from contextlib import redirect_stdout
from dataclasses import replace
import io
from pathlib import Path
import tempfile
import unittest

import numpy as np

from scripts import place195_path_preprocessing_autoresearch as pp
from scripts import place195_matched_pca as study
from scripts import verify_matched_pca as verify
from scripts import verify_path_preprocessing_results as vr


class MatchedPCATest(unittest.TestCase):
    def test_projection_rank_boundary_rotation_and_constant(self):
        rng = np.random.default_rng(17)
        X = rng.normal(size=(80, 4))
        state = pp.fit_pca_projection(X, variance_target=1)
        self.assertEqual(state["n_components"], 4)
        Z = pp.apply_projection(X, state)
        np.testing.assert_allclose(
            Z @ Z.T, (X - X.mean(0)) @ (X - X.mean(0)).T, atol=1e-10
        )
        low = np.column_stack((X[:, 0], 2 * X[:, 0]))
        self.assertEqual(pp.fit_pca_projection(low)["n_components"], 1)
        self.assertEqual(pp.fit_pca_projection(np.ones((8, 2)))["n_components"], 0)
        self.assertEqual(pp.fit_pca_projection(np.full((7, 2), 1.1))["n_components"], 0)
        # Exactly 90% in component one, including the frozen near-boundary rule.
        boundary = np.array([[3.0, 0.0], [-3.0, 0.0], [0.0, 1.0], [0.0, -1.0]])
        self.assertEqual(pp.fit_pca_projection(boundary)["n_components"], 1)
        with self.assertRaises(ValueError):
            pp.fit_pca_projection(np.array([[np.nan]]))
        tensor = pp.synthetic_tensor(mean_difference=3, seed=9, endpoints=("2->1",))
        train = pp.materialize_plan(
            tensor,
            pp.make_draw_plan(tensor.records, split="train", rows_per_class=64, seed=0),
        )
        raw = pp.fit_candidate_model(train, study.candidates()[2])
        features = pp.feature_matrix(train.X_counts, train.E, raw.candidate)
        scaled = pp.apply_scaler(features, raw.scaler)
        rotation = pp.fit_pca_projection(scaled, variance_target=1)
        model = pp.LogisticRegression(
            C=pp.average_loss_logistic_c(1, len(train.y)), max_iter=1000, random_state=0
        )
        model.fit(pp.apply_projection(scaled, rotation), train.y)
        rotated = replace(
            raw, candidate=study.candidates()[5], model=model, projection=rotation
        )
        np.testing.assert_allclose(
            pp.predict_candidate(raw, train),
            pp.predict_candidate(rotated, train),
            atol=1e-6,
        )
        fit = pp.fit_candidate_model(train, study.candidates()[5])
        self.assertEqual(
            pp.candidate_from_dict(pp.model_replay_payload(fit)), fit.candidate
        )
        self.assertEqual(
            pp.candidate_from_dict(pp.model_replay_payload(raw)), raw.candidate
        )
        doubled = replace(
            train,
            X_counts=np.tile(train.X_counts, (2, 1, 1)),
            E=np.tile(train.E, (2, 1, 1)),
            y=np.tile(train.y, 2),
            weights=np.tile(train.weights / 2, 2),
        )
        duplicate_fit = pp.fit_candidate_model(doubled, study.candidates()[5])
        np.testing.assert_allclose(
            pp.predict_candidate(fit, train),
            pp.predict_candidate(duplicate_fit, train),
            atol=1e-6,
        )
        np.testing.assert_allclose(
            pp.predict_candidate(fit, train),
            pp.predict_from_replay(
                pp.model_replay_payload(fit), train.X_counts, train.E
            ),
            atol=1e-12,
        )

    def test_selection_ties_metrics_and_pure_null(self):
        rows = [
            {**c.as_dict(), "mean_cv_log_loss": 1 + i * 1e-14}
            for i, c in enumerate(study.candidates())
        ]
        selected = study.select(rows)
        self.assertEqual(
            selected,
            {"raw": study.candidates()[2].key, "pca": study.candidates()[5].key},
        )
        # A different world must select anew, not retain observed choices.
        rows[0]["mean_cv_log_loss"] = 0.1
        rows[3]["mean_cv_log_loss"] = 0.2
        self.assertEqual(
            study.select(rows),
            {"raw": rows[0]["candidate_key"], "pca": rows[3]["candidate_key"]},
        )
        self.assertEqual(study.tail_reference(1, [1, 1, 1]), 1)
        self.assertEqual(study.tail_reference(1, [0, 1 - 5e-13]), 2 / 3)
        y, p, w = (
            np.array([0, 1, 1]),
            np.array([1.0, 1.0, 0.0]),
            np.array([0.5, 0.25, 0.25]),
        )
        expected = vr.group_metrics(
            [
                {"true_label": pp.INT_TO_LABEL[int(a)], "prob_present": b, "weight": c}
                for a, b, c in zip(y, p, w, strict=True)
            ]
        )
        vr.close_fields(pp.weighted_metrics(y, p, w), expected)
        self.assertGreater(expected["log_loss"], 10)
        tensor = pp.synthetic_tensor(mean_difference=0)
        pure = [replace(r, label="present") for r in tensor.records]
        labels, audit = pp.make_label_permutation(pure, seed=50000)
        self.assertTrue(all(labels[r.source_trial_id] == r.label for r in pure))
        self.assertEqual(audit["movable_fraction"], 0)

    def test_heldout_poison_cannot_change_cv(self):
        tensor = pp.synthetic_tensor(mean_difference=2, seed=15, endpoints=("2->1",))
        poisoned = tensor.X.copy()
        for i, r in enumerate(tensor.records):
            if r.split == "validation":
                poisoned[i, tensor.M[i]] = 1e6
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            a = study.run_cv(tensor, root / "a", rows_per_class=16)
            b = study.run_cv(replace(tensor, X=poisoned), root / "b", rows_per_class=16)
            self.assertEqual(a, b)
            self.assertEqual(
                pp.read_json(root / "a/cv_models.json.gz"),
                pp.read_json(root / "b/cv_models.json.gz"),
            )
        for projection in ("none", "pca90"):
            candidate = pp.Candidate(1, "raw_rate", "variance_floor", 1, projection)
            plan = pp.make_draw_plan(
                tensor.records,
                split="train",
                rows_per_class=16,
                seed=0,
                fold_mode="train",
                fold=0,
            )
            train = pp.materialize_plan(tensor, plan)
            fit = pp.fit_candidate_model(train, candidate)
            before = pp.model_replay_payload(fit)
            evaluation = pp.build_product_rows(
                tensor, split="train", fold_mode="validation", fold=0
            )
            pp.predict_candidate(
                fit, replace(evaluation, X_counts=evaluation.X_counts + 1e6)
            )
            self.assertEqual(before, pp.model_replay_payload(fit))
            train_ids = {r["source_trial_id"] for r in train.manifest}
            self.assertFalse(
                train_ids & {r["source_trial_id"] for r in evaluation.manifest}
            )

    def test_positive_and_constant_no_signal(self):
        for signal in (0, 30):
            tensor = pp.synthetic_tensor(
                mean_difference=signal, seed=33, endpoints=("2->1",)
            )
            if signal == 0:
                X = tensor.X.copy()
                X[tensor.M] = 1
                tensor = replace(tensor, X=X)
            train = pp.materialize_plan(
                tensor,
                pp.make_draw_plan(
                    tensor.records, split="train", rows_per_class=32, seed=0
                ),
            )
            evaluation = pp.build_product_rows(tensor, split="validation")
            for candidate in study.candidates():
                fit = pp.fit_candidate_model(train, candidate)
                probs = pp.predict_candidate(fit, evaluation)
                score = pp.weighted_metrics(evaluation.y, probs, evaluation.weights)
                if signal:
                    self.assertGreater(score["balanced_accuracy"], 0.8)
                    self.assertGreater(score["delta_log_loss_baseline_minus_model"], 0)
                else:
                    np.testing.assert_allclose(probs, 0.5, atol=1e-12)
                    self.assertAlmostEqual(score["log_loss"], np.log(2))

    def test_complete_integration_forward_only_and_corruptions(self):
        tensor = pp.synthetic_tensor(mean_difference=5, seed=71, endpoints=("2->1",))
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            try:
                with redirect_stdout(io.StringIO()):
                    result = study.execute(
                        tensor,
                        directory,
                        rows_per_class=8,
                        null_count=1,
                        bootstrap_count=2,
                    )
            finally:
                pp.ACTIVE_PROGRESS_PATH = None
            with verify.forbid_fits():
                receipt = verify.verify(directory, tensor, integrity=False)
            self.assertEqual(receipt["models_forward_replayed"], result["fit_count"])
            self.assertEqual(
                result["fit_count"], sum(study.fit_budget(tensor, 1, 2).values())
            )
            corruptions = (
                (
                    "observed/cv_models.json.gz",
                    lambda x: x[3].update(cell_ids=list(reversed(x[3]["cell_ids"]))),
                ),
                (
                    "observed/validation_models.json.gz",
                    lambda x: x[3]["projection_state"]["components"][0].__setitem__(
                        0, 123.0
                    ),
                ),
                (
                    "observed/validation_source_lineage.json.gz",
                    lambda x: x[0].update(source_trial_id="invented-corruption"),
                ),
                (
                    "observed/selection.json",
                    lambda x: x["selected"].update(raw="not-a-recipe"),
                ),
                (
                    "summary.json",
                    lambda x: x["observed"].update(raw_loss_minus_pca_loss=123.0),
                ),
            )
            for relative, mutate in corruptions:
                path = directory / relative
                original = path.read_bytes()
                payload = pp.read_json(path)
                mutate(payload)
                pp.write_json(path, payload)
                try:
                    with (
                        verify.forbid_fits(),
                        self.assertRaises((AssertionError, ValueError, KeyError)),
                    ):
                        verify.verify(directory, tensor, integrity=False)
                finally:
                    path.write_bytes(original)
            path = directory / "observed/validation_predictions.csv.gz"
            original = path.read_bytes()
            predictions = vr.csv_rows(path)
            predictions[0]["prob_present"] = 0.123456
            pp.write_csv(path, predictions)
            try:
                with verify.forbid_fits(), self.assertRaises(AssertionError):
                    verify.verify(directory, tensor, integrity=False)
            finally:
                path.write_bytes(original)


if __name__ == "__main__":
    unittest.main()
