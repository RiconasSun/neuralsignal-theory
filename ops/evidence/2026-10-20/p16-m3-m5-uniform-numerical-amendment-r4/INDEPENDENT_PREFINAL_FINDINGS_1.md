# Independent pre-final draft findings 1

Mission: P16-M3-M5-UNIFORM-NUMERICAL-AMENDMENT-R4.
Reviewer: /root/r4_interruption_review. Scope: saved-only draft documentation and requirement trace; no scientific computation or source-array access.

Two pre-final P1 documentation/evidence findings were reported to the author and corrected before final review. This appended note preserves the findings; it does not replace the earlier interruption approval or certify the final archive.

1. R-236 BUG_COUNT, R-237 WARN_COUNT and R-240 FINAL_REVIEW were prematurely marked VERIFIED while FINAL_REPORT still contained null technical counts and PENDING_ACTUAL_REVIEW. They now read IMPLEMENTED_UNVERIFIED pending an actual independent final review. No requirement was removed or reduced.
2. The prior draft joined the 952 optimizer states and 216 B0 certificates under an ambiguous historical ftol=1e-12 provenance sentence. B0 certificates are analytic and have no optimizer ftol. The corrected report and generator explicitly limit that ftol provenance to the 952 optimizer states.

The prior draft bytes were not separately snapshotted at the instant these findings were made; no prior-draft hash is invented. The original reviewer messages and this append-only record preserve the identified wording/status issue. Current corrected byte hashes follow. Both findings are resolved in the inspected drafts. Final PS result, scientific requirement states, technical counts, final review binding and public-manifest review remain to be verified separately. Open P0/P1 findings for these two corrections: 0/0.

Current corrected draft SHA256:
* paper16_development_r4/FINAL_REPORT.md: c9b85dc294ae462169ee265e608d50173040c5a3ab93089049e6ff55f4f10b2a
* paper16_development_r4/FINAL_REPORT.json: 21e45e71c9ec449d6e074e0bc367da801e9e592a4091e6cfa39c258b99988c4d
* ops/evidence/2026-10-20/p16-m3-m5-uniform-numerical-amendment-r4/BUILD_CLOSEOUT_DOCUMENTS.py: 6056b1e46c36dc93e48d5dde47266082b091fcf926983bde5571613d7a8ee0ef
* ops/evidence/2026-10-20/p16-m3-m5-uniform-numerical-amendment-r4/REQUIREMENT_OUTCOMES.json: d00a1929492e6bd7b2fdccad363aa5c21bd3b06ddccda1cd3bf867ae3768fdfe
