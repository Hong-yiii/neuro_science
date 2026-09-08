# Previous Student Analysis Write-up

> **Historical source summary, not current project framing.** “Trajectory” here
> follows the previous analysis's terminology, often meaning the `(start, goal)`
> class rather than the observed path. Use
> [`docs/research-questions.md`](../docs/research-questions.md) for current path
> terminology and H1/H2, and [`docs/analysis-contract.md`](../docs/analysis-contract.md)
> for current data requirements.

Source reviewed: `/Users/hongyilin/Downloads/Analysis Write-up.pdf`
PDF title: `Analysis Write-up`
Length: 20 pages
SHA-256: `b27a11d424e087ddc1674d399e18cb93b93f86654cc5a5895b054ca936e8c465`
Reviewed: 2026-08-10

The PDF remains in Downloads and is not copied into the repository. This note
preserves its scientifically relevant content and separates completed analyses
from proposed future work.

## Experimental and Dataset Facts Added by the Write-up

- The task used six start/goal posters.
- Start and goal cannot be the same, yielding 30 ordered
  `{start poster, goal poster}` trial types (`6 × 5`).
- A recording session contained approximately 400 trials, or roughly 13–14
  repetitions of each trial type on average.
- The next trial's start poster was constrained to equal the preceding trial's
  goal poster.
- The cue phase lasted 1 second.
- Navigation followed cue offset. Analyses also used a broader window from 3
  seconds before cue onset to 2 seconds after cue onset, which included the end
  of the preceding navigation period, the inter-trial interval, the cue, and
  early navigation.
- The screen faded to black during the middle of the inter-trial interval.
- The previous goal/current start poster was visible at the end of the preceding
  trial and might have remained partly visible behind the cue image.
- The original navigation representation was described as a 40 × 40 place-bin
  resolution. For a preliminary Bayesian decoder it was downsampled to 5 × 5.
- November 2018 cue analyses used sessions `20181105`, `20181102`, and
  `20181101`.
- A larger pseudopopulation analysis used sessions from `20180702` through
  `20181105` and produced 314 pseudotrials across 233 cells.

The 233-cell pseudopopulation is not the same object as the current local list of
195 place-selected cell paths. The former was assembled across recording
sessions; the latter is a curated place-selective export list.

## Pseudopopulation Construction

The cells were not treated as one simultaneously recorded population. Trials
from separate recording sessions were grouped into artificial pseudotrials by
matching the ordered `{start poster, goal poster}` condition.

For each trial type:

1. the target number of pseudotrials was the 25th percentile of that trial
   type's count across sessions;
2. a minimum acceptable count was two-thirds of that target;
3. sessions below the target but above the minimum were bootstrapped up to the
   target;
4. sessions below the minimum were excluded for that trial type;
5. excess trials were dropped;
6. trials were paired across sessions by chronological occurrence within each
   trial type.

This produced 314 pseudotrials and 233 pseudopopulation cells.

This construction supports condition-level population analyses only under
strong exchangeability assumptions. It does not preserve real simultaneous
noise correlations, exact shared trajectories, or shared trial timing.
Bootstrapped duplicate trials must remain in the same validation fold to avoid
train/test leakage.

## Completed Analyses Reported

### Cue and inter-trial activity

- Firing rates were analyzed in 100 ms windows.
- Mutual information with goal identity was estimated after discretizing firing
  rates into four quartiles and min-max scaling MI within each cell for
  visualization.
- Mean goal MI peaked approximately 0.3–0.7 seconds after cue onset.
- PCA was fit across all pseudotrials/time windows; the first three components
  were visualized.
- Goal-related PCA separation was most apparent around 0.3–0.6 seconds after cue
  onset.
- LDA was used both for supervised visualization and classification.
- Separate LDA classifiers decoded start poster, goal poster, or the ordered
  start-goal tuple in each 100 ms window using 10-fold cross-validation.
- Goal decoding peaked around 0.3–0.6 seconds after cue onset and appeared to
  persist into early navigation.
- Start decoding showed weaker peaks near the preceding navigation end and cue
  onset.
- Cross-temporal LDA examined whether start/goal codes generalized across time.

### Start-goal interaction attempts

The write-up tested whether trajectory had a representation beyond additive
start and goal effects using:

- two-way MANOVA;
- per-cell multivariate linear regression;
- per-cell Poisson regression;
- demixed PCA with start, goal, and start-goal interaction marginalizations.

The student described MANOVA and regression results as inconclusive. The Poisson
analysis produced widespread significance that the student suspected was mostly
false positives. dPCA yielded interpretable start and goal components, but the
interaction component remained unclear.

### Cell-correlation analysis

Pearson cell-cell correlations were computed across pseudotrials separately for
each 100 ms window, followed by K-means clustering with four clusters. Apparent
co-active subgroups were described near the preceding navigation end and during
the 0.2–0.7 second post-cue period.

Because these are pseudopopulation cells from different sessions, these
correlations are not simultaneous biological noise correlations. They can
reflect condition matching, chronological pairing, bootstrapping, or session
structure and should not be interpreted as local circuits without a genuinely
simultaneous population.

### Simulation

A simulation generated nonselective, start-selective, goal-selective, additive
mixed, and conjunctive mixed cells. One example used 90 cells: 30 start
selective, 30 goal selective, and 30 nonselective. Simulated firing rates were
sampled from normal distributions and converted to nonnegative values with an
absolute value. LDA, linear regression, and dPCA were rerun as method checks.

### Navigation/place decoding

A Naive Bayes place decoder was drafted using position priors and per-position
firing-rate likelihoods. The original 40 × 40 place representation was
coarsened to 5 × 5. At writing time, pseudopopulation navigation data was not
available, so models were trained separately per cell on all available
navigation data, no held-out test was performed, and cell predictions were
combined by majority vote. This was a prototype, not a validated decoder.

## Proposed but Unfinished Work

- Build navigation-phase pseudotrials.
- Use dynamic time warping to align position/velocity trajectories within
  matched start-goal conditions, then warp neural activity correspondingly.
- Correct experiment-controller pseudorandomization so both start and goal are
  balanced.
- Predetermine blocks of 30 trials containing every ordered start-goal type once
  while maintaining the previous-goal/current-start transition constraint.
- Find better tests of start-goal interaction/trajectory coding.
- Refine correlation clustering and subpopulation interpretation.

## Methodological Caveats for Future Use

- Random 10-fold pseudotrial splits can leak bootstrapped duplicate source trials
  unless grouped by source trial/session.
- Pseudopopulations preserve condition means but not simultaneous covariance or
  within-trial population dynamics.
- Poster IDs are categorical. Encoding them as preference-ordered integers in a
  linear interaction model imposes an unsupported ordinal geometry.
- Shifting z-scored firing rates to be nonnegative does not make them Poisson
  counts; Poisson GLMs should use spike counts with an exposure/offset.
- Repeated per-cell/per-window significance tests need multiplicity control and
  held-out confirmation.
- Fitting dimensionality reduction to all trials before evaluation can leak test
  information unless fitting occurs inside training folds.
- Correlations among nonsimultaneously recorded pseudopopulation cells should
  not be interpreted as functional connectivity or mutual inhibition.
- The untested 5 × 5 Bayesian decoder results are exploratory only.

## External Code Reference

The write-up links the prior student's scripts at:

`https://github.com/josephchengyx/Hippocampus_Decoding`

A bounded read-only source inspection was performed on 2026-09-07 at commit
`2f12016c58472888b83298d163be1daaf5291a1e`; historical notebooks were not executed
against the missing original data. In `neurosci_2023_pseudopop.ipynb`, the custom
10-fold helper uses deterministic row modulo, not source-trial groups. The
pooled-bin cell 70 splits different bins of the same trial across folds; the
separate per-bin LDA cells 72/73 are different code paths whose bootstrap-source
reuse requires tracing. Do not generalize that pooled-bin issue to every
historical result. See the [CEBRA diagnosis and comparison note](../docs/reports/start-goal-cebra-diagnosis.md)
for the bounded audit and a fair source-safe comparison plan.

### Matched adaptation completed, 2026-09-07

The [autonomous endpoint study](../docs/reports/start-goal-autoresearch.md) now
includes separate start/goal/joint SVD LDA on identical 195-unit source-safe
arrays and ten 100 ms cue bins. Three-seed development goal accuracy peaks
at 81.25% in 0.4–0.5 s; joint LDA in that bin is 37.22%. Whole-cue SVD LDA
is 48.47% joint; PCA8/bin + logistic C=.01 is 83.61% joint. These are different
input/target comparisons, not historical accuracy replication or evidence
that LDA/PCA generally dominates CEBRA.

The report also includes cross-temporal goal readouts, shrinkage joint LDA,
and an explicitly modern factorized two-head comparator. It retains the
known-condition pseudopopulation and inspected-development caveats. The
student's original 233-cell selection, preprocessing artifacts and source-safe
historical folds remain unavailable. Notebook cell numbers above are zero-based
indices in the notebook JSON, not execution counters.
