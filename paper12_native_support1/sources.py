"""Acquire bounded official synchronization/anatomy source receipts, not physiology."""
import json
from datetime import datetime, timezone
import requests
from register import HERE, sha, verify
from storage import bytes_for

def fetch(name,url,params=None,budget=25000000):
    directory=HERE/'metadata'
    directory.mkdir(exist_ok=True)
    path=directory/(name+'.receipt')
    if path.exists() or path.with_name(path.name+'.gz').exists():return bytes_for(path),json.loads(path.with_suffix('.json').read_text())
    with requests.get(url,params=params,stream=True,timeout=60) as response:
        chunks=[];size=0
        for chunk in response.iter_content(65536):
            size+=len(chunk)
            if size>budget: raise RuntimeError('Source budget exceeded')
            chunks.append(chunk)
        payload=b''.join(chunks)
        receipt={'utc':datetime.now(timezone.utc).isoformat(),'url':response.url,
                 'status':response.status_code,'bytes':size}
    path.write_bytes(payload)
    receipt['sha256']=sha(path)
    path.with_suffix('.json').write_text(json.dumps(receipt,indent=2))
    return payload,receipt

def main():
    verify()
    repos={'sdk':'AllenInstitute/AllenSDK','sorting':'AllenInstitute/ecephys_spike_sorting'}
    files={'sdk':[
        'allensdk/brain_observatory/ecephys/align_timestamps/barcode.py',
        'allensdk/brain_observatory/ecephys/align_timestamps/probe_synchronizer.py',
        'allensdk/brain_observatory/ecephys/align_timestamps/__main__.py',
        'allensdk/brain_observatory/sync_dataset.py',
        'allensdk/brain_observatory/ecephys/ecephys_session_api/ecephys_nwb_session_api.py',
        'LICENSE'],
        'sorting':['ecephys_spike_sorting/common/utils.py','ecephys_spike_sorting/common/OEFileInfo.py',
                   'ecephys_spike_sorting/modules/extract_from_npx/__main__.py','LICENSE']}
    pins={}
    for label,repo in repos.items():
        data,r=fetch(label+'_commit','https://api.github.com/repos/'+repo+'/commits/master')
        if r['status']!=200:
            info,ri=fetch(label+'_repo_info','https://api.github.com/repos/'+repo)
            if ri['status']!=200: raise RuntimeError('Official repo info unavailable')
            branch=json.loads(info)['default_branch']
            data,r=fetch(label+'_commit_default','https://api.github.com/repos/'+repo+'/commits/'+branch)
            if r['status']!=200: raise RuntimeError('Source commit unavailable')
        commit=json.loads(data)['sha'];pins[label]=commit
        for i,path in enumerate(files[label]):
            fetch(label+'_source_'+str(i),'https://raw.githubusercontent.com/'+repo+'/'+commit+'/'+path)
    fetch('allen_documentation','https://allensdk.readthedocs.io/en/latest/visual_coding_neuropixels.html')
    fetch('allen_access_documentation','https://allensdk.readthedocs.io/en/latest/_static/examples/nb/ecephys_data_access.html')
    try:
        fetch('allen_whitepaper','https://brainmapportal-live-4cc80a57cd6e400d854-f7fdcae.divio-media.net/filer_public/80/75/8075a100-ca64-429a-b39a-569121b612b2/neuropixels_visual_coding_-_white_paper_v10.pdf')
    except requests.RequestException as exc:
        (HERE/'metadata/whitepaper_legacy_failure.json').write_text(json.dumps({'error':type(exc).__name__,'reason':'Legacy host DNS unavailable; current official SDK document link used'},indent=2))
        fetch('allen_whitepaper_current','https://cdn.prod.website-files.com/689cfbd308fa7373b604d290/6a30107b2f53d6743336311d_neuropixels_visual_coding_-_white_paper_v10-compressed.pdf')
    base='https://raw.githubusercontent.com/AllenInstitute/AllenSDK/'+pins['sdk']+'/'
    for i,path in enumerate(['allensdk/brain_observatory/ecephys/align_timestamps/channel_states.py',
                             'allensdk/brain_observatory/ecephys/align_timestamps/barcode_sync_dataset.py',
                             'allensdk/brain_observatory/ecephys/align_timestamps/_schemas.py']):
        fetch('sdk_extra_'+str(i),base+path)
    (HERE/'source_pins.json').write_text(json.dumps(pins,indent=2))
    print(json.dumps(pins,indent=2))

if __name__=='__main__':main()
