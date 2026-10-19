"""Exactly one new first running-only source attempt, then reviewed conditional27."""
from pathlib import Path
import datetime
import gzip
import hashlib
import io
import json
import os
import subprocess
import sys
import time
import h5py
import numpy as np
import requests
from paper16_m1.code.roster_metadata import invalid_rows
from .reader import native_running
from .precision import derive, array_identity, admission_possible

R=Path(__file__).resolve().parents[1]
P=R/'paper16_running_r2'
E=R/'ops/evidence/2026-10-19/p16-m2-running-precision-recovery-r2'
M1E=R/'ops/evidence/2026-10-18/p16-m1-visual-dynamics-protocol-freeze'


class ResourceStop(RuntimeError):pass
class CoverageStop(ValueError):pass


def read(path):return json.loads(Path(path).read_text(encoding='utf8'))
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def once(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x',encoding='utf8',newline='\n') as f:
        json.dump(value,f,indent=2,allow_nan=False);f.write('\n');f.flush();os.fsync(f.fileno())


def save_arrays(path,arrays):
    with Path(path).open('xb') as f:
        np.savez_compressed(f,**arrays);f.flush();os.fsync(f.fileno())
    return {'path':Path(path).relative_to(R).as_posix(),'sha256':sha(path),
            'arrays':{name:array_identity(a) for name,a in arrays.items()}}


def guard(deadline):
    if time.monotonic()>=deadline:raise ResourceStop('Original4h stage deadline reached')


def validate_source(item,reg):
    matches=[x for x in reg['objects'] if x['session_id']==item['session_id']]
    if (item['session_id'] in reg['denied_final_session_ids'] or len(matches)!=1 or item!=matches[0] or item['role']!='Development'):
        raise ValueError('Unregistered/altered/Final source denied before open')


def review_gate():
    reg=read(P/'ACCESS_REGISTRATION.json');approval=read(E/'PREACCESS_APPROVAL.json')
    required={'paper16_running_r2/'+x for x in ['PRECISION_CONTRACT_DECISION.md','ACCESS_REGISTRATION.json','precision.py','reader.py','run_sources.py','test_running.py','test_interface.py']}
    required.add('ops/evidence/2026-10-19/p16-m2-running-precision-recovery-r2/PRECISION_CONTRACT_REVIEW_2.md')
    if approval.get('decision')!='ACCEPTED_R2_RUNNING_ONLY_PREACCESS' or any(type(approval.get(k)) is not int or approval[k]!=0 for k in ['open_P0','open_P1']):
        raise ValueError('Independent preaccess gate absent/failed')
    if not required<=approval.get('reviewed_hashes',{}).keys():raise ValueError('Incomplete exact reader review')
    for name,digest in approval['reviewed_hashes'].items():
        path=(R/name).resolve();path.relative_to(R)
        if sha(path)!=digest:raise ValueError('Reviewed source identity changed: '+name)
    if sha(E/'PREACCESS_REVIEW.md')!=approval['report_sha256']:raise ValueError('Preaccess report identity')
    for name,digest in reg['old_pins'].items():
        if sha(R/name)!=digest:raise ValueError('Frozen scientific/history source changed')
    for manifest,count in [('paper16_m1/M1_FREEZE_MANIFEST.json',334),('paper16_dev/STOP_FREEZE_MANIFEST.json',58),('paper16_linkdiag_r1/DIAGNOSTIC_FREEZE_MANIFEST.json',100)]:
        rows=read(R/manifest)['files']
        if len(rows)!=count:raise ValueError('Historical denominator')
        for row in rows:
            path=R/row['path']
            if path.stat().st_size!=row['bytes'] or sha(path)!=row['sha256']:raise ValueError('Historical evidence hash')
    return reg


class BudgetJournal:
    def __init__(self,path,append=False):
        self.path=Path(path)
        old=[json.loads(x) for x in self.path.read_text(encoding='utf8').splitlines()] if append else []
        self.total_reserved=sum(x['reserved_bytes'] for x in old if x['event']=='RESERVED')
        self.file=self.path.open('a' if append else 'x',encoding='utf8',newline='\n')
    def emit(self,event,**fields):
        self.file.write(json.dumps({'event':event,'monotonic':time.monotonic(),**fields},allow_nan=False)+'\n');self.file.flush();os.fsync(self.file.fileno())
    def close(self):self.file.close()


class RangeReader(io.RawIOBase):
    def __init__(self,item,deadline,journal):
        self.item=item;self.deadline=deadline;self.journal=journal
        self.pos=self.used=self.reserved=self.calls=0;self.cache={};self.ranges=[];self.headers=[]
        self.http=requests.Session()
    def readable(self):return True
    def seekable(self):return True
    def tell(self):return self.pos
    def seek(self,offset,whence=0):
        self.pos=offset if whence==0 else self.pos+offset if whence==1 else self.item['size']+offset
        if self.pos<0:raise ValueError('Negative source seek')
        return self.pos
    def read(self,n=-1):
        guard(self.deadline)
        if n<0 or n>33554432:raise ResourceStop('Oversized/unbounded native source request')
        n=min(n,max(0,self.item['size']-self.pos));out=bytearray()
        while n:
            guard(self.deadline);step=min(n,1048576);key=(self.pos,step)
            if key not in self.cache:
                if self.calls>=4096 or self.reserved+step+1>134217728 or self.journal.total_reserved+step+1>3758096384:
                    raise ResourceStop('Frozen per-source/global budget before request')
                self.calls+=1;self.reserved+=step+1;self.journal.total_reserved+=step+1
                sid=self.item['session_id'];req=self.calls;first=self.pos;last=first+step-1
                self.journal.emit('RESERVED',session_id=sid,request=req,offset=first,expected_bytes=step,reserved_bytes=step+1)
                url='https://api.brain-map.org/api/v2/well_known_file_download/'+str(self.item['file_id'])
                with self.http.get(url,params={'p16_r2_offset':first,'p16_r2_length':step},
                    headers={'Range':f'bytes={first}-{last}','If-Match':self.item['etag']},
                    stream=True,allow_redirects=False,timeout=min(30,max(.001,self.deadline-time.monotonic()))) as response:
                    header={'request':req,'status':response.status_code,'content_range':response.headers.get('Content-Range'),'etag':response.headers.get('ETag')}
                    self.headers.append(header);self.journal.emit('RESPONSE_HEADERS',session_id=sid,**header)
                    if response.status_code!=206 or header['content_range']!=f'bytes {first}-{last}/{self.item["size"]}' or header['etag']!=self.item['etag']:
                        raise ResourceStop('Exact pinned native range response failed; no redirect/retry/bulk fallback')
                    payload=bytearray()
                    while len(payload)<=step:
                        guard(self.deadline);chunk=response.raw.read(min(16384,step+1-len(payload)))
                        if not chunk:break
                        payload.extend(chunk);self.used+=len(chunk)
                        self.journal.emit('PAYLOAD',session_id=sid,request=req,bytes=len(chunk))
                    guard(self.deadline)
                    if len(payload)!=step:raise ResourceStop('Exact native range length failed')
                data=bytes(payload);self.cache[key]=data
                row={'request':req,'offset':first,'bytes':step,'sha256':hashlib.sha256(data).hexdigest()}
                self.ranges.append(row);self.journal.emit('COMPLETE_RANGE',session_id=sid,**row)
            out.extend(self.cache[key]);self.pos+=step;n-=step
        return bytes(out)
    def readinto(self,buffer):
        b=self.read(len(buffer));buffer[:len(b)]=b;return len(b)


def source_inputs(item):
    sid=item['session_id']
    header=read_gzip(R/'paper12_native_support1/metadata/native_headers'/f'{sid}.json.gz')
    entries=read(M1E/'ROSTER_METADATA_FINAL.json')['sessions'];matches=[x for x in entries if x['session_id']==sid]
    if len(matches)!=1:raise ValueError('Frozen successful flash metadata binding')
    path=R/matches[0]['path'];metadata=read(path)
    with np.load(path.with_suffix('.npz'),allow_pickle=False) as data:
        onsets,colors,valid=(data[k].copy() for k in ['start','color','main_valid'])
    probes=read(R/'paper16_m0/metadata/probes.body')['msg'];scope=[x for x in probes if int(x['ecephys_session_id'])==sid]
    inv=header['tables'].get('invalid_times',{})
    bad=invalid_rows(inv.get('start_time',[]),inv.get('stop_time',[]),inv.get('tags',[]),inv.get('tags_index',[]),item,scope)
    return header,onsets,colors,valid,bad,{'metadata_path':path.relative_to(R).as_posix(),'metadata_sha256':sha(path),'flash_array_sha256':sha(path.with_suffix('.npz'))}


def read_gzip(path):return json.loads(gzip.decompress(Path(path).read_bytes()))


def first_review_gate():
    approval=read(E/'FIRST_SOURCE_APPROVAL.json')
    if approval.get('decision')!='ACCEPTED_FIRST_R2_SOURCE_RUNNING_PASS' or any(type(approval.get(k)) is not int or approval[k]!=0 for k in ['open_P0','open_P1']):
        raise ValueError('Independent actual first-source review absent/failed')
    required={'paper16_running_r2/results/'+x for x in ['750749662/RESULT.json','750749662/NATIVE_SOURCE.json','750749662/NATIVE_rotation.npz','750749662/NATIVE_start.npz','750749662/NATIVE_end.npz','750749662/NATIVE_rotation.json','750749662/NATIVE_start.json','750749662/NATIVE_end.json','750749662/DERIVED_RUNNING.npz','750749662/ATTEMPT.json','STAGE_ATTEMPT.json','SUPERVISION_first.json','WORKER_first.json','BUDGET_FIRST.jsonl']}
    if not required<=approval.get('reviewed_hashes',{}).keys():raise ValueError('Incomplete actual first-source artifact review')
    if sha(E/'FIRST_SOURCE_REVIEW.md')!=approval['report_sha256']:raise ValueError('First source review identity')
    for name,digest in approval['reviewed_hashes'].items():
        path=(R/name).resolve();path.relative_to(R)
        if sha(path)!=digest:raise ValueError('First source evidence changed')
    first=read(P/'results/750749662/RESULT.json')
    if first['status']!='SOURCE_RUNNING_PASS' or not first['direct_running_coverage_pass']:raise ValueError('First source running gate not passed')
    if read(P/'results/SUPERVISION_first.json')['valid_completed_worker'] is not True:raise ValueError('First-source supervisor gate')
    snapshot=(P/'results/BUDGET_FIRST.jsonl').read_bytes()
    if not (P/'results/BUDGET_JOURNAL.jsonl').read_bytes().startswith(snapshot):raise ValueError('First source journal prefix altered')


def run_one(item,reg,deadline,journal,first):
    validate_source(item,reg);guard(deadline)
    folder=P/'results'/str(item['session_id']);folder.mkdir()
    once(folder/'ATTEMPT.json',{'started_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source':item,
         'registration_sha256':sha(P/'ACCESS_REGISTRATION.json'),'reader_sha256':sha(P/'reader.py'),'no_retry':True})
    reader=None;captured={};audit=[];reads=[];native_receipt=None;result=None;vectors={}
    def persist(key,array):
        receipt=save_arrays(folder/f'NATIVE_{key}.npz',{'values':array})
        once(folder/f'NATIVE_{key}.json',receipt)
        vectors[key]=receipt
    try:
        header,onsets,colors,valid,bad,meta=source_inputs(item);guard(deadline)
        reader=RangeReader(item,deadline,journal)
        with h5py.File(reader,'r') as file:
            structure=native_running(file,item,header,audit,reads,captured,first,persist)
        if set(vectors)!={'start','end','rotation'}:raise ValueError('Incomplete durable native-vector state')
        once(folder/'NATIVE_SOURCE.json',{'complete':set(vectors)=={'start','end','rotation'},'vectors':vectors})
        native_receipt={'manifest_path':(folder/'NATIVE_SOURCE.json').relative_to(R).as_posix(),'manifest_sha256':sha(folder/'NATIVE_SOURCE.json'),'vectors':vectors,'complete':True};guard(deadline)
        arrays,numerics=derive(captured['start'],captured['end'],captured['rotation'],onsets,colors,valid,bad,first)
        features=save_arrays(folder/'DERIVED_RUNNING.npz',arrays);guard(deadline)
        result={'source':item,'session_id':item['session_id'],'mouse_id':item['mouse_id'],'protocol':item['protocol'],
                'status':'SOURCE_RUNNING_PASS','structure':structure,'native_bundle':native_receipt,'derived_bundle':features,
                **numerics,'frozen_flash_metadata':meta,'neural_values_read':0,'A_physiology_executed':False,'model_fits':0,'Final_C_access':False,'Final_D_access':False}
        if first and not numerics['direct_running_coverage_pass']:
            result['status']='FIRST_SOURCE_COVERAGE_STOP';raise CoverageStop('First source original direct role/color coverage floor failed; remaining27 not authorized')
    except Exception as exc:
        if native_receipt is None:
            native_receipt={'vectors':vectors,'complete':False,'decoded_keys':sorted(captured)}
        result=result or {'source':item,'session_id':item['session_id'],'mouse_id':item['mouse_id'],'protocol':item['protocol'],'status':'SOURCE_FAILED_STOP',
                         'native_bundle':native_receipt,'neural_values_read':0,'A_physiology_executed':False,'model_fits':0,'Final_C_access':False,'Final_D_access':False}
        result.update({'error':type(exc).__name__+': '+str(exc),'terminal_verdict':'DEVELOPMENT_RUNNING_COVERAGE_INSUFFICIENT' if isinstance(exc,CoverageStop) else 'STOP_RESOURCE_OR_IMPLEMENTATION' if isinstance(exc,(ResourceStop,requests.RequestException,OSError)) else 'SOURCE_NUMERICAL_INCOMPATIBLE','no_retry':True})
    finally:
        if result is not None:
            result.update({'dataset_paths_read':reads,'component_audit':audit,'new_requests':reader.calls if reader else 0,'new_payload_bytes':reader.used if reader else 0,
                           'new_reserved_bytes':reader.reserved if reader else 0,'ranges':reader.ranges if reader else [],'response_headers':reader.headers if reader else [],
                           'payload_accounting_complete':reader is None or len(reader.ranges)==reader.calls,'finished_monotonic':time.monotonic(),
                           'source_array_hash_not_full_NWB_hash':True,'R2_attempt_separate_from_M2_and_R1':True})
            once(folder/'RESULT.json',result)
        if reader:reader.http.close()
    print(json.dumps({'session_id':item['session_id'],'status':result['status'],'requests':result['new_requests'],'payload':result['new_payload_bytes'],
                      'direct_coverage_pass':result.get('direct_running_coverage_pass'),'potential_coverage_pass':result.get('potential_running_coverage_pass'),'error':result.get('error')}),flush=True)
    return result


def worker(phase,deadline):
    if phase not in ['first','remaining']:raise ValueError('Unknown worker phase denied before any side effect')
    reg=review_gate();guard(deadline)
    stage=read(P/'results/STAGE_ATTEMPT.json')
    if stage['deadline']!=deadline or stage['registration_sha256']!=sha(P/'ACCESS_REGISTRATION.json'):raise ValueError('Stage identity/deadline mismatch')
    if phase=='remaining':first_review_gate()
    once(P/f'results/WORKER_{phase}.json',{'phase':phase,'deadline':deadline,'source_script_sha256':sha(Path(__file__))})
    journal=BudgetJournal(P/'results/BUDGET_JOURNAL.jsonl',append=phase=='remaining')
    objects=sorted(reg['objects'],key=lambda x:int(x['mouse_id']))
    first=[x for x in objects if x['session_id']==750749662]
    selected=first if phase=='first' else [x for x in objects if x['session_id']!=750749662]
    if len(first)!=1 or len(selected)!=(1 if phase=='first' else 27):raise ValueError('Frozen source roster')
    try:
        for item in selected:
            result=run_one(item,reg,deadline,journal,phase=='first')
            if result['status']!='SOURCE_RUNNING_PASS':return 1
        if phase=='remaining':
            rows=[read(P/'results'/str(x['session_id'])/'RESULT.json') for x in objects]
            summary=admission_possible(rows)
            summary.update({'terminal_verdict':'RUNNING_SOURCE_GATE_PASS' if summary['possible_A_physiological_admission'] else 'DEVELOPMENT_RUNNING_COVERAGE_INSUFFICIENT',
                            'sources_completed':28,'physiological_admission_established':False,'neural_values_read':0,'model_fits':0,'Final_C_D_access':False})
            guard(deadline);once(P/'results/RUNNING_GATE.json',summary)
        return 0
    finally:journal.close()


def supervise(command,deadline,target):
    started=time.monotonic();guard(deadline)
    once(Path(target).with_suffix('.attempt.json'),{'started':started,'deadline':deadline,'command':command})
    child=subprocess.Popen(command+['--deadline',repr(deadline)])
    try:code=child.wait(timeout=max(.001,deadline-time.monotonic()))
    except subprocess.TimeoutExpired:
        child.kill();child.wait();once(target,{'child_killed':True,'valid_completed_worker':False,'deadline':deadline,'completed':time.monotonic()});return 124
    complete=time.monotonic();valid=code==0 and complete<deadline
    once(target,{'child_exit':code,'child_killed':False,'valid_completed_worker':valid,'started':started,'deadline':deadline,'completed':complete})
    return code if code else (0 if valid else 124)


def main():
    if '--worker' in sys.argv:
        return worker(sys.argv[sys.argv.index('--worker')+1],float(sys.argv[sys.argv.index('--deadline')+1]))
    reg=review_gate();phase=sys.argv[1]
    if phase not in ['first','remaining']:raise ValueError('Fixed phase required')
    (P/'results').mkdir(exist_ok=True)
    if phase=='first':
        started=time.monotonic();deadline=started+14400
        once(P/'results/STAGE_ATTEMPT.json',{'started':started,'deadline':deadline,'registration_sha256':sha(P/'ACCESS_REGISTRATION.json'),'maximum_concurrency':1,'no_retry':True})
    else:
        first_review_gate();deadline=read(P/'results/STAGE_ATTEMPT.json')['deadline']
        if read(P/'results/SUPERVISION_first.json')['valid_completed_worker'] is not True:raise ValueError('First external supervisor did not pass')
    code=supervise([sys.executable,'-B','-m','paper16_running_r2.run_sources','--worker',phase],deadline,P/f'results/SUPERVISION_{phase}.json')
    if phase=='first' and (P/'results/BUDGET_JOURNAL.jsonl').exists():
        with (P/'results/BUDGET_FIRST.jsonl').open('xb') as f:
            f.write((P/'results/BUDGET_JOURNAL.jsonl').read_bytes());f.flush();os.fsync(f.fileno())
    return code


if __name__=='__main__':raise SystemExit(main())
