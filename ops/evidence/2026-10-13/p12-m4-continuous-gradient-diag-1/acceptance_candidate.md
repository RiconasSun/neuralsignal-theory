# Original 36-item acceptance plan execution

BASE 0e7ac4d816d2f006f7e394cfaa37a1d362679e5f. Original definitions below are verbatim, individually retained. Final independent review and actual remote closure are the last gates; neither is preclaimed. Saved numerical certification does not clear scientific FAIL.

| ID | Original requirement | Verification/evidence | Candidate status |
|---|---|---|---|
| REQ-001 | Start from independently reviewed predecessor closeout commit | stage_a_gate.json; Stage A closeout review and exact remote readback | VERIFIED |
| REQ-002 | Register populated frozen baseline before diagnostic code/data access | registration.json; baseline_registered.md; protocol.json; execution_registration.json | VERIFIED |
| REQ-003 | Preserve historical M4 failures and prior files | prior_manifest.json; preservation_audit.json; original_daily_operations.md | VERIFIED |
| REQ-004 | Enforce training A/synthetic-only custody | execution_registration.json A hashes; primary and certificate native/role_proof.json | VERIFIED |
| REQ-005 | Reproduce CA1 Continuous d4/ridge .001/seed11 | native/reproduction.json target and all_exact | VERIFIED |
| REQ-006 | Preserve all frozen solver options including maxiter2000 | protocol.json options; unchanged model source bindings; reproduction endpoint | VERIFIED |
| REQ-007 | Verify data/model/context/offset identities | execution_registration.json; reproduction data/context/offset hashes and layout | VERIFIED |
| REQ-008 | Preserve objective, normalization, ridge and bounds | independent_ad.py; native/*_audit.json; test_diagnostics.py ridge/normalization | VERIFIED |
| REQ-009 | Preserve original gradient-check implementation | execution_registration.json original and cached oracle SHA; replay exact checks | VERIFIED |
| REQ-010 | Reproduce original failure and approximately .693 PG | native/reproduction.json original checker + PG + histories exact | VERIFIED |
| REQ-011 | Predefine and retain full central-difference scale scan | protocol.json; gradient_scan.csv all seven scales | VERIFIED |
| REQ-012 | Run higher-order finite differences | gradient_scan.csv fourth_order and raw probes; native/*_audit.json | VERIFIED |
| REQ-013 | Run Richardson extrapolation where stable | gradient_scan.csv richardson, roundoff and stability; audit_statistics.py | VERIFIED |
| REQ-014 | Use independent AD or symbolic derivatives where feasible | independent_ad.py; native/*_audit.json; synthetic regression tests | VERIFIED |
| REQ-015 | Verify synthetic small-dimension recurrent oracle | test_diagnostics.py dimensions1/2/4 and one-bin oracle; native/synthetic_tests.json | VERIFIED |
| REQ-016 | Record coordinate absolute and relative errors | gradient_scan.csv absolute/scaled errors, all8064 rows | VERIFIED |
| REQ-017 | Examine initialization | native/initial_audit.json and initial CSV rows/vector hash | VERIFIED |
| REQ-018 | Examine predefined intermediate iterate | native/intermediate_audit.json; reproduction intermediate_index1000 | VERIFIED |
| REQ-019 | Examine preserved failing endpoint | native/endpoint_audit.json; exact history reproduction and recovered vector hash | VERIFIED |
| REQ-020 | Audit recurrent, history-input, context and readout weights | block_summary.json; CSV block mapping and four audited blocks | VERIFIED |
| REQ-021 | Examine intercept/offset contribution without introducing fitted parameters | NUMERICAL_AUDIT.md; frozen_sources/frozen_offset.py; independent_ad.py fixed offset | VERIFIED |
| REQ-022 | Examine ridge terms separately | CSV likelihood_AD + ridge_AD; block_summary.json; zero ridge discrepancy | VERIFIED |
| REQ-023 | Treat bounds explicitly | native/*_audit.json PG/AD_PG; CSV probe bounds; synthetic projection tests | VERIFIED |
| REQ-024 | Treat objective normalization and numerical precision explicitly | native/*_audit.json exposure7200/mantissa52; independent objective equality | VERIFIED |
| REQ-025 | Every derivative comparison uses identical objective/vector | CSV theta digests repeated across scales; independent objective equality | VERIFIED |
| REQ-026 | Determine analytical-gradient correctness separately | native/decision.json analytical_gradient_validated; AD error maxima | VERIFIED |
| REQ-027 | Determine finite-difference reliability separately | native/decision.json and full step/order scan, no original-gate substitution | VERIFIED |
| REQ-028 | Determine optimizer convergence separately | native/reproduction.json; independent endpoint AD_PG; original PG gate false | VERIFIED |
| REQ-029 | Return one of the five authorized diagnoses | native/decision.json FINITE_DIFFERENCE_INSTABILITY; saved reconstruction | VERIFIED |
| REQ-030 | Propose separate minimal repair or bounded optimizer study if indicated | NUMERICAL_AUDIT.md separate bounded future proposal only | VERIFIED |
| REQ-031 | Deliver numerical audit and root-cause verdict | NUMERICAL_AUDIT.md; CSV; block_summary.json; figures/ | VERIFIED |
| REQ-032 | Deliver meaningful regression tests | 13 independent synthetic +6 saved integrity regressions; preserved failed attempts | VERIFIED |
| REQ-033 | Deliver one-command PowerShell reproduction | reproduce.ps1; actual replay receipt (created after sealing) | VERIFIED |
| REQ-034 | Obtain independent review | review_final.md final independent review (required before closure) | PENDING_FINAL_REVIEW |
| REQ-035 | Exact mission commit and verified origin/test readback | external final Git closure receipt: exact path/blob hashes, origin/test SHA and clean tree | PENDING_REMOTE_CLOSURE |
| REQ-036 | Stop after diagnosis; preserve all prohibited downstream boundaries | scope_audit.json; no downstream execution; STOP after verified diagnosis | VERIFIED |
