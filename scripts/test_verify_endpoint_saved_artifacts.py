"""Synthetic checks for the packaging verifier; no model fitting or lab inputs."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

import numpy as np

from scripts.verify_endpoint_saved_artifacts import scores, verify_hashes


class EndpointSavedVerifierTest(unittest.TestCase):
    def test_hash_integrity_and_boundary(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            artifact = root / 'saved.txt'
            artifact.write_text('saved output')
            manifest = root / 'artifact_hashes.json'
            digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
            manifest.write_text(json.dumps({'saved.txt': digest}))
            self.assertEqual(verify_hashes(root), 1)
            artifact.write_text('changed output')
            with self.assertRaises(AssertionError):
                verify_hashes(root)
            manifest.write_text(json.dumps({'../outside.txt': digest}))
            with self.assertRaises(ValueError):
                verify_hashes(root)

    def test_metric_calculation(self):
        result = scores(np.array([0, 1]), np.array([0, 1]),
                        np.array([[.9, .1], [.2, .8]]))
        self.assertEqual(result['balanced_accuracy'], 1)
        self.assertEqual(result['macro_f1'], 1)
        self.assertAlmostEqual(result['log_loss'], -np.log(.9 * .8) / 2)


if __name__ == '__main__':
    unittest.main()
