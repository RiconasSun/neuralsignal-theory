# M3/M4 Saved-Output Audit Reproduction

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File paper11/scripts/reproduce-m3-m4-audit.ps1
```

Reads saved fit/score JSONs and verifies source/split identities. Does not load
raw spike times or feature arrays, fit new models, change selection, unlock
final/external holdouts or run M5-M7. First runs six focused automated tests.
Outputs CSV tables, PNG/PDF diagnostics, QC, claim audit and report gate under
results/M3_M4_scope_audit. Exit0 means report reproduction only, not M4 PASS.
Original M3/M4 execution commands and historical gates remain unchanged.

Baseline subject rows average session means equally within each subject for
each fixed candidate (9 subjects x21 candidates), not neurons/windows as subjects.
All 483 candidate rows retained. Figure displays ridge1 consistently for all
regularized baseline families, not a newly optimized alpha. Full grid in tables.
Trial SEs are descriptive and cannot replace subject uncertainty or account for
validation selection optimism. M4 rows cover a single smoke session, not
subject consistency. No three-family winner/comparison CI can validly be given.
Joint task+timing B2 not in old frozen grid; own-unit log1p-history ridge model
can be described as Poisson AR but is not raw-count or cross-population AR.
Definition/numerical-method amendment decisions remain pending.
