# Independent saved-only closure tooling review 1

Mission: P16-M3-M5-SHUTDOWN-RECOVERY-R5. Reviewer: /root/r4_interruption_review, 2026-10-21.

Decision: **CHANGES_REQUIRED_P1**. Open P0=0; open P1=3. This review concerns new, unused closure deliverable tooling only. It does not invalidate the accepted production prefit gate, historical admission or any independently checked new state. It is not a mandatory real-state failure and does not request termination of the running scientific Job. No real saved reproduction, raw neural access, numerical state re-audit, objective, derivative, score or optimizer call occurred. The existing independent observer was neither restarted nor modified.

Reviewed exact candidates: `reproduce_saved.py` SHA256 `f5d5ba1b7a31c23c59e6f0dc534ab8099b3957fde1296ac70f7bf38c2b69a761`; `build_archive.py` SHA256 `b18d830cefcda31e18e3aa255c306914db622714d8209651862512befa813707`; PowerShell wrapper SHA256 `f3d08b4e17befd4101bcab72b84675c9d4af4a0be40c7e4f5099dd0fb9fff4d9`.

The supplied synthetic result 4 records 46 parser checks and actual native exit 0, with six unchanged producer hashes. Those tests are useful evidence for their exact candidate, not full real reproduction or proof of all builder/terminal branches. Existing original tooling versions, primary unsuccessful review and all synthetic attempts remain evidence.

## P1-001 — closed journals accept an unterminated final record

`lines()` uses read_text().splitlines() and rejects blank entries, but does not require a nonempty journal to end with the producer's newline delimiter. A syntactically complete JSON object without its final newline is accepted as a complete reservation, completion, terminal or initializer record. The closed-archive verifier must distinguish a complete producer record from a torn write; its handoff currently claims torn-entry rejection. The independent focused synthetic proof wrote only `{"event":"COMPLETED"}` without a newline and observed one accepted record.

Required correction: require a terminal LF for every nonempty closed journal before parsing. Preserve legitimate *complete-line* partial reservation prefixes; an explicitly unsupported torn record must fail closed rather than be silently promoted into accounting. Add negative tests for valid JSON without a final delimiter in FG, task/terminal, derivative and initializer parser surfaces, with complete-line prefixes still accepted. No producer or old evidence bytes should be changed.

## P1-002 — archive-builder path denial occurs after filesystem resolution

The reproducer's `local()` validates canonical repository-local relative syntax before filesystem access. The archive builder does not: reference paths are joined and passed into `relative()`, whose first operation is resolve(strict=True). Repository containment is checked only afterward. A malformed UNC, absolute, ADS or traversal reference may therefore cause Windows filesystem resolution, including potential UNC access, before rejection. A Python socket patch would not prevent OS-level UNC resolution. Builder tests are absent from the 46-method parser receipt.

Required correction: apply pure lexical local-path validation to each untrusted reference *before* resolve/stat/hash/open. Then verify the resolved location and symbolic/junction boundary. Use the same bounded roots/reference/exclusion contract as the reproducer. Add builder-focused tests whose resolve/hash/open operations are traps and prove nonlocal syntax is rejected before any trap is reached. An actual external source or network access is unnecessary and unauthorized. Preserve failed candidate and regression evidence.

The independent synthetic proof patched Path.resolve with a no-filesystem sentinel and showed that `relative(Path('//synthetic-host/share/not-local.json'))` reaches that sentinel. No network request or external file access was made.

## P1-003 — native and scientific STOP labels are not connected to their evidence

`stage_and_native()` checks the stage digest, matching Job strings and several native field types, but omits the frozen producer's integer supervisor PID and `Local\\P16_R5_<pid>_...` Job identity rule. The independent synthetic metadata proof was accepted with supervisor_pid='not-an-integer' and job_name='INVALID_PRODUCER_JOB'. The builder has stronger rules, so the independently verifying reproducer currently does not enforce the same contract.

More materially, the stopped branch accepts any scientific_status in an allowed list plus no-retry/boundary booleans. It does not check whether stop.type/message generates that category under the frozen pure stop classifier, nor connect it to the actual terminal FAILED row or native deadline/clock/process/zero-exit-without-completion case. A ProcessStop receipt relabeled STOP_NUMERICAL_REQUIRED_GATE could therefore be echoed as a reproduced scientific verdict without numerical-failure evidence. This is a static finding from the stopped branch; no full run() or real state fixture was executed to manufacture an example.

Required correction: implement a saved-metadata-only terminal validator matching the actual frozen producer categories and receipt precedence. Join a worker failure to its exact task-terminal exception when present; independently handle bootstrap errors and native deadline, clock, abnormal process or zero-exit-without-completion records. Keep actual native returncodes and unknown fields truthful. Apply the builder's supervisor/Job identity rule in the reproducer too. Test swapped categories, incompatible worker/native evidence and malformed native identities, while retaining genuine implementation/bootstrap and budget/interruption stop cases. Missing original native receipts should remain unsupported/fail closed until a separately reviewed additive external-loss schema exists.

## Preserved positive findings and next gate

The candidate imports no scientific/model module and decodes only same-folder, exact-member saved fit/certificate NPZ bundles after receipt checks. The arithmetic enforces float64 coordinate AD/four-scale FD certificates, original fixed-step acceptance, outward PG, accepted/FG/halfway/endpoint associations, producer-specific R3 scalar journals, original caps, canonical task order, full historical admission and complete-M4 approval/selection bindings. Archive coverage and finite exclusions are substantially stronger than the original candidate. The wrapper anchors the repository, checks the Python launcher, uses -B and propagates failure.

These positive checks do not compensate for the three missing guarantees above. Amend only the new closure tooling, preserve prior candidates and this unsuccessful review, run fresh sufficient synthetic regressions, and present exact revised source hashes for independent re-review. Do not run real saved reproduction while science remains active. No M4_APPROVAL or scientific/publication permission is granted by this document.

Focused independent proof source: `INDEPENDENT_SAVED_TOOLING_REVIEW_CHECK_1.py`; result: `INDEPENDENT_SAVED_TOOLING_REVIEW_CHECK_RESULT_1.json`; execution: `INDEPENDENT_SAVED_TOOLING_REVIEW_CHECK_EXECUTION_1.log`, actual exit 0. All three checks used synthetic JSON or trapped filesystem operations, no real state arrays, no network and no scientific module calls.
