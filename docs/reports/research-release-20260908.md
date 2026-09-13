# Research release: preservation, verification and remaining gaps

**2026-09-08 consolidation into a PR targeting `main`; no new biological fits.** Read the [research index](README.md) for scientific status. PR #4 already contains V6–V9; this package adds the later work and collates the teaching discussion. It does not merge anything into `main` automatically.

## What is preserved in Git

- Existing tracked research code/history, plus endpoint and path follow-up runners, tests, report builders and read-only verification entry points from the accessible sibling worktrees.
- Current synthesis and continuation brief; historical plans/journals; professor/teaching reports; the PCA/below-chance explanation and curated figure.
- A byte-identical portable copy of the endpoint HTML, which was previously only in ignored outputs. Its nine figures and metric CSV are embedded.
- [Historical code archive](archive/research-20260908/README.md): 49 recorded project-code sources mapped to 26 distinct snapshots, including the original PCA plotting script, earlier temporary report/audit-view builders and three historical transfer-audit helpers. The latter can access raw/mixed-split files and the removed eight-unit candidate supplement; they are archival text only, were not executed during packaging, and do not authorize cohort expansion. Old and new execution/loader/reporting versions remain distinguishable rather than silently overwritten.
- Explicit status labels for accepted historical results, frozen plans, rejected interpretations, superseded artifacts and local-only files. Intermediate notes were not arbitrarily deleted.

The main, endpoint and path originals remain at:

```text
/home/hongyi-home-lab/neuro_science
/home/hongyi-home-lab/neuro_science-start-goal-cebra
/home/hongyi-home-lab/neuro_science-path-diagnosis
```

Integration uses `/home/hongyi-home-lab/neuro_science-release-20260908`, branch `release/research-consolidation-20260908`, initially based on `origin/main` at `ca8301c`. This avoids writing over source worktrees. Historical analysis HEAD `a9d8dac` and dirty-state descriptions are experiment provenance, not the release commit. A registered but inaccessible Mac worktree was not inspected or removed; no completeness claim covers its unavailable contents.

## What is NOT backed up by this PR

| Local location | Retention / meaning |
| --- | --- |
| Main checkout `outputs/` (~1.8G at inventory) | Includes accepted V6–V9, prior attempts, importer/behavioral outputs and audit receipts. Not all are approved model artifacts or part of one benchmark. |
| Endpoint checkout `outputs/` (~970M) | Baseline, diagnosis, follow-up, prediction arrays, trusted model checkpoints, detailed logs and verification receipts. |
| Path checkout `outputs/` (~492M) | Frozen producers, exact-product/Track B/Track C outputs, checkpoints, predictions, audits and report render checks. |
| Native data and recorded research runtime | Remain in ignored `data/` and `scratch/`; not uploaded or newly imported. |
| Planning/reviewer/browser scratch | Relevant completed conclusions and corrections are collated; source drafts and failed/intermediate receipts remain local. Temporary views are not canonical deliverables. |

**A Git clone cannot restore these ignored files.** They remain on the same host; preservation in place is not a verified off-host backup. Do not remove these worktrees with `--force`, prune their outputs, or treat all of `work/`/`scratch/` as disposable. A separately authorized data/artifact backup and restore rehearsal is still needed before removing the originals. We did not upload raw lab tables, checkpoints, arrays, environments, credentials or full terminal/session logs to GitHub.

The pre-existing main-checkout baseline formatting patch remains local and was not silently discarded. Its scientific code is already tracked; preservation checks distinguish byte differences from logical changes. “No code lost” here means the inventoried source work was retained—not a claim about unknown/deleted historical files, inaccessible worktrees or every temporary shell command ever executed.

## Checks actually rerun for this package

The checks below read accepted saved outputs or shipped files; none refits a biological model, reloads checkpoints, reads raw/importer tables or materializes original split assignments.

| Check | Verified outcome | Boundary |
| --- | --- | --- |
| Existing V6–V9 helper | Report/code/source-tensor hashes; 52 fit records, 52,000 loss rows, saved reload receipts; 24 observed CEBRA metric rows recomputed; eight non-fitting tests passed | Saved reload receipts checked, not checkpoint reload repeated. |
| Path verifier | 342 fit records; 510,000 updates; 4,488 hashed artifacts; 42 prefix receipts; exact weighted predictions, source separation and null recalculation | Exact observed maximum 7/12, 18 inclusive exceedances, family p **19/21**. Track C null table consistency is also checked; not lab metadata or every possible analysis invariant. |
| Bounded endpoint verifier | **2,251 baseline hashes + 5,515 study hashes**; **690 baseline + 1,618 follow-up metric rows** independently recalculated | Does not repeat original-split, source-assembly, scaler or checkpoint-reload checks. Those have historical receipts, not newly claimed coverage. |

The final merged package also passed **98 shipped-file checksums**, preserved all **9 numerical path-report tables and 12 figures**, and matched **5,253 retained local path-artifact hashes**. Both verification CLIs rejected `-O` as intended. An initial local-inventory command used the release checkout instead of the owning path worktree and failed on missing paths; the corrected command passed without changing artifacts or the inventory.

Hash counts are manifest entries, not counts of independent experiments or necessarily unique files. Software checks and AI-assisted reviews are not biological replication or external human peer review. The original holdout remains exposed.

### Re-run on the data-equipped host

Use the recorded research environment. The commands below deliberately identify artifact locations rather than imply a clean clone has them. Run without `-O`; assertions are verification checks.

```sh
PY=/home/hongyi-home-lab/neuro_science/scratch/v6-v9-runtime/bin/python
RELEASE=/home/hongyi-home-lab/neuro_science-release-20260908

# Historical V6–V9 artifacts and frozen report/code identities in their owning checkout:
(cd /home/hongyi-home-lab/neuro_science && \
  "$PY" scripts/verify_place195_v6_v9_artifacts.py)

# Saved path study, no new fitting:
"$PY" "$RELEASE/scripts/verify_path_generalization_results.py" \
  /home/hongyi-home-lab/neuro_science-path-diagnosis/outputs/path-generalization-20260907/results-20260907T081200Z

# Endpoint hashes and predictions only; does not call legacy receipt-writing verifiers:
"$PY" "$RELEASE/scripts/verify_endpoint_saved_artifacts.py" \
  /home/hongyi-home-lab/neuro_science-start-goal-cebra/outputs/start-goal-cebra-20260907 \
  /home/hongyi-home-lab/neuro_science-start-goal-cebra/outputs/start-goal-autoresearch-20260907
```

The final merged-tree code-only suite passed **82 tests** in 2.879 seconds; the earlier 2.806-second candidate check is preserved separately. It excludes two local-input tests (`test_actual_input_gate` and `test_saved_manifest_has_seven_session_components_per_pseudorow`); the latter was separately covered by the original V6–V9 artifact helper. The suite includes tiny CPU optimization tests on invented data, not biological model fits. All active Python scripts parsed. LSP checks were partly inconclusive; a sklearn `zero_division=0` stub warning was classified as a false positive against the supported, successfully executed runtime API. No full-project type-clean claim is made. Logs and copy identities are under [release receipts](release-20260908/).

Package and local-inventory commands (different working-directory requirements):

```sh
python "$RELEASE/scripts/verify_path_generalization_package.py"
(cd /home/hongyi-home-lab/neuro_science-path-diagnosis && \
  sha256sum --status -c "$RELEASE/docs/professor_updates/path_generalization_20260907/LOCAL_SHA256SUMS")
```

To repeat the bounded software suite for this release (uses the runtime above, including synthetic CPU optimizers):

```sh
cd "$RELEASE"
"$PY" - <<'PY'
import unittest

def flatten(item):
    if isinstance(item, unittest.TestSuite):
        for child in item:
            yield from flatten(child)
    else:
        yield item

omit = {'test_actual_input_gate',
        'test_saved_manifest_has_seven_session_components_per_pseudorow'}
suite = unittest.defaultTestLoader.discover('scripts', pattern='test_*.py')
cases = [case for case in flatten(suite)
         if case.id().rsplit('.', 1)[-1] not in omit]
result = unittest.TextTestRunner().run(unittest.TestSuite(cases))
raise SystemExit(not result.wasSuccessful())
PY
```

The endpoint verifier is a small read-only packaging check, not a replacement for the fuller historical scientific audit. Its synthetic regression tests cover metric calculation, changed-file detection and rejecting a manifest path outside its allowed artifact root. Missing/corrupt artifacts intentionally fail the command; it never rewrites a receipt to make verification pass.

## Known gaps and superseded material

- The missing first V7 log/artifact timing cannot be reconstructed honestly. It remains disclosed in the accepted report, not filled in by a new packaging receipt.
- The initial V6 exposure and follow-up mixed-split metadata access are retained, not “fixed” by resplitting or deleting notes.
- Old HTML formatting identities, initial Track A failure, exact-tie correction, and unsuccessful browser/checking attempts retain their chronology. The [supersession map](README.md#explicit-supersession-map) identifies the preferred authority.
- Archival verifiers can write receipts or access broader metadata; do not assume every file named `verify` is a read-only safe entry point. Use the bounded commands above.
- Some historical local links necessarily remain local. The portable HTML copies and this index remove dependence on a running cmux viewer for the delivered reports; they do not make model reproduction data-free.
- The small original path contrast, the 30-class endpoint task and broader real-trial Track C are different estimands. No favorable endpoint setting, flipped validation label, selected threshold or synthetic sample count converts this package into confirmation of H1.

The reviewed path leaf was merged as exact commit `9e0457438c901ad6aa0c06be107d2cc130e7a884`. Four documentation checksum entries were resealed for combined navigation/scope; protected report/code/archive bytes and the local inventory were unchanged. See [leaf integration](release-20260908/leaf-integration.json) and [preservation manifest](release-20260908/preservation-manifest.json). An ensuing formatting-only difference in the leaf working verifier was observed (AST identical); the release retains the committed bytes and does not restore another session's working files. The final PR description records verification/review status; this document is not authorization for further fitting, new data access, cleanup, service changes or an external artifact upload.
