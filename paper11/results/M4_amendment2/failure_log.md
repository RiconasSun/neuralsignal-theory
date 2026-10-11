# Failure/Repair Record
1. Formula tests10/10 passed; initial controlled fixture gate failed12/16
replicas. Original oracle source/audit/log retained in attempts/initial-collection.
2. Read-only review found P1: collector continued after mandatory failures.
Repair: return immediately on unit, quadrature or first replica failure.
Three new regression cases added; original assertions/budgets/seeds unchanged.
3. Corrected negative reproduction stops at first identical K1 seed1103; no
real evaluation activated. All13 proposal tests pass, numerical gate stillFAIL.
4. Report-layer single-replica SD initially emitted NaN/warnings. Corrected
to null (insufficient repetitions), no assertion/accuracy criterion changed.
No preferred regime, real d2 improvement or absolute-error proof follows.
