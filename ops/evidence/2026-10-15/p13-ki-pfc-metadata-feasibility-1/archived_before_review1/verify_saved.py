"""Offline saved-metadata reproduction, with byte-identical deterministic audit."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import uuid

P=Path(__file__).resolve().parent
ROOT=P.parent


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def verify():
    inv=json.loads((P/'saved_inventory.json').read_text())
    for row in inv['files']:
        path=(ROOT/row['path']).resolve()
        if not path.is_relative_to(ROOT) or not path.is_file() or sha(path)!=row['sha256']:
            raise ValueError('Missing/corrupt frozen metadata or source: '+row['path'])
    journal=[json.loads(s) for s in (P/'metadata/access.jsonl').read_text().splitlines()]
    policy=json.loads((P/'REGISTRATION.json').read_text())
    assert len(journal)<=policy['bounds']['http_requests']
    assert sum(r['bytes'] for r in journal)<=policy['bounds']['transport_bytes']
    assert not any('spike_times' in r['url'] or 'spikes.times' in r['url'] for r in journal)
    headers=list((P/'metadata/headers').glob('*.json'))
    assert len(headers)==99
    # Inspect recorded value-access paths; neural dataset structures are allowed
    # as public schema headers, but their values must never be decoded.
    for path in headers:
        h=json.loads(path.read_text())
        assert not h['spike_values_read']
        assert not any(any(term in s for term in ['spike_times','waveform','/data']) for s in h['decoded_paths'])
        assert h['transport_bytes']<=policy['bounds']['header_bytes_per_asset']
    return len(inv['files'])


def main(table_python):
    n=verify();work=P/'work'/('replay_'+uuid.uuid4().hex);work.mkdir(parents=True)
    subprocess.run([sys.executable,'-m','unittest','discover','-s',str(P),'-p','test_*.py','-v'],cwd=ROOT,check=True)
    subprocess.run([sys.executable,str(P/'audit.py'),'--output',str(work/'audit')],cwd=ROOT,check=True)
    subprocess.run([table_python,str(P/'independent_check.py'),'--output',str(work/'independent_check.json')],cwd=ROOT,check=True)
    names=['audit.json','all_unit_metadata.csv','all_basic_epoch_identities.csv','all_recording_identities.csv','all_mouse_denominators.csv']
    for name in names:
        if sha(work/'audit'/name)!=sha(P/'results/final'/name):raise ValueError('Audit replay changed: '+name)
    result={'pass':True,'saved_file_hashes':n,'byte_identical_outputs':names,'new_network_requests':0,
            'spike_values_read':0,'model_fits':0,'scientific_verdict':'INCONCLUSIVE_METADATA','M1_M7_started':False}
    (work/'receipt.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--table-python',default=sys.executable);main(ap.parse_args().table_python)
