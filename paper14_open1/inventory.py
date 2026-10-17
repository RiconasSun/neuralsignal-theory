"""Canonical identities and descriptor registration. No outcome data."""
import json
import re
import xml.etree.ElementTree as ET
from .retrieve import P,read,write,get

API='https://api.allenneuraldynamics.org/v2/metadata_index/data_assets'
S3='https://aind-open-data.s3.us-west-2.amazonaws.com/'

def versions(asset):
    return [z['code'].get('version') for z in asset.get('processing',{}).get('data_processes',[]) if z.get('process_type')=='File format conversion']

def session(asset):
    match=re.match(r'ecephys_(\d{6})_(\d{4}-\d{2}-\d{2})_\d{2}-\d{2}-\d{2}',asset['name'])
    if match and asset.get('data_description',{}).get('subject_id')==match[1]:return match[1]+'_'+match[2]
    raise ValueError('Unverified canonical subject/session identity')

def public(asset):
    return asset['location']=='s3://aind-open-data/'+asset['name'] and asset['data_description']['license']=='CC-BY-4.0'

def selected():
    allrows=read(P/'sources/dynamic_routing_nwb_catalog.json')
    assert len(allrows)<500
    groups={}
    for a in allrows:
        if public(a):groups.setdefault(session(a),[]).append(a)
    def key(a):
        v=versions(a)
        assert len(v)==1 and re.fullmatch(r'\d+\.\d+\.\d+',v[0])
        return tuple(map(int,v[0].split('.'))),a['data_description']['creation_time'],a['_id']
    return [max(groups[k],key=key) for k in sorted(groups)]

def catalog():
    get(API,'dynamic_routing_all_assets.json',dict(filter=json.dumps({'data_description.project_name':'Dynamic Routing'}),projection=json.dumps({'_id':1,'name':1,'location':1,'data_description':1}),limit='500'))
    selected_rows=selected()
    write(P/'CANONICAL_ACCESS.json',dict(registration='Metadata source paths only, before column values/eligibility counts; selects latest registered processing version per exact canonical session. No borrowed scratch masks.',prefixes=[a['name'] for a in selected_rows]))
    for a in selected_rows:
        sid=session(a)
        try:get(S3,sid+'_listing.xml',dict(**{'list-type':'2','prefix':a['name']+'/','max-keys':'1000'}))
        except Exception as exc:print(sid,type(exc).__name__)
    count=sum((P/'sources'/f'{session(a)}_listing.xml').exists() for a in selected_rows)
    print('Canonical object listings saved:',count,'of',len(selected_rows),'; no Zarr data chunks read.')

def descriptors():
    ns={'s':'http://s3.amazonaws.com/doc/2006-03-01/'}
    selected_rows=selected();desc=[]
    for a in selected_rows:
        sid=session(a);root=ET.fromstring((P/'sources'/f'{sid}_listing.xml').read_bytes())
        keys=[x.text for x in root.findall('.//s:Contents/s:Key',ns)]
        candidates=[k for k in keys if k.endswith('.nwb.zarr/.zmetadata')]
        # A lexicographically late metadata key can be beyond a truncated first page.
        if not candidates:
            keys=[k.rsplit('/.zattrs',1)[0]+'/.zmetadata' for k in keys if k.endswith('.nwb.zarr/.zattrs')]
            candidates=keys
        if len(candidates)!=1:
            print(sid,'UNRESOLVED_DESCRIPTOR_PATH',len(candidates));continue
        raw=get(S3+candidates[0],sid+'_zmetadata.json')
        desc.append(dict(session=sid,asset_id=a['_id'],key=candidates[0],processing=versions(a)))
    write(P/'DESCRIPTOR_PATHS.json',desc)
    print('Descriptor-only metadata saved for',len(desc),'canonical sessions; no signal/event/anatomy column values yet.')

if __name__=='__main__':
    import sys
    {'catalog':catalog,'descriptors':descriptors}[sys.argv[1]]()
