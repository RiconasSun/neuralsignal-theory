# P12 Curated-Release Exploratory V1

Separate authorized study; original M0 and native-support evidence immutable.
M1 registration freezes protocol,26mouse IDs,13/13groups,all15600trial IDs and
20664CA1/DG unit identities before any neural read.

## Entry Points
Registration (already executed, append-once):
`python paper12_curated_v1/register.py`

Verify allprior bytes and prospective locks:
`python paper12_curated_v1/register.py verify`

M2 online preflight (already executed; schema only, not spike QC):
`python paper12_curated_v1/access_audit.py --network-retry`
Only26frozen Allen objects,checked bounded Range requests and original ETags.
This is not permission to decode whole-session spikes.

Offline saved-evidence reproduction from repository root:
```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\paper12_curated_v1\reproduce.ps1
```
Requires Python3.11,numpy,h5py,requests. `-Python` may specify another runtime.
Replay verifies allprior/frozen hashes,regenerates the mouse table and stopped
gate from saved schema evidence,runs tests,and checks byteparity.
No network,neural reads,model fitting,null experiments or final evaluation.
It reproduces the stopped audit, NOT an unexecuted scientific study/manuscript.

## Read-Boundary Scope
Unit ragged vectors and their per-unit index boundaries do not identify spikes
belonging to arbitrary calibration trials. The official saved SDK exposes
whole-session `get_spike_times`,not a verified calibration-only query here.
HDF5 slicing works by element position; timestamp-to-position mapping has not
been established from permitted metadata. Binary searching neural timestamps
can itself read locked observations; read-all/filter is forbidden.

This is a strict-access-policy implementation blocker,not proof that the
dataset is unusable or that trustworthy preprocessing is impossible. A
separately authorized custodian could produce a trial-indexed derivative,
or an explicit prospective custody-policy amendment could define whether
automated decoding of mixed session arrays is allowed without analyst access.
Neither is silently authorized by this stopped package. No new cohort search.

## Provenance
Allregistration inputs are checkpoint files. Source NWB schema receipts record
URL,ETag,object bytes,each HTTP-range SHA256,UTC and read policy. Shape metadata
may describe mixed objects; opaque transport is not zero neural-byte transport.
No spike values,waveforms,analog/behavior outcomes or final scores decoded.
Provider licenses remain as in original frozen audit; not relicensed here.
