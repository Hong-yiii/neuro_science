"""Actual invented fits validate that staging preserves every scientific result."""

import json
import time
import numpy as np
from .. import study
from .staging import StagedCase
from contextlib import nullcontext
from types import SimpleNamespace


def train_staged_case(case, data, train_plan, dev_plan, *, meta, config, run_root):
    """Execute the exact fitting/arithmetic cells used by both real notebooks."""
    import matplotlib.pyplot as plt
    from IPython.display import HTML
    from scipy.special import softmax
    from neuro import cebra
    from neuro.pca_lda import fit_standardizer, fit_pca
    from neuro.studies.population_models import (
        ENCODERS,
        DECODERS,
        fit_decoder,
        fit_native,
    )
    from scripts.source_support_report import table
    from .build_notebooks import make_notebook

    staged = StagedCase(
        case, data, train_plan, dev_plan, meta=meta, config=config, run_root=run_root
    )
    namespace = dict(
        case=staged,
        x_train=staged.train.values,
        x_dev=staged.dev.values,
        config=config,
        execution=SimpleNamespace(
            stage=lambda _: nullcontext(),
            accounting=SimpleNamespace(
                counts={"classification": "invented stage execution"}
            ),
        ),
        np=np,
        plt=plt,
        HTML=HTML,
        softmax=softmax,
        cebra=cebra,
        fit_standardizer=fit_standardizer,
        fit_pca=fit_pca,
        fit_native=fit_native,
        fit_decoder=fit_decoder,
        ENCODERS=ENCODERS,
        DECODERS=DECODERS,
        display=lambda *_: None,
        table=table,
    )
    reuse = [
        c.source
        for c in make_notebook("reuse").cells
        if c.cell_type == "code" and c.source.startswith("with execution.stage(")
    ]
    width = [
        c.source
        for c in make_notebook("width").cells
        if c.cell_type == "code" and c.source.startswith("with execution.stage(")
    ]
    assert reuse == width and len(width) == 7
    for source in width:
        exec(compile(source, "<actual-notebook-stage>", "exec"), namespace)
    return staged.finish()


def compare_paths(out, config, data, meta, plans):
    durations, results, paths = [], [], []
    accounting = study.GridFitAccounting(cebra=True).start()
    try:
        for label, fn in [
            ("original", study.train_case),
            ("staged", train_staged_case),
        ]:
            root = out / label
            root.mkdir()
            case = dict(
                id="invented_full_width", arm="benchmark", world="invented", seed=0
            )
            start = time.monotonic()
            results.append(fn(case, *plans, meta=meta, config=config, run_root=root))
            durations.append(time.monotonic() - start)
            paths.append(root / "cases" / case["id"])
    finally:
        counts = accounting.stop()
        study.write_json(out / "actual-fit-counts.json", counts)
    assert counts == {k: v // 24 for k, v in config["expected_fit_counts"].items()}
    checked = 0
    with (
        np.load(paths[0] / "numeric_records.npz", allow_pickle=False) as left,
        np.load(paths[1] / "numeric_records.npz", allow_pickle=False) as right,
    ):
        assert left.files == right.files
        for key in left.files:
            if left[key].dtype.kind in "SUO":
                np.testing.assert_array_equal(left[key], right[key])
            else:
                np.testing.assert_allclose(left[key], right[key], rtol=1e-7, atol=1e-7)
            checked += 1
    for filename in ("case.json", "train_lineage.json", "development_lineage.json"):
        assert json.loads((paths[0] / filename).read_text()) == json.loads(
            (paths[1] / filename).read_text()
        )
    for key in results[0]:
        if key != "learning":
            assert results[0][key] == results[1][key], key
        else:
            for a, b in zip(results[0][key], results[1][key], strict=True):
                assert {k: v for k, v in a.items() if k != "wall_seconds"} == {
                    k: v for k, v in b.items() if k != "wall_seconds"
                }
    for root in paths:
        done = json.loads((root / "completion.json").read_text())
        assert (
            done["reloaded_encoders_checked"] == 4
            and done["composed_readout_splits_checked"] == 96
        )
        assert all(study.sha(root / p) == h for p, h in done["artifact_sha256"].items())
    study.write_json(
        out / "equivalence.json",
        dict(
            status="passed",
            numeric_arrays=checked,
            complete_result_tables_equal=True,
            composed_split_checks=192,
            fit_counts=counts,
            seconds=durations,
            classification="invented software check; no biological evidence",
        ),
    )
    return counts, durations
