# Final Preservation Readback

2026-10-11, branch test; base1fee7d1c1f67aee94b9f1cdbed92b620cc2925ac.
Fresh git fetch origin --prune exited0; HEAD and origin/test matched base.
origin/main absent (no repair or main mutation).

git diff --exit-code base -- paper11/protocol paper11/environment
paper11/results/M0 paper11/results/M1 paper11/results/M2 paper11/results/M3
paper11/results/M4 paper11/results/M4_amendment1 paper11/data_manifest/M0
paper11/data_manifest/M1 paper11/data_manifest/M2 exited0 with empty output.
Only pre-existing tracked changes are mission status and daily-operations;
new files scoped to NUM2 code, synthetic evidence, amendment and reproduction.

Python structured readback verified all six current source hashes in qc_report,
current oracle audit hash and archived initial oracle source hash. Strict JSON
parsing rejected nonfinite constants and passed all NUM2 JSON artifacts.
Full regression log:97 tests in2.555s, OK. Current oracle:13 tests exit0,
one first failed replica; no real data. Numerical entrypoint exit1 is expected
FAIL preservation, not a successful scientific comparison.
PNG inspected: nonblank error/ESS panels, visible threshold and synthetic-only
label, no clipping/overlap. No source or numerical-policy changes after replay;
closure edits only corrected documentation to actual audit values.
