# Report-first reorganization — implementation checkpoint

2026-10-12. **First slice implemented; full migration is not complete.**

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
- Relevant current provenance collectors include the actual `src/` implementation,
  not just the legacy alias. Snapshot writers now support that nested source path.
  Historical gates/snapshots were not rewritten to accept changed code.
- Removed the two obsolete tracked paper-queue documents, `papers/README.md` and
  `papers/reading-roadmap.md`; recovery is revision `b55b10f`. Ignored PDFs were
  not touched. Other proposed deletions wait for their actual dependencies to move.

## Boundaries and remaining work

The remaining scientific bodies still under `scripts/` are migration debt. Next
extract a coherent study family into `src/neuro/studies/` with thin launchers, retaining
its exact executed-source recovery route. Do not build a catch-all utils module or
copy implementations into weekly folders. No new package installation is needed for
the first seam (`PYTHONPATH=src` or existing `python -m scripts...` bootstrap).

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
reading. No notebook, biological fit, private-data access, replay, environment change,
server, worktree cleanup, commit, push or PR merge is included.

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

Original code/report recovery is Git revision `b55b10f`; this does not back up private
data. The moved split implementation also retains its original exact SHA-256, recorded
in its README/check. Local scout reports, baseline copies and implementation receipts
remain in `work/reorganization-weekly-audit/`; these are intentional retained audit
artifacts, not a new experiment or an off-host backup.

## Focused validation (no broad scientific runner)

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest scripts.test_place195_split_filtered_access -v
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

### Recorded outcome

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
