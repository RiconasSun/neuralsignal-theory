# A10 One-command Reproduction

Run:

```powershell
powershell -ExecutionPolicy Bypass -File paper5\scripts\reproduce-paper5.ps1
```

The command audits local HCP-YA 2025 inputs and either runs the ready gates or reports the exact missing inputs.

Optional access probe:

```powershell
powershell -ExecutionPolicy Bypass -File paper5\scripts\reproduce-paper5-balsa-access-probe.ps1
```
