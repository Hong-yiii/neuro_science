"""Data-free tests for notebook boundaries and executed-public-artifact checks.

Run with the notebook environment. No private artifacts are opened by this test.
"""

import base64
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import endpoint_replay as replay

HERE = Path(__file__).resolve().parent


class NotebookChecks(unittest.TestCase):
    def test_authentication_and_scope_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            payload = b'{"ok": true}'
            path = root / "observed/seed0/example.json"
            path.parent.mkdir(parents=True)
            path.write_bytes(payload)
            manifest = {"observed/seed0/example.json": hashlib.sha256(payload).hexdigest()}
            manifest_bytes = json.dumps(manifest).encode()
            (root / "hash_manifest.json").write_bytes(manifest_bytes)
            with self.assertRaisesRegex(ValueError, "manifest identity"):
                replay.SavedRun(root)
            with patch.object(replay, "MANIFEST_SHA256", hashlib.sha256(manifest_bytes).hexdigest()):
                saved = replay.SavedRun(root)
                self.assertEqual(saved.json("observed/seed0/example.json"), {"ok": True})
                for outside in ("null_000/seed0/example.json", "../example.json", "/tmp/example.json", "observed/seed3/example.json"):
                    with self.assertRaisesRegex(ValueError, "scope"):
                        saved.read(outside)
                path.write_bytes(b"tampered")
                with self.assertRaisesRegex(ValueError, "hash mismatch"):
                    saved.read("observed/seed0/example.json")
                path.unlink()
                path.symlink_to(root.parent / "outside.json")
                with self.assertRaises((ValueError, FileNotFoundError)):
                    saved.read("observed/seed0/example.json")

    def test_fit_and_optimizer_guard(self):
        import importlib.util

        if not all(importlib.util.find_spec(name) for name in ("torch", "cebra")):
            self.skipTest("Requires the recorded scientific/notebook runtime")
        import numpy as np
        import torch
        from sklearn.preprocessing import StandardScaler
        from threadpoolctl import threadpool_info

        original = StandardScaler.fit
        parameter = torch.nn.Parameter(torch.zeros(1))
        optimizer = torch.optim.Adam([parameter])
        with replay.no_fitting():
            blas = [library for library in threadpool_info() if library["user_api"] == "blas"]
            self.assertTrue(blas)
            self.assertTrue(all(library["num_threads"] == 2 for library in blas))
            with self.assertRaisesRegex(RuntimeError, "forbids fitting"):
                StandardScaler().fit(np.zeros((2, 2)))
            with self.assertRaisesRegex(RuntimeError, "forbids fitting"):
                optimizer.step()
        self.assertIs(StandardScaler.fit, original)
        self.assertEqual(parameter.item(), 0)

    def test_executed_notebook_and_public_outputs(self):
        notebook = json.loads((HERE / "endpoint_walkthrough.ipynb").read_text())
        cells = [c for c in notebook["cells"] if c["cell_type"] == "code"]
        self.assertEqual([c["execution_count"] for c in cells], list(range(1, len(cells) + 1)))
        evidence = notebook["metadata"]["saved_artifact_execution"]
        self.assertEqual(evidence["helper_sha256"], hashlib.sha256((HERE / "endpoint_replay.py").read_bytes()).hexdigest())
        sources = ["".join(c["source"]) for c in cells]
        self.assertEqual(evidence["code_sha256"], hashlib.sha256("\n".join(sources).encode()).hexdigest())
        images = 0
        for cell in cells:
            for output in cell["outputs"]:
                self.assertNotEqual(output["output_type"], "error")
                if "image/png" in output.get("data", {}):
                    data = base64.b64decode("".join(output["data"]["image/png"]), validate=True)
                    self.assertTrue(data.startswith(b"\x89PNG\r\n\x1a\n"))
                    images += 1
        self.assertGreaterEqual(images, 12)  # Six data/schematic figures plus rendered equations.
        public = json.dumps([c["outputs"] for c in cells])
        for forbidden in ("source_trial_id", "session_id", str(HERE.parent), "checkpoint_final.pth", "array(["):
            self.assertNotIn(forbidden, public)
        self.assertIn("END-TO-END SAVED-INPUT REPLAY PASSED", public)


if __name__ == "__main__":
    unittest.main()
