"""Exact saved-A reuse and role-gated native B/E extraction, cache first."""
import io,os,hashlib
from pathlib import Path
import h5py,numpy as np,requests
from .core import R,P,E,load,sha,once,event,arrays,array_id,guard,verify_pins,AccessStop,ImplementationStop,BudgetStop
from paper16_dev_r3.run_m2 import source_inputs
from paper16_source_r4.neural_reader import resolve,verify_index,verify_probe_metadata,value_scope,REQUIRED,SCALARS,metadata as native_metadata
from paper16_dev_r3.core import finite_native

def account():return load(R/'paper16_source_r4/SOURCE_AND_PHYSIOLOGY_ACCOUNT.json')['sources']
def admitted():return sorted([x for x in account() if x['selection']['admitted']],key=lambda x:int(x['source']['mouse_id']))

def validate(item):
    reg=load(P/'ACCESS_REGISTRATION.json')
    matches=[x for x in reg['objects'] if x['session_id']==item.get('session_id')]
    if len(matches)!=1 or item!=matches[0] or item['role']!='Development' or item['session_id'] in reg['denied_final_session_ids']:
        raise AccessStop('Final/unregistered/altered source denied before opening')
    return reg

def cache_identity(item,offset,length,record,raw):
    if any(record.get(k)!=v for k,v in {'session_id':item['session_id'],'offset':offset,'bytes':length,'source_size':item['size'],'etag':item['etag']}.items()) or len(raw)!=length or hashlib.sha256(raw).hexdigest()!=record.get('sha256'):
        raise AccessStop('Cache identity/hash mismatch')

def reserve_transport(reservations,item,offset,length):
    if not 0<length<=1048576 or not 0<=offset<offset+length<=item['size']:raise BudgetStop('Invalid bounded range')
    amount=length+1;sid=item['session_id']
    if sum(x['reserved_bytes'] for x in reservations)+amount>8*1024**3 or sum(x['reserved_bytes'] for x in reservations if x['session_id']==sid)+amount>512*1024**2:
        raise BudgetStop('New R2 HTTP cap denied before network')
    if any(x['session_id']==sid and x['offset']==offset for x in reservations):raise AccessStop('Source range attempt consumed; no retry')
    return amount

def metadata(record):
    validate(record['source'])
    verify_pins()
    frozen=checked_reference(record['result']);checked_reference(record['QC'])
    expected=frozen['source_metadata_pins'];path=R/expected['metadata_path']
    check_file(path,expected['metadata_sha256']);check_file(path.with_suffix('.npz'),expected['flash_array_sha256'])
    sid=record['source']['session_id'];running_state=load(R/'paper16_running_r2/results'/str(sid)/'RESULT.json')
    bundle=running_state['derived_bundle'];check_file(R/bundle['path'],bundle['sha256'])
    header,flashes,running,pins=source_inputs(record['source'])
    if pins!=expected or running_state['frozen_flash_metadata']!=expected:raise AccessStop('Frozen metadata adapter identity mismatch')
    with np.load(path.with_suffix('.npz'),allow_pickle=False) as saved:
        for name in ['start','stop','color','main_valid']:
            if not np.array_equal(flashes[name],saved[name],equal_nan=True):raise AccessStop('Frozen metadata adapter arrays changed')
        flashes['stimulus_valid']=stimulus_validity(saved['start'],saved['stop'],saved['color'],saved['stimulus_invalid_intervals'])
    if set(running)!=set(bundle['arrays']):raise AccessStop('Frozen running array set')
    for name,identity in bundle['arrays'].items():
        actual=array_id(running[name]);expected_array={'shape':identity['shape'],'dtype':identity['dtype'],'sha256':identity['raw_bytes_sha256']}
        if actual!=expected_array:raise AccessStop('Frozen running adapter array identity')
    return header,flashes,running,pins

def check_file(path,digest):
    if not Path(path).is_file() or sha(path)!=digest:raise AccessStop('Missing/corrupt frozen reference: '+str(path))

def checked_reference(ref):
    path=R/ref['path'];check_file(path,ref['sha256'])
    if 'bytes' in ref and path.stat().st_size!=ref['bytes']:raise AccessStop('Frozen reference byte count')
    return load(path) if path.suffix=='.json' else None

def stimulus_validity(starts,stops,colors,invalid):
    starts=np.asarray(starts);stops=np.asarray(stops);colors=np.asarray(colors);invalid=np.asarray(invalid).reshape(-1,2)
    if starts.shape!=stops.shape or starts.shape!=colors.shape or not np.isfinite(invalid).all():raise AccessStop('Stimulus metadata geometry')
    return np.isfinite(starts)&np.isfinite(stops)&(stops>starts)&np.isin(colors,[-1,1])&np.array([not np.any((invalid[:,0]<b)&(a<invalid[:,1])) for a,b in zip(starts,stops)])

def saved_A(record):
    from .controller import require_phase
    require_phase('A');validate(record['source'])
    sid=record['source']['session_id'];_,flashes,running,pins=metadata(record)
    selected=record['selection']['selected_unit_ids'];mask=np.asarray(record['selection']['common_mask'],bool)
    rows=np.flatnonzero(mask & (np.arange(150)<90));captures=load(R/'paper16_source_r4/A_ONLY_STATE_MANIFEST.json')['all_candidate_states']
    by={x['unit_id']:x for x in captures if x['session_id']==sid};perunit=[]
    for uid in selected:
        capture=by[uid];path=R/capture['private_path']
        if sha(path)!=capture['sha256']:raise AccessStop('Frozen A capture hash changed')
        with np.load(path,allow_pickle=False) as a:
            if {k:array_id(a[k]) for k in a.files}!=capture['arrays']:raise AccessStop('Frozen A array identity')
            offsets=a['offsets'];lookup={int(row):i for i,row in enumerate(a['original_ordinals'])}
            perunit.append([a['timestamps'][offsets[lookup[row]]:offsets[lookup[row]+1]].copy() for row in rows])
    trials=[[perunit[u][j] for u in range(len(selected))] for j in range(len(rows))]
    event(P/'results/ACCESS.jsonl',role='A',event='SAVED_A_EXPORTED',session_id=sid,units=selected,original_ordinals=rows.tolist(),new_source_requests=0)
    return flashes,running,trials,rows,np.asarray(selected,dtype=np.int64)

class CacheReader(io.RawIOBase):
    def __init__(self,item,stage):
        validate(item);guard(stage);self.item=item;self.stage=stage;self.pos=0;self.cache={}
        self.http=requests.Session();self.http.mount('https://',requests.adapters.HTTPAdapter(max_retries=0))
    def readable(self):return True
    def seekable(self):return True
    def tell(self):return self.pos
    def seek(self,n,whence=0):
        if type(n) is not int or whence not in [0,1,2]:raise AccessStop('Invalid source seek')
        self.pos=n if whence==0 else self.pos+n if whence==1 else self.item['size']+n
        if self.pos<0:raise AccessStop('Negative source offset')
        return self.pos
    def block(self,offset):
        guard(self.stage)
        if offset in self.cache:return self.cache[offset]
        length=min(1048576,self.item['size']-offset);sid=self.item['session_id']
        for root in [P,R/'paper16_source_r4',R/'paper16_dev_r3']:
            path=root/'work/private/ranges'/str(sid)/(str(offset)+'.bin');receipt=path.with_suffix('.json')
            if root==R/'paper16_dev_r3' and path.exists() and not receipt.exists():continue
            if path.exists() or receipt.exists():
                if not path.exists() or not receipt.exists():raise AccessStop('Incomplete cache publication; no retry/fallback')
                record=load(receipt);raw=path.read_bytes()
                cache_identity(self.item,offset,length,record,raw)
                self.cache[offset]=raw;return raw
        # New transfer is one prospective attempt, never an R4 timeout recovery.
        journal=P/'results/HTTP.jsonl';old=[loadline for loadline in self._journal(journal)]
        reservations=[x for x in old if x['event']=='RESERVED'];amount=reserve_transport(reservations,self.item,offset,length)
        event(journal,event='RESERVED',session_id=sid,offset=offset,reserved_bytes=amount,expected_bytes=length)
        path=P/'work/private/ranges'/str(sid)/(str(offset)+'.bin');path.parent.mkdir(parents=True,exist_ok=True)
        end=offset+length-1
        try:
            with self.http.get('https://api.brain-map.org/api/v2/well_known_file_download/'+str(self.item['file_id']),
                headers={'Range':f'bytes={offset}-{end}','If-Match':self.item['etag'],'Accept-Encoding':'identity'},
                stream=True,allow_redirects=False,timeout=30) as response:
                if response.status_code!=206 or response.headers.get('ETag')!=self.item['etag'] or response.headers.get('Content-Range')!=f'bytes {offset}-{end}/{self.item["size"]}':raise AccessStop('Exact pinned206/ETag/range required')
                if response.headers.get('Content-Length')!=str(length):raise AccessStop('Exact bounded response length required')
                raw=bytearray()
                with path.open('xb') as out:
                    while len(raw)<=length:
                        guard(self.stage);chunk=response.raw.read(min(16384,length+1-len(raw)))
                        if not chunk:break
                        out.write(chunk);out.flush();os.fsync(out.fileno());raw.extend(chunk)
                        event(journal,event='PAYLOAD',session_id=sid,offset=offset,bytes=len(chunk))
                if len(raw)!=length:raise AccessStop('Truncated/oversized body retained; no retry')
            raw=bytes(raw);receipt={'session_id':sid,'offset':offset,'bytes':length,'source_size':self.item['size'],'etag':self.item['etag'],'sha256':hashlib.sha256(raw).hexdigest()}
            once(path.with_suffix('.json'),receipt);self.cache[offset]=raw;return raw
        except BaseException as exc:
            event(journal,event='FAILED',session_id=sid,offset=offset,error=type(exc).__name__,retry=False);raise
    @staticmethod
    def _journal(path):
        import json
        return [json.loads(x) for x in path.read_text(encoding='utf8').splitlines()] if path.exists() else []
    def read(self,n=-1):
        guard(self.stage)
        if type(n) is not int or not 0<=n<=33554432:raise BudgetStop('Unbounded/oversized logical source read')
        n=min(n,max(0,self.item['size']-self.pos));out=bytearray()
        while n:
            offset=self.pos//1048576*1048576;raw=self.block(offset);left=self.pos-offset;count=min(n,len(raw)-left)
            if count<=0:raise AccessStop('Native cache cursor')
            out.extend(raw[left:left+count]);n-=count;self.pos+=count
        return bytes(out)
    def readinto(self,buffer):
        raw=self.read(len(buffer));buffer[:len(raw)]=raw;return len(raw)
    def close(self):
        if getattr(self,'http',None):self.http.close()
        super().close()

def split_role(spikes,flashes,mask,role,full_flash=False):
    if role not in ['B','E'] or (full_flash and role!='E'):raise AccessStop('Only gate-scoped B or E export')
    finite_native(spikes);lo,hi={'B':(90,120),'E':(120,150)}[role]
    rows=np.flatnonzero(np.asarray(mask)&(np.arange(150)>=lo)&(np.arange(150)<hi));out=[]
    for row in rows:
        a=flashes['start'][row];b=flashes['stop'][row] if full_flash else a+11*.02
        out.append(spikes[np.searchsorted(spikes,a,'left'):np.searchsorted(spikes,b,'left')].copy())
    return rows,out

def native_role(record,role,stage):
    from .controller import require_phase
    require_phase(role);reg=validate(record['source']);guard(stage)
    if role not in ['B','E']:raise AccessStop('Unknown/Final role denied before source open')
    item=record['source'];sid=item['session_id'];header,flashes,running,_=metadata(record)
    full_flash=role=='E' and load(P/'results/NONREFIT_COVERAGE_PLAN.json')[str(item['mouse_id'])]['N3_full_flash_support']
    checked_reference(record['QC']);frozen_result=checked_reference(record['result'])
    qc={int(x['unit_id']):x for x in CacheReader._journal(R/record['QC']['path'])}
    units=record['selection']['selected_unit_ids'];audit=[];reads=[];perunit=[]
    with CacheReader(item,stage) as reader:
        with h5py.File(reader,'r') as file:
            text=lambda x:x.decode('utf8') if isinstance(x,bytes) else str(x)
            for name in ['nwb_version','namespace','neurodata_type','object_id']:
                if name in header.get('root_attributes',{}) and text(file.attrs.get(name))!=text(header['root_attributes'][name]):raise AccessStop('Source root identity')
            verify_probe_metadata(file,item,header,audit)
            ds={p:resolve(file,p,audit) for p in REQUIRED};ids=ds['/units/id'];index=ds['/units/spike_times_index'];target=ds['/units/spike_times'];peak=ds['/units/peak_channel_id']
            expected_native=frozen_result['native_objects']
            if any(native_metadata(ds[path])!=expected_native[path] for path in REQUIRED):raise AccessStop('Frozen native dataset shape/dtype/address/compression identity')
            if target.dtype!=np.dtype('float64'):raise AccessStop('Native timestamp precision')
            verify_index(file,index,target);permitted={}
            def allow(path,selectors):permitted[int(h5py.h5o.get_info(ds[path].id).addr)]=(path,selectors)
            for path in SCALARS:allow(path,[()])
            allow('/units/id',[slice(None)])
            with value_scope(file,permitted,reads):
                for path in SCALARS:
                    expected=str(sid) if path=='/identifier' else header[path]
                    if text(np.asarray(ds[path][()]).item())!=str(expected):raise AccessStop('Source identity/clock')
                values=ids[:]
                if len(set(map(int,values)))!=len(values):raise AccessStop('Duplicate source units')
                lookup={int(x):i for i,x in enumerate(values)}
                for uid in units:
                    i=lookup[uid];allow('/units/peak_channel_id',[i])
                    if int(peak[i])!=qc[uid]['peak_channel_id']:raise AccessStop('Peak/probe/unit identity')
                    allow('/units/spike_times_index',[i] if i==0 else [i-1,i]);a=0 if i==0 else int(index[i-1]);b=int(index[i])
                    if not 0<=a<=b<=len(target) or b-a>load(R/'paper16_dev_r3/ACCESS_REGISTRATION.json')['resources']['selected_unit_row_values_max']:raise AccessStop('Row bounds/cap')
                    allow('/units/spike_times',[slice(a,b)]);raw=target[a:b];finite_native(raw)
                    if array_id(raw)!=qc[uid]['full_row_integrity_only']:raise AccessStop('Original full-row integrity/hash changed')
                    rows,export=split_role(raw,flashes,record['selection']['common_mask'],role,full_flash=full_flash);del raw
                    perunit.append(export)
    trials=[[perunit[u][j] for u in range(len(units))] for j in range(len(rows))]
    flat=[];offsets=[0]
    for trial in trials:
        for values in trial:flat.append(values);offsets.append(offsets[-1]+len(values))
    capture=arrays(P/'work/roles'/str(sid)/(role+'.npz'),timestamps=np.concatenate(flat),offsets=np.asarray(offsets,dtype=np.int64),
        original_ordinals=rows,unit_ids=np.asarray(units,dtype=np.int64))
    event(P/'results/ACCESS.jsonl',role=role,event='SCOPED_NATIVE_EXPORT',session_id=sid,units=units,ordinals=rows.tolist(),
        full_row_integrity_decoding_transient=True,exported_other_roles=False,protected_role_capture=capture,full_flash_export_for_registered_N3=full_flash)
    once(P/'results/source_access'/str(sid)/(role+'.json'),{'audit':audit,'logical_value_reads':reads,'role':role,'original_ordinals':rows.tolist()})
    return flashes,running,trials,rows,np.asarray(units,dtype=np.int64)
