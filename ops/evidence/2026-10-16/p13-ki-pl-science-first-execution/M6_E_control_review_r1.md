# Independent amended M6 E-control review r1

Mission: `P13-KI-PL-SCIENCE-FIRST-EXECUTION`.
Reviewed UTC: 2026-10-16T16:39:54Z, with subsequent independent synthetic probes in this same review.
Reviewer: separate local reviewer agent; independent internal scientific/evidence/code review, not external peer review.
Decision: **REQUEST_CHANGES — E CONTROL SUMMARY**.
Open P0: **0**. Open P1: **1**, a numerical summary defect below.
**No real E-control execution or final C/D release is accepted by this review.** The prior human-purpose ambiguity is resolved by the actual owner amendment; the new blocker is an ordinary demonstrated pre-outcome coding defect, not a request for additional owner permission.

## Frozen identity, owner amendment and tests

Verified `paper13_ki_execution1/M6_E_IMPLEMENTATION_FREEZE.json` SHA256 **17ca09c21bbe3f2f994bf5ca15b9ed2324bee54a25907d711633ebba66a090f5** and all **2,301** listed hashes. Read the exact owner reply, source-bound pre-D amendment, baseline amendment r3, original protocol control definitions and both prospective implementation/execution registrations. Owner reply SHA256 is **da5e3bb5e9ab65f2f8d4234b265a6691eb9f42abe14d89c490fa8652b56783b2** and matches its recorded evidence binding.

The amendment faithfully records the direct owner's **B** choice: a pre-D, coverage-informed stopping-rule exception only. Six versus eight recent-event coverage remains failed, with all three associated broad confirmatory primary verdicts permanently INCONCLUSIVE; later p-values, guards or controls cannot rescue them. Models, animals/partitions, QC, masks, tests, numerical standards and sensitivity coverage remain unchanged. All other required gates retain STOP, final C/D needs separate reviewed implementation, D is once-only/descriptive, and valid completion still requires all results/limits/paper/PDFs. No original failed gate or prior review is retroactively altered. This resolves the previously identified purpose question without granting final-path approval here.

Fresh `& .\paper13_ki_execution1\reproduce_M6_E.ps1` returned exit **0**: **108 prior + 4 runner = 112 synthetic tests PASS**, frozen/current/original hashes and saved M1-M5 evidence reproduced, **zero real control replicates/new fits/final-D values**. These tests do not cover the cancellation-dependent summary case found independently below. At independent inspection, neither `M6_E_APPROVAL.json` nor a real `results/M6_E_CONTROLS_GATE.json` exists. No real control outcome was used to discover or diagnose this defect.

## P1 — Floating equal-mouse reductions lose exact surrogate ties and can fabricate both necessary guard components

Evidence: `paper13_ki_execution1/control_core.py:72` and `:77` compute observed and replicate means in floating arithmetic; `:79` counts inclusive conditional tails from those rounded reductions; `:82` and `:88` use similarly rounded means for linear stress percentiles and strict observed-above-reference comparisons.

The per-mouse effects can be the **same exact multiset of supplied binary64 values**, with exactly equal rational sums, while their row ordering produces different floating sums. The lower-rounded surrogate mean is then incorrectly excluded from an inclusive tie. The same error makes an exactly tied observed/reference effect appear strictly larger. This can change actual reported conditional p-values and necessary stress-guard flags; it is not cosmetic display precision. The owner-locked broad verdict does not make incorrect reported null statistics acceptable, and the helper is intended for later unchanged scientific use too.

Independent reproducible synthetic case (all nine scores are finite and nonpositive; Bstar equals B2):

```python
import numpy as np
from fractions import Fraction
from paper13_ki_execution1 import control_core as c

v = np.array([.1,.2,.3,-.1,-.2,-.3,.1,.2,0.,0.])
mice = [str(i) for i in range(10)]
scores = {}
for j, mouse in enumerate(mice):
    base = -2*abs(v[j])-.001
    scores[mouse] = {name: base for name in c.LABELS}
    scores[mouse]['D'] = scores[mouse]['C'] = base+v[j]
observed = np.array([[scores[m][name] for name in c.LABELS] for m in mice])
permutation = [6,9,8,2,4,1,7,3,0,5]
surrogate = observed[permutation]
assert sum(map(Fraction.from_float, c.effects(observed)[:,3])) == \
       sum(map(Fraction.from_float, c.effects(surrogate)[:,3]))
arrays = {suite: np.broadcast_to(surrogate, (999,10,9)).copy()
          for suite in c.SUITES}
report, _ = c.summarize(arrays, scores, mice)
print(report['beyond_baseline_null_guards']['D'])
```

Observed floating mean is **.030000000000000006**; each surrogate's floating mean is **.029999999999999992**. Exact rational sums of the supplied effects are equal. The correct inclusive count is 999, hence plus-one p=(1+999)/1000=**1**, Holm2=**1**, and observed strictly above tied temporal/history q95 is **False**. Actual output is conditional p=**.001**, Holm2=**.002**, both stress-above flags **True**, and `numerical_reference_conditions_met=True`. The same defect affects C in this fixture. Thus this can falsely label every necessary numerical reference component as passing.

Required repair before real controls: use consistent deterministic, tie-preserving arithmetic for equal-mouse effect aggregation and the conditional inclusive-tail and strict percentile-reference decisions, retaining the exact supplied-effect interpretation and registered linear quantile convention. Exact common-denominator integer/rational totals with a properly defined linear interpolation comparison are one defensible approach. Keep report formatting separate from decision arithmetic. Do not add a favorable epsilon, round to selected decimals, change alpha, alter plus-one/999, change Holm2 or select a different percentile/reference after outcomes.

Add this nonpositive-score counterexample as a regression for **both** conditional p/Holm and strict temporal/history reference comparisons. Validate against an independent Fraction oracle over cancellation, permutations, exact ties and nearby unequal cases, including quantile interpolation. Preserve the failed r1 candidate/review, prospectively register the ordinary correction, re-freeze and independently re-review before any actual E control replicate. This repair does not require a new scientific hypothesis or weakening the owner's amendment.

## Other control and runner assessment

No additional P0/P1 was found in the reviewed transformation/gating/retention portions, subject to the summary repair:

- Temporal control independently permutes each unit/epoch's six five-bin strata, preserving each 500-ms stratum count multiset and original nominal denominator. Histories/filtering/leaky states are recomputed through the already reviewed frozen prediction operators.
- Donors are different epochs from the same current input partition and original ordinal quartile, using rejection-sampled derangements; groups with fewer than two fail rather than pool. The current E worker supplies only original E ordinals. Original outcomes are scored before donor HMM filtering updates; donor sequences drive designated neural histories, original nuisance trajectories remain. The independent donor-path and future-causality tests from the prediction core still pass.
- Task/order permutations move each entire eleven-column nuisance trajectory together; the same resulting nuisance feeds baseline/B4 offsets and both families. No neural outcome sequence or partition identity is changed by that suite.
- Conditional B* generation includes every bin including warm-up, with reset causal histories and frozen original coefficients/scalers. A separate independent synthetic script reconstructed sequential Poisson means for **all five** possible baseline identities, all 30 bins, from explicit past-count lag sums/source terms and nuisance covariates. All match (rtol2e-14). Invalid/overflow means stop; no clipping/refit/new draw rescue is used. The original tests separately exercise overflow and an explicit B2 oracle.
- The fixed four-suite order, seeds130101-130104 and suite -> replicate0..998 -> sorted mouse order use one RNG stream per suite. A separate **synthetic stub** runner probe consumed one RNG value per scheduled call and verified all **39,960** positions against independently generated expected streams, along with 3,996 replicate completion events. The scoring function and mmap flushing were replaced by synthetic stubs only for this scheduling probe; it performed **zero real control replicates** and wrote only ignored synthetic work artifacts.
- Arrays retain 999 x10x9 labels per suite, including Bstar alias; all six paired effects/equal-mouse distributions are retained. Shape/finite checks reject missing/invalid rows. The conditional formula is plus-one/1000 with Holm2, and no D-C parametric superiority test is invented. The task-order reference cannot rescue a failed claim. The mathematical definitions are correct; their exact tie implementation is the P1 above.
- Approval/hash checks precede input loading. M5 completion, development role and frozen model/E-state hashes constrain inputs; no source reader, parameter fitter, E scaler fit or final-role worker exists in this runner. Exact original ten sorted mice and original 30x30x8 E data are required.
- Exclusive execution journal and suite-file creation prohibit silent reruns after a failed/interrupted attempt. NaN cells identify unexecuted values, completed cells are flushed, durable per-replicate/per-mouse events identify prior successful cells, and errors record active suite/replicate/mouse without overwriting prior results. The injected-failure test preserves the first successful mouse and second-mouse failure, refuses a repeated execution, and makes no extra replicate call. Existing source/threshold/numerical failure gates remain unchanged.

## Scope and required next action

This review does not certify the complete pure sensitivity implementation, actual sensitivity panels, any 999-real-control study, final C calibration, D export/evaluation or manuscript. Original sign-null/exchangeability/plugin-model limitations remain; implementation correctness alone does not establish their biological assumptions. The owner amendment permanently withholds the affected broad confirmatory verdicts regardless of any future numerical guard output.

Repair the demonstrated summary defect synthetically, preserve the candidate and obtain fresh stage review. Until then **do not execute the actual E controls**. No owner ambiguity remains for this repair. No approval file is created by this reviewer, and the failed review does not revoke valid saved M1-M5 results or change any original science.

No network/raw source/new model fit/actual control study/final C/D neural access was performed. This review used saved-evidence reproduction and synthetic arrays/probes only. Only this new review file is written, apart from ignored synthetic artifacts made by tests/probes. Earlier reviews remain unchanged. The earlier checkpoint's remote receipt and the newly dirty amendment state are separate facts; this review makes no current clean-tree/Git closure claim and no full mission/scientific PASS.
