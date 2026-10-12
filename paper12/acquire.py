"""Bounded public metadata requests, never session physiology downloads."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
import requests
from register import verify

HERE = Path(__file__).resolve().parent
RAW = HERE / 'metadata'
API = 'https://api.brain-map.org/api/v2/data/query.json'
FIELDS = {
    'sessions': ('EcephysSession', 'id,specimen_id,stimulus_name,date_of_acquisition,fail_eye_tracking'),
    'probes': ('EcephysProbe', 'id,ecephys_session_id,name,sampling_rate,lfp_sampling_rate,use_lfp_data'),
    'units': ('EcephysUnit', 'id,ecephys_channel_id'),
    'channels': ('EcephysChannel', 'ecephys_channels.id,ecephys_probe_id,local_index,structures.id as structure_id,structures.acronym as structure_acronym'),
}

def save(name, url, content, status):
    RAW.mkdir(exist_ok=True)
    path = RAW / (name + '.receipt')
    if path.exists():
        raise RuntimeError('Never replace an acquired snapshot: ' + name)
    path.write_bytes(content)
    receipt = {'utc': datetime.now(timezone.utc).isoformat(), 'url': url,
               'status': status, 'bytes': len(content),
               'sha256': hashlib.sha256(content).hexdigest()}
    (RAW / (name + '.json')).write_text(json.dumps(receipt, indent=2))
    return receipt

def validate_projection(data, fields):
    allowed = {f.split(' as ')[-1].split('.')[-1] for f in fields.split(',')}
    if data.get('success') is not True:
        raise RuntimeError('Server rejected metadata projection')
    if len(data['msg']) != data['total_rows']:
        raise RuntimeError('Incomplete denominator')
    for row in data['msg']:
        if set(row) - allowed:
            raise RuntimeError('Fail closed: unexpected returned columns')

def get(name, url, params=None, projection=None):
    with requests.get(url, params=params, timeout=90, stream=True) as response:
        chunks, size = [], 0
        for chunk in response.iter_content(chunk_size=65536):
            size += len(chunk)
            if size > 25000000:
                raise RuntimeError('Metadata response budget exceeded before accepting snapshot')
            chunks.append(chunk)
        response._content = b''.join(chunks)
        if projection is not None:
            validate_projection(response.json(), projection)
        receipt = save(name, response.url, response.content, response.status_code)
    response.raise_for_status()
    return response, receipt

def acquire_allen():
    verify()
    get('allen_documentation', 'https://allensdk.readthedocs.io/en/latest/visual_coding_neuropixels.html')
    get('allen_sdk_source', 'https://raw.githubusercontent.com/AllenInstitute/AllenSDK/master/allensdk/brain_observatory/ecephys/ecephys_project_api/ecephys_project_warehouse_api.py')
    for name, (model, fields) in FIELDS.items():
        include = ',rma::include,structure' if name == 'channels' else ''
        criteria = f"model::{model}{include},rma::options[tabular$eq'{fields}'][num_rows$eq'all'][order$eq'id']"
        response, receipt = get('allen_' + name, API, {'criteria': criteria}, projection=fields)
        data = response.json()
        if data.get('success') is not True:
            raise RuntimeError('Server rejected metadata projection: ' + str(data.get('msg'))[:500])
        allowed = {f.split(' as ')[-1].split('.')[-1] for f in fields.split(',')}
        for row in data['msg']:
            if set(row) - allowed:
                raise RuntimeError('Fail closed: unexpected returned columns')
        if len(data['msg']) != data['total_rows']:
            raise RuntimeError('Incomplete denominator')
        print(json.dumps({'table': name, 'rows': len(data['msg']), 'sha256': receipt['sha256']}), flush=True)

if __name__ == '__main__':
    acquire_allen()
