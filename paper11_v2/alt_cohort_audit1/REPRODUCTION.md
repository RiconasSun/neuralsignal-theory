# Reproduction

From repository root, in PowerShell:

```powershell
& .\paper11_v2\alt_cohort_audit1\reproduce-all.ps1
```

For Windows PowerShell5.1 with the observed script-policy restriction, use the
verified process-local invocation (no permanent policy changes):

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\paper11_v2\alt_cohort_audit1\reproduce-all.ps1
```

The first native5.1attempt's policy failure is preserved separately from retry.

For another runtime, supply -Python with a Python3.11+ executable. Live metadata
acquisition used requests2.33.0; saved replay/tests need only the Python standard
library. No network, API login, MAT reader or neuroscience library is used during
replay. Acquisition receipts are frozen; do not rerun acquisition into occupied
directories or substitute newly modified provider files for the saved snapshot.

Replay executes all controlled tests, verifies prior tracked files and append-only
operations history, validates registered code and saved receipts/artifact hashes,
and reproduces the original scientific gate. Exit0means faithful reproduction of
INCONCLUSIVE, not an external-cohort scientificPASS. No spikes, outcomes, models
or holdouts are read. Old P11 gates and split locks are byte-identical.

Evidence order:register.py register; audit.py register; controlled safety tests;
audit.py primary (preserved budget stop); documents.py registration/acquisition;
inventory_complete.py registration/tests/acquisition; finalize.py QC registration
and tests; derive.py primary gate; audit.py fallback; fallback_document.py version
registration/acquisition; published table metadata summary; saved artifact seal;
actual PowerShell reproduction. Supplemental acquisition registrations preserve
original protocol, uniform cohort denominator and scientific eligibility criteria.
