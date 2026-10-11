# NUM3 Controlled Numerical Feasibility

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File paper11/scripts/reproduce-m4-num3.ps1
```

Registration hashes the specification, evaluator, oracle, tests, entrypoint,
prior gates and frozen split metadata before any new tests. Existing lock
mismatches stop; never silently overwrite a registration. Runtime is the frozen
M0 Python environment. No neural count arrays or final holdout are loaded.
Initial engineering attempt and lock remain preserved. The separate r2 lock
adds all Python script dependency hashes and identity enforcement before/after
tests, before fixtures and reporting. An equivalent searchsorted map replaces
quadratic-memory ancestor lookup. No numerical policy changed. The entrypoint
also generates figures, limitations and full regression logs before returning
the actual numerical gate exit status.
Three fixed fixtures,16 independent replicates and all power-of-two budgets
are mandatory under numerical_amendment3.json. Correctness precedes numerical
execution. Independent GH and finite-domain GL convergence plus a tail check
support reference sensitivity; they do not prove absolute discretization error.

FAIL exits nonzero and stops remediation, retaining M4 INCONCLUSIVE. The
lower-budget MC comparator cannot substitute for a failed final RQMC gate.
PASS here concerns controlled fixtures only; original real-data fitting and
numerical gates must still pass before M5-M7. Do not treat high ESS, reduced
variance or a synthetic PASS as a preferred neural regime.
