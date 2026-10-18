# Independent M3 numerical and causal source review 1

Mission: P15-M2-M5-NATIVE-QC-AND-DEVELOPMENT. Reviewed BASE: 30cb925f505d63ae52bb1461d9ab153a52f1888e. Reviewer: independent agent `/root/gradient_review`. Review date: 2026-10-17 America/Los_Angeles.

Decision: **NOT ADMITTED FOR REAL FITTING**. P0=0; P1=1. This review covers the identified model, independent derivative, feature and synthetic test sources, not an unwritten production fitting worker. No real neural arrays, B/E/Final observations, network calls or real fits were read or executed. No product code was edited. The reviewer executed only a small synthetic boundary-count reproduction; its results are below. Existing reported 12 model and 9 feature tests do not establish the missing boundary property.

## P1: history windows do not consistently use the canonical bin boundaries

Location: `paper15_dev/features.py:69-71`, within `observed_arrays`.

Targets are counted against `all_edges`, but history limits are independently recomputed using floating-point `bins-long` and `bins-short`. These operations can produce a different floating boundary from the already defined microbin edge. A spike on a canonical edge can consequently be moved into the wrong strictly past history window. This violates the frozen four disjoint windows and can alter B2/B3/B4 predictors, their comparison and the shared dynamic nuisance predictor.

Reproduction: synthetic stimulus=1 second; put one spike at each canonical edge `1-.5 + arange(21)*.05`, one unit. Compute target counts with the production feature function. At each prediction index compare its four histories with the sums of its own earlier target microbins over lag-index ranges [1,0], [2,1], [4,2], [10,4], divided by .05/.05/.1/.3 seconds. Only earlier canonical microbins are used; the current bin is excluded. There are 15 discrepant window assignments across warm/scored bins. Examples in scored bins:

| Prediction index / start | Window | Production Hz | Canonical past-count Hz |
|---|---|---:|---:|
| 11 / 1.05 | [.10,.05) seconds before bin | 0 | 20 |
| 11 / 1.05 | [.20,.10) seconds before bin | 30 | 20 |
| 14 / 1.2000000000000002 | [.05,0) seconds before bin | 0 | 20 |
| 14 / 1.2000000000000002 | [.10,.05) seconds before bin | 40 | 20 |

Required implementation repair: derive history interval endpoints from the same canonical microbin-edge indices as targets, respecting epoch reset and the registered window durations. Preserve half-open counting and the prescribed behavior for registered sensitivity bin/history configurations. Do not relax tolerances or alter the scientific lag definitions. Add a regression with spikes on every canonical edge, verifying all four histories for every warm/scored bin, then rerun feature checks and obtain a fresh independent review before real fitting. This is an ordinary implementation defect, not evidence that the frozen model mathematics is invalid.

## Mathematical and causal source findings

No additional P0/P1 defect was identified in the inspected model equations. The Poisson objective retains factorial and .05-second exposure; its denominator is population score bins T, not T times unit count. Intercepts are unpenalized, linear/state/logit free coordinates receive the specified ridge, fixed-zero constant columns are removed, and the parameter boxes/gauges and nominal D2/D3/S3/S4 counts match M1.

The HMM analytical gradient subtracts the differentiated warm-prefix likelihood from the differentiated full likelihood, including initial, transition and warm-up emission dependencies. The prediction API uses pre-bin weights and assimilates the current joint count afterward. The independent autograd implementation uses raw, unnormalized log forward equations rather than production posterior gradients. The IID mixture has no filtering carry; its same-K identity with IID transition rows is distinct from the larger S capacity guard. The fixed DCT basis, exponential ten-microbin weights, zero pre-epoch standardized history and separate A-score micro/q scaling are consistent with the source contract.

All 37 nuisance column positions were inspected. Stimulus/cue/response/feedback availability and wheel sample holding use strictly earlier timestamps. Wheel increment totals include the preceding held value. Previous completed-trial codes are frozen at epoch start; ordinal/session-time definitions do not use future trial count. Constant-feature scaling is fitted on score rows and shared through supplied state. `nuisance` itself maps two absent contrast sides to zeros, but `metadata_qc.task_masks` already excludes both-unknown/out-of-range contrast trials and `test_source.test_unknown_contrast_excluded_not_zero_filled` checks this. Consequently this is not classified as another scientific P1; the actual production worker must demonstrably consume only those admitted trials.

The derivative checker retains absolute and scaled coordinate errors and evaluates all three fixed central steps without selecting a favorable step. The synthetic tests cover three points for the main families, larger K at a boundary fixture, explicit conditional enumeration, IID mixture, outward-gradient signs and deterministic initialization. These are mathematical component checks, not evidence that a real fitting pipeline, attempt ledger, role release or global B selection already exists or passed.

## Required remaining certification coverage and scope

- Add the all-window canonical-boundary regression resolving the P1 above; the existing feature test checks only a few history entries.
- Strengthen nesting coverage with nonzero shared nuisance/history coefficients, explicit own/other exclusion, and zero-offset D/S and zero-added-coefficient C recovery of B4. Existing baseline nesting checks use zero added coefficients at initialization; inspection supports the identities but this is a weak regression oracle.
- Verify the full numerical values of the 37-column nuisance table, including prior completed-trial event equality, wheel signed/absolute increments and all four interval widths. Existing shape/event checks do not numerically exercise every column.
- The actual fitting worker still requires independent admission: closed-form constrained B0 including all-zero targets, frozen initialization/solver/start/attempt budgets, complete failure and coordinate-gradient records, independent real endpoint AD plus every fixed FD gate, actual score-bin denominators, admitted trial/unit/scale integration, causal ensemble prediction and role-specific B/E release. This review does not certify those unwritten integration paths or authorize real fitting ahead of their gate.

No new scientific grid, model, tolerance, optimizer, start policy or retry is proposed. All existing failures and the original M1 protocol must remain unchanged.

## Exact reviewed SHA256 identities

| Source | SHA256 |
|---|---|
| paper15_m1/FEATURE_MODELS.md | 37ef100353913eb2a99d92ffb9404093b2d850ce326fd6b497dec31ec2453b4e |
| paper15_m1/NUMERICAL_POLICY.json | cc0c926b04540f1787e0a005f6566bf42225cb2bca159fd9accdd3e74ab0358e |
| paper15_m1/NUMERICAL_SELECTION.md | 6580c55effc5ce13f07649279a39a009a66734407312413681d40e941a16bbef |
| paper15_dev/models.py | 30c46a983c62182bdd7d8b26d116b03522440ee9598e2dd72ebb54f33a1bd75c |
| paper15_dev/independent_ad.py | 919e8a82aea1e838dda5fb233bb462ebdad5a023d208fdef491771ecc0882dc3 |
| paper15_dev/features.py | 76fc7d8a545c3b3261db824d9d4053b144d21c2fea459f7b06cd5aedc731a16e |
| paper15_dev/test_models.py | 34a81644e2ebdd5cf80e9cdc7a127adfe4dc284e73a037377c9bf834190b96a8 |
| paper15_dev/test_features.py | a061b23cb49ef8a40bb4e6a723c5cdd329c1fe0d678028d44d3ca13d1a8b2f68 |

The three frozen mathematical-policy hashes were checked against `paper15_m1/PROTOCOL_FREEZE.json`. Later code changes require affected fresh checks and an append-only subsequent review; this failed review remains historical evidence.
