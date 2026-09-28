# Review and verification record

**28 September2026 · exploratory saved-output aggregation and presentation/software QA.** No new biological model fits, raw recording extraction, checkpoint loading, display-projection fitting or package installation. Detailed fit settings remain open.

## September28 visual-evidence follow-up

User approved source support → saved plots → bounded prefit protocol, plus a **new
PR and merge** carrying forward #13. The historical no-merge boundary below applies
to the original delivery, not this later authorization. Current scope adds
`evidence.py`, aggregate `evidence.json`, `validation-plan.md`, the expanded offline
review and canonical reporting/direction/contract/task guidance.

- 49 additional empirical figure panels (dense confusions/seed matrices collapsible).
  Counts and row-normalized confusions are both retained; source cohorts, weights,
  historical exposure and dependence are labelled. Start/goal endpoint-follow-up
  scores are components of the argmax pair—not summed probability marginals.

- Saved source ledger and session-pair support reconcile to15,553 unique sources;
  component metadata reconcile to82/22. Source counts and pseudorows are separate.
- All nine endpoint confusion/accuracy sets and six joint seed/arm BA, AUROC and
  balanced losses are reconstructed from predictions. The three historical
  cue→cue goal matrices have diagonals matching direct-goal cue-bin LDA curves.
- Navigation-time and joint-CEBRA time/phase transfer remain explicitly unmeasured.
  The existing within-cue matrix is plain LDA on raw195-unit bins, not CEBRA.
- Parent's initial source-replay check caught integer histogram keys becoming
  JSON strings; extraction now emits string keys directly and equality replay passes.
- Independent focused reviewer `9592e99d` identified a medium scope issue: hashing
  the complete derived NPZ read neural tensor bytes for provenance. Final extraction
  reads/hashes only four named identity/split/label ZIP members, never the tensor
  member or whole archive; a regression check forbids whole-archive provenance.
  Earlier whole-file hashing was not fitting or raw recording extraction, and no
  neural tensor values were interpreted, modified or committed. Focused follow-up
  reviewer6c7cfdbf verified the correction and found no remaining findings within
  that scope; it did not claim to rerun the parent's tests or broadly re-review.
- Direct Pyright checks reported0 errors/warnings; render/source-replay checks and
  20 desktop/mobile Chrome views passed, including49 figures, all18 viewer
  selections, keyboard rotation/reset and actual offline HTML download/reopening.
  No page errors or external HTTP(S) resource requests. Source/temporal/confusion
  screenshots were inspected; intentional horizontal figure scrolling is retained
  on narrow screens. Original interactive viewer remains intact.
- Narrow lens diagnostics misidentified tuples inside comparisons/iteration as
  truthy-tuple asserts and CLI-handled parse errors as unhandled. These were
  documented as false positives, not hidden with source suppression. Assertion
  checks are for an offline verification tool whose CLI rejects Python `-O`.
  The final small cleanup also checks the expected rejection message, uses list
  iterables for those guards and handles CLI parsing inside main. A later broad
  scan retained obsolete original widget/extractor flags, had unconfirmed Python
  LSP probes and a gitleaks timeout; direct Pyright and actual checks are the
  recorded code evidence. No whole-project security/dependency audit is claimed.

Follow-up QA/logs/before-hashes: ignored `outputs/professor-review-followup-20260928/`.
Browser profiles/downloads are removed automatically; no HTTP preview or other
persistent process is started. Discovery workers exhausted turn budgets; resumed
read-only responses returned their existing findings, verified by the parent.
Unrelated atlas test, old overview and reports-index edits remain outside the PR.

The following sections preserve the **original review/verification history**.

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
