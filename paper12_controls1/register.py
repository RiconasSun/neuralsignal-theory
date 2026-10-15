"""E0 registration, public source/metadata only; no scientific implementation."""
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
BASE='cbf3ef5b69c2fe8ba6720d32eb5a031194dcd74f'
MISSION='P12-FINAL-PRERELEASE-CONTROLS-1'
EVIDENCE=ROOT/'ops/evidence/2026-10-14/p12-final-prerelease-controls-1'
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def load(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,v,exclusive=True):
    if exclusive is not True:raise ValueError('APPEND_ONLY')
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(v,f,indent=2,sort_keys=True,allow_nan=False);f.write('\n')
REQ=[
('E0','Verify exact BASE and origin/test; preserve dirty work'),
('E0','Preserve historical final Stage1 FAIL and every scientific failure'),
('E0','Preserve development evidence, frozen hypotheses and acceptance rules'),
('E0','Preserve source identities,26mouse allocation and13final identities'),
('E0','Register original source/protocol hashes before implementation'),
('E0','Define custodian,approval issuer,release controller,C worker and final principal'),
('E0','Define threat model and administrator/operator limitations'),
('E0','Freeze controller state machine and realm separation'),
('E0','Freeze exactly-once ledger durability and failure semantics'),
('E0','Register atomic tests and required evidence before implementation'),
('E1','Isolated C worker reads C partitions only'),
('E1','No D array loader or shared development evaluation utility'),
('E1','Bind frozen physiological C QC with exact ISI/source provenance'),
('E1','Apply unchanged C trial masks and100ms counts'),
('E1','Apply salted unit identities and exact matching contract'),
('E1','Audit13mice mandatory sensitivity coverage before any fitting'),
('E1','Fit C-only scalers and five frozen nested GLMs'),
('E1','N is one flattened fullROI fit per frozen seed11/23/37'),
('E1','Preserve N ridge .1 and exact initialization/options/budgets'),
('E1','Use coefficient mean of all3N seeds with independent certificate'),
('E1','Original outward-gradient PG<=.001 for every required endpoint'),
('E1','Independent AD and original numerical tolerance<=1e-5'),
('E1','Retain each failed attempt and stop required numerical failure'),
('E1','Freeze all six model coefficients for every eligible view'),
('E1','Freeze every view scaler,ordered units,trial masks and metadata'),
('E1','Certify unchanged O/N/NH reuse and changed-pool NP/F/OHP fits'),
('E1','Complete artifact-bound calibration manifest before D request'),
('E2','Bind protocol/source/runtime/controller/analysis code hashes'),
('E2','Bind exact13final identities and D partition manifest'),
('E2','Bind verified complete C states and all relevant reviews'),
('E2','Bind approved actual principal and exact one-shot specification'),
('E2','Bind unique signed authorization ID and realm/key trust root'),
('E2','Exclusive durable append-only consumption BEFORE capability grant'),
('E2','No entitlement restoration after consumption/crash'),
('E2','Deny duplicate and concurrent release'),
('E2','Deny replay and changed code/calibration artifacts'),
('E2','Deny tampered/missing/truncated ledger or tombstones'),
('E2','Deny unauthorized principal and PID/token substitution'),
('E2','Deny incomplete C states and missing independent approval'),
('E2','Deny partial rollback; no flags/names/self-declared permission'),
('E2','Disclose enforcement limits; STOP if actual boundary unenforceable'),
('E3','Synthetic C/D partition canaries and realm separation'),
('E3','Actual source/key/ACL/network denial under Windows principal'),
('E3','Worker denied issuer key/ledger; controller denied issuer key'),
('E3','Ledger crash/interruption tests at every state transition'),
('E3','Concurrent and duplicate-release denial integration tests'),
('E3','Full calibration state completeness and roundtrip tests'),
('E3','Original PG/AD/fixed FD and objective/nesting/scaler parity tests'),
('E3','Tamper/hash/schema/reparse/substitution rejection tests'),
('E3','Native PowerShell synthetic end-to-end reproduction'),
('E3','Independent engineering and scientific review before real C'),
('E3','Injected failures preserved and never counted valid release'),
('E4','Real C permitted only after ALL E0-E3 gates PASS'),
('E4','Execute all13finalmice C-only under trusted custody'),
('E4','Preserve per-mouse/subfield evidence and all3N seeds'),
('E4','Require unchanged physiology/numerics/minimum mice/views'),
('E4','Seal full C state with exact model/policy/artifact hashes'),
('E4','STOP real C failure without D entitlement consumption'),
('E5','Deliver architecture,implementation,ledger and prospective registration'),
('E5','Deliver synthetic and actual-principal evidence'),
('E5','Deliver independent review and one-command reproduction'),
('E5','Report ENGINEERING_CONTROL_PASS separately'),
('E5','Report REAL_C_CALIBRATION_PASS separately'),
('E5','D_RELEASE_CONSUMED must remain FALSE'),
('E5','D_EVALUATION_EXECUTED must remain FALSE'),
('E5','Reviewed scoped Git commit,origin/test readback and clean gate'),
('E5','STOP after handoff; no automatic D progression'),
]
ARCH='''# Prospective security architecture and state machine

Mission P12-FINAL-PRERELEASE-CONTROLS-1. This engineering authorization permits synthetic enforcement tests and, only after E0-E3 PASS, one frozen real C calibration. It never grants real D authorization, consumption or evaluation. Original Stage1FAIL and all M4 evidence remain immutable.

Roles: the trusted host custodian alone holds original compartment keys and administers protected artifacts. An approval issuer is a separate trusted capability, not the scientific worker: Ed25519 private signing material is outside all analysis/controller grants. The release controller is a separate zero-network Windows AppContainer, granted only its registered signed request, immutable verification code/public authority and private ledger. Calibration and final-analysis principals are distinct fresh zero-capability AppContainers with immutable code/runtime/allowed inputs, no inherited handles, no source/issuer/ledger/compartment keys. A trusted host broker holds the actual target process handle, checks token AppContainer SID/capabilities and creation identity, and binds them to the approval; PID strings alone confer no authority. Broker grants scoped data (never keys) only after verifying controller identity, successful durable consumption and target/artifact identity again.

Threat model: hostile or mistaken restricted scientific worker/request files; concurrency, interruption, replay and artifact drift. Windows token/DACL enforcement and trusted immutable controller/custodian/issuer are trusted. Same desktop administrator/operator remains trusted and can alter files/tokens/keys; no hostile-admin, independent-human-custodian, physical rollback or power-loss hardware guarantee is claimed. OS fsync/FlushFileBuffers and protected NTFS records implement software-crash durability; missing/inconsistent records fail closed. No remote notary or hardware monotonic counter is claimed.

REAL_D and SYNTHETIC_D use separate authority domains, signed schema values, protected roots and keys. Only SYNTHETIC_D approvals can be issued in this mission. No real authorization or real decryption route is invoked. Future REAL_D activation requires separate human authorization plus independent artifact-bound approval. A synthetic approval can never authorize a real root/key/path.

Canonical signed binding: version/domain/realm/mission/BASE/unique authorization ID; SHA256 of protocol/locks/cohort/D metadata partition manifest/C complete state manifest/all artifacts/source/runtime/controller/worker; approved package SID and held-process creation identity; exact one-shot evaluation specification; required independent review/gate evidence. Strict schemas, duplicate-key/nonfinite rejection, no unknown fields or traversal/reparse/hardlink substitution. Verify actual immutable bytes, not asserted booleans.

State machine: UNINITIALIZED -> GENESIS (explicit trusted bootstrap only); GENESIS -> APPROVED (independent signed unique authorization); APPROVED -> INTENT (exclusive preexisting protected ledger lock, validate signatures/artifacts/principal/complete C); INTENT -> CONSUMED (durable append-only record and independent durable tombstone, flushed BEFORE capability); CONSUMED -> CAPABILITY_GRANTED (broker only); completion is recorded append-only. DENIED attempts never provide capability. Any crash at/after INTENT permanently poisons that unique entitlement; no retry/reset/rollback/recreation. Missing genesis/record/tombstone, broken chain, malformed or partial tail, inconsistent counterpart, missing approval or incorrect realm deny. A unique intent/consumption ID cannot be reused under another ledger or evaluation spec. Ledger root initialization is not exposed to the controller/evaluation path. Protected external issuance registry binds root/genesis and entitlement; missing root is denial, never auto-initialize.

Ledger: native exclusive OS file lock; signed genesis and issued binding; length-delimited/canonical hash-chained events with previous digest, unique auth ID, state and binding hash; flush each append; exclusive durable intent/tombstone prevents concurrent reuse. Crash after intent and before log consumption still denies forever. Ledger plus separately protected issuer/tombstone anchor prevents log truncation from making a used grant fresh within the stated non-hostile-controller model. Controller has no issuer key. All partial/injected failures retained; tests distinguish attempted consumption from valid capability grants. Successful synthetic consumption counters never count as REAL_D consumption.

C policy: custody opens C envelope/key only, never D or whole-session source; exact frozen C-QC provenance supplies timestamp/ISI eligibility because binned counts cannot prove ISI. It exports selected C counts and C metadata only into a protected derivative, no D keys/arrays. All13 metadata/view coverage audited before fitting: primary32/32, matched16/16, rate/boundary20/boundary40 >=5pairedunits and >=8mice; probe views descriptive. C scalers only. N uses original flattened fullROI29-feature L-BFGS-B ridge.1 seeds11/23/37 RNGnormal(0,.05,U*29), ftol1e-10/gtol1e-5/maxiter2000/maxfun80000, no retries; original per_unit_exposure objective, allseed+coefficientmean originalPG/AD certificates. Five GLMs use unchanged accepted_fit and solver. OriginalPG<=.001/independenterror<=1e-5; fixed synthetic FD1e-5/1e-6, unchanged scientific math. Reuse unchanged O/N/NH selected rows only with exact scaler/feature identity; refit NP/F/OHP for changed pool. Store every view sixcoefficients,scaler,orderedIDs/trials/masks,selection/QC/source/runtime/policy and all N seed states/certificates. Save each attempt before propagating failure. Any required real C numerical/coverage/source/security failure STOPs, with no retry or D consumption. Phase wall limit43200s unchanged.

Engineering retry policy: synthetic expected injected failures are required denial cases, never scientific releases. Unexpected implementation/test failures are preserved and fixed without changing this registered security/scientific contract. Security impossibility =>STOP. No real C before independent review of complete passing synthetic and real-principal receipts.
'''
TESTS=[
'Strict canonical approval/schema/domain/signature/unknown-fields/duplicate-key/nonfinite rejection',
'Exact code/protocol/cohort/partition/runtime/Cstate/spec/review/principal hash binding',
'No approval or incomplete C manifest denial',
'Real-vs-synthetic realm/key/root cross-use denial',
'Source,key,issuer-key,ledger read/write,DACL modification,network,host memory actual-role denial',
'Target actual token/SID/creation identity and unauthorized/PID-substitution denial',
'Duplicate/concurrent/replay attempts yield at most one complete synthetic capability',
'Crash before intent,after intent,after append,after consumption,before/after capability; no restoration',
'Missing/truncated/malformed/tampered/reordered ledger or missing/mismatched tombstone fails closed',
'Traversal,reparse,hardlink and immutable artifact substitution denial',
'C/D canary separation and changing synthetic D never changes C export/scaler/state',
'Frozen fullROI N design/scaler/flattened objective/gradient/seed/options and allseedmean parity',
'Original outwardPG near-bound counterexample,independentAD,fixedFD1e-5/1e-6,finite,bounds',
'Frozen causal histories/reset/ownexclusion/nested zeroembedding/ridge/intercept/scaler rules',
'Coverage of all13/primary32/matched16/rate/boundary >=8 before first fit',
'Insufficient coverage rejects before any optimizer call',
'Injected failed fit retains attempted state/diagnostic and stops further fits',
'All six coefficients/every view/scaler/unit/trial/mask/Nseeds and reuse provenance complete roundtrip',
'PowerShell host+native synthetic end-to-end with immutable registration and actual-role receipts',
'Independent security and scientific review before conditional realC',
'RealC:13identities exactCQC/masks/physiology/allseed/numeric/views/fullseal,noD',
'Saved-evidence reproduction distinct from fresh synthetic executable reproduction; never replay real C silently',
'History preservation,scoped staging,Gitblob hashes,origin/test remote readback and clean tree',
]
def main():
    if subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()!=BASE:raise RuntimeError('WRONG_BASE')
    paths=subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().rstrip('\0').split('\0')
    prior={n:sha(ROOT/n) for n in paths}
    EVIDENCE.mkdir(parents=True,exist_ok=False)
    (HERE/'historical_daily_operations.bin').write_bytes((ROOT/'ops/daily-operations.md').read_bytes())
    save(HERE/'preservation_manifest.json',{'base':BASE,'tracked_working_bytes_sha256':prior})
    (HERE/'SECURITY_ARCHITECTURE.md').write_text(ARCH,encoding='utf-8')
    requirements=[{'id':f'REQ-{i:03}','stage':stage,'requirement':v,'status':'OPEN'} for i,(stage,v) in enumerate(REQ,1)]
    save(HERE/'mission.json',{'mission':{'id':MISSION,'objective':'Implement and independently verify prerelease enforcement; conditional frozen C-only calibration; NO real D authorization/consumption/evaluation'},'base':BASE,'requirements':requirements,'baseline_requirement_count':len(requirements),'target':{'workdir':str(ROOT),'files':['paper12_controls1/**',EVIDENCE.relative_to(ROOT).as_posix(),'ops/daily-operations.md']}})
    frozen=load(ROOT/'paper12_predictive_v2/final_validation_freeze.json')['source_configuration_sha256']
    for n in ('paper12_curated_v1/locks/units.json','paper12_curated_v1/locks/trials.json','paper12_custody1/amendment.json','paper12_custody1/ROLE_POLICY1.json','paper12_custody1/baseline_fit.py','paper12_custody1/baseline_features.py','paper12_custody1/native_analysis_check.py','paper12_custody1/launch_analysis.py','paper12_resume1/verified_atomic.py','paper12_resume1/results/M2/gate_result.json','paper12_finalv2/pre_release_audit.json','paper12_predictive_v2/MANUSCRIPT.md'):
        frozen[n]=sha(ROOT/n)
    save(HERE/'prospective_registration.json',{'mission':MISSION,'base':BASE,'utc':datetime.now(timezone.utc).isoformat(),'before_implementation':True,'before_C_access':True,'real_D_authorization':False,'D_RELEASE_CONSUMED':False,'D_EVALUATION_EXECUTED':False,'architecture_sha256':sha(HERE/'SECURITY_ARCHITECTURE.md'),'mission_sha256':sha(HERE/'mission.json'),'preservation_sha256':sha(HERE/'preservation_manifest.json'),'source_sha256':frozen,'tests':TESTS,'branch_preflight':{'origin_test':BASE,'origin_main':None,'initial_tree':'CLEAN'}})
    body=['# Frozen prerelease engineering baseline','',f'Mission {MISSION}; BASE {BASE}.','',f'Atomic requirements: {len(requirements)}. All remain traceable; no scientific-policy amendment or D entitlement. Architecture and tests prospectively frozen before implementation.','',ARCH,'','## Required proof','']+['- '+t for t in TESTS]+['','## Requirements','', '| ID | Stage | Requirement | Status |','|---|---|---|---|']+[f"| {z['id']} | {z['stage']} | {z['requirement']} | OPEN |" for z in requirements]
    (EVIDENCE/'goldenstandards.md').write_text('\n'.join(body)+'\n',encoding='utf-8')
    print({'mission':MISSION,'requirements':len(requirements),'preserved_files':len(prior),'D_authorized':False})
if __name__=='__main__':main()
