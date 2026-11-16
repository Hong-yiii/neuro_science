# Why this nine-class panel permits the source-budget and width study

**Metadata feasibility, verified November 16, 2026.** This dated explanation
adds design context to the frozen November 14–15 study. It changes no class,
roster, completed case, fitted result, notebook output or scientific conclusion.
The expanded class-count comparison below is retrospective metadata context;
it is not a decoding experiment or evidence that nine was an optimized class count.

## Fix the task size, then select its classes

A prediction class is an **ordered start→goal pair**, not an observed path.
There are six locations. Excluding start=goal leaves 6×5=30 possible classes.
The study fixed **K=9 before selecting class identities**, then selected:

`1→2, 1→4, 2→5, 2→6, 3→1, 4→6, 5→3, 5→4, 6→2`.

Every start and every goal appears once or twice in this list. More generally,
the selection requires each endpoint to occur between floor(K/6) and ceil(K/6)
times, separately as a start and as a goal. This balances endpoint incidence
in the task; it does not balance recorded sources or biological sampling.

Nine was a workable compact task: the selected panel retains a three-session,
17-column core with five training sources available in every session–class
pool. That same core supports the fixed 2/3/5-source budgets and the native
multisession comparator. Keeping the classes fixed and relaxing availability
to three training sources permits a 20-session, 83-column roster, with the
frozen 11-session, 49-column middle roster between them. These properties explain
what the design permits; they do not show that nine was uniquely best, largest
feasible, or chosen for a favorable decoding score.

## Why abundant totals still leave a small common population

The counts are eligible **current-source trial IDs**, after the frozen splits,
label/adjacency requirements and global development current/predecessor embargo.
They are not spike counts, constructed rows, or independent biological replicates.
All 58 recorded sessions contribute to the marginal counts below. Rows are
starts and columns are goals; a dash is an excluded self-pair, not a missing
measurement. Each cell is **training / development sources**.

| Start \ Goal | 1 | 2 | 3 | 4 | 5 | 6 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | — | 275 / 119 | 246 / 103 | 286 / 115 | 236 / 97 | 241 / 104 |
| 2 | 259 / 111 | — | 262 / 106 | 256 / 101 | 251 / 111 | 268 / 103 |
| 3 | 273 / 107 | 253 / 102 | — | 270 / 107 | 264 / 109 | 291 / 114 |
| 4 | 244 / 102 | 246 / 97 | 264 / 113 | — | 275 / 122 | 275 / 117 |
| 5 | 266 / 113 | 253 / 109 | 275 / 120 | 275 / 114 | — | 249 / 98 |
| 6 | 251 / 112 | 261 / 106 | 258 / 105 | 265 / 113 | 273 / 115 | — |

These marginals are already nearly flat: 236–291 training and 97–122 development
sources per pair. The most frequent training pair, 3→6 (291 / 114), is **not**
selected. Choosing the most common pairs is not the implemented rule.

The next grid counts sessions that individually supply **at least five training
and one development source for that one pair**, out of the same 58 sessions.
It does not count sessions that jointly support an entire panel.

| Start \ Goal | 1 | 2 | 3 | 4 | 5 | 6 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | — | 28 | 25 | 34 | 22 | 21 |
| 2 | 25 | — | 28 | 31 | 25 | 29 |
| 3 | 32 | 24 | — | 30 | 25 | 33 |
| 4 | 26 | 23 | 28 | — | 33 | 32 |
| 5 | 28 | 28 | 31 | 32 | — | 28 |
| 6 | 26 | 31 | 30 | 31 | 28 | — |

Every pair individually has substantial support, but the supporting sessions
need not coincide. **A usable session must meet the threshold for every selected
pair. One deficient pool removes that session's entire recorded column block.**
Extra sources for another pair, or in another session, cannot supply the missing
response for that session and class. Allowing a different column roster for each
class would change the construction and expose class-dependent missingness.

Let t[s,c] and d[s,c] be eligible training and development source counts, and
u[s] the session's recorded column count. For class panel C and training minimum m,

```text
A_m(C) = intersection over c in C of {s : t[s,c] >= m and d[s,c] >= 1}
W_m(C) = sum of u[s] over sessions s in A_m(C)
```

Thus large sums over sessions do not guarantee a large all-class intersection.
For the chosen nine pairs, the five-source intersection is just S16, S27 and
S34: 3 sessions / 17 columns. The three-source intersection is 20 sessions /
83 columns. The archive's 195 recorded columns cannot all enter this complete
panel merely because each pair has many sources in aggregate. This support
sparsity is distinct from neural firing sparsity and from the later reuse of
eligible sources to construct more rows.

## The exact selection rule

At each supplied, fixed K, the study's `select_panel()` enforces the class count
and endpoint-incidence bounds, then:

1. Maximizes W_5(C), the recorded width with five training and one development
   source in every selected pool.
2. Holds that optimum fixed and maximizes W_3(C), requiring three training and
   one development source in every selected pool.
3. Holds both optima fixed and takes the lexicographically first class list.

The second width is therefore **conditional on the five-source optimum**, not
the independent maximum possible at three sources. The objective weights recorded
columns, not session count. Selection uses source availability and recorded
column metadata only; no neural features, decoder scores or spatial tuning enter.
Exposed development availability does enter eligibility, so this does not create
a pristine test set.

## Other fixed class counts under the same rule

The following newly verified frontier applies that same hierarchy separately
at each K. Every gate also requires at least one development source per selected
pair. Entries are **sessions / recorded columns** for the returned panel.

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
five-source gate. Those panels cannot provide the same multisession core for
the native comparison and shared 2/3/5-budget study. This does **not** mean that
single-session source-budget fitting is impossible, or that every alternative
panel of those sizes lacks a multisession cohort: maximizing width does not
maximize session count. The returned K=18, 24 and 30 panels have no five-source
session. With all 30 classes, no session even has three training sources in
every class (and the required development support).

K=8 has a slightly wider optimum than K=9: 19 then 95 columns. K=6 admits
108 columns at the three-source gate, but every endpoint then has degree one:
knowing the start alone, or the goal alone, determines the pair. This helps
explain the desire for a less degenerate endpoint task, without making nine a
mathematically optimal class count. Panels at different K are selected
separately and need not be nested; the frontier is not a monotonic learning
curve or a proof of universal panel infeasibility.

## What endpoint balance implies for the metrics

For an endpoint-only deterministic rule, all classes with the same start
receive the same pair prediction. At most one class in each of the six start
groups can be correct. Its pair balanced accuracy is therefore at most **6/K**;
the same argument holds for goal-only rules. A randomized rule has the same
ceiling in expectation. For K=9 this is 6/9; for K=10 it is 6/10; for K=6 it is 1.
These are algebraic task properties, not fitted baseline scores or evidence
that an observed neural decoder relies on a particular endpoint.

The primary arms construct 16 training and 8 development rows per pair.
Equal true-pair counts make pair accuracy equal pair balanced accuracy on each
such split. The separate start and goal heads have unequal class counts:
an endpoint used in two pairs has twice the rows of one used in a single pair.
Their accuracy and balanced accuracy need not coincide. A larger K would also
change the uniform pair reference to 1/K, so none of these metadata rows is a
decoding result comparable to the published nine-class scores.

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
explicit execution checks, not a general filesystem sandbox. The frozen design
and input hashes were unchanged afterward.

To repeat only this metadata verification, use a fresh receipt path:

```sh
PYTHONPATH=src:. PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 \
  python docs/experiments/source-reuse-width-20261114/verify_class_panel_20261116.py \
  --output work/class-panel-20261116/metadata-verification-new.json
```

The original [protocol](protocol.md), [design](design.json), completed 48-case
[results](README.md), source notebooks and published executed outputs remain
the evidence for the experiment. This note supplies the missing construction
rationale and feasibility distributions; it does not revise that evidence.
