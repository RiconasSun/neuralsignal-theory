# Independent Windows raw-artifact whitespace gate equivalence review

Mission: P15-M7-FULL-MANUSCRIPT-AND-PUBLICATION-PACKAGE. Reviewer: /root/pivot_review.

Decision: **ACCEPTED_ARCHIVE_TOOLING_EQUIVALENCE**. Open P0: **0**. Open P1: **0**.

This accepts the narrowly command-local Windows Git tooling correction as semantically equivalent raw-artifact format checking. It does not change a scientific, publication, numerical or source-identity criterion, approve future changed bytes, or certify a future Git commit/push/clean gate.

## Demonstrated cause and exact correction

The existing root `.gitattributes` says `* -text`,intentionally preserving published file bytes. Many frozen Windows text artifacts have CRLF endings. The unconfigured Git whitespace checker reports their carriage returns as trailing whitespace. Separately,the installed system `diff.astextplain.textconv` and existing PDF diff-driver attributes expose converted PDF text,or force raw binary PDF streams to be treated as textual diffs. Those diagnostics are not evidence of a malformed document or source whitespace defect. No frozen file was rewritten to accommodate them.

The accepted command prefix and flags are exactly:

`git -c core.whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol -c diff.astextplain.binary=true diff --no-textconv --cached --check`

The first setting recognizes CRLF while retaining real line-end/EOF/indentation checks. The second makes the already-selected PDF driver binary for this invocation;the third prevents arbitrary installed text conversion. No persistent configuration,global attributes or source/artifact bytes are changed. PDF text,glyph,bounds,numeral,page-count,visual and document-consistency QA remain mandatory and separately hash-bound. A binary-format gate does not replace those PDF content checks.

## Independent fixture and actual-scope checks

I created a separate ignored temporary Git repository under `paper15_manuscript/work/independent_git_whitespace_review_1`,with the same `* -text` preservation rule. I independently ran the exact staged-check command on **12 fixtures**:

- Clean LF and CRLF,both exit0.
- Internal blank lines in LF and CRLF,both exit0.
- Actual trailing spaces,trailing tabs,space-before-tab indentation,and extra blank EOF lines,in each LF and CRLF encoding:all eight exit2.

Thus CRLF awareness does not excuse actual spaces/tabs before CR or lose the original EOF/indentation checks. These are synthetic Git/document-format probes,not scientific tests or production Git mutation. Full probe identities/results are in GIT_WHITESPACE_EQUIVALENCE_PROBES_1.json,SHA256`3a4fe2f05018523be4c07a7f614b5747f1777a2a4b634a63435cb3d50647c2fb`. The producer's six-fixture evidence plus its additional CRLF-trailing-tab fixture cover seven cases. I independently reran the additional command and verified an actual trailing-whitespace diagnostic and exit3(whitespace error bit2 plus no-index difference bit1). Its first probe incorrectly expected2;the TEST_BUG receipt is retained,and the corrected receipt preserves the same required bad input/rejection. These no-index statuses are not confused with my staged-check0/2 oracle.

I independently queried `git check-attr -z --stdin diff` for the actual **243 staged paths**. Exactly **18** had the astextplain driver;all18 were current/historical main,supplement or figure PDFs. No code,Markdown,test,JSON,CSV or other text path was assigned that driver. I checked each raw `%PDF-` header,its actual SHA256,and successful PdfReader page count:main19/supplement36/figure1 for each current and preserved rejected candidate. The driver correction is therefore confined to demonstrated binary artifacts,not a code/document waiver. GIT_DIFF_DRIVER_SCOPE_1.json agrees with this actual scope.

I verified all **15** exact SHA/line-bound SVG/raw-log exemptions remain unchanged. I independently parsed the actual final raw check output as byte-level ASCII diagnostic headers,without trying to decode arbitrary PDF context as UTF8. All **1,745** remaining diagnostics map to the already-approved exact15path/line exceptions. I then independently ran the corrected command excluding only those15paths:the other **228 staged paths** passed with **exit0 and no output**. Newly staged metadata/review files must pass the same gate before actual commit;this snapshot does not certify files not yet staged.

## Failure and source preservation

I verified the paths,byte lengths and SHA256s of both failed raw diagnostics and the final raw output:

- work/GIT_DIFF_CHECK_FULL_1.log:10,780,026bytes,SHA256`1a75118402bda75e6c1daa4b634bd366c0f165818652b742c39ae7327920b603`.
- work/GIT_DIFF_CHECK_RAW_CRLF_2.log:399,050bytes,SHA256`60631b559399570526524d5d93341973e8255e5b358f6335242d7f32c9f7e865`.
- work/GIT_DIFF_CHECK_BINARY_CRLF_3.log:284,707bytes,SHA256`888f5558be9fb8fdf3456f79b2e15981f1c409a74a49ce3a0e1e813bab7ebf57`.

The original raw logs remain under ignored `paper15_manuscript/work/`. Their entire bytes are also preserved remotely in three tracked deterministic mtime0 gzip archives under git_tooling_raw_diagnostics. I independently checked each compressed/original hash and size,gzip header mtime,and byte-for-byte lossless decompression. GIT_TOOLING_DIAGNOSTIC_ARCHIVE_1.json binds both forms. No diagnostic context is omitted or text-normalized;the archives require no additional whitespace exemption. The first UTF8 parser failure and second forced-text PDF failure are preserved as failures,not called passed executions. Strict ASCII header parsing avoids corrupting/decoding binary context. No whitespace stripping,CRLF conversion,PDF rewriting or historical-log editing was used as a repair.

I reverified the unchanged publication candidate SHA256`c98ee27cd207a556ac087fb220f05b81392ae2dbe01f4629d0c5682eb3bc94f7` and all **3,099** original source hashes. The two accepted scientific/document review2 decisions and actual native4 PDF identities remain valid on their unchanged surfaces. Scientific Final remains **DESCRIPTIVE ONLY**;this tooling check cannot upgrade it or alter any result,model,test,threshold,cohort or source.

## Bounded acceptance and remaining gates

The earlier review2 reference to a default whitespace check is satisfied by this now-demonstrated equivalent raw-artifact command under the actual Windows byte-preserving environment. This is an explicit reviewed tooling interpretation,not silent assertion removal or test shrink. Reject genuine nonexempt whitespace and changed exception bytes exactly as before. Recheck the actual staged driver set if staging changes;only valid PDF artifacts may be treated as binary. Keep the independent PDF/document QA and current candidate hashes mandatory.

Normal exact-file origin/test archival may proceed after the final complete staged set passes these same flags and scope checks. Commit,push,remote current SHA/every changed blob readback,clean gate and literal final STOP remain actual future requirements. MERGE_ALLOWED=false;no main promotion,external submission or further scientific execution is approved. No production Git mutation,scientific source edit,neural read,fit,prediction,new hypothesis test or D reassessment was performed by this reviewer.
