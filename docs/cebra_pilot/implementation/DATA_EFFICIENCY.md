# Data-Efficiency And Sample-Size Notes

Date: 2026-08-26

Status: planning guidance, not a power calculation

## What “Data Efficient” Means Here

CEBRA has shown useful empirical performance across several neural datasets, but
neither the paper nor the public API provides a universal minimum number of
trials or neurons. For this project, data efficiency must mean:

> How quickly does held-out path prediction improve as the number of independent
> source trials increases?

The quantity of interest is the incremental held-out improvement

\[
\Delta_C = \mathcal R_0(C)-\mathcal R_1(C),
\]

where the baseline uses start and goal, and the neural model adds cue-period
population activity. A representation is more data efficient only if it reaches
a stable, positive held-out \(\Delta_C\) with fewer source trials under the same
split, target, decoder, and loss.

## Rows Are Not Independent Trials

A one-second cue sampled every 20 ms provides about 50 CEBRA input rows per
trial. Those rows help fit a temporal model, but they are repeated measurements
from one trial:

```text
300 trials x 50 cue bins = 15,000 model rows
                           but only 300 independent source trials
```

All bins and derived windows from one trial must stay in one split. Confidence
intervals, permutations, and learning curves operate on source trials or larger
blocks/groups, not individual bins or all pairwise distances.

## Coverage Arithmetic For 30 Start–Goal Conditions

The experiment has 30 ordered start–goal conditions. With a balanced 60/20/20
train/validation/test split, expected coverage is:

| Total source trials in one simultaneous group | Train per condition | Validation per condition | Test per condition |
| ---: | ---: | ---: | ---: |
| 400 | 8 | 2.7 | 2.7 |
| 750 | 15 | 5 | 5 |
| 1,500 | 30 | 10 | 10 |

These are averages, not guarantees. Imbalance, exclusions, timeouts, missing cue
bins, and successful-after-successful selection increase the required total.

A useful **coverage planning floor** is therefore about **750 balanced complete
trials per simultaneous recording group** if the goal is roughly five
validation and five test trials per condition. This is not a statistical-power
claim. About **1,500 balanced trials per group** gives substantially more room
for route variation, nuisance controls, and stable condition-level evaluation.

No sample size rescues an unidentifiable design. If paths are fixed by start and
goal, or matched high/low-overlap examples do not exist within nuisance strata,
collecting more repetitions of the same deterministic routes will not identify
H1a or the shared-path question.

## How Many Simultaneous Units?

There is no verified universal CEBRA neuron threshold. The software contract
requires at least two simultaneous units only to prevent a one-cell export from
masquerading as population data; that is not a scientific adequacy threshold.

Use the full curated simultaneous population, then construct training-only unit
subsampling curves, for example at increasing available unit counts. Report
held-out \(\Delta_C\) and uncertainty at each count. Unit count cannot substitute
for independent trials, and units assembled across sessions cannot restore
simultaneity.

## How To Estimate The Real Requirement

After adequate data arrives:

1. verify cue/path linkage and simultaneous groups;
2. freeze source-trial splits;
3. audit condition balance and within-condition route variation;
4. freeze the path target, loss, nuisance set, decoder, null, and success rule;
5. fit start–goal, raw-neural, PCA, and only then eligible CEBRA models;
6. build learning curves by reducing **training source trials only** while leaving
   validation and test sets fixed;
7. define required data as the smallest training count whose held-out
   \(\Delta_C\) is stable, exceeds the frozen null/effect criterion, and recurs
   across appropriate recording groups.

Power simulation should use pilot residuals and condition imbalance from valid
cue-population data. It cannot be estimated from the current one-cell navigation
export.

## What One Local Training Run Establishes

One intact current-export trial can test that real JLD2 counts pass the loader,
shape, CEBRA fit/transform, and save/load paths. It cannot estimate data
efficiency because it has:

- one selected cell, not a simultaneous population;
- navigation-period activity, not cue-period activity;
- one trial in the fit;
- no start, goal, or future-path target in the model; and
- no held-out independent trial.

The run is therefore a software/data-shape smoke only.

## Sources

- Schneider, Lee, and Mathis (2023), CEBRA:
  <https://doi.org/10.1038/s41586-023-06031-6>
- Official CEBRA documentation: <https://cebra.ai/docs/>
- Official sklearn API: <https://cebra.ai/docs/api/sklearn/cebra.html>
- Pilot estimands and gates: `../formalization.md`
