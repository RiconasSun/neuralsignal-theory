# P12 Real M2 Continuation

Separately registered mission P12-M2-REAL-RESUME-1, base 376ca01.
Original curated/custody/transport/checkpoint evidence remains immutable.

Saved public reproduction (no source requests, private QC or holdout access):

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File paper12_resume1/reproduce.ps1
```

This checks public evidence hashes, reconstructs the disposition table, runs
regressions, and executes the archived saved-only reproduce2.ps1. It does not
re-run real extraction, native security probes, or any unexecuted model/null test.
Final status and exact findings are in MILESTONE_STATUS.md and results/M2/gate_result.json.

Live paths are separately gated. preflight.py --seal registered the exact
implementation before live access. preflight.py verified opaque original artifacts
without decrypting them and ran one native synthetic checkpoint/isolation canary.
run_real.py is NOT a public reproduction shortcut or permission to release final data.
It requires trusted-host execution, the sealed code and current preflight proofs;
any recorded new critical failure stops further source access.

All raw byte ranges, response-body hashes, keys, ciphertexts and unit-level QC
are private custody evidence, excluded from Git. Public mouse-level admission QC
is not a scientific model-selection export. Isolation is against the native
zero-capability analysis process, not the trusted host/admin or ordinary tool sandbox.
