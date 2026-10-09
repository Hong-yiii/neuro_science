# pyright: reportMissingImports=false
"""Invented-data checks for the endpoint cue-time readout runner."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np

from scripts import cebra_endpoint_time_readout as ep


def _tiny_cohort() -> ep.EndpointCohort:
    sessions = ("S1_A", "S2_A")
    cells = ["S1/A/c0", "S1/A/c1", "S2/A/c0", "S2/A/c1"]
    metas: list[ep.EndpointSource] = []
    source_ids: list[str] = []
    counts_rows = []
    masks = []
    exposures = []
    for session in sessions:
        for split, stored in (("train", "train"), ("development", "validation")):
            for label_id, label in enumerate(ep.PAIR_LABELS):
                sid = f"{session}_{split}_{label.replace('->', '_')}"
                source_ids.append(sid)
                metas.append(
                    ep.EndpointSource(sid, session, split, stored, label, label_id + 1)
                )
                row = np.full((len(cells), ep.CUE_BINS), np.nan, dtype=np.float32)
                mask = np.zeros(len(cells), dtype=bool)
                for ci, cell in enumerate(cells):
                    if ep.session_from_cell(cell) == session:
                        row[ci] = label_id + np.arange(ep.CUE_BINS, dtype=np.float32)
                        mask[ci] = True
                counts_rows.append(row)
                masks.append(mask)
                exposures.append(np.full(ep.CUE_BINS, ep.BIN_WIDTH_S, dtype=np.float32))
    return ep.EndpointCohort(
        counts=np.asarray(counts_rows, dtype=np.float32),
        observed=np.asarray(masks, dtype=bool),
        exposure=np.asarray(exposures, dtype=np.float32),
        source_ids=source_ids,
        cells=cells,
        metas=metas,
        source_index={sid: idx for idx, sid in enumerate(source_ids)},
    )


def _write_tiny_accepted_root(root: Path, cohort: ep.EndpointCohort) -> None:
    np.savez_compressed(
        root / "source_tensor.npz",
        counts=cohort.counts,
        observed=cohort.observed,
        exposure=cohort.exposure,
        source_ids=np.asarray(cohort.source_ids),
        cells=np.asarray(cohort.cells),
    )
    ep.write_csv(
        root / "source_splits.csv",
        [
            {
                "source_trial_id": meta.source_trial_id,
                "session_id": meta.session_id,
                "split": meta.stored_split,
                "label": meta.label,
                "original_split": "train",
                "trial_index": meta.trial_index or "",
            }
            for meta in cohort.metas
        ],
    )
    ep.write_csv(root / "source_support.csv", ep.source_support_rows(cohort))
    ep.write_json(root / "source_audit.json", {"invented": True})
    ep.write_json(root / "inputs.json", {"invented": True})
    for seed in ep.SEEDS:
        train, dev = ep.assemble_world_seed(cohort, seed=seed)
        seed_dir = root / "observed" / f"seed{seed}"
        seed_dir.mkdir(parents=True)
        np.savez_compressed(
            seed_dir / "pseudo_arrays.npz",
            X_train=train.X_cue,
            y_train=train.y_pair,
            X_validation=dev.X_cue,
            y_validation=dev.y_pair,
        )
        rows = []
        for row in train.manifest + dev.manifest:
            copied = dict(row)
            copied.pop("row_id", None)
            rows.append(copied)
        ep.write_csv(seed_dir / "pseudo_components.csv", rows)
    manifest = {
        str(path.relative_to(root)): ep.sha256_file(path)
        for path in sorted(root.rglob("*"))
        if path.is_file() and path.name != "artifact_hashes.json"
    }
    ep.write_json(root / "artifact_hashes.json", manifest)


def _tiny_nav(
    cohort: ep.EndpointCohort, path: Path, *, variable_bins: bool = False
) -> ep.EndpointNavData:
    train = [meta for meta in cohort.metas if meta.split == "train"]
    counts_chunks = []
    exposure_chunks = []
    mask_chunks = []
    offsets = [0]
    cell_sessions = [ep.session_from_cell(cell) for cell in cohort.cells]
    bins_per_source = []
    for source_index, meta in enumerate(train):
        bins = 3 + source_index % 7 if variable_bins else 3
        bins_per_source.append(bins)
        counts = np.full((bins, len(cohort.cells)), np.nan, dtype=np.float32)
        mask = np.zeros((bins, len(cohort.cells)), dtype=bool)
        for ci, session in enumerate(cell_sessions):
            if session == meta.session_id:
                counts[:, ci] = (
                    np.arange(bins, dtype=np.float32) + ep.PAIR_TO_INT[meta.label]
                )
                mask[:, ci] = True
        counts_chunks.append(counts)
        exposure_chunks.append(np.full(bins, ep.BIN_WIDTH_S, dtype=np.float32))
        mask_chunks.append(mask)
        offsets.append(offsets[-1] + bins)
    np.savez_compressed(
        path,
        nav_counts_flat=np.concatenate(counts_chunks),
        nav_exposure_flat=np.concatenate(exposure_chunks),
        nav_observed_mask_flat=np.concatenate(mask_chunks),
        nav_offsets=np.asarray(offsets, dtype=np.int64),
        nav_n_bins=np.asarray(bins_per_source, dtype=np.int64),
        source_trial_ids=np.asarray([m.source_trial_id for m in train]),
        source_session_ids=np.asarray([m.session_id for m in train]),
        source_labels=np.asarray([m.label for m in train]),
        source_splits=np.asarray(["train"] * len(train)),
        source_trial_indices=np.asarray(
            [m.trial_index or 0 for m in train], dtype=np.int64
        ),
        cell_ids=np.asarray(cohort.cells),
        bin_width_s=np.asarray([ep.BIN_WIDTH_S], dtype=np.float32),
    )
    return ep.load_nav_data(path, cohort)


class EndpointTimeReadoutTests(unittest.TestCase):
    def test_artifact_hashes_and_observed_assembly_parity_on_invented_root(self):
        cohort = _tiny_cohort()
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _write_tiny_accepted_root(root, cohort)
            summary = ep.verify_accepted_endpoint_artifacts(root)
            self.assertGreaterEqual(summary["checked_files"], 11)
            loaded = ep.load_endpoint_cohort(root, strict_expected=False)
            self.assertEqual(
                ep.verify_observed_assembly_parity(loaded, root)["status"], "passed"
            )
            manifest_path = root / "observed" / "seed0" / "pseudo_components.csv"
            manifest_rows = ep.read_csv(manifest_path)
            ep.write_csv(
                manifest_path,
                [
                    {
                        key: value
                        for key, value in row.items()
                        if key != "source_trial_id"
                    }
                    for row in manifest_rows
                ],
            )
            with self.assertRaisesRegex(RuntimeError, "manifest schema"):
                ep.verify_observed_assembly_parity(loaded, root)
            (root / "source_audit.json").write_text("tampered")
            with self.assertRaises(RuntimeError):
                ep.verify_accepted_endpoint_artifacts(root)

    def test_run_hash_manifest_rejects_unmanifested_files(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "evidence.txt").write_text("included")
            nested = root / "nested"
            nested.mkdir()
            (nested / "hash_manifest.json").write_text("included nested file")
            manifest = ep.write_hash_manifest(root)
            self.assertEqual(
                set(manifest), {"evidence.txt", "nested/hash_manifest.json"}
            )
            self.assertEqual(ep.verify_hash_manifest(root)["status"], "passed")
            (root / "extra.txt").write_text("not manifested")
            with self.assertRaisesRegex(RuntimeError, "file-set mismatch"):
                ep.verify_hash_manifest(root)

    def test_read_jsonl_rejects_malformed_rows_with_line_number(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "metrics.jsonl"
            path.write_text('{"ok": true}\n{invalid}\n')
            with self.assertRaisesRegex(RuntimeError, "JSONL row 2"):
                ep.read_jsonl(path)

    def test_window_feature_order_and_direct_endpoint_targets(self):
        raw_cells = np.arange(2 * 4 * ep.CUE_BINS).reshape(2, 4, ep.CUE_BINS)
        raw_flat = raw_cells.reshape(2, 4 * ep.CUE_BINS)
        np.testing.assert_array_equal(
            ep.extract_window_features("raw", raw_flat, "bin03", cell_count=4),
            raw_cells[:, :, 3],
        )
        latent = np.arange(2 * ep.CUE_BINS * ep.CEBRA_DIM).reshape(
            2, ep.CUE_BINS * ep.CEBRA_DIM
        )
        np.testing.assert_array_equal(
            ep.extract_window_features("cebra_cue", latent, "bin02", cell_count=4),
            latent.reshape(2, ep.CUE_BINS, ep.CEBRA_DIM)[:, 2, :],
        )
        y = np.array([ep.PAIR_TO_INT["1->2"], ep.PAIR_TO_INT["6->5"]])
        np.testing.assert_array_equal(ep.target_labels(y, "start6"), np.array([1, 6]))
        np.testing.assert_array_equal(ep.target_labels(y, "goal6"), np.array([2, 5]))

    def test_pair_label_shuffle_is_within_session_split_and_not_endpoint_independent(
        self,
    ):
        metas = [
            ep.EndpointSource(f"s{i}", "S1_A", "train", "train", label)
            for i, label in enumerate(("1->2", "2->3", "3->4", "4->5"))
        ]
        shuffled, info = ep.shuffle_pair_labels_within_session_split(metas, seed=50000)
        self.assertEqual(info["group_fields"], ["session_id", "inner_split"])
        self.assertEqual(sorted(shuffled.values()), sorted(m.label for m in metas))
        for label in shuffled.values():
            pair_id = ep.PAIR_TO_INT[label]
            self.assertEqual(label, f"{ep.PAIRS[pair_id][0]}->{ep.PAIRS[pair_id][1]}")

    def test_training_nav_allowlist_rejects_development_sources(self):
        cohort = _tiny_cohort()
        train_id = next(m.source_trial_id for m in cohort.metas if m.split == "train")
        dev_id = next(
            m.source_trial_id for m in cohort.metas if m.split == "development"
        )
        self.assertEqual(
            ep.assert_training_nav_allowlist(cohort, [train_id]), [train_id]
        )
        with self.assertRaisesRegex(RuntimeError, "development"):
            ep.assert_training_nav_allowlist(cohort, [dev_id])

    def test_inner_training_filter_follows_outer_gate(self):
        cohort = _tiny_cohort()
        allowed = {
            meta.source_trial_id for meta in cohort.metas if meta.split == "train"
        }
        outer_train = allowed | {"outer_train_only_1", "outer_train_only_2"}
        rows = [
            {"source_trial_id": source_id, "split": "train"}
            for source_id in sorted(outer_train)
        ]
        selected = ep.select_training_trial_rows(rows, allowed, outer_train)
        self.assertEqual(set(selected), allowed)
        self.assertGreater(len(outer_train), len(allowed))
        with self.assertRaisesRegex(RuntimeError, "outer-training split-gate"):
            ep.select_training_trial_rows(rows[:-1], allowed, outer_train)
        with self.assertRaisesRegex(RuntimeError, "duplicate outer-training"):
            ep.select_training_trial_rows(rows + rows[:1], allowed, outer_train)
        with self.assertRaisesRegex(RuntimeError, "non-training"):
            ep.select_training_trial_rows(
                [dict(rows[0], split="validation"), *rows[1:]], allowed, outer_train
            )

    def test_imported_cue_windows_match_raw_marker_identity_and_times(self):
        source_id = "S1_A_trial002"
        meta = ep.EndpointSource(source_id, "S1_A", "train", "train", "1->2", 2)
        rows = [
            {
                "source_trial_id": source_id,
                "session_id": "S1_A",
                "trial_index": "2",
                "cell_id": cell,
                "split": "train",
                "cue_window_start_ripple_s": "1.25",
                "cue_window_end_ripple_s": "2.25",
            }
            for cell in ("S1/A/c0", "S1/A/c1")
        ]
        expected = {source_id: ("S1/A/c0", "S1/A/c1")}
        windows = ep.index_training_cue_windows(rows, expected_cells_by_source=expected)
        ep.verify_raw_cue_window(meta, (1.25, 2.25, 4.0), windows[source_id])
        with self.assertRaisesRegex(RuntimeError, "time mismatch"):
            ep.verify_raw_cue_window(meta, (1.5, 2.5, 4.0), windows[source_id])
        with self.assertRaisesRegex(RuntimeError, "incomplete"):
            ep.index_training_cue_windows(rows[:1], expected_cells_by_source=expected)
        rows[1]["cue_window_start_ripple_s"] = "1.5"
        with self.assertRaisesRegex(RuntimeError, "disagree"):
            ep.index_training_cue_windows(rows, expected_cells_by_source=expected)

    def test_raw_cue_times_match_exact_importer_precision(self):
        meta = ep.EndpointSource("source", "S1_A", "train", "train", "1->2", 4)
        raw = (36.1161, 37.14013333333333, 51.0078)
        windows = {"S1/A/c0": ("S1_A", 4, 36.1161, 37.1401333)}
        ep.verify_raw_cue_window(meta, raw, windows)
        with self.assertRaisesRegex(RuntimeError, "time mismatch"):
            ep.verify_raw_cue_window(meta, (raw[0], raw[1] + 1e-5, raw[2]), windows)

    def test_accepted_csv_precision_controls_cue_boundary_recount(self):
        events = np.array([np.nextafter(0.2, 0.0)])
        native, _, _ = ep.bin_events(events, 1.0, 0.1)
        serialized = [ep.parse_float(ep.imported_csv_value(t)) for t in events]
        accepted, _, _ = ep.bin_events(serialized, 1.0, 0.1)
        self.assertEqual(native[1], 1)
        self.assertEqual(accepted[2], 1)
        self.assertEqual(native.sum(), accepted.sum())

    def test_ripple_codes_accept_imported_space_separated_triplets(self):
        for text in ("16 26 36", "16,26,36", "16; 26; 36"):
            self.assertEqual(ep.parse_ripple_codes(text), (16, 26, 36))
        with self.assertRaises(RuntimeError):
            ep.parse_ripple_codes("16 nope 36")

    def test_complete_navigation_windows_never_extend_past_raw_end(self):
        n_bins, end, tail, overshoot = ep.complete_navigation_window(1.0, 1.3 - 5e-13)
        self.assertEqual(n_bins, 3)
        self.assertLessEqual(end, 1.3 - 5e-13)
        self.assertAlmostEqual(overshoot, 0.0)
        self.assertAlmostEqual(tail, 0.0)
        n_bins, end, tail, _overshoot = ep.complete_navigation_window(1.0, 1.299)
        self.assertEqual(n_bins, 2)
        self.assertAlmostEqual(end, 1.2)
        self.assertAlmostEqual(tail, 0.099)

    def test_navigation_window_lineage_uses_verified_trial_indices(self):
        original = _tiny_cohort()
        cohort = ep.EndpointCohort(
            counts=original.counts,
            observed=original.observed,
            exposure=original.exposure,
            source_ids=original.source_ids,
            cells=original.cells,
            metas=[
                ep.EndpointSource(
                    meta.source_trial_id,
                    meta.session_id,
                    meta.split,
                    meta.stored_split,
                    meta.label,
                )
                for meta in original.metas
            ],
            source_index=original.source_index,
        )
        with tempfile.TemporaryDirectory() as td:
            nav_path = Path(td) / "navigation.npz"
            _tiny_nav(original, nav_path)
            nav = ep.load_nav_data(nav_path, cohort)
        rows = []
        for meta in (m for m in original.metas if m.split == "train"):
            rows.append(
                {
                    "source_trial_id": meta.source_trial_id,
                    "session_id": meta.session_id,
                    "inner_split": "train",
                    "label": meta.label,
                    "trial_index": str(meta.trial_index),
                    "cue_start_s": "1.0",
                    "cue_end_s": "2.0",
                    "nav_end_s": "2.3",
                    "cue_duration_s": "1.0",
                    "nav_duration_s": "0.3",
                    "imported_cue_start_s": "1.0",
                    "imported_cue_end_s": "2.0",
                    "ripple_codes": "1,2,3",
                    "complete_nav_bins_100ms": "3",
                    "complete_nav_window_end_s": "2.3",
                    "discarded_nav_tail_s": "0.0",
                    "observed_cells": str(
                        sum(
                            ep.session_from_cell(cell) == meta.session_id
                            for cell in cohort.cells
                        )
                    ),
                }
            )
        trial_rows = {
            meta.source_trial_id: {
                "source_trial_id": meta.source_trial_id,
                "session_id": meta.session_id,
                "split": "train",
                "outcome": "success",
                "trial_index": str(meta.trial_index),
                "ripple_codes": "1,2,3",
                "ripple_cue_duration_s": "1.0",
                "ripple_nav_duration_s": "0.3",
            }
            for meta in original.metas
            if meta.split == "train"
        }
        ep.verify_navigation_window_lineage(nav, cohort, rows, trial_rows)
        rows[0]["trial_index"] = "999"
        with self.assertRaisesRegex(RuntimeError, "trial-index"):
            ep.verify_navigation_window_lineage(nav, cohort, rows, trial_rows)
        rows[0]["trial_index"] = trial_rows[rows[0]["source_trial_id"]]["trial_index"]
        rows[0]["cue_start_s"] = "invalid"
        with self.assertRaisesRegex(RuntimeError, "invalid numeric value"):
            ep.verify_navigation_window_lineage(nav, cohort, rows, trial_rows)

    def test_navigation_audit_claims_reject_development_access(self):
        cohort = _tiny_cohort()
        train = [meta for meta in cohort.metas if meta.split == "train"]
        development = [meta for meta in cohort.metas if meta.split != "train"]
        audit = {
            "training_sources": len(train),
            "training_source_allowlist_count": len(train),
            "development_sources_with_no_navigation": len(development),
            "training_source_allowlist_sha256": ep.stable_hash(
                sorted(meta.source_trial_id for meta in train)
            ),
            "raw_hashes_checked": True,
            "timing_checked": True,
            "cue_recount_exact": True,
            "cue_recount_mode": "raw_spikes_through_accepted_csv_precision",
            "development_navigation_selected": False,
            "split_gate_audit": {
                "allowed_splits": ["train"],
                "forbidden_rows_yielded": 0,
                "rows_yielded_by_split": {
                    # Outer training also includes inner-development/ineligible rows.
                    "trials": {"train": len(train) + len(development) + 1},
                    "cue_counts": {"train": 2 * (len(train) + len(development) + 1)},
                },
            },
        }
        ep.verify_navigation_audit_claims(audit, cohort)
        audit["development_navigation_selected"] = True
        with self.assertRaisesRegex(RuntimeError, "development exclusion"):
            ep.verify_navigation_audit_claims(audit, cohort)

    def test_pair_bank_covers_native_pairs_and_joint_sampler_is_half_nav(self):
        cohort = _tiny_cohort()
        with tempfile.TemporaryDirectory() as td:
            nav = _tiny_nav(cohort, Path(td) / "nav.npz")
            train, _dev = ep.assemble_world_seed(cohort, seed=0)
            scaler = ep.fit_cue_scaler(train.X_cue)
            bank = ep.build_endpoint_pair_bank(train, nav, scaler, cohort.cells)
            self.assertTrue(bank.coverage_rows)
            self.assertTrue(
                all(
                    r["represented_pairs"] == r["native_adjacent_pairs"]
                    for r in bank.coverage_rows
                )
            )
            scaled = ep.transform_cue(train.X_cue, scaler)
            _ds, payload, info = ep.cebra_dataset_for_endpoint_arm(
                "cebra_joint", scaled, train.y_pair, bank, device="cpu"
            )
            self.assertEqual(payload["phase_probs"], (0.5, 0.5))
            self.assertGreater(info["nav_sample_count"], 0)

    def test_pca_replay_matches_sklearn_on_invented_arrays(self):
        rng = np.random.default_rng(4)
        train = rng.normal(size=(12, 5, ep.CUE_BINS)).astype(np.float32)
        held = rng.normal(size=(3, 5, ep.CUE_BINS)).astype(np.float32)
        pca, features = ep.fit_pca_features(train, held)
        replay = ep._pca_replay_features(
            held,
            np.asarray(pca.components_, dtype=np.float64),
            np.asarray(pca.mean_, dtype=np.float64),
        )
        np.testing.assert_allclose(replay, features[1], atol=1e-6)

    def test_logistic_readout_replay_metrics_and_no_fit_guard(self):
        y = np.repeat(np.arange(1, 7), 3)
        X = np.eye(6)[y - 1].astype(float)
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "readout"
            pred_tr, prob_tr, pred_ev, prob_ev, _digest = ep.fit_readout_state(
                X_train=X,
                y_train=y,
                X_eval=X,
                target="start6",
                representation="raw",
                outdir=out,
            )
            with ep.no_fit_guard(), self.assertRaises(RuntimeError):
                ep.fit_readout_state(
                    X_train=X,
                    y_train=y,
                    X_eval=X,
                    target="start6",
                    representation="raw",
                    outdir=Path(td) / "blocked",
                )
            replay_pred, replay_prob = ep.predict_readout_state(
                out / "readout_state.npz", X
            )
            np.testing.assert_array_equal(replay_pred, pred_ev)
            np.testing.assert_allclose(replay_prob, prob_ev)
            row = ep.metric_row(
                y=y,
                pred=pred_tr,
                prob=prob_tr,
                classes=ep.target_classes("start6"),
                prefix={"split": "train"},
            )
            self.assertIn("brier", row)
            self.assertIn("class_recalls", row)

    def test_batched_deletion_scores_match_sklearn(self):
        rng = np.random.default_rng(71)
        classes = np.arange(1, 7)
        y = np.repeat(classes, 8)
        prob = rng.dirichlet(np.ones(6), size=len(y))
        prob[0] = [1, 0, 0, 0, 0, 0]
        pred = classes[prob.argmax(axis=1)]
        keep = rng.random((40, len(y))) > 0.2
        keep[0, y == 2] = False
        counts, ba, loss = ep.deletion_metrics(y, pred, prob, classes, keep)
        for i, mask in enumerate(keep):
            if np.any(counts[i] == 0):
                self.assertTrue(np.isnan(ba[i]) and np.isnan(loss[i]))
            else:
                self.assertAlmostEqual(
                    ba[i], ep.balanced_accuracy_score(y[mask], pred[mask]), places=14
                )
                self.assertAlmostEqual(
                    loss[i], ep.log_loss(y[mask], prob[mask], labels=classes), places=14
                )

    def test_batched_pair_bank_matches_scalar_rule(self):
        cohort = _tiny_cohort()
        with tempfile.TemporaryDirectory() as td:
            nav = _tiny_nav(cohort, Path(td) / "nav.npz", variable_bins=True)
            train, _ = ep.assemble_world_seed(cohort, seed=0)
            scaler = ep.fit_cue_scaler(train.X_cue)
            bank = ep.build_endpoint_pair_bank(train, nav, scaler, cohort.cells)
            expected = []
            for plan in train.plans:
                blocks = []
                for session, sid in plan["sources"].items():
                    counts = ep.nav_source_slice(nav, sid)[0]
                    cols = [
                        i
                        for i, c in enumerate(cohort.cells)
                        if ep.session_from_cell(c) == session
                    ]
                    blocks.append((counts, cols))
                length = max(len(counts) - 1 for counts, _ in blocks)
                for i in range(length):
                    pair = np.empty((2, len(cohort.cells)), dtype=np.float32)
                    for counts, cols in blocks:
                        native = min(
                            len(counts) - 2,
                            int(((i + 0.5) / length) * (len(counts) - 1)),
                        )
                        pair[0, cols] = counts[native, cols]
                        pair[1, cols] = counts[native + 1, cols]
                    expected.extend(scaler.transform(pair))
            np.testing.assert_array_equal(bank.nav_samples, np.asarray(expected))
            np.testing.assert_array_equal(
                bank.nav_pairs, np.arange(len(expected)).reshape(-1, 2)
            )

    def test_source_deletion_sensitivity_marks_lost_classes_inestimable(self):
        classes = ep.target_classes("start6")
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            for seed in ep.SEEDS:
                seed_dir = root / "observed" / f"seed{seed}"
                pred_dir = seed_dir / "readouts/raw/bin00/start6"
                pred_dir.mkdir(parents=True)
                ep.write_json(
                    seed_dir / "pseudo_development_manifest.json",
                    [
                        {
                            "source_trial_id": f"source-{int(label)}",
                            "pseudo_row": str(idx),
                        }
                        for idx, label in enumerate(classes)
                    ],
                )
                prob = np.eye(len(classes), dtype=np.float64)
                np.savez_compressed(
                    pred_dir / "readout_predictions.npz",
                    classes=classes,
                    y_development=classes,
                    pred_development=classes,
                    prob_development=prob,
                )
            summary = ep.source_deletion_sensitivity(root)
        self.assertEqual(summary["deleted_sources"], 6)
        self.assertEqual(
            summary["inestimable_source_ids_by_seed_target"][0]["count"], 6
        )
        self.assertFalse(summary["pseudorow_bootstrap_used"])

    def test_null_family_uses_world_maxima_and_plus_one_tail(self):
        rows = []
        for world_index in range(1 + len(ep.NULL_SEEDS)):
            world = "observed" if world_index == 0 else f"null_{world_index - 1:03d}"
            for seed in ep.SEEDS:
                for rep in ep.REPRESENTATIONS:
                    for window in ep.WINDOWS:
                        for target in ep.TARGETS:
                            rows.append(
                                {
                                    "world": world,
                                    "seed": seed,
                                    "representation": rep,
                                    "window": window,
                                    "target": target,
                                    "split": "development",
                                    "balanced_accuracy": 0.8
                                    if world == "observed"
                                    else 0.2,
                                    "log_loss": 0.2 if world == "observed" else 1.0,
                                }
                            )
        result = ep.summarize_null_families(rows)
        self.assertEqual(result["null_world_count"], 20)
        tails = result["plus_one_upper_tail"]
        self.assertEqual(tails["absolute_bin_balanced_accuracy_max_normalized"], 1 / 21)
        self.assertEqual(tails["absolute_bin_logloss_skill_max_normalized"], 1 / 21)
        self.assertEqual(tails["wholecue_joint_logloss_gain_max_normalized"], 1.0)
        self.assertEqual(tails["cue_joint_bin_logloss_gain_max_normalized"], 1.0)

    def test_paired_comparison_summary_reports_gaps_and_matched_differences(self):
        rows = []
        values = {
            "cebra_cue": {"train": (0.8, 0.6), "development": (0.7, 0.7)},
            "cebra_joint": {"train": (0.9, 0.4), "development": (0.8, 0.5)},
        }
        for representation, splits in values.items():
            for split, (balanced_accuracy, loss) in splits.items():
                rows.append(
                    {
                        "world": "observed",
                        "seed": 0,
                        "representation": representation,
                        "window": "bin00",
                        "target": "start6",
                        "split": split,
                        "n": 6,
                        "accuracy": balanced_accuracy,
                        "balanced_accuracy": balanced_accuracy,
                        "macro_f1": balanced_accuracy,
                        "log_loss": loss,
                        "brier": loss,
                    }
                )
        result = ep.summarize_paired_comparisons(rows)
        gaps = result["model_gaps"]
        cue_gap = next(row for row in gaps if row["representation"] == "cebra_cue")
        self.assertAlmostEqual(
            cue_gap["train_minus_development"]["balanced_accuracy"], 0.1
        )
        paired = result["cue_joint_development"][0]
        self.assertAlmostEqual(paired["joint_minus_cue"]["balanced_accuracy"], 0.1)
        self.assertAlmostEqual(paired["cue_minus_joint"]["log_loss"], 0.2)
        with self.assertRaisesRegex(RuntimeError, "incomplete"):
            ep.summarize_paired_comparisons(rows[:-1])

    def test_uniform_and_positive_metric_controls(self):
        classes = ep.target_classes("start6")
        y = classes.copy()
        uniform = np.full((len(y), len(classes)), 1 / len(classes))
        constant_prediction = np.full(len(y), classes[0])
        row = ep.metric_row(
            y=y,
            pred=constant_prediction,
            prob=uniform,
            classes=classes,
            prefix={},
        )
        self.assertAlmostEqual(row["balanced_accuracy"], 1 / len(classes))
        self.assertAlmostEqual(row["log_loss"], np.log(len(classes)))
        perfect_prob = np.eye(len(classes))
        perfect_row = ep.metric_row(
            y=y,
            pred=classes,
            prob=perfect_prob,
            classes=classes,
            prefix={},
        )
        self.assertEqual(perfect_row["balanced_accuracy"], 1.0)
        self.assertAlmostEqual(perfect_row["log_loss"], 0.0, places=14)

    def test_resource_benchmark_requires_current_hashes_coverage_and_pass_caps(self):
        with tempfile.TemporaryDirectory() as td:
            preparation = Path(td) / "preparation" / "current-hash"
            preparation.mkdir(parents=True)
            receipt_path = preparation / "synthetic-benchmark.json"
            script_path = preparation / "benchmark.py"
            script_path.write_text("invented-only benchmark")
            preflight_path = preparation.parent / "input-preflight.json"
            ep.write_json(
                preflight_path,
                {
                    "status": "passed",
                    "fits": 0,
                    "raw_navigation_access": False,
                    "dense_nav_cache_bytes": 1234,
                    "total_nav_bins": 100,
                    "endpoint_inner_training_sources": ep.EXPECTED_TRAIN_SOURCES,
                    "endpoint_inner_development_sources": ep.EXPECTED_DEVELOPMENT_SOURCES,
                },
            )
            readouts_per_seed = (
                len(ep.REPRESENTATIONS) * len(ep.TARGETS) * len(ep.WINDOWS)
            )
            confusion_rows_per_seed = (
                2
                * len(ep.REPRESENTATIONS)
                * len(ep.WINDOWS)
                * sum(len(ep.target_classes(target)) ** 2 for target in ep.TARGETS)
            )
            benchmark_configuration = {
                "device": "cuda",
                "updates": ep.CEBRA_UPDATES,
                "batch_size": 256,
                "hidden": 32,
                "dim": ep.CEBRA_DIM,
                "learning_rate": 3e-4,
                "cue_bins": ep.CUE_BINS,
                "train_pseudorows": ep.ROWS_PER_PAIR_TRAIN * len(ep.PAIR_LABELS),
                "development_pseudorows": ep.ROWS_PER_PAIR_DEVELOPMENT
                * len(ep.PAIR_LABELS),
                "encoder_fits_projected": ep.EXPECTED_ENCODER_FITS,
                "pca_fits_projected": ep.EXPECTED_PCA_FITS,
                "readout_fits_projected": ep.EXPECTED_READOUT_FITS,
                "world_seed_bundles_projected": ep.EXPECTED_READOUT_FITS
                // (len(ep.REPRESENTATIONS) * len(ep.TARGETS) * len(ep.WINDOWS)),
                "cells": ep.EXPECTED_CELLS,
                "sessions": ep.EXPECTED_SESSIONS,
            }
            receipt = {
                "classification": "software benchmark; invented arrays only",
                "biological_fits": 0,
                "raw_navigation_access": False,
                "device": "cuda",
                "cuda_available": True,
                "configuration": benchmark_configuration,
                "code_hashes": ep.helper_hashes(),
                "code_hashes_at_end": ep.helper_hashes(),
                "benchmark_script_sha256": ep.sha256_file(script_path),
                "benchmark_script_sha256_at_end": ep.sha256_file(script_path),
                "input_preflight_sha256": ep.sha256_file(preflight_path),
                "input_preflight_sha256_at_end": ep.sha256_file(preflight_path),
                "navigation_cache_bytes_from_preflight": 1234,
                "upper_navigation_bins_per_source": 251,
                "host_memory": {
                    "navigation_cache_padding_bytes": 0,
                    "cue_cohort_padding_bytes": (
                        ep.EXPECTED_TRAIN_SOURCES + ep.EXPECTED_DEVELOPMENT_SOURCES
                    )
                    * (
                        ep.EXPECTED_CELLS * ep.CUE_BINS * 4
                        + ep.EXPECTED_CELLS
                        + ep.CUE_BINS * 4
                    ),
                    "synthetic_resident_padding_bytes": (
                        ep.EXPECTED_TRAIN_SOURCES + ep.EXPECTED_DEVELOPMENT_SOURCES
                    )
                    * (
                        ep.EXPECTED_CELLS * ep.CUE_BINS * 4
                        + ep.EXPECTED_CELLS
                        + ep.CUE_BINS * 4
                    ),
                },
                "peak_rss_kib": 2_000_000,
                "readout_states_per_seed": readouts_per_seed,
                "confusion_rows_per_seed": confusion_rows_per_seed,
                "sensitivity_readout_states": len(ep.SEEDS) * readouts_per_seed,
                "development_sources_in_sensitivity": ep.EXPECTED_DEVELOPMENT_SOURCES,
                "sensitivity_summary_sources": ep.EXPECTED_DEVELOPMENT_SOURCES,
                "runtime_cap_seconds": ep.MAX_RUN_SECONDS,
                "projected_full_seconds_with_25pct_margin": 4000.0,
                "runtime_pass_with_margin": True,
                "output_cap_gib": ep.OUTPUT_LIMIT_GIB,
                "projected_model_output_bytes": 2862,
                "projected_full_output_bytes_including_nav_cache": 4096,
                "output_pass": True,
            }
            ep.write_json(receipt_path, receipt)
            validated = ep.validate_resource_benchmark(receipt_path)
            self.assertEqual(validated["receipt_sha256"], ep.sha256_file(receipt_path))
            self.assertEqual(validated["device"], "cuda")

            receipt["device"] = "cpu"
            receipt["configuration"]["device"] = "cpu"
            ep.write_json(receipt_path, receipt)
            with self.assertRaisesRegex(RuntimeError, "CUDA device"):
                ep.validate_resource_benchmark(receipt_path)
            receipt["device"] = "cuda"
            receipt["configuration"]["device"] = "cuda"
            receipt["benchmark_script_sha256_at_end"] = "0" * 64
            ep.write_json(receipt_path, receipt)
            with self.assertRaisesRegex(RuntimeError, "script changed"):
                ep.validate_resource_benchmark(receipt_path)
            receipt["benchmark_script_sha256_at_end"] = ep.sha256_file(script_path)

            receipt["runtime_pass_with_margin"] = False
            receipt["projected_full_seconds_with_25pct_margin"] = 6000.0
            ep.write_json(receipt_path, receipt)
            with self.assertRaisesRegex(RuntimeError, "runtime gate does not pass"):
                ep.validate_resource_benchmark(receipt_path)

            receipt["runtime_pass_with_margin"] = True
            receipt["projected_full_seconds_with_25pct_margin"] = 4000.0
            receipt["host_memory"]["cue_cohort_padding_bytes"] -= 1
            ep.write_json(receipt_path, receipt)
            with self.assertRaisesRegex(RuntimeError, "memory-padding evidence"):
                ep.validate_resource_benchmark(receipt_path)
            receipt["host_memory"]["cue_cohort_padding_bytes"] += 1
            receipt["code_hashes"] = {"stale": "0" * 64}
            ep.write_json(receipt_path, receipt)
            with self.assertRaisesRegex(RuntimeError, "hashes are stale"):
                ep.validate_resource_benchmark(receipt_path)

    def test_hash_bound_approval_rejects_config_tamper(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            nav = root / "navigation.npz"
            audit = root / "navigation_audit.json"
            path = root / "approval.json"
            benchmark = root / "benchmark.json"

            def fake_facts(**kwargs):
                return {"config_hash": ep.stable_hash(kwargs["config"])}

            config = {"device": "cpu"}
            with patch.object(ep, "approval_facts", side_effect=fake_facts):
                facts = ep.approval_facts(
                    accepted_root=root,
                    navigation_audit=audit,
                    navigation_npz=nav,
                    benchmark_receipt=benchmark,
                    config=config,
                )
                ep.write_json(path, {"approved": True, **facts})
                self.assertTrue(
                    ep.require_prefit_approval(
                        path,
                        accepted_root=root,
                        navigation_audit=audit,
                        navigation_npz=nav,
                        benchmark_receipt=benchmark,
                        config=config,
                    )["approved"]
                )
                with self.assertRaises(RuntimeError):
                    ep.require_prefit_approval(
                        path,
                        accepted_root=root,
                        navigation_audit=audit,
                        navigation_npz=nav,
                        benchmark_receipt=benchmark,
                        config={"device": "cuda"},
                    )

    def test_tiny_real_cebra_joint_sampler_encoder_save_reload(self):
        rng = np.random.default_rng(0)
        train_scaled = rng.normal(size=(4, 4, ep.CUE_BINS)).astype(np.float32)
        y = np.array([0, 1, 0, 1], dtype=np.int64)
        cue_samples = train_scaled.transpose(0, 2, 1).reshape(-1, 4)
        cue_pairs_by_row = [
            np.asarray(
                [
                    (r * ep.CUE_BINS + b, r * ep.CUE_BINS + b + 1)
                    for b in range(ep.CUE_BINS - 1)
                ],
                dtype=np.int64,
            )
            for r in range(4)
        ]
        cue_samples_by_row = [
            np.arange(r * ep.CUE_BINS, (r + 1) * ep.CUE_BINS, dtype=np.int64)
            for r in range(4)
        ]
        nav_samples = rng.normal(size=(8, 4)).astype(np.float32)
        nav_pairs_by_row = [
            np.asarray([(2 * r, 2 * r + 1)], dtype=np.int64) for r in range(4)
        ]
        nav_samples_by_row = [
            np.asarray([2 * r, 2 * r + 1], dtype=np.int64) for r in range(4)
        ]
        bank = ep.EndpointPairBank(
            cue_samples=cue_samples,
            cue_labels=np.repeat(y, ep.CUE_BINS),
            cue_pairs=np.concatenate(cue_pairs_by_row),
            cue_samples_by_row=cue_samples_by_row,
            cue_pairs_by_row=cue_pairs_by_row,
            nav_samples=nav_samples,
            nav_labels=np.repeat(y, 2),
            nav_pairs=np.concatenate(nav_pairs_by_row),
            nav_samples_by_row=nav_samples_by_row,
            nav_pairs_by_row=nav_pairs_by_row,
            row_labels=y,
            pair_lineage={},
            coverage_rows=[],
        )
        with tempfile.TemporaryDirectory() as td:
            solver, info = ep.train_endpoint_encoder(
                arm="cebra_joint",
                train_scaled=train_scaled,
                y_pair=y,
                pair_bank=bank,
                seed=0,
                outdir=Path(td) / "encoder",
                iterations=2,
                batch_size=4,
                hidden=8,
                dim=2,
                device="cpu",
            )
            checkpoint = Path(td) / "encoder" / "checkpoint_final.pth"
            self.assertEqual(info["checkpoints"], [str(checkpoint)])
            self.assertEqual(
                list((Path(td) / "encoder").glob("checkpoint*.pth")), [checkpoint]
            )
            loaded = ep.load_encoder_checkpoint(
                checkpoint,
                input_dim=4,
                dim=2,
                hidden=8,
                lr=3e-4,
                device="cpu",
            )
            np.testing.assert_allclose(
                ep._embed_cue(solver, train_scaled, device="cpu"),
                ep._embed_cue(loaded, train_scaled, device="cpu"),
                atol=1e-6,
            )


if __name__ == "__main__":
    unittest.main()
