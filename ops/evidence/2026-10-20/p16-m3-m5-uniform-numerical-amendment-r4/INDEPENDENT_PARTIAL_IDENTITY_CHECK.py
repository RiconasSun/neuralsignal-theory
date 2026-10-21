"""Constructor-only saved-A identity audit, never a derivative/fit experiment."""
import datetime,hashlib,json,socket
from pathlib import Path
from unittest.mock import patch
import numpy as np
from scipy import optimize
from paper16_development_r4 import models,features
from paper16_development_r4.core import spec,dynamics

R=Path.cwd();P=R/'paper16_development_r4';E=R/'ops/evidence/2026-10-20/p16-m3-m5-uniform-numerical-amendment-r4'
def J(p):return json.loads(p.read_bytes())
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def denied(*args,**kwargs):raise AssertionError('Constructor-only saved identity forbids scientific evaluations/network')
def array_id(a):return dict(shape=list(a.shape),dtype=a.dtype.str,sha256=hashlib.sha256(a.tobytes()).hexdigest())

def main():
    audit=J(E/'INDEPENDENT_INTERRUPTION_EVIDENCE.json');task=audit['partial_attempt']['task']
    folder=P/'work/fits'/hashlib.sha256(task['id'].encode()).hexdigest()
    attempt=J(folder/'ATTEMPT.json');client=J(folder/'CLIENT.json');bound=attempt['bounds']
    assert attempt['task']==task and attempt['no_retry'] is True and H(R/bound['path'])==bound['sha256']
    with np.load(folder/'initial.npz',allow_pickle=False) as a:initial={k:a[k].copy() for k in a.files}
    assert {k:array_id(v) for k,v in initial.items()}==bound['arrays']
    assert all(np.array_equal(initial[k],client[k]) for k in ['x0','lo','hi'])
    prep=next(r for r in J(R/'paper16_development_r3/results/A_PREPROCESSING_STATES.json') if r['key']==task['mouse_id']+'/'+task['panel'])
    assert prep['role']=='A' and H(R/prep['path'])==prep['sha256']
    with patch.object(models.Objective,'analytic',side_effect=denied),patch.object(models.Objective,'AD',side_effect=denied),patch.object(models.Objective,'score',side_effect=denied),patch.object(spec,'glm',side_effect=denied),patch.object(spec,'independent_AD',side_effect=denied),patch.object(dynamics,'objective',side_effect=denied),patch.object(dynamics,'independent_AD',side_effect=denied),patch.object(optimize,'minimize',side_effect=denied),patch.object(socket.socket,'connect',side_effect=denied):
        with np.load(R/prep['path'],allow_pickle=False) as a:z={k:a[k].copy() for k in a.files}
        assert np.all((z['ordinals']>=0)&(z['ordinals']<90))
        assert {k:array_id(v) for k,v in z.items()}==prep['arrays']
        batch=features.Batch(**{k:z[k] for k in ['raw','y','ordinals','unit_ids','colors','running_missing','score_mask']},dt=prep['dt'],psth=prep['psth'],b1=prep['b1'],role='A',panel=prep['panel'])
        scaler=features.Scaling(z['mean'],z['scale'],z['active'],prep['psth'])
        obj=models.Objective(batch,scaler,task['model'],1.,None,task['seed'])
        assert all(np.array_equal(initial[k],v) for k,v in [('x0',obj.x0),('lo',obj.lo),('hi',obj.hi)])
    out=dict(reviewer='/root/r4_interruption_review',reviewed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),task=task,original_initializer_and_bounds_match=True,CLIENT_matches_initial=True,prepared_A_path=prep['path'],prepared_A_sha256=prep['sha256'],all_A_members_match=True,parameters=len(initial['x0']),new_fits=0,new_objective_or_derivative_or_score_calls=0,new_neural_source_requests=0,B_E_Final_access=False,numerical_endpoint_verdict=None)
    with (E/'INDEPENDENT_PARTIAL_IDENTITY.json').open('x',encoding='utf8') as f:json.dump(out,f,indent=2);f.write('\n')
    print(json.dumps(out))

if __name__=='__main__':main()
