# P11-v2-R2-BOUNDARY-AUDIT-1

Scientific audit verdict:INCONCLUSIVE. Full52session denominator retained;
47DOCUMENTED_CONTINUOUS_SUPPORT envelopes confirmed,5unresolved,0contradictions.
Original R2 gate remains FAIL/DATA_INSUFFICIENT. No threshold or split changed.
No external spikes, new trial responses/final physiology, models/nulls orR3.

## Evidence

Prospective protocol registered before new source acquisition; separate source
and implementation lock registered before18tests and52NWB observations. Author
commit1d95162d2672e71dd234a31e4b8d70017a289ee3. All original tracked sources and
results hashed; scientific paper/gate files unchanged. Source receipts and
bounded206range SHA receipts retain provenance; partial ranges are not full-file
checksum verification. Opaque adjacent buffered bytes were never decoded.

All52NWB files are2.1.0 and have only two direct acquisition streams:events
(AnnotationSeries),experiment_ids(TimeSeries). No raw ElectricalSeries or
continuous acquisition timestamp series is present in those direct streams.
No signal, unit, response, trial-value or experimentID arrays were opened.

TTL1stimulusonset and55/66experimentstart/end are defined by the official author
code;99has no event definition in the94selected author source files. It stays
unknown, not mapped to recordingstart. Experiment instructions/start markers
are not automatically acquisitionstart. Descriptive schema statements alone
cannot provide per-channel start/end masks or missing-data guarantees.

## Five Unresolved Assets

| Asset | First TTL | First/Last event seconds (rounded) |
| --- | --- | --- |
|37347191-3430-47bb-a3b5-81bc1d81239e|1.0|1438781740.01 / 1438783742.16|
|383557c1-167f-42f4-be1e-6bb7d6948774|1.0|1452358746.04 / 1452360617.79|
|5f8737c1-8cc2-4ea2-8c00-085722c15db0|1.0|2441.04 / 4111.08|
|bed1fc5b-e8d1-40b1-9780-532df3f35804|1.0|915.93 / 2540.03|
|dab65d89-d309-4a67-bccb-d8f840961cfa|99.0|1439634720.85 / 1439636098.94|

All five event spans contain the already frozen scored intervals. That is
insufficient:these are event-stream endpoints, not independently documented
raw recordingstart/end or per-unit support. No first/last spike inferred range,
no candidate deletion, no post-hoc55search through response/finalTTLarrays.

## Clock And Synchronization

Native timestamp units are seconds. Author Python/MATLAB exporters scale event,
trial and neural timestamp source variables by1e-6 without subtracting TTL55.
This is a shared export scaling convention, not measured hardware sync error.
Some native values are epoch-sized(~1.4e9), others~1e3; do not assume all start
at zero or subtract anonymous session dates. The NWB reference dates are
deidentified/defaulted and are not independent acquisition zero evidence.
No new offset was fitted or inferred, and no neural clock was inspected.

Documentation and intact55/66envelopes confirm the prior47limited support
inferences. None of the52has new independent raw-stream/gap or per-unit dropout
certification. This audit cannot certify full cohort observation support or
physiological eligibility, nor establish that the missing records are unusable.

## QC And Reproduction

18controlled tests PASS:forbidden paths/indices, soft/external links, no
fullTTL/outcomes, scalar/clock validity, half-open1second containment,
unknown1/99support, nonzeroorigin, raw-shape-only access, no fake clock mapping.
Actual PowerShell saved-only reproduction exits0 and re-evaluates all52saved
metadata records under unchanged criteria. No network or new data in replay.
QC.json,session_summary.csv,52session receipts,tests.log and gate_result.json
are independently inspectable in results. Never interpret tests as scientificPASS.

## Stop And Blocker

Stop before anyR2restart orR3. Required external capability:independent complete
recording-support metadata/native header/gap evidence and common-clock mapping
for the five unresolved sessions, including official99semantics where relevant.
The public pinnedNWBmetadata and inspected author code did not supply it.
Safely permitted acquisition, official source search, metadata inspection,
testing and saved-result validation were completed. Other in-file neural or
response reads cannot substitute for missing support and are forbidden.

No routine milestone approval is requested. Any distinct future recovery or
alternative cohort needs separate prospective authorization. See
ALTERNATIVE_COHORT_FEASIBILITY.md for two independent-site candidates and
mandatory admission checks. No author contact/data replacement was performed.
