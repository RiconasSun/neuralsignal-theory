# Prospective R1-CODE-1 Repair

Initial R1 sources/results remain immutable and gate remains FAIL.17tests
reported1failure and14errors; no prescribed model-grid fitting occurred.
The reset assertion requires bit-identical trial predictions. Its difference
8.67361738e-19is consistent with batch-dependent floating-point reduction
order; it is not evidence that the1e-10likelihood threshold was exceeded.
The seven runner tests each failed setup/cleanup under the sandbox temporary
root's nested-directory permissions. No oldtest/final data were involved.

Classification: implementation batch-determinism defect plus local temporary
fixture environment. Numerical gate never bypassed; no fixture winner inspected.
Fresh oracle/gradient evidence is still required before fitting.

Repair uses a new subclass with per-trial fixed-shape vector recurrence and
readout. Same equations, parameters, BPTT, scoring target, bounds, tolerances,
seeds and grids. All17original test methods/assertions run unchanged against
the repaired recurrent class; one batch-permutation regression is added.
Workspace-local temporary fixtures restore test execution without relaxing
permissions or changing tests' expected behavior. No output rounding and no
looser comparison assertions. Old source modules are unchanged on disk.

New namespace results/R1_code1 registers all added sources and every initial
R1 result hash before repaired execution. Tests/model fits are one-shot, with
all failures retained. All scientific holdouts remain locked; current scope
is controlled implementation validation only, not R2/cohort competition.
