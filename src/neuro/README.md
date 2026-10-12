# Scientific implementation: first bounded slice

`place195_split_access.py` is the shared place195 development split gate. It
contains the unchanged CSV/gzip reader, split validation and audit objects moved
byte-for-byte from `scripts/place195_split_filtered_access.py` (original SHA-256
`2cd7e7a14f6a045078c59d2489e6d06a615f033dc0f6c0cbea14533561608c0d`).
It is stdlib-only. Importing `neuro` or this module performs no data/model access;
constructing a reader explicitly opens the supplied split files.

Use `from neuro.place195_split_access import SplitFilteredAccess` with
`PYTHONPATH=src` from the repository root (or an absolute `src` path elsewhere).
No install is needed. `scripts/__init__.py` bootstraps the same source path for
retained `python -m scripts.<name>` commands. The old split-access script is an
import alias, including legacy bare imports; direct execution still does no work
because this helper never had a CLI. Old and new imports share module/class
identity. Other callers' existing repository-root calculations are unchanged.

Direct V6, V7/V8, path-generalization, preprocessing, endpoint-baseline,
full-trial and endpoint-readout callers now import the implementation explicitly.
Relevant code manifests/snapshots include the implementation rather than only
its compatibility alias. Preprocessing already hashes the class's defining
module. Frozen source snapshots, approvals and hash ledgers were **not** rewritten:
current-script approvals are intentionally stale, and exact-source historical
replay/release verification may reject this checkout. Use the retained executed
source/revision for historical reproduction, not a newly approved alias hash.
Snapshot collections are provenance, not newly certified standalone packages.

Focused software-only check (invented temporary CSVs plus source reads):

```sh
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -m unittest scripts.test_place195_split_filtered_access -v
```

Only this shared seam has moved. The remaining scientific bodies still in
`scripts/`, package/install configuration, portable snapshot bootstrapping and
separately authorized historical replay compatibility remain migration work.
Tests stay in their existing discovery location. No new fits, private-input
verification or broad runner execution is part of this slice.
