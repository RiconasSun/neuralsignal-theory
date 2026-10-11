# Authoritative Saved-Execution Audit

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File paper11/audit/reproduce-num3-audit.ps1
```

This post-execution provenance amendment addresses the review finding that the
original report checked current source hashes without binding saved QC/gate to
that registration. No registered numerical source, budget, threshold or result
is rewritten and no additional numerical experiment is performed after FAIL.
An independently locked auditor rejects stale/mixed result identities, modified
raw-replica summaries, missing/reordered seeds, incorrect gates and inconsistent
registration/execution/report chronology. Six corruption regressions include
the real saved negative result. Final command exits1 because numerical FAIL
remains authoritative even when artifact integrity passes.

Original numerical replay command remains REPRODUCE_M4_NUM3.md; it was actually
executed and stopped. This audit is required before accepting any saved report
as final evidence; the legacy report-only path is not evidence certification.
The initial engineering interruption and both registrations remain preserved.
