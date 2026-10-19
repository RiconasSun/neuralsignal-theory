# Independent R4 source-only preaccess review 1

MISSION: P16-M2-BOUNDED-NEURAL-SOURCE-RECOVERY-R4
Reviewer: /root/r4_policy_review (independent internal review; not an external custodian)
Review timestamp UTC: 2026-10-19T20:29:15.535858+00:00
BASE / inspected HEAD / origin/test: d60e913c528feecfaaab9397ba1a6157c511526d
Decision: ACCEPTED_R4_SOURCE_ONLY_PREACCESS
open_P0: 0
open_P1: 0

## Scope and findings

Reviewed the complete 237 nonempty owner lines, all 120 atomic baseline requirements, prospective recovery policy, registration, source/reader/controller/transport/saved-replay code and all four test modules. The baseline is prospective and remains OPEN until actual execution/closure evidence resolves each applicable requirement. This acceptance concerns the source-only preaccess candidate below. It is not actual fourth-source acceptance, full M2 admission, model/numerical certification or a predictive scientific PASS.

P0 findings: none. P1 findings: none. Code was frozen throughout this review; this reviewer changed no implementation, policy, scientific criterion or source evidence and issued no approval artifact. No real source HTTP, range decode, source restart, model fitting, B/E neural scoring or Final access occurred during review.

## Independently executed verification

1. Transport + native-reader + resumed-prefix integration: 32 unique tests PASS (unittest, pinned Python3.11.15 runtime). All network calls in these tests are synthetic/blocked. The integration source_pass print refers solely to an owned synthetic HDF5 fixture, not a real source.
2. Actual Windows controller/Job/CIM tests: 5 unique tests PASS on the native host. An initial sandbox-only invocation produced 3 ResourceStop errors because Get-CimInstance was inaccessible, plus 2 PASS; no child/source access proceeded in those failing checks. The identical unchanged tests then passed under the authorized native-host execution path. This was an environment capability distinction, not a repaired test, ignored failure, real-source retry or scientific attempt. These test outputs remain in this review tool transcript; original parent test logs remain frozen in the table.
3. Independently validated all 35 preaccess payload sizes/SHA256 plus the manifest itself. Compared the entire original28 object list with R3: identical, 5 BO / 23 FC. Verified original27 Final identities remain denied.
4. Ran verify_history: all 373 R3 public payloads and 679 private payloads match frozen identities, except the explicitly allowed daily prepend whose original exact bytes remain its suffix and frozen snapshot. All 849 prior M1/oldM2/R1/R2 manifest entries and frozen imported source versions match.
5. Independently ran saved-only verify_saved with socket connection denied: all 228 R3 A states, including the first19 fourth-source captures, verified by file/native-array hashes and unchanged A QC; exactly3 historical complete sources reused. R4 requests/bytes/attempts/retries/model fits all0; M2_verdict null; recovered_range_verified false. Current 3 admitted BO mice are historical completed-source physiology only, not the full28 M2 verdict. Private raw arrays are required for this replay; a public clone alone cannot repeat that QC.
6. Compared R3 and R4 reader source directly: only the validated-prefix parameter, contiguous-ID assertion and skip of already verified prefix peak/index/spike payload reads were added. Scalar/root/probe/index/native timestamps/observation/A extraction/physiology mathematics remain unchanged. First fresh candidate is original candidate20 (unit950930971), not a rerun or replacement of the first19.

## Contract and safety assessment

The exact file1026124500, size2537645144 and ETag are pinned. HEAD occurs once before GET in the production fourth path and cannot fall back on failure. Existing540672-byte prefix is checked and preserved; only507904-byte suffix448282624..448790527 is requested, checked for exact206/range/ETag/length and concatenated at the original1048576-byte range offset. The retained combined digest proves saved byte/provenance integrity; the policy correctly makes no unavailable independent upstream whole-file-checksum claim.

Each required range has at most2 requests, adapter retries0/no redirects, only the two frozen timeout exception classes permit attempt2, fixed2s backoff, and a durably consumed R4 slot precedes retry. New R4 limits are2 slots/source,6 global,8GiB/512MiB reserved payload,1MiB ranges and8192 HTTP/source including HEAD. The known historical R3 timeout is separately preserved and does not count as a new R4 timeout; an R4 suffix timeout does count. Non-timeout semantic/header/partial-body failures stop immediately. Partial bodies, reservations and attempts remain append-only. The production caller stops the source on any exhausted or required error; no later mouse or third range request is used as fallback.

The source stage has one new48h UTC/monotonic/same-boot deadline before HEAD; claims forbid phase restart/reset; actual native Job tests prove descendant termination. The first3 completed sources are denied transport reopening. R3 is still3 complete /1 failed partial /24 unattempted and never reclassified. Original19 fourth-source states are reused only after frozen-file/native-array/QC verification. The new fourth record retains its exact old UNIT_QC prefix and only newly read candidate rows append. Physical HDF5 ranges may include unreturned bytes; the narrowly authorized full selected-unit-row integrity decode and A-only logical exports remain explicit, with no malicious-admin or separate third-party custody claim.

All original A physiology, native timestamps, true-zero handling, gap-safe ISI, curated/optional observation support, numeric lowest8 selection and one-time common-support checks remain. Mandatory source/common-support failure is not silently treated as individual biological attrition. Original B/E metadata coverage is allowed; B/E neural outcomes cannot select units or affect QC. Final sources are denied. No model implementation/fit/B selection/E evaluation path is activated. Full28 complete dispositions and unchanged14 overall /3 BO /10 FC floors gate the later source-only M2 decision.

## Subsequent gates remain mandatory

Only source-only preaccess is accepted. The real fourth-source result must independently pass complete-source/QC/transport review, including exact retained source/range/state identities and every new A artifact referenced by its immutable QC records, before objects[4:] are permitted. Full M2 or truthful stop review must reconcile all new and historical ledgers and source dispositions. The same deadline continues through the review pause. Model fitting and B/E scientific evaluation remain unauthorized regardless of a later source-only PASS. The final archive still requires saved-only reproduction, exact-file staging, origin/test remote readback and clean verification. No numerical or scientific historical failure may be cleared by this engineering decision.

## Exact reviewed payload identities

| Path | Bytes | SHA256 |
|---|---:|---|
| ops/evidence/2026-10-19/p16-m2-bounded-neural-source-recovery-r4/BOOTSTRAP.json | 793 | 0f13749a5b035f1d75387f6ecf25e248d2b7024db01313e24c5103d245416fbe |
| ops/evidence/2026-10-19/p16-m2-bounded-neural-source-recovery-r4/CLI_COMPATIBILITY.log | 420 | 0462d9954ee57ff9623e4628dd938302600c12b5c7c96e73564b9d4b857b82c3 |
| ops/evidence/2026-10-19/p16-m2-bounded-neural-source-recovery-r4/goldenstandards.md | 3527 | ebbd73e1ee6c381b7634f1989220978c57f9bee596be1fb550e1de54a3d72efc |
| ops/evidence/2026-10-19/p16-m2-bounded-neural-source-recovery-r4/OWNER_LINE_COVERAGE.json | 82075 | 6c86fc87a1d501d22400e926fba31c1fc61eecd6faa3dcae802c9c83e1199628 |
| ops/evidence/2026-10-19/p16-m2-bounded-neural-source-recovery-r4/OWNER_REQUEST.txt | 11168 | d218f7baed29a7570f18d312d07f7c9ef56f6871af4f5f1c6c242c04e855689d |
| ops/evidence/2026-10-19/p16-m2-bounded-neural-source-recovery-r4/PRE_FIX_TEST_INTEGRATION.py | 5483 | 4d0a155a37ff6400e599243edff7e7f22a8bb474669fc44de5d94185d13c3c62 |
| ops/evidence/2026-10-19/p16-m2-bounded-neural-source-recovery-r4/PREACCESS_SAVED_REPLAY.log | 1009 | 511ac46a94e2fc22ca180b6c4a7d379815dfcbe435af16f17c538292ff0111bf |
| ops/evidence/2026-10-19/p16-m2-bounded-neural-source-recovery-r4/R3_DAILY_FROZEN_SNAPSHOT.bin | 75807 | ab112e031102ac2086163989e19219503aa0c2a8a13acdf69f4e940654325df8 |
| ops/evidence/2026-10-19/p16-m2-bounded-neural-source-recovery-r4/R3_SAVED_REUSE_NATIVE.log | 948 | fed48bf9b304f983df53da3761c649a2ad199b537f391bde8da0c758a5f77108 |
| ops/evidence/2026-10-19/p16-m2-bounded-neural-source-recovery-r4/READER_PROJECTION.json | 749 | 88c432eb27f7ea6f412f18012b0d67fb03222c97df4505807e154f0a7dce685c |
| ops/evidence/2026-10-19/p16-m2-bounded-neural-source-recovery-r4/REQUIREMENT_BASELINE.json | 22533 | d6fa7377d154e9c28e54ffee899a1a4ffd55faa6a22b37b33a7197953e1dafae |
| ops/evidence/2026-10-19/p16-m2-bounded-neural-source-recovery-r4/SYNTHETIC_HOST_1.log | 8518 | c84c01f9634cd0eb32b9e5380b0a55c95a3223c3fd4728ac41f0ae93ab24a9a9 |
| ops/evidence/2026-10-19/p16-m2-bounded-neural-source-recovery-r4/SYNTHETIC_HOST_FINAL.log | 6759 | 784123632b6d5874c54cec6b5af7175ff56814ff34c129221deaf625e5462080 |
| ops/evidence/2026-10-19/p16-m2-bounded-neural-source-recovery-r4/SYNTHETIC_INTEGRATION_2.log | 401 | 2ab3d49eba7ab37c37d09c83a0f7222492548f5484f569d9a55b0334d7830c43 |
| ops/evidence/2026-10-19/p16-m2-bounded-neural-source-recovery-r4/SYNTHETIC_SOURCE_1.log | 5416 | 4863ebc0fcd77186086369e3359dbe1134a74ca965adf71fa0828a307ae950bc |
| ops/evidence/2026-10-19/p16-m2-bounded-neural-source-recovery-r4/TEST_SCOPE_NOTE.json | 522 | abf3ddb9c761a2a7716019d27c89ef9202fc7e7b4c2b8cb77d514134a9d4fb95 |
| ops/evidence/2026-10-19/p16-m2-bounded-neural-source-recovery-r4/TOOLING_RECEIPT.json | 935 | 4a9699d00211f5423d0ad4d42089bbe47bc22c8a1420195752f4be964304f0aa |
| ops/evidence/2026-10-19/p16-m2-bounded-neural-source-recovery-r4/WRAPPER_DRY_RUN.log | 89 | 887026a50521f3ebe11c84ef4c4dbdd602f7017bea3b451b5c261a3793d0de0a |
| ops/evidence/2026-10-19/p16-m2-bounded-neural-source-recovery-r4/WRAPPER_DRY_RUN_AUTHORIZED.log | 18267 | 48b1fbda58d6547d87b0316b461c28a67579052285e3271394f3e5c298068bd5 |
| paper16_source_r4/.gitignore | 28 | 49c03ed3cea6e6960d782305d5593f03f2a9d0ce92a8856864eac4e2dde9db01 |
| paper16_source_r4/ACCESS_REGISTRATION.json | 54853 | d4101f4ba67865e189d253408e31789fff49b3ac5cd1077b8dd4f7b9a81298aa |
| paper16_source_r4/core.py | 3807 | e7959793b3baf76f49fa274d5ecf936bd41f0e688eb4c3c2df73f7dfa12e61d3 |
| paper16_source_r4/MISSION_SPEC.json | 9471 | 80e996d28003fe60d50e030a317272b32458d8ec0f31c46cb902594b870159d6 |
| paper16_source_r4/neural_reader.py | 10877 | 1c3cb5ffaafea2ef2d5b0da3cf0765e51464890786d48b6bb9ec8a10b4de4b26 |
| paper16_source_r4/R3_REUSE_MANIFEST.json | 260509 | 96d193b9536c36a862c60da5fd1ec3876739a29fbf92928a24279381e5867565 |
| paper16_source_r4/README.md | 1467 | 08ec36a8d016b0c91c629924522856ffef59a802c97b26d887aed9e39413213a |
| paper16_source_r4/RECOVERY_POLICY.md | 7395 | a21b5cde21b21bef3a17a0b39834a582b82962f7c5abe34794722df65e48ffd8 |
| paper16_source_r4/reproduce.ps1 | 632 | 226e5f73e510ad6697deb69414ed92bb73f6184392b3f80706094d5bf448f35e |
| paper16_source_r4/run_sources.py | 11989 | ec61211a08c109f5ee18674852c2aa7aaadfdbb61156ac03936b950ac76fadfe |
| paper16_source_r4/test_controller.py | 3462 | a85197953a348ece2816d27f9c94360d9213b19cf3d7fa1674969a9055335a9e |
| paper16_source_r4/test_integration.py | 5649 | 973d0fe42a5f2152d0f1460931884a105da92be1b3258711c83612f1ea1992e0 |
| paper16_source_r4/test_reader.py | 2463 | b9a0c198388df53a6e79d1e9709cf43611dff80af6ba6ca3d61ebef49bbe6d9c |
| paper16_source_r4/test_transport.py | 10938 | 3afe0ac6ad323ed493526d28daaea0138e8390d409fd1140270912fe95de5fce |
| paper16_source_r4/transport.py | 13787 | cf4aaf17c63dd16fed768f750aa86567847fcbde5cfef07bd60cd49aaac01392 |
| paper16_source_r4/verify_saved.py | 8145 | 6157664f308db9df73623a7c59174927869160897e6b2b59e5448efdbcd75c46 |
| paper16_source_r4/PREACCESS_FREEZE_MANIFEST.json | 7263 | 6e60d32a3568baaca84e13c02c99b9fd049e11fdd87ad83163d27b532f615a57 |
