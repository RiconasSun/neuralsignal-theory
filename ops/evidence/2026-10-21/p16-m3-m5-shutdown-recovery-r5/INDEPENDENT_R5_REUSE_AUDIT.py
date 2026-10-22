"""One complete independent R5 saved-evidence qualification; no evaluations."""
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
from pathlib import Path
from unittest.mock import patch

import numpy as np

R = Path.cwd()
P = R / 'paper16_development_r5'
E = R / 'ops/evidence/2026-10-21/p16-m3-m5-shutdown-recovery-r5'
PROTO = R / 'paper16_shutdown_recovery_r5_protocol'
OLD = R / 'paper16_development_r3'
FOUR = R / 'paper16_development_r4'
BASE = 'b7bb1227379462c2c7a1cef40ab0d0e99a6d020b'
CONTEXT = {'stage':'NOT_STARTED','task':None}
COUNTS = collections.Counter()
HASHES = {}
CLAIM_SHA = None

def J(path):
    return json.loads(Path(path).read_bytes())

def H(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream,'sha256').hexdigest()

def C(ok, message):
    if not ok:
        raise AssertionError(message)

def once(path, value):
    with Path(path).open('x',encoding='utf8',newline='\n') as stream:
        json.dump(value,stream,indent=2,allow_nan=False);stream.write('\n')
        stream.flush();os.fsync(stream.fileno())

def append(path, value):
    with Path(path).open('a',encoding='utf8',newline='\n') as stream:
        stream.write(json.dumps(value,allow_nan=False)+'\n');stream.flush();os.fsync(stream.fileno())

def guard():
    claim=J(P/'PHASE_A_CLAIM.json')
    C(H(P/'PHASE_A_CLAIM.json')==CLAIM_SHA,'Original Phase A claim hash changed')
    C(claim['no_reset'] is True and abs(claim['deadline_monotonic']-claim['start_monotonic']-86400)<=1e-6,'One original24h phase claim')
    C(time.monotonic()<claim['deadline_monotonic'],'Phase A monotonic deadline')
    C(datetime.datetime.now(datetime.timezone.utc)<datetime.datetime.fromisoformat(claim['deadline_UTC']),'Phase A UTC deadline')

def Lines(path, optional=False):
    path=Path(path)
    if optional and not path.exists():return []
    raw=path.read_bytes();C(not raw or raw.endswith(b'\n'),'Torn saved journal: '+str(path))
    return [json.loads(line) for line in raw.splitlines()]

def ID(a):
    return {'shape':list(a.shape),'dtype':a.dtype.str,'sha256':hashlib.sha256(a.tobytes()).hexdigest()}

def receipt(ref):
    path=R/ref['path'];C(H(path)==ref['sha256'],'Array receipt SHA: '+ref['path'])
    with np.load(path,allow_pickle=False) as archive:values={k:archive[k].copy() for k in archive.files}
    C({k:ID(v) for k,v in values.items()}==ref['arrays'],'Every array receipt member: '+ref['path'])
    return values

def inventory(manifest, exact_roots=None):
    rows=manifest['files'];by={row['path']:row for row in rows}
    C(len(by)==len(rows),'No duplicate inventory rows')
    if exact_roots:
        actual={p.relative_to(R).as_posix() for root in exact_roots for p in root.rglob('*') if p.is_file()}
        C(actual==set(by),'Exact protected inventory union fileset')
    for index,(name,row) in enumerate(by.items()):
        path=R/name;C(path.is_file() and not path.is_symlink(),'Protected regular file '+name)
        digest=H(path);C(digest==row['sha256'],'Fresh protected SHA '+name)
        if 'bytes' in row:C(path.stat().st_size==row['bytes'],'Protected size '+name)
        HASHES[name]={'path':name,'bytes':path.stat().st_size,'sha256':digest}
        if index%1000==0:guard()
    return len(by)

def cert(folder):
    d=J(folder/'DIAGNOSTICS.json');v=receipt(d['coordinate_state']);p=d['free_coordinates']
    C(type(p) is int and p>0,'Certificate parameter count')
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
    calls=Lines(folder/'CALLS.jsonl');accepted=Lines(folder/'ACCEPTED.jsonl',True)
    n=result['nfev'];nit=result['nit'];p=len(initial['x0'])
    C(type(n) is int and type(nit) is int and len(calls)==2*n and n==result['external_value_gradient_pairs']<=6000,'Full FG journal counts/cap')
    C(len(accepted)==nit==result['external_accepted_iterations']==result['accepted_vector_count']<=1500,'Full accepted journal counts/cap')
    assoc={}
    for i in range(n):
        a,b=calls[2*i:2*i+2]
        C(a['event']=='RESERVED_BEFORE_EVALUATION' and b['event']=='COMPLETED' and a['call']==b['call']==i+1,'FG strict alternating reservations/completions')
        C(type(a['iterations']) is int and 0<=a['iterations']<=nit and math.isfinite(b['objective']) and math.isfinite(b['gradient_inf']),'Original finite FG journal scalars')
        if origin=='R4':
            x=np.asarray(a['x']);g=np.asarray(b['gradient'])
            C(x.shape==g.shape==(p,) and np.isfinite(x).all() and np.isfinite(g).all() and b['gradient_inf']==float(np.abs(g).max()),'Finite actual R4 FG vectors/norm')
            C(np.all(x>=initial['lo']-1e-12) and np.all(x<=initial['hi']+1e-12),'Actual R4 FG vector within original bounds')
        else:
            C('x' not in a and 'gradient' not in b,'Preserve original R3 scalar-only FG format without inventing vectors')
        assoc[a['iterations']]=(a,b)
    for i,row in enumerate(accepted):
        x=np.asarray(row['x']);C(row['iteration']==i+1 and x.shape==(p,) and np.isfinite(x).all() and np.all(x>=initial['lo']-1e-12) and np.all(x<=initial['hi']+1e-12),'Accepted iteration vector/bounds/order')
        if origin=='R4':C(np.array_equal(x,assoc[i][0]['x']),'Every R4 accepted vector equals actual broker FG')
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
    global CLAIM_SHA
    registration=J(E/'INDEPENDENT_REUSE_AUDIT_REGISTRATION.json')
    C(registration['script_sha256']==H(Path(__file__)),'Registered independent script bytes')
    CLAIM_SHA=registration['phase_A_claim_sha256'];guard()
    C(subprocess.check_output(['git','rev-parse','HEAD']).decode().strip()==BASE,'Exact authorized execution BASE')
    CONTEXT['stage']='FROZEN_SOURCE_AND_RUNTIME_IDENTITIES'
    proto_pins=J(PROTO/'SOURCE_PINS.json')['files']
    for name,row in proto_pins.items():C(H(R/name)==row['sha256'] and (R/name).stat().st_size==row['bytes'],'Prospective protocol source pin '+name)
    for name,digest in J(FOUR/'SOURCE_PINS.json')['files'].items():C(H(R/name)==digest,'Historical source/evidence pin '+name)
    for path in [OLD/'PREFIT_FREEZE_MANIFEST.json',FOUR/'PREFIT_FREEZE_MANIFEST.json']:
        for row in J(path)['files']:C(H(R/row['path'])==row['sha256'],'Frozen scientific/source identity '+row['path'])
    runtime=J(R/'paper16_termination_feasibility1/RUNTIME_IDENTITY.json')
    for name,digest in runtime['files'].items():C(H(R/name)==digest,'Original runtime/binary pin '+name)
    C(H(R/runtime['runtime_executable'])==runtime['python_launcher_sha256'],'Actual Python launcher pin')
    import scipy,h5py,requests
    versions={'Python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__,'h5py':h5py.__version__,'requests':requests.__version__}
    C(versions==runtime['versions'],'Native runtime version identities')
    CONTEXT['stage']='FRESH_ALL_PROTECTED_FILE_HASHES'
    old_count=inventory(J(OLD/'PROTECTED_STATE_MANIFEST.json'))
    original=J(FOUR/'PROTECTED_STATE_MANIFEST.json');supplement=J(FOUR/'PROTECTED_STATE_MANIFEST_SUPPLEMENT_1.json')
    C(supplement['original_manifest_sha256']==H(FOUR/'PROTECTED_STATE_MANIFEST.json'),'R4 supplement exact original binding')
    r4_count=inventory({'files':original['files']+supplement['files']},[FOUR/'work',FOUR/'results'])
    C(old_count==10717 and r4_count==33575,'Complete historical protected denominators')
    from paper16_development_r3 import models as m3,features as f3,panels
    from paper16_development_r4 import models as m4,features as f4
    from scipy import optimize
    from paper16_m1.code import spec,dynamics
    with contextlib.ExitStack() as stack:
        for model in [m3,m4]:
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
        for origin,root,count in [('R3',OLD,952),('R4',FOUR,3040)]:
            journal=Lines(root/'results/FIT_JOURNAL.jsonl');attempts=[r for r in journal if r['event']=='ATTEMPTED'];complete=[r for r in journal if r['event']=='COMPLETED']
            C(len(complete)==len({r['task']['id'] for r in complete})==count,'Original completed journal count '+origin)
            C(len(attempts)==len({r['task']['id'] for r in attempts})==(953 if origin=='R3' else 3041),'Original attempt count/no retry '+origin)
            C(all(taskmap[r['task']['id']]==r['task'] for r in journal),'All original journal task identities '+origin)
            active=None;seen=set();failed=0
            for row in journal:
                if row['event']=='ATTEMPTED':
                    C(active is None and row['task']['id'] not in seen,'Original ordered no-retry attempt/terminal join');active=row['task'];seen.add(active['id'])
                else:
                    C(row['event'] in ['COMPLETED','FAILED'] and row['task']==active,'Original terminal closes exact active task');failed+=row['event']=='FAILED';active=None
            C((active is None and failed==1) if origin=='R3' else (active['id']=='763236014:S02:S:None:11:GLOBAL' and failed==0),'Historical failure/partial retained without admission')
            originjournals[origin]={r['task']['id']:r for r in complete}
        preps={r['key']:r for r in J(OLD/'results/A_PREPROCESSING_STATES.json')};C(len(preps)==215,'All original215 A preparations')
        cache=collections.OrderedDict()
        def getprep(key):
            if key in cache:cache.move_to_end(key);return cache[key]
            row=preps[key];z=receipt(row);C(row['role']=='A','Only saved A preparation decode')
            C(np.all((z['ordinals']>=0)&(z['ordinals']<90)) and np.all(np.diff(z['ordinals'])>0) and np.isfinite(z['raw']).all() and np.isfinite(z['y']).all(),'Original finite A observation support')
            mean=z['raw'].mean((0,1));scale=np.maximum(.25,z['raw'].std((0,1)));active=z['raw'].var((0,1))>1e-12
            mean[:,:row['psth']]=0;scale[:,:row['psth']]=1;active[:,:row['psth']]=True
            C(all(np.array_equal(z[k],a) for k,a in [('mean',mean),('scale',scale),('active',active)]),'Original A-only scaler arithmetic')
            cache[key]=(z,row);COUNTS['prepared_A_receipt_checks']+=1
            if len(cache)>2:cache.popitem(last=False)
            return z,row
        CONTEXT['stage']='ALL_A_PREPARATION_IDENTITIES'
        for key in preps:guard();getprep(key)
        targets=J(PROTO/'REUSE_TARGETS.json');optimizer_rows=[];b0_rows=[];maxima={'PG':0.,'AD':0.,'FD':0.}
        C(len(targets['optimizer_targets'])==3992 and len(targets['B0_targets'])==216,'Prospective required audit denominators')
        for index,target in enumerate(targets['optimizer_targets']):
            guard();task=target['task'];CONTEXT.update(stage='OPTIMIZER_STATE',task=task['id']);origin=target['origin'];root=OLD if origin=='R3' else FOUR
            C(taskmap[task['id']]==task,'Exact logical task from original plan')
            terminal=originjournals[origin][task['id']];folder=root/'work/fits'/hashlib.sha256(task['id'].encode()).hexdigest()
            result=J(folder/'RESULT.json');attempt=J(folder/'ATTEMPT.json');client=J(folder/'CLIENT.json')
            C(target['historical_ftol']==(1e-12 if origin=='R3' else 0.) and target['R5_admitted'] is False,'Frozen target provenance; no prior R5 admission')
            C(terminal['result_path']==target['result_path']==(folder/'RESULT.json').relative_to(R).as_posix() and terminal['result_sha256']==target['result_sha256']==H(folder/'RESULT.json'),'Exact task/terminal/target result identity')
            C(result['task']==attempt['task']==task and attempt['no_retry'] is True and not (folder/'FAILURE.json').exists(),'Original complete attempt identity')
            initial=receipt(attempt['bounds']);endpoint=receipt(result['endpoint_state'])
            C(all(np.array_equal(client[k],initial[k]) for k in ['x0','lo','hi']),'Actual original CLIENT initializer/bounds')
            z,prep=getprep(task['mouse_id']+'/'+task['panel']);features=f3 if origin=='R3' else f4;models=m3 if origin=='R3' else m4
            batch=features.Batch(**{k:z[k] for k in ['raw','y','ordinals','unit_ids','colors','running_missing','score_mask']},dt=prep['dt'],psth=prep['psth'],b1=prep['b1'],role='A',panel=prep['panel'])
            scaler=features.Scaling(z['mean'],z['scale'],z['active'],prep['psth']);unit=None if task['unit_id'] is None else batch.unit_ids.tolist().index(task['unit_id']);lam=1. if task['lambda']=='GLOBAL' else task['lambda']
            obj=models.Objective(batch,scaler,task['model'],lam,unit,task['seed'])
            C(all(np.array_equal(initial[k],v) for k,v in [('x0',obj.x0),('lo',obj.lo),('hi',obj.hi)]),'Every original initializer/parameter packing/bounds from same A/model/lambda/seed')
            d,c,errors=cert(folder);C(attempt['parameters']==len(obj.x0)==d['free_coordinates'],'Original parameter dimensions')
            C(H(folder/'DIAGNOSTICS.json')==result['diagnostic_state_sha256'],'Diagnostics exact result binding')
            x,g=endpoint['x'],endpoint['gradient'];C(np.array_equal(x,c['endpoint_x']) and np.array_equal(g,c['endpoint_analytic']) and np.array_equal(x,result['x']) and np.allclose(g,result['jac'],atol=1e-12,rtol=1e-12),'Endpoint/certificate/result exact identity')
            C(np.all(x>=initial['lo']-1e-12) and np.all(x<=initial['hi']+1e-12),'Endpoint original bounds')
            projected=pg(x,g,initial['lo'],initial['hi']);C(projected==result['projected_gradient_inf']==terminal['PG']<=1e-5 and result['numerical_pass'] is True,'Original full outward PG and independent coordinate gates')
            C(result['success'] is True and result['message']=='CONVERGENCE: NORM OF PROJECTED GRADIENT <= PGTOL','Actual retained optimizer termination')
            C(math.isfinite(result['objective']) and result['objective']==result['fun'] and np.isclose(result['fun'],d['checkpoints'][-1]['objective'],atol=1e-10,rtol=1e-12),'Original objective/normalization proof and saved equality')
            fg,nit=journals(folder,result,c,initial,origin);C((folder/'CLIENT_STDERR.log').stat().st_size==0,'No completed optimizer stderr')
            if origin=='R3':C(result['objective']==terminal['objective'] and fg==terminal['calls'] and nit==terminal['iterations'],'Original R3 richer terminal scalar counters')
            row={'task':task,'origin':origin,'historical_ftol':target['historical_ftol'],'status':'INDEPENDENTLY_QUALIFIED','session_id':bymouse[task['mouse_id']]['source']['session_id'],'probe_id':bymouse[task['mouse_id']]['source']['probe_id'],'original_source':bymouse[task['mouse_id']]['source'],'prepared_A_path':prep['path'],'prepared_A_sha256':prep['sha256'],'feature_identity':prep['arrays']['raw'],'mask_identity':prep['arrays']['score_mask'],'unit_identity':prep['arrays']['unit_ids'],'scaler_identities':{k:prep['arrays'][k] for k in ['mean','scale','active']},'result_path':target['result_path'],'result_sha256':H(folder/'RESULT.json'),'initial_sha256':H(folder/'initial.npz'),'coordinate_sha256':d['coordinate_state']['sha256'],'endpoint_sha256':result['endpoint_state']['sha256'],'PG':projected,'AD_error_max':errors['AD'],'fixed_FD_error_max':errors['FD'],'FG_pairs':fg,'accepted_iterations':nit,'parameter_count':len(obj.x0),'lambda_used':lam,'objective':result['objective'],'termination':result['message'],'new_evaluations':0,'counterfactual_execution_equivalence_claimed':False}
            row['original_journal_format']='R3 scalar FG + accepted vectors + full coordinate certificate; no derivative reservation journal' if origin=='R3' else 'R4 full FG vectors + accepted vectors + full derivative reservation journal'
            optimizer_rows.append(row);append(E/'INDEPENDENT_R5_STATE_LEDGER.jsonl',row);COUNTS[origin]+=1;COUNTS['FG_pairs']+=fg;COUNTS['accepted_iterations']+=nit
            for key,value in [('PG',projected),('AD',errors['AD']),('FD',errors['FD'])]:maxima[key]=max(maxima[key],value)
            if (index+1)%100==0:print(json.dumps({'independent_optimizer_states_checked':index+1,'total':3992,'current_task':task['id']}),flush=True)
        for target in targets['B0_targets']:
            guard();CONTEXT.update(stage='B0_ANALYTIC_CERTIFICATE',task=str(target['mouse_id'])+':B0:'+str(target['unit_id']));folder=OLD/'work/B0'/target['mouse_id']/str(target['unit_id']);result=J(folder/'RESULT.json');d,c,errors=cert(folder)
            z,prep=getprep(target['mouse_id']+'/MAIN');unit=z['unit_ids'].tolist().index(target['unit_id']);counts=np.asarray(z['y'][:,:,unit],dtype=float);total=counts.sum();exposure=np.full(counts.size,prep['dt'],dtype=float).sum();expected=-10. if total==0 else float(np.clip(math.log(total/exposure),-10,10))
            C(all(np.array_equal(c[n+'_x'],[expected]) for n in ['initial','halfway','endpoint']),'B0 original bounded analytic MLE at all3 labelled points')
            projected=pg(c['endpoint_x'],c['endpoint_analytic'],np.array([-10.]),np.array([10.]))
            C(result['unit_id']==target['unit_id'] and result['analytic_MLE_not_optimizer_attempt'] is True and result['numeric_pass'] is True and projected==result['projected_gradient_inf']<=1e-5,'All B0 original identity/PG/AD/fixedFD gates')
            C(H(folder/'RESULT.json')==target['result_sha256'] and target['historical_ftol'] is None,'B0 original result target and analytic provenance')
            row={'mouse_id':target['mouse_id'],'unit_id':target['unit_id'],'status':'INDEPENDENTLY_QUALIFIED_ANALYTIC','historical_ftol':None,'result_path':target['result_path'],'result_sha256':target['result_sha256'],'prepared_A_sha256':prep['sha256'],'coordinate_sha256':d['coordinate_state']['sha256'],'PG':projected,'AD_error_max':errors['AD'],'fixed_FD_error_max':errors['FD'],'new_evaluations':0};b0_rows.append(row);append(E/'INDEPENDENT_R5_B0_LEDGER.jsonl',row)
        C(len(optimizer_rows)==3992 and len(b0_rows)==216 and COUNTS['R3']==952 and COUNTS['R4']==3040,'Complete independent qualification not sampling')
        CONTEXT.update(stage='FINAL_HASH_READBACK',task=None);guard()
        for name,row in HASHES.items():C(H(R/name)==row['sha256'],'Final fresh historical protected readback '+name)
        for name,row in proto_pins.items():C(H(R/name)==row['sha256'],'Final protocol source pin '+name)
        for name,digest in J(FOUR/'SOURCE_PINS.json')['files'].items():C(H(R/name)==digest,'Final historical source pin '+name)
        for path in [OLD/'PREFIT_FREEZE_MANIFEST.json',FOUR/'PREFIT_FREEZE_MANIFEST.json']:
            for row in J(path)['files']:C(H(R/row['path'])==row['sha256'],'Final frozen producer source '+row['path'])
        for name,digest in runtime['files'].items():C(H(R/name)==digest,'Final native runtime source/binary '+name)
        out={'mission':'P16-M3-M5-SHUTDOWN-RECOVERY-R5','reviewer':'/root/r4_interruption_review','completed_UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'phase_A_claim_sha256':CLAIM_SHA,'script_sha256':H(Path(__file__)),'independent_qualification_complete':True,'optimizer_states_qualified':3992,'R3_states':952,'R4_states':3040,'B0_certificates_qualified':216,'historical_protected_files_checked':old_count,'R4_protected_exact_union_files_checked':r4_count,'runtime_versions':versions,'maxima':maxima,'counters':dict(COUNTS),'primary_matrix_reviewed':False,'new_production_reviewed':False,'Phase_A_PASS':False,'E_access':False,'Final_C_D_access':False,'new_objective_gradient_AD_FD_score_optimizer_calls':0,'new_neural_source_requests':0,'historical_files_changed':0,'qualification_not_full_execution_approval':True}
        once(P/'INDEPENDENT_R5_OPTIMIZER_QUALIFICATION.json',{'states':optimizer_rows});once(P/'INDEPENDENT_R5_B0_QUALIFICATION.json',{'states':b0_rows});once(P/'INDEPENDENT_R5_PROTECTED_HASH_READBACK.json',{'files':list(HASHES.values()),'fresh_every_byte_initial_and_final':True});once(E/'INDEPENDENT_R5_REUSE_RESULT.json',out)
        print(json.dumps(out,indent=2),flush=True)

if __name__=='__main__':
    try:main()
    except BaseException as exc:
        failure={'recorded_UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'context':CONTEXT,'type':type(exc).__name__,'message':str(exc),'traceback':traceback.format_exc(),'counts_so_far':dict(COUNTS),'automatic_retry':False,'later_states_audited_after_failure':False}
        once(E/'INDEPENDENT_R5_AUDIT_FAILURE_1.json',failure)
        print(json.dumps(failure,indent=2),flush=True)
        raise
