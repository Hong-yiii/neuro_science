"""Invented-input regression tests; no biological models are fitted."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from threadpoolctl import threadpool_limits

from scripts.verify_cebra_endpoint_run import (
    float64_scaler_replay,
    load_frozen_runner,
    precision_corrected_replay,
    training_backend_replay,
)

CEBRA_DIM = 8


def _pca_replay_features(cue, components, mean):
    raise RuntimeError("test replay must bind its reviewed PCA adapter")


def scaler_probe(pooled_train):
    mean = np.mean(pooled_train, axis=0)
    scale = np.sqrt(np.var(pooled_train, axis=0))
    scale[scale == 0] = 1.0
    return mean, scale


def broader_probe(pooled_train):
    mean = np.mean(pooled_train, axis=1)
    return mean, np.var(pooled_train, axis=0)


def replay_probe(pooled_train, pca_file):
    scaler_mean = np.mean(pooled_train, axis=0)
    scaler_var = np.var(pooled_train, axis=0)
    components = np.asarray(pca_file["components"], dtype=np.float64)
    pca_mean = np.asarray(pca_file["mean"], dtype=np.float64)
    features = _pca_replay_features(pca_file["cue"], components, pca_mean)
    return scaler_mean, scaler_var, features


def wrong_pca_cast_probe(pooled_train, pca_file):
    scaler_mean = np.mean(pooled_train, axis=0)
    scaler_var = np.var(pooled_train, axis=0)
    components = np.asarray(pca_file["components"], dtype=np.float32)
    pca_mean = np.asarray(pca_file["mean"], dtype=np.float32)
    return scaler_mean, scaler_var, components, pca_mean


def load_encoder_checkpoint(*, device):
    return ("checkpoint", device)


def _embed_cue(solver, data, *, device):
    return (solver, data, device)


def backend_probe():
    solver = load_encoder_checkpoint(device="cpu")
    train = _embed_cue(solver, "train", device="cpu")
    development = _embed_cue(solver, "development", device="cpu")
    return solver, train, development


def wrong_backend_probe():
    solver = load_encoder_checkpoint(device="cuda")
    train = _embed_cue(solver, "train", device="cpu")
    development = _embed_cue(solver, "development", device="cpu")
    return solver, train, development


class ScalerReplayRegression(unittest.TestCase):
    def test_float32_source_reconstructs_sklearn_float64_statistics(self):
        pooled = np.sqrt(
            np.random.default_rng(123).poisson(0.25, (4800, 195)).astype(np.float32)
        )
        fitted = StandardScaler().fit(pooled)  # Invented data only.
        assert fitted.mean_ is not None and fitted.scale_ is not None
        expected_mean = np.asarray(fitted.mean_, dtype=np.float64)
        expected_scale = np.asarray(fitted.scale_, dtype=np.float64)
        original_mean, original_scale = scaler_probe(pooled)
        self.assertGreater(float(np.max(np.abs(original_scale - expected_scale))), 1e-6)
        amended = float64_scaler_replay(scaler_probe)
        mean, scale = amended(pooled)
        np.testing.assert_allclose(mean, expected_mean, rtol=1e-7, atol=1e-9)
        np.testing.assert_allclose(scale, expected_scale, rtol=1e-7, atol=1e-9)
        self.assertIs(amended.__code__, scaler_probe.__code__)
        self.assertEqual(original_mean.dtype, np.float32)
        self.assertEqual(mean.dtype, np.float64)

    def test_no_global_numpy_mutation(self):
        before_mean, before_var = np.mean, np.var
        amended = float64_scaler_replay(scaler_probe)
        amended(np.ones((3, 2), dtype=np.float32))
        self.assertIs(np.mean, before_mean)
        self.assertIs(np.var, before_var)
        self.assertEqual(np.mean(np.ones(3, dtype=np.float32)).dtype, np.float32)

    def test_refuses_broader_reduction_changes(self):
        with self.assertRaisesRegex(ValueError, "unexpected scaler reduction"):
            float64_scaler_replay(broader_probe)

    def test_refuses_unapproved_runner_before_import(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "unapproved.py"
            path.write_text("raise AssertionError('must never execute')\n")
            with self.assertRaisesRegex(ValueError, "approved bytes"):
                load_frozen_runner(path)

    def test_precision_corrected_replay_matches_fit_time_pca_without_refitting(self):
        rng = np.random.default_rng(456)
        cue = rng.normal(size=(48, 12, 8)).astype(np.float32)
        flat = cue.transpose(0, 2, 1).reshape(-1, cue.shape[1])
        fitted_pca = PCA(
            n_components=CEBRA_DIM,
            svd_solver="full",
            whiten=False,
            random_state=0,
        ).fit(flat)
        pooled = rng.random((120, 4), dtype=np.float32)
        fitted_scaler = StandardScaler().fit(pooled)
        assert fitted_pca.components_ is not None and fitted_pca.mean_ is not None
        assert fitted_scaler.mean_ is not None and fitted_scaler.var_ is not None
        pca_file = {
            "cue": cue,
            "components": np.asarray(fitted_pca.components_).copy(),
            "mean": np.asarray(fitted_pca.mean_).copy(),
        }
        expected_scaler_mean = np.asarray(fitted_scaler.mean_, dtype=np.float64)
        expected_scaler_var = np.asarray(fitted_scaler.var_, dtype=np.float64)
        with threadpool_limits(limits=2):
            expected = (
                fitted_pca.transform(flat)
                .astype(np.float32)
                .reshape(cue.shape[0], cue.shape[2] * CEBRA_DIM)
            )
            corrected = precision_corrected_replay(replay_probe)
            with patch.object(
                PCA, "fit", side_effect=AssertionError("replay must not fit PCA")
            ):
                scaler_mean, scaler_var, features = corrected(pooled, pca_file)
        np.testing.assert_allclose(features, expected, rtol=1e-7, atol=1e-6)
        np.testing.assert_allclose(
            scaler_mean, expected_scaler_mean, rtol=1e-7, atol=1e-9
        )
        np.testing.assert_allclose(
            scaler_var, expected_scaler_var, rtol=1e-7, atol=1e-9
        )
        self.assertEqual(pca_file["components"].dtype, np.float32)
        self.assertEqual(pca_file["mean"].dtype, np.float32)

    def test_refuses_unexpected_pca_state_cast(self):
        with self.assertRaisesRegex(ValueError, "unexpected persisted PCA state cast"):
            precision_corrected_replay(wrong_pca_cast_probe)

    def test_encoder_backend_is_scoped_without_global_mutation_or_fits(self):
        original_load, original_embed = load_encoder_checkpoint, _embed_cue
        amended = training_backend_replay(backend_probe, device="cuda")
        solver, train, development = amended()
        self.assertEqual(solver[1], "cuda")
        self.assertEqual(train[2], "cuda")
        self.assertEqual(development[2], "cuda")
        self.assertEqual(backend_probe()[0][1], "cpu")
        self.assertIs(load_encoder_checkpoint, original_load)
        self.assertIs(_embed_cue, original_embed)
        self.assertIs(amended.__code__, backend_probe.__code__)

    def test_refuses_unexpected_backend_or_callsite(self):
        with self.assertRaisesRegex(ValueError, "fitted on CUDA"):
            training_backend_replay(backend_probe, device="cpu")
        with self.assertRaisesRegex(ValueError, "unexpected original replay backend"):
            training_backend_replay(wrong_backend_probe, device="cuda")


if __name__ == "__main__":
    unittest.main()
