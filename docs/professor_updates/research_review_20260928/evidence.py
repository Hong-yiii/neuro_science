"""Saved-output aggregation and static SVG figures. Never imports model code or fits.

Run --extract with the existing NumPy runtime; normal rendering uses stdlib only.
The tracked aggregate contains no spike tensors, model state or trial identities.
"""

import csv
import gzip
import hashlib
import html
import io
import json
import math
import sys
from collections import Counter
from pathlib import Path
from statistics import mean
from zipfile import ZipFile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
TARGET = HERE / "evidence.json"
ENDPOINT = "outputs/start-goal-autoresearch-20260907"
BASELINE = "outputs/start-goal-cebra-20260907"
JOINT = "outputs/cebra-full-trial-transfer-20260924/biological-run-20260924T162913Z"
SOURCE = "outputs/prospective_path_first_run/place195-v6-v9-autoresearch-20260906/v7-v8-neural-experiments/primary29_min3train_min1val/bin100ms/source_level_cue_tensors.npz"
PAIRS = [(s, g) for s in range(1, 7) for g in range(1, 7) if s != g]
COLORS = ["#126e63", "#416db0", "#ad5420"]


def confusion(y, pred, classes):
    """Rows are true classes; reject missing/unknown classes rather than dropping them."""
    if len(y) != len(pred) or not y or len(set(classes)) != len(classes):
        raise ValueError("Invalid confusion inputs")
    index = {label: i for i, label in enumerate(classes)}
    matrix = [[0] * len(classes) for _ in classes]
    for truth, guess in zip(y, pred, strict=True):
        matrix[index[truth]][index[guess]] += 1
    if any(sum(row) == 0 for row in matrix):
        raise ValueError("Unsupported true class")
    return matrix


def normalize(matrix):
    if any(sum(row) <= 0 for row in matrix):
        raise ValueError("Cannot normalize an unsupported class")
    return [[100 * value / sum(row) for value in row] for row in matrix]


def accuracy(matrix):
    return sum(row[i] for i, row in enumerate(matrix)) / sum(map(sum, matrix))


def extract():
    import numpy as np  # Only saved numeric predictions/metadata; allow_pickle=False.

    provenance = {}

    def source(relative):
        path = ROOT / relative
        provenance[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
        return path

    def rows(relative):
        with source(relative).open(newline="") as handle:
            return list(csv.DictReader(handle))

    def obj(relative):
        return json.loads(source(relative).read_text())

    sources = rows(f"{BASELINE}/source_splits.csv")
    ids = [r["source_trial_id"] for r in sources]
    assert len(ids) == len(set(ids)) == 15553
    assert all(r["original_split"] == "train" for r in sources)
    support = rows(f"{BASELINE}/source_support.csv")
    assert len(support) == 1740
    counts = Counter((r["session_id"], r["label"], r["split"]) for r in sources)
    for r in support:
        for split in ("train", "validation"):
            assert counts[r["session_id"], r["label"], split] == int(r[split])
    distributions = {}
    for split in ("train", "validation"):
        pool = [r for r in sources if r["split"] == split]
        pairs = Counter(tuple(map(int, r["label"].split("->"))) for r in pool)
        distributions[split] = {
            "n": len(pool),
            "start": [sum(n for (s, _), n in pairs.items() if s == k) for k in range(1, 7)],
            "goal": [sum(n for (_, g), n in pairs.items() if g == k) for k in range(1, 7)],
            "pairs": [[None if s == g else pairs[s, g] for g in range(1, 7)] for s in range(1, 7)],
            "support_histogram": {str(value): count for value, count in sorted(Counter(int(r[split]) for r in support).items())},
        }
    assert [distributions[s]["n"] for s in ("train", "validation")] == [12288, 3265]

    # Hash/read selected ZIP members only: even provenance must avoid neural arrays.
    meta = {}
    with ZipFile(ROOT / SOURCE) as archive:
        for key in ("source_trial_ids", "source_session_ids", "source_splits", "source_labels"):
            member = key + ".npy"
            content = archive.read(member)
            provenance[SOURCE + "#" + member] = hashlib.sha256(content).hexdigest()
            meta[key] = np.load(io.BytesIO(content), allow_pickle=False).tolist()
    assert len(set(meta["source_trial_ids"])) == 104
    sessions = sorted(set(meta["source_session_ids"]))
    component_counts = Counter(zip(meta["source_session_ids"], meta["source_splits"], meta["source_labels"], strict=True))
    component = {
        "session_labels": [f"S{i + 1}" for i in range(len(sessions))],
        "columns": ["train absent", "train present", "validation absent", "validation present"],
        "counts": [[component_counts[s, split, label] for split in ("train", "validation") for label in ("absent", "present")] for s in sessions],
        "pseudorows": {},
    }
    assert [sum(row[i] for row in component["counts"]) for i in range(4)] == [30, 52, 12, 10]
    for split in ("train", "validation"):
        manifest = rows(f"{JOINT}/worlds/00_observed/seed0/{split}_manifest.csv")
        by_row = {}
        for row in manifest:
            key = row["row_id"]
            by_row.setdefault(key, []).append(row)
        assert all(len(group) == len(sessions) and len({r["session_id"] for r in group}) == 7 for group in by_row.values())
        assert all(len({r["label"] for r in group}) == 1 for group in by_row.values())
        component["pseudorows"][split] = [sum(group[0]["label"] == label for group in by_row.values()) for label in ("absent", "present")]
        assert {r["source_trial_id"] for r in manifest} == {sid for sid, fold in zip(meta["source_trial_ids"], meta["source_splits"], strict=True) if fold == split}
    assert component["pseudorows"] == {"train": [64, 64], "validation": [24, 6]}

    endpoint = []
    temporal = []
    cross = []
    for seed in range(3):
        cases = [
            ("Time 250", f"02-cebra/time_t1_seed{seed}/readout00250/joint"),
            ("Time 1000", f"02-cebra/time_t1_seed{seed}/readout01000/joint"),
            ("PCA8", f"01-baselines/classical_seed{seed}/pca_bin8"),
        ]
        for name, folder in cases:
            base = f"{ENDPOINT}/{folder}"
            metric = obj(base + "/development_metrics.json")
            assert metric["decoder"] == "logistic" and metric["decoder_C"] == 0.01
            assert metric["features"] == 80 and metric["n_rows"] == 240
            with np.load(source(base + "/development_predictions.npz"), allow_pickle=False) as z:
                y, pred, prob = z["y"].tolist(), z["pred"].tolist(), z["prob"]
                assert prob.shape == (240, 30) and np.isfinite(prob).all()
                assert np.allclose(prob.sum(axis=1), 1) and np.array_equal(prob.argmax(axis=1), pred)
            assert Counter(y) == Counter(dict.fromkeys(range(30), 8))
            cms = {"pair": confusion(y, pred, list(range(30)))}
            for target, index in (("start", 0), ("goal", 1)):
                cms[target] = confusion([PAIRS[i][index] for i in y], [PAIRS[i][index] for i in pred], list(range(1, 7)))
            for target in cms:
                key = "accuracy" if target == "pair" else target + "_accuracy"
                assert math.isclose(accuracy(cms[target]), metric[key], abs_tol=1e-12)
            endpoint.append({"model": name, "seed": seed, "confusions": cms, "accuracy": {k: accuracy(v) for k, v in cms.items()}})
        student = obj(f"{ENDPOINT}/01-baselines/student_seed{seed}/metrics.json")
        curves = {}
        for target in ("start", "goal", "joint"):
            entries = sorted([r for r in student if r["case"] == "student_lda" and r["split"] == "development" and r["target"] == target and r["bin"] >= 0], key=lambda r: r["bin"])
            assert [r["bin"] for r in entries] == list(range(10))
            assert all(r["features"] == 195 and r["n_rows"] == 240 for r in entries)
            curves[target] = [r["accuracy"] for r in entries]
        temporal.append({"seed": seed, "curves": curves})
        entries = rows(f"{ENDPOINT}/01-baselines/student_seed{seed}/cross_temporal_goal.csv")
        assert len(entries) == 100
        values = {(int(r["train_bin"]), int(r["development_bin"])): float(r["accuracy"]) for r in entries}
        assert set(values) == {(i, j) for i in range(10) for j in range(10)}
        matrix = [[values[i, j] for j in range(10)] for i in range(10)]
        assert all(math.isclose(matrix[i][i], curves["goal"][i], abs_tol=1e-12) for i in range(10))
        cross.append(matrix)

    summary = obj("docs/reports/cebra-full-trial-transfer/summary.json")
    joint = []
    for seed in range(3):
        path = source(f"{JOINT}/worlds/00_observed/seed{seed}/predictions.csv.gz")
        with gzip.open(path, "rt", newline="") as handle:
            predictions = list(csv.DictReader(handle))
        for arm in ("cue_time", "full_time"):
            selected = [r for r in predictions if r["world"] == "observed" and r["split"] == "validation" and r["representation"] == arm and r["readout"] == "logistic"]
            assert len(selected) == len({r["row_id"] for r in selected}) == 30
            y = [r["label"] for r in selected]
            assert Counter(y) == Counter({"absent": 24, "present": 6})
            cm = confusion(y, [r["pred_label"] for r in selected], ["absent", "present"])
            ba = mean(cm[i][i] / sum(cm[i]) for i in range(2))
            scores = [float(r["score"]) for r in selected]
            assert all(r["score_name"] == "prob_present" for r in selected)
            assert all(0 < p < 1 for p in scores)
            assert all(r["pred_label"] == ("present" if p >= 0.5 else "absent") for r, p in zip(selected, scores, strict=True))
            loss = mean(mean(-math.log(p if label == "present" else 1 - p) for truth, p in zip(y, scores, strict=True) if truth == label) for label in ("absent", "present"))
            positive = [p for label, p in zip(y, scores, strict=True) if label == "present"]
            negative = [p for label, p in zip(y, scores, strict=True) if label == "absent"]
            auc = mean(float(p > n) + 0.5 * (p == n) for p in positive for n in negative)
            saved = next(r for r in summary["observed"][arm + "/logistic"]["seed_rows"] if int(r["seed"]) == seed)
            for key, value in (("balanced_accuracy", ba), ("balanced_log_loss", loss), ("auroc", auc)):
                assert math.isclose(float(saved[key]), value, abs_tol=1e-12), (key, saved, value)
            joint.append({"arm": arm, "seed": seed, "confusion": cm, "balanced_accuracy": ba, "balanced_log_loss": loss, "auroc": auc})
    return {"version": 1, "classification": "exploratory saved-output aggregation; no fitting", "endpoint_sources": distributions, "component_sources": component, "endpoint": endpoint, "cue_lda": temporal, "cue_goal_cross_temporal": cross, "joint": joint, "provenance": provenance}


def text(x, y, value, size=14, anchor="start"):
    return f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}">{html.escape(str(value))}</text>'


def figure(key, title, body, caption, width=900, height=400):
    return f'<figure class="diagram" id="{key}"><div class="chart-scroll" tabindex="0" role="region" aria-label="{html.escape(title)}"><svg viewBox="0 0 {width} {height}" role="img" aria-labelledby="{key}-title {key}-desc"><title id="{key}-title">{html.escape(title)}</title><desc id="{key}-desc">{html.escape(caption)}</desc>{body}</svg></div><figcaption><b>{html.escape(title)}.</b> {html.escape(caption)}</figcaption></figure>'


def heatmap(key, title, matrix, rows, columns, caption, maximum=None, percent=False, axis="True class ↓ · predicted class →"):
    values = [v for row in matrix for v in row if v is not None]
    maximum = maximum or max(values) or 1
    assert all(math.isfinite(v) and 0 <= v <= maximum + 1e-8 for v in values)
    n, m = len(rows), len(columns)
    cell = 24 if m > 15 else 52
    left, top = 170, 185
    width, height = max(900, left + cell * m + 45), top + cell * n + 65
    body = text(22, 27, title, 18) + text(22, 52, axis) + text(22, 76, f"Color scale: 0–{maximum:g}{'%' if percent else ''}; gray = excluded / not applicable", 12)
    for j, label in enumerate(columns):
        x = left + (j + 0.5) * cell
        body += f'<text x="{x}" y="{top - 10}" transform="rotate(-45 {x} {top - 10})" font-size="{10 if m > 15 else 12}">{html.escape(str(label))}</text>'
    for i, row in enumerate(matrix):
        body += text(left - 10, top + (i + 0.65) * cell, rows[i], 10 if n > 15 else 13, "end")
        for j, value in enumerate(row):
            opacity = 0 if value is None else 0.08 + 0.7 * value / maximum
            fill = "#ddd" if value is None else "#48a49a"
            label = "—" if value is None else f"{value:.1f}" if percent else str(value)
            body += f'<rect x="{left + j * cell}" y="{top + i * cell}" width="{cell - 1}" height="{cell - 1}" fill="{fill}" fill-opacity="{1 if value is None else opacity}"><title>{html.escape(str(rows[i]))} / {html.escape(str(columns[j]))}: {label}{"%" if percent else ""}</title></rect>'
            if m <= 15 or (value is not None and value > 0):
                body += text(left + (j + 0.5) * cell, top + (i + 0.64) * cell, label, 9 if m > 15 else 12, "middle")
    return figure(key, title, body, caption, width, height)


def bars(key, title, labels, series, caption):
    maximum = max(v for _, values in series for v in values) * 1.12
    body = text(22, 27, title, 18)
    left, top, plot_w, plot_h = 90, 85, 750, 250
    for tick in range(5):
        value = maximum * tick / 4
        y = top + plot_h * (1 - tick / 4)
        body += f'<line x1="{left}" x2="{left + plot_w}" y1="{y}" y2="{y}" stroke="#ddd"/>' + text(left - 8, y + 4, f"{value:.0f}", 12, "end")
    for s, (name, values) in enumerate(series):
        body += f'<rect x="{90 + s * 260}" y="49" width="12" height="12" fill="{COLORS[s]}"/>' + text(110 + s * 260, 60, name, 12)
        for i, value in enumerate(values):
            width = plot_w / len(labels) / (len(series) + 1)
            x = left + i * plot_w / len(labels) + s * width + 5
            y = top + plot_h * (1 - value / maximum)
            body += f'<rect x="{x}" y="{y}" width="{width - 3}" height="{value / maximum * plot_h}" fill="{COLORS[s]}"/>' + text(x + width / 2, y - 5, value, 11, "middle")
    for i, label in enumerate(labels):
        body += text(left + (i + 0.5) * plot_w / len(labels), top + plot_h + 25, label, 12, "middle")
    return figure(key, title, body, caption)


def dots(key, title, groups, caption, baseline=0.5):
    body = text(22, 27, title, 18)
    left, top, width, height = 90, 80, 740, 250
    for tick in range(5):
        y = top + height * (1 - tick / 4)
        body += f'<line x1="{left}" x2="{left + width}" y1="{y}" y2="{y}" stroke="#ddd"/>' + text(left - 10, y + 4, f"{tick * 25}%", 12, "end")
    y = top + height * (1 - baseline)
    body += f'<line x1="{left}" x2="{left + width}" y1="{y}" y2="{y}" stroke="#ad5420" stroke-dasharray="6 4"/>' + text(left, y - 6, f"Reference {baseline * 100:.2f}%", 12)
    for i, (name, values) in enumerate(groups):
        x = left + (i + 0.5) * width / len(groups)
        avg = mean(values)
        body += f'<line x1="{x - 40}" x2="{x + 40}" y1="{top + height * (1 - avg)}" y2="{top + height * (1 - avg)}" stroke="#222" stroke-width="3"/>'
        for seed, value in enumerate(values):
            cy = top + height * (1 - value)
            body += f'<circle cx="{x + (seed - 1) * 20}" cy="{cy}" r="6" fill="{COLORS[seed]}"><title>Seed{seed}: {value * 100:.2f}%</title></circle>'
        body += text(x, top + height + 25, name, 14, "middle") + text(x, 58, f"mean {avg * 100:.2f}%", 13, "middle")
    return figure(key, title, body, caption)


def curve(key, target, series):
    caption = f"Historical endpoint cohort:195 units/58 sessions;12,288 training +3,265 development sources,480/240 conditional pseudorows per seed. Plain LDA fits a separate {target} decoder at each100-ms raw-count cue bin; all three seeds (thin) and their mean (thick). No CEBRA or navigation result, no biological confidence interval. Cue bins span[0,1)s from onset; time labels are bin centers. Saved01-baselines/student_seed*/metrics.json; S5."
    body = text(22, 27, f"Cue-time decoding · {target} · plain LDA", 18)
    left, top, width, height = 80, 70, 750, 245
    for tick in range(5):
        y = top + height * (1 - tick / 4)
        body += f'<line x1="{left}" x2="{left + width}" y1="{y}" y2="{y}" stroke="#ddd"/>' + text(left - 10, y + 4, f"{tick * 25}%", 12, "end")
    baseline = 1 / (30 if target == "pair" else 6)
    y = top + height * (1 - baseline)
    body += f'<line x1="{left}" x2="{left + width}" y1="{y}" y2="{y}" stroke="#ad5420" stroke-dasharray="6 4"/>' + text(left, y - 6, f"Chance {baseline * 100:.2f}%", 12)
    for i, values in enumerate([*series, [mean(v[b] for v in series) for b in range(10)]]):
        points = " ".join(f"{left + b * width / 9},{top + height * (1 - v)}" for b, v in enumerate(values))
        body += f'<polyline points="{points}" fill="none" stroke="{COLORS[i] if i < 3 else "#193f45"}" stroke-width="{1.5 if i < 3 else 4}"/>'
    for b in range(10):
        body += text(left + b * width / 9, 342, 50 + 100 * b, 12, "middle")
    body += text(450, 373, "Cue-onset-relative bin center (ms) · accuracy", 14, "middle")
    return figure(key, f"Cue-time {target} decoding", body, caption)


def confusion_figures(key, title, matrix, labels, caption):
    return heatmap(key + "-counts", title + " · counts", matrix, labels, labels, caption, maximum=max(map(sum, matrix))) + heatmap(key + "-recall", title + " · row %", normalize(matrix), labels, labels, caption + " Each true-class row sums to100%; values are class recall distributions, not source prevalence.", maximum=100, percent=True)


def figures(data):
    """Static, keyboard-scrollable SVG plus captions; no new browser dependency."""
    distributions = data["endpoint_sources"]
    support_caption = "Endpoint eligibility cohort:195 units/58 sessions;12,288 training and3,265 development real session–trials within the old training partition. Each source counted once, not per neuron/bin. Known operational start/goal labels; original validation/test excluded. Saved source_splits.csv reconciled against source_support.csv; no uncertainty bars or new fits. S2."
    source_figs = ""
    for target in ("start", "goal"):
        source_figs += bars("ev-source-" + target, "Real-source " + target + " distribution", list(range(1, 7)), [("Training sources", distributions["train"][target]), ("Development sources", distributions["validation"][target])], support_caption)
    for split in ("train", "validation"):
        source_figs += heatmap("ev-pairs-" + split, f"Real-source ordered pairs · {split}", distributions[split]["pairs"], list(range(1, 7)), list(range(1, 7)), support_caption + " Gray diagonal: equal endpoints excluded by this assay, not evidence of no such trials in the wider archive.", axis="Start ↓ · goal → · real-source counts")
    support_bins = [(0, 0), (1, 1), (2, 2), (3, 4), (5, 8), (9, math.inf)]
    support_series = [(label, [sum(count for value, count in distributions[split]["support_histogram"].items() if low <= int(value) <= high) for low, high in support_bins]) for split, label in (("train", "Training"), ("validation", "Development"))]
    source_figs += bars("ev-support", "Source support per session–pair cell", ["0", "1", "2", "3–4", "5–8", "9+"], support_series, support_caption + " X:number of real sources per session–pair cell; Y:number of cells. Each split has1,740 cells. Cells with one source have fragile support despite balanced aggregate classes.")
    component = data["component_sources"]
    source_figs += heatmap("ev-component-support", "Fixed4→3 component · real sources by session", component["counts"], component["session_labels"], component["columns"], "Separate path cohort:29 units/7 sessions,82 training +22 historical-validation sources. Columns sum30/52/12/10 (absent/present). Session codes follow sorted saved session IDs; these are not animals or proven simultaneous groups. Metadata only from frozen source_level_cue_tensors.npz; target D_N_R_T__N_R_M interior presence, not ordered-route classes. S3.", axis="Session ↓ · source split and component class →")
    source_figs += bars("ev-source-pseudo", "Component balance: real sources ≠ synthetic rows", ["Train sources", "Validation sources", "Train pseudorows", "Validation pseudorows"], [("Absent", [30, 12, 64, 24]), ("Present", [52, 10, 64, 6])], "Fixed4→3 path cohort only. Real sources82/22; seed0 assembly128/30 rows from7 session blocks. Saved source metadata and manifests, not independent row counts. Validation product space has24 absent/6 present combinations; balanced metrics give each class50% weight (per-row weights1/48 and1/12). Synthetic class imbalance differs from biological source prevalence; no full-route prevalence inferred. S3.")

    performance = ""
    endpoint_caption = "Endpoint follow-up:195 units/58 sessions,12,288 training +3,265 exposed development sources;480/240 conditional pseudorows per seed. Frozen80-feature representations; separately fitted scaled logistic C=.01. Dots:seeds0/1/2 (green/blue/orange), line:mean—not a biological interval. Pair is30-way; start/goal here are endpoints of the argmax pair, not separate heads or summed probability marginals. Saved predictions verified against metrics; S5."
    for target in ("pair", "start", "goal"):
        groups = [(name, [r["accuracy"][target] for r in data["endpoint"] if r["model"] == name]) for name in ("Time 250", "Time 1000", "PCA8")]
        performance += dots("ev-endpoint-" + target, "Endpoint " + target + " accuracy · common readout", groups, endpoint_caption, 1 / (30 if target == "pair" else 6))
    details = "<details><summary>All endpoint confusion matrices: pair, start and goal; counts and row-normalized</summary>"
    for name in ("Time 250", "Time 1000", "PCA8"):
        for target in ("pair", "start", "goal"):
            matrices = [r["confusions"][target] for r in data["endpoint"] if r["model"] == name]
            n = len(matrices[0])
            pooled = [[sum(m[i][j] for m in matrices) for j in range(n)] for i in range(n)]
            labels = [f"{s}→{g}" for s, g in PAIRS] if target == "pair" else list(range(1, 7))
            details += confusion_figures("ev-cm-" + name.lower().replace(" ", "") + "-" + target, name + " · " + target, pooled, labels, endpoint_caption + " Pooled720 prediction events across3 seeds reuse the same source pools; NOT720 independent trials. True-class support:24 events/pair or120/endpoint. Counts are unweighted; equal class support makes overall accuracy equal balanced accuracy.")
    performance += details + "</details>"

    temporal = "".join(curve("ev-cue-" + target, target, [r["curves"][key] for r in data["cue_lda"]]) for target, key in (("pair", "joint"), ("start", "start"), ("goal", "goal")))
    matrices = data["cue_goal_cross_temporal"]
    cross_mean = [[100 * mean(m[i][j] for m in matrices) for j in range(10)] for i in range(10)]
    cross_caption = "Historical plain-LDA goal decoding on raw195-unit bins;58 sessions,12,288 training +3,265 development sources,480/240 conditional pseudorows/seed. One training-bin decoder per row is frozen across development bins; each cell is accuracy, balanced chance16.67%. Mean of3 seeds, no biological CI. Diagonal equals same-bin goal curve; off-diagonal is within-cue transfer, NOT joint-CEBRA or cue↔navigation validation. Saved cross_temporal_goal.csv; bins are100ms; axes show bin centers from cue onset. S5."
    centers = [50 + 100 * i for i in range(10)]
    temporal += heatmap("ev-cross-cue", "Historical cue→cue goal generalization · mean accuracy %", cross_mean, centers, centers, cross_caption, 100, True, "Decoder-training bin center (ms) ↓ · held-out evaluation bin center (ms) →")
    temporal += "<details><summary>Temporal-generalization heatmaps for all three computational seeds</summary>"
    for seed, matrix in enumerate(matrices):
        temporal += heatmap(f"ev-cross-seed{seed}", f"Cue→cue goal accuracy % · seed{seed}", [[100 * v for v in row] for row in matrix], centers, centers, cross_caption.replace("Mean of3 seeds", f"Seed{seed} alone"), 100, True, "Training-bin center (ms) ↓ · evaluation-bin center (ms) →")
    temporal += "</details>"

    joint_caption = "Latest fixed4→3 interior-component assay:29 units/7 session blocks,82 training +22 historical-validation sources;128 training/30 evaluation conditional pseudorows per seed (24 absent/6 present). Frozen cue-only or joint Time encoder,1000 updates; separate scaled logistic C=.01 cue readouts. Dots:seeds0/1/2; line:mean, not biological CI. All predictions use whole cues. Source-coherent nulls and failed complete success rule still apply; S3/S7."
    joint = ""
    for metric, label in (("balanced_accuracy", "balanced accuracy"), ("auroc", "AUROC ×100")):
        joint += dots("ev-joint-" + metric, "Joint-training comparison · " + label, [(name, [r[metric] for r in data["joint"] if r["arm"] == arm]) for name, arm in (("Cue-trained", "cue_time"), ("Joint-trained", "full_time"))], joint_caption, 0.5)
    joint += "<details><summary>Every joint-comparison confusion matrix: both arms, all three seeds</summary>"
    for row in data["joint"]:
        label = "Cue-trained" if row["arm"] == "cue_time" else "Joint-trained"
        joint += confusion_figures(f"ev-joint-cm-{row['arm']}-{row['seed']}", f"{label} · seed{row['seed']}", row["confusion"], ["absent", "present"], joint_caption + " Counts are unweighted prediction events with row totals24/6. Balanced accuracy is the mean of the two diagonal row recalls, not raw accuracy; fixed decision threshold0.5.")
    return {"SOURCE_SUPPORT": source_figs, "ENDPOINT_PERFORMANCE": performance, "TEMPORAL_RESULTS": temporal, "JOINT_DETAIL": joint + "</details>"}


def self_check(data):
    assert confusion([0, 0, 1], [0, 1, 1], [0, 1]) == [[1, 1], [0, 1]]
    assert normalize([[1, 1], [0, 1]]) == [[50, 50], [0, 100]]
    for matrix in ([[0, 0], [1, 1]],):
        try:
            normalize(matrix)
        except ValueError as error:
            assert "unsupported class" in str(error)
        else:
            raise AssertionError("Unsupported class accepted")
    assert len(data["endpoint"]) == 9 and len(data["joint"]) == 6
    assert len(data["cue_goal_cross_temporal"]) == 3
    assert [sum(row[i] for row in data["component_sources"]["counts"]) for i in range(4)] == [30, 52, 12, 10]
    for row in data["endpoint"]:
        assert sum(map(sum, row["confusions"]["pair"])) == 240
        for target, matrix in row["confusions"].items():
            assert math.isclose(accuracy(matrix), row["accuracy"][target], abs_tol=1e-12)
    for row in data["joint"]:
        assert [sum(r) for r in row["confusion"]] == [24, 6]
        assert math.isclose(mean(normalize(row["confusion"])[i][i] for i in range(2)) / 100, row["balanced_accuracy"], abs_tol=1e-12)
    for record, matrix in zip(data["cue_lda"], data["cue_goal_cross_temporal"], strict=True):
        assert all(math.isclose(matrix[i][i], record["curves"]["goal"][i], abs_tol=1e-12) for i in range(10))
    assert all(len(value) == 64 for value in data["provenance"].values())
    assert SOURCE not in data["provenance"], "Do not hash the neural tensor archive"
    assert {key.split("#", 1)[1] for key in data["provenance"] if key.startswith(SOURCE + "#")} == {name + ".npy" for name in ["source_trial_ids", "source_session_ids", "source_splits", "source_labels"]}
    assert not any(name in sys.modules for name in ["torch", "cebra", "sklearn", "joblib"])


def main():
    if not __debug__ or sys.argv[1:] not in (["--extract"], ["--check"], ["--sources"]):
        raise SystemExit("Usage: evidence.py --extract | --check | --sources (without -O)")
    try:
        if sys.argv[1] == "--extract":
            data = extract()
            self_check(data)
            TARGET.write_text(json.dumps(data, indent=2, allow_nan=False) + "\n")
        else:
            data = json.loads(TARGET.read_text())
            self_check(data)
            if sys.argv[1] == "--sources":
                assert data == extract(), "Saved evidence replay differs"
            print("PASS: counts, confusion/metric reconstruction, temporal diagonal, no model imports")
    except (OSError, ValueError, KeyError, TypeError, AssertionError) as error:
        raise SystemExit(f"Saved-evidence check failed: {error}") from error


if __name__ == "__main__":
    main()
