# P12-M4-CONTINUOUS-GRADIENT-DIAG-1 — preflight planning

Mode: PLANNING_MODE. Execution has not started.
Baseline revision: draft 1. baseline_frozen_at: NONE.
Required base: independently reviewed final closeout commit of P12-M4-DYNAMICS-NUMERICAL-RECOVERY-1. This commit is not currently available. The offset closeout e635724f2aae45b7fdf30edb5902beaab425b8e2 is NOT an approved substitute.
Source: explicit user mission D1-D4 and deliverables, received 2026-10-13 America/Los_Angeles.

## Contract and boundaries

Actor: scientific investigator. Outcome: distinguish analytical-gradient defects, numerical derivative instability, and optimizer nonconvergence without changing the model or historical acceptance criteria.
Training A and synthetic only. No validation scores, B/C/D or final values, source acquisition, model repair, solver amendment, full-cohort M4, M5, M6 or null execution.
Prior failures remain immutable. One diagnostic mission only. An engineering diagnostic PASS cannot change the historical scientific gate.

## Draft atomic requirements

All items are OPEN; there is no verified implementation or numerical result in this mission.

| ID | Requirement | Proposed verification |
|---|---|---|
| REQ-001 | Start from independently reviewed predecessor closeout commit | Commit, review and archive readback |
| REQ-002 | Register populated frozen baseline before diagnostic code/data access | Timestamp, exact source/runtime hashes |
| REQ-003 | Preserve historical M4 failures and prior files | Pre/post hashes and scoped diff |
| REQ-004 | Enforce training A/synthetic-only custody | Native role proof and bound input manifest |
| REQ-005 | Reproduce CA1 Continuous d4/ridge .001/seed11 | Exact identity and solver receipt |
| REQ-006 | Preserve all frozen solver options including maxiter2000 | Source/options equality |
| REQ-007 | Verify data/model/context/offset identities | Hashes and parameter layout |
| REQ-008 | Preserve objective, normalization, ridge and bounds | Independent objective and penalty checks |
| REQ-009 | Preserve original gradient-check implementation | Original/cached-oracle source bindings |
| REQ-010 | Reproduce original failure and approximately .693 PG | Endpoint/PG/error comparison |
| REQ-011 | Predefine and retain full central-difference scale scan | All scales, no favorable-step selection |
| REQ-012 | Run higher-order finite differences | Coordinate tables and stability flags |
| REQ-013 | Run Richardson extrapolation where stable | Explicit instability/cancellation handling |
| REQ-014 | Use independent AD or symbolic derivatives where feasible | Independent recurrence implementation and oracle |
| REQ-015 | Verify synthetic small-dimension recurrent oracle | Deterministic synthetic tests |
| REQ-016 | Record coordinate absolute and relative errors | Complete coordinate evidence |
| REQ-017 | Examine initialization | Bound vector/hash and derivatives |
| REQ-018 | Examine predefined intermediate iterate | Bound vector/hash and derivatives |
| REQ-019 | Examine preserved failing endpoint | Bound vector/hash and derivatives |
| REQ-020 | Audit recurrent, history-input, context and readout weights | Parameter-block mapping and summaries |
| REQ-021 | Examine intercept/offset contribution without introducing fitted parameters | Frozen offset/context-intercept audit |
| REQ-022 | Examine ridge terms separately | Independent ridge gradient and objective |
| REQ-023 | Treat bounds explicitly | Unconstrained derivative vs projected gradient |
| REQ-024 | Treat objective normalization and numerical precision explicitly | Float64/reference calculations and recorded exposure |
| REQ-025 | Every derivative comparison uses identical objective/vector | Input hashes and loss equality |
| REQ-026 | Determine analytical-gradient correctness separately | Independent derivative agreement/disagreement |
| REQ-027 | Determine finite-difference reliability separately | Scale/order/precision evidence |
| REQ-028 | Determine optimizer convergence separately | Frozen solver/PG outcome; no gradient-based clearance |
| REQ-029 | Return one of the five authorized diagnoses | Explicit D4 decision table; no invented result |
| REQ-030 | Propose separate minimal repair or bounded optimizer study if indicated | Proposal only; no execution |
| REQ-031 | Deliver numerical audit and root-cause verdict | Source-bound report |
| REQ-032 | Deliver meaningful regression tests | Non-mirroring synthetic defect/instability tests |
| REQ-033 | Deliver one-command PowerShell reproduction | Actual execution and scope distinction |
| REQ-034 | Obtain independent review | Final-state review with P0/P1 resolution |
| REQ-035 | Exact mission commit and verified origin/test readback | Scoped staging, commit and remote SHA |
| REQ-036 | Stop after diagnosis; preserve all prohibited downstream boundaries | Negative scope audit |

draft_requirement_count: 36. verified_baseline_count: 0.

## Candidate diagnostic plan — not yet registered for execution

Freeze scale multipliers [1e-2,1e-3,1e-4,1e-5,1e-6,1e-7,1e-8] applied to max(1,abs(theta_i)); preserve the original 1e-5 formula/gate separately. Retain all scale outputs. Fourth-order differences and paired h/h2 Richardson estimates must identify cancellation, overflow and unstable extrapolation, not discard unfavorable evidence.
Use independent forward-mode differentiation of a separately written scalar recurrent Poisson objective where feasible; do not reuse production backpropagation. Inspect initialization, the accepted iterate at index floor(number_of_accepted_iterates/2), and failing endpoint. If vectors were not saved, exact frozen single-fit replay may capture them prospectively, with endpoint identity verified rather than assumed.
The archived model has four fitted blocks: recurrent A, past-count B, context D and readout C. It has no separate free bias block. The context includes intercept effects and the offset is frozen; examine these explicitly without adding parameters or refitting offsets.
Prefer L0-L2 diagnostics and mandatory real A-only custody proof. No mathematical code or optimizer-policy mutation. No gate clearance based on choosing a favorable scale.

## Blocking preflight decision

No predecessor final review, verdict or commit exists in the inspected checkout/ref inventory. A user question requests either authorization to finish its stopped-evidence closeout first, or the SHA/location of an already independently reviewed closeout. Pending that decision, no consequential execution is allowed and this draft is not a frozen scientific registration.
