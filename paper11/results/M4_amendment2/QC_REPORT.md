# M4-NUM-2 Proposal Stage: FAIL / INCONCLUSIVE

No revised real hippocampal evaluation or full cohort was performed.
All results below are controlled algorithm fixtures, not experimental findings.
Original M0-M3 gates/splits and M4/NUM1 failures remain unchanged.

Implemented q_i=0.9 shared state Laplace guide +0.1 exact ancestor prior.
Weight numerator retains exact ancestor-specific Gaussian transition and Poisson
count likelihood. Full mixture density in denominator; initialN(0,I) correction
and state correction explicit. Production state proposal equals prior; alternative
state proposal verified analytically/numerically in a fixture.
Predictive moment approximation only constructs q, never changes the target.

13 implementation/formula tests PASS: independent SciPy Gaussian density,
analytic Gaussian-posterior constant weights, non-prior state correction, state
support, log-score/ESS, systematic resampling, Laplace curvature, causal sequences,
zero loading, full defensive-mixture density, and three fail-fast regressions.

Independent2D Gauss-Hermite recursion for switching Poisson dynamics uses
orders24/32. Controlled4-unit3-bin sequences,8192 particles and fixed seeds;
oracle gate maximum per-bin error/unit plus order shift<=0.001, coded before
first execution. This per-bin gate is stricter than real trial-mean scoring.
Finite quadrature agreement is sensitivity evidence, not absolute accuracy proof.

Corrected fail-fast reproduction: first K1/D2 seed1103 fails,
maximum per-bin error0.001736609669442446 >0.001; minimum ESS/N0.8296796225990829.
One completed replica means no replicate SD or confidence bound is identifiable;
JSON uses null, not zero or NaN. No favorable later replica replaces the failure.

Initial collector defect (P1) continued synthetic replicas after recording a
failure. Preserved audit/source/logs under attempts/initial-collection:16 replicas,
12 failing the per-bin gate; maximum error0.0023130716511430283. No real data
were evaluated. Corrected explicit early returns and three regression tests;
independent review found no remaining P0/P1 formula or control-flow finding.
Fixture, seed order, budgets, threshold and proposal unchanged during repair.

Historical replicate SD in later bins~0.00125-0.00142 nats/unit-bin, while
mean signed errors are smaller and mixed in sign. This is compatible with
finite Monte Carlo variability despite ESS~0.78-0.83; it does not prove lack of
bias, or show that real d2 degeneracy was resolved. Whole-sequence historical
K2 maximum mean error0.0013271479411232818 also exceeded0.001, so the limitation
cannot be attributed solely to the stricter per-bin criterion.

Registration: stopped amendment design records planned budgets/repetitions and
references. Full prospective real-evaluation activation was BLOCKED by the
preceding oracle gate. The JSON was created after the pilot failure and is
explicitly NOT a retroactive pre-oracle preregistration. No budget enlargement
or threshold weakening after observed failure. No Discrete/Continuous/Hybrid
competition, M5-M7 or final holdout access. Five historical scientific gaps
remain open, not administratively cleared. No NAP/CWP/primitives validation.

PowerShell entrypoint reproduces the oracle failure and exits1. Detailed sources,
runtime and hashes in qc_report.json; gate/claims/logs/tables/PNG/PDF included.
