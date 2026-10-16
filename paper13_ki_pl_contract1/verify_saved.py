"""No-network, saved-only replay; it never imports acquisition entry points."""
import argparse
import hashlib
import json
from pathlib import Path
import socket
import uuid
from unittest.mock import patch
from audit import P,ROOT,run

def check_hashes(items,base):
    for name,expected in items.items():
        p=base/name
        if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=expected:raise ValueError('Missing/corrupt/hash mismatch: '+name)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--revision',default='r2');args=ap.parse_args()
    snap=json.loads((P/f'FREEZE_{args.revision}.json').read_text());check_hashes(snap['hashes'],ROOT)
    protocol=json.loads((P/snap.get('protocol_snapshot','PROPOSED_PROTOCOL_FREEZE.json')).read_text());check_hashes(protocol['hashes'],P)
    work=P/'work'/('replay_'+uuid.uuid4().hex);work.parent.mkdir(exist_ok=True)
    with patch.object(socket.socket,'connect',side_effect=AssertionError('Saved-only replay forbids network')):
        run(work)
    names=['audit.json','future_qc.json','animal_disposition.csv','epoch_disposition.csv']
    for name in names:
        if (work/name).read_bytes()!=(P/'results/initial'/name).read_bytes():raise ValueError('Replay output changed: '+name)
    access=[json.loads(x) for x in (P/'metadata/access.jsonl').read_text().splitlines()]
    result={'revision':args.revision,'saved_hashes_verified':len(snap['hashes']),'identical_replayed_outputs':names,'new_HTTP_requests':len(access),'new_transport_bytes':sum(x.get('bytes',0) for x in access),'real_spike_value_reads':0,'real_fits':0,'protocol_activated':False,'neural_numerical_models_tested':False,'work':str(work.relative_to(P))}
    print(json.dumps(result));return result

if __name__=='__main__':main()
