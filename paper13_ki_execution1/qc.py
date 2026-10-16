"""Frozen real A/C operational QC, no optimizer or evaluation-score code."""
import json
import math
import datetime
import os
from pathlib import Path
import h5py
import numpy as np
from .source import P,ROOT,ALLOCATION,SourceReader,unit_window_export,node,sha,require_access_approval

def screen(epoch_spikes):
    if len(epoch_spikes)!=60:raise ValueError('Exactly60A/Cepochs required')
    n=0;occupied=0;isi_n=0;bad=0
    for ts in epoch_spikes:
        ts=np.asarray(ts,dtype=np.float64)
        if ts.ndim!=1 or not np.isfinite(ts).all() or np.any(ts<0) or np.any(ts>=3):return {'pass':False,'failure':'nonfinite_or_outside_training_epoch'}
        isi=np.diff(ts)
        if np.any(isi<=0):return {'pass':False,'failure':'not_strictly_ordered_training_timestamps'}
        n+=len(ts);occupied+=bool(len(ts));isi_n+=len(isi);bad+=int(np.sum(isi<.0015))
    rate=n/180;fraction=bad/isi_n if isi_n else None
    gates={'minimum_spikes':n>=50,'minimum_ISIs':isi_n>=30,'minimum_occupied_epochs':occupied>=12,'rate':.1<=rate<=100,'refractory_fraction':fraction is not None and fraction<=.01}
    return {'pass':all(gates.values()),'gates':gates,'training_spikes':n,'within_epoch_ISIs':isi_n,'refractory_ISIs':bad,'occupied_epochs':occupied,'rate_hz':rate,'refractory_fraction':fraction,'exposure_seconds':180}

def counts_for(epoch_spikes):
    edges=np.arange(31,dtype=float)/10
    return np.stack([np.histogram(ts,bins=edges)[0] for ts in epoch_spikes]).astype(np.int64)

def durable_record(path,event,**fields):
    row={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'event':event,**fields}
    raw=(json.dumps(row,allow_nan=False)+'\n').encode('utf8')
    with path.open('ab') as f:
        f.write(raw);f.flush();os.fsync(f.fileno())

def begin_mouse(root,record,source_freeze):
    journal=root/(record['mouse_id']+'.attempts.jsonl')
    # Existing incomplete/failed attempts never become an implicit QC retry.
    with journal.open('xb') as f:
        row={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'event':'MOUSE_START',
             'mouse_id':record['mouse_id'],'partition':record['QC_partition'],'source_freeze':source_freeze}
        f.write((json.dumps(row)+'\n').encode('utf8'));f.flush();os.fsync(f.fileno())
    return journal

def examine_unit(file,unit,record,partition,journal):
    identity={'mouse_id':record['mouse_id'],'partition':partition,**unit}
    durable_record(journal,'UNIT_START',**identity)
    try:
        ids=node(file,'/units/id')
        if int(ids[unit['row']])!=unit['unit_id']:raise ValueError('Unit identity changed')
        times=unit_window_export(file,unit['row'],record,partition)
        result=screen(times)
        durable_record(journal,'UNIT_COMPLETE',**identity,QC=result)
        return times,result
    except Exception as exc:
        durable_record(journal,'UNIT_ERROR',**identity,error_type=type(exc).__name__)
        raise

def completed_result(path,source_freeze):
    saved=json.loads(path.read_text())
    if saved['source_freeze']!=source_freeze:raise ValueError('Cannot reuse state under changed extraction implementation')
    journal=path.with_name(path.stem+'.attempts.jsonl')
    rows=[json.loads(x) for x in journal.read_text().splitlines()]
    state=ROOT/saved['training_state_file']
    if not rows or rows[-1].get('event')!='MOUSE_COMPLETE':raise ValueError('Incomplete QC completion journal; no retry')
    if rows[-1]['result_sha256']!=sha(path.read_bytes()):raise ValueError('QC result receipt mismatch')
    digest=sha(state.read_bytes())
    if digest!=saved['training_state_sha256'] or digest!=rows[-1]['training_state_sha256']:raise ValueError('QC state receipt mismatch')
    return saved

def main():
    approval=require_access_approval();freeze_path=P/approval['freeze_file'];freeze_hash=sha(freeze_path.read_bytes())
    root=P/'results/qc';root.mkdir(parents=True,exist_ok=True)
    sealed=P/'work/training_states';sealed.mkdir(parents=True,exist_ok=True)
    all_results=[]
    for r in ALLOCATION:
        path=root/(r['mouse_id']+'.json')
        if path.exists():
            saved=completed_result(path,freeze_hash)
            all_results.append(saved);continue
        part=r['QC_partition'];selected=[];attempts=[];values=[]
        journal=begin_mouse(root,r,freeze_hash)
        try:
            reader=SourceReader(r)
            with h5py.File(reader,'r') as h:
                for unit in r['PL_units_numeric_order']:
                    ts,q=examine_unit(h,unit,r,part,journal)
                    attempts.append({**unit,**q,'partition':part})
                    if q['pass']:
                        selected.append(unit);values.append(ts)
                        if len(selected)==8:break
        except Exception as exc:
            durable_record(journal,'MOUSE_ERROR',mouse_id=r['mouse_id'],error_type=type(exc).__name__)
            raise
        counts=np.stack([counts_for(x) for x in values],axis=-1) if values else np.zeros((60,30,0),dtype=np.int64)
        state=sealed/(r['mouse_id']+'.npz')
        # Only A/C-derived data, no full-record arrays or B/E/Dfeatures are saved.
        arrays={'counts':counts,'unit_ids':np.array([x['unit_id'] for x in selected],dtype=np.int64)}
        for j,ts in enumerate(values):
            arrays[f'unit{j}_times']=np.concatenate(ts);arrays[f'unit{j}_ends']=np.cumsum([len(x) for x in ts],dtype=np.int64)
        with state.open('xb') as f:np.savez_compressed(f,**arrays)
        result={'mouse_id':r['mouse_id'],'role':r['role'],'partition':part,'eligible':len(selected)==8,'selected_units':selected,'attempts':attempts,'unexamined_remaining_PL_units':len(r['PL_units_numeric_order'])-len(attempts),
                'all_units_physio_certified':False,'training_state_file':str(state.relative_to(ROOT)).replace('\\','/'),'training_state_sha256':sha(state.read_bytes()),'source_freeze':freeze_hash,
                'source_range_bytes':reader.used,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'B_E_D_exported':False,
                'source_boundary':'Trusted adapter transiently decodes selected unit rawrecord timestamp arrays; only60A/Cwindow values enter QC or saved state. No raw fullrecord statistics or Dneural outcomes exported.'}
        with path.open('x',encoding='utf8',newline='\n') as f:f.write(json.dumps(result,indent=2,allow_nan=False)+'\n')
        durable_record(journal,'MOUSE_COMPLETE',mouse_id=r['mouse_id'],result_sha256=sha(path.read_bytes()),training_state_sha256=result['training_state_sha256'])
        all_results.append(result)
        print(json.dumps({'mouse':r['mouse_id'],'role':r['role'],'eligible':result['eligible'],'QC_units_attempted':len(attempts),'A_C_only':True}),flush=True)
    dev=[x['mouse_id'] for x in all_results if x['role']=='development' and x['eligible']]
    final=[x['mouse_id'] for x in all_results if x['role']=='final' and x['eligible']]
    summary={'M2':'PASS' if len(dev)>=8 and len(final)>=8 else 'DATA_INSUFFICIENT','eligible_development':dev,'eligible_final':final,'all19_candidates':all_results,'D_outcomes_exported':False,'fits':0}
    with (P/'results/M2_GATE.json').open('x',encoding='utf8',newline='\n') as f:f.write(json.dumps(summary,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'M2':summary['M2'],'development':len(dev),'final':len(final)}))

if __name__=='__main__':main()
