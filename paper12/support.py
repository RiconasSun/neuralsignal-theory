"""Uniform file descriptor and HTTP Range capability audit without bulk NWB."""
import json
from datetime import datetime, timezone
import requests
from acquire import API, HERE, get, save
from register import verify, sha

def register_policy():
    record = {'utc': datetime.now(timezone.utc).isoformat(),
              'policy_sha256': sha(HERE / 'HEADER_POLICY.json')}
    with (HERE / 'header_registration.json').open('x') as out:
        json.dump(record, out, indent=2)

def main():
    verify()
    if not (HERE / 'header_registration.json').exists():
        register_policy()
    if sha(HERE / 'HEADER_POLICY.json') != json.loads((HERE / 'header_registration.json').read_text())['policy_sha256']:
        raise RuntimeError('Header policy changed')
    if not (HERE / 'metadata/allen_access_documentation.receipt').exists():
        get('allen_access_documentation', 'https://allensdk.readthedocs.io/en/latest/_static/examples/nb/ecephys_data_access.html')
    criteria = "model::WellKnownFile,rma::criteria,well_known_file_type[name$eq'EcephysNwb'][attachable_type$eq'EcephysSession'],rma::options[tabular$eq'well_known_files.id,attachable_id'][num_rows$eq'all']"
    response, _ = get('allen_nwb_descriptors_code1', API, {'criteria': criteria})
    data = response.json()
    if not data['success'] or len(data['msg']) != data['total_rows']:
        raise RuntimeError('Incomplete descriptors')
    results = []
    for row in data['msg']:
        if set(row) != {'id', 'attachable_id'}:
            raise RuntimeError('Unexpected descriptor field')
        url = 'https://api.brain-map.org/api/v2/well_known_file_download/' + str(row['id'])
        item = {'session_id': row['attachable_id'], 'file_id': row['id'],
                'recording_support': 'UNKNOWN', 'decoded_neural_values': False}
        try:
            with requests.get(url, headers={'Range': 'bytes=0-7'}, stream=True, timeout=30) as res:
                item.update({'http_status': res.status_code, 'content_range': res.headers.get('Content-Range'),
                             'content_length': res.headers.get('Content-Length'), 'etag': res.headers.get('ETag'),
                             'last_modified': res.headers.get('Last-Modified')})
                if res.status_code == 206 and res.headers.get('Content-Range', '').startswith('bytes 0-7/'):
                    payload = res.raw.read(8)
                    item['header_signature_sha256'] = __import__('hashlib').sha256(payload).hexdigest()
                    item['hdf5_signature'] = payload == b'\x89HDF\r\n\x1a\n'
                    item['bytes_read'] = len(payload)
                else:
                    item['bytes_read'] = 0
                    item['limitation'] = 'Bounded range not honored; bulk physiological response closed without consuming body'
        except requests.RequestException as exc:
            item['error'] = type(exc).__name__
        results.append(item)
        print(json.dumps(item), flush=True)
    (HERE / 'metadata' / 'allen_header_capability.json').write_text(json.dumps(results, indent=2))

if __name__ == '__main__':
    main()
