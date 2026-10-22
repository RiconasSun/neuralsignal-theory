"""Independent R6 full saved-state qualification. Implemented only; never auto-run."""
import collections
import contextlib
import datetime
import hashlib
import json
import math
import os
import platform
import socket
import subprocess
import time
import traceback
from pathlib import Path, PurePosixPath, PureWindowsPath
import stat
from unittest.mock import patch

import numpy as np

R = Path.cwd()
P = R / 'paper16_development_r6'
E = R / 'ops/evidence/2026-10-21/p16-m3-m5-reliability-gated-recovery-r6'
PROTO = R / 'paper16_shutdown_recovery_r5_protocol'
OLD = R / 'paper16_development_r3'
FOUR = R / 'paper16_development_r4'
FIVE = R / 'paper16_development_r5'
E5 = R / 'ops/evidence/2026-10-21/p16-m3-m5-shutdown-recovery-r5'
BASE = 'e1aab9622a7e63b99335a529d8ad0107f611dc8c'
MISSION = 'P16-M3-M5-RELIABILITY-GATED-RECOVERY-R6'
PRIVATE_ALLOWED = False
ORIGINS = {'R3': OLD, 'R4': FOUR, 'R5': FIVE}
CONTEXT = {'stage':'NOT_STARTED','task':None}
COUNTS = collections.Counter()
HASHES = {}
CLAIM_SHA = None

def J(path):
    return json.loads(checked_path(path).read_bytes())

def H(path):
    with checked_path(path).open('rb') as stream:
        return hashlib.file_digest(stream,'sha256').hexdigest()

def C(ok, message):
    if not ok:
        raise AssertionError(message)


def checked_path(path):
    """Reject redirects and private reads before the actual public gates pass."""
    path=Path(path)
    try:name=path.absolute().relative_to(R).as_posix()
    except ValueError:raise AssertionError('Nonrepository audit input denied')
    C(name and '\\' not in name and ':' not in name and not PureWindowsPath(name).drive
      and all(part not in ['.','..'] for part in PurePosixPath(name).parts),'Canonical repository path')
    for origin in ORIGINS.values():
        private=(path.is_relative_to(origin/'work') or path in
                 [origin/'results/FIT_JOURNAL.jsonl',origin/'results/INITIALIZER_IDENTITIES.jsonl'])
        C(not private or PRIVATE_ALLOWED,'Private input denied before Host/freeze/review acceptance')
    cursor=R
    for part in PurePosixPath(name).parts:
        cursor=cursor/part
        try:record=cursor.lstat()
        except FileNotFoundError:break
        C(not stat.S_ISLNK(record.st_mode) and not getattr(record,'st_file_attributes',0)&stat.FILE_ATTRIBUTE_REPARSE_POINT,'Reparse/symbolic audit input denied')
    return path

def once(path, value):
    with Path(path).open('x',encoding='utf8',newline='\n') as stream:
        json.dump(value,stream,indent=2,allow_nan=False);stream.write('\n')
        stream.flush();os.fsync(stream.fileno())

def append(path, value):
    with Path(path).open('a',encoding='utf8',newline='\n') as stream:
        stream.write(json.dumps(value,allow_nan=False)+'\n');stream.flush();os.fsync(stream.fileno())

def guard():
    claim=J(P/'PHASE_A_CLAIM.json')
    C(not (E/'INDEPENDENT_R6_AUDIT_FAILURE_1.json').exists(),'Prior required failure is irreversible; no automatic retry')
    C(H(P/'PHASE_A_CLAIM.json')==CLAIM_SHA,'Original Phase A claim hash changed')
    C(claim['mission']==MISSION and claim['base']==BASE and claim['phase']=='A_PREFLIGHT' and claim['no_reset'] is True and abs(claim['deadline_monotonic']-claim['start_monotonic']-86400)<=1e-6,'One original24h phase claim')
    now=datetime.datetime.now(datetime.timezone.utc);elapsed=time.monotonic()-claim['start_monotonic']
    C(0<=elapsed<86400 and time.monotonic()<claim['deadline_monotonic'],'Phase A monotonic deadline/rollback')
    wall=(now-datetime.datetime.fromisoformat(claim['start_UTC'])).total_seconds()
    C(0<=wall<86400 and now<datetime.datetime.fromisoformat(claim['deadline_UTC']) and abs(wall-elapsed)<5,'Phase A UTC deadline/rollback/drift')

def Lines(path, optional=False):
    path=checked_path(path)
    if optional and not path.exists():return []
    raw=path.read_bytes();C(not raw or raw.endswith(b'\n'),'Torn saved journal: '+str(path))
    records=raw[:-1].split(b'\n') if raw else []
    C(all(row.strip() for row in records),'No blank saved journal records')
    return [json.loads(line) for line in records]

def ID(a):
    return {'shape':list(a.shape),'dtype':a.dtype.str,'sha256':hashlib.sha256(a.tobytes()).hexdigest()}

def receipt(ref,expected=None):
    C(PRIVATE_ALLOWED,'Saved arrays require preceding actual public gates')
    path=checked_path(R/ref['path']);C(H(path)==ref['sha256'],'Array receipt SHA: '+ref['path'])
    with np.load(path,allow_pickle=False) as archive:
        C(set(archive.files)==set(ref['arrays']) and (expected is None or set(archive.files)==set(expected)),'Exact registered NPZ members before decode')
        values={k:archive[k].copy() for k in archive.files}
    C({k:ID(v) for k,v in values.items()}==ref['arrays'],'Every array receipt member: '+ref['path'])
    return values


def walk_files(root):
    for entry in os.scandir(checked_path(root)):
        record=entry.stat(follow_symlinks=False)
        C(not stat.S_ISLNK(record.st_mode) and not getattr(record,'st_file_attributes',0)&stat.FILE_ATTRIBUTE_REPARSE_POINT,'Redirected inventory entry denied before descent')
        if stat.S_ISDIR(record.st_mode):yield from walk_files(Path(entry.path))
        else:
            C(stat.S_ISREG(record.st_mode),'Regular saved inventory member')
            yield Path(entry.path)

def inventory(manifest, exact_roots=None):
    C(PRIVATE_ALLOWED,'Full saved inventory requires actual preceding gates')
    rows=manifest['files'];by={row['path']:row for row in rows}
    C(len(by)==len(rows),'No duplicate inventory rows')
    if exact_roots:
        actual={p.relative_to(R).as_posix() for root in exact_roots for p in walk_files(root)}
        C(actual==set(by),'Exact protected inventory union fileset')
    for index,(name,row) in enumerate(by.items()):
        path=checked_path(R/name);C(path.is_file() and not path.is_symlink(),'Protected regular file '+name)
        digest=H(path);C(digest==row['sha256'],'Fresh protected SHA '+name)
        if 'bytes' in row:C(path.stat().st_size==row['bytes'],'Protected size '+name)
        HASHES[name]={'path':name,'bytes':path.stat().st_size,'sha256':digest}
        if index%1000==0:guard()
    return len(by)


def bound_rows(rows):
    C(type(rows) is list and rows,'Required complete public gate bindings')
    C(len({row['path'] for row in rows})==len(rows),'No duplicate gate binding paths')
    for row in rows:
        path=checked_path(R/row['path'])
        C(type(row['bytes']) is int and row['bytes']>=0 and path.stat().st_size==row['bytes'] and H(path)==row['sha256'],'Actual gate-bound file identity '+row['path'])
    return {row['path'] for row in rows}


def frozen_public(path):
    """Public historical metadata must equal immutable BASE, not co-edited pins."""
    path=checked_path(path);name=path.relative_to(R).as_posix()
    C(path.read_bytes()==subprocess.check_output(['git','show',BASE+':'+name],cwd=R),'Historical public source/manifest changed from authorized BASE '+name)


def public_gates():
    """Called before registration, model imports, inventory or any private read."""
    host_path=E/'HOST_RELIABILITY_ACCEPTANCE.json';host=J(host_path)
    C(host['decision']=='ACCEPTED_R6_HOST_RELIABILITY' and all(type(host[k]) is int and host[k]==0 for k in ['open_P0','open_P1']) and host['phase_claim_sha256']==CLAIM_SHA and host['real_A_optimization_authorized'] is False,'Actual independently accepted Host gate before private access')
    hostnames=bound_rows(host['bound_files'])
    C({(E/name).relative_to(R).as_posix() for name in ['HOST_AUDIT_NATIVE.json','HOST_AUDIT_REGISTRATION.json','NATIVE_LIFECYCLE_REGISTRATION_3.json','NATIVE_LIFECYCLE_RESULT_3.json']}<=hostnames,'Exact actual Host audit/registration/native-result evidence required')
    freeze_path=E/'REUSE_AUDIT_PREEXECUTION_FREEZE.json';freeze=J(freeze_path)
    C(freeze['mission']==MISSION and freeze['base']==BASE and freeze['phase_claim_sha256']==CLAIM_SHA,'Original claim and prospective audit freeze')
    names=bound_rows(freeze['bound_files'])
    required={(E/name).relative_to(R).as_posix() for name in ['PRIMARY_REUSE_AUDIT_R6.py','INDEPENDENT_REUSE_AUDIT_R6.py','HOST_RELIABILITY_ACCEPTANCE.json']}|{(P/name).relative_to(R).as_posix() for name in ['REUSE_CANDIDATES.json','RECOVERY_TASK_PLAN.json','PHASE_A_CLAIM.json']}
    C(required<=names and any(name.endswith('/RUNTIME_IDENTITY.json') for name in names),'Both exact independent/primary sources and complete candidate/runtime/Host bindings')
    review=J(E/'INDEPENDENT_REUSE_PREEXECUTION_REVIEW_BINDING.json')
    C(review['decision']=='ACCEPTED_SAVED_REUSE_AUDIT_EXECUTION_ONLY' and all(type(review[k]) is int and review[k]==0 for k in ['open_P0','open_P1']) and review['freeze_sha256']==H(freeze_path) and review['actual_host_gate_accepted'] is True and review['real_A_optimization_authorized'] is False,'Actual independent pre-execution approval; freeze alone is insufficient')
    return {'host_acceptance_sha256':H(host_path),'freeze_sha256':H(freeze_path),'preexecution_review_sha256':H(E/'INDEPENDENT_REUSE_PREEXECUTION_REVIEW_BINDING.json')}

def cert(folder):
    d=J(folder/'DIAGNOSTICS.json');p=d['free_coordinates']
    members={point+suffix for point in ['initial','halfway','endpoint'] for suffix in
             ['_x','_analytic','_AD','_AD_error']+['_FD_'+str(h) for h in [.001,.0001,.00001,.000001]]+['_FD_error_'+str(h) for h in [.001,.0001,.00001,.000001]]}
    C(checked_path(R/d['coordinate_state']['path'])==folder/'coordinate_certificates.npz','Same-folder full coordinate certificate')
    v=receipt(d['coordinate_state'],members)
    C(type(p) is int and 0<p<=368,'Certificate parameter count')
    C(all(a.dtype==np.dtype('float64') and a.shape==(p,) and np.isfinite(a).all() for a in v.values()),'Every saved certificate coordinate is finite float64')
    C((d['FD_objective_calls'],d['AD_calls'],d['analytic_checkpoint_calls'])==(24*p,3,3),'Original derivative certificate budgets')
    C(len(d['checkpoints'])==3 and d['all_checkpoints_pass'] is True and d['FD_step_not_selected_post_result'] is True,'Required three fixed-step checkpoints')
    maxima={'AD':0.,'FD':0.}
    for name,row in zip(['initial','halfway','endpoint'],d['checkpoints']):
        x,g,ad=[v[name+s] for s in ['_x','_analytic','_AD']]
        C(all(a.shape==(p,) and np.isfinite(a).all() for a in [x,g,ad]),'Finite saved coordinate vectors')
        error=np.abs(g-ad)/np.maximum(1,np.maximum(np.abs(g),np.abs(ad)))
        C(np.array_equal(error,v[name+'_AD_error']) and float(error.max())==row['AD_scaled_coordinate_error_max']<=1e-8,'Independent saved AD coordinate arithmetic')
        for step in [.001,.0001,.00001,.000001]:
            fd=v[name+'_FD_'+str(step)]
            diff=np.abs(fd-g)/np.maximum(1,np.maximum(np.abs(fd),np.abs(g)))
            C(fd.shape==(p,) and np.isfinite(fd).all() and np.array_equal(diff,v[name+'_FD_error_'+str(step)]) and float(diff.max())==row['FD_scaled_coordinate_errors'][str(step)],'Every frozen finite-difference scale arithmetic')
        C(row['checkpoint']==name and row['pass'] is True and row['frozen_FD_scaled_error']==row['FD_scaled_coordinate_errors']['1e-05']<=2e-5,'Frozen h1e-5 gate')
        C(math.isfinite(row['objective']) and math.isfinite(row['AD_objective']) and np.isclose(row['objective'],row['AD_objective'],atol=1e-10,rtol=1e-12),'Saved objective/independent AD objective agreement')
        maxima['AD']=max(maxima['AD'],float(error.max()));maxima['FD']=max(maxima['FD'],row['frozen_FD_scaled_error'])
    return d,v,maxima

def pg(x,g,lo,hi):
    return float(np.abs(np.where(((x<=lo+1e-12)&(g>0))|((x>=hi-1e-12)&(g<0)),0,g)).max())

def journals(folder,result,coords,initial,origin):
    C(origin in ORIGINS,'Only exact registered historical origins')
    calls=Lines(folder/'CALLS.jsonl');accepted=Lines(folder/'ACCEPTED.jsonl',True)
    n=result['nfev'];nit=result['nit'];p=len(initial['x0'])
    C(type(n) is int and type(nit) is int and len(calls)==2*n and 1<=n==result['external_value_gradient_pairs']<=6000,'Full FG journal counts/cap')
    C(len(accepted)==nit==result['external_accepted_iterations']==result['accepted_vector_count']<=1500 and nit>=0,'Full accepted journal counts/cap')
    assoc={}
    for i in range(n):
        a,b=calls[2*i:2*i+2]
        C(a['event']=='RESERVED_BEFORE_EVALUATION' and b['event']=='COMPLETED' and type(a['call']) is int and type(b['call']) is int and a['call']==b['call']==i+1,'FG strict alternating reservations/completions')
        C(type(a['iterations']) is int and 0<=a['iterations']<=nit and math.isfinite(b['objective']) and math.isfinite(b['gradient_inf']),'Original finite FG journal scalars')
        if origin in ['R4','R5']:
            x=np.asarray(a['x']);g=np.asarray(b['gradient'])
            C(x.shape==g.shape==(p,) and np.isfinite(x).all() and np.isfinite(g).all() and b['gradient_inf']==float(np.abs(g).max()),'Finite actual R4 FG vectors/norm')
            C(np.all(x>=initial['lo']-1e-12) and np.all(x<=initial['hi']+1e-12),'Actual R4 FG vector within original bounds')
        else:
            C('x' not in a and 'gradient' not in b,'Preserve original R3 scalar-only FG format without inventing vectors')
        assoc[a['iterations']]=(a,b)
    for i,row in enumerate(accepted):
        x=np.asarray(row['x']);C(row['iteration']==i+1 and x.shape==(p,) and np.isfinite(x).all() and np.all(x>=initial['lo']-1e-12) and np.all(x<=initial['hi']+1e-12),'Accepted iteration vector/bounds/order')
        if origin in ['R4','R5']:C(np.array_equal(x,assoc[i][0]['x']),'Every R4 accepted vector equals actual broker FG')
    mid=accepted[math.ceil(nit/2)-1]['x'] if accepted else result['x']
    C(np.array_equal(coords['initial_x'],initial['x0']) and np.array_equal(coords['halfway_x'],mid) and np.array_equal(coords['endpoint_x'],result['x']),'All certificate vectors equal actual original checkpoints')
    C(result['halfway_accepted_iteration']==math.ceil(nit/2),'Original midpoint rule')
    if accepted:C(np.array_equal(accepted[-1]['x'],coords['endpoint_x']),'Actual final accepted endpoint')
    if origin=='R3':
        C(not (folder/'DIAGNOSTIC_CALLS.jsonl').exists(),'Original R3 did not produce derivative reservation journal')
        return n,nit
    C(assoc[nit-1 if accepted else 0][1]['objective']==result['objective'],'Saved endpoint FG objective')
    diagnostic=Lines(folder/'DIAGNOSTIC_CALLS.jsonl');position=0
    for checkpoint_index,name in enumerate(['initial','halfway','endpoint'],1):
        for kind in ['ANALYTIC_RESERVED','AD_RESERVED']:
            C(diagnostic[position]=={'kind':kind,'checkpoint':name,'index':checkpoint_index},'Original diagnostic analytic/AD reservation order');position+=1
        for hi,h in enumerate([.001,.0001,1e-5,1e-6]):
            for coordinate in range(p):
                for si,side in enumerate(['plus','minus']):
                    index=(checkpoint_index-1)*8*p+hi*2*p+coordinate*2+si+1
                    C(diagnostic[position]=={'kind':'FD_RESERVED','checkpoint':name,'index':index,'h':h,'coordinate':coordinate,'side':side},'Complete frozen FD reservation order');position+=1
    C(position==len(diagnostic),'No missing or extra diagnostic reservation')
    return n,nit

def deny(*args,**kwargs):
    raise AssertionError('Independent saved-only audit forbids objective/gradient/AD/score/optimizer/network')

def main():
    global CLAIM_SHA,PRIVATE_ALLOWED
    CONTEXT['stage']='PUBLIC_HOST_AND_PREEXECUTION_GATES'
    CLAIM_SHA=H(P/'PHASE_A_CLAIM.json');guard()
    C(subprocess.check_output(['git','rev-parse','HEAD']).decode().strip()==BASE,'Exact authorized execution BASE')
    gates=public_gates()
    C(not (E/'INDEPENDENT_REUSE_AUDIT_REGISTRATION.json').exists() and not (E/'INDEPENDENT_R6_STATE_LEDGER.jsonl').exists() and not (E/'INDEPENDENT_R6_AUDIT_FAILURE_1.json').exists(),'Fresh single audit registration; prior failure is not retryable')
    boot=subprocess.check_output(['powershell','-NoProfile','-Command','(Get-CimInstance Win32_OperatingSystem).LastBootUpTime.ToUniversalTime().ToString("o")'],text=True).strip()
    phase=J(P/'PHASE_A_CLAIM.json')
    C(abs((datetime.datetime.fromisoformat(boot)-datetime.datetime.fromisoformat(phase['windows_boot_UTC'])).total_seconds())<.001,'Same original Phase A Windows boot')
    registration={'mission':MISSION,'role':'INDEPENDENT_SAVED_ONLY_FULL_REUSE_AUDIT','registered_UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'script_path':Path(__file__).relative_to(R).as_posix(),'script_sha256':H(Path(__file__)),'phase_claim_sha256':CLAIM_SHA,'owner_request_sha256':H(E/'OWNER_REQUEST.txt'),'targets_sha256':H(P/'REUSE_CANDIDATES.json'),'task_plan_sha256':H(P/'RECOVERY_TASK_PLAN.json'),'helper_sources':{'prior_independent_source':H(E5/'INDEPENDENT_R5_REUSE_AUDIT.py')},'optimizer_targets':4616,'B0_targets':216,'one_independent_pass':True,'stop_first_required_failure':True,'new_objective_derivative_optimizer_score_calls':0,'network_denied':True,'constructor_only_initializer_verification':True,'windows_boot_UTC':boot,'public_gates':gates}
    C(phase['owner_sha256']==registration['owner_request_sha256'],'Owner authority identity')
    once(E/'INDEPENDENT_REUSE_AUDIT_REGISTRATION.json',registration)
    PRIVATE_ALLOWED=True  # This sole transition follows every actual public gate.
    CONTEXT['stage']='FROZEN_SOURCE_AND_RUNTIME_IDENTITIES'
    historical_public=[PROTO/'SOURCE_PINS.json',OLD/'SOURCE_PINS.json',OLD/'PREFIT_FREEZE_MANIFEST.json',OLD/'PROTECTED_STATE_MANIFEST.json',FOUR/'SOURCE_PINS.json',FOUR/'PREFIT_FREEZE_MANIFEST.json',FOUR/'PROTECTED_STATE_MANIFEST.json',FOUR/'PROTECTED_STATE_MANIFEST_SUPPLEMENT_1.json',FOUR/'RUNTIME_IDENTITY.json',FIVE/'PREFIT_FREEZE_MANIFEST_V3.json',FIVE/'MATHEMATICAL_COPY_PROOF.json',FIVE/'RUNTIME_IDENTITY.json',FIVE/'EXTERNAL_INTERRUPTION_SNAPSHOT.json',E5/'EXTERNAL_CLOSEOUT_REGISTRATION_1.json',E5/'EXTERNAL_SCIENTIFIC_STOP.json',E5/'INDEPENDENT_EXTERNAL_CLOSEOUT_ACCEPTANCE_1.json']
    for path in historical_public:frozen_public(path)
    proto_pins=J(PROTO/'SOURCE_PINS.json')['files']
    for name,row in proto_pins.items():C(H(R/name)==row['sha256'] and (R/name).stat().st_size==row['bytes'],'Prospective protocol source pin '+name)
    for name,digest in J(FOUR/'SOURCE_PINS.json')['files'].items():C(H(R/name)==digest,'Historical source/evidence pin '+name)
    for path in [OLD/'PREFIT_FREEZE_MANIFEST.json',FOUR/'PREFIT_FREEZE_MANIFEST.json',FIVE/'PREFIT_FREEZE_MANIFEST_V3.json']:
        for row in J(path)['files']:C(H(R/row['path'])==row['sha256'],'Frozen scientific/source identity '+row['path'])
    for row in J(FIVE/'MATHEMATICAL_COPY_PROOF.json')['files']:
        source=checked_path(R/row['source']);target=checked_path(R/row['target'])
        C(H(source)==row['source_sha256'] and H(target)==row['target_sha256'],'Original R5 mathematical source hashes')
        expected=source.read_bytes().replace(b'paper16_development_r4',b'paper16_development_r5').replace(b'P16_R4_JOB',b'P16_R5_JOB') if row['permitted_replacements'] else source.read_bytes()
        C(target.read_bytes()==expected and row['mathematics_unchanged'] is True,'Only frozen R5 mathematical source namespace changes')
    runtime=J(R/'paper16_termination_feasibility1/RUNTIME_IDENTITY.json')
    for name,digest in runtime['files'].items():C(H(R/name)==digest,'Original runtime/binary pin '+name)
    C(H(R/runtime['runtime_executable'])==runtime['python_launcher_sha256'],'Actual Python launcher pin')
    import scipy,h5py,requests
    versions={'Python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__,'h5py':h5py.__version__,'requests':requests.__version__}
    C(versions==runtime['versions'],'Native runtime version identities')
    for path in [FOUR/'RUNTIME_IDENTITY.json',FIVE/'RUNTIME_IDENTITY.json']:
        original_runtime=J(path);C(original_runtime['versions']==versions,'Every historical runtime version identity')
        for name,digest in original_runtime['files'].items():C(H(R/name)==digest,'Historical runtime source/binary identity')
        C(H(R/original_runtime['runtime_executable'])==original_runtime['python_launcher_sha256'],'Historical launcher identity')
    CONTEXT['stage']='FRESH_ALL_PROTECTED_FILE_HASHES'
    old_count=inventory(J(OLD/'PROTECTED_STATE_MANIFEST.json'))
    original=J(FOUR/'PROTECTED_STATE_MANIFEST.json');supplement=J(FOUR/'PROTECTED_STATE_MANIFEST_SUPPLEMENT_1.json')
    C(supplement['original_manifest_sha256']==H(FOUR/'PROTECTED_STATE_MANIFEST.json'),'R4 supplement exact original binding')
    r4_count=inventory({'files':original['files']+supplement['files']},[FOUR/'work',FOUR/'results'])
    C(old_count==10717 and r4_count==33575,'Complete historical protected denominators')
    r5reg=J(E5/'EXTERNAL_CLOSEOUT_REGISTRATION_1.json');r5snapshot=J(FIVE/'EXTERNAL_INTERRUPTION_SNAPSHOT.json');r5stop=J(E5/'EXTERNAL_SCIENTIFIC_STOP.json');r5accept=J(E5/'INDEPENDENT_EXTERNAL_CLOSEOUT_ACCEPTANCE_1.json')
    C(r5reg['base']==r5snapshot['base']==r5stop['base']=='b7bb1227379462c2c7a1cef40ab0d0e99a6d020b','Original R5 mission BASE retained')
    C(r5snapshot['registration']['sha256']==r5stop['registration']['sha256']==r5accept['registration_sha256']==H(E5/'EXTERNAL_CLOSEOUT_REGISTRATION_1.json') and r5stop['snapshot']['sha256']==r5accept['snapshot_sha256']==H(FIVE/'EXTERNAL_INTERRUPTION_SNAPSHOT.json') and r5accept['external_stop_sha256']==H(E5/'EXTERNAL_SCIENTIFIC_STOP.json'),'Original independently reviewed R5 interruption chain')
    C(r5accept['decision']=='ACCEPTED_EXTERNAL_PROCESS_LOSS_CLOSEOUT' and r5accept['open_P0']==r5accept['open_P1']==0 and H(R/r5accept['review_path'])==r5accept['review_sha256'],'Original archive-only R5 independent review retained')
    C(r5snapshot['roots']==r5reg['snapshot_roots']==['paper16_development_r5/work/fits','paper16_development_r5/results'] and r5snapshot['extra_files']==r5reg['snapshot_extra_files'],'Exact full R5 snapshot scope')
    expected5={p.relative_to(R).as_posix() for root in r5snapshot['roots'] for p in walk_files(R/root)}|set(r5snapshot['extra_files'])|{row['path'] for row in r5reg['original_claims']}
    C(expected5=={row['path'] for row in r5snapshot['files']},'Full R5 saved inventory including the ineligible partial')
    r5_count=inventory(r5snapshot);C(r5_count==7505,'Original R5 snapshot denominator')
    C(r5stop['scientific_status']=='STOP_EXECUTION_INTERRUPTED_REQUIRED_GATE' and r5stop['M4_complete'] is False and r5stop['native_worker_exit_code'] is None and r5stop['exact_interruption_UTC'] is None and r5stop['interruption_cause']=='UNDETERMINED_FROM_SAVED_EVIDENCE','Historical R5 STOP and unknown native outcome never cleared')
    for name in r5reg['original_receipts_required_absent']:C(not checked_path(R/name).exists(),'No fabricated original R5 terminal/approval')
    from paper16_development_r3 import models as m3,features as f3,panels
    from paper16_development_r4 import models as m4,features as f4
    from paper16_development_r5 import models as m5,features as f5
    from scipy import optimize
    from paper16_m1.code import spec,dynamics
    with contextlib.ExitStack() as stack:
        for model in [m3,m4,m5]:
            for cls in [model.Objective,model.StationaryObjective]:
                for name in ['analytic','AD']:stack.enter_context(patch.object(cls,name,side_effect=deny))
            for name in ['score']:stack.enter_context(patch.object(model.Objective,name,side_effect=deny))
            for name in ['stationary_score','causal_score']:stack.enter_context(patch.object(model,name,side_effect=deny))
        for mod,names in [(spec,['glm','independent_AD']),(dynamics,['objective','independent_AD'])]:
            for name in names:stack.enter_context(patch.object(mod,name,side_effect=deny))
        stack.enter_context(patch.object(optimize,'minimize',side_effect=deny))
        stack.enter_context(patch.object(socket.socket,'connect',side_effect=deny))
        stack.enter_context(patch.object(socket,'create_connection',side_effect=deny))
        stack.enter_context(patch.object(requests.sessions.Session,'request',side_effect=deny))
        records=sorted([r for r in J(R/'paper16_source_r4/SOURCE_AND_PHYSIOLOGY_ACCOUNT.json')['sources'] if r['selection']['admitted']],key=lambda r:int(r['source']['mouse_id']))
        bymouse={r['source']['mouse_id']:r for r in records};C(len(bymouse)==27,'Original Development mouse identities')
        plan=J(OLD/'results/TASK_PLAN.json');C(plan==panels.task_plan(records,J(OLD/'results/PANEL_PREFIT_PLAN.json')),'Original complete task derivation')
        taskmap={t['id']:t for t in plan['tasks']};C(len(taskmap)==6471,'Original task identities unique')
        selection=J(OLD/'results/B_SELECTION.json');C(selection['selected_lambda']==1.0 and selection['selection_information']=='B1_UNPENALIZED_ONLY','Original historical lambda1 no reselection')
        originjournals={}
        for origin,root,count,attempted_count in [('R3',OLD,952,953),('R4',FOUR,3040,3041),('R5',FIVE,624,625)]:
            journal=Lines(root/'results/FIT_JOURNAL.jsonl');attempts=[r for r in journal if r['event']=='ATTEMPTED'];complete=[r for r in journal if r['event']=='COMPLETED']
            C(len(complete)==len({r['task']['id'] for r in complete})==count,'Original completed journal count '+origin)
            C(len(attempts)==len({r['task']['id'] for r in attempts})==attempted_count,'Original attempt count/no retry '+origin)
            C(all(taskmap[r['task']['id']]==r['task'] for r in journal),'All original journal task identities '+origin)
            active=None;seen=set();failed=0
            for row in journal:
                if row['event']=='ATTEMPTED':
                    C(active is None and row['task']['id'] not in seen,'Original ordered no-retry attempt/terminal join');active=row['task'];seen.add(active['id'])
                else:
                    C(row['event'] in ['COMPLETED','FAILED'] and row['task']==active,'Original terminal closes exact active task');failed+=row['event']=='FAILED';active=None
            expected_active={'R4':'763236014:S02:S:None:11:GLOBAL','R5':'774672366:S01:D:None:11:GLOBAL'}
            C((active is None and failed==1) if origin=='R3' else (active is not None and active['id']==expected_active[origin] and failed==0),'Historical failure/partial retained without admission')
            originjournals[origin]={r['task']['id']:r for r in complete}
        preps={r['key']:r for r in J(OLD/'results/A_PREPROCESSING_STATES.json')};C(len(preps)==215,'All original215 A preparations')
        initializers5=Lines(FIVE/'results/INITIALIZER_IDENTITIES.jsonl')
        C(len(initializers5)==625 and len({row['task_id'] for row in initializers5})==625,'Original R5 initializer ledger including ineligible partial')
        initializers5={row['task_id']:row for row in initializers5}
        observer5=Lines(E5/'INDEPENDENT_R5_M4_NEW_STATE_LEDGER.jsonl')
        C(len(observer5)==624 and H(E5/'INDEPENDENT_R5_M4_NEW_STATE_LEDGER.jsonl')==r5accept['newstate_ledger_sha256'],'Original R5 observer roster is preserved evidence, not new admission')
        observer5={row['task']['id']:row for row in observer5}
        C(set(observer5)==set(originjournals['R5']),'All and only R5 completed candidates; never the partial')
        cache=collections.OrderedDict()
        def getprep(key):
            if key in cache:cache.move_to_end(key);return cache[key]
            row=preps[key];C(row['role']=='A' and checked_path(R/row['path']).is_relative_to(OLD/'work'),'Only frozen saved A preparation path/role before decode');z=receipt(row)
            C(np.all((z['ordinals']>=0)&(z['ordinals']<90)) and np.all(np.diff(z['ordinals'])>0) and np.isfinite(z['raw']).all() and np.isfinite(z['y']).all(),'Original finite A observation support')
            mean=z['raw'].mean((0,1));scale=np.maximum(.25,z['raw'].std((0,1)));active=z['raw'].var((0,1))>1e-12
            mean[:,:row['psth']]=0;scale[:,:row['psth']]=1;active[:,:row['psth']]=True
            C(all(np.array_equal(z[k],a) for k,a in [('mean',mean),('scale',scale),('active',active)]),'Original A-only scaler arithmetic')
            cache[key]=(z,row);COUNTS['prepared_A_receipt_checks']+=1
            if len(cache)>2:cache.popitem(last=False)
            return z,row
        CONTEXT['stage']='ALL_A_PREPARATION_IDENTITIES'
        for key in preps:guard();getprep(key)
        targets=J(P/'REUSE_CANDIDATES.json');recovery=J(P/'RECOVERY_TASK_PLAN.json');optimizer_rows=[];b0_rows=[];maxima={'PG':0.,'AD':0.,'FD':0.}
        C(len(targets['optimizer_targets'])==4616 and len(targets['B0_targets'])==216,'Prospective required audit denominators')
        C(targets['mission']==recovery['mission']==MISSION and targets['base']==recovery['base']==BASE and targets['R6_admitted_count']==0 and targets['audit_executed'] is False,'Frozen R6 candidates never inherit an admission')
        C(H(P/'REUSE_CANDIDATES.json')==registration['targets_sha256'] and H(P/'RECOVERY_TASK_PLAN.json')==registration['task_plan_sha256'],'Candidate/remaining plan registration bindings')
        candidate_ids=[row['task']['id'] for row in targets['optimizer_targets']]
        C(len(set(candidate_ids))==4616 and collections.Counter(row['origin'] for row in targets['optimizer_targets'])=={'R3':952,'R4':3040,'R5':624},'Exact disjoint historical origins')
        C(set(candidate_ids)==set().union(*(set(rows) for rows in originjournals.values())),'Candidates are every exact completed origin and no failed/partial endpoint')
        remaining=[task for task in plan['tasks'] if task['id'] not in set(candidate_ids)]
        C(len(remaining)==1855 and [row['task'] for row in recovery['tasks']]==remaining and remaining==[row['task'] for row in J(PROTO/'RECOVERY_TASK_PLAN.json')['tasks'][624:]],'Independent original-order 1855-task exact difference/suffix proof')
        C(remaining[0]['id']=='774672366:S01:D:None:11:GLOBAL' and recovery['all_original_initialization'] is True and recovery['warm_start_authorized'] is False,'Original initializer only for the retained partial and all remaining tasks')
        for item in targets['optimizer_targets']+targets['B0_targets']:
            C(item['R6_admitted'] is False and item['R6_audit']=='NOT_EXECUTED' and item['R6_numerical_qualification_performed'] is False,'No inherited new scientific qualification')
        for ref in targets['source_metadata'].values():
            path=checked_path(R/ref['path']);C(H(path)==ref['sha256'] and path.stat().st_size==ref['bytes'],'Frozen public candidate metadata identity')
        for index,target in enumerate(targets['optimizer_targets']):
            guard();task=target['task'];CONTEXT.update(stage='OPTIMIZER_STATE',task=task['id']);origin=target['origin'];C(origin in ORIGINS,'Registered origin');root=ORIGINS[origin];COUNTS['optimizer_attempted']+=1
            C(taskmap[task['id']]==task,'Exact logical task from original plan')
            terminal=originjournals[origin][task['id']];folder=root/'work/fits'/hashlib.sha256(task['id'].encode()).hexdigest()
            result=J(folder/'RESULT.json');attempt=J(folder/'ATTEMPT.json');client=J(folder/'CLIENT.json')
            C(target['historical_ftol']==(1e-12 if origin=='R3' else 0.) and target['R6_admitted'] is False,'Frozen target provenance; no prior R6 admission')
            C(terminal['result_path']==target['result_path']==(folder/'RESULT.json').relative_to(R).as_posix() and terminal['result_sha256']==target['result_sha256']==H(folder/'RESULT.json'),'Exact task/terminal/target result identity')
            C(result['task']==attempt['task']==task and attempt['no_retry'] is True and not (folder/'FAILURE.json').exists(),'Original complete attempt identity')
            C(checked_path(R/attempt['bounds']['path'])==folder/'initial.npz' and checked_path(R/result['endpoint_state']['path'])==folder/'endpoint.npz','Same-folder initial and endpoint receipts')
            initial=receipt(attempt['bounds'],['x0','lo','hi']);endpoint=receipt(result['endpoint_state'],['x','gradient'])
            C(all(value.dtype==np.dtype('float64') and np.isfinite(value).all() for value in [*initial.values(),*endpoint.values()]),'Finite original float64 initializer/bounds/endpoint')
            C(all(np.array_equal(client[k],initial[k]) for k in ['x0','lo','hi']),'Actual original CLIENT initializer/bounds')
            z,prep=getprep(task['mouse_id']+'/'+task['panel']);features={'R3':f3,'R4':f4,'R5':f5}[origin];models={'R3':m3,'R4':m4,'R5':m5}[origin]
            batch=features.Batch(**{k:z[k] for k in ['raw','y','ordinals','unit_ids','colors','running_missing','score_mask']},dt=prep['dt'],psth=prep['psth'],b1=prep['b1'],role='A',panel=prep['panel'])
            scaler=features.Scaling(z['mean'],z['scale'],z['active'],prep['psth']);unit=None if task['unit_id'] is None else batch.unit_ids.tolist().index(task['unit_id']);lam=1. if task['lambda']=='GLOBAL' else task['lambda']
            obj=models.Objective(batch,scaler,task['model'],lam,unit,task['seed'])
            C(all(np.array_equal(initial[k],v) for k,v in [('x0',obj.x0),('lo',obj.lo),('hi',obj.hi)]),'Every original initializer/parameter packing/bounds from same A/model/lambda/seed')
            if origin=='R5':
                old_observer=observer5[task['id']];initializer=initializers5[task['id']]
                C(initializer['origin']=='ORIGINAL_FROZEN_CONSTRUCTOR' and initializer['no_warm_start'] is True and all(initializer[k]==ID(initial[k]) for k in ['x0','lo','hi']),'Original R5 initializer ledger identity, no warm-start substitution')
                C(old_observer['completed_receipt']==terminal and old_observer['initializer_identity']==initializer and old_observer['result_sha256']==target['result_sha256'],'R5 original observer/terminal/initializer provenance; still independently reaudited below')
                C({row['path']:row['sha256'] for row in target['recorded_complete_state_files']}=={row['path']:row['sha256'] for row in old_observer['files']},'Complete R5 candidate directory provenance')
                for ref in old_observer['files']:C(H(R/ref['path'])==ref['sha256'] and checked_path(R/ref['path']).stat().st_size==ref['bytes'],'Every original R5 completed directory file identity')
            d,c,errors=cert(folder);C(attempt['parameters']==len(obj.x0)==d['free_coordinates'],'Original parameter dimensions')
            C(H(folder/'DIAGNOSTICS.json')==result['diagnostic_state_sha256'],'Diagnostics exact result binding')
            x,g=endpoint['x'],endpoint['gradient'];C(np.array_equal(x,c['endpoint_x']) and np.array_equal(g,c['endpoint_analytic']) and np.array_equal(x,result['x']) and np.allclose(g,result['jac'],atol=1e-12,rtol=1e-12),'Endpoint/certificate/result exact identity')
            C(np.all(x>=initial['lo']-1e-12) and np.all(x<=initial['hi']+1e-12),'Endpoint original bounds')
            for name in ['initial','halfway','endpoint']:C(np.all(c[name+'_x']>=initial['lo']-1e-12) and np.all(c[name+'_x']<=initial['hi']+1e-12),'Every original checkpoint within original bounds')
            projected=pg(x,g,initial['lo'],initial['hi']);C(projected==result['projected_gradient_inf']==terminal['PG']<=1e-5 and result['numerical_pass'] is True,'Original full outward PG and independent coordinate gates')
            C(result['success'] is True and result['message']=='CONVERGENCE: NORM OF PROJECTED GRADIENT <= PGTOL','Actual retained optimizer termination')
            C(math.isfinite(result['objective']) and result['objective']==result['fun'] and np.isclose(result['fun'],d['checkpoints'][-1]['objective'],atol=1e-10,rtol=1e-12),'Original objective/normalization proof and saved equality')
            fg,nit=journals(folder,result,c,initial,origin);C((folder/'CLIENT_STDERR.log').stat().st_size==0,'No completed optimizer stderr')
            if origin=='R3':C(result['objective']==terminal['objective'] and fg==terminal['calls'] and nit==terminal['iterations'],'Original R3 richer terminal scalar counters')
            row={'task':task,'origin':origin,'historical_ftol':target['historical_ftol'],'status':'INDEPENDENTLY_QUALIFIED','session_id':bymouse[task['mouse_id']]['source']['session_id'],'probe_id':bymouse[task['mouse_id']]['source']['probe_id'],'original_source':bymouse[task['mouse_id']]['source'],'prepared_A_path':prep['path'],'prepared_A_sha256':prep['sha256'],'feature_identity':prep['arrays']['raw'],'mask_identity':prep['arrays']['score_mask'],'unit_identity':prep['arrays']['unit_ids'],'scaler_identities':{k:prep['arrays'][k] for k in ['mean','scale','active']},'result_path':target['result_path'],'result_sha256':H(folder/'RESULT.json'),'initial_sha256':H(folder/'initial.npz'),'coordinate_sha256':d['coordinate_state']['sha256'],'endpoint_sha256':result['endpoint_state']['sha256'],'PG':projected,'AD_error_max':errors['AD'],'fixed_FD_error_max':errors['FD'],'FG_pairs':fg,'accepted_iterations':nit,'parameter_count':len(obj.x0),'lambda_used':lam,'objective':result['objective'],'termination':result['message'],'new_evaluations':0,'counterfactual_execution_equivalence_claimed':False}
            row['R6_admitted']=False;row['R6_admission_pending_independent_matrix_and_production_review']=True
            row['free_coordinate_identity']=ID(obj.free);row['column_identity']=ID(obj.columns)
            row['original_journal_format']='R3 scalar FG + accepted vectors + full coordinate certificate; no derivative reservation journal' if origin=='R3' else origin+' full FG vectors + accepted vectors + full derivative reservation journal'
            optimizer_rows.append(row);append(E/'INDEPENDENT_R6_STATE_LEDGER.jsonl',row);COUNTS[origin]+=1;COUNTS['FG_pairs']+=fg;COUNTS['accepted_iterations']+=nit
            for key,value in [('PG',projected),('AD',errors['AD']),('FD',errors['FD'])]:maxima[key]=max(maxima[key],value)
            if (index+1)%100==0:print(json.dumps({'independent_optimizer_states_checked':index+1,'total':4616,'current_task':task['id']}),flush=True)
        for target in targets['B0_targets']:
            COUNTS['B0_attempted']+=1
            guard();CONTEXT.update(stage='B0_ANALYTIC_CERTIFICATE',task=str(target['mouse_id'])+':B0:'+str(target['unit_id']));folder=OLD/'work/B0'/target['mouse_id']/str(target['unit_id']);result=J(folder/'RESULT.json');d,c,errors=cert(folder)
            z,prep=getprep(target['mouse_id']+'/MAIN');unit=z['unit_ids'].tolist().index(target['unit_id']);counts=np.asarray(z['y'][:,:,unit],dtype=float);total=counts.sum();exposure=np.full(counts.size,prep['dt'],dtype=float).sum();expected=-10. if total==0 else float(np.clip(math.log(total/exposure),-10,10))
            C(all(np.array_equal(c[n+'_x'],[expected]) for n in ['initial','halfway','endpoint']),'B0 original bounded analytic MLE at all3 labelled points')
            projected=pg(c['endpoint_x'],c['endpoint_analytic'],np.array([-10.]),np.array([10.]))
            C(result['unit_id']==target['unit_id'] and result['analytic_MLE_not_optimizer_attempt'] is True and result['numeric_pass'] is True and projected==result['projected_gradient_inf']<=1e-5,'All B0 original identity/PG/AD/fixedFD gates')
            C(H(folder/'RESULT.json')==target['result_sha256'] and target['historical_ftol'] is None and target['origin']=='R3_ANALYTIC' and checked_path(R/target['result_path'])==folder/'RESULT.json','B0 original result target and analytic provenance')
            row={'mouse_id':target['mouse_id'],'unit_id':target['unit_id'],'origin':'R3_ANALYTIC','status':'INDEPENDENTLY_QUALIFIED_ANALYTIC','R6_admitted':False,'historical_ftol':None,'result_path':target['result_path'],'result_sha256':target['result_sha256'],'prepared_A_sha256':prep['sha256'],'coordinate_sha256':d['coordinate_state']['sha256'],'PG':projected,'AD_error_max':errors['AD'],'fixed_FD_error_max':errors['FD'],'new_evaluations':0};b0_rows.append(row);append(E/'INDEPENDENT_R6_B0_LEDGER.jsonl',row);COUNTS['B0_passed']+=1
        C(len(optimizer_rows)==4616 and len(b0_rows)==216 and COUNTS['R3']==952 and COUNTS['R4']==3040 and COUNTS['R5']==624 and COUNTS['optimizer_attempted']==4616 and COUNTS['B0_attempted']==COUNTS['B0_passed']==216,'Complete independent qualification not sampling')
        CONTEXT.update(stage='FINAL_HASH_READBACK',task=None);guard()
        for name,row in HASHES.items():C(H(R/name)==row['sha256'],'Final fresh historical protected readback '+name)
        for name,row in proto_pins.items():C(H(R/name)==row['sha256'],'Final protocol source pin '+name)
        for name,digest in J(FOUR/'SOURCE_PINS.json')['files'].items():C(H(R/name)==digest,'Final historical source pin '+name)
        for path in [OLD/'PREFIT_FREEZE_MANIFEST.json',FOUR/'PREFIT_FREEZE_MANIFEST.json',FIVE/'PREFIT_FREEZE_MANIFEST_V3.json']:
            for row in J(path)['files']:C(H(R/row['path'])==row['sha256'],'Final frozen producer source '+row['path'])
        for name,digest in runtime['files'].items():C(H(R/name)==digest,'Final native runtime source/binary '+name)
        for path in historical_public:frozen_public(path)
        C(public_gates()==gates,'Final public approval/freeze identities unchanged')
        out={'mission':MISSION,'reviewer':'INDEPENDENT_R6_SAVED_REUSE_ORACLE','completed_UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'phase_claim_sha256':CLAIM_SHA,'script_sha256':H(Path(__file__)),'independent_registration_sha256':H(E/'INDEPENDENT_REUSE_AUDIT_REGISTRATION.json'),'independent_qualification_complete':True,'optimizer_states_qualified':4616,'R3_states':952,'R4_states':3040,'R5_states':624,'B0_certificates_qualified':216,'historical_protected_files_checked':old_count,'R4_protected_exact_union_files_checked':r4_count,'R5_full_interruption_snapshot_files_checked':r5_count,'R5_partial_admitted':False,'remaining_tasks':1855,'targets_sha256':registration['targets_sha256'],'task_plan_sha256':registration['task_plan_sha256'],'runtime_versions':versions,'maxima':maxima,'counters':dict(COUNTS),'public_gates':gates,'primary_matrix_reviewed':False,'new_production_reviewed':False,'Phase_A_PASS':False,'E_access':False,'Final_C_D_access':False,'new_objective_gradient_AD_FD_score_optimizer_calls':0,'new_neural_source_requests':0,'historical_files_changed':0,'qualification_not_full_execution_approval':True}
        once(P/'INDEPENDENT_R6_OPTIMIZER_QUALIFICATION.json',{'states':optimizer_rows});once(P/'INDEPENDENT_R6_B0_QUALIFICATION.json',{'states':b0_rows});once(P/'INDEPENDENT_R6_PROTECTED_HASH_READBACK.json',{'files':list(HASHES.values()),'fresh_every_byte_initial_and_final':True});once(E/'INDEPENDENT_R6_REUSE_RESULT.json',out)
        print(json.dumps(out,indent=2),flush=True)

if __name__=='__main__':
    try:
        with patch.object(socket.socket,'connect',side_effect=deny),patch.object(socket.socket,'connect_ex',side_effect=deny),patch.object(socket,'create_connection',side_effect=deny):main()
    except BaseException as exc:
        failure={'mission':MISSION,'scientific_status':'STOP_REUSE_REQUIRED_GATE','recorded_UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'context':CONTEXT,'type':type(exc).__name__,'message':str(exc),'traceback':traceback.format_exc(),'counts_so_far':dict(COUNTS),'remaining_optimizer_unattempted':4616-COUNTS['optimizer_attempted'],'remaining_B0_unattempted':216-COUNTS['B0_attempted'],'automatic_retry':False,'later_states_audited_after_failure':False,'no_substitute_fits_or_certificate_recalculations':True,'private_gate_opened':PRIVATE_ALLOWED}
        if not (E/'INDEPENDENT_R6_AUDIT_FAILURE_1.json').exists():once(E/'INDEPENDENT_R6_AUDIT_FAILURE_1.json',failure)
        print(json.dumps(failure,indent=2),flush=True)
        raise
