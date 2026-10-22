# Native candidate 3 engineering repair handoff

Mission: P16-M3-M5-RELIABILITY-GATED-RECOVERY-R6. Implementation scope: only the two designated P6 sources; no actual native lifecycle exercise, private reuse audit, model call or OS configuration change.

Candidate 2's exact original bytes are retained in CANDIDATE_NATIVE_2_SOURCE with CANDIDATE_NATIVE_2_PRESERVATION.json. Both unsuccessful prospective candidate reviews remain unchanged. NATIVE_CANDIDATE_2_TO_3.patch records the source comparison. Candidate 3 changes its work, native registration and result names to suffix 3. Root remains responsible for the final native source freeze, registration and independent pre-execution review; this handoff and the pure test registrations grant no actual exercise authority.

## Three reviewed defects

1. `valid_json` and `exact_json` require recursive exact JSON types, string dictionary keys and finite floats. The shared terminal classifier rejects bool/int and int/float substitutions at any depth, malformed expected certificates and unsupported/nonfinite values. Native returncode and containment/deadline flags keep exact types. Native acceptance never implies scientific or M4 PASS.

2. `finalize_owned` uses nested try/finally so cancellation-marker create/write/flush/fsync errors cannot skip cleanup. Both failure phases are retained separately. The kernel cancellation Event is set before cancellation-file IO. A failed marker or cleanup action makes the final fixture result unaccepted. If durable output itself is unavailable, an actual invocation must fail; successful evidence is never synthesized.

3. Every fixture Popen now goes through one `spawn_owned` implementation. Under one claim-derived named Win32 mutex it checks irreversible cancellation/uncertainty, creates suspended, obtains the actual Popen handle's FILETIME/image identity, retains that handle, assigns the exact Job where applicable, fsyncs the CREATED receipt, and only then resumes. No child instruction or descendant creation precedes durable handoff. Descendant spawning, worker supervision, deadline tree termination and injected supervisor termination follow the same ownership mutex. Cleanup holds that mutex, sets cancellation first and reconciles stable registered identities plus locally retained actual Popen identities. This replaces the two scans plus fixed sleep; it is not an assertion that a published subset equals every owned process.

A separate manual-reset uncertainty Event is part of the same claim-bound ownership gate. Abandoned/unavailable mutex outcomes set both cancellation and sticky uncertainty. A later role cannot erase the earlier uncertainty merely by reacquiring the mutex; cleanup cannot report all-owned success in that state. An unresolved kernel/identity/IO outcome prevents capability PASS. This does not establish protection against arbitrary machine-administrator intervention or an unobserved driver crash.

## API choice and budgets

Before any detached child creation, `detached_flags` examines the actual read-only inherited Job result. SILENT_BREAKAWAY_OK selects a launch without CREATE_BREAKAWAY_FROM_JOB; explicit breakaway is used only if explicitly permitted and silent breakaway is absent. Neither permission means rejection before Popen. There is no retry/fallback after an actual failed creation. The retained broker/supervisor outside-inherited-Job oracle is unchanged.

The original 120-second claim and 115-second operation/5-second cleanup split remain. Waits use the original absolute deadline; no positive minimum wait extends an expired deadline. Stable creation/image handles are retained; no PID taskkill was introduced.

## Evidence and limits

PURE_NATIVE_REPAIR_TEST_REGISTRATION_3 and its 40-test result are preserved as the first pure-input version. The affected follow-up is prospectively registered in PURE_NATIVE_REPAIR_TEST_REGISTRATION_4.json; PURE_NATIVE_REPAIR_TESTS_4.py extracts selected AST functions/classes without importing either actual native module. It uses in-memory fake kernel/Popen objects and a controlled publication-delay/cancellation interleaving. Its 40 assertions passed with actual test-run exit 0, recorded in PURE_NATIVE_REPAIR_TEST_EXECUTION_4.log and PURE_NATIVE_REPAIR_TEST_RESULT_4.json. These overlapping test counts must not be summed. Actual WinAPI lifecycle calls=0; actual fixture Popen calls=0; private-state reads=0; scientific calls=0.

The pure tests demonstrate predicate/control-flow behavior and source structure, not actual Windows containment or lifetime reliability. Required next step is independent static review of these exact candidate sources, then root's final registration. No real fixture, private audit or scientific stage may be inferred PASS from this handoff. The original Phase A clock is unchanged.
