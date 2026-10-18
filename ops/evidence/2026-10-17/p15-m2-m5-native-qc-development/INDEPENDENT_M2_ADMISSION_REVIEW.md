# Independent internal M2 admission review

Mission: P15-M2-M5-NATIVE-QC-AND-DEVELOPMENT. Base: `30cb925f505d63ae52bb1461d9ab153a52f1888e`. Review date: 2026-10-18 UTC.

Decision: **ACCEPTED_M2_DEVELOPMENT_SOURCE_AND_A_PHYSIOLOGY_GATE**. Open P0: 0. Open P1: 0. Actual `M2_SOURCE_QC_PASS=true`, `DEVELOPMENT_ELIGIBLE_MICE=10`, `DEVELOPMENT_LABS=8` is supported by the saved admission gate and independent A-only recomputation below. This is internal review, not external peer review, whole-mission completion or M3 numerical certification.

## Reconciliation and scientific scope

The original 20 candidates remain unchanged: 12 Development and 8 Final reserved. Of the 12 Development candidates, NYU-37 fails the frozen B epoch floor (31 < 40), and CSHL059 has zero epochs under the frozen no-extrapolation sync-domain policy. Neither mouse's neural payload was requested for M2. These are retained per-mouse coverage exclusions, not replacement opportunities or retrospective source/clock PASS. The remaining ten fixed candidates all complete A-only physiology and each supplies eight primary qualified MOp units. Their eight original laboratory labels reconcile exactly to COHORT.csv.

Final eight remain metadata-only possibilities. Their wheel support and C physiology remain unverified/outside this mission's neural authorization. No Final neural observation is part of this review. The two original M0 pilot animals remain Development, with four original payload objects reused by their original SHA256 receipts. Their historical exposure is not independent confirmation.

| Development mouse | Valid A epochs | Valid B epochs (task metadata) | Valid E epochs (task metadata) | A-qualified units |
|---|---:|---:|---:|---:|
| KS046 | 346 | 116 | 119 | 35 |
| PL033 | 366 | 121 | 114 | 16 |
| SWC_043 | 303 | 102 | 99 | 9 |
| SWC_038 | 481 | 156 | 160 | 27 |
| CSH_ZAD_026 | 505 | 151 | 162 | 56 |
| NYU-30 | 398 | 135 | 125 | 18 |
| KS051 | 218 | 71 | 76 | 26 |
| ZFM-01937 | 260 | 85 | 87 | 12 |
| CSH_ZAD_019 | 363 | 120 | 115 | 62 |
| UCLA035 | 547 | 168 | 172 | 53 |

B/E columns above are authorized task/observation metadata, not neural summaries or scored outcomes. Every admitted mouse exceeds A>=80, B>=40 and E>=40. No B/E neural export, real model fit or predictive score was required to establish this M2 gate.

## Independent verification performed

- Verified all 34 source/code/task-state hashes in READER_GATE.json against current bytes, and the accepted r2 review SHA256. The executed reader, source-integrity helper and physiology implementation remain the exact reviewed versions. The gate predates all saved A QC attempts.
- Inspected all ten COMPLETED A-QC journals and reconciled their subject/lab identities and outcomes against all twelve Development rows in M2_PHYSIOLOGY_GATE.json and the unchanged cohort. Both excluded mice have `neural_access=false`. Every completed journal has role A and B_export/E_export/Final_access false.
- Verified all ten authorized A-export SHA256s against their journals, then read only those A exports. No full-record neural cache, B/E export, Final neural data or network was accessed by this reviewer.
- Independently recomputed **all 446 unit records** using an interval-index assignment algorithm separate from physiology.unit_qc: valid-epoch spike counts, same-epoch adjacent ISI denominators and refractory numerators, original A trial-quartile exposure/spike/rate values, primary and strict qualification, complete ranked lists and all **80 selected unit/UUID identities** agree exactly (floating rates within absolute 1e-12). The ten journals contain 314 primary-qualified units; only the frozen first eight per mouse are selected, without padding. The saved strict-QC indicators total 272; that count alone does not establish any future sensitivity-coverage or scientific robustness claim.
- Independently verified exported trial IDs/epochs equal the saved valid A mask, timestamps are finite and ordered, and every exported timestamp falls in the original A role's half-open time interval. Guard/outside-valid-epoch A rows are retained for registered role-local ordinal preservation; physiology uses only retained epochs. The independent recomputation creates no cross-epoch ISI pair.
- Reconciled all twenty journaled neural object identities/bytes/UUIDs with frozen source and header pins. For sixteen newly downloaded objects, recorded version identity agrees with the header pin. Four reused M0 object SHA256s agree with original successful M0 receipts; their absent new-download response fields are not falsely treated as fresh GET evidence.
- Prior pre-neural r1 failure and accepted r2 remain preserved. No thresholds, source revisions, cohort allocation, model definitions or fit budgets changed to achieve admission.

The existing NATIVE_COHORT_SOURCE_REPORT.csv was produced as the prephysiology metadata inventory and still says NOT_RUN in its physiology column at this review point. It was not used as contemporary physiological admission proof. The authoritative current stage evidence reviewed here is the complete A journals and M2_PHYSIOLOGY_GATE.json. Final mission reporting must reconcile that metadata snapshot with these completed outcomes rather than present its old column as current.

## Exact stage evidence identities

READER_GATE.json SHA256: `b63bd6f11930c58e632ecbe1f50c704bcdc330eca4321b94543d228d806d5147`.

M2_PHYSIOLOGY_GATE.json SHA256: `7de5edf523a04f1e945ff8cf65ca2b080ca390154cf8ba07104abbea5833304e`.

Executed reader SHA256: `fc3f4df8d29a2bd26dafa083fecf66e99892ec3d9fa28926bf66796dda9be613`.

Executed source_integrity SHA256: `453e7041a5954627ec41b195a9ce7fbbeb74e04f656f1a1aa9e57b732931aff0`.

Executed physiology SHA256: `1e85584d4f779df9b063941b153715def105ad9cf006046fa7694eb1a12176fd`.

| A-QC journal | SHA256 |
|---|---|
| KS046_A_QC.json | bebe37c19d1c268989f3cd7bb51be732a34dc771fc844cf8d9427ceba28f3f81 |
| PL033_A_QC.json | 349b9cb5d549ff93fc613f0bc118dbc51901527a7645483dcf4eb4a6978c0fac |
| SWC_043_A_QC.json | 833cf56ac3687369ca2340b5955195b4f6012a1c9f293114a81e953ec3bc229b |
| SWC_038_A_QC.json | 91a2a1bfb2ca9eaecde5ba41d0e014ab799ef28cb889a7b7672eb785d3f7db83 |
| CSH_ZAD_026_A_QC.json | e43969f0c40f39e8c8404aebd7118110dc286d561fb817fa8baaed3849a6f590 |
| NYU-30_A_QC.json | f144ea7397f342b49c954df9ac754b0df03de4b045eae0775589636a4f041c7d |
| KS051_A_QC.json | 0afb65bfe1054c9163516673ecdb5d91ddc2a373a6ce546ac34bb7909e7a9a76 |
| ZFM-01937_A_QC.json | 879232357126a7796a43c1c0724c3934a46c88cfe4b6d8b9058d0fcab6ad7cdb |
| CSH_ZAD_019_A_QC.json | 720c03d90739724f3f77434e37764fd1713adaa18027b565fa4f1b8c24b3b505 |
| UCLA035_A_QC.json | aa925c7123b7b8493c526d2daf1966207e7453075d87b9c35058d72072b57ebc |

## Readiness boundary

M2 Development admission is supported. The next authorized stage is construction and independent certification of the exact M3 production worker. **PRODUCTION_NUMERICAL_PASS is not established**, and no real fit or B/E neural release is approved by this review. Original mathematical/gradient/PG/causal-prediction tests must pass before real fitting; the earlier 31 source/reader tests cannot substitute for them. Final C/D access remains forbidden.

Only this review artifact was written by the reviewer. No model fitting or scientific evaluation was rerun.
