# Controlled R0 Amendment Reproduction

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File paper11_v2/scripts/reproduce-r0-amend1-code1.ps1
```

Default verifies original source/failure/holdout identities, saved cohort data,
unit/count features, admission logic, tests and artifact hashes without neural
reads. `-FreshQC` repeats the full real checksum-bound NIX train/development
validation array QC; it never decodes oldtest, other MTL, iEEG or external
arrays. The immutable original40trial failure is not rerun or overwritten.
Registered32usable/train24/validation8and minimum8subjects cannot change.

Each simultaneously recorded unit is session-local; summing units across
sessions is not a unique-neuron count. Training-only unit selection precedes
validation integrity checks; zero-rate validation units are retained. Array
existence verifies observed trials under the published8s convention, not
independent per-bin dropout masks. Unknown SU/MU sorting labels are disclosed.
External calibration/final60/40trial lists remain byte-identical and locked.
Code/test integrity or inadequate cohort yields nonzero, never a false PASS.

Use the code1 entrypoint above. The original entrypoint/source/output are kept
as historical evidence only: independent review identified incomplete access
logging for excluded units and unsafe missing-cache fallback. Code1 registered
the audit-only repair before fresh QC; all23feature objects remain identical.
Saved-only replay validates the entire artifact roster before loading results
and explicitly forbids fresh raw QC. Four repair regressions and the original
29R0 tests pass (33total); actual PowerShell reproduction exit0 is recorded in
results/R0_amendment1_code1/reproduction.json and reproduction.log.
