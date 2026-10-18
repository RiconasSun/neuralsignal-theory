"""Independent actual saved D arithmetic; no arrays/likelihood/model imports."""
from pathlib import Path
from collections import Counter
import csv,datetime,hashlib,itertools,json,re,socket
import numpy as np
R=Path(__file__).resolve().parents[4];P=R/'paper15_final1';E=Path(__file__).parent
def denied(*a,**k):raise PermissionError('Final results review denies arrays/network')
np.load=denied;socket.socket.connect=denied;socket.create_connection=denied
hashes={}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):
    assert p.suffix in ('.json','.jsonl') and 'work' not in p.relative_to(P).parts
    raw=p.read_bytes();hashes[p.relative_to(P).as_posix()]=hashlib.sha256(raw).hexdigest();return json.loads(raw)
def dig(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def holm(p):
    out=[None]*len(p);running=0.
    for rank,i in enumerate(sorted(range(len(p)),key=lambda j:p[j])):
        running=max(running,p[i]*(len(p)-rank));out[i]=min(1.,running)
    return out
C={'B4-B1':('B4','B1'),'B4-B3':('B4','B3'),'B4-B2':('B4','B2'),'D-B4':('D','B4'),'C-B4':('C','B4'),'D-S':('D','S')}
secondary=list(C)[1:];mandatory=['S01','S04','S05','S06','S07','S08','S09','S10','S11']
def effect(m):return [None if a not in m or b not in m else (m[a]['LL']-m[b]['LL'])/m[a]['unit_bins'] for a,b in C.values()]
def scores(m,q,f):
    assert set(m)==set(f)
    for r in m.values():assert type(r['unit_bins']) is int and r['unit_bins']==q and np.isfinite(r['LL'])
def mapping(ids,suite,s,rep,rm):
    seed=int.from_bytes(hashlib.sha256(f'P15-M1|150107|{suite}|{s}|D|{rep}'.encode()).digest()[:8],'big');rng=np.random.Generator(np.random.PCG64(seed))
    if suite=='N1':return seed,dict(offsets=[dict(trial=int(t),offset=int(rng.integers(1,20))) for t in sorted(ids)],donors=None)
    donors={}
    if suite=='N4':
        a,b=rm['role_bounds'];blocks=[list(range(k,k+5)) for k in range(a,b,5) if k+5<=b and set(range(k,k+5))<=set(ids)]
        if len(blocks)>=2:
            shift=int(rng.integers(1,len(blocks)));rolled=np.roll(np.array(blocks),shift,axis=0)
            donors={t:int(d) for block,db in zip(blocks,rolled) for t,d in zip(block,db)}
    else:
        keys=[tuple(k) for k in rm['keys_'+suite]];assert len(keys)==len(ids)
        for key in sorted(set(keys)):
            group=sorted(int(t) for t,k in zip(ids,keys) if k==key)
            if len(group)>=2:donors.update(zip(group,np.roll(group,int(rng.integers(1,len(group)))).tolist()))
    return seed,dict(donors=[dict(target_trial=int(t),donor_trial=donors[int(t)]) for t in ids if int(t) in donors])
def stats(d,labs,contrast,stored):
    d=np.asarray(d);n=len(d);assert n==6
    boot=d[np.random.Generator(np.random.PCG64(150101)).integers(0,n,(10000,n))].mean(axis=1)
    ci=np.quantile(boot,[.025,.975],method='linear').tolist();null=np.array([np.mean(d*np.array(s)) for s in itertools.product([-1.,1.],repeat=n)])
    p=float(np.mean(null>=d.mean()-1e-14)) if contrast=='B4-B1' else float(np.mean(abs(null)>=abs(d.mean())-1e-14))
    assert stored['equal_mouse_mean']==float(d.mean()) and stored['paired_sign_flip_p']==p and stored['CI95']==ci and stored['CI_width']==ci[1]-ci[0]
    assert stored['median']==float(np.median(d)) and stored['IQR']==np.quantile(d,[.25,.75],method='linear').tolist() and stored['SD']==float(d.std(ddof=1))
    assert stored['positive_mice']==int(sum(d>0)) and stored['positive_fraction']==float(np.mean(d>0))
    assert stored['leave_one_mouse_out_means']==[float(np.delete(d,j).mean()) for j in range(n)]
    unique=sorted(set(labs));lm={l:float(d[np.array(labs)==l].mean()) for l in unique};ll={l:float(d[np.array(labs)!=l].mean()) for l in unique}
    assert stored['lab_means']==lm and stored['equal_lab_mean']==float(np.mean(list(lm.values()))) and stored['leave_one_lab_out_means']==ll
    ix=np.random.Generator(np.random.PCG64(150102)).integers(0,len(unique),(10000,len(unique)));sums=np.array([d[np.array(labs)==l].sum() for l in unique]);sizes=np.array([sum(np.array(labs)==l) for l in unique])
    assert stored['lab_block_bootstrap_CI95']==np.quantile(sums[ix].sum(axis=1)/sizes[ix].sum(axis=1),[.025,.975],method='linear').tolist()
    assert stored['n_mice']==6 and stored['n_labs']==4 and stored['bootstrap_replicates']==10000 and stored['bootstrap_seed']==150101 and stored['lab_bootstrap_seed']==150102
    assert stored['heldout_animal_confirmation'] is False and stored['validated'] is False

def run():
    cand=read(P/'PRE_D_CANDIDATE.json');assert sha(P/'PRE_D_CANDIDATE.json')=='d59df6d55cb904267ee4ed08e6dcfae187529cd6a170d6553f048860c0b743e2'
    for rel,h in cand['hashes'].items():assert sha(P/rel)==h;hashes[rel]=h
    gate=read(P/'PRE_D_GATE.json');assert gate['hashes']==cand['hashes'] and gate['D_batches']==1 and gate['approved_one_D_batch'] is True
    for v in gate['independent_reviews'].values():
        receipt=json.loads((R/v['path']).read_text());assert sha(R/v['path'])==v['sha256'] and receipt['hashes']==cand['hashes'] and receipt['approved_one_D_batch'] is True
        assert sha(R/receipt['report_path'])==receipt['report_sha256']
    spec=read(P/'ONE_SHOT_D_SPECIFICATION.json');subjects=spec['primary_subjects'];assert gate['subjects']==subjects and len(subjects)==6
    claim=read(P/'D_BATCH_CLAIM.json');assert claim['status']=='COMPLETE_REGISTERED_DESCRIPTIVE_D_BATCH' and claim['attempt']==claim['D_batches']==1 and claim['new_fits']==0
    assert claim['subjects']==claim['D_projection_completed_subjects']==subjects and claim['mouse_count']==6 and claim['current_stage']=='COMPLETE' and claim['second_assessment_authorized'] is False
    assert claim['gate_sha256']==sha(P/'PRE_D_GATE.json') and claim['C_state_seal_sha256']==sha(P/'FINAL_C_STATE_SEAL.json')
    for n,h in claim['result_hashes'].items():assert sha(P/'results'/n)==h
    with (R/'paper15_m1/COHORT.csv').open(encoding='utf8') as f:labs={r['subject']:r['lab'] for r in csv.DictReader(f)}
    refs={r['subject']:r for r in read(P/'REFERENCE_METADATA_FREEZE.json')['records']};rows={};case_rows={};controls={};bundle_count=0;score_records=0;thin_count=0
    for s in subjects:
        row=read(P/f'results/D_mice/{s}.json');rows[s]=row;ids=refs[s]['D_trial_ids'];assert row['subject']==s and row['lab']==labs[s] and row['trial_ids']==ids
        assert row['C_preprocessing_sha256']==sha(P/f'states/{s}_C_PREPROCESSING.json') and re.fullmatch('[0-9a-f]{64}',row['D_export_sha256'])
        scores(row['models'],len(ids)*80,[f for f,ss in spec['family_subjects'].items() if s in ss])
        for n in range(1,12):
            case=f'S{n:02}';r=read(P/f'results/D_sensitivities/{s}/{case}.json');st=read(P/f'sensitivity_states/{s}/{case}.json');case_rows[(s,case)]=r
            assert r['subject']==s and r['case']==case and r['lab']==labs[s] and r['C_state_sha256']==sha(P/f'sensitivity_states/{s}/{case}.json') and r['status']==st['status']
            if st['status']!='C_PREPROCESSING_SEALED':assert not r.get('models') and r['unavailability_reasons']==st['unavailability_reasons'];continue
            met=st['metadata'];tids=[j for j,(valid,role) in enumerate(zip(met['valid'],met['roles'])) if valid and role=='D'];assert r['trial_ids']==tids and len(tids)==st['trial_counts']['D']
            scores(r['models'],len(tids)*round(.5/st['delta'])*len(st['units']),['B0','B1','B2','B3','B4']);assert r['numerically_unavailable_families']==[]
            if case!='S07':assert r['thinning_D'] is None
            else:
                receipts=r['thinning_D'];assert len(receipts)==len(st['units']);metrics={m['cluster_id']:m for m in st['physiology']}
                for unit,t in zip(st['units'],receipts):
                    uuid=met['native_uuid_list'][unit];sd=int.from_bytes(hashlib.sha256(f'P15-M1|150108|S07|{s}|{uuid}|D'.encode()).digest()[:8],'big');p=min(1.,2./metrics[unit]['C_rate_Hz'])
                    assert t['unit']==unit and t['uuid']==uuid and t['seed']==sd and t['role']=='D' and t['p']==p and type(t['draw_count']) is int and type(t['kept']) is int
                    assert t['kept']==int(sum(np.random.Generator(np.random.PCG64(sd)).random(t['draw_count'])<p));thin_count+=1
        crow=read(P/f'results/D_controls/{s}.json');controls[s]=crow;assert crow['subject']==s and crow['lab']==labs[s] and set(crow['suites'])=={'N1','N2','N3','N4'}
        for suite,panel in crow['suites'].items():
            jp=P/f'results/D_control_journals/{s}/{suite}.jsonl';raw=jp.read_bytes();hashes[jp.relative_to(P).as_posix()]=hashlib.sha256(raw).hexdigest();events=[json.loads(z) for z in raw.splitlines()]
            assert events[0]==dict(event='SUITE_STARTED',subject=s,suite=suite,coverage=panel['coverage'],replicates=999) and panel['coverage']==refs[s]['coverage'][suite]
            cov=panel['coverage'];q=len(cov['trial_ids'])*80;f=['B1','B4'] if suite=='N3' else ['B1','B2','B3','B4','D','C','S']
            if not cov['available']:
                assert suite=='N4' and panel['status']=='UNAVAILABLE_REGISTERED_COVERAGE' and panel['replicates_completed']==0 and events==[events[0],dict(event='UNAVAILABLE_REGISTERED_COVERAGE',coverage=cov)];continue
            assert panel['status']=='COMPLETE_FINITE_DESTRUCTIVE_REFERENCE' and panel['replicates_completed']==999 and len(events)==2001
            assert events[-1]==dict(event='SUITE_COMPLETE',replicates_completed=999,summary_sha256=dig(panel))
            ori=events[2];assert ori['event']=='ORIGINAL_CONTROL_EXPOSURE' and ori['trial_ids']==cov['trial_ids'] and ori['models']==panel['original_model_scores'];scores(ori['models'],q,f)
            observed=effect(ori['models']);observed=[ori['models']['B4']['LL']/q]*6 if suite=='N3' else observed;assert panel['observed']==observed
            for rep in range(999):
                j=1 if rep==0 else 2+2*rep;start=events[j];done=events[j+2 if rep==0 else j+1];sd,mp=mapping(ids,suite,s,rep,refs[s])
                assert start==dict(event='REPLICATE_STARTED',replicate=rep,seed=sd) and done['event']=='REPLICATE_COMPLETE' and done['replicate']==rep and done['seed']==sd
                assert panel['seeds'][rep]==sd and done['mapping_sha256']==panel['mapping_sha256'][rep]==dig(mp)
                selected=ids if suite=='N1' else [d['target_trial'] for d in mp['donors']];assert selected==cov['trial_ids'];scores(done['models'],q,f)
                value=effect(done['models'])
                if suite=='N3':assert done['wheel_gain']==panel['wheel_gain_reference'][rep]==value[0];value=[done['models']['B4']['LL']/q]*6
                else:assert done['wheel_gain'] is None
                assert done['reference_effects']==panel['reference_effects'][rep]==value;bundle_count+=1;score_records+=len(f)
            if suite=='N3':assert panel['wheel_gain_original']==effect(ori['models'])[0]
            else:assert panel['wheel_gain_original'] is None and panel['wheel_gain_reference'] is None
            assert panel['original_targets_preserved'] is True and panel['D_filter_assimilates_surrogate_past_counts']==(suite!='N3')
    assert bundle_count==spec['expected_reference_bundles']==20979
    # Complete exact result/journal membership, no favorable subset.
    for folder,expected in [('D_mice',{f'{s}.json' for s in subjects}),('D_controls',{f'{s}.json' for s in subjects}),('D_sensitivities',{f'{s}/S{i:02}.json' for s in subjects for i in range(1,12)}),('D_control_journals',{f'{s}/{n}.jsonl' for s in subjects for n in ['N1','N2','N3','N4']})]:
        root=P/'results'/folder;assert {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()}==expected
    st=read(P/'results/D_STATISTICS.json');ss=read(P/'results/D_SENSITIVITY_SUMMARY.json');cc=read(P/'results/D_CONTROL_SUMMARY.json');verdict=read(P/'results/D_SCIENTIFIC_VERDICTS.json');assert set(st)==set(cc)==set(verdict)==set(C)
    for contrast,(a,b) in C.items():
        cohort=spec['contrast_subjects'][contrast];d=[];stored=st[contrast];assert cohort==subjects
        for s,r in zip(cohort,stored['mouse_effects']):
            models=rows[s]['models'];val=(models[a]['LL']-models[b]['LL'])/models[a]['unit_bins'];d.append(val)
            assert r==dict(subject=s,lab=labs[s],effect=val,left_LL=models[a]['LL'],right_LL=models[b]['LL'],unit_bins=models[a]['unit_bins'])
        stats(d,[labs[s] for s in cohort],contrast,stored)
    assert [st[c]['Holm5_adjusted_p'] for c in secondary]==holm([st[c]['paired_sign_flip_p'] for c in secondary])
    for case in [f'S{i:02}' for i in range(1,12)]:
        assert set(ss[case])=={'B4-B1','B4-B3','B4-B2'}
        for contrast in ['B4-B1','B4-B3','B4-B2']:
            a,b=C[contrast];valid=[s for s in subjects if a in case_rows[(s,case)].get('models',{}) and b in case_rows[(s,case)].get('models',{})];d=np.array([(case_rows[(s,case)]['models'][a]['LL']-case_rows[(s,case)]['models'][b]['LL'])/case_rows[(s,case)]['models'][a]['unit_bins'] for s in valid]);panel=ss[case][contrast]
            assert panel['n_mice']==len(valid) and panel['subjects']==valid and panel['mouse_effects']==d.tolist() and panel['minimum6_coverage']==(len(valid)>=6) and panel['mandatory']==(case not in ('S02','S03'))
            rng=np.random.Generator(np.random.PCG64(150101));ci=np.quantile(d[rng.integers(0,len(d),(10000,len(d)))].mean(axis=1),[.025,.975],method='linear').tolist()
            assert panel['equal_mouse_mean']==float(d.mean()) and panel['CI95']==ci and panel['positive_mice']==sum(d>0)
            assert panel['status']==('DESCRIPTIVE_SENSITIVITY' if len(valid)>=6 else 'UNAVAILABLE_MINIMUM_PAIRED_MICE')
    for j,c in enumerate(C):
        for suite in ['N1','N2','N3','N4']:
            available=[s for s in subjects if controls[s]['suites'][suite]['status']=='COMPLETE_FINITE_DESTRUCTIVE_REFERENCE'];p=cc[c][suite]
            if len(available)<6:assert p['n_mice']==3 and p['p_reference']==1. and p['status']=='UNAVAILABLE_MINIMUM_PAIRED_MICE';continue
            obs=np.array([controls[s]['suites'][suite]['observed'][j] for s in available]);ref=np.array([[v[j] for v in controls[s]['suites'][suite]['reference_effects']] for s in available]);med=np.median(ref,axis=1);degrade=obs-med
            assert p['subjects']==available and p['n_mice']==6 and p['mouse_original']==obs.tolist() and p['mouse_reference_medians']==med.tolist()
            assert p['reference_equal_mouse_means']==ref.mean(axis=0).tolist() and p['observed_equal_mouse_mean']==float(obs.mean()) and p['mean_degradation']==float(degrade.mean())
            assert p['p_reference']==float((1+sum(ref.mean(axis=0)>=obs.mean()))/1000) and p['mice_above_reference_median']==sum(degrade>0) and p['descriptive_disruption_gate']==bool(sum(degrade>0)>=5 and degrade.mean()>0)
        assert [cc[c][n]['Holm4_reference_p'] for n in ['N1','N2','N3','N4']]==holm([cc[c][n]['p_reference'] for n in ['N1','N2','N3','N4']])
        r=st[c];criteria=verdict[c]['criteria'];expected=dict(cohort_at_least8=False,at_least4labs=True,no_lab_over50percent=True,source_and_main_numerical_valid=True,independence_and_symmetry_defensible=False,mean_at_least0p001=r['equal_mouse_mean']>=.001,positive_CI_lower=r['CI95'][0]>0,CI_width_at_most0p01=r['CI_width']<=.01,registered_p_at_most0p05=r['paired_sign_flip_p' if c=='B4-B1' else 'Holm5_adjusted_p']<=.05,at_least75percent_positive=r['positive_mice']>=5,all_leave_one_mouse_means_positive=all(v>0 for v in r['leave_one_mouse_out_means']),all_leave_one_lab_means_positive=all(v>0 for v in r['leave_one_lab_out_means'].values()))
        if c in ('B4-B1','B4-B3','B4-B2'):
            for case in mandatory:expected['mandatory_'+case]=bool(ss[case][c]['minimum6_coverage'] and ss[case][c]['equal_mouse_mean']>0)
        else:expected['no_unregistered_sensitivity_credit']=True
        required=['N1','N2']+(['N4'] if c in ('D-B4','D-S') else [])
        for suite in required:expected['reference_'+suite]=bool(cc[c][suite]['n_mice']>=6 and cc[c][suite].get('descriptive_disruption_gate',False))
        if c=='D-S':expected['prescribed_static_capacity_pair_valid']=True
        assert criteria==expected and set(verdict[c]['failed_criteria'])=={k for k,v in expected.items() if not v}
        assert verdict[c]['verdict']=='DESCRIPTIVE ONLY' and verdict[c]['supported_under_complete_registered_conjunction'] is False and verdict[c]['required_reference_suites']==required
        for key in ['causal_mechanism','all_movement_independence','biological_discrete_states','independent_lab_replication','NAP_CWP_validation']:assert verdict[c][key] is False
    # Denominators and original frozen inputs remain unchanged after the replay.
    for rel,h in hashes.items():assert sha(P/rel)==h,rel
    result=dict(time=datetime.datetime.now(datetime.timezone.utc).isoformat(),reviewer='/root/gradient_review',decision='ACCEPTED_SAVED_FINAL_NUMERICAL_RESULTS',open_P0=0,open_P1=0,script_sha256=sha(Path(__file__)),hashes=hashes,main_mice=6,main_model_scores=48,case_panels=66,available_cases=64,case_model_scores=320,unavailable_cases=2,journals=24,complete_suites=21,unavailable_suites=3,reference_bundles=bundle_count,reference_family_score_records=score_records,S07_D_receipts_verified=thin_count,sign_assignments_per_contrast=64,bootstrap_replicates=10000,secondary_family_size=5,actual_source_arrays_loaded=0,actual_model_score_calls=0,actual_likelihood_AD_FD_evaluations=0,new_fits=0,new_D_batches=0,scientific_scope='DESCRIPTIVE ONLY',Git_approval=False)
    with (E/'FINAL_NUMERICAL_RESULTS_CHECKS_1.json').open('x',encoding='utf8') as f:json.dump(result,f,indent=2,sort_keys=True);f.write('\n')
    print(json.dumps({k:v for k,v in result.items() if k!='hashes'},indent=2))

if __name__=='__main__':run()
