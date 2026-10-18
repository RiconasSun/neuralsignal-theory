"""Audit authorized saved C exports/states only. No raw source, fit or predictor."""
import datetime,hashlib,json,math
import numpy as np
from paper15_final1.source import R,P,E,read,sha,json_safe,source_rows
from paper15_final1.metadata_access import local_path
from paper15_final1.features import observed_arrays,nuisance,design,dct_state
from paper15_final1.sensitivities import CASES,metadata_case
from paper15_final1.anatomy import candidate_units,boundary_units

def same(a,b):
    if isinstance(a,dict):
        assert set(a)==set(b),(set(a)-set(b),set(b)-set(a))
        for k in a:same(a[k],b[k])
    elif isinstance(a,list):
        assert len(a)==len(b)
        for x,y in zip(a,b):same(x,y)
    elif isinstance(a,float):assert math.isclose(a,b,rel_tol=2e-13,abs_tol=2e-12),(a,b)
    else:assert a==b,(a,b)

def independent_qc(t,l,units,uuids,ids,epochs,stop):
    duration=epochs[:,1]-epochs[:,0];cuts=[0,*[int(k*.25*stop) for k in (1,2,3)],stop]
    q=np.array([next(j for j in range(4) if cuts[j]<=i<cuts[j+1]) for i in ids])
    exposure=float(duration.sum());qexp=[float(duration[q==j].sum()) for j in range(4)]
    metrics=[]
    for u,uuid in zip(units,uuids):
        st=t[l==u];idx=np.searchsorted(st,epochs,side='left');counts=idx[:,1]-idx[:,0]
        n=int(counts.sum());pairs=int(np.maximum(counts-1,0).sum())
        refractory=sum(int(np.count_nonzero(np.diff(st[a:b])<.001)) for a,b in idx)
        qcounts=[int(counts[q==j].sum()) for j in range(4)]
        rate=n/exposure if exposure else 0.;isi=refractory/pairs if pairs else None
        qrates=[c/e if e else 0. for c,e in zip(qcounts,qexp)]
        reasons=[]
        if not .5<=rate<=100:reasons.append('RATE_OUTSIDE_0.5_100_HZ')
        if n<100:reasons.append('SPIKES_LT_100')
        if pairs<99:reasons.append('ISI_PAIRS_LT_99')
        if isi is None or isi>.005:reasons.append('ISI_FRACTION_GT_0.005_OR_UNDEFINED')
        if min(qexp)<10:reasons.append('ORIGINAL_A_QUARTILE_EXPOSURE_LT_10_S')
        if min(qrates)<.1:reasons.append('ORIGINAL_A_QUARTILE_RATE_LT_0.1_HZ')
        metrics.append(dict(cluster_id=int(u),uuid=uuid,C_spikes=n,C_exposure_seconds=exposure,C_rate_Hz=rate,
            C_within_epoch_ISI_pairs=pairs,C_refractory_pairs=refractory,C_refractory_fraction=isi,
            original_C_quartile_exposures=qexp,original_C_quartile_spikes=qcounts,original_C_quartile_rates=qrates,
            primary_qualified=not reasons,strict_QC_qualified=not reasons and 1<=rate<=50 and isi<=.0025 and min(qrates)>=.2,
            exclusion_reasons=reasons))
    rank=sorted([m for m in metrics if m['primary_qualified']],key=lambda m:(m['C_refractory_fraction'],-m['C_rate_Hz'],m['uuid']))
    return metrics,[m['cluster_id'] for m in rank]

def arrays(path):
    with np.load(path,allow_pickle=False) as f:return {k:f[k] for k in f.files}

def derive_features(t,l,units,metadata,ids,wt,wp,delta=.05,warmup=.5,history=.5,rich=False):
    stimuli=np.array([metadata['trials'][i]['stimOn_times'] for i in ids])
    y,h,b,epoch,warm=observed_arrays(t,l,units,stimuli,delta,warmup,history)
    # Independently count half-open bins with per-epoch histograms.
    for v,u in enumerate(units):
        st=t[l==u]
        for i,starts in enumerate(b):
            edges=np.r_[starts,stimuli[i]+.5]
            a,z=np.searchsorted(st,[edges[0],edges[-1]],side='left')
            assert np.array_equal(np.histogram(st[a:z],bins=edges)[0],y[i,:,v])
    raw=nuisance(metadata['trials'],ids,b,stimuli-.5,wt,wp,rich);x,scales,active=design(raw,h,warm)
    combined=np.concatenate([raw,h],axis=-1)[:,warm:].reshape(-1,raw.shape[-1]+h.shape[-1])
    assert np.array_equal(combined.mean(axis=0),scales['mean']) and np.array_equal(combined.std(axis=0),scales['sd'])
    return dict(x=x,y=y,active=active,trial_ids=ids),scales,warm

c=read(P/'C_PRODUCTION_CANDIDATE.json');assert len(c['hashes'])==127
for rel,h in c['hashes'].items():assert sha(P/rel)==h,rel
for rel,h in c['external_hashes'].items():assert sha(R/rel)==h,rel
gate=read(P/'results/FINAL_C_QC_GATE.json');admitted=[x['subject'] for x in gate['subjects'] if x['admitted']]
assert len(gate['subjects'])==8 and len(admitted)==6 and gate['eligible_labs']==4 and not gate['primary_coverage']
assert admitted==c['subjects'] and gate['real_fits']==0 and not gate['D_neural_scientific_access']
assert not (P/'work/C_exports/NYU-21.npz').exists()
subjects=[];cases=[]
for row in source_rows():
    s=row['subject']
    if s=='NYU-21':continue
    state=read(P/'metadata'/(s+'_task.json'));qc=read(P/'results'/(s+'_C_QC.json'))
    exportpath=P/'work/C_exports'/(s+'.npz');assert sha(exportpath)==qc['C_export_sha256']
    export=arrays(exportpath);t,l=export['times'],export['labels'];ids=export['trial_ids'];epochs=export['epochs'];cut=state['result']['partitions']['C'][1]
    assert set(export)=={'times','labels','trial_ids','epochs'}
    assert len(t)==len(l) and np.isfinite(t).all() and np.all(np.diff(t)>=0)
    assert np.all((t>=state['trials'][0]['intervals_0'])&(t<state['trials'][cut-1]['intervals_1']))
    expected_ids=np.flatnonzero(np.asarray(state['valid'])&(np.asarray(state['roles'])=='C'));assert np.array_equal(ids,expected_ids)
    expected_epochs=np.array([[state['trials'][i]['stimOn_times']-.5,state['trials'][i]['stimOn_times']+.5] for i in ids]);assert np.array_equal(epochs,expected_epochs)
    units=candidate_units(state);metrics,rank=independent_qc(t,l,units,[state['native_uuid_list'][u] for u in units],ids,epochs,cut)
    same(metrics,qc['physiology']);assert rank==qc['ranking'] and len(rank)==qc['qualified_units']
    selected=rank[:8] if len(rank)>=8 else [];assert qc['selected_unit_ids']==selected
    assert qc['selected_unit_uuids']==[state['native_uuid_list'][u] for u in selected]
    assert qc['reader_gate_sha256']==sha(P/'C_READER_GATE.json') and qc['status']=='COMPLETE_C_ONLY' and not qc['D_scientific_projection']
    subjects.append(dict(subject=s,qualified=len(rank),admitted=bool(selected),C_epochs=len(ids),C_export_sha256=sha(exportpath),QC_sha256=sha(P/'results'/(s+'_C_QC.json'))))
    print(s,'independent C QC PASS',len(rank),flush=True)
    if s not in admitted:
        assert s=='UCLA033' and len(rank)==6 and not (P/'states'/(s+'_C_PREPROCESSING.json')).exists();continue
    prep=read(P/'states'/(s+'_C_PREPROCESSING.json'));savedpath=P/'work/C_features'/(s+'.npz');assert sha(savedpath)==prep['C_features_sha256']
    wheelpaths={f['role']:local_path(row,f) for f in row['files'] if f['role'] in ('wheel_times','wheel_position')}
    wt,wp=(np.load(wheelpaths[k],allow_pickle=False) for k in ('wheel_times','wheel_position'))
    expected,scales,warm=derive_features(t,l,selected,state,ids,wt,wp);same(scales,prep['scales']);saved=arrays(savedpath)
    for k,v in expected.items():assert np.array_equal(saved[k],v),(s,k)
    key='C_r1_tau0.1';q,qs=dct_state(expected['y'],1,.1,warm);same(qs,prep['C_scales'][key]);assert np.array_equal(q,saved[key])
    assert np.array_equal(saved[key+'_active'],qs['q_scale']['active']) and prep['trial_ids']==ids.tolist() and prep['units']==selected
    assert prep['unit_uuids']==qc['selected_unit_uuids'] and not prep['model_parameters_from_Development'] and not prep['D_neural_scientific_access']
    original={m['cluster_id']:m for m in metrics}
    for case in CASES:
        name=case['id'];path=P/'sensitivity_states'/s/(name+'.json');record=read(path);met=metadata_case(state,case)
        assert json_safe(record['metadata'])==json_safe(met)
        case_ids=np.flatnonzero(np.asarray(met['valid'])&(np.asarray(met['roles'])=='C'));warmup=case.get('warmup',.5)
        ranking=list(rank);case_metrics=metrics
        if name in ('S05','S08','S09'):
            eps=np.array([[met['trials'][i]['stimOn_times']-warmup,met['trials'][i]['stimOn_times']+.5] for i in case_ids]).reshape(-1,2)
            case_metrics,ranking=independent_qc(t,l,units,[state['native_uuid_list'][u] for u in units],case_ids,eps,cut)
        if case.get('strict'):ranking=[u for u in ranking if original[u]['strict_QC_qualified']]
        if case.get('boundary'):ranking=[u for u in ranking if u in boundary_units(state,row)]
        same(case_metrics,record['physiology']);assert ranking==record['ranked_units']
        chosen=ranking[:case['units']];assert chosen==record['units']
        counts={r:int(np.sum(np.asarray(met['valid'])&(np.asarray(met['roles'])==r))) for r in ('C','D')};assert counts==record['trial_counts']
        reasons=[]
        if len(chosen)<case['units']:reasons.append('INSUFFICIENT_REGISTERED_UNIT_CAPACITY')
        if counts['C']<80 or counts['D']<60:reasons.append('REGISTERED_TRIAL_COVERAGE_FAILURE')
        assert reasons==record['unavailability_reasons']
        if reasons:
            assert record['status']=='UNAVAILABLE';cases.append(dict(subject=s,case=name,status='UNAVAILABLE',reasons=reasons));continue
        st,sl=t,l
        if case.get('thin'):
            retain=np.zeros(len(t),bool);receipts=[]
            for u in selected:
                uuid=state['native_uuid_list'][u];p=min(1.,2./original[u]['C_rate_Hz'])
                seed=int.from_bytes(hashlib.sha256(f'P15-M1|150108|S07|{s}|{uuid}|C'.encode()).digest()[:8],'big')
                ix=np.flatnonzero(l==u);keep=np.random.Generator(np.random.PCG64(seed)).random(len(ix))<p;retain[ix[keep]]=True
                receipts.append(dict(unit=int(u),uuid=uuid,role='C',p=p,seed=seed,draw_count=len(ix),kept=int(keep.sum())))
            same(receipts,record['thinning_C']);st,sl=t[retain],l[retain]
        derived,case_scales,case_warm=derive_features(st,sl,chosen,met,case_ids,wt,wp,case.get('delta',.05),warmup,case.get('history',.5),case.get('rich',False))
        same(case_scales,record['scales']);arraypath=P/'work/sensitivity_C'/s/(name+'.npz');assert sha(arraypath)==record['C_features_sha256']
        actual=arrays(arraypath)
        for k,v in derived.items():assert np.array_equal(actual[k],v),(s,name,k)
        assert record['status']=='C_PREPROCESSING_SEALED' and not record['D_neural_scientific_access']
        if case.get('thin'):
            assert np.array_equal(derived['y'].sum(axis=(0,1))/(len(case_ids)*(warmup+.5)),record['achieved_C_epoch_rates_Hz'])
        cases.append(dict(subject=s,case=name,status='C_PREPROCESSING_SEALED',state_sha256=sha(path)))
    print(s,'main + eleven C states PASS',flush=True)
assert len(cases)==66 and sum(r['status']=='C_PREPROCESSING_SEALED' for r in cases)==64
assert {(r['subject'],r['case']) for r in cases if r['status']=='UNAVAILABLE'}=={('NR_0027','S03'),('DY_011','S03')}
plan=read(P/'C_FIT_PLAN.json');sens=read(P/'SENSITIVITY_FIT_PLAN.json')
assert plan['subjects']==sens['subjects']==admitted and plan['expected_attempts']==72 and sens['expected_attempts']==len(sens['attempts'])==320
assert len({(r['subject'],r['case'],r['family']) for r in sens['attempts']})==320
assert not (P/'fits').exists() and not (P/'sensitivity_fits').exists()
out=dict(mission='P15-M6-INDEPENDENT-FINAL-VALIDATION',time=datetime.datetime.now(datetime.timezone.utc).isoformat(),candidate_sha256=sha(P/'C_PRODUCTION_CANDIDATE.json'),hashes=c['hashes'],external_hashes=c['external_hashes'],C_physiology=subjects,cases=cases,main_states_verified=6,case_states_verified=66,available_cases=64,capacity_unavailable_cases=2,prospective_main_attempts=72,prospective_sensitivity_attempts=320,prospective_cumulative=1494+72+320,real_fits=0,D_neural_access=False,original_whole_record_neural_bodies_read=False,approved_pre_D=False)
(E/'C_PHYSIOLOGY_STATE_INDEPENDENT_CHECKS_1.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
print('ALL C-only physiological and state checks PASS',flush=True)
