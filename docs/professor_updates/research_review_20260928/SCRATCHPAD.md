# Professor-ready review — recoverable task record

## Request (28 September 2026, Singapore)

Hongyi requests one professor-ready self-contained HTML and a PR, reorganizing completed research in this order:

1. Raw data → pseudopopulation construction.
2. CEBRA-Time architecture: representation training plus downstream decoder; baseline architectures; use diagrams inspired by `/tmp/cmux-drop-70af6b13-d6df-4e6f-a0f4-4e93f131572c.png`.
3. Evaluation targets: start–goal pair, start, goal, graph-component existence (four outputs, grouped into endpoint and path questions; clarify the user's “3” without dropping a target).
4. Model training, overlaid saved loss curves, short sampling pseudocode, minimal fold detail, and a small curated interactive latent viewer rather than the full atlas menu.
5. Joint cue/navigation training: variable durations/data volume/sampling handling and completed evaluation.
6. Decoder ablation evaluation.
7. Future steps.
Include a download button, use diagrams not overwhelming tables, run necessary checks, open a PR. Maintain scratchpad across compaction; use subagents and keep messy work in isolated scratch/artifact locations.

## Scope / scientific boundary

This is a synthesis/presentation task with saved-artifact extraction and software/browser tests. No new biological fits, raw extraction, new-data access, architecture sweeps or silent protocol choices. Existing studies remain exploratory. Joint cue/navigation endpoint prediction is proposed, not completed. Drop Behavior from focal model menu/new work; historical ablation can be noted only when necessary, not reintroduced as a proposed arm. H1a/H1b remain; H2 removed. Phase rotation not established. Saved display plots do not establish H1b. Training objective and prediction metrics must remain distinct.

The latest conversational proposal separates decoder selection (inner sources, both encoder arms/checkpoints, freeze policy) from a later paired joint-training evaluation. Endpoint pair/start/goal proposal is not a frozen protocol or executed result. Do not claim an “optimal decoder.”

## Initial state and preservation

- Canonical root `/home/hongyi-home-lab/neuro_science`, main at `fac639b`, matching cached origin/main.
- Existing changes: docs/reports/README.md (previous overview link); scripts/test_cebra_latent_atlas.py (pre-existing unrelated user work); untracked docs/reports/current-state-20260927/ (earlier overview and notes).
- Preserve all of these. New PR should not silently stage unrelated atlas test edits or old untracked report references without their targets.
- Earlier overview scratchpad: docs/reports/current-state-20260927/scratchpad.md.
- Earlier preview b0cea7f53 on127.0.0.1:8767 expires02:17:08 SGT. Owned serving directory /tmp/current-state-http-M0w6L2; keep its cleanup/status accounting separate from this delivery.
- Whiteboard read directly. Main ideas: raw → baseline; neural encoder → latent → chosen decoder; train cue/navigation then reuse encoder on cue; distinguish lower loss from better task readout. Correct “well trained”/“no class info” shorthand rather than reproduce it as fact.

## Plan / branch ownership

- Parent: source authority, report narrative/diagrams, sole canonical writer, numerical reconciliation, QA, safe branch/PR publication and private preview.
- Read-only scout: map reusable atlas/viewer and saved curve artifacts, propose smallest curated subset.
- Read-only researcher: audit task/metric/architecture/pseudocode claims and endpoint/decoder numeric story.
- Isolated worker (only if helpful after discovery): extract curated presentation payload from saved outputs and implement/check bounded visualization in an isolated task directory; no writes to canonical scientific assets.
- Final fresh read-only reviewer: scientific/presentation claims and publication contents.

## Planned artifacts

- Durable deliverable folder: docs/professor_updates/research_review_20260928/.
- Main task record: this SCRATCHPAD.md.
- Branch notes: research_review_20260928/notes/ (runtime outputs copied by parent).
- HTML and readable narrative/source, small presentation payload/provenance, renderer/check as needed; reuse existing assets/helpers, no new dependencies.
- Bulky QA/screenshots/logs: outputs/professor-review-20260928/ (ignored).
- Isolated disposable construction: work/professor-review-20260928/ (ignored).
- PR branch: `docs/professor-review-20260928`, based on refreshed `origin/main` at `fac639b016ca2dd435eed689f9d5544d7c636e96`. Repository confirmed private. URL pending; no merge authorized.

## Acceptance checklist

- User's seven-section flow, concise orientation, visible claim limits and future/completed separation.
- Raw, masked source and synthetic tensors clearly differentiated; same-session≠proven simultaneous.
- Explicit encoder architecture plus decoder and raw/PCA/LDA roles; no PCA-before-CEBRA invention.
- Four outputs grouped clearly; separate direct heads versus marginals; no endpoint H1 claim.
- Real saved training curves with exact run/settings/seeds and comparable objective caveats; not fabricated curves or validation loss mislabeled training loss.
- Curated interactive latent plots, all retained seeds accessible, projection and reuse limits, no cloud-as-biological-path interpretation.
- Native navigation bins, normalized-progress pair bank, fixed update/phase weighting and cue-only evaluation explained.
- Decoder evidence does not assume logistic bottleneck; no cherry-picked or cross-study leaderboard.
- Self-contained HTML, keyboard/mobile usability, working download button, no remote assets/scripts; link/numerical tests and browser checks.
- Independent review, scoped commits only, PR on existing private repository, no raw/checkpoint upload, no merge.
- Dedicated finite loopback preview, registered lifecycle, actual cmux verification, offline fallback.

## Progress — 01:26 SGT

- Original local changes and earlier overview files hashed in `outputs/professor-review-20260928/before.json`; initial dirty tracked copies retained alongside. Branch created without stashing/altering prior work.
- Read-only discovery run `e5e6c525`: scout completed; researcher exceeded its18+2-turn allowance and failed. Resumed researcher as `fce5449f`, returned existing findings without more inspection. No scientific computation performed. Original agent artifacts remain under `.pi-subagents/artifacts/outputs/e5e6c525-6e54-47ef-8585-ff5984675a89/`; do not mistake recommendations/partial curve discovery for completed verification.
- Parent confirmed actual installed offset1 architecture195/29→32→32→16→8 with GELU and normalization; reread authoritative source reports and summary. Later separate-goal LDA exists, although original baseline endpoint scores were pair marginals.
- Parent drafted `review.md`, `diagrams.py`, `review.css`, `render.py`. Seven requested sections, four outputs grouped by endpoint versus component question, source-backed results, clear proposed next steps. Renderer reuses existing MarkdownIt; no new dependency.
- Isolated worker `09f2f0b2` owns only `work/professor-review-20260928/`. Extracts9 saved whole-cue atlas objects (Time250/1000 and PCA, all3seeds), two sets of actual Time training traces (observed world only), and lightweight Canvas/SVG widgets. No new projections, checkpoint loads or fits.
- Independent read-only scientific reviewer `d50ca2a2` is checking narrative and diagrams while UI is assembled. Parent handles deterministic, numerical, offline and real-browser checks, then final artifact review.
- Current old overview preview remains live on8767. New preview, if started, will use a separate checked port8768 with a finite lifetime and registry/runbook entry; never replace another listener.

## Release state — 01:54 SGT

- Worker exhausted its turn allowance after producing files; parent did not accept wrapper completion status as evidence. Read and integrated its saved outputs, made DOM construction injection-safe, corrected the retained-energy display, kept only9 saved whole-cue objects and all observed loss traces, and ran checks directly. Re-extraction is deterministic; no new projections/fits.
- Science reviewer found one ambiguous label, corrected to “Same readout policy; separately fitted decoder per arm.” Fresh final reviewer `71cb46fe` found no issues within its static/content scope. Original review outputs retained under ignored `outputs/professor-review-20260928/agent-notes/`.
- Final validation task `bd1c89885` exited0: source replay exact for four data/SVG artifacts, widget self-check/Node syntax, numerical/render checks, eight browser views,18 selections, synchronized keyboard rotation/reset, actual download+offline reopen, zero external resource requests, HTTP byte comparison and shell syntax. Primary LSP6-file check found no errors. Lens retained stale draft auxiliary findings; see review-checks.md rather than claiming a clean whole-project scan.
- Final HTML:710,051bytes, SHA256 `820a82b0fc220389e4b67c9a79f6145073380dd1136cc3ed238fa5986493d222`. Fourteen pre-existing file hashes still match, including the unrelated modified atlas test and the entire earlier overview. Nothing outside this deliverable folder should enter the PR.
- New finite preview task `b7a0c11bd`:127.0.0.1:8768, dedicated `/tmp/professor-review-http-czVcky`, started01:42:55 SGT; expires03:42:55 SGT. Registered in host AGENTS and this folder's README. Actual cmux DOM verified in surface:26/workspace:3; CSP retained. Old8767 preview untouched.
- Isolated worker source/generated drafts and its bytecode were removed after integration. Its `.pi` task logs and `.pi-subagents` execution transcripts/metadata remain under `work/professor-review-20260928/` as explicitly retained provenance; no worker process remains. Browser temporary profiles/downloads removed; QA screenshots/receipts and before-hashes retained under outputs.
- Publication: stage only `docs/professor_updates/research_review_20260928/`, commit and create the requested PR to main. Record URL/head in local delivery receipt and the publication note below; no merge.

## Publication

[PR #13](https://github.com/Hong-yiii/neuro_science/pull/13) opened against `main` from `docs/professor-review-20260928`; initial content commit `bc740d8`, followed by this publication-link update. Scope:18 presentation/source files in this folder only. No merge. Remote head and final preservation checks are recorded in `outputs/professor-review-20260928/delivery-validation.json`.

Original work is delivered; there is no new biological run queue. At the preview's03:42:55 SGT expiry, verify task completion, missing8768 listener and removed owned serving directory, then mark its lifecycle ended in README/host registry without signaling an old PID. The earlier8767 preview has an independent02:17 SGT expiry and runbook. Both previews subsequently expired normally; missing listeners/directories and retained HTML were verified, and runbooks/host registry marked ended.

## Follow-up — 28 September, authorized new PR and merge

Hongyi agreed to substantially more empirical figures, unique real-source class
support (start, goal, pair and path/component), decoding throughout cue and
navigation, and frozen temporal/cross-phase readout validation. Accepted order:
source support → saved-result visualization → bounded prefit protocol. Improved
cue decoding is primary; cross-phase transfer is supporting evidence, not proof
of identical biological geometry. No silent choice of unresolved fit settings.

Parent is sole writer. Read-only scouts map saved source/metric/prediction files.
`validation-plan.md` records the agreement and remaining fit gates. Canonical
AGENTS/direction/contract/task list are updated so the requirement survives this
chat. Publication branch `docs/visual-evidence-validation-20260928` descends from
PR#13 head7e9b1a1; new PR to main will carry that review forward without merging
PR13 separately. Preserve unrelated changes in reports index, atlas test and
untracked earlier overview. Baseline hashes/copies in ignored
`outputs/professor-review-followup-20260928/before.json` and `before/`.
Existing automatic formatting inside this report folder is retained, not reverted.
No persistent preview is requested or started. Software/presentation checks and
independent scientific review precede publication and the authorized merge.

Follow-up results:49 empirical panels added from saved artifacts, including
historical plain-LDA cue curves and within-cue goal generalization. Navigation-time
and joint-model cross-phase decoding remain planned. Reviewer9592e99d flagged
whole-derived-archive hashing; corrected to four metadata-only ZIP-member reads
and hashes. Focused follow-up6c7cfdbf found no remaining issue in that correction.
Final metadata-only replay, direct Pyright, deterministic rendering and20 Chrome
views/download/reopen passed in taskbb3a19f7e. A subsequent small CLI/error-test
cleanup preserves extraction semantics and is rechecked before publication.
All14 unrelated baseline file hashes still match. No scientific fits, new
persistent preview, installations or unrelated file staging. Keep local QA and
before-copies as recovery evidence; temporary browser profiles were removed.
