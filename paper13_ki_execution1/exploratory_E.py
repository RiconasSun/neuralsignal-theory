"""Reviewed E-only exploratory reporting; frozen models, no selection or refit."""
import json
import h5py
import numpy as np
from .source import P,ROOT,ALLOCATION,SourceReader,node,load_unit,cut_windows,sha
from .qc import durable_record
from . import baseline_A as b
from . import development_bundle as bundles
from .features import nuisance
from .predictive import evaluate
from .animal_stats import summarize
from .fit_engine import ScientificStop


def approved():
    path=P/'M5_E_APPROVAL.json'
    if not path.is_file():raise PermissionError('Fresh independent exploratory E approval required')
    a=b.read(path)
    if not a.get('accepted'):raise PermissionError('E path not accepted')
    freeze=P/a['freeze_file']
    if sha(freeze.read_bytes())!=a['freeze_sha256'] or sha((ROOT/a['review_path']).read_bytes())!=a['review_sha256']:
        raise PermissionError('E source/review hash mismatch')
    for name,digest in b.read(freeze)['hashes'].items():
        if sha((ROOT/name).read_bytes())!=digest:raise PermissionError('Unreviewed E source/artifact: '+name)
    return sha(freeze.read_bytes())


def windows(record):
    if record['role']!='development':raise PermissionError('E adapter denies final mice before source values')
    result=[e for e in record['epochs'] if e['partition']=='E']
    if len(result)!=30:raise ScientificStop('Exactly30frozen Eepochs required')
    return result


def export(record,qc,source_hash):
    epochs=windows(record)
    if source_hash!=approved():raise PermissionError('E export review identity mismatch')
    m4=b.read(P/'results/M4_MODEL_SELECTION.json');gate=b.read(P/'results/M4_A_GATE.json')
    if m4.get('M4')!='PASS' or gate.get('M4_A_NUMERICS')!='PASS' or gate.get('completed')!=540:raise ScientificStop('Full M4 must PASS before E')
    if qc!=b.read(P/'results/qc'/(record['mouse_id']+'.json')) or qc['mouse_id']!=record['mouse_id'] or qc['partition']!='A' or len(qc['selected_units'])!=8:
        raise PermissionError('Only frozen A-selected units in E')
    root=P/'results/exploratory_E';root.mkdir(parents=True,exist_ok=True)
    path=root/(record['mouse_id']+'.json');journal=root/(record['mouse_id']+'.attempts.jsonl')
    if path.exists():
        result=b.read(path);rows=[json.loads(line) for line in journal.read_text(encoding='utf8').splitlines()]
        if result['source_freeze']!=source_hash or rows[-1]['event']!='E_EXPORT_COMPLETE' or rows[-1]['result_sha256']!=sha(path.read_bytes()):raise ScientificStop('E export incomplete/changed; no implicit retry')
        if sha((ROOT/result['state_file']).read_bytes())!=result['state_sha256']:raise ScientificStop('E saved-state hash mismatch')
        return result
    with journal.open('xb'):pass
    durable_record(journal,'E_EXPORT_START',mouse_id=record['mouse_id'],source_freeze=source_hash,partition='E')
    state=P/'work/exploratory_E'/(record['mouse_id']+'.npz');state.parent.mkdir(parents=True,exist_ok=True)
    arrays={};counts=[];active=None
    try:
        reader=SourceReader(record)
        with h5py.File(reader,'r') as h:
            for j,unit in enumerate(qc['selected_units']):
                active=unit['unit_id'];durable_record(journal,'E_UNIT_START',mouse_id=record['mouse_id'],unit_id=active)
                if int(node(h,'/units/id')[unit['row']])!=active:raise ScientificStop('E unit identity mismatch')
                times=cut_windows(load_unit(h,unit['row']),epochs)
                counts.append(np.stack([np.histogram(ts,bins=np.arange(31)/10)[0] for ts in times]))
                arrays[f'unit{j}_times']=np.concatenate(times);arrays[f'unit{j}_ends']=np.cumsum([len(ts) for ts in times],dtype=np.int64)
                durable_record(journal,'E_UNIT_COMPLETE',mouse_id=record['mouse_id'],unit_id=active);active=None
        arrays.update(counts=np.stack(counts,axis=-1).astype(np.int64),unit_ids=np.array([u['unit_id'] for u in qc['selected_units']],dtype=np.int64))
        with state.open('xb') as f:np.savez_compressed(f,**arrays)
        result={'mouse_id':record['mouse_id'],'partition':'E','source_freeze':source_hash,'unit_ids':arrays['unit_ids'].tolist(),
            'epochs_sha256':sha(b.canonical(epochs)),'state_file':str(state.relative_to(ROOT)).replace('\\','/'),'state_sha256':sha(state.read_bytes()),
            'QC_scaling_selection_or_fitting_on_E':False,'final_D_exported':False}
        with path.open('x',encoding='utf8') as f:json.dump(result,f,indent=2)
        durable_record(journal,'E_EXPORT_COMPLETE',mouse_id=record['mouse_id'],result_sha256=sha(path.read_bytes()),state_sha256=result['state_sha256'])
        return result
    except Exception as exc:
        if active is not None:durable_record(journal,'E_UNIT_ERROR',mouse_id=record['mouse_id'],unit_id=active,error_type=type(exc).__name__)
        durable_record(journal,'E_EXPORT_ERROR',mouse_id=record['mouse_id'],error_type=type(exc).__name__)
        raise


def run():
    source_hash=approved();m2,qcs,baselines,m3,families,m4=bundles.gates()
    root=P/'results/exploratory_E';root.mkdir(parents=True,exist_ok=True);actions=root/'score_actions.jsonl'
    per_mouse={};core_scores={};identities={}
    for record in ALLOCATION:
        mouse=record['mouse_id']
        if mouse not in m2['eligible_development']:continue
        qc=qcs[mouse];bundle=bundles.build(mouse,qc,baselines,m3,families,m4)
        model_path=P/'results/development_models'/(mouse+'.json');model_hash=b.save_matching(model_path,bundle)
        exported=export(record,qc,source_hash);state_path=ROOT/exported['state_file']
        with np.load(state_path,allow_pickle=False) as state:
            y=state['counts'].copy();ids=state['unit_ids'].copy()
        if y.shape!=(30,30,8) or ids.tolist()!=[u['unit_id'] for u in bundle['units']]:raise ScientificStop('E bundle count/unit mismatch')
        q=nuisance(record,windows(record))
        durable_record(actions,'E_SCORE_START',mouse_id=mouse,model_bundle_sha256=model_hash,state_sha256=exported['state_sha256'])
        try:scored=evaluate(y,q,bundle,return_sequences=True)
        except Exception as exc:
            durable_record(actions,'E_SCORE_ERROR',mouse_id=mouse,error_type=type(exc).__name__);raise
        sequence_path=root/(mouse+'_bin_scores.npz')
        with sequence_path.open('xb') as f:np.savez_compressed(f,**scored.pop('joint_bin_log_scores'))
        per_mouse[mouse]=scored
        core_scores[mouse]={name:scored['scores'][name] for name in ['B4','D','C','Bstar','S']}
        identities[mouse]={'model_bundle_sha256':model_hash,'E_state_sha256':exported['state_sha256'],
            'joint_bin_scores_sha256':sha(sequence_path.read_bytes()),'epochs_sha256':exported['epochs_sha256']}
        durable_record(actions,'E_SCORE_COMPLETE',mouse_id=mouse,scores=scored['scores'],nominal_unit_bins=scored['nominal_unit_bins'])
        print(json.dumps({'M5_E_scored':mouse,'model_roles':8,'score_labels_including_Bstar_alias':9,'nominal_unit_bins':scored['nominal_unit_bins'],'no_selection_or_fitting':True}),flush=True)
    mice=sorted(m2['eligible_development']);statistics,arrays=summarize(core_scores,mice)
    boot=root/'mouse_bootstrap.npz'
    with boot.open('xb') as f:np.savez_compressed(f,**arrays)
    result={'M5':'PASS','scientific_scope':'EXPLORATORY_DEVELOPMENT_ONLY_NOT_FINAL_VALIDATION','source_freeze':source_hash,
        'mouse_order':mice,'per_mouse':per_mouse,'model_state_identities':identities,'registered_statistics':statistics,
        'bootstrap_file_sha256':sha(boot.read_bytes()),'selection_changed_after_E':False,'new_fits':0,'final_D_outcomes_accessed':False,
        'interpretation':'Same development mice previously used for A fitting/B selection; E cannot validate or retune. Final C/review/D and applicable registered controls/sensitivities still required.'}
    b.save_matching(P/'results/M5_EXPLORATORY_RESULTS.json',result)
    print(json.dumps({'M5':'PASS','scope':'EXPLORATORY_ONLY','final_D_outcomes_accessed':False}),flush=True)


if __name__=='__main__':run()
