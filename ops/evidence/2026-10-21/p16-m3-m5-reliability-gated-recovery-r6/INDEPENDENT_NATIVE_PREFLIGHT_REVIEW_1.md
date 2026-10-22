# Independent native lifecycle candidate-1 execution-preflight review

Mission: P16-M3-M5-RELIABILITY-GATED-RECOVERY-R6.
Reviewer: /root/r4_interruption_review.
Decision: REJECTED_PREFLIGHT_IMPLEMENTATION_DEFECTS. Open P0=0; open P1=3. Do not execute candidate1 or treat it as actual-host capability evidence. No host reliability gate, Phase-A gate, private reuse audit or real optimization is accepted.

This is static source/metadata review only. Source hashes and registration match the binding. AST parsing confirms syntax without importing or executing either native module. The native fixture directory and NATIVE_LIFECYCLE_RESULT_1.json are absent at review; no synthetic/native probe was performed. These defects are demonstrated before the actual host capability exercise and are not evidence of a failed CREATE_BREAKAWAY capability or scientific STOP. Preserve candidate1 source/registration/review exactly; repair in a separately frozen candidate under the existing unextended Phase-A clock.

## P1-01 — fail-closed terminal semantics are asserted labels, not tested acceptance logic

Locations: test_native_lifecycle.py:145-151,202; native_process.py:74-101.

The native supervisor returns an exit code and deadline flag only. The fixture computes normal_pass using native0 plus NORMAL_DONE.json.exists(), nonzero_failclosed using returncode==17, and zero_without_receipt_failclosed using native0 plus an absent EMPTY_DONE.json. Those predicates demonstrate the injected exit/absence, but no actual acceptance function rejects these outcomes. The injected-loss receipt simply writes no_PASS=True/no_retry=True. A future implementation that incorrectly accepts any native0 would still satisfy the empty_zero fixture predicate and produce all_cases_pass. Even the normal receipt is not parsed/validated for task/claim/job/native process identity or synthetic completion value. This does not satisfy registered H03/H04/H06 as fail-closed acceptance evidence.

Minimal prospective repair: introduce one strict terminal classifier, suitable for actual production reuse, requiring native0, no deadline/process-loss condition and an exact valid completion certificate bound to its consumed attempt/claim, process and Job. Feed the actual supervisor outcomes and parsed receipts into that classifier. Nonzero, zero-without-receipt, malformed/incomplete/wrong identity certificates and injected supervisor loss must yield explicit STOP and never acceptedPASS. Preserve the distinct expected injection-test PASS versus simulated scientific-worker STOP. Add direct regression assertions that prove a permissive-native0 classifier would fail. No model/objective changes are needed.

## P1-02 — detached exceptional cleanup and registered total fixture ceiling are not enforced

Locations: test_native_lifecycle.py:73,79-88,160-221; native_process.py:66-71,74-98.

After a successful breakaway launch, the supervisor deliberately escapes the outer tool Job. The driver only catches exceptions while waiting for the launcher and kills that launcher; no encompassing finally owns and reaps the detached broker/supervisor on a later wait_file/assertion/JSON/native failure. A launcher broker-wait timeout similarly leaves its detached child outside containment. Fixed per-wait timeouts do not establish the registered max_fixture_seconds=120 ceiling. taskkill subprocess.run has no timeout and the child.wait after termination is unbounded. Apart from BREAKAWAY_DENIAL, exceptions bypass the create-only final failure result entirely. Guard/source/checkpoint failures can therefore lose cleanup and auditable failure classification, which is the exact behavior the reliability mission must test.

Minimal prospective repair: one monotonic fixture-wide120s deadline checked/clamped by all waits and subprocess calls, plus the original Phase-A UTC/monotonic guards. Register only owned process/Job handles immediately at creation or verified discovery and use a top-level finally to terminate/reap those exact test descendants on every failure path. Persist a truthful create-only failure receipt with actual available exit/status and unknown fields where appropriate; do not invent native completion. Add synthetic failure-path tests for post-breakaway driver exception, missing/corrupt receipt, launcher/broker timeout and total ceiling. Do not kill unrelated tool/host processes or reset the Phase-A clock. A future actual registered native capability failure still requires HOSTSTOP, not an oracle revision or fallback.

## P1-03 — PID-only liveness and taskkill can target a reused unrelated process

Locations: native_process.py:48-71; test_native_lifecycle.py:132-136,187-201.

process_alive opens the process currently assigned a numeric PID; no creation identity is retained. H06 later runs taskkill.exe /PID live['pid'] /F using that number. The original detached supervisor could exit between its liveness check and taskkill, and Windows can reuse the PID. The test would then have authority over an unrelated process. Numeric PID receipts alone also cannot prove which exact parent process died. The fixture is only authorized to terminate its own synthetic lifecycle.

Minimal prospective repair: bind each original process to an OS creation identity and a stable process handle. Verify detached-process identity against its registered launch/receipt before accepting the handle; wait/terminate using that same retained handle. Do not verify creation time and then return to a PID-based kill, which leaves the race. Retain no child Job handle that defeats kill-on-last-close. Preserve actual termination and cleanup evidence, with ownership failure STOP. Test identity mismatch/exit-before-open/reused-PID rejection using synthetic or pure Windows-API fixture seams before the one actual registered native exercise.

## Other source and host observations

The proposed positive path does request CREATE_BREAKAWAY_FROM_JOB with no fallback. Broker and supervisor independently require in_job=false; supervisor waits for both broker and launcher disappearance, and the independent driver then checks supervisor liveness. A Job is created before the child is launched suspended, job.assign precedes resume_suspended, every synthetic child calls exact require_job and the old Job helper has kill-on-last-close/no-breakaway plus existing-name refusal. Exclusive-create LF/fsync JSON and duplicate creation denial are present. These are useful static design facts, not actual lifecycle PASS.

The actual read-only host audit reports26.08GiB available memory,62.26GiB disk free, session1 and inherited tool-Job membership. Its resource floor passes; capacity and worst-case journal safety are not established by that floor. The retained event evidence does not establish R5 root cause: listed System IDs have Volsnap/UserModePowerService providers rather than a matching shutdown claim, and two Python crash events name a different omeganeon Python3.13 path/PIDs. Localized powercfg output contains replacement question marks; do not infer unavailable policy labels from it or treat query exit0 as a full policy proof. Preserve raw results and explicit limitations; no OS mutation is authorized.

Current root cause remains UNKNOWN; no numerical or other cause is established or ruled out. Original R1-R5 stops and scientific definitions remain immutable. The native real exercise has not been consumed. New candidate source and registration must preserve these findings and be independently checked before execution. No private state, synthetic run, neural source, E/Final access, fit/gradient/AD/FD/score, OS setting change or network action was performed by this review.
