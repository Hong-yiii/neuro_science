# Professor-ready research review — 28 September 2026

Open **[review.html](review.html)** in a browser. The temporary cmux HTTP preview has expired; the saved HTML remains fully usable offline. The HTML has a **Download HTML** button and remains interactive after download without network access. GitHub's normal HTML file view displays source; download/open it locally for the rendered document.

Original [PR #13](https://github.com/Hong-yiii/neuro_science/pull/13), carried forward in the authorized follow-up · [Readable narrative](review.md) · [agreed temporal-validation plan](validation-plan.md) · [task scratchpad](SCRATCHPAD.md) · [review and verification](review-checks.md)

## What is included

Seven sections follow Hongyi's requested flow: raw recordings and pseudopopulations; CEBRA-Time/decoder and baseline architectures; pair/start/goal/component targets; sampling and training curves; joint cue/navigation handling and results; decoder comparisons; future steps. The architecture/construction figures redraw the user's whiteboard ideas without uploading the original image.

- Small viewer: Time250, Time1000, PCA8; all three computational seeds; start/goal coloring; shared train/development camera, pointer/keyboard rotation, zoom and reset.
- Nine saved **whole-cue** atlas projections, not newly computed embeddings or display fits. Each 80-feature whole cue is displayed in three saved training-fitted PCs. No decoder-score leaderboard is attached to this geometry menu.
- Two separate overlaid training-loss charts: endpoint Time and observed-world cue/joint Time. 25-update block averages; full step/value series embedded in the HTML and retained in `loss-curves.json`.
- **49 additional empirical figure panels**, with dense matrices inside expandable sections: real-source start/goal/pair and session-support distributions; real-source versus synthetic component balance; endpoint performance and pair/start/goal count/row-normalized confusions; cue-bin LDA curves and within-cue goal generalization; joint-study seed-level performance and all binary confusions.
- Completed studies and agreed/proposed future work remain distinct. Navigation-time decoding and joint-model temporal/cross-phase transfer are **planned, not executed**. The historical within-cue matrix is raw-feature LDA, not CEBRA. No new biological fits, raw recording extraction, checkpoint loads or null experiments; detailed run settings remain open.

The central caveats are visible: known-condition cross-session assembly, historical-source exposure/reuse, incomplete absolute joint-Time success, no confirmed H1a/H1b, and no implied common biological geometry. CEBRA-Behavior is not a new-work arm. H2 remains removed.

## Rebuild and checks

From the repository root, using the already installed project runtime:

```sh
D=docs/professor_updates/research_review_20260928
PYTHONDONTWRITEBYTECODE=1 PYTHONNOUSERSITE=1 \
  scratch/v6-v9-runtime/bin/python "$D/render.py"
PYTHONDONTWRITEBYTECODE=1 PYTHONNOUSERSITE=1 \
  scratch/v6-v9-runtime/bin/python "$D/render.py" --check
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 "$D/self_check.py"
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 "$D/evidence.py" --check
```

`render.py` uses the existing `markdown_it` installation and otherwise stdlib/local helpers. It checks headline metrics against their saved summaries, the four-part success rule, source paths, seven landmarks, unique anchors, self-contained resources and deterministic HTML bytes. `self_check.py` checks the curated selection, counts/finiteness, preserved trace lengths, offline widget structure and JavaScript syntax (`node --check`). Neither command imports an ML runtime.

For a host with the original ignored saved outputs, this optional **no-fit source replay** regenerates only presentation artifacts inside a disposable directory and requires every output byte to match:

```sh
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 "$D/self_check.py" --sources
```

The additional `evidence.json` contains aggregate counts, confusion matrices,
per-seed metrics, cue curves and temporal matrices with source hashes. `evidence.py`
recomputes endpoint confusion/accuracy and joint balanced accuracy/log loss/AUROC
from saved predictions, reconciles source ledgers, and checks temporal diagonals.
Rendering/checking tracked aggregates requires only stdlib; optional extraction
uses the **already installed NumPy**, never a model runtime:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONNOUSERSITE=1 \
  scratch/v6-v9-runtime/bin/python "$D/evidence.py" --sources
# Deliberate aggregate regeneration only:
PYTHONDONTWRITEBYTECODE=1 PYTHONNOUSERSITE=1 \
  scratch/v6-v9-runtime/bin/python "$D/evidence.py" --extract
```

For the derived source NPZ, only four identity/split/label ZIP members are read
and hashed individually (`archive.npz#member.npy` keys). Neural tensor members
are not read by the final extractor. No raw source tensors or individual trial
IDs are placed in the new aggregate. Hashes verify computational provenance, not
acquisition semantics or biological independence.

To deliberately re-extract the original viewer/loss assets after a reviewed source change:

```sh
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 "$D/extract.py" --root "$PWD" --out "$D"
```

This reads only the tracked saved atlas and historical loss/config files listed in the payload provenance. Do not substitute a null world for `worlds/00_observed`. Re-extraction is not training. No dependency installation is needed on this host. A clean clone without ignored outputs can render/check the tracked payloads, but cannot perform `--sources` replay until the saved archives are available.

Original browser QA is retained in ignored `outputs/professor-review-20260928/`; follow-up scripts/receipts/screenshots are in `outputs/professor-review-followup-20260928/`; see `review-checks.md`. No raw source tensors, spikes, model checkpoints or browser profiles are committed. `payload.json` contains already-published-to-this-private-repository derived display coordinates; keep this delivery private too.

## Temporary preview operations

**Ended normally on 28 September 2026 at 03:42:55 SGT** (27 September 19:42:55 UTC), after its two-hour lifetime. Pi task **`b7a0c11bd`** exited0; follow-up at03:43 SGT verified no8768 listener and `/tmp/professor-review-http-czVcky` absent. Its receipt is marked ended. No old PID was signaled or service restarted. The report/PR and loaded/downloaded copies remain available. The details below document the historical launch and deliberate future restart procedure.

- Former URL (now offline): **<http://localhost:8768/research-review.html>** inside the homelab-connected cmux workspace. Opened and DOM-verified in **workspace:3 / surface:26**.
- Exposure: Linux loopback `127.0.0.1:8768`, existing cmux SSH routing only. Not a public URL or an ordinary Mac-local listener.
- Launcher: this folder's `preview.sh`; `/usr/bin/timeout --foreground 7200` and absolute `/usr/bin/python3 -u -m http.server`.
- Serving directory: `/tmp/professor-review-http-czVcky`, containing only the report symlink. The repository, data and credentials are not served.
- State: `outputs/professor-review-20260928/preview.json`; log `.pi/tasks/session-1388750-1388750/b7a0c11bd.output`.
- Health: GET the URL on Linux and compare bytes with `review.html`; verify both canvases and the enabled download control in the actual cmux DOM. Headless Chrome separately tested the actual download and reopening; Mac-native file saving was not clicked automatically.
- Historical stop method: Pi `bg_kill` for the then-active task. This task is now complete; do not stop it again or signal its former PID1924500. For a deliberate new launch, verify that new wrapper's current owner/command before signaling. **Never signal a historical PID after expiry.** Closing the browser does not stop the server.
- Timeout/normal stop removes only its serving symlink/directory and marks its receipt ended. The HTML, sources and QA remain. Already loaded/downloaded pages still work after expiry.
- Deliberate restart: check port 8768 is unused, run `bash "$D/preview.sh"` through the session's background-task supervisor, and record the fresh task/directory/expiry here and in `~/AGENTS.md`. Do not auto-restart from this historical entry.
- No boot unit, auto-restart, public ingress, shared-service downtime, raw-data transfer, new private-state backup need or scientific computation. Dependencies are Python stdlib and existing SSH/cmux for viewing. Restore/rebuild the report from Git-backed sources; stop only this owned preview to roll back runtime exposure.

The earlier overview on 8767 and its lifecycle are separate and were not replaced or stopped. Host registration is in `/home/hongyi-home-lab/AGENTS.md`.
