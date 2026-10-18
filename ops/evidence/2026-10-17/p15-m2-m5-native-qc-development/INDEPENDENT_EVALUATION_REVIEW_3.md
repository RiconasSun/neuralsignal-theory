# Independent internal E integration review 3

Mission: P15-M2-M5-NATIVE-QC-AND-DEVELOPMENT. Review date: 2026-10-18 UTC.

Decision: **ACCEPTED_E_ENGINEERING_COMPONENT_ONLY_PENDING_ACTUAL_PREREQUISITES**. Open P0: 0. Open P1: 0 within this engineering review. The remaining r2 dependency finding is resolved. Earlier unsuccessful r1/r2 reviews remain preserved. This report does not assert that actual 610 main fits, sensitivity fits, B selection or final pre-E evidence already pass; it issues no executable E gate.

## Dependency and cohort repairs

verify_E_gate now traverses and verifies every stored hash in the frozen production and reader gates. Each fixed mouse's main preprocessing, task and QC files must also be directly present in the E hash map; main state must be in the production gate, and task state in the reader gate. It checks subject/A-role, selected unit IDs, QC/task hashes, original M1 freeze identity and reference metadata's child hashes before returning. Existing checks still cover the complete subject x eleven-case set, unavailable states/reasons, exact sensitivity plan, chosen lambdas/budgets, fit item/status/gate identities, independent review evidence and exact source identities. The former parent-manifest-only gap is closed.

Control summaries now require a unique exact fixed subject set, all four suite keys and only completed or registered-coverage-unavailable suite statuses. Sensitivity summaries require the unique exact subject x eleven-case Cartesian set. Repeated mice, missing cases or unknown suite failures cannot inflate paired coverage or silently disappear. run() and saved_audit pass the sealed selection roster to these interfaces. A source-defined unavailable sensitivity/reference panel can still retain its prescribed paired subset and unavailable label; it does not change main primary eligibility.

The r2 durable append-only suite/replicate journals, exclusive no-repeat batch claim and explicit seven-family control restriction remain unchanged. Their earlier independent interruption/prefix/model-set checks therefore retain relevance to the unchanged functions. No mathematical model, threshold, random schedule or fit budget was changed by these access/cohort repairs.

## Fresh independent verification

- Executed all **13 test_evaluation tests** with ResourceWarning treated as error: PASS, exit0. Expanded gate fixtures now cover missing main state/task/QC bindings, altered task bytes and the already required available/unavailable-case conditions. Summary tests now reject duplicate/missing control mice and duplicate/missing sensitivity cases.
- Independently altered a main preprocessing descendant and updated only its direct E-gate hash: verification still rejected the stale production-parent expectation. This checks actual descendant traversal, rather than only a stale top-level E hash.
- Independently altered a reference metadata child task hash and updated its top-level E-gate binding: verification rejected its disagreement with the frozen current task state.
- Independently exercised five summary violations: duplicate control mouse, missing control mouse, unknown suite status, duplicate sensitivity subject/case pair and missing sensitivity subject/case pair. All were rejected. Valid complete synthetic identity sets were accepted.
- Only synthetic fixtures in disposable project-local directories were used. No actual state/role data, cache, fit journal or scientific result was read by these checks. No implementation or test oracle was modified.

The parent's reported full112-test run is separate evidence; this reviewer directly ran the 13 affected evaluation tests and additional dependency/cohort injections above, not all112 tests.

## Exact reviewed SHA256 identities

| File | SHA256 |
|---|---|
| paper15_dev/evaluation.py | 83d80d0d05607e312a2bead824de1092e9a8490f06e1ba81447ec792c40bb472 |
| paper15_dev/evaluation_support.py (unchanged) | 01fe5bf8fb3000f4d53cf8b133de23ea6d2f26c2a82b00a07d93e500fd9062a8 |
| paper15_dev/test_evaluation.py | 837e36b4daeb2428bde121b4aee12ab361bf80c9e561c22c7c1637516d8c952b |
| paper15_dev/saved_audit.py (updated interface call sites inspected only) | 7a902ed8cfb8d64db35ddcde3ef1f0206969825f3745aab5d3d28a52a874b3a4 |

## Remaining actual release boundary

Before E execution, the final engineering and mathematical reviews must apply to the exact final code; the actual full A-attempt/B-selection/sensitivity/source/reference receipts must satisfy these checks; and a concrete gate must bind the actual approved reviews and all required artifacts. Missing/unavailable scientific coverage must retain its registered interpretation. A passing synthetic engineering gate is not a successful real control suite or scientific validation.

If those actual prerequisites pass under the owner's existing mission, this exact reviewed worker may perform the single frozen Development E batch. Any crash/failure remains an immutable incomplete assessment with preserved journals; no resume, extra draw, repaired scientific control after E or retuning is approved. Final C/D neural access remains forbidden.

No real A/B/E/Final neural observation, effect, cache, source/network request, fit or scientific suite was accessed or executed by this reviewer. Only this new review artifact was written.
