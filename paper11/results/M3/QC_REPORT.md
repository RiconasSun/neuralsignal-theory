# M3 Real Baseline QC

Gate PASS. 483 required candidates completed across 23 sessions and 9 subjects:
one stationary exact MLE and four ridge strengths for each of history, task,
timing, drift and combined Poisson GLMs. All required fits converged within500
iterations, finite predictive scores and gradient checks. Six automated tests
passed; real candidate scope, train/validation disjointness and identity checked.

Validation one-standard-error selection chose stationary in18 sessions, history
in4 and drift in1. These are validation selections, not final-test statistics or
evidence for a neural regime. Whole-trial scores rather than bins define the
selection standard error. Models keep integer counts, common exposure, causal
history resets and encoding-gated load. Train mean/std scaling applied unchanged
to validation. No final-test timestamps interpreted. No nulls or subject-level
inferential result. Full candidates/fits in sessions/*.json; nonselected results
are retained. Full validation table/figure in ../progress/.

Selection contract frozen before validation count extraction; no post-selection
baseline code or hyperparameter change. M4 uses the same combined causal GLM
offset for all families and counts its fitted coefficients in model complexity.
