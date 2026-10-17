"""Network-denied saved-result reproduction of the source STOP, never model fitting."""
import hashlib,json,socket,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import requests
from .source_metadata import P,read,verify_history
from .compatibility import run

def verify():
    hashes=read(P/'PAYLOAD_HASHES.json')['hashes']
    for name,h in hashes.items():
        if hashlib.sha256((P/name).read_bytes()).hexdigest()!=h:raise ValueError('Payload changed: '+name)
    return len(hashes)

def access_audit():
    ranges=[json.loads(x) for x in (P/'results/SOURCE_ACCESS.jsonl').read_text().splitlines()]
    hops=[json.loads(x) for x in (P/'results/SOURCE_HTTP_ACCESS.jsonl').read_text().splitlines()]
    r=read(P/'SOURCE_AUDIT_ROSTER.json')['records'][0];a=r['asset'];policy=read(P/'SOURCE_REGISTRATION.json')['access']
    assert {x['asset_id'] for x in ranges}=={a['asset_id']}
    assert len(hops)<=policy['max_requests'] and sum(x['bytes'] for x in ranges)<=policy['max_metadata_bytes_per_asset']
    assert all(x['status']==206 and x['bytes']==x['bytes_requested'] and x['size']==a['size'] and x['content_range']==f"bytes {x['start']}-{x['start']+x['bytes']-1}/{a['size']}" for x in ranges)
    assert len({x['etag'] for x in ranges})==1
    assert {x['host'] for x in hops}=={'api.dandiarchive.org','dandiarchive.s3.amazonaws.com'}
    assert all(x['asset_id']==a['asset_id'] and (x['path']==f"/api/assets/{a['asset_id']}/download/" if x['host']=='api.dandiarchive.org' else a['blob'] in x['path']) for x in hops)
    assert len(hops)==2*len(ranges)
    for folder in ['schemas','values']:
        x=read(P/'metadata'/folder/(a['asset_id']+'.json'))
        assert x['neural_values_decoded'] is False and x['raw_behavior_values_decoded'] is False
        assert all(z['opened'] is False and 'shape' not in z for z in x['schema'] if not z['permitted'])
    return dict(assets=1,range_attempts=len(ranges),http_requests=len(hops),opaque_transport_bytes=sum(x['bytes'] for x in ranges))

def main():
    with patch.object(requests.Session,'request',side_effect=AssertionError('Network forbidden in saved reproduction')),patch.object(socket.socket,'connect',side_effect=AssertionError('Network forbidden')),patch.object(socket.socket,'connect_ex',side_effect=AssertionError('Network forbidden')):
        payload=verify();history=verify_history();access=access_audit()
        suite=unittest.defaultTestLoader.loadTestsFromNames(['paper14_v2.test_source_metadata','paper14_v2.test_compatibility'])
        result=unittest.TextTestRunner(verbosity=2).run(suite)
        if not result.wasSuccessful():raise RuntimeError('Required regression failure')
        with tempfile.TemporaryDirectory(dir=P/'work') as d:
            x=run(Path(d))
            for name in ['SOURCE_COMPATIBILITY.json','TRIAL_EVENT_COMPARISON.csv']:
                if (Path(d)/name).read_bytes()!=(P/'results/source_gate'/name).read_bytes():raise ValueError('Saved result mismatch: '+name)
            assert x['source_compatibility']=='SOURCE_CONTRACT_INCONCLUSIVE'
            assert not x['annotation_bridge_pass'] and x['fits']==0 and x['scores']==0 and not x['neural_values_decoded']
        print(json.dumps(dict(status='SAVED_SOURCE_STOP_REPRODUCED',tests=result.testsRun,payload_hashes=payload,historical_hashes=history,access=access,new_network_calls=0,new_fits=0,new_scores=0)))

if __name__=='__main__':
    (P/'work').mkdir(exist_ok=True)
    main()
