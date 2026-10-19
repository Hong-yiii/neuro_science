# CEBRA-Time review notebook and retrospective

**Start with the [executed review notebook](endpoint_walkthrough.ipynb).** It follows
saved standardized cue → fitted PCA/CEBRA → readouts → verified evidence, with inline
equations, tensor diagrams, source-count views, confusions and all-seed comparisons.
GitHub renders its saved outputs without access to the private artifacts.

**Manuscript: working draft 03, not a finished paper.** This package owns the notebook,
current manuscript, editorial feedback and presentation tools. Past studies live in
[weekly history](../history/README.md); the [evidence catalog](../docs/reports/README.md)
links their original methods, results and limitations.

## Read or edit

| File | Purpose |
| --- | --- |
| [endpoint_walkthrough.ipynb](endpoint_walkthrough.ipynb) | Primary professor-facing artifact; executed saved-model walkthrough, 14 code cells and 15 inline images |
| [endpoint_replay.py](endpoint_replay.py) | Narrow authenticated observed-input adapter using current package operations; no fits |
| [manuscript.html](manuscript.html) | Editable revision03 source; build before reading offline |
| [retrospective-frozen-20261012.html](retrospective-frozen-20261012.html) | Standalone reading file; preserved checksum difference below |
| [feedback-20261012.md](feedback-20261012.md) | Original feedback and remaining editorial checklist |
| [outline.html](outline.html) | Historical revision02 source, not the current manuscript |

Download raw HTML from GitHub and open it locally; GitHub's source view is not a
rendered preview. Manuscript/outline sources retain historical relative evidence URLs
and are build templates, not standalone files. No server is needed.

## Edit and build

From the repository root, using Python's standard library:

```sh
python3 report/test_layout.py
python3 report/test_path_summary.py
python3 report/test_editorial.py
python3 report/test_build.py
python3 report/build.py
```

The last command builds current `manuscript.html` into
`outputs/cebra-retrospective-20261012/manuscript.html`; it does not overwrite the
frozen milestone. It replaces any previous generated manuscript at that output path.
Pass `outline.html` explicitly only when deliberately building revision02.

The builder embeds existing images, checks anchors/alt text, and preserves evidence
citations at revision `4862267`. Historical path existence is checked; this is not a
full scientific replay or proof that every current evidence byte matches that revision.
No raw data, predictions, checkpoints, fits or scientific runtime are needed.

## Frozen whole-file reading milestone — October 12

**Known integrity issue, preserved rather than silently repaired.** Before this
reorganization, the working file differed from the original milestone. Checkpoint
`ebe8256` records those existing working bytes; `test_build.py` deliberately continues
to reject them against the original expected hash.

- Original milestone at `b55b10f`: SHA-256
  `86497662096908f5fa92f1d00747377b2046e07a37ea225ae8fdbedcc9dfbde6`.
- Preserved working file: SHA-256
  `849fe48f40f9d8140517393bd7686c4153cbf89860fa2eb820216300c00f1a5c`.

Both copies are retained locally under `work/reorganization-weekly-audit/before-build/`.
The original Git blob is recoverable with
`git show b55b10f:docs/reports/cebra-retrospective-20261012/retrospective-frozen-20261012.html`.
Do not change the expected hash just to make the check pass. The builder checks run
before this integrity assertion, but that does **not** make the full test green.

## Saved-artifact notebook: execution and boundaries

October19 owner-approved scope: the accepted October7 **observed endpoint** artifacts,
seeds0–2, not raw recordings or null worlds. The notebook freshly replays six CEBRA
encoders, three PCA states and **495 fitted readouts / 990 split-level score rows**,
with zero fits. Authentication precedes parsing and pickle deserialization; never
substitute an untrusted checkpoint. Private arrays, per-example predictions and source
identifiers remain in memory and outside the published notebook.

This is a **new saved-input replay using current package operations**, not a rerun of
the historical full verifier. It starts at authenticated `scaled_cue.npz`: original
source assembly, input-scaler fitting, navigation preparation and null controls remain
inherited evidence, not newly reproduced. No old approval, helper hash or artifact is
rewritten. See the notebook's verification ledger and original study links.

The recorded scientific runtime is separate from `pyproject.toml`/`uv.lock`. On this
host, a notebook-only overlay inherits the retained scientific environment; creating
it does not modify that runtime:

```sh
scratch/v6-v9-runtime/bin/python -B -m venv \
  --without-pip --system-site-packages scratch/endpoint-notebook-runtime
uv pip install --python scratch/endpoint-notebook-runtime/bin/python \
  -r report/requirements-notebook.txt
```

For a deliberate, authorized re-execution from the repository root:

```sh
export PYTHONPATH="$PWD/src:$PWD/report:$PWD/scratch/v6-v9-runtime/lib/python3.13/site-packages"
export PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1
scratch/endpoint-notebook-runtime/bin/python -B report/run_endpoint_notebook.py
scratch/endpoint-notebook-runtime/bin/python -B report/test_endpoint_notebook.py
```

The runner clears outputs, creates a temporary kernelspec, executes all14 code cells
in a fresh native kernel, checks outputs, then replaces the tracked notebook and writes
`outputs/endpoint-notebook/endpoint_walkthrough.html`. It starts no server and leaves
no registered kernel. The HTML contains inline PNG equations/figures and needs neither
MathJax nor a network connection. Reading existing outputs requires no scientific runtime;
execution requires the approved private run, matching package versions and original CUDA
backend. Notebook execution metadata records UTC time and helper/code hashes.

**Numerical detail:** retain the original two-thread BLAS budget. A one-thread attempt
passed feature replay but failed five probabilities in the seed0 whole-cue pair LDA
readout (maximum difference4.17×10⁻⁷); changing only BLAS threads to two reproduced them
exactly. The full fresh-kernel pass retains the original feature/probability tolerances,
exact labels/predictions and `1e-9` score agreement; no tolerance was relaxed.

[Focused tests](test_endpoint_notebook.py) cover authentication, observed-only scope,
no-fit/thread guards and the executed artifact. Without the scientific environment,
the fit-guard test explicitly skips; the recorded-runtime command above must pass it.
Local preparation/render checks remain under `work/endpoint-notebook-20261019/`, and
native execution logs under the owning session's `.pi/tasks/`; these are not public data.

## Remaining editorial work

Review the October19 [editorial pass](feedback-20261012.md#october19-editorial-pass--training-metrics-and-controls):
training/validation is §2.4, with historical checkpoint accuracy and the latest endpoint
training–development gap; shuffle-heavy detail and displayed loss metrics are deferred
while original criteria and limitations remain. The notebook now supplies real-source
start/goal marginals. A definition of within-bin variability and a matched latest-endpoint
checkpoint trajectory remain unavailable; do not run missing analyses merely to fill gaps.

Here observability means inspectable computation, not formal observability of neural
state. Endpoint decoding, binary path components and full ordered routes remain distinct;
full ordered-route prediction was not evaluated. H1 is unresolved; H2 is removed.

## Delivery and historical checks

For the freshly built manuscript, run on your **local Mac**:

```sh
scp homelab:/home/hongyi-home-lab/neuro_science/outputs/cebra-retrospective-20261012/manuscript.html ./cebra-manuscript.html
open ./cebra-manuscript.html
```

Original editorial iterations, browser receipts and the failed remote-delivery incident
are preserved verbatim in the [publishing history](../history/operations/navigation-20261012/report-readme-before-tidy.md.txt).
Do not treat old preview commands or session IDs as live operations. No remote pane
manipulation or preview server is part of this workflow.

[Migration checks and limits](../docs/reorganization.md) ·
[Codebase design overview](../docs/codebase-design.html) ·
[Future research proposal](../docs/cebra-observability-agenda-20261011.md)
