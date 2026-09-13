# Is CEBRA the problem? Autonomous endpoint investigation

2026-09-07. Branch `baseline/start-goal-cebra`; exploratory development research.

## Deliverables

- [Self-contained teaching HTML — portable tracked copy](../professor_updates/start_goal_20260907/endpoint-research-report.html)
- [Pre-fit study plan](start-goal-autoresearch-plan.md)
- [Research journal, including the adaptive follow-up declaration](start-goal-autoresearch-journal.md)
- [All 1,618 metric rows](../../outputs/start-goal-autoresearch-20260907/all_metrics.csv)
- [Artifact validation receipt](../../outputs/start-goal-autoresearch-20260907/validation.json)
- [Current delivery hashes, model-source check, and identical report rebuild](../../outputs/start-goal-autoresearch-20260907/delivery-validation.json)
- [Historical pre-formatting finalization receipt](../../outputs/start-goal-autoresearch-20260907/finalization.json)
- [Offline browser validation](../../outputs/start-goal-autoresearch-20260907/browser-check/browser-validation.json)
- [21-page browser-print PDF](../../outputs/start-goal-autoresearch-20260907/browser-check/report.pdf)

Consolidation update, 2026-09-08: a byte-identical HTML copy is now tracked at the link above, with figures and metric CSV embedded. Models, arrays and detailed receipts remain in ignored local outputs. Historical worktree/commit-state and temporary-browser descriptions below record the original delivery, not this PR's state. See the [research handoff](README.md) for current status.

## Main results

All values below are three-seed mean **joint development accuracy**, except the
explicitly separate-goal result. This is true-label-conditioned pseudopopulation
separability, not unknown-real-trial deployment or path/H1 evidence.

| Question | Result |
| --- | --- |
| Simple reference | PCA8/bin + logistic C=.01: **83.61%** |
| Same temperature/update sampling contrast | Behavior τ=.3 at 250 updates: **53.06%**; same-pair/same-bin positives + global negatives: **83.33%** |
| Does more training help? | That same-bin-positive setting declines to **64.86%** at 3,000 updates; original Time declines from **69.72%** at 250 to **51.67%** at 1,000 |
| Also match negatives in time? | At 3,000 updates: grouped-bin references/global negatives **68.47%**, versus same-bin negatives **59.58%** |
| More synthetic training rows | Time-matched τ=.3 at 3,000 updates: **59.58% → 81.53%** for 16 → 64 rows/class; PCA **83.61% → 84.86%** |
| Fewer recorded sources | PCA **58.75/73.75/83.61%** for requested quarter/half/full pools; CEBRA **24.44/43.06/59.58%** |
| Student-style, separate target | Six-class goal LDA peaks descriptively at **81.25%**, 0.4–0.5 s; this is not 30-class joint accuracy |
| CE follow-up | Binwise CE common readout: **20.00%** at 3,000; its early sampled maximum **28.75%**; 64 rows/class reaches **49.03%** at 3,000 |
| Stronger CE regularization | Weight decay0.1 drives this recipe to **3.33%** chance; this does not rule out untested moderate regularization |

**Conclusion:** CEBRA is not intrinsically incapable of representing the target.
The original positive sampling mixed distinct cue phases. Many late checkpoints
worsen development decoding while retaining high training-readout scores:
overfitting of the combined encoder/readout pipeline. Lower temperature and correct
positive conditioning help; negative time matching is not automatically helpful.
More width/dimensions/updates, whole-cue inputs, or replacing InfoNCE with one
CE recipe did not provide a general cure. PCA remains the simplest practical
reference. Early/synthetic-augmentation CEBRA results are competitive descriptive
observations, not independently validated selections.

The synthetic-row gain is not pure optimization: mean distinct training sources
used rises from 10,889 to 12,279 out of the **same 12,288 available** sources.
Quarter/half requested source fractions retain at least one source per
session/condition, giving actual pools of 3,777 and 6,551.

Only 1/58 sessions supports all 30 classes under the audited strict 75/25 time
cut. The executed chronological-within-condition sensitivity is weaker and not
a new untouched holdout. Marker semantics, recording metadata and serial/history
confounds remain unresolved. No confidence intervals over pseudorows or
confirmatory significance claims are made.

## Validation and stopping

- **112 new neural fits:** 79 CEBRA and 33 CE, including one synthetic signal
  control and the bounded CE follow-up; old checkpoint readouts required no
  encoder refitting.
- Synthetic positive control **100%**; constant-input control **3.33%**.
- Recomputed **1,618 metrics**, checked **5,515 artifact hashes** and **1,769,760
  session/source components**, verified **111 train-only input scalers**, replayed
  **33 CE heads on CPU**, and recomputed **300 cross-temporal entries**.
- **112 checkpoint reload checks** passed; six follow-up replay fits reproduced
  original final encoder/head weights and predictions exactly.
- Twelve runnable tests and runtime-configured Pyright passed. Fresh read-only
  implementation and final artifact/content reviews found no substantive issues.
- All **286 stored/legacy checkpoint files** tested support restricted
  `weights_only=True` loading. Final model-source ASTs differ from the executed
  follow-up snapshots only at six reader arguments; training logic is unchanged.
- Offline Chrome checks passed: nine embedded figures, embedded CSV download,
  valid section anchors, visible scrolled headings, and no mobile page overflow.
  Browser profiles were removed; screenshots/PDF and the first failed layout
  receipt remain beside the report.
- All fitting is finished. No original validation/test features or additional
  cells were used; no persistent service was created. The original checkout and
  old run artifacts were preserved. Work remains uncommitted.

Source scripts: `scripts/start_goal_autoresearch.py`,
`scripts/start_goal_ce_followup.py`, `scripts/render_start_goal_autoresearch.py`,
and `scripts/test_start_goal_autoresearch.py`. Run as modules from the repository
root with the audited runtime in the plan. Verification/browser scripts and
receipts are retained with the local outputs.

## Suggested review flow (~30 minutes)

1. **Answer → Data & design (§§1–2):** establish the target and independent
   observation. Explain why a known-condition pseudopopulation is not one
   naturally recorded trial, and why endpoint decoding is not path/H1 evidence.
2. **Models → Results (§§3–4):** compare PCA/CEBRA/CE inputs and feature budgets.
   Keep original C=1 versus common C=.01, and six-class versus 30-class scores,
   distinct before ranking anything.
3. **Diagnosis → CE follow-up (§§5–5b):** read the checkpoint curves and sampler
   contrasts. Ask which explanations gained support, which simple fixes failed,
   and which comparisons change more than one factor.
4. **Inside the models → Scaling (§§6,8):** separate probe information from
   circuit claims, and additional recorded sources from synthetic recombinations.
   Check the differing probe dimensions and actual sources used.
5. **Student comparison → Nulls (§§7,9):** inspect what was genuinely matched,
   what was not replicated, and why the nulls are diagnostic rather than
   calibrated significance tests.
6. **Research trail → Limits & next steps (§§10–12):** check the sequence of
   hypotheses, controls, fixed screen, adaptive follow-up, and stopping decision.
   Finish with three notes: the strongest claim you accept, the weakest
   assumption, and the next experiment or metadata check worth doing.

For cmux review, a byte-identical HTML copy was staged at
`/tmp/pi-teach/start-goal-endpoint-research-20260907.html`, served by the existing
loopback-only port8765 server. It was opened in a new browser tab without
replacing the older report; all nine figures loaded. No new server was started.
The canonical report remains in the study output directory above.
