"""Saved-only native-state/hash/QC/transport replay; never performs source HTTP."""
import hashlib
import json
import platform
from collections import Counter,defaultdict
from importlib.metadata import version
from unittest.mock import patch
import numpy as np
from .core import R,P,E,S,load,sha,registration,verify_history,verify_saved_A,source_inputs,array_id,qc_a,select_common


def verify_saved():
    reg=registration();verify_history()
    expected=load(R/'paper16_m1/NUMERICAL_POLICY.json')['software']
    runtime={'Python':platform.python_version(),**{n:version(n) for n in ['numpy','scipy','h5py','requests']}}
    assert runtime==expected,'Pinned scientific runtime required'
    verify_saved_A(reg['objects'][3],19)
    complete=[];attempts=[];new_A=0;incomplete=[]
    for i,item in enumerate(reg['objects']):
        if i<3:
            _,rows=verify_saved_A(item,len(item['candidate_unit_ids']))
            result=load(S/'results/sources'/str(item['session_id'])/'RESULT.json');assert result['source_pass'] and result['A_QC_complete']
            complete.append(result);continue
        folder=P/'results/sources'/str(item['session_id'])
        if not folder.exists():continue
        attempts.append(item['session_id']);assert load(folder/'ATTEMPT.json')['source']==item
        rows=[json.loads(s) for s in (folder/'UNIT_QC.jsonl').read_text(encoding='utf8').splitlines()] if (folder/'UNIT_QC.jsonl').exists() else []
        assert [x['unit_id'] for x in rows]==item['candidate_unit_ids'][:len(rows)]
        _,flashes,running,_=source_inputs(item)
        prefix=19 if i==3 else 0
        if i==3 and rows:
            oldraw,oldrows=verify_saved_A(item,19)
            assert (folder/'UNIT_QC.jsonl').read_bytes().startswith(oldraw) and rows[:19]==oldrows
        for j,row in enumerate(rows):
            capture=row['private_A_capture'];path=(R/capture['private_path']).resolve()
            path.relative_to(((S if j<prefix else P)/'work/private/A'/str(item['session_id'])).resolve())
            assert sha(path)==capture['sha256']
            with np.load(path,allow_pickle=False) as saved:arrays={k:saved[k].copy() for k in saved.files}
            assert {k:array_id(v) for k,v in arrays.items()}==capture['arrays']
            assert qc_a(arrays,flashes['start'],reg)==row['A_physiology']
            if j>=prefix:new_A+=1
        if (folder/'RESULT.json').exists():
            result=load(folder/'RESULT.json');assert result['source_pass'] and result['A_QC_complete']
            assert len(rows)==len(item['candidate_unit_ids'])==result['candidate_units_examined_total']
            assert result['historical_R3_candidate_states_reused']==prefix
            assert result['new_R4_candidate_states']==len(rows)-prefix
            assert select_common(rows,flashes['color'],running['missing'],reg)==result['selection']
            assert not result['B_E_arrays_exported'] and not result['Final_C_access'] and not result['Final_D_access']
            assert result['model_fits']==result['running_acquisition_calls']==0
            complete.append(result)
        else:incomplete.append(item['session_id'])
    journal_path=P/'results/TRANSPORT.jsonl'
    journal=[json.loads(s) for s in journal_path.read_text(encoding='utf8').splitlines()] if journal_path.exists() else []
    states=defaultdict(lambda:{'requests':0,'reserved':0,'payload':0,'recovery_slots':0});get_counts=Counter();actual_retries=0
    for row in journal:
        sid=row['session_id'];state=states[sid]
        if row['event']=='RESERVED':
            assert row['request']==state['requests']+1
            assert row['reserved_bytes']==row['expected_bytes']+1 and 0<=row['expected_bytes']<=1048576
            state['requests']+=1;state['reserved']+=row['reserved_bytes']
        elif row['event']=='PAYLOAD':assert row['bytes']>0;state['payload']+=row['bytes']
        elif row['event']=='RETRY_SLOT_RESERVED':state['recovery_slots']+=1
        elif row['event']=='HTTP_SENT' and row['method']=='GET':
            key=(sid,row['offset'],row['length']);get_counts[key]+=1
            if row['attempt']==2:actual_retries+=1
    assert all(v<=2 for v in get_counts.values())
    assert all(v['requests']<=8192 and v['reserved']<=536870912 and v['recovery_slots']<=2 and v['payload']<=v['reserved'] for v in states.values())
    reserved=sum(v['reserved'] for v in states.values());payload=sum(v['payload'] for v in states.values());slots=sum(v['recovery_slots'] for v in states.values())
    assert reserved<=8589934592 and slots<=6 and actual_retries<=slots
    body_files=list((P/'work/private/http_attempts').rglob('*.bin'))
    assert sum(f.stat().st_size for f in body_files)==payload
    recovered=False
    if (P/'results/RECOVERED_RANGE.json').exists():
        receipt=load(P/'results/RECOVERED_RANGE.json');policy=reg['recovery']
        prefix=(R/policy['prefix_path']).read_bytes()
        suffix=(P/'work/private/http_attempts'/str(policy['session_id'])/(f"{receipt['request']:05}.bin")).read_bytes()
        combined=(P/'work/private/ranges'/str(policy['session_id'])/(str(policy['old_offset'])+'.bin')).read_bytes()
        assert len(prefix)==540672 and len(suffix)==507904 and len(combined)==1048576
        assert hashlib.sha256(prefix).hexdigest()==policy['prefix_sha256']==receipt['prefix_sha256']
        assert receipt['suffix_offset']==448282624 and receipt['suffix_bytes']==507904
        assert hashlib.sha256(suffix).hexdigest()==receipt['suffix_sha256']
        assert combined==prefix+suffix and hashlib.sha256(combined).hexdigest()==receipt['sha256']
        recovered=True
    admitted=[x for x in complete if x['selection']['admitted']]
    bo=sum(x['source']['protocol']=='brain_observatory_1.1' for x in admitted)
    decision=None
    if (P/'results/M2_DECISION.json').exists():
        decision=load(P/'results/M2_DECISION.json');assert len(complete)==28 and not incomplete
        assert decision['admitted_mice']==len(admitted) and decision['admitted_BO']==bo and decision['admitted_FC']==len(admitted)-bo
        passed=len(admitted)>=14 and bo>=3 and len(admitted)-bo>=10
        assert decision['verdict']==('M2_SOURCE_AND_PHYSIOLOGY_PASS' if passed else 'DATA_INSUFFICIENT')
        assert not decision['model_fits_authorized'] and decision['model_fits']==0
    freeze_count=0
    for manifest_name in ['PREACCESS_FREEZE_MANIFEST.json','FINAL_FREEZE_MANIFEST.json']:
        manifest=P/manifest_name
        if manifest.exists():
            rows=load(manifest)['files']
            for row in rows:
                path=R/row['path']
                if row['path']=='ops/daily-operations.md':
                    assert path.read_bytes().endswith((E/'R3_DAILY_FROZEN_SNAPSHOT.bin').read_bytes())
                else:assert path.stat().st_size==row['bytes'] and sha(path)==row['sha256'],row['path']
            freeze_count+=len(rows)
    return {'R3_STOP_preserved':True,'R3_public_files_verified':373,'R3_private_files_verified':679,
        'R3_A_states_verified':228,'original_completed_sources_reused':3,'R4_sources_attempted':len(attempts),
        'R4_sources_complete':len(complete)-3,'total_complete_sources':len(complete),'incomplete_R4_sources':incomplete,
        'new_R4_A_states_replayed':new_A,'recovered_range_verified':recovered,'admitted_complete_sources':len(admitted),
        'admitted_BO':bo,'admitted_FC':len(admitted)-bo,'R4_new_payload_bytes':payload,'R4_reserved_bytes':reserved,
        'R4_transport_retries':actual_retries,'R4_timeout_recovery_slots':slots,'R4_source_requests':sum(v['requests'] for v in states.values()),
        'M2_verdict':None if decision is None else decision['verdict'],'frozen_payloads_verified':freeze_count,
        'new_HTTP_requests_by_replay':0,'MODEL_FITS_EXECUTED':0,'B_E_NEURAL_SCIENTIFIC_ACCESS':False,
        'FINAL_C_ACCESS':False,'FINAL_D_ACCESS':False,'runtime':runtime,'public_clone_without_private_raw_cannot_replay_QC':True}


if __name__=='__main__':
    with patch('socket.socket.connect',side_effect=RuntimeError('Saved-only audit: no source network')):
        print(json.dumps(verify_saved(),sort_keys=True,allow_nan=False))
