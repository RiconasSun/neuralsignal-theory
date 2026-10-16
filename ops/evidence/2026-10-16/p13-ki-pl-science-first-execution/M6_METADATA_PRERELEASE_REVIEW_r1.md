# Independent M6 metadata prerelease review r1

Mission: `P13-KI-PL-SCIENCE-FIRST-EXECUTION`.
Reviewed UTC: 2026-10-16T16:23:32Z; interpretation completed before any reviewer final-C fit or D outcome access.
Reviewer: separate local reviewer agent; independent internal scientific/evidence review, not external peer review.
Decision: **FINAL PROGRESSION NOT APPROVED — MATERIAL_AUTHORIZATION_AMBIGUITY**.
Open P0: **0**. Open P1: **1**, concerning the unresolved final-progression interpretation below. No P0/P1 coding defect in the recounted recent-event predicate is identified. The known mandatory sensitivity coverage gate fails; its scientific implication must not be relabeled as an engineering bug or N/A.

## Independent metadata reconstruction

Verified every file in the original **85-entry** `paper13_ki_pl_contract1/FREEZE_r2.json` and the original protocol SHA256 **3129ee6017232db49a68136cc0cf04942d4abbf31081ef54782a23ddd3f01660**. Current activated allocation SHA256 is **d96b996d6c2961878460513a3a8f4dd58392180f0d793a34408b8588c79546b0**. Checked each of the nine final records' header bytes against its allocated header hash and matched original session/recording identity.

Two independent saved-only `python -B -` inspection scripts were executed. The first rebuilt the first 120 refined epochs from the original immutable disposition CSV, checked them against the activated allocation, then selected the final 60 by original ordinal. It gathered **all** actual `/stimulus/presentation/<series>/timestamps` entries from each frozen header, without using `sensitivity_plan.recent_keep`, `sensitivity_plan.metadata` or the new metadata-audit output. For each original epoch [a,b), it retained it precisely when there was no known onset t with **a-5 <= t < b**. All timestamps used were finite. All nine headers supply the four series AudStim_10kHz, OptogeneticSeries, air_puff and passive_bluenoise. No stimulus duration was inferred from a signal array or guessed from onsets. Every target tone equals the upper endpoint b and is correctly excluded by the strict upper comparison; the lower boundary is inclusive.

The second script used the **original frozen** `audit.candidate_windows`, `saturation` and `intersects` functions directly on the same headers. It reapplied original support/overlap, spike +/-1s, inclusive LFP +/-1s and applicable manual masks, sorted the refined windows and took the first 120. All **9/9** final allocations matched exactly. Thus the count does not depend on trusting the newly written sensitivity helper or a changed epoch selection. An initial attempt printed the successful 9/9 result but hit Windows cp1252 Unicode output encoding while printing protocol quotations; it was rerun with UTF-8 stdout and completed exit **0**. No scientific computation was changed to obtain this successful inspection.

| Final mouse | Original D epochs | Retained by (f) | Censored | Meets >=10 |
|---|---:|---:|---:|---|
| 128514 | 60 | 0 | 60 | No |
| 128516 | 60 | 27 | 33 | Yes |
| 152414 | 60 | 7 | 53 | No |
| 225757 | 60 | 24 | 36 | Yes |
| 225758 | 60 | 28 | 32 | Yes |
| 225759 | 60 | 28 | 32 | Yes |
| 258414 | 60 | 0 | 60 | No |
| 268947 | 60 | 21 | 39 | Yes |
| 273855 | 60 | 17 | 43 | Yes |

Only **6/9** final mice satisfy the ten-retained-epoch component, versus the mandatory **>=8**. There are 152 surviving epochs overall; the seven from mouse152414 cannot promote it into the contributing-mouse denominator, and pooling epochs cannot replace the equal-mouse requirement. This coverage shortfall is fixed by saved event metadata before any D neural outcomes. It is already sufficient to fail the panel even assuming all relevant unit-count conditions pass. It does not mean that the original M2 nine-final-mouse admission failed, that final neural effects are zero, or that D/C/S models failed numerically.

Read the new helper and confirmed its onset inequality agrees with this independent predicate. This bounded review does not certify the unfrozen `sensitivity_plan.py`, `control_core.py`, the new audit runner, their entire test suites, or any eventual final execution path.

## Scientific implications that are settled by the frozen text

`PROPOSED_P13_V2.md:82` requires whole-epoch censoring with exactly the interval above, target-tone exclusion and no replacement. `PROPOSED_P13_V2.md:86` requires >=8 final mice with >=10 retained D epochs and >=4 retained units for every mandatory panel, and explicitly says missing coverage makes the associated broad primary claim **INCONCLUSIVE**, a required sensitivity-gate failure, **not N/A**. `PROPOSED_P13_V2.md:61` conditions positive/family claims on applicable sensitivity gates. These requirements remain mandatory.

Accordingly:

- The panel's coverage cannot be repaired by excluding optogenetic onsets, checking only non-tone events, shortening the five-second lookback, censoring bins instead of epochs, replacing epochs/mice, pooling partitions, lowering ten/eight, or treating six as sufficient. Such actions would alter the frozen scientific contract.
- The associated broad primary claim is already unable to pass its registered sensitivity condition. More favorable primary p-values, B* or S guards, other sensitivity panels or nulls cannot compensate.
- Insufficient coverage is not an observed opposite effect and must not be called a scientific negative result, equivalence or absence of dynamics. Retained descriptive cells and the original 9-mouse disposition must remain visible.
- No automatic exception for a newly carved-out positive "narrower representation" claim is specified. Frozen descriptive scores/contrasts may be reported as such if their execution is separately authorized, while retaining the mandatory INCONCLUSIVE condition. Relabeling a failed broad target as a validated narrower target would require an explicit prospective scope decision, not reviewer inference.

## P1 — Final progression is not authorized by a uniquely determined reading

The actual owner activation says final held-out assessment follows **every prerequisite scientific gate** (`USER_MISSION.txt:18`), directs **stop on substantive scientific failures** (:29), automatic advancement only upon a passing registered gate (:30, :217), and a truthful scientific stop report if a prerequisite fails (:183). The activated frozen implementation records the stricter operational reading, **any scientific data insufficiency stops forward progression** (`ACTIVATION.json:70`). Under this reading, this known required-coverage failure is a pre-D scientific STOP.

There is nevertheless a distinct plausible reading of the incorporated protocol: paragraph86 attaches failure specifically to the **associated broad primary claim**, while paragraph90 describes one final bundle retaining failures and reporting valid positive/mixed outcomes. The original activation also explicitly requires preserving failed/unavailable panels (:147), reporting every comparison and completing a paper for a valid negative/mixed assessment. This can be read as allowing unchanged descriptive final measurement even when a broad claim is already necessarily inconclusive. It does not explicitly say whether a metadata-known mandatory sensitivity shortfall is itself an access prerequisite or solely an interpretive gate evaluated/reported with the final bundle.

The text uniquely resolves the scientific claim consequence, but does **not** uniquely resolve the owner's intended choice between **stop before final measurement** and **spend the one final exposure on an unchanged descriptive assessment despite the known failed broad-claim gate**. The derivative activation's strict stop wording supports stopping; it cannot independently manufacture an owner exception. Choosing continuation would consume consequential, once-only held-out exposure and change the practical acceptance target. Choosing that exception is outside a reviewer's authority. This is therefore a material authorization ambiguity, not a request to the owner to investigate a factual count that has already been independently resolved.

Required action: **do not start final C model fitting or release/score D while this final-progression decision is unresolved**. Ordinary saved/synthetic engineering, immutable evidence retention and already separately authorized E reporting need not be relabeled invalid, but cannot create permission to continue to the final stage. Preserve the failed gate, original model choices and all earlier evidence. This finding does not retract the preceding frozen E-only approval or certify unseen actual E outcomes.

### Minimum owner decision

The parent should present the confirmed six-versus-eight fact and ask one question:

> The mandatory recent-event sensitivity has only 6 of 9 final mice with at least 10 retained epochs; the frozen requirement is 8, so its associated broad primary claim must remain INCONCLUSIVE. Should we **(A) stop before final C fits/D and archive a scientific stop report**, or **(B) explicitly continue the unchanged, once-only final assessment for descriptive reporting, retaining this failed coverage gate and withholding the associated broad positive/temporal claims**?

Option B is not permission to lower any threshold, replace data, change models or promote a failed gate to PASS; it would be a recorded prospective owner decision about final execution purpose before final fitting/D exposure. If the owner instead requests a new confirmatory target or different admission/censoring rule, that is a new protocol/scope decision and must not be hidden inside the current execution.

No external environment item is missing and no further metadata lookup, neural access or real fitting is needed to resolve this authorization question. Saved sources establish the count; only the owner can choose the intended consequential stop/continue contract. The relevant pending baseline items include REQ-062/063 mandatory panels/failure retention and REQ-064 through068 final calibration/freeze/review/one-D progression. They must remain individually traceable and cannot be marked fully verified by this bounded metadata review.

## Boundaries

No network, raw neural source, neural count bundle, model fit, D likelihood or new E/D scientific output was accessed. D epoch timestamps/IDs and known stimulus onsets are frozen metadata, not held-out neural outcomes. No source/protocol/helper/test/approval file was changed. Only this new review file is written. No final release, scientific/full mission PASS, external peer review or prospective Git closure is certified.
