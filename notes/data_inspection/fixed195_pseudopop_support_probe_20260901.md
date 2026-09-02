# Fixed-195 pseudopopulation support probe

Date: 2026-09-01  
Status: behavior/support necessary-condition probe; not neural evidence

## Question

Can the current split support a full 195-cell pseudopopulation for labels of the form:

```text
(start, goal, route_family)
```

without imputing missing session/cell blocks?

## Result

No, not under the current train/validation split.

The proof fails before route family is even added: no ordered `(start, goal)`
label has all 195 selected cells represented in both train and validation. Since
`route_family` is defined within `(start, goal)`, adding it can only reduce or
equal support.

## Inputs

```text
outputs/prospective_path_first_run/place195-all-sessions-20260830-v4/trials.csv
sha256: aa0dc3e402a8a3c3c0fa355c0342f5061314f2c571d2f96dfaecc94e69fcd223

outputs/prospective_path_first_run/place195-splits-20260830-v3/source_trial_splits.csv
sha256: b0ef8cce43c79d9e2b1ae0a804c7d48fefeb92469670f3031485d0009fb10ff3

outputs/prospective_path_first_run/place195-all-sessions-20260830-v4/units.csv
sha256: fca36f2927af13a10db3df2312ad51689cf9c7ec28740bb0682b40918f65368f
```

Probe output:

```text
outputs/prospective_path_first_run/place195-pseudopop-support-probe-20260901-v1/
```

## Filters

- Splits used for design: train and validation only.
- Locked test path behavior: not used.
- Current timeout trials: dropped.
- Endpoint-labelled subset: `success_after_success`.
- Neural activity: not used.
- Path samples/route families: not used; this is a necessary-condition check.

## Counts

| Quantity | Value |
| --- | ---: |
| selected cells | 195 |
| session/cell blocks | 58 |
| cells per session min / max | 1 / 8 |
| ordered `(start, goal)` labels | 30 |
| labels with all 195 cells in train only | 30 |
| labels with all 195 cells in validation only | 0 |
| labels with all 195 cells in both train and validation | 0 |

Best possible old-style `(start, goal)` subsets across both train and validation:

| Start | Goal | Sessions supported | Cells supported |
| --- | --- | ---: | ---: |
| 4 | 3 | 57 / 58 | 190 / 195 |
| 6 | 3 | 55 / 58 | 181 / 195 |
| 3 | 1 | 49 / 58 | 175 / 195 |
| 4 | 5 | 51 / 58 | 174 / 195 |
| 6 | 5 | 51 / 58 | 174 / 195 |

Worst old-style `(start, goal)` subset across both train and validation supports
150 cells.

## Interpretation

A full 195-cell training pseudopopulation is possible for old-style `(start,
goal)` labels in train only. It is not evaluable as a full-195 model under the
current validation split, because validation has missing session/cell blocks for
every ordered `(start, goal)` label.

Therefore a full 195-cell `(start, goal, route_family)` pseudopopulation cannot
be supported without imputation under the current split. Route families divide
start-goal trials into smaller groups, so their support cannot exceed the
start-goal support above.

## Consequence for the next design

Use the behavior-only route audit to choose one of these instead:

1. support-declared subset pseudopopulations, e.g. up to 190 cells for the best
   old-style label before route-family splitting;
2. a coarser route-family definition that keeps enough support, while accepting
   that full 195 still fails validation under this split;
3. a refrozen exploratory split stratified by session and verified `(start,
   goal)` if Hongyi wants a full-195 validation design, clearly labelled as a new
   exploratory split;
4. old-style `(start, goal)` pseudopopulation as a historical baseline, not a
   route-family proof.

Do not impute missing cells or silently drop sessions after seeing route/test
support.
