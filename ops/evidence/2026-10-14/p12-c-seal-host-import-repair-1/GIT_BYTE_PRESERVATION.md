# Git byte-preservation closure note

The repository root .gitattributes specifies `* -text` to preserve published SHA256 bytes. New Windows-generated evidence uses CRLF, and the original failed synthetic run1/run2 logs retain blank terminal lines. A default staged whitespace check reported those bytes; the CRLF-aware diagnostic reduced findings to those two immutable raw logs. No published/frozen source, raw log, snapshot, calibration or model bytes were normalized or rewritten.

Scoped attributes in this new evidence directory recognize CRLF while retaining the original blank-at-eol/blank-at-eof/space-before-tab checks on text. Raw `.log` receipts and `.bin` byte snapshots are binary Git artifacts, preserving their exact bytes and hashes. New package attributes recognize CRLF only for its README markdown. There is no root/global Git configuration change, numerical/test-oracle change, or exclusion of executable source checks. Archived raw failure logs remain covered by SHA256 integrity and review evidence.

The initial staging diagnostic is retained in the authorized external Git receipt directory. The complete exact-file staged diff check is rerun after these presentation-only metadata additions. Independent review addenda bind this choice; the14-file host snapshot and all saved-state hashes remain unchanged.
