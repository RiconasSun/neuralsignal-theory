# Independent internal pre-B selection review 2

Mission: P15-M2-M5-NATIVE-QC-AND-DEVELOPMENT. Base: `30cb925f505d63ae52bb1461d9ab153a52f1888e`. Review date: 2026-10-18 UTC.

Decision: **ACCEPTED_SELECTION_COMPONENT_SUBJECT_TO_ACTUAL_ATTEMPT_COMPLETION_GATE**. Open P0: 0. Open P1: 0. The r1 E-prerequisite finding is resolved before any B/E access. R1 remains preserved. This is component acceptance, not evidence that all 610 A attempts have completed, actual B selection has run, or E has been released.

## R1 P1 closure

`require_stage('E')` now requires SELECTION_FREEZE.json, exact registered subjects, nonempty B1/B4 winners, the exact candidate-results hash, and available selected IDs with the proper family. Its separate E gate must contain mandatory hashes for the selection freeze, candidate results, models, features, training and selection sources; every binding is checked. The earlier approved-flag/empty-hash escape is closed. Missing or altered B winners cannot be replaced by E-gate self-declaration.

No A production source was changed by this selector repair. Existing A fits and their numerical evidence are not certified or invalidated by reviewing these new component files.

## Fresh independent verification

- Executed `paper15_dev/work/runtime/Scripts/python.exe -W error::ResourceWarning -m unittest paper15_dev.test_selection -v`: **9 tests PASS**, exit0. The expanded functional test retains complete synthetic 61-attempt ledgers and B admission, then exercises absent selection, false E approval, empty mandatory bindings, exact-bound acceptance and altered-selection rejection. Other original grouping/tie/availability/Final/role tests remain.
- Independently altered the candidate-results file and a bound production source in isolated synthetic fixtures, then called the actual `extract_role('dev','E')` entry. Both were rejected before any numpy neural-array load; the substituted load counter stayed zero. These fixtures did not inspect or modify real attempt journals, B/E observations or scientific outputs.
- Independently tested `score_group` using three artificial seed pre-bin mass arrays. Its result equals `20*log((exp(-1)+exp(-2)+exp(-3))/3)` for the scored bins, differs from averaging seed log-likelihoods, excludes warm bins, and uses the expected 160 nominal scored unit-bins for two ten-bin/eight-unit epochs. No actual model or neural observation was scored.
- Re-read the repaired prerequisite logic and unchanged global candidate selection, fixed tie rules and S capacity pairing. No remaining actionable P0/P1 was found in this component. Actual fit/numerical completion remains a future gate, not a test fixture substituted for real evidence.

## Exact reviewed SHA256

| File | SHA256 |
|---|---|
| paper15_dev/selection.py | 0b374c08ae3e187e73c2316b7ab5722da276aa13f2fda51eeff5f1ea63268fd3 |
| paper15_dev/test_selection.py | 278fec67b8d055ea71b40d615dfbb6839c354397e4e3fab299dd720ed20ee9ab |

The registered 37 candidate groups still require all required starts on all admitted mice. Once actual baseline and dynamic completion receipts seal all 610 registered A attempts and satisfy the required primary baseline gate, freeze this exact accepted selection/access candidate and its inputs before the authorized B-only selection. Unavailable secondary candidates remain unavailable globally; no easier-mouse averaging, E tuning, additional start or model substitution is approved.

The E gate repair establishes a prerequisite check only. No actual E approval is issued here: the complete frozen E analysis/control/sensitivity implementation and one-batch evidence still require their separately planned pre-E review. This review does not cover newly added controls.py/test_controls.py or imply control-suite acceptance. Final neural access remains forbidden.

No real B/E neural data, full neural cache, Final data, network/source request, real fit or real predictive score was accessed or computed by this reviewer. Only this new review artifact was written.
