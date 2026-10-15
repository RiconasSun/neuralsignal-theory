"""Frozen C-state predictions, all registered statistics/nulls. Never fits a model."""
import time
from pathlib import Path
import numpy as np
if __package__:
    from .common import *
    from .frozen_math import load
else:
    from common import *
    from frozen_math import load

def verdict(statistics,null_statistics,source_gates):
    result={}
    coverage=all(statistics.get(v,{}).get('mice',0)>=8 for v in MANDATORY)
    for name in PRIMARY:
        p=statistics.get('primary',{}).get('statistics',{}).get(name)
        if p is None or not source_gates or not coverage:
            result[name]={'classification':'INCONCLUSIVE DUE TO FAILED REQUIRED GATE','registered_criteria_satisfied':False};continue
        sign=DEV_SIGN[name]
        ci=p['CI95'];direction=p['mean_CA1_minus_DG']*sign>0
        same_sensitivity=all(statistics[v]['statistics'][name]['mean_CA1_minus_DG']*sign>0 for v in MANDATORY if v!='primary')
        same_lomo=all(x*sign>0 for x in p['leave_one_mouse_out_means'])
        controls={suite:bool(null_statistics[suite+'_'+name]['pooled_holm_p']<=.05 and null_statistics[suite+'_'+name]['regional_holm_p']<=.05) for suite in ('T','S','B','O')}
        relevant=any(controls[suite] for suite in RELEVANT[name])
        passed=bool(p['holm_p']<=.05 and (ci[0]>0 or ci[1]<0) and direction and same_sensitivity and same_lomo and relevant)
        result[name]={'classification':'VALIDATED UNDER REGISTERED CRITERIA' if passed else 'NOT VALIDATED / MIXED','registered_criteria_satisfied':passed,'Holm_pass':p['holm_p']<=.05,'CI_excludes_zero':ci[0]>0 or ci[1]<0,'direction_matches_development':direction,'sensitivity_signs_consistent':same_sensitivity,'all_LOMO_signs_consistent':same_lomo,'corrected_same_suite_controls':controls,'relevant_null_pass':relevant}
    return result

def probe_report(rows,manifest):
    answer=[]
    for mouse in manifest['cohort']:
        local=[r for r in rows if r['mouse_id']==mouse];paired={}
        for view in sorted({r['view'] for r in local}):
            pair={r['region']:r for r in local if r['view']==view}
            if set(pair)=={'CA1','DG'}:paired[view]={k:pair['CA1']['gains'][k]-pair['DG']['gains'][k] for k in PRIMARY}
        shared=next((v for v in paired if v.startswith('shared_probe_')),None);leave=[v for v in paired if v.startswith('leave_probe_')]
        for name in PRIMARY:
            values=[paired[v][name] for v in leave];changes=[paired[v][name]-paired['primary'][name] for v in leave+([] if shared is None else [shared])]
            answer.append({'mouse_id':mouse,'contrast':name,'primary':paired['primary'][name],'shared_view':shared,'shared_difference':None if shared is None else paired[shared][name],'LOPO_views':leave,'LOPO_differences':values,'LOPO_min':min(values) if values else None,'LOPO_max':max(values) if values else None,'max_abs_shift':max(map(abs,changes)) if changes else None})
    return answer

def rate_report(roster):
    rows=[]
    for session in roster['sessions']:
        views=session['views']['rate_matched'];rates=session['rates_C_Hz']
        errors=[abs(float(np.log(rates['CA1'][a]/rates['DG'][b]))) for a,b in zip(views['CA1'],views['DG'])]
        if any(e>float(np.log(2))+1e-14 for e in errors):raise PermissionError('REGISTERED_C_RATE_PAIR_TOLERANCE')
        rows.append({'mouse_id':session['mouse_id'],'matched_K':len(errors),'abs_log_rate_ratios':errors,'median_abs_log_rate_ratio':float(np.median(errors)) if errors else None,'max_abs_log_rate_ratio':max(errors) if errors else None,'within_original_log2':True})
    return {'rows':rows,'rate_source':'C_ONLY','exact_rate_equalization':False,'new_selection':False}

def summarize_nulls(manifest,output,holm):
    nulls={};keys=[];pooled_p=[];regional_p=[]
    for suite in ('T','S','B','O'):
        ca=[];dg=[];oc=[];od=[]
        for mouse in sorted(manifest['cohort']):
            for region,values,observed in (('CA1',ca,oc),('DG',dg,od)):
                record=read_json(output/('null_'+mouse+'_'+region+'_'+suite+'.json'))
                if record['replicates']!=999 or np.asarray(record['gains']).shape!=(999,4) or not np.isfinite(record['gains']).all() or not np.isfinite(record['observed']).all():raise PermissionError('COMPLETE_FINITE_NULL_REPLICATES')
                values.append(record['gains']);observed.append(record['observed'])
        ca=np.array(ca);dg=np.array(dg);pool=(ca+dg).mean(axis=0)/2;difference=(ca-dg).mean(axis=0)
        observed_pool=(np.array(oc)+np.array(od)).mean(axis=0)/2;observed_difference=(np.array(oc)-np.array(od)).mean(axis=0);center=difference.mean(axis=0)
        for i,name in enumerate(PRIMARY):
            p=float((1+np.sum(pool[:,i]>=observed_pool[i]))/1000)
            r=float((1+np.sum(np.abs(difference[:,i]-center[i])>=abs(observed_difference[i]-center[i])))/1000)
            key=suite+'_'+name;keys.append(key);pooled_p.append(p);regional_p.append(r)
            nulls[key]={'suite':suite,'contrast':name,'observed_pooled_gain':float(observed_pool[i]),'null_pooled_mean':float(pool[:,i].mean()),'null_pooled95':np.quantile(pool[:,i],[.025,.975]).tolist(),'pooled_exceedance_p':p,'observed_CA1_minus_DG':float(observed_difference[i]),'null_CA1_minus_DG_mean':float(center[i]),'null_CA1_minus_DG95':np.quantile(difference[:,i],[.025,.975]).tolist(),'regional_centered_exceedance_p':r,'replicates':999,'mice':13}
    for key,p,r in zip(keys,holm(pooled_p),holm(regional_p)):nulls[key].update(pooled_holm_p=p,regional_holm_p=r)
    return nulls

def evaluate(binding_root,delivery_root,output,expected,wall_limit=43200):
    start=time.monotonic();binding_root=Path(binding_root);delivery_root=Path(delivery_root);output=Path(output)
    manifest=read_json(binding_root/'C_state_manifest.json');partition=read_json(binding_root/'partition_manifest.json');delivered=read_json(delivery_root/'delivery_manifest.json')
    validate_state_manifest(manifest,binding_root)
    validate_partition(manifest,partition,read_json(binding_root/'animals.json') if not manifest['synthetic'] else None,read_json(binding_root/'trials.json') if not manifest['synthetic'] else None)
    for name in ('realm','authorization_id','binding','principal','C_manifest_sha256','partition_sha256','code_sha256'):
        if delivered[name]!=expected[name]:raise PermissionError('DELIVERY_BINDING:'+name)
    if delivered['complete'] is not True or delivered['cohort']!=manifest['cohort'] or set(delivered['sessions'])!=set(manifest['cohort']):raise PermissionError('DELIVERY_COMPLETE_COHORT')
    math=load();g=math['glm'];n=math['nulls'];s=math['mouse_statistics'];cachetype=math['null_cache'].Cache
    rows=[];states=np.load(binding_root/'complete_states.npz',allow_pickle=False);null_cases=0;invariants=0;cache_checks=0
    try:
        for mouse in manifest['cohort']:
            d=delivered['sessions'][mouse];path=safe(delivery_root,delivery_root/d['file'])
            if sha(path)!=d['sha256']:raise PermissionError('DELIVERED_ARRAY_HASH')
            part=partition['sessions'][mouse];cases=[c for c in manifest['cases'] if c['mouse_id']==mouse]
            with np.load(path,allow_pickle=False) as z:
                required={'CA1_D','DG_D','CA1_unit_ids','DG_unit_ids','trial_ids_D','conditions_D','orders_D'}
                if set(z.files)!=required or z['trial_ids_D'].tolist()!=part['trial_ids'] or z['conditions_D'].tolist()!=part['conditions'] or z['orders_D'].tolist()!=part['orders']:raise PermissionError('EXACT_D_ARRAY_CONTEXT')
                for region in ('CA1','DG'):
                    primary=next(c for c in cases if c['region']==region and c['view']=='primary')
                    if z[region+'_unit_ids'].tolist()!=primary['unit_ids'] or z[region+'_D'].shape!=(len(part['trial_ids']),20,32):raise PermissionError('EXACT_D_SELECTED_UNITS')
                for case in cases:
                    ids=case['selection'];y=z[case['region']+'_D'][:,:,ids].astype(float);c=z['conditions_D'];o=z['orders_D'];ms=(states[case['mean_key']],states[case['scale_key']])
                    x=g.transform(g.raw(y,c,o),ms);weights={name:states[value['key']] for name,value in case['models'].items()};scores={name:g.score(y,x,w) for name,w in weights.items()}
                    rows.append({'mouse_id':mouse,'session_id':case['session_id'],'region':case['region'],'view':case['view'],'case':case['case'],'unit_ids':case['unit_ids'],'selection':ids,'D_trials':len(y),'units':len(ids),'nominal_unit_bins':int(y.size),'scores':scores,'gains':g.gains(scores),'C_scaler_sha256':case['scaler_sha256']})
                    if time.monotonic()-start>wall_limit:raise RuntimeError('FROZEN_PHASE_WALL_LIMIT')
                for region in ('CA1','DG'):
                    case=next(c for c in cases if c['region']==region and c['view']=='primary');y=z[region+'_D'].astype(int);c=z['conditions_D'];o=z['orders_D'];ms=(states[case['mean_key']],states[case['scale_key']]);w=np.stack([states[case['models'][name]['key']] for name in n.NAMES])
                    original=n.eta(y,c,o,w,ms);observed=n.get_gains(y,original);reference=next(r for r in rows if r['mouse_id']==mouse and r['region']==region and r['view']=='primary')
                    np.testing.assert_allclose(observed,[reference['gains'][name] for name in PRIMARY],atol=1e-12,rtol=0);cache=cachetype(y,c,o,w,ms)
                    for suite in ('T','S','B','O'):
                        values=[]
                        for rep in range(999):
                            random=n.rng(case['session_id'],region,suite,rep)
                            if suite=='T':
                                changed=n.temporal(y,original[n.NAMES.index('N')],random);prediction=n.eta(changed,c,o,w,ms);invariants+=1
                            else:
                                changed=y;cc,oo,bb=n.permute_labels(c,o,suite,random);prediction=cache.predict(cc,oo,bb,suite)
                                if rep in (0,998):
                                    direct=n.eta(y,cc,oo,w,ms,bb);np.testing.assert_allclose(prediction,direct,atol=1e-12,rtol=0);np.testing.assert_allclose(n.get_gains(y,prediction),n.get_gains(y,direct),atol=1e-12,rtol=0);cache_checks+=1
                            values.append(n.get_gains(changed,prediction).tolist())
                            if rep%100==0:new(output/('progress_'+mouse+'_'+region+'_'+suite+'_'+str(rep)+'.json'),{'mouse':mouse,'region':region,'suite':suite,'replicate':rep,'elapsed_seconds':time.monotonic()-start})
                            if time.monotonic()-start>wall_limit:raise RuntimeError('FROZEN_PHASE_WALL_LIMIT')
                        new(output/('null_'+mouse+'_'+region+'_'+suite+'.json'),{'mouse_id':mouse,'session_id':case['session_id'],'region':region,'suite':suite,'replicates':999,'gains':values,'observed':observed.tolist(),'fixed_predictors':True,'null_refits':0,'trial_assignment_changed':False})
                        null_cases+=1
            new(output/('completed_'+mouse+'.json'),{'mouse':mouse,'completed_null_cases':null_cases,'elapsed_seconds':time.monotonic()-start})
    finally:states.close()
    if null_cases!=104 or len(rows)!=len(manifest['cases']):raise PermissionError('COMPLETE_ALL_REGISTERED_OUTPUTS')
    statistics=s.aggregate(rows);statistics['primary']['status']='SYNTHETIC_REGISTERED_CRITERIA' if manifest['synthetic'] else 'HELD_OUT_REGISTERED_PRIMARY'
    null_statistics=summarize_nulls(manifest,output,s.holm);verdicts=verdict(statistics,null_statistics,True);probes=probe_report(rows,manifest)
    result={'realm':delivered['realm'],'cohort':manifest['cohort'],'mouse_statistics':statistics,'null_statistics':null_statistics,'verdicts':verdicts,'units':'nats per actual nominal curated-release unit-bin','scope':'SYNTHETIC_ENGINEERING_ONLY' if manifest['synthetic'] else 'ONE_FINAL_D_ASSESSMENT','new_fits':0}
    roster=read_json(binding_root/'provenance_roster.json')
    new(output/'scientific_scores.json',{'rows':rows});new(output/'final_statistics.json',result);new(output/'probe_assessment.json',{'rows':probes,'unit_probe_composition':roster,'descriptive_only':True});new(output/'rate_assessment.json',rate_report(roster))
    report='# '+result['scope']+'\n\nAll13mice; no refitting or selection.\n\n|Contrast|CA1gain|DGgain|Difference|CI95|Rawp|Holmp|Registered outcome|\n|---|---|---|---|---|---|---|\n'
    for name in PRIMARY:
        r=statistics['primary']['statistics'][name];report+='|'+ '|'.join(map(str,[name,r['mean_CA1_gain'],r['mean_DG_gain'],r['mean_CA1_minus_DG'],r['CI95'],r['paired_signflip_p'],r['holm_p'],verdicts[name]['classification']]))+'|\n'
    with (output/'report.md').open('x',encoding='utf-8',newline='\n') as f:f.write(report)
    return {'gate':'PASS','synthetic':manifest['synthetic'],'scored_cases':len(rows),'mice':13,'null_cases':null_cases,'null_replicates_per_case':999,'null_evaluations':104*999,'count_preserving_checks':invariants,'cache_parity_checks':cache_checks,'new_fits':0,'elapsed_seconds':time.monotonic()-start,'D_EVALUATION_EXECUTED':not manifest['synthetic'],'SCIENTIFIC_VALIDATION_PASS':False,'synthetic_evaluator_executed':manifest['synthetic']}
