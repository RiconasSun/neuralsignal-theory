"""Strict metadata-value decoding from remote NWB files; forbidden canaries tested."""
import argparse
import datetime
import json
import math
import re
from pathlib import Path
import h5py
import numpy as np
from transport import P,META,POLICY,Transport,RangeReader,sha

IDENTITY={'/identifier','/session_id','/session_start_time','/timestamps_reference_time',
          '/general/session_id',
          '/session_description','/general/subject/subject_id','/general/experiment_description',
          '/general/notes','/general/protocol','/general/institution','/general/lab'}
UNIT_NAMES={'id','location','quality','unit_quality','KSLabel','ks_label','cluster_id','unit_id','probe','probe_id','electrodes','electrodes_index','electrode_group'}
ELECTRODE_NAMES={'id','location','group','group_name','label','probe','probe_id','anatomy','AP','DV','ML'}
INTERVAL_NAMES={'start_time','stop_time','id','tags','label','stimulus_name','condition','stimulus','trial_type',
                'Block','sound','sound_puretone','sound_bluenoise','sound_amp','sound_freq','airpuff','optogenetics'}


def permitted(path):
    if path in IDENTITY:return True
    if path.startswith('/units/') and path.count('/')==2:
        return path.rsplit('/',1)[1] in UNIT_NAMES
    if path.startswith('/general/extracellular_ephys/electrodes/') and path.count('/')==4:
        return path.rsplit('/',1)[1] in ELECTRODE_NAMES
    if re.fullmatch(r'/intervals/[^/]+/[^/]+',path):return path.rsplit('/',1)[1] in INTERVAL_NAMES
    if re.fullmatch(r'/analysis/(?:spike|LFP) saturation (?:start|stop)/timestamps',path):return True
    if re.fullmatch(r'/stimulus/presentation/[^/]+/timestamps',path):return True
    if path in ['/processing/behavior/Lick/lick/timestamps','/processing/ecephys/LFP/ElectricalSeries/starting_time']:return True
    return False


def hard_object(file,path):
    node=file
    for part in path.strip('/').split('/'):
        if not isinstance(node,h5py.Group) or not isinstance(node.get(part,getlink=True),h5py.HardLink):
            raise ValueError('Soft/external link denied: '+path)
        node=node[part]
    return node


def normalize(value,file=None):
    if isinstance(value,h5py.Reference):return file[value].name if value and file is not None else None
    if isinstance(value,bytes):return value.decode('utf8',errors='strict')
    if isinstance(value,np.ndarray):return [normalize(v,file) for v in value]
    if isinstance(value,np.generic):return normalize(value.item(),file)
    if isinstance(value,float) and not math.isfinite(value):return None
    return value


def read_value(file,path):
    if not permitted(path):raise ValueError('Dataset value denied: '+path)
    node=hard_object(file,path)
    if not isinstance(node,h5py.Dataset) or node.external:raise ValueError('Not an internal metadata dataset')
    if node.size>100000:raise ValueError('Metadata element bound exceeded')
    return normalize(node[()],file)


def schema(file):
    result=[]
    def walk(group,depth=0):
        if depth>10:return
        for name in group:
            path=group.name.rstrip('/')+'/'+name
            link=group.get(name,getlink=True)
            if not isinstance(link,h5py.HardLink):
                result.append({'path':path,'kind':'denied_link'});continue
            node=group[name]
            if isinstance(node,h5py.Group):
                result.append({'path':path,'kind':'group'})
                # Raw neural groups need no recursive schema expansion.
                if path!='/acquisition':walk(node,depth+1)
                else:
                    for child in node:
                        result.append({'path':path+'/'+child,'kind':'unexpanded_container'})
            else:
                attrs={k:normalize(v,file) for k,v in node.attrs.items() if k in ['description','unit','neurodata_type','namespace','comments','rate','starting_time']}
                result.append({'path':path,'kind':'dataset','shape':list(node.shape),'dtype':str(node.dtype),'allowed_value':permitted(path),'attrs':attrs})
    walk(file)
    return result


def inspect(asset,transport,values=False):
    reader=RangeReader(transport,f"https://api.dandiarchive.org/api/assets/{asset['asset_id']}/download/",asset['size'],asset['asset_id'])
    with h5py.File(reader,'r') as file:
        structure=schema(file)
        decoded={}
        if values:
            for entry in structure:
                if entry.get('allowed_value'):decoded[entry['path']]=read_value(file,entry['path'])
        result={'asset':asset,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
                'schema':structure,'decoded_values':decoded,'values_requested':values,
                'decoded_paths':list(decoded),'transport_bytes':reader.used,'ranges':reader.ranges,'etag':reader.etag,
                'spike_values_read':False,'full_object_hash_verified':False}
    reader.close()
    return result


def assets():
    result=[]
    for ds in POLICY['datasets']:
        found=[]
        for path in sorted(META.glob(ds['id']+'_assets_*.json')):
            if not re.fullmatch(ds['id']+r'_assets_\d{2}\.json',path.name):continue
            page=json.loads(path.read_text());found.extend(page['results'])
        expected=json.loads((META/(ds['id']+'_assets_00.json')).read_text())['count']
        if len(found)!=expected or len({x['asset_id'] for x in found})!=expected:raise ValueError('Incomplete/duplicate asset manifest')
        result.extend({**item,'dandiset':ds['id'],'version':ds['version']} for item in found if item['path'].endswith('.nwb'))
    if len(result)>POLICY['bounds']['nwb_assets']:raise ValueError('Asset bound exceeded')
    return result


def main(args):
    records=assets();t=Transport();target=META/('headers' if args.values else 'schemas')
    target.mkdir(exist_ok=True)
    if args.first:records=[next(x for x in records if x['dandiset']==ds['id']) for ds in POLICY['datasets']]
    for asset in records:
        path=target/(asset['dandiset']+'_'+asset['asset_id']+'.json')
        if path.exists():raise FileExistsError('Immutable header exists: '+str(path))
        result=inspect(asset,t,args.values)
        with path.open('x',encoding='utf8',newline='\n') as f:f.write(json.dumps(result,indent=2,allow_nan=False)+'\n')
        print(asset['dandiset'],asset['path'],result['transport_bytes'],flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--first',action='store_true');parser.add_argument('--values',action='store_true')
    main(parser.parse_args())
