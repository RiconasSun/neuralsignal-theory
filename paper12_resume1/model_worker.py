"""Native restricted development-only frozen M4 competition."""
import json
import hashlib
from pathlib import Path
import sys


def main():
    deps,data,output,source,key,pid,sddl=sys.argv[1:]
    sys.path.insert(0,deps);sys.path.insert(0,str(Path(__file__).parent))
    from native_analysis_check import check
    proof=check(source,key,pid,sddl);output=Path(output);output.mkdir(exist_ok=True)
    def save(name,value):
        with (output/name).open('x',encoding='utf-8') as f:json.dump(value,f,indent=2,allow_nan=False)
    save('role_proof.json',proof)
    if proof['pass'] is not True:raise PermissionError('NATIVE_ANALYSIS_ISOLATION_FAILED')
    import numpy as np
    import model_math as m
    from task_offset import fit_offset
    from competition import select
    data=Path(data);manifest=json.loads((data/'manifest.json').read_text())
    if manifest['group']!='development' or manifest['compartments']!=['A','B'] or manifest['ridge_normalization']!='per_unit_exposure':raise PermissionError('DEVELOPMENT_AB_ONLY')
    if len(manifest['sessions'])<8:raise RuntimeError('DEVELOPMENT_DENOMINATOR_FAILED')
    bundle=json.loads(Path(__file__).with_name('baseline_metrics.json').read_text())
    rows=bundle['rows'];sessions=[x['session_id'] for x in manifest['sessions']]
    if set(sessions)!={x['session_id'] for x in rows}:raise RuntimeError('M3_SESSION_IDENTITY_CHANGED')
    critical=None
    for session in manifest['sessions']:
        path=data/session['file']
        if hashlib.sha256(path.read_bytes()).hexdigest()!=session['sha256']:raise RuntimeError('INPUT_CHANGED')
        with np.load(path,allow_pickle=False) as saved:
            for region in ('CA1','DG'):
                y=saved[region+'_A'];valid=saved[region+'_B']
                matched=[row for row in rows if row['family']=='baseline' and row['session_id']==session['session_id'] and row['region']==region]
                if len(matched)!=63:raise RuntimeError('M3_BASELINE_DENOMINATOR_CHANGED')
                for baseline in matched:
                    if baseline['data_sha256']!=session['sha256'] or baseline['training_unit_bins']!=y.size or baseline['validation_unit_bins']!=valid.size or baseline['mouse_id']!=session['mouse_id']:
                        raise RuntimeError('M3_M4_MATCHED_INPUT_BINDING_FAILED')
                ot,ov,xt,xv,diagnostics=fit_offset(y,valid,saved['conditions_A'],saved['conditions_B'],saved['orders_A'],saved['orders_B'])
                save(session['session_id']+'_'+region+'_offset.json',dict(mouse_id=session['mouse_id'],session_id=session['session_id'],region=region,
                    seeds=diagnostics,shared_parameters=29*y.shape[-1],same_offset_all_families=True,validation_selection=False))
                if any(x['converged'] is not True for x in diagnostics):
                    critical='MANDATORY_SHARED_OFFSET_FAILURE';break
                for family in ('Discrete','Continuous','Hybrid'):
                    for size in ((1,2,4) if family=='Continuous' else (2,3,4)):
                        for ridge in (.001,.01,.1,1.):
                            train=m.make(family,y,xt,ot,size);validation=m.make(family,valid,xv,ov,size)
                            for seed in (11,23,37):
                                row=dict(mouse_id=session['mouse_id'],session_id=session['session_id'],region=region,family=family,
                                    kind=None,size=size,ridge=ridge,seed=seed,data_sha256=session['sha256'],shared_parameters=29*y.shape[-1])
                                try:
                                    theta,metrics=m.fit(train,validation,ridge,seed);row.update(metrics)
                                    row['parameter_count']=row['shared_parameters']+row['model_specific_parameters']
                                    row['training_bins_per_parameter']=y.shape[0]*y.shape[1]/row['parameter_count']
                                    scores=validation.score_bins(theta)
                                    row['validation_trial_LL_nats_per_unit_bin']=(scores.sum(axis=1)/(20*valid.shape[-1])).tolist()
                                    if family!='Continuous':
                                        reference=m.SequentialState(valid,ov,size,5 if family=='Hybrid' else 0)
                                        discrepancy=float(np.max(np.abs(scores-reference.score_bins(theta))))
                                        row['exact_sequential_max_bin_discrepancy']=discrepancy
                                        if discrepancy>1e-10:critical='EXACT_FORWARD_PARITY_FAILED';row['converged']=False
                                except Exception as exc:
                                    row.update(converged=False,error_type=type(exc).__name__,error_code='FROZEN_MODEL_FIT_FAILED',
                                               parameter_count=row['shared_parameters']+train.n_parameters,model_specific_parameters=train.n_parameters)
                                rows.append(row)
                                save('%s_%s_%s_%s_%s_%s.json'%(session['session_id'],region,family,size,ridge,seed),row)
                                if critical:break
                            if critical:break
                        if critical:break
                    if critical:break
                if critical:break
        print(json.dumps(dict(session_id=session['session_id'],M4_fit_records=sum(r['family']!='baseline' for r in rows))),flush=True)
        if critical:break
    expected=len(sessions)*2*57*3
    chosen=None
    if not critical and len(rows)==expected:
        try:chosen=select(rows,sessions)
        except RuntimeError as exc:critical=str(exc)
    elif not critical:critical='INCOMPLETE_FIT_DENOMINATOR'
    if chosen is not None:save('selection_manifest.json',chosen)
    save('comparison_rows.json',dict(rows=rows))
    gate=dict(gate='PASS' if chosen is not None else 'FAIL',scientific_verdict='DEVELOPMENT_REPRESENTATION_COMPARISON' if chosen is not None else 'INCONCLUSIVE',
        mouse_count=len(sessions),expected_competition_fit_count=expected,completed_competition_fit_count=len(rows),
        converged_fit_count=sum(r['converged'] for r in rows),failure=critical,
        final_values_exposed_to_analysis=False,final_holdout_evaluated=False,NAP_CWP_validated=False)
    save('gate_result.json',gate)
    if chosen is None:sys.exit(2)


if __name__=='__main__':
    try:main()
    except Exception as exc:
        print(json.dumps(dict(aborted=True,error_type=type(exc).__name__,error_code='RESTRICTED_M4_ABORT')),flush=True);sys.exit(1)
