# First CEBRA Pilot Implementation Review

Date: 2026-08-26  
Scientific status: software smoke only; H1 analysis remains blocked

## Code Reading Order

1. `contracts.py` for the scientific trial gate and graph hash.
2. `neural.py` for cue-bin/unit axis and exposure math.
3. `paths.py` for invalid-gap splitting and path metrics.
4. `splits.py` for supplied split validation and hash stability.
5. `manifest.py` for run records and no-overwrite behavior.
6. `preflight.py` for CLI smoke boundaries.
7. `tests/test_framework.py` for executable boundary checks.

## Method Decisions

- Trial arrays are `cue_bin x unit`; no transpose fallback.
- One-cell navigation exports are loader-smoke only and cannot satisfy the
  scientific trial contract.
- Graphs are explicit directed edges with content hashes.
- Invalid path samples and nonadjacent transitions split; no interpolation.
- Raw repeats are retained; collapsed views are only for route-shape metrics.
- Split rows are caller supplied; derivatives of one source trial cannot cross
  splits.
- Manifests carry `scientific_status` and stop conditions.

## Review Trail

1. A pre-implementation method reviewer required the same-trial population gate,
   derivative-safe split hashing, a fixed bin-by-unit axis, explicit
   multi-segment path rules, retained dwell repeats, and software-only labeling.
2. A first code reviewer then found missing session/group fields in split
   records, package import failures, overly broad ignored output paths, missing
   complete-path classification, incomplete runtime package provenance, and a
   shape-only CEBRA save/load check.
3. A closeout reviewer then found that the scientific trial contract still
   lacked success/selection-history fields and that one imported manifest writer
   could bypass the CLI's output confinement.
4. The contract now requires those fields—or an explicit audited reason when
   predecessor metadata is unavailable—all manifest writers enforce
   `outputs/cebra_pilot/`, and the complete trial was rerun before final review.
5. A separate reviewer approved one intact local-data CEBRA smoke as a software
   check, required hard selector gates, and then identified three low findings:
   missing selector-edge tests, no explicit expected-embedding-shape assertion,
   and missing reproduction instructions. All three were fixed.

## Pre-Review Findings And Dispositions

- Same-trial and simultaneity fields: fixed in `CueNavigationTrial` required fields.
- Derivatives crossing splits: rejected by `freeze_splits`; session and
  simultaneous-group metadata are hashed and group-by-split counts are exposed.
- Axis transpose fallback: rejected by unit-axis alignment checks.
- Multi-segment and empty metric rules: documented in `paths.py` and the API
  math notes; full overlap is distinguished as `complete`.
- Raw repeats retained: `raw_valid_segments` keeps them.
- Current export boundary: JLD2 smoke always records `software_smoke_only` and H1 stop.
- Zero exposure: rejected for valid cue bins.
- Explicit hashable graph: `MazeGraph` only accepts explicit directed edges.
- Manifest claim status: `scientific_status` is required; every writer is
  restricted to `outputs/cebra_pilot/` and hashes include generated artifacts.
- Sequential/selection metadata: the scientific contract requires trial index,
  previous trial/goal/success, current success versus timeout, and inclusion
  reason; partial history and unexplained absence are rejected.
- Import usability: all sibling imports are package-relative and the CLI runs as
  `python -m docs.cebra_pilot.implementation.preflight`.
- CEBRA provenance/fidelity: runtime package versions are recorded and loaded
  transforms must match the pre-save transform.

## Executable Trial Evidence

| Check | Result | Artifact |
| --- | --- | --- |
| Boundary tests | 9 tests passed | `docs/cebra_pilot/implementation/tests/test_framework.py` |
| Synthetic preprocessing | Passed; graph/split/neural/path summaries written | `outputs/cebra_pilot/trial-20260825-preprocessing-v4/` |
| Current one-cell loader | 395 trials, 65,576 samples, 1,441 spikes; shape aligned | `outputs/cebra_pilot/trial-20260825-current-export-v3/` |
| Synthetic CEBRA 0.6.1 | `256 x 12 -> 256 x 3`; save/load maximum absolute transform difference `0.0` | `outputs/cebra_pilot/trial-20260825-cebra-v2/` |
| One intact local trial | Trial index 2, `134 x 1 -> 134 x 3`, one spike; save/load difference `0.0` | `outputs/cebra_pilot/trial-20260826-one-cell-cebra-v1/` |

Every manifest says `software_smoke_only`. The current-export manifests also
record the missing cue-period/same-trial/simultaneous-population H1 stop. The
local training run used the first eligible intact file-order trial, so no
CEBRA-Time pair crossed a trial boundary. Its one observed spike and one cell
make it an API/data-shape check, not a representation result.
Generated embeddings were checked for shape and save/load fidelity only; their
geometry was not inspected or interpreted. The repeated v1 and v2 CEBRA runs had
different embedding hashes despite the same recorded external seeds, while each
run's pre-save and reloaded transforms matched exactly. This is consistent with
the documented absence of full sklearn-estimator seeding and is why the framework
records but does not promise exact training determinism.

The first dependency-resolution attempt failed because the workspace required
NumPy `>=2.1` while CEBRA 0.6.1 requires NumPy `<2` on Windows. The workspace
floor was changed to `>=1.26.4`; the lockfile now resolves platform-specific
NumPy versions and the pinned CEBRA environment completed the trial.

## Final Independent Verdict

The post-fix reviewers reported no remaining blocker, high, medium, or low
findings. They verified the same-trial selection-history contract,
unexplained-history stop, central output-path confinement, package imports, all
nine boundary tests, expected CEBRA output shape, local-trial selector gates,
reproduction command, and the non-power wording of the 750-trial coverage floor.

- **Software framework: go.**
- **Scientific H1 analysis: no-go** until cue-aligned, same-trial,
  trial-linked simultaneous population data passes the hard gate.

## Blocked Or Deferred

Still blocked: real neural analysis, cue-aligned simultaneous population data,
authoritative maze adjacency, frozen real splits, behavior audit, and independent
review before interpretation.

Deliberately not implemented: raw/PCA decoding, behavior audit reports,
CEBRA-Time, path-conditioned CEBRA, graph-DTW, ANN comparison, and confirmatory
testing. Add them only after the documented gates pass.
