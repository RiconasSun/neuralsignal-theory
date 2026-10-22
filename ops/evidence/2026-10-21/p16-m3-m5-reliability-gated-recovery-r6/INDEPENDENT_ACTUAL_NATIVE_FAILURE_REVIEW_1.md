# Independent review of the unique actual native preflight failure

Mission P16-M3-M5-RELIABILITY-GATED-RECOVERY-R6; reviewer /root/r4_interruption_review.
Decision ACCEPTED_ACTUAL_REQUIRED_PREFLIGHT_STOP_EVIDENCE_ONLY. Failure-evidence review P0=0/P1=0; this is not source/host/production acceptance. The known separate four auditor implementation P1 remain unresolved and preserved; the observed native runtime-image guard failure also remains unresolved. No engineering or scientific recovery PASS is issued.

## Exact observed failure and first mandatory STOP

The single documented candidate4 actual fixture invocation returned native exit1. Native execution receipt binds registration4 SHA396543dafa2fcdde594d1d5520ce4995dc286f0df49140722cb866073d26f09f, prior independent execution-only acceptance SHA25bb1c56e3c9f1eed26195e1d45ad1c2a9bfc5d5634037a7c618f401b5b94f8d and original complete traceback log SHA43fe4b408f7c2d1684e68cf7f5dc403f3190c1ba99a0c4fc98b3f90eb922e38a. Receipt completion timestamp is2026-10-22T03:19:02.8031258Z. It is an operator execution receipt, not a fabricated successful lifecycle result.

The trace reaches exercise's FIRST statement reg=guard(allow_unstarted=True), then verify_fixture_runtime, and fails:

os.path.normcase(native.own_identity()['image']) == os.path.normcase(str(FIXTURE_PYTHON))

AssertionError: Driver/role image differs from the registered real PE.

Current native/test source hashes still match the exact independently reviewed candidate4. Earlier sequential checks of the registered runtime metadata, PE hash, Python version, sys.executable path and -B/-S flags precede this assertion and did not raise in the preserved traceback. The actual image string itself is not preserved. Therefore the grounded observation is a rejected runtime-image identity comparison, not proof of a different binary, a source-hash defect, unsupported Job breakaway, a shutdown, or any particular alias/loader/WinAPI cause.

Required scientific verdict: STOP_HOST_RELIABILITY_REQUIRED_GATE, meaning a mandatory actual runtime/host-preflight implementation-environment interaction failed acceptance. Physical host inability to support the intended detached lifecycle has NOT been established. Root cause beyond the exact failed comparison remains UNKNOWN. No new query, environment inspection, code repair, alternate launch or second fixture is authorized after this STOP.

The source would not have created its software EXERCISE_CLAIM yet, but that absence does not restore mission permission to try again. The one actual registered exercise has been attempted and the first mandatory actual failure ends R6 scientific progression. Prior unexecuted static candidates and their rejection/repair history remain distinct from this actual failure. The prior candidate4 pre-execution decision allowed one test, never predicted actual runtime/Host/PhaseA PASS, and is retained unchanged.

## Actual execution/resource denominators and their limits

- Documented actual native fixture invocations:1, failed nativeexit1.
- EXERCISE_CLAIM created:0; W4 output root and lifecycle result4 absent.
- Fixture-created launcher/broker/supervisor/worker/grandchild births:0. Their only spawn_owned/Popen path lies after the failed exercise guard. This is not a claim that no OS/Python driver process existed: the documented actual driver invocation occurred; its native PID was not captured in the retained receipt.
- Ownership mutex/Event and child Job creation/assignment/resume stages:0 reached by this fixture; construction occurs after the absent claim.
- H01-H07 actual lifecycle cases completed:0; no actual breakaway, parent-exit liveness, containment, injected loss or duplicate-claim result was produced.
- R6 primary/independent reuse audit registrations/results/ledgers:0; newly qualified optimizer/B0 states:0/0. Historical4616+216 remain candidates, not new R6 admissions.
- Real A tasks attempted/passed/failed/incomplete:0/0/0/0; planned/unattempted1855/1855. Scientific FG/accepted/FD/AD/analytic calls:0. A failed preflight is separately reported, not relabeled as an optimizer numerical failure.
- Host memory/disk figures26.08GiB/62.26GiB belong to the earlier readonly audit only. No fresh resource measurement or full OS process-birth accounting was performed here. Actual image string, driver PID, exact start timestamp and detailed loader cause are unavailable, not inferred.

The only native operations on the failed path are runtime/process-identity inspection and ordinary module/metadata/PE reads; it does not reach model imports, protected saved arrays, raw neural sources or optimizer calls. This review read only existing source/log/receipt/public metadata and checked absence of expected outputs. It performed no new WinAPI/process/host query, fixture, private-state read, constructor or scientific calculation.

## Preserved boundaries and next authorized work

Host reliability gate=false; PhaseA=false; independent reuse admission=false; StageB not claimed; M4 complete=false; E/Final/M6/P17 forbidden and unexecuted. Original PhaseA24h claim remains unchanged; STOP does not create a new budget or entitlement. All R1-R5 historical failures and unknown R5 exit/time/cause remain immutable. No numerical or other root cause of the historical process losses is established or ruled out by this failure.

Four static auditor P1 were not resolved/accepted before STOP; unfinished engineering source must be preserved, not repaired or run to manufacture a gate. Existing source snapshots, rejected reviews, candidate4 execution-only acceptance, actual failure and any partial implementation attempts remain append-only evidence. No NATIVE_LIFECYCLE_RESULT_4.json or missing exercise claim may be retrospectively synthesized as though written by the original worker.

Remaining authorized work is saved-only sealing, integrity checks, truthful178-item trace, one-command saved-results reproduction, independent final/archive review and exact local publication preparation. This receipt review is an input to that closeout, not acceptance of a yet-uncreated archive/reproducer or Git payload. Public transmission is not authorized. Any future scientific retry would require a new separately authorized prospective mission; none is proposed or executed here.
