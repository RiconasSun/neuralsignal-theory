# Negative Result Interpretation

No experimental neural data were evaluated. On the first mandatory original
K1/D2 controlled fixture, all16 fixed seeds ran at every registered budget.
Both later fixtures are NOT_EXECUTED under STOP, not silently excluded or PASS.

At final131072 particles, raw maximum bin errors:
0.0000005901886399595213,0.0005372261328018269,0.0006401831552509396.
The final bin SDs are0.00000034314071562684757,0.0002993901070328084,
0.00026963037219849254. Last-bin raw error plus1.96 SD plus reference
sensitivity gives0.0011686586847694219 >0.001. This is an empirical conservative
acceptance statistic, not a certified confidence bound or actual absolute error.
Trial-mean statistic0.00033673041189710744 passes but does not satisfy the
additional registered per-bin accuracy criterion. Neither endpoint was changed.

At matched8192 budgets, maximum replicate SD is0.0014795193893954292 for MC
and0.0006532464505117267 for RQMC on this fixture. This is a local observed
variance comparison, not general superiority or a biological finding. Bin2 SD
is not monotonic:0.00028205891612107225 at32768 versus0.0002993901070328084
at131072. Larger budgets do not guarantee lower empirical error in every bin.
Final mean-minus-oracle signs are mixed; mean halfwidths include zero. This does
not establish absence of bias. Prefix Jensen gaps quantify finite-ensemble
log/likelihood convexity only, not exact log-score bias or unbiased bin ratios.
Minimum final ESS/N0.8210120285687262 is not an accuracy certificate.

First oracle convergence sensitivity~9.44e-15 dominates neither SD nor the
failed acceptance statistic. However independent quadratures can agree while
sharing unresolved discretization error. Tail-to-log conversion uses estimated
prefix evidence. No absolute-error theorem or rigorous remainder bound is claimed.
Implementation/reference consistency is improved; registered numerical accuracy
is still not established. Remediation stops; M4 INCONCLUSIVE is retained.

Saved result integrity is certified only by the separately registered auditor
and artifact_integrity_audit.json, not by the legacy report-only command.
14 focused/111 full/6 artifact tests pass; tests do not override scientific FAIL.
All M4/NUM1/NUM2 failures and initial NUM3 engineering attempt remain preserved.
