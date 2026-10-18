"""Independent saved-certificate arithmetic and complete-set/journal audit.

No likelihood, optimizer, AD, FD, neural array load, or source request is made.
Reference RNG is reconstructed against zero arrays solely to verify donor maps.
"""
import importlib.metadata
from pathlib import PurePosixPath
import re
import numpy as np
from .source import P,R,E,read,sha,load_json
from .models import pg
from .controls import seed,reference,thinning_seed
from .reference_evaluation import digest,effect_vector


def archive_paths(root=P):
    return {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()
            and not {'work','__pycache__'}&set(p.relative_to(root).parts)
            and p.relative_to(root).as_posix()!='ARCHIVE_FREEZE.json' and p.suffix!='.pyc'}


def required_external_paths():
    required={str((E/n).relative_to(R).as_posix()) for n in
              ['baseline.json','goldenstandards.md','PRESERVATION_REGISTRATION.json']}
    required|={'paper15_m1/PROTOCOL_FREEZE.json','paper15_r1/ARCHIVE_FREEZE.json',
               'paper15_r1/SELECTION_FREEZE.json'}
    required|={'paper15_m1/'+n for n in read(R/'paper15_m1/PROTOCOL_FREEZE.json')['hashes']}
    old=read(R/'paper15_r1/ARCHIVE_FREEZE.json')
    required|={'paper15_r1/'+n for n in old['hashes']}
    required|=set(old['external_hashes'])
    required|=set(read(P/'METADATA_SOURCE_EXTERNAL_FREEZE.json')['hashes'])
    for name in ['C_READER_GATE.json','C_PRODUCTION_GATE.json','PRE_D_GATE.json']:
        if not (P/name).exists():continue
        gate=read(P/name)
        reviews=list(gate.get('independent_reviews',{}).values()) if name=='PRE_D_GATE.json' else [gate['independent_review']]
        if 'actual_C_physiology_review' in gate:reviews.append(gate['actual_C_physiology_review'])
        for item in reviews:
            required.add(item['path']);required.add(read(R/item['path'])['report_path'])
    return required


def verify_archive(freeze,root=P,repository=R,required_external=None):
    required={'saved_verify.py','saved_audit.py','test_saved_audit.py','reproduce.ps1','requirements.txt',
              'models.py','features.py','source.py','controls.py','statistics.py','report.py',
              'C_FIT_PLAN.json','SENSITIVITY_FIT_PLAN.json','C_READER_GATE.json','C_PRODUCTION_GATE.json',
              'SOURCE_FILE_FREEZE.json','REFERENCE_METADATA_FREEZE.json','results/FINAL_DELIVERY.json',
              'FINAL_SCIENTIFIC_REPORT.md'}
    assert required<=set(freeze['hashes']) and set(freeze['hashes'])==archive_paths(root),'Exact package manifest required'
    ext=required_external_paths() if required_external is None else required_external
    assert ext and ext<=set(freeze['external_hashes']),'Mandatory external source/review identities missing'
    for base,key in [(root,'hashes'),(repository,'external_hashes')]:
        for rel,h in freeze[key].items():
            parts=PurePosixPath(rel)
            assert not parts.is_absolute() and '..' not in parts.parts and '\\' not in rel
            assert re.fullmatch('[0-9a-f]{64}',h) and sha(base/rel)==h,rel
    delivery=read(root/'results/FINAL_DELIVERY.json')
    if delivery['D_BATCH_COMPLETE']:
        assert {'D_BATCH_CLAIM.json','PRE_D_GATE.json','FINAL_C_STATE_SEAL.json','ONE_SHOT_D_SPECIFICATION.json',
                'results/D_STATISTICS.json','results/D_CONTROL_SUMMARY.json','results/D_SENSITIVITY_SUMMARY.json',
                'results/D_SCIENTIFIC_VERDICTS.json'}<=set(freeze['hashes'])


def score_table(scores,unit_bins,families):
    assert type(unit_bins) is int and unit_bins>0 and set(scores)==set(families),'Exact scored family set required'
    for row in scores.values():
        assert type(row['unit_bins']) is int and row['unit_bins']==unit_bins
        assert np.isfinite(row['LL'])


def verify_thinning_receipt(state,receipts,role):
    assert role in ('C','D')
    if not state['case'].get('thin'):
        assert receipts is None;return
    assert type(receipts) is list and len(receipts)==len(state['units'])
    metrics={r['cluster_id']:r for r in state['physiology']}
    for unit,row in zip(state['units'],receipts):
        uuid=state['metadata']['native_uuid_list'][unit];p=min(1.,2./metrics[unit]['C_rate_Hz'])
        s=thinning_seed(state['subject'],uuid,role)
        assert set(row)=={'unit','uuid','role','p','seed','draw_count','kept'}
        assert row['unit']==unit and row['uuid']==uuid and row['role']==role and row['p']==p and row['seed']==s
        n=row['draw_count'];kept=row['kept']
        assert type(n) is int and type(kept) is int and 0<=kept<=n
        rng=np.random.Generator(np.random.PCG64(s));actual=0;remaining=n
        while remaining:
            count=min(remaining,1000000);actual+=int(np.sum(rng.random(count)<p));remaining-=count
        assert actual==kept


def verify_optimizer_history(record):
    hist=record['optimizer_history'];assert len(hist)==record['iterations']<=2000
    assert [x['iteration'] for x in hist]==list(range(1,len(hist)+1))
    calls=[x['calls'] for x in hist]
    assert calls==sorted(calls) and all(0<c<=record['optimizer_objective_calls'] for c in calls)
    assert type(record['budget_exhausted']) is bool and record['budget_exhausted']==(record['optimizer_status']==1)
    # SciPy may finish the current line search after maxfun. Preserve its failed
    # endpoint as unavailable; the over-budget endpoint can never become PASS.
    assert record['optimizer_objective_calls']<=80000 or (record['status']=='NUMERICAL_FAIL' and record['budget_exhausted'])
    assert all(np.isfinite([x['objective'],x['PG'],x['full_gradient_inf']]).all() for x in hist)


def numerical_record(record,config,state,state_hash):
    from .seal_C import verify_endpoint
    assert record['status'] in ('NUMERICAL_PASS','NUMERICAL_FAIL') and 'error' not in record
    assert record['fit_role']=='C' and record['D_neural_fit_data'] is False and record['Development_coefficients_reused'] is False
    # Reconstruct shape/mask/bounds using zero synthetic arrays, never saved neural data.
    from .models import Model
    u=len(state['units']);active=list(state['active'])
    if config['family']=='C':
        key=f"C_r{config['rank']}_tau{config['tau']}";active+=state['C_scales'][key]['q_scale']['active']
    model=Model(np.zeros((1,2,len(active))),np.zeros((1,2,u)),config['family'],ridge=config['ridge'],
                k=config.get('k',2),active=active,warm=1,nuisance=state.get('nuisance_columns',37))
    assert record['free_parameters']==model.size and record['bounds']==[list(x) for x in model.bounds]
    theta=np.asarray(record['coefficients']);initial=np.asarray(record['initial']);g=np.asarray(record['independent']['analytic_gradient'])
    assert theta.shape==initial.shape==g.shape==(model.size,) and np.isfinite(initial).all()
    ind=record['independent']
    for name in ['analytic_gradient','AD_gradient','AD_coordinate_absolute','AD_coordinate_scaled']:
        assert np.asarray(ind[name]).shape==(model.size,),name
    for item in ind['FD']:
        for name in ['numerical_gradient','coordinate_absolute','coordinate_scaled']:
            assert np.asarray(item[name]).shape==(model.size,),name
    assert ((initial>=np.asarray(model.bounds)[:,0])&(initial<=np.asarray(model.bounds)[:,1])).all()
    assert record['full_gradient_inf']==float(abs(g).max(initial=0)) and record['PG']==pg(theta,g,model.bounds)
    verify_optimizer_history(record)
    bins=len(state['trial_ids'])*10 if 'case' not in state else state['trial_counts']['C']*int(round(.5/state['delta']))
    assert record['training_population_bins']==bins and record['training_unit_bins']==bins*u
    if record['status']=='NUMERICAL_PASS':return verify_endpoint(record,config,state_hash)
    assert record['configuration']==config and record['C_state_sha256']==state_hash and record['attempt']==1
    assert record['production_gate_sha256']==sha(P/'C_PRODUCTION_GATE.json')
    # A completed ordinary NUMFAIL must retain a concrete original failed gate.
    assert not (record['finite_all'] and record['exact_bounds'] and record['PG']<=.001
                and record['independent']['PASS'] and not record['budget_exhausted'])
    return False


def require_exact_files(folder,expected):
    observed={p.relative_to(P).as_posix() for p in folder.rglob('*.json')}
    assert observed==set(expected),'Missing or unplanned certificate: '+str(sorted(observed^set(expected)))


def audit_fits():
    plan=read(P/'C_FIT_PLAN.json');sp=read(P/'SENSITIVITY_FIT_PLAN.json');subjects=plan['subjects']
    main=[(s,c) for dynamic in [False,True] for s in subjects for c in plan['configurations'] if (c['family'] in ('C','D','S'))==dynamic]
    expected={'fits/'+s+'/'+c['id']+'.json' for s,c in main}
    sexpected={'sensitivity_fits/'+x['subject']+'/'+x['case']+'/'+x['family']+'.json' for x in sp['attempts']}
    # Only a documented critical-stop prefix permits incomplete C. Completed D never does.
    if (P/'results/C_MAIN_REQUIRED_STOP.json').exists():
        stop=read(P/'results/C_MAIN_REQUIRED_STOP.json');entries=stop['attempts'];assert entries
        assert [(x['subject'],x['configuration']) for x in entries]==main[:len(entries)]
        expected={f"fits/{s}/{c['id']}.json" for s,c in main[:len(entries)]};sexpected=set()
        assert not (P/'D_BATCH_CLAIM.json').exists()
        rows=entries
    else:
        complete=read(P/'results/C_MAIN_ATTEMPTS_COMPLETE.json');rows=complete['attempts']
        assert complete['attempted']==plan['expected_attempts']==len(main)==len(rows)
        assert [(x['subject'],x['configuration']) for x in rows]==main
    require_exact_files(P/'fits',expected)
    sensstop=P/'results/C_SENSITIVITY_REQUIRED_STOP.json'
    srows=[]
    if sexpected:
        doc=read(sensstop if sensstop.exists() else P/'results/C_SENSITIVITY_ATTEMPTS_COMPLETE.json')
        srows=doc['attempts'] if sensstop.exists() else doc['records']
        assert [x['item'] for x in srows]==sp['attempts'][:len(srows)]
        if sensstop.exists():
            assert not (P/'D_BATCH_CLAIM.json').exists()
            sexpected={f"sensitivity_fits/{x['item']['subject']}/{x['item']['case']}/{x['item']['family']}.json" for x in srows}
        else:assert doc['attempted']==sp['expected_attempts']==len(srows)==len(sp['attempts'])
    require_exact_files(P/'sensitivity_fits',sexpected)
    verified=[]
    for row in rows+srows:
        sensitivity='item' in row
        if sensitivity:
            item=row['item'];s=item['subject'];path=P/f"sensitivity_fits/{s}/{item['case']}/{item['family']}.json"
            statepath=P/f"sensitivity_states/{s}/{item['case']}.json"
            config=dict(id=item['family'],family=item['family'],ridge=item['ridge'],seed=11);sh=item['state_sha256']
        else:
            s=row['subject'];config=row['configuration'];path=P/f"fits/{s}/{config['id']}.json"
            statepath=P/'states'/(s+'_C_PREPROCESSING.json');sh=plan['state_hashes'][s]
        record=read(path);assert sha(path)==row['sha256'] and record['status']==row['status'] and sha(statepath)==sh
        state=read(statepath)
        if sensitivity and state['case'].get('thin'):verify_thinning_receipt(state,state['thinning_C'],'C')
        if 'error' in record or record['status']=='STARTED':
            assert row is (rows+srows)[-1] and ((P/'results/C_MAIN_REQUIRED_STOP.json').exists() or sensstop.exists())
            assert not (P/'D_BATCH_CLAIM.json').exists();verified.append(False)
        else:verified.append(numerical_record(record,config,state,sh))
    return dict(main_attempts=len(rows),sensitivity_attempts=len(srows),passing_endpoint_certificates=sum(verified),
                preserved_failed_or_interrupted_certificates=len(verified)-sum(verified))


def audit_control_panel(panel,events,subject,suite,metadata,families):
    cov=metadata['coverage'][suite]
    assert panel['coverage']==cov
    assert events[0]==dict(event='SUITE_STARTED',subject=subject,suite=suite,coverage=cov,replicates=999)
    if not cov['available']:
        assert panel==dict(status='UNAVAILABLE_REGISTERED_COVERAGE',coverage=cov,replicates_completed=0)
        assert events==[events[0],dict(event='UNAVAILABLE_REGISTERED_COVERAGE',coverage=cov)];return 0
    assert panel['status']=='COMPLETE_FINITE_DESTRUCTIVE_REFERENCE' and panel['replicates_completed']==999
    assert all(len(panel[k])==999 for k in ['reference_effects','mapping_sha256','seeds'])
    expected_q=len(cov['trial_ids'])*80;selected=[f for f in (['B1','B4'] if suite=='N3' else ['B1','B2','B3','B4','D','C','S']) if f in families]
    score_table(panel['original_model_scores'],expected_q,selected)
    observed=effect_vector(panel['original_model_scores'])
    if suite=='N3':
        assert panel['wheel_gain_original']==observed[0] and len(panel['wheel_gain_reference'])==999
        observed=[panel['original_model_scores']['B4']['LL']/expected_q]*6
    else:assert panel['wheel_gain_original'] is None and panel['wheel_gain_reference'] is None
    assert panel['observed']==observed and panel['original_targets_preserved'] is True
    assert panel['D_filter_assimilates_surrogate_past_counts']==(suite!='N3')
    assert len(events)==2001 and events[-1]==dict(event='SUITE_COMPLETE',replicates_completed=999,summary_sha256=digest(panel))
    assert events[2]==dict(event='ORIGINAL_CONTROL_EXPOSURE',models=panel['original_model_scores'],trial_ids=cov['trial_ids'])
    ids=np.asarray(metadata['D_trial_ids']);dummy=np.zeros((len(ids),20,8),int)
    keys=None if suite in ('N1','N4') else [tuple(x) for x in metadata['keys_'+suite]]
    for r in range(999):
        start=events[1 if r==0 else 2*r+2];event=events[3 if r==0 else 2*r+3]
        s=seed(suite,subject,'D',r)
        assert start==dict(event='REPLICATE_STARTED',replicate=r,seed=s)
        assert event['event']=='REPLICATE_COMPLETE' and event['replicate']==r and event['seed']==panel['seeds'][r]==s
        _,ix,mapping=reference(dummy,suite,ids,np.random.Generator(np.random.PCG64(s)),keys,metadata['role_bounds'])
        assert ids[ix].tolist()==cov['trial_ids'] and event['mapping_sha256']==panel['mapping_sha256'][r]==digest(mapping)
        score_table(event['models'],expected_q,selected);values=effect_vector(event['models'])
        if suite=='N3':
            assert event['wheel_gain']==panel['wheel_gain_reference'][r]==values[0]
            values=[event['models']['B4']['LL']/expected_q]*6
        else:assert event['wheel_gain'] is None
        assert event['reference_effects']==panel['reference_effects'][r]==values
    return 999


def audit_D():
    from .admission import verify_pre_D_gate
    from .source import roster
    from .d_batch import complete_saved_statistics
    gate=verify_pre_D_gate();spec=read(P/'ONE_SHOT_D_SPECIFICATION.json');subjects=spec['primary_subjects']
    claim=read(P/'D_BATCH_CLAIM.json');seal=read(P/'FINAL_C_STATE_SEAL.json')
    assert claim['status']=='COMPLETE_REGISTERED_DESCRIPTIVE_D_BATCH' and claim['attempt']==claim['D_batches']==1
    assert claim['subjects']==subjects==gate['subjects']==seal['primary_subjects'] and claim['mouse_count']==len(subjects)
    assert claim['gate_sha256']==sha(P/'PRE_D_GATE.json') and claim['C_state_seal_sha256']==sha(P/'FINAL_C_STATE_SEAL.json')
    assert claim['new_fits']==0 and claim['second_assessment_authorized'] is False and claim['current_stage']=='COMPLETE'
    assert claim['D_neural_access_attempted'] is True and claim['D_projection_completed_subjects']==subjects
    assert set(claim['result_hashes'])=={'D_STATISTICS.json','D_SENSITIVITY_SUMMARY.json','D_CONTROL_SUMMARY.json','D_SCIENTIFIC_VERDICTS.json'}
    for name,h in claim['result_hashes'].items():assert sha(P/'results'/name)==h
    expected={f'results/D_mice/{s}.json' for s in subjects};require_exact_files(P/'results/D_mice',expected)
    require_exact_files(P/'results/D_controls',{f'results/D_controls/{s}.json' for s in subjects})
    require_exact_files(P/'results/D_sensitivities',{f'results/D_sensitivities/{s}/S{i:02}.json' for s in subjects for i in range(1,12)})
    journals={f'results/D_control_journals/{s}/{n}.jsonl' for s in subjects for n in ['N1','N2','N3','N4']}
    assert {p.relative_to(P).as_posix() for p in (P/'results/D_control_journals').rglob('*') if p.is_file()}==journals
    labs={r['subject']:r['lab'] for r in roster()};refs={r['subject']:r for r in read(P/'REFERENCE_METADATA_FREEZE.json')['records']}
    rows=[];cases=[];controls=[];total=0
    for s in subjects:
        row=read(P/f'results/D_mice/{s}.json');rm=refs[s];families=[f for f,ss in spec['family_subjects'].items() if s in ss]
        assert row['subject']==s and row['lab']==labs[s] and row['trial_ids']==rm['D_trial_ids']
        assert row['C_preprocessing_sha256']==sha(P/f'states/{s}_C_PREPROCESSING.json')
        assert re.fullmatch('[0-9a-f]{64}',row['D_export_sha256'])
        score_table(row['models'],len(row['trial_ids'])*80,families);rows.append(row)
        for i in range(1,12):
            cid=f'S{i:02}';r=read(P/f'results/D_sensitivities/{s}/{cid}.json');statepath=P/f'sensitivity_states/{s}/{cid}.json';state=read(statepath)
            assert r['subject']==s and r['case']==cid and r['lab']==labs[s] and r['C_state_sha256']==sha(statepath)
            assert r['status']==state['status']
            if state['status']=='C_PREPROCESSING_SEALED':
                met=state['metadata'];ids=np.flatnonzero(np.asarray(met['valid'])&(np.asarray(met['roles'])=='D')).tolist()
                assert r['trial_ids']==ids
                good=[f for f in ['B0','B1','B2','B3','B4'] if read(P/f'sensitivity_fits/{s}/{cid}/{f}.json')['status']=='NUMERICAL_PASS']
                assert r['numerically_unavailable_families']==[f for f in ['B0','B1','B2','B3','B4'] if f not in good]
                score_table(r['models'],len(ids)*int(round(.5/state['delta']))*len(state['units']),good)
                verify_thinning_receipt(state,r['thinning_D'],'D')
            else:assert not r.get('models') and r['unavailability_reasons']==state['unavailability_reasons']
            cases.append(r)
        control=read(P/f'results/D_controls/{s}.json');assert control['subject']==s and control['lab']==labs[s]
        assert set(control['suites'])=={'N1','N2','N3','N4'}
        for suite,panel in control['suites'].items():
            events=[load_json(line) for line in (P/f'results/D_control_journals/{s}/{suite}.jsonl').read_text(encoding='utf8').splitlines()]
            total+=audit_control_panel(panel,events,s,suite,rm,families)
        controls.append(control)
    rebuilt=complete_saved_statistics(rows,cases,controls,spec)
    for name,value in zip(['D_STATISTICS.json','D_SENSITIVITY_SUMMARY.json','D_CONTROL_SUMMARY.json','D_SCIENTIFIC_VERDICTS.json'],rebuilt):
        assert value==read(P/'results'/name),name
    from .anatomy_report import build as anatomy_description
    anatomy,table=anatomy_description(write=False)
    assert anatomy==read(P/'results/LAYER_PROXY_ASSOCIATIONS.json')
    assert table==(P/'tables/ANATOMY_LAYER_PROXY.csv').read_bytes()
    assert total==spec['expected_reference_bundles']
    return dict(saved_statistics_exact=True,main_mouse_rows=len(rows),case_rows=len(cases),
                complete_reference_bundles=total,journals_verified=len(journals),anatomy_description_reproduced=True)
