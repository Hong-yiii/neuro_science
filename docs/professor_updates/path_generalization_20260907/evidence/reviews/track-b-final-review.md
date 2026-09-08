medium — outputs/path-generalization-20260907/results-20260907T081200Z/track_b/track_b_family_null_pvalues.json:3 — family-max null p-value artifact is stale/float-biased

Verified: this artifact reports 17 exceedances and p=0.8571428571428571 at lines 4-7, with null19 stored as 0.5833333333333333 at line 21 while observed is 0.5833333333333334. Parent audit corrects this at `audits/track_b_exact_audit.json:19-20,41,65-69`: observed exact max is `7/12`, null19 is also `7/12`, inclusive exact exceedances are 18, and p=`19/21`=`0.9047619047619048`. I independently recomputed exact BA from saved prediction counts as `corr_abs/48 + corr_pres/12`; no mismatches with `track_b_exact_ba.csv`. Minimum fix: treat `audits/track_b_exact_audit.json` as authoritative and regenerate/supersede `track_b_family_null_pvalues.json` and `summary.json` before citation. Impact does not change the scientific result: the best fixed-family BA remains non-positive.

Approval with correction: use exact-audit p=`19/21` (`0.9047619`), not the raw producer p=`0.8571429`.

Audit notes:
- Content success: satisfied with the numeric correction above. Verified 342 fits = 62 observed + 280 null, 684 metric rows, 42 prefix pairs, and 510000 saved optimizer updates.
- Operational success: satisfied. Parent audit reports 4488 artifacts hashed, zero prefix/reload differences, complete exact rational audit; my read-only checks found all validation prediction rows had exact-Q 24 absent / 6 present and weights 1/48 absent, 1/12 present.
- Instruction compliance: satisfied. I used only saved outputs/audits; no new fitting, raw/importer/split access, edits, or subagents.

Scientific interpretation approved, bounded: fitting works on sampled training assemblies and replays across same-source assemblies (`other_assembly_same_training_sources` mean BA ≈ 0.995; own assembly 1.0), but exact-Q heldout transfer is poor/non-positive. Crossed-seed validation means verified as Time ≈ 0.249 and Behavior ≈ 0.352. Larger dimensions, more rows, and longer training did not consistently rescue validation BA. This supports “finite-source relationship does not transfer under this artifact contract,” not a causal explanation and not evidence for absence of biology.

Residual risks: artifact-only review cannot independently validate raw provenance beyond saved hashes/manifests; 20 null permutations give coarse p-value resolution.