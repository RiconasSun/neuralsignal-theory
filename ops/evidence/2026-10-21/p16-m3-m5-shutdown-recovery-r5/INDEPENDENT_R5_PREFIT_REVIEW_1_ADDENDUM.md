# Prefit review 1 addendum — preseal historical identity anchors

Mission: P16-M3-M5-SHUTDOWN-RECOVERY-R5. Reviewer: /root/r4_interruption_review, 2026-10-21.

This append-only clarification belongs to existing P1-002 in PREFIT_REVIEW_1.md. It does not replace that unsuccessful review, invalidate the completed 3,992+216 saved-state qualification or authorize real fitting.

The archived candidate-3 controller, SHA256 522e6e472c6c49e7eb81d94fbc304aa797541fd2b0bdcd5f95c6d8fd6affb8b1, seals B0 folders by target count/iterdir without checking all original B0 file bytes against the independently qualified inventory. It also lacks an explicit historical RESULT-to-canonical-target hash join at M4 readiness, and its new-completion check compares the task sequence rather than joining each current RESULT byte hash to the corresponding original COMPLETED receipt.

Required correction before production approval: reject altered, missing or unregistered historical artifacts being admitted into the M4 package. The independent fresh protected readback provides the original per-file hashes for old optimizer folders, all B0 certificate files and saved A preparations. Check those anchors without recomputing a model or certificate. Verify historical optimizer RESULT paths/SHA against canonical prospective targets, and verify each newly produced RESULT path/SHA against its recorded R5 COMPLETED event. Preserve the original producer/attempt namespaces and all consumed attempts.

Synthetic negative fixtures should demonstrate rejection of changed B0 diagnostic/coordinate bytes, changed historical RESULT bytes and changed new RESULT bytes after a COMPLETED digest was recorded. No real certificate, gradient, objective, model, scientific threshold or fitting budget is changed by these hash-only checks. The Stage-B clock must include the checks as originally registered. M4 independent review remains mandatory even after readiness succeeds.

The original complete-M4 acceptance was already blocked; no false M4 PASS or new real A execution occurred. The revised candidate must preserve earlier sources/tests/freezes and receive fresh sufficient certification and independent exact-source review before Phase A approval.
