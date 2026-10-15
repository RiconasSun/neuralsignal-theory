"""Read-only saved C model/state byte hashes. No raw neural arrays, D keys or ledger."""
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path

E=Path(__file__).resolve().parent;ROOT=E.parents[3]

def main():
    inventory_path=ROOT/'ops/evidence/2026-10-14/p12-c-seal-host-import-repair-1/complete_seal_inventory.json'
    inventory=json.loads(inventory_path.read_text());root=(ROOT/'paper12_cseal1/.private/sealed_C_recovery_1').resolve()
    if inventory['files']!=1862 or inventory['original_partial_files']!=1858 or len(inventory['sha256'])!=1862:raise RuntimeError('ORIGINAL_COMPLETE_SEAL_INVENTORY')
    for name,value in inventory['sha256'].items():
        p=root/name
        if not p.resolve().is_relative_to(root) or '..' in Path(name).parts or p.is_symlink() or getattr(p.lstat(),'st_file_attributes',0)&0x400:raise RuntimeError('SAVED_C_PATH_IDENTITY')
        if hashlib.sha256(p.read_bytes()).hexdigest()!=value:raise RuntimeError('SAVED_C_HASH:'+name)
    report={'utc':datetime.now(timezone.utc).isoformat(),'complete_C_seal_unchanged':True,'verified_files':1862,'original_partial_files':1858,'inventory_sha256':hashlib.sha256(inventory_path.read_bytes()).hexdigest(),'fullstate_sha256':hashlib.sha256((root/'complete_states.npz').read_bytes()).hexdigest(),'operation':'READONLY_SAVED_MODEL_STATE_HASHES','raw_C_D_count_reads':0,'new_fits':0,'real_D_source_key_or_ledger_opens':0}
    with (E/'C_seal_unchanged.json').open('x',encoding='utf-8') as f:json.dump(report,f,indent=2,sort_keys=True);f.write('\n')
    print(json.dumps(report,sort_keys=True))

if __name__=='__main__':main()
