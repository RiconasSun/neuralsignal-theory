# Independent frozen-byte formatting preservation review

Mission: P15-M6-INDEPENDENT-FINAL-VALIDATION. Reviewer: /root/pivot_review.

Decision: **ACCEPTED_EXACT_FROZEN_FORMAT_EXCEPTIONS**. Open P0: **0**. Open P1: **0**.

This is only a cosmetic-check exception for three exact immutable byte sequences. It does not exempt scientific checks, source identity, staging scope, archive verification, remote readback, or clean-tree verification. It does not authorize editing the frozen files or the failed execution log.

I independently ran the exact registered command from GIT_WHITESPACE_PRESERVATION_EXCEPTION_1.json:

`git -c core.whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol diff --cached --check`

It returned exit2 and exactly the saved diagnostics: failed native saved-reproduction log line19 trailing whitespace/blank EOF; reference_evaluation.py line153 blank EOF; sensitivities.py line35 blank EOF. The cr-at-eol setting recognizes native Windows CRLF and does not relax the scientific or source-byte identity oracle. An initial unconfigured read-only git check produced noisy CRLF diagnostics; the decision uses the exact configured command above, independently matched to its saved receipt.

The three exact exceptions are:

| Repository path | SHA256 |
|---|---|
| ops/evidence/2026-10-18/p15-m6-independent-final-validation/NATIVE_SAVED_REPRODUCTION_1.log | 2357f003bec704c0ce70f062e342ba5298f20b18cd02c5a47d54ee8e66bc2f26 |
| paper15_final1/reference_evaluation.py | cba7b00e962a74d9175d13a454f6e0e92c0d71b92b3028bc00ef5525e2824572 |
| paper15_final1/sensitivities.py | 256c27f8fa2df2a76294ad097b00d97517b2c7d3d62f1168f32b742a370ba191 |

For every exception I hashed both working-tree bytes and the actual staged Git blob; both equal the listed identity. Both Python file hashes equal their original prospective PRE_D_CANDIDATE entries. The failed native log equals its original typed FAILED receipt's log_sha256. All **546** pre-D inputs remain unchanged. These are preserved historical bytes, not changes to mathematics, tests, scientific criteria, data or outputs.

At review there were **877 exact staged paths and no deletions**. Running the identical configured whitespace command while excluding only the three named paths returned **exit0**, with no diagnostics, for the other **874 paths**. New review/closure files added after this snapshot must also pass that same nonexempt check before commit; this is not a blanket exemption for future changes.

The exception request receipt SHA256 is `5c4cf08e275a5063e36701d5da37175ace345731ab74d8e3fdf8296689e7e76c`. Scientific archive SHA256 remains `57a6350c7f7f8159b30b84c1b8f7466cb8aa9e55268222a416dfabacfadf92a5`, and the accepted scientific review/native attempt2 remain applicable to their unchanged surfaces. No source modification, raw-array access, model evaluation, scientific test rerun, commit or push was performed by this reviewer.

Preserving these exact bytes is preferable to rewriting a prospective source identity or an original failed log merely to remove blank lines. Normal H1 commit/push/remote changed-blob/clean verification and the later metadata-only review remain mandatory and are not pre-certified here. MERGE_ALLOWED=false; no main promotion or further scientific stage is approved.
