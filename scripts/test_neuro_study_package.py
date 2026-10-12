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
STUDIES = ("full_trial_transfer", "endpoint_time_readout", "cue_time_readout")
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
            statement for statement in node.body
            if not (
                isinstance(statement, ast.For)
                and ast.unparse(statement.iter) == "helper_paths().items()"
            ) and not (
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
                node.name: node for node in ast.parse(original).body
                if isinstance(node, (ast.FunctionDef, ast.ClassDef))
            }
            after = {
                node.name: node for node in ast.parse(_source(name).read_text()).body
                if isinstance(node, (ast.FunctionDef, ast.ClassDef))
            }
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

    def test_shared_bookkeeping_and_nested_source_snapshots(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            ensure_fresh_dir(root / "fresh")
            with self.assertRaisesRegex(RuntimeError, "overwrite"):
                ensure_fresh_dir(root / "fresh")
            data = root / "invented.txt"
            data.write_bytes(b"invented-source")
            self.assertEqual(sha256_file(data), hashlib.sha256(data.read_bytes()).hexdigest())
            check_deadline(None)
            with self.assertRaisesRegex(RuntimeError, "deadline"):
                check_deadline(0)
            for name in STUDIES:
                paths = study_sources(_source(name))
                destination = root / name
                snapshot_sources(destination, paths)
                for relative, path in paths.items():
                    self.assertEqual((destination / relative).read_bytes(), path.read_bytes())
                self.assertIn("src/neuro/studies/full_trial_transfer.py", paths)
                self.assertIn(f"src/neuro/studies/{name}.py", paths)
                self.assertIn("src/neuro/legacy_adapters.py", paths)
                self.assertIn("src/neuro/execution.py", paths)
                self.assertIn("src/neuro/provenance.py", paths)
                self.assertIn("scripts/place195_v8b_v9_cebra.py", paths)
            with self.assertRaisesRegex(ValueError, "escapes"):
                snapshot_sources(root / "snap", {"../escape": data})
            self.assertFalse((root / "escape").exists())

    def test_cold_import_identity_legacy_pickle_and_no_private_access(self):
        with tempfile.TemporaryDirectory() as td:
            env = {
                **os.environ, "PYTHONPATH": str(ROOT / "src"),
                "PYTHONDONTWRITEBYTECODE": "1", "MPLCONFIGDIR": td,
                "OMP_NUM_THREADS": "2", "OPENBLAS_NUM_THREADS": "2",
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
            )
            for name in STUDIES:
                for first in (f"neuro.studies.{name}", f"scripts.cebra_{name}", f"cebra_{name}"):
                    code = guard + (
                        "import importlib, pickle\n"
                        f"sys.path.insert(0, {str(ROOT / 'scripts')!r})\n"
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
                        first_env["PYTHONPATH"] = str(ROOT) + os.pathsep + env["PYTHONPATH"]
                    subprocess.run([sys.executable, "-B", "-c", code], cwd=td, env=first_env, check=True)
                # The source closure must import without falling back to this checkout.
                snapshot = Path(td) / name
                snapshot_sources(snapshot, study_sources(_source(name)))
                snapshot_env = {**env, "PYTHONPATH": str(snapshot / "src")}
                code = guard + (
                    "import importlib\nfrom pathlib import Path\n"
                    f"new = importlib.import_module('neuro.studies.{name}')\n"
                    f"old = importlib.import_module('scripts.cebra_{name}')\n"
                    "assert new is old\n"
                    f"snapshot = Path({str(snapshot)!r})\n"
                    "for module_name, module in list(sys.modules.items()):\n"
                    "    if module_name == 'scripts' or module_name.startswith(('scripts.', 'neuro')):\n"
                    "        path = getattr(module, '__file__', None)\n"
                    "        if path is not None:\n"
                    "            assert Path(path).is_relative_to(snapshot), (module_name, path)\n"
                )
                subprocess.run([sys.executable, "-B", "-c", code], cwd=td, env=snapshot_env, check=True)
            lightweight = (
                "import sys, neuro, neuro.studies, neuro.execution, neuro.provenance\n"
                "assert not {'numpy', 'torch', 'cebra', 'h5py'} & sys.modules.keys()\n"
            )
            subprocess.run([sys.executable, "-S", "-B", "-c", lightweight], cwd=td, env=env, check=True)

    def test_legacy_module_direct_and_package_cli_help(self):
        with tempfile.TemporaryDirectory() as td:
            env = {
                **os.environ, "PYTHONPATH": str(ROOT) + os.pathsep + str(ROOT / "src"),
                "PYTHONDONTWRITEBYTECODE": "1", "MPLCONFIGDIR": td,
                "OMP_NUM_THREADS": "2", "OPENBLAS_NUM_THREADS": "2",
            }
            for name in STUDIES:
                for invocation in (
                    ("-m", f"scripts.cebra_{name}"),
                    (str(ROOT / f"scripts/cebra_{name}.py"),),
                    ("-m", f"neuro.studies.{name}"),
                ):
                    result = subprocess.run(
                        [sys.executable, "-B", *invocation, "--help"],
                        cwd=td, env=env, text=True, capture_output=True, check=True,
                    )
                    self.assertIn("usage:", result.stdout)
                    self.assertIn("verify", result.stdout)


if __name__ == "__main__":
    unittest.main()
