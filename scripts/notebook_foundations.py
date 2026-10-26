"""The experimental and measurement prerequisites, independent of any model run."""

from __future__ import annotations


def foundations(md, code, root):
    """Return a reading chapter; no inputs, model state or external network access."""
    del code, root
    return [md(section) for section in SECTIONS]


SECTIONS = [
    r"""# Foundations — What experiment are we trying to understand?

This chapter supplies the experimental background needed to read the analysis. It
assumes familiarity with ML but no prior hippocampal recording experience. Its facts
come from the workspace's recorded dataset inspection and upstream processing code;
its diagrams and small examples are **schematics**, not new observations.

The study asks what task information can be recovered from neural activity during a
cue, and whether a learned representation offers a useful, defensible description.
The original stronger question concerned the subsequently observed **path beyond
start and goal**. Keep those questions separate: recognizing a destination does not
establish knowledge of the route taken to reach it.

Reading route: [research overview](00_research_guide.ipynb) → this foundation →
[worked numerical example](00b_worked_example.ipynb) →
[source construction](01_pseudopopulation.ipynb) → [baselines](02_pca_lda.ipynb) →
[CEBRA](03_cebra.ipynb) → [historical tests and evidence](04_study_evidence.ipynb).
The numerical example shows the actual arithmetic on invented values. The practical
chapters then expose those operations in the real workflow. Historical evidence is
read without reproducing private models.
""",
    r"""## 1. The task: cue first, navigation afterward

The local analysis code describes a first-person Unity virtual maze with four
internal pillars and six animal-image landmarks. The prior student's write-up
describes trials between distinct start and goal landmarks, giving `6 × 5 = 30`
ordered endpoint conditions. The same endpoints can permit different ordered paths.
Those are code/write-up descriptions; exact apparatus and behavioral instructions
have not all been independently confirmed for the recordings.

The working trial sequence is:

```text
previous successful trial       current trial (schematic, not to scale)
ends at landmark A
          │
          └─ inferred current start = A
              interval       cue                        navigation
                         ┌──────────────┐       ┌─────────────────────┐
                         │ ~1 s, goal B │       │ move toward goal B  │
                         └──────────────┘       └─────────────────────┘
                         marker 1B      marker 2B                  3B or 4B
                         cue onset      cue offset/nav onset       success/timeout
                         time 0         nominal time 1 s

cue analysis:            [0, .1) [.1, .2) ... [.9, 1.0) seconds
derived endpoint label:  A → B         observed path: recorded movement sequence
```

`B` is a categorical landmark digit, not a physical coordinate. Marker families
`1x`, `2x`, `3x/4x` designate events in the code; the final digit should agree within
one trial. The working start comes from the predecessor's successful goal. Therefore
the current label can depend on two source records even when the neural input uses
only one trial's cue. This is why the split audit tracks predecessor contributors.

The previous write-up reports a black interval between trials and that the previous
goal/current start image may remain visible behind the next cue. Consequently, a
start decoder could exploit recent sensory history; a goal decoder could exploit the
cue image. These are plausible competing explanations, not experimentally isolated
mechanisms. Later navigation is used to define a path target in the historical path
work, not silently included in the cue decoder's input.

**Known limits:** organism/species and subject count, exact hippocampal subfield,
controls, reward, timeout duration and recording simultaneity are not established
by the available metadata. Do not fill them in from filenames. The source for these
distinctions is the [dataset card](../docs/dataset-card.md); the diagram above marks
the nominal analysis window, not a new audit of individual trial durations.
""",
    r"""## 2. What a spike train measures

An extracellular recording begins as voltage measurements. Spike detection and
sorting assign candidate events to clusters; a **sorted unit** is the cluster whose
timestamps enter this analysis. Calling it a cell is convenient, but the timestamp
file does not establish the identity, morphology or isolation quality of a biological
neuron. Sorting and curation are upstream processing steps, inherited rather than
reproduced in these notebooks. The general sorting problem and its validation are
illustrated by [Rossant et al. (2016)](https://www.nature.com/articles/nn.4268); that
paper does not establish which sorter or quality thresholds this lab used.

For this analysis, the measurement object is a list such as
`[12.01, 12.07, 12.13, ...]` seconds on the neural clock. A **spike count** is the
number of timestamps inside a declared interval. A **rate estimate** divides that
count by the interval's observed exposure. Two spikes in 100 ms give `2 / .1 = 20`
spikes/s; two spikes in 200 ms give 10 spikes/s. Counts with unequal exposure are not
directly comparable as rates. The cue workflow models fixed-width counts, then
standardizes them; those standardized values are neither spike counts nor rates.

An observed zero is a measured interval with no detected spikes. An unrecorded unit
in another session is missing, even if its array slot is convenient to fill. Missing
values remain masked until construction supplies an actually recorded source block.
This distinction is analogous to an absent sensor versus a sensor reporting zero.

The 195-unit archive is **place-selected**. It describes a curated set, not a random
sample of all hippocampal neurons. Apparent performance or response frequencies
cannot estimate how common a coding property is across the entire hippocampus.
Within this dataset, place-, view-, goal- or conjunctive response descriptions remain
associations that can reflect correlated task variables, not uniquely identified
functions of a unit. The unit-selection and sorting criteria themselves remain
inherited/partly unresolved metadata.
""",
    r"""## 3. Four streams must agree about one trial

| Stream | What we use | What it does not establish alone |
| --- | --- | --- |
| Sorted spikes | Unit-specific timestamps, native milliseconds | What the subject saw or intended |
| Ripple | Neural-clock event codes/timestamps, native seconds | The full behavioral trajectory or semantic truth of a code |
| Eyelink | Event codes/times and explicit missingness for cue checks | Gaze-confound control when dense gaze samples are omitted |
| Unity | Ordered task markers and cumulative timing; historical full behavior additionally had positions | Neural activity or correct alignment merely because row counts agree |

The compact route retains all marker/delta rows needed for timing, but intentionally
omits dense position, heading and gaze. Its ordinal trial join, agreement checks,
success flags and timing tolerances constrain the analysis. Matching array sizes
alone would not prove identity or clock alignment. Missing Eye events are represented
with an observation mask so a placeholder zero cannot impersonate a real event.

To count a selected source's cue, convert its unit's milliseconds to the Ripple
clock's seconds and use absolute half-open edges. For onset `t0`, bin `i` counts
timestamps in `[t0 + i·.1, t0 + (i+1)·.1)`. Thus an event at exactly `.1` after onset
enters bin 1, not bin 0. The current compact reader preserves native precision and
duplicates; it does not round timestamps to force equality with older CSV exports.
The nominal first second and any additional cue tail are accounted for separately.

There is also a **different historical alignment path** in
[`ViewAndPlaceRepresentationNew`](../Hippocampus.jl/src/replay.jl). Its default
`trial_start=2` begins at cue offset/navigation onset and maps spikes to behavioral
samples, optionally restricting to fixations. A previously received export from that
path cannot supply cue activity just because it contains a trial dimension. The
fresh cue notebook reconstructs its own cue window instead. That distinction prevents
accidentally answering a cue question with navigation measurements.
""",
    r"""## 4. What is one observation, and why construct a population?

One source trial supplies the units recorded in its block. A conceptual source
table may look like this; dashes mean **unobserved**, not zero:

| Real source, known pair | Block A unit 1 | Block A unit 2 | Block B unit 3 |
| --- | --- | --- | --- |
| A-trial-7, 1→2 | its cue bins | its cue bins | — |
| A-trial-9, 1→2 | its cue bins | its cue bins | — |
| B-trial-4, 1→2 | — | — | its cue bins |

An assembled row takes one whole A trial and one whole B trial sharing `1→2`.
It carries all bins and unit columns from each selected block. It therefore provides
a complete condition-matched vector that was never observed simultaneously. Several
draws can reuse A-trial-7 or B-trial-4; constructed rows are not new recordings.

The implied approximation is a product of empirical **block response distributions
conditional on the matching label**. It can assay condition-level differences across
recorded features. It cannot identify their unmeasured cross-session covariance.
For a schematic example, simultaneous activity might produce only `(low, low)` and
`(high, high)`; independently drawing two blocks can also create `(low, high)` and
`(high, low)`. Those extra combinations do not show that the brain visited those states.

Same-session membership is not automatically verified simultaneity either. We preserve
the available within-source block structure and its provenance without upgrading its
metadata. Source trials are the provenance units; temporal dependence and shared
sessions still constrain statistical independence. Units and sessions are not counts
of independent animals.

The current panel must support every requested pair in every retained block and split.
The complete-support rule, after global contributor embargo, retains 27 units in ten
blocks. This is a specified conditional assay, not a claim that every study requires
all 195 units or that excluded recordings were biologically uninteresting.
""",
    r"""## 5. Labels can enter before the network sees a single example

Because assembly uses `(start, goal)`, evaluation requires those labels too. A strong
decoder means different **known-condition response constructions** are recoverable
on source-disjoint measurements. It is not yet a deployed predictor for one unknown
natural trial. That is true even for PCA or CEBRA-Time, whose transformation objective
does not directly optimize the endpoint label.

Think of an NLP corpus assembled by taking paragraphs from several documents of the
same known class. A model may recover the class of those synthetic documents, but
their score does not describe a single naturally authored document. Splitting the
synthetic documents after reuse could leak identical paragraphs across train/test.
Here we split real sources and their contributors first, then construct within splits.

Development was exposed during earlier research. Keeping it source-disjoint prevents
direct source reuse; it does not reverse past model selection or create an untouched
test set. Computational seeds vary construction and optimization, not the number of
independent experiments. The practical chapters preserve development values and
lineage across each declared comparison so a performance change cannot arise from
quietly swapping the evaluation rows.

There are therefore three separate gates: **measurement validity** (the row means
what we say), **computational separation** (fit only on allowed training inputs), and
**claim validity** (the design can answer the stated question). A perfect software
test covers only part of those gates.
""",
    r"""## 6. From counts to features to predictions

Use `R` for constructed rows, `U` for unit columns and `T` for cue bins. The assembled
count tensor is `R × U × T`. Pooled-bin standardization estimates one training mean
and scale per unit from `R·T` unit vectors. It reuses those numbers on development;
pooling does not make adjacent bins independent.

The **representation** maps each unit vector to features. Raw uses standardized unit
values; PCA finds directions of training variance; the pointwise CEBRA network learns
coordinates under a contrastive sampling objective. The **readout** maps these
features to an operational label. Its training objective is different from the
encoder's. A three-dimensional **display** then selects or projects coordinates for
inspection; it is a third object and need not contain everything the readout uses.

In the current biological configuration, a row contains ten bins and 27 units. Raw
whole-cue features have 270 columns. Eight PCA/CEBRA coordinates per bin yield 80
columns after concatenation. The historical 195-unit endpoint raw vector had 1,950
columns. None of those numbers means an 80-dimensional directly measured brain state.
Whole-cue concatenation preserves order; averaging bins would answer a different
question and erase that structure.

The next [worked example](00b_worked_example.ipynb) makes each transformation numerical.
Its projection and readout weights are deliberately supplied by hand, so arithmetic
is visible without presenting another fitted model as research evidence. Chapters
[2](02_pca_lda.ipynb) and [3](03_cebra.ipynb) then separate the first actual fitting
case into inspectable stages before repeating the fixed comparison grid.
""",
    r"""## 7. What a result would—and would not—answer

| Question | Observation needed | Interpretation ceiling here |
| --- | --- | --- |
| Can an endpoint be recovered? | Matched source-disjoint predictions, class support, baseline and errors | Association in the known-condition construction |
| Did optimization progress? | Actual objective/update history and sampler exposure | Behavior of the training objective; not necessarily improved decoding |
| Does the embedding collapse? | Spread/spectrum in full features plus predictive evidence | A diagnostic of numerical representation, not proof of a neural manifold |
| Did joint training help? | Matched cue readouts for declared cue-only/joint encoders | Effect of the bundled phase/exposure intervention in that study |
| Is there path information beyond endpoints? | Behavior-defined path variation within or controlled for endpoints, source-safe evaluation and appropriate controls | Requires the separate path assay; endpoint success is insufficient |
| Can we estimate a hidden neural state? | Defined dynamics/measurement model and distinguishability from observation histories | Not established by this decoder suite |

In this task, goal, cue image, start/previous goal, visual scene, time, movement and
session can covary. A model can exploit their shared information without separating
their causes. Restricting a path assay to fixed endpoints removes endpoint differences
as an explanation within that comparison, but it may leave too little independent
source variation or other nuisance differences. This is why the historical controls,
support failures and negative findings belong in the same story as favorable scores.

The working research ambition is useful task representations with clear measurement
and generalization boundaries. Formal observability would additionally require a
specified model of how hidden states generate observations over time. Source-traceable
notebooks provide computational transparency; they do not by themselves identify that
hidden system.
""",
    r"""## 8. Check understanding before running a model

1. A trial has `1B, 2B, 3B` and its successful predecessor ended at A. What are the
   analysis window and endpoint pair? **Answer:** the first declared second from
   `1B`, not the default Julia navigation window from `2B`; provisional pair `A→B`.
2. Why could an accurate goal decoder still fail to establish prospective path
   coding? **Answer:** it may recover the goal/cue condition; multiple paths share
   those endpoints and sensory confounds remain.
3. If ten synthetic rows reuse the same block-B source, how many B recordings did
   that add? **Answer:** one distinct source was used, regardless of row count.
4. Why keep a zero count and a missing value separate? **Answer:** zero reports
   observed activity in an interval; missing records no measurement at all.
5. Why may a CEBRA-Time pipeline still depend on labels? **Answer:** labels determine
   source matching before the temporal objective is optimized.

The evidence boundary is intentional: known facts are taught here, and unknown
experimental metadata stays unknown. The [worked numerical chapter](00b_worked_example.ipynb)
continues with concrete arithmetic. The [historical study chapter](04_study_evidence.ipynb)
shows how the competing explanations were tested, including which tests were negative.

**Sources for this chapter:** [dataset facts and evidence labels](../docs/dataset-card.md),
[prior-student write-up summary](../context/previous-student-analysis.md),
[current compact-data contract](../data/README.md),
[source/claim contract](../docs/analysis-contract.md), and the
[Julia alignment implementation](../Hippocampus.jl/src/replay.jl).
These links provide provenance; the reasoning needed for the next chapters is above.
""",
]
