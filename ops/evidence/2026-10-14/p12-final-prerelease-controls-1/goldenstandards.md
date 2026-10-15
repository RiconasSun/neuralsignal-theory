# Frozen prerelease engineering baseline

Mission P12-FINAL-PRERELEASE-CONTROLS-1; BASE cbf3ef5b69c2fe8ba6720d32eb5a031194dcd74f.

Atomic requirements: 67. All remain traceable; no scientific-policy amendment or D entitlement. Architecture and tests prospectively frozen before implementation.

# Prospective security architecture and state machine

Mission P12-FINAL-PRERELEASE-CONTROLS-1. This engineering authorization permits synthetic enforcement tests and, only after E0-E3 PASS, one frozen real C calibration. It never grants real D authorization, consumption or evaluation. Original Stage1FAIL and all M4 evidence remain immutable.

Roles: the trusted host custodian alone holds original compartment keys and administers protected artifacts. An approval issuer is a separate trusted capability, not the scientific worker: Ed25519 private signing material is outside all analysis/controller grants. The release controller is a separate zero-network Windows AppContainer, granted only its registered signed request, immutable verification code/public authority and private ledger. Calibration and final-analysis principals are distinct fresh zero-capability AppContainers with immutable code/runtime/allowed inputs, no inherited handles, no source/issuer/ledger/compartment keys. A trusted host broker holds the actual target process handle, checks token AppContainer SID/capabilities and creation identity, and binds them to the approval; PID strings alone confer no authority. Broker grants scoped data (never keys) only after verifying controller identity, successful durable consumption and target/artifact identity again.

Threat model: hostile or mistaken restricted scientific worker/request files; concurrency, interruption, replay and artifact drift. Windows token/DACL enforcement and trusted immutable controller/custodian/issuer are trusted. Same desktop administrator/operator remains trusted and can alter files/tokens/keys; no hostile-admin, independent-human-custodian, physical rollback or power-loss hardware guarantee is claimed. OS fsync/FlushFileBuffers and protected NTFS records implement software-crash durability; missing/inconsistent records fail closed. No remote notary or hardware monotonic counter is claimed.

REAL_D and SYNTHETIC_D use separate authority domains, signed schema values, protected roots and keys. Only SYNTHETIC_D approvals can be issued in this mission. No real authorization or real decryption route is invoked. Future REAL_D activation requires separate human authorization plus independent artifact-bound approval. A synthetic approval can never authorize a real root/key/path.

Canonical signed binding: version/domain/realm/mission/BASE/unique authorization ID; SHA256 of protocol/locks/cohort/D metadata partition manifest/C complete state manifest/all artifacts/source/runtime/controller/worker; approved package SID and held-process creation identity; exact one-shot evaluation specification; required independent review/gate evidence. Strict schemas, duplicate-key/nonfinite rejection, no unknown fields or traversal/reparse/hardlink substitution. Verify actual immutable bytes, not asserted booleans.

State machine: UNINITIALIZED -> GENESIS (explicit trusted bootstrap only); GENESIS -> APPROVED (independent signed unique authorization); APPROVED -> INTENT (exclusive preexisting protected ledger lock, validate signatures/artifacts/principal/complete C); INTENT -> CONSUMED (durable append-only record and independent durable tombstone, flushed BEFORE capability); CONSUMED -> CAPABILITY_GRANTED (broker only); completion is recorded append-only. DENIED attempts never provide capability. Any crash at/after INTENT permanently poisons that unique entitlement; no retry/reset/rollback/recreation. Missing genesis/record/tombstone, broken chain, malformed or partial tail, inconsistent counterpart, missing approval or incorrect realm deny. A unique intent/consumption ID cannot be reused under another ledger or evaluation spec. Ledger root initialization is not exposed to the controller/evaluation path. Protected external issuance registry binds root/genesis and entitlement; missing root is denial, never auto-initialize.

Ledger: native exclusive OS file lock; signed genesis and issued binding; length-delimited/canonical hash-chained events with previous digest, unique auth ID, state and binding hash; flush each append; exclusive durable intent/tombstone prevents concurrent reuse. Crash after intent and before log consumption still denies forever. Ledger plus separately protected issuer/tombstone anchor prevents log truncation from making a used grant fresh within the stated non-hostile-controller model. Controller has no issuer key. All partial/injected failures retained; tests distinguish attempted consumption from valid capability grants. Successful synthetic consumption counters never count as REAL_D consumption.

C policy: custody opens C envelope/key only, never D or whole-session source; exact frozen C-QC provenance supplies timestamp/ISI eligibility because binned counts cannot prove ISI. It exports selected C counts and C metadata only into a protected derivative, no D keys/arrays. All13 metadata/view coverage audited before fitting: primary32/32, matched16/16, rate/boundary20/boundary40 >=5pairedunits and >=8mice; probe views descriptive. C scalers only. N uses original flattened fullROI29-feature L-BFGS-B ridge.1 seeds11/23/37 RNGnormal(0,.05,U*29), ftol1e-10/gtol1e-5/maxiter2000/maxfun80000, no retries; original per_unit_exposure objective, allseed+coefficientmean originalPG/AD certificates. Five GLMs use unchanged accepted_fit and solver. OriginalPG<=.001/independenterror<=1e-5; fixed synthetic FD1e-5/1e-6, unchanged scientific math. Reuse unchanged O/N/NH selected rows only with exact scaler/feature identity; refit NP/F/OHP for changed pool. Store every view sixcoefficients,scaler,orderedIDs/trials/masks,selection/QC/source/runtime/policy and all N seed states/certificates. Save each attempt before propagating failure. Any required real C numerical/coverage/source/security failure STOPs, with no retry or D consumption. Phase wall limit43200s unchanged.

Engineering retry policy: synthetic expected injected failures are required denial cases, never scientific releases. Unexpected implementation/test failures are preserved and fixed without changing this registered security/scientific contract. Security impossibility =>STOP. No real C before independent review of complete passing synthetic and real-principal receipts.


## Required proof

- Strict canonical approval/schema/domain/signature/unknown-fields/duplicate-key/nonfinite rejection
- Exact code/protocol/cohort/partition/runtime/Cstate/spec/review/principal hash binding
- No approval or incomplete C manifest denial
- Real-vs-synthetic realm/key/root cross-use denial
- Source,key,issuer-key,ledger read/write,DACL modification,network,host memory actual-role denial
- Target actual token/SID/creation identity and unauthorized/PID-substitution denial
- Duplicate/concurrent/replay attempts yield at most one complete synthetic capability
- Crash before intent,after intent,after append,after consumption,before/after capability; no restoration
- Missing/truncated/malformed/tampered/reordered ledger or missing/mismatched tombstone fails closed
- Traversal,reparse,hardlink and immutable artifact substitution denial
- C/D canary separation and changing synthetic D never changes C export/scaler/state
- Frozen fullROI N design/scaler/flattened objective/gradient/seed/options and allseedmean parity
- Original outwardPG near-bound counterexample,independentAD,fixedFD1e-5/1e-6,finite,bounds
- Frozen causal histories/reset/ownexclusion/nested zeroembedding/ridge/intercept/scaler rules
- Coverage of all13/primary32/matched16/rate/boundary >=8 before first fit
- Insufficient coverage rejects before any optimizer call
- Injected failed fit retains attempted state/diagnostic and stops further fits
- All six coefficients/every view/scaler/unit/trial/mask/Nseeds and reuse provenance complete roundtrip
- PowerShell host+native synthetic end-to-end with immutable registration and actual-role receipts
- Independent security and scientific review before conditional realC
- RealC:13identities exactCQC/masks/physiology/allseed/numeric/views/fullseal,noD
- Saved-evidence reproduction distinct from fresh synthetic executable reproduction; never replay real C silently
- History preservation,scoped staging,Gitblob hashes,origin/test remote readback and clean tree

## Requirements

| ID | Stage | Requirement | Status |
|---|---|---|---|
| REQ-001 | E0 | Verify exact BASE and origin/test; preserve dirty work | OPEN |
| REQ-002 | E0 | Preserve historical final Stage1 FAIL and every scientific failure | OPEN |
| REQ-003 | E0 | Preserve development evidence, frozen hypotheses and acceptance rules | OPEN |
| REQ-004 | E0 | Preserve source identities,26mouse allocation and13final identities | OPEN |
| REQ-005 | E0 | Register original source/protocol hashes before implementation | OPEN |
| REQ-006 | E0 | Define custodian,approval issuer,release controller,C worker and final principal | OPEN |
| REQ-007 | E0 | Define threat model and administrator/operator limitations | OPEN |
| REQ-008 | E0 | Freeze controller state machine and realm separation | OPEN |
| REQ-009 | E0 | Freeze exactly-once ledger durability and failure semantics | OPEN |
| REQ-010 | E0 | Register atomic tests and required evidence before implementation | OPEN |
| REQ-011 | E1 | Isolated C worker reads C partitions only | OPEN |
| REQ-012 | E1 | No D array loader or shared development evaluation utility | OPEN |
| REQ-013 | E1 | Bind frozen physiological C QC with exact ISI/source provenance | OPEN |
| REQ-014 | E1 | Apply unchanged C trial masks and100ms counts | OPEN |
| REQ-015 | E1 | Apply salted unit identities and exact matching contract | OPEN |
| REQ-016 | E1 | Audit13mice mandatory sensitivity coverage before any fitting | OPEN |
| REQ-017 | E1 | Fit C-only scalers and five frozen nested GLMs | OPEN |
| REQ-018 | E1 | N is one flattened fullROI fit per frozen seed11/23/37 | OPEN |
| REQ-019 | E1 | Preserve N ridge .1 and exact initialization/options/budgets | OPEN |
| REQ-020 | E1 | Use coefficient mean of all3N seeds with independent certificate | OPEN |
| REQ-021 | E1 | Original outward-gradient PG<=.001 for every required endpoint | OPEN |
| REQ-022 | E1 | Independent AD and original numerical tolerance<=1e-5 | OPEN |
| REQ-023 | E1 | Retain each failed attempt and stop required numerical failure | OPEN |
| REQ-024 | E1 | Freeze all six model coefficients for every eligible view | OPEN |
| REQ-025 | E1 | Freeze every view scaler,ordered units,trial masks and metadata | OPEN |
| REQ-026 | E1 | Certify unchanged O/N/NH reuse and changed-pool NP/F/OHP fits | OPEN |
| REQ-027 | E1 | Complete artifact-bound calibration manifest before D request | OPEN |
| REQ-028 | E2 | Bind protocol/source/runtime/controller/analysis code hashes | OPEN |
| REQ-029 | E2 | Bind exact13final identities and D partition manifest | OPEN |
| REQ-030 | E2 | Bind verified complete C states and all relevant reviews | OPEN |
| REQ-031 | E2 | Bind approved actual principal and exact one-shot specification | OPEN |
| REQ-032 | E2 | Bind unique signed authorization ID and realm/key trust root | OPEN |
| REQ-033 | E2 | Exclusive durable append-only consumption BEFORE capability grant | OPEN |
| REQ-034 | E2 | No entitlement restoration after consumption/crash | OPEN |
| REQ-035 | E2 | Deny duplicate and concurrent release | OPEN |
| REQ-036 | E2 | Deny replay and changed code/calibration artifacts | OPEN |
| REQ-037 | E2 | Deny tampered/missing/truncated ledger or tombstones | OPEN |
| REQ-038 | E2 | Deny unauthorized principal and PID/token substitution | OPEN |
| REQ-039 | E2 | Deny incomplete C states and missing independent approval | OPEN |
| REQ-040 | E2 | Deny partial rollback; no flags/names/self-declared permission | OPEN |
| REQ-041 | E2 | Disclose enforcement limits; STOP if actual boundary unenforceable | OPEN |
| REQ-042 | E3 | Synthetic C/D partition canaries and realm separation | OPEN |
| REQ-043 | E3 | Actual source/key/ACL/network denial under Windows principal | OPEN |
| REQ-044 | E3 | Worker denied issuer key/ledger; controller denied issuer key | OPEN |
| REQ-045 | E3 | Ledger crash/interruption tests at every state transition | OPEN |
| REQ-046 | E3 | Concurrent and duplicate-release denial integration tests | OPEN |
| REQ-047 | E3 | Full calibration state completeness and roundtrip tests | OPEN |
| REQ-048 | E3 | Original PG/AD/fixed FD and objective/nesting/scaler parity tests | OPEN |
| REQ-049 | E3 | Tamper/hash/schema/reparse/substitution rejection tests | OPEN |
| REQ-050 | E3 | Native PowerShell synthetic end-to-end reproduction | OPEN |
| REQ-051 | E3 | Independent engineering and scientific review before real C | OPEN |
| REQ-052 | E3 | Injected failures preserved and never counted valid release | OPEN |
| REQ-053 | E4 | Real C permitted only after ALL E0-E3 gates PASS | OPEN |
| REQ-054 | E4 | Execute all13finalmice C-only under trusted custody | OPEN |
| REQ-055 | E4 | Preserve per-mouse/subfield evidence and all3N seeds | OPEN |
| REQ-056 | E4 | Require unchanged physiology/numerics/minimum mice/views | OPEN |
| REQ-057 | E4 | Seal full C state with exact model/policy/artifact hashes | OPEN |
| REQ-058 | E4 | STOP real C failure without D entitlement consumption | OPEN |
| REQ-059 | E5 | Deliver architecture,implementation,ledger and prospective registration | OPEN |
| REQ-060 | E5 | Deliver synthetic and actual-principal evidence | OPEN |
| REQ-061 | E5 | Deliver independent review and one-command reproduction | OPEN |
| REQ-062 | E5 | Report ENGINEERING_CONTROL_PASS separately | OPEN |
| REQ-063 | E5 | Report REAL_C_CALIBRATION_PASS separately | OPEN |
| REQ-064 | E5 | D_RELEASE_CONSUMED must remain FALSE | OPEN |
| REQ-065 | E5 | D_EVALUATION_EXECUTED must remain FALSE | OPEN |
| REQ-066 | E5 | Reviewed scoped Git commit,origin/test readback and clean gate | OPEN |
| REQ-067 | E5 | STOP after handoff; no automatic D progression | OPEN |

## Closeout mapping (baseline remains unchanged)

All67 requirements remain traceable in requirement_results.json and requirements.md. E0–E3 independently passed. E4 was rejected by automatic approval before process creation; REQ-054–057 remain human-blocked. Precommit62 verified +4 human-blocked +1 pending actual Git remote-readback. No full-mission PASS. Original source hashes, allocation, hypotheses, numerical thresholds and historical failures remain unchanged. See blocker.md and HANDOFF.json.
