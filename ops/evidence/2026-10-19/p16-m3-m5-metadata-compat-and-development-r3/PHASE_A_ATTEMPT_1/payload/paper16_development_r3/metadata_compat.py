"""Metadata-only source-backed compatibility; never imports a neural worker."""
import gzip,socket
from unittest.mock import patch
import numpy as np
from .identity import *
verify_pins()
from paper16_m1.code.roster_metadata import invalid_rows

def array_identity(a):
    a=np.asarray(a);return {'shape':list(a.shape),'dtype':a.dtype.str,'sha256':hashlib.sha256(a.tobytes()).hexdigest()}

def intervals(values,label):
    a=np.asarray(values)
    if a.dtype.kind not in 'fiu' or not np.isfinite(a).all():raise ProvenanceStop('Invalid numeric interval '+label)
    if a.size==0:
        if a.shape not in [(0,),(0,2)]:raise ProvenanceStop('Empty interval geometry '+label)
        return np.empty((0,2),dtype=np.float64)
    if a.ndim!=2 or a.shape[1]!=2 or np.any(a[:,1]<=a[:,0]):raise ProvenanceStop('Invalid interval geometry '+label)
    return a.astype(np.float64,copy=False)

def labeled_invalidity(header,item,probes):
    if header.get('error') or header.get('session_id')!=item['session_id'] or header.get('decoded_neural_values') is not False:raise ProvenanceStop('Incomplete/wrong frozen native header')
    names=header.get('all_interval_names')
    if not isinstance(names,list) or not all(isinstance(x,str) for x in names) or len(set(names))!=len(names):raise ProvenanceStop('Complete native interval inventory required')
    tables=header.get('tables')
    if not isinstance(tables,dict):raise ProvenanceStop('Native table provenance missing')
    present='invalid_times' in names
    if present!=('invalid_times' in tables):raise ProvenanceStop('Invalid table inventory/values disagree')
    if not present:
        return np.empty((0,2)),np.empty((0,2)),{'status':'VERIFIED_ABSENT_FROM_FULL_NATIVE_INTERVAL_INVENTORY','native_interval_names':names,'rows':[],'original_numeric_HDF5_dtype':'NO_INTERVAL_DATASET_PRESENT'}
    inv=tables['invalid_times'];required=['start_time','stop_time','tags','tags_index']
    if not isinstance(inv,dict) or any(k not in inv or not isinstance(inv[k],list) for k in required):raise ProvenanceStop('Incomplete native invalid table')
    if not all(isinstance(x,str) for x in inv['tags']):raise ProvenanceStop('Native tags must be decoded source strings')
    for key in ['start_time','stop_time']:
        if not all(type(v) in [float,int] and np.isfinite(v) for v in inv[key]):raise ProvenanceStop('Native numeric boundary integrity')
    try:app,stim=invalid_rows(inv['start_time'],inv['stop_time'],inv['tags'],inv['tags_index'],item,probes,return_labels=True)
    except (ValueError,TypeError,OverflowError) as exc:raise ProvenanceStop('Frozen M1 invalid tag/scope rule: '+str(exc)) from exc
    prior=0;rows=[]
    for a,b,right in zip(inv['start_time'],inv['stop_time'],inv['tags_index']):
        tags=inv['tags'][prior:right];prior=right;scope,scope_id,label=tags
        applies=scope=='EcephysSession' or int(scope_id)==item['probe_id']
        rows.append({'start':a,'stop':b,'tags':tags,'applies_to_selected_probe':applies,'stimulus_only':scope=='EcephysSession' and label=='stimulus'})
    return intervals(np.asarray(app,dtype=np.float64).reshape(-1,2),'reconstructed applicable'),intervals(np.asarray(stim,dtype=np.float64).reshape(-1,2),'reconstructed stimulus'),{'status':'COMPLETE_FROZEN_LABELED_NATIVE_TABLE','native_interval_names':names,'rows':rows,'original_numeric_HDF5_dtype':'Numeric f/i/u verified by frozen native_headers.validate_type; exact HDF5 width not serialized in JSON and not asserted','JSON_numeric_to_float64':'Original frozen invalid_rows conversion, not added source precision'}

def validate_arrays(arrays):
    required={'start','stop','id','color','ordinal','main_valid','invalid_intervals'}
    if not required<=set(arrays) or set(arrays)-required-{'stimulus_invalid_intervals'}:raise ProvenanceStop('Unexpected saved metadata schema')
    a,b,ids,c,ordinal,valid=(arrays[k] for k in ['start','stop','id','color','ordinal','main_valid'])
    if a.dtype!=np.dtype('float64') or b.dtype!=np.dtype('float64') or c.dtype!=np.dtype('float64') or valid.dtype!=np.dtype('bool'):raise ProvenanceStop('Original metadata dtype mismatch')
    if any(x.shape!=(150,) for x in [a,b,ids,c,ordinal,valid]) or ids.dtype.kind not in 'iu' or ordinal.dtype.kind not in 'iu':raise ProvenanceStop('Original metadata geometry')
    if not np.isfinite(a).all() or not np.isfinite(b).all() or not np.all(np.diff(a)>0) or len(set(ids.tolist()))!=150 or not np.array_equal(ordinal,np.arange(150)):raise ProvenanceStop('Original event/ordinal integrity')
    if not np.isin(c,[-1,1]).all() or np.any(b<=a):raise ProvenanceStop('Original condition/timing integrity')
    for key in ['invalid_intervals','stimulus_invalid_intervals']:
        if key in arrays:
            if arrays[key].dtype!=np.dtype('float64'):raise ProvenanceStop('Saved interval dtype: '+key)
            intervals(arrays[key],key)

def read_archive(path,digest):
    check(path,digest)
    try:
        with np.load(path,allow_pickle=False) as z:
            names=set(z.files)
            if not {'start','stop','id','color','ordinal','main_valid','invalid_intervals'}<=names or names-{'start','stop','id','color','ordinal','main_valid','invalid_intervals','stimulus_invalid_intervals'}:raise ProvenanceStop('Unregistered metadata archive member')
            arrays={k:z[k].copy() for k in z.files}
        validate_arrays(arrays);return arrays
    except (ValueError,EOFError,OSError) as exc:raise ProvenanceStop('Corrupt saved metadata archive: '+str(exc)) from exc

def derive(header,item,probes,arrays,common_mask):
    validate_arrays(arrays)
    app,stim,labels=labeled_invalidity(header,item,probes)
    if not np.array_equal(app,intervals(arrays['invalid_intervals'],'saved applicable')):raise ContractStop('Reconstructed applicable intervals differ from frozen invalid_intervals')
    if 'stimulus_invalid_intervals' in arrays and not np.array_equal(stim,intervals(arrays['stimulus_invalid_intervals'],'saved stimulus')):raise ContractStop('Existing explicit stimulus field disagrees')
    a,b,c=(arrays[k] for k in ['start','stop','color'])
    # Literal original M1 roster_metadata.evaluate support formula, without
    # substituting support validity for stimulus validity.
    complete=(b>=a+.22)&np.array([not any(l<t+.22 and t<r for l,r in app) and not any(l<end and t<r for l,r in stim) for t,end in zip(a,b)])
    if not np.array_equal(complete,arrays['main_valid']):raise ContractStop('Reconstructed complete validity differs from frozen main_valid')
    common=np.asarray(common_mask)
    if common.dtype!=np.dtype('bool') or common.shape!=(150,) or np.any(common&~complete):raise ContractStop('Original admitted common mask not preserved')
    stimulus=np.isfinite(a)&np.isfinite(b)&(b>a)&np.isin(c,[-1,1])&np.array([not np.any((stim[:,0]<end)&(t<stim[:,1])) for t,end in zip(a,b)])
    coverage={}
    for role,lo,hi,floor in [('A',0,90,30),('B',90,120,8),('E',120,150,8)]:
        counts={str(color):int(np.count_nonzero(common[lo:hi]&(c[lo:hi]==color))) for color in [-1,1]}
        if min(counts.values())<floor:raise ContractStop('Frozen admitted coverage mismatch')
        coverage[role]={'original_ordinal_bounds':[lo,hi],'color_counts':counts,'minimum_per_color':floor}
    return {'applicable_invalid_intervals':app.tolist(),'stimulus_invalid_intervals':stim.tolist(),'reconstructed_interval_dtype':app.dtype.str,
        'native_label_provenance':labels,'original_main_valid':arrays['main_valid'].tolist(),'complete_validity_equal_original':True,
        'stimulus_valid':stimulus.tolist(),'original_admitted_common_mask':common.tolist(),'role_coverage':coverage,
        'saved_array_identities':{k:array_identity(v) for k,v in arrays.items()},'stimulus_field_already_present':'stimulus_invalid_intervals' in arrays,
        'neural_support_exclusions_not_used_as_stimulus_missing':True,'neural_features_constructed':False,'source_precision_amended':False}

def read_input(record):
    exact_record(record);verify_pins();item=record['source'];sid=item['session_id']
    for key in ['result','QC']:check(R/record[key]['path'],record[key]['sha256'])
    frozen=load(R/record['result']['path']);pins=frozen['source_metadata_pins'];mpath=R/pins['metadata_path'];npath=mpath.with_suffix('.npz')
    check(mpath,pins['metadata_sha256']);check(npath,pins['flash_array_sha256']);metadata=load(mpath)
    for key in ['mouse_id','session_id','probe_id','protocol','role','file_id','etag','size']:
        if metadata.get(key)!=item[key]:raise ProvenanceStop('Frozen metadata source identity: '+key)
    if metadata.get('status')!='COMPLETE' or not metadata.get('clock_matches_original_source_metadata') or metadata.get('source_nwb_version')!='2.2.2':raise ProvenanceStop('Original source timing admission')
    hpath=R/'paper12_native_support1/metadata/native_headers'/f'{sid}.json.gz';check(hpath,metadata['source_header_sha256'])
    header=json.loads(gzip.decompress(hpath.read_bytes()))
    if header.get('root_attributes',{}).get('nwb_version')!='2.2.2' or any(not isinstance(header.get(k),str) or not header[k] for k in ['/session_start_time','/timestamps_reference_time']):raise ProvenanceStop('Frozen clock/root identity')
    probes=[p for p in load(R/'paper16_m0/metadata/probes.body')['msg'] if int(p['ecephys_session_id'])==sid]
    selected=[p for p in probes if int(p['id'])==item['probe_id'] and p['name']==item['source_probe_name']]
    if len(selected)!=1:raise ProvenanceStop('Source selected-probe identity')
    for root in ['/general/devices/','/general/extracellular_ephys/']:
        observed=header.get('probe_metadata',{}).get(root+item['source_probe_name'],{}).get('attributes',{})
        if observed.get('probe_id')!=str(item['probe_id']):raise ProvenanceStop('Native probe identity')
    arrays=read_archive(npath,pins['flash_array_sha256'])
    provenance={'source':item,'frozen_metadata_json':{'path':mpath.relative_to(R).as_posix(),'sha256':sha(mpath)},
        'frozen_metadata_npz':{'path':npath.relative_to(R).as_posix(),'sha256':sha(npath)},'native_header':{'path':hpath.relative_to(R).as_posix(),'sha256':sha(hpath)},
        'probe_catalog_sha256':sha(R/'paper16_m0/metadata/probes.body'),'frozen_parser_sha256':sha(R/'paper16_m1/code/roster_metadata.py'),
        'native_header_producer_sha256':sha(R/'paper12_native_support1/native_headers.py'),'root_attributes':header['root_attributes'],
        'relative_clock_reference':header['/timestamps_reference_time'],'archive_members':list(arrays)}
    return header,item,probes,arrays,record['selection']['common_mask'],provenance

def run():
    verify_pins()
    for row in load(P/'PHASE_A_IMPLEMENTATION_MANIFEST.json')['files']:
        check(R/row['path'],row['sha256'])
    once(P/'results/PHASE_A_ATTEMPT.json',{'mission':MISSION,'phase':'METADATA_ONLY','scientific_stage_consumed':False})
    try:
        inputs=[];schema=[]
        for record in records():
            data=read_input(record);inputs.append(data);schema.append({'source':data[1],'archive_members':list(data[3]),'stimulus_field_present':'stimulus_invalid_intervals' in data[3],'array_identities':{k:array_identity(v) for k,v in data[3].items()},'provenance':data[5]})
        if len(schema)!=27 or sum(x['stimulus_field_present'] for x in schema)!=3:raise ContractStop('Historical 24/3 archive schema denominator changed')
        once(P/'SCHEMA_AUDIT.json',{'sources':schema,'actual_inputs':27,'field_present':3,'field_missing':24,'new_neural_access':False})
        receipts=[]
        for header,item,probes,arrays,common,provenance in inputs:
            result=derive(header,item,probes,arrays,common);path=P/'metadata_compat'/f"{item['session_id']}.json"
            once(path,{'mission':MISSION,**provenance,**result});receipts.append({'mouse_id':item['mouse_id'],'session_id':item['session_id'],'path':path.relative_to(R).as_posix(),'sha256':sha(path)})
        once(P/'PHASE_A_RESULTS.json',{'actual_schemas_audited':27,'compatible_representations':27,'source_provenance_verified':27,'existing_explicit_field_agreement':3,'additive_missing_field_reconstruction':24,'files':receipts,'frozen_masks_redefined':False,'neural_features_constructed':False,'model_fits':0,'scientific_stage_consumed':False,'B_E_neural_access':False,'Final_C_D_access':False,'independent_review_required':True})
        print(json.dumps({'metadata_preflight_sources':27,'representations':27,'scientific_stage_consumed':False}))
    except BaseException as exc:
        once(P/'results/PHASE_A_STOP.json',{'scientific_verdict':'STOP_METADATA_CONTRACT_MISMATCH' if isinstance(exc,ContractStop) else 'STOP_METADATA_PROVENANCE_UNRESOLVED','type':type(exc).__name__,'message':str(exc),'later_phases_not_executed':True,'scientific_stage_consumed':False});raise

if __name__=='__main__':
    with patch.object(socket.socket,'connect',side_effect=RuntimeError('Phase A metadata-only forbids network')):run()
