# Saved A Documentation

FAIL / DATA_INSUFFICIENT: external source support incomplete; spikes locked

A documentation gate PASS:3887/3887 primary fits,57 configurations,9 patients/23 sessions. This is not R2 scientific PASS, null validation or physical regime validation. No incomplete B nulls are interpreted. No cohort pruning or unknown-support zero filling.

Saved selection only; training-objective seed rule. Equal-session within patient, equal-patient population summaries. CIs/Holm-six copied without new inference; session/patient whole-trial intervals descriptive, not independent windows.

design_rank is the recorded FIRST-unit design rank only, not a global rank. Optimizer success (including ftol termination or nit1) does not establish small gradient or global optimality; see full diagnostics.

Reproduce saved-only: `python -B paper11_v2/scripts/r2_development_report.py verify` then `python -B paper11_v2/scripts/r2_development_report.py report` once after registration; existing report outputs are never overwritten.
