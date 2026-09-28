"""Presentation diagrams; fictional examples are labelled, results use saved summary."""

import html
import math


def number(value: str | float) -> float:
    """Fail clearly on malformed/nonfinite saved numerical evidence."""
    try:
        result = float(value)
    except (TypeError, ValueError) as error:
        raise ValueError("Invalid saved evidence number") from error
    if not math.isfinite(result):
        raise ValueError("Nonfinite saved evidence number")
    return result


def flow(items: list[tuple[str, str]], label: str, *, kind: str = "") -> str:
    """Responsive diagram shared by several short processing chains."""
    boxes = '<span class="flow-arrow" aria-hidden="true">→</span>'.join(
        f'<div class="flow-node"><b>{title}</b><span>{detail}</span></div>'
        for title, detail in items
    )
    return f'<figure class="process {kind}" role="group" aria-label="{html.escape(label)}">{boxes}</figure>'


def encoder() -> str:
    columns = [
        (70, 5, "195 / 29", "input units"),
        (225, 6, "32", "GELU"),
        (370, 6, "32", "GELU"),
        (515, 4, "16", "GELU"),
        (670, 4, "8", "unit-length zₜ"),
    ]
    nodes = [
        [(x, 140 + (i - (n - 1) / 2) * 24) for i in range(n)] for x, n, _, _ in columns
    ]
    parts = [
        '<figure class="diagram"><div class="chart-scroll" tabindex="0" role="region" aria-label="Encoder architecture"><svg viewBox="0 0 820 365" role="img" aria-labelledby="encoder-title encoder-desc"><title id="encoder-title">Pointwise CEBRA-Time encoder and whole-cue decoder</title><desc id="encoder-desc">One standardized count bin enters a multilayer perceptron:195 or29 inputs,32,32,16 hidden units,8 normalized outputs. Apply the same network to ten bins, concatenate to80 features, then fit a supervised decoder.</desc><text x="35" y="30" class="svg-heading">One 100-ms bin · shared network for every bin</text>'
    ]
    for left, right in zip(nodes[:-1], nodes[1:], strict=True):
        for x1, y1 in left:
            for x2, y2 in right:
                parts.append(
                    f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#b6c8c4" stroke-width=".65"/>'
                )
    for (x, _, width, subtitle), group in zip(columns, nodes, strict=True):
        for cx, cy in group:
            parts.append(
                f'<circle cx="{cx}" cy="{cy}" r="7" fill="#e1f0e9" stroke="#19746b" stroke-width="2"/>'
            )
        parts.append(
            f'<text x="{x}" y="246" text-anchor="middle" font-weight="700">{width}</text><text x="{x}" y="267" text-anchor="middle" font-size="13">{subtitle}</text>'
        )
    parts.append(
        '<path d="M670 284 V297 H75 V313" fill="none" stroke="#19746b" stroke-width="2"/><rect x="30" y="314" width="250" height="36" rx="8" fill="#e1f0e9"/><text x="155" y="338" text-anchor="middle" font-size="14">z₁ ⊕ z₂ ⊕ … ⊕ z₁₀ → 80 features</text><text x="299" y="338" font-size="23">→</text><rect x="333" y="314" width="245" height="36" rx="8" fill="#e5edf8"/><text x="455" y="338" text-anchor="middle" font-size="14">train-only scaling → fitted decoder</text><text x="591" y="338" font-size="23">→</text><text x="632" y="337" font-size="14">target prediction</text></svg></div></figure>'
    )
    return "".join(parts)


def targets() -> str:
    return """<figure class="diagram"><div class="chart-scroll" tabindex="0" role="region" aria-label="Four target outputs and two schematic paths"><svg viewBox="0 0 820 260" role="img" aria-labelledby="target-title target-desc"><title id="target-title">Same endpoints do not imply the same path</title><desc id="target-desc">Teaching graph: path S to A to B to G and path S to C to B to G have the same start and goal. Only the first uses edge A to B. Endpoint pair, start, goal and edge existence are distinct targets.</desc><text x="28" y="30" class="svg-heading">Teaching maze · not the laboratory map</text><path d="M60 145 L160 80 L275 145 L390 145" fill="none" stroke="#168477" stroke-width="5"/><path d="M60 145 L160 210 L275 145 L390 145" fill="none" stroke="#416db0" stroke-width="4" stroke-dasharray="7 5"/><path d="M210 101 L228 119 L205 119" fill="#168477"/><path d="M205 180 L229 169 L214 189" fill="#416db0"/>
    <g fill="#fff" stroke="#254850" stroke-width="2"><circle cx="60" cy="145" r="19"/><circle cx="160" cy="80" r="19"/><circle cx="160" cy="210" r="19"/><circle cx="275" cy="145" r="19"/><circle cx="390" cy="145" r="19"/></g>
    <g text-anchor="middle" font-weight="700"><text x="60" y="151">S</text><text x="160" y="86">A</text><text x="160" y="216">C</text><text x="275" y="151">B</text><text x="390" y="151">G</text></g>
    <text x="480" y="67" font-weight="700">Both routes: pair = (S, G)</text><text x="480" y="105">Start = S</text><text x="480" y="140">Goal = G</text><text x="480" y="183" fill="#168477">Solid route: edge A→B present</text><text x="480" y="220" fill="#416db0">Dashed route: edge A→B absent</text></svg></div></figure>"""


def paired_loss(summary: dict) -> str:
    """Redraw the accepted three paired losses, including the constant baseline."""
    observed = summary["observed"]

    def scale(value):
        return 180 + (number(value) - 0.4) * 640

    baseline = scale(math.log(2))
    parts = [
        f'<figure class="diagram"><div class="chart-scroll" tabindex="0" role="region" aria-label="Paired saved prediction losses"><svg viewBox="0 0 820 295" role="img" aria-labelledby="paired-title paired-desc"><title id="paired-title">Paired Time prediction losses, all three computational seeds</title><desc id="paired-desc">Every joint-trained encoder improves loss relative to its cue-only counterpart. Only seed zero beats constant .5. Lower is better; seeds are not biological replicates.</desc><text x="180" y="25" class="svg-heading">Prediction log loss · lower is better</text><line x1="{baseline}" x2="{baseline}" y1="53" y2="226" stroke="#a3511d" stroke-width="2" stroke-dasharray="6 5"/><text x="{baseline + 8}" y="53" font-size="12">constant .5 · ln2</text>'
    ]
    for i, (cue, joint) in enumerate(
        zip(
            observed["cue_time/logistic"]["seed_rows"],
            observed["full_time/logistic"]["seed_rows"],
            strict=True,
        )
    ):
        assert cue["seed"] == joint["seed"] == str(i)
        y = 95 + i * 60
        x1, x2 = scale(cue["balanced_log_loss"]), scale(joint["balanced_log_loss"])
        parts.append(
            f'<text x="40" y="{y + 5}">Seed {i}</text><line x1="180" x2="692" y1="{y}" y2="{y}" stroke="#d8e0dd"/><line x1="{x1}" x2="{x2}" y1="{y}" y2="{y}" stroke="#819293" stroke-width="3"/><rect x="{x1 - 6}" y="{y - 6}" width="12" height="12" fill="#416db0"/><circle cx="{x2}" cy="{y}" r="7" fill="#168477"/><text x="{x2}" y="{y - 13}" text-anchor="middle" font-size="12">{number(joint["balanced_log_loss"]):.3f}</text><text x="{x1}" y="{y - 13}" text-anchor="middle" font-size="12">{number(cue["balanced_log_loss"]):.3f}</text>'
        )
    for tick in (0.4, 0.6, 0.8, 1.0, 1.2):
        parts.append(
            f'<text x="{scale(tick)}" y="247" text-anchor="middle" font-size="13">{tick:.1f}</text>'
        )
    parts.append(
        '<rect x="180" y="272" width="10" height="10" fill="#416db0"/><text x="198" y="282" font-size="14">cue-only</text><circle cx="390" cy="277" r="6" fill="#168477"/><text x="405" y="282" font-size="14">joint cue/navigation</text></svg></div><figcaption>Saved logistic-readout losses. Pairing controls computational initialization/assembly; the three seeds share evaluation source pools, so this is not a biological uncertainty interval. <a href="#s7">S7</a>.</figcaption></figure>'
    )
    return "".join(parts)


def all_diagrams(summary: dict) -> dict[str, str]:
    return {
        "DATAFLOW": flow(
            [
                ("Recorded streams", "Spikes + trial markers<br>+ behavior"),
                ("Align and bin", "Trial/phase timestamps<br>→ spike counts"),
                ("Source ledger", "Session × trial identity<br>+ observation mask"),
                (
                    "Conditional assembly",
                    "Match real source blocks<br>→ synthetic population",
                ),
            ],
            "Recorded signals through derived features to a conditional pseudopopulation",
        ),
        "ASSEMBLY": """<figure class="assembly" role="group" aria-label="Fictional two-session construction example">
<div class="source-block"><b>Session A · chosen trial a</b><span>2 recorded units</span><code>bin3 [2, 0]<br>bin4 [1, 2]</code></div><span class="flow-arrow" aria-hidden="true">⊕</span><div class="source-block alt"><b>Session B · chosen trial b</b><span>3 different units</span><code>bin3 [1, 4, 0]<br>bin4 [0, 3, 1]</code></div><span class="flow-arrow" aria-hidden="true">→</span><div class="source-block result"><b>One synthetic5-unit row</b><span>Same sources across bins</span><code>bin3 [2, 0 | 1, 4, 0]<br>bin4 [1, 2 | 0, 3, 1]</code></div></figure>""",
        "ENCODER": encoder(),
        "BASELINES": """<figure class="lanes" role="group" aria-label="Parallel baseline pathways"><div><b>Raw</b><span>10 bins ×195 /29 units</span><i>→</i><span>1,950 /290 features</span><i>→</i><strong>fitted readout</strong></div><div><b>PCA</b><span>train-only scaler + PCA8/bin</span><i>→</i><span>10 ×8 =80 features</span><i>→</i><strong>fitted readout</strong></div><div><b>LDA</b><span>raw per-bin counts + labels</span><i>→</i><span>supervised discriminants</span><i>→</i><strong>class prediction</strong></div><figcaption>No arrow from PCA into CEBRA. Match task, input window, folds and readout policy when testing representation differences; historical per-bin LDA is not an80-feature whole-cue match.</figcaption></figure>""",
        "TARGETS": targets(),
        "JOINT_PIPELINE": """<figure role="group" aria-label="Matched encoder arms followed by cue-only prediction"><div class="two-col"><div class="training-arm"><b>Cue-only training</b><span>100% cue pairs</span><div class="model-box">f<sub>cue</sub> ·1,000 updates</div></div><div class="training-arm alt"><b>Joint cue/navigation training</b><span>50% cue /50% navigation pairs</span><div class="model-box">f<sub>joint</sub> ·1,000 updates</div></div></div><div class="common-readout"><b>Same readout policy; separately fitted decoder per arm</b><p>Training cue → frozen encoder → fit that arm's decoder<br>Held-out cue → frozen encoder → that arm's fixed decoder → component prediction</p><span>No held-out navigation features enter either pipeline.</span></div></figure>""",
        "NAV_PAIRS": """<figure class="pair-bank" role="group" aria-label="Toy native navigation adjacency pair bank"><div><b>Bank entry</b><span>0</span><span>1</span><span>2</span><span>3</span><span>4</span><span>5</span></div><div><b>A ·4 bins</b><span>0→1</span><span>0→1</span><span>1→2</span><span>1→2</span><span>2→3</span><span>2→3</span></div><div><b>B ·7 bins</b><span>0→1</span><span>1→2</span><span>2→3</span><span>3→4</span><span>4→5</span><span>5→6</span></div></figure>""",
        "JOINT_RESULTS": paired_loss(summary),
        "DECODERS": flow(
            [
                (
                    "One frozen representation",
                    "Same training features<br>and source-safe evaluation",
                ),
                (
                    "Alternative fitted readouts",
                    "Linear logistic<br>vs nonlinear RBF / kNN",
                ),
                (
                    "Matched outcome metric",
                    "Accuracy ≠ ranking<br>≠ probability quality",
                ),
            ],
            "Frozen representation followed by separately fitted readouts and a matched held-out metric",
        ),
        "FUTURE": flow(
            [
                (
                    "Specify the assay",
                    "Sources · target · metric<br>two checkpoints · budget",
                ),
                (
                    "A · Select decoder policy",
                    "Inner-source validation<br>both arms / checkpoints",
                ),
                (
                    "Lock selection rule",
                    "No outer-score selection<br>fresh weights per representation",
                ),
                (
                    "B · Compare training arms",
                    "Separate outer evaluation<br>cue-only prediction",
                ),
            ],
            "Proposed two-stage decoder and encoder evaluation, not yet executed",
            kind="proposed",
        ),
    }
