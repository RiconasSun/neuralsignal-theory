# R0 Reproduction

From the repository root:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File paper11_v2/scripts/reproduce.ps1
```

The combined gate currently returns exit2 for DATA_INSUFFICIENT. That is the
correct reproduced scientific stop, not a successful scientific study. Verify
the actual exit code and logs with:

```powershell
& 'C:/Users/85993/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe' paper11_v2/scripts/verify_r0_package.py
```

The retained original `reproduce-r0.ps1` and amended
`reproduce-r0-schema.ps1 -Acquire` are subordinate metadata-audit entrypoints.
The external schema subgate PASS is not permission to proceed. The final script verifies
the prospective input hashes, immutable archived papers, unit tests and saved
metadata gate. A failed scientific gate must return a nonzero exit, not PASS.
It never opens spike times or final scores. The frozen CPython interpreter is
the same executable used by v1, not a Hermes agent invocation. Dependencies:
NumPy, h5py, requests; exact environment inventory accompanies registration.

Public whole-file SHA256 values are provenance pins, not falsely claimed local
whole-file verifications. HTTP ranges have independent SHA256 receipts and only
allowlisted metadata datasets are decoded. Transport blocks can buffer adjacent
uninterpreted bytes. Neural recording coverage and training-rate QC remain R2.

Coding wrapper failures are retained in engineering evidence. Account model
incompatibility prevented CLI generation; primary workspace tools implement the
same registered local-only mission, without changing permissions or endpoints.
