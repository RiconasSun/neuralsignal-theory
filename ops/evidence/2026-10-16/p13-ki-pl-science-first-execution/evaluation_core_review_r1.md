# Independent pure evaluation-core review r1

Mission: `P13-KI-PL-SCIENCE-FIRST-EXECUTION`.
Reviewed UTC: 2026-10-16T16:11:32Z.
Reviewer: separate local reviewer agent; internal scientific/evidence/code review, not external peer review.
Decision: **REQUEST_CHANGES — PURE STATISTICS CORE**.
Open P0: **0**. Open P1: **1**.
The prediction operators have no identified P0/P1 at the reviewed pure-array scope. The combined core is not accepted until the exact-tail defect below is repaired. **No real E/D release, final claim or scientific PASS is granted.**

## Candidate and synthetic-only evidence

Reviewed `paper13_ki_execution1/EVALUATION_CORE_FREEZE.json`, SHA256 `c6b1b0be5a3b930aef0fd5ee26eee6011c99144ec0cd286d0385464e9c4b7926`, with **973** hashes. All current hashes independently match. All 966 entries from the previously reviewed M4 freeze are unchanged in this expanded manifest. No partial real M4 output was opened or scored.

Read `animal_stats.py`, `predictive.py`, both test modules and prospective statistics/prediction registrations against the activated protocol's six contrasts, sign-null/CI/multiplicity conditions, unit-mask and history-control definitions. Executed `python -B -m unittest paper13_ki_execution1.test_animal_stats paper13_ki_execution1.test_predictive -v`: fresh exit **0**, **13 focused synthetic tests PASS**. Separate independent exact-rational/integer synthetic sign-enumeration checks exposed a defect not covered by these tests.

No raw source, network, real model fit, real E/final-D values or new E/D output was accessed. No actual partial family model was used on B. Only this new review file is written by the reviewer; no package/test/protocol source is changed. The review is of pure mathematics/operators, not an approval to execute scientific evaluation.

## P1 — Floating summation drops exact sign-flip tail ties and can change Holm acceptance

Evidence: `paper13_ki_execution1/animal_stats.py:17-22`, specifically floating `abs(mean(signs*v)) >= abs(mean(v))`; the exact-inclusive-tail contract in the activated protocol and `STATISTICS_IMPLEMENTATION_REGISTRATION.md`.

The implementation enumerates all assignments but sums each in ordinary binary64 arithmetic before the inclusive comparison. Mathematically equal absolute sums can round differently across sign assignments, so an exact tail tie can be counted as strictly smaller. The constant-positive/all-zero tests do not expose cancellation/order-sensitive ties.

Independent oracle: convert each supplied finite binary64 effect with `as_integer_ratio()`, scale to the common power-of-two denominator, and enumerate all signed integer sums against the exact observed absolute integer sum. This tests the exact represented input values, not a decimal-rounding convention or an arbitrary tolerance.

Two synthetic counterexamples:

| Eight supplied effects | Exact inclusive exceedances | Implemented exceedances | Exact p | Implemented p |
|---|---:|---:|---:|---:|
| [.1,.2,.3,−.1,−.2,−.3,.1,.2] | 170 | 168 | .6640625 | .65625 |
| [.04,.1,−.01,.1,.04,.01,.05,.03] | 6 | 4 | .0234375 | .015625 |

For the second vector, if it is the smallest p in its three-test family, the first-rank Holm value changes from **.0703125** to **.046875**. Thus the bug can turn a non-passing registered statistical gate into a passing one. It is not merely cosmetic last-digit output, and Holm cannot correct omitted sign assignments.

Required repair: implement a deterministic inclusive-tail comparison that faithfully preserves mathematical ties of the supplied finite effects—for example common-denominator integer sums—and verify against a genuinely independent Fraction/integer oracle. Do not choose an outcome-dependent epsilon, round effects to favorable decimals or change alpha/multiplicity/sign-null assumptions. Add both counterexamples, cancellation/duplicate/zero/permutation cases and the Holm-boundary consequence as synthetic regressions. Preserve this failed candidate/review, re-freeze and obtain independent pure-core re-review before E/final statistics use. This is an ordinary pre-outcome coding correction, not an amendment to scientific acceptance criteria.

## Other statistics reviewed

Contrast order and paired mouse identity requirements match the frozen three primaries plus three guards. Holm adjustment is correctly monotone and applied separately to the two registered families. The 10,000 bootstrap draws use seed130041, shared whole-mouse indices across all six columns and the fixed linear percentile convention. Equal-mouse means, direction counts with zero effects retained, >=75% requirements and LOMO components are explicit. Sign symmetry/sampling limitations are disclosed; statistical component flags are not classified as final scientific claims. No additional P0/P1 was found in those portions, subject to correcting the sign p-values.

## Pure prediction/operator assessment

The seven prediction tests pass and code inspection supports the registered operators:

- Full-eight-unit baseline, joint HMM and continuous scores match the frozen models with the same five-bin warm-up and actual unit-bin denominator. Static mixtures are joint distributions, not products of per-unit mixture scores.
- Reduced-unit baselines first standardize original source features, set omitted neural-source contributions to zero, retain intercept/nuisance inputs and target rows, and recompute the same restricted B4 offset for D/C/S. Omitting raw counts before standardization is correctly distinguished and tested as a different operation.
- HMM emissions and filtering use retained units only. The continuous driver masks standardized coordinates before the original Q, without renormalization, retains original hidden-state scales/readout rows and never fits evaluation moments. Finite omitted-unit canaries and zero-SD handling are covered.
- Donor-history evaluation scores original current outcomes before the donor filtering update. Donor neural histories drive the designated baselines/continuous state while original external nuisance remains. Independent small-path enumeration reproduces the donor HMM score, and future donor changes do not alter earlier/current scores. These are component operators; future control assembly must still enforce donor/partition/exchangeability policies.
- A 29-bin shifted input correctly leaves 24 scored bins, with denominator based on retained units/bins. Bundle state is not mutated. No fitter, source loader or final-claim classifier exists in these helpers.

No further predictive-operator P0/P1 was identified for the frozen pure-array scope. This does not approve an E/D runner, final release, null-generation implementation, sample/censor selection or claim classification, which remain separate future reviewed gates.

## Continuing boundaries

The identified defect is confined to the new statistics module and is not used by the unchanged, previously accepted M4 A-fit/global-B-selection path. This review neither inspects nor invalidates that ongoing path based on unseen real results. All 540 required numerical fits must still pass before any dynamic B scoring; no partial-fit evaluation or model pruning is authorized.

Keep E/final-D scientific evaluation unreleased. Repair and independently re-review the pure statistics core synthetically, preserve all earlier hashes/failures and retain the original numerical/inferential/scientific gates. Neither passing synthetic tests nor this operator review establishes a model advantage, conditional-null validity, final inference, manuscript completion or full mission PASS. Actual later Git receipts remain separate and are not prospectively certified.
