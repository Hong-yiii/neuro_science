# Report-first reorganization — implementation checkpoint

2026-10-12. **Three-study scientific package implemented; wider migration remains open.**

Checkpoint **`ebe8256`** preserves the implemented state on
`refactor/report-first-weekly-layout`, based on merged PR19 (`a169edf`). The owner
subsequently authorized a draft PR and high-level documentation cleanup.
[Maintained software design](software-design.md) records the current package and diagrams;
the preserved [historical HTML preview](codebase-design.html) may lag this reference.
[Documentation map](README.md) replaces competing entry points. Long-form workspace
and publishing records are preserved verbatim in the
[operations archive](../history/operations/README.md).

The subsequent package consolidation from **`cc0527e`** is committed at **`8c98b52`**
and published on the same branch in
[PR20](https://github.com/Hong-yiii/neuro_science/pull/20). It packages the full-trial,
endpoint-time and cue-time readout family; the pre-existing dirty design HTML is
explicitly excluded and unchanged. Whether/how the future companion notebook uses
this package remains open, depending on its needs and complexity; no notebook is
implemented or required to depend on these scientific workflows.

## Implemented

- Current eight-file manuscript package moved physically to [`report/`](../report/README.md).
  The old package path is a relative compatibility symlink. The builder defaults to
  the current manuscript, not revision02. Source HTML retains its original virtual
  evidence base; local relocation does not change historical Git citations.
- Seven Monday–Sunday Singapore-time [weekly overviews](../history/README.md).
  Eleven self-contained historical HTML files moved physically under weeks/studies,
  byte-for-byte, with clean names. [Exact paths/hashes](../history/relocations.json).
  Old paths remain symlinks, not independent copies. Frozen relative-link HTML,
  protocols and aggregate source packages stay in place in this slice.
- Shared place195 split validation/access/audit implementation moved byte-for-byte
  to [`src/neuro/place195_split_access.py`](../src/neuro/place195_split_access.py).
  Seven scientific callers import it explicitly. Legacy imports retain module/class
  identity through a small compatibility module. No algorithm changed.
- Full-trial transfer, endpoint-time and cue-time scientific bodies now live in
  [`neuro.studies`](../src/neuro/README.md), with thin old CLI/import aliases retaining
  module identity, monkeypatch behavior and saved-class lookup paths. Numerical
  definitions retain pre-migration AST; labels and pair-lineage schemas stay distinct.
  The existing shared dataset/training/embedding/decoder objects now use package imports.
- Equivalent file hashing, endpoint/cue-time fresh-directory policy, full-trial/endpoint
  monotonic deadline and nested source copying are shared without a universal runner.
  Streaming endpoint outputs versus accumulated full-trial results remain unchanged.
- Current collectors include actual package implementations, initializers, execution/
  provenance seams and audited active helper modules—not only aliases. Snapshots
  support nested paths. Historical gates/hashes/approvals were not rewritten; cue-time's
  historical typing-only review is explicitly not approval of current packaged source.
- Removed the two obsolete tracked paper-queue documents, `papers/README.md` and
  `papers/reading-roadmap.md`; recovery is revision `b55b10f`. Ignored PDFs were
  not touched. Other proposed deletions wait for their actual dependencies to move.

## Boundaries and remaining work

The requested three-study family is complete in `src/neuro/studies/`. **October15
active-helper cleanup is implemented and independently reviewed**, after
checkpoint `ce31248`. Only the 21 required raw IO/binning/session/solver/geometry
definitions and their support closure were extracted, retaining exact pinned AST.
`neuro.legacy_adapters` is removed. Current package imports have no scripts dependency
or path shim. Other scientific bodies remain unchanged historical implementations
outside package support, not a current second source of truth. The source manifest
now includes only active package closure and external CLI aliases/initializer justified
by the current launch/snapshot contract. Older scripts are not hashed merely for history.
See [ownership](../src/neuro/README.md#active-helper-ownership-and-historical-boundary).
No install is needed (`PYTHONPATH=src` or external legacy bootstrap); a standalone wheel
or portable historical snapshot runtime is not claimed.

Whole evidence packages still need a location/identity-aware migration. Some protocols,
geometry paths and helper files are bound into approvals/hashes; some historical
renderers load private results. Do not mechanically regenerate them, rewrite frozen
hashes or claim current source is the exact historical runner. Current-source approvals
are intentionally stale after the import/provenance edits. Historical reproduction
must use retained executed sources/original revision plus separately authorized private
artifacts. Private replay compatibility has **not** been certified here.

Old-path symlinks are deliberate transitional compatibility, not the final desired
layout. Read weekly links to the real files on GitHub; GitHub may show a symlink's text
instead of rendering its target. Source report templates are built before offline
reading. Notebook integration remains open. No fit (including fitting smoke tests),
private-data access/replay, environment change, server or worktree cleanup
is included in package consolidation. The owner subsequently authorized publication
and merge of PR20, including the reviewed October15 helper cleanup and README showcase,
to close this session. The linked PR records the merge result; merging does not
approve scientific execution or additional migration work.

## Preservation

The report's frozen HTML already differed locally from the committed milestone.
It was moved unchanged. Both versions were copied to the ignored
`work/reorganization-weekly-audit/before-build/` before migration:

- Working file: `849fe48f40f9d8140517393bd7686c4153cbf89860fa2eb820216300c00f1a5c`.
- Committed milestone: `86497662096908f5fa92f1d00747377b2046e07a37ea225ae8fdbedcc9dfbde6`.

The exact frozen check continues to fail on the preserved local file. Its expected
hash was not changed. Deciding which version should become the published milestone
is separate from filing. Untracked `docs/reports/current-state-20260927/`, ignored
PDFs/data/outputs/runtimes, submodules and retained worktrees remain untouched.
For package consolidation, the dirty `docs/codebase-design.html` SHA-256 remains
`21e05d4b11cb58a9a3d8455b99dca11868cf457a7aec8127e9fd97f40cd1b9b5`.
The unrelated untracked tree's complete file-hash baseline and original study hashes
are retained in `work/package-consolidation/baseline.json`; original pre-package source
is recoverable at `cc0527e`, distinct from older executed-source snapshots.

Original code/report recovery is Git revision `b55b10f`; this does not back up private
data. The moved split implementation also retains its original exact SHA-256, recorded
in its README/check. Local scout reports, baseline copies and implementation receipts
remain in `work/reorganization-weekly-audit/`; these are intentional retained audit
artifacts, not a new experiment or an off-host backup.

## Focused validation (no broad scientific runner)

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest scripts.test_place195_split_filtered_access -v
PYTHONDONTWRITEBYTECODE=1 PYTHONNOUSERSITE=1 scratch/v6-v9-runtime/bin/python -B \
  -m unittest scripts.test_neuro_study_package -v
PYTHONDONTWRITEBYTECODE=1 python3 report/test_layout.py
PYTHONDONTWRITEBYTECODE=1 python3 report/test_path_summary.py
PYTHONDONTWRITEBYTECODE=1 python3 report/test_build.py
```

The split suite reuses three existing invented-data checks and adds one relocation
check (identity, source provenance and cold imports). The single layout check covers
all moved reading bytes, old aliases and new navigation. Existing report arithmetic
and builder checks are reused. `test_build.py` runs builder checks, then the unchanged
exact frozen-integrity check: its known local mismatch is **not a green test**.
Builder checks can be diagnosed separately by importing `check_builder`; do not
mistake that for passing frozen integrity.

The broad `scripts/check_research_software.py` is deliberately not run: its unexcluded
embedding QA can read private inputs. No additional test framework or per-week suite.

The package suite adds four focused migration checks (pinned-source AST, nested
snapshot/bookkeeping, cold import/module/class/source identity, and CLI help). It
reads tracked source and invented temporary files only; cold imports reject private
lab paths. Existing scientific test modules must be selected method-by-method: many
fit even on invented inputs. The scoped retained validation harness in
`work/package-consolidation/validate.py` blocks fit/optimization APIs and private
`data/`/`outputs/` access while reusing reviewed non-fitting methods.

### Earlier slice: recorded outcome

Task `b65019e21` passed four split tests, the layout check, existing report aggregate
arithmetic and builder regressions. A temporary tracked-only baseline export confirmed
**byte-identical generated output** for both current manuscript and revision02 before
and after relocation; no existing output file was overwritten. The temporary tree was
removed automatically. The check also confirmed the frozen working bytes stayed
unchanged and the default integrity test still fails specifically on the known mismatch.
Earlier task `b87803f7c` caught a fixture path normalization bug through the legacy
directory symlink; it was fixed and the complete focused check rerun.

Independent read-only reviewer `923a153e-47b7-4814-b7e7-80fe6def44d6` found no findings
for this bounded slice and considered the checks proportionate. It independently
verified moved HTML and split-implementation bytes against Git, aliases and provenance
collectors. Review did not execute scientific CLIs or private replay. Its result is
retained at `work/reorganization-weekly-audit/implementation-review.md`.

Eight focused primary Python diagnostic checks were clean. Of nine larger touched
scientific modules, two checks confirmed clean and seven timed out: **not a clean
project-wide type-check claim**. Auxiliary scanning also flags existing fail-fast
numeric conversions in historical runners; this filing pass does not change their
scientific error behavior merely to satisfy a blanket try/except rule. Syntax/lint
and final whitespace checks are separate from historical runtime certification.

### Publication/documentation follow-up

The offline design HTML passed primary HTML diagnostics and Chrome checks at 1200px
and 390px: no horizontal overflow, duplicate IDs, broken internal anchors or remote
resources. Screenshots were inspected; no server/listening port was started. Sixty
local documentation links/anchors passed, and both archived long documents match
checkpoint `ebe8256` exactly. Independent documentation review reported no findings.
Receipts/screenshots/review remain in `work/reorganization-weekly-audit/`.

Task `b75b2f2a5` reran the four split checks, layout, report arithmetic and builder
checks successfully, then confirmed the **expected frozen-integrity failure**.
The earlier publication harness `bf266490d` had omitted the report import path;
correcting that harness required no production change. Chrome task `bede6cce2`
completed and its temporary profile was removed. Full scientific diagnostics and
private replay remain outside this publication claim; cached historical fail-fast
conversion warnings are not silently suppressed.

### Package consolidation validation — October13

Task `b58aef249` completed with 42 guarded checks passing (34 existing non-fitting
checks, four package migration checks and four split checks), followed by passing
report layout/arithmetic/builder checks and the explicitly expected frozen-integrity
failure. Its receipt/log are under `.pi/tasks/session-1027780-1027780/`. An earlier
cold-import fixture omitted the repository path for scripts-first imports; the test
harness was corrected without changing production import behavior. The implementation
worker timed out after the successful final checks; the parent inspected the outcome
and independently reran six stdlib source/split checks in task `b34528b0d` successfully.

Independent read-only review found no findings; retained report:
`work/package-consolidation/review.md`. Primary diagnostics were clean for the three
study modules and seven supporting modules/wrappers/tests. Seventy-seven documentation
links/anchors passed and all 14 protected baseline file hashes matched. At that earlier
local validation checkpoint no files were staged, committed or pushed; the package was
subsequently committed/pushed at `8c98b52` to open draft PR20. The audit baseline,
guarded validation harness, review and
small matplotlib cache remain under ignored `work/package-consolidation/` intentionally.

CUDA availability probes in the existing runtime emitted error-804 initialization
warnings. These passing import/source/synthetic checks do **not** establish GPU readiness,
private replay compatibility or standalone-wheel support. No GPU fit or runtime/driver
repair was attempted. Package use by the future notebook remains an open design choice.

### Software-engineering reference — October13

[`software-design.md`](software-design.md) is the maintained as-built reference for
package `8c98b52`: module ownership, explicit object/data contracts, import compatibility,
three workflow sequences, approvals, source/artifact provenance, partial failures,
retry limitations, resource bounds and testing layers. Six Mermaid diagrams accompany
it; no generic Runner or wheel/deployment certification is implied. Full per-function
API documentation and comprehensive legacy-family coverage remain gaps.

Independent source review found no findings in its targeted coverage; receipt:
`work/package-consolidation/engineering-review.md`. All six final diagram sources were
parsed and rendered locally with temporary Mermaid 11.4.1 and existing headless Chrome.
An initial sequence-label semicolon parse error (`bbc074711`) was corrected; rerender
`b8ff37937` and visual capture `b16a73253` completed successfully. Dependency, UML and
cue lifecycle images were inspected. Sixty-nine local links/anchors and all 14 protected
baseline hashes passed. No scientific code changed or scientific checks were rerun in
this documentation follow-up. The known frozen-integrity and GPU caveats remain.

Render receipts, source hashes, SVG/PNG and a script-free offline diagram gallery are
retained under ignored `work/package-consolidation/engineering-diagrams/`. Temporary
renderer assets/profiles were removed after verification; no installation, serving port,
retained process or private-data transfer was introduced. The Git-backed Markdown uses
GitHub's native Mermaid rendering, not a repository renderer dependency.

### Active-helper cleanup validation — October15

Task `b06823806` completed with **46 guarded checks passing**: 34 reviewed existing
non-fitting study checks, eight focused package checks and four split checks. All
21 extracted definitions match pinned `ce31248` AST; all other study top-level AST
is unchanged apart from imports and the exact cue-time geometry reexport. Cold imports
from an unrelated cwd load no scripts or mutate the import path. Copied source closures
import without fallback to the checkout, then retain documented external alias identity.
Invented HDF5 markers/spikes and geometry arrays exercise extracted input/geometry seams.

Earlier tasks `b3712d633` and `bcf85ba7b` failed on an intermediate generated import
formatting error and stale test expectations (the old implicit checkout bootstrap and
historical split-alias manifest entry). These were corrected, not suppressed; final
guarded coverage passed. No fit, private input/model/replay, broad scientific runner,
installation or service was invoked. CUDA error804 import/help warnings remain a
runtime caveat, not GPU certification.

Ruff and syntax checks passed. Primary diagnostics confirmed all seven small helper/
provenance/test files clean; one study was clean and two larger study checks timed out,
so full type-check cleanliness is not claimed. All 14 original protected hashes match,
including unrelated dirty HTML and untracked report files. Seventy-six local Markdown
link targets exist. All six updated Mermaid diagrams rendered with temporary Mermaid
11.4.1 and existing headless Chrome in task `b3b3361b7`; the dependency/import preview
was visually checked. At that validation checkpoint no files were staged. Independent source-only acceptance review
found no findings. Existing untested MATLAB-v5/string/fallback-reader branches retain
exact AST and complete dependencies; no new execution certification is implied.
Evidence (baseline, exact AST/caller inventory, validation logs, extraction scripts,
review and diagram receipts) is retained intentionally under ignored
`work/active-helper-cleanup/`. Temporary browser assets/profile were removed. No
historical source/hash/approval was rewritten.
