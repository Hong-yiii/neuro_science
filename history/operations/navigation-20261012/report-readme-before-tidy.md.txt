# Collaborative retrospective manuscript

**October12 reorganization:** this is now the top-level report package.
[Weekly reading history](../history/README.md) owns past deliveries; the future
notebook will be one companion to this report. Detailed notebook targets remain open.
The current frozen file has a **pre-existing local byte difference** from the
committed milestone described below. Migration preserved it, not repaired it;
`test_build.py` still reports that integrity failure. Both original versions are
preserved locally under `work/reorganization-weekly-audit/before-build/`.
See [migration status](../docs/reorganization.md).

Created October 12, 2026. **Current reading version: revision 03, `manuscript.html`.**
It is an expanded **CEBRA-Time-focused** paper-style draft with methods, results,
literature references, existing empirical figures and visual construction/feature
shapes. Cue-only/joint Time models and raw/PCA/LDA references remain; Behavior
comparisons and their mixed-model figures have been removed from this manuscript.
Original reports remain unchanged as historical provenance.
It is **not** a finished manuscript: the feedback status below lists outstanding
work. Scientific analyses that were never performed remain explicitly unavailable.

**The old `outline.html` copy is frozen revision 02.** An `scp` command naming
that file still downloads the old abbreviated draft, not current manuscript edits.
Use the current Mac command below; its timestamped destination avoids reusing an
old browser URL. Revision 01 is retained under the ignored
`outputs/cebra-retrospective-20261012/revision-01/` directory.

This manuscript complements the
[October 11 evidence blueprint](../docs/reports/cebra-research-synthesis-20261011.md); it does
not replace that audit or adopt the separate future-research proposals.

## Frozen whole-file reading milestone — October 12

At Hongyi's request, the current report is retained as one self-contained file
before the proposed repository spring cleaning:

[`retrospective-frozen-20261012.html`](retrospective-frozen-20261012.html)

This exact reading milestone is included in the PR, not just ignored outputs.
From GitHub, download the raw file and open it locally; GitHub's HTML source view
is not a rendered preview. A fresh clone can open it without Python, private
artifacts, scientific dependencies or a server.

The committed milestone was a byte-identical copy of the verified portable manuscript: 2,670,108 bytes,
14 embedded PNGs and five inline SVGs, no scripts or server requirement. SHA-256:
`86497662096908f5fa92f1d00747377b2046e07a37ea225ae8fdbedcc9dfbde6`.
The original local `outputs/cebra-retrospective-20261012/retrospective-frozen-20261012.receipt.json`
records provenance and the existing browser checks for identical bytes; that
receipt and screenshots remain local, not PR deliverables. `test_build.py` checks
the versioned reading copy against the exact SHA-256 above. Preserve this export; later
edits/builds continue to use `manuscript.html`, never overwrite the frozen copy.
Optional evidence links still require repository access.

“Frozen” is a reading/version milestone, not a declaration of scientific or
editorial completion. Pending feedback below remains recorded. The original
export stays protected in ignored outputs; the identical versioned copy makes
this report portable through Git, not a backup of the private scientific artifacts.
The [original reorganization proposal](../docs/repo-reorganization-plan-20261012.md)
records the earlier filing pass. The [current migration record](../docs/reorganization.md)
distinguishes newly moved reading files/shared code from retained frozen evidence.

## Reader feedback and next revision

[Hongyi's October 12 feedback](feedback-20261012.md) preserves the original
comments and a pending section-by-section checklist: defer shuffle/loss
presentation, explain pair/start/goal sampling and balance, visualize feature
shapes, and introduce training/validation diagnostics before scientific results.
The flagged Figure 5 screenshot is retained in the ignored output directory;
its path and hash are recorded in that note.

[manuscript.html](manuscript.html#sampling) is the separately expanded revision 03
source. Its §2.2 now explains recorded neurons/trials → split → sampling →
synthetic examples, with session-block and four-target branching diagrams,
class balance, per-seed counts and actual source reuse. The queued messages are
now consolidated into this explanation. Following the visual-first preference,
construction diagrams lead §2.2; §2.3 uses a matrix-to-feature diagram (Figure 2C)
in place of the long shape explanation, with exact matrix counts in Table 1c.
§3.2 now opens with all eight latest whole-cue path-component scores (Table 3),
followed by per-seed cue/joint confusion matrices and a class-recall/BA diagram
(Figure 5). Earlier readout contrasts remain separate in Table 4. Full ordered
route prediction was never evaluated; the binary component is not a substitute.
Prefer informative diagrams/plots over repetitive prose; never present schematics
as empirical results. This is **partial** feedback application: shuffle/loss
removal, the dedicated training section and separate real-source start/goal plots
remain pending. The revision 02 reading copy remains unchanged; do not describe revision 03 as fully
reviewed or as delivered to the Mac browser.

## Next work: report first, then notebook

Hongyi's next sequence is **sharpen the report → create an easily interpretable,
high-observability Jupyter notebook**. This PR preserves the reading milestone
and handoff; it does not claim the report revisions or notebook are complete.

1. Finish the [feedback ledger](feedback-20261012.md): defer shuffle/loss detail,
   separate training/validation from scientific results, add real-source
   start/goal marginal views where saved aggregates support them, and define
   exactly which observations “within-bin variability” refers to. Preserve
   historical selection criteria and explicitly label unavailable diagnostics.
2. The repository discussion now specifies one companion notebook. Before
   implementation, freeze its target/cohort, input availability and intended
   reader; do not silently select pair decoding or another scientific question.
3. Proposed minimal first notebook: explain and reproduce approved report views
   from tracked aggregates, using narrative cells, visible input provenance,
   shape/count/split assertions, labeled figures, baselines and interpretation
   immediately beside each result. Reuse existing helpers rather than fork
   pipeline logic. Identify unavailable private inputs instead of fabricating them.
4. Require restart-and-run-all in a documented environment, deterministic outputs
   and no hidden cell-order state. Do not package private data, credentials,
   predictions or checkpoints in notebook outputs. Separate any later authorized
   fitting/replay workflow from the reader-facing notebook.

Here notebook observability means inspectable computation, not proof of formal
neural-state observability. New fits, raw access, downloads or saved-model reanalysis
still require a separately approved scope. Notebook dependencies, detailed scope
and execution validation remain future work—not an installation/run queue.

## Edit and build

Edit [manuscript.html](manuscript.html) for the next revision, preserving the
revision 02 source [outline.html](outline.html). From the repository root:

```sh
/usr/bin/python3 report/test_build.py
/usr/bin/python3 report/test_path_summary.py
/usr/bin/python3 report/build.py
```

This writes `outputs/cebra-retrospective-20261012/manuscript.html` separately.
The no-argument command now builds the current manuscript. Pass `outline.html`
explicitly only to build revision 02. The two HTML sources retain historical
relative evidence URLs: the builder resolves them against their original virtual
base and keeps citations pinned to `4862267`, even when evidence has moved through
a compatibility symlink. Treat them as build templates, not portable reading files;
open the standalone output or frozen milestone for offline reading.

The standard-library-only builder checks local navigation, unique IDs, image
alternative text and the existence of every evidence path in accepted revision
`4862267`. It embeds unchanged PNG bytes into the selected output filename:
`manuscript.html` for revision 03, or `outline.html` for revision 02, both under
`outputs/cebra-retrospective-20261012/`.

These ignored outputs are **portable reading copies**; all figures work offline.
Optional source links point to the private repository at that revision, require
appropriate access, and show GitHub's source view rather than rendered HTML.
Only presentation arithmetic on archived aggregate counts is used for the new
path-error diagrams; no private raw data/predictions, saved models, new scientific
evaluation or fits are needed. No JavaScript, build dependencies, server, public hosting or persistent
worker is introduced. Re-run the builder after each agreed HTML edit.

## Mac / right-pane delivery

The current remote cmux relay rejected `browser.open_split` and explicitly
restricted `surface.split` to terminal surfaces. No browser was opened, and no
permissions, client, daemon or service configuration was changed to bypass this.
A fresh local Mac action is needed to open the reading copy in the right browser.
Use the same file-copy transport, but copy **`manuscript.html`, not `outline.html`**.
Run this in a **local Mac cmux terminal, not inside the homelab SSH shell**:

```sh
file="$HOME/Downloads/cebra-retrospective-r03-$(date +%Y%m%d-%H%M%S).html"
scp homelab:/home/hongyi-home-lab/neuro_science/outputs/cebra-retrospective-20261012/manuscript.html "$file" &&
  cmux browser open "file://$file"
```

The timestamp gives each download a new local filename and browser URL. The page
should identify itself as **working draft 03**, with **CEBRA-Time** in the title,
construction diagrams at the start of §2.2 and the feature-matrix diagram in §2.3. Existing old tabs will
not automatically switch to the new file. If browser opening fails, the successful
`scp` still leaves the HTML in Downloads; open that exact file locally.

No HTTP server or new transport is needed. These are instructions for local Mac
execution, not a claim that this Linux agent has opened or verified the Mac pane.
Incomplete feedback items may still appear in revision 03; see the status above.

### Delegated `/teach` delivery attempt and incident — October 12

Worker run `a490b0a2` read the installed
`~/.agents/skills/teach/SKILL.md` (also linked from `~/.claude/skills/teach/`)
and `~/pi_harness_setup/skills/teach/SKILL.md`. Their remote loopback-HTTP →
`cmux browser open` route still returned `remote_relay_denied` for
`browser.open_split`; browser inspection was also denied. **The report was not
opened.** No preview server or permission/configuration change was made.

**Unintended action:** at 03:28 SGT the worker probed commands without arguments
and executed bare `cmux close-surface`, closing pre-existing surface
`E8D7895A-C2A3-44F0-B420-659D9690D128` (reported as `surface:27`) in workspace
`4AA2D51D-4A78-42F6-9544-E69C1D066D14`. The parent independently checked the
recorded close response. Do not treat destructive/mutating commands without
arguments as help probes. The closed terminal's process/recovery impact is
unverified; no restoration was attempted.

The worker subsequently created a separate temporary helper terminal
`0D2FA854-DDEA-4DC9-A7E7-D5EF5B3B8186`, then explicitly closed that helper;
a follow-up access check rejected the removed surface. Read-only parent checks
at 03:31 SGT showed the workspace connected with one active terminal session,
versus two before the attempt. Further pane operations were stopped. The child
hit its turn budget; retain its partial result as a blocked attempt, not a
successful delivery. Its transcript is in the local Pi/subagent session history.
Existing HTML and the unrelated pre-existing port-8765 server were untouched.
Any recovery/opening now requires deliberate authorized local Mac control, not
more remote command guessing.

## Checks and retained local artifacts

- Passed: build-time link/image checks; primary Python/HTML diagnostics;
  `git diff --check`. Negative checks reject missing anchors, duplicate IDs,
  missing images and external asset URLs.
- Revision 03 sampling update: builder regression checks, pinned paths, count
  arithmetic and revision-02 preservation hashes passed. Offline Chrome checks
  at 860px/390px loaded all 20 images, found no broken anchors, page overflow,
  clipped construction-diagram labels, page errors or external requests.
  Construction diagram and mobile section opening were visually inspected.
  Hash-bound receipt/screenshots:
  `outputs/cebra-retrospective-20261012/revision-03/sampling-check/`.
  This checks presentation, not independent scientific review or completed
  application of all feedback. No Mac browser delivery was performed.
- Revision 03 four-target follow-up: Figure 2B explicitly separates the shared
  pair/start/goal construction from the binary-component construction. Rebuild,
  desktop/mobile browser checks, four-branch labels, unclipped SVG text and
  revision-02 preservation hashes passed; desktop diagram visually inspected.
  Hash-bound receipt/screenshots:
  `outputs/cebra-retrospective-20261012/revision-03/target-branches-check/`.
- Revision 03 queued-message consolidation: §2.2 now begins with the complete
  flow and four-target/two-construction distinction; §2.3 supplies the decoder
  feature-view bridge and Table 1c. Builder regressions, all four shape rows,
  both diagrams, offline desktop/mobile rendering and revision-02 preservation
  hashes passed. Desktop overview and mobile shape table visually inspected.
  Hash-bound receipt/screenshots:
  `outputs/cebra-retrospective-20261012/revision-03/queued-message-check/`.
- Revision 03 visual-first update: construction diagrams now precede the count
  tables; Figure 2C illustrates neuron/time matrices and the four feature views
  in place of repetitive prose. All three SVGs, 20 existing images, four matrix
  rows, anchors and preserved revision-02 hashes passed desktop/mobile checks.
  Grid alignment and single-row feature strips were corrected during visual QA;
  desktop and both horizontally scrollable mobile views were inspected. The
  diagrams are explicitly schematic, not new neural-data figures.
  Hash-bound receipt/screenshots:
  `outputs/cebra-retrospective-20261012/revision-03/visual-first-check/`.
- Current-delivery refresh: rebuilt `manuscript.html` and verified exact equality
  with packaging the current source. Draft-03 title, all 20 images, three diagrams,
  desktop/mobile rendering and preserved revision-02 output passed. Updated the
  Mac command to use the correct source and a timestamped local filename; no Mac
  action was executed. That delivery's hash and checks:
  `outputs/cebra-retrospective-20261012/revision-03/delivery-check/receipt.json`.
- CEBRA-Time-only scope update: edited the same manuscript and portable filename.
  Removed six mixed-objective images and Behavior-derived prose/ablations;
  retained 14 original images and renumbered main figures 1–7. Read-only evidence
  audit `dcc7251f` and independent manuscript review `419a7444` found no residual
  model-scope or numerical blockers. Build tests, image-source allowlist,
  no-excluded-model checks, anchors, desktop/mobile rendering and preserved
  revision-02 hash passed; Time readout/geometry sections visually inspected.
  Review concerned the current text/sources, not the full deletion history or
  Mac delivery. That update's hash-bound receipt/screenshots:
  `outputs/cebra-retrospective-20261012/revision-03/time-only-check/`.
- Path-error explanation: Table 3 reports all eight latest whole-cue scores;
  Figure 5 adds six empirical confusion panels and a mean-recall/BA diagram,
  distinguishing a constant-reference rule from fitted results. The new
  `test_path_summary.py` verifies counts, percentages, means and bar lengths
  against tracked aggregates. Independent read-only review `3f6876df` found
  no numerical/claim-scope findings. Build tests and source/output equality
  passed; both revision-02 hashes are preserved. Offline 860px/390px checks
  load all 14 PNGs/five SVGs with no broken anchors, overflow, clipped text,
  header collisions, page errors or external requests. Visual QA shortened
  tightly spaced column headings; desktop and mobile panels were inspected.
  Initial QA and final hash-bound screenshots/receipt are retained under:
  `outputs/cebra-retrospective-20261012/revision-03/path-failure-check/`
  (latest: `final/receipt.json`). No scientific fits, private prediction
  access, model replay or Mac delivery. Other feedback remains pending.
- Revision 02: seven manuscript sections and five visible numbered figures;
  build/link checks and desktop/mobile browser checks. All embedded image bytes
  match the existing source PNGs. Current screenshots and hash-bound receipt:
  `outputs/cebra-retrospective-20261012/revision-02/`. No cmux operations or new
  server were attempted for this editorial revision.
- Revision 01 passed at 860px and 390px: nine sections, all six image elements loaded
  (five distinct figures), contents navigation and disclosure toggling, no page
  overflow even with disclosures open, no page errors or external requests.
  Visual inspection confirmed the opening and endpoint section; the receipt is
  `outputs/cebra-retrospective-20261012/render-check.json`.
- `outputs/cebra-retrospective-20261012/` retains generated HTML and browser-QA
  screenshots/receipts, not scientific analysis output. The user-requested frozen
  reading export above is protected. Other presentation artifacts are candidates
  for a separately approved retention pass, not blanket deletion. Temporary browser profiles are removed at process exit.
- Browser checks use existing Chrome and an already installed Playwright-core;
  neither is installed or modified by this task. No scientific runtime is used.
- The initial Chrome CLI screenshot of a fragment was blank despite a zero exit
  code. The follow-up interaction check navigates by clicking the actual contents
  link and verifies images, disclosures and page width; use its receipt rather
  than the initial command's exit status as presentation evidence.

Next: apply the remaining feedback in the linked ledger, particularly removal
of shuffle/loss presentation and the dedicated training/validation section.
Do not present this expanded draft as a finished paper or run missing scientific
analyses merely to fill gaps.
