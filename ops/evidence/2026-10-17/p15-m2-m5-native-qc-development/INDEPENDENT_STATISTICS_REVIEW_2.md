# Independent internal statistics review 2

Mission: P15-M2-M5-NATIVE-QC-AND-DEVELOPMENT. Review date: 2026-10-18 UTC.

Decision: **ACCEPTED_DEVELOPMENT_STATISTICS_COMPONENT_ONLY**. Open P0: 0. Open P1: 0. R1's cohort-integrity finding is resolved before real E analysis. R1 remains preserved with SHA256 `999b2545dd5229dd8786d5b428ef91d2273d86df09c05ec4ace21fc8a1760420`.

`analyze` now requires an explicit nonempty expected-subject list, uniqueness in both expected and input identities, and exact identity-set agreement. Missing B1/B4 primary input is rejected. Available scores must have positive unit-bin denominators and finite LL; paired denominators must agree. A secondary comparison missing any fixed-cohort model is retained as UNAVAILABLE_FIXED_COHORT with p=1 and explicit missing identities, rather than silently recomputed on fewer mice. Its original Holm5 slot remains intact. The unchanged primary cohort is retained.

Fresh independent execution: all **7 test_statistics tests PASS** with ResourceWarning as error, including all five original numerical/statistical tests plus duplicate/incomplete-cohort and secondary-slot regressions. Independently repeated four additional violation cases: an extra duplicate input mouse, a missing primary model, an unexpected mouse replacing an expected mouse, and duplicated expected identities. All were rejected. Independently removed D for one of eight synthetic mice: the primary remained n=8, D-B4 remained unavailable with raw and Holm p=1 and the exact missing subject, and all five correction slots remained present. No real effects or scores were used.

The source-reviewed exhaustive sign test directions, frozen equality handling, equal-mouse LL/Q arithmetic, 10,000 whole-mouse PCG64 bootstrap/linear intervals, separate lab-block diagnostic, LOMO/LOLO summaries and conditional sign-symmetry/lab-dependence caveats are otherwise unchanged. Exploratory=true, heldout_animal_confirmation=false and validated=false remain enforced for computed Development comparisons. This does not establish independence, symmetry, power, equivalence or biological absence from any future p-value.

Exact reviewed SHA256 identities:

| File | SHA256 |
|---|---|
| paper15_dev/statistics.py | a62ba9119624b293ff0ffcc8a6679120b3956dc10e63a47bf66d9d29c1c54382 |
| paper15_dev/test_statistics.py | 7769f96b39c1a6fdff0861e17bdcbb06f810a3e2020f6b4fcdd124345e9480b5 |

The future pre-E worker must supply expected_subjects from the already frozen admitted/B-selection identities, not from successful E results or a post-score subset. It must verify registered common masks/nominal integer denominators, frozen model-family availability and the same ordered mouse-index stream across complete contrasts. These are integration prerequisites, not certified by calling this pure helper on synthetic inputs. Complete pre-E review, gate freezing and source/role/failure controls remain pending before any real E batch.

No real effects, neural arrays/cache, B/E or Final observations, network/source request, real fitting or scientific suite was accessed or executed by this reviewer. Only this new review artifact was added. No Final assessment or confirmatory claim is approved.
