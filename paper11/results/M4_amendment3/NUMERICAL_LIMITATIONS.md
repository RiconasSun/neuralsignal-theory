# Complete NUM3 Numerical Limitations

All entries concern controlled sequences, not biological evidence.
Registered UTC: 2026-10-11T16:38:46.221977+00:00.
Gate FAIL; Registered accuracy FAIL: original_K1_D2.

## Error Sources
- Monte Carlo variability: independent16-replicate SD, worst errors and numerical95% mean halfwidth reported per bin/budget.
- Reference uncertainty: independent GH and GL order shifts, cross-method difference and finite-domain tail sensitivity reported separately. No finite-particle reference used as truth.
- Log-score bias: mean-minus-oracle and prefix Jensen gap are recorded separately from SD. A confidence interval containing zero does not prove no bias. The Jensen gap is a diagnostic, not exact expected bias; bin evidence ratios are not unbiased likelihood estimators.
- Integration error: independent-method/order consistency supports only empirical discretization stability; no rigorous quadrature remainder bound. Conservative tail bound controls omitted prior-path probability with Poisson likelihood<=1, not discretization. Log sensitivity uses estimated prefix evidence, not a certified evidence lower bound.
- High ESS: instrumented for concentration, never accepted as likelihood accuracy proof.

## Registered Results
### original_K1_D2
Independent oracle: PASS.
Maximum reference sensitivity: 9.436895781820573e-15.
- mc N=8192: worst-bin bound 0.00658604427007; trial bound 0.00215891421581; max SD 0.0014795193894; min ESS/N 0.8074732.
- rqmc N=8192: worst-bin bound 0.00302634156795; trial bound 0.00125171283314; max SD 0.000653246450512; min ESS/N 0.81157927.
- rqmc N=32768: worst-bin bound 0.00147955011566; trial bound 0.000690157387878; max SD 0.000407373339722; min ESS/N 0.8086945.
- rqmc N=131072: worst-bin bound 0.00116865868477; trial bound 0.000336730411897; max SD 0.000299390107033; min ESS/N 0.82101203.

## Boundaries
Primary scientific metric remains trial-normalized joint predictive likelihood. The controlled procedure additionally requires per-bin precision; it does not redefine the frozen scientific metric.
Threshold0.001 unchanged. No seed/replica exclusion, target-density approximation, best-replica selection, post-failure budget increase or final holdout access.
Lexicographic RQMC particle ordering is not the Hilbert SQMC algorithm; published SQMC convergence rates are not asserted for this implementation.
Worst replica plus1.96 SD is an empirical frozen acceptance statistic, not a calibrated simultaneous95% confidence or prediction bound.
Three-bin low-dimensional oracles cannot establish accuracy on longer real trials, other fitted configurations or the full cohort.
A failed conservative verification procedure means accuracy not established under the registered procedure, not proof that0.001 is impossible for every numerical method.
On mandatory FAIL, numerical remediation stops; M4 remains INCONCLUSIVE. Prior failures remain immutable.

## Five Outstanding Scientific Warnings
- R05: full Discrete/Continuous/Hybrid competition incomplete.
- R06: complete selected-model freeze/locked holdout evidence incomplete; isolation retained.
- R07: subject-level statistics and required nulls not executed.
- R08: subject transfer and independent external compatibility/test not executed.
- R13: full-paper one-command reproduction not established. Controlled STOP reproduction is narrower.
None cleared administratively using improved variance, unit tests or upload.

Full regression exit code: 0. No NAP/CWP or preferred-regime validation.
