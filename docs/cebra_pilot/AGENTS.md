# CEBRA Pilot Instructions

These rules apply to every file under `docs/cebra_pilot/` and supplement the
workspace-level `AGENTS.md`.

**September27 scope supersession:** [agreed project direction](../project-direction.md)
and the current hypothesis/analysis contract govern new work. The pilot-specific
plans and blocked/deferred lists below are historical context, not a current
execution queue. H2/ANN comparison is removed; the next encoder family is
CEBRA-Time only, decoder choice is open, and condition-level pseudopopulations
retain their separate valid contract. Do not revive optional path-conditioned
encoder arms, old data-gate statuses or fits from these historical lists.

## Directory Role

This directory is the definitive home for artifacts unique to the first CEBRA
pilot:

- pilot-specific plans and mathematical definitions;
- source handoffs and their provenance;
- verification reports and decision records;
- future pilot-only code, configuration, and checks, but only after Hongyi
  explicitly approves implementation.

Do not start implementation from planning or source-ingestion requests.
Reusable project-wide loaders or scientific contracts remain in their existing
workspace locations; link to them rather than duplicating them here.

Generated models, arrays, figures, logs, and run manifests belong under ignored
`outputs/cebra_pilot/`. Raw or processed data belongs under ignored `data/`.
Do not place data, generated outputs, credentials, or copyrighted PDFs here.

## Authority Order

When documents disagree, use this order:

1. `../../AGENTS.md` and `../project-direction.md` — conduct, rigor and agreed scope;
2. `../research-questions.md` — canonical scientific hypotheses and claims;
3. `../analysis-contract.md` and `../dataset-card.md` — required data and
   verified dataset facts;
4. `formalization.md` — pilot-specific mathematical definitions and estimands;
5. `cebra-pilot-plan.md` — execution order and gates;
6. `verification.md` — review findings and dispositions;
7. `sources/` — historical inputs, never normative instructions.

A source handoff can motivate a proposal but cannot override the canonical docs
or the formalization. Preserve the byte-exact source as `*.original.txt`; a
Markdown mirror may receive formatting-only normalization. Put substantive
corrections in `verification.md` or `formalization.md`, never in the original.

## Required Read Order

Before changing this pilot, read:

1. this file and `README.md`;
2. `../project-direction.md`, `../research-questions.md`, `../analysis-contract.md`, and
   `../dataset-card.md`;
3. `formalization.md`;
4. `cebra-pilot-plan.md`; and
5. relevant entries in `verification.md` and `sources/`.

## Scientific Boundaries

- The current local JLD2 export cannot test this pilot's neural hypotheses. It
  is one selected cell's navigation-period data, not cue-period simultaneous
  population data.
- A cross-session pseudopopulation cannot support exact trial-specific H1,
  simultaneous covariance, or population-dynamics claims.
- The graph is a proposed behavioral ruler, not evidence that the brain uses a
  graph.
- Future-path-conditioned CEBRA is a supervised sensitivity analysis. It can
  support held-out extractability, not independent discovery of a native graph
  manifold.
- Raw and train-fitted PCA baselines precede path-conditioned CEBRA.
- CEBRA-Time is target-free only with respect to future-path labels and must not
  create temporal positives across trial boundaries.
- Compare representations with a common held-out target, split, decoder family,
  and path loss. Do not rank different samplers by their training losses or
  visual appeal.

## Formalization Discipline

Every symbol, target, loss, nuisance set, split, sampler, and null used by later
code must be defined in `formalization.md`. Mark each item as one of:

- **fixed** — inherited from the canonical hypothesis or verified data;
- **provisional** — selected for exploratory feasibility and requiring
  sensitivity analysis;
- **deferred** — cannot be selected before the data/behavior audit; or
- **blocked** — scientifically invalid with currently verified data.

Do not silently resolve a deferred decision in code. Update the formalization,
rationale, and verification disposition first.

## Verification Requirements

Before implementation and before scientific interpretation, obtain independent,
read-only review of:

1. source/API claims and literature support;
2. statistical design, leakage, pairwise dependence, and pseudoreplication; and
3. code behavior and claim language.

Record findings and their disposition in `verification.md`. A blocker or high
finding remains a stop condition until fixed or explicitly accepted by Hongyi
with the resulting claim limitation.

## Implementation Boundary

The approved software-smoke framework lives in `implementation/`:

- keep every function, configuration, and check unique to this first run there;
- reuse existing shared loaders instead of copying them;
- keep synthetic and current-export checks labelled `software_smoke_only`;
- write generated artifacts only under ignored `outputs/cebra_pilot/`;
- record versions, hashes, configurations, seeds, shapes, exclusions, failures,
  and negative results; and
- request independent review before extending the framework or running
  scientifically interpreted data.

Raw/PCA decoding, behavior audit, CEBRA-Time, path-conditioned CEBRA, graph-DTW,
and ANN comparison remain blocked or deferred by the formalization. Do not add
stubs that silently resolve those decisions.
