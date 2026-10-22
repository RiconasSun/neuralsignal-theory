# Independent native lifecycle candidate-2 execution-preflight review

Mission: P16-M3-M5-RELIABILITY-GATED-RECOVERY-R6. Reviewer: /root/r4_interruption_review.
Decision: REJECTED_PREFLIGHT_IMPLEMENTATION_DEFECTS. Open P0=0; open P1=3. Candidate2 must not run the actual host exercise. No actual host capability failure has been observed, no real native exercise is consumed, and no private state/PhaseA/production/scientific gate is approved.

The exact candidate2 registration/native/test hashes match the accompanying binding. Candidate1 source copies are byte-identical to their rejected original hashes and preservation manifest; candidate1 review remains unchanged. Candidate2 output directory/result are absent. This review used static source and one isolated pure classifier check, not the actual module import, WinAPI or any spawned-process fixture. No clock was reset.

## P1-01: completion equality is not strict JSON identity

Location: native_process.py:149-170, particularly completion != expected at166.

Ordinary Python dictionary equality equates booleans with integers and integers with floats, including nested values. Exact AST extraction of only classify_terminal (without imports or other source execution) produced these actual results under native0/valid containment/no deadline:

- completion {complete:1}, expected {complete:true}: ACCEPTED_NATIVE_COMPLETION.
- completion {n:1.0}, expected {n:1}: ACCEPTED_NATIVE_COMPLETION.
- completion {state:[0]}, expected {state:[false]}: ACCEPTED_NATIVE_COMPLETION.
- equal string-only claim: ACCEPTED_NATIVE_COMPLETION.
- missing completion or altered string claim: STOP.

Pure predicate inspection command actualexit0. The first three are strict-identity counterexamples. Current normal fixture completion values are strings, so this is not evidence that an actual current host exercise failed; however the registered shared production-capable strict classifier does not yet fulfill its advertised general contract.

Repair: exact recursive JSON type/value comparison, reject unsupported/nonfinite values, and ensure expected itself is a valid frozen structured certificate. Native returncode must remain exact int, flags exact bool, and malformed/incomplete completion must STOP. Add meaningful nested bool/int, int/float, nonfinite and malformed tests, preserving successful equal-certificate behavior. Do not change the scientific model or gate.

## P1-02: failure writing cancellation bypasses driver cleanup

Location: test_native_lifecycle.py:103-107 and305-324.

The top-level finally calls cancel() before cleanup(). cancel catches FileExistsError only. If the create/write/flush/fsync of CANCELLED.json raises OSError (for example disk or permission failure), the finally exits immediately and neither owned cleanup pass, cleanup status nor durable result is attempted. Detached children are outside the tool Job, so this is a real missing exception boundary. A finally statement alone is not proof of unconditional cleanup.

Repair: nested try/finally guarantees handle-bound cleanup regardless of cancellation-marker failure, preserving the primary failure and separately recording cancellation/cleanup failures wherever durable output remains possible. Failure to persist an authoritative marker is never PASS. A pure injected filesystem failure before/during cancellation must assert cleanup is still called and no acceptance is possible. Do not repair this by skipping fsync, ignoring the error or broad process termination.

## P1-03: fixed two-snapshot cleanup is not an ownership/quiescence proof

Locations: test_native_lifecycle.py:76-87,142-150,163-166,255-258 and305-313.

Launches check guard, then start an already-running detached child, then publish CREATED identity. Cancellation and these steps are not atomic. A broker can pass guard and create its detached supervisor, then be terminated by driver cleanup before the CREATED supervisor record is durable. The child may itself not have reached its identity receipt. cleanup snapshots only current IDENTITY/CREATED files, sleeps at most0.1seconds and scans once more; no barrier proves that there are no in-flight births or late records. all_published_owned_processes_cleaned can be true for an incomplete published set. This does not prove cleanup of every owned process on the exceptional path. The child may eventually observe CANCELLED and exit; eventual unobserved self-exit is not the required bounded ownership/reaping evidence.

Repair: make ownership durable before the child may execute or spawn further descendants, for example CREATE_SUSPENDED, capture stable creation/image handle identity, persist registration, then resume with failure cleanup through that same handle; an equivalent acknowledged handoff is acceptable. Retain actual owned handles until transfer is confirmed. After cancellation, reconcile creation/ownership to bounded quiescence under the original120s deadline and verify all registered handles are dead; fail closed for unresolved/late births. Add a controlled publication-delay/cancel interleaving test. Do not extend the deadline or count only published records as every owned child.

## Repair progress accepted statically, actual evidence still pending

Candidate2 introduces a shared terminal classifier and checks real native outcomes; missing/altered completion and nonzero/deadline outcomes now reject in the inspected predicates. This is a substantial repair of candidate1's label-only H04, subject to P1-01 above. A unique120s claim with115s operation/5s cleanup split, explicit cancellation and driver finally are present, subject to P1-02/03. The previous PID-only taskkill was removed. OwnedProcess compares FILETIME/image, keeps a stable verified handle through liveness and injected termination, and never issues PID taskkill. Candidate1 P1-03 PID-reuse kill is statically repaired. Its eventual actual host behavior remains untested.

No new mathematical/source-role/numerical-policy alteration was found. Literal CREATE_BREAKAWAY no-fallback, actual outside-Job checks, suspended worker assignment before resume, exact worker require_job and kill-on-close remain. Actual native capability must still be tested once only after a repaired exact-source pre-execution review. An actual registered host failure requires permanent STOP_HOST_RELIABILITY_REQUIRED_GATE before private qualification/science; it is not interchangeable with these unexecuted implementation defects.

No native process API, actual lifecycle probe, neural source, private saved state, fit/gradient/AD/FD/score, E/Final access, OS setting change or network action was executed. Pure nonprocess predicate cases above do not constitute the actual host capability exercise. R1-R5 STOPs and the original PhaseA24h deadline remain unchanged.
