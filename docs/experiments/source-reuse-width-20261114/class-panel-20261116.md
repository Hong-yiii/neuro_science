# Why this nine-class panel permits the source-budget and width study

**Every recording session included in the study must support every selected
prediction class.** A **session** is a recording block with its own trials and
recorded units. A **recorded unit** is an identified spike train obtained by spike
sorting; the analysis represents its activity as a column. A prediction **class**
is an **ordered start→goal pair**. The animal's detailed movement path is outside
this target.
The support requirement determines which recorded columns can enter both study
comparisons.

**Metadata feasibility, verified November 16, 2026.** This dated explanation
adds design context to the frozen November 14–15 study. Its class list, session
selection, completed cases, fitted results, notebook outputs and scientific
conclusions remain unchanged. The expanded class-count comparison below uses
retrospective source-availability metadata to assess which populations can be
constructed. How decoding changes with class count remains an open question.

## What each session must supply

The selected classes form the **class panel**. The included sessions form the
**session roster**, and their total number of recorded unit columns is the
population's **recorded width**.

A **current source** is a recorded trial identified in the frozen assignment
table. Its required preceding trial is tracked as a contributor. A
**session–class pool** contains eligible current sources from a particular
session for a particular start→goal pair, with training and development sources
counted separately. Development is the study's evaluation subset.

A **gate** is the minimum source count required in each pool. Every included
session must pass the gate for every selected class. A **source budget** is the
number of distinct training sources selected from each eligible pool. This
construction keeps the same recorded columns available for every class.

## Fix the task size, then select its classes

There are six locations. Excluding start=goal leaves 6×5=30 possible classes.
**K** is the number of selected classes. The study fixed **K=9 before selecting
class identities**, then selected:

`1→2, 1→4, 2→5, 2→6, 3→1, 4→6, 5→3, 5→4, 6→2`.

Every start and every goal appears once or twice in this list. An endpoint's
**degree** counts how many selected pairs contain it, separately in its start
and goal roles. The selection requires each endpoint to occur between floor(K/6)
and ceil(K/6) times; floor and ceil round down and up to whole numbers. This
balances endpoint incidence in the task. Recorded source counts and biological
sampling can remain unequal.

Nine was a workable compact task: the selected panel retains a three-session,
17-column core with five training sources available in every session–class
pool. That same core supports the fixed 2/3/5-source budgets and the native
multisession CEBRA comparator, which jointly trains a separate encoder for each
session. Keeping the classes fixed and lowering the gate to three training
sources permits a 20-session, 83-column roster, with the frozen 11-session,
49-column middle roster between them. Holding class identities fixed keeps the
prediction target unchanged. The source-budget comparison keeps all core columns;
the width comparison adds whole-session blocks while retaining the core. These
matches provide a common task and population reference for reading the later
decoding results.
Nine is one feasible design choice. Establishing a uniquely best or largest
feasible task would require a separate criterion and analysis; decoder scores
played no role in this selection.

## Why abundant totals still leave a small common population

The counts are eligible **current-source trial IDs**, after the frozen splits,
label/adjacency requirements and global development current/predecessor embargo.
That embargo excludes training trials whose current or preceding contributor
also contributes to development. The totals describe available trial identities;
spike counts and constructed rows are separate quantities, and distinct source
IDs can remain biologically dependent. All 58 recorded sessions contribute to
the totals below. Rows are starts and columns are goals; a dash marks a self-pair
excluded by the task definition. Each cell is **training / development sources**.

| Start \ Goal | 1 | 2 | 3 | 4 | 5 | 6 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | — | 275 / 119 | 246 / 103 | 286 / 115 | 236 / 97 | 241 / 104 |
| 2 | 259 / 111 | — | 262 / 106 | 256 / 101 | 251 / 111 | 268 / 103 |
| 3 | 273 / 107 | 253 / 102 | — | 270 / 107 | 264 / 109 | 291 / 114 |
| 4 | 244 / 102 | 246 / 97 | 264 / 113 | — | 275 / 122 | 275 / 117 |
| 5 | 266 / 113 | 253 / 109 | 275 / 120 | 275 / 114 | — | 249 / 98 |
| 6 | 251 / 112 | 261 / 106 | 258 / 105 | 265 / 113 | 273 / 115 | — |

These totals are already nearly flat: 236–291 training and 97–122 development
sources per pair. The most frequent training pair is 3→6 (291 / 114); the selected
list excludes it. Selection asks how many recorded columns can support all
selected classes together.

The next grid counts sessions that individually supply **at least five training
and one development source for that one pair**, out of the same 58 sessions.
Each cell describes support for its own pair. Complete-panel support requires
the same session to meet the threshold for every selected pair.

| Start \ Goal | 1 | 2 | 3 | 4 | 5 | 6 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | — | 28 | 25 | 34 | 22 | 21 |
| 2 | 25 | — | 28 | 31 | 25 | 29 |
| 3 | 32 | 24 | — | 30 | 25 | 33 |
| 4 | 26 | 23 | 28 | — | 33 | 32 |
| 5 | 28 | 28 | 31 | 32 | — | 28 |
| 6 | 26 | 31 | 30 | 31 | 28 | — |

The supporting sessions vary across pairs. **One deficient pool removes that
session's entire recorded column block.** Extra sources for another pair, or in
another session, cannot supply the missing response for that session and class.
Using different columns for each class would change the construction and
introduce class-dependent missingness.

Let t[s,c] and d[s,c] be eligible training and development source counts, and
u[s] the session's recorded column count. For class panel C and training minimum m,

```text
A_m(C) = intersection over c in C of {s : t[s,c] >= m and d[s,c] >= 1}
W_m(C) = sum of u[s] over sessions s in A_m(C)
```

The intersection contains only sessions that support all selected classes.
For the chosen nine pairs, the five-source intersection is just S16, S27 and
S34: 3 sessions / 17 columns. The three-source intersection is 20 sessions /
83 columns. Of the archive's 195 recorded columns, only those belonging to
sessions in the intersection can enter this complete panel. This restriction
describes incomplete class coverage within sessions. Neural firing sparsity
concerns activity values; source reuse concerns how often eligible trials are
used to construct rows.

## The exact selection rule

At each supplied, fixed K, the study's `select_panel()` enforces the class count
and endpoint-incidence bounds, then:

1. Maximizes W_5(C), the recorded width with five training and one development
   source in every selected pool.
2. Holds that optimum fixed and maximizes W_3(C), requiring three training and
   one development source in every selected pool.
3. Holds both optima fixed and takes the lexicographically first class list,
   using the fixed ordering of pair labels to break ties.

The three-source width is therefore **conditional on the five-source optimum**:
it is maximized among panels that already attain the primary optimum. Maximizing
three-source width independently could select a different panel. The objective
weights recorded columns; an objective based on session count could also give a
different result. Selection uses source availability and recorded-column metadata
only. Neural features, decoder scores and spatial tuning were excluded from
selection. Development availability enters eligibility, and that subset had
already been exposed during earlier work. The study retains this evaluation
limitation.

## Other fixed class counts under the same rule

The following newly verified table applies the same selection hierarchy
separately at each fixed K. Every gate also requires at least one development
source per selected pair. Entries are **sessions / recorded columns** for the
returned panel.

| Fixed K | At ≥5 training sources (primary width optimum) | At ≥3 training sources (conditional secondary optimum) |
| ---: | ---: | ---: |
| 6 | 4 / 18 | 29 / 108 |
| 8 | 3 / 19 | 23 / 95 |
| **9 — frozen task** | **3 / 17** | **20 / 83** |
| 10 | 3 / 17 | 13 / 58 |
| 12 | 1 / 8 | 15 / 66 |
| 15 | 1 / 8 | 12 / 51 |
| 18 | 0 / 0 | 10 / 44 |
| 24 | 0 / 0 | 2 / 12 |
| 30 | 0 / 0 | 0 / 0 |

K=10 selects the nine-class list plus **4→1**. Its five-source core remains the
same three sessions and 17 columns, while its three-source roster falls from
20 / 83 to 13 / 58. This particular nested comparison directly shows how one
additional class can remove session blocks from the wider population.

The returned K=12 and K=15 optima each leave one eight-column session at the
five-source gate. Source-budget fitting can in principle use a single session.
That session cannot supply the shared multisession core required for this study's
native comparison and 2/3/5-budget design. Whether alternative panels of those
sizes retain several sessions remains open: maximizing recorded width can select
fewer sessions.
The returned K=18, 24 and 30 panels have no five-source session. With all 30
classes, no session even has three training sources in every class and the
required development support.

K=8 has a slightly wider optimum than K=9: 19 then 95 columns. K=6 admits
108 columns at the three-source gate. Every endpoint then has degree one, so
knowing the start alone, or the goal alone, determines the pair. This supplies a
practical reason to consider a task with repeated endpoints. The choice of nine
remains a design decision. Panels at different K are selected separately, and
their class lists need not be nested. The table measures recorded width
under this selection rule. How decoding changes with task size, and which
alternative panels retain multiple sessions, remain open questions.

## What endpoint balance implies for the metrics

**Recall** is the fraction of examples from a given class predicted correctly.
**Pair balanced accuracy** is the mean recall across pair classes, giving every
class equal weight. **Accuracy** is the fraction of all predictions that are
correct.

For an endpoint-only deterministic rule, all classes with the same start
receive the same pair prediction. At most one class in each of the six start
groups can be correct. Its pair balanced accuracy is therefore at most **6/K**;
the same argument holds for goal-only rules. A randomized rule has the same
ceiling in expectation. For K=9 this is 6/9; for K=10 it is 6/10; for K=6 it is 1.
These ceilings follow from how the task groups classes. Fitted baseline
performance and an observed neural decoder's reliance on a particular endpoint
require separate evidence.

The primary arms construct 16 training and 8 development rows per pair.
Equal true-pair counts make pair accuracy equal pair balanced accuracy on each
such split. The separate start and goal prediction heads receive unequal row
counts across endpoint labels: an endpoint used in two pairs has twice the rows
of one used in a single pair. Their accuracy and balanced accuracy can differ.
The uniform pair reference is 1/K, so changing K changes the scoring reference
as well as the task. Comparing decoding with the published nine-class scores
requires fitted results for the respective tasks.

## Verification and preservation

[Verification code](verify_class_panel_20261116.py) called the study's actual
`metadata()` and `select_panel()` on `data/cue-source-v1`, with its original
source implementation and frozen design authenticated against revision
`a0ca80180e2bb52b90e499357d3d6965b26806da`. It independently counted the three
full-session matrices and directly recomputed session membership and width
from every returned panel. All expected values matched; each optimizer result
reported `optimal` and a zero gap. At K=9, the complete panel object and all
three rosters from `derive_rosters()` matched `design.json` exactly.

The [machine-readable receipt](class-panel-metadata-20261116.json) retains every
returned class list, session aliases, counts, input/code hashes and runtime
versions. Only the public manifest and two frozen assignment tables were read
from the compact data. The named fitting entrypoints, `study.materialize()`,
`study.prepare_design()` and `numpy.load()` were blocked; the data-access guard
rejected other compact files and local output reads. No Torch or CEBRA runtime
was imported, no notebook was executed, and no result was replayed. These are
explicit execution checks implemented through blocked calls and a data-access
guard. A general filesystem sandbox was outside this verification's scope.
The frozen design and input hashes were unchanged afterward.

To repeat only this metadata verification, use a fresh receipt path:

```sh
PYTHONPATH=src:. PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 \
  python docs/experiments/source-reuse-width-20261114/verify_class_panel_20261116.py \
  --output work/class-panel-20261116/metadata-verification-new.json
```

The original [protocol](protocol.md), [design](design.json), completed 48-case
[results](README.md), source notebooks and published executed outputs remain
the evidence for the experiment. This note supplies the missing construction
rationale and feasibility distributions. All original experimental evidence
remains unchanged.
