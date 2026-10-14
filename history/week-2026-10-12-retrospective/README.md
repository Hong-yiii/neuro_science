# Oct12–18 — Retrospective and repository organization

**Week in progress; only October12 work is recorded.**

The [current retrospective lives in `report/`](../../report/README.md), not in a
second historical manuscript copy. October12 work assembled and refined the
CEBRA-Time retrospective, recorded feedback and a frozen reading milestone, and
began report-first filing. These are publishing/software changes, not experiments.

## This week's records

- [Current manuscript and pending feedback](../../report/README.md)
- [Earlier filing archive](../../docs/reports/archive/early-work-20261012/README.md)
- [Original reorganization assessment](../../docs/repo-reorganization-plan-20261012.md)
- [Implemented migration scope and checks](../../docs/reorganization.md)

The later approved hierarchy puts weekly reading artifacts here and genuine shared
scientific implementation under `src/neuro/`. Remaining scripts are explicitly
legacy migration work, not the desired permanent home for scientific logic.
The notebook will be one companion to the report; its detailed scientific scope
is not yet implemented or authorized to fit models.

The frozen HTML already had a local byte difference before this migration. Both
versions were preserved; its exact-integrity check must continue to expose that
unresolved difference rather than silently accepting a new hash.
