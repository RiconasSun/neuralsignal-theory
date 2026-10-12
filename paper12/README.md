# P12 M0 Audit Reproduction

This package is a stopped mouse metadata feasibility audit, not a completed
neural dynamics study. Scientific M0 admission remains INCONCLUSIVE for Allen
and the one IBL candidate. M1-M7 were not executed.

From the repository root:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\paper12\reproduce.ps1
```

The command verifies frozen prior-paper and metadata/source hashes; regenerates
all Allen coverage/support tables and corrected IBL identity/anatomy joins;
checks exact saved-result parity and executes the automated tests. Output is
under ignored `paper12/replay/`. Saved proofs are copied to `paper12/evidence/`.
Dependencies for offline replay: Python3.11, requests, numpy, h5py. Override the
runtime path with `-Python <path>` if necessary. No persistent execution-policy
change occurs. pyarrow was needed for the original column-selective public
Parquet access, not the offline replay.

This does NOT reconstruct missing raw clock/support witnesses or reproduce
unexecuted physiology, fitting, nulls, animal statistics or final validation.
Do not automatically rerun acquisition scripts: snapshots use exclusive creation
and scientific stopping rules. New public snapshots are not interchangeable with
this registered evidence. Both initial unpassed gate files remain immutable.

Key files: REPORT.md; MILESTONE_STATUS.md; CLAIM_AUDIT.md; registration.json;
results/gate_result.json; manifest.json. Full metadata source receipts include
URLs, UTC, byte counts and SHA256. NWB ranged bytes were not saved as raw data;
their offsets/hashes and decoded allowed metadata summaries are retained.

Missing metadata for admission: authoritative probe-specific raw observation
start/end/gap and clock mapping, matched-repeat support, per-session behavioral
missingness, and independently assessed anatomy uncertainty. Existing public
sync files are catalogued but were not decoded; no impossibility-of-recovery
claim is made. No additional dataset search or scientific rescue is active.
