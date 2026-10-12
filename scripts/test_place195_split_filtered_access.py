from __future__ import annotations

import csv
import gzip
import json
import tempfile
import unittest
from pathlib import Path

from scripts.place195_split_filtered_access import SplitAccessError, SplitFilteredAccess


class SplitFilteredAccessTest(unittest.TestCase):
    def test_source_relocation_preserves_identity_and_provenance(self) -> None:
        """Software migration check: source and invented fixtures only, no models."""
        import ast
        import hashlib
        import os
        import subprocess
        import sys
        from types import SimpleNamespace

        from neuro import place195_split_access as implementation
        from scripts import place195_split_filtered_access as legacy

        root = Path(__file__).resolve().parents[1]
        source = root / "src/neuro/place195_split_access.py"
        original_sha256 = "2cd7e7a14f6a045078c59d2489e6d06a615f033dc0f6c0cbea14533561608c0d"
        self.assertIs(legacy, implementation)
        self.assertIs(SplitFilteredAccess, implementation.SplitFilteredAccess)
        self.assertEqual(SplitFilteredAccess.__module__, "neuro.place195_split_access")
        self.assertEqual(Path(implementation.__file__).resolve(), source)
        self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(), original_sha256)

        # Compile only provenance helpers, not runners' imports or private inputs.
        for name in ("cebra_full_trial_transfer", "cebra_cue_time_readout", "cebra_endpoint_time_readout"):
            script = root / "scripts" / f"{name}.py"
            nodes: list[ast.stmt] = [
                node for node in ast.parse(script.read_text()).body
                if isinstance(node, ast.FunctionDef)
                and node.name in ("helper_paths", "helper_hashes")
            ]
            namespace = {
                "Path": Path, "sys": sys, "WORKTREE_ROOT": root, "CANONICAL_ROOT": root,
                "SCRIPT_PATH": script, "PROTOCOL_PATH": root / "scripts/README.md",
                "SplitFilteredAccess": SplitFilteredAccess,
                "ft": SimpleNamespace(SplitFilteredAccess=SplitFilteredAccess),
                "sha256_file": lambda path: hashlib.sha256(path.read_bytes()).hexdigest(),
            }
            exec(compile(ast.Module(body=nodes, type_ignores=[]), str(script), "exec"), namespace)
            paths = namespace["helper_paths"]()
            hashes = namespace["helper_hashes"]()
            self.assertEqual(paths["src/neuro/place195_split_access.py"].resolve(), source)
            self.assertEqual(hashes["src/neuro/place195_split_access.py"], original_sha256)
            old_key = next(key for key in hashes if key.endswith("place195_split_filtered_access.py"))
            self.assertNotEqual(hashes[old_key], original_sha256)  # old approvals are stale

        with tempfile.TemporaryDirectory() as tmp:
            env = {**os.environ, "PYTHONPATH": str(root), "PYTHONDONTWRITEBYTECODE": "1"}
            for first in ("scripts.place195_split_filtered_access", "place195_split_filtered_access", "neuro.place195_split_access"):
                code = (
                    "import importlib, sys\n"
                    f"sys.path[:0] = [{str(root / 'scripts')!r}, {str(root / 'src')!r}]\n"
                    f"first = importlib.import_module({first!r})\n"
                    "new = importlib.import_module('neuro.place195_split_access')\n"
                    "old = importlib.import_module('scripts.place195_split_filtered_access')\n"
                    "bare = importlib.import_module('place195_split_filtered_access')\n"
                    "assert first is new is old is bare\n"
                    "assert not {'numpy', 'torch', 'cebra', 'h5py'} & sys.modules.keys()\n"
                )
                subprocess.run([sys.executable, "-S", "-B", "-c", code], cwd=tmp, env=env, check=True)
            for args in ((str(root / "scripts/place195_split_filtered_access.py"),), ("-m", "scripts.place195_split_filtered_access")):
                subprocess.run([sys.executable, "-S", "-B", *args], cwd=tmp, env=env, check=True)
            self.assertEqual(list(Path(tmp).iterdir()), [])

    def test_sentinel_test_values_do_not_reach_downstream_aggregates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            import_dir, split_dir = _fixture(root)
            access = SplitFilteredAccess(import_dir, split_dir)

            trial_goals = [row["marker_minor_digit"] for row in access.iter_trials()]
            path_sum = sum(
                float(row["position_axis1"]) for row in access.iter_path_samples()
            )
            cue_sum = sum(
                float(row["cue_spike_count"]) for row in access.iter_cue_counts()
            )
            event_sum = sum(
                float(row["cue_relative_time_s"])
                for row in access.iter_cue_spike_events()
            )

            self.assertEqual(trial_goals, ["1", "2"])
            self.assertEqual(path_sum, 3.0)
            self.assertEqual(cue_sum, 7.0)
            self.assertAlmostEqual(event_sum, 0.3)
            audit = access.audit.as_dict()
            self.assertEqual(audit["forbidden_rows_yielded"], 0)
            self.assertEqual(audit["rows_skipped_by_split"]["cue_counts"]["test"], 1)

    def test_missing_split_mapping_fails_before_yield(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            import_dir, split_dir = _fixture(root, include_unmapped_trial=True)
            access = SplitFilteredAccess(import_dir, split_dir)
            with self.assertRaisesRegex(SplitAccessError, "no split mapping"):
                list(access.iter_trials())

    def test_test_split_cannot_be_allowed_for_development_access(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            import_dir, split_dir = _fixture(root)
            with self.assertRaisesRegex(SplitAccessError, "forbids"):
                SplitFilteredAccess(import_dir, split_dir, allowed_splits={"test"})


def _fixture(root: Path, include_unmapped_trial: bool = False) -> tuple[Path, Path]:
    import_dir = root / "import"
    split_dir = root / "splits"
    import_dir.mkdir()
    split_dir.mkdir()
    _write_csv(
        split_dir / "source_trial_splits.csv",
        [
            {"source_trial_id": "train_trial", "split": "train"},
            {"source_trial_id": "validation_trial", "split": "validation"},
            {"source_trial_id": "test_trial", "split": "test"},
        ],
        ("source_trial_id", "split"),
    )
    (split_dir / "split_summary.json").write_text(
        json.dumps({"split_hash": "fixture"}), encoding="utf-8"
    )
    trial_rows = [
        {
            "session_id": "s1",
            "source_trial_id": "train_trial",
            "trial_index": "1",
            "marker_minor_digit": "1",
        },
        {
            "session_id": "s1",
            "source_trial_id": "validation_trial",
            "trial_index": "2",
            "marker_minor_digit": "2",
        },
        {
            "session_id": "s1",
            "source_trial_id": "test_trial",
            "trial_index": "3",
            "marker_minor_digit": "TEST_SENTINEL",
        },
    ]
    if include_unmapped_trial:
        trial_rows.append(
            {
                "session_id": "s1",
                "source_trial_id": "missing_trial",
                "trial_index": "4",
                "marker_minor_digit": "999",
            }
        )
    _write_csv(
        import_dir / "trials.csv",
        trial_rows,
        ("session_id", "source_trial_id", "trial_index", "marker_minor_digit"),
    )
    _write_gzip_csv(
        import_dir / "path_samples.csv.gz",
        [
            {"source_trial_id": "train_trial", "position_axis1": "1"},
            {"source_trial_id": "validation_trial", "position_axis1": "2"},
            {"source_trial_id": "test_trial", "position_axis1": "999999"},
        ],
        ("source_trial_id", "position_axis1"),
    )
    _write_gzip_csv(
        import_dir / "cue_counts.csv.gz",
        [
            {"source_trial_id": "train_trial", "cell_id": "c1", "cue_spike_count": "3"},
            {
                "source_trial_id": "validation_trial",
                "cell_id": "c1",
                "cue_spike_count": "4",
            },
            {
                "source_trial_id": "test_trial",
                "cell_id": "c1",
                "cue_spike_count": "777",
            },
        ],
        ("source_trial_id", "cell_id", "cue_spike_count"),
    )
    _write_gzip_csv(
        import_dir / "cue_spike_events.csv.gz",
        [
            {"source_trial_id": "train_trial", "cue_relative_time_s": "0.1"},
            {"source_trial_id": "validation_trial", "cue_relative_time_s": "0.2"},
            {"source_trial_id": "test_trial", "cue_relative_time_s": "999"},
        ],
        ("source_trial_id", "cue_relative_time_s"),
    )
    return import_dir, split_dir


def _write_csv(
    path: Path, rows: list[dict[str, str]], fieldnames: tuple[str, ...]
) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _write_gzip_csv(
    path: Path, rows: list[dict[str, str]], fieldnames: tuple[str, ...]
) -> None:
    with gzip.open(path, "wt", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    unittest.main()
