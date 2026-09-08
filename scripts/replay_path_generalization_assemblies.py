"""Frozen-checkpoint, CPU-only transfer across mixtures of the SAME training sources.

This is not independent biological validation. No fitting or optimizer step occurs.
"""

import csv
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import torch
from scipy.special import expit

from scripts.place195_path_generalization_phase1 import (
    _standard_scaler_from_mean_scale as restore_scaler,
)
from scripts.place195_path_generalization_phase1 import (
    ndarray_sha256,
    validate_completed_cebra_fit,
    weighted_binary_metrics,
    write_csv,
)
from scripts.place195_v7_v8_neural_experiments import LABELS, assemble_pseudo
from scripts.place195_v8b_v9_cebra import embed_rows, load_source_npz, make_solver


def main(run_root: Path):
    stage = Path(
        "/home/hongyi-home-lab/neuro_science/outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/v7-v8-neural-experiments/primary29_min3train_min1val/bin100ms"
    )
    source, metas, source_index, cells = load_source_npz(stage)
    Xsrc, Msrc = source["X_source_cell_bin"], source["observed_source_cell_mask"]
    source_hash = hashlib.sha256(
        (stage / "source_level_cue_tensors.npz").read_bytes()
    ).hexdigest()
    assert (
        source_hash
        == "688e3b52f69a872c7aec420da99ebb6f0b80464351ded3813b077cd7ed3cf567"
    )
    torch.set_num_threads(1)
    arrays = {}
    for assembly in range(5):
        parts = [
            assemble_pseudo(
                Xsrc, Msrc, source_index, metas, cells, "train", label, 64, assembly
            )[0]
            for label in LABELS
        ]
        arrays[assembly] = np.concatenate(parts)
    y = np.repeat([0, 1], 64).astype(np.int64)
    # Select the declared factorial role, not completion order (sensitivity fits interleave).
    files = [
        path
        for path in sorted((run_root / "track_b/fits").glob("*/fit_info.json"))
        if json.loads(path.read_text())["fit_spec"]["family_role"]
        == "crossed_seed_primary"
    ]
    if len(files) != 50:
        raise ValueError("all 50 crossed-seed fits must finish before this replay")
    output = run_root / "assembly_transfer"
    if output.exists():
        raise FileExistsError(output)
    records, checks = [], []
    seen = set()
    for file in files:
        info = json.loads(file.read_text())
        spec = info["fit_spec"]
        if spec["family_role"] != "crossed_seed_primary":
            raise ValueError("receipt is not a member of the crossed-seed grid")
        key = (spec["objective"], spec["assembly_seed"], spec["optimizer_seed"])
        if key in seen:
            raise ValueError("duplicate factorial fit")
        seen.add(key)
        validate_completed_cebra_fit(file.parent, info["fit_identity_hash"])
        assert (
            ndarray_sha256(arrays[spec["assembly_seed"]])
            == info["fit_identity"]["train_array_sha256"]
        )
        assert ndarray_sha256(y) == info["fit_identity"]["train_label_sha256"]
        saved = np.load(
            file.parent / "embeddings_predictions_decoder.npz", allow_pickle=False
        )
        neural_scaler = restore_scaler(
            saved["neural_scaler_mean"], saved["neural_scaler_scale"]
        )
        decoder_scaler = restore_scaler(
            saved["decoder_scaler_mean"], saved["decoder_scaler_scale"]
        )
        solver = make_solver(29, 8, 32, 3e-4, "cpu")
        checkpoint = file.parent / "checkpoint_final.pth"
        checkpoint_hash = hashlib.sha256(checkpoint.read_bytes()).hexdigest()
        solver.load_state_dict(
            torch.load(checkpoint, map_location="cpu", weights_only=True), strict=True
        )
        solver.n_features = 29
        solver.model.eval()
        with (file.parent / "predictions.csv").open() as handle:
            original = [
                r for r in csv.DictReader(handle) if r["split"] == "train_sampled"
            ]
        original.sort(key=lambda r: int(r["row"]))
        for target_assembly, X in arrays.items():
            Z = embed_rows(solver, neural_scaler, X, device="cpu", dim=8)
            D = np.asarray(decoder_scaler.transform(Z))
            logit = (D @ saved["decoder_coef"].T + saved["decoder_intercept"]).ravel()
            p = expit(logit)
            own = target_assembly == spec["assembly_seed"]
            if own:
                z_error = float(np.max(np.abs(Z - saved["Z_train"])))
                p_error = float(
                    np.max(
                        np.abs(
                            p - np.asarray([float(r["prob_present"]) for r in original])
                        )
                    )
                )
                assert z_error < 1e-4 and p_error < 1e-4
                assert np.array_equal(
                    p >= 0.5,
                    np.asarray([r["pred_label"] == "present" for r in original]),
                )
                checks.append(
                    {
                        "fit": str(file.parent),
                        "embedding_CPU_GPU_max_difference": z_error,
                        "probability_CPU_GPU_max_difference": p_error,
                        "checkpoint_sha256": checkpoint_hash,
                    }
                )
            records.append(
                {
                    **spec,
                    "evaluation_assembly_seed": target_assembly,
                    "evaluation_kind": "own_training_assembly"
                    if own
                    else "other_assembly_same_training_sources",
                    "fit_identity_hash": info["fit_identity_hash"],
                    **weighted_binary_metrics(y, p, ranking_score=logit),
                }
            )
        assert hashlib.sha256(checkpoint.read_bytes()).hexdigest() == checkpoint_hash
    assert len(seen) == 50 and len(records) == 250 and len(checks) == 50
    output.mkdir()
    write_csv(output / "assembly_transfer_metrics.csv", records)
    write_csv(output / "replay_parity.csv", checks)
    summary = {
        "scope": "CPU forward only; same training-source pools, not independent biological validation",
        "fits_replayed": 50,
        "metric_rows": 250,
        "new_fits": 0,
        "device": "cpu",
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "source_npz_sha256": source_hash,
        "maximum_embedding_CPU_GPU_difference": max(
            r["embedding_CPU_GPU_max_difference"] for r in checks
        ),
        "maximum_probability_CPU_GPU_difference": max(
            r["probability_CPU_GPU_max_difference"] for r in checks
        ),
    }
    (output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main(Path(sys.argv[1]))
