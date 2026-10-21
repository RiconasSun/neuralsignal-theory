"""Incremental immutable-completion review; no optimizer/model evaluations."""
import datetime, hashlib, json, math, os, socket, time
from pathlib import Path
from unittest.mock import patch
import numpy as np

R=Path.cwd();P=R/'paper16_development_r4';O=R/'paper16_development_r3'
E=R/'ops/evidence/2026-10-20/p16-m3-m5-uniform-numerical-amendment-r4'
LEDGER=E/'INDEPENDENT_NEW_STATE_AUDIT.jsonl'
VERIFIED_SIGNATURES={}
def J(p):return json.loads(Path(p).read_bytes())
def H(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def C(ok,why):
    if not ok:raise AssertionError(why)
def V(p):
    with np.load(p,allow_pickle=False) as z:return {k:z[k].copy() for k in z.files}
def ID(a):return dict(shape=list(a.shape),dtype=a.dtype.str,sha256=hashlib.sha256(a.tobytes()).hexdigest())
def denied(*a,**k):raise AssertionError('Independent review forbids scientific evaluations/network')
def receipt(ref):
    C(H(R/ref['path'])==ref['sha256'],'state file identity')
    values=V(R/ref['path']);C({k:ID(v) for k,v in values.items()}==ref['arrays'],'state member identity');return values
def rows(path):
    if not path.exists():return []
    raw=path.read_bytes();complete=raw.rsplit(b'\n',1)[0] if not raw.endswith(b'\n') else raw
    return [json.loads(s) for s in complete.splitlines()]
def append(row):
    with LEDGER.open('a',encoding='utf8',newline='\n') as f:
        f.write(json.dumps(row,allow_nan=False)+'\n');f.flush();os.fsync(f.fileno())

def unchanged_files(receipts):
    for row in receipts:
        for item in row.get('files',[]):
            path=R/item['path'];st=path.stat();signature=(st.st_size,st.st_mtime_ns)
            C(st.st_size==item['bytes'],'previously reviewed state size changed')
            if VERIFIED_SIGNATURES.get(item['path'])!=signature:
                C(H(path)==item['sha256'],'previously reviewed state bytes changed')
                VERIFIED_SIGNATURES[item['path']]=signature

def run(seconds=55):
    from paper16_termination_feasibility1.reproduce import check_fit
    from paper16_development_r4 import models,features
    from paper16_development_r4.core import spec,dynamics
    from scipy import optimize
    freeze=P/'PREFIT_FREEZE_MANIFEST.json';fhash=H(freeze)
    C(fhash=='37b40a80af9eab485ea5817b92fb77e4b3cf64e1245a6e79b9183904278183b0','frozen production identity')
    for row in J(freeze)['files']:C(H(R/row['path'])==row['sha256'],'production freeze changed')
    planned={t['id']:t for t in J(P/'NEW_TASK_PLAN_CANDIDATE.json')['tasks']}
    preps={r['key']:r for r in J(O/'results/A_PREPROCESSING_STATES.json')}
    if LEDGER.exists():C(LEDGER.read_bytes().endswith(b'\n'),'torn independent receipt ledger preserved; no silent append')
    seen=rows(LEDGER);unchanged_files(seen);done_ids={r['task_id'] for r in seen if r['event']=='INDEPENDENT_COMPLETED_STATE_ACCEPTED'}
    C(len(done_ids)==sum(r['event']=='INDEPENDENT_COMPLETED_STATE_ACCEPTED' for r in seen),'independent receipt duplicates')
    chain=hashlib.sha256(LEDGER.read_bytes()).hexdigest() if LEDGER.exists() else None
    cache={};started=time.monotonic();new=0;signal=None
    with patch.object(models.Objective,'analytic',side_effect=denied),patch.object(models.Objective,'AD',side_effect=denied),patch.object(models.Objective,'score',side_effect=denied),patch.object(spec,'glm',side_effect=denied),patch.object(spec,'independent_AD',side_effect=denied),patch.object(dynamics,'objective',side_effect=denied),patch.object(dynamics,'independent_AD',side_effect=denied),patch.object(optimize,'minimize',side_effect=denied),patch.object(socket.socket,'connect',side_effect=denied):
        while True:
            journal=rows(P/'results/FIT_JOURNAL.jsonl');completed=[r for r in journal if r['event']=='COMPLETED'];attempts=[r for r in journal if r['event']=='ATTEMPTED'];att={r['task']['id']:r for r in attempts}
            C(len(att)==len(attempts) and len({r['task']['id'] for r in completed})==len(completed),'production no duplicate attempts/completions')
            for name in ['SCIENTIFIC_STOP.json','SUPERVISION.json','M4_READY_FOR_INDEPENDENT_REVIEW.json']:
                if (P/'results'/name).exists():signal=name;break
            if signal:break
            for terminal in completed:
                task=terminal['task'];tid=task['id']
                if tid in done_ids:continue
                C(planned.get(tid)==task and att[tid]['task']==task and att[tid]['ftol']==0.,'exact task/policy/attempt')
                folder=P/'work/fits'/hashlib.sha256(tid.encode()).hexdigest();result=J(folder/'RESULT.json');attempt=J(folder/'ATTEMPT.json');client=J(folder/'CLIENT.json')
                C(result['task']==attempt['task']==task and attempt['no_retry'] and not (folder/'FAILURE.json').exists(),'completed task no failure/retry')
                C(terminal['result_path']==(folder/'RESULT.json').relative_to(R).as_posix() and terminal['result_sha256']==H(folder/'RESULT.json'),'completed result exact path/hash')
                initial=receipt(attempt['bounds']);endpoint=receipt(result['endpoint_state'])
                C(all(np.array_equal(client[k],initial[k]) for k in ['x0','lo','hi']),'actual client initializer')
                key=task['mouse_id']+'/'+task['panel'];prep=preps[key]
                if key not in cache:
                    z=receipt(prep);C(prep['role']=='A' and np.all((z['ordinals']>=0)&(z['ordinals']<90)),'A preparation domain')
                    batch=features.Batch(**{k:z[k] for k in ['raw','y','ordinals','unit_ids','colors','running_missing','score_mask']},dt=prep['dt'],psth=prep['psth'],b1=prep['b1'],role='A',panel=prep['panel'])
                    cache[key]=(batch,features.Scaling(z['mean'],z['scale'],z['active'],prep['psth']))
                batch,scaler=cache[key];unit=None if task['unit_id'] is None else batch.unit_ids.tolist().index(task['unit_id']);obj=models.Objective(batch,scaler,task['model'],1.,unit,task['seed'])
                C(all(np.array_equal(initial[k],v) for k,v in [('x0',obj.x0),('lo',obj.lo),('hi',obj.hi)]),'original A/model/seed initialization and packing/bounds')
                C(attempt['parameters']==len(obj.x0),'parameter count')
                r,coords=check_fit(folder);C(r['numerical_pass'] and terminal['PG']==r['projected_gradient_inf']<=1e-5,'all numerical gates')
                C(r['external_value_gradient_pairs']==r['nfev']<=6000 and r['external_accepted_iterations']==r['nit']<=1500,'all external counters')
                C((folder/'CLIENT_STDERR.log').stat().st_size==0,'completed solver stderr')
                d=J(folder/'DIAGNOSTICS.json');cert=receipt(d['coordinate_state'])
                C(np.array_equal(endpoint['x'],cert['endpoint_x']) and np.array_equal(endpoint['gradient'],cert['endpoint_analytic']),'endpoint member identities')
                # Bind every immutable numerical artifact, not only RESULT.
                files=[dict(path=x.relative_to(R).as_posix(),bytes=x.stat().st_size,sha256=H(x)) for x in sorted(folder.iterdir()) if x.is_file()]
                for item in files:
                    stat=(R/item['path']).stat();VERIFIED_SIGNATURES[item['path']]=(stat.st_size,stat.st_mtime_ns)
                row=dict(event='INDEPENDENT_COMPLETED_STATE_ACCEPTED',reviewer='/root/r4_reuse_review',reviewed_UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),task_id=tid,task=task,ftol=0.,parameter_count=len(obj.x0),objective=r['objective'],PG=r['projected_gradient_inf'],AD_error_max=max(c['AD_scaled_coordinate_error_max'] for c in d['checkpoints']),fixed_FD_error_max=max(c['frozen_FD_scaled_error'] for c in d['checkpoints']),FG_pairs=r['nfev'],accepted_iterations=r['nit'],termination=r['message'],optimizer_success=r['success'],prepared_A_path=prep['path'],prepared_A_sha256=prep['sha256'],prefit_manifest_sha256=fhash,scientific_stage_sha256=H(P/'results/STAGE_CLAIM.json'),files=files,new_optimizer_calls=0,new_likelihood_derivative_score_calls=0,B_E_Final_access=False,complete_M4_approval=False,previous_ledger_sha256=chain)
                append(row);chain=H(LEDGER);done_ids.add(tid);new+=1
            for name in ['SCIENTIFIC_STOP.json','SUPERVISION.json','M4_READY_FOR_INDEPENDENT_REVIEW.json']:
                if (P/'results'/name).exists():signal=name;break
            if signal or time.monotonic()-started>=seconds:break
            time.sleep(min(5,max(.01,seconds-(time.monotonic()-started))))
    out=dict(independent_completed_states_total=len(done_ids),newly_checked=new,production_completed_snapshot=len(completed),production_attempted_snapshot=len(attempts),signal=signal,ledger_sha256=H(LEDGER) if LEDGER.exists() else None,new_scientific_calls=0,complete_M4_approval=False)
    print(json.dumps(out),flush=True)
    with (E/'INDEPENDENT_NEW_REVIEW_PROGRESS.jsonl').open('a',encoding='utf8',newline='\n') as f:
        f.write(json.dumps(dict(recorded_UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),**out))+'\n');f.flush();os.fsync(f.fileno())
    return out
if __name__=='__main__':run()
