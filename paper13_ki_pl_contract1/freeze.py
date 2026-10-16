"""Create append-only, source/input/output-bound review snapshots."""
import argparse
import datetime
import hashlib
import importlib.metadata
import json
from pathlib import Path

P=Path(__file__).resolve().parent
ROOT=P.parent
OLD=ROOT/'paper13_ki_feasibility1'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def inventory():
    paths=list((OLD/'metadata/headers').glob('000473_*.json'))
    paths += [OLD/'results/review1/audit.json',OLD/'headers.py',OLD/'REGISTRATION.json',OLD/'saved_inventory.json']
    paths += [OLD/'metadata'/x for x in ['000473_version.json','000473_assets_00.json','provider_active_intervals.json','preprocessing_record_14205018.json','preprocessing_zip_index.json','pfcmap_commit.json','pfcmap_tree.json','code__LICENSE','code__python__utils__data_classes.py','code__python__metrics_extraction__spontaneous__extract_prepost_quietactive.py','code__python__config__datatables__allrecs_allprobes.xlsx']]
    paths += [p for p in P.rglob('*') if p.is_file() and not any(x in p.parts for x in ['work','__pycache__']) and not p.name.startswith('FREEZE_')]
    return {str(p.relative_to(ROOT)).replace('\\','/'):sha(p) for p in sorted(set(paths))}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('revision');args=ap.parse_args()
    snap={'mission':'P13-KI-PL-QUALITY-EPOCH-RESOLUTION-1','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'revision':args.revision,
          'scope':'metadata audit, synthetic QC references and proposed protocol; no neural execution',
          'protocol_snapshot':sorted(P.glob('PROPOSED_PROTOCOL_FREEZE*.json'))[-1].name,
          'runtime':{'python':'3.11','packages':{x:importlib.metadata.version(x) for x in ['requests','numpy','h5py']}},'hashes':inventory()}
    with (P/f'FREEZE_{args.revision}.json').open('x',encoding='utf8',newline='\n') as f:f.write(json.dumps(snap,indent=2)+'\n')
    print(json.dumps({'revision':args.revision,'files':len(snap['hashes']),'freeze_sha256':sha(P/f'FREEZE_{args.revision}.json')}))

if __name__=='__main__':main()
