2026-10-16T16:00:45.662728+00:00

# Prospective mouse-level statistics implementation

Before E or final D neural outcomes, implement the original three primaries in order D-B4,C-B4,D-C and three interpretation guards D-Bstar,C-Bstar,D-S. Allscores must be finite and paired on the same>=8mouse IDs/unit-bin denominators; no deletion/weighting by units/trials. Equalmouse mean, exact2^n sign enumeration using inclusive abs(mean) tails, three-test Holm for primaries and a separate3-test Holm forguards. Bootstrap10000wholemouse indices jointly across all6contrasts, numpydefault_rng130041, percentile.025/.975 with quantilemethodlinear. Preserve bootstrap draws/hash, allmouse gains, signs and leave-one-mouse-out means. Non-significance is not equivalence; sign-test null requires fair conditional signs/joint sign symmetry, not arbitrary mean-zero validity.

This helper reports numerical inferential summaries/statistical condition components only. Development E is exploratory and cannot validate claims or retune. Final claim classification additionally requires every applicable frozen control/sensitivity/coverage/temporal/Bstar condition and independent final review; no stats-only PASS. No finalDread/score is authorized by implementation tests.

Predefined synthetictests: exactconstantpositive p=2/2^n andallzero p1, inclusive ties, primary/guardHolmseparatefamilies with manualknownpvalues, pairedjointbootstrap sharedindices andfrozenseed, equalmouse/LOMO formulas, direction/75percent conditions, missing/nonfinite/insufficientmouse denial, exactguarddifferences and no claimwhenCIcrosseszero. No threshold/multiplicity/seed/CIalgorithm changes after outcomes.
