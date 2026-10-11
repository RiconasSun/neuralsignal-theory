# R1 Numerical QC

Original R1 FAIL preserved, no controlled grid fits performed then. CODE-1 was
registered before evaluation; same17original assertions and1e-10score tolerance
plus one new determinism regression. No real experimental arrays loaded.

| Check | Actual Result |
| --- | --- |
| R1 tests |18/18PASS |
| Unique current R0+R1 suite |51/51PASS |
| Independent oracle cases |220 |
| Causal/reset checks |54 |
| Max Poisson score error |9.094947017729282e-13nats/unit-bin |
| Max exact-state score error |1.1102230246251565e-15nats/unit-bin |
| Max recurrent score error |4.440892098500626e-16nats/unit-bin |
| Frozen score criterion |<=1e-10nats/unit-bin |
| Max independent gradient error |3.555037817945528e-11; criterion1e-6 |
| Controlled fitted models |169/169converged |
| Maximum iterations |273of500 |
| Coefficient-bound hits |0 |
| Fitting time sum |6.453251700208057s, excludes tests/registration |
| Actual PowerShell replay |exit0 |

1stationary+60GLM+24discrete+36continuous+48hybrid; all seeds11/23/37,
ridge.001/.01/.1/1and specified family dimensions/state/lag grids retained.
Common combined GLM offset is preset ridge.1/seed11 on fixture training only;
not a winner selected from fixture scores. Extra/shared/total parameters and
observed unit-bin denominators recorded for every family candidate.

Oracles independently use scalar math Poisson, hidden-path enumeration and
scalar recurrent recursion; gradients finite-difference independent objectives.
Exact HMM and switching observed-history AR score before assimilating current
counts. Backward smoothing is used for training derivatives, not prediction.
All history/filter/state resets occur at trials. Continuous recurrence is
deterministic conditioned on causal observed history, not PLDS or hidden-latent
integration. Initial R1 numerical failure is not reclassified.

Boundaries: this is numerical/software verification in registered controlled
domains, not global optimization, biological preference, validation of NAP/CWP,
cohort prediction, statistical significance or independent external convergence.
Previously exposed development is exploratory. All original40trial and P11-v1
failures remain unchanged. Oldtest/external60/40 final values remain locked.
R2 must still establish real model convergence, matched subject-level comparisons,
null validity and source-supported independent physiological coverage.
