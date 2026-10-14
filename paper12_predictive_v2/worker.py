"""Registered no-fit compatibility and mandatory coverage gate in native A/B role."""
import hashlib
import json
from pathlib import Path
import sys
def main():
    deps,data,output,source,key,pid,sddl=sys.argv[1:];sys.path[:0]=[deps,str(Path(__file__).parent)]
    code=Path(__file__).parent;out=Path(output);data=Path(data)
    def load(p):return json.loads(Path(p).read_text())
    def save(n,v):
        with (out/n).open('x',encoding='utf-8') as f:json.dump(v,f,indent=2,allow_nan=False)
    from native_analysis_check import check
    proof=check(source,key,pid,sddl);save('role_proof.json',proof)
    if not proof['pass']:raise PermissionError('NATIVE_ROLE')
    import unittest
    t=unittest.TestResult();unittest.defaultTestLoader.discover(str(code),pattern='test_selection.py').run(t)
    save('oracle_tests.json',{'count':t.testsRun,'passed':t.wasSuccessful(),'skips':len(t.skipped),'errors':str(t.errors),'failures':str(t.failures)})
    if not t.wasSuccessful() or t.testsRun!=5 or t.skipped:raise RuntimeError('SELECTION_REGRESSION')
    import numpy as np
    from scipy.special import gammaln
    from selection import views,expected_shape
    manifest=load(data/'manifest.json');rows=load(code/'baseline_records.json');offset=load(code/'offset_records.json');bundle=load(code/'offset_bundle.json');metadata=load(code/'development_metadata.json')
    if manifest['group']!='development' or manifest['compartments']!=['A','B'] or len(manifest['sessions'])!=13 or len({s['mouse_id'] for s in manifest['sessions']})!=13:raise RuntimeError('FROZEN_COHORT')
    expected={(s['session_id'],region,kind,ridge,seed) for s in manifest['sessions'] for region in ('CA1','DG') for kind in ('stationary','history','population','event','drift','combined') for ridge in ([None] if kind=='stationary' else [.001,.01,.1,1.]) for seed in (11,23,37)}
    actual={(z['session_id'],z['region'],z['kind'],z['ridge'],z['seed']) for z in rows}
    if len(rows)!=1638 or actual!=expected or any(not z['converged'] or not z['optimizer_success'] or z['projected_gradient']>.001 or not np.isfinite([z['training_LL_nats_per_unit_bin'],z['validation_LL_nats_per_unit_bin']]).all() for z in rows):raise RuntimeError('M3_ROSTER_NUMERICAL_GATE')
    for name,k in (('offset_states.npz','state_sha256'),('offset_records.json','records_sha256')):
        if hashlib.sha256((code/name).read_bytes()).hexdigest()!=bundle[k]:raise RuntimeError('OFFSET_HASH')
    if len(offset['rows'])!=78 or any(not z['converged'] or not z['optimizer_success'] or z['projected_gradient']>.001 for z in offset['rows']):raise RuntimeError('OFFSET_GATE')
    offsetkeys={(z['session_id'],z['region'],z['seed']) for z in offset['rows']}
    if offsetkeys!={(s['session_id'],region,seed) for s in manifest['sessions'] for region in ('CA1','DG') for seed in (11,23,37)}:raise RuntimeError('OFFSET_ROSTER')
    coverage=[];score_errors=[]
    for s in manifest['sessions']:
        p=data/s['file']
        if hashlib.sha256(p.read_bytes()).hexdigest()!=s['sha256']:raise RuntimeError('AB_HASH')
        with np.load(p,allow_pickle=False) as z:
            if any(k.endswith(('_C','_D')) for k in z.files):raise PermissionError('FINAL_INPUT_FORBIDDEN')
            ids={k:[str(v) for v in z[k+'_unit_ids']] for k in ('CA1','DG')}
            ms={k:[next(u for u in metadata if u['unit_id']==uid and u['session_id']==s['session_id']) for uid in ids[k]] for k in ids}
            rates={k:z[k+'_A'].mean(axis=(0,1))/.1 for k in ids}
            if any(ids[k]!=s['unit_ids'][k] for k in ids):raise RuntimeError('UNIT_IDENTITIES')
            for part in ('A','B'):
                if z['trial_ids_'+part].tolist()!=s['trial_ids'][part]:raise RuntimeError('TRIAL_IDENTITIES')
                if set(z['conditions_'+part].tolist())!=set(range(8)) or min(np.bincount(z['conditions_'+part],minlength=8))<({'A':24,'B':16}[part]):raise RuntimeError('FROZEN_CONDITION_COVERAGE')
            for k in ids:
                y=z[k+'_A'];v=z[k+'_B']
                if y.shape!=expected_shape(s,k,'A') or v.shape!=expected_shape(s,k,'B') or not 5<=y.shape[-1]<=32 or not np.isfinite(y).all() or not np.isfinite(v).all() or np.any(y<0) or np.any(v<0) or np.any(y!=np.floor(y)) or np.any(v!=np.floor(v)):raise RuntimeError('FROZEN_COUNT_SHAPE')
                selected=[r for r in rows if r['session_id']==s['session_id'] and r['region']==k]
                if any(r['data_sha256']!=s['sha256'] or r['training_unit_bins']!=y.size or r['validation_unit_bins']!=v.size or r['ridge_normalization']!='per_unit_exposure' for r in selected):raise RuntimeError('M3_SCORING_COMPATIBILITY')
                eta=np.log(y.mean(axis=(0,1)));score=float((v*eta-np.exp(eta)-gammaln(v+1)).sum()/v.size)
                for r in selected:
                    if r['kind']=='stationary':score_errors.append(abs(score-r['validation_LL_nats_per_unit_bin']))
                om=offset['meta'][s['session_id']+'_'+k]
                if om['parent_AB_sha256']!=s['sha256'] or om['training_array_sha256']!=hashlib.sha256(np.ascontiguousarray(y).tobytes()).hexdigest():raise RuntimeError('OFFSET_DATA_COMPATIBILITY')
            vv=views(rates['CA1'],rates['DG'],ms)
            coverage.append({'mouse_id':s['mouse_id'],'session_id':s['session_id'],'unit_ids':ids,'metadata':ms,'views':{name:{'CA1_count':len(q['CA1']),'DG_count':len(q['DG']),'CA1_indices':q['CA1'],'DG_indices':q['DG'],'eligible_pair':min(len(q['CA1']),len(q['DG']))>=5} for name,q in vv.items()},'rate_pairs_abs_log_ratio':[float(abs(np.log(rates['CA1'][i]/rates['DG'][j]))) for i,j in zip(vv['rate_matched']['CA1'],vv['rate_matched']['DG'])]})
    if max(score_errors)>1e-12:raise RuntimeError('STATIONARY_SCORER_ORACLE')
    required=['primary','matched16','rate_matched','boundary20','boundary40'];counts={name:sum(c['views'][name]['eligible_pair'] for c in coverage) for name in required}
    missing=[{'view':name,'eligible_paired_mice':n,'required':8} for name,n in counts.items() if n<8]
    save('coverage.json',{'mice':coverage,'paired_counts':counts,'critical_failures':missing})
    save('reuse_audit.json',{'M3_records':1638,'M3_all_converged':True,'M3_exact_source_hashes_controller_verified':True,'M3_fit_weights_saved':False,'M3_nonstationary_scores_verification':'Frozen scored records, unchanged scorer, denominators and prior numerical oracles; no unavailable endpoint weights claimed recomputed','stationary_score_max_abs_error':max(score_errors),'offset_records':78,'offset_states_hash_verified':True,'offset_training_hashes_verified':True,'new_fits':0,'final_access':False})
    save('gate_result.json',{'gate':'PASS','compatibility_integrity_pass':True,'scientific_coverage_pass':not missing,'scientific_stop':bool(missing),'stop_reason':'INSUFFICIENT_REGISTERED_SENSITIVITY_COVERAGE' if missing else None,'critical_failures':missing,'new_fits':0,'reused_M3':1638,'reused_offsets':78,'final_access':False,'development_scope':['A','B']})
if __name__=='__main__':
    try:main()
    except Exception as e:
        import traceback
        with (Path(sys.argv[3])/'failure.json').open('x',encoding='utf-8') as f:
            json.dump({'type':type(e).__name__,'message':str(e),'traceback':traceback.format_exc(),'new_fits':0,'final_access':False},f,indent=2)
        raise
