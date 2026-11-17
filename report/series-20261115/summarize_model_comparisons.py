#!/usr/bin/env python3
"""Exploratory, post-hoc summaries of authenticated saved pair scores only."""

import csv
from decimal import Decimal, ROUND_HALF_EVEN, localcontext
from fractions import Fraction
import hashlib
import io
import json
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[2]
REPORT = Path("report/series-20261115")
SOURCE = REPORT / "data/case_scores.csv"
SOURCE_COMMIT = "6f362603d302d07de6cc33d80c846e1df92efe17"
SOURCE_SHA256 = "1661ff9d7b55644d586ad8efb21a440032c23d18f0121767100fd162acb89249"
SCHEMA = (
    "world", "seed", "arm", "encoder", "decoder", "head", "balanced_accuracy",
    "accuracy", "macro_f1", "log_loss", "train_BA", "train_development_gap",
)
ARMS = ("B2", "B3", "B5", "U3", "Wmid", "Wfull")
DECODERS = ("logistic", "svm", "knn", "lda")
ENCODERS = {"raw": "Raw", "pca": "PCA", "cebra": "Time", "native": "Native"}
SEEDS = ("0", "1", "2")


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def percentage(value, display=False):
    with localcontext() as context:
        context.prec = 50
        context.rounding = ROUND_HALF_EVEN
        number = Decimal(value.numerator) * 100 / Decimal(value.denominator)
        return format(number, ".2f" if display else ".17g")


def csv_bytes(rows):
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue().encode("utf-8")


def main():
    source = (ROOT / SOURCE).read_bytes()
    committed = subprocess.run(
        ["git", "show", f"{SOURCE_COMMIT}:{SOURCE.as_posix()}"],
        cwd=ROOT, check=True, capture_output=True,
    ).stdout
    if source != committed or sha256(source) != SOURCE_SHA256:
        raise ValueError("case_scores.csv differs from the authenticated source")
    reader = csv.DictReader(io.StringIO(source.decode("utf-8"), newline=""))
    if tuple(reader.fieldnames or ()) != SCHEMA:
        raise ValueError("unexpected case-score schema")
    rows = list(reader)
    worlds = {"observed": SEEDS}
    worlds.update({f"permuted{i}": ("0",) for i in range(61000, 61005)})
    expected = {
        (world, seed, arm, encoder, decoder, head)
        for world, seeds in worlds.items() for seed in seeds
        for arm in ARMS for encoder in ENCODERS for decoder in DECODERS
        for head in ("pair", "start", "goal")
    }
    seen, scores = set(), {}
    for row in rows:
        if None in row or None in row.values():
            raise ValueError("malformed case-score row")
        key = tuple(row[name] for name in SCHEMA[:6])
        if key in seen:
            raise ValueError("duplicate case-score key")
        seen.add(key)
        if row["world"] == "observed" and row["head"] == "pair":
            score = Fraction(row["balanced_accuracy"])
            if not 0 <= score <= 1:
                raise ValueError("pair balanced accuracy outside [0, 1]")
            scores[row["arm"], row["decoder"], row["encoder"], row["seed"]] = score
    if seen != expected or len(rows) != 2304 or len(scores) != 288:
        raise ValueError("incomplete or unexpected case-score grid")

    means, mean_rows, best_rows, best = {}, [], [], {}
    for arm in ARMS:
        for decoder in DECODERS:
            for encoder, label in ENCODERS.items():
                values = [scores[arm, decoder, encoder, seed] for seed in SEEDS]
                mean = sum(values) / len(values)
                means[arm, decoder, encoder] = mean
                mean_rows.append({
                    "arm": arm, "decoder": decoder, "encoder": encoder,
                    "representation": label,
                    **{f"seed{seed}_pair_BA_percent": percentage(value)
                       for seed, value in zip(SEEDS, values)},
                    "mean_pair_BA_percent": percentage(mean),
                    "min_pair_BA_percent": percentage(min(values)),
                    "max_pair_BA_percent": percentage(max(values)),
                })
            maximum = max(means[arm, decoder, encoder] for encoder in ENCODERS)
            labels = [label for encoder, label in ENCODERS.items()
                      if means[arm, decoder, encoder] == maximum]
            best[arm, decoder] = (labels, maximum)
            best_rows.append({
                "arm": arm, "decoder": decoder,
                **{f"{label}_mean_pair_BA_percent": percentage(means[arm, decoder, encoder])
                   for encoder, label in ENCODERS.items()},
                "best_representation": "/".join(labels),
                "best_mean_pair_BA_percent": percentage(maximum),
            })

    tex_rows = []
    for arm in ARMS:
        cells = []
        for decoder in DECODERS:
            labels, maximum = best[arm, decoder]
            shown = "/".join(r"\textbf{" + label + "}" if label in ("Time", "Native")
                             else label for label in labels)
            cells.append(f"{shown} {percentage(maximum, display=True)}")
        tex_rows.append(arm + " & " + " & ".join(cells) + r" \\")
    outputs = {
        REPORT / "data/model_pair_means.csv": (csv_bytes(mean_rows), len(mean_rows)),
        REPORT / "data/model_pair_best_means.csv": (csv_bytes(best_rows), len(best_rows)),
        REPORT / "data/model_pair_best_rows.tex":
            ((r"\newcommand{\modelChoiceRows}{%" + "\n" + "\n".join(tex_rows)
              + "\n}\n").encode("utf-8"), len(tex_rows)),
    }
    script = Path(__file__).resolve()
    provenance = {
        "classification": "exploratory post-hoc saved-score summary",
        "generator": {"path": script.relative_to(ROOT).as_posix(),
                      "sha256": sha256(script.read_bytes())},
        "input": {"path": SOURCE.as_posix(), "commit": SOURCE_COMMIT,
                  "sha256": sha256(source), "bytes": len(source), "rows": len(rows),
                  "schema": list(SCHEMA), "matches_committed_bytes": True},
        "selection": {"world": "observed", "head": "pair", "seeds": list(SEEDS),
                      "arms": list(ARMS), "decoders": list(DECODERS),
                      "encoder_labels": ENCODERS, "selected_score_rows": len(scores)},
        "numeric_policy": {
            "metric": "development pair balanced accuracy, percentage scale",
            "aggregation": "exact rational arithmetic on source decimal strings; equal seed weights",
            "csv_precision": "17 significant decimal digits",
            "table_precision": "two decimal places, round half to even",
            "ranking": "highest unrounded three-seed mean within each arm and decoder",
            "ties": "retain every exactly tied highest mean; join labels with / in Raw/PCA/Time/Native order",
            "display_ties": "rounding may show equal values whose unrounded means differ",
            "range": "minimum and maximum of the three computational seed scores",
        },
        "interpretation": [
            "Rankings are post-hoc descriptions of three computational repeats.",
            "The rankings provide no validated model-selection procedure or significance test.",
            "All observed seeds share the same historically exposed development arrays at a fixed roster.",
            "Known-label construction and shared exposed development limit generalization claims.",
            "Seed ranges describe computational variation; biological uncertainty remains unestimated.",
            "A representation's ranking is conditional on the arm and readout.",
        ],
        "execution_scope": {"scientific_input": "case_scores.csv only",
                            "new_fits": 0, "model_loads": 0, "notebooks_executed": 0,
                            "metadata_or_old_results_regenerated": False},
        "exact_top_mean_ties": sum(len(labels) > 1 for labels, _ in best.values()),
        "outputs": {path.as_posix(): {"sha256": sha256(data), "bytes": len(data), "rows": count}
                    for path, (data, count) in outputs.items()},
    }
    for path, (data, _) in outputs.items():
        (ROOT / path).write_bytes(data)
    (ROOT / REPORT / "model-comparison-provenance.json").write_text(
        json.dumps(provenance, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"Wrote {len(mean_rows)} model means, {len(best_rows)} rankings and {len(tex_rows)} table rows.")


if __name__ == "__main__":
    main()
