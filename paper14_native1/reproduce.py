"""Network-denied canonical-native source decision reproduction, no model API."""
import json,socket,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import requests
from .source_metadata import P,ROOT,read,sha,verify_history,permitted
from .audit import run
RESULTS=['CANONICAL_NATIVE_DECISION.json','ANIMAL_EXCLUSION_MATRIX.csv','TRIAL_EXCLUSIONS.csv','CANONICAL_UNIT_MAPPING.csv','ORIGINAL_BLOCKS.csv']

def integrity():
    hashes=read(P/'PAYLOAD_HASHES.json')['hashes']
    for name,h in hashes.items():
        if sha((P/name).read_bytes())!=h:raise ValueError('Changed package: '+name)
    r=read(P/'SOURCE_AUDIT_ROSTER.json')['records'];registry={z['asset']['asset_id']:z for z in r}
    policy=read(P/'SOURCE_REGISTRATION.json')['access']
    ranges=[json.loads(x) for x in (P/'results/SOURCE_ACCESS.jsonl').read_text().splitlines()]
    hops=[json.loads(x) for x in (P/'results/SOURCE_HTTP_ACCESS.jsonl').read_text().splitlines()]
    assert len(hops)<=policy['max_requests'] and sum(x['bytes'] for x in ranges)<=policy['max_total_bytes']
    for asset_id,record in registry.items():
        x=read(P/'metadata/values'/(asset_id+'.json'));a=record['asset']
        assert x['neural_values_decoded'] is False and x['raw_behavior_values_decoded'] is False
        assert all(permitted(k) for k in x['values'])
        assert all(z['opened'] is False and 'shape' not in z for z in x['schema'] if not z['permitted'])
        relevant=[z for z in ranges if z['asset_id']==asset_id];assert relevant
        assert sum(z['bytes'] for z in relevant)<=policy['max_metadata_bytes_per_asset']
        for z in relevant:
            if 'sha256' in z:
                assert z['status']==206 and z['bytes']==z['bytes_requested'] and z['size']==a['size']
                assert z['content_range']==f"bytes {z['start']}-{z['start']+z['bytes']-1}/{a['size']}"
                assert z['etag']==x['etag']
    for h in hops:
        assert h['asset_id'] in registry
        a=registry[h['asset_id']]['asset']
        if h['host']=='api.dandiarchive.org':assert h['path']==f"/api/assets/{a['asset_id']}/download/"
        else:assert h['host'] in {'dandiarchive.s3.amazonaws.com','dandiarchive.s3.us-east-1.amazonaws.com','dandiarchive.s3.us-east-2.amazonaws.com'} and a['blob'] in h['path']
    reuse=read(P/'results/CACHED_METADATA_REUSE.json')['files']
    assert len(reuse)==448 and all(x['source'].startswith('paper14_v2/work/source_metadata_ranges/9e27ec60-e8d9-4dcf-a9a4-4b8acb6265ef/') for x in reuse)
    docs=[json.loads(x) for x in (P/'results/DOCUMENTARY_ACCESS.jsonl').read_text().splitlines()]
    assert len(docs)==20 and all(x['status']==200 and sha((P/'sources'/x['name']).read_bytes())==x['sha256'] for x in docs)
    return dict(payload_hashes=len(hashes),metadata_assets=len(registry),range_attempts=len(ranges),http_transactions=len(hops),new_opaque_bytes=sum(x['bytes'] for x in ranges),reused_range_pairs=224,documentary_requests=len(docs),failed_range_attempts=sum('error' in x for x in ranges))

def main():
    with patch.object(requests.Session,'request',side_effect=AssertionError('Network forbidden')),patch.object(socket.socket,'connect',side_effect=AssertionError('Network forbidden')),patch.object(socket.socket,'connect_ex',side_effect=AssertionError('Network forbidden')):
        checks=integrity();historical=verify_history()
        suite=unittest.defaultTestLoader.loadTestsFromNames(['paper14_native1.test_source_metadata','paper14_native1.test_native','paper14_native1.test_audit'])
        test=unittest.TextTestRunner(verbosity=2).run(suite)
        if not test.wasSuccessful():raise RuntimeError('Canonical-native regression failure')
        with tempfile.TemporaryDirectory(dir=P/'work') as temp:
            x=run(Path(temp))
            for name in RESULTS:
                if (Path(temp)/name).read_bytes()!=(P/'results/audit'/name).read_bytes():raise ValueError('Saved result differs: '+name)
        assert x['model_fits']==x['predictive_scores']==x['temporal_evaluations']==0
        print(json.dumps(dict(saved_decision_reproduced=x['scientific_decision'],tests=test.testsRun,byte_exact_results=len(RESULTS),historical_hashes=historical,**checks,network_calls=0,neural_access=False,fits=0,scores=0)))

if __name__=='__main__':
    (P/'work').mkdir(exist_ok=True);main()
