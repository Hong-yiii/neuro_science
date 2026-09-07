# Place-data verification and narrow homelab transfer

**Current status: removed from the homelab at Hongyi's request.** The eight-cell candidate package was deleted after deciding to exclude it from the research set. The original 195-cell dataset and source-trial splits remain unchanged. The Mac copy remains local; the transfer details below are historical provenance.

Date: 2026-09-06 (Asia/Singapore). Status: **software smoke test / provenance and data-feasibility audit**, not new scientific evidence. No model fitting or path/response comparison.

## Outcome and user scope

Hongyi explicitly requested **place/spatially selected units only**. The current professor-supplied 195-unit list is complete on the homelab and unchanged upstream. No additional units were found in that exact list.

A separate **eight-unit place-selected candidate supplement** was copied via the Mac to the homelab. It is supported by an older explicit filtered-place list and a later upstream spatial-selection report. Its selection equivalence to the current 195 list remains unresolved. It has not been merged into the active dataset or used in analysis; do not describe it as a verified 203-cell cohort.

## Independently checked current state

Read the homelab in place at `/home/hongyi-home-lab/neuro_science`. Its HEAD is `c4eec752a0eab95e5c48300bc327191aefa57778`, one commit ahead of this Mac worktree's `7557881`, with additional uncommitted V6–V9 code and reports. Those files were not overwritten or synchronized from this older worktree.

| Stage | Units | Sessions | Distinct source trials | Train / validation |
| --- | ---: | ---: | ---: | --- |
| Completed selected-cell import | 195 | 58 | 23,901 | Not a benchmark split count |
| Primary V7–V9 source tensor | 29 | 7 | 104 | 82 / 22 |
| Relaxed V7–V8 source tensor | 40 | 11 | 146 | 114 / 32 |
| Strict V7–V8 source tensor | 6 | 1 | 11 | 6 / 5 |

Counts were checked against importer tables and saved source-tensor IDs/shapes, not inferred from report prose. The 104×29×10 primary tensor is masked source storage, not 104 simultaneous 29-cell recordings. Synthetic rows combine session blocks conditional on the behavioral target. Resampling does not create new biological trials. The selected snapshot has 1–8 units/session, median 3; every imported unit's simultaneity field is `candidate_same_session_unverified`.

Integrity checks:

- All 370 importer source-file records match homelab sizes and SHA-256 hashes.
- All seven hashed importer outputs match.
- All 666 old manifest paths exist; 664 hashes match, with only two `.DS_Store` differences.
- All 369 native importer source files also match **current upstream** SHA-256 hashes. The selection list independently has the expected hash `6ff311aab2feb4eafdbd16270deba1c57e0dd0261ea175dd59b88e5d966af35e`.
- The historical six-unit bundle remains absent, with 13 of its 22 receipt paths absent from the active snapshot. It was not restored wholesale.
- `20181105/session01` currently has six exact `array/channel/cell/spiketrain.mat` paths in `picasso-misc` and fifteen in `picasso`. Different file sizes and sorting/export provenance prevent summing or substituting those roots as additional independent units.

The Mac's authorized `cortex` SSH connection works. The former homelab-only upstream access limitation is resolved by using the Mac as the transfer route.

## Latest experiments and what they mean

Read the September 6 V6–V9 report, its holdout-exposure audit, saved panel metadata, final same-array metrics, and bin-selection null receipt.

- **V6:** replaced fragmented path signatures with a static operational graph of nine node/plaza regions and twelve corridors, giving 24 directed components. The primary neural task predicts one future directed component within provisional endpoint pair 4→3. This is a restricted path target, not whole-path reconstruction.
- **V7/V8:** used ten 100 ms cue bins, raw counts, and train-fitted PCA. Mean validation balanced accuracy: constant 0.500; raw total 0.453; raw ten-bin 0.474; PCA-3 0.521; PCA-8 0.453. PCA-3 ranged 0.258–0.789 across three assembly seeds, so the small positive mean is not a stable effect.
- **V8b:** the apparently perfect 0.2–0.3 s bin did not survive the matched diagnostic for selecting among ten bins: finite permutation p=0.2178. Pseudorow reuse and tiny real-source pools matter.
- **V9:** native GPU CEBRA completed 12 observed fits plus 40 full-pipeline null fits. Mean balanced accuracy was 0.443 for CEBRA-Time-8 and 0.414 for CEBRA-Behavior-8. No robust whole-cue improvement was established.

The accepted result is nonpositive/unstable **development-only condition-level evidence**, not evidence that prospective hippocampal information is biologically absent. These results do not establish H1a or H1b.

An earlier rejected V6 probe exposed endpoint aggregates containing original test trials. The accepted pipeline was restarted with guarded development access, but the old holdout cannot be called pristine. There was no test-model evaluation in this audit, and changing the random split would not erase the earlier exposure.

## Which additional data qualified for this transfer

The broader analysis list has 364 unique IDs, containing all 195 current selected IDs plus 169 others. All corresponding spike files exist, but broader-list membership does not establish spatial selection. That proposed expansion was rejected after Hongyi clarified scope.

The older `place_selective_cells.txt` has 16 extra IDs relative to the current 195. Several have nonselective entries in the later spatial report. It was not simply unioned with the current list. The older **filtered** place list has eight extra IDs; all eight are also adaptive-spatial-selective in the later report:

| Session | Candidate additions | Implication |
| --- | ---: | --- |
| 20181026/session01 | 6 | One additional available session; 421 matching marker-triplet rows |
| 20181102/session01 | 2 | Adds cells to an existing session; its 441 trial rows are not new trials |

These are import-compatible candidates, not final scientific inclusions. All eight have MATLAB-v5 numeric, finite, nonempty, sorted timestamp vectors, component labels, and the same `from firings.curated2.mda` reference convention as existing inputs. Three-stream marker triplets match exactly in both sessions. The audit loaded only Unity marker/time columns, not x/y/heading, and did not compute path statistics, outcome breakdowns, or spike/path associations.

The filtered list predates the professor's current 195 list. A bounded search did not find the generating record explaining their differing membership. Confirm selection equivalence, accepted-unit/anatomy metadata, real simultaneous recording groups, clock QC, and recording overlap before using these candidates. The new files do not directly increase the existing seven-session primary panel.

## Transfer receipt

Same repository-relative destination on the Mac worktree and homelab:

`data/raw/lab_server/cortex_place_filtered_candidates8_20260906/`

The Mac holds the staged copy; `scp` copied it to the homelab. The final package contains:

- Eight candidate spike trains.
- Eight native/session-metadata files for 20181026, including Ripple, Unity, and Eyelink.
- Seven small selection/provenance files.
- README, transfer manifest, schema check, upstream checksum receipt, and package checksums.

The 23 upstream payload files total **36,133,760 bytes**; all 28 package files total **36,163,971 bytes**. All payload hashes match upstream and the local copy. On the homelab, all 27 entries in `SHA256SUMS` match, as do the three reused native dependencies for 20181102. `SHA256SUMS` itself matches between hosts, hash `036cda34dd29b10ba49636ba40beb7663aeab2e2e3b8171f999201975f8ad420`.

No raytrace bulk data, broadband recordings, sorting workspaces, large spatial-map outputs, unselected spike collection, or cross-root unit union was transferred. The earlier 78 MB broader staging download completed before scope clarification; after retaining the narrow verified package, its 195 local files (including its scope marker) were removed. That broader package never reached the homelab.

No existing inputs, importer outputs, model outputs, or split assignments were modified. The existing source-trial split CSV's byte SHA-256 at final verification is `b0ef8cce43c79d9e2b1ae0a804c7d48fefeb92469670f3031485d0009fb10ff3`; distinguish this from the experiment's logical split hash `11237c8c35af4b09b6d81c1994ff3f8b702d245d3a262f70413dab2b182973d1`.

Detailed verification receipts and the bounded audit scripts are under ignored `outputs/data_transfer_audit_20260906/`. The first SFTP-style `scp` read from cortex failed to resolve its absolute paths and was replaced with bounded `rsync`; an early homelab verification ran before copying completed and was repeated successfully after completion. Both are recorded in `audit_attempts.json`.

Next step is selection/provenance reconciliation and a separately specified session-level feasibility analysis, preserving the existing 20181102 trial assignments. Do not run the fixed-place195 importer against this supplemental root unchanged: it expects its original selection and single-root dependency layout.
