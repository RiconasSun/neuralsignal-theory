# Closure tooling review-1 repair candidate

Mission: `P16-M3-M5-SHUTDOWN-RECOVERY-R5`.
Scope is new closure tooling and temporary synthetic tests only. The running
producer, frozen sources, scientific policies, real saved-state audits and
active journals were not changed or rerun. No actual local archive or full
real reproduction was executed. The real archive manifest remains absent.

## Preserved unsuccessful candidate

The independent three-P1 review is retained as
`INDEPENDENT_SAVED_TOOLING_REVIEW_1.md`. Exact prior candidates are retained as
`reproduce_saved_review1_snapshot.py` and `build_archive_review1_snapshot.py`;
the prior 46-test source is `test_reproduce_tooling_review1_snapshot.py`.
All previous test receipts/native attempts and earlier versions remain intact.

## Exact amended sources

- `reproduce_saved.py`:
  `f0a6c0c9ce29ee448f8c302f3c8aeac6a3a5fa819c4880d2c8bcc8e7d367a804`.
- `build_archive.py`:
  `28c00fc289a8233dd19010222bc9e8f739b3b2efdf60c2e08ace94a0a39529c1`.
- Unchanged PowerShell wrapper:
  `f3d08b4e17befd4101bcab72b84675c9d4af4a0be40c7e4f5099dd0fb9fff4d9`.

## Corrections

P1-001: complete journals require terminal LF and split only on LF, not other
Unicode/control line separators. STOP-only parsing can preserve the committed
complete-line prefix and separately record an unterminated suffix's size,
hash and JSON parse status. That suffix is never counted as an atomic event.
Torn evidence makes saved-only verification INCOMPLETE, preserves reported
versus verified STOP separately, marks incomplete resource totals, and uses
null for unknown task counts. Complete-M4 cannot admit torn journals.

P1-002: the builder rejects UNC, drives, ADS, absolute/traversal and noncanonical
reference strings lexically before resolve/stat/hash/open. Both tools validate
each filesystem component using no-follow metadata and reject symbolic,
junction/reparse redirects before following them. Inventory traversal also
checks each entry before descent. The builder's references now pass through
this guard before resolution. Trap tests exercised both direct APIs and the
actual reference loop without external access.

P1-003: a pure metadata classifier transcribes frozen stop_category and
record_supervision precedence. STOP labels must match their type/message and
an exact atomic FAILED task, exact native deadline/clock/process/zero-exit
fallback, or a corroborated bootstrap/intertask worker exception trace plus
abnormal native outcome. A numerical traceback alone cannot replace a FAILED
record. Missing provenance with a torn suffix is explicitly unknown. Original
worker failure is preserved when it precedes a later native kill. Supervisor
PID is a positive integer; Job name must have the exact PID-bound producer
prefix and ASCII numeric suffix; stage hash and actual native fields must
agree. The builder shares the reproducer's metadata-only terminal validator.

The separately authorized canonical `review.md` exclusion is now registered in
both finite annex policies, alongside FINAL_REVIEW.md and the common binding.
`REPRO_ANNEX_POLICY_REGISTRATION_2.json` records the exact ten fixed paths before
any real archive. No dynamically added annex exemption is allowed.

## Fresh limited verification

Existing parser regressions: 46 PASS, actual native exit 0;
`REPRO_TOOLING_SYNTHETIC_TEST_RESULT_7.json`, SHA256
`8abc63196e60edc8cc0849f85f6f420ee19c86510688e46b9c28a1bae8101c40`.
Its source checks retain six unchanged frozen producer identities.

Focused review-1 repairs: 55 PASS, actual native exit 0;
`REPRO_TOOLING_REVIEW1_REPAIR_TEST_RESULT_3.json`, SHA256
`a3d0557fce4d9ae360b3eebc7da9f5abf6b5ae2fe460e6c718fe5ebaea108a0d`.
These methods include LF/torn-record cases, lexical filesystem traps,
symlink/junction denial before traversal, temporary builder integration and
create-only behavior, torn-STOP metadata preservation, contradictory STOP
labels/native outcomes, bootstrap and native precedence, and malformed PID/Job
identities. The suites overlap and are not summed as independent evidence.

Latest native logs are `REPRO_TOOLING_SYNTHETIC_TEST_NATIVE_8.log` and
`REPRO_TOOLING_REVIEW1_REPAIR_TEST_NATIVE_3.log`. Any manifest records printed
in earlier test logs were created only under verified temporary fixture roots,
then removed; they were never the real P5 archive. The latest focused runner
captures such synthetic-only stdout inside its explicitly synthetic receipt.

## Remaining gate

Independent re-review of these exact candidates is required. No scientific
PASS, M4 approval, publication authorization or permission to run full saved
reproduction is issued by this tooling handoff. Actual closed-archive
reproduction remains deferred until real native/scientific termination.
