# Independent archive transport review 1 — not accepted

Mission: P16-M3-M5-FROZEN-DEVELOPMENT-R1
Reviewer: /root/r4_policy_review
Timestamp UTC: 2026-10-20T02:05:00.948815+00:00
Decision: NOT_ACCEPTED_ARCHIVE_TRANSPORT_GUARD
archive_open_P0: 0
archive_open_P1: 1
Scientific S07/N4 findings:2, unchanged and not addressed by this archive-only review.

## P1-01: unreviewed/raw files can enter the exact-path stage list

In the inspected ignored helper, prepare():34-40 enumerates every untracked file under the new P/E namespaces, adds daily, checks namespace prefixes and excludes only /work/ and __pycache__. It validates the frozen53 entries but does not require each selected path to belong to that manifest or an explicitly reviewed/hash-bound closure set, and it does not reject raw-array/source extensions.

Consequently an additional unreviewed paper16_development_r1/extra.npy or evidence/extra.nwb satisfies these path predicates and is copied into stage_paths.nul and STAGING_CANDIDATE. Later index/readback checks only prove those selected bytes were committed; they do not establish independent review or authorized public redistribution. This violates the owner requirement to commit only authorized evidence and no raw neural arrays/private caches. The issue is independent of the truthful53-payload scientific STOP package, whose saved checks passed; it concerns the consequential archive preparation path. No unsafe Git operation or source/raw-file injection was executed to demonstrate it; the counterexample follows directly from the predicates.

Required smallest repair: construct/verify the exact path set from the frozen manifest plus a fixed explicit list of legitimate closure artifacts, hash-bind every reviewed closure file, reject all other untracked P/E paths and raw-array/source extensions before preparing the NUL list. Preserve the old helper and this failed review, run focused synthetic guard regressions (including an extra unreviewed path and raw extension), and obtain a fresh independent helper review before staging. No scientific contract,53 payload, model/threshold or data access amendment is required. A separately evidenced manual exact-reviewed-file path could also meet the same contract; namespace-wide enumeration alone cannot.

No new neural/source access, fits, B/E/Final evaluation, helper execution or Git mutation was performed. This report authorizes no staging and makes no science PASS claim.

| Inspected file | Bytes | SHA256 |
|---|---:|---|
| paper16_development_r1/work/git_archive.py | 5867 | 888929f69521cb3be67506aeb6f8fab657f321be114daaa645b4cdf71fc86d5a |
