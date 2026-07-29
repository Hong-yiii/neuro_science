# RNN Unity To Neural Coding Project

Created: 2026-07-29

## One-Sentence Aim

Use a Unity-based RNN navigation environment as an artificial model system, then compare the model's hidden-unit representations with neural coding patterns observed in hippocampal navigation data.

## Current Framing

The project is about representational comparison, not primarily about inventing a new RL method.

The working bridge is:

```text
Unity task variables + RNN hidden activations
        matched to
behavior/gaze variables + biological spike trains
```

The useful scientific question is whether comparable analyses reveal place-like, view/visual-like, or conjunctive coding in both systems, and where the analogy breaks.

## Target Representations

### Place-Like

Signals that vary with the animal/agent's spatial position.

Potential operational tests:

- position-conditioned firing or activation rate maps;
- decoding position from population state;
- spatial information score;
- stability of place-like tuning across trials or task phases.

### View Or Visual-Like

Signals that vary with what the animal/agent sees, attends to, or has in allocentric view.

Potential operational tests:

- view-bin or raycast-bin tuning;
- gaze-informed visual scene tuning;
- decoding viewed object/wall/bin from population state;
- comparing visual selectivity after controlling for position.

### Conjunctive

Signals that carry both spatial and visual/view information, or whose response depends on a joint state.

Potential operational tests:

- joint place-view response maps;
- GLM or encoding models with position, view, and interaction terms;
- model comparison between additive and interaction models;
- selectivity that survives controls for marginal position and marginal view.

## Why The Comparison Is Tricky

The major risk is overclaiming. A hidden RNN unit and a biological neuron can both correlate with position without being the same kind of object.

Important confounds:

- position and view are strongly correlated in a constrained maze;
- heading, action, goal, reward proximity, and time in trial may explain apparent tuning;
- occupancy and sampling bias can create fake selectivity;
- a single RNN seed/checkpoint may be unrepresentative;
- an RNN may solve the task through a brittle strategy that does not resemble animal behavior.

## First Good Slice

A useful first deliverable should be small and defensible:

```text
one formatted biological subset
        +
one RNN rollout/checkpoint
        +
one shared analysis schema
        +
place/view/conjunctive classification
        +
null controls
        +
figures with conservative interpretation
```

This should come before broad claims, new model families, or large infrastructure rewrites.

## Pending Inputs

- formatted biological data from the lab;
- RNN/Unity rollout data or model checkpoint;
- exact observation/action/reward/task specification for the RNN environment;
- decision on whether analysis code should live in this parent repo or a separate project repo.

