"""Public saved-only reproduction: hashes, synthetic oracles and exact replay."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import uuid

P=Path(__file__).resolve().parent
ROOT=P.parent


def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_inventory():
    inventory=json.loads((P/'saved_inventory.json').read_text())
    for item in inventory['files']:
        path=(ROOT/item['path']).resolve()
        if not path.is_relative_to(ROOT) or not path.is_file() or digest(path)!=item['sha256']:
            raise ValueError('Missing or altered saved artifact: '+item['path'])
    pin=json.loads((P/'M0_SOURCE_PIN.json').read_text())
    for name,expected in pin['source_hashes'].items():
        path=P/'metadata'/name
        if name=='access.jsonl':
            # This is an append-only access log; the source pin sealed its prefix.
            data=b'';matches=False
            for line in path.read_bytes().splitlines(keepends=True):
                data+=line
                if hashlib.sha256(data).hexdigest()==expected:
                    matches=True;break
            if not matches: raise ValueError('Original access prefix changed')
        elif digest(path)!=expected:
            raise ValueError('Pinned original metadata changed: '+name)
    journal=[json.loads(line) for line in (P/'metadata/access.jsonl').read_text().splitlines()]
    policy=json.loads((P/'M0_REGISTRATION.json').read_text())
    assert len(journal)<=policy['bounds']['http_requests']
    assert sum(row.get('bytes',0) for row in journal)<=policy['bounds']['transport_bytes']
    assert not any('spikes' in row['url'].lower() for row in journal)
    return len(inventory['files'])


def main():
    count=verify_inventory()
    work=P/'work'/('saved_replay_'+uuid.uuid4().hex)
    output=work/'M0'
    work.mkdir(parents=True)
    calls=[['-m','unittest','discover','-s',str(P),'-p','test_metadata_audit.py','-v'],
           [str(P/'metadata_audit.py'),'--output',str(output)],
           [str(P/'independent_metadata_check.py'),'--output',str(work/'independent_counts.json')]]
    for args in calls:
        subprocess.run([sys.executable,*args],cwd=ROOT,check=True)
    regenerated=[]
    for name in ['M0_audit.json','all_probe_region_denominators.csv','all_candidate_unit_identities.csv']:
        if digest(output/name)!=digest(P/'results/M0'/name):
            raise ValueError('Saved replay discrepancy: '+name)
        regenerated.append(name)
    receipt={'pass':True,'verified_file_hashes':count,'byte_identical_replays':regenerated,
             'network_requests':0,'neural_array_reads':0,'model_fits':0,
             'scientific_gate':'FAIL_DATA_INSUFFICIENT','continue_M1':False}
    (work/'reproduction_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))


if __name__=='__main__': main()
