# P12 C-only saved-state seal recovery

Mission P12-C-SEAL-HOST-IMPORT-REPAIR-1, BASE 6cb50aaaffc1a89b4a6dddadb73e991d37c02448. This is host packaging and saved-state integrity recovery, not new calibration or final scientific evaluation.

Run from repository root in native PowerShell:

```powershell
& .\paper12_cseal1\reproduce.ps1
```

This verifies archived public evidence and the already-created protected complete saved-model seal. It never fits models, opens raw neural C/D arrays, releases D, or creates a second seal. Requires trusted local custodian access to the saved seal; an ordinary public clone lacks the protected fitted-state bundle.

Public evidence only:

```powershell
& .\paper12_cseal1\reproduce.ps1 -PublicOnly
```

Public-only integrity cannot independently certify unshipped protected coefficient arrays. The original complete-state numerical/provenance validator was run on protected saved states; its exact manifest, all1858original artifact hashes, source identities and audited receipt are retained in mission evidence. Reproduction check receipts are append-only and Git-ignored.

Synthetic engineering regression (no raw neural inputs or fitting):

```powershell
python -B -m paper12_cseal1.test_saved
```

This requires the original protected saved-synthetic fixture at paper12_controls1/jobs/saved_v2_9546086888504515998/exports/saved and writes new synthetic namespaces only. Historical failed synthetic runs are immutable evidence. See ops/evidence/2026-10-14/p12-c-seal-host-import-repair-1 for registration, fixed14-file source snapshot, independent reviews and complete result bindings.

Real recovery is intentionally non-repeatable: the public real_recovery_attempt.json and protected destination reserve a single attempt. Do not delete them, reuse the old partial seal, rerun real C fitting, or grant D. A future D mission requires separately validated human authorization and its original exactly-once controller; this mission grants no entitlement.
