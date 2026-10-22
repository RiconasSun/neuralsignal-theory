# Independent native lifecycle candidate-3 execution-preflight review

Mission P16-M3-M5-RELIABILITY-GATED-RECOVERY-R6; exact BASE e1aab9622a7e63b99335a529d8ad0107f611dc8c. Reviewer /root/r4_interruption_review.

Decision: REJECTED_PREFLIGHT_RUNTIME_TOPOLOGY_DEFECT. Open P0=0; open P1=1. Do not execute candidate3. Actual native capability exercise remains unconsumed; no host-capability failure, hostPASS, PhaseA approval or scientific-stage permission is established.

## P1-01 — selected Windows venv redirector violates the exact self/created registry

Locations test_native_lifecycle.py:76-77,101-120,156-196, especially171-174. Registration3 invokes paper16_m1/work/runtime/Scripts/python.exe and command() recursively uses sys.executable. spawn_owned registers immediate Popen PID/FILETIME/image; receipt registers the process actually executing the module; cleanup requires every self identity to be the exact CREATED identity. The selected Windows virtualenv launcher introduces a separate interpreter process.

Existing actual HOST_AUDIT_NATIVE.json shows runtime/Scripts/python.exe PID72504 parenting uv CPython3.11 python.exe PID71136. Subsequently, the separately preregistered readonly RUNTIME_LOADER_READONLY_RESULT_1.json confirmed sys.executable is that venv launcher (SHAde13d8017f63cb63b0b5bfd2f25e69245c9196433a224856ca1abde1e24d0cb7) and sys._base_executable is the real uv python.exe (SHA28d2965d061656abbe3a46100bd3342d1152185289445d489782a21a8cfe9b57). It reports no child created by query, no WinAPI fixture/model/neural calls. This metadata confirms the relevant runtime topology without spending the native exercise.

Exact AST extraction of cleanup into an entirely in-memory fake registry/gate reproduced the contradiction: CREATED launcher=(PID100,FILETIME1000,venv/python.exe), IDENTITY launcher=(PID101,FILETIME1001,base/python.exe), same claim/registration. The function raises AssertionError: Executing role lacks durable ownership handoff. Pure-check actualexit0, no imports of native module, no WinAPI/Popen/filesystem fixture/model calls. This is a static implementation/runtime incompatibility, not proof the actual host lacks breakaway/lifecycle capabilities.

Minimal repair: prospectively register/invoke the exact real base PE for this stdlib-only fixture, freezing path/hash/version, or explicitly model and verify every redirector/interpreter ownership edge and containment. Do not weaken the exact all-owned registry or ignore implicit children. Fixture runtime selection does not automatically amend/certify the scientific optimizer runtime; later full numerical/source/runtime certification remains required. Root acknowledged this defect; preserve candidate3 unchanged, register candidate4 under the original PhaseA clock, and independently review before actual execution.

## Previous P1 repairs now accepted statically and by isolated pure checks

Recursive valid_json/exact_json enforces JSON types, finite floats/string keys, rejecting bool/int, int/float and nested coercions. Independent AST-only pure checks reject three former type counterexamples plus NaN, accept equal nested certificates, and retain strict native flags/returncode. finalize_owned catches cancellation OSError and invokes cleanup in nested finally; injected pure callbacks observed cancel then cleanup, preserved the failure and denied successful finalization.

Every fixture Popen is inside spawn_owned under one kernel ownership mutex: create suspended, capture stable identity, optionally assign exact Job, persist CREATED with fsync, resume, release. Cancellation sets an irreversible Event under the same mutex; cleanup holds it over its registry reconciliation. Abandoned mutex sets sticky uncertainty and cannot PASS. OpenMutex0x00100001 supports wait/release; OpenEvent0x00100002 supports wait/set. Normal handoff does not wait for child execution while holding this mutex; child receipt can acquire after parent releases. This fixes late-birth ownership logic in the intended single-process interpreter topology, subject to the redirector defect above.

FILETIME/image verified handles replace PID-only taskkill; the supervisor handle is retained through injection. Child Job kill-on-last-close/existing-name denial and exact require_job are unchanged. Assignment occurs before resume. Normal/nonzero/emptyzero/tree outcomes feed the real terminal predicate; expected injected STOP never implies scientific PASS. H06 injection holds the ownership mutex, preventing termination halfway through durable handoff.

Readonly outer flags0x3000 indicate SILENT_BREAKAWAY_OK and KILL_ON_JOB_CLOSE without explicit BREAKAWAY_OK. Pre-birth silent/explicit selection is prospectively registered; independent pure predicates select silent for0x3000, explicit only for0x800. Actual outside-Job and liveness oracle is unchanged; no post-failure fallback. Native liveness, Job containment, runtime topology and120s whole lifecycle are still untested.

## Evidence and boundaries

Candidate2 preserved source hashes match originals. Root pure-test result4 binds exact candidate3 source and reports40 assertions/no failures/no native calls; those40 are not native evidence and are not summed with this independent pure check. Registration/source hashes match binding; W3/result3 are absent. No actual native fixture, protected state, real model/derivative/score, E/Final, OS change or network action was executed. Original24h PhaseA and120s fixture budget are unreset. R1-R5 STOPs remain immutable; R5 root cause UNKNOWN, neither numerical nor other causes established or ruled out. The next action is a new exact-source candidate review, not actual execution of rejected candidate3.
