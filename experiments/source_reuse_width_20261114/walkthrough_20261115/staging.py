"""Experiment-local staged persistence; fitting is visible in the notebooks.

The saving, scoring and guarded reload operations retain the accepted
population_models.train_case contract. The invented equivalence gate compares
both paths numerically. No package API or scientific estimator is changed.
"""

from __future__ import annotations
import time
from collections import Counter
from pathlib import Path
import joblib
import numpy as np
from neuro.evaluation import classification_metrics
from neuro.notebook_artifacts import target_heads
from neuro.pca_lda import raw_features
from neuro.pseudopopulation import materialize
from neuro.studies.population_models import (
    ENCODERS,
    DECODERS,
    frozen_models,
)
from neuro.studies.source_support_ablation import (
    plan_digest,
    usage_tables,
    overlap_summary,
    sha,
    write_json,
)


class StagedCase:
    def __init__(self, case, data, train_plan, dev_plan, *, meta, config, run_root):
        self.case, self.data = case, data
        self.train_plan, self.dev_plan = train_plan, dev_plan
        self.meta, self.config = meta, config
        self.representations, self.features = {}, {}
        self.readout_keys = []
        self.finished = False
        self.root = Path(run_root) / "cases" / self.case["id"]
        self.root.mkdir(parents=True, exist_ok=False, mode=448)
        self.started = time.monotonic()
        self.train, self.dev = (
            materialize(self.data, self.train_plan),
            materialize(self.data, self.dev_plan),
        )
        self.by_id = {s.source_id: s for s in self.data.sources}
        unions = [
            {
                v
                for row in a.plan.rows
                for sid in row.source_ids
                for v in (sid, *self.by_id[sid].dependency_ids)
            }
            for a in (self.train, self.dev)
        ]
        if unions[0] & unions[1]:
            raise ValueError("training/development contributor overlap")
        self.identities = {
            split: plan_digest(a.plan, a.block_ids, a.unit_ids)
            for split, a in [("train", self.train), ("development", self.dev)]
        }
        write_json(
            self.root / "case.json",
            dict(
                **self.case,
                plan_identities=self.identities,
                units=list(self.train.unit_ids),
                blocks=list(self.train.block_ids),
                train_rows=len(self.train.values),
                development_rows=len(self.dev.values),
            ),
        )
        for split, a in [("train", self.train), ("development", self.dev)]:
            write_json(
                self.root / (split + "_lineage.json"),
                dict(
                    identity=self.identities[split],
                    policy=a.plan.policy,
                    blocks=list(a.block_ids),
                    units=list(a.unit_ids),
                    rows=[
                        dict(
                            row_id=r.row_id,
                            pair=r.condition,
                            source_ids=list(r.source_ids),
                        )
                        for r in a.plan.rows
                    ],
                ),
            )
        self.yt, self.yd = (target_heads(self.train), target_heads(self.dev))
        self.ratio = 16 * len(set(self.yt["pair"])) / len(self.train.values)
        self.dimension = self.config["output_dimension"]
        (
            self.metrics,
            self.confusions,
            self.error_rows,
            self.class_errors,
            self.state_hashes,
            self.projections,
        ) = ([], [], [], [], {}, {})
        self.arrays = dict(
            train_values=self.train.values, development_values=self.dev.values
        )

    def record_representation(self, name, encoder):
        """Transform/save/reload one already fitted encoder; never fit here."""
        if self.finished or name != ENCODERS[len(self.representations)]:
            raise ValueError("representation sequence changed")
        self.representations[name] = encoder
        tr, dv = (
            encoder.transform(self.train.values),
            encoder.transform(self.dev.values),
        )
        if name == "raw":
            tr, dv = (raw_features(tr), raw_features(dv))
        else:
            self.projections[name] = dv.reshape(len(dv), 10, self.dimension).copy()
        (
            self.arrays[name + "_train_features"],
            self.arrays[name + "_development_features"],
        ) = (tr, dv)
        state = self.root / (name + "_encoder.joblib")
        joblib.dump(encoder, state, compress=3)
        state.chmod(384)
        self.state_hashes[state.name] = sha(state)
        with frozen_models():
            restored = joblib.load(state)
            rt, rd = (
                restored.transform(self.train.values),
                restored.transform(self.dev.values),
            )
            if name == "raw":
                rt, rd = (raw_features(rt), raw_features(rd))
            np.testing.assert_allclose(rt, tr, rtol=1e-05, atol=1e-05)
            np.testing.assert_allclose(rd, dv, rtol=1e-05, atol=1e-05)

        self.features[name] = (tr, dv, rt, rd, state)
        return tr, dv

    def record_readout(self, name, decoder, head, model):
        """Score/save/reload one already fitted readout on both splits."""
        expected = [
            (e, d, h)
            for e in ENCODERS
            for d in DECODERS
            for h in ("pair", "start", "goal")
        ]
        if self.finished or (name, decoder, head) != expected[len(self.readout_keys)]:
            raise ValueError("readout sequence changed")
        tr, dv, rt, rd, state = self.features[name]
        family = name if decoder == "logistic" else name + "_" + decoder
        tp, dp = (model.predict(tr), model.predict(dv))
        score_method = "decision_function" if decoder == "svm" else "predict_proba"
        ts, ds = (getattr(model, score_method)(tr), getattr(model, score_method)(dv))
        if not np.isfinite(ts).all() or not np.isfinite(ds).all():
            raise ValueError("nonfinite readout scores")
        mt = classification_metrics(
            self.yt[head],
            tp,
            classes=model.classes_,
            probabilities=None if decoder == "svm" else ts,
        )
        md = classification_metrics(
            self.yd[head],
            dp,
            classes=model.classes_,
            probabilities=None if decoder == "svm" else ds,
        )
        record = dict(
            **self.case,
            representation=family,
            encoder=name,
            decoder=decoder,
            head=head,
            units=len(self.data.units),
            sessions=len(self.data.block_ids),
            classes=len(model.classes_),
            train_rows=len(tr),
            development_rows=len(dv),
            readout_features=tr.shape[1],
            logistic_C=self.config["base_logistic_C"] * self.ratio
            if decoder == "logistic"
            else "",
            svm_C=self.ratio if decoder == "svm" else "",
            train_BA=mt["balanced_accuracy"],
            train_development_gap=mt["balanced_accuracy"] - md["balanced_accuracy"],
            **{
                k: md.get(k)
                for k in ("accuracy", "balanced_accuracy", "macro_f1", "log_loss")
            },
        )
        self.metrics.append(record)
        labels = [str(c) for c in model.classes_]
        counts = np.asarray(md["confusion_counts"])
        if counts.sum() != len(dv) or not np.isclose(
            np.mean(np.diag(counts) / counts.sum(1)), md["balanced_accuracy"]
        ):
            raise ValueError("confusion reconciliation failed")
        self.confusions.append(
            dict(
                **self.case,
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
            ("", self.yd[head], dp, ds),
            ("_train", self.yt[head], tp, ts),
        ]:
            self.arrays[readout + prefix + "_truth"] = truth
            self.arrays[readout + prefix + "_prediction"] = pred
            self.arrays[
                readout
                + prefix
                + ("_margins" if decoder == "svm" else "_probabilities")
            ] = scores
        model_path = self.root / (readout + "_readout.joblib")
        joblib.dump(model, model_path, compress=3)
        model_path.chmod(384)
        self.state_hashes[model_path.name] = sha(model_path)
        with frozen_models():
            if (
                sha(state) != self.state_hashes[state.name]
                or sha(model_path) != self.state_hashes[model_path.name]
            ):
                raise ValueError("new state hash drift")
            loaded = joblib.load(model_path)
            for x, p, scores in ((rt, tp, ts), (rd, dp, ds)):
                np.testing.assert_array_equal(loaded.predict(x), p)
                np.testing.assert_allclose(
                    getattr(loaded, score_method)(x), scores, rtol=1e-07, atol=1e-07
                )
        wrong = dp != self.yd[head]
        appearances, errors = (Counter(), Counter())
        for row, error in zip(self.dev_plan.rows, wrong, strict=True):
            appearances.update(row.source_ids)
            if error:
                errors.update(row.source_ids)
        for sid in sorted(appearances):
            total, incorrect = (appearances[sid], errors[sid])
            self.error_rows.append(
                dict(
                    case=self.case["id"],
                    representation=family,
                    head=head,
                    assembly_identity=self.identities["development"],
                    source=self.meta["source_aliases"][sid],
                    session=self.meta["aliases"][self.by_id[sid].block_id],
                    appearances=total,
                    wrong_appearances=incorrect,
                    correct_appearances=total - incorrect,
                    wrong_fraction=incorrect / total,
                )
            )
        assert sum(errors.values()) == int(wrong.sum()) * len(self.data.block_ids)
        for label in labels:
            choose = np.asarray([str(v) == label for v in self.yd[head]])
            self.class_errors.append(
                dict(
                    case=self.case["id"],
                    representation=family,
                    head=head,
                    **{"class": label},
                    evaluated_rows=int(choose.sum()),
                    wrong_rows=int(wrong[choose].sum()),
                    error_rate=float(wrong[choose].mean()),
                )
            )

        self.readout_keys.append((name, decoder, head))
        return record

    def finish(self):
        """Close a fully fitted case and authenticate all its persisted outputs."""
        if (
            self.finished
            or len(self.representations) != 4
            or len(self.readout_keys) != 48
        ):
            raise ValueError("case incomplete or already closed")
        self.finished = True
        # Match the original encoder-by-encoder archive order even though the
        # teaching cells expose all representation fits before the readout loop.
        ordered = {k: self.arrays[k] for k in ("train_values", "development_values")}
        for name in ENCODERS:
            ordered.update(
                {k: v for k, v in self.arrays.items() if k.startswith(name + "_")}
            )
        assert set(ordered) == set(self.arrays)
        np.savez_compressed(self.root / "numeric_records.npz", **ordered)
        (self.root / "numeric_records.npz").chmod(384)
        pool_rows, source_rows, overlaps = ([], [], [])
        for plan in (self.train_plan, self.dev_plan):
            p, s = usage_tables(self.data, plan, self.meta, self.case["id"])
            pool_rows.extend(p)
            source_rows.extend(s)
            overlaps.extend(
                (
                    dict(case=self.case["id"], split=plan.split_id, **r)
                    for r in overlap_summary(plan)
                )
            )
        learning = [
            dict(
                case=self.case["id"] + "_" + name,
                encoder=name,
                **{
                    k: self.representations[name].diagnostics[k]
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
                str(label): z[np.asarray(self.yd["pair"]) == label, :, :3]
                .mean(0)
                .tolist()
                for label in sorted(set(self.yd["pair"]))
            }
            for name, z in self.projections.items()
        }
        counts = dict(
            cebra=1,
            native=1,
            pca=1,
            logistic=12,
            lda=12,
            svm=12,
            knn=12,
            optimizer_updates=2 * self.config["iterations"],
        )
        for filename, obj in [
            ("metrics", self.metrics),
            ("confusions", self.confusions),
            ("learning", learning),
            ("trajectories", trajectories),
            ("native_diagnostics", self.representations["native"].diagnostics),
        ]:
            write_json(self.root / (filename + ".json"), obj)
        write_json(
            self.root / "completion.json",
            dict(
                **self.case,
                fit_counts=counts,
                state_sha256=self.state_hashes,
                numeric_sha256=sha(self.root / "numeric_records.npz"),
                artifact_sha256={
                    p.name: sha(p) for p in sorted(self.root.iterdir()) if p.is_file()
                },
                paired_contributors_overlap=0,
                wall_seconds=time.monotonic() - self.started,
                reloaded_readouts_checked=48,
                composed_readout_splits_checked=96,
                reloaded_encoders_checked=4,
                native_session_encoders=len(self.data.block_ids),
                plan_identities=self.identities,
            ),
        )
        return dict(
            metrics=self.metrics,
            confusions=self.confusions,
            pool_usage=pool_rows,
            source_usage=source_rows,
            source_errors=self.error_rows,
            class_errors=self.class_errors,
            overlap=overlaps,
            trajectories=dict(case=self.case["id"], coordinates=trajectories),
            learning=learning,
            fit_counts=counts,
        )
