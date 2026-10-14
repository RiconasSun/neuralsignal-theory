# P12 Continuous gradient diagnostic

BASE: `0e7ac4d816d2f006f7e394cfaa37a1d362679e5f`.

Diagnosis: **FINITE_DIFFERENCE_INSTABILITY**. Analytical vs independent AD maximum error is 7.26e-12 across the three registered vectors. Original fixed checker error 2.0676e-4 and endpoint PG 0.692604771056502 remain failures. Optimizer convergence is not cleared.

Read [NUMERICAL_AUDIT.md](NUMERICAL_AUDIT.md). Complete evidence is [gradient_scan.csv](results/diagnostic/native/gradient_scan.csv), [decision.json](results/diagnostic/native/decision.json), [exact replay](results/diagnostic/native/reproduction.json), [fresh saved certificate](results/receipt_recovery_launch_receipt.json) and the mission evidence folder under `ops/evidence/2026-10-13/p12-m4-continuous-gradient-diag-1`.

Run from repository root:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\paper12_contgrad1\reproduce.ps1
```

Requires Python, NumPy and SciPy. Replays public saved evidence and synthetic tests only; no protected data or new fit. Primary numerical execution was one A-only native fit. Its controller failed while serializing its completion receipt; original native exit/cleanup remain unpublished. A separate fresh saved-only native certificate validates the completed results without pretending to recover those historical metadata values.

`registration.json` freezes the protocol before implementation; `execution_registration.json` binds the exact numerical worker sources. Later output/receipt audit helpers are separately bound. `final_manifest.json` seals public source/evidence bytes; ignored `replay/` contains fresh replay receipts. Original Stage A and the three archived preflight drafts remain preserved. No scientific recovery or downstream competition is authorized.
