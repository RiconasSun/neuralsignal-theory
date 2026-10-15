# Preserved review Markdown line breaks

The first exact staged diff check identified four two-space Markdown hard line breaks: lines 3 and 4 in `engineering_final_review.md` and `engineering_preexecution_review_r4.md`. These are intentional Markdown formatting, not runtime code or accidental altered evidence. The latter review is a preserved historical source artifact; both files are hash-bound by other evidence.

Their original bytes and hashes remain unchanged. The local evidence `.gitattributes` exempts blank-at-eol checking only for these two exact Markdown filenames, while retaining blank-at-eof, space-before-tab and CRLF checks. Every other file retains the original whitespace checks. No scientific, security, numerical, scalar QA or acceptance assertion changed. A fresh staged diff check is required after this documentation-only adjustment.
