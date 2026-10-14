# Exact historical-draft staging authorization

Mission: P12-M4-DYNAMICS-NUMERICAL-RECOVERY-1-CLOSEOUT.
candidate_exit: WAIT_FOR_HUMAN_INPUT. Stage B NOT STARTED.
Blocked requirements: A-13 exact complete archive commit, A-14 remote readback, A-15 full working-tree clean, A-16 terminal Stage A gate.

Independent final archive review P0=0/P1=0 approves normal commit. Final saved-only PowerShell audit PASS,10 regressions, no numerical experiments; final manifest ce4b90fea345e901a0c810d9ff659dd5db68f92437379ce5066de9f45165db57; final receipt3e223659e2b607846277e0cc979f0e718b43501fc10e1da24c3cb5d22027d407. Original source/evidence byte preservation and61/59/2/155 counts verified.

Automatic approval rejected the full manifest-derived Git staging command because it also included three Stage B/preflight files, beyond the clearly authorized Stage A closeout staging scope, and required inspection/narrowing. The exact three files are:
- ops/evidence/2026-10-13/p12-m4-continuous-gradient-diag-1/goldenstandards.md
- ops/evidence/2026-10-13/p12-m4-continuous-gradient-diag-1/blocker.md
- ops/evidence/2026-10-13/p12-m4-continuous-gradient-diag-1/verdict.md

All three hashes match the original precloseout inventory; no B implementation, data read or numerical experiment exists. Safe narrowed staging was approved:405 individually inspected Stage A paths, no protected directories/path traversal, zero index-vs-candidate blob SHA mismatches. All code/docs whitespace checks passed with cr-at-eol to preserve Windows evidence bytes; raw immutable logs preserved. The three B drafts remain untracked and untouched.

Alternatives: deleting/ignoring them would not preserve evidence or prove genuine clean tree; silently moving them would invent a custody decision. Committing an archive that expects original inventory/source references to absent B drafts would not satisfy complete standalone archive verification. Therefore the unresolved exact scope/custody choice prevents the final commit/remote/clean gate. No commit/push was attempted;405 files remain safely staged.

Exact requested action: authorize including these three unchanged preflight drafts as historical evidence in the Stage A closeout commit; alternatively authorize byte-verified preservation outside the checkout and restoration at Stage B. The asynchronous question states these options and the automatic approval rejection. No approval is inferred from elapsed time.
Next action after decision: apply the exact authorized disposition, seal/replay final metadata, exact staging/normal commit/push/remote readback/clean proof; only then use the actual reviewed Stage A commit as B BASE. No invented or substituted SHA.
