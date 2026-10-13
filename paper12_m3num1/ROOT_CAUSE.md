# Numerical Diagnosis

All 120 nonstationary original smoke fits were replayed under the original L-BFGS-B policy using only first-mouse development training A. Objective, projected-gradient and iteration values match the original recorded results exactly. All terminated via relative objective reduction before their iteration/function budgets despite PG above 0.001.

Independent unit-local scalar Poisson likelihood/factorial and ridge calculations verify the exposure denominator N*T and intercept exclusion. Central finite differences at 1e-5 and 1e-6 cover all coefficients of controlled fixtures and fixed prespecified sampled coefficients plus all intercepts at initial/terminal points of every real replay. Maximum real relative error is 4.320093505150169e-9, below the registered 1e-5 oracle tolerance. No implementation bug was demonstrated.

The sampled unit-local penalized Hessians reach condition number 13,551.398533679338. Duplicate own-history/population-history columns and correlated order/order-squared features are retained; ridge and all feature definitions remain frozen. Conditioning is a contributing numerical burden, not a reason to discard features or candidates. Terminal bound hits are zero. Active-bound KKT projection is independently tested synthetically.

Original objective histories were never saved. New histories are prospective diagnostic replays, not recovered original trajectories. All objective evaluations and accepted iterates are recorded as aggregate numerical diagnostics without exporting fitted parameters or neural arrays.

After completed native diagnosis, one prospective amendment sets ftol=1e-10, gtol=1e-5, maxiter=2000, maxfun=80000 for all nonstationary M3 fits. PG acceptance, bounds, all ridges, all seeds, normalization, splits and model definitions remain unchanged. Improved convergence must be demonstrated by the complete smoke; correctness of gradients alone does not establish convergence or a neural mechanism.
