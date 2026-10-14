# Family-Specific Training-Only Diagnosis

Native diagnosis completed 216/216 original-budget replays with exact agreement on objective, PG, iterations, objective calls, success/termination flags and bound hits. The independent native child exited 0 after 2909.843 seconds; isolation proof passed, capabilities were zero and profile cleanup returned 0x00000000. No validation or final data were exported to that role.

| Family | Original/replayed convergence | Maximum PG | Maximum independent FD error | Maximum independent objective error | Maximum iterations/calls |
|---|---:|---:|---:|---:|---:|
| Discrete | 4/72 | 0.02722291772072312 | 5.468762751675849e-10 | 1.0658141036401503e-14 | 52/61 |
| Continuous | 2/72 | 0.2554549342225719 | 2.523244570090677e-7 | 7.105427357601002e-15 | 157/169 |
| Hybrid | 0/72 | 0.06585542685816687 | 5.182807621658195e-10 | 7.105427357601002e-15 | 123/133 |

Every fit terminated on relative objective reduction, not exhausted iteration/function budgets. None hit bounds. The 210 failed first-order acceptance checks therefore remain failures despite solver success. Independent gradients, exact likelihood checks and all-coefficient ridge/exposure checks found no demonstrated mathematical implementation defect. Premature relative-objective termination is supported as a mismatch with the frozen PG criterion, not proof that conditioning, nonconvexity or local optima are absent.

The conditioning evidence records training-only context singular values, context condition numbers, log-history amplitude, initial/terminal gradients and complete evaluation/accepted-step histories separately for CA1/DG. It is not a full parameter-Hessian audit or a global-optimum certificate. Dynamics use -LL/(trial x bin) plus ridge times all dynamical coefficients squared/2; the baseline intercept-exclusion rule does not apply to these frozen dynamic models.

All-coordinate independent checks cover 108 four-bin synthetic family/size/ridge/seed cases; an additional 36 six-bin Hybrid cases activate all five lags. The latter maximum FD error is 7.303711802020274e-11 and exhaustive-forward error is 4.973799150320701e-14. Original five frozen M4 checks also ran unchanged. Initial new-harness syntax and runner routing failures remain separate saved evidence, not counted as executed numerical categories.

The fixed new dynamics-only optimizer was prospectively registered after completed diagnosis: ftol=1e-10, gtol=1e-5, maxiter=2000, maxfun=80000. PG<=.001, bounds, seeds, ridge grids, architectures, offsets, partitions and selection rules remain unchanged. The original failure is not reclassified.

For future checks only, independently validated integer-factorial caching preserves exact PMF/likelihood values and original oracle bytecode; above the cache range it falls back to the original calculation. No count-domain restriction or numerical tolerance change is introduced. The active original replay used the original oracle throughout.

An overly broad optional compile command traversed an unused bundled Tcl Python file and failed on its legacy indentation. The error is preserved. Registered runtime files had zero SHA mismatches; 3063 newly generated cache files in this mission's own runtime copy were removed with checked literal paths. Scoped compilation of 27 own files and zero-extra/runtime-SHA revalidation passed. No model source, data, frozen dependency bytes or scientific criterion was changed to address that diagnostic error.

No new M2 source vectors were decoded, no M3 or offset fits were repeated, and no final neural data or final evaluation were exposed. Numerical diagnosis is not model preference or biological validation.
