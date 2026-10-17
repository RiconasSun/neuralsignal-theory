"""Canonical-native bounded HDF5 metadata reads; no neural dataset API."""
import datetime,hashlib,io,json,math,re
from pathlib import Path
from urllib.parse import urlparse,urlencode,parse_qs,urlunparse
import h5py
import numpy as np
import requests
P=Path(__file__).resolve().parent;ROOT=P.parent
def read(p):return json.loads(Path(p).read_text(encoding='utf8'))
def sha(b):return hashlib.sha256(b).hexdigest()
def write(p,obj):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x',encoding='utf8',newline='\n') as f:json.dump(obj,f,indent=2,sort_keys=True,allow_nan=False);f.write('\n')
def append(p,obj):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('a',encoding='utf8',newline='\n') as f:f.write(json.dumps(obj,sort_keys=True,allow_nan=False)+'\n')
def verify_history():
    hashes=read(P/'INPUT_FREEZE.json')['hashes']
    for name,h in hashes.items():
        if sha((ROOT/name).read_bytes())!=h:raise ValueError('Historicalinput changed: '+name)
    return len(hashes)

IDENTITY={'/identifier','/session_id','/general/session_id','/session_start_time','/timestamps_reference_time','/general/subject/subject_id','/general/institution','/general/lab','/session_description','/notes','/general/notes','/general/experiment_description','/general/protocol'}
UNIT={'id','probe_name','cluster_uuid','ibl_quality_score','max_electrode','obs_intervals','obs_intervals_index'}
ELECTRODES={'id','location','group_name','x','y','z'}
TRIAL={'id','start_time','stop_time','gabor_stimulus_onset_time','auditory_cue_time','wheel_movement_onset_time','choice_registration_time','feedback_time','gabor_stimulus_offset_time','gabor_stimulus_contrast','gabor_stimulus_side','mouse_wheel_choice','is_mouse_rewarded','reward_volume_uL','probability_left','block_type','block_index','bwm_include','saturation_stim_plus06'}
INTERVALS={'epochs','invalid_times','valid_times','observation_intervals','artifact_intervals','bad_intervals','saturation_intervals'}
INTERVAL_FIELDS={'id','start_time','stop_time','tags','tags_index','probe_name','unit_id','description','reason','clock','coverage_complete'}
LOCALIZATION_BASES=['/general/localization','/general/localization/anatomical_coordinates_tables']
LOC_TABLES=[b+'/'+t for b in LOCALIZATION_BASES for t in ['ElectrodesIBLBregma','ElectrodesCCFv3']]
LOC_FIELDS={'id','localized_entity','probe_name','x','y','z','brain_region','atlas_id','beryl_location','cosmos_location'}
GROUPS=['/','/general','/units','/intervals','/intervals/trials','/general/subject','/general/extracellular_ephys','/general/extracellular_ephys/electrodes']+['/intervals/'+n for n in sorted(INTERVALS)]+LOCALIZATION_BASES+LOC_TABLES
ATTRS={'description','unit','neurodata_type','namespace','table','target','comments','method','clock','coverage_complete','reference_frame','time_reference','resolution','source'}
def permitted(path):
    if path in IDENTITY:return True
    if path.startswith('/units/') and path.count('/')==2:return path.rsplit('/',1)[1] in UNIT
    if path.startswith('/general/extracellular_ephys/electrodes/') and path.count('/')==4:return path.rsplit('/',1)[1] in ELECTRODES
    if path.startswith('/intervals/trials/') and path.count('/')==3:return path.rsplit('/',1)[1] in TRIAL
    if path.startswith('/intervals/') and path.count('/')==3:return path.split('/')[2] in INTERVALS and path.rsplit('/',1)[1] in INTERVAL_FIELDS
    if any(path.startswith(t+'/') and path[len(t)+1:] in LOC_FIELDS for t in LOC_TABLES):return True
    return False
def hard(file,path):
    node=file
    for part in path.strip('/').split('/'):
        if not isinstance(node,h5py.Group) or not isinstance(node.get(part,getlink=True),h5py.HardLink):raise ValueError('Soft/external/missing link denied: '+path)
        node=node[part]
    return node
def normalize(x,file):
    if isinstance(x,h5py.Reference):return file[x].name if x else None
    if isinstance(x,bytes):return x.decode('utf8')
    if isinstance(x,np.ndarray):return [normalize(v,file) for v in x]
    if isinstance(x,np.generic):return normalize(x.item(),file)
    if isinstance(x,float) and not math.isfinite(x):return None
    return x
def value(file,path):
    if not permitted(path):raise PermissionError('No neural/rawbehavior/arbitrary dataset values: '+path)
    node=hard(file,path)
    if not isinstance(node,h5py.Dataset) or node.is_virtual or node.external or node.size>100000:raise ValueError('Noninternal/oversized metadata dataset')
    return normalize(node[()],file)
def schema(file):
    """Enumerate whitelisted metadata groups; never open protected datasets."""
    result=[]
    for prefix in GROUPS:
        try:g=file if prefix=='/' else hard(file,prefix)
        except ValueError:continue
        if not isinstance(g,h5py.Group):continue
        if prefix!='/':result.append(dict(path=prefix,metadata_group=True,permitted=True,opened=True,attrs={k:normalize(v,file) for k,v in g.attrs.items() if k in ATTRS}))
        for name in g:
            path=prefix.rstrip('/')+'/'+name;row=dict(path=path,permitted=permitted(path))
            if not row['permitted']:
                row['opened']=False;result.append(row);continue
            node=hard(file,path);row['opened']=True
            if isinstance(node,h5py.Dataset):
                row.update(shape=list(node.shape),dtype=str(node.dtype),attrs={k:normalize(v,file) for k,v in node.attrs.items() if k in ATTRS})
            result.append(row)
    return result

DELIVERY_HOSTS={'api.dandiarchive.org','dandiarchive.s3.amazonaws.com','dandiarchive.s3.us-east-2.amazonaws.com','dandiarchive.s3.us-east-1.amazonaws.com'}
def validate_delivery(url,asset):
    u=urlparse(url)
    if u.scheme!='https' or u.username or u.password or u.hostname not in DELIVERY_HOSTS:raise PermissionError('Unexpected source delivery target before request')
    if u.hostname=='api.dandiarchive.org':
        if u.path!=f"/api/assets/{asset['asset_id']}/download/":raise PermissionError('Wrong canonical asset delivery endpoint')
    elif str(asset['blob']) not in u.path or not u.path.startswith('/blobs/'):
        raise PermissionError('Wrong canonical blob delivery path')

class Ranges(io.RawIOBase):
    def __init__(self,record,*,session=None):
        self.record=record;self.asset=record['asset'];self.size=int(self.asset['size']);self.pos=0;self.etag=None;self.asset_bytes=0;self.memory={}
        self.policy=read(P/'SOURCE_REGISTRATION.json')['access'];self.session=session or requests.Session()
        self.folder=P/'work/source_metadata_ranges'/self.asset['asset_id'];self.folder.mkdir(parents=True,exist_ok=True)
        self.log=P/'results/SOURCE_ACCESS.jsonl';self.range_receipts=[]
        allowed={r['asset']['asset_id']:r for r in read(P/'SOURCE_AUDIT_ROSTER.json')['records']}
        if self.asset['asset_id'] not in allowed or any(record[k]!=allowed[self.asset['asset_id']][k] for k in ['asset','mouse','eid','probe']):raise PermissionError('Asset/identity outside prospective metadata roster')
    def readable(self):return True
    def seekable(self):return True
    def tell(self):return self.pos
    def seek(self,n,whence=0):
        p=n if whence==0 else self.pos+n if whence==1 else self.size+n if whence==2 else -1
        if p<0 or p>self.size:raise ValueError('Invalid metadata seek')
        self.pos=p;return p
    def fetch(self,start,n):
        if n<=0 or n>self.policy['max_range_bytes'] or start<0 or start+n>self.size:raise ValueError('Invalid/unbounded metadata range')
        key=f'{start}_{n}';p=self.folder/(key+'.bin');receipt=self.folder/(key+'.json')
        if p.exists():
            r=read(receipt);raw=p.read_bytes()
            if sha(raw)!=r['sha256'] or r['asset_id']!=self.asset['asset_id'] or r['size']!=self.size or len(raw)!=n or r.get('start')!=start or r.get('bytes_requested')!=n or r.get('content_range')!=f'bytes {start}-{start+n-1}/{self.size}' or not r.get('etag'):raise ValueError('Metadata cache corrupt/mismatched range identity')
            if self.etag and self.etag!=r['etag']:raise ValueError('Cached source version mismatch')
            self.etag=r['etag'];return raw
        prior=[json.loads(x) for x in self.log.read_text().splitlines()] if self.log.exists() else []
        used=sum(r.get('bytes',0) for r in prior)
        asset_used=sum(r.get('bytes',0) for r in prior if r.get('asset_id')==self.asset['asset_id'])
        headers={'Range':f'bytes={start}-{start+n-1}','Accept-Encoding':'identity'}
        if self.etag:headers['If-Match']=self.etag
        last=None
        for attempt in range(self.policy['attempts_per_range']):
            if len(prior)>=self.policy['max_requests'] or used+n>self.policy['max_total_bytes']:raise RuntimeError('Prospective sourceaudit budget exhausted')
            if asset_used+n>self.policy['max_metadata_bytes_per_asset']:raise RuntimeError('Prospective perassetmetadata byte budget exhausted')
            row=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),asset_id=self.asset['asset_id'],mouse=self.record['mouse'],eid=self.record['eid'],start=start,bytes_requested=n,size=self.size,attempt=attempt+1,purpose='Opaque exact HDF5 transport for whitelisted metadata only; no neural dataset values',bytes=0)
            try:
                url=f"https://api.dandiarchive.org/api/assets/{self.asset['asset_id']}/download/?p14metadata_start={start}&length={n}&attempt={attempt+1}"
                hosts=[];response=None
                # Validate every hop before opening it; do not log signed query strings.
                for hop in range(4):
                    validate_delivery(url,self.asset)
                    http_log=P/'results/SOURCE_HTTP_ACCESS.jsonl'
                    calls=len(http_log.read_text(encoding='utf8').splitlines()) if http_log.exists() else 0
                    if calls>=self.policy['max_requests']:raise RuntimeError('Prospective HTTP transaction budget exhausted')
                    http_row=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),asset_id=self.asset['asset_id'],start=start,bytes_requested=n,host=urlparse(url).hostname,path=urlparse(url).path,attempt=attempt+1,hop=hop)
                    try:
                        response=self.session.get(url,headers=headers,timeout=(20,45),stream=True,allow_redirects=False)
                        http_row['status']=response.status_code
                    except Exception as exc:http_row.update(error_type=type(exc).__name__);raise
                    finally:append(http_log,http_row)
                    hosts.append(urlparse(url).hostname)
                    if response.status_code not in {301,302,303,307,308}:break
                    destination=response.headers.get('Location','');response.close();response=None
                    validate_delivery(destination,self.asset)
                    url=destination
                if response is None:raise RuntimeError('Too many source delivery redirects')
                with response:
                    row.update(status=response.status_code,delivery_hosts=hosts)
                    if response.status_code!=206:raise RuntimeError('Range refused; bulk body left unread')
                    expected=f'bytes {start}-{start+n-1}/{self.size}'
                    etag=response.headers.get('ETag')
                    if response.headers.get('Content-Range')!=expected or not etag or self.etag and etag!=self.etag:raise RuntimeError('Changed/mismatched source range')
                    parts=[]
                    for chunk in response.iter_content(65536):
                        row['bytes']+=len(chunk)
                        if row['bytes']>n:raise RuntimeError('Oversized source range')
                        parts.append(chunk)
                    raw=b''.join(parts)
                    if len(raw)!=n:raise RuntimeError('Truncated range')
                    self.etag=etag;row.update(etag=etag,content_range=expected,sha256=sha(raw));p.write_bytes(raw);write(receipt,row)
                    self.asset_bytes+=n;self.range_receipts.append(dict(start=start,bytes=n,sha256=sha(raw)));return raw
            except Exception as exc:row.update(error_type=type(exc).__name__,error=str(exc).split('?')[0]);last=exc
            finally:
                append(self.log,row);prior.append(row);used+=row['bytes'];asset_used+=row['bytes']
        raise RuntimeError('Registered metadata range attempts failed; sanitized journal preserves cause') from None
    def read(self,n=-1):
        if n<0:raise ValueError('Unbounded/fullNWB read forbidden')
        n=min(n,self.size-self.pos)
        if n==0:return b''
        key=(self.pos,n)
        if key not in self.memory:self.memory[key]=self.fetch(*key)
        raw=self.memory[key];self.pos+=n;return raw
    def readinto(self,b):
        raw=self.read(len(b));b[:len(raw)]=raw;return len(raw)

def inspect(record,values=False):
    reader=Ranges(record)
    with h5py.File(reader,'r') as f:
        s=schema(f);v={}
        if values:
            for row in s:
                if row['permitted'] and 'shape' in row:v[row['path']]=value(f,row['path'])
        result=dict(asset_id=record['asset']['asset_id'],source_asset_path=record['asset']['path'],eid=record['eid'],mouse=record['mouse'],source_size=reader.size,etag=reader.etag,schema=s,values=v,neural_values_decoded=False,raw_behavior_values_decoded=False,new_transport_bytes=reader.asset_bytes,opaque_range_hashes=reader.range_receipts)
    return result

def main(mode):
    verify_history();records=read(P/'SOURCE_AUDIT_ROSTER.json')['records']
    if mode=='first_schema':records=records[:1]
    target=P/'metadata'/('values' if mode=='values' else 'schemas');target.mkdir(parents=True,exist_ok=True)
    for record in records:
        path=target/(record['asset']['asset_id']+'.json')
        if path.exists():raise FileExistsError('Preserve prior metadata export; use reviewed explicit recovery instead of overwrite')
        result=inspect(record,values=mode=='values');write(path,result)
        print(record['mouse'],record['asset']['asset_id'],'metadata_fields',len(result['schema']),'values',len(result['values']),'newbytes',result['new_transport_bytes'],flush=True)

if __name__=='__main__':
    import sys
    main(sys.argv[1])
