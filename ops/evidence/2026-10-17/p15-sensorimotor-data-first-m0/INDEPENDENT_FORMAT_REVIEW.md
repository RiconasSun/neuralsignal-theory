# P15 M0 independent byte-preserving format review

Mission: P15-SENSORIMOTOR-DATA-FIRST-M0.

Decision: **ACCEPTED_SCOPED_ARCHIVE_FORMAT_FIX**. Actionable P0: **0**. Actionable P1: **0**. Prior scientific/engineering/closure reviews remain intact. Actual commit/push, remote readback and clean gates remain pending.

The reviewer inspected the two new mission-local .gitattributes and ARCHIVE_FORMAT_CHECK.md. Root `* -text` remains unchanged. Both new scopes only enable `cr-at-eol`, accepting original Windows CRLF without normalizing published/source/evidence bytes. The sole `-blank-at-eol` exception is `paper15_m0/source/*.html`, limited to the five original official documentation snapshots. No Python, PowerShell, test or other authored implementation path receives that exception. Historical paths outside the new mission directories have no new whitespace attribute.

Independent `git check-attr whitespace text` confirms ordinary paper15_m0/pilot.py, reproduce.ps1 and test_m0.py have `whitespace=cr-at-eol` and `text` unset; source/license.html alone additionally has `-blank-at-eol`. A historical paper14_native1/audit.py remains unaffected. A read-only stdin Git format canary with the same CR-at-EOL rule accepted ordinary CRLF without a whitespace diagnostic, while a real space before CRLF still produced `trailing whitespace`. The canary changed no files, index, persistent config or scientific oracle. Plain `git diff --cached --check` currently exits0 under the scoped working-tree attributes. The final exact staging must include these attributes and this review and repeat that check before commit; this review does not pre-certify that future staged state.

All16 principal scientific/program/result hashes recorded in INDEPENDENT_REVIEW_1.md remain unchanged. All five official HTML hashes still match their original acquisition-ledger hashes. Source bytes were preserved rather than edited to satisfy a style checker. No model, scientific cutoff, count, proof assertion, test behavior, source identity, pilot/allocation boundary or final-access rule changed. Accepting upstream HTML whitespace is a narrowly classified immutable-source style exception, not a reduced scientific or implementation test.

Reviewed new surface SHA256:

| Surface | SHA256 |
|---|---|
| paper15_m0/.gitattributes | 468484911d75ba8b8839fca074335fbbe2863647c5818723cd01b47aa6273671 |
| mission evidence .gitattributes | 1b620b54d24219e9cba1c91246cfceb73b9647328e00028a0b41776f3d805dd3 |
| ARCHIVE_FORMAT_CHECK.md | 501b2bcd26d46385e2efc488769a4e4217349c82488b1fd8c6bcd70bdc2e4b73 |

No numerical/pilot experiment or redundant scientific reproduction was rerun. Only exact normal origin/test archive, executed remote SHA/all changed-blob verification and clean gate remain authorized. No main promotion, PR, model fitting, final neural access or M1-M7 continuation is granted. Stop after the verified M0 handoff.
