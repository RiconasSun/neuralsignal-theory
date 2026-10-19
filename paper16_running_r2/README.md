# P16 native running precision recovery R2

Mission P16-M2-RUNNING-PRECISION-RECOVERY-R2. BASE67188e8e53a5c9a6c2ae7835b8b29aab7768db9e. This package is a separately registered running-only compatibility and source-validity study. It does not authorize neural QC, model fitting, B selection, E assessment, Final C/D or an automatic M2–M5 restart. Historical M2 STOP and R1 SOURCE_SCHEMA_INCOMPATIBLE remain unchanged.

PRECISION_CONTRACT_DECISION.md distinguishes actual source storage from float64 arithmetic. The exact permitted internal alias is verified within the pinned file. Native `<f4` rotation values are retained and promoted exactly; supported `<f8` rotation is preserved, timestamps stay nativebinary64, formula/strictpast/missingness/masks/thresholds remain frozen. No additional sensor precision, neural benefit or biological admission is established by a source gate.

The preaccess and first-actual-source independent reviews are in `ops/evidence/2026-10-19/p16-m2-running-precision-recovery-r2/`. Both failed initial reviews, their complete candidates and the failed test setup are preserved. Each full decoded native vector is fsynced before reading the next. Result JSON records source identity, aliases, clocks, original array hashes, complete/partial vector manifests, derived state and every role/color denominator. Source array hashes are not full NWB hashes.

After the source stage and final content freeze, reproduce from the repository root in native Windows PowerShell:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\paper16_running_r2\reproduce.ps1
```

The default uses `paper16_m1/work/runtime/Scripts/python.exe`. Else pass `-Python C:\path\python.exe` in the pinned Python3.11.15 / NumPy2.4.6 / SciPy1.16.3 / h5py3.16.0 / requests2.32.5 environment. No installation/download fallback. Reproduction reads only saved R2 running vectors, frozen flash/invalid metadata and evidence; it blocks network/native NWB/neural loads. It replays arithmetic/coverage, independently checks all900 causal targets per completed source, validates fixed payload hashes and runs19 synthetic regressions. Synthetic files are temporary beneath ignored `work/`; source workers are never invoked.

`run_sources.py` is the frozen historical real execution path, **not a reproduction command**. Do not run either phase again. Exclusive claims and original single4h deadline persist. All real source attempts are final within this mission; no retry, substitution or budget extension is authorized.

Current native outcomes and exact denominators belong in NATIVE_SOURCE_VALIDATION.md, RUNNING_COHORT_REPORT.md and the coverage/attempt/resource tables after execution. Final review and actual Git transport proof are separate gates. A tracked content file cannot truthfully know its own future commit hash; executed terminal values/remote blob checks/clean proof go in ignored `work/closure_receipt.json` after normal origin/test archive and are reported to the owner. Stop at the reviewed running-only handoff.
