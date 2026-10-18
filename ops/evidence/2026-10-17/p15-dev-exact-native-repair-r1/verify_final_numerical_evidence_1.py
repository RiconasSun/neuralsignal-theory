"""Independent saved scalar/statistic/mapping/archive review; no neural or model evaluation."""
import collections
import csv
import datetime
import hashlib
import json
import math
import socket
import sys
from pathlib import Path

import numpy as np

E = Path(__file__).resolve().parent
R = E.parents[3]
P = R / 'paper15_r1'
PAIRS = {'B4-B1': ('B4','B1'), 'B4-B3': ('B4','B3'), 'B4-B2': ('B4','B2'),
         'D-B4': ('D','B4'), 'C-B4': ('C','B4'), 'D-S': ('D','S')}
SECONDARY = ['B4-B3','B4-B2','D-B4','C-B4','D-S']


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path): return json.loads(path.read_text(encoding='utf8'))
def digest(value): return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def denied(*a,**kw): raise AssertionError('No neural arrays, network, models, likelihoods, derivatives or fits')


def holm_independent(values):
    order=sorted(range(len(values)),key=lambda i:(values[i],i));out=[None]*len(values);previous=0.
    for rank,index in enumerate(order):
        previous=max(previous,min(1.,values[index]*(len(values)-rank)));out[index]=previous
    return out


def score_table(models,q,families):
    assert set(models)==set(families) and q>0
    assert all(v['unit_bins']==q and math.isfinite(v['LL']) for v in models.values())


def effect(models):
    return [(models[a]['LL']-models[b]['LL'])/models[a]['unit_bins'] if a in models and b in models else None for a,b in PAIRS.values()]


def mapping_independent(suite,ids,metadata,rng):
    if suite=='N1':
        return list(range(len(ids))),dict(offsets=[dict(trial=int(t),offset=int(rng.integers(1,20))) for t in sorted(ids)],donors=None)
    donors={};lookup={t:i for i,t in enumerate(ids)}
    if suite=='N4':
        blocks=[];lo,hi=metadata['role_bounds']
        for begin in range(lo,hi,5):
            ts=list(range(begin,min(begin+5,hi)))
            if len(ts)==5 and all(t in lookup for t in ts):blocks.append([lookup[t] for t in ts])
        if len(blocks)>=2:
            shifted=np.roll(np.asarray(blocks),int(rng.integers(1,len(blocks))),axis=0)
            donors.update(zip(np.asarray(blocks).ravel().tolist(),shifted.ravel().tolist()))
    else:
        keys=[tuple(v) for v in metadata['keys_'+suite]]
        for key in sorted(set(keys)):
            group=sorted([i for i,k in enumerate(keys) if k==key],key=lambda i:ids[i])
            if len(group)>1:
                donors.update(zip(group,np.roll(group,int(rng.integers(1,len(group)))).tolist()))
    selected=sorted(donors)
    return selected,dict(donors=[dict(target_trial=int(ids[i]),donor_trial=int(ids[donors[i]])) for i in selected])


def run():
    np.load=denied;socket.create_connection=denied;socket.socket.connect=denied
    sys.path.insert(0,str(R))
    from paper15_r1.source import load_json
    import paper15_r1.models as models
    import paper15_r1.training as training
    import paper15_r1.independent_ad as derivatives
    from paper15_r1.evaluation_support import FrozenPredictors
    from paper15_r1.statistics import analyze
    from paper15_r1.evaluation import control_summary,sensitivity_summary
    for method in ['__init__','initialize','objective','value','prebin_logmasses']:setattr(models.Model,method,denied)
    training.minimize=denied;derivatives.ad_function=denied;derivatives.coordinate_check=denied;FrozenPredictors.score=denied
    archive_path=P/'ARCHIVE_FREEZE.json';archive_sha=sha(archive_path);archive=read(archive_path)
    assert len(archive['hashes'])==1565 and len(archive['external_hashes'])==33
    assert all(not k.startswith('work/') and not k.endswith(('.npy','.npz')) for k in archive['hashes'])
    for rel,value in archive['hashes'].items():assert sha(P/rel)==value,rel
    for rel,value in archive['external_hashes'].items():assert sha(R/rel)==value,rel
    claim=read(P/'E_BATCH_CLAIM.json');gate=read(P/'E_EXPLORATORY_GATE.json');selection=read(P/'SELECTION_FREEZE.json')
    subjects=selection['subjects'];assert len(subjects)==len(set(subjects))==10
    assert claim['status']=='COMPLETE_EXPLORATORY_E_BATCH' and claim['attempt']==claim['E_batches']==1 and claim['mouse_count']==10
    assert claim['Final_access'] is False and claim['validated'] is False and claim['gate_sha256']==sha(P/'E_EXPLORATORY_GATE.json')
    assert datetime.datetime.fromisoformat(claim['completed_at'])>datetime.datetime.fromisoformat(claim['started_at'])>datetime.datetime.fromisoformat(gate['frozen_at'])
    for rel,value in gate['hashes'].items():assert sha(P/rel)==value
    for item in gate['independent_review_evidence'].values():
        assert sha(R/item['path'])==item['sha256'] and sha(R/item['receipt_path'])==item['receipt_sha256']
    for name,value in claim['result_hashes'].items():assert sha(P/'results'/name)==value
    main_review=read(E/'MAIN_NUMERICAL_REVIEW_1_RECEIPT.json');sens_review=read(E/'E_NUMERICAL_SAVED_CHECKS_1.json')
    for key,value in main_review['fit_hashes'].items():assert sha(P/'fits'/(key+'.json'))==value
    for key,value in sens_review['sensitivity_fit_hashes'].items():assert sha(P/'sensitivity_fits'/(key+'.json'))==value
    metadata=read(P/'REFERENCE_METADATA_FREEZE.json');by_meta={r['subject']:r for r in metadata['records']}
    with (R/'paper15_m1/COHORT.csv').open(encoding='utf8') as f:labs={r['subject']:r['lab'] for r in csv.DictReader(f)}
    rows=[read(P/'results/E_mice'/(s+'.json')) for s in subjects]
    assert len(list((P/'results/E_mice').glob('*.json')))==10
    total_q=0
    for sub,row in zip(subjects,rows):
        assert row['subject']==sub and row['lab']==labs[sub] and row['trial_ids']==by_meta[sub]['E_trial_ids']
        q=len(row['trial_ids'])*10*8;score_table(row['models'],q,['B0','B1','B2','B3','B4','D','C','S']);total_q+=q
    stats=read(P/'results/E_STATISTICS.json');assert analyze(rows,subjects)==stats
    independent_stats={}
    for contrast,(a,b) in PAIRS.items():
        d=np.array([(r['models'][a]['LL']-r['models'][b]['LL'])/r['models'][a]['unit_bins'] for r in rows])
        n=len(d);signs=np.array([[1. if (bits>>j)&1 else -1. for j in range(n)] for bits in range(1<<n)])
        null=(signs*d).mean(axis=1);observed=float(d.mean())
        p=float(np.mean(null>=observed-1e-14)) if contrast=='B4-B1' else float(np.mean(np.abs(null)>=abs(observed)-1e-14))
        rng=np.random.Generator(np.random.PCG64(150101));boot=d[rng.integers(0,n,(10000,n))].mean(axis=1)
        ci=np.quantile(boot,[.025,.975],method='linear').tolist()
        assert stats[contrast]['equal_mouse_mean']==observed and stats[contrast]['paired_sign_flip_p']==p
        assert stats[contrast]['CI95']==ci and stats[contrast]['positive_mice']==int(np.sum(d>0))
        assert stats[contrast]['validated'] is False and stats[contrast]['heldout_animal_confirmation'] is False
        independent_stats[contrast]=dict(mean=observed,CI95=ci,raw_p=p,positive_mice=int(np.sum(d>0)))
    adjusted=holm_independent([independent_stats[k]['raw_p'] for k in SECONDARY])
    for c,value in zip(SECONDARY,adjusted):assert stats[c]['Holm5_adjusted_p']==value;independent_stats[c]['Holm5_p']=value
    case_rows=[];unavailable=0
    for s in subjects:
        paths=list((P/'results/E_sensitivities'/s).glob('*.json'));assert len(paths)==11
        for number in range(1,12):
            cid=f'S{number:02}';row=read(P/'results/E_sensitivities'/s/(cid+'.json'))
            path=P/'sensitivity_states'/s/(cid+'.json');state=load_json(path.read_text())
            assert row['subject']==s and row['case']==cid and row['lab']==labs[s] and row['A_state_sha256']==sha(path) and row['status']==state['status']
            if row['status']=='A_PREPROCESSING_SEALED':
                ids=[i for i,(valid,role) in enumerate(zip(state['metadata']['valid'],state['metadata']['roles'])) if valid and role=='E']
                assert row['trial_ids']==ids and not row['numerically_unavailable_families']
                score_table(row['models'],len(ids)*int(round(.5/state['delta']))*len(state['units']),['B0','B1','B2','B3','B4'])
            else:assert not row.get('models');unavailable+=1
            case_rows.append(row)
    assert len(case_rows)==110 and unavailable==5
    sensitivities=read(P/'results/E_SENSITIVITY_SUMMARY.json');assert sensitivity_summary(case_rows,subjects)==sensitivities
    for cid,panels in sensitivities.items():
        for c,panel in panels.items():
            a,b=PAIRS[c];valid=[r for r in case_rows if r['case']==cid and a in r.get('models',{}) and b in r.get('models',{})]
            d=np.array([(r['models'][a]['LL']-r['models'][b]['LL'])/r['models'][a]['unit_bins'] for r in valid])
            rng=np.random.Generator(np.random.PCG64(150101));ci=np.quantile(d[rng.integers(0,len(d),(10000,len(d)))].mean(axis=1),[.025,.975],method='linear').tolist()
            assert panel['equal_mouse_mean']==float(d.mean()) and panel['CI95']==ci
            assert 'paired_sign_flip_p' not in panel and panel['validated'] is False
    control_rows=[];bundle_count=family_count=unavailable_suites=0;per_suite=collections.Counter()
    for subject in subjects:
        row=read(P/'results/E_controls'/(subject+'.json'));assert row['subject']==subject and row['lab']==labs[subject]
        assert set(row['suites'])=={'N1','N2','N3','N4'}
        m=by_meta[subject];ids=m['E_trial_ids']
        for suite,panel in row['suites'].items():
            path=P/'results/E_control_journals'/subject/(suite+'.jsonl')
            events=[load_json(line) for line in path.read_text(encoding='utf8').splitlines()]
            assert events[0]['event']=='SUITE_STARTED' and events[0]['subject']==subject and events[0]['suite']==suite
            assert panel['coverage']==m['coverage'][suite]==events[0]['coverage']
            if panel['status']=='UNAVAILABLE_REGISTERED_COVERAGE':
                assert suite=='N4' and not m['coverage'][suite]['available'] and panel['replicates_completed']==0
                assert len(events)==2 and events[1]['event']=='UNAVAILABLE_REGISTERED_COVERAGE';unavailable_suites+=1;continue
            assert panel['status']=='COMPLETE_FINITE_DESTRUCTIVE_REFERENCE' and m['coverage'][suite]['available']
            assert len(events)==2001 and events[-1]['event']=='SUITE_COMPLETE' and events[-1]['summary_sha256']==digest(panel)
            assert events[-1]['replicates_completed']==panel['replicates_completed']==999
            assert [x['event'] for x in events[1:4]]==['REPLICATE_STARTED','ORIGINAL_CONTROL_EXPOSURE','REPLICATE_COMPLETE']
            starts=[x for x in events if x['event']=='REPLICATE_STARTED'];done=[x for x in events if x['event']=='REPLICATE_COMPLETE']
            originals=[x for x in events if x['event']=='ORIGINAL_CONTROL_EXPOSURE'];assert len(originals)==1
            assert len(starts)==len(done)==len(set(panel['seeds']))==999
            families=['B1','B4'] if suite=='N3' else ['B1','B2','B3','B4','D','C','S']
            q=len(panel['coverage']['trial_ids'])*80;score_table(originals[0]['models'],q,families)
            assert originals[0]['models']==panel['original_model_scores'] and originals[0]['trial_ids']==panel['coverage']['trial_ids']
            observed=effect(originals[0]['models'])
            if suite=='N3':assert panel['wheel_gain_original']==observed[0];observed=[originals[0]['models']['B4']['LL']/q]*6
            assert observed==panel['observed']
            for i,(start,item) in enumerate(zip(starts,done)):
                seed=int.from_bytes(hashlib.sha256(f'P15-M1|150107|{suite}|{subject}|E|{i}'.encode()).digest()[:8],'big')
                assert start['replicate']==item['replicate']==i and start['seed']==item['seed']==panel['seeds'][i]==seed
                if i:
                    assert events[2*i+2]==start and events[2*i+3]==item
                chosen,mapping=mapping_independent(suite,ids,m,np.random.Generator(np.random.PCG64(seed)))
                assert [ids[j] for j in chosen]==panel['coverage']['trial_ids']
                assert digest(mapping)==item['mapping_sha256']==panel['mapping_sha256'][i]
                score_table(item['models'],q,families);values=effect(item['models'])
                if suite=='N3':
                    assert item['wheel_gain']==panel['wheel_gain_reference'][i]==values[0];values=[item['models']['B4']['LL']/q]*6
                else:assert item['wheel_gain'] is None
                assert values==item['reference_effects']==panel['reference_effects'][i] and all(math.isfinite(v) for v in values)
            bundle_count+=999;family_count+=999*len(families);per_suite[suite]+=1
        control_rows.append(row);print(subject,'saved journals verified',flush=True)
    assert bundle_count==34965 and unavailable_suites==5 and per_suite=={'N1':10,'N2':10,'N3':10,'N4':5} and family_count==194805
    controls=read(P/'results/E_CONTROL_SUMMARY.json');assert control_summary(control_rows,subjects)==controls
    for j,c in enumerate(PAIRS):
        values=[]
        for suite in ['N1','N2','N3','N4']:
            panel=controls[c][suite];valid=[r['suites'][suite] for r in control_rows if r['suites'][suite]['status']=='COMPLETE_FINITE_DESTRUCTIVE_REFERENCE']
            if len(valid)<6:
                assert panel['status']=='UNAVAILABLE_MINIMUM_PAIRED_MICE' and panel['p_reference']==1 and panel['n_mice']==5
            else:
                obs=np.array([v['observed'][j] for v in valid]);refs=np.array([[w[j] for w in v['reference_effects']] for v in valid])
                p=float((1+np.count_nonzero(refs.mean(axis=0)>=obs.mean()))/1000)
                medians=np.median(refs,axis=1);difference=obs-medians;above=int(np.sum(difference>0))
                assert panel['p_reference']==p and panel['mice_above_reference_median']==above and panel['mean_degradation']==float(difference.mean())
                assert panel['descriptive_disruption_gate']==bool(above>=math.ceil(.75*len(valid)) and difference.mean()>0)
            values.append(panel['p_reference'])
        for suite,adjust in zip(['N1','N2','N3','N4'],holm_independent(values)):assert controls[c][suite]['Holm4_reference_p']==adjust
    claims=read(P/'results/CLAIM_TO_EVIDENCE_AUDIT.json');status=read(P/'results/DEVELOPMENT_STATUS.json')
    assert total_q==claims['scored_nominal_curated_release_unit_bins']==98320
    assert claims['primary_N1']==dict(above_median=7,required=8,gate=False,Holm4_reference_p=.004)
    assert controls['B4-B1']['N1']['descriptive_disruption_gate'] is False and controls['B4-B1']['N2']['descriptive_disruption_gate'] is True
    assert claims['primary_N2_gate'] is True and claims['all_secondary_Holm5_nonsignificant'] is True
    for flag in ['robust_positive_primary_claim','persistent_state_claim','causal_mechanism','all_movement_independence','heldout_validation','completed_paper','Final_C_access','Final_D_access','N4_aggregate_available']:assert claims[flag] is False
    assert all(stats[c]['Holm5_adjusted_p']>.05 for c in SECONDARY)
    reproduction=read(E/'SAVED_REPRODUCTION_RECEIPT_1.json')
    assert reproduction['exit_code']==0 and reproduction['archive_sha256']==archive_sha and reproduction['result']['synthetic_tests']==126
    assert sha(E/'SAVED_REPRODUCTION_1.log')==reproduction['log_sha256']
    assert sha(archive_path)==archive_sha
    result=dict(mission='P15-DEV-EXACT-NATIVE-REPAIR-R1',reviewer='/root/gradient_review',time=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                source_archive_sha256=archive_sha,archive_files_verified=1565,external_files_verified=33,E_batches=1,E_mice=10,E_labs=len({r['lab'] for r in rows}),
                main_numerical_review_reused=610,sensitivity_numerical_review_reused=525,main_unit_bins=total_q,main_effects=independent_stats,
                reference_bundles=bundle_count,reference_family_outputs=family_count,reference_complete_suites=dict(per_suite),unavailable_N4_suites=5,
                control_aggregate_panels=24,N4_aggregate_unavailable=True,sensitivity_records=110,available_sensitivity_records=105,unavailable_sensitivity_records=5,
                primary_N1_above_reference_median=7,primary_N1_required=8,primary_N1_gate=False,primary_N2_gate=True,primary_CI_width=stats['B4-B1']['CI_width'],
                robust_positive_claim=False,dynamics_or_mechanistic_claim=False,Final_access=False,real_fits=0,real_likelihood_AD_FD_evaluations=0,neural_arrays_loaded=0,
                diagnostic_script_sha256=sha(Path(__file__)),scope='H1 archive candidate numerical evidence only; no Git/remote/clean or scientific positive-claim acceptance')
    path=E/'FINAL_NUMERICAL_SAVED_CHECKS_1.json';assert not path.exists();path.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n',encoding='utf8')
    print(json.dumps(result,indent=2));print('saved_checks_sha256='+sha(path))


if __name__=='__main__':run()
