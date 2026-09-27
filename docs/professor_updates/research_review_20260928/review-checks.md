# Review and verification record

**28 September2026 · presentation/software QA only.** No new biological model fits, raw-data extraction, checkpoint loading, display-projection fitting, package installation, or protocol selection.

## Independent review

1. Scientific/editorial review `d50ca2a2-5a40-45bb-ad64-120327fe4b83` found one medium wording issue: the joint diagram's “same prediction boundary” could imply shared decoder weights. Parent corrected it to **“Same readout policy; separately fitted decoder per arm”** and explicitly distinguished each arm's fitted decoder.
2. Fresh final delivery review `71cb46fe-0672-476f-9e69-fa90a4ecbd29` reported **no findings**. It checked the corrected text,9 selected saved atlas objects, omitted decoder-score leaderboard, correct retained training-PC energy rather than development-spectrum fractions, offline structure, and proposed-versus-completed scope. It did not perform the parent's browser tests or verify raw laboratory metadata.
3. Parent read the actual installed `offset1-model` implementation, experiment code, original reports and accepted machine summary. Exact architecture is195/29→32→32→16→8, GELU then unit-length output. Later standalone goal-LDA work exists; original baseline start/goal scores were pair marginals. The joint-training endpoint benchmark remains proposed, not executed.

Reviewer outputs are retained in `.pi-subagents/artifacts/outputs/{review-id}/` and copied into ignored `outputs/professor-review-20260928/agent-notes/`.

## Saved-evidence checks

- Nine curated atlas objects: Time250, Time1000 and PCA8, each seeds0/1/2.480 training and240 development whole-cue coordinates per object; identical to the previously saved, rounded atlas values. No new geometric fit.
- Exact source paths and SHA256 in `payload.json` and `loss-curves.json`.
- Three endpoint Time traces ×3,000 updates and six observed-world cue/joint traces ×1,000 updates. Headers, contiguous steps, temperature, selected configuration and observed-world identity checked. Charts use25-update block means; every raw step/value is embedded too.
- `self_check.py --sources` reproduces both JSON payloads and both SVGs byte-for-byte from the retained saved archives in a freshly removed temporary directory. Extraction is deterministic and stdlib-only.
- `render.py --check` verifies displayed joint means from the three seed rows, gain/rule arithmetic, traceable historical headline numbers, source paths, seven top-level sections, all anchors, no external asset dependencies, and deterministic output bytes.
- Software checks are not a new source-null analysis or a completion claim for the separately planned construction-validation methods artifact.

## Browser and delivery checks

Parent's headless Chrome/CDP script: `outputs/professor-review-20260928/check_browser.py` (local/ignored, reuses the already installed `websockets` runtime).

- Desktop1280px and mobile390px; eight captured views including both loss charts, architecture, viewer and joint result.
- No page overflow, including when details are expanded; deliberate internal diagram/table scrolling is allowed.
- All18 model×seed×color selections; two rendered canvases, six labeled colors, synchronized keyboard rotation and exact reset.
- Actual **Download HTML** click, real saved file, and reopening that file without a server: controls initialized once, both canvases redrawn, full loss data present, download button usable again.
- No page JavaScript errors or external HTTP(S) resource requests.
- Real Linux HTTP response byte-identical to `review.html`; actual cmux **surface:26 / workspace:3** showed seven sections, two drawn canvases, three model choices and an enabled download button. cmux DOM inspection used its isolated content world because CSP correctly disallowed page-world eval. No CSP weakening was needed. Mac-native save dialog behavior was not clicked automatically.

Retained receipts: `browser-validation.json`, `cmux-validation.json`, `preview.json` and `delivery-validation.json` under `outputs/professor-review-20260928/`. Browser profiles and test downloads were temporary and removed. Preview lifecycle/stop procedure is in [README](README.md) and the host registry.

## Static diagnostics and limits

Primary language-server checks confirmed no errors in the six edited Python/JS/shell implementation files; Node syntax and shell syntax checks passed. File-specific edit diagnostics were clean after fixes.

A broader lens scan retained stale cached worker-draft findings for two removed `innerHTML` assignments and a replaced boolean-identity check, marked pending even after current-file checks. These do not occur in the delivered source; parent checked the actual source and recorded dispositions rather than adding suppressions. The broad scanner also reported a project-level gitleaks timeout. **No clean project-wide security/dependency audit is claimed.** This small static report adds no authentication, external data fetching, telemetry or user-upload processing.

## Orchestration failures and recovery

The discovery researcher exceeded its initial18+2-turn budget; a resumed read-only response recovered existing findings. The isolated visualization worker also exceeded its45+3-turn budget after writing artifacts and checks. Neither failure was a scientific run failure. Parent read the returned code, corrected integration/security/labeling issues, completed verification directly, and obtained the fresh final review. Child completion claims alone were not accepted as final evidence.

Initial drafts lived only in ignored `work/professor-review-20260928/`. The canonical accepted deliverable is this folder. No scientific outputs were overwritten or mixed with unaccepted runs.

## Publication/preservation boundary

The requested PR contains only `docs/professor_updates/research_review_20260928/`; no raw tensors, checkpoints, unrelated test modifications, old untracked overview or its local index link are silently included. Initial hashes/copies in `outputs/professor-review-20260928/before.json` protect the pre-existing edits and earlier overview. No merge is authorized by creating the PR.

The finite preview is the only newly retained process, registered with a two-hour expiry. It exposes only a symlink to this HTML on loopback8768. No shared service was restarted or modified; the earlier8767 preview retains its own lifecycle.
