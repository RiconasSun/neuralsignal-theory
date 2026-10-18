"""Original finite-reference/statistical arithmetic with Final D role names."""
import os,json,hashlib
import numpy as np
from .source import P
from .controls import seed,reference
from .statistics import CONTRASTS,holm
from .sensitivities import CASES
from .d_support import control_arrays
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


def run_controls(subject,arrays,predictors,prep,reference_metadata,journal_root=None):
    out={};trial_ids=arrays['trial_ids'];total=len(trial_ids)
    assert trial_ids.tolist()==reference_metadata['D_trial_ids']
    bounds=reference_metadata['role_bounds']
    root=P/'results/D_control_journals'/subject if journal_root is None else journal_root
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
            s=seed(suite,subject,'D',r);append_event(journal,dict(event='REPLICATE_STARTED',replicate=r,seed=s))
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
            C_matching_diagnostics={k:v for k,v in reference_metadata.items() if k.startswith('C_warm_rate') or k.startswith('C_wheel_displacement')})
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
            panel=dict(status='DESCRIPTIVE_FINITE_REFERENCE',subjects=[r['subject'] for r in complete],n_mice=len(complete),
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

