"""Signed, artifact-bound native ledger controller; no keys or neural decoder."""
import ctypes as c
from ctypes import wintypes as w
import hashlib
import json
import os
from pathlib import Path
from contextlib import contextmanager
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def digest(value):return hashlib.sha256(value).hexdigest()
def pairs(items):
    result={}
    for key,value in items:
        if key in result:raise ValueError('DUPLICATE_JSON_KEY')
        result[key]=value
    return result
def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'),object_pairs_hook=pairs,parse_constant=lambda x:(_ for _ in ()).throw(ValueError('NONFINITE_JSON')))
def safe(root,path):
    root=Path(root).resolve();path=Path(path).absolute()
    if not path.is_relative_to(root) or '..' in path.parts:raise PermissionError('PATH_ESCAPE')
    for p in [path]+list(path.parents):
        if p.exists():
            st=p.lstat()
            if getattr(st,'st_file_attributes',0)&0x400 or p.is_symlink() or (p.is_file() and st.st_nlink!=1):raise PermissionError('LINK_SUBSTITUTION')
        if p==root:break
    if not path.resolve().is_relative_to(root):raise PermissionError('CANONICAL_ESCAPE')
    return path
def package_sid():
    adv=c.WinDLL('advapi32',use_last_error=True);k=c.WinDLL('kernel32',use_last_error=True)
    k.GetCurrentProcess.restype=w.HANDLE
    adv.OpenProcessToken.argtypes=[w.HANDLE,w.DWORD,c.POINTER(w.HANDLE)]
    adv.GetTokenInformation.argtypes=[w.HANDLE,c.c_int,c.c_void_p,w.DWORD,c.POINTER(w.DWORD)]
    token=w.HANDLE();size=w.DWORD()
    if not adv.OpenProcessToken(k.GetCurrentProcess(),8,c.byref(token)):raise PermissionError('TOKEN_QUERY')
    try:
        flag=w.DWORD()
        if not adv.GetTokenInformation(token,29,c.byref(flag),4,c.byref(size)) or not flag.value:raise PermissionError('CONTROLLER_APPCONTAINER_REQUIRED')
        adv.GetTokenInformation(token,30,None,0,c.byref(size));caps=c.create_string_buffer(size.value)
        if not adv.GetTokenInformation(token,30,caps,size.value,c.byref(size)) or c.cast(caps,c.POINTER(w.DWORD)).contents.value!=0:raise PermissionError('ZERO_CAPABILITIES_REQUIRED')
        adv.GetTokenInformation(token,31,None,0,c.byref(size));sid=c.create_string_buffer(size.value)
        if not adv.GetTokenInformation(token,31,sid,size.value,c.byref(size)):raise PermissionError('PACKAGE_QUERY')
        adv.ConvertSidToStringSidW.argtypes=[c.c_void_p,c.POINTER(w.LPWSTR)];value=w.LPWSTR()
        if not adv.ConvertSidToStringSidW(c.cast(sid,c.POINTER(c.c_void_p)).contents.value,c.byref(value)):raise PermissionError('PACKAGE_STRING')
        try:return value.value
        finally:k.LocalFree.argtypes=[c.c_void_p];k.LocalFree(c.cast(value,c.c_void_p))
    finally:k.CloseHandle.argtypes=[w.HANDLE];k.CloseHandle(token)

@contextmanager
def exclusive(path):
    # Share mode zero serializes across processes and threads; kernel releases lock on crash.
    k=c.WinDLL('kernel32',use_last_error=True)
    k.CreateFileW.argtypes=[w.LPCWSTR,w.DWORD,w.DWORD,c.c_void_p,w.DWORD,w.DWORD,w.HANDLE];k.CreateFileW.restype=w.HANDLE
    h=k.CreateFileW(str(path),0xC0000000,0,None,3,0x80000000,None)
    if h==w.HANDLE(-1).value:raise PermissionError('CONTROLLER_BUSY_OR_LOCK_MISSING')
    try:yield
    finally:k.CloseHandle.argtypes=[w.HANDLE];k.CloseHandle(h)

def durable_new(path,value):
    with Path(path).open('xb') as f:f.write(canonical(value)+b'\n');f.flush();os.fsync(f.fileno())

FIELDS={'version','realm','mission','base','authorization_id','cohort','protocol_sha256','partition_sha256','C_manifest_sha256','analysis_spec_sha256','principal','artifacts','reviews'}
def verify_approval(approval,anchor,binding_root):
    if set(approval)!={'body','signature'}:raise PermissionError('APPROVAL_SCHEMA')
    body=approval['body']
    if set(body)!=FIELDS or body['version']!=1:raise PermissionError('BINDING_SCHEMA')
    if body['realm']!=anchor['realm'] or body['mission']!=anchor['mission'] or body['base']!=anchor['base']:raise PermissionError('REALM_MISSION_BASE')
    ident=body['authorization_id']
    if not isinstance(ident,str) or len(ident)!=32 or any(x not in '0123456789abcdef' for x in ident):raise PermissionError('AUTHORIZATION_ID')
    Ed25519PublicKey.from_public_bytes(bytes.fromhex(anchor['authority_public'])).verify(bytes.fromhex(approval['signature']),canonical(body))
    if len(body['cohort'])!=13 or len(set(body['cohort']))!=13 or body['cohort']!=anchor['cohort']:raise PermissionError('COHORT')
    if body['principal']!=anchor['principal'] or not body['principal']['package_sid'].startswith('S-1-15-2-') or not body['principal']['creation_identity']:raise PermissionError('APPROVED_PRINCIPAL')
    if set(body['artifacts'])!=set(anchor['artifacts']) or body['artifacts']!=anchor['artifacts']:raise PermissionError('ARTIFACT_ROSTER')
    for name,value in body['artifacts'].items():
        p=safe(binding_root,Path(binding_root)/name)
        if not p.is_file() or digest(p.read_bytes())!=value:raise PermissionError('ARTIFACT_DRIFT')
    for key in ('protocol_sha256','partition_sha256','C_manifest_sha256','analysis_spec_sha256','reviews'):
        if body[key]!=anchor[key]:raise PermissionError('FROZEN_BINDING_DRIFT')
    if set(body['reviews'])!={'engineering','scientific'} or any(v not in body['artifacts'].values() for v in body['reviews'].values()):raise PermissionError('INDEPENDENT_REVIEW_BINDING')
    if body['realm']=='REAL_D':
        validate_real_bindings(body,binding_root)
    manifest=read_json(Path(binding_root)/anchor['C_manifest_file'])
    if digest(canonical(manifest))!=body['C_manifest_sha256']:raise PermissionError('C_MANIFEST_BINDING')
    check_C_realm(body['realm'],manifest)
    if manifest['cohort']!=body['cohort']:raise PermissionError('C_MANIFEST_COHORT')
    validate_state_manifest(manifest,binding_root)
    return body

def check_C_realm(realm,manifest):
    if (realm=='REAL_D' and manifest.get('synthetic') is not False) or (realm=='SYNTHETIC_D' and manifest.get('synthetic') is not True):raise PermissionError('C_CALIBRATION_REALM_MISMATCH')

def validate_real_bindings(body,binding_root):
    # Future REAL activation needs a separately approved signature/key/root, never engineering flags.
    root=Path(binding_root)
    required={'animals.json','trials.json','final_D_partition_manifest.json','final_human_authorization.json','analysis_spec.json'}
    if not required<=set(body['artifacts']):raise PermissionError('REAL_RELEASE_EVIDENCE_REQUIRED')
    animals=read_json(root/'animals.json');trials=read_json(root/'trials.json')
    expected=[a for a in animals if a['group']=='final']
    if len(animals)!=26 or len(expected)!=13 or body['cohort']!=[a['mouse_id'] for a in expected]:raise PermissionError('ORIGINAL_FINAL_COHORT_REQUIRED')
    partition=read_json(root/'final_D_partition_manifest.json')
    if digest((root/'final_D_partition_manifest.json').read_bytes())!=body['partition_sha256']:raise PermissionError('REAL_D_PARTITION_HASH')
    wanted={a['mouse_id']:[t['trial_id'] for t in trials if t['session_id']==a['session_id'] and t['partition']=='locked_evaluation' and t['metadata_admitted']] for a in expected}
    if partition.get('D_trial_ids')!=wanted:raise PermissionError('ORIGINAL_D_TRIAL_ASSIGNMENTS_REQUIRED')
    human=read_json(root/'final_human_authorization.json')
    if human.get('scope')!='ONE_FINAL_D_ASSESSMENT' or human.get('authorization_id')!=body['authorization_id'] or human.get('realm')!='REAL_D' or human.get('C_manifest_sha256')!=body['C_manifest_sha256']:raise PermissionError('SEPARATE_HUMAN_D_AUTHORIZATION_REQUIRED')
    spec=read_json(root/'analysis_spec.json')
    if spec.get('hypotheses')!=['own','population','stimulus_time','combined'] or spec.get('Holm')!=4 or spec.get('bootstrap')!=10000 or spec.get('controls')!=4 or spec.get('replicates')!=999 or spec.get('one_assessment') is not True:raise PermissionError('FROZEN_FINAL_SPECIFICATION_REQUIRED')

def check_numerical_rows(cert,case,label):
    n=len(case['unit_ids']);reused=cert.get('reused') is True
    rows=cert.get('certificates' if reused else 'records')
    if cert.get('passed') is not True or not isinstance(rows,list) or len(rows)!=n:raise PermissionError('C_EXACT_UNIT_CERTIFICATES_REQUIRED')
    for u,v in enumerate(rows):
        if reused:
            if v.get('unit')!=u:raise PermissionError('C_REUSED_UNIT_ORDER')
        elif v.get('unit_id')!=case['unit_ids'][u] or v.get('optimizer_success') is not True or not v.get('finite') or not v.get('bounds') or not v.get('history') or v.get('iterations',101)>100 or v.get('objective_calls',4001)>4000:
            raise PermissionError('C_ORIGINAL_UNIT_SOLVER_RECORD_REQUIRED')
        pg=v.get('original_PG') if reused else v.get('original_definition_PG')
        adpg=v.get('AD_original_PG') if reused else v.get('AD_original_definition_PG')
        values=[pg,adpg,v.get('AD_scaled_error'),v.get('AD_objective_error')]
        import math
        if any(not isinstance(x,(int,float)) or not math.isfinite(x) or x<0 for x in values) or pg>.001 or adpg>.001 or values[2]>1e-5 or values[3]>1e-10 or v.get('passed') is not True:raise PermissionError('C_NUMERICAL_GATE')
    if reused and label not in ('O','N','NH'):raise PermissionError('C_UNREGISTERED_REUSE')
    return rows,reused

def validate_provenance(manifest,root):
    import zipfile
    if __package__:
        from .selection_dependency import load_views
        views=load_views()
    else:
        from selection import views
    root=Path(root)
    required={'input_manifest','metadata','calibration_states','role_proof','gate_result','extra_role_denials','protected_open_checks_without_reading','launch_receipt','roster','QC','identity'}
    if not {('provenance_'+n+'.json') for n in required}<=set(manifest['artifact_sha256']) or not {'attempt_journals.zip','attempt_journals_index.json'}<=set(manifest['artifact_sha256']):raise PermissionError('C_COMPLETE_PROVENANCE_REQUIRED')
    p={n:read_json(root/('provenance_'+n+'.json')) for n in required}
    inputs=p['input_manifest'];roster=p['roster'];report=p['calibration_states'];launch=p['launch_receipt']
    if inputs['synthetic'] is not manifest['synthetic'] or inputs['compartments']!=['C'] or inputs['group']!='final' or [s['mouse_id'] for s in inputs['sessions']]!=manifest['cohort']:raise PermissionError('C_INPUT_IDENTITY')
    if report['input_manifest_sha256']!=manifest['artifact_sha256']['provenance_input_manifest.json'] or report['metadata_sha256']!=manifest['artifact_sha256']['provenance_metadata.json'] or report['state_sha256']!=manifest['artifact_sha256']['complete_states.npz'] or not report['complete'] or not report['C_only'] or report['D_loaded']:raise PermissionError('C_REPORT_PROVENANCE')
    if launch['exit_code']!=0 or launch['timed_out'] or not launch['role_proof_pass'] or launch['profile_cleanup_hresult']!='0x00000000' or launch['D_RELEASE_CONSUMED'] or launch['D_EVALUATION_EXECUTED'] or not p['role_proof']['pass'] or p['gate_result']['gate']!='PASS':raise PermissionError('C_ACTUAL_NATIVE_LAUNCH_REQUIRED')
    if not all(p['extra_role_denials'].values()) or not all(p['protected_open_checks_without_reading'].values()):raise PermissionError('C_ROLE_DENIAL_EVIDENCE')
    mode=roster['registration']
    if mode not in ('PROSPECTIVE_BEFORE_ANY_OPTIMIZER','RETROSPECTIVE_SAVED_SYNTHETIC') or (not manifest['synthetic'] and mode!='PROSPECTIVE_BEFORE_ANY_OPTIMIZER'):raise PermissionError('C_PROSPECTIVE_ROSTER_REQUIRED')
    if not manifest['synthetic']:
        if not inputs.get('C_approval_sha256') or not inputs.get('QC_attestation_sha256') or inputs['QC_attestation_sha256']!=manifest['artifact_sha256']['provenance_QC.json'] or p['identity']['C_approval_sha256']!=inputs['C_approval_sha256']:raise PermissionError('C_REAL_QC_APPROVAL_BINDING')
        if len(p['QC'])!=26 or any(not q['all_selected_C_QC_passed'] or not q['ISI_from_frozen_C_timestamp_QC'] for q in p['QC']):raise PermissionError('C_REAL_QC_COVERAGE')
    if not p['identity']['runtime_sha256'] or not p['identity']['source_code_sha256'] or not p['identity']['frozen_source_sha256'] or not p['identity']['checkpoint_sha256']:raise PermissionError('C_SOURCE_RUNTIME_IDENTITY')
    md={(m['session_id'],m['unit_id']):m for m in p['metadata']};expected=[];counts={v:0 for v in manifest['coverage']}
    if len(roster['sessions'])!=13 or [s['mouse_id'] for s in roster['sessions']]!=manifest['cohort']:raise PermissionError('C_ROSTER_COHORT')
    reports={c['case']:c for c in report['cases']}
    for item,s in zip(roster['sessions'],inputs['sessions']):
        if item['session_id']!=s['session_id'] or item['unit_ids']!=s['unit_ids'] or item['trial_ids_C']!=s['trial_ids']['C']:raise PermissionError('C_ROSTER_INPUT_MISMATCH')
        metadata={k:[md[(s['session_id'],uid)] for uid in s['unit_ids'][k]] for k in ('CA1','DG')}
        if metadata!=item['metadata']:raise PermissionError('C_SELECTION_METADATA_MISMATCH')
        vv=views(item['rates_C_Hz']['CA1'],item['rates_C_Hz']['DG'],metadata);vv={k:v for k,v in vv.items() if min(map(len,v.values()))>=5}
        if vv!=item['views']:raise PermissionError('C_INDEPENDENT_SELECTION_ROSTER')
        for view,selection in vv.items():
            if view in counts:counts[view]+=1
            for region in ('CA1','DG'):
                expected.append([s['mouse_id'],region,view]);case=next((c for c in manifest['cases'] if [c['mouse_id'],c['region'],c['view']]==expected[-1]),None)
                if case is None or case['session_id']!=s['session_id'] or case['selection']!=selection[region] or case['unit_ids']!=[s['unit_ids'][region][i] for i in selection[region]] or case['trial_ids']!=s['trial_ids']['C']:raise PermissionError('C_CASE_PREFIT_ROSTER_MISMATCH')
                old=reports.get(case['case'])
                if old is None or old['selection']!=case['selection'] or old['unit_ids']!=case['unit_ids']:raise PermissionError('C_SEALED_REPORT_CASE_MISMATCH')
    if sorted(expected)!=sorted(manifest['expected_cases']) or counts!=manifest['coverage'] or counts!=roster['paired_counts'] or counts!=report['paired_counts']:raise PermissionError('C_PREFIT_DENOMINATOR_MISMATCH')
    index=read_json(root/'attempt_journals_index.json')
    with zipfile.ZipFile(root/'attempt_journals.zip') as archive:
        if len(archive.namelist())!=len(index) or set(archive.namelist())!=set(index):raise PermissionError('C_ATTEMPT_JOURNAL_ROSTER')
        for name,h in index.items():
            if Path(name).name!=name or digest(archive.read(name))!=h:raise PermissionError('C_ATTEMPT_JOURNAL_INTEGRITY')
        attempts=0
        for case in manifest['cases']:
            for label in case['models']:
                name=case['case']+'_'+label+'.json';cert=read_json(root/name);rows,reused=check_numerical_rows(cert,case,label)
                if digest(archive.read(name))!=manifest['artifact_sha256'][name]:raise PermissionError('C_CERTIFICATE_JOURNAL_MISMATCH')
                if reused:continue
                for u,row in enumerate(rows):
                    tag=case['case']+'_'+label+'_unit'+str(u)
                    saved=json.loads(archive.read(tag+'.json'));started=json.loads(archive.read(tag+'_started.json'))
                    if saved!=row or started['unit_id']!=row['unit_id'] or started['attempt']!=row['attempt']:raise PermissionError('C_ORIGINAL_ATTEMPT_TRACE')
                    attempts+=1
        if attempts!=report['new_GLM_unit_attempts']:raise PermissionError('C_ALL_ATTEMPTS_REQUIRED')
    return True

def validate_state_manifest(manifest,bundle_root=None):
    if set(manifest)!= {'version','cohort','cases','expected_cases','seed_certificates','coverage','artifact_sha256','synthetic'} or manifest['version']!=2:raise PermissionError('COMPLETE_C_SCHEMA')
    if len(manifest['cohort'])!=13 or len(set(manifest['cohort']))!=13:raise PermissionError('COMPLETE_C_COHORT')
    for v in ('primary','matched16','rate_matched','boundary20','boundary40'):
        if manifest['coverage'].get(v,0)<8:raise PermissionError('COMPLETE_C_COVERAGE')
    seen=set()
    for case in manifest['cases']:
        key=(case['mouse_id'],case['region'],case['view'])
        if key in seen or key[0] not in manifest['cohort'] or key[1] not in ('CA1','DG'):raise PermissionError('COMPLETE_C_IDENTITY')
        seen.add(key);n=len(case['unit_ids'])
        if n<5 or len(set(case['unit_ids']))!=n or not case['trial_mask_sha256'] or not case['scaler_sha256']:raise PermissionError('COMPLETE_C_PREPROCESSING')
        if set(case['models'])!={'O','N','NH','NP','F','OHP'}:raise PermissionError('COMPLETE_C_MODELS')
        if any(z.get('shape')!=[n,39] or not z.get('sha256') or not z.get('certificate_sha256') for z in case['models'].values()):raise PermissionError('COMPLETE_C_MODEL_SHAPE')
    if sorted([list(x) for x in seen])!=sorted(manifest['expected_cases']):raise PermissionError('COMPLETE_C_CASE_ROSTER')
    for view in ('primary','matched16','rate_matched','boundary20','boundary40'):
        n=sum(all((m,r,view) in seen for r in ('CA1','DG')) for m in manifest['cohort'])
        if n<8 or n!=manifest['coverage'][view]:raise PermissionError('COMPLETE_C_ACTUAL_COVERAGE')
    for mouse in manifest['cohort']:
        for region in ('CA1','DG'):
            for view,n in (('primary',32),('matched16',16)):
                case=next((z for z in manifest['cases'] if (z['mouse_id'],z['region'],z['view'])==(mouse,region,view)),None)
                if case is None or len(case['unit_ids'])!=n:raise PermissionError('COMPLETE_C_REQUIRED_VIEW')
            for seed in ('11','23','37','mean'):
                cert=manifest['seed_certificates'].get(mouse+'_'+region+'_'+seed)
                if cert is None or not cert['sha256'] or cert['original_PG']>.001 or cert['AD_error']>1e-5:raise PermissionError('COMPLETE_C_N_SEEDS')
    if bundle_root is not None:
        import numpy as np
        for name,value in manifest['artifact_sha256'].items():
            if digest(safe(bundle_root,Path(bundle_root)/name).read_bytes())!=value:raise PermissionError('C_ARTIFACT_HASH')
        validate_provenance(manifest,bundle_root)
        with np.load(safe(bundle_root,Path(bundle_root)/'complete_states.npz'),allow_pickle=False) as arrays:
            for key,record in manifest['seed_certificates'].items():
                name=record['file']
                if manifest['artifact_sha256'].get(name)!=record['sha256']:raise PermissionError('C_N_CERTIFICATE_ARTIFACT')
                cert=read_json(Path(bundle_root)/name)
                if cert.get('passed') is not True or cert['original_PG']>.001 or cert['AD_original_PG']>.001 or cert['AD_scaled_error']>1e-5 or cert['AD_objective_error']>1e-10:raise PermissionError('C_N_ACTUAL_CERTIFICATE')
                if not key.endswith('_mean') and cert.get('optimizer_success') is not True:raise PermissionError('C_N_SOLVER_FAILURE')
                a=arrays[record['array_key']]
                shape=(32,39) if key.endswith('_mean') else (32,29)
                if a.shape!=shape or not np.isfinite(a).all() or np.any(np.abs(a)>8) or digest(np.ascontiguousarray(a).tobytes())!=record['array_sha256']:raise PermissionError('C_N_SEED_ARRAY_IDENTITY')
            for case in manifest['cases']:
                for label,z in case['models'].items():
                    if z['key'] not in arrays.files:raise PermissionError('C_ARRAY_MISSING')
                    a=arrays[z['key']]
                    if list(a.shape)!=z['shape'] or digest(np.ascontiguousarray(a).tobytes())!=z['sha256'] or not np.isfinite(a).all() or np.any(np.abs(a)>8):raise PermissionError('C_ARRAY_INVALID')
                    certificate_path=Path(bundle_root)/(case['case']+'_'+label+'.json')
                    if digest(certificate_path.read_bytes())!=z['certificate_sha256']:raise PermissionError('C_CERTIFICATE_HASH')
                    cert=read_json(certificate_path)
                    rows,reused=check_numerical_rows(cert,case,label)
                    if reused:
                        parent=next(c for c in manifest['cases'] if c['mouse_id']==case['mouse_id'] and c['region']==case['region'] and c['view']=='primary')
                        if not np.array_equal(a,arrays[parent['models'][label]['key']][case['selection']]):raise PermissionError('C_REUSE_COEFFICIENT_TRACE')
                        if label!='N':
                            parent_cert=read_json(Path(bundle_root)/(parent['case']+'_'+label+'.json'));original,_=check_numerical_rows(parent_cert,parent,label)
                            if parent_cert.get('reused'):raise PermissionError('C_REUSE_ORIGINAL_SOLVER_REQUIRED')
                            for u,index in enumerate(case['selection']):
                                if original[index]['unit_id']!=case['unit_ids'][u]:raise PermissionError('C_REUSE_SOLVER_UNIT_TRACE')
                m=arrays[case['mean_key']];s=arrays[case['scale_key']]
                if m.shape!=(len(case['unit_ids']),39) or s.shape!=m.shape or not np.isfinite(m).all() or not np.isfinite(s).all() or np.any(s<=0) or digest(np.ascontiguousarray(m).tobytes()+np.ascontiguousarray(s).tobytes())!=case['scaler_sha256']:raise PermissionError('C_SCALER_INVALID')
                if digest(canonical(case['trial_ids']))!=case['trial_mask_sha256']:raise PermissionError('C_MASK_INVALID')
                if case['view']=='primary':
                    prefix=case['case'][:-len('_primary')]
                    ws=[arrays[prefix+'_N_seed'+str(seed)] for seed in (11,23,37)]
                    if any(a.shape!=(32,29) for a in ws) or not np.array_equal(np.mean(ws,axis=0),arrays[case['models']['N']['key']][:,:29]):raise PermissionError('C_N_MEAN_STATE')
    return True

class Controller:
    def __init__(self,root,anchor_path,binding_root):
        self.root=Path(root);self.anchor_path=Path(anchor_path);self.binding_root=Path(binding_root)
    def consume(self,approval_path,hook=lambda point:None):
        anchor=read_json(self.anchor_path)
        if package_sid()!=anchor['controller_sid']:raise PermissionError('ACTUAL_CONTROLLER_PRINCIPAL')
        if anchor['realm'] not in ('SYNTHETIC_D','REAL_D'):raise PermissionError('REGISTERED_REALM')
        for p in (self.root,self.anchor_path,self.binding_root):safe(p if p.is_dir() else p.parent,p)
        # Anchor resides outside ledger write grant. No bootstrap or reset API exists here.
        if self.anchor_path.is_relative_to(self.root):raise PermissionError('ANCHOR_MUST_BE_INDEPENDENT')
        approval=read_json(approval_path);body=verify_approval(approval,anchor,self.binding_root);ident=body['authorization_id'];bound=digest(canonical(body))
        with exclusive(safe(self.root,self.root/'writer.lock')):
            verify_approval(approval,anchor,self.binding_root)
            genesis=read_json(safe(self.root,self.root/'genesis.json'))
            if digest(canonical(genesis))!=anchor['genesis_sha256']:raise PermissionError('GENESIS_MISMATCH')
            log=safe(self.root,self.root/'events.jsonl');raw=log.read_bytes()
            if not raw.endswith(b'\n'):raise PermissionError('PARTIAL_LEDGER')
            events=[json.loads(line,object_pairs_hook=pairs) for line in raw.splitlines()];previous=anchor['genesis_sha256']
            if not events:raise PermissionError('LEDGER_MISSING_GENESIS_EVENT')
            for i,event in enumerate(events):
                if set(event)!={'sequence','previous','state','authorization_id','binding'} or event['sequence']!=i or event['previous']!=previous:raise PermissionError('LEDGER_CHAIN')
                previous=digest(canonical(event))
            if events[0]['state']!='GENESIS' or events[0]['binding']!=anchor['genesis_sha256']:raise PermissionError('LEDGER_GENESIS')
            # This ledger is bound to a single authorization; no ID/ledger switching.
            if body['authorization_id']!=anchor['authorization_id']:raise PermissionError('ISSUED_ENTITLEMENT')
            fence=safe(Path(anchor['fence_root']),Path(anchor['fence_root'])/(ident+'.json'))
            if Path(anchor['fence_root']).is_relative_to(self.root):raise PermissionError('INDEPENDENT_FENCE_REQUIRED')
            if len(events)!=1 or (self.root/'intent.json').exists() or (self.root/'consumed.json').exists() or fence.exists():raise PermissionError('ENTITLEMENT_USED_OR_INTERRUPTED')
            hook('before_intent')
            durable_new(fence,{'authorization_id':ident,'binding':bound,'genesis':anchor['genesis_sha256']})
            durable_new(self.root/'intent.json',{'authorization_id':ident,'binding':bound,'genesis':anchor['genesis_sha256']})
            hook('after_intent')
            for state in ('INTENT','CONSUMED'):
                event={'sequence':len(events),'previous':previous,'state':state,'authorization_id':ident,'binding':bound}
                with log.open('ab') as f:f.write(canonical(event)+b'\n');f.flush();os.fsync(f.fileno())
                events.append(event);previous=digest(canonical(event));hook('after_'+state.lower()+'_append')
            durable_new(self.root/'consumed.json',{'authorization_id':ident,'binding':bound,'ledger_tail':previous})
            hook('after_consumed')
            # Return only a consumed receipt. The controller has no D key or data capability.
            return {'authorization_id':ident,'binding':bound,'ledger_tail':previous,'principal':body['principal'],'realm':body['realm']}
