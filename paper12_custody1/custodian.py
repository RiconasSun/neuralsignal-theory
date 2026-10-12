"""Guarded NWB extraction. This must run under the trusted host role only."""
import hashlib
import io
import json
import os
from pathlib import Path
import sys
from collections import OrderedDict
import h5py
import numpy as np
import requests
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import register as r
from security import require_custodian, protect
from custody_core import count_unit
from cipher_core import seal


def check_gate():
    r.verify()
    registration=r.load(r.HERE/'role_registration.json')
    for name,value in registration['sha256'].items():
        if r.sha(r.HERE/name)!=value:
            raise RuntimeError('CUSTODY_SOURCE_CHANGED')
    proof=r.load(r.HERE/'results/isolation/native_profile_runtime2.json')
    if proof['mandatory_isolation_pass'] is not True:
        raise PermissionError('ISOLATION_NOT_VERIFIED')
    if not r.load(r.HERE/'results/functional_gate.json')['pass']:
        raise PermissionError('FUNCTIONAL_CUSTODY_NOT_VERIFIED')
    require_custodian()


class Source(io.RawIOBase):
    def __init__(self,item):
        self.url='https://api.brain-map.org/api/v2/well_known_file_download/'+item['file_id']
        self.size=int(item['content_range'].split('/')[-1]);self.etag=item['etag']
        self.position=0;self.cache=OrderedDict();self.http=requests.Session();self.bytes=0
        self.private_hash=hashlib.sha256()
    def readable(self):return True
    def seekable(self):return True
    def tell(self):return self.position
    def seek(self,n,whence=0):
        self.position=n if whence==0 else self.position+n if whence==1 else self.size+n
        if self.position<0:raise ValueError('NEGATIVE_SOURCE_OFFSET')
        return self.position
    def read(self,n=-1):
        if n<0 or n>134217728:raise ValueError('UNBOUNDED_SOURCE_READ')
        n=min(n,self.size-self.position)
        if n<=0:return b''
        pieces=[];remaining=n
        block=4194304
        while remaining:
            start=self.position//block*block;end=min(start+block,self.size)-1
            if start not in self.cache:
                with self.http.get(self.url,params={'p12_custody_offset':start,'p12_custody_end':end},
                                   headers={'Range':f'bytes={start}-{end}','If-Match':self.etag},stream=True,timeout=60) as res:
                    if res.status_code!=206 or res.headers.get('Content-Range')!=f'bytes {start}-{end}/{self.size}' or res.headers.get('ETag')!=self.etag:
                        raise RuntimeError('SOURCE_VERSION_OR_RANGE_INVALID')
                    value=res.raw.read(end-start+2)
                    if len(value)!=end-start+1:raise RuntimeError('SOURCE_RESPONSE_LENGTH_INVALID')
                self.cache[start]=value;self.bytes+=len(value);self.private_hash.update(value)
                while len(self.cache)>16:self.cache.popitem(last=False)
            self.cache.move_to_end(start)
            offset=self.position-start;take=min(remaining,len(self.cache[start])-offset)
            pieces.append(self.cache[start][offset:offset+take]);self.position+=take;remaining-=take
        return b''.join(pieces)
    def readinto(self,buf):
        value=self.read(len(buf));buf[:len(value)]=value;return len(value)
    def close(self):
        self.cache.clear();self.http.close();super().close()


def dataset(file,path,kind):
    if path not in ('/units/id','/units/peak_channel_id','/units/spike_times_index','/units/spike_times'):
        raise PermissionError('NWB_VALUE_PATH_FORBIDDEN')
    obj=file
    for name in path.strip('/').split('/'):
        if not isinstance(obj.get(name,getlink=True),h5py.HardLink):raise RuntimeError('NWB_EXTERNAL_LINK')
        obj=obj[name]
    if not isinstance(obj,h5py.Dataset) or obj.ndim!=1 or obj.dtype.kind not in kind:
        raise RuntimeError('NWB_SOURCE_SCHEMA_INVALID')
    return obj


def encrypted_write(root,name,payload,context):
    key=AESGCM.generate_key(bit_length=256)
    artifact=seal(key,payload,context)
    keyfile=root/(name+'.key')
    with keyfile.open('xb') as f:f.write(key)
    protect(keyfile)
    target=root/(name+'.gcm')
    with target.open('xb') as f:f.write(artifact)
    protect(target)
    return {'ciphertext_sha256':r.sha(target),'ciphertext_bytes':len(artifact)}


def session(animal,item,units,trials):
    check_gate()
    root=r.HERE/'.private/real'/animal['session_id']
    root.mkdir(parents=True,exist_ok=False)
    protect(root)
    qcpart='train' if animal['group']=='development' else 'calibration'
    tensor=np.zeros((len(trials),20,len(units)),dtype='<u4')
    audit=[];decoded=False;reader=Source(item)
    try:
        with h5py.File(reader,'r') as f:
            ids=np.asarray(dataset(f,'/units/id','iu')[:],dtype=np.int64)
            channels=np.asarray(dataset(f,'/units/peak_channel_id','iu')[:],dtype=np.int64)
            offsets=np.asarray(dataset(f,'/units/spike_times_index','iu')[:],dtype=np.int64)
            spikes=dataset(f,'/units/spike_times','f')
            if len(ids)!=len(channels) or len(ids)!=len(offsets) or len(np.unique(ids))!=len(ids) or np.any(np.diff(offsets)<0) or (len(offsets) and offsets[-1]!=len(spikes)):
                raise RuntimeError('NWB_UNIT_INDEX_INTEGRITY_FAILED')
            lookup={str(u):i for i,u in enumerate(ids)}
            # Verify every represented locked unit's channel before reading spikes.
            for unit in units:
                if unit['unit_id'] in lookup and str(channels[lookup[unit['unit_id']]])!=unit['channel_id']:
                    raise RuntimeError('FROZEN_UNIT_CHANNEL_MISMATCH')
            for col,unit in enumerate(units):
                row={'unit_id':unit['unit_id'],'subfield':unit['subfield'],'eligible':False}
                if unit['metadata_quarantined']:
                    row['reason']='METADATA_QUARANTINE'
                elif unit['unit_id'] not in lookup:
                    row['reason']='UNIT_NOT_PRESENT_IN_NWB'
                else:
                    i=lookup[unit['unit_id']];begin=int(offsets[i-1]) if i else 0;end=int(offsets[i])
                    values=np.asarray(spikes[begin:end],dtype=float)
                    decoded=True
                    tensor[:,:,col],qc=count_unit(values,trials,qcpart)
                    row.update(qc);row['reason']='ELIGIBLE' if qc['eligible'] else 'FROZEN_PHYSIOLOGICAL_QC_REJECT'
                    del values
                audit.append(row)
        private_provenance={'source_bytes_transported':reader.bytes,'source_transport_order_digest_not_whole_file':reader.private_hash.hexdigest(),
                            'source_full_session_decoded_by_custodian':decoded,'decoding_scope':'Complete time vectors of locked target units only;other-region spike values not decoded',
                            'unit_QC':audit}
        r.save(root/'private_provenance.json',private_provenance,True);protect(root/'private_provenance.json')
        context={'study':r.ID,'mouse':animal['mouse_id'],'source_etag':item['etag'],
                 'trial_lock_sha256':r.sha(r.ROOT/'paper12_curated_v1/locks/trials.json'),
                 'unit_lock_sha256':r.sha(r.ROOT/'paper12_curated_v1/locks/units.json')}
        cipher_receipts={}
        for partition,compartment in (('train','A'),('validation','B'),('calibration','C'),('locked_evaluation','D')):
            idx=[i for i,t in enumerate(trials) if t['partition']==partition and t['metadata_admitted']]
            if idx:
                payload=np.ascontiguousarray(tensor[idx]).tobytes()
                cipher_receipts[compartment]=encrypted_write(root,compartment,payload,{**context,'compartment':compartment,
                    'shape':[len(idx),20,len(units)],'dtype':'<u4'})
        # No partition plaintext published at extraction. A needs cohort gate then role export.
        eligible={field:sum(x['eligible'] and x['subfield']==field for x in audit) for field in ('CA1','DG')}
        result={'mouse_id':animal['mouse_id'],'session_id':animal['session_id'],'group':animal['group'],
                'candidate_units':len(units),'eligible_unit_counts':eligible,'eligible_mouse':min(eligible.values())>=5,
                'qc_partition':qcpart,'QC_detail_access':'PRIVATE_CUSTODY_ONLY','ciphertext_receipts':cipher_receipts,
                'source_full_session_decoded_by_custodian':decoded,'final_values_exposed_to_analysis':False,'final_holdout_evaluated':False,
                'raw_vectors_exported':False,'source_etag':item['etag']}
        r.save(r.HERE/'results/M2/sessions'/(animal['session_id']+'.json'),result,True)
        print(json.dumps({k:result[k] for k in ('session_id','group','eligible_unit_counts','eligible_mouse','source_full_session_decoded_by_custodian','final_values_exposed_to_analysis','final_holdout_evaluated')}),flush=True)
    except Exception as exc:
        r.save(r.HERE/'results/M2/failures'/(animal['session_id']+'.json'),{
            'session_id':animal['session_id'],'group':animal['group'],'error_type':type(exc).__name__,
            'error_code':str(exc) if isinstance(exc,(RuntimeError,ValueError,PermissionError)) else 'SOURCE_EXTRACTION_FAILED',
            'source_full_session_decoded_by_custodian':decoded,'final_values_exposed_to_analysis':False,'final_holdout_evaluated':False,
            'partial_public_partition_exported':False},True)
        raise
    finally:
        reader.close()


def main():
    check_gate()
    old=r.ROOT/'paper12_curated_v1'
    animals=r.load(old/'locks/animals.json');allunits=r.load(old/'locks/units.json');alltrials=r.load(old/'locks/trials.json')
    items={x['session_id']:x for x in r.load(r.ROOT/'paper12/metadata/allen_header_capability.json')}
    if '--smoke' in sys.argv:animals=animals[:1]
    for animal in animals:
        sid=animal['session_id']
        if (r.HERE/'results/M2/sessions'/(sid+'.json')).exists():continue
        if (r.HERE/'results/M2/failures'/(sid+'.json')).exists():raise RuntimeError('PRESERVED_EXTRACTION_FAILURE_STOP')
        session(animal,items[sid],[u for u in allunits if u['session_id']==sid],
                [t for t in alltrials if t['session_id']==sid])


if __name__=='__main__':
    try:main()
    except Exception:
        print('CUSTODY_ABORTED_SEE_SANITIZED_FAILURE_RECEIPT',flush=True)
        sys.exit(1)
