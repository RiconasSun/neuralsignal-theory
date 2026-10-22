# Primary saved-audit launch account

Mission: `P16-M3-M5-SHUTDOWN-RECOVERY-R5`.

The first three launch attempts stopped during BOOTSTRAP, before registration,
inventory hashing, prepared-A loading or per-state scientific admission. Their
reported optimizer and B0 attempted counts are all zero. They are preserved,
not deleted or represented as completed audits.

1. `PRIMARY_AUDIT_NATIVE_1.log`: exact float subtraction of the original
   monotonic interval failed equality with 86,400 seconds. The harness was
   corrected to the existing 1e-6 interval-identity tolerance. Original source
   retained as `PRIMARY_SAVED_AUDIT_ATTEMPT1.py`.
2. `PRIMARY_AUDIT_NATIVE_2.log`: sandbox CIM access denied the actual Windows
   boot-identity read. No bypass was used; the actual boot check was executed
   with approved escalation on the next attempt.
3. `PRIMARY_AUDIT_NATIVE_3.log`: relative `runpy` filename prevented construction
   of a repository-relative script path for registration. The launch path was
   made absolute without a scientific or source change.

The first receipt `paper16_development_r5/PRIMARY_AUDIT_STOP.json` is immutable
evidence of launch 1. Its generic `STOP_REUSE_REQUIRED_GATE` label was emitted
by the outer harness before the private reuse gate was entered. It is not a
finding that any frozen fitted state failed. Launches 2 and 3 are preserved in
their own native logs; the first receipt was not overwritten.

`PRIMARY_AUDIT_NATIVE_4.log` is the first actual primary saved-state admission
pass. Its registered source and Phase A claim are bound by the create-only
`PRIMARY_AUDIT_REGISTRATION.json`. Any actual required-state failure in that
pass stops further scientific audit; no full-pass repetition is authorized.
