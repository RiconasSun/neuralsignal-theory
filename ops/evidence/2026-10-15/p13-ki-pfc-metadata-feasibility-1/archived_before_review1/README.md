# P13 KI/PFC metadata feasibility only

Read `REPORT.md`, `SUMMARY.json`, the prospective `REGISTRATION.json`, all `results/final/` tables and the separately marked `design_proposal.md`. Overall scientific verdict: INCONCLUSIVE_METADATA. Primary single-task Passive route: DATA_INSUFFICIENT. Secondary aversive candidate: unresolved metadata, never automatically promoted to a viable cohort.

Public saved-only PowerShell reproduction:

```powershell
& .\paper13_ki_feasibility1\reproduce.ps1
```

Requires the Python dependencies in `requirements.txt`. The supplied Windows environment uses system Python for h5py/numpy/requests and its already-installed bundled Python for the independent openpyxl check; no package installation or network request occurs during reproduction. For another environment with all dependencies installed, pass `-Python <python.exe> -TablePython <same-python.exe>`.

Reproduction checks saved hashes and access boundaries, runs synthetic metadata/QC oracles, regenerates five deterministic audit outputs byte-for-byte, and independently recomputes all region/task/tier animal denominators. It never calls acquisition tools, opens original NWB/ZIP data, decodes spike arrays or fits models. Passing reproduction confirms the metadata audit, not scientific eligibility.

Acquisition code is separate and bounded. Do not rerun it to bypass a failure. Original attempts, source freezes, parser/HTTP compatibility repairs, independent review and actual Git closure are retained in `ops/evidence/2026-10-15/p13-ki-pfc-metadata-feasibility-1/` plus its external Git receipt. Original P13 and P1–P12 remain unchanged. No M1–M7, final outcome assessment, manuscript completion, pooled task/region substitution or new dataset search is authorized by this package.
