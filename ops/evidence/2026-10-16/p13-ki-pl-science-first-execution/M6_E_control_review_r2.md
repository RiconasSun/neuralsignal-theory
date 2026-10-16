# Independent amended M6 E-control review r2

Mission: `P13-KI-PL-SCIENCE-FIRST-EXECUTION`.
Reviewed UTC: 2026-10-16T16:44:42Z, with subsequent synthetic oracle/boundary checks in this same review.
Reviewer: separate local reviewer agent; independent internal scientific/evidence/code review, not external peer review.
Decision: **ACCEPTED_FOR_E_CONTROLS_ONLY**.
Open P0: **0**. Open P1: **0** for this frozen stage.

The r1 summary P1 is resolved before any actual control run. Acceptance covers the frozen E-only four-suite/999-replicate execution and descriptive summary. It does **not** approve final C fitting, D outcome release/evaluation, the complete sensitivity/final path or any scientific/full mission PASS. The affected broad confirmatory verdicts remain permanently INCONCLUSIVE under the owner amendment. No approval file is created by this reviewer.

## Candidate, preservation and fresh reproduction

Verified `paper13_ki_execution1/M6_E_IMPLEMENTATION_FREEZE_r2.json` SHA256 **c55f5dc3f04371bf367af6910c7d0a671f72048a5b5817434b9ad1bb48478e91** and all **2,316** listed current hashes. Read prospective `M6_EXACT_REFERENCE_REPAIR_REGISTRATION_r2.md`, dated 2026-10-16T16:42:11.953500+00:00, before actual controls/C fitting/D outcomes. It registers only the demonstrated decision-arithmetic correction, without changing models, transformations, seeds, 999/plus-one/Holm2, alpha, nominal percentile level or owner restrictions.

Independently verified failed-candidate archive `M6_E_r1_failed_code_package.zip` SHA256 **1fff0993fc541e49125f641a7fef196266ed411450ebac635ed2e80763dc7750**. Its exact four members are original `control_core.py`, original `test_control_core.py`, original M6 E freeze and the failed r1 review. Compared the r1 manifest to current files: only those two core/test files differ among its listed artifacts, and their archived bytes match their original hashes exactly. The E controls runner itself is unchanged. Earlier failures and reviews remain retained and are not relabeled as passing.

Fresh `& .\paper13_ki_execution1\reproduce_M6_E_r2.ps1` returned exit **0**, **120 tests PASS**. It verifies **2,316 current +85 original** hashes, six historical source/test checks using exact archived bytes, 39 original saved states, 390 baseline +540 family saved fits and ten frozen E model/state inputs. It explicitly does not execute old failed source, substitute old code into the current run, or waive a historical hash mismatch. Older reproduction scripts remain historical and retain their original assertions. The five synthetic final-C worker tests included in this run do not constitute review or execution permission for that separate stage.

## Exact tail and linear percentile repair

`control_core.exact_total` interprets the already defined per-mouse binary64 score differences as exact dyadic values and sums their integer numerators on a common power-of-two denominator. Observed and surrogate totals therefore share the same mathematical interpretation. The common number of contributing mice cancels for comparison. Conditional inclusive counts now compare exact totals; converting a displayed mean to float cannot decide tail membership.

`linear_q95` sorts exact surrogate totals and uses rank **(999-1)*95/100 =948+1/10**, so the exact nominal linear interpolant is **9/10 of order statistic948 +1/10 of order statistic949**, with zero-based indices. The common mouse denominator again cancels. The strict stress guard compares the exact observed total to this exact interpolant; equality is correctly not greater. This computes the original nominal 95th linear percentile without an order-dependent floating reduction or binary floating-rank artifact. It adds neither a tolerance nor a selected decimal rounding convention. Display means/quantiles are converted afterward; remaining floating display averages do not control guard decisions.

The original nonpositive-score/permuted-multiset counterexample now has **999 inclusive exceedances**, conditional p=**1**, Holm2=**1**, and **False** for both temporal/history strict-above flags, for both D and C. Its necessary numerical reference component no longer falsely passes. The original r1 evidence remains immutable.

Independent `python -B -` Fraction oracle probes, separate from the implementation's integer-scaling helper, checked:

- Complete synthetic summaries with **n=8,9,10**, independently forming all six per-mouse effects from the supplied scores and using `Fraction.from_float` addition. All **six conditional tail counts/p-values**, **54 stress quantiles** and their relevant strict guard decisions match. All **71,928 returned replicate/contrast display means** match exact-total/n conversion.
- **60** additional cancellation/zero/extreme-scale vectors and their reversals against direct Fraction summation. No order-dependent total was found.
- Generic exact linear percentile calculations at lengths **1,2,3,9,20,999**, independently using rank19*(n-1)/20 and rational interpolation; all match.
- A 999-ramp exact interpolation tie and one-ULP-lower/higher observed score cases. The exact nominal rank is948+1/10. Strict reference flags are respectively **False, False, True**; the inclusive count is50 and p=.051 for all three, matching the independent oracle. The tie is not pushed to either side by display rounding.

The newly added regression tests also cover the original D/C counterexample, interpolation tie/neighbors and 30 deterministic cancellation/permutation vectors. No additional P0/P1 was identified in the repaired arithmetic.

## Retained E-only runner assessment

The unchanged runner retains the reviewed approval-before-input, M5 completion, development-only frozen-model/E-state identity checks and exact original ten sorted mice. It has no neural source loader or parameter fitter. Original E counts/scalers/coefficients, B* identity and D/C/S selections remain frozen. No E QC, selection, scaling, refit, final-role input or new model candidate is introduced.

The r1-reviewed transformation definitions remain unchanged: independent six-stratum temporal permutations; different-epoch donor histories within original partition/order quartile, original outcomes scored before donor filtering; whole-eleven-column nuisance trajectory permutation; full sequential frozen B* conditional generation including warm-up, without clipping or retry. The independent all-five-baseline sequential-generator and 39,960-position synthetic RNG-scheduling probes documented in r1 remain applicable to these byte-identical portions, and current corresponding regressions pass. No actual control study was rerun by the reviewer.

Four suites retain exactly **999x10x9** scores, all six effects and equal-mouse distributions. Execution remains suite -> replicate -> sorted mouse with one frozen stream per suite. Exclusive journal/array creation, flushed completed cells, durable progress/error events and refusal of failed/interrupted repeat preserve the original attempt rather than substituting a new random draw. Existing injected-failure and approval/role/input tests pass. The new arithmetic changes only summary decisions after these same fixed transformations.

## Owner authority and continuing limits

The exact direct owner B reply and recorded pre-D stopping-rule/baseline amendments remain hash-bound and unchanged. They resolve the earlier purpose ambiguity prospectively: preserve **6/9<8** and all three affected broad primary INCONCLUSIVE verdicts permanently, while permitting unchanged descriptive final execution only after all other required gates. This E-controls acceptance does not itself satisfy those later gates. Other substantive source/implementation/numerical failures still stop; no optimizer rescue, threshold/mask change, new candidate, result-driven repair or repeated D assessment is authorized.

The parent may bind this actual review to E-controls-only approval and execute the frozen stage. Preserve every failed/negative/mixed reference and report assumption-dependent stress/plugin-null limitations. Numerical guard components cannot rescue the owner-locked claim verdicts or establish biological exchangeability/causality. Final C calibration, complete sensitivity integration and final D require their separately frozen and independently reviewed path.

No network/raw source/new model fit/actual E control replicate/final C or D outcome access was performed by this review. Only this new review file is written, apart from ignored synthetic artifacts generated by tests. No external peer review, full mission/scientific PASS, current clean tree or prospective Git closure is certified.
