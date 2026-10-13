# Numerical recovery QC

Mission P12-M3-NUMERICAL-RECOVERY-1, base 98666f3. Scientific status: amended M3 PASS; M4 admission FAIL / INCONCLUSIVE; mandatory STOP.

- Original 120 nonstationary failures exactly replayed on development training only: objective and projected-gradient differences zero. Objective histories are prospective replays, not previously saved original histories.
- All 120 terminated on relative objective reduction before satisfying PG <=0.001. PG range 0.001749584006721426 to 0.061066324748139805. No terminal bound hits. Sampled maximum unit-local Hessian condition number 13551.398533679338.
- Independent finite differences: maximum recorded real sampled-coordinate relative error 4.320093505150169e-9. Real checks cover all intercepts plus fixed 16 sampled coordinates per fit at initialization and termination; synthetic checks cover all coordinates. Not an exhaustive real-data gradient audit.
- Registered amendment: ftol=1e-10, gtol=1e-5, maxiter=2000, maxfun=80000. PG acceptance, bounds, exposure normalization, intercept exclusion, grids and all seeds unchanged.
- Smoke: 126/126 converged; maximum PG 0.00027272890153967. Progressive four-mouse check: 504/504. Full: 1638/1638 across 13 mice; maximum PG 0.0004067067872125981. Reused 126 fits unchanged; new 1512. Admission elapsed 15781.436999999976 seconds; deadline not reached.
- Full gate links 13 completed native evaluations, exit 0, native denial proofs, no timeout and cleanup HRESULT 0. Aggregate receipt is not a separate new native isolation experiment.
- M4 pre-registered after M3; five required synthetic fixtures could not import the unchanged archived module. SyntaxError line 30; exit 1; unittest reports one import-error pseudo-test. No fixture completed and no real M4 trained. No retry or frozen-source patch applied.
- M2 physiological admission remains 13 development and 13 final mice. Current mission does not reassess admission or decode full-session source vectors. Previous trusted-custodian decoding is historical M2 evidence, not a new operation here.
- Analysis: training A only for diagnosis, permitted A/B development data for repaired fits. No source requests, extraction, C/D export, final neural evaluation, holdout-based tuning or model preference claim.

See per-fit JSON for objective traces, iterations, optimizer messages, gradients, parameter-bound counts, finite scores and computational cost. baseline_comparison.csv has 546 descriptive mouse/session/subfield/configuration rows, means over all three seeds; independent statistical denominator is 13 mice, not 546 rows or 1638 fits.
