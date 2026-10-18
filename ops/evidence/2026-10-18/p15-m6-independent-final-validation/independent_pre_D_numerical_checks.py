"""Metadata/JSON-only independent pre-D audit; no arrays or prediction calls."""
from pathlib import Path
from collections import Counter
import datetime,hashlib,itertools,json,socket
import numpy as np
R=Path(__file__).resolve().parents[4];P=R/'paper15_final1';E=Path(__file__).parent
def deny(*a,**k):raise PermissionError('Independent pre-D saved audit denies arrays/network')
np.load=deny;socket.socket.connect=deny;socket.create_connection=deny
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_bytes())
def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
contrasts={'B4-B1':('B4','B1'),'B4-B3':('B4','B3'),'B4-B2':('B4','B2'),'D-B4':('D','B4'),'C-B4':('C','B4'),'D-S':('D','S')}

def ordered_mapping(ids,suite,rep,subject,keys):
    seed=int.from_bytes(hashlib.sha256(f'P15-M1|150107|{suite}|{subject}|D|{rep}'.encode()).digest()[:8],'big')
    rng=np.random.Generator(np.random.PCG64(seed))
    if suite=='N1':return seed,dict(offsets=[dict(trial=int(i),offset=int(rng.integers(1,20))) for i in ids],donors=None)
    donor={}
    if suite=='N4':
        blocks=[list(range(a,a+5)) for a in range(240,400,5) if set(range(a,a+5))<=set(ids)]
        if len(blocks)>=2:
            shift=int(rng.integers(1,len(blocks)));src=np.roll(np.asarray(blocks),shift,axis=0)
            donor={t:int(d) for block,db in zip(blocks,src) for t,d in zip(block,db)}
    else:
        for key in sorted(set(keys)):
            group=[int(t) for t,k in zip(ids,keys) if k==key]
            if len(group)<2:continue
            shift=int(rng.integers(1,len(group)))
            donor.update(zip(group,np.roll(group,shift).tolist()))
    return seed,dict(donors=[dict(target_trial=int(t),donor_trial=donor[int(t)]) for t in ids if int(t) in donor])

def synthetic_metadata(i):
    ids=np.arange(241,321) if i<3 else np.arange(241,400,2);cids=np.arange(1,240,3)
    wt=np.arange(-1.,801.,.05);wp=np.sin(wt*.1)+.1*np.sin(wt*.7)
    def mag(v):
        ep=2.*v+.25
        return abs(wp[np.searchsorted(wt,ep,side='right')-1]-wp[np.searchsorted(wt,ep-.5,side='right')-1])
    threshold=float(np.median(mag(cids)));dmag=mag(ids)
    k3=[(int(t%2==0),int(t%2==0),int(t>=320)) for t in ids]
    k2=[k+(int(d>threshold),) for k,d in zip(k3,dmag)]
    return ids,{'N2':k2,'N3':k3}

def effects(models):
    return [None if a not in models or b not in models else (models[a]['LL']-models[b]['LL'])/models[a]['unit_bins'] for a,b in contrasts.values()]

def run():
    candidate=read(P/'PRE_D_CANDIDATE.json');assert sha(P/'PRE_D_CANDIDATE.json')=='d59df6d55cb904267ee4ed08e6dcfae187529cd6a170d6553f048860c0b743e2'
    assert len(candidate['hashes'])==546
    assert not (P/'D_BATCH_CLAIM.json').exists() and not (P/'PRE_D_GATE.json').exists()
    for rel,h in candidate['hashes'].items():assert sha(P/rel)==h,rel
    for rel,h in candidate['external_dependencies'].items():assert sha(R/rel)==h,rel
    current_py={p.name for p in P.glob('*.py')};assert current_py<=set(candidate['hashes'])
    static=read(E/'D_STATIC_REVIEW_RECEIPT_3.json')
    assert static['decision']=='ACCEPTED_D_STAGE_STATIC_ENGINEERING' and static['open_P0']==static['open_P1']==0
    for rel,h in static['hashes'].items():assert sha(P/rel)==h,rel
    assert sha(R/static['report_path'])==static['report_sha256']
    own=read(E/'C_ENDPOINT_FINAL_CHECKS_1.json');assert own['completed_checked']==own['numerical_pass']==392 and own['numerical_fail']==own['unattempted']==0 and not own['started']
    seal=read(P/'FINAL_C_STATE_SEAL.json');spec=read(P/'ONE_SHOT_D_SPECIFICATION.json');plan=read(P/'C_FIT_PLAN.json');sp=read(P/'SENSITIVITY_FIT_PLAN.json')
    subjects=plan['subjects'];assert len(subjects)==6 and subjects==sp['subjects']==spec['primary_subjects']==seal['primary_subjects']==candidate['subjects']
    assert seal['complete_calibration_state'] is True and seal['cumulative_attempts']==1886 and seal['original_attempts']==359 and seal['R1_corrective_attempts']==1135
    assert len(seal['main'])==72 and len(seal['sensitivities'])==320 and all(x['valid'] is True for x in seal['main']+seal['sensitivities'])
    endpointmap={r['path']:r['sha256'] for r in own['records']}
    assert {x['path']:x['sha256'] for x in seal['main']+seal['sensitivities']}==endpointmap
    for item in seal['artifacts']:assert candidate['hashes'][item['path']]==item['sha256']
    main=read(P/'results/C_MAIN_ATTEMPTS_COMPLETE.json');sens=read(P/'results/C_SENSITIVITY_ATTEMPTS_COMPLETE.json')
    assert main['attempted']==main['numerical_pass']==len(main['attempts'])==72 and sens['attempted']==sens['numerical_pass']==len(sens['records'])==320
    assert {(r['subject'],r['configuration']['id']) for r in main['attempts']}=={(s,c['id']) for s in subjects for c in plan['configurations']}
    for r in main['attempts']:assert r['status']=='NUMERICAL_PASS' and r['sha256']==endpointmap['fits/'+r['subject']+'/'+r['configuration']['id']+'.json']
    assert [r['item'] for r in sens['records']]==sp['attempts']
    for r in sens['records']:
        i=r['item'];assert r['status']=='NUMERICAL_PASS' and r['disposition']=='VALID' and r['sha256']==endpointmap['sensitivity_fits/'+i['subject']+'/'+i['case']+'/'+i['family']+'.json']
    assert all(v==subjects for v in seal['family_subjects'].values()) and spec['family_subjects']==seal['family_subjects']
    assert spec['contrast_subjects']=={c:subjects for c in contrasts}
    assert spec['mandatory_descriptive_only'] is True and spec['confirmatory_assumptions_defensible'] is False and spec['D_batches']==1 and spec['no_D_fit_or_selection'] is True
    ref=read(P/'REFERENCE_METADATA_FREEZE.json');assert ref['subjects']==subjects and ref['D_neural_values_accessed'] is False and ref['matching_thresholds_fit_C_only'] is True
    coverage=Counter(suite for row in ref['records'] for suite,cov in row['coverage'].items() if cov['available'])
    assert coverage=={'N1':6,'N2':6,'N3':6,'N4':3} and spec['expected_reference_bundles']==20979
    # Full successful synthetic evidence: source kernel identity + every journal mapping/score-derived effect.
    fresh=read(E/'FULL_SYNTHETIC_FRESHNESS_BINDING.json');certpath=P/'results/FULL_D_SYNTHETIC_REHEARSAL.json';cert=read(certpath)
    assert sha(certpath)==candidate['full_synthetic_certificate_sha256']==fresh['certificate_sha256']
    for rel,h in fresh['kernel_hashes'].items():assert sha(P/rel)==h
    assert cert['scope']=='FULL_PLANNED_D_KERNEL_SYNTHETIC_ONLY' and cert['real_C_fits']==0 and cert['real_D_neural_access'] is False and cert['actual_D_batch_claim_created'] is False
    assert cert['source_array_loading_denied'] is True and cert['network_denied'] is True
    bundles=0;model_scores=0;complete=0;unavailable=0;originals={};references={}
    for rel,h in cert['journal_hashes'].items():
        path=P/rel;assert path.resolve().is_relative_to((P/'work/full_D_synthetic').resolve()) and sha(path)==h
        events=[json.loads(s) for s in path.read_text().splitlines()];subject=path.parent.name;suite=path.stem;i=int(subject.rsplit('_',1)[1]);assert subject.startswith('SYNTHETIC_ONLY_') and 0<=i<6
        ids,keys=synthetic_metadata(i);assert events[0]['event']=='SUITE_STARTED' and events[0]['subject']==subject and events[0]['suite']==suite
        cov=events[0]['coverage'];assert cov['total_epochs']==len(ids)
        if not cov['available']:
            assert suite=='N4' and i>=3 and len(events)==2 and events[1]['event']=='UNAVAILABLE_REGISTERED_COVERAGE';unavailable+=1;continue
        complete+=1;starts=[x for x in events if x['event']=='REPLICATE_STARTED'];done=[x for x in events if x['event']=='REPLICATE_COMPLETE'];ori=[x for x in events if x['event']=='ORIGINAL_CONTROL_EXPOSURE']
        assert len(starts)==len(done)==999 and len(ori)==1 and events[-1]['event']=='SUITE_COMPLETE' and len(events)==2001
        assert [x['replicate'] for x in starts]==[x['replicate'] for x in done]==list(range(999))
        assert ori[0]['trial_ids']==cov['trial_ids'];q=len(cov['trial_ids'])*80;families={'B1','B4'} if suite=='N3' else {'B1','B2','B3','B4','C','D','S'}
        def scores(m):
            assert set(m)==families
            for s in m.values():assert type(s['unit_bins']) is int and s['unit_bins']==q and np.isfinite(s['LL'])
        scores(ori[0]['models']);obs=effects(ori[0]['models'])
        if suite=='N3':obs=[ori[0]['models']['B4']['LL']/q]*6
        originals[(subject,suite)]=obs;vals=[]
        for start,event in zip(starts,done):
            rep=event['replicate'];seed,mapping=ordered_mapping(ids,suite,rep,subject,keys.get(suite));assert seed==start['seed']==event['seed'] and digest(mapping)==event['mapping_sha256']
            selected=ids.tolist() if suite=='N1' else [d['target_trial'] for d in mapping['donors']];assert selected==cov['trial_ids']
            scores(event['models']);value=effects(event['models'])
            if suite=='N3':assert event['wheel_gain']==value[0];value=[event['models']['B4']['LL']/q]*6
            else:assert event['wheel_gain'] is None
            assert event['reference_effects']==value;vals.append(value);bundles+=1;model_scores+=len(event['models'])
        references[(subject,suite)]=np.asarray(vals)
    assert complete==21 and unavailable==3 and bundles==cert['actual_reference_bundles']==20979 and len(cert['journal_hashes'])==24
    for j,c in enumerate(contrasts):
        panels=cert['control_summaries'][c]
        for suite in ['N1','N2','N3','N4']:
            subs=[f'SYNTHETIC_ONLY_{i}' for i in range(6) if (f'SYNTHETIC_ONLY_{i}',suite) in originals]
            panel=panels[suite]
            if len(subs)<6:assert panel['p_reference']==1. and panel['n_mice']==3;continue
            obs=np.array([originals[(s,suite)][j] for s in subs]);refs=np.array([references[(s,suite)][:,j] for s in subs]);degrade=obs-np.median(refs,axis=1)
            assert panel['observed_equal_mouse_mean']==float(obs.mean()) and panel['mean_degradation']==float(degrade.mean())
            assert panel['reference_equal_mouse_means']==refs.mean(axis=0).tolist() and panel['p_reference']==float((1+sum(refs.mean(axis=0)>=obs.mean()))/1000)
            assert panel['mice_above_reference_median']==int(sum(degrade>0)) and panel['descriptive_disruption_gate']==bool(sum(degrade>0)>=5 and degrade.mean()>0)
        # Fixed six-mouse sign enumeration and bootstrap from certificate's mouse effects, not model calls.
        st=cert['statistics'][c];d=np.array([r['effect'] for r in st['mouse_effects']]);assert len(d)==6
        signs=np.array(list(itertools.product([-1.,1.],repeat=6)));null=(signs*d).mean(axis=1)
        pv=float(np.mean(null>=d.mean()-1e-14)) if j==0 else float(np.mean(abs(null)>=abs(d.mean())-1e-14))
        assert st['paired_sign_flip_p']==pv and st['equal_mouse_mean']==float(d.mean())
        rng=np.random.Generator(np.random.PCG64(150101));ci=np.quantile(d[rng.integers(0,6,(10000,6))].mean(axis=1),[.025,.975],method='linear').tolist();assert st['CI95']==ci
        assert cert['claim_verdicts'][c]['verdict']=='DESCRIPTIVE ONLY' and cert['claim_verdicts'][c]['supported_under_complete_registered_conjunction'] is False
    assert sha(P/'PRE_D_CANDIDATE.json')=='d59df6d55cb904267ee4ed08e6dcfae187529cd6a170d6553f048860c0b743e2'
    out=dict(time=datetime.datetime.now(datetime.timezone.utc).isoformat(),reviewer='/root/gradient_review',candidate_sha256=sha(P/'PRE_D_CANDIDATE.json'),payload_hashes=candidate['hashes'],script_sha256=sha(Path(__file__)),passing_C_endpoints=392,main=72,sensitivity=320,historical=1494,cumulative=1886,synthetic_journals=24,synthetic_completed_suites=21,synthetic_unavailable_suites=3,synthetic_bundles_independently_replayed=bundles,synthetic_family_score_records=model_scores,synthetic_original_family_counts_and_denominators_exact=True,synthetic_rng_mapping_hashes_exact=True,synthetic_statistics_saved_arithmetic_exact=True,actual_reference_available_mice=dict(coverage),real_source_arrays_loaded=0,real_D_access=False,real_model_score_calls=0,real_likelihood_AD_FD_evaluations=0,new_fits=0,final_gate_not_created_by_reviewer=True)
    target=E/'PRE_D_NUMERICAL_CHECKS_1.json'
    with target.open('x',encoding='utf8') as f:json.dump(out,f,indent=2,sort_keys=True);f.write('\n')
    print(json.dumps({k:v for k,v in out.items() if k!='payload_hashes'},indent=2))

if __name__=='__main__':run()
