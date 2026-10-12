# Recovery QC and Limits

Frozen denominator: 26 distinct mice, 13 development / 13 final. Disposition:
8 verified reused completions, 1 failed new extraction, 17 not executed. Eight
completed sessions satisfy the unchanged per-mouse minimum of five CA1 and five
DG units. Known group counts are only 4/4; complete eligibility is unknown.

Known eligible units: 4,921 session-local units. Development: CA1 2,009, DG 569.
Final calibration QC: CA1 1,833, DG 510. No cap/reselection/refitting was applied
to reused artifacts. Aggregate exclusion reasons and nonexclusive physiological
causes appear in `results/M2/aggregate_QC_reasons.json` and the 26-row CSV. Counts
for failed/unexecuted mice are blank, not imputed. Trial counts come from frozen
stimulus metadata and do not independently certify neural completeness.

Transport: 18 new requests, each on a different chunk with one recorded attempt;
all 18 response bodies passed original exact header/length validation. Accepted
HTTP bytes: 73,947,536. No transient network failures. Seventeen completed blocks
and one pending block were checksum-audited in custody. Pending is NOT accepted.
Source-marker identity/range/directory/journal binding is verified only by the
corrected audit, not the preserved initial overstatement. ETag is not whole-file
SHA256. No data version change or source substitution occurred.

Native isolation: real zero-capability AppContainer denied source/key reads,
DACL regrant, direct network access (10013) and custodian memory access. Copied
scientific runtime imports and synthetic AEAD roundtrip passed. This does not
protect against a malicious host administrator or controller.

Local checkpoint atomic rename failed with WinError 5. A separate 20-trial
synthetic protected-directory audit reproduced one failure, retaining all trials.
It does not determine whether the underlying cause is a transient handle, policy,
security software or another filesystem interaction. No such explanation is
asserted. HTTP retries cannot repair this local failure under the frozen policy.

Curated-release limits remain: continuous native observation support is not
independently certified; peak-channel atlas assignment is not independently
confirmed histology. No neural mechanism, model preference, NAP or CWP validation
is established. M3-M5, null suites and final evaluation were not run here.
