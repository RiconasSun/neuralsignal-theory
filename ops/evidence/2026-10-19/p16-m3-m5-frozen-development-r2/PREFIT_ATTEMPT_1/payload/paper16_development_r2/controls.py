"""Frozen nonrecursive reference transformations; no fitting or favorable redraw."""
from dataclasses import replace
import hashlib
import math
import json
import numpy as np
from .core import spec,analysis_oracles,ImplementationStop,CONTRASTS
from .features import build,wrong_map

def rng_for(mouse,operator):
    seed={'N1':16051,'N2':16052,'N3':16053}[operator]
    key=str(int(mouse));offset=int.from_bytes(hashlib.sha256(key.encode('ascii')).digest()[:4],'big')
    return np.random.Generator(np.random.PCG64((seed+offset)%(2**64)))

def donor_map(batch,rng):
    groups={}
    for j,(original,color) in enumerate(zip(batch.ordinals,batch.colors)):
        groups.setdefault((int(color),int(original)//30),[]).append(j)
    out=np.arange(len(batch.ordinals))
    for group in sorted(groups.values(),key=lambda x:batch.ordinals[x[0]]):out[group]=spec.derangement(group,rng)
    return out

def history_derangement(batch,donors):
    raw=batch.raw.copy();raw[...,batch.b1:]=batch.raw[donors,...,batch.b1:]
    return replace(batch,raw=raw)

def jitter_trials(flashes,trials,ordinals,rng):
    result=[]
    for row,units in zip(ordinals,trials):
        edges=spec.grid(float(flashes['start'][row]));out=[]
        for values in units:
            head=values[values<edges[-1]];tail=values[values>=edges[-1]]
            out.append(np.r_[spec.jitter_within_bins(head,edges,rng),tail])
        result.append(out)
    return result

def shift_trials(flashes,trials,ordinals,rng):
    return [[analysis_oracles.circular_shift(values,float(flashes['start'][row]),float(flashes['stop'][row]),rng) for values in units] for row,units in zip(ordinals,trials)]

def n2_check(original,changed,score_original,score_changed):
    np.testing.assert_array_equal(original.y,changed.y)
    np.testing.assert_allclose(original.raw[...,:original.b1+6],changed.raw[...,:changed.b1+6],rtol=0,atol=1e-12)
    for model in ['B0','B1','B2','B3','B4','D','S']:
        if not np.allclose(score_original[model],score_changed[model],rtol=0,atol=1e-12):raise ImplementationStop('Required N2 20ms invariance failed: '+model)

def all_effects(scores,mask,units):
    denominator=int(np.count_nonzero(mask))*units
    if denominator<=0:raise ImplementationStop('No valid comparison targets')
    for values in scores.values():
        if values.shape!=mask.shape or not np.isfinite(values).all():raise ImplementationStop('Nonfinite/mismatched score')
    absolute={key:float(values[mask].sum()/denominator) for key,values in scores.items()}
    effects={a+'-'+b:float((scores[a]-scores[b])[mask].sum()/denominator) for a,b in CONTRASTS if a in scores and b in scores}
    return {'absolute':absolute,'effects':effects,'actual_valid_unit_bins':denominator,'valid_bins':int(mask.sum()),
        'unregistered_refit_panel_contrasts':[a+'-'+b for a,b in CONTRASTS if a not in scores or b not in scores]}

def descriptive_groups(records):
    result={}
    for group,seed in [('BO',16043),('FC',16044)]:
        rows=sorted([x for x in records if x['protocol']==group],key=lambda x:int(x['mouse_id']))
        if len(rows)<(3 if group=='BO' else 10):raise ImplementationStop('Original BO/FC Development reporting floor')
        names=[a+'-'+b for a,b in CONTRASTS];values=np.array([[r['effects'][k] for k in names] for r in rows])
        draw=np.random.Generator(np.random.PCG64(seed)).integers(0,len(rows),size=(10000,len(rows)))
        ci=np.quantile(values[draw].mean(axis=1),[.025,.975],axis=0,method='linear')
        result[group]={'mouse_ids':[r['mouse_id'] for r in rows],'n':len(rows),'equal_mouse_mean':values.mean(axis=0).tolist(),
            'effect_names':names,'CI95':ci.tolist(),'bootstrap_replicates':10000,'seed':seed,'causal_protocol_effect':False,
            'absolute_model_means':{m:math.fsum(r['absolute'][m] for r in rows)/len(rows) for m in rows[0]['absolute']},
            'actual_unit_bins_sum_descriptive_not_inference_n':sum(r['actual_valid_unit_bins'] for r in rows)}
        result[group]['equal_mouse_mean']=[math.fsum(values[:,k])/len(rows) for k in range(values.shape[1])]
    return result

def aggregate_references(main_results,root):
    names=[a+'-'+b for a,b in CONTRASTS];out={};tails={}
    for operator in ['N1','N2','N3']:
        included=[];effects=[];absolute=[];unavailable=[]
        for row in sorted(main_results,key=lambda x:int(x['mouse_id'])):
            path=root/str(row['mouse_id'])/(operator+'.npz')
            if not path.exists():unavailable.append(row['mouse_id']);continue
            with np.load(path,allow_pickle=False) as a:effects.append(a['effects'].copy());absolute.append(a['absolute'].copy())
            included.append(row)
        if not included:
            out[operator]={'status':'UNAVAILABLE','mouse_ids':[],'unavailable_mouse_ids':unavailable};continue
        values=np.asarray(effects).mean(axis=0);absvalues=np.asarray(absolute).mean(axis=0)
        observed=np.array([math.fsum(row['effects'][k] for row in included)/len(included) for k in names])
        report={'status':'COMPLETED','mouse_ids':[r['mouse_id'] for r in included],'unavailable_mouse_ids':unavailable,
            'replicates':len(values),'observed_matched_equal_mouse_effects':observed.tolist(),
            'reference_mean_effects':values.mean(axis=0).tolist(),'reference_mean_absolute':absvalues.mean(axis=0).tolist(),
            'reference_effect_q025_q50_q95_q975':np.quantile(values,[.025,.5,.95,.975],axis=0,method='linear').tolist(),
            'reference_absolute_q025_q50_q95_q975':np.quantile(absvalues,[.025,.5,.95,.975],axis=0,method='linear').tolist()}
        if operator in ['N1','N3']:
            tail=(1+np.count_nonzero(values>=observed,axis=0))/(len(values)+1);tails[operator]=tail
            report['descriptive_reference_tail_fraction']=tail.tolist();report['exact_conditional_p_value']=False
            report['observed_exceeds_q95']=(observed>np.quantile(values,.95,axis=0,method='linear')).tolist()
        else:report['B_D_S_invariance']='PASS_ALL_REPLICATES';report['C_variation_not_forced_invariant']=True
        out[operator]=report
    if 'N1' in tails and 'N3' in tails:
        out['N1_N3_Holm2_descriptive_only']=[spec.holm([tails['N1'][k],tails['N3'][k]]).tolist() for k in range(6)]
    out['effect_names']=names;out['model_order']=['B0','B1','B2','B3','B4','C','D','S']
    n4=[]
    for row in sorted(main_results,key=lambda x:int(x['mouse_id'])):
        state=json.loads((root/str(row['mouse_id'])/'N4.json').read_bytes())
        n4.append({'mouse_id':row['mouse_id'],'true_B1_logscore':row['absolute']['B1'],**state})
    out['N4']={'status':'COMPLETED','operators':11,'no_p_value':True,'per_mouse':n4,'forced_degradation':False}
    out['Final_specific_gates']='NOT_EXECUTED_FINAL_BOUNDARY'
    return out
