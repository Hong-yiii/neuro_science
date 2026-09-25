# Learning

This folder is for Hongyi's neuroscience learning path.

Hongyi's background is strongest in ML, deep learning, and NLP. Explanations should bridge from familiar ML concepts into neuroscience concepts, especially:

- what is directly observed versus inferred;
- how cue-period spikes and subsequent behavior become trial-linked tables;
- how prospective path information differs from inferred intention or planning;
- how place/view/conjunctive coding can expose correlated-variable confounds;
- how binning, representation learning, controls, and null models affect claims.

## Working Principle

Learn the neuroscience just in time for H1: cue-period path information beyond
start and goal. Artificial-agent comparison belongs to the later H2 stretch aim.

The goal is not to become a general neuroscientist first. The goal is to
understand enough measurement, preprocessing, and representational analysis to
make careful claims about prospective hippocampal path information.

## Start Here

- `../docs/research-questions.md`: current H1/H2 and claim boundaries.
- `../docs/getting-started-tasks.md`: current executable checklist.
- `neural-agent-action-plan.md`: pre-pivot curriculum retained for supporting
  measurement and validation lessons.
- `../papers/reading-roadmap.md`: pre-pivot reading map, now labeled by relevance
  to H1 versus H2.

## Completed max-context lessons

- **[CEBRA-Time transfer: what improved, what did not, and why the mechanism is unresolved](cebra-time-transfer-teach-max-20260925.html)** — requested September 25, 2026. Download/open the standalone HTML; inline figures, captions and collapsible explanations work offline. It teaches the [PR #9 experiment](https://github.com/Hong-yiii/neuro_science/pull/9), not a new model run. Separate teaching PR is stacked on PR #9 because that experiment has not merged into `main`.
  - Starts from the scientific question, then traces source assembly → native-pair training → frozen encoder → cue-only readout → relative/absolute checks.
  - Distinguishes temporal pairing from temporal-context architecture, label-free objective from label-conditioned measurement, and improvement from biological evidence. Includes full seed/decoder context, source sensitivity, matched controls, a source map and one teach-back question.
  - Source links are pinned to `c19d07c`; actual fitting was at `e171328`. The teaching copy makes no scientific-code, protocol or result changes. New durable storage is explicitly requested through this PR, unlike the default disposable `/teach` artifact.
  - Standalone check: `python3 learning/check_cebra_time_transfer_teach.py` verifies 18 displayed metric cells against the committed result receipt, accessible inline-diagram IDs/captions, anchor integrity and no external resource dependencies. Requires Python standard library only; no fitting or private inputs.
  - Evidence fanout and independent lesson review are retained in canonical `outputs/cebra-time-teach-20260925/`; compact [QA/review receipt](cebra-time-transfer-teach-qa-20260925.json) is versioned. Historical 113-test/model-replay receipts belong to the original experiment, not a new run performed for this lesson.
  - Disposable preview `/tmp/pi-teach/20260925T134330Z-cebra-time-transfer-max.html` is a byte-identical copy. Its own loopback port 8766 server expires at **2026-09-25 23:54 SGT / 15:54 UTC**, task `be7695c35`; footer and host `~/AGENTS.md` record its operations. Earlier port 8765 was left untouched after an empty HTTP response. The preview is not a permanent service or backup; the Git-backed HTML remains available after expiry.

## Possible Later Files

Add these only when the action plan produces enough durable material:

- `glossary.md`: spike train, place cell, fixation, occupancy, rate map, tuning,
  decoding, and null model;
- `methods-map.md`: how raw neural/behavioral signals become aligned tables;
- `questions.md`: open questions to ask the professor or lab.
