# Independent sensitivity implementation review 2

Mission: P15-M2-M5-NATIVE-QC-AND-DEVELOPMENT. Reviewer: independent agent `/root/gradient_review`. Date: 2026-10-17 America/Los_Angeles.

**P0=0; P1=1. Case fitting is not yet admitted.** The prior S05 scientific-definition defect is resolved. A remaining plan-validation gap must be fixed before the sensitivity plan/gate is finalized. Review 1 is preserved. Only this review report was written; no actual neural cache, A/B/E/Final array, network or real fit was accessed.

## Prior S05 P1 resolved

Both `sensitivities.prepare` and the optional-warm-up path of `selection.extract_role` now pass `stimuli-.5` as the behavioral epoch reference to `nuisance`. `observed_arrays` still uses the separately registered shorter neural warm-up/reset for S05. This preserves the behavioral support, wheel reference and prior completed-trial-code freeze while changing only the prescribed neural history estimand. The main default warm-up remains .5; its behavioral reference is unchanged.

The added nonconstant-wheel regression compares every scored nuisance column between primary and shortened-neural-history fixtures, requiring exact equality, and verifies that deliberately substituting the wrong short neural reference produces a difference. The reviewer independently ran all **eight current sensitivity tests PASS**, including this regression and the nondefault numerical cases. No scientific threshold or case definition was amended.

## P1 — plan validation permits omitted cases and changed solver budgets

`sensitivity_fits.verify_plan` reconstructs attempts only from the preparation records supplied to it. It does not verify that those records cover the complete unique admitted-subject by eleven-case manifest; nor does it verify the solver options consumed by `run`.

An independent synthetic call using one admitted subject, `preparation={'cases':CASES,'records':[]}` and a plan with zero attempts is accepted. The same accepted plan can contain `solver={'maxiter':2001,'maxfun':80001}`: these options are ignored by the validator, despite contradicting the frozen 2000/80000 policy. The preparation's eleven-definition list alone does not prove that every actual case was retained as sealed or explicitly unavailable. A source-bound gate can bind the wrong plan perfectly; hashes do not replace these scientific completeness/budget checks.

Required repair, before any case fit:

- Require exactly one preparation record for every admitted-subject/case pair; reject missing or duplicate pairs and unknown subjects/cases. Every record must be A_PREPROCESSING_SEALED or explicitly UNAVAILABLE with retained reasons.
- Require exactly the frozen solver dictionary: maxiter2000, maxfun80000, maxls40, ftol1e-12, gtol1e-6. Do not accept a larger/different budget merely because its plan hash was frozen.
- Validate that each selected baseline candidate's configuration family matches its B0-B4 selection key, then reconstruct the five intended family/ridge/seed11/state identities from the complete sealed-case manifest. Preserve unavailable cases; do not invent a ridge for an unavailable baseline.
- Add synthetic missing/duplicate-record and changed-solver/selection-family denial regressions. These are ordinary contract-validator repairs, not scientific amendments.

The current exact seed/ridge/family/Final-subject mutation checks are useful but do not exercise the omissions or solver mutation above. Fixing these gaps does not permit any extra candidate, case, start or numerical rescue.

## Mandatory binding and entry-point check

`run` now requires hashes for the sensitivity plan, selection freeze, B candidate scores, sensitivity preparation, production gate and the specified numerical/sensitivity sources before opening case arrays or invoking a solver. The reviewer exercised the actual `run` entry point using an in-memory mocked gate with approval=true and an empty hash map: it correctly raised before optimizer execution, and the optimizer mock was never called. No real file payload or case array was supplied to this test.

The mandatory hash-set repair is therefore effective for that denial path. It does not cure the separate semantic plan-validation gap. The completed prospective plan, source/state identities and final gate must still be checked after preparation and selection exist; no actual plan or case result is certified here.

## Exact reviewed SHA256 identities

| Source | SHA256 |
|---|---|
| paper15_dev/sensitivities.py | 26923c185124cb51bcca941d965fc26bd02181a295eb21f4180fdd4ee1bf2101 |
| paper15_dev/sensitivity_fits.py | 8fd5cde7cc3e0c5064020a073c61458741e9de877181cbd730209eab078f7a2e |
| paper15_dev/test_sensitivities.py | dfe5fb758ff30ec5779a968f84b539765f83326e02985f328742aabb07ea9868 |
| paper15_dev/selection.py, only the relevant nuisance reference change reviewed here | f7b36f12875138dd395740a4ea1412d8bfb837ae9e67b94bc0f82b061421c7ad |

Other frozen case definitions, causal numerical equations and interpretation limits remain as inspected in review 1. This report does not certify the whole B/E selector or authorize E access. Preserve this report and obtain a fresh focused review after the plan-integrity repair.
