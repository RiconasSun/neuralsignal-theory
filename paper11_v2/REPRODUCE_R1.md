# R1 Controlled Numerical Verification

From the repository root, use the registered saved-output entrypoint:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File paper11_v2/scripts/reproduce-r1-code1.ps1
```

Supply `-Python <path-to-python.exe>` on another installation. Recorded runtime
is CPython3.11.15; required packages are pinned in requirements.txt. This
command verifies preserved archives, prior gates, sources and numerical
artifacts, reruns independent analytical/exhaustive correctness tests, and
replays the immutable R1 verdict. Missing/corrupt evidence fails closed, without
real neural data, raw fallback, training rerun, network or holdout access.

Initial execution, after source registration, is:

```powershell
python paper11_v2/scripts/run_r1_code1.py register
python paper11_v2/scripts/run_r1_code1.py execute
```

`execute` is one-shot: a started namespace cannot be reused even if it failed.
Registration must precede all model testing/fitting. All predetermined seeds,
ridges/configurations are retained; failures stop the milestone, not dropped.
Controlled fixture fits validate software only and never count as biological
findings, development-cohort comparisons, null tests or final validation.

R0's authoritative reproduction remains reproduce-r0-amend1-code1.ps1.
Do not run historical R0 pipelines that overwrite immutable failure evidence.
Old primary test and the frozen external60/40 partition remain locked.

Original R1 implementation remains FAIL in results/R1: batch-size arithmetic
failed a bitwise reset assertion; temporary fixture permissions failed runner
tests. Do not rerun or reinterpret that gate. CODE-1 sources/results are separate;
all original assertions and1e-10score threshold remain unchanged. Per-trial
deterministic arithmetic fixes the implementation, not test tolerances. The
new test harness uses writable workspace temporary fixtures without escalation.
Actual one-command receipt/log is results/R1_code1/reproduction.json and .log.
51unique current R0/R1 checks passed; controlled fits are169/169converged.
