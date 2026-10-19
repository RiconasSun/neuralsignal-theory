# Final independent scientific/source and archive-content review

Mission: `P16-M2-NATIVE-LINK-DIAGNOSTIC-R1`.
BASE: `a0065c66aaa84ad39a985903fcd77bdc1e1e711c`.
Decision: **ACCEPTED_DIAGNOSTIC_ARCHIVE_CONTENT**.
Open P0: **0**. Open P1: **0**.

This is independent internal review of the complete diagnostic candidate, not independent-laboratory review or peer review. It accepts the diagnostic content for normal archival closure. It does not certify a future Git commit, remote readback, clean gate, production reader, numerical running semantics, M2 scientific PASS, or permission to resume scientific execution.

## Candidate and complete contract

I checked the exact `paper16_linkdiag_r1/DIAGNOSTIC_FREEZE_MANIFEST.json` SHA256 `ce6670ca01bdad66c71fc769557962feaad65037c943f865f1078a84cc3ab284`: all **100** unique payload paths, bytes and SHA256 match the independently fixed `payload_contract.py` set. This is a nonempty fixed denominator, not merely a self-selected list of existing files. Every payload hash was independently checked. The manifest's exclusion of its own bytes, ignored work, final review and post-freeze reproduction log is explicit; the additional reviewed closure identities appear below.

I read the complete owner request, all **247** lossless trace rows and all **60** semantic acceptance items. Independent comparison establishes that the first 243 baseline rows are exactly every nonempty owner line in order, with correct source-line references, and the remaining four retain the explicit preservation/review/Git/stop conditions. Baseline and trace IDs/text/line references agree without deletion or reinterpretation. The supplementary acceptance oracles cover source identity, every material link/security case, metadata compatibility, actual event chronology, budgets, historical preservation, diagnostic claims, saved replay and closure. Conditional A-only proposal requirements remain conditional: B means no such proposal or activation, not omission of an applicable deliverable.

The current content trace correctly has **234 VERIFIED and 13 OPEN_CLOSURE**, not 247 completed claims. Open rows are REQ-016, REQ-027, REQ-207, REQ-209, REQ-231, REQ-232, REQ-233, REQ-234, REQ-242, REQ-244, REQ-245, REQ-246 and REQ-247. Semantic acceptance has **55 VERIFIED and five OPEN_CLOSURE** (AC-054, AC-056, AC-058, AC-059, AC-060). Review, final defect fields, archival handoff, actual commit/readback/clean and final stop appropriately await executed closure predicates. There is no prematurely verified owner Git requirement.

## Scientific/source conclusion

The single grounded disposition remains **B — SOURCE_SCHEMA_INCOMPATIBLE** under the frozen executed source contract. The report answers Q1–Q8 with actual metadata and keeps two mechanisms distinct:

* The original four-component HardLink-only traversal fails at the final `/processing/running/running_wheel_rotation/timestamps` component. Its actual serialized class is **SoftLink**; the three preceding path components are HardLinks. Its literal and normalized absolute target are `/processing/running/running_speed/timestamps`.
* Safe fixed-target metadata traversal establishes same-file identity and equal object address **19550656**, not just matching shapes or a plausible path. The timestamp target and end timestamps are `<f8`; their metadata units are seconds. All three relevant vectors have **365911** rows.
* The separate schema contradiction is `/processing/running/running_wheel_rotation/data` native storage **`<f4`**, with radians/identity conversion, versus the unchanged executed reader's all-three-float64 requirement. `ROOT_CAUSE.json` correctly identifies this concrete offending dataset while preserving the combined diagnostic exception's generic alias `problem_path`. It does not falsely label timestamps float32 or rewrite the original failure.

The legitimate internal alias does not by itself require a changed running-feature definition. It also does not clear the independent storage-contract blocker. Source storage precision, computational precision and the scientific estimand are explicitly distinguished: promoting float32 storage cannot recover absent source precision. Whether the frozen reader restriction is an implementation error or requires a prospective contract amendment remains a separate owner decision, not an inference made in this mission. Under B, no routine outcome-A-only compatibility patch proposal, production repair or automatic M2 restart is supplied or authorized.

Object identity does not validate rotation/time row correspondence, finite/order/duplicates, durations, source clock scalar values, strict-past causal lookup, coverage, physiology or biological inference. These remain untested. The metadata do not establish source corruption, biological QC failure, cohort feasibility/impossibility, neural prediction or scientific recovery. The report, README, root cause, handoff, claim audit, verdict and daily prefix preserve these limits consistently.

## Actual evidence, scope and resource reconciliation

I reused my earlier exact-source preaccess and independent actual-metadata review, verified unchanged source bindings, and independently replayed the retained actual metadata again in this final review. No new network request, real source/NWB open, dataset-value access, neural array, fit, scoring, AD/FD, QC or Final C/D access was performed.

The retained response identity is the sole original Development mouse **726162197**, session **750749662**, file **1026124242**, size **2818447324**, ETag `"5a68875f05100"`. The actual 44 responses are HTTP206 with exact registered Content-Range/ETag. Durable request reservations, response headers, payload accounting and completed-range records agree with the receipt. All 44 retained raw metadata bodies validate their lengths/hashes and overlapping bytes, with no missing-range download fallback.

The diagnostic has **one** source inspection, **44** requests, **85712** payload bytes, **85756** conservative reserved bytes, **5.406** seconds; external supervision completed with child exit0, no kill, before the registered 600-second deadline. These remain within 8 MiB/128 requests/131072 bytes per request/one-object/no-retry limits. The immutable original M2 ledger separately remains one failed source, **39/81912/81951**, **5.468** seconds, 27 Development sessions unattempted. This diagnosis is not a retry or retroactive success of that M2 attempt.

The offline HDF5 metadata replay reproduces **all 33 events**, the exact exception/status, pending-to-resolved alias chronology, object identities, dtypes and metadata. Inspector rows, original receipt rows and immutable JSONL agree exactly. I also independently verified `COMPONENT_AUDIT.json` against the receipt and all 33 CSV flattened rows against their corresponding parent/object/resolved metadata. My initial ad hoc CSV adapter assumed flat fields; correcting it to the documented nested parent and resolved metadata made the complete comparison pass. That reviewer adapter issue did not alter package code, evidence or expectations.

All **334 M1** and **58 M2** declared payload hashes and sizes independently pass. The original reader and STOP remain immutable; original 55 candidates/28 Development (5 BO,23 FC)/27 Final BO, flash design, B0–B4/C/D/S, 12 sensitivities/four references, selection/statistics and attempt budgets remain unchanged. New actual running/identity-scalar/neural dataset values, additional source sessions, physiology, model work, B/E, Final, production repair and M2 restart are zero.

## Reproduction, regressions and unsuccessful evidence

I inspected the saved-only entry point, network denial, dataset-value canaries, retained-range reader and tests, then independently ran:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\paper16_linkdiag_r1\reproduce.ps1
```

Actual independent result: **exit0**, Windows PowerShell **5.1.26100.9711**, pinned runtime, **15 tests PASS** (0.374 seconds), exact100/334/58 payload checks, 33-event replay, B disposition, zero new network/dataset values. The tests cover valid alias/Hard/Missing/External/cycle/unauthorized targets, literal normalization, identity-versus-shape, units/scaling/parent conflicts/capacity, source pins, HTTP/budgets/deadlines, external timeout/duplicate denial, partial accounting, saved corruption/missing/traversal and float32 rotation with otherwise valid metadata. Synthetic execution is not real scientific QC or future production certification.

The rejected preaccess candidate and unsuccessful review remain preserved. I additionally verified the rejected saved-reproduction ZIP against its receipt and every listed archived hash (59 archived files). Original inspected registration, inspector, link logic, range reader, tests and actual results remain exact. The saved verifier's emitter correction copies the mutable callback dictionary at emission, matching the original immediate JSONL serialization; the three-way 33-row equality assertion remains intact. Later changes add runtime/baseline/preservation checks and the 15th regression, without changing the source inspection, recorded outcome or scientific oracle. No source retry was used to repair tooling evidence.

## Preservation and conditional closure

The saved prechange tree is exactly `git ls-tree -r -z BASE`, containing **36647** entries. Current tracked diff against BASE contains only `ops/daily-operations.md`, with no tracked deletion. The reviewed daily adds **1332 bytes**, and its entire BASE suffix is byte-exact. Current untracked mission files are confined to the new P/E namespaces. `git diff --check` passes. Full all-blob remote verification and final clean proof remain future execution obligations.

`CLOSURE_CONTRACT.md`, README, verdict and HANDOFF_FIELDS honestly retain pending future transport identities. I inspected ignored `work/archive_handoff.py` as a closure helper: it binds accepted content and extra closure hashes, stages an exact path list, compares staged bytes, requires the expected parent/remote SHA, reads every changed remote-tracking blob, verifies daily preservation and clean state, and writes only an ignored post-execution overlay. I did not execute it or any Git mutation/network operation. Review does not establish that its future predicates have run. Normal commit/push commands, fresh fetch/ls-remote, all changed-blob readback and final clean proof must actually complete before the 247/247 and 60/60 terminal overlays or archive PASS are asserted. Any intervening relevant byte change requires affected review/verification again.

Content is suitable for the already authorized normal **origin/test** archive, conditional on those actual closure gates. No PR, main mutation, force push, broad staging, next mission or scientific restart is permitted by this review. STOP after the diagnostic archival handoff.

## Exact reviewed identities

SHA256 below; paths beginning `E/` expand to `ops/evidence/2026-10-18/p16-m2-native-link-diagnostic-r1/`, and `P/` to `paper16_linkdiag_r1/`. The manifest cryptographically binds the full reviewed 100-path hash/size list.

|Path|SHA256|
|---|---|
|P/DIAGNOSTIC_FREEZE_MANIFEST.json|ce6670ca01bdad66c71fc769557962feaad65037c943f865f1078a84cc3ab284|
|ops/daily-operations.md|57e60d70bec2c70f7d76af03f6d2e6c59a1cec1b1dae4c468fefecd44eca4d6c|
|E/SAVED_REPRODUCTION_3.log|1c53b166ad2c9cff6a112f8696a09b33812d461a745fb42cc095706c3fb04133|
|E/OWNER_REQUEST.txt|639855609c68618895eceb8dc51f25487778ea1f60543ec51a3d296933e48604|
|E/baseline.json|ab01d85c87a856bcbedefdb1d47dc98b9d9286ae2ad336d8019e36b1f9ae2cd1|
|E/goldenstandards.md|b451437cac81f4c5962775143e804d08d2d8c20b6b0af52b3434fac0952c37d0|
|E/verdict.md|ec3fca1e378569749f782fe85cd2e801fe1cca06e84e2989e524eb7034146c5e|
|E/ACTUAL_METADATA_REVIEW.md|c63227a125b63d75f32107587a1e86668d80033be8c0371096238a88f9380668|
|P/ACCESS_REGISTRATION.json|72badf889acdafbaf02f9179ec1412dfea85ef211f2a7e520d1bd40d82835600|
|P/links.py|a1e4812418e18b66f6c410ff9cf846d6e1a1e813540de0b9b1dafe6ac1a92141|
|P/inspect_source.py|cd9979978a5f266eb005449c1ed4233d56d89930a57422cf34540411ac02f71b|
|P/saved_ranges.py|1d1c854a921787cb3050b3328b84dc67962704025bae41813f2c79e1772a73c4|
|P/test_diagnostic.py|51b9909bcda69bc15f35c940d345c0650f66090a59dd206ac049ec40de5cc016|
|P/test_saved_evidence.py|705721c6dd01e7310c6aebbe8141ad545d3f64b4cd5c42ed0a52087270648210|
|P/verify_saved.py|11b1d2f2508b63d6ce956129bdd2bcfd7b9bb00b51926b9b4f0349f844cc0dc5|
|P/payload_contract.py|82c681b4a8841e3d4075d05f3f7e6069d86dd3e20abcc7e2198096ce2ec324ec|
|P/REQUIREMENT_TRACE.json|ba2291d4cf9f7d1d25ef5c2f4fd4cafffd96867651f54e6c15db3cff43a96121|
|P/SEMANTIC_ACCEPTANCE.json|df72277da0a2d6a2e7a2859ea45891a03f36ae70d6e987d847cdbde8794ab5d8|
|P/CLOSURE_CONTRACT.md|fc2f72c4c758e370425ef8ab1c667c4c910700f6d457b0ec045862f2e194a142|
|P/HANDOFF_FIELDS.json|9dc43ab8a1aba3740f5bcb25cb994b630e0b8ebfa7990e403dfc08b68ff4a682|
|P/LINK_DIAGNOSTIC_REPORT.md|3d85398b3dd7f6f307ec61aa1208f9a2ef1a5972b08f43bf03f4d16e8cf1673d|
|P/ROOT_CAUSE.json|58afc8236ab003d540ce4b7d868e52aef6bc9752ff59b9d82dd279f4585ac415|
|P/COMPONENT_AUDIT.json|0b893f482e2c6e2db12576a0ca58a07ad788eac38bccd3775425f15816a7efac|
|P/COMPONENT_AUDIT.csv|f96f4256f1ca8ef59eb2b7611a8a426803d9b55bbdf74b7f5723c832958fcdac|
|P/RESOURCE_ACCOUNTING.json|aeeec26a60aee621fc73f776273d302888cb647d8dd22cf036aae483dbcf9d77|
|P/SCIENTIFIC_CLAIM_AUDIT.md|bfd6bb14c6d0ef68d3bc6193e468cb559bac084b2a53dbddd92ae9b0d671e0ab|
|P/README.md|269c7896be3de54b63e268dc4822ff4cf247b26b00aaaa0b0fc18fd3239f350b|
|P/work/archive_handoff.py (ignored, closure helper only)|8a8996258b48bccb72e91f67c67e2d939ebbb86cca24f7e98954d3f8f9f28e88|

No unresolved P0/P1 reporting, source, scientific-scope or archive-content defect was identified. Reviewer writers are **COMPLETE / QUIESCENT** after sealing this report. Only this new review report was written; no frozen payload or historical evidence was modified.
