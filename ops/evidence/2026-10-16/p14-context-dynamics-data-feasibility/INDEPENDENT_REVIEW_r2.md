# Independent P14 M0 focused final review r2

Mission: `P14-CONTEXT-DYNAMICS-DATA-FEASIBILITY`.
Exact BASE: `fae4fa316bbb499a86949d496e6ba4f36380e29f`.
Candidate identity: `CANDIDATE_IDENTITY_r2.json`.
Candidate payload-freeze SHA256: **b48828547f99790c403a00d555d2bfed3d500c62b572f062412e98b4a2596752**.
Decision: **REJECTED — FRESH-CHECKOUT SAVED REPRODUCTION REPAIR REQUIRED**.
Open P0: **0**. Open P1: **1**.
Reviewer: separate internal reviewer; not external peer review.

## P1 — Reproduction assumes an ignored directory already exists

`paper14_m0/.gitignore` excludes `work/`. A clean checkout therefore does not inherit the acquisition workspace's scratch directory. Nevertheless, `test_metadata.py:158`,167 and175 call `tempfile.TemporaryDirectory(dir=P/'work')` without creating that parent. `reproduce.py:28` makes the same assumption for the complete saved audit, and neither the runner's earlier steps nor the PowerShell wrapper initializes the directory. The documented one-command saved reproduction fails on an otherwise correctly restored checkout until an undocumented manual directory creation is performed.

Independently confirmed using an isolated fresh ignored workspace root with **no child work directory**, patching only the test module's P to that root and running the unchanged `AccessBoundaryTests.test_reader_deny_bulk_and_invalid_seek`: **one FileNotFoundError**, before a source reader or network operation. This is a self-initialization/code defect, not a missing external environment capability. The existing26-test receipt demonstrates the acquired workspace, not this fresh-path case.

Initialize the ignored scratch parent before the runner needs it and make the relevant standalone tests self-contained. Add a regression beginning with an absent scratch directory, verifying automatic initialization and successful offline execution without manual setup, while preserving all existing assertions and source/metadata/eligibility rules. Preserve r2 candidate/review/receipts before repair; re-freeze and run the affected fresh-path case plus full saved reproduction afterward. No neural data, new retrieval or scientific criterion change is needed.

The first reviewer probe already confirmed FileNotFoundError but its diagnostic printing/cleanup then encountered sandbox-temp encoding/ACL errors. A second isolated probe under the permitted ignored workspace repeated the **same product failure** cleanly with exit0 in the reviewer harness. These wrapper diagnostics are separate from the missing-directory defect; no existing workspace directory was removed or renamed. The successful isolated confirmation root is `paper14_m0/work/reviewer_fresh_no_work_d03ec1cd36a648b3800210579840a09a`, with its missing child `work` deliberately uncreated.

## R1 repairs verified and preserved

Verified all103 current payload entries and the exact comparison to `REVIEWED_CANDIDATE_r1.zip` SHA256 **17d886306f57bb1d23bbe69b1009ec1e66a8dba9136c18f2ae5fc766f1c41417**. Exactly the seven declared payload paths changed; all other **96** original payload hashes remain identical. The original registrations, metadata43-file freeze,25 historical inputs, thresholds, anatomical targets, trial masks, DR/IBL eligibility and scientific decisions remain unchanged. All affected old hashes resolve to the preserved archive.

The prior P1 is **closed**: report line15 now correctly describes300 bins/context/half and600/context total, explicitly identifies the rejected report's false error attribution and preserves the already correct original registration bytes. No post-count trial/window threshold amendment occurred.

The new signed_contrast helper canonicalizes -0.0/+0.0 before string grouping while retaining NaN. The sole algorithm diff replaces the earlier signed-contrast expression with that helper; it is not used by admission. Independently ran `test_signed_zero_is_one_stimulus_level_and_missing_is_not_zero`: **PASS**,0.004s. It tests numeric sign normalization, actual category coalescing/counts and missingness. Existing25 tests are retained, and the only result-table changes are the two descriptive IBL overlap tables:9 numeric levels instead of10 string encodings. DR18/IBL8 and all eligibility masks are exact to r1.

The report/context assessment/inactive M1 proposal now explicitly distinguish frozen provider release/full-session curation from newly calculated A/C-only physiology and disclose that strict independence from scoring-period provider curation is not established. They do not claim the existing provider flags are C-only, resolve future access or admit a neural cohort. The original scientific/source assessment remains valid and bounded.

The final parent-run `REPRODUCTION_r3.txt` binds this103-entry candidate and reports26 tests/35 exact deterministic outputs/43 metadata/25 historical inputs with network denied. Intermediate code-only r2 and cp1252 helper interruption are transparently preserved and superseded. I did not repeat the full saved runner in this focused r2 review after confirming its absent-work precondition defect; the previous independent r1 full run and current targeted tests/probes are distinct evidence. E/verdict's current-identity pointer should name `CANDIDATE_IDENTITY_r2.json` (and the eventual repaired identity), leaving r1 identity historical.

## Scope, scientific limits and closure

All52 original requirements remain traceable; the49-verified/3-open pre-review matrix does not certify review/Git/handoff prospectively. The current scientific verdict remains **INCONCLUSIVE_METADATA**: DR18 is a metadata upper bound with exact licensing and per-session aligned movement/arousal still unresolved; IBL8, KI Context8 and Steinmetz10 retain their separate meanings. No pooling, false physiological admission, independent confirmation from exposed P13 results, outcome-driven threshold, expanded dataset search or neural recommendation is introduced by these corrections. M1–M7 remain inactive.

The three exact upstream README whitespace exceptions remain hash-bound to unchanged metadata/payload snapshots and are acceptable only with normal checks on every other mission file and full eventual index/remote byte checks. They supply no stage/commit/readback receipt.

No further P0/P1 source-scientific defect was identified in the seven-file repair. This new reproducibility P1 blocks candidate acceptance until narrow initialization/regression repair and fresh review. Only this new review, requested JSON and isolated ignored scratch probe were written. No product source, registration, metadata, raw/count array, old neural bundle, network, fit, predictive score, new candidate or M1 activation was changed/accessed/executed. Normal origin/test closure and final handoff/stop remain future actual gates.
