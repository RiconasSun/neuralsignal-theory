# Official Source And Clock Audit Before NWB Observation

Author repository pinned commit1d95162d2672e71dd234a31e4b8d70017a289ee3;
full source URLs/content SHA receipts in results/sources/receipt.json.
Source files were read as text only, never executed; no data/example downloads.

Author export no2nwb.py lines45,176-190,270-300,407 uses microseconds/1e6 for
events,trial times and unit times. MATLAB exportNO2NWB_main.m lines168-188,
282-287 uses10^-6. Both establish shared exported scaling, not measured hardware
clock synchronization error or raw per-channel recording-start/end/dropout.
There is no start-marker subtraction in these event export expressions.
Do not assume TTL55timestamp0. Wall-clock session dates are deidentified/defaulted,
not evidence of native acquisitionzero or real experiment timing.

TTL55experimentstart,66experimentend,1stimulusonset are documented by author
export descriptions and setMarkerIDs.m lines2-22. No TTL99mapping was found in
the94selected author code/document files. Two literal99matches refer to a
session index comment and undefined brain area, not TTL; never reuse them as
event definitions. Unretrieved native hardware logs/manuals could add evidence;
absence here does not prove99has no meaning. Unknown99remainsunknown.

The dataset publication describes continuous acquisition and event alignment;
its acquisition section describes two annotation streams, not a per-channel
recording-duration mask. This supports documented55/66envelopes only under the
frozen policy; source text alone cannot rescue absent boundaries.
[Dataset descriptor](https://www.nature.com/articles/s41597-020-0415-9).

NWB timestamps use a common reference and seconds; starting_time/rate can
describe uniformly sampled data. This schema convention is not hardware
synchronization validation. Native NWB version/reference/units and descriptors
must be recorded separately; do not force the current schema onto old files.
[NWB specification](https://nwb-schema.readthedocs.io/en/stable/format.html).

Uniform observation policy:reuse only already frozen trial-onset lock/previous
endpoint receipts, inspect native descriptions/root/reference/acquisition
clock metadata and eventtimestamp endpoints. No new trial/response/experimentID
values, fullTTLlabels, signals, spike times/indices or final physiology. Search
all direct acquisition groups for declared raw ElectricalSeries metadata.
Missing raw streams/boundaries stay unknown; annotations are not raw recordings.
All52sessions retained. OriginalR2FAILimmutable even if new support is discovered.
