# Independent precloseout helper review 1

Mission P15-M6-INDEPENDENT-FINAL-VALIDATION. Decision: **CHANGES_REQUIRED**. Open P0: **0**; open P1: **2**. This is a source-only/precloseout review while the sole D batch is running, not review of D results or final scientific acceptance.

## P1-1 — Git clean/scope proof can be closed without an actual clean gate

verify_git_readback records working_tree_clean_before_receipt but only requires it for ignored paper15_final1/work outputs. An H1 receipt written into tracked evidence can be generated despite an already dirty checkout. build_requirement_matrix subsequently verifies GIT_COMMIT/REMOTE_VERIFICATION using remote/blob booleans alone, ignoring the recorded false clean value. A synthetic injected-Git probe against the actual helper confirmed remote_readback_verified=true and changed_blob_hashes_verified=true are emitted with working_tree_clean_before_receipt=false and no exception. No actual Git/network command or receipt write occurred in that probe.

Require a clean checkout before either H1 or H2 receipt, retain the expected tracked-H1 receipt's own post-write dirty state truthfully, and require the appropriate literal clean proof before Git rows close. H2 final ignored/external receipt must establish its own actual post-receipt clean state. Use no-rename/raw scope accounting so an original historical path renamed into the mission namespace cannot evade deletion/scope detection. Normal origin/test and exact blob readback remain required; no force/main operation is introduced.

An H1 receipt inside H2 may certify only the actual historical H1 snapshot. It cannot retrospectively certify H2's own future push/readback/clean or the not-yet-issued literal terminal response. Record those pending obligations explicitly; the final live H2 receipt can remain ignored/external to avoid cyclic self-reference.

## P1-2 — Atomic row verification is inferred from evidence-file existence

The helper preserves311 IDs/text, but marks every non-Git requirement VERIFIED once D delivery is complete and its grouped paths exist. No semantic receipt/test/audit check distinguishes an executed successful final closeout review from an existing pending or rejected review.md. Specifically REQ-275, '- Independently reviewed closeout', can be marked VERIFIED without an actual accepted final review receipt, report hash, zero P0/P1 or archive identity. Actual saved-audit/native PowerShell reproduction freshness is similarly not consulted before report/archive closure claims.

Sharing supporting evidence across rows is legitimate; file existence alone is not completion proof. Retain every frozen ID/text and individually gate final-review/reproduction/Git/terminal obligations on the actual matching typed receipts/logs and current archive identity. Leave them OPEN until that proof exists. Untriggered conditional branches should explicitly name the condition and preserved/tested source path rather than imply an unexecuted scientific branch passed. Reporting actual negative/failed criteria under the authorized fallback remains valid completion of a reporting obligation; it is not a positive scientific PASS.

## Other reviewed boundaries

OWNER_REQUEST.txt SHA matches the frozen baseline source exactly. The311 owner requirements remain untouched. REPRODUCTION.md separates saved-result audit from real once-only executable evaluation and Git proof; A1-A10 map is a scientific handoff, not a manuscript/Prompt5 claim. assemble_final_report denies network/array loads and operates on saved results/arithmetic only, with the already reviewed no-fit/no-prediction audit surface. archive_package's closure metadata exclusions aim to avoid recursive hashes; the final review must still bind mutable closure files to actual Git blobs and preserve all prior failed attempts/reviews.

The synthetic journal archive and historical-preservation receipts are source/custody evidence, not actual D outcomes. Gate invocation1's import-root failure and identical-source runpy correction are preserved with no scientific rerun or gate bypass. No scientific source P file was edited by the reviewer.

Exact helper/document identities and the injected dirty-Git counterexample are in PRECLOSEOUT_STATIC_CHECKS_1.json. No current D output, D array, likelihood, predictor, fit, AD/FD or actual closeout/Git helper was executed. Preserve this unsuccessful review and helper snapshots, repair only the two closure-proof defects, then re-review. Actual completed-D/report/reproduction/final scientific review and H1/H2 transport remain future work.
