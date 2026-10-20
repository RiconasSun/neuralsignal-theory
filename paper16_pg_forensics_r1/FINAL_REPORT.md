# P16 saved-evidence PG failure forensics

MISSION P16-PG-FAILURE-FORENSICS-R1. Required and verified initial BASE:1ab5a7b2077f9f8526bf5d5028b042da199f6bc6 on test/origin/test. Initial working tree clean. origin/main is absent, verified by remote enumeration; no fabricated SYNCED relation or main integration.

Diagnostic verdict: **SOLVER_TERMINATION_POLICY_LIMITATION**. Original R3 **STOP_NUMERICAL_REQUIRED_GATE** remains unchanged. The forensic mission's completion status is separate from scientific acceptance.

The exact failed endpoint has37 packed coordinates, f0.35200449304009157 and independently reconfirmed outward PG1.9827644454692775e-5>1e-5. It used254 accepted iterations and275 FG calls, then returned SciPy successTrue on relative-objective reduction. Last protocol-associated accepted relative decrease5.4511950509095186e-14 satisfies frozen ftol1e-12 while scientific PG fails. All saved analytic/AD/fixed-FD checks pass. No implementation bug was demonstrated; no production code was patched.

The largest residual is interior packed26, original27 color*order. Next are color*repeat and own20-60ms history. Saved A/S02 scaler active metadata recovers every name; only original23 running_missing was dropped. Endpoint lower-bound coordinates3/4 correctly have outward PG zero. All37 endpoint coordinates and all111 three-checkpoint rows are in the coordinate CSVs, with coefficients, bounds and four saved FD gradients. These are derivative certificates and parameter/scaler metadata requested by the mission, not raw neural arrays.

The275 FG values and254 accepted-vector summaries preserve initial/mid/final objectives, saved raw gradient-inf, step sizes and bounds. EveryFG objective is directly recorded. Accepted-objective association follows pinned SciPy callback and broker ordering, cross-checked at initial,127,254; other identities are explicitly protocol-derived because FG x/full g were not logged. Line-search trial274's objective increase is retained. No objective/gradient has been recomputed. Saved250 has gradient-inf below1e-5 but above solvergtol2e-6; choosing it retrospectively violates the frozen endpoint/checkpoint contract and is not a recovery.

All952 accepted optimizer endpoints were rechecked from saved arrays, not a sample. PG range1.880169292085894e-7..1.9997389862705384e-6, median1.4774231426179981e-6. All952 terminate on solver gradient condition and none exceed0.5 of the scientificPG threshold. Their iterations range13..759 (median64); FG15..789 (median70). Earlier72C,48S02 and10S02/C passes show this objective-stop mode was exceptional in the saved prefix, but cannot establish cohort-wide frequency. Sequential STOP leaves5518 tasks unavailable; multiple fits within a mouse are not independent animals. No predictive scores were recalculated or compared.

The narrow numerical explanation is established: solver objective tolerance can terminate before the scientific gradient gate, and the wrapper correctly rejects it. Weak unpenalized PSTH curvature or conditioning may contribute; scaler ranges and long checkpoint chords do not measure Hessian conditioning or establish causality. No local Hessian/design or compiled line-search state was inspected. Full unknowns and competing explanations appear in ROOT_CAUSE_ASSESSMENT.

Integrity:581 original source/evidence pins,193 R3 BASE payload bindings and10717 protected files totaling325603327bytes verified before/after analysis. Original953 endpoints (952pass/1fail),216 analyticB0 certificates,5518 unattempted, all prior source freezes/reviews and failures remain immutable. The required inherited saved-only PowerShell reproduction passed before diagnostics; it rechecked existing B score summaries, not a new likelihood/model evaluation. The new forensic reproduction never opens score arrays. The new mission has zero model fits, optimizer calls, objective/gradient evaluations, scientific scores or source requests; no B/E neural or FinalC/D access.

Reproduce from repository root with the existing pinned runtime and protected saved evidence:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\paper16_pg_forensics_r1\REPRODUCE_FORENSICS.ps1
```

This runs synthetic arithmetic/parser/access regressions and deterministic saved-only report reproduction. Missing/changed evidence fails closed. It does not create missing coefficients, reacquire neural sources or resume R3. Native inherited reproduction log and fresh final reproduction log are retained in the mission evidence directory. Independent review, requirement-level completion, archive identity and remote receipts accompany the handoff; post-Git SHA/readback receipts are outside their own committed manifest to avoid self-reference.

Safest next action is retain STOP. A separately authorized termination-policy feasibility study is optional, requires prospective registration and independent review, and cannot retrospectively clear R3. Exact alternatives, candidate resource caps and scientific-contract consequences are in PROSPECTIVE_OPTIONS. No scientific restart, E, M6, Final or P17 is authorized or executed.
