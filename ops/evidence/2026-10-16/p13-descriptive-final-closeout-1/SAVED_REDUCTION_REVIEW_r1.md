# Independent saved-reduction diagnosis and repair review r1

Mission: `P13-DESCRIPTIVE-FINAL-CLOSEOUT-1`.
Scope: saved log-score arrays, result JSON and static code only.
Decision: **SAVED_AUDIT_ORACLE_DEFECT_CONFIRMED; SEPARATE NONSEMANTIC SAVED-ONLY REPAIR JUSTIFIED**.
Open P0: **0**. Open P1: **1**, the currently failed saved-audit comparison below. This is not evidence of a new scientific D failure or permission to repeat D.

## P1 — Bitwise equality compares different floating reductions

`paper13_descriptive_final1/audit_saved.py:38–39` reduces stored60x30 joint-bin arrays over their60x25 scored region and demands exact equality with the original serialized mean. However, frozen `paper13_ki_execution1/predictive.py:63–64` saves each baseline sequence after summing8 unit log terms, while computing its scalar score by directly reducing the60x25x8 unit-log array. Lines73–74 do the same for continuous C. Two association orders need not give the same binary64 result. In contrast, D/S lines68–69 both serialize and reduce the same joint-bin array; Bstar aliases B2 at75.

Independent saved-only inspection confirms **22 unequal cells among81 mouse/model entries**, maximum absolute discrepancy **2.220446049250313e-16**, maximum **2 ULP**. All18 D/S entries match exactly; all nine Bstar/B2 score and sequence aliases match exactly. All arrays have the required60x30 finite float64 shape and match their recorded SHA256 identities. Every saved joint-bin log score inspected is nonpositive. For example, mouse128514/B1 stores -0.9914513135426504 while the grouped reduction is -0.9914513135426505. The failed reproduction occurs at this equality assertion after88 synthetic cases pass; native D exit0 and that later audit exception are separate evidence.

The source-level reduction distinction and small family-specific discrepancies support floating association as the diagnosis. Joint bins do not preserve the original per-unit float terms, so they cannot supply a lossless reconstruction or independently prove the absence of cancellation among those unseen terms. No raw neural counts, likelihood evaluations or new experiment is needed or authorized to resolve this saved-oracle defect.

Original `FINAL_D_RESULTS.json` SHA256 at inspection: **3619ae66a55200cf4e05126d25ef23e31eb4102cd18b24187134b615fd4cc7da**. Preserve it and all existing scientific values unchanged.

## Fixed forward-error derivation for a separate audit

Use binary64 unit roundoff **u=2^-53**, `gamma(k)=k*u/(1-k*u)`, and fixed dimensions **N=12000 unit terms, M=1500 scored bins, U=8 terms/bin**. Let the unseen computed unit-log floats be `a_i`, their exact sum be T, and A=sum(abs(a_i)). Let B be the **exact dyadic sum of the1500 saved scored-bin floats**, computed using integer ratios/Fraction rather than another floating sum.

Under the explicitly stated premise that the unseen computed unit terms are nonpositive/noncancelling, A=abs(T), group-rounding error is at most gamma(8)*A, and A<=abs(B)/(1-gamma(8)). Conservatively allowing the full12000-term reduction plus division, and the1500-bin reduction plus division, gives the following bound on the discrepancy between the two stored/reconstructed mean reductions:

`E = abs(B)/12000 * ((gamma(12001)+gamma(8))/(1-gamma(8)) + gamma(1501))`.

Compare the **exact binary64-as-rational mean residual** to this **exact rational bound**. The deliberately conservative operation counts include the final divisions and are fixed by the registered dimensions; they are not selected from the observed2-ULP discrepancy. No epsilon, np.isclose, decimal rounding, convenient step or scientific alpha/PG/FD/coverage threshold is changed.

As an independent diagnostic, all63 baseline/C/Bstar cells satisfy this fixed conditional bound. Bound values range **7.584782302187022e-13 to3.3509580339146424e-12**; the largest observed residual uses approximately0.00015493 of its corresponding bound. This calculation is **conditional aggregate compatibility**, not exact all-model bin reconstruction. Nonpositive joint bins do not establish the unseen-term premise. State that limitation explicitly and do not promote this check into proof of scientific correctness, individual log-term identity or null validity.

## Smallest acceptable repair and remaining review

Prospectively register a new saved-only audit/verifier/PowerShell entrypoint, leaving the original audit, original failed receipt, all pre-D638 frozen bytes and all real scientific artifacts unchanged. Preserve the failed equality/traceback as historical evidence. The new entrypoint may apply only the fixed bound above to B0–B4/C and the corresponding alias, with strict dimensions/dtype/finite checks and disclosed premise. Keep **bitwise D/S checks**, **exact Bstar/B2 score-and-array aliases**, and all saved array hashes.

The owner's proposed exact bindings are appropriate: original per-mouse primary JSON scores, the completed-mouse journal score dictionary and final-result score dictionary must match exactly. Recompute all six statistics from the **original serialized means**, preserving those means and all scientific thresholds; never substitute the grouped means, average the two reductions, round a score or recompute a neural likelihood. Retain all one-shot/control-completion/error checks. Labels should distinguish aggregate compatibility and archival integrity from unavailable lossless per-unit reconstruction.

Test the new helper on synthetic nonpositive12000-term arrays and their8-term group reductions; test incorrect dimensions/dtype/nonfinite values, materially corrupted aggregates and exact-rational boundary decisions. Demonstrate that a one-ULP D/S or alias mutation is rejected and exact score/journal/final bindings reject tampering. A cancellation example should document why joint-bin signs alone cannot establish the premise. Preserve the original88 tests and run fresh affected saved checks on the newly frozen audit state. No old source substitution or changed scientific result is permitted.

This is within the owner's allowance for reviewed bounded software corrections preserving scientific semantics: it repairs a post-execution saved-evidence comparison, not the consumed evaluator, numerical model, control, sensitivity, data partition, D result or scientific PASS oracle. It grants no new D access, fit, draw, rescore, second assessment or post-D scientific repair. The current saved-reproduction P1 remains open until the separate implementation/tests and actual new reproduction are reviewed. Full paper/claim/PDF/mission closure review is deferred to the complete candidate; no manuscript/full scientific PASS or prospective Git receipt is certified here.

Only this new review file was written. Independent calculations read saved joint log scores and JSON; no raw C/D count array, raw source, network, model fit, predictive evaluator, real control or numerical replay was accessed/executed.
