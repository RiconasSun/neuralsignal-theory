# Independent static time-precision review 1

Mission: P15-M2-M5-NATIVE-QC-AND-DEVELOPMENT. Review date: 2026-10-18 UTC. Scope: frozen source/protocol interpretation and code path only. No native table values, real A/B/E/Final neural arrays, effects, fits or new numerical replay were read/run by this reviewer. Existing accepted/unsuccessful reviews and all scientific evidence remain unchanged.

**Judgment: SOURCE-TIME EQUIVALENCE IS UNRESOLVED PENDING THE BOUNDED A-ONLY EVIDENCE AUDIT.** Static serialization inspection alone neither establishes a changed scientific observation nor clears the issue. B/E access must remain closed while this material source-fidelity question is examined. A prospective hash of a derived JSON file does not itself authorize a new scientific time-quantization policy.

## What the exact frozen contract says

| Frozen source | Requirement and interpretation |
|---|---|
| SCIENTIFIC_PROTOCOL.md:21 | Serialize original pinned-native trial ordinals/values and deterministic partitions before neural QC. The source is the original native table, not an independently redefined rounded table. |
| NUMERICAL_POLICY.json:2; SCIENTIFIC_PROTOCOL.md:33 | Computation dtype is float64. This does not by itself prescribe a JSON encoding or authorize decimal quantization of input values. |
| FEATURE_MODELS.md:3 | Events/samples are available only when time < bin start; equality is deferred. Subsequent bins use the source event value. Counts are half-open. |
| FEATURE_MODELS.md:27,31 | Behavioral support and four disjoint strictly past neural windows are anchored to the source stimulus/bin schedule; no current-bin input or cross-epoch history is permitted. |
| SOURCE_QC.md:15,19,25 | Native event ordering/support, half-open QC observations and strictly past held wheel samples must be respected. The separate one-AP-sample range check is not a rounding allowance for bin membership or event availability. |

There is **no literal statement** requiring a particular JSON format or a bit-for-bit float64-to-JSON-to-float64 round trip. I did not find a prospectively registered ten-decimal timestamp policy or source-time error budget either. It would therefore be wrong both to invent an explicit bitwise-storage requirement and to treat an arbitrary rounded cache as automatically equivalent to the registered source values.

The existing PG, AD and FD thresholds concern derivatives/convergence of the supplied objective. They are not permission to change counts, event indicators, wheel predecessor indices, masks or input source coordinates. Passing those gates on a rounded-input objective does not prove source equivalence.

## Demonstrated static path

metadata_qc.py computes task masks/cuts from the loaded native table, then at line110 calls `json.loads(tr.to_json(orient='records'))`. Inspection of the installed pandas API confirms `DataFrame.to_json` defaults to `double_precision=10`. This is potentially lossy decimal formatting; it is not the same guarantee as Python's round-trip float representation. I did not inspect real rows to decide which values actually change.

The saved JSON trials are later used by reader.py for A role time endpoints and QC epochs, by training.py for stimulus-anchored bins, and by features.py for searchsorted counts/lag windows, strict event comparisons and held wheel lookup. Thus full-precision mask construction and rounded downstream event construction coexist in the current path. A raw-source hash proves custody of the original table, and the JSON hash proves integrity of that derived snapshot; neither hash alone proves the two numerical views are equivalent.

For ordinary session-second values, ten decimal places suggests errors on the order of 1e-11 seconds. That scale comparison is not a PASS argument: searchsorted, strict `<`, categorical masks and predecessor selection are discontinuous. A tiny signed displacement can change an exactly coincident boundary. Physical acquisition resolution cannot be substituted for checking these actual predicates without source-specific proof.

## What the authorized saved/A-only comparison can establish

The bounded audit should distinguish source value differences from their downstream effects. Appropriate evidence includes original versus saved event values, original row/cut identities and missingness; masks/checks; selected valid epochs; half-open target counts and each history window; causal event indicators and wheel-held indices; original A QC counts/ISIs/ranking where affected; and raw/transformed nuisance differences, active flags and scaler effects. Continuous floating-point differences must be reported separately from integer/Boolean/index changes. No favorable tolerance may be introduced after inspecting results.

Using only existing A exports has a specific limitation: those exports were already filtered by saved role endpoints. Comparing bins inside them cannot prove that no source rows were omitted/added in the tiny interval between a native and saved role boundary. This matters particularly to S07, which consumes every original within-role selected-unit spike ordinal, including rows outside retained epochs; a boundary row can shift later thinning draws even if main retained-epoch counts agree. State this limitation unless boundary identity can be established from separately authorized existing evidence. This report does not authorize a broader source read.

A measured change in any registered discrete membership/target/history/causal-availability predicate is a verified implementation/source-fidelity defect, not an optimizer failure or harmless serialization claim. Preserve all affected fits, stop downstream activation under the original gates, and do not silently rewrite task files, change bin tolerances, rerun QC, refit or reset attempt budgets. Even if discrete quantities match and only small continuous differences remain, an independent source-equivalence assessment is still needed; a newly invented timing tolerance cannot retrospectively clear it.

## Exact inspected identities

| File | SHA256 |
|---|---|
| paper15_m1/SOURCE_QC.md | da5ca1a926df11cdce32f786a6e1de5ea9ed7648a5ca73045a4bbead4b8407e7 |
| paper15_m1/FEATURE_MODELS.md | 37ef100353913eb2a99d92ffb9404093b2d850ce326fd6b497dec31ec2453b4e |
| paper15_m1/SCIENTIFIC_PROTOCOL.md | fbdc36c393456b02a87b7e23b15bf7aa422458478ff1a621a0e6f1bdf2da03cc |
| paper15_m1/NUMERICAL_POLICY.json | cc0c926b04540f1787e0a005f6566bf42225cb2bca159fd9accdd3e74ab0358e |
| paper15_dev/metadata_qc.py | 14068246912971fea75eacc510afd088230d1b1e174d14c175d9e17319008ecf |
| paper15_dev/features.py | 30d17b3a902429537e8b83fc9ac5a483933bdb8080ff890c5f43c6fc5f4dd3fd |
| paper15_dev/reader.py | fc3f4df8d29a2bd26dafa083fecf66e99892ec3d9fa28926bf66796dda9be613 |
| paper15_dev/training.py | 1c11098672df8d24c54770375c6c0c8db351622d533badf30bc11170dba0212d |

Earlier reviews verified saved-JSON internal consistency and their stated implementation/numerical surfaces. They did not independently establish native-event precision equivalence. Their historical acceptance is retained with that factual scope; it cannot be used to preempt this new evidence question. This static review makes no final scientific failure/PASS determination before the actual bounded audit results.
