# Round2 decision — 2026-09-08, after Round1 CV and BEFORE Round2 fits

Exploratory methods result only. Biological export approved and completed; no originaltest evaluation. Historical development-validation predictive outcomes have NOT been computed/viewed in this study.

## Completed Round1

Run: /home/hongyi-home-lab/neuro_science-path-autoresearch-20260908/outputs/path-preprocessing-autoresearch-20260908/biological-20260908T115508Z/round1/

18 frozen representations ×5 fixed endpoint panels ×3 inner folds =270 fits, seed0,128train rows/class. All selected recipe fits converged; all eligible training sources actually used in its matched assemblies. Export:188real sources,49selected units/13sessions,756unit-source observations/7560native bins, zero forbidden rows yielded; fullcue/tail count conservation passed.

CV-best representation: t1_raw_rate_variance_floor_l2_0p1.
- Equal-panel/equal-fold CV delta logloss =+0.0738615811; logloss0.6192855994; BA0.6636831276.
- Train logloss0.2896463076; sizable remaining train/CVgap0.3296392919.
- EndpointCVdelta:2->1 -0.173052;3->1 +0.299784;4->1 -0.116498;5->1 -0.128803;6->1 +0.487876. Only2/5positive; aggregate not broad consistency evidence.
- Matched standard scaling wholecue/raw:CVdelta-0.012603,trainloss0.272844,cvloss0.705750.
- Fivebins/raw/standard:CVdelta-0.449998,trainloss0.094731,cvloss1.143146. More temporal detail fit training much better but generalized worse in this screen.

## Hypothesis update and exact next intervention

Evidence motivates estimation-stability check, not a new target or network: variance-floor scaling improved this matched raw wholecue comparison; finerbins and compressive transforms did not win. This does NOT establish a biological noise model or prove the unique failure mechanism.

Apply EXACT frozen single axis: add lambda0.01 and1.0 ONLY to t1_raw_rate_variance_floor; keep original18candidate family andlambda0.1. Choose final recipe by seed0 innerCV across20. No other representation/target/bin/cellpanel/source selection. Every null later must choose its OWN basewinner and corresponding two lambdas, not merely reuse this observed choice.

No biological success claim until prescribed diagnostic/null/sensitivity audits complete. The original validation is exposed historical development data even though it remains withheld during this new adaptive loop.
