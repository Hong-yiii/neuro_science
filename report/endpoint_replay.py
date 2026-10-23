"""Read-only, observed-only saved-input replay for the endpoint review notebook.

Not the historical full verifier: no source reconstruction, navigation or null-world
replay. Private arrays remain in memory. Current package helpers are used honestly
as current code, never substituted into historical approval hashes.
"""

import json
from contextlib import ExitStack, contextmanager
from hashlib import sha256
from importlib.metadata import version
from io import BytesIO
from pathlib import Path
from typing import Any, cast
from unittest.mock import patch

MANIFEST_SHA256 = "e0f88a72b436b6fd86299c5e4575af2137904b4e21c57a7fbaa392661b802a36"
RUN_RELATIVE = "outputs/cebra-endpoint-time-readout-20261006/run-reviewed-20261007"
REPRESENTATIONS = ("raw", "pca8", "cebra_cue", "cebra_joint", "raw_svd_lda")
TARGETS = ("pair30", "start6", "goal6")
WINDOWS = tuple(f"bin{i:02d}" for i in range(10)) + ("wholecue",)


def require(condition, message):
    if not condition:
        raise ValueError(message)


class SavedRun:
    """Authenticate bytes before parsing; only observed artifacts and metadata."""

    def __init__(self, root):
        self.root = Path(root).resolve(strict=True)
        content = (self.root / "hash_manifest.json").read_bytes()
        if sha256(content).hexdigest() != MANIFEST_SHA256:
            raise ValueError("Saved-run manifest identity mismatch")
        try:
            self.manifest = json.loads(content)
        except json.JSONDecodeError as exc:
            raise ValueError("Invalid run manifest JSON") from exc
        self.accessed = set()

    def read(self, relative):
        path = Path(relative)
        allowed = str(path) in {
            "run_config.json",
            "run_inputs.json",
            "source_support.json",
        }
        allowed |= len(path.parts) > 2 and path.parts[:2] in {
            ("observed", f"seed{i}") for i in range(3)
        }
        if path.is_absolute() or ".." in path.parts or not allowed:
            raise ValueError("Outside observed-only notebook scope")
        resolved = (self.root / path).resolve(strict=True)
        if not resolved.is_relative_to(self.root):
            raise ValueError("Artifact escapes run root")
        content = resolved.read_bytes()
        if sha256(content).hexdigest() != self.manifest.get(path.as_posix()):
            raise ValueError("Saved artifact hash mismatch")
        self.accessed.add(path.as_posix())
        return content

    def json(self, relative):
        try:
            return json.loads(self.read(relative))
        except json.JSONDecodeError as exc:
            raise ValueError("Invalid authenticated artifact JSON") from exc

    def arrays(self, relative):
        import numpy as np

        with np.load(BytesIO(self.read(relative)), allow_pickle=False) as archive:
            return {key: archive[key] for key in archive.files}


def runtime_report(run):
    import torch

    expected = run.json("run_inputs.json")["packages"]
    actual = {name: version(name) for name in expected}
    if actual != expected:
        raise RuntimeError("Scientific package versions differ from the saved run")
    config = run.json("run_config.json")
    if config["device"] != "cuda" or not torch.cuda.is_available():
        raise RuntimeError("Original CUDA backend required; no silent CPU fallback")
    if (config["dim"], config["hidden"], config["updates"], config["lr"]) != (
        8,
        32,
        1000,
        0.0003,
    ):
        raise ValueError("Unexpected encoder configuration")
    torch.set_num_threads(2)
    return actual


@contextmanager
def no_fitting():
    """Block the fitting/update paths used by this workflow, restore on exit."""
    from sklearn.decomposition import PCA
    from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler
    from threadpoolctl import threadpool_limits
    from torch.optim import Adam

    from neuro.studies import endpoint_time_readout as ep

    def forbidden(*args, **kwargs):
        raise RuntimeError("Notebook replay forbids fitting and optimizer steps")

    with ExitStack() as stack:
        # Original run used two BLAS threads; one changes float32 LDA probabilities.
        stack.enter_context(threadpool_limits(limits=2))
        stack.enter_context(ep.no_fit_guard())
        for owner, name in (
            (StandardScaler, "fit"),
            (StandardScaler, "partial_fit"),
            (PCA, "fit_transform"),
            (LogisticRegression, "fit"),
            (LinearDiscriminantAnalysis, "fit"),
            (Adam, "step"),
        ):
            stack.enter_context(patch.object(owner, name, forbidden))
        yield


def load_seed(run, seed):
    """Load saved standardized cue and labels, verify private assembly lineage."""
    import numpy as np

    from neuro.studies import endpoint_time_readout as ep

    if seed not in range(3):
        raise ValueError("Observed seeds are 0, 1, 2")
    base = f"observed/seed{seed}"
    cue = run.arrays(f"{base}/scaled_cue.npz")
    targets = run.arrays(f"{base}/pseudo_targets.npz")
    scaler = run.arrays(f"{base}/cue_input_scaler.npz")
    if any(scaler[k].shape != (195,) for k in ("mean", "scale", "var")):
        raise ValueError("Input scaler dimensions changed")
    require(all(np.isfinite(v).all() for v in scaler.values()), "Nonfinite scaler")
    require(
        (scaler["scale"] > 0).all() and (scaler["var"] >= 0).all(),
        "Invalid scaler range",
    )
    sources = {}
    lineage_counts = {}
    for split, n, per_class in (("train", 480, 16), ("development", 240, 8)):
        require(
            cue[split].shape == (n, 195, 10) and cue[split].dtype == np.float32,
            "Cue schema mismatch",
        )
        require(np.isfinite(cue[split]).all(), "Nonfinite cue")
        y = targets[f"y_pair_{split}"]
        require(y.shape == (n,) and y.dtype == np.int64, "Target schema mismatch")
        np.testing.assert_array_equal(
            np.bincount(y, minlength=30), np.full(30, per_class)
        )
        plans = run.json(f"{base}/pseudo_{split}_manifest.json")
        require(len(plans) == n * 58, "Lineage count mismatch")
        sessions = {row["session_id"] for row in plans}
        require(len(sessions) == 58, "Session count mismatch")
        require(
            len({(row["pseudo_row"], row["session_id"]) for row in plans}) == n * 58,
            "Repeated row/session",
        )
        for row in plans:
            try:
                index = int(row["pseudo_row"])
            except (TypeError, ValueError) as exc:
                raise ValueError("Invalid lineage row index") from exc
            recorded_split = "train" if split == "train" else "validation"
            require(
                0 <= index < n and row["split"] == recorded_split,
                "Lineage index mismatch",
            )
            require(row["label"] == ep.PAIR_LABELS[y[index]], "Lineage label mismatch")
        sources[split] = {(row["session_id"], row["source_trial_id"]) for row in plans}
        lineage_counts[split] = {
            "selections": len(plans),
            "distinct_used_sources": len(sources[split]),
        }
    require(
        sources["train"].isdisjoint(sources["development"]),
        "Source overlap across splits",
    )
    return cue, targets, scaler, lineage_counts


def replay_features(run, seed, cue):
    """Restore fitted PCA/CEBRA; compare both splits with stored feature arrays."""
    import numpy as np
    import torch
    from sklearn.decomposition import PCA

    from neuro.studies import endpoint_time_readout as ep

    base = f"observed/seed{seed}"
    state = run.arrays(f"{base}/pca_state.npz")
    require(
        state["components"].shape == (8, 195) and state["mean"].shape == (195,),
        "PCA shape mismatch",
    )
    require(
        state["components"].dtype == state["mean"].dtype == np.float32,
        "PCA dtype mismatch",
    )
    pca = cast(Any, PCA(n_components=8, whiten=False))
    pca.components_, pca.mean_ = state["components"], state["mean"]
    pca.n_features_in_ = 195
    pca.n_components_ = 8
    # Namespace-selection placeholder only; whitening is disabled. Not measured variance.
    pca.explained_variance_ = np.zeros(8, dtype=np.float32)
    features, architectures = {}, {}
    with no_fitting():
        for split, x in cue.items():
            flat = x.transpose(0, 2, 1).reshape(-1, 195)
            features[split] = {
                "raw": ep.flatten_cue(x),
                # Preserve sklearn's float32 transform order, not (X-mean) @ V.T.
                "pca8": pca.transform(flat).astype(np.float32).reshape(len(x), 80),
            }
        for arm in ("cebra_cue", "cebra_joint"):
            solver = ep.make_solver(195, 8, 32, 0.0003, "cuda")
            checkpoint = torch.load(
                BytesIO(run.read(f"{base}/{arm}/checkpoint_final.pth")),
                map_location="cuda",
                weights_only=True,
            )
            solver.load_state_dict(checkpoint)
            architectures[arm] = str(solver.model)
            for split, x in cue.items():
                features[split][arm] = ep._embed_cue(solver, x, device="cuda")
            del solver, checkpoint
    errors = []
    for split in ("train", "development"):
        saved = run.arrays(f"{base}/features_{split}.npz")
        for name, array in features[split].items():
            require(
                array.shape == saved[name].shape and np.isfinite(array).all(),
                "Feature schema mismatch",
            )
            # Original accepted feature tolerance; also record actual max error.
            np.testing.assert_allclose(array, saved[name], rtol=1e-7, atol=1e-6)
            errors.append(
                {
                    "seed": seed,
                    "split": split,
                    "representation": name,
                    "max_abs_error": np.max(np.abs(array - saved[name])).item(),
                }
            )
    return features, errors, architectures


def replay_readouts(run, seed, features, targets):
    """Replay 165 fitted pipelines; return aggregate scores/confusions, not rows."""
    import joblib
    import numpy as np
    from sklearn.metrics import (
        accuracy_score,
        balanced_accuracy_score,
        confusion_matrix,
    )

    from neuro.studies import endpoint_time_readout as ep

    results, confusions = [], {}
    max_probability_error = 0.0
    with no_fitting():
        for representation in REPRESENTATIONS:
            source = "raw" if representation == "raw_svd_lda" else representation
            for window in WINDOWS:
                for target in TARGETS:
                    base = f"observed/seed{seed}/readouts/{representation}/{window}/{target}"
                    # Pickle-based loading is allowed ONLY after pinned-manifest authentication.
                    payload = joblib.load(
                        BytesIO(run.read(f"{base}/readout_model.joblib"))
                    )
                    saved = run.arrays(f"{base}/readout_predictions.npz")
                    classes = ep.target_classes(target)
                    np.testing.assert_array_equal(payload["classes"], classes)
                    np.testing.assert_array_equal(saved["classes"], classes)
                    for split in ("train", "development"):
                        x = ep.extract_window_features(
                            source, features[split][source], window, cell_count=195
                        )
                        y = ep.target_labels(targets[f"y_pair_{split}"], target)
                        model = payload["model"]
                        prob = ep.align_probabilities(
                            model.predict_proba(payload["scaler"].transform(x)),
                            model.classes_,
                            classes,
                        )
                        pred = classes[prob.argmax(axis=1)]
                        np.testing.assert_array_equal(y, saved[f"y_{split}"])
                        np.testing.assert_array_equal(pred, saved[f"pred_{split}"])
                        np.testing.assert_allclose(
                            prob, saved[f"prob_{split}"], rtol=1e-7, atol=1e-9,
                            err_msg=f"{seed}/{representation}/{window}/{target}/{split}",
                            verbose=False,
                        )
                        max_probability_error = max(
                            max_probability_error,
                            np.abs(prob - saved[f"prob_{split}"]).max().item(),
                        )
                        matrix = confusion_matrix(y, pred, labels=classes)
                        results.append(
                            {
                                "seed": seed,
                                "representation": representation,
                                "window": window,
                                "target": target,
                                "split": split,
                                "n": len(y),
                                "accuracy": accuracy_score(y, pred),
                                "balanced_accuracy": balanced_accuracy_score(y, pred),
                            }
                        )
                        if split == "development" and window == "wholecue":
                            confusions[representation, target] = matrix
    return results, confusions, max_probability_error
