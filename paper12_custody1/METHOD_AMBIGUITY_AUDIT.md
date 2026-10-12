# Prospective Method Clarifications

The immutable curated protocol specified ridge values but not the objective
normalization. It specified a shared task offset for Discrete/Hybrid without
its fixed fitting recipe, and did not specify the Continuous fixed offset.
Independent implementation review flagged the first two omissions before
any real A/B analysis export or model fitting. They were not resolved by
retrospectively inheriting P11 defaults or selecting favorable results.

Direct human decisions, preserved as separate append-only registrations:

- M3_METHOD_DECISION1.json: per-unit-exposure training loss normalization;
  baseline intercept unpenalized; fixed offset ridge0.1,all11/23/37 seeds,
  arithmetic mean log-rate,training-only,no validation selection.
- M4_OFFSET_AMENDMENT1.json: same common offset in Discrete/Continuous/Hybrid,
  separate shared/model-specific complexity,unchanged grids/gates/selection,
  calibration-only final fitting,explicit residual task-effect limitations.

The original files, ambiguous definitions, M0/native-support limitations,
M1PASS and original M2FAIL are not edited or reclassified. Registrations do
not certify numerical feasibility, cohort admission or scientific findings.
