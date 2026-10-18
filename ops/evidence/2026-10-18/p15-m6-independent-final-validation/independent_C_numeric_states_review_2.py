"""Saved C-only tensor arithmetic; no whole-source/D reads, likelihood, AD/FD or fit."""
import datetime
import hashlib
import json
import socket
import sys
from pathlib import Path

import numpy as np

E=Path(__file__).resolve().parent
R=E.parents[3]
P=R/'paper15_final1'


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path):
    from paper15_final1.source import read as loader
    return loader(path)
def denied(*a,**k):raise AssertionError('No whole-record/D/model/likelihood/AD/FD/fit')


def hist(micro,step,history):
    n,l,u=micro.shape;out=np.zeros((n,l//step,u*4))
    edges=[0,1,2,4,int(round(history/.05))]
    for t in range(l//step):
        current=t*step
        for j,(short,long) in enumerate(zip(edges[:-1],edges[1:])):
            out[:,t,j::4]=micro[:,max(0,current-long):max(0,current-short)].sum(axis=1)/((long-short)*.05)
    return out


def scaled(raw,scales,begin):
    mean=np.asarray(scales['mean'])[begin:];sd=np.asarray(scales['sd'])[begin:];active=np.asarray(scales['active'])[begin:]
    assert np.array_equal(active,sd>=1e-8)
    return np.where(active,np.clip((raw-mean)/np.where(active,sd,1),-3,3),0.)


def run():
    sys.path.insert(0,str(R));socket.create_connection=denied;socket.socket.connect=denied
    import paper15_final1.models as models
    import paper15_final1.calibration as calibration
    import paper15_final1.independent_ad as ad
    for name in ['__init__','initialize','objective','value','prebin_logmasses']:setattr(models.Model,name,denied)
    calibration.minimize=denied;ad.ad_function=denied;ad.coordinate_check=denied
    original_load=np.load;allowed=[(P/'work'/n).resolve() for n in ['C_exports','C_features','sensitivity_C']]
    def load(path,*args,**kwargs):
        path=Path(path).resolve()
        assert path.suffix=='.npz' and any(path.is_relative_to(base) for base in allowed)
        return original_load(path,*args,**kwargs)
    np.load=load
    def arrays(path):
        with np.load(path,allow_pickle=False) as f:return {k:f[k] for k in f.files}
    candidate=read(P/'C_PRODUCTION_CANDIDATE.json');candidate_sha=sha(P/'C_PRODUCTION_CANDIDATE.json')
    assert len(candidate['hashes'])==127
    for rel,h in candidate['hashes'].items():assert sha(P/rel)==h
    for rel,h in candidate['external_hashes'].items():assert sha(R/rel)==h
    source_receipt=read(E/'C_PHYSIOLOGY_STATE_REVIEW_RECEIPT_1.json')
    assert source_receipt['decision']=='ACCEPTED_C_ONLY_PHYSIOLOGY_AND_STATES' and source_receipt['hashes']==candidate['hashes']
    assert source_receipt['candidate_sha256']==candidate_sha and source_receipt['open_P0']==source_receipt['open_P1']==0
    assert source_receipt['approved_C_only_physiology_and_states'] is True and source_receipt['approved_D_evaluation'] is False
    plan=read(P/'C_FIT_PLAN.json');sensplan=read(P/'SENSITIVITY_FIT_PLAN.json');prep=read(P/'results/C_SENSITIVITY_PREPARATION.json')
    subjects=calibration.admitted();assert subjects==plan['subjects']==sensplan['subjects'] and len(subjects)==6
    assert plan['configurations']==calibration.configurations() and len(plan['configurations'])==12 and plan['expected_attempts']==72
    assert plan['solver']==calibration.SOLVER and plan['max_retries']==sensplan['max_retries']==0
    assert plan['cumulative_before_Final']==1494 and 1494+72+320==1886
    chosen={c['family']:c for c in plan['configurations'] if c['family'].startswith('B')}
    expected=[];unavailable=[];case_checks=[];main_checks=[]
    for subject in subjects:
        statepath=P/'states'/(subject+'_C_PREPROCESSING.json');state=read(statepath)
        path=P/'work/C_features'/(subject+'.npz');assert sha(path)==state['C_features_sha256'] and sha(statepath)==plan['state_hashes'][subject]
        a=arrays(path);y,x=a['y'],a['x'];n,l,u=y.shape
        assert state['role']=='C' and u==8 and l==20 and state['warm_bins']==10
        assert np.isfinite(x).all() and np.isfinite(y).all() and (y>=0).all() and np.equal(y,np.floor(y)).all()
        np.testing.assert_array_equal(a['trial_ids'],state['trial_ids']);np.testing.assert_array_equal(a['active'],state['active'])
        assert state['actual_score_population_bins']==n*10 and state['actual_score_unit_bins']==n*80
        np.testing.assert_array_equal(x[:,:,0],np.ones((n,l)))
        h=hist(y,1,.5);np.testing.assert_array_equal(x[:,:,38:],scaled(h,state['scales'],37))
        for key,cs in state['C_scales'].items():
            rank=cs['rank'];tau=cs['tau'];micro=cs['micro_scale'];rate=y/.05
            z=np.where(micro['active'],(rate-micro['mean'])/np.where(micro['active'],micro['sd'],1),0.)
            basis=np.cos(np.pi*(np.arange(u)[:,None]+.5)*np.arange(rank)[None,:]/u)*np.sqrt(2/u);basis[:,0]=1/np.sqrt(u)
            np.testing.assert_array_equal(basis,cs['R']);weights=np.exp(-np.arange(10)*.05/tau);weights/=weights.sum();np.testing.assert_array_equal(weights,cs['weights'])
            projected=z@basis;q=np.zeros((n,l,rank))
            for lag,w in enumerate(weights,1):q[:,lag:]+=w*projected[:,:-lag]
            qs=cs['q_scale'];out=np.where(qs['active'],np.clip((q-qs['mean'])/np.where(qs['active'],qs['sd'],1),-3,3),0.)
            np.testing.assert_array_equal(out,a[key]);np.testing.assert_array_equal(a[key+'_active'],qs['active'])
        main_checks.append(dict(subject=subject,epochs=n,units=u,C_hist_and_selected_DCT_exact=True))
        source_export=None
        for row in [r for r in prep['records'] if r['subject']==subject]:
            cid=row['case'];sp=P/'sensitivity_states'/subject/(cid+'.json');st=read(sp)
            assert sha(sp)==row['state_sha256'] and st['status']==row['status'] and st['subject']==subject
            if st['status']=='UNAVAILABLE':
                assert st['unavailability_reasons'];unavailable.append((subject,cid));continue
            for family in ['B0','B1','B2','B3','B4']:
                expected.append(dict(subject=subject,case=cid,family=family,ridge=chosen[family]['ridge'],seed=11,state_sha256=sha(sp)))
            fp=P/'work/sensitivity_C'/subject/(cid+'.npz');assert sha(fp)==st['C_features_sha256'];data=arrays(fp)
            yy,xx=data['y'],data['x'];n,l,u=yy.shape;warm=st['warm'];delta=st['delta'];nuisance=st['nuisance_columns']
            ids=np.flatnonzero(np.asarray(st['metadata']['valid'])&(np.asarray(st['metadata']['roles'])=='C'))
            np.testing.assert_array_equal(ids,data['trial_ids']);np.testing.assert_array_equal(data['active'],st['active'])
            assert n==st['trial_counts']['C'] and l==warm+int(round(.5/delta)) and u==len(st['units'])
            assert nuisance==(41 if cid=='S10' else 37) and xx.shape==(n,l,1+nuisance+4*u)
            assert np.isfinite(xx).all() and np.isfinite(yy).all() and np.equal(yy,np.floor(yy)).all() and (yy>=0).all()
            np.testing.assert_array_equal(xx[:,:,0],np.ones((n,l)))
            if delta==.05:hh=hist(yy,1,st['case'].get('history',.5))
            else:
                assert cid=='S04' and delta==.1 and warm==5
                if source_export is None:
                    ep=P/'work/C_exports'/(subject+'.npz');assert sha(ep)==state['C_export_sha256'];source_export=arrays(ep)
                stimuli=np.array([st['metadata']['trials'][i]['stimOn_times'] for i in ids]);micro=np.zeros((n,20,u),np.int64)
                edges=stimuli[:,None]+(np.arange(21)[None,:]-10)*.05;edges[:,10]=stimuli;edges[:,-1]=stimuli+.5
                for v,unit in enumerate(st['units']):
                    times=source_export['times'][source_export['labels']==unit]
                    for i,b in enumerate(edges):
                        subset=times[(times>=b[0])&(times<b[-1])]
                        micro[i,:,v]=np.histogram(subset,bins=b)[0]
                np.testing.assert_array_equal(yy,micro.reshape(n,10,2,u).sum(axis=2));hh=hist(micro,2,.5)
            np.testing.assert_array_equal(xx[:,:,1+nuisance:],scaled(hh,st['scales'],nuisance))
            assert np.max(np.abs(xx[:,:,1:]))<=3
            np.testing.assert_array_equal(xx[:,:,np.logical_not(data['active'])],0.)
            if cid=='S07':
                exposure=n*(st['case'].get('warmup',.5)+.5)
                assert st['achieved_C_rate_exposure_seconds']==exposure
                np.testing.assert_array_equal(st['achieved_C_epoch_rates_Hz'],yy.sum(axis=(0,1))/exposure)
            case_checks.append(dict(subject=subject,case=cid,epochs=n,units=u,warm=warm,delta=delta,nuisance=nuisance,scored_population_bins=n*int(round(.5/delta)),saved_history_transform_exact=True))
        print(subject,'saved C main/cases arithmetic verified',flush=True)
    assert len(prep['records'])==66 and len(case_checks)==64 and set(unavailable)=={('NR_0027','S03'),('DY_011','S03')}
    assert sensplan['attempts']==expected and len(expected)==sensplan['expected_attempts']==320
    assert sensplan['cohort_cap']==330 and sensplan['absolute_Final_cap']==440 and sensplan['new_search'] is False
    assert not list((P/'fits').glob('*/*.json')) and not list((P/'sensitivity_fits').glob('*/*/*.json'))
    assert sha(P/'C_PRODUCTION_CANDIDATE.json')==candidate_sha
    result=dict(mission='P15-M6-INDEPENDENT-FINAL-VALIDATION',reviewer='/root/gradient_review',time=datetime.datetime.now(datetime.timezone.utc).isoformat(),candidate_sha256=candidate_sha,hashes=candidate['hashes'],external_hashes=candidate['external_hashes'],main_checks=main_checks,case_checks=case_checks,unavailable=unavailable,main_plan_attempts=72,sensitivity_plan_attempts=320,historical_cumulative_before=1494,prospective_cumulative_after=1886,
                source_physiology_review_reused=True,source_review_receipt_sha256=sha(E/'C_PHYSIOLOGY_STATE_REVIEW_RECEIPT_1.json'),synthetic_tests_independent_passed=38,repaired_actual_sensitivity_branch_probes_passed=2,
                own_actual_C_scope='Six C_features,64 sensitivity_C tensors; six authorized C_exports only for independent S04 microhistogram. No whole-source or D arrays; no actual likelihood/AD/FD/fit.',main_history_and_DCT_reconstructed=6,sensitivity_history_exposure_arithmetic_checked=64,S04_independent_microhistograms=6,
                real_C_fits=0,real_likelihood_AD_FD_evaluations=0,whole_recording_neural_access=False,D_neural_access=False,approved_pre_D=False,maximum_scientific_scope='DESCRIPTIVE ONLY',diagnostic_script_sha256=sha(Path(__file__)))
    target=E/'C_PRODUCTION_REVIEW_CHECKS_2.json';assert not target.exists();target.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n',encoding='utf8')
    print('PASS six main/64available+2unavailable cases,72/320 plans,0realfit/D; checksSHA='+sha(target))


if __name__=='__main__':run()
