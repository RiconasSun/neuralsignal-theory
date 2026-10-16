# P14 metadata-only M0

Read `P14_M0_REPORT.md` first. The scientific result is INCONCLUSIVE_METADATA;18DynamicRouting metadata candidates are not18physiologically admitted animals. No neural activation is authorized. `PROPOSED_M1_FREEZE.md` is inactive.

From native WindowsPowerShell in repository root:

```powershell
& .\paper14_m0\reproduce.ps1
# Or provide a Python3.11 interpreter with pandas/numpy/requests:
& .\paper14_m0\reproduce.ps1 -Python 'C:\path\to\python.exe'
```

The recorded runtime uses Python3.11.15, pandas3.0.5, numpy2.4.6 and requests (exact version printed in receipt). No installation, internet, PyArrow, NWB package, neural arrays or fits are needed for reproduction. Budget about a minute; result hashes are byte-exact. Original inputs remain under the preexistingP13metadata paths listed in INPUT_FREEZE.json. `work/` is ignored temporary metadata scratch and regenerated saved-audit output only.

Do not execute retrieval modules for reproduction. `fetch_sources.py`, `range_metadata.py` and `decode_metadata.py` document the completed bounded source/column acquisition. Extraction required read-only PyArrow26.0.0 from the preexistingpaper12/deps runtime; saved-only reproduction does not import it. No providerSDK or automaticNWBfallback was used.

Source metadata is preserved byte-exact, including upstream whitespace and failed retrieval receipts. METADATA_FREEZE and CLOSEOUT_FREEZE verify identities; these hashes are ordinary reproducibility integrity, not a new cryptographic custody or release system. Git/remote/clean verification is certified separately by the external closure receipt after commit.
