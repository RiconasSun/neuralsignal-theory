"""Arithmetic/hash audit of sealed outputs; never loads neural arrays or refits."""
import csv
import json
import numpy as np
from .source import P,R
from .training import sha,configurations,baseline_availability,admitted
from .models import pg,Model
from .statistics import analyze
from .evaluation import control_summary,sensitivity_summary,verify_E_gate,digest,effect_vector
from .controls import seed,reference


def read(path):return json.loads(path.read_text(encoding='utf8'))


def score_table(scores,expected_unit_bins):
    assert expected_unit_bins>0
    for row in scores.values():assert row['unit_bins']==expected_unit_bins and np.isfinite(row['LL'])


def original_control(panel,suite,expected_unit_bins):
    scores=panel['original_model_scores'];score_table(scores,expected_unit_bins)
    expected=effect_vector(scores)
    if suite=='N3':
        assert panel['wheel_gain_original']==expected[0]
        expected=[scores['B4']['LL']/scores['B4']['unit_bins']]*6
    assert panel['observed']==expected


def numerical_record(record,sensitivity=False,state=None):
    assert record['status'] in ('NUMERICAL_PASS','NUMERICAL_FAIL')
    if 'coefficients' not in record:
        assert record['status']=='NUMERICAL_FAIL' and record['error'];return
    theta=np.asarray(record['coefficients']);check=record['independent']
    g=np.asarray(check['analytic_gradient']);ad=np.asarray(check['AD_gradient'])
    assert theta.shape==g.shape==ad.shape and np.isfinite(theta).all() and np.isfinite(g).all() and np.isfinite(ad).all()
    absolute=np.abs(g-ad);scaled=absolute/np.maximum(1,np.maximum(np.abs(g),np.abs(ad)))
    np.testing.assert_allclose(absolute,check['AD_coordinate_absolute'],rtol=0,atol=1e-14)
    np.testing.assert_allclose(scaled,check['AD_coordinate_scaled'],rtol=0,atol=1e-14)
    assert check['AD_max_scaled']==float(scaled.max(initial=0))
    assert [f['step'] for f in check['FD']]==[1e-4,1e-5,1e-6]
    for f in check['FD']:
        fd=np.asarray(f['numerical_gradient']);error=np.abs(fd-g);relative=error/np.maximum(1,np.maximum(np.abs(g),np.abs(fd)))
        np.testing.assert_allclose(error,f['coordinate_absolute'],rtol=0,atol=1e-14)
        np.testing.assert_allclose(relative,f['coordinate_scaled'],rtol=0,atol=1e-14)
        assert f['max_scaled']==float(relative.max(initial=0)) and f['max_absolute']==float(error.max(initial=0))
    independent=(abs(check['objective']-check['AD_objective'])<=1e-8*max(1,abs(check['objective']))
        and check['AD_max_scaled']<=1e-5 and all(f['max_scaled']<=1e-5 for f in check['FD']))
    assert check['PASS']==independent
    assert record['full_gradient_inf']==float(np.max(np.abs(g)))
    assert abs(record['objective']-check['objective'])<1e-12
    if not sensitivity:
        bounds=np.array(record['bounds']);assert theta.shape==(len(bounds),)
        assert record['PG']==pg(theta,g,bounds)
        accepted=bool(((theta>=bounds[:,0])&(theta<=bounds[:,1])).all()) and record['PG']<=.001 and independent and not record['budget_exhausted']
        assert (record['status']=='NUMERICAL_PASS')==accepted
    else:
        assert state is not None and state['status']=='A_PREPROCESSING_SEALED'
        units=len(state['units']);p=len(state['active']);warm=state['warm'];length=warm+int(round(.5/state['delta']))
        # Synthetic zeros establish the registered parameter mask/bounds only.
        # No real feature/count arrays or likelihood values are reconstructed.
        model=Model(np.zeros((1,length,p)),np.zeros((1,length,units)),record['plan_item']['family'],
            ridge=record['plan_item']['ridge'],active=state['active'],warm=warm,delta=state['delta'],nuisance=state['nuisance_columns'])
        bounds=np.asarray(model.bounds);assert theta.shape==(model.size,)==(record['free_parameters'],)
        assert record['PG']==pg(theta,g,bounds)
        accepted=bool(((theta>=bounds[:,0])&(theta<=bounds[:,1])).all()) and record['PG']<=.001 and independent and record['optimizer_status']!=1
        assert (record['status']=='NUMERICAL_PASS')==accepted


def audit_fits():
    plan=read(P/'A_FIT_PLAN.json');assert plan['subjects']==admitted() and plan['configurations']==configurations()
    records=[]
    for subject in plan['subjects']:
        for config in plan['configurations']:
            record=read(P/'fits'/subject/(config['id']+'.json'))
            assert record['subject']==subject and record['configuration']==config and record['attempt']==1
            assert record['production_gate_sha256']==sha(P/'PRODUCTION_GATE.json')
            assert record['A_preprocessing_sha256']==sha(P/'states'/(subject+'_A_PREPROCESSING.json'))
            numerical_record(record);records.append(record)
    assert len(records)==plan['total_main']==len(plan['subjects'])*61<=732
    for name,baseline in [('BASELINE_ATTEMPTS_COMPLETE.json',True),('DYNAMIC_ATTEMPTS_COMPLETE.json',False)]:
        marker=read(P/'results'/name);subset=[r for r in records if r['configuration']['family'].startswith('B')==baseline]
        assert marker['attempted']==marker['completed']==len(subset)
        assert marker['numerical_pass']==sum(r['status']=='NUMERICAL_PASS' for r in subset)
        assert set(marker['attempt_hashes'])=={r['subject']+'/'+r['configuration']['id'] for r in subset}
        for key,h in marker['attempt_hashes'].items():assert sha(P/'fits'/(key+'.json'))==h
        if baseline:assert baseline_availability(subset,plan['subjects'])['PRIMARY_BASELINE_NUMERICAL_GATE']==marker['PRIMARY_BASELINE_NUMERICAL_GATE']
    return records


def audit_selection():
    from .selection import choose,groups,nominal
    candidates=read(P/'results/B_CANDIDATE_SCORES.json');selection=read(P/'SELECTION_FREEZE.json');subjects=selection['subjects']
    assert subjects==admitted()==read(P/'A_FIT_PLAN.json')['subjects']
    registered=groups();assert len(candidates)==len({x['id'] for x in candidates})==len(registered)
    assert {x['id'] for x in candidates}==set(registered)
    for entry in candidates:
        assert entry['configurations']==registered[entry['id']] and entry['nominal_parameters']==nominal(entry['configurations'][0])
    assert len(candidates)==37 and selection['candidates_sha256']==sha(P/'results/B_CANDIDATE_SCORES.json')
    for entry in candidates:
        valid=all(read(P/'fits'/s/(c['id']+'.json'))['status']=='NUMERICAL_PASS' for s in subjects for c in entry['configurations'])
        assert entry['available']==valid
        if not valid:continue
        assert [x['subject'] for x in entry['mouse_scores']]==subjects
        for row in entry['mouse_scores']:
            assert row['unit_bins']>0 and row['LL_per_unit_bin']==row['LL']/row['unit_bins']
            assert row['fit_hashes']==[sha(P/'fits'/row['subject']/(c['id']+'.json')) for c in entry['configurations']]
        assert entry['equal_mouse_LL_per_unit_bin']==float(np.mean([r['LL_per_unit_bin'] for r in entry['mouse_scores']]))
    for family in ['B0','B1','B2','B3','B4','D','C','S']:
        eligible=[c for c in candidates if c['configurations'][0]['family']==family]
        if family=='S':
            kd=next((x['configurations'][0]['k'] for x in candidates if x['id']==selection['selected']['D']),None)
            eligible=[x for x in eligible if kd is not None and x['configurations'][0]['k']==kd+1]
        winner=choose(eligible);assert selection['selected'][family]==(winner['id'] if winner else None)
    return selection


def audit_E():
    verify_E_gate()  # JSON/hash-only predecessor validation; no extraction/scoring.
    subjects=read(P/'SELECTION_FREEZE.json')['subjects'];assert subjects==admitted()==read(P/'A_FIT_PLAN.json')['subjects']
    claim=read(P/'E_BATCH_CLAIM.json')
    assert claim['status']=='COMPLETE_EXPLORATORY_E_BATCH' and claim['attempt']==claim['E_batches']==1
    assert claim['gate_sha256']==sha(P/'E_EXPLORATORY_GATE.json') and claim['Final_access'] is False
    assert claim['mouse_count']==len(subjects)
    assert set(claim['result_hashes'])=={'E_STATISTICS.json','E_SENSITIVITY_SUMMARY.json','E_CONTROL_SUMMARY.json'}
    with (R/'paper15_m1/COHORT.csv').open(encoding='utf8') as f:labs={r['subject']:r['lab'] for r in csv.DictReader(f)}
    rows=[read(P/'results/E_mice'/(s+'.json')) for s in subjects]
    assert all(r['subject']==s and r['lab']==labs[s] for s,r in zip(subjects,rows))
    refmeta=read(P/'REFERENCE_METADATA_FREEZE.json')
    for row in rows:
        rm=next(r for r in refmeta['records'] if r['subject']==row['subject'])
        assert row['trial_ids']==rm['E_trial_ids'];score_table(row['models'],len(row['trial_ids'])*10*8)
    stats=analyze(rows,subjects);assert stats==read(P/'results/E_STATISTICS.json')
    cases=[]
    for s in subjects:
        for i in range(1,12):
            cid=f'S{i:02}';r=read(P/'results/E_sensitivities'/s/(cid+'.json'))
            assert r['subject']==s and r['case']==cid and r['lab']==labs[s]
            statepath=P/'sensitivity_states'/s/(cid+'.json');assert r['A_state_sha256']==sha(statepath)
            state=read(statepath);assert r['status']==state['status']
            if state['status']=='A_PREPROCESSING_SEALED':
                metadata=state['metadata'];ids=np.flatnonzero(np.asarray(metadata['valid'])&(np.asarray(metadata['roles'])=='E')).tolist()
                assert r['trial_ids']==ids
                score_table(r['models'],len(ids)*int(round(.5/state['delta']))*len(state['units']))
            else:assert not r.get('models')
            cases.append(r)
    assert sensitivity_summary(cases,subjects)==read(P/'results/E_SENSITIVITY_SUMMARY.json')
    controls=[read(P/'results/E_controls'/(s+'.json')) for s in subjects]
    assert all(r['subject']==s and r['lab']==labs[s] for s,r in zip(subjects,controls))
    for row in controls:
        metadata=next(r for r in refmeta['records'] if r['subject']==row['subject'])
        ids=np.asarray(metadata['E_trial_ids']);dummy=np.zeros((len(ids),20,8),int)
        for suite,panel in row['suites'].items():
            path=P/'results/E_control_journals'/row['subject']/(suite+'.jsonl')
            events=[json.loads(line) for line in path.read_text(encoding='utf8').splitlines()]
            assert events[0]['event']=='SUITE_STARTED' and events[0]['subject']==row['subject'] and events[0]['suite']==suite
            done=[e for e in events if e['event']=='REPLICATE_COMPLETE'];starts=[e for e in events if e['event']=='REPLICATE_STARTED']
            if panel['status']=='UNAVAILABLE_REGISTERED_COVERAGE':
                assert not done and not starts and events[-1]['event']=='UNAVAILABLE_REGISTERED_COVERAGE';continue
            expected_q=len(panel['coverage']['trial_ids'])*10*8
            original_control(panel,suite,expected_q)
            originals=[e for e in events if e['event']=='ORIGINAL_CONTROL_EXPOSURE'];assert len(originals)==1
            assert originals[0]['models']==panel['original_model_scores'] and originals[0]['trial_ids']==panel['coverage']['trial_ids']
            assert events[-1]['event']=='SUITE_COMPLETE' and events[-1]['summary_sha256']==digest(panel)
            assert len(done)==len(starts)==999 and [e['replicate'] for e in done]==list(range(999))==[e['replicate'] for e in starts]
            keys=None if suite in ('N1','N4') else [tuple(k) for k in metadata['keys_'+suite]]
            for r,(event,start) in enumerate(zip(done,starts)):
                s=seed(suite,row['subject'],'E',r)
                assert event['seed']==start['seed']==panel['seeds'][r]==s
                _,ix,mapping=reference(dummy,suite,ids,np.random.Generator(np.random.PCG64(s)),keys,metadata['role_bounds'])
                assert ids[ix].tolist()==panel['coverage']['trial_ids']
                assert event['mapping_sha256']==panel['mapping_sha256'][r]==digest(mapping)
                assert 'B0' not in event['models'] and len(event['models'])<=7
                score_table(event['models'],expected_q)
                values=effect_vector(event['models'])
                if suite=='N3':
                    assert event['wheel_gain']==panel['wheel_gain_reference'][r]==values[0]
                    values=[event['models']['B4']['LL']/event['models']['B4']['unit_bins']]*6
                assert event['reference_effects']==panel['reference_effects'][r]==values
    assert control_summary(controls,subjects)==read(P/'results/E_CONTROL_SUMMARY.json')
    for name,h in claim['result_hashes'].items():assert sha(P/'results'/name)==h
    return dict(main_mouse_rows=len(rows),case_rows=len(cases),control_mice=len(controls),
        complete_reference_bundles=sum(panel.get('replicates_completed',0) for row in controls for panel in row['suites'].values()))


def audit_all():
    records=audit_fits();selection=audit_selection()
    plan=read(P/'SENSITIVITY_FIT_PLAN.json');complete=read(P/'results/SENSITIVITY_ATTEMPTS_COMPLETE.json')
    assert complete['attempted']==complete['completed']==len(plan['attempts'])
    for item in plan['attempts']:
        path=P/'sensitivity_fits'/item['subject']/item['case']/(item['family']+'.json');record=read(path)
        assert record['plan_item']==item and record['attempt']==1 and record['sensitivity_gate_sha256']==sha(P/'SENSITIVITY_GATE.json')
        state=read(P/'sensitivity_states'/item['subject']/(item['case']+'.json'));assert sha(P/'sensitivity_states'/item['subject']/(item['case']+'.json'))==item['state_sha256']
        numerical_record(record,True,state)
    from .anatomy import build
    anatomy,table=build(write=False)
    assert anatomy==read(P/'results/LAYER_PROXY_ASSOCIATIONS.json') and table==(P/'tables/ANATOMY_LAYER_PROXY.csv').read_bytes()
    return dict(main_attempts_verified=len(records),main_numerical_pass=sum(r['status']=='NUMERICAL_PASS' for r in records),
        sensitivity_attempts_verified=len(plan['attempts']),B_winners=selection['selected'],E=audit_E(),layer_proxy_description_reproduced=True)
