# Independent saved/report review 2

Mission P15-M2-M5-NATIVE-QC-AND-DEVELOPMENT. Decision: REPAIR_REQUIRED. Open P0=0; open P1=1. Original review1 and all failures are preserved. This is a static/synthetic component review, not final archive or scientific acceptance.

Scope and hashes:
- `saved_audit.py` SHA256 `1c526416af809d6db8a6771228e8cca79d2d1e9e86c50e1bdc604956d2347f22`
- `saved_verify.py` SHA256 `c3ba6b11092837cf3ac9f48922244fbbd76d45950f72e01cfe58daf59fae1e2a`
- `reproduce.ps1` SHA256 `c9b8595d13038ef74881e82234c7ab8b910b3a80fb1bfe9fac184bb5acd76397`
- `report.py` SHA256 `cb28c35d2ff99dfac61b60290dd68461c011239bbc68547c3afdd284a2626bc7`
- `test_saved_audit.py` SHA256 `6aaf4bcd65215345926f241e30ee24ee65d5d69f569abd707051df8e1a489626`
- `evaluation.py` SHA256 `12a07251f51be6bd6e56a6cac738621ee5781375e6868add02d12e50cf1e92da`

No actual ARCHIVE_FREEZE/E reproduction was attempted. No raw neural, A cache, B/E/Final values, network, real fit or second E prediction was accessed. Two focused synthetic saved-audit tests independently ran under Werror::ResourceWarning, exit0. An isolated AST re-execution rejects the original forged sensitivity PG/out-of-bounds counterexample; report prerequisite now rejects production=false. No product source was edited by reviewer.

## Closed components from r1

P1-1 is closed for revised numerical validator: sensitivity state hash is verified; synthetic zero Model reconstructs the frozen mask/bounds/dimension without any real likelihood/features; PG is independently recomputed from saved vectors and PASS/FAIL is checked equivalently. P1-2 is closed at code-design level: exact nonwork/nonpycache manifest set, mandatory key set, exact expected neural-access QC-journal names and pinned runtime versions are now required. Actual final archive construction/reproduction remains to be performed once scientific artifacts exist. P1-4 readiness conjunction now includes M2 floors/labs, production, baseline, complete fixed-attempt counts and selection cohort. It is explicitly a Development handoff, no actual Final C/D authority. It does not demand favorable p-values, unavailable capacity sensitivities or every optimizer candidate PASS. Final generated report/claim audit and external reviewed closure must still be checked. P1-3 is closed for B selection: exact admitted/A-plan/selection subjects and unique registered37 configuration groups/nominal counts are checked.

## Remaining P1 — E case/control contents are not bound to expected path identities

`saved_audit.audit_E` reads per-subject filenames but does not assert each E_control record subject equals its filename/expected subject, or each sensitivity record subject/case equals its registered subject/case path. `sensitivity_summary` counts rows rather than unique mice, and `control_summary` likewise admits duplicated subjects. The independent pure-function synthetic counterexample supplied six identical rows for one real identity and returned n_mice=6, minimum6_coverage=true. A file can have a correct content hash and still contain the wrong animal/case; exact archive hashing alone does not establish semantic identity.

Repair: require one-to-one path/content subject+case bindings, unique expected subject/cohort and suite/case key sets in saved audit. Require duplicate mouse records and duplicate (mouse,case) pairs to fail closed in the summary functions (without changing any valid-source statistic). Bind each case A_state_sha256 to its exact sealed state and preserve unavailable cases. Assert the complete E result-hash key set (three registered summary files) and one-batch mouse_count, rather than silently accepting any subset of claimed hashes. Do not rescore/refit/restart E or change thresholds to repair this validator.

The revised audit already validates frozen JSON/hash-only predecessor gates, individual saved numerical arithmetic, deterministic PCG64 seed/mapping journals and reference-effect arithmetic, without invoking extract_role/prepare/run or a frozen predictor. This useful strengthening does not compensate for the remaining animal-identity gap.

M1 conditional guard remains: negative/mixed controls or mandatory-sensitivity coverage restrict named scientific claims and must be reported; they are not a new result-dependent implementation failure or automatic positive PASS. Secondary failures cannot shrink the primary cohort. Any later primary-only or six/seven-mouse Final option needs its registered conditions and separate human authorization. No Final-ready/source-clock/physiology claim follows from this component review.

Next: fix only the identity validator/regressions, rerun meaningful synthetic checks, then request review3 at exact final hashes. Actual saved-only full reproduction and final report/claim review remain later gates.
