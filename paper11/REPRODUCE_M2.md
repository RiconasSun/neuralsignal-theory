# M2 Training Feature Reproduction

Run from the repository root after acquiring M1's real pinned data:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File paper11/scripts/reproduce-m2.ps1
```

Requires Python 3.11, h5py 3.16.0 for local NIX metadata inspection, and
matplotlib 3.11.1 for descriptive QC figures. Current runtime versions verified.
Acquire pinned NEMAR NIX objects with the `-AcquireNix` switch. The documented
public annex remote is used; 23 files total 11,387,335,686 bytes, stored ignored
under `paper11/raw/NIX/`. Original/masked SHA256 identities remain separate.
Pinned publisher provenance attests administrative timestamp masking only, with
no data-array changes. Pointer/provenance/filename bindings are checked offline.
Pinned conversion source is preserved in
data_manifest/M2/source_audit with Git-blob verification. M0/M1 gates and hashes
are checked without rewriting them. Extracts training only; validation/test rows
are skipped before unit/timestamp decoding. No model or parameter tuning occurs.
Three stages execute in order: one session, two subjects, full eligible cohort.
Counts retain zeros conditional on the published complete trial-array coverage;
the derivative does not provide per-bin acquisition dropout masks. Session-local
units and upstream SU/MU/sorting limitations remain explicit. A data-integrity or
test failure stops the gate. Missing exact unit/trial coverage inventories cause
scientific gate FAIL and execution NEED_ENV, despite passing count-extraction
tests. Array cardinality alone is not accepted as exact observation provenance.
NIX audit reads names/units/schema only, never timestamp values or array lengths.
Fixture data are automated tests only. Three upstream GIN endpoints returned
HTTP 403; public annex resolution subsequently restored the coverage sources.
Earlier failure artifacts are retained in results/M2/attempts. The command
regenerates descriptive PNG/PDF training QC with input provenance.

Predictor metadata gates set size until encoding, excludes probe/response fields,
and resets history at each trial. Epoch timing is task-schedule conditioned, not
unconstrained online prediction. No heldout timestamp is parsed for feasibility.
100ms remains the frozen primary width; convergence can only be assessed in M4.
