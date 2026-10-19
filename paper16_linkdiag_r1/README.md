# P16 targeted metadata-only diagnosis

Disposition: **SOURCE_SCHEMA_INCOMPATIBLE**. A legitimate internal timestamp SoftLink was established by same-file/object-address identity. Rotation storage is float32, contrary to the frozen executed all-float64 reader requirement. No production reader repair, native numeric read or scientific restart is authorized by this package.

Read `LINK_DIAGNOSTIC_REPORT.md` for Q1–Q8, `ROOT_CAUSE.json` for the two distinct blockers, `COMPONENT_AUDIT.json` and original results journals for exact observations. `SCIENTIFIC_CLAIM_AUDIT.md` distinguishes engineering from scientific conclusions.

Saved-only reproduction from the repository root in Windows PowerShell5.1:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\paper16_linkdiag_r1\reproduce.ps1
```

The default reuses the existing pinned `paper16_m1/work/runtime/Scripts/python.exe`. On another host supply `-Python C:\path\to\python.exe` in the matching Python3.11.15 / numpy2.4.6 / scipy1.16.3 / h5py3.16.0 / requests2.32.5 environment. No network/runtime-install fallback exists. The scientific freeze verifier checks every declared payload against a static independent expected filename set. Reproduction writes synthetic temporary fixtures only beneath ignored `work/`; it never invokes the live inspection entry point, reopens NWB sources, reads arrays, fits or scores.

`inspect_source.py` is the historical one-shot diagnostic execution path. **Do not run it again.** Existing immutable parent/child claims block a duplicate. Saved response ranges are bounded metadata from that completed execution, not a whole NWB. `verify_saved.py` uses only these retained bytes, fails on missing/corrupt/contradictory coverage, denies network and guards dataset-value APIs.

Source-level bindings and both unsuccessful/accepted independent preaccess reviews are in `ops/evidence/2026-10-18/p16-m2-native-link-diagnostic-r1/`. All prior M1/M2 evidence remains immutable. Final content review evidence, reviewed manifest identity and actual remote readback are kept distinct. STOP after archival handoff; no automatic next mission.
