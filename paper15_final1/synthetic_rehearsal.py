"""Entire planned D numerical kernel on six fictional mice; no protected source reads."""
import datetime
import time
import tempfile
import numpy as np
from .source import P,read,dump,sha
from .features import observed_arrays,nuisance,design,dct_state
from .physiology import unit_qc
from .controls import thin_role,stratum_keys
from .sensitivities import CASES,metadata_case
from .calibration import configurations,build_model
from .d_support import main_arrays,case_arrays,pre_epoch_wheel,FrozenPredictors,case_logmass
from .reference_metadata import control_coverage
from .reference_evaluation import run_controls,control_summary,sensitivity_summary
from .final_statistics import analyze_final,claim_verdicts
from .models import Model


def synthetic_source(index):
    rng=np.random.Generator(np.random.PCG64(150501+index));n=400;u=20
    tr=[dict(intervals_0=2.*i,intervals_1=2.*i+1.8,stimOn_times=2.*i+.75,goCue_times=2.*i+.7,
        response_times=2.*i+1.1,feedback_times=2.*i+1.25,choice=(-1.)**i,feedbackType=1.,
        contrastLeft=.25 if i%2 else None,contrastRight=1. if i%2==0 else None) for i in range(n)]
    cids=np.arange(1,240,3);dids=np.arange(241,321) if index<3 else np.arange(241,400,2)
    valid=np.zeros(n,bool);valid[cids]=True;valid[dids]=True
    roles=np.array(['C']*240+['D']*160)
    metadata=dict(trials=tr,roles=roles.tolist(),valid=valid.tolist(),
        check_masks={k:valid.tolist() for k in ['event_order','behavioral_support','boundary_guard','role_support','essential_contrast','wheel_support','no_overlapping_epoch','neural_epoch_inside_trial','recording_sync_support','no_known_saturation']},
        selected_probe_saturation_session_seconds=[],native_uuid_list=[f'synthetic-unit-{j:02}' for j in range(u)],
        result=dict(partitions={'C':[0,240],'D':[240,400]},recording_sync_support=[0.,800.]))
    # At most one synthetic spike/unit/microbin avoids introducing irrelevant refractory artifacts.
    counts=(rng.random((n,20,u))<.20).astype(int);events=[];labels=[]
    for trial in range(n):
        bins,units=np.nonzero(counts[trial])
        events.extend((2.*trial+.25+(bins+.5)*.05).tolist());labels.extend(units.tolist())
        events.extend([2.*trial+1.6]*u);labels.extend(range(u))  # Outside retained epochs; S07 must consume these draws.
    order=np.argsort(events,kind='stable');events=np.asarray(events)[order];labels=np.asarray(labels)[order]
    ckeep=events<479.8;ct,cl=events[ckeep],labels[ckeep];dt,dl=events[~ckeep],labels[~ckeep]
    eps=np.array([[tr[i]['stimOn_times']-.5,tr[i]['stimOn_times']+.5] for i in cids])
    metrics,ranked=unit_qc(ct,cl,list(range(u)),metadata['native_uuid_list'],cids,eps,240)
    assert len(ranked)>=20
    metrics=[{k.replace('original_A_','original_C_').replace('A_','C_'):v for k,v in r.items()} for r in metrics]
    units=[r['cluster_id'] for r in ranked[:8]];ranking=[r['cluster_id'] for r in ranked]
    wt=np.arange(-1.,801.,.05);wp=np.sin(wt*.1)+.1*np.sin(wt*.7)
    return metadata,ct,cl,dt,dl,wt,wp,cids,dids,metrics,units,ranking


def one_mouse(index,root):
    subject=f'SYNTHETIC_ONLY_{index}';meta,ct,cl,dt,dl,wt,wp,cids,dids,metrics,units,ranking=synthetic_source(index)
    stimuli=np.array([meta['trials'][i]['stimOn_times'] for i in cids])
    y,h,b,epoch,warm=observed_arrays(ct,cl,units,stimuli);raw=nuisance(meta['trials'],cids,b,epoch,wt,wp)
    x,scales,active=design(raw,h,warm);q,cs=dct_state(y,1,.1,warm)
    c_arrays=dict(x=x,y=y,active=active,trial_ids=cids)
    c_arrays['C_r1_tau0.1']=q;c_arrays['C_r1_tau0.1_active']=np.asarray(cs['q_scale']['active'])
    prep=dict(units=units,scales=scales,C_scales={'C_r1_tau0.1':cs},active=active.tolist(),warm_bins=warm)
    main=main_arrays(dt,dl,meta,prep,wt,wp)
    assert main['trial_ids'].tolist()==dids.tolist()
    predictor=FrozenPredictors.__new__(FrozenPredictors);predictor.configs={};predictor.parameters={}
    configs=configurations()
    for config in configs:
        model=build_model(c_arrays,config);theta=model.initialize(config['seed']);bounds=np.asarray(model.bounds)
        theta=np.clip(theta+.003*np.sin(np.arange(len(theta))),bounds[:,0],bounds[:,1])
        predictor.configs.setdefault(config['family'],[]).append(config);predictor.parameters.setdefault(config['family'],[]).append(theta)
    row=dict(subject=subject,lab=f'synthetic_lab{index%4}',models=predictor.score(main),trial_ids=dids.tolist())
    cases=[];rates={r['cluster_id']:r['C_rate_Hz'] for r in metrics}
    for case in CASES:
        metadata=metadata_case(meta,case);selected=ranking[:case['units']]
        st,sl=ct,cl
        if case.get('thin'):
            selected=units
            st,sl,_=thin_role(ct,cl,selected,[meta['native_uuid_list'][u] for u in selected],[rates[u] for u in selected],subject,'C')
        warmup=case.get('warmup',.5);delta=case.get('delta',.05)
        yy,hh,bb,_,ww=observed_arrays(st,sl,selected,stimuli,delta,warmup,case.get('history',.5))
        xx,ss,aa=design(nuisance(meta['trials'],cids,bb,stimuli-.5,wt,wp,case.get('rich',False)),hh,ww)
        state=dict(subject=subject,case=case,metadata=metadata,units=selected,physiology=metrics,status='C_PREPROCESSING_SEALED',
            delta=delta,warm=ww,nuisance_columns=41 if case.get('rich') else 37,scales=ss,active=aa.tolist())
        arrays,thinning=case_arrays(subject,state,dt,dl,wt,wp);scores={}
        for config in [c for c in configs if c['family'].startswith('B')]:
            model=Model(xx,yy,config['family'],ridge=config['ridge'],active=aa,warm=ww,delta=delta,nuisance=state['nuisance_columns'])
            theta=model.initialize(11);bounds=np.asarray(model.bounds)
            theta=np.clip(theta+.003*np.sin(np.arange(len(theta))),bounds[:,0],bounds[:,1])
            scores[config['family']]=case_logmass(arrays,state,config['family'],config['ridge'],theta)
        cases.append(dict(subject=subject,lab=row['lab'],case=case['id'],models=scores,status=state['status'],
            trial_ids=arrays['trial_ids'].tolist(),thinning_D=thinning))
    cmag=pre_epoch_wheel(meta,cids,wt,wp);threshold=float(np.median(cmag));dmag=pre_epoch_wheel(meta,dids,wt,wp)
    bounds=meta['result']['partitions']['D'];keys2=stratum_keys(meta['trials'],dids,bounds,dmag,threshold);keys3=stratum_keys(meta['trials'],dids,bounds)
    metadata=dict(D_trial_ids=dids.tolist(),role_bounds=bounds,keys_N2=keys2,keys_N3=keys3,coverage=control_coverage(dids,keys2,keys3,bounds))
    controls=run_controls(subject,main,predictor,prep,metadata,journal_root=root/subject)
    print(subject,'all11cases + actual999replicate schedules complete',flush=True)
    return row,cases,dict(subject=subject,lab=row['lab'],suites=controls)


def run():
    from unittest.mock import patch
    started=time.perf_counter();root=P/'work/full_D_synthetic';root.mkdir(parents=True,exist_ok=True)
    folder=__import__('pathlib').Path(tempfile.mkdtemp(dir=root));rows=[];cases=[];controls=[]
    with patch('numpy.load',side_effect=PermissionError('Synthetic rehearsal cannot open source arrays')),patch('socket.socket.connect',side_effect=PermissionError('Synthetic rehearsal network denied')):
        for index in range(6):
            row,cs,control=one_mouse(index,folder);rows.append(row);cases.extend(cs);controls.append(control)
        subjects=[r['subject'] for r in rows];families={f:subjects[:] for f in ['B0','B1','B2','B3','B4','C','D','S']}
        from .statistics import CONTRASTS
        spec=dict(primary_subjects=subjects,family_subjects=families,contrast_subjects={c:subjects[:] for c in CONTRASTS},
            source_main_numerical_valid=True,static_capacity_pair_valid=True,confirmatory_assumptions_defensible=False,mandatory_descriptive_only=True)
        stats=analyze_final(rows,spec);ss=sensitivity_summary(cases,subjects);cc=control_summary(controls,subjects);verdicts=claim_verdicts(stats,ss,cc,spec)
        assert len(cases)==66 and len(ss)==11 and len(cc)==6 and all(v['verdict']=='DESCRIPTIVE ONLY' for v in verdicts.values())
    journals=sorted(folder.rglob('*.jsonl'))
    count=sum(v['replicates_completed'] for r in controls for v in r['suites'].values())
    assert len(journals)==24 and count==20979
    result=dict(scope='FULL_PLANNED_D_KERNEL_SYNTHETIC_ONLY',fictional_mice=6,main_model_families=8,
        sensitivity_cases=11,sensitivity_panels=66,scheduled_suites=24,complete_suites=21,unavailable_suites=3,
        actual_reference_bundles=count,replicates_per_available_suite=999,
        statistics=stats,sensitivity_summaries=ss,control_summaries=cc,claim_verdicts=verdicts,
        journal_hashes={p.relative_to(P).as_posix():sha(p) for p in journals},
        source_array_loading_denied=True,network_denied=True,real_C_fits=0,real_D_neural_access=False,
        actual_D_batch_claim_created=False,wall_seconds=time.perf_counter()-started,
        fixture_parameters='C-only synthetic initialization plus fixed .003sin perturbation; no optimization or scientific outcome',
        outputs_are_scientific_evidence=False,time=datetime.datetime.now(datetime.timezone.utc).isoformat())
    dump(P/'results/FULL_D_SYNTHETIC_REHEARSAL.json',result)
    print('FULL SYNTHETIC KERNEL PASS',count,'bundles',round(result['wall_seconds'],2),'seconds; no actual D access',flush=True)


if __name__=='__main__':run()
