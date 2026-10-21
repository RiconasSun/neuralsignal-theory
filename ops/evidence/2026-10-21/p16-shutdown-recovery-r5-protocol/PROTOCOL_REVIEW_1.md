# Independent R5 protocol review 1

Current mission: `P16-M3-M5-SHUTDOWN-RECOVERY-R5-PROTOCOL`.
Proposed future execution mission: `P16-M3-M5-SHUTDOWN-RECOVERY-R5`.
Base: `5ed9a6854248cd250a097a9e657519ad0a057f64`.
Reviewer: `/root/r4_interruption_review`, 2026-10-21.

**Decision: ACCEPTED_PROSPECTIVE_PROTOCOL_ONLY.** Open P0=0; open P1=0; protocol/documentation bug_count=0; warn_count=0. No unresolved scientific-contract shrink was identified. This accepts the prospective drafting package, not its future execution or numerical results. Current local commit and remote/clean checks must still complete before the whole protocol-delivery contract can be reported complete.

## Scope and reviewed evidence

The review inspected PROSPECTIVE_MISSION.md, PROPOSED_EXECUTION_POLICY.json, MISSION_SPEC.json, the metadata builder and verifier, VERIFY_PROTOCOL.ps1, SOURCE_PINS.json, RECOVERY_TASK_PLAN.json, REUSE_TARGETS.json, ROSTER_IDENTITIES.json, CURRENT_HANDOFF.md, PROTOCOL_HANDOFF.json, the 40-item requirement baseline/outcomes and native metadata-verification output. Only already-public BASE Git objects, text and JSON/JSONL/CSV metadata were read. No private saved-state file or neural array was audited, no scientific module was imported, and no synthetic or real numerical model, objective, gradient, AD, FD, likelihood, score, source transport, E or Final operation was executed.

The baseline was frozen before protocol construction and contains the exact 40 MISSION_SPEC requirements. The inspected trace has 37 VERIFIED and 3 IMPLEMENTED_UNVERIFIED items: actual independent review, scoped commit and remote/clean handoff. It does not report future reuse audits or scientific gates as passed. REQ-036 may cite this actual review; REQ-037/038 remain dependent on actual Git receipts. No 40/40 completion is pre-signed. All historical R1/R2/R3/R4 stops, source definitions, failed attempts/reviews and the shutdown explanation remain unchanged. The pinned historical daily-operations file is preserved; the new namespace supplies an additive current handoff.

## Independent metadata checks

An independent standard-library/Git-object comparison verified all 33 public source pins against the exact BASE bytes, sizes and SHA256. The 952 R3 reuse-target task identities and result paths/hashes match the published compatibility matrix; the 3,040 R4 targets match the published completed outcomes and unique COMPLETED journal receipts; the 216 B0 target identities and result paths/hashes match their published analytic matrix. These comparisons verify target indexing only, not the private fitted states or their current eligibility.

The 3,992 optimizer target IDs and 2,479 proposed new task IDs are unique, mutually exclusive and together equal the original 6,471 optimizer tasks. The new task list retains the exact original R4 order, with one interrupted task first and 2,478 unattempted tasks. Every task explicitly requires the original initializer; the first task is `763236014:S02:S:None:11:GLOBAL`. The existing failed, diagnostic or partial vectors cannot be warm starts or admitted endpoints. B0 is accounted separately. All 3,992+216 R5 admission flags remain false and their new audits remain NOT_EXECUTED.

All 27 Development and 27 locked Final mouse identities are unique within their sets and the sets do not overlap. Development retains 5 BO/22 FC. The inherited optimizer options, diagnostic scan, checkpoints and seed-selection definition match the frozen original policy. Budget arithmetic was independently checked: at most 2,479 attempts, 14,874,000 optimizer FG pairs, 3,718,500 accepted iterations, 7,437 independent AD and 7,437 analytic checkpoint calls. The inherited free-coordinate FD budget is at most 24P per task, with the stated total ceiling 21,894,528 derived from P<=368. This maximum is a ceiling, not permission to replace the original parameter packing or spend unused budget on a task.

The independent native command below actually returned exit 0; the captured command, scope and output are in `INDEPENDENT_PROTOCOL_METADATA_1.log`. Parent native output is separately retained as `VERIFY_PROTOCOL_FINAL_2.log`.

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\paper16_shutdown_recovery_r5_protocol\VERIFY_PROTOCOL.ps1
```

The reported PASS is exclusively public protocol-metadata consistency. The verifier/builder use standard-library JSON/hash/Git operations and contain no scientific-module import, model execution, private-array read or transport fallback. The verifier does not certify future controller enforcement or substitute for registered synthetic/real-role tests.

## Prospective scientific and resource contract

The new proposed preflight stage is bounded to 24 hours and must include complete saved-evidence admission, independent review, implementation/synthetic certification and exact future source freeze before any real A optimization. Every one of the 3,992 optimizer and 216 B0 targets is mandatory. Missing, inconsistent, corrupt or numerically insufficient required evidence stops the future mission without cherry-picking states, recomputing old certificates or switching to full refitting. B0 uses its original analytic MLE/checkpoint-label certificates and does not acquire an invented optimizer trajectory or optimizer ftol label. Old optimizer origins retain R3 ftol=1e-12 and R4 ftol=0; counterfactual execution-equivalence claims are forbidden.

The proposed new A/complete-M4 stage is separately bounded to 48 hours, one optimization worker and the fixed 2,479 attempts. It does not resume, reset or extend the consumed R4 clock. The clock starts before any real A objective/derivative call and includes checkpoints, selection, M4 sealing and independent review waiting. Inclusive 6,000 FG/1,500 accepted-iteration limits retain the original semantics; 6,001/1,501 requests must be denied before execution. Every diagnostic reservation/completion is separately journaled. No retry, replacement seed/solver, post-failure extension or restart after another interruption is authorized. Completion within the proposed budget is not promised.

The mathematical models, original initialization, normalization, penalties, bounds, ridge grid, lambda=1 historical B1-only B selection, features, scalers, masks, unit/trial choices, cohort and statistical hypotheses remain fixed. Original PG<=1e-5, AD<=1e-8, fixed h=1e-5 FD<=2e-5, all three checkpoints and all registered FD scales remain mandatory; solver success cannot override them. S07 and N4 retain their registered precision definitions. All three D/S seeds must pass before the original A-objective/tie rule can select a state. Existing verified saved Development A is the only future input source; missing inputs cause STOP rather than reacquisition.

Future process/Job, interruption, budget, source/role and numerical negative tests are explicitly required before real fitting. These tests have not been run in this protocol mission. No new cryptographic custody architecture or malicious-administrator protection is claimed. Any mathematical change or new optimization policy lies outside this proposal and requires a different protocol.

## Complete-M4, E and interpretation boundaries

Only an independently accepted complete M4 containing all 6,471 optimizer-task accountability and 216 B0 certificates can lead to an E authorization request. This protocol authorizes neither E release nor E scoring; a separate explicit owner decision must bind the complete M4/hash, original E specification and one batch, with separate resource/stop terms. All original eight model levels, six contrasts, sensitivity/control suites and statistical requirements remain. Final C/D, M6 and P17 remain forbidden. The inherited policy's A/C wording does not grant Final calibration authority; the current machine policy expressly limits inputs to saved Development A and keeps E/Final authorization false.

Post-A/B exposure, historical lambda selection, numerical amendment and cross-R3/R4 state reuse remain disclosed. Future Development results remain exploratory. Unfinished work is not numerical PASS, a proven numerical FAIL, a biological negative or equivalence. No causal connectivity, physical primitive, CWP/NAP proof, independent-laboratory replication or Final confirmation follows from this protocol review.

After mechanical documentation updates, a separate binding will record the exact final protocol/evidence bytes. Local commit and remote readback receipts must be actual, outside self-containing public hash cycles, and restricted to the two new protocol namespaces. Future private-derived numerical publication retains its own explicit permission boundary. Delivery must stop after protocol handoff. Separate execution approval tied to the final protocol commit is necessary before any future private audit, synthetic numerical execution or real fitting.
