"""Collate reviewed saved-result error analysis into report, notebook and teach.

Only authenticated aggregates are used. No neuro/model libraries are imported.
Existing run, interpreted deliverables and disposable lesson remain unchanged.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import html
import json
import os
from pathlib import Path
import re
import shutil

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mistune
import nbformat
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS_RECEIPT = "fd6197cbb526ab3bfc96d71fe43abe23afa88e43f7dab04a32e897b734ad329a"
BASE_COLLATION = "2fd29557e906718f465ae4a1eff3c78d45cc9436c06fc788024bb0e7c048af89"
BASE_TEACH = "10eec3b5d205639c6a7abc69e4622b0073f3ef48fb04a2fd4efb71bfde942121"
NAMES = {
    "raw": "Raw",
    "pca": "PCA7",
    "cebra": "CEBRA-Time7",
    "native": "Native multisession7",
}
COLORS = {"raw": "#245a81", "pca": "#57986c", "cebra": "#b44b43", "native": "#8b75aa"}


def sha(path):
    with Path(path).open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def write_json(path, data):
    Path(path).write_text(
        json.dumps(data, ensure_ascii=False, allow_nan=False, indent=2) + "\n"
    )


def authenticated(root, manifest_name, digest):
    if sha(root / manifest_name) != digest:
        raise ValueError("unexpected input manifest")
    manifest = json.loads((root / manifest_name).read_text())
    for relative, expected in manifest["files_sha256"].items():
        path = (root / relative).resolve()
        if not path.is_relative_to(root) or sha(path) != expected:
            raise ValueError(f"input changed: {relative}")
    return manifest


def compact_payload(data):
    matrices = {}
    for r in data["confusions"]:
        head = (
            matrices.setdefault(r["id"], {})
            .setdefault(r["representation"], {})
            .setdefault(r["head"], {"labels": r["labels"]})
        )
        assert head["labels"] == r["labels"] and r["split"] not in head
        head[r["split"]] = r["counts"]
    usage = {}
    usage_fields = (
        "available_train_sources",
        "harmonic_session_train_pool",
        "train_used_sources",
        "train_block_draws",
        "train_reuse_fraction",
        "available_development_sources",
        "development_used_sources",
        "development_block_draws",
        "development_reuse_fraction",
    )
    for r in data["class_performance"]:
        values = {k: r[k] for k in usage_fields}
        selected = usage.setdefault(r["case"], {})
        if r["pair"] in selected:
            assert selected[r["pair"]] == values
        else:
            selected[r["pair"]] = values
    correlations = {}
    for r in data["correlations"]:
        correlations.setdefault(r["case"], {}).setdefault(
            r["representation"], []
        ).append({k: r[k] for k in ("variable", "spearman_rho", "status")})
    changes = {}
    fields = (
        "pair",
        "both_correct",
        "wrong_to_right",
        "right_to_wrong",
        "both_wrong",
        "changed_wrong_label",
    )
    for r in data["paired_changes"]:
        changes.setdefault(r["before_case"] + "|" + r["after_case"], {}).setdefault(
            r["representation"], []
        ).append([r[k] for k in fields])
    return dict(
        receipt_sha256=data["receipt_sha256"],
        analysis_receipt_sha256=ANALYSIS_RECEIPT,
        matrices=matrices,
        usage=usage,
        correlations=correlations,
        changes=changes,
        grid=data["grid"],
        panels=data["panels"],
        exclusions=data["exclusions"],
    )


def make_figures(data, output):
    directory = output / "images"
    directory.mkdir()
    figures = []
    panel = {r["class_count"]: r["conditions"] for r in data["panels"]}
    matrices = {
        (r["id"], r["representation"], r["head"], r["split"]): r
        for r in data["confusions"]
    }
    grid = {(g["class_count"], g["roster"]): g for g in data["grid"]}
    usage = {}
    for r in data["class_performance"]:
        if r["encoder"] == "raw" and r["decoder"] == "logistic":
            usage.setdefault(r["case"], []).append(r)

    def counts_text(case):
        rows = usage[case]
        train_used = sum(r["train_used_sources"] for r in rows)
        train_available = sum(r["available_train_sources"] for r in rows)
        development_used = sum(r["development_used_sources"] for r in rows)
        development_available = sum(r["available_development_sources"] for r in rows)
        train_rows = sum(r["train_rows"] for r in rows)
        development_rows = sum(r["development_rows"] for r in rows)
        return f"T sources{train_used}/{train_available} → {train_rows} rows; D sources{development_used}/{development_available} → {development_rows} rows"

    full_cohorts = "; ".join(
        f"K{k}: {counts_text(f'observed_seed0_K{k}_S100_F16')}" for k in (30, 20, 15)
    )

    def save(fig, name, caption):
        if name in ("deletion_groups_svm.png", "reuse_correlations_svm.png"):
            caption += (
                " Cohort counts (T/D=training/development, sources used/available): "
                + full_cohorts
                + "."
            )
        elif name.startswith("class_recall_K"):
            selected_k = int(re.search(r"class_recall_K(\d+)", name).group(1))
            caption += (
                " Counts (T/D=training/development, sources used/available; counts constant across seeds): "
                + "; ".join(
                    f"{roster}/{policy}: {counts_text(f'observed_seed0_K{selected_k}_{roster}_{policy}')}"
                    for roster in ("S33", "S67", "S100")
                    for policy in ("U2", "R16", "F16")
                )
                + "."
            )
        file = directory / name
        fig.savefig(file, dpi=140, facecolor="white")
        plt.close(fig)
        figures.append(dict(file="images/" + name, sha256=sha(file), caption=caption))

    for encoder in NAMES:
        for policy in ("U2", "R16", "F16"):
            fig, axes = plt.subplots(3, 3, figsize=(19, 19))
            for i, k in enumerate((30, 20, 15)):
                for j, roster in enumerate(("S33", "S67", "S100")):
                    case = f"observed_seed0_K{k}_{roster}_{policy}"
                    r = matrices[case, encoder + "_svm", "pair", "development"]
                    counts = np.asarray(r["counts"])
                    normalized = counts / counts.sum(axis=1, keepdims=True)
                    ax = axes[i, j]
                    im = ax.imshow(
                        normalized,
                        vmin=0,
                        vmax=1,
                        cmap="Blues",
                        interpolation="nearest",
                    )
                    labels = [label.replace("->", "→") for label in r["labels"]]
                    ax.set_xticks(range(k), labels=labels, rotation=90, fontsize=6)
                    ax.set_yticks(range(k), labels=labels, fontsize=6)
                    for artist, label in zip(
                        ax.get_yticklabels(), r["labels"], strict=True
                    ):
                        if label not in panel[15]:
                            artist.set_color("#a14017")
                    g = grid[k, roster]
                    ax.set_title(
                        f"K{k} {roster}: {g['units']} columns / {g['sessions']} sessions; BA {100 * np.diag(normalized).mean():.1f}%\n{counts_text(case)}",
                        fontsize=8.5,
                    )
                    ax.set_xlabel("Predicted pair", fontsize=9)
                    ax.set_ylabel("True pair", fontsize=9)
            fig.suptitle(
                f"All nine configurations · {NAMES[encoder]} / RBF-SVM · {policy} · observed seed0",
                fontsize=20,
            )
            fig.subplots_adjust(
                left=0.07, right=0.9, top=0.94, bottom=0.105, wspace=0.35, hspace=0.38
            )
            bar = fig.colorbar(im, cax=fig.add_axes([0.925, 0.25, 0.015, 0.5]))
            bar.set_label("Fraction of rows for each true class")
            fig.text(
                0.06,
                0.052,
                "Whole cue0–1s; exposed source-separated development; eight constructed rows per pair. Rows=true, columns=predicted.\nT/D=training/development; source counts=used/available distinct session×trial sources, separate from synthetic rows.\nRed true-label text marks labels absent from the15-class task; each matrix retains its entire actual label set.\nSingle computational seed; no biological interval. Different K values are different tasks/cohorts, not matched deletion effects.",
                fontsize=10,
            )
            caption = f"{NAMES[encoder]}/RBF-SVM, {policy}, observed seed0. All9 class×session configurations. Row-normalized development pair confusions on eight constructed rows/pair, whole cue[0,1)s. Input columns/sessions and BA are shown per panel. Red true-label text denotes absence from the15-class task, not unevaluated rows inside this matrix. Counts, other seeds, all four decoders, training and independent endpoint heads are available in the interactive explorer. Fixed exposed, known-label assembly; dependent synthetic rows; no uncertainty interval or causal cross-K comparison. Derived from authenticated saved predictions in the November11 run; no fitting."
            save(fig, f"confusion_overview_{encoder}_{policy}.png", caption)

    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    for ax, (source_k, destination_k) in zip(
        axes, ((30, 20), (30, 15), (20, 15)), strict=True
    ):
        for i, encoder in enumerate(NAMES):
            selected = [
                r
                for r in data["deletion_groups"]
                if r["source_k"] == source_k
                and r["destination_k"] == destination_k
                and r["roster"] == "S100"
                and r["sampling"] == "F16"
                and r["decoder"] == "svm"
                and r["encoder"] == encoder
            ]
            for offset, field, color, label in (
                (
                    -0.18,
                    "source_retained_recall",
                    "#2f7591",
                    "Retained in smaller task",
                ),
                (0.18, "source_deleted_recall", "#b36332", "Deleted in smaller task"),
            ):
                values = [100 * r[field] for r in selected]
                ax.bar(
                    i + offset,
                    np.mean(values),
                    0.32,
                    color=color,
                    alpha=0.75,
                    label=label if i == 0 else None,
                )
                ax.scatter(
                    [i + offset] * 3,
                    values,
                    color=color,
                    edgecolors="black",
                    s=22,
                    zorder=3,
                )
        ax.set_xticks(range(4), labels=list(NAMES.values()), rotation=20, ha="right")
        ax.set_ylim(0, 100)
        ax.set_title(f"Before {source_k}→{destination_k}: source-task recall")
        ax.set_ylabel("Mean class recall (%)")
        ax.grid(axis="y", alpha=0.2)
    axes[0].legend(fontsize=9)
    fig.suptitle(
        "Were the classes later removed already harder to decode?", fontsize=18
    )
    fig.subplots_adjust(top=0.84, bottom=0.27, wspace=0.25)
    fig.text(
        0.06,
        0.055,
        "Full source-task roster, F16, SVM; pair classes; source-separated exposed development, eight constructed rows/class.\nBars=three computational-seed means; dots=each seed, not biological replication. Selection used metadata, not errors.\nBoth groups are scored in the source task. Deleted classes have no destination score; new tasks also change sessions, source coverage and competitors.",
        fontsize=10,
    )
    save(
        fig,
        "deletion_groups_svm.png",
        "Source-task recall of classes retained versus removed in30→20,30→15 and20→15. Full roster/F16/SVM; all four feature pipelines; bars mean seeds0/1/2, dots individual computational seeds. Eight known-label-assembled development rows/class, whole cue0–1s; source IDs separated from training but development exposed/reused. The smaller task's absent labels are not assigned zero recall. This compares metadata-selected groups within the larger task, not a causal removal experiment; cohorts also change across K.",
    )

    fig, axes = plt.subplots(1, 3, figsize=(17, 5.5))
    for ax, k in zip(axes, (30, 20, 15), strict=True):
        for i, encoder in enumerate(NAMES):
            selected = sorted(
                [
                    r
                    for r in data["correlations"]
                    if r["class_count"] == k
                    and r["roster"] == "S100"
                    and r["sampling"] == "F16"
                    and r["decoder"] == "svm"
                    and r["encoder"] == encoder
                    and r["variable"] == "train_reuse_fraction"
                ],
                key=lambda r: r["seed"],
            )
            ax.scatter(
                [i - 0.1, i, i + 0.1],
                [r["spearman_rho"] for r in selected],
                c=COLORS[encoder],
                s=55,
            )
        ax.axhline(0, c="black", lw=0.8)
        ax.set_ylim(-1, 1)
        ax.set_xticks(range(4), labels=list(NAMES.values()), rotation=20, ha="right")
        ax.set_title(f"K{k}: {k} pair-class observations per seed")
        ax.set_ylabel("Spearmanρ: training reuse vs class error")
        ax.grid(axis="y", alpha=0.2)
    fig.suptitle(
        "Does greater source reuse accompany more development error?", fontsize=17
    )
    fig.subplots_adjust(top=0.82, bottom=0.28, wspace=0.3)
    fig.text(
        0.05,
        0.05,
        "Full roster/F16/SVM; dots left→right=seeds0/1/2. Positiveρ means more reuse accompanies more error.\nReuse=1−available_sources/(16×sessions), so this is also lower source coverage; the two cannot be separated here.\nAcross classes within each fitted case, not pooled synthetic trials or independent seeds. No p-values or biological confidence intervals.",
        fontsize=10,
    )
    save(
        fig,
        "reuse_correlations_svm.png",
        "Average-tie-rank Spearman associations across pair classes, full roster/F16/SVM. Each dot is one computational seed, with K classes as the descriptive observations. Positive values associate more training-source reuse with more development error. Under fixed F16 quota/roster, reuse is a deterministic inverse of available source count; no independent reuse-versus-coverage effect or causation is identified. U2/R16 reuse is constant and their correlations are undefined, not zero. No p-values or biological uncertainty intervals.",
    )

    for k in (30, 20, 15):
        labels = panel[k]
        rowlabels, scores = [], []
        for roster in ("S33", "S67", "S100"):
            for policy in ("U2", "R16", "F16"):
                rowlabels.append(f"{roster} / {policy}")
                scores.append(
                    [
                        100
                        * np.mean(
                            [
                                r["development_recall"]
                                for r in data["class_performance"]
                                if r["class_count"] == k
                                and r["roster"] == roster
                                and r["sampling"] == policy
                                and r["encoder"] == "cebra"
                                and r["decoder"] == "svm"
                                and r["pair"] == label
                            ]
                        )
                        for label in labels
                    ]
                )
        fig, ax = plt.subplots(figsize=(max(12, 0.52 * k), 6.5))
        im = ax.imshow(scores, vmin=0, vmax=100, cmap="Blues", aspect="auto")
        ax.set_xticks(
            range(k),
            labels=[c.replace("->", "→") for c in labels],
            rotation=60,
            ha="right",
        )
        ax.set_yticks(range(9), labels=rowlabels)
        for i in range(9):
            for j in range(k):
                ax.text(
                    j,
                    i,
                    f"{scores[i][j]:.0f}",
                    ha="center",
                    va="center",
                    fontsize=7,
                    color="white" if scores[i][j] > 55 else "#193647",
                )
        ax.set_title(f"K{k} · CEBRA-Time7 / RBF-SVM · per-class development recall")
        fig.colorbar(im, ax=ax, label="Recall (%)")
        fig.subplots_adjust(left=0.12, right=0.94, top=0.9, bottom=0.28)
        fig.text(
            0.1,
            0.05,
            "Each cell=mean recall across computational seeds0/1/2, not an independent-trial estimate. Whole cue0–1s; eight constructed development rows/class.\nU2 uses two sources once per session/class; R16 repeats those same sources; F16 uses all available sources. Rows are class-balanced; source reuse differs.\nRosters change recorded width and source composition. Individual seeds, true/predicted confusion cells and paired wrong↔right counts remain in the explorer.",
            fontsize=9,
        )
        save(
            fig,
            f"class_recall_K{k}_cebra_svm.png",
            f"K{k} retained pair classes, CEBRA-Time7/SVM. Rows compare all three session rosters and three sampling policies; cells show mean class recall across seeds0/1/2, rounded to integer percent for display, with exact seed counts in tables/explorer. Same eight source-separated but exposed/condition-matched development rows per class within K, projected across rosters. Computational averages are not biological uncertainty intervals. U2/R16 share measured source sets; F16 changes coverage/weighting at fixed16-row quota. No new fit.",
        )
    return figures


def select(label, ident, values, selected):
    return (
        "<label>"
        + label
        + f'<select id="ea-{ident}">'
        + "".join(
            f'<option value="{html.escape(str(value))}"'
            + (" selected" if value == selected else "")
            + ">"
            + html.escape(text)
            + "</option>"
            for value, text in values
        )
        + "</select></label>"
    )


def explorer_markup():
    controls = "".join(
        [
            select("Pair classes", "k", [(k, str(k)) for k in (30, 20, 15)], 30),
            select(
                "Session roster",
                "roster",
                [
                    ("S33", "First third"),
                    ("S67", "First two-thirds"),
                    ("S100", "All eligible"),
                ],
                "S100",
            ),
            select(
                "Sampling",
                "policy",
                [
                    ("U2", "U2: two sources once"),
                    ("R16", "R16: same two repeated"),
                    ("F16", "F16: all sources"),
                ],
                "F16",
            ),
            select("Features", "encoder", list(NAMES.items()), "cebra"),
            select(
                "Decoder",
                "decoder",
                [
                    ("logistic", "Logistic"),
                    ("svm", "RBF-SVM"),
                    ("knn", "kNN5"),
                    ("lda", "SVD-LDA"),
                ],
                "svm",
            ),
            select(
                "Confusion target",
                "head",
                [("pair", "Start→goal pair"), ("start", "Start"), ("goal", "Goal")],
                "pair",
            ),
            select("Seed", "seed", [(x, str(x)) for x in (0, 1, 2)], 0),
            select(
                "Label world",
                "world",
                [("observed", "Observed")]
                + [(str(x), f"Permutation{x}") for x in range(60000, 60005)],
                "observed",
            ),
            select(
                "Confusion split",
                "split",
                [("development", "Development"), ("train", "Training")],
                "development",
            ),
            select(
                "Cell numbers",
                "mode",
                [("counts", "Counts"), ("percent", "Row-normalized %")],
                "counts",
            ),
        ]
    )
    transition = select(
        "Class selection / label highlight",
        "transition",
        [("30-20", "30→20"), ("30-15", "30→15"), ("20-15", "20→15")],
        "30-20",
    )
    reuse = select(
        "Scatter x-axis",
        "xaxis",
        [
            ("train_reuse_fraction", "Training source reuse"),
            ("available_train_sources", "Available training sources"),
            ("harmonic_session_train_pool", "Harmonic session support"),
            ("development_reuse_fraction", "Development source reuse"),
        ],
        "train_reuse_fraction",
    )
    policy_cut = select(
        "Matched policy change",
        "policy-cut",
        [
            ("U2-R16", "U2→R16: same sources"),
            ("R16-F16", "R16→F16: same row quota"),
            ("U2-F16", "U2→F16"),
        ],
        "R16-F16",
    )
    session_cut = select(
        "Remove session group",
        "cut",
        [
            ("S100-S33", "All→first third"),
            ("S100-S67", "All→first two-thirds"),
            ("S67-S33", "Two-thirds→first third"),
        ],
        "S100-S33",
    )
    return f"""<section id="error-explorer" class="ea"><h2>Confusions, removed classes and source reuse</h2>
<p><b>Post-hoc descriptive saved-result analysis.</b> All nine configurations, three sampling policies, three observed seeds, four feature pipelines and four decoders. These matrices come from saved predictions; no models were refitted.</p>
<div class="ea-controls">{controls}{transition}</div><p id="ea-context" class="ea-caption"></p>
<p><a href="#ea-class-removal">Classes removed</a> · <a href="#ea-reuse">Reuse and errors</a> · <a href="#ea-session-removal">Sessions removed</a> · <a href="#error-findings">Interpreted findings</a></p>
<h3>The selected confusion matrix</h3><div id="ea-matrix" class="ea-detail"></div><p id="ea-matrix-note" class="ea-caption"></p><button type="button" id="ea-download">Download this matrix as CSV</button><details><summary>Exact class recall and most frequent mistake</summary><p>One most frequent wrong label is shown; ties follow the displayed label order.</p><div id="ea-matrix-table"></div></details>
<h3>All nine configurations side by side</h3><p>Click a panel button to inspect its full matrix. Every panel uses the selected model, sampling policy, seed, target and split. Color is row fraction0–100% throughout. Different class counts define different tasks; small panels are an overview, not a pooled performance ranking.</p><div id="ea-grid" class="ea-grid"></div>
<h3 id="ea-class-removal">Were deleted classes already difficult?</h3><p>Uses the selected class transition, roster, policy, encoder, decoder and observed seed. Both before-groups are evaluated in the larger source task. The smaller destination task also changes sessions, features and source construction. A missing class is <b>not evaluated</b>, not incorrect.</p><p id="ea-deletion-summary" class="ea-callout"></p><div id="ea-deletion-table"></div>
<h3 id="ea-reuse">Which reused classes were right or wrong?</h3><div class="ea-controls">{reuse}{policy_cut}</div><p id="ea-reuse-note"></p><div id="ea-reuse-plot"></div><div id="ea-rho-table"></div><div id="ea-reuse-table"></div>
<h4>Prediction switches under the selected policy change</h4><p>Same pair task, roster, seed and exact development source rows. Counts partition the eight constructed development rows for each class; these are dependent observations. R16→F16 changes coverage, weights and combinations at equal row quota.</p><div id="ea-policy-flips"></div>
<h3 id="ea-session-removal">What changes when a session group is removed?</h3><div class="ea-controls">{session_cut}</div><p id="ea-session-note" class="ea-callout"></p><div id="ea-session-flips"></div><details><summary>Which sessions were retained or excluded?</summary><div id="ea-session-table"></div></details>
<p class="ea-caption">Provenance: completed November11 run, original receipt6f070f…; corrected saved-result analysis receiptfd6197…. Pair/source associations are descriptive across classes, not tests on independent trials. Previously exposed development, known-label assembly and serial/session dependence remain limitations. Confusion heads are separately fitted; pair mistakes are not silently collapsed into endpoint-head predictions.</p></section>"""


STYLE = """.ea{border-top:4px solid #32778a;background:#fff;padding:28px;max-width:1450px;margin:30px auto;color:#203c46}.ea h2{font-size:30px}.ea h3{margin-top:42px}.ea-controls{display:flex;flex-wrap:wrap;gap:14px;padding:16px;background:#eaf0ed}.ea-controls label{display:flex;flex-direction:column;font-size:13px;gap:5px}.ea select,.ea button{font:14px system-ui;padding:8px;border:1px solid #8ba5a7;border-radius:4px;background:white;color:#174e66}.ea button{cursor:pointer}.ea select:focus,.ea button:focus{outline:3px solid #66aba5}.ea-caption{font-size:13px;color:#536b72}.ea-detail{max-width:980px;margin:auto}.ea-matrix{width:100%;height:auto;background:white}.ea-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}.ea-grid-card{border:1px solid #c9d9d7;padding:8px}.ea-grid-card button{width:100%}.ea-scroll{overflow:auto}.ea table{display:table;border-collapse:collapse;font-size:13px;width:100%;margin:16px 0}.ea th,.ea td{border:1px solid #cad7d4;padding:8px;vertical-align:top}.ea th{background:#e9f0ec}.ea svg text{font-family:system-ui,sans-serif}.ea-callout{padding:16px;background:#e9f1ee;border-left:4px solid #347a79}.ea-missing{padding:20px;background:#f3ece2}.ea svg{max-width:100%;height:auto}.ea p{line-height:1.6}@media(max-width:800px){.ea-grid{grid-template-columns:1fr}.ea{padding:15px}.ea-detail{overflow:auto}.ea-detail svg{min-width:620px}}"""


def rewrite_html_links(text, before, after):
    def replace(match):
        target = html.unescape(match.group(1))
        if re.match(r"[a-zA-Z]+:|#", target):
            return match.group(0)
        path, sep, fragment = target.partition("#")
        resolved = (before / path).resolve()
        relative = Path(os.path.relpath(resolved, after)).as_posix()
        return (
            'href="'
            + html.escape(relative + ("#" + fragment if sep else ""), quote=True)
            + '"'
        )

    return re.sub(r'href="([^"]+)"', replace, text)


def build(analysis, base, output, note, teach_source, teach_output):
    for path in (output, teach_output):
        if path.exists():
            raise FileExistsError(f"fresh destination required: {path}")
    analysis_manifest = authenticated(
        analysis, "analysis-receipt.json", ANALYSIS_RECEIPT
    )
    base_manifest = authenticated(base, "collation.json", BASE_COLLATION)
    if sha(teach_source) != BASE_TEACH:
        raise ValueError("base teaching artifact changed")
    script = ROOT / "scripts/population_grid_error_explorer.js"
    start_hashes = {
        "builder": sha(__file__),
        "javascript": sha(script),
        "note": sha(note),
    }
    data = json.loads((analysis / "analysis.json").read_text())
    output.mkdir(parents=True, mode=0o700)
    figures = make_figures(data, output)
    write_json(output / "error_figure_provenance.json", figures)
    shutil.copytree(analysis / "tables", output / "error-tables")
    shutil.copy2(analysis / "analysis-receipt.json", output / "analysis-receipt.json")
    # Preserve old notebook cells/relative table links by copying their sidecars.
    shutil.copytree(base / "tables", output / "tables")
    assert not (
        {p.name for p in (base / "images").iterdir()}
        & {p.name for p in (output / "images").iterdir()}
    )
    shutil.copytree(base / "images", output / "images", dirs_exist_ok=True)
    for name in (
        "configuration.json",
        "reconstruction_accounting.json",
        "figure_provenance.json",
    ):
        shutil.copy2(base / name, output / name)
    payload = compact_payload(data)
    payload_text = json.dumps(
        payload, separators=(",", ":"), ensure_ascii=False, allow_nan=False
    ).replace("</", "<\\/")
    write_json(output / "error-explorer-data.json", payload)
    render = mistune.create_markdown(plugins=["table"])
    narrative = render(note.read_text())
    narrative = rewrite_html_links(narrative, note.parent, output)
    figure_html = []
    attachments = {}
    figure_md = []
    for i, r in enumerate(figures):
        encoded = base64.b64encode((output / r["file"]).read_bytes()).decode()
        figure_html.append(
            "<details><summary>"
            + html.escape(r["caption"].split(".")[0])
            + '</summary><figure><img alt="'
            + html.escape(r["caption"], quote=True)
            + '" src="data:image/png;base64,'
            + encoded
            + '"><figcaption>'
            + html.escape(r["caption"])
            + "</figcaption></figure></details>"
        )
        key = f"error-figure-{i + 1}.png"
        attachments[key] = {"image/png": encoded}
        figure_md.append(
            f"![{r['caption'].split('.')[0]}](attachment:{key})\n\n{r['caption']}"
        )
    snippet = (
        explorer_markup()
        + '<section id="error-findings" class="ea"><h2>Reviewed interpretation of the error audit</h2>'
        + narrative
        + "<h3>Saved comparison figures</h3>"
        + "".join(figure_html)
        + "</section>"
    )
    js = (
        '<script id="error-analysis-data" type="application/json">'
        + payload_text
        + "</script><script>"
        + script.read_text()
        + "</script>"
    )
    report = (base / "report.html").read_text()
    report = rewrite_html_links(report, base, output)
    report = (
        report.replace("</style>", STYLE + "</style>", 1)
        .replace("<body>", "<body>" + snippet, 1)
        .replace("</body>", js + "</body>", 1)
    )
    (output / "report.html").write_text(report)
    original = json.loads((base / "population_grid.executed.ipynb").read_text())
    notebook = json.loads(json.dumps(original))
    intro = "This saved-result error section was added after the original model execution. It reads authenticated saved predictions through `scripts/population_grid_error_analysis.py`; no model was fitted or replayed. Every prior notebook cell/output below is unchanged. The independent review and analysis receipts identify the new computation. Open [the interactive handoff](report.html#error-explorer) for all9,216 included training/development matrices, all decoder/target/seed choices and exact paired switches.\n\n"
    markdown = (
        intro
        + note.read_text()
        + "\n\n## Saved error-comparison figures\n\n"
        + "\n\n".join(figure_md)
    )

    # Resolve original note links without changing preserved earlier notebook cells.
    def relink(match):
        target = match.group(2)
        if re.match(r"[a-zA-Z]+:|#|attachment:", target):
            return match.group(0)
        resolved = (note.parent / target).resolve()
        return (
            match.group(1)
            + "("
            + Path(os.path.relpath(resolved, output)).as_posix()
            + ")"
        )

    # Only note links need rebasing; intro/attachment links already target this directory.
    rebased_note = re.sub(r"(!?\[[^\]]+\])\(([^\s)]+)\)", relink, note.read_text())
    markdown = (
        intro
        + rebased_note
        + "\n\n## Saved error-comparison figures\n\n"
        + "\n\n".join(figure_md)
    )
    addition = nbformat.v4.new_markdown_cell(
        markdown, id="error-audit-20261111", attachments=attachments
    )
    notebook["cells"].insert(1, addition)
    notebook["metadata"]["population_grid_error_addition"] = {
        "base_collation_sha256": BASE_COLLATION,
        "analysis_receipt_sha256": ANALYSIS_RECEIPT,
        "note_sha256": start_hashes["note"],
        "new_fits": 0,
        "model_loads": 0,
        "preserved_prior_cells": True,
    }
    assert notebook["cells"][:1] + notebook["cells"][2:] == original["cells"]
    nbformat.validate(nbformat.from_dict(notebook))
    (output / "population_grid.executed.ipynb").write_text(
        json.dumps(notebook, ensure_ascii=False, indent=1) + "\n"
    )
    (output / "error-interpretation.md").write_text(rebased_note)
    # Standalone lesson has no required file-relative dependencies.
    lesson_snippet = snippet

    def pointer(match):
        target = html.unescape(match.group(1))
        if re.match(r"[a-zA-Z]+:|#", target):
            return match.group(0)
        return (
            match.group(2)
            + " <small>(server file: <code>"
            + html.escape(str((output / target).resolve()))
            + "</code>)</small>"
        )

    lesson_snippet = re.sub(
        r'<a href="([^"]+)">(.*?)</a>', pointer, lesson_snippet, flags=re.S
    )
    lesson = teach_source.read_text()
    lesson = lesson.replace("</style>", STYLE + "</style>", 1)
    lesson = lesson.replace(
        "<nav>", '<nav><a href="#error-explorer">Confusions + errors</a>', 1
    )
    lesson = lesson.replace(
        '<section id="explore">', lesson_snippet + '<section id="explore">', 1
    )
    lesson = lesson.replace("</body>", js + "</body>", 1)
    lesson = lesson.replace(str(teach_source), str(teach_output))
    teach_output.parent.mkdir(parents=True, mode=0o700)
    teach_output.write_text(lesson)
    teach_output.chmod(0o600)
    assert start_hashes == {
        "builder": sha(__file__),
        "javascript": sha(script),
        "note": sha(note),
    }
    manifest = dict(
        classification="reviewed post-hoc saved-result presentation; no fitting",
        original_receipt_sha256=data["receipt_sha256"],
        analysis_receipt_sha256=ANALYSIS_RECEIPT,
        base_collation_sha256=BASE_COLLATION,
        base_teach_sha256=BASE_TEACH,
        source_sha256=start_hashes,
        note_source=str(note.relative_to(ROOT)),
        original_run_figures=246,
        prior_image_occurrences=249,
        new_figures=len(figures),
        preserved_prior_notebook_cells=len(original["cells"]),
        preserved_executed_code_cells=12,
        new_fits=0,
        model_loads=0,
        biological_replays=0,
        compact_matrix_count=sum(
            len([key for key in head if key != "labels"])
            for case in payload["matrices"].values()
            for model in case.values()
            for head in model.values()
        ),
        teach_path=str(teach_output),
        teach_sha256=sha(teach_output),
        authenticated_analysis_inputs=len(analysis_manifest["inputs_sha256"]),
        authenticated_prior_deliverables=len(base_manifest["files_sha256"]),
        files_sha256={
            p.relative_to(output).as_posix(): sha(p)
            for p in sorted(output.rglob("*"))
            if p.is_file()
        },
    )
    write_json(output / "error-handoff-receipt.json", manifest)
    return {k: v for k, v in manifest.items() if k != "files_sha256"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for argument in (
        "analysis",
        "base",
        "output",
        "note",
        "teach-source",
        "teach-output",
    ):
        parser.add_argument("--" + argument, type=Path, required=True)
    args = parser.parse_args()
    print(
        json.dumps(
            build(
                args.analysis.resolve(),
                args.base.resolve(),
                args.output.resolve(),
                args.note.resolve(),
                args.teach_source.resolve(),
                args.teach_output.resolve(),
            ),
            indent=2,
        )
    )
