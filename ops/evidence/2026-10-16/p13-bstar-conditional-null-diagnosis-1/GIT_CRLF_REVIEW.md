# Independent scoped Git CRLF review

Mission: `P13-BSTAR-CONDITIONAL-NULL-DIAGNOSIS-1`.
Decision: **ACCEPTED_FOR_BYTE_PRESERVING_ARCHIVAL_WHITESPACE_CHECK_ONLY**.
Open P0: **0**. Open P1: **0**.

The per-command setting `core.whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol` is appropriate for this repository's existing `.gitattributes` policy `* -text`. It retains the three ordinary default whitespace checks and recognizes a carriage return immediately before a line feed as part of a CRLF line ending. It does not waive trailing spaces/tabs, extra blank lines at EOF, or spaces before tabs. Preserving CRLF bytes avoids invalidating the scientific SHA256 inventories; no scientific oracle or source bytes need change. This scoped interpretation is accepted, rather than converting immutable evidence to LF or disabling whitespace checking.

Read the preserved external `staged_diff_check_r1_CRLF.txt` and `crlf_oracle_note.json`. The failed default-check receipt identifies the expected preserved carriage returns. The closure helper uses the stated scoped command and still checks exact staged paths and index bytes. Its later execution and receipts are not certified prospectively.

Independent read-only verification checked all **51** current final-freeze hashes, all **54** currently untracked candidate files as additions using `git -c core.whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol diff --no-index --check -- /dev/null <path>`, and the tracked daily-operations diff with the same setting. There were no whitespace diagnostics. The daily file retains the exact BASE `c7ae3d4753f94ba50134d1f15a4a62dcb101d842` byte suffix, and the index was empty. For `--no-index`, exit 1 with no diagnostics records that compared files differ; an initial reviewer wrapper incorrectly treated that normal exit as a failed check. The corrected read-only wrapper accepted exits 0/1 only with empty stdout/stderr and passed; no file was changed by either check.

The accepted final r2 diagnostic review remains applicable. This note grants no replay, source access, fit, control, final C/D, scientific M6 PASS, or future-option activation. Actual exact-file commit, ordinary origin/test push, remote readback and clean-tree receipts remain pending. Only this new review file was written; no staging, numerical execution or source modification was performed.
