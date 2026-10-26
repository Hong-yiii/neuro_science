# pyright: reportMissingImports=false
"""Source/synthetic non-fitting migration checks; never run private studies here."""

from __future__ import annotations

import ast
import copy
import hashlib
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from neuro.execution import (
    check_deadline,
    ensure_fresh_dir,
    sha256_file,
    snapshot_sources,
)
from neuro.provenance import REPOSITORY_ROOT, study_sources

ROOT = REPOSITORY_ROOT
BASELINE = "cc0527e5f6d4d84f7024044d69c2c85f2b563b4c"
HELPER_BASELINE = "ce31248729a9b54aaf3fea8c014fe16c0e0105b4"
HELPER_SOURCES = {
    "raw_io": (
        "scripts/import_place195_sessions.py",
        "1ae0030803c911e0f57eed330408a0f43d8951504d73d31e7e06bdc075f752c5",
        [
            "EventTrials",
            "SpikeTrain",
            "_codes_at",
            "_csv_value",
            "_decode_matlab_string",
            "_event_matrix",
            "_find_hdf5_group_with",
            "_scalar_to_string",
            "_times_at",
            "_to_float",
            "_to_int",
            "read_ripple_trials",
            "read_spiketrain",
            "spikes_in_window",
        ],
    ),
    "neural_inputs": (
        "scripts/place195_v7_v8_neural_experiments.py",
        "db3b79d4afe162872365795b6f944497eac03671b71e0659f66978292af4e477",
        ["bin_events", "session_from_cell"],
    ),
    "cebra_solver": (
        "scripts/place195_v8b_v9_cebra.py",
        "737ad148dcc261c3ec1bbbd1ada395b34b47b2b37c5920370d3107c209976f9a",
        ["make_solver"],
    ),
    "geometry": (
        "scripts/cebra_latent_atlas.py",
        "34ac15404904431ce3d0cef3192ea49eabe7ed33fd85e9ca54baee0a0cb228a4",
        ["fidelity", "rank_correlation", "require", "spectrum"],
    ),
}
STUDIES = ("full_trial_transfer", "endpoint_time_readout", "cue_time_readout")
SAMPLER_MOVED = {
    "CebraVectorDataset",
    "pad_groups",
    "PhaseTimeLoader",
    "PhaseBehaviorLoader",
}
ORIGINAL_HASHES = (
    "bea7561b922f1c3a36dfe563ba1c1d08b85749d4a3221243bf1adc35d425b7d1",
    "0967a9a69c56e7d0b59aa20600817d48c34deeb7fd9aceabec11b3706a4f84a5",
    "746a570a5bda809bdd3659e02e12ba5cad226444f6f889e9a93abd1296f47b55",
)


def _source(name: str) -> Path:
    return ROOT / "src/neuro/studies" / f"{name}.py"


def _without_snapshot_loop(node: ast.AST) -> ast.AST:
    """Only the declared helper-copy loop moved to snapshot_sources."""
    node = copy.deepcopy(node)
    if isinstance(node, ast.FunctionDef):
        node.body = [
            statement
            for statement in node.body
            if not (
                isinstance(statement, ast.For)
                and ast.unparse(statement.iter) == "helper_paths().items()"
            )
            and not (
                isinstance(statement, ast.Expr)
                and isinstance(statement.value, ast.Call)
                and ast.unparse(statement.value.func) == "snapshot_sources"
            )
        ]
    return node


class StudyPackageTests(unittest.TestCase):
    def test_scientific_definitions_preserve_baseline_ast(self):
        for name, expected_hash in zip(STUDIES, ORIGINAL_HASHES, strict=True):
            original = subprocess.check_output(
                ["git", "show", f"{BASELINE}:scripts/cebra_{name}.py"], cwd=ROOT
            )
            self.assertEqual(hashlib.sha256(original).hexdigest(), expected_hash)
            before = {
                node.name: node
                for node in ast.parse(original).body
                if isinstance(node, (ast.FunctionDef, ast.ClassDef))
            }
            after = {
                node.name: node
                for node in ast.parse(_source(name).read_text()).body
                if isinstance(node, (ast.FunctionDef, ast.ClassDef))
            }
            if name == "full_trial_transfer":
                extracted = {
                    node.name: node
                    for node in ast.parse(
                        (ROOT / "src/neuro/_cebra_sampling.py").read_text()
                    ).body
                    if isinstance(node, (ast.FunctionDef, ast.ClassDef))
                }
                self.assertEqual(set(extracted), SAMPLER_MOVED)
                self.assertTrue(set(extracted).isdisjoint(after))
                after.update(
                    extracted
                )  # Exact pinned AST checks still cover every moved body.
            changed = {"sha256_file", "helper_paths"}
            moved = {"sha256_file"} if name != "endpoint_time_readout" else set()
            if name == "full_trial_transfer":
                moved.add("check_deadline")
            else:
                moved.add("ensure_fresh_dir")
            if name == "cue_time_readout":
                changed.add("approval_facts")  # current-source identity, not old review
            self.assertEqual(set(after), set(before) - moved)
            for symbol in set(after) - changed:
                self.assertEqual(
                    ast.dump(_without_snapshot_loop(before[symbol])),
                    ast.dump(_without_snapshot_loop(after[symbol])),
                    f"scientific AST changed: {name}.{symbol}",
                )

    def test_extracted_helpers_preserve_exact_pinned_ast(self):
        for module, (source, expected_hash, symbols) in HELPER_SOURCES.items():
            original = subprocess.check_output(
                ["git", "show", f"{HELPER_BASELINE}:{source}"], cwd=ROOT
            )
            self.assertEqual(hashlib.sha256(original).hexdigest(), expected_hash)
            before = {
                node.name: node
                for node in ast.parse(original).body
                if isinstance(node, (ast.FunctionDef, ast.ClassDef))
            }
            after = {
                node.name: node
                for node in ast.parse(
                    (ROOT / f"src/neuro/{module}.py").read_text()
                ).body
                if isinstance(node, (ast.FunctionDef, ast.ClassDef))
            }
            self.assertEqual(set(after), set(symbols))
            for symbol in symbols:
                self.assertEqual(
                    ast.dump(before[symbol]),
                    ast.dump(after[symbol]),
                    f"helper AST changed: {module}.{symbol}",
                )

    def test_cleanup_changes_only_imports_and_geometry_reexport(self):
        for name in STUDIES:
            before = ast.parse(
                subprocess.check_output(
                    ["git", "show", f"{HELPER_BASELINE}:src/neuro/studies/{name}.py"],
                    cwd=ROOT,
                )
            )
            after = ast.parse(_source(name).read_text())
            if name == "cue_time_readout":
                reexport = ast.parse("fidelity, spectrum = geometry_helpers()").body[0]
                removed = [n for n in before.body if ast.dump(n) == ast.dump(reexport)]
                self.assertEqual(len(removed), 1)
                before.body.remove(removed[0])
            if name == "full_trial_transfer":
                before.body = [
                    n
                    for n in before.body
                    if not isinstance(n, (ast.ClassDef, ast.FunctionDef))
                    or n.name not in SAMPLER_MOVED
                ]
                # Moved bodies are independently compared against the pinned baseline above.
            for tree in (before, after):
                tree.body = [
                    n
                    for n in tree.body
                    if not isinstance(n, (ast.Import, ast.ImportFrom))
                ]
            self.assertEqual(ast.dump(before), ast.dump(after), name)

    def test_extracted_io_and_geometry_on_invented_arrays(self):
        import h5py
        import numpy as np

        import neuro.geometry as geometry
        import neuro.raw_io as raw_io
        from neuro.neural_inputs import bin_events, session_from_cell

        with tempfile.TemporaryDirectory() as td:
            ripple = Path(td) / "ripple.mat"
            with h5py.File(ripple, "w") as handle:
                group = handle.create_group("rp/data")
                group["markers"] = [[1, 2, 3], [4, 5, 6]]
                group["timeStamps"] = [[0, 1, 2], [3, 4, 5]]
            events = raw_io.read_ripple_trials(ripple)
            self.assertEqual(raw_io._codes_at(events, 1), (4, 5, 6))
            self.assertEqual(raw_io._times_at(events, 0), (0.0, 1.0, 2.0))
            self.assertIsNone(raw_io._codes_at(events, -1))
            spikes = Path(td) / "spikes.mat"
            with h5py.File(spikes, "w") as handle:
                handle["timestamps"] = [2000.0, 0.0, 1000.0]
            train = raw_io.read_spiketrain(spikes)
            self.assertFalse(train.sorted_input)
            np.testing.assert_array_equal(train.timestamps_seconds, [0.0, 1.0, 2.0])
            np.testing.assert_array_equal(
                raw_io.spikes_in_window(train.timestamps_seconds, 0.0, 2.0), [0.0, 1.0]
            )
        counts, exposure, omitted = bin_events([0.0, 0.25, 1.25], 1.5, 0.5)
        np.testing.assert_array_equal(counts, [2.0, 0.0])
        np.testing.assert_array_equal(exposure, [0.5, 0.5])
        self.assertEqual(omitted, 1)
        self.assertEqual(session_from_cell("S1/A/c0"), "S1_A")
        self.assertEqual(raw_io._csv_value(1.23456789123), "1.23456789")
        rng = np.random.default_rng(42)
        points = rng.normal(size=(24, 3))
        fidelity = geometry.fidelity(points, points.copy(), np.repeat(np.arange(12), 2))
        self.assertAlmostEqual(fidelity["distance_spearman"], 1.0)
        self.assertEqual(fidelity["knn10_overlap"], 1.0)
        self.assertIsNone(geometry.spectrum(np.zeros((24, 3)))["participation_ratio"])

    def test_package_has_no_script_imports_or_path_bootstrap(self):
        self.assertFalse((ROOT / "src/neuro/legacy_adapters.py").exists())
        for path in (ROOT / "src/neuro").rglob("*.py"):
            for node in ast.walk(ast.parse(path.read_text())):
                if isinstance(node, ast.ImportFrom):
                    self.assertFalse(
                        (node.module or "").startswith("scripts"), str(path)
                    )
                if isinstance(node, ast.Import):
                    self.assertFalse(
                        any(a.name.startswith("scripts") for a in node.names), str(path)
                    )
                if isinstance(node, ast.Attribute):
                    self.assertNotEqual(ast.unparse(node), "sys.path", str(path))

    def test_shared_bookkeeping_and_nested_source_snapshots(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            ensure_fresh_dir(root / "fresh")
            with self.assertRaisesRegex(RuntimeError, "overwrite"):
                ensure_fresh_dir(root / "fresh")
            data = root / "invented.txt"
            data.write_bytes(b"invented-source")
            self.assertEqual(
                sha256_file(data), hashlib.sha256(data.read_bytes()).hexdigest()
            )
            check_deadline(None)
            with self.assertRaisesRegex(RuntimeError, "deadline"):
                check_deadline(0)
            for name in STUDIES:
                paths = study_sources(_source(name))
                destination = root / name
                snapshot_sources(destination, paths)
                for relative, path in paths.items():
                    self.assertEqual(
                        (destination / relative).read_bytes(), path.read_bytes()
                    )
                self.assertIn("src/neuro/studies/full_trial_transfer.py", paths)
                self.assertIn(f"src/neuro/studies/{name}.py", paths)
                self.assertNotIn("src/neuro/legacy_adapters.py", paths)
                for module in ("raw_io", "neural_inputs", "cebra_solver"):
                    self.assertIn(f"src/neuro/{module}.py", paths)
                self.assertEqual(
                    "src/neuro/geometry.py" in paths, name == "cue_time_readout"
                )
                self.assertEqual(
                    {key for key in paths if key.startswith("scripts/")},
                    {
                        "scripts/__init__.py",
                        "scripts/cebra_full_trial_transfer.py",
                        f"scripts/cebra_{name}.py",
                    },
                )
                self.assertIn("src/neuro/_cebra_sampling.py", paths)
                self.assertIn("src/neuro/execution.py", paths)
                self.assertIn("src/neuro/provenance.py", paths)
                self.assertNotIn("scripts/place195_v8b_v9_cebra.py", paths)
            with self.assertRaisesRegex(ValueError, "escapes"):
                snapshot_sources(root / "snap", {"../escape": data})
            self.assertFalse((root / "escape").exists())

    def test_cold_import_identity_legacy_pickle_and_no_private_access(self):
        with tempfile.TemporaryDirectory() as td:
            env = {
                **os.environ,
                "PYTHONPATH": str(ROOT / "src"),
                "PYTHONDONTWRITEBYTECODE": "1",
                "MPLCONFIGDIR": td,
                "OMP_NUM_THREADS": "2",
                "OPENBLAS_NUM_THREADS": "2",
            }
            guard = (
                "import sys, os\n"
                f"protected = {[str(ROOT / 'data'), str(ROOT / 'outputs')]!r}\n"
                "def audit(event, args):\n"
                "    if event == 'open' and isinstance(args[0], (str, bytes, os.PathLike)):\n"
                "        path = os.path.abspath(os.fsdecode(args[0]))\n"
                "        if any(path == p or path.startswith(p + '/') for p in protected):\n"
                "            raise AssertionError('private input access: ' + path)\n"
                "sys.addaudithook(audit)\n"
                "from sklearn.decomposition import PCA\n"
                "from sklearn.discriminant_analysis import LinearDiscriminantAnalysis\n"
                "from sklearn.linear_model import LogisticRegression\n"
                "from sklearn.preprocessing import StandardScaler\n"
                "from sklearn.svm import SVC\n"
                "import torch\n"
                "def forbid(*args, **kwargs):\n"
                "    raise AssertionError('fit/optimization during cold import')\n"
                "for cls in (PCA, LinearDiscriminantAnalysis, LogisticRegression, StandardScaler, SVC):\n"
                "    for method in ('fit', 'fit_transform'):\n"
                "        if hasattr(cls, method): setattr(cls, method, forbid)\n"
                "torch.optim.Adam.step = forbid\n"
                "torch.optim.Optimizer.step = forbid\n"
            )
            for name in STUDIES:
                package_only = guard + (
                    "import importlib\n"
                    "before_path = list(sys.path)\n"
                    f"new = importlib.import_module('neuro.studies.{name}')\n"
                    "assert sys.path == before_path\n"
                    "assert not any(n == 'scripts' or n.startswith('scripts.') for n in sys.modules)\n"
                )
                subprocess.run(
                    [sys.executable, "-B", "-c", package_only],
                    cwd=td,
                    env=env,
                    check=True,
                )
                for first in (
                    f"neuro.studies.{name}",
                    f"scripts.cebra_{name}",
                    f"cebra_{name}",
                ):
                    code = guard + (
                        "import importlib, pickle\n"
                        f"sys.path[:0] = [{str(ROOT)!r}, {str(ROOT / 'scripts')!r}]\n"
                        f"first = importlib.import_module({first!r})\n"
                        f"new = importlib.import_module('neuro.studies.{name}')\n"
                        f"old = importlib.import_module('scripts.cebra_{name}')\n"
                        f"bare = importlib.import_module('cebra_{name}')\n"
                        "assert first is new is old is bare\n"
                        "assert old.main is new.main\n"
                        "old._migration_patch = object()\n"
                        "assert new._migration_patch is old._migration_patch\n"
                        "del old._migration_patch\n"
                        "for attr, obj in vars(new).items():\n"
                        "    if isinstance(obj, type) and obj.__module__ == new.__name__:\n"
                        "        legacy = ('cscripts.cebra_' + new.__name__.rsplit('.', 1)[-1] + '\\n' + attr + '\\n.').encode()\n"
                        "        assert pickle.loads(legacy) is obj\n"
                        "from pathlib import Path\n"
                        "declared = {p.resolve() for p in new.helper_paths().values()}\n"
                        "assert Path(new.__file__).resolve() in declared\n"
                        "for module_name, module in list(sys.modules.items()):\n"
                        "    if module_name == 'scripts' or module_name.startswith(('scripts.', 'neuro')):\n"
                        "        path = getattr(module, '__file__', None)\n"
                        "        if path is not None:\n"
                        "            assert Path(path).resolve() in declared, (module_name, path)\n"
                        "hashes = new.helper_hashes()\n"
                        "assert all(new.sha256_file(path) == hashes[key] for key, path in new.helper_paths().items())\n"
                        "from neuro.studies import full_trial_transfer as ft\n"
                        "assert ft.WORKTREE_ROOT == Path(" + repr(str(ROOT)) + ")\n"
                    )
                    first_env = dict(env)
                    if first.startswith("scripts."):
                        first_env["PYTHONPATH"] = (
                            str(ROOT) + os.pathsep + env["PYTHONPATH"]
                        )
                    subprocess.run(
                        [sys.executable, "-B", "-c", code],
                        cwd=td,
                        env=first_env,
                        check=True,
                    )
                # The source closure must import without falling back to this checkout.
                snapshot = Path(td) / name
                snapshot_sources(snapshot, study_sources(_source(name)))
                snapshot_env = {**env, "PYTHONPATH": str(snapshot / "src")}
                code = guard + (
                    "import importlib\nfrom pathlib import Path\n"
                    f"new = importlib.import_module('neuro.studies.{name}')\n"
                    "assert not any(n == 'scripts' or n.startswith('scripts.') for n in sys.modules)\n"
                    f"snapshot = Path({str(snapshot)!r})\n"
                    "sys.path.insert(0, str(snapshot))\n"
                    f"old = importlib.import_module('scripts.cebra_{name}')\n"
                    "assert new is old\n"
                    "for module_name, module in list(sys.modules.items()):\n"
                    "    if module_name == 'scripts' or module_name.startswith(('scripts.', 'neuro')):\n"
                    "        path = getattr(module, '__file__', None)\n"
                    "        if path is not None:\n"
                    "            assert Path(path).is_relative_to(snapshot), (module_name, path)\n"
                )
                subprocess.run(
                    [sys.executable, "-B", "-c", code],
                    cwd=td,
                    env=snapshot_env,
                    check=True,
                )
            lightweight = (
                "import sys, neuro, neuro.studies, neuro.execution, neuro.provenance\n"
                "assert not {'numpy', 'torch', 'cebra', 'h5py'} & sys.modules.keys()\n"
            )
            subprocess.run(
                [sys.executable, "-S", "-B", "-c", lightweight],
                cwd=td,
                env=env,
                check=True,
            )

    def test_legacy_module_direct_and_package_cli_help(self):
        with tempfile.TemporaryDirectory() as td:
            env = {
                **os.environ,
                "PYTHONPATH": str(ROOT) + os.pathsep + str(ROOT / "src"),
                "PYTHONDONTWRITEBYTECODE": "1",
                "MPLCONFIGDIR": td,
                "OMP_NUM_THREADS": "2",
                "OPENBLAS_NUM_THREADS": "2",
            }
            for name in STUDIES:
                for invocation in (
                    ("-m", f"scripts.cebra_{name}"),
                    (str(ROOT / f"scripts/cebra_{name}.py"),),
                    ("-m", f"neuro.studies.{name}"),
                ):
                    result = subprocess.run(
                        [sys.executable, "-B", *invocation, "--help"],
                        cwd=td,
                        env=env,
                        text=True,
                        capture_output=True,
                        check=True,
                    )
                    self.assertIn("usage:", result.stdout)
                    self.assertIn("verify", result.stdout)


if __name__ == "__main__":
    unittest.main()
