# CEBRA Pilot Verification Record

Date: 2026-08-25  
Scope: literature/API claims, statistical design, documentation coherence, and
formalization  
Implementation status: first approved software framework present; scientific analysis not run

## Independent Verification Performed

Three independent read-only verifiers reviewed the changed workspace before the
formalization was rewritten:

1. **Literature/API verifier:** local CEBRA paper, official CEBRA docs and
   publicly available repository source, graph/path metric claims, and the filed
   graph-navigation handoff. CEBRA is not installed locally, so installed-release
   behavior was not tested.
2. **Statistical/scientific verifier:** estimands, data gate, confounds, split
   hierarchy, dyadic dependence, nulls, graph preprocessing, CEBRA supervision,
   pseudopopulations, and claim ceilings.
3. **Documentation/coherence verifier:** authority order, moved files, stale
   absolute references, source provenance, directory rules, and cross-document
   consistency.

Targeted web source checks were also performed for CEBRA documentation, dynamic
time warping, and prospective/path-related hippocampal literature. No model,
embedding, or data analysis was run during that formalization review.

## Implementation Verification

A later implementation-stage researcher rechecked official CEBRA documentation,
PyPI metadata, and public release source. CEBRA `0.6.1` supports Python 3.12 and
the public sklearn API supports fit/transform/save/load, but exposes neither
explicit ragged trial-boundary metadata nor a fully implemented estimator seed.
The installed preflight therefore uses CPU, contiguous synthetic data, external
NumPy/Torch seeds, and no scientific determinism or trial-boundary claim.

Iterative independent method/code reviews were then performed:

1. pre-implementation review fixed the same-trial population gate, bin-by-unit
   axis, derivative-safe split hash, multi-segment metrics, exposure validation,
   and software-only current-export boundary before writing code;
2. first code review found and then verified fixes for package imports,
   session/group split metadata, output-directory confinement, complete-path
   classification, runtime package provenance, and save/load transform fidelity.

The executable trail is recorded in `implementation/REVIEW.md`. Nine boundary
tests, synthetic preprocessing, the current one-cell loader smoke, the CEBRA
`256 x 12 -> 256 x 3` synthetic smoke, and one intact local-data
`134 x 1 -> 134 x 3` smoke passed. The local run used one navigation-period cell
and one spike; it has no cue, population, path-decoding, or data-efficiency
interpretation. Reviewers retained the scientific H1 no-go. All artifacts remain
labelled `software_smoke_only`; no biological embedding was interpreted.

## Finding Disposition

| Severity | Finding | Disposition |
| --- | --- | --- |
| Blocker | Current local export lacks cue-period simultaneous population data, start/goal linkage, and the same trial's path | **Open scientific blocker.** Preserved as a hard stop in `formalization.md`, the plan, and `README.md`. Current data permits only loader/place/API smoke checks. |
| High | Historical handoff's implementation order could start graph-conditioned CEBRA before data, behavior, raw, and PCA gates | **Fixed.** Handoff filed verbatim under `sources/`, marked noncanonical/superseded; plan order is now data/split → behavior → raw/PCA → boundary-safe CEBRA-Time → optional supervised CEBRA. |
| High | Adaptive behavior audit occurred before immutable split reservation | **Fixed.** Canonical docs and plan now reserve and hash source-trial splits before metric/contrast selection; training/validation selects rules; test behavior remains untouched. |
| High | Purpose implied control beyond cue/session without a formal nuisance estimand | **Fixed.** `formalization.md` defines canonical \(\Delta_C\) and nuisance-adjusted \(\Delta_{C^+}\); wording is limited to available variables, with first-action sensitivity where possible. |
| High | Handoff proposed comparing losses across different CEBRA samplers | **Fixed.** Source retained only historically. Plan/formalization restrict contrastive loss to within-sampler diagnostics and require common held-out targets, decoder family, path loss, and nulls. |
| High | Path-conditioned sampler did not exclude self-pairs, derivatives, or validation/test samples | **Fixed.** Formal eligible set \(\mathcal A_i\) excludes self/source derivatives and uses training trials only; insufficient strata block the sampler. |
| Medium | Pairwise RDM entries could be treated as independent or include self/derivative comparisons | **Fixed.** Per-anchor matched statistic \(\delta_i\) uses a held-out, within-group eligible pool excluding self/source derivatives; inference operates on source trials/blocks/sessions/animals, not all matrix entries. |
| Medium | Graph cleaning had no primary default and split paths were under-defined | **Fixed provisionally.** Cleaning returns an ordered segment list, defines empty/single-node handling and edge-set union without bridge edges, splits invalid gaps, collapses repeats only for shape metrics, rejects nonadjacent transitions, and performs no primary interpolation. Every ordered metric must declare segment aggregation. |
| Medium | Sequential trials and successful-after-successful selection were omitted | **Fixed in contract/formalization.** Previous-trial ID, previous goal/success, trial index, inclusion reason, and block/session sensitivity are required. Actual metadata remains to be obtained. |
| Medium | Pooling across recording groups with different unit identities was ambiguous | **Fixed.** Primary neural estimation is within verified simultaneous group, followed by predeclared group-level synthesis. Cross-session raw vectors are not pooled. |
| Medium | Primary target, loss, null, and effect threshold could be selected after exploration | **Fixed as a gate.** One primary target/loss/null/effect criterion is frozen using training/validation before final testing; alternatives remain exploratory sensitivities. |
| Medium | Public sklearn CEBRA API was treated as if arbitrary graph samplers were a simple option | **Fixed.** Formalization distinguishes framework support from high-level API support and requires lower-level implementation/API review later. |
| Medium | `docs/cebra_pilot/` lacked local rules and a definitive filing structure | **Fixed.** Added nested `AGENTS.md`, `README.md`, formalization, verification record, and `sources/`. |
| Medium | Plan used stale absolute Downloads path and competing “authoritative” sources | **Fixed.** Verbatim source is repo-relative; canonical and pilot-local authority orders are explicit. |
| Low | `cue_id` was undefined | **Fixed.** `../analysis-contract.md` defines it as cue-period visual/instruction identity and requires verification of its relationship to goal. |
| Low | Project context date was stale | **Fixed.** Updated context date/provenance and linked this pilot directory. |
| Low | Copyrighted PDFs appeared as untracked authoritative inputs | **Fixed operationally.** Plan cites DOI/official docs rather than PDF authority; `/papers/*.pdf` is ignored and PDFs are not filed under this pilot. |

## Source Claim Verification

### Supported

- CEBRA defines reference, positive, and negative sampling distributions and an
  InfoNCE-style objective.
- The CEBRA framework permits custom/domain-specific sampling distributions.
- CEBRA-Time is self-supervised/time-contrastive with respect to behavior labels.
- CEBRA consistency is conditional and up to a linear transformation, not
  identical coordinates.
- Directed-edge sets and Jaccard dissimilarity are valid candidates for unordered
  route overlap, with order/repetition deliberately discarded.
- DTW provides a standard sequence-alignment recurrence.

### Supported only with qualification

- The inspected public sklearn CEBRA interface offers built-in conditionals; it
  does not expose an arbitrary precomputed graph-distance pair sampler as a
  simple argument. Lower-level extension may support one later.
- The public sklearn API does not expose explicit trial-boundary metadata, and
  an earlier public-repository source review found contiguous index offsets for
  time sampling. Safe multi-trial use still requires verification against the
  selected installed release and explicit boundary handling.
- Graph shortest-path distance is a standard graph quantity, but choosing it as
  local DTW cost is this project's proposal.
- Published rat hippocampal studies support biological plausibility of
  prospective/path-related activity, but differ in species, task, timing,
  recording state, and analysis. They do not validate this project's cue-period
  hypothesis.

### Unsupported and prohibited as conclusions

- “The brain uses a graph” based on graph-conditioned CEBRA.
- “CEBRA discovered a natural path manifold” when future path shaped training.
- Intention or causal planning from held-out decoding alone.
- Exact trial-specific path, covariance, or population-dynamics claims from a
  cross-session pseudopopulation.
- Biological–ANN shared mechanism from similar decodability or RDM geometry.

## Filed Source Integrity

Byte-exact source:

```text
docs/cebra_pilot/sources/cebra-graph-navigation-handoff.original.txt
```

Readable Markdown mirror:

```text
docs/cebra_pilot/sources/cebra-graph-navigation-handoff.md
```

SHA-256:

```text
a35fe6473a0abee25f34344123b3a9acfb9c1b7991e283e8fbc651e905f7862c  cebra-graph-navigation-handoff.original.txt
6e1c6cac3dce2e577270f3541fe8b2f70e92edbc736643fb79d37f24188e4171  cebra-graph-navigation-handoff.md
```

The original-text hash matches the external file at filing time. The Markdown
mirror has formatting-only normalization. Both contain the superseded
recommendations; corrections live in this verification record and
`formalization.md`.

## Residual Open Gates

These are not documentation defects; they are unresolved research prerequisites:

1. obtain cue-aligned, same-trial path-linked simultaneous population data;
2. verify cue semantics and its relationship to goal;
3. obtain previous-trial and success-selection metadata;
4. verify authoritative graph geometry/adjacency and hash;
5. reserve immutable trial/group-aware splits;
6. use training/validation behavior to select graph granularity, target, loss,
   null, and effect criterion;
7. verify adequate matched shared-path contrasts beyond endpoint/nuisance
   structure;
8. independently review any lower-level boundary-aware or graph sampler; and
9. obtain explicit approval before scientific analysis or the next implementation phase.

## Literature And Official Sources

- Schneider, Lee, and Mathis (2023), CEBRA:
  <https://doi.org/10.1038/s41586-023-06031-6>
- Official CEBRA sklearn API:
  <https://cebra.ai/docs/api/sklearn/cebra.html>
- Sakoe and Chiba (1978), dynamic time warping:
  <https://doi.org/10.1109/TASSP.1978.1163055>
- Johnson and Redish (2007), CA3 forward path sweeps:
  <https://doi.org/10.1523/JNEUROSCI.3761-07.2007>
- Pfeiffer and Foster (2013), future paths to remembered goals:
  <https://doi.org/10.1038/nature12112>
- Ferbinteanu and Shapiro (2003), prospective/retrospective hippocampal coding:
  <https://doi.org/10.1016/S0896-6273(03)00752-9>
- SciPy Jaccard definition:
  <https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.distance.jaccard.html>
- NetworkX shortest-path definition:
  <https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.shortest_paths.generic.shortest_path_length.html>

## Verification Verdict

**Documentation/formalization: conditional go.** The pilot now has a coherent
home, authority order, mathematical specification, source provenance, and gated
execution plan.

**Scientific analysis: no-go.** The current data fails the hard scientific gate.
The approved framework is software-smoke only until adequate cue-linked
simultaneous population data and review gates exist.
