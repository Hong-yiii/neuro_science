"""One explicitly adaptive CE diagnostic round; run as a module from repository root."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import importlib.metadata
import json
from pathlib import Path
import shutil
import sys
import time
import traceback

import joblib
import numpy as np
import torch

from scripts.start_goal_autoresearch import (
    ROOT,
    SPLITS,
    arrays,
    encoder_rows,
    git,
    hidden_features,
    make_solver,
    readout,
    save_scores,
    sha256_file,
    train_ce_case,
    verify_inputs,
    write_json,
)

MARKS = (10, 25, 100, 250, 1000)


def earlier_readouts(out, data, meta, whole):
    scaler = joblib.load(out / "input_scaler.joblib")
    transformed = {s: encoder_rows(x, whole) for s, (x, _) in data.items()}
    labels = {s: y for s, (_, y) in data.items()}
    rows = []
    for step in MARKS:
        state = torch.load(
            out / f"model_step{step:04}.pth", map_location="cuda", weights_only=True
        )
        encoder = make_solver(transformed["train"].shape[1], 8, 32, 0.001, "cuda").model
        encoder.load_state_dict(state["encoder"], strict=True)
        head = torch.nn.Linear(8 if whole else 80, 30).to("cuda")
        head.load_state_dict(state["head"], strict=True)
        features = {
            s: hidden_features(encoder, scaler, x, "cuda", 8)
            for s, x in transformed.items()
        }
        folder = out / f"readout{step:04}"
        info = {**meta, "step": step, "whole": whole}
        rr, _ = readout(folder / "joint", features, labels, info)
        rows.extend(rr)
        for split in SPLITS:
            with torch.no_grad():
                prob = (
                    torch.softmax(
                        head(torch.as_tensor(features[split], device="cuda")), dim=1
                    )
                    .cpu()
                    .numpy()
                )
            rows.append(
                save_scores(
                    folder / "head",
                    labels[split],
                    prob.argmax(axis=1),
                    prob,
                    {
                        **info,
                        "target": "joint",
                        "split": split,
                        "decoder": "trained_ce_head",
                    },
                )
            )
    return rows


def check_replay(out, old):
    current = torch.load(out / "model.pth", map_location="cpu", weights_only=True)
    previous = torch.load(old / "model.pth", map_location="cpu", weights_only=True)
    for part in ("encoder", "head"):
        for name, value in current[part].items():
            if not torch.equal(value, previous[part][name]):
                raise ValueError(f"replay state mismatch: {part}/{name}")
    for method in ("joint", "head"):
        for split in SPLITS:
            with (
                np.load(out / method / f"{split}_predictions.npz") as a,
                np.load(old / method / f"{split}_predictions.npz") as b,
            ):
                for key in ("pred", "prob"):
                    np.testing.assert_array_equal(a[key], b[key])
    write_json(
        out / "replay.json",
        {"status": "exact_state_and_prediction_match", "original": old},
    )


def run(out, study, receipt):
    recipes = [
        ("ce_bin_replay", False, 0.001, False),
        ("ce_whole_replay", True, 0.001, False),
        ("ce_bin_wd01", False, 0.1, False),
        ("ce_bin_pseudo64", False, 0.001, True),
    ]
    rows = []
    for case, whole, decay, augmented in recipes:
        for seed in (0, 1, 2):
            data = arrays(seed)
            if augmented:
                source = study / "04-scaling" / f"pseudo64_seed{seed}" / "arrays.npz"
                if (
                    sha256_file(source)
                    != receipt[str(source.relative_to(study / "04-scaling"))]
                ):
                    raise ValueError("augmentation source hash mismatch")
                with np.load(source) as z:
                    data = {s: (z[f"X_{s}"], z[f"y_{s}"]) for s in SPLITS}
                np.testing.assert_array_equal(
                    data["development"][0], arrays(seed)["development"][0]
                )
            parent = out / f"{case}_seed{seed}"
            parent.mkdir()
            np.savez_compressed(
                parent / "arrays.npz",
                X_train=data["train"][0],
                y_train=data["train"][1],
                X_development=data["development"][0],
                y_development=data["development"][1],
            )
            meta = {
                "case": case,
                "seed": seed,
                "adaptive": True,
                "weight_decay": decay,
                "pseudo_rows_per_class": len(data["train"][1]) // 30,
            }
            fit = parent / "fit"
            # Reuse the original trainer. Snapshot writing must not alter the training RNG.
            rr = train_ce_case(
                fit,
                data,
                meta,
                "cuda",
                whole=whole,
                weight_decay=decay,
                checkpoints=MARKS,
            )
            if case.endswith("replay"):
                oldcase = "ce_whole" if whole else "ce_bin"
                check_replay(fit, study / "03-supervised" / f"{oldcase}_seed{seed}")
            rr += earlier_readouts(fit, data, meta, whole)
            write_json(parent / "metrics.json", rr)
            rows += rr
            write_json(out / "metrics.json", rows)
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--study-dir", type=Path, required=True)
    args = parser.parse_args()
    study = args.study_dir.resolve()
    out = study / "06-ce-followup"
    out.mkdir(exist_ok=False)
    torch.set_num_threads(2)
    started = time.monotonic()
    manifest = {
        "status": "running",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "config": {"phase": "followup", "seeds": [0, 1, 2], "adaptive": True},
        "git": git(["-C", str(ROOT), "rev-parse", "HEAD"]),
        "dirty": git(["-C", str(ROOT), "status", "--short"]),
        "executable": sys.executable,
        "packages": {
            d.metadata["Name"]: d.version for d in importlib.metadata.distributions()
        },
    }
    write_json(out / "manifest.json", manifest)
    try:
        if not torch.cuda.is_available():
            raise ValueError("CUDA unavailable; no silent fallback")
        manifest["input_hashes"] = verify_inputs()
        manifest["prior_phase_hashes"] = {
            p: sha256_file(study / p / "artifact_hashes.json")
            for p in ("03-supervised", "04-scaling")
        }
        code = out / "code"
        code.mkdir()
        for source in (
            Path(__file__),
            ROOT / "scripts/start_goal_autoresearch.py",
            ROOT / "docs/reports/start-goal-autoresearch-journal.md",
        ):
            shutil.copy2(source, code / source.name)
        write_json(out / "manifest.json", manifest)
        receipt = json.loads((study / "04-scaling/artifact_hashes.json").read_text())
        rows = run(out, study, receipt)
        manifest.update(status="completed", metric_rows=len(rows))
    except Exception:
        manifest.update(status="failed", traceback=traceback.format_exc())
        raise
    finally:
        manifest["elapsed_seconds"] = time.monotonic() - started
        manifest["finished_utc"] = datetime.now(timezone.utc).isoformat()
        write_json(out / "manifest.json", manifest)
    write_json(
        out / "artifact_hashes.json",
        {
            str(p.relative_to(out)): sha256_file(p)
            for p in sorted(out.rglob("*"))
            if p.is_file()
        },
    )


if __name__ == "__main__":
    main()
