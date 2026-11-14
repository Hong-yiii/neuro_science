"""New grid's decoder comparison and genuine CEBRA discrete multisession fits."""

from __future__ import annotations

import time
import warnings
from collections import Counter
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from unittest.mock import patch

import joblib
import numpy as np
from sklearn.exceptions import ConvergenceWarning
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from threadpoolctl import threadpool_limits

from neuro.evaluation import classification_metrics
from neuro.notebook_artifacts import FitAccounting, no_fitting, target_heads
from neuro.notebook_support import fit_logistic
from neuro.pca_lda import fit_lda, fit_pca, fit_standardizer, raw_features
from neuro.pseudopopulation import materialize
from neuro.studies.source_support_ablation import (
    plan_digest,
    usage_tables,
    overlap_summary,
    sha,
    write_json,
)

ENCODERS = ("raw", "pca", "cebra", "native")
DECODERS = ("logistic", "svm", "knn", "lda")
FAMILIES = tuple(
    e if d == "logistic" else e + "_" + d for e in ENCODERS for d in DECODERS
)


class GridFitAccounting(FitAccounting):
    def start(self):
        super().start()
        import cebra

        for cls, kind in (
            (cebra.CEBRA, "native"),
            (SVC, "svm"),
            (KNeighborsClassifier, "knn"),
        ):
            self.counts[kind] = 0

            def counted(original, category):
                def call(*args, **kwargs):
                    self.counts[category] += 1
                    return original(*args, **kwargs)

                return call

            self.stack.enter_context(patch.object(cls, "fit", counted(cls.fit, kind)))
        return self


@contextmanager
def frozen_models():
    import cebra

    def forbidden(*args, **kwargs):
        raise RuntimeError("new grid verification forbids fitting")

    with (
        no_fitting(cebra=True),
        patch.object(SVC, "fit", forbidden),
        patch.object(KNeighborsClassifier, "fit", forbidden),
        patch.object(cebra.CEBRA, "fit", forbidden),
    ):
        yield


@dataclass
class NativeMultisessionFit:
    estimator: object
    standardizer: object
    columns: tuple
    diagnostics: dict

    def transform(self, values):
        scaled = self.standardizer.transform(values)
        embeddings = []
        for i, columns in enumerate(self.columns):
            x = (
                scaled[:, columns, :]
                .transpose(0, 2, 1)
                .reshape(-1, len(columns))
                .copy()
            )
            z = self.estimator.transform(x, session_id=i)
            embeddings.append(z.reshape(len(values), values.shape[2], -1))
        # Fixed equal-session consensus of aligned coordinates, no learned pooling.
        result = np.mean(np.stack(embeddings), axis=0, dtype=np.float32)
        if not np.isfinite(result).all():
            raise ValueError("nonfinite native multisession transform")
        return result.reshape(len(values), -1)


def fit_native(train, targets, units, blocks, config, seed):
    import cebra
    import torch

    from cebra.distributions import multisession as native_sampling

    if str(native_sampling._device) != "cpu":
        raise RuntimeError("native sampler must stay on CPU; hide CUDA before import")
    columns = tuple(
        tuple(i for i, u in enumerate(units) if u.block_id == b) for b in blocks
    )
    if len(columns) < 2 or any(not c for c in columns):
        raise ValueError(
            "native multisession requires multiple nonempty session inputs"
        )
    started = time.monotonic()
    standardizer = fit_standardizer(train)
    scaled = standardizer.transform(train)
    xs = [
        scaled[:, c, :].transpose(0, 2, 1).reshape(-1, len(c)).copy() for c in columns
    ]
    _, codes = np.unique(targets, return_inverse=True)
    ys = [np.repeat(codes, train.shape[2]).astype(np.int64) for _ in columns]
    batch = max(2, 256 // len(columns))
    estimator = cebra.CEBRA(
        model_architecture="offset1-model",
        num_hidden_units=32,
        output_dimension=config["output_dimension"],
        max_iterations=config["iterations"],
        batch_size=batch,
        learning_rate=0.0003,
        temperature=1.0,
        temperature_mode="constant",
        distance="cosine",
        device="cpu",
        verbose=False,
        time_offsets=1,
        conditional=None,
        hybrid=False,
    )

    def check(step, solver):
        if time.monotonic() - started > config["limits"]["native_fit_seconds"]:
            raise TimeoutError("native multisession fitting deadline exceeded")
        if not all(
            np.isfinite(solver.log[key][-1])
            for key in ("total", "pos", "neg", "temperature")
        ):
            raise ValueError("nonfinite native loss")

    previous_threads = torch.get_num_threads()
    previous_numpy = np.random.get_state()
    try:
        torch.set_num_threads(1)
        np.random.seed(seed + 3011)
        with torch.random.fork_rng(devices=[]):
            torch.manual_seed(seed + 3011)
            estimator.fit(xs, ys, callback=check, callback_frequency=1)
    finally:
        np.random.set_state(previous_numpy)
        torch.set_num_threads(previous_threads)
    assert estimator.solver_name_ == "multi-session" and estimator.num_sessions_ == len(
        columns
    )
    loss = {
        key: np.asarray(estimator.solver_.log[key], float).tolist()
        for key in ("total", "pos", "neg", "temperature")
    }
    assert len(loss["total"]) == config["iterations"]
    if any(not torch.isfinite(p).all().item() for p in estimator.model_.parameters()):
        raise ValueError("nonfinite native parameters")
    diag = dict(
        objective="joint-pair supervised native discrete multisession",
        loss=loss,
        iterations=config["iterations"],
        seed=seed,
        sampler_seed=seed + 3011,
        wall_seconds=time.monotonic() - started,
        torch_threads=1,
        sessions=len(columns),
        session_input_dimensions=[len(c) for c in columns],
        batch_per_session=batch,
        references_per_update=batch * len(columns),
        aggregation="equal-session mean of aligned embeddings per cue bin",
        training_vectors_per_session=[len(x) for x in xs],
        exposure_summary={
            "reference_draws": config["iterations"] * batch * len(columns)
        },
    )
    return NativeMultisessionFit(estimator, standardizer, columns, diag)


def fit_decoder(name, x, y, config, ratio, seed):
    if name == "logistic":
        return fit_logistic(
            x,
            y,
            C=config["base_logistic_C"] * ratio,
            max_iter=config["logistic_max_iter"],
        )
    if name == "lda":
        return fit_lda(x, y)
    classifier = (
        SVC(
            C=ratio,
            kernel="rbf",
            gamma="scale",
            class_weight="balanced",
            probability=False,
            tol=0.001,
            max_iter=100000,
            cache_size=200,
            random_state=seed,
        )
        if name == "svm"
        else KNeighborsClassifier(
            n_neighbors=5,
            weights="uniform",
            metric="euclidean",
            algorithm="brute",
            n_jobs=2,
        )
    )
    model = make_pipeline(StandardScaler(), classifier)
    with warnings.catch_warnings(), threadpool_limits(limits=2):
        warnings.simplefilter("error", ConvergenceWarning)
        model.fit(x, y)
    if name == "svm" and classifier.fit_status_ != 0:
        raise RuntimeError("SVM did not converge")
    return model


def train_case(case, data, train_plan, dev_plan, *, meta, config, run_root):
    from neuro import cebra

    root = Path(run_root) / "cases" / case["id"]
    root.mkdir(parents=True, exist_ok=False, mode=0o700)
    started = time.monotonic()
    train, dev = materialize(data, train_plan), materialize(data, dev_plan)
    by_id = {s.source_id: s for s in data.sources}
    unions = [
        {
            v
            for row in a.plan.rows
            for sid in row.source_ids
            for v in (sid, *by_id[sid].dependency_ids)
        }
        for a in (train, dev)
    ]
    if unions[0] & unions[1]:
        raise ValueError("training/development contributor overlap")
    identities = {
        split: plan_digest(a.plan, a.block_ids, a.unit_ids)
        for split, a in [("train", train), ("development", dev)]
    }
    write_json(
        root / "case.json",
        dict(
            **case,
            plan_identities=identities,
            units=list(train.unit_ids),
            blocks=list(train.block_ids),
            train_rows=len(train.values),
            development_rows=len(dev.values),
        ),
    )
    for split, a in [("train", train), ("development", dev)]:
        write_json(
            root / (split + "_lineage.json"),
            dict(
                identity=identities[split],
                policy=a.plan.policy,
                blocks=list(a.block_ids),
                units=list(a.unit_ids),
                rows=[
                    dict(
                        row_id=r.row_id, pair=r.condition, source_ids=list(r.source_ids)
                    )
                    for r in a.plan.rows
                ],
            ),
        )
    yt, yd = target_heads(train), target_heads(dev)
    ratio = 16 * len(set(yt["pair"])) / len(train.values)
    dimension = config["output_dimension"]
    representations = {
        "raw": fit_standardizer(train.values),
        "pca": fit_pca(train.values, n_components=dimension),
        "cebra": cebra.fit(
            train.values,
            train.targets,
            iterations=config["iterations"],
            batch_size=config["batch_size"],
            output_dimension=dimension,
            hidden=config["hidden"],
            learning_rate=config["learning_rate"],
            seed=case["seed"],
            max_seconds=config["limits"]["cebra_fit_seconds"],
            device="cpu",
        ),
        "native": fit_native(
            train.values,
            train.targets,
            data.units,
            data.block_ids,
            config,
            case["seed"],
        ),
    }
    metrics, confusions, error_rows, class_errors, state_hashes, projections = (
        [],
        [],
        [],
        [],
        {},
        {},
    )
    arrays = dict(train_values=train.values, development_values=dev.values)
    for name, encoder in representations.items():
        tr, dv = encoder.transform(train.values), encoder.transform(dev.values)
        if name == "raw":
            tr, dv = raw_features(tr), raw_features(dv)
        else:
            projections[name] = dv.reshape(len(dv), 10, dimension).copy()
        arrays[name + "_train_features"], arrays[name + "_development_features"] = (
            tr,
            dv,
        )
        state = root / (name + "_encoder.joblib")
        joblib.dump(encoder, state, compress=3)
        state.chmod(0o600)
        state_hashes[state.name] = sha(state)
        with frozen_models():
            restored = joblib.load(state)
            rt, rd = restored.transform(train.values), restored.transform(dev.values)
            if name == "raw":
                rt, rd = raw_features(rt), raw_features(rd)
            np.testing.assert_allclose(rt, tr, rtol=1e-5, atol=1e-5)
            np.testing.assert_allclose(rd, dv, rtol=1e-5, atol=1e-5)
        for decoder in DECODERS:
            family = name if decoder == "logistic" else name + "_" + decoder
            for head in ("pair", "start", "goal"):
                model = fit_decoder(decoder, tr, yt[head], config, ratio, case["seed"])
                tp, dp = model.predict(tr), model.predict(dv)
                score_method = (
                    "decision_function" if decoder == "svm" else "predict_proba"
                )
                ts, ds = (
                    getattr(model, score_method)(tr),
                    getattr(model, score_method)(dv),
                )
                if not np.isfinite(ts).all() or not np.isfinite(ds).all():
                    raise ValueError("nonfinite readout scores")
                mt = classification_metrics(
                    yt[head],
                    tp,
                    classes=model.classes_,
                    probabilities=None if decoder == "svm" else ts,
                )
                md = classification_metrics(
                    yd[head],
                    dp,
                    classes=model.classes_,
                    probabilities=None if decoder == "svm" else ds,
                )
                record = dict(
                    **case,
                    representation=family,
                    encoder=name,
                    decoder=decoder,
                    head=head,
                    units=len(data.units),
                    sessions=len(data.block_ids),
                    classes=len(model.classes_),
                    train_rows=len(tr),
                    development_rows=len(dv),
                    readout_features=tr.shape[1],
                    logistic_C=config["base_logistic_C"] * ratio
                    if decoder == "logistic"
                    else "",
                    svm_C=ratio if decoder == "svm" else "",
                    train_BA=mt["balanced_accuracy"],
                    train_development_gap=mt["balanced_accuracy"]
                    - md["balanced_accuracy"],
                    **{
                        k: md.get(k)
                        for k in (
                            "accuracy",
                            "balanced_accuracy",
                            "macro_f1",
                            "log_loss",
                        )
                    },
                )
                metrics.append(record)
                labels = [str(c) for c in model.classes_]
                counts = np.asarray(md["confusion_counts"])
                if counts.sum() != len(dv) or not np.isclose(
                    np.mean(np.diag(counts) / counts.sum(1)), md["balanced_accuracy"]
                ):
                    raise ValueError("confusion reconciliation failed")
                confusions.append(
                    dict(
                        **case,
                        representation=family,
                        encoder=name,
                        decoder=decoder,
                        head=head,
                        labels=labels,
                        counts=counts.tolist(),
                    )
                )
                readout = family + "_" + head
                for prefix, truth, pred, scores in [
                    ("", yd[head], dp, ds),
                    ("_train", yt[head], tp, ts),
                ]:
                    arrays[readout + prefix + "_truth"] = truth
                    arrays[readout + prefix + "_prediction"] = pred
                    arrays[
                        readout
                        + prefix
                        + ("_margins" if decoder == "svm" else "_probabilities")
                    ] = scores
                model_path = root / (readout + "_readout.joblib")
                joblib.dump(model, model_path, compress=3)
                model_path.chmod(0o600)
                state_hashes[model_path.name] = sha(model_path)
                with frozen_models():
                    if (
                        sha(state) != state_hashes[state.name]
                        or sha(model_path) != state_hashes[model_path.name]
                    ):
                        raise ValueError("new state hash drift")
                    loaded = joblib.load(model_path)
                    for x, p, scores in ((rt, tp, ts), (rd, dp, ds)):
                        np.testing.assert_array_equal(loaded.predict(x), p)
                        np.testing.assert_allclose(
                            getattr(loaded, score_method)(x),
                            scores,
                            rtol=1e-7,
                            atol=1e-7,
                        )
                wrong = dp != yd[head]
                appearances, errors = Counter(), Counter()
                for row, error in zip(dev_plan.rows, wrong, strict=True):
                    appearances.update(row.source_ids)
                    if error:
                        errors.update(row.source_ids)
                for sid in sorted(appearances):
                    total, incorrect = appearances[sid], errors[sid]
                    error_rows.append(
                        dict(
                            case=case["id"],
                            representation=family,
                            head=head,
                            assembly_identity=identities["development"],
                            source=meta["source_aliases"][sid],
                            session=meta["aliases"][by_id[sid].block_id],
                            appearances=total,
                            wrong_appearances=incorrect,
                            correct_appearances=total - incorrect,
                            wrong_fraction=incorrect / total,
                        )
                    )
                assert sum(errors.values()) == int(wrong.sum()) * len(data.block_ids)
                for label in labels:
                    choose = np.asarray([str(v) == label for v in yd[head]])
                    class_errors.append(
                        dict(
                            case=case["id"],
                            representation=family,
                            head=head,
                            **{"class": label},
                            evaluated_rows=int(choose.sum()),
                            wrong_rows=int(wrong[choose].sum()),
                            error_rate=float(wrong[choose].mean()),
                        )
                    )
    np.savez_compressed(root / "numeric_records.npz", **arrays)
    (root / "numeric_records.npz").chmod(0o600)
    pool_rows, source_rows, overlaps = [], [], []
    for plan in (train_plan, dev_plan):
        p, s = usage_tables(data, plan, meta, case["id"])
        pool_rows.extend(p)
        source_rows.extend(s)
        overlaps.extend(
            dict(case=case["id"], split=plan.split_id, **r)
            for r in overlap_summary(plan)
        )
    learning = [
        dict(
            case=case["id"] + "_" + name,
            encoder=name,
            **{
                k: representations[name].diagnostics[k]
                for k in (
                    "loss",
                    "iterations",
                    "seed",
                    "sampler_seed",
                    "wall_seconds",
                    "exposure_summary",
                )
            },
        )
        for name in ("cebra", "native")
    ]
    trajectories = {
        name: {
            str(label): z[np.asarray(yd["pair"]) == label, :, :3].mean(0).tolist()
            for label in sorted(set(yd["pair"]))
        }
        for name, z in projections.items()
    }
    counts = dict(
        cebra=1,
        native=1,
        pca=1,
        logistic=12,
        lda=12,
        svm=12,
        knn=12,
        optimizer_updates=2 * config["iterations"],
    )
    for filename, obj in [
        ("metrics", metrics),
        ("confusions", confusions),
        ("learning", learning),
        ("trajectories", trajectories),
        ("native_diagnostics", representations["native"].diagnostics),
    ]:
        write_json(root / (filename + ".json"), obj)
    write_json(
        root / "completion.json",
        dict(
            **case,
            fit_counts=counts,
            state_sha256=state_hashes,
            numeric_sha256=sha(root / "numeric_records.npz"),
            artifact_sha256={
                p.name: sha(p) for p in sorted(root.iterdir()) if p.is_file()
            },
            paired_contributors_overlap=0,
            wall_seconds=time.monotonic() - started,
            reloaded_readouts_checked=48,
            composed_readout_splits_checked=96,
            reloaded_encoders_checked=4,
            native_session_encoders=len(data.block_ids),
            plan_identities=identities,
        ),
    )
    return dict(
        metrics=metrics,
        confusions=confusions,
        pool_usage=pool_rows,
        source_usage=source_rows,
        source_errors=error_rows,
        class_errors=class_errors,
        overlap=overlaps,
        trajectories=dict(case=case["id"], coordinates=trajectories),
        learning=learning,
        fit_counts=counts,
    )
