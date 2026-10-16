# Independent internal review

Mission: `P13-KI-PFC-METADATA-FEASIBILITY-1`.
Reviewed UTC: 2026-10-16T05:16:44Z.
Reviewer: separate local reviewer agent, frozen implementation; **internal review, not external peer review**.
Decision: **REQUEST_CHANGES**. P0 findings: 0. P1 findings: 3.

## Evidence and independence

Read the complete `USER_MISSION.txt`, frozen 100-item `baseline.json`, `goldenstandards.md`, registration, report, design proposal, summary, acquisition/header/range/interval access implementation, audit, synthetic tests, saved-only verifier and separate openpyxl checker. Inspected `saved_reproduction_v1.log`: 20 tests pass, five deterministic audit outputs are byte-identical, 181 saved hashes pass, and the independent checker covers 308 task/region/tier denominators. Independently rehashed all 181 saved inventory entries during this review; all matched. Independently inspected saved header value paths and recomputed task and relevant animal unions from saved metadata only. No original NWB/ZIP was opened, no network request was made, and no neural dataset values or model scores were read. Review writes only this new review file.

Reviewed working candidate: branch `test`, HEAD `54f4bb572c33b11937b1939b4e643fda5269f58c`; package and mission evidence were untracked at review time. This review does **not** certify a future commit, push, remote manifest/readback or clean-tree gate.

Relevant reviewed SHA256 identities:

| File | SHA256 |
|---|---|
| `paper13_ki_feasibility1/REPORT.md` | `c102d55c132550b63feee8de6daaf9f481cee7faddc07596996e1a785eba6305` |
| `paper13_ki_feasibility1/REGISTRATION.json` | `c066234dcc3edb98eac55212055b3af451fdf63c6f99f5d93b89215261a116a1` |
| `paper13_ki_feasibility1/SUMMARY.json` | `9855de00232b9658a084dde384a3ae9e4dc78ebb61cedce5e4a8b174bb1dab86` |
| `paper13_ki_feasibility1/audit.py` | `e95e9a979cfc392fc466ba0e1aa6924d7ae81f92b7e191d488d447c76db0d851` |
| `paper13_ki_feasibility1/headers.py` | `b89e9822eea9609114dd8fdd960ec7ffac2dc0f4b6c8be7af2cf99c8b4d8ba8a` |
| `paper13_ki_feasibility1/saved_inventory.json` | `c549bac1efa5a6f561abcd75002794766df3b304475b596dde8ee83f14b57a9b` |

## P1 findings

### P1 — Keep the Passive insufficiency result at its actual scope

Evidence: `paper13_ki_feasibility1/audit.py:186-193`, `SUMMARY.json:4-6`, `REPORT.md:25`, `REPORT.md:60`; authorization `USER_MISSION.txt:38` and `USER_MISSION.txt:46`; registration `REGISTRATION.json:57`, `REGISTRATION.json:64`, `REGISTRATION.json:71`.

The authorization specifies primary **pre-tone activity** and prohibits combining passive auditory and aversive-conditioning observations. It does not select Passive as the only primary route or ban every possible combination of nonaversive experimental contexts. The audit hard-codes `primary_task='Passive'` for 001260 and promotes that stratum's maximum to the candidate `scientific_verdict`; `SUMMARY.json` then exports the bare release-level `001260: DATA_INSUFFICIENT`. The report correctly qualifies its prose as the single-task Passive route and retains all other strata, but calling it a "registered single-task Passive route" overstates the registration: no explicit primary-Passive selector exists there, and its broader task-settings restriction was analyst-authored rather than a user-selected scientific boundary.

Passive's 10-mouse insufficiency is valid, as is the finding that every individual primary task stratum is below 16. Neither proves the entire authorized primary pre-tone candidate has a mouse upper bound below 16. As a scope diagnostic only, the saved metadata contain 20 distinct nonaversive primary animals with at least eight raw PL units on one probe, and 18 for ACAd, before epoch/QC restrictions. These are **not** admitted cohorts or permission to pool tasks; they demonstrate why a per-stratum ceiling cannot establish a release-level impossibility. Essential quality and event/exclusion uncertainty still supports an inconclusive primary assessment.

Required correction: preserve the explicit `Passive: DATA_INSUFFICIENT` route result, all task rows and historical attempt evidence, but distinguish it from the broader primary candidate assessment in machine-readable and human-facing outputs. Treat unapproved multi-context possibilities as unassessed/`INCONCLUSIVE_METADATA`, not feasible and not disproved. Do not combine observations, lower the proposed minimum or change the scientific estimand during this correction. Any later multi-context design needs its own explicit product/scientific decision and authorization. If machine-readable outputs change, update inventory/fresh saved reproduction and re-review the final candidate.

### P1 — Do not claim Git closure before the evidence exists

Evidence: `paper13_ki_feasibility1/REPORT.md:72`, `README.md:15`, frozen `baseline.json` requirements REQ-091 through REQ-094, and the review-time Git state above.

The report says "Saved-only reproduction, independent internal review, scoped Git commit and remote readback are documented in the mission evidence." At review time the scoped commit, push and remote readback have not occurred; HEAD is still the declared base and both new directories are untracked. The README similarly refers to actual Git closure and an external Git receipt as retained. These statements certify pending evidence prospectively and would be false if the candidate were archived at this point.

Required correction: mark commit/push/readback/clean closure as pending until actual receipts exist; then record real commit/remote identities and the final clean gate through the authorized closure process. A review cannot pre-certify those later actions. Final documentation must refer to actual evidence or explicitly retain a pending state.

### P1 — Add a saved-only regression for the observed lowercase-header failure

Evidence: `documentation_transport_repair.json` root-causes/fix, `failure_journal.md` item 4, `interval_archive_attempt2.log:20`, `paper13_ki_feasibility1/transport.py:47`, `transport.py:102`, `test_headers.py:43-67`; user execution directive section 10 requires regression coverage for every discovered mission bug before PASS unless impossibility is documented.

The real second interval-archive attempt failed because a lowercase `content-range` header became an ordinary case-sensitive dictionary, while `RangeReader` accesses `Content-Range`. The repaired `Transport.request` returns a `CaseInsensitiveDict`, and the real third acquisition succeeded, so this is not a claim that the current fix is broken. However, the current range tests bypass `Transport.request` entirely with fake transports returning title-cased keys; the ZIP tests cover the bounded-tail and missing-ETag exception but do not exercise header normalization. Removing the `CaseInsensitiveDict` repair would leave all 20 current tests passing while restoring the observed bug. Saved byte-identical audit replay also does not call transport, so it cannot provide this regression.

Required correction: add a narrow offline test that exercises the actual `Transport.request` result for lowercase response-header keys, then the exact range/identity checks, using an in-memory fake response and isolated temporary journal. It must fail without the repair and pass with it, while preserving the NWB ETag requirement and documented Zenodo exception. No new external request or original data acquisition is needed. Refresh the source inventory and saved-only reproduction after this test-only change.

## Scientific and access assessment

The bounded audit substrate is substantial and reproducible: exact specified DANDI releases, public source revision/license and manifest evidence; 99 metadata-only headers; 74/25 files, 41/25 canonical animals, 50/25 sessions and 20,374/9,408 units; suffix-alias reconciliation; no identified cross-release identity overlap; unit anatomy through electrode row lookup; all 11 labeled regions and all task/tier strata; and no physiological quality admission. Saved headers contain no ragged electrode-index arrays requiring a different live mapping path, and the independent direct-electrode check supports the reported saved denominators.

Epoch and exclusion language generally respects evidence limits: basic windows are upper bounds, supplied active intervals are matched rather than assumed absent, unknown saturation completeness is retained (42 complete and 57 incomplete flags), noise events are not silently called pure tones, Attention's unrecognized tone-series semantics are not used to admit mice, and historical source-version/QC limitations remain explicit. No true good-unit flag or reliable ratio interpretation is invented. The ZIP inspection is selective interval metadata, not a full 1.9 GB neural download; full-object integrity is not falsely claimed. The two unresolved historical creator hashes, `ignore` cases, manual eligibility and training-only QC concerns remain unresolved rather than passed.

The secondary aversive assessment is appropriately separate and inconclusive: 20 raw PL animals do not establish an eligible cohort, and 15 passing the proposed 120 matched-epoch count does not establish universal biological impossibility. The conditional proposal retains strong rate/history/context baselines, causal forward scoring, small model families, mouse-level evaluation and one-final-evaluation safeguards without asserting numerical success, power, causal/choice mechanisms or execution authority.

The `design_proposal.md:21` PG recommendation is evaluated here only as a future proposal under the document's explicit no-execution boundary; this review does not establish an existing frozen P13 numerical threshold. The word "unchanged" does not supply a source for any such earlier P13 rule.

**Archive completion assessment:** the collected metadata and saved audit are adequate for an honest bounded inconclusive archive, but the current final package is **not yet review-complete** because of the three P1 scope/evidence/regression defects above and pending actual Git closure. This does not call for additional dataset search, spike access or model fitting. Resolve the claims at their existing scope, add the offline regression and perform the separately required fresh closure checks.

**Scientific execution remains blocked:** no cohort is admitted; no roster/split/model is authorized. Resolve eligible-unit quality semantics and source-linked exclusion/mask provenance, and obtain a separately reviewed and explicitly authorized scientific protocol before neural access, M1-M7 or final evaluation. `INCONCLUSIVE_METADATA` is a scientific decision, not a claim that the broad P13 question failed or that the earlier IBL failure was repaired.
