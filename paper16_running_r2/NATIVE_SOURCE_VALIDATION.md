# Native source validation — precision recovery R2

Mission P16-M2-RUNNING-PRECISION-RECOVERY-R2. Exact BASE67188e8e53a5c9a6c2ae7835b8b29aab7768db9e. Execution verdict **RUNNING_SOURCE_GATE_PASS**, subject to complete final saved-state/content review and actual archival gates. This is running-source recovery only.

## Contract and chronology

Independent normative comparison found no M1 requirement that rotation **source storage** be float64. M1 requires binary64 original timing and float64 computation. PRECISION_CONTRACT_REVIEW_2 accepts the prospective distinction. The original executed M2 all-three-float64 check and R1 SOURCE_SCHEMA_INCOMPATIBLE remain correct historical facts under their frozen implementation, not retrospective successes.

The first contract review rejected two documentation mistakes; their complete candidate and review are preserved. First preaccess review independently reproduced unknown-phase bypass and loss of completed native vectors during a hard kill. Both were repaired before any real access, with exact rejected candidate preserved.19 synthetic tests then passed and preaccess review2 accepted exact source hashes. The only test setup error was a missing `sys` import, before its child launched; original test/log and unchanged assertions are preserved.

One new first-source attempt on750749662 completed. Independent actual saved-state review verified full native vectors, source metadata/clocks, exact promotion,900 target causal calculations, all14 derived arrays and all six direct coverage cells. Only after exact approval was installed did the remaining27 source attempts run. The original global deadline was reused. No source or phase was retried, replaced or restarted.

## Native and arithmetic evidence

All28 registered Development sources completed; all have native `<f4` rotation and `<f8` start/end timestamps. **10,279,046 original rows** were preserved in84 individually compressed native vectors, with raw dtype/shape/byte SHA256, file hash and per-vector fsynced receipt. Each completed source has a complete NATIVE_SOURCE.json manifest and separate DERIVED_RUNNING.npz. Per-vector persistence happens before the next source dataset read; partial/failed files would remain evidence rather than valid states.

Every finite float32 rotation was promoted to float64 and cast back with exact byte equality, including the signed-zero/subnormal cases checked synthetically. Original arrays' raw-byte identities are unchanged after feature generation. Native float64 rotation remains supported, although none of these28 sources used it. Timestamps were never rounded, interpolated, normalized to another clock or otherwise corrected.

The exact literal alias is `/processing/running/running_wheel_rotation/timestamps` → `/processing/running/running_speed/timestamps`. Canonical target components are HardLinks; the verified alias and expected timestamp dataset have equal native object IDs/addresses within the same pinned file. No ExternalLink, arbitrary relative link, cycle, spoofed target or unauthorized/neural path is followed. Hard timestamp aliases remain acceptable only with the same exact target identity.

For every source, original identifier and two original clock scalars match frozen header references, rootNWB2.2.2 and source file ID/size/ETag agree, rotation units are radians, identity conversion/offset semantics are unchanged, timestamps are seconds, all running values/times are finite and ordered, row counts match, and durations are positive. Source metadata retains which scaling attributes were actually stored; absent offset retains the original reader's default0 interpretation, not a new empirical sensor-bias measurement.

Source row correspondence is supported by the frozen writer's same-DataFrame net_rotation/start_time/end_time mapping, actual same-file timestamp alias, shapes and numerical interval checks. It is not inferred from shape equality alone, and does not claim ground-truth sensor synchronization or independent physical calibration.

Actual interval division and tanh use float64 without clipping. The pinned original m2_core mathematics computes `r=tanh((net_rotation/(end-start))/10)`, r², color*r and explicit missingness. It retains original row order and source-row indices, excludes invalid/long intervals, requires end strictly before the target and duration/age in(0,.1], and uses the latest valid parent. Original flash-window subsetting and onsets+integer*.02 anchored targets are unchanged. Source-removed near-zero rows are not recreated; stored zero rows would remain actual observations rather than inferred stationarity.

All28 source outputs were rederived from saved originals under network/native-NWB denial. All14 derived-array dtype/shape/raw-byte identities match, and an independent candidate-mask lookup checks all900 targets/source (25,200 targets total), including invalid targets retained only as auditable metadata/features and excluded by original source-valid masks. Coverage includes only25,182 source-valid scored bins. No neural target/count is read or inferred.

## Precision and source limits

Float32-to-float64 promotion preserves already quantized source numbers; it adds no measurement precision. IEEE representation spacing depends on magnitude. No raw encoder truth, independent angle/velocity calibration, complete stationary observations, physical-time synchronization repair or extra sensor accuracy was measured. Zero retained source rows numbered0 across this release; the number and physiological meaning of previously source-removed rows are unknown. Missing r=0/flag1 remains an encoding, not a zero-arousal claim.

Saved native-vector hashes bind the arrays observed through h5py; pinned HTTP ranges bind source file identity. They are **not a full NWB cryptographic digest**. Local worker/value-path guards are not protection against a malicious administrator or an independent third-party custody service. No new cryptographic architecture is claimed.

## Resources and boundaries

R2 used **1,676 requests,207,760,032 payload bytes,207,761,708 conservative reserved bytes** across28 objects. Largest single-source payload7,869,768bytes and request count64 are below134,217,728/4096; each request≤1,048,576bytes. Total is below3,758,096,384bytes, concurrency1≤4, no redirect/retry/bulk fallback. External supervisors completed normally, child exit0/no kill. Global source-stage elapsed921.062seconds includes first review time and is below14,400; deadline339696.781 was never reset. Complete incremental payload accounting is in RESOURCE_LEDGER.json and the append-only budget journal.

Original M2 remains one failed attempt39requests/81912payload/81951reserved,27unattempted; R1 remains one metadata diagnosis44/85712/85756 with outcome B. Neither is refunded, overwritten or relabeled. All334M1+58M2+100R1 frozen payload hashes/sizes match. Git BASE preservation must additionally pass at actual archive closure.

New neural values, A physiological QC, model fits, B selection, E neural assessment, neural sensitivities/nulls and Final C/D access: **zero**. Exact cohort/coverage facts and limits are in RUNNING_COHORT_REPORT.md. M2_FULL_RESUME_READY=false; subsequent neural/QC/model work requires separate authorization and production validation. Stop after this reviewed handoff.
