# P15 Development archive: scientific execution stopped

Read [STOP_REPORT.md](STOP_REPORT.md) and `results/DEVELOPMENT_STATUS.json` first. The native task timestamp serializer changes strict-past wheel inputs. The production source was preserved, and no repair/refit or downstream B/E/Final execution occurred.

Saved-only stopped-evidence reproduction, from the repository in Windows PowerShell:

```powershell
& .\paper15_dev\reproduce_stop.ps1
```

The default uses the existing pinned local runtime. On another host, install `requirements.txt` separately and supply `-Python C:\path\to\python.exe`. Reproduction itself never installs, downloads, loads real neural arrays or performs real-data fitting/scoring. Tests may optimize synthetic fixtures. It verifies the stopped archive, rather than declaring scientific completion. The complete-E `reproduce.ps1` is a preserved conditional implementation and cannot pass without outputs that were never generated.

`FINAL_IMPLEMENTATION_HANDOFF.md`, `A1_A10_CLAIM_AUDIT.md` and the implementation modules were prepared conditionally before the stop. They grant no progression. Their complete-run claims require actual missing outputs and are superseded for the current run by this notice, `STOP_CLAIM_AUDIT.md` and `STOP_REPORT.md`.
