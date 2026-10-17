"""Explicit anatomy/curation columns only; no NWB library or signal array API."""
import datetime
import re
import numpy as np
import numcodecs
from .retrieve import P,read,write,get,sha
from .inventory import S3

FIELDS=('units/structure','units/electrode_group_name','units/unit_id','units/is_qc_pass')

def register():
    rows=[];keys=[]
    for d in read(P/'DESCRIPTOR_PATHS.json'):
        meta=read(P/'sources'/f"{d['session']}_zmetadata.json")['metadata']
        for field in FIELDS:
            a=meta[field+'/.zarray']
            if len(a['shape'])!=1 or len(a['chunks'])!=1 or a['chunks'][0]<a['shape'][0]:raise ValueError('Only verified single-chunk metadata columns registered')
            if a['dtype'] not in {'|O','|b1'}:raise ValueError('Unexpected metadata type')
            if a['compressor']['id']!='blosc' or any(f['id']!='vlen-utf8' for f in a.get('filters') or []):raise ValueError('Unregistered codec')
            key=d['key'].rsplit('/.zmetadata',1)[0]+'/'+field+'/0'
            keys.append(key);rows.append(dict(session=d['session'],field=field,key=key,descriptor_sha256=sha((P/'sources'/f"{d['session']}_zmetadata.json").read_bytes()),saved_as=d['session']+'__'+field.replace('/','_')+'.chunk'))
    path=P/'COLUMN_ACCESS.json'
    if path.exists():raise FileExistsError('Column registration is append-only; preserve prior plan')
    write(path,dict(registered_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),before_anatomy_QC_values=True,purpose='Conservative single-probe anatomical/provider-QC upper bound; unread sessions count as potentially eligible. No counts transferred from scratch.',fields=FIELDS,exact_keys=keys,columns=rows,forbidden=['spike_times','spike_amplitudes','waveforms','firing_rate','raw running/lick/pupil samples'],codec='numcodecs==0.16.5; Blosc and vlen-utf8 only; never pickle'))
    print('Registered',len(keys),'individual metadata chunks before values.')

def download():
    for row in read(P/'COLUMN_ACCESS.json')['columns']:
        get(S3+row['key'],row['saved_as'])
    print('Saved exact registered anatomy/probe/identity/provider-QC metadata columns only.')

def decode(session,field):
    if field not in FIELDS:raise PermissionError('No neural or arbitrary column access')
    plan=read(P/'COLUMN_ACCESS.json')
    rows=[r for r in plan['columns'] if r['session']==session and r['field']==field]
    if len(rows)!=1:raise ValueError('Unregistered or duplicate column')
    row=rows[0];desc=P/'sources'/f'{session}_zmetadata.json'
    if sha(desc.read_bytes())!=row['descriptor_sha256']:raise ValueError('Descriptor identity changed')
    a=read(desc)['metadata'][field+'/.zarray']
    raw=(P/'sources'/row['saved_as']).read_bytes()
    if sha(raw)!=read(P/'sources'/(row['saved_as']+'.receipt.json'))['sha256']:raise ValueError('Column changed')
    if a['compressor']['id']!='blosc':raise ValueError('Unsafe codec')
    raw=numcodecs.get_codec(a['compressor']).decode(raw)
    filters=a.get('filters') or []
    if a['dtype']=='|O':
        if len(filters)!=1 or filters[0]['id']!='vlen-utf8':raise ValueError('Unsafe object codec')
        x=numcodecs.get_codec(filters[0]).decode(raw)
    else:
        if a['dtype']!='|b1' or filters:raise ValueError('Unexpected scalar codec')
        x=np.frombuffer(raw,dtype=np.dtype(a['dtype']))
    if len(x)!=a['shape'][0]:raise ValueError('Decoded row count mismatch')
    return x

def region(label):
    match=re.fullmatch(r'(ACAd|ACAv|PL|ILA)(?:1|2/3|4|5|6a|6b)?',str(label))
    return match[1] if match else None

if __name__=='__main__':
    import sys
    {'register':register,'download':download}[sys.argv[1]]()
