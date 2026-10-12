# CEBRA-Time retrospective

**Working draft 03, not a finished paper.** This package owns the current manuscript,
its editorial feedback and presentation-only tools. Past studies live in
[weekly history](../history/README.md); the [evidence catalog](../docs/reports/README.md)
links their original methods, results and limitations.

## Read or edit

| File | Purpose |
| --- | --- |
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

## Next work: report first, then notebook

1. Finish the [feedback ledger](feedback-20261012.md): defer shuffle/loss detail,
   distinguish training diagnostics from scientific results, clarify real-source
   marginal counts and within-bin variability. Do not run missing analyses to fill gaps.
2. Build **one companion Jupyter notebook**, with its target/cohort and approved inputs
   specified first. Start with tracked aggregates, visible provenance, shape/count/split
   assertions and explanations beside each figure. Import shared implementation from
   `src/neuro/`; do not copy scientific algorithms into notebook cells.
3. Require restart-and-run-all without hidden cell state. Private predictions/checkpoints
   must not leak into committed outputs. Fits and private replay remain separate approvals.

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
