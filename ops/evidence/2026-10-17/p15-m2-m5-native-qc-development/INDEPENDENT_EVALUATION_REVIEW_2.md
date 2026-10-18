# Independent internal E integration review 2

Mission: P15-M2-M5-NATIVE-QC-AND-DEVELOPMENT. Review date: 2026-10-18 UTC.

Decision: **REPAIR_REQUIRED_BEFORE_E_ACCESS**. Open P0: 0. Open P1: 1, the remaining main-state dependency part of r1 P1-01. R1 is preserved. R1's durable-control-evidence and seven-family findings are resolved on this candidate. No real A/B/E/Final neural data, cache, network/source request, real fit or scientific batch was read or run by this reviewer. Only this new review artifact was added.

## Remaining P1: main preprocessing/task descendants are not checked before release

The revised verify_E_gate correctly binds every available and unavailable sensitivity case, reconciles the exact subject/case preparation and plan, checks completed sensitivity item hashes/gate identities and checks the reference metadata roster. However, it pins only the READER_GATE.json and PRODUCTION_GATE.json files themselves; it does not traverse those gates' stored hash maps, nor directly require/check each main `states/{subject}_A_PREPROCESSING.json` and `metadata/{subject}_task.json` before claim/E access. These descendants are subsequently used by extract_role, FrozenPredictors/control preparation and source_state.

Hashing a parent manifest does not establish that the current child bytes still match its frozen expectations. The current valid synthetic all-unavailable-case fixture demonstrates the gap: verify_E_gate returns successfully without any main preprocessing or task file existing. The actual worker would then discover missing/stale main inputs after consuming its one-shot claim, or could use altered unbound state bytes.

Required narrow repair: mandate and verify the current main state/task/QC identities for every fixed subject before claim/E I/O, or enforce the equivalent complete existing reader/production dependency closure. Reconcile reference metadata's main-state/task hashes with those exact files. Retain direct complete-case bindings already added. Add missing/altered main state/task and mismatched reference-child hash regressions that perform zero E I/O and consume no batch claim. This requires no new scientific policy, data access or security architecture.

## Resolved findings and positive verification

- Case closure: every subject x eleven-case state, including UNAVAILABLE states, must now be in the E hash map. Content identities, case definitions/status, B selection/QC hashes and unavailable reasons are checked. verify_plan enforces full case denominator, chosen baseline lambdas, exact fit plan and frozen budgets. Actual sensitivity records must match completion hashes, plan items, terminal status and sensitivity-gate identity before release.
- Durable controls: suite journals are created exclusively; START/COMPLETE/FAILED events are flushed/fsynced. Every replicate's start/seed and completed model results/mapping hash are retained before progression. A later failure preserves the completed prefix and failure ordinal/seed. Existing suite journals prohibit another run; a missing journal cannot silently be recreated by append_event. The batch's exclusive claim continues to deny crash/repeat/concurrent consumption.
- Model set: N1/N2/N4 now explicitly request B1-B4,D,C,S, while N3 requests B1/B4 only. B0 remains in original-result predictors but is excluded from control bundles. No new realization is drawn per contrast.
- The fixed source/target/filter/coverage/statistical semantics reviewed in r1 are otherwise unchanged. The unclosed main dependency remains a pre-release blocker despite these repairs.

## Fresh reviewer execution

Executed all **13 test_evaluation tests** with ResourceWarning treated as error: PASS, exit0. The three new tests exercise unavailable-case binding, preserved interrupted-control prefix/repeat denial/seven-model behavior and missing-journal failure. All original ten arithmetic/access tests remain.

Additional independent synthetic injection: interrupted the third reference call, after two completed replicates, using a predictor that would expose eight models if no restriction were supplied. The journal durably retained two completed seven-family results without B0, followed by REPLICATE_FAILED_IMMUTABLE with replicate=2 and completed_prefix=2. A repeated call failed on exclusive journal creation and left the exact journal bytes unchanged. No real model/data was involved.

## Exact reviewed SHA256

| File | SHA256 |
|---|---|
| paper15_dev/evaluation.py | 12a07251f51be6bd6e56a6cac738621ee5781375e6868add02d12e50cf1e92da |
| paper15_dev/evaluation_support.py | 01fe5bf8fb3000f4d53cf8b133de23ea6d2f26c2a82b00a07d93e500fd9062a8 |
| paper15_dev/test_evaluation.py | 6767e86921027ac9135e97830ae92d66a9242ba4b42cf7fdf4a7835c66165b05 |

The other independently assigned review's cohort/summary checks are separate required evidence; this report does not waive them. No executable E approval follows until the final source-bound engineering and mathematics reviews and all actual predecessor gates pass. No historical failed review is replaced by this repair progress.
