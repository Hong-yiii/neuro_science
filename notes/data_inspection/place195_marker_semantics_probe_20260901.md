# Place195 marker-semantics probe

Date: 2026-09-01  
Status: exploratory data/code probe; enough for exploratory path-family design, not a substitute for lab protocol provenance

## Question

Can the marker minor digit `x` in trial codes `1x 2x 3x/4x` be treated as the current goal/cue poster, and can the previous successful trial's marker digit be used as the current start poster?

## Inputs

- `outputs/prospective_path_first_run/place195-all-sessions-20260830-v4/trials.csv`
- Unity header poster coordinates from native `RawData_T1-400/session_*.txt` files, e.g.:

```text
P1(-5,1.5,-7.55) P2(-7.55,1.5,5) P3(7.55,1.5,-5)
P4(5,1.5,7.55) P5(5,1.5,2.45) P6(-5,1.5,-2.45)
```

## Result

The current marker minor digit is strongly supported as the current goal/cue poster ID:

| Check | Result |
| --- | ---: |
| successful trials with Unity end positions | 23,200 |
| nearest end poster equals current marker digit | 23,200 / 23,200 |

The current start poster is supported as the previous successful trial's marker digit:

| Check | Result |
| --- | ---: |
| current successful trials with previous successful trial | 22,740 |
| nearest navigation-start poster equals previous marker digit | 22,740 / 22,740 |
| same previous/current marker among those rows | 0 |

If the previous trial is not required to be successful, this rule becomes noisier:

| Check | Result |
| --- | ---: |
| current successful trials with previous trial | 23,144 |
| nearest start poster equals previous marker digit | 22,856 / 23,144 |
| same previous/current marker rows | 404 |

## Working exploratory rule

For success-only path-family design:

```text
current goal_id / cue_id = current marker minor digit
start_id = previous trial's marker minor digit only when previous trial succeeded
```

Trials whose current outcome is timeout are dropped from the experiment for now.
When a true `(start, goal)` label is required, the cleaner primary subset is
`success_after_success`: current trial succeeded and the previous trial also
succeeded. First trials and trials following timeouts lack a clean previous-goal
start label unless lab protocol provides another verified start source.

## Remaining caution

This probe validates the rule against observed Unity starts/ends and code
comments. It does not replace formal lab documentation of the task protocol or
the mapping from poster numbers to poster identities.
