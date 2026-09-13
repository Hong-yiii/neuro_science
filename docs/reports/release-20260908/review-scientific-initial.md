major — /home/hongyi-home-lab/neuro_science-release-20260908/docs/research-questions.md:184 — release normative docs still point to the stale simultaneous-data-first milestone.

Verified evidence: the release index says normative authority remains `docs/research-questions.md` and `docs/analysis-contract.md` (`docs/reports/README.md:12`), but release `research-questions.md:184-189` still says “Before fitting CEBRA” obtain/verify simultaneous population data, and release `analysis-contract.md:173-175` says every analysis should report within verified simultaneous groups before synthesis. The sibling path package has already corrected this into a distinct condition-level pseudopopulation lane (`neuro_science-path-diagnosis/docs/research-questions.md:167-189`, `docs/analysis-contract.md:25-48`, `:201-206`) while preserving exact trial-specific H1 limits. Impact: if the main PR ships as-is, it has not fully collated the current path-package learning and will make the source-safe pseudopopulation proposal look inconsistent with the declared normative authority. Minimum fix: merge the leaf normative wording, or add equivalent status/index wording that labels it as a current **proposal** distinct from exact same-trial H1.

## Compatibility recommendation

The proposals are not genuinely incompatible. Preserve them as two distinct lanes:

- synthesis lane: E0/E1/E2 history/support/per-unit-first gates for a better-identified real-trial/control question;
- leaf lane: condition-level, source-safe pseudopopulation reproducibility for population-pattern evidence under recording constraints.

Do not change H1 or claim gates: exact trial-specific population-state/dynamics claims still require verified simultaneous same-trial population data; source-safe pseudopopulations can support only condition-level prospective-path coding, not intention/mechanism/H1b from supervised geometry alone. Merging the leaf normative changes is safe if those boundaries stay.

## Metric/explanation checks

No findings. Verified saved metrics support the PCA/below-chance explainer: PCA-3 validation BA `.7890625/.515625/.2578125` mean `.520833`; PCA-8 `.3671875/.4921875/.5` mean `.453125`; retained variance ranges match 21.2–21.5% and 44.4–45.2%; CEBRA-Time-3 validation confusions match the table and AUROCs `.0222168/.946289/0`.

No findings on interior-target wording. Packaged target-semantics evidence supports “interior after dropping first/last corridor runs,” the 50+1 outside-interior old-absent count, and the correction that the 99-source route lacks the selected edge.

## Grades

- Content success: mostly satisfied, with the normative-doc integration gap above.
- Operational success: satisfied for read-only review; no fits or installs run.
- Instruction compliance: satisfied; no edits, no raw/importer/test/checkpoint inspection.

Residual risks: active parent/leaf packaging may have changed after this snapshot; I inspected only requested docs/diffs and compact saved metrics, not all untracked artifacts.
