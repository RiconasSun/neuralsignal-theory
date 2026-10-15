# Required C sealing gate failure — no retry

The explicitly authorized frozen C-only run executed once. The isolated native calibration worker passed its numerical, physiology, coverage and source/access gates and exited0 with cleanup0 after571.187seconds. It completed13mice,26subfields,290cases,21,716GLM unit fits,78joint N seed fits and26N coefficient-mean certificates. Every required view has13paired mice. All40,104model-unit endpoint certificates passed. Maximum original outward-gradient PG was0.0002573605165640388, maximum independent AD scaled error5.510782802309322e-15, and maximum AD objective discrepancy1.4210854715202004e-14. These are below the unchanged thresholds. There were no fit retries.

The mandatory complete-state seal then failed with `ModuleNotFoundError: No module named 'selection'`. Frozen call path:

```text
real_C.py:120 -> state_manifest.create
state_manifest.py:80 -> validate_state_manifest
release_control.py:211 -> validate_provenance
release_control.py:130 -> from selection import views
ModuleNotFoundError: No module named 'selection'
```

This is a P1 host packaging/import defect. In the prior retrospective synthetic path, `state_manifest.create` inserted the copied code directory and imported calibration, indirectly loading selection into the process module cache. That path masked the missing host dependency. The real path correctly has a prospective roster, so it skips reconstruction and reaches the bare import in a fresh host environment. The native worker has its own copied selection.py; native numerical success does not certify the host sealing branch. Both independent reviewers confirmed the defect and acknowledged the earlier review missed this branch distinction.

All92 frozen source hashes remain unchanged. The run stopped at that error. No source fix, import-path injection, cache workaround, validation retry, seal retry or refit was performed. The partially written private directory and all native outputs remain preserved. Its1,858files are hash-bound in partial_seal_inventory.json. The complete C_state_manifest.json and public C_sealing_receipt.json are absent. Hashing/copying the existing journals for evidence preservation does not complete or retry the failed seal.

Current claims: REAL_C_NUMERICAL_FITS_PASS=TRUE; ENGINEERING_CONTROL_PASS=FALSE; COMPLETE_C_SEAL_PASS=FALSE; REAL_C_CALIBRATION_PASS=FALSE. Historical E0–E3 receipts and reviews remain unchanged and separately identified as earlier evidence; they do not override this new required-gate failure. Original final-validation Stage1 FAIL and all prior P12 scientific/numerical failures remain immutable.

D_AUTHORIZED=FALSE; D_RELEASE_CONSUMED=FALSE; D_EVALUATION_EXECUTED=FALSE. The26actual protected D open checks all denied access without reading bytes. The new D partition file contains frozen trial metadata only and creates no entitlement. No D score, D-derived QC, null or final evaluation was executed.

The native launch receipt retains legacy fields final_values_exposed_to_analysis=false/final_holdout_evaluated=false. For this run the explicit phase=real_C, C_access_authorized=true and synthetic_only=false record authorized final-mouse C access by the calibration principal. These legacy fields must not be read as claiming that no C values were used.
