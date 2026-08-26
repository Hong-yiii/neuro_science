# Handoff — CEBRA, Graph-Based Behavioural Geometry, and Navigation Latents

**Date:** 2026-08-24  
**Primary source:** Schneider, Lee & Mathis (2023), *Learnable latent embeddings for joint behavioural and neural analysis*, Nature 617, 360–368. DOI: 10.1038/s41586-023-06031-6.

---

## 1. Why this handoff exists

This note captures the current working understanding of **CEBRA**, especially the mathematical role of its aligned variables and a proposed extension for navigation tasks where behavioural similarity is better represented by a **graph or trajectory metric** than by ordinary Euclidean coordinates.

The core research direction is:

> Test whether cue-phase neural population activity is organized according to the structure of a future navigational trajectory, rather than merely current Cartesian position or simple start/goal labels.

This is a proposal derived from the discussion, not a claim made by the CEBRA paper.

---

# 2. CEBRA in one sentence

CEBRA learns a low-dimensional neural representation by using **time and/or behavioural variables to define which neural samples should be treated as positive versus negative pairs in a contrastive objective**.

The important part is not the CNN itself.

The key components are:

1. a neural signal,
2. a notion of behavioural / temporal similarity,
3. a positive-pair distribution,
4. a negative-pair distribution,
5. an InfoNCE-like contrastive objective.

---

# 3. The three aligned variables: \(s_t, c_t, k_t\)

The CEBRA Methods define three possible time-aligned variables.

\[
s_t = \text{signal}
\]

\[
c_t = \text{continuous context}
\]

\[
k_t = \text{categorical / discrete context}
\]

They are **not three mandatory inputs**. They are three kinds of information that may be available at time \(t\).

Typical neuroscience interpretation:

\[
s_t =
\begin{bmatrix}
r_1(t)\\
r_2(t)\\
\vdots\\
r_N(t)
\end{bmatrix}
\]

where \(r_i(t)\) is the activity of neuron \(i\).

Continuous context might be:

\[
c_t=(x_t,y_t)
\]

or velocity, joint coordinates, etc.

Discrete context might be:

\[
k_t \in \{\text{left},\text{right}\}
\]

or trial type, active/passive condition, reward, animal ID, brain area, etc.

### Why split continuous and discrete context?

Because they induce different sampling rules.

For a discrete variable:

\[
k_i=k_j
\]

can directly define a positive relationship.

For a continuous variable, one needs a metric or conditional distribution such as:

\[
\|c_i-c_j\|
\]

to determine which observations are behaviourally close.

This distinction is implementation-level rather than a deep constraint on what behavioural space must look like.

---

# 4. Mathematical core of CEBRA

## 4.1 Reference, positive, and negative samples

Take a neural observation:

\[
x=s_t.
\]

Define:

\[
y^+ \sim p(y\mid x)
\]

as a positive sample and:

\[
y^- \sim q(y\mid x)
\]

as a negative sample.

The scientific hypothesis enters through the definition of:

\[
p(y\mid x)
\]

and:

\[
q(y\mid x).
\]

For example, if position defines similarity, two neural states corresponding to similar positions are likely to form a positive pair.

---

## 4.2 Encoder

CEBRA learns:

\[
f_\theta:\mathbb R^N\rightarrow\mathbb R^d
\]

with \(d\ll N\).

\[
z=f_\theta(x).
\]

The paper generally uses temporal convolutional encoders for neural data, but the architecture is not the conceptual heart of CEBRA.

---

## 4.3 Similarity function

Most experiments use a normalized dot product:

\[
\phi(z,z')
=

\frac{z^\top z'}{\tau}.
\]

An alternative is negative squared Euclidean distance:

\[
\phi(z,z')
=

-\frac{\|z-z'\|^2}{\tau}.
\]

The choice of similarity function encodes assumptions about latent geometry.

---

## 4.4 Contrastive objective

For one reference \(x\), one positive \(y^+\), and negatives \(y^-_1,\ldots,y^-_n\):

\[
\mathcal L
=

-\psi(x,y^+)
+
\log
\sum_{i=1}^{n}
e^{\psi(x,y^-_i)}
\]

where:

\[
\psi(x,y)=\phi(f(x),f'(y)).
\]

Interpretation:

- increase similarity to the positive,
- reduce similarity to negatives,
- hard negatives receive larger gradients through the log-sum-exp term.

---

# 5. CEBRA modes

## CEBRA-Behaviour

Behavioural labels define the sampling structure.

Example hypothesis:

\[
\text{hippocampal activity is organized by position + direction}.
\]

This is **supervised / hypothesis-driven**.

---

## CEBRA-Time

Temporal relationships define positive sampling.

No explicit behaviour label is required.

This is better described as **self-supervised**, not fully unsupervised.

---

## Hybrid CEBRA

Time and behavioural variables jointly shape the representation.

---

# 6. What “consistent across runs” means

CEBRA does **not** claim that two independent runs produce numerically identical coordinates.

The theoretical notion is linear identifiability:

\[
f_1(x)\approx Lf_2(x)
\]

for some linear transform \(L\), under the relevant assumptions.

Thus two runs may produce rotated, reflected, or linearly distorted versions of the same underlying geometry.

This is a central advantage over embeddings whose geometry may vary arbitrarily between runs.

---

# 7. Why a graph-based behavioural space may make sense

A navigation task often has:

- walls,
- obstacles,
- junctions,
- one-way transitions,
- discrete action choices,
- routes that are close in Cartesian distance but far in reachable distance.

Therefore:

\[
d_{\text{Euclidean}}(i,j)
\]

may be a poor behavioural similarity measure.

A graph representation:

\[
G=(V,E)
\]

can instead define:

\[
d_G(v_i,v_j)
\]

as graph / shortest-path distance.

Example:

Two physical positions may be 20 cm apart but separated by a wall.  
Euclidean distance says “very similar”; graph distance says “far apart in navigational state.”

For a navigation representation, the latter may be more appropriate.

---

# 8. Graph-based CEBRA: minimal modification

The simplest extension keeps the CEBRA objective unchanged.

Only the **positive sampling geometry** changes.

Standard continuous-context version:

\[
d(c_i,c_j)=\|c_i-c_j\|_2.
\]

Graph-based version:

\[
d(c_i,c_j)=d_G(v_i,v_j).
\]

A possible positive distribution is:

\[
p(j\mid i)
=

\frac{
\exp\left(-d_G(v_i,v_j)^2/2\sigma^2\right)
}{
\sum_{j'}
\exp\left(-d_G(v_i,v_{j'})^2/2\sigma^2\right)
}.
\]

Then:

\[
d_G(v_i,v_j)\downarrow
\Rightarrow
P(j\text{ is positive}\mid i)\uparrow.
\]

The contrastive objective itself can remain unchanged.

---

# 9. For planning, graph node alone is probably insufficient

For a navigation task, a current node:

\[
v_t
\]

may not uniquely determine the relevant internal state.

At a junction, identical current position can lead to different future paths.

A more informative state might be:

\[
u_t=(v_t,g_t,a_t)
\]

where:

- \(v_t\): current node,
- \(g_t\): goal,
- \(a_t\): next action / chosen outgoing edge.

Or even:

\[
u_i=(\text{start},\text{goal},\text{planned path}).
\]

This matters especially if the neural recordings of interest are from a **cue / planning phase**, where the subject has not yet traversed the environment.

---

# 10. Trajectory-conditioned CEBRA

For trial \(i\), define:

\[
N_i = \text{cue-phase neural population representation}
\]

and:

\[
P_i=(v_1,v_2,\ldots,v_T)
\]

as the future executed trajectory.

The scientific question becomes:

> Are trials with similar future routes already represented similarly in cue-phase neural activity?

Define a route distance:

\[
D_{ij}=d_{\text{traj}}(P_i,P_j).
\]

Then:

\[
p(j\mid i)
=

\frac{
\exp(-D_{ij}/\sigma)
}{
\sum_{j'\neq i}\exp(-D_{ij'}/\sigma)
}.
\]

Encode:

\[
z_i=f_\theta(N_i).
\]

Train with the usual contrastive objective:

\[
\mathcal L_i
=

-\frac{z_i^\top z_j^+}{\tau}
+
\log
\sum_k
\exp
\left(
\frac{z_i^\top z_k^-}{\tau}
\right).
\]

The resulting inductive bias is:

\[
\boxed{
\text{similar future trajectories}
\Rightarrow
\text{similar cue-phase neural states}
}
\]

---

# 11. Candidate trajectory similarity metrics

Several choices should be compared rather than assuming one is correct.

## A. Shared-node similarity

\[
S(P_i,P_j)
=

\frac{|V(P_i)\cap V(P_j)|}{|V(P_i)\cup V(P_j)|}.
\]

Simple but ignores sequence ordering.

---

## B. Shared-edge similarity

\[
S(P_i,P_j)
=

\frac{|E(P_i)\cap E(P_j)|}{|E(P_i)\cup E(P_j)|}.
\]

Better for path structure because route direction and connectivity matter more directly.

---

## C. Graph-aware dynamic time warping

For trajectory sequences:

\[
P_i=(v_{i1},\ldots,v_{im})
\]

and:

\[
P_j=(v_{j1},\ldots,v_{jn}),
\]

use graph distance as the local cost:

\[
D(a,b)
=

d_G(v_{ia},v_{jb})
+
\min
\begin{cases}
D(a-1,b)\\
D(a,b-1)\\
D(a-1,b-1)
\end{cases}.
\]

This allows trajectories of different lengths while respecting navigation topology.

---

## D. Shortest-path / route-geodesic representations

Map paths to their graph-geometric structure and compare them using shortest-path statistics, branch choices, path length, or graph embeddings.

---

# 12. Important methodological warning

A graph-conditioned latent space **cannot by itself prove that the brain uses a graph representation**.

If the learning objective explicitly pulls graph-near samples together, a graph-like representation is partly induced by the method.

Therefore the correct experiment is **model comparison**, not one graph-conditioned CEBRA run.

At minimum compare:

\[
H_0:\text{shuffled labels}
\]

\[
H_1:\text{Euclidean position}
\]

\[
H_2:\text{graph shortest-path distance}
\]

\[
H_3:\text{start + goal}
\]

\[
H_4:\text{full trajectory similarity}
\]

and separately:

\[
H_5:\text{CEBRA-Time / self-supervised}
\]

where feasible.

---

# 13. Evaluation criteria

Do not judge the result only by whether a 2D / 3D visualization looks compelling.

Compare models using:

## 13.1 Contrastive goodness of fit

Compare converged objective values under controlled training conditions.

The original CEBRA paper uses the normalized value:

\[
L_n-\log n.
\]

Lower is better.

---

## 13.2 Decoding

Test whether the latent predicts held-out variables such as:

- goal,
- route class,
- next action,
- trajectory sequence,
- path length,
- chosen branch.

Use held-out trials.

---

## 13.3 Cross-run consistency

Train several random seeds.

Test whether representations agree up to linear transformation.

---

## 13.4 Topological robustness

If the environment has known topology, compare learned latent topology using persistent homology / cohomology.

Do this only where the behavioural topology makes a clear prediction.

---

## 13.5 Generalization

Important tests:

- new start-goal combinations,
- held-out route variants,
- possibly held-out sessions or animals,
- similar paths with different physical coordinates,
- physically close states separated by graph obstacles.

---

# 14. Strongest current research formulation

A clean hypothesis is:

\[
\boxed{
H:
\text{cue-phase hippocampal population activity is organized by future navigational trajectory structure}
}
\]

Operational version:

> If two trials contain similar future graph trajectories, then their cue-phase neural population activity should occupy nearby locations in a learned latent representation, beyond what is explained by start position, goal, or Euclidean geometry alone.

This is more specific than:

> “trajectory data exists in a higher-dimensional manifold.”

The latter is likely too weak because almost any structured data can be embedded into some latent geometry.

The scientifically useful claim is about **which behavioural geometry best explains the neural geometry**.

---

# 15. Recommended experiment matrix

| Model | Positive-pair geometry | Main question |
| --- | --- | --- |
| CEBRA-Time | temporal proximity only | What structure is discoverable without behavioural labels? |
| CEBRA-XY | Euclidean position | Is neural geometry mainly spatial? |
| CEBRA-Graph | shortest-path graph distance | Is navigational topology more explanatory than Cartesian space? |
| CEBRA-StartGoal | same / similar start-goal condition | Is the representation primarily task-condition based? |
| CEBRA-Trajectory | route similarity | Is future path structure represented? |
| CEBRA-Shuffled | randomized labels | Null control |

For each:

1. train multiple seeds,
2. match latent dimensionality where possible,
3. match training budget and architecture,
4. compare loss,
5. compare held-out decoding,
6. compare representation consistency,
7. inspect topology only after quantitative checks.

---

# 16. Suggested first implementation

Do **not** begin with a sophisticated graph neural network.

Start with the smallest intervention:

1. Build the environment graph \(G=(V,E)\).
2. Convert every executed path into a sequence of graph nodes / edges.
3. Compute a trial-by-trial trajectory distance matrix:

\[
D\in\mathbb R^{M\times M}
\]

for \(M\) trials.

1. Begin with a simple metric:
   - shared-edge Jaccard, or
   - graph-DTW.

2. Convert distance into positive-pair sampling probabilities:

\[
p(j\mid i)\propto e^{-D_{ij}/\sigma}.
\]

1. Keep the neural encoder and InfoNCE objective close to standard CEBRA.

2. Compare against Euclidean, start-goal, and shuffled baselines.

This isolates the key research question:

> Does changing behavioural geometry improve the neural representation?

If yes, then consider more sophisticated graph-native architectures later.

---

# 17. Open questions

### Data representation

- Is each cue phase represented by one neural vector or a short neural time series?
- How are pseudo-populations constructed across trials?
- Are trial counts sufficient to populate each route / start-goal condition?
- How many unique route families exist?

### Metric choice

- Should route similarity care about:
  - node overlap,
  - edge overlap,
  - sequence order,
  - direction,
  - path optimality,
  - future goal,
  - first branch decision?

### Confounds

- Are route and goal almost perfectly correlated?
- Are start and trajectory almost perfectly correlated?
- Does trial duration leak route identity?
- Does time within session correlate with condition?
- Can pseudo-population construction itself induce artificial geometry?

### Generalization

- Can a model trained on some route families decode unseen routes?
- Does the latent capture trajectory structure or simply memorize route IDs?

---

# 18. Main conceptual distinction to preserve

There are two different claims:

### Weak claim

> A supervised contrastive model can be forced to organize neural data according to path similarity.

This is almost guaranteed if enough relevant neural signal exists.

### Strong claim

> Path / graph geometry explains neural population structure better than plausible competing behavioural geometries, generalizes to held-out trials, and agrees with self-supervised structure.

The second claim is the scientifically interesting one.

---

# 19. Current best next steps

1. Formalize the navigation environment as a graph.
2. Enumerate all trials as graph trajectories.
3. Plot the pairwise distance matrices for:
   - Euclidean start/goal,
   - graph shortest path,
   - trajectory overlap,
   - graph-DTW.
4. Check how correlated these metrics are.
5. If two metrics are almost identical, they will be hard to distinguish experimentally.
6. Implement the simplest custom positive sampler.
7. Reproduce a normal CEBRA baseline first.
8. Run the model-comparison matrix.
9. Only after this, consider a graph neural network or more elaborate latent model.

---

# 20. Source-grounded points from the CEBRA paper

The following are supported directly by Schneider et al. (2023):

- CEBRA uses neural signals together with optional continuous and discrete context variables.
- Positive and negative sampling distributions are central configuration choices.
- The sampling scheme is the main mechanism through which behavioural / temporal structure shapes the latent.
- CEBRA can be hypothesis-driven, self-supervised / time-driven, or hybrid.
- Its contrastive objective is InfoNCE-like.
- The similarity function can be dot-product or negative squared Euclidean distance.
- Different independently trained models can be linearly identifiable / consistent up to a linear transformation under stated assumptions.
- The paper uses decoding, consistency, loss, and persistent cohomology to evaluate learned representations.
- Custom / domain-specific sampling distributions are allowed by the framework.

The following are **extensions proposed in this handoff**, not results from the original paper:

- graph shortest-path distance as behavioural context geometry,
- route-conditioned positive sampling,
- graph-DTW for trajectory similarity,
- direct comparison of Euclidean versus graph versus trajectory geometry for cue-phase navigation.

---

# 21. One-line project framing

> **Use CEBRA-style contrastive representation learning to test whether cue-phase neural population activity is better explained by future graph-trajectory geometry than by Euclidean position, start-goal condition, or temporal structure alone.**
