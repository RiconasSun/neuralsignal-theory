# M4-NUM-2 Proposal/Oracle Stop Reproduction

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File paper11/scripts/reproduce-m4-num2.ps1
```

Only algorithm fixtures are evaluated. No raw spikes, train/validation feature
arrays or final holdout are loaded. The entrypoint runs13 formula/implementation
tests and stops at the first failed controlled-sequence replica against independent2D quadrature,
then reports actual FAIL/INCONCLUSIVE and exits nonzero. It cannot silently activate
a real-data or full-cohort pipeline. Previous M4/NUM1 failures remain unchanged.
The original collector's16 replicas and source are preserved under
results/M4_amendment2/attempts/initial-collection; continuing after failure was
an execution defect, now covered by fail-fast regression tests.

Full registration for revised real evaluation was not activated because the
preceding oracle gate failed. numerical_amendment2.json records the stopped
design and future budgets, with explicit post-oracle creation disclosure; it is
not claimed to be a prospective preregistration of already-completed fixtures.
Oracle thresholds, budgets and seeds were coded before first fixture execution;
none was changed after failure. No favorable replicas removed.

Mathematics: state initial/transition prior is sampled, explicit state correction
is evaluated (zero in production). Each ancestor retains its own Gaussian prior
in the weight numerator. The q denominator is the full90/10 defensive mixture,
including ancestor-specific prior component; shared predictive-moment Laplace
Gaussian is only a proposal. Initial t0 uses exactN(0,I) prior correction.
Controlled quadrature is independent of Laplace/proposal implementation and
propagates the switching Gaussian/Poisson target on fixed Gauss-Hermite nodes.
Orders24/32 agreement is a finite-oracle sensitivity check, not absolute proof.

Important distinction: per-bin oracle gate is stricter than the real trial-mean
endpoint. Both per-bin failure and supplementary whole-sequence discrepancies
are disclosed; neither is a real hippocampal result. High ESS alone cannot prove
log-score precision. Do not raise the fixture budget or weaken assertions after
failure to obtain a PASS under this stopped execution.
