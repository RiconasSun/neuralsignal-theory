# Execution Log

2026-10-12 UTC: prospective M0 registration completed before source access.
Codex wrapper invoked with registered mission JSON; no output after bounded
observation; interrupted with Ctrl-C (exit1). No files changed by wrapper.
CIM process inspection unavailable in sandbox. Scoped direct-tool execution
continues; wrapper policy was not modified or overridden.
Official docs/source inspected only after registration. SDK defaults hide units
using physiological metrics; this audit deliberately uses explicit identity-only
server projections instead. No default SDK session or unit loader is called.

Header descriptor request1 failed server projection validation (exit1); original
receipt preserved. Corrected RMA association syntax and removed download_link
from projected SQL fields (it is an API-derived URL, not a database column).
The file download endpoint is derived from official SDK documentation and ID.
No threshold, access boundary or original receipt was changed.

First NWB metadata decoder preserved four session attempts under metadata/headers.
Large stimulus timestamp arrays hit the single-read limit. Interrupted original
run, retained original receipts. Code1 reads numeric timestamp arrays in bounded
chunks under the unchanged total transport budget; applies to all58 sessions,
not a favorable subset. Corrected records use separate headers_code1 directory.
No spike/waveform/rate/quality datasets are decoded. HDF5 structural transport
may include opaque adjacent bytes; no zero-physiological-transport claim is made.

Premature first15-test invocation occurred before header collection finished:
14 passed, completeness test failed on three pending sessions. Test preserved;
after all58 completed, unchanged15 tests passed. No assertion was weakened.
Independent review identified three P1 protections, recorded in review history.
Corrected source performs capped streaming and projection rejection before
snapshot acceptance; validates hard HDF links and timestamp dataset types;
IBL replay checks fixture(eid,pid), duplicate units and lab/subject identities.
Actual original58 metadata paths receive a separate same-ETag link-only audit;
no dataset values decoded by that verification. Original header summaries and
original Allen/IBL INCONCLUSIVE gate files are preserved. IBL revised join
results use *_code1 files; no source release or cohort is replaced.
Local ignored dependency: pyarrow26.0.0 installed solely for column-projected
IBL anatomy read. Saved metadata replay does not require pyarrow or network.

Expanded26-test run:23 passed; three HDF5 fixture tests failed because sandbox
system Temp directory was not writable by HDF5. Fixture temporaries now live
under ignored writable paper12/replay, with unchanged values and assertions.
No scientific data or frozen threshold changed. Re-run required before closure.

Pre-review IBL source was mechanically reconstructed from documented bounded
patches and verified byte-for-byte against its prospective registration SHA256
c28341065ec899c1e8eaf24807b717305907f6d8e50a6d031f484b8af4cdc2f3.
It is archived for historical inspection only, not approved re-execution.
Source receipt licenses verified separately; Allen software commercial-use
restriction and IBL MIT notices retained verbatim, without relicensing.
