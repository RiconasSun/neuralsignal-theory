"""Eleven frozen A-only sensitivity preparations; E results never affect eligibility."""
from .source import load_json
import copy
import json
import re
import numpy as np
from .source import P,R,dump
from .training import admitted,sha
from .metadata_access import local_path
from .physiology import unit_qc
from .features import observed_arrays,nuisance,design
from .controls import thin_role

CASES=[dict(id='S01',units=5),dict(id='S02',units=12),dict(id='S03',units=20),
    dict(id='S04',units=8,delta=.1),dict(id='S05',units=8,warmup=.25,history=.25),
    dict(id='S06',units=8,strict=True),dict(id='S07',units=8,thin=True),
    dict(id='S08',units=8,dilation=.01),dict(id='S09',units=8,dilation=.05),
    dict(id='S10',units=8,rich=True),dict(id='S11',units=5,boundary=True)]


def metadata_case(state,case):
    out=copy.deepcopy(state);tr=out['trials'];n=len(tr);warm=case.get('warmup',.5)
    s=np.array([np.nan if t['stimOn_times'] is None else t['stimOn_times'] for t in tr])
    a=np.array([np.nan if t['intervals_0'] is None else t['intervals_0'] for t in tr])
    z=np.array([np.nan if t['intervals_1'] is None else t['intervals_1'] for t in tr])
    checks={k:np.asarray(v,bool) for k,v in state['check_masks'].items()}
    lo=s-warm;hi=s+.5;support=state['result']['recording_sync_support']
    checks['neural_epoch_inside_trial']=(lo>=a)&(hi<=z)
    checks['recording_sync_support']=(lo>=support[0])&(hi<=support[1])
    nonoverlap=np.ones(n,bool);finite=np.flatnonzero(np.isfinite(s))
    for before,after in zip(finite[:-1],finite[1:]):
        if lo[after]<hi[before]:nonoverlap[[before,after]]=False
    checks['no_overlapping_epoch']=nonoverlap
    sat=np.asarray(state['selected_probe_saturation_session_seconds']).reshape(-1,2).copy()
    dilation=case.get('dilation',0.)
    if len(sat):sat[:,0]-=dilation;sat[:,1]+=dilation
    bad=np.zeros(n,bool)
    for b,e in sat:bad|=(s-1<e)&(hi>b)
    checks['no_known_saturation']=~bad
    out['valid']=np.logical_and.reduce(list(checks.values())).tolist()
    out['check_masks']={k:v.tolist() for k,v in checks.items()}
    out['selected_probe_saturation_session_seconds']=sat.tolist()
    return out


def boundary_units(state,row):
    atlas={int(x['id']):x['acronym'] for x in load_json((R/'paper13/metadata/atlas.json').read_text(encoding='utf8'))['msg']}
    f=next(x for x in row['files'] if x['role']=='atlas')
    contacts=np.load(local_path(row,f),allow_pickle=False)
    valid=[]
    for unit,channel in enumerate(state['native_cluster_channel']):
        if channel<2 or channel+2>=len(contacts):continue
        if all(re.fullmatch(r'MOp(?:1|2/3|4|5|6a|6b)?',str(atlas.get(int(x)))) for x in contacts[channel-2:channel+3]):valid.append(unit)
    return set(valid)


def prepare():
    assert (P/'SELECTION_FREEZE.json').exists(),'Sensitivity lambda policy requires prior frozen B selection'
    selection=load_json((P/'SELECTION_FREEZE.json').read_text(encoding='utf8'))
    source=load_json((P/'SOURCE_FILE_FREEZE.json').read_text(encoding='utf8'));manifest=[]
    for subject in admitted():
        state=load_json((P/'metadata'/(subject+'_task.json')).read_text(encoding='utf8'))
        qc=load_json((P/'results'/(subject+'_A_QC.json')).read_text(encoding='utf8'))
        row=next(x for x in source['subjects'] if x['subject']==subject)
        export=P/'work/A_exports'/(subject+'.npz');assert sha(export)==qc['A_export_sha256']
        with np.load(export,allow_pickle=False) as f:times=f['times'];labels=f['labels']
        wp={x['role']:local_path(row,x) for x in row['files'] if x['role'] in ('wheel_times','wheel_position')}
        wt=np.load(wp['wheel_times'],allow_pickle=False);wheel=np.load(wp['wheel_position'],allow_pickle=False)
        original={x['cluster_id']:x for x in qc['physiology']}
        for case in CASES:
            caseid=case['id'];met=metadata_case(state,case);roles=np.asarray(met['roles']);mask=np.asarray(met['valid'])
            ids=np.flatnonzero(mask&(roles=='A'));warmup=case.get('warmup',.5)
            record=dict(subject=subject,case=case,source_QC_sha256=sha(P/'results'/(subject+'_A_QC.json')),
                B_selection_sha256=sha(P/'SELECTION_FREEZE.json'),status='PREPARING',Final_access=False,E_neural_access=False)
            # Recomputed source-mask cases retain all original physiology thresholds and A quartiles.
            ranking=qc['ranking'];metrics=qc['physiology']
            if caseid in ('S05','S08','S09'):
                eps=np.array([[met['trials'][i]['stimOn_times']-warmup,met['trials'][i]['stimOn_times']+.5] for i in ids]).reshape(-1,2)
                all_units=list(original);metrics,ranked=unit_qc(times,labels,all_units,[state['native_uuid_list'][i] for i in all_units],ids,eps,state['result']['partitions']['A'][1]);ranking=[x['cluster_id'] for x in ranked]
            if case.get('strict'):ranking=[u for u in ranking if original[u]['strict_QC_qualified']]
            if case.get('boundary'):
                boundary=boundary_units(state,row);ranking=[u for u in ranking if u in boundary]
            selected=ranking[:case['units']]
            trial_counts={r:int(np.sum(mask&(roles==r))) for r in ['A','B','E']}
            reasons=[]
            if len(selected)<case['units']:reasons.append('INSUFFICIENT_REGISTERED_UNIT_CAPACITY')
            if any(trial_counts[r]<v for r,v in dict(A=80,B=40,E=40).items()):reasons.append('REGISTERED_TRIAL_COVERAGE_FAILURE')
            if any(selection['selected'][f] is None for f in ['B0','B1','B2','B3','B4']):reasons.append('REQUIRED_BASELINE_FAMILY_UNAVAILABLE')
            record.update(trial_counts=trial_counts,ranked_units=ranking,units=selected,physiology=metrics,
                metadata=met,unavailability_reasons=reasons)
            dest=P/'sensitivity_states'/subject/(caseid+'.json');assert not dest.exists()
            if reasons:
                record['status']='UNAVAILABLE';dump(dest,record);manifest.append(dict(subject=subject,case=caseid,status='UNAVAILABLE',reasons=reasons));continue
            st,sl=times,labels
            if case.get('thin'):
                # Always original primary8 and unthinned A rates; no thinned QC/reranking.
                selected=qc['selected_unit_ids'];record['units']=selected
                st,sl,tr=thin_role(times,labels,selected,[state['native_uuid_list'][u] for u in selected],[original[u]['A_rate_Hz'] for u in selected],subject,'A');record['thinning_A']=tr
            stimuli=np.array([met['trials'][i]['stimOn_times'] for i in ids])
            y,h,b,ep,warm=observed_arrays(st,sl,selected,stimuli,case.get('delta',.05),warmup,case.get('history',.5))
            if case.get('thin'):
                record['achieved_A_epoch_rates_Hz']=(y.sum(axis=(0,1))/(len(ids)*(warmup+.5))).tolist()
                record['achieved_A_rate_exposure_seconds']=len(ids)*(warmup+.5)
            nx=nuisance(met['trials'],ids,b,stimuli-.5,wt,wheel,case.get('rich',False));x,scales,active=design(nx,h,warm)
            path=P/'work/sensitivity_A'/subject/(caseid+'.npz');path.parent.mkdir(parents=True,exist_ok=True);assert not path.exists()
            np.savez_compressed(path,x=x,y=y,active=active,trial_ids=ids)
            record.update(status='A_PREPROCESSING_SEALED',scales=scales,active=active.tolist(),A_features_sha256=sha(path),warm=warm,delta=case.get('delta',.05),nuisance_columns=41 if case.get('rich') else 37)
            dump(dest,record);manifest.append(dict(subject=subject,case=caseid,status=record['status'],state_sha256=sha(dest)))
    dump(P/'results/SENSITIVITY_PREPARATION.json',dict(cases=CASES,records=manifest,planned_fits=5*sum(x['status']=='A_PREPROCESSING_SEALED' for x in manifest),maximum_Development_fits=550,Final_fits=0))


if __name__=='__main__':prepare()
