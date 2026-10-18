# Independent M3 numerical and causal source review 2

Mission: P15-M2-M5-NATIVE-QC-AND-DEVELOPMENT. BASE: 30cb925f505d63ae52bb1461d9ab153a52f1888e. Reviewer: independent agent `/root/gradient_review`. Date: 2026-10-17 America/Los_Angeles.

**P0=0; P1=0 within this component review.** The review-1 history-boundary defect is resolved. Accept the reviewed feature/model/independent-derivative components and `training.build_model` integration for consolidation into the production gate. This is not independent approval of the whole fitting worker, attempt/failure persistence, solver-budget enforcement, B/E release, model selection or real fitting. The separately assigned worker review and the complete source-bound production gate remain required before any real fit. Review 1 remains unchanged historical evidence.

## Resolution of review-1 P1

`observed_arrays` now creates one stimulus-anchored 50-ms micro-edge vector. Targets subsample this same vector, and all four lag intervals index its shared edges with epoch-reset clipping. Independently recomputed time-subtraction boundaries are gone. The registered physical windows, half-open counts, zero pre-epoch neural history and score epoch are preserved; there is no tolerance or scientific-model amendment.

The added regression covers 50-ms primary bins, 100-ms sensitivity target bins and the 250-ms history/warm-up case. The reviewer independently repeated the boundary property for **every warm and scored bin** under six fixtures: these three configurations crossed with both the old arithmetic edge representation and the new stimulus-anchored representation. Every history equals its canonical prior microbin-count sum divided by the frozen interval duration. No mismatches remain. This independently includes the scored positions that failed review 1.

## Fresh reviewer-executed synthetic verification

Runtime: `paper15_dev/work/runtime/Scripts/python.exe`; OPENBLAS_NUM_THREADS=1, OMP_NUM_THREADS=1, PYTHONDONTWRITEBYTECODE=1, ResourceWarning treated as an error. No real neural arrays, role exports, B/E/Final observations, network or real optimization attempts were read or run.

- All **11 production feature tests PASS**, including the complete manual 37-column numeric oracle, strict event boundaries, held wheel/previous-trial codes, future-behavior/neural invariance, A-score-only scaling, fixed-zero constants, DCT basis/finite-history reset, rich drift and repaired history boundaries.
- The explicit nonzero shared-nuisance nesting/dynamic-reduction test and nominal parameter-count test both PASS.
- The reviewer independently reran the all-coordinate analytical/AD/all-fixed-FD test at **24 synthetic points** (eight families times initialization, fixed intermediate and synthetic endpoint), the conditional HMM brute-force oracle, same-K IID mixture identity and larger-state/boundary derivative checks. All four test methods PASS. Maximum analytic/independent-AD scaled error across those 24 points: **1.6653345369377348e-16**. Maximum scaled finite-difference error over every retained step and point: **1.1584238013284676e-09**. These satisfy the unchanged synthetic AD<=1e-8 and every-fixed-FD<=1e-5 gates.
- Only the synthetic test's persistence callback was intercepted to retain its diagnostic rows in reviewer memory; production math, AD, finite differences and assertions ran unchanged. This prevented overwriting the already existing synthetic numerical certificate. No scientific oracle or acceptance assertion was replaced.
- Additional reviewer-created synthetic integration fixtures verified fixed-zero coordinates and actual free counts in ten `training.build_model` configurations: B0/B1/B2/B3/B4, D2/D3, S3/S4 and C. With one constant nuisance and one constant history column, counts were respectively 8,296,327,513,544,555,568,562,571,552; the C fixture also had one of two q columns inactive. Inactive coefficients remain exactly zero. No real arrays were involved.

The parent's reported full 55-test suite is additional evidence; this review's directly executed checks are identified individually above and are not represented as a separate execution of all 55.

## Source review and scope

The underlying `models.py` and raw-equation `independent_ad.py` are unchanged from review 1. Their Poisson factorial/exposure/population-bin normalization, intercept ridge exemption, free-coordinate boxes/gauges, HMM full-minus-warm derivative, prediction-before-assimilation and static-IID distinction remain consistent with frozen M1. The new nonzero nesting test now gives a stronger regression oracle than identical zero-added-coefficient initialization alone. The complete numeric nuisance oracle exercises the actual 37-column positions, prior completed-trial codes and wheel interval terms.

`training.build_model` passes the same A design, target, active-coordinate mask and ridge to B/D/S models. C appends the chosen rank/tau q columns and their independently persisted q-active flags, then passes the combined mask. Constant q columns do not silently become fitted parameters. The primary eight-unit nominal counts and actual active counts remain distinct. No validation or other-mouse coefficient input is introduced by this helper.

This review has **no remaining component P0/P1 finding**. It does not certify other training functions merely because their source file was opened. In particular the independent worker review must still approve real fit start/attempt budgets, hard numerical/failure gates and records, B0 constrained MLE integration, admitted A identity/scales, and the separation of A fits from later B selection/E reporting. No PRODUCTION_NUMERICAL_PASS or real-fit authorization is issued by this report alone.

## Exact reviewed SHA256 identities

| Source | SHA256 |
|---|---|
| paper15_dev/models.py | 30c46a983c62182bdd7d8b26d116b03522440ee9598e2dd72ebb54f33a1bd75c |
| paper15_dev/independent_ad.py | 919e8a82aea1e838dda5fb233bb462ebdad5a023d208fdef491771ecc0882dc3 |
| paper15_dev/features.py | 30d17b3a902429537e8b83fc9ac5a483933bdb8080ff890c5f43c6fc5f4dd3fd |
| paper15_dev/test_models.py | b28784635c22d2ebb81be088f9cd75a57accd25807449165f83b95f242af95ad |
| paper15_dev/test_features.py | 751fd03f1e084a9c7d1d35f5e001f43f028a18f2afc23a68a482b1ac6eb0b122 |
| paper15_dev/training.py at component inspection | 0d2520f4796772f5aece3119443a140a040430569141cec181819257679c0739 |
| training.build_model function source, UTF-8 via inspect.getsource | a40e8e29dda5df3e365d37fe3270dc0c8793c81f08b1541b3cbd9839f28bf0b6 |
| paper15_m1/FEATURE_MODELS.md | 37ef100353913eb2a99d92ffb9404093b2d850ce326fd6b497dec31ec2453b4e |
| paper15_m1/NUMERICAL_POLICY.json | cc0c926b04540f1787e0a005f6566bf42225cb2bca159fd9accdd3e74ab0358e |
| paper15_m1/NUMERICAL_SELECTION.md | 6580c55effc5ce13f07649279a39a009a66734407312413681d40e941a16bbef |

The full training-file hash identifies the inspected candidate; approval is restricted to its reviewed helper, whose function hash is given separately. Later worker-only repairs do not certify themselves through this component report. Any relevant feature/model/helper change requires affected fresh evidence and independent review. No product code was edited by this reviewer; only this append-only report was created.
