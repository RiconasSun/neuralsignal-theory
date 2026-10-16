# Independent pure evaluation-core review r2

Mission: `P13-KI-PL-SCIENCE-FIRST-EXECUTION`.
Reviewed UTC: 2026-10-16T16:14:43Z.
Reviewer: separate local reviewer agent; independent internal scientific/evidence/code review, not external peer review.
Decision: **ACCEPTED — PURE EVALUATION CORE ENGINEERING ONLY**.
Open P0: **0**. Open P1: **0**.

The previously identified exact-tail P1 is resolved. This acceptance covers the frozen pure-array statistics and prediction operators. It does **not** authorize E/final-D source access, outcome export, real model scoring, null/control assembly, final claim classification or scientific/mission PASS.

## Candidate identity and preservation

Independently verified SHA256 `35799f508f31e3eec819c0f248205af9037594ecf0a35dbd779e041be30c49eb` for `paper13_ki_execution1/EVALUATION_CORE_FREEZE_r2.json` and all **976** listed current file hashes. Read the prospective `EXACT_SIGN_TAIL_REPAIR_REGISTRATION_r2.md`, registered at 2026-10-16T16:13:12.208420+00:00. It records an exact-inclusive-tail coding correction before E/D outcomes, without changing alpha, multiplicity, the conditional fair-sign null, bootstrap convention or scientific acceptance criteria.

The failed r1 review remains retained. Opened `evaluation_core_r1_code_package.zip` and verified its original four source/test files against the preserved original 973-entry freeze. Its five members are the original freeze, `animal_stats.py`, `test_animal_stats.py`, `predictive.py` and `test_predictive.py`. Current prediction implementation and prediction tests are byte-identical to those archived reviewed files. No earlier failure was overwritten or relabeled as a pass.

## Exact-tail repair assessment

Reviewed `paper13_ki_execution1/animal_stats.py:20` onward. Each supplied finite binary64 effect is converted with `as_integer_ratio()`. Because all resulting denominators are powers of two, scaling to their maximum yields exact integers. Arbitrary-precision integer signed sums are compared inclusively against the exact observed absolute sum. The common sample-size divisor cancels. Consequently assignment order and floating cancellation cannot discard mathematically equal tail ties of the represented inputs. No epsilon or decimal rounding has been introduced. The floating `observed_abs_mean` field is display information and is not used for tail membership.

Both prior counterexamples now match the exact oracle:

| Eight supplied effects | Inclusive exceedances / assignments | Exact p |
|---|---:|---:|
| [.1,.2,.3,-.1,-.2,-.3,.1,.2] | 170 / 256 | .6640625 |
| [.04,.1,-.01,.1,.04,.01,.05,.03] | 6 / 256 | .0234375 |

For the second example, first-rank Holm adjustment in a three-test family is **.0703125**, correctly above .05. The old erroneous .046875 result is not retained. Tests cover this acceptance consequence, exact cancellation, duplicates, zeros, extreme finite scales and permutations.

Independent synthetic oracle: a separate `python -B -c` script used `fractions.Fraction.from_float` and enumerated every sign assignment with exact rational addition/comparison, without calling the implementation's integer-scaling helper. Five explicit cancellation/extreme-scale/zero vectors plus 20 deterministic vectors for each of n=8,9,10 (Python `random.Random(130076)`, values drawn from [.001,-.001,.01,-.01,.02,-.02,0.,.2]) gave **65/65** matching exact exceedance counts and p-values. Reversal and cyclic permutation of each vector gave **130/130** invariant results. This independently checks the new algorithm rather than mirroring its integer representation.

The correction preserves separate Holm3 primary/guard families, six paired mouse contrasts, zero-effect inclusion, whole-mouse joint bootstrap indices, 10,000 draws/seed130041/linear quantiles, >=75% direction and LOMO components. Conditional fair-sign/sign-symmetry assumptions remain necessary; arbitrary mean zero is not presented as sufficient. Statistical component flags still explicitly withhold final scientific classification pending all applicable gates. No further P0/P1 was identified in these portions.

## Fresh synthetic verification and unchanged operator scope

Ran `python -B -m unittest paper13_ki_execution1.test_animal_stats paper13_ki_execution1.test_predictive -v`: fresh exit **0**, **15 focused synthetic tests PASS** (eight statistics, seven prediction). The parent-saved `evaluation_core_reproduction_r2.txt` also records 15 passing focused tests. This review does not claim that the entire earlier scientific execution suite was rerun.

The unchanged prediction operators retain the r1 assessment: full-eight parity; shared restricted B4 offset; zeroing omitted standardized source contributions before target restriction; retained-unit HMM filtering; original Q without renormalization and frozen hidden/count scales; original outcomes scored before donor-filter update; causal donor-history behavior; correct retained unit/bin denominator including the 29-bin/24-scored-bin case; zero-SD handling and input-state preservation. Independent donor path enumeration, omitted-source canaries and parity tests continue to pass. No fitter, source loader or final-claim classifier is included in these helpers. Future control assembly must independently implement the registered donor, partition, censoring and exchangeability policies.

## Boundaries and next gate

No network, raw neural source, real model fit, real E/final-D value or new E/D output was accessed. No actual completed/partial M4 model was opened or scored during this review. Reported actual M4 completion and configuration selection are outside this pure-core acceptance and are not independently certified here. Source/protocol/test files were not changed by the reviewer; only this new review file is written.

The pure-core engineering repair is accepted with **0 open P0/P1**. Keep E/final-D scientific execution unreleased until the separate full stage review binds its actual source/export authority, selected model/state identities, all required numerical denominators, control assembly and prospective outcome policy. Passing this pure core establishes neither model superiority nor null validity, scientific eligibility, final inference, manuscript completion or full mission PASS. Later Git archive/push/readback/clean receipts remain separate and are not prospectively certified.
