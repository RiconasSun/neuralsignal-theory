"""Eleven registered C-only cases; fixed selected baseline ridges, no search."""
import argparse
import datetime
import numpy as np
from .source import P,R,read,dump,sha,source_rows
from .calibration import admitted,c_export,wheel,configurations,fit_one,check_production_gate,failure_policy
from .sensitivities import CASES,metadata_case
from .physiology import unit_qc
from .anatomy import candidate_units,boundary_units
from .features import observed_arrays,nuisance,design
from .controls import thin_role
from .models import Model


def prepare():
    assert not (P/'results/C_SENSITIVITY_PREPARATION.json').exists()
    manifest=[]
    for subject in admitted():
        source=next(r for r in source_rows() if r['subject']==subject)
        state=read(P/'metadata'/(subject+'_task.json'));qc=read(P/'results'/(subject+'_C_QC.json'))
        export=c_export(subject);times,labels=export['times'],export['labels'];wt,wp=wheel(source)
        original={r['cluster_id']:r for r in qc['physiology']}
        for case in CASES:
            met=metadata_case(state,case);roles=np.asarray(met['roles']);mask=np.asarray(met['valid'])
            ids=np.flatnonzero(mask&(roles=='C'));warmup=case.get('warmup',.5)
            ranking=list(qc['ranking']);metrics=qc['physiology']
            if case['id'] in ('S05','S08','S09'):
                eps=np.array([[met['trials'][i]['stimOn_times']-warmup,met['trials'][i]['stimOn_times']+.5] for i in ids]).reshape(-1,2)
                units=list(original)
                metrics,ranked=unit_qc(times,labels,units,[state['native_uuid_list'][u] for u in units],ids,eps,state['result']['partitions']['C'][1])
                ranking=[r['cluster_id'] for r in ranked]
                metrics=[{k.replace('original_A_','original_C_').replace('A_','C_'):v for k,v in m.items()} for m in metrics]
            if case.get('strict'):ranking=[u for u in ranking if original[u]['strict_QC_qualified']]
            if case.get('boundary'):
                boundary=boundary_units(state,source);ranking=[u for u in ranking if u in boundary]
            selected=ranking[:case['units']]
            counts={r:int(np.sum(mask&(roles==r))) for r in ('C','D')};reasons=[]
            if len(selected)<case['units']:reasons.append('INSUFFICIENT_REGISTERED_UNIT_CAPACITY')
            if counts['C']<80 or counts['D']<60:reasons.append('REGISTERED_TRIAL_COVERAGE_FAILURE')
            record=dict(subject=subject,case=case,metadata=met,units=selected,ranked_units=ranking,physiology=metrics,
                trial_counts=counts,unavailability_reasons=reasons,status='UNAVAILABLE' if reasons else 'PREPARING_C_ONLY',
                source_QC_sha256=sha(P/'results'/(subject+'_C_QC.json')),
                B_selection_sha256=sha(R/'paper15_r1/SELECTION_FREEZE.json'),D_neural_scientific_access=False)
            target=P/'sensitivity_states'/subject/(case['id']+'.json');assert not target.exists()
            if reasons:
                dump(target,record);manifest.append(dict(subject=subject,case=case['id'],status='UNAVAILABLE',reasons=reasons,state_sha256=sha(target)));continue
            st,sl=times,labels
            if case.get('thin'):
                selected=qc['selected_unit_ids'];record['units']=selected
                st,sl,thinning=thin_role(times,labels,selected,[state['native_uuid_list'][u] for u in selected],
                    [original[u]['C_rate_Hz'] for u in selected],subject,'C');record['thinning_C']=thinning
            stimuli=np.array([met['trials'][i]['stimOn_times'] for i in ids])
            y,h,b,_,warm=observed_arrays(st,sl,selected,stimuli,case.get('delta',.05),warmup,case.get('history',.5))
            raw=nuisance(met['trials'],ids,b,stimuli-.5,wt,wp,case.get('rich',False));x,scales,active=design(raw,h,warm)
            arraypath=P/'work/sensitivity_C'/subject/(case['id']+'.npz');arraypath.parent.mkdir(parents=True,exist_ok=True);assert not arraypath.exists()
            np.savez_compressed(arraypath,x=x,y=y,active=active,trial_ids=ids)
            if case.get('thin'):
                record['achieved_C_epoch_rates_Hz']=(y.sum(axis=(0,1))/(len(ids)*(warmup+.5))).tolist()
                record['achieved_C_rate_exposure_seconds']=len(ids)*(warmup+.5)
            record.update(status='C_PREPROCESSING_SEALED',scales=scales,active=active.tolist(),C_features_sha256=sha(arraypath),
                warm=warm,delta=case.get('delta',.05),nuisance_columns=41 if case.get('rich') else 37)
            dump(target,record);manifest.append(dict(subject=subject,case=case['id'],status=record['status'],state_sha256=sha(target)))
    dump(P/'results/C_SENSITIVITY_PREPARATION.json',dict(cases=CASES,records=manifest,
        planned_fits=5*sum(r['status']=='C_PREPROCESSING_SEALED' for r in manifest),absolute_Final_cap=440,D_neural_access=False))


def register():
    target=P/'SENSITIVITY_FIT_PLAN.json';assert not target.exists()
    prep=read(P/'results/C_SENSITIVITY_PREPARATION.json');selected={c['family']:c for c in configurations() if c['family'].startswith('B')}
    expected=[]
    for row in prep['records']:
        if row['status']!='C_PREPROCESSING_SEALED':continue
        for family in ('B0','B1','B2','B3','B4'):
            expected.append(dict(subject=row['subject'],case=row['case'],family=family,ridge=selected[family]['ridge'],seed=11,state_sha256=row['state_sha256']))
    assert len(expected)<=55*len(admitted())<=440
    dump(target,dict(time=datetime.datetime.now(datetime.timezone.utc).isoformat(),subjects=admitted(),cases=CASES,attempts=expected,
        expected_attempts=len(expected),cohort_cap=55*len(admitted()),absolute_Final_cap=440,max_retries=0,new_search=False,
        selection_sha256=sha(R/'paper15_r1/SELECTION_FREEZE.json'),preparation_sha256=sha(P/'results/C_SENSITIVITY_PREPARATION.json')))


def execute():
    gate=read(P/'C_PRODUCTION_GATE.json');check_production_gate(gate)
    assert not (P/'results/C_MAIN_REQUIRED_STOP.json').exists(),'Mandatory main failure stops sensitivity calibration'
    assert (P/'results/C_MAIN_ATTEMPTS_COMPLETE.json').exists()
    plan=read(P/'SENSITIVITY_FIT_PLAN.json');assert plan['subjects']==admitted() and len(plan['attempts'])==plan['expected_attempts']<=440
    records=[]
    for item in plan['attempts']:
        path=P/'sensitivity_states'/item['subject']/(item['case']+'.json');assert sha(path)==item['state_sha256']
        state=read(path);arraypath=P/'work/sensitivity_C'/item['subject']/(item['case']+'.npz');assert sha(arraypath)==state['C_features_sha256']
        with np.load(arraypath,allow_pickle=False) as f:arrays={k:f[k] for k in f.files}
        model=Model(arrays['x'],arrays['y'],item['family'],ridge=item['ridge'],active=arrays['active'],warm=state['warm'],delta=state['delta'],nuisance=state['nuisance_columns'])
        target=P/'sensitivity_fits'/item['subject']/item['case']/(item['family']+'.json')
        config=dict(id=item['family'],family=item['family'],ridge=item['ridge'],seed=11)
        record=fit_one(model,config,target,sha(P/'C_PRODUCTION_GATE.json'),item['state_sha256'])
        disposition=failure_policy(record,sensitivity=True)
        records.append(dict(item=item,status=record['status'],disposition=disposition,sha256=sha(target)))
        print(item['subject'],item['case'],item['family'],record['status'],'PG',record.get('PG'),flush=True)
        if disposition=='CRITICAL_INTEGRITY_STOP':
            dump(P/'results/C_SENSITIVITY_REQUIRED_STOP.json',dict(reason='CRITICAL_INTEGRITY_STOP',attempts=records,D_executed=False))
            return
    dump(P/'results/C_SENSITIVITY_ATTEMPTS_COMPLETE.json',dict(attempted=len(records),numerical_pass=sum(r['status']=='NUMERICAL_PASS' for r in records),records=records,D_neural_access=False))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['prepare','register','run']);action=p.parse_args().action
    {'prepare':prepare,'register':register,'run':execute}[action]()
