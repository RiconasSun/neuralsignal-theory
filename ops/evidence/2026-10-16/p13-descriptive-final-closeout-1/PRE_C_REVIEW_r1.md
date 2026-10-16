# Independent pre-C implementation and numerical review r1

Mission: `P13-DESCRIPTIVE-FINAL-CLOSEOUT-1`.
Reviewer: separate local internal reviewer; not external peer review.
Decision: **REQUEST_CHANGES — PRE-C EXECUTION NOT YET ACCEPTED**.
Open P0: **0**. Open P1: **1**.

## P1 — Add regression coverage for both explicitly corrected D failure paths

`IMPLEMENTATION_DELTA.md:9` registers two execution corrections: persist each mouse's primary JSON before a sensitivity failure, and STOP on any new mandatory nonrecent coverage failure. These are consequential retention/stop guarantees in a one-shot execution that forbids post-D repair. Their code is present at `paper13_descriptive_final1/final_D.py:223` (before the call at230) and249–252, but neither correction has a focused regression in the frozen test suite.

The two integration cases at `test_final_D_integration.py:35` and49 exercise a successful bundle and an exception from the later null loop. The latter checks the already aggregated nine-mouse primary result at57; it does not inject an earlier sensitivity exception or inspect the affected mouse's primary JSON. Both cases can pass if the early persistence correction is removed. Neither forces `required_coverage_pass=False` for a nonrecent mandatory panel, distinguishes that failure from the narrowly exempted recent-event panel, or asserts that no valid final result is emitted. Existing pure sensitivity tests establish how coverage is calculated; they do not exercise this new runner's STOP branch.

Before execution acceptance, add synthetic runner regressions that (1) raise from sensitivity scoring after a primary score and verify saved primary/bin/state identities, failed one-shot status, no subsequent mouse/control execution and retry denial; and (2) make a nonrecent mandatory panel fail coverage and verify the serialized panel report plus failure/no valid final bundle, while showing the existing recent-only 6/9 exception remains descriptive and INCONCLUSIVE. The checks should fail when their respective correction is removed. This follows the supplied mission regression requirement; no real data, new draws, scientific definition or threshold change is needed. Preserve this failed review and its reviewed identities before repair/re-freeze.

## Supported scope and checks

The owner attachment expressly authorizes a separately amended descriptive C-to-one-D route, conditional on implementation review, full C numerical acceptance, complete state sealing and later independent pre-D review. It removes only the failed four-null completion prerequisite and retains the known 6/9 coverage exception, unavailable conditional reference and broad INCONCLUSIVE claim locks. It does not clear original M6 or permit a replacement conditional null. No additional routine post-C human permission is required when the registered gates pass.

Verified `PRE_C_IMPLEMENTATION_FREEZE.json` SHA256 **b95a3bedc00c5fe6eebe0c9fdf4823a1b8e7ec1a7a5dd8b78f87cd107ff9f449**, all **26** entries, **120** input-freeze entries and the transitive historical identities checked by `common.policies()`. The retained E arrays each have999x10x9 finite values and their unique completion markers/hash identities; original M6 remains FAIL. All original nine final mice retain60 C and60 D epochs; B*=B2 and development-selected policies are unchanged. At review there is no new C approval, real C fit directory or D execution directory.

Independently ran:

`python -m unittest paper13_descriptive_final1.test_final_C paper13_descriptive_final1.test_final_D paper13_descriptive_final1.test_final_D_prior paper13_descriptive_final1.test_final_D_integration paper13_descriptive_final1.test_seal_final_C paper13_descriptive_final1.test_route`

Result: **23 tests PASS**,28.731s. Tests use synthetic fixtures under ignored new-package work directories. The saved original-numerical receipt reports60 passing unchanged oracles; synthetic test success is not actual C/D success. No real fit, control draw, network request or D outcome was accessed by this reviewer.

The AST-equivalence checks cover original C loading/design/fit_mouse and D window_sets/export/consume/run_controls. Actual model/objective, independent AD/fixed FD, bounded optimizer, seeds, selected policies and shared C-B4 offset remain original imports. The schedule is15 baseline+3 D+3 S+1 C per mouse, **198** maximum, from scratch on C; C-only scaling and selected-state identities are retained. The seal/pre-D code checks full model dimensions, exact22-configuration rosters, all three coordinate certificates, trajectories, C seed choices and source/scaler/Q identities. Actual198-fit acceptance and sealing remain future evidence.

The three-control adapter delegates unchanged original operators and seeds, denies conditional generation, and matches original stress means/q95 arithmetic in the differential test. Conditional p/Holm fields remain unavailable; three controls cannot establish the missing conditional guard. D export retains primary and original shifted pre-tone masks, rejects response-bin inclusion, preserves partial exports on source failure and consumes its exclusive once-only marker before decoding. The source adapter retains original range/cache/ETag/budgets and adds current D authorization/consumption checks before the inherited constructor, with a separate operational journal and combined old/new budget usage. No extra security framework is required or claimed.

No additional P0/P1 mathematical or authorization defect was identified in this scoped review. The missing runner regressions above prevent an unconditional pre-C acceptance under the owner's requirement to review the actual C/D paths before fitting. After that narrow verification repair, obtain fresh review of the new frozen state. A later complete-C/reporting/pre-D review remains mandatory before any D outcome access; this review never grants that release or certifies scientific or full-mission PASS. Git closure remains pending actual receipts.
