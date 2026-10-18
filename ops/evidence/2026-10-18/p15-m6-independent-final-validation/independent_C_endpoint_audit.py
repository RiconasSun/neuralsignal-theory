"""Reviewer-owned JSON-only endpoint audit. No source arrays or real evaluations."""
from pathlib import Path
import datetime, hashlib, json, socket, sys
import numpy as np

R=Path(__file__).resolve().parents[4]
P=R/'paper15_final1'
E=Path(__file__).parent

def denied(*args,**kwargs):raise PermissionError('Independent saved-endpoint audit denies arrays/network')
np.load=denied
socket.socket.connect=denied
socket.create_connection=denied

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path):return json.loads(path.read_bytes())
def finite(a):assert np.isfinite(np.asarray(a,dtype=float)).all()
def same(a,b):assert np.array_equal(np.asarray(a),np.asarray(b))

def structure(state,c,intercepts):
    u=len(state['units']);active=np.asarray(state['active'],bool)
    if c['family']=='C':active=np.r_[active,state['C_scales'][f"C_r{c['rank']}_tau{c['tau']}"]['q_scale']['active']]
    p=len(active);nuisance=state.get('nuisance_columns',37);hstart=1+nuisance
    mask=np.ones((p,u),bool);f=c['family']
    if f=='B0':mask[1:]=False
    elif f=='B1':mask[hstart:]=False
    elif f in ('B2','B3'):
        mask[hstart:]=False
        for source in range(u):
            for target in range(u):
                if (source==target)==(f=='B2'):mask[hstart+4*source:hstart+4*(source+1),target]=True
    else:assert f in ('B4','C','D','S')
    mask &= active[:,None];mask[0]=True
    lin=int(mask.sum());bounds=[[-8.,8.] if j<u else [-1.,1.] for j in np.flatnonzero(mask.ravel())]
    penalty=list(np.broadcast_to((np.arange(p)>0)[:,None],(p,u))[mask].astype(float))
    initial=np.zeros((p,u));initial[0]=intercepts;initial=list(initial[mask]);k=c.get('k',2)
    if f in ('D','S'):
        initial.extend(np.random.Generator(np.random.PCG64(c['seed'])).uniform(-.05,.05,(k-1)*u))
        bounds += [[-2.,2.]]*((k-1)*u)
        if f=='D':
            initial.extend([2.*(i==j)-2.*(i==k-1) for i in range(k) for j in range(k-1)])
            bounds += [[-4.,4.]]*(k*(k-1))
        initial.extend([0.]*(k-1));bounds += [[-4.,4.]]*(k-1)
    penalty += [1.]*(len(bounds)-lin)
    return np.asarray(bounds),np.asarray(penalty),np.asarray(initial)

def endpoint(rec,c,state,sh,gatehash,base_initial):
    assert rec['configuration']==c and rec['C_state_sha256']==sh and rec['production_gate_sha256']==gatehash
    assert rec['attempt']==1 and rec['fit_role']=='C' and rec['D_neural_fit_data'] is False and rec['Development_coefficients_reused'] is False
    assert rec['status'] in ('NUMERICAL_PASS','NUMERICAL_FAIL') and 'error' not in rec
    gcheck=rec['independent'];theta=np.asarray(rec['coefficients']);g=np.asarray(gcheck['analytic_gradient']);ad=np.asarray(gcheck['AD_gradient'])
    bounds,penalty,initial=structure(state,c,base_initial)
    same(rec['bounds'],bounds);same(rec['initial'],initial)
    assert theta.shape==g.shape==ad.shape==(len(bounds),)==(rec['free_parameters'],)
    finite(theta);finite(g);finite(ad);finite(rec['objective']);finite(gcheck['objective']);finite(gcheck['AD_objective'])
    adabs=abs(g-ad);adscaled=adabs/np.maximum(1.,np.maximum(abs(g),abs(ad)))
    same(adabs,gcheck['AD_coordinate_absolute']);same(adscaled,gcheck['AD_coordinate_scaled'])
    assert float(adscaled.max(initial=0))==gcheck['AD_max_scaled']
    assert abs(gcheck['objective']-gcheck['AD_objective'])==gcheck['objective_difference']
    assert [fd['step'] for fd in gcheck['FD']]==[1e-4,1e-5,1e-6]
    maxima=[]
    for fd in gcheck['FD']:
        v=np.asarray(fd['numerical_gradient']);assert v.shape==theta.shape;finite(v)
        a=abs(v-g);s=a/np.maximum(1.,np.maximum(abs(v),abs(g)))
        same(a,fd['coordinate_absolute']);same(s,fd['coordinate_scaled'])
        assert a.max(initial=0)==fd['max_absolute'] and s.max(initial=0)==fd['max_scaled'];maxima.append(float(s.max(initial=0)))
    independent=bool(gcheck['objective_difference']<=1e-8*max(1.,abs(gcheck['objective'])) and gcheck['AD_max_scaled']<=1e-5 and max(maxima)<=1e-5)
    assert gcheck['PASS'] is independent
    projected=g.copy();projected[((theta==bounds[:,0])&(g>0))|((theta==bounds[:,1])&(g<0))]=0.
    pg=float(abs(projected).max(initial=0));inbounds=bool(((theta>=bounds[:,0])&(theta<=bounds[:,1])).all())
    assert pg==rec['PG'] and abs(g).max(initial=0)==rec['full_gradient_inf'] and rec['objective']==gcheck['objective']
    assert rec['exact_bounds'] is inbounds and rec['finite_all'] is True
    exhausted=rec['optimizer_status']==1;assert rec['budget_exhausted'] is exhausted
    passed=bool(inbounds and pg<=.001 and independent and not exhausted)
    assert (rec['status']=='NUMERICAL_PASS')==passed
    T=state['actual_score_population_bins'] if 'actual_score_population_bins' in state else state['trial_counts']['C']*round(.5/state['delta'])
    assert rec['training_population_bins']==T and rec['training_unit_bins']==T*len(state['units'])
    finite(rec['training_score_LL']);rebuilt=-rec['training_score_LL']/T+c['ridge']/2*float(np.sum(penalty*theta**2))
    assert np.isclose(rebuilt,rec['objective'],rtol=0,atol=2e-12)
    hist=rec['optimizer_history'];calls=rec['optimizer_objective_calls'];its=rec['iterations']
    assert its==len(hist) and 0<=its<=2000 and 1<=calls<=80000
    assert [h['iteration'] for h in hist]==list(range(1,its+1))
    hc=[h['calls'] for h in hist];assert all(a<=b for a,b in zip(hc,hc[1:])) and (not hc or hc[-1]<=calls)
    for h in hist:
        finite([h['objective'],h['PG'],h['full_gradient_inf']]);assert 0<=h['PG']<=h['full_gradient_inf']
    if hist:
        assert np.isclose(hist[-1]['objective'],rec['objective'],rtol=0,atol=1e-12)
        assert np.isclose(hist[-1]['PG'],pg,rtol=0,atol=1e-12)
    if c['family']=='B0':assert its==0 and calls==1 and rec['optimizer_status']==0
    assert rec['completed_at']>=rec['started_at'] and rec['wall_seconds']>=0
    return dict(status=rec['status'],parameters=len(theta),PG=pg,AD=gcheck['AD_max_scaled'],FD=maxima,iterations=its,calls=calls,trajectory_rows=len(hist),objective_ridge_LL_reconciled=True,initialization_structure_seed_exact=True)

def run(final=False):
    plan=read(P/'C_FIT_PLAN.json');sp=read(P/'SENSITIVITY_FIT_PLAN.json');candidate=read(P/'C_PRODUCTION_CANDIDATE.json');gate=read(P/'C_PRODUCTION_GATE.json')
    assert len(candidate['hashes'])==127 and gate['hashes']==candidate['hashes']
    for rel,h in candidate['hashes'].items():assert sha(P/rel)==h,rel
    assert plan['subjects']==sp['subjects'] and plan['expected_attempts']==72 and sp['expected_attempts']==320
    assert plan['cumulative_before_Final']==1494 and plan['max_retries']==0 and sp['max_retries']==0
    assert plan['solver']==dict(maxiter=2000,maxfun=80000,maxls=40,ftol=1e-12,gtol=1e-6)
    expected={};bases={}
    for subject in plan['subjects']:
        state=read(P/'states'/(subject+'_C_PREPROCESSING.json'));sh=sha(P/'states'/(subject+'_C_PREPROCESSING.json'));assert sh==plan['state_hashes'][subject]
        bpath=P/'fits'/subject/'B0.json'
        if bpath.exists():bases[(subject,'main')]=read(bpath)['initial']
        for c in plan['configurations']:expected['fits/'+subject+'/'+c['id']+'.json']=(c,state,sh,(subject,'main'))
    for item in sp['attempts']:
        subject=item['subject'];case=item['case'];path=P/'sensitivity_states'/subject/(case+'.json');state=read(path);assert sha(path)==item['state_sha256']
        c=dict(id=item['family'],family=item['family'],ridge=item['ridge'],seed=item['seed'])
        bpath=P/'sensitivity_fits'/subject/case/'B0.json'
        if bpath.exists():bases[(subject,case)]=read(bpath)['initial']
        key='sensitivity_fits/'+subject+'/'+case+'/'+item['family']+'.json';assert key not in expected
        expected[key]=(c,state,item['state_sha256'],(subject,case))
    assert len(expected)==392
    existing={p.relative_to(P).as_posix() for folder in ['fits','sensitivity_fits'] for p in (P/folder).rglob('*.json')}
    assert existing<=set(expected),'Unregistered attempt path'
    results=[];started=[];transient=[]
    for rel in sorted(existing):
        path=P/rel;raw=path.read_bytes();h=hashlib.sha256(raw).hexdigest()
        try:record=json.loads(raw)
        except json.JSONDecodeError:transient.append(rel);continue
        if record['status']=='STARTED':started.append(dict(path=rel,sha256=h));continue
        c,state,sh,bkey=expected[rel];out=endpoint(record,c,state,sh,sha(P/'C_PRODUCTION_GATE.json'),bases[bkey])
        assert sha(path)==h,'Completed endpoint changed during read'
        results.append(dict(path=rel,sha256=h,**out))
    if final:
        assert not transient and not started and len(results)==392
        seal=read(P/'FINAL_C_STATE_SEAL.json');assert seal['complete_calibration_state'] is True and seal['main_attempts']==72 and seal['sensitivity_attempts']==320 and seal['cumulative_attempts']==1886
        for item in seal['artifacts']:assert sha(P/item['path'])==item['sha256']
        for item in seal['main']+seal['sensitivities']:assert sha(P/item['path'])==item['sha256']
    out=dict(mission='P15-M6-INDEPENDENT-FINAL-VALIDATION',reviewer='/root/gradient_review',time=datetime.datetime.now(datetime.timezone.utc).isoformat(),mode='FINAL_SAVED_C' if final else 'INTERIM_COMPLETED_RECORDS_ONLY',approved_pre_D=False,script_sha256=sha(Path(__file__)),candidate_sha256=sha(P/'C_PRODUCTION_CANDIDATE.json'),gate_sha256=sha(P/'C_PRODUCTION_GATE.json'),plan_hashes={n:sha(P/n) for n in ['C_FIT_PLAN.json','SENSITIVITY_FIT_PLAN.json']},registered=392,completed_checked=len(results),numerical_pass=sum(r['status']=='NUMERICAL_PASS' for r in results),numerical_fail=sum(r['status']=='NUMERICAL_FAIL' for r in results),started=started,transient_write_skipped=transient,unattempted=len(expected)-len(existing),records=results,real_arrays_loaded=0,real_likelihood_AD_FD_evaluations=0,new_fits=0,D_access=False)
    target=E/('C_ENDPOINT_FINAL_CHECKS_1.json' if final else 'C_ENDPOINT_INTERIM_CHECKS_1.json')
    with target.open('x',encoding='utf8') as f:json.dump(out,f,indent=2,sort_keys=True);f.write('\n')
    print(json.dumps({k:v for k,v in out.items() if k!='records'},indent=2))

if __name__=='__main__':run('--final' in sys.argv)
