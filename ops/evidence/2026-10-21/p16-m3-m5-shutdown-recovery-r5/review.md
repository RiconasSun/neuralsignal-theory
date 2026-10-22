# R5 append-only closure review process

This is a prospective environment repair and review process record, not final independent scientific acceptance. The original failure is immutable. FINAL_REVIEW.md will provide the independent final decision.

## Before saved-only run 2

```json
{
  "schema": "R5_SAVED_REPRODUCTION_ENVIRONMENT_AMENDMENT_V1",
  "registered_UTC": "2026-10-22T01:13:43.937476+00:00",
  "mission": "P16-M3-M5-SHUTDOWN-RECOVERY-R5",
  "base": "b7bb1227379462c2c7a1cef40ab0d0e99a6d020b",
  "status": "APPENDED_REVIEW_PROCESS_RECORD_NOT_FINAL_INDEPENDENT_ACCEPTANCE",
  "first_actual_native_exit_code": 1,
  "first_failure": "Windows PowerShell 5.1 could not auto-load Get-FileHash before entering frozen Python reproducer",
  "observed_cause": "Python subprocess inherited PowerShell 7 module search path; Windows PowerShell selected incompatible Microsoft.PowerShell.Utility 7.0 before built-in 3.1",
  "observed_preflight": "Unchanged environment: Get-Command Get-FileHash failed; child-only PSModulePath repair: actual native exit 0, Get-FileHash from built-in Microsoft.PowerShell.Utility at WindowsPowerShell v1.0 Modules",
  "exact_run2_command": [
    "powershell.exe",
    "-NoProfile",
    "-File",
    "C:\\Users\\85993\\Desktop\\codebase\\neuralsignal institute\\paper16_development_r5\\reproduce_saved.ps1"
  ],
  "only_child_environment_change": {
    "PSModulePath": "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\Modules"
  },
  "original_parent_PSModulePath": "C:\\Users\\85993\\OneDrive\\\u6587\u6863\\PowerShell\\Modules;C:\\Program Files\\PowerShell\\Modules;c:\\users\\85993\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\native\\powershell\\Modules;C:\\Users\\85993\\OneDrive\\\u6587\u6863\\WindowsPowerShell\\Modules;C:\\Program Files\\WindowsPowerShell\\Modules;C:\\Windows\\system32\\WindowsPowerShell\\v1.0\\Modules",
  "global_environment_modified": false,
  "source_files_modified": false,
  "scientific_retry_or_restart": false,
  "scientific_policy_changed": false,
  "new_fits_derivatives_scores": 0,
  "E_or_Final_access": false,
  "preserved_pins": [
    {
      "path": "ops/evidence/2026-10-21/p16-m3-m5-shutdown-recovery-r5/reproduce_saved.py",
      "sha256": "b0f5723264693184cf800309feeba89031fb13a5003567e698579cc2867fc476"
    },
    {
      "path": "paper16_development_r5/reproduce_saved.ps1",
      "sha256": "f3d08b4e17befd4101bcab72b84675c9d4af4a0be40c7e4f5099dd0fb9fff4d9"
    },
    {
      "path": "paper16_development_r5/LOCAL_ARCHIVE_MANIFEST.json",
      "sha256": "7e2ddf07c1fef9b7b43b603d254409222edb88fd6f48805d0b6ebdbe7ab35732"
    },
    {
      "path": "ops/evidence/2026-10-21/p16-m3-m5-shutdown-recovery-r5/SAVED_REPRODUCTION.log",
      "sha256": "4bc6bdcfcbaba15b030cd9e024248851675edde3a9ec5a663e301fa953a84757"
    },
    {
      "path": "ops/evidence/2026-10-21/p16-m3-m5-shutdown-recovery-r5/SAVED_REPRODUCTION_RECEIPT.json",
      "sha256": "bb3283902fd08d691c2b5e02118f1fae6003d225eddb5f9bb7b0d63d3d8e53ab"
    }
  ],
  "raw_stdout_policy": "Complete combined native stdout/stderr retained as base64 and sha256 below; parse uses utf-8-sig, with no result inferred from exit alone",
  "independent_reviewer_preexecution_acceptance": "r4_interruption_review accepted this exact fixed-annex process, preserving all failed original files and sources"
}
```

## Actual saved-only run 2

```json
{
  "schema": "R5_NATIVE_SAVED_REPRODUCTION_RUN2_V1",
  "started_UTC": "2026-10-22T01:13:43.939488+00:00",
  "ended_UTC": "2026-10-22T01:15:47.652764+00:00",
  "command": [
    "powershell.exe",
    "-NoProfile",
    "-File",
    "C:\\Users\\85993\\Desktop\\codebase\\neuralsignal institute\\paper16_development_r5\\reproduce_saved.ps1"
  ],
  "child_PSModulePath": "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\Modules",
  "actual_native_exit_code": 0,
  "saved_only_verification": "PASS",
  "scientific_verdict": "STOP_EXECUTION_INTERRUPTED_REQUIRED_GATE",
  "raw_combined_stdout_base64": "ew0KICAibWlzc2lvbiI6ICJQMTYtTTMtTTUtU0hVVERPV04tUkVDT1ZFUlktUjUiLA0KICAic2F2ZWRfb25seV92ZXJpZmljYXRpb24iOiAiUEFTUyIsDQogICJzY2llbnRpZmljX3ZlcmRpY3QiOiAiU1RPUF9FWEVDVVRJT05fSU5URVJSVVBURURfUkVRVUlSRURfR0FURSIsDQogICJ0ZXJtaW5hbF92YWxpZGF0aW9uIjogew0KICAgICJzdGF0dXMiOiAiVkVSSUZJRUQiLA0KICAgICJ2ZXJpZmllZF9zY2llbnRpZmljX3N0YXR1cyI6ICJTVE9QX0VYRUNVVElPTl9JTlRFUlJVUFRFRF9SRVFVSVJFRF9HQVRFIiwNCiAgICAicmVwb3J0ZWRfc2NpZW50aWZpY19zdGF0dXMiOiAiU1RPUF9FWEVDVVRJT05fSU5URVJSVVBURURfUkVRVUlSRURfR0FURSIsDQogICAgImJhc2lzIjogIlJFR0lTVEVSRURfSU5ERVBFTkRFTlRMWV9BQ0NFUFRFRF9FWFRFUk5BTF9QUk9DRVNTX0xPU1NfU0FWRURfSEFTSEVTX09OTFkiDQogIH0sDQogICJjbG9zdXJlX2JyYW5jaCI6ICJFWFRFUk5BTF9QUk9DRVNTX0xPU1MiLA0KICAibmV3X2F0dGVtcHRlZCI6IDYyNSwNCiAgIm5ld19qb3VybmFsX2NvbXBsZXRlZCI6IDYyNCwNCiAgIm5ld19wYXJ0aWFsX3NhdmVkX2F0dGVtcHRzIjogMSwNCiAgInVuYXR0ZW1wdGVkIjogMTg1NCwNCiAgIm5hdGl2ZV93b3JrZXJfZXhpdF9jb2RlIjogbnVsbCwNCiAgImV4YWN0X2ludGVycnVwdGlvbl9VVEMiOiBudWxsLA0KICAiaW50ZXJydXB0aW9uX2NhdXNlIjogIlVOREVURVJNSU5FRF9GUk9NX1NBVkVEX0VWSURFTkNFIiwNCiAgIk00X2NvbXBsZXRlIjogZmFsc2UsDQogICJwYXJ0aWFsX251bWVyaWNhbF9zdGF0dXMiOiAiSU5DT01QTEVURV9OT1RfUEFTU0VEIiwNCiAgInBhcnRpYWxfZGlhZ25vc3RpY19yZXNlcnZhdGlvbnMiOiB7DQogICAgIkFOQUxZVElDX1JFU0VSVkVEIjogMSwNCiAgICAiQURfUkVTRVJWRUQiOiAxLA0KICAgICJGRF9SRVNFUlZFRCI6IDExNzYNCiAgfSwNCiAgInBhcnRpYWxfZGlhZ25vc3RpY19jb21wbGV0ZWRfY291bnRzIjogbnVsbCwNCiAgInNuYXBzaG90X3NoYTI1NiI6ICIwZjNjMzQ1OGU2NDhjYzA1ZTE1OTE0YTEyNzNmNGIzNjUzYzU3NmIzYjQ1NDhiNmNhYjI0ZDU5MjQ2MjA1MmEyIiwNCiAgImV4dGVybmFsX3N0b3Bfc2hhMjU2IjogIjNjNTlmZWUwYjdmN2RlMDVlNGRkYTBkZTI3NWQ2OTY2OWNjM2Q2YWIwOWUxNjk1NmUxNWE5MGJhMDdhYzRlNTMiLA0KICAiYXJjaGl2ZV9tYW5pZmVzdF9zaGEyNTYiOiAiN2UyZGRmMDdjMWZlZjliN2I0M2I2MDNkMjU0NDA5MjIyZWRiODhmZDZmNDg4MDVkMGI2ZWJkYmU3YWIzNTczMiIsDQogICJyZXByb2R1Y2VyX3NoYTI1NiI6ICJiMGY1NzIzMjY0NjkzMTg0Y2Y4MDAzMDlmZWViYTg5MDMxZmIxM2E1MDAzNTY3ZTY5ODU3OWNjMjg2N2ZjNDc2IiwNCiAgIk5QWl9kZWNvZGVzIjogMCwNCiAgIm51bWVyaWNhbF9jZXJ0aWZpY2F0ZV9hdWRpdHNfcmVwZWF0ZWQiOiAwLA0KICAibmV3X2ZpdHNfZGVyaXZhdGl2ZXNfc2NvcmVzIjogMCwNCiAgIkVfYWNjZXNzIjogZmFsc2UsDQogICJGaW5hbF9DX0RfYWNjZXNzIjogZmFsc2UsDQogICJwdWJsaWNhdGlvbl9hdXRob3JpemVkIjogZmFsc2UNCn0NCg==",
  "raw_combined_stdout_sha256": "156b3d542e198cb01f5107fd7e2d7c259e84bd760decaf8f73b4154577fd7720",
  "raw_combined_stdout_bytes": 1585,
  "decoded_as": "utf-8-sig",
  "output": {
    "mission": "P16-M3-M5-SHUTDOWN-RECOVERY-R5",
    "saved_only_verification": "PASS",
    "scientific_verdict": "STOP_EXECUTION_INTERRUPTED_REQUIRED_GATE",
    "terminal_validation": {
      "status": "VERIFIED",
      "verified_scientific_status": "STOP_EXECUTION_INTERRUPTED_REQUIRED_GATE",
      "reported_scientific_status": "STOP_EXECUTION_INTERRUPTED_REQUIRED_GATE",
      "basis": "REGISTERED_INDEPENDENTLY_ACCEPTED_EXTERNAL_PROCESS_LOSS_SAVED_HASHES_ONLY"
    },
    "closure_branch": "EXTERNAL_PROCESS_LOSS",
    "new_attempted": 625,
    "new_journal_completed": 624,
    "new_partial_saved_attempts": 1,
    "unattempted": 1854,
    "native_worker_exit_code": null,
    "exact_interruption_UTC": null,
    "interruption_cause": "UNDETERMINED_FROM_SAVED_EVIDENCE",
    "M4_complete": false,
    "partial_numerical_status": "INCOMPLETE_NOT_PASSED",
    "partial_diagnostic_reservations": {
      "ANALYTIC_RESERVED": 1,
      "AD_RESERVED": 1,
      "FD_RESERVED": 1176
    },
    "partial_diagnostic_completed_counts": null,
    "snapshot_sha256": "0f3c3458e648cc05e15914a1273f4b3653c576b3b4548b6cab24d592462052a2",
    "external_stop_sha256": "3c59fee0b7f7de05e4dda0de275d69669cc3d6ab09e16956e15a90ba07ac4e53",
    "archive_manifest_sha256": "7e2ddf07c1fef9b7b43b603d254409222edb88fd6f48805d0b6ebdbe7ab35732",
    "reproducer_sha256": "b0f5723264693184cf800309feeba89031fb13a5003567e698579cc2867fc476",
    "NPZ_decodes": 0,
    "numerical_certificate_audits_repeated": 0,
    "new_fits_derivatives_scores": 0,
    "E_access": false,
    "Final_C_D_access": false,
    "publication_authorized": false
  },
  "all_preserved_pins_rechecked_unchanged": true,
  "not_original_scientific_worker_exit": true,
  "scientific_execution_restarted": false
}
```
