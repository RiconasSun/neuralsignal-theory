# Independent Allen Support Audit

Original M0 remains INCONCLUSIVE. Scientific recommendation is a separately
registered curated-release exploratory design, not original admission or M1.
See REPORT.md, RECOMMENDED_PROTOCOL.md, CLAIM_AUDIT.md and results/gate_result.json.

From the repository root, replay compact saved metadata, all clock fits and tests:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\paper12_native_support1\reproduce.ps1
```

Full frozen digital timing reconstruction, independently captured and verified:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\paper12_native_support1\reproduce.ps1 -FullDigitalTiming
```

Python3.11,requests,numpy,h5py,scipy required; use-Python to override runtime.
No persistent execution-policy change. Neither mode fits neural models, accesses
spikes/analogs/behavior outcomes, downloads data or runs M1-M7.

Default mode regenerates tables/metadata gate and every barcode affine diagnostic
from saved permitted edges. Full mode additionally reconstructs master digital
barcodes, physical visual frames and official endpoint oracles from the already
hash-verified sync cache. It requires ignored sync_cache payloads acquired during
this mission (~1.2GB), not distributed in the Git evidence package. Missing cache
fails closed without network. Metadata/default reproduction does not pretend to
reproduce unexecuted experiments or replace missing native packet certificates.

For a fresh checkout, full timing inputs can be reacquired only from the exact
frozen raw-object URLs/ETags/checksums in metadata/digital/*.json and the original
paper12/metadata/allen_raw_inventory.json, under the registered digital-only policy.
No substitution of a newer object is permitted. Obtain separate authorization
before new acquisition after this stopped audit; no automatic rescue is active.
Verbatim metadata/source receipts, lossless compressed headers/anatomy, original
smoke failures and corrected diagnostics are retained. Native cache originals
verify every compressed metadata body; no originalP1-P11/P12 bytes changed.
