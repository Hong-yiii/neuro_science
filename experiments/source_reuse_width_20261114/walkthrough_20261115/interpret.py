"""Data-driven prose for this execution; no models, fits or previous-run imports."""

import csv
import html
from collections import defaultdict
from pathlib import Path
from scripts.source_support_report import table

NAMES = {
    "raw": "Raw",
    "pca": "PCA7",
    "cebra": "CEBRA-Time7",
    "native": "Native multisession7",
}


def explain(run, part, scores, contrasts):
    arms = ("B2", "B3", "B5", "U3") if part == "reuse" else ("B3", "Wmid", "Wfull")
    indexed = {(r["arm"], r["encoder"], r["decoder"], r["head"]): r for r in scores}
    rows = []
    for encoder, name in NAMES.items():
        rows.append(
            dict(
                encoder=name,
                **{
                    arm: f"{100 * indexed[arm, encoder, 'svm', 'pair']['observed_mean']:.2f}%"
                    for arm in arms
                },
            )
        )
    result = [
        "<p><strong>RBF-SVM pair balanced accuracy, mean of3computational repeats:</strong></p>",
        table(rows),
    ]
    if part == "reuse":
        separate = []
        for e in NAMES:
            r = indexed["U3", e, "svm", "pair"]
            if r["all_observed_above_five_diagnostics"]:
                separate.append(NAMES[e])
        result.append(
            "<p>Once-only assembly: "
            + (", ".join(separate) if separate else "no SVM encoder")
            + " has every observed pair score above all five source-label diagnostic scores. For these pipelines, repeated assembly copies are not necessary for the observed endpoint association. This does not validate every readout/head or eliminate label-conditioned construction and exposed-development limitations.</p>"
        )
        values = [
            r
            for r in contrasts
            if (r["before"], r["after"], r["decoder"], r["head"])
            == ("U3", "B3", "svm", "pair")
        ]
        result.append(
            "<p>B3−U3 holds source identities fixed: "
            + "; ".join(
                f"{NAMES[r['encoder']]} {100 * r['observed_mean']:+.2f} percentage points"
                for r in values
            )
            + ". "
            + str(sum(r["all_observed_above_diagnostic_contrasts"] for r in values))
            + " of these four contrasts has all observed changes above all five diagnostic changes. "
            + (
                "All four mean differences favor B3."
                if all(r["observed_mean"] > 0 for r in values)
                else "More repeated rows do not yield a positive mean change in every pipeline."
            )
            + "</p>"
        )
    else:
        monotonic = []
        for decoder in ("logistic", "svm", "knn", "lda"):
            values = [indexed[a, "pca", decoder, "pair"]["observed_mean"] for a in arms]
            if values[0] < values[1] < values[2]:
                monotonic.append(decoder)
        result.append(
            "<p>PCA mean pair recovery increases at both width steps with "
            + (", ".join(monotonic) if monotonic else "no readout")
            + ". This is a mean-score pattern; not every seed or endpoint head must improve. Raw, Time and native comparisons must be read with their own decoder and repeat results.</p>"
        )
        r = next(
            r
            for r in contrasts
            if (r["before"], r["after"], r["encoder"], r["decoder"], r["head"])
            == ("Wmid", "Wfull", "pca", "svm", "pair")
        )
        result.append(
            f"<p>For PCA/SVM49→83columns, mean pair gain={100 * r['observed_mean']:+.2f} points; observed changes span{100 * r['observed_min']:+.2f}to{100 * r['observed_max']:+.2f}, with{r['positive_repeats']}/3positive repeats. Five diagnostic changes span{100 * r['diagnostic_min']:+.2f}to{100 * r['diagnostic_max']:+.2f}.</p>"
            + (
                "<p>All three changes are positive in this comparison.</p>"
                if r["positive_repeats"] == 3
                else "<p>This width change does not improve all three repeats.</p>"
            )
        )
    separated = [
        dict(
            contrast=r["after"] + " − " + r["before"],
            encoder=NAMES[r["encoder"]],
            mean_change_pp=round(100 * r["observed_mean"], 2),
            observed_range_pp=f"{100 * r['observed_min']:.2f}…{100 * r['observed_max']:.2f}",
            diagnostic_range_pp=f"{100 * r['diagnostic_min']:.2f}…{100 * r['diagnostic_max']:.2f}",
        )
        for r in contrasts
        if r["decoder"] == "svm"
        and r["head"] == "pair"
        and r["all_observed_above_diagnostic_contrasts"]
    ]
    result.extend(
        [
            "<p>SVM pair contrasts with all three observed changes above all five diagnostic changes (descriptive, no calibrated significance test):</p>",
            table(separated) if separated else "<p>None.</p>",
        ]
    )
    folder = Path(run) / ("report_" + part)
    with (folder / "class_recall.csv").open() as handle:
        recalls = list(csv.DictReader(handle))
    with (folder / "best_worst.csv").open() as handle:
        ranked = list(csv.DictReader(handle))
    groups = defaultdict(list)
    for row in recalls:
        if (row["world"], row["head"], row["split"]) == (
            "observed",
            "pair",
            "development",
        ):
            groups[row["arm"], row["encoder"], row["decoder"], row["label"]].append(
                float(row["recall"])
            )
    labels = sorted({key[-1] for key in groups})
    errors = []
    for row in ranked:
        for label in labels:
            worst = groups[row["worst"], row["encoder"], row["decoder"], label]
            best = groups[row["best"], row["encoder"], row["decoder"], label]
            assert len(worst) == len(best) == 3
            errors.append(
                dict(
                    encoder=row["encoder"],
                    decoder=row["decoder"],
                    label=label,
                    worst=row["worst"],
                    best=row["best"],
                    worst_mean_recall=sum(worst) / 3,
                    best_mean_recall=sum(best) / 3,
                    change_pp=100 * (sum(best) - sum(worst)) / 3,
                )
            )
    result.extend(
        [
            "<details><summary>Every class change for the selected best/worst comparisons</summary>",
            table(errors),
            "</details>",
        ]
    )
    result.append(
        "<p>Best/worst selection is post-hoc within a fixed encoder/readout. A higher aggregate score may coexist with worse recall for some classes. No class is removed here, and session-group changes cannot identify an individually harmful session. Issue#29requires authenticated field maps, occupancy/reliability and coordinate joins; issue#30spatial selectivity remains untested.</p>"
    )
    return "".join(result)


def confusion_explorer(run, part):
    """Embed the tested report explorer and all its matrices, with no external file."""
    document = (Path(run) / ("report_" + part) / "report.html").read_text()
    assert document.count("<script>") == document.count("</script>") == 1
    script = document[
        document.index("<script>") : document.index("</script>") + len("</script>")
    ]
    content = (
        """<!doctype html><html><head><meta charset="utf-8"><style>
body{font:14px/1.5 system-ui;color:#172c40}label{display:inline-block;margin:5px}
select{padding:4px}table{border-collapse:collapse}td,th{padding:5px;border:1px solid #ccd6df;text-align:right}
</style></head><body><p>All observed/control cases, readouts, heads and both splits. Rows=true; columns=predicted.
Pair N=72development rows (144training,27forU3). Endpoint heads share rows. No independence claim.</p>
<div id="explorer"></div>"""
        + script
        + "</body></html>"
    )
    return (
        '<iframe title="Complete confusion explorer" style="width:100%;height:610px;border:1px solid #ccd6df" srcdoc="'
        + html.escape(content, quote=True)
        + '"></iframe>'
    )
