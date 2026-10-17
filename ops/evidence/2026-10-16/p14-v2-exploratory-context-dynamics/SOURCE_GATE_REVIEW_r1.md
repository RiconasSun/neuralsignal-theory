# Independent scientific source-gate review

Mission: P14-V2-EXPLORATORY-CONTEXT-DYNAMICS

Decision: ACCEPTED_SCIENTIFIC_STOP_ONLY. Scientific source decision: SOURCE_CONTRACT_INCONCLUSIVE. Open P0: 0. Open P1: 0.

The STOP is grounded in the prospectively registered essential annotation-compatibility gate. It is not a failed neural prediction experiment, a cohort-size estimate or a source-wide DATA_INSUFFICIENT finding. Full mission archival/remote verification remains outside this source-gate review.

## Evidence supporting STOP

The single first audit asset is CSHL049 / session d2918f52-8280-43c0-924b-029b2317e62c / asset 9e27ec60-e8d9-4dcf-a9a4-4b8acb6265ef. The subject matches and the frozen asset-path/session association is retained; the NWB identifier itself is a separate UUID, not claimed to equal the session UUID. All 837 trial rows are retained in original order. The saved comparison contains 6,696 event rows (837 trials times eight event fields), and additional trial categories/contexts are compared without selecting a favorable subset.

Canonical `bwm_include` and `saturation_stim_plus06` columns are absent. Their historical values therefore cannot be used under an assumed release equivalence. The registered bridge requires every available curatorial-event value and missingness pattern to agree, with the prospective 1e-6-second serialization tolerance and exact categorical/context equality. It fails:

- wheel movement onset / historical firstMovement: 794 mismatches, including one finite/missing disagreement; maximum finite discrepancy 0.16523332996939644 seconds. Of the mismatching rows, 592 were included by the historical bwm mask.
- stimulus offset: one mismatch, maximum discrepancy 12.699666666666872 seconds.
- The other six compared event fields, context values, stimulus contrast/side, choice, reward flag and reward volume agree under their registered comparisons.

The official documentary source at commit 118fc36cb3602934466ad2c6087c2b3b441f9f1f uses firstMovement in default missing-event exclusions and reaction-time masking. Its saved receipt SHA256 matches the documentary role. It establishes relevance of movement-event agreement to source curation; it does not establish that this current commit wrote either historical metadata or the canonical NWB. The discrepancy does not prove a canonical source defect, clock misalignment, or any specific writer/version root cause.

The 1,088 canonical unit UUID set and UUID-keyed quality labels agree with historical metadata, and canonical max-electrode indices are in bounds with probe-name/electrode-group internal consistency. These are narrower checks than full old/new unit-to-probe, atlas leaf or sorting-writer equivalence; no complete anatomical or processing-source certification is claimed. Target eligibility counts were not computed.

Stopping the remaining 12 registered assets avoids replacing an essential source-bridge failure with a favorable asset. Canonical eligible cohort size and physiological eligible mice remain UNKNOWN/null. Zero currently admitted mice is an admission-state count, not evidence that the official release contains zero scientifically eligible mice. Historical 13 candidates and prior 8+8 failures remain unchanged.

## Independent saved-only verification

With socket connections and Requests network calls denied, the reviewer ran 28 tests under warnings-as-errors and regenerated both source-gate outputs in a temporary folder. Both outputs are byte-identical to the frozen saved results. The 746 frozen historical source/metadata/document hashes pass verification. Transcript: REVIEWER_SOURCE_GATE_TESTS_r2.txt.

The earlier reviewer helper transcript REVIEWER_SOURCE_GATE_TESTS_r1.txt contains an unclosed CSV handle ResourceWarning from the reviewer's own reporting script after the tests and comparison completed. It remains preserved; the helper was corrected to use a context manager and rerun cleanly. No implementation, acceptance criterion or saved result was changed to resolve it. The separately preserved SOURCE_COMPATIBILITY_RUN1 deprecation warning was repaired without changing either scientific output.

Saved transport journals show 224 bounded range responses, 499,986 payload bytes and 448 HTTP transactions, one registered asset, and no recorded transport errors. This is opaque HDF5 metadata transport, not a claim that every transported byte can be proven non-neural. The reader's whitelisted decoded exports and schema are the applicable boundary: all value paths are permitted; the 59 unopened schema nodes contain no exported shapes. No new source request, real NWB/cache read, neural dataset decode, raw behavioral signal decode, physiological QC, fit, score or late-outcome access was performed by this reviewer.

## Required handoff interpretation

Preserve SOURCE_CONTRACT_INCONCLUSIVE and stop neural activation. Full scientific model/statistics/control registration remains incomplete because the essential source prerequisite failed. Do not relax the bridge, transfer masks, infer absent counts, reclassify this as DATA_INSUFFICIENT, or resume a subset after observing these discrepancies. Any substantive future resolution or protocol change needs the owner-defined scientific authorization boundary; routine archive/reproduction work can continue. No neural model finding or manuscript findings paper is supported.

Reviewed hashes:

- compatibility.py: 09d42ba094c9da8a23549768d65a5285a0ea77ab4d1860b4ced548b6c8e3b42f
- test_compatibility.py: bae6d080889d2b11aa7521b85dff9c5c36ee38be0e4536bbd59bc1c0a6ee2907
- SOURCE_COMPATIBILITY.json: fd22724aa8cddd313f2efacbf94da3f7b0c292a0358cd092645756e4f7ee116d
- TRIAL_EVENT_COMPARISON.csv: 93c268b5c388234acca67a8f89d088541f04bb1e1cb660c5f2d538174d4b6e5e
- canonical whitelisted values export: 5aeece0345d219ac1aaa8042d94e8d0719b197be8195eac6c379cef75570cec8
- canonical metadata schema export: 78460ca4d96fc234467a4c15021d772eebf5cd451e467ea1153304a8328ed287

No MERGE_ALLOWED, source compatibility PASS, neural activation or full mission PASS is granted.
