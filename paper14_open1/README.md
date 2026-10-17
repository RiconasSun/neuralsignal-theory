# P14 open-release recovery — saved metadata only

Read OPEN_RELEASE_REPORT.md and results/RECOVERY_DECISION.json. Decision SOURCE_OR_TIMING_INCONCLUSIVE; no complete M1 freeze, no Prompt3 eligibility.

From the repository root in Windows PowerShell:

```powershell
& .\paper14_open1\reproduce.ps1
```

Optional `-Python C:\path\to\python.exe` selects Python3.11 with numpy2.4.6, pandas3.0.5, requests2.33.0 and numcodecs0.16.5. Fixed codec installation used `python -m pip install numcodecs==0.16.5 --no-deps`; reproduction itself blocks network and installs nothing. It verifies frozen payload/source/history hashes, runs20 synthetic/source policy regressions and byte-compares8 regenerated metadata results in a fresh ignored temporary directory.

Never run retrieval as reproduction. `retrieve.py`/`inventory.py`/`columns.py` are bounded research tools, not a security system against hostile administrators. Their only actual array payloads are four explicitly registered anatomy/probe/unit-ID/provider-QC metadata columns from twelve canonical Zarr sessions. All other arrays, full NWB, raw behavior and automatic SDK fallback are outside scope. No fits or neural scores exist.
