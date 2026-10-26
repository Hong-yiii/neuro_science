"""Invented-only compact IO/policy checks; no native inputs, model fits or downloads."""

from __future__ import annotations

import copy
import io
import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import h5py  # type: ignore[reportMissingImports]
import numpy as np
from scipy.io import savemat

from neuro.cue_source import (
    authenticate,
    event_matrix,
    exact_bins,
    eye_observed,
    load_arrays,
    reconstruct_compact,
    unity_trials,
)
from neuro.cue_source_export import (
    event_arrays,
    regular,
    spike_arrays,
    unity_arrays,
    write_npz,
)
from neuro.notebook_artifacts import no_fitting, validate_kernel_identity
from neuro.notebook_inputs import demo_configuration, inspect_inputs, load_inputs
from neuro.place195 import (
    MetadataSelection,
    _index,
    reconstruct_neural,
    select_metadata,
    select_tables,
)
from neuro.pseudopopulation import materialize, sample_plan
from scripts.test_fresh_notebooks import invented_ledgers


class CompactTests(unittest.TestCase):
    def test_spikes_v5_v73_exact_shape_order_duplicates_precision_and_determinism(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            values = np.array([[1000.123456789123], [2.0], [2.0], [0.0]])
            for format_name in ("v5", "v73"):
                path = root / (format_name + ".mat")
                arrays = {
                    "timestamps": values,
                    "components": np.array([[1.0]]),
                    "reference": np.array([[65]], dtype=np.uint16),
                }
                if format_name == "v5":
                    savemat(path, arrays)
                else:
                    with h5py.File(path, "w") as handle:
                        for key, value in arrays.items():
                            handle[key] = value
                actual, _ = spike_arrays(path)
                np.testing.assert_array_equal(actual["timestamps"], values)
                self.assertEqual(actual["timestamps"].dtype, values.dtype)
                a, b = root / (format_name + "a.npz"), root / (format_name + "b.npz")
                write_npz(a, actual)
                write_npz(b, actual)
                self.assertEqual(a.read_bytes(), b.read_bytes())
                np.testing.assert_array_equal(load_arrays(a)["timestamps"], values)
            with self.assertRaisesRegex(ValueError, "object"):
                write_npz(root / "object.npz", {"x": np.array([{}], dtype=object)})

    def test_unity_all_deltas_startup_orphan_headers_and_exact_tokens(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "unity.txt"
            path.write_text(
                "Version: invented\nTask: test\n84 .1 0 0 0\n0 .123456789123 1 2 3\n11 .2 0 0 0\n21 .3 0 0 0\n31 .4 0 0 0\n12 .5 0 0 0\n"
            )
            arrays, headers = unity_arrays(path)
            self.assertEqual(headers, ["Version: invented", "Task: test"])
            tokens = arrays["timing_tokens"]
            self.assertEqual(tokens[1, 1], b".123456789123")
            codes, times, rows, orphan = unity_trials(tokens.astype(float))
            np.testing.assert_array_equal(codes, [[11, 21, 31]])
            self.assertEqual(times[0, 0], 0.1 + 0.123456789123 + 0.2)
            np.testing.assert_array_equal(rows, [[2, 3, 4]])
            self.assertEqual(orphan, [5])
            self.assertEqual(len(tokens), 6)

    def test_eye_explicit_axes_missing_mask_and_zero_not_missing(self):
        single = np.array([[11], [21], [31]])
        self.assertEqual(event_matrix(single, event_axis=0).shape, (1, 3))
        three = np.arange(9).reshape(3, 3)
        np.testing.assert_array_equal(event_matrix(three, event_axis=0), three.T)
        np.testing.assert_array_equal(event_matrix(three, event_axis=1), three)
        with self.assertRaises(ValueError):
            event_matrix(np.arange(3), event_axis=0)
        arrays = {
            "eye__triggers": np.zeros((3, 4)),
            "eye__missing_idx": np.array([[2, 3], [1, 2]]),
        }
        observed = eye_observed(arrays, {"event_axis": 0})
        self.assertTrue(observed[0].all())  # real zero observation is not missing
        self.assertFalse(observed[1, 0])
        self.assertFalse(observed[2, 1])
        arrays["eye__missing_idx"] = np.array([[0], [1]])
        with self.assertRaisesRegex(ValueError, "bounds"):
            eye_observed(arrays, {"event_axis": 0})
        with tempfile.TemporaryDirectory() as td:
            for alternative in (False, True):
                path = Path(td) / str(alternative)
                with h5py.File(path, "w") as f:
                    if alternative:
                        f["triggers"] = single
                        f["timestamps"] = single * 1000
                        f["missing_idx"] = np.empty((2, 0), dtype=int)
                    else:
                        f["el/data/trial_codes"] = single
                        f["el/data/trial_timestamps"] = single * 1000
                        f["el/data/eye_pos"] = np.zeros((2, 100))
                payload, details = event_arrays(path, "eyelink_markers")
                self.assertNotIn("eye_pos", payload)
                self.assertEqual(details["event_axis"], 0)

    def test_event_empty_semantics_and_optional_raw_sample_rate(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "events.mat"
            with h5py.File(path, "w") as f:
                f["el/data/trial_codes"] = np.array([[11], [21], [31]])
                f["el/data/trial_timestamps"] = np.array([[0], [1000], [2000]])
                empty = f.create_dataset(
                    "el/data/timeouts", data=np.array([0, 0], dtype=np.uint64)
                )
                empty.attrs["MATLAB_empty"] = np.uint8(1)
                empty.attrs["MATLAB_class"] = np.bytes_("double")
                f["rp/data/markers"] = np.array([[11], [21], [31]])
                f["rp/data/timeStamps"] = np.array([[0.0], [1.0], [2.0]])
                f["rp/data/Args/Data/SampleRate"] = np.array([[30000.0]])
            arrays, details = event_arrays(path, "eyelink_markers")
            np.testing.assert_array_equal(
                arrays["timeouts"], np.array([0, 0], dtype=np.uint64)
            )
            self.assertEqual(
                details["attributes"]["timeouts"],
                {"MATLAB_empty": 1, "MATLAB_class": "double"},
            )
            arrays, details = event_arrays(path, "ripple_markers")
            np.testing.assert_array_equal(arrays["Args__Data__SampleRate"], [[30000.0]])
            self.assertEqual(
                details["origins"]["Args__Data__SampleRate"],
                "rp/data/Args/Data/SampleRate",
            )

    def test_npy_shape_is_bounded_before_any_array_allocation(self):
        with tempfile.TemporaryDirectory() as td:
            for shape, dtype, body in (
                ((2**40,), "<f8", b""),
                ((2**40,), "|S0", b""),
                ((2,), "<f8", b"\0" * 8),
                ((1,), "|O", b"\0" * 8),
                ((-1,), "<f8", b""),
            ):
                header = io.BytesIO()
                np.lib.format.write_array_header_1_0(
                    header, {"shape": shape, "descr": dtype, "fortran_order": False}
                )
                path = Path(td) / "bad.npz"
                with zipfile.ZipFile(path, "w") as archive:
                    archive.writestr("x.npy", header.getvalue() + body)
                with patch("neuro.cue_source.np.load") as load:
                    with self.assertRaisesRegex(ValueError, "NPY shape"):
                        load_arrays(path)
                    load.assert_not_called()

    def test_dataset_pin_rebinding_fails_before_reinspection(self):
        selection = MetadataSelection(
            {}, {"dataset_manifest_sha256": "original"}, {}, (), (), (), (), {}
        )
        selection.manifest["dataset_manifest_sha256"] = "changed-spikes-and-manifest"
        with patch("neuro.cue_source.inspect_compact") as inspect:
            with self.assertRaisesRegex(ValueError, "fingerprint changed"):
                reconstruct_compact(selection, interpret_neural=True)
            inspect.assert_not_called()
        with tempfile.TemporaryDirectory() as td:
            manifest, _, _ = invented_ledgers(Path(td))
            legacy = select_metadata(manifest)
            legacy.manifest["inputs"]["events"]["sha256"] = "rebound"
            with self.assertRaisesRegex(ValueError, "fingerprint changed"):
                reconstruct_neural(legacy, interpret_neural=True)

    def test_exact_absolute_boundaries_duplicate_counts_zeros_and_tail(self):
        # Input order deliberately nonmonotonic; exact boundaries including [1s,end).
        timestamps = np.array([1100.0, 1000.0, 1000.0, 1200.0, 2000.0, 2100.0, 2200.0])
        counts, tail, total = exact_bins(timestamps, 1.0, 2.2, np.arange(11) / 10)
        np.testing.assert_array_equal(counts[:3], [2, 1, 1])
        self.assertEqual((int(counts.sum()), tail, total), (4, 2, 6))
        empty, tail, total = exact_bins(np.array([]), 1.0, 2.2, np.arange(11) / 10)
        self.assertEqual((empty.sum(), tail, total), (0, 0, 0))

    def test_root_hash_schema_duplicate_and_bounded_artifact_read(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "safe").write_text("x")
            (root / "link").symlink_to(root / "safe")
            for relative in ("../safe", "/safe", "link", "absent"):
                with self.assertRaises(ValueError):
                    regular(root, relative)
            (root / "manifest.json").write_text("{}")
            with self.assertRaisesRegex(ValueError, "authentication"):
                authenticate({"data_root": td, "dataset_manifest_sha256": "wrong"})
            path = root / "duplicate.npz"
            with zipfile.ZipFile(path, "w") as z:
                z.writestr("x.npy", b"")
                z.writestr("x.npy", b"")
            with self.assertRaisesRegex(ValueError, "duplicate"):
                load_arrays(path)
            with patch("neuro.cue_source.zipfile.ZipFile") as archive:
                archive.return_value.__enter__.return_value.infolist.return_value = [
                    SimpleNamespace(filename="x.npy", file_size=513 * 1024**2)
                ]
                with self.assertRaisesRegex(ValueError, "oversized"):
                    load_arrays(path)

    def test_shared_selector_exact_assignments_embargo_support_and_reuse(self):
        with tempfile.TemporaryDirectory() as td, no_fitting():
            manifest, tables, paths = invented_ledgers(Path(td))
            legacy = select_metadata(manifest)
            shared = select_tables(
                manifest,
                paths=paths,
                outer=_index(tables["outer_splits"], "source_trial_id"),
                trials_all=_index(tables["trials"], "source_trial_id"),
                units_by_id=_index(tables["units"], "cell_id"),
                frozen=_index(tables["inner_splits"], "source_trial_id"),
            )
            self.assertEqual(shared, legacy)
            self.assertEqual(shared.audit["contributor_overlap"], 0)
            bad = copy.deepcopy(tables["inner_splits"])
            bad[0]["split"] = "test"
            with self.assertRaisesRegex(ValueError, "frozen assignment"):
                select_tables(
                    manifest,
                    paths=paths,
                    outer=_index(tables["outer_splits"], "source_trial_id"),
                    trials_all=_index(tables["trials"], "source_trial_id"),
                    units_by_id=_index(tables["units"], "cell_id"),
                    frozen=_index(bad, "source_trial_id"),
                )
            data, _ = load_inputs(inspect_inputs(demo_configuration()))
            assembly = materialize(
                data, sample_plan(data, split_id="train", rows_per_condition=16, seed=0)
            )
            np.testing.assert_array_equal(
                materialize(data, assembly.plan).values, assembly.values
            )
            self.assertLess(
                len({sid for r in assembly.plan.rows for sid in r.source_ids}),
                sum(len(r.source_ids) for r in assembly.plan.rows),
            )

    def test_compact_gates_fail_closed_and_mutable_selection_reauthenticated(self):
        config = {**demo_configuration(), "mode": "compact"}
        with self.assertRaisesRegex(ValueError, "pinned kernel"):
            validate_kernel_identity(config)
        selection = MetadataSelection({}, {}, {}, (), (), (), (), {})
        with self.assertRaises(PermissionError):
            reconstruct_compact(selection)
        with (
            patch(
                "neuro.cue_source.inspect_compact",
                return_value=SimpleNamespace(manifest={"changed": True}),
            ),
            self.assertRaisesRegex(ValueError, "forged"),
        ):
            reconstruct_compact(selection, interpret_neural=True)
        from scripts.execute_fresh_notebooks import execute

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            manifest = root / "config.json"
            manifest.write_text(json.dumps(config))
            from neuro.place195 import file_hash

            args = SimpleNamespace(
                output=root / "out",
                timeout_seconds=5,
                memory_gib=1,
                manifest=manifest,
                manifest_sha256=file_hash(manifest),
                allow_biological=False,
            )
            with self.assertRaisesRegex(PermissionError, "not authorized"):
                execute(args)


if __name__ == "__main__":
    unittest.main()
