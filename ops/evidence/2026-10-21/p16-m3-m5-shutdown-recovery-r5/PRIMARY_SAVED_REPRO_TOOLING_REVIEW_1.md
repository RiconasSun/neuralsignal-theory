# R5 saved-only reproduction tooling: preparatory static review

Reviewer: `/root/r5_primary_audit`. Scope: new deliverable tooling only.
No reproduction run, model import/call, AD/gradient/score call, raw array access,
running-journal modification, M4 decision or scientific PASS was performed.

Reviewed Python SHA256:
`805cb0fee9a22ae4e6d3351c530d7c8797b2fce5ffa3a6b30fdb14f456602402`.
Reviewed PowerShell SHA256:
`6780eafb5d481cad69bf0736332ad6329dd16f032b50ae4c69007ab2f284c5ca`.

Compared producer source schemas and metadata from the first three completed
R5 tasks (mouse 763236014/S02/S, seeds 11/23/37). Their RESULT, ATTEMPT and
DIAGNOSTICS metadata contain the expected fields and same-folder receipts.
Only JSON metadata was inspected; no NPZ was loaded. The actual Stage B
monotonic span is 172800.0 seconds. This is schema evidence, not a numerical
reproduction or acceptance of those states.

## P1 findings required before final saved-only reproduction

1. **Approval and complete M4 bindings are not verified** (Python lines 71–74).
   Existence of M4_APPROVAL.json suffices, even if it rejects another manifest.
   The reproducer does not verify decision/open-P0/P1/review hash/manifest hash,
   full 6471 disjoint task origins, all 3992+216 admitted historical states,
   complete selected D/S seed groups, or original tie rule. Add saved identity
   and scalar-only checks using the actual frozen approval/manifest schemas.

2. **Journal and vector coverage is too weak** (lines 21–40, 47–63). Counts
   alone admit reordered/nonalternating FG entries and malformed diagnostic
   reservations. ATTEMPT task/parameter binding, result x/jac/objective binding,
   accepted-vector order and halfway/endpoint association, fixed-FD policy flag,
   strict serial task/terminal/failure handling and complete per-fit 24P/3/3
   derivative reservation sequences are missing. Add origin-aware checks;
   original R3 scalar FG journals must never be required to contain R4/R5's
   newer full-vector fields. Preserve legitimate partial reservation prefixes.

3. **Archive coverage and path boundaries are not enforced** (lines 15–18,
   43–45). An arbitrary list, including an empty list, can be the archive.
   Receipt paths are followed before requiring the exact expected state folder;
   absolute/traversal/UNC paths are not rejected. On Windows, OS filesystem UNC
   access is not prevented by patching Python sockets. Bind a complete final
   local inventory and separate public manifest; validate canonical local
   repository-relative paths, same-folder member names, exact inventory coverage
   and an explicit narrowly enumerated exclusion policy before any NPZ read.

4. **Stopped/native/access assertions are not grounded** (lines 66–79).
   Stage presence is optional; a stop's arbitrary scientific_status is echoed
   without typed no-retry/terminal/partial accounting. Boot/stage-supervisor hash
   and actual native process/Job outcome are unchecked. E/Final FALSE is printed
   from directory absence rather than complete saved boundary evidence. Verify
   the frozen prefit, admission, stage, supervisor/native, closure and allowed
   A-preparation bindings; distinguish boundary evidence from an unsupported
   universal claim. An active or unsealed archive must remain nonterminal.

The PowerShell wrapper's repository anchoring, explicit runtime, `-B`, exit-code
handling and finally/Pop-Location are sound. It should additionally verify the
intended interpreter/tool paths and forward a strictly validated local manifest.

## Recommendation

Preserve these versions and this review, amend only the new nonproducer
deliverable tooling, and test strict parsers with temporary synthetic saved
JSON/NPZ fixtures. Do not run full real-state reproduction until a terminal,
closed archive exists. Independent review of the amended tooling remains
required. These findings do not authorize changes to the running producer,
scientific standards, task plan, historical evidence or Phase B execution.
