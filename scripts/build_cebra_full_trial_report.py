"""Render verified transfer results; no fitting or private raw-data access."""
from __future__ import annotations

import argparse
import base64
import csv
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from markdown_it import MarkdownIt

NAMES = {"cue_time": "Cue Time", "full_time": "Broader Time", "cue_behavior": "Cue Behavior", "full_behavior": "Broader Behavior", "raw290": "Raw cue", "pca8": "PCA cue"}
ORDER = tuple(NAMES)


def load_json(path):
    return json.loads(Path(path).read_text())


def table(headers, rows):
    return "\n".join(["| " + " | ".join(headers) + " |", "|" + "---|" * len(headers), *["| " + " | ".join(map(str, row)) + " |" for row in rows]])


def build(run: Path, verify: Path, output: Path):
    receipt = load_json(verify / "verification_receipt.json")
    if receipt["status"] != "verified_forward_only" or Path(receipt["run_dir"]).resolve() != run.resolve():
        raise ValueError("matching verified run required")
    with (run / "metrics.csv").open() as f:
        metrics = list(csv.DictReader(f))
    summary = load_json(run / "summary.json")
    sensitivity = load_json(run / "source_sensitivity_summary.json")
    runtime = load_json(run / "runtime_manifest.json")
    rows = {}
    for rep in ORDER:
        for readout in ("logistic", "svc"):
            selected = [r for r in metrics if r["world"] == "observed" and r["split"] == "validation" and r["representation"] == rep and r["readout"] == readout]
            assert len(selected) == 3 and {int(r["seed"]) for r in selected} == {0, 1, 2}
            rows[(rep, readout)] = {key: float(np.mean([float(r[key]) for r in selected])) for key in ("balanced_accuracy", "auroc", "recall_absent", "recall_present")}
            if readout == "logistic":
                rows[(rep, readout)]["balanced_log_loss"] = float(np.mean([float(r["balanced_log_loss"]) for r in selected]))
            rows[(rep, readout)]["seed_rows"] = sorted(selected, key=lambda r: int(r["seed"]))
    output.mkdir(parents=True, exist_ok=True)
    # Keep generated PNGs with ignored canonical outputs; HTML embeds both images.
    figures = run.parent / "report-figures"
    figures.mkdir(exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.4), layout="constrained")
    labels = [NAMES[r].replace(" ", "\n") for r in ORDER]
    losses = [rows[(r, "logistic")]["balanced_log_loss"] for r in ORDER]
    axes[0].bar(np.arange(6), losses, color=["#8497b0", "#187c91", "#afa0bd", "#775996", "#b4b4b4", "#888888"])
    for i, rep in enumerate(ORDER):
        axes[0].scatter(np.full(3, i), [float(r["balanced_log_loss"]) for r in rows[(rep, "logistic")]["seed_rows"]], color="black", s=20, zorder=3)
    axes[0].axhline(np.log(2), ls="--", color="#d24a3a", label="constant .5")
    axes[0].set(ylabel="Balanced log loss (lower better)", xticks=np.arange(6), xticklabels=labels, title="Cue-only logistic readout")
    axes[0].legend()
    for shift, head, color in [(-.18, "logistic", "#187c91"), (.18, "svc", "#b57629")]:
        axes[1].bar(np.arange(6) + shift, [100 * rows[(r, head)]["balanced_accuracy"] for r in ORDER], width=.35, color=color, label=head)
    axes[1].axhline(50, ls="--", color="#d24a3a")
    axes[1].set(ylabel="Balanced accuracy (%)", ylim=(0, 100), xticks=np.arange(6), xticklabels=labels, title="Both fixed readouts; matched controls")
    axes[1].legend()
    fig.savefig(figures / "matched-results.png", dpi=150)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(7.5, 3.7), layout="constrained")
    nulls = summary["null_time_logistic_mean_gains"]
    gain = summary["observed_time_logistic_mean_gain"]
    ax.hist(nulls, bins=8, color="#b5cbd1", edgecolor="white", label="20 source-label null worlds")
    ax.axvline(gain, color="#a13c2f", lw=2, label=f"Observed three-seed mean: {gain:+.4f}")
    ax.axvline(0, color="black", ls=":")
    ax.set(xlabel="Cue loss minus broader-training loss (positive favors broader)", ylabel="Null worlds", title="No-association reference, not an equal-risk superiority test")
    ax.legend(fontsize=8)
    fig.savefig(figures / "paired-null.png", dpi=150)
    plt.close(fig)
    lead = summary["worthwhile_exploratory_followup_lead"]
    time_cue, time_full = rows[("cue_time", "logistic")], rows[("full_time", "logistic")]
    verdict = "The predeclared primary exploratory follow-up criterion passed; this is not confirmation." if lead else "The predeclared primary exploratory follow-up criterion did not pass."
    metrics_table = table(["Representation", "Logistic loss ↓", "Logistic BA", "Logistic AUROC", "RBF BA", "RBF AUROC"], [[NAMES[r], f"{rows[(r, 'logistic')]['balanced_log_loss']:.6f}", f"{100*rows[(r, 'logistic')]['balanced_accuracy']:.2f}%", f"{rows[(r, 'logistic')]['auroc']:.3f}", f"{100*rows[(r, 'svc')]['balanced_accuracy']:.2f}%", f"{rows[(r, 'svc')]['auroc']:.3f}"] for r in ORDER])
    paired_table = table(["Seed", "Time cue−broader loss", "Broader Time BA", "Broader Time AUROC", "Behavior cue−broader loss"], [[s, f"{summary['observed_time_logistic_seed_gains_cue_minus_full_loss'][s]:+.6f}", f"{100*float(rows[('full_time', 'logistic')]['seed_rows'][s]['balanced_accuracy']):.2f}%", f"{float(rows[('full_time', 'logistic')]['seed_rows'][s]['auroc']):.3f}", f"{summary['observed_behavior_logistic_seed_gains_cue_minus_full_loss'][s]:+.6f}"] for s in range(3)])
    with (run / "validation_source_resamples.csv").open() as handle:
        source_rows = [r for r in csv.DictReader(handle) if r['objective'] == 'time' and r['readout'] == 'logistic' and r['seed'] == 'mean' and r['estimable'] == 'True']
    full_ba_quantiles = np.quantile([float(r['full_ba']) for r in source_rows], [.025, .5, .975]).tolist()
    absolute_time_tail = summary['absolute_full_arm_no_association_references']['time']['inclusive_tail']
    quantiles = sensitivity["time_mean_gain_quantiles_025_50_975"]
    primary_tail = summary["null_time_logistic_inclusive_p_ge_observed"]
    family_tail = summary["null_max_two_objectives_inclusive_tail"]
    text = f"""# Does broader CEBRA training help cue-only decoding?

**Completed exploratory experiment · September24–25,2026.**
[Offline illustrated HTML](report.html) · [Frozen protocol](protocol.md) · [Execution/review ledger](execution.md)

## Answer

**{verdict}** Time/logistic balanced loss changed from **{time_cue['balanced_log_loss']:.6f}** with cue-only encoder training to **{time_full['balanced_log_loss']:.6f}** with broader training: paired gain **{gain:+.6f} nats**. Its balanced accuracy changed from **{100*time_cue['balanced_accuracy']:.2f}%** to **{100*time_full['balanced_accuracy']:.2f}%**. Constant-.5 loss is **{np.log(2):.6f}** and chance BA is **50%**.

**Your idea improved this cue-only readout for CEBRA-Time; Behavior was not similarly helped.** Time loss improved in all three computational seeds, but absolute discrimination was uneven: only one seed had AUROC above .5. That is an informative pipeline result, not established biological path information.

The experiment distinguishes training coverage from prediction inputs. Navigation activity was added **only while training the encoder on training source trials**. Both decoder fitting and historical-validation prediction received **only the original cue window**. This is not decoding the path after observing its navigation activity.

## Matched results

All numbers below are means of three paired assembly/optimizer seeds. Seeds are computational sensitivity, not three independent biological replications. Lower loss and higher BA/AUROC mean different things; a loss improvement that remains worse than the constant baseline does not, by itself, satisfy this study's declared success rule or establish prospective coding.

{metrics_table}

![Matched losses and balanced accuracies](figures/matched-results.png)

{paired_table}

The frozen primary follow-up rule required all four: Time loss gain≥.01nats, broader-Time loss<log2, BA>50%, AUROC>.5. Component decisions are `{json.dumps(summary['criteria'], sort_keys=True)}`. Behavior and the RBF readout were predeclared secondary comparisons, not outcome-selected replacements for the primary analysis. No hyperparameter/threshold/checkpoint was selected after observing these results.

## Null and source sensitivity

The source-coherent label null repeats the entire conditional assembly, scaler, encoder, PCA and decoder pipeline in20worlds, with all three seeds in each world. The observed **three-seed mean** gain is compared to that same statistic in each null world—not to an unrelated single-seed anchor.

- Primary Time/logistic paired-gain inclusive plus-one tail: **{primary_tail:.6f}** ({round(primary_tail*21)}/21).
- Maximum-over-two-objectives paired-gain tail: **{family_tail:.6f}** ({round(family_tail*21)}/21).
- **Absolute broader-Time performance:** its loss-based no-association tail is **{absolute_time_tail:.6f}** ({round(absolute_time_tail*21)}/21). The small primary paired-gain tail concerns improvement over a poor cue-only model; it is not evidence that the broader model's absolute path decoding passed its null.
- These are limited-resolution no-association references, **not general tests of equal predictive risk/superiority**, and they do not undo prior adaptive exposure or unresolved serial exchangeability.
- Paired source-reweighting gain2.5/50/97.5% quantiles: **{quantiles[0]:+.6f} / {quantiles[1]:+.6f} / {quantiles[2]:+.6f}**. These are fixed-model pool-weight sensitivity, **not biological confidence intervals**.
- Broader-Time BA source-weight 2.5/50/97.5% quantiles: **{100*full_ba_quantiles[0]:.2f}% / {100*full_ba_quantiles[1]:.2f}% / {100*full_ba_quantiles[2]:.2f}%**. Absolute discrimination is more fragile than the relative loss gain.
- {sensitivity['inestimable_deletions']}/22source deletions are inestimable because a class loses support; these were retained explicitly. Singleton pools cannot estimate variability from unseen sources.

![Paired-gain null reference](figures/paired-null.png)

Full-arm baseline-relative null references, all observed seed/metric rows, and sensitivity summaries are in [summary.json](summary.json). Complete per-source/per-world arrays remain in the ignored local run directory. The primary rule alone cannot establish biological signal.

## What was actually compared?

- **Fixed cohort/target:** 29 selected unit IDs, seven session blocks;82training+22historical-validation sources; endpoint4→3; presence of `D_N_R_T__N_R_M` among all interior corridor runs after removing first/last runs. It is not full-path reconstruction or endpoint classification.
- **Population construction:** 64 known-label-conditioned training rows/class; exact validation30combinations (24absent/6present), half the evaluation mass/class. These synthetic combinations are not30independent natural trials or a simultaneous29-unit population. Time omits path labels from its objective, but assembly is still label-conditioned.
- **Cue readout:** ten 100-ms bins in the original first-second window, with actual cue-offset clipping where needed. Encoder8coordinates/bin→80decoder features; raw cue has290features. PCA8/bin uses one pooled training-bin basis.
- **Broader training:** retained cue window plus complete native100-ms navigation bins across the training sources' navigation span. Small cue tails beyond one second and final partial navigation bins are excluded and audited. “Full” in machine arm IDs is shorthand, not literal use of every millisecond.
- **Variable duration:** navigation source bins are never time-warped or zero-filled. A normalized-duration pair bank matches relative phase progress across session blocks. Each Time positive advances every block by its own actual next100-ms bin. Pair-bank rows are **not a real continuous pseudotrajectory or physical-position alignment**.
- **Matched encoder budget:** four arms (cue/broader × Time/Behavior), shared cue-fitted scaler, paired model initialization, offset1pointwise encoder, hidden32/output8, cosine temperature1, Adam3e−4, batch256,1000updates. Broader training samples50/50cue/navigation; the intervention therefore reallocates a fixed contrastive budget, not additional optimization steps.
- **Fixed readouts:** scaled logistic C.01 and scaled RBF-SVM C1/gamma=scale; no new tuning. Raw/PCA controls use identical newly assembled cue rows. Do not transplant scores from older differently assembled/optimized experiments.

## What can and cannot follow

This tests whether one specified broader-training representation transfers better to cue-only decoding across historically disjoint source pools **within the existing sessions**. Any positive result remains condition-level association beyond a fixed endpoint, with unresolved cue/history/view and selected-cell/source-support confounds. Known future labels also define validation assembly, so this is not an operational unknown-trial predictor.

It does not establish intention, causal planning, a simultaneous population state, H1confirmation, H1bgeometry or H2. A negative result does not show absence of cue information or that broader pretraining can never help. Different coverage weighting, temporal encoders or independent recordings are untested—not queued automatically by this report. The historically exposed validation pool is not a pristine test set.

## Execution and reproducibility

Exactly **252CEBRA encoders** (12observed+240null), **63PCA transforms** and **756readouts** were fitted under the frozen family. Verification replays every model without fitting; shared helper logic is complemented by independent numerical/claim review. Software controls and rejected implementation drafts are not biological replications.

- Fit code revision: `{runtime['git']['head']}`; exact executed code/protocol/helper snapshots and package/device metadata are retained with the run.
- Accepted local run: `{run}`.
- Forward-only verification: `{verify}`; [compact verification receipt](verification.json).
- The new worktree is retained through PR review; private data/models live in canonical outputs, not Git. No persistent service or public endpoint was created.

See [execution.md](execution.md) for review resolutions, commands, static-check limitations, and retained QA attempts. Git is not a backup of ignored private inputs/models. AI review is QA, not laboratory metadata verification or scientific peer review.
"""
    # Readable typography in the human report; do not alter target IDs or code paths.
    for old, new in {
        'September24–25,2026': 'September 24–25, 2026', 'gain≥.01nats': 'gain ≥ .01 nats',
        'in20worlds': 'in 20 worlds', 'gain2.5/50/97.5%': 'gain 2.5/50/97.5%',
        '/22source': '/22 source', ':29selected': ': 29 selected', ';82training+22historical-validation': '; 82 training + 22 historical-validation',
        'endpoint4→3': 'endpoint 4→3', ':64known-label': ': 64 known-label', 'validation30combinations': 'validation 30 combinations',
        '(24absent/6present)': '(24 absent / 6 present)', 'not30independent': 'not 30 independent', 'simultaneous29-unit': 'simultaneous 29-unit',
        ':ten100-ms': ': ten 100-ms', 'Encoder8coordinates/bin→80decoder': 'Encoder: 8 coordinates/bin → 80 decoder',
        'has290features': 'has 290 features', 'PCA8/bin': 'PCA 8/bin', ':retained': ': retained', 'native100-ms': 'native 100-ms',
        ':navigation': ': navigation', 'next100-ms': 'next 100-ms', ':fourarms': ': four arms', 'offset1pointwise': 'offset1 pointwise',
        'hidden32/output8': 'hidden 32 / output 8', 'temperature1': 'temperature 1', 'Adam3e−4': 'Adam 3e−4',
        'batch256,1000updates': 'batch 256, 1,000 updates', 'samples50/50cue/navigation': 'samples 50/50 cue/navigation',
        ':scaled': ': scaled', 'C.01': 'C=.01', 'C1/gamma=scale': 'C=1 / gamma=scale',
        'H1confirmation': 'H1 confirmation', 'H1bgeometry': 'H1b geometry', '**252CEBRA': '**252 CEBRA',
        '(12observed+240null)': '(12 observed + 240 null)', '**63PCA': '**63 PCA', '**756readouts': '**756 readouts'
    }.items():
        text = text.replace(old, new)
    markdown = text.replace("![Matched losses and balanced accuracies](figures/matched-results.png)", "[View the matched-result figures in the offline report](report.html).")
    markdown = markdown.replace("![Paired-gain null reference](figures/paired-null.png)", "[View the paired-gain null figure in the offline report](report.html).")
    (output / "README.md").write_text(markdown)
    machine = {"run": str(run), "verification": str(verify), "primary_and_nulls": summary, "source_sensitivity": sensitivity,
               "primary_full_ba_source_weight_quantiles": full_ba_quantiles,
               "observed": {f"{rep}/{head}": value for (rep, head), value in rows.items()}}
    (output / "summary.json").write_text(json.dumps(machine, indent=2) + "\n")
    (output / "verification.json").write_text(json.dumps(receipt, indent=2) + "\n")
    html_body = MarkdownIt("commonmark").enable("table").render(text)
    for name in ("matched-results.png", "paired-null.png"):
        encoded = base64.b64encode((figures / name).read_bytes()).decode()
        html_body = html_body.replace(f'src="figures/{name}"', f'src="data:image/png;base64,{encoded}"')
    # This is a portable static report, not a new server/dashboard.
    html = '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>CEBRA broader training, cue-only decoding</title><style>body{max-width:1050px;margin:auto;padding:24px;font:17px/1.65 system-ui;color:#182c37}img{max-width:100%;height:auto}table{display:block;overflow-x:auto;border-collapse:collapse;font-size:14px}td,th{padding:9px;border-bottom:1px solid #ddd}code{overflow-wrap:anywhere;font-size:.85em}a{color:#12687e}h1,h2{line-height:1.2}h2{margin-top:2em}</style><body>' + html_body + '</body></html>'
    assert 'src="figures/' not in html and '<script' not in html and html.count('src="data:image/png;base64,') == 2
    (output / "report.html").write_text(html)
    print(json.dumps({"output": str(output), "primary_gain": gain, "primary_lead": lead, "observed_groups": len(rows)}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--verify-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    build(args.run_dir, args.verify_dir, args.output_dir)
