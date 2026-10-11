# M4-NUM-2 Requirement Baseline
User authorization: targeted observation-guided importance remediation;
proposal/oracle correctness first; freeze before revised real evaluation.
Prechange HEAD1fee7d1c1f67aee94b9f1cdbed92b620cc2925ac, clean test branch,
origin/test identical after fetch; origin/main absent. One active mission.
No M0-M3, split, threshold, previous failure or holdout changes permitted.

| ID | Atomic requirement | Verification | Status |
| --- | --- | --- | --- |
| R01 | Target-preserving guided proposal, latent/initial/state correction | Formula tests and independent review; not precision certification | VERIFIED |
| R02 | Normalization, log score, ESS, resampling, causal sequence correctness | Unit tests pass; controlled numerical oracle fails | IMPLEMENTED_UNVERIFIED |
| R03 | Freeze all numerical choices before revised data evaluation | Real evaluation not activated after oracle failure | BLOCKED_HUMAN_INPUT |
| R04 | Fair required seeds/configurations and unchanged scientific gates | Full evaluation prohibited by preceding failure | IMPLEMENTED_UNVERIFIED |
| R05 | Accuracy<=0.001 with independent repetitions/reference | First controlled replica exceeds threshold | IMPLEMENTED_UNVERIFIED |
| R06 | Five outstanding warnings investigated, no administrative clearance | warnings_audit.md; all five remain open | VERIFIED |
| R07 | Actual code/tests/logs/QC/claims/reproduction/provenance | 13 focused/97 regression tests; PowerShell correctly exits1 | VERIFIED |
| R08 | Critical failure STOP, no holdout or regime-validation claim | Fail-fast regression, no real evaluation, preserved original files | VERIFIED |

Baseline requirement count8; verified count4. No full mission PASS.

Plan: guided Gaussian approximation to count-conditioned predictive state
distribution, with exact per-ancestor prior/proposal density correction. Shared
state-specific Laplace guide economizes computation; defensive prior mixture
retains tails. Approximate predictive moments appear in proposal only, never
replace transition density in weights. Discrete states sampled from original
transition/initial prior; explicit correction helper tested for alternatives.
Validate analytic Gaussian fixture, independent Poisson quadrature and controlled
switching sequences before real evaluation. Synthetic fixtures never findings.
Then freeze budgets/references/seeds, all original training configs/seeds.
Smoke -> small -> full cohort only on every preceding numerical gate PASS.
Any required oracle/training/numerical failure stops, preserving INCONCLUSIVE.
