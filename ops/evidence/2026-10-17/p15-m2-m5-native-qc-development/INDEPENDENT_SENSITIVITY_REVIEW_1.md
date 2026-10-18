# Independent sensitivity implementation review 1

Mission: P15-M2-M5-NATIVE-QC-AND-DEVELOPMENT. Independent reviewer: `/root/gradient_review`. Date: 2026-10-17 America/Los_Angeles. Frozen reference: `paper15_m1/STATISTICS_CONTROLS.md`, `FEATURE_MODELS.md` and `NUMERICAL_POLICY.json`.

**P0=0; P1=1. Sensitivity preparation/fitting is not admitted yet.** Existing main production fits were not reviewed or changed by this task. No actual neural cache, A/B/E/Final array or source network was accessed; only source inspection and synthetic tests were performed. Only this new review report was written.

## P1 — S05 changes the behavioral epoch reference while shortening neural warm-up

`sensitivities.prepare` passes `ep` from `observed_arrays(...,warmup=.25)` directly into `nuisance`. That value is `stim-.25`, while the original behavioral epoch reference is `stim-.5`. Frozen S05 specifies shortened neural warm-up/history with the same score window and **behavior warm-up unchanged**. Metadata support alone is preserved by `metadata_case`; the actual nuisance call does not preserve the behavioral reference.

This changes nuisance column24, the held wheel position relative to behavioral epoch start, and can change columns18/19's previous-completed-trial eligibility/freeze point. It makes S05 vary behavioral adjustment as well as neural history, contrary to its registered scope. The same integration pattern exists in `selection.extract_role` for future later-role sensitivity construction and must remain consistent with the corrected A preparation.

Independent synthetic reproduction: stimulus=1, identical scored starts [1,1.05,1.1], wheel timestamps at 10-ms intervals with position `2*time`. Calling the production nuisance function with the primary behavioral start .5 gives column24 approximately [1.0,1.1,1.2]; passing the shorter neural start .75 gives [.5,.6,.7]. The approximately .5-radian difference demonstrates that an unchanged metadata support mask is insufficient to preserve the actual behavioral design.

Required implementation repair: keep neural warm-up/reset and its history windows separate from the frozen behavioral epoch reference (`stim-.5`); preserve behavioral support (`stim-1` onward), wheel reference and previous-completed-trial code freeze in A preparation and the eventual later-role scoring path. Add a scored-row regression proving that common nuisance columns remain identical between primary and S05 while the neural history/warm-up changes as registered. This is an ordinary implementation defect; do not change the sensitivity definition or scientific protocol. If a different behavioral estimand is desired, it requires owner resolution rather than silently interpreting this case differently.

## Other inspected scientific and numerical behavior

No additional P0/P1 was identified in the reviewed source:

- All eleven case IDs and the primary/capacity-conditional unit counts match M1. Unit-count cases use the original A ranking; strict QC filters original qualified units with the stricter A criteria. S11 intersects A-qualified ranking with the exact center/plus-minus-two native contact-index MOp proxy, rather than asserting histological distance.
- Changed-epoch/saturation cases recompute A-only physiology and original-A-quartile eligibility on their retained case epochs; original role cuts and guards remain unchanged. Missing unit/trial/baseline capacity is retained as UNAVAILABLE, not padded or passed.
- S04 preserves .1-second exposure/five score bins and histories defined from the same 50-ms micro-edge support. S05's shorter neural windows are correct independently of the behavioral-reference defect above. S08/S09 dilate the actual frozen saturation endpoints, exclude affected epochs and never recode targets to zero.
- S07 uses the original primary eight units and unthinned A rates, role/unit-specific SHA256-derived PCG64 streams and all source spikes in role order. The inspected thinning primitive does not rerank with thinned scoring values or consume Final streams. The preparation retains per-role seed/probability/draw/retained-count receipts.
- S10 appends the registered four drift columns to all nonstationary baseline designs. Passing nuisance=41 to the production model keeps history masks correctly positioned rather than treating drift additions as history.
- Case preparation requires B selection to be frozen first but computes its new eligibility, unit ranking and transforms from A only. Case fitting uses only the already selected ridge for each of B0-B4, not a new grid. The prospective plan has five fits per available case, at most550 for the ten admitted Development mice, with the original overall sensitivity ceiling unchanged.
- The refit code uses the frozen L-BFGS-B options, same coefficient bounds/initialization, original physical PG<=.001, independent AD and every fixed FD step. It records failures rather than choosing a favorable checker step; the closed-form stationary case uses case-specific exposure/warm-up. Exclusive attempt acquisition and matching gate/plan checks prevent a second fit of an already claimed attempt. These observations do not certify a not-yet-created sensitivity gate/plan or actual case results.

## Fresh synthetic evidence and remaining scope

The reviewer independently executed all **six `test_sensitivities` methods PASS**, using the bundled runtime, single BLAS/OMP threads and ResourceWarning as error. This includes exact case IDs, original behavioral support/role guards, saturation dilation, the rich41 nuisance/history parameter map, all-step derivative checks at nondefault exposure/warm-up/rich designs, and the five-native-contact boundary proxy. These tests do not detect the S05 nuisance-reference error because their behavior-preservation assertion checks metadata masks rather than actual scored nuisance rows.

Before case execution, resolve the P1, retain this failed review and obtain an affected fresh review with exact source hashes. The actual selected-ridge plan and source/state-bound sensitivity gate must then be frozen and checked. Later E construction must use the same repaired behavioral reference and stored A transforms, and must follow its separate frozen-selection/access gate; this report does not authorize E access. Final anatomy/layer descriptive summaries and achieved A thinning rates remain reporting obligations, not biological or robustness conclusions already established here. No case fit, E sensitivity result or Final sensitivity analysis is certified by this source review.

## Exact reviewed SHA256 identities

| Source | SHA256 |
|---|---|
| paper15_dev/sensitivities.py | 8d58b5365981580b715232e6299c24260d5dc2cfe56f4b6c935527720b265bff |
| paper15_dev/sensitivity_fits.py | e0f674485fdf9745220bb7776dc2db0ee21aee8310d86c9efc3dded5b8a8014c |
| paper15_dev/test_sensitivities.py | 147a6a76306114167a885fa44988381af41f852c55df7defb5726cb9980704a5 |
| paper15_dev/physiology.py | 1e85584d4f779df9b063941b153715def105ad9cf006046fa7694eb1a12176fd |
| paper15_dev/controls.py | 093bc970d429575b66e9032006060198377633212312e817bcbd2a278a431a35 |

The report identifies the inspected source state before any sensitivity preparation/fit. Subsequent repairs require a new report; do not edit this historical review to match the repaired code.
