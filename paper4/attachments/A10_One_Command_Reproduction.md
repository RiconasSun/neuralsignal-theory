# A10 One-command Reproduction

Run on this Windows workspace:

```powershell
powershell -ExecutionPolicy Bypass -File paper4\scripts\reproduce-paper4.ps1
```

To refresh the online OpenNeuro confound-recovery audit first, run:

```powershell
powershell -ExecutionPolicy Bypass -File paper4\scripts\reproduce-paper4-online-confounds.ps1
```

Expected outputs include:

```text
paper4/results/e8_claim_audit.json
paper4/results/CURRENT_RESULTS.md
paper4/manuscript/PAPER4_MANUSCRIPT_CURRENT.md
paper4/submission/PAPER4_BIORXIV_DRAFT_CURRENT.pdf
```
