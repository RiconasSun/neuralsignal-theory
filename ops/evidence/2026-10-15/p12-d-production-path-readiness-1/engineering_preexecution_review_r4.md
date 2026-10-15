# Independent engineering/security preexecution review — revision 4

Mission: `P12-D-PRODUCTION-PATH-READINESS-1`  
Base: `76b19508a5a0728e500ff2e5f9c959309fbf967e`  
Reviewer: independent Codex custody/security review agent; this is not independent human approval.

Decision: **APPROVE_SYNTHETIC_REHEARSAL_ONLY**. P0 = 0; P1 preventing the registered synthetic rehearsal = 0. This is a prospective source/evidence decision, not a completed runtime gate or scientific PASS.

## Exact evidence binding

- On-disk `paper12_production1/source_freeze.json` revision 4 SHA256: `de328c15891e60d7b2a07bf8f66407ccb6b3f64b0075e5dc8aba4a3b916dd301`.
- Independently read and hashed all 19 files in that freeze: no mismatches.
- Independently hashed all 28 original files in the mission registration: no mismatches.
- `focused_r4.log` SHA256: `3284a7bda9b5f0f75891b660570836b6b5df38454e977ddff651f1fb05bd151a`; saved evidence reports 19 tests, all PASS.
- `bundle_roster_r4.log` SHA256: `c1fcf37388988c42fe6706d92f6715a2e4192983191ff8879307c3690d3e9aea`; saved evidence reports exact positive target/controller code-bundle checks, 30 files each.

The reviewer performed public source/metadata/hash reads only. No protected REAL C/D states, arrays, ciphertext, keys, authority roots, releases, fits, or runtime experiments were accessed or executed.

## Engineering findings

The earlier dual-principal ACL defect is repaired: shared binding and success approval/anchor grants explicitly enroll both controller and target. Actual target readiness now requires reading the bound public/model artifacts before the success entitlement can be consumed. The controller receives write access only to its registered ledger/fence paths; host activation metadata remains outside those writable paths.

`complete_code_identity` now requires the exact host freeze and full target/controller file rosters, including worker aliases, original dependencies, math-source manifests, and bootstrap manifests, before consumption. Host source bytes, role bundles, runtime hashes, signature-bound artifacts, actual held target identity, and registered private deployment hashes are checked together. Empty or omitted candidate code rosters cannot satisfy these checks.

Revision 4 addresses the earlier production-entrypoint coverage gap prospectively. The rehearsal will run the unchanged 29 controller oracles and extra synthetic consumptions, then retain that same controller process waiting for the host activation cue. `activate_registered` validates the prepared roles, code/runtime/configuration and actual target readiness, rechecks preflight, and writes the artifact-bound cue. The controller's generic production-consumption branch verifies that cue and invokes the frozen controller. Delivery and evaluation then use the registered production entrypoint. Runtime success for this path remains to be demonstrated by this rehearsal.

The producer requires durable consumption and a delivery-start fence, verifies the catalog and selected unit/trial identities, stages a complete scoped payload privately, and grants data rather than keys to the exact approved target. Delivery interruption poisons replay. The after-ACL interruption is truthfully distinguished as a synthetic capability grant without a start signal or completed assessment. Controller hard-crash fixtures and host exception interruptions are not represented as interchangeable tests.

REAL authority remains pending. The REAL preflight denies before source resolution or process resume when the separately registered authority receipt is absent. There is no REAL signing/key-generation entrypoint in the reviewed production path. Local ACLs and the pinned deployment protect against the restricted workers under the registered trusted-host model; they do not establish protection from a hostile desktop administrator or an independent human custodian.

## Mandatory downstream gate

Proceed only with the registered synthetic cohort, synthetic authority and synthetic source roots. Preserve failed attempts and the exact revision-4 freeze. Final readiness requires fresh matching actual-role/held-process evidence, the unchanged 29 oracles, all registered delivery negatives, one full 13-mouse evaluation, source/runtime/binding checks, protected-source/key/issuer/ledger denial proofs, durable consumption/delivery evidence and native exit/cleanup receipts. Missing or failed proof must remain unresolved; this review cannot substitute for it.

This review may be bound as a **SYNTHETIC_D engineering review artifact only**. It does not provision a REAL authority, issue a REAL signature, permit REAL D consumption or evaluation, clear any historical scientific failure, or approve a manuscript claim. Those fields remain false or pending as applicable.
