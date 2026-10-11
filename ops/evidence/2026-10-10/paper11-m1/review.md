# P11 M1 Review

Decision: scoped M1 upload allowed after final source verification.
P0: 0. P1: 0. No main promotion and no M2 execution authorized.

Reviewed source-pin acquisition, Git blob checks, metadata trial validity,
companion task/electrode alignment, anatomy classification, immutable splits,
training-only spike-count QC, subject coverage and one-command reproduction.
All 22 automated tests pass, with no skips. Papers 1-10, M0 code/results,
protocol and freeze remain unchanged. Only M1 data and evidence are new.

Initial real M1 run passed 17 tests. Added population-membership regression
exposed a comma/tab reader error; the FAIL gate and test report are retained.
Fixed the parser with explicit CSV/TSV separator handling and added its dedicated
regression, not a weakened expected result. Final replay distinguishes 630
unit-QC passing units from 613 eligible session-population units. Actual source
fusiform labels are kept explicit rather than classified as unknown. No split,
threshold or primary hippocampal classification was changed to obtain PASS.

Actual manifest freeze digest stays
d66ff7cc5dcadf3e0b7f18bfddcb50f3baa8fe59fc28b999910b3b66bd3e1eaa.
Acquired heldout bytes are never decoded for timing/rate QC. Row trial IDs are
used only to skip heldout content; a destructive fixture verifies malformed
heldout unit/timestamp values cannot influence training QC.

Data limitations are not suppressed: seven sessions without units, excluded
trials, small populations, unpaired sub-08/ses-05, session-local identities,
unresolved SU/MU and upstream session-wide sorting. M1 success is data readiness
under prospective thresholds; no model/scientific regime conclusion is claimed.
