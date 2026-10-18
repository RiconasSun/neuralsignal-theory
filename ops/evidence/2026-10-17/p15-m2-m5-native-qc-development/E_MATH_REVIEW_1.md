# Independent Development E mathematical integration review 1

Mission: P15-M2-M5-NATIVE-QC-AND-DEVELOPMENT. Independent reviewer: `/root/gradient_review`. Date: 2026-10-17 America/Los_Angeles. Scope: new `evaluation_support.py`, `evaluation.py` and their synthetic tests against frozen M1 feature/model/control definitions. No whole-E admission or scientific-result certification is issued.

**P0=0; P1=1.** The numerical/causal mechanisms below are consistent, but the reference-family dispatch violates the registered per-bundle model limit. Preserve this report and repair before any actual E batch. No real A/B/E/Final neural cache, network or fit was accessed; only synthetic examples were executed. Only this report was written; frozen running core was not edited.

## P1 — reference bundles include an unregistered eighth family, B0

`FrozenPredictors` loads every selected family, including B0. `run_controls` calls `predictors.score(...,families=None)` for both original and reference arrays in N1/N2/N4. Consequently a complete real selection containing B0-B4,D,C,S evaluates eight selected families per reference bundle. Frozen M1 permits at most seven: B1-B4,D,C,S. B0 contributes to none of the registered reference contrasts.

The current test predictor contains only B1-B4,D,C,S, so the tests miss the actual B0-containing selection. An independent synthetic probe added the valid B0 configuration/initialized parameter vector to that same predictor and called the real `FrozenPredictors.score` with its default family dispatch. The output contained all eight families, confirming the code path without a real fit or E array.

Required repair: explicitly dispatch only the fixed seven reference families for N1/N2/N4 and only B1/B4 for N3. Preserve ordinary primary E B0 scoring/reporting. Add a regression with a B0-containing selected predictor proving no reference bundle evaluates or reports B0 and that the existing contrast slots remain intact. N3's smaller two-family calculation leaves aggregate slack, but does not waive the independent per-bundle seven-family constraint. No new random draw, model or scientific definition is needed.

## Mathematical mechanisms reviewed without another P0/P1

- Surrogate histories are recomputed from the supplied multivariate microbin sequence with the registered four causal windows, then transformed using the original frozen A history means/SD/active flags. Original task columns, target counts, unit order and comparison exposures remain unchanged. C states are recomputed from the surrogate stream with the same fixed DCT projection, finite lag weights and stored A micro/q scales; state activity does not get reselected on a surrogate.
- D's predictive mass uses the original current target counts; only its subsequent assimilation uses the surrogate counts. The current bin is scored before assimilation. Each fitted seed retains its own filter, and the three predictive joint masses are mixed by logmeanexp at each bin before score-bin summation. This is not coefficient averaging or whole-sequence ensemble weighting.
- N3 replaces design indices `24:38`, exactly nuisance columns24-37 after the intercept. It leaves neural history and C state untouched and applies the same wheel substitution to B1/B4. Its formal statistic is B4 LL/unit-bin; changes in B4-B1 are retained separately as descriptive wheel-gain results. Copied contrast-slot diagnostics are labeled as B4 wheel reliance and do not purport to be D/C wheel-null evidence.
- Sensitivity scoring uses its persisted A masks/scales, case-specific .1-second exposure/five score bins or .25-second neural warm-up as applicable, correct rich41 nuisance count, and unchanged behavioral reference. Only B0-B4 are scored for sensitivities. Main/control denominators are actual nominal scored unit-bins; comparisons require equal denominators. No rate-normalization reinterpretation is introduced across sensitivity bin widths.
- Reference seeds remain suite/subject/E/replicate-specific; 999 replicates per suite are constructed with the same mapping shared across available contrasts. Metadata-defined coverage is fixed before neural E scoring. N2/N3 singleton exclusions and N4 complete-block exposures match original/reference comparisons. The summary uses equal-mouse means, `(1+count(reference>=observed))/1000`, fixed Holm4 slots and p=1 for unavailable panels; no exact mechanistic-null claim is made.
- `require_stage('E')` already checks all E-gate hash values as well as frozen A attempts/B winners. Therefore the absence of a second hash loop inside `verify_E_gate` was not incorrectly treated as an independent mathematical defect. Full source/access/one-batch safety remains a separate review, not an approval inferred from these mathematical checks.

## Independently executed synthetic evidence

All **ten existing evaluation tests PASS** with the bundled runtime, single BLAS/OMP threads and ResourceWarning as error. These cover surrogate history/C transformations, wheel-only coordinates, pre-bin ensemble arithmetic, D causal assimilation, strict-past wheel threshold inputs, denominators/unavailable slots, reference pseudocount/Holm4 and source/access denials. Their omission of B0 is the coverage gap underlying the P1 above.

A separate mocked N3 assembly probe ran the actual 999-iteration dispatch/summary construction with a synthetic predictor and deterministic mocked donor mapping, without production likelihood calls or real data. It verified 999 distinct recorded seeds, one original plus999 reference predictor calls, no D/C evaluation, B4-LL formal value2 versus descriptive B4-B1 gain1, and preservation of all six labeled contrast slots. This is a scheduling/statistic-assembly check, explicitly **not** a certificate of 999 actual surrogate likelihood evaluations or real control coverage.

The additional B0 probe used the actual synthetic production predictor and observed eight families under default dispatch, as described above. No optimizer was invoked.

## Scope and reporting limits

This report is about mathematical integration, not complete E approval. The independently identified source/access issues, real frozen selection, sensitivity completion, exact gate/record identities, one-shot claim and final claim audit remain separate mandatory gates. Current `A_matching_diagnostics` are marginal A mean/SD descriptors; they must not be called proof of pairwise donor balance or validated exchangeability. Registered donor-match/imbalance limitations still need honest final reporting. No unavailable control/sensitivity can be labeled passed, and Development E remains exploratory rather than independent-animal confirmation.

## Exact reviewed SHA256 identities

| Source | SHA256 |
|---|---|
| paper15_dev/evaluation_support.py | 01fe5bf8fb3000f4d53cf8b133de23ea6d2f26c2a82b00a07d93e500fd9062a8 |
| paper15_dev/evaluation.py | 6d9827ab9b55963f76e77ef51b2dfc3b0ae18198cd9bfc7cb42efe95850379ba |
| paper15_dev/test_evaluation.py | 38f198fba2e623154bab437dda06d478a7384c209b27f85550141cb1ca50944b |
| paper15_dev/controls.py | 093bc970d429575b66e9032006060198377633212312e817bcbd2a278a431a35 |
| paper15_dev/features.py | 30d17b3a902429537e8b83fc9ac5a483933bdb8080ff890c5f43c6fc5f4dd3fd |
| paper15_dev/models.py | e13d12d3986b42ba1691075804df7b2ec6a033dcfe20fac36e5b6ed8e359ba90 |
| paper15_dev/statistics.py | a62ba9119624b293ff0ffcc8a6679120b3956dc10e63a47bf66d9d29c1c54382 |

Relevant repairs require fresh affected checks and a new review. Preserve this unsuccessful review; do not edit it into a post-repair approval.
