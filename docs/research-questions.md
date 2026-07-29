# Research Questions

## Primary Question

Can a Unity-based RNN navigation agent develop internal representations that can be compared meaningfully with neural coding patterns from hippocampal navigation data?

## Representation Questions

1. Which biological units and RNN hidden units show place-like selectivity?
2. Which biological units and RNN hidden units show visual, view, or gaze-related selectivity?
3. Which units show conjunctive place-and-view behavior?
4. Are conjunctive responses better explained by true interactions or by correlated marginal variables?
5. Do population-level representations support decoding of position, view, heading, goal, or task phase?
6. Are observed representations stable across trials, sessions, seeds, and analysis choices?

## Minimal Claim Ladder

Use the lowest defensible claim supported by the data.

1. Descriptive: this unit's activity is correlated with a variable.
2. Controlled: this relationship survives a stated control or null model.
3. Comparative: the same analysis finds a similar or different pattern in biological and model units.
4. Mechanistic: only make this claim with additional evidence about training, architecture, task constraints, or perturbations.

## Core Nulls And Controls

- shuffle spike or activation times within/around trials;
- shuffle labels for place/view bins;
- time-shift neural/model activity relative to behavior;
- occupancy-normalized rate maps;
- held-out trial cross-validation;
- GLM or encoding model comparisons with position, view, heading, action, goal, and trial time;
- repeated analysis across multiple RNN seeds/checkpoints when available.

## First Milestone

Produce one matched analysis on one biological subset and one RNN rollout:

- a shared data table or object schema;
- one place-like metric;
- one view/visual-like metric;
- one conjunctive metric or model comparison;
- at least one null control;
- figures and a short interpretation note.

