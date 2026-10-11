# Boundary Audit Reproduction

Repository-root PowerShell, saved-only, repeat-safe:

```powershell
& ./paper11_v2/boundary_audit1/reproduce-safe.ps1
```

`-Python <absolute-python.exe>` can select an equivalent recorded environment.
Runtime uses Python3.11.15,h5py3.16.0,NumPy2.4.6,requests2.33.0. Requests are
used only in original metadata acquisition, never this reproduction. No new
dependency is required. Prior tracked files and scientific gates must be intact.

Saved replay verifies pinned source/artifact/prior hashes, all52asset identities,
decode allowlist, all52metadata support verdicts and18controlled tests. Exit0
means engineering replay, not full52scientific support or authorization to
resume R2. Scientific verdict remains INCONCLUSIVE; original R2FAIL unchanged.

Original execution order:register_sources.py register, then sources; audit.py
register, then execute. Results/sources contains pinned author text and metadata
only. Never execute downloaded code. Never delete execution_started.json or
overwrite registrations, gates, receipts or original source files.

The original audit.py replay wrote a one-time immutable receipt, and was actually
verified through reproduce.ps1. It intentionally cannot overwrite that receipt.
The separately registered verify_saved.py/reproduce-safe.ps1 wrapper makes
subsequent saved-only reproduction repeatable without changing the registered
scientific evaluator or previous receipt. It does not refit, reacquire or tune.
