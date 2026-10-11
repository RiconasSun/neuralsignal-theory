# M3 Baseline Reproduction
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File paper11/scripts/reproduce-m3.ps1
```
Requires scientific M2 PASS and its exact training feature/coverage identities.
All six frozen baseline families use Poisson counts and matched exposure; five
nonstationary families fit four predeclared ridge strengths. Stationary rate is
exact MLE. Optimizer fits training only, analytic gradients, maximum500 iterations.
Validation whole-trial scores support one-standard-error complexity selection.
Final test remains opaque. No scientific model-family verdict or inferential
statistic follows from this gate. Software and numerical choices are frozen in
data_manifest/M3/baseline_spec.json before validation count access. Selection
contract refuses post-access mutation; a repair requires a disclosed new version.
History resets per trial; set-size is unavailable during fixation. Timing is
conditioned on the known task schedule. Per-unit train design mean/std are used
unchanged on validation. BLAS workers fixed to one for reproducible resource use.
