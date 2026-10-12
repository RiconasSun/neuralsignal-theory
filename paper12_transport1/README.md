# P12 Bounded Transport Recovery

See `MILESTONE_STATUS.md`, `QC_REPORT.md`, `CLAIM_AUDIT.md` and the machine-readable
`results/M2/gate_result.json`. The new M2 failed locally; no downstream scientific
execution or final release is authorized by these results.

Saved public reproduction, from repository root:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File paper12_transport1/reproduce.ps1
```

It verifies the final public input manifest before/after replay, preserves all
prior tracked evidence, executes old `paper12_custody1/reproduce2.ps1`, reruns
synthetic regressions, and reconstructs the disposition table/gate. A zero exit
code means saved-evidence reproduction, not M2 scientific PASS. It never starts
retrieval, accesses private QC, launches live security probes, fits models, runs
nulls or unlocks the final evaluation. Python selection follows the existing
PowerShell reproducer and can be overridden by `-Python`.

Real execution was prospectively registered, followed by implementation sealing,
preflight, fresh native isolation and trusted `run_recovery.py`. The preserved
current failure prevents that driver from starting more retrieval on restart.
Do not delete STOP records, reset per-block attempt ledgers, replace ETags,
reclassify gates or accept pending blocks. The trusted custodian and private
artifacts are environment-specific, not distributed in Git.

Exact detailed new failure diagnostics are private; the public redaction records
their checksum. Original prior failure is unchanged. Reproducer verifies saved
public evidence, not possession or validity of unavailable private artifacts.
