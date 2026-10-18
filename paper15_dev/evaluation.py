"""Exactly one frozen exploratory Development E assessment, never Final C/D."""
import argparse
import csv
import datetime
import hashlib
import json
import os
import numpy as np
from .source import P,R,dump
from .training import admitted,sha,claim_attempt
from .selection import require_stage,extract_role
from .evaluation_support import read_json,source_state,wheel,raw_E,case_arrays,pre_epoch_wheel,control_arrays,FrozenPredictors,score_case
from .controls import seed,reference,stratum_keys,coverage
from .statistics import CONTRASTS,analyze,holm
from .sensitivities import CASES
from .sensitivity_fits import verify_plan

CONTROL_FAMILIES=['B1','B2','B3','B4','D','C','S']


def append_event(path,event):
    with path.open('r+',encoding='utf8') as handle:
        handle.seek(0,2)
        handle.write(json.dumps(event,sort_keys=True,allow_nan=False)+'\n');handle.flush();os.fsync(handle.fileno())


def create_journal(path,event):
    with path.open('x',encoding='utf8') as handle:
        handle.write(json.dumps(event,sort_keys=True,allow_nan=False)+'\n');handle.flush();os.fsync(handle.fileno())


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()


def effect_vector(scores):
    out=[]
    for a,b in CONTRASTS.values():
        if a not in scores or b not in scores:out.append(None);continue
        assert scores[a]['unit_bins']==scores[b]['unit_bins']
        value=(scores[a]['LL']-scores[b]['LL'])/scores[a]['unit_bins']
        assert np.isfinite(value);out.append(float(value))
    return out


def prepare_reference_metadata():
    """Only A exports/preprocessing and already-open task/wheel metadata."""
    require_stage('B');assert (P/'SELECTION_FREEZE.json').exists()
    target=P/'REFERENCE_METADATA_FREEZE.json';assert not target.exists()
    records=[]
    for subject in admitted():
        row,metadata=source_state(subject);wt,wp=wheel(row)
        a_ids=np.flatnonzero(np.asarray(metadata['valid'])&(np.asarray(metadata['roles'])=='A'))
        e_ids=np.flatnonzero(np.asarray(metadata['valid'])&(np.asarray(metadata['roles'])=='E'))
        magnitudes=pre_epoch_wheel(metadata,a_ids,wt,wp);threshold=float(np.median(magnitudes))
        e_magnitudes=pre_epoch_wheel(metadata,e_ids,wt,wp)
        bounds=metadata['result']['partitions']['E']
        keys2=stratum_keys(metadata['trials'],e_ids,bounds,e_magnitudes,threshold)
        keys3=stratum_keys(metadata['trials'],e_ids,bounds)
        # Eligibility depends solely on fixed task metadata and A-only threshold.
        dummy=np.zeros((len(e_ids),20,8),int);coverage_records={}
        for suite,keys in [('N1',None),('N2',keys2),('N3',keys3),('N4',None)]:
            _,ix,_=reference(dummy,suite,e_ids,np.random.Generator(np.random.PCG64(seed(suite,subject,'E',0))),keys,bounds)
            coverage_records[suite]=dict(trial_ids=e_ids[ix].tolist(),epochs=len(ix),total_epochs=len(e_ids),
                available=True if suite=='N1' else coverage(ix,len(e_ids)))
        ap=P/'work/A_features'/(subject+'.npz');prep=read_json(P/'states'/(subject+'_A_PREPROCESSING.json'));assert sha(ap)==prep['A_features_sha256']
        with np.load(ap,allow_pickle=False) as arrays:
            a_warm_rate=np.asarray(arrays['y'][:,:10].sum(axis=1)/.5)
        records.append(dict(subject=subject,E_trial_ids=e_ids.tolist(),A_wheel_median=threshold,A_wheel_magnitudes=magnitudes.tolist(),
            E_metadata_wheel_magnitudes=e_magnitudes.tolist(),keys_N2=keys2,keys_N3=keys3,role_bounds=bounds,coverage=coverage_records,
            A_warm_rate_mean_by_unit=a_warm_rate.mean(axis=0).tolist(),A_warm_rate_sd_by_unit=a_warm_rate.std(axis=0).tolist(),
            A_wheel_displacement_mean=float(magnitudes.mean()),A_wheel_displacement_sd=float(magnitudes.std()),
            A_preprocessing_sha256=sha(P/'states'/(subject+'_A_PREPROCESSING.json')),task_sha256=sha(P/'metadata'/(subject+'_task.json'))))
    dump(target,dict(subjects=admitted(),records=records,replicates=999,suites=['N1','N2','N3','N4'],
        draws='PCG64 fresh per suite/subject/E/replicate; exact M1 numeric schedule',E_neural_access=False,Final_access=False))


def verify_E_gate():
    require_stage('E');gate=read_json(P/'E_EXPLORATORY_GATE.json')
    required={'evaluation.py','evaluation_support.py','controls.py','statistics.py','sensitivities.py','sensitivity_fits.py',
        'REFERENCE_METADATA_FREEZE.json','SENSITIVITY_FIT_PLAN.json','SENSITIVITY_GATE.json','results/SENSITIVITY_ATTEMPTS_COMPLETE.json',
        'results/SENSITIVITY_PREPARATION.json','independent_ad.py','source.py','reader.py','source_integrity.py',
        'SOURCE_FILE_FREEZE.json','NEURAL_HEADER_FREEZE.json','READER_GATE.json','results/M2_PHYSIOLOGY_GATE.json','PRODUCTION_GATE.json'}
    assert required<=set(gate['hashes'])
    for rel,h in gate['hashes'].items():assert sha(P/rel)==h
    reviews=gate['independent_review_evidence'];assert set(reviews)=={'engineering','mathematics'}
    for item in reviews.values():assert sha(R/item['path'])==item['sha256']
    subjects=admitted();assert gate['subjects']==subjects and gate['E_batches']==1 and gate['Final_access'] is False
    selected=read_json(P/'SELECTION_FREEZE.json');assert selected['subjects']==subjects
    ref=read_json(P/'REFERENCE_METADATA_FREEZE.json');assert ref['subjects']==subjects and ref['replicates']==999 and ref['suites']==['N1','N2','N3','N4']
    assert [x['subject'] for x in ref['records']]==subjects
    production=read_json(P/'PRODUCTION_GATE.json');reader=read_json(P/'READER_GATE.json')
    assert production['PRODUCTION_NUMERICAL_PASS'] and reader['approved_for_A_only']
    for parent in [production,reader]:
        assert parent['hashes']
        for rel,h in parent['hashes'].items():assert sha(P/rel)==h
    for subject in subjects:
        sp=f'states/{subject}_A_PREPROCESSING.json';mp=f'metadata/{subject}_task.json';qp=f'results/{subject}_A_QC.json'
        assert {sp,mp,qp}<=set(gate['hashes'])
        assert sp in production['hashes'] and mp in reader['hashes']
        state=read_json(P/sp);qc=read_json(P/qp)
        assert state['subject']==subject and state['role']=='A' and state['units']==qc['selected_unit_ids']
        assert state['QC_sha256']==sha(P/qp) and state['task_sha256']==sha(P/mp)
        assert state['M1_freeze_sha256']==sha(R/'paper15_m1/PROTOCOL_FREEZE.json')
        item=next(x for x in ref['records'] if x['subject']==subject)
        assert item['A_preprocessing_sha256']==sha(P/sp) and item['task_sha256']==sha(P/mp)
    plan=read_json(P/'SENSITIVITY_FIT_PLAN.json');complete=read_json(P/'results/SENSITIVITY_ATTEMPTS_COMPLETE.json')
    preparation=read_json(P/'results/SENSITIVITY_PREPARATION.json');candidates=read_json(P/'results/B_CANDIDATE_SCORES.json')
    verify_plan(plan,selected,candidates,preparation,subjects)
    assert plan['B_selection_sha256']==sha(P/'SELECTION_FREEZE.json')
    sg=read_json(P/'SENSITIVITY_GATE.json');assert sg['approved_for_fixed_A_sensitivity_refits']
    assert {'SENSITIVITY_FIT_PLAN.json','SELECTION_FREEZE.json','results/B_CANDIDATE_SCORES.json','results/SENSITIVITY_PREPARATION.json',
        'models.py','independent_ad.py','features.py','sensitivities.py','sensitivity_fits.py','PRODUCTION_GATE.json'}<=set(sg['hashes'])
    for rel,h in sg['hashes'].items():assert sha(P/rel)==h
    for item in preparation['records']:
        rel=f"sensitivity_states/{item['subject']}/{item['case']}.json"
        assert rel in gate['hashes'], 'All sealed AND unavailable cases must be bound before any E access'
        state=read_json(P/rel)
        assert state['subject']==item['subject'] and state['case']==next(c for c in CASES if c['id']==item['case'])
        assert state['status']==item['status'] and state['B_selection_sha256']==sha(P/'SELECTION_FREEZE.json')
        assert state['source_QC_sha256']==sha(P/'results'/(item['subject']+'_A_QC.json'))
        if state['status']=='A_PREPROCESSING_SEALED':assert item['state_sha256']==sha(P/rel)
        else:assert state['unavailability_reasons']==item['reasons'] and item['reasons']
    assert complete['attempted']==complete['completed']==plan['expected_attempts']
    expected={(x['subject'],x['case'],x['family']) for x in plan['attempts']}
    assert len(expected)==len(plan['attempts'])==len(complete['records'])
    assert {(x['item']['subject'],x['item']['case'],x['item']['family']) for x in complete['records']}==expected
    for record in complete['records']:
        item=record['item'];path=P/'sensitivity_fits'/item['subject']/item['case']/(item['family']+'.json')
        assert record['sha256']==sha(path)
        actual=read_json(path);assert actual['plan_item']==item and actual['status']==record['status'] and record['status'] in ('NUMERICAL_PASS','NUMERICAL_FAIL')
        assert actual['sensitivity_gate_sha256']==sha(P/'SENSITIVITY_GATE.json')
    return gate,selected,candidates,ref


def run_controls(subject,arrays,predictors,prep,reference_metadata,journal_root=None):
    out={};trial_ids=arrays['trial_ids'];total=len(trial_ids)
    assert trial_ids.tolist()==reference_metadata['E_trial_ids']
    bounds=reference_metadata['role_bounds']
    root=P/'results/E_control_journals'/subject if journal_root is None else journal_root
    root.mkdir(parents=True,exist_ok=True)
    for suite in ['N1','N2','N3','N4']:
        cov=reference_metadata['coverage'][suite]
        journal=root/(suite+'.jsonl')
        create_journal(journal,dict(event='SUITE_STARTED',subject=subject,suite=suite,coverage=cov,replicates=999))
        if not cov['available']:
            out[suite]=dict(status='UNAVAILABLE_REGISTERED_COVERAGE',coverage=cov,replicates_completed=0)
            append_event(journal,dict(event='UNAVAILABLE_REGISTERED_COVERAGE',coverage=cov));continue
        keys=None if suite in ('N1','N4') else [tuple(x) for x in reference_metadata['keys_'+suite]]
        replicates=[];mapping_hashes=[];seeds=[];wheel_gains=[];original=None
        for r in range(999):
            s=seed(suite,subject,'E',r);append_event(journal,dict(event='REPLICATE_STARTED',replicate=r,seed=s))
            try:
                rng=np.random.Generator(np.random.PCG64(s))
                surrogate,ix,mapping=reference(arrays['y'],suite,trial_ids,rng,keys,bounds)
                assert trial_ids[ix].tolist()==cov['trial_ids']
                families=['B1','B4'] if suite=='N3' else CONTROL_FAMILIES
                if original is None:
                    original_arrays={k:(v[ix] if k not in ('active',) and not k.endswith('_active') else v) for k,v in arrays.items()}
                    original=predictors.score(original_arrays,families=families)
                    append_event(journal,dict(event='ORIGINAL_CONTROL_EXPOSURE',models=original,trial_ids=trial_ids[ix].tolist()))
                if suite=='N3':
                    lookup={int(t):i for i,t in enumerate(trial_ids)}
                    donors=[lookup[x['donor_trial']] for x in mapping['donors']]
                    ref_arrays=control_arrays(arrays,prep,surrogate,ix,wheel_donors=donors)
                else:ref_arrays=control_arrays(arrays,prep,surrogate,ix)
                scores=predictors.score(ref_arrays,filter_y=surrogate if suite!='N3' else None,families=families)
                assert set(scores)<=set(families) and 'B0' not in scores
                values=effect_vector(scores);gain=None
                if suite=='N3':
                    gain=effect_vector(scores)[0];wheel_gains.append(gain)
                    values=[scores['B4']['LL']/scores['B4']['unit_bins']]*len(CONTRASTS)
                mh=digest(mapping)
                append_event(journal,dict(event='REPLICATE_COMPLETE',replicate=r,seed=s,mapping_sha256=mh,
                    models=scores,reference_effects=values,wheel_gain=gain))
                replicates.append(values);mapping_hashes.append(mh);seeds.append(s)
            except Exception as exc:
                append_event(journal,dict(event='REPLICATE_FAILED_IMMUTABLE',replicate=r,seed=s,
                    completed_prefix=len(replicates),error=type(exc).__name__+': '+str(exc)))
                raise
        observed=effect_vector(original)
        if suite=='N3':observed=[original['B4']['LL']/original['B4']['unit_bins']]*len(CONTRASTS)
        out[suite]=dict(status='COMPLETE_FINITE_DESTRUCTIVE_REFERENCE',coverage=cov,replicates_completed=999,
            observed=observed,reference_effects=replicates,original_model_scores=original,mapping_sha256=mapping_hashes,seeds=seeds,
            statistic='B4 LL/unit-bin wheel reliance diagnostic copied across contrast slots' if suite=='N3' else 'Registered original-minus-comparator predictive gain',
            wheel_gain_original=effect_vector(original)[0] if suite=='N3' else None,
            wheel_gain_reference=wheel_gains if suite=='N3' else None,
            original_targets_preserved=True,D_filter_assimilates_surrogate_past_counts=suite!='N3',
            exchangeability='Destructive reference, not exact mechanistic or population null; nuisance imbalance/stationarity limitations retained',
            A_matching_diagnostics={k:v for k,v in reference_metadata.items() if k.startswith('A_warm_rate') or k.startswith('A_wheel_displacement')})
        append_event(journal,dict(event='SUITE_COMPLETE',replicates_completed=len(replicates),summary_sha256=digest(out[suite])))
    return out


def control_summary(records,expected_subjects):
    subjects=[r['subject'] for r in records]
    assert len(expected_subjects)==len(set(expected_subjects))>0
    assert len(subjects)==len(set(subjects)) and set(subjects)==set(expected_subjects)
    assert all(set(r['suites'])=={'N1','N2','N3','N4'} for r in records)
    assert all(p['status'] in ('COMPLETE_FINITE_DESTRUCTIVE_REFERENCE','UNAVAILABLE_REGISTERED_COVERAGE') for r in records for p in r['suites'].values())
    result={}
    for j,contrast in enumerate(CONTRASTS):
        panels={}
        for suite in ['N1','N2','N3','N4']:
            complete=[r for r in records if r['suites'][suite]['status']=='COMPLETE_FINITE_DESTRUCTIVE_REFERENCE'
                and r['suites'][suite]['observed'][j] is not None]
            if len(complete)<6:
                panels[suite]=dict(status='UNAVAILABLE_MINIMUM_PAIRED_MICE',n_mice=len(complete),p_reference=1.);continue
            observed=np.array([r['suites'][suite]['observed'][j] for r in complete])
            refs=np.array([[x[j] for x in r['suites'][suite]['reference_effects']] for r in complete],float)
            assert refs.shape==(len(complete),999) and np.isfinite(refs).all()
            medians=np.median(refs,axis=1);degradation=observed-medians
            panel=dict(status='EXPLORATORY_FINITE_REFERENCE',subjects=[r['subject'] for r in complete],n_mice=len(complete),
                observed_equal_mouse_mean=float(observed.mean()),reference_equal_mouse_means=refs.mean(axis=0).tolist(),
                p_reference=float((1+np.sum(refs.mean(axis=0)>=observed.mean()))/1000),
                mouse_original=observed.tolist(),mouse_reference_medians=medians.tolist(),mean_degradation=float(degradation.mean()),
                mice_above_reference_median=int(np.sum(degradation>0)),
                descriptive_disruption_gate=bool(np.sum(degradation>0)>=np.ceil(.75*len(complete)) and degradation.mean()>0),
                exact_mechanistic_null=False,validated=False)
            if suite=='N3':panel['statistic']='Copied B4-LL wheel reliance diagnostic; no D/C wheel-null claim'
            panels[suite]=panel
        adjusted=holm([panels[k]['p_reference'] for k in ['N1','N2','N3','N4']])
        for suite,p in zip(['N1','N2','N3','N4'],adjusted):panels[suite]['Holm4_reference_p']=float(p)
        result[contrast]=panels
    return result


def sensitivity_summary(rows,expected_subjects):
    expected={(s,c['id']) for s in expected_subjects for c in CASES}
    observed=[(r['subject'],r['case']) for r in rows]
    assert len(expected_subjects)==len(set(expected_subjects))>0
    assert len(observed)==len(set(observed))==len(expected) and set(observed)==expected
    out={}
    for case in CASES:
        cid=case['id'];records=[r for r in rows if r['case']==cid];panels={}
        for contrast in ['B4-B1','B4-B3','B4-B2']:
            left,right=CONTRASTS[contrast];valid=[r for r in records if left in r.get('models',{}) and right in r.get('models',{})]
            effects=[]
            for r in valid:
                a,b=r['models'][left],r['models'][right];assert a['unit_bins']==b['unit_bins']
                effects.append((a['LL']-b['LL'])/a['unit_bins'])
            panel=dict(n_mice=len(valid),subjects=[r['subject'] for r in valid],minimum6_coverage=len(valid)>=6,
                status='DESCRIPTIVE_SENSITIVITY' if len(valid)>=6 else 'UNAVAILABLE_MINIMUM_PAIRED_MICE',
                mouse_effects=effects,mandatory=cid not in ('S02','S03'),validated=False)
            if valid:
                # No new family of formal sensitivity hypothesis tests is introduced.
                d=np.asarray(effects);rng=np.random.Generator(np.random.PCG64(150101))
                boot=d[rng.integers(0,len(d),(10000,len(d)))].mean(axis=1)
                panel.update(equal_mouse_mean=float(d.mean()),CI95=np.quantile(boot,[.025,.975],method='linear').tolist(),positive_mice=int(np.sum(d>0)))
            panels[contrast]=panel
        out[cid]=panels
    return out


def run():
    gate,selection,candidates,ref=verify_E_gate()
    claim=P/'E_BATCH_CLAIM.json';record=dict(status='STARTED',attempt=1,E_batches=1,
        started_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),gate_sha256=sha(P/'E_EXPLORATORY_GATE.json'),Final_access=False)
    claim_attempt(claim,record)  # A residue after any interruption denies another E batch.
    with (R/'paper15_m1/COHORT.csv').open(encoding='utf8') as handle:labs={r['subject']:r['lab'] for r in csv.DictReader(handle)}
    mouse_rows=[];case_rows=[];control_rows=[]
    try:
        for subject in gate['subjects']:
            arrays,receipt=extract_role(subject,'E');dump(P/'results/E_exports'/(subject+'.json'),receipt)
            export=P/'work/E_exports'/(subject+'.npz');export.parent.mkdir(parents=True,exist_ok=True);assert not export.exists();np.savez_compressed(export,**arrays)
            predictors=FrozenPredictors(subject,selection,candidates)
            row=dict(subject=subject,lab=labs[subject],models=predictors.score(arrays),E_export_sha256=sha(export),trial_ids=arrays['trial_ids'].tolist())
            dump(P/'results/E_mice'/(subject+'.json'),row);mouse_rows.append(row)
            source,metadata=source_state(subject);wt,wp=wheel(source);times,labels=raw_E(subject)
            for case in CASES:
                path=P/'sensitivity_states'/subject/(case['id']+'.json');state=read_json(path)
                panel=dict(subject=subject,lab=labs[subject],case=case['id'],A_state_sha256=sha(path),status=state['status'])
                if state['status']=='A_PREPROCESSING_SEALED':
                    ca,thinning=case_arrays(subject,state,times,labels,wt,wp);scores,failed=score_case(subject,state,ca)
                    panel.update(models=scores,numerically_unavailable_families=failed,thinning_E=thinning,trial_ids=ca['trial_ids'].tolist())
                else:panel['unavailability_reasons']=state['unavailability_reasons']
                dump(P/'results/E_sensitivities'/subject/(case['id']+'.json'),panel);case_rows.append(panel)
            prep=read_json(P/'states'/(subject+'_A_PREPROCESSING.json'))
            suites=run_controls(subject,arrays,predictors,prep,next(x for x in ref['records'] if x['subject']==subject))
            controls=dict(subject=subject,lab=labs[subject],suites=suites)
            dump(P/'results/E_controls'/(subject+'.json'),controls);control_rows.append(controls)
            print(subject,'E original + 11 cases + fixed4x999 references sealed',flush=True)
        dump(P/'results/E_STATISTICS.json',analyze(mouse_rows,selection['subjects']))
        dump(P/'results/E_SENSITIVITY_SUMMARY.json',sensitivity_summary(case_rows,selection['subjects']))
        dump(P/'results/E_CONTROL_SUMMARY.json',control_summary(control_rows,selection['subjects']))
        record.update(status='COMPLETE_EXPLORATORY_E_BATCH',completed_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            mouse_count=len(mouse_rows),validated=False,result_hashes={n:sha(P/'results'/n) for n in ['E_STATISTICS.json','E_SENSITIVITY_SUMMARY.json','E_CONTROL_SUMMARY.json']})
        dump(claim,record)
    except Exception as exc:
        record.update(status='INTERRUPTED_OR_FAILED_IMMUTABLE_E_BATCH',error=type(exc).__name__+': '+str(exc),
            completed_mice=[x['subject'] for x in mouse_rows],completed_control_mice=[x['subject'] for x in control_rows])
        dump(claim,record);raise


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('action',choices=['prepare','run']);action=ap.parse_args().action
    prepare_reference_metadata() if action=='prepare' else run()
