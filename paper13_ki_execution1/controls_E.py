"""Prospectively reviewed 999x4 E controls, frozen coefficients, no source IO."""
import json
import numpy as np
from .source import P,ROOT,ALLOCATION,sha
from . import baseline_A as b
from . import control_core as core
from .features import nuisance
from .qc import durable_record
from .fit_engine import ScientificStop


def approved():
    path=P/'M6_E_APPROVAL.json'
    if not path.is_file():raise PermissionError('Independent frozen M6 E-control review required')
    a=b.read(path)
    if not a.get('accepted'):raise PermissionError('M6 E control path unapproved')
    freeze=P/a['freeze_file']
    if sha(freeze.read_bytes())!=a['freeze_sha256'] or sha((ROOT/a['review_path']).read_bytes())!=a['review_sha256']:
        raise PermissionError('M6 E source/review mismatch')
    for name,digest in b.read(freeze)['hashes'].items():
        if sha((ROOT/name).read_bytes())!=digest:raise PermissionError('Unreviewed M6 E input: '+name)
    return sha(freeze.read_bytes())


def inputs():
    saved=b.read(P/'results/M5_EXPLORATORY_RESULTS.json')
    if saved.get('M5')!='PASS' or saved['scientific_scope']!='EXPLORATORY_DEVELOPMENT_ONLY_NOT_FINAL_VALIDATION':
        raise ScientificStop('Complete frozen M5 E before controls')
    by_id={r['mouse_id']:r for r in ALLOCATION};data={}
    for mouse in saved['mouse_order']:
        record=by_id[mouse]
        if record['role']!='development':raise PermissionError('E control worker denies final mice')
        model=P/'results/development_models'/(mouse+'.json');export=b.read(P/'results/exploratory_E'/(mouse+'.json'))
        state=ROOT/export['state_file']
        if sha(model.read_bytes())!=saved['model_state_identities'][mouse]['model_bundle_sha256'] or sha(state.read_bytes())!=saved['model_state_identities'][mouse]['E_state_sha256']:
            raise ScientificStop('Frozen E model/value identity mismatch')
        with np.load(state,allow_pickle=False) as arrays:y=arrays['counts'].copy()
        epochs=[e for e in record['epochs'] if e['partition']=='E']
        if y.shape!=(30,30,8) or len(epochs)!=30:raise ScientificStop('Original E count/epoch denominator mismatch')
        data[mouse]=(y,nuisance(record,epochs),b.read(model),[e['ordinal'] for e in epochs])
    return saved,data


def run():
    source=approved();saved,data=inputs();mice=saved['mouse_order']
    if mice!=sorted(mice) or len(mice)!=10:raise ScientificStop('Exact original ten development mice required')
    root=P/'results/m6_controls_E';root.mkdir(parents=True,exist_ok=True);journal=root/'actions.jsonl'
    with journal.open('xb'):pass
    durable_record(journal,'CONTROL_EXECUTION_START',source_freeze=source,replicates=999,seeds=core.SEEDS,mouse_order=mice)
    arrays={};active={}
    try:
        for suite in core.SUITES:
            active={'suite':suite};path=root/(suite+'.npy')
            with path.open('xb'):pass
            array=np.lib.format.open_memmap(path,mode='w+',dtype=np.float64,shape=(999,len(mice),len(core.LABELS)))
            array[:]=np.nan;array.flush();arrays[suite]=array;rng=np.random.default_rng(core.SEEDS[suite])
            for replicate in range(999):
                active={'suite':suite,'replicate':replicate}
                durable_record(journal,'REPLICATE_START',**active)
                for index,mouse in enumerate(mice):
                    active={'suite':suite,'replicate':replicate,'mouse_id':mouse}
                    y,q,bundle,ordinals=data[mouse]
                    with np.errstate(over='raise',invalid='raise',divide='raise'):
                        result=core.replicate(suite,y,q,bundle,ordinals,rng)
                    array[replicate,index]=[result['scores'][name] for name in core.LABELS];array.flush()
                    durable_record(journal,'MOUSE_CONTROL_COMPLETE',**active,nominal_unit_bins=result['nominal_unit_bins'])
                durable_record(journal,'REPLICATE_COMPLETE',suite=suite,replicate=replicate)
                if (replicate+1)%100==0:print(json.dumps({'M6_E_suite':suite,'completed_replicates':replicate+1,'no_new_fits':True}),flush=True)
            durable_record(journal,'SUITE_COMPLETE',suite=suite,completed_replicates=999,artifact_sha256=sha(path.read_bytes()))
        observed={mouse:saved['per_mouse'][mouse]['scores'] for mouse in mice}
        report,means=core.summarize(arrays,observed,mice)
        path=root/'equal_mouse_distributions.npz'
        with path.open('xb') as f:np.savez_compressed(f,**means)
        result={'M6_E_CONTROLS':'PASS','scope':'EXPLORATORY_CONTROLS_ONLY','source_freeze':source,'report':report,
            'score_labels':core.LABELS,'contrasts':['D_minus_B4','C_minus_B4','D_minus_C','D_minus_Bstar','C_minus_Bstar','D_minus_S'],
            'artifacts':{s:{'path':str((root/(s+'.npy')).relative_to(ROOT)).replace('\\','/'),'sha256':sha((root/(s+'.npy')).read_bytes())} for s in core.SUITES},
            'equal_mouse_distributions_sha256':sha(path.read_bytes()),'new_fits':0,'final_C_model_fits':0,'final_D_outcomes_accessed':False,
            'associated_broad_claim':'INCONCLUSIVE_PER_OWNER_PRE_D_COVERAGE_AMENDMENT; controls cannot rescue'}
        b.save_matching(P/'results/M6_E_CONTROLS_GATE.json',result)
        durable_record(journal,'CONTROL_EXECUTION_COMPLETE',status='PASS',mouse_replicates=39960)
        print(json.dumps({'M6_E_CONTROLS':'PASS','suites':4,'replicates_per_suite':999,'mouse_replicates':39960}),flush=True)
    except Exception as exc:
        for array in arrays.values():array.flush()
        failure={'M6_E_CONTROLS':'FAIL','source_freeze':source,'attempt':active,'error_type':type(exc).__name__,'error':str(exc),
            'retry_or_new_random_draw_authorized':False,'final_C_model_fits':0,'final_D_outcomes_accessed':False}
        durable_record(journal,'CONTROL_EXECUTION_ERROR',**failure)
        b.save_matching(P/'results/M6_E_CONTROLS_GATE.json',failure)
        raise


if __name__=='__main__':run()
