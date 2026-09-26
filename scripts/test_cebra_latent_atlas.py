"""Synthetic and portable-delivery checks: no private inputs or model training."""

import ast
import hashlib
import json
import sys
import unittest
from pathlib import Path

import numpy as np
from numpy.testing import assert_allclose

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.cebra_latent_atlas import (
    condition_rdm,
    display_projection,
    fidelity,
    row_bins,
    sample_rows,
    source_audit,
    spectrum,
)


class AtlasTests(unittest.TestCase):
    def test_training_only_projection_and_native_identity(self):
        rng = np.random.default_rng(4)
        train = rng.normal(size=(50, 8))
        dev = rng.normal(size=(20, 8))
        a = display_projection(train, dev)
        b = display_projection(train, dev * 1000 + 99)
        assert_allclose(a[0], b[0])
        assert_allclose(a[1], b[1])
        assert_allclose(a[2][0], b[2][0])
        assert_allclose(a[1].T @ a[1], np.eye(3), atol=1e-12)
        residual = (dev - a[0]) - a[2][1] @ a[1].T
        expected = 1 - np.sum(residual**2) / np.sum((dev - a[0]) ** 2)
        self.assertAlmostEqual(a[3][1], expected)
        n = display_projection(train[:, :3], dev[:, :3], native=True)
        assert_allclose(n[2][1], dev[:, :3])
        assert_allclose(n[3], [1, 1])

    def test_row_bins_reject_bad_shapes_and_nonfinite(self):
        flat = np.arange(120).reshape(4, 30)
        z = row_bins(flat, 4, 3)
        assert_allclose(z[2, 7], flat[2, 21:24])
        with self.assertRaises(ValueError):
            row_bins(flat, 3, 4)
        with self.assertRaises(ValueError):
            row_bins(np.full((4, 30), np.nan), 4, 3)

    def test_fidelity_rotation_and_degeneracy(self):
        x = np.random.default_rng(8).normal(size=(40, 3))
        q, _ = np.linalg.qr(np.random.default_rng(5).normal(size=(3, 3)))
        ids = np.repeat(np.arange(20), 2)
        m = fidelity(x, x @ q, ids)
        self.assertAlmostEqual(m["distance_spearman"], 1)
        self.assertEqual(m["knn10_overlap"], 1)
        self.assertEqual(m["sample_rows"], 20)
        collapsed = fidelity(x, np.zeros_like(x), ids)
        self.assertIsNone(collapsed["distance_spearman"])
        self.assertIsNone(collapsed["knn10_overlap"])
        self.assertIsNone(spectrum(np.ones((20, 3)))["participation_ratio"])
        self.assertEqual(
            display_projection(np.ones((20, 3)), np.ones((20, 3)))[3], [None, None]
        )

    def test_condition_rdm_and_sampling(self):
        y = np.repeat(np.arange(3), 30)
        z = np.random.default_rng(2).normal(size=(90, 10, 5))
        bins, whole = condition_rdm(z, y, "bin"), condition_rdm(z, y, "whole")
        assert bins is not None and whole is not None
        self.assertEqual(bins.shape, (30,))
        self.assertEqual(whole.shape, (3,))
        self.assertIsNone(condition_rdm(z[:60], y[:60], "bin"))
        chosen = sample_rows(y)
        self.assertLessEqual(len(chosen), 64)
        assert_allclose(chosen, sample_rows(y))
        self.assertEqual(set(y[chosen]), {0, 1, 2})

    def test_source_join_and_corruption(self):
        ys = {s: np.array([0, 0, 1, 1]) for s in ("train", "development")}
        manifest, authority = [], []
        for split in ("train", "validation"):
            for label in ("absent", "present"):
                for row in range(2):
                    for session in range(7):
                        sid = f"{split}-{label}-{row}-{session}"
                        a = {
                            "source_trial_id": sid,
                            "session_id": str(session),
                            "split": split,
                            "label": label,
                        }
                        authority.append(a)
                        manifest.append({**a, "pseudo_row": str(row)})
        support, _ = source_audit(manifest[::-1], ys, "path", authority)
        self.assertEqual(support["train"]["unique_sources_used"], 28)
        bad = [*manifest, manifest[0]]
        with self.assertRaises(ValueError):
            source_audit(bad, ys, "path", authority)
        authority[0] = {**authority[0], "split": "validation"}
        with self.assertRaises(ValueError):
            source_audit(manifest, ys, "path", authority)

    def test_portable_delivery(self):
        package = (
            Path(__file__).resolve().parents[1] / "docs/reports/cebra-latent-atlas"
        )
        checks = json.loads((package / "delivery-checks.json").read_text())
        for name, digest in checks["files"].items():
            path = (package / name).resolve()
            self.assertTrue(path.is_relative_to(package))
            with self.subTest(file=name):
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), digest)
        manifest = json.loads((package / "execution-manifest.json").read_text())
        for name in ("atlas.html", "summary.json"):
            self.assertEqual(checks["files"][name], manifest["outputs"][name])
        atlas = (package / "atlas.html").read_text()
        payload = json.loads(
            atlas.split('<script type="application/json" id="data">', 1)[1]
            .split("</script>", 1)[0]
        )
        summary = json.loads((package / "summary.json").read_text())
        self.assertEqual(summary["run_count"], 39)
        self.assertEqual(summary["encoder_fits"], 0)
        self.assertEqual(summary["decoder_fits"], 0)
        self.assertEqual(summary["checkpoint_loads"], 0)
        self.assertEqual(
            [{k: v for k, v in run.items() if k != "views"} for run in payload["runs"]],
            summary["runs"],
        )
        self.assertEqual(payload["seeds"], summary["seed_consistency"])
        review = (package / "review.html").read_text()
        for expired in ("/tmp/pi-teach", "127.0.0.1:8766", "bg_kill", "19:07"):
            self.assertNotIn(expired, review)
        self.assertIn('href="atlas.html"', review)

    def test_no_model_runtime_imports_or_pickle_loader(self):
        path = Path(__file__).with_name("cebra_latent_atlas.py")
        tree = ast.parse(path.read_text())
        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(a.name.split(".")[0] for a in node.names)
            elif isinstance(node, ast.ImportFrom):
                imports.add((node.module or "").split(".")[0])
        self.assertFalse(imports & {"torch", "cebra", "joblib", "pickle", "sklearn"})
        self.assertNotIn("allow_pickle=True", path.read_text())


if __name__ == "__main__":
    unittest.main()
