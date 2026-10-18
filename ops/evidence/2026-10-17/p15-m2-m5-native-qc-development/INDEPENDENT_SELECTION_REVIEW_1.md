# Independent internal pre-B selection review 1

Mission: P15-M2-M5-NATIVE-QC-AND-DEVELOPMENT. Base: `30cb925f505d63ae52bb1461d9ab153a52f1888e`. Review date: 2026-10-18 UTC.

Decision: **REPAIR_REQUIRED_IN_SELECTION_ACCESS_COMPONENT**. Open P0: 0. Open P1: 1. This unsuccessful review remains preserved. No real B/E neural data, neural cache, source/network request, score or model fit was accessed or computed by this reviewer. Only this new review artifact was written. Review of these new files does not certify, alter or invalidate unchanged A production mathematics or already running registered A fits.

## P1-01: E release does not require or bind a frozen B selection

`selection.require_stage('E')` verifies completed attempt-marker sets and then checks only an E approval Boolean and whichever entries happen to be supplied in that gate's `hashes` dictionary. It does not require SELECTION_FREEZE.json to exist, nor require that the E gate bind its exact hash. An empty dictionary passes vacuously.

I independently reproduced this with isolated synthetic files: complete synthetic baseline/dynamic attempt markers, approved_for_one_frozen_E_batch=true and hashes={} allow `require_stage('E')` to return successfully while SELECTION_FREEZE.json does not exist. No actual extraction was called. The owner's M5 and frozen M1 require global B winners to be frozen before E access/reporting. A self-declared E flag cannot substitute for this scientific prerequisite.

Minimal repair: require a valid completed B selection freeze and enforce a mandatory E-gate binding to its exact hash, with its candidate-results/winner identities and other required frozen dependencies verified before neural I/O. Missing/empty or stale bindings must fail closed. Keep the distinct E gate and registered one-batch scope; no cryptographic entitlement system or scientific-policy change is requested.

Required synthetic regressions: approved E flag with no selection freeze; empty required bindings; altered selection/candidate result; and a valid bound synthetic freeze. The denied cases must perform zero neural I/O. The current test only checks missing/false E gate, so its success does not cover the demonstrated missing-freeze case.

## Reviewed B selection behavior

- The fixed 61 configurations form exactly 37 candidates. Every D/S candidate contains seeds11/23/37; B/C remain their registered single starts. `select` requires every candidate's starts to be NUMERICAL_PASS on every fixed admitted mouse before it can be available, rather than averaging only successful mice.
- The stage check requires exact complete baseline/dynamic attempt-key sets and counts, each sealed attempt hash, and the required baseline numerical marker before B extraction. The B path does not confer implicit E permission. Subject and source allocation checks deny Final/nonadmitted subjects before neural loading.
- Role extraction verifies existing source-object hashes, uses the trusted Development chunk projector for the requested role, and obtains only that role's target/history/nuisance arrays. It uses A-selected units and A scalers; C q scaling/activity is retained from A. There is no fitting or scaling-estimation operation in the B selector.
- `score_group` computes a uniform mixture of the seeds' joint pre-bin masses with logsumexp-minus-log(seed count), then sums only scored bins. It does not average coefficients or log-likelihoods across seeds. The nominal curated-release unit-bin denominator is taken from the scored target shape.
- Candidate scores use an arithmetic mean of mouse LL/Q, preserving equal-mouse aggregation. The fixed 1e-6 tie band is resolved by fewer nominal parameters, stronger ridge, smaller K/r, smaller tau and lexical candidate ID. Nominal counts retain constant-feature capacity, and each baseline selects independently. S selection is restricted to K_S=selected_K_D+1 while other attempted S candidates remain reported.
- The B winner freeze records all global selected identities, candidate-score hash and source-code identities before E. No individualized mouse winner, A+B refit or E-driven tuning is implemented by this selection function.

These observations are source review, not actual B score or selection-result verification. Before execution the final accepted selection/access candidate and required inputs must be frozen as part of the prospective selection handoff; the future actual 610-fit completion and valid numerical receipts remain prerequisites.

## Fresh independent verification

Executed `paper15_dev/work/runtime/Scripts/python.exe -W error::ResourceWarning -m unittest paper15_dev.test_selection -v`: **9 tests PASS**, exit0. Those tests cover candidate grouping, seed membership, fixed tie rules, unavailable candidates, nominal capacity, Final/role denial, missing/false E flag and an empty-attempt marker. Additionally executed the isolated positive-empty-E-gate reproduction described above: it incorrectly admitted E without any B selection freeze. No real fit or scoring was run.

Exact reviewed SHA256 identities:

| File | SHA256 |
|---|---|
| paper15_dev/selection.py | d6dff607cccf12bb179f642e8afe6923e42770005be01661697180f0d03f1e6d |
| paper15_dev/test_selection.py | 987ac222524820b034dc26577ce474d2bbdb9dfa38d8446ad7603f16603616bc |

Do not use this report to claim completed B selection, E-release approval, M5 completion, Final readiness or scientific validation. Repair and independently review the new access component before its production use; the historical unsuccessful r1 must not be overwritten.
