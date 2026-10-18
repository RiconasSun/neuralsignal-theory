# Independent internal finite-control operator review 1

Mission: P15-M2-M5-NATIVE-QC-AND-DEVELOPMENT. Base: `30cb925f505d63ae52bb1461d9ab153a52f1888e`. Review date: 2026-10-18 UTC.

Decision: **ACCEPTED_PURE_OPERATOR_COMPONENT_ONLY**. Open P0: 0. Open P1: 0 within the finite-operator scope reviewed. This is not acceptance of a scientific reference suite, pre-E batch integration or any E access. No real data/cache/source/network, real fits, B/E observations or scientific reference draws were accessed or executed by this reviewer. Only this new review artifact was written.

## Frozen policy comparison

- Seeds use UTF-8, the frozen master string and first eight SHA256 bytes interpreted big-endian. PCG64 is explicit. Reference seed helpers reject A/C/D and permit only Development score roles B/E; thinning seeds permit A/B/E and reject Final C/D in this mission. They do not authorize reading any role by themselves.
- N1 visits retained epochs by increasing numeric original trial ID and calls one offset in 1..19 per epoch. All units' 20 warm+score bins rotate together; trial/unit totals are retained and input counts are not modified. Its output is a surrogate stream; the caller must retain original targets.
- N2/N3 donor strata are visited in sorted tuple order. Within a stratum, epochs are sorted by numeric original trial ID, nonsingletons receive one nonzero cyclic offset, and singletons receive neither a donor nor a draw. Side coding L/R/other, contrast threshold >.25, original-role half and wheel ties in the lower stratum match the frozen definitions when supplied the registered finite inputs.
- N3 uses the same donor helper with the caller supplying side/contrast/order keys without wheel. The pure helper does not itself choose replacement columns or define N3's statistic; those remain batch integration obligations.
- N4 groups original role trials into role-anchored consecutive blocks of five, discards incomplete/ineligible blocks, visits complete blocks in original ordinal order, and samples **one global nonzero cyclic offset across complete blocks**. It preserves within-block trial order and multivariate synchrony. It does not draw a new offset per target block. Fewer than two complete blocks yields unavailable donors with no draw.
- The coverage helper implements the unchanged >=30 epochs and >=60% original eligible exposure rule. Donor helpers return target indices so the caller can restrict both observed and reference scores to identical common exposures rather than change the primary cohort.
- S07 consumes one independent unit/role PCG64 stream over every supplied spike row for each selected unit, preserving original array order including duplicate timestamps and spikes outside retained epochs. p=min(1,2/r) uses the supplied unthinned training rate and still draws all rows when p=1. Returned arrays preserve source order; receipts retain p/seed/draw_count/kept count by unit and role. No score-based reranking or matching is performed by the helper.
- The history reconstruction uses only earlier microbins in the fixed four intervals and resets at each epoch, with the frozen physical denominators and zero pre-epoch history. It introduces no recursive Poisson generator or rate/count clipping.

These are finite destructive-reference operators. Their existence or numerical finiteness does not establish exchangeability, an exact conditional-null test, a successful scientific falsification suite or causal/movement independence.

## Independent fresh checks

Executed `paper15_dev/work/runtime/Scripts/python.exe -W error::ResourceWarning -m unittest paper15_dev.test_controls -v`: **9 tests PASS**, exit0. These include frozen seed/role isolation, N1 multivariate count preservation/no mutation, N2 nonself donors/draw schedule, wheel tie/role-half definition, N4 complete original blocks, coverage boundaries, full-role thinning, generator chunk advancement and causal microhistory reset.

Additional independent synthetic oracles:

1. Used a recording RNG stub with fixed outputs on shuffled trial IDs to verify N1's exact numeric-ordinal call order, three (1,20) integer calls and the corresponding rotations for every unit.
2. Used shuffled IDs and lexically distinct strata to verify N2's exact donor identities, one call for each nonsingleton stratum and no call for the singleton. This checked the actual RNG bounds and mapping, not only count preservation.
3. Used a nonzero original role start (7), reversed epoch input order and an incomplete original block to verify N4 makes exactly one (1,6) offset call, excludes the incomplete block, and applies the same global offset to all six complete blocks while preserving each within-block position.
4. Independently constructed the SHA256/PCG64 thinning masks for two units at different rates, duplicate timestamps and unselected-unit rows, separately for A/B/E. Every returned source row and draw count matched. This uses synthetic full-role streams only.

All additional checks passed. No implementation, test oracle or scientific threshold was edited.

## Necessary later integration verification (not claimed complete)

The future independently reviewed pre-E worker must supply: N2's exact strict-past .5s pre-epoch wheel magnitude and A-only median; N3's wheel-only columns24-37 replacement and registered B4-LL diagnostic; original targets and matching original/reference exposures; surrogate-past D filtering and corresponding C/history inputs; original A-only states and masks; all available model contrasts sharing each suite realization; fixed 999-replicate schedules and four-suite correction slots; coverage/unavailable/failed-suite preservation and honest assumption labels.

S07 must be called on the full original authorized-role spike sequence, with the original selected eight units and unthinned A rates. Calling the stateless helper independently on chunks would reseed; either one complete role call or a separately verified continuously advanced stream is required. The future persistent receipt must additionally identify the RNG/operator algorithm version and frozen code/runtime identity, as required by M1; this pure helper's returned dictionary alone is not the complete future archival receipt. No Final role stream or count may be consumed.

Those batch responsibilities are intentionally not implemented/certified by this operator-only review. A later pre-E integration review remains mandatory before any real E batch. No E gate, secondary scientific claim or reference-suite PASS follows from the present result.

## Exact reviewed SHA256 identities

| File | SHA256 |
|---|---|
| paper15_dev/controls.py | 093bc970d429575b66e9032006060198377633212312e817bcbd2a278a431a35 |
| paper15_dev/test_controls.py | c07d6b49b409e6e4f168bcc840b84cfde58f1ad8a50d468f59ac93254ae26529 |
| paper15_m1/STATISTICS_CONTROLS.md | 3a2665cc43cffac9af7e33ae5c61d937f7caf9cb4ca89c4e692ae4dc39fa0254 |

No prior failure or source/model policy is reclassified by this component acceptance.
