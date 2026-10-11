# M4 Regime Training and Validation
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File paper11/scripts/reproduce-m4.ps1
```
Requires M0-M3 scientific PASS and unchanged source/input identities. All frozen
state/dimension grids and eight seeds are required. Common causal combined GLM
offsets are training fitted, validation one-SE selected and shared across families.
The exact HMM, continuous Poisson Gaussian dynamics and switching Poisson Gaussian
dynamics use true count likelihoods; Gaussianization only initializes latent
coordinates from training. Initial/process Gaussian covariance is fixed identity.
Variational ELBO is a training objective, never the predictive endpoint.

Exact joint HMM likelihood and joint particle-filter marginal count scores are
used for validation. Continuous/hybrid accuracy needs independent repetitions
and higher-budget reference; empirical discrepancy is not a proof of absolute
error. Tolerance, grids, numerical policy and diagnostics are frozen in model_spec.
A failed required candidate or estimator diagnostic stops before final test.
All negative fits are retained. This command does not on its own establish final
holdout advantage or a preferred regime. Full locked test evaluation requires
all fitting/validation gates to pass first; no M5 begins after a critical failure.
