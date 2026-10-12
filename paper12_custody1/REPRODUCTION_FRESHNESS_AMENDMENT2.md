# Append-Only Saved-Replay Freshness Repair

Independent final review identified a P1:original replay checked the manifest
only at start,and its binder attached whichever manifest SHA existed later.
The original code,seal and actual successful test logs are preserved. Those
checks are not accepted as final candidate-bound certification.

New entrypoint:
`powershell -NoProfile -ExecutionPolicy Bypass -File paper12_custody1/reproduce2.ps1`

reproduce_saved2 pins the starting manifest SHA,checks every public input,
rechecks the same manifest/files at completion,and records both SHAs.
finalize_evidence2 requires the identical starting/ending SHA and revalidates
all inputs at binding before publishing the fresh receipt. Original replay
receipts/logs are copied intact into results/reproduction_initial1/.

This repairs saved-evidence identity binding only. It does not rerun neural
extraction,live security probes,model fitting/nulls or final evaluation. The
scientific M2 gate remains FAIL / INCONCLUSIVE. No old gate is reclassified.
