"""Independent saved-certificate admission check; never evaluates a model."""
import collections, hashlib, json, math, platform, socket
from pathlib import Path
from unittest.mock import patch
import numpy as np

R = Path.cwd(); P = R/'paper16_development_r4'; O = R/'paper16_development_r3'
E = R/'ops/evidence/2026-10-20/p16-m3-m5-uniform-numerical-amendment-r4'
def J(p): return json.loads(Path(p).read_bytes())
def H(p):
    with Path(p).open('rb') as f: return hashlib.file_digest(f,'sha256').hexdigest()
def C(ok,why):
    if not ok: raise AssertionError(why)
def A(p):
    with np.load(p,allow_pickle=False) as z:return {k:z[k].copy() for k in z.files}
def ID(a):return dict(shape=list(a.shape),dtype=a.dtype.str,sha256=hashlib.sha256(a.tobytes()).hexdigest())
def denied(*a,**k):raise AssertionError('Forbidden optimizer/model/network evaluation')
def Lines(p):return [json.loads(s) for s in p.read_text().splitlines()]
def CheckReceipt(receipt):
    C(H(R/receipt['path'])==receipt['sha256'],'receipt hash')
    v=A(R/receipt['path']);C({k:ID(a) for k,a in v.items()}==receipt['arrays'],'receipt members');return v
def Cert(folder):
    d=J(folder/'DIAGNOSTICS.json');v=CheckReceipt(d['coordinate_state']);p=d['free_coordinates']
    C((d['FD_objective_calls'],d['AD_calls'],d['analytic_checkpoint_calls'])==(24*p,3,3),'budgets')
    C(len(d['checkpoints'])==3 and d['all_checkpoints_pass'] and d['FD_step_not_selected_post_result'],'certificate structure')
    am=fm=0.
    for name,row in zip(['initial','halfway','endpoint'],d['checkpoints']):
        x,g,ad=[v[name+s] for s in ['_x','_analytic','_AD']]
        C(all(z.shape==(p,) and np.isfinite(z).all() for z in [x,g,ad]),'coordinate finiteness')
        err=np.abs(g-ad)/np.maximum(1,np.maximum(np.abs(g),np.abs(ad)))
        C(np.array_equal(err,v[name+'_AD_error']) and float(err.max())==row['AD_scaled_coordinate_error_max']<=1e-8,'AD arithmetic')
        for h in [.001,.0001,.00001,.000001]:
            fd=v[name+'_FD_'+str(h)];de=np.abs(fd-g)/np.maximum(1,np.maximum(np.abs(fd),np.abs(g)))
            C(fd.shape==(p,) and np.isfinite(fd).all() and np.array_equal(de,v[name+'_FD_error_'+str(h)]) and float(de.max())==row['FD_scaled_coordinate_errors'][str(h)],'FD arithmetic')
        C(row['checkpoint']==name and row['pass'] and row['frozen_FD_scaled_error']==row['FD_scaled_coordinate_errors']['1e-05']<=2e-5,'fixed FD')
        C(math.isfinite(row['objective']) and math.isfinite(row['AD_objective']) and np.isclose(row['objective'],row['AD_objective'],atol=1e-10,rtol=1e-12),'objective oracle agreement')
        am=max(am,float(err.max()));fm=max(fm,row['frozen_FD_scaled_error'])
    return d,v,am,fm
def PG(x,g,lo,hi):return float(np.abs(np.where(((x<=lo+1e-12)&(g>0))|((x>=hi-1e-12)&(g<0)),0,g)).max())

def run():
    # Identity proof includes all original private files, not merely admitted endpoints.
    pin=J(P/'SOURCE_PINS.json')['files']
    for p,h in pin.items():C(H(R/p)==h,'source pin '+p)
    old=J(O/'PROTECTED_STATE_MANIFEST.json')['files']
    for r in old:C(H(R/r['path'])==r['sha256'] and (R/r['path']).stat().st_size==r['bytes'],'old state hash')
    freeze=J(P/'AUDIT_CODE_FREEZE.json')
    for r in freeze['files']:C(H(R/r['path'])==r['sha256'],'prospective freeze')
    prod=J(O/'PRODUCTION_NUMERICAL_CERTIFICATION.json')
    C(prod['mandatory_tests_pass'] and prod['real_fits_executed']==0,'historical prefit certification')
    for p,h in prod['candidate_source_hashes'].items():C(H(R/p)==h,'historical tested source')
    rt=J(R/'paper16_termination_feasibility1/RUNTIME_IDENTITY.json')
    for p,h in rt['files'].items():C(H(R/p)==h,'native runtime hash')
    C(H(R/rt['runtime_executable'])==rt['python_launcher_sha256'],'runtime launcher')
    import scipy,h5py,requests
    versions=dict(Python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__,h5py=h5py.__version__,requests=requests.__version__)
    C(versions==rt['versions']==prod['runtime'],'native versions')
    from paper16_development_r3 import models,features,panels
    from paper16_development_r3.core import spec,dynamics
    from scipy import optimize
    with patch.object(models.Objective,'analytic',side_effect=denied),patch.object(models.Objective,'AD',side_effect=denied),patch.object(models.Objective,'score',side_effect=denied),patch.object(spec,'glm',side_effect=denied),patch.object(dynamics,'objective',side_effect=denied),patch.object(optimize,'minimize',side_effect=denied),patch.object(socket.socket,'connect',side_effect=denied):
        records=sorted([r for r in J(R/'paper16_source_r4/SOURCE_AND_PHYSIOLOGY_ACCOUNT.json')['sources'] if r['selection']['admitted']],key=lambda r:int(r['source']['mouse_id']))
        by={r['source']['mouse_id']:r for r in records};C(len(by)==27,'mouse identities')
        plan=J(O/'results/TASK_PLAN.json');C(plan==panels.task_plan(records,J(O/'results/PANEL_PREFIT_PLAN.json')),'full task derivation')
        tasks={t['id']:t for t in plan['tasks']};C(len(tasks)==6471,'full task denominator')
        j=Lines(O/'results/FIT_JOURNAL.jsonl');att=[r for r in j if r['event']=='ATTEMPTED'];done=[r for r in j if r['event']=='COMPLETED'];failed=[r for r in j if r['event']=='FAILED']
        C((len(att),len(done),len(failed))==(953,952,1),'journal denominators')
        C(len({r['task']['id'] for r in att})==953 and len({r['task']['id'] for r in done})==952,'no retry')
        complete={r['task']['id']:r for r in done};C(all(tasks[r['task']['id']]==r['task'] for r in j),'all journal task identities')
        prep={}
        for r in J(O/'results/A_PREPROCESSING_STATES.json'):
            z=CheckReceipt(r);C(r['role']=='A' and r['key'] not in prep,'prepared unique A')
            C(np.all((z['ordinals']>=0)&(z['ordinals']<90)) and np.all(np.diff(z['ordinals'])>0),'A ordinals')
            b=features.Batch(**{k:z[k] for k in ['raw','y','ordinals','unit_ids','colors','running_missing','score_mask']},dt=r['dt'],psth=r['psth'],b1=r['b1'],role='A',panel=r['panel'])
            mean=z['raw'].mean((0,1));scale=np.maximum(.25,z['raw'].std((0,1)));active=z['raw'].var((0,1))>1e-12
            mean[:,:r['psth']]=0;scale[:,:r['psth']]=1;active[:,:r['psth']]=True
            C(all(np.array_equal(z[k],a) for k,a in [('mean',mean),('scale',scale),('active',active)]),'saved scaler equivalence')
            prep[r['key']]=(b,features.Scaling(z['mean'],z['scale'],z['active'],r['psth']),r)
        C(len(prep)==215,'all saved A preparations')
        matrix=J(P/'STATE_COMPATIBILITY_MATRIX.json')['states'];C(len(matrix)==952 and len({r['task_id'] for r in matrix})==952,'matrix uniqueness')
        stats=collections.Counter();maxima=dict(PG=0.,AD=0.,FD=0.);fg=nit=0
        for row in matrix:
            t=tasks[row['task_id']];C(t['id'] in complete and complete[t['id']]['task']==t,'independent task-completion join')
            f=O/'work/fits'/hashlib.sha256(t['id'].encode()).hexdigest();r=J(f/'RESULT.json');a=J(f/'ATTEMPT.json');client=J(f/'CLIENT.json');d,c,ad,fd=Cert(f)
            C(complete[t['id']]['result_path']==str((f/'RESULT.json').relative_to(R)).replace('\\','/') and complete[t['id']]['result_sha256']==H(f/'RESULT.json')==row['result_sha256'],'completion result hash')
            C(t==r['task']==a['task'] and a['no_retry'] and not (f/'FAILURE.json').exists() and (f/'CLIENT_STDERR.log').stat().st_size==0,'attempt/state integrity')
            initial=CheckReceipt(a['bounds']);endpoint=CheckReceipt(r['endpoint_state'])
            C(all(np.array_equal(client[k],initial[k]) for k in ['x0','lo','hi']),'actual optimizer CLIENT initializer')
            b,s,pr=prep[t['mouse_id']+'/'+t['panel']];u=None if t['unit_id'] is None else b.unit_ids.tolist().index(t['unit_id']);lam=1. if t['lambda']=='GLOBAL' else t['lambda']
            obj=models.Objective(b,s,t['model'],lam,u,t['seed'])
            C(all(np.array_equal(initial[k],v) for k,v in [('x0',obj.x0),('lo',obj.lo),('hi',obj.hi)]),'exact mathematical packing/bounds/initializer')
            C(a['parameters']==len(obj.x0)==d['free_coordinates'],'parameter dimensions')
            C(np.array_equal(endpoint['x'],c['endpoint_x']) and np.array_equal(endpoint['gradient'],c['endpoint_analytic']) and np.array_equal(r['x'],endpoint['x']) and np.allclose(r['jac'],endpoint['gradient'],atol=1e-12,rtol=1e-12),'endpoint identities')
            C(H(f/'DIAGNOSTICS.json')==r['diagnostic_state_sha256'],'diagnostic hash')
            x=endpoint['x'];C(np.all(x>=initial['lo']-1e-12) and np.all(x<=initial['hi']+1e-12),'endpoint bounds')
            pg=PG(x,endpoint['gradient'],initial['lo'],initial['hi'])
            C(pg==r['projected_gradient_inf']==row['PG']==complete[t['id']]['PG']<=1e-5,'PG gate')
            C(r['success'] and r['numerical_pass'] and r['message']=='CONVERGENCE: NORM OF PROJECTED GRADIENT <= PGTOL','gradient termination')
            C(r['fun']==r['objective']==row['objective']==complete[t['id']]['objective'] and np.isclose(r['fun'],d['checkpoints'][-1]['objective'],atol=1e-10,rtol=1e-12),'objective identity')
            calls=Lines(f/'CALLS.jsonl');accepted=Lines(f/'ACCEPTED.jsonl') if (f/'ACCEPTED.jsonl').exists() else []
            n=r['nfev'];k=r['nit'];C(n==r['external_value_gradient_pairs']==complete[t['id']]['calls']<=6000 and len(calls)==2*n,'FG journal counts')
            C(k==r['external_accepted_iterations']==r['accepted_vector_count']==complete[t['id']]['iterations']<=1500 and len(accepted)==k,'iteration journal counts')
            for i in range(n):
                q,v=calls[2*i:2*i+2];C(q['event']=='RESERVED_BEFORE_EVALUATION' and v['event']=='COMPLETED' and q['call']==v['call']==i+1 and math.isfinite(v['objective']) and math.isfinite(v['gradient_inf']),'FG reservation sequence')
            for i,v in enumerate(accepted):
                xx=np.asarray(v['x']);C(v['iteration']==i+1 and xx.shape==x.shape and np.isfinite(xx).all() and np.all(xx>=initial['lo']-1e-12) and np.all(xx<=initial['hi']+1e-12),'accepted vector integrity')
            C(np.array_equal(c['initial_x'],initial['x0']) and np.array_equal(c['halfway_x'],accepted[math.ceil(k/2)-1]['x'] if k else x) and r['halfway_accepted_iteration']==math.ceil(k/2),'registered checkpoint vectors')
            C(row['status']=='COMPATIBLE' and row['generated_by']=='R3' and row['historical_ftol']==1e-12 and not row['counterfactual_execution_equivalence_claimed'] and row['lambda_used']==lam and row['prepared_A_sha256']==pr['sha256'] and row['AD_error_max']==ad and row['fixed_FD_error_max']==fd,'matrix provenance/gates')
            for key,v in [('PG',pg),('AD',ad),('FD',fd)]:maxima[key]=max(maxima[key],v)
            stats[t['model']]+=1;fg+=n;nit+=k
        b0=J(P/'B0_COMPATIBILITY_MATRIX.json')['states'];C(len(b0)==216 and len({(r['mouse_id'],r['unit_id']) for r in b0})==216,'B0 denominator')
        for row in b0:
            f=O/'work/B0'/row['mouse_id']/str(row['unit_id']);r=J(f/'RESULT.json');d,c,ad,fd=Cert(f);b,s,pr=prep[row['mouse_id']+'/MAIN'];u=b.unit_ids.tolist().index(row['unit_id'])
            counts=b.y[:,:,u];rate=float(counts.sum())/(counts.size*b.dt);expected=-10. if rate==0 else float(np.clip(math.log(rate),-10,10))
            # Same registered logarithm uses numpy; tolerate only final elementary-function rounding.
            C(all(np.allclose(c[n+'_x'],[expected],atol=1e-15,rtol=1e-15) for n in ['initial','halfway','endpoint']),'B0 bounded analytic count/exposure MLE')
            pg=PG(c['endpoint_x'],c['endpoint_analytic'],np.array([-10.]),np.array([10.]))
            C(r['unit_id']==row['unit_id'] and r['analytic_MLE_not_optimizer_attempt'] and r['numeric_pass'] and pg==r['projected_gradient_inf']==row['PG']<=1e-5 and H(f/'RESULT.json')==row['result_sha256'],'B0 identity/gates')
        new=J(P/'NEW_TASK_PLAN_CANDIDATE.json');left=[t for t in plan['tasks'] if t['id'] not in complete]
        C(new['tasks']==left and len(left)==5519 and new['full_task_plan_sha256']==H(O/'results/TASK_PLAN.json'),'exact5519 difference')
        C(failed[0]['task'] in left and all(r['task_id']!=failed[0]['task']['id'] for r in matrix),'failed endpoint excluded')
    out=dict(mission='P16-M3-M5-UNIFORM-NUMERICAL-AMENDMENT-R4',decision='ACCEPTED_HISTORICAL_STATE_ADMISSION_ONLY',optimizer_states=952,B0_states=216,prepared_A_states=215,remaining_tasks=5519,old_protected_files=len(old),source_pins=len(pin),all_state_completion_result_joins=True,all_actual_CLIENT_vectors_verified=True,all_native_runtime_source_identities_verified=True,model_counts=dict(stats),FG_pairs=fg,accepted_iterations=nit,maxima=maxima,new_optimizer_calls=0,new_likelihood_derivative_score_calls=0,B_E_neural_arrays_accessed=False,Final_access=False,old_ftol_label=1e-12,counterfactual_execution_claim=False,production_execution_approval=False,P0=0,P1=0)
    path=E/'INDEPENDENT_REUSE_CHECK_RESULT.json'
    with path.open('x',encoding='utf8') as f:json.dump(out,f,indent=2);f.write('\n')
    print(json.dumps(out,indent=2))
if __name__=='__main__':run()
